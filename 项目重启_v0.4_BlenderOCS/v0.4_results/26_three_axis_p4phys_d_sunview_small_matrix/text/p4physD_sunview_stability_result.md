# P4-PHYS-D sun/view 小矩阵稳定性结果

几何：5 个（G0 baseline + sun±7° + view±7°，角距 baseline 恰 7.0°）。
姿态：14 个（必选 top1/R4/R3 + top1 邻域 D + R4 同簇 E + bright-edge F）。

## 1. baseline top-1 在其它几何下是否仍高亮
- A_top1 在 baseline OCS=0.20889（rank 1）。在扰动几何下 rank 退居 7/4/4/6（G1/G2/G3/G4），OCS 降到 0.164–0.188。
- 即 A_top1 仍属高亮候选（始终 metal 主导、OCS 仍在候选前列），但不再是每个几何的最亮点。

## 2. 每个新几何下最高亮候选是谁，是否迁移
- G0_baseline: 最亮 = A_top1（top1），OCS=0.20889，metal%=95.02，near_specular_metal=1。
- G1_sun_plus: 最亮 = D5_roll125（top1_neighbor_roll125），OCS=0.19528，metal%=94.66，near_specular_metal=0。
- G2_sun_minus: 最亮 = D6_roll175（top1_neighbor_roll175），OCS=0.19493，metal%=94.78，near_specular_metal=0。
- G3_view_plus: 最亮 = D6_roll175（top1_neighbor_roll175），OCS=0.20492，metal%=94.86，near_specular_metal=1。
- G4_view_minus: 最亮 = D5_roll125（top1_neighbor_roll125），OCS=0.18549，metal%=94.64，near_specular_metal=0。

最亮点在 sun/view 变化下发生迁移，但迁移目标 100% 落在 top-1 roll 邻域簇（group={mandatory,top1_neighbor}），未跳到 R3/暗区。

## 3. 高亮候选是否仍满足 near_specular_metal
- 严格二值 `near_specular_metal`（25 包阈值 metal%≥80 且 avgN_vs_H≤2° 且 reflect_vs_det≤4°）在 ±7° 下大多翻为 0：因为阈值是 baseline 定制的，7° 扰动把 avgN_vs_H 推到 ~2.3–4.4°、reflect 推到 ~4–7.6°。
- 但连续量显示机制未消失而是**分级弱化**：全 70 个组合 dominant_part 均为金属主体（metal% 92.7–99.3），pct_NoH≥0.99 仍 ~80%，最亮点 avgN_vs_H 仍在 1.8–2.5° 量级。G3 最亮点 D6 仍严格 nsm=1。
- 结论：高亮仍由金属近镜面对齐解释，只是最优对齐姿态随 sun/view 平移。

## 4. R4 是否仍是同机制高亮对照
- G0_baseline: R4 OCS=0.20115 metal%=98.79 nsm=1
- G1_sun_plus: R4 OCS=0.17183 metal%=98.60 nsm=0
- G2_sun_minus: R4 OCS=0.16313 metal%=98.57 nsm=0
- G3_view_plus: R4 OCS=0.16895 metal%=98.55 nsm=0
- G4_view_minus: R4 OCS=0.16373 metal%=98.31 nsm=0
R4 在各几何下仍为金属主导高亮候选（OCS 0.16–0.20），与 top-1 簇同机制。

## 5. R3 是否仍保持负面对照
- G0_baseline: R3 OCS=0.06626 nsm=0
- G1_sun_plus: R3 OCS=0.13100 nsm=0
- G2_sun_minus: R3 OCS=0.03954 nsm=0
- G3_view_plus: R3 OCS=0.03979 nsm=0
- G4_view_minus: R3 OCS=0.13244 nsm=0
R3 在所有几何下 near_specular_metal=0；OCS 随几何波动（G1/G4 升到 ~0.13），但始终显著低于 top-1 簇最亮点，负面对照关系保持（非近镜面对齐）。

## 6. 隐身板增量是否随几何变化保持、减弱或消失
- G0_baseline: top-1 dark_pct=4.201%  R4 dark_pct=0.463%
- G1_sun_plus: top-1 dark_pct=5.078%  R4 dark_pct=0.536%
- G2_sun_minus: top-1 dark_pct=4.765%  R4 dark_pct=0.557%
- G3_view_plus: top-1 dark_pct=4.708%  R4 dark_pct=0.564%
- G4_view_minus: top-1 dark_pct=5.098%  R4 dark_pct=0.544%
隐身板增量仍是 top-1 簇（roll+15 附近）相对 R4（roll=0）的排序特征，随几何存在但幅度小；不构成普遍高亮机制，与 R152 PARTIAL_GENERALITY 一致。

## 7. 一句话
**SUNVIEW_DEPENDENT_BUT_MECHANISTIC**：最亮姿态随 sun/view 迁移，但迁移仍由金属主体近镜面对齐机制解释，最亮点始终落在 top-1 roll 邻域簇内。