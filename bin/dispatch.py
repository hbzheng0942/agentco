#!/usr/bin/env python3
"""agentco dispatcher (Wave③) — 队列在 Codex 外,Codex 只当 worker。
cron 每 5 分钟;四域独立文件锁并行消费(域内串行),慢任务只阻塞本域。

Wave③ 变更:
- 工具域 4:retriever / executor-{code,data,3d} / digester / auditor(worker=profile 变体)。
- 路由:retriever/digester/auditor 产出→inbox&done;executor→review(机器验收)。
- retriever 预处理:codex 前先跑 search.py(query 取自 spec frontmatter)→ raw 注入上下文,模型不联网。
- 取任务:status='queued' 且依赖已 done,ORDER BY priority,created_at;依赖未 done 的任务是 waiting_dep,不占 worker。
- 依赖边:任务 done→扫 waiting_dep(depends_on==该 tid)→queued+dep_triggered;任务 blocked→下游标 dep_failed 进日报。
- 3D:executor-3d 入队即 waiting_gpu,不进主循环(bin/gpu_worker.sh 本地拉取)。
- skill_hit:spec 引用 skill 路径时记 event 并 bump use_count。
- 难度路由(Wave③后修订):tier=难度档(0=light 1=medium 2=heavy),派单时定;
  失败同档重试 2 次即 blocked,不再自动升档换厂商。
"""
import fcntl, multiprocessing, re, sqlite3, subprocess, sys, threading
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agentlib import load_env
load_env()  # cron 环境无 .env 变量;codex/feishu_card 子进程靠继承 os.environ 拿 LITELLM_MASTER_KEY 等

ROOT = Path(__file__).resolve().parent.parent
DB, TRACES, LOG = ROOT/"state.db", ROOT/"traces", ROOT/"logs/dispatch.log"
MAX_ATTEMPTS = 2

# 难度路由:tier=难度档(0=light 1=medium 2=heavy),入队时定,失败不自动升档。
# 多模态仅 GPT 通道(-hi profile)可用;auditor 刻意不给 GPT(审 executor 产出须异厂商)。
DIFF = {0: "light", 1: "medium", 2: "heavy"}
PROFILE = {  # (agent, tier) -> codex profile
    ("retriever", 0): "retriever",         ("retriever", 1): "retriever",         ("retriever", 2): "retriever-long",
    ("executor-code", 0): "executor-code", ("executor-code", 1): "executor-code-hi", ("executor-code", 2): "executor-code-hi",
    ("executor-data", 0): "executor-data", ("executor-data", 1): "executor-data-hi", ("executor-data", 2): "executor-data-hi",
    ("executor-3d", 0): "executor-3d",     ("executor-3d", 1): "executor-3d",     ("executor-3d", 2): "executor-3d",
    ("digester", 0): "digester",           ("digester", 1): "digester",           ("digester", 2): "digester-hi",
    ("auditor", 0): "auditor",             ("auditor", 1): "auditor",             ("auditor", 2): "auditor",
}
VALID_AGENTS = {"retriever", "executor-code", "executor-data", "executor-3d", "digester", "auditor"}
INBOX_AGENTS = {"retriever", "digester", "auditor"}   # 产出→inbox&done;其余(executor)→review

def log(msg):
    line = f"{datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line); LOG.parent.mkdir(exist_ok=True); LOG.open("a").write(line+"\n")

def feishu(text):
    subprocess.run([str(ROOT/"bin/feishu_push.sh"), text], check=False)

def feishu_archive(path, name):
    """md 产物存档到飞书云文档 agentco 目录,返回链接;未配凭据/失败返回 None(降级本地路径)。"""
    try:
        r = subprocess.run([sys.executable, str(ROOT/"bin/feishu_archive.py"), str(path), name],
                           capture_output=True, text=True, timeout=30)
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip().startswith("http") else None
    except Exception:
        return None

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

# ---- envelope 规范化:溯源字段(source_urls/content_hash)信模型,身份字段(model/tier/…)信 dispatcher ----
# 背景:envelope 由模型手写时格式漂移(yaml 围栏包裹/tier 错/model 自报不可信,T-20260706-003 审计实锤)。
_ENV_LINE = re.compile(r"^(?:[\w_]+:.*|-\s.*|---|```(?:yaml)?|#\s*envelope.*|\s*)$")

def split_envelope(final):
    """从产出末尾剥离模型手写 envelope(容忍 ``` 围栏/---/# envelope 标头),
    返回 (正文, source_urls行, content_hash)。无 envelope 返回 (原文, None, None)。"""
    lines = final.rstrip().splitlines()
    i = len(lines)
    while i > 0 and _ENV_LINE.match(lines[i-1]):
        i -= 1
    tail = "\n".join(lines[i:])
    if "task_id:" not in tail and "content_hash:" not in tail:
        return final.rstrip(), None, None
    m_urls = re.search(r"^source_urls:\s*(.+)$", tail, re.M)
    urls = m_urls.group(1).strip() if m_urls else None
    if urls is None and re.search(r"^source_urls:\s*$", tail, re.M):  # yaml 多行列表
        block = re.search(r"^source_urls:\s*\n((?:\s*-\s.*\n?)+)", tail, re.M)
        if block:
            urls = "[" + ", ".join(x.strip("- ").strip() for x in block.group(1).splitlines()) + "]"
    m_hash = re.search(r"^content_hash:\s*(\S+)", tail, re.M)
    return "\n".join(lines[:i]).rstrip(), urls, (m_hash.group(1) if m_hash else None)

