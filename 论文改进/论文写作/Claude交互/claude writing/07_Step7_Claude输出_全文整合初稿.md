# Step 7 Output: Integrated Manuscript Draft

> 本文件为 Claude 侧全文整合初稿。基于 Step 1-6 各阶段产出，统一叙事、删减重复、统一术语、保留边界、标注待确认项。

---

## A. Integrated Manuscript Draft

---

# BRDF-Driven Optical Cross Section and Photometric Image Simulation for Space Object Attitude Inversion: A Controlled Benchmark Study

---

## Abstract

Accurate attitude estimation of space objects is critical for space situational awareness, yet existing approaches typically treat optical cross section (OCS) signatures and photometric images as independent modalities without a unified physical model connecting them. It remains unclear under what observation conditions each modality provides reliable attitude constraints, and whether their fusion offers robust complementary benefits or merely redundant information. We develop a unified BRDF-driven simulation framework that generates physically consistent OCS signatures and photometric images from the same satellite STL geometry, GGX/Cook-Torrance material model, and ray-traced self-occlusion, enabling controlled attitude inversion experiments across OCS-only, image-only, and multi-modal fusion configurations. Under clean synthetic images, a ResNet-18 model achieves a mean angular error of 1.69 ± 0.07° with 97.6% of predictions within 5°, establishing an upper bound for image-based inversion; incorporating multi-geometry OCS features further reduces the worst-case error from 9.9° to 6.6°. However, this clean-image performance does not transfer to degraded conditions: controlled image degradation tests show that 1% additive Gaussian noise degrades the ResNet to 85.9° mean error, whereas the OCS-only result (5.91°) is unaffected because it does not depend on image inputs; the fusion compensation gain increases monotonically from +2.0° to +6.3° as OCS noise rises from 0% to 20%, demonstrating conditional rather than universal complementarity. These findings, obtained entirely within a controlled simulation environment, provide quantitative guidance for multi-modal observation strategy design and motivate future validation with real optical telescope data.

**Keywords:** space object attitude estimation; optical cross section; photometric image; BRDF; GGX/Cook-Torrance; multi-modal fusion; controlled benchmark

---

## 1. Introduction

Accurate attitude estimation of resident space objects is essential for space situational awareness, enabling conjunction risk assessment, on-orbit anomaly diagnosis, and debris characterization [CITATION: SSA overview]. Ground-based optical observations offer passive, non-cooperative sensing capabilities that complement radar and telemetry-based approaches [CITATION: optical space object characterization]. A central challenge is to extract reliable attitude information from optical signatures that depend jointly on the object's geometry, surface materials, self-occlusion configuration, and the observation geometry defined by the Sun-object-observer relationship.

Two distinct optical modalities carry attitude-dependent information. Optical cross section (OCS) measurements—scalar quantities representing the total reflected solar flux—are obtainable at low cost across multiple observation geometries and provide physically interpretable photometric constraints [CITATION: light-curve photometry]. Resolved photometric images capture spatially distributed brightness patterns that encode shape silhouettes, shadow boundaries, and component-level reflectance variations, offering richer spatial information per observation [CITATION: image-based spacecraft pose estimation]. These modalities access attitude information through fundamentally different mechanisms: OCS aggregates the surface BRDF contribution over all visible facets into a single value, while images preserve the pixel-level radiance distribution.

However, existing research typically treats these modalities in isolation. Light-curve and OCS inversion studies often employ simplified reflectance models without generating corresponding images [CITATION: light-curve inversion methods], while image-based pose estimation methods rarely enforce physical consistency with OCS predictions or exploit multi-geometry photometric constraints [CITATION: CNN pose estimation]. Two critical gaps remain: first, the absence of a unified physical framework where both modalities share identical geometry, nonuniform BRDF, and self-occlusion assumptions; second, the lack of systematic evaluation of when each modality provides reliable attitude constraints and under what conditions their fusion yields genuine complementary benefit rather than redundant information. In particular, the performance of high-capacity image models on clean synthetic data may represent an optimistic upper bound that does not transfer to observations degraded by atmospheric seeing, sensor noise, and tracking errors [CITATION: observation degradation effects].

