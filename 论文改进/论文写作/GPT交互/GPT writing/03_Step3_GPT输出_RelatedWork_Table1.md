# Step 3 GPT 输出：Related Work + Table 1

## A. Related Work Logic Map

1. Related Work should support the Introduction gap: OCS/light-curve signatures and photometric images have both been studied, but they are often evaluated under different modeling assumptions.
2. The first literature line establishes why optical signatures require BRDF, material, illumination, viewing geometry, and radiometric modeling.
3. The second line covers light-curve or OCS-like attitude inversion, showing that scalar photometry is valuable but usually does not include a resolved-image branch under the same forward model.
4. The third line covers image-based spacecraft pose estimation, showing that resolved imagery can carry strong spatial cues but is sensitive to imaging conditions and sim-to-real assumptions.
5. The fourth line covers fusion and robustness, showing that tightly coupled or feature-level fusion can be useful, but existing fusion work does not directly answer OCS-image photometric complementarity.
6. Table 1 should not claim SOTA. Its purpose is to show the combination position of this work: real STL geometry, nonuniform materials, GGX BRDF, ray-based self-occlusion, both OCS and photometric images, controlled yaw-pitch inversion, and fusion analysis.
7. The manuscript should repeatedly separate “field-validated performance” from “controlled simulation benchmark.”
8. Unverified bibliographic details should remain marked as `[to verify]` until the final reference manager or publisher pages are checked.

中文说明：Related Work 的核心作用不是堆文献，而是证明本文为什么需要“统一 BRDF + 自遮挡 + OCS/image 双模态 + 受控反演”这个组合。

## B. Section Outline

### 2.1 Optical signatures and BRDF modeling of space objects

- Topic sentence: Optical signatures of space objects are governed by geometry, material reflectance, illumination, viewing direction, phase angle, and radiometric effects.
- Core references: Yang et al. `[to verify: prompt says 2024 Photonics; web search suggests Photonics 2025]`; Lu/Yao 2024 Universe; Fankhauser et al. 2023 AJ.
- Gap: These works support BRDF/material/brightness modeling, but they usually focus on reflectance characterization or brightness prediction rather than a closed OCS-image attitude inversion benchmark.
- Distinction: This work uses BRDF modeling as a shared forward-model basis for both OCS signatures and photometric images.

### 2.2 Light-curve and OCS-based attitude inversion

- Topic sentence: Light curves and OCS-like scalar photometric signatures remain attractive for attitude inference because they are low-dimensional and can be collected across observation geometries.
- Core references: Wang et al. 2024 ASR; Burton et al. 2024 ASR; Kumar et al. 2025 Acta Astronautica.
- Gap: These works motivate photometry-based attitude inversion but generally do not compare scalar photometric constraints with resolved image constraints generated from the same BRDF/self-occlusion model.
- Distinction: This work evaluates OCS-only inversion alongside image-only and fusion models under a shared simulation protocol.

### 2.3 Photometric image simulation and image-based pose estimation

- Topic sentence: Resolved or rendered images can provide spatial attitude cues that scalar photometry cannot preserve.
- Core references: Dickinson 2025 RIT PhD; optional Sosa 2025 `[to verify]`.
- Gap: Image-based pose work often focuses on visual pose estimation and sim-to-real transfer, but not on how image cues compare with OCS/light-curve cues under identical scattering assumptions.
- Distinction: This work treats clean synthetic image performance as an upper-bound benchmark and explicitly evaluates degradation sensitivity.

### 2.4 Multi-modal fusion and robustness under observation degradation

- Topic sentence: Fusion can improve robustness when modalities fail differently, but its benefit depends on modality quality, task setting, and fusion design.
- Core references: Liu et al. 2024 Remote Sensing; optional Xiong 2025 `[to verify]`.
- Gap: Existing fusion work supports feature-level/tightly coupled fusion ideas, but does not directly address OCS-image photometric fusion with shared BRDF and self-occlusion.
- Distinction: This work frames fusion as conditional complementarity rather than a universally superior architecture.

## C. Related Work Draft

### 2.1 Optical signatures and BRDF modeling of space objects

