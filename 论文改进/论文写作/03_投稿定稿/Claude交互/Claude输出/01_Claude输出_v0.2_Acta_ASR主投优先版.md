# Claude Candidate v0.2 Acta/ASR Manuscript

Status: candidate draft for the first-tier Acta Astronautica / Advances in Space Research priority submission. This is not the final master manuscript. It must be reviewed and integrated by Codex before entering `03_投稿定稿/manuscript_md/主稿_v0.2_Acta_ASR主投优先版.md`. v0.1 is not overwritten. All `[CITATION: ...]`, `[to verify]`, and `[需要作者确认：...]` placeholders are retained for author resolution. CJA/AST and TAES/JGCD versions are intentionally not produced.

Source strategy: build on v0.1 (GPT structural base with Claude title/abstract/compact wording), retain Sections 1-3 and 4.1-4.3 largely as in v0.1, and rewrite the Results fusion/robustness block plus the Discussion and Limitations to integrate experiments 12 (07), 12b (07b), and 12c-12g (07c) in a single pass.

---

## A. Candidate Manuscript Draft

# BRDF-Driven Optical Cross Section and Photometric Image Simulation for Space Object Attitude Inversion: A Controlled Benchmark Study

## Abstract

Accurate attitude estimation of non-cooperative space objects from optical observations remains difficult because scalar photometric signatures and resolved photometric images encode different, observation-dependent attitude cues. Existing studies often treat light-curve-like signatures, image-based pose estimation, and multi-modal fusion under different forward-model assumptions, making it unclear when these modalities are complementary rather than redundant, and how fusion behaves when image quality degrades. Here we develop a unified BRDF-driven simulation framework that generates optical cross section (OCS) signatures and clean photometric images from the same satellite STL geometry, nonuniform material assignment, GGX/Cook-Torrance reflectance model, yaw-pitch attitude definition, observation geometry, and self-occlusion treatment. This physically consistent setting enables a controlled benchmark across OCS-only, image-only, late-fusion, and feature-fusion attitude inversion models, evaluated under both ideal and degraded image conditions. Under clean rendered images, a ResNet-18 image-only model reaches 1.69 +/- 0.07 deg mean angular error with Hit@5 = 97.6%, defining an idealized upper-bound condition rather than field performance. The same model is fragile under controlled degradation: 1% Gaussian image noise raises the mean error above 85 deg. Component-level OCS features provide a lower-dimensional, interpretable photometric constraint that is independent of image-pixel degradation in this benchmark. We further show that fusion behavior is architecture- and training-dependent: a clean-trained naive feature-fusion model is image-dominant and is contaminated by image noise (mean error about 73 deg under sigma = 0.01), and it does not automatically fall back to OCS. Degradation-aware fusion training (U1) restores stable mean, P90, and Hit@5 across the tested and several held-out synthetic degradations (for example 2.31 deg under sigma = 0.10), and branch-masking, OCS-noise, and image-only-augmentation controls indicate that the mechanism is coupled OCS-image co-utilization rather than a standalone OCS fallback. Synthetic observation-style degradation, cross-phase rendering, centroid-control, and explicit late-fusion weighting stress tests bound these claims: severe combined degradation and a phase-120 cross-geometry case remain failure modes, rare large outliers persist near polar attitudes, and oracle inference-time weighting is an upper bound, not a deployable automatic gate. These results support conditional, design-dependent complementarity between OCS and photometric images, not universal fusion superiority or guaranteed robustness. Real optical telescope validation, calibrated material measurements, and explicit atmosphere/sensor modeling remain necessary before operational field-performance claims can be made.

## Keywords

Space object attitude inversion; optical cross section; BRDF; photometric image simulation; multi-modal fusion; degradation-aware fusion; controlled benchmark

## 1. Introduction

Optical observations provide a practical route for inferring the attitude and scattering behavior of non-cooperative space objects when cooperative telemetry is unavailable. The measured optical response depends jointly on target geometry, surface reflectance, illumination direction, viewing direction, phase angle, and self-occlusion. Space object attitude inversion is therefore not only a regression problem, but also a forward-modeling problem: the physical origin of the observation determines what attitude information is available and how robustly it can be interpreted [CITATION: optical space object characterization]. This study focuses on controlled yaw-pitch attitude inversion from two optical modalities: scalar optical cross section (OCS) signatures and resolved photometric images.

OCS signatures and photometric images access attitude information through different mechanisms. OCS or light-curve-like measurements summarize the integrated reflected response under a given sun-sensor geometry, making them compact, interpretable, and naturally extensible across multiple observation geometries [CITATION: optical light-curve attitude inversion]. Photometric images preserve spatially distributed cues such as projected outline, component layout, shadow structure, centroid displacement, brightness distribution, and specular highlights [CITATION: image-based spacecraft pose estimation]. Clean rendered images can therefore be highly informative for attitude inversion, but their usefulness depends strongly on image quality and on consistency between the training and test distributions.

The central unresolved question is when OCS and photometric images are complementary, and how their fusion behaves when one modality degrades. This question cannot be answered cleanly if the two modalities are generated under inconsistent assumptions about geometry, material reflectance, BRDF, attitude parameterization, or visibility [CITATION: BRDF-based space object photometry]. It also cannot be answered by treating clean synthetic image performance as expected field performance. Real ground-based optical observations are affected by atmospheric seeing, tracking error, sensor noise, optical blur, limited resolution, background contamination, phase-angle variation, and calibration uncertainty [CITATION: ground-based optical observation degradation]. A useful benchmark should therefore generate both modalities from the same physical model and evaluate them under both ideal and degraded conditions, while explicitly testing whether fusion adds robustness rather than assuming it.

Here we present a unified BRDF-driven OCS-image simulation and controlled inversion benchmark for space object attitude estimation. The forward model uses a real satellite STL geometry with nonuniform component-level material assignment, a GGX/Cook-Torrance BRDF, analytical ray-based self-occlusion, and shared yaw-pitch attitude and observation-geometry definitions. From this common model, we generate OCS signatures and clean photometric images, then evaluate OCS-only, image-only, late-fusion, and feature-fusion models under both clean and degraded image conditions. The benchmark reveals four linked behaviors: clean rendered images provide a strong image-based upper-bound case; image-only performance collapses under controlled pixel-level degradation; a clean-trained naive feature-fusion model inherits this fragility and is image-dominant rather than OCS-protected; and degradation-aware fusion training restores stable average and tail behavior across the tested and several held-out synthetic degradations through coupled OCS-image co-utilization, subject to clearly bounded failure modes.

This paper makes five contributions. First, it introduces a physically consistent forward simulation framework linking OCS and photometric images through the same geometry, material assignment, GGX reflectance model, attitude definition, observation geometry, and self-occlusion treatment. Second, it establishes a controlled yaw-pitch inversion benchmark comparing OCS-only, image-only, late-fusion, and feature-fusion models under shared data-generation assumptions. Third, it separates clean-image upper-bound performance from degraded-observation robustness, showing that strong CNN performance under ideal synthetic images should not be read as a field-performance guarantee. Fourth, it diagnoses the fusion mechanism directly: naive clean-trained feature fusion is image-dominant and is contaminated, not protected, under image degradation, whereas degradation-aware training restores robustness through OCS-image co-utilization rather than an automatic OCS fallback. Fifth, it bounds these claims with synthetic observation-style degradation, cross-phase, centroid-control, and explicit-weighting stress tests that identify remaining failure modes. The present study does not use real optical telescope images with known attitude ground truth and does not explicitly model atmosphere, detector response, PSF, earthshine, or background contamination. These boundaries define the scope of the current controlled study and the requirements for future validation.

## 2. Related Work

### 2.1 Optical signatures and BRDF modeling of space objects

Optical signatures of space objects are governed by the coupled effects of target geometry, surface material, illumination direction, viewing direction, phase angle, and visibility. BRDF-based modeling is therefore central to physically meaningful satellite photometry because it connects surface reflectance behavior with observed brightness and image intensity under changing geometries. Studies of satellite material reflectance and goniopolarimetric behavior provide experimental and semi-empirical support for using microfacet and Cook-Torrance-type descriptions to represent spacecraft surface scattering [Yang et al., 2024/2025, to verify]. Large-scale satellite brightness studies further show that BRDF-based photometric models can explain and predict the brightness behavior of LEO constellation satellites using real observation campaigns [Lu/Yao, 2024, to verify]. Radiometric analyses also emphasize that observed satellite brightness can depend on effects beyond direct sunlight, including Earth-reflected illumination and observation-dependent contributions [Fankhauser et al., 2023, to verify].

The present study follows this physical-modeling tradition but uses it for a different purpose: not only to predict scalar brightness, but to generate paired OCS signatures and photometric images from one shared forward model. This shared model is essential for judging whether differences in inversion accuracy reflect modality information rather than inconsistent simulation assumptions.

### 2.2 Light-curve and OCS-based attitude inversion

Light curves and OCS-like scalar photometric signatures are attractive for attitude inference because they are compact, interpretable, and obtainable across multiple observation geometries. Laboratory-tested photometry datasets and simulated photometric signatures have been used to investigate attitude inversion from scalar brightness measurements [Wang et al., 2024, to verify]. Optimization-based approaches, including particle swarm strategies, further demonstrate that light-curve attitude estimation can be formulated as a search problem over attitude states when object shape, reflectance, and illumination geometry are known or assumed [Burton et al., 2024, to verify]. Recent digital-twin and sequential-comparison strategies for LEO uncontrolled objects also support the broader use of light curves for object understanding and attitude-related inference [Kumar et al., 2025, to verify].

