# 相似方法坑专项排查报告（Claude 生成）

生成时间：2026-06-08
审计基准：Codex 复审意见（CR-001~CR-008）+ Codex 方法思路类坑位汇总（METH-001~004）

---

## 零、排查原则（Codex 口径）

旧结果一律不进入 v0.4 主结果。本次排查不讨论"旧结果能不能复用"。旧材料只用于三件事：

1. 作为历史证据，说明为什么 v0.3 封存。
2. 作为诊断材料，帮助发现类似 OCS 采样问题的隐藏坑。
3. 作为方法/代码结构参考，但所有新结果必须在 v0.4 链路下重新生成。

**排查目标**：找出方法、思路、定义、数据链路中可能导致第二次整体重启的坑。

---

## 一、大坑（会改变 OCS/image/fusion 主结果或导致全链路重跑）

### H1：diffuse 基底下 A/B visible area 语义差异（~26% gap 非来自镜面采样）

| 属性 | 内容 |
|---|---|
| **ID** | METH-H1 |
| **级别** | 大坑 |
| **类别** | 采样 / 可见性 |
| **问题描述** | 纯 diffuse 模式下（rho_s=0，关闭所有镜面项），旧模块 A face-center OCS 与 Blender pixel-level OCS 仍存在 ~26% 差异（A_with_occ=0.0163 vs B_diffuse=0.0219，diffuse-only gap）。这说明 A/B 差异的主因不是镜面峰采样精度，而是**可见面积语义差异**：A 端用法线判据 `(n·sun > 0) & (n·det > 0)` 筛选可见面元，B 端用相机光栅化 depth 测试。两种可见性定义对薄板、遮挡边缘和斜面给出不同的有效面积。 |
| **为什么类似这次 OCS 采样问题** | 采样口径问题只是表象。更深层的问题是：OCS 的"可见表面"定义与图像的"可见表面"定义根本不同。即使 v0.4 改用 Blender-derived OCS，如果 OCS 积分时使用不同的 visible pixel mask（如 camera-only vs camera+sun），依然可能产生一个新的结构性差异。 |
| **证据文件** | `进度档案_仿真与反演_full.md` line 266-281（diffuse-only 验证结果）、line 384-385（"主因是可见面积差异，非镜面采样"）、line 385（太阳能板 72× 差异来自薄板两面均满足法线判据仅一面对相机可见） |
| **可能影响范围** | v0.4 OCS 积分中 visible pixel 的定义；per-part OCS 的绝对值；camera-only visibility vs sun+camera visibility 的选择；论文中 OCS 定义的方法描述 |
| **当前处置方式** | v0.4 使用 Blender pixel-level camera visibility 作为 OCS 可见性基准（与图像一致）。但 sun-side visibility 是否额外施加仍需方法冻结时决定。 |
| **应在哪个阶段关闭** | **方法冻结前** |
| **是否需要 Codex 复审** | 是 — pixel visibility mask 的定义（camera-only / camera+NoL>0 / camera+sun-visible）直接影响 OCS 的物理含义 |

### H2：薄板/平面结构的双面可见性问题（薄板两面法线均满足判据但仅一面相机可见）

