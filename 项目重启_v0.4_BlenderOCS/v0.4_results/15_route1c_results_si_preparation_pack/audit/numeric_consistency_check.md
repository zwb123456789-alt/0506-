# 数字一致性核验（numeric_consistency_check）

最后更新：2026-07-01  来源任务：R122 子任务 D

复算自 10/11/12/13 原始 CSV/JSON，与 R122 任务单第 6 节声明值比对。角度容差 0.5°，hit/相关系数容差 0.01。

**汇总：PASS=33 / CONFLICT=0 / 其他(区间核验)=0，共 33 项。**

| check_id | 描述 | 声明值 | 复算值 | 容差 | 状态 | 源路径 |
|---|---|---|---|---|---|---|
| R115-cmae-G1 | R115 OCS-only cMAE G1 | 76.56 | 76.56 | 0.5 | PASS | `11_l1m2/l1m2_pint_vs_pext_ocs_only.csv` |
| R115-hit-G1 | R115 OCS-only hit@30 G1 | 0.277 | 0.277 | 0.01 | PASS | `11_l1m2/l1m2_pint_vs_pext_ocs_only.csv` |
| R115-cmae-G3 | R115 OCS-only cMAE G3 | 38.22 | 38.22 | 0.5 | PASS | `11_l1m2/l1m2_pint_vs_pext_ocs_only.csv` |
| R115-hit-G3 | R115 OCS-only hit@30 G3 | 0.672 | 0.672 | 0.01 | PASS | `11_l1m2/l1m2_pint_vs_pext_ocs_only.csv` |
| R115-cmae-G5 | R115 OCS-only cMAE G5 | 22.77 | 22.77 | 0.5 | PASS | `11_l1m2/l1m2_pint_vs_pext_ocs_only.csv` |
| R115-hit-G5 | R115 OCS-only hit@30 G5 | 0.811 | 0.811 | 0.01 | PASS | `11_l1m2/l1m2_pint_vs_pext_ocs_only.csv` |
| R115-pext-G1 | R115 P-EXT cMAE G1 | 154.58 | 154.58 | 0.5 | PASS | `11_l1m2/l1m2_pint_vs_pext_ocs_only.csv` |
| R115-pext-G3 | R115 P-EXT cMAE G3 | 146.19 | 146.19 | 0.5 | PASS | `11_l1m2/l1m2_pint_vs_pext_ocs_only.csv` |
| R115-pext-G5 | R115 P-EXT cMAE G5 | 157.25 | 157.25 | 0.5 | PASS | `11_l1m2/l1m2_pint_vs_pext_ocs_only.csv` |
| R117-G5-clean | R117 degraded G5 clean cMAE | 22.77 | 22.77 | 0.5 | PASS | `11_l1m2 (clean ref)` |
| R117-G5-degraded-mild | R117 degraded G5 degraded-mild cMAE | 27.83 | 27.8265 | 0.5 | PASS | `12_l1m3/degraded/l1m3_degraded_metrics_summary_best.csv` |
| R117-G5-degraded-moderate | R117 degraded G5 degraded-moderate cMAE | 38.46 | 38.4566 | 0.5 | PASS | `12_l1m3/degraded/l1m3_degraded_metrics_summary_best.csv` |
| R117-mroll-G5-0 | M-roll G5 0° cMAE | 8.68 | 8.684 | 0.5 | PASS | `12_l1m3/mroll/mroll_metrics_summary_best.csv` |
| R117-mroll-G5-p15 | M-roll G5 +15° cMAE≈17.5 | 17.53 | 17.533 | 0.5 | PASS | `12_l1m3/mroll/mroll_metrics_summary_best.csv` |
| R117-mroll-G5-m15 | M-roll G5 -15° cMAE≈19.7 | 19.67 | 19.665 | 0.5 | PASS | `12_l1m3/mroll/mroll_metrics_summary_best.csv` |
| R117-mroll-G5-p30 | M-roll G5 +30° cMAE≈33.0 | 32.99 | 32.99 | 0.5 | PASS | `12_l1m3/mroll/mroll_metrics_summary_best.csv` |
| R117-mroll-G5-m30 | M-roll G5 -30° cMAE≈28.7 | 28.69 | 28.692 | 0.5 | PASS | `12_l1m3/mroll/mroll_metrics_summary_best.csv` |
| R119-pdb-G5-hit | R119 P-DB clean G5 top1 hit@30 | 0.949 | 0.9493 | 0.01 | PASS | `13_l1d3/pdb/l1d3_pdb_retrieval_summary.csv` |
| R119-pdb-G5-cmae | R119 P-DB clean G5 cMAE | 8.19 | 8.1926 | 0.5 | PASS | `13_l1d3/pdb/l1d3_pdb_retrieval_summary.csv` |
| R119-neural-G5 | R119 neural ocs_only clean G5 cMAE | 22.77 | 22.769 | 0.5 | PASS | `13_l1d3/consistency/l1d3_error_correlation_summary.csv` |
| R119-oracle | R119 oracle hit@30 clean G5 | 0.96 | 0.9595 | 0.01 | PASS | `13_l1d3/consistency/l1d3_complementarity_cases.csv` |
| R119-spearman | R119 Spearman≈0 (clean G5 ocs_only) | 0.066 | 0.0661 | 0.01 | PASS | `13_l1d3/consistency/l1d3_error_correlation_summary.csv` |
| R119-quad-both_correct | R119 四象限 both_correct | 237 | 237.0 | 0.5 | PASS | `13_l1d3/consistency/l1d3_complementarity_cases.csv` |
| R119-quad-neural_only | R119 四象限 neural_only | 3 | 3.0 | 0.5 | PASS | `13_l1d3/consistency/l1d3_complementarity_cases.csv` |
| R119-quad-pdb_only | R119 四象限 pdb_only | 44 | 44.0 | 0.5 | PASS | `13_l1d3/consistency/l1d3_complementarity_cases.csv` |
| R119-quad-both_wrong | R119 四象限 both_wrong | 12 | 12.0 | 0.5 | PASS | `13_l1d3/consistency/l1d3_complementarity_cases.csv` |
| R119-conf-G1 | R119 conformal set_size G1 | 321.8 | 321.7954 | 0.5 | PASS | `13_l1d3/conformal/l1d3_conformal_summary.csv` |
| R119-conf-G3 | R119 conformal set_size G3 | 245.7 | 245.6907 | 0.5 | PASS | `13_l1d3/conformal/l1d3_conformal_summary.csv` |
| R119-conf-G5 | R119 conformal set_size G5 | 126.2 | 126.1807 | 0.5 | PASS | `13_l1d3/conformal/l1d3_conformal_summary.csv` |
| R119-img-cov | R119 image_only clean coverage 区间(欠覆盖) | 0.83-0.85 | 0.8345-0.8919 | range | PASS | `13_l1d3/conformal/l1d3_conformal_summary.csv` |
| R113-b6-image_only | R113 B6 image_only no-aug fold-mean cMAE | 60.273 | 60.2732 | 1.0 | PASS | `10_b6/b6_foldmatched_vs_p1a_best.csv (fold-mean)` |
| R113-b6-joint | R113 B6 joint no-aug fold-mean cMAE | 72.74 | 72.74 | 1.0 | PASS | `10_b6/b6_foldmatched_vs_p1a_best.csv (fold-mean)` |
| R113-b6-ocs_only | R113 B6 ocs_only no-aug fold-mean cMAE | 143.805 | 143.8046 | 1.0 | PASS | `10_b6/b6_foldmatched_vs_p1a_best.csv (fold-mean)` |

若有 CONFLICT：不自行改写上游结论，交回 Codex 裁决。
