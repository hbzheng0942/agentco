# 命题:Workflow Harness —— 3D 生产的下一个抓手

> 状态: brainstorm(2026-07-08 起)· 本项目 = 灵感/产品启发存放地
> 相邻: kb/30-projects/assembly/PRD.md(阶段推演画布——同一哲学在装配域的实例)

## 核心命题

当前 3D AI 生成(Meshy/Tripo 一类)的体验本质是**抽卡**:结果随机、不可微调、
不能逐步迭代。真实生产要的不是更好的卡池,而是**稳定可复用的 workflow**。

产品假设:
1. 把优秀 3D 生产者的复杂 workflow/pipeline **harness 出来**,变成结构化知识库;
2. 在真实可用的 workflow 骨架上再做 AI 能力配置(哪一步用哪个模型、参数、验收标准);
3. "老师傅经验"(工序顺序、每步的判断标准、失败时的回退)是核心壁垒,
   而不是任何单点生成模型。

类比:抽卡 → 流水线;prompt → SOP;单模型 → 编排 + 验收门。

## 第一个资产:Stefan 3D AI(Stefan Vaskevich)

- 频道: https://www.youtube.com/@stefan_3d_ai · 131 视频 / 36.2h(2026-07-08 盘点)
- 10+ 年商业 3D 经验;办 learn3d.ai 教学(=其 workflow 被市场验证为可教学资产)
- 清单: raw/stefan-3d-ai-channel-inventory.md(按七类分组)
- 为什么是他:
  - **34 个 workflow 全流程视频(11.7h)**——工序级"老师傅经验"密度极高
  - **14 个 AI-harness 视频(Claude Code 接管 Blender/UE5、MCP、ComfyUI)**——
    他自己就在做"把 AI 配置进 workflow"这件事,是本命题的活样本
  - **Ep.1-6 系列课(From AI to Game-ready)**——sculpt→retopo→UV/烘焙→贴图→
    绑定/动画→上架,教科书级工序分解,天然是 harness schema 的标定集
  - 高播放 = 需求验证:Claude Code × Blender/UE5 三条视频 224K/250K/199K views

## 待解问题(deep talk 进行中)

- D1 采集通道:云 IP 被 YouTube 封锁,字幕/视频帧取数路线待裁决(见对话)
- D2 理解架构:长视频 + 建模软件界面的多模态理解——转写层 vs 视觉层怎么分工
- D3 Workflow schema:把视频蒸馏成什么结构才"可复用/可配置 AI"?
  (候选:工序节点 = 工具+操作+输入/输出+验收判据+失败回退;与 assembly 的
  ASG/阶段推演画布对齐)

## 竞品/生态观察(随手记)

- Stefan 本人 + learn3d.ai:把 workflow 变成课程卖——知识被 harness 进人脑,不是系统
- MiniMax Hub("Real AI Agent for Creatives",102K views):agent 化方向的对手信号,待深挖
- **Top 3D AI Arena**(Stefan 自建,压测卡 T-014 发现):3D AI 工具 Elo 盲投排行榜,
  反操纵设计,分维度排名(general/geometry/low-poly/segmentation)——
  他已经在做"社区化验收基础设施",这是 workflow harness 里"验收门"的市场雏形
- **Asset Hub**(T-012 发现):聚合平台(参考图→部件提取→3D生成→retopo→UV→纹理,
  内嵌 Tripo P1/Hunyuan 可混搭)——"工具编排"的商业化已开始,但编排的是工具调用,
  不是工序知识(验收判据/回退逻辑仍在 Stefan 脑子里)——这正是我们的差异位

## L1 蒸馏校准结论(2026-07-09)

- workflow/教程类:schema v1.1 直接适配,卡片质量≈golden card 的 85%+
- 横评类:digester 自主提出 **Tool Evaluation Card** 变体(评分矩阵/社区信号/定价模型/
  购买决策树)——待第二品类样本确认后定稿变体 schema
- ASR 系统性失真确认:Claude→"Cloth/CloD",数字含混——L3 视觉层的必要性再添一证
