# 87_1C-B2 文献方法总结与后续方法规划

最后更新：2026-06-29
执行端：Claude
性质：头B `B-2` 文献方法总结与后续方法规划。**这是 Claude 的方法判断与候选规划，不是审阅、不是放行、不是裁决。**
读者：Codex / 作者。
输入：R91（B-1 六方向文献约束）、85 号（文献补课材料）、84 号（暂停点复盘与代码事实）、R90（头A桥接稳定）、R05（两头并行结构）、05 号（PDF 入库状态）。

> 本文件不启动训练、不生成数据、不改 split/模型/超参/seed、不改代码、不改论文正文、不改成果区、不改 CLAUDE.md。
> 所有“建议采用 / 优先级 / B-3 / B-4”均为候选，必须由 Codex / 作者按阶段门另行放行。
> 本文件严格区分两层：**【Claude 方法判断】**（我的技术意见）与 **【放行状态】**（项目是否已正式放行）。除非显式标注“已放行”，一律视为未放行候选。

---

## 0. 执行摘要

- **单帧多维 OCS 在文献谱系中处于边缘/非标准位置。** 真实工程与天文界主流信息形态是 light-curve 序列（多时刻/多几何亮度演化），单帧多视角标量分解几乎不是真实采集姿态信息的标准方式。当前 C2/C3 负结果首先是一个“信息形态选择”的结果，其次才可能涉及物理边界。

- **当前负结果是四重口径选择的叠加产物，不是物理不可观测。** 四重来源：(1) 单帧标量而非序列；(2) 分类 + exact-bin 精确命中判据；(3) early-concat + 单线性头的弱融合且图像 256 维淹没 OCS 128 维；(4) 图像零噪声、无增广。每一重都有文献支持的改正方向。

- **后续信息源升级主线应是 light-curve sequence，且与单帧 OCS 是层级关系而非二选一。** 序列是更高信息层级（可打破单帧姿态歧义）；单帧 OCS 仍有价值，作为信息下界、对照基线与“为什么单帧不够、序列才够”的正向可观测性叙事的必要对照。建议骨架：单帧 vs 序列的信息源对比，而不是替换。

- **early fusion negative result 只否定了一种 naive early fusion。** 它否定的是“feature-concat + 单线性头 + 模态维度失衡”下的自动增益；它**没有**否定 mid fusion、late/decision-level fusion、cross-attention、modality-balanced fusion、uncertainty-aware fusion。互补性支柱目前是“虚”的，需要至少一个非朴素融合对照才能真正回答。

- **方法改正建议排序（我的判断，未放行）：P0 判据/损失（分类→circular regression / von-Mises），P1 协议对齐核查 + fusion 结构改正 + 可观测性只读诊断，P2 信息源升级（light curve，需新数据），P3 不确定性/校准/拒识。先改判据是最低风险、最高杠杆，且可能直接改变“是否失败”的判断。**

- **可观测性诊断应从“实验失败”升级为“正式可观测性论证”。** Gerwe & Idell 2003 提供 Cramér-Rao/Fisher 工具，Kaasalainen 提供歧义理论。引入 signature distance / Fisher-CRLB / confusion cluster / geometry coverage，可把 yaw-block extrapolation gap 写成有理论支撑的边界，而非单纯训练失败。

- **所有改正必须保 R04 负结果链可复现。** 改判据、改 fusion、升级信息源全部属 C 类阶段门，必须另建副本/新脚本，不得原地改 R04 代码/数据/成果链。任何单项放行都应记录其边际贡献，使改进过程成为可发表的消融/可观测性分析，而非“调参追结果”。

- **建议下一阶段入口：先做两项零/低风险动作——(a) V0.3↔V0.4 协议对齐只读核查，(b) 伪光变曲线只读探针——再据其结果决定是否进入 P0 判据改正的 C 类阶段门。** 不建议现在直接进入新训练或正文改写；建议本 B-2 与头A（R90）一起进入合并审阅。

---

## 1. 文献方法谱系（按六方向提炼方法模式，不只罗列）

下表先给方向的“方法模式”而非文献清单；文献以 R91/05 已入库的为锚点。

### 1.1 光变曲线 / 光度反演（方法源头）

