# R111 Codex 原文保留：现有结果问答与路线一阶段分析

最后更新：2026-06-30  
性质：对 R110 的增强版记忆文件；优先保留作者问题原文与 Codex 已落盘回答内容，再进行总结性分析  
状态：**不作新裁决，不放行新阶段，不替代后续 Claude 执行结果审阅。**

## 0. 本文件目的

本文件按作者最新要求，对从以下问题开始的关键对话进行原文级保留：

```text
到目前为止，我得到的结果是什么（严格根据结果回答，采取了什么方式，预期得到什么结果，最后得到了什么结果），说明了说明问题
```

作者进一步要求：

```text
确保把刚才我的问题和你的回答均完整保留后，再做一个总结性的分析，一定保留原文
```

因此本文采用固定结构：

```text
1. 先保留作者问题原文。
2. 再保留 Codex 已落盘回答内容原文/回答保留稿。
3. 最后单独做总结性分析。
```

说明：当前对话发生过上下文压缩，聊天窗口中的 Codex 逐字回复无法从运行环境完整反查；因此本文将“可见的作者问题”逐字保留，并把 R110 已经落盘的 Codex 回答正文作为回答保留稿完整纳入。后续审阅应以本文件和 R110 一并作为记忆锚点，不再只依赖模型短期记忆。

## 1. 作者问题原文保留

### 1.1 起点问题：要求严格按结果复盘

```text
到目前为止，我得到的结果是什么（严格根据结果回答，采取了什么方式，预期得到什么结果，最后得到了什么结果），说明了说明问题
```

### 1.2 要求回答更细致，解释术语和实验方式

```text
回答更细致一点。1.采取的方式：4维是什么意思，yaw-block 5-fold什么意思，结果中的英文结果是什么意思看不懂，说明单组/单帧外推不够？实际用了几帧做训练，哪些角度？这些都说清楚。我只是拿C2距离，后面几个的回答都这样说清楚细致
```

### 1.3 对 C2 输入现实性、反演任务分层、外推协议、V0.3 对比和噪声的质疑

```text
1.单帧OCS采取4维聚合光度量，都是现实中是得不到各个部位的OCS值的，只有总体，最开始的计划不是多角度的OCS吗？2.输入应该是光度与图像，然后反演姿态。3.为什么我的模型要去外推一整段完全没见过的一整段yaw呢，其实我觉得这里可以分几层，本质上是反演模型的问题，一是这类，训练部分信息，然后去测试完全没见过的。二是进一步，训练大量信息，基本包含任何一段，能测试出对一些未训练的精确插值反演。三是数据库方式，基本都进行训练，反演时候只需要对应查库查表即可。因为输出就是图像与OCS光度两端，用两端做这个信息量反演，达成的目的就是我只要获取到相关航天器的外形，我就可以用同一套方法，进行训练，然后只要获取到它的OCS与拍到的图像（模糊），就可以反演出真实姿态。从这个角度去回答置信度等三方面，你认为呢？之前又是怎么想的？4.single-frame / fixed-roll / yaw-block是什么意思。5.你说C2输入太压缩，但是V0.3也是这种输入，它的效果就很好，之前对比过，是采样问题还是模型问题？6.现在不论光度还是图像的反演结果都不好，我确实怀疑是方法与模型问题，怎么可能用这么少的数据训练模型去推一段完全未知的姿态呢？相关文献也调研了，别人是怎么做的？7.yaw_sin, yaw_cos, pitch_sin, pitch_cos。这具体是在输出什么，circular regression换后改为回归，那反演的结果是什么？角度吗？8.加图像噪声可能确实破坏了结果，但是真实情况噪声是必须的。
```

### 1.4 对后续小项目、1C 目标、外推原因和光度方向的追问

