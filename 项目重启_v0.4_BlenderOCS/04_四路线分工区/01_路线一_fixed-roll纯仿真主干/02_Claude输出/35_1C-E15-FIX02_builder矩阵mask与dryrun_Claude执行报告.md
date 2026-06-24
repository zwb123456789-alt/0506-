# 35 1C-E15-FIX02：Builder/矩阵/Mask 修复与 3 姿态物理 dry-run Claude 执行报告

最后更新：2026-06-24  
执行端：Claude  
依据文件：`04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R33_Codex_审阅_1C-E15-FIX01通过并规划FIX02.md`（§5 短提示词）

---

## 0. 总体结果

```text
1C-E15-FIX02：COMPLETE → 17/17 PASS
全量 2664 姿态生成：NOT RELEASED
训练：NOT RELEASED
论文正文改写：NOT RELEASED
下一步：待 Codex 审阅；若通过，Step7c 可宣告完成并评估全量前最后放行条件
```

3 姿态 dry-run 全部完成；OCS/Image manifest 路径基准已统一为项目根相对路径（`v0.4_results/` 前缀）；camera_matrix_world 和 sun_camera_matrix_world 来自 Blender `matrix_world` 真实日志；V_sun_macro mask 已输出并写入 `sun_visibility_mask_path`；17 项 checker 全 PASS。

---

## 1. 修改文件清单

| 操作 | 文件 | 说明 |
|------|------|------|
| **新增** | `06_v0.4_code/02_blender/log_camera_matrices.py` | Blender 矩阵日志脚本：搭建与 `render_20_attitudes_shadow.py` 完全相同的场景，记录 `Camera_Detector.matrix_world` 和 `Camera_Sun.matrix_world` 到 JSON。不执行任何渲染。 |
| **新增** | `06_v0.4_code/05_postprocess/run_phase0_step7c_dryrun.py` | Step7c 3 姿态 dry-run 管线脚本：复用 `image_response_v0_4` 和 `ocs_integration_v0_4`，为 3 个新姿态输出 BRDF/OCS/image 产物 + V_sun_macro mask（PNG + NPY）。 |
| **修改** | `06_v0.4_code/06_manifest/build_ocs_manifest_v0_4.py` | 新增 `--data-root` 参数；所有 record 路径统一为 data_root 相对路径 POSIX `/`；新增 `--camera-matrix-json` 从 Blender 日志读取矩阵；新增 `--sun-visibility-mask-dir` 自动发现 mask 路径；B1 分支映射为 `improved_phong_book_model_pending_author_confirmation`。 |
| **修改** | `06_v0.4_code/06_manifest/build_image_manifest_v0_4.py` | 新增 `--data-root` 参数；所有 record 路径统一为 data_root 相对路径 POSIX `/`；B1 分支映射与 OCS builder 保持一致。 |

---

## 2. 3 姿态产物路径

### 2.1 输出目录

```text
v0.4_results/00_validation/phase0_step7c_dryrun_fix02/
```

### 2.2 每姿态产物

| 姿态 | label | 产物 |
|------|-------|------|
| yaw=45, pitch=0 | `yaw045_pitch+000_roll+000` | `_linear.exr`, `_brdf.png`, `_ocs.json`, `_v_sun_macro.png`, `_v_sun_macro.npy` |
| yaw=270, pitch=-30 | `yaw270_pitch-030_roll+000` | `_linear.exr`, `_brdf.png`, `_ocs.json`, `_v_sun_macro.png`, `_v_sun_macro.npy` |
| yaw=135, pitch=0 | `yaw135_pitch+000_roll+000` | `_linear.exr`, `_brdf.png`, `_ocs.json`, `_v_sun_macro.png`, `_v_sun_macro.npy` |

### 2.3 全局文件

