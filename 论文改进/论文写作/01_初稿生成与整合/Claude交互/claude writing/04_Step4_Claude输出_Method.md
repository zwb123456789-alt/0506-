# Step 4 Output: Method

> 本阶段任务：基于 Step 1-3 已定稿的主线，生成 Method 章节的结构、英文初稿、符号表、可复现性清单和自检。Method 不写性能数值，不写成代码说明。

---

## A. Method Logic Map

1. §3.1 Overview 建立全文方法论锚点：统一 forward model 使 OCS 和图像共享物理假设 → 支撑 Contribution 1。
2. §3.2 Geometry + attitude 定义姿态空间和坐标系 → 支撑 "controlled benchmark" 的可复现性。
3. §3.3 Observation geometry 说明多几何 OCS 与单相位图像的数据生成协议 → 支撑 Contribution 2 的 systematic comparison。
4. §3.4 BRDF + material 提供物理散射模型 → 支撑 "BRDF-driven" 标题和 Contribution 1。
5. §3.5 Self-occlusion 说明非凸几何的可见性处理 → 支撑遮挡消融实验的方法基础。
6. §3.6 OCS integration 给出 OCS 公式和特征构造 → 支撑 OCS-only inversion 和 fusion 的输入定义。
7. §3.7 Image generation 说明图像渲染管线 → 支撑 Contribution 3 的 "clean-image upper bound" 定义。
8. §3.8 Inversion models 定义四类反演方法 → 支撑 Contribution 2 的 benchmark 和 Contribution 4 的 conditional fusion。
9. §3.9 Data splits + metrics 确保评估公平性 → 支撑审稿人对 reproducibility 的要求。
10. 全章末尾的 boundary 段落呼应 Introduction 的 limitation 声明 → 审稿防御。

---

## B. Pipeline Figure Sketch

建议 Fig. 1 为左到右流程图，分三层：

```
┌─────────────────────────────────────────────────────────────────────┐
│                    UNIFIED FORWARD MODEL                            │
│                                                                     │
│  ┌──────────┐    ┌──────────────┐    ┌─────────────────────┐       │
│  │ Satellite │───▶│ Attitude     │───▶│ GGX/Cook-Torrance   │       │
│  │ STL       │    │ yaw, pitch   │    │ BRDF + Nonuniform   │       │
│  │ Geometry  │    │ (fixed roll) │    │ Material Assignment │       │
│  └──────────┘    └──────────────┘    └─────────┬───────────┘       │
│                                                 │                   │
│                  ┌──────────────────────────────┼──────────┐        │
│                  │  Observation Geometry         │          │        │
│                  │  (Sun dir, Detector dir)      ▼          │        │
│                  │              ┌────────────────────┐      │        │
│                  │              │ Self-Occlusion &   │      │        │
│                  │              │ Visibility Query   │      │        │
│                  │              └────────┬───────────┘      │        │
│                  └──────────────────────┼──────────────────┘        │
│                                         │                           │
│                    ┌────────────────────┼────────────────────┐      │
│                    ▼                                          ▼      │
│         ┌──────────────────┐                    ┌───────────────┐   │
│         │ OCS Integration  │                    │ Photometric   │   │
│         │ (facet-level)    │                    │ Image Render  │   │
│         │ → OCS features   │                    │ (pixel-level) │   │
│         └────────┬─────────┘                    └───────┬───────┘   │
└──────────────────┼──────────────────────────────────────┼───────────┘
                   │                                      │
                   ▼                                      ▼
         ┌──────────────────┐                    ┌───────────────┐
         │ OCS-only MLP     │                    │ Image-only    │
         │                  │                    │ CNN / ResNet  │
         └────────┬─────────┘                    └───────┬───────┘
                  │                                      │
                  └──────────────┬────────────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │ Late Fusion / Feature   │
                    │ Fusion                  │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │ Attitude Prediction     │
                    │ (yaw, pitch)            │
                    └─────────────────────────┘
```

---

## C. Section Outline

