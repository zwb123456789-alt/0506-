# R118 Codex 任务单：1C-L1D3 置信一致性与 P-DB 正式评估

最后更新：2026-07-01  
任务类型：给执行端 Claude 的长程执行提示词  
上游阶段门：R117 已通过 104，接收 L1M3 degraded / M-roll / D3 准备材料  
执行端报告必须写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/105_1C-L1D3_置信一致性与PDB正式评估_Claude执行报告.md
```

本文是 Codex 调度/提示词文件，保留在 `04_Codex审阅/`。执行端不得把报告、结果或裁决文件写入 `04_Codex审阅/`。

---

## 0. 给 Claude 的总提示词

你现在执行路线一 C 的下一阶段长程任务：

```text
1C-L1D3_置信一致性与PDB正式评估
```

R113 已关闭 single-frame 判据/输出头补救轴；R115 已接收 clean / P-INT 下 OCS-only 多观测总光度向量 L1-G1 -> L1-G3 -> L1-G5 单调增益；R117 已接收 degraded 真实性轴、M-roll fixed-roll 边界探针、P-DB/conformal smoke 与 val per-attitude 补齐。

本轮目标是把 R117 的 D3/P-DB/conformal smoke 升级为**正式可审计评估包**，回答：

```text
1. P-DB / template retrieval 是否能作为多观测总光度向量含 yaw 信息的非神经证据链。
2. 神经回归、P-DB 检索与 posterior-like 工程分数的置信排序是否与 yaw error 一致。
3. split-conformal / Mondrian conformal 能否在 val/test 分离条件下给出可用覆盖率与集合宽度。
4. 哪些 attitude / geometry / degradation 条件构成后续 P-INT-hard 或更强 degraded 的最小候选集合。
```

本轮主要是**后处理、检索、校准、分层统计与图表**。除非报告中证明低成本 smoke 必要，默认不启动新的大规模训练、不新渲染、不铺 full M-roll、不改 split、不改 backbone。

如果上下文、输出长度或文件写入受限，必须按 `Part 1/2/3...` 分段输出或分段写入，直到任务报告和交付清单完整。

---

## 1. 必读文件

先按顺序读取，并在报告中列出已读文件清单。只引用关键结论，不复述长历史。

```text
CLAUDE.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R113_Codex_审阅_102通过_B6判据轴闭口并放行L1M2阶段门.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R115_Codex_审阅_103通过_L1M2多几何OCS第一阶段正结果.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R117_Codex_审阅_104通过_L1M3退化真实性与Mroll边界探针.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/01_路线一C后续技术路线执行框架_R113通过.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/05_L1M2多几何OCS第一阶段正结果_R115通过.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/06_L1M3退化真实性与Mroll边界探针_R117通过.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/104_1C-L1M3Mroll_退化真实性与roll边界探针_Claude执行报告.md
```

同时定位并按需读取：

```text
v0.4_results/11_l1m2_multigeometry_ocs/
v0.4_results/12_l1m3_degraded_mroll/
06_v0.4_code/07_training/build_d3_confidence_inputs.py
06_v0.4_code/07_training/postprocess_l1m3_mroll_metrics.py
06_v0.4_code/07_training/train_l1m2_multigeometry.py
06_v0.4_code/07_training/dataset_l1m2_multigeometry.py
```

必要时读取：

```text
06_v0.4_code/07_training/postprocess_l1m2_metrics.py
06_v0.4_code/07_training/plot_l1m3_mroll.py
```

---

## 2. 总体交付路径

所有新结果写入：

```text
v0.4_results/13_l1d3_confidence_pdb/
```

建议新增脚本：

```text
06_v0.4_code/07_training/build_l1d3_pdb_templates.py
06_v0.4_code/07_training/eval_l1d3_pdb_retrieval.py
06_v0.4_code/07_training/eval_l1d3_confidence_consistency.py
06_v0.4_code/07_training/eval_l1d3_conformal.py
06_v0.4_code/07_training/build_l1d3_hardcase_index.py
06_v0.4_code/07_training/plot_l1d3_confidence_pdb.py
```

如果能安全复用 R117 的 `build_d3_confidence_inputs.py`，可以通过 wrapper 或 CLI 参数扩展；不要覆盖 R115/R117 的结果目录，不要改旧 metrics/test 文件。

命令环境必须遵守：

```text
Python:
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" "<script>"
```

不要假设系统默认 `python` 可用。中文路径必须加英文双引号。

---

## 3. 子任务 A：输入索引与审计复核

基于 R117 的：

```text
v0.4_results/12_l1m3_degraded_mroll/d3/l1m3_confidence_inputs_index.csv
v0.4_results/12_l1m3_degraded_mroll/audit/l1m2_val_samples_recovery_summary.csv
v0.4_results/12_l1m3_degraded_mroll/audit/l1m2_transform_leakage_check.json
```

生成本轮正式输入索引：

```text
v0.4_results/13_l1d3_confidence_pdb/audit/l1d3_input_manifest.csv
v0.4_results/13_l1d3_confidence_pdb/audit/l1d3_input_manifest.json
v0.4_results/13_l1d3_confidence_pdb/audit/l1d3_input_audit.md
```

最低要求：

```text
1. 明确每个 run 的 source、protocol、geometry_group、mode、degrade_level、split、select、path、n_samples、字段完整性。
2. val/test 必须分开；任何校准或阈值选择只能用 val，不得用 test 反调。
3. clean 与 degraded 来源必须标清：clean 来自 11_l1m2，degraded 来自 12_l1m3。
4. posterior-like 必须标注为工程候选分数，不是真实 Bayesian posterior。
5. 若某些样本字段缺失，列出缺口，不要静默跳过。
```

---

## 4. 子任务 B：P-DB / template retrieval 正式评估

R117 的 P-DB smoke 只验证了 L1-G5 clean neg-L2/cosine 的可行性。本轮把它升级为正式评估包。

### B1. Template 库构建

使用 train split 的多观测总光度向量作为 template 库。必须保证 template 只来自 train，不得混入 val/test。

评估范围：

```text
protocol: P-INT
degrade_level: clean, degraded-mild, degraded-moderate
geometry_group: L1-G1, L1-G3, L1-G5
query_split: val, test
similarity: neg-L2, cosine, zscore-neg-L2
top_k: 1, 3, 5, 10
```

如果 degraded template 与 query 的构造存在两种合理口径，分开标注：

```text
matched-degraded: template 与 query 使用同一 degrade_level
clean-template: template clean，query degraded，用作退化迁移探针
```

若成本过高，优先完成 clean + matched-degraded；clean-template 作为 optional。

### B2. 输出指标

每个组合输出：

```text
top1 yaw circular MAE
top1 yaw hit@15 / hit@30 / hit@45
top1 pitch MAE
top-k-best yaw circular MAE
top-k-best yaw hit@30
nearest-neighbor distance / margin / rank gap
yaw-sector 分层结果（例如 0-90, 90-180, 180-270, 270-360）
pitch-bin 分层结果
```

输出文件：

```text
v0.4_results/13_l1d3_confidence_pdb/pdb/l1d3_pdb_template_manifest.csv
v0.4_results/13_l1d3_confidence_pdb/pdb/l1d3_pdb_retrieval_summary.csv
v0.4_results/13_l1d3_confidence_pdb/pdb/l1d3_pdb_retrieval_per_query.csv
v0.4_results/13_l1d3_confidence_pdb/pdb/l1d3_pdb_retrieval_strata.csv
v0.4_results/13_l1d3_confidence_pdb/pdb/l1d3_pdb_key_findings.md
```

注意口径：

```text
P-DB 是 model-known simulated template retrieval，不是真实未知目标姿态反演系统。
P-DB top-k 是候选姿态检索，不是 Bayesian posterior，也不是真实观测成功率。
```

---

## 5. 子任务 C：神经回归 vs P-DB 的互补与一致性

目标不是证明 joint 强互补性，而是比较不同证据链在同一 test split 上的错误、置信与候选排序是否一致。

评估对象：

```text
neural regression:
  ocs_only / image_only / joint
  final / best
  clean / degraded-mild / degraded-moderate
  G1 / G3 / G5

