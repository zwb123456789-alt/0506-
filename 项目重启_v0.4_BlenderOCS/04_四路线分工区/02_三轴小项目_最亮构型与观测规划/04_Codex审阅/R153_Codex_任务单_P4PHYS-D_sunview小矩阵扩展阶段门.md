# R153 Codex 任务单：P4-PHYS-D sun/view 小矩阵扩展阶段门

最后更新：2026-07-06  
任务类型：给 Claude 的长程执行任务  
上游依据：R152 接收 008 / 25 包，fixed phase63/L1-G1 机制普遍性为 PARTIAL_GENERALITY  
本轮目标：受控检验 top-1 与高亮机制对 sun/view 几何变化的稳定性  

## 1. 本轮目标

R148 已确认 fixed `phase63/L1-G1` 下 top-1：

```text
yaw=245.0
pitch=+27.5
roll=+15
ocs_total=0.2088904828
```

R150/R152 已确认：

```text
1. top-1 主光路机制为金属主体大面元近镜面对齐探测器。
2. 在 fixed phase63/L1-G1 候选池中，金属近镜面对齐机制普遍富集于高亮候选。
3. 隐身板增量只解释 top-1 相对 R4 的排序，不是普遍高亮机制。
```

本轮 P4-PHYS-D 要回答：

```text
当 sun/view 几何从 phase63/L1-G1 做小范围或代表性变化时，
当前 top-1 姿态是否仍亮？
高亮机制是否仍是金属近镜面对齐？
最亮姿态是否明显迁移？
```

本轮是 **sun/view 小矩阵扩展阶段门**，不是全局 sun/view 搜索。

## 2. 重要边界

必须写清：

```text
1. 本轮允许少量新增渲染，但必须规模受控。
2. 本轮不做全 sun/view 全局最亮搜索。
3. 本轮不启动 R128、路线二/三/四、训练或论文正文最终改写。
4. material-level 仍为 proxy；material pass 不作为本轮前置。
5. 本轮结果最多判断是否进入更大 sun/view 搜索或小项目收口裁决。
```

## 3. 输出位置

执行报告写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/009_P4PHYS_D_sunview_small_matrix_Claude执行报告.md
```

新结果包写入：

```text
v0.4_results/26_three_axis_p4phys_d_sunview_small_matrix/
```

建议目录结构：

```text
audit/
tables/
figures/
text/
scripts/
logs/
render/
postprocess/
```

不得改写 20/21/23A/23B/24/25 包。

## 4. 必读文件

按顺序读取：

```text
CLAUDE.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/00_路线冻结文件区/01_三轴小项目_最亮构型与观测规划指导文件.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/05_三轴小项目最亮构型与光路解释技术路线_R144依据.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/06_P4PHYS-A_fixed几何top1确认_R148通过.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/07_P4PHYS-B_top1光路归因_R150通过.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R150_Codex_审阅_007通过_P4PHYSB光路归因接收并放行P4PHYSC.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R152_Codex_审阅_008通过_PARTIAL_GENERALITY并放行P4PHYSD.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/008_P4PHYS_C_mechanism_generality_Claude执行报告.md
```

必须读取机制与候选表：

```text
v0.4_results/25_three_axis_p4phys_c_mechanism_generality/tables/p4physC_candidate_mechanism_labels.csv
v0.4_results/25_three_axis_p4phys_c_mechanism_generality/tables/p4physC_top_quantile_enrichment.csv
v0.4_results/25_three_axis_p4phys_c_mechanism_generality/tables/p4physC_claim_boundary_table.csv
v0.4_results/24_three_axis_p4phys_b_light_path_attribution/tables/p4physB_mechanism_signature_seed.csv
```

必须审计代码/配置：

```text
06_v0.4_code/00_config/config_v0_4.py
06_v0.4_code/00_config/materials_v0_4.py
06_v0.4_code/01_geometry/geometry_loader.py
06_v0.4_code/05_postprocess/ocs_integration_v0_4.py
```

## 5. sun/view 小矩阵设计

本轮只做小矩阵，不做全局搜索。优先选择 5 个观测几何：

```text
G0_baseline: phase63 / L1-G1，SUN=[1,0,0.3]，DET=[0.5,-1,0.1]（可复用，不新渲染）
G1_sun_plus:  在 baseline 附近小幅改变太阳方向
G2_sun_minus: 在 baseline 附近反向小幅改变太阳方向
G3_view_plus: 在 baseline 附近小幅改变探测器方向
G4_view_minus: 在 baseline 附近反向小幅改变探测器方向
```

如现有代码已有 phase/geometry registry，应优先沿用 registry 方式新增临时本包配置，不改全局配置。若没有现成 registry，允许在 26 包脚本中定义本轮局部 `SUN/DET` 向量，并写明坐标口径与归一化方式。

建议扰动尺度：

```text
太阳方向与探测器方向相对 baseline 角距约 5°–10°。
```

若实现小扰动成本过高，可退而使用现有代码中已定义的相邻 phase / L1-G? 几何，但必须说明等效角距。

## 6. 姿态候选设计

每个几何只评估少量固定姿态，不做全姿态搜索。

必选姿态：

```text
A. top-1：yaw=245.0, pitch=27.5, roll=+15
B. R4 robust：yaw=147.5, pitch=12.5, roll=0
C. R3 negative：yaw=55.0, pitch=60.0, roll=0
```

建议追加姿态：

```text
D. top-1 邻域候选 4–6 个：来自 23A/23B top-N，覆盖 roll=+12.5/+15/+17.5 与 pitch/yaw 邻点。
E. R4 同簇候选 2–4 个：来自 25 包 near_specular_metal=1 的 R4/R1 代表点。
F. non-mechanism bright-edge 候选 2–4 个：25 包中 near_specular_metal=0 但 OCS 较高的边缘点，用于检验阈值边界。
```

规模上限：

```text
几何数 <= 5
姿态数 <= 16
新增渲染单元 <= 80 poses × camera/sun views
```

如果需要 roll/yaw/pitch 全新搜索，必须停止并返回 Codex，不能自行扩大。

## 7. 必做子任务

### A. 设计与预检

输出：

```text
audit/input_manifest.csv
audit/sunview_geometry_manifest.csv
audit/pose_candidate_manifest.csv
audit/render_plan_manifest.csv
audit/redline_precheck.csv
```

必须回答：

```text
1. 使用了哪些 sun/view 几何，角距 baseline 多大。
2. 使用了哪些姿态，来源是什么。
3. 哪些点复用 baseline，哪些点新增渲染。
4. 新增渲染规模是否低于上限。
```

### B. smoke 测试

先做最小 smoke：

```text
1 个非 baseline 几何 × top-1 / R4 / R3 三个姿态
```

输出：

```text
logs/p4physD_smoke_render.log
logs/p4physD_smoke_postprocess.log
tables/p4physD_smoke_metrics.csv
```

smoke 必须确认：

```text
camera/sun EXR 生成；
IndexOB/Normal/Position/Depth 可读；
ocs.json 生成；
无 failed 渲染。
```

smoke 失败则停止，不跑正式矩阵。

### C. 正式小矩阵渲染与后处理

输出：

```text
tables/p4physD_render_manifest.csv
tables/p4physD_metrics.csv
audit/render_postprocess_status.csv
logs/p4physD_render.log
logs/p4physD_postprocess.log
```

必须记录：

```text
geometry_id
SUN / DET
pose_label / yaw / pitch / roll
ocs_total
ocs_per_part
image_usable
failed_reason
```

### D. 跨几何 top-1 与机制迁移分析

复用 24/25 包机制签名算法，输出：

```text
tables/p4physD_cross_geometry_rank_table.csv
tables/p4physD_top1_stability_table.csv
tables/p4physD_mechanism_signature_by_geometry.csv
figures/p4physD_ocs_by_geometry_pose.png
figures/p4physD_ocs_by_geometry_pose.pdf
figures/p4physD_mechanism_signature_shift.png
figures/p4physD_mechanism_signature_shift.pdf
text/p4physD_sunview_stability_result.md
```

必须回答：

```text
1. baseline top-1 在其它几何下是否仍高亮。
2. 每个新几何下最高亮候选是谁，是否迁移。
3. 高亮候选是否仍满足 near_specular_metal。
4. R4 是否仍是同机制高亮对照。
5. R3 是否仍保持负面对照。
6. 隐身板增量是否随几何变化保持、减弱或消失。
```

### E. 下一步裁决接口

输出：

```text
tables/p4physD_claim_boundary_table.csv
text/p4physD_next_step_recommendation.md
text/codex_review_checklist_for_009.md
```

必须给出三类建议之一：

```text
1. SUNVIEW_STABILITY_SUPPORTED：
   小矩阵中金属近镜面机制稳定，top-1 或同簇候选保持高亮，可考虑三轴小项目收口或有限扩大。
