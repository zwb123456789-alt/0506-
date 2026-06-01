# Step 4 GPT 输出：Method

## A. Method Logic Map

1. The Method must present the paper as a reproducible controlled simulation benchmark, not as a codebase description.
2. The framework starts from a real satellite STL model and assigns nonuniform materials to three components: metal body, solar panel, and baffle/shade.
3. The same attitude definition, illumination direction, viewing direction, material assignment, BRDF, and visibility assumptions are used to generate OCS signatures and photometric images.
4. Yaw and pitch are the estimated attitude variables; roll is fixed in the present benchmark, so this is not full 3-DOF pose recovery.
5. OCS is computed through facet-level integration of BRDF-weighted illuminated and visible surface contributions.
6. Self-occlusion is modeled through analytical ray visibility queries along illumination and viewing directions, with epsilon and minimum hit distance used to suppress self-intersection and near-field mesh noise.
7. Clean rendered images provide an idealized image-based upper-bound setting rather than real telescope imagery.
8. OCS-only, image-only, late-fusion, and feature-fusion models are used as controlled probes of modality information, not as universal architecture claims.
9. The 10 deg -> 5 deg split tests interpolation over attitude space rather than simple memorization of the 5 deg grid.
10. The Method must explicitly separate practical OCS features such as `per_part_log` from semi-oracle diagnostic features such as `all_raw`.

中文说明：Method 的主线是“同一套物理模型生成 OCS 和图像，再用一组受控反演模型测试模态信息”。不要写成 Python 脚本列表。

## B. Pipeline Figure Sketch

Suggested Fig. 1 / Method pipeline:

```text
Real satellite STL geometry
        |
        v
Component segmentation and material assignment
(metal body / solar panel / baffle-shade)
        |
        v
Yaw-pitch attitude grid + sun-sensor observation geometry
        |
        v
GGX/Cook-Torrance BRDF + facet visibility / self-occlusion
        |
        +-----------------------------+
        |                             |
        v                             v
Multi-geometry OCS signatures      Clean photometric images
(total / per-part / diagnostic)    (128 x 128, main phase branch)
        |                             |
        +-------------+---------------+
                      v
        Controlled attitude inversion models
        OCS-only MLP / image-only CNN-ResNet /
        late fusion / feature fusion
                      |
                      v
        Yaw-pitch prediction and metrics
        mean angular error / Hit@5 / Hit@10 / P90 / worst-case
```

中文说明：图中要把“同源 forward model”画清楚，避免读者以为 OCS 和图像是两个不相关数据源。

## C. Section Outline

| Section | Section goal | Key inputs | Key operations | Key outputs | Boundary / risk |
|---|---|---|---|---|---|
| 3.1 Overview | Define the unified benchmark | STL, materials, BRDF, attitude grid, observation geometry | Generate OCS and images under shared assumptions | Paired OCS-image samples | Controlled simulation, no field validation |
| 3.2 Geometry and attitude | Define object and attitude space | Three-component STL model | Facet representation, yaw-pitch grid, fixed roll | Attitude-indexed geometry states | Not full 3-DOF pose |
| 3.3 Materials and BRDF | Define reflectance model | Component labels, nominal material parameters | Assign GGX/Cook-Torrance parameters | Per-facet BRDF evaluation | Parameters are nominal, not calibrated |
| 3.4 Visibility and self-occlusion | Define facet visibility | Facet centers/normals, sun/view vectors | Ray queries with epsilon and minimum hit distance | Binary illumination/view visibility | Validated by synthetic and manual checks, not real telescope data |
| 3.5 OCS integration | Compute scalar OCS features | Facet area, BRDF, cosines, visibility | Sum visible illuminated BRDF-weighted facets | Total/per-part/log/diagnostic OCS features | all_raw is semi-oracle |
| 3.6 Photometric images | Generate image branch | Same geometry/material/attitude/observation | Clean rendering at 128 x 128 | Idealized photometric images | Not real telescope imagery; main phase branch only |
| 3.7 Inversion models | Probe modality information | OCS features, images, labels | MLP, CNN/ResNet, late fusion, feature fusion | Yaw-pitch predictions | Fusion is benchmark strategy, not universal best |
| 3.8 Split and metrics | Define evaluation | 10 deg/5 deg grids, predictions | Interpolation split and angular metrics | Mean error, Hit@5/10, P90, worst-case | Angular error formula needs exact confirmation |

