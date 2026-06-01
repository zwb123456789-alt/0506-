# Step 7 GPT 输出：全文整合初稿

## A. Integrated Manuscript Draft

# BRDF-Driven Optical Cross Section and Photometric Image Simulation for Robust Space Object Attitude Inversion

## Abstract

Space object attitude inversion from optical observations remains challenging because scalar photometric signatures and resolved photometric images encode different, observation-dependent attitude information. Existing studies often evaluate light-curve-like signatures, image-based pose estimation, and fusion under different modeling assumptions, making it difficult to determine when the modalities are complementary. Here we construct a physically consistent simulation and controlled inversion benchmark that generates optical cross section (OCS) signatures and photometric images from the same satellite STL geometry, nonuniform material assignment, GGX/Cook-Torrance BRDF, yaw-pitch attitude definition, observation geometry, and analytical self-occlusion model. Under clean synthetic photometric images, a ResNet-18 image-only model reaches 1.69 +/- 0.07 deg with Hit@5 = 97.6%, defining an optimistic upper-bound condition for image-based inversion rather than field performance. However, 1% Gaussian image noise degrades the same image-only setting to 85.85 +/- 3.00 deg with Hit@5 = 2.2%. Practical component-level OCS features provide a lower-dimensional and interpretable photometric constraint, while OCS-image fusion reduces selected clean-image tail errors, including a worst-case reduction from 9.9 deg to 6.6 deg. These results suggest that OCS-image fusion should be interpreted as conditional complementarity rather than universal superiority. Real optical telescope validation, calibrated material measurements, and explicit atmosphere/sensor modeling remain necessary before operational field-performance claims can be made.

**Keywords:** space object attitude inversion; optical cross section; photometric image simulation; BRDF; self-occlusion; multi-modal fusion; robustness

## 1. Introduction

Optical observations provide one of the most practical ways to infer the attitude and scattering behavior of non-cooperative space objects when cooperative telemetry is unavailable. The measured optical signal depends jointly on object geometry, surface reflectance, illumination direction, viewing direction, phase angle, and self-occlusion. Attitude inversion is therefore not only a regression or learning problem, but also a forward-modeling problem in which the physical origin of the observation affects the reliability of the inferred attitude [CITATION: optical space object characterization]. This study focuses on controlled yaw-pitch attitude inversion from two optical modalities: scalar optical cross section (OCS) signatures and resolved photometric images. The aim is to determine how these two measurements contribute to attitude estimation under ideal and degraded observation conditions, not to claim operational performance from field telescope images.

OCS signatures and photometric images encode different aspects of the same attitude-dependent scattering process. OCS or light-curve-like measurements summarize the reflected optical response under a given sun-sensor geometry, making them low-dimensional, interpretable, and relatively inexpensive to obtain across multiple observation geometries [CITATION: optical light-curve attitude inversion]. Photometric images, by contrast, preserve spatial cues such as projected outline, component layout, shadow structure, centroid displacement, brightness distribution, and specular highlights [CITATION: image-based spacecraft pose estimation]. Clean resolved images can therefore be highly informative for attitude inversion, but their usefulness depends strongly on image quality and on consistency between training and test conditions. OCS should not be treated as the performance upper bound when clean resolved imagery is available; its value lies in robust photometric constraint, multi-geometry availability, and physical interpretability. Conversely, images should not be treated as merely auxiliary, because clean images may carry strong attitude cues.

The key unresolved question is when these two modalities are complementary. Answering this question requires more than training separate regressors on separate data products. If OCS and images are generated with inconsistent assumptions about geometry, material reflectance, BRDF, attitude parameterization, or self-occlusion, differences in inversion accuracy cannot be attributed cleanly to modality information [CITATION: BRDF-based space object photometry]. Similarly, image-based results on clean synthetic images should not be interpreted as direct estimates of field performance, because real ground-based optical observations are affected by atmospheric seeing, tracking error, sensor noise, optical blur, limited resolution, background contamination, and phase-angle variation [CITATION: ground-based optical observation degradation]. A useful benchmark should therefore generate both modalities from the same physical model and evaluate them across ideal and degraded conditions, so that complementarity can be analyzed as a conditional property rather than assumed as a universal benefit of fusion.

Here we present a unified BRDF-driven OCS-image simulation and controlled inversion benchmark for space object attitude estimation. The forward model uses a real satellite STL geometry with nonuniform material assignment, a GGX/Cook-Torrance BRDF, analytical ray-based self-occlusion, and shared yaw-pitch attitude and observation geometry definitions. From this common model, we generate OCS signatures and photometric images and evaluate OCS-only, image-only, late-fusion, and feature-fusion models. The benchmark reveals three linked behaviors. First, clean synthetic images provide an optimistic upper-bound case: a ResNet-18 image-only model reaches 1.69 +/- 0.07 deg with Hit@5 = 97.6%. Second, this image-based performance is fragile under controlled degradation: 1% Gaussian image noise degrades the result to 85.85 +/- 3.00 deg with Hit@5 = 2.2%. Third, OCS provides a low-dimensional photometric constraint, and OCS-image fusion can improve selected tail errors when the modalities retain complementary information.

This paper makes four contributions. First, it introduces a physically consistent forward simulation framework that links OCS and photometric images through the same geometry, material assignment, GGX reflectance, attitude convention, observation geometry, and self-occlusion model. Second, it establishes a controlled yaw-pitch inversion benchmark comparing OCS-only, image-only, late-fusion, and feature-fusion models under shared data-generation assumptions. Third, it separates clean-image upper-bound performance from degraded-observation robustness, showing that strong CNN performance under ideal synthetic images should not be read as a field-performance guarantee. Fourth, it characterizes OCS-image fusion as conditional complementarity: fusion is useful when it improves tail errors or provides a fallback under degradation, but it should not be described as universally superior. The present study does not use real optical telescope images with known attitude ground truth and does not explicitly model atmosphere, detector response, PSF, earthshine, or background contamination. These limitations define the scope of the current controlled study and the requirements for future field validation.

## 2. Related Work

### 2.1 Optical signatures and BRDF modeling of space objects

