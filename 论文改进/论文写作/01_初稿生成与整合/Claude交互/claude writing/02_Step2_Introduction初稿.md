# Step 2 Output: Introduction Structure and Drafts

> 本阶段任务：基于 Step 1 返修版主线，写 Introduction 的逻辑地图、段落规划、两个版本初稿（保守版 A + 平衡版 B）、自检清单和作者确认项。

---

## 1. Introduction Logic Map

```
Field Need (SSA + optical attitude estimation)
    │
    ├── Two optical modalities: OCS (scalar, low-cost, multi-geometry)
    │                           Image (resolved, rich spatial cues)
    │
    ├── Gap 1: typically modeled separately, no unified physical framework
    │
    ├── Gap 2: no systematic evaluation of when each modality is reliable
    │          and when fusion provides genuine complementary benefit
    │
    ├── Present Study: unified BRDF-driven simulation + controlled benchmark
    │   ├── Clean-image upper bound (ResNet 1.69°)
    │   ├── Fragility under degradation (1% noise → 85.9°)
    │   ├── OCS robustness (5.91° unaffected)
    │   └── Conditional fusion (tail improvement + degradation gain)
    │
    └── Contributions (4) + Boundary (simulation-focused, yaw-pitch, no field data)
```

---

## 2. Paragraph Plan

| Para | Function | Topic Sentence Direction | Length |
|---|---|---|---|
| 1 | Field need & task definition | Space object attitude estimation from optical observations is essential for SSA... | ~150 words |
| 2 | Two optical modalities | Two complementary optical information sources are available... | ~160 words |
| 3 | Technical gap | Despite progress in both directions, existing studies typically model OCS and images separately... | ~180 words |
| 4 | Present study & key insight | In this work, we develop a unified BRDF-driven simulation framework... | ~200 words |
| 5 | Contributions & boundary | The main contributions of this study are... | ~160 words |

---

## 3. Version A: Conservative Reviewer-Safe Introduction

Space object attitude estimation from ground-based optical observations is a fundamental task in space situational awareness (SSA). Accurate knowledge of a resident space object's orientation enables conjunction assessment, anomaly detection, and mission planning [CITATION: SSA overview]. Among the available sensing modalities, optical observations—including photometric brightness measurements and resolved imaging—provide non-cooperative, passive characterization capabilities applicable to both cooperative and non-cooperative targets [CITATION: optical space object characterization].

Two principal optical information sources carry attitude-dependent signatures. The first is the optical cross section (OCS), a scalar quantity proportional to the total reflected solar flux received by a ground-based detector. OCS measurements are low-cost, obtainable with modest aperture telescopes, and naturally available across multiple observation geometries as the object traverses its orbit [CITATION: light-curve photometry]. The second is the resolved photometric image, which captures spatially distributed brightness patterns encoding shape, shadow boundaries, and component-level reflectance variations [CITATION: image-based spacecraft pose estimation]. Each modality encodes attitude information through different physical mechanisms: OCS integrates the bidirectional reflectance distribution function (BRDF) over all visible surface elements, while images preserve the spatial distribution of reflected radiance.

Despite progress in both light-curve inversion [CITATION: light-curve inversion methods] and image-based pose estimation [CITATION: CNN pose estimation], existing studies typically model these two modalities separately. Light-curve and OCS analyses often employ simplified BRDF assumptions without generating corresponding images, while image-based methods rarely incorporate explicit OCS consistency or multi-geometry photometric constraints. A unified physical framework—where OCS and images share the same geometry, nonuniform material assignment, BRDF model, attitude parameterization, and self-occlusion treatment—has not been systematically established for controlled attitude inversion benchmarking. Furthermore, it remains unclear under what observation conditions each modality provides reliable attitude constraints: high-capacity image models may achieve excellent performance on clean synthetic data, but the transferability of such performance to degraded observation conditions—where atmospheric turbulence, sensor noise, tracking errors, and point-spread function variations are present—has not been systematically quantified in this context [CITATION: observation degradation effects].

In this work, we develop a unified BRDF-driven simulation framework that generates physically consistent OCS signatures and photometric images from the same satellite STL geometry, nonuniform GGX/Cook-Torrance material model, and ray-traced self-occlusion. This framework enables a controlled attitude inversion benchmark comparing OCS-only, image-only, and multi-modal fusion approaches under both ideal and degraded conditions. Our controlled experiments reveal three key findings: (1) under clean synthetic images, a ResNet-18 model achieves 1.69 ± 0.07° mean angular error, establishing an upper-bound for image-based inversion; (2) this performance is highly fragile—1% additive Gaussian noise degrades the model to 85.85° mean error; and (3) OCS-only inversion provides a stable 5.91° constraint unaffected by image quality, while OCS-image fusion conditionally improves tail errors from 9.9° to 6.6° under clean conditions and provides increasing compensation as OCS quality degrades. These findings demonstrate that multi-modal complementarity is conditional on observation quality rather than universally guaranteed.

