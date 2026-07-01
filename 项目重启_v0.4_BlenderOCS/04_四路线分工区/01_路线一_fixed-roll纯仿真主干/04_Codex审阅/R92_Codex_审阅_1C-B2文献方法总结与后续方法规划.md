# R92 Codex 审阅：1C-B2 文献方法总结与后续方法规划

最后更新：2026-06-29
执行端：Codex
性质：对 `87_1C-B2_文献方法总结与后续方法规划_Claude执行报告.md` 的文献核读、方法审阅与下一步建议。本文不放行新训练、不生成新数据、不改 split/模型/超参/seed、不改代码、不改论文正文、不改成果区、不改 CLAUDE.md。

## 0. 裁决

```text
1C-B2 Claude 方法总结：整体通过，建议进入头A/头B合并审阅
P0 只读诊断层：建议作为下一阶段首入口，但仍需作者/阶段门正式放行
P1 判据改正 / fusion 改正：建议列为第一批 C 类候选，不在本文件放行
P2 light-curve sequence 正式数据线：方向成立，但必须等 P0/P1 证据后另设重门
R04 负结果链：必须保持可复现，不得原地覆盖
```

Codex 判断：Claude 的大方向是对的，尤其是把当前 yaw-block 失败从“物理不可观测”收窄为 `protocol-defined extrapolation gap`，并把单帧 OCS 定位为 light-curve 谱系中的退化信息形态。需要补强的是：Wetterer & Jah 应作为核心证据写进主叙事；Gerwe & Idell、Kaasalainen I/II、Rondao ChiNet 分别支撑“可观测性诊断”“序列/多几何消歧”“非朴素融合/时序融合”三条方法线。

## 1. 四篇关键文献核读结论

### 1.1 Wetterer & Jah 2009：最贴近本项目的核心证据

本篇不是泛泛的光变反演文献，而是与本项目高度同族：

```text
输入：ground-based brightness / light curve
估计器：quaternion-based UKF
前向模型：facet model + simplified Cook-Torrance reflectance
未知量：attitude / angular velocity，可扩展到 surface-reflection parameters
失败模式：对称目标会让不同 rotation-axis positions 产生近乎相同 light curves
```

关键意义：

- 它直接证明“用光度序列估姿”在受控模型下可行，但前提是有时间序列、动态模型和较准确的测量模型。
- 它明确把不同自转轴导致近似相同光变曲线称为经典可观测性问题。Fig. 4 的初值到终值聚簇，正是你当前 yaw 问题最好的文献镜像。
- 它使用 Cook-Torrance 反射模型族，和项目的 BRDF/OCS 前向模型有自然亲缘关系，可作为“不是凭空换信息源，而是沿同族物理模型升维”的证据。
- 它也提醒真实数据不能轻易宣称成功：形状、BRDF、端部结构、饱和 glint、真实测量模型都会影响收敛。

对项目的写法建议：

```text
不要写：我们的 yaw 物理不可观测。
应写：在当前单帧 OCS + yaw-block 协议下出现的外推失败，与光变定姿文献中由目标对称性和几何覆盖不足导致的可观测性歧义一致；序列化和多几何观测是文献中处理该问题的主流路径。
```

### 1.2 Gerwe & Idell 2003：把失败写成可观测性分析的工具箱

本篇提供的不是新网络结构，而是评价“给定观测几何到底能估多准”的理论框架：

```text
核心工具：Cramer-Rao / Fisher information
目标：orientation estimation accuracy limit
变量：viewing perspective, sensor/noise, target geometry, nuisance parameters
扩展：multiple images / multiple sensors / multiperspective fusion
```

对项目最重要的三点：

- Fisher/CRLB 可把“某些 yaw 区域难估”从训练现象提升为局部信息量不足的论证。
- 文中多视角结果显示，不同姿态分量有不同最佳观测视角，多视角组合能减少 blind spots。这正对应项目中 pitch 明显好于 yaw 的各向异性。
- nuisance parameters 会抬高 CRLB；若忽略形状、反射、传感器误差，理论下界会偏乐观。这能约束我们不要把理想合成结论外推真实 GEO。

建议落地为 P0/P1 诊断：

```text
P0-D1 signature distance：同一 pitch 或同一几何下，计算不同 yaw 的 OCS/图像特征距离矩阵。
P0-D2 confusion cluster：把误判样本按真实 yaw / 预测 yaw 聚簇，找对称或近似等价弧段。
P0-D3 geometry coverage：按观测相位、太阳-目标-相机角、可见/遮挡比例分层，看 yaw 失败是否集中在信息低谷。
P1-D4 Fisher/CRLB-lite：若后续建模，先做有限差分雅可比和局部 Fisher proxy，不急于写完整 CRLB。
```

