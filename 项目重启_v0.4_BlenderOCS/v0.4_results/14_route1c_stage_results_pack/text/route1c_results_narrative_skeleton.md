# 路线一 C 阶段性 Results 非正文叙事骨架（route1c_results_narrative_skeleton）

最后更新：2026-07-01  
来源任务：R120 Codex 任务单 `1C_stage_results_evidence_pack` 子任务 C  
状态：**非正文** outline / claim ledger，供后续 Codex/作者写 Results 时取用；**不是**论文段落、不是投稿摘要、不是最终稿

格式约定：本文件为 bullet / outline / claim ledger。每条 claim 后统一附四项：
- `supporting evidence path`（支撑证据路径）
- `allowed wording`（允许措辞）
- `forbidden wording`（禁止措辞）
- `usable in`（main text / SI / limitation / future work）

术语统一：实验层命名 L1-G1/L1-G3/L1-G5；代码层 OBS_GEOMETRIES G0~G4 仅在方法附录/registry 出现。所有结论均限定 model-known simulated 条件。

---

## 1. Problem framing：旧 single-frame 负结果为何不等于光度无用

**Claim 1.1** 在 single-frame / fixed-roll / yaw-block 整段外推协议下，单帧图像、4维 per-part OCS 与 early-concat joint 均未得到稳定 yaw 外推，但这是特定协议+信息形态下的条件性负结果，不等于光度或图像无姿态信息。
- supporting evidence path：`10_b6_circular_regression_fix01/b6_foldmatched_vs_p1a_best.csv`、`b6_yawblock_stratified_best.csv`；`01_成果区/00_当前主用成果/00_B6-FIX01与single-frame负结果收口说明_R113通过.md`
- allowed wording：条件性负结果；single-frame 信息形态不足；yaw-block strict extrapolation gap。
- forbidden wording：光度无用；yaw 物理不可观测；图像无姿态信息；所有融合方法无效。
- usable in：SI + limitation

**Claim 1.2** exact-bin 是过严 sentinel 指标；改用 circular regression 可改善 image/joint 的 cMAE，说明训练头/判据不是主要失败原因，主因指向信息形态与外推协议。
- supporting evidence path：`10_b6_circular_regression_fix01/b6_foldmatched_vs_p1a_best.csv`（image_only cMAE=60.273°/delta −21.167°；joint=72.740°/delta −8.653°；ocs_only=143.805°/delta +54.553°）
- allowed wording：exact-bin 过严；circular regression 改善指标读数但救不回外推；判据非主因（已测 single-frame 判据轴）。
- forbidden wording：判据问题已完全排除所有因素；训练头修复即可解决 yaw 外推。
- usable in：SI + methods note

**Claim 1.3** 由此把主线从"single-frame yaw-block CNN 胜负"复位到 24 号定义的跨几何多观测可观测性、互补性与置信一致性。
- supporting evidence path：`01_成果区/00_当前主用成果/01_路线一C后续技术路线执行框架_R113通过.md`
- allowed wording：主线复位；negative result 作为 motivation 引出多观测路线。
- forbidden wording：路线一 C 整体失败；头A/头B 已大合并裁决。
- usable in：main text（作为 motivation 过渡）

---

## 2. Result block 1：clean/P-INT 多几何 OCS 可观测性

**Claim 2.1** model-known / fixed-roll / clean / P-INT 条件下，OCS-only 多观测总光度向量随几何数 L1-G1→L1-G3→L1-G5 呈单调增益。
- supporting evidence path：`11_l1m2_multigeometry_ocs/l1m2_gain_curve_G1_G3_G5.csv`、`l1m2_metrics_summary_best.csv`、`figures/l1m2_gain_curve_best.png`（cMAE 76.56→38.22→22.77°；hit@30 0.277→0.672→0.811）
- allowed wording：跨几何多观测总光度向量提升姿态可观测性；加几何=单调加信息（G1⊂G3⊂G5 嵌套）。
- forbidden wording：真实反演成功；所有协议成立；operational-ready。
- usable in：main text（核心正结果）

