# Claude 方案：v0.4 主线三条软肋与解决办法（附 FIM/CRLB 策略与投稿定位）

生成时间：2026-06-09
作者：Claude 执行端（97_交互审阅记录/01_Claude输出）
状态：候选方案稿，待作者与 Codex 审阅端确认；本文不修改 24/25/13/14 与启动集

---

## 〇、本文定位与边界

本文是对作者问题「24/25 号新主线（model-known 条件下 OCS/image 姿态信息可观测性、互补性、置信一致性）是否合理」的独立审阅结论，以及对审阅中发现的三条软肋给出可执行解决办法。

- 审阅对象：`24_v0.4项目论文主线最终冻结稿.md`、`25_v0.4主线冻结原因备案.md`，并对照已冻结的 `13_v0.4前向模型冻结规范.md`、`14_v0.4数据与manifest字段规范.md`。
- 总判断：**重构方向（旧"真实未知目标反演系统" → 24/25 新主线）合理且必要**。真正的硬触发是 v0.3 的 OCS/image 采样口径不统一（25 号 §3.3），这是修辞绕不过的定义级污染，必须重建统一前向模型。
- 本文不替代 24/25。本文输出的是：三条软肋的诊断 + 解决办法 + 优先级，供作者据此推进"下一步：重写 13/14 号规范 / 新建信息量与置信指标实现规范"。
- 硬约束遵循：本文只放在 `97_交互审阅记录/01_Claude输出/`，不擅改定位主线、方法冻结文件与启动集；是否采纳、是否同步启动集由作者与 Codex 审阅端决定。

---

## 一、三条软肋总览

新主线把投稿风险从"被审稿人一击击穿（旧主线过度宣称）"降到了"温和但仍需主动防守"。代价是引入三个**新的、需要在代码与实验阶段主动闭合**的弱点。若不闭合，合理的方案会在执行阶段漏气。

| 编号 | 软肋 | 性质 | 紧迫度 |
|---|---|---|---|
| 软肋 1 | L1 跨几何多观测向量隐含"采样窗口内姿态不变"假设 | 物理前提需明示 + 需边界实验 | 中（顺带做） |
| 软肋 2 | posterior-like distribution 实现口径未定，且已冻结的 13/14 schema 已脱节 | **直接 block 代码** | **高（最先做）** |
| 软肋 3 | 贡献点偏方法论，科学新颖性需升级（关系投稿层级） | 写作 + 可选理论增强 | 中（贯穿全程） |

三者并非孤立：软肋 1 与"OCS 必须多几何"是同一枚硬币的两面；软肋 3 的理论增强（FIM/CRLB）与作者的观测规划小项目咬合。

---

## 二、软肋 1：L1 向量的"姿态准静态"假设

### 2.1 问题

主线 OCS 形态为 L1 = multi-observation photometric vector across controlled sun/view geometries（24 号 §1.3 决策 2）：同一姿态在 k 个不同 sun/det 几何下各取一次总光通量，拼成跨几何向量。

审稿人会攻击：真实非合作目标通常在自转。若采集这 k 个几何观测的时间窗内姿态已经改变，则 L1 向量不再是"同一姿态的多几何读数"，而是"多个不同姿态的混合读数"，可观测性分析的前提就被破坏。

24 号把时变 / 自转留给 L2（Future Work），恰恰使 L1 的"姿态冻结"成为一个**被推迟却未明示**的理想化前提。当前红线清单（24 号 §15、CLAUDE.md §4）没有专门一条管这个。

### 2.2 作者已确认的方法设定

作者于 2026-06-09 确认：主线方法采用**短时间窗内多几何观测同一姿态**，后续增加敏感性分析。即：

```
controlled multi-geometry sampling under quasi-static assumption
= 在目标姿态可视为基本不变的短时间窗内，
  主动在多个受控 sun/det 观测几何下分别采集独立 OCS 读数，组成跨几何光度向量。
```

- controlled：观测几何是主动设计/挑选的（对应 13 号 §4.3 的 5 组 sun/det、相位角 24°~120°），不是随机。
- quasi-static：窗口内姿态近似不变，或已被姿态传播 / 补偿修正。纯仿真中固定姿态切换光照/视角，quasi-static 自动成立；论文须诚实声明真实部署时需要此假设。

### 2.3 解决办法（两步）

**第一步：明示物理语义 + 补一条红线。**

