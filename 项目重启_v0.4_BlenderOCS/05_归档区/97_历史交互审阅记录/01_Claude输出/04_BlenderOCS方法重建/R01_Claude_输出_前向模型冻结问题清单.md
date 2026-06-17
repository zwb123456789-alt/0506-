# v0.4 前向模型冻结问题清单（Claude 生成）

生成时间：2026-06-08
来源：Codex 复审意见（CR-001～CR-008）+ Codex 方法思路类坑位汇总 + 本轮专项排查（大坑 H1-H5、小坑 S1-S8、未知坑 U1-U5）

---

## 说明

本文件只列"方法冻结前必须回答的问题"。每个问题给出可选方案、推荐方案和理由。

标有 🔴 的是 Codex CR 中明确要求进入方法冻结的项。标有 🟡 的是本轮排查新发现的必须在方法冻结前决定的问题。标有 ⚪ 的是可在代码/重跑阶段决定但建议尽早明确的问题。

---

## 一、采样与可见性

### Q1 🔴 pixel visibility mask 的定义

**问题**：v0.4 的 OCS 积分使用哪些像素？是所有 camera-visible 像素，还是同时施加 sun-side 限制？

**可选方案**：
- A：camera-visible only（depth-buffer 可见的像素全部计入 OCS，不论 sun 方向）
- B：camera-visible + NoL>0（额外要求像素法线满足 n·sun > 0）
- C：camera-visible + sun-ray visibility（对每个 camera-visible 像素发一条 sun 方向 shadow ray，被遮挡的排除）

**推荐方案**：**A 作为默认 OCS（camera-visible only），C 作为 with-sun-shadow OCS 的可选增强**

**为什么**：
- 方案 A 与图像的形成过程完全一致（相机看见什么就积分什么），OCS 直接是"图像线性响应的积分"
- 方案 B 退回到法线判据，已被旧模块 A 证明是可见面积差异的根源之一
- 方案 C 是最物理的，但 sun shadow ray 实现复杂度高。如果当前阶段不实现，需要在论文中明确限定为"viewer-side visibility only, without explicit sun shadow"
- Codex CR-002 要求"若不实现 sun visibility，论文必须明确限定"

**不解决会影响什么**：论文中"含自遮挡/阴影"的声称无法验证；如果后来加上 sun shadow，OCS 数值会变

**需要写入文件**：`04_BlenderOCS方法重建/04_v0.4前向模型冻结规范.md`

---

### Q2 🔴 camera-only visible pixel 的确定方式

**问题**：如何从 Blender EXR 中确定哪些像素是 camera-visible？

**可选方案**：
- A：depth < 1e10 判断（EXR depth 通道中有效值 vs 无穷远）
- B：Combined 通道亮度 > 0 判断
- C：Object Index > 0 判断（IndexOB 通道中背景=0）

**推荐方案**：**C（IndexOB > 0），辅以 A（depth 安全检查）**

**为什么**：
- IndexOB 是最直接的"目标/背景"分割
- 需要确认三部件各自的 IndexOB pass id 与 STL 导入顺序一致
- 进度档案已确认 backfacing 对外视图始终为 0（不需要背面过滤）

**不解决会影响什么**：OCS 像素计数不准，积分值错误

**需要写入文件**：同上

---

### Q3 🔴 边缘像素 fractional coverage 处理

**问题**：图像边缘像素部分覆盖目标、部分为背景。当前分配统一 pixel_area。是否需要 sub-pixel coverage 修正？

**可选方案**：
- A：不做修正，接受为已知舍入误差（预计 <2% 对总 OCS）
- B：用 Combined alpha 或 depth 梯度估算边缘 fractional coverage
- C：提高渲染分辨率（如 512×512），使边缘像素比例更低

**推荐方案**：**A（接受已知舍入误差），同时在方法文件中记录此简化假设**

**为什么**：
- Codex CR-003 明确要求"边缘像素面积处理"写入方法冻结文件
- 对 256×256 分辨率，边缘像素占比约 4×256/65536 ≈ 1.6%，影响很小
- 方案 B 引入额外的不确定性

**不解决会影响什么**：论文方法部分对面积的描述不精确；审稿人可能质疑边缘像素

**需要写入文件**：同上，单独一节"pixel_area 定义与边缘处理"

---

### Q4 🟡 薄板/平面结构的像素级可见性

