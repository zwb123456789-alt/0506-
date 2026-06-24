# R32 Codex 审阅：1C-E15 Step7c 未通过返工单

最后更新：2026-06-24  
审阅端：Codex  
审阅对象：`33_1C-E15_Phase0_Step7c_manifest小修与dryrun_Claude执行报告.md`  
关联代码：`06_v0.4_code/06_manifest/check_manifest_consistency_v0_4.py`

---

## 1. 阶段判定

```text
1C-E15 / Phase 0 Step 7c：FAIL / NEEDS FIX01
全量 2664 姿态生成：NOT RELEASED
训练：NOT RELEASED
论文正文改写：NOT RELEASED
下一步：1C-E15-FIX01，修正 checker 路径解析与完成真正 Step7c dry-run
```

本轮不能判为 Step7c 通过。Claude 只完成了 consistency checker 的部分代码修改和后续方案撰写；R31 要求的 builder 修复、矩阵输出、V_sun_macro mask 输出和 3 姿态 dry-run 实际未执行。

此外，Codex 实测发现新增 checker 的路径存在性检查存在实现错误：真实存在的 `v0.4_results/...` 图像和 EXR 文件被误报为 missing。因此 checker 不能作为全量前门禁使用，必须返工。

---

## 2. 归位与边界问题

### 2.1 报告路径写入异常

R31 指定输出路径为：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/33_1C-E15_Phase0_Step7c_manifest小修与dryrun_Claude执行报告.md
```

但当前发现完整报告位于嵌套镜像路径：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/项目重启_v0.4_BlenderOCS/04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/33_1C-E15_Phase0_Step7c_manifest小修与dryrun_Claude执行报告.md
```

同时直接 `02_Claude输出/` 下还有一个 `33_..._Part1.md`。这说明 Claude 的输出路径处理不稳，后续必须归位为一个完整报告文件，不得继续产生项目根镜像嵌套目录。

### 2.2 本轮未越界进入全量

未发现进入全量 2664 姿态生成、训练或论文正文改写。但 Step7c 本身也未完成。

---

## 3. Codex 实测结果

Codex 使用 `ocs_sim` Python 对当前 Step7a manifest 运行修改后的 checker：

```powershell
C:\Users\97466\.conda\envs\ocs_sim\python.exe 06_v0.4_code\06_manifest\check_manifest_consistency_v0_4.py `
  --ocs-manifest v0.4_results\00_validation\phase0_step7a_manifest_trial\ocs_manifest_v0_4_step6trial.json `
  --image-manifest v0.4_results\00_validation\phase0_step7a_manifest_trial\image_manifest_v0_4_step6trial.json `
  --step6-summary v0.4_results\00_validation\phase0_step6_small_trial\phase0_step6_small_trial_summary.json `
  --output v0.4_results\00_validation\phase0_step7c_checker_test\consistency_check_report.json
```

运行结果：

```text
check_count = 17
overall_status = NOT_COMPLETE
checks 1-11 = PASS
path_base_consistency = FAIL，10 inconsistencies
ocs_paths_exist = FAIL，20 missing
image_paths_exist = FAIL，10 missing
camera_matrix_non_null_and_valid = FAIL，5 invalid
sun_visibility_mask_path_non_null_and_exists = FAIL，5 missing
records_completeness = INFO，5/5
```

其中矩阵和 mask 失败符合当前 Step7a manifest 的已知状态；但 `ocs_paths_exist` 与 `image_paths_exist` 的 missing 数量不可信，因为下列文件实际存在：

```text
v0.4_results/00_validation/phase0_step6_small_trial/yaw180_pitch+000_roll+000_linear.exr
v0.4_results/00_validation/phase0_step6_small_trial/yaw180_pitch+000_roll+000_brdf.png
v0.4_results/00_validation/shadow_passes/yaw180_pitch+000_roll+000_camera.exr
```

---

## 4. 阻断问题

### 4.1 R32-B1：checker 路径解析根目录错误

当前代码：

```python
data_root = os.path.dirname(os.path.dirname(ocs_manifest_path))  # 推断项目根
full_path = os.path.join(data_root, path)
```

