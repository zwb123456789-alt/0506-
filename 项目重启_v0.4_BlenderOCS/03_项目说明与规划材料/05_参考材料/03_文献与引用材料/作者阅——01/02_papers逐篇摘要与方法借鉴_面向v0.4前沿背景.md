# papers 文件夹逐篇摘要与方法借鉴

生成日期：2026-07-06

来源目录：

```text
03_项目说明与规划材料/05_参考材料/03_文献与引用材料/papers/
```

用途：面向本项目 v0.4 BlenderOCS 方向，逐篇整理 `papers` 文件夹中文献的研究问题、方法、主要结果，以及对本项目可借鉴或可对比之处。本文用于作者后续阅读文献、总结方法和理解前沿背景，不是路线裁决，不改写论文正文。

重要说明：

- 本文覆盖当前 `papers` 文件夹内 58 篇 PDF。
- 条目按 PDF 文件名对应，便于回到文件夹打开原文。
- 摘要以 PDF 首页、摘要、方法段落和题名为依据做中文归纳；少数老文或会议文摘要段落无法自动抽取，已按题名和首页信息人工归纳。
- 有 3 篇文件内容与文件名或本项目主题明显不匹配，已放入“疑似不相关/需核查”部分，避免误导后续阅读。
- 本项目红线仍然有效：不得把 v0.4 写成真实未知目标完整姿态反演系统；不得把 GEO 光度库写成有三轴姿态真值的监督数据集；不得把光度负结果写成“光度无用”。

## 1. 快速分类导览

| 类别 | 主要用途 | 代表文件 |
|---|---|---|
| 图像姿态估计与 domain gap | 支撑 image-only baseline、图像通道饱和、synthetic-to-real 边界 | `2305.07348v3.pdf`, `ASR_2024_Park_DAmico_SPNv2_domain_gap_pose_estimation.pdf`, `1-s2.0-S0094576525002176-main.pdf` |
| 光变/光度姿态反演 | 支撑 OCS/photometry 的物理意义、多解性和跨几何价值 | `1-s2.0-S0273117725013961-main.pdf`, `s40295-025-00557-9.pdf`, `Burton 2024.pdf` |
| 物理前向、BRDF、材料和仿真验证 | 支撑 BlenderOCS shared forward model、材料/光路解释 | `aerospace-09-00403-v2.pdf`, `lu2024_brdf_starlink.pdf`, `Fankhauser_2023_Satellite_Optical_Brightness_arXiv2305.11123.pdf` |
| 置信、不确定性和候选集 | 支撑 conformal、置信一致性、失败边界写法 | `1-s2.0-S1270963825001269-main.pdf`, `FnTML_2023_Angelopoulos_Bates_conformal_prediction_intro.pdf`, `ICML_2017_Guo_calibration_modern_neural_networks.pdf` |
| 真实观测/实验室数据 | 支撑真实光度只做锚点、不写成监督姿态真值 | `1-s2.0-S0094576526000391-main.pdf`, `Kumar_2025_Light_curves_sequential_comparison_ActaAstronautica_10.1016-j.actaastro.2025.04.018.pdf`, `Wang 2024.pdf` |

## 2. 图像姿态估计与 domain gap

### 2.1 `2305.07348v3.pdf`

文章：A Survey on Deep Learning-Based Monocular Spacecraft Pose Estimation: Current State, Limitations and Prospects

- **针对的问题**：综述非合作航天器单目图像姿态估计，重点讨论深度学习方法在在轨服务、碎片移除等任务中的潜力和限制。
- **使用的方法**：按方法路线整理 hybrid modular pipeline、direct end-to-end regression、关键点/PnP、数据集、仿真器、实验平台和 domain gap 问题。
- **主要结果/结论**：当前方法在 benchmark 上进展明显，但 real deployment 仍受 synthetic-to-real domain gap、算力、模型大小、验证数据不足和真实场景泛化限制。
- **对本项目的借鉴**：适合作为 image-only 通道的总背景文献。可借鉴其分类框架，把本项目图像通道写成“单目图像姿态信息基线”，并强调 v0.4 不追求真实在轨部署，而是在 model-known 仿真协议下研究图像与 OCS 光度的互补性。
- **可对比点**：该综述强调图像姿态估计依赖渲染数据和 domain gap；本项目可将 OCS 作为另一类同源物理观测，比较其在跨几何条件下是否补充图像通道。

### 2.2 `Acta_2021_PasqualettoCassinis_CNN_pose_tightly_loosely_coupled.pdf`

文章：Evaluation of tightly- and loosely-coupled approaches in CNN-based pose estimation systems for uncooperative spacecraft

- **针对的问题**：非合作航天器近距离操作中，如何用单目图像和 CNN 框架实现鲁棒相对姿态估计，并比较 tightly-coupled 与 loosely-coupled 方案。
- **使用的方法**：结合 CNN 特征/关键点估计与几何位姿求解，比较不同耦合方式在姿态估计系统中的表现。
- **主要结果/结论**：CNN-based 姿态估计可以服务非合作目标，但耦合方式、几何约束和中间表示会显著影响鲁棒性。
- **对本项目的借鉴**：可作为 image-only baseline 与 joint 结构讨论的早期依据。它提示后续写作应区分“图像特征提取”和“物理/几何约束求解”，不要把神经网络当成唯一贡献。
- **可对比点**：本文是视觉姿态估计框架比较；v0.4 可对比“图像几何通道”与“跨几何 OCS 光度通道”各自提供的信息类型。

### 2.3 `Acta_2023_Bechini_dataset_generation_validation_spacecraft_pose.pdf`

文章：Dataset generation and validation for spacecraft pose estimation via monocular images processing

- **针对的问题**：单目航天器姿态估计算法受限于高质量空间图像数据集不足。
- **使用的方法**：构建高保真合成图像生成工具，基于开源光线追踪，讨论几何、材料、渲染时间、光学属性调参和验证流程。
- **主要结果/结论**：合成数据集经过定性和定量验证后，可为图像导航算法训练与测试提供更有代表性的 benchmark。
- **对本项目的借鉴**：这是 BlenderOCS 论文 Method 写作的重要参照。v0.4 必须清楚交代 CAD、材料、姿态网格、sun/view 几何、相机/探测器和光度积分，不能只说“用 Blender 生成数据”。
- **可对比点**：该文重在图像数据集真实性验证；v0.4 可扩展为“同一物理前向模型同时生成图像和 OCS 光度向量”。

### 2.4 `1-s2.0-S0094576523006185-main.pdf`

文章：Robust spacecraft relative pose estimation via CNN-aided line segments detection in monocular images

- **针对的问题**：非合作航天器单目相对位姿初始化需要高精度，但重型 CNN 计算成本高，传统几何方法又对图像质量敏感。
- **使用的方法**：先用目标检测 CNN 定位目标，再用线段检测 CNN 提取结构线段，通过几何分组、复杂 perceptual groups 和匹配矩阵求解位姿。
- **主要结果/结论**：在 benchmark 中达到较高精度和解算可用率，误差主要受相对姿态估计影响，某些目标轴方向存在几何歧义。
- **对本项目的借鉴**：该文的“学习局部结构 + 显式几何求解”路线值得借鉴。v0.4 的图像通道可以被解释为形状投影/边缘/几何结构信息，而 OCS 提供积分光度响应。
- **可对比点**：图像方法在可见结构清楚时强；OCS 光度可能在多几何时提供额外约束，但不一定在 single-frame 下有效。

### 2.5 `1-s2.0-S0094576524002017-main.pdf`

文章：AI-based monocular pose estimation for autonomous space refuelling

