# R120 Codex 任务单：路线一 C 阶段性 Results 非正文证据包

最后更新：2026-07-01  
任务类型：给执行端 Claude 的长程整理提示词  
上游阶段门：R119 已通过 105，L1D3 置信一致性与 P-DB 正式评估接收  
执行端报告必须写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/106_1C阶段性Results非正文证据包_Claude执行报告.md
```

本文是 Codex 调度/提示词文件，保留在 `04_Codex审阅/`。执行端不得把报告、结果或裁决文件写入 `04_Codex审阅/`。

---

## 0. 给 Claude 的总提示词

你现在执行路线一 C 的阶段性证据整理任务：

```text
1C_stage_results_evidence_pack
```

R113/R115/R117/R119 已形成当前路线一 C 的阶段性主证据链：

```text
R113: B6 关闭 single-frame 判据/输出头补救轴，旧 single-frame 负结果追因阶段性收束。
R115: L1(M2) clean / P-INT 下，OCS-only 多观测总光度向量 L1-G1 -> L1-G3 -> L1-G5 单调增益。
R117: L1(M3) degraded 下 OCS-only 多几何增益保持；M-roll fixed-roll 边界探针接收；D3/P-DB/conformal 准备接收。
R119: L1D3 P-DB 正式评估与置信一致性接收；P-DB 与 neural ocs_only 构成互补证据链；conformal set_size 随几何收紧。
```

本轮目标是把上述结果整理成**Results 非正文证据包**，供后续 Codex/作者决定论文 Results 叙事、图表、SI、待补实验和 claim 边界。你不是写论文正文，不是阶段闭口，不是生成最终投稿稿。

本轮不启动任何新训练、新渲染、新后处理矩阵或超参搜索；只允许读取、汇总、核对、复制/引用现有结果表与图表，必要时生成轻量索引 CSV/MD 和汇总图表草案。

如果上下文、输出长度或文件写入受限，必须按 `Part 1/2/3...` 分段输出或分段写入，直到任务报告和交付清单完整。

---

## 1. 必读文件

先按顺序读取，并在报告中列出已读文件清单。只引用关键结论，不复述长历史。

```text
CLAUDE.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R113_Codex_审阅_102通过_B6判据轴闭口并放行L1M2阶段门.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R115_Codex_审阅_103通过_L1M2多几何OCS第一阶段正结果.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R117_Codex_审阅_104通过_L1M3退化真实性与Mroll边界探针.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R119_Codex_审阅_105通过_L1D3置信一致性与PDB正式评估.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/00_B6-FIX01与single-frame负结果收口说明_R113通过.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/01_路线一C后续技术路线执行框架_R113通过.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/05_L1M2多几何OCS第一阶段正结果_R115通过.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/06_L1M3退化真实性与Mroll边界探针_R117通过.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/07_L1D3置信一致性与PDB正式评估_R119通过.md
```

按需读取 Claude 报告与结果目录：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/102_1C-后续技术路线总规划_观测方式×反演方法×真实性矩阵与闭口时序_草案供Codex审阅.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/103_1C-L1M2_多几何OCS主线长程执行_Claude执行报告.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/104_1C-L1M3Mroll_退化真实性与roll边界探针_Claude执行报告.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/105_1C-L1D3_置信一致性与PDB正式评估_Claude执行报告.md
v0.4_results/10_b6_circular_regression_fix01/
v0.4_results/11_l1m2_multigeometry_ocs/
v0.4_results/12_l1m3_degraded_mroll/
v0.4_results/13_l1d3_confidence_pdb/
```

---

## 2. 总体交付路径

所有新整理材料写入：

```text
v0.4_results/14_route1c_stage_results_pack/
```

建议目录：

```text
v0.4_results/14_route1c_stage_results_pack/
  tables/
  figures/
  text/
  audit/
```

