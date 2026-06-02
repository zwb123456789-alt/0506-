# Step 5 Output: Results

> 本阶段任务：基于 Step 1-4 已定稿的主线和 Method，生成 Results 章节的证据链、结构、英文初稿、图表计划、结果表格和审稿风险自检。

---

## A. Results Evidence Ladder

1. §4.1 验证 forward model 的物理一致性 → 建立后续所有反演结果的可信度基础。
2. §4.2 展示 OCS-only 反演能力 → 证明 OCS 是有效的独立姿态信号源（per_part_log 5.91°）。
3. §4.2 展示多几何增益 → 证明多观测几何对 OCS 姿态辨识的决定性作用。
4. §4.3 展示 TinyCNN → ResNet 的图像能力阶梯 → 证明图像模态含丰富姿态信息，ResNet 建立 clean upper-bound。
5. §4.4 展示 ResNet+OCS fusion → 证明即使图像已很强，OCS 仍改善 tail errors（worst 9.9°→6.6°）。
6. §4.5 展示 1% noise 崩溃 → 证明 clean-image 性能不可迁移到退化条件。
7. §4.5 展示 OCS 不受图像退化影响 → 证明 OCS 的鲁棒性价值。
8. §4.5 展示 OCS noise 下 fusion gain 递增 → 证明互补性是条件性的，随退化程度增强。
9. §4.6 消融/敏感性 → 审稿防御：split 公平性、BRDF 参数、遮挡必要性、roll 影响。
10. 全章逻辑：clean upper-bound → fragility → OCS robustness → conditional fusion = 论文核心发现。

---

## B. Section Outline

### §4.1 Forward-Model Validation and OCS Signature Analysis

- **Topic sentence:** The unified forward model produces physically consistent OCS signatures and photometric images, as verified through analytical closure tests and self-occlusion validation on canonical geometries.
- **Key evidence:** Three-way closure ≤ sub-percent on simple geometries; occlusion validation (single plate, double plate, U-block, nested cylinder); occlusion rates 60%–78.5% across geometries; OCS heatmaps showing attitude-dependent structure.
- **Figure/table target:** Fig. 3 (OCS heatmaps, component contribution, occlusion rate).
- **Boundary:** Validation is on canonical/synthetic geometries + rendering consistency; not real telescope validation.

### §4.2 OCS-Only Attitude Inversion and Multi-Geometry Constraints

- **Topic sentence:** Multi-geometry OCS features provide effective attitude constraints, with per-component features achieving 5.91° mean error in the controlled benchmark.
- **Key evidence:** OCS MLP per_part_log 5.91°; all_raw 3.98° (semi-oracle); total_log 36.69° (weak); multi-geometry gain over single geometry.
- **Figure/table target:** Table 2 (main inversion results); part of Fig. 4.
- **Boundary:** all_raw is semi-oracle; per_part requires component-resolved OCS.

### §4.3 Image-Only Inversion: From TinyCNN to ResNet Clean-Image Upper Bound

- **Topic sentence:** Under clean synthetic images, a ResNet-18 model achieves 1.69° mean error, establishing an idealized upper bound for image-based attitude inversion that substantially exceeds the lightweight TinyCNN baseline.
- **Key evidence:** TinyCNN 12.38°; ResNet 1.69°; data audit (no leakage, centroid correlation is physical cue).
- **Figure/table target:** Table 2; part of Fig. 4.
- **Boundary:** Clean-image result is upper bound, not field performance; centroid cue may not transfer to real tracking.

### §4.4 OCS-Image Fusion Under Clean Images

- **Topic sentence:** Incorporating multi-geometry OCS features into the ResNet-based model provides modest but meaningful improvements in tail errors and prediction reliability under clean image conditions.
- **Key evidence:** ResNet+OCS 1.47° (mean −13%); worst-case 9.9°→6.6° (−33%); Hit@5° 97.6%→99.7%.
- **Figure/table target:** Table 3 (ResNet fusion); part of Fig. 4.
- **Boundary:** Mean improvement is modest (0.22°); fusion value is primarily in tails; not universally best.

