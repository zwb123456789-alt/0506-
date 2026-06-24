# R34 Codex 审阅：1C-E15-FIX02 通过并完成 Step7c

最后更新：2026-06-24  
审阅端：Codex  
审阅对象：`04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/35_1C-E15-FIX02_builder矩阵mask与dryrun_Claude执行报告.md`  
关联产物：`v0.4_results/00_validation/phase0_step7c_dryrun_fix02/`  
关联代码：

```text
06_v0.4_code/06_manifest/build_ocs_manifest_v0_4.py
06_v0.4_code/06_manifest/build_image_manifest_v0_4.py
06_v0.4_code/06_manifest/check_manifest_consistency_v0_4.py
06_v0.4_code/02_blender/log_camera_matrices.py
06_v0.4_code/05_postprocess/run_phase0_step7c_dryrun.py
```

---

## 1. 阶段判定

```text
1C-E15-FIX02：PASS
Phase 0 Step 7c：COMPLETE
全量 2664 姿态生成：NOT YET RELEASED
训练：NOT RELEASED
论文正文改写：NOT RELEASED
下一步：1C-E16，全量 2664 生成前最终放行审阅与小修确认
```

FIX02 已完成 R33 要求的 builder/matrix/mask 修复与 3 姿态物理 dry-run。3 个非 Step6 small-run 姿态均生成完整产物，OCS/Image manifest 路径基准统一，camera/sun camera 矩阵非空且来自 Blender `matrix_world` 日志，`V_sun_macro` mask 已写入 manifest，17 项 checker 通过。

但根据项目阶段门规则，本轮仍不直接放行全量 2664。全量启动前还需进行一次最终放行审阅，确认正式 full-run 参数、输出目录、失败恢复边界和两个小修提醒。

---

## 2. 产物归位与范围

### 2.1 Claude 报告

