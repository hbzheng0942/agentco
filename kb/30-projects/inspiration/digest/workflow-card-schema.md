# Workflow Card Schema v1.2

> D3 产物(2026-07-09)。目标:把视频里的"老师傅 workflow"蒸馏成**可复用/可配置 AI**
> 的结构,而非观后感。标定集 = Ep.1-6;golden card 见 cards/*.golden.md。

## 卡片结构

```yaml
workflow_card:
  meta: {video_id, title, url, duration, 抓取日期, 上游卡片, 下游卡片}  # 系列课=天然DAG
  retrieval:         # v1.2 新增:agent 按需求检索卡片的第一入口(见 decisions/2026-07-09-consumer-is-agent.md)
    intent: 一句话任务意图,用户需求的语言(如"AI参考图 → 游戏可用的绑定角色")
    capability_tags: [能力标签,如 image-to-3d, retopology, rigging, ue5-import]
    preconditions: [工具/版本/账号/预算前提(如 "UE 5.8+", "Meshy付费档")]
    io: {input_artifact: 输入物类型, output_artifact: 输出物类型}
  goal: 一句话(输入工件 → 输出工件)
  tools: [{名称, 版本/模式, 费用}]
  stages:            # 工序节点列表(有序;分支/循环显式标注)
    - id: S1
      name: 工序名
      tool: 所用工具+模式(如 Blender/Sculpt Mode)
      ops: 操作序列(菜单路径/快捷键/参数;参数取自屏幕的标 ⚠︎visual)
      input: 输入工件状态
      output: 输出工件状态
      accept: 验收判据 —— 他凭什么判断这步"成了"(原话依据+时间戳)
      fail_modes: [{症状, 原因, 回退/补救}]
      rationale: 为什么这步在这个位置(工序排序逻辑)
      visual_deps: [需要看屏幕才能确定的点(参数值/UI位置/结果外观)+时间戳]
  cross_cutting: 贯穿性经验(快捷键体系/通用心法/反模式警告)
  economics: {总耗时, 各阶段耗时, 费用}
  provenance: 每条判断标时间戳锚点,可回视频核验
```

## 蒸馏纪律(给 digester 的规约)

1. **判据优先**:accept 和 fail_modes 是卡片价值核心,宁缺毋编;转写里没有就留空标 `∅`
2. **参数存疑标记**:转写常"set it to something like this"——数值没念出来就写 `⚠︎visual@[mm:ss]`,
   留给 L3 视觉层补;**禁止臆造数值**
3. **rationale 抓取**:凡"because/so that/otherwise"句式必抓——工序排序逻辑是抽卡产品最缺的
4. **provenance 强制**:每个 stage 至少一个 [mm:ss] 锚点
5. 营销/求订阅段落直接丢弃

## 消费者(已裁决 2026-07-09:agent)

闭环 = 人提需求 → agent 意图理解 → agent 检索 workflow 库 → 完成人的需求。
- retrieval 块服务检索环节(intent/capability_tags/preconditions/io)
- stages 即编排骨架——tool→MCP/API 绑定,accept→自动验收门,fail_modes→重试策略
- 不建僵硬 DSL:agent 执行时自行解释与适配;人类可读性作为副产品保留
