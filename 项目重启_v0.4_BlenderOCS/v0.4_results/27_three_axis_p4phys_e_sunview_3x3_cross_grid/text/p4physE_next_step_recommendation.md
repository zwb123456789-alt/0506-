# P4-PHYS-E 下一步建议

## 裁决标签
**NEED_LOCAL_STEP_REFINEMENT**

## 依据
1. 全 126 组合最高 OCS 出现在 3×3 **角落几何** Hsp_vm（sun+7,view-7），OCS=0.22556，超过 baseline A_top1（0.20889）。最高点在网格边界/角落，不满足 READY_FOR_THREE_AXIS_CLOSURE_REVIEW 的“内部稳定”条件。
2. 该角落最亮点是**负对照 C_R3**，脱离 top-1 roll 邻域簇，且 nsm=0（非近镜面）。说明采样的 14 个固定姿态未覆盖组合角落的真实最亮姿态，且 R3 在组合几何下不再是可靠负对照。
3. 逐几何最亮点 8/9 落在 top-1 roll 邻域簇（pure-shift 与同号对角），但组合反对角（sun 与 view 反向）打破该规律。
4. 金属主导在全 126 组合稳定（metal% 87.6–99.5），但严格 near_specular_metal 只在同号扰动附近成立，不能写成全 sun/view 组合稳定。

## 具体建议（供 Codex 裁决，非自行放行）
1. 在组合角落（尤其 sun+7,view-7 及其邻域）做**更小步长 / 中心平移**的局部 sun/view + 姿态 refinement，定位组合角落真实最亮姿态，判断其是否仍金属主导、是否可归入某一连续机制。
2. 重新评估 R3 作为负对照的适用边界：R3 在 Hsp_vm 成为全表最高，需明确 R3 只在 baseline 邻域几何是负对照，不能写成全 sun/view 负对照。
3. material-level 结论仍需单独补 material pass（本轮仍 B0 proxy）。
4. 不建议：直接进入三轴小项目收口审阅（角落未收敛）、全 sun/view 全姿态搜索、训练、R128、路线二/三/四扩展。