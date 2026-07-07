# 路线一 C 受控 Results 候选草案（results_candidate_draft_controlled）

最后更新：2026-07-01
来源任务：R122 子任务 C
状态：**受控草案（controlled draft）**，非最终论文正文、非投稿摘要、非投稿稿。每段可审查、可回滚、可逐句追溯。

全文限定 **model-known simulated**。术语统一：实验层 L1-G1 / L1-G3 / L1-G5。
每段附：paragraph_id / claim_ids / evidence paths / linked figures / allowed wording / forbidden wording / risk tag。
配套映射：`tables/paragraph_claim_evidence_map.csv`、`tables/claim_figure_table_map.csv`。

---

## R0 — Problem framing：single-frame 负结果为何不等于光度无用

**草案段落：**
在 single-frame、fixed-roll、yaw-block 整段外推协议下，单帧图像、4维 per-part OCS 与 early-concat joint 均未获得稳定的 yaw 外推。这是特定协议与信息形态下的**条件性负结果**，不等于光度或图像无姿态信息。进一步分析显示 exact-bin 是过严的 sentinel 指标：改用 circular regression 可改善 image_only / joint 的 cMAE，说明训练判据与输出头不是主要失败原因，主因指向 single-frame 信息形态不足与 yaw-block 外推协议过强。据此本工作把主线从"single-frame yaw-block 胜负"复位到 model-known simulated 条件下跨几何多观测的可观测性、互补性与置信一致性。

- paragraph_id：R0
- claim_ids：C1.1, C1.2, C1.3（对应骨架 Claim 1.1/1.2/1.3）
- evidence paths：`10_b6_circular_regression_fix01/b6_foldmatched_vs_p1a_best.csv`、`b6_yawblock_stratified_best.csv`；`01_成果区/.../00_...收口说明_R113通过.md`、`01_...执行框架_R113通过.md`
- linked figures/tables：SI-1
- allowed wording：条件性负结果；exact-bin 过严；判据非主因（已测 single-frame 判据轴）；主线复位。
- forbidden wording：光度无用；yaw 物理不可观测；图像无姿态信息；训练头修复即可解决 yaw 外推；路线一 C 整体失败。
- risk tag：low

---

## R1 — clean/P-INT 多几何 OCS 可观测性

**草案段落：**
在 model-known、fixed-roll、clean、P-INT、总光度向量输入条件下，OCS-only 多观测总光度向量随观测几何数 L1-G1→L1-G3→L1-G5 呈单调增益：yaw circular MAE 由 76.56° 降至 38.22° 与 22.77°，yaw hit@30 由 0.277 升至 0.672 与 0.811。几何组严格嵌套（L1-G1 ⊂ L1-G3 ⊂ L1-G5），即增加观测几何单调增加可用姿态信息。需要说明的是，clean P-INT 上界下 image_only 已近饱和，joint 增益受天花板限制，本阶段不主张强互补性。以上为 seed=42 单次 run 结果，正式主结果前建议多 seed/fold 复算。

- paragraph_id：R1
- claim_ids：C2.1, C2.2
- evidence paths：`11_l1m2_multigeometry_ocs/l1m2_pint_vs_pext_ocs_only.csv`、`l1m2_metrics_summary_best.csv`、`l1m2_complementarity_summary.csv`、`figures/l1m2_gain_curve_best.png`
- linked figures/tables：Fig.2；main_figure_source_map W1
- allowed wording：跨几何多观测总光度向量提升姿态可观测性；加几何=单调加信息；clean 上界下 image_only 近饱和。
- forbidden wording：真实反演成功；所有协议成立；operational-ready；joint 强互补性已证明。
- risk tag：low

---

## R2 — degraded 真实性轴与 M-roll fixed-roll 边界