当 `ocs_manifest_path` 是：

```text
v0.4_results/00_validation/phase0_step7a_manifest_trial/ocs_manifest_v0_4_step6trial.json
```

上述 `data_root` 实际变成：

```text
v0.4_results/00_validation
```

于是对 manifest 中已有的项目根相对路径：

```text
v0.4_results/00_validation/phase0_step6_small_trial/xxx.exr
```

会错误拼成：

```text
v0.4_results/00_validation/v0.4_results/00_validation/phase0_step6_small_trial/xxx.exr
```

导致真实存在的文件被误报 missing。

返工要求：

```text
1. checker 必须新增显式 --data-root 参数，默认可以是当前工作目录 "."，但不得从 manifest 文件路径反推项目根。
2. 所有路径存在性检查统一使用 Path(data_root) / manifest_path。
3. 允许 Windows 反斜杠输入，但报告中建议规范化为 POSIX "/"。
4. checker 输出 report 时记录 data_root_resolved。
```

### 4.2 R32-B2：path_base_consistency 写死 `v0.4_results/` 过窄

当前代码只允许路径以：

```text
v0.4_results/
```

开头。这个规则可用于当前 Step7c dry-run，但不应硬编码为唯一合法路径。14 号规范说的是 relative to v0.4 data root；R31 给出的建议是“统一为项目根相对路径，或显式 data_root 后全部相对 data_root”。

返工要求：

```text
1. 若采用项目根相对路径，可要求当前阶段路径以 v0.4_results/ 开头。
2. 但 checker 的提示必须写清这是当前 Phase0 数据布局约束，而不是永久 schema 规则。
3. 更稳妥做法：检查路径是否全部为相对路径、是否不含绝对盘符、是否不含 .. 越界、是否能相对 data_root 解析存在；是否要求 v0.4_results/ 可作为 --require-prefix 参数。
```

### 4.3 R32-B3：矩阵 4x4 检查未验证 float 可转性

R31 要求矩阵字段不仅要非空和 4x4，还要所有元素可转 float。当前 checker 只检查 list 和长度，没有检查元素数值类型。

返工要求：

```text
对 camera_matrix_world 和 sun_camera_matrix_world 的 16 个元素逐个 float(x) 校验；
失败时报告 record_id、字段名、行列位置和值。
```

### 4.4 R32-B4：records_completeness 只是 INFO，不足以作为 full-run final gate

R31 要求最小 completeness gate。当前检查 17 只输出 INFO，且 `n_total_expected` 默认等于当前 records 数，因此无法发现“预期 2664、当前 1000”的未完成状态，除非 manifest 手动写入 `n_total_expected`。

返工要求：

```text
1. checker 增加可选 --expected-record-count 参数。
2. 若 manifest 顶层存在 n_total_expected，或 CLI 传入 expected-record-count，则当前 records 数不足时应 FAIL / NOT_COMPLETE。
3. 若二者都没有，则保持 INFO，但报告中写明 completeness gate 未启用。
```

### 4.5 R32-B5：builder 修复与 dry-run 未执行

Claude 报告明确写了：

```text
Manifest builder 路径基准统一修复：待执行
Blender 脚本输出相机矩阵：待执行
Shadow reprojection 脚本创建与 V_sun_macro mask 输出：待执行
3 姿态 dry-run 实际执行：待执行
```

这与 R31 对 Step7c 的要求不一致。Step7c 不是只写方案，而是要求小修并执行 3 姿态 dry-run。

返工要求：

```text
FIX01 必须至少完成 checker 修正并通过 checker 自测。
若当前执行端无法运行 Blender 或无法完成 dry-run，应明确报告“Step7c 未完成，停在 checker 修复阶段”，不得写“本报告已完整覆盖 R31 指定 9 项任务”。
```

### 4.6 R32-B6：不得手动构造相机矩阵 JSON 当作正式 dry-run 依据

报告提出“手动构造矩阵 JSON（如果矩阵是固定的）”。这条不能作为正式 dry-run 通过依据。R31 已明确要求不要用 identity 或占位矩阵冒充真实输出。

返工要求：

