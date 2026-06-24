# 36 1C-E16：全量前最终放行准备 Claude 执行报告

最后更新：2026-06-24  
执行端：Claude  
依据文件：`04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R34_Codex_审阅_1C-E15-FIX02通过并完成Step7c.md`（§7 短提示词）

---

## 0. 总体结论

```text
1C-E16 全量前最终放行准备：COMPLETE
全量 2664 姿态生成：NOT YET STARTED（本报告不含任何全量执行）
训练：NOT RELEASED
论文正文改写：NOT RELEASED
下一步：待 Codex 审阅 R35 正式放行全量
```

两项 R34 §5 保留小修已完成，Step7c dry-run checker 复跑 17/17 PASS，全量前最终放行条件清单已排出。

---

## 1. R34 小修执行

### 1.1 BRDF 分支判断顺序修复

**修改文件**：
- `06_v0.4_code/06_manifest/build_ocs_manifest_v0_4.py`
- `06_v0.4_code/06_manifest/build_image_manifest_v0_4.py`

**修改内容**：将 BRDF 分支判断顺序从 `B0/phong → GGX → B1` 改为 `B1 → GGX → B0/phong`

```text
修复前（R34 §5.1 发现的风险）：
  if "B0" in brdf_version or "phong" in brdf_version or "provisional" in brdf_version:
      → phong_like_provisional_baseline          ← B1 如果含 "phong" 会先命中这里
  elif "GGX" ...:
      → ggx_cook_torrance
  elif "B1" ...:
      → improved_phong_book_model_pending_author_confirmation

修复后：
  if "B1" in brdf_version or "improved_phong" in brdf_version:
      → improved_phong_book_model_pending_author_confirmation  ← B1 优先匹配
  elif "GGX" in brdf_version or "ggx" in brdf_version:
      → ggx_cook_torrance
  elif "B0" in brdf_version or "phong" in brdf_version or "provisional" in brdf_version:
      → phong_like_provisional_baseline
```

**验证**：对于当前 B0 dry-run（`brdf_version = v0.4_B0_phong_like_provisional`），修复前后均正确映射为 `phong_like_provisional_baseline`。对于未来 B1 full-run，不会误判为 B0。

### 1.2 Checker task 标签中性化

**修改文件**：`06_v0.4_code/06_manifest/check_manifest_consistency_v0_4.py`（第 664 行）

```text
修复前: "task": "1C-E15-FIX01 manifest consistency check (17 checks)"
修复后: "task": "v0.4 manifest consistency check (17 checks)"
```

**验证**：复跑后 report 的 `task` 字段已变为中性名称，不携带 FIX01 标签。

---

## 2. Step7c Dry-run Checker 复跑结果

### 2.1 复跑命令

```powershell
cd "D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS"
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" 06_v0.4_code\06_manifest\check_manifest_consistency_v0_4.py `
  --ocs-manifest v0.4_results\00_validation\phase0_step7c_dryrun_fix02\ocs_manifest_v0_4_step7c_dryrun.json `
  --image-manifest v0.4_results\00_validation\phase0_step7c_dryrun_fix02\image_manifest_v0_4_step7c_dryrun.json `
  --step6-summary v0.4_results\00_validation\phase0_step6_small_trial\phase0_step6_small_trial_summary.json `
  --data-root . `
  --require-prefix v0.4_results/ `
  --expected-record-count 3 `
  --output v0.4_results\00_validation\phase0_step7c_dryrun_fix02\consistency_check_report_r34fix.json