2. SUNVIEW_DEPENDENT_BUT_MECHANISTIC：
   最亮姿态随 sun/view 迁移，但迁移仍由金属近镜面对齐解释；建议设计受控 sun/view 搜索。
3. SUNVIEW_UNSTABLE_OR_INCONCLUSIVE：
   机制在新几何下不稳定或样本不足；建议补小矩阵或回退机制定义。
```

## 8. 验收与报告

必须输出：

```text
tables/p4physD_gate_matrix.csv
audit/generated_files_manifest.csv
audit/redline_self_check.csv
audit/numeric_consistency_check.csv
```

报告写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/009_P4PHYS_D_sunview_small_matrix_Claude执行报告.md
```

报告必须简洁回答：

```text
1. 本轮 sun/view 小矩阵如何设计。
2. 新增渲染规模是多少。
3. top-1 在其它几何下是否仍亮。
4. 最亮候选是否随几何迁移。
5. 金属近镜面机制是否仍解释高亮。
6. R4/R3 对照是否保持。
7. 是否建议小项目收口、扩大 sun/view，或补 material pass。
```

## 9. 红线

```text
不得训练。
不得启动 R128。
不得启动路线二/三/四。
不得做全 sun/view 全姿态搜索。
不得新增超过 80 个姿态单元。
不得改 20/21/23A/23B/24/25 包。
不得写成果区，不改 CLAUDE.md，不生成 Codex 审阅文件。
不得把小矩阵结果写成所有 sun/view 全局结论。
不得把 material proxy 写成真实 material-level attribution。
```

## 10. 接收标准

最低接收：

```text
1. 26 包存在。
2. 009 报告存在。
3. sun/view 几何与姿态候选设计清楚。
4. smoke 通过后才执行正式矩阵。
5. 新增渲染规模受控。
6. 跨几何 OCS 与机制签名表存在。
7. 给出 SUNVIEW_STABILITY_SUPPORTED / SUNVIEW_DEPENDENT_BUT_MECHANISTIC / SUNVIEW_UNSTABLE_OR_INCONCLUSIVE 之一。
8. 红线全 PASS。
```

强接收：

```text
1. 每个几何下 top 候选、top-1 原姿态、R4、R3 均可比较。
2. 机制签名复用 24/25 包口径且有数值一致性检查。
3. 能清楚判断“机制稳定”与“姿态迁移”之间的关系。
4. 给出小项目最终收口或后续有限扩大的一步建议。
```

