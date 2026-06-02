# Step 5 GPT 输出：Results

## A. Results Evidence Ladder

1. Start from forward-model credibility: real STL, nonuniform GGX materials, analytical self-occlusion, multi-geometry OCS, and clean photometric rendering define a controlled physical benchmark.
2. Validate physical consistency before inversion: simple-geometry OCS-image checks close within sub-percent error, and synthetic/manual occlusion tests support the visibility model.
3. Show that OCS signatures are attitude-informative, especially when multi-geometry and component-level features are used.
4. Separate practical OCS features from diagnostic upper bounds: `per_part_log` is practical; `all_raw` is semi-oracle.
5. Establish lightweight image baseline first: TinyCNN shows that a small CNN can use image cues but does not represent the image modality upper bound.
6. Establish clean-image upper bound: ResNet-18 on clean phase63 images reaches very high accuracy under ideal rendered conditions.
7. Show clean fusion effect with strong image model: ResNet + per_part_log OCS improves mean, Hit@5, and worst-case tail error, but only modestly because the clean image branch is already strong.
8. Use early TinyCNN/OCS fusion as diagnostic evidence: fusion benefit depends on OCS information level, and `r = 0.003` only supports complementary failure modes in that earlier diagnostic.
9. Stress-test observation quality: additive Gaussian image noise collapses ResNet performance, whereas OCS is independent of image pixels in this benchmark.
10. Show conditional fusion under OCS degradation: as OCS noise increases, fusion gain increases, supporting conditional complementarity rather than universal superiority.
11. Close with ablation/sensitivity evidence and boundaries: self-occlusion, split design, feature choices, fixed roll, phase63, and nominal material parameters define the controlled scope.

中文说明：Results 的证据顺序是“先证明 forward model 可信，再证明 OCS 和图像各自是什么水平，再证明 fusion 何时有用，最后用退化与消融防御审稿风险”。

## B. Section Outline

| Section | Claim-first topic sentence | Key evidence | Figure/table target | Boundary / risk |
|---|---|---|---|---|
| 4.1 Forward-model validation and OCS signature analysis | The forward model provides a physically consistent basis for comparing OCS and image observations. | STL, 3 components, GGX, 5 geometries, 2701 attitudes, 13,505 geometry-attitude samples, sub-percent simple-geometry checks, occlusion validation. | Fig. 2, Fig. 3 | Not real telescope validation. |
| 4.2 OCS-only attitude inversion | Multi-geometry and component-level OCS features provide usable attitude constraints, while diagnostic all_raw defines an upper bound. | per_part_log 5.91 deg, Hit@5 73.8%; all_raw 3.98 +/- 0.60 deg, Hit@5 90.7%; total_log 36.69 deg. | Table 2, Fig. 4 | all_raw is semi-oracle. |
| 4.3 Image-only inversion | Clean rendered images provide a strong upper-bound case for image-based inversion when a high-capacity model is used. | TinyCNN 12.38 +/- 0.74 deg; ResNet-18 1.69 +/- 0.07 deg, Hit@5 97.6%; audit facts. | Table 2, Fig. 4 | Clean synthetic upper bound, not field performance. |
| 4.4 OCS-image fusion under clean images | Fusion provides modest but meaningful benefits under clean images, especially in tail errors, but not all OCS features improve fusion equally. | ResNet+per_part_log 1.47 +/- 0.07 deg, Hit@5 99.7%, worst 6.6 deg; all_raw fusion worst 18.7 deg. | Table 3, Fig. 4 | Conditional benefit, not universal best. |
| 4.5 Robustness under controlled observation degradation | Image-only clean performance is fragile under additive noise, while OCS remains independent of image-pixel degradation and fusion gains increase when OCS quality degrades. | 1% noise 85.85 deg, Hit@5 2.2%; brightness scaling results; OCS noise gain +1.97 to +6.29 deg. | Fig. 5, Fig. 6, Table 4 | Controlled stress tests, not full atmosphere/detector model. |
| 4.6 Ablation and sensitivity analysis | Additional checks support the interpretation of the benchmark and define its boundaries. | 10 deg -> 5 deg split; mhd/epsilon validation; phase63 fairness and random split `[需要作者确认]`; BRDF/roll sensitivity `[需要作者确认]`. | Fig. 7, Table 4 | Do not imply unreported ablation numbers. |

## C. Results Draft

### 4.1 Forward-model validation and OCS signature analysis

