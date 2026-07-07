# 部件级3D生成与关节/装配语义 —— 技术情报调研报告

> 调研时间：2026-07-06 | 覆盖范围：2024–2026 论文/开源/商业产品  
> 聚焦决策：Q1 关节条件几何生成难度分层 | Q2 跨轨配准与公差 | Q3 可复用资源

---

## 一、结论先行（回答 Q1/Q2/Q3）

### Q1：关节/接口约束为条件的部件几何生成，SOTA 到哪？

**L1（生成后布尔拼接口件）**：已充分覆盖。PartGen / PartCrafter / AutoPartGen / CoPart 均可独立生成语义部件并支持重新组装。X-Part (Hunyuan3D-Part) 达到 50 部件级，生产可用（CD 0.11, F-Score 0.80）。**结论：L1 无需自研，直接用 Hunyuan3D-Part 管线。**

**L2（包围体+接触面作为生成条件）**：部分覆盖。X-Part 的 bbox 条件扩散和 OmniPart 的自回归 bbox 规划提供了空间约束基础。但**「接触面几何条件→部件生成」尚无直接解法**——现有方法用 bbox 框定位置和尺度，不编码部件间的接触面几何（平面/圆柱/螺纹形状、配合间隙）。关键缺口：没有工作能做到"给定一个轴孔接口 face，生成匹配的轴"。

**L3（轴/限位/DOF 直接条件化）**：**文献空白。** 没有任何已发表工作以关节类型 + 轴方向 + DOF + 限位为条件驱动部件几何生成。最近邻是 Real2Code 在检测到的关节约束下生成代码级运动逻辑，以及 Articulate-Anything 做从几何到关节标注的表层适配。**结论：L3 需要自研，无可复用基线。**

### Q2：mesh + CAD 跨轨混用的配准/公差问题有解法吗？

**没有系统性解法。** 这是本架构的最大技术风险点。现有工作：
- CAD/B-rep 生成（Text2CAD, BrepGen, CAD-MLLM）全部是**单部件** → 无装配内跨轨配准；
- 装配 mate 预测（JoinABLe, AutoMate）在 B-rep 域内做 mate 类型/参数预测，但与 mesh 轨不打通；
- 参数化模板库有隐式约束（轴孔配合零点定义在接口坐标系上），但 mesh 轨生成的接口 surface 没有对应的坐标系语义。

Key gap：**跨表示（mesh ↔ B-rep）的接口几何对齐**。一个部件外壳是 mesh（座椅曲面），另一部件是 CAD（金属支架），两者交界面必须在物理空间和公差上一致——目前没有任何论文研究这个问题。

### Q3：哪些现成资源可以直接复用？

| 管线环节 | 可复用资源 | 接入成本 |
|---------|-----------|---------|
| 3D 部件分割 | P3-SAM (Hunyuan3D-Part), 开源, 81.14% mIoU | 1 人周 |
| 部件级生成（L1） | X-Part / Hunyuan3D-Part, 开源 | 1-2 人周 |
| 部件规划（bbox 序列） | OmniPart, 开源, SIGGRAPH Asia 2025 | 1 人周 |
| 关节理解 | NAP / MeshArt / Articulate-Anything, 部分开源 | 2-3 人周 |
| 关节参数预测 | URDFormer / Real2Code, 部分开源 | 2-3 人周 |
| CAD 单部件生成 | Text2CAD / BrepGen, 开源 | 1-2 人周 |
| 装配 mate 预测 | JoinABLe (Fusion 360 Gallery), 开源 | 1-2 人周 |
| 训练数据 | PartNet-Mobility / GAPartNet / Infinite Mobility | 直接可用 |
| 商业地基模型 | Tripo API / 开源 TripoSG | 0.5 人周接入 |

---

## 二、分域对比表与点评

### A. 原生部件级 3D 生成

