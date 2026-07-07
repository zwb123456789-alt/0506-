# 009 P4-PHYS-D sun/view 小矩阵扩展阶段门 Claude 执行报告

任务依据：R153 任务单（P4-PHYS-D sun/view 小矩阵扩展阶段门）
上游：R152 接收 008/25 包，fixed phase63/L1-G1 机制普遍性为 PARTIAL_GENERALITY
执行日期：2026-07-06
输出包：`v0.4_results/26_three_axis_p4phys_d_sunview_small_matrix/`

---

## 0. 一句话结论

在 phase63/L1-G1 baseline 附近做 sun±7° / view±7° 小矩阵（5 几何 × 14 姿态），**最亮姿态随 sun/view 迁移**（baseline top-1 在扰动几何退居 rank 4–7），**但迁移目标 100% 落在 top-1 roll 邻域簇（D5_roll125 / D6_roll175），且全部金属主体主导（metal% 92.7–99.3）、金属近镜面分级对齐**。裁决 **SUNVIEW_DEPENDENT_BUT_MECHANISTIC**。material 层仍为 B0 proxy。

## 1. 本轮 sun/view 小矩阵如何设计

- 几何 5 个（`audit/sunview_geometry_manifest.csv`），均由 baseline 单位方向做 Rodrigues 旋转 ±7° 得到，角距 baseline **恰 7°**（5–10° 区间内）：
  - G0_baseline：SUN=[1,0,0.3], DET=[0.5,-1,0.1]（复用，不新渲染）
  - G1_sun_plus / G2_sun_minus：太阳方向绕世界 Y 轴 ±7°（sun_dir.y=0，轴与 sun 垂直）
  - G3_view_plus / G4_view_minus：探测器方向绕 (det×Z) 归一化轴 ±7°
  - 坐标口径：惯性系方向向量，渲染与后处理端统一 L2 归一化。
- 姿态 14 个（`audit/pose_candidate_manifest.csv`），**全部来自既有渲染，无新姿态搜索**：
  - 必选：A_top1(245/27.5/+15)、B_R4(147.5/12.5/0)、C_R3(55/60/0)
  - D top-1 邻域 6 个：D1–D4（pitch/yaw 邻点）+ D5_roll125 + D6_roll175（roll +12.5/+17.5）
  - E R4 同簇 2 个：R4 roll±15（near_specular_metal=1）
  - F bright-edge 3 个：25 包中 near_specular_metal=0 但 OCS 高的边缘点
- 规模：几何 5≤5，姿态 14≤16，新增渲染 56≤80（`audit/redline_precheck.csv` 全 PASS）。

## 2. 新增渲染规模是多少

**56 个渲染单元**（`tables/p4physD_render_manifest.csv`，全 OK）。利用几何 pass 光照无关的物理事实精确复用 baseline：
- 太阳扰动 G1/G2：camera 几何 pass（Normal/Depth/IndexOB/Position）与太阳无关 → 复用 baseline camera EXR，仅新渲 sun EXR（2 几何 × 14 = 28）。
- 探测器扰动 G3/G4：sun 几何 pass（太阳视角 Depth/Position）与探测器无关 → 复用 baseline sun EXR，仅新渲 camera EXR（2 几何 × 14 = 28）。
- G0 baseline：两视角全复用，0 新渲染。
- 正确性验证：G0 逐像素 OCS 复现既有 ocs.json，14/14 rel_diff≈0（`audit/render_postprocess_status.csv`、`audit/numeric_consistency_check.csv`）。

smoke 先行（G3_view_plus × top1/R4/R3，3/3 通过）再跑正式矩阵；后处理 70/70 COMPLETE。

## 3. top-1 在其它几何下是否仍亮

**仍是高亮候选，但不再是每几何最亮点。** A_top1 baseline OCS=0.20889（rank 1）；扰动几何 rank=7/4/4/6（G1/G2/G3/G4），OCS 降到 0.164–0.188（`tables/p4physD_top1_stability_table.csv`）。始终金属主导（metal% 93.9–95.0），仍属前列，但最优对齐姿态平移出去。

## 4. 最亮候选是否随几何迁移

**是，且迁移受控。** 各几何最亮点（`tables/p4physD_cross_geometry_rank_table.csv`）：

