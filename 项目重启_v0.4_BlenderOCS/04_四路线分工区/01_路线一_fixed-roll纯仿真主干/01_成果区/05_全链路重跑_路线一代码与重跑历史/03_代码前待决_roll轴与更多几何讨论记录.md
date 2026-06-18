# 代码前待决：是否加入 roll 轴与更多观测几何

最后更新：2026-06-18

## 状态

本文件是代码实施前关于 roll 轴与更多观测几何的历史讨论记录，不再作为阻塞路线一代码回归的待决项。

四路线综合审阅与最终路线裁决 R01 已确认：路线一 fixed-roll yaw-pitch controlled benchmark 作为 v0.4 必选主干成立，roll sensitivity 为主线必做探针；3-DOF / roll-aware 作为后续扩展或路线三暗室条件增强方向，不反向阻塞路线一 Phase 0 代码回归。

## 历史问题来源

当前冻结路线把姿态定义为 `(yaw, pitch)`，`roll = 0`。这条路线可以支撑 fixed-roll yaw-pitch benchmark，但不能支撑完整三轴姿态反演。

作者提出的核心担心是正确的：

- roll 不是一个可随手忽略的小参数，而是一个新的姿态自由度。
- 若真实任务中 roll 未知，固定 roll 的反演结果不能说明完整 3-DOF 姿态准确性。
- 若加入 roll，现有 yaw-pitch 反演、误差指标、manifest 字段、图表和论文 claim 都需要重新审视。
- 对最亮姿态问题，固定 roll 只能得到二维切片最亮点，不能排除 roll 不为 0 时出现更亮 glint。

## 当前已明确的判断

### 1. fixed-roll 路线仍然可以成立，但必须收窄 claim

如果继续当前路线，大项目只能写成：

```text
controlled yaw-pitch inversion benchmark under fixed roll
```

不能写成：

```text
full 3-DOF attitude inversion
real unknown target attitude recovery
```

准确性只能解释为：在同一 STL、BRDF、visibility、sun/det 几何和 `roll = 0` 条件下，对 yaw-pitch 标签的条件性反演准确性。

### 2. 若加入 roll，问题会变成近似重开一篇

加入 roll 后，至少需要重新决定：

- 姿态采样：Euler yaw/pitch/roll 网格，还是 SO(3) / quaternion 采样。
- 输出标签：继续输出 Euler 三角，还是输出 rotation matrix / quaternion / 6D rotation。
- 主指标：应从 yaw-pitch 球面角误差改为 SO(3) rotation geodesic error。
- manifest：记录 `roll_deg` 或完整 rotation representation，并保证 OCS/image/fusion 对齐。
- 数据规模：5 度全量 3D 网格会非常大。

粗略规模：

```text
5 deg:  72 yaw x 37 pitch x 72 roll = 191,808 poses / geom
10 deg: 36 yaw x 19 pitch x 36 roll = 24,624 poses / geom
15 deg: 24 yaw x 13 pitch x 24 roll = 7,488 poses / geom
```

若再乘以 5 个观测几何，5 度全量会接近百万姿态记录，不应在未做资源评估前直接启动。

### 3. 更多几何应作为独立设计变量

更多几何不只是“多跑几个 phase”。它改变 OCS 可观测性与信息量定义。

后续可讨论的几何集合包括：

- `G1`: single-geometry phase63 公平基线。
- `G3`: 低/中/高相位角代表几何。
- `G5`: 现有 24/45/63/90/120 五几何。
- `G9` 或 `G12`: 更密相位角集合，作为扩展而非默认主线。

大项目的多几何反演应明确：几何是已知观测配置，OCS 特征是同一姿态在多个 sun/det 几何下的多观测光度向量；这不是“未知观测几何反演”。

### 4. 大项目与小项目的处理不同

大项目关注反演与可观测性，可以选择 fixed-roll benchmark 或 3-DOF benchmark。

小项目关注最亮构型搜索，最终必须考虑 roll；否则只能得到 `roll = 0` 二维切片的最亮点，不能说明三维姿态空间最亮。

## 后续若解冻 3-DOF 时再讨论的问题

1. 大项目是否仍接受 fixed-roll yaw-pitch benchmark 作为主线？
2. 如果不接受，是否正式改为 3-DOF roll-aware benchmark？
3. 若改为 3-DOF，采用 10 度/15 度粗网格，还是 SO(3) 随机采样？
4. 主表是否保留 single-geometry 公平基线，并把 G3/G5 作为多几何扩展？
5. image 是否仍只做 phase63，还是也扩展到多几何图像？
6. 是否先做一个小规模资源评估：若单姿态耗时和存储量过高，则不进入全量 3D。
7. 若不加入 roll，论文标题、摘要、方法、结果和 limitation 中如何明确 fixed-roll 边界？

## 当前执行门槛

R01 已明确路线一可沿 fixed-roll 主干推进，但仍不得直接进入全量生成或训练。当前只允许回到 Phase 0 gate：

允许做的事情：

- 搭建 `06_v0.4_code/` 骨架。
- 记录环境依赖和硬件信息。
- 做单姿态 smoke test、资源估算、depth round-trip、20 姿态 shadow validation。
- 按路线一主线执行 roll sensitivity 探针设计。

不应做的事情：

- 跳过 Phase 0 gate，直接按 `roll = 0` 路线全量生成数据。
- 直接训练 OCS-only / image-only / fusion。
- 直接修改方法冻结文件 `13` / `14` 为 3-DOF，除非作者确认改线。