| 属性 | 内容 |
|---|---|
| **ID** | METH-H2 |
| **级别** | 大坑 |
| **类别** | 采样 / 可见性 |
| **问题描述** | 太阳能电池板是薄板结构。旧模块 A 用法线判据 `(n·sun > 0) & (n·det > 0)` 时，薄板的两侧物理面（法线方向相反）**同时满足判据**（因为太阳和探测器在薄板的同一侧，薄板的两面法线分别指向两端）。但在相机光栅化中，**只有面向相机的那一面被渲染**。这导致 A 端 OCS 对太阳能板的面元计数是 B 端的 ~72 倍。 |
| **为什么类似这次 OCS 采样问题** | 这不是精度问题——更多面元反而导致更差的一致性。根因是面元级的法线判据无法模拟相机光栅化的 depth-buffer 遮挡。v0.4 用 pixel-level 采样能自然解决，但必须确认 Blender EXR 中对薄板的 depth 遮挡是否正确（polygon offset / z-fighting 风险）。 |
| **证据文件** | `进度档案_仿真与反演_full.md` line 384-387（"薄板两面均满足法线判据但仅一面对相机可见"、"太阳能板极端异常 ad/B_diff=72×"）、`subface_adaptive_comparison.csv` yaw=90° pitch=-40° taiyangnengban ad/B_diff=72× |
| **可能影响范围** | 太阳能板 OCS 贡献在旧模块 A 中被高估；per-part OCS 比例关系（金属主体 vs 太阳能板 vs 遮光板）在新旧 OCS 中可能显著不同 |
| **当前处置方式** | v0.4 使用 Blender depth-buffer visibility（与图像一致），薄板背面自然被剔除。需确认 Blender 渲染中薄板的背面剔除正确（已验证 Backfacing AOV=0，封闭网格外视图全部前向面）。 |
| **应在哪个阶段关闭** | **方法冻结前**——方法文件中必须明确：OCS 可见像素 = camera-visible pixels only；薄板背面不进入 OCS 积分 |
| **是否需要 Codex 复审** | 是 — per-part OCS 的新比例关系需要与旧 OCS 做差异审计 |

### H3：Blender Cycles 背向面着色伪影（NoL≤0 / NoV≤0 姿态产生非零残差）

| 属性 | 内容 |
|---|---|
| **ID** | METH-H3 |
| **级别** | 大坑 |
| **类别** | 遮挡 / 渲染 |
| **问题描述** | Blender Cycles 对外部视图的封闭网格，即使太阳在目标背面（NoL≤0），shading normal 仍会自动翻转向相机侧，产生一个非零的微小亮度残差（例如 yaw=0/pitch=-30 时 B=2.1e-3，而解析/A 端正确给出 0）。这在凸几何（立方体）上不可见（背面自然隐藏），但在真实卫星复杂几何的某些边缘姿态可能出现。 |
| **为什么类似这次 OCS 采样问题** | 这会系统性污染 OCS 在 NoL≈0 或 NoV≈0 姿态的数值。OCS 被解释为"光度截面积"，如果包含这些伪影，在某些姿态会被高估。v0.4 如果不在后处理中过滤这些像素，会在姿态网格的边缘区域引入非物理的 OCS 贡献。 |
| **证据文件** | `进度档案_仿真与反演_full.md` line 303（"yaw=0/pitch=-30 B端因Blender着色法线行为有微小残差"）、line 338（"Plate_H NoL=0 但 B=1.19e-3，已知 Blender Cycles 着色法线行为"）、line 371（"Blender Cycles 背向面着色是已知噪声源"） |
| **可能影响范围** | 极边缘姿态（|pitch|≈90°或 sun 近背面）的 OCS 数值；Per-part OCS 在这些姿态的信噪比 |
| **当前处置方式** | v0.4 BRDF 后处理中需要对 `NoL ≤ 0` 或 `NoV ≤ 0` 的像素显式设 OCS 贡献为零，不依赖 Blender shading normal 的自动翻转。 |
| **应在哪个阶段关闭** | **代码前**——在 brdf_postprocess 中增加 `NoL <= 0` 或 `NoV <= 0` 的显式零化 |
| **是否需要 Codex 复审** | 否 — 纯代码级处理 |

### H4：log1p / tone-mapping / 线性辐亮度 / 8-bit PNG 转换链未正式冻结

