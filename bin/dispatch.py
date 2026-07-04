#!/usr/bin/env python3
"""agentco dispatcher — 队列在Codex外,Codex只当worker(官方推荐形态).
cron每5分钟跑一次;文件锁防重入;串行消费(一人公司不需要并发调度器).
"""
import fcntl, json, os, sqlite3, subprocess, sys, time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB, TRACES, LOG = ROOT/"state.db", ROOT/"traces", ROOT/"logs/dispatch.log"
MAX_ATTEMPTS_PER_TIER, MAX_TIER = 2, 1
PROFILE = {  # (agent, tier) -> codex profile
    ("owl-intel", 0): "owl-intel", ("owl-intel", 1): "owl-intel-hi",
    ("exec-ds", 0): "exec-ds",     ("exec-ds", 1): "exec-hi",
    ("critic", 0): "critic",       ("critic", 1): "critic-hi",
}

def log(msg):
    line = f"{datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line); LOG.parent.mkdir(exist_ok=True); LOG.open("a").write(line+"\n")

def feishu(text):
    subprocess.run([str(ROOT/"bin/feishu_push.sh"), text], check=False)

def ev(db, task_id, agent, kind, detail=""):
    db.execute("INSERT INTO events(task_id,agent,kind,detail) VALUES(?,?,?,?)",
               (task_id, agent, kind, detail)); db.commit()

def run_task(db, t):
    tid, agent, tier = t["id"], t["agent"], t["tier"]
    profile = PROFILE.get((agent, tier))
    if not profile:
        ev(db, tid, agent, "block", f"no profile for tier {tier}")
        db.execute("UPDATE tasks SET status='blocked',updated_at=datetime('now') WHERE id=?", (tid,)); db.commit()
        return
    spec = (ROOT/t["spec_path"]).read_text()
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
        ok, r = False, None
        ev(db, tid, agent, "fail", "timeout")

    if ok:
        final = Path(str(trace)+".final").read_text()
        out = ROOT/"handoff"/f"{tid}.result.md"
        out.write_text(f"# {tid} result ({agent}/{profile})\n\n{final}\n")
        # intel/critic产出直接落盘90-inbox(headless下dispatcher即"父会话"),并自动闭环
        if agent in ("owl-intel", "critic"):
            inbox = ROOT/"kb/90-inbox"/f"{tid}-{agent}.md"
            inbox.write_text(f"---\nsource: {agent}\ntask: {tid}\ndate: {datetime.now():%Y-%m-%d}\nstatus: raw\n---\n\n{final}\n")
            new_status = "done"
        else:
            new_status = "review"   # build类任务等人工验收(bin/review.py)
        db.execute("UPDATE tasks SET status=?,result_path=?,updated_at=datetime('now') WHERE id=?",
                   (new_status, str(out.relative_to(ROOT)), tid))
        ev(db, tid, agent, "done", profile)
        if t["notify"]:
            if new_status == "review":   # 待验收 → 交互卡片(一键采纳/返工/废弃)
                subprocess.run([sys.executable, str(ROOT/"bin/feishu_card.py"),
                                tid, t["title"], final[:600]], check=False)
            else:
                feishu(f"✅ {tid} {t['title']}\nagent={agent} tier={tier}\n---\n{final[:800]}")
    else:
        attempts = t["attempts"]+1
        if attempts >= MAX_ATTEMPTS_PER_TIER and tier < MAX_TIER:
            db.execute("UPDATE tasks SET tier=tier+1,attempts=0,status='queued',updated_at=datetime('now') WHERE id=?", (tid,))
            ev(db, tid, agent, "escalate", f"tier{tier}->{tier+1}")
            log(f"{tid} escalated")
        elif attempts >= MAX_ATTEMPTS_PER_TIER:
            db.execute("UPDATE tasks SET status='blocked',attempts=?,updated_at=datetime('now') WHERE id=?", (attempts, tid))
            ev(db, tid, agent, "block", "max attempts at max tier")
            feishu(f"🛑 {tid} {t['title']} BLOCKED,需人工。trace: {trace}")
        else:
            db.execute("UPDATE tasks SET attempts=?,status='queued',updated_at=datetime('now') WHERE id=?", (attempts, tid))
            ev(db, tid, agent, "fail", f"attempt {attempts}")
    db.commit()

def main():
    lock = open(ROOT/".dispatch.lock", "w")
    try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError: sys.exit(0)  # 上一轮还在跑
    db = sqlite3.connect(DB); db.row_factory = sqlite3.Row
    # 崩溃/重启恢复:running超过2×ttl视为僵尸,回收重排并记账
    stale = db.execute("""SELECT id,agent FROM tasks WHERE status='running'
        AND (strftime('%s','now')-strftime('%s',updated_at)) > 2*ttl_sec""").fetchall()
    for s in stale:
        db.execute("UPDATE tasks SET status='queued',attempts=attempts+1,updated_at=datetime('now') WHERE id=?", (s["id"],))
        ev(db, s["id"], s["agent"], "fail", "stale-running recovered")
    while True:
        row = db.execute("SELECT * FROM tasks WHERE status='queued' ORDER BY created_at LIMIT 1").fetchone()
        if not row: break
        db.execute("UPDATE tasks SET status='running',updated_at=datetime('now') WHERE id=?", (row["id"],)); db.commit()
        ev(db, row["id"], row["agent"], "claim")
        run_task(db, dict(row))

if __name__ == "__main__":
    main()
