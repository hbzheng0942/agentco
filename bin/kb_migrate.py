#!/usr/bin/env python3
"""kb_migrate.py — 存量文件治理迁移(回填 scope/tier/topics frontmatter)。

按 kb-governance.md,给现有 md 回填治理元数据(scope/tier + 种子 topics),
让 GC/Feishu 路由/图谱能工作。**只添加缺失字段,绝不修改已有字段,不移动文件**(保守)。
默认 --dry-run(只报);--apply 才写。

推断规则:
- scope: 路径前缀(00-core→core / 10-domain→resource / 30-projects→project / 40-areas→area /
  99-archive→archive / 90-inbox→跳过(分诊区不回填))
- tier: kind 或路径(raw/*→ephemeral,digest/*→working,decisions|specs|retro→canonical,core→canonical)
- topics 种子: [scope对象名(项目/area)] + 标题里命中 concept-index 的概念词

CLI:  kb_migrate.py [--apply]
"""
import argparse, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT

KB = ROOT / "kb"
EPHEMERAL = {"search_raw", "community_raw", "paper_raw"}
WORKING = {"digest", "paper_digest", "research_report", "intel"}
CANONICAL = {"decision", "battle", "spec", "prd", "retro", "domain", "concept",
             "governance", "principle", "index", "governance"}


def _concept_terms():
    ci = KB / "00-core/concept-index.md"
    if not ci.exists():
        return []
    return sorted({t.strip() for t in re.findall(r"^\s*[-*#]+\s*([A-Za-z一-鿿][^\|:\n]{1,24})",
                                                  ci.read_text(errors="ignore"), re.M)}, key=len, reverse=True)


def _scope_of(rel):
    p = rel.replace("\\", "/")
    if p.startswith("kb/00-core"): return "core", ""
    if p.startswith("kb/10-domain"): return "resource", ""
    if p.startswith("kb/20-intel"): return "area", "intel"
    if p.startswith("kb/40-areas/"): return "area", p.split("/")[2] if len(p.split("/")) > 2 else ""
    if p.startswith("kb/30-projects/"): return "project", p.split("/")[2] if len(p.split("/")) > 2 else ""
    if p.startswith("kb/99-archive"): return "archive", ""
    return "", ""   # 90-inbox 等 → 跳过


def _tier_of(kind, rel):
    if kind in EPHEMERAL: return "ephemeral"
    if kind in WORKING: return "working"
    if kind in CANONICAL: return "canonical"
    p = rel.replace("\\", "/")
    if "/raw/" in p: return "ephemeral"
    if "/digest/" in p: return "working"
    if any(s in p for s in ("/decisions/", "/specs/", "/retro/")) or p.startswith("kb/00-core") or p.startswith("kb/10-domain"):
        return "canonical"
    return "working"


def _has(fm, key):
    return re.search(rf"^{key}:", fm, re.M) is not None


def _get(fm, key):
    m = re.search(rf"^{key}:\s*(.+)$", fm, re.M)
    return m.group(1).strip() if m else ""


def plan(concepts):
    changes = []
    for path in KB.rglob("*.md"):
        if path.name.startswith("_") or path.name == "topic-graph.md":
            continue
        rel = str(path.relative_to(ROOT))
        scope, obj = _scope_of(rel)
        if not scope:
            continue   # inbox 等分诊区跳过
        text = path.read_text(errors="ignore")
        fm = text.split("---", 2)[1] if text.startswith("---") and text.count("---") >= 2 else ""
        kind = _get(fm, "kind")
        add = {}
        tier = _tier_of(kind, rel)
        if not _has(fm, "scope"): add["scope"] = scope
        if not _has(fm, "tier"): add["tier"] = tier
        # 种子 topics 只给 working/canonical(ephemeral 原料会被 GC,不值得),
        # 且只用有意义的 项目/area 名(跳过 default;概念匹配太噪弃用,topics 由产出方逐步补)
        if not _has(fm, "topics") and tier in ("working", "canonical") and obj and obj != "default":
            add["topics"] = f"[{obj}]"
        if add:
            changes.append((path, text, add))
    return changes


def apply_changes(changes):
    for path, text, add in changes:
        lines = [f"{k}: {v}" for k, v in add.items()]
        if text.startswith("---") and text.count("---") >= 2:
            i = text.index("---", 3)          # 第二个 --- 位置
            new = text[:i] + "\n".join(lines) + "\n" + text[i:]
        else:                                  # 无 frontmatter → 新建
            new = "---\n" + "\n".join(lines) + "\n---\n\n" + text
        path.write_text(new)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    changes = plan(_concept_terms())
    print(f"[kb_migrate] {'已回填' if a.apply else '将回填(dry-run)'} {len(changes)} 个文件的治理元数据")
    for path, _, add in changes[:30]:
        print(f"  - {path.relative_to(ROOT)}: +{add}")
    if len(changes) > 30:
        print(f"  … 及另外 {len(changes)-30} 个")
    if a.apply:
        apply_changes(changes)
        print("  已写入(只加缺失字段,未改已有);建议 git diff 复核后提交,再跑 kb_graph.py 刷新图谱")
    elif changes:
        print("  (dry-run;--apply 落盘)")
