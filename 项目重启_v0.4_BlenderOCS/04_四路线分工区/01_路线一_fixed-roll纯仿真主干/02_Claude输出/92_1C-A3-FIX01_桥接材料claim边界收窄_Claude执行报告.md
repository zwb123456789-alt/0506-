# 92_1C-A3-FIX01 桥接材料 claim 边界收窄 — Claude 执行报告

最后更新：2026-06-29  
执行端：Claude  
任务来源：R89_Codex_审阅_1C-A3需FIX01_桥接材料claim边界收窄.md  
修正对象：91_1C-A3_负结果到24号三问桥接材料_Claude执行报告.md  
性质：FIX01 修正版桥接说明材料（非论文正文正式段落）

---

## 0. 执行摘要

本文档是 91 号 A-3 桥接材料的 FIX01 修正版。按 R89 要求，对五处 claim 边界进行了收窄：sentinel/拒识口径、Figure S3 口径、OCS-only 口径、pitch 定性口径、共同失效口径。三问结构、数值主线和资产映射保持不变。

核心桥接结论（FIX01 收窄后）：

```text
fixed-roll + circular yaw-block holdout 协议下：
- yaw 在分布内可学（random split ~65-70% exact），在分布外不可外推（circular yaw-block exact-bin = 0.00%）；
- fixed-roll + 当前图像模型 + circular yaw-block 协议下，pitch 指标稳定高于 chance（within-3 ~52-56% vs chance ~19%）；
- early fusion（joint）不自动提升 yaw，pitch 甚至略低于 image-only；
- exact-bin yaw = 0.00% 只作为诊断性 sentinel，提示 strict classifier 在 circular yaw-block 外推场景下发生失败；
  可以启发后续 reject / confidence gate 设计，但当前尚未实现或验证真正的拒识机制。
```

---

## 1. 固定协议负结果证据总览

### 1.1 固定协议定义

```text
协议：fixed-roll（roll ≡ 0°），circular yaw-block 5-fold holdout
姿态空间：yaw ∈ [0°, 360°)，pitch ∈ [-90°, 90°]，roll ≡ 0°
split 策略：circular yaw-block — 训练集覆盖连续 yaw 弧段，验证/测试集覆盖剩余 yaw 弧段
度量：exact-bin（72 bins × 37 bins）、circular MAE、within-k、coarse-bin
模型：共享 ResNet-18 主干 + yaw/pitch 双头分类器，OCS 通过 MLP 投影后与图像特征 concat
```

### 1.2 当前稳定指标（Table 2 精炼）

| 指标 | chance/random baseline | C2 OCS-only | C3 image_only | C3 joint |
|---|---:|---:|---:|---:|
| exact-bin yaw_acc | 1.39% | 0.00% | 0.00% | 0.00% |
| yaw CMAE (deg) | ≈90.0 | 97.0 | 81.4 | 81.4 |
| yaw within-3 | 9.72% | 9.96% | 17.12% | 17.74% |
| yaw within-6 | 18.06% | 18.89% | 25.57% | 26.51% |
| yaw coarse45 | 12.50% | 14.53% | 17.96% | 18.16% |
| pitch exact | 2.70% | 3.03% | 21.20% | 19.42% |
| pitch within-3 | 18.92% | 17.75% | 56.07% | 51.77% |

**对照：random split 下的 yaw exact-bin ≈ 65–70%（E45A 归因诊断，R80 稳定）。**

### 1.3 关键发现

1. **Yaw extrapolation gap（核心发现）**：circular yaw-block 下，所有通道的 exact-bin yaw = 0.00%，连续指标（CMAE / within-k / coarse45）仅微弱高于 chance。但 random split 下 yaw 可学到 ~65-70%，说明问题不在 yaw 信号不存在，而在 cross-yaw-arc 外推。

2. **Pitch anisotropy under fixed-roll（稳定发现）**：fixed-roll + 当前图像模型 + circular yaw-block 协议下，pitch 指标稳定高于 chance——pitch within-3 达到 ~52-56%（chance ~19%），但该结论不泛化至三轴姿态、真实目标或其他图像退化条件。

3. **Early fusion no automatic gain（稳定发现）**：joint（early fusion by concatenation）在 yaw 上不优于 image-only（CMAE 均为 81.4°），pitch 上甚至略低于 image-only（within-3: 51.77% vs 56.07%）。