Optical signatures of space objects are shaped by the coupled effects of target geometry, surface material, illumination direction, viewing direction, phase angle, and visibility. BRDF-based modeling is therefore central to physically meaningful satellite photometry, because it links surface reflectance behavior to observed brightness or image intensity under varying geometries. Studies of satellite material reflectance and goniopolarimetric behavior provide experimental and semi-empirical support for using BRDF models, including Cook-Torrance-type descriptions, to represent satellite surface scattering [Yang et al., 2024/2025, to verify]. Large-scale satellite brightness studies further show that BRDF-based photometric models can explain and predict the brightness behavior of LEO constellation satellites using real observation campaigns [Lu/Yao, 2024]. Radiometric analyses also emphasize that satellite optical brightness can depend on effects beyond direct sunlight, including Earth-reflected illumination and other observation-dependent contributions [Fankhauser et al., 2023].

These studies motivate the need for physically consistent optical modeling, but their primary emphasis is usually material characterization, brightness prediction, radiometric modeling, or observation interpretation. They do not directly answer how scalar OCS signatures and resolved photometric images behave when both are generated from the same geometry, material assignment, BRDF, attitude convention, and self-occlusion assumptions. The present work builds on this BRDF-based photometric modeling line, but uses it as a common forward-model foundation for a controlled OCS-image attitude inversion benchmark rather than as an end point for brightness prediction alone.

### 2.2 Light-curve and OCS-based attitude inversion

Light curves and OCS-like scalar photometric signatures have long been attractive for attitude inference because they are compact, interpretable, and can be obtained across multiple observation geometries. Laboratory-tested photometry datasets and simulated photometric signatures have been used to investigate attitude inversion from scalar brightness measurements [Wang et al., 2024]. Optimization-based approaches, including particle swarm strategies, further demonstrate that light-curve attitude estimation can be formulated as a search problem over attitude states when object shape, reflectance, and illumination geometry are available or assumed [Burton et al., 2024]. Recent digital-twin and sequential-comparison strategies for LEO uncontrolled objects also support the broader use of light curves for object understanding and attitude-related inference [Kumar et al., 2025].

The limitation relevant to this paper is not that scalar photometry is unimportant, but that scalar photometric inversion alone cannot reveal how much additional or different information is contained in resolved photometric images. Light-curve studies often focus on photometric sequence matching, optimization, or digital-twin comparison, while the image branch is absent or generated under different assumptions. As a result, they do not isolate when OCS-like measurements and image-based cues are complementary. This work retains the interpretability and multi-geometry advantages of OCS signatures, but places OCS-only inversion in the same benchmark as image-only, late-fusion, and feature-fusion models.

### 2.3 Photometric image simulation and image-based pose estimation

Resolved and rendered images provide spatial cues that scalar signatures cannot preserve, including projected shape, component layout, shadow structure, brightness distribution, and specular patterns. Image-based satellite pose estimation studies have increasingly used synthetic imagery and deep learning to estimate spacecraft pose from resolved ground-based or simulated imagery. Dickinson’s 2025 dissertation, for example, addresses 6DOF satellite pose estimation from resolved ground-based imagery using synthetic training and image-quality analysis [Dickinson, 2025]. Such work highlights both the power of resolved imagery and the difficulty of sim-to-real transfer under blur, noise, illumination variation, and limited image quality.

For the present paper, image-based pose estimation provides an important contrast to scalar OCS inversion. Clean synthetic photometric images may contain strong attitude cues, and a high-capacity image model can exploit these cues effectively. However, this does not mean that clean-image performance is a direct estimate of field performance. Ground-based imagery can be affected by atmospheric seeing, tracking error, sensor noise, optical blur, low resolution, background contamination, and phase-angle changes. Existing image-pose studies therefore motivate the need to separate idealized image upper-bound behavior from degraded-observation robustness. The present work follows this distinction by treating clean rendered images as a controlled upper-bound setting and by explicitly evaluating image degradation sensitivity.

### 2.4 Multi-modal fusion and robustness under observation degradation

Multi-modal fusion is often motivated by the possibility that different sensors or feature streams fail under different conditions. In spacecraft attitude estimation, tightly coupled visual-inertial methods illustrate how feature-level fusion can use raw visual and inertial information to improve robustness compared with more loosely coupled designs [Liu et al., 2024]. This literature supports the general idea that fusion should be evaluated not only by mean accuracy but also by robustness, failure modes, and the information carried by each modality.

