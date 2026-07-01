# R94 Codex PDF 补读筛选：1C-B2 阶段门边界确认

最后更新：2026-06-29  
执行端：Codex  
性质：对 R92/R93 之后“其他 PDF 是否还要读”的补充筛选。本文只做文献方法确认与阶段门建议，不修改代码、数据、split、模型、超参、seed、实验结果或 CLAUDE.md。

## 0. 总结论

```text
其他 PDF 值得补读，但它们不会推翻 R92/R93。

核心证据仍然是：
Wetterer & Jah 2009 + Gerwe & Idell 2003 + Kaasalainen I/II

补读文献的主要作用是：
1. 强化“先 P0 只读诊断，再 P1 方法改造，再 P2 光变序列”的阶段门；
2. 限制论文表述边界，尤其是 sim-to-real、BRDF/材料、观测噪声、模型复杂度；
3. 提醒后续 fusion 不能只做 naive early concat，应转向 decision-level/model-bank/uncertainty-aware 设计。
```

因此，当前建议不变：

```text
立即做：P0 只读诊断包
谨慎放行：P1-A 连续/圆周角度判据，P1-B 非朴素 fusion
暂不放行：正式 light-curve sequence 新数据线、完整 CRLB、复杂 BRDF/光学参数反演
```

## 1. 光变定姿与联合估计补读

### 1.1 Piergentili 2017

文献要点：以虚拟三维航天器模型、刚体姿态传播、多目标遗传算法重建光变曲线；目标是匹配峰谷结构而非逐点精确星等。作者明确强调形状、材料、反射模型不确定性会影响可用性，多站点、多波段观测能改善可观测性；球对称目标会失败，真实观测前应先用含噪仿真评估可行性。

对本项目含义：

```text
支持 P0/P2：光变序列有价值，但必须先确认几何/形状/材料约束是否足够。
不支持现在直接开 P2：因为当前单帧 OCS 的 yaw 外推问题还没有被诊断清楚。
论文可写：后续光变线应以“峰谷/签名可分性”为早期诊断，不宜一开始承诺精确逐点反演。
```

### 1.2 Linares JGCD 2014 与 Fusion 2014

文献要点：使用 light curve + angles 的 Multiple Model Adaptive Estimation（MMAE），并行 UKF 模型库对应不同形状/类别假设，输出状态估计与模型概率。若真形状在模型库中，正确模型可被选中；若不在模型库中，会选最接近的近似模型。形状不确定会劣化姿态与角速度估计。

对本项目含义：

```text
支持 P1-B：非朴素 fusion 应优先考虑 late fusion、decision-level fusion、model-bank/probabilistic fusion。
支持论文边界：当前 early concat 负结果只否定朴素拼接，不否定 image 与 OCS 的所有互补可能。
提醒：若后续引入形状/材料/BRDF 假设，必须显式记录模型库边界，否则容易把模型假设误写成物理结论。
```

### 1.3 Clark ASR 2022

文献要点：用空间基低分辨率光变估计 RSO 形状、姿态和光学属性；强调单个亮度测量对应许多可能解，必须依赖时间序列。更复杂的 Phong/facet 模型可能带来更多局部最优，不一定更稳；最优算法依赖空间/时间分辨率、场景和模型保真度。

对本项目含义：

```text
强支持“不要先复杂化 BRDF”。
当前最稳路径是先做 signature distance / confusion cluster / pseudo-light-curve probe。
如果 P2 启动，必须写清 inverse-crime 防护、噪声、几何覆盖、预配准和模型保真度。
```

### 1.4 Aerospace 2025 joint estimation

文献要点：从光变同时估计非受控目标的姿态、角速度、漫反射光学参数和大气影响；方法结合 Adaptive Importance Sampling、PSO、聚类和局部最小二乘。文献综述明确指出：光变测量模型高度非线性，状态分布可非高斯、多峰；不同几何、光学、姿态参数组合可能产生等价光变曲线。该文还把 Wetterer & Jah 的初始化敏感和 measurement ambiguity 放进同一条证据链。

对本项目含义：

