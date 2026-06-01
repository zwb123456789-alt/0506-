# Step 3 Output: Related Work + Table 1

> 本阶段任务：基于 Step 2 Introduction 的 gap 段，生成 Related Work 四小节英文初稿、Table 1 文献方案对比表、引用占位符映射和自检清单。

---

## A. Related Work Logic Map

1. Introduction Para 3 指出两个 gap：(a) 缺少统一物理框架让 OCS 和图像共享 BRDF/几何/遮挡；(b) 缺少对各模态在不同观测质量下可靠性的系统评估。
2. §2.1 建立 BRDF/光学特征建模的文献基础 → 说明现有 BRDF 工作重点在 photometric prediction 而非闭环到 attitude inversion benchmark。
3. §2.2 建立 OCS/light-curve 姿态反演的文献基础 → 说明这类工作通常不与 resolved image 在同一物理模型下公平比较。
4. §2.3 建立 image-based pose estimation 的文献基础 → 说明图像方法通常不与 OCS/light-curve 在同一 BRDF/遮挡假设下对比。
5. §2.4 建立 multi-modal fusion 的文献基础 → 说明现有 fusion 文献不直接回答 OCS-image 在统一仿真下何时互补。
6. 四节合力支撑 Introduction 的 "two critical gaps"，为 Method 的统一框架提供动机。
7. Table 1 用一张表直观展示本文的组合位置：不是单点 SOTA，而是唯一同时覆盖 real STL + GGX BRDF + self-occlusion + OCS + image + controlled inversion + fusion 的 benchmark。
8. 每节末尾的 "distinction" 句直接呼应 Introduction 的贡献点，形成闭环。

---

## B. Section Outline

### §2.1 Optical Signatures and BRDF Modeling of Space Objects

- **Topic sentence:** The optical signatures of space objects depend on the interplay of geometry, surface material reflectance, illumination and viewing directions, and self-occlusion configuration.
- **Core references:** Yang et al. 2024 (satellite material BRDF / Cook-Torrance); Lu 2024 (Starlink BRDF photometric modeling); Fankhauser et al. 2023 (satellite optical brightness / radiometric complexity).
- **Gap:** These works advance BRDF characterization and brightness prediction but do not close the loop to a controlled OCS-image joint attitude inversion benchmark.
- **Distinction:** This work adopts GGX/Cook-Torrance BRDF with nonuniform material assignment and uses it as the shared physical basis for both OCS computation and image rendering.

### §2.2 Light-Curve and OCS-Based Attitude Inversion

- **Topic sentence:** Scalar photometric signatures such as light curves and OCS values encode attitude-dependent information and have been used for attitude estimation through template matching, optimization, and learning-based methods.
- **Core references:** Wang et al. 2024 (laboratory photometry dataset for attitude inversion); Burton et al. 2024 (light curve attitude estimation via particle swarm); Kumar et al. 2025 (digital twin light-curve sequential comparison).
- **Gap:** These approaches typically do not compare against resolved photometric images generated under the same BRDF and self-occlusion assumptions.
- **Distinction:** This work generates OCS and images from the same forward model and benchmarks OCS-only inversion against image-only and fusion approaches under consistent evaluation.

### §2.3 Photometric Image Simulation and Image-Based Pose Estimation

- **Topic sentence:** Resolved or rendered photometric images provide rich spatial cues—silhouette, shadow, brightness distribution—that enable high-accuracy pose estimation when image quality is sufficient.
- **Core references:** Dickinson 2025 (sim-to-real 6DOF ground-based satellite pose); optionally Sosa 2025 (ViT-based pose).
- **Gap:** Image-based pose methods focus on visual accuracy and sim-to-real transfer but typically do not compare against scalar OCS/light-curve constraints generated under the same physical scattering model, nor do they systematically evaluate fragility under observation degradation.
- **Distinction:** This work quantifies the clean-image upper bound and demonstrates its fragility under controlled degradation, positioning image-based results as idealized benchmarks rather than field performance estimates.

### §2.4 Multi-Modal Fusion and Robustness Under Observation Degradation

- **Topic sentence:** Multi-modal fusion can improve estimation robustness when constituent modalities exhibit complementary failure modes, but the benefit depends on modality quality and fusion architecture.
- **Core references:** Liu et al. 2024 (tightly coupled visual-inertial fusion—not OCS-image, but supports fusion concept); optionally Xiong 2025 (multi-exposure image fusion / observation quality).
- **Gap:** Existing fusion literature does not directly address when OCS and photometric images provide complementary attitude constraints under a unified BRDF/self-occlusion simulation, nor does it quantify how fusion value changes with observation quality.
- **Distinction:** This work evaluates late fusion and feature fusion under both clean and degraded conditions, revealing that complementarity is conditional on observation quality rather than universally guaranteed.

