# Step 1 指导文件：论文定位、标题、摘要骨架与贡献点

将本文件完整交给 Claude。Claude 只执行 Step 1，不写 Introduction、Method 或 Results 正文。

## 1. 你的角色

你是一个面向 SCI 二区、按一区边缘标准组织论文的学术写作助手。你的任务是基于作者已经完成的 OCS-光度图像联合姿态反演项目，先定稿论文主线、标题、摘要骨架和贡献点。

不要写完整论文正文。不要扩展实验。不要创造引用、数值或真实数据验证。

## 2. 投稿档次

目标：

- 主攻 SCI 二区
- 写作质量按一区边缘标准
- 推荐方向：Acta Astronautica / Advances in Space Research / Optics Express / Remote Sensing

定位：

> A physically consistent simulation and controlled inversion study that reveals when OCS and photometric images provide complementary attitude constraints under ideal and degraded observation conditions.

不要写成：

- 顶刊突破
- 真实观测已经验证
- fusion 永远最好
- OCS 永远比图像强
- ResNet 结果代表真实场景性能

## 3. 必须采用的新主线

英文主线：

> Unified BRDF-driven OCS and photometric image simulation enables a controlled benchmark for space object attitude inversion. Clean synthetic images provide an upper-bound case where strong CNNs achieve high accuracy, whereas OCS provides robust, interpretable, and low-cost attitude constraints under degraded image conditions. Multi-modal fusion is conditionally beneficial, improving tail errors in clean settings and becoming more valuable when observations degrade.

中文主线：

> 本文建立统一 BRDF 驱动的 OCS 与光度图像仿真框架，并在受控姿态反演实验中揭示：理想干净图像下强 CNN 可达到极高精度，但该性能对图像退化高度敏感；OCS 作为低维光度量在退化条件下更鲁棒；OCS-图像融合的价值不是“永远最优”，而是随观测质量和模态信息强度变化的条件性互补。

核心科学问题建议写成：

> Under nonuniform BRDF, self-occlusion, and varying observation quality, how do scalar OCS signatures and photometric images contribute to space object attitude inversion, and under what conditions does multi-modal fusion provide robust complementary constraints?

## 4. 已有证据与可用数值

只允许使用以下已给出事实和数值。

物理建模链条：

- 真实卫星 STL 几何
- 非均匀材料分区
- GGX/Cook-Torrance BRDF
- 解析射线自遮挡
- 多观测几何 OCS 扫描
- 光度图像渲染
- yaw-pitch 姿态反演，fixed roll
- OCS-only / image-only / late fusion / feature fusion

核心结果：

- ResNet image-only clean：1.69 ± 0.07 deg, Hit@5 = 97.6%
- ResNet + concat5 per_part_log：1.47 ± 0.07 deg
- worst-case：9.9 deg -> 6.6 deg
- 1% Gaussian image noise：ResNet 退化到 85.85 deg, Hit@5 = 2.2%
- OCS MLP per_part_log：5.91 deg，作为实用 OCS-only 结果
- OCS MLP all_raw 45D：3.98 ± 0.60 deg, Hit@5 = 90.7%，只能写成 semi-oracle 上界
- TinyCNN image-only：12.38 ± 0.74 deg, Hit@5 = 26.1%，只能作为轻量 CNN baseline
- Early feature fusion per_part_log：4.10 ± 0.77 deg, Hit@5 = 87.3%
- OCS-CNN 误差相关性 r = 0.003
- OCS-noise fusion gain 从 +1.97 deg 增至 +6.29 deg，随 OCS noise 0% 到 20% 增加

重要边界：

- 没有真实光学望远镜图像验证
- clean rendered images 是 idealized photometric imagery
- atmosphere、detector response、PSF、earthshine、background contamination 未显式建模
- 当前任务估计 yaw-pitch，roll 固定
- 图像主分支主要基于 phase63
- 材料参数为 nominal，需要 sensitivity analysis 和文献支撑

## 5. 必须避免的旧叙事

不要写：

```text
OCS is the primary sensor and images are only auxiliary.
Feature fusion is always the best method.
TinyCNN image-only represents the capability of image-based inversion.
The method is directly applicable to real telescope images.
The ResNet result demonstrates real-world image-based attitude accuracy.
```

