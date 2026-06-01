# Step 5 Claude 指导文件：Results

> 使用对象：Claude  
> 当前任务：在已完成 Step 1-4 的基础上，生成论文 Results 章节的证据链、结构、英文初稿、图表计划、结果表格草稿和审稿风险自检。  
> 输出建议保存为：`claude writing/05_Step5_Claude输出_Results.md`

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

Results 章节的核心任务：

> 证明本文不是单一模型堆砌，而是一个 physically consistent simulation and controlled inversion benchmark。Results 要展示 OCS、clean photometric images 和 fusion 在不同观测质量下的条件性互补关系，并且始终保持仿真研究边界。

---

## 1. 必须遵守的硬边界

1. 不发明实验、数值、图表或统计。
2. 不把 clean rendered image 结果写成真实望远镜性能。
3. 不宣称真实 optical telescope validation。
4. 不写 fusion universally best。
5. 不写 OCS always better than images。
6. 不把 TinyCNN image-only 当作图像能力上限。
7. 不把 `all_raw 45D` 写成实用观测特征；它只能是 semi-oracle diagnostic upper-bound representation。
8. 不把 `r = 0.003` 写成 ResNet-image 与 OCS 的正式相关性结论；它只能是 earlier TinyCNN/OCS diagnostic。
9. 不把 Gaussian noise / brightness scaling 写成完整 realistic degradation model；只能写 controlled degradation tests 或 observation-quality stress tests。
10. 不把 ISAR 并入 Results 主线。
11. 不确定的 sensitivity / ablation 项必须标注 `[需要作者确认：...]`。

---

## 2. Results 总结构

请按以下小节组织 Results：

```text
4.1 Forward-model validation and OCS signature analysis
4.2 OCS-only attitude inversion and multi-geometry photometric constraints
4.3 Image-only inversion: from TinyCNN to ResNet clean-image upper bound
4.4 OCS-image fusion under clean images
4.5 Robustness under controlled observation degradation
4.6 Ablation and sensitivity analysis
```

写作原则：

- 每节开头先给一句 claim-first topic sentence。
- 每个结果按 `what was tested -> what was observed -> what it means -> boundary` 写。
- Results 可以解释数据意义，但不要写成长 Discussion。
- 不要把 Method 细节重复一遍。
- 正文只写支撑主线的关键数字，其余放表格或图注。

---

## 3. 当前可用核心事实与数值

### 3.1 Forward model / validation / physical setup

可写事实：

- Real satellite STL geometry
- Three components: metal body, solar panel, baffle/shade
- Nonuniform GGX/Cook-Torrance materials
- Analytical ray-based self-occlusion
- Multi-geometry OCS signatures: 5 sun-sensor geometries
- Phase-angle range: about `24°-120°`
- Phase63 image branch: `128 x 128` clean photometric images, 2701 attitudes
- OCS scan: 5° grid, yaw `73` samples, pitch `37` samples, `2701` attitudes
- Multi-geometry OCS data: `5 x 2701 = 13,505` attitude-geometry samples
- OCS-image consistency checks on simple geometries: if exact threshold is uncertain, write `within sub-percent error in simple-geometry checks`
- Self-occlusion validation: single plate, double plate, U-block, nested cylinder, Blender/manual ray-cast review
- Occlusion rates across geometry roughly `60%-78.5%`

写法边界：

- 这些结果支撑 forward model credibility，不等于真实望远镜验证。
- 不展开代码排查历史。

### 3.2 OCS-only inversion

可用结果：

| Method / feature | Mean error | Hit@5° | Hit@10° | Role |
|---|---:|---:|---:|---|
| OCS MLP `all_raw 45D` | `3.98 ± 0.60°` | `90.7%` | `97.1%` | semi-oracle upper bound |
| OCS MLP `per_part_log 30D` | `5.91 ± 0.22°` | `73.8%` | `94.3%` | practical OCS-only |
| OCS MLP `total_log 15D` | `36.69 ± 3.6°` | `9.7%` | `23.5%` | weak OCS baseline |
| Weighted kNN `all_raw` | `21.84°` | `47.9%` | `[if needed]` | classical / low-capacity baseline |

