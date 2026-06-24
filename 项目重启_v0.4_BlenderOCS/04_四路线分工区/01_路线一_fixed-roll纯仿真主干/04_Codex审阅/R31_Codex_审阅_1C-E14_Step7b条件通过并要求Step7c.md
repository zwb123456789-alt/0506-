# R31 Codex 审阅：1C-E14 Step7b 条件通过并要求 Step7c

最后更新：2026-06-24  
审阅端：Codex  
审阅对象：`04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/32_1C-E14_Phase0_Step7b_全量前入口检查与字段补齐规划_Claude执行报告.md`  
关联产物：`v0.4_results/00_validation/phase0_step7a_manifest_trial/`

---

## 1. 阶段判定

```text
1C-E14 / Phase 0 Step 7b：CONDITIONAL PASS
全量 2664 姿态生成：NOT RELEASED
训练：NOT RELEASED
论文正文改写：NOT RELEASED
下一步：1C-E15 / Phase 0 Step 7c，全量前 manifest builder/checker 小修与 3 姿态 dry-run
```

Claude 本轮报告完成了 R30 指定的主要任务：检查 Step 7a manifest 中的空字段，给出字段补齐裁决，排查 builder/checker 缺失功能，并形成风险清单与最小修复建议。报告可作为 Step 7b 的规划依据。

但该报告仍有两个需要 Codex 补充裁决的点：

```text
1. 当前 OCS manifest 路径基准混用，报告只泛称“路径存在性检查”，未单独列为阻断风险。
2. BRDF 参数文件示例把 B1 与 ggx_cook_torrance 绑在一起，容易冲掉路线一 C 的 B1/GGX 分工边界。
```

因此本轮只判定 Step 7b 规划条件通过，不放行全量；必须先执行 Step 7c 小修和 dry-run。

---

## 2. 复核依据

### 2.1 Step 7a manifest 当前状态

独立读取 `ocs_manifest_v0_4_step6trial.json` 后确认：

```text
sun_visibility               = camera_visible_nol_plus_sun_shadow_pass
shadow_mapping_method        = sun_view_depth_reprojection
camera_matrix_world          = null
sun_camera_matrix_world      = null
position_exr_path            = null
sun_visibility_mask_path     = null
n_pixels_per_part            = 已有 per-part dict
```

这与 Claude 报告中字段状态判断基本一致。

### 2.2 规范约束

14 号 manifest 规范要求：

```text
camera_exr_path              relative to v0.4 data root
position_exr_path            string or null；null 表示由 depth + camera matrix 重建
sun_depth_exr_path           string or null；null if sun_visibility == camera_visible_nol
sun_visibility_mask_path     string or null；null if sun_visibility == camera_visible_nol
camera_matrix_world          float[4][4]
sun_camera_matrix_world      float[4][4]
```

13 号前向模型规范要求：

```text
主线优先实现 Level 2: camera_visible_nol_plus_sun_shadow_pass
camera-view pixel -> world point -> sun-view depth comparison -> V_sun_macro
输出 V_sun_macro_mask，并写入 manifest 的 sun_visibility_mask_path
矩阵方向必须为 camera/sun camera local -> world，重投影时使用逆矩阵
```

因此在当前 Level 2 shadow pass 层级下，矩阵和 mask 路径不能作为全量正式 manifest 的空字段保留。

### 2.3 代码状态

复核 `06_v0.4_code/06_manifest/build_ocs_manifest_v0_4.py` 后确认：

```text
camera_matrix_world / sun_camera_matrix_world 当前由 main() 传入 None
position_exr_path 当前写死为 None
sun_visibility_mask_path 当前写死为 None
camera_exr_path / sun_depth_exr_path 使用一个相对基准
exr_path / png_path 直接沿用 summary 中另一个相对基准
```

复核 `check_manifest_consistency_v0_4.py` 后确认：

```text
已有 11 项检查
已有 brdf_model_match
已有 brdf_model_vs_brdf_version_consistency
尚无路径存在性检查
尚无 camera_matrix_world / sun_camera_matrix_world 非空和 4x4 形状检查
尚无 sun_visibility_mask_path 非空与存在性检查
尚无 manifest 路径基准一致性检查
```

---

## 3. Codex 补充发现

### 3.1 P0：manifest 路径基准混用必须修复

当前 OCS manifest 中同一 record 同时出现两类路径：

```text
camera_exr_path = 00_validation/shadow_passes/yaw180_pitch+000_roll+000_camera.exr
sun_depth_exr_path = 00_validation/shadow_passes/yaw180_pitch+000_roll+000_sun.exr
exr_path = v0.4_results/00_validation/phase0_step6_small_trial/yaw180_pitch+000_roll+000_linear.exr
png_path = v0.4_results/00_validation/phase0_step6_small_trial/yaw180_pitch+000_roll+000_brdf.png
```