```text
1.而且我认为这样做能够续接之后的小项目目标。2.这样做也能达到我最初的第一C目的。3.为什么之前会采取这样的外推方法？而且反演等cnn都是用的最基础的，文献参考明显不够。4.后续准备光度方向，一个是单帧多几何得做，一个单帧单几何要做，一个光变时序也要做，进行对比研究你觉得呢
```

### 1.5 指出 Codex 对小目标和 1C 理解出错，要求重新读文件

```text
你理解的小目标出错，重新看文件后回答，1C也出错，读了文件再回答
```

### 1.6 询问 Claude 结果回来后是否可以闭口，是否要等 B 完毕、T3/T4

```text
后续等待claude这套结果返回后，是否就可以闭口，按照这个方向继续路线一？还是说要等B完毕比较好，T3,T4？
```

### 1.7 要求形成最新审阅 md，并按分支总结路线一进展

```text
不要做决定与总结回答。现在我需要你讲“到目前为止，我得到的结果是什么（严格根据结果回答，采取了什么方式，预期得到什么结果，最后得到了什么结果），说明了说明问题”的问答开始的关键信息到最后的对话全部保留，然后最后总结现在的路线一进展情况（类似分了几个分支，0.分析现有结果与最初目的。1是负结果追因。2.头B进行。3.准备回归路线1.4.续接后续小项目目的），形成最新的审阅md文件
```

### 1.8 最新补充要求：问题和回答均完整保留后再分析

```text
确保把刚才我的问题和你的回答均完整保留后，再做一个总结性的分析，一定保留原文
```

## 2. Codex 回答内容原文保留稿

本节保留 R110 已落盘的 Codex 回答正文。其功能是把前述问答中已经澄清的事实、术语、结果和路线判断固定下来，避免后续审阅又回到“只剩碎片记忆”的状态。

### 2.1 严格根据结果：当前已得到什么

当前路线一 C 已执行结果主要来自 fixed-roll yaw-pitch 网格：

```text
yaw：0° 到 355°，每 5° 一个点，共 72 个 yaw
pitch：-90° 到 +90°，每 5° 一个点，共 37 个 pitch
roll：固定为 0°
总样本数：72 × 37 = 2664
```

每个样本是一个固定姿态记录：

```text
1 张 256×256 灰度图像
+ 同姿态下 OCS 光度特征
+ yaw / pitch 标签
```

这不是时间序列，也不是光变曲线。所谓 single-frame，当前指每次输入只有一个姿态下的一张图像或一组同姿态光度。

### 2.2 当前 C2 的 4维 OCS 是什么

C2 当前使用的 4维 OCS 为：

```text
ocs_total：总 OCS 光度积分
ocs_jinshuzhuti：金属主体部分 OCS
ocs_taiyangnengban：太阳能板部分 OCS
ocs_yinshenban：隐身板/遮挡板部分 OCS
```

作者指出：现实中无法得到各个部位的 OCS 值，通常只能得到目标整体光度。

因此，该 4维 per-part OCS 不应作为真实 independent photometric channel 的可运营输入，只能作为：

```text
semi-oracle upper bound / diagnostic feature
```

这一点与 24 号文件一致：

```text
F2 per-part OCS = semi-oracle 上界或诊断
```

### 2.3 yaw-block 5-fold 是什么

当前 yaw-block 5-fold 不是随机划分，而是按连续 yaw 弧段留出测试。

test yaw block 为：

| fold | test yaw block | test 样本数 | pitch |
|---|---:|---:|---|
| fold0 | 0° 到 70° | 555 | -90° 到 +90° |
| fold1 | 75° 到 145° | 555 | -90° 到 +90° |
| fold2 | 150° 到 215° | 518 | -90° 到 +90° |
| fold3 | 220° 到 285° | 518 | -90° 到 +90° |
| fold4 | 290° 到 355° | 518 | -90° 到 +90° |

因此 yaw-block 是严格外推压力测试：模型要预测训练中完全没见过的一整段 yaw。

