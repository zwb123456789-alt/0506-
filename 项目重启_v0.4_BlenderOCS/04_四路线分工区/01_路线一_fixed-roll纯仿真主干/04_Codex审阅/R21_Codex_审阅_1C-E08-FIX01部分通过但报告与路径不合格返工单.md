# R21 Codex 审阅：1C-E08-FIX01 部分通过但报告与路径不合格返工单

最后更新：2026-06-23  
审阅端：Codex  
审阅对象：Claude 提交的 `1C-E08-FIX01_shadow_validation修复与重验证`

## 1. 审阅结论

```text
1C-E08-FIX01：PARTIAL_PASS
Phase 0 Step 4：暂不放行
DEPTH_EPSILON_M_FINAL：暂不批准写入冻结/manifest
不得进入 Phase 0 Step 5
```

本轮确实修复了 R20 中最关键的一部分：`shadow_validation_summary.json` 已从旧的“只检查前景像素非零”更新为包含投影匹配与 `depth_error` 分布的结果。  
但仍存在两个阻断项：校准报告没有更新，Claude 执行报告写入了错误的嵌套项目目录。

## 2. 审阅输入

用户提交清单：

```text
06_v0.4_code/10_validation/validate_shadow_consistency_fixed.py
v0.4_results/00_validation/shadow_validation/shadow_validation_summary.json
v0.4_results/00_validation/shadow_validation/depth_epsilon_calibration_report.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/21_1C-E08-FIX01_shadow_validation修复与重验证_Claude执行报告.md
```

实际核验发现：标准输出目录中不存在用户所列执行报告；报告实际写入了嵌套错误目录：

```text
项目重启_v0.4_BlenderOCS/04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/21_1C-E08-FIX01_shadow_validation修复与重验证_Claude执行报告.md
```

标准目录下缺失：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/21_1C-E08-FIX01_shadow_validation修复与重验证_Claude执行报告.md
```

## 3. 已通过项

### 3.1 验证脚本新增投影匹配逻辑

文件：

```text
06_v0.4_code/10_validation/validate_shadow_consistency_fixed.py
```

当前脚本新增了：

- `get_sun_camera_params(r_max)`
- `world_to_sun_pixel(...)`
- camera-view 前景点到 sun-view 像素的投影匹配
- `depth_sun_actual_matched`
- `depth_sun_expected`
- `depth_error = depth_sun_actual_matched - depth_sun_expected`

判定：通过。

### 3.2 `shadow_validation_summary.json` 已包含真实误差字段

文件时间：

```text
v0.4_results/00_validation/shadow_validation/shadow_validation_summary.json
LastWriteTime: 2026-06-23 20:16:17
```

核心统计：

```text
attitudes_validated: 20
pass_count: 20
warn_count: 0
fail_count: 0
depth_epsilon_suggested: 0.7952109582768545
calibration_method: mean(abs_p99) across all attitudes
matched_point_count: min 917, mean 2842.15
abs_p99: mean 0.7952109582768545, max 1.3351661015404772
```

结果字段包含：

```text
projection_stats
depth_error.matched_point_count
depth_error.mean
depth_error.std
depth_error.abs_mean
depth_error.abs_p95
depth_error.abs_p99
depth_error.abs_max
pass_threshold_used
```

判定：通过。  
备注：`pass_threshold_used` 仍为 `0.001`，但最终建议 epsilon 在 summary 顶层给出为 `0.7952109582768545`。后续报告中必须解释清楚二者关系，避免误导。

### 3.3 未发现新 Codex 裁决文件

本轮未发现 Claude 在标准 `04_Codex审阅/` 下新增 `R21_Codex...` 或验收/最终放行文件。

判定：通过。

## 4. 阻断项

### B1. 校准报告仍是旧报告，未按 FIX01 结果更新

严重性：阻断

文件：

```text
v0.4_results/00_validation/shadow_validation/depth_epsilon_calibration_report.md
```

文件时间：

```text
LastWriteTime: 2026-06-23 20:06:22
```

该报告仍写：

```text
建议最终阈值：7.4852e-01 m
校准方法：基于 20 个代表姿态的 sun depth 统计，采用 3-sigma 准则
DEPTH_EPSILON_M_FINAL = 7.4852e-01 m
```

这正是 R20 已判定错误的旧方法。它没有使用 20:16 生成的真实 `depth_error.abs_p99` 结果，也没有写入新的：

```text
DEPTH_EPSILON_M_FINAL = 0.7952109582768545 m
calibration_method = mean(abs_p99) across all attitudes
```

判定：不通过。

### B2. Claude 执行报告写入了错误嵌套项目目录

严重性：阻断

错误目录：

```text
项目重启_v0.4_BlenderOCS/项目重启_v0.4_BlenderOCS/...
```

这违反 `CLAUDE.md` 的项目根目录规则，也说明 Claude 仍存在工作目录理解错误。标准 `02_Claude输出/` 下没有本轮 `21_...` 报告。

判定：不通过。

### B3. 当前不能进入 Step 5

严重性：阻断

尽管核心 JSON 已接近可用，但阶段交付包仍不完整：校准报告错误、执行报告路径错误。因此不能宣布 Phase 0 Step 4 COMPLETE，也不能进入 `V_sun_macro reprojection`。

判定：不通过。

## 5. 返工要求：1C-E08-FIX02

本轮不需要重渲染 40 个 EXR。只做报告与路径修复，除非 Claude 自查发现 summary 与脚本不一致。

必须完成：

1. 使用当前新的 `shadow_validation_summary.json` 重新生成 `depth_epsilon_calibration_report.md`。
2. 报告必须写入 `DEPTH_EPSILON_M_FINAL = 0.7952109582768545 m`，并说明来自 `mean(abs_p99) across all attitudes`。
3. 报告必须删除/替换旧的 `0.7485 m` 和 “sun depth 标准差 3-sigma” 口径。
4. 将 Claude 执行报告移动或重写到标准目录：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/21_1C-E08-FIX01_shadow_validation修复与重验证_Claude执行报告.md
```

