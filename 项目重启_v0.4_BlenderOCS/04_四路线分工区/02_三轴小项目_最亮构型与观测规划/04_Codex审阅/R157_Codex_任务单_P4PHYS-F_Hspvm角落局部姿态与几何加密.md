# R157 Codex 任务单：P4-PHYS-F Hsp_vm 角落局部姿态与几何加密

最后更新：2026-07-06  
任务类型：给 Claude 的长程执行任务  
上游依据：R156 接收 010/27，但裁定 `NEED_LOCAL_STEP_REFINEMENT`  
本轮目标：围绕 `Hsp_vm(sun+7, view-7)` 角落做受控局部加密，判断 `C_R3` 成为全表最高是真局部峰、边界采样效应，还是机制失稳。  

## 1. 本轮目标

R156 已确认：

```text
1. 27 包 3×3 组合小网格数值链路可信。
2. 全 126 组合最高 = Hsp_vm / C_R3，OCS=0.22555675。
3. 该最高点位于 3×3 角落，脱离 top-1 roll 邻域簇，nsm=0。
4. 逐几何最亮 8/9 仍在 top-1 roll 邻域，但 Hsp_vm 打破收口条件。
```

本轮 P4-PHYS-F 只回答三个问题：

```text
1. 在固定 Hsp_vm 几何下，C_R3 附近是否存在更亮的局部姿态峰？
2. 在 Hsp_vm 周围极小 sun/view 邻域内，最高点是否仍落在边界？
3. 角落高亮机制是可解释的金属宽瓣/几何因子高亮，还是数值链路/对照设计失稳？
```

本轮不是全 sun/view 搜索，不是全姿态搜索，不训练。

## 2. 输出位置

新结果包写入：

```text
v0.4_results/28_three_axis_p4phys_f_hspvm_local_refinement/
```

