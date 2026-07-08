#!/usr/bin/env python3
"""xhs_hot.py — 小红书每日热点追踪(关键词监控 + 发布日期 freshness gate,分 AI/非 AI 两线)。

借 RedSkill 的 xiaohongshu-cn 方法(热门笔记发现/关键词监控/趋势分析)。
弃用旧版"首页第一屏"(个性化推荐流样本小且偏,不代表全站热点)。

方法(两线各用对路的信号):
- AI 线:关键词 watchlist(config/xhs_watchlist.json)→ 优先 search_feeds filters(近窗+最多点赞)→ 失败回退裸搜。
- 非 AI 线:种子词同样 filter-first,并剔除 AI 类标题。
- freshness 判断(核心):逐笔 get_feed_detail 读取 note.time,只保留近 window 天发布的高互动笔记。
  "今日新出现 id"只能做辅助趋势信号,不能替代发布日期 freshness 判据。

确定性采集,无 LLM。依赖 xiaohongshu-mcp(:18060,systemd 常驻)。

CLI:  xhs_hot.py [--project default] [--top 10] [--detail 3]
      打印两行:AI 线 raw 路径 / 非 AI 线 raw 路径。
"""
import argparse, hashlib, json, re, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT
from xhs_search import _MCP, _int, _note_url, note_date, restart_mcp

WATCHLIST = ROOT / "config/xhs_watchlist.json"
DETAIL_TIMEOUT = 90       # 单笔 detail/search 上限;超时判卡死触发看门狗
FILTER_TIMEOUT = 45       # filter UI 更易卡,短超时后立即回退裸搜+detail gate
DEFAULT_WINDOW = 7        # 默认只看近 7 天发布(daily 热度口径:一周内)
CANDIDATE_CAP = 14        # 每线逐笔 detail 的候选上限(detail 慢,须克制)
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


def _publish_time_for_window(window_days):
    if window_days <= 1:
        return "一天内"
    if window_days <= 7:
        return "一周内"
    return "半年内"


def _feeds_from_raw(res):
    return (res or {}).get("feeds", []) if isinstance(res, dict) else []


def _collect(mcp, keywords, drop_ai, publish_time="一周内", sort_by="最多点赞"):
    """filter-first 搜索候选,失败/空返回退裸 search_feeds。
    publish_time/sort_by 只用于降低候选污染;真实 freshness 仍由 detail note.time 验证。
    返回 (候选卡片列表, 搜索统计, 可能重连后的 mcp)。"""
    seen, notes = set(), []
    stats = {
        "keywords": len(keywords),
        "filter_publish_time": publish_time,
        "filter_sort_by": sort_by,
        "filtered_ok": 0,
        "filter_empty": 0,
        "filter_failed": 0,
        "fallback_ok": 0,
        "fallback_empty": 0,
        "fallback_failed": 0,
        "mcp_restarts": 0,
    }

    def add(feeds, via, freshness_source):
        added = 0
        for f in feeds:
            k = f.get("id")
            title = (f.get("noteCard", {}) or {}).get("displayTitle", "")
            if k and k not in seen and not (drop_ai and AI_KW.search(title)):
                seen.add(k)
                c = _card(f)
                c["via"] = via
                c["freshness_source"] = freshness_source
                notes.append(c)
                added += 1
        return added

    for kw in keywords:
        try:
            feeds = mcp.search(kw, publish_time=publish_time, sort_by=sort_by, timeout=FILTER_TIMEOUT)
            if feeds:
                stats["filtered_ok"] += 1
                add(feeds, f"kw:{kw}|filter:{publish_time}/{sort_by}", "filtered_search")
                continue
            stats["filter_empty"] += 1
        except Exception:
            stats["filter_failed"] += 1
            if restart_mcp():
                stats["mcp_restarts"] += 1
                try:
                    mcp = _MCP()
                except Exception:
                    pass

        try:
            res = mcp.call("search_feeds", {"keyword": kw}, timeout=DETAIL_TIMEOUT)
            feeds = _feeds_from_raw(res)
            if feeds:
                stats["fallback_ok"] += 1
                add(feeds, f"kw:{kw}|fallback:裸搜", "fallback_search")
            else:
                stats["fallback_empty"] += 1
        except Exception:
            stats["fallback_failed"] += 1

    stats["candidates_collected"] = len(notes)
    return notes, stats, mcp