已确认报告位于正确路径：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/35_1C-E15-FIX02_builder矩阵mask与dryrun_Claude执行报告.md
```

未发现写入 `04_Codex审阅/` 或生成 Codex 裁决文件。

### 2.2 Dry-run 输出目录

产物目录：

```text
v0.4_results/00_validation/phase0_step7c_dryrun_fix02/
```

关键文件已存在：

```text
camera_matrices_blender.json
phase0_step7c_dryrun_summary.json
ocs_manifest_v0_4_step7c_dryrun.json
image_manifest_v0_4_step7c_dryrun.json
consistency_check_report.json
codex_rerun_consistency_check_report.json
yaw045_pitch+000_roll+000_linear.exr / _brdf.png / _ocs.json / _v_sun_macro.png / _v_sun_macro.npy
yaw270_pitch-030_roll+000_linear.exr / _brdf.png / _ocs.json / _v_sun_macro.png / _v_sun_macro.npy
yaw135_pitch+000_roll+000_linear.exr / _brdf.png / _ocs.json / _v_sun_macro.png / _v_sun_macro.npy
```

---

## 3. Codex 复核结果

### 3.1 3 姿态选择

Dry-run 姿态为：

```text
yaw045_pitch+000_roll+000
yaw270_pitch-030_roll+000
yaw135_pitch+000_roll+000
```

它们均不属于 Step6 small-run 的 5 姿态集合：

```text
yaw180_pitch+000_roll+000
yaw150_pitch+025_roll+000
yaw000_pitch+000_roll+000
yaw090_pitch+000_roll+000
yaw300_pitch-025_roll+000
```

满足 R33 的独立 dry-run 要求。

### 3.2 Matrix 来源

已读取：

```text
v0.4_results/00_validation/phase0_step7c_dryrun_fix02/camera_matrices_blender.json
```

文件声明矩阵来自：

```text
camera_matrix_world     = Camera_Detector.matrix_world
sun_camera_matrix_world = Camera_Sun.matrix_world
```

矩阵为 4x4，非 null，非 identity，且在 OCS manifest 的 3 个 records 中均已写入。checker 第 15 项通过。

### 3.3 Manifest 路径基准

OCS manifest 的路径示例：

```text
camera_exr_path = v0.4_results/00_validation/shadow_passes/yaw045_pitch+000_roll+000_camera.exr
sun_depth_exr_path = v0.4_results/00_validation/shadow_passes/yaw045_pitch+000_roll+000_sun.exr
sun_visibility_mask_path = v0.4_results/00_validation/phase0_step7c_dryrun_fix02/yaw045_pitch+000_roll+000_v_sun_macro.png
exr_path = v0.4_results/00_validation/phase0_step7c_dryrun_fix02/yaw045_pitch+000_roll+000_linear.exr
png_path = v0.4_results/00_validation/phase0_step7c_dryrun_fix02/yaw045_pitch+000_roll+000_brdf.png
```

Image manifest 路径同样为项目根相对路径，均满足 `v0.4_results/` 前缀。checker 第 12-14 项通过。

### 3.4 Mask 抽查

Codex 读取 3 个 `*_v_sun_macro.npy` 后确认：

```text
phase63_yaw045_pitch+000: mask sum = 5834, n_pixels_sun_visible = 5834
phase63_yaw270_pitch-030: mask sum = 5536, n_pixels_sun_visible = 5536
phase63_yaw135_pitch+000: mask sum = 5052, n_pixels_sun_visible = 5052
```

3 个 mask 均为 256x256，取值只包含 0/1。`sun_visibility_mask_path` 写入 PNG，PNG/NPY 文件均存在。checker 第 16 项通过。

### 3.5 Checker 复跑

Codex 复跑命令：

```powershell
C:\Users\97466\.conda\envs\ocs_sim\python.exe 06_v0.4_code\06_manifest\check_manifest_consistency_v0_4.py `
  --ocs-manifest v0.4_results\00_validation\phase0_step7c_dryrun_fix02\ocs_manifest_v0_4_step7c_dryrun.json `
  --image-manifest v0.4_results\00_validation\phase0_step7c_dryrun_fix02\image_manifest_v0_4_step7c_dryrun.json `
  --step6-summary v0.4_results\00_validation\phase0_step6_small_trial\phase0_step6_small_trial_summary.json `
  --data-root . `
  --require-prefix v0.4_results/ `
  --expected-record-count 3 `
  --output v0.4_results\00_validation\phase0_step7c_dryrun_fix02\codex_rerun_consistency_check_report.json
```

复跑结果：

```text
overall_status = PASS
check_count = 17
checks 1-17 = PASS
records_completeness = PASS, expected = 3, OCS = 3, Image = 3
```

---

## 4. 本轮裁决

| R33 判断项 | Codex 裁决 |
|---|---|
| 3 姿态 dry-run 是否真实执行 | PASS |
| manifest 路径基准是否统一 | PASS |
| 矩阵是否来自 Blender 真实 matrix_world | PASS |
| V_sun_macro mask 是否存在且与 manifest 对齐 | PASS |
| 17 项 checker 是否 PASS | PASS |
| 是否具备进入全量前最后放行审阅条件 | YES，但尚未直接放行全量 |

---

## 5. 保留小修提醒

### 5.1 BRDF 分支判断顺序需在全量前小修

当前 builder 中的 BRDF 判断顺序为：

```python
if "B0" in brdf_version or "phong" in brdf_version or "provisional" in brdf_version:
    brdf_model = "phong_like_provisional_baseline"
elif "GGX" in brdf_version or "ggx" in brdf_version:
    brdf_model = "ggx_cook_torrance"
elif "B1" in brdf_version or "improved_phong" in brdf_version:
    brdf_model = "improved_phong_book_model_pending_author_confirmation"
```

这对本轮 B0 dry-run 无影响，但未来如果 `brdf_version` 同时包含 `B1` 与 `phong`，会先命中 `phong` 分支而不是 B1 分支。全量前建议改为显式函数：