**问题**：太阳能板是薄板结构。Blender depth-buffer 是否能正确只渲染前向面（不出现背面像素）？是否有 z-fighting 风险？

**可选方案**：
- A：信任 Blender Cycles depth-buffer（已验证封闭网格 backfacing=0）
- B：做一次 sanity check（关键姿态下手动检查太阳能板边缘像素的 depth 连续性）

**推荐方案**：**B（sanity check），成本很低**

**为什么**：
- 旧诊断已确认 backfacing AOV 全零
- 但薄板的另一个面（物理上存在的背面多边形）是否可能在特定角度被 depth-buffer 错误地判定为可见，需要确认

**不解决会影响什么**：如果薄板背面像素进入 OCS 积分，太阳能板贡献会翻倍

**需要写入文件**：sanity check 结果写入方法验证文档

---

## 二、BRDF 与材料

### Q5 🔴 主 BRDF 模型选择

**问题**：v0.4 主线使用 GGX/Cook-Torrance 还是 LegacyPhong？

**可选方案**：
- A：GGX/Cook-Torrance 作为主 BRDF（与旧口径一致，论文级选择）
- B：LegacyPhong 作为主 BRDF（更简单，三端闭合已验证）
- C：两个都跑，主表用 GGX，附录用 LegacyPhong 对比

**推荐方案**：**A（GGX/Cook-Torrance 为主），C（LegacyPhong 仅在 appendix 对照）**

**为什么**：
- Codex CR-004 明确"v0.4 主线采用 GGX/Cook-Torrance"
- GGX 是论文主模型（旧材料参数库已为此设计：金属 metallic=1, roughness=0.20, F0=0.91）
- 旧模块 B 的 EXR geometry pass 不含材质信息，可以同时计算 GGX 和 LegacyPhong OCS（不需要重新渲染）
- `brdf_models.py` 已支持双 BRDF

**不解决会影响什么**：如果选错，所有 OCS 数值、fusion 结果、BRDF 敏感性实验都需重跑

**需要写入文件**：方法冻结规范

---

### Q6 🔴 GGX G_Smith microfacet shadowing-masking 与几何遮挡的术语区分

**问题**：GGX 的 G_Smith 叫"shadowing-masking"，项目的几何遮挡也叫"occlusion/shadowing"。论文中如何避免术语混淆？

**可选方案**：
- A：GGX 侧用 "microfacet shadowing-masking (G)"，几何侧用 "geometric occlusion / sun-shadow"
- B：统一用 "occlusion"，上下文区分（不推荐）
- C：GGX 侧用 "G-term"，几何侧用 "visibility"（不准确——visibility 也有其他含义）

**推荐方案**：**A（明确术语区分）**

**为什么**：
- 审稿人如果混淆两个概念，会质疑方法的物理有效性
- 方案 A 在每个术语出现时都带限定词

**不解决会影响什么**：审稿混淆；方法部分的物理严谨性下降

**需要写入文件**：方法冻结规范中的术语表

---

### Q7 🟡 材料参数不确定性的传播

**问题**：论文中是否要写"材料参数为 nominal synthetic values"？是否需要做材料参数敏感性分析？

**可选方案**：
- A：保留旧实验中的 BRDF sensitivity（金属 roughness ±20%）作为补充材料
- B：v0.4 重新做材料敏感性分析（因为 OCS 源变了）
- C：不在 v0.4 主稿中做材料敏感性分析，仅声明参数为 nominal

**推荐方案**：**B（重新做），但可以在主实验完成后作为 sensitivity analysis 批量跑**

**为什么**：
- 旧 BRDF sensitivity 用的是旧 OCS，数值不能直接引用
- 但材料参数敏感性分析的逻辑（±20% roughness 等）可以复用
- 如果时间不够，至少在主稿中声明 "nominal synthetic material parameters; a systematic sensitivity analysis is left for future work"

**不解决会影响什么**：审稿人可能质疑材料参数是否 tuned for performance

**需要写入文件**：不必须进入方法冻结规范，但应在重跑清单中标记

---

## 三、OCS 积分公式与面积

### Q8 🔴 连续公式、像素离散公式、NoV 抵消条件

**问题**：OCS 积分的数学定义是什么？从连续积分到像素离散求和的每一步推导和假设是什么？

**要求**（Codex CR-003）：

1. 连续形式：
   ```
   OCS = ∫_{visible_surface} f_r(ω_i, ω_o, N(x)) · cos(θ_i) · cos(θ_o) dA
   ```

