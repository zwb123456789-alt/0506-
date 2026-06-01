# Step 4 Claude 指导文件：Method

> 使用对象：Claude  
> 当前任务：在已完成 Step 1-3 的基础上，生成论文 Method 章节的结构、英文初稿、方法边界和可复现性说明。  
> 输出建议保存为：`claude writing/04_Step4_Claude输出_Method.md`

---

## 0. 当前论文定位

论文主题：

> BRDF-driven optical cross section and photometric image simulation for robust space object attitude inversion.

中文定位：

> 基于统一 BRDF 与自遮挡建模的 OCS-光度图像姿态反演基准研究，重点分析理想图像上限、图像退化脆弱性与 OCS 鲁棒互补价值。

目标档次：

- 主攻 SCI 二区
- 按 SCI 一区边缘标准组织论证
- 候选期刊：Acta Astronautica / Advances in Space Research / Optics Express / Remote Sensing

Method 章节的核心任务：

> 把本文写成一个可复现的 physically consistent simulation and controlled inversion benchmark，而不是代码说明、工程日志或模型堆砌。

---

## 1. 必须遵守的硬边界

1. 不发明方法细节、实验结果、参数或数据规模。
2. 不把 clean rendered images 写成真实望远镜图像。
3. 不宣称真实光学望远镜验证。
4. 不写 fusion universally superior。
5. 不写 OCS always better than images。
6. 不把 ISAR 并入 Method 主线。
7. 不写成代码文件说明，不要逐个列 Python 脚本。
8. 不在 Method 中过度解释性能结果，具体数值留到 Results。
9. 对不确定方法细节用 `[需要作者确认：...]` 标注。

---

## 2. Method 章节推荐结构

请按以下小节组织：

```text
3.1 Overview of the unified OCS-image simulation framework
3.2 Satellite geometry and attitude parameterization
3.3 Observation geometry and data generation protocol
3.4 Nonuniform material assignment and GGX BRDF
3.5 Self-occlusion and visibility modeling
3.6 OCS integration and feature construction
3.7 Photometric image generation
3.8 Attitude inversion models
    3.8.1 OCS-only MLP
    3.8.2 Image-only CNN / ResNet
    3.8.3 Late fusion
    3.8.4 Feature fusion
3.9 Data splits, metrics, and reproducibility settings
```

写作原则：

- 每个模块都回答三件事：How it runs / Why it is needed / Why it works。
- 先写模块设计，再写动机和优势。
- 每段首句说明本段任务。
- 方法边界必须写清楚。
- 不要在 Method 中写 Results 的性能数值。

---

## 3. 当前可用项目事实

### 3.1 总体框架

本文建立统一 forward model，使 OCS signatures 和 photometric images 共享：

- same satellite geometry
- same attitude definition
- same material assignment
- same GGX/Cook-Torrance BRDF
- same illumination and viewing geometry
- same self-occlusion / visibility assumptions

本文是 controlled simulation benchmark，不是 field telescope validation。

### 3.2 几何与姿态

可写事实：

- 使用真实卫星 STL 几何。
- 模型包含三个部件：metal body、solar panel、baffle/shade。
- 面元级几何用于 OCS 积分。
- 姿态用 yaw-pitch 表示，roll 在当前 benchmark 中固定。
- 主要姿态网格为 5°：yaw `73` 个采样，pitch `37` 个采样，共 `2701` 个 yaw-pitch attitudes。
- 反演使用 10°→5° split 测试内插泛化。
- 项目总览中已有旋转约定：`R = Rz(yaw) @ Ry(pitch) @ Rx(roll)`，Z-Y-X 内旋；正式稿仍可标 `[需要作者确认：Euler order / matrix convention]`。

必须写清楚：

```text
The present benchmark estimates yaw and pitch under fixed roll, and therefore does not claim full 3-DOF pose recovery.
```

### 3.3 观测几何

可写事实：

- OCS 端使用多观测几何。
- 多观测几何基线包含 5 组 sun-sensor geometries。
- 相位角覆盖约 `24°-120°`。
- 图像主分支主要基于 phase63 / one photometric image branch。
- 不能把 phase63 写成多相位图像泛化。

安全表述：

```text
The main image branch uses one rendered photometric phase for controlled benchmarking, whereas OCS signatures are evaluated across multiple observation geometries.
```

### 3.4 材料与 BRDF

可写事实：