方法模式：
- **核心信息形态是时间/几何序列亮度演化（light curve），不是单时刻标量。** Kaasalainen 2001 I/II、Wetterer & Jah 2009、Linares 2014、Piergentili 2017、Coder 2018、Burton 2024、Kumar 2025 等，姿态/自旋/形状反演的输入几乎都是多历元光变。
- **歧义与退化是该领域核心结论**：凸体/非凸体歧义、镜像歧义、单历元信息不足；序列与多几何观测正是用来打破歧义的手段。
- Kumar 2025 明确做 light-curve 的序列对比；Tang 2025 用深度学习做光变形状反演；Dianetti & Crassidis 2023 用偏振光变增加可观测维度。

对本项目的方法启示：单帧多维 OCS 在此谱系中是“被简化掉时间维度”的退化输入；负结果首先应被理解为“信息形态不足”，序列化是主流升级路径。

### 1.2 SSA 空间目标光学特征化

方法模式：
- 光度在 SSA 中**主流用途是表征、状态变化与异常监测**（Fankhauser 2023、Lu 2024、Groves 2025、Aerospace 2026 review），与专家“光度多用于异动监测而非精确定姿”的质疑一致。
- 精确定姿通常需要：已知/参数化形状 + BRDF + 姿态动力学 + 多历元约束。无姿态真值的真实数据集普遍只能做弱监督/自监督表征。

对本项目的方法启示：model-known 合成 benchmark 可作为“受控下界”，但不能写成真实 GEO 监督定姿系统；这同时给路线二（真实 GEO 无姿态真值）划了边界。

### 1.3 图像 + 光度 / 多模态融合

方法模式：
- 现代多模态姿态工作（Rondao 2022 ChiNet、Pasqualetto Cassinis 2021、Liu 2024 视觉-惯性紧耦合）几乎都用 **mid/late fusion、cross-attention 或紧/松耦合**，而不是单纯 feature-concat + 单线性头。
- 高维模态淹没低维模态是已知问题；衡量真实互补需要互信息、消融、late-fusion gain 等独立手段，而非只看一次 early concat。

对本项目的方法启示：当前 joint 结论只覆盖“最朴素 early fusion 无自动增益”，互补性问题在文献意义上**尚未被回答**。

### 1.4 sim-to-real 与 synthetic benchmark 可信度

方法模式：
- SPEED+（Park 2022）、Park & D'Amico 2024、Bechini 2023、Dickinson 2025 都显式承认 domain gap，并用域随机化、噪声注入、域适配提升可信度。
- “inverse crime”（同一前向模型既生成数据又反演）是公认陷阱；零噪声理想渲染易让模型学渲染伪影捷径。

对本项目的方法启示：v0.4 可讲 controlled benchmark + inverse-crime 防护，但不能声称迁移真实望远镜/GEO；图像零噪声是当前现实性隐患，噪声/退化/域随机化是低 claim 风险的可信度增强方向。

### 1.5 可观测性 / 可辨识性

方法模式：
- Gerwe & Idell 2003 用 **Cramér-Rao / Fisher information** 分析有限观测几何下朝向估计的理论下界；Kaasalainen 提供歧义/退化的解析结构。
- 这些工具能把“某姿态区不可反演”从实验现象提升为理论可观测性论证。

对本项目的方法启示：yaw-block extrapolation gap 可被组织为 protocol-defined extrapolation gap，并用 signature distance / Fisher-CRLB / 混淆簇进一步支撑；但当前结果**不足以**写成 yaw 物理不可观测。

### 1.6 现代姿态反演 / 序列 / 不确定性架构

方法模式：
- 角度目标：**回归 + circular/von-Mises 损失** 优于硬 bin 分类 + exact-bin（Tang 2025、一般姿态回归实践）。
- backbone：ResNet / ViT / 预训练（Sosa 2025 ViT 6DOF、Dickinson 2025）相对手搓浅 CNN 有实测增益。
- 序列：1D-CNN / LSTM / Transformer 用于光变/时间序列反演。
- 不确定性：Guo 2017（校准/ECE）、Angelopoulos & Bates 2023（conformal prediction / prediction set）提供把“置信”落成可验证机制的工具。

对本项目的方法启示：exact-bin yaw=0% 是 sentinel；真正的“可信/拒识”机制必须另行实现校准、ECE、conformal 或 posterior-like agreement 才能从 sentinel 升级为可写机制。

---

## 2. 当前项目结果在文献谱系中的位置

### 2.1 单帧多维 OCS 的定位

