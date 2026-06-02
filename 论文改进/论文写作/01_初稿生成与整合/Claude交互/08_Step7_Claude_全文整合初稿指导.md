# Step 7 Claude 指导文件：全文整合初稿与一致性自检

> 使用对象：Claude  
> 当前任务：将 Step 1-6 的 Claude 阶段输出整合成一版连续英文 manuscript draft，并完成跨章节一致性、证据边界和待确认项自检。  
> 输出建议保存为：`claude writing/07_Step7_Claude输出_全文整合初稿.md`

---

## 0. 当前论文定位

论文主题：

> BRDF-driven optical cross section and photometric image simulation for robust space object attitude inversion.

中文定位：

> 基于统一 BRDF 与自遮挡建模的 OCS-光度图像姿态反演基准研究，重点分析理想图像上限、图像退化脆弱性与 OCS 鲁棒互补价值。

目标档次：

- 主攻 SCI 二区
- 按 SCI 一区边缘标准组织论证
- 候选期刊：Acta Astronautica / Advances in Space Research / Optics Express / Remote Sensing

Step 7 的核心任务：

> 把 Step 1-6 分散产物整合为一版可通读的英文论文初稿。重点是统一叙事、删减重复、统一术语、保留边界、标注待确认项。不要重新发明结果，也不要把每一步原文机械拼接成冗长稿。

---

## 1. 必须读取并整合的输入文件

请按顺序读取以下文件：

```text
claude writing/01_Step1_返修版_标题摘要贡献点.md
claude writing/02_Step2_Introduction初稿.md
claude writing/03_Step3_Claude输出_RelatedWork_Table1.md
claude writing/04_Step4_Claude输出_Method.md
claude writing/05_Step5_Claude输出_Results.md
claude writing/06_Step6_Claude输出_Discussion_Limitations_Conclusion.md
```

可参考但不要照抄：

```text
Claude交互/00_总览.md
论文写作/00_总控流程.md
论文改进/20260529_论文写作完整规划.md
对比评分/Step6_Claude单边初审.md
```

---

## 2. 硬边界

1. 不新增实验、数值、图表或引用。
2. 不把 clean rendered images 写成真实望远镜图像性能。
3. 不宣称真实 optical telescope validation。
4. 不写 fusion universally best。
5. 不写 OCS always better than images。
6. 不把 `all_raw 45D` 写成实用观测特征；全篇只能是 semi-oracle diagnostic upper bound。
7. 不把 `r = 0.003` 写成 ResNet-image 与 OCS 的正式相关性结论；全篇只能是 earlier TinyCNN/OCS diagnostic。
8. 不把 Gaussian noise / brightness scaling 写成完整 realistic degradation model；只能写 controlled stress tests。
9. 不把 OCS 写成对所有真实观测噪声免疫；只能说在本 benchmark 中独立于 image-pixel degradation。
10. 不把 ISAR 并入论文主线。
11. 保留 `[CITATION: ...]`、`[to verify]`、`[需要作者确认：...]`，不要自行补文献或猜测结果。
12. Reviewer-facing defense points 不要混入正式正文，可放到输出末尾的 revision notes。

---

## 3. Step 6 审阅后必须收紧的项目

以下内容在全文整合时必须处理：

### 3.1 未确认 sensitivity / ablation 数值

以下数值若未由作者确认，必须标为 `[需要作者确认：...]`：

- roll sensitivity: `approximately 20% OCS variation`
- metallic roughness sensitivity: `30-42% OCS variation`
- non-metallic components: `<5%`
- full 3-DOF extension requires `approximately 37x larger datasets`
- random split / phase63 / occlusion / single-geometry OCS 等消融值

不要把这些未确认项写入 Abstract 或 Conclusion 的主结论句。

### 3.2 数据审计数字

若写：

- mean image intensity correlation `r < 0.02`
- centroid displacement correlation with yaw `r ≈ 0.66`

必须标注为 `[需要作者确认：data-audit source]`，或改成保守表述：

```text
Preliminary data-audit checks suggest that the image model is not explained by global intensity alone, although centroid-related geometric cues may contribute under the fixed simulated camera-target geometry.
```