- 材料为非均匀分区：metal body、solar panel、baffle/shade。
- 使用 GGX/Cook-Torrance BRDF 作为论文主模型。
- LegacyPhong 只可作为历史/兼容 baseline，不要作为主模型。
- GGX nominal 参数包括：
  - metal body: `metallic=1`, `roughness=0.20`, `F0=0.91`
  - solar panel: `metallic=0`, `roughness=0.40`, `ior=1.5`
  - baffle/shade: `metallic=0`, `roughness=0.90`, `base_color=0.08`
- 材料参数为 nominal，需要文献和 sensitivity analysis 支撑。

必须降调：

```text
These parameters are used as nominal material settings for controlled simulation, not as calibrated measurements of the specific target.
```

### 3.5 Self-occlusion and visibility

可写事实：

- OCS 使用解析射线查询做面元级自遮挡判断。
- 对每个面元，分别沿 sun direction 和 detector direction 做 visibility query。
- 只有同时满足 illumination visibility 和 detector visibility 的面元才贡献 OCS。
- 使用 epsilon / minimum hit distance 过滤自相交或近距离网格噪声。
- 当前安全值为 `epsilon = 1.0 mm` 和 `min_hit_distance = 1.0 mm`。
- 该值来自合成几何验证和真实三部件模型的敏感性扫描。
- 模块 A 与 Blender 独立 ray-cast 有人工抽查交叉验证。

可写验证事实：

- Single-plate tests suppress self-intersection.
- Double-plate, U-block, and nested-cylinder synthetic tests verify cross-part and internal occlusion.
- Blender manual review confirms agreement for sampled cases.

不要写：

- 不要说遮挡模型已用真实望远镜数据验证。
- 不要把开发阶段异常和代码排查细节写进正文。

### 3.6 OCS integration

OCS 公式可写为：

```text
OCS = sum_i A_i f_r(n_i, l, v) max(n_i·l, 0) max(n_i·v, 0) V_i(l) V_i(v)
```

其中：

- `A_i` is facet area.
- `f_r` is the GGX/Cook-Torrance BRDF.
- `n_i` is facet normal.
- `l` and `v` are illumination and viewing directions.
- `V_i(l)` and `V_i(v)` are binary visibility terms for illumination and viewing.

可以说明 OCS features：

- total OCS features
- per-part OCS features
- log-transformed features
- `all_raw`, `per_part_log`, `total_log`

注意：

- `all_raw 45D` 含遮挡率/额外信息，只能写成 semi-oracle upper bound。
- `per_part_log` 是主要实用 OCS setting。
- 不要在 Method 里提前写结果数值。

### 3.7 Photometric image generation

可写事实：

- 图像由 Blender / rendering pipeline 生成。
- 图像为 clean rendered photometric images。
- 图像分辨率为 `128 x 128`。
- 图像和 OCS 来自同一几何、姿态、材料、BRDF 和观测设置。
- 图像主分支使用 phase63。
- clean images 不含 atmosphere、detector response、PSF、earthshine、background contamination。

可以写：

```text
The rendered images are used to create an idealized upper-bound setting for image-based inversion.
```

不能写：

```text
The rendered images reproduce real telescope images.
```

### 3.8 Inversion models

请按模型组写，不要写成代码说明。

#### OCS-only model

可写：

- MLP regression using OCS feature vectors.
- Target encoded with periodic representation for yaw and pitch, e.g. sin/cos。
- Feature variants: `total_log`, `per_part_log`, `all_raw`。
- `all_raw 45D` 是 semi-oracle upper bound，不作为现实观测主结论。
- `per_part_log` 是主要实用 OCS setting。

#### Image-only model

可写：

- TinyCNN as lightweight image baseline。
- ResNet-18 as stronger image model for clean synthetic upper-bound evaluation。
- Single-channel `128 x 128` photometric image input。
- Output yaw-pitch attitude representation。

注意：

- TinyCNN 不能代表图像能力上限。
- ResNet clean result 是 idealized upper-bound。

#### Late fusion

可写：

- Prediction-level fusion。
- Combines OCS and image predictions in periodic yaw-pitch space。
- Uses beta / weight sweep to test tradeoff。

不要写成 universal best。

#### Feature fusion

可写：

- Two-branch model: image branch + OCS branch + fusion head。
- Image branch extracts image features; OCS branch embeds OCS feature vector; fusion head predicts yaw-pitch representation。
- Used to test whether feature-level complementarity exists。

边界：

```text
Feature fusion is a benchmarked fusion strategy, not asserted as universally optimal.
```

### 3.9 Data split and metrics

可写事实：

