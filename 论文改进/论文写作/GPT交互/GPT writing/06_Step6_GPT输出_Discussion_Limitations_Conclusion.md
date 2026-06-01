# Step 6 GPT 输出：Discussion / Limitations / Conclusion

## A. Discussion Logic Map

1. Start from the central interpretation rather than repeating tables: OCS and photometric images encode different attitude information under a shared BRDF-driven forward model.
2. Explain why clean rendered images are strong: they preserve stable shape, shadow, centroid, and brightness-distribution cues that a ResNet-18 can exploit.
3. Immediately bound this image result as an idealized upper-bound because real telescope effects are not modeled.
4. Explain why OCS remains useful even when it is not the clean-image accuracy upper bound: it is low-dimensional, interpretable, multi-geometry, and independent of image-pixel degradation in this benchmark.
5. Interpret fusion as a conditional reliability mechanism: useful for tail errors and degradation scenarios, not universally best.
6. Discuss operational implications cautiously: future systems should report clean-image upper bounds separately from degraded performance and should evaluate tail errors, not just mean error.
7. Present limitations as scope boundaries of a controlled benchmark: no real telescope validation, fixed roll, phase63 image branch, nominal materials, and simplified degradation.
8. End with future work toward real optical observations, calibrated materials, broader phase/roll conditions, and more realistic sensor/atmosphere modeling.

中文说明：Discussion 的核心不是重复 Results，而是回答审稿人最可能问的问题：为什么 clean ResNet 很强、为什么还需要 OCS、fusion 到底有什么价值、没有真实数据是否还能投稿。

## B. Section Outline

| Section | Section goal | Key interpretation | Evidence to cite | Boundary / risk |
|---|---|---|---|---|
| 5.1 Main finding | State central contribution | OCS and images provide conditionally complementary constraints under shared physics | Unified model; OCS/image/fusion results | Do not claim universal fusion superiority |
| 5.2 Clean image upper bound | Explain why ResNet is strong | Clean images preserve stable spatial and photometric cues | ResNet 1.69 deg; TinyCNN 12.38 deg | Not field performance |
| 5.3 OCS value | Explain why OCS remains important | OCS is interpretable, low-dimensional, multi-geometry, image-pixel independent | per_part_log 5.91 deg; all_raw 3.98 semi-oracle | Not always better than images |
| 5.4 Conditional fusion | Explain fusion behavior | Fusion improves mean modestly and tail errors, but depends on feature quality | 1.69 -> 1.47; worst 9.9 -> 6.6; all_raw worst 18.7; OCS-noise gains | Not universally best |
| 5.5 Implications | Translate findings to field design | Separate upper-bound image performance from degradation; report tail metrics | degradation and fusion results | Do not imply deployment |
| 5.6 Scope and limitations | Define boundaries honestly | Controlled simulation, no real telescope validation, fixed roll, phase63, nominal materials | project facts | Avoid self-damaging tone |
| 6 Conclusion | Close with bounded takeaways | Unified benchmark reveals conditional complementarity | strongest evidence only | No new claims |

## C. Discussion Draft

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

## D. Limitations Draft

The present work should be interpreted as a physically consistent simulation and controlled inversion benchmark, not as a field validation study. No real optical telescope images with known attitude ground truth are used. The rendered photometric images are clean and idealized; they do not explicitly model atmospheric seeing, tracking error, detector response, optical PSF, earthshine, background contamination, saturation, or realistic sensor noise. Consequently, the ResNet-18 image-only result represents an optimistic upper bound under clean rendered imagery, not an estimate of operational telescope performance. The current attitude task is limited to yaw-pitch inversion under fixed roll, and the main image branch uses one rendered phase condition; broader cross-phase image generalization and full roll variation remain outside the main benchmark. The material parameters are nominal rather than calibrated measurements of the specific target, so BRDF sensitivity analysis and material validation are needed before stronger physical conclusions can be drawn. Finally, OCS is independent of image-pixel degradation in this benchmark, but real OCS or light-curve measurements may still suffer from photometric calibration errors, BRDF mismatch, observation-geometry uncertainty, target-model uncertainty, and measurement noise. These limitations do not invalidate the controlled comparison; instead, they define the scope in which the reported OCS-image complementarity should be interpreted and identify the next steps required for field deployment.

中文说明：这段可以作为独立 Limitations 小节，也可以放在 Discussion 最后一节。语气是“边界清楚”，不是“自我否定”。

## E. Conclusion Draft

This paper presented a unified BRDF-driven simulation and controlled inversion benchmark for space object yaw-pitch attitude estimation from OCS signatures and photometric images. By generating both modalities from the same STL geometry, nonuniform material assignment, GGX/Cook-Torrance BRDF, attitude definition, and self-occlusion model, the study isolates how scalar photometric signatures and resolved images contribute to attitude inversion under consistent physical assumptions.

The results show that clean rendered photometric images provide a strong upper-bound case for image-based inversion, with ResNet-18 reaching 1.69 +/- 0.07 deg under idealized imagery. However, the same image-only setting is highly fragile under additive image noise, degrading to 85.85 +/- 3.00 deg under 1% Gaussian noise. OCS does not define the clean-image accuracy upper bound, but the practical `per_part_log` OCS setting provides an interpretable photometric constraint, and OCS-image fusion improves selected clean-image tail errors from 9.9 deg to 6.6 deg. Fusion gains also increase under controlled OCS degradation, supporting the interpretation of fusion as conditional complementarity rather than universal superiority.

