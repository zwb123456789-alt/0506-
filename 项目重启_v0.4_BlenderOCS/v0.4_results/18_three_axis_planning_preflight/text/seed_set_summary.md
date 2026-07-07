# 三轴搜索种子集摘要（seed_set_summary）

最后更新：2026-07-01
来源：`seeds/three_axis_seed_candidates.csv`（66 seed），R129 子任务 C。

## 1. 种子总量与类别覆盖

共 66 个种子，覆盖 9 类（建议全部类别）：

| 类别 | 数量 | 代表姿态 | 关键指标 | 风险标记 |
|---|---:|---|---|---|
| bright-seed | 8 | yaw145_pitch+015 | ocs_total=0.178 | glint/saturation-check |
| dark-seed | 8 | yaw285_pitch-070 | ocs_total=0.0106 | low-signal |
| high-info-seed | 8 | yaw240_pitch+030 | gain_g1→g5=179.2° | none |
| low-info-seed | 8 | yaw065_pitch+070 | cand_spread=86.5 | ambiguous |
| ocs-hard-seed | 8 | yaw065_pitch+075 | ocs_g5_err=171.8° | ocs-hard |
| image-hard-seed | 2 | yaw165_pitch-020 | image-hard(image_only) | image-hard |
| disagreement-seed | 8 | yaw250_pitch-010 | disagreement-hard | channel-conflict |
| roll-sensitive-seed | 8 | yaw285_pitch-085 | d(err30-err15)=131.2° | roll-sensitive |
| robust-easy-seed | 8 | yaw150_pitch+010 | ocs_total=0.175 | none |

## 2. 追溯性

- bright / dark：`01_fullrun/postprocess`（phase63 OCS，roll=0，2664 姿态）。
- high-info / ocs-hard：`16_route1c_closure_d2d4_m5/tables/d4_geometry_gain_by_attitude.csv`。
- low-info / image-hard / disagreement / robust-easy：`13_l1d3_confidence_pdb/hardcases/l1d3_hardcase_index.csv`
  + `consistency/l1d3_neural_pdb_joined_per_attitude.csv`。
- roll-sensitive：`17_route1c_postclosure_enhancement_sweep/mroll_full2664/`（G1 ocs_only, ±15/±30）。

全部满足强接收标准"能追溯到 16/17/13/12/11 号结果"。

## 3. 说明与边界

- image-hard-seed 仅 2 个：数据集中 image-hard(image_only) 标签本就极少（clean 全集约 3 条），
  这反映 clean/P-INT 下 image_only 近饱和的既有结论，不是提取遗漏。
- 种子姿态是三轴 roll 扫描的**起点**，不是最优反演姿态结论。
- 最亮姿态（bright-seed）与高信息姿态（high-info-seed）交集很小，
  实证 corr(亮度, gain)≈-0.09，印证 brightness ≠ information。

## 4. 可视化

- `figures/seed_map_fixedroll.png/.pdf`：yaw-pitch 平面上 9 类种子分布，底图为 OCS 亮度。
- `figures/brightness_vs_information.png/.pdf`：亮度-信息解耦散点。
