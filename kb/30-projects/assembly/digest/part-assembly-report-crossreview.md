---
scope: project
tier: working
topics: [assembly]
---

# DeepSeek 外部报告交叉审 — part-assembly-report.md

> 日期:2026-07-07 | 审者:CC(Architect)| 源:`raw/part-assembly-report.md`(HB 自行投递 DeepSeek 产出)
> 依据草案约定:"DeepSeek 易混淆'论文声称'与'已验证',报告回来先过交叉审再定裁决"。

## 裁决:结论层采纳,引文层隔离

**采纳(与我方独立调研 T-20260706-002 交叉印证一致)**——报告三大结构性结论可作为 D1/D2 裁决证据:

1. **Q1 分层验证成立**:L1 已被部件级生成(Hunyuan3D-Part/X-Part/P3-SAM 等)充分覆盖,无需自研生成模型;
   L2"接触面几何条件化"是真缺口(bbox 条件≠接口几何条件);**L3 文献空白,无基线**。
   → 直接支撑 D1(L1 出货/L2 立研/L3 攒数据)。
2. **Q2 跨轨配准(mesh↔B-rep)无系统性解法**,是架构最大技术风险。
   → 支撑"一期选机器人仿真(公差宽容)、跨轨硬骨头顺延二期"的 PRD 判断;也支撑 D2(接口永走参数化轨,
   一期内跨轨面收窄到"参数化接口件 vs mesh 外壳"的碰撞级配准,不碰真公差)。
3. **竞品无人做"关节语义+仿真导出"**(唯一迹象 PEGAVERSE PHIDIAS,证据仅新闻稿);
   部件分割 3-6 个月商品化白热化,纵深窗口期约 6-12 个月。→ 一期节奏必须紧。

另采纳两条重要增量:**G4(sim-in-the-loop 出厂验收无人研究,须自研,可基于 SAPIEN/MuJoCo)**、
**G5(ASG→草模→约束生成端到端管线无先例,耦合工程量大但技术风险中等)**——G5 正是我们的产品内核,
"无先例"在此处是好消息(蓝海)而非坏消息(基线各环节均存在)。

**隔离(不得直接引用,须逐条核实后方可进 spec)**——引文元数据错误率高,已证伪样例:

- Ditto:机构写 NVIDIA+MIT,但其自附链接为 UT-Austin-RPL,自相矛盾;
- PARIS:写 CVPR 2024/UCLA/单图,与我方 T-20260706-002 抓到的 ICCV 2023 原文 PDF 冲突;
- Articulate-Anything:写 arXiv 2025.06/代码未公开,与我方抓到的 arXiv 2410.13882 冲突;
- SAPIEN:写 ICML 2020、repo 归 columbia-ai-robotics,公开记录为 CVPR 2020 / haosulab;
- JoinABLe/AutoMate 的机构/年份/repo 归属与公开记录不符;
- Tripo UniRig "200B 参数、1-5s 推理"数量级不自洽;
- 大量 GitHub 链接呈 `github.com/<论文名>/<论文名>` 模式,系典型编造特征。

## 后续动作

- 复用清单(P3-SAM/X-Part/SAPIEN/Real2Code/URDFormer/JoinABLe/数据集)按"线索"对待,
  立 `spec-report-verification`(retriever/executor, light):逐条核实真实 repo、License(尤其
  GAPartNet CC-BY-NC 商用禁令、腾讯系开源条款)、指标复现口径,产出核实版复用清单。
- 本交叉审结论已并入 `PRD.md` v0.2 与决策草案证据栏。

---
关联:`decisions/20260706-articulation-generation-route.md` | `PRD.md`