将 L1 向量明确表述为 *controlled multi-geometry sampling under a quasi-static / attitude-compensated assumption*，不得隐含"瞬时多通道同时读出"。建议新增红线（供作者并入 24 号 §15 或新规范，由 Codex 同步）：

```
红线（新增）：L1 跨几何 OCS 向量必须声明为"短时间窗内受控多几何采样、
窗口内姿态准静态或已补偿"。不得隐含瞬时多通道同时观测；
凡涉及自转 / 时变几何，归 L2 时域光变曲线（Future Work）。
```

**第二步：把攻击点做成一张结果图（零额外数据）。**

在主线数据集上，对 L1 向量施加一个小姿态扰动 Δθ，画 **observability 随 Δθ 的退化曲线 / 边界图**：

- 做法：对某姿态 q，构造其 L1 向量时，让 k 个几何分量分别取自 q + 微扰（模拟窗口内姿态漂移 Δθ），观察可观测性指标（如 nearest-neighbor ambiguity / posterior entropy / top-k confusion）随 Δθ 增大如何退化。
- 产出："L1 对姿态漂移的鲁棒性边界图"——回答"姿态漂移多大会破坏 L1 的有效性"。
- 价值：审稿人想攻击的点，反过来成为 observability 分析的一部分；同时给出 quasi-static 假设的**定量适用窗口**。
- 成本：零额外数据生成，主线离散网格数据集上即可计算（微扰可用网格邻域姿态近似或对签名插值）。

### 2.4 结论

软肋 1 不是要消除假设（假设无法消除），而是**明示假设 + 量化假设的适用边界**。处理后它从"被动挨打的漏洞"变成"主动报告的边界结果"。

---

## 三、软肋 1 与"OCS 为何必须多几何"的物理论证（支撑材料）

此节回答作者反复确认的关键问题：为什么 OCS 不能只记单方向，必须多几何。它是软肋 1 的"另一面"。

### 3.1 单方向 OCS 的数学困境

单方向 OCS 是一个标量：

```
OCS(q) = ∫ f_r(N, L, V) · NoL · V_sun · dA   （固定 sun_dir、det_dir）
```

这是从 2–3 维姿态空间到 1 维实数的映射。任何"高维→1 维"映射都有巨大的等值面（level set）：**一大片不同姿态给出几乎相同的 OCS 标量**。给定一个 OCS 读数反求姿态，是严重欠定问题。

后果（对应 24 号 §二）：
- OCS-only 的 posterior-like 分布接近均匀（一个标量切不开 2664 个候选）；
- OCS 相对 image 无真正互补，沦为图像陪跑；
- consistency-as-confidence 无从成立（OCS 端给不出有意义的候选分布）。

**单方向 OCS 不是"信息少一点"，而是"信息少到主线坍塌"。**

### 3.2 为什么多几何能解决

不同 (sun_dir, det_dir) 几何对同一姿态的等值面方向不同。k 个方向不同的标量约束取交集，可行姿态集被收窄：

```
单方向： q → s₁              （1 条等值面族）
多几何： q → (s₁,…,s_k)       （k 条不同方向的等值面族取交集 → 姿态被夹住）
```

这就是 24 号把主线 OCS 定为 L1 多观测向量、而非把单标量重复 k 次的原因——必须是**不同的** sun/view 几何（重复同一几何不增信息）。作者项目的 5 组 sun/det、相位角 24°~120° 正为此设计。

### 3.3 "2664 个候选"的来源

候选集 = 姿态网格全体（13 号 §4.2）：

```
yaw 72 个（0°~355°，步长 5°） × pitch 37 个（-90°~90°，步长 5°） = 2664 个离散姿态
```

姿态反演被建模为"从 2664 个已知姿态里挑出最像的"。若走网格分类范式，网络末层即 2664-d softmax，这 2664 个概率构成 posterior-like 分布。单标量 OCS 只能模糊抬高一大片候选 → 分布摊平；多几何向量 → 少数候选脱颖而出 → 分布尖锐。

### 3.4 代价 = 软肋 1

多几何买来的信息量，代价就是"k 个读数必须对应同一姿态"的 quasi-static 假设。所以：**必须上多几何（否则信息不足、主线塌）↔ 一旦多几何就默认窗口内姿态不变（软肋 1）**。处理方式见 §2.3。

---

## 四、软肋 2：posterior-like 实现口径未定 + 已冻结 schema 已脱节（最紧迫）

### 4.1 问题：两层问题，下层已 block 代码

