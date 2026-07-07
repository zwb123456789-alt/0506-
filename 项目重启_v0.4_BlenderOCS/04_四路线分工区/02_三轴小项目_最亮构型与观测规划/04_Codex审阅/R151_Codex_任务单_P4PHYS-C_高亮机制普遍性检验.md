# R151 Codex 任务单：P4-PHYS-C 高亮机制普遍性检验

最后更新：2026-07-06  
任务类型：给 Claude 的长程执行任务  
上游依据：R150 接收 007 / 24 包，P4-PHYS-B top-1 光路归因完成  
本轮目标：检验 top-1 机制是否普遍对应高亮候选  

## 1. 本轮目标

R148 已确认 fixed `phase63/L1-G1` 下当前 yaw/pitch/roll top-1：

```text
yaw=245.0
pitch=+27.5
roll=+15
ocs_total=0.2088904828
```

R150 已接收 P4-PHYS-B 光路归因，当前 top-1 机制签名为：

```text
金属主体大面元近镜面对齐探测器；
金属主体贡献约 95%；
金属法向与半程向量夹角约 0.57°；
反射方向与探测器夹角约 1.06°；
隐身板附加受照面提供 top-1 超过 R4 的小增量。
```

本轮 P4-PHYS-C 的目标是回答：

```text
这种“金属主体近镜面对齐 + 隐身板附加增量”的机制，
是否在 fixed phase63/L1-G1 的既有候选集中普遍对应高亮？
```

本轮不是继续搜索新姿态，不扩展 sun/view，不做新渲染。只复用已有渲染与 24 包脚本口径，做机制签名统计与高亮排序验证。

## 2. 重要边界

必须写清：

```text
1. 本轮仍限定 fixed phase63/L1-G1，SUN=[1,0,0.3]，DET=[0.5,-1,0.1]。
2. 本轮检验的是固定几何下的机制普遍性，不是所有 sun/view 下的全局机制。
3. material-level 仍为 proxy；material pass 不作为本轮前置。
4. 不得新增渲染，不得扩展 sun/view，不得训练，不得启动 R128。
5. 不得把本轮写成三轴小项目最终闭口；本轮最多放行后续 sun/view 扩展或收口裁决。
```

关于 material pass：

```text
本轮不要求 material pass。
若发现 part/material proxy 无法支撑关键结论，只能列为后续可选增强，不得自行启动。
```

## 3. 输出位置