These studies motivate the use of scalar photometric constraints, but they do not by themselves determine how OCS compares with resolved photometric images under the same physical assumptions. In the present work, OCS is not treated as the automatic accuracy upper bound. Its value is instead tested as a low-dimensional, multi-geometry, physically interpretable constraint within a shared OCS-image benchmark.

### 2.3 Photometric image simulation and image-based pose estimation

Resolved and rendered images provide spatial cues that scalar signatures cannot preserve, including projected shape, component layout, shadow structure, brightness distribution, and specular patterns. Image-based satellite pose estimation studies increasingly use synthetic imagery and deep learning to estimate spacecraft pose from resolved ground-based or simulated imagery. Dickinson's 2025 dissertation, for example, addresses 6DOF satellite pose estimation from resolved ground-based imagery using synthetic training and image-quality analysis [Dickinson, 2025, to verify]. Such work highlights both the power of resolved imagery and the difficulty of sim-to-real transfer under blur, noise, illumination variation, and limited image quality.

For the present paper, image-based pose estimation provides an important contrast to scalar OCS inversion. Clean synthetic photometric images may contain strong attitude cues, and a high-capacity image model can exploit these cues effectively. However, clean-image accuracy is not a direct estimate of field performance. The present work therefore treats clean rendered images as a controlled upper-bound setting and explicitly evaluates controlled degradation sensitivity.

### 2.4 Multi-modal fusion and robustness under observation degradation

Multi-modal fusion is often motivated by the possibility that different measurements fail under different conditions. In spacecraft attitude estimation, tightly coupled visual-inertial methods illustrate how feature-level fusion can use different information streams to improve robustness compared with more loosely coupled designs [Liu et al., 2024, to verify]. This literature supports the general idea that fusion should be evaluated not only by mean accuracy but also by robustness, failure modes, and the information carried by each modality.

The fusion problem studied here is different from visual-inertial fusion because both modalities are optical: one is an integrated scalar photometric response and the other is a resolved photometric image generated from the same BRDF-driven scene. This setting allows us to ask a narrower question: when OCS and photometric images are physically consistent, does fusion add meaningful information and robustness, or does it merely duplicate what a strong image model already captures and inherit its failure modes? Our diagnostic experiments show that the answer depends on fusion architecture and training, which motivates an explicit mechanistic analysis rather than a single fusion accuracy number.

**Table 1. Related work positioning and scope comparison.**

| Study | Target / data | BRDF or reflectance model | Self-occlusion / visibility | Image branch | Scalar photometric branch | Attitude inversion | Fusion | Validation type |
|---|---|---|---|---|---|---|---|---|
| Yang et al. 2024/2025 Photonics `[to verify]` | Material samples / satellite material surfaces `[to verify]` | Semi-empirical pBRDF / Cook-Torrance-related models `[to verify]` | Not central `[to verify]` | No resolved attitude image branch | Reflectance characterization, not OCS inversion | No attitude inversion benchmark | No | Laboratory/material measurement `[to verify]` |
| Lu/Yao 2024 Universe `[to verify]` | LEO constellation satellite / Starlink model | BRDF-based photometric model | Observation geometry considered; detailed self-occlusion `[to verify]` | No resolved inversion image branch | Massive photometric observations / brightness modeling | Not primarily attitude inversion | No | Real photometric observations |
| Wang et al. 2024 ASR `[to verify]` | Space debris / lab photometry target `[to verify]` | Reflectance assumptions `[to verify]` | `[to verify]` | No resolved image branch | Laboratory-tested photometry dataset | Yes, photometry-based attitude inversion | No | Laboratory photometry dataset |
| Burton et al. 2024 ASR `[to verify]` | Known object model / space debris or satellite `[to verify]` | Reflective properties assumed | `[to verify]` | No | Light curve | Yes, particle-swarm attitude estimation | No | Simulation / light-curve experiments `[to verify]` |
| Dickinson 2025 RIT PhD `[to verify]` | CAD/satellite models; resolved ground-based imagery | Image simulation `[to verify]` | Included through rendering/simulation `[to verify]` | Yes, resolved imagery | No OCS/light-curve branch | Yes, 6DOF image-based pose estimation | No OCS-image fusion | Synthetic training and resolved imagery evaluation `[to verify]` |
| Kumar et al. 2025 Acta Astronautica `[to verify]` | Digital twin / LEO uncontrolled objects `[to verify]` | Light-curve modeling assumptions `[to verify]` | `[to verify]` | No resolved image branch | Light curves / sequential comparison | Attitude/object understanding `[to verify]` | No | Observation/digital-twin comparison `[to verify]` |
| Liu et al. 2024 Remote Sensing `[to verify]` | Spacecraft attitude estimation setting | Not BRDF-based | Not relevant | Visual/star-sensor features `[to verify]` | No OCS/light curve | Yes, spacecraft attitude estimation | Visual-inertial tightly coupled fusion | Simulation and experimental evaluations `[to verify]` |
| Fankhauser et al. 2023 AJ `[to verify]` | Satellite brightness geometry | Radiometric brightness model; sunlight and earthshine `[to verify]` | Not attitude-inversion focus | No resolved inversion image branch | Brightness modeling | No attitude inversion benchmark | No | Radiometric/astronomical analysis |
| Present work | Real satellite STL; controlled yaw-pitch grid | GGX/Cook-Torrance with nonuniform component assignment | Analytical ray-based self-occlusion | Clean rendered photometric images + controlled/synthetic degradation | Multi-geometry OCS signatures | Yes, controlled yaw-pitch inversion | OCS-image late and feature fusion; degradation-aware fusion diagnosis | Simulation benchmark; no real telescope validation |

## 3. Method

### 3.1 Overview of the unified OCS-image simulation framework

We formulate the study as a physically consistent simulation and controlled inversion benchmark for space object attitude estimation. The objective is to estimate yaw and pitch from two optical modalities: scalar OCS signatures and resolved photometric images. Both modalities are generated from the same object geometry, attitude definition, material assignment, BRDF model, illumination direction, viewing direction, and self-occlusion assumptions. This design allows inversion experiments to compare modality information under controlled conditions rather than under mismatched forward models.

The pipeline consists of four stages. First, a real satellite STL model is converted into a facet-level representation with component labels and nonuniform material parameters. Second, each yaw-pitch attitude and observation geometry defines the orientation of the object relative to the illumination and detector directions. Third, a GGX/Cook-Torrance BRDF and an analytical visibility model are used to generate multi-geometry OCS signatures and clean rendered photometric images. Fourth, OCS-only, image-only, late-fusion, and feature-fusion models are trained and evaluated as controlled probes of the information carried by each modality, including dedicated diagnostic and degradation-aware training variants. The benchmark is simulation-focused: real optical telescope images are not used, and atmosphere, detector response, optical PSF, earthshine, and background contamination are not explicitly modeled.

**Fig. 1 caption intent.** Unified OCS-image simulation and inversion pipeline. The figure should show the path from real STL geometry, component segmentation, nonuniform material assignment, yaw-pitch attitude grid, observation geometry, GGX/Cook-Torrance BRDF, and self-occlusion to paired OCS signatures and clean photometric images, followed by OCS-only, image-only, late-fusion, and feature-fusion inversion models, and the degradation-aware fusion and stress-test branches.

### 3.2 Satellite geometry and attitude parameterization

The geometric input is a real satellite STL model consisting of three component groups: a metal body, a solar panel, and a baffle or shade component. The model is represented as triangular facets, each with an area, a surface normal, a component label, and a material assignment. This facet-level representation is required for OCS integration because scalar OCS is computed as a surface integral over illuminated and visible facets.

The attitude state in the present benchmark is parameterized by yaw and pitch, while roll is fixed. The main attitude grid uses a 5 deg resolution with 73 yaw samples and 37 pitch samples, giving 2701 yaw-pitch attitudes. A coarser 10 deg grid is used for training in the interpolation split, while the remaining 5 deg intermediate attitudes are used for testing. This split is designed to evaluate interpolation over attitude space rather than direct memorization of all 5 deg grid points. The exact Euler order and rotation-matrix convention should be reported in the final manuscript as `[需要作者确认：Euler order / rotation matrix convention]`.

The present setting should be interpreted as a controlled yaw-pitch benchmark, not a full three-degree-of-freedom pose-estimation system. This limitation is intentional: the goal is to isolate the information provided by OCS signatures, photometric images, and their fusion under a defined attitude parameterization.

### 3.3 Observation geometry and data generation protocol

For OCS generation, five sun-sensor geometries are used for each attitude, producing 5 x 2701 = 13,505 attitude-geometry samples. The phase-angle range is approximately 24 deg to 120 deg. These multiple geometries allow the OCS branch to sample attitude-dependent photometric behavior beyond a single scalar response.

For image generation, the main branch uses clean rendered photometric images at 128 x 128 resolution under the phase condition referred to in the project notes as phase63. This design provides a controlled image benchmark aligned with the forward model, but it does not test all possible phase-angle generalization cases. To bound cross-phase behavior, we additionally render two off-nominal phase conditions, phase24 and phase120, as full-grid sanity tests; these are used only to characterize cross-geometry generalization limits, not as additional training distributions `[需要作者确认：phase63 fairness and cross-phase values]`.

**Fig. 2 caption intent.** Satellite geometry and observation setup. The figure should show the three component groups, material labels, yaw-pitch coordinate definition, fixed roll boundary, five sun-sensor geometries, and the approximate phase-angle range.

### 3.4 Nonuniform material assignment and GGX BRDF

Nonuniform material assignment is used to reflect the fact that different satellite components have different optical scattering behavior. The three component groups are assigned nominal material parameters for the metal body, solar panel, and baffle/shade. The main paper model uses a GGX/Cook-Torrance BRDF, while LegacyPhong is retained only as a historical or compatibility baseline and is not treated as the primary physical model.