### 2.4 C2 OCS-only 结果

方式：

```text
只输入 4维 OCS 光度特征；
不输入图像；
在 yaw-block 5-fold 下训练/测试。
```

预期：

```text
如果 OCS 光度特征单独携带足够姿态信息，则 OCS-only 应明显好于随机。
```

结果：

```text
exact-bin yaw = 0.00%
circular MAE = 17.79 bins ≈ 88.97°
within-6bin = 16.03%
coarse45 = 11.82%
coarse90 = 24.44%
```

解释：

```text
random circular MAE 理论约 90°
random coarse90 约 25%
random coarse45 约 12.5%
```

因此当前 C2 结果说明：

```text
当前 4维 per-part OCS 聚合签名在 single-frame / fixed-roll / yaw-block 外推协议中，不能稳定支持 yaw 反演。
```

它不能说明：

```text
所有 OCS 不携带姿态信息；
多几何 OCS 不行；
光变曲线不行；
yaw 物理上完全不可观测。
```

### 2.5 C3 image_only 结果

方式：

```text
只输入单姿态灰度图像；
不用 OCS；
仍采用 yaw-block 5-fold。
```

预期：

```text
图像保留空间结构，应比 4维 OCS 更有姿态线索。
```

结果：

```text
exact-bin yaw = 0.00%
circular MAE = 16.33 bins ≈ 81.63°
within-6bin = 25.56%
coarse45 = 18.09%
coarse90 = 25.41%
```

说明：

```text
图像比 C2 OCS-only 略好，说明图像通道携带更多姿态线索；
但 exact-bin 仍为 0%，coarse90 仍接近随机，不能写成稳定 yaw 反演成功。
```

### 2.6 C3 joint 结果

方式：

```text
图像 + 4维 OCS early concat；
仍采用 yaw-block 5-fold。
```

预期：

```text
图像提供空间结构，OCS 提供积分光度信息，二者可能互补。
```

结果：

```text
exact-bin yaw = 0.00%
circular MAE = 16.32 bins ≈ 81.58°
within-6bin = 26.50%
coarse45 = 18.32%
coarse90 = 24.85%
```

与 image_only 几乎持平。说明：

```text
当前 early-concat joint 没有带来实质增益。
```

边界：

```text
这只能否定当前 naive early concat；
不能否定所有 image + OCS 融合；
不能否定 non-naive fusion、posterior-level fusion 或 consistency-as-confidence。
```

### 2.7 P1-A 指标重构结果

方式：

```text
不只看 exact-bin；
改看 circular MAE、within-k、coarse45/coarse90、yaw-block 分层、pitch 分层。
```

预期：

```text
判断 0% exact-bin 是不是只是判据太苛刻；
判断 relaxed metrics 下是否存在部分信息；
判断不同 yaw-block 是否异质。
```

结果：

```text
exact-bin 确实过严；
但 relaxed metrics 仍显示 yaw 外推整体较弱；
yaw-block 异质性强。
```

例如 C2：

```text
fold3 test yaw [220°, 285°]：circular MAE = 7.50 bins ≈ 37.5°
within-6bin = 42.86%

fold4 test yaw [290°, 355°]：circular MAE = 26.59 bins ≈ 132.95°
coarse45 = 0%
```

说明：

```text
0% exact-bin 不能读成 yaw 信息完全不存在；
但也不能读成只是指标过严。
当前结果更像位置依赖的 yaw-block 外推鸿沟。
```

### 2.8 B6 fold0 circular regression 结果

方式：

```text
把 72-bin / 37-bin 分类头改为连续 circular regression；
输出 [yaw_sin, yaw_cos, pitch_sin, pitch_cos]；
用 atan2 解码回 yaw/pitch 角度；
目前只完成 fold0 pilot，未完成 5-fold。
```

预期：

```text
如果 exact-bin 分类训练头是主因，换成连续角度回归后 yaw 应明显改善。
```

