# 02 第一批最小验证任务清单

生成时间：2026-06-08
状态更新：2026-06-18
依据：方法冻结规范 `13`/`14` + 代码资产盘点 `01`

当前主线前置说明：

```text
项目/论文主线：24_v0.4项目论文主线最终冻结稿_OCS口径形态与mismatch账面对齐版.md
原因备案：25_v0.4主线冻结原因备案_为什么采用24号.md
当前状态：四路线综合审阅与最终路线裁决 R01 已通过；代码实施前指标规范已冻结；当前回到 Phase 0 门控验证
```

本文件是路线一代码阶段的第一批门控验证清单。指标规范已经冻结，当前可按本文件执行 depth round-trip、20 姿态 shadow validation、V_sun_macro 对图像影响检查等 Phase 0 gate；任一硬 gate 失败前不得启动全量生成或训练。

---

## 一、验证任务总览

第一批最小验证任务是进入全量生成（2664×5 EXR）前的**门控检查**。目的是用最少的计算成本验证：

1. Blender depth 定义与反投影公式正确
2. sun shadow reprojection 矩阵方向与 depth 比较正确
3. V_sun_macro 对 OCS/image 的影响符合统一前向模型
4. `depth_epsilon_m_final` 可校准到不误判不漏判

**禁止操作**：在任一 P0 验证失败前启动全量渲染或训练模型。

---

## 二、硬 gate 验证任务（必须通过才能进入全量生成）

### 2.1 验证 1：depth round-trip sanity check

**目的**：确认 Blender depth pass 的符号、单位、相机 local z 方向映射，避免 sun shadow reprojection 系统性错位。

**实现模块**：
- `06_v0.4_code/04_sun_shadow/depth_round_trip_check.py`
- `06_v0.4_code/02_blender/render_camera_geometry.py`（提供 camera-view EXR）

**输入**：
- 3 个已知世界点（手动选取，覆盖目标中心/边缘/远近）
- camera-view EXR（含 depth + Position）
- camera_matrix_world

**检查内容**（见 `13` §7.4.2）：

```text
检查 1（camera-view round-trip）：
  camera pixel (u,v) + depth
    → P_camera_local（用规范公式映射）
    → P_world = camera_matrix_world @ P_camera_local
    → P_camera_local' = inverse(camera_matrix_world) @ P_world
    → 重投影 pixel (u',v') 与 depth'
  断言：(u',v') ≈ (u,v)（误差 < 1 pixel）且 depth' ≈ 原 EXR depth（相对误差 < 0.1%）

检查 2（sun-view round-trip）：
  已知 sun-view 世界点 P_world（从 camera-view 已知点取）
    → P_sun_local = inverse(sun_camera_matrix_world) @ P_world
    → 重投影 (u_sun, v_sun) 与 sun_depth_reproj
    → 与 sun-view EXR 在 (u_sun, v_sun) 处的 depth 比较
  断言：sun_depth_reproj 与 EXR depth 的符号、量级一致（相对误差 < 1%）
```

**通过标准**：
- 3 个已知点的 camera/sun 双向 round-trip 全部通过
- 确定 depth→camera_local z 的映射常量（例如 `z_local = -depth` 或 `z_local = depth`，取决于 Blender 实际）

**失败处理**：
- 若 round-trip 误差系统性偏大（> 1%），检查 Blender depth 编码、相机 local 坐标系约定
- 若 camera/sun 矩阵方向不一致，回到 `13` §7.3.1 检查是否误用 `matrix_world` 代替 `inverse(matrix_world)`

**产物**：
- `v0.4_results/00_validation/depth_round_trip_report.txt`（记录 3 点误差、映射常量）

---

### 2.2 验证 2：20 姿态 sun shadow validation + depth_epsilon_m 校准

**目的**：验证 sun shadow reprojection 在代表姿态下物理合理，校准 `depth_epsilon_m_final`。

**实现模块**：
- `06_v0.4_code/10_validation/validate_20_attitudes.py`
- `06_v0.4_code/04_sun_shadow/sun_shadow_reprojection.py`

**输入**：
- 20 个代表姿态（手动选取，见下表）
- 每姿态的 camera-view EXR + Position + sun-view depth EXR
- camera/sun 矩阵
- `depth_epsilon_m_initial = 1e-3` m

**20 姿态选取策略**（见 `13` §12.6）：

在 **phase63 sun/det 几何配置**（相位角 63°）下，选取以下 20 个 `(yaw, pitch)` 姿态：

