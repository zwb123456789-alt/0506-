# P4-PHYS-E sun/view 3×3 组合小网格结果

几何：9 个（sun_offset ∈ {-7,0,+7} × view_offset ∈ {-7,0,+7}，角距 baseline 各 7.0°）。
姿态：14 个（复用 26 包同源 14 候选，无新姿态搜索）。
组合：9×14=126，全部 COMPLETE；0 新增渲染（camera EXR←view_offset，sun EXR←sun_offset，均复用 26/baseline）。
5 个可锚点组合（H00/pure sun/pure view）与 26 包 G0–G4 逐姿态 OCS 精确一致（70/70，max rel_diff=0）。

## 1. 逐几何最亮点
- Hsp_vm (sun+7,view-7): 最亮=C_R3（R3_negative, cluster=control），OCS=0.22556，metal%=99.51，nsm=0
- Hsp_v0 (sun+7,view+0): 最亮=D5_roll125（top1_neighbor_roll125, cluster=primary_shift_target），OCS=0.19528，metal%=94.66，nsm=0
- Hsp_vp (sun+7,view+7): 最亮=A_top1（top1, cluster=core_top1_roll_neighborhood），OCS=0.21040，metal%=95.09，nsm=1
- Hs0_vm (sun+0,view-7): 最亮=D5_roll125（top1_neighbor_roll125, cluster=primary_shift_target），OCS=0.18549，metal%=94.64，nsm=0
- H00_baseline (sun+0,view+0): 最亮=A_top1（top1, cluster=core_top1_roll_neighborhood），OCS=0.20889，metal%=95.02，nsm=1
- Hs0_vp (sun+0,view+7): 最亮=D6_roll175（top1_neighbor_roll175, cluster=primary_shift_target），OCS=0.20492，metal%=94.86，nsm=1
- Hsm_vm (sun-7,view-7): 最亮=D2（top1_neighbor, cluster=core_top1_roll_neighborhood），OCS=0.20011，metal%=95.04，nsm=1
- Hsm_v0 (sun-7,view+0): 最亮=D6_roll175（top1_neighbor_roll175, cluster=primary_shift_target），OCS=0.19493，metal%=94.78，nsm=0
- Hsm_vp (sun-7,view+7): 最亮=D6_roll175（top1_neighbor_roll175, cluster=primary_shift_target），OCS=0.14992，metal%=93.20，nsm=0

## 2. 全 126 组合最高 OCS，baseline A_top1 是否仍最高
- **全表最高 = Hsp_vm / C_R3（R3_negative），OCS=0.22556**，cluster=control，nsm=0，metal%=99.51。
- baseline A_top1 OCS=0.20889；全表最高 **超过** baseline A_top1。
- 全表最高点位于 3×3 **角落**几何 Hsp_vm（sun 与 view 同时扰动），**不是** baseline A_top1，也不是 top-1 roll 邻域簇成员。

## 3. 逐几何最亮点是否都落在 top-1 roll 邻域簇
- 9 个几何中 **8/9** 的逐几何最亮点落在 top-1 roll 邻域簇。
  - H00_baseline: A_top1 → core_top1_roll_neighborhood ✓
  - Hsp_v0: D5_roll125 → primary_shift_target ✓
  - Hsm_v0: D6_roll175 → primary_shift_target ✓
  - Hs0_vp: D6_roll175 → primary_shift_target ✓
  - Hs0_vm: D5_roll125 → primary_shift_target ✓
  - Hsp_vp: A_top1 → core_top1_roll_neighborhood ✓
  - Hsp_vm: C_R3 → control ✗ (脱簇)
  - Hsm_vp: D6_roll175 → primary_shift_target ✓
  - Hsm_vm: D2 → core_top1_roll_neighborhood ✓
- **例外：Hsp_vm（sun+7,view-7）最亮点是 C_R3（负对照），脱离 top-1 roll 邻域簇**，且恰为全表最高 OCS。这是纯 sun / 纯 view 扰动（26 包）未暴露的组合角落效应。

## 4. D5/D6 是否继续承担迁移目标
- D5_roll125 / D6_roll175 在 5 个几何承担逐几何最亮（Hsp_v0,Hsm_v0,Hs0_vp,Hs0_vm,Hsm_vp），主要是 pure sun / pure view 边（与 26 包一致）。
- 但在组合角落（Hsp_vp/Hsm_vm 由 A_top1/D2 领先；Hsp_vm 由 R3 领先），D5/D6 不再普遍是最亮点，迁移目标本身随组合几何变化。

## 5. R4/R3 对照
- R4：各几何 OCS 0.10–0.20、metal% 97–99，始终金属主导；在 pure-shift 与 (sun+7,view+7)/(sun-7,view-7) 对角仍高，但在 (sun+7,view-7)/(sun-7,view+7) 反对角明显掉到 ~0.10。R4 不再稳定是同机制高亮对照。
- **R3：不再是稳定负对照。** R3 OCS 随组合几何在 0.03296–0.22556 间大幅摆动，在 Hsp_vm 升到 0.22556（全表最高）。R3 各几何 nsm=0（非近镜面），说明该角落的高亮不是近镜面对齐机制，而是 R3 大面元在该 sun+view 组合下进入高 NoL·NoV 且金属主导的漫/宽瓣区间。

## 6. 严格 near_specular_metal 与连续机制量
- 全 126 组合 dominant_part 均为金属主体（metal% 87.6–99.5），金属主导稳定。
- 严格二值 near_specular_metal=1 仅 29/126：集中在 baseline 与两条同号对角（sun+view 同侧）附近；反对角组合（sun 与 view 反向）把 H 推离所有采样姿态法向，nsm 全 0。
- 因此金属近镜面对齐仍是**部分组合**（同号扰动）的连续机制解释，但在**反号组合角落**，最亮点由非近镜面的金属漫/宽瓣主导，沿用 R154 限定：机制为连续量意义下的金属主导，不得写成严格 near_specular_metal 在所有 sun/view 组合稳定。

## 7. 裁决标签
**NEED_LOCAL_STEP_REFINEMENT**：3×3 组合网格内全表最高点出现在**角落几何**（sun+7,view-7），且由**负对照 R3** 领先、脱离 top-1 roll 邻域簇；采样的 14 个固定姿态未覆盖组合角落的真实最亮姿态。需在组合角落附近做更小步长 / 中心平移的局部 refinement，并重新评估 R3 在组合几何下是否仍能作为负对照。