# GPT Candidate v0.2 Acta/ASR Manuscript

Source basis: `最终整合版_v0.1_基于GPT吸收Claude.md`, plus Codex-reviewed integration lists 07, 07b, and 07c.

Status: GPT-side candidate material only. This file must be reviewed against the Claude candidate and the original experiment logs before it is integrated into `manuscript_md/主稿_v0.2_Acta_ASR主投优先版.md`.

---

## A. Candidate Manuscript Draft

# BRDF-Driven OCS and Photometric Image Simulation for Controlled Space Object Attitude Inversion

## Abstract

Accurate attitude estimation of non-cooperative space objects from optical observations is limited by the different information carried by scalar photometric signatures and resolved images, and by the sensitivity of image-based models to observation quality. We develop a unified BRDF-driven simulation benchmark that generates optical cross section (OCS) signatures and photometric images from the same satellite STL geometry, nonuniform material assignment, GGX/Cook-Torrance reflectance model, self-occlusion treatment, observation geometry, and yaw-pitch attitude grid. This paired setting enables controlled comparison of OCS-only, image-only, late-fusion, and feature-fusion attitude inversion models. Under clean rendered images, a ResNet image-only model reaches 1.69 +/- 0.07 deg mean angular error with Hit@5 = 97.6%, while ResNet feature fusion with concat5 `per_part_log` OCS improves the clean result to 1.47 +/- 0.07 deg. However, clean-trained image and fusion models are not robust by default: image-only performance collapses under 1% Gaussian image noise, and a clean-trained feature-fusion model degrades to about 73 deg under the same noise level. A degradation-aware fusion model (U1) restores stable mean and tail behavior under the tested synthetic degradations, reaching 1.95 deg on clean images and 2.31 deg under noise sigma=0.10, while image-only training with the same augmentation remains worse at 9.55 deg under noise sigma=0.10. Branch-masking, OCS-noise, observation-style degradation, cross-phase, beta-sweep, and outlier audits show that this behavior is best interpreted as degradation-aware OCS-image co-utilization, not automatic OCS fallback. The benchmark therefore supports conditional robustness under tested synthetic degradations, with remaining failures under severe combined degradation, phase120 geometry, fixed framing sensitivity, and rare polar outliers. No real telescope validation or operational field robustness is claimed.

## Keywords

Space object attitude inversion; optical cross section; photometric image simulation; BRDF; self-occlusion; multi-modal fusion; synthetic observation degradation

## 1. Introduction

Optical observations are a practical source of information for non-cooperative space object attitude estimation, especially when cooperative telemetry is unavailable. The measured optical response depends on object geometry, surface material, illumination, viewing direction, phase angle, visibility, and self-occlusion. These dependencies make attitude inversion both a physical forward-modeling problem and a statistical estimation problem. Scalar photometric signatures and resolved photometric images can both encode attitude, but they do so through different information channels.

Optical cross section (OCS) or light-curve-like signatures summarize integrated reflected intensity across one or more observation geometries. They are compact, physically interpretable, and naturally suited to multi-geometry sampling, but they discard spatial image structure. Resolved photometric images preserve projected shape, component layout, shadow patterns, centroid shifts, and local brightness distributions. Clean synthetic images can therefore provide strong attitude cues for convolutional models, but that strength depends on image quality and on consistency between training and test rendering conditions.

The central question is not whether OCS or images are universally better. It is when the two modalities are complementary, and under what training or fusion design that complementarity is actually used. This question is difficult to answer if OCS signatures and images are generated from inconsistent assumptions about geometry, BRDF, attitude convention, material assignment, or visibility. It is also unsafe to read high accuracy on clean rendered images as evidence of field performance, because real optical observations may include seeing, optical blur, detector noise, finite resolution, background contamination, tracking errors, earthshine, calibration uncertainty, and phase-geometry shifts.

Here we present a unified BRDF-driven OCS-image simulation framework and a controlled yaw-pitch attitude inversion benchmark. A real satellite STL model is assigned nonuniform component materials and rendered through a GGX/Cook-Torrance BRDF with analytical self-occlusion. From the same physical model, we generate multi-geometry OCS features and clean photometric images, then evaluate OCS-only, image-only, late-fusion, and feature-fusion models. The benchmark separates three issues that are often conflated: clean-image upper-bound accuracy, image-degradation fragility, and the conditions under which fusion can use OCS as an active joint constraint.

