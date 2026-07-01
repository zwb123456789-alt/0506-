# 1C-E45B 指标重构与 extrapolation-gap 叙事说明 — Claude 执行报告

最后更新：2026-06-27
执行端：Claude
依据审阅：R81 Codex 审阅放行
性质：D 类只读指标重构与 framing 说明（不训练、不改代码、不改 split、不改模型）

## 0. 执行声明

本报告只读取 R77/R78/R80 已稳定成果、E45A JSON 指标文件和既有成果区材料，做指标重组、基线对照和叙事修正说明。未触发任何训练、代码修改、split 重设、模型/超参变更或论文正文正式改写。

## 1. 三通道指标重构表

### 1.1 C2/C3 三通道 yaw 指标 vs chance baseline

| 指标 | chance | C2 OCS-only (65-run mean) | C3 image_only (5-fold mean) | C3 joint (5-fold mean) | random split (分布内参考) |
|---|---:|---:|---:|---:|---:|
| exact-bin yaw_acc | 1/72 = 1.39% | **0.00%** | **0.00%** | **0.00%** | ≈ 65–70% |
| yaw CMAE (deg) | ≈ 90.0 | 96.97 | 81.44 | 81.39 | — |
| yaw within-3 bins | 7/72 = 9.72% | — (见注) | ≈ 17.1% | ≈ 17.7% | — |
| yaw within-6 bins | 13/72 = 18.06% | 18.89% | 25.57% | 26.51% | — |
| yaw coarse45 | 9/72 = 12.50% | 14.53% | 17.96% | 18.16% | — |

> 注：C2 within-3 在 R80 中未报告五折跨 config 均值。E45A JSON 中各 config/fold 的 within-3 中位数约 7–14%，跨 config 和 fold 波动极大，整体贴近 chance。此处不单独列为一个稳定点估计，避免给人"可靠近邻信号"的错觉。

### 1.2 三通道 pitch 指标对照

| 指标 | chance | C2 OCS-only (65-run mean) | C3 image_only (5-fold mean) | C3 joint (5-fold mean) |
|---|---:|---:|---:|---:|
| exact-bin pitch_acc | 1/37 = 2.70% | 3.03% | 21.20% | 19.42% |
| pitch within-3 bins | 7/37 = 18.92% | 17.75% | 56.07% | 51.77% |

### 1.3 关键解读

1. **exact-bin yaw = 0.00% 是三通道共同特征**，但这不等于"yaw 信息不存在"。random split 下约 65–70% 说明分布内 yaw 信息可被模型学习；问题出在 circular yaw-block 外推。

2. **yaw CMAE 三通道均在 81–97 deg 范围**，与 uniform random 期望 90 deg 接近或略差。C3 image_only/joint 的 81.4 deg 略优于 chance 90 deg，但差异不足以支撑"可靠跨弧段外推"。

3. **within-6 和 coarse45 仅在 C3 图像通道上有微弱超出 chance**（within-6: 25.6–26.5% vs chance 18.1%；coarse45: 18.0–18.2% vs chance 12.5%）。这些可写成"弱粗粒度残留信号"，但对应 C2 OCS-only 的 within-6 (18.9%) 和 coarse45 (14.5%) 已非常接近 chance。

4. **pitch 显著强于 yaw**：C3 image_only pitch exact 21.2%（chance 2.7%）、within-3 56.1%（chance 18.9%），可写成 fixed-roll 设定下 yaw/pitch 各向异性的定量证据。

5. **joint 相对于 image_only 无实质增益**：yaw 各指标几乎持平，pitch 反而略低（exact 19.4% vs 21.2%）。当前证据不支持"raw 4-dim OCS 对图像通道有实质互补增益"。

## 2. 叙事修正：从 exact-bin 0% 到 extrapolation gap

### 2.1 旧风险口径（应弃用）

```text
三通道 cross-yaw exact-bin yaw accuracy 全为 0.00%，
因此 fixed-protocol yaw 泛化为 null。
```