| 类别 | 姿态 (yaw, pitch) | 数量 | 预期特征 |
|---|---|---|---|
| 低遮挡（部件分离）| (0°, 0°), (180°, 0°), (0°, -30°), (180°, 30°) | 4 | V_sun_macro 多数为 1，遮挡少 |
| 高遮挡（部件互相遮蔽）| (90°, -60°), (90°, 75°), (270°, -80°), (270°, 60°), (45°, -70°) | 5 | 太阳能板/引伸板互相遮挡，V_sun_macro 分区明显 |
| 边缘姿态（\|pitch\| > 75°）| (45°, 85°), (135°, -85°), (270°, 88°), (0°, -88°) | 4 | 极端俯仰，测试边缘数值稳定性 |
| 典型训练姿态 | (45°, -45°), (225°, 45°) | 2 | 中等遮挡，覆盖训练集常见状态 |
| 中等遮挡 | (135°, 30°), (225°, -15°), (315°, 60°), (60°, -50°), (300°, 20°) | 5 | 覆盖中间状态 |

**检查内容**：

1. **Sun-view EXR 渲染成功**：depth 数据完整，无 NaN/inf
2. **World position 重建正确**：与已知几何比对（选 3 个特征点）
3. **Camera-view → sun-view reprojection 坐标正确**：
   - 矩阵方向按 `13` §7.3.1（`world_to_sun_camera = inverse(sun_camera_matrix_world)`）
   - 重投影像素 (u_sun, v_sun) 落在 [0, resolution-1] 内
4. **Depth comparison 产生的 V_sun_macro_mask 物理合理**：
   - 部件轮廓清晰（非模糊边缘）
   - 遮挡区域与几何直觉一致（太阳能板遮挡引伸板时，引伸板对应像素 V_sun_macro=0）
   - 无大面积误判（如整片部件全 0 或全 1 且不符合几何）
5. **与 `camera_visible_nol` 的 OCS 差异可解释**（启发式诊断）：
   - 计算同一姿态的 OCS_level1（V_sun_macro≡1）和 OCS_level2（V_sun_macro 来自 shadow mask）
   - `OCS_level2 ≤ OCS_level1`（**硬约束**：遮挡只能减少 OCS，不能增加）
   - 差异量 `(OCS_level1 - OCS_level2) / OCS_level1`：高遮挡姿态通常 > 5%，低遮挡姿态通常 < 2%（**启发式阈值**，用于辅助诊断 mask 合理性；若不满足需人工复核几何直觉，不自动判失败）
6. **`depth_epsilon_m_final` 校准**：
   - 扫描候选容差：`[5e-4, 1e-3, 2e-3, 5e-3]` m
   - 每个容差生成一版 V_sun_macro_mask，检查：
     - 误判率（应遮挡但 V_sun_macro=1 的像素）
     - 漏判率（不应遮挡但 V_sun_macro=0 的像素）
   - 选出误判率和漏判率均 < 1% 的最小容差，记录为 `depth_epsilon_m_final`
   - 若无法满足，记录失败原因，考虑降级

**通过标准**：
- 20 姿态的 V_sun_macro_mask 全部物理合理
- 与 `camera_visible_nol` 的 OCS 差异满足硬约束（`OCS_level2 ≤ OCS_level1`）
- `depth_epsilon_m_final` 校准成功（误判/漏判率均 < 1%）

**失败处理**（CR-CODE-001 修正）：
- 若 V_sun_macro_mask 系统性错位（整体偏移或镜像）：检查矩阵方向、depth 符号
- 若轮廓模糊或部件边界误判：检查 sun_depth 采样方式（必须最近邻，不能双线性）
- 若 depth_epsilon 无法校准（误判/漏判 trade-off 无解）：**整体降级为 Level 1**（`camera_visible_nol`），manifest 记录降级原因
- **任一姿态验证失败时**：**不允许以 Level 2 进入全量生成**；必须修正实现并重测全部 20 姿态，或**整体降级为 Level 1**
- 失败姿态可记录在 validation report 中作为诊断证据，但**不能作为 manifest 中排除后继续通过的依据**

**产物**：
- `v0.4_results/00_validation/20_attitudes_shadow_validation_report.md`（含每姿态 V_sun_macro 可视化 PNG、OCS 差异表、depth_epsilon 校准曲线）
- `depth_epsilon_m_final` 确定值（写入后续 manifest）

---

## 三、辅助诊断验证任务（建议完成，辅助主 gate）

### 3.1 验证 3：3 姿态 camera geometry pass 检查

