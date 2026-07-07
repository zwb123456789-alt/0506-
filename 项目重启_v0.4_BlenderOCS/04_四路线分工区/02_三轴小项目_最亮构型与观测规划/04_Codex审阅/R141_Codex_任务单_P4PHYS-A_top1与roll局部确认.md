# R141 Codex 任务单：P4-PHYS-A top-1 与 roll 局部确认

最后更新：2026-07-06  
任务类型：给执行端 Claude 的分阶段长程任务  
上游状态：R139 不接收旧 005/22；R140 作为 P4-PHYS 总路线图  
本轮目标：先锁定当前采样内的 top-1 最亮姿态，并判断是否需要小范围 roll/yaw/pitch 加密

补充裁决：执行本任务时必须同时读取 `R142_Codex_审阅_R141讨论稿部分采纳但不替代006A执行.md`、`R143_Codex_规划_R141_R142后固定几何最亮姿态确认执行方案.md` 与 `R144_Codex_技术路线_三轴小项目最亮构型与光路解释.md`。若需要给 Claude 一份可直接执行的完整提示词，使用 `R145_Codex_长任务提示词_执行R141生成23A006A.md`。R142 明确：Claude 讨论稿不替代 006A 正式执行；23A 包仍需建立；R141 应采用数值触发门，并在固定 phase63/L1-G1 sun/view 几何边界内确认 top-1。R143 明确：当前不做全局暴力遍历，而是围绕 R1 top 簇做局部 roll/yaw/pitch 加密，并保留 R4 鲁棒亮区作机制对照。R144 明确小项目全技术路线：先 top-1、再光路归因、再机制普遍性、最后 sun/view 扩展和路线二/三接口。

## 1. 为什么先做本轮

不能直接把 R140 一次性执行到底。原因：

```text
1. 当前 P1/P2/P3 已遍历离散 roll，但只覆盖 {-60,-45,-30,-15,0,+15,+30,+45,+60}。
2. 现有 top-1 只能先称为“当前采样网格内 single-pose top-1”，不能直接写成连续姿态空间全局最亮。
3. 如果 top-1 位于局部边界、roll 曲线峰值未被细化，或 top-N 中存在相近峰，需要先做小范围加密再谈物理光路归因。
4. 只有 top-1 和高亮簇稳定后，后续物理光路归因才有意义。
```

因此本轮不是材料整理，而是第一阶段决策任务：确认“现在能不能锁定 top-1”，以及“是否需要补一个很小的 roll/yaw/pitch 局部诊断”。

## 2. 任务代码

```text
three_axis_p4phys_a_top1_roll_confirmation
```

## 3. 输出位置

执行报告写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/006A_P4PHYS_top1_roll_confirmation_Claude执行报告.md
```

全部新结果写入：

```text
v0.4_results/23A_three_axis_p4phys_top1_roll_confirmation/
```

不得覆盖 19/20/21/22 号包。

## 4. 必读文件

按顺序读取：

```text
CLAUDE.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/00_路线冻结文件区/01_三轴小项目_最亮构型与观测规划指导文件.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R138_Codex_补充校正_三轴小项目最亮构型主目标与roll遍历口径.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R139_Codex_审阅_005不通过_旧P4需按最亮构型光路机制返工.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R140_Codex_任务单_P4PHYS最亮构型物理光路归因长程任务.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R142_Codex_审阅_R141讨论稿部分采纳但不替代006A执行.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R143_Codex_规划_R141_R142后固定几何最亮姿态确认执行方案.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R144_Codex_技术路线_三轴小项目最亮构型与光路解释.md
```

必须读取数据表：

```text
v0.4_results/19_three_axis_p1_seed_roll_scan/tables/p1_seed_roll_ocs_table.csv
v0.4_results/20_three_axis_p2_sparse_grid/tables/p2_sparse_grid_metrics.csv
v0.4_results/21_three_axis_p3_local_refinement/tables/p3_local_refinement_metrics.csv
v0.4_results/21_three_axis_p3_local_refinement/tables/p3_high_brightness_refined_candidates.csv
v0.4_results/21_three_axis_p3_local_refinement/tables/p3_region_summary.csv
```

若要判断是否能做局部加密，还需只读：

```text
v0.4_results/21_three_axis_p3_local_refinement/scripts/p3_render_local_refinement.py
v0.4_results/21_three_axis_p3_local_refinement/scripts/b_c_metrics.py
06_v0.4_code/02_blender/render_full_2664_shadow.py
06_v0.4_code/05_postprocess/run_full_postprocess.py
```

## 5. 允许与禁止

允许：

```text
1. 新建 23A 包内的汇总、审计、制图、可选局部加密脚本。
2. 全量读取并重聚合 P1/P2/P3 现有明细表。
3. 判断 top-1 是否稳定、是否位于当前采样边界、是否需要局部 roll/yaw/pitch 加密。
4. 若现有数据不足以锁定 top-1，可执行小范围诊断加密。
```

禁止：

```text
1. 不训练任何模型。
2. 不启动 R128、路线二/三/四或 T3/L2。
3. 不做全网格新渲染。
4. 不改 19/20/21/22 号包。
5. 不写成果区，不生成 Codex 审阅文件，不改 CLAUDE.md。
6. 本轮不做完整材料/表面/探测器光路归因；只做字段可行性预检。
```

## 6. 必做子任务

### A. top-1 / top-N 现有采样重聚合

输出：

```text
tables/p4physA_existing_global_top1.csv
tables/p4physA_existing_global_topN.csv
tables/p4physA_source_pack_coverage.csv
figures/p4physA_existing_topN_map.png/.pdf
text/p4physA_existing_top1_summary.md
```

必须回答：

```text
1. 当前 P1/P2/P3 已有采样内 single-pose top-1 是什么。
2. top-1 是否来自 P3 明细表的 yaw=245.0, pitch=+30.0, roll=+15。
3. top-10 是否集中在同一 R1 高亮簇，还是 R4 亮区也接近。
4. P1/P2/P3 之间是否存在量纲或来源不可比问题。
```

### B. roll 曲线与局部峰稳定性

输出：

```text
tables/p4physA_top1_roll_profile.csv
tables/p4physA_topN_cluster_roll_profiles.csv
tables/p4physA_local_peak_stability.csv
figures/p4physA_top1_roll_curve.png/.pdf
figures/p4physA_top_cluster_roll_curves.png/.pdf
```

必须回答：

```text
1. top-1 的 roll=+15 是否高于 roll=0 和 roll=+30。
2. top-1 是否处在 roll 采样边界；若不在边界，是否仍需要细化 roll。
3. R1 top 簇在 yaw/pitch 邻域是否稳定。
4. R4 roll-aggregated 高亮区是否在 single-pose 排名中接近 top-1。
```

### C. 是否需要小范围加密的决策

输出：

```text
tables/p4physA_refinement_need_decision.csv
tables/p4physA_refinement_candidate_matrix.csv
text/p4physA_refinement_decision.md
```

决策规则：

```text
若 top-1 与 top-2/top-3 差距很小，或 roll 曲线在 +15 附近尖锐，或局部最大可能落在 +10/+20 等未采样 roll，则需要加密。
若 top-1 稳定且邻近 roll 明显更暗，可先不加密，进入 P4-PHYS-B 光路归因。
```

### D. 可选小范围 roll/yaw/pitch 加密

只有 C 判定需要加密时才执行。先 smoke，再正式。

建议规模：

```text
R1 top 簇优先：
yaw ∈ {242.5,245.0,247.5}
pitch ∈ {27.5,30.0,32.5,35.0}
roll ∈ {+5,+10,+12.5,+15,+17.5,+20,+25}