To address these gaps, we develop a unified BRDF-driven simulation framework that generates physically consistent OCS signatures and photometric images from the same satellite STL geometry, nonuniform GGX/Cook-Torrance material assignment, and ray-traced self-occlusion model. Using this framework, we construct a controlled yaw-pitch attitude inversion benchmark and systematically compare OCS-only (MLP), image-only (ResNet-18), late fusion, and feature fusion approaches. Our experiments reveal that observation quality fundamentally determines the relative value of each modality: a ResNet-18 achieves 1.69 ± 0.07° mean error under clean rendered images—an idealized upper bound—but collapses to 85.85° under 1% additive Gaussian noise; OCS-only inversion maintains 5.91° regardless of image quality because it does not depend on image inputs; and OCS-image fusion provides conditional benefits, reducing worst-case errors from 9.9° to 6.6° under clean conditions while the fusion compensation gain increases monotonically as OCS quality degrades.

The contributions of this work are: (1) a unified physical forward model ensuring BRDF-consistent OCS and image generation; (2) a controlled multi-modal attitude inversion benchmark with systematic comparison under consistent protocols; (3) quantification of the clean-image upper bound for image-based inversion and its fragility under controlled degradation; and (4) evidence that OCS provides robust photometric constraints and that fusion value depends on observation quality. This study is conducted entirely within a controlled simulation environment without real optical telescope validation, and the benchmark is limited to yaw-pitch estimation under fixed roll. These boundaries provide a controlled and interpretable evaluation framework while motivating future validation under realistic atmospheric and sensor conditions.

---

## 2. Related Work

### 2.1 Optical Signatures and BRDF Modeling of Space Objects

The optical signatures of space objects arise from the interaction of solar illumination with surface geometry and material reflectance properties. Yang et al. [Yang et al., 2024] investigated the goniopolarimetric properties of satellite surface materials and demonstrated that microfacet BRDF models such as Cook-Torrance provide physically grounded descriptions of metallic and dielectric spacecraft surfaces [to verify: specific model details]. Lu [Lu, 2024] developed BRDF-based photometric models for LEO constellation satellites, showing that realistic brightness predictions require careful treatment of material heterogeneity and observation geometry [to verify: BRDF model type]. Fankhauser et al. [Fankhauser et al., 2023] characterized satellite optical brightness under varying phase angles and highlighted the complexity introduced by earthshine, atmospheric extinction, and sensor response in real photometric observations.

These studies establish the physical foundations for satellite optical signature modeling but primarily focus on photometric prediction or material characterization rather than closing the loop to a controlled attitude inversion benchmark where OCS and resolved images are jointly generated and compared. The present work adopts a GGX/Cook-Torrance BRDF with nonuniform material assignment and uses this shared physical model as the basis for both facet-level OCS integration and pixel-level photometric image rendering.

### 2.2 Light-Curve and OCS-Based Attitude Inversion

Scalar photometric signatures encode attitude-dependent information through the integrated BRDF response over all visible surface elements. Wang et al. [Wang et al., 2024] constructed a laboratory-tested photometry dataset and demonstrated attitude inversion from controlled light-curve measurements [to verify: inversion method]. Burton et al. [Burton et al., 2024] applied particle swarm optimization to estimate satellite attitude from simulated light curves. Kumar et al. [Kumar et al., 2025] proposed a digital twin framework using sequential light-curve comparison for LEO object characterization.

These approaches typically do not compare their results against resolved photometric image-based methods generated under the same physical scattering assumptions. The present work addresses this gap by generating both OCS signatures and photometric images from the same unified forward model and benchmarking OCS-only inversion against image-only and fusion approaches under consistent evaluation.

### 2.3 Photometric Image Simulation and Image-Based Pose Estimation

Resolved photometric images provide spatially distributed brightness information encoding shape, shadow, and component layout cues. Dickinson [Dickinson, 2025] addressed sim-to-real 6DOF satellite pose estimation from ground-based resolved imagery, demonstrating both the potential and challenges of transferring models trained on rendered data to real telescope observations [to verify: architecture and accuracy].

The present work does not claim image-based results as field performance estimates. Instead, clean synthetic image results are explicitly positioned as an idealized upper bound. By generating images under the same BRDF and self-occlusion model used for OCS computation, this work enables direct comparison of the attitude information carried by scalar OCS versus resolved images.

### 2.4 Multi-Modal Fusion and Robustness Under Observation Degradation

Multi-modal fusion aims to combine complementary information sources. Liu et al. [Liu et al., 2024] demonstrated tightly coupled visual-inertial fusion for spacecraft attitude estimation [to verify: degradation robustness addressed?]. However, this addresses visual-inertial fusion rather than OCS-image photometric fusion.