### §4.5 Robustness Under Controlled Observation Degradation

- **Topic sentence:** The clean-image upper bound does not transfer to degraded conditions: controlled image degradation tests reveal catastrophic fragility of the ResNet model, while OCS-based inversion remains unaffected within this benchmark.
- **Key evidence:** 1% noise → 85.85°; brightness ×0.5 → 3.45°; OCS MLP stable at 5.91°; OCS-noise fusion gain +1.97° → +6.29°.
- **Figure/table target:** Fig. 5 (image degradation); Fig. 6 (OCS noise + fusion gain); Table 4.
- **Boundary:** Gaussian noise is controlled stress test, not full atmospheric model; OCS robustness is within simulation (no real calibration noise).

### §4.6 Ablation and Sensitivity Analysis

- **Topic sentence:** Supplementary ablation experiments confirm the robustness of the main findings to data split strategy, BRDF parameter perturbation, self-occlusion modeling, and roll variation.
- **Key evidence:** Random split consistency; BRDF sensitivity (metal roughness ±20% → OCS 30–42%); occlusion rates; roll ~20% OCS variation.
- **Figure/table target:** Fig. 7 (sensitivity summary); part of Table 4.
- **Boundary:** These are reviewer-defense items; not new main findings.

---

## C. Results Draft

### 4.1 Forward-Model Validation and OCS Signature Analysis

The physical consistency of the unified forward model is verified through analytical closure tests on canonical geometries. For single-plate and cube configurations, the three-way comparison between analytical solutions, facet-level OCS integration, and pixel-level image-based OCS achieves agreement within sub-percent relative error, confirming that the BRDF evaluation, geometric projection, area computation, and visibility logic are correctly implemented across both the OCS and image generation pathways.

Self-occlusion modeling is validated on four synthetic test geometries: a single plate (verifying self-intersection suppression), a double plate (verifying cross-component occlusion detection), a U-block (verifying internal same-component occlusion), and a nested cylinder (verifying extreme enclosure scenarios). All tests pass their expected occlusion detection criteria. The minimum hit distance parameter ($d_{\min} = 1.0$ mm) is confirmed through sensitivity analysis on the real satellite model, where the occlusion ratio remains stable for $d_{\min} \leq 1.0$ mm but drops sharply at larger values as genuine near-neighbor occlusion is incorrectly suppressed.

The OCS signatures of the real satellite model exhibit strong attitude dependence. Across the five observation geometries, the mean occlusion rate ranges from approximately 60% (near-backscatter) to 78.5% (forward-scatter), reflecting the complex self-shadowing behavior of the non-convex three-component geometry. The metallic main body dominates the OCS contribution due to its strong specular reflection under the GGX model (roughness = 0.20, metallic = 1), while the baffle contributes minimally due to its high roughness and low base reflectance. These attitude-dependent OCS patterns form the physical basis for OCS-based attitude inversion.

### 4.2 OCS-Only Attitude Inversion and Multi-Geometry Photometric Constraints

Multi-geometry OCS features provide effective attitude constraints within the controlled benchmark. Using the per-component log-transformed OCS features across five observation geometries (per\_part\_log, 30D), the MLP achieves a mean angular error of 5.91 ± 0.22° with 73.8% of predictions within 5° of the true attitude. This demonstrates that scalar photometric measurements, when collected across multiple observation geometries and resolved by component, carry substantial attitude information.

The full diagnostic representation (all\_raw, 45D), which additionally includes occlusion ratios and unoccluded OCS values, achieves 3.98 ± 0.60° mean error with 90.7% Hit@5°. However, this representation includes quantities that are not readily available from real photometric observations and is therefore reported as a semi-oracle upper bound rather than a practical operating point.

The importance of multi-geometry observations is evident from the feature-level comparison: total OCS features from a single observation geometry yield mean errors exceeding 50° [需要作者确认：exact single-geom total OCS MLP mean error for 10°→5° split], whereas concatenating five geometries reduces this to 36.69° (total\_log) and further to 5.91° when per-component information is available. This multi-geometry gain demonstrates that diverse photometric sampling is essential for OCS-based attitude discrimination.

