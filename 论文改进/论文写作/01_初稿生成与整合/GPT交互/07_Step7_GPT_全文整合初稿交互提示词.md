# Step 7 GPT 交互提示词：全文整合初稿与一致性自检

> 使用对象：GPT  
> 当前任务：将 Step 1-6 的阶段输出整合成一版连续论文初稿骨架，并完成跨章节一致性自检。  
> 输出建议保存为：`GPT writing/07_GPT输出_全文整合初稿.md`

---

## 0. 你当前接手的论文项目

论文主题：

> BRDF-driven optical cross section and photometric image simulation for robust space object attitude inversion.

中文定位：

> 基于统一 BRDF 与自遮挡建模的 OCS-光度图像姿态反演基准研究，重点分析理想图像上限、图像退化脆弱性与 OCS 鲁棒互补价值。

目标档次：

- 主攻 SCI 二区
- 按 SCI 一区边缘标准组织论证
- 候选期刊：Acta Astronautica / Advances in Space Research / Optics Express / Remote Sensing

Step 7 的核心任务：

> 把 Step 1-6 的分段产物整合为一版可以通读的英文 manuscript draft。重点不是新增内容，而是统一叙事、删减重复、保留边界、标注待核对项。

---

## 1. 必须读取的输入文件

请按顺序读取并整合：

```text
GPT writing/01_Step1_GPT输出_论文定位标题摘要贡献点.md
GPT writing/02_Step2_GPT输出_Introduction结构与初稿.md
GPT writing/03_Step3_GPT输出_RelatedWork_Table1.md
GPT writing/04_Step4_GPT输出_Method.md
GPT writing/05_Step5_GPT输出_Results.md
GPT writing/06_Step6_GPT输出_Discussion_Limitations_Conclusion.md
```

可参考但不要照抄：

```text
GPT交互/GPT写作工作流总览.md
论文写作/00_总控流程.md
论文改进/20260529_论文写作完整规划.md
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

---

## 3. 全文推荐结构

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

## 4. 整合原则

### 4.1 叙事统一

全文主线必须保持：

```text
Unified BRDF-driven OCS and photometric image simulation enables a controlled benchmark for space object attitude inversion. Clean synthetic images provide an upper-bound case where strong CNNs achieve high accuracy, whereas OCS provides robust, interpretable, and low-cost attitude constraints under degraded image conditions. Multi-modal fusion is conditionally beneficial, improving tail errors in clean settings and becoming more valuable when observations degrade.
```

不要回到旧叙事：

```text
OCS is the main modality and images are auxiliary.
Fusion is always best.
TinyCNN represents the image upper bound.
```

### 4.2 数字控制

同一组核心数字不要在 Abstract、Introduction、Results、Discussion、Conclusion 中无限重复。

建议：

- Abstract 放 3-4 个最关键数字。
- Introduction 放 1-2 个 teaser 数字即可。
- Results 放完整数字。
- Discussion 只引用解释所需数字。
- Conclusion 只保留 2-3 个最强数字。

### 4.3 图表控制

保留以下图表计划，但不需要画图：

| Figure / Table | Role |
|---|---|
| Fig. 1 | Unified framework |
| Fig. 2 | Satellite geometry and observation setup |
| Fig. 3 | OCS maps and occlusion diagnostics |
| Fig. 4 | Main inversion results |
| Fig. 5 | Image degradation robustness |
| Fig. 6 | OCS noise and fusion gain |
| Fig. 7 | Sensitivity / ablation summary |
| Table 1 | Related work comparison |
| Table 2 | Main inversion benchmark |
| Table 3 | ResNet fusion under clean images |
| Table 4 | Robustness and sensitivity summary |

### 4.4 待核对项保留

以下项目必须保留为作者核对项，不能自行填充：

- Target journal final choice
- Final title
- Citation metadata and Table 1 `[to verify]`
- Euler rotation convention
- Angular error formula
- Target encoding
- 0% OCS-noise table values
- Which BRDF / occlusion / roll / random split / phase63 fairness values can enter main text
- Whether ResNet-fusion image-degradation results exist
- Whether Limitations should be separate or folded into Discussion

---

## 5. 请输出的内容

请按以下格式输出完整 Markdown。

### A. Integrated Manuscript Draft

输出连续英文初稿。要求：

- 以论文正文为主，不要夹大量中文解释。
- 可以适度压缩每节，避免把阶段产物机械拼接成超长稿。
- 保留必要公式、表格草稿和 figure/table caption intent。
- 对未确认项使用 `[需要作者确认：...]`。
- 对引用使用 `[CITATION: ...]` 或 `[to verify]`。

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

## 6. 输出文件命名

完成后请把输出保存为：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\GPT交互\GPT writing\07_GPT输出_全文整合初稿.md
```

如果不能直接保存文件，则把完整 Markdown 内容返回给作者，由作者保存。