```text
矩阵必须来自 Blender 场景对象的 matrix_world 日志，或来自可复核的渲染脚本输出。
若仅为 checker 单元测试，可构造 synthetic manifest，但必须标记为 synthetic，不得作为物理 dry-run 通过依据。
```

---

## 5. 对本轮已完成工作的裁决

| 项目 | 裁决 |
|---|---|
| checker 新增 6 项检查 | 部分完成，但路径解析和 completeness gate 不合格 |
| checker 实测运行 | 可运行，但误报真实存在文件 missing |
| builder 路径基准统一 | 未执行，仅方案 |
| Blender 矩阵输出 | 未执行，仅方案 |
| V_sun_macro mask 输出 | 未执行，仅方案 |
| 3 姿态 dry-run | 未执行，仅方案 |
| BRDF 命名边界修正 | 文档方案可接受，代码未修 |
| I_scale 5 姿态说明 | 文档方案可接受 |
| 输出路径归位 | 不合格，生成嵌套镜像路径 |

---

## 6. 给 Claude 的 FIX01 短提示词

```text
执行 1C-E15-FIX01：修复 Step7c checker 实现问题，并重新输出归位报告。

依据文件：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R32_Codex_审阅_1C-E15_Step7c未通过返工单.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R31_Codex_审阅_1C-E14_Step7b条件通过并要求Step7c.md
06_v0.4_code/06_manifest/check_manifest_consistency_v0_4.py

任务：
1. 修复 check_manifest_consistency_v0_4.py 的路径解析：新增 --data-root 参数，默认 "."；所有 manifest record 路径相对 data_root 解析，不得从 ocs_manifest_path 反推项目根。
2. 修复路径存在性误报：用当前 Step7a manifest 自测时，已经真实存在的 image EXR/PNG 不得被误报 missing；camera_exr_path/sun_depth_exr_path 由于当前基准混用可继续由 path_base_consistency 拦截，但路径存在性报告必须能区分“基准不一致”和“文件真实缺失”。
3. path_base_consistency 不要硬写成永久 schema；当前 Phase0 可要求 v0.4_results/ 前缀，但请在 report 中说明这是当前数据布局约束，或实现 --require-prefix v0.4_results/。
4. 矩阵检查补充 16 个元素 float 可转性验证。
5. records_completeness 增加 --expected-record-count 可选参数；启用时记录数不足必须 FAIL / NOT_COMPLETE；未启用时保持 INFO 并说明 completeness gate 未启用。
6. 更新 checker 文件头部检查项说明，使其包含 17 项，不要停留在旧 9 项。
7. 运行 checker 自测，输出到：
   v0.4_results/00_validation/phase0_step7c_checker_test_fix01/consistency_check_report.json
8. 将完整执行报告写入正确路径：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/34_1C-E15-FIX01_checker路径解析修复_Claude执行报告.md
   不得再次写入嵌套的 项目重启_v0.4_BlenderOCS/... 镜像路径。

边界：
不得进入全量 2664 姿态生成；不得训练；不得修改论文正文；不得修改冻结文件 13/14/24/25；不得写入 04_Codex审阅/；不得生成 Codex 裁决文件。

说明：
本次 FIX01 只要求修复 checker 并自测通过“检查逻辑正确”。如果无法完成 builder 修复和 3 姿态 dry-run，不要声称 Step7c 完成；报告中明确写“Step7c 仍未完成，下一步需执行 builder/matrix/mask/dry-run”。
```

---

## 7. Codex 暂定下一步

Claude 完成 FIX01 后，作者将以下文件交回 Codex：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/34_1C-E15-FIX01_checker路径解析修复_Claude执行报告.md
v0.4_results/00_validation/phase0_step7c_checker_test_fix01/consistency_check_report.json
```

Codex 下一轮只审：

```text
1. checker 路径解析是否不再误报已存在文件；
2. 新增 17 项检查是否结构正确；
3. completeness gate 是否可用于 full-run final 模式；
4. 是否进入下一轮 Step7c-FIX02，执行 builder/matrix/mask/dry-run。
```

在 FIX01 未通过前，仍不得放行全量 2664、训练或论文正文改写。