### 4.3 Image-Only Inversion: From TinyCNN to ResNet Clean-Image Upper Bound

Under clean synthetic photometric images, image-based models achieve high attitude estimation accuracy that scales with model capacity. The lightweight TinyCNN baseline (approximately 106k parameters) achieves 12.38 ± 0.74° mean error with 26.1% Hit@5°, demonstrating that even a compact model can extract meaningful attitude information from single rendered images. However, this result does not represent the upper bound of image-based inversion capability.

A ResNet-18 model (approximately 11.2M parameters) achieves 1.69 ± 0.07° mean error with 97.6% Hit@5° and 99.9% Hit@10° on the same clean rendered images. This result establishes an idealized upper bound for image-based attitude inversion under perfect photometric rendering conditions. A data audit confirms that no train-test attitude overlap exists under the 10°→5° split, normalization uses fixed constants rather than test-set statistics, and mean image intensity shows negligible correlation with attitude (r < 0.02). The target centroid displacement correlates with yaw (r ≈ 0.66), which is a physical rendering cue arising from the attitude-dependent projected position; however, this cue may not transfer to real telescope observations where tracking systems control image centering.

The ResNet clean-image result should be interpreted as an upper-bound case for image-based inversion under idealized rendered photometric images, not as a field-performance estimate. Real ground-based observations are subject to atmospheric seeing, sensor noise, tracking errors, and point-spread function variations that are absent from the rendered training and test images.

### 4.4 OCS-Image Fusion Under Clean Images

Incorporating multi-geometry OCS features into the ResNet-based model provides modest but meaningful improvements in prediction reliability under clean image conditions. The ResNet + concat5 per\_part\_log fusion model achieves 1.47 ± 0.07° mean error, reducing the mean by 0.22° (13%) compared to the image-only ResNet. More notably, the worst-case error decreases from 9.9° to 6.6° (a 33% reduction), and Hit@5° improves from 97.6% to 99.7%.

These improvements indicate that OCS features provide complementary attitude constraints that are most valuable for reducing tail errors—cases where the image model alone makes its largest mistakes. The fusion benefit is concentrated in the prediction tails rather than the bulk of the distribution, consistent with the interpretation that OCS and image modalities encode partially non-overlapping attitude information.

A comparison across OCS feature levels reveals that the practical per\_part\_log representation (30D) provides the best fusion balance. The semi-oracle all\_raw representation (45D), despite its stronger standalone OCS performance, yields a worse worst-case error (18.7°) in fusion, suggesting that including diagnostic quantities not available in practice may introduce optimization difficulties in the joint model without proportional benefit.

Earlier diagnostic experiments using the TinyCNN image model and OCS MLP showed near-zero error correlation (r = 0.003) between the two modalities, indicating that they tend to fail on different attitude configurations. While this specific correlation has not been re-measured for the ResNet pair, the observed fusion tail improvement is consistent with complementary failure modes.

### 4.5 Robustness Under Controlled Observation Degradation

The clean-image upper bound established in §4.3 does not transfer to degraded observation conditions. Controlled image degradation tests reveal that the ResNet-18 model is catastrophically sensitive to additive noise: introducing Gaussian noise with standard deviation $\sigma = 0.01$ (1% of the normalized intensity range) degrades the mean error from 1.69° to 85.85 ± 3.00°, with Hit@5° collapsing from 97.6% to 2.2%. Further increases in noise level ($\sigma = 0.03, 0.05, 0.10$) produce similarly collapsed performance, indicating that the failure is not gradual but catastrophic once the noise exceeds a threshold.

Brightness scaling is less destructive: reducing intensity by 50% degrades the mean to 3.45° (Hit@5° = 78.7%), while moderate brightness variations (×0.75 to ×1.50) have limited impact (mean remains below 2.03°). This asymmetry suggests that the ResNet relies primarily on spatial pattern features that are preserved under uniform brightness changes but destroyed by pixel-level noise that disrupts local texture and edge information.

