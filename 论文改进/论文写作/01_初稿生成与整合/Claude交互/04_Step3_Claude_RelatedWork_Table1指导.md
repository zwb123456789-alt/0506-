# Step 3 Claude 指导文件：Related Work + Table 1

> 使用对象：Claude  
> 当前任务：基于已通过单边初审的 Step 2 Introduction，生成 Related Work 结构、英文初稿、Table 1 文献方案对比表和引用风险自检。  
> 输出建议保存为：`claude writing/03_Step3_Claude输出_RelatedWork_Table1.md`

---

## 0. 当前论文定位

论文主题：

> BRDF-driven optical cross section (OCS) and photometric image simulation for controlled space object attitude inversion.

中文定位：

> 基于统一 BRDF 与自遮挡建模的 OCS-光度图像姿态反演基准研究，重点分析理想图像上限、图像退化脆弱性与 OCS 鲁棒互补价值。

目标档次：

- 主攻 SCI 二区
- 按 SCI 一区边缘标准组织论证
- 候选期刊：Acta Astronautica / Advances in Space Research / Optics Express / Remote Sensing

当前 Step 2 结论：

- Introduction 可用 **Version B: Balanced Submission Introduction** 作为 Claude 侧主稿基础。
- Introduction 中数字略密，后续正式稿可适当减少。
- Clean rendered images 必须写成 idealized upper-bound。
- Fusion 必须写成 conditional complementarity。
- 本文无真实光学望远镜验证，必须持续明确。

---

## 1. 你必须遵守的硬边界

1. 不发明引用。不能编造作者、题名、期刊、年份、DOI。
2. 不发明实验结果、数值、图表或真实验证。
3. 不把 clean synthetic image 结果写成真实地基观测性能。
4. 不写 fusion universally outperforms single modalities。
5. 不写 OCS is always better than images。
6. 不宣称本文已有真实 optical telescope validation。
7. 不把 ISAR 并入本文主线。
8. 不使用 `state-of-the-art`, `first`, `novel` 等过强词，除非明确标注为 `[to verify]`。
9. 所有不确定文献信息一律写成 `[to verify]` 或 `[需要作者核对]`。

---

## 2. 当前可用核心证据

物理建模链条：

- Real satellite STL geometry
- Nonuniform material assignment
- GGX/Cook-Torrance BRDF
- Analytical ray-based self-occlusion
- Multi-geometry OCS signatures
- Photometric image rendering
- Yaw-pitch attitude inversion under fixed roll
- OCS-only / image-only / late fusion / feature fusion

核心结果：

- ResNet image-only clean：`1.69 ± 0.07 deg`, Hit@5 `97.6%`
- ResNet + concat5 per_part_log：`1.47 ± 0.07 deg`
- worst-case：`9.9 deg -> 6.6 deg`
- 1% Gaussian image noise：ResNet `85.85 deg`, Hit@5 `2.2%`
- OCS MLP per_part_log：`5.91 deg`
- OCS MLP all_raw 45D：`3.98 ± 0.60 deg`, Hit@5 `90.7%`，只能写为 semi-oracle upper bound
- TinyCNN image-only：`12.38 ± 0.74 deg`，只能作为 lightweight baseline
- Early feature fusion per_part_log：`4.10 ± 0.77 deg`, Hit@5 `87.3%`
- OCS-CNN error correlation `r = 0.003`，只能写为 earlier TinyCNN/OCS diagnostic，不能写成 ResNet pair 结论
- OCS-noise fusion gain：`+1.97 deg -> +6.29 deg` as OCS noise rises `0% -> 20%`

重要限制：

- No real optical telescope validation
- Clean rendered images are idealized photometric imagery
- Atmosphere, detector response, PSF, earthshine, and background contamination are not explicitly modeled
- Current task estimates yaw-pitch under fixed roll
- Image branch mainly uses phase63
- Material parameters are nominal

---

## 3. 必须覆盖的文献

请至少覆盖以下文献。你只能基于这里给出的用途做保守表述；如果具体细节不确定，必须标注 `[to verify]`。