```

### 2.2 复跑结果

```text
overall_status = PASS
check_count = 17
task = "v0.4 manifest consistency check (17 checks)"   ← 标签已中性化
checks 1-17 = PASS（全部）
records_completeness = PASS（expected=3, OCS=3, Image=3）
```

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
| 10 | record_id_set_match | PASS |
| 11 | per_record_consistency | PASS |
| 12 | path_base_consistency | PASS（0 inconsistencies） |
| 13 | ocs_paths_exist | PASS（0 missing） |
| 14 | image_paths_exist | PASS（0 missing） |
| 15 | camera_matrix_non_null_and_valid | PASS（0 invalid） |
| 16 | sun_visibility_mask_path_non_null_and_exists | PASS（0 missing） |
| 17 | records_completeness | PASS（gate enabled） |

---

## 3. 全量正式运行命令边界建议

### 3.1 全量姿态网格

```text
来源：06_v0.4_code/01_geometry/attitude_grid.py
yaw  = 0°, 5°, 10°, ..., 355° → 72 个
pitch = -90°, -85°, ..., 0°, ..., 85°, 90° → 37 个
总计 = 72 × 37 = 2664 姿态
```

### 3.2 建议输出目录

```text
全量 shadow passes:
  v0.4_results/01_fullrun/shadow_passes/

全量 BRDF/OCS/image 后处理产物 + summary:
  v0.4_results/01_fullrun/postprocess/

全量 manifest:
  v0.4_results/01_fullrun/manifest/ocs_manifest_v0_4_fullrun.json
  v0.4_results/01_fullrun/manifest/image_manifest_v0_4_fullrun.json

全量 checker 报告:
  v0.4_results/01_fullrun/manifest/consistency_check_report_fullrun.json
```

理由：与 `00_validation/` 区分，全量产物的命名空间独立，避免覆盖验证阶段的输出。

### 3.3 Stage 1 — Blender shadow 渲染

```powershell
# 需要在 Blender 脚本中实现 2664 姿态循环，或对现有 render_20_attitudes_shadow.py 做批量化改造
"D:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --background --python 06_v0.4_code\02_blender\render_full_2664_shadow.py

# 关键要求（从 Step7c 经验导出）：
# - 每个姿态输出 camera.exr + sun.exr
# - 另起独立脚本 log_camera_matrices.py（已有）记录相机矩阵，矩阵对所有姿态相同
# - 渲染后输出 render_metadata.json（含姿态列表、文件存在性检查）
# - 推荐分批渲染（如 72 个 yaw 分 8 批 × 9 yaw/批），避免单次 Blender 运行时间过长
```

### 3.4 Stage 2 — Shadow validation

```powershell
# 从 Step 4 脚本改造：validate_shadow_consistency_fixed.py
# 输入：shadow_passes/
# 输出：shadow_validation/ 目录 + shadow_validation_summary.json
# 关键参数：DEPTH_EPSILON_M_FINAL = 0.7952109582768545 m
```

### 3.5 Stage 3 — BRDF/OCS/image 后处理

```powershell
cd "D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS"
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" 06_v0.4_code\05_postprocess\run_phase1_fullrun.py

# 从 run_phase0_step7c_dryrun.py 改造为 2664 姿态批处理：
# - 循环 2664 姿态
# - 每个姿态：BRDF response → I_linear EXR + log1p PNG → V_sun_macro mask → OCS JSON
# - 输出 fullrun_summary.json
# - 关键参数：
#   BRDF_BRANCH = "B0"（或 B1/GGX 取决于正式分支选择）
#   I_scale = 沿用 Step5 的 0.5444863931551639（若 full-run 出现更高 I_linear 需审计）
#   DEPTH_EPSILON_M_FINAL = 0.7952109582768545
```

### 3.6 Stage 4 — Manifest 构建

```powershell
# OCS manifest
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" 06_v0.4_code\06_manifest\build_ocs_manifest_v0_4.py `
  --step-summary v0.4_results\01_fullrun\postprocess\fullrun_summary.json `
  --step-output-dir v0.4_results\01_fullrun\postprocess `
  --shadow-passes-dir v0.4_results\01_fullrun\shadow_passes `
  --output v0.4_results\01_fullrun\manifest\ocs_manifest_v0_4_fullrun.json `
  --data-root . `
  --camera-matrix-json v0.4_results\00_validation\phase0_step7c_dryrun_fix02\camera_matrices_blender.json `
  --sun-visibility-mask-dir v0.4_results\01_fullrun\postprocess

