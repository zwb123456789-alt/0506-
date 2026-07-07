# R140 Codex 任务单：P4-PHYS 最亮构型物理光路归因长程任务

最后更新：2026-07-06  
任务类型：给执行端 Claude 的长程物理诊断任务  
上游状态：R139 已裁定旧 005/22 号包不接收为当前 P4  
本文件定位：取代 R139 第 4 节偏重表格重聚合的窄返工提示词，作为 P4-PHYS 总路线图。

后续拆分：考虑到一次性完成 top-1 锁定、局部 roll 加密判断、物理光路归因和机制普遍性验证过长，实际执行拆为阶段门。立即执行 `R141_Codex_任务单_P4PHYS-A_top1与roll局部确认.md`，先回答“当前采样内 top-1 是什么、是否需要围绕 roll/yaw/pitch 做小范围加密”。R141 通过后，再下达 P4-PHYS-B 物理光路归因任务。

## 1. 核心目标

本轮不是材料整理，也不是再做 observation planning summary。

你的目标是向三轴小项目的最终科学问题推进：

```text
在已知卫星模型和前向光学模型下，
确认哪个 yaw/pitch/roll + sun/view 构型最亮；
解释此时光从哪里入射、照到卫星哪个部位、哪种材料/表面，
再沿什么方向进入探测器；
并检验同类物理光路机制是否普遍对应一片高亮姿态/几何候选。
```

本轮允许做受控的物理诊断和必要的 top-N 诊断渲染/重后处理；不允许训练、不允许启动 R128、不允许路线二/三/四扩展。

## 2. 任务代码

```text
three_axis_p4_phys_brightest_light_path_attribution
```

## 3. 输出位置

