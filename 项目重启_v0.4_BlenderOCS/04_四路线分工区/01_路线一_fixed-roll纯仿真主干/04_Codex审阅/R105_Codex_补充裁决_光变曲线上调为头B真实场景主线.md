# R105 Codex 补充裁决：光变曲线上调为头B真实场景主线

最后更新：2026-06-29
审阅端：Codex
性质：对 R104 的补充裁决，不替代 R104。

关联文件：

```text
R104_Codex_审阅_100通过_头B转入A类同门真改进阶段.md
R93_Codex_PDF精读确认_1C-B2相关方法可采纳性.md
R91_Codex_文献检索_1C-B1六方向方法约束与PDF入库.md
```

## 0. 补充裁决

```text
接受作者判断：
若后续真实数据来源主要是随时间采样的光度观测，那么 light-curve sequence / 多几何光变曲线不应只是远期备选，
而应上调为头B面向真实场景的核心主线之一。
```

但执行顺序仍需分层：

```text
1. B6 仍先做：continuous/circular regression + 图像噪声/增广。
2. B6 不是最终目标，而是清理低成本混杂项：判据是否人为放大失败、干净图像是否造成伪捷径。
3. B6 后，若单帧仍失败或只局部改善，则 T3 light-curve sequence 不得再被轻易“future work”化；
   它应进入头B后续主阶段门。
```

一句话：

```text
单帧 OCS 是 lower information layer / 诊断下界；
光变曲线才更接近真实光度数据形态和后续可用系统形态。
```

## 1. 为什么光变曲线应上调

### 1.1 真实数据形态更接近时间序列

若真实观测来自光度测量，通常不是“某个姿态下一个孤立 OCS 标量”，而是：

```text
多时刻亮度；
目标姿态随时间演化；
太阳-目标-观测者几何随时间变化；
噪声、遮挡、相位角、采样间隔共同影响观测。
```

因此，单帧 OCS/单帧图像更适合作为 controlled benchmark 或 lower bound，不应被当作真实光度反演的最终信息形态。

### 1.2 单帧 yaw 歧义可能是信息形态问题

当前 v0.4 的 yaw-block 外推失败，可能同时来自：

```text
判据过硬；
训练协议外推；
单帧信息不足；
几何覆盖不足；
朴素 fusion 结构不足。
```

其中“单帧信息不足/几何覆盖不足”不能靠换 loss 完全解决。光变曲线通过时间演化和多几何覆盖，才有可能打破单帧下的近似等价解簇。

## 2. 文献依据

R91/R93 已经给出足够依据，不能把 light-curve sequence 当作凭空设想。

```text
Kaasalainen 2001 I/II：
  光变反演核心依赖多几何 lightcurves、约束和对歧义的克制；
  多几何覆盖比单纯样本点数更重要。

Wetterer & Jah 2009：
  使用 light curve time history + facet forward model + UKF；
  near-identical light curves 与姿态可观测性问题直接相关。

Kumar 2025：
  支撑 SSA 场景中 light curve sequential comparison 与 digital twin 对照思想。

Tang 2025：
  支撑光变数据 + 深度模型作为候选路线，但不支持当前直接换强 backbone。

Gerwe & Idell 2003：
  支撑 Fisher/CRLB/可观测性语言，但提示完整理论下界需要噪声和测量模型，不能轻率做强结论。
```

由此形成的边界：

```text
可以说：单帧 OCS 是光变曲线信息链的低信息下界。
可以说：正式 light-curve sequence 是更贴近真实光度数据的后续主线。
不能说：当前单帧负结果证明光度通道无用。
不能说：光变曲线一定唯一反演姿态。
不能说：v0.3/v0.4 合成结果已经等于真实光变验证。
```

## 3. 对 R104 路线的修正

R104 中 T1/T1'/T2/T3 的顺序保留，但 T3 的定位修正如下：

```text
原定位：
  T3 = 暂缓、最重门、满足条件后再开。

补充后定位：
  T3 = 面向真实数据适配性的核心主线；
       执行上仍是重门，但战略上不应被降级为可有可无的 future work。
```

B6 的意义也相应改写：

```text
B6 不是为了证明单帧路线就是最终路线；
B6 是为了在进入 light-curve sequence 前，先排除两个廉价混杂因素：
  1. exact-bin 分类判据是否人为制造了 0%；
  2. 干净图像/无增广是否放大了外推失败。
```

## 4. T3 进入条件

B6 后，若出现以下任一情况，应启动 T3 阶段门准备：

```text
1. circular regression 后 yaw-block 仍严重失败；
2. regression 只在少数 block 改善，整体仍不可用；
3. noise/augmentation 只能改善图像鲁棒性，不能解决 yaw 外推；
4. non-naive fusion 仍不能证明单帧 image+OCS 互补；
5. 作者确认真实数据主来源为光变曲线序列，而非单帧 OCS/图像。
```

特别是第 5 条成立时，T3 不应等待所有轻量枝节都做完；可以在 B6 后并行准备协议，但正式新渲染/新数据仍需另设阶段门。

## 5. T3 最低技术设计要求

正式 light-curve sequence 阶段门必须预注册：

```text
1. 数据形态：
   - 多时刻光度序列；
   - 多几何或随时间变化几何；
   - 是否包含图像帧，或仅光度序列。

2. 物理协议：
   - 姿态演化模型；
   - 太阳/观测者几何采样；
   - BRDF/OCS 前向模型；
   - 噪声、遮挡、相位角、采样间隔。

3. split 协议：
   - train/test yaw-block 是否保留；
   - 是否按序列级划分，而不是帧级泄漏；
   - 防止同一姿态轨迹的近邻泄漏。

4. 模型：
   - single-frame baseline；
   - simple temporal pooling；
   - 1D-CNN / LSTM / Transformer 等序列模型；
   - 必须有可分离消融。

5. 指标：
   - circular MAE；
   - Hit@5/10；
   - yaw-block 分层；
   - 轨迹级指标；
   - 与 single-frame lower bound 的边际增益。

6. inverse-crime 防护：
   - 不得只用完全同分布、无噪声、无退化的生成-反演闭环来声称真实可用；
   - 必须显式列出噪声/退化/几何扰动。
```

## 6. 对头B结束条件的补充

R104 的头B结束条件保留，但增加真实数据主线约束：

```text
若作者确认真实数据主要是 light-curve sequence，
则仅靠单帧 B6 成功，不足以声称“真实场景路线已解决”。
```

更精确的收口口径为：

```text
B6 成功：
  可以收口“单帧 benchmark 的判据/训练口径问题”；
  T3 可作为真实数据适配的下一阶段主线，而不是普通 future work。

B6 失败：
  必须进入 T2/T3 裁定；
  若真实数据主来源为光变曲线，则 T3 优先级高于单纯 backbone 升级。

T3 成功：
  头B获得更接近真实光度数据形态的正向方法贡献。

T3 失败：
  负结果才更有资格写成在当前受控协议与序列信息形态下仍然 robust。
```

## 7. 给后续任务的短提示

```text
请在执行 R104 的 1C-B6 时同步记录：
B6 是进入 light-curve sequence 前的低成本混杂项清理，不是单帧路线最终裁决。

B6 后若 yaw-block 仍失败，或若作者确认真实数据以光变曲线为主，
下一阶段应准备 T3 light-curve sequence 阶段门：
多时刻/多几何光度序列、序列级 split、防泄漏、噪声/退化/inverse-crime 防护、
single-frame vs sequence 的边际增益对照。
```

