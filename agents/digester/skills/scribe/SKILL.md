---
name: scribe
description: 纪要/落档:把讨论或原始产出整理成结构化纪要与归档条目(前身 scribe 角色,现为 digester 域的 skill)
created: 2026-07-06
use_count: 15
---
# scribe(纪要/落档 skill)

digester 域的一个 skill——scribe 角色坍缩后并入本域,不再是独立 profile。

## 何时命中
spec 引用本 skill 路径(`agents/digester/skills/scribe/SKILL.md`)时,dispatch 记 `skill_hit` 并
bump 上方 `use_count`(见 bin/dispatch.py record_skill_hits)。

## 方法
1. 输入:depends_on 指向的源(带 content_hash),只读。
2. 产出:结构化纪要 = 主题 → 关键结论(每条附源 hash)→ 决议/待决 → 归档去向建议。
3. 归档提级建议以 `git mv` 明确命令给出,由 HB 裁决。

## 生命周期(见 kb/00-core/constitution.md#skill心跳,weekly_review 审计)
- 90 天零 hit → 归档提议;与其他 skill hit 高重合 → 合并提议。
- 准入:同流程 ≥3 次(event 计数)+ 附 3 个 task_id 才可提议新 skill。
