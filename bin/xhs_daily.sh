#!/usr/bin/env bash
# cron入口:小红书每日热点追踪(T+1)。先跑 xhs_hot.py 拉首页流分 AI/非 AI 两线产 raw,
# 再各派一个 digester 任务蒸馏"今日热点话题"。依赖 xiaohongshu-mcp.service(:18060)常驻。
# xhs_hot 无 LLM(确定性采集);蒸馏交 digester(ds-reasoner 推理档),模型只读 raw 不联网。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATE=$(date +%F)

# 服务健康检查:MCP 没起就直接告警退出,不派空任务
if ! curl -s -m 8 -o /dev/null -X POST http://localhost:18060/mcp \
     -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
     -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"cron","version":"1"}},"id":1}'; then
  "$ROOT/bin/feishu_push.sh" "🛑 小红书热点追踪跳过:xiaohongshu-mcp(:18060)不可达,检查 systemctl status xiaohongshu-mcp" || true
  exit 0
fi

# 采集两线 raw(打印两行:AI 路径 / 非 AI 路径)
MAPFILE=$(python3 "$ROOT/bin/xhs_hot.py" --project default --top 8 --detail 2)
AI_RAW=$(echo "$MAPFILE" | sed -n '1p')
NON_RAW=$(echo "$MAPFILE" | sed -n '2p')

# 各派一个 digester 蒸馏任务(read_raw 让 dispatch 注入路径;difficulty medium=推理档)
# read_raw 必须独占一行行首(dispatch 用 ^read_raw: 匹配注入)
python3 "$ROOT/bin/enqueue.py" digester "xhs热点-AI线-$DATE" --ttl 900 --difficulty medium \
  --body "read_raw: $AI_RAW
蒸馏今日小红书 AI 线热点($DATE,T+1)。提炼:①今日 AI 线热点话题聚类(3-5 簇,每簇 so-what);②新冒头 vs 持续发酵;③营销号刷量甄别;④对我们(具身/仿真方向)值得关注的信号。原声回指具体评论。"

python3 "$ROOT/bin/enqueue.py" digester "xhs热点-非AI线-$DATE" --ttl 900 --difficulty medium \
  --body "read_raw: $NON_RAW
蒸馏今日小红书非 AI 线热点($DATE,T+1)。提炼:①今日大众热点话题聚类;②情绪/需求信号(用户在关心什么、焦虑什么);③潜在的跨界机会。原声回指具体评论。"

python3 "$ROOT/bin/dispatch.py"