**草案段落：**
OCS-only 多几何单调增益并非 clean-only 假象：在物理退化（PSF/高斯模糊、Poisson shot noise、read noise、背景与梯度、降采样、测光误差）下增益保持，并随退化强度优雅收缩（L1-G5 yaw cMAE clean/mild/moderate = 22.77 / 27.83 / 38.46°）。审计缺口已补齐：val samples 恢复后 cmae_delta=0.0，跨五个几何 pixel area/ortho scale/depth epsilon/resolution 一致，flux transform 仅由 train 拟合、train/val/test 无 attitude 泄漏，几何嵌套对齐。对 roll 敏感性，fixed-roll 结论在 ±15° roll 量级扰动（image_only zero-shot）下未被直接推翻，±30° 明显敏感（L1-G5 yaw cMAE 0°/±15°/±30° = 8.68 / 17.5–19.7 / 33.0–28.7°）。M-roll 仅为 fixed-roll 边界探针，不构成 roll-aware 能力或三轴姿态反演。

- paragraph_id：R2
- claim_ids：C3.1, C3.2, C3.3
- evidence paths：`12_l1m3_degraded_mroll/degraded/l1m3_degraded_metrics_summary_best.csv`、`degraded/l1m3_degraded_gain_and_drop_summary.md`、`mroll/mroll_metrics_summary_best.csv`、`audit/l1m2_val_samples_recovery_summary.csv`、`audit/l1m2_geometry_scale_consistency.csv`、`audit/l1m2_transform_leakage_check.json`
- linked figures/tables：Fig.3；SI-3
- allowed wording：增益非 clean-only 假象；物理退化下保持并优雅收缩；量纲一致性核验通过；无 inverse-crime 泄漏；fixed-roll 边界探针；±15° 未直接推翻、±30° 敏感。
- forbidden wording：真实观测验证；真实系统鲁棒性完成；severe 退化已验证；roll-aware 能力；三轴姿态反演；M-roll 替代三轴小项目。
- risk tag：low

---

## R3 — P-DB / conformal 可检索信息与置信一致性

**草案段落：**
作为非神经证据，P-DB（model-known simulated template retrieval）证明 L1 多观测总光度向量含可检索的 yaw 信息：top1 yaw hit@30 随 L1-G1→L1-G3→L1-G5 单调上升（clean = 0.291 / 0.821 / 0.949），并随退化优雅下降（moderate L1-G5 = 0.780）。P-DB 检索强于 neural ocs_only 回归（clean L1-G5 cMAE 8.19° vs 22.77°），二者误差近不相关（Spearman≈0），构成互补证据链（clean L1-G5 四象限 both-correct/neural-only/P-DB-only/both-wrong = 237/3/44/12，oracle hit@30=0.960）；这说明当前神经回归未充分吸收光度信息，而 oracle 仅为上界，不代表可无监督选中正确一方。置信一致性方面，conformal set_size 随几何收紧（ocs_only clean α=0.10 set_size L1-G1/G3/G5 = 321.8 / 245.7 / 126.2°），coverage 近 target=0.90，与多观测信息量增益一致；此处为当前 simulated split 下的集合宽度/校准结果，非 Bayesian posterior 或最终概率校准。

- paragraph_id：R3
- claim_ids：C4.1, C4.2, C4.3
- evidence paths：`13_l1d3_confidence_pdb/pdb/l1d3_pdb_retrieval_summary.csv`、`consistency/l1d3_error_correlation_summary.csv`、`consistency/l1d3_complementarity_cases.csv`、`conformal/l1d3_conformal_summary.csv`、`figures/pdb_gain_curve.png`、`figures/complementarity_quadrants.png`、`figures/risk_coverage_curves.png`
- linked figures/tables：Fig.4；Fig.5；SI-x1
- allowed wording：多观测总光度向量含可检索 yaw 信息；simulated template retrieval；P-DB 与 neural 互补；oracle 为上界；set_size 随几何收紧；当前 simulated split 下校准自洽。
- forbidden wording：真实观测反演成功率；真实望远镜验证；无监督可选中正确一方；两通道融合已实现；Bayesian posterior；最终概率校准完成；真实天文观测不确定度。
- risk tag：**medium**（P-DB / conformal 措辞最易被过度解读，必须持续加 simulated / template retrieval / current split 限定）