A critical question that remains underexplored is whether fusion benefits are universal or conditional on observation quality. The present work directly addresses this by evaluating OCS-image fusion under both clean and degraded conditions, revealing that complementarity is conditional on observation quality rather than universally guaranteed.

[INSERT Table 1: Related work comparison — see Step 3 output for draft]

---

## 3. Method

### 3.1 Overview

This study establishes a unified forward model where both OCS signatures and photometric images are generated from the same satellite geometry, attitude parameterization, nonuniform material assignment, GGX/Cook-Torrance BRDF, observation geometry, and self-occlusion model. This ensures that any difference in inversion performance reflects intrinsic modality information content rather than modeling inconsistencies. The rendered images define an idealized upper-bound setting; they do not reproduce real telescope observations.

### 3.2 Satellite Geometry and Attitude Parameterization

The satellite model consists of a real STL geometry comprising three components: a metallic main body, a solar panel, and a baffle. Attitude is parameterized using Z-Y-X intrinsic Euler angles: $R = R_z(\psi) \cdot R_y(\theta) \cdot R_x(\phi)$, where $\psi$ is yaw, $\theta$ is pitch, and $\phi$ is roll (fixed at 0°). The primary grid uses 5° spacing: 73 yaw × 37 pitch = 2,701 attitudes. The satellite is rotated while Sun and detector directions remain fixed in the inertial frame [需要作者确认：Euler convention final confirmation].

### 3.3 Observation Geometry and Data Generation Protocol

For OCS computation, five observation geometries spanning phase angles from approximately 24° to 120° are used, covering near-backscatter, side-scatter, and forward-scatter configurations. For the image branch, a single observation geometry (phase angle ≈ 63°) produces one 128 × 128 photometric image per attitude. This asymmetry reflects different information densities: each OCS measurement yields one scalar, whereas each image provides 16,384 pixel values.

### 3.4 Nonuniform Material Assignment and GGX BRDF

Each component is assigned distinct GGX/Cook-Torrance material properties:

$$f_r = (1-m)\frac{\rho_d}{\pi} + \frac{D_{\text{GGX}} \cdot G_{\text{Smith}} \cdot F_{\text{Schlick}}}{4(\mathbf{n}\cdot\mathbf{l})(\mathbf{n}\cdot\mathbf{v})}$$

| Component | Metallic | Roughness | F0 / Base color |
|---|---|---|---|
| Metal body | 1 | 0.20 | F0 = 0.91 |
| Solar panel | 0 | 0.40 | IOR = 1.5 |
| Baffle | 0 | 0.90 | 0.08 |

These are nominal material settings for controlled simulation, not calibrated measurements of the specific target.

### 3.5 Self-Occlusion and Visibility Modeling

For each facet, rays are cast from the offset center ($\mathbf{c}_i + \epsilon \cdot \mathbf{n}_i$, $\epsilon = 1.0$ mm) along Sun and detector directions. Intersections beyond the minimum hit distance ($d_{\min} = 1.0$ mm) indicate occlusion. Only facets with unobstructed lines of sight to both Sun and detector contribute to OCS. These parameters are validated through synthetic geometry tests and sensitivity analysis on the real satellite model.

### 3.6 OCS Integration and Feature Construction

$$\text{OCS} = \sum_{i} A_i \cdot f_r(\mathbf{n}_i, \mathbf{l}, \mathbf{v}) \cdot (\mathbf{n}_i \cdot \mathbf{l}) \cdot (\mathbf{n}_i \cdot \mathbf{v}) \cdot V_i(\mathbf{l}) \cdot V_i(\mathbf{v})$$

OCS features are organized at three levels: **total\_log** (15D, total OCS across 5 geometries), **per\_part\_log** (30D, per-component OCS, the primary practical setting), and **all\_raw** (45D, including occlusion ratios—a semi-oracle upper bound not available from standard observations).

### 3.7 Photometric Image Generation

Images are generated via a geometry-buffer rendering pipeline: per-pixel normals, depth, and component indices are rendered, then exact GGX BRDF is evaluated in post-processing using the same material parameters as OCS computation. Output is a single-channel 128 × 128 grayscale image with log1p intensity transformation. The images are free from atmosphere, sensor noise, PSF, earthshine, and background contamination—they define an idealized upper-bound condition.

### 3.8 Attitude Inversion Models

The inversion models serve as controlled probes of modality information rather than claims of universally optimal architectures.

**OCS-only MLP.** Maps OCS feature vectors to $[\sin\psi, \cos\psi, \sin\theta, \cos\theta]$ via a multi-layer perceptron [需要作者确认：architecture details 128→128→64].

