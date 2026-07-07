# 008 报告 Codex 审阅清单

供 Codex 审阅 008 / 25 包时逐项核验。

## 接收标准（R151 §9 最低）

1. 25 包存在 → `v0.4_results/25_three_axis_p4phys_c_mechanism_generality/`。
2. 008 报告存在 → `02_Claude输出/008_P4PHYS_C_mechanism_generality_Claude执行报告.md`。
3. 候选池来源清楚、EXR/JSON 可定位 → `audit/input_manifest.csv`、`audit/candidate_pool_manifest.csv`、`audit/exr_json_availability.csv`。
4. 批量机制签名表存在 → `tables/p4physC_mechanism_signature_table.csv`（n=159）。
5. near_specular_metal 与亮度排序关系明确 → `tables/p4physC_top_quantile_enrichment.csv`、`p4physC_brightness_by_mechanism.csv`。
6. 隐身板增量是否普遍有明确判断 → `tables/p4physC_dark_panel_increment_test.csv` + `text/p4physC_mechanism_generality_result.md` §4。
7. claim boundary 清楚 → `tables/p4physC_claim_boundary_table.csv`、`text/p4physC_what_can_be_claimed.md`。
8. 红线全 PASS → `audit/redline_self_check.csv`、`tables/p4physC_gate_matrix.csv`。

## 强接收（R151 §9）

1. 候选池覆盖 top-1/R4/R3/23A-23B topN/P3-P2 对照 → build_pool log region_counts。
2. 机制签名复用 24 包口径 + 抽样数值一致性 → `audit/numeric_consistency_sample_check.csv`（max rel_diff 1.5e-7）。
3. 明确裁决 → PARTIAL_GENERALITY（`logs/p4physC_analysis_log.json`）。
4. 下一阶段 sun/view 或 material pass 建议 → `text/p4physC_next_step_recommendation.md`。

## 审阅重点建议

- 核验阈值非 top-1 事后定制：`text/p4physC_mechanism_rule_definition.md` 给出分布 p25/p75 断层依据。
- 核验隐身板增量结论：top-1 dark=0.00877 与 roll+15 亮簇 median 0.00873 几乎相同，R4 dark=0.00093；应确认“排序增量 vs 普遍机制”表述准确。
- 核验固定几何边界与 material proxy 边界未越线。

## 两点交 Codex 裁决

1. PARTIAL_GENERALITY 是否接收并放行 P4-PHYS-D sun/view 扩展阶段门。
2. material pass 是否列为 P4-PHYS-D 前置（当前仅 proxy）。