---

## R4 — Negative observations and limitations

**草案段落：**
以下负向观察必须保留、不得淡化。其一，P-EXT yaw-block strict extrapolation 下 OCS-only 仍坍缩（三几何 cMAE≈146–157°），说明多观测提升的是内插可观测性而非整段外推。其二，clean P-INT 下 image/joint 存在天花板效应，且 degraded final 口径出现检查点选择敏感（L1-G5 joint moderate hit@30=0.189），故 joint 强互补性未显现。其三，neural margin 的 risk–coverage 曲线近平坦（置信区分度弱），image_only conformal 略欠覆盖（clean α=0.10 复算 coverage≈0.83–0.89，L1-G5 最低 0.835 < 0.90；叙事骨架记为≈0.83-0.85），故选择性预测尚不能宣称强可用。其四，image_only 在部分分析维欠覆盖（image-hard 仅 2 行），joint 未展示对 image_only 的稳定增量，需留待 P-INT-hard / degraded-severe 检验。

- paragraph_id：R4
- claim_ids：C5.1, C5.2, C5.3, C5.4
- evidence paths：`11_l1m2.../l1m2_pint_vs_pext_ocs_only.csv`、`l1m2_complementarity_summary.csv`；`12_l1m3.../degraded/l1m3_degraded_metrics_summary_final.csv`；`13_l1d3.../consistency/l1d3_risk_coverage.csv`、`conformal/l1d3_conformal_summary.csv`、`hardcases/l1d3_hardcase_index.csv`
- linked figures/tables：Fig.5(b)；SI-2；SI-x2
- allowed wording：P-EXT 仍是过强外推 stress test；joint 强互补性未显现；检查点选择敏感；置信区分度弱；image_only 欠覆盖。
- forbidden wording：P-EXT yaw-block 已解决；joint 强互补性已证明；选择性预测强可用；image/joint 已充分覆盖。
- risk tag：low（限定明确，但删去任一负向观察即升为 high 误读风险）

---

## R5 — Remaining gaps and next-stage options

**草案段落：**
以下为未解决/未启动项，仅作 future work 备案。degraded-severe 与 P-INT-hard 尚未评估，hard-case index（1231 行，disagreement-hard 748 / robust-easy 351 / ambiguous-flux 148 / ocs-hard 121 / image-hard 2）已备为候选输入，但不构成阶段门放行。真实 GEO 数据仅可作 sim-to-real 光度趋势/分布/多帧几何锚点，无三轴姿态真值，不能写成监督反演数据集。三轴小项目未启动，M-roll 仅 fixed-roll 边界探针，不替代三轴。上述扩展均需另行 Codex 阶段门。

- paragraph_id：R5
- claim_ids：C6.1, C6.2, C6.3
- evidence paths：`13_l1d3.../hardcases/l1d3_hardcase_index.csv`、`l1d3_recommended_pinthard_design.md`；`01_成果区/.../01_...执行框架_R113通过.md`（第6/7节）
- linked figures/tables：SI-4
- allowed wording：degraded-severe / P-INT-hard 为候选下一步；hard-case index 为候选输入；GEO 只可作光度锚点；三轴小项目为后续桥接层、本阶段未启动。
- forbidden wording：已启动新训练；阶段门已放行；GEO 有三轴姿态真值；真实 GEO 反演成功率；三轴小项目已启动/完成。
- risk tag：low

---

## 草案自检

- 结构覆盖 R122 第 5 节建议的 6 段（R0–R5），每段绑定 paragraph_id / claim_ids / evidence paths / linked figures / allowed / forbidden / risk tag。
- 未新增 R121 以外的 claim；未写 Abstract / Introduction / Discussion 全文；未写投稿语气或 "we demonstrate a real-world system"。
- 所有强结论均带 model-known simulated / clean P-INT / current split / template retrieval 限定。
- 负向观察（R4）独立成段且不淡化；R3 标为 medium 风险。