For the controlled simulation, the nominal GGX material settings are as follows: the metal body uses `metallic = 1`, `roughness = 0.20`, and `F0 = 0.91`; the solar panel uses `metallic = 0`, `roughness = 0.40`, and `ior = 1.5`; and the baffle/shade uses `metallic = 0`, `roughness = 0.90`, and `base_color = 0.08`. These parameters are physically motivated nominal settings for controlled simulation, not calibrated measurements of the specific target. Their effect should therefore be interpreted together with sensitivity analysis.

Let `f_r(n_i, l, v)` denote the BRDF value of facet `i`, where `n_i` is the facet normal, `l` is the illumination direction, and `v` is the viewing direction. The same BRDF evaluation is used by the OCS integration and by the photometric-image generation pipeline, so that both modalities are tied to the same material and reflectance assumptions.

### 3.5 Self-occlusion and visibility modeling

Self-occlusion is modeled at the facet level for OCS integration. For each facet, two visibility queries are evaluated: one along the illumination direction and one along the detector direction. A facet contributes to OCS only when it is both illuminated by the light source and visible to the detector. This design separates local cosine visibility, determined by `max(n_i . l, 0)` and `max(n_i . v, 0)`, from geometric occlusion caused by other parts of the satellite.

The visibility query is implemented using analytical ray tracing over the triangulated geometry. To suppress self-intersection and near-distance mesh artifacts, the ray origin is displaced from the facet surface by an epsilon offset, and intersections closer than a minimum hit distance are filtered. The current validated setting uses `epsilon = 1.0 mm` and `min_hit_distance = 1.0 mm`. These values are chosen from synthetic-geometry validation and sensitivity scans on the real three-component model. Single-plate tests verify that self-intersection is suppressed; double-plate, U-block, and nested-cylinder tests verify cross-part and internal occlusion behavior; and Blender-based manual ray-cast review confirms agreement for sampled cases.

This visibility model is designed for deterministic facet-level OCS computation. It is not a replacement for real optical validation and does not imply that all field imaging effects are modeled. Rather, it provides a controlled and reproducible self-occlusion treatment for comparing OCS and image-derived attitude information.

### 3.6 OCS integration and feature construction

For a given attitude and observation geometry, OCS is computed as a BRDF-weighted surface integral over visible and illuminated facets:

```text
OCS = sum_i A_i f_r(n_i, l, v) max(n_i . l, 0) max(n_i . v, 0) V_i(l) V_i(v),
```

where `A_i` is the area of facet `i`, `f_r` is the GGX/Cook-Torrance BRDF value, `n_i` is the facet normal, `l` and `v` are unit illumination and viewing directions, and `V_i(l)` and `V_i(v)` are binary visibility terms for the illumination and viewing directions. The product of cosine terms enforces local front-facing illumination and observation, while the binary visibility terms account for self-occlusion.

Several OCS feature representations are constructed from this integration. Total OCS features summarize the scalar response for each observation geometry. Per-part OCS features retain component-level contributions from the metal body, solar panel, and baffle/shade. Log-transformed versions are used to reduce dynamic-range imbalance across observation geometries and components. Diagnostic feature variants, such as `all_raw`, may include additional quantities and are therefore treated as semi-oracle upper-bound representations rather than operationally realistic OCS features. In contrast, `per_part_log` is treated as a practical OCS setting for the controlled benchmark. Unless otherwise stated, the fusion experiments use the `concat5 per_part_log` 30-dimensional representation, in which per-part log OCS features from the five observation geometries are concatenated. OCS feature standardization uses training-set statistics only, so that no test-set information leaks into normalization.

### 3.7 Photometric image generation

Photometric images are generated from the same geometry, attitude, material assignment, BRDF model, and observation settings used by the OCS pipeline. The main image branch uses clean rendered photometric images at 128 x 128 resolution, stored with a log1p intensity transform. These images provide spatial cues such as silhouette, component layout, shadowing, and brightness distribution, which are not preserved by scalar OCS signatures.

The rendered images are not intended to reproduce field telescope images. Instead, they define an idealized and controlled image-based upper-bound setting. Atmosphere, detector response, optical PSF, earthshine, background contamination, and other real-observation effects are not explicitly modeled. The main image branch uses one rendered photometric phase condition, phase63. Broader cross-phase image generalization is outside the primary scope of the present benchmark and is examined only as a bounded sanity test (Section 4.7).

### 3.8 Attitude inversion models

The inversion models are used to probe modality information under controlled conditions. Each model predicts yaw-pitch attitude from either OCS features, photometric images, or both. To handle angular periodicity, the target is encoded using a periodic sine-cosine representation for yaw and pitch `[需要作者确认：exact target encoding]`.

The OCS-only model maps OCS feature vectors to yaw-pitch attitude predictions using a multilayer perceptron. This model tests how much attitude information is carried by low-dimensional scalar photometric signatures. The `all_raw` 45-dimensional representation is treated as a semi-oracle upper bound because it includes additional diagnostic quantities; it should not be interpreted as a fully realistic field-observation feature. The `per_part_log` representation is used as a more practical OCS feature setting.

The image-only models map a single-channel 128 x 128 photometric image to a yaw-pitch attitude prediction. A TinyCNN is used as a lightweight image baseline, while ResNet-18 is used as a stronger image model for clean synthetic upper-bound evaluation. TinyCNN should not be used to characterize the upper limit of image-based inversion because stronger image models can exploit clean rendered image cues more effectively. Conversely, ResNet-18 performance on clean rendered images should be interpreted as an idealized upper bound, not as a real telescope performance estimate.

Late fusion combines independently produced OCS and image predictions at the prediction level. Fusion is performed in a periodic yaw-pitch representation, and a weighting parameter beta defines the relative image weight, where beta = 1 corresponds to image-only and beta = 0 corresponds to OCS-only; a beta sweep explores the tradeoff between prediction sources. Feature fusion uses a two-branch architecture consisting of an image branch, an OCS branch, and a fusion head. The image branch extracts features from the rendered photometric image, while the OCS branch embeds the OCS feature vector. The concatenated feature representation is then mapped to the yaw-pitch target representation. Both late fusion and feature fusion are benchmark strategies for evaluating conditional complementarity, not claims that a single fusion design is universally best.

### 3.9 Fusion-mechanism diagnostics and degradation-aware training

To diagnose how feature fusion uses each modality, and whether fusion provides robustness under image degradation, we add four controlled training and probing variants on top of the baseline `concat5 per_part_log` feature-fusion model.

First, a clean-trained naive feature-fusion model is evaluated under clean images and under additive Gaussian image noise (sigma = 0.01 and sigma = 0.10) and brightness scaling (x0.50, x1.50). For this model we apply branch masking at evaluation time: the image branch input or the OCS branch input is replaced by a fixed value (zero or the training-set mean), isolating how much each branch contributes to the fused prediction. Branch masking is a feature-level diagnostic and does not represent a deployable single-modality predictor.

Second, a degradation-aware fusion model (denoted U1) is trained with online image-degradation augmentation, exposing the fusion model to image noise and brightness perturbations during training. U1 is evaluated under the same clean and degraded conditions, and additionally under held-out synthetic degradations not used in training (Gaussian noise sigma = 0.03 and 0.05, Gaussian blur with kernel size 3 and 5, and downsampling to 64 and 32 pixels), under OCS feature noise (0% to 20%), and under the same branch-masking probe.

Third, to isolate whether the recovered robustness is simply an image-augmentation effect, an image-only model is trained with the same online image-degradation augmentation and compared with U1 under identical conditions.

Fourth, as alternative upgrade strategies we evaluate modality dropout alone (U2), combined augmentation plus dropout (U3), and an OCS-anchored gating variant (U4). These are reported as comparative or supplementary mechanisms rather than the primary method.

All degradation operators in Sections 3.9 and 4.7 are applied in the linear intensity domain. For the log1p-stored images, degradation follows an `expm1 -> degradation -> log1p` sequence so that noise, background, and scaling act on physically meaningful intensities rather than on log-compressed values.

### 3.10 Synthetic observation-style degradation and stress tests

To bound robustness claims, we further define a set of synthetic observation-style stress tests. These are observation-chain-inspired and do not constitute real telescope validation. They include: additive read-out noise; additive background offset; a synthetic starfield contamination; and combined-degradation settings at medium and severe levels. We also evaluate a centroid-control experiment, in which the target is recentered so that the centroid-displacement cue available under fixed framing is removed; the centroid is computed in the linear intensity domain. Finally, we evaluate an explicit late-fusion beta sweep under image degradation, reporting the oracle (inference-time best) beta as an upper bound, and an outlier audit over all test evaluations.

### 3.11 Data splits and evaluation metrics

The evaluation uses a 10 deg -> 5 deg attitude split. Attitudes on the coarser 10 deg grid form the training pool, while the remaining attitudes on the 5 deg grid form the test set. This split is stricter than a simple random split because the model must infer intermediate attitude states that were not directly included in the training grid. Neural models are evaluated across multiple random seeds where applicable (the fusion-mechanism experiments use five seeds, 0-4).

Performance is measured using great-circle angular error in degrees, reported as mean angular error, standard deviation across seeds where applicable, median, Hit@5, Hit@10, P90, and worst-case error. The angular-error computation accounts for yaw periodicity and pitch geometry; the final paper should report the exact formula as `[需要作者确认：angular error formula]`. These metrics are used to compare OCS-only, image-only, and fusion models in terms of average accuracy, threshold success rate, and tail behavior.

