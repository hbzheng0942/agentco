#!/usr/bin/env python3
"""search.py — dispatcher 层搜索(REST 直调,零 MCP,stdlib only)。

路由分三层(2026-07-08 扩展,Minecraft任务实锤通用SERP覆盖不了垂直社区):
- 核心四路(恒开):Brave web/news + Serper web/news
- 免费垂直(缺省开):github(API,按star)/ reddit(公开JSON,按热度)/ hn(Algolia)
- 定向站内(opt-in,吃 Serper 配额+Google索引):x / xiaohongshu / wechat(site:限定)
加权去重:URL 归一化 → 同 URL 跨路叠加 1/(rank+1) → 按总分降序取 topN。
产物:kb/30-projects/<proj>/raw/search-<slug>-<date>.md,frontmatter 带
content_hash / source_urls / query / fetch_ts / routes 状态(单路失败不阻断,记入产物)。

CLI:  search.py --project <proj> --query "<q>" [--query "<q2>"...] [--sources github,reddit,x] [--topn N]
API:  from search import run_search; path = run_search(queries, project, sources=[...])
"""
import argparse, concurrent.futures as cf, hashlib, json, os, re, sys, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT, load_env

load_env()
TIMEOUT = 15
TOPN_PER_ROUTE = 10
TOPN_FINAL = 12
_TRACKING = re.compile(r"^(utm_|gclid$|fbclid$|mc_|ref$|ref_src$|spm$)", re.I)


def normalize_url(u):
    """归一化:小写 scheme/host,去锚点,滤 utm/追踪参,排序余参,去尾斜杠。"""
    try:
        p = urllib.parse.urlsplit(u.strip())
    except Exception:
        return u.strip()
    if not p.netloc:
        return u.strip()
    scheme = (p.scheme or "https").lower()
    netloc = p.netloc.lower()
    q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query) if not _TRACKING.match(k)]
    q.sort()
    query = urllib.parse.urlencode(q)
    path = p.path.rstrip("/") or "/"
    return urllib.parse.urlunsplit((scheme, netloc, path, query, ""))


def _http(method, url, headers, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode())


_CJK = re.compile(r"[一-鿿]")

def _lang(query):
    return "zh" if _CJK.search(query) else "en"


def brave(kind, query):
    key = os.environ.get("BRAVE_API_KEY", "")
    if not key:
        raise RuntimeError("BRAVE_API_KEY 未配置")
    path = "/res/v1/news/search" if kind == "news" else "/res/v1/web/search"
    params = {"q": query, "count": TOPN_PER_ROUTE}
    if _lang(query) == "en":   # 英文 query 锚定全球英文语料;中文保持缺省(本土源有独有信息)
        params.update({"country": "us", "search_lang": "en"})
    url = "https://api.search.brave.com" + path + "?" + urllib.parse.urlencode(params)
    hdr = {"Accept": "application/json", "X-Subscription-Token": key}
    data = _http("GET", url, hdr)
    # web 结果在 .web.results;news 结果在 .results
    items = (data.get("web", {}).get("results") if kind == "web" else data.get("results")) or []
    out = []
    for it in items[:TOPN_PER_ROUTE]:
        u = it.get("url")
        if u:
            out.append((u, it.get("title", ""), it.get("description", "")))
    return out


def serper(kind, query):
    key = os.environ.get("SERPER_API_KEY", "")
    if not key:
        raise RuntimeError("SERPER_API_KEY 未配置")
    path = "/news" if kind == "news" else "/search"
    hdr = {"X-API-KEY": key, "Content-Type": "application/json"}
    body = {"q": query, "num": TOPN_PER_ROUTE}
    if _lang(query) == "en":
        body.update({"gl": "us", "hl": "en"})
    data = _http("POST", "https://google.serper.dev" + path, hdr, body)
    items = (data.get("news") if kind == "news" else data.get("organic")) or []
    out = []
    for it in items[:TOPN_PER_ROUTE]:
        u = it.get("link")
        if u:
            out.append((u, it.get("title", ""), it.get("snippet", "")))
    return out