结果：

```text
image_only no-aug：yaw cMAE = 96.26°
yaw hit@10 = 8.83%
yaw hit@30 = 27.75%
coarse90 = 27.03%
pitch MAE = 14.89°

joint no-aug：yaw cMAE = 99.63°
yaw hit@10 = 7.21%
yaw hit@30 = 23.42%
coarse90 = 27.57%
pitch MAE = 15.70°

ocs_only no-aug：yaw cMAE = 112.06°
hit@10 / hit@30 / coarse90 = 0
pitch MAE = 46.34°
```

说明：

```text
fold0 上，circular regression 没有解决 yaw 外推；
但 pitch 明显改善，说明回归头不是整体无效；
问题集中在 yaw 外推，而非模型完全不能学。
```

重要口径修正：

```text
101 曾用 B6 fold0 对比 P1-A 5-fold pooled baseline，口径不匹配。
按 fold0 对齐后，image/joint cMAE 并非简单“更差”，而是 cMAE 持平或局部略好，但 within/coarse 未形成稳定改善。
```

### 2.9 B6 augmentation 结果

方式：

```text
train-time 图像增广：
Gaussian noise σ=0.01
brightness ±10%
integer shift ≤2 px
```

结果：

```text
image_only standard：yaw cMAE = 148.24°
hit@10 = 0
hit@30 = 0
coarse90 = 0
pitch MAE = 54.67°

joint standard：yaw cMAE = 160.00°
hit@10 = 0
hit@30 = 0
coarse90 = 0
pitch MAE = 57.01°
```

说明：

```text
当前这组粗增广包在 fold0 下明显负面；
但不能据此否定真实噪声建模。
```

真实情况仍必须考虑噪声，但需要更合理的噪声/退化模型：

```text
PSF/模糊、曝光、Poisson noise、read noise、背景、运动拖影、低分辨率、测光误差等。
```

## 3. 作者提出的关键纠偏与 Codex 文件校正

### 3.1 4维 OCS 与现实不一致

作者指出：

```text
现实中得不到各个部位的 OCS 值，通常只有整体光度。
```

因此当前 4维 per-part OCS 不能代表真实可观测的独立光度通道。

文件校正：

```text
24 号已明确：
F1 单瞬时总光通量标量 = 信息下界；
F2 per-part OCS = semi-oracle 上界或诊断；
L1 跨几何多观测光度向量 = 主线 OCS。
```

### 3.2 最初计划应是多角度 / 多几何 OCS

作者指出：

```text
最开始的计划不是单个 4维 per-part OCS，而是多角度 OCS。
```

文件校正：

```text
24 号主线：
OCS 主形态采用 multi-observation photometric vector across controlled sun/view geometries。

路线一 C：
fixed-roll yaw-pitch controlled benchmark
+ roll sensitivity 探针
+ G1/G3/G5 多几何 OCS 可观测性分析。
```

因此后续必须把路线一 C 从当前单几何/4维诊断，拉回：

```text
G1 / G3 / G5 多几何总光度向量
```

而不是继续让 4维 per-part C2 代表主线。

### 3.3 输入应是光度与图像，目标是反演姿态

作者提出：

```text
输入应该是光度与图像，然后反演姿态；
目标是获取相关航天器外形后，用同一套方法训练/建库，再用 OCS 光度和模糊图像反演真实姿态。
```

文件边界：

```text
v0.4 不是“真实未知目标姿态反演系统”；
而是 model-known 条件下，OCS 与图像的姿态信息可观测性、互补性和置信一致性研究。
```

反演在路线一 C 中的定位：

```text
反演结果只作为可观测性验证工具；
不写成真实未知目标反演成功率。
```

### 3.4 作者提出三层反演任务

作者提出可分三层：