| 属性 | 内容 |
|---|---|
| **ID** | METH-H4 |
| **级别** | 大坑 |
| **类别** | 图像响应 |
| **问题描述** | 旧实验的图像处理管线是：线性辐亮度（f_r-based radiance）→ log1p 变换 → 8-bit PNG（0-255）→ 训练。log1p 选择是基于消融实验（12.13° vs raw 15.99°），但从未在方法文件中正式冻结以下问题：(a) log1p 是否改变了图像的物理亮度排序（单调性保留但间距变化）？(b) 退化实验中的噪声加在"log1p 空间"还是"线性空间"？v0.3 稿件 line 173 称"degradation follows expm1 -> degradation -> log1p"，但这是否在所有实验中一致执行？(c) 训练 PNG 的 0-255 范围与线性辐亮度范围（0~53.07）之间的映射关系是什么？ |
| **为什么类似这次 OCS 采样问题** | 图像响应链定义了"image-only 模型到底看到了什么物理量"。如果 log1p 转换不被理解为物理预处理的一部分，image-only 的"亮度"含义就会模糊。这不会导致 v0.3 级的重启，但会导致 image-only 结果的方法可复现性不足。 |
| **证据文件** | `进度档案_仿真与反演_full.md` line 587-589（"log1p mean=12.13° 胜 raw 15.99°"）、v0.3 稿件 line 147（"stored with a log1p intensity transform"）、line 173（"expm1 -> degradation -> log1p sequence"）、`_新对话启动包.md` line 92-96（实验11 log1p 空间加噪） |
| **可能影响范围** | image-only baseline 的复现性；退化实验的噪声施加位置一致性；论文方法部分 |
| **当前处置方式** | 方法冻结文件中必须写清：线性辐亮度 → log1p 动机（压缩动态范围，保留亮度排序）、log1p 变换公式、PNG 8-bit 存储范围与线性辐亮度的映射、退化实验的 noise 作用域 |
| **应在哪个阶段关闭** | **方法冻结前** |
| **是否需要 Codex 复审** | 是 — 图像响应链的定义直接影响 image-only 结果的物理可解释性 |

### H5：遮挡率从 35.78%→72.88% 的重新解释（EPSILON/min_hit_distance 修订后）

| 属性 | 内容 |
|---|---|
| **ID** | METH-H5 |
| **级别** | 大坑 |
| **类别** | 遮挡 |
| **问题描述** | 2026-05-12 将遮挡逻辑从 `exclude_parts` 切换为 `min_hit_distance=EPSILON` 后，真实三件套 mean 遮挡率从 35.78% 跳升到 72.88%（+37pp）。虽然经验证是正确结果（不是阈值误杀），但论文中的遮挡率从 ~36% 改写到 ~73%，必须提供详细的解释和证据。v0.4 如果使用 pixel-level visibility，遮挡率的定义再次改变（从 face-center ray-cast 到 depth-buffer），数值可能与两者都不同。 |
| **为什么类似这次 OCS 采样问题** | 遮挡率的数值锚点变化幅度（2×）与 OCS 采样问题（rel_err 117%）量级相当。如果 v0.4 的遮挡率又与旧值不同（第三次变化），论文中对遮挡率的任何引用都需要完整的审计链。 |
| **证据文件** | `项目理解.md` line 307（"ocs_with_occ mean 遮挡率 = 72.88%相较旧版 35.78% 增 +37pp"）、`进度档案_仿真与反演_full.md` line 208-210（EPSILON 敏感性扫描）、line 294-297（三部件各 mhd 遮挡率表） |
| **可能影响范围** | 论文中所有引用遮挡率的图表和文字；Fig.3d 遮挡率 heatmap；OCS with occlusion vs without occlusion 的比较 |
| **当前处置方式** | v0.4 使用 camera depth-buffer visibility 作为遮挡基础 + 可选 sun-side visibility。每种遮挡定义必须在方法文件中清晰区分。 |
| **应在哪个阶段关闭** | **方法冻结前** |
| **是否需要 Codex 复审** | 是 — 遮挡率的定义变化是 paper 的敏感性话题 |

---

## 二、小坑（不一定改变主结果，但影响复现/记录/一致性）

### S1：同部件/跨部件遮挡阈值区分——"待评估选项"从未被解决

| 属性 | 内容 |
|---|---|
| **ID** | METH-S1 |
| **级别** | 小坑 |
| **类别** | 遮挡 |
| **问题描述** | `项目理解.md` line 794 记录了"区分同部件/跨部件阈值"作为"待评估选项（非当前队列）"——对同部件命中用较大 mhd（跳过 1~5 mm 近邻几何），对跨部件命中仍用 1 mm。这可以降低 jinshuzhuti 的高遮挡率，但"无法区分同部件真实遮挡与同部件几何粘连"。这个选项从未被评估或决定是否采用。 |
| **证据文件** | `项目理解.md` line 794（"待评估选项（非当前队列，记录备查）"） |
| **可能影响范围** | jinshuzhuti 的遮挡率（72.88% 是否包含过度计数的几何粘连） |
| **当前处置方式** | v0.4 的 pixel-level visibility 用 depth-buffer 天然区分部件内和部件间遮挡（不需阈值）。但需要确认非水密网格不会产生 depth 伪影。 |
| **应在哪个阶段关闭** | **代码前** — 确认 Blender depth-buffer 遮挡对非水密 STL 的行为 |
| **是否需要 Codex 复审** | 否 |

