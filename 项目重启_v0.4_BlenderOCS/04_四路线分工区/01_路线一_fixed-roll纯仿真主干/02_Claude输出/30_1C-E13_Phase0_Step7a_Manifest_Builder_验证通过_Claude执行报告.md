# 30_1C-E13_Phase0_Step7a_Manifest_Builder_验证通过_Claude执行报告

最后更新：2026-06-24  
执行端：Claude  
任务：1C-E13 / Phase 0 Step 7a —— Manifest Builder + Consistency Checker 实现与验证

---

## 1. 执行总结

```text
任务状态：COMPLETE
一致性检查：PASS（9/9 检查项全部通过）
输出产物：3 个工具脚本 + 2 个 manifest JSON + 1 个一致性报告
边界遵守：未进入全量生成、未训练模型、未改写论文、未修改冻结文件
```

**关键成果**：
- 实现了 OCS manifest builder、Image manifest builder、Consistency checker 三个工具脚本
- 使用 Step 6 的 5 姿态 small-run 产物成功生成两个 manifest
- 一致性检查全部通过（geometry/BRDF/visibility/sun_visibility/shadow_mapping_method/v_sun_macro_mode/I_scale/record_id/per-record 九项）
- 验证了 14 号规范的 manifest 字段 schema 和一致性规则可执行

---

## 2. 任务依据

### 2.1 上游审阅

**R28 Codex 审阅**（`04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R28_Codex_审阅_1C-E12全量前规划通过并规划Step7a.md`）：
- E12 全量前规划通过
- 放行 Step 7a：manifest builder + consistency checker 在 Step 6 的 5 姿态上实现并验证
- 明确不得进入全量 2664 姿态生成

### 2.2 规范依据

- **14 号** §3.1（OCS manifest schema）、§3.2（Image manifest schema）、§8.1（一致性规则）
- **13 号** §6.2（OCS 积分公式）、§8.2（图像响应链）
- **R28** §5（给 Claude 的下一步短提示词）

---

## 3. 实现内容

### 3.1 工具脚本实现

**已创建三个工具脚本**：

| 脚本 | 路径 | 功能 |
|---|---|---|
| OCS manifest builder | `06_v0.4_code/06_manifest/build_ocs_manifest_v0_4.py` | 从 Step 6 产物构建 OCS manifest |
| Image manifest builder | `06_v0.4_code/06_manifest/build_image_manifest_v0_4.py` | 从 Step 6 产物构建 Image manifest |
| Consistency checker | `06_v0.4_code/06_manifest/check_manifest_consistency_v0_4.py` | 检查两个 manifest 的一致性 |

### 3.2 OCS Manifest Builder (`build_ocs_manifest_v0_4.py`)

**输入**：
- Step 6 summary JSON（r_max, ortho_scale_m, pixel_area_m2, depth_epsilon_m_final）
- Step 6 的 5 个 OCS JSON（per-part OCS + 像素统计）
- shadow_passes 目录（camera/sun EXR 路径）

**输出**：
- `ocs_manifest_v0_4_step6trial.json`（5 条 records）

**实现要点**：
- 从 Step 6 summary 提取全局参数（r_max=1.473m, ortho_scale_m=3.240m, pixel_area_m2=1.602e-4, depth_epsilon_m=0.795m）
- 版本字段：`geometry_version`, `brdf_version`, `visibility_version`, `ocs_integration_version`
- 每个 record 包含：record_id, yaw/pitch/geom_id, sun_dir/det_dir, ocs_total, ocs_per_part, 四类像素统计, EXR 路径
- `sun_visibility = "camera_visible_nol_plus_sun_shadow_pass"`
- `shadow_mapping_method = "sun_view_depth_reprojection"`
- `camera_matrix_world` 和 `sun_camera_matrix_world` 当前为 null（Phase 0 暂未从 Blender 脚本记录，Step 7b 补充）

### 3.3 Image Manifest Builder (`build_image_manifest_v0_4.py`)

**输入**：
- Step 6 summary JSON（i_scale_smallrun=0.5445, log1p_alpha=10.0）
- Step 6 的 5 个 linear EXR + log1p PNG

