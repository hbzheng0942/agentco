# Golden Card · Ep.1 Mesh Editing (Sculpting) — From AI to Game-ready

> 标定卡(人工精读,2026-07-09)。用途:校准 L1 蒸馏 prompt 的对照标准。
> video: `ouHL_Rlebss` · https://www.youtube.com/watch?v=ouHL_Rlebss · 20m59s
> 上游卡片: 无(系列第1集;输入模型来自 3D AI 生成,他另有视频讲生成)
> 下游卡片: Ep.2 retopology(低模+法线烘焙)→ Ep.3 UV/烘焙 → Ep.4 贴图 → Ep.5 绑定动画 → Ep.6 上架

**goal**: AI 生成的 GLB 模型(恐龙)→ 几何缺陷修复完毕、可进入 retopo 的高模
**tools**: Blender(免费;Edit/Sculpt/Object 三模式)

## stages

### S1 导入与清理 [01:00-02:30]
- ops: 导出 GLB → 拖入 Blender,**不改任何导入设置**,Import;Material tab → `-` 移除材质;视图切 Solid
- accept: 只看几何、无材质干扰
- rationale: **先改几何后重做贴图**——几何改动后原贴图必然错位,所以第一步就删掉
  (工序排序逻辑,原话 [02:00-02:30])
- visual_deps: 生成该模型用的 AI 工具名(口播含混"it 3D",疑为 Hitem3D)⚠︎visual@[00:30]

### S2 缺陷盘点(判断工序,纯经验)[02:30-03:31]
- ops: 旋转查看模型,列缺陷清单:眼球(删→换球体)/牙齿/脚趾/腹部条纹过渡/背部条纹/爪子/尾下纹样
- accept: 有明确的逐项修复计划再动手,不边看边改
- rationale: AI 生成模型的**典型缺陷分类**——眼球糊、细节碎、对称性差、纹样断裂。
  这一步是"老师傅的眼",纯判断,无操作
- visual_deps: 每个缺陷的具体外观 ⚠︎visual@[02:30-03:31]

### S3 预处理:Clear Sharp + Remesh [03:31-05:31]
- ops: Edit Mode → edge mode → 右键 → **Clear Sharp**;Sculpt Mode → Remesh voxel size ≈0.02 ⚠︎visual@[04:31]
- accept(带调参环,原话 [04:31-05:31]):用 clay brush 试画一笔——
  - 画痕平滑 → 分辨率够,继续
  - 太平滑/顶点过多/卡顿 → 调低分辨率
  - 画痕有棱 → 调高分辨率
- fail_modes: 不 Clear Sharp → 模型渲染异常("very important step" [04:01])
- rationale: AI 生成网格自带 sharp 边标记和低密度区,不预处理后续笔刷全失真

### S4 对称化(省一半工) [05:31-06:31]
- ops: 前视图 → Edit Mode + Wireframe + **X-Ray**(否则选不到背面)→ 框选一半 → X 删除 faces
  → Object Mode → Mirror modifier,轴选 X + **clipping 开** → Apply
- accept: 确认两侧 100% 一致后 Apply
- fail_modes: 轴不对 → "might be a different axis in your case, depends on where the model is rotated"
  [06:01](参数依模型而变,非常数);忘开 X-Ray → 只删了朝屏幕的半边
- rationale: 对称模型改一半自动镜像;Apply 前是活修改器可反悔
- 后置:Object Mode 改过几何 → **再 Remesh 一次**("will not hurt" [06:31]);
  Sculpt 内开 mirror(和 modifier 是两回事!)

### S5 眼球置换 [07:32-11:33]
- ops: 遮罩画眼→Sharpen Mask→Invert Mask→Elastic Grab 把旧眼球推进去→Inflate+Ctrl(=deflate)
  →Shift 平滑→Clear Mask;Shift+A 加 UV Sphere→转90°→**Origin 设到 3D cursor 且 cursor 必须在世界原点**
  →Mirror modifier→Shade Smooth→回主体用 Elastic Grab 调眼窝+clay 补眼周
