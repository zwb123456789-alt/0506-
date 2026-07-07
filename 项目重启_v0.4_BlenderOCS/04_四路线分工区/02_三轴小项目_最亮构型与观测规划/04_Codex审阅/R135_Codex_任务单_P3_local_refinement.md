# R135 Codex 任务单：P3 local refinement

最后更新：2026-07-06  
任务类型：给执行端 Claude 的长程局部加密任务提示词  
上游阶段门：R134 已通过 003，P2 sparse grid 接收  
当前状态：放行 P3 local refinement；不放行 P4、roll-aware 训练或 R128

执行端报告必须写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/004_P3_local_refinement_Claude执行报告.md
```

所有新结果写入：

```text
v0.4_results/21_three_axis_p3_local_refinement/
```

本文件是 Codex 调度/提示词文件，保留在本路线 `04_Codex审阅/`。执行端不得把报告、结果或裁决文件写入 `04_Codex审阅/`。

---

## 0. 给 Claude 的总提示词

你现在执行三轴小项目第三阶段：

```text
three_axis_p3_local_refinement
```

R134 已接收 P2 sparse grid。P2 验证了 P1 观察在局部三轴邻域中保持：高亮区域与高信息区域不等同，R1 高 |pitch| / yaw240 系 roll 最敏感，R3 低信息区域较连通，brightness 与 information 持续解耦。你的任务是在受控规模内围绕 P2 候选区域做局部加密，确认 single-pose 最亮候选、高信息辅助点、roll-sensitive 点和低信息连通区域是否稳定，并为后续 P4 最亮构型与光路解释综合形成可审阅输入。

本轮不训练，不启动 P4，不启动 R128。

---

## 1. 当前允许与禁止

允许：

```text
1. 读取 20 号包、003 报告、R134 审阅与 P2 成果摘要。
2. 新增派生渲染、后处理、汇总与制图脚本。
3. 围绕 P2 候选做局部 yaw/pitch/roll 加密。
4. 计算 OCS magnitude、rank、neighbor_contrast_ypr、roll sensitivity、rank shift、glint/saturation、image usability、local stability。
5. 生成 P4 最亮构型与光路解释综合候选输入。
```

禁止：

```text
1. 不启动 P4 最亮构型与光路解释综合。
2. 不训练任何模型，不做 roll-aware neural model。
3. 不启动 R128、新路线二、GEO 真实数据处理、路线二/三/四或 T3/L2。
4. 不改旧脚本、旧 metrics、旧 samples、旧结果目录 10-20。
5. 不改 OBS_GEOMETRIES、split、backbone 或超参。
6. 不写成果区，不生成 Codex 审阅文件，不改 CLAUDE.md。
7. 不把 P3 写成三轴小项目完成或真实未知目标反演系统。
```

---

## 2. 必读文件

按顺序读取并在报告列出：

```text
CLAUDE.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R134_Codex_审阅_003通过_P2_sparse_grid接收并放行P3_local_refinement.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/03_P2_sparse_3axis_grid_R134通过.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/02_三轴小项目后续技术路线执行框架_R132通过.md
v0.4_results/20_three_axis_p2_sparse_grid/tables/p2_p3_refinement_candidates.csv
v0.4_results/20_three_axis_p2_sparse_grid/tables/p2_sparse_grid_metrics.csv
v0.4_results/20_three_axis_p2_sparse_grid/tables/p2_region_summary.csv
v0.4_results/20_three_axis_p2_sparse_grid/tables/p2_next_step_recommendations.csv
v0.4_results/20_three_axis_p2_sparse_grid/text/p2_sparse_grid_summary.md
```

---

## 3. 子任务 A：P3 局部加密预注册

优先区域：

```text
P3-R1-high-info：围绕 yaw245, pitch+30/+35，加密 yaw240-250、pitch+25-40。
P3-R4-bright-info-boundary：围绕 yaw150,+15 与 yaw155,+20，加密 yaw145-160、pitch+10-25。
P3-R3-low-info-connectivity：围绕 yaw55-65、pitch+60-70，加密低信息连通边界。
P3-R2/R5-controls：只取少量暗区/中性区对照点，不扩大为主任务。
```

建议局部网格：

```text
yaw step：2.5 或 5 度，按代码可支持精度选择；若非 5 度会破坏复用链路，则统一 5 度。
pitch step：2.5 或 5 度，同上。
roll values：{-60,-45,-30,-15,0,+15,+30,+45,+60}。
```

规模控制：

```text
非零 roll 新渲染单位原则上 <= 2000。
若超过上限，优先保留 R1/R4，裁剪 R2/R5，对 R3 只保留低信息边界。
roll=0 能复用则复用，不能复用时必须报告原因；不得静默缺失。
```

必须输出：

```text
audit/p3_input_manifest.csv
tables/p3_local_refinement_pre_registered_matrix.csv
tables/p3_region_definition.csv
audit/p3_redline_precheck.csv
```

---

## 4. 子任务 B：P3 渲染与后处理

必须输出：

```text
render/p3_render_manifest.csv
postprocess/p3_postprocess_manifest.csv
logs/p3_render_postprocess.log
```

要求：

```text
1. 所有姿态必须有 yaw/pitch/roll/region/category/source_p2_candidate。
2. 渲染与后处理采用与 P1/P2/路线一一致量纲和配置。
3. 失败不能静默跳过，必须列失败列表和原因。
4. 不改 20 号包和旧结果目录。
```

---

## 5. 子任务 C：P3 稳定性指标

必须输出：

```text
tables/p3_local_refinement_metrics.csv
tables/p3_region_summary.csv
tables/p3_stability_assessment.csv
tables/p3_high_brightness_refined_candidates.csv
tables/p3_high_information_refined_candidates.csv
tables/p3_low_information_connectivity.csv
tables/p3_p4_planning_candidates.csv
metrics/p3_metric_definitions_used.md
```

至少计算：

```text
ocs_total；
brightness_rank；
neighbor_contrast_ypr；
roll_sensitivity_score；
rank_shift；
glint/saturation flag；
image_usable flag；
local peak migration；
local information stability；
low-info connectivity；
P4 最亮构型与光路解释辅助 utility score；
```

必须回答：

```text
1. R4 最亮点是否仍在 yaw150/+15 附近，还是向 yaw155/+20 或其他边界迁移。
2. R4 高信息边界点是否稳定，是否能作为亮-信息折中候选。
3. R1 roll-sensitive peak 是否稳定在 yaw245、pitch+30/+35 邻域。
4. R3 低信息区是否连通，是否适合作为负面对照。
5. R2/R5 是否仅支持对照定位，是否需要从 P4 主规划中降权。
```

---

## 6. 子任务 D：图表与解释

必须输出：

```text
figures/p3_refined_brightness_map.png/.pdf
figures/p3_refined_information_proxy_map.png/.pdf
figures/p3_peak_migration_panel.png/.pdf
figures/p3_low_info_connectivity_panel.png/.pdf
figures/p3_planning_candidate_scatter.png/.pdf
text/p3_local_refinement_summary.md
```

---

## 7. 子任务 E：验收矩阵与下一步建议

必须输出：

```text
tables/p3_gate_matrix.csv
tables/p3_next_step_recommendations.csv
audit/generated_files_manifest.csv
audit/numeric_path_consistency_check.csv
audit/redline_self_check.csv
text/codex_review_checklist_for_004.md
```

---

## 8. 成功判据

最低接收标准：

```text
1. 21 号包目录存在。
2. P3 预注册矩阵存在且规模受控。
3. 至少完成 R1/R4/R3 三类核心区域的渲染/后处理，或明确阻塞。
4. 稳定性指标、区域汇总、P4 候选清单完成。
5. manifest、路径一致性、红线自检完成。
6. 未写成果区、未改 CLAUDE.md、未启动 P4/R128/训练。
```

强接收标准：

```text
1. P3 预注册矩阵全部完成。
2. R1/R4/R3 形成稳定性判断。
3. P4 最亮构型与光路解释候选明确且规模可控。
4. 图表与 summary 能直接支撑 Codex 裁决是否放行 P4。
```

---

## 9. 最后提醒

本轮只做 P3 local refinement。完成后只提交 21 号包和 004 报告。不要自行把结果升级到成果区，不要生成 Codex 审阅文件，不要修改 `CLAUDE.md`，不要启动 P4、roll-aware 训练或 R128。
