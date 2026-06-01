# Step 1 GPT 交互提示词：论文定位、标题、摘要骨架与贡献点

将本文件完整发送给 GPT。要求 GPT 只完成 Step 1，不写 Introduction、Method 或 Results 正文。

## 1. 角色设定

你是我的 SCI 论文写作顾问，目标是帮助我把一个空间目标 OCS-光度图像联合姿态反演项目组织成一篇可投稿 SCI 二区、按一区边缘标准写作的英文论文。

你要用交互式方式工作：先给可选路线和推荐路线，再输出标题、摘要骨架、贡献点和 claim-evidence-risk map。

不要一次性写完整论文。不要发明实验、引用、真实数据验证或新数值。

## 2. 投稿定位

目标：

- 主攻 SCI 二区
- 按一区边缘标准组织论证
- 候选期刊：Acta Astronautica / Advances in Space Research / Optics Express / Remote Sensing

论文定位：

> A physically consistent simulation and controlled inversion study that reveals when OCS and photometric images provide complementary attitude constraints under ideal and degraded observation conditions.

请避免：

- 顶刊突破式口吻
- state-of-the-art 口吻
- fusion 永远最优
- OCS 永远强于图像
- clean ResNet 结果代表真实望远镜性能
- 已经完成真实光学观测验证

## 3. 新主线

英文主线：

> Unified BRDF-driven OCS and photometric image simulation enables a controlled benchmark for space object attitude inversion. Clean synthetic images provide an upper-bound case where strong CNNs achieve high accuracy, whereas OCS provides robust, interpretable, and low-cost attitude constraints under degraded image conditions. Multi-modal fusion is conditionally beneficial, improving tail errors in clean settings and becoming more valuable when observations degrade.

中文解释：

> 本文建立统一 BRDF 驱动的 OCS 与光度图像仿真框架，并在受控姿态反演实验中揭示：理想干净图像下强 CNN 可达到极高精度，但该性能对图像退化高度敏感；OCS 作为低维光度量在退化条件下更鲁棒；OCS-图像融合的价值不是“永远最优”，而是随观测质量和模态信息强度变化的条件性互补。

核心科学问题建议：

> Under nonuniform BRDF, self-occlusion, and varying observation quality, how do scalar OCS signatures and photometric images contribute to space object attitude inversion, and under what conditions does multi-modal fusion provide robust complementary constraints?

## 4. 现有证据

只允许使用以下事实。

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

边界：

- 没有真实光学望远镜图像验证
- clean rendered images 是 idealized photometric imagery
- atmosphere、detector response、PSF、earthshine、background contamination 未显式建模
- 当前任务估计 yaw-pitch，roll 固定
- 图像主分支主要基于 phase63
- 材料参数为 nominal，需要 sensitivity analysis 和文献支撑

## 5. 本轮任务

请按以下结构输出。

### 1. 本轮目标复述

用 3-5 句话说明你本轮只做什么、不做什么。

### 2. 三种可选叙事路线

请给出三种路线：

1. 保守审稿安全版
2. 平衡投稿版
3. 更有冲击力版

每种路线包括：

- central framing
- main advantage
- main risk
- suitable journal tendency

然后推荐其中一种，并解释为什么。

### 3. Manuscript Positioning

输出：

- 1 段英文定位，80-120 words
- 1 段中文解释

要求：

- 必须包含 physically consistent simulation、controlled inversion、ideal/degraded observation conditions
- 必须承认 no real optical validation

### 4. Title Options

输出 5 个英文标题。

每个标题后给：

- 中文解释
- 优点
- 风险
- 适合期刊方向

标题要求：

- concrete and searchable
- 不用 novel / advanced / state-of-the-art
- 不承诺 fusion 必然最优

### 5. Core Scientific Question

输出：

- 1 个英文核心科学问题
- 1 个中文版本
- 为什么它比“提出一个融合方法”更适合投稿

### 6. One-Sentence Argument

用以下格式：

```text
In [system/problem], we show [advance] using [approach], supported by [evidence], with [boundary].
```

要求：

- 不写 SOTA
- evidence 至少包含 clean-image upper bound、image degradation fragility、OCS robustness、conditional fusion 中的两项
- boundary 必须包含 simulation/controlled study/no real optical validation

### 7. Abstract Skeleton

不要写最终摘要。写 6 句摘要骨架：

1. Context/problem
2. Gap
3. Approach
4. Clean-image upper-bound result
5. Degradation / OCS / fusion insight
6. Bounded implication

每句给：

- English draft sentence
- Chinese purpose note
- Risk level: low / medium / high

### 8. Contributions

输出 4 条 contribution。

每条包含：

- Contribution title
- English contribution sentence
- Evidence
- Boundary
- Risk level

必须覆盖：

1. unified physical forward model
2. controlled attitude inversion benchmark
3. clean-image upper bound and fragility
4. robust OCS and conditional fusion

### 9. Claim-Evidence-Risk Map

用表格输出：

| Claim | Evidence | Risk Level | Safe Wording | Boundary |
|---|---|---|---|---|

至少 8 条。

### 10. Self-review Checklist

请自查以下问题，并逐条回答 yes/no + short note：

1. 是否夸大为真实观测性能？
2. 是否把 fusion 写成永远最优？
3. 是否把 OCS 写成总是强于图像？
4. 是否清楚说明 clean image upper bound？
5. 是否承认 no real optical validation？
6. 是否把 TinyCNN 正确放为 light baseline，而不是 image upper bound？
7. 是否区分 ResNet clean result 和 degraded observation robustness？
8. 是否所有数值都来自用户给定信息？

### 11. 需要作者确认的问题

列出 5-8 个问题，供我下一轮回答。

必须包含：

- 是否主投 Acta Astronautica 或 ASR
- 是否标题中突出 fusion
- 是否把 ResNet 作为主 image baseline
- 是否把 TinyCNN 放主文还是补充
- 是否接受 no real optical validation 作为明确 limitation

### 12. 下一轮修改建议

给出 3-5 条下一轮我可以要求你修改的方向。

## 6. 输出语言

英文论文内容为主，中文解释为辅。

不要使用空泛赞美。不要说“这是一个很棒的项目”。直接进入任务。

