#!/usr/bin/env python3
"""xhs_search.py — L2 深潜层 小红书分支(社区原声采集)。

产出 `kind: community_raw`(带评论=用户原声),对外契约同 reddit_deep/x_search。
deepdive_preprocess 里被调用(platform=xiaohongshu)。

采集方式:直连本地 xiaohongshu-mcp(HTTP JSON-RPC,默认 :18060,HB 扫码登录后自托管),
**确定性调用,无 LLM**(工具具体:search_feeds → get_feed_detail,零幻觉零成本)。
原声在 get_feed_detail 的 comments.list 里。

⚠️ 依赖:xiaohongshu-mcp 服务需在跑(vendor/xhs/xiaohongshu-mcp,登录态在其 ./data)。
服务没起/未登录 → 抛异常,deepdive_preprocess 转 BLOCKED,绝不凭先验编造。
get_feed_detail 驱动无头浏览器,每条 ~10-30s,故 notes 数克制(缺省 4)。

CLI:  xhs_search.py --project <proj> --topic "<关键词>" [--notes 4]
API:  from xhs_search import run_xhs_search; path = run_xhs_search(topic, project)
"""
import argparse, hashlib, json, os, re, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT, load_env

load_env()
XHS_URL = os.environ.get("XHS_MCP_URL", "http://localhost:18060/mcp")
HTTP_TIMEOUT = 180
_id = [10]