| 几何 | 最亮姿态 | role | OCS | metal% | nsm |
|---|---|---|---|---|---|
| G0_baseline | A_top1 | top1 | 0.20889 | 95.0 | 1 |
| G1_sun_plus | D5_roll125 | top1 邻域 | 0.19528 | 94.7 | 0 |
| G2_sun_minus | D6_roll175 | top1 邻域 | 0.19493 | 94.8 | 0 |
| G3_view_plus | D6_roll175 | top1 邻域 | 0.20492 | 94.9 | 1 |
| G4_view_minus | D5_roll125 | top1 邻域 | 0.18549 | 94.6 | 0 |

迁移目标 100% 落在 top-1 roll 邻域簇，未跳到 R3/暗区。

## 5. 金属近镜面机制是否仍解释高亮

**是，机制稳定，只是最优对齐姿态随 sun/view 平移。**
- 全 70 个 (几何,姿态) 组合 dominant_part 均为金属主体，metal% 92.7–99.3。
- 严格二值 `near_specular_metal`（25 包阈值 metal%≥80 且 avgN_vs_H≤2° 且 reflect_vs_det≤4°）在 ±7° 下多翻为 0——这是 **baseline 定制阈值的敏感性**，不是机制消失：7° 扰动把最亮点 avgN_vs_H 推到 ~1.8–2.5°、reflect 推到 ~4–4.4°，恰跨过阈值。连续量（pct_NoH≥0.99 仍 ~80%、mean_NoH^80 量级不变、metal 主导）表明机制**分级弱化**而非丢失；G3 最亮点 D6 仍严格 nsm=1（`figures/p4physD_mechanism_signature_shift.png` 显示各几何点沿近镜面带平移）。

## 6. R4/R3 对照是否保持

- **R4：保持同机制高亮。** 各几何 OCS 0.16–0.20、metal% 98.3–98.8，始终金属主导（`p4physD_top1_stability_table.csv`）。
- **R3：保持负面对照。** 各几何 near_specular_metal=0、rank 均为 14（最低）；OCS 随几何波动（G1/G4 升到 ~0.13）但始终显著低于 top-1 簇最亮点，非近镜面对齐关系保持。
- 隐身板增量：仍是 top-1 簇（roll+15 附近）相对 R4（roll=0）的排序特征（top-1 dark_contrib ~0.0084–0.0088 vs R4 ~0.0009），随几何存在但幅度小，不是普遍机制——与 R152 PARTIAL_GENERALITY 一致。

## 7. 是否建议小项目收口、扩大 sun/view，或补 material pass

裁决标签 **SUNVIEW_DEPENDENT_BUT_MECHANISTIC**（`tables/p4physD_claim_boundary_table.csv`、`text/p4physD_next_step_recommendation.md`）。建议（供 Codex 裁决，非自行放行）：
1. 若继续：设计受控 sun/view 搜索（top-1 roll 邻域簇附近加密 sun/view 网格），验证局部最亮点是否始终落该簇。
2. material-level 结论需单独补 material pass（本轮仍 B0 proxy）。
3. 收口选项：将"最亮构型对 sun/view 的敏感性（机制稳定 + 姿态平移）"作为三轴小项目一节直接收口。
4. 不建议：全 sun/view 全局搜索、训练、R128、路线二/三/四扩展。

---

## 附：产物清单（`audit/generated_files_manifest.csv`，26 包共 232 文件）

- scripts/（6）：p4physD_config、design_audit、render、postprocess、mechanism_analysis、finalize。
- audit/（9）：input/sunview_geometry/pose_candidate/render_plan/redline_precheck manifest、render_postprocess_status、numeric_consistency_check、redline_self_check、generated_files_manifest。
- tables/（8）：smoke_metrics、metrics、render_manifest、cross_geometry_rank_table、top1_stability_table、mechanism_signature_by_geometry、claim_boundary_table、gate_matrix。
- figures/（4）：ocs_by_geometry_pose、mechanism_signature_shift（各 png+pdf）。
- text/（3）：sunview_stability_result、next_step_recommendation、codex_review_checklist_for_009。
- logs/（4）：smoke_render、smoke_postprocess、render、postprocess。
- render/（56 EXR）、postprocess/（70 ocs.json + 70 v_sun_macro.npy），按 5 几何分目录。

验收：`tables/p4physD_gate_matrix.csv`（渲染 56/56、后处理 70/70、baseline OCS 复现、一致性 70/70 max rel_diff=1.4e-7、机制复用 24/25 口径均 PASS）。红线自检全 PASS（`audit/redline_self_check.csv`）：不训练、不 R128、不路线二三四、不全局 sun/view 全姿态搜索、新增渲染 56≤80、不改 20/21/23A/23B/24/25 源包、不写成果区/CLAUDE.md/Codex 文件、结论限定 ±7° 小矩阵、material 仅 proxy。