The main contributions of this study are fourfold: (1) a unified BRDF-driven forward model generating physically consistent OCS and photometric images from shared geometry, material, and occlusion assumptions; (2) a controlled yaw-pitch attitude inversion benchmark systematically comparing OCS-only, image-only, and fusion methods under consistent evaluation protocols; (3) quantification of the clean-image upper bound and its fragility under controlled degradation tests; and (4) demonstration that OCS provides robust photometric constraints within the simulation domain and that fusion gain is conditional on observation quality. The study is simulation-focused and does not include real optical telescope validation; the current benchmark estimates yaw and pitch under fixed roll. These boundaries ensure a controlled and interpretable evaluation while motivating future field validation under atmospheric and sensor degradation.

---

## 4. Version B: Balanced Submission Introduction

Accurate attitude estimation of resident space objects is essential for space situational awareness, enabling conjunction risk assessment, on-orbit anomaly diagnosis, and debris characterization [CITATION: SSA overview]. Ground-based optical observations offer passive, non-cooperative sensing capabilities that complement radar and telemetry-based approaches [CITATION: optical space object characterization]. A central challenge is to extract reliable attitude information from optical signatures that depend jointly on the object's geometry, surface materials, self-occlusion configuration, and the observation geometry defined by the Sun-object-observer relationship.

Two distinct optical modalities carry attitude-dependent information. Optical cross section (OCS) measurements—scalar quantities representing the total reflected solar flux—are obtainable at low cost across multiple observation geometries and provide physically interpretable photometric constraints [CITATION: light-curve photometry]. Resolved photometric images capture spatially distributed brightness patterns that encode shape silhouettes, shadow boundaries, and component-level reflectance variations, offering richer spatial information per observation [CITATION: image-based spacecraft pose estimation]. These modalities access attitude information through fundamentally different mechanisms: OCS aggregates the surface BRDF contribution over all visible facets into a single value, while images preserve the pixel-level radiance distribution.

However, existing research typically treats these modalities in isolation. Light-curve and OCS inversion studies often employ simplified reflectance models without generating corresponding images [CITATION: light-curve inversion methods], while image-based pose estimation methods rarely enforce physical consistency with OCS predictions or exploit multi-geometry photometric constraints [CITATION: CNN pose estimation]. Two critical gaps remain: first, the absence of a unified physical framework where both modalities share identical geometry, nonuniform BRDF, and self-occlusion assumptions; second, the lack of systematic evaluation of when each modality provides reliable attitude constraints and under what conditions their fusion yields genuine complementary benefit rather than redundant information. In particular, the performance of high-capacity image models on clean synthetic data may represent an optimistic upper bound that does not transfer to observations degraded by atmospheric seeing, sensor noise, and tracking errors [CITATION: observation degradation effects].

To address these gaps, we develop a unified BRDF-driven simulation framework that generates physically consistent OCS signatures and photometric images from the same satellite STL geometry, nonuniform GGX/Cook-Torrance material assignment, and ray-traced self-occlusion model. Using this framework, we construct a controlled yaw-pitch attitude inversion benchmark and systematically compare OCS-only (MLP), image-only (ResNet-18), late fusion, and feature fusion approaches. Our experiments reveal that observation quality fundamentally determines the relative value of each modality: a ResNet-18 achieves 1.69 ± 0.07° mean error under clean rendered images—an idealized upper bound—but collapses to 85.85° under 1% additive Gaussian noise; OCS-only inversion maintains 5.91° regardless of image quality because it does not depend on image inputs; and OCS-image fusion provides conditional benefits, reducing worst-case errors from 9.9° to 6.6° under clean conditions while the fusion compensation gain increases monotonically from +2.0° to +6.3° as OCS noise rises. Multi-modal complementarity is thus conditional on observation quality, not universally guaranteed.

The contributions of this work are: (1) a unified physical forward model ensuring BRDF-consistent OCS and image generation; (2) a controlled multi-modal attitude inversion benchmark with systematic comparison under consistent protocols; (3) quantification of the clean-image upper bound for image-based inversion and its fragility under controlled degradation; and (4) evidence that OCS provides robust photometric constraints and that fusion value depends on observation quality. This study is conducted entirely within a controlled simulation environment without real optical telescope validation, and the benchmark is limited to yaw-pitch estimation under fixed roll. These boundaries provide a controlled and interpretable evaluation framework while motivating future validation under realistic atmospheric and sensor conditions.

---

## 5. Recommended Version and Rationale

**推荐 Version B** 作为后续主稿基础。

理由：
- Version A 过于防守，读起来像在不断道歉，可能让审稿人觉得贡献不够自信；
- Version B 在保持所有边界声明的同时，主线更有冲击力——"observation quality fundamentally determines the relative value of each modality" 是一个清晰的科学发现陈述；
- Version B 的 gap 段更自然地引出 "two critical gaps"，逻辑链更紧凑；
- 两个版本的边界声明完全一致（no real validation, fixed roll, simulation-focused），审稿安全性相同。