### S2：NoV 抵消仅在正交投影+常数 pixel_area 下严格成立

| 属性 | 内容 |
|---|---|
| **ID** | METH-S2 |
| **级别** | 小坑 |
| **类别** | 面积 |
| **问题描述** | 旧 BRDF postprocess 中 OCS 公式 `Σ pixel_area · f_r · NoL` 是基于 `A_face_pix = pixel_area / NoV` 代换后 NoV 抵消推导的（进度档案 line 185）。但这一步严格成立的条件是：(1) 正交投影（pixel_area 为常数）；(2) 像素面积在投影前后关系为 `dA_projected = dA_surface · NoV`。在图像边缘像素（部分覆盖目标）或非正交投影下，这个关系不精确。v0.4 如果沿用此公式，需要明确其适用条件。 |
| **证据文件** | `进度档案_仿真与反演_full.md` line 185（"A_face_pix = pixel_area / NoV … NoV 抵消 … 数学自洽"）、`brdf_postprocess_summary.json` pixel_area_m2=0.00016015（常数） |
| **可能影响范围** | 边缘像素 OCS 贡献的高估/低估；论文方法部分的公式推导 |
| **当前处置方式** | v0.4 方法冻结文件必须明确：使用正交投影、pixel_area 为常数、"NoV 抵消"成立的边界条件、边缘像素处理策略 |
| **应在哪个阶段关闭** | **方法冻结前** |
| **是否需要 Codex 复审** | 是 — Codex CR-003 明确要求"方法冻结文件必须单独写一节 pixel_area" |

### S3：v0.3 汇报口径与真实数据流不一致

| 属性 | 内容 |
|---|---|
| **ID** | METH-S3 |
| **级别** | 小坑 |
| **类别** | 写作 |
| **问题描述** | 0603 汇报 slide 7 (line 143-144) 写道"OCS 借鉴 Blender 像素级采样的原因：面元中心采样速度快但对 GGX 金属窄镜面峰可能漏掉局部高光；Blender 光栅化提供更细可见区采样"。这个表述给人的印象是 v0.3 的 OCS 已经使用了 Blender 像素级采样。但实际上 v0.3 的反演数据全部来自旧模块 A face-center OCS。汇报口径超前于真实数据流。 |
| **证据文件** | `20260603_项目进展汇报_v2_extracted_text.txt` line 143-144、旧 CLAUDE.md §6.2（OCS 路径指向旧模块 A `ocs_scan.csv`） |
| **可能影响范围** | 如果审稿人或导师认为 v0.3 已完成 Blender-derived OCS，会形成错误预期 |
| **当前处置方式** | v0.4 的汇报和论文中必须明确区分：v0.3 使用旧 face-center OCS（已封存），v0.4 使用 Blender-derived OCS（正在进行） |
| **应在哪个阶段关闭** | **论文阶段** |
| **是否需要 Codex 复审** | 否 — 写作口径问题 |

### S4：edge pixel fractional coverage 未处理

| 属性 | 内容 |
|---|---|
| **ID** | METH-S4 |
| **级别** | 小坑 |
| **类别** | 面积 |
| **问题描述** | 当前所有像素分配相同的 `pixel_area`（正交投影下常数）。但目标边缘的像素仅部分覆盖目标表面（其余为背景），其有效 OCS 贡献面积应小于完整像素面积。当前不做 fractional coverage 修正，可能导致 OCS 对边缘像素过计。 |
| **证据文件** | `brdf_postprocess_summary.json` pixel_area_m2=0.00016015（统一常数）、Codex CR-003（"边缘像素是否做 fractional coverage 也要冻结"） |
| **可能影响范围** | OCS 绝对值在图像边缘区域被微幅高估（对总 OCS 贡献预计 <2%） |
| **当前处置方式** | v0.4 方法冻结文件中需决策：是否做 sub-pixel coverage 修正、还是接受为已知舍入误差 |
| **应在哪个阶段关闭** | **方法冻结前** |
| **是否需要 Codex 复审** | 是 — Codex CR-003 包含此项 |