**输出**：
- `image_manifest_v0_4_step6trial.json`（5 条 records）

**实现要点**：
- 版本字段：`geometry_version`, `brdf_version`, `visibility_version`, `image_preprocess_version`
- 与 OCS manifest 使用相同的 `sun_visibility` 和 `shadow_mapping_method`
- `preprocessing.v_sun_macro_mode = "shadow_mask"`（对应 Level 2 sun shadow pass）
- `preprocessing.v_sun_macro_applied_to_image = true`
- `preprocessing.I_scale = 0.5444863931551639`（与 Step 6 summary 一致）
- 每个 record 包含：record_id, yaw/pitch/geom_id, png_path, exr_linear_path, is_clean=true, I_scale_record

### 3.4 Consistency Checker (`check_manifest_consistency_v0_4.py`)

**检查项**（9 项，全部 PASS）：

| # | 检查项 | 状态 | OCS 值 | Image 值 |
|---|---|---|---|---|
| 1 | `geometry_version_match` | **PASS** | `v0.4_phase0_step6_smallrun` | `v0.4_phase0_step6_smallrun` |
| 2 | `brdf_version_match` | **PASS** | `v0.4_B0_phong_like_provisional` | `v0.4_B0_phong_like_provisional` |
| 3 | `visibility_version_match` | **PASS** | `v0.4_level2_sun_shadow_reprojection_step6` | `v0.4_level2_sun_shadow_reprojection_step6` |
| 4 | `sun_visibility_match` | **PASS** | `camera_visible_nol_plus_sun_shadow_pass` | `camera_visible_nol_plus_sun_shadow_pass` |
| 5 | `shadow_mapping_method_match` | **PASS** | `sun_view_depth_reprojection` | `sun_view_depth_reprojection` |
| 6 | `v_sun_macro_mode_consistency` | **PASS** | sun_visibility=Level2 → mode=`shadow_mask` | `shadow_mask` + applied=true |
| 7 | `i_scale_match` | **PASS** | — | Image=0.5445, Step6=0.5445 |
| 8 | `record_id_set_match` | **PASS** | 5 个 record_id | 5 个 record_id，完全一致 |
| 9 | `per_record_consistency` | **PASS** | 5/5 records | yaw/pitch/geom_id 全部匹配 |

**关键验证点**：
- **v_sun_macro_mode 与 sun_visibility 对应**（14 号 §8.1 核心规则）：sun_visibility=Level2 → v_sun_macro_mode="shadow_mask"，检查通过
- **record_id 集合一致**：OCS 和 Image 的 5 个 record_id 完全一致，无遗漏或多余
- **per-record yaw/pitch/geom_id 一致**：5 个姿态的 yaw/pitch/geom_id 在两个 manifest 中完全对齐

---

## 4. 产物路径

### 4.1 输出目录

```text
v0.4_results/00_validation/phase0_step7a_manifest_trial/
```

### 4.2 产物清单

| 产物 | 路径 | 说明 |
|---|---|---|
| OCS manifest | `ocs_manifest_v0_4_step6trial.json` | 5 条 records，包含 OCS 总量、per-part OCS、四类像素统计 |
| Image manifest | `image_manifest_v0_4_step6trial.json` | 5 条 records，包含 PNG/EXR 路径、I_scale、log1p_alpha |
| 一致性报告 | `consistency_check_report.json` | 9 项检查全部 PASS |

### 4.3 工具脚本路径

```text
06_v0.4_code/06_manifest/build_ocs_manifest_v0_4.py
06_v0.4_code/06_manifest/build_image_manifest_v0_4.py
06_v0.4_code/06_manifest/check_manifest_consistency_v0_4.py
```

---

## 5. 验收标准对照

**R28 最低验收标准**（全部满足）：

