# Step 6 Output: Discussion / Limitations / Conclusion

> 本阶段任务：基于 Step 1-5 已完成的主线和 Results，生成 Discussion、Limitations 和 Conclusion 的英文初稿、审稿防御点和风险自检。Discussion 解释结果意义和边界，不重复 Results 表格。

---

## A. Discussion Logic Map

1. §5.1 从 Results 提炼核心发现：OCS 和图像在统一物理模型下提供不同类型的姿态约束 → 互补性是条件性的。
2. §5.2 解释为什么 clean image 下 ResNet 极强 → 因为 clean rendering 保留了所有空间/光度线索 → 但这不代表真实场景。
3. §5.3 解释为什么 OCS 仍然重要 → 不是因为 OCS 比 clean image 更准，而是因为 OCS 低维、可解释、多几何、不依赖图像像素。
4. §5.4 解释 fusion 的条件性 → clean 下改善 tail，退化下增益递增 → fusion 是可靠性机制而非精度最大化器。
5. §5.5 对空间目标观测策略的启示 → 统一框架的价值、观测质量报告的必要性、多模态互补设计。
6. §5.6 诚实声明边界 → 仿真研究、无真实验证、fixed roll、nominal 材料、未建模真实退化。
7. Conclusion 用 2-3 段收束全文 → 重述问题和方法 → 最强证据 → 边界和未来方向。
8. 全章逻辑：interpretation → implication → boundary → future = 完整的学术闭环。

---

## B. Section Outline

| Section | Goal | Key Interpretation | Evidence to Cite | Boundary/Risk |
|---|---|---|---|---|
| 5.1 Main finding | State the core scientific insight | Complementarity is conditional on observation quality | All key numbers from §4.2–4.5 | Don't overstate; it's a simulation finding |
| 5.2 Why clean images are strong | Explain ResNet 1.69° | Clean rendering preserves all spatial/photometric cues | ResNet vs TinyCNN; centroid r=0.66 | Must immediately bound as upper-bound |
| 5.3 Why OCS remains useful | Explain OCS value proposition | Low-cost, interpretable, multi-geometry, pixel-independent | per_part_log 5.91°; unaffected by image noise | Don't say OCS beats images or is noise-immune in reality |
| 5.4 Conditional fusion | Explain when fusion helps | Tail improvement clean; gain increases with degradation | worst 9.9→6.6; gain +1.97→+6.29 | Don't say universally best |
| 5.5 Implications | Connect to SSA practice | Unified models enable fair comparison; report clean vs degraded separately | Framework design; observation strategy | Don't promise deployment |
| 5.6 Limitations | Honest boundary | Simulation-focused; no field data; fixed roll; nominal materials | List of 8 limitations | Don't self-destruct; frame as controlled scope |
| 6. Conclusion | Summarize and close | Restate problem → strongest evidence → boundary → future | 3-4 key numbers only | No new results |

---

## C. Discussion Draft

### 5.1 Main Finding: Conditional Complementarity Between OCS and Photometric Images

The central finding of this study is that scalar OCS signatures and resolved photometric images provide qualitatively different attitude constraints under a unified BRDF-driven forward model, and that their relative value depends fundamentally on observation quality. Under idealized clean rendering conditions, a high-capacity image model exploits rich spatial and photometric cues to achieve very high accuracy, establishing an upper bound that scalar OCS measurements cannot match in absolute terms. However, this image-based upper bound is structurally fragile: it relies on the preservation of pixel-level patterns that are easily disrupted by observation degradation. In contrast, OCS-based inversion provides a lower but stable constraint that is independent of image-pixel quality within this benchmark.

This observation reframes the relationship between OCS and images from a simple accuracy competition to a conditional complementarity: the modalities are not redundant, nor is one universally superior. Rather, their relative contribution shifts with observation conditions. Multi-modal fusion captures this complementarity by improving tail errors under clean conditions and providing increasing compensation as one modality degrades. The study thus contributes not a single best method, but a quantitative characterization of when and why each modality is valuable.

### 5.2 Why Clean Rendered Images Provide a Strong Image-Only Upper Bound

The ResNet-18 model achieves 1.69° mean error under clean synthetic images—substantially exceeding the OCS-only practical result of 5.91°. This performance arises because clean rendered photometric images preserve multiple attitude-dependent cues simultaneously: projected shape and silhouette, shadow boundaries, component-level brightness distribution, specular highlight positions, and target centroid displacement. A high-capacity convolutional network can jointly exploit these cues to achieve fine-grained attitude discrimination.

