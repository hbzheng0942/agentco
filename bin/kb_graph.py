#!/usr/bin/env python3
"""kb_graph.py — 知识库 cross-topic 图谱构建器(治理图谱底座)。

读全库 md 的 frontmatter(topics/entities/links/scope/kind)+ 正文 [[链接]],
构建 节点(文件/主题/实体)与 边(文件-主题、文件-实体、文件-文件),产出:
- kb/00-core/topic-graph.md —— 人读总览:主题按覆盖度排序、跨 scope 桥接主题(启发点)、孤儿文件
- state/kb_graph.json —— 机读 节点/边,供后续工具/可视化

主题词典来自 kb/00-core/concept-index.md(权威登记)+ 文件 frontmatter.topics。
随文件逐步补 topics(见 kb-governance.md),图谱自动变密。只读,不改任何文件。

CLI:  kb_graph.py [--json-only]
"""
import argparse, json, re, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT

KB = ROOT / "kb"
LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def _parse(path):
    text = path.read_text(errors="ignore")
    fm, body = "", text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm, body = parts[1], parts[2]

    def _list(key):
        m = re.search(rf"^{key}:\s*\[(.*?)\]", fm, re.M)
        if m:
            return [x.strip().strip('"\'') for x in m.group(1).split(",") if x.strip()]
        m = re.search(rf"^{key}:\s*\n((?:\s*-\s.*\n?)+)", fm, re.M)
        if m:
            return [ln.strip("- \t").strip() for ln in m.group(1).splitlines() if ln.strip()]
        return []

    def _val(key):
        m = re.search(rf"^{key}:\s*(.+)$", fm, re.M)
        return m.group(1).strip() if m else ""

    title = ""
    mt = re.search(r"^#\s+(.+)$", body, re.M)
    if mt:
        title = mt.group(1).strip()
    links = set(_list("links")) | set(LINK_RE.findall(body))
    return {
        "path": str(path.relative_to(ROOT)),
        "name": path.stem,
        "title": title or path.stem,
        "kind": _val("kind"), "tier": _val("tier"), "scope": _val("scope"),
        "project": _val("project") or _val("area"),
        "topics": _list("topics"), "entities": _list("entities"),
        "links": sorted(links),
    }


def _concepts():
    """concept-index.md 里登记的概念词,作为主题词典种子。"""
    ci = KB / "00-core/concept-index.md"
    if not ci.exists():
        return []
    # 取形如 `- 概念名` / `| 概念名 |` / `## 概念名` 的词条(宽松)
    txt = ci.read_text(errors="ignore")
    return sorted(set(re.findall(r"^\s*[-*|#]+\s*([^\|:\n]{2,30})", txt, re.M)))[:200]


def build():
    files = [_parse(p) for p in KB.rglob("*.md") if not p.name.startswith("_")]
    topic_files = defaultdict(list)      # topic -> [file names]
    entity_files = defaultdict(list)
    scope_of = {}
    for f in files:
        scope_of[f["name"]] = f["scope"] or f["project"] or "?"
        for t in f["topics"]:
            topic_files[t].append(f["name"])
        for e in f["entities"]:
            entity_files[e].append(f["name"])
    edges = []
    names = {f["name"] for f in files}
    for f in files:
        for l in f["links"]:
            if l in names:
                edges.append({"from": f["name"], "to": l, "type": "link"})
    # 跨 scope 桥接主题:同一 topic 关联到 ≥2 个不同 scope 的文件 = 启发性连接点
    bridges = {}
    for t, fs in topic_files.items():
        scopes = {scope_of.get(n, "?") for n in fs}
        if len(scopes) >= 2 and len(fs) >= 2:
            bridges[t] = {"files": fs, "scopes": sorted(scopes)}
    orphans = [f["name"] for f in files if not f["topics"] and f["tier"] in ("working", "canonical")]

    graph = {
        "n_files": len(files),
        "topics": {t: fs for t, fs in sorted(topic_files.items(), key=lambda x: -len(x[1]))},
        "entities": {e: fs for e, fs in sorted(entity_files.items(), key=lambda x: -len(x[1]))},
        "edges": edges, "bridges": bridges, "orphans_working_canonical": orphans,
        "concept_dict_size": len(_concepts()),
    }
    return files, graph


def render_md(graph):
    L = ["---", "kind: index", "tier: canonical", "scope: core", "---",
         "# 知识库主题图谱(自动生成 by kb_graph.py)", "",
         f"> {graph['n_files']} 个文件。主题/实体来自 frontmatter,随 kb-governance 的 topics 标注逐步变密。", "",
         "## 跨 scope 桥接主题(启发点:连接不同项目/领域的主题)"]
    if graph["bridges"]:
        for t, b in sorted(graph["bridges"].items(), key=lambda x: -len(x[1]["files"])):
            L.append(f"- **{t}** — 横跨 {'/'.join(b['scopes'])};{len(b['files'])} 文件:{', '.join(b['files'][:6])}")
    else:
        L.append("- (暂无:待更多文件带上 topics 后浮现)")
    L += ["", "## 主题覆盖(按文件数)"]
    for t, fs in list(graph["topics"].items())[:30]:
        L.append(f"- {t} ({len(fs)}): {', '.join(fs[:8])}")
    if not graph["topics"]:
        L.append("- (暂无 topics 标注;迁移/新产出补齐后浮现)")
    if graph["orphans_working_canonical"]:
        L += ["", f"## 待标注(working/canonical 但无 topics,共 {len(graph['orphans_working_canonical'])})",
              "  " + ", ".join(graph["orphans_working_canonical"][:40])]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-only", action="store_true")
    a = ap.parse_args()
    files, graph = build()
    (ROOT / "state").mkdir(exist_ok=True)
    (ROOT / "state/kb_graph.json").write_text(json.dumps(graph, ensure_ascii=False, indent=1))
    if not a.json_only:
        (KB / "00-core/topic-graph.md").write_text(render_md(graph))
    print(f"[kb_graph] {graph['n_files']} 文件 | {len(graph['topics'])} 主题 | "
          f"{len(graph['bridges'])} 桥接 | {len(graph['edges'])} 链接边 | "
          f"{len(graph['orphans_working_canonical'])} 待标注")