### S5：sun/det 向量归一化未文档化

| 属性 | 内容 |
|---|---|
| **ID** | METH-S5 |
| **级别** | 小坑 |
| **类别** | 坐标 |
| **问题描述** | BRDF 计算依赖单位向量（NoL、NoV、NoH 全部使用 `max(dot(N, L), 0)` 等）。如果 sun 或 det 向量不是单位向量，D_GGX、G_Smith 和 OCS 积分全部错误。当前代码中 sun/det 向量在 `config.py` 中定义为 `[1,0,0.3]` 等（显然不是单位向量），但在 `ocs_core.py` 中是否归一化未在主要文档中明确。 |
| **证据文件** | `config.py`（SUN_VECTOR=[1,0,0.3]、DET_VECTOR=[0.5,-1,0.1] — 非单位向量）、`项目理解.md` line 118-119（配置表列出但未标注是否归一化） |
| **可能影响范围** | OCS 数值的系统性偏差（如果某端未归一化） |
| **当前处置方式** | 审计两端代码的向量归一化逻辑，在方法冻结文件中明确"所有方向向量在使用前均归一化为单位向量" |
| **应在哪个阶段关闭** | **代码前** |
| **是否需要 Codex 复审** | 否 |

### S6：多观测几何 OCS (5 几何) vs 单几何图像 (phase63) 的信息量不对等

| 属性 | 内容 |
|---|---|
| **ID** | METH-S6 |
| **级别** | 小坑 |
| **类别** | 数据划分 |
| **问题描述** | 当前 fusion 的 OCS 端使用 concat5（5 几何 × per_part_log），即 5 组 sun/det 方向的 OCS 特征拼接。但 image 端仅使用 phase63 单几何图像。这意味着 OCS 端有 5× 的观测几何信息。fusion 优于 image-only 的部分原因可能是 OCS 的多几何信息，而非 OCS 与图像的互补性。 |
| **证据文件** | `进度档案_仿真与反演_full.md` line 422-425（multi_geom: 5 组 sun/det，相位角 24°~120°）、v0.3 Codex 审阅 line 44-45（12f internal OCS reference 6.58° vs main OCS-only 5.91°，不同几何配置） |
| **可能影响范围** | fusion vs image-only 的比较公平性；论文 discussion 中需要讨论这个不对等 |
| **当前处置方式** | v0.4 论文 discussion 中应写一节讨论"信息量不对称"；主对比建议使用 1-geom OCS（phase63 同几何）作为更公平的 OCS-only baseline |
| **应在哪个阶段关闭** | **论文阶段** |
| **是否需要 Codex 复审** | 是 — 对比公平性是审稿关注点 |

### S7：latest-run 自动发现逻辑

| 属性 | 内容 |
|---|---|
| **ID** | METH-S7 |
| **级别** | 小坑 |
| **类别** | 路径版本 |
| **问题描述** | `_新对话启动包.md` line 118 中 manifest 使用 `sorted(glob.glob(_MANIFEST_GLOB), key=os.path.getmtime, reverse=True)[0]` 自动找最新 run。v0.4 如果不禁止此模式，可能误读到旧目录中的 run。 |
| **证据文件** | `_新对话启动包.md` line 118（"manifest = sorted(glob.glob…), key=os.path.getmtime, reverse=True)[0]"）、Codex CR-004（"反演脚本必须禁止 latest-run 自动读取旧路径"） |
| **可能影响范围** | v0.4 代码可能读入旧数据 |
| **当前处置方式** | v0.4 所有脚本使用显式 manifest 路径，禁止 latest-run 启发式 |
| **应在哪个阶段关闭** | **代码前** |
| **是否需要 Codex 复审** | 否 |

### S8：clean image 的线性辐亮度仅以 PNG+log1p 存储——原始线性数据不可恢复