Additional OCS evidence:

- Multi-geometry total OCS Top1@5 improves about `7.6x` over single phase63 total in earlier observability / kNN analysis.
- Component-level / per-part features carry much more attitude information than total OCS alone.

写法要求：

- 主实用 OCS 结果优先写 `per_part_log 5.91°`。
- `all_raw 3.98°` 必须写为 semi-oracle upper bound because it includes additional diagnostic quantities。
- 不要写 OCS clean performance beats ResNet clean；它不 beats。

### 3.3 Image-only inversion

可用结果：

| Model | Input | Mean error | Hit@5° | Hit@10° | Role |
|---|---|---:|---:|---:|---|
| TinyCNN | phase63 `128 x 128` clean image | `12.38 ± 0.74°` | `26.1%` | `55.8%` | lightweight baseline |
| ResNet-18 | phase63 `128 x 128` clean image | `1.69 ± 0.07°` | `97.6%` | `99.9%` | clean-image upper bound |

Dataset audit facts for ResNet:

- No explicit train/val/test attitude overlap.
- Test attitudes are not training grid points under the `10° -> 5°` split.
- File names and labels are aligned.
- Normalization uses fixed constants, not test-set statistics.
- Target centroid displacement correlates with yaw (`r = 0.66`) and is a physical rendering cue, but may not transfer to field observations where tracking controls image position.
- Mean intensity is nearly uncorrelated with attitude (`r < 0.02`), reducing concern that the network uses a simple brightness proxy.

写法要求：

- TinyCNN 是 lightweight baseline，不代表 image modality upper bound。
- ResNet-18 clean result is an idealized upper bound under clean rendered images。
- Dataset audit 可简短写，目的是解释 ResNet 不是 obvious leakage。

### 3.4 OCS-image fusion under clean images

ResNet-level fusion:

| Case | Model | Mean±std | P90 | Worst | Hit@5° | Hit@10° |
|---|---|---:|---:|---:|---:|---:|
| A1 | ResNet image-only | `1.69 ± 0.07°` | `3.31°` | `9.9°` | `97.6%` | `99.9%` |
| A2 | ResNet + concat5 `per_part_log 30D` | `1.47 ± 0.07°` | `2.71°` | `6.6°` | `99.7%` | `100%` |
| A3 | ResNet + phase63 `per_part_log 6D` | `1.61 ± 0.07°` | `2.97°` | `7.4°` | `99.2%` | `100%` |
| A4 | ResNet + concat5 `all_raw 45D` | `1.49 ± 0.10°` | `2.70°` | `18.7°` | `99.2%` | `99.9%` |

Interpretation:

- OCS gives a modest but meaningful gain even with a strong clean-image model.
- Mean improves `1.69° -> 1.47°` (`0.22°`, about `13%`).
- Hit@5 improves `97.6% -> 99.7%` (`+2.1 pp`).
- Worst-case improves `9.9° -> 6.6°` (`33%` reduction).
- A4 shows stronger / semi-oracle OCS features do not automatically improve fusion tail behavior; `all_raw` has worse worst-case `18.7°`.

Earlier TinyCNN / OCS fusion evidence:

| Case | OCS-only MLP | CNN-only | Late fusion | Feature fusion | Interpretation |
|---|---:|---:|---:|---:|---|
| `all_raw` | `3.98°` | `12.38°` | `5.03°` | `5.42°` | OCS too strong; image can hurt |
| `per_part_log` | `5.91°` | `12.38°` | `6.15°` | `4.10°` | intermediate balance; feature fusion helps |
| `total_log` | `36.69°` | `12.38°` | `11.99°` | `13.75°` | weak OCS; image dominates |