```text
1. 训练部分信息，测试完全没见过的一整段 yaw。
2. 训练大量信息，基本覆盖任何一段，测试未训练精确姿态的插值反演。
3. 数据库方式，基本都训练/仿真，反演时对应查库查表。
```

保留判断：

```text
第 1 层 = yaw-block 外推 stress test；
第 2 层 = 更接近 model-known 条件下的插值/局部泛化；
第 3 层 = 可作为 posterior-like / template / database 反演框架的一部分。
```

但需回到文件主线：

```text
路线一 C 不以真实反演成功率为终点；
查库/候选分布/后验分布的价值在于支撑 what can be known / when complementary / when trustworthy。
```

### 3.5 作者质疑为什么强外推一整段 yaw

作者指出：

```text
用这么少数据训练模型去推一段完全未知姿态不合理；
更像是在测试反演模型问题，而不是原始目的。
```

保留回答：

```text
yaw-block 的合理性是作为严格压力测试，防止 random split 虚高；
但它不应替代路线一 C 主线。
```

应降级为：

```text
strict extrapolation stress test / 外推边界诊断。
```

主线仍应补回：

```text
F1 lower-bound；
L1 G1/G3/G5 多几何 OCS；
image-only；
OCS-image consistency；
roll sensitivity。
```

## 4. Codex 先前误解与文件校正

### 4.1 对小项目的先前误解

Codex 先前曾把小项目误解成偏“查库/反演数据库”方向。

作者指出理解错误，要求重新读文件。

文件校正后，小项目真实目标为：

```text
在 yaw / pitch / roll 三轴姿态空间中，
寻找最亮构型、高信息构型、最优可观测姿态，
以及低信息 / 易混淆 / 不值得观测区域，
形成观测规划价值。
```

三轴小项目不是：

```text
真实未知目标三轴姿态反演系统；
单纯查库反演项目。
```

### 4.2 对 1C 的先前误解

Codex 先前把 1C 过度理解成 model-known 查库/反演方向。

文件校正后，1C 目标为：

```text
fixed-roll yaw-pitch controlled benchmark
+ roll sensitivity 探针
+ G1/G3/G5 多几何 OCS 可观测性分析
```

服务 24 号三问：

```text
What can be known?
When are OCS and image complementary?
When should we trust the estimate?
```

因此，路线一 C 后续不是简单转向查库，而是要回到：

```text
多几何 OCS 光度向量；
图像通道；
互补性；
置信一致性；
roll sensitivity；
三轴小项目接口。
```

### 4.3 24 号对 OCS 口径和形态的权威定义

24 号主线规定：

```text
OCS = independent non-imaging photometric channel
image = spatially resolved optical observation
```

OCS 主形态：

```text
OCS_L1 = multi-observation photometric vector across controlled sun/view geometries
```

非主线形态：

```text
F1 单瞬时总光通量标量 = 信息下界 baseline
F2 per-part OCS = semi-oracle 上界 / 诊断
L2 时域光变曲线 = Future Work / 后续方向
```

### 4.4 路线二与光变/时序的校正

R105/R106 将真实数据方向细化为：

```text
稀疏 GEO 光度时序 / 多帧多几何 photometric sequence
```

但路线二文件同时规定：

```text
GEO 数据库有光度、有几何、有型号、有时间序列；
没有目标 yaw/pitch/roll 姿态真值；
不能作为监督姿态反演数据集。
```

因此，真实光度时序可用于：

```text
真实光度趋势；
分布级对照；
多帧多几何现实性锚点；
sim-to-real 光度校准；
支撑路线一 C 和三轴小项目。
```

不能用于：

```text
监督训练真实 GEO 姿态反演器；
计算真实 GEO 姿态反演成功率；
验证某个三轴姿态真值。
```

## 5. 关于是否等待 B6 / T3 / T4 的上下文

作者问：

```text
后续等待 Claude 这套结果返回后，是否就可以闭口，按照这个方向继续路线一？
还是说要等 B 完毕比较好，T3, T4？
```