This paper makes four contributions. First, it introduces a physically consistent simulation pipeline for paired OCS and photometric image generation under shared geometry, BRDF, attitude, observation, and visibility assumptions. Second, it establishes a controlled yaw-pitch inversion benchmark across OCS-only, image-only, late-fusion, and feature-fusion models. Third, it diagnoses the failure of clean-trained feature fusion under image degradation and shows that degradation-aware fusion can stabilize mean, p90, and Hit@5 under the tested synthetic degradations. Fourth, it clarifies the boundary of the fusion claim: U1 uses OCS and images jointly, but the evidence does not show automatic switching to an OCS-only fallback. The study remains simulation-based and does not claim real telescope validation.

## 2. Related Work

### 2.1 Optical signatures and BRDF modeling of space objects

Optical signatures of space objects are governed by target geometry, material reflectance, illumination and viewing geometry, phase angle, and visibility. BRDF-based modeling is therefore central to physically meaningful satellite photometry because it links surface scattering behavior to observed brightness and image intensity. Prior work on satellite material reflectance, brightness prediction, and radiometric modeling motivates physically grounded optical simulation [CITATION: BRDF-based space object photometry; CITATION: satellite brightness modeling]. The present study follows this modeling direction but uses it to generate paired OCS signatures and photometric images for attitude inversion under one shared forward model.

### 2.2 Light-curve and OCS-based attitude inversion

Light curves and OCS-like scalar signatures are attractive for attitude inference because they are low-dimensional and interpretable. They can be collected across multiple observation geometries and compared against forward models when object shape, material properties, and illumination conditions are known or assumed [CITATION: light-curve attitude inversion]. In this work, OCS is not treated as an automatic accuracy upper bound. It is tested as a component-level photometric constraint, using practical `per_part_log` features and diagnostic higher-dimensional variants to separate operationally plausible OCS inputs from semi-oracle information.

### 2.3 Photometric image simulation and image-based pose estimation

Resolved photometric images provide spatial cues that scalar signatures cannot preserve, including projected shape, component layout, shadow structure, centroid displacement, and local specular patterns. Synthetic imagery is widely used in spacecraft pose-estimation studies because real labeled imagery is scarce [CITATION: image-based spacecraft pose estimation]. The same practice also creates a risk: clean synthetic images may be easier than real or degraded observations. This paper therefore treats clean rendered images as an idealized upper-bound condition and tests degradation sensitivity explicitly.

### 2.4 Multi-modal fusion and robustness under degradation

Fusion is often motivated by the expectation that different modalities will fail under different conditions. In practice, feature-level fusion can become dominated by the strongest branch, and a clean-trained fusion model may not learn how to use a weaker branch when the dominant branch is degraded. The present OCS-image setting is a useful controlled case because both inputs are optical but differ in dimensionality, spatial structure, and degradation exposure. The core fusion question is therefore not whether fusion is always better, but whether the fusion design supports degradation-aware co-utilization of OCS and image evidence.

## 3. Method

### 3.1 Unified OCS-image simulation framework

We formulate the task as controlled yaw-pitch attitude inversion from two optical modalities: scalar OCS signatures and resolved photometric images. Both are generated from the same satellite STL geometry, component material assignment, BRDF model, attitude definition, illumination geometry, viewing geometry, and self-occlusion model. This design allows modality comparisons to be interpreted as information differences rather than artifacts of mismatched forward models.

The pipeline contains four stages. First, the satellite STL is converted into a facet-level representation with component labels, surface normals, facet areas, and nominal material parameters. Second, yaw-pitch attitudes and observation geometries define the relative orientation between the target, illumination, and detector directions. Third, a GGX/Cook-Torrance BRDF and analytical visibility calculation generate OCS values and photometric images. Fourth, OCS-only, image-only, late-fusion, and feature-fusion models are trained and evaluated using a shared split and angular metric.

### 3.2 Geometry, attitude parameterization, and split

The object geometry is a real satellite STL model represented by triangular facets and grouped into component-level material regions. The attitude state is parameterized by yaw and pitch, with roll fixed in the main benchmark. The main attitude grid uses 5 deg resolution, while a 10 deg grid is used for training and intermediate 5 deg attitudes are used for testing. This split tests interpolation across attitude space rather than direct reuse of all grid states.

The neural targets use a sin-cos representation for angular variables, and evaluation uses great-circle angular error in degrees. The OCS features are standardized using training-set statistics only. The final manuscript should keep the detailed Euler order, coordinate convention, hyperparameters, and implementation settings in a reproducibility table once the author has completed the remaining confirmation items.

### 3.3 OCS features and image generation

OCS signatures are generated over five observation geometries. The practical OCS feature used in the main OCS-only and fusion comparisons is concat5 `per_part_log`, a 30D component-level representation. The practical OCS-only reference is 5.91 deg mean error. A higher-dimensional `all_raw` 45D setting is treated only as a semi-oracle diagnostic and not as the main operational OCS result.