Complementarity diagnostic:

- Earlier TinyCNN/OCS diagnostic: OCS-CNN error correlation `r = 0.003`.
- Use only as diagnostic, not as ResNet-pair evidence.

写法要求：

- Fusion is conditional, not universally best.
- ResNet fusion is primary clean-image fusion evidence.
- TinyCNN fusion can be written as diagnostic / ablation / supplement-leaning evidence.

### 3.5 Robustness under controlled degradation

Image degradation / ResNet robustness:

| Degradation | ResNet mean | Hit@5° | Interpretation |
|---|---:|---:|---|
| clean | `1.69°` | `97.6%` | clean upper-bound |
| noise `sigma=0.01` | `85.85 ± 3.00°` | `2.2%` | severe image-noise fragility |
| noise `sigma=0.03` | `85.49°` | `1.5%` | collapsed |
| noise `sigma=0.05` | `85.97°` | `1.2%` | collapsed |
| noise `sigma=0.10` | `87.92°` | `1.0%` | collapsed |
| brightness x0.50 | `3.45°` | `78.7%` | less destructive than additive noise |
| brightness x0.75 | `2.03°` | `94.8%` | mostly robust |
| brightness x1.25 | `1.77°` | `97.5%` | mostly robust |
| brightness x1.50 | `2.00°` | `95.8%` | mostly robust |

OCS noise / conditional fusion gain:

| OCS noise | OCS-only mean | Fusion mean | Gain |
|---:|---:|---:|---:|
| 0% | `[需要作者确认：0% OCS-only mean]` | `[需要作者确认：0% fusion mean]` | `+1.97°` |
| 10% | `9.99 ± 0.35°` | `6.69 ± 1.34°` | `+3.30°` |
| 20% | `17.25 ± 0.71°` | `10.96 ± 2.51°` | `+6.29°` |

写法要求：

- Image noise is a controlled stress test, not a full atmosphere / detector model.
- Brightness scaling is less destructive than additive Gaussian noise; do not overgeneralize.
- OCS does not depend on image pixels, so it is unaffected by image degradation in this benchmark.
- Do not write OCS is immune to all real photometric/calibration noise.
- OCS-noise experiment assumes image branch remains clean; state this boundary.

### 3.6 Ablation and sensitivity analysis

可写证据：

- `10° -> 5°` split tests interpolation rather than direct grid memorization.
- Self-occlusion validation and mhd sensitivity support choosing `epsilon = 1.0 mm` and `min_hit_distance = 1.0 mm`.
- Random split / phase63 fairness / BRDF sensitivity / occlusion w vs w/o / roll sensitivity are reviewer-defense items; only write as finalized experiments where exact values are available.
- LegacyPhong vs GGX and BRDF parameter sensitivity may be supporting analysis; if exact results are not known, do not invent.
- Roll is fixed in main benchmark; any roll analysis should be written as sensitivity / limitation, not full 3-DOF result.

写法要求：

- 没有具体数值，不要装成完整实验。
- 对不确定项写 `[需要作者确认：...]`。
- 这一节的作用是审稿防御，不是开启新主线。

---

## 4. 建议图表安排

请为每个图表写一句 caption intent，不需要画图。

正文主图建议：

| Figure | Content | Purpose |
|---|---|---|
| Fig. 1 | Unified BRDF-driven OCS-image simulation and inversion framework | Method / overview |
| Fig. 2 | STL geometry, material labels, coordinate system, observation geometries | Physical setup |
| Fig. 3 | OCS yaw-pitch heatmaps, component contribution, occlusion rate | OCS observability |
| Fig. 4 | Main inversion results: OCS-only / TinyCNN / ResNet / fusion | Main benchmark |
| Fig. 5 | Image degradation robustness: ResNet clean vs noise / brightness | Clean-image fragility |
| Fig. 6 | OCS noise and fusion gain | Conditional complementarity |
| Fig. 7 | BRDF / occlusion / roll / split sensitivity summary | Reviewer defense |