执行报告写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/006_P4PHYS_brightest_light_path_attribution_Claude执行报告.md
```

全部新结果写入：

```text
v0.4_results/23_three_axis_p4_phys_light_path_attribution/
```

不得覆盖 19/20/21/22 号包。

## 4. 必读文件与代码

先按顺序读取：

```text
CLAUDE.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/00_路线冻结文件区/01_三轴小项目_最亮构型与观测规划指导文件.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R137_Codex_任务单_P4_observation_planning_synthesis.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R138_Codex_补充校正_三轴小项目最亮构型主目标与roll遍历口径.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R139_Codex_审阅_005不通过_旧P4需按最亮构型光路机制返工.md
```

必须审计这些代码/配置，确认可用字段和可扩展点：

```text
06_v0.4_code/00_config/materials_v0_4.py
06_v0.4_code/01_geometry/geometry_loader.py
06_v0.4_code/02_blender/render_full_2664_shadow.py
06_v0.4_code/05_postprocess/ocs_integration_v0_4.py
06_v0.4_code/05_postprocess/image_response_v0_4.py
v0.4_results/21_three_axis_p3_local_refinement/scripts/p3_render_local_refinement.py
v0.4_results/21_three_axis_p3_local_refinement/scripts/b_c_metrics.py
```

必须读取数据表：

```text
v0.4_results/19_three_axis_p1_seed_roll_scan/tables/p1_seed_roll_ocs_table.csv
v0.4_results/20_three_axis_p2_sparse_grid/tables/p2_sparse_grid_metrics.csv
v0.4_results/21_three_axis_p3_local_refinement/tables/p3_local_refinement_metrics.csv
v0.4_results/21_three_axis_p3_local_refinement/tables/p3_high_brightness_refined_candidates.csv
v0.4_results/22_three_axis_p4_observation_planning/tables/p4_planning_candidate_roles.csv
```

旧 22 号包只作为辅助角色分层参考，不作为最高标准依据。

## 5. 允许与禁止

允许：

```text
1. 新建 23 号包中的诊断脚本、汇总脚本、制图脚本。
2. 从 P1/P2/P3 明细表重聚合 top-1 / top-N / roll profile。
3. 审计 Blender 场景、几何、材料、对象命名和渲染/后处理通道。
4. 对 top-1、top-N 和少量机制邻域候选做受控诊断渲染或重后处理。
5. 为了归因可新增只在 23 号包使用的派生 Blender 诊断脚本。
6. 若已有 EXR/NPY/JSON 足够，优先用已有产物做像素级归因，减少重渲染。
```

禁止：

```text
1. 不训练任何模型。
2. 不启动 R128、路线二、路线三、路线四或 T3/L2。
3. 不改 19/20/21/22 号包。
4. 不改原始 06_v0.4_code 文件；如需派生脚本，只复制/新建到 23 号包 scripts/。
5. 不做全网格新渲染；诊断渲染只允许围绕 top-1/top-N/机制邻域。
6. 不把无法追溯的 part/material/surface 字段编造成已知。
7. 不写成果区，不生成 Codex 审阅文件，不改 CLAUDE.md。
```

受控规模建议：

```text
top-N 明细重聚合：全量读表，零渲染。
物理归因诊断姿态：优先 top-1、top-10、R4 roll-aggregated 亮区代表、C09、R3 对照；总姿态数建议 <= 40。
若采用 per-object/per-material isolation 渲染，必须先 smoke 1 个姿态，估算规模，再控制总诊断渲染单位 <= 300。
```

## 6. 必做子任务

### A. 代码与字段可用性审计

输出：

```text
audit/p4phys_code_audit.csv
audit/p4phys_required_field_audit.csv
text/p4phys_diagnostic_feasibility.md
```

必须回答：

```text
1. 当前后处理产物中是否已有 per-pixel / per-part / per-material 贡献信息。
2. 当前 Blender 场景中对象、部件、材料名称是否可追溯。
3. 是否能输出 object/material ID pass、normal pass、depth pass 或等价诊断。
4. 若不能直接输出，最小可行替代方案是什么：per-object isolation、per-material isolation、mask pass、或只给字段缺口。
```

### B. top-1 / top-N 亮度重聚合

输出：

```text
tables/p4phys_global_brightest_pose_table.csv
tables/p4phys_global_brightest_topN.csv
tables/p4phys_brightest_roll_profile.csv
tables/p4phys_roll_aggregated_brightest_region.csv
figures/p4phys_global_brightest_pose_panel.png/.pdf
text/p4phys_brightest_configuration_summary.md
```

必须以 P1/P2/P3 明细表验证：

```text
single-pose top-1 是否为 yaw=245.0, pitch=+30.0, roll=+15；
top-N 是否集中在 R1 yaw245-247.5 / pitch+30~40 / roll+15；
R4 yaw147.5/+12.5 是 roll-aggregated 高亮区还是 single-pose top-1；
top-1 与 C09 亮-信息折中点的角色差异。
```

### C. 物理光路归因诊断

优先实现一个可审计的归因方法。可选路径按优先级：

```text
1. 读取已有像素级/通道级产物，计算 top-1 的主要贡献像素、太阳入射方向、相机方向和 BRDF 响应。
2. 若 Blender 可输出 object/material/normal/depth pass，则为 top-1/top-N 做诊断渲染。
3. 若 pass 不可用，则对少量 top 姿态做 per-object 或 per-material isolation 诊断，估计各部件/材料贡献占比。
4. 若仍不可行，必须输出具体阻塞和最小代码改动需求，不得假装完成物理解释。
```

输出：

```text
tables/p4phys_light_path_trace.csv
tables/p4phys_surface_material_attribution.csv
tables/p4phys_detector_path_trace.csv
tables/p4phys_part_material_contribution.csv
figures/p4phys_top1_light_path_schematic.png/.pdf
figures/p4phys_top1_part_material_contribution.png/.pdf
text/p4phys_light_path_explanation.md
```

必须回答：

```text
1. top-1 的太阳入射方向在目标/相机坐标中是什么。
2. 哪个部件、哪种材料/表面对 OCS_total 贡献最大。
3. 该贡献是镜面/glint、漫反射、遮挡边界还是几何投影导致。
4. 反射/散射后如何进入探测器，视线方向与表面法向/反射方向关系是什么。
5. 上述判断哪些是直接计算，哪些只是 proxy。
```

### D. 高亮机制普遍性验证

基于 C 的归因结果定义机制签名，例如：

```text
dominant_part + dominant_material + incident_angle_bin + view_angle_bin + glint/saturation state
```

输出：

```text
tables/p4phys_bright_mechanism_signature.csv
tables/p4phys_bright_mechanism_generality_check.csv
tables/p4phys_mechanism_candidate_cluster.csv
figures/p4phys_mechanism_brightness_distribution.png/.pdf
figures/p4phys_mechanism_consistency_map.png/.pdf
text/p4phys_mechanism_generality_summary.md
```

必须回答：

```text
1. 与 top-1 同机制签名的候选是否普遍高亮。
2. top-N 中同机制候选占比是多少。
3. 同机制候选的亮度中位数、最小值、最大值和 rank 分布是什么。
4. 机制不普遍时，top-1 是否是局部 glint、饱和、遮挡边界或数值尖峰。
5. 若机制普遍，给出“高亮机制”的物理解释句。
```

### E. 与旧 P4 角色分层的关系

输出：

```text
tables/p4phys_auxiliary_role_reconciliation.csv
text/p4phys_observation_planning_reinterpreted_as_auxiliary.md
```

必须重新解释：

```text
C09 只是亮-信息折中/观测辅助候选，不是最亮主目标；
C01-C08 是否与 top-1 高亮机制一致；
R4 roll-aggregated bright region 是否与 top-1 机制一致；
R3/R2/R5 只作为负面对照或暗/中性对照。
```

### F. 验收与报告

输出：

```text
tables/p4phys_gate_matrix.csv
audit/generated_files_manifest.csv
audit/numeric_path_consistency_check.csv
audit/redline_self_check.csv
text/codex_review_checklist_for_006.md
```

006 报告必须短而完整，只写：

```text
1. 执行了哪些代码审计和诊断。
2. 是否做了新诊断渲染，规模多少，为什么必要。
3. top-1 是什么。
4. 光从哪里入射，照到哪里，什么材料/表面贡献最大，如何进探测器。
5. 同类机制是否普遍高亮。
6. 哪些字段仍然缺失，是否需要下一轮最小新增诊断。
7. 红线自检。
```

## 7. 接收标准

最低接收：

```text
1. 23 号包和 006 报告存在。
2. top-1/top-N/roll-aggregated 高亮区域分清。
3. 代码审计说明当前能否做 part/material/surface/detector path 归因。
4. 至少对 top-1 给出可审计的光路解释或明确不可归因的字段缺口。
5. 完成机制普遍性验证，或明确说明只能进行 proxy 验证并给出原因。
6. 旧 P4 角色分层被降为辅助标注。
7. 未训练，未启动 R128，未写成果区，未改 CLAUDE.md。
```

强接收：

```text
1. top-1 主要贡献部件/材料/表面有定量贡献占比。
2. 反射/入射/探测器方向关系有角度或向量证据。
3. top-1 所属机制在 top-N 或邻域中被证明为普遍高亮，或被清楚判定为局部尖峰。
4. 输出足以支撑作者回答“卫星什么姿态/几何最亮，光从哪里来、照到哪里、怎么进探测器”。
```

## 8. 当前阶段门状态

```text
旧 005/22：不按当前 P4 接收，只作辅助历史材料。
R139：审阅结论仍有效，但其窄返工提示词被 R140 取代。
R140：作为 P4-PHYS 总路线图，不作为一次性直接执行任务。
下一步：Claude 执行 R141 / P4-PHYS-A / 006A。
R128：继续挂起。
三轴小项目：未收口。
```
