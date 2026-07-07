# R155 Codex 任务单：P4-PHYS-E sun/view 3×3 组合小网格补齐

最后更新：2026-07-06  
任务类型：给 Claude 的长程执行任务  
上游依据：R154 接收 009 / 26 包，P4-PHYS-D 裁定 `SUNVIEW_DEPENDENT_BUT_MECHANISTIC`  
本轮目标：在不做全局搜索的前提下，补齐 baseline 邻域 sun/view 同时扰动的小组合网格，判断是否可进入三轴小项目收口裁决。  

## 1. 本轮目标

R154 已确认：

```text
1. pure sun±7° / pure view±7° 下，逐几何最亮姿态会迁移。
2. 迁移目标仍落在 top-1 roll 邻域簇 D5/D6。
3. 高亮仍由金属主体近镜面对齐探测器的连续机制解释。
4. 当前尚未检验 sun 与 view 同时扰动时，机制和 top 候选是否仍成立。
```

本轮 P4-PHYS-E 要回答：

```text
在 sun_offset ∈ {-7,0,+7} 与 view_offset ∈ {-7,0,+7} 的 3×3 组合几何内，
最高亮候选是否仍为 A_top1 / D5_roll125 / D6_roll175 这一 top-1 roll 邻域簇；
G0 baseline 是否仍是本局部组合网格内最高 OCS；
金属主体近镜面对齐连续机制是否仍能解释高亮迁移；
是否已经足够进入三轴小项目收口裁决，或还需更小步长局部加密。
```

本轮不是全 sun/view 搜索，不新增姿态搜索。

## 2. 输出位置

新结果包写入：

```text
v0.4_results/27_three_axis_p4phys_e_sunview_3x3_cross_grid/
```

执行报告写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/010_P4PHYS_E_sunview_3x3_cross_grid_Claude执行报告.md
```

建议目录结构：

```text
audit/
tables/
figures/
text/
scripts/
logs/
postprocess/
```

原则上不新增 `render/`；若发现复用路径不足，必须先停止并在报告中说明，不得自行扩大渲染。

## 3. 必读文件

按顺序读取：

```text
CLAUDE.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R153_Codex_任务单_P4PHYS-D_sunview小矩阵扩展阶段门.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R154_Codex_审阅_009通过_P4PHYSD小矩阵接收并放行P4PHYSE.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/09_P4PHYS-D_sunview小矩阵扩展_R154通过.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/009_P4PHYS_D_sunview_small_matrix_Claude执行报告.md
```

必须读取 26 包：

```text
v0.4_results/26_three_axis_p4phys_d_sunview_small_matrix/scripts/p4physD_config.py
v0.4_results/26_three_axis_p4phys_d_sunview_small_matrix/scripts/p4physD_postprocess.py
v0.4_results/26_three_axis_p4phys_d_sunview_small_matrix/scripts/p4physD_mechanism_analysis.py
v0.4_results/26_three_axis_p4phys_d_sunview_small_matrix/audit/sunview_geometry_manifest.csv
v0.4_results/26_three_axis_p4phys_d_sunview_small_matrix/audit/pose_candidate_manifest.csv
v0.4_results/26_three_axis_p4phys_d_sunview_small_matrix/tables/p4physD_cross_geometry_rank_table.csv
v0.4_results/26_three_axis_p4phys_d_sunview_small_matrix/tables/p4physD_top1_stability_table.csv
v0.4_results/26_three_axis_p4phys_d_sunview_small_matrix/tables/p4physD_mechanism_signature_by_geometry.csv
```

## 4. 几何设计

构造 9 个组合几何：

```text
sun_offset  ∈ {-7°, 0°, +7°}
view_offset ∈ {-7°, 0°, +7°}
```

命名建议：

```text
H00_baseline       : sun 0,  view 0
Hsp_v0             : sun +7, view 0
Hsm_v0             : sun -7, view 0
Hs0_vp             : sun 0,  view +7
Hs0_vm             : sun 0,  view -7
Hsp_vp             : sun +7, view +7
Hsp_vm             : sun +7, view -7
Hsm_vp             : sun -7, view +7
Hsm_vm             : sun -7, view -7
```

复用原则：

```text
camera EXR 只由 view_offset 决定：
view 0 复用 G0 baseline camera；
view +7 复用 26 包 G3_view_plus camera；
view -7 复用 26 包 G4_view_minus camera。

