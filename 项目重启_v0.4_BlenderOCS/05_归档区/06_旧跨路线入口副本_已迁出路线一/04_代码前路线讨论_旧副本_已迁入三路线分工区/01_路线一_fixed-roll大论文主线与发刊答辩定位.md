# 路线一：fixed-roll 大论文主线与发刊答辩定位

最后更新：2026-06-15

## 1. 文件性质

本文是 `03_代码前待决_roll轴与更多几何讨论记录.md` 之后形成的第一条候选路线记录。

本文不是最终方法冻结结论，也不修改 `13/14` 方法冻结文件。后续作者还会继续讨论其他路线，最终路线需在多路线比较后再决定是否同步到启动集、总控流程和代码阶段任务清单。

本路线针对**硕士学位论文**定位。后文对答辩委员容忍度的判断、roll 探针规模和工作量防线，均以硕士学位论文为前提；若改为博士论文，完整性要求与 roll 处理深度需重新评估。

## 2. 路线一一句话

```text
保留 fixed-roll yaw-pitch controlled benchmark 作为大论文与 v0.4 主线，
把 roll 明确写成边界与敏感性验证问题，
把多观测几何作为 OCS 可观测性、互补性和置信一致性的主变量，
不把本文声称为 full 3-DOF attitude inversion 或真实未知目标可部署反演系统。
```

## 3. 面向大论文的主线表述

建议大论文主线写为：

```text
面向几何已知或近似已知的非合作航天器，
建立统一的光学前向仿真与可审计 OCS 计算框架，
研究跨观测几何的积分光度向量与光学图像通道
在姿态可观测性、互补性和置信评估中的作用边界。
```

这一路线不把论文写成“任意未知目标完整姿态反演系统”，而是写成“统一物理前向模型下的观测信息结构研究”。

## 4. 与当前 v0.4 冻结主线的关系

路线一继承 24 号主线：

- OCS 采用 `independent photometric channel` 口径。
- OCS 主形态采用 `multi-observation photometric vector across controlled sun/view geometries`。
- 图像通道是空间分辨的 optical observation。
- 研究问题是 `what can be known / when complementary / when trustworthy`。
- 全链路重跑目的不是获得一张更好看的误差表，而是形成可审计证据链。

路线一新增的明确边界是：

```text
姿态标签仍采用 yaw-pitch fixed-roll 条件；
roll 不进入主实验全量 3-DOF 反演；
roll 作为敏感性、资源评估、limitations 和后续路线讨论处理。
```

## 5. 答辩可接受性判断

路线一可以支撑学术大论文，但必须主动建立三道防线。

### 5.1 roll 防线

必须承认当前主实验不是完整三轴姿态反演。

允许写：

```text
controlled yaw-pitch attitude estimation / observability benchmark under fixed roll
```

不允许写：

```text
full 3-DOF attitude inversion
real unknown target attitude recovery
field-ready non-cooperative target pose estimation
```

大论文中建议加入一节：

```text
roll sensitivity and 3-DOF extensibility discussion
```

该节至少回答：

1. 固定 roll 为什么是本轮可控基准的选择。
2. roll 加入后会如何改变采样空间、误差指标和 manifest。
3. 是否做小规模 roll sensitivity 或单姿态资源估计。
4. 为什么本文不把 full 3-DOF 作为已完成 claim。

答辩话术定调：不要把 `roll = 0` 写成“为简化问题而固定”（示弱），而要写成“显式固定的受控变量 + 已量化边界”。建议措辞为——“本文研究的是受控观测几何下的姿态信息可观测性；roll 作为一个受控自由度被显式固定，并通过敏感性分析量化了 roll 扰动对可观测性结论的影响边界，表明主结论在 roll 有界扰动下保持稳定。”这样把 roll=0 从“偷懒”翻译为“受控实验设计”，委员的追问即落空。

### 5.2 真实性防线

