#!/usr/bin/env bash
# cron入口:生成当日情报检索任务并入队(retriever 域;周一深扫,其余日事件扫描)。
# dispatch 预处理会先跑 search.py(query 取自 spec frontmatter),retriever 只读 raw 蒸馏,模型不联网。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOW=$(date +%u)
if [ "$DOW" = "1" ]; then
  MODE="深度周扫:全 watchlist 逐项蒸馏,产出周报"
  QUERY="AI 空间智能 3D 建模 行业 最新 融资 发布 latest news"
else
  MODE="事件扫描:仅高优先级项,只报影响评分≥4的信号,无则一句话收工"
  QUERY="AI spatial intelligence 3D generation latest news"
fi
# --query 让 enqueue 写入 spec 的 query 字段;dispatch retriever 预处理据此跑 search.py
python3 "$ROOT/bin/enqueue.py" retriever "intel-$(date +%F)" --ttl 1200 --query "$QUERY" \
  --body "$MODE。今天是 $(date +%F)。只读 dispatch 抓好的 raw,按信号卡格式蒸馏输出,末尾附 envelope。"
python3 "$ROOT/bin/dispatch.py"