| 属性 | 内容 |
|---|---|
| **ID** | METH-S8 |
| **级别** | 小坑 |
| **类别** | 图像响应 |
| **问题描述** | 当前 PNG 图像是 8-bit 量化后的产物。退化实验（如 noise σ=0.01）需要在线性空间操作，所以做 `expm1 → add noise → log1p`。但如果将来需要不同的 tone-mapping 或更高精度（如 16-bit），必须从 raw EXR 重新生成。PNG 8-bit 的量化损失（1/255 ≈ 0.4%）在 log1p 压缩后对暗区影响更大。 |
| **证据文件** | v0.3 稿件 line 147（"stored with a log1p intensity transform"）、`进度档案_仿真与反演_full.md` line 553（"radiance_max=53.07"） |
| **可能影响范围** | 退化实验的精度（暗区噪声被量化误差污染）；未来如果需要不同预处理 |
| **当前处置方式** | v0.4 同时保留线性 EXR 或 16-bit PNG 作为 raw data；训练用 8-bit PNG+log1p 从 raw data 生成而非独立存储 |
| **应在哪个阶段关闭** | **重跑前** |
| **是否需要 Codex 复审** | 否 |

---

## 三、未知坑（当前没有证据证明有问题，但一旦有问题会影响方法可信度）

### U1：sun-side visibility 的三条实现路径选择

| 属性 | 内容 |
|---|---|
| **ID** | METH-U1 |
| **级别** | 未知坑 |
| **类别** | 遮挡 |
| **问题描述** | 如果论文写"含自遮挡/阴影"，v0.4 必须实现 sun-side visibility。三条可选路径（各有 trade-off）：(a) Blender shadow ray — 需要额外渲染 pass 或 shadow map，增加执行复杂度；(b) Python ray-cast — 复用旧 occlusion.py 逻辑但在 pixel-level 上操作，需确认精度；(c) 限定为 viewer-side visibility only — 不实现 sun shadow，在论文中明确声明边界。三条路径未被评估。 |
| **证据文件** | `04_BlenderOCS方法重建/00_公式与Blender分工说明.md` line 63（"sun-side visibility/self-shadow 待定并必须明确"）、Codex CR-002（"方法冻结前必须决定并实现"） |
| **当前处置方式** | 方法冻结时评估三条路径的代价和收益，做出明确选择并写入方法文件 |
| **应在哪个阶段关闭** | **方法冻结前** |
| **是否需要 Codex 复审** | 是 |

### U2：GGX / Cook-Torrance 的 shadowing-masking (G_Smith) 与几何遮挡的语义重合

| 属性 | 内容 |
|---|---|
| **ID** | METH-U2 |
| **级别** | 未知坑 |
| **类别** | 材料 / 遮挡 |
| **问题描述** | GGX BRDF 的 G_Smith 项是 microfacet shadowing-masking——描述微表面尺度上入射和出射方向被微面遮挡的概率。而项目的"遮挡"是几何尺度的 ray-cast/pixel visibility——描述太阳射线或视线是否被其他部件阻挡。两者叫"遮挡"但在不同尺度。论文中如果不区分，审稿人可能混淆。 |
| **证据文件** | `brdf_models.py`（G_Smith_GGX 实现）、`04_BlenderOCS方法重建/00_公式与Blender分工说明.md` §6（待定 sun-side visibility） |
| **当前处置方式** | 方法文件中明确术语：(a) micro-scale shadowing-masking = G_Smith in BRDF，(b) macro-scale occlusion = geometric ray/depth visibility。论文中用不同术语区分。 |
| **应在哪个阶段关闭** | **方法冻结前** |
| **是否需要 Codex 复审** | 是 — 术语混淆是审稿风险 |

### U3：phase63 single-geometry image + multi-geometry OCS 的公平性