The unified forward model provides a physically consistent basis for comparing scalar OCS signatures and rendered photometric images. The benchmark uses a real satellite STL geometry with three component groups: metal body, solar panel, and baffle/shade. These components are assigned nonuniform GGX/Cook-Torrance material settings, and the same attitude definition, illumination direction, viewing direction, BRDF, and visibility assumptions are used to generate both OCS signatures and photometric images. The main yaw-pitch grid contains 73 yaw samples and 37 pitch samples, resulting in 2701 attitudes. For the OCS branch, five sun-sensor geometries are used, producing 5 x 2701 = 13,505 attitude-geometry samples across a phase-angle range of approximately 24 deg to 120 deg.

Before evaluating attitude inversion, we checked the numerical consistency and visibility behavior of the forward model. Simple-geometry tests, including single-plate and cube-like closure cases, showed sub-percent agreement between analytical or facet-level OCS calculations and rendering-derived checks. Self-occlusion behavior was evaluated using synthetic single-plate, double-plate, U-block, and nested-cylinder cases, together with sampled Blender/manual ray-cast review. These checks support the use of the analytical ray-based visibility model for controlled OCS simulation. They should not be interpreted as real optical validation, but they reduce the risk that the inversion results are driven by obvious geometric or visibility implementation artifacts.

The OCS scans further show that attitude-dependent optical signatures are strongly affected by both observation geometry and self-occlusion. Across the five observation geometries, occlusion rates fall roughly in the 60% to 78.5% range, indicating that visibility is not a minor correction for this nonconvex three-component target. The resulting OCS maps and component-level contribution maps are therefore important not only as input features for inversion but also as observability diagnostics. Fig. 3 should visualize this point using yaw-pitch OCS heatmaps, part-level contribution maps, and occlusion-rate maps.

### 4.2 OCS-only attitude inversion and multi-geometry photometric constraints

OCS-only inversion demonstrates that low-dimensional photometric signatures can provide useful yaw-pitch attitude constraints when multi-geometry and component-level information is retained. The practical `per_part_log` OCS representation reaches a mean angular error of 5.91 +/- 0.22 deg, with Hit@5 = 73.8% and Hit@10 = 94.3%. This result indicates that component-resolved OCS signatures encode substantially more attitude information than a single scalar total brightness response.

The importance of feature design is visible across OCS variants. The `total_log` feature gives a much weaker result, with 36.69 +/- 3.6 deg mean error, Hit@5 = 9.7%, and Hit@10 = 23.5%. This weak baseline suggests that total OCS alone is often insufficient for precise yaw-pitch inversion in the tested setting. In contrast, the `all_raw` 45D representation reaches 3.98 +/- 0.60 deg, Hit@5 = 90.7%, and Hit@10 = 97.1%. However, this representation includes additional diagnostic quantities and is therefore treated as a semi-oracle upper bound rather than a practical observation setting.

The OCS-only results support two conclusions. First, OCS is not inherently weak: when multi-geometry and component-level information is available, it provides a robust and interpretable photometric constraint. Second, not every OCS representation has the same operational meaning. In the remaining Results, `per_part_log` is emphasized as the practical OCS-only setting, while `all_raw` is reported only as a diagnostic upper bound.

### 4.3 Image-only inversion: from TinyCNN to ResNet clean-image upper bound

Image-only inversion shows that clean rendered photometric images can provide highly informative attitude cues, but only when the model capacity is sufficient. The lightweight TinyCNN baseline reaches 12.38 +/- 0.74 deg mean error and Hit@5 = 26.1% on the clean phase63 128 x 128 images. This result is useful as a lightweight baseline, but it should not be used to characterize the upper bound of image-based inversion.

When the image branch is evaluated with a stronger ResNet-18 model, the clean-image result improves to 1.69 +/- 0.07 deg mean error, Hit@5 = 97.6%, and Hit@10 = 99.9%. This establishes clean rendered photometric images as a strong upper-bound condition for image-based attitude inversion in the controlled benchmark. The result should be interpreted carefully: the rendered images are clean, aligned with the simulation distribution, and do not include atmosphere, optical PSF, detector response, earthshine, or background contamination. Therefore, this result is not a field-performance estimate for real telescope images.

We also audited the dataset structure to reduce the likelihood that the strong ResNet result is caused by trivial leakage. The train/test split follows the 10 deg -> 5 deg protocol, so test attitudes are not simply repeated training grid points. File names and labels are aligned, and normalization uses fixed constants rather than test-set statistics. The target centroid displacement has a correlation with yaw (r = 0.66), which is a physical rendering cue under the controlled camera setup, but this cue may not transfer to field observations where tracking and centering procedures can change the image-position distribution. Mean intensity is nearly uncorrelated with attitude (r < 0.02), reducing the concern that the network is using a simple brightness proxy for angle.

### 4.4 OCS-image fusion under clean images