如果主投 ASR（偏保守），可以用 Version A 的第 3 段措辞替换 Version B 的第 3 段。

---

## 6. Claim-Evidence-Risk Map for Introduction

| Claim in Introduction | Evidence Used | Risk Level | Mitigation |
|---|---|---|---|
| OCS is low-cost and multi-geometry | Literature consensus + 5 geometries in this work | Low | Standard claim |
| Images encode shape/shadow/brightness cues | Literature consensus | Low | Standard claim |
| Existing studies model OCS and images separately | Literature survey | Low | Use "typically" not "always" |
| No unified BRDF framework for joint benchmark | Literature gap | Medium | Use "has not been systematically established" |
| ResNet achieves 1.69° under clean images | Experimental result, 5 seeds, audit passed | Low | Label as upper-bound |
| 1% noise degrades ResNet to 85.85° | Controlled experiment | Medium | Label as "controlled degradation test" not "realistic" |
| OCS-only provides 5.91° stable constraint | Experimental result | Low | Add "within simulation, does not depend on image inputs" |
| Fusion reduces worst-case 9.9° → 6.6° | Experimental result | Low | Specify "under clean conditions" |
| Fusion gain increases with OCS noise | Experimental result, monotonic trend | Low | Specify "image branch assumed clean" |
| Complementarity is conditional | Supported by all degradation experiments | Low | Core finding, well-supported |

---

## 7. Citation Placeholder List

| Placeholder | Suggested Topic | Candidate References |
|---|---|---|
| [CITATION: SSA overview] | Space situational awareness importance | [PLACEHOLDER: Vallado, Kelso, or recent SSA review] |
| [CITATION: optical space object characterization] | Optical observation of space objects | [PLACEHOLDER: Cognion 2013, Hall 2017, or similar] |
| [CITATION: light-curve photometry] | Light-curve / OCS measurement methods | [PLACEHOLDER: Linares 2014, Wetterer 2014] |
| [CITATION: image-based spacecraft pose estimation] | CNN/deep learning pose estimation | [PLACEHOLDER: Sharma 2020 SPEED, Park 2019] |
| [CITATION: light-curve inversion methods] | Attitude from light curves | [PLACEHOLDER: Kaasalainen 2004, Linares 2014] |
| [CITATION: CNN pose estimation] | Deep learning spacecraft pose | [PLACEHOLDER: Proença 2020, Chen 2019] |
| [CITATION: observation degradation effects] | Atmospheric/sensor effects on optical obs | [PLACEHOLDER: Hardy 1998, Tyson 2015 adaptive optics context] |

---

## 8. Self-review Checklist

| # | Question | Answer |
|---|---|---|
| 1 | Did the Introduction avoid claiming real optical validation? | ✅ Yes — explicitly states "simulation-focused" and "does not include real optical telescope validation" |
| 2 | Did it frame clean images as an upper bound? | ✅ Yes — "establishing an upper-bound for image-based inversion" / "idealized upper bound" |
| 3 | Did it avoid saying fusion is universally best? | ✅ Yes — "conditional on observation quality rather than universally guaranteed" |
| 4 | Did it explain why a unified BRDF-driven model is needed? | ✅ Yes — Para 3 identifies the gap of separate modeling |
| 5 | Did it clearly separate OCS and image strengths? | ✅ Yes — Para 2 presents both without ranking |
| 6 | Did it keep detailed numbers mostly out of the Introduction? | ✅ Yes — only 3 core numbers (1.69°, 85.85°, 5.91°) + tail improvement |
| 7 | Did it use citation placeholders instead of invented references? | ✅ Yes — all citations are [CITATION: topic] or [PLACEHOLDER: author] |
| 8 | Did it state fixed roll / yaw-pitch boundary without overemphasizing? | ✅ Yes — one sentence in final paragraph, framed positively |
| 9 | Did it avoid using r=0.003 as ResNet evidence? | ✅ Yes — r=0.003 not mentioned in Introduction |

---

## 9. Author Check Items

1. **版本选择**：是否采用 Version B 作为主稿基础？还是偏好 Version A 的保守风格？

2. **数值密度**：Introduction 第 4 段包含 4 个核心数值（1.69°, 85.85°, 5.91°, 9.9°→6.6°）。是否觉得过多？是否需要删减到 2-3 个？

3. **引用占位符**：是否需要我在下一步（Step 3 Related Work）中帮你匹配具体文献？还是你自己填充？

4. **OCS noise fusion gain (+2.0° → +6.3°)**：是否放入 Introduction 第 4 段？当前 Version B 包含了，Version A 未包含。

5. **"two critical gaps" 措辞**：是否接受这种写法？还是觉得 "gap" 一词对二区论文过于强势？

6. **Introduction 长度**：Version B 约 850 words，是否合适？Acta Astronautica 通常接受 800-1200 words 的 Introduction。

---

*Step 2 完成。等待作者确认后进入 Step 3: Related Work + Table 1。*
