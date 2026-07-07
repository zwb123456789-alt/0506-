# p4physF_result：Hsp_vm 角落局部加密结果（R157）

生成时间：2026-07-06 21:48

## 三个任务问题的回答

**Q1 固定 Hsp_vm 下 C_R3 附近是否存在更亮局部姿态峰？**
存在，且不止一个方向。3×3×3 网格中最高点为 yaw=35/pitch=75/roll=-20（OCS=0.27081），
超过 C_R3（0.22556）约 +20.1%，超过 A_top1 baseline（0.20889）约 +29.6%。
该点位于姿态网格三轴角落边界。roll=0 平面上 C_R3 邻域相对平坦
（y55/p45=0.22385、y55/p75=0.22570），真正的上升方向是 (yaw↓, pitch↑, roll↓)。

**Q2 Hsp_vm 周围极小 sun/view 邻域内最高点是否仍在边界？**
是。microgrid 全表最高为 sp5_vm7 / Stage1_best（OCS=0.27194），sun_offset=+5 位于
microgrid 边缘（朝 baseline 方向），几何边界亦未闭合。

**Q3 角落高亮是机制可解释还是链路失稳？**
机制可解释、链路可信：79 组合逐像素重算 vs ocs.json 一致性 79/79（max_rel=1.2e-07），
与 27 包 Hsp_vm 锚点 5/5 完全一致。最高点为金属主体主导（metal_pct=99.5%）的
**宽瓣/几何因子高亮**：weighted_NoL_NoV≈0.709（对照 C_R3≈0.707），
avgN_vs_H≈3.55°、reflect_vs_det≈7.11°——接近但不满足严格 near_specular_metal
阈值（2°/4°），nsm=0。按 R157 §7 应写作 metal wide-lobe / geometric-factor highlight，
不得写成严格近镜面对齐。

## 建议标签

**NEED_SECOND_STEP_REFINEMENT**（姿态与几何双边界未闭合；机制未断裂）。

## 停机规则视角的补充（供 Codex 落判参考，非裁决）

本轮是 P4-PHYS 系列第二次出现"加密后最高点仍在采样边界"（E 轮角落 → F 轮角落外侧）。
若按 016 号工作流建议 1 的停机规则（两轮加密仍出现新边界即触发 c 条款），
本任务已满足触发条件，可选择以
"**受控采样包络内局部最优 = sp5_vm7 / yaw35/pitch75/roll-20, OCS≈0.272，包络外未检验**"
的表述收口三轴小项目搜索轴，把 (yaw↓,pitch↑,roll↓,sun→baseline) 上升方向
作为明确边界写入结论。是否收口或再做一轮平移加密由 Codex/作者裁决。