Fusion under clean rendered images provides modest but meaningful gains when OCS is combined with a strong image model. The ResNet image-only baseline reaches 1.69 +/- 0.07 deg mean error, P90 = 3.31 deg, worst-case error = 9.9 deg, and Hit@5 = 97.6%. Adding concat5 `per_part_log` OCS features improves the result to 1.47 +/- 0.07 deg, P90 = 2.71 deg, worst-case error = 6.6 deg, and Hit@5 = 99.7%. In relative terms, the mean error decreases by 0.22 deg, or about 13%, and the worst-case error decreases by about one third.

This improvement should be described as conditional complementarity rather than fusion dominance. The clean image branch is already very strong, so the remaining mean-error margin is small. The main value of OCS in this setting is not to replace the image branch, but to improve tail behavior and provide an additional physical constraint. The comparison between fusion variants supports this interpretation. Using only phase63 `per_part_log` OCS features gives 1.61 +/- 0.07 deg, P90 = 2.97 deg, worst-case = 7.4 deg, and Hit@5 = 99.2%. In contrast, ResNet + concat5 `all_raw` reaches 1.49 +/- 0.10 deg but has a worse worst-case error of 18.7 deg, despite using a stronger semi-oracle OCS representation. Thus, a stronger OCS representation does not automatically produce better fusion tail behavior.

Earlier TinyCNN/OCS fusion experiments provide an additional diagnostic view of conditional complementarity. When OCS information is very strong (`all_raw`), adding a weaker image branch can hurt, with feature fusion reaching 5.42 deg compared with 3.98 deg for OCS-only. When OCS information is at an intermediate level (`per_part_log`), feature fusion improves from 5.91 deg for OCS-only and 12.38 deg for CNN-only to 4.10 +/- 0.77 deg. When OCS is weak (`total_log`), the image branch dominates, and late fusion reaches 11.99 deg compared with 36.69 deg for OCS-only. These trends indicate that fusion benefit depends on the information balance between modalities. In an earlier TinyCNN/OCS diagnostic, the error correlation between OCS and CNN was r = 0.003, suggesting complementary failure modes; this diagnostic should not be reported as a ResNet-pair correlation unless a corresponding ResNet analysis is performed.

### 4.5 Robustness under controlled observation degradation

The clean-image upper bound is fragile under additive image noise. With no added noise, ResNet-18 reaches 1.69 deg and Hit@5 = 97.6%. Under Gaussian image noise with sigma = 0.01, performance degrades to 85.85 +/- 3.00 deg and Hit@5 = 2.2%. Increasing the noise level to sigma = 0.03, 0.05, and 0.10 gives similarly poor mean errors of 85.49 deg, 85.97 deg, and 87.92 deg, with Hit@5 decreasing to 1.5%, 1.2%, and 1.0%, respectively. These results show that the clean ResNet result depends strongly on image quality and distribution consistency.

Brightness scaling is less destructive than additive Gaussian noise in the tested setting. Scaling brightness by 0.50 gives 3.45 deg and Hit@5 = 78.7%, while scaling by 0.75, 1.25, and 1.50 gives 2.03 deg, 1.77 deg, and 2.00 deg, respectively. This contrast suggests that the ResNet branch is more sensitive to pixel-level stochastic corruption than to global intensity scaling in the controlled images. However, neither Gaussian noise nor brightness scaling should be treated as a complete model of real atmospheric or detector degradation. They are controlled observation-quality stress tests.

OCS provides a complementary robustness perspective because it is independent of image pixels in this benchmark. The practical OCS-only `per_part_log` result of 5.91 deg is not the clean-image accuracy upper bound, but it remains unaffected by image noise. Conversely, when the OCS branch is degraded by synthetic OCS noise while the image branch remains clean, fusion gains become larger. The reported gain increases from +1.97 deg at 0% OCS noise to +3.30 deg at 10% OCS noise and +6.29 deg at 20% OCS noise. At 10% OCS noise, OCS-only reaches 9.99 +/- 0.35 deg while fusion reaches 6.69 +/- 1.34 deg; at 20% OCS noise, OCS-only reaches 17.25 +/- 0.71 deg while fusion reaches 10.96 +/- 2.51 deg. The exact 0% OCS-only and fusion values for this OCS-noise table should be filled as `[需要作者确认：0% OCS noise table values]`.

Together, the degradation experiments support the central claim that fusion is conditional. Clean images can be extremely accurate, but their performance is vulnerable to image corruption. OCS is not the accuracy upper bound under clean image conditions, but it provides an interpretable photometric constraint independent of image quality. Fusion becomes most valuable when one modality is weakened and the other retains complementary information.

