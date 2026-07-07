# .claude/agents — AGENTCO 角色注册表(Wave④)

## 端点规则(先懂这个再用)

一个 Claude Code 进程 = 一个 API 端点,`/model` 只列该端点的模型:

| 会话怎么开 | 端点 | 可用模型 | 可用 agents |
|---|---|---|---|
| `claude`(平时) | Anthropic 订阅 | Fable/Opus/Sonnet/Haiku | strategist / architect / warden(判断层) |
| `bin/cc-model [别名]` | litellm(127.0.0.1:4000) | ds-chat/ds-reasoner/kimi-long/qwen-max/qwen-plus/gpt-5.4/gpt-5.5 | retriever / executor / digester / auditor(执行域镜像,frontmatter 已绑各自模型,**同一会话内可多厂商混用**) |

跨端点调用会报模型不存在——这是隔离,不是故障。

## 与生产队列的关系

这里的执行域 agents 是**交互镜像**:快速试产出、调 prompt、对比模型用。
生产任务永远走队列(飞书"派"/bin/enqueue.py → dispatch cron),那边有难度路由、
envelope/report 强制、验收闭环、预算记账——镜像 agent 没有这些护栏。

## 判断层档位(roles.md)

Architect 日常 Sonnet、重决策切 Opus;Strategist battle 用 Sonnet 跑量+Opus 裁决;≤5 轮硬上限。
