#!/usr/bin/env bash
# cron入口:arxiv 论文监控(T+1)。跑 arxiv_monitor 拉近日 cs.AI/cs.CL/cs.RO 新论文
# (含空间智能/3D/具身主题过滤),派 digester 蒸馏论文日报。自包含,无需社区登录。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATE=$(date +%F)

# 主题过滤:盯我们的域(空间智能/3D/具身/仿真)。全量太杂,过滤后更聚焦。
RAW=$(python3 "$ROOT/bin/arxiv_monitor.py" --project default \
        --cats cs.AI,cs.CV,cs.LG,cs.RO \
        --keywords "spatial,3D,embodied,simulation,world model,robot,scene" \
        --days 2 --max 80) || { "$ROOT/bin/feishu_push.sh" "🛑 arxiv 监控失败" || true; exit 0; }

python3 "$ROOT/bin/enqueue.py" digester "arxiv论文日报-$DATE" --ttl 900 --difficulty medium \
  --body "read_raw: $RAW
蒸馏今日 arxiv 论文($DATE)。按技术方向聚类(3D生成/世界模型/具身/仿真/多模态等),
标出对我们(空间智能/仿真)有直接关系的、新方法 vs 增量,给一句话 so-what。不逐篇复述。"

python3 "$ROOT/bin/dispatch.py"
