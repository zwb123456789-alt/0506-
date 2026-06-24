# R33 Codex 审阅：1C-E15-FIX01 通过并规划 FIX02

最后更新：2026-06-24  
审阅端：Codex  
审阅对象：`04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/34_1C-E15-FIX01_checker路径解析修复_Claude执行报告.md`  
关联代码：`06_v0.4_code/06_manifest/check_manifest_consistency_v0_4.py`  
关联自测：`v0.4_results/00_validation/phase0_step7c_checker_test_fix01/`

---

## 1. 阶段判定

```text
1C-E15-FIX01：PASS
Phase 0 Step 7c：STILL NOT COMPLETE
全量 2664 姿态生成：NOT RELEASED
训练：NOT RELEASED
论文正文改写：NOT RELEASED
下一步：1C-E15-FIX02，执行 builder/matrix/mask 修复与 3 姿态物理 dry-run
```

FIX01 已完成 R32 要求的 checker 路径解析修复和自测。当前 checker 可以作为后续 Step7c dry-run 的一致性门禁基础。

但 Step7c 整体仍未完成，因为以下任务尚未执行：

```text
1. manifest builder 路径基准统一；
2. Blender 相机矩阵输出与 manifest 写入；
3. V_sun_macro mask 输出与 manifest 写入；
4. 3 姿态物理 dry-run；
5. dry-run manifest 通过 17 项 checker。
```

---

## 2. 复核结果

### 2.1 输出归位

已确认 FIX01 报告位于 R32 指定路径：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/34_1C-E15-FIX01_checker路径解析修复_Claude执行报告.md
```

已确认上一轮嵌套镜像目录与残留 Part1 文件不存在：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/项目重启_v0.4_BlenderOCS/  不存在
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/33_1C-E15_Phase0_Step7c_manifest小修与dryrun_Claude执行报告_Part1.md  不存在
```

### 2.2 checker 代码复核

`check_manifest_consistency_v0_4.py` 已完成 R32 要求：

```text
新增 --data-root，默认 "."
新增 --require-prefix
新增 --expected-record-count
report 写入 data_root_resolved / require_prefix / expected_record_count / check_count
文件头 docstring 更新为 17 项检查
路径解析不再从 ocs_manifest_path 反推项目根
路径结构检查包含相对路径、盘符绝对路径、POSIX 绝对路径、.. 越界、可选前缀
矩阵检查包含 4x4 结构与 16 元素 float(x) 可转性
records_completeness 支持 expected-record-count gate
```

### 2.3 Codex 复跑主自测

Codex 复跑命令：

```powershell
C:\Users\97466\.conda\envs\ocs_sim\python.exe 06_v0.4_code\06_manifest\check_manifest_consistency_v0_4.py `
  --ocs-manifest v0.4_results\00_validation\phase0_step7a_manifest_trial\ocs_manifest_v0_4_step6trial.json `
  --image-manifest v0.4_results\00_validation\phase0_step7a_manifest_trial\image_manifest_v0_4_step6trial.json `
  --step6-summary v0.4_results\00_validation\phase0_step6_small_trial\phase0_step6_small_trial_summary.json `
  --data-root . `
  --require-prefix v0.4_results/ `
  --output v0.4_results\00_validation\phase0_step7c_checker_test_fix01\codex_rerun_consistency_check_report.json
```

复跑结果：

```text
check_count = 17
overall_status = NOT_COMPLETE
checks 1-11 = PASS
path_base_consistency = FAIL，10 inconsistencies
ocs_paths_exist = PASS，0 missing，10 base-inconsistent
image_paths_exist = PASS，0 missing，0 base-inconsistent
camera_matrix_non_null_and_valid = FAIL，5 invalid
sun_visibility_mask_path_non_null_and_exists = FAIL，5 missing
records_completeness = INFO，gate 未启用
```

该结果符合预期：Step7a 旧 manifest 仍存在路径基准混用、矩阵 null、mask null；但真实存在的 image EXR/PNG 不再被误报 missing，R32-B1 已解决。

### 2.4 合成 fixture 自测

已读取并复核合成测试报告：

```text
report_clean.json       overall_status = PASS，17 项可达正向通过
report_clean_gate.json  expected_record_count = 2664 时 records_completeness = NOT_COMPLETE
report_badmatrix.json   可精确定位 camera_matrix_world[1][2] 与 sun_camera_matrix_world[0][0] 的非 float 值
report_badpath.json     可拦截 ../ 越界与 C:/ 盘符绝对路径
```

合成件带 `_synthetic` 标记，仅用于 checker 单元测试，不作为物理 dry-run 依据。R32-B6 已遵守。

---

## 3. 本轮裁决

