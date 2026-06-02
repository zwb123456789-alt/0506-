# Step 1 返修版：标题、摘要骨架与贡献点

> 基于 `02_Step1_Claude返修提示.md` 的 6 项修改要求，对上一版做降调、核验和收紧。保留整体结构，只修正问题表述。

---

## 1. Revised Recommended Title

**Primary recommendation:**

> BRDF-Driven Optical Cross Section and Photometric Image Simulation for Space Object Attitude Inversion: A Controlled Benchmark Study

**Compressed alternative (15 words):**

> Controlled Benchmark for OCS-Image Attitude Inversion of Space Objects under BRDF-Consistent Simulation

中文说明：主推第一个，信息完整且明确标注 "Controlled Benchmark Study"，让审稿人第一眼知道这不是声称真实验证的论文。若期刊要求标题 ≤15 词，用压缩版。

---

## 2. Revised Manuscript Positioning

This manuscript presents a physically consistent simulation and controlled inversion study for space object attitude estimation. We develop a unified BRDF-driven framework that generates optical cross section (OCS) signatures and photometric images from the same geometry, material, and occlusion model, enabling systematic comparison of OCS-only, image-only, and multi-modal fusion approaches. Through controlled experiments under both ideal and degraded observation conditions—including simple image degradation tests motivated by realistic observation artifacts—we reveal that clean synthetic images provide an upper-bound for image-based inversion that does not transfer to degraded conditions, while OCS offers robust photometric constraints within the simulation domain. No real optical telescope validation is performed; all conclusions are bounded to the controlled simulation environment.

---

## 3. Revised One-Sentence Argument

```text
In space object attitude inversion under nonuniform BRDF and self-occlusion, we show that OCS and photometric images provide conditionally complementary constraints whose fusion value depends on observation quality, using a unified GGX-driven simulation framework with multi-geometry OCS and pixel-level rendered images, supported by evidence that clean-image CNNs achieve 1.69° mean error but collapse to 86° under controlled image degradation tests while OCS-only inversion remains unaffected within the simulation, with the boundary that all results are obtained in a controlled simulation environment without real optical telescope validation.
```

---

## 4. Revised Abstract Skeleton

### Sentence 1: Context/Problem

> Accurate attitude estimation of space objects is critical for space situational awareness, yet existing approaches typically treat optical cross section (OCS) signatures and photometric images as independent modalities without a unified physical model connecting them.

中文说明：不变，建立领域需求。

### Sentence 2: Gap

> It remains unclear under what observation conditions each modality provides reliable attitude constraints, and whether their fusion offers robust complementary benefits or merely redundant information.

中文说明：不变，指出核心知识空白。

### Sentence 3: Approach

> We develop a unified BRDF-driven simulation framework that generates physically consistent OCS signatures and photometric images from the same satellite STL geometry, GGX/Cook-Torrance material model, and ray-traced self-occlusion, enabling controlled attitude inversion experiments across OCS-only, image-only, and multi-modal fusion configurations.

中文说明：去掉 "ideal and degraded" 的具体描述，留给后面两句展开。

### Sentence 4: Clean-Image Upper-Bound Result

> Under clean synthetic images, a ResNet-18 model achieves a mean angular error of 1.69° with 97.6% of predictions within 5°, establishing an upper-bound for image-based inversion; incorporating multi-geometry OCS features further reduces the worst-case error from 9.9° to 6.6°.

中文说明：**修改点**——去掉 Hit@5°=99.7% 细节，只保留 worst-case 改善作为融合增益的代表性证据。

### Sentence 5: Degradation / OCS / Fusion Insight

> However, this clean-image performance does not transfer to degraded conditions: controlled image degradation tests show that 1% additive Gaussian noise degrades the ResNet to 85.9° mean error, whereas the OCS-only result (5.91°) is unaffected because it does not depend on image inputs; the fusion compensation gain increases monotonically from +2.0° to +6.3° as OCS noise rises from 0% to 20%, demonstrating conditional rather than universal complementarity.

中文说明：**修改点**——(1) "realistic degradation" → "controlled image degradation tests"；(2) OCS 鲁棒性表述改为"不依赖图像输入所以不受影响"，而非暗示 OCS 本身无噪声。

### Sentence 6: Bounded Implication

> These findings, obtained entirely within a controlled simulation environment, provide quantitative guidance for multi-modal observation strategy design and motivate future validation with real optical telescope data under atmospheric and sensor degradation.

中文说明：不变，限定边界 + 指出意义。

---

## 5. Revised Contributions

### Contribution 1: Unified Physical Forward Model

**Statement:** We develop a unified simulation framework that generates physically consistent OCS signatures and photometric images from the same satellite geometry, nonuniform GGX/Cook-Torrance BRDF, and ray-traced self-occlusion model, ensuring that both modalities share identical physical assumptions.

**Primary evidence:** Three-way closure validation on canonical geometries (single plate, cube) achieves ≤0.25% relative error; five observation geometries covering 24°–120° phase angles produce 13,505 attitude-OCS pairs; 2,701 photometric images rendered via exact BRDF post-processing.

**Boundary:** Material parameters are nominal literature values. Atmosphere, detector response, and PSF are not modeled.

---

### Contribution 2: Controlled Attitude Inversion Benchmark

**Statement:** We construct a controlled yaw-pitch attitude inversion benchmark that systematically compares OCS-only (MLP), image-only (TinyCNN, ResNet-18), late fusion, and feature fusion under consistent data splits, evaluation metrics, and multiple random seeds.