保留回答要点：

```text
B6-FIX01 若合规返回，只能闭 B6/T1：
判据、分类头、circular regression 是否是失败主因。
它不能闭整个路线一 C。
```

原因：

```text
路线一 C 还缺 24 号主线中的 F1/L1/G1/G3/G5、置信一致性、roll sensitivity 等证据。
```

同时：

```text
路线一 C 不必等待 T3/T4 全部完成。
```

R105/R106 的 T3 / 稀疏 GEO 光度时序是增强层或真实数据方向，不应反向阻塞路线一 C 主干。

但如果 B6 继续失败，则说明 single-frame 低信息形态不足，T3 的优先级会上升。

## 6. 当前路线一进展情况：按分支整理

### 6.0 分支 0：分析现有结果与最初目的

当前已完成：

```text
C2/C3 yaw-block 5-fold 负结果；
P1-A 指标重构；
B6 fold0 circular regression pilot；
P0/P1-A 只读诊断和指标分析；
文献与真实数据方向校正。
```

现有结果说明：

```text
single-frame / fixed-roll / yaw-block 压力测试下，
当前 4维 per-part OCS、image_only、early concat joint 均未得到稳定 yaw 外推。
```

但现有结果与最初目的存在偏移：

```text
最初 24号主线强调 L1 跨几何多观测光度向量；
当前 C2/C3 主要集中在 single-geometry / per-part 诊断和 yaw-block 外推；
不能让当前 C2/C3 完全代表路线一 C 主线。
```

需要保留的纠偏：

```text
F1 单几何总光通量 = 下界；
F2 per-part = semi-oracle / 诊断；
L1 G1/G3/G5 多几何总光度向量 = 主线。
```

### 6.1 分支 1：负结果追因

已做：

```text
exact-bin 0% 被确认过严，不能解释为 yaw 信息完全不存在；
relaxed metrics 显示 yaw 外推仍弱；
yaw-block 异质性强；
4维 OCS yaw 签名存在重叠；
fold0 B6 显示换 circular regression 未直接救回 yaw，但 pitch 改善明显。
```

当前追因状态：

```text
评价口径过严：已确认。
分类头/训练判据是否主因：B6-FIX01 待确认。
single-frame 信息形态不足：可能性上升，但不能用 B6 fold0 直接闭口。
多几何 OCS 主线尚未被充分检验。
```

作者的重要质疑：

```text
强迫模型外推一整段完全没见过的 yaw，可能不是最贴近实际反演目标的任务；
应区分外推 stress test、密集覆盖插值、数据库/候选分布反演三层任务。
```

### 6.2 分支 2：头B进行中

头B 已完成 / 稳定部分：

```text
B1 文献检索约束；
B2 方法总结与阶段门候选；
B3/P0 只读诊断；
B4/P1-A 指标重构；
B5 技术路线 / V0.3 协议坐实；
B6 初版 fold0 pilot。
```

当前状态：

```text
B6 初版 101 已由 R108 判定为 pilot 接收，但不闭口；
R109 已下达 B6-FIX01 多折补齐与 fold-matched baseline 修正任务。
```

B6-FIX01 预期能闭的范围：

```text
classification exact-bin -> circular regression 是否有效；
best-val vs final-epoch 是否影响结论；
pitch 改善是否稳定；
augmentation 当前包是否稳定负面；
判据/训练头是否可从“待确认”转为较稳定判断。
```

B6-FIX01 不能闭的范围：

```text
不能闭整个路线一 C；
不能替代 G1/G3/G5 多几何 OCS 主线；
不能替代 roll sensitivity；
不能触发头A/头B大合并裁决。
```

### 6.3 分支 3：准备回归路线一 C 主线

当前需要回归的路线一 C 主线来自 24 号和路线一文件：

