# 路线一 C 阶段性证据链总表（route1c_evidence_chain）

最后更新：2026-07-01  
来源任务：R120 Codex 任务单 `1C_stage_results_evidence_pack`  
配套 CSV：`route1c_evidence_chain.csv`  
状态：Results 非正文证据整理，非论文正文、非阶段闭口、非最终投稿稿

本表把 R113/R115/R117/R119 四个已通过 Codex 审阅的阶段串成路线一 C 当前主证据链，供后续 Codex/作者裁决 Results 叙事、图表、SI、claim 边界与待补实验。只引用关键结论，不复述长历史。

---

## 四条主链概览

```text
链1 (R113): single-frame 负结果收口与 B6 判据轴闭口。
链2 (R115): clean/P-INT 多几何 OCS 单调增益。
链3 (R117): degraded/M-roll 真实性与 fixed-roll 边界。
链4 (R119): D3/P-DB/conformal 置信一致性与互补证据。
```

四链关系：链1 关闭旧 single-frame 判据/输出头补救轴，并把主线从"single-frame yaw-block CNN 胜负"复位到 24 号定义的多观测可观测性；链2 在 clean/P-INT 上给出 OCS-only 多几何单调增益的正向证据；链3 把该正结果推进到物理退化真实性轴与 fixed-roll 边界；链4 用非神经 P-DB 检索与 conformal 给出置信一致性与互补证据。四链共同支撑"model-known simulated 条件下多观测总光度向量对姿态信息的可观测性、互补性、置信一致性"这一 v0.4 主线，但均不构成路线一 C 整体闭口。

---

## 链1（R113）single-frame 负结果收口与 B6 判据轴闭口

- 审阅文件：`04_Codex审阅/R113_Codex_审阅_102通过_B6判据轴闭口并放行L1M2阶段门.md`
- 结果目录：`v0.4_results/10_b6_circular_regression_fix01/`
- 可写结论：model-known / fixed-roll / yaw-block 整段外推条件下，单帧图像、4维 per-part OCS 与 early-concat joint 均未得到稳定 yaw 外推；exact-bin 口径过严，不能读成 yaw 信息完全不存在；circular regression 改善 image/joint 的 cMAE 但救不回外推；判据/输出头不是主因，主因指向 single-frame 信息形态不足与 yaw-block 外推协议过强。
- 不可写边界：不得写成光度无用 / yaw 物理不可观测 / 图像无姿态信息 / 所有融合无效 / 多几何 OCS 已失败 / 路线一 C 整体失败；4维 per-part OCS 是 semi-oracle 诊断，非现实主线输入；"判据非主因"是已测 single-frame 判据轴上的稳定判断，非排除所有非信息形态因素。
- 核心数字：no-aug fold-matched best 口径 image_only cMAE=60.273°（delta vs P1-A −21.167°）；joint cMAE=72.740°（delta −8.653°）；ocs_only cMAE=143.805°（delta +54.553°）；C2/C3 exact-bin yaw=0.00%；基础网格总样本 2664（72 yaw × 37 pitch，roll 固定 0）。
- 数据源：`b6_foldmatched_vs_p1a_best.csv`、`b6_foldmatched_vs_p1a_final.csv`、`b6_run_metrics_summary_best.csv`、`b6_yawblock_stratified_best.csv`
- 论文用途：SI + limitation + methods note
- 风险等级：low

## 链2（R115）clean/P-INT 多几何 OCS 单调增益

- 审阅文件：`04_Codex审阅/R115_Codex_审阅_103通过_L1M2多几何OCS第一阶段正结果.md`
- 结果目录：`v0.4_results/11_l1m2_multigeometry_ocs/`
- 可写结论：model-known / fixed-roll / clean / P-INT / 总光度向量输入条件下，OCS-only 多观测总光度向量随观测几何数 L1-G1→L1-G3→L1-G5 呈单调增益；跨几何多观测总光度向量在 clean/P-INT 内插协议下提升姿态可观测性；旧 single-frame 负结果不能扩大为光度无用。
- 不可写边界：不得写成真实反演成功 / 真实望远镜验证 / field-proven / operational-ready / P-EXT yaw-block 已解决 / 多几何 OCS 在所有协议成立 / 路线一 C 整体闭口；clean P-INT 下 image_only 近饱和、joint 增益受天花板限制，不写强互补性；seed=42 单次 run，主结果前需多 seed/fold。
- 核心数字：OCS-only best yaw cMAE G1/G3/G5=76.56° / 38.22° / 22.77°；hit@30=0.277 / 0.672 / 0.811；P-EXT cMAE G1/G3/G5=154.58° / 146.19° / 157.25°（仍坍缩）。
- 几何注册：L1-G1={phase63}；L1-G3={phase24, phase63, phase120}；L1-G5={phase24, phase45, phase63, phase90, phase120}；G1⊂G3⊂G5 嵌套。
- 数据源：`l1m2_gain_curve_G1_G3_G5.csv`、`l1m2_metrics_summary_best.csv`、`l1m2_pint_vs_pext_ocs_only.csv`、`figures/l1m2_gain_curve_best.png`
- 论文用途：main + SI
- 风险等级：low

