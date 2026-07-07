# R122 Codex 任务单：路线一 C Results/SI 图表与写作准备包

最后更新：2026-07-01  
任务类型：给执行端 Claude 的长程整理提示词  
上游阶段门：R121 已通过 106，路线一 C 阶段性 Results 非正文证据包接收  
执行端报告必须写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/107_1C-ResultsSI图表与写作准备包_Claude执行报告.md
```

本文件是 Codex 调度/提示词文件，保留在 `04_Codex审阅/`。执行端不得把报告、结果或裁决文件写入 `04_Codex审阅/`。

---

## 0. 给 Claude 的总提示词

你现在执行路线一 C 的下一阶段整理任务：

```text
1C_results_si_preparation_pack
```

R121 已接收 `v0.4_results/14_route1c_stage_results_pack/` 作为路线一 C 阶段性 Results 非正文证据包。本轮目标是在**不新增科学实验**的前提下，把 14 号证据包推进为可供作者/Codex 后续写作审阅的 **Results/SI 图表与写作准备包**。

本轮允许做：

```text
1. 基于既有 CSV/JSON/MD/PNG 进行轻量制图、表格重排和图注草案。
2. 整理 main figures / SI figures / SI tables 的文件包和 manifest。
3. 写 Results 候选段落草案，但必须是“受控草案”：每段绑定 evidence path、allowed claim、forbidden reading、risk tag。
4. 生成 claim-to-figure 映射、figure-to-source 映射、negative-observation checklist。
5. 新增轻量绘图/汇总脚本，但只能写入新文件，不得改旧脚本。
```

本轮禁止做：

```text
1. 不新训练、不新渲染、不新后处理大矩阵、不做超参搜索。
2. 不修改旧脚本、旧 metrics、旧 samples、旧结果目录 10/11/12/13/14。
3. 不写最终论文正文、投稿摘要、最终投稿稿或 cover letter。
4. 不把本轮材料写入成果区，不生成 Codex 审阅文件，不改 CLAUDE.md。
5. 不启动头A/头B大合并裁决，不把路线一 C 写成整体闭口。
6. 不启动 T3/L2、三轴小项目、路线二/三/四扩展。
7. 不把 P-DB 写成真实观测反演成功率，不把 conformal 写成 Bayesian posterior 或最终概率校准。
8. 不把 P-EXT yaw-block 写成已解决，不把 joint 强互补性写成已证明。
```

如果上下文、输出长度或文件写入受限，必须按 `Part 1/2/3...` 分段输出或分段写入，直到报告和交付清单完整。

---

## 1. 必读文件

先按顺序读取，并在执行报告中列出已读文件清单。只引用关键结论，不复述长历史。

```text
CLAUDE.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R121_Codex_审阅_106通过_1C阶段性Results非正文证据包.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/08_路线一C阶段性Results非正文证据包_R121通过.md
v0.4_results/14_route1c_stage_results_pack/text/route1c_evidence_chain.md
v0.4_results/14_route1c_stage_results_pack/text/route1c_figure_plan.md
v0.4_results/14_route1c_stage_results_pack/text/route1c_results_narrative_skeleton.md
v0.4_results/14_route1c_stage_results_pack/text/route1c_claim_boundary_table.md
v0.4_results/14_route1c_stage_results_pack/text/route1c_next_experiment_options.md
v0.4_results/14_route1c_stage_results_pack/audit/route1c_stage_results_manifest.csv
```

按需读取结果目录中的数据源：

```text
v0.4_results/10_b6_circular_regression_fix01/
v0.4_results/11_l1m2_multigeometry_ocs/
v0.4_results/12_l1m3_degraded_mroll/
v0.4_results/13_l1d3_confidence_pdb/
```

---

## 2. 总体交付路径

所有本轮新整理材料写入：

```text
v0.4_results/15_route1c_results_si_preparation_pack/
```

建议目录：

```text
v0.4_results/15_route1c_results_si_preparation_pack/
  figures_main/
  figures_si/
  tables/
  text/
  scripts/
  audit/
```

执行报告写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/107_1C-ResultsSI图表与写作准备包_Claude执行报告.md
```

如需新增脚本，只能新增在本轮包内：

```text
v0.4_results/15_route1c_results_si_preparation_pack/scripts/
```

或新增在代码区的新文件：

```text
06_v0.4_code/11_reporting/
```

不得修改任何既有 `.py` 脚本。

---

## 3. 子任务 A：正式候选主图包

基于 R121 已认可的图表计划，生成候选主图文件。优先输出 PNG，同时尽量输出 PDF 或 SVG；若某图无法输出矢量，报告原因。

