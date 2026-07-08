#!/usr/bin/env python3
"""arxiv_monitor.py — arxiv 论文监控(cs.AI/cs.CL 等最新论文,可选主题关键词过滤)。

借 RedSkill 的 arxiv-xhs-daily 方法:自包含、无需任何社区登录,仅 arxiv API。
用途:每日/主题论文监测。产 paper_raw → digester 蒸馏成论文日报/主题跟踪。

确定性采集,stdlib only(urllib+re,零第三方依赖)。

CLI:  arxiv_monitor.py [--project default] [--cats cs.AI,cs.CL] [--keywords 空间智能,3D生成]
                        [--days 2] [--max 40]
API:  from arxiv_monitor import run_arxiv_monitor
"""
import argparse, hashlib, re, sys, urllib.parse, urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT

ARXIV_API = "http://export.arxiv.org/api/query"
DEFAULT_CATS = ["cs.AI", "cs.CL"]


def _fetch(cats, max_results):
    cat_q = " OR ".join(f"cat:{c}" for c in cats)
    q = urllib.parse.urlencode({"search_query": cat_q, "sortBy": "submittedDate",
                                "sortOrder": "descending", "max_results": max_results})
    req = urllib.request.Request(ARXIV_API + "?" + q, headers={"User-Agent": "agentco-arxiv/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode()


def _g(pat, s, default=""):
    m = re.search(pat, s, re.S)
    return m.group(1).strip() if m else default


def _parse(xml):
    out = []
    for e in re.findall(r"<entry>(.*?)</entry>", xml, re.S):
        arxiv_id = _g(r"<id>(.*?)</id>", e)
        out.append({
            "title": re.sub(r"\s+", " ", _g(r"<title>(.*?)</title>", e)),
            "published": _g(r"<published>(.*?)</published>", e)[:10],
            "updated": _g(r"<updated>(.*?)</updated>", e)[:10],
            "summary": re.sub(r"\s+", " ", _g(r"<summary>(.*?)</summary>", e)),
            "authors": re.findall(r"<name>(.*?)</name>", e),
            "url": arxiv_id,
            "primary_cat": _g(r'<arxiv:primary_category[^>]*term="([^"]+)"', e)
                           or _g(r'<category[^>]*term="([^"]+)"', e),
        })
    return out


def _slug(s):
    s = re.sub(r"[^\w一-鿿]+", "-", s.strip().lower()).strip("-")
    return (s[:36] or "arxiv").rstrip("-")


def run_arxiv_monitor(project="default", cats=None, keywords=None, days=2, max_results=60):
    cats = cats or DEFAULT_CATS
    papers = _parse(_fetch(cats, max_results))
    # 时窗过滤:只留近 days 天提交的(submittedDate 降序,足够新)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    papers = [p for p in papers if (p["published"] or p["updated"]) >= cutoff]
    # 主题关键词过滤(可选):title/summary 命中任一即留;命中词记入 hit
    kw = [k.strip() for k in (keywords or []) if k.strip()]
    if kw:
        kre = re.compile("|".join(re.escape(k) for k in kw), re.I)
        for p in papers:
            p["hits"] = sorted(set(kre.findall(p["title"] + " " + p["summary"])))
        papers = [p for p in papers if p.get("hits")]

    if not papers:
        scope = f"cats={','.join(cats)} days={days}" + (f" kw={','.join(kw)}" if kw else "")
        raise RuntimeError(f"arxiv 无匹配论文({scope});关键词太窄或时窗内无新论文")

    urls = [p["url"] for p in papers]
    body_lines = []
    for i, p in enumerate(papers, 1):
        au = ", ".join(p["authors"][:4]) + (" 等" if len(p["authors"]) > 4 else "")
        hit = f" · 命中:{'/'.join(p['hits'])}" if p.get("hits") else ""
        body_lines += [
            f"## {i}. {p['title']}",
            f"- url: {p['url']}",
            f"- 日期: {p['published']} · 分类: {p['primary_cat']}{hit}",
            f"- 作者: {au}",
            f"- 摘要: {p['summary'][:600]}",
            "",
        ]
    body = "\n".join(body_lines)

    h = hashlib.sha256()
    for u in urls:
        h.update(u.encode())
    content_hash = h.hexdigest()[:16]
    fetch_ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

    tag = _slug(",".join(kw)) if kw else "daily"
    raw_dir = ROOT / "kb/30-projects" / project / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    out = raw_dir / f"paper-arxiv-{tag}-{datetime.now():%Y%m%d}.md"
    head = ["---", "kind: paper_raw", "source: arxiv", f"cats: {','.join(cats)}",
            f"keywords: {','.join(kw) if kw else '(全量)'}", f"fetch_ts: {fetch_ts}",
            f"content_hash: {content_hash}", f"project: {project}",
            "collector: arxiv-api(确定性,无LLM)", "source_urls:"]
    head += [f"  - {u}" for u in urls]
    head += ["---", "",
             f"# arxiv 论文监控 · {','.join(cats)}{(' · '+'/'.join(kw)) if kw else ''} · {datetime.now():%Y-%m-%d}", "",
             f"> 近 {days} 天 {len(papers)} 篇。digester 蒸馏时:①按主题/技术方向聚类;"
             f"②标出对我们(空间智能/3D/具身/仿真)有直接关系的;③新方法 vs 增量工作;不逐篇复述。",
             "", body]
    out.write_text("\n".join(head))
    return str(out.relative_to(ROOT))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="default")
    ap.add_argument("--cats", default="cs.AI,cs.CL")
    ap.add_argument("--keywords", default="")
    ap.add_argument("--days", type=int, default=2)
    ap.add_argument("--max", type=int, default=60)
    a = ap.parse_args()
    cats = [c.strip() for c in a.cats.split(",") if c.strip()]
    kw = [k.strip() for k in a.keywords.split(",") if k.strip()]
    print(run_arxiv_monitor(a.project, cats, kw, a.days, a.max))