2. 像素离散形式：
   - 正交投影下：`dA = dA_projected / cos(θ_o)`
   - `OCS ≈ Σ pixel_area_projected · f_r · cos(θ_i) / cos(θ_o) · cos(θ_o) = Σ pixel_area_projected · f_r · cos(θ_i)`
   - NoV 抵消后：`OCS = Σ pixel_area_projected · f_r · NoL`

3. NoV 抵消的成立条件：
   - 正交投影（pixel_area_projected 为常数）
   - `NoV > 0`（NoV ≤ 0 的像素 OCS 贡献 = 0）
   - 像素全部覆盖目标表面（无 fractional coverage 假设）

4. NoV ≈ 0 的边界处理：
   - `NoV < eps` 时显式设贡献为 0（避免除零）

5. 边缘像素处理：
   - 如前 Q3 所述，接受已知舍入误差

**推荐方案**：以上 5 条全部写入方法冻结规范，公式用 LaTeX

**不解决会影响什么**：这是 OCS 方法的数学根基。如果不写清楚，整个论文的物理一致性无法验证

**需要写入文件**：方法冻结规范中的独立章节"OCS Integral Definition"

---

### Q9 🔴 pixel_area 的物理含义

**问题**：`pixel_area_projected` 是投影像素面积还是表面像素面积？单位是什么？

**可选方案**：
- A：`pixel_area_projected` = (ortho_scale / resolution)²，单位 m²，是正交投影下一个像素对应的目标平面面积（常数）
- B：从 Blender 输出逐像素的 projected area（如果存在此 pass）

**推荐方案**：**A（常数 pixel_area，正交投影）**

**为什么**：
- 代码中 `pixel_area_m2 = (ortho_scale / resolution)²` 是常数
- `brdf_postprocess_summary.json` 中 pixel_area_m2 = 0.00016015（= 3.24²/256²）
- 如果 B（逐像素面积）需要额外的 Blender pass 或复杂计算

**不解决会影响什么**：面积单位错误会导致 OCS 绝对值差几个数量级

**需要写入文件**：方法冻结规范中"pixel_area"一节

---

### Q10 ⚪ 分辨率对 OCS 积分精度的影响

**问题**：v0.4 使用多少分辨率？是否需要在论文中做 resolution ablation？

**可选方案**：
- A：256×256（与旧模块 B 一致），不做 ablation
- B：256×256 + 补充材料中 128 vs 256 vs 512 的 OCS 差异分析

**推荐方案**：**B（256×256 为主线，128 vs 256 的 ablation 作为补充材料）**

**为什么**：
- 旧记录中"res=128 vs 256 OCS 差 <1%"，但这不是正式的 ablation
- 做一个简单的 3 分辨率 OCS 差异扫描，在补充材料中放表即可

**不解决会影响什么**：审稿人可能问"为什么选 256，是否够"

**需要写入文件**：不必须进入方法冻结，标记为重跑清单

---

## 四、图像响应链

### Q11 🔴 线性辐亮度 → log1p → 8-bit PNG 的完整定义

**问题**：图像从物理辐亮度到训练输入的每一步的公式和动机是什么？

**要求**（Codex CR 的综合要求 + H4 排查发现）：

1. 线性辐亮度 I_linear（f_r · NoL · pixel_response，单位 arbitrary but proportional to radiance）
2. log1p 变换：`I_log = log1p(I_linear / scale)` — 需要确定 scale 参数
3. 8-bit 量化：`PNG = clip(I_log / max_val * 255, 0, 255)` — 需要确定 max_val
4. 训练时：`input = PNG / 255 * max_val`（逆转量化后输入网络）还是直接 `PNG/255`？
5. 退化实验：噪声加在 `I_linear`（expm1 空间）还是 `I_log`（log1p 空间）？
6. log1p 的动机：压缩动态范围、保持亮度排序（单调性）、但不保持亮度间距（非线性）

**推荐方案**：以上 6 条全部写入方法冻结规范中的"图像预处理"一节

**为什么**：
- H4 排查发现这个链从未被正式文档化
- log1p 是基于经验选择（12.13° vs 15.99°），论文中需要提供 justification

**不解决会影响什么**：image-only 结果的不可复现；退化实验的作用域不明确

**需要写入文件**：方法冻结规范中"图像预处理与训练输入"一节