## 4. Results

### 4.1 Forward-model validation and OCS signature analysis

The unified forward model provides a physically consistent basis for comparing scalar OCS signatures and rendered photometric images. The benchmark uses a real satellite STL geometry with three component groups: metal body, solar panel, and baffle/shade. These components are assigned nonuniform GGX/Cook-Torrance material settings, and the same attitude definition, illumination direction, viewing direction, BRDF, and visibility assumptions are used to generate both OCS signatures and photometric images. The main yaw-pitch grid contains 73 yaw samples and 37 pitch samples, resulting in 2701 attitudes. For the OCS branch, five sun-sensor geometries are used, producing 13,505 attitude-geometry samples across a phase-angle range of approximately 24 deg to 120 deg.

Before evaluating attitude inversion, we checked the numerical consistency and visibility behavior of the forward model. Simple-geometry tests, including single-plate and cube-like closure cases, showed sub-percent agreement between analytical or facet-level OCS calculations and rendering-derived checks. Self-occlusion behavior was evaluated using synthetic single-plate, double-plate, U-block, and nested-cylinder cases, together with sampled Blender/manual ray-cast review. These checks support the use of the analytical ray-based visibility model for controlled OCS simulation. They should not be interpreted as real optical validation, but they reduce the risk that the inversion results are driven by obvious geometric or visibility implementation artifacts.

The OCS scans further show that attitude-dependent optical signatures are strongly affected by both observation geometry and self-occlusion. Across the five observation geometries, occlusion rates fall roughly in the 60% to 78.5% range, indicating that visibility is not a minor correction for this nonconvex three-component target. The resulting OCS maps and component-level contribution maps are therefore important not only as input features for inversion but also as observability diagnostics.

**Fig. 3 caption intent.** OCS maps and occlusion diagnostics. The figure should include yaw-pitch OCS heatmaps, part-level contribution maps, and occlusion-rate maps to show that scalar photometric signatures are attitude-dependent and visibility-sensitive.

### 4.2 OCS-only attitude inversion and multi-geometry photometric constraints

OCS-only inversion demonstrates that low-dimensional photometric signatures can provide useful yaw-pitch attitude constraints when multi-geometry and component-level information is retained. The practical `per_part_log` OCS representation reaches a mean angular error of 5.91 +/- 0.22 deg, with Hit@5 = 73.8% and Hit@10 = 94.3%. This result indicates that component-resolved OCS signatures encode substantially more attitude information than a single scalar total-brightness response.

The importance of feature design is visible across OCS variants. The `total_log` feature gives a much weaker result, with 36.69 +/- 3.6 deg mean error, Hit@5 = 9.7%, and Hit@10 = 23.5%. This weak baseline suggests that total OCS alone is often insufficient for precise yaw-pitch inversion in the tested setting. In contrast, the `all_raw` 45D representation reaches 3.98 +/- 0.60 deg, Hit@5 = 90.7%, and Hit@10 = 97.1%. However, this representation includes additional diagnostic quantities and is therefore treated as a semi-oracle upper bound rather than a practical observation setting.

The OCS-only results support two conclusions. First, OCS is not inherently weak: when multi-geometry and component-level information is available, it provides a useful and interpretable photometric constraint. Second, not every OCS representation has the same operational meaning. In the remaining Results, `per_part_log` is emphasized as the practical OCS-only setting at 5.91 deg, while `all_raw` is reported only as a diagnostic upper bound.

### 4.3 Image-only inversion: from TinyCNN to ResNet clean-image upper bound

Image-only inversion shows that clean rendered photometric images can provide highly informative attitude cues when model capacity is sufficient. The lightweight TinyCNN baseline reaches 12.38 +/- 0.74 deg mean error and Hit@5 = 26.1% on clean phase63 128 x 128 images. This result is useful as a lightweight baseline, but it should not be used to characterize the upper bound of image-based inversion.

When the image branch is evaluated with ResNet-18, the clean-image result improves to 1.69 +/- 0.07 deg mean error, Hit@5 = 97.6%, and Hit@10 = 99.9%. This establishes clean rendered photometric images as a strong upper-bound condition for image-based attitude inversion in the controlled benchmark. The result should be interpreted carefully: the rendered images are clean, aligned with the simulation distribution, and do not include atmosphere, optical PSF, detector response, earthshine, or background contamination. Therefore, this result is not a field-performance estimate for real telescope images.

We also audited the dataset structure to reduce the likelihood that the strong ResNet result is caused by trivial leakage. The train/test split follows the 10 deg -> 5 deg protocol, so test attitudes are not simply repeated training grid points. File names and labels are aligned, and normalization uses fixed constants rather than test-set statistics. The target centroid displacement has a correlation with yaw (r = 0.66), which is a physical rendering cue under the controlled camera setup, but this cue may not transfer to field observations where tracking and centering procedures can change the image-position distribution; we quantify its contribution directly with a centroid-control experiment in Section 4.7. Mean intensity is nearly uncorrelated with attitude (r < 0.02), reducing the concern that the network is using a simple brightness proxy for angle.

### 4.4 Clean-image fusion and modality dominance

Fusion under clean rendered images provides modest but meaningful gains when OCS is combined with a strong image model. The ResNet image-only baseline reaches 1.69 +/- 0.07 deg mean error, P90 = 3.31 deg, worst-case error = 9.9 deg, and Hit@5 = 97.6%. Adding `concat5 per_part_log` OCS features improves the result to 1.47 +/- 0.07 deg, P90 = 2.71 deg, worst-case error = 6.6 deg, and Hit@5 = 99.7%. In relative terms, the mean error decreases by 0.22 deg, and the worst-case error decreases by about one third.

This improvement should be described as conditional complementarity rather than fusion dominance. The clean image branch is already very strong, so the remaining mean-error margin is small. The main value of OCS in this setting is not to replace the image branch, but to improve tail behavior and provide an additional physical constraint. The comparison between fusion variants supports this interpretation. Using only phase63 `per_part_log` OCS features gives 1.61 +/- 0.07 deg, P90 = 2.97 deg, worst-case = 7.4 deg, and Hit@5 = 99.2%. In contrast, ResNet + `concat5 all_raw` reaches 1.49 +/- 0.10 deg but has a worse worst-case error of 18.7 deg, despite using a stronger semi-oracle OCS representation. Thus, a stronger OCS representation does not automatically produce better fusion tail behavior.

A direct mechanistic question is whether this clean-image fusion is balanced between modalities or dominated by the image branch. Branch-masking diagnostics on the clean-trained naive feature-fusion model show clear image dominance. Under clean images, the normal fused prediction reaches 1.57 deg; masking the OCS branch degrades it only modestly to 18.14 deg, whereas masking the image branch degrades it severely to 52.84 deg. The fused prediction therefore relies primarily on the image branch under nominal conditions, while the OCS branch contributes a smaller refinement. This image dominance is benign when images are clean, but it has direct consequences under degradation, which we examine next.

Earlier TinyCNN/OCS fusion experiments provide an additional diagnostic view of conditional complementarity. When OCS information is very strong (`all_raw`), adding a weaker image branch can hurt, with feature fusion reaching 5.42 deg compared with 3.98 deg for OCS-only. When OCS information is at an intermediate level (`per_part_log`), feature fusion improves from 5.91 deg for OCS-only and 12.38 deg for CNN-only to 4.10 +/- 0.77 deg. When OCS is weak (`total_log`), the image branch dominates, and late fusion reaches 11.99 deg compared with 36.69 deg for OCS-only. These trends indicate that fusion benefit depends on the information balance between modalities. In an earlier TinyCNN/OCS diagnostic, the error correlation between OCS and CNN was r = 0.003, suggesting complementary failure modes; this diagnostic should not be reported as a ResNet-pair correlation unless a corresponding ResNet analysis is performed.

**Table 2. Main inversion benchmark.**

| Method / feature | Input | Mean error (deg) | Hit@5 | Hit@10 | Role |
|---|---|---:|---:|---:|---|
| OCS MLP all_raw 45D | Multi-geometry OCS + diagnostic quantities | 3.98 +/- 0.60 | 90.7% | 97.1% | Semi-oracle OCS upper bound |
| OCS MLP per_part_log 30D | Practical component-level OCS | 5.91 +/- 0.22 | 73.8% | 94.3% | Practical OCS-only setting |
| OCS MLP total_log 15D | Total OCS only | 36.69 +/- 3.6 | 9.7% | 23.5% | Weak OCS baseline |
| Weighted kNN all_raw | OCS feature baseline | 21.84 | 47.9% | `[需要作者确认]` | Classical / low-capacity baseline |
| TinyCNN image-only | phase63 128 x 128 clean image | 12.38 +/- 0.74 | 26.1% | 55.8% | Lightweight image baseline |
| ResNet-18 image-only | phase63 128 x 128 clean image | 1.69 +/- 0.07 | 97.6% | 99.9% | Clean-image upper bound |

**Table 3. ResNet feature fusion under clean rendered images.**

| Case | Model / input | Mean +/- std (deg) | P90 (deg) | Worst (deg) | Hit@5 | Hit@10 | Interpretation |
|---|---|---:|---:|---:|---:|---:|---|
| A1 | ResNet image-only | 1.69 +/- 0.07 | 3.31 | 9.9 | 97.6% | 99.9% | Clean-image upper bound |
| A2 | ResNet + concat5 per_part_log 30D | 1.47 +/- 0.07 | 2.71 | 6.6 | 99.7% | 100% | Best clean fusion setting |
| A3 | ResNet + phase63 per_part_log 6D | 1.61 +/- 0.07 | 2.97 | 7.4 | 99.2% | 100% | Single-phase OCS fairness check |
| A4 | ResNet + concat5 all_raw 45D | 1.49 +/- 0.10 | 2.70 | 18.7 | 99.2% | 99.9% | Semi-oracle OCS does not guarantee tail robustness |

