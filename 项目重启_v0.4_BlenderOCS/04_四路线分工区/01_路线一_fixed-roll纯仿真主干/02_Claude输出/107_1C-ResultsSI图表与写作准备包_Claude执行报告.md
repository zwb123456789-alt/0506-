# 107 路线一 C：Results/SI 图表与写作准备包 — Claude 执行报告

最后更新：2026-07-01
任务单：`04_Codex审阅/R122_Codex_任务单_1C-ResultsSI图表与写作准备包.md`
上游阶段门：R121 已通过 106，路线一 C 阶段性 Results 非正文证据包接收
交付包目录：`v0.4_results/15_route1c_results_si_preparation_pack/`

---

## 1. 任务结论摘要

**完成。** R122 子任务 A-E 全部达标：主图 Fig.1-Fig.5、SI 图 SI-1至SI-4（+SIx1/x2 复用）、5 张表、3 份文本草案、2 个绘图/汇总脚本、4 个 audit 文件全部生成。数字核验 33 项全部 PASS、0 CONFLICT；红线自检 RL1-RL10 全部 PASS。本轮为写作前整理，不新训练、不新渲染、不写最终正文、不入成果区、不生成 Codex 审阅文件、不改 CLAUDE.md。

无阻塞。存在 1 项数字记法差异（image_only coverage 区间）已透明报备，交 Codex 裁决（见第 9/11 节）。

## 2. 已读文件与遵守的红线

已读：

```text
CLAUDE.md（v0.4 权威入口）
04_Codex审阅/R121_..._1C阶段性Results非正文证据包.md
04_Codex审阅/R122_..._1C-ResultsSI图表与写作准备包.md（任务单）
01_成果区/00_当前主用成果/08_路线一C阶段性Results非正文证据包_R121通过.md
14_route1c_stage_results_pack/text/: route1c_evidence_chain.md / route1c_figure_plan.md /
  route1c_results_narrative_skeleton.md / route1c_claim_boundary_table.md
14_route1c_stage_results_pack/audit/route1c_stage_results_manifest.csv
数据源 CSV/JSON：10/11/12/13 目录相关文件（逐条见 source_map 与 numeric_consistency_check）
```

遵守红线：仅改动项目根目录内部；本轮只写 15 号包与本 107 报告；未新训练/新渲染/新后处理矩阵；未改任何旧 `.py`/旧 metrics/旧 samples/旧结果目录；所有 claim 限定 model-known simulated；P-DB 写为 simulated template retrieval；conformal 写为当前 simulated split；保留全部负向观察。

## 3. 新增脚本清单

| 脚本 | 用途 | 是否改旧脚本 |
|---|---|---|
| `15.../scripts/make_figures.py` | 读 10/11/12/13 源 CSV/JSON 生成 Fig1-5、SI1-4（PNG+PDF） | 否，新文件 |
| `15.../scripts/make_audit.py` | 数字核验、生成文件 manifest、SI5 manifest | 否，新文件 |

均写入 15 号包 `scripts/`，未新增到 `06_v0.4_code/`，未改任何既有脚本。

## 4. 主图交付清单

| 图 | 路径(PNG+PDF) | 数据源 | 重绘/复用 |
|---|---|---|---|
| Fig.1 | figures_main/Fig1_protocol_schematic.* | geometry_registry.json + 24号定义 | 新绘概念图 |
| Fig.2 | figures_main/Fig2_clean_pint_ocs_gain.* | 11_l1m2/l1m2_pint_vs_pext_ocs_only.csv | 新绘 |
| Fig.3 | figures_main/Fig3_degraded_ocs_gain.* | 11(clean)+12/degraded/..._best.csv | 新绘 |
| Fig.4 | figures_main/Fig4_pdb_neural_complementarity.* | 13/pdb+consistency 三文件 | 新绘 |
| Fig.5 | figures_main/Fig5_conformal_geometry_confidence.* | 13/conformal/l1d3_conformal_summary.csv | 新绘 |

配套：`tables/main_figure_source_map.csv`、`text/main_figure_captions_draft.md`。全部 PNG+PDF（矢量）双格式。

## 5. SI 图表交付清单