The data audit confirms that the network does not rely on trivial shortcuts: mean image intensity shows negligible correlation with attitude (r < 0.02), and the centroid displacement correlation with yaw (r ≈ 0.66) reflects a genuine physical rendering effect rather than a labeling artifact. However, this centroid cue arises from the fixed camera-target geometry in the simulation and may not transfer to real telescope observations where tracking systems actively center the target in the field of view.

Critically, this clean-image result should not be interpreted as a field-performance estimate. Real ground-based optical observations of space objects are subject to atmospheric seeing, sensor readout noise, tracking jitter, point-spread function variation, background contamination, and illumination changes across the orbit. The controlled degradation tests in §4.5 demonstrate that even minimal additive noise (1% of the intensity range) is sufficient to collapse the ResNet performance catastrophically, indicating that the clean-image accuracy is not robust to the types of perturbation expected in real observations.

### 5.3 Why OCS Remains Valuable Despite Lower Clean-Image Accuracy

OCS does not compete with clean-image models on absolute accuracy under idealized conditions. Its value lies in four complementary properties:

First, OCS is low-dimensional and physically interpretable. Each OCS value directly corresponds to the integrated BRDF response over visible surface elements, providing a transparent link between the measurement and the underlying physical scattering process. This interpretability supports diagnostic analysis and physical validation in ways that learned image features do not.

Second, OCS measurements are naturally available across multiple observation geometries as a space object traverses its orbit, providing diverse photometric sampling at low marginal cost. The multi-geometry gain demonstrated in this study—from single-geometry total OCS (mean error > 36°) to five-geometry per-component features (5.91°)—shows that geometric diversity is the key enabler of OCS-based attitude discrimination.

Third, within this benchmark, OCS computation is structurally independent of image pixels. It does not pass through the rendering pipeline and is therefore unaffected by image-level degradation. This independence is not a learned robustness but a structural property of the measurement modality.

Fourth, OCS measurements require only photometric detection (total flux), not spatially resolved imaging. This makes OCS accessible with smaller aperture telescopes and under conditions where resolved imaging is impractical due to distance, atmospheric conditions, or target size.

These properties position OCS not as a competitor to high-quality resolved images, but as a complementary constraint that provides robustness and interpretability when image quality is uncertain or degraded. Real OCS measurements would still be subject to photometric calibration errors, BRDF model mismatch, and measurement noise; the structural independence demonstrated here applies specifically to image-pixel degradation within the controlled simulation.

### 5.4 Conditional Value of OCS-Image Fusion

The fusion results reveal that multi-modal combination is conditionally beneficial rather than universally superior. Under clean image conditions, incorporating OCS features into the ResNet model reduces the mean error modestly (1.69° → 1.47°, a 13% improvement) but provides more substantial improvements in tail behavior: the worst-case error decreases from 9.9° to 6.6° (33% reduction) and Hit@5° improves from 97.6% to 99.7%. These tail improvements indicate that OCS provides complementary constraints precisely for the attitudes where the image model alone makes its largest errors.

The conditional nature of fusion value is further demonstrated by the OCS-noise experiments: as OCS quality degrades from 0% to 20% noise, the image compensation gain increases monotonically from +1.97° to +6.29°. This confirms that fusion becomes more valuable when one modality weakens, consistent with the interpretation that the two modalities encode partially non-overlapping attitude information.

However, fusion is not without risk. The all\_raw representation (45D), despite its stronger standalone OCS performance, produces a worse worst-case error (18.7°) in fusion than the more practical per\_part\_log representation (6.6°). This suggests that including overly strong or semi-oracle features can introduce optimization difficulties without proportional benefit, and that fusion architecture design must account for the information balance between modalities.

Fusion should therefore be viewed as a conditional reliability mechanism—improving tail errors and providing degradation robustness—rather than a universal accuracy maximizer. Its operational value is greatest when observation quality is uncertain or when the system must maintain reliability across varying conditions.

### 5.5 Implications for Space Object Attitude Inversion

The findings of this controlled benchmark suggest several implications for the design of space object attitude estimation systems:

First, unified physical forward models that generate both OCS and image predictions from shared assumptions enable fair modality comparison and physically grounded fusion design. Without such consistency, apparent modality differences may reflect modeling inconsistencies rather than genuine information content differences.