| Section | Goal | Key Inputs | Key Operations | Key Outputs | Boundary/Risk |
|---|---|---|---|---|---|
| 3.1 Overview | Establish unified framework concept | — | Describe shared physical assumptions | Reader understands why OCS and images are comparable | Must state simulation-focused |
| 3.2 Geometry & attitude | Define spatial domain | STL files, Euler convention | Load geometry, define yaw-pitch grid | 2701 attitudes, facet normals/areas | Fixed roll; must state |
| 3.3 Observation geometry | Define illumination/viewing | 5 sun-det pairs | Multi-geometry protocol | Phase angles 24°–120° | Image uses only phase63 |
| 3.4 BRDF & materials | Define scattering physics | GGX params per component | Evaluate f_r for each facet/pixel | BRDF values | Nominal params, not calibrated |
| 3.5 Self-occlusion | Handle non-convex visibility | Ray queries, epsilon/mhd | Binary visibility per facet | V_i(l), V_i(v) | Validated on synthetic geometries only |
| 3.6 OCS integration | Compute scalar signatures | Facet data + BRDF + visibility | Summation formula | OCS feature vectors | all_raw is semi-oracle |
| 3.7 Image generation | Produce photometric images | Blender + exact BRDF post-processing | Pixel-level rendering | 128×128 grayscale images | Clean only; no atmosphere/PSF |
| 3.8 Inversion models | Define estimation methods | OCS features / images | MLP, CNN, ResNet, fusion | Predicted yaw-pitch | Models are probes, not claimed optimal |
| 3.9 Splits & metrics | Ensure fair evaluation | 2701 attitudes | 10°→5° split, 5 seeds | mean error, Hit@5°, p90 | Interpolation test, not memorization |

---

## D. Method Draft

### 3.1 Overview of the Unified OCS-Image Simulation Framework

This section describes the unified forward model and controlled inversion benchmark used in this study. The central design principle is that both optical cross section (OCS) signatures and photometric images are generated from the same satellite geometry, attitude parameterization, nonuniform material assignment, GGX/Cook-Torrance BRDF, observation geometry, and self-occlusion model. This ensures that any difference in attitude inversion performance between OCS-based and image-based approaches reflects the intrinsic information content of each modality rather than inconsistencies in the underlying physical assumptions.

The framework operates in two stages. In the forward stage, a real satellite STL model is assigned nonuniform surface materials, rotated through a dense yaw-pitch attitude grid, and evaluated under multiple observation geometries to produce both facet-level OCS signatures and pixel-level photometric images. In the inversion stage, these signatures and images serve as inputs to OCS-only, image-only, and multi-modal fusion models that predict the generating attitude. The rendered images define an idealized upper-bound setting for image-based inversion; they do not reproduce real telescope observations affected by atmospheric turbulence, sensor noise, or optical aberrations. The study is simulation-focused and does not include real optical telescope validation.

### 3.2 Satellite Geometry and Attitude Parameterization

The satellite model consists of a real STL geometry comprising three distinct components: a metallic main body, a solar panel, and a baffle (shade). Each component is represented as a triangulated surface mesh with known facet areas and outward-pointing normals. The geometry is processed at the facet level for OCS computation and at the pixel level for image rendering.

Attitude is parameterized using Euler angles in the Z-Y-X intrinsic rotation convention:

$$R = R_z(\psi) \cdot R_y(\theta) \cdot R_x(\phi)$$

where $\psi$ denotes yaw, $\theta$ denotes pitch, and $\phi$ denotes roll. In the present benchmark, roll is fixed at zero, and the attitude space is defined by yaw $\in [0°, 360°)$ and pitch $\in [-90°, 90°]$. The primary attitude grid uses 5° spacing: 73 yaw values and 37 pitch values, yielding 2,701 distinct attitudes. The satellite is rotated while the Sun and detector directions remain fixed in the inertial frame.

The present benchmark estimates yaw and pitch under fixed roll and therefore does not claim full three-degree-of-freedom pose recovery. A roll sensitivity analysis is provided separately to characterize the impact of this simplification.

### 3.3 Observation Geometry and Data Generation Protocol