P-DB:
  clean / degraded-mild / degraded-moderate
  G1 / G3 / G5
  neg-L2 / cosine / zscore-neg-L2
```

最低输出：

```text
1. per-attitude 合并表：true yaw/pitch、neural pred/error、P-DB top1/topk error、entropy/margin、P-DB distance/margin。
2. 错误相关性：neural yaw error vs P-DB yaw error，按 G1/G3/G5、clean/degraded 分层。
3. 互补候选：neural 错但 P-DB 对、P-DB 错但 neural 对、两者都错、两者都对。
4. 置信排序曲线：按 confidence decile 的 MAE / hit@30 / coverage。
5. risk-coverage 曲线：按置信从高到低保留样本，报告覆盖比例与误差。
```

输出文件：

```text
v0.4_results/13_l1d3_confidence_pdb/consistency/l1d3_neural_pdb_joined_per_attitude.csv
v0.4_results/13_l1d3_confidence_pdb/consistency/l1d3_error_correlation_summary.csv
v0.4_results/13_l1d3_confidence_pdb/consistency/l1d3_complementarity_cases.csv
v0.4_results/13_l1d3_confidence_pdb/consistency/l1d3_confidence_deciles.csv
v0.4_results/13_l1d3_confidence_pdb/consistency/l1d3_risk_coverage.csv
v0.4_results/13_l1d3_confidence_pdb/consistency/l1d3_consistency_key_findings.md
```

图表建议：

```text
figures/pdb_gain_curve.png
figures/neural_vs_pdb_error_scatter.png
figures/confidence_decile_error.png
figures/risk_coverage_curves.png
figures/complementarity_quadrants.png
```

---

## 6. 子任务 D：Conformal 正式评估

R117 的 conformal 只是 smoke。本轮做正式 split-conformal 与分层 Mondrian conformal，但仍只使用 val 校准、test 评估。

评估对象：

```text
neural:
  G1/G3/G5 x ocs_only/image_only/joint
  clean/degraded-mild/degraded-moderate
  final/best