- 在文献谱系中是 **light curve 的退化/降维形态**：保留了多视角空间分解，但抹去了时间/几何演化维。
- 它**不是**真实工程采集姿态信息的标准方式（1.1/1.2），是路线一仿真与真实数据之间的隐性裂缝。
- 正向价值：作为信息**下界**与对照基线，支撑“单帧信息不足以消歧 → 需要序列”的可观测性叙事。它本身不该被丢弃，而应被定位为对比的一极。

### 2.2 图像通道的定位

- 当前是 6 层灰度 CNN、零噪声、无增广（84 号代码事实）。在文献谱系（1.4）中属“理想合成、未做可信度增强”的初级形态。
- pitch 在 fixed-roll + 当前图像模型 + circular yaw-block 协议下稳定高于 chance（R90），说明图像通道确实承载部分姿态信息；但这一结论严格限定于当前协议，不能外推。

### 2.3 early fusion 的定位

- 当前是 image 256 维 + OCS 128 维 → concat 384 维 → 单线性头（84 号代码事实），且数值上图像淹没 OCS。
- 在融合谱系（1.3）中是**最朴素的一种 early fusion**。它的 negative result 只能定位为“该 naive early fusion 在当前协议下无自动增益”。

### 2.4 yaw-block negative result 的定位

- random split 下 yaw 分布内可学（~50–70%，84 号）；circular yaw-block 下 continuous/near-hit 接近或仅弱高于随机（R82/E45B）。
- 正确定位：**protocol-defined extrapolation gap**——当前模型无法可靠外推到未见连续 yaw 弧段。
- exact-bin yaw=0.00% 是 strict classifier + circular yaw-block 外推下的 **diagnostic sentinel**（R90），不是物理不可观测、不是已实现拒识。

### 2.5 “能说明什么 / 不能说明什么”（关键边界）

能说明（fixed-protocol 内成立）：
```text
- 在单帧标量 OCS + 分类 exact-bin + naive early fusion + 零噪声图像 + circular yaw-block 协议下，
  yaw 无法跨未见弧段外推；C2 OCS-only 未检出稳定高于 chance 的可区分信号；
  naive early fusion 无自动互补增益；pitch 高于 chance 但存在 pitch>yaw 各向异性。
```

不能说明（红线，禁止外推）：
```text
- 不能说 yaw 物理不可观测。
- 不能说 OCS 通道本身不携带姿态信息。
- 不能说 image 与 OCS 普遍不互补 / fusion 普遍无效。
- 不能说当前 exact-bin 0% 是真实拒识机制。
- 不能说结论可迁移真实 GEO / 三轴自由姿态 / 暗室实验。
```

---

## 3. 方法采用判断（Claude 判断，均未放行）

等级定义：**建议采用**=技术上应纳入下一阶段主路径；**候选采用**=有价值但需先决条件或并列对照；**暂缓**=方向成立但当前不做；**不建议**=当前不应做或风险过高。所有等级都要 Codex/作者放行后才执行。