The observation geometry is defined by the Sun direction vector $\mathbf{l}$ and the detector direction vector $\mathbf{v}$, both fixed in the inertial frame. For OCS computation, five observation geometries are used, spanning phase angles from approximately 24° to 120°. These cover near-backscatter, side-scatter, and forward-scatter configurations, providing diverse photometric sampling of the attitude-dependent OCS response.

For the image branch, the primary rendered phase uses a single observation geometry (phase angle ≈ 63°) to produce one photometric image per attitude. This asymmetry between OCS (five geometries) and images (one geometry) reflects the different information densities of the two modalities: each OCS measurement yields a single scalar, whereas each image provides $128 \times 128 = 16{,}384$ pixel values. The main image branch uses one rendered phase condition for controlled benchmarking; broader cross-phase image generalization is left for future work.

### 3.4 Nonuniform Material Assignment and GGX BRDF

Each satellite component is assigned distinct material properties reflecting its physical composition. The BRDF is modeled using the GGX/Cook-Torrance microfacet model:

$$f_r = f_{\text{diffuse}} + f_{\text{specular}}$$

$$f_{\text{diffuse}} = (1 - m) \cdot \frac{\rho_d}{\pi}$$

$$f_{\text{specular}} = \frac{D_{\text{GGX}}(\mathbf{n} \cdot \mathbf{h}, \alpha) \cdot G_{\text{Smith}}(\mathbf{n} \cdot \mathbf{l}, \mathbf{n} \cdot \mathbf{v}, \alpha) \cdot F_{\text{Schlick}}(\mathbf{v} \cdot \mathbf{h}, F_0)}{4 \cdot (\mathbf{n} \cdot \mathbf{l}) \cdot (\mathbf{n} \cdot \mathbf{v})}$$

where $m$ is the metallic flag, $\alpha = \text{roughness}^2$, $D_{\text{GGX}}$ is the GGX normal distribution function, $G_{\text{Smith}}$ is the Smith geometry term, and $F_{\text{Schlick}}$ is the Schlick Fresnel approximation. The nominal material parameters are:

| Component | Metallic | Roughness | F0 / Base color | Physical basis |
|---|---|---|---|---|
| Metal body | 1 | 0.20 | F0 = 0.91 | Aluminum optical constants |
| Solar panel | 0 | 0.40 | IOR = 1.5 | Glass cover sheet |
| Baffle/shade | 0 | 0.90 | 0.08 | Dark absorptive coating |

These parameters are used as nominal material settings for controlled simulation, not as calibrated measurements of the specific target. Their sensitivity is evaluated through parameter perturbation experiments reported in the results.

### 3.5 Self-Occlusion and Visibility Modeling

For non-convex satellite geometries, some surface facets may be occluded from the Sun or detector by other parts of the structure. The self-occlusion model determines, for each facet, whether unobstructed lines of sight exist to both the Sun and the detector.

For each facet with center $\mathbf{c}_i$ and outward normal $\mathbf{n}_i$, two visibility queries are performed. A ray is cast from $\mathbf{c}_i + \epsilon \cdot \mathbf{n}_i$ along the Sun direction $\mathbf{l}$ and along the detector direction $\mathbf{v}$. If either ray intersects another surface element at a distance exceeding the minimum hit distance threshold, the facet is marked as occluded from that direction. Only facets satisfying both $V_i(\mathbf{l}) = 1$ and $V_i(\mathbf{v}) = 1$ contribute to the OCS.

The offset $\epsilon = 1.0$ mm and minimum hit distance threshold $d_{\min} = 1.0$ mm are determined through sensitivity analysis on both synthetic test geometries (single plate, double plate, U-block, nested cylinder) and the real satellite model. These values represent the optimal balance between suppressing mesh discretization artifacts and preserving genuine near-neighbor occlusion. The occlusion model has been cross-validated against independent ray-cast queries for sampled cases [需要作者确认：whether to cite Blender cross-validation explicitly or keep implicit].

### 3.6 OCS Integration and Feature Construction

The optical cross section for a given attitude and observation geometry is computed as:

$$\text{OCS} = \sum_{i} A_i \cdot f_r(\mathbf{n}_i, \mathbf{l}, \mathbf{v}) \cdot \max(\mathbf{n}_i \cdot \mathbf{l}, 0) \cdot \max(\mathbf{n}_i \cdot \mathbf{v}, 0) \cdot V_i(\mathbf{l}) \cdot V_i(\mathbf{v})$$

where $A_i$ is the facet area in m², and the summation runs over all facets satisfying the geometric visibility condition $\mathbf{n}_i \cdot \mathbf{l} > 0$ and $\mathbf{n}_i \cdot \mathbf{v} > 0$.

For attitude inversion, OCS values are organized into feature vectors at three information levels:

- **total\_log** (15D): Total OCS values (with and without occlusion) and occlusion ratio across 5 geometries, log-transformed.
- **per\_part\_log** (30D): Per-component OCS values across 5 geometries, log-transformed. This is the primary practical OCS feature setting.
- **all\_raw** (45D): All per-component OCS values plus occlusion ratios across 5 geometries, without transformation. This representation includes diagnostic quantities not readily available from real observations and is therefore treated as a semi-oracle upper bound.

### 3.7 Photometric Image Generation

Photometric images are generated using a geometry-buffer rendering pipeline. For each attitude, the rendering engine produces a multi-layer output containing per-pixel surface normals, depth, and component indices. A Python post-processing stage then evaluates the exact GGX/Cook-Torrance BRDF at each visible pixel using the same material parameters and BRDF function as the OCS computation, ensuring physical consistency between the two modalities.

The output is a single-channel $128 \times 128$ grayscale image representing the spatially resolved radiance distribution. A log1p intensity transformation is applied to compress the dynamic range of specular highlights before input to neural networks. The rendered images are free from atmospheric turbulence, sensor noise, tracking error, point-spread function variation, and background contamination. They therefore define an idealized upper-bound condition for image-based attitude inversion, not a prediction of field telescope performance.

### 3.8 Attitude Inversion Models

The inversion models are used as controlled probes of modality information content rather than as claims of a universally optimal architecture.

#### 3.8.1 OCS-Only MLP

A multi-layer perceptron (MLP) maps OCS feature vectors to attitude predictions. The network architecture consists of fully connected layers with SiLU activation and layer normalization [需要作者确认：exact architecture 128→128→64 or simplified description]. The output is a four-dimensional vector $[\sin\psi, \cos\psi, \sin\theta, \cos\theta]$ encoding yaw and pitch in periodic form. The predicted angles are recovered by normalization and arctangent.

#### 3.8.2 Image-Only CNN and ResNet

Two image models are evaluated. A lightweight TinyCNN (approximately 106k parameters) serves as a compact baseline. A ResNet-18 (approximately 11.2M parameters) serves as a higher-capacity model to establish the clean-image upper bound. Both models take a single-channel $128 \times 128$ image as input and output the same four-dimensional periodic attitude representation.

The ResNet-18 clean-image result represents an idealized upper bound for image-based inversion under perfect rendering conditions. It should not be interpreted as achievable performance under real telescope observations.

#### 3.8.3 Late Fusion

Late fusion combines independently trained OCS and image model predictions in the periodic $[\sin, \cos]$ attitude space:

$$\mathbf{z}_{\text{fused}} = \beta \cdot \mathbf{z}_{\text{OCS}} + (1 - \beta) \cdot \mathbf{z}_{\text{image}}$$

where $\beta \in [0, 1]$ is swept to characterize the fusion tradeoff. This approach tests whether simple prediction averaging captures complementary information without joint training.

#### 3.8.4 Feature Fusion

Feature fusion uses a two-branch architecture: an image branch extracts a learned feature vector from the input image, an OCS branch embeds the OCS feature vector, and a fusion head concatenates both representations to predict the attitude. The entire model is trained end-to-end. This architecture tests whether feature-level interaction between modalities provides benefits beyond prediction-level combination. Feature fusion is evaluated as a benchmarked fusion strategy, not asserted as universally optimal.

### 3.9 Data Splits, Evaluation Metrics, and Reproducibility