### 4.5 Degradation-aware fusion and modality-isolation controls

The image dominance of clean-trained fusion becomes a liability under image degradation. With additive Gaussian image noise at sigma = 0.01, the clean-trained naive feature-fusion model degrades from 1.57 deg to about 75 deg, comparable to the image-only collapse (the ResNet-fusion noise result is about 73 deg under sigma = 0.01). Branch masking shows that this is an active contamination effect rather than a passive loss of image information: under sigma = 0.01, masking the degraded image branch improves the noisy fused prediction from about 75 deg to about 53 deg, while masking the OCS branch worsens it to about 89 deg. The OCS branch therefore still carries useful information, but the clean-trained fusion head has not learned to rely on it when the image branch fails. Crucially, even the image-masked noisy fusion at about 53 deg remains far worse than the dedicated OCS-only predictor at 5.91 deg, so this must not be described as an automatic OCS fallback. Naive feature fusion does not automatically protect attitude inversion when the dominant modality degrades.

Degradation-aware fusion training (U1) substantially changes this behavior. By exposing the fusion model to image degradations during training, U1 retains 1.95 +/- 0.21 deg under clean images (Hit@5 = 97.8%, P90 = 3.53 deg), 1.95 deg under sigma = 0.01, and 2.31 +/- 0.26 deg under sigma = 0.10 (Hit@5 = 96.6%, P90 = 3.73 deg). It also remains near 2 deg under brightness scaling. U1 therefore strongly stabilizes mean and P90 errors under the tested degradations and prevents the clean-trained fusion collapse for degradation types represented in augmentation. However, worst-case errors above 100 deg persist for individual samples, so U1 must not be described as fully robust or near-perfect.

Three controls clarify the mechanism of U1's robustness. First, an image-only model trained with the same online image-degradation augmentation does not match U1: under sigma = 0.10 the image-only-plus-augmentation model reaches 9.55 deg while U1 reaches 2.31 deg, and U1 is consistently better across clean, noise, and brightness conditions (Table 5). The recovered robustness is therefore not a pure image-augmentation effect. Second, branch masking on U1 shows that the OCS branch is an active input to the joint representation: masking the OCS branch (replacing it with its training mean) degrades U1 to 30.87 deg under image degradation, while masking the image branch degrades it to about 56-59 deg. Both branches contribute, and neither masked variant approaches the standalone OCS-only predictor, confirming that U1 operates as coupled OCS-image co-utilization rather than a switch to OCS. Third, perturbing the OCS features monotonically degrades U1 (for example, 20% OCS noise raises U1 from 1.95 to 5.36 deg under clean images and from 2.31 to 5.95 deg under sigma = 0.10), which further supports active OCS involvement; this effect is not triggered specifically by image degradation, again arguing against a switching fallback interpretation.

U1 also generalizes to several held-out synthetic degradations not used in training. It remains near 2 deg under Gaussian noise at sigma = 0.03 (1.99 deg) and 0.05 (2.06 deg), under Gaussian blur (1.96 deg at kernel 3, 2.00 deg at kernel 5), and under downsampling (1.96 deg at 64 px, 2.01 deg at 32 px), whereas the image-only-plus-augmentation model is markedly worse (for example 6.43 deg at sigma = 0.05 and 4.93 deg at 32 px). This indicates that U1's robustness extends beyond exactly matched training degradations within synthetic perturbations, but it does not constitute real-observation validation.

By contrast, alternative upgrade strategies are weaker. Modality dropout alone (U2) does not defend against unseen image noise (about 84 deg under sigma = 0.10) and is reported as a negative result. Combined augmentation plus dropout (U3) is effective but inferior to U1, with a clean-accuracy and Hit@5 cost (about 2.90 deg clean, 4.59 deg under sigma = 0.10), and is reported in the Supplementary material. An OCS-anchored gating variant (U4) is mechanistically suggestive, with a gate that responds to noise, but its accuracy is insufficient (about 7.75 deg clean), so it is discussed only as a future direction.

Together, these results refine the central claim. Fusion is not automatically robust; clean-trained naive fusion is image-dominant and is contaminated by image degradation, with no automatic OCS fallback. Degradation-aware training restores stable average and tail behavior across the tested and several held-out synthetic degradations, and modality-isolation controls show that the mechanism is coupled OCS-image co-utilization, not a standalone OCS fallback. These claims hold within synthetic degradations and do not extend to real telescope robustness.

**Table 4. Modality-isolation diagnostics (clean-trained naive fusion vs U1).**

| Probe | Condition | Clean-trained fusion (deg) | U1 (deg) | Interpretation |
|---|---|---:|---:|---|
| Normal | clean | 1.57 | 1.95 | Both strong on clean images |
| Normal | image noise sigma=0.01 | ~75.08 | 1.95 | Naive fusion collapses; U1 stable |
| Normal | image noise sigma=0.10 | ~72.48 | 2.31 | Naive fusion collapses; U1 stable |
| Image-branch masked | clean | 52.84 | ~56.48 | Image branch dominant in clean fusion |
| Image-branch masked | image noise sigma=0.10 | 52.84 | 30.87 | Feature-level diagnostic, not single-modality performance |
| OCS-branch masked | clean | 18.14 | n/a | OCS contributes a refinement under clean images |
| OCS-branch masked | image noise sigma=0.01 | 88.88 | n/a | Removing OCS worsens noisy fusion; OCS still informative |

Note: branch masking replaces a branch input with zero or its training-set mean and is a feature-level diagnostic. Masked values are not single-modality predictors and remain far from the dedicated OCS-only result of 5.91 deg.

**Table 5. Degradation-aware fusion vs image-only same augmentation, and held-out synthetic degradations.**

| Condition | Image-only + same aug (deg) | U1 degradation-aware fusion (deg) |
|---|---:|---:|
| clean | 2.63 | 1.95 |
| Gaussian noise sigma=0.01 | 2.80 | 1.95 |
| Gaussian noise sigma=0.10 | 9.55 | 2.31 |
| Brightness x0.50 | 2.76 | 1.98 |
| Brightness x1.50 | 2.76 | 2.00 |
| Gaussian noise sigma=0.03 (held out) | 4.25 | 1.99 |
| Gaussian noise sigma=0.05 (held out) | 6.43 | 2.06 |
| Gaussian blur k3 (held out) | 2.84 | 1.96 |
| Gaussian blur k5 (held out) | 4.12 | 2.00 |
| Downsample 64 (held out) | 3.06 | 1.96 |
| Downsample 32 (held out) | 4.93 | 2.01 |

**Fig. 4 caption intent.** Image-degradation robustness of fusion variants. The figure should compare four curves across degradation levels: clean-trained image-only, clean-trained naive fusion, OCS-only reference at 5.91 deg, and U1 degradation-aware fusion, emphasizing that the noise tests are controlled/synthetic degradations rather than a full atmosphere/sensor model.

### 4.6 Ablation and sensitivity analysis

Several additional checks support the interpretation of the benchmark and define its limits. The 10 deg -> 5 deg split is designed to test interpolation over attitude space rather than direct memorization of all 5 deg grid states. Random split, phase63 fairness, BRDF sensitivity, occlusion ablation, and roll sensitivity should be reported as supporting analyses where finalized values are available `[需要作者确认：which ablations have final numbers for main text]`.

Self-occlusion sensitivity supports the chosen visibility settings. The benchmark uses `epsilon = 1.0 mm` and `min_hit_distance = 1.0 mm`, selected from synthetic-geometry validation and sensitivity scans on the real three-component model. This setting suppresses self-intersection in single-plate tests and retains cross-part and internal occlusion in double-plate, U-block, and nested-cylinder tests. In the main satellite scans, occlusion rates of roughly 60% to 78.5% across observation geometries show that self-occlusion is substantial and should not be ignored.

OCS-noise sensitivity also clarifies the conditional value of fusion. When the OCS branch is degraded by synthetic OCS noise while the image branch remains clean, the fusion gain increases from +1.97 deg at 0% OCS noise to +3.30 deg at 10% and +6.29 deg at 20%. At 10% OCS noise, OCS-only reaches 9.99 +/- 0.35 deg while fusion reaches 6.69 +/- 1.34 deg; at 20% OCS noise, OCS-only reaches 17.25 +/- 0.71 deg while fusion reaches 10.96 +/- 2.51 deg. The exact 0% OCS-only and fusion values for this OCS-noise table should be filled as `[需要作者确认：0% OCS noise table values]`. Because the image branch remains clean here, this is a one-sided modality-degradation analysis and not a complete field-degradation study.

The remaining limitations should be interpreted as study boundaries rather than hidden claims. The current benchmark estimates yaw and pitch under fixed roll. The main image branch uses phase63 clean rendered images, and broader cross-phase image generalization is examined only as a bounded sanity test (Section 4.7). Material parameters are nominal rather than target-calibrated. These choices make the benchmark controlled and interpretable, but they also define the scope of the reported Results.

**Fig. 5 caption intent.** Sensitivity and ablation summary. The figure should summarize OCS-noise fusion gain, occlusion, and split/phase-condition sensitivity only where final values are available; otherwise, unavailable items should remain in the author-confirmation list rather than being plotted.

### 4.7 Synthetic observation-style degradation and cross-geometry sanity tests

To bound the robustness claims of Sections 4.4 and 4.5, we evaluate a set of observation-chain-inspired synthetic stress tests. These tests are not real telescope validation; they probe whether the conclusions survive more structured synthetic degradations and off-nominal geometries.