class _Session:
    """持有 mcp 连接 + 连败计数;detail 卡死时看门狗重启服务并重连(登录态持久)。"""
    def __init__(self, mcp):
        self.mcp, self.fails = mcp, 0

    def detail(self, nid, tok):
        try:
            d = self.mcp.call("get_feed_detail",
                              {"feed_id": nid, "xsec_token": tok, "load_all_comments": False},
                              timeout=DETAIL_TIMEOUT)
            self.fails = 0
            return d if isinstance(d, dict) and "data" in d else None
        except Exception:
            self.fails += 1
            if self.fails >= 2:          # 连续卡死 → 看门狗重启+重连
                if restart_mcp():
                    try:
                        self.mcp = _MCP(); self.fails = 0
                    except Exception:
                        pass
            return None


def _detail_gate(sess, cands, window_days, cap):
    """按赞取 top cap 候选逐笔 detail,拿发布日期+评论,只留 window_days 内发布的(freshness 门)。
    这是修时间窗的核心:老帖(如 TapNow Marble 4.28)被日期门挡掉。"""
    cutoff = (datetime.now() - timedelta(days=window_days)).strftime("%Y-%m-%d")
    cands = sorted(cands, key=lambda n: n["likes"], reverse=True)[:cap]
    fresh, stale, undated = [], 0, 0
    for n in cands:
        d = sess.detail(n["id"], n["token"])
        if not d:
            undated += 1
            continue
        note = d["data"].get("note", {}) or {}
        n["date"] = note_date(note)
        n["desc"] = (note.get("desc") or "").strip()
        n["comments_list"] = sorted(((d["data"].get("comments") or {}).get("list")) or [],
                                    key=lambda c: _int(c.get("likeCount")), reverse=True)
        if not n["date"]:
            undated += 1; continue
        if n["date"] >= cutoff:
            fresh.append(n)
        else:
            stale += 1
    fresh.sort(key=lambda n: n["likes"], reverse=True)
    return fresh, {
        "stale_dropped": stale,
        "undated_skipped": undated,
        "cutoff": cutoff,
        "window_days": window_days,
        "candidates_detail_checked": len(cands),
        "fresh_kept": len(fresh),
    }


def _fmt(notes):
    urls, secs = [], []
    for n in notes:
        u = _note_url(n["id"], n["token"])
        urls.append(u)
        head = (f"## {n['title']}\n- url: {u}\n- 发布日期: {n.get('date') or '(未知)'}\n"
                f"- 作者: {n['author']} · ▲{n['likes_raw']}赞 · {n['comments']}评论 · "
                f"{n['collects']}收藏 · 类型:{n['type']} · 来源:{n.get('via','?')}")
        if n.get("desc"):
            head += f"\n- 笔记原声: {n['desc'][:280]}"
        if n.get("comments_list"):
            head += "\n- 高赞评论(原声):"
            for c in n["comments_list"][:5]:
                txt = (c.get("content") or "").strip().replace("\n", " ")
                if txt:
                    head += (f"\n  - ▲{c.get('likeCount','0')} "
                             f"{(c.get('userInfo') or {}).get('nickname','?')}"
                             f"(IP:{c.get('ipLocation','?')}): \"{txt[:220]}\"")
        secs.append(head)
    return urls, "\n\n".join(secs)