1. **Yang et al., 2024, Photonics**  
   主题：goniopolarimetric properties / satellite material BRDF。  
   用途：支撑 satellite material reflectance、Cook-Torrance/GGX、BRDF 参数合理性。

2. **Lu Yao, 2024, Universe**  
   主题：BRDF-based photometric modeling of Starlink / LEO constellation satellites。  
   用途：支撑真实大规模 photometry + BRDF modeling；也用于说明真实 brightness modeling 包含更复杂观测因素。

3. **Wang et al., 2024, Advances in Space Research**  
   主题：laboratory-tested photometry dataset for attitude inversion。  
   用途：支撑 light-curve / photometry-based attitude inversion，与 OCS-based inversion 最接近。

4. **Burton et al., 2024, Advances in Space Research**  
   主题：light curve attitude estimation using particle swarm optimizers。  
   用途：支撑 optimization-based light-curve attitude estimation baseline。

5. **Dickinson, 2025, RIT PhD**  
   主题：sim-to-real 6DOF satellite pose estimation from resolved ground-based imagery。  
   用途：支撑 image-based spacecraft pose estimation、sim-to-real、ground-based resolved imagery 的挑战。

6. **Kumar et al., 2025, Acta Astronautica**  
   主题：light-curve sequential comparison / digital twin for LEO uncontrolled objects。  
   用途：支撑 digital twin + light curve + attitude/object understanding 的目标期刊叙事。

7. **Liu et al., 2024, Remote Sensing**  
   主题：tightly coupled visual-inertial fusion for spacecraft attitude estimation。  
   用途：支撑 feature-level / tightly coupled fusion 的一般思想，但要说明它不是 OCS-image photometric fusion。

8. **Fankhauser et al., 2023, AJ**  
   主题：satellite optical brightness。  
   用途：支撑 satellite brightness modeling、earthshine / radiometric effects / real observation complexity，也可服务 limitations。

可选补充：

- AISwarm-LS 2025 Aerospace：joint estimation
- Marto 2024 hyperspectral light curve + NN inversion
- Sosa 2025 ViT / 6DOF image pose
- Xiong 2025 multi-exposure image fusion
- Behari 2023 SUNDIAL
- Groves 2025 self-supervised SSA light curve model

---

## 4. Related Work 推荐结构

不要写成逐篇文献流水账。每节按以下逻辑写：

```text
topic scope -> representative methods -> limitation tied to this paper -> distinction of this work
```

### 2.1 Optical signatures and BRDF modeling of space objects

要点：

- Space-object optical signatures depend on geometry, material reflectance, illumination, viewing direction, phase angle, and occlusion.
- Yang 2024 支撑 satellite material BRDF / Cook-Torrance / GGX 的材料反射基础。
- Lu 2024 支撑真实 satellite photometry + BRDF modeling。
- Fankhauser 2023 支撑 satellite optical brightness 与真实 radiometric complexity。
- 缺口：许多 BRDF / brightness modeling 工作重点在 photometric prediction、material characterization 或 brightness modeling，不一定闭环到 OCS-image joint attitude inversion benchmark。

### 2.2 Light-curve and OCS-based attitude inversion

要点：

- Light curve / OCS-like scalar signatures are low-dimensional, interpretable, and often available across multiple observation geometries.
- Wang 2024、Burton 2024、Kumar 2025 支撑 photometry/light-curve attitude inversion、optimization-based estimation 或 digital twin comparison。
- 缺口：这类工作通常不与 resolved photometric image branch 在同一 BRDF/self-occlusion forward model 中做公平比较。

### 2.3 Photometric image simulation and image-based pose estimation

要点：

- Resolved or rendered images provide spatial cues such as silhouette, shadow, brightness distribution, and component layout.
- Dickinson 2025 支撑 sim-to-real 6DOF image-based satellite pose estimation；可选 Sosa 2025 支撑 strong visual model baseline。
- 缺口：image-based pose work often focuses on visual pose accuracy and sim-to-real transfer, but may not compare against scalar OCS/light-curve constraints generated under the same physical scattering assumptions。
- 必须提醒：本文 clean-image result 是 upper-bound benchmark，不是 real AO / telescope performance。

### 2.4 Multi-modal fusion and robustness under observation degradation

要点：

