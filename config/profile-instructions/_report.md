
# 产出契约补充:report 块(envelope 2.0,所有 worker 必守)

最终回复的**结尾**必须依次输出两个块:

1. report 块 —— 给人看的报告,飞书卡片直接渲染它,不写等于产出不可见:

```report
tldr: 一句话结论(≤40字,写"做成了什么/发现了什么",不写过程)
highlights:
  - 要点1(≤60字,结论性陈述)
  - 要点2
  - 要点3(最多3条,少于3条可以)
action_needed: null 或 "需要人裁决的具体事项(一句话)"
confidence: high|medium|low
```

2. envelope 块 —— 溯源(source_urls/content_hash),按原有 AGENT.md 规范。

report 硬规则:
- 系统只落盘你的**最后一条消息**:正文+report块+envelope 必须在同一条消息里一次性输出,
  分多条消息=正文丢失=任务白做。
- tldr 写给手机上扫一眼的人:禁止"我分析了""首先""Good."之类过程独白,直接给结论。
- BLOCKED 时:tldr 写"BLOCKED:缺什么",action_needed 写需要人做什么,confidence 填 low。
- 不写 report 块会被系统打回重写,浪费你自己的 turn 配额。