- accept: "look exactly as an eyeball" [11:33] ⚠︎visual
- fail_modes: 3D cursor 不在原点 → 镜像错位;修复:菜单把 cursor 归零 [10:02]
- rationale: origin 决定镜像基准——这是新手最常见的镜像翻车点,他专门解释了"为什么"

### S6 牙齿重建 [11:33-16:05]
- ops: Box Mask 粗选+普通 mask 补画→Invert→**Line Project 一刀切掉旧牙**→烂面处开 **Dyntopo**
  修复(clay+Ctrl、draw sharp+Ctrl 画分隔线、Shift 平滑)→新牙:Cube→删顶面→缩放→
  Subdivision modifier=2→Shade Smooth→**Edit Mode 内 Shift+D 复制**排一圈→Mirror X
- accept: 底视图检查牙齿贴合上颚 [15:05] ⚠︎visual
- fail_modes:
  - Dyntopo 开着不关 → 面数暴涨卡死("be careful...might result into freezes" [14:04])
  - 开 Dyntopo 前 modifier 未 Apply → 报错/异常,先 Apply [13:34]
  - 在 Object Mode 复制牙 → 变成独立物体,镜像/管理混乱;必须 Edit Mode 内复制 [15:05]
- rationale: 一颗牙做好→复制变体,比逐颗雕快一个量级

### S7 纹样重绘(条纹/尾下)[16:05-18:37]
- ops: Smooth 抹掉 AI 原纹样→**Draw Sharp 从中线起笔重画**(对称起点)→**Pinch 收窄线条**→
  低强度 Smooth;尾下改用 Stroke=**Line 模式**(vs 默认 Space),F 调小,强度 0.5 [17:36]
- accept: 线条"way accurate"于 AI 原生成 [17:06] ⚠︎visual
- rationale: **AI 的纹样不修——直接删了重画**。修复成本 > 重画成本,是他对 AI 产出的
  核心处置原则(可推广:低质细节区域重做,不缝补)
- economics: 纹样全部重画 ≈15min [17:06]

### S8 细节收尾:爪/纹深 [18:37-20:07]
- ops: 爪:Smooth→Elastic Grab 调形→**Crease Polish 沿缘压线**→Pinch;
  纹样连接处用 crease sharp 加深"更有效果"
- accept: 逐爪对照,前爪逻辑复用到后爪("absolutely the same logic" [19:07])

### S9 终检与交接 [20:07-20:37]
- ops: 全模型环视,对照 S2 缺陷清单逐项核销
- output: 高模(高面数、几何正确)→ 交 Ep.2 做低模+法线烘焙
- rationale: 终检对照的是**开工前的缺陷清单**,不是凭感觉

## cross_cutting(贯穿性老师傅经验)

- 快捷键体系:`F`=笔刷大小 · `M`=遮罩 · `Shift`=临时平滑(不用切笔刷)· `Ctrl`=反转任何操作(brush/mask/select 通用)· `~`=视角菜单 · `Shift+A`=加物体
- 心法:**mask→invert→操作** 是所有局部修改的标准三步;对称模型必先对称化;
  AI 产出"删了重画"优于"缝补"
- 反模式:Dyntopo 常开、Object Mode 复制部件、3D cursor 不归零就镜像

## economics
- 视频 21min;实际工时:纹样 15min + 其余未口播 ⚠︎(speedrun 系列有整段计时,可交叉)

## L3 视觉层待补清单(本卡的 visual_deps 汇总)
1. Remesh voxel size 精确值 [04:31] 2. 生成工具名 [00:30] 3. 各笔刷 strength 值(多处)
4. S5/S7/S8 的 accept 外观标准(需帧) 5. modifier 面板具体设置 [06:01][14:35]