实际文件位于：

```text
v0.4_results/00_validation/shadow_passes/yaw180_pitch+000_roll+000_camera.exr
v0.4_results/00_validation/shadow_passes/yaw180_pitch+000_roll+000_sun.exr
```

若按项目根解析 `camera_exr_path`，路径不存在；若按 `v0.4_results` 解析，又与 `exr_path/png_path` 的写法不一致。全量前必须统一 manifest 的路径基准，并让 builder/checker 使用同一个 `data_root` 解析全部路径。

裁决：

```text
Step 7c 必须将路径基准混用列为 P0 修复项。
建议所有 manifest record 路径统一为项目根相对路径，或显式写入 data_root 并统一相对该 data_root。
不得继续让不同字段使用不同隐含根目录。
```

### 3.2 P0：矩阵字段必须补齐并做结构检查

Claude 对 `camera_matrix_world` 和 `sun_camera_matrix_world` 的阻断判断正确。Step 7c 不仅要检查非空，还要检查：

```text
字段为 list
外层长度 = 4
每行长度 = 4
所有元素可转 float
矩阵方向仍按 camera/sun camera local -> world
```

若 Blender 渲染脚本还不能输出矩阵日志，则 Step 7c 应先修脚本输出矩阵 JSON，而不是在 manifest 中填 identity 占位。

### 3.3 P0：sun_visibility_mask_path 必须在 Level 2 下非空并存在

Claude 对 `sun_visibility_mask_path` 的阻断判断正确。因为当前 `sun_visibility` 是：

```text
camera_visible_nol_plus_sun_shadow_pass
```

此时 `sun_visibility_mask_path = null` 不符合 13/14 号规范的可追踪要求。Step 7c 至少要做到：

```text
1. shadow reprojection 输出与 camera-view 对齐的 V_sun_macro mask。
2. manifest 记录该 mask 路径。
3. checker 在 Level 2/Level 3 下要求 mask 路径非空且文件存在。
4. dry-run 中抽查 mask 像素和 n_pixels_sun_visible / n_pixels_contributing 的关系。
```

存储格式可先用 PNG 或 NPY，但必须在 manifest 和 checker 中保持一致。若同时输出 PNG+NPY，应明确哪个路径写入 `sun_visibility_mask_path`。

### 3.4 P1：BRDF 正式命名检查需要修正表述

Claude 报告建议添加 BRDF 参数文件验证，这个方向可以接受；但报告中示例：

```text
brdf_params_B1_ggx_cook_torrance.json
```

不宜照搬。当前路线一 C 的分工是：

```text
B0 = 工程 baseline / smoke test
B1 = 书中改进冯模型待确认主线
GGX = 对照与 mismatch 分支
```

因此 Step 7c 的 BRDF 命名检查应采用中性字段和分支映射，不要把 B1 默认命名为 GGX。建议：

```text
brdf_branch
brdf_model
brdf_params_version
brdf_params_path
```

并用显式映射表校验：

```text
B0/provisional/phong_like -> phong_like_provisional_baseline
B1/improved_phong        -> improved_phong_book_model_pending_author_confirmation（或作者确认后的正式名）
GGX/ggx                  -> ggx_cook_torrance
```

B1 正式公式和材料对应关系未经作者确认前，不得在全量正式产物中伪装为已最终冻结的正式物理模型。

### 3.5 P1：断点续跑需要最小可用机制，不要求完整 append/finalize 框架一次做完

Claude 将断点续跑列为 P1 是合理的。考虑当前阶段仍在全量前入口，Step 7c 的最低要求是：

```text
渲染/后处理产物可按 record_id 判定 COMPLETE / MISSING / FAILED
manifest builder 可跳过缺失或失败项并输出 NOT_COMPLETE，或在 final 模式下直接失败
consistency checker 能报告 n_total_expected、n_records_current、missing_records、failed_records
```

完整 `--append / --partial / --finalize` 可以作为增强项，不必阻塞 Step 7c 小修；但全量正式启动前至少要有 checkpoint 或 manifest completeness gate。

### 3.6 P1：I_scale 策略不能写成“20 姿态校准”

Claude 报告第 3.2.2 写到 Step 5 已用 20 姿态校准 I_scale，这与当前可复核的 Step 5 summary 不一致。`v_sun_macro_image_check_summary.json` 显示：

```text
selected_attitudes = 5
i_scale_step5 = 0.5444863931551639
i_scale_policy = fixed = max(I_without_vsun over 5 attitudes); no per-frame normalization
```