执行报告写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/011_P4PHYS_F_Hspvm_local_refinement_Claude执行报告.md
```

建议目录：

```text
audit/
render/
postprocess/
tables/
figures/
text/
scripts/
logs/
```

## 3. 必读文件

按顺序读取：

```text
CLAUDE.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R155_Codex_任务单_P4PHYS-E_sunview3x3组合小网格补齐.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R156_Codex_审阅_010通过_NEED_LOCAL_STEP_REFINEMENT并放行P4PHYSF.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/10_P4PHYS-E_sunview3x3组合小网格_R156通过_需局部加密.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/010_P4PHYS_E_sunview_3x3_cross_grid_Claude执行报告.md
```

必须读取并复用 27 包脚本口径：

```text
v0.4_results/27_three_axis_p4phys_e_sunview_3x3_cross_grid/scripts/p4physE_config.py
v0.4_results/27_three_axis_p4phys_e_sunview_3x3_cross_grid/scripts/p4physE_postprocess.py
v0.4_results/27_three_axis_p4phys_e_sunview_3x3_cross_grid/scripts/p4physE_mechanism_analysis.py
v0.4_results/27_three_axis_p4phys_e_sunview_3x3_cross_grid/tables/p4physE_top_candidate_summary.csv
v0.4_results/27_three_axis_p4phys_e_sunview_3x3_cross_grid/tables/p4physE_mechanism_signature_by_geometry.csv
```

需要复用 26 包 EXR 与配置：

```text
v0.4_results/26_three_axis_p4phys_d_sunview_small_matrix/scripts/p4physD_config.py
v0.4_results/26_three_axis_p4phys_d_sunview_small_matrix/render/
```

## 4. 阶段 A：设计审计与 smoke

先生成设计审计，不得直接大批量渲染：

```text
audit/input_manifest.csv
audit/pose_local_grid_manifest.csv
audit/sunview_microgrid_manifest.csv
audit/render_plan_manifest.csv
audit/redline_precheck.csv
```

定义一个 smoke 新姿态：

```text
R3L_smoke: yaw=55, pitch=60, roll=+20
geometry: Hsp_vm(sun+7, view-7)
```

先只对该姿态做 Hsp_vm 所需 camera/sun EXR、后处理和机制重算。若 smoke 渲染、EXR 通道、OCS 积分或机制一致性任一失败，停止并写阻塞报告，不得继续正式矩阵。

## 5. 阶段 B：固定 Hsp_vm 的 C_R3 局部姿态网格

固定几何：

```text
Hsp_vm: sun_offset=+7, view_offset=-7
```

围绕 `C_R3(yaw=55, pitch=+60, roll=0)` 做 3×3×3 局部姿态网格：

```text
yaw   ∈ {35, 55, 75}
pitch ∈ {45, 60, 75}
roll  ∈ {-20, 0, +20}
```

共 27 个局部姿态。中心点 `yaw=55,pitch=60,roll=0` 等同既有 `C_R3`，必须复用 26/27 已有结果；其余最多 26 个新姿态。每个新姿态在 Hsp_vm 只需要：

```text
camera EXR：view -7
sun EXR：sun +7
```

本阶段新增渲染上限：

```text
≤ 52 个 render units
```

输出：

```text
tables/p4physF_stage1_pose_local_rank.csv
tables/p4physF_stage1_best_summary.csv
figures/p4physF_stage1_pose_slices.png
figures/p4physF_stage1_pose_slices.pdf
```

必须标注：

```text
1. Stage1 最高姿态是谁，OCS 多少，是否超过原 C_R3。
2. Stage1 最高点是否在局部姿态网格边界。
3. Stage1 最高点是否仍为金属主体主导。
4. Stage1 最高点是否为 near_specular_metal。
```

如果 Stage1 最高点在 yaw/pitch/roll 任一轴边界，本轮仍继续阶段 C，但最终不得收口，只能报告边界未闭合。

## 6. 阶段 C：Hsp_vm 周围极小 sun/view microgrid

只对少量姿态做几何 microgrid，不得扩大。

姿态集合：

```text
S0 = C_R3
S1 = Stage1_best
S2 = A_top1
S3 = D5_roll125
S4 = D6_roll175
S5 = B_R4
```

若 `Stage1_best` 与上述任一姿态重复，去重。不得加入其他姿态。

几何集合：

```text
sun_offset  ∈ {+5, +7, +9}
view_offset ∈ {-9, -7, -5}
```

中心为 `Hsp_vm(+7,-7)`。复用原则仍与 27 包一致：

```text
camera EXR 只由 view_offset 和姿态决定；
sun EXR 只由 sun_offset 和姿态决定。
```

必须复用已存在的 `sun+7` 与 `view-7` EXR；只渲染缺失的 `sun+5/sun+9` 与 `view-9/view-5` EXR。

本阶段新增渲染上限：

```text
≤ 24 个 render units
```

全轮新增渲染硬上限：

```text
≤ 80 个 render units
```

若预检查发现会超过 80，必须停止并报告，不得自行扩大或改网格。

输出：

```text
tables/p4physF_stage2_sunview_microgrid_rank.csv
tables/p4physF_stage2_top_candidate_summary.csv
figures/p4physF_stage2_microgrid_heatmap.png
figures/p4physF_stage2_microgrid_heatmap.pdf
```

必须回答：

```text
1. Stage2 全表最高是谁。
2. Stage2 最高几何是否仍在 microgrid 边界。
3. Stage2 最高姿态是否是 Stage1_best / C_R3 / 原 top-1 roll 邻域 / R4。
4. C_R3 在 microgrid 中是否仍能作为负对照。
```

## 7. 机制分析要求

复用 24/25/26/27 的机制签名口径，并额外输出几何因子诊断：

```text
dominant_part
metal%
dark%
avgN_vs_H_deg
reflect_vs_det_deg
pct_NoH_ge_0.99
mean_NoH_pow_n
near_specular_metal
weighted_NoL
weighted_NoV
weighted_NoL_NoV
```

输出：

```text
tables/p4physF_mechanism_signature.csv
tables/p4physF_control_boundary_table.csv
audit/numeric_consistency_check.csv
```

解释边界：

```text
若最高点 nsm=0，但 weighted_NoL / weighted_NoV / weighted_NoL_NoV 高，可以写成金属宽瓣/几何因子高亮。
不得把它写成严格近镜面对齐。
不得写真实 material-level attribution。
```

## 8. 裁决接口

输出：

```text
tables/p4physF_gate_matrix.csv
tables/p4physF_claim_boundary_table.csv
audit/redline_self_check.csv
audit/generated_files_manifest.csv
text/p4physF_result.md
text/p4physF_next_step_recommendation.md
text/codex_review_checklist_for_011.md
```

三类建议标签只能选一类：

```text
LOCAL_MAX_INTERNALIZED：
  Stage1/Stage2 最高点不在姿态或几何边界，机制可解释，可交 Codex 判断是否进入三轴小项目收口审阅。

NEED_SECOND_STEP_REFINEMENT：
  最高点仍在姿态或几何边界，或 Stage1/Stage2 暴露新的更亮边界方向，需要更小步长或中心平移。

MECHANISM_BREAK_OR_AUDIT_FAIL：
  渲染/复用/OCS/机制一致性不可信，或金属主导/机制解释链条出现不能解释的断裂。
```

## 9. 红线

```text
不得训练。
不得启动 R128。
不得启动路线二/三/四。
不得做全 sun/view 全姿态搜索。
不得把本轮局部 microgrid 写成全局 sun/view 结论。
不得超过 80 个新增 render units。
不得改 20/21/23A/23B/24/25/26/27 源包。
不得写成果区，不改 CLAUDE.md，不生成 Codex 审阅文件。
不得把 B0 proxy 写成真实 material-level attribution。
若最高点仍在边界，不得自行扩大第二轮网格，必须交回 Codex。
```

## 10. 报告要求

011 报告保持简洁，只写：

```text
1. smoke 是否通过。
2. 实际新增 render units 数量，是否 ≤80。
3. Stage1 固定 Hsp_vm 姿态局部网格最高点。
4. Stage2 sun/view microgrid 最高点。
5. 最高点是否在边界。
6. C_R3 / Stage1_best / A_top1 / D5 / D6 / R4 的核心变化。
7. 机制解释：近镜面还是宽瓣/几何因子，金属占比多少。
8. 三类建议标签之一。
9. 红线自查。
```

不得复述 P4-PHYS-A/B/C/D/E 的完整历史。