### 3.3 `total_log` 与 single-geometry 不要混淆

当前可安全写法：

```text
The weak total-log OCS baseline (36.69 +/- 3.6 deg) and the stronger five-geometry per-part representation (5.91 +/- 0.22 deg) indicate that component-level and multi-geometry information are important for OCS-based discrimination.
```

除非作者确认，不要写 `single-geometry total OCS > 36 deg`。

### 3.4 OCS 低成本 / 小口径望远镜价值要降调

可以写：

```text
OCS-like integrated photometric measurements may be less demanding than fully resolved imagery, but the practical acquisition requirements depend on telescope aperture, target brightness, range, phase angle, calibration accuracy and atmospheric conditions.
```

不要写成本文已经证明“小口径望远镜可实现该精度”。

### 3.5 `catastrophic` 控制使用

全文最多使用一次 `catastrophic`。其他地方使用：

```text
severe degradation
sharp performance drop
performance collapse under controlled additive-noise stress tests
```

---

## 4. 推荐全文结构

请输出一版连续 manuscript draft，结构如下：

```text
Title
Abstract
Keywords

1. Introduction
2. Related Work
   2.1 Optical signatures and BRDF modeling of space objects
   2.2 Light-curve and OCS-based attitude inversion
   2.3 Photometric image simulation and image-based pose estimation
   2.4 Multi-modal fusion and robustness under observation degradation
3. Method
   3.1 Overview of the unified OCS-image simulation framework
   3.2 Satellite geometry and attitude parameterization
   3.3 Observation geometry and data generation protocol
   3.4 Nonuniform material assignment and GGX BRDF
   3.5 Self-occlusion and visibility modeling
   3.6 OCS integration and feature construction
   3.7 Photometric image generation
   3.8 Attitude inversion models
   3.9 Data splits and evaluation metrics
4. Results
   4.1 Forward-model validation and OCS signature analysis
   4.2 OCS-only attitude inversion and multi-geometry photometric constraints
   4.3 Image-only inversion: from TinyCNN to ResNet clean-image upper bound
   4.4 OCS-image fusion under clean images
   4.5 Robustness under controlled observation degradation
   4.6 Ablation and sensitivity analysis
5. Discussion
   5.1 Main finding: controlled complementarity between OCS and photometric images
   5.2 Why clean rendered images give a strong image-only upper bound
   5.3 Why OCS remains useful despite lower clean-image accuracy
   5.4 Conditional value of OCS-image fusion
   5.5 Implications for space object attitude inversion
   5.6 Scope and limitations
6. Conclusion
Data Availability [placeholder]
Author Contributions [placeholder]
Conflict of Interest [placeholder]
References [placeholder]
```

如果某些期刊不需要单独的 Data Availability / Author Contributions，可先作为 placeholder 保留。

---

## 5. 全文主线必须一致

全篇统一到以下主线：

```text
Unified BRDF-driven OCS and photometric image simulation enables a controlled benchmark for space object attitude inversion. Clean synthetic images provide an upper-bound case where strong CNNs achieve high accuracy, whereas OCS provides robust, interpretable, and low-cost attitude constraints under degraded image conditions. Multi-modal fusion is conditionally beneficial, improving tail errors in clean settings and becoming more valuable when observations degrade.
```

不要回到旧叙事：

```text
OCS is the main modality and images are auxiliary.
Fusion is always best.
TinyCNN represents the image upper bound.
```

---

## 6. 数字使用规则

同一组核心数字不要在 Abstract、Introduction、Results、Discussion、Conclusion 中无限重复。

建议：

- Abstract 放 3-4 个最关键数字。
- Introduction 放 1-2 个 teaser 数字即可。
- Results 放完整数字。
- Discussion 只引用解释所需数字。
- Conclusion 只保留 2-3 个最强数字。

核心安全数字：