主图候选：

```text
Fig.1 任务与协议示意图：model-known simulated multi-view OCS/image/P-DB/conformal 证据链。
Fig.2 clean/P-INT OCS-only L1-G1/G3/G5 单调增益曲线。
Fig.3 degraded 下 OCS-only G1/G3/G5 增益保持与退化收缩。
Fig.4 P-DB vs neural ocs_only + 互补四象限双 panel。
Fig.5 conformal set_size 随几何收紧 + 负向观察摘要。
```

要求：

```text
1. 每张图必须绑定 source CSV/JSON/PNG/MD 路径。
2. 图中命名统一使用实验层 L1-G1 / L1-G3 / L1-G5。
3. Fig.1 只能画 model-known simulated 前向模型与协议关系，不画真实望远镜验证、真实 GEO 姿态真值或三轴反演链路。
4. Fig.2 必须同时体现 cMAE 与 hit@30，或在图旁表格中保留 hit@30。
5. Fig.3 必须体现 clean/mild/moderate 下的几何增益保持与退化收缩。
6. Fig.4 必须标注 P-DB 是 simulated template retrieval，oracle 是上界。
7. Fig.5 必须保留 neural margin 弱、image_only 欠覆盖等负向观察，不得只画正结果。
```

输出：

```text
figures_main/Fig1_protocol_schematic.*
figures_main/Fig2_clean_pint_ocs_gain.*
figures_main/Fig3_degraded_ocs_gain.*
figures_main/Fig4_pdb_neural_complementarity.*
figures_main/Fig5_conformal_geometry_confidence.*
tables/main_figure_source_map.csv
text/main_figure_captions_draft.md
```

---

## 4. 子任务 B：SI 图表与表格包

生成 SI 候选图表/表格，至少覆盖：

```text
SI-1 R113 B6 single-frame 判据轴闭口证据链。
SI-2 R115 P-EXT yaw-block stress test 仍坍缩。
SI-3 R117 M-roll ±15/±30 边界探针。
SI-4 R119 hard-case index 与 P-INT-hard 候选定义。
SI-5 数据/代码/结果路径 manifest。
SI-x1 neural vs P-DB error scatter 可选补充。
SI-x2 confidence decile error 可选补充。
```

要求：

```text
1. SI-1 可用表格代图，但必须清楚写出 circular regression 改善 image/joint cMAE 但救不回 yaw 外推。
2. SI-2 必须显示 P-INT vs P-EXT 对照，P-EXT cMAE 约 146-157° 仍坍缩。
3. SI-3 只写 fixed-roll 边界探针，不写 roll-aware 能力或三轴姿态反演。
4. SI-4 只写 hard-case index 是候选输入，不写已放行新训练。
5. SI-5 从 14 号 manifest 与本轮新文件生成可复查表。
```

输出：

```text
figures_si/SI1_b6_single_frame_closure.*
figures_si/SI2_pint_vs_pext_stress.*
figures_si/SI3_mroll_boundary_probe.*
figures_si/SI4_hardcase_index.*
figures_si/SIx1_neural_vs_pdb_error_scatter.*   # 若复用/重绘
figures_si/SIx2_confidence_decile_error.*       # 若复用/重绘
tables/SI5_manifest_table.csv
tables/si_figure_source_map.csv
text/si_captions_draft.md
```

---

## 5. 子任务 C：受控 Results 草案包

基于 14 号叙事骨架生成受控 Results 候选文本。注意：这不是最终论文正文，也不是投稿稿。写法必须可审查、可回滚、可逐句追溯。

建议结构：

```text
R0 Problem framing: single-frame 负结果为何不等于光度无用。
R1 Clean/P-INT 多几何 OCS 可观测性。
R2 Degraded 真实性轴与 M-roll fixed-roll 边界。
R3 P-DB / conformal 可检索信息与置信一致性。
R4 Negative observations and limitations.
R5 Remaining gaps and next-stage options.
```

每个段落必须附：

```text
paragraph_id
claim_ids
supporting evidence paths
linked figure/table ids
allowed wording
forbidden wording
risk tag: low / medium / high
```

输出：

```text
text/results_candidate_draft_controlled.md
tables/paragraph_claim_evidence_map.csv
tables/claim_figure_table_map.csv
```

红线：

```text
1. 不写 Abstract、Introduction、Discussion 全文。
2. 不写最终投稿语气，不写“we demonstrate a real-world system”。
3. 不新增 R121 以外的 claim。
4. 所有强结论必须带 model-known simulated / clean P-INT / current split / template retrieval 等限定语。
```