| 方法方向 | 建议等级 | 文献依据 | 项目对应问题 | 预期解决 | 主要风险 | 需新阶段门 | 是否破坏 R04 链 |
|---|---|---|---|---|---|---|---|
| 分类 exact-bin → circular regression / von-Mises | 建议采用 | Tang 2025；现代角度回归实践；1.6 | exact-bin 0% 由判据放大 | 把哨兵指标换成连续角误差，可能直接改变“是否失败”判断 | 被读成“为追结果换判据” | 是（C 类） | 否（新脚本/副本，不改原链） |
| regression+classification 双头 | 候选采用 | 1.6 | 兼容旧叙事与新指标 | 保留 exact-bin 作 sentinel，同时给连续误差 | 复杂度上升 | 是 | 否 |
| V0.3↔V0.4 协议对齐只读核查 | 建议采用 | 84 号 Q5；无需新文献 | 判定是口径问题还是物理边界 | 区分“口径变严”vs“真边界” | 误读为可换回 random split 宣告成功 | 否（只读重聚合） | 否 |
| 伪光变曲线只读探针 | 建议采用 | 84 号 3A；Kaasalainen；Kumar 2025 | 单帧 vs 序列信息差的零成本预检 | 看序列结构是否强于单帧 | 仅探针，不能当正式结论 | 否（只读已有数据） | 否 |
| mid / late / decision-level fusion | 建议采用 | ChiNet 2022；Pasqualetto 2021；Liu 2024；1.3 | 互补性支柱目前是虚的 | 真正回答“是否互补” | 工程量；需平衡模态维度 | 是（C 类） | 否 |
| cross-attention fusion | 候选采用 | ChiNet 2022；1.3/1.6 | 防图像淹没 OCS | 更强互补建模 | 数据量小易过拟合 | 是 | 否 |
| modality-balanced（维度/归一化平衡） | 候选采用 | 1.3 | image 256 淹没 OCS 128 | 低成本缓解淹没 | 增益可能有限 | 是 | 否 |
| 图像加噪声 / 数据增广 | 候选采用 | SPEED+；Bechini 2023；1.4 | 零噪声学渲染伪影捷径 | 提升现实性、防捷径 | 改变 baseline 难度，需重训对照 | 是（C 类） | 否 |
| 信息源升级：light-curve sequence + 序列模型 | 建议采用（治本，需新数据） | Kaasalainen；Wetterer&Jah 2009；Kumar 2025；1.1/1.6 | 单帧信息不足以消歧 | 把负结果升级为“序列才够”的正向发现 | 需新渲染/新数据，工程最大 | 是（C 类，最重） | 否（全新数据线） |
| 更强 backbone（ResNet/ViT/预训练） | 暂缓 | Sosa 2025；Dickinson 2025；1.6 | 浅 CNN 容量限制 | 提升图像分支上限 | 易被读成堆模型追结果；小数据过拟合 | 是 | 否 |
| 偏振 / 多光谱信息维 | 暂缓 | Dianetti&Crassidis 2023；Marto 2024；Yang 2025 | 增加可观测维度 | 打破歧义的物理新维 | 需全新前向模型与数据 | 是 | 否 |
| 可观测性诊断：signature distance / Fisher-CRLB / confusion cluster / geometry coverage | 建议采用（只读优先） | Gerwe&Idell 2003；Kaasalainen；1.5 | extrapolation gap 缺理论支撑 | 把实验失败升级为可观测性论证 | 理论工具与当前离散协议对接需谨慎 | 部分只读可不设门；建模分析需门 | 否 |
| 校准 / ECE | 候选采用 | Guo 2017；1.6 | 置信一致性目前偏弱 | 给“可信”一个可测指标 | 不改信息源则增益有限 | 是 | 否 |
| conformal prediction / prediction set | 候选采用 | Angelopoulos&Bates 2023；1.6 | sentinel→可写拒识机制 | 实现有覆盖保证的拒识 | 需校准集；解释成本 | 是 | 否 |
| agreement/disagreement（双通道一致性） | 候选采用 | 多模态融合；24 号三问 trustworthy | 置信一致性主线 | 用通道一致性做置信代理 | 需先有非朴素 fusion | 是 | 否 |

---

## 4. 推荐优先级（Claude 判断，未放行）

分级原则：**杠杆 ÷ 风险 ÷ 成本**。低成本、高杠杆、能改变“是否失败”判断、且不威胁 R04 链的优先。

**P0（最先，零/低风险，无新训练）——先做诊断，再谈改模型**
```text
P0-1  V0.3↔V0.4 评测协议对齐只读核查（同 split 口径、同判据下 V0.3 数是否仍成立）。
P0-2  伪光变曲线只读探针（现有数据按 yaw 排序串序列，看序列结构与可分性）。
P0-3  可观测性只读诊断起步：signature distance / confusion cluster / geometry coverage 的只读版本。
理由：这三项不新训练、不改 split/模型，能直接判定“负结果是口径产物还是物理边界”，
      是后续一切方法选择的前置事实。先做这层最划算。
```

**P1（次先，单项 C 类阶段门，逐项记录边际贡献）**
```text
P1-1  判据/损失改正：分类 exact-bin → circular regression / von-Mises（或回归+分类双头）。
P1-2  fusion 结构改正：naive early → mid/late/decision-level，并做模态维度平衡，真正测互补性。
P1-3  可观测性建模诊断：Fisher/CRLB 下界分析（需建模，单设门）。
理由：P1-1 是“判据放大”最大人为来源的直接修正，最高单点杠杆；
      P1-2 是把“互补性虚目标”变实的唯一途径；二者均不需新数据，仅需副本/新脚本。
```

**P2（治本，需新数据，最重阶段门）**
```text
P2-1  light-curve sequence 正式数据生成 + 序列模型（1D-CNN/LSTM/Transformer）。
P2-2  图像加噪声/数据增广 + 现实性增强对照。
理由：治本但成本最高、风险最大（追结果质疑）。必须在 P0/P1 把“是否值得投入”判断清楚后再进。
```