The attitude dataset of 2,701 samples is split using a structured 10°→5° protocol: attitudes on the coarser 10° grid (563 samples) form the training pool, while the remaining 5° intermediate attitudes (1,998 samples) form the test set. This tests the model's ability to interpolate to unseen attitudes rather than memorize training examples. A random 80/10/10 split is additionally reported for consistency verification.

All neural network experiments are repeated with 5 random seeds to report mean ± standard deviation. The primary evaluation metrics are:

- **Mean angular error** (degrees): the average geodesic angular distance between predicted and true attitudes, accounting for yaw periodicity.
- **Hit@5°**: the fraction of test predictions with angular error ≤ 5°.
- **Hit@10°**: the fraction with error ≤ 10°.
- **P90**: the 90th percentile error.
- **Worst-case**: the maximum error across the test set.

[需要作者确认：angular error formula — is it Euclidean in yaw-pitch space with yaw wraparound, or geodesic on the sphere?]

---

## E. Method Variables and Notation Table

| Symbol / Term | Meaning | Unit / Range | Used In |
|---|---|---|---|
| $A_i$ | Facet area | m² | §3.6 OCS integration |
| $\mathbf{n}_i$ | Facet unit outward normal | dimensionless | §3.5, §3.6 |
| $\mathbf{l}$ | Sun direction (unit vector, inertial frame) | dimensionless | §3.3, §3.5, §3.6 |
| $\mathbf{v}$ | Detector direction (unit vector, inertial frame) | dimensionless | §3.3, §3.5, §3.6 |
| $\mathbf{h}$ | Half-angle vector, normalize($\mathbf{l} + \mathbf{v}$) | dimensionless | §3.4 |
| $f_r$ | BRDF value | sr⁻¹ | §3.4, §3.6 |
| $V_i(\mathbf{l})$, $V_i(\mathbf{v})$ | Binary visibility (1 = unoccluded) | {0, 1} | §3.5, §3.6 |
| $\epsilon$ | Ray origin offset along normal | mm (1.0) | §3.5 |
| $d_{\min}$ | Minimum hit distance threshold | mm (1.0) | §3.5 |
| $\psi$ | Yaw angle | [0°, 360°) | §3.2 |
| $\theta$ | Pitch angle | [−90°, 90°] | §3.2 |
| $\phi$ | Roll angle (fixed = 0°) | — | §3.2 |
| OCS | Optical cross section | m² | §3.6 |
| per\_part\_log | Per-component OCS features, log-transformed, 30D | — | §3.6 |
| all\_raw | Full OCS features including occlusion ratio, 45D | — | §3.6 (semi-oracle) |
| total\_log | Total OCS features, log-transformed, 15D | — | §3.6 |
| Hit@5° | Fraction of predictions with error ≤ 5° | [0, 1] | §3.9 |
| P90 | 90th percentile angular error | degrees | §3.9 |
| $\beta$ | Late fusion weight | [0, 1] | §3.8.3 |

---

## F. Reproducibility Checklist

| Item | Value / Setting | Report In |
|---|---|---|
| STL source | Real satellite model, 3 components | Method §3.2 |
| Geometry units | mm (converted to m for OCS) | Method §3.2 |
| Component segmentation | Metal body / Solar panel / Baffle | Method §3.2 |
| BRDF model | GGX/Cook-Torrance | Method §3.4 |
| Material parameters | See Table in §3.4 | Method §3.4 |
| Observation geometries | 5 sun-det pairs, phase 24°–120° | Method §3.3 |
| Yaw grid | 73 values, 5° spacing, [0°, 360°) | Method §3.2 |
| Pitch grid | 37 values, 5° spacing, [−90°, 90°] | Method §3.2 |
| Roll | Fixed at 0° | Method §3.2 |
| Self-occlusion epsilon | 1.0 mm | Method §3.5 |
| Self-occlusion mhd | 1.0 mm | Method §3.5 |
| Image resolution | 128 × 128, single channel | Method §3.7 |
| Image phase | phase63 (≈63° phase angle) | Method §3.3 |
| Intensity transform | log1p | Method §3.7 |
| Data split | 10°→5° (563 train / 1998 test) | Method §3.9 |
| Random seeds | 5 (0, 1, 2, 3, 4) | Method §3.9 |
| OCS-only model | MLP, periodic output encoding | Method §3.8.1 |
| Image models | TinyCNN (106k), ResNet-18 (11.2M) | Method §3.8.2 |
| Fusion models | Late (β-sweep), Feature (two-branch) | Method §3.8.3–4 |
| Metrics | Mean error, Hit@5°, Hit@10°, P90, worst-case | Method §3.9 |