**Primary evidence:** 10°-train → 5°-test interpolation split; random 80/10/10 split for consistency; 5-seed averaging; fair single-geometry ablation (phase63 OCS vs phase63 image).

**Boundary:** Task limited to yaw-pitch with fixed roll. Image branch uses phase63 only. Training set is modest (563 samples for interpolation split).

---

### Contribution 3: Clean-Image Upper Bound and Fragility

**Statement:** We show that high-capacity image models achieve very high accuracy under clean synthetic images, establishing an upper bound for image-based attitude inversion, but this performance collapses under controlled image degradation tests, revealing extreme sensitivity to observation quality.

**Primary evidence:**
- ResNet-18 clean: 1.69 ± 0.07°, Hit@5° = 97.6%
- 1% Gaussian noise: 85.85 ± 3.00°, Hit@5° = 2.2%

**Candidate secondary evidence (for Results section, not abstract):** brightness ×0.5: 3.45°.

**Boundary:** The clean-image result is an idealized upper bound, not a prediction of field performance. The degradation tests use simple additive Gaussian noise and brightness scaling, not a full atmospheric/detector model.

---

### Contribution 4: Robust OCS and Conditional Fusion

**Statement:** We demonstrate that in the controlled simulation, OCS-only inversion is unaffected by image degradation because it does not depend on image inputs, and that OCS-image fusion gain is conditional: under clean images it improves tail errors, while under degraded OCS conditions the image compensation gain increases monotonically.

**Primary evidence:**
- OCS MLP per_part_log: 5.91 ± 0.22°, stable regardless of image noise
- ResNet + OCS fusion (clean): worst-case reduced from 9.9° to 6.6° (−33%)
- OCS-noise experiment: fusion gain +1.97° (0% noise) → +6.29° (20% noise)

**Candidate secondary evidence:** OCS-image error correlation r = 0.003 (measured on TinyCNN + OCS MLP pair, not yet confirmed for ResNet pair).

**Boundary:** OCS "robustness" is demonstrated within the simulation where OCS computation is deterministic; real OCS measurements would still be affected by photometric calibration errors and sensor noise. The per_part_log feature (30D) requires component-resolved OCS.

---

## 6. Revised Claim-Evidence-Boundary Notes

| # | Claim | Evidence | Boundary |
|---|---|---|---|
| 1 | Unified framework produces physically consistent OCS and images | Three-way closure ≤0.25% on plate/cube; shared `eval_ggx()` and material DB | Validated on canonical geometries; real satellite has sampling-semantic gap |
| 2 | Multi-geometry OCS improves attitude discrimination | Single-geom: 21.68°; concat5 per_part: 5.91°; concat5 all: 3.98° (semi-oracle) | all_raw 45D is semi-oracle; per_part requires component-resolved OCS; detailed values for Results/Ablation, not Abstract |
| 3 | Clean synthetic images enable very high image-based accuracy | ResNet-18: 1.69 ± 0.07°, Hit@5°=97.6%; data audit confirms no leakage | Clean rendered images only; not a field performance estimate |
| 4 | Image accuracy is fragile under controlled degradation | 1% Gaussian noise → 85.85°; brightness ×0.5 → 3.45° | Only simple degradation tested; real degradation is more complex (seeing, PSF, tracking) |
| 5 | OCS-only inversion is unaffected by image degradation in simulation | OCS MLP 5.91° regardless of image noise level | OCS does not use image inputs; real OCS has calibration/sensor noise |
| 6 | Fusion improves tail errors under clean images | Worst-case: 9.9° → 6.6° (−33%); mean: 1.69° → 1.47° | Mean improvement modest; fusion value primarily in tails and Hit@5° |
| 7 | Fusion gain increases as OCS quality degrades | Gain: +1.97° (0%) → +6.29° (20%), monotonic | Image branch assumed clean in this experiment |
| 8 | OCS and image errors are near-uncorrelated | r = 0.003 (TinyCNN + OCS MLP pair) | **Not yet measured for ResNet pair**; should not be generalized without verification |
| 9 | Self-occlusion modeling is necessary | Occlusion rate 60%–78.5%; mhd=1.0mm validated | Specific to this STL geometry |
| 10 | BRDF model choice affects OCS magnitude | Metal roughness ±20% → OCS change 30–42%; non-metal <5% | Nominal parameters; no real material calibration |

---

## 7. Remaining Author-Check Items

1. **标题确认**：是否接受推荐标题 "BRDF-Driven Optical Cross Section and Photometric Image Simulation for Space Object Attitude Inversion: A Controlled Benchmark Study"？若嫌长，是否用压缩版？

2. **目标期刊**：主投 Acta Astronautica 还是 ASR？影响标题长度限制和 Method 详细程度。

3. **ResNet 定位**：正文以 ResNet-18 为主图像 baseline，TinyCNN 作为 lightweight baseline 简要提及或放补充材料？

4. **r = 0.003 处理**：是否在投稿前补测 ResNet + OCS MLP 的误差相关性？若不补测，论文中需注明来源为 TinyCNN pair。

5. **Feature fusion (TinyCNN-based, 4.10°) 的位置**：是否放入正文消融部分作为"轻量模型融合 baseline"，与 ResNet fusion (1.47°) 形成对比？

6. **论文语言**：正文英文，是否需要中文翻译版供导师审阅？

7. **补充实验优先级**：是否在投稿前补做 cross-phase sanity test（用 phase90 图像测试 phase63 训练的 ResNet）？还是写入 Future Work？

---

*返修完成。等待作者确认后进入 Step 2: Introduction 初稿。*