**Claim 2.2** clean P-INT 下 image_only 已近饱和，joint 增益受天花板限制，本阶段不主张强互补性。
- supporting evidence path：`11_l1m2_multigeometry_ocs/l1m2_metrics_summary_best.csv`、`l1m2_complementarity_summary.csv`
- allowed wording：clean 上界下 image_only 近饱和；joint 增益受天花板限制；互补性留待更难协议。
- forbidden wording：joint 强互补性已证明。
- usable in：main text + limitation

---

## 3. Result block 2：degraded 真实性轴与 M-roll fixed-roll 边界

**Claim 3.1** OCS-only 多几何单调增益在物理退化（PSF/模糊、Poisson/read noise、背景梯度、降采样、测光误差）下保持，并随退化强度优雅收缩。
- supporting evidence path：`12_l1m3_degraded_mroll/degraded/l1m3_degraded_metrics_summary_best.csv`、`degraded/l1m3_degraded_gain_and_drop_summary.md`（G5 cMAE clean/mild/moderate=22.77/27.83/38.46°）
- allowed wording：增益非 clean-only 假象；物理退化下保持并优雅收缩。
- forbidden wording：真实观测验证；真实系统鲁棒性完成；severe 退化已验证。
- usable in：main text + SI

**Claim 3.2** 审计缺口已补齐：val samples 恢复 cmae_delta=0.0，跨几何量纲一致，train/val/test 无 attitude 泄漏，G1⊂G3⊂G5 对齐。
- supporting evidence path：`12_l1m3_degraded_mroll/audit/l1m2_val_samples_recovery_summary.csv`、`audit/l1m2_geometry_scale_consistency.csv`、`audit/l1m2_transform_leakage_check.json`
- allowed wording：量纲一致性核验通过；无 inverse-crime 泄漏；simulated multi-view geometry。
- forbidden wording：真实跨时间多几何；路线二真实数据已对齐。
- usable in：SI + methods note

**Claim 3.3** fixed-roll 结论对 ±15° roll 量级扰动（image_only zero-shot）未被直接推翻，±30° 明显敏感。
- supporting evidence path：`12_l1m3_degraded_mroll/mroll/mroll_metrics_summary_best.csv`、`mroll/mroll_roll_sensitivity_summary.md`（G5 0°/±15°/±30° cMAE=8.68/17.5-19.7/33.0-28.7°）
- allowed wording：fixed-roll 边界探针；±15° 未直接推翻、±30° 敏感。
- forbidden wording：roll-aware 能力；三轴姿态反演；M-roll 替代三轴小项目。
- usable in：main text + limitation

---

## 4. Result block 3：P-DB / conformal 证明可检索信息与置信一致性

**Claim 4.1** P-DB（model-known simulated template retrieval）证明 L1 多观测总光度向量含可检索 yaw 信息，top1 hit@30 随 G1→G3→G5 单调上升、随退化优雅下降。
- supporting evidence path：`13_l1d3_confidence_pdb/pdb/l1d3_pdb_retrieval_summary.csv`、`figures/pdb_gain_curve.png`（clean G1/G3/G5=0.291/0.821/0.949；moderate G5=0.780）
- allowed wording：多观测总光度向量含可检索 yaw 信息；simulated template retrieval。
- forbidden wording：真实观测反演成功率；真实望远镜验证。
- usable in：main text

**Claim 4.2** P-DB 检索强于 neural ocs_only 回归，二者误差近不相关（Spearman≈0），构成互补证据链，说明神经回归未充分利用光度信息。
- supporting evidence path：`13_l1d3_confidence_pdb/consistency/l1d3_error_correlation_summary.csv`、`figures/complementarity_quadrants.png`（P-DB cMAE=8.19° vs neural=22.77°；四象限 237/3/44/12；oracle hit@30=0.960）
- allowed wording：P-DB 与 neural 互补；神经回归未充分吸收光度信息；oracle 为上界。
- forbidden wording：无监督可选中正确一方；两通道融合已实现。
- usable in：main text + SI

**Claim 4.3** conformal set_size 随几何收紧，与多观测信息量增益一致，coverage 近 target=0.90。
- supporting evidence path：`13_l1d3_confidence_pdb/conformal/l1d3_conformal_summary.csv`、`figures/risk_coverage_curves.png`（ocs_only clean α=0.10 set_size G1/G3/G5=321.8/245.7/126.2°）
- allowed wording：set_size 随几何收紧；当前 simulated split 下校准自洽。
- forbidden wording：Bayesian posterior；最终概率校准完成；真实天文观测不确定度。
- usable in：main text + SI