---

### Q12 ⚪ 原始线性辐亮度数据的存储

**问题**：是否保留原始线性辐亮度数据（非 log1p、非 8-bit 量化）？如果将来需要改变预处理，是否需要从头重新渲染？

**可选方案**：
- A：保留 EXR（线性浮点，lossless）作为 canonical raw data；训练用 PNG+log1p 从 EXR 生成
- B：只保留 PNG+log1p，如果需要改变预处理就重新跑 brdf_postprocess

**推荐方案**：**A（保留 EXR 作为 raw data）**

**为什么**：
- EXR geometry pass 可反复用于不同 BRDF/预处理参数，不需重新渲染（进度档案 line 312 已确认材质独立性）
- EXR 文件体量大（2701×~20MB ≈ 54GB），但硬盘成本可接受
- 如果选 B，改变预处理就要重新生成全部图像（虽不需要重渲染，但需要重跑后处理）

**不解决会影响什么**：数据完整性

**需要写入文件**：不必须进入方法冻结，标记为 v0.4 数据管理规范

---

## 五、遮挡与阴影

### Q13 🔴 sun-side visibility / self-shadow 的实现或边界限定

**问题**：论文是否写"含自遮挡/阴影"？如果写，如何实现和验证？

**可选方案**：
- A：实现 Blender shadow ray（额外渲染 sun-view EXR 或使用 shadow map）
- B：实现 Python ray-cast（复用旧 occlusion.py 的 trimesh+Embree，但在 pixel-level 操作）
- C：不实现 sun shadow，论文明确限定为 "viewer-side (camera) visibility only, without explicit sun-side self-shadowing treatment"

**推荐方案**：**C（论文限定为 viewer-side visibility），但保留 A/B 作为未来工作**

**为什么**：
- sun shadow 实现复杂度高（尤其方案 A 需要修改 Blender 渲染流程）
- 论文的核心信息（OCS vs image vs fusion）不需要 sun shadow 也能成立
- 但必须诚实声明："本文的遮挡只考虑视线方向可见性；太阳方向的自身阴影/遮挡未纳入前向模型，是未来工作"
- 如果不实现 sun shadow，论文中的关键词从 "self-occlusion/shadowing" 改为 "camera-viewer-side visibility"

**不解决会影响什么**：如果承诺了但没有实现，构成方法缺陷

**需要写入文件**：方法冻结规范中"遮挡与可见性"一节

---

### Q14 🟡 Blender Cycles 背向面着色伪影的过滤

**问题**：在 NoL ≤ 0 或 NoV ≤ 0 的姿态，Blender 的 shading normal 会自动翻转，产生非零亮度残差。v0.4 后处理中如何处理？

**可选方案**：
- A：在 BRDF 后处理中显式检查 `NoL ≤ 0` 或 `NoV ≤ 0` 的像素，设 OCS 贡献 = 0
- B：信任 Blender，不额外过滤（有已知残差）

**推荐方案**：**A（显式设 0）**

**为什么**：
- 三端闭合验证中已确认"Blender Cycles 背向面着色是已知噪声源"（进度档案 line 371）
- 实现成本极低（一行 numpy 条件赋值）
- 不这样做会在某些边缘姿态系统性地高估 OCS

**不解决会影响什么**：边缘姿态 OCS 被高估（已知但可控的误差）

**需要写入文件**：方法冻结规范中"边界条件处理"一节

---

## 六、坐标与姿态

### Q15 ⚪ 坐标系的完全一致性审计

**问题**：Blender 和 Python 端的 yaw/pitch/roll、法线方向、sun/det 向量是否完全一致？

**需要确认的内容**：
1. 姿态矩阵 R = Rz(yaw) @ Ry(pitch) @ Rx(roll) — Z-Y-X 内旋（进度档案确认）
2. 法线坐标系：世界坐标，Blender EXR normal pass 输出世界坐标法线（进度档案 line 186 确认）
3. sun/det 向量在 Python 端使用前归一化为单位向量（待审计确认）
4. Blender 端相机位置 = det_vector × r_max × ortho_scale_factor（待审计确认）
5. Yaw/Pitch 的正方向定义（yaw CCW 从 +Z 看，pitch CCW 从 +Y 看？— 需要在方法冻结文件中用图定义）