| 验收项 | 要求 | 实际 | 状态 |
|---|---|---|---|
| 两个 manifest 均包含 5 条 records | 5 条 | OCS=5, Image=5 | ✅ |
| record_id 在 OCS/image 两侧完全一致 | 完全一致 | 5 个 record_id 集合相同 | ✅ |
| 顶层版本字段完整 | geometry/brdf/visibility/sun_visibility/shadow_mapping_method | 全部字段完整且一致 | ✅ |
| v_sun_macro_mode 与 sun_visibility 对应 | Level2 → shadow_mask | 检查通过 | ✅ |
| I_scale 与 Step 6 summary 一致 | 一致 | 0.5445（精确匹配） | ✅ |
| record_id 集合一致 | 完全一致 | 无遗漏、无多余 | ✅ |
| 每个 record 的 yaw/pitch/geom_id 一致 | 一致 | 5/5 records 全部匹配 | ✅ |
| 检查结果必须 PASS | PASS | overall_status=PASS | ✅ |

---

## 6. 关键数据核验

### 6.1 全局参数

| 参数 | 值 | 来源 |
|---|---|---|
| `r_max` | 1.4726 m | Step 4 shadow validation |
| `ortho_scale_m` | 3.2397 m | 2.2 × r_max |
| `resolution` | 256 | 固定 |
| `pixel_area_m2` | 1.602e-4 m² | (ortho_scale / resolution)² |
| `depth_epsilon_m` | 0.7952 m | Step 4 shadow validation 校准 |
| `i_scale_smallrun` | 0.5445 | Step 5 V_sun_macro image check |
| `log1p_alpha` | 10.0 | D3 初始值 |

### 6.2 版本字段（Phase 0 临时标识）

| 字段 | OCS manifest | Image manifest |
|---|---|---|
| `geometry_version` | `v0.4_phase0_step6_smallrun` | `v0.4_phase0_step6_smallrun` |
| `brdf_version` | `v0.4_B0_phong_like_provisional` | `v0.4_B0_phong_like_provisional` |
| `visibility_version` | `v0.4_level2_sun_shadow_reprojection_step6` | `v0.4_level2_sun_shadow_reprojection_step6` |
| `ocs_integration_version` | `v0.4_pixel_level_step6` | — |
| `image_preprocess_version` | — | `v0.4_log1p_step6` |

### 6.3 5 个姿态 record_id

```text
phase63_yaw000_pitch+000
phase63_yaw090_pitch+000
phase63_yaw150_pitch+025
phase63_yaw180_pitch+000
phase63_yaw300_pitch-025
```

---

## 7. 一致性检查详情

### 7.1 核心一致性规则验证（14 号 §8.1）

**规则 1**：`ocs_manifest.geometry_version == image_manifest.geometry_version`  
✅ 通过：`v0.4_phase0_step6_smallrun`

**规则 2**：`ocs_manifest.brdf_version == image_manifest.brdf_version`  
✅ 通过：`v0.4_B0_phong_like_provisional`

**规则 3**：`ocs_manifest.visibility_version == image_manifest.visibility_version`  
✅ 通过：`v0.4_level2_sun_shadow_reprojection_step6`

**规则 4**：`ocs_manifest.sun_visibility == image_manifest.sun_visibility`  
✅ 通过：`camera_visible_nol_plus_sun_shadow_pass`

**规则 5**：`ocs_manifest.shadow_mapping_method == image_manifest.shadow_mapping_method`  
✅ 通过：`sun_view_depth_reprojection`

**规则 6**（CR5-004 修正后的 v_sun_macro 同源性）：
```text
若 ocs_manifest.sun_visibility == "camera_visible_nol":
    image_manifest.preprocessing.v_sun_macro_mode == "identity"
否则（Level 2 / Level 3）:
    image_manifest.preprocessing.v_sun_macro_mode == "shadow_mask"
image_manifest.preprocessing.v_sun_macro_applied_to_image == true
```
✅ 通过：sun_visibility=Level2 → v_sun_macro_mode="shadow_mask" + applied=true

**规则 7**：`image_manifest.preprocessing.I_scale == step6_summary.i_scale_smallrun`  
✅ 通过：0.5444863931551639（精确匹配）

**规则 8**：record_id 集合完全一致  
✅ 通过：OCS 和 Image 各 5 条，集合相同

**规则 9**：每个 record 的 yaw/pitch/geom_id 一致  
✅ 通过：5/5 records 全部匹配