- **针对的问题**：自主空间加注/对接任务中，能否用低成本单目相机替代或补充主动传感器进行位姿估计。
- **使用的方法**：比较多个 CNN backbone，用视觉输入回归位置和姿态，采用 6D attitude representation，并从软件验证、硬件验证和集成验证角度评估。
- **主要结果/结论**：在受控场景中能达到较好的位置和姿态精度，说明 AI-based 单目视觉在自主加注中有可行性。
- **对本项目的借鉴**：可借鉴“软件-硬件-集成”分层验证写法。v0.4 当前仍是纯仿真，应避免借用该文的工程部署语气，但可借鉴其 direct vs indirect method 的讨论。
- **可对比点**：该文是单目图像姿态估计工程化路线；v0.4 更偏科学问题，即图像和 OCS 的观测信息互补性。

### 2.6 `1-s2.0-S0094576525002176-main.pdf`

文章：Robust and efficient single-CNN-based spacecraft relative pose estimation from monocular images

- **针对的问题**：现有 AI 姿态估计算法常优先追求精度，计算效率和 synthetic-to-real 泛化不足。
- **使用的方法**：提出单个 multitask CNN，同时处理检测/关键点等任务；用 confidence score 做 outlier rejection，并引入模拟真实传感器噪声的数据增强。
- **主要结果/结论**：在 synthetic SPEED 图像上性能强，在 SPEED+ mock-up 图像上也保持竞争力，说明传感器噪声增强和多任务结构有助于 domain gap。
- **对本项目的借鉴**：可作为 image baseline 和 augmentation 消融写法参考。尤其是“传感器噪声增强不是装饰，而是针对 domain gap 的物理扰动”这一点，适合 v0.4 的 degraded protocol。
- **可对比点**：该文针对图像 domain gap；v0.4 可对比 OCS 光度在 material/roll/degraded 下的稳定性。

### 2.7 `1-s2.0-S0094576525006836-main.pdf`

文章：Hybrid deep learning based monocular pose estimation for autonomous space docking operations

- **针对的问题**：自主空间对接需要可靠、可解释、能在真实实验场景中工作的单目姿态估计。
- **使用的方法**：CNN 预测关键点或中间特征，再结合 PnP、RANSAC outlier rejection 和 soft dataset regularization；比较 ResNet、MobileNet、EfficientNet、HRNet 等 backbone，并用合成和真实实验数据验证。
- **主要结果/结论**：混合式 CNN+PnP 方法在精度和可解释性上优于纯直接回归，并能在受控真实实验场景中展示可用性。
- **对本项目的借鉴**：后续如果写 image/joint，应强调几何约束和物理约束的重要性。该文也提供了“多 backbone 对比 + 合成/真实验证”的实验组织方式。
- **可对比点**：该文处理 docking 近距离图像；v0.4 是远距离/积分光度信息与图像通道的仿真可观测性研究，不能直接类比工程精度。

### 2.8 `2212.12103v1.pdf`

文章：Bridging the Domain Gap in Satellite Pose Estimation: a Self-Training Approach based on Geometrical Constraints

- **针对的问题**：卫星姿态估计在 synthetic-to-real domain gap 下性能下降，真实图像标注昂贵。
- **使用的方法**：用几何约束构建 self-training 框架，先预测 2D keypoints，再用 PnP 求解姿态；把目标域姿态作为 latent variable，通过 pseudo-label generation 和网络训练迭代优化，并引入细粒度分割缓解稀疏关键点信息损失。
- **主要结果/结论**：方法能在目标域适配，且在 SPEC2021 sunlamp 任务中表现突出。
- **对本项目的借鉴**：可借鉴“几何一致性 + pseudo-label”的 domain gap 思路。若未来路线二/真实图像锚点启动，可考虑不依赖真实三轴真值的自监督/弱监督一致性。
- **可对比点**：该文用图像几何约束跨域；v0.4 的 OCS 可以探索 photometric consistency 是否也能作为弱约束，但不能写成已有监督反演。

### 2.9 `1-s2.0-S0273117724004368-main.pdf`

文章：PVSPE: A pyramid vision multitask transformer network for spacecraft pose estimation

- **针对的问题**：传统 CNN 在航天器姿态估计中对远程视觉注意力和复杂结构建模不足，影响准确性和鲁棒性。
- **使用的方法**：提出 pyramid vision multitask transformer network，引入 transformer 注意力和多任务输出以提升姿态估计。
- **主要结果/结论**：端到端多任务 transformer 对 SPE 任务有性能提升，表明视觉 attention 对复杂航天器结构有价值。
- **对本项目的借鉴**：可作为更强 image-only baseline 的背景。v0.4 若 image_only 已接近饱和，需要说明 joint 增益受 image ceiling 限制，而不是简单归咎 OCS。
- **可对比点**：视觉 attention 捕获形状结构；OCS 多几何捕获光度响应。二者观测信息不同，适合互补性讨论。

### 2.10 `ASR_2024_Park_DAmico_SPNv2_domain_gap_pose_estimation.pdf`

文章：Robust multi-task learning and online refinement for spacecraft pose estimation across domain gap

- **针对的问题**：非合作航天器图像姿态估计跨 synthetic/real domain gap 时精度下降。
- **使用的方法**：SPNv2 采用 multi-scale、multi-task CNN，共享特征编码器，多个预测头同时做 keypoint、direct pose、segmentation 等任务，并结合强数据增强和 online domain refinement。
- **主要结果/结论**：多任务结构和在线 refinement 能显著提升跨域性能，是 SPEED+ 方向的重要基线。
- **对本项目的借鉴**：非常适合借鉴其 protocol 写法：训练域、目标域、任务头、增强、online refinement、跨域测试必须清楚分开。
- **可对比点**：SPNv2 解决的是图像 domain gap；v0.4 可以把 degraded/mroll/yaw-block 写成 OCS 和图像通道的信息边界协议。

### 2.11 `IEEEAero_2022_Park_SPEEDplus_spacecraft_pose_domain_gap.pdf`

文章：SPEED+: Next-Generation Dataset for Spacecraft Pose Estimation across Domain Gap

- **针对的问题**：缺少能系统评估 synthetic-to-real domain gap 的航天器姿态估计数据集。
- **使用的方法**：构建 SPEED+ 数据集，包含合成、lightbox、sunlamp 等域，服务 SPEC2021 等 benchmark。
- **主要结果/结论**：SPEED+ 使社区能够在统一数据和指标上测试跨域姿态估计算法。
- **对本项目的借鉴**：写 v0.4 数据协议时应学习这种“域”和“协议”清楚命名的方式。比如 clean/degraded、P-INT/P-EXT、L1-G1/G3/G5、M-roll 需要成为可复现实验协议，而不是口头描述。
- **可对比点**：SPEED+ 是图像域迁移 benchmark；v0.4 可类比构建 OCS 多几何可观测性 benchmark。

### 2.12 `TAES_2022_Rondao_ChiNet_multimodal_spacecraft_pose.pdf`

文章：ChiNet: Deep Recurrent Convolutional Learning for Multimodal Spacecraft Pose Estimation

- **针对的问题**：单帧图像姿态估计没有利用 rendezvous 序列中的时序信息，多模态 RGB/LWIR 信息融合不足。
- **使用的方法**：CNN backbone 提取图像特征，LSTM 建模序列时序，融合 RGB 与 thermal infrared，并采用 coarse-to-fine 训练策略。
- **主要结果/结论**：时序与多模态输入能使姿态估计更连续、更鲁棒，在合成数据和实验数据上验证了 pipeline。
- **对本项目的借鉴**：可作为“多观测比单观测更有信息”的视觉证据。v0.4 的 L1-G1/G3/G5 多几何 OCS 与该文的 temporal/multimodal 思路有类比价值。
- **可对比点**：ChiNet 融合图像模态和时间；v0.4 融合图像与跨几何光度向量。二者都需要证明融合是否带来真实增益。