# Image manifest
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" 06_v0.4_code\06_manifest\build_image_manifest_v0_4.py `
  --step-summary v0.4_results\01_fullrun\postprocess\fullrun_summary.json `
  --step-output-dir v0.4_results\01_fullrun\postprocess `
  --output v0.4_results\01_fullrun\manifest\image_manifest_v0_4_fullrun.json `
  --data-root .
```

### 3.7 Stage 5 — 全量门禁检查

```powershell
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" 06_v0.4_code\06_manifest\check_manifest_consistency_v0_4.py `
  --ocs-manifest v0.4_results\01_fullrun\manifest\ocs_manifest_v0_4_fullrun.json `
  --image-manifest v0.4_results\01_fullrun\manifest\image_manifest_v0_4_fullrun.json `
  --step6-summary <对应 full-run 的 summary> `
  --data-root . `
  --require-prefix v0.4_results/ `
  --expected-record-count 2664 `
  --output v0.4_results\01_fullrun\manifest\consistency_check_report_fullrun.json
```

**全量放行条件**：
```text
overall_status = PASS
17 项全部 PASS
records_completeness = PASS（OCS=2664, Image=2664, expected=2664）
path_base_consistency = PASS（0 inconsistencies）
camera_matrix_non_null_and_valid = PASS（0 invalid）
sun_visibility_mask_path_non_null_and_exists = PASS（0 missing）
```

---

## 4. Checkpoint / 失败恢复最小策略

### 4.1 设计原则

当前阶段不要求完整 `--append / --partial / --finalize` 框架。全量运行的最低恢复策略基于 record-level 状态标记：

### 4.2 每姿态状态标记

后处理 summary 的每个 record 已包含：

```json
{
  "record_id": "phase63_yaw045_pitch+000",
  "status": "COMPLETE"   // COMPLETE | MISSING | FAILED
}
```

### 4.3 恢复策略

```text
1. Blender 渲染阶段：
   - render_metadata.json 已记录每个姿态 camera_exists / sun_exists
   - 重跑前先检查已有 EXR，跳过已存在的姿态
   - 推荐：Blender 脚本检查 output file 是否存在，若存在则 skip

2. 后处理阶段：
   - 读取 fullrun_summary.json 已有的 records
   - 只处理 status ≠ "COMPLETE" 的 record_id
   - 新完成记录追加/更新 summary 中的 records

3. Manifest 构建阶段：
   - builder 读取 summary 中 status="COMPLETE" 的记录构建 manifest
   - 若存在 FAILED/MISSING，manifest 的 n_total_expected 写入预期总数
   - checker 的 records_completeness gate 会自动发现不足

4. 最小 checkpoint 文件：
   - fullrun_summary.json 本身就是 checkpoint
   - 每次写入前先备份为 fullrun_summary_backup_TIMESTAMP.json
