#!/usr/bin/env python3
"""xhs_deep_research.py — 小红书特定话题深度调研。

借 RedSkill 的 xiaohongshu-deep-research 方法(话题深度调研:输入话题→自动采集+分析)。
与 xhs_search(单话题浅采)的区别:多角度扩展 + 更多笔记 + 高赞笔记全评论树深抓,
产出更厚的单一 community_raw(话题深研料),供 digester 或深研 agent 做痛点/机会分析。

采集确定性无 LLM;角度(angles)由调用方给(深研 agent 编排时它决定挖哪些角度,
这就是"agent 驱动"的体现);standalone 不给 angles 时只用 topic。

CLI:  xhs_deep_research.py --topic "具身智能 数据采集" [--angles "仿真数据,真机采集,遥操作"]
                          [--project research] [--notes 8] [--deep 4]
API:  from xhs_deep_research import run_xhs_deep_research
"""
import argparse, hashlib, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT
from xhs_search import _MCP, _int, _note_url, _slug, note_date


def _collect(mcp, queries):
    """多角度 search_feeds 汇总去重,记每条来自哪个角度。"""
    seen, notes = set(), []
    for q in queries:
        try:
            res = mcp.call("search_feeds", {"keyword": q})
        except Exception:
            continue
        for f in (res or {}).get("feeds", []) if isinstance(res, dict) else []:
            k = f.get("id")
            if k and k not in seen:
                seen.add(k)
                nc = f.get("noteCard", {}) or {}
                ii = nc.get("interactInfo", {}) or {}
                notes.append({"id": k, "token": f.get("xsecToken"),
                              "title": nc.get("displayTitle") or "(无标题)",
                              "author": (nc.get("user") or {}).get("nickname", "?"),
                              "likes": _int(ii.get("likedCount")), "likes_raw": ii.get("likedCount", "?"),
                              "comments": ii.get("commentCount", "?"), "collects": ii.get("collectedCount", "?"),
                              "via": q})
    notes.sort(key=lambda n: n["likes"], reverse=True)
    return notes


def _deep_note(mcp, n, cmt_limit):
    """抓单篇笔记详情 + 顶层高赞评论(cmt_limit 条)。返回格式化 section 与 url。
    刻意不用 load_all_comments(它驱动浏览器滚动加载全部,热门笔记要数分钟,生产会超时);
    顶层高赞评论已是原声主体,cmt_limit 控制深浅。"""
    u = _note_url(n["id"], n["token"])
    head = [f"## {n['title']}", f"- url: {u}",
            f"- 作者: {n['author']} · ▲{n['likes_raw']}赞 · {n['comments']}评论 · "
            f"{n['collects']}收藏 · 命中角度:{n['via']}"]
    try:
        d = mcp.call("get_feed_detail", {"feed_id": n["id"], "xsec_token": n["token"],
                                         "load_all_comments": False})
        if isinstance(d, dict) and "data" in d:
            note = d["data"].get("note", {}) or {}
            cl = sorted(((d["data"].get("comments") or {}).get("list")) or [],
                        key=lambda c: _int(c.get("likeCount")), reverse=True)
            head.insert(3, f"- 发布日期: {note_date(note) or '(未知)'}")
            if note.get("desc"):
                head.append(f"- 笔记原声: {note['desc'].strip()[:400]}")
            if cl:
                head.append("- 评论树(原声):")
                for c in cl[:cmt_limit]:   # 深研:多留评论
                    txt = (c.get("content") or "").strip().replace("\n", " ")
                    if not txt:
                        continue
                    head.append(f"  - ▲{c.get('likeCount','0')} "
                                f"{(c.get('userInfo') or {}).get('nickname','?')}"
                                f"(IP:{c.get('ipLocation','?')}): \"{txt[:280]}\"")
                    sub = c.get("subComments") or []
                    if sub and (sub[0].get('content') or '').strip():
                        head.append(f"    ↳ ▲{sub[0].get('likeCount','0')} "
                                    f"{(sub[0].get('userInfo') or {}).get('nickname','?')}: "
                                    f"\"{sub[0]['content'].strip()[:200]}\"")
        else:
            head.append(f"- (详情不可解析:{str(d)[:60]})")
    except Exception as e:
        head.append(f"- (评论抓取失败:{str(e)[:60]})")
    return u, "\n".join(head)


def run_xhs_deep_research(topic, project="research", angles=None, notes=8, deep=4):
    if not topic or not topic.strip():
        raise ValueError("topic 为空")
    queries = [topic] + [a.strip() for a in (angles or []) if a.strip()]
    mcp = _MCP()
    if "已登录" not in str(mcp.call("check_login_status", {})):
        raise RuntimeError("xiaohongshu-mcp 未登录")
    found = _collect(mcp, queries)
    if not found:
        raise RuntimeError(f"xhs 深研无结果:'{topic}'(角度:{queries})")
    picks = found[:notes]
    urls, secs = [], []
    for i, n in enumerate(picks):
        u, sec = _deep_note(mcp, n, cmt_limit=(12 if i < deep else 5))   # 前 deep 篇多留评论
        urls.append(u); secs.append(sec)
    urls = sorted(set(u for u in urls if u))
    body = "\n\n".join(secs)
    h = hashlib.sha256()
    for u in urls:
        h.update(u.encode())
    h.update(body.encode())
    chash = h.hexdigest()[:16]
    raw_dir = ROOT / "kb/30-projects" / project / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    out = raw_dir / f"community-xhs-deepresearch-{_slug(topic)}-{datetime.now():%Y%m%d}.md"
    lines = ["---", "kind: community_raw", "platform: xiaohongshu", "mode: deep_research",
             f"topic: {json.dumps(topic, ensure_ascii=False)}",
             f"angles: {json.dumps(queries, ensure_ascii=False)}",
             f"fetch_ts: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
             f"content_hash: {chash}", f"project: {project}",
             "collector: xiaohongshu-mcp(确定性,无LLM)", "source_urls:"]
    lines += [f"  - {u}" for u in urls]
    lines += ["---", "",
              f"# 小红书深度调研:{topic}", "",
              f"> 多角度({' / '.join(queries)})采集,共 {len(picks)} 篇,前 {deep} 篇全评论树。"
              f"digester/深研 agent 蒸馏:①话题下的核心痛点/需求聚类(回指评论);"
              f"②不同人群/立场分歧;③潜在机会与空白;④营销号 vs 真实用户甄别。",
              "", body]
    out.write_text("\n".join(lines))
    return str(out.relative_to(ROOT))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True)
    ap.add_argument("--angles", default="")
    ap.add_argument("--project", default="research")
    ap.add_argument("--notes", type=int, default=8)
    ap.add_argument("--deep", type=int, default=4)
    a = ap.parse_args()
    angles = [x.strip() for x in a.angles.split(",") if x.strip()]
    print(run_xhs_deep_research(a.topic, a.project, angles, a.notes, a.deep))
