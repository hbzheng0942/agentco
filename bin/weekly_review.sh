#!/usr/bin/env bash
# weekly_review.sh — 周报 + 治理 + skill_audit 合并单次产出(cron 0 10 * * 5)。
# 取消月度 cron;所有周期性治理合并到此一次 auditor pass。
# 产出单文件候选包 → 90-inbox → 飞书提醒;HB 花 15 分钟裁决,采纳项 git commit 生效。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
WEEK=$(date +%G-W%V)

STATS=$(sqlite3 state.db "SELECT agent||' | '||kind||' | '||COUNT(*) FROM events WHERE ts>datetime('now','-7 day') GROUP BY agent,kind" 2>/dev/null || echo "无")
FB=$(sqlite3 state.db "SELECT agent||' | '||signal||' | '||COALESCE(note,'') FROM feedback WHERE ts>datetime('now','-7 day')" 2>/dev/null || echo "无")
# skill 心跳:命中计数(全期)+ frontmatter created/use_count
SKILL_HITS=$(sqlite3 state.db "SELECT detail||' | hits='||COUNT(*) FROM events WHERE kind='skill_hit' GROUP BY detail" 2>/dev/null || echo "无")
SKILLS=$(for f in $(find agents kb -path '*/skills/*/SKILL.md' 2>/dev/null); do
           echo "$f | $(grep -E '^(created|use_count):' "$f" | tr '\n' ' ')"; done)
[ -z "$SKILLS" ] && SKILLS="(暂无 skill)"

SPEC=$(cat << EOF
# 周治理 + skill_audit 合并 $WEEK

你是 auditor(与被审 agent 异厂商模型,禁止自我表扬;每条建议必须引用 task_id/文件/trace 作证据)。
本次为**合并 pass**:周报 + 治理 + skill_audit 一次产出,禁止拆分。

## 输入(只读)
- 本周事件统计:
$STATS
- 本周人工反馈(feedback,最高权重):
$FB
- skill 命中计数:
$SKILL_HITS
- skill 清单(created/use_count):
$SKILLS
- 资产:agents/*/AGENT.md、kb/00-core/concept-index.md、kb/00-core/shared/、各项目 _index.md、traces/(抽样)

## 必须产出(单文件,五区块,可为空但须写"无")
1.【周报】本周产出/采纳率/遗留一屏概览。
2.【memory/playbook diff】各 AGENT.md 修改建议(引用返工/纠正证据),可直接 apply 的最终文本。
3.【概念索引维护】发现的重复概念/失权威文件 → 合并建议。
4.【共享组件】本周 breaking 传播是否闭环;dependents 是否遗漏。
5.【skill_audit】
   - 90 天零 hit 的 skill → 归档提议;
   - hit 高重合的 skill → 合并提议;
   - 新 skill 准入需:同流程 ≥3 次(event 计数)+ 附 3 个 task_id,否则不得提议。

铁律:只提议不执行;所有 diff 给可直接应用的最终文本;禁止建议放宽沙箱。末尾附 envelope。
EOF
)

echo "$SPEC" | python3 bin/enqueue.py auditor "weekly-review-$WEEK" --ttl 1800
python3 bin/dispatch.py
bash bin/feishu_push.sh "🗂 周治理+skill_audit 已生成(kb/90-inbox/),周五花 15 分钟裁决:采纳的 diff 手动应用后 git commit。"