def _post(body, sid=None):
    h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if sid:
        h["Mcp-Session-Id"] = sid
    req = urllib.request.Request(XHS_URL, data=json.dumps(body).encode(), headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
        objs = []
        for line in r.read().decode().splitlines():
            line = line.strip()
            if line.startswith("data:"):
                line = line[5:].strip()
            if line.startswith("{"):
                try:
                    objs.append(json.loads(line))
                except Exception:
                    pass
        return objs, r.headers.get("Mcp-Session-Id")


class _MCP:
    """极简 streamable-HTTP MCP 客户端(握手 + tools/call + SSE 解析)。"""
    def __init__(self):
        try:
            _, self.sid = _post({"jsonrpc": "2.0", "method": "initialize",
                                 "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                                            "clientInfo": {"name": "agentco", "version": "1"}}, "id": 1})
        except Exception as e:
            raise RuntimeError(f"xiaohongshu-mcp 不可达({XHS_URL});服务是否在跑? {str(e)[:120]}")
        _post({"jsonrpc": "2.0", "method": "notifications/initialized"}, self.sid)

    def call(self, name, args):
        _id[0] += 1
        i = _id[0]
        objs, _ = _post({"jsonrpc": "2.0", "method": "tools/call",
                         "params": {"name": name, "arguments": args}, "id": i}, self.sid)
        for o in objs:
            if o.get("id") == i:
                if o.get("error"):
                    raise RuntimeError(f"{name} error: {json.dumps(o['error'], ensure_ascii=False)[:150]}")
                c = o.get("result", {}).get("content", [])
                if c and c[0].get("text"):
                    txt = c[0]["text"]
                    try:
                        return json.loads(txt)
                    except Exception:
                        return txt   # 非 JSON(多为错误串,如 not found in noteDetailMap)
                return o.get("result")
        return None


def _int(v):
    try:
        return int(str(v).replace(",", "") or 0)
    except Exception:
        return 0


def _note_url(note_id, token):
    u = f"https://www.xiaohongshu.com/explore/{note_id}"
    return u + (f"?xsec_token={token}" if token else "")


def _slug(s):
    s = re.sub(r"[^\w一-鿿]+", "-", s.strip().lower()).strip("-")
    return (s[:40] or "topic").rstrip("-")


def run_xhs_search(topic, project="default", notes=4):
    if not topic or not topic.strip():
        raise ValueError("topic 为空")
    fetch_ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    mcp = _MCP()
    login = mcp.call("check_login_status", {})
    if not (isinstance(login, dict) and any("已登录" in str(v) for v in _flat(login))) \
       and "已登录" not in str(login):
        raise RuntimeError(f"xiaohongshu-mcp 未登录(需 HB 扫码);check_login_status={str(login)[:120]}")

    res = mcp.call("search_feeds", {"keyword": topic})
    feeds = (res or {}).get("feeds") if isinstance(res, dict) else None
    if not feeds:
        raise RuntimeError(f"search_feeds 空返:'{topic}'(关键词太窄或被风控);raw={str(res)[:120]}")

    urls, sections = [], []
    for f in feeds[:notes]:
        nid, tok = f.get("id"), f.get("xsecToken")
        nc = f.get("noteCard", {}) or {}
        title = nc.get("displayTitle") or "(无标题)"
        try:
            d = mcp.call("get_feed_detail", {"feed_id": nid, "xsec_token": tok, "load_all_comments": False})
        except Exception as e:
            sections.append(f"> 采集缺口:笔记 {title[:20]} 详情抓取失败({str(e)[:80]})")
            continue
        if not isinstance(d, dict) or "data" not in d:   # not found in noteDetailMap 等
            sections.append(f"> 采集缺口:笔记 {title[:20]} 详情不可解析({str(d)[:80]})")
            continue
        note = d["data"].get("note", {}) or {}
        ii = note.get("interactInfo", {}) or {}
        clist = ((d["data"].get("comments") or {}).get("list")) or []
        clist.sort(key=lambda c: _int(c.get("likeCount")), reverse=True)
        u = _note_url(nid, tok)
        urls.append(u)
        sec = [f"## {note.get('title') or title}",
               f"- url: {u}",
               f"- 作者: {(note.get('user') or {}).get('nickname','?')} · ▲{ii.get('likedCount','?')}赞 · "
               f"{ii.get('commentCount','?')}评论 · {ii.get('collectedCount','?')}收藏 · IP:{note.get('ipLocation','?')}",
               f"- 笔记原声: {(note.get('desc') or '(仅图文无正文)').strip()}",
               "- 高赞评论(原声):"]
        if clist:
            for c in clist[:8]:
                txt = (c.get("content") or "").strip().replace("\n", " ")
                if not txt:
                    continue
                who = (c.get("userInfo") or {}).get("nickname", "?")
                sec.append(f"  - ▲{c.get('likeCount','0')} {who}(IP:{c.get('ipLocation','?')}): \"{txt[:300]}\"")
                sub = c.get("subComments") or []
                if sub and (sub[0].get("content") or "").strip():
                    st = sub[0]["content"].strip().replace("\n", " ")
                    sec.append(f"    ↳ ▲{sub[0].get('likeCount','0')} {(sub[0].get('userInfo') or {}).get('nickname','?')}: \"{st[:200]}\"")
        else:
            sec.append("  - (无评论或未抓到)")
        sections.append("\n".join(sec))

    if not urls:
        raise RuntimeError(f"xhs_search 无可解析笔记:'{topic}'(详情全失败,见 sections)")

    urls = sorted(set(urls))
    body = "\n\n".join(sections)
    h = hashlib.sha256()
    for u in urls:
        h.update(u.encode())
    h.update(body.encode())
    content_hash = h.hexdigest()[:16]

    raw_dir = ROOT / "kb/30-projects" / project / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_path = raw_dir / f"community-xhs-{_slug(topic)}-{datetime.now():%Y%m%d}.md"
    lines = ["---", "kind: community_raw", "platform: xiaohongshu",
             f"topic: {json.dumps(topic, ensure_ascii=False)}",
             f"fetch_ts: {fetch_ts}", f"content_hash: {content_hash}",
             f"project: {project}", "collector: xiaohongshu-mcp(确定性,无LLM)", "source_urls:"]
    lines += [f"  - {u}" for u in urls]
    lines += ["---", "",
              f"# 社区原声:小红书 / {topic}", "",
              "> xiaohongshu-mcp 深潜采集(确定性格式化,无模型加工)。**原声在高赞评论里**(中文本土视角);"
              "digester 蒸馏时逐条痛点回指具体评论(带▲赞/IP属地),勿把评论区综合成一句。"
              "注意小红书含种草/营销号,digester 需甄别真实用户声音。",
              "", body, ""]
    out_path.write_text("\n".join(lines))
    return str(out_path.relative_to(ROOT))


def _flat(o):
    if isinstance(o, dict):
        for v in o.values():
            yield from _flat(v)
    elif isinstance(o, list):
        for v in o:
            yield from _flat(v)
    else:
        yield o


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="default")
    ap.add_argument("--topic", required=True)
    ap.add_argument("--notes", type=int, default=4)
    a = ap.parse_args()
    print(run_xhs_search(a.topic, a.project, a.notes))
