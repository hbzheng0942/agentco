# 裁决:workflow 库消费者 = agent(2026-07-09,HB)

**结论**:workflow card 的消费者是 agent,不是人直接读 SOP。
但真实场景是四段闭环:**人提需求 → agent 意图理解 → agent 检索 workflow 库 → 完成人的需求**。

## 对 schema 的含义

1. **不走僵硬 DSL**:agent 有意图理解能力,card 不需要可执行到机器指令级;
   结构化 markdown/yaml(现 schema)即可,由 agent 在执行时解释与适配。
2. **检索面是第一公民**:card 必须让 agent 能"按需求找到对的卡"——
   meta 需补检索字段:任务意图(intent,如"AI图→游戏可用角色")、能力标签(capability tags)、
   工具/版本前提(preconditions)、输入输出物类型。L1 放量时 meta 层按此补充,正文 stages 结构不变。
3. **accept/fail_modes 价值上升**:agent 执行时靠它们自检与规避,比给人读时更关键——
   现有蒸馏纪律(分支保留/原话锚定)方向正确。
4. **cross 视频融合(L4)服务于检索与组合**:同一意图多条路线的卡要能被 agent 对比选择,
   上游/下游卡片链接字段将承担工序组合。

已有卡(压测 10 张)不返工,放量卡先按现 schema 走;meta 检索字段作为 schema v1.2 增量,
在放量第二波前补进 workflow-card-schema.md。