def profile_model(profile):
    f = Path.home()/".codex"/f"{profile}.config.toml"
    if f.exists():
        m = re.search(r'^model\s*=\s*"([^"]+)"', f.read_text(), re.M)
        if m:
            return m.group(1)
    return "gpt-plus-default"   # -hi 档不写 model = 用 ChatGPT 登录账号默认模型

def canonical_envelope(t, profile, urls, chash, artifacts):
    return ("---\n"
            f"task_id: {t['id']}\nagent: {t['agent']}\nmodel: {profile_model(profile)}\n"
            f"tier: {t['tier']}\nproject: {t['project'] or 'default'}\n"
            f"depends_on: {t['depends_on'] or 'null'}\n"
            f"source_urls: {urls if urls else '[]'}\ncontent_hash: {chash or ''}\n"
            f"artifacts: [{', '.join(artifacts)}]\n---")

# ---- retriever 预处理:跑 search.py,把 raw 路径注入上下文 ----
def search_preprocess(db, t, spec):
    # query 行可多条(bridge 生成双语:query: / query_en: / query_zh: 都认)
    queries = [q.strip().strip('"').strip("'")
               for q in re.findall(r"^query(?:_[a-z]+)?:\s*(.+?)\s*$", spec, re.M) if q.strip()]
    if not queries:
        log(f"{t['id']} retriever 无 query 字段,跳过搜索预处理")
        return spec
    try:
        from search import run_search
        raw = run_search(queries, project=t["project"] or "default")
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
    spec_file = ROOT/t["spec_path"]
    if not spec_file.exists():   # spec 丢失(如项目目录被清理):blocked 进日报,绝不让单任务崩掉整个调度器
        ev(db, tid, agent, "block", f"spec missing: {t['spec_path']}")
        db.execute("UPDATE tasks SET status='blocked',updated_at=datetime('now') WHERE id=?", (tid,)); db.commit()
        feishu(f"🛑 {tid} {t['title']} BLOCKED:spec 文件丢失 {t['spec_path']},需人工裁决")
        propagate_block(db, t); return
    spec = spec_file.read_text()
    record_skill_hits(db, tid, agent, spec)
    if agent == "retriever":
        spec = search_preprocess(db, t, spec)
    trace_dir = TRACES/agent/datetime.now().strftime("%Y%m%d"); trace_dir.mkdir(parents=True, exist_ok=True)
    trace = trace_dir/f"{tid}.a{t['attempts']}.jsonl"
    log(f"{tid} -> {profile} (attempt {t['attempts']+1})")
    hb = None
    if t["notify"]:   # 长任务心跳:ttl 70% 仍未完 → 出站告知还活着,免得静默到超时
        hb_sec = max(60, int(t["ttl_sec"]*0.7))
        hb = threading.Timer(hb_sec, feishu,
            [f"⏳ {tid} {t['title']} 仍在运行(已 {hb_sec//60} 分钟,上限 {t['ttl_sec']//60} 分钟)agent={agent}"])
        hb.daemon = True; hb.start()
    try:
        r = subprocess.run(
            ["codex", "exec", "-p", profile, "--json",
             "--cd", str(ROOT), "--output-last-message", str(trace)+".final", "--", spec],
            capture_output=True, text=True, timeout=t["ttl_sec"])
        trace.write_text(r.stdout + (f"\n\n# stderr\n{r.stderr}" if r.stderr else ""))
        ok = r.returncode == 0 and Path(str(trace)+".final").exists()
    except subprocess.TimeoutExpired:
        ok = False
        ev(db, tid, agent, "fail", "timeout")
    finally:
        if hb:
            hb.cancel()

    if ok:
        final = Path(str(trace)+".final").read_text()
        body, urls, chash = split_envelope(final)
        if urls is None and chash is None:
            ev(db, tid, agent, "envelope_missing", profile)   # 模型没写 envelope,进周治理统计
        proj = t["project"] or "default"
        out = ROOT/"handoff"/proj/f"{tid}.result.md"          # 与 spec 同项目目录,禁扁平落 handoff/
        out.parent.mkdir(parents=True, exist_ok=True)
        artifacts = [str(out.relative_to(ROOT))]
        inbox = None
        if agent in INBOX_AGENTS:
            inbox = ROOT/"kb/90-inbox"/f"{tid}-{agent}.md"
            artifacts.append(str(inbox.relative_to(ROOT)))
        envelope = canonical_envelope(t, profile, urls, chash, artifacts)
        out.write_text(f"# {tid} result ({agent}/{profile})\n\n{body}\n\n{envelope}\n")
        if inbox is not None:       # retriever/digester/auditor 直接闭环落 inbox
            inbox.write_text(f"---\nsource: {agent}\ntask: {tid}\nproject: {proj}\n"
                             f"date: {datetime.now():%Y-%m-%d}\nstatus: raw\n---\n\n{body}\n\n{envelope}\n")
            new_status = "done"
        else:                       # executor → review(机器验收)
            new_status = "review"
        db.execute("UPDATE tasks SET status=?,result_path=?,updated_at=datetime('now') WHERE id=?",
                   (new_status, str(out.relative_to(ROOT)), tid))
        ev(db, tid, agent, "done", profile)
        if new_status == "done":
            trigger_dependents(db, tid)
        if t["notify"]:
            paths = " ; ".join(artifacts)
            if new_status == "review":
                subprocess.run([sys.executable, str(ROOT/"bin/feishu_card.py"),
                                tid, t["title"], f"📄 {paths}\n\n{body[:600]}"], check=False)
            else:
                head = f"✅ {tid} {t['title']}\nagent={agent} difficulty={DIFF.get(tier, tier)}\n📄 {paths}"
                link = feishu_archive(inbox or out, f"{tid}-{agent}.md")
                if link:            # md 产物已存档飞书:发链接+摘要,不刷全文
                    feishu(f"{head}\n☁️ {link}\n---\n{body[:300]}")
                elif len(body) <= 800:   # 无存档通道:短产出退全文
                    feishu(f"{head}\n---\n{body}")
                else:
                    feishu(f"{head}\n(超800字,全文见上述路径)\n---\n{body[:800]}")
    else:
        attempts = t["attempts"]+1
        # 失败不换厂商:难度是入队时已知的任务属性,失败是给人看的信号(裁决后可改难度重派)
        if attempts >= MAX_ATTEMPTS:
            db.execute("UPDATE tasks SET status='blocked',attempts=?,updated_at=datetime('now') WHERE id=?", (attempts, tid))
            ev(db, tid, agent, "block", f"max attempts at difficulty={DIFF.get(tier, tier)}")
            feishu(f"🛑 {tid} {t['title']} BLOCKED,需人工裁决(可改难度重派)。trace: {trace}")
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

