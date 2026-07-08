#!/usr/bin/env python3
"""xhs_hot.py — 小红书每日热点追踪(关键词监控 + 日间趋势检测,分 AI/非 AI 两线)。

借 RedSkill 的 xiaohongshu-cn 方法(热门笔记发现/关键词监控/趋势分析)。
弃用旧版"首页第一屏"(个性化推荐流样本小且偏,不代表全站热点)。

方法(两线各用对路的信号):
- AI 线:关键词 watchlist(config/xhs_watchlist.json)→ 每词 search_feeds → 汇总去重。精准盯我们的域。
- 非 AI 线:多次拉 list_feeds(explore 流)去重 + 少量种子词补充 → 通用大盘脉搏。
- 趋势检测(核心):存昨日各线 note id(data/xhs_hot_state/),今日标出**新冒头**(🆕)——
  日间新增的高互动笔记才是"趋势",不是高赞存量。按互动降序、新冒头优先。

确定性采集,无 LLM。依赖 xiaohongshu-mcp(:18060,systemd 常驻)。

CLI:  xhs_hot.py [--project default] [--top 10] [--detail 3]
      打印两行:AI 线 raw 路径 / 非 AI 线 raw 路径。
"""
import argparse, hashlib, json, re, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT
from xhs_search import _MCP, _int, _note_url

WATCHLIST = ROOT / "config/xhs_watchlist.json"
STATE_DIR = ROOT / "data/xhs_hot_state"
AI_KW = re.compile(
    r"(AI|AGI|AIGC|LLM|GPT|Sora|agent|智能体|大模型|多模态|具身|机器人|人形|算法|模型|"
    r"神经网络|深度学习|生成式|文生|图生|扩散|自动驾驶|智驾|英伟达|GPU|算力|豆包|文心|"
    r"通义|Kimi|DeepSeek|Claude|OpenAI|Gemini|prompt|RAG|微调|世界模型|空间智能|3D生成)", re.I)


def _note_key(f):
    return f.get("id")


def _card(f):
    nc = f.get("noteCard", {}) or {}
    ii = nc.get("interactInfo", {}) or {}
    return {
        "id": f.get("id"), "token": f.get("xsecToken"),
        "title": nc.get("displayTitle") or "(无标题)",
        "author": (nc.get("user") or {}).get("nickname", "?"),
        "likes": _int(ii.get("likedCount")), "likes_raw": ii.get("likedCount", "?"),
        "comments": ii.get("commentCount", "?"), "collects": ii.get("collectedCount", "?"),
        "type": nc.get("type", "?"),
    }


def _collect_ai(mcp, keywords):
    seen, notes = set(), []
    for kw in keywords:
        try:
            res = mcp.call("search_feeds", {"keyword": kw})
        except Exception:
            continue
        for f in (res or {}).get("feeds", []) if isinstance(res, dict) else []:
            k = _note_key(f)
            if k and k not in seen:
                seen.add(k); c = _card(f); c["via"] = f"kw:{kw}"; notes.append(c)
    return notes


def _collect_nonai(mcp, seed_kw, pulls=3):
    seen, notes = set(), []
    for _ in range(pulls):   # 多次拉 explore 流增加覆盖(每次略不同),去重
        try:
            res = mcp.call("list_feeds", {})
        except Exception:
            continue
        for f in (res or {}).get("feeds", []) if isinstance(res, dict) else []:
            k = _note_key(f)
            if k and k not in seen:
                seen.add(k); c = _card(f)
                if not AI_KW.search(c["title"]):   # 只留非 AI
                    c["via"] = "explore"; notes.append(c)
    for kw in seed_kw:   # 种子词补充
        try:
            res = mcp.call("search_feeds", {"keyword": kw})
        except Exception:
            continue
        for f in (res or {}).get("feeds", []) if isinstance(res, dict) else []:
            k = _note_key(f)
            if k and k not in seen and not AI_KW.search((f.get("noteCard", {}) or {}).get("displayTitle", "")):
                seen.add(k); c = _card(f); c["via"] = f"kw:{kw}"; notes.append(c)
    return notes


