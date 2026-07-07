# P4-PHYS-D 下一步建议

## 裁决标签
**SUNVIEW_DEPENDENT_BUT_MECHANISTIC**

## 依据
- 最亮姿态随 sun/view ±7° 迁移（baseline top-1 退居 rank 4–7），但每个几何的最亮点都落在 top-1 roll 邻域簇（D5_roll125 / D6_roll175），且金属主导（metal% ~95）、金属近镜面分级对齐。
- 严格二值 near_specular_metal 因 baseline 定制阈值在 ±7° 下多翻 0，但连续机制量（metal 主导、pct_NoH≥0.99 ~80%、最亮点 avgN_vs_H ~2°）表明机制稳定、只是最优对齐姿态平移。
- R4 各几何仍同机制高亮；R3 各几何仍非近镜面负对照。

## 建议（供 Codex 裁决，非自行放行）
1. 若继续三轴小项目：设计**受控 sun/view 搜索**（在 top-1 roll 邻域簇附近，对 sun/view 做更密网格），定位每个几何的局部最亮姿态并验证是否始终落在该簇。
2. 若要写 material-level 结论：单独补 material pass（本轮仍 B0 proxy）。
3. 收口选项：也可将本轮结论（机制稳定 + 姿态随几何平移）作为三轴小项目"最亮构型对 sun/view 的敏感性"小节直接收口，不再扩大。
4. 不建议：全 sun/view 全局最亮搜索、训练、R128、路线二/三/四扩展——均超出本阶段门。