**上层（论文层）：** confidence / JS divergence / entropy / ECE / consistency 全部依赖"候选姿态分布"。若反演模型是角度回归（直接吐 yaw/pitch 标量），天然没有分布，上述指标全部无法计算。24 号 §10.2 自己也标明 posterior-like distribution 的实现口径"必须在进训练代码前确定"。

**下层（已冻结文档层，更紧迫）：** 13/14 号（2026-06-08，已过 Codex CR5）只解决了**统一前向模型**（OCS 与 image 同源：同几何 / 同 BRDF / 同 V_sun_macro），这一层做得扎实。但它们的 manifest / summary / source_data schema 仍是 **v0.3 误差表范式**：

- 14 号 §9.1 `summary.json` 的 `metrics` 只有 `mean_error / hit@5 / hit@10 / worst_case / rmse`；
- 14 号 §1.3 训练任务仍是标准 OCS-only / image-only / fusion；
- **完全缺失** posterior-like distribution、top-k candidates、entropy、JS divergence、consistency、modality attribution、image-derived OCS_B 等字段。

而 24 号 §12 明确要求重跑必须保存这些。**结论：两份已冻结、已过复审的方法文件，撑不起 24 号主线的证据链。** 这不是它们写错，而是 13/14 冻结时点与主线定稿并行，新指标未并入。作者已确认（2026-06-09）：13/14 号确实过时，重写规范是下一步工作。本节给出重写的核心决策与回填增量。

### 4.2 核心决策：先定死"姿态反演范式"

这是唯一必须先拍板的决策，它决定网络末层、loss 与所有下游指标脚本：

```
OCS-only / image-only / fusion 三个模型必须输出
"同一离散姿态网格上的候选分布"，不能直接回归 (yaw, pitch)。
```

否则 entropy / JS / top-k / margin / consistency 全部无从计算。两条可选实现：

| 方案 | 做法 | 优点 | 代价 |
|---|---|---|---|
| **A. 网格分类（推荐主口径）** | 姿态网格本就离散（2664 类），末层 2664-d softmax = 天然 posterior-like | 指标口径统一、可比 | 类间无序，丢姿态流形结构；可用角度距离 soft-label / label smoothing 缓解 |
| **B. kNN likelihood（推荐作对照）** | 特征空间对 query 找最近邻姿态，用距离核构造分布 | 不必重训成分类器 | 分布质量依赖度量好坏 |

**建议：A 作主口径（指标可比、口径统一），B 作 sanity 对照。** 无论 A/B，三模态必须输出**同一姿态网格上的分布**，否则 JS divergence / top-k overlap 没有可比基础。

> 作者待拍板项：A 还是 B 作主口径。本文建议 A 主 + B 对照。

### 4.3 回填增量：14 号 summary schema 需新增字段

在重写 14 号时，`summary.json`（或新的 per-attitude 结果文件）需新增以下字段（对应 24 号 §10.3 最小指标集）。下表为增量，不替换原有 `mean_error` 等（它们降级为验证工具，保留）：

```json
{
  "inversion_paradigm": "<enum: 'grid_classification' | 'knn_likelihood'>",
  "pose_grid": { "n_candidates": 2664, "yaw_grid_deg": "...", "pitch_grid_deg": "..." },
  "per_attitude": [
    {
      "record_id": "<string>",
      "topk_candidates_ocs":   [{"cand_id": "...", "score": "..."}],
      "topk_candidates_image": [{"cand_id": "...", "score": "..."}],
      "topk_candidates_fusion":[{"cand_id": "...", "score": "..."}],
      "H_ocs":    "<float: OCS posterior-like entropy>",
      "H_img":    "<float: image posterior-like entropy>",
      "H_fusion": "<float: fusion posterior-like entropy>",
      "M_ocs":    "<float: OCS top1-top2 margin>",
      "M_img":    "<float: image top1-top2 margin>",
      "Overlap_k":   "<float: top-k overlap between image and OCS>",
      "JS_img_ocs":  "<float: Jensen-Shannon divergence image vs OCS>",
      "Conf_consist":"<float: consistency-as-confidence score>"
    }
  ],
  "ocs_derived_B": {
    "enabled": "<bool>",
    "aperture_photometry_params": { "...": "..." },
    "background_subtraction_params": { "...": "..." },
    "note": "image-derived OCS, common-mode failure 对照口径，禁止与口径 A 结论混用"
  }
}
```

`Conf_consist` 的口径（24 号 §10.3）：

