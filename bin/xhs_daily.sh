#!/usr/bin/env bash
# cron入口:小红书每日热点追踪(scope=area,近7天发布口径,T+1)。
# 采集(xhs_hot,确定性无LLM)→ 两线 community_raw(落 kb/40-areas/xhs-hot/raw/)→
# 派 digester 蒸馏 → 结果归位 kb/40-areas/xhs-hot/digest/。依赖 xiaohongshu-mcp.service。
set -uo pipefail   # 不用 -e:单步失败要能继续/告警,不静默整体退出
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATE=$(date +%F)
DIGEST_DIR="$ROOT/kb/40-areas/xhs-hot/digest"; mkdir -p "$DIGEST_DIR"

# 看门狗:跑前重启 MCP,保证浏览器新鲜(单浏览器实例慢调用会累积卡死)
sudo systemctl restart xiaohongshu-mcp.service 2>/dev/null; sleep 7

# 健康检查:MCP 不可达则告警退出,不派空任务
if ! curl -s -m 8 -o /dev/null -X POST http://localhost:18060/mcp \
     -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
     -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"cron","version":"1"}},"id":1}'; then
  "$ROOT/bin/feishu_push.sh" "🛑 小红书热点追踪跳过:xiaohongshu-mcp(:18060)不可达" || true
  exit 0
fi

# 采集近7天发布的高互动笔记(freshness 门,老帖按发布日期过滤)
MAP=$(python3 "$ROOT/bin/xhs_hot.py" --top 10 --window 7)
AI_RAW=$(echo "$MAP" | sed -n '1p'); NON_RAW=$(echo "$MAP" | sed -n '2p')
[ -z "$AI_RAW" ] && { "$ROOT/bin/feishu_push.sh" "🛑 小红书热点采集失败(xhs_hot 无输出)" || true; exit 0; }

# 派两线 digester(read_raw 独占行行首→dispatch 注入路径;medium=推理档)
AI_TID=$(python3 "$ROOT/bin/enqueue.py" digester "xhs热点-AI线-$DATE" --ttl 900 --difficulty medium \
  --body "read_raw: $AI_RAW
蒸馏今日小红书 AI 线新热点($DATE,近7天发布)。提炼:①今日新热话题聚类(3-5簇,每簇so-what);②新方法/新产品 vs 炒作;③营销号刷量甄别;④对我们(具身/仿真/空间智能)值得关注的。原声回指具体评论。")
NON_TID=$(python3 "$ROOT/bin/enqueue.py" digester "xhs热点-非AI线-$DATE" --ttl 900 --difficulty medium \
  --body "read_raw: $NON_RAW
蒸馏今日小红书非 AI 线新热点($DATE,近7天发布)。提炼:①今日大众新热话题聚类;②情绪/需求信号;③潜在跨界机会。原声回指具体评论。")

python3 "$ROOT/bin/dispatch.py"

# 蒸馏结果归位 area digest(时间序列);dispatch 落 handoff/,这里镜像到 40-areas
for pair in "ai:$AI_TID" "nonai:$NON_TID"; do
  line="${pair%%:*}"; tid="${pair##*:}"
  src="$ROOT/handoff/default/$tid.result.md"
  [ -f "$src" ] && cp "$src" "$DIGEST_DIR/$DATE-$line.md"
done
echo "xhs_daily done: raw→kb/40-areas/xhs-hot/raw/, digest→kb/40-areas/xhs-hot/digest/$DATE-{ai,nonai}.md"
