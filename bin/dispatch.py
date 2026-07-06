#!/usr/bin/env python3
"""agentco dispatcher (Wave③) — 队列在 Codex 外,Codex 只当 worker。
cron 每 5 分钟;文件锁防重入;串行消费。

Wave③ 变更:
- 工具域 4:retriever / executor-{code,data,3d} / digester / auditor(worker=profile 变体)。
- 路由:retriever/digester/auditor 产出→inbox&done;executor→review(机器验收)。
- retriever 预处理:codex 前先跑 search.py(query 取自 spec frontmatter)→ raw 注入上下文,模型不联网。
- 取任务:status='queued' 且依赖已 done,ORDER BY priority,created_at;依赖未 done 的任务是 waiting_dep,不占 worker。
- 依赖边:任务 done→扫 waiting_dep(depends_on==该 tid)→queued+dep_triggered;任务 blocked→下游标 dep_failed 进日报。
- 3D:executor-3d 入队即 waiting_gpu,不进主循环(bin/gpu_worker.sh 本地拉取)。
- skill_hit:spec 引用 skill 路径时记 event 并 bump use_count。
"""
import fcntl, re, sqlite3, subprocess, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agentlib import load_env
load_env()  # cron 环境无 .env 变量;codex/feishu_card 子进程靠继承 os.environ 拿 LITELLM_MASTER_KEY 等

ROOT = Path(__file__).resolve().parent.parent
DB, TRACES, LOG = ROOT/"state.db", ROOT/"traces", ROOT/"logs/dispatch.log"
MAX_ATTEMPTS_PER_TIER, MAX_TIER = 2, 1

PROFILE = {  # (agent, tier) -> codex profile;无 -hi 的域两档同 profile
    ("retriever", 0): "retriever",         ("retriever", 1): "retriever",
    ("executor-code", 0): "executor-code", ("executor-code", 1): "executor-code-hi",
    ("executor-data", 0): "executor-data", ("executor-data", 1): "executor-data",
    ("executor-3d", 0): "executor-3d",     ("executor-3d", 1): "executor-3d",
    ("digester", 0): "digester",           ("digester", 1): "digester-hi",
    ("auditor", 0): "auditor",             ("auditor", 1): "auditor",
}
VALID_AGENTS = {"retriever", "executor-code", "executor-data", "executor-3d", "digester", "auditor"}
INBOX_AGENTS = {"retriever", "digester", "auditor"}   # 产出→inbox&done;其余(executor)→review

def log(msg):
    line = f"{datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line); LOG.parent.mkdir(exist_ok=True); LOG.open("a").write(line+"\n")

def feishu(text):
    subprocess.run([str(ROOT/"bin/feishu_push.sh"), text], check=False)

def ev(db, task_id, agent, kind, detail=""):
    db.execute("INSERT INTO events(task_id,agent,kind,detail) VALUES(?,?,?,?)",
               (task_id, agent, kind, detail)); db.commit()

# ---- skill 心跳:spec 引用 skill 路径 → skill_hit + bump use_count ----
_SKILL_RE = re.compile(r"skills/([A-Za-z0-9_\-]+)")

def record_skill_hits(db, tid, agent, spec):
    for sid in sorted(set(_SKILL_RE.findall(spec))):
        ev(db, tid, agent, "skill_hit", sid)
        for f in ROOT.glob(f"**/skills/{sid}/SKILL.md"):
            txt = f.read_text()
            m = re.search(r"^use_count:\s*(\d+)\s*$", txt, re.M)
            if m:
                f.write_text(txt[:m.start(1)] + str(int(m.group(1)) + 1) + txt[m.end(1):])

# ---- retriever 预处理:跑 search.py,把 raw 路径注入上下文 ----
def search_preprocess(db, t, spec):
    m = re.search(r"^query:\s*(.+?)\s*$", spec, re.M)
    if not m:
        log(f"{t['id']} retriever 无 query 字段,跳过搜索预处理")
        return spec
    query = m.group(1).strip().strip('"').strip("'")
    try:
        from search import run_search
        raw = run_search(query, project=t["project"] or "default")
        ev(db, t["id"], t["agent"], "search", raw)
        log(f"{t['id']} search.py → {raw}")
        return (f"# 已抓取搜索原料(只读它分析,禁止联网)\n路径:{raw}\n"
                f"内容见该文件;其 frontmatter 的 content_hash/source_urls 必须继承进你的 envelope。\n\n" + spec)
    except Exception as e:
        ev(db, t["id"], t["agent"], "search_fail", str(e)[:200])
        log(f"{t['id']} search.py 失败:{e}")
        return spec