### 2.13 `sosa2025_vit_6dof.pdf`

文章：Motion Aware ViT-based Framework for Monocular 6-DoF Spacecraft Pose Estimation

- **针对的问题**：多数单目 6-DoF 姿态估计只用静态单帧关键点，忽略空间任务中的连续运动信息。
- **使用的方法**：将 human pose estimation 中的 motion-aware heatmap、optical flow 和 ViT 框架迁移到航天器姿态估计。
- **主要结果/结论**：时序运动信息能改善单目姿态估计，尤其在连续序列场景下有价值。
- **对本项目的借鉴**：适合作为未来光变/时序方向背景，不应并入当前路线一 C 必做闭环。
- **可对比点**：该文用图像时序；路线四未来方向可考虑光度时序与姿态运动耦合。

### 2.14 `behari2023_sundial.pdf`

文章：SUNDIAL: 3D Satellite Understanding through Direct, Ambient, and Complex Lighting Decomposition

- **针对的问题**：遥感卫星影像 3D 建模受多视角基线有限、光照复杂、场景变化等影响。
- **使用的方法**：将直接光、环境光和复杂光照分解，用于改进 3D satellite imagery understanding。
- **主要结果/结论**：光照分解有助于在复杂成像条件下理解三维结构。
- **对本项目的借鉴**：主题不是 RSO 姿态反演，但“光照分解”概念可启发三轴最亮构型的光路解释：直接太阳入射、环境/地照、材料反射需要区分。
- **可对比点**：该文关注地表/遥感 3D 建模，不应作为本项目空间目标光变反演核心引用。

## 3. 光变/光度姿态反演与空间目标表征

### 3.1 `ASR_2022_Clark_RSO_attitude_optical_property_light_curves.pdf`

文章：Resident space object (RSO) attitude and optical property estimation from space-based light curves

- **针对的问题**：低分辨率空间基光学观测能否用于估计 RSO 的形状、姿态和光学属性。
- **使用的方法**：用 space-based image simulator 生成 RSO light curves，采用 Phong/BRDF 类光学模型，通过迭代比较观测 light curve 和 simulated light curve 进行反演。
- **主要结果/结论**：在已知或有限先验条件下，space-based light curves 可用于估计姿态和光学属性，但问题依赖形状、材料和几何假设。
- **对本项目的借鉴**：是 OCS/光度主线的重要背景。它证明光度信号可以携带姿态和材料信息，但也说明必须写清 known shape/material/geometries。
- **可对比点**：该文使用时序 light curve；v0.4 使用跨几何 OCS 光度向量。两者都应强调物理前向模型和多解性。

### 3.2 `1-s2.0-S0273117724010640-main.pdf`

文章：Attitude motion classification of resident space objects using light curve spectral analysis

- **针对的问题**：如何从 RSO light curves 推断姿态运动类型，而不是直接求解完整姿态。
- **使用的方法**：对 light curve 做频谱分析，提取周期和频率特征，用于姿态运动分类。
- **主要结果/结论**：频谱特征能支持姿态运动分类，但 light curve inversion 受噪声、数据缺口、形状/材料/姿态耦合影响。
- **对本项目的借鉴**：提示光度通道可以用于“运动/信息状态判断”，不一定必须承担完整姿态回归。v0.4 的低信息/高信息区域、置信一致性与此思路一致。
- **可对比点**：该文是频域 motion classification；v0.4 是姿态可观测性和多几何光度向量约束。

### 3.3 `1-s2.0-S0273117725013961-main.pdf`

文章：Attitude estimation of uncontrolled space objects: A Bayesian-informed swarm intelligence approach

- **针对的问题**：非受控空间物体的姿态估计对再入、碰撞风险和碎片减缓很重要，但 light curve inversion 非线性强、多解且易受噪声影响。
- **使用的方法**：提出 Bayesian-informed swarm intelligence / AISwarm-UKF 类方法，将全局搜索和贝叶斯滤波结合，用 light curve 估计姿态状态。
- **主要结果/结论**：该方法在模拟/受控条件下能更稳健地处理 uncontrolled object light curve attitude estimation。
- **对本项目的借鉴**：可作为 OCS/P-DB/retrieval 的对照背景：当光度反演非凸、多解时，全局搜索和候选集比单一神经回归更自然。
- **可对比点**：该文面向时序 light curve；v0.4 可用跨几何离散光度向量做信息约束，不等同于连续时序滤波。

### 3.4 `1-s2.0-S0273117722010493-main.pdf`

文章：The adaptive Gaussian mixtures unscented Kalman filter for attitude determination using light curves

- **针对的问题**：light curve measurement model 非线性强，姿态后验可能非高斯、多峰，传统 UKF 难以表达。
- **使用的方法**：Adaptive Gaussian Mixtures UKF，用高斯混合表示状态概率密度，通过 non-linearity index 自适应拆分和合并高斯核。
- **主要结果/结论**：AGMUKF 能在保持混合核数量可控的同时表示复杂、多峰、不对称后验。
- **对本项目的借鉴**：非常适合支持“光度姿态问题天然多解，不能只看单点回归”的叙事。v0.4 的 conformal set/P-DB candidate set 可类比为 ambiguity-aware 输出。
- **可对比点**：AGMUKF 是递推滤波；v0.4 当前是离线 benchmark 和多几何观测，不需要写成动态滤波系统。

### 3.5 `s40295-025-00486-7.pdf`

文章：Particle Swarm Optimization on the Space of Quaternions with Applications to Attitude Estimation from Light Curves

- **针对的问题**：姿态四元数位于非欧氏空间，传统 particle swarm optimization 直接加法更新不适合姿态搜索；light curve 姿态估计又是非凸问题。
- **使用的方法**：提出 multiplicative PSO，在四元数流形上用乘法姿态运动更新粒子，并用于 light curve 姿态和角速度估计。
- **主要结果/结论**：MPSO 能更自然地处理姿态空间搜索，在多观测 light curve 场景下可估计姿态和角速度。
- **对本项目的借鉴**：如果后续要做 OCS 反演或最亮构型全局搜索，姿态空间应按 SO(3)/四元数几何处理，而不是简单欧氏回归。
- **可对比点**：MPSO 可作为非神经、物理前向驱动的强 baseline 思路；v0.4 的 P-DB/retrieval 与其同属 model-based search。

### 3.6 `Burton 2024.pdf`

文章：Light curve attitude estimation using particle swarm optimizers

- **针对的问题**：仅用 unresolved light curve 估计空间物体姿态存在多解、非线性和局部最优问题。
- **使用的方法**：比较 particle swarm optimizer 及其变体，用已知形状/轨道条件下的 light curve 估计姿态。
- **主要结果/结论**：PSO 类方法能作为 light curve attitude estimation 的全局优化工具，但性能依赖几何、噪声和先验条件。
- **对本项目的借鉴**：可作为 OCS-only 非神经优化基线的背景；强调物理前向模型 + 搜索比单纯监督回归更可解释。
- **可对比点**：v0.4 的 P-DB 检索可以和 PSO 类方法共同支持“光度反演应看候选集合和搜索空间”。

### 3.7 `s40295-025-00557-9.pdf`

文章：A Direct Light Curve Inversion Scheme in the Presence of Measurement Noise and Inertia Uncertainty