The main image branch uses 128 x 128 clean rendered photometric images under the phase63 condition. These images are idealized rendered products of the forward model. They do not include real atmosphere, detector response, optical PSF, tracking error, earthshine, background contamination, or telescope calibration effects. For this reason, clean-image results are reported as a controlled upper-bound condition for image-based inversion, not as expected field performance.

### 3.4 Baseline and fusion models

The benchmark includes OCS-only MLP predictors, image-only CNN predictors, late fusion, and feature-level OCS-image fusion. The main clean image baseline is a ResNet image-only model. The main clean fusion baseline concatenates ResNet image features with concat5 `per_part_log` OCS features. Earlier TinyCNN/OCS experiments are retained only as supporting diagnostics for complementarity and should not be confused with the ResNet-pair results.

The clean-trained feature-fusion model is evaluated under both clean and degraded images to diagnose whether it can fall back to OCS when image features fail. A degradation-aware fusion model, U1, is then trained with online image degradations. Additional variants and controls include modality dropout, augmentation plus dropout, an OCS-anchored gate, image-only same-augmentation controls, branch masking, OCS-noise tests, held-out synthetic degradations, observation-style degradation, cross-phase rendering, centroid-control analysis, beta-sweep late fusion, and outlier audits.

### 3.5 Degradation and control protocols

Controlled image degradations include Gaussian noise and brightness scaling in the v0.1 robustness tests. Experiment 12 diagnoses clean-trained naive fusion and evaluates U1 degradation-aware fusion under clean, noise sigma=0.01, noise sigma=0.10, brightness x0.50, and brightness x1.50 settings.

Experiment 12b adds causal controls. First, an image-only model is trained with the same augmentation used by U1, testing whether the U1 gains are only an image-augmentation effect. Second, U1 branches are masked using train-mean replacement for the image or OCS branch, testing whether each branch is active in the joint representation. Third, OCS noise and dual-degradation settings test whether OCS sensitivity increases under image degradation. Fourth, held-out synthetic degradations such as intermediate noise, blur, and downsampling test whether the learned robustness is limited to exactly matched augmentation cases. Fifth, outlier audits quantify rare large errors.

Experiment 12c applies observation-chain-inspired synthetic image degradations in the linear intensity domain using `expm1 -> degrade -> log1p`. These tests include read noise, background contamination, starfield contamination, combined medium degradation, and combined severe degradation. Experiment 12d renders additional phase24 and phase120 image grids for cross-phase sanity testing. Experiment 12e tests centered images to assess fixed-framing and centroid effects. Experiment 12f performs an oracle late-fusion beta sweep where beta is the image weight, beta=1 is image-only, and beta=0 is OCS-only. Experiment 12g audits U1 and 12b outliers. These are controlled synthetic stress tests, not real telescope validation.

## 4. Results

### 4.1 Forward-model validation and OCS signature behavior

The unified forward model produces paired scalar OCS signatures and photometric images under the same geometry, material, BRDF, attitude, and visibility assumptions. Self-occlusion is a necessary part of the simulation because visibility changes with attitude and observation geometry. The OCS signatures vary across component groups and observation geometries, making them suitable as compact attitude-dependent photometric features. This section should retain the v0.1 validation figures and any finalized self-occlusion sensitivity values, while keeping unconfirmed numerical details in the author-check list.

### 4.2 OCS-only attitude inversion

The practical concat5 `per_part_log` OCS-only model reaches 5.91 deg mean angular error. This result is less accurate than the clean ResNet image-only model, but it establishes OCS as a low-dimensional and interpretable photometric constraint. The higher-dimensional `all_raw` 45D OCS setting reaches 3.98 +/- 0.60 deg with Hit@5 = 90.7%, but this setting should remain a semi-oracle diagnostic rather than the operational OCS-only reference. Total-only OCS is much weaker at 36.69 deg, showing that component-level and multi-geometry structure are important for OCS inversion.

### 4.3 Image-only inversion under clean rendered images

Clean rendered photometric images provide a strong upper-bound case. The ResNet image-only model reaches 1.69 +/- 0.07 deg mean error with Hit@5 = 97.6%, while the lightweight TinyCNN baseline reaches 12.38 +/- 0.74 deg with Hit@5 = 26.1%. This gap indicates that clean rendered images contain strong attitude cues that a high-capacity CNN can exploit. It also motivates strict scope control: the result reflects idealized clean rendered images under the phase63 condition, not real telescope performance.

The centered-image control in Experiment 12e refines this interpretation. Removing or reducing the original fixed-framing cue degrades the ResNet image-only model from 1.69 deg to 2.88 deg and Hit@5 from 97.6% to 87.4%. This shows that fixed framing or centroid information contributes to the clean-image upper bound. Because the centered model remains substantially better than weak baselines, the clean-image result is not only a centroid leak; it still uses shape and photometric information. The manuscript should place this result in Limitations or Supplementary unless space allows a compact main-text note.

