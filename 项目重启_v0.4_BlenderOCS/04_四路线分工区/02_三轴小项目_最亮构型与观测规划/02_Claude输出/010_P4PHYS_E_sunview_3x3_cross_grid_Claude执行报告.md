# 010 P4-PHYS-E sun/view 3×3 组合小网格补齐 Claude 执行报告

任务依据：R155 任务单（P4-PHYS-E sun/view 3×3 组合小网格补齐）
上游：R154 接收 009/26 包，P4-PHYS-D 裁定 `SUNVIEW_DEPENDENT_BUT_MECHANISTIC`
执行日期：2026-07-06
输出包：`v0.4_results/27_three_axis_p4phys_e_sunview_3x3_cross_grid/`

---

## 0. 一句话结论

在 phase63/L1-G1 baseline 邻域做 `sun_offset∈{-7,0,+7} × view_offset∈{-7,0,+7}` 的 3×3 组合小网格（9 几何 × 14 姿态 = 126 组合，**0 新增渲染**），发现：**全 126 组合的最高 OCS 出现在组合角落几何 `Hsp_vm`(sun+7,view-7)、且由负对照 `C_R3` 领先（OCS=0.22556 > baseline A_top1 0.20889），脱离 top-1 roll 邻域簇、nsm=0**。逐几何最亮点 8/9 仍落在 top-1 roll 邻域簇，但组合反对角打破该规律，R4/R3 对照在反对角失稳。裁决 **NEED_LOCAL_STEP_REFINEMENT**。material 层仍为 B0 proxy。

## 1. 3×3 组合几何如何构造和复用 EXR

- 9 个组合几何 = `sun_offset∈{-7,0,+7}` × `view_offset∈{-7,0,+7}`（`audit/sunview_3x3_geometry_manifest.csv`），命名 H00_baseline / Hsp_v0 / Hsm_v0 / Hs0_vp / Hs0_vm / Hsp_vp / Hsp_vm / Hsm_vp / Hsm_vm。sun/view 方向向量与角距（各 7°）直接 import 26 包 config，同源无漂移。
- **复用原理（物理精确）**：camera 几何 pass（Normal/Depth/IndexOB/Position）与太阳无关 → camera EXR 只由 view_offset 决定；sun 几何 pass 与探测器无关 → sun EXR 只由 sun_offset 决定。因此：
  - camera EXR：view0 复用 baseline camera；view+7 复用 26/G3_view_plus；view-7 复用 26/G4_view_minus。
  - sun EXR：sun0 复用 baseline sun；sun+7 复用 26/G1_sun_plus；sun-7 复用 26/G2_sun_minus。
- 9 组合中 5 个（H00 / pure sun±7 / pure view±7）与 26 包 G0–G4 一一对应，作为数值锚点；4 个角落（sun±7 & view±7 同时扰动）是 26 已有 sun/camera EXR 的新组合。

## 2. 是否 0 新增渲染，后处理是否 126/126 complete

- **0 新增渲染**（`audit/reuse_exr_manifest.csv`、`redline_precheck.csv`）：252 个 EXR 引用全部复用（baseline 84 + 26 包 168），新增渲染=0，全部 EXR 可达。
- 后处理 **126/126 COMPLETE**（`tables/p4physE_metrics.csv`、`audit/postprocess_status.csv`）。
- **锚点一致性**：5 个可锚点组合共 70 个姿态-锚点与 26 包 G0–G4 的 ocs.json **精确一致，70/70 OK，max rel_diff = 0**（复用同一 EXR 对 + 同一官方后处理口径）。
- 机制重算逐像素 OCS vs metrics 一致性 126/126 OK，max rel_diff=1.44e-7（`audit/numeric_consistency_check.csv`），复用 24/25/26 机制签名口径、H 随组合几何取值。

## 3. 全表最高 OCS 与逐几何 top 候选

**全表最高（`tables/p4physE_top_candidate_summary.csv`）：`Hsp_vm`(sun+7,view-7) / `C_R3`，OCS=0.22556，cluster=control，nsm=0，metal%=99.5** —— 超过 baseline A_top1（0.20889），位于 3×3 **角落**。

逐几何最亮点（sun 行 × view 列，见 `figures/p4physE_ocs_3x3_heatmap.png`）：

| 几何 | (sun,view) | 最亮 pose | OCS | nsm | cluster |
|---|---|---|---|---|---|
| H00_baseline | (0,0) | A_top1 | 0.20889 | 1 | core ✓ |
| Hsp_v0 | (+7,0) | D5_roll125 | 0.19528 | 0 | shift ✓ |
| Hsm_v0 | (-7,0) | D6_roll175 | 0.19493 | 0 | shift ✓ |
| Hs0_vp | (0,+7) | D6_roll175 | 0.20492 | 1 | shift ✓ |
| Hs0_vm | (0,-7) | D5_roll125 | 0.18549 | 0 | shift ✓ |
| Hsp_vp | (+7,+7) | A_top1 | 0.21040 | 1 | core ✓ |
| **Hsp_vm** | **(+7,-7)** | **C_R3** | **0.22556** | **0** | **control ✗** |
| Hsm_vp | (-7,+7) | D6_roll175 | 0.14992 | 0 | shift ✓ |
| Hsm_vm | (-7,-7) | D2 | 0.20011 | 1 | core ✓ |

