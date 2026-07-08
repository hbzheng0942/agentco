#!/usr/bin/env python3
"""kb_gc.py — 知识库 ephemeral 原料回收(按 kb-governance.md 规则)。

只回收 tier=ephemeral 的采集原料(search_raw/community_raw/paper_raw),超 RETENTION_DAYS 天即删。
删前把溯源信息(路径/kind/content_hash/topics/日期/source_urls 数)追加进
kb/30-projects/<proj>/raw/_manifest.jsonl —— 原料可再生,靠 hash 溯源,不永久占地。
working/canonical(digest/decision/spec/...)绝不动。

⚠️ 默认 --dry-run(只报不删);--apply 才真删。上 cron 前请先 dry-run 审阅。

CLI:  kb_gc.py [--days 21] [--apply]   (缺省 dry-run)
"""
import argparse, json, re
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT

EPHEMERAL_KINDS = {"search_raw", "community_raw", "paper_raw"}


def _front(text):
    """极简 frontmatter 解析(kind/content_hash/topics/project/source_urls 计数)。"""
    if not text.startswith("---"):
        return {}
    fm = text.split("---", 2)[1] if text.count("---") >= 2 else ""
    out = {}
    m = re.search(r"^kind:\s*(\S+)", fm, re.M);       out["kind"] = m.group(1) if m else ""
    m = re.search(r"^content_hash:\s*(\S+)", fm, re.M); out["hash"] = m.group(1) if m else ""
    m = re.search(r"^project:\s*(\S+)", fm, re.M);    out["project"] = m.group(1) if m else ""
    m = re.search(r"^topic[s]?:\s*(.+)$", fm, re.M);  out["topic"] = m.group(1).strip() if m else ""
    out["n_urls"] = len(re.findall(r"^\s*-\s+https?://", fm, re.M))
    return out


def run_gc(days=21, apply=False):
    cutoff = datetime.now() - timedelta(days=days)
    reclaimed, kept, freed_bytes = [], 0, 0
    for raw_dir in ROOT.glob("kb/30-projects/*/raw"):
        for f in raw_dir.glob("*.md"):
            if f.name.startswith("_"):
                continue
            text = f.read_text(errors="ignore")
            meta = _front(text)
            if meta.get("kind") not in EPHEMERAL_KINDS:
                kept += 1
                continue
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime >= cutoff:
                kept += 1
                continue
            rec = {"path": str(f.relative_to(ROOT)), "kind": meta.get("kind"),
                   "content_hash": meta.get("hash"), "topic": meta.get("topic"),
                   "n_source_urls": meta.get("n_urls"), "mtime": mtime.strftime("%Y-%m-%d"),
                   "gc_at": datetime.now().strftime("%Y-%m-%d")}
            reclaimed.append(rec)
            freed_bytes += f.stat().st_size
            if apply:
                (raw_dir / "_manifest.jsonl").open("a").write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.unlink()
    mode = "已删除" if apply else "将删除(dry-run)"
    print(f"[kb_gc] {mode} {len(reclaimed)} 个 ephemeral 原料(>{days}天),"
          f"释放 {freed_bytes//1024} KB;保留 working/canonical 及新鲜原料 {kept} 个。")
    for r in reclaimed[:20]:
        print(f"  - {r['path']} [{r['kind']} {r['mtime']}]")
    if len(reclaimed) > 20:
        print(f"  … 及另外 {len(reclaimed)-20} 个")
    if not apply and reclaimed:
        print("  (dry-run;确认无误后加 --apply 真删,删前会写 _manifest.jsonl 溯源)")
    return reclaimed


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=21)
    ap.add_argument("--apply", action="store_true", help="真删(缺省 dry-run 只报)")
    a = ap.parse_args()
    run_gc(a.days, a.apply)