```text
进一步确认 R93：yaw 失败应写作可观测性/测量歧义相关的外推鸿沟，而不是“模型偶然失败”。
支持未来 P2：粒子/混合/聚类类方法比单一 UKF 更适合多峰后验。
不建议现在采用：该路线参数多、工程重，且依赖严格前向模型与观测噪声定义。
```

## 2. Sim-to-real 与合成数据验证补读

### 2.1 SPEED+ 2022

文献要点：SPEED+ 明确以 synthetic-to-HIL domain gap 为核心问题，提供大规模合成训练图像与 lightbox/sunlamp 两类 HIL 测试图像；强调纯合成训练在真实或 HIL 域上会性能下降，HIL 是空间真实图像的弱替代验证。

对本项目含义：

```text
论文不能把 Blender 纯仿真结果写成真实空间泛化结论。
当前路线一结果应表述为 protocol-defined simulation evidence。
若后续要走真实适用性，至少需要 domain randomization / HIL-like validation / realistic illumination-noise stress test 之一。
```

### 2.2 SPNv2 / Park & D'Amico 2024

文献要点：SPNv2 用多任务 CNN、强数据增强和 Online Domain Refinement 缓解 domain gap；即使在 SPEED+ HIL 上有效，作者仍说明 HIL 到真正 spaceborne 图像之间仍存在差距。ODR 平均改善性能，但部分样本会变差，未来还需评估不确定性并接入滤波器。

对本项目含义：

```text
支持 P1-B 的 uncertainty-aware / calibration / agreement 设计。
不支持把一次模型提升写成普适鲁棒性。
若使用在线/自监督适配，必须报告样本级退化风险，而不只报告平均值。
```

### 2.3 Bechini 2023

文献要点：提出基于物理光线追踪的合成图像生成与验证流程，强调合成图像需做定性与定量验证；同时指出 domain gap 会危及图像处理管线。其数据集是 noiseless，噪声可后处理添加；真实镜头内反射、耀斑、杂散光等仍需额外模型。

对本项目含义：

```text
直接约束 BlenderOCS 论文措辞：合成数据有效，但应声明无噪/受控渲染边界。
支持 P0 协议对齐：先确认 V0.3/V0.4、random split/yaw-block、exact-bin/near-hit 口径是否一致。
若后续扩展数据，应先定义噪声、曝光、阴影、材质扰动，而不是只扩大样本量。
```

## 3. 真实光度与 BRDF 补读

### 3.1 Fankhauser 2023

文献要点：用 BRDF 和地球反照光预测卫星亮度，可用实验室 BRDF 或多角度观测拟合；Starlink 验证中，BRDF 模型优于校准漫反射球模型。但作者也指出小型镜面部件、glint、未知姿态、地球反照光和小部件几何会造成难建模误差。

对本项目含义：

```text
支持“材料/BRDF/地球反照光是不确定源”，但不支持当前立即做完整 BRDF 反演。
可作为论文讨论：单帧或少量观测下，亮度/OCS 签名可能由姿态、材料和照明共同决定。
如果后续引入真实光度，应优先做简单、可控、可验证的 BRDF，而非一开始追求复杂模型。
```

### 3.2 Lu 2024 Starlink BRDF

文献要点：用百万级观测拟合 Starlink BRDF 光度模型，考虑遮挡、地球反照光、姿态假设和太阳帆角度假设；结论显示 BRDF 模型可用于 SSA 和星迹预测，但模型残差仍受未知部件反射、姿态不确定、观测数据不确定和多参数耦合影响。作者明确认为实验室真实形状/材料 BRDF 需要厂商支持，而观测拟合仍不可或缺。

对本项目含义：

```text
进一步支持“复杂 BRDF 会带来参数耦合”，不是当前 P0/P1 的优先方向。
若后续写真实应用，应把 BRDF/材料作为 nuisance factors 或不确定性来源。
可借鉴其做法：用观测几何分箱、残差图和模型组件消融来检查物理假设。
```

## 4. 对下一步方法的最终阶段门

### P0：现在放行

