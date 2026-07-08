# L1 蒸馏任务规约:视频转写 → Workflow Card(v1.1)

> 消费者:digester(ds-reasoner)。本 spec 可复用于全频道;单任务只处理指定视频。
> v1.1(2026-07-09):Ep.1 校准后新增规则 8-11(对照 golden card 发现的系统性漏洞)。

## 输入
1. 转写文本(带 [mm:ss] 时间锚):`data/inspiration/stefan-3d-ai/transcripts/<video_id>.txt`
2. 卡片 schema 与蒸馏纪律(必读,按此执行):`kb/30-projects/inspiration/digest/workflow-card-schema.md`
3. 视频元数据(标题/时长/描述含章节):`data/inspiration/stefan-3d-ai/info/<video_id>.info.json`(如存在)

## 任务
把转写蒸馏成一张 workflow card(markdown,按 schema 的 stages 结构),核心要求:

1. **stages 切分**:按工序切,不按视频章节切;每 stage 必有 [mm:ss] 锚点
2. **accept(验收判据)**:只写他明说的判断依据(原话线索),没有就写 `∅`;
   带条件分支的判断(如"如果卡顿就调低")必须完整保留分支结构
3. **fail_modes**:所有"be careful / don't / otherwise / might result"句式必抓
4. **rationale**:所有"because / so that / why do we need it"句式必抓——工序排序逻辑最值钱
5. **⚠︎visual 标记**:凡参数值/外观标准只在屏幕上、转写含混处("set it to this"),
   写 `⚠︎visual@[mm:ss]`,**禁止臆造数值**
6. 卡尾输出两个汇总:cross_cutting(贯穿性经验/快捷键体系/反模式)、
   L3 视觉层待补清单(全部 ⚠︎visual 条目汇总)
7. 营销求订阅段落丢弃;不确定的内容标 `?` 而不是编
8. **纯判断工序也是 stage**:没有任何软件操作的步骤(缺陷盘点/规划/对照检查/终检)
   必须独立成 stage——"只看不动手"的工序恰恰是老师傅经验密度最高处,禁止合并或丢弃
9. **ASR 数字一律存疑**:自动字幕的数字高频出错("00.2"是 0.02 还是 0.2?)。
   所有从转写提取的数值必须附 `(ASR原文: "...")⚠︎visual@[mm:ss]`,禁止直接断言
10. **推断与转写分离**:fail_modes/rationale 里凡非转写原话支撑、由你推理补全的,
    句尾标 `(推断)`——推断有价值但必须可区分
11. **耗时/费用口播必抓**:任何"took X minutes / $X / X tokens"都进 economics,含所在 stage
12. meta 的 title 以任务书提供的 inventory 标题为准,禁止自拟

## 输出
单个 markdown 文件,标题 `# Workflow Card · <视频标题>`,直接写在任务 result 里。

## 质量对照(仅校准阶段)
Ep.1(ouHL_Rlebss)有人工 golden card:
`kb/30-projects/inspiration/digest/cards/ep1-mesh-sculpting.golden.md`
——蒸馏时**不得阅读**该文件(污染校准);审收人负责对照。
