# 018 术语映射表：内部名 → 论文名（持续维护，D 类四合一子任务 3）

生成时间：2026-07-06
性质：按 016 号工作流建议 8 建立的首版术语映射表。维护规则：每产生一个新内部概念，产生它的执行报告在文末登记一行；写作期与冷启动外审（016 号建议 3）投喂材料必须只使用"论文名"列。

## 核心口径与形态

| 内部名 | 论文名（英） | 一句定义 |
|---|---|---|
| OCS 口径 A | independent non-imaging photometric channel | 与图像不共享退化链路的独立积分光度通道 |
| OCS 口径 B | image-derived photometry | 从成像图像孔径测光导出的光度量（共模失效对照） |
| L1 / L1-G1/G3/G5 | multi-observation photometric vector (1/3/5 geometries) | 跨受控 sun/view 几何采样的总光通量向量 |
| F1 | single-epoch total-flux scalar | 单瞬时总光通量标量（信息下界基线） |
| F2 / 4维 per-part OCS | part-resolved photometric decomposition (semi-oracle) | 部件级光度分解，仅作诊断/上界，非现实输入 |
| L2 | time-domain light curve | 时域光变曲线（Future Work） |

## 协议与实验

| 内部名 | 论文名（英） | 一句定义 |
|---|---|---|
| P-INT | interpolation protocol | 姿态网格内插评估协议 |
| P-EXT / yaw-block | strict yaw-block extrapolation protocol | 严格 yaw 区块外推压力测试 |
| P-DB | template-retrieval baseline (model-known) | 模板检索对照（非神经、非真实反演成功率） |
| M-roll | roll-perturbation sensitivity probe | fixed-roll 结论对 roll 扰动的边界探针 |
| degraded mild/moderate/severe | graded image degradation protocol | 分级图像退化协议（仅作用图像通道） |
| exact-bin | exact-grid-cell accuracy (sentinel metric) | 精确网格命中率（哨兵指标，非主评价） |
| cMAE | circular mean absolute error | 角度环形平均绝对误差 |
| hit@30 | accuracy within 30 deg | 30° 容差命中率 |
| 头A / 头B | (历史归因线，论文中不出现) | 旧 single-frame 诊断与判据补救实验线 |
| B6-FIX01 | single-frame regression-head ablation | 单帧输出头/判据消融（负结果归因来源） |

## 三轴小项目与机制

| 内部名 | 论文名（英） | 一句定义 |
|---|---|---|
| 三轴小项目 | brightest-configuration search and light-path attribution | 三轴姿态+观测几何最亮构型搜索与光路归因（非反演） |
| top-1 / A_top1 | brightest sampled configuration (fixed geometry) | 固定几何下采样范围内最亮构型（yaw245/pitch27.5/roll+15） |
| 近镜面机制 / nsm | near-specular large-facet alignment mechanism | 金属大面元法向近对齐半程向量的高亮机制（阈值 2°/4°） |
| 宽瓣/几何因子高亮 | metal wide-lobe / geometric-factor highlight | 金属主导、NoL·NoV 几何因子高但不满足严格近镜面阈值的高亮（28 包新增） |
| 隐身板增量 / dpi | secondary illuminated-panel increment | top-1 相对鲁棒亮区的附加受照面小增量 |
| R4 / B_R4 | roll-robust bright reference configuration | roll 稳健高亮对照构型（yaw147.5/pitch12.5） |
| C_R3 | corner-geometry bright candidate (formerly negative control) | 原负对照，在组合几何角落变为高亮候选（27/28 包） |
| Hsp_vm | combined sun+7°/view−7° perturbed geometry | 太阳+7°、探测器−7° 同时扰动的组合观测几何 |
| PARTIAL_GENERALITY 等标签 | (论文中译为具体结论句，不用标签) | 阶段门裁决标签，仅内部流程使用 |
| B0 / B1 / GGX | engineering baseline BRDF / book-calibrated Phong-family BRDF / GGX contrast branch | 三个 BRDF 分支：工程基线 / 书中改进冯模型 / GGX 对照 |
| 23A/24/25/26/27/28…包 | SI Dataset S1, S2, …（另建对照表） | 结果包 → SI 数据集编号，写作期统一编号 |

## 数据与真实性

| 内部名 | 论文名（英） | 一句定义 |
|---|---|---|
| GEO 库 | attitude-truth-free GEO photometric survey database | 有光度/几何/型号/时序、无三轴姿态真值的真实监测库 |
| MAN 表 | maneuver-detection statistics table | 光度统计量异动检测表（事件级弱标签来源） |
| PRE 表 | orbit-prediction geometry table | 可反算每帧 sun/view 几何的预报表 |
| 接管边界 | information takeover boundary | 退化谱上图像信息消失、光度信息接管的位置（014/015 号新增） |
| model-known | non-cooperative but model-known target | 不合作但几何模型已知/近似已知的目标 |

## 登记区（新条目在此追加）

| 日期 | 内部名 | 论文名 | 来源报告 |
|---|---|---|---|
| 2026-07-06 | 宽瓣/几何因子高亮 | metal wide-lobe / geometric-factor highlight | 011_P4PHYS_F 报告 |