### 7.2 禁止的混用（全部避免）

- ❌ v0.4 OCS + 旧 v0.3 图像 → ✅ 未发生
- ❌ 不同 geometry/brdf/visibility 版本混用 → ✅ 未发生
- ❌ OCS 含 V_sun_macro + 图像 identity → ✅ 未发生（两侧均为 shadow_mask）

---

## 8. Phase 0 当前缺口与后续补充

### 8.1 当前 Phase 0 简化项（Step 7a 已知缺口）

| 字段 | 当前状态 | 后续补充时机 |
|---|---|---|
| `camera_matrix_world` | null | Step 7b：从 Blender 渲染脚本记录中提取 |
| `sun_camera_matrix_world` | null | Step 7b：从 Blender 渲染脚本记录中提取 |
| `position_exr_path` | null | Step 7b：独立输出 Position pass（当前由 depth + 矩阵重建） |
| `sun_visibility_mask_path` | null | Step 7b：独立输出 V_sun_macro_mask PNG/NPY |
| `n_pixels_per_part` | OCS JSON 中已有，但 manifest 记录不完整 | Step 7b：从 OCS JSON 读取并写入 manifest |

### 8.2 版本字段临时标识说明

当前版本字段为 Phase 0 small-run 临时标识（如 `v0.4_phase0_step6_smallrun`），不是全量 corpus 最终版本。全量生成时需要更新为正式版本号（如 `v0.4_geometry_1.0`）。

---

## 9. 下一步建议

### 9.1 Step 7b：补充矩阵与路径字段（可选，非阻断）

- 从 Blender 渲染脚本或元数据中提取 `camera_matrix_world` 和 `sun_camera_matrix_world`
- 独立输出 Position pass EXR（当前由 depth + 矩阵重建，可改为 Blender 直接输出）
- 独立输出 V_sun_macro_mask PNG/NPY（当前内嵌在 BRDF 后处理中）
- 补充 `n_pixels_per_part` 字段到 OCS manifest

### 9.2 全量前最后检查

- 确认 manifest builder 脚本可复用于全量 2664 姿态
- 确认 consistency checker 可应用于全量 manifest
- 确认版本字段命名规范（从临时标识改为正式版本号）

### 9.3 Codex 审阅 Step 7a 后

若 R29 审阅通过，可进入全量生成准备（需满足 R28 §3.2 全量生成边界）。

---

## 10. 边界遵守确认

### 10.1 已遵守的边界（R28 禁止项）

- ✅ 未进入全量 2664 姿态生成
- ✅ 未重渲染 EXR（复用 Step 6 产物）
- ✅ 未训练模型
- ✅ 未改写论文正文
- ✅ 未修改 CLAUDE.md、13/14/24/25、路线冻结文件或书籍知识库
- ✅ 未写入 `04_Codex审阅/`
- ✅ 未生成 Codex、验收、最终放行等名义文件

### 10.2 产物分流

**工具脚本**：
```text
06_v0.4_code/06_manifest/
```

**manifest 与报告**：
```text
v0.4_results/00_validation/phase0_step7a_manifest_trial/
```

**本执行报告**：
```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/30_1C-E13_Phase0_Step7a_Manifest_Builder_验证通过_Claude执行报告.md
```

---

## 11. 总结

**Step 7a 任务完成**：
- 三个工具脚本实现并通过验证
- 两个 manifest 生成成功，各 5 条 records
- 一致性检查 9/9 全部 PASS
- 验证了 14 号 manifest 规范可执行
- 未越界，符合 R28 边界要求

**关键验证**：
- v_sun_macro_mode 与 sun_visibility 对应关系正确（14 号 §8.1 核心规则）
- record_id 跨 manifest 完全对齐
- 版本字段一致性规则全部满足

**下一步**：
- 等待 Codex 审阅 Step 7a（R29）
- Step 7b 补充矩阵与路径字段（可选）
- 全量前最后检查（R28 §3.2 全量生成边界）

---

**执行状态**：COMPLETE  
**一致性检查**：PASS（9/9）  
**产物交付**：3 scripts + 2 manifests + 1 report  
**边界遵守**：全部遵守