def _trend_mark(line, notes):
    """日间趋势:与昨日 note id 集合 diff,标 🆕 新冒头;保存今日集合供明日。"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    yday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    yfile = STATE_DIR / f"{line}-{yday}.json"
    prev = set(json.loads(yfile.read_text())) if yfile.exists() else set()
    for n in notes:
        n["new"] = bool(prev) and n["id"] not in prev   # 首日无基线,不误标全新
    (STATE_DIR / f"{line}-{today}.json").write_text(json.dumps([n["id"] for n in notes]))
    return bool(prev)


def _rank(notes, top):
    # 新冒头优先,其次绝对互动;都为热点候选
    return sorted(notes, key=lambda n: (n.get("new", False), n["likes"]), reverse=True)[:top]


def _fmt(mcp, notes, detail_n):
    urls, secs = [], []
    for i, n in enumerate(notes):
        u = _note_url(n["id"], n["token"])
        urls.append(u)
        flag = "🆕新冒头 " if n.get("new") else ""
        head = (f"## {flag}{n['title']}\n- url: {u}\n"
                f"- 作者: {n['author']} · ▲{n['likes_raw']}赞 · {n['comments']}评论 · "
                f"{n['collects']}收藏 · 类型:{n['type']} · 来源:{n.get('via','?')}")
        if i < detail_n and n["id"] and n["token"]:
            try:
                d = mcp.call("get_feed_detail", {"feed_id": n["id"], "xsec_token": n["token"],
                                                 "load_all_comments": False})
                if isinstance(d, dict) and "data" in d:
                    note = d["data"].get("note", {}) or {}
                    cl = sorted(((d["data"].get("comments") or {}).get("list")) or [],
                                key=lambda c: _int(c.get("likeCount")), reverse=True)
                    if note.get("desc"):
                        head += f"\n- 笔记原声: {note['desc'].strip()[:280]}"
                    if cl:
                        head += "\n- 高赞评论(原声):"
                        for c in cl[:5]:
                            txt = (c.get("content") or "").strip().replace("\n", " ")
                            if txt:
                                head += (f"\n  - ▲{c.get('likeCount','0')} "
                                         f"{(c.get('userInfo') or {}).get('nickname','?')}"
                                         f"(IP:{c.get('ipLocation','?')}): \"{txt[:220]}\"")
            except Exception as e:
                head += f"\n- (评论抓取失败:{str(e)[:50]})"
        secs.append(head)
    return urls, "\n\n".join(secs)


def _write(line, urls, body, project, had_baseline):
    urls = sorted(set(u for u in urls if u))
    h = hashlib.sha256()
    for u in urls:
        h.update(u.encode())
    h.update(body.encode())
    chash = h.hexdigest()[:16]
    zh = "AI" if line == "ai" else "非AI"
    trend_note = ("🆕=今日新冒头(相对昨日)" if had_baseline else "⚠️首日无昨日基线,趋势标记从明日起生效")
    raw_dir = ROOT / "kb/30-projects" / project / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    out = raw_dir / f"community-xhs-hot-{line}-{datetime.now():%Y%m%d}.md"
    lines = ["---", "kind: community_raw", "platform: xiaohongshu", f"line: {line}",
             f"topic: 小红书每日热点-{zh}线", "method: 关键词监控+日间趋势检测",
             f"fetch_ts: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
             f"content_hash: {chash}", f"project: {project}",
             "collector: xiaohongshu-mcp(确定性,无LLM)", "source_urls:"]
    lines += [f"  - {u}" for u in urls] or ["  []"]
    lines += ["---", "",
              f"# 小红书每日热点 · {zh}线 · {datetime.now():%Y-%m-%d}", "",
              f"> {trend_note}。digester 蒸馏:①今日该线热点话题聚类(3-5簇,每簇so-what);"
              f"②**新冒头(🆕)重点看**——这是趋势信号;③营销号刷量甄别;"
              f"④对我们(具身/仿真/空间智能)值得关注的。原声回指具体评论。",
              "", body]
    out.write_text("\n".join(lines))
    return str(out.relative_to(ROOT))


def run_xhs_hot(project="default", top=10, detail_n=3):
    wl = json.loads(WATCHLIST.read_text())
    mcp = _MCP()
    if "已登录" not in str(mcp.call("check_login_status", {})):
        raise RuntimeError("xiaohongshu-mcp 未登录")
    ai = _collect_ai(mcp, wl.get("ai", []))
    non = _collect_nonai(mcp, wl.get("nonai_seed", []))
    base_ai = _trend_mark("ai", ai)
    base_non = _trend_mark("nonai", non)
    ai_urls, ai_body = _fmt(mcp, _rank(ai, top), detail_n)
    non_urls, non_body = _fmt(mcp, _rank(non, top), detail_n)
    ai_path = _write("ai", ai_urls, ai_body or "> 本日 AI 线无命中。", project, base_ai)
    non_path = _write("nonai", non_urls, non_body or "> 本日非 AI 线无命中。", project, base_non)
    return ai_path, non_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="default")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--detail", type=int, default=3)
    a = ap.parse_args()
    ai_path, non_path = run_xhs_hot(a.project, a.top, a.detail)
    print(ai_path)
    print(non_path)