def github_repos(query):
    """GitHub 仓库搜索(按 star 降序)。无 key 可用(10req/min);GITHUB_TOKEN 可选提额。
    热度(⭐/语言/最近推送)写进 title,retriever 蒸馏时可直接引用。"""
    hdr = {"Accept": "application/vnd.github+json", "User-Agent": "agentco-search"}
    tok = os.environ.get("GITHUB_TOKEN", "")
    if tok:
        hdr["Authorization"] = f"Bearer {tok}"
    def _q(q):
        url = ("https://api.github.com/search/repositories?"
               + urllib.parse.urlencode({"q": q, "sort": "stars", "order": "desc",
                                         "per_page": TOPN_PER_ROUTE}))
        return _http("GET", url, hdr).get("items") or []
    items = _q(query)
    if not items:   # GitHub 是全词匹配,"trending/popular"类修饰词会清零;缩到前2个实词重试
        words = [w for w in re.split(r"\s+", query)
                 if w.lower() not in ("trending", "popular", "best", "top", "awesome", "latest")]
        if len(words) >= 2:
            items = _q(" ".join(words[:2]))
    return [(it["html_url"],
             f"{it['full_name']} ⭐{it['stargazers_count']}",
             f"{(it.get('description') or '').strip()} | lang:{it.get('language')} "
             f"updated:{(it.get('pushed_at') or '')[:10]}")
            for it in items[:TOPN_PER_ROUTE]]


def reddit(query):
    """Reddit 公开搜索 JSON(免 key,带▲热度);数据中心 IP 常被 403(腾讯云实锤 2026-07-08),
    自动降级 serper site:reddit.com(吃 Google 索引,丢热度但保话题覆盖)。"""
    try:
        url = ("https://www.reddit.com/search.json?"
               + urllib.parse.urlencode({"q": query, "sort": "relevance", "t": "year",
                                         "limit": TOPN_PER_ROUTE}))
        data = _http("GET", url, {"User-Agent": "agentco-search/1.0 (research bot)"})
        posts = [c.get("data", {}) for c in data.get("data", {}).get("children", [])]
        return [("https://www.reddit.com" + p["permalink"],
                 f"[r/{p.get('subreddit')}] {p.get('title')} (▲{p.get('score')} · {p.get('num_comments')}评论)",
                 (p.get("selftext") or "")[:220])
                for p in posts[:TOPN_PER_ROUTE] if p.get("permalink")]
    except Exception:
        return [(u, f"[reddit] {t}", s) for u, t, s in serper("web", f"site:reddit.com {query}")]


def hackernews(query):
    """Hacker News Algolia 搜索(免 key)。"""
    url = ("https://hn.algolia.com/api/v1/search?"
           + urllib.parse.urlencode({"query": query, "tags": "story",
                                     "hitsPerPage": TOPN_PER_ROUTE}))
    hits = _http("GET", url, {"User-Agent": "agentco-search"}).get("hits") or []
    out = []
    for h in hits[:TOPN_PER_ROUTE]:
        u = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}"
        out.append((u, f"[HN] {h.get('title')} (▲{h.get('points')} · {h.get('num_comments')}评论)",
                    (h.get("story_text") or "")[:200]))
    return out


def _serper_site(domain):
    """定向站内搜索(吃 Google 索引,Serper 配额):x/小红书/公众号无官方免费API,索引覆盖有限但零风险。"""
    return lambda q: serper("web", f"site:{domain} {q}")


ROUTES = {  # 核心四路,恒开
    "brave_web":   lambda q: brave("web", q),
    "brave_news":  lambda q: brave("news", q),
    "serper_web":  lambda q: serper("web", q),
    "serper_news": lambda q: serper("news", q),
}
FREE_VERTICAL = {  # 免费垂直,缺省开(sources 显式给出时以 sources 为准)
    "github": github_repos,
    "reddit": reddit,
    "hn":     hackernews,
}
SITE_ROUTES = {  # 定向站内,仅 sources 点名才开
    "x":           _serper_site("x.com"),
    "xiaohongshu": _serper_site("xiaohongshu.com"),
    "wechat":      _serper_site("mp.weixin.qq.com"),
}
VALID_SOURCES = set(FREE_VERTICAL) | set(SITE_ROUTES)


def _slug(s):
    s = re.sub(r"[^\w一-鿿]+", "-", s.strip().lower()).strip("-")
    return (s[:40] or "q").rstrip("-")