- Fusion can improve robustness when modalities carry complementary failure modes, but benefits depend on modality quality and fusion design.
- Liu 2024 支撑 tightly coupled / feature-level fusion 的一般思想，但它是 visual-inertial fusion，不是 OCS-image photometric fusion。
- 可选 Xiong 2025 支撑 image-quality degradation / image fusion 的观测质量问题。
- 缺口：现有 fusion 文献不直接回答 OCS 与 photometric image 在统一 BRDF/self-occlusion simulation 下何时互补。

---

## 5. Table 1 必须生成

请生成一张 Related Work 方案对比表草稿。表头必须使用：

| Work | Geometry | BRDF | Self-occlusion | Image | OCS/light curve | Attitude inversion | Fusion | External validation |
|---|---|---|---|---|---|---|---|---|

填表要求：

1. 每个单元格使用短语，不要写长段落。
2. 不确定的地方写 `[to verify]` 或 `[需要作者核对]`。
3. 本文最后一行写为 `This work`。
4. Table 1 的目的不是证明本文 SOTA，而是说明本文的组合位置：
   - Real satellite STL
   - GGX/Cook-Torrance BRDF
   - Nonuniform materials
   - Analytical ray-based self-occlusion
   - Both OCS and photometric images
   - Yaw-pitch controlled inversion benchmark
   - Late and feature fusion
   - No real external validation; only analytical/rendering consistency and controlled sensitivity tests

建议表内至少包含：

- Yang 2024
- Lu 2024
- Wang 2024
- Burton 2024
- Dickinson 2025
- Kumar 2025
- Liu 2024
- Fankhauser 2023
- This work

---

## 6. 请输出的内容

请按以下格式一次性输出完整 Markdown。

### A. Related Work Logic Map

用 6-10 条说明 Related Work 如何服务 Introduction 的 gap。

### B. Section Outline

给出 2.1-2.4 每节的 topic sentence、核心文献、缺口、与本文区别。

### C. Related Work Draft

写英文初稿。建议总长 900-1300 words。要求：

- 机制比较优先，不要论文逐篇堆砌。
- 每段要有 topic sentence。
- 每节末尾要明确本文与该方向的区别。
- 引用使用安全占位，例如 `[Yang et al., 2024]` 或 `[CITATION: satellite BRDF modeling]`。
- 对不确定文献细节加 `[to verify]`。

### D. Table 1 Draft

生成 Markdown 表格。

### E. Citation Placeholder Map

列出每个 citation placeholder 应由哪篇文献支撑。格式：

| Placeholder | Candidate references | Used for | Verification needed |
|---|---|---|---|

### F. Claim-Evidence-Risk Map

列出 Related Work 中最容易被审稿人质疑的 6-8 个 claims，并标注证据与风险。

### G. Self-review Checklist

检查：

1. 是否发明了引用？
2. 是否把本文说成 SOTA？
3. 是否夸大 fusion？
4. 是否承认无真实光学验证？
5. 是否覆盖了 BRDF modeling、light-curve/OCS inversion、image pose、fusion 四条线？
6. 是否把 Table 1 的不确定信息标注为待核对？

### H. Questions for Author

最多提出 5 个需要作者确认的问题，不要超过 5 个。

---

## 7. 重要写作口径

可用表述：

```text
These studies motivate the need for physically consistent optical modeling, but they do not directly answer how scalar OCS signatures and resolved photometric images behave when both are generated from the same BRDF, geometry, material, and self-occlusion assumptions.
```

```text
The present work is positioned as a controlled simulation benchmark rather than a claim of field-validated performance.
```

```text
The comparison focuses on modality information and robustness, not on declaring a universally superior sensor or fusion architecture.
```

避免表述：

```text
No prior work has studied this problem.
Our method is the first / state-of-the-art.
Fusion always improves attitude inversion.
The reported image accuracy reflects real telescope performance.
OCS is more accurate than images.
```

---

## 8. 输出文件命名

完成后请把输出保存为：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\Claude交互\claude writing\03_Step3_Claude输出_RelatedWork_Table1.md
```

如果不能直接保存文件，则把完整 Markdown 内容返回给作者，由作者保存。