```text
B0/provisional/phong_like_provisional -> phong_like_provisional_baseline
B1/improved_phong                     -> improved_phong_book_model_pending_author_confirmation
GGX/ggx                               -> ggx_cook_torrance
```

优先检查更明确的 branch token，而不是泛化匹配 `phong`。

### 5.2 checker task 标签仍显示 FIX01

当前 checker report 的 `task` 仍为：

```text
1C-E15-FIX01 manifest consistency check (17 checks)
```

这不影响检查结果，但全量前建议改为更中性的：

```text
v0.4 manifest consistency check (17 checks)
```

避免后续 full-run report 仍带 Step7c-FIX01 标签。

上述两项是全量前清理项，不阻断 Step7c 完成。

---

## 6. 阶段门结论

```text
Phase 0 Step 7c：COMPLETE
```

Step7c 已经证明：

```text
1. builder 可输出路径基准统一的 OCS/Image manifest；
2. camera_matrix_world / sun_camera_matrix_world 可由 Blender matrix_world 日志写入；
3. Level 2 sun shadow 下可输出 V_sun_macro mask 并写入 sun_visibility_mask_path；
4. 3 姿态 dry-run 可生成完整 BRDF/OCS/image/mask 产物；
5. 17 项 checker 可对 dry-run manifest 给出 PASS；
6. completeness gate 可按 expected-record-count 生效。
```

因此具备进入“全量前最后放行审阅”的条件。

---

## 7. 给 Claude 的下一步短提示词

```text
执行 1C-E16：全量 2664 生成前最终放行审阅准备与小修确认。

依据文件：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R34_Codex_审阅_1C-E15-FIX02通过并完成Step7c.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/35_1C-E15-FIX02_builder矩阵mask与dryrun_Claude执行报告.md
v0.4_results/00_validation/phase0_step7c_dryrun_fix02/
06_v0.4_code/06_manifest/

任务：
1. 不进入全量 2664 生成，只做全量前最终放行准备。
2. 对 build_ocs_manifest_v0_4.py 和 build_image_manifest_v0_4.py 做 BRDF 分支判断小修：B1/improved_phong 必须优先于泛化 phong/provisional 匹配，确保 B1 不会被误判为 B0 phong_like_provisional_baseline。
3. 将 checker report 的 task 标签改为中性名称：v0.4 manifest consistency check (17 checks)，不要继续固定写 1C-E15-FIX01。
4. 复跑 Step7c dry-run checker，确认 17 项仍 PASS。
5. 输出一份全量前最终放行准备报告，列出：
   - 小修文件和差异；
   - Step7c dry-run 仍 PASS 的 checker 路径；
   - 全量正式运行建议命令边界；
   - full-run 输出目录建议；
   - expected-record-count = 2664 的 checker 使用方式；
   - checkpoint / 失败恢复最小策略；
   - 明确仍未实际启动全量。
6. 报告写入：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/36_1C-E16_全量前最终放行准备_Claude执行报告.md

边界：
不得进入全量 2664 姿态生成；不得训练；不得修改论文正文；不得修改冻结文件 13/14/24/25；不得写入 04_Codex审阅/；不得生成 Codex 裁决文件。
若输出过长或文件无法一次写完，按 Part 1/2/3 分段完成，直到报告完整。
```

---

## 8. Codex 暂定下一步

Claude 完成 1C-E16 后，作者将以下文件交回 Codex：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/36_1C-E16_全量前最终放行准备_Claude执行报告.md
```

Codex 下一轮判断：

```text
1. 两项全量前小修是否完成；
2. Step7c dry-run checker 是否仍 PASS；
3. full-run 命令、输出目录、expected-record-count、checkpoint/失败恢复边界是否明确；
4. 是否正式放行全量 2664 姿态生成。
```

在 R34 之后、R35 放行之前，仍不得直接启动全量 2664、训练或论文正文改写。
