# 路线一 C SI 图表图注草案（si_captions_draft）

最后更新：2026-07-01
来源任务：R122 子任务 B
状态：**图注草案**，供 Codex/作者润色；非最终论文正文。所有结论限定 model-known simulated。

---

## SI-1 — B6 single-frame 判据轴闭口证据链

**Caption（草案）：** single-frame / fixed-roll / yaw-block 整段外推下，circular regression（B6）相对 exact-bin head（P1-A）改善 image_only / joint 的 yaw cMAE（fold-mean，no-aug best），但未救回 yaw 外推，ocs_only 反而变差。说明 exact-bin 是过严 sentinel，判据/输出头不是主要失败原因，主因指向 single-frame 信息形态不足与 yaw-block 外推协议过强。

**allowed：** circular regression 改善 image/joint cMAE 但 yaw 外推仍坍缩；条件性负结果。
**forbidden：** 不写光度无用 / 图像无姿态信息 / 训练头修复即可解决 yaw 外推。
**source：** `10_b6_circular_regression_fix01/b6_foldmatched_vs_p1a_best.csv`（aug=none）。

---

## SI-2 — P-INT vs P-EXT yaw-block stress test

**Caption（草案）：** OCS-only 在 P-INT 内插下随几何单调增益（76.56→38.22→22.77°），但在 P-EXT strict yaw-block 外推下三个几何均坍缩（154.58 / 146.19 / 157.25°）。多观测总光度向量提升内插可观测性，但不解决 yaw-block 整段外推。

**allowed：** P-EXT strict extrapolation 仍坍缩，不能替代主线协议。
**forbidden：** 不写 yaw-block 外推已解决。
**source：** `11_l1m2_multigeometry_ocs/l1m2_pint_vs_pext_ocs_only.csv`。

---

## SI-3 — M-roll ±15/±30 边界探针

**Caption（草案）：** fixed-roll 结论的 roll 敏感性边界探针（image_only zero-shot）。roll∈{0,±15,±30}° 下 L1-G1 与 L1-G5 的 yaw cMAE / hit@30；阴影区为 ±15° 范围。L1-G5 由 0° 的 8.68° 升至 ±15° 的 17.5–19.7°、±30° 的 33.0–28.7°。±15° 未直接推翻 fixed-roll，±30° 明显敏感。

**allowed：** fixed-roll 边界探针；±15° 未直接推翻、±30° 敏感。
**forbidden：** 不写 roll-aware 能力 / 三轴姿态反演 / M-roll 替代三轴小项目。
**source：** `12_l1m3_degraded_mroll/mroll/mroll_metrics_summary_best.csv`。

---

## SI-4 — hard-case index 五类分布

**Caption（草案）：** hard-case index 共 1231 行的标签分布：disagreement-hard=748、robust-easy=351、ambiguous-flux=148、ocs-hard=121、image-hard=2。该分布为下一阶段 P-INT-hard 的候选输入定义，不构成阶段门放行。

**allowed：** hard-case index 是下一阶段候选输入的五类分布。
**forbidden：** 不写阶段门放行 / 已启动新训练。
**source：** `13_l1d3_confidence_pdb/hardcases/l1d3_hardcase_index.csv`。

---

## SI-5 — 数据/代码/结果路径 manifest

**Caption（草案）：** 汇总 14 号证据包 60 行 manifest 与本轮 15 号包新增文件的可复查路径索引，见 `tables/SI5_manifest_table.csv`。

**source：** `14_route1c_stage_results_pack/audit/route1c_stage_results_manifest.csv` + 本轮新文件。

---

## SI-x1（可选补充）— neural vs P-DB error scatter（复用 R119）

**Caption（草案）：** neural ocs_only 与 P-DB 的 yaw 误差近不相关（Spearman≈0），支撑二者互补性。复用 R119 现有图。

**forbidden：** 不写两者可无监督融合已实现。
**source：** `13_l1d3_confidence_pdb/figures/neural_vs_pdb_error_scatter.png`（复制为 `SIx1_...`）。

---

## SI-x2（可选补充）— confidence decile error（复用 R119）

**Caption（草案）：** neural margin 置信分数按 decile 分层的误差近平坦，支撑置信区分度弱的负向观察。复用 R119 现有图。

**forbidden：** 不写选择性预测强可用。
**source：** `13_l1d3_confidence_pdb/figures/confidence_decile_error.png`（复制为 `SIx2_...`）。

---

## SI 图注自检

- SI-1 至 SI-5 图注均绑定 source path 与 allowed/forbidden，与 claim 边界表、叙事骨架口径一致。
- SI-x1/x2 明确标为 R119 复用图，未伪装为本轮新证据。
- 负向观察（P-EXT 坍缩、roll 敏感、置信区分度弱）在 SI 中显式保留。