| 文件 | 说明 |
|------|------|
| `camera_matrices_blender.json` | 来自 Blender `matrix_world` 日志的 4x4 矩阵 |
| `ocs_manifest_v0_4_step7c_dryrun.json` | OCS manifest（3 records） |
| `image_manifest_v0_4_step7c_dryrun.json` | Image manifest（3 records） |
| `phase0_step7c_dryrun_summary.json` | Dry-run summary（含完整 records 和像素统计） |
| `consistency_check_report.json` | 17 项 checker 报告（overall_status = PASS） |

### 2.4 各姿态关键统计

| 姿态 | OCS_total | camera_visible | nol_positive | sun_visible | contributing |
|------|-----------|----------------|--------------|-------------|-------------|
| yaw045_pitch+000 | 3.72e-02 | 5862 | 4855 | 5834 | 4845 |
| yaw270_pitch-030 | 1.94e-02 | 5536 | 4111 | 5536 | 4111 |
| yaw135_pitch+000 | 2.65e-02 | 5052 | 3452 | 5052 | 3452 |

---

## 3. Camera Matrix 来源验证

### 3.1 矩阵来源

```text
来源：Blender 场景对象 matrix_world 属性
脚本：06_v0.4_code/02_blender/log_camera_matrices.py
命令："D:/Program Files/Blender Foundation/Blender 4.2/blender.exe" --background --python log_camera_matrices.py
输出：v0.4_results/00_validation/phase0_step7c_dryrun_fix02/camera_matrices_blender.json
```

### 3.2 Camera_Detector matrix_world

```text
[[ 0.8944, -0.0398,  0.4454,  3.2798],
 [ 0.4472,  0.0797, -0.8909, -6.5595],
 [-0.0000,  0.9960,  0.0891,  0.6560],
 [ 0.0000,  0.0000,  0.0000,  1.0000]]
```

### 3.3 Camera_Sun matrix_world

```text
[[-0.0000, -0.2873,  0.9578,  7.0525],
 [ 1.0000, -0.0000,  0.0000,  0.0000],
 [ 0.0000,  0.9578,  0.2873,  2.1157],
 [ 0.0000,  0.0000,  0.0000,  1.0000]]
```

### 3.4 验证结果

- [x] 矩阵来自 Blender 场景对象的 `matrix_world` 属性（非 identity、非手工构造）
- [x] 4x4 结构完整，16 元素均为 float
- [x] camera_matrix_world 和 sun_camera_matrix_world 均非 null
- [x] 矩阵方向为 camera/sun camera local → world
- [x] 所有 16 元素 float(x) 可转性在 Blender 内自检通过
- [x] Checker 检查 15（camera_matrix_non_null_and_valid）= PASS，0 invalid

---

## 4. V_sun_macro Mask 验证

### 4.1 Mask 产物

每个姿态输出两个格式的 mask：

| 格式 | 用途 | 示例路径（相对项目根） |
|------|------|------------------------|
| PNG | manifest `sun_visibility_mask_path` | `v0.4_results/00_validation/phase0_step7c_dryrun_fix02/yaw045_pitch+000_roll+000_v_sun_macro.png` |
| NPY | 可复核的浮点数组 | `v0.4_results/00_validation/phase0_step7c_dryrun_fix02/yaw045_pitch+000_roll+000_v_sun_macro.npy` |

### 4.2 验证结果

- [x] Mask 通过 `compute_v_sun_macro()` 从真实 camera/sun EXR 重投影生成（复用 Step 4 validated 逻辑）
- [x] `sun_visibility_mask_path` 在 OCS manifest 中非空（manifest 写入的是 PNG 路径）
- [x] Mask 文件真实存在（checker 检查 16 = PASS，0 missing）
- [x] Mask 路径使用项目根相对路径（`v0.4_results/` 前缀），基准已统一
- [x] Mask 仅含 0/1 值（`compute_v_sun_macro` 保证）

---

## 5. Checker 17 项结果

### 5.1 运行命令