问题：exact-bin 0% 是 72-way softmax 分类头 + circular yaw-block holdout 协议 + strict 5 deg exact 命中判据三者共同决定的哨兵指标，不应被单独读作"yaw 信息不存在"或"物理不可观测"。

### 2.2 修正后口径（推荐）

```text
在 circular yaw-block holdout 外推设定下，三通道 exact-bin yaw accuracy 均为 0.00%。
该 0.00% 是 strict cross-yaw extrapolation + 72-bin exact 5 deg 命中判据下的稳定失败模式，
主要反映未见 yaw 弧段的外推失败（extrapolation gap），而非 yaw 信息完全不存在。

更有论文说服力的证据来自连续/近邻指标与随机基线的对照：
- yaw CMAE 三通道 81–97 deg，接近 uniform chance 90 deg；
- within-6 和 coarse45 仅在 C3 图像通道上有微弱超出 chance，C2 OCS-only 已贴近 chance；
- random split yaw_acc ≈ 65–70% 证明分布内 yaw 信息可被模型学习；
- E45A 的 holdout-prediction ratio = 0.0 确认预测系统性坍缩到训练可见 yaw 区间。

综合判断：当前 fixed-protocol 模型在未见 yaw 弧段上存在严重 extrapolation gap，
仅保留弱粗定位信号，无法形成可靠跨 yaw 弧段外推。
```

### 2.3 证据层级

```text
主叙事证据（承担论文核心论证）：
  yaw circular MAE、within-k、coarse-bin 与 chance/random baseline 的对照

辅助哨兵指标（说明严格分类命中失败，不单独承载物理 claim）：
  exact-bin yaw accuracy = 0.00%

机制解释证据（定位失败模式）：
  E45A holdout-prediction ratio = 0.0（全部 75 npz / 39960 样本无一命中 holdout yaw 块）
```

## 3. 必须避免的措辞（红线）

```text
不可写 "yaw 信息不存在"
不可写 "OCS/image 物理不可观测 yaw"
不可写 "三通道均无法学习任何 yaw 信息"
不可把 exact-bin 0% 单独作为主图/主结论
不可用 E45A 证明 fusion 永久无价值
不可外推到真实 GEO、三轴姿态、暗室实验或所有模型
```

## 4. Figure/Table 调整建议

### 4.1 Figure 5（C2/C3 three-channel yaw_acc comparison）

当前 Figure 5（R78 体系内编号）为全 0 yaw_acc 对比图。建议：

```text
方案 A（推荐）：降级为 supplementary figure，compact 嵌入 SI。
方案 B：保留在正文但改为小尺寸 inset，配合 coarse/continuous 指标主图。
方案 C：直接移除，改为正文一句话 "exact-bin yaw accuracy was 0.00% across all three channels"。
```

Codex 后续审阅时应选择其一。

### 4.2 建议新增/替代的正文图表

| 优先级 | 类型 | 内容 | 数据来源 |
|---|---|---|---|
| P0（正文主图） | 分组柱状图 | yaw CMAE / within-6 / coarse45 三通道 vs chance baseline | E45A JSON + R80 摘要 |
| P0（正文主表） | 对照表 | 类似本报告 §1.1 的指标重构表，含 chance 列 | 本报告 |
| P1（正文候选） | 散点图 | yaw CMAE vs within-6，按通道着色，叠加 chance 参考线 | E45A JSON per-fold |
| P1（正文候选） | 分组柱状图 | pitch exact / within-3 三通道 vs chance（展示 yaw/pitch 各向异性） | E45A JSON + R77 |
| P2（SI） | Per-fold 详表 | C3 10 folds × 关键指标 | C3 per-fold JSON |
| P2（SI） | 小提琴/箱线图 | C2 65-run yaw CMAE 分布，按 config 分组 | C2 extended_metrics.json |

### 4.3 现有图表体系中需注意的事项

