# R133 Codex 任务单：P2 sparse 3-axis grid

最后更新：2026-07-01  
任务类型：给执行端 Claude 的长程 sparse grid 任务提示词  
上游阶段门：R132 已通过 002，P1 seed-roll smoke 接收  
当前状态：放行 P2 sparse 3-axis grid；不放行 P3/P4、roll-aware 训练或 R128

执行端报告必须写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/003_P2_sparse_3axis_grid_Claude执行报告.md
```

所有新结果写入：

```text
v0.4_results/20_three_axis_p2_sparse_grid/
```

本文件是 Codex 调度/提示词文件，保留在本路线 `04_Codex审阅/`。执行端不得把报告、结果或裁决文件写入 `04_Codex审阅/`。

---

## 0. 给 Claude 的总提示词

你现在执行三轴小项目第二阶段：

```text
three_axis_p2_sparse_3axis_grid
```

R132 已接收 P1 seed-roll smoke，证明 seed-roll 渲染/后处理/roll 曲线链路跑通，并观察到最亮构型 roll 稳健但低对比、高 |pitch| 暗构型 roll 敏感。你的任务是在受控规模内构建 sparse 3-axis grid，验证这些观察是否在局部三轴邻域保持，并产生 P3 local refinement 候选。

本轮不训练，不启动 P3/P4，不启动 R128。

---

## 1. 当前允许与禁止

允许：

```text
1. 读取 18/19 号包、R130/R132 成果摘要与 P1 表。
2. 新增派生渲染、后处理、汇总与制图脚本。
3. 执行受控 sparse 3-axis grid 渲染与后处理。
4. 计算 OCS magnitude、rank、local contrast、roll sensitivity、glint/saturation、image usability。
5. 生成 P3 local refinement 候选清单。
```

禁止：

```text
1. 不启动 P3 local refinement。
2. 不启动 P4 最亮构型与光路解释综合。
3. 不训练任何模型，不做 roll-aware neural model。
4. 不启动 R128、新路线二、GEO 真实数据处理、路线二/三/四或 T3/L2。
5. 不改旧脚本、旧 metrics、旧 samples、旧结果目录 10-19。
6. 不改姿态网格、OBS_GEOMETRIES、split、backbone 或超参。
7. 不写成果区，不生成 Codex 审阅文件，不改 CLAUDE.md。
8. 不把 P2 写成三轴小项目完成或真实未知目标反演系统。
```

---

## 2. 必读文件

按顺序读取并在报告列出：

```text
CLAUDE.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R132_Codex_审阅_002通过_P1_seed_roll_smoke接收并放行P2_sparse_grid.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/01_P1_seed_roll_smoke_R132通过.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/02_三轴小项目后续技术路线执行框架_R132通过.md
v0.4_results/19_three_axis_p1_seed_roll_scan/tables/p1_roll_sensitivity_summary.csv
v0.4_results/19_three_axis_p1_seed_roll_scan/tables/p1_brightness_information_smoke.csv
v0.4_results/19_three_axis_p1_seed_roll_scan/tables/p1_next_step_recommendations.csv
```

---

## 3. 子任务 A：P2 sparse grid 预注册

建议区域：

```text
R1 high-info：yaw around 240，pitch around +20/+30。
R2 dark / roll-sensitive：yaw around 285，pitch around -70/-85。
R3 low-info / ocs-hard：yaw around 065，pitch around +70/+75。
R4 bright / robust-easy：yaw around 145/150，pitch around +10/+15。
R5 neutral controls：从固定 roll 中等亮度/中等 contrast 区选少量姿态。
```

建议 sparse 网格：

```text
yaw offsets: center +/- {0,5,10}
pitch offsets: center +/- {0,5,10}
roll values: {-60,-45,-30,-15,0,+15,+30,+45,+60}
```

为控制规模，必须合并重复姿态并给出最终渲染单位数。若规模超过 2500 渲染单位，需裁剪到优先区域并报告原因。

必须输出：

```text
audit/p2_input_manifest.csv
tables/p2_sparse_grid_pre_registered_matrix.csv
tables/p2_region_definition.csv
audit/p2_redline_precheck.csv
```

## 4. 子任务 B：P2 渲染与后处理

必须输出：

```text
render/p2_render_manifest.csv
postprocess/p2_postprocess_manifest.csv
logs/p2_render_postprocess.log
```

要求：

```text
1. 所有姿态有 yaw/pitch/roll/region/category/source_seed。
2. 渲染与后处理采用与 P1/路线一一致量纲和配置。
3. 失败不能静默跳过，必须列失败列表和原因。
```

## 5. 子任务 C：P2 三轴指标与区域图

必须输出：

```text
tables/p2_sparse_grid_metrics.csv
tables/p2_region_summary.csv
tables/p2_high_brightness_candidates.csv
tables/p2_high_information_candidates.csv
tables/p2_low_information_regions.csv
tables/p2_p3_refinement_candidates.csv
metrics/p2_metric_definitions_used.md
```

至少计算：

```text
ocs_total；
brightness_rank；
local_contrast in yaw/pitch/roll neighborhood；
roll_sensitivity_score；
rank_shift；
glint/saturation flag；
image_usable flag；
region utility score；
```

## 6. 子任务 D：图表与解释

必须输出：

```text
figures/p2_sparse_grid_brightness_map.png/.pdf
figures/p2_sparse_grid_information_proxy_map.png/.pdf
figures/p2_region_roll_sensitivity_panel.png/.pdf
figures/p2_brightness_vs_information_scatter.png/.pdf
text/p2_sparse_grid_summary.md
```

## 7. 子任务 E：验收矩阵与下一步建议

必须输出：

```text
tables/p2_gate_matrix.csv
tables/p2_next_step_recommendations.csv
audit/generated_files_manifest.csv
audit/numeric_path_consistency_check.csv
audit/redline_self_check.csv
text/codex_review_checklist_for_003.md
```

---

## 8. 成功判据

最低接收标准：

```text
1. 20 号包目录存在。
2. P2 预注册矩阵存在且规模受控。
3. 至少完成 R1/R2/R3/R4 四类区域的渲染/后处理，或明确阻塞。
4. 指标表、区域汇总、P3 候选清单完成。
5. manifest、路径一致性、红线自检完成。
6. 未写成果区、未改 CLAUDE.md、未启动 P3/P4/R128/训练。
```

强接收标准：

```text
1. P2 预注册矩阵全部完成。
2. P2 产生可审阅的高亮、高信息、低信息、风险区域候选。
3. P3 refinement candidates 明确且规模可控。
4. 图表与 summary 能直接支撑 Codex 裁决是否放行 P3。
```

---

## 9. 最后提醒

本轮只做 P2 sparse 3-axis grid。完成后只提交 20 号包和 003 报告。不要自行把结果升级到成果区，不要生成 Codex 审阅文件，不要修改 `CLAUDE.md`，不要启动 P3/P4、roll-aware 训练或 R128。
