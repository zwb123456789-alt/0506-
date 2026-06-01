# Step 1 Output: Manuscript Positioning, Title, Abstract Skeleton & Contributions

> 本阶段解决的写作问题：确定论文主线定位、标题选项、核心科学问题、摘要骨架结构和贡献点，为后续各章节写作提供统一锚点。不写正文。

---

## 1. Manuscript Positioning

### English Positioning (108 words)

This manuscript presents a physically consistent simulation and controlled inversion study for space object attitude estimation. We develop a unified BRDF-driven framework that generates optical cross section (OCS) signatures and photometric images from the same geometry, material, and occlusion model, enabling systematic comparison of OCS-only, image-only, and multi-modal fusion approaches. Through controlled experiments under both ideal and degraded observation conditions, we reveal that clean synthetic images provide an upper-bound for image-based inversion that is highly fragile to realistic degradation, while OCS offers robust photometric constraints. No real optical telescope validation is performed; all conclusions are bounded to the simulation domain.

### 中文解释

该定位适合 SCI 二区（一区边缘标准）的原因：
- **物理一致性**是空间目标光学表征领域的核心关切，统一框架比单一方法论文更有系统性贡献；
- **受控基准研究**（controlled benchmark）在该领域稀缺——多数文献要么只做 OCS/光变曲线，要么只做图像姿态估计，很少在同一物理模型下系统对比；
- **条件性互补分析**（ideal vs degraded）比"提出一个新融合方法"更有科学深度，适合 Acta Astronautica / ASR 的读者群；
- 诚实声明 simulation-focused 避免审稿人质疑真实验证缺失。

---

## 2. Title Options

### Title 1
**BRDF-Driven Optical Cross Section and Photometric Image Simulation for Space Object Attitude Inversion: A Controlled Benchmark Study**

中文评价：突出 BRDF 驱动和受控基准，定位清晰。风险：标题偏长（18 词），部分期刊可能要求缩短。

### Title 2
**Conditional Complementarity of OCS and Photometric Images for Space Object Attitude Estimation under Nonuniform BRDF and Self-Occlusion**

中文评价：直接点明"条件性互补"这一核心发现，学术味强。风险：OCS 缩写在标题中可能需要展开，且未提及 simulation/benchmark 属性。

### Title 3
**When Does Multi-Modal Fusion Help? OCS-Image Attitude Inversion of Space Objects under Ideal and Degraded Observations**

中文评价：问句式标题吸引眼球，直接传达核心科学问题。风险：部分保守期刊/审稿人不喜欢问句标题。

### Title 4
**Unified GGX BRDF Simulation Framework for OCS-Photometric Image Joint Attitude Estimation of Space Objects**

中文评价：突出统一框架和 GGX BRDF 技术路线，对光学/BRDF 方向读者友好。风险：未体现"条件性互补"这一核心发现。

### Title 5
**Robustness and Complementarity of Optical Cross Section and Photometric Images for Space Object Attitude Inversion: A BRDF-Consistent Simulation Study**

中文评价：同时包含鲁棒性、互补性和 BRDF 一致性三个关键词，信息量大。风险：标题较长（20 词），需要根据目标期刊调整。

---

## 3. Core Scientific Question

### English

> Under nonuniform BRDF, self-occlusion, and varying observation quality, how do scalar OCS signatures and resolved photometric images each contribute to space object attitude inversion, and under what conditions does their fusion provide robust complementary constraints rather than redundant information?

### 中文

> 在非均匀 BRDF、自遮挡和观测质量变化条件下，OCS 标量光度特征与分辨光度图像分别承载何种姿态信息？两者融合在什么条件下提供鲁棒互补约束，而非冗余信息？

### 为什么这个问题比"提出一个融合方法"更适合投稿

"提出融合方法"是工程贡献，容易被审稿人质疑"为什么不用更大模型/更多数据"。而"条件性互补分析"是科学发现——它回答的是"什么时候融合有用、什么时候没用"，这个问题对空间态势感知领域的观测策略设计有直接指导意义，且不依赖于特定模型架构的 SOTA 竞争。

---

## 4. One-Sentence Argument

```text
In space object attitude inversion under nonuniform BRDF and self-occlusion, we show that OCS and photometric images provide conditionally complementary constraints whose fusion value depends on observation quality, using a unified GGX-driven simulation framework with multi-geometry OCS and pixel-level rendered images, supported by evidence that clean-image CNNs achieve 1.69° mean error but collapse to 86° under 1% noise while OCS remains robust at 5.91°, with the boundary that all results are obtained in a controlled simulation environment without real optical telescope validation.
```

