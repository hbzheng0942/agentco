#!/usr/bin/env python3
"""cache_gc.py — 近两周 raw 缓存清理(并入 daily cron)。

删 kb/30-projects/*/raw/ 下 mtime > 14 天的文件。
**危险动作**:删前先扫 decisions/ 的引用做豁免——被 done 决策 envelope 引用的原始快照必须保留,
否则断掉 envelope 溯源链。顺序铁律:先扫 decisions → 分类 → 记 event → 再删。

豁免判定:raw 的 文件名 / content_hash / 任一 source_url 出现在任一 decision 文件文本中 → 保留。

用法:cache_gc.py [--days 14] [--dry-run]
"""
import argparse, re, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT, db, ev

RAW_GLOB = "kb/30-projects/*/raw/*"
DECISIONS_GLOB = "kb/30-projects/*/decisions/**/*"


def collect_decision_refs():
    """先扫 decisions/,汇总全部决策文本(引用面)。删除前调用——顺序不可颠倒。"""
    blob = []
    for f in ROOT.glob(DECISIONS_GLOB):
        if f.is_file() and f.suffix in (".md", ".txt", ".yaml", ".yml", ".json"):
            try:
                blob.append(f.read_text(errors="ignore"))
            except Exception:
                pass
    return "\n".join(blob)


def raw_tokens(raw_path):
    """一个 raw 文件的可被引用标识:文件名 + content_hash + source_urls。"""
    toks = {raw_path.name, raw_path.stem}
    try:
        head = raw_path.read_text(errors="ignore")[:4000]
    except Exception:
        return toks
    m = re.search(r"^content_hash:\s*(\S+)", head, re.M)
    if m:
        toks.add(m.group(1).strip())
    for um in re.finditer(r"^\s*-\s*(https?://\S+)", head, re.M):
        toks.add(um.group(1).strip())
    return {t for t in toks if t}


def is_exempt(raw_path, decisions_blob):
    return any(tok and tok in decisions_blob for tok in raw_tokens(raw_path))


def gc(days=14, dry_run=False):
    cutoff = time.time() - days * 86400
    decisions_blob = collect_decision_refs()          # ① 先扫 decisions(豁免面)
    to_delete, exempt = [], []
    for f in ROOT.glob(RAW_GLOB):                      # ② 分类
        if not f.is_file() or f.name == ".gitkeep":
            continue
        if f.stat().st_mtime >= cutoff:
            continue                                    # 未过期
        if is_exempt(f, decisions_blob):
            exempt.append(f)                            # 被决策引用 → 保留
        else:
            to_delete.append(f)
    c = db()
    ev(c, None, "cache_gc", "cache_gc",                # ③ 记 event(删前)
       f"deleted={len(to_delete)} exempt={len(exempt)} days>{days}"
       + (" dry-run" if dry_run else ""))
    if not dry_run:
        for f in to_delete:                             # ④ 再删
            f.unlink(missing_ok=True)
    return to_delete, exempt


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    dele, exe = gc(a.days, a.dry_run)
    print(f"cache_gc: {'would delete' if a.dry_run else 'deleted'} {len(dele)}, exempt {len(exe)}")
    for f in exe:
        print(f"  exempt(引用保留): {f.relative_to(ROOT)}")