The current study does not include real optical telescope validation and is limited to yaw-pitch inversion under fixed roll with clean rendered images and nominal material parameters. Future work should extend the benchmark to calibrated materials, broader phase and roll conditions, explicit atmosphere and sensor modeling, and real optical observations with reliable attitude ground truth.

## F. Reviewer-Facing Defense Points

1. **Why no real telescope validation?**  
   Response: The paper is positioned as a physically consistent simulation and controlled inversion benchmark. It does not claim field performance. Real optical validation is identified as future work requiring known attitude ground truth.

2. **Why use OCS if ResNet clean is much better?**  
   Response: ResNet clean is an idealized image upper bound. OCS provides low-dimensional, interpretable, multi-geometry photometric constraints and remains independent of image-pixel degradation in this benchmark.

3. **Why does image noise collapse ResNet?**  
   Response: The result indicates sensitivity of clean-image cues to pixel-level corruption. Gaussian noise is a controlled stress test, not a full atmosphere model. It supports separating clean upper-bound accuracy from degraded-observation robustness.

4. **Why is fusion improvement modest in clean images?**  
   Response: The clean image branch is already very strong, leaving little mean-error margin. The more relevant fusion gains are Hit@5 and tail-error improvements, including worst-case reduction from 9.9 deg to 6.6 deg.

5. **Why fixed roll?**  
   Response: The benchmark intentionally isolates yaw-pitch inversion to study modality information under controlled conditions. Full roll variation is a scope extension and should be addressed in future work or sensitivity analysis.

6. **Why nominal BRDF parameters?**  
   Response: The study evaluates a controlled physically motivated forward model. Material parameters are not claimed to be calibrated target measurements; sensitivity analysis and literature support are needed for stronger material claims.

7. **Why phase63 only for the main image branch?**  
   Response: The image branch is used as a controlled clean-image benchmark. Cross-phase generalization is an important future or supplementary analysis, but the current claim is limited to the tested phase condition.

8. **Does fusion always help?**  
   Response: No. The paper explicitly frames fusion as conditional complementarity. Some feature choices improve tail behavior, while others can worsen worst-case error.

## G. Claim-Evidence-Risk Map

| Claim | Evidence | Risk | Safe wording |
|---|---|---:|---|
| OCS and images provide different constraints. | Unified benchmark; OCS/image/fusion comparisons. | Medium | "within this controlled benchmark" |
| Clean images define an upper-bound case. | ResNet-18 1.69 +/- 0.07 deg; idealized rendering. | Low | "optimistic upper-bound under clean rendered imagery" |
| ResNet clean result is not field performance. | No atmosphere/detector/PSF/real telescope data. | Low | "not a field-performance estimate" |
| OCS remains useful despite lower clean accuracy. | per_part_log 5.91 deg; independent of image pixels. | Medium | "useful complementary photometric constraint" |
| OCS is robust in the benchmark. | Image degradation does not affect OCS branch. | Medium | "independent of image-pixel degradation in this benchmark" |
| Fusion improves tail errors. | Worst-case 9.9 -> 6.6; Hit@5 97.6 -> 99.7. | Low | "improves selected tail errors" |
| Fusion is conditional. | all_raw fusion worst 18.7; OCS-noise gains vary. | Low | "conditional reliability mechanism" |
| Gaussian noise shows image fragility. | sigma=0.01 gives 85.85 deg, Hit@5 2.2%. | Medium | "controlled image-noise stress test" |
| Nominal BRDF parameters are acceptable for controlled simulation. | GGX parameter assignments; planned sensitivity. | Medium | "nominal physically motivated settings" |
| Study is publishable without field validation. | Controlled benchmark, validation checks, explicit limitations. | Medium | "simulation-focused contribution, not field validation" |

## H. Self-review Checklist

1. 是否把 clean image 写成 field performance？  
   **No.** It is consistently described as an idealized upper bound.

2. 是否宣称真实光学验证？  
   **No.** The text explicitly states no real telescope validation.

3. 是否夸大 fusion？  
   **No.** Fusion is conditional complementarity, not universal superiority.

4. 是否把 OCS 写成永远优于图像？  
   **No.** The text states ResNet clean is stronger under ideal images.

5. 是否把 OCS 写成对所有噪声免疫？  
   **No.** OCS is only described as independent of image-pixel degradation in this benchmark.

6. 是否把 `all_raw` 写成实用特征？  
   **No.** It remains a semi-oracle diagnostic upper bound.

7. 是否把 `r = 0.003` 写成 ResNet-pair 证据？  
   **No.** It is not used in the Discussion draft as a ResNet-pair claim.

8. 是否新增了未给出的实验或数值？  
   **No.** Only provided values are used.

9. 是否把 limitations 写得足够诚实？  
   **Yes.** It covers no real validation, clean images, fixed roll, phase63, nominal materials, and simplified degradation.

10. 是否避免引入 ISAR 主线？  
    **Yes.** ISAR is not included.

## I. Questions for Author

1. 0% OCS-noise 的 OCS-only / fusion mean 是否可以补全，以便 Conclusion 或 Discussion 更精确？
2. 哪些 sensitivity / ablation 已有最终值可以进入 Discussion，而不是只作为 future work？
3. 是否已有 ResNet-fusion 图像退化结果？如果没有，建议只写 future work。
4. Limitations 是否独立成小节，还是并入 Discussion 最后一节？
5. 目标期刊优先 Acta Astronautica、ASR、Optics Express 还是 Remote Sensing？不同期刊的 Discussion 语气可微调。
6. 是否计划在投稿前补真实观测，还是明确放入 future work？