**P3（增强层，置信一致性与可信度）**
```text
P3-1  校准/ECE。
P3-2  conformal prediction / prediction set / agreement-disagreement 拒识机制。
P3-3  更强 backbone、偏振/多光谱等新信息维（暂缓档）。
理由：这些服务 24 号三问的 trustworthy 支柱，但在信息源/融合未升级前，单独做增益有限。
```

> 我不机械保守：**我明确建议把“判据改正（P1-1）+ fusion 改正（P1-2）”作为最值得投入的两项**，并把 light-curve（P2-1）列为治本主线。但我同样明确：这些是我的方法判断，**全部未放行**，且必须先过 P0 只读诊断这一关。

---

## 5. B-3 候选设计：单帧 OCS vs light-curve / 多时刻光度对比（只设计，不执行）

目标：把当前负结果升级为“单帧信息不足、序列才够”的正向可观测性发现，而**不是**用序列替换单帧后只报新数。核心是**信息源对比**，单帧与序列都保留。

### 5.1 设计骨架（三阶梯，风险递增）

```text
阶梯 0（P0，红线内，只读，无新数据）：伪光变曲线探针
  - 用现有数据：固定 pitch，将连续 yaw 的多帧单帧 OCS 按 yaw 排序串成伪序列。
  - 只做只读分析：序列是否呈可辨识曲线结构；序列可分性是否强于单帧（如最近邻/线性可分性的描述性对比）。
  - 不重新渲染、不训练新模型、不改 split。
  - 产出：单帧 vs 伪序列“信息差是否存在”的描述性证据，决定是否值得做阶梯 2。

阶梯 1（P1，C 类，无新数据，改判据/模型）：同数据不同任务形式对照
  - 在现有单帧数据上，对比 分类exact-bin / circular regression / von-Mises 三种判据。
  - 用于剥离“判据放大”对负结果的贡献，是阶梯 2 的对照基线。

阶梯 2（P2，C 类，需新数据，最重门）：正式 light-curve 序列生成与对比
  - Blender 前向模型沿连续观测几何/自转角渲染帧序列，聚合成亮度-角度曲线。
  - 配序列模型（1D-CNN / LSTM / Transformer）。
  - 主对比：单帧 OCS vs light-curve sequence 在同一姿态量、同一 split 协议下的 yaw 外推可分性。
```

### 5.2 对照与协议要求（防 inverse crime / 防 leakage）

```text
- 必须沿用 circular yaw-block 外推协议作为主难度档，random split 仅作分布内对照。
- 序列与单帧必须在同一 yaw-block 划分下比较，禁止序列偷偷使用单帧未见的 yaw 信息造成泄漏。
- 序列数据生成属新数据：必须显式记录前向模型、采样几何、与 R04 数据的关系，保 inverse-crime 防护。
- 关系定位：单帧 vs 序列是【层级关系】（序列是更高信息层级），不是替代；论文骨架写成对比，不写成“换了就好”。
```

### 5.3 B-3 不做什么
```text
- 不二选一删除单帧 OCS 线。
- 不在本设计中放行任何渲染或训练。
- 不声称序列一定成功（探针前不预判结论）。
```

---

## 6. B-4 候选设计：模型 / 任务形式 / 融合 / 不确定性改正（只设计，不执行）

四个子模块，建议**逐项单独阶段门、逐项记录边际贡献**，禁止一次性全堆（84 号已警告：全堆=把预注册负结果污染成调参追结果）。

### 6.1 任务形式 / 判据（B-4A，P1）
```text
- 主候选：circular regression + von-Mises loss，替代 72 硬 bin + exact-bin。
- 兼容候选：regression + classification 双头，保留 exact-bin 作 sentinel。
- 指标：circular MAE / within-k° / coarse-bin vs chance（延续 E45B 重构口径）；新增连续角误差与校准前置位。
- 验证：必须与现有分类基线在同 split 下对照，单独报告判据改正贡献。
```

### 6.2 融合结构（B-4B，P1）
```text
- 候选谱：mid fusion / late(decision-level) fusion / cross-attention / modality-balanced concat。
- 必做：模态维度平衡（防 image 256 淹没 OCS 128）。
- 互补性度量：late-fusion gain、消融、（可选）互信息估计；不能只看一次 early concat。
- 验证：以现有 early-concat 为基线，报告每种 fusion 的互补增益边际值。
```