4. **C2 OCS-only 在当前协议下未检出高于 chance 的信号（固定协议证据）**：C2 OCS-only 在所有 yaw 和 pitch 指标上接近 chance。这不等于 OCS 通道本身不携带姿态信息——可能是 C2 OCS 特征构造、几何采样方案或模型架构在此协议下不足以提取信号。

---

## 2. 桥接到 24 号三问

### 2.1 桥接 What can be known?

**24 号原问：**

> 在已知几何和名义材料条件下，跨几何 OCS 光度向量与图像通道分别对姿态有多少可区分信息？

**当前负结果能回答什么：**

```text
1. fixed-roll + 当前图像模型 + circular yaw-block 协议下，图像通道对 pitch
   携带可区分信息：
   C3 image_only pitch within-3 = 56.07%（chance = 18.92%），
   但该结论限于 fixed-roll 条件，不泛化至三轴姿态、真实目标或任意图像退化条件。

2. fixed-roll 条件下，图像通道对 yaw 的可区分信息受限于观测几何覆盖：
   random split（分布内 yaw）→ yaw exact-bin ≈ 65-70%；
   circular yaw-block（分布外 yaw 弧段）→ yaw exact-bin = 0.00%，
   连续指标仅微弱高于 chance。
   结论：yaw 信息在分布内存在，但无法通过当前模型跨 yaw 弧段外推。

3. 在当前固定协议下，C2 OCS-only 未检出稳定高于 chance 的 yaw 或 pitch 可区分信息：
   C2 OCS-only 所有指标接近 chance。
   这不等于 OCS 通道原则上不可能携带姿态信息——
   可能是 C2 的 OCS 特征构造、几何采样方案或模型架构在此协议下不充分。
```

**当前负结果不能回答什么：**

```text
- OCS 在其他几何采样方案（如更密集的 sun/view 覆盖、最优几何选择）下是否可区分 yaw/pitch。
- roll ≠ 0 时 yaw/pitch 的可观测性是否改变。
- 更复杂的 OCS 特征（如几何编码、物理信息嵌入）是否能提取 yaw 信号。
- 三轴姿态（yaw/pitch/roll 同时自由）下各通道的信息量。
```

**桥接判断：**

当前负结果给出了 fixed-roll 下 "what can be known" 的一个 **lower-bound 约束**：在固定协议下，图像通道可在 fixed-roll 条件下区分 pitch，但 yaw 信息无法跨弧段外推；C2 OCS-only 在当前特征、模型和协议下未检出高于 chance 的可区分信号。这是 24 号第一问在当前实验条件下的一个具体、有边界的部分回答。

### 2.2 桥接 When complementary?

**24 号原问：**

> 哪些姿态或观测几何下 OCS 有效，哪些地方图像有效，哪些地方二者互补或共同失效？

**当前负结果能回答什么：**

```text
1. 互补在 fixed-roll + circular yaw-block + early fusion 协议下未观察到：
   joint（early fusion）在所有 yaw 指标上不优于 image-only，
   pitch 指标上 joint 甚至略低于 image-only。
   这不是"互补不存在"的普适结论，而是"在当前协议和当前 early fusion
   策略下，未观察到自动互补增益"的固定协议证据。

2. 当前观察到的是单模态主导而非互补：
   image-only 主导 pitch 信息，C2 OCS-only 在当前协议下未检出高于 chance 的信号，
   fusion 未超越 image-only。
   这意味着互补可能需要更精细的条件——
   可能是 OCS 特征质量、融合策略、或观测几何设计的问题。

3. protocol-defined extrapolation failure regime：
   yaw 在 circular holdout 下三通道均接近 chance
   → 这是 cross-yaw-arc 外推失败，不是已定位的物理低信息区域。
   当前尚未做 per-geometry observability map 或三轴信息地图。
```

**当前负结果不能回答什么：**

```text
- OCS 在图像退化（blur/PSF/低 SNR）下是否提供互补信息——
  当前实验图像通道无退化。
- OCS 与图像在不同观测几何下的互补地图——
  当前未做按几何分层的 per-geometry 分析。
- 更复杂的融合策略（late fusion / attention / uncertainty-weighted）
  是否能解锁互补增益。
- image-derived OCS（口径 B）对照下互补是否退化为 common-mode error。
```

**桥接判断：**