**推荐方案**：做一次 3 姿态 sanity check（0°/0°、90°/-45°、150°/-80°），对比 Python 端和 Blender 端在相同姿态下的 normal/sun/det 向量数值

**不解决会影响什么**：坐标系不一致会导致 OCS 和图像不是同一姿态，所有反演结果无意义

**需要写入文件**：方法冻结规范中"坐标系定义"一节

---

## 七、方法与数据管理

### Q16 🔴 source_data.json 和 manifest 的字段规范

**问题**：v0.4 的每个实验产物需要记录哪些元数据以确保完全可复现？

**要求**（Codex CR-004/CR-007 + Codex 方法汇总）：

每个 run 的 `source_data.json` 至少包含：

```json
{
  "ocs_source": "v0.4 Blender-derived OCS manifest path",
  "ocs_manifest": "multi_geom_blender_ocs_yaw73_pitch37.json",
  "image_source": "v0.4 image run path",
  "brdf_model": "ggx_cook_torrance",
  "feature_mode": "per_part_log",
  "split_seed": 42,
  "split_method": "coarse_to_fine 10deg_train_5deg_test",
  "train_val_ratio": "80/20 from train",
  "yaw_grid": [0, 5, 10, ..., 360],
  "pitch_grid": [-90, -85, ..., 90],
  "geometries": ["phase24", "phase63", "phase90", "phase120", "free"],
  "image_geometry": "phase63",
  "resolution": 256,
  "ortho_scale": 3.24,
  "log1p_scale": <value>,
  "run_id": "<timestamp>",
  "v0.4_method_version": "1.0"
}
```

**推荐方案**：以上 schema 写入方法冻结规范；每个脚本自动生成 `source_data.json`

**不解决会影响什么**：v0.4 可能重蹈旧项目 metadata 缺失的覆辙

**需要写入文件**：方法冻结规范 + 单独的 `source_data.json` schema 文件

---

### Q17 ⚪ 禁止 latest-run 自动发现

**问题**：v0.4 所有脚本是否使用显式 manifest 路径而非 `max(glob)` 之类自动发现？

**要求**（Codex CR-004）：**全部使用显式路径**

**推荐方案**：每个脚本接受 `--manifest` / `--ocs-manifest` / `--image-dir` 参数；不设默认值；不自动发现

**不解决会影响什么**：新旧结果混读

**需要写入文件**：方法冻结规范中的"数据管理"一节

---

## 八、方法冻结前必须解决的问题（优先级排序）

| 优先级 | 问题编号 | 问题 | 类别 |
|---|---|---|---|
| **1** | Q8 + Q9 | OCS 积分连续/离散公式 + pixel_area 定义 | 核心数学根基 |
| **2** | Q1 + Q2 | pixel visibility mask 的定义 + 确定方式 | 核心物理定义 |
| **3** | Q13 | sun-side visibility 的实现或边界限定 | 论文的物理可信度 |
| **4** | Q5 | BRDF 主模型选择（GGX vs LegacyPhong） | 后续所有实验的基线 |
| **5** | Q11 | 图像响应链（linear→log1p→PNG→train） | image-only 的物理含义 |
| **6** | Q6 | 术语区分（G_Smith vs geometric occlusion） | 论文物理严谨性 |
| **7** | Q3 + Q4 | 边缘像素 + 薄板可见性 | OCS 积分的数值边界 |
| **8** | Q15 | 坐标系统一性审计 | 防止最基本的姿态错误 |
| **9** | Q14 | 背向面着色过滤 | OCS 数值清理 |
| **10** | Q16 + Q17 | source_data.json schema + 禁止 latest-run | 可复现性 |

---

## 九、不进入方法冻结但需在后续阶段解决的问题

| 阶段 | 问题编号 | 问题 |
|---|---|---|
| 代码前 | Q4 | 薄板 depth-buffer sanity check |
| 代码前 | Q15 | 3 姿态坐标系 sanity check |
| 重跑前 | Q10 | 分辨率 ablation |
| 重跑前 | Q12 | 原始线性辐亮度数据存储方案 |
| 重跑前 | U4 | split seed 全局一致性 |
| 重跑前 | U5 | 非水密 STL depth 行为检查 |
| 论文阶段 | S3 | 汇报口径与数据流一致性 |
| 论文阶段 | S6 | 多几何 OCS vs 单几何 image 公平性 discussion |
| 论文阶段 | Q7 | 材料参数敏感性分析（可标记为 future work） |