---

## 6. 子任务 D：图表一致性与数字核验

对本轮所有图、表、草案中的关键数字做一次可审计核验。

至少核验：

```text
R115 OCS-only cMAE/hit@30: G1/G3/G5 = 76.56/38.22/22.77°, 0.277/0.672/0.811。
R115 P-EXT cMAE: G1/G3/G5 = 154.58/146.19/157.25°。
R117 degraded OCS-only cMAE clean/mild/moderate: G5 = 22.77/27.83/38.46°。
R117 M-roll G5: 0°=8.68°; ±15°≈17.5/19.7°; ±30°≈33.0/28.7°。
R119 P-DB clean G5 top1 hit@30=0.949, cMAE=8.19°。
R119 neural ocs_only clean G5 cMAE=22.77°。
R119 oracle hit@30=0.960; Spearman≈0。
R119 conformal ocs_only clean α=0.10 set_size G1/G3/G5 = 321.8/245.7/126.2°。
R119 image_only coverage≈0.83-0.85 欠覆盖。
```

输出：

```text
audit/numeric_consistency_check.csv
audit/numeric_consistency_check.md
audit/generated_files_manifest.csv
audit/generated_files_manifest.md
```

若发现数字冲突，不要自行改写上游结论；在报告中列出冲突路径、冲突值和建议交回 Codex 裁决。

---

## 7. 子任务 E：红线自检与可审阅清单

生成本轮红线自检表，至少包含：

```text
1. 是否未新训练/新渲染/新后处理矩阵。
2. 是否未改旧脚本/旧 metrics/旧 samples/旧结果目录。
3. 是否未写成果区/未生成 Codex 审阅文件/未改 CLAUDE.md。
4. 是否未写最终论文正文/投稿摘要。
5. 是否所有 claim 均限定 model-known simulated。
6. 是否保留 P-EXT 坍缩、joint 天花板/检查点敏感、neural margin 弱、image_only 欠覆盖。
7. 是否未把 P-DB 写成真实观测反演成功率。
8. 是否未把 conformal 写成 Bayesian posterior 或最终概率校准。
9. 是否未把路线一 C 写成整体闭口。
10. 是否未启动三轴小项目、T3/L2 或路线二三四扩展。
```

输出：

```text
audit/redline_self_check.csv
text/codex_review_checklist_for_107.md
```

---

## 8. 执行报告结构

执行报告写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/107_1C-ResultsSI图表与写作准备包_Claude执行报告.md
```

报告必须包含：

```text
1. 任务结论摘要：完成 / 部分完成 / 阻塞。
2. 已读文件与遵守的红线。
3. 新增脚本清单：路径、用途、是否改旧脚本。
4. 主图交付清单：每张图路径、数据源、是否重绘/复用。
5. SI 图表交付清单：每张图/表路径、数据源、是否重绘/复用。
6. Results 受控草案交付清单：段落数、claim map、证据路径。
7. 数字一致性核验摘要：通过项、冲突项、缺失项。
8. manifest 与可复查索引摘要。
9. 未完成项与阻塞项。
10. 红线自检。
11. 交给 Codex 审阅的裁决问题清单。
```

---

## 9. 成功判据

最低接收标准：

```text
1. 15 号结果包目录存在，结构清楚。
2. Fig.1-Fig.5 至少输出 PNG 或可直接打开的图/表替代物。
3. SI-1 至 SI-5 至少输出图或表替代物。
4. main_figure_source_map.csv、si_figure_source_map.csv 完成。
5. results_candidate_draft_controlled.md 完成，且每段绑定 evidence path / allowed / forbidden / risk。
6. numeric_consistency_check.csv/md 完成。
7. generated_files_manifest.csv/md 完成，且本轮文件路径可复查。
8. 执行报告写入正确路径，未写成果区、未写 Codex 审阅文件、未改 CLAUDE.md。
```

强接收标准：

```text
1. 所有图表均有统一命名、统一术语 L1-G1/G3/G5、清晰 source path。
2. 图注草案能直接交给 Codex/作者进一步润色。
3. Results 受控草案不越界，负向观察独立可见。
4. 所有关键数字能追溯到 10/11/12/13/14 的原始 CSV/JSON/MD。
5. 15 号包可直接作为下一轮 Codex 审阅对象。
```

---

## 10. 最后交付提醒

执行完成后，只提交候选整理包与 Claude 执行报告。不要自行把结果升级到成果区，不要生成 Codex 审阅文件，不要修改 `CLAUDE.md`。作者会把 107 报告路径交给 Codex，由 Codex 进行 R123 审阅或返工裁决。