First, under synthetic observation-style image degradations applied in the linear intensity domain, clean-trained image-only inversion collapses while U1 remains stable up to a boundary. Read-out noise, background offset, a synthetic starfield, and a medium combined degradation each drive the clean-trained image-only model above 78 deg (for example 87.30 deg for read-out noise and 88.99 deg for medium combined degradation), while U1 remains near 2 deg (1.95 to 2.20 deg). The OCS-only predictor is unaffected by image degradation at 6.58 deg in this stress-test configuration. However, under severe combined degradation, U1 degrades to 13.88 deg, identifying a clear failure boundary. This supports conditional robustness with an explicit boundary, not fully robust behavior, and it shows that a low-dimensional photometric constraint such as OCS retains value under severe image degradation without implying that U1 automatically falls back to OCS.

Second, a cross-phase rendering sanity test shows that the clean-image upper bound depends on phase63 in-distribution rendering. Under phase24, image-only inversion degrades to 11.34 deg and feature fusion to 6.85 deg, while under phase120 both collapse (image-only 83.08 deg, fusion 79.71 deg). The phase120 case is a strong cross-geometry failure mode; cross-phase generalization is not solved by the present models.

Third, a centroid-control experiment quantifies the contribution of fixed-framing cues. When the target is recentered so that the centroid-displacement cue is removed, clean-image ResNet image-only inversion degrades from 1.69 deg (P90 = 3.31 deg, Hit@5 = 97.6%) to 2.88 deg (P90 = 5.42 deg, Hit@5 = 87.4%). The clean-image upper bound therefore partly depends on fixed-framing/centroid cues, but it is not solely centroid leakage, because substantial shape information remains after recentering.

Fourth, an explicit late-fusion beta sweep characterizes inference-time weighting as an upper bound. Under clean images, the best image weight is near beta = 0.9 (best 1.67 deg), close to the image end. Under Gaussian image noise, the oracle best weight moves to beta = 0 (OCS end) with a best of 6.58 deg, which is far better than the naive feature-fusion collapse near 73 deg, but this best beta is selected with oracle knowledge of the degradation. Explicit weighting is therefore an inference-time robustness upper bound, not a deployable automatic gate: deployment would require independent degradation detection, confidence estimation, or a learned gating policy. The 6.58 deg OCS end in this beta sweep comes from a within-experiment OCS retrain and is used only as an internal reference for the beta sweep; it must not be conflated with the main-line OCS-only result of 5.91 deg as a performance change.

Fifth, an outlier audit over all test evaluations confirms that rare large errors persist. Across 49,950 evaluations, errors above 30 deg occur in 42 cases (0.084%), above 60 deg in 40 cases (0.080%), and above 90 deg in 35 cases (0.070%), and these outliers are concentrated near polar attitudes (|pitch| large). The main text therefore reports mean, P90, and Hit@5 as stable while explicitly retaining worst-case and polar outliers as a limitation.

**Table 6. Synthetic observation-style degradation and cross-phase sanity tests (main-text compressed).**

| Stress test | Clean-trained image-only (deg) | U1 / fusion (deg) | OCS-only (deg) | Interpretation |
|---|---:|---:|---:|---|
| Clean (phase63) | 1.72 | 1.95 (U1) | 6.58 | Clean image is an upper bound, not a field promise |
| Read-out noise | 87.30 | 1.95 (U1) | 6.58 | U1 stable under additive read-out noise |
| Background offset | 78.57 | 2.12 (U1) | 6.58 | Image-only collapses under background contamination |
| Synthetic starfield | 86.39 | 2.20 (U1) | 6.58 | U1 stable under starfield contamination |
| Combined (medium) | 88.99 | 1.98 (U1) | 6.58 | U1 stable under moderate combined degradation |
| Combined (severe) | 88.85 | 13.88 (U1) | 6.58 | Severe combined degradation remains a failure boundary |
| Cross-phase phase24 | 11.34 | 6.85 (fusion) | n/a | Near-back-scatter geometry already degraded |
| Cross-phase phase120 | 83.08 | 79.71 (fusion) | n/a | Strong cross-geometry failure case |

Note: the OCS-only column reports the within-stress-test OCS retrain (6.58 deg). It is an internal reference for this configuration and is distinct from the main-line OCS-only result of 5.91 deg.

**Fig. 6 caption intent.** Synthetic observation-style and cross-geometry stress tests. The figure should show image-only collapse versus U1 stability under read-out/background/starfield/combined-medium degradations, the severe-combined and phase120 failure boundaries, and the explicit-weighting oracle upper bound, with text clearly stating these are synthetic stress tests, not real telescope validation. Centroid-control and the outlier audit are placed in the Supplementary material and named in Limitations.

## 5. Discussion

### 5.1 Main finding: controlled, design-dependent complementarity between OCS and photometric images

The main finding is that scalar OCS signatures and resolved photometric images provide different attitude constraints when they are generated from the same BRDF-driven physical model, and that the value of fusing them is conditional on fusion architecture and training. The benchmark is not simply a comparison of neural architectures. It isolates how two optical modalities behave when geometry, material assignment, attitude convention, BRDF, illumination, viewing geometry, and self-occlusion are held consistent, and how their fusion responds when image quality degrades. Within this controlled setting, clean photometric images define a strong image-based upper-bound case, OCS provides a low-dimensional and interpretable photometric constraint that remains independent of image-pixel degradation, and fusion is helpful or harmful depending on how it is designed and trained.

This framing changes the interpretation of multi-modal fusion. Fusion should not be understood as a universal accuracy maximizer or an automatic robustness mechanism. A clean-trained naive feature-fusion model is image-dominant and inherits the image branch's fragility, collapsing under image degradation rather than falling back to OCS. Only when fusion training explicitly accounts for degradation does the model retain stable average and tail behavior, and even then the mechanism is coupled OCS-image co-utilization rather than a switch to standalone OCS. The results therefore support conditional, design-dependent complementarity rather than a fixed hierarchy between OCS, images, and fusion.

### 5.2 Why clean rendered images give a strong image-only upper bound

The strong ResNet-18 image-only result is understandable because the clean rendered images preserve stable visual cues that are tightly linked to yaw-pitch attitude. These cues include projected shape, shadow structure, component layout, centroid displacement, brightness distribution, and specular patterns. A higher-capacity CNN can exploit these cues more effectively than a lightweight TinyCNN, which explains the large difference between the TinyCNN baseline and the ResNet-18 clean-image result.

However, this result should be interpreted as an optimistic upper-bound case for image-based inversion under idealized rendered photometric images. The images do not include atmosphere, detector response, optical PSF, earthshine, background contamination, tracking errors, or real calibration uncertainty. The degradation experiments support this boundary: under 1% Gaussian image noise, ResNet performance collapses from the clean-image upper-bound regime to a mean error above 85 deg with Hit@5 near 2%. The centroid-control experiment further shows that part of the clean-image advantage depends on fixed-framing/centroid cues, since recentering raises the error from 1.69 deg to 2.88 deg; the residual accuracy indicates that shape information remains informative but that fixed framing should not be assumed in field observations. The cross-phase sanity test shows that the upper bound is also tied to the in-distribution phase63 geometry, with phase120 representing a strong failure mode. These results do not mean image-based inversion is inherently unreliable; they show that clean synthetic image performance must be separated from degraded-observation robustness and from cross-geometry generalization.

### 5.3 Why OCS remains useful despite lower clean-image accuracy

OCS is not the accuracy upper bound when clean resolved images are available. The practical `per_part_log` OCS-only setting at 5.91 deg is less accurate than ResNet-18 under clean rendered images. Its value lies elsewhere: OCS is low-dimensional, physically interpretable, available across multiple observation geometries, and independent of image pixels in this benchmark. These properties make it a useful complementary constraint when high-quality resolved images are unavailable, degraded, or operationally expensive, as the synthetic observation-style stress tests illustrate, where OCS-only remains stable while clean-trained image-only inversion collapses.

The distinction between practical and diagnostic OCS features is important. The `per_part_log` representation provides a practical OCS-only setting, whereas the `all_raw` 45D representation should be interpreted as a semi-oracle diagnostic upper bound because it includes additional quantities beyond a straightforward operational OCS feature. Presenting both results is useful: the practical feature shows what component-level OCS can support, while the semi-oracle setting indicates the information potential when richer diagnostic quantities are available. It would be misleading, however, to treat `all_raw` as the main operational OCS result.

OCS robustness should also be stated carefully. In this benchmark, OCS is independent of image-pixel degradation because it is generated and used as a separate scalar photometric modality. This does not imply immunity to all real observational errors. Real OCS or light-curve measurements may be affected by photometric calibration error, atmospheric transparency variation, geometry uncertainty, BRDF mismatch, target-model mismatch, and measurement noise; the OCS-noise sensitivity analysis already shows monotonic degradation under synthetic OCS noise. The claim is therefore not that OCS is universally robust, but that it provides a non-image photometric constraint whose failure modes can differ from those of resolved images.

### 5.4 The fusion mechanism: contamination, co-utilization, and the limits of fallback

The fusion results require a careful mechanistic reading. Under clean images, adding `concat5 per_part_log` OCS improves the mean error from 1.69 deg to 1.47 deg, increases Hit@5 from 97.6% to 99.7%, and reduces the worst-case error from 9.9 deg to 6.6 deg. The mean gain is modest because the clean image branch is already strong, but the tail improvement is important for a task where occasional large errors may be operationally more consequential than small changes in average error. At the same time, fusion is not automatically improved by a stronger or richer OCS representation: ResNet + `concat5 all_raw` achieves a similar mean error but a worse worst-case error of 18.7 deg, a warning that semi-oracle features may improve aggregate metrics while harming tail behavior.