Optical signatures of space objects are governed by the coupled effects of target geometry, surface material, illumination direction, viewing direction, phase angle, and visibility. BRDF-based modeling is therefore central to physically meaningful satellite photometry, because it links surface reflectance behavior to observed brightness or image intensity under varying geometries. Studies of satellite material reflectance and goniopolarimetric behavior provide experimental and semi-empirical support for using BRDF models, including Cook-Torrance-type descriptions, to represent satellite surface scattering [Yang et al., 2024/2025, to verify]. Large-scale satellite brightness studies further show that BRDF-based photometric models can explain and predict the brightness behavior of LEO constellation satellites using real observation campaigns [Lu/Yao, 2024, to verify]. Radiometric analyses also emphasize that satellite optical brightness can depend on effects beyond direct sunlight, including Earth-reflected illumination and other observation-dependent contributions [Fankhauser et al., 2023, to verify].

These studies motivate the need for physically consistent optical modeling, but their primary emphasis is usually material characterization, brightness prediction, radiometric modeling, or observation interpretation. They do not directly answer how scalar OCS signatures and resolved photometric images behave when both are generated from the same geometry, material assignment, BRDF, attitude convention, and self-occlusion assumptions. The present work builds on this BRDF-based photometric modeling line, but uses it as a common forward-model foundation for a controlled OCS-image attitude inversion benchmark rather than as an end point for brightness prediction alone.

### 2.2 Light-curve and OCS-based attitude inversion

Light curves and OCS-like scalar photometric signatures are attractive for attitude inference because they are compact, interpretable, and can be obtained across multiple observation geometries. Laboratory-tested photometry datasets and simulated photometric signatures have been used to investigate attitude inversion from scalar brightness measurements [Wang et al., 2024, to verify]. Optimization-based approaches, including particle swarm strategies, further demonstrate that light-curve attitude estimation can be formulated as a search problem over attitude states when object shape, reflectance, and illumination geometry are available or assumed [Burton et al., 2024, to verify]. Recent digital-twin and sequential-comparison strategies for LEO uncontrolled objects also support the broader use of light curves for object understanding and attitude-related inference [Kumar et al., 2025, to verify].

The limitation relevant to this paper is not that scalar photometry is unimportant, but that scalar photometric inversion alone cannot reveal how much additional or different information is contained in resolved photometric images. Light-curve studies often focus on photometric sequence matching, optimization, or digital-twin comparison, while the image branch is absent or generated under different assumptions. As a result, they do not isolate when OCS-like measurements and image-based cues are complementary. This work retains the interpretability and multi-geometry advantages of OCS signatures, but places OCS-only inversion in the same benchmark as image-only, late-fusion, and feature-fusion models.

### 2.3 Photometric image simulation and image-based pose estimation

Resolved and rendered images provide spatial cues that scalar signatures cannot preserve, including projected shape, component layout, shadow structure, brightness distribution, and specular patterns. Image-based satellite pose estimation studies have increasingly used synthetic imagery and deep learning to estimate spacecraft pose from resolved ground-based or simulated imagery. Dickinson's 2025 dissertation, for example, addresses 6DOF satellite pose estimation from resolved ground-based imagery using synthetic training and image-quality analysis [Dickinson, 2025, to verify]. Such work highlights both the power of resolved imagery and the difficulty of sim-to-real transfer under blur, noise, illumination variation, and limited image quality.

For the present paper, image-based pose estimation provides an important contrast to scalar OCS inversion. Clean synthetic photometric images may contain strong attitude cues, and a high-capacity image model can exploit these cues effectively. However, this does not mean that clean-image performance is a direct estimate of field performance. Ground-based imagery can be affected by atmospheric seeing, tracking error, sensor noise, optical blur, low resolution, background contamination, and phase-angle changes. Existing image-pose studies therefore motivate the need to separate idealized image upper-bound behavior from degraded-observation robustness. The present work follows this distinction by treating clean rendered images as a controlled upper-bound setting and by explicitly evaluating image degradation sensitivity.

### 2.4 Multi-modal fusion and robustness under observation degradation

Multi-modal fusion is often motivated by the possibility that different sensors or feature streams fail under different conditions. In spacecraft attitude estimation, tightly coupled visual-inertial methods illustrate how feature-level fusion can use raw visual and inertial information to improve robustness compared with more loosely coupled designs [Liu et al., 2024, to verify]. This literature supports the general idea that fusion should be evaluated not only by mean accuracy but also by robustness, failure modes, and the information carried by each modality.

However, visual-inertial fusion is not the same problem as OCS-image photometric fusion. The latter combines a low-dimensional scalar photometric constraint with a resolved photometric image generated by the same scattering physics. Existing fusion studies do not directly answer when OCS and images are complementary under a shared BRDF, geometry, material, attitude, and self-occlusion model. The present work is therefore positioned as a controlled simulation benchmark rather than a claim of field-validated performance. Its comparison focuses on modality information and robustness, not on declaring a universally superior sensor or fusion architecture.

**Table 1. Related work positioning and scope comparison.**

| Work | Geometry | BRDF | Self-occlusion | Image | OCS/light curve | Attitude inversion | Fusion | External validation |
|---|---|---|---|---|---|---|---|---|
| Yang et al. 2024/2025 Photonics `[to verify]` | Material samples / satellite material surfaces `[to verify]` | Semi-empirical pBRDF / Cook-Torrance-related models `[to verify]` | Not central `[to verify]` | No resolved attitude image branch | Reflectance characterization, not OCS inversion | No attitude inversion benchmark | No | Laboratory/material measurement `[to verify]` |
| Lu/Yao 2024 Universe `[to verify]` | LEO constellation satellite / Starlink model | BRDF-based photometric model | Observation geometry considered; detailed self-occlusion `[to verify]` | No resolved inversion image branch | Massive photometric observations / brightness modeling | Not primarily attitude inversion | No | Real photometric observations |
| Wang et al. 2024 ASR `[to verify]` | Space debris / lab photometry target `[to verify]` | Reflectance assumptions `[to verify]` | `[to verify]` | No resolved image branch | Laboratory-tested photometry dataset | Yes, photometry-based attitude inversion | No | Laboratory photometry dataset |
| Burton et al. 2024 ASR `[to verify]` | Known object model / space debris or satellite `[to verify]` | Reflective properties assumed | `[to verify]` | No | Light curve | Yes, particle-swarm attitude estimation | No | Simulation / light-curve experiments `[to verify]` |
| Dickinson 2025 RIT PhD `[to verify]` | CAD/satellite models; resolved ground-based imagery | Image simulation `[to verify]` | Included through rendering/simulation `[to verify]` | Yes, resolved imagery | No OCS/light-curve branch | Yes, 6DOF image-based pose estimation | No OCS-image fusion | Synthetic training and resolved imagery evaluation `[to verify]` |
| Kumar et al. 2025 Acta Astronautica `[to verify]` | Digital twin / LEO uncontrolled objects `[to verify]` | Light-curve modeling assumptions `[to verify]` | `[to verify]` | No resolved image branch | Light curves / sequential comparison | Attitude/object understanding `[to verify]` | No | Observation/digital-twin comparison `[to verify]` |
| Liu et al. 2024 Remote Sensing `[to verify]` | Spacecraft attitude estimation setting | Not BRDF-based | Not relevant | Visual/star-sensor features `[to verify]` | No OCS/light curve | Yes, spacecraft attitude estimation | Visual-inertial tightly coupled fusion | Simulation and experimental evaluations `[to verify]` |
| Fankhauser et al. 2023 AJ `[to verify]` | Satellite brightness geometry | Radiometric brightness model; sunlight and earthshine `[to verify]` | Not attitude-inversion focus | No resolved inversion image branch | Brightness modeling | No attitude inversion benchmark | No | Radiometric/astronomical analysis `[to verify]` |
| This work | Real satellite STL; yaw-pitch under fixed roll | GGX/Cook-Torrance; nonuniform materials | Analytical ray-based self-occlusion | Yes, rendered photometric images | Yes, multi-geometry OCS signatures | Yes, controlled OCS/image/fusion yaw-pitch inversion | Late fusion and feature fusion | No real optical validation; analytical/rendering consistency and controlled sensitivity tests |