def _write(line, urls, body, project, window, stats):
    urls = sorted(set(u for u in urls if u))
    h = hashlib.sha256()
    for u in urls:
        h.update(u.encode())
    h.update(body.encode())
    chash = h.hexdigest()[:16]
    zh = "AI" if line == "ai" else "非AI"
    # scope=area(周期性监测,非项目):落 kb/40-areas/xhs-hot/raw/,时间序列按日期命名
    raw_dir = ROOT / "kb/40-areas/xhs-hot/raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    out = raw_dir / f"{datetime.now():%Y-%m-%d}-{line}.md"
    lines = ["---", "kind: community_raw", "tier: ephemeral", "scope: area", "area: xhs-hot",
             "platform: xiaohongshu", f"line: {line}",
             f"topic: 小红书每日热点-{zh}线",
             f"method: filter-first({stats.get('filter_publish_time','?')}+{stats.get('filter_sort_by','?')})+发布日期freshness门(近{window}天)",
             f"window_days: {window}", f"freshness_stats: {json.dumps(stats, ensure_ascii=False)}",
             f"fetch_ts: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
             f"content_hash: {chash}", f"project: {project}", "topics: [小红书热点, AI市场, 用户原声]",
             "collector: xiaohongshu-mcp(确定性,无LLM)", "source_urls:"]
    lines += [f"  - {u}" for u in urls] or ["  []"]
    lines += ["---", "",
              f"# 小红书每日热点 · {zh}线 · {datetime.now():%Y-%m-%d}(近{window}天发布)", "",
              f"> **口径:每个关键词优先用 publish_time={stats.get('filter_publish_time','?')} + "
              f"sort_by={stats.get('filter_sort_by','?')} 搜索,再用详情页发布日期二次验证**;"
              f"存量老帖已按 note.time 过滤,本批丢弃 {stats.get('stale_dropped',0)} 篇过期、"
              f"{stats.get('undated_skipped',0)} 篇无日期。filter 失败 {stats.get('filter_failed',0)} 次、"
              f"fallback 成功 {stats.get('fallback_ok',0)} 次。digester 蒸馏:①今日该线新热话题聚类(3-5簇,每簇so-what);"
              f"②营销号刷量甄别;③对我们(具身/仿真/空间智能)值得关注的。原声回指具体评论。",
              "", body]
    out.write_text("\n".join(lines))
    return str(out.relative_to(ROOT))


def run_xhs_hot(project="default", top=10, window=DEFAULT_WINDOW, cap=CANDIDATE_CAP):
    wl = json.loads(WATCHLIST.read_text())
    mcp = _MCP()
    if "已登录" not in str(mcp.call("check_login_status", {})):
        raise RuntimeError("xiaohongshu-mcp 未登录")
    publish_time = _publish_time_for_window(window)
    ai_cands, ai_collect_stats, mcp = _collect(mcp, wl.get("ai", []), drop_ai=False,
                                               publish_time=publish_time, sort_by="最多点赞")
    non_cands, non_collect_stats, mcp = _collect(mcp, wl.get("nonai_seed", []), drop_ai=True,
                                                 publish_time=publish_time, sort_by="最多点赞")
    sess = _Session(mcp)   # 逐笔 detail 拿发布日期+评论,freshness 门
    ai_fresh, ai_gate_stats = _detail_gate(sess, ai_cands, window, cap)
    non_fresh, non_gate_stats = _detail_gate(sess, non_cands, window, cap)
    ai_stats = {**ai_collect_stats, **ai_gate_stats}
    non_stats = {**non_collect_stats, **non_gate_stats}
    ai_urls, ai_body = _fmt(ai_fresh[:top])
    non_urls, non_body = _fmt(non_fresh[:top])
    ai_path = _write("ai", ai_urls, ai_body or f"> 近 {window} 天 AI 线无新热笔记。", project, window, ai_stats)
    non_path = _write("nonai", non_urls, non_body or f"> 近 {window} 天非 AI 线无新热笔记。", project, window, non_stats)
    return ai_path, non_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="default")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--window", type=int, default=DEFAULT_WINDOW, help="只看近N天发布(缺省7=一周内)")
    ap.add_argument("--cap", type=int, default=CANDIDATE_CAP, help="每线逐笔detail候选上限")
    a = ap.parse_args()
    ai_path, non_path = run_xhs_hot(a.project, a.top, a.window, a.cap)
    print(ai_path)
    print(non_path)