The key mechanistic result concerns degradation. Clean-trained naive feature fusion is image-dominant, and under image noise the degraded image branch actively contaminates the fused representation, driving the error to about 75 deg. Branch masking shows that the OCS branch still carries information (removing it worsens the noisy case from about 75 deg to about 89 deg), but the fusion head has not learned to use OCS as a standalone fallback: masking the failed image branch only improves the noisy case to about 53 deg, still far above the dedicated OCS-only predictor at 5.91 deg. This is direct evidence that naive fusion does not automatically provide an OCS fallback when the dominant modality fails.

Degradation-aware training (U1) prevents this collapse, and the controls explain why this is not merely an image-augmentation effect. U1 outperforms an image-only model trained with the same augmentation (2.31 deg vs 9.55 deg at sigma = 0.10), branch masking shows the OCS branch is an active input to U1's joint representation, and OCS-feature perturbation monotonically degrades U1. The most accurate description is coupled OCS-image co-utilization: degradation-aware training prevents the fused representation from over-specializing to pristine image statistics and lets both modalities jointly inform the prediction. It does not establish that OCS alone rescues the model, nor that the model switches to OCS when images fail. Modality dropout alone (U2) is insufficient, combined augmentation plus dropout (U3) is effective but inferior with a clean-accuracy cost, and the OCS-anchored gate (U4) is directionally interesting but not yet accurate enough; these comparisons indicate that degradation-aware joint training, not a single architectural trick, is what restores robustness here.

Finally, the explicit late-fusion beta sweep frames the ceiling of simple weighting strategies. Under noise, the oracle best weight moves to the OCS end (beta = 0, 6.58 deg), far better than naive fusion, but this weight is chosen with oracle knowledge of the degradation. Explicit inference-time weighting is therefore an upper bound on what a perfectly informed gate could achieve, not a deployable automatic gate; a deployable system would need independent degradation detection or confidence estimation. The 6.58 deg OCS end here is an internal beta-sweep reference and is not the main-line OCS-only result.

### 5.5 Implications for space object attitude inversion

The results suggest several practical principles for future optical attitude-inversion studies. First, clean-image performance should be reported separately from degraded-image performance and from cross-geometry generalization. A high-capacity image model may achieve very high accuracy under clean synthetic imagery, but this upper-bound setting does not by itself establish field robustness, and it can depend on fixed framing and in-distribution phase geometry. Second, scalar photometric constraints such as OCS should not be evaluated only by whether they outperform clean images. Their value includes interpretability, low dimensionality, multi-geometry availability, and different failure modes.

Third, fusion should be designed and evaluated for robustness, not assumed to provide it. Naive feature fusion can be image-dominant and can fail exactly when robustness is most needed. Degradation-aware training, modality-isolation diagnostics, and tail metrics (Hit@5, Hit@10, P90, worst-case) are necessary to characterize when fusion helps. For operational use, the demonstrated mechanism is coupled co-utilization under known synthetic degradations, and any claim of automatic fallback or deployable gating would require additional degradation detection and real-data validation.

Finally, a unified forward model is essential for interpreting modality comparisons. If OCS and images are generated using different geometry, material, BRDF, or visibility assumptions, it is difficult to attribute performance differences to modality information. The proposed benchmark therefore provides a controlled way to study modality complementarity and fusion mechanism before moving to field observations. It should be seen as a step toward, not a substitute for, real optical validation.

### 5.6 Scope and limitations

The present study has several scope limitations. It does not use real optical telescope images with known attitude ground truth. The clean rendered images are idealized photometric images and exclude atmosphere, detector response, optical PSF, earthshine, background contamination, and tracking errors. As a result, the ResNet-18 image result should be interpreted as a clean-image upper bound rather than expected field performance, and the synthetic observation-style stress tests are observation-chain-inspired rather than real-observation validation.

The robustness conclusions are bounded. Degradation-aware fusion (U1) is stable in mean, P90, and Hit@5 across the tested and several held-out synthetic degradations, but rare large outliers persist (about 0.084% of evaluations exceed 30 deg, concentrated near polar attitudes), severe combined degradation degrades U1 to 13.88 deg, and the cross-phase phase120 case remains a strong failure mode. Modality dropout alone and the observation-style augmentation variants are not uniformly successful, and the OCS-anchored gate is not yet accurate; these are reported honestly as partial or negative results. The explicit late-fusion beta sweep is an oracle inference-time upper bound and is not a deployable automatic gate.

The attitude task is also bounded. The benchmark estimates yaw and pitch under fixed roll and does not claim full 3-DOF pose recovery. The main image branch uses one rendered phase condition for training, so broader cross-phase image generalization is examined only as a sanity test. Part of the clean-image accuracy depends on fixed-framing/centroid cues, as shown by the centroid-control experiment. Material parameters are nominal rather than calibrated for the specific target, and further BRDF sensitivity analysis and material validation are needed for stronger physical claims. These limitations define the boundary of the present controlled study and motivate future work on calibrated material parameters, real optical datasets, cross-phase imagery, full roll variation, deployable degradation-aware gating, and more realistic sensor/atmosphere models.

## 6. Conclusion

This paper presented a unified BRDF-driven simulation and controlled inversion benchmark for space object yaw-pitch attitude estimation from OCS signatures and photometric images. By generating both modalities from the same STL geometry, nonuniform material assignment, GGX/Cook-Torrance BRDF, attitude definition, and self-occlusion model, the study isolates how scalar photometric signatures and resolved images contribute to attitude inversion under consistent physical assumptions, and how their fusion behaves under image degradation.

The results show that clean rendered photometric images provide a strong upper-bound case for image-based inversion, with ResNet-18 reaching 1.69 +/- 0.07 deg under idealized imagery, while the same image-only setting is highly fragile under additive image noise. OCS does not define the clean-image accuracy upper bound, but the practical `per_part_log` OCS setting at 5.91 deg provides an interpretable, image-independent photometric constraint. Multi-modal fusion is architecture- and training-dependent: clean-trained naive feature fusion is image-dominant and is contaminated, not protected, under image degradation, with no automatic OCS fallback; degradation-aware fusion training restores stable mean, P90, and Hit@5 across the tested and several held-out synthetic degradations through coupled OCS-image co-utilization. Synthetic observation-style degradation, cross-phase, centroid-control, and explicit-weighting stress tests bound these claims, identifying severe combined degradation, the phase120 cross-geometry case, and rare polar outliers as remaining failure modes, and framing explicit inference-time weighting as an upper bound rather than a deployable gate.

The current study does not include real optical telescope validation and is limited to yaw-pitch inversion under fixed roll with clean rendered images and nominal material parameters. Future work should extend the benchmark to calibrated materials, broader phase and roll conditions, deployable degradation-aware gating with explicit confidence estimation, explicit atmosphere and sensor modeling, and real optical observations with reliable attitude ground truth.

## Data Availability

Data availability will be specified in the final submission. `[需要作者确认：whether simulation data, STL-derived products, trained models, and scripts can be shared; repository or access statement]`

## Author Contributions

Author contributions will be completed before submission according to the target journal format. `[需要作者确认：author list and CRediT roles]`

## Funding

Funding information will be completed before submission. `[需要作者确认：funding sources and grant numbers]`

## Conflict of Interest

The authors declare no conflict of interest. `[需要作者确认：final conflict-of-interest wording required by target journal]`

## References

Reference metadata remains to be verified. Current placeholders include:

- `[CITATION: optical space object characterization]`
- `[CITATION: optical light-curve attitude inversion]`
- `[CITATION: BRDF-based space object photometry]`
- `[CITATION: image-based spacecraft pose estimation]`
- `[CITATION: ground-based optical observation degradation]`
- `[CITATION: multi-modal fusion robustness]`
- Yang et al. 2024/2025 Photonics `[to verify]`
- Lu/Yao 2024 Universe `[to verify]`
- Fankhauser et al. 2023 AJ `[to verify]`
- Wang et al. 2024 ASR `[to verify]`
- Burton et al. 2024 ASR `[to verify]`
- Dickinson 2025 RIT PhD `[to verify]`
- Kumar et al. 2025 Acta Astronautica `[to verify]`
- Liu et al. 2024 Remote Sensing `[to verify]`

---

## B. Integration Notes

This section explains how experiments 12 (07), 12b (07b), and 12c-12g (07c) enter the manuscript, so Codex can trace each claim to its source.

### B.1 How 07 (experiment 12) enters the text

- **Methods 3.9** introduces the fusion-mechanism diagnostics: clean-trained naive fusion, branch masking, U1 degradation-aware training, and the U2/U3/U4 alternatives. This is the methodological home for all of experiment 12.
- **Results 4.4** adds the clean-image branch-masking result (normal 1.57, OCS-masked 18.14, image-masked 52.84) to establish image dominance under clean conditions, connecting it to the existing v0.1 fusion table.
- **Results 4.5** is the core 07 narrative: naive fusion contamination under noise (~75 deg), branch masking under noise (image-masked ~53, OCS-masked ~89), U1 recovery (1.95 clean, 2.31 at sigma=0.10), and the U2 (negative), U3 (supplementary), U4 (future) comparisons.
- **Discussion 5.4** gives the mechanistic interpretation: contamination, no automatic fallback, and degradation-aware training as the fix.
- Red-line compliance: image masking is always labeled a feature-level diagnostic; the ~53 deg image-masked value is explicitly stated to be far from OCS-only 5.91 deg, so it is never written as an OCS fallback.

### B.2 How 07b (experiment 12b) enters the text