## 3. Method

### 3.1 Overview of the unified OCS-image simulation framework

We formulate the proposed study as a physically consistent simulation and controlled inversion benchmark for space object attitude estimation. The objective is to estimate yaw and pitch from two optical modalities: scalar OCS signatures and resolved photometric images. Both modalities are generated from the same object geometry, attitude definition, material assignment, BRDF model, illumination direction, viewing direction, and self-occlusion assumptions. This design allows the subsequent inversion experiments to compare modality information under controlled conditions rather than under mismatched forward models.

The pipeline consists of four stages. First, a real satellite STL model is converted into a facet-level representation with component labels and nonuniform material parameters. Second, each yaw-pitch attitude and observation geometry defines the orientation of the object relative to the illumination and detector directions. Third, a GGX/Cook-Torrance BRDF and an analytical visibility model are used to generate multi-geometry OCS signatures and clean rendered photometric images. Fourth, OCS-only, image-only, late-fusion, and feature-fusion models are trained and evaluated as controlled probes of the information carried by each modality. The benchmark is simulation-focused: real optical telescope images are not used, and atmosphere, detector response, optical PSF, earthshine, and background contamination are not explicitly modeled.

**Fig. 1 caption intent.** Unified OCS-image simulation and inversion pipeline. The figure should show the path from real STL geometry, component segmentation, nonuniform material assignment, yaw-pitch attitude grid, observation geometry, GGX/Cook-Torrance BRDF, and self-occlusion to paired OCS signatures and clean photometric images, followed by OCS-only, image-only, late-fusion, and feature-fusion inversion models.

### 3.2 Satellite geometry and attitude parameterization

The geometric input is a real satellite STL model consisting of three component groups: a metal body, a solar panel, and a baffle or shade component. The model is represented as triangular facets, each with an area, a surface normal, a component label, and a material assignment. This facet-level representation is required for OCS integration because scalar OCS is computed as a surface integral over illuminated and visible facets.

The attitude state in the present benchmark is parameterized by yaw and pitch, while roll is fixed. The main attitude grid uses a 5 deg resolution with 73 yaw samples and 37 pitch samples, giving 2701 yaw-pitch attitudes. A coarser 10 deg grid is used for training in the interpolation split, while the remaining 5 deg intermediate attitudes are used for testing. This split is designed to evaluate interpolation over attitude space rather than direct memorization of all 5 deg grid points. The exact Euler order and matrix convention should be reported in the final manuscript as `[需要作者确认：Euler order / rotation matrix convention]`.

The present setting should be interpreted as a controlled yaw-pitch benchmark, not as a full three-degree-of-freedom pose-estimation system. This limitation is intentional: the goal is to isolate the information provided by OCS signatures, photometric images, and their fusion under a defined attitude parameterization.

### 3.3 Observation geometry and data generation protocol

For OCS generation, five sun-sensor geometries are used for each attitude, producing 5 x 2701 = 13,505 attitude-geometry samples. The phase-angle range is approximately 24 deg to 120 deg. These multiple geometries allow the OCS branch to sample attitude-dependent photometric behavior beyond a single scalar response.

