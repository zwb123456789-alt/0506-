# 路线一 C 可复用资产索引（三轴小项目继承）

本文件由 `scripts/a_input_audit.py` 只读生成，供三轴小项目复用。

## OCS 亮度源（roll=0 fixed-roll 基线）

| 几何 | 姿态数 | 路径 |
|---|---:|---|
| phase63 (L1-G1) | 2664 | `01_fullrun/postprocess/` |
| phase24 | 2664 | `11_l1m2_multigeometry_ocs/postprocess/phase24/` |
| phase45 | 2664 | `11_l1m2_multigeometry_ocs/postprocess/phase45/` |
| phase90 | 2664 | `11_l1m2_multigeometry_ocs/postprocess/phase90/` |
| phase120 | 2664 | `11_l1m2_multigeometry_ocs/postprocess/phase120/` |

五何合计覆盖 L1-G5，全部 roll=0；三轴 roll 扩展需新渲染，本轮不执行。

## D4 可观测性地图（高信息/低信息接口）

- `16_.../tables/d4_geometry_gain_by_attitude.csv`：G1->G5 yaw err 增益，救回/变差区。
- `16_.../tables/d4_observability_region_stats.csv`：各通道 low/med/high err 分布。
- `16_.../tables/d4_confusion_regions.csv`：ambiguous-flux / pdb_near_but_wrong。
- `16_.../tables/d4_hardcase_region_cross_tab.csv`：yaw_quad×pitch_band×hardcase。

## 置信/检索/hardcase 指标源

- `13_.../hardcases/l1d3_hardcase_index.csv`：hardcase 标签（disagreement/ocs-hard/ambiguous-flux/robust-easy）。
- `13_.../pdb/l1d3_pdb_retrieval_per_query.csv`：nearest_distance/margin/topk10。
- `13_.../conformal/l1d3_conformal_per_sample.csv`：q_deg/covered。
- `13_.../consistency/l1d3_neural_pdb_joined_per_attitude.csv`：entropy/margin/通道一致性。

## roll 边界先验

- `17_.../mroll_full2664/`：±15°/±30° 预测，roll-sensitive 种子来源。
- `render_mroll_probe.py` 证明 Blender 渲染可参数化到 roll 轴（三轴渲染可行性依据）。
