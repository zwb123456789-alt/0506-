# 路线一 C 阶段性 Claim 边界与红线表（route1c_claim_boundary_table）

最后更新：2026-07-01  
来源任务：R120 Codex 任务单 `1C_stage_results_evidence_pack` 子任务 D  
配套 CSV：`route1c_claim_boundary_table.csv`  
状态：可写/不可写边界表，供后续 Results 写作红线校准；每条可写 claim 均绑定证据路径

---

## 可写（writable）

| id | 可写陈述 | 关键数字 | 论文范围 | 证据路径 |
|---|---|---|---|---|
| W1 | model-known simulated 条件下，L1 多观测总光度向量含姿态(yaw)信息 | OCS-only cMAE G5=22.77°；P-DB top1 hit@30 clean G5=0.949 | main | `11_l1m2.../l1m2_gain_curve_G1_G3_G5.csv`；`13_l1d3.../pdb/l1d3_pdb_retrieval_summary.csv` |
| W2 | OCS-only 多几何增益在 clean 与 mild/moderate degraded 下保持 | G5 cMAE clean/mild/moderate=22.77/27.83/38.46° | main | `12_l1m3.../degraded/l1m3_degraded_metrics_summary_best.csv` |
| W3 | P-DB 检索提供非神经证据，说明 neural ocs_only 未充分利用光度信息 | P-DB=8.19° vs neural=22.77°；Spearman≈0；oracle hit@30=0.960 | main+SI | `13_l1d3.../consistency/l1d3_error_correlation_summary.csv` |
| W4 | conformal set_size 随几何收紧，当前 split 下 uncertainty interval 与信息量一致 | set_size G1/G3/G5=321.8/245.7/126.2°；coverage≈0.90 | main+SI | `13_l1d3.../conformal/l1d3_conformal_summary.csv` |
| W5 | M-roll ±15° 未直接推翻 fixed-roll 结论，±30° 敏感 | G5 0°/±15°/±30° cMAE=8.68/17.5-19.7/33.0-28.7° | main+limitation | `12_l1m3.../mroll/mroll_metrics_summary_best.csv` |
| W6 | 旧 single-frame 负结果为条件性负结果，非光度无用 | image_only cMAE=60.273°(delta −21.167°) | SI+limitation | `10_b6.../b6_foldmatched_vs_p1a_best.csv` |
| W7 | 当前证据支持路线一 C 阶段性 Results 非正文材料整理 | 四链 R113/R115/R117/R119 | process note | 本证据包 `14_route1c_stage_results_pack/` |
| W8 | 主线已从 single-frame 负结果转入 L1 多观测正结果与置信一致性证据链 | — | main(motivation) | `01_成果区/00_当前主用成果/01_...执行框架_R113通过.md` |

关键限定语（写作时必带）：所有 W 类 claim 均限定 **model-known simulated**；P-DB 写为 **simulated template retrieval**；conformal 写为 **当前 simulated split 下**；M-roll 写为 **image_only zero-shot 边界探针**。

---

## 不可写（forbidden）

| id | 禁止陈述 | 反证/边界 | 证据路径 |
|---|---|---|---|
| F1 | 真实未知目标姿态反演系统已经实现 | 仅 model-known simulated | — |
| F2 | 真实望远镜验证 / field-proven / operational-ready | 无任何真实观测验证 | — |
| F3 | GEO 数据库有三轴姿态真值 | GEO 无姿态真值，只可作光度锚点 | `01_成果区/.../01_...执行框架_R113通过.md`(第7节) |
| F4 | P-EXT yaw-block 已解决 | P-EXT cMAE≈146-157° 仍坍缩 | `11_l1m2.../l1m2_pint_vs_pext_ocs_only.csv` |
| F5 | joint 强互补性已证明 | G5 joint moderate hit@30=0.189 检查点敏感 | `12_l1m3.../degraded/l1m3_degraded_metrics_summary_final.csv` |
| F6 | Bayesian posterior 或最终概率校准已完成 | posterior-like 仅工程候选分数；conformal 仅 simulated split | `13_l1d3.../conformal/l1d3_conformal_summary.csv` |
| F7 | P-DB 是真实观测反演成功率 | model-known simulated template retrieval | `13_l1d3.../pdb/l1d3_pdb_retrieval_summary.csv` |
| F8 | 选择性预测/置信排序已强可用 | neural margin risk-coverage 近平坦 | `13_l1d3.../consistency/l1d3_risk_coverage.csv` |
| F9 | 路线一 C 整体闭口 | 当前非整体闭口点 | — |
| F10 | 三轴小项目已启动或完成 | M-roll 非三轴替代；未启动 | `01_成果区/.../01_...执行框架_R113通过.md`(第6节) |
| F11 | 头A/头B 大合并裁决已完成 | 未放行 | CLAUDE.md 红线 |
| F12 | 4维 per-part OCS 是现实主线输入 | semi-oracle/diagnostic | `00_...single-frame负结果收口说明_R113通过.md` |
| F13 | image_only conformal 覆盖良好 | image_only coverage≈0.83-0.85 欠覆盖 | `13_l1d3.../conformal/l1d3_conformal_summary.csv` |
| F14 | T3/L2 光变正式训练 / 路线二三四扩展已启动 | 未放行 | CLAUDE.md 红线 |

---

## 边界表自检

- 覆盖 R120 第 6 节列出的全部可写/不可写项，并按当前证据补充 W6-W8、F11-F14。
- 每条可写 claim 均绑定证据路径与数字；每条不可写 claim 均给出反证或红线来源。
- 与叙事骨架、证据链总表口径一致，可作为后续 Results 写作的红线校准依据。
