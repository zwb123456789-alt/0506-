# Step 2 GPT 交互提示词：Introduction 结构与初稿

将本文件完整发送给 GPT。要求 GPT 只完成 Step 2：Introduction，不写 Related Work、Method、Results、Discussion 或完整论文。

## 1. 当前背景

你已经完成 Step 1：论文定位、标题、摘要骨架与贡献点。现在进入 Step 2：Introduction。

论文定位保持不变：

> A physically consistent simulation and controlled inversion study that reveals when OCS and photometric images provide complementary attitude constraints under ideal and degraded observation conditions.

推荐叙事路线：

> 平衡投稿版：A unified BRDF-driven OCS-image simulation framework that reveals conditional complementarity between scalar photometric signatures and clean/degraded photometric images for space object attitude inversion.

不要改写论文主线，不要扩展新实验。

## 2. Step 1 已确认的核心边界

必须保留：

- 主攻 SCI 二区，按一区边缘标准组织。
- 没有真实光学望远镜图像验证。
- clean synthetic image result 是 idealized upper-bound，不代表 field performance。
- fusion 是 conditional complementarity，不是 universal superiority。
- OCS 的价值是 low-cost、interpretable、multi-geometry、robust photometric constraint。
- 当前任务是 yaw-pitch inversion under fixed roll。
- 图像主分支主要基于 phase63。
- 材料参数为 nominal。
- ISAR 不进入论文主线。

## 3. 可用证据

只允许使用以下事实和数值：

- 真实卫星 STL 几何
- 非均匀材料分区
- GGX/Cook-Torrance BRDF
- 解析射线自遮挡
- 多观测几何 OCS 扫描
- 光度图像渲染
- OCS-only / image-only / late fusion / feature fusion
- ResNet image-only clean：1.69 ± 0.07 deg, Hit@5 = 97.6%
- ResNet + concat5 per_part_log：1.47 ± 0.07 deg
- worst-case：9.9 deg -> 6.6 deg
- 1% Gaussian image noise：ResNet 退化到 85.85 deg, Hit@5 = 2.2%
- OCS MLP per_part_log：5.91 deg
- OCS MLP all_raw 45D：3.98 ± 0.60 deg, Hit@5 = 90.7%，只能作为 semi-oracle upper bound
- TinyCNN image-only：12.38 ± 0.74 deg, Hit@5 = 26.1%，只能作为 lightweight baseline
- Early feature fusion per_part_log：4.10 ± 0.77 deg, Hit@5 = 87.3%
- OCS-CNN error correlation r = 0.003，但必须标注它来自早期 TinyCNN/OCS diagnostic，不默认代表 ResNet pair
- OCS-noise fusion gain 从 +1.97 deg 增至 +6.29 deg，随 OCS noise 0% 到 20% 增加

## 4. Introduction 目标

Introduction 要回答：

1. 为什么空间目标光学姿态反演重要？
2. 为什么 OCS/light-curve 和 photometric images 都有价值？
3. 为什么现有研究如果不统一 BRDF、几何、姿态和遮挡，就难以公平判断两种模态何时互补？
4. 为什么 clean image 结果只能看作 image-based inversion 的 optimistic upper bound？
5. 本文具体做了什么？
6. 本文贡献是什么，边界在哪里？

## 5. 推荐 Introduction 漏斗结构

请按 5 段结构写。

### Paragraph 1：Field Need and Task Definition

任务：

- 引入 space situational awareness / space object characterization / optical attitude inversion。
- 定义本文任务：recover yaw-pitch attitude from OCS signatures and photometric images。
- 不要一上来讲神经网络。

应包含：

```text
Space object attitude estimation from optical observations is important for ...
This study focuses on yaw-pitch attitude inversion from scalar OCS signatures and resolved photometric images.
```

### Paragraph 2：Two Optical Modalities and Their Separate Strengths

任务：

- 介绍 OCS/light curve 和 photometric images 两条路线。
- OCS：low-dimensional、low-cost、multi-geometry、interpretable。
- Images：resolved spatial cues、shape/shadow/brightness distribution。
- 不要说谁天然更强。

### Paragraph 3：Technical Gap

任务：

- 指出现有工作常常分开处理 OCS 与图像。
- 缺少 unified BRDF-driven framework，使两者共享 geometry、attitude、material、BRDF、self-occlusion。
- 缺少对 ideal clean images vs controlled degradation 下 conditional complementarity 的系统分析。

注意：

- 不要写 “no prior work has ever...”。
- 用 `typically`、`often`、`remain limited` 等安全措辞。
- 引用先用占位符 `[CITATION: ...]`，不要发明文献。

### Paragraph 4：Present Study

任务：

- 介绍本文建立 unified BRDF-driven simulation and controlled inversion benchmark。
- 写清同一 STL geometry、nonuniform material、GGX/Cook-Torrance BRDF、self-occlusion。
- 写清比较 OCS-only、image-only、late fusion、feature fusion。
- 简要预告关键发现：clean ResNet upper bound、noise fragility、OCS robustness、conditional fusion。

注意：

- 结果不要堆太多数字。
- 最多放 2-3 个核心数字。
- 不要把所有 Results 写进 Introduction。

### Paragraph 5：Contributions and Boundary

任务：

- 用 4 条 contribution 收束。
- 最后一两句写 boundary：simulation-focused、no real optical validation、fixed roll/yaw-pitch benchmark。

四条 contribution：

1. unified physical forward model
2. controlled attitude inversion benchmark
3. clean-image upper bound and fragility
4. robust OCS and conditional fusion

## 6. 本轮输出要求

请按以下结构输出：

```text
1. Introduction Logic Map
2. Paragraph Plan
3. Version A: Conservative Reviewer-Safe Introduction
4. Version B: Balanced Submission Introduction
5. Recommended Version and Why
6. Claim-Evidence-Risk Map for Introduction
7. Citation Placeholders Needed
8. Self-review Checklist
9. Questions for Author
```

## 7. 写作细节要求

### 7.1 版本要求

请输出两个版本：

**Version A: Conservative Reviewer-Safe Introduction**

- 更强调 controlled simulation benchmark。
- 更主动承认 no real validation。
- 适合 ASR / Acta Astronautica 保守路线。

**Version B: Balanced Submission Introduction**

- 更突出 conditional complementarity。
- 保持边界，但语言更有论文主线冲击力。
- 推荐作为主稿基础。

### 7.2 长度

每个 Introduction 版本控制在 700-950 English words。

### 7.3 引用

不要发明真实引用。用占位符：

```text
[CITATION: optical light-curve attitude inversion]
[CITATION: BRDF-based space object photometry]
[CITATION: image-based spacecraft pose estimation]
[CITATION: multi-modal fusion robustness]
```

### 7.4 禁止事项

不要写：

```text
This is the first work ...
state-of-the-art
real-world validated
fusion consistently outperforms all methods
OCS is superior to images
ResNet result demonstrates field performance
```

不要把 `r=0.003` 默认说成 ResNet 的错误相关性。若使用，必须写：

```text
In an earlier TinyCNN/OCS diagnostic, the near-zero error correlation suggested complementary failure modes.
```

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

