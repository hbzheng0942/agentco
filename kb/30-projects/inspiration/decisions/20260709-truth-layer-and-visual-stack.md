# 决策:采集真值层设计 + 视觉分析开源技术栈

> 2026-07-09 · 背景:分析思路/维度必然反复迭代,不能每次迭代重新抓取。
> 原则:**采集一次成真值,分析多次皆下游**。

## 一、真值库分层(data/inspiration/<slug>/)

```
L0 原始层(真值,不可变,抓到即冻结)
  inventory.json        频道全量元数据(flat)
  info/<vid>.info.json  单视频完整元数据(description=章节/工具链接)
  subs/<vid>.*.json3    字幕原始格式(YouTube 原生,带毫秒级时间戳)
  video/<vid>.mp4       720p 原片(仅精选集;这是视觉层的真值,帧都从这来)

L1 确定性派生层(可由 L0 用固定脚本重生成,损坏可弃)
  transcripts/<vid>.txt       bin/yt_transcript.py 产物(带[mm:ss]锚)
  scenes/<vid>.json           镜头边界(scene-detect 产物)
  frames/<vid>/<ts>.jpg       抽帧(带 manifest)
  ocr/<vid>.json              帧上文字/参数读取

L2 分析层(会反复迭代,永远只以 L0/L1 为输入)
  → kb/30-projects/inspiration/digest/cards/*(workflow cards)
```

**留痕纪律**:
1. L1 每个派生目录带 `manifest.json`:生成脚本+版本+参数+源文件哈希+时间——
   分析口径变了,只改 L2;抽帧策略变了,重跑 L1 并 bump manifest,L0 永不动
2. L0 只增不改;视频下架/改标题时保留旧档,新抓另存
3. 视频文件不进 git(已 gitignore),但**必须进离机备份**(backup.sh 范围待确认 ⚠︎)

## 二、视觉层开源盘点(2026-07 调研)

| 层 | 方案 | 定位 | 备注 |
|---|---|---|---|
| 镜头切分 | PySceneDetect / ffmpeg scene filter | L1 scenes | CPU 即可;ffmpeg 用 pip imageio-ffmpeg 静态二进制,免 sudo |
| 屏幕结构化 | **OmniParser v2**(微软,CC-BY-4.0) | 截图→结构化 UI 元素(YOLO 图标检测+Florence-2 语义) | 需小 GPU;可走 M4 本地通道(gpu_worker.sh 模式) |
| 帧上文字/参数 | PaddleOCR / EasyOCR | 读参数面板数值(⚠︎visual 补值的主力) | CPU 可跑;Blender 深色 UI 小字,需 720p+ 帧 |
| 帧语义理解 | **Qwen3-VL**(开源;或 API) | 时间戳对齐+秒级索引,256K ctx 可整片喂;8B≈上代72B | 我方已有 qwen 通道(auditor 用 qwen-max)→ **qwen3-vl API 是零新增基建的路**;kimi-long(digester-visual)为备选 |
| 整库检索问答 | HKUDS **VideoRAG**(KDD'26) | 双通道:跨视频知识图谱+多模态编码;LongerVideos 基准 134h | 参考架构价值>直接采用;我们的 workflow card 是更定向的蒸馏,但其"跨视频图谱"思路对'工序卡片跨视频聚合'有直接借鉴 |

## 三、路线裁决

**v0 视觉流水线**(先跑通,不追求全自动):
1. L2 精选 ~20 视频下载 720p(真值)
2. scene-detect 全片切段 + **字幕层 ⚠︎visual@[mm:ss] 锚点定向抽帧**(±3s 内抽 3-5 帧)——
   靶向抽帧优先于均匀扫描,靶点清单由 L1 蒸馏卡自动产出
3. 靶点帧 → OCR(读参数)+ qwen3-vl/kimi-long(读 UI 状态与外观验收标准)→ 回填卡片 ⚠︎visual 项
4. OmniParser 暂缓:等"UI 元素级结构化"有真需求(如做 agent 可执行 DSL)再上,走 M4 通道

**不采用**:整片喂 VLM(36h 全量成本高且丢参数细节);OmniParser 起手(重且现阶段过度)。

## 依据
- OmniParser: github.com/microsoft/OmniParser(v2, OmniTool)
- Qwen3-VL: arxiv 2511.21631(timestamp 对齐/256K→1M ctx)
- VideoRAG: github.com/HKUDS/VideoRAG(KDD'26, arxiv 2502.01549)
- PySceneDetect/EasyOCR/PaddleOCR/VideOCR: 各 github