**Image-only CNN/ResNet.** TinyCNN (~106k params) as lightweight baseline; ResNet-18 (~11.2M params) for clean-image upper-bound evaluation. Single-channel 128 × 128 input.

**Late fusion.** Prediction-level combination: $\mathbf{z}_{\text{fused}} = \beta \cdot \mathbf{z}_{\text{OCS}} + (1-\beta) \cdot \mathbf{z}_{\text{image}}$, with $\beta$ swept over [0, 1].

**Feature fusion.** Two-branch architecture (image branch + OCS branch → fusion head), trained end-to-end. Evaluated as a benchmark strategy, not asserted as universally optimal.

### 3.9 Data Splits and Evaluation Metrics

The 2,701 attitudes are split using a 10°→5° protocol: 563 training samples (10° grid) and 1,998 test samples (5° intermediate attitudes), testing interpolation rather than memorization. A random 80/10/10 split is additionally reported. All neural networks use 5 random seeds. Metrics: mean angular error (°), Hit@5°, Hit@10°, P90, and worst-case [需要作者确认：angular error formula].

---

## 4. Results

### 4.1 Forward-Model Validation and OCS Signature Analysis

The unified forward model achieves sub-percent agreement between analytical, facet-level, and pixel-level OCS on canonical geometries (single plate, cube), confirming correct BRDF evaluation, projection, and visibility logic. Self-occlusion validation passes on four synthetic test geometries. The real satellite model exhibits occlusion rates of approximately 60%–78.5% across observation geometries, with the metallic main body dominating OCS contribution due to its strong specular reflection (GGX roughness = 0.20, metallic = 1).

### 4.2 OCS-Only Attitude Inversion

Multi-geometry per-component OCS features (per\_part\_log, 30D) achieve 5.91 ± 0.22° mean error with 73.8% Hit@5°. The semi-oracle all\_raw representation (45D) reaches 3.98 ± 0.60° (90.7% Hit@5°) but includes quantities unavailable from standard observations. The weak total\_log baseline (36.69°) confirms that component-level and multi-geometry information are essential for OCS-based discrimination.

[INSERT Table 2: Main inversion benchmark]

### 4.3 Image-Only Inversion

Under clean synthetic images, TinyCNN achieves 12.38 ± 0.74° (26.1% Hit@5°) as a lightweight baseline. ResNet-18 achieves 1.69 ± 0.07° (97.6% Hit@5°, 99.9% Hit@10°), establishing an idealized upper bound. Data audit confirms no train-test overlap; mean intensity correlation with attitude is negligible (r < 0.02) [需要作者确认：data-audit source]. The clean-image result should not be interpreted as field-performance.

### 4.4 OCS-Image Fusion Under Clean Images

ResNet + concat5 per\_part\_log achieves 1.47 ± 0.07° (99.7% Hit@5°), reducing worst-case from 9.9° to 6.6° (−33%). Mean improvement is modest (0.22°, 13%) but tail improvement is substantial. The semi-oracle all\_raw fusion (1.49°) shows worse worst-case (18.7°), indicating that stronger OCS features do not automatically improve fusion tails.

[INSERT Table 3: ResNet fusion detail]

### 4.5 Robustness Under Controlled Observation Degradation

Controlled image degradation tests reveal severe fragility: 1% Gaussian noise degrades ResNet from 1.69° to 85.85 ± 3.00° (Hit@5° = 2.2%). Brightness scaling is less destructive (×0.50 → 3.45°). OCS-only inversion (5.91°) is unaffected because it does not depend on image inputs.

OCS-noise experiments show fusion compensation gain increasing monotonically: +1.97° at 0% noise → +3.30° at 10% → +6.29° at 20% [需要作者确认：0% OCS-only and fusion exact values]. This demonstrates that multi-modal complementarity is conditional on observation quality.

[INSERT Table 4: Robustness summary]

### 4.6 Ablation and Sensitivity Analysis

Random split yields consistent trends [需要作者确认：exact random split numbers]. BRDF sensitivity: metallic roughness ±20% → 30–42% OCS variation; non-metallic <5% [需要作者确认：final values]. Roll sensitivity: ~20% OCS variation [需要作者确认：exact values]. Self-occlusion rates (60–78.5%) confirm occlusion modeling necessity.

---

## 5. Discussion

### 5.1 Main Finding