### 1.3 Kaasalainen I/II：序列、多几何和歧义边界的理论背景

Kaasalainen I/II 的价值不在于“它是小行星所以可照搬”，而在于它把光变反问题的边界讲清楚：

```text
充分多的 lightcurves + 多几何观测，可稳定求 convex shape / pole / period。
非凸细节和散射参数更不稳定，常常只有定性意义。
非凸问题失去严格唯一性，局部极小和初值很重要。
散射律对总体形状/旋转状态影响相对次要，但不能无限加复杂参数。
```

对本项目的约束：

- 单帧 OCS 不是 lightcurve inversion 的等价物；它是抽掉时间/多几何演化后的下界输入。
- 若后续做 light-curve sequence，必须写成“信息源层级对比”，不是抛弃 OCS 后另起炉灶。
- 多几何覆盖比“更多同分布样本”更关键。当前 yaw-block 正是在问未见连续 yaw 弧段能否外推，因此应优先分析几何覆盖和签名相似性。

### 1.4 Rondao ChiNet 2022：融合与序列架构的边界证据

ChiNet 对当前 joint negative result 的意义很明确：

```text
它使用 CNN 前端 + LSTM 后端处理序列，而不是单帧独立估计。
它用 RGBT channel-wise low-level fusion，并单独消融 recurrent module 和 multimodal inputs。
它报告 multimodal input 与 recurrent module 的边际贡献，而不是只做一次 early concat 后下普遍结论。
```

对项目的约束：

- 当前 image 256 + OCS 128 + concat + single linear head 只能否定这一种 naive early fusion。
- 不能把它写成“图像与 OCS 不互补”。
- 如果要回答互补性，至少需要一个 `late/decision-level fusion` 或 `mid fusion + modality balance` 的独立消融。

## 2. 对 Claude B-2 的修正与加固

### 2.1 应保留的判断

```text
1. 单帧 OCS 是 light-curve 谱系中的退化信息形态。
2. 当前 exact-bin yaw=0% 是 diagnostic sentinel，不是物理不可观测。
3. 当前 early fusion 只否定 naive early concat。
4. P0 只读诊断应先于任何新训练。
5. 所有改正都必须保护 R04 负结果链。
```

### 2.2 需要收窄的表述

```text
1. “P0 判据/损失”不应叫 P0。凡涉及训练目标、loss、输出头变化，都应归入 P1/C 类阶段门。
2. “伪光变曲线”只能叫 probe，不能叫 light-curve experiment。它由现有 yaw 排序样本拼接，不等价真实时间序列观测。
3. “Fisher/CRLB”在当前阶段应先做 proxy 或诊断设计，完整 CRLB 需要明确噪声模型、观测模型、参数化与 nuisance parameters。
4. ChiNet 支撑的是序列/多模态/消融纪律，不直接支撑 OCS 与图像必然互补。
```

## 3. 下一步方法建议

### 3.1 第一优先级：P0 只读诊断

建议先放行一个纯只读阶段，不训练、不渲染、不改 split：

```text
P0-1 协议对齐核查
目的：确认 V0.3/V0.4 差异来自 split、判据、数据形态还是模型能力。
输出：同口径重聚合表，不宣称恢复成功。

P0-2 signature distance / confusion cluster
目的：证明 yaw-block 失败是否对应输入签名近似重合。
输出：yaw-yaw 距离热图、混淆簇、近邻对案例。

P0-3 伪光变曲线 probe
目的：在不生成新数据前，检查按 yaw/几何排序后的 OCS 序列是否比单帧更可分。
输出：描述性图和最近邻/线性可分性对比，只作为是否进入 P2 的依据。
```

这三项最适合现在做，因为它们能决定后续是“改判据即可解释一部分失败”，还是“必须升级信息源到序列”。

### 3.2 第二优先级：P1 单项 C 类改正

P1 不应一次全堆。建议拆成两个独立阶段门，各自只回答一个问题：

```text
P1-A 判据改正
问题：exact-bin 分类是否放大了 yaw-block 失败？
候选：circular regression / sin-cos regression / von-Mises loss / regression+classification 双头。
必须保留：原 exact-bin sentinel 作为附指标，方便和 R04 链对照。

P1-B fusion 改正
问题：图像与 OCS 是否互补，而不是 naive concat 是否碰巧增益？
候选：late fusion、decision-level averaging/selection、mid fusion with balanced embeddings、gated fusion。
必须报告：image-only、OCS-only、early concat、改进 fusion 的边际贡献。
```

