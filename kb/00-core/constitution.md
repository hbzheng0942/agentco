# AGENTCO 宪法(Wave③ 追加)

> 单一真相源级约束。修改需 HB 手动 commit。各 AGENT.md / dispatch / 索引均从此文件取权威定义。

## 概念索引查表规则(全局优先)
查表顺序:全局 `kb/00-core/concept-index.md` → 项目 `kb/30-projects/<proj>/_index.md`,
**查到即停,全局优先**。通用概念入全局,项目特有入项目内。产出新概念前必查;
已有→更新其权威文件,**禁止另建重复**;新概念→追加索引一行并声明相邻概念。

## 单一真相源
同一概念**只有一个权威文件**。任何产出引用概念须指向其权威文件,不得就地复制定义。

## 工具域切分
- **域 = 工具边界**。四域:retriever / executor / digester / auditor。
- **worker = profile 变体**(同域内因模型/档位不同派生 executor-code / executor-code-hi 等)。
- **新 profile 准入 = 独立工具或独立模型**;若仅 prompt 差异,应做成 **skill** 而非新 profile。

## 搜索在 dispatcher 层(非模型工具)
时效性由 `bin/search.py` 四路 REST(brave/serper × web/news)在 **dispatcher 预处理**阶段保证,
落 raw;retriever 只读 raw 蒸馏,**模型不联网**。搜索不是模型的一个 tool,是队列前置步骤。

## skill 心跳(use_count)
skill frontmatter 带 `created` / `use_count`。dispatch 命中(spec 引用 skill 路径)时记 `skill_hit`
并 bump `use_count`。weekly_review 审计:90 天零 hit → 归档提议;hit 高重合 → 合并提议。
**准入**:同流程 ≥3 次(event 计数)+ 附 3 个 task_id 才可提议新 skill。

## envelope(产出溯源信封)
所有产出 frontmatter 必附:
```
task_id, agent, model, tier, project, source_urls[], content_hash, depends_on, artifacts[]
```
digester/executor 只读 depends_on 指向的源,**继承 source_urls + 标注所依据的 content_hash**;
worker 间禁对话,仅带 hash 的 artifact 交接。

## events 不可变
`events` 表 append-only:UPDATE/DELETE 由 trigger 拒绝(`events is append-only`)。审计流不可篡改。

## agent 不得自评
产出型 agent 不为自己的质量背书;评价交 auditor(异厂商模型)。auditor 亦不读其他 auditor 产出(防套娃)。

## 三入口按认知模式
判断 → **CC**;执行 → **飞书 或 codex**;探索 → **codex 桌面**。
PRD / 红蓝队 battle 留 CC + KB,仅可执行 spec 入 codex 队列。

## internal 不过 LiteLLM
`sensitivity: internal` 的内容(群核内部约束、资源图等)**禁止进入 LiteLLM 通道**。
