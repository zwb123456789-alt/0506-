# 85 文献补课材料：检索提示词与重点订阅期刊

最后更新：2026-06-29
性质：Claude 整理的文献检索辅助材料，供作者交 GPT / 数据库检索与订阅参考。
用途：补齐"光度/光变曲线姿态反演、可观测性、图像-光度融合、sim-to-real"方法盲区。

> 本文件不是路线裁决、不是放行、不替代任何审阅。仅作为方法学习与文献调研的输入。

---

## 第一部分：需要补充的文献领域 + GPT 检索提示词

下列每块给出「为什么要查 + 直接可复制给 GPT/检索引擎的提示词」。建议中英文各检一轮（CNKI 用中文，WoS/Scopus/Google Scholar 用英文）。

### 领域 1：光变曲线 / 光度反演（方法源头，最重要）
为什么：本项目当前是"单帧多维标量 OCS"反演；真实工程与天文界主流是"光变曲线（light-curve）反演"，对"何时可反演、何时退化/歧义"有几十年成熟结论，直接对应可观测性边界。

英文提示词：
```text
Survey light curve inversion methods for determining the shape, spin state, and
attitude of space objects and asteroids. Focus on: (1) when attitude/pose is
observable from photometry vs when it is ambiguous or degenerate (convex vs
non-convex ambiguity, mirror ambiguity); (2) information limits of single-epoch
vs multi-epoch / multi-geometry photometry; (3) Kaasalainen-type inversion and
its assumptions. Return key papers with year, venue, and the core observability
conclusion of each.
```

中文提示词：
```text
综述空间目标与小行星光变曲线反演方法，用于反演形状、自旋状态与姿态。重点：
(1) 何种条件下姿态可由光度观测；何时存在歧义或退化（凸/非凸歧义、镜像歧义）；
(2) 单时刻 vs 多时刻/多几何光度的信息上限；(3) 经典反演方法的前提假设。
按年份、来源、核心可观测性结论列出关键文献。
```

### 领域 2：空间目标光学特征化（SSA / Space Object Characterization）
为什么：直接对标本项目应用背景（GEO/空间目标姿态、材质、构型识别），并印证专家"光度多用于异动监测而非精确定姿"的现状。

英文提示词：
```text
Review space situational awareness (SSA) work on characterizing GEO/LEO objects
from ground-based photometry: attitude estimation, material/BRDF inference,
anomaly detection. Distinguish methods that claim accurate attitude inversion
from methods that only do anomaly/state-change detection. Note datasets used,
whether ground-truth attitude was available, and reported accuracy limits.
```

中文提示词：
```text
综述地基光度观测对 GEO/LEO 空间目标的特征化研究：姿态估计、材质/BRDF 推断、
异常监测。区分"声称可精确反演姿态"与"仅做异常/状态变化检测"的方法。注明所用
数据集、是否有姿态真值、报告的精度上限。
```

### 领域 3：图像 + 光度 / 多模态融合方法（补"互补性"缺口）
为什么：本项目 joint 只测了 early-concat+线性头（见 84 号文件），无法真正回答互补性。需了解 early/mid/late fusion、交叉注意力、信息论互信息评估。

英文提示词：
```text
Survey multimodal fusion strategies (early/feature-level, intermediate,
late/decision-level, cross-attention) for combining a high-dimensional image
branch with a low-dimensional scalar/vector branch. Focus on: how to prevent the
high-dimensional modality from dominating; how to measure whether two modalities
are genuinely complementary (mutual information, ablation, late fusion gain).
Include remote sensing / vision examples.
```

中文提示词：
```text
综述多模态融合策略（早期/特征级、中间级、晚期/决策级、交叉注意力），用于结合
高维图像分支与低维标量/向量分支。重点：如何防止高维模态淹没低维模态；如何衡量
两模态是否真正互补（互信息、消融、晚期融合增益）。可含遥感/视觉示例。
```

### 领域 4：仿真到真实 / sim-to-real 与合成数据反演可信度
为什么：回应专家"仿真偏离真实、结论无法解耦"的质疑；学习如何用域随机化、噪声注入、真实数据锚点提升合成基准可信度。

英文提示词：
```text
Review sim-to-real gap and synthetic-data credibility for vision/photometry-based
inverse problems: domain randomization, noise injection (Gaussian/Poisson/sensor),
domain adaptation, and the "inverse crime" pitfall where the same forward model is
used for data generation and inversion. How do papers justify that conclusions from
synthetic benchmarks transfer (or explicitly do not transfer) to real data?
```

中文提示词：
```text
综述基于视觉/光度的反问题中 sim-to-real 差距与合成数据可信度：域随机化、噪声注入
（高斯/泊松/传感器噪声）、域适配，以及"inverse crime"陷阱（同一前向模型既生成数据
又做反演）。论文如何论证合成基准结论能否迁移到真实数据？
```