当前负结果给出了 "when complementary" 的一个 **null-result 基准**：在 fixed-roll + circular yaw-block + early fusion 协议下，未观察到 OCS-image 互补。这为论文提供了一个诚实的研究基线——互补不是自动发生的，需要特定条件。这一 null result 本身可作为 24 号第二问的对照基线："在没有互补的条件下，各通道表现为何"。

### 2.3 桥接 When trustworthy?

**24 号原问：**

> OCS 与图像的候选姿态是否一致，能否作为置信度或拒识依据？

**当前负结果能回答什么：**

```text
1. exact-bin yaw = 0.00% 的诊断性 sentinel 含义：
   exact-bin yaw = 0.00% 是 strict classifier + circular yaw-block 外推场景下的
   诊断性指标，提示当前协议下 exact-bin 分类发生失败。
   它可以启发后续 reject / confidence gate 设计，
   但当前尚未实现或验证真正的拒识机制（如 calibrated rejection、
   conformal prediction、ECE/reliability diagram 或 posterior-like agreement）。
   对照 random split 下 exact-bin ≈ 65-70%，说明 sentinel 的触发
   与 split protocol（分布内 vs 分布外）强相关。

2. 跨通道一致性的当前状态：
   C3 image_only 和 joint 在 yaw 连续指标上高度一致
   （CMAE 均为 81.4°，within-3 分别为 17.12% 和 17.74%），
   但这不是"两个独立通道互相印证"——
   因为 C2 OCS-only 在当前协议下未检出高于 chance 的独立信号，
   一致性更可能来自 image 通道主导和 OCS 通道的接近均匀输出。

3. 诊断性 sentinel 对后续置信机制设计的启发：
   exact-bin yaw = 0.00% 在 circular yaw-block 下提示：
   当 split protocol 限制为 strict cross-yaw-arc 时，
   该诊断指标标记了分类失败。
   这为后续设计 reject option / confidence gate 提供了经验证据——
   但当前尚未实现或验证这些机制。
```

**当前负结果不能回答什么：**

```text
- OCS-image posterior-like distribution agreement——
  当前模型为分类器 softmax 输出，未单独计算 posterior-like distribution。
- JS divergence / top-k overlap / consistency vs error 曲线——
  这些 24 号规划的置信指标当前未实现。
- image-derived OCS 对照下 consistency 是否退化为 common-mode failure——
  未做口径 B 对照。
- 当 OCS 和图像分别高置信但冲突时，应如何处理——
  当前 OCS-only 接近 chance，不存在"各自主张不同姿态"的场景。
- 当前尚未实现或验证 calibrated rejection / conformal prediction / ECE
  等正式拒识或置信校准机制。
```

**桥接判断：**

当前负结果给出了 "when trustworthy" 的一个 **诊断性 sentinel 级证据**：当系统处于 circular yaw-block 外推场景时，exact-bin sentinel 标记了 strict classifier 的失败。但这距离 24 号规划的完整 consistency-as-confidence 框架（跨通道分布对齐、JS divergence、top-k overlap、consistency vs error 曲线、拒识机制）还有显著距离。当前"可信"相关的判断更多来自对失败模式的诚实呈现，而非来自跨通道一致性的正向验证或已实现的拒识机制。

---

## 3. A-1/A-2 图表资产与三问的映射关系

### 3.1 已稳定资产的功能定位

| 资产 | 编号 | 服务的三问 | 功能 |
|---|---|---|---|
| Figure 3 | E45D | What can be known | yaw extrapolation gap 主图：yaw CMAE / within-6 / coarse45，三通道 vs chance |
| Figure 4 | E45D | What can be known | pitch anisotropy 辅助图：pitch exact / within-3，支撑 fixed-roll 下 pitch 强于 yaw |
| Table 2 | E45D | What can be known + When complementary | R82 指标重构主表：yaw + pitch 全指标，三通道对照 |
| Figure S3 | A2 | What can be known（方法透明度） | 训练过程可视化：training loss 下降且未见数值发散，提供训练透明度；但不排除优化不足、过拟合、模型结构限制或特征表达不足 |
| Figure S4 | A2 | What can be known（协议透明度） | circular yaw-block fold0 的 yaw-bin 覆盖，所有 formal folds overlap = strict |
| Table S3 | A2 | What can be known（结果透明度） | C3 image_only + joint 的 10 行 per-fold 明细 |
| Figure S5 | E45D | When trustworthy（sentinel 诊断） | exact-bin sentinel + holdout-prediction failure-mode diagnostic；诊断性指标，非已实现的拒识机制 |

### 3.2 当前资产覆盖的三问