```text
fixed-roll yaw-pitch controlled benchmark；
roll sensitivity 探针；
G1/G3/G5 多几何 OCS 可观测性分析；
OCS/image 互补性；
consistency-as-confidence。
```

后续应重点补回：

```text
F1 单几何总光通量下界；
L1 G1/G3/G5 多几何总光度向量；
image-only 可观测性地图；
OCS-image top-k overlap / disagreement；
entropy / margin / JS divergence；
consistency vs error；
total-only vs per-part semi-oracle 边界；
yaw-block 仅作为 stress test，而非唯一主线。
```

需要避免：

```text
继续让 4维 per-part OCS 代表主线 OCS；
继续让 yaw-block CNN 外推代表整个 1C 成败；
把查库反演写成路线一 C 的原始主线；
把真实 GEO 数据写成监督姿态反演闭环。
```

### 6.4 分支 4：续接后三轴小项目目的

三轴小项目文件定义：

```text
在 yaw / pitch / roll 三轴姿态空间中，
利用路线一 C 的统一前向模型和可观测性指标，
寻找最亮构型、高信息构型、最优可观测姿态和低信息/不值得观测区域，
把路线一基础可观测性研究转化为观测规划价值。
```

它要解决：

```text
哪些 yaw/pitch/roll 姿态最亮、最暗、最容易 glint 或饱和；
哪些姿态虽然亮但信息量低；
哪些姿态不一定最亮但最利于区分；
哪些 sun/view 几何值得观测，哪些不值得。
```

与路线一 C 的关系：

```text
路线一 C 提供 fixed-roll 基础结论、前向模型、OCS/image 指标和可观测性工具；
三轴小项目扩展到 roll-aware 三轴姿态搜索；
路线一 C 的 roll sensitivity 不是三轴小项目替代品，而是接口。
```

与路线二的关系：

```text
路线二提供真实 GEO 光度趋势、分布和多帧多几何现实性锚点；
但不提供三轴姿态真值；
只能用于趋势级/分布级/几何覆盖级对照。
```

## 7. 总结性分析

### 7.1 现在最大的处境不是“单纯负结果”，而是“负结果发生在偏窄协议里”

到目前为止，严格根据结果，确实没有得到稳定的 yaw 反演成功：

```text
C2 OCS-only 接近随机；
C3 image_only 略好但仍不稳定；
C3 joint 与 image_only 基本持平；
B6 fold0 circular regression 没有直接救回 yaw；
粗图像增广在 fold0 下明显破坏结果。
```

但这些结果发生在一个很窄、很强的测试条件中：

```text
single-frame；
fixed-roll；
yaw-block 整段外推；
当前 C2 使用 per-part semi-oracle 4维 OCS；
joint 采用 naive early concat；
B6 初版只有 fold0 pilot。
```

所以现在不能把结论写成“光度无信息、图像无信息、联合无价值”。更准确的状态是：

```text
当前协议下的单帧/固定 roll/整段 yaw 外推没有形成稳定反演；
评价口径确实过严，但失败不只是评价口径问题；
主线所需的多几何总光度向量和置信一致性尚未充分回到实验中心。
```

### 7.2 exact-bin 0% 的性质已经更清楚，但还没有解释完所有失败

现在可以稳定保留两句话：

```text
exact-bin 0% 作为主评价口径太苛刻。
exact-bin 0% 不能证明 yaw 信息完全不存在。
```

同时也必须保留另一半：

```text
relaxed metrics 下 yaw 仍弱；
coarse90 多数接近随机；
yaw-block 异质性很强；
fold0 circular regression 未直接解决 yaw。
```

因此，“评价口径太严格”只能解释一部分处境，不能单独解释全部负结果。当前更像是：

```text
评价口径过严
+ 单帧信息形态偏弱
+ yaw-block 外推协议过强
+ 当前模型/融合方式基础
+ 当前 OCS 输入形态偏离主线
```

共同导致了现在的负结果。

