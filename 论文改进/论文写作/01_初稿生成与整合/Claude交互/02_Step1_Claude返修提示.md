# Step 1 Claude 返修提示：标题、摘要骨架与贡献点

将本文件发送给 Claude，让它基于上一版 `01_Step1_输出_标题摘要贡献点.md` 做轻量返修。不要重写全部内容，只修正以下问题。

## 1. 当前判断

上一版整体可用，主线正确：

- 已把论文定位为 physically consistent simulation and controlled inversion study。
- 已承认 clean synthetic image 是 upper-bound。
- 已避免 “OCS 主力、图像辅助、fusion 永远最优” 的旧叙事。
- 已明确 no real optical telescope validation。
- 标题、核心科学问题、贡献点结构基本适合作为 Step 1 基础。

本轮目标不是重做 Step 1，而是降调、核验和收紧表述，使其更适合后续 Introduction / Abstract。

## 2. 必须修改的问题

### 2.1 降调 “realistic degradation”

上一版多处使用 “realistic degradation”。当前证据主要是：

- 1% Gaussian image noise
- brightness scaling

这些是受控退化测试，不能等同完整真实观测退化模型。

请改为以下更稳妥表达：

```text
simple image degradation tests motivated by realistic observation artifacts
```

或：

```text
controlled image degradation tests
```

不要写成：

```text
realistic degradation model
field observation degradation has been fully modeled
```

### 2.2 摘要骨架不要塞入过多细节数值

上一版 Abstract Skeleton Sentence 4 写了：

```text
improves Hit@5° to 99.7%
```

这个数值有补充实验来源，但在摘要骨架阶段太细。请改成更稳的写法：

```text
incorporating multi-geometry OCS features further improves tail errors, reducing the worst-case error from 9.9° to 6.6°.
```

`Hit@5 = 99.7%` 可以移动到 Results candidate evidence 或 Table 2，不要作为摘要骨架主句。

### 2.3 brightness ×0.5 = 3.45° 不放入贡献点主证据

上一版 Contribution 3 写了：

```text
brightness ×0.5: 3.45°
```

该结果可作为 robustness subsection 的补充，但不是 Step 1 核心证据。请把它移到 “candidate secondary evidence” 或删除。

Contribution 3 的主证据只保留：

```text
ResNet-18 clean: 1.69 ± 0.07°, Hit@5 = 97.6%
1% Gaussian noise: 85.85 ± 3.00°, Hit@5 = 2.2%
```

### 2.4 明确 r = 0.003 的来源

上一版使用了：

```text
OCS-image error correlation r = 0.003
```

必须明确：

```text
This correlation was measured in the earlier TinyCNN + OCS MLP diagnostic, not yet for the ResNet pair.
```

不要默认推广到 ResNet + OCS。

### 2.5 OCS robustness 表述要限定在 simulation

上一版类似写法：

```text
OCS remains robust at 5.91° regardless of image quality
```

请改为：

```text
In the controlled simulation, the OCS-only result is unaffected by image degradation because it does not depend on image inputs.
```

并补一句边界：

```text
Real OCS measurements would still be affected by photometric calibration errors and sensor noise.
```

### 2.6 Claim map 中单几何 OCS 数值放到候选证据

上一版 Claim 2 中写：

```text
Single-geom total OCS: mean=79°; concat5 total: mean=26.5°; concat5 all MLP: 3.98°
```

这些内容可保留，但请加边界：

```text
These values should be used in Results/Ablation rather than the Abstract.
```

另外 `all_raw 45D = 3.98°` 必须继续标注为 semi-oracle upper bound。

## 3. 需要保留的内容

请保留上一版中的以下优点：

1. Manuscript Positioning 的总体结构。
2. Core Scientific Question 的 conditional complementarity 写法。
3. Contribution 1-4 的四条结构。
4. Reviewer-Risk Notes 的五类风险。
5. No real optical validation 的明确边界。
6. Fixed roll / phase63 / nominal material parameters 的 limitation。

## 4. 推荐标题处理

请在返修版中给出一个 “recommended title”。

优先考虑以下两个方向：

```text
BRDF-Driven Optical Cross Section and Photometric Image Simulation for Space Object Attitude Inversion: A Controlled Benchmark Study
```

或：

```text
Robustness and Complementarity of Optical Cross Section and Photometric Images for Space Object Attitude Inversion: A BRDF-Consistent Simulation Study
```

如果标题过长，请提供一个压缩版。

## 5. 返修输出格式

请只输出返修后的关键部分，不要重写所有解释性文本。

输出结构：

```text
1. Revised Recommended Title
2. Revised Manuscript Positioning
3. Revised One-Sentence Argument
4. Revised Abstract Skeleton
5. Revised Contributions
6. Revised Claim-Evidence-Boundary Notes
7. Remaining Author-Check Items
```

## 6. 返修质量标准

返修后应满足：

1. 不把 clean image 结果写成真实场景性能。
2. 不把 Gaussian noise/brightness test 写成完整真实退化模型。
3. 不把 fusion 写成永远最优。
4. 不把 OCS 写成总是强于图像。
5. 不把 r=0.003 默认推广到 ResNet。
6. Abstract skeleton 控制在核心证据，不堆过多 Results 细节。

