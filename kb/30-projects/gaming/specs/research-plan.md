# gaming · AI×游戏 深度技术&商业研究计划 v0.1

> 目的:全面看清游戏×AI 各环节的可能性与发展进度,判断未来游戏的发展趋势与我们(3D 技术背景)的可投入机会。
> 创建:2026-07-14。执行方式:信息搜集/蒸馏 handoff 给队列 worker(retriever/digester,light/medium 档),判断层(strategist/architect/人工)只做收敛。

## 0. 核心问题(北极星)

1. AI 重塑游戏的哪个环节会**最先商业化收敛**:引擎层重构 / 制作管道提效 / 运行时体验(NPC·剧情·关卡) / AI-native 玩法?
2. 世界模型入局游戏,**3D 路线 vs 视频路线**谁更接近可玩产品?收敛点在哪(可控性/一致性/成本/时延)?
3. 以我们的 3D 技术积累(空间智能/仿真背景),**切入点在哪一层**:给别人做管道工具、做引擎组件、还是做 AI-native 内容?

## 1. 领域拆解(7 条工作流)

| # | 工作流 | 范围 | 关键玩家(起点,待补全) |
|---|--------|------|------------------------|
| A | AI-native 引擎层 | 跳出 Unity/UE 制作逻辑的全新引擎:生成式引擎、神经渲染引擎、"模型即引擎" | DeepMind Genie 3、Decart(Oasis)、Dynamics Lab(Mirage)、Roblox Cube;对照组:Unity Muse/Sentis、UE PCG/ML Deformer |
| B | 制作管道 AI 化 | 现有管线内提效:3D 资产生成、贴图、动画/动捕、代码副驾、QA/playtest agent、音频 | Meshy、Tripo、Rodin/Hyper3D、CSM、Scenario、Layer AI、Move AI、Cascadeur、modl.ai、Regression Games |
| C | 运行时 AI(剧情/关卡/NPC) | NPC 对话与行为 agent、叙事引擎、关卡/内容动态生成、director AI | Inworld、Convai、Hidden Door、Latitude、Anuttacon(蔡浩宇 Whispers from the Star) |
| D | AI-native 玩法/游戏 | AI 是核心机制而非工具的游戏形态 | Suck Up!、1001 Nights、Infinite Craft、Death by AI、websim 类 |
| E1 | 世界模型→游戏(3D 路线) | 显式 3D 表征的可交互世界生成 | World Labs(Marble)、腾讯混元 Hunyuan3D/HunyuanWorld、Autodesk×World Labs 合作 |
| E2 | 世界模型→游戏(视频路线) | 视频生成/帧预测的可交互世界 | Genie 3、Odyssey、Decart、Pixverse(爱诗)、Lingbot、Happy Oyster、Matrix-Game 等 |
| F | 多智能体共生世界 | 多 agent 共同空间共生实验、多玩家世界一致性、持久世界 | Altera(Project Sid)、Stanford generative agents、AI Town;技术题:multi-player consistency |
| G | 商业层横切 | 融资/并购/大厂布局(腾讯/网易/米哈游/Roblox/Epic)、商业模式、开发者采纳度与情绪 | — |

每条工作流固定四问:**谁在做→做到什么程度(demo/测试/上线/收入)→技术瓶颈是什么→距离商业收敛还差什么**。

## 2. 执行方案(三波)

### Wave 1 · 广度扫描(retriever,light 档,已入队)
7 条工作流各 1 个 landscape 扫描任务 + 1 个 reddit 开发者情绪深潜(digester)。产出:信号卡落 `kb/30-projects/gaming/raw/` 与 inbox。验收:玩家清单+进度分档+来源回指。

### Wave 2 · 深潜蒸馏(digester + retriever 补抓,Wave 1 结果出来后入队)
- 按 Wave 1 的 gaps 定向补抓(沿用搜索流水线 v2 的 gaps 闭环,≤2 轮)。
- 关键玩家深读:World Labs Marble、Genie 3、Decart、Hunyuan、Pixverse/Lingbot/Happy Oyster、Inworld、Anuttacon 等,每家一张能力/成熟度卡。
- 社区深潜:r/gamedev、r/aigamedev、HN 对 AI 工具链的真实采纳与抵触;X 上世界模型 demo 的从业者评价。
- 产出:`digest/` 下按工作流的成熟度地图(每环节:能力边界/瓶颈/时间表证据)。

### Wave 3 · 收敛判断(判断层,不 handoff)
- strategist 红蓝 battle:①3D vs 视频世界模型路线之争;②我们切入层(管道工具 vs 引擎组件 vs AI-native 内容)。产物落 `decisions/`。
- 综合成趋势判断 + 机会清单(每个机会:依赖的技术成熟节点/竞争密度/我们的差异化),形成立项建议。

## 3. 验收与节奏

- Wave 1 预期 1-2 天内队列跑完;结果审后触发 Wave 2 入队。
- 所有 worker 产出必附 envelope,原声/数据必须回指来源;无法确认的玩家(如 Lingbot/Happy Oyster 具体身份)标注置信度,禁止编造。
- 与既有项目的边界:与 `game-modeling`(mixar 分析)、`inspiration`(3D 工作流)相关材料可交叉引用,不重复采集。