执行报告写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/008_P4PHYS_C_mechanism_generality_Claude执行报告.md
```

新结果包写入：

```text
v0.4_results/25_three_axis_p4phys_c_mechanism_generality/
```

建议目录结构：

```text
audit/
tables/
figures/
text/
scripts/
logs/
```

不得改写 20/21/23A/23B/24 包。

## 4. 必读文件

按顺序读取：

```text
CLAUDE.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/00_路线冻结文件区/01_三轴小项目_最亮构型与观测规划指导文件.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/05_三轴小项目最亮构型与光路解释技术路线_R144依据.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/06_P4PHYS-A_fixed几何top1确认_R148通过.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R148_Codex_审阅_006B通过_fixed几何top1闭口并放行P4PHYSB.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R149_Codex_任务单_P4PHYS-B_top1物理光路归因.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R150_Codex_审阅_007通过_P4PHYSB光路归因接收并放行P4PHYSC.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/007_P4PHYS_B_top1_light_path_attribution_Claude执行报告.md
```

必须读取 24 包机制签名与口径：

```text
v0.4_results/24_three_axis_p4phys_b_light_path_attribution/tables/p4physB_mechanism_signature_seed.csv
v0.4_results/24_three_axis_p4phys_b_light_path_attribution/tables/p4physB_top1_ocs_per_part.csv
v0.4_results/24_three_axis_p4phys_b_light_path_attribution/tables/p4physB_control_part_contribution.csv
v0.4_results/24_three_axis_p4phys_b_light_path_attribution/tables/p4physB_top1_light_path_geometry.csv
v0.4_results/24_three_axis_p4phys_b_light_path_attribution/tables/p4physB_control_light_path_geometry.csv
v0.4_results/24_three_axis_p4phys_b_light_path_attribution/audit/exr_path_manifest.csv
v0.4_results/24_three_axis_p4phys_b_light_path_attribution/audit/numeric_path_consistency_check.csv
```

候选池优先读取：

```text
v0.4_results/23A_three_axis_p4phys_top1_roll_confirmation/tables/p4physA_refined_topN.csv
v0.4_results/23B_three_axis_p4phys_pitch_boundary_followup/tables/p4physA2_combined_topN_with_23A.csv
v0.4_results/21_three_axis_p3_local_refinement/tables/p3_local_refinement_metrics.csv
v0.4_results/20_three_axis_p2_sparse_grid/tables/
```

若 P2/P3 表名与本任务不完全一致，允许脚本自动发现包含 `metrics/topN/roll_profile` 字样的 CSV，并把实际读取文件写入 `audit/input_manifest.csv`。

## 5. 候选池设计

本轮候选池按“可复用既有 EXR/JSON、覆盖高亮与对照、规模受控”原则建立。

最低候选池：

```text
1. 23A/23B 合并 top-N 中亮度前 20 个候选。
2. R4 roll-robust 亮区 roll profile 的所有可定位候选。
3. R3 负面对照。
4. P3 local refinement 中每个 primary 区域亮度前若干候选，至少覆盖 R1/R4/R3。
```

强候选池：

```text
1. fixed phase63/L1-G1 下可定位 EXR/JSON 的 P3 全候选或主要候选。
2. P2 sparse grid 中 brightness top 分位候选与 bottom/negative 对照。
3. 23A/23B refined top-N 全部候选。
```

规模控制：

```text
优先不超过 200 个候选。
若自动发现可定位候选超过 200 个，按 brightness/topN/区域对照分层采样；
若不足 30 个，必须报告候选池不足并仍完成最小统计。
```

## 6. 必做子任务

### A. 输入审计与候选池生成

输出：

```text
audit/input_manifest.csv
audit/candidate_pool_manifest.csv
audit/exr_json_availability.csv
audit/redline_precheck.csv
tables/p4physC_candidate_pool.csv
```

必须回答：

```text
1. 每个候选的 EXR、v_sun_macro.npy、ocs.json 是否可定位。
2. 候选来自 23A/23B、21/P3、20/P2 或其它已存在包。
3. 有多少高亮候选、R4 候选、R3/低亮对照。
4. 是否存在只能读指标、不能读 EXR 的候选；这些不得进入几何签名统计。
```

### B. 机制签名批量计算

复用 24 包脚本思路，必要时复制并改造到 25 包 `scripts/`，不得改 24 包。

输出：

```text
tables/p4physC_mechanism_signature_table.csv
tables/p4physC_part_contribution_table.csv
tables/p4physC_geometry_signature_table.csv
audit/numeric_consistency_sample_check.csv
```

每个候选至少计算：

```text
pose_label
yaw / pitch / roll
ocs_total
brightness_rank 或 ocs_rank
dominant_part
metal_body_contrib
dark_panel_contrib
solar_panel_contrib
metal_body_pct
dark_panel_pct
weighted_metal_NH
avgN_vs_H_deg
reflect_vs_det_deg
pct_NoH_ge_0.99
mean_NoH_pow_n_metal
saturation_flag / glint_flag 若可读
```

### C. 高亮机制判据

基于 24 包 seed，定义不超过 3 个可解释机制判据。建议：

```text
near_specular_metal = metal_body_pct >= 80% 且 avgN_vs_H_deg <= 2° 且 reflect_vs_det_deg <= 4°
strong_surface_highlight = pct_NoH_ge_0.99 >= 50% 或 mean_NoH_pow_n_metal >= 0.5
dark_panel_increment = dark_panel_contrib >= 0.004 或 dark_panel_pct >= 2%
```

阈值可根据候选池分布微调，但必须在报告中说明来源，不得事后只为 top-1 服务。

输出：

```text
tables/p4physC_mechanism_rule_table.csv
tables/p4physC_candidate_mechanism_labels.csv
text/p4physC_mechanism_rule_definition.md
```

### D. 普遍性检验

输出：

```text
tables/p4physC_brightness_by_mechanism.csv
tables/p4physC_top_quantile_enrichment.csv
tables/p4physC_dark_panel_increment_test.csv
figures/p4physC_ocs_vs_reflection_alignment.png
figures/p4physC_ocs_vs_reflection_alignment.pdf
figures/p4physC_mechanism_enrichment_bar.png
figures/p4physC_mechanism_enrichment_bar.pdf
text/p4physC_mechanism_generality_result.md
```

必须回答：

```text
1. near_specular_metal 候选是否显著集中在高亮 top 分位。
2. 不满足 near_specular_metal 的候选是否系统性更暗。
3. R4 与 top-1 是否属于同一高亮机制簇。
4. top-1 超过 R4 的隐身板增量，在其它高亮候选中是否可复现。
5. 如果不能复现，要写成“top-1 排序增量”，不能写成普遍高亮机制。
```

不要求严格统计显著性；可以用分位、均值/中位数、top-k enrichment、排序对比。但必须避免把小样本趋势写成定律。

### E. 结论边界与下一阶段接口

输出：

```text
tables/p4physC_claim_boundary_table.csv
text/p4physC_what_can_be_claimed.md
text/p4physC_next_step_recommendation.md
```

必须给出三类结论之一：

```text
1. MECHANISM_GENERALITY_SUPPORTED：
   近镜面金属机制普遍富集于高亮候选，可作为 fixed-geometry 高亮机制结论。