The central finding is that OCS and photometric images provide qualitatively different attitude constraints under a unified BRDF-driven forward model, and their relative value depends fundamentally on observation quality. Under idealized clean conditions, a high-capacity image model exploits rich spatial cues to achieve very high accuracy. However, this upper bound is structurally fragile. OCS provides a lower but stable constraint independent of image-pixel quality within this benchmark. Multi-modal complementarity is thus conditional rather than universal.

### 5.2 Why Clean Rendered Images Are Strong

Clean rendered images preserve stable shape, shadow, centroid, and photometric distribution cues that a ResNet-18 can jointly exploit. The data audit confirms the network does not rely on trivial shortcuts. However, the centroid displacement cue (correlated with yaw under fixed camera geometry) may not transfer to real observations where tracking systems control image centering. This result should not be interpreted as field performance because the images exclude atmosphere, PSF, detector effects, and tracking errors.

### 5.3 Why OCS Remains Valuable

OCS does not compete with clean-image models on absolute accuracy. Its value lies in: (1) physical interpretability—each value corresponds to integrated BRDF response; (2) multi-geometry availability at low marginal cost; (3) structural independence from image pixels in this benchmark; (4) accessibility with photometric detection rather than resolved imaging. OCS-like integrated photometric measurements may be less demanding than fully resolved imagery, but practical acquisition requirements depend on telescope aperture, target brightness, and atmospheric conditions.

### 5.4 Conditional Value of Fusion

Fusion improves tail errors under clean conditions (worst-case −33%) and provides increasing compensation as OCS quality degrades (+1.97° → +6.29°). However, the all\_raw fusion worst-case (18.7°) warns that including overly strong features can introduce optimization difficulties. Fusion should be viewed as a conditional reliability mechanism rather than a universal accuracy maximizer.

### 5.5 Implications

These findings suggest: (1) unified forward models enable fair modality comparison; (2) image-based results should report clean vs degraded performance separately; (3) OCS provides an additional constraint when resolved images are unavailable or degraded; (4) tail error and Hit@5° may matter as much as mean error for operational use.

### 5.6 Scope and Limitations

This study is conducted entirely within a controlled simulation environment. No real optical telescope observations with known attitude ground truth are used. The clean-image results represent an idealized upper bound. The benchmark estimates yaw and pitch under fixed roll; roll sensitivity (~20% OCS variation) confirms roll is non-negligible [需要作者确认：exact value]. The main image branch uses phase63; cross-phase generalization is not evaluated. Material parameters are nominal. The controlled degradation tests (Gaussian noise, brightness scaling) do not constitute a comprehensive atmospheric or detector model. OCS independence from image-pixel degradation is structural within the simulation; real OCS measurements would be affected by photometric calibration uncertainty and atmospheric extinction.

---

## 6. Conclusion

This study develops a unified BRDF-driven simulation framework generating physically consistent OCS signatures and photometric images from the same satellite geometry, nonuniform GGX/Cook-Torrance material model, and ray-traced self-occlusion. A controlled yaw-pitch attitude inversion benchmark systematically compares OCS-only, image-only, and fusion approaches under ideal and degraded conditions.

Key findings: (1) ResNet-18 achieves 1.69° mean error under clean images—an idealized upper bound; (2) 1% additive noise degrades this to 85.85°; (3) OCS-based inversion provides a stable 5.91° constraint independent of image quality; (4) fusion reduces worst-case errors from 9.9° to 6.6° under clean conditions, with compensation gain increasing from +2.0° to +6.3° as OCS degrades.

Multi-modal complementarity is conditional on observation quality rather than universally guaranteed. The study is simulation-focused without real telescope validation. Future work will pursue ground-based telescope validation, three-degree-of-freedom attitude estimation, cross-phase image generalization, and comprehensive observation degradation modeling.

---

**Data Availability:** [PLACEHOLDER: to be completed per journal requirements]

**Author Contributions:** [PLACEHOLDER]

**Conflict of Interest:** The authors declare no conflict of interest.

**References:** [PLACEHOLDER — all citations marked in text]

---

## B. Cross-Section Consistency Checklist