- **针对的问题**：真实 light curve 受到背景、传感器、湍流、shot noise 等噪声影响，且目标几何对称和材料不确定会导致无穷多姿态可能对应同一亮度。
- **使用的方法**：在已知形状和材料的前提下，对全姿态空间进行高效搜索，输出满足观测和噪声条件的解集合，而不是强行给唯一姿态。
- **主要结果/结论**：ambiguity-aware 的候选集合能更真实地表达 light curve attitude inversion 的不确定性和多解性。
- **对本项目的借鉴**：这是 v0.4 写置信集、低信息区域、P-DB 和 exact-bin 哨兵指标的关键参考。不要把失败写成“无信息”，应写成观测协议下候选集合无法充分收缩。
- **可对比点**：该文是时序 light curve；v0.4 可把跨几何 OCS 写成离散多观测光度向量，分析候选姿态集随几何数收缩。

### 3.8 `ESA_SDC8_2019_two_methods_light_curve_inversion_space_debris.pdf`

文章：Two Methods for Light Curve Inversion for Space Object Attitude Determination

- **针对的问题**：在目标形状和轨道已知但只有 light curve 的情况下，如何估计空间目标姿态和旋转。
- **使用的方法**：提出两种 light curve inversion 方法，一种从每个亮度测量对应的可能姿态集合构造时间历史，另一种用优化/搜索方式估计姿态运动。
- **主要结果/结论**：light curve 可以用于姿态估计，但多解性和观测几何使问题本质困难。
- **对本项目的借鉴**：适合支持“光度反演不是单点确定问题，而是候选集约束问题”的写法。
- **可对比点**：v0.4 的 exact-bin 负结果可以与该类候选集合方法对比，说明严格单点分类不是唯一评价口径。

### 3.9 `JGCD_2009_Wetterer_Jah_attitude_determination_light_curves.pdf`

文章：Attitude Estimation from Light Curves

- **针对的问题**：能否用未分辨光变曲线估计空间目标姿态。
- **使用的方法**：使用 UKF 等滤波框架，把 light curve 作为观测量，并结合光度前向模型估计姿态状态。
- **主要结果/结论**：证明 light curve attitude estimation 在理论和仿真层面可行，但依赖目标模型、反射模型和观测几何。
- **对本项目的借鉴**：这是空间目标 light curve 姿态估计的基础文献。v0.4 应引用其作为光度信号含姿态信息的早期依据。
- **可对比点**：该文是动态滤波；v0.4 当前更适合写成静态/多几何 benchmark，不应直接宣称动态定姿系统。

### 3.10 `TAES_2017_Piergentili_attitude_lightcurve_measurements.pdf`

文章：Attitude Determination of Orbiting Objects from Lightcurve Measurements

- **针对的问题**：如何利用 lightcurve measurements 判断在轨目标姿态。
- **使用的方法**：构建虚拟现实/仿真工具，生成不同姿态下的 light curves，并与观测或模拟测量比较。
- **主要结果/结论**：光变测量可以支持姿态确定，但要求较好的几何、形状和光学建模。
- **对本项目的借鉴**：可作为“仿真库/查表/匹配”式光度姿态估计的早期对照。
- **可对比点**：v0.4 的 OCS 数据库和 P-DB 检索可与这类仿真匹配方法建立背景联系。

### 3.11 `JGCD_2014_Linares_shape_tracking_lightcurve_angles.pdf`

文章：Space Object Shape Characterization and Tracking Using Light Curve and Angles Data

- **针对的问题**：仅靠轨道角度观测或 light curve 难以完整表征空间目标形状和姿态。
- **使用的方法**：将 light curve 与 angles data 融合，用递推估计/滤波方法同时跟踪形状和状态。
- **主要结果/结论**：多源观测融合能增强空间目标形状和姿态表征。
- **对本项目的借鉴**：支持“联合观测”思想：不同观测通道提供不同信息，应通过协议验证互补性，而不是默认融合有效。
- **可对比点**：该文融合 angles + light curve；v0.4 融合 image + OCS photometry。

### 3.12 `JGCD_2018_Coder_active_control_mode_lightcurve_inversion.pdf`

文章：Space-Object Active Control Mode Inference Using Light Curve Inversion

- **针对的问题**：从 light curve 判断空间目标是否处于不同 active control mode，而不是直接估计完整姿态。
- **使用的方法**：构建候选控制模式与 light curve inversion 框架，根据观测光变推断控制模式。
- **主要结果/结论**：light curve 可用于状态/模式识别，适合作为空间目标健康状态和行为表征的一部分。
- **对本项目的借鉴**：支持本项目谨慎口径：光度不一定要承担精确定姿，也可用于置信、异常、模式或信息区分。
- **可对比点**：路线四未来动态光变/姿态运动方向可参考，但当前不应并入路线一 C。

### 3.13 `JGCD_2023_Dianetti_Crassidis_polarized_light_curves.pdf`

文章：Resident Space Object Characterization Using Polarized Light Curves

- **针对的问题**：普通光变可能不足以区分材料/姿态/形状耦合，偏振光变是否能增强 RSO 表征。
- **使用的方法**：利用 polarized light curves 和偏振反射模型进行 RSO 表征。
- **主要结果/结论**：偏振信息为材料和表面反射提供额外观测维度，有助于缓解普通光度信息不足。
- **对本项目的借鉴**：说明“增加物理观测维度”是光度反演的重要方向。v0.4 当前 OCS 是多几何总光度，不是偏振/高光谱；后续 Discussion 可写成未来扩展。
- **可对比点**：偏振是通道增强；v0.4 的多几何是几何增强。

### 3.14 `1-s2.0-S0094576521000588-main.pdf`

文章：A transfer learning approach to space debris classification using observational light curve data

- **针对的问题**：能否用真实观测 light curve 对空间碎片形状进行数据驱动分类。
- **使用的方法**：用 simulated light curves 训练 1D CNN，再通过 transfer learning 适配 observational light curve data。
- **主要结果/结论**：1D CNN 能从光变中学习形状分类信息，但真实观测和仿真之间存在明显 domain gap，需要迁移学习。
- **对本项目的借鉴**：适合说明真实光度数据可用于分类/表征，但不等同于三轴监督姿态反演。路线二 GEO 光度锚点应保持这个谨慎口径。
- **可对比点**：该文是 shape classification；v0.4 是姿态可观测性和跨几何光度向量信息分析。

### 3.15 `1-s2.0-S0094576521003295-main.pdf`

文章：Full attitude state reconstruction of tumbling space debris TOPEX/Poseidon via light-curve inversion with Quanta Photogrammetry

- **针对的问题**：如何从真实观测 light curve 重建 TOPEX/Poseidon 失效卫星的 tumbling attitude state。
- **使用的方法**：使用 Quanta Photogrammetry，结合 SRP torque、旋转相位、角动量方向和光度观测进行姿态状态重建。
- **主要结果/结论**：在特定目标、特定物理模型和观测条件下，真实光变可用于重建 tumbling state。
- **对本项目的借鉴**：这是“真实案例可做，但强依赖目标先验和动力学模型”的典型例子。v0.4 不能据此宣称真实未知目标姿态反演。
- **可对比点**：该文是目标特例和动态反演；v0.4 是 model-known 仿真 benchmark。

### 3.16 `Kumar_2025_Light_curves_sequential_comparison_ActaAstronautica_10.1016-j.actaastro.2025.04.018.pdf`

文章：Light curves sequential comparison strategy for improved understanding of LEO uncontrolled objects

- **针对的问题**：在通常缺少目标几何和姿态真值的 LEO uncontrolled objects 场景下，如何利用多次 light curve 改善对目标旋转状态的理解。
- **使用的方法**：对 sequential light curves 做比较和频率分析，提取旋转周期、变化趋势和对象行为信息。
- **主要结果/结论**：顺序比较多次观测可以比单次 light curve 更可靠地理解 tumbling/rotation。
- **对本项目的借鉴**：支持“多观测/多几何”比单观测更有信息。也提示真实数据里更现实的任务常是趋势/周期/行为分析，而不是监督姿态真值回归。
- **可对比点**：路线二真实光度锚点可借鉴 sequential comparison，而不是强行做三轴监督姿态。