- Use 10°→5° split。
- Training pool uses coarser 10° attitude grid。
- Test set uses remaining 5° intermediate attitudes。
- This tests interpolation rather than simple memorization。
- Multiple random seeds are used for neural models。
- Metrics include:
  - mean angular error in degrees
  - standard deviation across seeds
  - Hit@5°
  - Hit@10°
  - P90 / worst-case where relevant

需要解释角度误差：

- yaw is periodic。
- pitch is bounded。
- angular error should account for spherical / yaw-pitch geometry。若不确定公式细节，用 `[需要作者确认：angular error formula]`。

---

## 4. Method 中必须写清楚的边界

请在 Overview 或 Method 末尾明确写：

```text
The present study focuses on yaw-pitch inversion under fixed roll.
The clean rendered images are used for controlled benchmarking.
Real telescope images are not used.
Atmosphere, detector response, optical PSF, earthshine, and background contamination are not explicitly modeled.
The main image branch uses one rendered phase condition, while broader cross-phase image generalization is left for future work.
The material parameters are nominal rather than target-calibrated.
```

---

## 5. 请输出的内容

请按以下格式一次性输出完整 Markdown。

### A. Method Logic Map

用 8-12 条说明 Method 如何支撑论文主线。

### B. Pipeline Figure Sketch

用文字描述 Fig. 1 或 Method pipeline 图，至少包含：

```text
STL geometry -> material assignment -> attitude + observation geometry -> GGX BRDF + visibility -> OCS signatures + photometric images -> inversion models -> metrics
```

### C. Section Outline

对 3.1-3.9 每节写：

- section goal
- key inputs
- key operations
- key outputs
- boundary/risk

### D. Method Draft

写英文 Method 初稿。建议总长 `1700-2500 words`。要求：

- 以可复现方法为主，不要像代码说明。
- 每节至少 1-2 段。
- 公式只写必要的 OCS / BRDF / visibility / target encoding。
- 不要放 Results 性能数值。
- 对不确定的工程细节使用 `[需要作者确认：...]`。

### E. Method Variables and Notation Table

生成表格：

| Symbol / term | Meaning | Unit / range | Used in |
|---|---|---|---|

至少包含：

- `A_i`
- `n_i`
- `l`
- `v`
- `f_r`
- `V_i(l)`
- `V_i(v)`
- yaw
- pitch
- roll
- OCS
- `per_part_log`
- `all_raw`
- Hit@5

### F. Reproducibility Checklist

列出正文或补充材料需要报告的参数：

- STL source / geometry units
- component segmentation
- material parameters
- BRDF model
- observation geometries
- yaw/pitch grid
- roll setting
- self-occlusion settings
- image resolution
- split rule
- model families
- metrics
- random seeds

### G. Claim-Evidence-Risk Map

列出 Method 中最容易被审稿人质疑的 claims：

- unified physical consistency
- self-occlusion correctness
- nominal material validity
- clean image upper-bound
- fixed roll limitation
- one-phase image branch
- semi-oracle all_raw boundary
- fusion as benchmark strategy

### H. Self-review Checklist

检查：

1. 是否写成代码说明？
2. 是否发明参数？
3. 是否宣称真实光学验证？
4. 是否说明 fixed roll？
5. 是否说明 clean image upper-bound？
6. 是否区分 all_raw semi-oracle 和 per_part_log practical OCS setting？
7. 是否把 fusion 写成 benchmark strategy 而非 universal best？
8. 是否没有在 Method 中提前写 Results 性能数值？

### I. Questions for Author

最多提出 6 个需要作者确认的问题。

---

## 6. 推荐英文口径

可用表述：

```text
We use the forward model to generate both scalar OCS signatures and resolved photometric images from the same geometry, attitude, material, BRDF, and visibility assumptions.
```

```text
The rendered images are not intended to reproduce field telescope images; instead, they define an idealized and controlled image-based upper-bound setting.
```

```text
The inversion models are used as controlled probes of modality information rather than as claims of a universally optimal architecture.
```

```text
The all_raw OCS representation includes additional diagnostic quantities and is therefore treated as a semi-oracle upper bound.
```

避免表述：

```text
Our rendered images are equivalent to real telescope observations.
Our fusion model is the proposed best method in all conditions.
The material parameters are calibrated for the actual target.
The benchmark solves full 3-DOF pose estimation.
```

---

## 7. 输出文件命名

完成后请把输出保存为：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\Claude交互\claude writing\04_Step4_Claude输出_Method.md
```

如果不能直接保存文件，则把完整 Markdown 内容返回给作者，由作者保存。