### 4.6 Ablation and sensitivity analysis

Several additional checks support the interpretation of the benchmark and define its limits. The 10 deg -> 5 deg split is designed to test interpolation over attitude space rather than direct memorization of all 5 deg grid states. Random split, phase63 fairness, BRDF sensitivity, occlusion ablation, and roll sensitivity should be reported as supporting analyses where finalized values are available `[需要作者确认：which ablations have final numbers for main text]`.

Self-occlusion sensitivity supports the chosen visibility settings. The benchmark uses `epsilon = 1.0 mm` and `min_hit_distance = 1.0 mm`, selected from synthetic-geometry validation and sensitivity scans on the real three-component model. This setting suppresses self-intersection in single-plate tests and retains cross-part and internal occlusion in double-plate, U-block, and nested-cylinder tests. In the main satellite scans, occlusion rates of roughly 60% to 78.5% across observation geometries show that self-occlusion is substantial and should not be ignored.

The remaining limitations should be interpreted as study boundaries rather than hidden claims. The current benchmark estimates yaw and pitch under fixed roll. The main image branch uses phase63 clean rendered images, and broader cross-phase image generalization is not treated as a primary result. Material parameters are nominal rather than target-calibrated. These choices make the benchmark controlled and interpretable, but they also define the scope of the reported Results.

## D. Figure and Table Plan

| Figure / Table | Content | Key data | Caption intent |
|---|---|---|---|
| Fig. 2 | STL geometry, material labels, coordinate system, observation geometries | three components; 5 geometries; phase range 24-120 deg | Show the physical setup used by both OCS and images. |
| Fig. 3 | OCS yaw-pitch heatmaps, component contributions, occlusion rate | 2701 attitudes; occlusion 60%-78.5% | Show that OCS is attitude-dependent and visibility-sensitive. |
| Fig. 4 | Main inversion results | OCS-only, TinyCNN, ResNet, fusion | Summarize the controlled inversion benchmark and clean-image upper bound. |
| Fig. 5 | Image degradation robustness | ResNet clean vs Gaussian noise / brightness scaling | Show fragility of clean image performance under controlled degradation. |
| Fig. 6 | OCS noise and fusion gain | gain +1.97 to +6.29 deg | Show that fusion value increases when OCS quality degrades. |
| Fig. 7 | BRDF / occlusion / roll / split sensitivity summary | `[需要作者确认：final values]` | Provide reviewer-facing sensitivity and limitation support. |
| Table 2 | Main inversion benchmark | OCS MLP variants, TinyCNN, ResNet | One table for main accuracy hierarchy and roles. |
| Table 3 | ResNet fusion vs image-only | A1-A4 cases | Show clean-image fusion mean and tail-error gains. |
| Table 4 | Robustness and sensitivity summary | degradation table and OCS-noise table | Summarize controlled observation-quality stress tests. |

## E. Main Results Tables Draft

### Table 2. Main inversion benchmark

| Method / feature | Input | Mean error (deg) ↓ | Hit@5 ↑ | Hit@10 ↑ | Role |
|---|---|---:|---:|---:|---|
| OCS MLP all_raw 45D | Multi-geometry OCS + diagnostic quantities | 3.98 +/- 0.60 | 90.7% | 97.1% | Semi-oracle OCS upper bound |
| OCS MLP per_part_log 30D | Practical component-level OCS | 5.91 +/- 0.22 | 73.8% | 94.3% | Practical OCS-only setting |
| OCS MLP total_log 15D | Total OCS only | 36.69 +/- 3.6 | 9.7% | 23.5% | Weak OCS baseline |
| Weighted kNN all_raw | OCS feature baseline | 21.84 | 47.9% | [需要作者确认] | Classical / low-capacity baseline |
| TinyCNN image-only | phase63 128 x 128 clean image | 12.38 +/- 0.74 | 26.1% | 55.8% | Lightweight image baseline |
| ResNet-18 image-only | phase63 128 x 128 clean image | 1.69 +/- 0.07 | 97.6% | 99.9% | Clean-image upper bound |

### Table 3. ResNet fusion under clean rendered images

| Case | Model / input | Mean +/- std (deg) ↓ | P90 (deg) ↓ | Worst (deg) ↓ | Hit@5 ↑ | Hit@10 ↑ | Interpretation |
|---|---|---:|---:|---:|---:|---:|---|
| A1 | ResNet image-only | 1.69 +/- 0.07 | 3.31 | 9.9 | 97.6% | 99.9% | Clean-image upper bound |
| A2 | ResNet + concat5 per_part_log 30D | 1.47 +/- 0.07 | 2.71 | 6.6 | 99.7% | 100% | Best clean fusion setting |
| A3 | ResNet + phase63 per_part_log 6D | 1.61 +/- 0.07 | 2.97 | 7.4 | 99.2% | 100% | Single-phase OCS fairness check |
| A4 | ResNet + concat5 all_raw 45D | 1.49 +/- 0.10 | 2.70 | 18.7 | 99.2% | 99.9% | Semi-oracle OCS does not guarantee tail robustness |