P-DB:
  G1/G3/G5
  clean/degraded-mild/degraded-moderate
  neg-L2 / zscore-neg-L2
```

方法：

```text
1. 基础 split-conformal：val yaw circular error 的 (1-alpha) quantile，test 报告 coverage 与 set_size。
2. Mondrian conformal：按 geometry_group、mode、degrade_level、yaw-sector 或 confidence-bin 分层；若某层 val 样本太少，必须回退到 pooled 校准并标注。
3. α 至少包含 0.05, 0.10, 0.20。
4. 报告 yaw 区间宽度；如 pitch 也有可用 error，则可附 pitch smoke，但主结论以 yaw 为主。
```

输出文件：

```text
v0.4_results/13_l1d3_confidence_pdb/conformal/l1d3_conformal_summary.csv
v0.4_results/13_l1d3_confidence_pdb/conformal/l1d3_conformal_per_sample.csv
v0.4_results/13_l1d3_confidence_pdb/conformal/l1d3_mondrian_summary.csv
v0.4_results/13_l1d3_confidence_pdb/conformal/l1d3_conformal_key_findings.md
v0.4_results/13_l1d3_confidence_pdb/conformal/figures/
```

严格口径：

```text
conformal 输出是基于当前 simulated split 的误差覆盖区间，不是真实天文观测不确定度。
coverage 接近 target 只能说明该 split 下校准自洽，不能写成最终概率校准完成。
posterior-like 不能写成 Bayesian posterior。
```

---

## 7. 子任务 E：Hard-case / P-INT-hard 候选索引

本轮不正式启动 P-INT-hard 新训练，但必须用 D3 结果生成下一步可执行候选索引，避免后续继续凭直觉选难例。

生成 hard-case 定义，至少包含：

```text
1. OCS-hard: G5 ocs_only neural yaw error 高、P-DB margin 低或 nearest distance 高。
2. image-hard: image_only / joint 出现高 error 或低 confidence。
3. disagreement-hard: neural 与 P-DB 预测相差大。
4. ambiguous-flux: P-DB top-k 多候选 yaw 分散但距离接近。
5. robust-easy: neural 与 P-DB 都高置信且低 error，用作对照。
```

输出：

```text
v0.4_results/13_l1d3_confidence_pdb/hardcases/l1d3_hardcase_index.csv
v0.4_results/13_l1d3_confidence_pdb/hardcases/l1d3_hardcase_summary.md
v0.4_results/13_l1d3_confidence_pdb/hardcases/l1d3_recommended_pinthard_design.md
```

`l1d3_recommended_pinthard_design.md` 只写下一步设计建议，不得自行放行训练。建议内容可包括：

```text
候选 split / 子集定义
是否需要更强 degraded
是否值得补 joint/full M-roll
预计训练矩阵与成本
哪些指标作为下一阶段门
```

---

## 8. 本轮不得越界

禁止执行或表述：

```text
1. 不启动头A/头B大合并裁决。
2. 不把 R113/R115/R117/R118 写成路线一 C 整体闭口。
3. 不写论文正文，不写成果区新结论，不生成 Codex 审阅文件，不改 CLAUDE.md。
4. 不启动 T3/L2 光变正式训练。
5. 不启动三轴小项目、路线二、路线三、路线四扩展。
6. 不把 v0.4 写成真实未知目标姿态反演系统。
7. 不把 P-DB 写成真实观测反演成功率。
8. 不把 conformal 写成真实 Bayesian posterior 或最终概率校准。
9. 不把 P-EXT yaw-block 写成已解决。
10. 不做开放式超参搜索，不换 backbone，不覆盖旧结果目录。
```

允许写：

```text
1. P-DB / template retrieval 是 model-known simulated template retrieval，可作为多观测总光度向量含 yaw 信息的非神经证据链。
2. conformal 是当前 split 下的覆盖率与集合宽度评估。
3. confidence consistency 是工程置信分数、检索 margin 与实际误差之间的一致性分析。
4. hard-case index 是后续 P-INT-hard / stronger degraded 的候选输入，不是阶段门放行。
```

---

## 9. 执行报告结构

报告写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/105_1C-L1D3_置信一致性与PDB正式评估_Claude执行报告.md
```