## D. Method Draft

### 3.1 Overview of the unified OCS-image simulation framework

We formulate the proposed study as a physically consistent simulation and controlled inversion benchmark for space object attitude estimation. The objective is to estimate yaw and pitch from two optical modalities: scalar optical cross section (OCS) signatures and resolved photometric images. Both modalities are generated from the same object geometry, attitude definition, material assignment, BRDF model, illumination direction, viewing direction, and self-occlusion assumptions. This design allows the subsequent inversion experiments to compare modality information under controlled conditions rather than under mismatched forward models.

The pipeline consists of four stages. First, a real satellite STL model is converted into a facet-level representation with component labels and nonuniform material parameters. Second, each yaw-pitch attitude and observation geometry defines the orientation of the object relative to the illumination and detector directions. Third, a GGX/Cook-Torrance BRDF and an analytical visibility model are used to generate multi-geometry OCS signatures and clean rendered photometric images. Fourth, OCS-only, image-only, late-fusion, and feature-fusion models are trained and evaluated as controlled probes of the information carried by each modality. The benchmark is simulation-focused: real optical telescope images are not used, and atmosphere, detector response, optical PSF, earthshine, and background contamination are not explicitly modeled.

### 3.2 Satellite geometry and attitude parameterization

The geometric input is a real satellite STL model consisting of three component groups: a metal body, a solar panel, and a baffle or shade component. The model is represented as triangular facets, each with an area, a surface normal, a component label, and a material assignment. This facet-level representation is required for OCS integration because scalar OCS is computed as a surface integral over illuminated and visible facets.

The attitude state in the present benchmark is parameterized by yaw and pitch, while roll is fixed. The main attitude grid uses a 5 deg resolution with 73 yaw samples and 37 pitch samples, giving 2701 yaw-pitch attitudes. A coarser 10 deg grid is used for training in the interpolation split, while the remaining 5 deg intermediate attitudes are used for testing. This split is designed to evaluate interpolation over attitude space rather than direct memorization of all 5 deg grid points. The exact Euler order and matrix convention should be reported in the final manuscript as `[需要作者确认：Euler order / rotation matrix convention]`.

The present setting should be interpreted as a controlled yaw-pitch benchmark, not as a full three-degree-of-freedom pose-estimation system. This limitation is intentional: the goal is to isolate the information provided by OCS signatures, photometric images, and their fusion under a defined attitude parameterization.

### 3.3 Nonuniform material assignment and GGX BRDF

Nonuniform material assignment is used to reflect the fact that different satellite components have different optical scattering behavior. The three component groups are assigned nominal material parameters for the metal body, solar panel, and baffle/shade. The main paper model uses a GGX/Cook-Torrance BRDF, while LegacyPhong is retained only as a historical or compatibility baseline and is not treated as the primary physical model.

For the controlled simulation, the nominal GGX material settings are as follows: the metal body uses `metallic = 1`, `roughness = 0.20`, and `F0 = 0.91`; the solar panel uses `metallic = 0`, `roughness = 0.40`, and `ior = 1.5`; and the baffle/shade uses `metallic = 0`, `roughness = 0.90`, and `base_color = 0.08`. These parameters are used as physically motivated nominal settings for controlled simulation, not as calibrated measurements of the specific target. Their effect should therefore be interpreted together with the sensitivity analysis reported in the experimental sections.

Let `f_r(n_i, l, v)` denote the BRDF value of facet `i`, where `n_i` is the facet normal, `l` is the illumination direction, and `v` is the viewing direction. The same BRDF evaluation is used by the OCS integration and by the photometric-image generation pipeline, so that both modalities are tied to the same material and reflectance assumptions.

### 3.4 Self-occlusion and visibility modeling

Self-occlusion is modeled at the facet level for OCS integration. For each facet, two visibility queries are evaluated: one along the illumination direction and one along the detector direction. A facet contributes to OCS only when it is both illuminated by the light source and visible to the detector. This design separates local cosine visibility, determined by `max(n_i . l, 0)` and `max(n_i . v, 0)`, from geometric occlusion caused by other parts of the satellite.