```powershell
cd "D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS"
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" 06_v0.4_code\06_manifest\check_manifest_consistency_v0_4.py `
  --ocs-manifest v0.4_results\00_validation\phase0_step7c_dryrun_fix02\ocs_manifest_v0_4_step7c_dryrun.json `
  --image-manifest v0.4_results\00_validation\phase0_step7c_dryrun_fix02\image_manifest_v0_4_step7c_dryrun.json `
  --step6-summary v0.4_results\00_validation\phase0_step6_small_trial\phase0_step6_small_trial_summary.json `
  --data-root . `
  --require-prefix v0.4_results/ `
  --expected-record-count 3 `
  --output v0.4_results\00_validation\phase0_step7c_dryrun_fix02\consistency_check_report.json
```

### 5.2 检查结果

| # | 检查项 | 结果 |
|---|--------|------|
| 1 | geometry_version_match | PASS |
| 2 | brdf_version_match | PASS |
| 3 | visibility_version_match | PASS |
| 4 | sun_visibility_match | PASS |
| 5 | shadow_mapping_method_match | PASS |
| 6 | brdf_model_match | PASS |
| 7 | brdf_model_vs_brdf_version_consistency | PASS |
| 8 | v_sun_macro_mode_consistency | PASS |
| 9 | i_scale_match | PASS |
| 10 | record_id_set_match | PASS（3 vs 3） |
| 11 | per_record_consistency | PASS（3 records checked） |
| 12 | path_base_consistency | PASS（0 inconsistencies） |
| 13 | ocs_paths_exist | PASS（0 missing, 0 base-inconsistent） |
| 14 | image_paths_exist | PASS（0 missing, 0 base-inconsistent） |
| 15 | camera_matrix_non_null_and_valid | PASS（0 invalid） |
| 16 | sun_visibility_mask_path_non_null_and_exists | PASS（0 missing） |
| 17 | records_completeness | PASS（3/3, gate enabled via --expected-record-count 3） |

```text
overall_status = PASS
check_count = 17
```

---

## 6. 路径基准统一验证

### 6.1 统一策略

所有 manifest record 路径统一为：

```text
基准：项目根相对路径（data_root = "." 即 项目重启_v0.4_BlenderOCS/）
前缀：必须满足 --require-prefix v0.4_results/
格式：POSIX "/"（Windows 反斜杠已转为 /）
```

### 6.2 OCS manifest record 路径示例（yaw045_pitch+000_roll+000）

```json
{
  "camera_exr_path": "v0.4_results/00_validation/shadow_passes/yaw045_pitch+000_roll+000_camera.exr",
  "sun_depth_exr_path": "v0.4_results/00_validation/shadow_passes/yaw045_pitch+000_roll+000_sun.exr",
  "exr_path": "v0.4_results/00_validation/phase0_step7c_dryrun_fix02/yaw045_pitch+000_roll+000_linear.exr",
  "png_path": "v0.4_results/00_validation/phase0_step7c_dryrun_fix02/yaw045_pitch+000_roll+000_brdf.png",
  "sun_visibility_mask_path": "v0.4_results/00_validation/phase0_step7c_dryrun_fix02/yaw045_pitch+000_roll+000_v_sun_macro.png"
}
```

### 6.3 对比 FIX01 之前的路径混用（已修复）

```text
修复前（R32 发现）：
  camera_exr_path = 00_validation/shadow_passes/...   （相对于 v0.4_results 而非项目根）
  exr_path = v0.4_results/00_validation/...           （相对于项目根）
  → 两种基准混用，checker 无法正确解析

修复后（FIX02）：
  所有路径 = v0.4_results/...                        （统一为项目根相对路径）
  → checker --data-root . 统一解析，0 base-inconsistent