# ---- 域级并发:四域各持独立锁并行消费,慢任务只阻塞本域,不再队头阻塞全队 ----
DOMAINS = ("retriever", "executor", "digester", "auditor")

def connect():
    db = sqlite3.connect(DB, timeout=30); db.row_factory = sqlite3.Row
    db.execute("PRAGMA busy_timeout=30000")   # WAL + busy_timeout:多域写者共存
    return db

def domain_loop(domain):
    lock = open(ROOT/f".dispatch.{domain}.lock", "w")
    try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError: return            # 该域上一轮还在跑,跳过(其余域不受影响)
    sys.path.insert(0, str(ROOT/"bin"))       # for `import search`
    db = connect()
    like = domain + "-%"
    # 僵尸回收(本域):running 超 2×ttl → 重排
    for s in db.execute("""SELECT id,agent FROM tasks WHERE status='running'
        AND (agent=? OR agent LIKE ?)
        AND (strftime('%s','now')-strftime('%s',updated_at)) > 2*ttl_sec""", (domain, like)).fetchall():
        db.execute("UPDATE tasks SET status='queued',attempts=attempts+1,updated_at=datetime('now') WHERE id=?", (s["id"],))
        ev(db, s["id"], s["agent"], "fail", "stale-running recovered")
    while True:
        # 只取本域 queued 且依赖已满足(NULL 或指向的任务 done);按优先级、创建时间
        row = db.execute("""SELECT * FROM tasks WHERE status='queued'
            AND (agent=? OR agent LIKE ?)
            AND (depends_on IS NULL OR depends_on='' OR
                 depends_on IN (SELECT id FROM tasks WHERE status='done'))
            ORDER BY priority, created_at LIMIT 1""", (domain, like)).fetchone()
        if not row: break
        db.execute("UPDATE tasks SET status='running',updated_at=datetime('now') WHERE id=?", (row["id"],)); db.commit()
        ev(db, row["id"], row["agent"], "claim", f"domain={domain}")
        run_task(db, dict(row))

def _ready_count(db):
    return db.execute("""SELECT count(*) FROM tasks WHERE status='queued'
        AND (depends_on IS NULL OR depends_on='' OR
             depends_on IN (SELECT id FROM tasks WHERE status='done'))""").fetchone()[0]

def main():
    # 最多 3 轮:上游 done 触发的跨域下游任务(dep_triggered)同一次 cron 内接力消费,不等下轮
    for _ in range(3):
        procs = [multiprocessing.Process(target=domain_loop, args=(d,)) for d in DOMAINS]
        for p in procs: p.start()
        for p in procs: p.join()
        if _ready_count(connect()) == 0:
            break

if __name__ == "__main__":
    main()