---

## 5. Negative observations（必须保留、不得淡化）

**Claim 5.1** P-EXT yaw-block strict extrapolation 下 OCS-only 仍坍缩（三几何 cMAE≈146-157°）。
- supporting evidence path：`11_l1m2_multigeometry_ocs/l1m2_pint_vs_pext_ocs_only.csv`
- allowed wording：P-EXT 仍是过强外推 stress test，不能替代主线。
- forbidden wording：P-EXT yaw-block 已解决。
- usable in：SI + limitation

**Claim 5.2** image/joint 天花板效应与 final 口径检查点敏感（G5 joint moderate hit@30=0.189）。
- supporting evidence path：`12_l1m3_degraded_mroll/degraded/l1m3_degraded_metrics_summary_final.csv`
- allowed wording：joint 强互补性未显现；存在检查点选择敏感性。
- forbidden wording：joint 强互补性已证明。
- usable in：limitation

**Claim 5.3** neural margin 置信区分度弱（risk-coverage 近平坦）、image_only conformal 略欠覆盖（≈0.83-0.85）。
- supporting evidence path：`13_l1d3_confidence_pdb/consistency/l1d3_risk_coverage.csv`、`conformal/l1d3_conformal_summary.csv`、`figures/confidence_decile_error.png`
- allowed wording：当前工程置信分数区分度弱；image_only 存在分布/误差形态偏移。
- forbidden wording：选择性预测强可用；置信排序已强可用。
- usable in：limitation

**Claim 5.4** image_only 在部分分析维欠覆盖，joint 未展示对 image_only 的稳定增量。
- supporting evidence path：`11_l1m2_multigeometry_ocs/l1m2_complementarity_summary.csv`、`13_l1d3_confidence_pdb/hardcases/l1d3_hardcase_index.csv`（image-hard 仅 2/0 行）
- allowed wording：image_only 欠覆盖；joint 增量待 P-INT-hard/degraded-severe 检验。
- forbidden wording：image/joint 已充分覆盖。
- usable in：limitation

---

## 6. Remaining gaps（未解决/未启动，仅作 future work 备案）

**Claim 6.1** degraded-severe 与 P-INT-hard 尚未评估；hard-case index 已备为候选输入，但非阶段门放行。
- supporting evidence path：`13_l1d3_confidence_pdb/hardcases/l1d3_hardcase_index.csv`、`l1d3_recommended_pinthard_design.md`
- allowed wording：degraded-severe / P-INT-hard 为候选下一步；hard-case index 为候选输入。
- forbidden wording：已启动新训练；阶段门已放行。
- usable in：future work

**Claim 6.2** 真实 GEO 数据只可作 sim-to-real 光度趋势/分布/多帧几何锚点，无三轴姿态真值，不能写成监督反演数据集。
- supporting evidence path：`01_成果区/00_当前主用成果/01_路线一C后续技术路线执行框架_R113通过.md`（第 7 节）
- allowed wording：GEO 只可作光度锚点；无姿态真值。
- forbidden wording：GEO 有三轴姿态真值；真实 GEO 反演成功率。
- usable in：future work + limitation

**Claim 6.3** 三轴小项目未启动；M-roll 仅 fixed-roll 边界探针，不替代三轴。
- supporting evidence path：`01_成果区/00_当前主用成果/01_路线一C后续技术路线执行框架_R113通过.md`（第 6 节）
- allowed wording：三轴小项目为路线一 C 之后的桥接层；本阶段未启动。
- forbidden wording：三轴小项目已启动/完成。
- usable in：future work

---

## 7. 叙事骨架自检

- 结构覆盖 R120 建议的 6 段：problem framing → block1 → block2 → block3 → negative observations → remaining gaps。
- 每条 claim 均附 evidence path / allowed / forbidden / usable in 四项。
- 全文为 outline / claim ledger，无正式论文段落；负向观察独立成段且不淡化；未越界写路线一 C 整体闭口或真实反演验证。