### 3.17 `AMOS_2019_Furfaro_shape_identification_light_curve_inversion.pdf`

文章：Shape Identification of Space Objects via Light Curve Inversion using Deep Learning

- **针对的问题**：如何通过 light curve 判断空间目标形状类别，服务 SSA 目标识别。
- **使用的方法**：基于仿真 light curves 和 deep learning 进行 shape identification。
- **主要结果/结论**：光变信号可用于形状类别识别，但这通常是分类或识别任务，不是完整姿态反演。
- **对本项目的借鉴**：可支持 OCS 光度向量具有目标/姿态相关信息这一背景，但要避免把形状分类结果外推为姿态精确估计。
- **可对比点**：v0.4 当前 target model known，不做 shape identification；因此此文更适合背景而非方法对照。

### 3.18 `AMOS_2024_deAndres_attitude_monitoring_three_axis_light_curves.pdf`

文章：Attitude determination and monitoring of three-axis controlled satellites with photometric observations

- **针对的问题**：三轴稳定卫星能否通过 photometric observations 做姿态确定和监测。
- **使用的方法**：在已知形状、尺寸和合理材料假设下，用光度观测与前向模型匹配，监测三轴受控卫星姿态。
- **主要结果/结论**：对三轴受控目标，光度观测在先验充分时可用于姿态监测。
- **对本项目的借鉴**：与三轴小项目最接近，但仍应注意它依赖 known shape/material assumptions。本项目三轴小项目应写成最亮构型和光路解释，不写成真实未知三轴反演系统。
- **可对比点**：该文是三轴监测；v0.4 可对比最亮构型的物理解释和高亮机制，而非直接 claim 定姿成功。

### 3.19 `aerospace2025_joint_estimation.pdf`

文章：Joint Estimation of Attitude and Optical Properties of Uncontrolled Space Objects from Light Curves Considering Atmospheric Effects

- **针对的问题**：估计 uncontrolled space objects 的姿态和光学反射属性时，大气影响和 AOD 等变量会干扰光变反演。
- **使用的方法**：建立考虑 atmospheric effects 的 light curve 模型，联合估计姿态和光学属性，并通过优化/数据分析方法求解。
- **主要结果/结论**：联合估计框架在现实条件模拟中可提高鲁棒性，但依赖已知形状、观测几何和大气建模。
- **对本项目的借鉴**：提示后续 Discussion 可把 atmosphere/material uncertainty 作为真实光度锚点的关键限制。
- **可对比点**：该文联合估计姿态和光学属性；v0.4 当前不估真实材料参数，只研究同源前向模型下通道信息。

### 3.20 `marto2024_hyperspectral_lightcurve.pdf`

文章：Hyperspectral Lightcurve Inversion for Attitude Determination

- **针对的问题**：普通单波段 light curve 对姿态和材料耦合敏感，高光谱 lightcurve 是否能改善姿态反演。
- **使用的方法**：利用 hyperspectral lightcurve 的多谱段信息，在已知观测几何下建立姿态与光谱反射关系。
- **主要结果/结论**：多谱段光度提供比单通道光变更丰富的材料/姿态信息，有助于反演。
- **对本项目的借鉴**：v0.4 目前是总光度 OCS；该文说明“增加观测通道”是提升可观测性的自然方向。可在 Future Work 中提到 hyperspectral OCS/光变。
- **可对比点**：高光谱是谱维增强；v0.4 的 L1-G1/G3/G5 是几何维增强。

### 3.21 `Fusion_2014_Linares_space_object_classification_characterization_MMAE.pdf`

文章：Space object classification and characterization using Multiple Model Adaptive Estimation

- **针对的问题**：空间目标类别、形状和状态不确定时，如何从观测中分类和表征。
- **使用的方法**：Multiple Model Adaptive Estimation，维护多个候选模型并根据观测更新模型概率。
- **主要结果/结论**：模型库/候选模型方法适合处理空间目标特征不确定和多假设问题。
- **对本项目的借鉴**：可类比 P-DB/retrieval：不是只输出一个神经网络姿态，而是比较候选物理模型或候选姿态。
- **可对比点**：MMAE 是多模型估计；v0.4 的 P-DB 是多姿态/多几何数据库检索。

### 3.22 `groves2025_selfsupervised_ssa.pdf`

文章：A Self-Supervised Framework for Space Object Behaviour Characterisation

- **针对的问题**：空间目标行为表征缺少大规模标注数据，传统监督学习难以覆盖真实轨道行为。
- **使用的方法**：self-supervised / foundation model 思路，先用未标注数据预训练，再用于空间目标行为分析任务。
- **主要结果/结论**：自监督表征学习可为 SSA 行为理解提供可扩展方向。
- **对本项目的借鉴**：更适合路线四未来动态光变/姿态运动研究，不适合作为当前路线一 C 主干证据。
- **可对比点**：v0.4 当前是物理仿真 benchmark；未来真实光变时序可考虑自监督表征。

## 4. 物理前向、BRDF、光谱和真实观测

### 4.1 `aerospace-09-00403-v2.pdf`

文章：Spectral Light Curve Simulation for Parameter Estimation from Space Debris

- **针对的问题**：空间碎片参数估计严重欠定，单波段光变信息有限，多光谱/光谱 light curve 可能提高可观测性。
- **使用的方法**：扩展 DLR Raxus Prime 仿真环境，用 Mitsuba2 光谱渲染、libRadTran 大气衰减和材料反射模型生成 spectral light curves，并与实测多光谱观测验证。
- **主要结果/结论**：仿真与实测数据达到较好一致性，说明物理前向模型可以作为 light curve inversion 算法开发和测试平台。
- **对本项目的借鉴**：这是 BlenderOCS 最重要的前向模型类参考之一。v0.4 应强调图像和 OCS 共享前向模型，并对材料、几何、传感器、噪声给出清楚说明。
- **可对比点**：该文验证 spectral light curves；v0.4 当前验证的是宽带/积分 OCS 光度向量的姿态信息。

### 4.2 `1-s2.0-S0094576522006464-main.pdf`

文章：Intelligent characterisation of space objects with hyperspectral imaging

- **针对的问题**：如何利用 hyperspectral imaging 和机器学习表征空间目标材料组成和姿态运动。
- **使用的方法**：结合 hyperspectral/multispectral 光谱观测、机器学习、材料识别和姿态运动重建。
- **主要结果/结论**：光谱维度可帮助识别空间目标表面材料，并为姿态运动重建提供额外信息。
- **对本项目的借鉴**：三轴最亮构型中的“材料/表面响应”可以借鉴该文的光谱材料思路，但 v0.4 目前没有高光谱数据，不应过度类比。
- **可对比点**：该文多谱段观测；v0.4 多几何总光度。

### 4.3 `Fankhauser_2023_Satellite_Optical_Brightness_arXiv2305.11123.pdf`

文章：Satellite Optical Brightness

- **针对的问题**：如何根据卫星位置、太阳照明、地球反照和部件 BRDF 估计卫星视亮度。
- **使用的方法**：建立包含太阳直接照明和 Earthshine 的卫星光学亮度模型，使用 BRDF 描述卫星组件和地球反射特性。
- **主要结果/结论**：卫星亮度强烈依赖几何、BRDF、地照和部件朝向。
- **对本项目的借鉴**：支持三轴小项目的光路解释：最亮构型不能只报数值，应解释太阳入射、表面/材料、探测器方向和可能的地照/环境光影响。
- **可对比点**：该文偏宏观亮度模型；v0.4 是 Blender-derived OCS 和图像同源仿真。

### 4.4 `lu2024_brdf_starlink.pdf`