正文主表建议：

| Table | Content |
|---|---|
| Table 2 | Main inversion results and clean-image upper-bound |
| Table 3 | ResNet-fusion vs image-only |
| Table 4 | Robustness and sensitivity summary |

---

## 5. 请输出的内容

请按以下格式一次性输出完整 Markdown。

### A. Results Evidence Ladder

用 8-12 条说明 Results 的证据链如何支撑论文主线。

### B. Section Outline

对 4.1-4.6 每节写：

- claim-first topic sentence
- key evidence
- figure/table target
- boundary/risk

### C. Results Draft

写英文 Results 初稿。建议总长 `1800-2600 words`。要求：

- 每小节至少 2-3 段，段落不要过长。
- 主体语言用 `show`, `indicate`, `suggest`, `demonstrate within this benchmark`，避免过度承诺。
- 不重复 Method 细节。
- 不发明未给出的数值。
- 对不确定数据用 `[需要作者确认：...]`。

### D. Figure and Table Plan

列出 Fig. 2-7 和 Table 2-4 的用途、关键数据、caption intent。

### E. Main Results Tables Draft

至少生成三个 Markdown 表格草稿：

1. Main inversion benchmark table
2. ResNet fusion table
3. Robustness / degradation table

注意：`all_raw` 必须标注为 semi-oracle，`per_part_log` 标注为 practical OCS setting。

### F. Claim-Evidence-Risk Map

列出 Results 中最容易被审稿人质疑的 8-10 个 claims，并标注 evidence、risk、safe wording。

### G. Self-review Checklist

检查：

1. 是否发明了实验或数值？
2. 是否把 clean image 写成 field performance？
3. 是否夸大 fusion？
4. 是否把 OCS 写成永远优于图像？
5. 是否把 `all_raw` 写成 semi-oracle？
6. 是否把 `r = 0.003` 限定为 TinyCNN/OCS diagnostic？
7. 是否说明 image degradation 是 controlled stress test？
8. 是否明确 no real telescope validation？
9. 是否没有把 ISAR 并入主线？

### H. Questions for Author

最多提出 6 个需要作者确认的问题。优先问：

- angular error formula 是否已固定？
- 0% OCS noise 的具体 OCS-only / fusion mean 是否可填写？
- BRDF sensitivity / occlusion ablation / roll sensitivity 哪些已有最终数值可放正文？
- ResNet-fusion degradation 是否补测，还是写 Future Work？
- `r = 0.003` 是否补测 ResNet pair，否则只作为 TinyCNN diagnostic？
- phase63 fairness / cross-phase test 是否放正文、补充或 Future Work？

---

## 6. 推荐英文口径

可用表述：

```text
The clean-image result should be interpreted as an upper-bound case for image-based inversion under idealized rendered photometric images, not as a field-performance estimate.
```

```text
OCS is not the accuracy upper bound when clean resolved images are available; its value lies in low-dimensional, interpretable, multi-geometry photometric constraints that remain independent of image-pixel degradation in this benchmark.
```

```text
Fusion provides conditional benefits: it improves tail errors in clean settings and becomes more valuable as observation quality degrades.
```

```text
The all_raw representation is reported as a semi-oracle diagnostic upper bound, whereas per_part_log is used as the more practical OCS setting.
```

避免表述：

```text
The proposed fusion model is best in all conditions.
OCS is always more reliable than images.
The rendered images validate real telescope performance.
The Gaussian noise experiment is a realistic atmospheric model.
The r=0.003 diagnostic proves ResNet-OCS complementarity.
```

---

## 7. 输出文件命名

完成后请把输出保存为：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\Claude交互\claude writing\05_Step5_Claude输出_Results.md
```

如果不能直接保存文件，则把完整 Markdown 内容返回给作者，由作者保存。