Second, image-based inversion results obtained under clean synthetic conditions should be reported separately from degraded-condition performance. The gap between clean upper-bound accuracy and degraded-condition accuracy may be very large, and conflating the two can lead to overoptimistic system design expectations.

Third, OCS provides a low-cost additional photometric constraint that can improve system reliability when high-quality resolved images are unavailable or unreliable. Multi-geometry OCS collection is operationally feasible for photometric monitoring campaigns and can complement imaging observations without requiring additional large-aperture telescope resources.

Fourth, tail error and prediction reliability metrics (Hit@5°, worst-case) may be as important as mean error for operational attitude estimation, particularly in conjunction assessment and anomaly detection scenarios where individual large errors can have disproportionate consequences.

### 5.6 Scope and Limitations

This study is conducted entirely within a controlled simulation environment and is subject to several important limitations:

No real optical telescope observations with known attitude ground truth are used. The reported accuracies—particularly the clean-image upper bound—should not be interpreted as predictions of field performance. Validation with real ground-based telescope data under atmospheric and sensor degradation remains an essential future step.

The clean rendered images are free from atmospheric turbulence, sensor noise, tracking errors, point-spread function variations, earthshine, and background contamination. They therefore represent an idealized upper-bound condition that is unlikely to be achieved in practice. The controlled degradation tests (additive Gaussian noise, brightness scaling) provide initial stress-test evidence but do not constitute a comprehensive atmospheric or detector degradation model.

The current benchmark estimates yaw and pitch under fixed roll. Real satellite attitude is three-dimensional, and the roll sensitivity analysis (approximately 20% OCS variation) confirms that roll is a non-negligible factor. Extension to full three-degree-of-freedom attitude estimation requires substantially larger datasets and is planned as future work.

The main image branch uses a single observation geometry (phase63). Cross-phase image generalization has not been systematically evaluated and represents an important direction for future investigation.

Material parameters are nominal literature values rather than calibrated measurements of the specific target. The BRDF sensitivity analysis shows that metallic roughness is the most influential parameter (30–42% OCS variation under ±20% perturbation), indicating that material uncertainty is a relevant factor for absolute OCS accuracy. However, the conditional complementarity finding—that fusion value depends on observation quality—is expected to be robust to moderate parameter variations because it reflects structural modality differences rather than specific parameter choices.

OCS robustness within this benchmark arises from structural independence of image pixels, not from immunity to all observational errors. Real OCS measurements would be affected by photometric calibration uncertainty, atmospheric extinction, BRDF model mismatch, and detector noise. The present results characterize OCS behavior under controlled conditions and motivate future investigation of OCS robustness under realistic photometric measurement errors.

---

## D. Limitations Draft

(This can be placed as §5.6 within Discussion or as a standalone section.)

This study is a physically consistent simulation and controlled inversion benchmark. Several limitations bound the interpretation of the reported results.

First, no real optical telescope observations with known attitude ground truth are used. The credibility of the framework rests on analytical closure validation, rendering consistency checks, self-occlusion verification on canonical geometries, BRDF sensitivity analysis, and alignment with trends reported in the satellite photometry literature. Future validation with ground-based telescope data under realistic atmospheric and sensor conditions is essential before the findings can inform operational system design.

Second, the clean-image results represent an idealized upper bound. The rendered images exclude atmospheric seeing, sensor noise, tracking errors, PSF variation, earthshine, and background contamination. The controlled degradation tests (Gaussian noise, brightness scaling) provide initial fragility evidence but do not constitute a comprehensive observation degradation model. More realistic degradation chains—including atmospheric turbulence simulation, detector response modeling, and tracking error injection—are needed to bridge the gap between simulation and field performance.

Third, the benchmark is limited to yaw-pitch estimation under fixed roll. The roll sensitivity experiment confirms that roll variation produces approximately 20% OCS change, indicating that the present two-axis benchmark is a controlled subset of the full attitude estimation problem. Extension to three-degree-of-freedom estimation with roll is computationally feasible within the framework but requires approximately 37× larger datasets.

Fourth, the image branch uses a single observation geometry (phase63). The OCS branch benefits from five geometries because each geometry yields only a scalar measurement, whereas a single image provides 16,384 pixel values. Cross-phase image generalization has not been systematically tested and remains a direction for future work.

Fifth, material parameters are nominal rather than target-calibrated. The sensitivity analysis shows that metallic roughness dominates OCS uncertainty (30–42% variation under ±20% perturbation), while non-metallic components contribute less than 5%. Material calibration from real photometric observations would improve absolute accuracy but is beyond the scope of the present controlled benchmark.