| 属性 | 内容 |
|---|---|
| **ID** | METH-U3 |
| **级别** | 未知坑 |
| **类别** | 数据划分 |
| **问题描述** | 如果 v0.4 继续使用 multi-geometry OCS（5 几何 concat5）与 single-geometry image（phase63），则 OCS 有 5 倍观测信息。这不公平。但另一方面，论文的主线恰恰是"OCS 的多观测几何优势"——如果只用 1 几何 OCS，paper 的卖点会被削弱。需要决定如何平衡公平对比和论文叙事。 |
| **证据文件** | v0.3 Codex 审阅 line 44（12f 用了不同的 OCS 几何配置）、`进度档案_仿真与反演_full.md` line 606-607（CNN image-only phase63 单几何） |
| **当前处置方式** | 方法冻结时决定：主表用 single-geometry OCS（与 image 同几何）做公平对比，补充实验用 multi-geometry OCS 展示多几何优势 |
| **应在哪个阶段关闭** | **方法冻结前** |
| **是否需要 Codex 复审** | 是 |

### U4：训练 split seed 全局一致性

| 属性 | 内容 |
|---|---|
| **ID** | METH-U4 |
| **级别** | 未知坑 |
| **类别** | 数据划分 |
| **问题描述** | 旧实验的 split 是否全部使用相同的随机种子和划分方案？如果不同实验用了不同 split，则数值对比不可靠。Codex CR-007 明确指出"全部改为 unknown/not located"。 |
| **证据文件** | Codex CR-007（"不能把未知 seed 当成已记录信息"）、CLAUDE.md（多处写"旧 seed"但未给具体值） |
| **当前处置方式** | v0.4 使用全局统一 split 文件（固定 seed），所有实验从同一 manifest 读取；source_data.json 记录 seed |
| **应在哪个阶段关闭** | **重跑前** |
| **是否需要 Codex 复审** | 否 |

### U5：非水密 STL 几何在 Blender depth-buffer 下的行为

| 属性 | 内容 |
|---|---|
| **ID** | METH-U5 |
| **级别** | 未知坑 |
| **类别** | 采样 |
| **问题描述** | 真实卫星 STL 的三部件是独立文件。如果部件间有缝隙或非水密区域，Blender depth-buffer 可能产生 depth 不连续或 z-fighting。在旧 face-center ray-cast 中这不是问题（每条射线独立），但在 pixel-level 统一积分中可能导致某些边缘像素的可见性判断不稳定。 |
| **证据文件** | 无直接证据（未测试过） |
| **当前处置方式** | v0.4 代码前做一次 sanity check：检查关键姿态下部件边界的 depth 连续性 |
| **应在哪个阶段关闭** | **代码前** |
| **是否需要 Codex 复审** | 否 |

---

## 四、旧记录文档发现的隐性坑

本节专门汇总从旧进度记录、启动包、CLAUDE.md、项目理解和汇报材料中"曾经发现但没有闭环"的问题。

