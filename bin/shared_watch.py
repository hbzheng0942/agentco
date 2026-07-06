#!/usr/bin/env python3
"""shared_watch.py — 共享组件传播。git diff 检测 kb/00-core/shared/*/spec.md 变更并分类。

- `## API契约` 段 hash 变化 = breaking → 每个 dependent 项目实时生成 review 任务(auditor,高优先级)。
- 其他部分变化(API契约段不变) = non-breaking → 仅记 event(shared_change),攒入每日简报。
- 新增 spec(base 中不存在) = shared_new event。

用法:shared_watch.py [--base HEAD]   # 比较工作树 vs <base>(默认 HEAD)
"""
import argparse, hashlib, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT, db, ev, enqueue

API_RE = re.compile(r"^##\s*API契约\s*$.*?(?=^##\s|\Z)", re.M | re.S)


def api_section(text):
    m = API_RE.search(text or "")
    return m.group(0) if m else ""


def h(s):
    return hashlib.sha256((s or "").encode()).hexdigest()[:16]


def git_show(base, relpath):
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{base}:{relpath}"],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def dependents_of(comp_dir):
    f = comp_dir / "dependents.md"
    if not f.exists():
        return []
    projs = []
    for line in f.read_text().splitlines():
        s = line.strip().lstrip("-*").strip()
        if s and not s.startswith("#") and not s.startswith("|"):
            projs.append(s.split()[0])
    return projs


def watch(base="HEAD"):
    c = db()
    results = []
    for spec in ROOT.glob("kb/00-core/shared/*/spec.md"):
        rel = str(spec.relative_to(ROOT))
        comp = spec.parent.name
        cur = spec.read_text()
        old = git_show(base, rel)
        if old is None:
            ev(c, None, "shared", "shared_new", comp)
            results.append((comp, "new", []))
            continue
        if h(api_section(cur)) != h(api_section(old)):
            deps = dependents_of(spec.parent)
            tids = []
            for proj in deps:
                tid = enqueue("auditor", f"[breaking] shared {comp} API契约变更 → review 影响",
                              f"共享组件 {comp} 的 ## API契约 段发生 breaking 变化。"
                              f"审 {proj} 对 {comp} 的依赖点,列出需适配项与风险。spec: {rel}",
                              project=proj, priority=1)
                tids.append(tid)
            ev(c, None, "shared", "shared_breaking", f"{comp} dependents={deps} tasks={tids}")
            results.append((comp, "breaking", tids))
        elif cur != old:
            ev(c, None, "shared", "shared_change", comp)
            results.append((comp, "non-breaking", []))
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="HEAD")
    a = ap.parse_args()
    for comp, kind, tids in watch(a.base):
        print(f"{comp}: {kind}" + (f" → review tasks {tids}" if tids else ""))