Sixth, OCS independence from image-pixel degradation is a structural property of the simulation design, not a claim of immunity to all real-world observational errors. Real OCS measurements are subject to photometric calibration uncertainty, atmospheric extinction, and detector noise that are not modeled here.

These limitations define the scope of the present work as a controlled benchmark study. They do not invalidate the core finding—that OCS and images provide conditionally complementary attitude constraints—but they bound its applicability to the simulation domain until future field validation is conducted.

---

## E. Conclusion Draft

This study develops a unified BRDF-driven simulation framework that generates physically consistent optical cross section signatures and photometric images from the same satellite geometry, nonuniform GGX/Cook-Torrance material model, and ray-traced self-occlusion. Using this framework, we construct a controlled yaw-pitch attitude inversion benchmark and systematically compare OCS-only, image-only, and multi-modal fusion approaches under both ideal and degraded observation conditions.

The key findings are: (1) under clean synthetic images, a ResNet-18 model achieves 1.69° mean angular error, establishing an idealized upper bound for image-based inversion; (2) this performance is catastrophically fragile—1% additive noise degrades the model to 85.85°; (3) OCS-based inversion provides a stable 5.91° constraint that is structurally independent of image-pixel quality within this benchmark; and (4) OCS-image fusion provides conditional benefits, reducing worst-case errors from 9.9° to 6.6° under clean conditions while the fusion compensation gain increases monotonically from +2.0° to +6.3° as OCS quality degrades.

These results demonstrate that multi-modal complementarity between OCS and photometric images is conditional on observation quality rather than universally guaranteed. The study is conducted entirely within a controlled simulation environment without real optical telescope validation. Future work will pursue validation with ground-based telescope observations, extension to three-degree-of-freedom attitude estimation including roll, cross-phase image generalization, and more comprehensive observation degradation modeling to bridge the gap between the controlled benchmark and operational space object attitude estimation.

---

## F. Reviewer-Facing Defense Points

| # | Reviewer Question | Suggested Response |
|---|---|---|
| 1 | Why no real telescope validation? | "The study is explicitly positioned as a controlled simulation benchmark. Credibility is supported by analytical closure tests, rendering consistency, self-occlusion validation, BRDF sensitivity analysis, and alignment with satellite photometry literature. Real validation is identified as the primary future work direction." |
| 2 | Why bother with OCS if ResNet clean is 1.69°? | "The clean-image result is an idealized upper bound that collapses under 1% noise (85.85°). OCS provides a stable constraint (5.91°) independent of image quality. In operational settings where image quality is uncertain, OCS offers robustness that clean-image accuracy cannot guarantee." |
| 3 | Why does 1% noise collapse ResNet? | "The ResNet is trained and tested on clean rendered images. It has learned pixel-level patterns (edges, textures, specular highlights) that are destroyed by additive noise. This is a known vulnerability of CNNs trained on synthetic data without domain randomization or noise augmentation. The collapse demonstrates the fragility of clean-image performance, not a flaw in the model architecture." |
| 4 | Why is fusion improvement only 0.22° in mean? | "Fusion value is concentrated in tail errors (worst-case −33%, Hit@5° +2.1pp) rather than mean. When the image model is already very strong, the marginal contribution of OCS is small in the bulk but meaningful in the tails. Fusion becomes more valuable as observation quality degrades (+6.29° gain at 20% OCS noise)." |
| 5 | Why fixed roll? | "The present benchmark focuses on yaw-pitch as a controlled two-axis problem. Roll sensitivity (~20% OCS variation) is reported separately. Full 3-DOF extension requires ~37× larger datasets and is planned as future work. The framework is architecturally roll-extensible." |
| 6 | Why nominal BRDF parameters? | "Parameters are based on published optical constants (aluminum F0, glass IOR, dark coating reflectance). Sensitivity analysis shows metallic roughness is the dominant factor (30–42% OCS variation). The conditional complementarity finding is expected to be robust to moderate parameter variations because it reflects structural modality differences." |
| 7 | Why only phase63 for images? | "OCS uses 5 geometries because each yields 1 scalar; one image yields 16,384 pixels. The information density asymmetry justifies the design. Cross-phase generalization is acknowledged as a limitation and future work direction." |
| 8 | Is this just a software demo? | "No. The contribution is a quantitative characterization of conditional complementarity between OCS and images under controlled conditions—a scientific finding about modality information content, not a software tool. The unified framework enables this finding; it is the means, not the end." |