For image generation, the main branch uses clean rendered photometric images at 128 x 128 resolution under the phase condition referred to in the project notes as phase63. This design provides a controlled image benchmark aligned with the forward model, but it does not test all possible phase-angle generalization cases. Broader cross-phase image generalization should be treated as a future extension or supplementary sensitivity analysis unless final results are available `[需要作者确认：phase63 fairness and cross-phase values]`.

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
OCS = sum_i A_i f_r(n_i, l, v) max(n_i·l, 0) max(n_i·v, 0) V_i(l) V_i(v),
```

where `A_i` is the area of facet `i`, `f_r` is the GGX/Cook-Torrance BRDF value, `n_i` is the facet normal, `l` and `v` are unit illumination and viewing directions, and `V_i(l)` and `V_i(v)` are binary visibility terms for the illumination and viewing directions. The product of cosine terms enforces local front-facing illumination and observation, while the binary visibility terms account for self-occlusion.

Several OCS feature representations are constructed from this integration. Total OCS features summarize the scalar response for each observation geometry. Per-part OCS features retain component-level contributions from the metal body, solar panel, and baffle/shade. Log-transformed versions are used to reduce dynamic-range imbalance across observation geometries and components. Diagnostic feature variants, such as `all_raw`, may include additional quantities and are therefore treated as semi-oracle upper-bound representations rather than operationally realistic OCS features. In contrast, `per_part_log` is treated as a practical OCS setting for the controlled benchmark.

### 3.7 Photometric image generation

Photometric images are generated from the same geometry, attitude, material assignment, BRDF model, and observation settings used by the OCS pipeline. The main image branch uses clean rendered photometric images at 128 x 128 resolution. These images provide spatial cues such as silhouette, component layout, shadowing, and brightness distribution, which are not preserved by scalar OCS signatures.

The rendered images are not intended to reproduce field telescope images. Instead, they define an idealized and controlled image-based upper-bound setting. Atmosphere, detector response, optical PSF, earthshine, background contamination, and other real-observation effects are not explicitly modeled. The main image branch uses one rendered photometric phase condition, phase63. Broader cross-phase image generalization is outside the primary scope of the present benchmark.

### 3.8 Attitude inversion models

The inversion models are used to probe modality information under controlled conditions. Each model predicts yaw-pitch attitude from either OCS features, photometric images, or both. To handle angular periodicity, the target can be encoded using a periodic representation such as sine and cosine components for yaw and pitch `[需要作者确认：exact target encoding]`.

The OCS-only model maps OCS feature vectors to yaw-pitch attitude predictions using a multilayer perceptron. This model tests how much attitude information is carried by low-dimensional scalar photometric signatures. The `all_raw` 45-dimensional representation is treated as a semi-oracle upper bound because it includes additional diagnostic quantities; it should not be interpreted as a fully realistic field-observation feature. The `per_part_log` representation is used as a more practical OCS feature setting.

The image-only models map a single-channel 128 x 128 photometric image to a yaw-pitch attitude prediction. A TinyCNN is used as a lightweight image baseline, while ResNet-18 is used as a stronger image model for clean synthetic upper-bound evaluation. TinyCNN should not be used to characterize the upper limit of image-based inversion, because stronger image models can exploit clean rendered image cues more effectively. Conversely, ResNet-18 performance on clean rendered images should be interpreted as an idealized upper bound, not as a real telescope performance estimate.

Late fusion combines independently produced OCS and image predictions at the prediction level. Fusion is performed in a periodic yaw-pitch representation, and a weighting or beta sweep explores the tradeoff between prediction sources. Feature fusion uses a two-branch architecture consisting of an image branch, an OCS branch, and a fusion head. The image branch extracts features from the rendered photometric image, while the OCS branch embeds the OCS feature vector. The concatenated feature representation is then mapped to the yaw-pitch target representation. Both late fusion and feature fusion are benchmark strategies for evaluating conditional complementarity, not claims that a single fusion design is universally best.

### 3.9 Data splits and evaluation metrics

The evaluation uses a 10 deg -> 5 deg attitude split. Attitudes on the coarser 10 deg grid form the training pool, while the remaining attitudes on the 5 deg grid form the test set. This split is stricter than a simple random split because the model must infer intermediate attitude states that were not directly included in the training grid. Neural models are evaluated across multiple random seeds where applicable.

Performance is measured using angular error in degrees, mean angular error, standard deviation across seeds where applicable, Hit@5, Hit@10, P90, and worst-case error. The angular-error computation should account for yaw periodicity and pitch geometry; the final paper should report the exact formula as `[需要作者确认：angular error formula]`. These metrics are used to compare OCS-only, image-only, and fusion models in terms of average accuracy, threshold success rate, and tail behavior.

## 4. Results

### 4.1 Forward-model validation and OCS signature analysis

The unified forward model provides a physically consistent basis for comparing scalar OCS signatures and rendered photometric images. The benchmark uses a real satellite STL geometry with three component groups: metal body, solar panel, and baffle/shade. These components are assigned nonuniform GGX/Cook-Torrance material settings, and the same attitude definition, illumination direction, viewing direction, BRDF, and visibility assumptions are used to generate both OCS signatures and photometric images. The main yaw-pitch grid contains 73 yaw samples and 37 pitch samples, resulting in 2701 attitudes. For the OCS branch, five sun-sensor geometries are used, producing 13,505 attitude-geometry samples across a phase-angle range of approximately 24 deg to 120 deg.

Before evaluating attitude inversion, we checked the numerical consistency and visibility behavior of the forward model. Simple-geometry tests, including single-plate and cube-like closure cases, showed sub-percent agreement between analytical or facet-level OCS calculations and rendering-derived checks. Self-occlusion behavior was evaluated using synthetic single-plate, double-plate, U-block, and nested-cylinder cases, together with sampled Blender/manual ray-cast review. These checks support the use of the analytical ray-based visibility model for controlled OCS simulation. They should not be interpreted as real optical validation, but they reduce the risk that the inversion results are driven by obvious geometric or visibility implementation artifacts.

The OCS scans further show that attitude-dependent optical signatures are strongly affected by both observation geometry and self-occlusion. Across the five observation geometries, occlusion rates fall roughly in the 60% to 78.5% range, indicating that visibility is not a minor correction for this nonconvex three-component target. The resulting OCS maps and component-level contribution maps are therefore important not only as input features for inversion but also as observability diagnostics.

**Fig. 3 caption intent.** OCS maps and occlusion diagnostics. The figure should include yaw-pitch OCS heatmaps, part-level contribution maps, and occlusion-rate maps to show that scalar photometric signatures are attitude-dependent and visibility-sensitive.

### 4.2 OCS-only attitude inversion and multi-geometry photometric constraints

OCS-only inversion demonstrates that low-dimensional photometric signatures can provide useful yaw-pitch attitude constraints when multi-geometry and component-level information is retained. The practical `per_part_log` OCS representation reaches a mean angular error of 5.91 +/- 0.22 deg, with Hit@5 = 73.8% and Hit@10 = 94.3%. This result indicates that component-resolved OCS signatures encode substantially more attitude information than a single scalar total-brightness response.

The importance of feature design is visible across OCS variants. The `total_log` feature gives a much weaker result, with 36.69 +/- 3.6 deg mean error, Hit@5 = 9.7%, and Hit@10 = 23.5%. This weak baseline suggests that total OCS alone is often insufficient for precise yaw-pitch inversion in the tested setting. In contrast, the `all_raw` 45D representation reaches 3.98 +/- 0.60 deg, Hit@5 = 90.7%, and Hit@10 = 97.1%. However, this representation includes additional diagnostic quantities and is therefore treated as a semi-oracle upper bound rather than a practical observation setting.

The OCS-only results support two conclusions. First, OCS is not inherently weak: when multi-geometry and component-level information is available, it provides a robust and interpretable photometric constraint. Second, not every OCS representation has the same operational meaning. In the remaining Results, `per_part_log` is emphasized as the practical OCS-only setting, while `all_raw` is reported only as a diagnostic upper bound.

### 4.3 Image-only inversion: from TinyCNN to ResNet clean-image upper bound

Image-only inversion shows that clean rendered photometric images can provide highly informative attitude cues when model capacity is sufficient. The lightweight TinyCNN baseline reaches 12.38 +/- 0.74 deg mean error and Hit@5 = 26.1% on clean phase63 128 x 128 images. This result is useful as a lightweight baseline, but it should not be used to characterize the upper bound of image-based inversion.

When the image branch is evaluated with ResNet-18, the clean-image result improves to 1.69 +/- 0.07 deg mean error, Hit@5 = 97.6%, and Hit@10 = 99.9%. This establishes clean rendered photometric images as a strong upper-bound condition for image-based attitude inversion in the controlled benchmark. The result should be interpreted carefully: the rendered images are clean, aligned with the simulation distribution, and do not include atmosphere, optical PSF, detector response, earthshine, or background contamination. Therefore, this result is not a field-performance estimate for real telescope images.

We also audited the dataset structure to reduce the likelihood that the strong ResNet result is caused by trivial leakage. The train/test split follows the 10 deg -> 5 deg protocol, so test attitudes are not simply repeated training grid points. File names and labels are aligned, and normalization uses fixed constants rather than test-set statistics. The target centroid displacement has a correlation with yaw (r = 0.66), which is a physical rendering cue under the controlled camera setup, but this cue may not transfer to field observations where tracking and centering procedures can change the image-position distribution. Mean intensity is nearly uncorrelated with attitude (r < 0.02), reducing the concern that the network is using a simple brightness proxy for angle.

### 4.4 OCS-image fusion under clean images

Fusion under clean rendered images provides modest but meaningful gains when OCS is combined with a strong image model. The ResNet image-only baseline reaches 1.69 +/- 0.07 deg mean error, P90 = 3.31 deg, worst-case error = 9.9 deg, and Hit@5 = 97.6%. Adding concat5 `per_part_log` OCS features improves the result to 1.47 +/- 0.07 deg, P90 = 2.71 deg, worst-case error = 6.6 deg, and Hit@5 = 99.7%. In relative terms, the mean error decreases by 0.22 deg, and the worst-case error decreases by about one third.

This improvement should be described as conditional complementarity rather than fusion dominance. The clean image branch is already very strong, so the remaining mean-error margin is small. The main value of OCS in this setting is not to replace the image branch, but to improve tail behavior and provide an additional physical constraint. The comparison between fusion variants supports this interpretation. Using only phase63 `per_part_log` OCS features gives 1.61 +/- 0.07 deg, P90 = 2.97 deg, worst-case = 7.4 deg, and Hit@5 = 99.2%. In contrast, ResNet + concat5 `all_raw` reaches 1.49 +/- 0.10 deg but has a worse worst-case error of 18.7 deg, despite using a stronger semi-oracle OCS representation. Thus, a stronger OCS representation does not automatically produce better fusion tail behavior.

Earlier TinyCNN/OCS fusion experiments provide an additional diagnostic view of conditional complementarity. When OCS information is very strong (`all_raw`), adding a weaker image branch can hurt, with feature fusion reaching 5.42 deg compared with 3.98 deg for OCS-only. When OCS information is at an intermediate level (`per_part_log`), feature fusion improves from 5.91 deg for OCS-only and 12.38 deg for CNN-only to 4.10 +/- 0.77 deg. When OCS is weak (`total_log`), the image branch dominates, and late fusion reaches 11.99 deg compared with 36.69 deg for OCS-only. These trends indicate that fusion benefit depends on the information balance between modalities. In an earlier TinyCNN/OCS diagnostic, the error correlation between OCS and CNN was r = 0.003, suggesting complementary failure modes; this diagnostic should not be reported as a ResNet-pair correlation unless a corresponding ResNet analysis is performed.

**Table 2. Main inversion benchmark.**

| Method / feature | Input | Mean error (deg) ↓ | Hit@5 ↑ | Hit@10 ↑ | Role |
|---|---|---:|---:|---:|---|
| OCS MLP all_raw 45D | Multi-geometry OCS + diagnostic quantities | 3.98 +/- 0.60 | 90.7% | 97.1% | Semi-oracle OCS upper bound |
| OCS MLP per_part_log 30D | Practical component-level OCS | 5.91 +/- 0.22 | 73.8% | 94.3% | Practical OCS-only setting |
| OCS MLP total_log 15D | Total OCS only | 36.69 +/- 3.6 | 9.7% | 23.5% | Weak OCS baseline |
| Weighted kNN all_raw | OCS feature baseline | 21.84 | 47.9% | `[需要作者确认]` | Classical / low-capacity baseline |
| TinyCNN image-only | phase63 128 x 128 clean image | 12.38 +/- 0.74 | 26.1% | 55.8% | Lightweight image baseline |
| ResNet-18 image-only | phase63 128 x 128 clean image | 1.69 +/- 0.07 | 97.6% | 99.9% | Clean-image upper bound |

**Table 3. ResNet fusion under clean rendered images.**

| Case | Model / input | Mean +/- std (deg) ↓ | P90 (deg) ↓ | Worst (deg) ↓ | Hit@5 ↑ | Hit@10 ↑ | Interpretation |
|---|---|---:|---:|---:|---:|---:|---|
| A1 | ResNet image-only | 1.69 +/- 0.07 | 3.31 | 9.9 | 97.6% | 99.9% | Clean-image upper bound |
| A2 | ResNet + concat5 per_part_log 30D | 1.47 +/- 0.07 | 2.71 | 6.6 | 99.7% | 100% | Best clean fusion setting |
| A3 | ResNet + phase63 per_part_log 6D | 1.61 +/- 0.07 | 2.97 | 7.4 | 99.2% | 100% | Single-phase OCS fairness check |
| A4 | ResNet + concat5 all_raw 45D | 1.49 +/- 0.10 | 2.70 | 18.7 | 99.2% | 99.9% | Semi-oracle OCS does not guarantee tail robustness |

### 4.5 Robustness under controlled observation degradation

The clean-image upper bound is fragile under additive image noise. With no added noise, ResNet-18 reaches 1.69 deg and Hit@5 = 97.6%. Under Gaussian image noise with sigma = 0.01, performance degrades to 85.85 +/- 3.00 deg and Hit@5 = 2.2%. Increasing the noise level to sigma = 0.03, 0.05, and 0.10 gives similarly poor mean errors of 85.49 deg, 85.97 deg, and 87.92 deg, with Hit@5 decreasing to 1.5%, 1.2%, and 1.0%, respectively. These results show that the clean ResNet result depends strongly on image quality and distribution consistency.

Brightness scaling is less destructive than additive Gaussian noise in the tested setting. Scaling brightness by 0.50 gives 3.45 deg and Hit@5 = 78.7%, while scaling brightness by 0.75, 1.25, and 1.50 gives 2.03 deg, 1.77 deg, and 2.00 deg, respectively. This contrast suggests that the ResNet branch is more sensitive to pixel-level stochastic corruption than to global intensity scaling in the controlled images. However, neither Gaussian noise nor brightness scaling should be treated as a complete model of real atmospheric or detector degradation. They are controlled observation-quality stress tests.

OCS provides a complementary robustness perspective because it is independent of image pixels in this benchmark. The practical OCS-only `per_part_log` result of 5.91 deg is not the clean-image accuracy upper bound, but it remains unaffected by image noise. Conversely, when the OCS branch is degraded by synthetic OCS noise while the image branch remains clean, fusion gains become larger. The reported gain increases from +1.97 deg at 0% OCS noise to +3.30 deg at 10% OCS noise and +6.29 deg at 20% OCS noise. At 10% OCS noise, OCS-only reaches 9.99 +/- 0.35 deg while fusion reaches 6.69 +/- 1.34 deg; at 20% OCS noise, OCS-only reaches 17.25 +/- 0.71 deg while fusion reaches 10.96 +/- 2.51 deg. The exact 0% OCS-only and fusion values for this OCS-noise table should be filled as `[需要作者确认：0% OCS noise table values]`.

Together, the degradation experiments support the central claim that fusion is conditional. Clean images can be extremely accurate, but their performance is vulnerable to image corruption. OCS is not the accuracy upper bound under clean image conditions, but it provides an interpretable photometric constraint independent of image-pixel degradation. Fusion becomes most valuable when one modality is weakened and the other retains complementary information.

**Fig. 5 caption intent.** Image degradation robustness. The figure should compare clean ResNet image-only performance with Gaussian noise and brightness-scaling stress tests, emphasizing that the noise tests are controlled degradations rather than a full atmosphere/sensor model.

**Fig. 6 caption intent.** OCS noise and fusion gain. The figure should show how fusion gain increases from 0% to 20% OCS noise, while marking the missing 0% table values for author confirmation.

**Table 4. Robustness and controlled degradation summary.**

| Setting | Model / modality | Mean error (deg) ↓ | Hit@5 ↑ | Interpretation |
|---|---|---:|---:|---|
| Clean image | ResNet image-only | 1.69 | 97.6% | Idealized clean-image upper bound |
| Gaussian noise sigma=0.01 | ResNet image-only | 85.85 +/- 3.00 | 2.2% | Severe image-noise fragility |
| Gaussian noise sigma=0.03 | ResNet image-only | 85.49 | 1.5% | Still collapsed |
| Gaussian noise sigma=0.05 | ResNet image-only | 85.97 | 1.2% | Still collapsed |
| Gaussian noise sigma=0.10 | ResNet image-only | 87.92 | 1.0% | Still collapsed |
| Brightness x0.50 | ResNet image-only | 3.45 | 78.7% | Less destructive than additive noise |
| Brightness x0.75 | ResNet image-only | 2.03 | 94.8% | Mostly robust |
| Brightness x1.25 | ResNet image-only | 1.77 | 97.5% | Mostly robust |
| Brightness x1.50 | ResNet image-only | 2.00 | 95.8% | Mostly robust |
| OCS noise 0% | OCS / fusion | `[需要作者确认]` | `[需要作者确认]` | Fusion gain +1.97 deg |
| OCS noise 10% | OCS-only -> fusion | 9.99 +/- 0.35 -> 6.69 +/- 1.34 | `[需要作者确认]` | Fusion gain +3.30 deg |
| OCS noise 20% | OCS-only -> fusion | 17.25 +/- 0.71 -> 10.96 +/- 2.51 | `[需要作者确认]` | Fusion gain +6.29 deg |

### 4.6 Ablation and sensitivity analysis

Several additional checks support the interpretation of the benchmark and define its limits. The 10 deg -> 5 deg split is designed to test interpolation over attitude space rather than direct memorization of all 5 deg grid states. Random split, phase63 fairness, BRDF sensitivity, occlusion ablation, and roll sensitivity should be reported as supporting analyses where finalized values are available `[需要作者确认：which ablations have final numbers for main text]`.

Self-occlusion sensitivity supports the chosen visibility settings. The benchmark uses `epsilon = 1.0 mm` and `min_hit_distance = 1.0 mm`, selected from synthetic-geometry validation and sensitivity scans on the real three-component model. This setting suppresses self-intersection in single-plate tests and retains cross-part and internal occlusion in double-plate, U-block, and nested-cylinder tests. In the main satellite scans, occlusion rates of roughly 60% to 78.5% across observation geometries show that self-occlusion is substantial and should not be ignored.

The remaining limitations should be interpreted as study boundaries rather than hidden claims. The current benchmark estimates yaw and pitch under fixed roll. The main image branch uses phase63 clean rendered images, and broader cross-phase image generalization is not treated as a primary result. Material parameters are nominal rather than target-calibrated. These choices make the benchmark controlled and interpretable, but they also define the scope of the reported Results.

**Fig. 7 caption intent.** Sensitivity and ablation summary. The figure should summarize BRDF, occlusion, roll, split, and phase-condition sensitivity only where final values are available; otherwise, the unavailable items should remain in the author-confirmation list rather than being plotted.

## 5. Discussion

### 5.1 Main finding: controlled complementarity between OCS and photometric images

The main finding of this study is that scalar OCS signatures and resolved photometric images provide different attitude constraints when they are generated from the same BRDF-driven physical model. The benchmark is not simply a comparison of several neural architectures. Instead, it isolates how two optical modalities behave when geometry, material assignment, attitude convention, BRDF, illumination, viewing geometry, and self-occlusion are held consistent. Within this controlled setting, clean photometric images define a strong image-based upper-bound case, while OCS provides a low-dimensional and interpretable photometric constraint that remains independent of image-pixel degradation.

This framing changes the interpretation of multi-modal fusion. Fusion should not be understood as a universal accuracy maximizer. Its value depends on the information content and degradation state of each modality. When a clean resolved image contains strong spatial cues, the image branch can dominate mean accuracy. When image quality degrades or when OCS and image errors occur on different samples, the additional OCS constraint can improve reliability and reduce tail errors. The results therefore support conditional complementarity rather than a fixed hierarchy between OCS, images, and fusion.

### 5.2 Why clean rendered images give a strong image-only upper bound

The strong ResNet-18 image-only result is understandable because the clean rendered images preserve stable visual cues that are tightly linked to yaw-pitch attitude. These cues include projected shape, shadow structure, component layout, centroid displacement, brightness distribution, and specular patterns. A higher-capacity CNN can exploit these cues more effectively than a lightweight TinyCNN, which explains the large difference between the TinyCNN baseline and the ResNet-18 clean-image result.

However, this result should be interpreted as an optimistic upper-bound case for image-based inversion under idealized rendered photometric images. The images do not include atmosphere, detector response, optical PSF, earthshine, background contamination, tracking errors, or real calibration uncertainty. The degradation experiments support this boundary: under 1% Gaussian image noise, ResNet performance collapses from the clean-image upper-bound regime to a mean error above 85 deg with Hit@5 near 2%. This does not mean image-based inversion is inherently unreliable; rather, it shows that clean synthetic image performance must be separated from degraded-observation robustness.

The brightness-scaling tests further clarify the type of fragility observed in this benchmark. Global brightness changes are less destructive than additive Gaussian noise, suggesting that the ResNet branch is not relying only on absolute intensity. Instead, pixel-level stochastic corruption disrupts the spatial and photometric cues used by the image model. These tests are controlled stress tests, not complete atmosphere or detector models, but they demonstrate why clean-image accuracy should not be reported as expected field performance.

### 5.3 Why OCS remains useful despite lower clean-image accuracy

OCS is not the accuracy upper bound when clean resolved images are available. The practical `per_part_log` OCS-only setting is less accurate than ResNet-18 under clean rendered images. Its value lies elsewhere: OCS is low-dimensional, physically interpretable, available across multiple observation geometries, and independent of image pixels in this benchmark. These properties make it a useful complementary constraint when high-quality resolved images are unavailable, degraded, or operationally expensive.

The distinction between practical and diagnostic OCS features is important. The `per_part_log` representation provides a practical OCS-only setting, whereas the `all_raw` 45D representation should be interpreted as a semi-oracle diagnostic upper bound because it includes additional quantities beyond a straightforward operational OCS feature. Presenting both results is useful: the practical feature shows what component-level OCS can support, while the semi-oracle setting indicates the information potential when richer diagnostic quantities are available. It would be misleading, however, to treat `all_raw` as the main operational OCS result.

OCS robustness should also be stated carefully. In this benchmark, OCS is unaffected by image-pixel degradation because it is generated and used as a separate scalar photometric modality. This does not imply immunity to all real observational errors. Real OCS or light-curve measurements may be affected by photometric calibration error, atmospheric transparency variation, geometry uncertainty, BRDF mismatch, target-model mismatch, and measurement noise. The claim is therefore not that OCS is universally robust, but that it provides a non-image photometric constraint whose failure modes can differ from those of resolved images.

### 5.4 Conditional value of OCS-image fusion

The fusion results show a conditional benefit. In the clean ResNet setting, adding concat5 `per_part_log` OCS improves the mean error from 1.69 deg to 1.47 deg, increases Hit@5 from 97.6% to 99.7%, and reduces the worst-case error from 9.9 deg to 6.6 deg. The mean gain is modest because the clean image branch is already strong, but the tail improvement is important for a task where occasional large errors may be operationally more consequential than small changes in average error.

At the same time, fusion is not automatically improved by using a stronger or richer OCS representation. The ResNet + concat5 `all_raw` case achieves a similar mean error but a worse worst-case error of 18.7 deg. This result is a useful warning: semi-oracle or high-dimensional diagnostic features may improve some aggregate metrics while harming tail behavior. Fusion should therefore be evaluated using mean error, threshold metrics, and tail statistics together, rather than by mean accuracy alone.

The OCS-noise experiments reinforce the conditional nature of fusion. As OCS quality degrades, the gain from fusion increases from +1.97 deg at 0% OCS noise to +3.30 deg at 10% and +6.29 deg at 20%. This pattern suggests that fusion becomes more valuable when one modality weakens and the other retains useful information. The experiment also has a boundary: the image branch remains clean in this OCS-noise setting, so the result should not be interpreted as a complete field-degradation study. It does, however, support the broader conclusion that fusion should be viewed as a reliability mechanism whose benefit depends on modality quality.

### 5.5 Implications for space object attitude inversion

The results suggest several practical principles for future optical attitude-inversion studies. First, clean-image performance should be reported separately from degraded-image performance. A high-capacity image model may achieve very high accuracy under clean synthetic imagery, but this upper-bound setting does not by itself establish field robustness. Second, scalar photometric constraints such as OCS should not be evaluated only by whether they outperform clean images. Their value includes interpretability, low dimensionality, multi-geometry availability, and different failure modes.

Third, fusion should be evaluated through tail metrics and robustness tests, not only through mean error. The improvement from 9.9 deg to 6.6 deg in the clean fusion setting and the increasing fusion gain under OCS noise indicate that fusion can be useful even when mean improvements are modest. For operational use, Hit@5, Hit@10, P90, and worst-case behavior may be as important as average error.

Finally, a unified forward model is essential for interpreting modality comparisons. If OCS and images are generated using different geometry, material, BRDF, or visibility assumptions, it is difficult to attribute performance differences to modality information. The proposed benchmark therefore provides a controlled way to study modality complementarity before moving to field observations. It should be seen as a step toward, not a substitute for, real optical validation.

### 5.6 Scope and limitations

The present study has several scope limitations. It does not use real optical telescope images with known attitude ground truth. The clean rendered images are idealized photometric images and exclude atmosphere, detector response, optical PSF, earthshine, background contamination, and tracking errors. As a result, the ResNet-18 image result should be interpreted as a clean-image upper bound rather than expected field performance.

The attitude task is also bounded. The benchmark estimates yaw and pitch under fixed roll and does not claim full 3-DOF pose recovery. The main image branch uses one rendered phase condition, so broader cross-phase image generalization remains to be tested. Material parameters are nominal rather than calibrated for the specific target, and further BRDF sensitivity analysis and material validation are needed for stronger physical claims.

The robustness results are controlled stress tests rather than comprehensive observation models. Gaussian image noise and brightness scaling do not fully represent atmospheric turbulence, tracking error, detector response, or telescope optics. Similarly, OCS independence from image-pixel degradation in this benchmark does not mean that real OCS measurements are immune to photometric or geometric uncertainty. These limitations define the boundary of the present controlled study and motivate future work on calibrated material parameters, real optical datasets, cross-phase imagery, full roll variation, and more realistic sensor/atmosphere models.

## 6. Conclusion

This paper presented a unified BRDF-driven simulation and controlled inversion benchmark for space object yaw-pitch attitude estimation from OCS signatures and photometric images. By generating both modalities from the same STL geometry, nonuniform material assignment, GGX/Cook-Torrance BRDF, attitude definition, and self-occlusion model, the study isolates how scalar photometric signatures and resolved images contribute to attitude inversion under consistent physical assumptions.

The results show that clean rendered photometric images provide a strong upper-bound case for image-based inversion, with ResNet-18 reaching 1.69 +/- 0.07 deg under idealized imagery. However, the same image-only setting is highly fragile under additive image noise, degrading to 85.85 +/- 3.00 deg under 1% Gaussian noise. OCS does not define the clean-image accuracy upper bound, but the practical `per_part_log` OCS setting provides an interpretable photometric constraint, and OCS-image fusion improves selected clean-image tail errors from 9.9 deg to 6.6 deg. Fusion gains also increase under controlled OCS degradation, supporting the interpretation of fusion as conditional complementarity rather than universal superiority.

The current study does not include real optical telescope validation and is limited to yaw-pitch inversion under fixed roll with clean rendered images and nominal material parameters. Future work should extend the benchmark to calibrated materials, broader phase and roll conditions, explicit atmosphere and sensor modeling, and real optical observations with reliable attitude ground truth.

## Data Availability

Data availability will be specified in the final submission. `[需要作者确认：whether simulation data, STL-derived products, trained models, and scripts can be shared; repository or access statement]`

## Author Contributions

Author contributions will be completed before submission according to the target journal format. `[需要作者确认：author list and CRediT roles]`

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

## B. Cross-section Consistency Checklist

| Check item | Status | Notes |
|---|---|---|
| Title / abstract / contribution are aligned | Pass | All emphasize BRDF-driven OCS-image simulation, controlled inversion, and conditional complementarity. |
| `OCS`, `photometric images`, and `fusion` terminology is consistent | Pass | OCS is scalar photometric constraint; photometric images are clean rendered images unless otherwise stated; fusion is conditional. |
| `all_raw` is always semi-oracle | Pass | It is described as diagnostic/semi-oracle, not the practical field setting. |
| `per_part_log` is the practical OCS setting | Pass | It is used as the practical component-level OCS representation. |
| Clean image is always upper-bound | Pass | ResNet clean result is described as idealized clean rendered upper bound, not field performance. |
| No real telescope validation is clear | Pass | Stated in Abstract, Introduction, Method, Discussion, Conclusion, and Limitations. |
| Fixed roll / phase63 / nominal materials limitations are consistent | Pass | These are stated as benchmark boundaries. |
| `r = 0.003` is limited to TinyCNN/OCS diagnostic | Pass | It is explicitly labeled as an earlier TinyCNN/OCS diagnostic, not a ResNet-pair result. |
| Gaussian noise is controlled stress test | Pass | It is not presented as full realistic atmosphere/sensor degradation. |
| Numerical conflicts | Needs author audit | No internal conflict found in this integration, but 0% OCS-noise values and some ablations remain missing. |

## C. Author Confirmation List

1. Final target journal priority: Acta Astronautica, Advances in Space Research, Optics Express, Remote Sensing, or another journal.
2. Final title choice: keep the current BRDF-driven title or switch to a title emphasizing conditional complementarity.
3. Euler rotation convention and coordinate definitions, including yaw/pitch/roll axes and rotation order.
4. Angular error formula, including yaw periodicity and pitch handling.
5. Target encoding for neural models, especially whether yaw/pitch use sin-cos outputs.
6. 0% OCS-noise table values for OCS-only, fusion, Hit@5, and any seed statistics.
7. Which BRDF sensitivity, occlusion ablation, roll sensitivity, random split, and phase63 fairness results are final enough for main text.
8. Whether ResNet-fusion image-degradation results exist; if not, keep this as future work rather than Results.
9. Exact OCS feature units, normalization, and operational interpretation.
10. Training details to report in Method or Supplementary: epochs, batch size, learning rate, seeds, early stopping, hardware.
11. Table 1 bibliographic metadata and claims marked `[to verify]`.
12. Whether Dickinson 2025 PhD should remain in Table 1 or be replaced by a conference/journal source.
13. Whether Limitations should remain as Discussion 5.6 or become a separate standalone section depending on the journal.
14. Data availability policy: share generated OCS/images/models/scripts or provide access on request.
15. Author contribution and conflict-of-interest wording.

## D. Revision Priority List

### Must fix before internal review

1. Confirm angular error formula, Euler convention, and target encoding.
2. Fill or remove 0% OCS-noise table values.
3. Verify all Table 1 references and replace `[to verify]` placeholders with accurate metadata.
4. Decide which sensitivity/ablation values can enter main text and which should remain future work.
5. Check all numerical values against the original experiment logs.
6. Ensure the manuscript never implies real telescope validation or field performance.

### Should fix before journal submission

1. Convert figure caption intents into final figure captions after figures are made.
2. Decide whether Table 1 belongs in the main text or supplementary material.
3. Add a compact reproducibility paragraph or supplementary table for model hyperparameters.
4. Add citation support for optical degradation, BRDF satellite photometry, light-curve inversion, and image-based pose estimation.
5. Polish Abstract and Introduction after final journal target is chosen.
6. Align terminology with the target journal: "attitude inversion", "pose estimation", "OCS", and "photometric image".

### Optional strengthening

1. Add ResNet-pair OCS-image error correlation if results are available.
2. Add ResNet-fusion robustness under image degradation if already tested or feasible.
3. Add cross-phase or additional phase-condition results if available.
4. Add material-parameter sensitivity plots if the values are final.
5. Add an explicit field-validation roadmap figure or short paragraph in Discussion if the target journal values operational implications.

## E. Self-review Checklist

| Self-review item | Result |
|---|---|
| Did this draft add experiments or numerical values not provided by prior steps? | No. |
| Did this draft add unverified citations as if they were final? | No; placeholders and `[to verify]` are retained. |
| Did it write clean-image results as field performance? | No; clean images are consistently upper-bound controlled imagery. |
| Did it overstate fusion? | No; fusion is consistently conditional complementarity. |
| Did it overstate OCS? | No; OCS is useful and robust in the benchmark, not universally better than clean images. |
| Did it weaken or hide the lack of real optical validation? | No; it is explicit across the manuscript. |
| Did it mix reviewer-facing defenses into the formal manuscript text? | Mostly no; interpretation is integrated, while confirmation lists are separated after the manuscript. |
| Did it preserve author-confirmation items? | Yes; uncertain methods, citations, and missing values remain marked. |
| Did it keep ISAR out of the main manuscript line? | Yes. |
| Does the draft avoid mechanical pasting? | Yes; repeated stage content is compressed and organized into a continuous manuscript. |