```
Conf_consist = f(M_img, M_ocs, Overlap_k, -JS_img_ocs)
```

解释规则（24 号 §10.3，照搬作约束）：
- image 与 OCS 高一致 + 候选集中 → 高置信；
- image 高置信、OCS 低置信 → 检查 OCS 是否本身不可观测；
- OCS 高置信、image 低置信 → 检查图像退化 / 空间结构弱；
- image 与 OCS 高冲突 → 不强行输出姿态，标记低置信 / 模型失配；
- **image-derived OCS_B 与 image 高一致 → 必须额外检查是否 common-mode failure，不可直接判高置信**。

### 4.4 这就是 CLAUDE.md 钦定的"信息量与置信指标实现规范"

CLAUDE.md §5 把"v0.4 信息量与置信指标实现规范"列为代码实施前必须先冻结的下一步。本节 §4.2 范式决策 + §4.3 schema 回填，正是该规范应装的核心内容。建议作者在重写 13/14 号的同时（或之前），把这部分独立冻结为该规范，再进入 `06_v0.4_code/`。

### 4.5 结论与优先级

软肋 2 是三条里**唯一真正卡住推进**的：它既是论文核心贡献（consistency-as-confidence）的地基，又已在已冻结文档留下实际 schema 缺口。**必须最先做**：先拍板 A/B 范式 → 回填 schema → 冻结指标规范 → 才进代码。

---

## 五、软肋 3：科学新颖性升级（关系投稿层级）

### 5.1 问题

新主线最扎实的贡献是"建立同源前向模型 + observability / complementarity / confidence 分析框架"（24 号 §7 贡献点 1–2 为定义地基）。这对 Acta / ASR / Remote Sensing 一档够用，但作者目标是"尽量向上冲刺"（CLAUDE.md §1 最新确认）。问题在于：

- 贡献点 1–2 偏"定义 / 框架"，方法论性质；
- "observability 分析"在遥感 / 姿态估计领域已有成熟工具（FIM / CRLB 本就是经典）；
- 若新颖性被看成"已知工具的拼装"，难以支撑二类A（AST / TGRS）层级。

### 5.2 解决办法：新颖性锚在"组合 + 场景"，不锚在单指标

创新性不要求工具新，而要求**应用对象 + 组合 + 结论新**。用三段承重墙守住（纯写作，代码无关）：

1. **双通道同源可比**：纯光变曲线文献只有光度、纯成像位姿文献只有图像；同时 / 同源 / 可比地做 observability 分解的少。这是统一前向模型直接换来的、别人难复制的立论。
2. **consistency-as-confidence + 共模对照**：用 image-derived OCS（口径 B）证明"一致 ≠ 可信"。多数 fusion 论文不做这个对照——这既是诚实点，也是新意。
3. **observation-geometry 信息量地图 → observation planning**：落到"哪些 sun/view 几何最值得观测"，有明确工程价值。**此点正是作者的观测规划小项目的目的**，与主线咬合。

**关键提醒：不要把创新性押在"做出 CRLB"上。** 真正稳的升级是上述三点的组合；FIM/CRLB 跑通是给第 3 点加理论外衣，跑不通第 3 点用离散信息量指标照样成立。

---

## 六、FIM / CRLB 策略定位（软肋 3 的可选理论增强）

### 6.1 FIM 与 CRLB 是什么

**FIM（Fisher Information Matrix，费希尔信息矩阵）** 衡量观测数据中关于待估参数（姿态 q）含多少信息。直觉：姿态微变时观测量变化越大，观测对姿态越敏感，信息越多。

```
FIM(q) = E[ (∂s/∂q)ᵀ · Σ⁻¹ · (∂s/∂q) ]
```

`∂s/∂q` 为观测量对姿态的雅可比（敏感度），`Σ` 为观测噪声协方差。FIM 越大 = 信息越多 = 姿态越可估。

**CRLB（Cramér-Rao Lower Bound，克拉美-罗下界）** 是 FIM 的推论：任何无偏估计器对姿态的估计方差不可能低于 FIM 的逆：

```
Cov(q̂) ⪰ FIM(q)⁻¹
```

它给出"该观测条件下姿态最好能估到多准"的理论极限，与所用网络无关。吸引力：能把"OCS 在哪可观测、哪个几何信息量大"从经验图升级为**理论保证**（信息量地图 / 精度下界地图），审稿档次更高。

### 6.2 为什么 24 号要先降级——真实风险

