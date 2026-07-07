# P4-PHYS-C 机制判据定义

固定几何：phase63 / L1-G1，SUN=[1,0,0.3]、DET=[0.5,-1,0.1]（惯性系，全候选共用）。
候选池 n=159（20/21/23A/23B/01 去重后 geometry-eligible 分层采样）。

## 阈值标定来源（非 top-1 事后定制）

候选池分布（见 `tables/p4physC_geometry_signature_table.csv`）：

- `avgN_vs_H_deg`：p25=2.54°，median=11.4°，p75=21.2°。
- `reflect_vs_det_deg`：p25=4.63°，median=20.3°。
- `pct_NoH>=0.99`：median=0.74，p75=81.0（明显双峰，中间几乎无候选）。
- `metal_body_pct`：p25=66.2，median=94.1。
- `dark_panel_contrib`：median=0.00103，p75=0.00693，p90=0.00873。

阈值取在分布的自然断层（p25/p75 之间的空档），与 24 包 seed 一致，不是为使 top-1 单独通过而设。

## 三个判据

1. `near_specular_metal`：`metal_body_pct >= 80` 且 `avgN_vs_H_deg <= 2.0°` 且 `reflect_vs_det_deg <= 4.0°`。
   物理含义：金属主体主导 + 亮度加权代表法向近似半程向量 + 理想反射方向近似正对探测器。
2. `strong_surface_highlight`：`pct_NoH>=0.99 >= 50%` 或 `mean_NoH^80 >= 0.5`。
   物理含义：金属贡献像素中过半接近镜面峰，或整体镜面项均值高（面状近饱和）。
3. `dark_panel_increment`：`dark_panel_contrib >= 0.004` 或 `dark_panel_pct >= 2%`。
   物理含义：隐身板附加受照面提供可观增量。

判据为可解释 proxy，material 层仍为 B0 参数级 proxy（无 material pass）。