报告必须包含：

```text
1. 任务结论摘要：完成 / 部分完成 / 阻塞。
2. 已读文件与遵守的红线。
3. 新增或派生脚本清单：路径、用途、是否修改旧脚本。
4. 新生成结果目录清单。
5. 输入索引与审计复核结果。
6. P-DB / template retrieval 正式评估结果。
7. neural vs P-DB 一致性、互补性与置信排序结果。
8. split-conformal / Mondrian conformal 结果。
9. hard-case / P-INT-hard 候选索引与下一步建议。
10. 未完成项与阻塞项。
11. 红线自查。
12. 交给 Codex 审阅的裁决问题清单。
```

报告不要写成论文正文，不要扩大战果。所有结论必须绑定本轮输出文件路径。

---

## 10. 成功判据

最低接收标准：

```text
1. 输入 manifest 与字段审计完成。
2. P-DB 至少完成 clean P-INT 的 G1/G3/G5 x neg-L2/cosine x val/test 正式评估。
3. 至少完成 G5 clean 的 neural vs P-DB per-attitude 合并表与置信 decile / risk-coverage。
4. 至少完成 G5 clean 的 split-conformal 正式表。
5. hard-case index 至少完成 clean G5 ocs_only，并给出 P-INT-hard 设计建议。
6. 报告路径正确，未写成果区，未生成 Codex 审阅文件，未改 CLAUDE.md。
```

强接收标准：

```text
1. P-DB 完成 clean / degraded-mild / degraded-moderate 的 G1/G3/G5 全矩阵，并含 matched-degraded 与 clean-template 对照。
2. neural vs P-DB 一致性覆盖 ocs_only/image_only/joint、final/best、clean/degraded。
3. split-conformal 与 Mondrian conformal 覆盖 neural 与 P-DB，并输出 coverage/set_size/分层回退说明。
4. hard-case index 覆盖 OCS-hard、image-hard、disagreement-hard、ambiguous-flux、robust-easy 五类。
5. 图表、CSV、JSON/MD 摘要完整，可供 Codex 一次性审阅。
```

---

## 11. 最后交付提醒

执行完成后，只提交候选执行包与 Claude 报告。不要自行把结果升级到成果区，不要生成 Codex 审阅文件，不要修改 `CLAUDE.md`。作者会把你的报告路径交给 Codex，由 Codex 进行 R119 审阅或返工裁决。