执行报告写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/106_1C阶段性Results非正文证据包_Claude执行报告.md
```

如果需要新增脚本，只能新增轻量汇总/制表/画图脚本，例如：

```text
06_v0.4_code/07_training/build_route1c_stage_results_pack.py
06_v0.4_code/07_training/plot_route1c_stage_results_summary.py
```

不得修改旧脚本，不得覆盖旧结果目录。

---

## 3. 子任务 A：证据链总表

生成路线一 C 当前主证据链总表，至少包含：

```text
stage_id: R113 / R115 / R117 / R119
source_file: 审阅文件路径
result_dir: 结果目录
accepted_claim: 可写结论
boundary: 不可写边界
key_numbers: 核心数字
figure_or_table_source: 对应 CSV/JSON/PNG/MD 路径
paper_use: main / SI / methods note / limitation / future work
risk_level: low / medium / high
```

输出：

```text
v0.4_results/14_route1c_stage_results_pack/tables/route1c_evidence_chain.csv
v0.4_results/14_route1c_stage_results_pack/text/route1c_evidence_chain.md
```

必须覆盖四条主链：

```text
1. single-frame 负结果收口与 B6 判据轴闭口。
2. clean/P-INT 多几何 OCS 单调增益。
3. degraded/M-roll 真实性与 fixed-roll 边界。
4. D3/P-DB/conformal 置信一致性与互补证据。
```

---

## 4. 子任务 B：Results 图表与 SI 清单

请生成一个**候选图表清单**，不是正式论文图。每个图表必须绑定现有数据源，不能凭记忆画。

建议主图候选：

```text
Fig. 1: 任务与协议示意，不画真实望远镜验证，只画 model-known simulated multi-view OCS / image / P-DB / conformal 证据链。
Fig. 2: R115 clean/P-INT OCS-only G1/G3/G5 单调增益曲线。
Fig. 3: R117 degraded 下 OCS-only G1/G3/G5 增益保持与退化收缩。
Fig. 4: R119 P-DB vs neural ocs_only，显示 P-DB 检索强于回归与互补四象限。
Fig. 5: R119 conformal set_size 随几何收紧与负向观察。
```

建议 SI 图表候选：

```text
SI-1: R113 B6 single-frame 判据轴闭口证据链。
SI-2: R115 P-EXT yaw-block stress test 仍坍缩。
SI-3: R117 M-roll ±15/±30 边界探针。
SI-4: R119 hard-case index 与 P-INT-hard 候选定义。
SI-5: 数据/代码/结果路径 manifest。
```

输出：

```text
v0.4_results/14_route1c_stage_results_pack/tables/route1c_figure_plan.csv
v0.4_results/14_route1c_stage_results_pack/text/route1c_figure_plan.md
v0.4_results/14_route1c_stage_results_pack/figures/
```

允许复制或轻量重绘现有汇总图，但必须保留数据源路径。若只生成占位图清单，也要说明原因。

---

## 5. 子任务 C：Results 非正文叙事骨架

生成一份**非正文**叙事骨架，供后续 Codex/作者写论文时使用。它不能写成正式论文段落，必须是 bullet / outline / claim ledger 形式。

输出：

```text
v0.4_results/14_route1c_stage_results_pack/text/route1c_results_narrative_skeleton.md
```

建议结构：

```text
1. Problem framing: 旧 single-frame 负结果为何不等于光度无用。
2. Result block 1: clean/P-INT 多几何 OCS 可观测性。
3. Result block 2: degraded 真实性轴与 M-roll fixed-roll 边界。
4. Result block 3: P-DB / conformal 证明可检索信息与置信一致性。
5. Negative observations: P-EXT 坍缩、image/joint 天花板、neural margin 弱、image_only 欠覆盖。
6. Remaining gaps: degraded-severe / P-INT-hard、真实 GEO 只可作光度锚点、三轴小项目未启动。
```

每条 claim 后必须跟：

```text
supporting evidence path
allowed wording
forbidden wording
whether usable in main text / SI / limitation
```

---

## 6. 子任务 D：Claim 边界与红线表

生成明确的可写/不可写表：

```text
v0.4_results/14_route1c_stage_results_pack/tables/route1c_claim_boundary_table.csv
v0.4_results/14_route1c_stage_results_pack/text/route1c_claim_boundary_table.md
```

至少包含这些边界：

```text
可写：
- model-known simulated 条件下，L1 多观测总光度向量含姿态信息。
- OCS-only 多几何增益在 clean 与 mild/moderate degraded 下保持。
- P-DB 检索提供非神经证据，说明 neural ocs_only 未充分利用光度信息。
- conformal set_size 随几何收紧，说明当前 split 下 uncertainty interval 与信息量一致。
- M-roll ±15° 未直接推翻 fixed-roll 结论，±30° 敏感。