文章：BRDF-Based Photometric Modeling of LEO Constellation Satellite from Massive Observations

- **针对的问题**：如何基于大量观测建立 LEO 星座卫星的亮度模型，评估其对天文观测的影响。
- **使用的方法**：利用 massive observations 拟合/验证 Starlink 等 LEO 卫星的 BRDF-based photometric model。
- **主要结果/结论**：卫星亮度可通过 BRDF 和几何参数建模，但真实观测存在复杂变化。
- **对本项目的借鉴**：可作为 BRDF/真实光度锚点背景，支持路线二真实光度只做趋势和分布锚点。
- **可对比点**：该文真实观测规模大但无三轴姿态真值；v0.4 必须保持这一边界。

### 4.5 `s40295-025-00502-w.pdf`

文章：Daytime Photometry of Starlink Satellites with the Huntsman Telescope Pathfinder

- **针对的问题**：传统光学 SSA 受限于晨昏观测窗口，白天是否能进行卫星光度观测。
- **使用的方法**：用 Huntsman Telescope Pathfinder 白天观测 Starlink 卫星，提取光变曲线，并分析 Earthshine 对亮度的贡献。
- **主要结果/结论**：白天可探测到大量 Starlink，且 Earthshine 对亮度模型至关重要。
- **对本项目的借鉴**：提示真实光度不仅受太阳-目标-观测器几何影响，还可能受地照、天气、背景和观测时段影响。
- **可对比点**：当前 v0.4 仿真若未纳入 Earthshine，应在边界或 Future Work 说明。

### 4.6 `SDC9-paper344.pdf`

文章：Atmospheric Scintillation in Resident Space Object Photometry

- **针对的问题**：大气闪烁对 RSO photometry 和 light curves 的噪声贡献常被低估。
- **使用的方法**：分析 atmospheric turbulence/scintillation 对光度测量的影响，并评估其在 RSO 光度中的重要性。
- **主要结果/结论**：闪烁噪声会影响高精度光度和 light curve 解释，是真实观测中必须考虑的误差源。
- **对本项目的借鉴**：支持 degraded/noise protocol 和真实数据边界。v0.4 不能把仿真 clean 结果直接外推到真实望远镜。
- **可对比点**：真实 photometry noise 可作为路线二/Discussion 的限制项。

### 4.7 `remotesensing-15-04718-v2.pdf`

文章：On-Earth Observation of Low Earth Orbit Targets through Phase Disturbances by Atmospheric Turbulence

- **针对的问题**：地基望远镜观测 LEO 目标时，大气湍流、平台振动和目标快速运动会降低图像质量。
- **使用的方法**：建立 LEO 目标地基观测场景，分析湍流相位扰动、模糊、跟踪和成像质量问题。
- **主要结果/结论**：真实 LEO 成像需要处理湍流、运动和平台误差，直接得到高质量图像并不容易。
- **对本项目的借鉴**：可作为 image degraded / real observation boundary 的背景。
- **可对比点**：v0.4 的 image 通道是仿真图像，不应写成真实地基成像验证。

### 4.8 `Wang 2024.pdf`

文章：Attitude inversion of space debris based on the laboratory-tested photometry dataset

- **针对的问题**：如何用实验室测试光度数据支持空间碎片姿态反演。
- **使用的方法**：构建 CZ-4C 目标实验室 photometry dataset，加入噪声和平移模拟望远镜观测，用遗传算法搜索姿态参数。
- **主要结果/结论**：实验室光度数据可用于姿态反演验证，但实验设置、材料、几何和噪声建模很关键。
- **对本项目的借鉴**：路线三暗室缩比验证可参考该文：实验室真值闭环可作为增强层，但不能外推为 GEO 在轨验证。
- **可对比点**：该文 lab photometry + GA；v0.4 当前是仿真 OCS + neural/retrieval。

## 5. 置信、不确定性、评价和理论基础

### 5.1 `1-s2.0-S1270963825001269-main.pdf`

文章：Predicting uncertainty in vision-based satellite pose estimation using deep evidential regression

- **针对的问题**：视觉卫星姿态估计不仅要输出姿态，还要知道预测什么时候不可靠。
- **使用的方法**：使用 deep evidential regression 进行姿态估计不确定性量化，使网络同时输出预测和证据/不确定性。
- **主要结果/结论**：不确定性预测可帮助识别高误差样本和困难条件，是视觉姿态估计安全部署的重要组成。
- **对本项目的借鉴**：直接支持 v0.4 的 confidence/conformal 方向。后续写作可强调“置信一致性”是研究贡献之一，而不是附属指标。
- **可对比点**：该文是 evidential uncertainty；v0.4 已有 conformal set size、coverage、margin 等，可作为不同 UQ 思路对照。

### 5.2 `ICML_2017_Guo_calibration_modern_neural_networks.pdf`

文章：On Calibration of Modern Neural Networks

- **针对的问题**：现代神经网络的置信度往往不能代表真实正确概率，出现过度自信。
- **使用的方法**：系统评估 depth、width、weight decay、BatchNorm 等因素对 calibration 的影响，并提出 temperature scaling 等校准方法。
- **主要结果/结论**：高准确率不等于置信度可靠；现代深网通常需要额外校准。
- **对本项目的借鉴**：支撑“不能只看 neural margin 或 softmax confidence”的论证。v0.4 的 confidence consistency 和 conformal 分析是必要的。
- **可对比点**：这不是航天领域文献，但可作为置信校准基础引用。

### 5.3 `FnTML_2023_Angelopoulos_Bates_conformal_prediction_intro.pdf`

文章：A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification

- **针对的问题**：黑箱模型在高风险场景下需要可靠 uncertainty set，而不只是一点预测。
- **使用的方法**：介绍 conformal prediction，通过校准集构造满足分布无关覆盖率的预测集合/区间。
- **主要结果/结论**：conformal prediction 能提供显式 coverage guarantee，但 set size 和适用条件需要谨慎解释。
- **对本项目的借鉴**：可直接支撑 v0.4 的 conformal set_size/coverage 写法。
- **可对比点**：不要把 conformal 写成最终概率校准；应写成 protocol 内的分布无关候选集覆盖分析。

### 5.4 `JOSAA_2003_Gerwe_Idell_orientation_Cramer_Rao.pdf`

文章：Cramer-Rao analysis of orientation estimation: viewing geometry influences on the information conveyed by target features

- **针对的问题**：目标姿态估计的信息量如何受观测几何影响。
- **使用的方法**：用 Cramer-Rao bound / Fisher information 分析 viewing geometry 对 orientation estimation 的影响。
- **主要结果/结论**：观测几何会显著改变目标特征对姿态的约束能力。
- **对本项目的借鉴**：这是 v0.4 “多几何 OCS 可观测性”和“三轴最亮构型/高信息区域”的理论背景。几何不是实验细节，而是信息来源。
- **可对比点**：该文是理论信息分析；v0.4 可通过 L1-G1/G3/G5 和三轴 top-1/局部加密做实验对应。

## 6. 经典光变反演和小天体基础文献

### 6.1 `Icarus_2001_Kaasalainen_lightcurve_inversion_I_shape.pdf`

文章：Optimization Methods for Asteroid Lightcurve Inversion I. Shape Determination

- **针对的问题**：如何从小行星光变曲线反演三维形状。
- **使用的方法**：以优化方法求解小行星 lightcurve inversion，通常依赖凸形状、旋转和多几何观测。
- **主要结果/结论**：建立了经典 asteroid lightcurve shape inversion 的优化框架。
- **对本项目的借鉴**：提供光变反演的数学根基：多几何光度确实可以约束形状/姿态相关参数。
- **可对比点**：小行星通常近似凸体和稳定旋转；人工航天器有非凸结构、材料不均匀和姿态/材料耦合，不能直接套用。