### 4.4 Clean-image fusion and modality dominance

Under clean rendered images, ResNet feature fusion with concat5 `per_part_log` OCS improves the image-only mean error from 1.69 +/- 0.07 deg to 1.47 +/- 0.07 deg. Hit@5 increases from 97.6% to 99.7%, and the worst-case error decreases from 9.9 deg to 6.6 deg. This supports a clean-condition fusion benefit, especially for tail behavior, but the gain is modest because the clean image branch is already strong.

The clean-fusion result should therefore be described as conditional complementarity, not fusion dominance. A stronger or richer OCS feature does not automatically improve all outcomes: ResNet + concat5 `all_raw` reaches a similar mean error of 1.49 +/- 0.10 deg but has a worse worst-case error of 18.7 deg. This conflict with a simple "more OCS information is always better" reading is handled by keeping `all_raw` as a semi-oracle diagnostic and evaluating fusion through mean, Hit@5, p90, and tail behavior together.

Experiment 12 shows that the clean-trained fusion model is image-dominant. Under clean conditions, the normal fusion model gives 1.57 deg, while masking the image branch gives 52.84 deg and masking the OCS branch gives 18.14 deg. These diagnostics indicate that the clean fusion head does not use OCS as a standalone replacement for the image branch, even though OCS carries useful information.

### 4.5 Degradation-aware fusion and modality-isolation controls

Clean-trained image-only and feature-fusion models are fragile under image degradation. The ResNet image-only model degrades from 1.69 deg to 85.85 +/- 3.00 deg under Gaussian noise sigma=0.01, with Hit@5 = 2.2%. The clean-trained ResNet-fusion model similarly fails: Experiment 11 reports about 73.36 deg under noise sigma=0.01, and Experiment 12 branch diagnostics report 75.08 deg under noise sigma=0.01 and 72.48 deg under noise sigma=0.10. This is a direct conflict with any old reading that feature fusion automatically provides robustness.

Branch masking shows why the failure occurs. Under noise sigma=0.01, the normal clean-trained fusion model gives 75.08 deg, image-masked fusion gives 52.84 deg, and OCS-masked fusion gives 88.88 deg. The degraded image branch actively contaminates the fused representation. Removing OCS makes the noisy fusion worse, so OCS is informative; however, masking the image branch leaves the model far from the practical OCS-only result of 5.91 deg. The correct conclusion is not OCS standalone fallback, but failure of the clean-trained fusion head to learn a usable fallback representation.

U1 changes this behavior by training fusion with online image degradation augmentation. U1 reaches 1.95 +/- 0.21 deg on clean images, 1.95 +/- 0.21 deg under noise sigma=0.01, and 2.31 +/- 0.26 deg under noise sigma=0.10, with Hit@5 = 96.6% and p90 = 3.73 deg at noise sigma=0.10. This largely eliminates the mean and p90 collapse seen in clean-trained image-only and fusion models under the tested image degradations. Rare large outliers remain, including worst-case errors above 100 deg in the Experiment 12 summary, so the result should not be described as fully robust.

Experiment 12b establishes that U1 is not merely an image-augmentation effect. Under the same augmentation, image-only+aug reaches 9.55 deg under noise sigma=0.10, whereas U1 reaches 2.31 deg. U1 is also better under clean images (1.95 deg vs 2.63 deg), noise sigma=0.01 (1.95 deg vs 2.80 deg), brightness x0.50 (1.98 deg vs 2.76 deg), and brightness x1.50 (2.00 deg vs 2.76 deg). These controls support degradation-aware OCS-image co-utilization.

The branch-masking and OCS-noise controls further define the mechanism. Under noise sigma=0.10, U1 normal inference gives 2.31 deg, image-train-mean masking gives 30.87 deg, and OCS-train-mean masking gives 58.56 deg. Both branches are active in the joint representation. However, image masking is still far above the practical OCS-only reference of 5.91 deg, so U1 is not an OCS-standalone fallback. OCS noise degrades U1 from 1.95 deg to 5.36 deg under clean images and from 2.31 deg to 5.95 deg under noise sigma=0.10 as OCS noise increases from 0% to 20%, supporting active OCS involvement rather than a discrete switching mechanism.

Held-out synthetic degradations support a bounded generalization claim. For noise sigma=0.03, noise sigma=0.05, blur k3, blur k5, downsample 64, and downsample 32, U1 remains around 1.96-2.06 deg, whereas image-only+aug ranges from 2.84 deg to 6.43 deg. This extends the evidence beyond exactly matched training degradation levels, but it is still synthetic and cannot be written as real-observation validation.