In contrast, OCS-based inversion is entirely unaffected by image degradation within this benchmark because OCS features are computed independently of image pixels. The OCS MLP maintains its 5.91° performance regardless of the image noise level applied. This independence is structural rather than learned: OCS is a separate physical measurement that does not pass through the image rendering pipeline.

The conditional nature of multi-modal complementarity is further demonstrated through OCS-noise experiments, where Gaussian noise is added to the OCS features while the image branch remains clean. As OCS noise increases from 0% to 20%, the OCS-only mean error rises from 5.91° to 17.25°, while the fusion model (OCS + clean image) degrades more gracefully from approximately 3.93° to 10.96° [需要作者确认：0% fusion mean = 3.93 ± 0.46°?]. The image compensation gain—defined as the difference between OCS-only and fusion errors—increases monotonically from +1.97° at 0% noise to +6.29° at 20% noise. This demonstrates that fusion becomes increasingly valuable as one modality degrades, confirming that multi-modal complementarity is conditional on observation quality rather than universally guaranteed.

### 4.6 Ablation and Sensitivity Analysis

Supplementary experiments confirm the robustness of the main findings to methodological choices and parameter variations.

**Data split consistency.** The main results use a structured 10°→5° interpolation split. A random 80/10/10 split yields consistent trends with improved absolute performance (fusion per\_part\_log: 2.13°, Hit@5° = 98.6%), confirming that the interpolation split is a more challenging but scientifically meaningful evaluation protocol [需要作者确认：random split exact numbers].

**BRDF parameter sensitivity.** Perturbing the GGX material parameters by ±20% reveals that the metallic main body roughness is the most sensitive parameter, producing 30–42% median OCS variation. The metallic F0 parameter causes 13–16% variation, while non-metallic components (solar panel, baffle) contribute less than 5% variation. This indicates that attitude inversion accuracy is primarily sensitive to the specular reflection characteristics of the dominant metallic component.

**Self-occlusion necessity.** The occlusion rates of 60–78.5% across observation geometries demonstrate that self-occlusion modeling is essential for physically consistent OCS computation. Without occlusion modeling, OCS values would be systematically overestimated, particularly for forward-scatter geometries where complex self-shadowing is most severe.

**Roll sensitivity.** Varying roll angle produces approximately 20% mean OCS variation, with extreme attitudes showing up to 26% change [需要作者确认：exact roll sensitivity numbers]. This confirms that roll is a non-negligible factor and that the present yaw-pitch benchmark represents a controlled subset of the full three-degree-of-freedom attitude estimation problem.

**Phase63 fairness.** A single-geometry ablation comparing phase63 OCS (per\_part, 6D) against phase63 image under the same observation geometry shows that single-geometry OCS achieves approximately 21.68° mean error, while the image achieves 1.69° under clean conditions [需要作者确认：phase63 single-geom OCS MLP exact value]. This confirms that the multi-geometry OCS advantage (5.91° with 5 geometries) arises from geometric diversity rather than an inherent modality superiority.

---

## D. Figure and Table Plan

| Item | Content | Key Data | Caption Intent |
|---|---|---|---|
| Fig. 3 | OCS yaw-pitch heatmaps | Total OCS + per-part + occlusion rate across 5 geometries | "Attitude-dependent OCS signatures and occlusion rates across five observation geometries, showing strong yaw-pitch structure exploited by the inversion models." |
| Fig. 4 | Main inversion comparison | Bar chart or CDF: OCS MLP / TinyCNN / ResNet / ResNet+OCS | "Comparison of attitude inversion methods under clean conditions, showing the ResNet clean-image upper bound and the modest but meaningful fusion improvement in tail errors." |
| Fig. 5 | Image degradation robustness | ResNet mean vs noise level; brightness scaling | "Controlled image degradation tests revealing catastrophic fragility of the ResNet model under additive noise, contrasted with robustness to uniform brightness scaling." |
| Fig. 6 | OCS noise + fusion gain | OCS-only vs fusion mean as function of OCS noise %; gain curve | "Conditional complementarity: image compensation gain increases monotonically as OCS quality degrades, demonstrating that fusion value depends on observation quality." |
| Fig. 7 | Sensitivity summary | BRDF perturbation bars; roll variation; split comparison | "Summary of sensitivity analyses confirming robustness of main findings to BRDF parameters, roll variation, and data split strategy." |
| Table 2 | Main inversion benchmark | All methods: OCS MLP / TinyCNN / ResNet / fusion variants | Main results table with semi-oracle and practical labels |
| Table 3 | ResNet fusion detail | A1–A4 cases with mean, p90, worst, Hit@5°, Hit@10° | Fusion tail improvement evidence |
| Table 4 | Robustness + sensitivity | Image noise / brightness / OCS noise / BRDF / roll | Reviewer-defense summary |