### 6.3 信息源（B-4C，P2，指向 B-3 阶梯 2）
```text
- 单帧 OCS（保留为下界基线）→ light-curve sequence + 序列模型。
- 与 B-3 共用同一序列数据生成阶段门，避免重复造数据。
```

### 6.4 不确定性 / 置信（B-4D，P3）
```text
- 校准/ECE（Guo 2017）作为第一步可测置信指标。
- conformal prediction / prediction set（Angelopoulos&Bates 2023）把 sentinel 升级为有覆盖保证的拒识。
- 双通道 agreement/disagreement 作为 24 号三问 trustworthy 支柱的置信代理。
- 前置条件：B-4D 的收益依赖 B-4A/B 已落地；信息源未改时单独做校准增益有限。
```

### 6.5 B-4 执行纪律
```text
- 顺序建议：A（判据）→ B（融合）→ C（信息源）→ D（不确定性）。
- 每项独立可放行单元，逐项记录边际贡献，使改进过程成为可发表消融，而非追结果。
- 全部基于副本/新脚本，保 R04 负结果链可复现。
```

---

## 7. 与头A合并审阅的触发条件

按 R05，头A 已在 R90 达成闭合口（A-1/A-2/A-3 全部 DONE：R86/R88/R90，成果区 16/17/18）。头B 现状：

```text
B-1 文献检索：DONE（R91，PDF 入库 30 篇）
B-2 方法总结与后续方法规划：本文件（待 Codex 审阅）
B-3 单帧 vs 光变曲线对比设计：本文件已给候选设计，未执行
B-4 模型改正候选：本文件已给候选设计，未执行
```

合并审阅触发条件（R05 第 5 节）现状判断：
```text
条件 1 头A收口边界清晰：已满足（R90）。
条件 2 头B后续方案清晰：
  - 文献检索结论成形：是（R91）。
  - 方法总结草案成形：本 B-2 提供。
  - 单帧 vs 光变曲线对比方案 + 模型改正优先级有候选版本：本 B-2 提供。
→ 我的判断：本 B-2 通过 Codex 审阅后，条件 2 即满足，可触发头A/头B合并审阅。
```

建议合并审阅重定的下一阶段入口（供裁决，未放行）：
```text
优先裁定是否放行 P0 只读层（协议对齐核查 + 伪光变探针 + 只读可观测性诊断），
再据 P0 结果决定是否进入 P1 判据/融合改正的 C 类阶段门。
```

---

## 8. 红线与待 Codex / 作者裁决问题

### 8.1 红线自检
```text
- 本文件不启动训练、不生成数据、不改 split/模型/超参/seed、不改代码、不改正文、不改成果区、不改 CLAUDE.md。
- 未声称当前模型能可靠反演；未声称已证互补；未把 exact-bin 0% 当物理不可观测或已实现拒识。
- 未把 light-curve 文献等同当前单帧 OCS 结果；未把 modern fusion 文献当作 joint negative result 的反证。
- 未把 calibration/conformal 文献包装成系统已有拒识能力；未外推真实 GEO/三轴/暗室。
- “建议采用/优先级/B-3/B-4”全部为 Claude 方法判断，均未放行，需 Codex/作者按阶段门裁定。
```

### 8.2 待裁决问题（不自行放行）
```text
Q1. 是否放行 P0 只读层（协议对齐核查 / 伪光变探针 / 只读可观测性诊断）？三者顺序与范围？
Q2. P1 判据改正（circular regression/von-Mises）是否值得作为第一个 C 类阶段门？是否要求双头以保 sentinel 兼容？
Q3. fusion 改正（P1-2）与判据改正（P1-1）谁先？是否要求二者解耦各自单独消融？
Q4. light-curve 序列数据生成（P2）的阶段门门槛与 inverse-crime 防护规格由谁定稿？
Q5. 可观测性诊断中，哪些可归为 D 类只读（不设重门），哪些必须建模另设门？
Q6. 本 B-2 是否已满足 R05 合并审阅条件 2，可否即触发头A/头B合并审阅？
Q7. 置信一致性（24 号三问 trustworthy）最低可写实现门槛是什么（ECE？conformal？agreement？），由 Codex 定义验收口径。
```

### 8.3 关联文件
```text
R91（B-1 文献约束）、85（文献补课）、84（暂停点复盘与代码事实）、
R90（头A桥接稳定）、R05（两头并行结构）、05（PDF 入库状态）。
```

