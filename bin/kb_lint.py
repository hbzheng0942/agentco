#!/usr/bin/env python3
"""kb_lint.py — KB 机器体检(weekly 注入 auditor 输入;verify.sh 探针):
1) kb 内 markdown 相对链接死链;2) 索引(concept-index/_index)引用的文件不存在;
3) 概念同时出现在全局与项目索引(违反"全局优先,查到即停"=冗余)。
输出人可读报告;--strict 时发现问题退出码 1。"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT/"kb"
LINK = re.compile(r"\[[^\]]*\]\((?!https?://|#|mailto:)([^)#\s]+)")
CONCEPT = re.compile(r"\[([^\]]+)\]\(|\*\*([^*|]+)\*\*")   # 索引行里的链接文本或加粗词视为概念名

def lint():
    issues = []
    # 1) 死链
    for f in KB.rglob("*.md"):
        for m in LINK.finditer(f.read_text(errors="ignore")):
            rel = m.group(1)
            if not ((f.parent/rel).exists() or (ROOT/rel).exists() or (KB/rel).exists()):
                issues.append(f"死链: {f.relative_to(ROOT)} -> {rel}")
    # 2/3) 索引概念:全局 vs 项目重复
    def names(p):
        if not p.exists():
            return set()
        return {(m.group(1) or m.group(2)).strip().lower() for m in CONCEPT.finditer(p.read_text(errors="ignore"))}
    glob_idx = names(KB/"00-core/concept-index.md")
    for idx in KB.glob("30-projects/*/_index.md"):
        dup = glob_idx & names(idx)
        for d in sorted(dup):
            issues.append(f"概念冗余(全局+项目双收,应删项目侧): '{d}' in {idx.relative_to(ROOT)}")
    return issues

if __name__ == "__main__":
    issues = lint()
    if not issues:
        print("kb_lint: 无死链/无冗余概念")
        sys.exit(0)
    print(f"kb_lint: {len(issues)} 个问题")
    for i in issues[:50]:
        print(" -", i)
    sys.exit(1 if "--strict" in sys.argv else 0)