sun EXR 只由 sun_offset 决定：
sun 0 复用 G0 baseline sun；
sun +7 复用 26 包 G1_sun_plus sun；
sun -7 复用 26 包 G2_sun_minus sun。
```

因此本轮原则上 **0 新增渲染**，只做 9×14 的组合后处理与机制重算。若某个复用 EXR 缺失，不得自行补渲染；先写明阻塞。

## 5. 姿态候选

沿用 26 包同一 14 个姿态候选，不新增姿态搜索：

```text
A_top1
B_R4
C_R3
D1-D6
E1/E2
F1-F3
```

必须额外标注 top-1 roll 邻域簇：

```text
core_top1_roll_neighborhood = A_top1 + D1-D6 + F1/F2/F3 中与 roll+15 高亮簇相关的候选
primary_shift_targets = D5_roll125, D6_roll175
controls = B_R4, C_R3
```

## 6. 必做输出

### A. 设计与复用审计

输出：

```text
audit/input_manifest.csv
audit/sunview_3x3_geometry_manifest.csv
audit/pose_candidate_manifest.csv
audit/reuse_exr_manifest.csv
audit/redline_precheck.csv
```

必须回答：

```text
1. 9 个组合几何的 sun_dir / det_dir / offset 标签。
2. 每个组合几何复用哪个 camera EXR、哪个 sun EXR。
3. 是否 0 新增渲染。
4. 是否未改 20/21/23A/23B/24/25/26 源包。
```

### B. 组合后处理与一致性

输出：

```text
tables/p4physE_metrics.csv
audit/postprocess_status.csv
audit/numeric_consistency_check.csv
logs/p4physE_postprocess.log
```

要求：

```text
9×14 = 126 个组合全部 COMPLETE；
H00 / pure sun / pure view 的结果必须与 26 包对应 G0/G1/G2/G3/G4 数值一致；
max rel_diff < 1e-4，否则停止并报告。
```

### C. 排名与机制分析

输出：

```text
tables/p4physE_cross_geometry_rank_table.csv
tables/p4physE_top_candidate_summary.csv
tables/p4physE_top1_stability_table.csv
tables/p4physE_mechanism_signature_by_geometry.csv
figures/p4physE_ocs_3x3_heatmap.png
figures/p4physE_ocs_3x3_heatmap.pdf
figures/p4physE_top_pose_by_geometry.png
figures/p4physE_top_pose_by_geometry.pdf
text/p4physE_sunview_3x3_result.md
```

必须回答：

```text
1. 9 个组合几何下逐几何最亮点是谁。
2. 全 126 个组合的最高 OCS 是谁；baseline A_top1 是否仍最高。
3. 逐几何最亮点是否都落在 top-1 roll 邻域簇。
4. D5/D6 是否继续承担迁移目标。
5. R4 是否仍是金属主导对照；R3 是否仍为候选集最低或近最低。
6. 严格 near_specular_metal 与连续机制量是否继续分歧；若分歧，必须沿用 R154 的限定。
```

### D. 下一步裁决接口

输出：

```text
tables/p4physE_claim_boundary_table.csv
tables/p4physE_gate_matrix.csv
audit/redline_self_check.csv
audit/generated_files_manifest.csv
text/p4physE_next_step_recommendation.md
text/codex_review_checklist_for_010.md
```

必须给出三类建议之一：

```text
1. READY_FOR_THREE_AXIS_CLOSURE_REVIEW：
   3×3 组合几何内 baseline 或同一 top-1 roll 邻域机制稳定，可进入三轴小项目收口审阅。
2. NEED_LOCAL_STEP_REFINEMENT：
   3×3 内最高点出现在边界或混合角落，需更小步长或中心平移的局部 refinement。
3. INCONCLUSIVE_OR_MECHANISM_BREAK：
   组合几何下机制解释失稳、R3/R4 对照失效或复用链路不可信，需返工。
```

## 7. 红线

```text
不得训练。
不得启动 R128。
不得启动路线二/三/四。
不得做全 sun/view 全姿态搜索。
不得新增姿态候选。
原则上不得新增渲染；若确需渲染，必须停止并交回 Codex，不得自行执行。
不得改 20/21/23A/23B/24/25/26 源包。
不得写成果区，不改 CLAUDE.md，不生成 Codex 审阅文件。
不得把 3×3 局部组合网格写成全局 sun/view 结论。
不得把 material proxy 写成真实 material-level attribution。
```

## 8. 报告要求

010 报告保持简洁，只写：

```text
1. 3×3 组合几何如何构造和复用 EXR。
2. 是否 0 新增渲染，后处理是否 126/126 complete。
3. 全表最高 OCS 与逐几何 top 候选。
4. A_top1 / D5 / D6 / R4 / R3 的核心变化。
5. 机制连续量与 strict nsm 的关系。
6. 三类建议标签之一。
7. 红线自查。
```

不得复述 P4-PHYS-A/B/C/D 的完整历史。

