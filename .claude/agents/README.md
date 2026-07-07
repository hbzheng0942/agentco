# .claude/agents — AGENTCO 角色注册表(Wave④)

## 端点规则(先懂这个再用)

一个 Claude Code 进程 = 一个 API 端点,`/model` 只列该端点的模型:

| 会话怎么开 | 端点 | 可用模型 | 可用 agents |
|---|---|---|---|
| `claude`(判断层终端) | Anthropic 订阅 | Fable/Opus/Sonnet/Haiku | strategist / architect / warden |
| `bin/cc-model [别名]`(执行域终端) | litellm(127.0.0.1:4000) | 全部非Claude模型,见下 | retriever / executor / digester / auditor(frontmatter 已绑模型,**同会话多厂商混用已实证**) |

执行域终端内切模型:
- `/model opus|sonnet|haiku` → 槽位已映射:**opus=gpt-5.5 sonnet=gpt-5.4 haiku=ds-chat**(cc-model 注入,CC_OPUS/CC_SONNET/CC_HAIKU 可覆盖)
- `/model <litellm别名>` → ds-chat / ds-reasoner / kimi-long / qwen-max / qwen-plus / gpt-5.4 / gpt-5.5

跨端点调用会报模型不存在(执行域终端切不到真 Claude,订阅终端切不到外部模型)——这是隔离,不是故障。

## 双终端工作流(HB 定式)

终端A(订阅):判断层。strategist battle / architect 拆 spec →
`bin/enqueue.py`(或让 architect 代跑)把 spec 落 handoff/<project>/ 并写 DB 队列 → dispatch cron 接管。
终端B(cc-model):执行域手动调试/对比模型/临时蒸馏。
注意:**只写 handoff/ 文件不入 DB 是不会被调度的**,交接必须经 enqueue(飞书"派"/enqueue.py/architect)。

## 与生产队列的关系

这里的执行域 agents 是**交互镜像**:快速试产出、调 prompt、对比模型用。
生产任务永远走队列(飞书"派"/bin/enqueue.py → dispatch cron),那边有难度路由、
envelope/report 强制、验收闭环、预算记账——镜像 agent 没有这些护栏。

## 判断层档位(roles.md)

Architect 日常 Sonnet、重决策切 Opus;Strategist battle 用 Sonnet 跑量+Opus 裁决;≤5 轮硬上限。