Step 7c 中可暂时沿用 `i_scale_step5 = 0.5444863931551639`，但说明必须改为“来自 Step 5 的 5 姿态 image impact validation”，不得写成 20 姿态校准。若后续 full-run 出现更高 `I_linear`，再在 Phase 1 做全局重标定或保留饱和审计。

---

## 4. 对 Claude 报告的逐项裁决

| 项目 | Codex 裁决 |
|---|---|
| 字段状态检查 | 基本通过 |
| `camera_matrix_world` / `sun_camera_matrix_world` 必须补齐 | 通过，且 Step 7c 要加 4x4 结构检查 |
| `position_exr_path` 可保持 null | 通过，但前提是 depth + camera matrix 重建链已验证 |
| `sun_visibility_mask_path` 必须补齐 | 通过 |
| builder 路径存在性检查 | 通过，但需升级为路径基准统一 + 存在性检查 |
| checker 矩阵/mask 检查 | 通过 |
| 断点续跑策略 | 方向通过，Step 7c 先做最小 completeness gate |
| BRDF 参数文件验证 | 方向通过，但不得使用 B1=GGX 的示例命名 |
| I_scale 策略 | 可暂沿用 Step 5 值，但报告中的“20 姿态”依据需修正为“5 姿态” |
| Step 7c dry-run 建议 | 通过，必须执行 |

---

## 5. 给 Claude 的下一步短提示词

```text
执行 1C-E15：Phase 0 Step 7c，全量前 manifest builder/checker 小修与 3 姿态 dry-run。

依据文件：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R31_Codex_审阅_1C-E14_Step7b条件通过并要求Step7c.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/32_1C-E14_Phase0_Step7b_全量前入口检查与字段补齐规划_Claude执行报告.md
06_v0.4_code/06_manifest/
v0.4_results/00_validation/phase0_step7a_manifest_trial/

任务：
1. 不进入全量 2664 生成，只做全量前小修和 3 姿态 dry-run。
2. 修复 manifest 路径基准混用：统一 camera_exr_path、sun_depth_exr_path、exr_path、png_path、sun_visibility_mask_path 的解析根；建议统一为项目根相对路径，或显式 data_root 后全部相对 data_root。
3. 修改 Blender / shadow pass / 后处理链的最小必要脚本，使 dry-run 能输出 camera_matrix_world、sun_camera_matrix_world，并由 OCS manifest 写入 4x4 矩阵。
4. 输出 V_sun_macro mask，并让 OCS manifest 写入 sun_visibility_mask_path；checker 在 Level 2/3 下检查 mask 路径非空且文件存在。
5. 修改 checker：新增路径存在性检查、路径基准一致性检查、矩阵非空与 4x4 结构检查、mask 路径非空检查、records 完整性/缺失项报告。
6. BRDF 检查只做分支与模型名一致性，不得把 B1 默认写成 GGX；B1 仍是书中改进冯模型待作者确认，GGX 只是对照/mismatch 分支。
7. I_scale 说明修正为沿用 Step 5 的 5 姿态 image impact validation 值 i_scale_step5 = 0.5444863931551639，不得写成 20 姿态校准。
8. 选择 3 个未在 Step 6 small-run 中出现的新姿态，执行完整 dry-run：Blender 渲染/或必要小规模重渲染 -> shadow reprojection -> BRDF 后处理 -> manifest 构建 -> consistency check。
9. 输出 dry-run 报告，列出每个 record 的矩阵、mask、路径存在性、checker 新增检查结果、失败/缺失记录。

输出文件：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/33_1C-E15_Phase0_Step7c_manifest小修与dryrun_Claude执行报告.md

边界：
不得进入全量 2664 姿态生成；不得训练；不得修改论文正文；不得修改冻结文件 13/14/24/25；不得写入 04_Codex审阅/；不得生成 Codex 裁决文件。
若输出过长或文件无法一次写完，按 Part 1/2/3 分段完成，直到报告完整。
```

---

## 6. Codex 暂定下一步

Claude 完成 Step 7c 后，作者将以下文件交回 Codex 审阅：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/33_1C-E15_Phase0_Step7c_manifest小修与dryrun_Claude执行报告.md
```

Codex 下一轮判断：

```text
1. Step 7c dry-run 是否 PASS；
2. manifest builder/checker 是否具备全量前门禁；
3. 是否仍需 FIX01；
4. 是否具备放行全量 2664 姿态生成的最低条件。
```

在 Step 7c 未通过前，仍不更新 `CLAUDE.md` 为“全量可执行”，也不放行全量、训练或论文正文改写。