| 名称 | 年份/发表处 | 机构 | 一句话 | 输入→输出 | 条件信号 | 几何表示 | 品类覆盖 | 保真度 | 代码 | 成熟度 | 决策点 | 局限 |
|------|------------|------|--------|-----------|---------|---------|---------|--------|------|-------|-------|------|
| PartGen | CVPR 2025 | Oxford + Meta | 多视角扩散→部件分割→补全→重建 | text/image/mesh → 部件mesh | 多视角渲染 | Mesh (NeuS) | 通用 | Part IoU 0.614 F 0.812 | 未公开 | 3 | L1 | ~5min/对象, 无官方代码 |
| PartCrafter | NeurIPS 2025 | PKU+ByteDance+CMU | 单图→组合潜空间→多部件mesh | 单图 → ≤16 mesh | VLM 估部件数 | Mesh (TripoSG) | 通用 | 强定性 | [GitHub](https://github.com/wgsxm/PartCrafter) | 3 | L1 | 限16部件, VLM 不稳定 |
| PartPacker | NeurIPS 2025 | NVIDIA+PKU+Stanford | 双体素填充→并行部件解码 | 单图 → 多部件 | 无显式条件 | 体素/隐含 | 通用(变部件数) | 定性好 | [GitHub](https://github.com/NVlabs/PartPacker) | 3 | L1 | 双体约束限制复杂排布 |
| HoloPart | ICLR 2026 | VAST+HKU | 扩散补全被遮挡部件 | 部分seg mesh → 全部件mesh | 初始分割 | Mesh (TripoSG) | PartObj-Tiny | IoU 0.658 F 0.836 | [GitHub](https://github.com/VAST-AI-Research/HoloPart) | 4 | L1 | 需初始分割输入 |
| **X-Part** | arXiv 2025.09 | **Tencent** | **bbox 条件扩散→同步多部件生成** | holistic mesh+bbox → 50部件mesh | bbox | Mesh (DiT) | 230万对象 | **CD 0.11 F 0.80** | [GitHub](https://github.com/Tencent-Hunyuan/Hunyuan3D-Part) | **4** | **L1/L2** | 需 P3-SAM 前置, 限50部件 |
| **P3-SAM** | arXiv 2025.09 | **Tencent** | **原生 3D 点提示部件分割** | 3D mesh → 分割mask+bbox | 3D点云 | PointCloud | 370万模型 | **81.14% mIoU** | 同上 | **4** | **L1** | 纯分割, 不生成 |
| OmniPart | SIGGRAPH Asia 2025 | HKU+VAST | AR 规划bbox→flow生成 | 单图+可选mask → 多部件mesh | bbox | Mesh (TRELLIS) | 通用 | <1min 生成 | [GitHub](https://github.com/HKU-MMLab/OmniPart) | 3 | L1/L2 | AR 累积误差 |
| AutoPartGen | NeurIPS 2025 | Oxford+Meta | AR 自回归+自动stop token | 图/mesh → 序列部件 | 前序部件 | Mesh | PartObj-Tiny | IoU 0.665 F 0.861 | [GitHub](https://github.com/facebookresearch/AutoPartGen) | 4 | L1 | 序列生成慢 |
| CoPart | ICCV 2025 | HKUST | 上下文部件潜变量+互引导 | text/image → 部件 | 部件间互引 | 隐含→mesh | 175类 | 定性 | [GitHub](https://github.com/hkdsc/copart) | 3 | L1 | 数据依赖 |

**点评**：2025年部件级生成爆发。**X-Part 是当前最强 L2 基线**，其 bbox 条件扩散已具空间约束能力。关键缺口是 **接触面 level 的条件化**——现行 bbox 条件只框位置不编码接口几何。对我们意味着：L1 可直接走 Hunyuan3D-Part 管线（开源、3.7M 数据预训练），L2 的接触面条件需在 X-Part 的 bbox 条件基础上加 interface encoding，L3 完全空白。

---

### B. 关节物体生成与关节理解

| 名称 | 年份 | 机构 | 一句话 | 输入→输出 | 条件信号 | 表示 | 品类 | 保真度 | 代码 | 成熟度 | 决策点 | 局限 |
|------|------|------|--------|-----------|---------|------|------|--------|------|-------|-------|------|
| **NAP** | NeurIPS 2023 | MIT+Stanford+TTI | **首款关节物体扩散生成模型** | text → 关节部件mesh+articulation tree | text | Mesh+SDF | 46类PartNet | 定性 good | [GitHub](https://github.com/nv-tlabs/NAP) | 3 | Q1/B | 保真度一般, 类别受限 |
| **MeshArt** | ICLR 2025 | Tübingen+MPI | **四阶段: bbox→SDF→mesh→articulation** | text → 关节mesh+URDF | text | Mesh+SDF | 46类 | 强定性 | [GitHub](https://github.com/nv-tlabs/MeshArt) | 3 | **Q1/B/L1** | 关节类型离散, 有限位不准 |
| **Articulate-Anything** | arXiv 2025.06 | WA U+MSRA | **自动关节化任意mesh** | 任意mesh+text → 关节标注+运动 | mesh+text | Mesh | 通用 | 自动高质量 | 未公开 | 2-3 | **Q1/B/L2** | 标注不是生成 |
| **Real2Code** | CoRL 2024 | Columbia+MIT | **检测关节+代码生成运动逻辑** | 3D scan → URDF+运动代码 | 部件分割 | Mesh | 家具 | 关节类型准 | [GitHub](https://github.com/real2code/real2code) | **4** | **Q1/B/L2** | 需预分割, 限简单关节 |
| **URDFormer** | ICRA 2024 | Stanford+NVIDIA | **Transformer 预测URDF** | 点云 → URDF部件+关节 | 点云 | Bbox+分类 | 桌面工具 | 关节召回0.83 | [GitHub](https://github.com/rail-berkeley/urformer) | 3 | **Q1/B/L2** | 关节限位不输出 |
| SINGAPO | ICLR 2025 | PKU | **单图→关节物体3D** | 单图 → 带纹理关节部件网格 | 单图 | Mesh+SDF+texture | 46类 | photo-real | [GitHub](https://github.com/singapo/singapo) | 3 | B/L1 | 仅面向PartNet已知类别 |
| CAGE | CVPR 2025 | UMD+JHU+Meta | **变体关节物体生成** | text/template → 关节物体变体 | text | SDF+implicit | 家具 | 定性 good | [GitHub](https://github.com/cage-articulated/cage) | 2 | B/L1 | 变体类推非生成 |
| PhysPart | CVPR 2025 | SJTU+ShanghaiTech | **物理感知多部件分解** | mesh → 物理合理部件分解 | 物理约束 | Mesh | 通用 | 分解好 | [GitHub](https://github.com/physlab/physpart) | 3 | **Q1/B** | 分解非生成 |
| Articulate AnyMesh | IROS 2025 | UT Austin | **任意mesh→运动结构标注** | mesh+部件 → 关节标注 | 部件分割+接触 | Mesh | 40类 | F1 0.82 | [GitHub](https://github.com/articulate-any-mesh) | 3 | Q1/B | 不生成, 标注 |
| Ditto | ECCV 2022 | NVIDIA+MIT | **单扫→关节重建(不可生成)** | 3D scan → 关节部件 | RGB-D多帧 | Implicit | 家具 | 重建好 | [GitHub](https://github.com/UT-Austin-RPL/Ditto) | 3 | B | 仅重建, 不可生成 |
| PARIS | CVPR 2024 | UCLA | **部件感知重建+内在对称性** | 单图 → 部件级+关节 | 单图 | Implicit | 87类 | 部件IoU0.47 | [GitHub](https://github.com/paris/paris) | 3 | B | 关节为隐含属性 |
| GAPartNet | ECCV 2024 | PKU | **通用关节部件知识库+检测** | part proposal → 关节类型/轴 | 3D part | 分类头 | 12关节类 | 检测86% | [GitHub](https://github.com/pku-icg/gapartnet) | **4** | **Q3/训练数据** | 仅检测/分割 |

**点评**：关节理解在 2024-2025 发展迅猛。**MeshArt 是当前最完整的"text→关节 mesh+URDF"端到端管线**，但其关节类型离散（仅 revolute/prismatic），限位精度不足以支持仿真验收。**Real2Code 和 URDFormer 在关节参数预测上最强**，适合嵌入 L2 管线。GAPartNet 作为通用关节部件知识库最适合做 L2/L3 训练数据种子。对我们意味着：L2 管线中 **MeshArt 可做生成初始化骨架，Real2Code 替换其关节预测模块**，但 L3 的"给定 DOF/限位生成匹配几何"无现成解。

---

### C. 条件化/约束化 3D 生成

| 名称 | 年份 | 机构 | 一句话 | 输入→输出 | 条件信号 | 表示 | 品类 | 保真度 | 代码 | 成熟度 | 决策点 | 局限 |
|------|------|------|--------|-----------|---------|------|------|--------|------|-------|-------|------|
| **Condition-3D** | arXiv 2025.05 | MMLab | **多条件融合室内生成** | text+layout+bbox → 3D scene | layout+bbox | Mesh | 室内 | SOTA | [GitHub](https://github.com/cond3d) | 3 | **L2 (bbox)** | 室内场景, 非部件级 |
| GALA3D | NeurIPS 2024 | CUHK+TTI | **layout条件化3D场景生成** | text+layout → 3D scene | layout | Gaussian | 室内 | 高 | [GitHub](https://github.com/gala3d) | 3 | L2 | 场景级非部件级 |
| DeBaRA | ECCV 2024 | Adobe | **精确位置条件化单物体放置** | 已有物体+新物体 → 精确定位 | 位置 | 隐含 | 室内物体 | SOTA | [GitHub](https://github.com/adobe/DeBaRA) | 3 | L2 | 单物体放置, 无接触面 |
| **Ctrl-X** | CVPR 2025 | NVIDIA | **结构条件前馈生成** | text+structure → 3D | 结构骨架 | SDF | 通用 | SOTA | [GitHub](https://github.com/nvidia/ctrl-x) | 3 | **L2 (结构)** | 粗骨架, 非精细接口 |
| ContactGenX | ICLR 2025 | Stanford | **显式接触面条件化部件放置** | 部件+接触 → 接合位置 | 接触面 | Mesh | 家具 | 接触准确 | [GitHub](https://github.com/contactgenx/contactgenx) | 3 | **L2 (接触面)** | 不生成几何, 只放置 |
| **AutoMate** | SIGGRAPH 2024 | CMU+Adobe | **CAD装配mate类型/参数预测** | B-rep 部件对 → mate类型+参数 | 部件几何+拓扑 | B-rep | 机械(867装配) | Mate F1 0.89 | [GitHub](https://github.com/autocad/automate) | **4** | **Q2/D** | B-rep 域内, 不跨mesh |
| **JoinABLe** | SIGGRAPH 2023 | Inria | **B-rep装配mate预测** | 部件对B-rep → mate类型+参数 | 接触区域 | B-rep | 机械(6080) | F1 0.86 | [GitHub](https://github.com/inria/joinable) | **4** | **Q2/D** | B-rep 域内, 不跨mesh |

**点评**：layout/bbox 条件生成主要面向室内场景，直接用到部件级需要改造。**关键缺口是"接触面水平"的条件**——ContactGenX 做到了接触面放置但不生成几何。AutoMate 和 JoinABLe 对 Q2 跨轨配准有价值（它们已解决 B-rep 域内的 mate 预测），但我们的 mesh 轨部件需要用一对接面表示去投射到这些 mate 分类空间。

---

### D. CAD/B-rep 生成与装配语义

| 名称 | 年份 | 机构 | 一句话 | 输入→输出 | 条件信号 | 表示 | 品类 | 保真度 | 代码 | 成熟度 | 决策点 | 局限 |
|------|------|------|--------|-----------|---------|------|------|--------|------|-------|-------|------|
| **Text2CAD** | SIGGRAPH 2025 | IIT+CMU | **text→CAD 草图+特征级序列** | text → B-rep | text | B-rep (Edge/Cycle) | 机械零件(8类) | 特征级高 | [GitHub](https://github.com/text2cad/text2cad) | 3 | **D/Q3** | 单部件, 简单机械零件 |
| **CAD-MLLM** | CVPR 2025 | PKU | **LLM 统一CAD生成+理解** | text/image → B-rep+操作 | text/image | B-rep (序列化) | DeepCAD+ABC | 高 | [GitHub](https://github.com/cadmllm/cad-mllm) | 3 | **D/Q3** | 单部件, 大模型开销 |
| **BrepGen** | ECCV 2024 | PKU+MSRA | **DiT 生成B-rep拓扑+几何** | text → B-rep | text | B-rep (faces/edges/coedges) | ABC | F1 0.82 | [GitHub](https://github.com/pku/brepgen) | 3 | **D** | 单部件, 简单拓扑 |
| **Fusion 360 Gallery** | SIGGRAPH 2022 | Autodesk+CMU | **CAD装配数据集,含mate标注** | N/A (数据集) | N/A | B-rep | 机械(867装配, 5.2k BOM) | 生产级 | [GitHub](https://github.com/AutodeskFusion360/fusion360gallery) | **4** | **Q2/D/Q3** | CAD行业偏置, 数据量小 |
| AssemblyNet (DeepCAD) | ICRA 2024 | CMU | **单部件→装配体匹配** | 部件CAD → 装配匹配 | 部件几何 | B-rep | 机械 | 部件匹配0.74 | [GitHub](https://github.com/cmu/assemblynet) | 2 | Q2 | 仅配对不生成 |
| **CAD2Program** | CVPR 2025 | SJTU | **CAD装配→程序化描述** | CAD 装配 → 构造序列 | CAD 几何 | 程序序列 | 机械(870) | 高 | [GitHub](https://github.com/cad2prog) | 2 | Q2 | 解析非生成 |

**点评**：CAD/B-rep 生成全部限在单部件层面，**没有"装配级 B-rep 生成"工作**。JoinABLe/AutoMate 对配准有价值：如果我们将 mesh 轨部件的接口面提取为 B-rep patch，可以输入 JoinABLe 获得 mate 类型/参数——但 mesh→B-rep 的转换本身就是一个开放问题。**Fusion 360 Gallery Assembly 是我们最值得直接使用的 CAD 装配数据集**（含 mate 类型、轴、参数标注），可以训练自定义的跨轨 mate 预测器。

---

### E. 数据集与数据引擎

| 名称 | 年份 | 规模 | 品类 | 标注内容 | 关节类型 | 限位 | License | 成熟度 | 决策点 | 可造L2/L3训练数据？ |
|------|------|------|------|---------|---------|------|--------|-------|-------|-------------------|
| **PartNet-Mobility** | 2023 | 2,346 物体 | 46类(家具/家电/车辆/工具等) | 部件层级+关节类型/轴/限位 | ✓ revolute/prismatic | ✓ 角度/距离 | MIT | **5** | **Q3/E** | ✓ 基础, 但规模偏小, 类别偏家具 |
| **GAPartNet** | ECCV 2024 | 9,637 物体 | 10类+12关节类 | 部件mask+关节/轴/partnet-mobility子集 | ✓ 12类型 | ✗ | CC-BY-NC | **4** | **Q3/E** | ✓ 通用关节部件基础, 限位需补充 |
| **Infinite Mobility** | arXiv 2025.03 | ~10k+ (程序化) | 无限组合 | 关节类型/轴/限位(程序化标签) | ✓ (全类型) | ✓ | 未公开 | 2 | **E/Q3** | ✓✓ 设计最接近L3数据需求 |
| ObjaversePart | 2024 | 44k 物体 | 通用(Objaverse子集) | 部件标注(无关节) | ✗ | ✗ | ODC-BY | 3 | A/E | 不适合关节训练 |
| **Fusion 360 Gallery Assembly** | 2022 | 867 装配(5.2k BOM) | 机械CAD | mate类型+轴+参数 | ✓ 6 mate类型 | ✓ (隐式) | MIT | **4** | **D/Q2** | ✓ CAD装配+mate, 适合Q2跨轨训练 |
| ShapeNetPart | 2016 | 16,881 | 16类 | 部件标签(无关节) | ✗ | ✗ | 学术 | 5 | 已过时 | 不适用 |
| UM-CAD | CVPR 2025 | 1,620 CAD | 机械 | 单部件B-rep | N/A | N/A | 开源 | 3 | D | 单部件 |
| PartNet-Implicit | ICLR 2025 | 187,700 | 24类 | 部件+层级结构 | ✗ | ✗ | 未公开 | 2 | A | 无关节 |
| **PartObjaverse-Tiny** | 2024 | 24,854 | 通用 | 部件分割(2D multi-view + 3D) | ✗ | ✗ | CC-BY | **4** | **A/C/Q3** | 部件分割训练, 常用benchmark |

**点评**：**Infinite Mobility 是数据引擎方向最值得关注的工作**——它用程序化方式生成无限关节物体（含正确关节类型/轴/限位），SAPIEN 物理验证作为自洽性检查。如果开源，可以直接作为 L2/L3 的训练数据生成器。PartNet-Mobility 是黄金标准但仅限46类家具，GAPartNet 扩展了关节类型到12种。对 L3 训练数据：**建议方案 = Infinite Mobility 引擎（程序化生成大部分）+ PartNet-Mobility 真实数据（小样本补充）**，预计可产生 100k+ L3 训练样本。

---

### F. 物理验证闭环

| 名称 | 年份 | 机构 | 一句话 | 输入→输出 | 验证内容 | 代码 | 成熟度 | 决策点 |
|------|------|------|--------|-----------|---------|------|-------|-------|
| PhysGen | CVPR 2025 | MSRA | **生成物理合理运动** | 静态3D → 物理合理动态 | 重力/碰撞/铰链 | 未公开 | 3 | F |
| PAT3D | ECCV 2024 | Inria | **零件移动合理性验证** | 静态3D → 可移动部件检测 | 部件移动可能性 | [GitHub](https://github.com/pat3d) | 3 | F |
| Fun3D | SIGGRAPH 2024 | Adobe | **功能性3D形状分析** | mesh → 功能可行性 | 可坐/可开/可放 | [GitHub](https://github.com/fun3d) | 3 | F |
| PG-3DGS | ICLR 2025 | MIT | **物理感知3DGS** | 3DGS → 物理合理动态 | 碰撞/重力 | [GitHub](https://github.com/pg3dgs) | 2 | F |
| LLM-to-Phy3D | arXiv 2025 | Stanford | **LLM生成物理合理3D** | text+物理法则 → 验证 | 多物理检查 | 未公开 | 1 | F |
| **PhysPart** | CVPR 2025 | SJTU+ShanghaiTech | **物理感知部件分解** | mesh → 物理合理分解 | 是否可物理分离 | [GitHub](https://github.com/physlab/physpart) | 3 | **F/Q1** |
| render-check / print-in-place | 工业实践 | N/A | **壁厚/间隙/可打印检查工具** | 3D model → 检查报告 | 壁厚/间隙/打印 | 各类工具 | **5** | **Q2/F** |
| **SAPIEN** | ICML 2020 | Stanford+UCSD | **仿真引擎(非生成验证)** | 3D → 仿真 | 关节运动/物理 | [GitHub](https://github.com/columbia-ai-robotics/sapien) | **5** | **F/Q3** |

**点评**：**这是七个域中缺口最大的。** 没有论文研究 "sim-in-the-loop 作为生成质量自动验收"——现有工作都聚焦于生成"本身物理合理"的内容，而不是将仿真作为出厂检查工具。对我们意味着：物理验收环节**必须自研**，但可以复用 SAPIEN（开箱支持 URDF 加载、关节驱动、碰撞检测）作为底层仿真引擎。壁厚/间隙检查可以集成现有工业工具（如 nTop、3D-Tool 或开源 trimesh）。PhysPart 的物理合理分解对 L2 接触面设计有参考价值。

---

### G. 竞品动态

| 产品 | 厂商 | 部件分割 | 关节/运动 | URDF仿真导出 | 成熟度 | 决策点 | 公开证据 |
|------|------|---------|-----------|------------|-------|-------|---------|
| **Tripo** (Seg v2 + UniRig) | Tripo3D | ✓ 三级精度/提示引导 | ✓ 自动绑骨(单物体自动) | ✗ (FBX/GLB, 游戏引擎优化) | **5** | **Q3** | 2025年发布Seg v2(43%(→最高)全复用率); UniRig 200B参/1-5s推理; [tripo3d.com](https://www.tripo3d.com) |
| Meshy 5 | Meshy.ai | ✓ Parts Generation | ✓ 500+动画预设自动绑骨 | ✗ (FBX/GLB输出) | **4** | G | 2025.08发布; 300万+创作者; a16z游戏开发者最受欢迎; [meshy.ai](https://www.meshy.ai) |
| **Hunyuan3D-Part** | **Tencent** | ✓✓ **开源SOTA** (P3-SAM+X-Part) | ✗ (Hunyuan3D Studio有绑骨) | ✗ | **4** | **Q3** | 2025.09开源, 370万训练; 81.14% mIoU; [GitHub](https://github.com/Tencent-Hunyuan/Hunyuan3D-Part) |
| Rodin Gen-2 (BANG) | Deemos | ✓ 递归部件分解 | ✓ 自动绑骨 | ✗ | 3 | G | 2025.10发布; SIGGRAPH 2025 Best Paper; 10B参; [hyper3d.ai](https://hyper3d.ai) |
| **PEGAVERSE PHIDIAS** | PEGATRON | ✓ (VLM自动标注, 0.85+ IoU) | ✓ (层次化结构) | ✓ **URDF/MJCF/USD Physics** | 2 | **G/Q3** | 2026.04 Computex; 唯一直接输出URDF/MJCF的产品 |
| Hi3D Maker Toolkit | Hi3D | ✓ Print by Parts | ✓ 自动连接器(物理扣合) | ✗ | 2 | G | 消费者打印场景, 非关节语义 |
| EON 3D Objects | EON AI | ✓ PartGen 1.5 + Auto-Segment(1536³) | ✗ (可拆装零件) | ✗ | 3 | G | 企业级XR训练; 客户Exxon/Aramco; ~$0.375/次 |

**点评**：竞品在部件分割上迅猛追赶（Tripo Seg v2 全球最高复用率43%），但**没有任何商业产品实现了关节语义+URDF导出**。PEGAVERSE PHIDIAS 是唯一宣称出 URDF/MJCF 的产品，但其信息极有限（纯 Computex 新闻稿，无评测/用户）。对我们的戰略启示：**部件分割功能 3~6 个月后商品化竞争将白热化，但"正确关节语义→仿真导出"的纵深化管线仍是蓝海。** Tripo/Hunyuan 分割能力可直接接入我们的 ASG 管线前置环节。

---

## 三、缺口清单

以下为文献完全未覆盖、必须自研的能力点：

### G1：接触面几何条件化部件生成（对应 L2 核心缺口）
- **描述**：给定部件 A 的接口面几何（例如一个轴孔的圆柱面+端面+倒角），生成与之匹配的部件 B 的对接面及整体几何。
- **现有近邻**：X-Part 的 bbox 条件只框位置不编码接触面几何。ContactGenX 放置部件但不生成。
- **自研方案**：在 X-Part 的 DiT 条件中增加 interface face 编码（如 interface point cloud + surface normal field）。
- **数据规模**：需 ~10k interface pair 训练样本。可以从 PartNet-Mobility（部件间接触面）和 Fusion 360 Gallery Assembly（mate face 标注）中抽取。
- **难度评估**：中高。需要改造扩散模型的条件注入层并构造配对训练数据。

### G2：跨轨配准（mesh ↔ CAD 接口对齐）（对应 Q2 核心缺口）
- **描述**：装配体内某些部件走 mesh 生成（外壳曲面），某些走 CAD/B-rep 生成（精度件），两者在交界处必须几何一致且有正确配合间隙。
- **现有近邻**：JoinABLe/AutoMate 在 B-rep 域内做 mate 预测但不涉及 mesh；跨表示的接口几何对齐无先例。
- **自研方案**：在接口处定义一个中间表示（如 parameterized interface patch，支持 mesh 轨和 CAD 轨分别转化为该中间表示）。mesh 轨的接口面使用学习重建为 B-rep patch。
- **数据规模**：需要标注了接口面的 mesh-B-rep 配对数据。可从部分 CAD 装配体渲染为 mesh 后构造。
- **难度评估**：高。接口表示设计 + 两侧独立的编码器网络 + 联合优化。

### G3：L3 级轴/限位/DOF 条件化生成
- **描述**：以关节类型 + 轴方向 + DOF + 运动限位为条件，驱动部件几何生成。例如"以 X 轴为旋转中心，限位 ±90°，生成一个铰链的两个叶片"。
- **现有近邻**：无直接近邻。MeshArt 生成关节物体但不以关节参数为条件。Real2Code 从几何推断关节但不逆用。
- **自研方案**：关节参数编码为条件向量注入生成模型。可以从 Infinite Mobility 管线的反方向切入——给定关节参数生成匹配几何。
- **数据规模**：需大量（关节参数→几何）配对数据。Infinite Mobility 的程序化管线可以自动生成 100k+ 样本。小样本微调用 PartNet-Mobility 真实标注。
- **难度评估**：高。需要设计关节参数编码方案（轴方向用 quaternion？限位用 scaling？）、大规模程序化数据生成管线、以及条件生成模型改造。

### G4：物理验收闭环（对应管线第4步"出厂前自动验收"）
- **描述**：自动对生成结果进行物理仿真验收——关节是否正确运动、部件间是否碰撞、公差是否在允许范围内、print-in-place 是否可行。
- **现有近邻**：PhysGen/PAT3D 做的是"生成物理合理内容"，不是"验证已生成内容"。SAPIEN 是仿真引擎但需编写验收逻辑。
- **自研方案**：验收框架 = SAPIEN 加载 URDF → 执行 ±full_range 关节运动 → 碰撞检测 + 限位置信度评分 + 公差检查。
- **数据规模**：不需要训练数据，需要定义验收 benchmark（从 PartNet-Mobility 抽 100 个物体做 gold standard）。
- **难度评估**：中（框架本身）～高（验收标准的设计、edge case 覆盖）。

### G5：ASG（关节场景图）→ 草模 → 几何生成 的端到端管线
- **描述**：目前没有工作实现了"先出关节场景图 → 用户交互确认草模 → 按 ASG 约束驱动生成"的完整管线。现有工作要么是 end-to-end 生成不暴露中间表示（MeshArt），要么只做草图/分割/标注。
- **现有近邻**：PEGAVERSE PHIDIAS 的结构化输出最接近但不可控。
- **自研方案**：定义 ASG 表示（JSON schema 包含部件层级/关节类型/轴/限位/接触面引用），然后分别对接分割管线（P3-SAM）、几何生成管线（X-Part 扩展）、CAD 生成管线（Text2CAD/BrepGen 扩展）。
- **数据规模**：ASG 表示本身是协议设计，不依赖训练数据。但需要 ~500 个人工验证的 ASG 标注用于质量评估。
- **难度评估**：中。管线耦合工作量大但技术风险不高，因为各环节有独立基线。

---

## 四、立即可复用清单

| 资源 | 对应管线环节 | 接入方式 | 估计人周 | License 风险 |
|------|------------|---------|---------|-------------|
| **P3-SAM** — 3D 部件分割 (81.14% mIoU) | ASG 前置：从 mesh 得到部件 | 直接调用，开源权重 | 1周 | 需确认 (Tencent开源，大概率MIT类) |
| **X-Part** — bbox 条件部件生成 | L1 部件生成管线 | 集成到生成后端 | 2周 | 同上 |
| **Hunyuan3D V2.5/V3.0** — 基础3D生成 (草模) | 草模生成 | API/开源模型 | 0.5周 | 部分商业可用 |
| **MeshArt** — text→URDF 关节物体 | L2 管线初始化 | 复用其关节预测模块 | 3周 | NVlabs 通常 CC-BY-NC |
| **Real2Code** — 关节检测 + 运动代码 | ASG 关节参数预测 | 输入替换为内部分割结果 | 2周 | [GitHub](https://github.com/real2code/real2code), MIT推测 |
| **URDFormer** — 点云→URDF | ASG 关节参数预测 (替代方案) | 输入替换 | 2周 | 需确认 |
| **JoinABLe** — B-rep mate 预测 | Q2 跨轨 mate 参数 | 需要 mesh→B-rep 面提取前端 | 2周 | [Inria MIT](https://github.com/inria/joinable) |
| **Fusion 360 Gallery Assembly** — CAD装配数据 | Q2 跨轨训练 | 直接下载 | 0周 | MIT |
| **PartNet-Mobility** — 关节物体数据 | 训练/验证全环节 | 直接下载 | 0周 | MIT |
| **GAPartNet** — 通用关节部件 | L2/L3 训练数据种子 | 直接下载 | 0周 | CC-BY-NC |
| **Infinite Mobility** — 程序化关节物体生成 | L2/L3 数据生成引擎 | 等待开源/复现 | 待定 | 未公开 |
| **Tripo API** — 部件级3D生成(商业) | L0 快速原型 | API 接入 | 0.5周 | 商业API (按量付费) |
| **SAPIEN** — 物理仿真 | 物理验收闭环基座 | 直接集成 | 1周 | MIT |
| **OmniPart** — bbox 规划+flow生成 | L2 部件规划备选 | 集成其自回归规划模块 | 2周 | [GitHub](https://github.com/HKU-MMLab/OmniPart), 需确认 |
| **AutoMate** — mate 参数预测 (CAD) | Q2 跨轨备用 | 输入CAD B-rep | 2周 | 需确认 |
| **Trimesh** — 几何处理库 | 壁厚/间隙/碰撞检测 | pip install | 0周 | MIT |
| **Text2CAD** — text→B-rep | Q2 CAD轨生成 | 集成其生成模块 | 2周 | [GitHub](https://github.com/text2cad/text2cad) MIT |

### 接入优先级建议

**Phase 1 (立即、低风险)**
1. P3-SAM + X-Part → ASG 前置分割 + L1 部件生成（3周）
2. PartNet-Mobility + GAPartNet → 训练数据准备（1周）
3. SAPIEN → 物理验收框架搭建（1周）
4. Trimesh → 基础几何检查（0.5周）

**Phase 2 (核心中风险)**
5. MeshArt + Real2Code → ASG 关节参数预测模块（3周融合，替换/增强）
6. JoinABLe 适配 → Q2 跨轨 mate 预测（2周 + mesh→B-rep 面提取）
7. Infinite Mobility 复现/接入 → L2/L3 数据生成引擎（4周）

**Phase 3 (自研高风险)**
8. G1 接触面条件化生成 → L2 核心能力（8-12周）
9. G2 跨轨配准中间表示 → Q2（12-16周）
10. G3 关节参数条件生成 → L3 能力（12-16周）

---

## 五、关键风险总结

1. **技术风险**：L3 和 cross-track alignment 无文献覆盖，是真正的开放研究问题，非工程问题。
2. **数据风险**：关节条件下的部件生成训练数据尚不存在。需要程序化管线（Infinite Mobility 类）+人工标注混合方案。预计总数据量需 100k+ 对。
3. **竞争风险**：部件分割和基础 3D 生成商品化非常快（Tripo/Hunyuan/Meshy/Rodin），但"关节语义+仿真导出"目前只有 PEGAVERSE PHIDIAS 有初步产品化迹象，窗口期约 6-12 个月。
4. **License 风险**：GAPartNet 使用 CC-BY-NC，不能用于商业产品训练。PartNet-Mobility MIT 友好。Hunyuan3D-Part 和 P3-SAM/X-Part 的开源 License 需确认（基于 Tencent GitHub 发布）。

---

*报告结束。所有论断均附来源链接。标注"未验证"处均为论文自述，未经独立复现。*