### 6.2 `Icarus_2001_Kaasalainen_lightcurve_inversion_II_complete_inverse_problem.pdf`

文章：Optimization Methods for Asteroid Lightcurve Inversion II. The Complete Inverse Problem

- **针对的问题**：小行星 lightcurve inversion 的完整问题，包括形状、旋转状态和散射参数。
- **使用的方法**：扩展优化框架，处理 complete inverse problem。
- **主要结果/结论**：多几何光变可以联合约束形状和旋转，但仍依赖模型假设和观测覆盖。
- **对本项目的借鉴**：可作为“光度反演需要多几何覆盖”的经典依据。
- **可对比点**：v0.4 的 L1-G1/G3/G5 与 asteroid 多观测思想一致，但目标类型和光学复杂度不同。

### 6.3 `AandA_2025_Tang_asteroid_shape_inversion_deep_learning.pdf`

文章：Asteroid shape inversion with light curves using deep learning

- **针对的问题**：传统小行星光变形状反演计算复杂，能否用深度学习提升反演效率。
- **使用的方法**：用深度学习从 photometric light curves 重建 asteroid shape。
- **主要结果/结论**：深度学习可加速或增强 asteroid shape inversion，但仍以小天体光变假设为基础。
- **对本项目的借鉴**：说明低维光度序列可以训练神经模型提取形状/姿态信息，但人工空间目标需要额外处理材料、非凸和几何耦合。
- **可对比点**：可作为 OCS-only neural regression 的远亲背景，但不应作为 RSO 直接证据。

## 7. 真实光度巡天、观测策略和行为理解

### 7.1 `1-s2.0-S0094576526000391-main.pdf`

文章：APSIS: Automated Photometric Survey of Inactive Satellites for rotational dynamics and lightcurve characterization

- **针对的问题**：如何自动化、高频率地监测 inactive GEO/MEO 卫星光变，以表征旋转动力学和长期行为。
- **使用的方法**：构建自动化地基光学系统，包含图像采集、校准、测光、lightcurve modeling、survey 和 targeted follow-up。
- **主要结果/结论**：自动光度巡天能生成高质量光变数据，支持周期、旋转状态和长期变化分析。
- **对本项目的借鉴**：路线二真实 GEO 光度锚点可借鉴其数据处理流程和谨慎表述：真实光度用于趋势、分布、周期和行为，不等同于三轴姿态真值。
- **可对比点**：APSIS 是真实数据系统；v0.4 当前是仿真主干和三轴最亮构型。

### 7.2 `s40295-025-00502-w.pdf`

文章：Daytime Photometry of Starlink Satellites with the Huntsman Telescope Pathfinder

- **针对的问题**：是否能把空间域感知光度观测从晨昏扩展到白天。
- **使用的方法**：使用 Huntsman Telescope Pathfinder 对 Starlink 做白天光度观测，分析亮度分布和 light curves。
- **主要结果/结论**：白天观测可行，但 Earthshine 和背景条件对亮度建模影响显著。
- **对本项目的借鉴**：真实光度模型要考虑观测条件，不应只依赖理想太阳直接照明。
- **可对比点**：可作为真实观测限制和未来路线二背景。

### 7.3 `Kumar_2025_Light_curves_sequential_comparison_ActaAstronautica_10.1016-j.actaastro.2025.04.018.pdf`

文章：Light curves sequential comparison strategy for improved understanding of LEO uncontrolled objects

- **针对的问题**：对无几何真值或形状先验不足的 LEO 目标，如何通过连续光变比较理解旋转状态。
- **使用的方法**：顺序比较多次 light curves，结合频谱/周期分析，跟踪 tumbling 变化。
- **主要结果/结论**：多次观测比单次观测更能揭示 uncontrolled object 的旋转行为。
- **对本项目的借鉴**：支持“多观测”路线；路线二真实光度可借鉴 sequential analysis，而不是强行姿态监督。
- **可对比点**：该文处理真实 LEO 光变；v0.4 处理仿真 OCS 多几何向量。

### 7.4 `SDC9-paper344.pdf`

文章：Atmospheric Scintillation in Resident Space Object Photometry

- **针对的问题**：大气闪烁是否会成为 RSO photometry 的重要噪声源。
- **使用的方法**：分析 scintillation 对测光误差和 light curve 的影响。
- **主要结果/结论**：闪烁需要纳入高精度光度误差预算。
- **对本项目的借鉴**：为 degraded/real-noise 边界提供依据。
- **可对比点**：真实光度与仿真 clean OCS 的差异应在 Discussion 中明确。

## 8. 图像-光度联合、跨模态和成像退化

### 8.1 `kobayashi-frueh-2024-image-recovery-for-low-earth-orbit-by-leveraging-turbulence-and-light-curves.pdf`

文章：Image Recovery for Low Earth Orbit by Leveraging Turbulence and Light Curves

- **针对的问题**：在大气湍流下，是否能用 unresolved light curve 和 PSF/turbulence 信息恢复 LEO 目标图像。
- **使用的方法**：将 light curve model 转换为线性测量模型，用 compressed sensing 和 total variation 进行图像恢复，并考虑 PSF map 误差和 Poisson noise。
- **主要结果/结论**：light curve 与成像退化模型结合后，可以为低分辨/受湍流影响的图像恢复提供信息。
- **对本项目的借鉴**：这是图像和光度建立数学联系的强参考。v0.4 可借鉴其“光度不是图像替代品，而是另一个积分观测约束”的表达。
- **可对比点**：该文目标是图像恢复；v0.4 目标是姿态信息可观测性、互补性和置信一致性。

### 8.2 `TAES_2022_Rondao_ChiNet_multimodal_spacecraft_pose.pdf`

文章：ChiNet: Deep Recurrent Convolutional Learning for Multimodal Spacecraft Pose Estimation

- **针对的问题**：图像姿态估计能否通过 temporal sequence 和 RGB/LWIR 多模态融合提升鲁棒性。
- **使用的方法**：CNN 提取图像特征，LSTM 建模序列，融合 RGB 与热红外输入，并采用 coarse-to-fine 训练策略。
- **主要结果/结论**：多模态和时序信息有助于平滑和改进姿态估计。
- **对本项目的借鉴**：为 v0.4 的 joint 叙事提供类比：融合必须说明每个通道增加了什么信息。
- **可对比点**：ChiNet 是 RGB/LWIR/time；v0.4 是 image/OCS geometry。

### 8.3 `liu2024_visual_inertial_fusion.pdf`

文章：Tightly Coupled Visual-Inertial Fusion for Attitude Estimation of Spacecraft

- **针对的问题**：星敏感器在高动态、杂散光和在轨扰动下可能输出异常，需要与陀螺融合提升航天器自身姿态估计。
- **使用的方法**：紧耦合视觉-惯性融合，将星敏感器和陀螺数据结合。
- **主要结果/结论**：融合能提升 spacecraft own attitude estimation 的鲁棒性。
- **对本项目的借鉴**：该文是“航天器自身姿态确定”而非“外部目标姿态反演”，只适合作为多传感器融合思想参考。
- **可对比点**：不要将其误引用为 RSO 光度/图像姿态反演文献。

## 9. 综述和前沿路线图

### 9.1 `aerospace-13-00418-v2.pdf`

文章：Photometric Characterization of Space Objects: From Classical BRDF Models to Data-Driven Prediction

- **针对的问题**：空间目标 photometric characterization 如何从经典 BRDF 模型发展到数据驱动预测。
- **使用的方法**：综述光学散射、BRDF、shape/attitude inversion、machine learning 和 photometric prediction。
- **主要结果/结论**：领域趋势是物理模型与数据驱动结合，但真实观测的姿态/材料/形状耦合仍是核心挑战。
- **对本项目的借鉴**：适合作为 v0.4 Introduction 和 Related Work 的高层综述。
- **可对比点**：可帮助定位本项目：不是真实未知目标反演，而是 model-known 仿真条件下系统评估 OCS 光度信息。