必须把本文定位为受控仿真与可审计前向模型研究，而不是真实外场验证。

答辩表述应强调：

- 使用统一前向模型消除 OCS 与 image 两条链路的口径混用。
- 使用 source data、manifest 和几何/BRDF/visibility 字段保证可审计。
- 使用 mismatch 分析说明材料、几何、观测链和真实定标仍是外推边界。

不应把 synthetic benchmark 的误差写成外场性能。

### 5.3 工作量防线

作为大论文，路线一不能只是一组训练结果。建议章节结构支撑为：

```text
第 1 章：研究背景与问题定义
第 2 章：空间目标光学散射、OCS 与姿态观测相关工作
第 3 章：统一光学前向模型与 Blender-derived OCS 计算框架
第 4 章：OCS 多观测光度向量的可观测性与信息量分析
第 5 章：图像通道、OCS 通道与融合/互补机制实验
第 6 章：置信一致性、mismatch、roll 与多几何边界分析
第 7 章：总结与后续 3-DOF / 真实锚点路线
```

这样可以把代码、物理建模、实验体系、指标体系和边界讨论组合成完整学位课题。

## 6. 发刊目标适配判断

路线一的发刊策略应是：

```text
高目标牵引写作质量；
证据强度决定最终档位；
投稿目标不能反向扩大 claim。
```

### 6.1 最高冲刺档

候选包括 Nature / Science / Nature 或 Science 子刊 / NSR / Science Bulletin / Engineering / PRL / Progress in Aerospace Sciences。

路线一目前不宜把这些作为真实默认主投，除非后续补出至少一种强支撑：

- 更普适的理论突破；
- 真实或半真实观测锚点；
- 面向领域的综述级或范式级贡献；
- 对航天器光学观测可观测性提出足够一般化的新问题框架。

对硕士学位论文阶段，建议不按最高冲刺档的 framing 组织写作。该档真正的门槛是 sim-to-real 真机锚点或普适理论突破，本轮明确不做；若按该档 framing 写作，易诱导 claim 膨胀而触碰投稿红线。硕论应按下文“主攻冲刺档”要求写指标与图表，最高档仅作为远期上探目标，不作为本轮写作牵引基准。

### 6.2 主攻冲刺档

候选包括 IEEE TAES、AIAA Journal、IEEE TGRS、Aerospace Science and Technology、Optics Express、高水平遥感/光学/航天期刊。

路线一若完成以下内容，可作为主要冲刺层级：

- v0.4 统一前向模型验证闭合；
- OCS/image/fusion 全链路结果重跑；
- observability、posterior-like distribution、consistency 等指标闭合；
- G1/G3/G5 多几何证据链清楚；
- roll 和 mismatch 边界诚实；
- 图表与 source data 可复现、可审计。

### 6.3 稳健 SCI 档

候选包括 Acta Astronautica、ASR、Chinese Journal of Aeronautics、Remote Sensing 等。

若结果主要停留在受控仿真、缺少真实/半真实锚点，但 v0.4 证据链完整，则路线一适合落在该档。Acta/ASR 不再作为默认第一目标，但仍是稳健承接选项。

## 7. 多观测几何处理

路线一建议把多观测几何作为主线变量，而不是附属补充。

推荐分层：

| 几何层级 | 作用 | 是否进入主线 |
|---|---|---|
| G1 | single-geometry phase63 公平基线 | 是 |
| G3 | 少量代表性 phase 几何，检验多观测增益 | 是，优先 |
| G5 | 现有 24/45/63/90/120 五几何 | 是，作为完整主线候选 |
| G9/G12 | 更密 phase 集合 | 暂作扩展，不作为默认主线 |

写作时必须说明：几何是已知观测配置，OCS 特征是同一姿态在多个 sun/det 几何下的光度向量；这不是“未知观测几何反演”。

## 8. roll 处理

路线一不进入 full 3-DOF 全量重跑，但也不忽略 roll。