However, visual-inertial fusion is not the same problem as OCS-image photometric fusion. The latter combines a low-dimensional scalar photometric constraint with a resolved photometric image generated by the same scattering physics. Existing fusion studies do not directly answer when OCS and images are complementary under a shared BRDF, geometry, material, attitude, and self-occlusion model. The present work is therefore positioned as a controlled simulation benchmark rather than a claim of field-validated performance. Its comparison focuses on modality information and robustness, not on declaring a universally superior sensor or fusion architecture.

## D. Table 1 Draft

| Work | Geometry | BRDF | Self-occlusion | Image | OCS/light curve | Attitude inversion | Fusion | External validation |
|---|---|---|---|---|---|---|---|---|
| Yang et al. 2024/2025 Photonics `[to verify]` | Material samples / satellite material surfaces `[to verify]` | Semi-empirical pBRDF / Cook-Torrance-related models `[to verify]` | Not central / `[to verify]` | No resolved attitude image branch | Reflectance characterization, not OCS inversion | No attitude inversion benchmark | No | Laboratory/material measurement `[to verify]` |
| Lu/Yao 2024 Universe | LEO constellation satellite / Starlink model | BRDF-based photometric model | Observation geometry considered; detailed self-occlusion `[to verify]` | No resolved inversion image branch | Massive photometric observations / brightness modeling | Not primarily attitude inversion | No | Real photometric observations |
| Wang et al. 2024 ASR | Space debris / lab photometry target `[to verify]` | Reflectance assumptions `[to verify]` | `[to verify]` | No resolved image branch | Laboratory-tested photometry dataset | Yes, photometry-based attitude inversion | No | Laboratory photometry dataset |
| Burton et al. 2024 ASR | Known object model / space debris or satellite `[to verify]` | Reflective properties assumed | `[to verify]` | No | Light curve | Yes, particle swarm optimizer attitude estimation | No | Simulation / light-curve experiments `[to verify]` |
| Dickinson 2025 RIT PhD | CAD/satellite models; resolved ground-based imagery | Image simulation / HFWO synthetic imagery `[to verify]` | Included through rendering/simulation `[to verify]` | Yes, resolved imagery | No OCS/light-curve branch | Yes, 6DOF image-based pose estimation | No OCS-image fusion | Synthetic training and resolved imagery evaluation `[to verify]` |
| Kumar et al. 2025 Acta Astronautica | Digital twin / LEO uncontrolled objects `[to verify]` | Light-curve modeling assumptions `[to verify]` | `[to verify]` | No resolved image branch | Light curves / sequential comparison | Attitude/object understanding `[to verify]` | No | Observation/digital-twin comparison `[to verify]` |
| Liu et al. 2024 Remote Sensing | Spacecraft attitude estimation setting | Not BRDF-based | Not relevant | Visual/star-sensor features `[to verify]` | No OCS/light curve | Yes, spacecraft attitude estimation | Visual-inertial tightly coupled fusion | Simulation and experimental evaluations `[to verify]` |
| Fankhauser et al. 2023 AJ | Satellite brightness geometry | Radiometric brightness model; sunlight and earthshine `[to verify]` | Not attitude-inversion focus | No resolved inversion image branch | Brightness modeling | No attitude inversion benchmark | No | Radiometric/astronomical analysis `[to verify]` |
| This work | Real satellite STL; yaw-pitch under fixed roll | GGX/Cook-Torrance; nonuniform materials | Analytical ray-based self-occlusion | Yes, rendered photometric images | Yes, multi-geometry OCS signatures | Yes, controlled OCS/image/fusion yaw-pitch inversion | Late fusion and feature fusion | No real optical validation; analytical/rendering consistency and controlled sensitivity tests |

## E. Citation Placeholder Map