### 7.3 B6 的价值是把“判据/训练头问题”单独关掉或保留，不是关掉路线一 C

B6-FIX01 如果完成 5-fold、best-val/final、fold-matched baseline 后，最有价值的是回答：

```text
72-bin 分类头是不是主要失败原因？
circular regression 能不能稳定改善 yaw 或至少改善 pitch？
当前粗噪声增广是否稳定负面？
```

如果 B6-FIX01 仍然显示 yaw 不改善，它可以支持：

```text
失败不主要是 exact-bin 分类头造成；
single-frame yaw 外推本身可能信息不足；
需要把主线拉回多几何 OCS / consistency / roll sensitivity。
```

但它不能支持：

```text
路线一 C 整体闭口；
OCS 主线失败；
图像-光度融合彻底失败；
三轴小项目没有价值。
```

### 7.4 后续路线一应从“外推模型胜负”复位到“可观测性主线”

目前路线一最需要复位的不是继续讲负结果叙事，而是把实验对象拉回 24 号定义：

```text
F1：单几何总光通量下界；
F2：per-part semi-oracle 诊断；
L1：G1/G3/G5 跨几何多观测总光度向量；
image：空间分辨图像通道；
consistency：OCS 与 image 是否给出一致候选、置信和不确定性；
roll sensitivity：从 fixed-roll 接到三轴小项目。
```

这样路线一才不是“CNN 外推失败记录”，而是回到原始问题：

```text
什么能知道；
什么时候 OCS 和图像互补；
什么时候应该相信估计；
哪些姿态和几何值得观测。
```

### 7.5 光变曲线/光度时序应被保留为后续重要方向，但不能偷换当前主线

作者指出真实数据来源更可能是光变曲线或稀疏光度时序，这一点是重要纠偏。现在应区分三种形态：

```text
单帧单几何总光度：F1，下界；
单帧多几何或跨几何多观测总光度向量：L1，当前主线应补回；
真实时域光变曲线/稀疏 GEO 光度时序：后续真实场景增强层或路线二锚点。
```

因此光度方向可以保留为对比研究框架：

```text
单帧单几何；
单帧/跨观测多几何；
稀疏光度时序或光变曲线。
```

但当前不能把真实 GEO 光度时序写成监督姿态反演闭环，因为路线二数据没有 yaw/pitch/roll 真值。

### 7.6 当前路线一进展的最简图

```text
0. 分析现有结果与最初目的
   已发现当前负结果主要来自 single-frame/fixed-roll/yaw-block/per-part/naive fusion 组合，
   与 24 号 L1 多几何主线存在偏移。

1. 负结果追因
   exact-bin 过严已确认；
   分类头是否主因待 B6-FIX01；
   single-frame 信息不足和 yaw-block 外推过强的可能性上升。

2. 头B进行
   B6-FIX01 正在等待 Claude 补齐；
   它只能闭判据/训练头问题，不能闭路线一 C。

3. 准备回归路线一 C
   应回到 F1/L1/G1/G3/G5、image、consistency、roll sensitivity；
   yaw-block 只作为 stress test。

4. 续接后三轴小项目
   三轴小项目目标是最亮构型、高信息姿态、低信息区域和观测规划；
   需要路线一 C 的 roll sensitivity 和可观测性指标作为接口。
```

## 8. 后续使用规则

后续 Claude/Codex 若涉及以下主题，必须先读本文件：

```text
现有负结果解释；
exact-bin / circular MAE / within-k / coarse-bin 评价口径；
C2 4维 OCS 现实性；
yaw-block 5-fold 外推协议；
B6-FIX01 是否闭口；
路线一 C 是否回归 F1/L1/G1/G3/G5；
光变曲线 / 稀疏 GEO 光度时序；
三轴小项目与路线一 C 的接口。
```

本文件不替代 R104/R105/R106/R108/R109，也不替代后续对 Claude 102 或后续执行报告的审阅。