FIM 要算 `∂s/∂q`，即观测量对姿态的梯度。作者前向模型里到处是不可微 / 非光滑：

- camera visibility（像素出现 / 消失是阶跃）；
- V_sun_macro shadow mask ∈ {0,1}（阴影边界是阶跃）；
- 边缘像素 fractional coverage（13 号 §6.5 直接舍掉）；
- GGX 镜面峰附近梯度极陡、数值不稳。

在这些地方做数值差分，`∂s/∂q` 会乱跳 → 不可信梯度 → 不可信 FIM → 不可信 CRLB。若一上来就把 CRLB 当硬理论主轴，审稿人一句"shadow boundary 不可微，你的 Fisher 信息怎么定义"即可击穿——比不用更糟。

### 6.3 降级—稳定—升级策略及最终效果评估

24 号 §10.1 的三段策略，逐段评估能走到哪：

**降级（起步，几乎必达）：** 不写 FIM/CRLB，改用离散网格稳健指标——pairwise signature distance、nearest-neighbor ambiguity、top-k confusion、posterior-like entropy。不需梯度，数值稳、无可微性争议。术语用 *Fisher-like local sensitivity / local observability score*，不碰 CRLB 强声明。
> 效果：稳拿，足以支撑 observability 主体论证。

**稳定（中间，验证可微性）：** 在 visibility / shadow mask / 边缘 / GGX 峰附近检验数值梯度是否稳定。可用 soft visibility / soft shadow 平滑替代，或局部多次差分看收敛。
> 效果：这是闸门。梯度稳 → 放行升级；不稳 → 停在降级档并诚实声明"局部不可微，采用离散稳健指标"。这一步本身即可写为方法贡献（认真处理了度量的数值合法性）。

**升级（目标，有条件）：** 仅当梯度被验证稳定，才把局部敏感度升级为正式 FIM，把 D-optimality / CRLB 作为 observation planning 理论判据。
> 效果：**不保证拿到。** 大概率只能在"几何光滑、无阴影遮挡、远离镜面峰"的姿态子集做到局部 FIM，阴影 / 自遮挡区做不到。

**最终现实效果（诚实判断）：**

```
降级档： 近 100% 拿到，撑起 observability 主体。           ← 投稿底线稳
稳定档： 做该做的可微性检验，本身是方法贡献。             ← 加分且防击穿
升级档： 大概率仅部分光滑姿态子集成立，作理论佐证而非主轴。 ← 锦上添花，拿到算赚
```

该策略真正价值不是"最终一定升到 CRLB"，而是**无论走到哪一档都站得住**：升不上去有稳健指标兜底，升得上去有理论加成。下有保底、上有空间，而非赌 CRLB 能成。

### 6.4 FIM/CRLB 成熟，还能算创新吗

能，但创新不在工具本身。可主张的新意：
1. 把 FIM/CRLB 用在"OCS 独立光度通道 vs 成像通道"的姿态可观测性对比（对象新）；
2. 用信息量地图驱动 observation planning（工程落点，= 作者小项目）；
3. consistency-as-confidence 置信判据（与 FIM/CRLB 无关的独立新意）。

即使 FIM/CRLB 跑通，也只是给第 1、2 点加理论外衣，不是孤立卖点。承重墙是 §5.2 的三点组合。

---

## 七、投稿定位（基于学位认定期刊分级目录 + 项目真实命中率）

依据：`文献/00投稿目标/` 三张截图（学位认定期刊分级目录，决定毕业成果认定），结合 24 号 §14 与"纯合成、无真实锚点"硬约束重排。

### 7.1 剔除不相关

- 别的学科：燃烧（Combustion and Flame）、等离子（PSST/PST）、多相流（IJMF/JFM）、推进（JPP）、非线性动力学（ND）——与项目无关。
- 一类综合 TOP（Nature/Science/子刊/NSR/Science Bulletin/PRL/Engineering）——增量性合成研究够不到。
- **Progress in Aerospace Sciences**：综述期刊，仅受邀综述，不收原创研究，排除。
- TAES / JGCD（二类A）：24 号判定项目不做 field-ready 估计系统 / GNC 算法，硬投易被"不是完整系统 / 算法"打回，不建议。

### 7.2 按项目真实命中率重排