The visibility query is implemented using analytical ray tracing over the triangulated geometry. To suppress self-intersection and near-distance mesh artifacts, the ray origin is displaced from the facet surface by an epsilon offset, and intersections closer than a minimum hit distance are filtered. The current validated setting uses `epsilon = 1.0 mm` and `min_hit_distance = 1.0 mm`. These values are chosen from synthetic-geometry validation and sensitivity scans on the real three-component model. Single-plate tests are used to verify that self-intersection is suppressed; double-plate, U-block, and nested-cylinder tests verify cross-part and internal occlusion behavior; and Blender-based manual ray-cast review confirms agreement for sampled cases.

This visibility model is designed for deterministic facet-level OCS computation. It is not a replacement for real optical validation, and it does not imply that all field imaging effects are modeled. Rather, it provides a controlled and reproducible self-occlusion treatment for comparing OCS and image-derived attitude information.

### 3.5 OCS integration

For a given attitude and observation geometry, OCS is computed as a BRDF-weighted surface integral over visible and illuminated facets:

```text
OCS = sum_i A_i f_r(n_i, l, v) max(n_i·l, 0) max(n_i·v, 0) V_i(l) V_i(v),
```

where `A_i` is the area of facet `i`, `f_r` is the GGX/Cook-Torrance BRDF value, `n_i` is the facet normal, `l` and `v` are unit illumination and viewing directions, and `V_i(l)` and `V_i(v)` are binary visibility terms for the illumination and viewing directions. The product of cosine terms enforces local front-facing illumination and observation, while the binary visibility terms account for self-occlusion.

Several OCS feature representations are constructed from this integration. Total OCS features summarize the scalar response for each observation geometry. Per-part OCS features retain component-level contributions from the metal body, solar panel, and baffle/shade. Log-transformed versions are used to reduce dynamic-range imbalance across observation geometries and components. Diagnostic feature variants, such as `all_raw`, may include additional quantities and are therefore treated as semi-oracle upper-bound representations rather than operationally realistic OCS features. In contrast, `per_part_log` is treated as a practical OCS setting for the controlled benchmark.

### 3.6 Photometric image generation

Photometric images are generated from the same geometry, attitude, material assignment, BRDF model, and observation settings used by the OCS pipeline. The main image branch uses clean rendered photometric images at `128 x 128` resolution. These images provide spatial cues such as silhouette, component layout, shadowing, and brightness distribution, which are not preserved by scalar OCS signatures.

The rendered images are not intended to reproduce field telescope images. Instead, they define an idealized and controlled image-based upper-bound setting. Atmosphere, detector response, optical PSF, earthshine, background contamination, and other real-observation effects are not explicitly modeled. The main image branch uses one rendered photometric phase condition, referred to in the project notes as phase63. Broader cross-phase image generalization is outside the scope of the present benchmark and should be treated as future work or a supplementary sensitivity question.

### 3.7 Attitude inversion models

The inversion models are used to probe modality information under controlled conditions. Each model predicts the yaw-pitch attitude from either OCS features, photometric images, or both. To handle angular periodicity, the target can be encoded using a periodic representation such as sine and cosine components for yaw and pitch `[需要作者确认：exact target encoding]`.

#### 3.7.1 OCS-only MLP

The OCS-only model maps OCS feature vectors to yaw-pitch attitude predictions using a multilayer perceptron. The feature input may include total, per-part, or diagnostic OCS representations, with raw or log-transformed scaling. This model tests how much attitude information is carried by low-dimensional scalar photometric signatures. The `all_raw` 45-dimensional representation is treated as a semi-oracle upper bound because it includes additional diagnostic quantities; it should not be interpreted as a fully realistic field-observation feature. The `per_part_log` representation is used as a more practical OCS feature setting in the benchmark.

#### 3.7.2 Image-only CNN and ResNet

The image-only models map a single-channel `128 x 128` photometric image to a yaw-pitch attitude prediction. A TinyCNN is used as a lightweight image baseline, while a ResNet-type model is used as a stronger image model for clean synthetic upper-bound evaluation. The distinction is important: TinyCNN should not be used to characterize the upper limit of image-based inversion, because stronger image models can exploit clean rendered image cues more effectively. Conversely, ResNet performance on clean rendered images should be interpreted as an idealized upper bound, not as a real telescope performance estimate.

