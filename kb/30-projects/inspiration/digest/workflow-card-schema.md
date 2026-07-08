# Workflow Card Schema v0.1

> D3 产物(2026-07-09)。目标:把视频里的"老师傅 workflow"蒸馏成**可复用/可配置 AI**
> 的结构,而非观后感。标定集 = Ep.1-6;golden card 见 cards/*.golden.md。

## 卡片结构

```yaml
workflow_card:
  meta: {video_id, title, url, duration, 抓取日期, 上游卡片, 下游卡片}  # 系列课=天然DAG
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

## 双消费者(待裁决 D:人 vs agent)

- 对人:卡片渲染成 SOP 文档即可用
- 对 agent:stages 即编排骨架——tool→MCP/API 绑定,accept→自动验收门,
  fail_modes→重试策略。schema 字段设计已为此预留,暂不建 DSL
