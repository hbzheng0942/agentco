# Warden 巡检清单(供 CC 开 Warden 会话喂入)

> Warden = CC 的系统巡检 stance(非 codex worker)。定期开一个 CC 会话,按四维逐项核验,
> 异常项落 inbox 或直接修。只读证据(events/feedback/traces/git log),不自评。

## 1. harness 健康
- [ ] litellm `/health` 通;两厂商真实调用返回(ds-chat / kimi-long)。
- [ ] gateway `/health` 通;systemd `agentco-gateway` active;`/review`、`/enqueue` 鉴权生效。
- [ ] dispatch cron 在跑(logs/cron.log 有近轮记录);无长期 running 僵尸。
- [ ] codex headless auth 存活(`codex exec` 可返回)。

## 2. A2A 协作
- [ ] worker 间无越界对话:产出只经带 hash 的 artifact 交接(抽查 envelope)。
- [ ] 依赖边正确:done→dep_triggered、blocked→dep_failed 有 event,无静默挂起。
- [ ] retriever 预处理:search.py 有 raw 落盘,retriever 未联网(trace 无 web 调用)。
- [ ] 路由正确:retriever/digester/auditor→inbox&done;executor→review。

## 3. 自进化审计
- [ ] weekly_review 按周产出;skill_audit 有跑(90 天零 hit / 高重合有提议)。
- [ ] skill 准入守则被遵守(≥3 次 + 3 task_id 才提议)。
- [ ] 概念索引无重复权威文件;新概念都声明了相邻。
- [ ] feedback 中 rework/reject 模式有被 auditor 追根因。

## 4. 架构漂移
- [ ] 新增 profile 是否符合准入(独立工具或独立模型,仅 prompt 差异应为 skill)。
- [ ] shared 组件 breaking 传播是否闭环(dependents review 任务有生成)。
- [ ] cache_gc 未误删被决策引用的 raw(抽查 decisions 溯源链完整)。
- [ ] events 不可变(UPDATE/DELETE 被拒);internal 内容未进 LiteLLM。
- [ ] 单一真相源:同一概念只有一个权威文件。