### 4.6 Ablation and sensitivity analysis

Several ablations define the benchmark boundary. Self-occlusion sensitivity supports retaining visibility modeling because the satellite scans show substantial occlusion across observation geometries. The 10 deg training to 5 deg testing split is used to evaluate interpolation across attitude space. Roll remains fixed, material parameters are nominal, and detailed BRDF, split, and phase-condition sensitivity values should only be entered where final author-confirmed values exist.

The U1-adjacent variants are also important because they prevent overclaiming. U2 modality dropout alone gives clean 1.96 deg but fails under image noise, reaching about 83.72 deg at noise sigma=0.01 and 84.26 deg at noise sigma=0.10. U3 augmentation plus dropout is more robust but worse than U1 in the reported setting, with clean 2.90 deg and noise sigma=0.10 4.59 deg. U4 OCS-anchored gating gives clean 7.75 deg and noise sigma=0.10 9.76 deg. These negative or weaker results show that robust fusion is not guaranteed by adding dropout or a gate; the current evidence supports U1-style degradation-aware co-utilization, while deployable gating remains future work.

### 4.7 Synthetic observation-style degradation and cross-geometry sanity tests

Experiment 12c tests observation-chain-inspired synthetic degradations in the linear intensity domain. Clean-trained image-only collapses under read noise, background contamination, starfield contamination, and combined degradations, with mean errors from about 78 deg to 89 deg. U1 remains near 2 deg under read_0.005 (1.95 deg), background_0.005 (2.12 deg), starfield (2.20 deg), and combined_medium (1.98 deg). Under combined_severe, U1 degrades to 13.88 deg while the 12f-internal OCS-only reference remains 6.58 deg. This result strengthens the Acta/ASR version by showing robust behavior under several synthetic observation-style stress tests, but it also supplies a clear severe-degradation failure boundary.

Experiment 12d tests cross-phase image generalization. Under phase63, image-only and fusion are strong at 1.69 deg and 1.57 deg. Under phase24, image-only degrades to 11.34 deg while fusion gives 6.85 deg. Under phase120, both image-only and fusion fail, at 83.08 deg and 79.71 deg. The conflict with an overly broad clean-image claim is handled by restricting phase63 clean-image performance to an idealized same-distribution upper-bound setting. Phase120 is not solved.

Experiment 12f provides an oracle late-fusion upper bound for inference-time weighting. In this sweep, beta is the image weight, beta=1 is image-only, and beta=0 is OCS-only. Under clean images, the best beta is 0.9 with best error 1.67 deg, close to the image branch. Under noise sigma=0.01 and sigma=0.10, the oracle best beta is 0.0 with best error 6.58 deg, matching the 12f-internal OCS-only reference. This result shows that explicit weighting could prevent catastrophic noisy-image failures if a reliable degradation detector, uncertainty estimator, or gate exists. It does not show that U1 automatically switches to OCS, and the 6.58 deg value must remain internal to the 12f retraining setup rather than replacing the main practical OCS-only value of 5.91 deg.

Experiment 12g audits rare large errors. For U1/12b outlier evaluation, errors above 30 deg occur in 42 of 49,950 evaluations, or 0.084%. Errors above 60 deg occur in 40 of 49,950 evaluations, and errors above 90 deg occur in 35 of 49,950 evaluations. The outliers concentrate near polar attitudes. This supports reporting stable mean, p90, and Hit@5, while preserving rare-outlier limitations.

## 5. Discussion

### 5.1 Main finding: controlled complementarity with explicit failure modes

The main finding is that OCS and photometric images provide complementary constraints only when the model design and training allow those constraints to be used under degradation. The unified simulator makes this conclusion interpretable because both modalities are generated under shared physical assumptions. Clean rendered images are highly informative, but they are also distribution-sensitive. OCS is less accurate than clean ResNet images in the main practical feature setting, but it provides a compact photometric constraint with different degradation exposure. Fusion can improve clean tail behavior and support degradation-aware robustness, but it is not automatically robust.

### 5.2 Why clean rendered images are an upper-bound condition

The clean ResNet image-only result is strong because the rendered images preserve stable projected shape, component layout, brightness distribution, and shadow cues. The centered-image control shows that fixed framing or centroid information contributes to this performance, but does not fully explain it. The cross-phase test shows that phase63 accuracy does not automatically transfer to phase120. Therefore, the correct scope is narrow: clean phase63 rendered images define an idealized upper-bound condition for image-based inversion under the present simulator.

### 5.3 Why OCS remains useful despite lower clean-image accuracy