---

## C. Related Work Draft

### 2.1 Optical Signatures and BRDF Modeling of Space Objects

The optical signatures of space objects arise from the interaction of solar illumination with surface geometry and material reflectance properties. Accurate modeling of these signatures requires specifying the bidirectional reflectance distribution function (BRDF) for each surface component, accounting for the observation geometry defined by the Sun-object-observer configuration, and considering self-occlusion effects in non-convex geometries. Yang et al. [Yang et al., 2024] investigated the goniopolarimetric properties of satellite surface materials and demonstrated that microfacet BRDF models such as Cook-Torrance provide physically grounded descriptions of metallic and dielectric spacecraft surfaces [to verify: specific Cook-Torrance vs GGX distinction in Yang 2024]. Lu [Lu, 2024] developed BRDF-based photometric models for Starlink and other LEO constellation satellites, showing that realistic brightness predictions require careful treatment of material heterogeneity and observation geometry [to verify: whether Lu 2024 uses Cook-Torrance or other BRDF model]. Fankhauser et al. [Fankhauser et al., 2023] characterized satellite optical brightness under varying phase angles and highlighted the complexity introduced by earthshine, atmospheric extinction, and sensor response in real photometric observations.

These studies establish the physical foundations for satellite optical signature modeling. However, they primarily focus on photometric prediction, material characterization, or brightness catalog construction, rather than closing the loop to a controlled attitude inversion benchmark where OCS and resolved images are jointly generated and compared under the same BRDF and self-occlusion assumptions. The present work adopts a GGX/Cook-Torrance BRDF with nonuniform material assignment across three satellite components and uses this shared physical model as the basis for both facet-level OCS integration and pixel-level photometric image rendering.

### 2.2 Light-Curve and OCS-Based Attitude Inversion

Scalar photometric signatures—including light curves and optical cross section (OCS) values—encode attitude-dependent information through the integrated BRDF response over all visible and illuminated surface elements. These low-dimensional measurements are obtainable with modest aperture telescopes across multiple observation geometries, making them attractive for operational attitude monitoring. Wang et al. [Wang et al., 2024] constructed a laboratory-tested photometry dataset and demonstrated attitude inversion from controlled light-curve measurements [to verify: specific inversion method used]. Burton et al. [Burton et al., 2024] applied particle swarm optimization to estimate satellite attitude from simulated light curves, showing that optimization-based approaches can recover attitude parameters from scalar photometric time series. Kumar et al. [Kumar et al., 2025] proposed a digital twin framework using sequential light-curve comparison for LEO uncontrolled object characterization, demonstrating the value of physics-based forward models in attitude understanding.

A common limitation of these approaches is that they typically do not compare their OCS or light-curve inversion results against resolved photometric image-based methods generated under the same physical scattering assumptions. This makes it difficult to assess the relative information content of scalar versus spatially resolved optical measurements for attitude estimation. The present work addresses this gap by generating both OCS signatures and photometric images from the same unified forward model and benchmarking OCS-only inversion against image-only and fusion approaches under consistent data splits and evaluation metrics.

### 2.3 Photometric Image Simulation and Image-Based Pose Estimation

Resolved or rendered photometric images provide spatially distributed brightness information that encodes shape silhouettes, shadow boundaries, component layout, and specular highlight positions—cues that are absent from scalar OCS measurements. Recent advances in deep learning have enabled high-accuracy spacecraft pose estimation from synthetic and real images. Dickinson [Dickinson, 2025] addressed sim-to-real 6DOF satellite pose estimation from ground-based resolved imagery, demonstrating both the potential and the challenges of transferring models trained on rendered data to real telescope observations [to verify: specific network architecture and reported accuracy]. These works highlight that image-based methods can achieve excellent pose accuracy when high-quality resolved images are available, but their performance is sensitive to the domain gap between synthetic training data and real observations affected by atmospheric turbulence, sensor noise, and tracking errors.

A key distinction of the present work is that it does not claim image-based results as field performance estimates. Instead, the clean synthetic image results are explicitly positioned as an idealized upper bound for image-based attitude inversion. Furthermore, by generating images under the same BRDF and self-occlusion model used for OCS computation, this work enables direct comparison of the attitude information carried by scalar OCS versus resolved images—a comparison that is typically absent in image-only pose estimation studies.

