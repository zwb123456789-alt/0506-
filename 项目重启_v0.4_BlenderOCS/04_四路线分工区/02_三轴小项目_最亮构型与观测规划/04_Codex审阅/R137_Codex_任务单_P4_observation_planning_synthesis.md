# R137 Codex 任务单：P4 最亮构型与光路解释综合

最后更新：2026-07-06  
任务类型：给执行端 Claude 的长程综合收口任务提示词  
上游阶段门：R136 已通过 004，P3 local refinement 接收；R138 已补充校正三轴小项目唯一最高标准  
当前状态：放行 P4 最亮构型与光路解释综合；不放行 R128、训练或路线二/三/四

执行端报告必须写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/005_P4_observation_planning_synthesis_Claude执行报告.md
```

所有新结果写入：

```text
v0.4_results/22_three_axis_p4_observation_planning/
```

本文件是 Codex 调度/提示词文件，保留在本路线 `04_Codex审阅/`。执行端不得把报告、结果或裁决文件写入 `04_Codex审阅/`。

---

## 0. 给 Claude 的总提示词

你现在执行三轴小项目第四阶段：

```text
three_axis_p4_brightest_configuration_and_light_path_synthesis
```

R136 已接收 P3 local refinement，R138 已补充校正：三轴小项目唯一且最高标准是在已知卫星模型和前向光学模型下，找出卫星在哪个 yaw/pitch/roll 姿态、哪个太阳入射几何和哪个探测器观测几何下最亮，并解释这束光从哪里入射、照到卫星哪个部位/材料/表面、再沿哪个方向进入探测器。P1 跑通 seed-roll 链路；P2/P3 已提供局部三轴候选。你的任务是综合 P1/P2/P3 的表格、图表和摘要，首先确认 single-pose top-1 最亮 yaw/pitch/roll + sun/view 构型，然后解释其光路、受光部位、材料/表面响应和探测器接收路径；随后检验共享同类入射-表面/材料-探测器光路的邻近姿态或候选簇是否普遍高亮。高信息、低信息、易混淆和观测规划只作为辅助标注。

本轮不新增渲染，不训练，不启动 R128，不启动路线二/三/四。

---

## 1. 当前允许与禁止

允许：

```text
1. 读取 18/19/20/21 号包、R130/R132/R134/R136 审阅和当前主用成果摘要。
2. 汇总 P1/P2/P3 的核心数值、候选姿态、图表和红线。
3. 生成最亮构型的光路解释：太阳入射方向、受光部位、材料/表面响应、探测器接收方向。
4. 在 top-1 确认后，检验同类光路机制是否对应普遍高亮的邻近姿态或候选簇。
5. 将高信息区域、低信息负面对照、dark/neutral 对照作为辅助标注。
6. 生成三轴小项目阶段性收口候选材料，供 Codex 裁决。
7. 生成面向后续 R128 回看、论文 Results/SI 或 Discussion 的候选接口清单。
```

禁止：

```text
1. 不新增 Blender 渲染或后处理。
2. 不训练任何模型，不做 roll-aware neural model。
3. 不启动 R128、新路线二、GEO 真实数据处理、路线二/三/四或 T3/L2。
4. 不改旧脚本、旧 metrics、旧 samples、旧结果目录 10-21。
5. 不写成果区，不生成 Codex 审阅文件，不改 CLAUDE.md。
6. 不把 P4 写成真实未知目标三轴姿态反演系统。
7. 不把高信息/观测规划写成三轴小项目主目标。
8. 不把 neighbor_contrast_ypr 写成最终模型级信息量证明。
```

---

## 2. 必读文件

按顺序读取并在报告列出：

```text
CLAUDE.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R136_Codex_审阅_004通过_P3_local_refinement接收并放行P4_planning.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R138_Codex_补充校正_三轴小项目最亮构型主目标与roll遍历口径.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/04_P3_local_refinement_R136通过.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/03_P2_sparse_3axis_grid_R134通过.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/02_三轴小项目后续技术路线执行框架_R132通过.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/01_P1_seed_roll_smoke_R132通过.md
v0.4_results/21_three_axis_p3_local_refinement/tables/p3_p4_planning_candidates.csv
v0.4_results/21_three_axis_p3_local_refinement/tables/p3_region_summary.csv
v0.4_results/21_three_axis_p3_local_refinement/tables/p3_stability_assessment.csv
v0.4_results/21_three_axis_p3_local_refinement/text/p3_local_refinement_summary.md
v0.4_results/20_three_axis_p2_sparse_grid/tables/p2_region_summary.csv
v0.4_results/20_three_axis_p2_sparse_grid/text/p2_sparse_grid_summary.md
v0.4_results/19_three_axis_p1_seed_roll_scan/tables/p1_roll_sensitivity_summary.csv
v0.4_results/19_three_axis_p1_seed_roll_scan/text/p1_seed_roll_smoke_summary.md
```

---

## 3. 子任务 A：输入审计与证据索引

必须输出：

```text
audit/p4_input_manifest.csv
audit/p4_source_tables_figures_manifest.csv
audit/p4_redline_precheck.csv
tables/p4_evidence_index.csv
```

要求：

```text
1. 明确每条结论来自 P1/P2/P3 哪个文件和哪一列。
2. 标记哪些结论是稳定成果、哪些只是 proxy 级或待后续阶段门。
3. 不复制大段上游报告，只做路径、表名、字段、核心数值索引。
```

---

## 4. 子任务 B：最亮构型与光路口径重聚合

必须优先输出：

```text
tables/p4_global_brightest_pose_table.csv
tables/p4_brightest_roll_profile.csv
tables/p4_roll_aggregated_brightest_region.csv
tables/p4_brightest_light_path_trace.csv
tables/p4_brightest_surface_material_trace.csv
tables/p4_bright_mechanism_generality_check.csv
figures/p4_global_brightest_pose_panel.png/.pdf
figures/p4_bright_mechanism_consistency_map.png/.pdf
text/p4_brightest_configuration_summary.md
text/p4_bright_mechanism_generality_summary.md
```

必须回答：

```text
1. 当前 P1/P2/P3 范围内 single-pose 最亮 yaw/pitch/roll + sun/view 构型是什么。
2. roll-aggregated 最亮 yaw/pitch 区域是什么。
3. single-pose 最亮与 roll 稳健高亮区域是否一致。
4. 最亮 single-pose 对应的太阳入射方向、受光部位、材料/表面响应和探测器接收方向是什么。
5. 与最亮 single-pose 共享同类入射-表面/材料-探测器光路的姿态/几何候选是否普遍高亮。
6. 若同类机制不普遍高亮，top-1 是否只是局部 glint、饱和、遮挡边界或数值偶然峰。
7. 最亮 single-pose 是否有 glint/saturation 风险。
8. 高信息/低信息/观测规划只作为辅助标注，不改变最亮构型主结论。
```

注意：

```text
R4 yaw147.5/+12.5 只能先写作 roll-aggregated bright/robust 区候选；
不能在未重聚合 single-pose ocs_total 前写作全局最亮三轴构型；
R1 yaw245/+30/roll+15 等高亮 single-pose 候选必须纳入核验。
```

## 5. 子任务 C：观测规划角色分层

必须输出：

```text
tables/p4_planning_candidate_roles.csv
tables/p4_region_role_summary.csv
tables/p4_observation_priority_matrix.csv
tables/p4_risk_and_boundary_matrix.csv
```

至少分成：

```text
1. high-info-roll-sensitive：R1 yaw245-247.5, pitch+30~40。
2. bright-info-tradeoff：R4 yaw155/+20 与邻近点。
3. roll-aggregated bright/robust reference：R4 roll-aggregated bright 区 yaw147.5/+12.5 及最亮簇。
4. low-info-negative-control：R3 低信息连通区。
5. dark/neutral-control：R2/R5 降权对照。
```

必须说明：

```text
最亮构型与高信息/观测规划必须分开；
高信息姿态不一定最亮；
低信息区域适合作负面对照或避开区域；
glint/saturation 风险如何影响候选使用。
```

---

## 6. 子任务 D：三轴小项目阶段性收口候选

必须输出：

```text
text/p4_three_axis_project_stage_summary.md
tables/p4_stage_claim_boundary_table.csv
tables/p4_what_can_be_claimed.csv
tables/p4_what_must_not_be_claimed.csv
```

收口候选必须严格限定为：

```text
model-known simulated 条件；
phase63 / L1-G1 局部三轴观测规划；
基于 OCS brightness、neighbor_contrast_ypr、roll_sensitivity 等 proxy；
寻找最亮姿态-几何构型并解释入射-表面-探测器光路；
先确认 top-1，再检验同类光路机制是否普遍对应高亮候选簇；
高信息姿态、低信息区和观测规划建议只作为辅助标注；
不提供真实未知目标三轴姿态反演成功率。
```

---

## 7. 子任务 E：图表与可解释材料

允许复用 P1/P2/P3 图表，但必须生成 P4 综合图：

```text
figures/p4_observation_role_map.png/.pdf
figures/p4_global_brightest_pose_panel.png/.pdf
figures/p4_brightest_light_path_schematic.png/.pdf
figures/p4_brightness_information_decoupling_summary.png/.pdf
figures/p4_planning_candidate_panel.png/.pdf
figures/p4_stage_evidence_flow.png/.pdf
text/p4_observation_planning_summary.md
```

图表不得暗示真实观测定姿成功率，不得把 proxy 指标画成最终概率或模型置信。

---

## 8. 子任务 F：后续接口与验收

必须输出：

```text
tables/p4_next_step_recommendations.csv
tables/p4_r128_interface_candidates.csv
tables/p4_results_si_candidate_assets.csv
tables/p4_gate_matrix.csv
audit/generated_files_manifest.csv
audit/numeric_path_consistency_check.csv
audit/redline_self_check.csv
text/codex_review_checklist_for_005.md
```

`p4_r128_interface_candidates.csv` 只列接口候选，不启动 R128。至少包括：

```text
R1 高信息/roll-sensitive 场景；
R4 亮-信息折中场景；
R4 bright-but-low-info caution 场景；
R3 low-info negative control；
R2/R5 dark/neutral controls。
```

---

## 9. 成功判据

最低接收标准：

```text
1. 22 号包目录存在。
2. 没有新增渲染、训练或后处理。
3. single-pose 最亮 yaw/pitch/roll + sun/view 与 roll-aggregated 最亮区域均已明确。
4. 最亮构型对应的入射光方向、受光部位、材料/表面响应和探测器接收方向均已明确或列出缺口。
5. 已检验同类光路机制是否对应普遍高亮候选簇，或明确列出无法检验的字段缺口。
6. 高信息/低信息/观测规划被明确标为辅助标注。
7. stage summary、claim boundary、must-not-claim 表完成。
8. R128 接口候选只列清单，不启动。
9. manifest、路径一致性、红线自检完成。
10. 未写成果区、未改 CLAUDE.md、未生成 Codex 审阅文件。
```

强接收标准：

```text
1. P4 能直接支撑 Codex 裁决三轴小项目是否阶段性收口。
2. P4 给出可用于论文 Results/SI/Discussion 的候选资产清单。
3. P4 明确下一步是回看 R128、论文写作准备，还是补充极小诊断。
```

---

## 10. 最后提醒

本轮只做 P4 最亮构型与光路解释综合。完成后只提交 22 号包和 005 报告。不要自行把结果升级到成果区，不要生成 Codex 审阅文件，不要修改 `CLAUDE.md`，不要启动 R128、路线二/三/四、roll-aware 训练或新渲染。
