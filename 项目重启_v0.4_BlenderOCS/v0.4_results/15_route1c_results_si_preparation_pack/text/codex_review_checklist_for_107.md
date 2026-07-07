# 107 交付给 Codex 的审阅清单（codex_review_checklist_for_107）

最后更新：2026-07-01
来源任务：R122 子任务 E
状态：本轮 15 号包交给 Codex（预期 R123）审阅前的自检清单与裁决问题。本文件仅为清单，不是 Codex 审阅文件本体。

---

## 1. 交付物清单（15 号包）

```text
figures_main/  Fig1-Fig5 (.png + .pdf)
figures_si/    SI1-SI4 (.png + .pdf) + SIx1/SIx2 (复用R119 .png)
tables/        main_figure_source_map.csv; si_figure_source_map.csv; SI5_manifest_table.csv;
               paragraph_claim_evidence_map.csv; claim_figure_table_map.csv
text/          main_figure_captions_draft.md; si_captions_draft.md; results_candidate_draft_controlled.md
scripts/       make_figures.py; make_audit.py（均为新文件，不改旧脚本）
audit/         numeric_consistency_check.csv/.md; generated_files_manifest.csv/.md; redline_self_check.csv
```

## 2. 自检结论

```text
- 图：Fig1-Fig5 + SI1-SI4 全部输出 PNG+PDF（矢量）；SIx1/x2 复用 R119 图。
- 数字核验：33 项全部 PASS，0 CONFLICT（numeric_consistency_check）。
- 红线自检：RL1-RL10 全部 PASS（redline_self_check）。
- 术语统一 L1-G1/G3/G5；每图/每段绑定 source path + allowed/forbidden + risk tag。
- 受控草案 R0-R5 未越界，负向观察独立成段。
```

## 3. 建议 Codex 复核项

```text
1. Fig.1 概念图是否越界画了真实链路（自检：未画真实望远镜/GEO真值/三轴）。
2. Fig.4/R3 段 P-DB 与 conformal 措辞是否仍为 medium 风险可接受范围。
3. R4 负向观察是否完整（P-EXT/joint天花板/neural margin/image_only欠覆盖四项齐全）。
4. 复算口径：P-DB 主口径取 neg-L2 + matched-degraded + test；conformal 取 neural+best+α=0.10；
   degraded 取 best 口径。请确认是否与 R115/R117/R119 审阅口径一致。
5. Results 草案是否可直接作为下一轮写作输入，或需先补多 seed/fold 说明。
```

## 4. 交给 Codex 的裁决问题

```text
Q1 主图口径：Fig.2/Fig.3 clean 数据取自 l1m2_pint_vs_pext_ocs_only.csv(P-INT行)，
   是否需要改用 l1m2_metrics_summary_best.csv 的 best 口径以与 R115 完全一致？
Q2 P-DB 检索口径：主图/核验固定 neg-L2 + matched-degraded 是否为 R119 认可主口径？
   zscore-neg-L2 / clean-template 是否需并列进 SI？
Q3 conformal 口径：set_size 是否统一 α=0.10 best？是否需补 α=0.05/0.20 敏感性到 SI？
Q4 受控草案是否可进入下一轮"正式 Results 段落"，还是仍停留在草案层等 P-INT-hard/多seed？
Q5 15 号包是否可作为 R123 审阅对象；若通过，成果区升级由 Codex 决定，本轮不自行升级。
Q6 数字记法差异（不改上游，仅报备）：image_only clean α=0.10 conformal coverage 从
   l1d3_conformal_summary.csv 复算为 G1/G3/G5=0.892/0.865/0.835，区间≈0.83-0.89；
   而 14 号叙事骨架/claim边界表记为"≈0.83-0.85"。二者对"欠覆盖(<0.90)"结论一致，
   本轮图与草案已按复算区间标注并注明骨架记法。请 Codex 裁决以哪一记法为准。
```

## 5. 未决/阻塞

```text
- 无阻塞。所有子任务 A-E 完成，图/表/草案/核验/红线自检齐备。
- seed=42 单次 run 的多 seed/fold 复算属 C 类改动，未在本轮执行，已在草案 R1 标注。
```