逐几何最亮点 **8/9** 落在 top-1 roll 邻域簇；唯一例外是全表最高点 Hsp_vm→C_R3。

## 4. A_top1 / D5 / D6 / R4 / R3 的核心变化

- **A_top1**：仅在同号对角（H00、Hsp_vp）与其邻域是最亮/近最亮（0.208–0.210）；反对角 Hsp_vm 掉到 0.1004（`figures` 右图黑色格）。不再是组合网格的全局最亮姿态。
- **D5/D6**：在 pure-shift 边继续承担迁移目标（4 个几何），但在组合角落被 A_top1/D2/R3 取代，迁移目标本身随组合几何变化。
- **R4**：各几何金属主导（metal% 97–99），同号对角仍高（0.19–0.20），但反对角（Hsp_vm/Hsm_vp）掉到 ~0.10，nsm=0，**不再是稳定同机制高亮对照**。
- **R3**：OCS 随组合几何在 0.033–0.226 大幅摆动，在 Hsp_vm 成为全表最高（nsm=0，非近镜面）。**R3 不再是稳定负对照**；其高亮是 R3 大面元在该 sun+view 组合下进入高 NoL·NoV、金属主导的漫/宽瓣区间，而非近镜面对齐。

## 5. 机制连续量与 strict nsm 的关系

- 全 126 组合 dominant_part 均为金属主体，metal% 87.6–99.5，**金属主导稳定**。
- 严格二值 near_specular_metal=1 仅 **29/126**：集中在 baseline 与 sun/view 同号扰动（对角）附近；反号组合（sun 与 view 反向）把半程向量 H 推离所有采样姿态法向，nsm 全 0。
- 因此金属近镜面对齐仍是**部分组合（同号扰动）**的连续机制解释；但在**反号组合角落**，最亮点由非近镜面的金属漫/宽瓣主导。沿用 R154 限定：机制写为连续量意义下的金属主导，**不得写成严格 near_specular_metal 在所有 sun/view 组合稳定**。

## 6. 三类建议标签之一

裁决标签 **NEED_LOCAL_STEP_REFINEMENT**（`tables/p4physE_claim_boundary_table.csv`、`text/p4physE_next_step_recommendation.md`）。理由：3×3 组合网格内全表最高点出现在**角落几何**、由**负对照 R3** 领先、脱离 top-1 roll 邻域簇，采样的 14 个固定姿态未覆盖组合角落真实最亮姿态，不满足 READY_FOR_THREE_AXIS_CLOSURE_REVIEW 的"内部稳定"条件。建议（供 Codex 裁决，非自行放行）：

1. 在组合角落（尤其 sun+7,view-7 及邻域）做更小步长 / 中心平移的局部 sun/view + 姿态 refinement，定位角落真实最亮姿态。
2. 重新界定 R3 作为负对照的适用边界（只在 baseline 邻域几何成立，不能写成全 sun/view 负对照）。
3. material-level 结论仍需单独补 material pass（本轮仍 B0 proxy）。
4. 不建议：直接进入三轴小项目收口审阅、全 sun/view 全姿态搜索、训练、R128、路线二/三/四扩展。

## 7. 红线自查

`audit/redline_self_check.csv` 全 PASS：不训练、不 R128、不路线二/三/四、不做全 sun/view 全姿态搜索、**0 新增渲染**、不新增姿态候选、不改 20/21/23A/23B/24/25/26 源包、不写成果区/不改 CLAUDE.md/不生成 Codex 文件、结论限定 ±7° 3×3 组合小网格、material 仅 proxy 未写 material-level attribution。

---

## 附：产物清单（`audit/generated_files_manifest.csv`，27 包共 281 文件）

- scripts/（4）：p4physE_config、design_audit、postprocess、mechanism_analysis、finalize。
- audit/（9）：input/sunview_3x3_geometry/pose_candidate/reuse_exr/redline_precheck manifest、postprocess_status、numeric_consistency_check、redline_self_check、generated_files_manifest。
- tables/（7）：metrics、cross_geometry_rank_table、top_candidate_summary、top1_stability_table、mechanism_signature_by_geometry、claim_boundary_table、gate_matrix。
- figures/（4）：ocs_3x3_heatmap、top_pose_by_geometry（各 png+pdf）。
- text/（3）：sunview_3x3_result、next_step_recommendation、codex_review_checklist_for_010。
- logs/（1）：p4physE_postprocess.log。
- postprocess/（126 ocs.json + 126 v_sun_macro.npy），按 9 组合几何分目录。

验收：`tables/p4physE_gate_matrix.csv`（后处理 126/126、锚点一致性 70/70 max rel_diff=0、机制一致性 126/126 max rel_diff=1.4e-7、复用 24/25/26 口径、0 新增渲染、裁决标签给出均 PASS）。