```text
What can be known：      Figure 3, Figure 4, Table 2, Figure S3, Figure S4, Table S3
                         → fixed-roll 下 yaw/pitch 可观测性的 fixed-protocol 证据

When complementary：     Table 2（三通道对比行）
                         → 当前协议下未观察到互补增益的 null-result 基准

When trustworthy：       Figure S5（exact-bin 诊断性 sentinel diagnostic）
                         → 诊断性指标，启发后续设计；非已实现的拒识机制
```

---

## 4. 桥接后的缺口：从负结果到 24 号完整叙事还需要什么

以下缺口按 24 号的要求逐项列出，不作为当前放行任务，仅用于桥接说明。

### 4.1 What can be known — 缺口

```text
- 多几何 OCS 可观测性地图（per-geometry 信息量分布）：当前只有 aggregate 指标，
  不知道哪些 sun/view 几何携带更多 yaw/pitch 信息。
- 单几何 OCS 信息下界（F1 baseline）：未做。
- 姿态混淆图 / pairwise distance / nearest-neighbor ambiguity：未做。
- roll ≠ 0 时的可观测性变化：固定 roll=0，无法外推。
- random split 的 yaw 可学性已被 E45A 归因诊断确认（~65-70%），
  但 C3 formal 5-fold 未跑 random split 对照——当前只有 C2/C3 circular yaw-block 的正式结果。
```

### 4.2 When complementary — 缺口

```text
- OCS/image 错误互补图：未做。
- OCS/image 混淆互补图：未做。
- per-geometry 互补分析：当前无 geometry-stratified 指标。
- 图像退化下 OCS 互补性检验：当前图像无退化。
- 替代融合策略（late fusion / attention / uncertainty-weighted）：仅测试了 early concat fusion。
- 口径 B（image-derived OCS）对照：未做。
```

### 4.3 When trustworthy — 缺口

```text
- OCS-image posterior-like distribution agreement：当前模型输出为 softmax 分类分数，
  未实现 24 号要求的 posterior-like distribution。
- JS divergence / top-k overlap / consistency vs error 曲线：未实现。
- ECE / reliability diagram：未实现。
- Calibrated rejection / conformal prediction：未实现。
- image-derived OCS 对照下 common-mode failure 分析：未做。
- 当前 exact-bin sentinel 为诊断性指标，标记 strict classifier 在 circular yaw-block
  外推下的失败；不是已实现或已校准的拒识机制。
```

---

## 5. 桥接材料的 claim 边界（红线）

### 5.1 允许的表述

```text
1. fixed-roll + circular yaw-block holdout 下，图像通道对 pitch 具有可区分的姿态信息
   （限于 fixed-roll 条件，不泛化至三轴姿态、真实目标或其他图像退化条件），
   对 yaw 的信息无法跨未见 yaw 弧段外推。

2. random split（分布内 yaw）下 yaw 可学到 ~65-70%（exact-bin），
   说明 yaw 信号在分布内存在；circular yaw-block 的失败本质是 extrapolation gap
   而非 yaw 信息完全不存在。

3. 在固定协议和 early fusion 策略下，OCS-image joint 未观察到自动互补增益，
   这构成互补研究的 fixed-protocol null-result 基准。

4. exact-bin yaw = 0.00% 可作为诊断性 sentinel，提示 strict classifier
   在 circular yaw-block 外推场景下发生失败；
   它可以启发后续 reject / confidence gate 设计，
   但当前尚未实现或验证真正的拒识机制。

5. 当前负结果为 24 号三问提供了 fixed-protocol 下的 lower-bound 约束
   和 null-result 基准，但不构成对三问的完整回答。
```

### 5.2 不得使用的表述

```text
- yaw 在物理上不可观测。
- OCS 通道本身不携带姿态信息。
- OCS-image fusion 在所有条件下均无用。
- 系统"知道自己不知道" / 已实现拒识。
- exact-bin sentinel 可提供清晰的拒识信号 / 系统应当拒识而非猜测。
- Figure S3 排除了训练失败作为负结果原因。
- 当前结果可外推至真实 GEO 目标、三轴自由姿态或暗室实验。
- 当前结果证明了 consistency-as-confidence 框架的有效性或无效性。
- 当前负结果已完整回答 24 号三问。
- Figure S3 证明模型无过拟合 / 已学到最优表示。
- exact-bin yaw = 0.00% 单独承载了 yaw 不可观测的主 claim。
- pitch 在任何条件下均可学（未加 fixed-roll 限定）。
- 已定位出姿态空间中的物理低信息区域（"共同失效区域"）。
```