```

---

## 7. 红线边界确认

- [x] **未进入全量 2664 姿态生成**：仅 3 个 dry-run 姿态
- [x] **未训练**：无模型训练
- [x] **未修改论文正文**：未触及任何论文文件
- [x] **未修改冻结文件**：13/14/24/25 未改动
- [x] **未写入 04_Codex审阅/**：报告写入 `02_Claude输出/`
- [x] **未生成 Codex 裁决文件**：报告不含 Codex/验收/最终放行名义
- [x] **B1 ≠ GGX**：brdf_model 映射中 B1 → `improved_phong_book_model_pending_author_confirmation`，GGX 独立为 `ggx_cook_torrance`
- [x] **I_scale 说明修正**：summary 和报告均写为 "来自 Step 5 的 5 姿态 image impact validation"
- [x] **矩阵不是 identity 或手工构造**：来自 Blender `matrix_world` 真实日志
- [x] **3 姿态均非 Step 6 small-run 姿态**：独立 dry-run，可独立验证

---

## 8. 阻断项与已知问题

### 8.1 当前无阻断项

```text
3 姿态 dry-run 全部 COMPLETE，17 项 checker 全部 PASS，无阻断项。
```

### 8.2 保留注意项

1. **Step6 summary 作为 I_scale 的参照源**：checker 检查 9（i_scale_match）使用 Step6 summary 的 `i_scale_smallrun`。当前 dry-run 延续 Step5 的 `i_scale_step5 = 0.5444863931551639`，两者一致。若后续全量出现更高 `I_linear` 像素值，需审计是否需要重标定。

2. **checker 报告 task 字段标注为 "1C-E15-FIX01"**：这是 checker 代码内的固定标签（FIX01 更新 docstring 时写入），不影响对 FIX02 数据的实际检查内容。17 项检查所有结果均为针对 FIX02 dry-run manifest 的正确判定。

3. **B1 正式公式未经作者确认**：brdf_model 映射中 B1 写为 `improved_phong_book_model_pending_author_confirmation`，等待作者确认书中改进冯模型公式与材料的对应关系。

---

## 9. 全量前就绪评估

FIX02 完成后，以下全量前条件已满足：

| 条件 | 状态 |
|------|------|
| Manifest builder 路径基准统一 | ✅ 已修复 |
| Checker 路径解析正确 | ✅ FIX01 修复，FIX02 验证通过 |
| 相机矩阵来自 Blender matrix_world | ✅ 已验证 |
| V_sun_macro mask 输出并写入 manifest | ✅ 已验证 |
| 17 项 checker 体系可用 | ✅ 全 PASS |
| Completeness gate 可用 | ✅ --expected-record-count 验证通过 |
| 物理 dry-run 可完整执行 | ✅ 3 姿态通过 |

待 Codex 确认的下一步条件：

```text
1. 3 姿态 dry-run 是否真实执行（物理产物齐全） → YES
2. manifest 路径基准是否统一 → YES，0 inconsistencies
3. 矩阵是否来自 Blender 真实 matrix_world → YES，来源可追溯
4. V_sun_macro mask 是否存在且与 manifest 对齐 → YES，checker 检查 16 PASS
5. 17 项 checker 是否 PASS → YES，overall_status = PASS
6. 是否具备进入全量前最后放行审阅的条件 → 待 Codex 判定
```

---

## 10. 给 Codex 的下轮审阅入口

```text
Claude 输出报告：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/35_1C-E15-FIX02_builder矩阵mask与dryrun_Claude执行报告.md

Codex 需审阅的产物：
- v0.4_results/00_validation/phase0_step7c_dryrun_fix02/ocs_manifest_v0_4_step7c_dryrun.json
- v0.4_results/00_validation/phase0_step7c_dryrun_fix02/image_manifest_v0_4_step7c_dryrun.json
- v0.4_results/00_validation/phase0_step7c_dryrun_fix02/consistency_check_report.json
- v0.4_results/00_validation/phase0_step7c_dryrun_fix02/camera_matrices_blender.json
- v0.4_results/00_validation/phase0_step7c_dryrun_fix02/phase0_step7c_dryrun_summary.json

修改后的代码（供复核）：
- 06_v0.4_code/06_manifest/build_ocs_manifest_v0_4.py
- 06_v0.4_code/06_manifest/build_image_manifest_v0_4.py
- 06_v0.4_code/02_blender/log_camera_matrices.py
- 06_v0.4_code/05_postprocess/run_phase0_step7c_dryrun.py
```