### 2.4 Multi-Modal Fusion and Robustness Under Observation Degradation

Multi-modal fusion aims to combine complementary information sources to improve estimation accuracy or robustness. In spacecraft state estimation, fusion architectures range from prediction-level averaging to feature-level concatenation and end-to-end joint training. Liu et al. [Liu et al., 2024] demonstrated tightly coupled visual-inertial fusion for spacecraft attitude estimation, showing that feature-level integration can outperform single-modality approaches when both modalities provide reliable measurements [to verify: whether Liu 2024 addresses degradation robustness]. However, this work addresses visual-inertial fusion rather than OCS-image photometric fusion, and the underlying physical models differ substantially.

A critical question that remains underexplored is whether fusion benefits are universal or conditional on observation quality. When one modality provides highly accurate information (e.g., clean high-resolution images), the marginal contribution of a second modality may be minimal. Conversely, when one modality degrades (e.g., images corrupted by noise or atmospheric effects), the complementary modality may become essential for maintaining estimation reliability. The present work directly addresses this question by evaluating OCS-image fusion under both clean and degraded conditions within a unified simulation framework, revealing that multi-modal complementarity is conditional on observation quality rather than universally guaranteed.

---

## D. Table 1 Draft

| Work | Geometry | BRDF | Self-occlusion | Image | OCS / Light curve | Attitude inversion | Fusion | External validation |
|---|---|---|---|---|---|---|---|---|
| Yang et al., 2024 | Satellite materials [to verify] | Cook-Torrance / microfacet | Not addressed [to verify] | Not used | Not used for inversion | No | No | Laboratory measurements [to verify] |
| Lu, 2024 | Starlink / LEO satellites | BRDF-based [to verify model] | Not explicitly modeled [to verify] | Not used | Photometric prediction | No attitude inversion | No | Real photometric observations [to verify] |
| Fankhauser et al., 2023 | Multiple satellites | Empirical / physical [to verify] | Not explicitly [to verify] | Not used | Brightness characterization | No | No | Real observations [to verify] |
| Wang et al., 2024 | Laboratory model [to verify] | Simplified [to verify] | Implicit in lab setup | Not used | Light-curve dataset | Attitude inversion [to verify method] | No | Laboratory validation |
| Burton et al., 2024 | Simulated geometry [to verify] | Simplified [to verify] | [to verify] | Not used | Simulated light curves | PSO-based estimation | No | Simulation only [to verify] |
| Kumar et al., 2025 | Digital twin / LEO objects | [to verify] | [to verify] | Not used | Sequential light-curve comparison | Object characterization | No | [to verify] |
| Dickinson, 2025 | Real satellite CAD [to verify] | Rendering-based [to verify] | Implicit in rendering | Resolved ground-based images | Not used | 6DOF pose estimation | No | Sim-to-real transfer [to verify] |
| Liu et al., 2024 | Spacecraft [to verify] | N/A (visual-inertial) | N/A | Visual images | N/A | Attitude estimation | Visual-inertial fusion | [to verify] |
| **This work** | **Real satellite STL** | **GGX/Cook-Torrance, nonuniform** | **Analytical ray-based** | **Photometric rendering (exact BRDF)** | **Multi-geometry OCS** | **Yaw-pitch controlled benchmark** | **Late + feature fusion** | **Analytical closure + rendering consistency + controlled sensitivity; no real telescope** |

---

## E. Citation Placeholder Map

| Placeholder | Candidate References | Used For | Verification Needed |
|---|---|---|---|
| [Yang et al., 2024] | Yang et al., 2024, Photonics | Satellite material BRDF, Cook-Torrance/GGX basis | Confirm exact BRDF model used; confirm journal is Photonics |
| [Lu, 2024] | Lu Yao, 2024, Universe | Starlink BRDF photometric modeling | Confirm BRDF model type; confirm single-author or multi-author |
| [Fankhauser et al., 2023] | Fankhauser et al., 2023, AJ | Satellite optical brightness, radiometric complexity | Confirm journal (Astronomical Journal?); confirm scope |
| [Wang et al., 2024] | Wang et al., 2024, Advances in Space Research | Laboratory photometry dataset, attitude inversion | Confirm inversion method; confirm it is ASR |
| [Burton et al., 2024] | Burton et al., 2024, Advances in Space Research | Light curve attitude estimation, PSO | Confirm journal; confirm PSO method |
| [Kumar et al., 2025] | Kumar et al., 2025, Acta Astronautica | Digital twin, light-curve sequential comparison | Confirm journal; confirm LEO focus |
| [Dickinson, 2025] | Dickinson, 2025, RIT PhD thesis | Sim-to-real 6DOF satellite pose, ground-based imagery | Confirm it is PhD thesis; confirm institution |
| [Liu et al., 2024] | Liu et al., 2024, Remote Sensing | Tightly coupled visual-inertial fusion | Confirm journal; confirm it is NOT OCS-image fusion |
| [CITATION: SSA overview] | To be determined by author | Space situational awareness importance | Author to select appropriate SSA review paper |
| [CITATION: observation degradation effects] | To be determined by author | Atmospheric/sensor effects on optical observations | Author to select (e.g., Hardy 1998, Tyson 2015, or domain-specific) |