---

## G. Claim-Evidence-Risk Map

| # | Claim | Evidence | Risk | Safe Wording |
|---|---|---|---|---|
| 1 | OCS and images provide conditionally complementary constraints | All degradation + fusion experiments | Low | "within this controlled benchmark" |
| 2 | Clean-image performance is an idealized upper bound | ResNet 1.69° + 1% noise collapse to 85.85° | Low | "should not be interpreted as field performance" |
| 3 | OCS is structurally independent of image-pixel degradation | OCS does not use image inputs | Low | "within this benchmark"; real OCS has calibration noise |
| 4 | Fusion improves tail errors under clean conditions | Worst 9.9°→6.6°; Hit@5° 97.6%→99.7% | Low | "modest mean improvement but meaningful tail reduction" |
| 5 | Fusion gain increases with OCS degradation | +1.97° → +6.29° monotonic | Low | "image compensation gain increases monotonically" |
| 6 | Multi-geometry is essential for OCS discrimination | Single-geom >36° vs concat5 5.91° | Low | Supported by ablation |
| 7 | Centroid cue may not transfer to real observations | r=0.66 is physical but tracking-dependent | Medium | "may not transfer to field observations where tracking controls centering" |
| 8 | Material sensitivity is manageable | ±20% roughness → 30–42% OCS; non-metal <5% | Medium | "nominal parameters; sensitivity reported" |
| 9 | Roll is non-negligible but bounded | ~20% OCS variation | Low | "controlled subset; extension planned" |
| 10 | The study is not just a software demo | Quantitative conditional complementarity finding | Medium | "scientific finding about modality information content" |

---

## H. Self-review Checklist

| # | Question | Answer |
|---|---|---|
| 1 | Did I write clean image as field performance? | ✅ No — "idealized upper bound", "should not be interpreted as field-performance estimate" |
| 2 | Did I claim real optical telescope validation? | ✅ No — "no real telescope observations... are used" |
| 3 | Did I overstate fusion? | ✅ No — "conditional reliability mechanism rather than universal accuracy maximizer" |
| 4 | Did I write OCS always better than images? | ✅ No — "OCS does not compete with clean-image models on absolute accuracy" |
| 5 | Did I write OCS immune to all noise? | ✅ No — "real OCS measurements would be affected by photometric calibration uncertainty" |
| 6 | Did I write all\_raw as practical feature? | ✅ No — "semi-oracle" in §5.4 |
| 7 | Did I write r=0.003 as ResNet-pair evidence? | ✅ No — not mentioned in Discussion (kept in Results as TinyCNN diagnostic only) |
| 8 | Did I invent experiments or numbers? | ✅ No — all values from provided data |
| 9 | Are limitations honest and sufficient? | ✅ Yes — 6 explicit limitations covering all major gaps |
| 10 | Did I keep ISAR out? | ✅ Yes — not mentioned |

---

## I. Questions for Author

1. **Limitations 位置**：是否将 Limitations 作为 Discussion 的 §5.6 子节？还是独立成 §6 Limitations + §7 Conclusion？不同期刊有不同偏好。

2. **0% OCS noise 数值**：Conclusion 中写了 "+2.0° to +6.3°"。0% 的 OCS-only mean 和 fusion mean 具体值是否可确认（5.91° 和 ~3.93°）？

3. **Future Work 是否独立成段**：当前 Conclusion 末尾简要提及 future work。是否需要在 Discussion 末尾或 Conclusion 后单独写一段 Future Work（200-300 words）？

4. **ResNet-fusion 图像退化实验**：Discussion §5.4 提到 fusion 在退化下更有价值，但 Results 中 ResNet+OCS fusion 在 image noise 下的具体数值为空。是否已有该实验结果？如果没有，Discussion 中只能写 "expected to provide robustness" 而非 "demonstrated"。

5. **目标期刊格式**：Acta Astronautica 和 ASR 对 Discussion/Conclusion 的长度和结构有无特殊要求？当前 Discussion ~1500 words + Limitations ~400 words + Conclusion ~250 words 是否合适？

6. **Acknowledgments / Data Availability**：是否需要在本步骤中起草这两个小节？还是留到最终整合阶段？

---

*Step 6 完成。全部 6 步写作初稿已产出。等待作者确认后进入全文整合阶段。*