**目的**：验证 Normal/Depth/IndexOB pass 物理合理。

**实现模块**：`06_v0.4_code/02_blender/render_camera_geometry.py`

**输入**：3 个姿态（如 (0°,0°), (90°,-45°), (150°,-80°)）

**检查内容**（见 `13` §12.1）：
- Normal 方向与几何直觉一致（特征面法线方向）
- Depth 分布连续（薄板边缘无突变）
- IndexOB 分区正确（1=jinshuzhuti, 2=taiyangnengban, 3=yinshenban）
- 可见像素数合理（与姿态对应）

**通过标准**：3 姿态 Normal/Depth/IndexOB 全部合理。

**产物**：`v0.4_results/00_validation/3_attitudes_geometry_check.png`（可视化）

---

### 3.2 验证 4：3 姿态 Position/WorldCoord 检查

**目的**：验证 Position pass 或 depth+matrix 重建的世界坐标正确。

**实现模块**：`06_v0.4_code/02_blender/render_camera_geometry.py`（Position AOV 或重建）

**输入**：同验证 3 的 3 姿态

**检查内容**：
- 若 Blender 支持 Position AOV：读取 `_position.exr`，与 depth 反投影结果比对
- 若不支持：用 depth + camera_matrix 重建 P_world，与已知几何特征点比对
- 世界坐标范围合理（目标包围球半径量级）

**通过标准**：P_world 与已知几何比对误差 < 1%。

**产物**：`v0.4_results/00_validation/3_attitudes_position_check.txt`

---

### 3.3 验证 5：3 姿态 sun-view depth 检查

**目的**：验证 sun-view depth pass 渲染成功、深度合理。

**实现模块**：`06_v0.4_code/02_blender/render_sun_depth.py`

**输入**：同验证 3 的 3 姿态 + 对应 sun_camera_matrix_world

**检查内容**：
- sun_depth EXR 完整（无 NaN/空白区域）
- 深度范围合理（与目标尺度一致）
- 部件轮廓清晰

**通过标准**：3 姿态 sun_depth 全部合理。

**产物**：`v0.4_results/00_validation/3_attitudes_sun_depth_check.png`

---

### 3.4 验证 6：5 姿态 V_sun_macro 对图像影响检查

**目的**：验证图像线性响应加入 `V_sun_macro` 后，sun-shadowed 像素正确归零，且 EXR/PNG 同步。

**实现模块**：`06_v0.4_code/10_validation/validate_v_sun_macro_on_image.py`

**输入**：
- 5 个姿态（选 1 个低遮挡 + 3 个高遮挡 + 1 个典型训练姿态）
- 每姿态生成两版图像：
  - `I_linear_with_V` = f_r·NoL·V_sun_macro
  - `I_linear_without_V` = f_r·NoL（V_sun_macro≡1）

**检查内容**（见 `13` §12.7）：
1. sun-shadowed 像素（V_sun_macro=0）在 `I_linear_with_V` 中亮度归零
2. `I_linear_without_V` 中该像素亮度 > 0（证明不是 NoL≤0 导致）
3. 两版图像的 log1p PNG 同步（with_V 的 shadowed 区域为黑）

**通过标准**：5 姿态全部符合预期。

**产物**：`v0.4_results/00_validation/5_attitudes_v_sun_macro_on_image_comparison.png`（左右对比）

---

## 四、可选验证任务（可延后到全量生成后）

### 4.1 验证 7：per-part OCS 比例审计

**目的**：新旧 OCS per-part 比例差异审计（见 `13` §12.4）。

**输入**：新 v0.4 OCS manifest + 旧 OCS CSV（如有）

**检查内容**：per-part OCS 比例是否合理（jinshuzhuti/taiyangnengban/yinshenban 比例不出现反常）。

**时机**：全量生成后。

---

### 4.2 验证 8：log1p α quick ablation

**目的**：确定 log1p α 最优值（见 `13` §12.5）。

**输入**：v0.4 clean corpus I_linear 全局统计

**检查内容**：α ∈ {5, 10, 20} + raw 的动态范围与训练效果。

**时机**：全量生成后、训练前。

---

### 4.3 验证 9：薄板 depth-buffer 审计

**目的**：检查太阳能板边缘 depth 连续性（见 `13` §12.2）。

**输入**：yaw=90°, pitch=-40° 姿态 EXR

**时机**：全量生成后。

---

## 五、验证任务执行顺序与依赖

