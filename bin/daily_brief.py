#!/usr/bin/env python3
"""daily_brief.py — 每日简报(cron 0 22 * * *)。

**只读原始 events/feedback/decisions/shared 变更,禁读其他 Auditor 产出(防套娃)。**
五段,空段省略:
  ⚡需你决策(review 任务,复用 feishu_card link 按钮直裁)
  📦今日产出(done,采纳态一行一条)
  🔧架构自变更(shared breaking/non + skill 增删)
  ⏳遗留(blocked/dep_failed/超期)
  📊健康度一行
决策段对每个 review 任务发交互卡片(采纳/返工/废弃直达 gateway)。
"""
import subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT, db

WIN = "-1 day"


def build_brief(c):
    sections, decisions = [], []

    # ⚡ 需你决策:待人工验收的 review 任务
    review = c.execute("SELECT id,title,agent,project FROM tasks WHERE status='review' "
                       "ORDER BY priority,created_at").fetchall()
    if review:
        lines = ["⚡ **需你决策**"]
        for r in review:
            lines.append(f"- {r['id']} [{r['project']}/{r['agent']}] {r['title']}")
            decisions.append(dict(r))
        sections.append("\n".join(lines))

    # 📦 今日产出:done 任务 + 采纳态(feedback 信号优先)
    done = c.execute(f"""SELECT t.id,t.title,t.project,t.agent,
        (SELECT signal FROM feedback f WHERE f.task_id=t.id ORDER BY f.id DESC LIMIT 1) sig
        FROM tasks t WHERE t.status='done' AND t.updated_at > datetime('now','{WIN}')
        ORDER BY t.updated_at""").fetchall()
    if done:
        lines = ["📦 **今日产出**"]
        for r in done:
            lines.append(f"- {r['id']} [{r['project']}/{r['agent']}] {r['title']} · {r['sig'] or '已归档'}")
        sections.append("\n".join(lines))

    # 🔧 架构自变更:shared breaking/non + skill 增删
    arch = c.execute(f"""SELECT kind,detail,count(*) n FROM events
        WHERE kind IN ('shared_breaking','shared_change','shared_new','skill_new','skill_archive','skill_merge')
        AND ts > datetime('now','{WIN}') GROUP BY kind,detail""").fetchall()
    if arch:
        lines = ["🔧 **架构自变更**"]
        for r in arch:
            lines.append(f"- {r['kind']}: {r['detail']}" + (f" ×{r['n']}" if r['n'] > 1 else ""))
        sections.append("\n".join(lines))

    # ⏳ 遗留:blocked / dep_failed / 超期(running 超 2×ttl 或 queued 超 1 天)
    left = c.execute("""SELECT id,title,project,status FROM tasks
        WHERE status IN ('blocked','dep_failed')
        OR (status='running' AND (strftime('%s','now')-strftime('%s',updated_at)) > 2*ttl_sec)
        OR (status='queued' AND created_at < datetime('now','-1 day'))
        ORDER BY status,created_at""").fetchall()
    if left:
        lines = ["⏳ **遗留**"]
        for r in left:
            lines.append(f"- [{r['status']}] {r['id']} [{r['project']}] {r['title']}")
        sections.append("\n".join(lines))

    # 📊 健康度一行
    h = {s: c.execute("SELECT count(*) FROM tasks WHERE status=?", (s,)).fetchone()[0]
         for s in ("queued", "running", "review", "waiting_dep", "waiting_gpu", "blocked", "dep_failed")}
    done_today = c.execute(f"SELECT count(*) FROM tasks WHERE status='done' AND updated_at>datetime('now','{WIN}')").fetchone()[0]
    sections.append(f"📊 **健康度** queued={h['queued']} running={h['running']} review={h['review']} "
                    f"waiting(dep/gpu)={h['waiting_dep']}/{h['waiting_gpu']} "
                    f"blocked={h['blocked']} dep_failed={h['dep_failed']} done24h={done_today}")

    return "\n\n".join(sections), decisions


def main():
    c = db()
    text, decisions = build_brief(c)
    from datetime import datetime
    header = f"📮 每日简报 {datetime.now():%Y-%m-%d}\n\n"
    subprocess.run([str(ROOT/"bin/feishu_push.sh"), header + text], check=False)
    # 决策段:每个 review 任务发交互卡片(按钮直裁)
    for d in decisions:
        rp = c.execute("SELECT result_path FROM tasks WHERE id=?", (d["id"],)).fetchone()
        preview = ""
        if rp and rp["result_path"] and (ROOT/rp["result_path"]).exists():
            preview = (ROOT/rp["result_path"]).read_text()[:600]
        subprocess.run([sys.executable, str(ROOT/"bin/feishu_card.py"), d["id"], d["title"], preview], check=False)
    print(header + text)


if __name__ == "__main__":
    main()
