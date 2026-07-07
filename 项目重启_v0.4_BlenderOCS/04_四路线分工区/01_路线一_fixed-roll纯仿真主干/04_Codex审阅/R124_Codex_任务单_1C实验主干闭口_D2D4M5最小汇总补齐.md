# R124 Codex 任务单：路线一 C 实验主干闭口，D2/D4/M5 最小汇总补齐

最后更新：2026-07-01  
任务类型：给执行端 Claude 的长程闭口补齐提示词  
上游阶段门：R123 已通过 107，Results/SI 图表与写作准备包接收  
执行端报告必须写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/108_1C实验主干闭口_D2D4M5最小汇总补齐_Claude执行报告.md
```

本文件是 Codex 调度/提示词文件，保留在 `04_Codex审阅/`。执行端不得把报告、结果或裁决文件写入 `04_Codex审阅/`。

---

## 0. 给 Claude 的总提示词

你现在执行路线一 C 的实验主干闭口补齐任务：

```text
1C_closure_D2_D4_M5_minimal_aggregation
```

目标是在**不新训练、不新渲染、不改旧脚本、不改旧结果**的前提下，用现有 10/11/12/13/14/15 号结果与中间量，补齐 R113 技术路线中尚未独立闭口的三个汇总门：

```text
D2: image_only / ocs_only / joint 三通道 top-k overlap、disagreement、互补性闭口。
D4: yaw/pitch 姿态空间可观测性地图、易混淆区域、低信息区域闭口。
M5: P-INT / P-EXT / P-DB 三协议对比门闭口。
```

本轮可以一次性生成“路线一 C 实验主干闭口候选包”，但你不能自行宣布路线一 C 正式闭口，也不能启动三轴小项目。最终闭口裁决和是否进入三轴小项目，由作者把 108 报告交给 Codex 后进行 R125 审阅。

如果文件缺失、字段不一致、top-k 不可重建或结果显示 joint 无增量，你必须如实报告；不得为了闭口而改写口径。

---

## 1. 本轮允许与禁止

允许：

```text
1. 读取现有 CSV/NPZ/JSON/MD/PNG。
2. 从现有 per-attitude predictions、top-k、posterior-like、entropy、margin、P-DB top-k 中重聚合指标。
3. 生成新的汇总 CSV/JSON/MD/PNG/PDF。
4. 新增轻量汇总/制图脚本，只写入 16 号包 scripts/。
5. 对现有中间量做路径核验、字段审计和数字一致性核验。
```

禁止：

```text
1. 不新训练、不新渲染、不新后处理大矩阵。
2. 不改 split、不改姿态网格、不改模型、不做超参搜索。
3. 不修改旧脚本、旧 metrics、旧 samples、旧结果目录 10/11/12/13/14/15。
4. 不写成果区，不生成 Codex 审阅文件，不改 CLAUDE.md。
5. 不写最终论文正文、投稿摘要或投稿稿。
6. 不启动三轴小项目、T3/L2、路线二/三/四扩展。
7. 不把 P-EXT 写成已解决，不把 P-DB 写成真实观测反演成功率。
8. 不把 conformal 写成 Bayesian posterior 或最终概率校准。
9. 不把本轮自检写成路线一 C 已闭口；只能写“闭口候选包，等待 Codex 裁决”。
```

若上下文、输出长度或文件写入受限，必须按 `Part 1/2/3...` 分段输出或分段写入，直到报告和交付清单完整。

---

## 2. 必读文件

先按顺序读取，并在执行报告中列出已读文件清单。只引用关键结论，不复述长历史。

```text
CLAUDE.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/01_路线一C后续技术路线执行框架_R113通过.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R121_Codex_审阅_106通过_1C阶段性Results非正文证据包.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R123_Codex_审阅_107通过_1C-ResultsSI图表与写作准备包.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/08_路线一C阶段性Results非正文证据包_R121通过.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/09_路线一C-ResultsSI图表与写作准备包_R123通过.md
```

按需读取结果目录：

```text
v0.4_results/10_b6_circular_regression_fix01/
v0.4_results/11_l1m2_multigeometry_ocs/
v0.4_results/12_l1m3_degraded_mroll/
v0.4_results/13_l1d3_confidence_pdb/
v0.4_results/14_route1c_stage_results_pack/
v0.4_results/15_route1c_results_si_preparation_pack/
```

重点定位以下中间量，若路径/字段不同，以实际文件为准并在 manifest 中记录：

```text
11_l1m2_multigeometry_ocs/runs/*/samples_test_*.csv
11_l1m2_multigeometry_ocs/runs/*/samples_test_*.npz
11_l1m2_multigeometry_ocs/runs/*/metrics_test_*.json
13_l1d3_confidence_pdb/pdb/l1d3_pdb_retrieval_per_query.csv
13_l1d3_confidence_pdb/consistency/l1d3_neural_pdb_joined_per_attitude.csv
13_l1d3_confidence_pdb/consistency/l1d3_complementarity_cases.csv
13_l1d3_confidence_pdb/hardcases/l1d3_hardcase_index.csv
```

---

## 3. 总体交付路径

所有本轮新材料写入：

```text
v0.4_results/16_route1c_closure_d2d4_m5/
```

建议结构：

```text
v0.4_results/16_route1c_closure_d2d4_m5/
  tables/
  figures/
  text/
  scripts/
  audit/
```

执行报告写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/108_1C实验主干闭口_D2D4M5最小汇总补齐_Claude执行报告.md
```

---

## 4. 子任务 A：中间量可用性审计

先做路径与字段审计，确认 D2/D4/M5 是否可用现有中间量完成。

必须检查：

```text
1. P-INT G1/G3/G5 下 image_only / ocs_only / joint 是否都有 per-attitude samples_test_final/best。
2. P-EXT G1/G3/G5 下 ocs_only 是否有 per-attitude samples 或至少可汇总指标。
3. 每个 samples 是否含 record_id 或可对齐键、yaw_true/pitch_true、yaw_pred/pitch_pred、yaw_error/circular error、top-k 或 score/margin/entropy 字段。
4. 若 neural top-k 缺失，是否能从保存的 npz/posterior-like score 重建；若不能，D2 top-k overlap 降级为 top-1 / hit@30 / disagreement，并明确缺口。
5. P-DB per-query 是否含 topk10_idx、nearest_distance、margin、yaw/pitch 真值或可对齐 record_id。
6. joined per-attitude 是否可支持 yaw/pitch map。
```

输出：

```text
audit/intermediate_availability_audit.csv
audit/intermediate_availability_audit.md
audit/input_file_manifest.csv
```

若发现缺口，不要停止整个任务；先尽可能完成可支持部分，并把缺口列为 R125 裁决问题。

---

## 5. 子任务 B：D2 三通道互补性闭口

目标：补齐 R113 §3/§4 中 D2 要求的 image vs OCS vs joint 互补性，而不只停留在 neural vs P-DB。

使用对象：

```text
P-INT G1/G3/G5: image_only / ocs_only / joint
优先 best 口径，同时保留 final 摘要或说明为何不使用 final。
如 top-k 可用，计算 top-k overlap；如 top-k 不可用，计算 top-1/hit/disagreement 替代并标注。
```

至少输出这些统计：

```text
1. 三通道 yaw hit@30、cMAE、pitch error 基础表。
2. pairwise top-k overlap/Jaccard：image-ocs、image-joint、ocs-joint。
3. pairwise disagreement：一个对一个错、两者都错、两者都对。
4. oracle hit@30：image ∪ ocs、image ∪ joint、ocs ∪ joint、image ∪ ocs ∪ joint。
5. joint incremental value：joint-only correct、image-only correct、ocs-only correct，按 G1/G3/G5。
6. hard cases：image wrong but ocs/P-DB correct；ocs wrong but image correct；joint fails despite branch success。
```

输出：

```text
tables/d2_three_channel_metrics_summary.csv
tables/d2_pairwise_topk_overlap.csv
tables/d2_pairwise_disagreement.csv
tables/d2_oracle_increment_summary.csv
tables/d2_hardcase_examples.csv
figures/d2_three_channel_hit_cmae.png/.pdf
figures/d2_overlap_disagreement_heatmap.png/.pdf
figures/d2_oracle_increment_bars.png/.pdf
text/d2_complementarity_closure_summary.md
```

闭口判断必须诚实：

```text
如果 joint 稳定优于 image_only，写“joint 增量在当前口径可见”。
如果 joint 无稳定增量，写“joint 强互补性仍未闭口，需 P-INT-hard/degraded-severe 裁决”。
无论哪种，都不能写真实反演成功。
```

---

## 6. 子任务 C：D4 姿态空间可观测性地图闭口

目标：把已有 per-attitude 坐标与误差组织成独立 D4 可观测性地图成果。

使用对象：

```text
P-INT G1/G3/G5 ocs_only / image_only / joint per-attitude error
P-DB per-query error
P-EXT ocs_only stress test error
hardcase index
```

至少输出：

```text
1. yaw × pitch 网格上的 error heatmap：ocs_only G1/G3/G5、P-DB G5、image_only G5、joint G5。
2. low-error / medium-error / high-error 区域分类表，阈值可用 yaw hit@30 与 cMAE 分档。
3. 易混淆区域：P-DB nearest_distance 小但 yaw error 大、neural margin 高但 error 大、P-EXT 坍缩区域。
4. 几何增益地图：G5 error - G1 error 或 G1->G5 改善量，显示哪些姿态区被多几何救回。
5. 与 hardcase index 的交叉统计：ocs-hard / image-hard / disagreement-hard / ambiguous-flux / robust-easy 在 yaw/pitch 区域中的分布。
```

输出：

```text
tables/d4_observability_region_stats.csv
tables/d4_hardcase_region_cross_tab.csv
tables/d4_geometry_gain_by_attitude.csv
figures/d4_error_maps_ocs_g1_g3_g5.png/.pdf
figures/d4_error_maps_image_joint_pdb.png/.pdf
figures/d4_geometry_gain_map.png/.pdf
figures/d4_hardcase_region_map.png/.pdf
text/d4_observability_map_closure_summary.md
```

边界：

```text
只能写 model-known simulated 姿态空间可观测性地图。
不能写真实天空观测可观测性地图。
不能写三轴小项目已完成。
```

---

## 7. 子任务 D：M5 三协议对比门闭口

目标：把 P-INT / P-EXT / P-DB 放在一个反演协议边界矩阵里闭口。

必须对比：

```text
P-INT neural ocs_only: G1/G3/G5 clean 主线。
P-EXT neural ocs_only: G1/G3/G5 yaw-block stress test。
P-DB template retrieval: G1/G3/G5 clean + degraded mild/moderate，如已有。
可选：image_only/joint P-INT 作为通道对照，但不要让 image 天花板掩盖 OCS 主线。
```

至少输出：

```text
1. protocol × geometry × method 的 cMAE / hit@30 表。
2. 协议边界矩阵：哪些条件下成立、哪些条件下坍缩、哪些只是 template retrieval。
3. 三协议主结论：
   - P-INT: 多几何 OCS 正结果。
   - P-EXT: strict yaw-block 仍坍缩。
   - P-DB: model-known simulated template retrieval 显示可检索 yaw 信息。
4. 论文可写/不可写口径表。
```

输出：

```text
tables/m5_protocol_comparison_metrics.csv
tables/m5_protocol_boundary_matrix.csv
tables/m5_allowed_forbidden_protocol_claims.csv
figures/m5_protocol_comparison_panel.png/.pdf
text/m5_protocol_gate_closure_summary.md
```

---

## 8. 子任务 E：路线一 C 实验主干闭口候选总表

目标：对照 R113 的 M1-M5/M-roll 技术路线，生成“闭口候选总表”，供 Codex R125 裁决。

必须逐项列：

```text
M1/F1 单几何下界：完成证据、路径、是否阻塞。
M2/L1 多几何主线：完成证据、路径、是否阻塞。
M3 clean/degraded：完成证据、路径、是否阻塞。
M4 D2/D3/D4：D2、D3、D4 分项完成证据、路径、是否阻塞。
M5 P-EXT/P-INT/P-DB：完成证据、路径、是否阻塞。
M-roll：完成证据、边界、是否阻塞。
L2/T3：为何不阻塞路线一 C 主干闭口。
三轴小项目：是否可作为下一阶段候选，但不得自行启动。
```

输出：

```text
tables/route1c_closure_gate_matrix.csv
text/route1c_experimental_closure_candidate_summary.md
text/remaining_blockers_vs_enhancements.md
```

分类规则：

```text
BLOCKER: 不补就不能判路线一 C 实验主干闭口。
ENHANCEMENT: 可增强论文或后续路线，但不阻塞实验主干闭口。
FUTURE_ROUTE: 三轴小项目、L2/T3、路线二三四等后续方向。
```

---

## 9. 子任务 F：审计与红线自检

输出：

```text
audit/numeric_consistency_check.csv
audit/generated_files_manifest.csv
audit/redline_self_check.csv
text/codex_review_checklist_for_108.md
```

红线自检至少包含：

```text
1. 未新训练/新渲染/新后处理大矩阵。
2. 未改旧脚本/旧 metrics/旧 samples/旧结果目录。
3. 未写成果区/未生成 Codex 审阅文件/未改 CLAUDE.md。
4. 未写最终论文正文/投稿摘要。
5. 未启动三轴小项目、T3/L2 或路线二三四。
6. 未把路线一 C 写成已闭口，只写闭口候选等待 Codex。
7. 未把 P-EXT 写成已解决。
8. 未把 P-DB 写成真实观测反演成功率。
9. 未把 conformal 写成最终概率校准。
10. 保留 joint 是否有增量的诚实结论。
```

---

## 10. 执行报告结构

执行报告写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/108_1C实验主干闭口_D2D4M5最小汇总补齐_Claude执行报告.md
```

报告必须包含：

```text
1. 任务结论摘要：完成 / 部分完成 / 阻塞。
2. 已读文件与遵守红线。
3. 新增脚本清单：路径、用途、是否改旧脚本。
4. 中间量可用性审计摘要。
5. D2 三通道互补性闭口摘要。
6. D4 可观测性地图闭口摘要。
7. M5 三协议对比门摘要。
8. 路线一 C 实验主干闭口候选总表摘要。
9. 数字一致性与 manifest 摘要。
10. 未完成项、阻塞项、增强项。
11. 红线自检。
12. 交给 Codex R125 审阅的裁决问题清单。
```

---

## 11. 成功判据

最低接收标准：

```text
1. 16 号结果包目录存在，结构清楚。
2. 中间量可用性审计完成。
3. D2 三通道互补性至少完成 top-1/hit/disagreement/oracle；若 top-k 不可用，明确原因。
4. D4 至少完成 yaw/pitch error map、区域统计、hardcase 交叉统计。
5. M5 至少完成 P-INT/P-EXT/P-DB 对比表和边界矩阵。
6. route1c_closure_gate_matrix.csv 完成。
7. redline_self_check.csv 完成。
8. 执行报告写入正确路径，未写成果区、未生成 Codex 审阅文件、未改 CLAUDE.md。
```

强接收标准：

```text
1. D2 top-k overlap/Jaccard 成功完成。
2. D4 形成可直接用于后续论文/三轴小项目接口的可观测性地图。
3. M5 清楚回答 P-INT 正结果、P-EXT 坍缩、P-DB 可检索信息三者边界。
4. 闭口候选总表能让 Codex 直接裁决“路线一 C 实验主干是否闭口”。
5. 若仍有 BLOCKER，能直接改写成下一轮最小任务单；若只有 ENHANCEMENT/FUTURE_ROUTE，能支持 Codex 放行进入三轴小项目准备。
```

---

## 12. 最后交付提醒

执行完成后，只提交 16 号候选闭口包与 108 Claude 执行报告。不要自行把结果升级到成果区，不要生成 Codex 审阅文件，不要修改 `CLAUDE.md`，不要启动三轴小项目。

作者会把 108 报告路径交给 Codex，由 Codex 进行 R125 审阅，裁决：

```text
1. D2/D4/M5 是否通过；
2. 路线一 C 实验主干是否可正式闭口；
3. 是否还有 BLOCKER；
4. 是否可以进入三轴小项目准备阶段；
5. 是否需要另行开 P-INT-hard / degraded-severe / joint-full-M-roll 增强任务。
```