---

## E. Main Results Tables Draft

### Table 2: Main Attitude Inversion Benchmark

| Method | Input | Dim | Mean ± std (°) | Hit@5° | Hit@10° | Role |
|---|---|---:|---:|---:|---:|---|
| OCS MLP | all\_raw (5 geom) | 45 | 3.98 ± 0.60 | 90.7% | 97.1% | Semi-oracle upper bound† |
| OCS MLP | per\_part\_log (5 geom) | 30 | 5.91 ± 0.22 | 73.8% | 94.3% | **Practical OCS-only** |
| OCS MLP | total\_log (5 geom) | 15 | 36.69 ± 3.62 | 9.7% | 23.5% | Weak OCS baseline |
| Weighted kNN | all\_raw (5 geom) | 45 | 21.84 | 47.9% | — | Classical baseline |
| TinyCNN | phase63 image | 128² | 12.38 ± 0.74 | 26.1% | 55.8% | Lightweight image baseline |
| **ResNet-18** | **phase63 image** | **128²** | **1.69 ± 0.07** | **97.6%** | **99.9%** | **Clean-image upper bound** |
| ResNet + OCS | per\_part\_log (5 geom) + image | 30 + 128² | 1.47 ± 0.07 | 99.7% | 100% | Fusion (clean) |

† all\_raw includes occlusion ratios and unoccluded OCS not available from standard photometric observations.

### Table 3: ResNet-Level Fusion Under Clean Images

| Case | Configuration | Mean ± std (°) | P90 (°) | Worst (°) | Hit@5° | Hit@10° |
|---|---|---:|---:|---:|---:|---:|
| A1 | ResNet image-only | 1.69 ± 0.07 | 3.31 | 9.9 | 97.6% | 99.9% |
| **A2** | **ResNet + concat5 per\_part\_log 30D** | **1.47 ± 0.07** | **2.71** | **6.6** | **99.7%** | **100%** |
| A3 | ResNet + phase63 per\_part\_log 6D | 1.61 ± 0.07 | 2.97 | 7.4 | 99.2% | 100% |
| A4 | ResNet + concat5 all\_raw 45D | 1.49 ± 0.10 | 2.70 | 18.7 | 99.2% | 99.9% |

### Table 4: Robustness Under Controlled Degradation

| Condition | ResNet Mean (°) | Hit@5° | OCS MLP Mean (°) | Fusion Mean (°) | Fusion Gain |
|---|---:|---:|---:|---:|---:|
| Clean (baseline) | 1.69 | 97.6% | 5.91 | 1.47 | — |
| Image noise σ=0.01 | 85.85 | 2.2% | 5.91 (unaffected) | — | — |
| Image noise σ=0.05 | 85.97 | 1.2% | 5.91 (unaffected) | — | — |
| Brightness ×0.50 | 3.45 | 78.7% | 5.91 (unaffected) | — | — |
| OCS noise 0% | — | — | 5.91 | [≈3.93] | +1.97° |
| OCS noise 10% | — | — | 9.99 | 6.69 | +3.30° |
| OCS noise 20% | — | — | 17.25 | 10.96 | +6.29° |

---

## F. Claim-Evidence-Risk Map