不可写：
- 真实未知目标姿态反演系统已经实现。
- 真实望远镜验证、field-proven、operational-ready。
- GEO 数据库有三轴姿态真值。
- P-EXT yaw-block 已解决。
- joint 强互补性已证明。
- Bayesian posterior 或最终概率校准已完成。
- 路线一 C 整体闭口。
- 三轴小项目已启动或完成。
```

---

## 7. 子任务 E：待补实验与下一阶段建议

基于 R119 hard-case index 和当前成果边界，生成一份下一阶段建议表：

```text
v0.4_results/14_route1c_stage_results_pack/tables/route1c_next_experiment_options.csv
v0.4_results/14_route1c_stage_results_pack/text/route1c_next_experiment_options.md
```

建议至少列出：

```text
Option A: 先整理论文 Results / SI，不立即新训练。
Option B: degraded-severe / P-INT-hard 小矩阵，用 hard-case index 选难例，检验 joint 相对 image_only 增量。
Option C: joint/full-2664 M-roll 子集扩展，只回答 fixed-roll 边界，不启动三轴。
Option D: 路线一 C 阶段性闭口前的 minimal sanity check。
```

每个选项必须包含：

```text
goal
input data
needed new computation
expected cost
stage-gate metric
risk
what it would enable
what it cannot claim
```

不得自行放行任何选项，只给 Codex/作者裁决。

---

## 8. 子任务 F：路径 manifest 与可复查索引

生成完整路径 manifest，方便后续审稿/写作回查：

```text
v0.4_results/14_route1c_stage_results_pack/audit/route1c_stage_results_manifest.csv
v0.4_results/14_route1c_stage_results_pack/audit/route1c_stage_results_manifest.md
```

至少收录：

```text
Codex 审阅文件：R113/R115/R117/R119/R120
Claude 报告：102/103/104/105/106
成果区文件：00/01/05/06/07
结果目录：10/11/12/13/14
关键 CSV/JSON/PNG/MD
关键脚本路径
```

---

## 9. 本轮不得越界

禁止执行或表述：

```text
1. 不启动新训练、新渲染、新后处理大矩阵。
2. 不改旧脚本、旧 metrics、旧 samples 或旧结果目录。
3. 不写论文正文，不写投稿摘要，不写最终投稿稿。
4. 不自行把本轮结果写入成果区，不生成 Codex 审阅文件，不改 CLAUDE.md。
5. 不启动头A/头B大合并裁决。
6. 不把路线一 C 写成整体闭口。
7. 不启动 T3/L2 光变正式训练、三轴小项目、路线二/三/四扩展。
8. 不把 P-DB 写成真实观测反演成功率。
9. 不把 conformal 写成真实 Bayesian posterior 或最终概率校准。
10. 不把 P-EXT yaw-block 写成已解决。
```

允许写：

```text
1. 当前证据支持路线一 C 的阶段性 Results 非正文材料整理。
2. 当前主线已从 single-frame 负结果转入 L1 多观测总光度向量正结果与置信一致性证据链。
3. 下一步可由 Codex/作者在 Results 整理与 degraded-severe/P-INT-hard 小矩阵之间裁决。
```

---

## 10. 执行报告结构

报告写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/106_1C阶段性Results非正文证据包_Claude执行报告.md
```

报告必须包含：

```text
1. 任务结论摘要：完成 / 部分完成 / 阻塞。
2. 已读文件与遵守的红线。
3. 新增脚本清单：路径、用途、是否修改旧脚本。
4. 新生成结果目录清单。
5. 证据链总表摘要。
6. 图表与 SI 清单摘要。
7. Results 非正文叙事骨架摘要。
8. claim 边界表摘要。
9. 待补实验与下一阶段建议摘要。
10. manifest 与可复查索引摘要。
11. 未完成项与阻塞项。
12. 红线自查。
13. 交给 Codex 审阅的裁决问题清单。
```

---

## 11. 成功判据

最低接收标准：

```text
1. evidence_chain.csv/md 完成，覆盖 R113/R115/R117/R119。
2. figure_plan.csv/md 完成，每个候选图表绑定数据源。
3. narrative_skeleton.md 完成，使用非正文 outline / claim ledger 格式。
4. claim_boundary_table.csv/md 完成。
5. next_experiment_options.csv/md 完成。
6. manifest.csv/md 完成。
7. 报告路径正确，未写成果区，未生成 Codex 审阅文件，未改 CLAUDE.md。
```

强接收标准：

```text
1. 能直接支撑下一轮 Codex 审阅后进入成果区。
2. 每条 claim 都有 evidence path、allowed wording、forbidden wording。
3. 主图/SI 图候选已给出数据源、优先级和是否需重绘。
4. 待补实验选项能直接改写成下一轮 Claude 任务单。
5. 所有路径 manifest 可复查且无失效路径。
```

---

## 12. 最后交付提醒

执行完成后，只提交候选整理包与 Claude 报告。不要自行把结果升级到成果区，不要生成 Codex 审阅文件，不要修改 `CLAUDE.md`。作者会把你的报告路径交给 Codex，由 Codex 进行 R121 审阅或返工裁决。
