#!/usr/bin/env bash
# cron入口:生成当日Intel任务并入队(周报制:周一深扫,其余日仅事件扫描)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOW=$(date +%u)
if [ "$DOW" = "1" ]; then MODE="深度周扫:全watchlist逐项检索,产出周报"; else MODE="事件扫描:仅检索watchlist高优先级项,只报影响评分≥4的信号,无则一句话收工"; fi
echo "$MODE。今天是 $(date +%F)。检索后按信号卡格式输出。" | \
  python3 "$ROOT/bin/enqueue.py" owl-intel "intel-$(date +%F)" --ttl 1200
python3 "$ROOT/bin/dispatch.py"
