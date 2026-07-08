#!/usr/bin/env python3
"""collectors_mcp.py — 采集器 tool 化:把 agentco 的确定性采集器暴露成 MCP 工具。

用途:深度调研层的 agent worker 经 --mcp-config 挂载本 server,自主编排采集
(边查边决定下一步),而非 dispatcher 固定流水线。stdio 传输(worker 直接 spawn,无需常驻)。

每个工具:调对应 run_* 采集器(仍确定性落 raw 文件,保审计),读回正文返回给 agent。
返回带 raw 路径,agent 引用时可回指。reddit 不在此暴露——它本身就是 dialog-mcp,
深研 worker 直接挂 reddit MCP 用即可。

运行:  .venv/bin/python bin/collectors_mcp.py   (fastmcp 依赖在 .venv)
配置:  config/mcp/collectors.json
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT

from fastmcp import FastMCP

mcp = FastMCP("agentco-collectors")


def _read_body(rel_path, max_chars=16000):
    """读回采集器产出的 raw 正文(去 frontmatter),供 agent 直接推理。"""
    p = ROOT / rel_path
    text = p.read_text()
    if text.startswith("---"):
        parts = text.split("---", 2)
        body = parts[2] if len(parts) >= 3 else text
    else:
        body = text
    body = body.strip()
    if len(body) > max_chars:
        body = body[:max_chars] + f"\n\n…(截断,完整见 {rel_path})"
    return f"[raw: {rel_path}]\n\n{body}"


@mcp.tool
def web_search(query: str, sources: str = "") -> str:
    """SERP+免费垂直广度搜索(brave/serper × web/news + github/reddit/hn)。
    query: 搜索词。sources: 逗号分隔可选垂直/站内路由(github,reddit,hn,x,xiaohongshu,wechat),空=缺省。
    返回加权去重后的 topN 结果(带日期/独立印证标注)。用于广度发现、事实核查、找信源。"""
    from search import run_search
    srcs = [s.strip() for s in sources.split(",") if s.strip()] or None
    path = run_search(query, project="research", sources=srcs)
    return _read_body(path)


@mcp.tool
def x_search(topic: str) -> str:
    """X(Twitter)话题采集:相关性 top 推文 + 回复线程(用户原声)。
    topic: 话题词。返回推文与高赞回复。用于看 X 上的即时讨论/观点/情绪。噪声高需甄别。"""
    from x_search import run_x_search
    path = run_x_search(topic, project="research")
    return _read_body(path)


@mcp.tool
def xhs_search(topic: str, notes: int = 4) -> str:
    """小红书话题采集:相关笔记 + 高赞评论(中文本土用户原声)。
    topic: 话题词。notes: 抓几篇笔记(默认4,越多越慢)。用于中文市场的真实用户声音/痛点/种草。"""
    from xhs_search import run_xhs_search
    path = run_xhs_search(topic, project="research", notes=notes)
    return _read_body(path)


@mcp.tool
def xhs_deep_research(topic: str, angles: str = "", notes: int = 6, deep: int = 3) -> str:
    """小红书话题深度调研:多角度采集 + 高赞笔记全评论树。比 xhs_search 更厚。
    topic: 话题。angles: 逗号分隔的扩展角度(你决定挖哪些子话题)。用于对一个话题做穷尽式原声挖掘。"""
    from xhs_deep_research import run_xhs_deep_research
    ang = [a.strip() for a in angles.split(",") if a.strip()]
    path = run_xhs_deep_research(topic, project="research", angles=ang, notes=notes, deep=deep)
    return _read_body(path)


@mcp.tool
def arxiv_search(keywords: str = "", cats: str = "cs.AI,cs.CL", days: int = 3) -> str:
    """arxiv 论文检索:近 days 天指定分类的最新论文,可选关键词过滤。
    keywords: 逗号分隔主题词(空=全量)。cats: arxiv 分类。用于技术前沿/主题论文监测。"""
    from arxiv_monitor import run_arxiv_monitor
    kw = [k.strip() for k in keywords.split(",") if k.strip()]
    cs = [c.strip() for c in cats.split(",") if c.strip()]
    path = run_arxiv_monitor(project="research", cats=cs, keywords=kw, days=days)
    return _read_body(path)


if __name__ == "__main__":
    mcp.run()