- **Methods 3.9** adds the three isolation controls: image-only same augmentation, U1 branch masking, and OCS-noise perturbation, plus held-out synthetic degradations.
- **Results 4.5 and Table 5** carry 12b-1 (image-only+aug vs U1: 9.55 vs 2.31 at sigma=0.10) and 12b-5 (held-out degradations). **Table 4** carries 12b-2 (U1 branch masking: 30.87 image-masked, ~56-59 OCS-masked). The OCS-noise control (12b-3: 5.36 clean, 5.95 noise at 20%) is in the 4.5 text.
- **Results 4.7 fifth point** and **Limitations 5.6** carry 12b-4 outlier audit (42/49,950 = 0.084%, polar), shared with 12g.
- **Discussion 5.4** states the co-utilization conclusion explicitly and rejects standalone fallback.
- Red-line compliance: the mechanism is named "coupled OCS-image co-utilization / active joint constraint"; the phrase "OCS standalone fallback" is explicitly negated; U1 is never called fully robust.

### B.3 How 07c (experiments 12c-12g) enters the text

- **Methods 3.10** defines the synthetic observation-style stress tests, centroid control (linear-domain centroid), explicit beta sweep (beta = image weight), and outlier audit. **Methods 3.7/3.9** specify the `expm1 -> degradation -> log1p` linear-intensity-domain operator and the phase24/phase120 full-grid renders (3.3).
- **Results 4.7** is the dedicated 07c section: 12c (Table 6, U1 ~2 deg vs image-only collapse, combined_severe 13.88), 12d (phase24 11.34/6.85, phase120 83.08/79.71), 12e centroid control (1.69 -> 2.88), 12f beta sweep (noise best beta=0, 6.58), 12g outlier audit. Per the integration list, 12c/12d/12f are in the main text; 12e and 12g are flagged for Supplementary with a named mention in Limitations.
- **Discussion 5.2/5.4** uses 12d (cross-phase dependence), 12e (centroid dependence), and 12f (oracle weighting ceiling).
- **Limitations 5.6** carries combined_severe, phase120, centroid dependence, outliers, and the oracle-not-gate caveat.
- Red-line compliance: 12c is "observation-chain-inspired synthetic degradation stress test"; phase120 and combined_severe are named failure boundaries; 12f best beta is an oracle upper bound; the 6.58 deg OCS end is explicitly separated from the main-line 5.91 deg.

### B.4 Why all three integrate in one pass

U1 (the protagonist of 12c) originates in 07; its mechanism boundary (co-utilization, not fallback) comes from 07b. Integrating only 07c would break the narrative, because the reader would meet U1 in stress tests without the diagnostic basis for trusting it. The Results therefore flow: clean fusion and dominance (4.4) -> degradation-aware fusion and isolation controls (4.5) -> sensitivity (4.6) -> synthetic observation-style and cross-geometry stress tests (4.7).

## C. Tables/Figures To Update

### Main-text tables

- **Table 1** Related work positioning — retained from v0.1, with the "Present work" row updated to mention degradation-aware fusion diagnosis. Metadata still `[to verify]`.
- **Table 2** Main inversion benchmark — retained from v0.1.
- **Table 3** ResNet feature fusion under clean images — retained from v0.1.
- **Table 4 (new)** Modality-isolation diagnostics (clean-trained naive fusion vs U1; branch masking). From 07/07b.
- **Table 5 (new)** Degradation-aware fusion vs image-only same augmentation, plus held-out synthetic degradations. From 07b (12b-1, 12b-5).
- **Table 6 (new)** Synthetic observation-style degradation and cross-phase sanity tests. From 07c (12c, 12d).

### Supplementary tables (recommended)

- **S1** U1 full degradation table with worst-case and seed std (07: clean 1.95/worst 102.11, sigma=0.10 2.31/worst 164.27, etc.).
- **S2** U2/U3/U4 alternative upgrade strategies (07: U2 ~84 at sigma=0.10; U3 2.90 clean/4.59 noise; U4 7.75 clean).
- **S3** OCS-noise fusion-gain table including the `[需要作者确认：0% OCS noise table values]`.
- **S4** Centroid-control experiment (12e: original 1.69/3.31/97.6% vs centered 2.88/5.42/87.4%).
- **S5** Outlier audit and polar concentration (12g/12b-4: 42/40/35 of 49,950 above 30/60/90 deg).
- **S6** Explicit late-fusion beta sweep full table (12f: per-condition beta=0/beta=1/best beta/best).

### Figures

- **Fig. 1** Pipeline (updated to show degradation-aware and stress-test branches).
- **Fig. 2** Geometry and observation setup (add phase24/phase120 sanity-test note).
- **Fig. 3** OCS maps and occlusion diagnostics (retained).
- **Fig. 4 (new)** Image-degradation robustness of fusion variants (image-only, naive fusion, OCS-only 5.91 reference, U1).
- **Fig. 5** Sensitivity/ablation summary (OCS-noise gain, occlusion, split/phase) — only finalized values.
- **Fig. 6 (new)** Synthetic observation-style and cross-geometry stress tests (12c/12d/12f), with failure boundaries marked.

Note: v0.1 figure numbering had a Fig. 5 (degradation) and Fig. 6 (OCS noise); v0.2 renumbers so that Fig. 4 is fusion-degradation robustness and Fig. 6 is synthetic stress tests. Codex should finalize numbering during integration.

## D. Limitations and Red-line Audit

Per-line self-check against the guidance §8 and the project red lines.

| Red line | Status in this draft | Where enforced |
|---|---|---|
| No "fusion automatically robust" | Pass — naive fusion is shown to collapse; only degradation-aware training is stable, and only within synthetic degradations | 4.5, 5.1, 5.4, Abstract |
| No "U1 automatically switches to OCS" | Pass — explicitly negated; mechanism is co-utilization | 4.5, 5.4, B.2 |
| No "OCS standalone fallback" | Pass — image-masked values stated to remain far from OCS-only 5.91 deg | 4.5, Table 4 note, 5.4 |
| No "near-perfect / fully robust" | Pass — rare outliers, combined_severe, phase120 all retained | 4.5, 4.7, 5.6 |
| No "real telescope validation" | Pass — stated in Abstract, 3.1, 4.7, 5.6, 6 | throughout |
| No "operational / field-proven robustness" | Pass — stress tests labeled observation-chain-inspired synthetic | 4.7, 5.6 |
| No "phase120 generalization is solved" | Pass — phase120 named as strong failure case | 4.7, 5.2, 5.6 |
| No "obs-aug is a successful robust training strategy" | Pass — U2/obs-aug variants reported as negative/partial | 4.5 (U2), 5.4, 5.6 |
| No "12f best beta is deployable automatic gating" | Pass — oracle inference-time upper bound; deployment needs detection/confidence | 4.7, 5.4, 5.6 |
| Clean images are upper bound, not field | Pass | Abstract, 4.3, 5.2, 6 |
| 12c is synthetic stress test | Pass | 3.10, 4.7, 5.6 |
| 12f beta sweep is oracle upper bound | Pass | 4.7, 5.4 |
| Rare large outliers remain | Pass | 4.7, 5.6 |
| Separate OCS-only 5.91 (main) from 6.58 (12f internal) | Pass — explicitly separated wherever 6.58 appears | 4.7 note, Table 6 note, 5.4 |
| `all_raw` is semi-oracle, not operational | Pass | 3.6, 3.8, 4.2, 5.3 |
| `r = 0.003` limited to TinyCNN/OCS | Pass — flagged not-ResNet | 4.4 |
| No invented experiments/citations/author facts | Pass — only audited numbers; citations remain `[to verify]`; Q12-Q14 placeholders kept | References, Data/Author/Funding/COI |

Honest negative/partial results retained (not hidden): U2 modality dropout fails under unseen noise; U3 inferior to U1 with clean-accuracy cost; U4 gate not accurate enough; combined_severe and phase120 are failure boundaries; centroid contributes to clean-image accuracy; rare polar outliers persist.

## E. Remaining Placeholders

Items not filled by this draft (require author or Codex action before submission):

1. `[需要作者确认：Euler order / rotation matrix convention]` (Method 3.2).
2. `[需要作者确认：exact target encoding]` — drafted as sin-cos per Q-answers, but kept flagged (Method 3.8).
3. `[需要作者确认：angular error formula]` — drafted as great-circle, kept flagged (Method 3.11).
4. `[需要作者确认：phase63 fairness and cross-phase values]` (Method 3.3); phase24/phase120 numbers are from 12d and used as sanity tests.
5. `[需要作者确认：0% OCS noise table values]` (Result 4.6 / S3).
6. `[需要作者确认：which ablations have final numbers for main text]` (Result 4.6): BRDF sensitivity, occlusion ablation, roll sensitivity, random split.
7. `[需要作者确认]` for Weighted kNN all_raw Hit@10 (Table 2).
8. Table 1 references and all `[to verify]` bibliographic metadata; reference list still placeholder.
9. `[CITATION: ...]` placeholders in Introduction and Related Work.
10. **Q12** Data/Code availability — `[需要作者确认]` placeholder kept; not AI-filled.
11. **Q13** Author contributions / CRediT — `[需要作者确认]` placeholder kept; not AI-filled.
12. **Q14** Funding and Conflict of Interest — `[需要作者确认]` placeholders kept; not AI-filled.

Open question for Codex/author: whether the OCS-noise fusion-gain table (currently Result 4.6, from v0.1) should stay in the main text alongside the new 4.5 isolation controls, or move to Supplementary S3 to keep the main robustness narrative focused on image degradation. This draft keeps it in 4.6 but flags it.
