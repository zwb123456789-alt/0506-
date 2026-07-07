# 路线一 C 主图图注草案（main_figure_captions_draft）

最后更新：2026-07-01
来源任务：R122 子任务 A
状态：**图注草案**，供 Codex/作者润色；非最终论文正文。所有结论限定 model-known simulated。

术语统一：实验层 L1-G1 / L1-G3 / L1-G5（代码层 OBS_GEOMETRIES G0~G4 仅方法附录/registry 出现）。

---

## Fig.1 — 任务与协议示意图

**Caption（草案）：** Model-known simulated multi-view observability protocol. 在已知三维目标（几何与材料已知）上，按嵌套多几何 sun/view 采样（L1-G1 ⊂ L1-G3 ⊂ L1-G5）经共享物理前向模型（Blender-derived）生成两条通道：OCS 通道给出跨几何总光度向量，图像通道给出单视角渲染图像。下游分析协议包括 P-INT 内插 / P-EXT yaw-block 外推（可观测性）、P-DB simulated template retrieval（非神经证据）、neural 回归（ocs_only / image_only / joint）与 conformal set-size（当前 split 校准）。

**限定语（必带）：** simulated only；no real telescope；no real GEO attitude truth。
**allowed：** 仅示意 model-known simulated 数据流与协议关系。
**forbidden：** 不画真实望远镜验证 / 真实 GEO 反演 / 三轴姿态真值链路。
**source：** `11_l1m2_multigeometry_ocs/l1m2_geometry_registry.json`；24 号主线定义。

---

## Fig.2 — clean/P-INT OCS-only 多几何单调增益

**Caption（草案）：** clean / P-INT 条件下 OCS-only 多观测总光度向量随几何数单调增益（seed=42）。(a) yaw circular MAE 从 L1-G1 的 76.56° 降至 L1-G3 的 38.22°、L1-G5 的 22.77°；(b) yaw hit@30 从 0.277 升至 0.672、0.811。几何组严格嵌套（L1-G1 ⊂ L1-G3 ⊂ L1-G5），增加观测几何即单调增加姿态信息。

**限定语：** model-known simulated；clean / P-INT；seed=42 单次 run（主结果前建议多 seed/fold）。
**allowed：** OCS-only cMAE/hit@30 随几何数单调改善。
**forbidden：** 不标注为真实反演精度 / 所有协议成立 / operational-ready。
**source：** `11_l1m2_multigeometry_ocs/l1m2_pint_vs_pext_ocs_only.csv`（P-INT 行）。

---

## Fig.3 — degraded 真实性轴 OCS-only 增益保持与优雅收缩

**Caption（草案）：** OCS-only 多几何单调增益在物理退化（PSF/高斯模糊、Poisson shot noise、read noise、背景与梯度、降采样、测光误差）下保持，并随退化强度优雅收缩。三条曲线为 clean / degraded-mild / degraded-moderate 下 L1-G1→L1-G3→L1-G5 的 yaw cMAE；L1-G5 由 clean 22.77° 收缩至 mild 27.83°、moderate 38.46°，几何单调性在各退化等级下均保持。

**限定语：** model-known simulated；物理合理退化（非 B6 粗增广包）；best 口径。
**allowed：** 增益非 clean-only 假象；物理退化下保持并优雅收缩。
**forbidden：** 不写真实观测验证 / 真实系统鲁棒性完成 / severe 退化已验证。
**source：** `11_l1m2.../l1m2_pint_vs_pext_ocs_only.csv` + `12_l1m3.../degraded/l1m3_degraded_metrics_summary_best.csv`。

---

## Fig.4 — P-DB 检索 vs neural 回归与互补四象限

**Caption（草案）：** P-DB simulated template retrieval 与 neural ocs_only 回归互补（clean，test split）。(a) P-DB top1 yaw hit@30 随几何数单调上升（L1-G1/G3/G5 = 0.291 / 0.821 / 0.949），全面高于 neural ocs_only。(b) clean L1-G5 互补四象限（n=296）：both-correct=237、neural-only=3、P-DB-only=44、both-wrong=12；oracle hit@30=0.960 为上界，neural 与 P-DB 误差近不相关（Spearman≈0）。P-DB 检索强于 neural 回归，说明当前神经回归未充分吸收光度信息。

**限定语：** model-known simulated template retrieval；oracle 为上界，不代表可无监督选中正确一方。
**allowed：** P-DB 与 neural 互补；神经回归未充分利用光度信息。
**forbidden：** 不写真实观测反演成功率 / 真实望远镜验证 / 无监督可选中正确一方 / 两通道融合已实现。
**source：** `13_l1d3.../pdb/l1d3_pdb_retrieval_summary.csv` + `consistency/l1d3_error_correlation_summary.csv` + `consistency/l1d3_complementarity_cases.csv`。

---

## Fig.5 — conformal set_size 随几何收紧 + 负向观察摘要

**Caption（草案）：** 置信一致性。(a) OCS-only conformal set size（α=0.10）随几何数收紧：L1-G1/G3/G5 = 321.8° / 245.7° / 126.2°，coverage 近 target=0.90（当前 simulated split）。(b) 必须保留的负向观察：image_only conformal 略欠覆盖（clean α=0.10 复算 coverage≈0.83–0.89 < 0.90；叙事骨架记为≈0.83-0.85）、neural margin risk–coverage 近平坦（置信区分度弱）、P-EXT yaw-block 仍坍缩（≈146–157°）、joint 增益受天花板限制且 final 口径检查点敏感（G5 joint moderate hit@30=0.189）、oracle 仅为上界。

**限定语：** 当前 simulated split 下；conformal 非 Bayesian posterior、非最终概率校准。
**allowed：** set_size 随几何收紧；当前 split 下校准自洽。
**forbidden：** 不写 Bayesian posterior / 最终概率校准完成 / 真实天文观测不确定度；image_only 欠覆盖须标注。
**source：** `13_l1d3.../conformal/l1d3_conformal_summary.csv`。

---

## 图注自检

- 五张主图图注均绑定 source path、key numbers、allowed/forbidden，与 claim 边界表 W1–W5 及叙事骨架一致。
- 全部限定语覆盖 model-known simulated / clean P-INT / current split / template retrieval。
- 负向观察在 Fig.4/Fig.5 图注中显式保留，未淡化。