```
┌─ 现实能冲到的最高档（主攻）
│   ★ Aerospace Science and Technology (AST) —— 二类A
│     二类A高档，且对纯合成的"物理建模+信息分析+航天应用"接受度高。
│     现实能命中的最高档，应作主攻目标。
│
├─ 冲刺档（可投，命中率受"无真实数据"拖累）
│   ◇ IEEE TGRS —— 二类A
│     遥感顶刊，强烈偏好真实观测；纯合成+DL可观测性是硬卖点，
│     无真实/半真实锚点风险大。
│   ◇ Optics Express —— 经二类B兜底（中科院二区）
│     框成"光学观测/BRDF前向建模+可观测性"则契合；OE 对姿态估计
│     本身兴趣较弱，中等契合。
│
├─ 稳健保底（大概率中，二类B，达标无忧）
│   ✓ Acta Astronautica —— 二类B
│   ✓ Advances in Space Research (ASR) —— 二类B
│
└─ 不建议作为目标
    ✗ TAES / JGCD（二类A）、一类全部、Progress in Aero Sci（综述）。
```

### 7.3 定位与软肋的咬合关系

决定落"二类A（AST/TGRS）"还是"二类B（Acta/ASR）"的，正是三条软肋的闭合质量：

- 软肋 2（consistency-as-confidence 框架）做扎实 → 够 AST；
- 再加软肋 3 第 3 点（FIM / observation-planning，即作者小项目）做出来 → 才有底气冲 TGRS；
- **FIM 升级档是 二类A→TGRS 的加分项，不是 AST 的入场券**。AST 用降级+稳定档即可。

### 7.4 两点硬提醒

1. **预警名单自查**：学位目录备注 2 明确"中科院《国际期刊预警名单》期间发表的不算紧密相关成果"。ASR、部分 MDPI 期刊历年有上观察 / 预警名单的情况（逐年变动）。**投稿前务必核对当年最新预警名单**，避免中了却不算数。
2. **claim 不得因冲高而膨胀**：CLAUDE.md §1 已定"以高水平期刊要求牵引问题定义 / 指标 / 图表 / 审稿防线，但不得扩大未经证据支撑的 claim"。冲 AST/TGRS 靠把信息分析做扎实，不靠扩大宣称。

---

## 八、执行优先级与下一步

```
软肋 2  →【最先做】block 代码，且已冻结 13/14 schema 有实际缺口需回填。
          先拍板 A/B 反演范式 → 回填 summary schema → 冻结"信息量与置信指标实现规范"。
软肋 1  →【顺带做】补一条红线 + 主线数据集上零成本 Δθ 敏感性实验（鲁棒性边界图）。
软肋 3  →【贯穿全程】Intro/Related Work 落实三段新颖性承重墙；FIM/CRLB 走降级-稳定-升级，
          以降级档保底、升级档锦上添花；observation-planning 与作者小项目咬合。
```

与 CLAUDE.md §5 既定下一步一致：先冻结"v0.4 信息量与置信指标实现规范"（= 软肋 2 的 §4.2+§4.3），再进 `06_v0.4_code/` phase 0 验证，不直接全量重跑或训练。

### 待作者拍板项

1. 反演范式：方案 A（网格分类，本文推荐主口径）还是 B（kNN likelihood）？本文建议 A 主 + B 对照。
2. 投稿定位：是否认可"主攻 AST、冲刺 TGRS、保底 Acta/ASR"？
3. 是否将本文 §2.3（L1 红线）、§4.2–§4.3（范式+schema）提交 Codex 审阅端，作为重写 13/14 号与新建指标规范的输入。

### 同步约束（重申）

本文为 97 目录候选稿。是否采纳、是否据此重写 13/14 号、是否同步 CLAUDE.md / 启动集 / 总控 / 归档索引，按工作区硬约束**只能由 Codex 审阅端在阶段通过后执行**。Claude 执行端不擅改定位主线、方法冻结文件与启动集。

---

## 九、一句话总结

> 24/25 新主线方向合理且必要（硬触发是 v0.3 口径污染，修辞绕不过）。但它引入三条需主动闭合的软肋：软肋 2（posterior 范式 + schema 回填）最紧迫、直接 block 代码，须最先做；软肋 1（L1 准静态假设）用红线 + Δθ 鲁棒性边界图把攻击点转为结果；软肋 3（新颖性）锚在"双通道同源可比 + consistency-as-confidence 共模对照 + observation-planning"三点组合，FIM/CRLB 走降级-稳定-升级、保底优先。投稿主攻 AST、冲刺 TGRS、保底 Acta/ASR，冲高靠信息分析做扎实而非扩大 claim。