```

### 4.4 明确不在本次范围

```text
- 不实现自动 resume / 断点续跑框架
- 不实现分布式/并行批处理调度
- 不实现渲染队列管理系统
- 上述可在 Phase 1 后续迭代中按需添加
```

---

## 5. 全量前额外提醒

### 5.1 I_scale 审计

当前 `I_scale = 0.5444863931551639` 来自 Step 5 的 5 姿态 max。若全量 2664 姿态中出现更高的 `I_linear` 像素值：

```text
1. 记录 max(I_linear) 和对应的 record_id
2. 若超过当前 I_scale 导致 log1p PNG 饱和（>0.99 的像素比例显著增加）
3. 则在全量后做全局重标定：I_scale_full = max(I_linear over 2664)
4. 重标定后重新生成 log1p PNG（不需要重渲染，只重新执行 log1p 映射）
```

### 5.2 相机矩阵可复用

相机矩阵对所有 2664 姿态是相同的（camera/sun camera 在世界空间不动，只有卫星旋转）。已生成的 `camera_matrices_blender.json` 可直接用于全量 manifest 构建，不需要每次渲染重新记录。

### 5.3 BRDF 分支选择

当前 `BRDF_BRANCH = "B0"`（phong_like_provisional_baseline）。若全量改用 B1 或 GGX：

```text
- 修改后处理脚本中的 BRDF_BRANCH 参数
- 确保 brdf_version 字段反映真实分支
- B1 公式必须在作者确认后才能在正式全量产物中使用
- GGX 作为对照分支，manifest 中 brdf_model 应写为 ggx_cook_torrance
```

### 5.4 多观测几何

`config_v0_4.py` 定义了 5 个观测几何（G0-G4）。当前 Phase 0 所有验证仅使用 G0（phase63, ~63°）。若全量需要覆盖多几何：

```text
- 每个几何需要独立的 shadow pass 渲染（相机位置不同）
- 相机矩阵因几何而异，需为每个几何单独记录
- 建议先完成 G0 全量并通过门禁，再扩展到 G1-G4
```

---

## 6. 修改文件汇总

| 操作 | 文件 | 变更 |
|------|------|------|
| **修改** | `06_v0.4_code/06_manifest/build_ocs_manifest_v0_4.py` | BRDF 分支判断顺序：B1 → GGX → B0/phong |
| **修改** | `06_v0.4_code/06_manifest/build_image_manifest_v0_4.py` | 同上 |
| **修改** | `06_v0.4_code/06_manifest/check_manifest_consistency_v0_4.py` | task 标签中性化为 `v0.4 manifest consistency check (17 checks)` |

---

## 7. 红线边界确认

- [x] **未进入全量 2664 姿态生成**：本报告仅做准备和命令边界建议
- [x] **未训练**：无模型训练
- [x] **未修改论文正文**：未触及任何论文文件
- [x] **未修改冻结文件**：13/14/24/25 未改动
- [x] **未写入 04_Codex审阅/**：报告写入 `02_Claude输出/`
- [x] **未生成 Codex 裁决文件**：报告不含 Codex/验收/最终放行名义
- [x] **Step7c dry-run checker 17/17 仍 PASS**：小修不影响现有产物

---

## 8. 全量前就绪清单 → 待 Codex R35 裁决

| # | 条件 | 状态 |
|---|------|------|
| 1 | BRDF 分支判断顺序已修复 | ✅ R34 §5.1 小修完成 |
| 2 | Checker task 标签已中性化 | ✅ R34 §5.2 小修完成 |
| 3 | Step7c dry-run checker 17/17 PASS | ✅ 复跑确认 |
| 4 | Manifest builder 路径基准统一 | ✅ 已验证 |
| 5 | 相机矩阵来自 Blender matrix_world | ✅ 已验证 |
| 6 | V_sun_macro mask 输出链路完整 | ✅ 已验证 |
| 7 | Completeness gate 可用 | ✅ 已验证 |
| 8 | Full-run 输出目录建议明确 | ✅ §3.2 |
| 9 | Full-run 命令边界明确 | ✅ §3.3-3.7 |
| 10 | Checkpoint/失败恢复策略明确 | ✅ §4 |
| 11 | 全量仍未实际启动 | ✅ 本报告不含任何全量执行 |
| 12 | **正式放行全量 2664 姿态生成** | ⏳ 待 R35 Codex 裁决 |

---

## 9. 给 Codex 的下轮审阅入口

```text
Claude 输出报告：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/36_1C-E16_全量前最终放行准备_Claude执行报告.md

修改后的代码（供复核）：
- 06_v0.4_code/06_manifest/build_ocs_manifest_v0_4.py（BRDF 分支顺序修复）
- 06_v0.4_code/06_manifest/build_image_manifest_v0_4.py（BRDF 分支顺序修复）
- 06_v0.4_code/06_manifest/check_manifest_consistency_v0_4.py（task 标签中性化）

R34 小修复跑验证产物：
- v0.4_results/00_validation/phase0_step7c_dryrun_fix02/consistency_check_report_r34fix.json

Codex 下一轮判断（R35）：
1. 两项全量前小修是否完成 → YES（§1 已执行并验证）
2. Step7c dry-run checker 是否仍 PASS → YES（§2 复跑确认）
3. full-run 命令、输出目录、expected-record-count、checkpoint/失败恢复边界是否明确 → YES（§3-4）
4. 是否正式放行全量 2664 姿态生成 → 待 R35 裁决
```
