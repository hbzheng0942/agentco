#!/usr/bin/env python3
"""reddit_deep.py — L2 深潜层 Reddit 分支(社区原声采集)。

产出 `kind: community_raw`(带高赞评论树=用户原声),对外契约同 search.py:
吃 topic 吐 raw 文件,下游(digester)只读离线文件,不碰 MCP。

采集方式(HB 2026-07-08 定:所有子渠道走 ds-chat/litellm):
内部 spawn 一个 `claude -p` worker 经 litellm 驱动 reddit-research-mcp(dialog-mcp),
worker 只做**忠实转录**——discover_subreddits → 定位讨论帖 → fetch_comments 抓评论树,
每条 post/comment 带真实 permalink,不分析(分析是 digester 的活)。
审计收口:worker 的 tool-call trace 落 traces/reddit_deep/;content_hash 与 source_urls
由本脚本从落盘正文**确定性计算**(正则抽 reddit URL),不信模型自报。

⚠️ worker 必须用默认 CLAUDE_CONFIG_DIR(~/.claude,持有 dialog-mcp 的 OAuth token),
不能用 dispatcher 的隔离 .claude-worker——那里没认证。--strict-mcp-config 只加载本项目
config/mcp/dialog-mcp.json,不吃用户会话里的其它 MCP。

CLI:  reddit_deep.py --project <proj> --topic "<具体话题,越具体越好>" [--model ds-chat]
API:  from reddit_deep import run_reddit_deep; path = run_reddit_deep(topic, project)
"""
import argparse, hashlib, json, os, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT, claude_bin, load_env

load_env()
MCP_CONFIG = ROOT / "config/mcp/dialog-mcp.json"
TIMEOUT = 300
MAX_TURNS = 12
DIALOG_TOOLS = ("mcp__dialog-mcp__discover_operations,"
                "mcp__dialog-mcp__get_operation_schema,"
                "mcp__dialog-mcp__execute_operation")

# worker 指令:严格转录,不分析。原声在评论里,楼主标题只是话题。
BRIEF = """\
你是 reddit 社区原声采集器。用 dialog-mcp 的 reddit 研究工具,就下面这个话题抓取真实讨论与评论,
**只忠实转录工具返回的数据,绝不分析、绝不评价、绝不编造**——分析是下游 digester 的活。

话题:{topic}

步骤:
1. discover_operations 看可用操作;get_operation_schema 确认参数。
2. discover_subreddits(话题) → 选置信度最高、最对口的 2-3 个 subreddit(优先 core 层级;
   若全是 peripheral/低置信,说明话题词太泛,用更专业的词重试一次)。
3. 对选中的 subreddit,search_subreddit / fetch_posts 找与话题最相关、讨论最热(评论多)的帖子,
   合计选 4-6 个最有信息量的帖子。
4. 对每个选中的帖子 fetch_comments 抓评论树,取赞数最高的若干条评论。

输出格式(Markdown,严格按此,不加前言不加总结):
对每个帖子输出一节:
## [r/子版] 帖子标题
- url: <帖子真实 permalink>
- score: ▲<赞> · <评论数>评论 · date: <YYYY-MM-DD 或 unknown>
- 楼主原声: <selftext 前 300 字,无正文写 (仅标题)>
- 高赞评论(原声):
  - ▲<赞> "<评论原文,保留用户真实措辞,长则截断到 400 字>"
  - ▲<赞> "<...>"

硬规则:
- 每个 url 必须是工具返回的真实 reddit permalink,一个都不许编。
- 评论要保留用户原话口吻(痛点/吐槽/需求都在措辞里),不要转述成书面语。
- 某步工具失败/空返:如实写 `> 采集缺口:<subreddit/操作> 返回空`,不拿先验补。
- 不写"综上/总结/建议"——你是采集器不是分析师。
"""


