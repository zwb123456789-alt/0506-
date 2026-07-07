# 路线一 C 阶段性 Results 图表与 SI 候选清单（route1c_figure_plan）

最后更新：2026-07-01  
来源任务：R120 Codex 任务单 `1C_stage_results_evidence_pack` 子任务 B  
配套 CSV：`route1c_figure_plan.csv`  
状态：候选图表清单，非正式论文图；每个候选均绑定现有数据源，禁止凭记忆画

说明：本清单区分"已存在可复用图"（已复制进 `figures/` 目录，前缀 `copy_`）与"需新绘/表格代图"两类。所有需新绘图仅做轻量制图，不启动新训练/新渲染/新后处理矩阵。若最终只生成占位图清单，原因是本轮任务边界为整理而非正式出图。

---

## 主图候选

### Fig.1（P0）任务与协议示意图 — 需新绘概念图
- 内容：model-known simulated multi-view OCS / image / P-DB / conformal 证据链示意。画 model-known 前向模型 → 多几何 sun/view → 总光度向量 / 图像 → P-INT / P-DB / conformal。
- 数据源：概念图，无单一数据源；标注引用 `l1m2_geometry_registry.md` 与 24 号主线定义。
- 允许读法：仅示意 model-known simulated 数据流与协议关系。
- 禁止读法：不画真实望远镜验证 / 真实 GEO 反演 / 三轴姿态真值链路。

### Fig.2（P0）clean/P-INT OCS-only G1/G3/G5 单调增益曲线 — 现有图可用
- 数据源：`v0.4_results/11_l1m2_multigeometry_ocs/l1m2_gain_curve_G1_G3_G5.csv`
- 现有图：`11_l1m2_multigeometry_ocs/figures/l1m2_gain_curve_best.png` → 已复制 `figures/copy_R115_l1m2_gain_curve_best.png`
- 重绘：可选。若做正式主图，建议统一实验层命名 L1-G1/G3/G5 并加 hit@30 子图。
- 允许读法：OCS-only cMAE/hit@30 随几何数单调改善（G1=76.56°→G5=22.77°）。
- 禁止读法：不得标注为真实反演精度 / 所有协议成立。

### Fig.3（P1）degraded 下 OCS-only 增益保持与退化收缩 — 需新绘
- 数据源：`12_l1m3_degraded_mroll/degraded/l1m3_degraded_metrics_summary_best.csv`、`degraded/l1m3_degraded_gain_and_drop_summary.md`
- 重绘：需新绘 clean/mild/moderate 三条增益曲线并列，展示增益保持 + 优雅收缩；数据已在 CSV，轻量制图。
- 允许读法：多几何增益在物理退化下保持并随退化优雅收缩。
- 禁止读法：不得写成真实观测鲁棒性完成 / severe 退化已验证。

### Fig.4（P0）P-DB vs neural ocs_only + 互补四象限 — 现有图可合成
- 数据源：`13_l1d3_confidence_pdb/pdb/l1d3_pdb_retrieval_summary.csv`、`consistency/l1d3_error_correlation_summary.csv`
- 现有图：`figures/pdb_gain_curve.png` + `figures/complementarity_quadrants.png` → 已复制 `figures/copy_R119_pdb_gain_curve.png`、`figures/copy_R119_complementarity_quadrants.png`
- 重绘：可选，两现有图可合成双 panel 主图；保留 simulated template retrieval 标注。
- 允许读法：P-DB（cMAE=8.19°）强于 neural（22.77°）且互补（Spearman≈0，oracle hit@30=0.960）。
- 禁止读法：不得写成真实观测反演成功率 / 无监督可选中正确一方。

### Fig.5（P1）conformal set_size 随几何收紧与负向观察 — 现有图可用
- 数据源：`13_l1d3_confidence_pdb/conformal/l1d3_conformal_summary.csv`
- 现有图：`figures/risk_coverage_curves.png` → 已复制 `figures/copy_R119_risk_coverage_curves.png`
- 重绘：可选，建议补一张 set_size(G1/G3/G5) 柱状 + coverage 标注。
- 允许读法：set_size 随几何收紧（321.8°→126.2°），coverage 近 target=0.90。
- 禁止读法：不得写成 Bayesian posterior / 最终概率校准；image_only 欠覆盖须标注。

---

## SI 图表候选

### SI-1（P1）B6 single-frame 判据轴闭口证据链 — 需新绘/表格代图
- 数据源：`10_b6_circular_regression_fix01/b6_foldmatched_vs_p1a_best.csv`、`b6_yawblock_stratified_best.csv`
- 允许读法：circular regression 改善 image/joint cMAE 但 yaw 外推仍坍缩。
- 禁止读法：不得写成光度无用 / 图像无姿态信息。

### SI-2（P1）P-EXT yaw-block stress test 仍坍缩 — 需新绘
- 数据源：`11_l1m2_multigeometry_ocs/l1m2_pint_vs_pext_ocs_only.csv`
- 重绘：P-INT vs P-EXT cMAE 并列条形，显示 P-EXT 三几何均 ≈150°。
- 允许读法：P-EXT strict extrapolation 仍坍缩，不能替代主线协议。
- 禁止读法：不得写成 yaw-block 外推已解决。

### SI-3（P1）M-roll ±15/±30 边界探针 — 需新绘
- 数据源：`12_l1m3_degraded_mroll/mroll/mroll_metrics_summary_best.csv`、`mroll/mroll_roll_sensitivity_summary.md`、原始 `mroll/mroll_eval_results.json`
- 重绘：roll∈{0,±15,±30} 的 cMAE/hit@30 曲线（G1,G5）。
- 允许读法：±15° roll 未直接推翻 fixed-roll，±30° 明显敏感。
- 禁止读法：不得写成 roll-aware 能力 / 三轴姿态反演。

### SI-4（P2）hard-case index 与 P-INT-hard 候选定义 — 需新绘/表格代图
- 数据源：`13_l1d3_confidence_pdb/hardcases/l1d3_hardcase_index.csv`、`l1d3_hardcase_summary.md`、`l1d3_recommended_pinthard_design.md`
- 重绘：五类 hard-case 计数柱状（1231 行）；或表格代图。
- 允许读法：hard-case index 是下一阶段候选输入的五类分布。
- 禁止读法：不得写成阶段门放行 / 已启动新训练。

### SI-5（P0）数据/代码/结果路径 manifest — 表格
- 数据源：`14_route1c_stage_results_pack/audit/route1c_stage_results_manifest.csv`
- 直接用 manifest 表格，无需作图。

### 可选补充 SI

- SI-x1（P2）neural_vs_pdb error scatter：现有 `copy_R119_neural_vs_pdb_error_scatter.png`，支撑互补性（误差近不相关）。禁止写成两者可无监督融合已实现。
- SI-x2（P2）confidence decile error：现有 `copy_R119_confidence_decile_error.png`，支撑 neural margin 置信区分度弱的负向观察。禁止写成选择性预测强可用。

---

## 图表清单自检

- 已复用现有图 7 张（R115 2 张、R119 5 张），全部保留原始数据源路径且复制到 `figures/` 时加 `copy_R1xx_` 前缀，不覆盖原图。
- 需新绘 6 项（Fig.1 概念图、Fig.3、SI-1、SI-2、SI-3、SI-4），本轮不出正式图，只给绑定数据源与重绘说明，留待正式 Results 阶段轻量制图。
- 每个候选均给出 allowed reading 与 forbidden reading，与 claim 边界表一致。
