#!/usr/bin/env python3
"""inbox_digest.py — 90-inbox 消化 SLA(每日 cron):
status: raw 且落地超 24h 的 idea-*.md 批量入队一个 digester light 任务归拢,
文件 frontmatter 置 status: digesting 防重复入队。产出(摘要+归档建议)照常走 inbox+飞书。"""
import re, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT, enqueue, load_env

load_env()
INBOX = ROOT/"kb/90-inbox"

def collect():
    stale = []
    for f in sorted(INBOX.glob("idea-*.md")):
        txt = f.read_text()
        if re.search(r"^status:\s*raw\s*$", txt, re.M) and time.time() - f.stat().st_mtime > 86400:
            stale.append(f)
    return stale

def main():
    stale = collect()
    if not stale:
        print("inbox 无滞留 idea"); return
    files = "\n".join(f"- {f.relative_to(ROOT)}" for f in stale)
    tid = enqueue("digester", f"inbox 消化:{len(stale)} 条滞留 idea",
                  f"逐条读取下列 idea 文件,产出:一句话摘要 + 处置建议(入项目KB/转任务/归档丢弃),"
                  f"表格化。只读分析,不改文件。\n\n{files}",
                  project="default", difficulty="light")
    for f in stale:
        f.write_text(re.sub(r"^status:\s*raw\s*$", "status: digesting", f.read_text(), flags=re.M))
    print(f"{tid} <- {len(stale)} idea")

if __name__ == "__main__":
    main()