5. 不得再写入嵌套目录：

```text
项目重启_v0.4_BlenderOCS/项目重启_v0.4_BlenderOCS/
```

6. 输出一份新的 Claude FIX02 报告到标准 `02_Claude输出/`，说明只修复报告与路径，不做阶段裁决。

## 6. 给 Claude 的返工短提示词

```text
你是 Claude 执行端，只执行，不做 Codex 审阅或阶段裁决。

任务：执行 1C-E08-FIX02，只修复报告与路径问题，不重渲染，不进入 Step 5。

必须读取：
1. CLAUDE.md 的 1.1 执行环境与命令规则
2. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R21_Codex_审阅_1C-E08-FIX01部分通过但报告与路径不合格返工单.md
3. v0.4_results/00_validation/shadow_validation/shadow_validation_summary.json
4. v0.4_results/00_validation/shadow_validation/depth_epsilon_calibration_report.md

当前判定：
- validate_shadow_consistency_fixed.py 和新的 shadow_validation_summary.json 基本通过。
- depth_epsilon_calibration_report.md 仍是旧报告，必须重生成。
- 21_Claude 执行报告被写入了错误嵌套目录，必须放回标准 02_Claude输出。

必须执行：
1. 以项目根目录为工作目录：
   D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS
2. 基于当前 shadow_validation_summary.json 重新生成 depth_epsilon_calibration_report.md。
3. 报告必须使用：
   DEPTH_EPSILON_M_FINAL = 0.7952109582768545 m
   calibration_method = mean(abs_p99) across all attitudes
4. 报告中不得再出现 0.7485 m 作为推荐最终阈值。
5. 将 21_1C-E08-FIX01_shadow_validation修复与重验证_Claude执行报告.md 写入标准目录：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
6. 新增 FIX02 执行报告到同一标准目录。

禁止：
- 不得进入 Phase 0 Step 5。
- 不得重渲染 40 个 EXR。
- 不得进入全量 2664 姿态。
- 不得训练模型。
- 不得修改 CLAUDE.md、13/14/24/25、路线冻结文件或书籍知识库。
- 不得写入 04_Codex审阅/。
- 不得生成以 Codex、R22_Codex、验收、最终放行为名义的文件。

输出状态：
- 若报告和路径均修复，写 COMPLETE。
- 若无法确认项目根目录或无法写入标准目录，写 NOT_COMPLETE 并列阻断项。
```

## 7. 本轮分流

本轮不生成成果区稳定成果索引，因为 Phase 0 Step 4 尚未完整通过。

返工审阅文件：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R21_Codex_审阅_1C-E08-FIX01部分通过但报告与路径不合格返工单.md
```