def run_search(query, project="default", topn=None, sources=None):
    """query: str 或 [str,...](多聚焦子query:每个各跑活跃路由,跨路跨语加权去重)。
    sources: None=核心四路+免费垂直(github/reddit/hn);
             [str,...]=核心四路+点名的垂直/站内路由(x/xiaohongshu/wechat 只能点名开)。"""
    queries = [query] if isinstance(query, str) else [q for q in query if q and q.strip()]
    if not queries:
        raise ValueError("query 为空")
    if sources is None:
        extra = dict(FREE_VERTICAL)
    else:
        extra = {s: (FREE_VERTICAL.get(s) or SITE_ROUTES.get(s))
                 for s in sources if s in VALID_SOURCES}
    active = {**ROUTES, **{k: v for k, v in extra.items() if v}}
    if topn is None:   # 多 query/多路由适度放宽名额
        topn = min(30, TOPN_FINAL + 4*(len(queries)-1) + 2*len(extra))
    fetch_ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    route_status, agg = {}, {}  # norm_url -> {url,title,snippet,sources:set,score}
    # label 记账带语言标签(多query时);sources 恒用纯路由名,保证跨语去重聚合
    jobs = {}
    for i, q in enumerate(queries):
        for name, fn in active.items():
            label = name if len(queries) == 1 else f"{name}[{_lang(q)}{i}]"
            jobs[label] = (name, fn, q)
    with cf.ThreadPoolExecutor(max_workers=min(8, len(jobs))) as ex:
        futs = {ex.submit(fn, q): (label, name) for label, (name, fn, q) in jobs.items()}
        for fut, (label, name) in ((f, futs[f]) for f in cf.as_completed(futs)):
            try:
                results = fut.result()
                route_status[label] = f"ok({len(results)})"
                for rank, (u, title, snippet) in enumerate(results):
                    key = normalize_url(u)
                    e = agg.setdefault(key, {"url": u, "title": title, "snippet": snippet,
                                             "sources": set(), "score": 0.0})
                    e["sources"].add(name)
                    e["score"] += 1.0 / (rank + 1)
                    if not e["title"] and title:
                        e["title"] = title
                    if not e["snippet"] and snippet:
                        e["snippet"] = snippet
            except Exception as e:
                route_status[label] = f"failed: {type(e).__name__}: {str(e)[:120]}"

    ranked = sorted(agg.values(), key=lambda e: (-e["score"], e["url"]))[:topn]
    for e in ranked:
        e["sources"] = sorted(e["sources"])
        e["score"] = round(e["score"], 4)

    # content_hash:对结果集(归一化url|title)稳定哈希
    h = hashlib.sha256()
    for e in ranked:
        h.update((normalize_url(e["url"]) + "|" + e["title"]).encode())
    content_hash = h.hexdigest()[:16]

    raw_dir = ROOT / "kb/30-projects" / project / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_path = raw_dir / f"search-{_slug(queries[0])}-{datetime.now():%Y%m%d}.md"

    lines = ["---", "queries:"]
    lines += [f"  - {json.dumps(q, ensure_ascii=False)}" for q in queries]
    lines += [f"fetch_ts: {fetch_ts}",
              f"content_hash: {content_hash}", "kind: search_raw", f"project: {project}", "routes:"]
    for name in sorted(route_status):
        lines.append(f"  {name}: {route_status[name]}")
    lines.append("source_urls:")
    for e in ranked:
        lines.append(f"  - {e['url']}")
    lines += ["---", "", f"# 搜索原料:{' / '.join(queries)}", "",
              f"> {len(active)}路并行({'+'.join(sorted(active))})×{len(queries)} query,加权去重后 top{len(ranked)}。"
              f"单路失败见 frontmatter.routes。模型只读本文件,不得联网;"
              f"蒸馏时必须评估语言/地域/平台覆盖面(frontmatter 的 queries 与 routes);"
              f"github/reddit/hn 条目 title 内嵌热度(⭐/▲/评论数),蒸馏时引用。", ""]
    for i, e in enumerate(ranked, 1):
        lines.append(f"## {i}. {e['title'] or '(无标题)'}")
        lines.append(f"- url: {e['url']}")
        lines.append(f"- score: {e['score']}  sources: {', '.join(e['sources'])}")
        if e["snippet"]:
            lines.append(f"- 摘要: {e['snippet']}")
        lines.append("")
    out_path.write_text("\n".join(lines))
    return str(out_path.relative_to(ROOT))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="default")
    ap.add_argument("--query", required=True, action="append", help="可重复传入(多聚焦子query)")
    ap.add_argument("--topn", type=int, default=None)
    ap.add_argument("--sources", default=None,
                    help=f"逗号分隔:{','.join(sorted(VALID_SOURCES))}(缺省=github,reddit,hn)")
    a = ap.parse_args()
    srcs = [s.strip() for s in a.sources.split(",") if s.strip()] if a.sources else None
    print(run_search(a.query, a.project, a.topn, sources=srcs))