def _worker_collect(topic, model, trace_path):
    """spawn ds-chat worker 经 litellm 驱动 dialog-mcp,返回 (body, ok)。"""
    env = os.environ.copy()
    env.update({
        "ANTHROPIC_BASE_URL": "http://127.0.0.1:4000",
        "ANTHROPIC_AUTH_TOKEN": os.environ.get("LITELLM_MASTER_KEY", ""),
        "ANTHROPIC_SMALL_FAST_MODEL": "ds-chat",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    })
    env.pop("CLAUDE_CONFIG_DIR", None)   # 关键:用默认 config(持 dialog-mcp OAuth),非隔离 worker config
    cmd = [claude_bin(), "-p", "--model", model, "--max-turns", str(MAX_TURNS),
           "--output-format", "json", "--strict-mcp-config", "--mcp-config", str(MCP_CONFIG),
           "--allowedTools", DIALOG_TOOLS]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, start_new_session=True, cwd=str(ROOT), env=env)
    try:
        out, err = p.communicate(input=BRIEF.format(topic=topic), timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        import signal
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        p.communicate()
        trace_path.write_text("TIMEOUT")
        return "", False
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    trace_path.write_text(out + (f"\n\n# stderr\n{err}" if err else ""))
    try:
        res = json.loads(out.strip().splitlines()[-1])
        body = res.get("result", "") or ""
        ok = not res.get("is_error") and bool(body.strip())
        return body, ok
    except Exception:
        return "", False


_REDDIT_URL = re.compile(r"https?://(?:www\.)?reddit\.com/[^\s)\]]+")


def _slug(s):
    s = re.sub(r"[^\w一-鿿]+", "-", s.strip().lower()).strip("-")
    return (s[:40] or "topic").rstrip("-")


def run_reddit_deep(topic, project="default", model="ds-chat"):
    if not topic or not topic.strip():
        raise ValueError("topic 为空")
    fetch_ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    trace = ROOT / "traces/reddit_deep" / datetime.now().strftime("%Y%m%d") / f"{_slug(topic)}.json"
    body, ok = _worker_collect(topic, model, trace)
    if not ok:
        raise RuntimeError(f"reddit_deep worker 失败(见 trace {trace.relative_to(ROOT)});"
                           f"常见原因:dialog-mcp 未认证 / litellm 端点不通")
    # 去掉模型偶发的工作独白前言:正文按契约从第一个 '## ' 帖节开始
    m = re.search(r"^##\s", body, re.M)
    if m:
        body = body[m.start():]
    # source_urls / content_hash 确定性计算:抽正文里的真实 reddit permalink,不信模型自报
    urls = sorted(set(_REDDIT_URL.findall(body)))
    h = hashlib.sha256()
    for u in urls:
        h.update(u.encode())
    h.update(body.encode())
    content_hash = h.hexdigest()[:16]

    raw_dir = ROOT / "kb/30-projects" / project / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_path = raw_dir / f"community-reddit-{_slug(topic)}-{datetime.now():%Y%m%d}.md"
    lines = ["---", "kind: community_raw", "platform: reddit",
             f"topic: {json.dumps(topic, ensure_ascii=False)}",
             f"fetch_ts: {fetch_ts}", f"content_hash: {content_hash}",
             f"project: {project}", f"model: {model}",
             f"trace: {trace.relative_to(ROOT)}", "source_urls:"]
    lines += [f"  - {u}" for u in urls] or ["  []"]
    lines += ["---", "",
              f"# 社区原声:reddit / {topic}", "",
              "> reddit-research-mcp 深潜采集(ds-chat 忠实转录,未分析)。**原声在高赞评论里**;"
              "digester 蒸馏时逐条痛点回指具体评论(带▲赞数),交叉验证,勿把评论区综合成一句。",
              "", body.strip(), ""]
    out_path.write_text("\n".join(lines))
    return str(out_path.relative_to(ROOT))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="default")
    ap.add_argument("--topic", required=True, help="越具体越好(泛词命中游戏模拟版块)")
    ap.add_argument("--model", default="ds-chat")
    a = ap.parse_args()
    print(run_reddit_deep(a.topic, a.project, a.model))
