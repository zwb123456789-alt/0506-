# Step 2 Claude 指导文件：Introduction 结构与初稿

将本文件完整发送给 Claude。Claude 只执行 Step 2：Introduction，不写 Related Work、Method、Results、Discussion 或完整论文。

## 1. 当前状态

Step 1 已完成返修并通过复审。当前采用的 Step 1 基础文件是：

```text
Claude交互/claude writing/01_Step1_返修版_标题摘要贡献点.md
```

Step 2 任务是基于 Step 1 主线写 Introduction 的结构和初稿。

不要重新讨论标题、摘要、贡献点，除非 Introduction 中需要引用。

## 2. 论文定位

投稿定位：

- 主攻 SCI 二区
- 写作标准按一区边缘标准组织
- 候选期刊：Acta Astronautica / Advances in Space Research / Optics Express / Remote Sensing

论文定位：

> A physically consistent simulation and controlled inversion study that reveals when OCS and photometric images provide complementary attitude constraints under ideal and degraded observation conditions.

更稳妥的 Introduction 表述：

```text
controlled degradation tests
observation-quality variations
idealized clean-image upper-bound
simulation-focused benchmark
```

避免写：

```text
realistic degradation model
field-validated performance
fusion is universally superior
OCS is always stronger than images
```

## 3. Introduction 必须回答的问题

Introduction 要让审稿人明白：

1. 为什么空间目标光学姿态反演重要？
2. OCS/light-curve 与 photometric images 分别提供什么信息？
3. 为什么需要统一 BRDF、几何、姿态、材料和自遮挡框架？
4. 为什么 clean synthetic images 只能视为 image-based inversion 的 upper-bound？
5. 本文如何通过 controlled benchmark 分析 OCS、图像和 fusion 的条件性互补？
6. 本文贡献是什么，边界在哪里？

## 4. 证据边界

Introduction 可以使用少量核心结果，但不能写成 Results。

允许使用：

- ResNet image-only clean：1.69 ± 0.07 deg, Hit@5 = 97.6%
- 1% Gaussian image noise：85.85 ± 3.00 deg, Hit@5 = 2.2%
- OCS MLP per_part_log：5.91 ± 0.22 deg
- ResNet + OCS fusion worst-case：9.9 deg -> 6.6 deg
- OCS-noise fusion gain：+1.97 deg -> +6.29 deg

谨慎使用：

- r = 0.003，只能写为 TinyCNN + OCS MLP diagnostic，不要默认推广到 ResNet
- 13,505 OCS pairs / 2,701 images：可放 present study 中简要提，不要堆数字
- single-geom OCS 相关数值：不要在 Introduction 使用，留给 Results/Ablation

## 5. 推荐 Introduction 结构

请写 5 段。

### Paragraph 1：Field Need and Task Definition

目标：

- 从 space situational awareness / space object characterization / optical observation 进入。
- 定义任务：recover yaw-pitch attitude from scalar OCS signatures and resolved photometric images。
- 不要一开始讲模型或 ResNet。

### Paragraph 2：Two Optical Modalities

目标：

- 介绍 OCS/light curve 和 photometric images 两条光学信息源。
- OCS：low-dimensional, low-cost, interpretable, multi-geometry photometric constraint。
- Images：resolved shape, shadow, silhouette, brightness distribution cues。
- 不要说 OCS 强于图像，也不要说图像强于 OCS。

### Paragraph 3：Technical Gap

目标：

- 指出现有研究通常分开建模 OCS/light curve 和 image-based pose/attitude estimation。
- 关键 gap 是缺少统一物理框架，使两种模态共享 geometry、material、BRDF、attitude、self-occlusion。
- 另一个 gap 是缺少对 ideal clean images、controlled degradation、OCS robustness、conditional fusion 的系统评估。

安全措辞：

```text
typically
often
remain limited
has not been systematically quantified
```

不要写：

```text
no previous work
first
never
state-of-the-art
```

引用先用占位符：

```text
[CITATION: BRDF-based space object photometry]
[CITATION: optical light-curve inversion]
[CITATION: image-based spacecraft pose estimation]
[CITATION: multi-modal fusion robustness]
```

### Paragraph 4：Present Study and Key Insight

目标：

- 介绍 unified BRDF-driven simulation and controlled inversion benchmark。
- 说明同一 STL geometry、nonuniform GGX/Cook-Torrance BRDF、ray-traced self-occlusion、OCS and photometric image generation。
- 简要说明比较 OCS-only、image-only、late fusion、feature fusion。
- 用 2-3 个核心结果预告主发现。

建议只写：

```text
Clean ResNet reaches 1.69 ± 0.07 deg under idealized images but degrades to 85.85 deg under 1% Gaussian noise.
OCS-only inversion provides a 5.91 deg controlled benchmark constraint.
Fusion improves selected tail errors from 9.9 deg to 6.6 deg.
```

不要把所有结果和消融都塞进 Introduction。

### Paragraph 5：Contributions and Boundary

目标：

用 4 条贡献收束：

1. Unified physical forward model
2. Controlled attitude inversion benchmark
3. Clean-image upper bound and fragility
4. Robust OCS and conditional fusion

最后用 1-2 句写边界：

```text
The study is simulation-focused and does not include real optical telescope validation.
The current benchmark estimates yaw-pitch under fixed roll.
```

不要让 limitation 变成自毁，语气要稳：

```text
These boundaries make the benchmark controlled and interpretable, while motivating future field validation.
```

## 6. 输出要求

请按以下结构输出：

```text
1. Introduction Logic Map
2. Paragraph Plan
3. Version A: Conservative Reviewer-Safe Introduction
4. Version B: Balanced Submission Introduction
5. Recommended Version and Rationale
6. Claim-Evidence-Risk Map for Introduction
7. Citation Placeholder List
8. Self-review Checklist
9. Author Check Items
```

## 7. 两个版本要求

### Version A: Conservative Reviewer-Safe Introduction

特点：

- 更强调 controlled simulation benchmark。
- 更主动处理 no real optical validation。
- 适合 ASR / Acta Astronautica 保守审稿路线。

长度：

- 700-950 English words。

### Version B: Balanced Submission Introduction

特点：

- 更突出 conditional complementarity。
- 保持边界，但主线更有冲击力。
- 推荐作为后续主稿基础。

长度：

- 700-950 English words。

## 8. Self-review Checklist

输出末尾必须逐条回答：

1. Did the Introduction avoid claiming real optical validation?
2. Did it frame clean images as an upper bound?
3. Did it avoid saying fusion is universally best?
4. Did it explain why a unified BRDF-driven model is needed?
5. Did it clearly separate OCS and image strengths?
6. Did it keep detailed numbers mostly out of the Introduction?
7. Did it use citation placeholders instead of invented references?
8. Did it state fixed roll / yaw-pitch boundary without overemphasizing weakness?
9. Did it avoid using r=0.003 as ResNet evidence?