| # | Claim | Evidence | Risk | Safe Wording |
|---|---|---|---|---|
| 1 | Forward model is physically consistent | Three-way closure ≤ sub-percent; occlusion tests pass | Low | "verified through analytical closure tests on canonical geometries" |
| 2 | OCS per\_part\_log achieves 5.91° | 5-seed MLP experiment | Low | Direct experimental result |
| 3 | ResNet achieves 1.69° under clean images | 5-seed experiment + data audit | Low | "establishing an idealized upper bound" |
| 4 | 1% noise collapses ResNet to 85.85° | Controlled experiment | Medium | "controlled image degradation tests" not "realistic degradation" |
| 5 | OCS is unaffected by image degradation | Structural independence (no image input) | Low | "unaffected within this benchmark because OCS does not depend on image inputs" |
| 6 | Fusion reduces worst-case 9.9°→6.6° | ResNet+OCS experiment | Low | "under clean conditions" |
| 7 | Fusion gain increases with OCS noise | Monotonic trend 0%→20% | Low | "image compensation gain increases monotonically" |
| 8 | Complementarity is conditional | All degradation experiments combined | Low | "conditional on observation quality rather than universally guaranteed" |
| 9 | all\_raw is semi-oracle | Contains occlusion ratio | Low | Clearly labeled |
| 10 | Centroid correlation (r=0.66) is physical cue | Data audit | Medium | "physical rendering cue that may not transfer to field observations" |

---

## G. Self-review Checklist

| # | Question | Answer |
|---|---|---|
| 1 | Did I invent experiments or numbers? | ✅ No — all values from provided data; uncertain items marked [需要作者确认] |
| 2 | Did I write clean image as field performance? | ✅ No — "idealized upper bound" throughout |
| 3 | Did I overstate fusion? | ✅ No — "modest but meaningful", "conditional", "primarily in tails" |
| 4 | Did I write OCS always better than images? | ✅ No — explicitly stated OCS is not the upper bound when clean images available |
| 5 | Did I label all\_raw as semi-oracle? | ✅ Yes — in text, tables, and footnote |
| 6 | Did I limit r=0.003 to TinyCNN/OCS diagnostic? | ✅ Yes — "earlier diagnostic... not re-measured for ResNet pair" |
| 7 | Did I state image degradation is controlled stress test? | ✅ Yes — "controlled image degradation tests" |
| 8 | Did I state no real telescope validation? | ✅ Yes — §4.3 and §4.5 |
| 9 | Did I keep ISAR out of Results? | ✅ Yes — not mentioned |

---

## H. Questions for Author

1. **0% OCS noise 的 fusion mean**：指导文件中标注 [需要作者确认]。根据补充实验数据，0% OCS noise 下 fusion mean 是否为 3.93 ± 0.46°？OCS-only 是否为 5.91 ± 0.22°？

2. **单几何 OCS MLP mean error**：§4.6 phase63 fairness 中写了 "approximately 21.68°"。这是 per\_part\_log 6D 在 10°→5° split 下的 MLP 结果吗？还是 kNN 结果？

3. **BRDF sensitivity / roll sensitivity 具体数值**：当前写了 "30–42% OCS variation" 和 "~20% roll variation"。这些是否为最终可引用数值？是否有更精确的表格可放入 Table 4？

4. **ResNet-fusion 在图像退化下的表现**：Table 4 中 image noise 行的 fusion mean 为空。是否已有 ResNet+OCS fusion 在 noise σ=0.01 下的结果？如果没有，是否写入 Future Work？

5. **Random split 具体数值**：§4.6 写了 "fusion per\_part\_log: 2.13°, Hit@5° = 98.6%"。这是 ResNet fusion 还是 TinyCNN fusion？需要确认以避免混淆。

6. **Angular error formula**：是否已最终确定？当前 Method §3.9 中标注了 [需要作者确认]。如果是欧氏距离 + yaw 周期性处理，需要在正文中写出公式。

---

*Step 5 完成。等待作者确认后进入 Step 6: Discussion / Limitations / Conclusion。*
