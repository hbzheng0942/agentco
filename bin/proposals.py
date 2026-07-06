#!/usr/bin/env python3
"""proposals.py — 进化闭环:auditor 提议 → 人裁决 → apply 任务 → 下周复检,全程入库可度量。
状态机:proposed →(人)adopted|rejected;adopted→apply 任务→(人验收 adopt)applied;→(auditor 复检)verified。

子命令:
  ingest <result_file> [--src-task TID]   解析 auditor 产出中的 PROPOSAL/VERIFY 区块入库+推送裁决链接
  set <P-id> <adopt|reject> [--note N]    裁决;adopt 自动入队 executor apply 任务(产出 patch 仍走 review)
  list [--status S] / dump-open           查看 / 给 weekly spec 注入未闭环提议
  mark-applied <apply_task_tid>           apply 任务验收采纳时回写 applied(apply_review 调用)

auditor 产出格式约定(weekly spec 注入):
  ### PROPOSAL: <标题>
  target: <目标文件>
  ```
  <可直接应用的最终文本/diff>
  ```
  复检通过的旧提议写:### VERIFY P-xxxxWxx-NN: ok|fail <一句话证据>
"""
import argparse, os, re, subprocess, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT, db, ev, enqueue, load_env, sign

load_env()

_P = re.compile(r"^###\s*PROPOSAL:\s*(.+?)\s*$\n(?:target:\s*(.+?)\s*$\n)?"
                r"(?:.*?```[a-z]*\n(.*?)\n```)?", re.M | re.S)
_V = re.compile(r"^###\s*VERIFY\s+(P-\S+):\s*(ok|fail)\s*(.*)$", re.M)


def push(text):
    subprocess.run([str(ROOT/"bin/feishu_push.sh"), text], check=False)


def ingest(path, src_task=""):
    text = Path(path).read_text()
    week = f"{datetime.now():%G}W{datetime.now():%V}"
    c = db()
    n = c.execute("SELECT count(*) FROM proposals WHERE week=?", (week,)).fetchone()[0]
    base = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")
    new = 0
    for m in _P.finditer(text):
        title, target, diff = m.group(1)[:120], (m.group(2) or "")[:200], (m.group(3) or "")[:4000]
        n += 1
        pid = f"P-{week}-{n:02d}"
        c.execute("INSERT INTO proposals(id,week,title,target,diff,src_task) VALUES(?,?,?,?,?,?)",
                  (pid, week, title, target, diff, src_task))
        ev(c, src_task or pid, "auditor", "proposal", pid)
        new += 1
        if base:
            adopt = f"{base}/proposal?id={pid}&action=adopt&s={sign(pid, 'adopt')}"
            reject = f"{base}/proposal?id={pid}&action=reject&s={sign(pid, 'reject')}"
            push(f"🧬 提议 {pid} {title}\ntarget: {target or '(未指明)'}\n"
                 f"✅采纳 {adopt}\n🗑拒绝 {reject}")
    for m in _V.finditer(text):   # auditor 复检旧提议:applied → verified(fail 则退回 adopted 并留痕)
        pid, verdict, note = m.group(1), m.group(2), m.group(3)[:200]
        st = "verified" if verdict == "ok" else "adopted"
        c.execute("UPDATE proposals SET status=?,note=?,updated_at=datetime('now') "
                  "WHERE id=? AND status='applied'", (st, f"复检{verdict}: {note}", pid))
        ev(c, src_task or pid, "auditor", "proposal_verify", f"{pid} {verdict}")
    c.commit()
    print(f"ingested={new}")


def set_status(pid, action, note=""):
    c = db()
    p = c.execute("SELECT * FROM proposals WHERE id=?", (pid,)).fetchone()
    if not p:
        print(f"不存在 {pid}"); return 1
    if p["status"] != "proposed":
        print(f"{pid} 当前 {p['status']},不可重复裁决"); return 1
    if action == "adopt":
        tid = enqueue("executor-code", f"apply {pid}: {p['title']}"[:60],
                      f"应用进化提议 {pid}(来源 {p['src_task']}),target: {p['target']}\n"
                      f"产出可直接应用的最终 patch,走 review 人工验收。\n\n# 提议内容\n{p['diff']}",
                      project="system", difficulty="light")
        c.execute("UPDATE proposals SET status='adopted',apply_task=?,note=?,updated_at=datetime('now') WHERE id=?",
                  (tid, note, pid))
        ev(c, tid, "executor-code", "proposal_adopt", pid)
        print(f"{pid} adopted → apply任务 {tid}")
    else:
        c.execute("UPDATE proposals SET status='rejected',note=?,updated_at=datetime('now') WHERE id=?", (note, pid))
        ev(c, pid, "auditor", "proposal_reject", pid)
        print(f"{pid} rejected")
    c.commit(); return 0


def mark_applied(apply_tid):
    c = db()
    c.execute("UPDATE proposals SET status='applied',updated_at=datetime('now') "
              "WHERE apply_task=? AND status='adopted'", (apply_tid,))
    c.commit()


def dump_open():
    c = db()
    rows = c.execute("SELECT id,status,title,target,apply_task FROM proposals "
                     "WHERE status IN ('proposed','adopted','applied') ORDER BY ts").fetchall()
    if not rows:
        print("(无未闭环提议)"); return
    for r in rows:
        print(f"{r['id']} | {r['status']} | {r['title']} | target={r['target']} | apply={r['apply_task'] or '-'}")


if __name__ == "__main__":
    a = argparse.ArgumentParser(); sub = a.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("ingest"); s.add_argument("file"); s.add_argument("--src-task", default="")
    s = sub.add_parser("set"); s.add_argument("pid"); s.add_argument("action", choices=["adopt", "reject"])
    s.add_argument("--note", default="")
    s = sub.add_parser("list"); s.add_argument("--status")
    sub.add_parser("dump-open")
    s = sub.add_parser("mark-applied"); s.add_argument("tid")
    ar = a.parse_args()
    if ar.cmd == "ingest": ingest(ar.file, ar.src_task)
    elif ar.cmd == "set": sys.exit(set_status(ar.pid, ar.action, ar.note))
    elif ar.cmd == "list":
        for r in db().execute("SELECT id,status,title FROM proposals" +
                              (" WHERE status=?" if ar.status else ""),
                              ((ar.status,) if ar.status else ())).fetchall():
            print(f"{r['id']} | {r['status']} | {r['title']}")
    elif ar.cmd == "dump-open": dump_open()
    elif ar.cmd == "mark-applied": mark_applied(ar.tid)