The practical OCS-only result of 5.91 deg is not the best clean-image result. Its value lies in interpretability, low dimensionality, multi-geometry availability, and independence from image pixels within this benchmark. The 12f beta sweep further shows that when image evidence is catastrophically corrupted, an explicit oracle weighting can recover the OCS-side solution in that retrained setup. This does not mean real OCS measurements are error-free; real scalar photometry may still suffer from calibration, geometry, atmosphere, BRDF mismatch, and target-model uncertainty.

### 5.4 Conditional value of OCS-image fusion

The v0.2 evidence requires a sharper fusion interpretation than v0.1. Clean fusion improves the ResNet image-only result from 1.69 deg to 1.47 deg and improves selected tail behavior, but naive clean-trained fusion fails under image noise. Experiment 11 and Experiment 12 show that degraded image features can contaminate the fused representation rather than allowing OCS to take over. Experiment 12b then shows that U1 is stronger than image-only same augmentation and that OCS is active in the joint representation. The mechanism is therefore degradation-aware OCS-image co-utilization, not automatic fallback.

This distinction matters for future systems. A deployable robust fusion system would need explicit uncertainty estimation, degradation detection, adaptive gating, sensor-aware training, or OCS-anchored prediction to decide when image evidence should be downweighted. The 12f beta sweep is useful because it defines an oracle upper bound for such inference-time weighting. It is not a deployable automatic gate.

### 5.5 Implications for space object attitude inversion

For controlled optical attitude-inversion studies, the results suggest three reporting principles. First, clean synthetic image accuracy should be separated from degraded-image robustness. Second, OCS should be evaluated not only as a competitor to clean images, but also as a physically interpretable constraint with different failure modes. Third, fusion claims should be supported by degradation tests, branch diagnostics, and tail metrics rather than by mean clean accuracy alone.

For Acta Astronautica or Advances in Space Research, the most defensible contribution is a controlled simulation benchmark with a transparent fusion-mechanism audit. The paper should not be framed as an operational telescope system. Its contribution is to show how a BRDF-driven paired OCS-image simulator can expose when clean image models, naive fusion, degradation-aware fusion, and explicit weighting succeed or fail.

### 5.6 Scope and limitations

The study remains a controlled simulation benchmark. It does not use real optical telescope images with known attitude ground truth. The observation-style degradation tests are synthetic stress tests inspired by sensor and scene effects, not calibrated atmosphere-detector-telescope simulations. The clean image branch uses phase63 as the main condition, and phase120 is a strong cross-geometry failure case. The attitude task is yaw-pitch inversion with fixed roll, not full 3-DOF pose recovery.

Additional limitations are now explicit. Fixed framing and centroid cues contribute to the clean image upper bound, as shown by the 1.69 deg to 2.88 deg centered-image degradation. U1 remains vulnerable to severe combined degradation, where the mean error rises to 13.88 deg. Rare large outliers remain: error >30 deg occurs in 42/49,950 evaluations, concentrated near polar attitudes. The 12f beta sweep is an oracle analysis and does not provide an automatic deployable gate. The 12f OCS-only value of 6.58 deg is an internal retraining reference and should not be mixed with the main practical OCS-only result of 5.91 deg.

## 6. Conclusion

This paper presents a unified BRDF-driven OCS and photometric image simulation benchmark for controlled space object yaw-pitch attitude inversion. By generating scalar OCS signatures and clean rendered images from the same STL geometry, component materials, GGX/Cook-Torrance BRDF, observation geometry, attitude grid, and self-occlusion model, the benchmark isolates how the two optical modalities contribute under consistent assumptions.

The results show that clean rendered images provide a strong image-based upper-bound condition, with ResNet image-only performance of 1.69 +/- 0.07 deg and Hit@5 = 97.6%. Clean feature fusion with concat5 `per_part_log` OCS improves this to 1.47 +/- 0.07 deg, but clean-trained fusion is not robust by default and degrades to about 73 deg under image noise. Degradation-aware U1 fusion stabilizes the tested synthetic degradations, reaching 2.31 deg under noise sigma=0.10, and 12b controls show that this behavior is not explained by image augmentation alone. The supported interpretation is active OCS-image co-utilization, not OCS-standalone fallback.

The benchmark also defines the boundary of the claim. U1 remains imperfect under combined_severe degradation, phase120 cross-geometry tests fail, fixed framing affects clean image performance, and rare polar outliers remain. Future work should extend the benchmark to calibrated sensor and atmosphere models, broader phase and roll conditions, deployable uncertainty-aware fusion, and real optical observations with reliable attitude ground truth.

## Data Availability

Data availability will be specified in the final submission. `[需要作者确认 Q12：whether simulation data, STL-derived products, rendered images, OCS tables, trained models, scripts, and experiment logs can be shared; repository, embargo, or access-on-request wording]`

