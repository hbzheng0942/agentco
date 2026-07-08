#!/usr/bin/env python3
"""deep_research.py — 深度调研层(agent 驱动,采集器 tool 化的落地)。

给一个研究问题,spawn 一个 reasoning agent worker,挂载:
- collectors MCP(web_search/x_search/xhs_search/xhs_deep_research/arxiv_search)
- dialog-mcp(reddit-research-mcp:discover/search/fetch_comments)
agent **自主迭代编排**这些 tool(边查边决定下一步),最后产一份带引用的调研报告。

这是与确定性传感器/单次深潜的分工:深研=开放问题、需要判断和多源交叉的调研。
仍可审计:tool 每次调用都确定性落 raw 文件(kb/.../research/raw/),worker trace 存 traces/。

⚠️ 用默认 CLAUDE_CONFIG_DIR(~/.claude,持 dialog-mcp OAuth);模型走 litellm。
成本高于单次采集(多轮 + reasoning 档),按需触发,非 cron。

CLI:  deep_research.py --question "..." [--project research] [--model ds-reasoner] [--turns 30]
"""
import argparse, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agentlib import ROOT, claude_bin, load_env

load_env()
MCP_CONFIG = ROOT / "config/mcp/research.json"
TIMEOUT = 900
TOOLS = ",".join([
    "mcp__collectors__web_search", "mcp__collectors__x_search",
    "mcp__collectors__xhs_search", "mcp__collectors__xhs_deep_research",
    "mcp__collectors__arxiv_search",
    "mcp__dialog-mcp__discover_operations", "mcp__dialog-mcp__get_operation_schema",
    "mcp__dialog-mcp__execute_operation",
])

BRIEF = """\
你是 AGENTCO 的深度调研员。就下面这个问题做多源交叉调研,产出带引用的结论。

问题:{question}

可用采集工具(自主决定用哪些、查几轮):
- collectors.web_search: SERP 广度发现/事实核查
- collectors.x_search / xhs_search / xhs_deep_research: X / 小红书 社区原声(痛点/需求/观点)
- collectors.arxiv_search: 技术前沿论文
- dialog-mcp(reddit): discover_operations 看操作,再 discover_subreddits→search→fetch_comments 挖英文社区原声

方法:
1. 先拆解问题成 2-4 个子问题/角度。
2. 每个角度选合适的源查(社区问题优先社区工具,技术问题优先 arxiv/web,中文市场优先小红书)。
3. 发现缺口/矛盾就补查(最多约 {turns} 轮工具调用内收敛),交叉验证。
4. 产出结论:每条结论回指来源(工具返回里的真实 URL);事实与推断分离,推断标 [推断];
   矛盾并列呈现;信息不足直说"未获证据",禁止用先验编造。

输出结构:
## 核心结论(3-5 条,每条带来源 URL)
## 分角度发现(每角度:证据 + so-what)
## 矛盾与缺口
## 建议(可选)
"""


def run_deep_research(question, project="research", model="ds-reasoner", turns=30):
    env = os.environ.copy()
    env.update({
        "ANTHROPIC_BASE_URL": "http://127.0.0.1:4000",
        "ANTHROPIC_AUTH_TOKEN": os.environ.get("LITELLM_MASTER_KEY", ""),
        "ANTHROPIC_SMALL_FAST_MODEL": "ds-chat",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    })
    env.pop("CLAUDE_CONFIG_DIR", None)   # 默认 config(持 dialog-mcp OAuth)
    cmd = [claude_bin(), "-p", "--model", model, "--max-turns", str(turns),
           "--output-format", "json", "--strict-mcp-config", "--mcp-config", str(MCP_CONFIG),
           "--allowedTools", TOOLS]
    trace = ROOT / "traces/deep_research" / datetime.now().strftime("%Y%m%d")
    trace.mkdir(parents=True, exist_ok=True)
    tfile = trace / f"{datetime.now():%H%M%S}.json"
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, start_new_session=True, cwd=str(ROOT), env=env)
    try:
        out, err = p.communicate(input=BRIEF.format(question=question, turns=turns), timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        import signal
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        p.communicate()
        raise RuntimeError(f"deep_research 超时({TIMEOUT}s)")
    tfile.write_text(out + (f"\n\n# stderr\n{err}" if err else ""))
    try:
        res = json.loads(out.strip().splitlines()[-1])
        body = res.get("result", "") or ""
        cost = res.get("total_cost_usd") or 0.0
    except Exception:
        raise RuntimeError(f"deep_research 输出不可解析(见 trace {tfile.relative_to(ROOT)})")
    if not body.strip():
        raise RuntimeError(f"deep_research 空产出(见 trace {tfile.relative_to(ROOT)})")

    out_dir = ROOT / "kb/30-projects" / project / "digest"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = __import__("re").sub(r"[^\w一-鿿]+", "-", question.strip().lower())[:40].strip("-")
    out_path = out_dir / f"deepresearch-{slug}-{datetime.now():%Y%m%d}.md"
    out_path.write_text(
        f"---\nkind: research_report\nquestion: {json.dumps(question, ensure_ascii=False)}\n"
        f"fetch_ts: {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n"
        f"project: {project}\nmodel: {model}\ncost_usd: {round(cost,4)}\n"
        f"trace: {tfile.relative_to(ROOT)}\n---\n\n# 深度调研:{question}\n\n{body.strip()}\n")
    return str(out_path.relative_to(ROOT))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--question", required=True)
    ap.add_argument("--project", default="research")
    ap.add_argument("--model", default="ds-reasoner")
    ap.add_argument("--turns", type=int, default=30)
    a = ap.parse_args()
    print(run_deep_research(a.question, a.project, a.model, a.turns))