### 9.2 `Fankhauser_2023_Satellite_Optical_Brightness_arXiv2305.11123.pdf`

文章：Satellite Optical Brightness

- **针对的问题**：卫星亮度如何随太阳、地球、观测者和卫星部件反射变化。
- **使用的方法**：物理亮度模型，包含 direct Sun illumination 和 Earthshine，使用 BRDF 估计反射。
- **主要结果/结论**：卫星亮度不是单一姿态函数，而是几何、材料和环境共同作用。
- **对本项目的借鉴**：支持 OCS 和三轴最亮构型的物理前向叙事。
- **可对比点**：如果 v0.4 不含 Earthshine，应明确为模型边界。

## 10. 其他相关但不宜作为主线核心的条目

### 10.1 `remotesensing-15-04718-v2.pdf`

文章：On-Earth Observation of Low Earth Orbit Targets through Phase Disturbances by Atmospheric Turbulence

- **针对的问题**：地基观测 LEO 目标时，大气湍流和平台误差导致图像退化。
- **方法/结果**：分析湍流、模糊、目标运动和跟踪问题，提出观测/成像质量改善思路。
- **对本项目的借鉴**：可作为真实图像退化和 domain gap 的背景。
- **注意**：不是 OCS 或 light curve 主文献。

### 10.2 `yang2024_goniopolarimetric.pdf`

文章内容：A Miniaturized Electrothermal-MEMS-Based Optical Coherence Tomography (OCT) Handheld Microscope

- **核查结论**：文件名像 goniopolarimetric 相关，但 PDF 内容实际是 OCT 手持显微镜，与空间目标光度/姿态反演主题不匹配。
- **建议**：从本项目核心阅读清单移出或重新核对是否下载错文件。

### 10.3 `xiong2025_sfda_mef.pdf`

文章内容：General Table Question Answering via Answer-Formula Joint Generation

- **核查结论**：这是表格问答/大模型相关论文，与空间目标光度、图像姿态估计、OCS 或 SSA 无直接关系。
- **建议**：从当前 papers 核心文献中移出或核对下载来源。

### 10.4 `dickinson2025_sim2real_6dof.pdf`

文章内容：Advancements in Scanning Electron Microscopy

- **核查结论**：文件名像 sim2real 6DoF，但 PDF 首页显示为扫描电子显微镜相关学位论文，与当前主题不匹配。
- **建议**：核查是否下载错文件；若目标是 sim-to-real 6DoF spacecraft pose 文献，需要重新下载正确 PDF。

## 11. 面向 v0.4 的方法总结表

| 可借鉴方向 | 对应文献 | 可用于 v0.4 的位置 |
|---|---|---|
| 图像姿态估计领域背景 | `2305.07348v3.pdf` | Introduction / Related Work |
| 合成图像数据集生成与验证 | `Acta_2023_Bechini_dataset_generation_validation_spacecraft_pose.pdf` | Methods: dataset and rendering |
| domain gap 与多任务图像姿态 | `ASR_2024_Park_DAmico_SPNv2_domain_gap_pose_estimation.pdf`, `2212.12103v1.pdf` | Image baseline / Discussion |
| 图像混合几何方法 | `1-s2.0-S0094576523006185-main.pdf`, `1-s2.0-S0094576525006836-main.pdf` | Image channel interpretation |
| 多几何/多观测思想 | `TAES_2022_Rondao_ChiNet_multimodal_spacecraft_pose.pdf`, `Kumar_2025...pdf` | L1-G1/G3/G5 多几何 OCS |
| 光变姿态反演多解性 | `s40295-025-00557-9.pdf`, `1-s2.0-S0273117722010493-main.pdf` | P-DB / conformal / low-information |
| 全局优化/搜索 baseline | `Burton 2024.pdf`, `s40295-025-00486-7.pdf`, `1-s2.0-S0273117725013961-main.pdf` | OCS-only retrieval / non-neural baseline |
| 物理前向和光谱仿真 | `aerospace-09-00403-v2.pdf`, `1-s2.0-S0094576522006464-main.pdf` | Shared forward model / 三轴光路解释 |
| 真实光度观测限制 | `1-s2.0-S0094576526000391-main.pdf`, `SDC9-paper344.pdf`, `s40295-025-00502-w.pdf` | Route 2 / Discussion |
| 置信和不确定性 | `1-s2.0-S1270963825001269-main.pdf`, `FnTML_2023...pdf`, `ICML_2017...pdf` | Confidence consistency / conformal |

## 12. 建议阅读优先级

### 第一优先级：直接支撑 v0.4 主论文

1. `2305.07348v3.pdf`
2. `Acta_2023_Bechini_dataset_generation_validation_spacecraft_pose.pdf`
3. `ASR_2024_Park_DAmico_SPNv2_domain_gap_pose_estimation.pdf`
4. `ASR_2022_Clark_RSO_attitude_optical_property_light_curves.pdf`
5. `1-s2.0-S0273117725013961-main.pdf`
6. `s40295-025-00557-9.pdf`
7. `aerospace-09-00403-v2.pdf`
8. `1-s2.0-S1270963825001269-main.pdf`

### 第二优先级：支撑实验和 Discussion

1. `1-s2.0-S0094576525002176-main.pdf`
2. `2212.12103v1.pdf`
3. `1-s2.0-S0273117722010493-main.pdf`
4. `s40295-025-00486-7.pdf`
5. `Kumar_2025_Light_curves_sequential_comparison_ActaAstronautica_10.1016-j.actaastro.2025.04.018.pdf`
6. `1-s2.0-S0094576526000391-main.pdf`
7. `kobayashi-frueh-2024-image-recovery-for-low-earth-orbit-by-leveraging-turbulence-and-light-curves.pdf`

### 第三优先级：背景、历史或未来方向

1. `Icarus_2001_Kaasalainen_lightcurve_inversion_I_shape.pdf`
2. `Icarus_2001_Kaasalainen_lightcurve_inversion_II_complete_inverse_problem.pdf`
3. `JGCD_2009_Wetterer_Jah_attitude_determination_light_curves.pdf`
4. `JGCD_2014_Linares_shape_tracking_lightcurve_angles.pdf`
5. `JGCD_2018_Coder_active_control_mode_lightcurve_inversion.pdf`
6. `JGCD_2023_Dianetti_Crassidis_polarized_light_curves.pdf`
7. `groves2025_selfsupervised_ssa.pdf`

## 13. 对当前项目最关键的前沿背景判断

当前前沿并不是简单走向“光度直接精确定姿”，而是走向几条更谨慎、更可发表的路线：

```text
1. 图像姿态估计：深度学习 + 几何约束 + domain gap 处理。
2. 光变姿态反演：物理前向模型 + 多观测 + 候选集/多解处理。
3. 物理仿真：材料/BRDF/几何/传感器/大气逐项建模和验证。
4. 置信不确定性：从单点精度转向 coverage、set size、uncertainty-error relation。
5. 真实数据：更多用于光度趋势、行为、周期、材料/亮度模型锚点，而不是直接提供三轴姿态监督标签。
```

这与 v0.4 当前定位是匹配的。最稳的论文叙事不是“OCS 光度能完成真实未知目标姿态反演”，而是：

```text
在已知目标模型和共享物理前向模型条件下，
系统研究跨几何 OCS 光度向量与图像通道对姿态信息的可观测性、互补性和置信一致性，
并进一步通过三轴最亮构型解释光路和材料/表面响应机制。
```