---

## F. Claim-Evidence-Risk Map

| # | Claim in Related Work | Evidence / Basis | Risk | Mitigation |
|---|---|---|---|---|
| 1 | Existing BRDF studies focus on photometric prediction, not joint inversion benchmark | Survey of Yang/Lu/Fankhauser scope | Medium — reviewer may cite a paper we missed | Use "typically" and "to our knowledge"; add [to verify] for uncertain claims |
| 2 | Light-curve inversion studies do not compare against resolved images under same BRDF | Survey of Wang/Burton/Kumar scope | Medium — some recent work may do partial comparison | Use "typically do not" rather than "never" |
| 3 | Image-based pose methods do not enforce OCS consistency | Survey of Dickinson and image-pose literature | Low-Medium — image methods rarely use OCS | Safe with "typically" qualifier |
| 4 | Clean-image performance is an upper bound | Our experimental evidence (ResNet 1.69° vs 85.85° under noise) | Low — well-supported by our data | State clearly in §2.3 distinction |
| 5 | Existing fusion literature does not address OCS-image conditional complementarity | Survey of Liu 2024 and general fusion literature | Medium — reviewer may cite niche paper | Use "has not been systematically quantified in this context" |
| 6 | Cook-Torrance/GGX is appropriate for satellite materials | Yang 2024 + general PBR literature | Low | Supported by materials science consensus |
| 7 | Multi-geometry OCS improves attitude discrimination | Our experimental evidence (single vs concat5) | Low — well-supported | Not a Related Work claim per se; only referenced in distinction |
| 8 | Liu 2024 is visual-inertial, not OCS-image | Paper scope | Low — factual | Verify paper scope is correctly characterized |

---

## G. Self-review Checklist

| # | Question | Answer |
|---|---|---|
| 1 | Did I invent any citations? | ✅ No — all references are from the provided list; uncertain details marked [to verify] |
| 2 | Did I claim this work is SOTA? | ✅ No — positioned as "controlled benchmark" throughout |
| 3 | Did I overstate fusion benefits? | ✅ No — §2.4 explicitly states "conditional on observation quality rather than universally guaranteed" |
| 4 | Did I acknowledge no real optical validation? | ✅ Yes — Table 1 "This work" row and §2.3 distinction both state this |
| 5 | Did I cover all four literature lines (BRDF, OCS/LC inversion, image pose, fusion)? | ✅ Yes — §2.1–2.4 |
| 6 | Did I mark uncertain Table 1 information as [to verify]? | ✅ Yes — 20+ cells marked |

---

## H. Questions for Author

1. **Yang 2024 细节**：该文是否明确使用了 GGX 微表面模型？还是仅用 Cook-Torrance 原始形式？这影响 §2.1 中 "Cook-Torrance/GGX" 的表述精度。

2. **Lu 2024 作者信息**：是单作者（Lu Yao）还是多作者？期刊确认是 Universe？需要核对以确保引用格式正确。

3. **Table 1 补充文献**：是否需要在 Table 1 中加入可选文献（如 Sosa 2025 ViT pose、Marto 2024 hyperspectral、Groves 2025 self-supervised）？还是保持当前 8+1 行的精简版本？

4. **§2.4 补充**：是否需要引用 Xiong 2025（multi-exposure image fusion）来加强 "observation quality degradation" 的文献支撑？还是当前 Liu 2024 单篇足够？

5. **Related Work 长度**：当前约 1100 words，是否合适？Acta Astronautica 通常接受 800-1500 words 的 Related Work。

---

*Step 3 完成。等待作者核对文献细节和 Table 1 后进入 Step 4: Method 初稿。*
