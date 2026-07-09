#!/usr/bin/env python3
"""l1_enqueue.py — inspiration L1 蒸馏放量:transcripts 有、卡没有的视频批量入队 digester

去重三层:digest/cards/ 已有卡 | kb/90-inbox 已有产出 | 队列在途(spec 含 video_id 且非 blocked)。
分波投放:--limit 控制每波数量(默认 5),先小波看质量再放大。

用法:
  l1_enqueue.py --dry-run          # 只列待办,不入队
  l1_enqueue.py --limit 10         # 入队 10 个
"""
import argparse, json, re, sqlite3, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import enqueue

ROOT = Path(__file__).resolve().parent.parent
SLUG = "stefan-3d-ai"
BASE = ROOT / "data/inspiration" / SLUG

BODY = """# 任务
L1 蒸馏任务。先完整阅读并严格执行共享规约: kb/30-projects/inspiration/specs/l1-distill-spec.md(v1.1,全部13条规则)。
处理对象: video_id={vid}
inventory 标题:《{title}》
品类: 未预标注——按规约规则13自行判断品类;与 workflow card 不匹配时写【schema适配备注】再尽力填充。
转写: data/inspiration/{slug}/transcripts/{vid}.txt
禁止读取任何 *.golden.md。

# 验收
- 按 AGENT.md 规定格式输出
- 末尾必附 envelope(task_id/agent/model/tier/project/source_urls/content_hash/depends_on/artifacts)
"""


def carded_ids():
    """已有卡或在途任务覆盖的 video_id 集合"""
    ids = set()
    for d in (ROOT / "kb/30-projects/inspiration/digest/cards",
              ROOT / "kb/90-inbox"):
        if not d.exists():
            continue
        for f in d.glob("*.md"):
            # 覆盖多种写法:video_id: X / video_id=X / 表格 | video_id | X | / `video_id`: `X`
            ids |= set(re.findall(r"video_id`?\s*[:=|]\s*`?([\w-]{11})`?", f.read_text()))
    db = sqlite3.connect(ROOT / "state.db")
    db.row_factory = sqlite3.Row
    for r in db.execute("SELECT spec_path FROM tasks WHERE agent='digester' "
                        "AND project='inspiration' AND status IN ('queued','running','review','done')"):
        p = ROOT / r["spec_path"]
        if p.exists():
            ids |= set(re.findall(r"video_id=([\w-]{11})", p.read_text()))
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    inv = {v["id"]: v.get("title", "") for v in
           json.loads((BASE / "inventory.json").read_text()).get("entries", [])}
    have_tx = {p.stem for p in (BASE / "transcripts").glob("*.txt")}
    done = carded_ids()
    # 按 inventory 顺序(新→旧)取未蒸馏的
    todo = [vid for vid in inv if vid in have_tx and vid not in done]
    print(f"transcripts={len(have_tx)} 已覆盖={len(have_tx & done)} 待蒸馏={len(todo)}")
    for vid in todo[: a.limit]:
        title = inv[vid]
        if a.dry_run:
            print(f"  DRY {vid} {title[:60]}")
            continue
        tid = enqueue("digester", f"L1蒸馏·{title[:40]}",
                      BODY.format(vid=vid, title=title, slug=SLUG),
                      project="inspiration", priority=2)
        print(f"  {tid} {vid} {title[:60]}")


if __name__ == "__main__":
    main()