2. PARTIAL_GENERALITY：
   金属近镜面机制普遍解释高亮，但隐身板增量只解释 top-1 排序。
3. NOT_GENERAL：
   top-1 机制只是局部个例，不足以上升为候选簇机制。
```

并建议后续是：

```text
进入 P4-PHYS-D sun/view 扩展；
或先做 material pass / material-ID 增强；
或回退补充机制候选池。
```

Codex 预设倾向：若金属近镜面机制支持、隐身板增量仅局部成立，仍可接收为 `PARTIAL_GENERALITY`，并进入 sun/view 扩展前的阶段门裁决。

## 7. 验收与报告

必须输出：

```text
tables/p4physC_gate_matrix.csv
audit/generated_files_manifest.csv
audit/redline_self_check.csv
audit/numeric_consistency_sample_check.csv
text/codex_review_checklist_for_008.md
```

报告写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/008_P4PHYS_C_mechanism_generality_Claude执行报告.md
```

报告必须简洁回答：

```text
1. 候选池规模与来源。
2. 机制签名如何定义。
3. 近镜面金属机制是否普遍对应高亮。
4. 隐身板增量是否普遍，还是只解释 top-1 超 R4 的排序。
5. R4/R3 在机制统计中分别扮演什么角色。
6. 哪些是 direct，哪些仍是 proxy。
7. 是否建议进入 sun/view 扩展或补 material pass。
```

## 8. 红线

```text
不得训练。
不得启动 R128。
不得启动路线二/三/四。
不得扩展 sun/view。
不得新增渲染。
不得搜索新姿态。
不得改 20/21/23A/23B/24 包。
不得写成果区，不改 CLAUDE.md，不生成 Codex 审阅文件。
不得把固定几何机制写成所有 sun/view 全局机制。
不得把 material proxy 写成真实 material-level attribution。
```

## 9. 接收标准

最低接收：

```text
1. 25 包存在。
2. 008 报告存在。
3. 候选池来源清楚，EXR/JSON 可定位。
4. 批量机制签名表存在。
5. near_specular_metal 与亮度排序的关系有明确结果。
6. 隐身板增量是否普遍有明确判断。
7. claim boundary 清楚。
8. 红线全 PASS。
```

强接收：

```text
1. 候选池覆盖 top-1、R4、R3、23A/23B top-N 与 P3/P2 对照。
2. 机制签名复用 24 包口径且有抽样数值一致性检查。
3. 能明确裁决 MECHANISM_GENERALITY_SUPPORTED / PARTIAL_GENERALITY / NOT_GENERAL。
4. 给出下一阶段 sun/view 扩展或 material pass 的可执行建议。
```