- ResNet image-only clean: `1.69 +/- 0.07 deg`, Hit@5 `97.6%`
- ResNet + concat5 `per_part_log`: `1.47 +/- 0.07 deg`, Hit@5 `99.7%`
- Worst-case: `9.9 deg -> 6.6 deg`
- 1% Gaussian image noise: ResNet `85.85 +/- 3.00 deg`, Hit@5 `2.2%`
- OCS MLP `per_part_log`: `5.91 +/- 0.22 deg`, Hit@5 `73.8%`
- OCS MLP `all_raw 45D`: `3.98 +/- 0.60 deg`, Hit@5 `90.7%`, semi-oracle only
- TinyCNN image-only: `12.38 +/- 0.74 deg`, Hit@5 `26.1%`
- Early feature fusion `per_part_log`: `4.10 +/- 0.77 deg`, Hit@5 `87.3%`
- OCS-CNN diagnostic correlation: `r = 0.003`, TinyCNN/OCS diagnostic only
- OCS-noise fusion gain: `+1.97 deg -> +6.29 deg`

---

## 7. 图表计划

保留以下图表计划，但不需要画图：

| Figure / Table | Role |
|---|---|
| Fig. 1 | Unified framework |
| Fig. 2 | Satellite geometry, material partition and observation setup |
| Fig. 3 | OCS maps and occlusion diagnostics |
| Fig. 4 | Main inversion results |
| Fig. 5 | Image degradation robustness |
| Fig. 6 | OCS noise and fusion gain |
| Fig. 7 | Sensitivity / ablation summary |
| Table 1 | Related work comparison |
| Table 2 | Main inversion benchmark |
| Table 3 | ResNet fusion under clean images |
| Table 4 | Robustness and sensitivity summary |

对于图表 caption，只写 intent，不要编造具体图中尚未提供的曲线或数值。

---

## 8. 待核对项必须保留

以下项目必须保留为作者核对项，不能自行填充：

- Target journal final choice
- Final title
- Citation metadata and Table 1 `[to verify]`
- Euler rotation convention
- Angular error formula
- Target encoding
- 0% OCS-noise table values
- Which BRDF / occlusion / roll / random split / phase63 fairness values can enter main text
- Data-audit correlation values and source
- Whether ResNet-fusion image-degradation results exist
- Whether Limitations should be separate or folded into Discussion
- Whether Data Availability / Author Contributions / Conflict of Interest are required by target journal

---

## 9. 请输出的内容

请按以下格式输出完整 Markdown。

### A. Integrated Manuscript Draft

输出连续英文初稿。要求：

- 以论文正文为主，不要夹大量中文解释。
- 适度压缩每节，避免把阶段产物机械拼接成超长稿。
- 保留必要公式、表格草稿和 figure/table caption intent。
- 对未确认项使用 `[需要作者确认：...]`。
- 对引用使用 `[CITATION: ...]` 或 `[to verify]`。
- 不把 reviewer-facing defense points 写入正式正文。

### B. Cross-section Consistency Checklist

检查并列出结果：

1. Title / abstract / contribution 是否一致？
2. `OCS`, `photometric images`, `fusion` 术语是否一致？
3. `all_raw` 是否全篇都是 semi-oracle？
4. `per_part_log` 是否全篇都是 practical OCS setting？
5. clean image 是否全篇都是 upper-bound？
6. no real telescope validation 是否全篇清楚？
7. fixed roll / phase63 / nominal material limitations 是否一致？
8. `r = 0.003` 是否全篇限定为 TinyCNN/OCS diagnostic？
9. Gaussian noise 是否全篇写成 controlled stress test？
10. 是否存在数字冲突？

### C. Author Confirmation List

列出所有正式投稿前必须由作者确认的项目，按优先级排序。

### D. Revision Priority List

按优先级列出下一轮修订任务：

1. Must fix before internal review
2. Should fix before journal submission
3. Optional strengthening

### E. Self-review Checklist

检查：

1. 是否新增未给出的实验或数值？
2. 是否新增未核对引用？
3. 是否把 clean image 写成 field performance？
4. 是否夸大 fusion？
5. 是否夸大 OCS？
6. 是否弱化或遗漏 no real validation？
7. 是否把 reviewer-facing defense points 混入正式正文？
8. 是否保留所有待核对项？

---

## 10. 输出文件命名

完成后请把输出保存为：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\Claude交互\claude writing\07_Step7_Claude输出_全文整合初稿.md
```

如果不能直接保存文件，则把完整 Markdown 内容返回给作者，由作者保存。