---

## 5. Abstract Skeleton

### Sentence 1: Context/Problem

> Accurate attitude estimation of space objects is critical for space situational awareness, yet existing approaches typically treat optical cross section (OCS) signatures and photometric images as independent modalities without a unified physical model connecting them.

中文说明：建立领域需求，指出 OCS 和图像通常被割裂处理。

### Sentence 2: Gap

> It remains unclear under what observation conditions each modality provides reliable attitude constraints, and whether their fusion offers robust complementary benefits or merely redundant information.

中文说明：指出核心知识空白——"什么条件下融合有用"这个问题没有被系统回答过。

### Sentence 3: Approach

> We develop a unified BRDF-driven simulation framework that generates physically consistent OCS signatures and photometric images from the same satellite STL geometry, GGX/Cook-Torrance material model, and ray-traced self-occlusion, enabling controlled attitude inversion experiments across OCS-only, image-only, and multi-modal fusion configurations under both ideal and degraded observation conditions.

中文说明：一句话概括方法——统一框架 + 受控实验设计。

### Sentence 4: Clean-Image Upper-Bound Result

> Under clean synthetic images, a ResNet-18 model achieves a mean angular error of 1.69° with 97.6% of predictions within 5°, establishing an upper-bound for image-based inversion; incorporating multi-geometry OCS features further reduces the worst-case error from 9.9° to 6.6° and improves Hit@5° to 99.7%.

中文说明：报告理想条件下的最佳性能，明确标注为 upper-bound。

### Sentence 5: Degradation / OCS / Fusion Insight

> However, this clean-image performance is highly fragile: 1% additive Gaussian noise degrades the ResNet to 85.9° mean error, whereas OCS-based inversion remains stable at 5.91° regardless of image quality; the fusion gain increases monotonically from +2.0° to +6.3° as OCS noise rises from 0% to 20%, demonstrating that multi-modal complementarity is conditional on observation quality rather than universally guaranteed.

中文说明：核心发现——图像脆弱、OCS 鲁棒、融合增益随退化递增。这是论文最重要的一句。

### Sentence 6: Bounded Implication

> These findings, obtained entirely within a physically consistent simulation environment, provide quantitative guidance for observation strategy design in space object attitude estimation and motivate future validation with real optical telescope data.

中文说明：限定结论边界（仿真环境），同时指出实际意义（观测策略指导）。

---

## 6. Contributions

### Contribution 1: Unified Physical Forward Model

**Title:** Unified BRDF-driven OCS-image simulation framework

**Statement:** We develop a unified simulation framework that generates physically consistent OCS signatures and photometric images from the same satellite geometry, nonuniform GGX/Cook-Torrance BRDF, and ray-traced self-occlusion model, ensuring that both modalities share identical physical assumptions.

**Evidence:** Three-way closure validation on canonical geometries (single plate, cube) achieves ≤0.25% relative error between analytical, facet-based, and pixel-level OCS; five observation geometries covering 24°–120° phase angles produce 13,505 attitude-OCS pairs; 2,701 photometric images rendered via exact BRDF post-processing pipeline.

**Boundary:** Material parameters are nominal literature values, not calibrated from real observations. Atmosphere, detector response, and PSF are not modeled.

---

### Contribution 2: Controlled Attitude Inversion Benchmark

**Title:** Systematic multi-modal attitude inversion benchmark

**Statement:** We construct a controlled yaw-pitch attitude inversion benchmark that systematically compares OCS-only (MLP), image-only (TinyCNN, ResNet-18), late fusion, and feature fusion under consistent data splits, evaluation metrics, and multiple random seeds.

**Evidence:** 10°-train → 5°-test interpolation split (563 train / 1,998 test); random 80/10/10 split for consistency check; 5-seed averaging for all neural network results; fair single-geometry ablation (phase63 OCS vs phase63 image).

**Boundary:** Task is limited to yaw-pitch estimation with fixed roll. Only phase63 geometry is used for the image branch. Training set size is modest (563 samples for interpolation split).

---

### Contribution 3: Clean-Image Upper Bound and Fragility

**Title:** Quantification of clean-image upper bound and its fragility to observation degradation