关键判断：对硕士学位论文，roll sensitivity 探针不是可选项，而是答辩承重墙。答辩委员几乎必问“roll 固定为 0，roll≠0 时你的可观测性地图/最亮姿态会不会被推翻”。这一刀只能用敏感性实验数据回答，不能用“资源估计表明数据量太大所以未做”搪塞。因此 roll sensitivity 与资源估计是“且”的关系，不是“或”。

建议处理方式：

1. 主实验：`roll = 0`，只声明 fixed-roll yaw-pitch benchmark。
2. roll sensitivity 探针（主线必做，非可选）：在姿态子集与代表几何上扫 `roll ∈ {±5,±10,±15…}`，量化三件事——signature 漂移幅度（OCS 向量与图像随 roll 变化多大）、混淆结构稳定性（roll≠0 时 yaw-pitch 混淆图是否被推翻）、最亮点是否迁移。该实验一份多用：答辩防线 + 高刊 rebuttal 弹药 + 大小项目衔接。
3. 资源估计：同时给出单姿态耗时与存储估计表，说明 full 3-DOF 全量为何超出本轮预算。此项与第 2 项并行，不能相互替代。
4. 论文边界：标题、摘要、方法、结果、limitations 均显式标注 fixed-roll。
5. 后续路线：把 roll-aware / 3-DOF benchmark 留给路线二或后续工作。
6. 小项目衔接：小项目（最亮构型搜索）本质是三维问题，`roll = 0` 切片最亮点在答辩中是硬伤，必须 roll-aware；大论文 roll 探针的结果正好喂给小项目的 roll-aware 最亮搜索。两者解耦但衔接。

如果后续作者无法接受 fixed-roll 大论文边界，则路线一不应作为最终主线。

## 9. 路线一优势

- 与 24 号冻结主线兼容，不需要立即推翻方法冻结文件。
- 可控、可落地，避免全量 3-DOF 数据规模爆炸。
- 更适合先完成大论文主体，再根据证据强度决定发刊档位。
- 可以把贡献从“误差更低”转为“信息量、互补性、置信和边界更清楚”。
- 答辩时容易解释为什么不夸大为真实未知目标完整反演。

## 10. 路线一风险

- fixed-roll 可能被质疑为姿态空间不完整。
- 如果没有 roll sensitivity，答辩老师可能认为边界处理不足。
- 如果没有真实/半真实锚点，高水平期刊冲刺风险较高。
- 如果多几何只停留在 G1 或 phase63，OCS 多观测向量主线会显得不充分。
- 如果仍混用旧 v0.3 OCS 结果，路线一失效。

## 11. 最低可接受补强

若采用路线一，进入正式代码前至少应规划以下补强：

1. 保持 v0.4 Blender-derived OCS 全链路重跑。
2. 保留 G1/G3/G5 几何分层设计。
3. 做单姿态 smoke test 与资源估计。
4. 做 depth round-trip、Position/WorldCoord、sun-view depth、V_sun_macro_mask reprojection 和 20 姿态 shadow validation。
5. roll sensitivity 小实验（主线必做，非可选）与资源估计表二者并行，不可相互替代。
6. 在大论文结构中单列 fixed-roll 边界与 3-DOF 后续路线。

## 12. 暂定结论

路线一暂定为：

```text
大论文主线可接受；
主攻 SCI 有现实可行性；
高刊可作为写作质量牵引但不作为默认主投；
代码阶段可继续沿 fixed-roll yaw-pitch v0.4 路线准备，
但必须先把 roll sensitivity / 3-DOF boundary 作为答辩与发刊防线写入后续计划。
```

本结论仅为“路线一”候选。后续应继续形成路线二、路线三等备选方案，再统一比较：

- 学位大论文是否更稳；
- 发刊上限是否更高；
- 代码与实验成本是否可承受；
- 答辩老师与审稿人最可能质疑什么；
- 哪条路线最不容易在 claim 上被一票否决。

