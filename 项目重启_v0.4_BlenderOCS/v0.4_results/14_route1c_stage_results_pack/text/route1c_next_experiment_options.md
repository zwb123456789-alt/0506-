# 路线一 C 待补实验与下一阶段建议表（route1c_next_experiment_options）

最后更新：2026-07-01  
来源任务：R120 Codex 任务单 `1C_stage_results_evidence_pack` 子任务 E  
配套 CSV：`route1c_next_experiment_options.csv`  
状态：候选建议表，**不自行放行任何选项**，仅供 Codex/作者裁决

基于 R119 hard-case index 与当前成果边界，列出四个下一阶段候选。每个选项含 goal / input data / needed new computation / expected cost / stage-gate metric / risk / what it enables / what it cannot claim。

---

## Option A：先整理论文 Results / SI，不立即新训练

- goal：把 R113/R115/R117/R119 固化为可审稿结果叙事与图表包。
- input data：本证据包 `14_route1c_stage_results_pack/` 全部；成果区 00/01/05/06/07；结果目录 10/11/12/13。
- needed new computation：无新训练；仅正式出图（Fig.2-5、SI-1 至 SI-5）、Results 正文起草、SI 组织。
- expected cost：低（制图 + 写作，数天）。
- stage-gate metric：Codex 审阅通过阶段性 Results 材料并可进成果区。
- risk：低；不引入新不确定性。
- what it enables：把当前四链固化为可审稿结果包。
- what it cannot claim：不能新增可观测性/互补性/鲁棒性结论；不闭口路线一 C。

## Option B：degraded-severe / P-INT-hard 小矩阵

- goal：用 hard-case index 选难例，检验 joint 相对 image_only 的增量。
- input data：`13_l1d3_confidence_pdb/hardcases/l1d3_hardcase_index.csv`（难例选取）；11/12 现有 split/geometry；`hardcases/l1d3_recommended_pinthard_design.md`。
- needed new computation：用 hard-case index 选难例；新训练 image_only/joint/ocs_only 于 P-INT-hard 或 degraded-severe；物理合理退化（不复用 B6 粗增广包）；保存 per-attitude/top-k/置信中间量。
- expected cost：中（新训练矩阵，约数天-一周；需 GPU）。
- stage-gate metric：joint 相对 image_only 在难例上是否有稳定增量；附多 seed/fold 稳健性。
- risk：中；结果可能仍为 joint 无稳定增量的负/弱结果。
- what it enables：回答 joint 互补性是否在更难协议显现；补强 D3 置信一致性。
- what it cannot claim：不能写成真实反演/真实鲁棒性；不能因单 seed 下结论。
- 备注：属 C 类主变量改动（新训练/split 变化），必须另行由 Codex 走完整阶段门放行，不做开放超参搜索。

## Option C：joint/full-2664 M-roll 子集扩展

- goal：只回答 fixed-roll 边界，不启动三轴。
- input data：`12_l1m3_degraded_mroll/mroll/` 现有探针；full-2664 姿态网格；G3 代表几何。
- needed new computation：扩展 M-roll 到 joint/full-2664 子集（roll∈{0,±15,±30}）；约 10-11h（R117 已估）。
- expected cost：中（约 10-11h 渲染 + 评估）。
- stage-gate metric：±15°/±30° 下 joint fixed-roll 边界是否与 image_only 一致。
- risk：中；可能仅确认已知边界，增量有限。
- what it enables：把 fixed-roll 边界从 image_only 探针扩展到 joint；明确 roll 敏感阈。
- what it cannot claim：不能启动三轴小项目；不能写成 roll-aware 反演能力。

## Option D：阶段性闭口前的 minimal sanity check

- goal：路线一 C 阶段性闭口前的最小一致性核验。
- input data：10/11/12/13 全部现有结果；各 metrics/split/registry。
- needed new computation：无新训练；仅跨阶段一致性复核（几何注册一致、split 无泄漏、数字与成果区一致、路径无失效）。
- expected cost：低（核验脚本，1-2 天）。
- stage-gate metric：四链数字/路径/口径完全自洽，无残余审计缺口。
- risk：低。
- what it enables：为后续任一正式闭口或投稿提供可复查基线。
- what it cannot claim：不构成路线一 C 整体闭口；不新增科学结论。

---

## 建议表自检

- 四个选项对应 R120 建议的 A/B/C/D，且每项均含 8 个必需字段。
- 未自行放行任何选项；Option B/C 明确标注为需 Codex 另行走阶段门的 C 类改动。
- 选项可直接改写成下一轮 Claude 任务单（尤其 Option A 与 Option B）。