| # | 记录来源 | 原始问题/原始表述 | 为什么可能是类似 OCS 采样问题的坑 | 现在应如何处置 | 是否进入方法冻结 |
|---|---|---|---|---|---|
| 1 | 进度档案 line 794 | "待评估选项（非当前队列，记录备查）"——区分同部件/跨部件遮挡阈值 | 旧遮挡逻辑的遗留决策从未被正式关闭。v0.4 切换遮挡语义后可能再次出现同类问题 | v0.4 用 depth-buffer 统一遮挡，但需检查非水密 STL 行为 | 否，代码前 |
| 2 | 进度档案 line 387 | "性能不可接受：单姿态 12-15s（vs 面中心 0.03s），400-500× 减速"——subface adaptive 方法失败后性能被放弃 | v0.4 的 Blender-derived OCS 需要每次读取 EXR→计算 OCS。如果 2701 姿态都需完整后处理，总耗时可能成为瓶颈 | v0.4 先跑通全量，再评估是否需要优化（批量读取 EXR、GPU 加速等） | 否 |
| 3 | 进度档案 line 395 | "compute_ocs_from_exr() 函数可用但尚未接入 ocs_core.py 生产扫描循环"——Step 7b 的核心交付物从未接入生产 | 这正是 v0.4 要做的事。但旧代码中这个函数用 LegacyPhong 而不是 GGX，v0.4 必须确认接口兼容 | v0.4 直接写新的 Blender-derived OCS 生成器（不继承旧 compute_ocs_from_exr），确保使用 GGX | 是 |
| 4 | 进度档案 line 818-820 | AOV 在 Cycles "最终着色点"记录，Backfacing 对封闭网格外视图始终为 0，背面 AOV 方案不可行 | v0.4 不能复用旧背面检测方法。pixel-level visibility 完全依赖 depth-buffer | v0.4 方法文件中明确：camera visibility = depth-buffer test；不依赖 Backfacing AOV | 是 |
| 5 | 旧 CLAUDE.md line 82 | "真实三件套 native gap 根因确认为 face-center vs pixel-level 可见性语义差异，已冻结" | "已冻结"在当时意味着不再深入追查。但 v0.4 需要精确知道这个 gap 的定量规模，以设定新 OCS 的审计预期 | v0.4 做新旧 OCS per-part per-attitude 差异审计 | 否，重跑前 |
| 6 | 0603 汇报 line 20-23 | "Blender 负责'看见哪里'，Python 负责'如何反光'" | 这个分工在 v0.3 汇报中被提出但未在反演链路中实施。v0.4 是首次实施 | v0.4 方法冻结时必须完整实现这个分工 | 是 |
| 7 | v0.3 稿件 line 131 | "This visibility model is designed for deterministic facet-level OCS computation. It is not a replacement for real optical data evaluation" | 这是正确的边界表述。但需要确认 v0.4 在改为 pixel-level 后，类似的限制表述是否同步更新 | v0.4 论文中统一更新为 pixel-level visibility 的边界表述 | 否，论文阶段 |
| 8 | `_新对话启动包.md` line 147 | "aerospace2025_joint_estimation 作者字段仍是占位符 {AISwarm-LS Authors}"——bibliography 元数据不完整 | v0.4 的 references.bib 可能仍然包含占位符 | v0.4 启动前审计 references.bib 的完整性 | 否 |
| 9 | 进度档案 line 418 | "关键发现：10° 网格严重欠采样金属镜面峰（max 差 11.4×），5° 网格为论文必需" | 这是 5° 网格被确定为必需品的证据。v0.4 重跑也必须使用 5° 网格（73×37=2701 姿态） | v0.4 沿用 5° 网格 | 否，不属于"坑"，是已确立的决策 |

---

## 五、统计总表

| 级别 | 采样 | 遮挡 | 面积 | 坐标 | 材料 | 图像响应 | 数据划分 | 路径版本 | 写作 | 合计 |
|---|---|---|---|---|---|---|---|---|---|---|
| 大坑 | 2 (H1,H2) | 1 (H3) | 0 | 0 | 0 | 1 (H4) | 0 | 0 | 1 (H5) | **5** |
| 小坑 | 0 | 1 (S1) | 2 (S2,S4) | 1 (S5) | 0 | 1 (S8) | 1 (S6) | 1 (S7) | 1 (S3) | **8** |
| 未知坑 | 1 (U5) | 1 (U1) | 0 | 0 | 1 (U2) | 0 | 2 (U3,U4) | 0 | 0 | **5** |
| 旧记录隐性坑 | — | — | — | — | — | — | — | — | — | **9** |
| **合计** | — | — | — | — | — | — | — | — | — | **27** |

---

## 六、相比第一轮排查（02_全项目坑位排查报告_Claude.md）的新发现

第一轮排查（PIT-A/B/C/D/E/F 系列）聚焦于"旧结果能不能用"和"数据/代码/管理坑"。第二轮排查（本文）深入到"方法、思路、定义、链路口径"层面，新发现了以下第一轮未覆盖的问题：

1. **diffuse 基底可见面积语义差异（H1）**——第一轮仅将问题归因为"采样口径不统一"，本轮的结论是更深层的"可见性语义差异"
2. **薄板双面可见性（H2）**——第一轮未单独列出
3. **Blender 背向面着色伪影（H3）**——第一轮未发现
4. **log1p/tone-mapping 链未冻结（H4）**——第一轮仅在 UNK-004 中提了"待定"，未意识到是整个图像响应链的定义空白
5. **sun-side visibility 路径选择的完整 trade-off 矩阵（U1）**——第一轮仅标记为"待定"，未展开三条路径
6. **GGX G_Smith 与几何遮挡的术语混淆风险（U2）**——第一轮完全未覆盖
7. **clean image 线性数据不可恢复（S8）**——第一轮未覆盖