正确写法：

```text
The clean-image result represents an upper-bound condition for image-based inversion, not a direct estimate of field performance.
OCS is not the performance upper bound when high-quality resolved photometric images are available; its value lies in robustness, interpretability, low acquisition cost, and multi-geometry availability.
Fusion provides conditional benefits: it improves tail errors under clean images and provides robustness when one modality is degraded.
```

## 6. 本阶段输出任务

请按以下顺序输出。

### 6.1 Manuscript Positioning

输出：

- 1 段英文定位，80-120 words
- 1 段中文解释，说明为什么该定位适合 SCI 二区、一区边缘标准

要求：

- 必须包含 physically consistent simulation、controlled inversion、ideal and degraded observation conditions
- 必须承认没有 real optical validation

### 6.2 Title Options

输出 5 个英文标题。

要求：

- 标题要 concrete and searchable
- 包含 OCS / photometric image / BRDF / attitude inversion 中至少两个核心元素
- 不要使用 `novel`、`advanced`、`state-of-the-art`
- 不要承诺 fusion 必然最优

请给每个标题一句中文评价，说明优点和风险。

可参考但不要机械照抄：

```text
BRDF-Driven Optical Cross Section and Photometric Image Simulation for Robust Space Object Attitude Inversion
A Unified Simulation Framework for OCS-Image Attitude Estimation of Space Objects under Nonuniform BRDF and Self-Occlusion
When Does OCS-Image Fusion Help? A BRDF-Driven Benchmark for Space Object Attitude Inversion
Conditional Complementarity of Optical Cross Section and Photometric Images for Space Object Attitude Inversion
```

### 6.3 Core Scientific Question

输出：

- 1 个英文核心科学问题
- 1 个中文版本
- 1 句解释：为什么这个问题比“提出一个融合方法”更适合投稿

### 6.4 One-Sentence Argument

用以下格式输出全文论证链：

```text
In [system/problem], we show [advance] using [approach], supported by [evidence], with [boundary].
```

要求：

- `advance` 不能写成 SOTA
- `evidence` 必须包含 clean-image upper bound、image degradation fragility、OCS robustness 或 conditional fusion 中至少两项
- `boundary` 必须包含 simulation/controlled study/no real optical validation

### 6.5 Abstract Skeleton

不要写最终摘要。只写 6 句摘要骨架，每句说明功能和建议内容。

结构：

1. Context/problem
2. Gap
3. Approach
4. Clean-image upper-bound result
5. Degradation / OCS / fusion insight
6. Bounded implication

每句先给英文草句，再给中文说明。

### 6.6 Contributions

输出 4 条 contribution，每条包括：

- Contribution title
- 1 句英文贡献表述
- 对应证据
- 边界/不能夸大的地方

贡献必须覆盖：

1. unified physical forward model
2. controlled attitude inversion benchmark
3. clean-image upper bound and fragility
4. robust OCS and conditional fusion

### 6.7 Claim-Evidence Map

用表格输出：

| Claim | Evidence | Supported? | Boundary |
|---|---|---|---|

至少包含 8 条 claim。

### 6.8 Reviewer-Risk Notes

输出 5 条最可能的审稿风险，每条包括：

- Risk
- Why it matters
- How the manuscript should handle it

必须包含：

- no real optical validation
- clean synthetic image upper bound
- fixed roll
- phase63 image branch
- nominal material parameters

## 7. 输出格式要求

使用英文为主，中文解释为辅。

最终结构必须是：

```text
1. Manuscript Positioning
2. Title Options
3. Core Scientific Question
4. One-Sentence Argument
5. Abstract Skeleton
6. Contributions
7. Claim-Evidence Map
8. Reviewer-Risk Notes
9. Items for Author Check
```

最后的 `Items for Author Check` 必须列出作者需要确认的 5-8 个问题，例如：

- 是否确定主投 Acta Astronautica 或 ASR
- 是否将 ResNet 作为主图像 baseline
- 是否把 TinyCNN 放入补充或主文
- 是否在标题中突出 fusion
- 是否接受 no real optical validation 的边界声明