| Placeholder | Candidate references | Used for | Verification needed |
|---|---|---|---|
| `[CITATION: satellite material BRDF]` | Yang et al. 2024/2025 Photonics | Material BRDF, goniopolarimetric/surface reflectance, Cook-Torrance-type model support | Year, exact title, model list, material types |
| `[CITATION: BRDF-based satellite photometry]` | Lu/Yao 2024 Universe | BRDF-based photometric modeling of Starlink/LEO constellation satellites from observations | Exact author order, whether “Lu Yao” is author or name order |
| `[CITATION: satellite optical brightness]` | Fankhauser et al. 2023 AJ | Earthshine, sunlight, radiometric brightness complexity | Exact journal issue/pages and scope |
| `[CITATION: laboratory photometry attitude inversion]` | Wang et al. 2024 ASR | Lab-tested photometry dataset and attitude inversion | Dataset target, inversion task, BRDF assumptions |
| `[CITATION: particle swarm light-curve attitude estimation]` | Burton et al. 2024 ASR | Optimization-based light-curve attitude estimation | Exact assumptions and validation setting |
| `[CITATION: light-curve digital twin comparison]` | Kumar et al. 2025 Acta Astronautica | Sequential light-curve comparison / digital twin for LEO uncontrolled objects | Final publication metadata and task details |
| `[CITATION: image-based satellite pose estimation]` | Dickinson 2025 RIT PhD | Resolved ground-based imagery, synthetic training, 6DOF pose estimation | Which details to cite in main text vs related work |
| `[CITATION: tightly coupled spacecraft fusion]` | Liu et al. 2024 Remote Sensing | Feature-level/tightly coupled fusion analogy | Clarify it is visual-inertial, not OCS-image |
| `[CITATION: image degradation or image fusion]` | Xiong 2025 `[to verify]` or other sources | Image quality degradation / image fusion robustness | Need actual source details |

## F. Claim-Evidence-Risk Map

| Claim | Evidence / Literature support | Risk | Safe wording |
|---|---|---:|---|
| BRDF modeling is necessary for physically meaningful satellite photometry. | Yang; Lu/Yao; Fankhauser. | Low | "BRDF-based modeling is central to physically meaningful satellite photometry." |
| Satellite brightness depends on more than direct solar reflection. | Fankhauser 2023 AJ; Lu/Yao 2024 Universe. | Medium | "can depend on effects beyond direct sunlight..." |
| Light curves support attitude-related inference. | Wang 2024; Burton 2024; Kumar 2025. | Low | "have been used to investigate attitude inference..." |
| Light-curve works do not usually compare with resolved images under the same forward model. | Based on provided literature roles; needs final check. | Medium | "often do not..." rather than "never." |
| Resolved images carry spatial cues useful for pose estimation. | Dickinson 2025; image-pose literature. | Low | "can provide spatial cues..." |
| Clean image performance should not be interpreted as field performance. | Project boundary + Dickinson-type sim-to-real/imaging challenges. | Low | "should be interpreted as an upper-bound benchmark." |
| Fusion can improve robustness when modalities fail differently. | Liu 2024 general fusion; project results. | Medium | "can improve robustness when..." |
| Existing fusion literature does not directly answer OCS-image BRDF-based complementarity. | Liu is visual-inertial, not OCS-image; project gap. | Medium | "does not directly answer..." |
| This work combines OCS and photometric images under shared BRDF/self-occlusion assumptions. | Project method chain. | Low | "This work is positioned as..." |
| This work is not field-validated. | Project limitation. | Low | "controlled simulation benchmark rather than field-validated performance." |

## G. Self-review Checklist

1. 是否发明了引用？  
   **No.** 引用使用给定文献名或占位符；不确定信息标注 `[to verify]`。

2. 是否把本文说成 SOTA？  
   **No.** 文中没有使用 state-of-the-art 或 first。

3. 是否夸大 fusion？  
   **No.** Fusion 被写成 conditional complementarity，不是 universal superiority。

4. 是否承认无真实光学验证？  
   **Yes.** Related Work 明确将本文定位为 controlled simulation benchmark。

5. 是否覆盖了 light-curve/OCS、BRDF、image pose、fusion 四条线？  
   **Yes.** 四个小节分别覆盖。

6. 是否把 Table 1 的不确定信息标注为待核对？  
   **Yes.** 多处用 `[to verify]` 或 `[需要作者核对]`。

## H. Questions for Author

1. Yang 文献年份是否应写 2024 还是 2025？我检索到的 Photonics 条目像是 2025，需要你核对最终引用。
2. Table 1 是否要保留 Dickinson 2025 PhD dissertation，还是换成其 AMOS 2024 conference version 作为更正式会议引用？
3. Wang 2024 ASR 的目标、BRDF 假设和验证形式是否有你本地阅读笔记可补充？
4. Kumar 2025 Acta Astronautica 是否已有最终 PDF 或 DOI 信息，用于减少 `[to verify]`？
5. Table 1 是否需要扩展到补充材料，正文只保留 8-9 篇核心工作？

