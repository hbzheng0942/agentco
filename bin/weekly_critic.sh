#!/usr/bin/env bash
# weekly_critic.sh — 周日晚治理pass:异模型审计 + inbox策展 + watchlist进化
# 产出单文件候选包 → 90-inbox → 飞书提醒;周一早你花15分钟裁决,采纳项 git commit 生效。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
WEEK=$(date +%G-W%V)

STATS=$(sqlite3 state.db "SELECT agent||' | '||kind||' | '||COUNT(*) FROM events WHERE ts>datetime('now','-7 day') GROUP BY agent,kind" 2>/dev/null || echo "无")
FB=$(sqlite3 state.db "SELECT agent||' | '||signal||' | '||COALESCE(note,'') FROM feedback WHERE ts>datetime('now','-7 day')" 2>/dev/null || echo "无")
INBOX=$(ls -1 kb/90-inbox/*.md 2>/dev/null | head -60 || echo "空")

SPEC=$(cat << EOF
# 周治理审计 $WEEK

你是治理审计agent(与被审计agent不同厂商模型,禁止自我表扬,每条建议必须引用具体task_id或文件作为证据)。

## 输入
- 本周事件统计:
$STATS
- 本周人工反馈(feedback表,最高权重证据):
$FB
- inbox现存文件(自行读取内容):
$INBOX
- 各agent资产:agents/*/AGENT.md、agents/*/memory.md、kb/20-intel/watchlist.md、traces/(可抽样读取本周JSONL)

## 必须产出(单文件,四区块,每区块可为空但须写"无")
1.【memory候选】各agent memory.md 追加条目(格式:日期|经验|来源task_id)
2.【playbook diff】AGENT.md 修改建议(引用返工/纠正证据)
3.【watchlist进化】本周≥4分信号中来自watchlist之外的方向→建议新增;连续两周零产出的条目→建议降级或删除
4.【inbox策展】去重合并清单 + 提级方案(逐条给出:git mv kb/90-inbox/x.md kb/10-domain/或20-intel/的确切命令)+ 可归档清单

铁律:只提议不执行;所有diff用代码块给出可直接应用的最终文本。
EOF
)

echo "$SPEC" | python3 bin/enqueue.py critic "weekly-governance-$WEEK" --ttl 1800
python3 bin/dispatch.py
bash bin/feishu_push.sh "🗂 周治理报告已生成(kb/90-inbox/),周一早花15分钟裁决:采纳的diff手动应用后 git commit。"