**Statement:** We show that high-capacity image models (ResNet-18) achieve 1.69° mean error under clean synthetic images, establishing an upper bound for image-based attitude inversion, but this performance collapses catastrophically (to 85.9°) under minimal (1%) additive noise, revealing extreme sensitivity to observation quality.

**Evidence:** ResNet-18 clean: 1.69 ± 0.07°, Hit@5° = 97.6%; 1% Gaussian noise: 85.85 ± 3.00°, Hit@5° = 2.2%; brightness ×0.5: 3.45°. Data audit confirms no train-test leakage.

**Boundary:** The clean-image result is an idealized upper bound, not a prediction of field performance. The noise test uses simple additive Gaussian noise, not a full atmospheric/detector degradation model.

---

### Contribution 4: Robust OCS and Conditional Fusion

**Title:** OCS robustness and conditional complementarity of multi-modal fusion

**Statement:** We demonstrate that OCS provides robust attitude constraints (5.91° mean error) unaffected by image degradation, and that OCS-image fusion gain is conditional: under clean images it improves tail errors (worst-case 9.9° → 6.6°), while under degraded OCS conditions the image compensation gain increases monotonically from +2.0° to +6.3°.

**Evidence:** OCS MLP per_part_log: 5.91 ± 0.22° stable regardless of image noise; ResNet + OCS fusion: 1.47 ± 0.07° (clean), worst-case reduced 33%; OCS-noise experiment: fusion gain +1.97° at 0% noise → +6.29° at 20% noise; OCS-image error correlation r = 0.003 (near-zero, confirming complementarity).

**Boundary:** OCS "robustness" is demonstrated within the simulation where OCS computation is deterministic; real OCS measurements would have photometric calibration errors. The per_part_log feature (30D) requires component-resolved OCS, which may not always be available.

---

## 7. Claim-Evidence Map

| # | Claim | Evidence | Supported? | Boundary |
|---|---|---|---|---|
| 1 | The unified framework produces physically consistent OCS and images | Three-way closure ≤0.25% on plate/cube; A/B share same `eval_ggx()` function and material DB | Yes | Validated on canonical geometries; real satellite native A/B gap exists due to sampling semantics |
| 2 | Multi-geometry OCS dramatically improves attitude discrimination | Single-geom total OCS: mean=79°; concat5 total: mean=26.5°; concat5 all MLP: 3.98° | Yes | 5 geometries may be more than operationally available; all_raw 45D is semi-oracle |
| 3 | Clean synthetic images enable very high image-based accuracy | ResNet-18: 1.69 ± 0.07°, Hit@5°=97.6% | Yes | Clean rendered images only; no atmosphere/noise/PSF |
| 4 | Image-based accuracy is fragile to minimal noise | 1% Gaussian noise → 85.85°; brightness ×0.5 → 3.45° | Yes | Only additive Gaussian tested; real degradation is more complex |
| 5 | OCS-based inversion is robust to image degradation | OCS MLP per_part_log: 5.91° regardless of image noise level | Yes | OCS itself is noise-free in simulation; real OCS has calibration errors |
| 6 | OCS-image fusion improves tail errors under clean images | Worst-case: 9.9° → 6.6° (−33%); Hit@5°: 97.6% → 99.7% | Yes | Mean improvement is modest (1.69° → 1.47°); fusion value is primarily in tails |
| 7 | Fusion gain increases as OCS quality degrades | Gain: +1.97° (0% noise) → +6.29° (20% noise), monotonic | Yes | Image branch assumed clean in this experiment |
| 8 | OCS and image errors are near-uncorrelated | Pearson r = 0.003 between OCS MLP and CNN angular errors | Yes | Measured on TinyCNN+OCS MLP pair; ResNet pair not yet measured |
| 9 | Self-occlusion modeling is necessary | Occlusion rate 60%–78.5% across geometries; mhd sensitivity validated | Yes | mhd=1.0mm optimal for this STL; other geometries may differ |
| 10 | BRDF model choice affects OCS magnitude | GGX vs LegacyPhong ratio 0.02–8.86; metal roughness ±20% → OCS change 30–42% | Yes | Nominal parameters; no real material calibration |

---

## 8. Reviewer-Risk Notes

### Risk 1: No Real Optical Validation

**Why it matters:** Reviewers in Acta Astronautica / ASR expect at least discussion of how simulation results relate to real observations. Pure simulation papers risk being seen as "just a software demo."