| # | Check | Status |
|---|---|---|
| 1 | Title / Abstract / Contributions aligned? | ✅ All reference "unified BRDF-driven framework", "controlled benchmark", "conditional complementarity" |
| 2 | OCS / photometric images / fusion terminology consistent? | ✅ "OCS" throughout (not "light curve" in main text); "photometric images" (not "rendered images" alone) |
| 3 | all\_raw labeled semi-oracle everywhere? | ✅ §3.6, §4.2, §4.4, §5.4 |
| 4 | per\_part\_log labeled practical OCS setting? | ✅ §3.6, §4.2, §4.4 |
| 5 | Clean image = upper-bound throughout? | ✅ Abstract, §1, §3.7, §4.3, §5.2, §5.6, §6 |
| 6 | No real telescope validation stated clearly? | ✅ Abstract, §1 (last para), §3.1, §5.6, §6 |
| 7 | Fixed roll / phase63 / nominal materials consistent? | ✅ §3.2, §3.3, §3.4, §5.6 |
| 8 | r = 0.003 limited to TinyCNN/OCS diagnostic? | ✅ Only in §4.4 as "earlier diagnostic"; not in Abstract/Conclusion |
| 9 | Gaussian noise = controlled stress test? | ✅ §4.5, §5.6 — never "realistic degradation model" |
| 10 | Number conflicts? | ✅ No conflicts found; same values used consistently |

---

## C. Author Confirmation List (Priority Order)

| Priority | Item | Impact |
|---|---|---|
| 1 | **Target journal** (Acta Astronautica vs ASR) | Affects title length, format, word limits |
| 2 | **Angular error formula** | Must be stated precisely in §3.9 |
| 3 | **0% OCS-noise table values** (OCS-only ~5.91, fusion ~3.93?) | Needed for Table 4 completeness |
| 4 | **Citation metadata** — verify all [to verify] items in Table 1 and Related Work | Required before submission |
| 5 | **Data-audit correlation values** (r < 0.02, r ≈ 0.66) — confirm source | Needed for §4.3 |
| 6 | **MLP architecture** (128→128→64 SiLU LN?) | Needed for §3.8.1 |
| 7 | **Euler convention** final confirmation | Needed for §3.2 |
| 8 | **BRDF/roll/occlusion sensitivity exact values** for Table 4 | Needed for §4.6 |
| 9 | **Random split exact numbers** (fusion 2.13°?) and which model | Needed for §4.6 |
| 10 | **ResNet-fusion under image degradation** — exists or Future Work? | Affects §4.5 and §5.4 |
| 11 | **Limitations placement** — §5.6 or separate section? | Journal-dependent |
| 12 | **TinyCNN feature fusion (4.10°)** — main text ablation or supplement? | Affects §4.4 length |
| 13 | **Cross-phase test** — supplement or Future Work only? | Affects §5.6 |

---

## D. Revision Priority List

### Must fix before internal review

1. Fill all `[需要作者确认：...]` items with confirmed values or remove.
2. Verify and complete all `[to verify]` citation details in §2 and Table 1.
3. Confirm angular error formula and write it explicitly in §3.9.
4. Confirm 0% OCS-noise values and complete Table 4.
5. Decide TinyCNN fusion placement (main text vs supplement).

### Should fix before journal submission

6. Compress Introduction to ≤800 words if journal requires.
7. Add figure/table captions once figures are produced.
8. Ensure total word count fits target journal limits (~6000–8000 for Acta Astronautica).
9. Replace all `[CITATION: ...]` with proper references.
10. Add Data Availability and Author Contributions per journal template.
11. Run language polish pass for conciseness.

### Optional strengthening

12. Add ResNet-fusion image-degradation experiment if available.
13. Add cross-phase sanity test if time permits.
14. Measure ResNet+OCS error correlation to update r = 0.003 diagnostic.
15. Add supplementary material with full 5-seed tables and training curves.

---

## E. Self-review Checklist

| # | Question | Answer |
|---|---|---|
| 1 | Did I invent experiments or numbers? | ✅ No — all from provided data; uncertain items marked |
| 2 | Did I invent citations? | ✅ No — all [CITATION] or [to verify] |
| 3 | Did I write clean image as field performance? | ✅ No — "idealized upper bound" throughout |
| 4 | Did I overstate fusion? | ✅ No — "conditional", "tail improvement", "not universally best" |
| 5 | Did I overstate OCS? | ✅ No — "does not compete on absolute accuracy"; "within this benchmark" |
| 6 | Did I weaken or omit no-real-validation? | ✅ No — stated in Abstract, §1, §3.1, §5.6, §6 |
| 7 | Did I mix reviewer-defense into formal text? | ✅ No — defense points kept in Step 6 output only |
| 8 | Did I preserve all pending items? | ✅ Yes — 13 items in Author Confirmation List |

---

*Step 7 全文整合初稿完成。全部写作阶段产出结束。等待作者确认待核对项后进入最终定稿。*