| 项 | 路径 | 数据源 | 重绘/复用 |
|---|---|---|---|
| SI-1 | figures_si/SI1_b6_single_frame_closure.* | 10/b6_foldmatched_vs_p1a_best.csv | 新绘 |
| SI-2 | figures_si/SI2_pint_vs_pext_stress.* | 11/l1m2_pint_vs_pext_ocs_only.csv | 新绘 |
| SI-3 | figures_si/SI3_mroll_boundary_probe.* | 12/mroll/mroll_metrics_summary_best.csv | 新绘 |
| SI-4 | figures_si/SI4_hardcase_index.* | 13/hardcases/l1d3_hardcase_index.csv | 新绘 |
| SI-5 | tables/SI5_manifest_table.csv | 14 manifest(60) + 15号新文件(36) | 表格 |
| SI-x1 | figures_si/SIx1_neural_vs_pdb_error_scatter.png | 13/figures/ 同名图 | 复用R119 |
| SI-x2 | figures_si/SIx2_confidence_decile_error.png | 13/figures/ 同名图 | 复用R119 |

配套：`tables/si_figure_source_map.csv`、`text/si_captions_draft.md`。

## 6. Results 受控草案交付清单

- `text/results_candidate_draft_controlled.md`：6 段（R0-R5），每段绑定 paragraph_id / claim_ids / evidence paths / linked figures / allowed / forbidden / risk tag。
- `tables/paragraph_claim_evidence_map.csv`：6 段 → claim/证据/图/风险映射。
- `tables/claim_figure_table_map.csv`：18 条 claim（C1.1-C6.3）→ writable_id / 图 / 表 / 关键数字 / 风险映射。
- R3（P-DB/conformal）标为 medium 风险；负向观察 R4 独立成段。未新增 R121 以外 claim，未写 Abstract/Intro/Discussion 全文与投稿语气。

## 7. 数字一致性核验摘要

- `audit/numeric_consistency_check.csv/.md`：共 **33 项，PASS=33，CONFLICT=0**。
- 覆盖 R122 第 6 节全部指定数字：R115 OCS-only cMAE/hit@30(G1/G3/G5)、P-EXT cMAE、R117 degraded G5、M-roll G5(0/±15/±30)、R119 P-DB clean G5、neural G5、oracle、Spearman、四象限、conformal set_size(G1/G3/G5)、image_only coverage 区间、R113 B6 三模式。
- 均从 10/11/12/13 原始 CSV 复算比对（角度容差 0.5°，hit/相关系数 0.01）。

## 8. manifest 与可复查索引摘要

- `audit/generated_files_manifest.csv/.md`：15 号包 **36 个文件**，含 size + sha256(8)。
- `tables/SI5_manifest_table.csv`：上游 14 号 60 行 + 本轮新增 36 行，可复查路径索引。

## 9. 未完成项与阻塞项

- 无阻塞，A-E 全部完成。
- seed=42 单次 run 的多 seed/fold 复算属 C 类改动，本轮未执行（红线内），已在草案 R1 与 checklist 标注。

## 10. 红线自检

`audit/redline_self_check.csv`：RL1-RL10 全部 PASS。要点：未新训练/新渲染/新后处理矩阵；未改旧脚本/旧结果目录；未写成果区/未生成Codex审阅文件/未改CLAUDE.md；未写最终正文/投稿摘要；claim 全程 model-known simulated；P-EXT坍缩/joint天花板检查点敏感/neural margin弱/image_only欠覆盖四项负向观察保留；P-DB非真实反演成功率；conformal非Bayesian posterior/最终校准；路线一C非整体闭口；三轴/T3-L2/路线二三四未启动。

## 11. 交给 Codex 审阅的裁决问题清单

详见 `text/codex_review_checklist_for_107.md`，摘要：

```text
Q1 Fig.2/Fig.3 clean 数据取 l1m2_pint_vs_pext_ocs_only.csv(P-INT) 是否需改 metrics_summary_best 口径。
Q2 P-DB 主口径固定 neg-L2 + matched-degraded + test 是否为 R119 认可主口径。
Q3 conformal 是否统一 α=0.10 best，是否补 α=0.05/0.20 敏感性到 SI。
Q4 受控草案能否进入正式 Results 段落，还是需先补多 seed/fold 与 P-INT-hard。
Q5 15 号包能否作为 R123 审阅对象；成果区升级由 Codex 决定，本轮不自行升级。
Q6 数字记法差异报备：image_only clean α=0.10 coverage 复算为 0.892/0.865/0.835（区间0.83-0.89），
   14号骨架记"≈0.83-0.85"，二者"欠覆盖<0.90"结论一致；本轮已按复算区间标注并注明骨架记法，请 Codex 裁决记法。
```