### Table 4. Robustness and controlled degradation summary

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
| OCS noise 0% | OCS / fusion | [需要作者确认] | [需要作者确认] | Fusion gain +1.97 deg |
| OCS noise 10% | OCS-only -> fusion | 9.99 +/- 0.35 -> 6.69 +/- 1.34 | [需要作者确认] | Fusion gain +3.30 deg |
| OCS noise 20% | OCS-only -> fusion | 17.25 +/- 0.71 -> 10.96 +/- 2.51 | [需要作者确认] | Fusion gain +6.29 deg |

## F. Claim-Evidence-Risk Map

| Claim | Evidence | Risk | Safe wording |
|---|---|---:|---|
| Forward model is physically consistent for controlled comparison. | Same STL/material/BRDF/visibility; simple-geometry closure; occlusion validation. | Medium | "physically consistent controlled benchmark" not real validation |
| OCS is attitude-informative. | per_part_log 5.91 deg; all_raw 3.98 deg upper bound. | Low | "provides usable attitude constraints" |
| all_raw is not practical. | Includes diagnostic quantities; 45D. | Low | "semi-oracle upper bound" |
| Clean images are highly informative. | ResNet 1.69 deg, Hit@5 97.6%. | Medium | "clean rendered upper-bound setting" |
| TinyCNN is not image upper bound. | TinyCNN 12.38 deg vs ResNet 1.69 deg. | Low | "lightweight baseline" |
| Fusion improves clean ResNet tail errors. | ResNet+per_part_log: worst 9.9 -> 6.6; Hit@5 97.6 -> 99.7. | Medium | "modest but meaningful gains" |
| Fusion is conditional. | all_raw fusion has worst 18.7; OCS strength changes fusion behavior; OCS-noise gain increases. | Low | "conditional complementarity" |
| Image noise exposes fragility. | sigma=0.01 gives 85.85 deg, Hit@5 2.2%. | Medium | "controlled stress test" |
| OCS is robust to image degradation. | OCS features independent of image pixels. | Medium | "unaffected by image-pixel degradation in this benchmark" |
| r=0.003 supports complementarity. | Earlier TinyCNN/OCS diagnostic only. | High | "suggested complementary failure modes in an earlier diagnostic" |

## G. Self-review Checklist

1. 是否发明了实验或数值？  
   **No.** Only provided values are used; missing values are marked `[需要作者确认]`.

2. 是否把 clean image 写成 field performance？  
   **No.** Clean image is consistently described as idealized rendered upper-bound.

3. 是否夸大 fusion？  
   **No.** Fusion is described as conditional, with cases where it helps and cases where it does not automatically help.

4. 是否把 OCS 写成永远优于图像？  
   **No.** ResNet clean image is explicitly stronger than practical OCS-only in clean conditions.

5. 是否把 all_raw 写成 semi-oracle？  
   **Yes.** all_raw is repeatedly marked semi-oracle / diagnostic upper bound.

6. 是否把 r=0.003 限定为 TinyCNN/OCS diagnostic？  
   **Yes.** It is not written as ResNet-pair evidence.

7. 是否说明 image degradation 是 controlled stress test？  
   **Yes.** Gaussian noise and brightness scaling are not treated as full realistic degradation models.

8. 是否明确 no real telescope validation？  
   **Yes.** Forward-model checks are distinguished from real optical validation.

9. 是否没有把 ISAR 并入主线？  
   **Yes.** ISAR is not mentioned in Results.

## H. Questions for Author

1. Angular error formula 是否已固定？Results 表和 Method 需要一致写法。
2. OCS noise 0% 的 OCS-only / fusion mean 和 Hit@5 是否可以补入 Table 4？
3. BRDF sensitivity、occlusion ablation、roll sensitivity、random split、phase63 fairness 哪些已有最终数值可以放正文？
4. ResNet-fusion 在图像退化下是否已经补测？如果没有，是否写入 Future Work 而不是 Results？
5. 是否需要补测 ResNet-pair 的 OCS-image error correlation，否则 `r=0.003` 只保留为 TinyCNN diagnostic？
6. Fig. 7 是否放正文，还是把敏感性分析合并到 Supplementary？