def run_task(db, t):
    tid, agent, tier = t["id"], t["agent"], t["tier"]
    profile = PROFILE.get((agent, tier))
    if not profile:
        ev(db, tid, agent, "block", f"no profile for ({agent},{tier})")
        db.execute("UPDATE tasks SET status='blocked',updated_at=datetime('now') WHERE id=?", (tid,)); db.commit()
        propagate_block(db, t); return
    spec = (ROOT/t["spec_path"]).read_text()
    record_skill_hits(db, tid, agent, spec)
    if agent == "retriever":
        spec = search_preprocess(db, t, spec)
    trace_dir = TRACES/agent/datetime.now().strftime("%Y%m%d"); trace_dir.mkdir(parents=True, exist_ok=True)
    trace = trace_dir/f"{tid}.a{t['attempts']}.jsonl"
    log(f"{tid} -> {profile} (attempt {t['attempts']+1})")
    try:
        r = subprocess.run(
            ["codex", "exec", "-p", profile, "--json",
             "--cd", str(ROOT), "--output-last-message", str(trace)+".final", spec],
            capture_output=True, text=True, timeout=t["ttl_sec"])
        trace.write_text(r.stdout)
        ok = r.returncode == 0 and Path(str(trace)+".final").exists()
    except subprocess.TimeoutExpired:
        ok = False
        ev(db, tid, agent, "fail", "timeout")

    if ok:
        final = Path(str(trace)+".final").read_text()
        out = ROOT/"handoff"/f"{tid}.result.md"
        out.write_text(f"# {tid} result ({agent}/{profile})\n\n{final}\n")
        if agent in INBOX_AGENTS:   # retriever/digester/auditor 直接闭环落 inbox
            inbox = ROOT/"kb/90-inbox"/f"{tid}-{agent}.md"
            inbox.write_text(f"---\nsource: {agent}\ntask: {tid}\nproject: {t['project']}\n"
                             f"date: {datetime.now():%Y-%m-%d}\nstatus: raw\n---\n\n{final}\n")
            new_status = "done"
        else:                       # executor → review(机器验收)
            new_status = "review"
        db.execute("UPDATE tasks SET status=?,result_path=?,updated_at=datetime('now') WHERE id=?",
                   (new_status, str(out.relative_to(ROOT)), tid))
        ev(db, tid, agent, "done", profile)
        if new_status == "done":
            trigger_dependents(db, tid)
        if t["notify"]:
            if new_status == "review":
                subprocess.run([sys.executable, str(ROOT/"bin/feishu_card.py"),
                                tid, t["title"], final[:600]], check=False)
            else:
                feishu(f"✅ {tid} {t['title']}\nagent={agent} tier={tier}\n---\n{final[:800]}")
    else:
        attempts = t["attempts"]+1
        if attempts >= MAX_ATTEMPTS_PER_TIER and tier < MAX_TIER:
            db.execute("UPDATE tasks SET tier=tier+1,attempts=0,status='queued',updated_at=datetime('now') WHERE id=?", (tid,))
            ev(db, tid, agent, "escalate", f"tier{tier}->{tier+1}"); log(f"{tid} escalated")
        elif attempts >= MAX_ATTEMPTS_PER_TIER:
            db.execute("UPDATE tasks SET status='blocked',attempts=?,updated_at=datetime('now') WHERE id=?", (attempts, tid))
            ev(db, tid, agent, "block", "max attempts at max tier")
            feishu(f"🛑 {tid} {t['title']} BLOCKED,需人工。trace: {trace}")
            propagate_block(db, t)
        else:
            db.execute("UPDATE tasks SET attempts=?,status='queued',updated_at=datetime('now') WHERE id=?", (attempts, tid))
            ev(db, tid, agent, "fail", f"attempt {attempts}")
    db.commit()

# ---- 依赖边 ----
def trigger_dependents(db, done_tid):
    """上游 done → 依赖它的 waiting_dep 任务转 queued(幂等:仅动 waiting_dep)。"""
    for r in db.execute("SELECT id,agent FROM tasks WHERE depends_on=? AND status='waiting_dep'", (done_tid,)).fetchall():
        db.execute("UPDATE tasks SET status='queued',updated_at=datetime('now') WHERE id=?", (r["id"],))
        ev(db, r["id"], r["agent"], "dep_triggered", f"upstream {done_tid} done")
        log(f"{r['id']} dep_triggered by {done_tid}")
    db.commit()

def propagate_block(db, t):
    """上游 blocked → 下游(waiting_dep/queued 依赖它的)标 dep_failed,不静默挂起,进日报。"""
    for r in db.execute("SELECT id,agent FROM tasks WHERE depends_on=? AND status IN ('waiting_dep','queued')",
                        (t["id"],)).fetchall():
        db.execute("UPDATE tasks SET status='dep_failed',updated_at=datetime('now') WHERE id=?", (r["id"],))
        ev(db, r["id"], r["agent"], "dep_failed", f"upstream {t['id']} blocked")
        log(f"{r['id']} dep_failed <- {t['id']} blocked")
    db.commit()

def main():
    lock = open(ROOT/".dispatch.lock", "w")
    try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError: sys.exit(0)
    sys.path.insert(0, str(ROOT/"bin"))   # for `import search`
    db = sqlite3.connect(DB); db.row_factory = sqlite3.Row
    # 僵尸回收:running 超 2×ttl → 重排
    for s in db.execute("""SELECT id,agent FROM tasks WHERE status='running'
        AND (strftime('%s','now')-strftime('%s',updated_at)) > 2*ttl_sec""").fetchall():
        db.execute("UPDATE tasks SET status='queued',attempts=attempts+1,updated_at=datetime('now') WHERE id=?", (s["id"],))
        ev(db, s["id"], s["agent"], "fail", "stale-running recovered")
    while True:
        # 只取 queued 且依赖已满足(NULL 或指向的任务 done);按优先级、创建时间
        row = db.execute("""SELECT * FROM tasks WHERE status='queued'
            AND (depends_on IS NULL OR depends_on='' OR
                 depends_on IN (SELECT id FROM tasks WHERE status='done'))
            ORDER BY priority, created_at LIMIT 1""").fetchone()
        if not row: break
        db.execute("UPDATE tasks SET status='running',updated_at=datetime('now') WHERE id=?", (row["id"],)); db.commit()
        ev(db, row["id"], row["agent"], "claim")
        run_task(db, dict(row))

if __name__ == "__main__":
    main()