- Figure 2（circular yaw-block holdout strategy）：保留，是解释 extrapolation gap 的关键方法图。
- Figure 3（yaw CMAE vs within-3 scatter）：可在更新数据后保留为正文候选，需叠加 chance 参考线。
- Figure 4（pitch accuracy by config）：保留为二级诊断，可作为 yaw/pitch 各向异性证据。

## 5. 方法学说明草稿（供后续论文 Methods/Discussion 参考）

以下为草稿级文本，不是论文正文正式段落。仅供后续 Codex 审阅和作者改写参考。

---

**Extrapolation gap framing（草稿）**

> Under the fixed-roll, circular yaw-block holdout protocol, the test set comprises a contiguous block of yaw bins that are entirely absent from training. The 72-way softmax classification head is therefore evaluated on classes it has never observed during training. Exact-bin yaw accuracy, defined as the fraction of samples for which argmax(yaw_logits) equals the true yaw bin, is 0.00% across all three channels (C2 enhanced OCS-only, C3 image-only, C3 image+raw-OCS joint). This null result is a stable consequence of the strict cross-yaw extrapolation requirement combined with a 5° exact-match criterion, and should not be interpreted as evidence that yaw information is physically absent from the OCS or image channels.
>
> Two lines of evidence support an extrapolation-gap interpretation rather than a claim of unobservability. First, under a random train/test split (no yaw-block holdout), the same architectures achieve yaw exact-bin accuracy of approximately 65–70%, demonstrating that within-distribution yaw information is learnable. Second, continuous and near-hit metrics (circular MAE, within-k-bin rates, coarse-bin accuracy) under the circular yaw-block protocol remain close to chance baselines, with only weak coarse-localization residuals in the image-based channels, consistent with a model that fails to extrapolate across unseen yaw arcs rather than one that finds no yaw-related structure in the input.
>
> The E45A diagnostic further confirms this interpretation: across all 39,960 test samples (75 model-fold combinations), not a single predicted yaw bin falls inside the corresponding holdout yaw block, indicating systematic collapse of predictions into the training-visible yaw range.

---

## 6. 数据来源清单

| 数据 | 来源文件 |
|---|---|
| C3 image_only per-fold | `v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.json` (mode=image_only) |
| C3 joint per-fold | 同上 (mode=joint) |
| C2 65-run per-config/fold | `v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c2_extended_metrics.json` |
| C2/C3 稳定摘要 | `01_成果区/11_C2C3三通道负结果证据包_E43_R77通过.md` |
| C2/C3 Results 总材料包 | `01_成果区/12_C2C3_Results非正文总材料包_E44_R78通过.md` |
| E45A 归因诊断 | `01_成果区/13_E45A负结果归因诊断_R80通过.md` |
| R80 审阅 | `04_Codex审阅/R80_Codex_审阅_1C-E45A通过_负结果归因诊断稳定.md` |
| R81 审阅（本任务放行） | `04_Codex审阅/R81_Codex_审阅_主指标叙事地雷与E45B指标重构放行.md` |
| Random split 参考值 | R77 §5 |

## 7. 红线确认

```text
✅ 未训练
✅ 未改任何代码、split、模型、超参、seed
✅ 未写论文正文正式段落（§5 仅为草稿供后续参考）
✅ 未把结果写成 unobservability
✅ 未外推真实 GEO、三轴姿态、暗室实验或所有模型
✅ 未改成果区
✅ 输出位置：02_Claude输出/（非 04_Codex审阅/、非 01_成果区/）
```

## 8. 待 Codex 审阅事项

1. §1.1 指标重构表的结构和 chance baseline 是否准确。
2. §2.2 修正后口径的措辞是否满足论文发表要求。
3. §4 的 Figure/Table 调整建议是否合理（尤其是 Figure 5 的三个方案选择）。
4. §5 方法学草稿的 extrapolation gap framing 是否可作为后续论文 Discussion 的基础文本。
5. E45B 通过后，E45A/E45B 诊断资产如何分流进入 Results/SI 图表体系。
