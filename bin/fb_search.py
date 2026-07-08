#!/usr/bin/env python3
"""fb_search.py — L2 深潜层 Facebook 分支(社区原声采集)。

FB 纯 HTTP 抓不到内容(全 JS 懒加载),故用 Playwright headless chromium 注入 cookie
渲染后抓取。cookie 已验证有效(m.facebook.com/me 200)。产 kind:community_raw,
契约同其它采集器。

⚠️ FB 反爬激进:小号 cookie(封号风险)、克制调用、检测到 checkpoint/登录墙即报错不硬抓。
依赖:playwright + chromium(装在 .venv;运行须用 .venv/bin/python)。

CLI:  .venv/bin/python bin/fb_search.py --project research --topic "robot simulation" [--posts 8]
API:  from fb_search import run_fb_search   (须在 .venv 下 import)
"""
import argparse, hashlib, json, os, re, sys, urllib.parse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT, load_env

load_env()
NAV_TIMEOUT = 45000
UA = ("Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0.0.0 Mobile Safari/537.36")


def _cookies_from_env():
    raw = os.environ.get("FB_COOKIE", "")
    if not raw:
        raise RuntimeError("FB_COOKIE 未在 .env 配置")
    out = []
    for part in raw.split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            out.append({"name": k.strip(), "value": v.strip(),
                        "domain": ".facebook.com", "path": "/"})
    return out


def _slug(s):
    s = re.sub(r"[^\w一-鿿]+", "-", s.strip().lower()).strip("-")
    return (s[:40] or "topic").rstrip("-")


def _extract(page):
    """从渲染后的 DOM 抽帖子文本:优先 [role=article],回退长文本 div。返回 [(text, url)]。"""
    js = """
    () => {
      const seen = new Set(); const out = [];
      const arts = document.querySelectorAll('[role=article]');
      for (const a of arts) {
        const t = (a.innerText || '').trim();
        if (t.length < 40) continue;
        // 找帖子链接(story/permalink/posts/groups)
        let url = '';
        const link = a.querySelector('a[href*="/posts/"],a[href*="/permalink/"],a[href*="story_fbid"],a[href*="/groups/"]');
        if (link) url = link.href;
        const key = t.slice(0, 80);
        if (seen.has(key)) continue; seen.add(key);
        out.push({text: t.slice(0, 1200), url});
      }
      return out;
    }
    """
    return page.evaluate(js)


def _blocked(page):
    low = (page.content() or "").lower()
    url = page.url.lower()
    if "checkpoint" in url or "/login" in url and "next" in url:
        return "命中 checkpoint/登录墙(cookie 失效或触发风控)"
    if "you must log in" in low or ("log in" in low and "password" in low and "create new account" in low):
        return "命中登录墙"
    return None


def run_fb_search(topic, project="research", posts=8):
    if not topic or not topic.strip():
        raise ValueError("topic 为空")
    from playwright.sync_api import sync_playwright
    cookies = _cookies_from_env()
    results, note = [], None
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
                                     args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(user_agent=UA, viewport={"width": 412, "height": 900},
                                  locale="en-US")
        ctx.add_cookies(cookies)
        page = ctx.new_page()
        try:
            q = urllib.parse.quote(topic)
            page.goto(f"https://m.facebook.com/search/posts/?q={q}", timeout=NAV_TIMEOUT,
                      wait_until="domcontentloaded")
            page.wait_for_timeout(3500)                 # 等 JS 渲染首屏
            note = _blocked(page)
            if not note:
                for _ in range(4):                       # 滚动加载更多帖子
                    page.mouse.wheel(0, 4000)
                    page.wait_for_timeout(1800)
                results = _extract(page)
        finally:
            ctx.close(); browser.close()

    if note:
        raise RuntimeError(f"fb_search 受阻:{note}")
    if not results:
        raise RuntimeError(f"fb_search 空返:'{topic}'(渲染后无帖子;可能 cookie 失效或该 query 无公开结果)")

    results = results[:posts]
    urls, secs = [], []
    for i, r in enumerate(results, 1):
        u = r.get("url") or ""
        if u:
            urls.append(u)
        txt = re.sub(r"\n{2,}", "\n", r["text"].strip())
        secs.append(f"## 帖子 {i}" + (f"\n- url: {u}" if u else "") + f"\n- 内容:\n{txt}")
    body = "\n\n".join(secs)
    h = hashlib.sha256()
    for u in sorted(set(urls)):
        h.update(u.encode())
    h.update(body.encode())
    chash = h.hexdigest()[:16]
    raw_dir = ROOT / "kb/30-projects" / project / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    out = raw_dir / f"community-fb-{_slug(topic)}-{datetime.now():%Y%m%d}.md"
    lines = ["---", "kind: community_raw", "platform: facebook",
             f"topic: {json.dumps(topic, ensure_ascii=False)}",
             f"fetch_ts: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
             f"content_hash: {chash}", f"project: {project}",
             "collector: playwright-headless(渲染抓取)", "source_urls:"]
    lines += [f"  - {u}" for u in sorted(set(urls))] or ["  []"]
    lines += ["---", "",
              f"# 社区原声:Facebook / {topic}", "",
              "> Playwright headless 渲染 m.facebook.com 搜索抓取。FB 帖子结构混淆,内容为整块文本;"
              "digester 蒸馏时甄别有效讨论 vs 广告/群发,注意 FB 公开搜索结果有限。",
              "", body]
    out.write_text("\n".join(lines))
    return str(out.relative_to(ROOT))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="research")
    ap.add_argument("--topic", required=True)
    ap.add_argument("--posts", type=int, default=8)
    a = ap.parse_args()
    print(run_fb_search(a.topic, a.project, a.posts))
