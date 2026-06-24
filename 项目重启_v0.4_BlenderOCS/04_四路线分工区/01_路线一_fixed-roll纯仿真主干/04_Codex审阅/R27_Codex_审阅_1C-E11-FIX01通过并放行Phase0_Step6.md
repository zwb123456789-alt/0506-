# R27 Codex 审阅：1C-E11-FIX01 通过并放行 Phase 0 Step 6

最后更新：2026-06-23  
审阅端：Codex  
审阅对象：Claude 提交的 `28_1C-E11-FIX01_ortho_scale因子修正_Claude执行报告.md`

## 1. 审阅结论

```text
1C-E11-FIX01：PASS
Phase 0 Step 6：COMPLETE
Step 6 small-run 产物可作为后续 Step 7 / 全量前规划依据
不得直接进入全量 2664 姿态生成
```

本轮已修正 R26 后续审阅中发现的 `ortho_scale` 因子错误。`run_phase0_step6_small_trial.py` 已从错误的 `2.0 * r_max` 修正为 `2.2 * r_max`，与 13 号冻结规范、`config_v0_4.py` 和 Step 4/5 验证脚本保持一致。修正后的 5 姿态 OCS JSON 与 summary 已重新生成。

## 2. 核验证据

### 2.1 Claude 报告路径

标准目录中已存在：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/28_1C-E11-FIX01_ortho_scale因子修正_Claude执行报告.md
```

### 2.2 代码修正核验

目标文件：

```text
06_v0.4_code/05_postprocess/run_phase0_step6_small_trial.py
```

已核验：

```text
ortho_scale_m = 2.2 * r_max
pixel_area_m2 = (ortho_scale_m / resolution) ** 2
```

未检出旧的 `ortho_scale_m = 2.0 * r_max`。

### 2.3 Summary 数值核验

目标文件：

```text
v0.4_results/00_validation/phase0_step6_small_trial/phase0_step6_small_trial_summary.json
```

独立核验结果：

```text
overall = COMPLETE
ortho_scale_m = 3.239731375366906
expected_ortho = 3.239731375366906
pixel_area_m2 = 0.00016015410437830724
expected_area = 0.00016015410437830724
ortho_match = True
area_match = True
n_completed = 5
blockers = []
```

### 2.4 OCS 修正核验

5 个姿态的 `ocs_total` 已按正确面积尺度更新：

| 姿态 | 修正后 OCS | contributing |
|---|---:|---:|
| yaw180_pitch+000_roll+000 | 0.015744979323653596 | 2213 |
| yaw150_pitch+025_roll+000 | 0.047638793367835164 | 3435 |
| yaw000_pitch+000_roll+000 | 0.014416927756804448 | 1885 |
| yaw090_pitch+000_roll+000 | 0.0222607167063682 | 2785 |
| yaw300_pitch-025_roll+000 | 0.017791907426358 | 2972 |

`ocs_per_part` 求和与 `ocs_total` 的差异仅为浮点舍入量级。

## 3. 阶段门判定

Phase 0 Step 6 的验收项已满足：

- B0 BRDF/image 后处理模块入口已建立。
- OCS 积分模块入口已建立。
- 5 姿态 small-run 生成 `I_linear EXR`、log1p PNG、per-frame OCS JSON。
- 四类像素统计已输出。
- `I_scale_smallrun` 固定复用 Step 5 值，未使用 per-frame normalization。
- `pixel_area_m2` 已与 `ortho_scale = 2.2 × r_max` 对齐。
- 未进入全量 2664 姿态生成，未训练模型，未改写论文正文。

因此：

```text
Phase 0 Step 6 = COMPLETE
```

## 4. 非阻断边界记录

本轮仍是：

```text
B0 small-run
NOT full corpus
NOT training input final manifest
```

完整 manifest、全量 corpus-level `I_scale`、multi-geom 扩展、B1/GGX 分支升级和训练入口均未在本轮完成，不能用 Step 6 small-run 直接替代。

## 5. 下一步裁决

不建议直接进入全量 2664 姿态生成。下一步应先做 Phase 0 后续规划门：

```text
1C-E12：Phase 0 Step 7 / 全量前规划与风险清单
```

该任务应明确：

- 全量生成前还缺哪些模块与字段。
- 是否先补 manifest builder / consistency checker。
- B0 全量是否可先跑，B1/GGX 分支是否后置。
- corpus-level `I_scale` 的计算与冻结流程。
- 错误嵌套目录、单姿态 JSON 绝对路径等历史痕迹是否需要清理。
- 全量 2664 的耗时、磁盘、重跑策略和失败恢复策略。

## 6. 给 Claude 的下一步短提示词

```text
你是 Claude 执行端，只执行，不做 Codex 审阅或阶段裁决。

任务：执行 1C-E12，生成 Phase 0 Step 7 / 全量前规划与风险清单。不要进入全量 2664 姿态生成。

必须读取：
1. CLAUDE.md 的 1.1 执行环境与命令规则
2. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R27_Codex_审阅_1C-E11-FIX01通过并放行Phase0_Step6.md
3. 04_四路线分工区/00_总览与裁决/00_路线冻结文件区/04_BlenderOCS方法重建_全局方法冻结文件/13_v0.4前向模型冻结规范_最终冻结版.md
4. 04_四路线分工区/00_总览与裁决/00_路线冻结文件区/04_BlenderOCS方法重建_全局方法冻结文件/14_v0.4数据与manifest字段规范_最终冻结版.md
5. 06_v0.4_code/05_postprocess/run_phase0_step6_small_trial.py
6. v0.4_results/00_validation/phase0_step6_small_trial/phase0_step6_small_trial_summary.json

必须输出：
- 全量前缺口清单
- Step 7 候选任务拆分
- manifest builder / consistency checker 是否必须先做的判断
- corpus-level I_scale 计算流程
- B0/B1/GGX 分支顺序建议
- 全量生成资源与失败恢复策略
- 不进入全量生成的边界声明

输出报告写入：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/

禁止：
- 不得进入全量 2664 姿态生成。
- 不得训练模型。
- 不得改写论文正文。
- 不得修改 CLAUDE.md、13/14/24/25、路线冻结文件或书籍知识库。
- 不得写入 04_Codex审阅/。
- 不得生成 Codex、验收、最终放行等名义文件。
```

## 7. 本轮分流

Codex 审阅记录：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R27_Codex_审阅_1C-E11-FIX01通过并放行Phase0_Step6.md
```

稳定 Step 6 small-run 产物：

```text
06_v0.4_code/05_postprocess/image_response_v0_4.py
06_v0.4_code/05_postprocess/ocs_integration_v0_4.py
06_v0.4_code/05_postprocess/run_phase0_step6_small_trial.py
v0.4_results/00_validation/phase0_step6_small_trial/phase0_step6_small_trial_summary.json
v0.4_results/00_validation/phase0_step6_small_trial/
```