## 链3（R117）degraded 真实性与 M-roll fixed-roll 边界

- 审阅文件：`04_Codex审阅/R117_Codex_审阅_104通过_L1M3退化真实性与Mroll边界探针.md`
- 结果目录：`v0.4_results/12_l1m3_degraded_mroll/`
- 可写结论：R115 审计缺口补齐（12 个 run 的 samples_val final/best cmae_delta=0.0，五个几何 pixel area/ortho scale/depth epsilon/resolution 一致，flux transform 仅由 train 拟合、train/val/test 无 attitude 泄漏，G1⊂G3⊂G5 嵌套对齐）；OCS-only 多几何单调增益在物理退化（PSF/高斯模糊、Poisson shot noise、read noise、背景与梯度、降采样、测光误差）下保持，并随退化强度优雅收缩；fixed-roll 结论对 ±15° roll 量级扰动未被直接推翻，±30° 明显敏感。
- 不可写边界：不得写成真实观测验证 / 真实系统鲁棒性完成 / 路线一 C 整体闭口 / 三轴小项目完成 / P-EXT 已解决 / joint 强互补性已证明；degraded 非 B6 粗增广包；final 口径 G5 joint moderate hit@30=0.189 存在检查点选择敏感性；M-roll 仅 fixed-roll 边界探针、image_only zero-shot，非 roll-aware 训练、非三轴小项目。
- 核心数字：OCS-only cMAE clean/mild/moderate — G1=76.56 / 76.78 / 78.48°，G3=38.22 / 40.15 / 51.72°，G5=22.77 / 27.83 / 38.46°；M-roll G5 image_only zero-shot — 0° cMAE=8.68°/hit=0.990，±15°≈17.53°/19.67°、hit≈0.843/0.830，±30°≈32.99°/28.69°、hit≈0.587/0.567。
- 数据源：`degraded/l1m3_degraded_metrics_summary_best.csv`、`degraded/l1m3_degraded_gain_and_drop_summary.md`、`mroll/mroll_metrics_summary_best.csv`、`mroll/mroll_roll_sensitivity_summary.md`、`audit/l1m2_geometry_scale_consistency.csv`、`audit/l1m2_val_samples_recovery_summary.csv`
- 论文用途：main + SI + limitation
- 风险等级：low

## 链4（R119）D3/P-DB/conformal 置信一致性与互补证据

- 审阅文件：`04_Codex审阅/R119_Codex_审阅_105通过_L1D3置信一致性与PDB正式评估.md`
- 结果目录：`v0.4_results/13_l1d3_confidence_pdb/`
- 可写结论：P-DB 作为 model-known simulated template retrieval 证明 L1 多观测总光度向量含可检索 yaw 信息，top1 yaw hit@30 随 G1→G3→G5 单调上升并随退化优雅下降；P-DB 检索强于 neural ocs_only 回归，且二者构成互补证据链（yaw error Spearman≈0）；conformal set_size 随几何收紧，与多观测 OCS 信息量增益一致。
- 不可写边界：不得写成真实观测反演成功率 / 真实望远镜验证 / Bayesian posterior / 最终概率校准完成 / P-EXT 已解决 / 路线一 C 整体闭口 / 三轴小项目完成；neural margin risk-coverage 曲线近乎平坦（置信区分度弱）、image_only conformal 略欠覆盖，二者必须保留为负向观察；oracle 是上界，不代表可无监督选中正确一方。
- 核心数字：P-DB top1 yaw hit@30 clean G1/G3/G5=0.291 / 0.821 / 0.949，mild G5=0.892，moderate G5=0.780；clean G5 P-DB cMAE=8.19° vs neural ocs_only best=22.77°；clean G5 ocs_only 互补四象限 both-correct=237 / neural-only=3 / P-DB-only=44 / both-wrong=12，oracle hit@30=0.960，Spearman=0.066；conformal ocs_only clean α=0.10 set_size G1/G3/G5=321.8 / 245.7 / 126.2°；image_only coverage≈0.83–0.85（欠覆盖）；hardcase index 1231 行（ocs-hard 121 / image-hard 2 / disagreement-hard 748 / ambiguous-flux 148 / robust-easy 351）。
- 数据源：`pdb/l1d3_pdb_retrieval_summary.csv`、`consistency/l1d3_error_correlation_summary.csv`、`conformal/l1d3_conformal_summary.csv`、`hardcases/l1d3_hardcase_index.csv`、`figures/pdb_gain_curve.png`、`figures/complementarity_quadrants.png`、`figures/risk_coverage_curves.png`
- 论文用途：main + SI + limitation
- 风险等级：medium（P-DB / conformal 措辞边界较易被过度解读，须严格限定为 simulated）

---

## 证据链一致性自检

- 四链的 OCS-only 多几何增益方向一致：clean（R115）、退化（R117）、非神经检索（R119）三条独立口径都显示 G1→G3→G5 单调改善，互为交叉验证。
- 负向观察在四链中始终保留且不淡化：P-EXT 坍缩（R115）、joint 天花板/检查点敏感（R117）、neural margin 区分度弱与 image_only 欠覆盖（R119）。
- 无任何一链单独或合并可支撑路线一 C 整体闭口、真实反演验证或三轴小项目启动。