#### 3.7.3 Late fusion

Late fusion combines independently produced OCS and image predictions at the prediction level. Fusion is performed in a periodic yaw-pitch representation, and a weighting or beta sweep is used to explore the tradeoff between the two prediction sources. This design tests whether a simple prediction-level combination can exploit complementary errors without learning a joint feature space. Late fusion is a benchmark strategy; it is not assumed to be universally optimal.

#### 3.7.4 Feature fusion

Feature fusion uses a two-branch architecture consisting of an image branch, an OCS branch, and a fusion head. The image branch extracts features from the rendered photometric image, while the OCS branch embeds the OCS feature vector. The concatenated feature representation is then mapped to the yaw-pitch target representation. This model tests whether feature-level interaction between the two modalities improves attitude inference beyond separate predictions. As with late fusion, feature fusion is used to evaluate conditional complementarity, not to claim that a single fusion architecture is best under all conditions.

### 3.8 Evaluation metrics and data splits

The evaluation uses a 10 deg -> 5 deg attitude split. Attitudes on the coarser 10 deg grid form the training pool, while the remaining attitudes on the 5 deg grid form the test set. This split is stricter than a simple random split because the model must infer intermediate attitude states that were not directly included in the training grid. Neural models are evaluated across multiple random seeds to quantify training variability.

Performance is measured using angular error in degrees, mean angular error, standard deviation across seeds where applicable, Hit@5, Hit@10, P90, and worst-case error when relevant. The angular-error computation should account for yaw periodicity and pitch geometry; the final paper should report the exact formula as `[需要作者确认：angular error formula]`. These metrics are used to compare OCS-only, image-only, and fusion models in terms of average accuracy, threshold success rate, and tail behavior.

The benchmark has several explicit boundaries. It estimates yaw and pitch under fixed roll and therefore does not claim full 3-DOF pose recovery. The photometric images are clean rendered images and are not real telescope observations. The main image branch uses one rendered phase condition, while broader cross-phase generalization is not treated as a primary claim. The material parameters are nominal rather than target-calibrated. These boundaries are part of the controlled study design and should be revisited in field validation and extended simulations.

## E. Method Variables and Notation Table

| Symbol / term | Meaning | Unit / range | Used in |
|---|---|---|---|
| `A_i` | Area of facet `i` | m^2 | OCS integration |
| `n_i` | Unit normal of facet `i` | Unit vector | BRDF, cosine visibility |
| `l` | Illumination / sun direction | Unit vector | BRDF, illumination visibility |
| `v` | Viewing / detector direction | Unit vector | BRDF, viewing visibility |
| `f_r(n_i,l,v)` | BRDF value for facet `i` | sr^-1 | OCS and rendering |
| `V_i(l)` | Binary illumination visibility term | 0 or 1 | Self-occlusion / OCS |
| `V_i(v)` | Binary viewing visibility term | 0 or 1 | Self-occlusion / OCS |
| yaw | Horizontal attitude angle | degrees, periodic | Attitude target |
| pitch | Vertical attitude angle | degrees, bounded | Attitude target |
| roll | Third attitude angle, fixed in this benchmark | fixed | Boundary condition |
| OCS | Optical cross section signature | m^2 or normalized feature `[需要作者确认]` | OCS-only and fusion |
| `per_part_log` | Log-transformed component-level OCS feature | feature vector | Practical OCS setting |
| `all_raw` | Raw diagnostic OCS feature representation | 45D in project notes | Semi-oracle upper bound |
| Hit@5 | Fraction of samples with angular error <= 5 deg | percentage | Evaluation metric |
| Hit@10 | Fraction of samples with angular error <= 10 deg | percentage | Evaluation metric |

## F. Reproducibility Checklist

Report in the main paper or supplementary material:

1. STL source and geometry units.
2. Component segmentation: metal body, solar panel, baffle/shade.
3. Material parameters for each component.
4. BRDF model: GGX/Cook-Torrance; LegacyPhong only as compatibility baseline if discussed.
5. Observation geometries: five sun-sensor geometries and phase-angle range of about 24 deg to 120 deg.
6. Yaw/pitch grid: 73 yaw samples, 37 pitch samples, 2701 attitudes.
7. Roll setting: fixed roll.
8. Self-occlusion settings: epsilon = 1.0 mm and min_hit_distance = 1.0 mm.
9. Self-occlusion validation: single plate, double plate, U-block, nested cylinder, and Blender manual review.
10. OCS feature variants: total, per-part, log-transformed, diagnostic all_raw.
11. Image rendering: 128 x 128 clean photometric images; main phase condition phase63.
12. Data split: 10 deg -> 5 deg interpolation split.
13. Model families: OCS MLP, TinyCNN, ResNet, late fusion, feature fusion.
14. Target encoding: `[需要作者确认：sin/cos target encoding details]`.
15. Metrics: mean angular error, seed standard deviation, Hit@5, Hit@10, P90, worst-case.
16. Random seeds and training protocol details: `[需要作者确认：number of seeds and hyperparameters to report in main text or supplement]`.

## G. Claim-Evidence-Risk Map

| Claim | Evidence / method support | Risk | Safe wording |
|---|---|---:|---|
| OCS and images are physically consistent in this benchmark. | Same STL, material assignment, BRDF, attitude, observation, visibility assumptions. | Medium | "generated under shared forward-model assumptions" |
| Self-occlusion model is reliable for controlled OCS simulation. | Synthetic geometry tests and Blender manual ray-cast review. | Medium | "validated in synthetic and sampled manual checks" |
| Material parameters are physically motivated. | Nominal GGX parameters for three components. | Medium | "nominal material settings" not calibrated target parameters |
| Clean images define image upper-bound setting. | Images are rendered without atmosphere/sensor/PSF effects. | Low | "idealized controlled image setting" |
| The benchmark evaluates attitude interpolation. | 10 deg -> 5 deg split. | Low | "tests interpolation rather than direct grid memorization" |
| all_raw is an upper-bound OCS representation. | Includes additional diagnostic quantities. | Low | "semi-oracle upper bound" |
| Fusion tests complementarity. | Late and feature fusion models. | Medium | "benchmark strategy to test complementarity" |
| The task is yaw-pitch under fixed roll. | Project boundary. | Low | "does not claim full 3-DOF pose recovery" |
| Main image branch uses one phase condition. | phase63 image branch. | Medium | "one rendered phase condition for controlled benchmarking" |

## H. Self-review Checklist

1. 是否写成代码说明？  
   **No.** Method is organized by research modules, not Python files.

2. 是否发明参数？  
   **No.** Used only provided parameters; uncertain details are marked with `[需要作者确认]`.

3. 是否宣称真实光学验证？  
   **No.** It explicitly states that real telescope images are not used.

4. 是否说明 fixed roll？  
   **Yes.** Fixed roll is stated in geometry, evaluation boundary, and notation.

5. 是否说明 clean image upper-bound？  
   **Yes.** Rendered images are described as idealized upper-bound setting, not real telescope images.

6. 是否区分 all_raw semi-oracle 和 per_part_log practical OCS setting？  
   **Yes.** `all_raw` is marked semi-oracle; `per_part_log` is described as practical OCS setting.

7. 是否把 fusion 写成 benchmark strategy 而非 universal best？  
   **Yes.** Both late fusion and feature fusion are framed as controlled strategies for testing complementarity.

## I. Questions for Author

1. Euler rotation convention是否可以正式写为 `R = Rz @ Ry @ Rx`，以及 yaw/pitch/roll 的坐标轴定义是否需要画图说明？
2. Angular error 的正式公式是什么？是否基于 yaw-pitch 球面角距离，还是分别计算 yaw/pitch 后合成？
3. OCS 特征的单位和归一化方式是否需要在 Method 中写明？
4. Target encoding 是否确认为 yaw/pitch 的 sin-cos 四维输出？
5. ResNet 是否明确为 ResNet-18？如果是，Method 中可直接写 ResNet-18。
6. 训练超参数是否放 Method 主文，还是放 Supplementary：epoch、batch size、learning rate、seeds、early stopping？