```text
验证 1（depth round-trip）
  ↓ 必须通过
验证 3（camera geometry pass）+ 验证 4（Position）+ 验证 5（sun depth）
  ↓ 建议通过
验证 2（20 姿态 shadow validation）
  ↓ 必须通过，depth_epsilon_m_final 确定
验证 6（V_sun_macro 对图像影响）
  ↓ 建议通过
【gate 通过，进入全量生成】
  ↓
验证 7/8/9（可选，全量生成后）
```

---

## 六、失败场景与降级预案（CR-CODE-001 已修正）

| 失败场景 | 降级预案 | manifest 记录 |
|---|---|---|
| depth round-trip 无法通过（误差 > 1%）| 不进入全量生成，回到 Blender 配置检查 | — |
| sun shadow reprojection 系统性错位 | 检查矩阵方向、depth 符号；若无法修正，**整体降级为 Level 1** | `sun_visibility = "camera_visible_nol"`, `v_sun_macro_mode = "identity"` |
| depth_epsilon 无法校准（误判/漏判 trade-off 无解）| **整体降级为 Level 1** | 同上 + `shadow_mapping_method = "none"` |
| **20 姿态中任一姿态失败** | **整体降级为 Level 1**，或修正实现并重测全部 20 姿态 | 同上；失败姿态记录在 validation report，不作为排除后继续通过的依据 |
| Position AOV 不可用 | 改用 depth+matrix 重建 | `position_exr_path = null` |

**降级时必须做**：
1. 在 `v0.4_results/00_validation/` 记录降级原因与失败日志
2. 更新 manifest：`sun_visibility = "camera_visible_nol"`, `v_sun_macro_mode = "identity"`, `shadow_mapping_method = "none"`
3. 更新论文写作边界：显式声明未实现 sun-side self-shadow

---

## 七、验证产物清单

所有验证产物写入：

```
v0.4_results/00_validation/
├── phase0_smoke_test_report.md
├── resource_estimate.json
├── failure_diagnosis_template.md
├── depth_round_trip_report.txt
├── 20_attitudes_shadow_validation_report.md
├── 3_attitudes_geometry_check.png
├── 3_attitudes_position_check.txt
├── 3_attitudes_sun_depth_check.png
├── 5_attitudes_v_sun_macro_on_image_comparison.png
└── validation_summary.json  # 汇总：哪些通过、depth_epsilon_m_final、是否降级
```

`validation_summary.json` schema：

```json
{
  "validation_date": "2026-06-XX",
  "gate_passed": true,
  "depth_round_trip": {"status": "passed", "details": "..."},
  "shadow_validation_20": {"status": "passed", "depth_epsilon_m_final": 1.5e-3},
  "camera_geometry_3": {"status": "passed"},
  "position_3": {"status": "passed", "method": "Position AOV"},
  "sun_depth_3": {"status": "passed"},
  "v_sun_macro_on_image_5": {"status": "passed"},
  "resource_estimate": {
    "single_attitude_seconds": null,
    "single_attitude_storage_mb": null,
    "single_geom_estimated_hours": null,
    "multi_geom_estimated_hours": null
  },
  "degradation_decision": {
    "final_sun_visibility": "camera_visible_nol_plus_sun_shadow_pass",
    "v_sun_macro_mode": "shadow_mask",
    "degraded_from_plan": false
  }
}
```

---

## 八、gate 通过标准总结（CR-CODE-003 已修正）

**必须全部满足才能进入全量生成**：

1. ✅ 验证 1（depth round-trip）通过
2. ✅ 验证 2（20 姿态 shadow validation）通过，`depth_epsilon_m_final` 确定
3. ✅ 验证 3/4/5（camera geometry / Position / sun depth）全部通过（辅助诊断，但强烈建议在 20 姿态验证前完成）
4. ✅ 验证 6（V_sun_macro 对图像影响）通过（辅助诊断，但强烈建议）
5. ✅ BRDF/OCS/image 后处理 3 姿态试跑成功（不在本清单，见 `01` §四.5）
6. ✅ OCS/image manifest builder 实现完成（不在本清单，见 `01` §四.6）

**任一硬 gate 项失败**：不进入全量生成，诊断根因、修正、重测或降级。

失败诊断记录必须写入 `v0.4_results/00_validation/`，建议使用 `failure_diagnosis_template.md`。诊断记录至少包含：

- 失败任务和失败姿态。
- 使用的 camera/sun EXR、Position 或 depth 重建路径。
- camera/sun 矩阵方向检查结果。
- depth 符号、单位、local-z 映射检查结果。
- V_sun_macro 可视化与异常区域说明。
- 修正动作和重测结论。

