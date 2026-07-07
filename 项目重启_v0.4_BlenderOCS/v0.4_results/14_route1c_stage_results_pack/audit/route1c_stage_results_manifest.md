# 路线一 C 阶段性证据包路径 manifest（route1c_stage_results_manifest）

最后更新：2026-07-01  
来源任务：R120 Codex 任务单 `1C_stage_results_evidence_pack` 子任务 F  
配套 CSV：`route1c_stage_results_manifest.csv`  
状态：可复查路径索引，供后续审稿/写作回查

路径核验：本 manifest 收录的 41 条现有路径已用脚本逐条核验，**缺失 0**（核验命令与结果见执行报告 106）。唯一标记为 PENDING 的是本轮执行报告 106（写入 `02_Claude输出/` 后即变 OK）；本 manifest 自身两文件与图副本目录标记为 OK。

---

## 1. Codex 审阅文件（R113/R115/R117/R119/R120）

| ref | 路径 | 角色 |
|---|---|---|
| R113 | `04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R113_..._B6判据轴闭口并放行L1M2阶段门.md` | 链1审阅 |
| R115 | `.../04_Codex审阅/R115_..._L1M2多几何OCS第一阶段正结果.md` | 链2审阅 |
| R117 | `.../04_Codex审阅/R117_..._L1M3退化真实性与Mroll边界探针.md` | 链3审阅 |
| R119 | `.../04_Codex审阅/R119_..._L1D3置信一致性与PDB正式评估.md` | 链4审阅 |
| R120 | `.../04_Codex审阅/R120_Codex_任务单_1C阶段性Results非正文证据包.md` | 本轮任务单 |

## 2. Claude 报告（102/103/104/105/106）

| ref | 路径 | 状态 |
|---|---|---|
| 102 | `.../02_Claude输出/102_1C-B6-FIX01_多折补齐与foldmatched修正_Claude执行报告.md` | OK |
| 103 | `.../02_Claude输出/103_1C-L1M2_多几何OCS主线长程执行_Claude执行报告.md` | OK |
| 104 | `.../02_Claude输出/104_1C-L1M3Mroll_退化真实性与roll边界探针_Claude执行报告.md` | OK |
| 105 | `.../02_Claude输出/105_1C-L1D3_置信一致性与PDB正式评估_Claude执行报告.md` | OK |
| 106 | `.../02_Claude输出/106_1C阶段性Results非正文证据包_Claude执行报告.md` | 本轮写入 |

## 3. 成果区文件（00/01/05/06/07，均在 `01_成果区/00_当前主用成果/`）

| ref | 文件 | 角色 |
|---|---|---|
| 00 | `00_B6-FIX01与single-frame负结果收口说明_R113通过.md` | 链1成果摘要 |
| 01 | `01_路线一C后续技术路线执行框架_R113通过.md` | 后续技术路线框架 |
| 05 | `05_L1M2多几何OCS第一阶段正结果_R115通过.md` | 链2成果摘要 |
| 06 | `06_L1M3退化真实性与Mroll边界探针_R117通过.md` | 链3成果摘要 |
| 07 | `07_L1D3置信一致性与PDB正式评估_R119通过.md` | 链4成果摘要 |

## 4. 结果目录（10/11/12/13/14）

| ref | 目录 | 内容 |
|---|---|---|
| 10 | `v0.4_results/10_b6_circular_regression_fix01/` | 链1 B6-FIX01 |
| 11 | `v0.4_results/11_l1m2_multigeometry_ocs/` | 链2 L1M2 多几何 |
| 12 | `v0.4_results/12_l1m3_degraded_mroll/` | 链3 退化/M-roll |
| 13 | `v0.4_results/13_l1d3_confidence_pdb/` | 链4 D3/P-DB/conformal |
| 14 | `v0.4_results/14_route1c_stage_results_pack/` | 本轮证据包 |

## 5. 关键 CSV/JSON/PNG/MD（按链）

- 链1（10）：`b6_foldmatched_vs_p1a_best.csv`、`b6_yawblock_stratified_best.csv`、`b6_run_metrics_summary_best.csv`
- 链2（11）：`l1m2_gain_curve_G1_G3_G5.csv`、`l1m2_metrics_summary_best.csv`、`l1m2_pint_vs_pext_ocs_only.csv`、`l1m2_complementarity_summary.csv`、`l1m2_geometry_registry.json`、`figures/l1m2_gain_curve_best.png`
- 链3（12）：`degraded/l1m3_degraded_metrics_summary_best.csv`、`degraded/l1m3_degraded_metrics_summary_final.csv`、`degraded/l1m3_degraded_gain_and_drop_summary.md`、`mroll/mroll_metrics_summary_best.csv`、`mroll/mroll_roll_sensitivity_summary.md`、`mroll/mroll_eval_results.json`、`audit/l1m2_geometry_scale_consistency.csv`、`audit/l1m2_val_samples_recovery_summary.csv`、`audit/l1m2_transform_leakage_check.json`
- 链4（13）：`pdb/l1d3_pdb_retrieval_summary.csv`、`consistency/l1d3_error_correlation_summary.csv`、`consistency/l1d3_risk_coverage.csv`、`conformal/l1d3_conformal_summary.csv`、`hardcases/l1d3_hardcase_index.csv`、`hardcases/l1d3_recommended_pinthard_design.md`、`audit/l1d3_input_manifest.csv`、`figures/pdb_gain_curve.png`、`figures/complementarity_quadrants.png`、`figures/risk_coverage_curves.png`

## 6. 本证据包（14）交付物

| 子任务 | tables/ | text/ | 其它 |
|---|---|---|---|
| A 证据链 | `route1c_evidence_chain.csv` | `route1c_evidence_chain.md` | — |
| B 图表/SI | `route1c_figure_plan.csv` | `route1c_figure_plan.md` | `figures/` 7 张复用图副本 |
| C 叙事骨架 | — | `route1c_results_narrative_skeleton.md` | — |
| D claim边界 | `route1c_claim_boundary_table.csv` | `route1c_claim_boundary_table.md` | — |
| E 待补实验 | `route1c_next_experiment_options.csv` | `route1c_next_experiment_options.md` | — |
| F manifest | — | — | `audit/route1c_stage_results_manifest.csv` + 本 MD |

复用图副本（`figures/`，加 `copy_` 前缀，不覆盖原图）：`copy_R115_l1m2_gain_curve_best.png`、`copy_R115_l1m2_complementarity_hit30.png`、`copy_R119_pdb_gain_curve.png`、`copy_R119_complementarity_quadrants.png`、`copy_R119_neural_vs_pdb_error_scatter.png`、`copy_R119_risk_coverage_curves.png`、`copy_R119_confidence_decile_error.png`。

---

## manifest 自检

- 收录 R120 要求的全部五类：Codex 审阅（R113-R120）、Claude 报告（102-106）、成果区（00/01/05/06/07）、结果目录（10-14）、关键 CSV/JSON/PNG/MD 与本证据包交付物。
- 41 条现有路径脚本核验缺失 0；106 报告为本轮写入项，manifest 自身与图副本为 OK。
- 所有路径为项目根目录内部相对路径，未引用外部材料。