```text
P0-1 协议对齐
核查 V0.3/V0.4、random split/yaw-block、exact-bin/near-hit、fold/bin 定义是否完全一致。

P0-2 signature distance
计算 OCS-only、image embedding、joint embedding 的 yaw-yaw 距离矩阵。

P0-3 confusion cluster
按真 yaw、预测 yaw、pitch、fold 聚类，寻找近似等价解簇。

P0-4 pseudo-light-curve probe
在固定 pitch/几何条件下串联现有 yaw-ordered 样本，只做描述性可分性分析。
```

验收口径：

```text
P0 只回答“信息在哪里不足、歧义是否成簇、是否值得做序列”，不训练、不改 split、不生成新数据。
```

### P1：P0 后逐项放行

```text
P1-A continuous/circular angle criteria
目标：剥离 exact-bin 对 yaw 评价的放大效应。
候选：sin-cos regression、circular distance、von-Mises/NLL、near-hit/top-k angular band。

P1-B non-naive fusion
目标：重新检验 image 与 OCS 是否互补。
候选：late fusion、decision-level fusion、model-bank fusion、gated/mid-balanced fusion。
必要消融：image-only / OCS-only / early concat / late-or-decision fusion。
```

### P2：暂缓，满足条件后再开

```text
P2 formal light-curve sequence
启动条件：
1. P0 证明单帧签名存在 yaw 等价簇或低距离混淆；
2. P1-A 后 yaw-block 仍存在显著外推鸿沟；
3. 新数据协议写清多时刻/多几何采样、噪声、BRDF、遮挡、预配准；
4. 明确 inverse-crime 防护；
5. 明确 single-frame OCS 是 lower information layer，sequence 是 higher information layer。
```

## 5. 可写进论文的方法叙事

推荐中文表述：

```text
当前结果揭示的是单帧 OCS/图像输入在 yaw-block 协议下的外推鸿沟，而不是 yaw 姿态的物理不可观测。光变定姿、CRLB 和小行星光变反演文献共同表明，姿态信息的可辨识性强依赖观测几何、时间序列、反射模型和目标对称性。因而，本文将单帧 OCS 视为受控仿真条件下的信息下界，并将后续工作设计为阶段式路径：首先进行只读可观测性诊断，其次评估连续角度判据和非朴素多模态融合，最后在证据充分时扩展到光变序列建模。
```

推荐英文表述：

```text
The current results indicate a protocol-defined yaw extrapolation gap under single-frame OCS/image inputs, rather than a physical unobservability of yaw itself. Prior work on photometric attitude estimation, CRLB-based orientation analysis, and light-curve inversion shows that attitude identifiability depends strongly on viewing geometry, temporal coverage, reflectance modeling, and target symmetry. We therefore treat single-frame OCS as a controlled lower-information setting and propose a staged path: read-only observability diagnostics, continuous angular criteria and non-naive multimodal fusion, followed by light-curve sequence modeling only when the diagnostic evidence justifies the added complexity.
```

## 6. 本轮补读 PDF

```text
TAES_2017_Piergentili_attitude_lightcurve_measurements.pdf
JGCD_2014_Linares_shape_tracking_lightcurve_angles.pdf
Fusion_2014_Linares_space_object_classification_characterization_MMAE.pdf
ASR_2022_Clark_RSO_attitude_optical_property_light_curves.pdf
aerospace2025_joint_estimation.pdf
IEEEAero_2022_Park_SPEEDplus_spacecraft_pose_domain_gap.pdf
ASR_2024_Park_DAmico_SPNv2_domain_gap_pose_estimation.pdf
Acta_2023_Bechini_dataset_generation_validation_spacecraft_pose.pdf
Fankhauser_2023_Satellite_Optical_Brightness_arXiv2305.11123.pdf
lu2024_brdf_starlink.pdf
```

## 7. 最终建议

```text
接受 R92/R93，并以 R94 作为“其他 PDF 补读后不改变主阶段门”的边界确认。

下一步只放行 P0 只读诊断包：
protocol alignment + signature distance + confusion cluster + pseudo-light-curve probe。

暂缓：
新训练、新渲染、完整 CRLB、正式 light-curve sequence、复杂 BRDF/材料参数反演。
```