## Author Contributions

Author contributions will be completed before submission according to the target journal format. `[需要作者确认 Q13：author list, order, affiliations, and CRediT roles]`

## Funding

Funding information will be completed before submission. `[需要作者确认 Q14：grant numbers, institutional funding, or no-funding statement]`

## Conflict of Interest

Conflict-of-interest wording will be finalized according to the target journal format. `[需要作者确认 Q14：final COI statement]`

## References

Reference metadata remains to be verified before submission. Current placeholders should be replaced with checked bibliographic entries:

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

## B. Major Changes from v0.1

### 4.4 / 4.5 / 4.7 Results restructuring

1. v0.1 `4.4 OCS-image fusion under clean images` is split into clean fusion benefit and modality-dominance diagnosis. The clean gain remains, but the new text explicitly states that clean-trained fusion is image-dominant and does not learn an OCS-standalone fallback.
2. v0.1 `4.5 Robustness under controlled observation degradation` is rewritten around the conflict introduced by Experiment 11/12: image-only and naive fusion both collapse under image noise. U1 is introduced only after this failure mechanism is established.
3. New `4.7 Synthetic observation-style degradation and cross-geometry sanity tests` integrates 12c, 12d, 12f, and summarizes 12e/12g boundaries. The section states that 12c is synthetic observation-style stress testing, phase120 is a failure case, and 12f is an oracle weighting upper bound.

### Discussion

The old Discussion framed fusion as conditional complementarity. The v0.2 candidate keeps that idea but narrows it: fusion value depends on explicit training or weighting support. Naive fusion failure is now a central result, not a side note. U1 is described as degradation-aware OCS-image co-utilization, not automatic fallback.

### Limitations

The limitations are expanded to include no real telescope validation, synthetic-only observation-style degradation, fixed phase63 image branch, fixed roll/yaw-pitch task scope, centroid/framing contribution, combined_severe failure, phase120 failure, rare polar outliers, and 12f oracle beta not being a deployable gate.

### Data / Author / Funding / COI

Q12-Q14 remain placeholders. No AI-filled final data-sharing, author-contribution, funding, or conflict statement is introduced.

### Conflict handling between old text and new evidence

1. Old possible reading: clean fusion gain suggests fusion robustness. New handling: clean fusion gain is retained, but Experiment 11/12 proves clean-trained fusion fails under image degradation.
2. Old possible reading: OCS can act as fallback. New handling: OCS is active, but branch masking shows neither naive fusion nor U1 becomes OCS-only fallback.
3. Old possible reading: clean image result is a strong general result. New handling: centered-image and cross-phase tests restrict it to idealized same-distribution rendered imagery.
4. Old possible reading: U1 solves robustness. New handling: U1 stabilizes tested synthetic degradations but fails or weakens under combined_severe, rare polar outliers, and phase120.

## C. Claim-Evidence Map

| Claim | Evidence | Status |
|---|---|---|
| Clean rendered images define a strong image-based upper-bound condition. | ResNet image-only clean: 1.69 +/- 0.07 deg, Hit@5 = 97.6%. | Supported, but limited to clean phase63 rendered imagery. |
| Clean fusion improves mean and tail behavior. | ResNet + concat5 `per_part_log`: 1.47 +/- 0.07 deg; worst-case 9.9 -> 6.6 deg; Hit@5 99.7%. | Supported under clean rendered images. |
| Naive feature fusion is not automatically robust. | Experiment 11: noise sigma=0.01 about 73.36 deg; Experiment 12: noise sigma=0.01 normal 75.08 deg. | Supported. |
| Degraded image features contaminate clean-trained fusion. | Experiment 12 branch masking: noise sigma=0.01 normal 75.08 deg, image-masked 52.84 deg, OCS-masked 88.88 deg. | Supported. |
| Naive fusion does not learn OCS-standalone fallback. | Image-masked noisy fusion remains 52.84 deg, far from practical OCS-only 5.91 deg. | Supported. |
| U1 stabilizes tested image degradations. | Experiment 12 U1: clean 1.95 +/- 0.21 deg; noise sigma=0.10 2.31 +/- 0.26 deg; Hit@5 96.6%; p90 3.73 deg. | Supported for tested synthetic degradations. |
| U1 robustness is not only image augmentation. | Experiment 12b: image-only+aug noise sigma=0.10 9.55 deg vs U1 2.31 deg. | Supported. |
| OCS is active in U1 joint representation. | Experiment 12b branch masking: normal 2.31 deg, image_train_mean 30.87 deg, ocs_train_mean 58.56 deg under noise sigma=0.10; OCS noise degrades U1 from 2.31 to 5.95 deg at 20% OCS noise. | Supported. |
| U1 is not automatic OCS fallback. | Image masking gives 30.87 deg under noise sigma=0.10, still far above OCS-only 5.91 deg. | Supported. |
| U1 extends to held-out synthetic degradations. | Experiment 12b held-out noise/blur/downsample: U1 about 1.96-2.06 deg; image-only+aug 2.84-6.43 deg. | Supported, but synthetic only. |
| Observation-style stress tests strengthen bounded robustness. | Experiment 12c: U1 about 2 deg under read/background/starfield/combined_medium; combined_severe 13.88 deg. | Supported with severe boundary. |
| Cross-phase generalization is not solved. | Experiment 12d: phase24 image-only 11.34 deg / fusion 6.85 deg; phase120 image-only 83.08 deg / fusion 79.71 deg. | Supported as limitation. |
| Fixed framing or centroid cues contribute to clean image performance. | Experiment 12e: original 1.69 deg, Hit@5 97.6%; centered 2.88 deg, Hit@5 87.4%. | Supported as limitation, not sole explanation. |
| Oracle late-fusion weighting is an upper-bound path, not a deployed gate. | Experiment 12f: clean best beta=0.9, best 1.67 deg; noise best beta=0.0, best 6.58 deg. | Supported; requires future uncertainty/gating. |
| Rare large outliers remain. | Experiment 12g: >30 deg errors 42/49,950 = 0.084%; concentrated near polar attitudes. | Supported. |
| Main OCS-only reference and 12f OCS-only reference must not be mixed. | Main practical OCS-only `per_part_log`: 5.91 deg; 12f internal OCS-only: 6.58 deg. | Required consistency rule. |