---

## 6. 桥接材料的使用方式

本材料预计在后续论文正文中以下列方式使用：

```text
1. Introduction 末尾 → 三问的提出（来自 24 号）。
2. Results 开头 → "在报告正面结果之前，先呈现固定协议下的负结果基准"。
3. Results 的 yaw extrapolation gap 小节 →
   Figure 3 + Table 2 支撑 "what can be known" 的 lower bound。
4. Results 的 pitch anisotropy 小节 →
   Figure 4 支撑 fixed-roll 下 pitch 指标高于 chance。
5. Results 的 fusion 小节 →
   Table 2 三通道对比行支撑 "early fusion no automatic gain"。
6. Discussion →
   - 负结果不应被解读为 yaw 不可观测或 fusion 无用；
   - extrapolation gap 的本质是 cross-yaw-arc 外推失败；
   - random split 的 ~65-70% 说明 yaw 在分布内可学；
   - exact-bin sentinel 是诊断性指标，启发后续置信门控设计，非已实现的拒识机制；
   - 下一步需要 per-geometry 分析、替代融合策略和 OCS 特征改进。
7. SI →
   Figure S3/S4/Table S3 补充训练透明度、协议透明度、per-fold 明细。
   Figure S5 补充 exact-bin 诊断性 sentinel 与 holdout-prediction 失败模式。
```

---

## 7. 总结：从负结果到三问的一句话桥接（FIX01 收窄版）

```text
在 fixed-roll + circular yaw-block holdout 的固定协议下，
"what can be known" 的回答是：fixed-roll 条件下 pitch 指标高于 chance，
yaw 在分布内可学但无法跨弧段外推，
C2 OCS-only 在当前特征、模型和协议下未检出高于 chance 的可区分信号；
"when complementary" 的回答是：以当前 early fusion 策略，未观察到自动互补增益，
这构成互补研究的 null-result 基准；
"when trustworthy" 的回答是：exact-bin sentinel 作为诊断性指标标记了
strict classifier 在 circular yaw-block 外推下的失败，
可以启发后续 reject / confidence gate 设计，但当前尚未实现或验证真正的拒识机制。
```

---

## 附录：FIX01 修改对照

| 位置 | 91 号原文（问题表述） | FIX01 修正 |
|---|---|---|
| 多处 | "系统知道自己不知道""应当拒识""拒绝输出""清晰拒识信号" | "诊断性 sentinel，提示 strict classifier 在外推场景下发生失败；可启发后续 reject/confidence gate 设计，但当前尚未实现或验证真正的拒识机制" |
| §3.1 Figure S3 行 | "排除训练失败作为负结果原因" | "提供训练透明度，training loss 下降且未见数值发散；但不排除优化不足、过拟合、模型结构限制或特征表达不足" |
| §1.3(4) / §2.1 | "OCS 多观测光度向量未携带可区分的 yaw 或 pitch 信息" | "C2 OCS-only 在当前特征、几何采样、模型和固定协议下，未检出稳定高于 chance 的 yaw/pitch 可区分信息" |
| §1.3(2) / §2.1 | "pitch 在各向异性下稳定可学" | "fixed-roll + 当前图像模型 + circular yaw-block 协议下，pitch 指标稳定高于 chance；不泛化至三轴姿态、真实目标或任意图像退化条件" |
| §2.2 | "共同失效区域" | "protocol-defined extrapolation failure regime；不是已定位的物理低信息区域" |

---

## 依据文件清单

```text
R89_Codex_审阅_1C-A3需FIX01_桥接材料claim边界收窄.md
R88_Codex_审阅_1C-A2-FIX01与A2-GEN通过_P0_SI资产草案稳定.md
91_1C-A3_负结果到24号三问桥接材料_Claude执行报告.md（修正对象）
```

执行红线确认：

```text
- 未启动训练、推理、新图表/表格生成。
- 未修改 split / 模型 / 超参 / seed。
- 未撰写论文正文正式段落——本文件为 FIX01 修正版桥接说明材料。
- 未启动档 B、raw 4-dim OCS-only、--mode all、三轴小项目、路线二/三/四。
- 未声称 yaw 物理不可观测、fusion 永久无用。
- 未外推真实 GEO / 三轴 / 暗室。
```