### 领域 5（可选）：姿态估计的可观测性分析
为什么：把"yaw-block 外推失败"提升为正式的可观测性/可辨识性论述，而非单纯实验失败。

英文提示词：
```text
Survey observability and identifiability analysis for attitude/pose estimation from
optical measurements. Include theoretical tools (observability Gramian, Fisher
information / Cramér-Rao bound, identifiability under limited viewing geometry) and
how they explain when attitude is recoverable vs unrecoverable from limited
observations.
```

### 领域 6：现代姿态反演/融合/序列/不确定性架构（模型改进重点参考）
为什么：本项目当前是 2018 风格纯基础模型（CNN + 单层线性头 + 分类 exact-bin），疑为实验失败重要根源。模型改进前必须先看清现代可选架构与其相对基础 CNN 的实测增益。直接服务 84 号文件 3B 的 A→D 改进清单。

英文提示词：
```text
Survey modern deep architectures for pose/attitude regression from images and
from low-dimensional sensor vectors, as upgrades over plain CNN + linear-head
classifiers. Cover: (1) regression vs binned-classification for angular targets,
circular/von-Mises loss; (2) backbones (ResNet, ViT, pretrained) for pose;
(3) multimodal fusion (mid/late, cross-attention) preventing high-dim modality
dominance; (4) sequence models (1D-CNN/LSTM/Transformer) for light-curve / time-
series inversion; (5) uncertainty-aware prediction for confidence/rejection.
Return concrete architecture choices with the reported accuracy gain over CNN
baselines.
```

中文提示词：
```text
综述用于图像与低维传感向量姿态反演的现代深度架构，作为"纯 CNN + 线性分类头"的升级。
覆盖：(1) 角度目标的回归 vs 分箱分类、circular/von-Mises 损失；(2) 姿态用 backbone
（ResNet、ViT、预训练）；(3) 多模态融合（中/晚期、交叉注意力）如何防止高维模态淹没低维；
(4) 序列模型（1D-CNN/LSTM/Transformer）用于光变曲线/时间序列反演；(5) 不确定性预测用于
置信/拒识。给出具体架构选择及其相对 CNN baseline 的实测精度增益。
```

---

## 第二部分：最需要订阅 / 重点参考的期刊与会议

### 领域核心期刊（优先订阅前 2 个）
| 期刊 | 为什么 |
|---|---|
| **Advances in Space Research**（COSPAR/Elsevier） | SSA 光度反演、空间目标特征化高频发表，最贴本项目应用与 claim 边界 |
| **Acta Astronautica**（IAA/Elsevier） | 航天工程、空间目标观测与姿态相关 |
| **Journal of Guidance, Control, and Dynamics**（AIAA） | 姿态估计、可观测性、滤波，方法层支撑 |
| **IEEE Transactions on Aerospace and Electronic Systems (TAES)** | 雷达/光学目标观测、估计理论 |

### 光学 / 反演方法期刊
| 期刊 | 为什么 |
|---|---|
| **JOSA A**（Optica） | BRDF、成像物理、光学反问题 |
| **Optics Express / Applied Optics** | 成像、传感器噪声、光度测量 |
| **Icarus / Astronomy & Astrophysics** | 光变曲线反演方法源头（小行星/天体，方法可借鉴） |

### 会议（本领域会议常比期刊更前沿，强烈建议跟踪）
| 会议 | 为什么 |
|---|---|
| **AMOS — Advanced Maui Optical and Space Surveillance Technologies** | SSA 光度/光变反演核心会议，**必看**；几乎所有空间目标光度姿态工作都在此发表 |
| **AAS/AIAA Astrodynamics Specialist Conference** | 姿态/轨道估计 |
| **IAC — International Astronautical Congress** | 航天综合 |

### 订阅建议（最小可行）
```text
优先级 1：Advances in Space Research（期刊）+ AMOS proceedings（会议）
          —— 与本项目 claim 边界、专家"光度多用于异动监测"质疑最贴。
优先级 2：JGCD（姿态估计/可观测性）+ Icarus（光变曲线反演方法源头）。
其余按检索命中文献的出处再补订。
```

---

## 第三部分：内部知识库先行回看
在外部检索前，先回看本项目已有知识库对方法的支撑，避免重复：
```text
06_书籍知识库/13_书籍知识库对v0.4主线的方法支撑与路线把控.md
（R2-Codex 已正式覆盖；含 B1 书中改进冯模型、BRDF、方法把控）
```

---

## 红线自检
- 本文件为文献调研辅助材料，不放行、不裁决、不改成果区。
- 不据此宣称任何方法已验证有效；文献用于学习与故事化，不替代本项目实验证据。
- 关联：84 号暂停点中期复盘（本目录）。