## D. Red-line Audit

| Red line | Audit result |
|---|---|
| Do not claim fusion automatically robust. | The draft says clean-trained naive fusion fails under image degradation and that robust fusion needs degradation-aware training or explicit weighting. |
| Do not claim U1 automatically switches to OCS. | The draft states U1 is OCS-image co-utilization and explicitly rejects switching/fallback interpretation. |
| Do not claim OCS standalone fallback. | Branch masking is used to show image-masked U1 remains far above OCS-only. |
| Do not claim near-perfect or fully robust performance. | The draft names combined_severe failure, phase120 failure, and rare polar outliers. |
| Do not claim real telescope validation. | The draft repeatedly states no real telescope validation and labels 12c as synthetic observation-style stress testing. |
| Do not claim operational or field-proven robustness. | The draft frames the work as controlled simulation benchmark and leaves deployment requirements to future work. |
| Do not claim phase120 generalization is solved. | Phase120 is reported as a strong failure case at about 80 deg. |
| Do not claim obs-aug is a successful robust training strategy. | The draft centers U1 and same-augmentation controls; it does not promote obs-aug as a general solution. |
| Do not claim 12f beta is deployable automatic gating. | The draft calls 12f an oracle upper bound requiring future uncertainty estimation or gating. |
| Do not mix 5.91 deg and 6.58 deg OCS-only values. | The draft uses 5.91 deg as the main practical OCS-only reference and 6.58 deg only as the 12f internal retraining reference. |

## E. Remaining Author/Codex Checks

1. Q12: Confirm data availability wording, including whether simulation data, STL-derived products, rendered images, OCS tables, trained models, and scripts can be shared.
2. Q13: Confirm author list, author order, affiliations, and CRediT roles.
3. Q14: Confirm funding, grant numbers, no-funding wording if applicable, and conflict-of-interest statement.
4. Verify all citation placeholders and Table 1 related-work claims against the corrected bibliography.
5. Confirm final figure/table numbering after deciding whether 12b branch masking, 12c, 12d, and 12f are main-text tables or supplementary tables.
6. Decide whether 12e centered-image and 12g outlier audit appear in main text, Supplementary, or Limitations only.
7. Recheck Experiment 11 vs Experiment 12 naive-fusion numbers in final wording: 73.36 deg is the Experiment 11 headline; 75.08/72.48 deg are Experiment 12 diagnostic values.
8. Confirm that the final Methods table includes split, sin-cos target, great-circle metric, OCS train-only standardization, U1 training, 12b controls, 12c linear-domain degradation, 12d rendering protocol, and 12f beta definition.
9. Verify whether U2/U3/U4 variant values should remain in the main manuscript, Supplementary, or Codex audit notes only.
10. Confirm target-journal formatting for Data Availability, Author Contributions, Funding, Conflict of Interest, and Supplementary Material.
11. Keep CJA/AST and TAES/JGCD versions frozen until the Acta/ASR first-priority version is reviewed and accepted by the author.
