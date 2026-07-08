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
from xhs_search import _MCP, _int, _note_url, note_date, restart_mcp

WATCHLIST = ROOT / "config/xhs_watchlist.json"
STATE_DIR = ROOT / "data/xhs_hot_state"
DETAIL_TIMEOUT = 90       # 单笔 detail/search 上限;超时判卡死触发看门狗
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


def _collect(mcp, keywords, drop_ai):
    """基础 search_feeds(能用;filter 版会卡浏览器,弃用)汇总候选去重。
    drop_ai=True 时剔除 AI 类(非 AI 线用)。返回候选卡片列表。"""
    seen, notes = set(), []
    for kw in keywords:
        try:
            res = mcp.call("search_feeds", {"keyword": kw}, timeout=DETAIL_TIMEOUT)
        except Exception:
            continue
        for f in (res or {}).get("feeds", []) if isinstance(res, dict) else []:
            k = f.get("id")
            title = (f.get("noteCard", {}) or {}).get("displayTitle", "")
            if k and k not in seen and not (drop_ai and AI_KW.search(title)):
                seen.add(k); c = _card(f); c["via"] = f"kw:{kw}"; notes.append(c)
    return notes


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
    return fresh, {"stale_dropped": stale, "undated_skipped": undated, "cutoff": cutoff}


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
             f"topic: 小红书每日热点-{zh}线", f"method: 关键词监控+发布日期freshness门(近{window}天)",
             f"window_days: {window}", f"freshness_stats: {json.dumps(stats, ensure_ascii=False)}",
             f"fetch_ts: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
             f"content_hash: {chash}", f"project: {project}", "topics: [小红书热点, AI市场, 用户原声]",
             "collector: xiaohongshu-mcp(确定性,无LLM)", "source_urls:"]
    lines += [f"  - {u}" for u in urls] or ["  []"]
    lines += ["---", "",
              f"# 小红书每日热点 · {zh}线 · {datetime.now():%Y-%m-%d}(近{window}天发布)", "",
              f"> **口径:只收近 {window} 天发布的高互动笔记**(存量老帖已按发布日期过滤,"
              f"本批丢弃 {stats.get('stale_dropped',0)} 篇过期、{stats.get('undated_skipped',0)} 篇无日期)。"
              f"digester 蒸馏:①今日该线新热话题聚类(3-5簇,每簇so-what);②营销号刷量甄别;"
              f"③对我们(具身/仿真/空间智能)值得关注的。原声回指具体评论。",
              "", body]
    out.write_text("\n".join(lines))
    return str(out.relative_to(ROOT))


def run_xhs_hot(project="default", top=10, window=DEFAULT_WINDOW, cap=CANDIDATE_CAP):
    wl = json.loads(WATCHLIST.read_text())
    mcp = _MCP()
    if "已登录" not in str(mcp.call("check_login_status", {})):
        raise RuntimeError("xiaohongshu-mcp 未登录")
    ai_cands = _collect(mcp, wl.get("ai", []), drop_ai=False)
    non_cands = _collect(mcp, wl.get("nonai_seed", []), drop_ai=True)
    sess = _Session(mcp)   # 逐笔 detail 拿发布日期+评论,freshness 门
    ai_fresh, ai_stats = _detail_gate(sess, ai_cands, window, cap)
    non_fresh, non_stats = _detail_gate(sess, non_cands, window, cap)
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