---

## G. Claim-Evidence-Risk Map

| # | Claim | Evidence | Risk | Mitigation |
|---|---|---|---|---|
| 1 | OCS and images share unified physical assumptions | Same BRDF function, material DB, geometry, attitude | Low | Explicitly stated in §3.1 |
| 2 | Self-occlusion model is correct | Synthetic geometry tests + mhd sensitivity + cross-validation | Medium | Report validation in Results; acknowledge no field validation |
| 3 | Nominal material parameters are reasonable | Literature values (Al F0, glass IOR) + sensitivity analysis | Medium | State "nominal" explicitly; report sensitivity |
| 4 | Clean images define an upper bound | Images lack all real degradation sources | Low | Stated in §3.7 |
| 5 | Fixed roll is acceptable for benchmark | Roll sensitivity experiment shows ~20% OCS variation | Medium | State limitation; report sensitivity |
| 6 | One-phase image branch is sufficient for benchmark | Single phase provides 16k pixels vs OCS scalar | Medium | Acknowledge; leave cross-phase for future work |
| 7 | all\_raw 45D is semi-oracle | Contains occlusion ratio not measurable in practice | Low | Clearly labeled throughout |
| 8 | Fusion is benchmarked, not claimed optimal | Multiple fusion strategies compared | Low | Stated in §3.8.4 |
| 9 | 10°→5° split tests interpolation | Training on coarse grid, testing on fine grid | Low | Standard approach; random split also reported |

---

## H. Self-review Checklist

| # | Question | Answer |
|---|---|---|
| 1 | Is it written as a reproducible method, not code documentation? | ✅ Yes — no script names, no file paths, no implementation logs |
| 2 | Did I invent any parameters or results? | ✅ No — all values from project documentation |
| 3 | Did I claim real optical telescope validation? | ✅ No — explicitly denied in §3.1 and §3.7 |
| 4 | Did I state fixed roll? | ✅ Yes — §3.2 and boundary paragraph |
| 5 | Did I state clean image = upper bound? | ✅ Yes — §3.7 and §3.8.2 |
| 6 | Did I distinguish all\_raw (semi-oracle) from per\_part\_log (practical)? | ✅ Yes — §3.6 |
| 7 | Did I frame fusion as benchmark strategy, not universal best? | ✅ Yes — §3.8 opening and §3.8.4 |
| 8 | Did I avoid putting Results performance numbers in Method? | ✅ Yes — no mean errors, Hit@5°, or comparison numbers |

---

## I. Questions for Author

1. **MLP 架构细节**：正文是否需要写出具体层数和宽度（128→128→64）？还是用 "a three-layer MLP with SiLU activation and layer normalization" 的抽象描述？

2. **角度误差公式**：当前使用的是欧氏距离（考虑 yaw 周期性）还是球面测地距离？需要确认以便在 §3.9 中写出精确公式。

3. **Blender 交叉验证**：§3.5 中是否需要明确提及 Blender 独立 ray-cast 验证？还是只写 "cross-validated against independent ray-cast queries"？

4. **ResNet-18 训练细节**：是否需要在 Method 中报告 learning rate、batch size、epochs、optimizer？还是放入补充材料？

5. **图像 log1p 变换**：是否需要在 §3.7 中给出公式 $I' = \log(1 + I)$？还是一句话带过？

6. **OCS 特征 z-score 归一化**：训练前是否对 OCS 特征做了 z-score 标准化？如果是，需要在 §3.6 或 §3.9 中提及。

---

*Step 4 完成。等待作者确认后进入 Step 5: Results 初稿。*