**How to handle:** (1) Explicitly position as "controlled simulation and benchmark study" in title/abstract; (2) Provide analytical validation (three-way closure), rendering consistency checks, and sensitivity analysis as credibility proxies; (3) Cite literature trends (Yang 2024, Lu 2024) showing similar OCS magnitudes; (4) Write honest Limitations paragraph; (5) Propose specific real-validation path in Future Work (ground-based 1m telescope with known attitude from TLE+gyro).

---

### Risk 2: Clean Synthetic Image Upper Bound

**Why it matters:** A reviewer may ask "if ResNet gets 1.69° on clean images, why bother with OCS at all?" This undermines the fusion contribution.

**How to handle:** (1) Immediately follow the clean result with the 1% noise collapse (85.9°); (2) Frame clean result as "upper bound under idealized conditions that are unlikely in field observations"; (3) List real degradation sources (seeing, tracking, noise, PSF, background); (4) Show OCS remains at 5.91° regardless; (5) Argue that operational systems need robustness, not just peak performance.

---

### Risk 3: Fixed Roll (2-DOF Only)

**Why it matters:** Real satellite attitude is 3-DOF. Reviewers may question generalizability.

**How to handle:** (1) Clearly state yaw-pitch scope in Method; (2) Report roll sensitivity experiment (OCS varies ~20% with roll); (3) Argue that yaw-pitch is a standard starting configuration in the literature; (4) Note that 3-DOF extension requires ~37× computation and is planned as future work; (5) The framework itself is roll-extensible without architectural changes.

---

### Risk 4: Single Phase Angle for Image Branch

**Why it matters:** Images are rendered only at phase63 (63° phase angle). Reviewer may question whether results generalize to other observation geometries.

**How to handle:** (1) Report phase63 fair ablation (single-geom OCS vs single-geom image under same geometry); (2) Note that OCS uses 5 geometries because each geometry yields only 1 scalar, while one image yields 16,384 pixels; (3) Acknowledge as limitation; (4) Optionally add 1-2 cross-phase sanity tests if time permits before submission.

---

### Risk 5: Nominal Material Parameters

**Why it matters:** GGX parameters (F0=0.91, roughness=0.20 for aluminum, etc.) are literature nominal values, not measured from the actual satellite.

**How to handle:** (1) Report BRDF sensitivity analysis: metal roughness ±20% → OCS change 30–42%, other parts <5%; (2) Cite parameter sources (aluminum optical constants, solar cell glass IOR); (3) Argue that the paper's contribution is the framework and conditional complementarity finding, not absolute radiometric accuracy; (4) Position material calibration as future work requiring real photometric observations.

---

## 9. Items for Author Check

请作者确认以下问题，确认后进入 Step 2（Introduction 写作）：

1. **目标期刊**：是否确定主投 Acta Astronautica？还是优先 Advances in Space Research？这影响标题长度和 Method 详细程度。

2. **标题选择**：5 个标题中倾向哪个方向？是否接受问句式标题（Title 3）？是否需要在标题中包含 "simulation" 或 "benchmark" 以明确定位？

3. **ResNet 定位**：是否将 ResNet-18 作为主图像 baseline 写入正文？TinyCNN (12.38°) 是否仅放入补充材料或作为 lightweight baseline 简要提及？

4. **OCS all_raw 45D (3.98°) 的处理**：是否接受将其标注为 "semi-oracle upper bound"（因为包含遮挡率等实际难以测量的信息），而以 per_part_log 30D (5.91°) 作为 "practical OCS-only" 结果？

5. **Feature fusion (4.10°) vs ResNet fusion (1.47°) 的关系**：旧实验的 feature fusion 基于 TinyCNN，新实验的 ResNet fusion 性能更强。正文是否以 ResNet fusion 为主线，TinyCNN fusion 放消融/补充？

6. **"No real optical validation" 边界声明**：是否接受在 Abstract 最后一句和 Limitations 中明确写出？这是审稿防御的关键。

7. **互补性数据 r=0.003**：该数据来自 TinyCNN+OCS MLP 对。是否需要补测 ResNet+OCS MLP 的误差相关性？（预期仍然很低，但数值可能不同。）

8. **论文语言**：正文用英文写作，是否需要同步产出中文翻译版本供导师审阅？

---

*Step 1 完成。等待作者确认后进入 Step 2: Introduction 初稿指导。*