执行顺序建议：先 P1-A，再 P1-B。理由是判据问题更底层、更便宜，也更可能直接改变“0% 是否代表失败”的解释。

### 3.3 第三优先级：P2 正式 light-curve sequence

P2 是治本线，但现在不宜直接开。进入 P2 前至少要满足：

```text
1. P0 证明单帧签名确有歧义或几何盲区。
2. P1-A 证明连续角度判据仍不能充分解决 yaw-block 外推。
3. 已定义新数据与 R04 数据的关系，避免把新结果污染成旧链修补。
4. 明确 inverse-crime 防护：前向模型、噪声/退化、几何采样、train/test yaw-block 全部预注册。
```

正式 P2 的论文价值应写成：

```text
single-frame OCS lower bound vs light-curve sequence upper information layer
```

而不是：

```text
single-frame failed, so replaced by sequence
```

## 4. 论文叙事建议

当前最稳的论文主线不是“我们做出了一个高准确率姿态估计器”，而是：

```text
在已知形状与受控 BRDF 的 fixed-roll 合成 benchmark 中，单帧多视角 OCS 与简单图像融合在 strict yaw-block 外推下暴露出 yaw 可观测性边界。该边界与光变定姿文献中的对称性歧义一致。进一步的可观测性诊断、连续角度判据、非朴素融合和 light-curve sequence 对比，可把该负结果发展为“信息形态与几何覆盖如何决定姿态可辨识性”的方法论文。
```

可以写的 claim：

```text
- 当前协议下存在 yaw extrapolation gap。
- pitch 与 yaw 存在姿态分量各向异性。
- 单帧 OCS 是有价值的信息下界，但不足以自动消除 yaw 歧义。
- naive early fusion 无自动增益，不代表所有 fusion 无效。
- 后续应以可观测性诊断和序列化信息源作为主线。
```

不能写的 claim：

```text
- yaw 物理不可观测。
- OCS 不携带 yaw 信息。
- 图像和 OCS 普遍不互补。
- exact-bin 0% 等于可靠拒识。
- 当前结论可迁移真实 GEO、三轴自由姿态或暗室实验。
```

## 5. 建议合并审阅问题

进入头A/头B合并审阅时，建议只裁定下面五个问题：

```text
Q1. 是否正式放行 P0 只读诊断包？
Q2. P0 输出目录、命名、验收表由谁定稿？
Q3. P1-A 判据改正是否作为第一项 C 类阶段门？是否要求双头保留 sentinel？
Q4. P1-B fusion 改正是否必须与 P1-A 解耦，分别报告边际贡献？
Q5. P2 light-curve sequence 的进入条件是否采用本 R92 第 3.3 节四条门槛？
```

## 6. 本轮阅读依据

本轮实际核读的 PDF：

```text
03_项目说明与规划材料/05_参考材料/03_文献与引用材料/papers/JGCD_2009_Wetterer_Jah_attitude_determination_light_curves.pdf
03_项目说明与规划材料/05_参考材料/03_文献与引用材料/papers/JOSAA_2003_Gerwe_Idell_orientation_Cramer_Rao.pdf
03_项目说明与规划材料/05_参考材料/03_文献与引用材料/papers/Icarus_2001_Kaasalainen_lightcurve_inversion_I_shape.pdf
03_项目说明与规划材料/05_参考材料/03_文献与引用材料/papers/Icarus_2001_Kaasalainen_lightcurve_inversion_II_complete_inverse_problem.pdf
03_项目说明与规划材料/05_参考材料/03_文献与引用材料/papers/TAES_2022_Rondao_ChiNet_multimodal_spacecraft_pose.pdf
```

关联输入：

```text
02_Claude输出/87_1C-B2_文献方法总结与后续方法规划_Claude执行报告.md
04_Codex审阅/R91_Codex_文献检索_1C-B1六方向方法约束与PDF入库.md
04_Codex审阅/R90_Codex_审阅_1C-A3-FIX01通过_头A桥接材料稳定.md
02_Claude输出/84_暂停点中期复盘_质疑与后期路线建议_Claude意见供Codex.md
02_Claude输出/85_文献补课材料_检索提示词与重点订阅期刊_Claude整理.md
```

## 7. 最终建议

建议接受 Claude B-2 作为候选方法规划，并用本 R92 的收窄口径进入合并审阅。下一步最合理的技术动作是 P0 只读诊断包，而不是立刻改模型或生成 light-curve 新数据。