| R32 项 | 裁决 |
|---|---|
| R32-B1 路径解析根错误 | PASS |
| R32-B2 路径结构 + 可选前缀 | PASS |
| R32-B3 矩阵 float 可转性 | PASS |
| R32-B4 completeness gate | PASS |
| R32-B5 不得声称 Step7c 完成 | PASS，报告已明确 Step7c 未完成 |
| R32-B6 synthetic 不得冒充物理 dry-run | PASS |
| 输出归位 | PASS |

---

## 4. 保留问题

FIX01 只修复 checker；以下仍是全量前 P0 阻断项：

```text
1. build_ocs_manifest_v0_4.py 仍未统一路径基准；
2. build_image_manifest_v0_4.py 仍未统一路径基准；
3. OCS manifest 仍无法读取/写入 camera_matrix_world 和 sun_camera_matrix_world；
4. shadow reprojection 尚未稳定输出 V_sun_macro mask 并写入 sun_visibility_mask_path；
5. dry-run 物理产物尚未生成；
6. 正式 dry-run manifest 尚未通过 17 项 checker。
```

因此仍不得进入全量 2664 姿态生成。

---

## 5. 给 Claude 的 FIX02 短提示词

```text
执行 1C-E15-FIX02：完成 Step7c 的 builder/matrix/mask 修复与 3 姿态物理 dry-run。

依据文件：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R33_Codex_审阅_1C-E15-FIX01通过并规划FIX02.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R32_Codex_审阅_1C-E15_Step7c未通过返工单.md
06_v0.4_code/06_manifest/check_manifest_consistency_v0_4.py
06_v0.4_code/06_manifest/build_ocs_manifest_v0_4.py
06_v0.4_code/06_manifest/build_image_manifest_v0_4.py

任务：
1. 修改 build_ocs_manifest_v0_4.py 和 build_image_manifest_v0_4.py，新增 --data-root 参数，所有 record 路径统一为项目根相对路径，并满足 checker 的 --require-prefix v0.4_results/。
2. 修改或新增最小必要 Blender/记录脚本，使 3 姿态 dry-run 能从真实 Blender 场景对象输出 camera_matrix_world 和 sun_camera_matrix_world，不得用 identity 或手工矩阵冒充正式 dry-run。
3. 修改或新增 shadow reprojection / mask 输出脚本，为 3 姿态输出 V_sun_macro mask，并写入 sun_visibility_mask_path。mask 路径必须是项目根相对路径。
4. 选择 R31 已指定的 3 个非 Step6 small-run 姿态：
   yaw045_pitch+000_roll+000
   yaw270_pitch-030_roll+000
   yaw135_pitch+000_roll+000
5. 执行完整 3 姿态物理 dry-run：必要小规模 Blender 渲染或复用已有 shadow pass + 矩阵日志 -> V_sun_macro mask -> BRDF/OCS/image 后处理 -> OCS/Image manifest -> checker。
6. checker 必须使用：
   --data-root .
   --require-prefix v0.4_results/
   --expected-record-count 3
7. dry-run 输出目录建议：
   v0.4_results/00_validation/phase0_step7c_dryrun_fix02/
8. 输出报告必须列出：
   - 修改文件清单；
   - 3 个姿态的实际产物路径；
   - camera_matrix_world / sun_camera_matrix_world 是否来自 Blender matrix_world 日志；
   - sun_visibility_mask_path 是否非空且文件存在；
   - checker 17 项结果；
   - 若仍无法完成 Blender/mask/dry-run，明确列阻断原因，不得声称 Step7c 完成。
9. 报告写入：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/35_1C-E15-FIX02_builder矩阵mask与dryrun_Claude执行报告.md

边界：
不得进入全量 2664 姿态生成；不得训练；不得修改论文正文；不得修改冻结文件 13/14/24/25；不得写入 04_Codex审阅/；不得生成 Codex 裁决文件。
若输出过长或文件无法一次写完，按 Part 1/2/3 分段完成，直到报告完整。
```

---

## 6. Codex 暂定下一步

Claude 完成 FIX02 后，作者将以下材料交回 Codex：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/35_1C-E15-FIX02_builder矩阵mask与dryrun_Claude执行报告.md
v0.4_results/00_validation/phase0_step7c_dryrun_fix02/consistency_check_report.json
```

Codex 下一轮判断：

```text
1. 3 姿态 dry-run 是否真实执行；
2. manifest 路径基准是否统一；
3. 矩阵是否来自 Blender 真实 matrix_world；
4. V_sun_macro mask 是否存在且与 manifest 对齐；
5. 17 项 checker 是否 PASS；
6. 是否具备进入全量前最后放行审阅的条件。
```

在 FIX02 未通过前，仍不更新 `CLAUDE.md` 为全量可执行，也不放行全量、训练或论文正文改写。