必要时加入 R4 亮区对照：
yaw ∈ {145.0,147.5,150.0}
pitch ∈ {10.0,12.5,15.0}
roll ∈ {-30,-15,0,+15,+30}
```

规模上限：

```text
新增诊断渲染/后处理单位 <= 150。
若超过，优先保留 R1 top 簇 roll 细化，R4 只保留少量对照。
```

输出：

```text
tables/p4physA_refined_top1_metrics.csv
tables/p4physA_refined_roll_profile.csv
figures/p4physA_refined_top1_roll_curve.png/.pdf
text/p4physA_refined_top1_summary.md
```

若未执行加密，必须说明“不执行”的证据。

### E. 光路归因可行性预检

本轮只做可行性预检，不做完整物理归因。

输出：

```text
audit/p4physA_light_path_field_availability.csv
text/p4physA_next_physical_attribution_plan.md
```

必须回答：

```text
1. 下一轮 P4-PHYS-B 能否用已有 EXR/NPY/JSON 做 part/material 归因。
2. 是否需要新增 object/material/normal/depth pass。
3. 若需要，预计只对哪些姿态做诊断，规模多少。
```

### F. 验收与报告

输出：

```text
tables/p4physA_gate_matrix.csv
audit/generated_files_manifest.csv
audit/numeric_path_consistency_check.csv
audit/redline_self_check.csv
text/codex_review_checklist_for_006A.md
```

006A 报告必须简洁回答：

```text
1. 当前采样内 top-1 是什么。
2. roll 是否已遍历：现有遍历到什么程度，是否足以锁定 top-1。
3. 是否执行了局部加密；若执行，新 top-1 是否改变。
4. 下一步是否进入 P4-PHYS-B 光路归因，还是继续小范围加密。
```

## 7. 接收标准

最低接收：

```text
1. 23A 包和 006A 报告存在。
2. 当前采样内 top-1 / top-N 明确。
3. roll profile 明确，说明是否需要更细 roll。
4. 若需要加密，给出受控矩阵并完成或明确阻塞。
5. 给出下一轮物理光路归因可行性预检。
6. 未训练，未启动 R128，未写成果区，未改 CLAUDE.md。
```

强接收：

```text
1. top-1 在当前采样或加密后稳定，可作为 P4-PHYS-B 物理归因对象。
2. 明确回答“是否还需要继续遍历 roll”。
3. 给出下一轮 part/material/surface/detector path 归因的最小任务范围。
```

## 8. 当前阶段门状态

```text
旧 005/22：不接收。
R140：作为总路线图，不一次性执行。
当前执行：R141 / P4-PHYS-A / 006A。
R128：继续挂起。
三轴小项目：未收口。
```
