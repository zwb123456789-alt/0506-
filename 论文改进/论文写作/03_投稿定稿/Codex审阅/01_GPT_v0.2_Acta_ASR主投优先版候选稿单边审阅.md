# Codex 审阅：GPT v0.2 Acta/ASR 主投优先版候选稿

> 审阅日期：2026-06-05  
> 审阅对象：`03_投稿定稿/GPT交互/GPT输出/01_GPT输出_v0.2_Acta_ASR主投优先版.md`  
> 对照提示词：`03_投稿定稿/GPT交互/01_v0.2_Acta_ASR主投优先版_GPT提示词.md`  
> 阶段任务：`03_投稿定稿/01_v0.2_Acta_ASR主投优先版/00_本阶段任务说明.md`  
> 审阅结论：通过，可作为 v0.2 Acta/ASR 主投优先版的 GPT 侧候选底稿之一；等待 Claude 候选稿返回后再做最终整合，不直接写入 `manuscript_md/`。

## 1. 总体判定

GPT 候选稿基本完成提示词要求：

1. 以 v0.1 为底稿，重构了 Results 4.4/4.5，并新增 4.7。
2. 一次性整合了 07、07b、07c，而不是只接 07c。
3. 正确把 U1 机制写成 degradation-aware OCS-image co-utilization，而不是 OCS standalone fallback。
4. 明确保留 no real telescope validation、no operational robustness、no fully robust 的边界。
5. 正确区分主线 OCS-only 5.91 deg 与 12f 内部重训 OCS-only 6.58 deg。
6. 保留 Q12-Q14 作者事实占位，未代填 Data/Author/Funding/COI。

结论：GPT 输出可进入后续 GPT-vs-Claude 对比整合。

## 2. 结构审阅

GPT 候选稿采用以下结构：

```text
4.4 Clean-image fusion and modality dominance
4.5 Degradation-aware fusion and modality-isolation controls
4.6 Ablation and sensitivity analysis
4.7 Synthetic observation-style degradation and cross-geometry sanity tests
```

该结构与本阶段任务说明一致。尤其值得保留：

- 4.4 先保留 clean fusion 的 1.47 deg 优势，再引入 Experiment 12 的 modality dominance。
- 4.5 明确从 naive fusion 崩溃推进到 U1，再用 12b 控制说明 U1 不只是 image augmentation。
- 4.7 把 12c/12d/12f 作为主文压缩证据，并把 12g rare outliers 写入边界。
- Discussion 的 5.4 段能清楚区分 co-utilization 和 automatic fallback。

## 3. 数值与口径核查

主要数值与已审阅清单一致：

- ResNet image-only clean：1.69 +/- 0.07 deg，Hit@5 = 97.6%。
- ResNet + concat5 per_part_log clean：1.47 +/- 0.07 deg，Hit@5 = 99.7%，worst 9.9 -> 6.6 deg。
- Experiment 11 naive fusion noise sigma=0.01：约 73.36 deg。
- Experiment 12 branch masking：clean normal 1.57 deg，image-masked 52.84 deg，OCS-masked 18.14 deg；noise sigma=0.01 normal 75.08 deg，OCS-masked 88.88 deg。
- U1：clean 1.95 deg；noise sigma=0.10 为 2.31 deg；rare large outliers 保留。
- 12b image-only same augmentation：noise sigma=0.10 为 9.55 deg；U1 为 2.31 deg。
- 12b masking：noise sigma=0.10 下 image_train_mean 30.87 deg，ocs_train_mean 58.56 deg。
- 12c：read/background/starfield/combined_medium 下 U1 约 2 deg；combined_severe 为 13.88 deg。
- 12d：phase24 image-only 11.34 deg、fusion 6.85 deg；phase120 image-only 83.08 deg、fusion 79.71 deg。
- 12e：centered 2.88 deg vs original 1.69 deg。
- 12f：best beta 在噪声下为 0.0，12f 内部 OCS-only 为 6.58 deg。
- 12g：error >30 deg 为 42/49,950，占 0.084%。

需要后续整合时注意：

- GPT 候选稿中 total_log 36.69 deg、Hit@5 99.7%、all_raw 3.98 deg 等来自 v0.1，口径可保留，但最终整合时仍应以 v0.1 原文或结果表复核。
- `about 78 deg to 89 deg` 这类概括可用于叙事，但主文表格中建议列出 12c 代表档具体数值。

## 4. 红线审阅

GPT 候选稿未触碰以下红线：

- 未写 fusion automatically robust。
- 未写 U1 automatically switches to OCS。
- 未写 OCS standalone fallback。
- 未写 near-perfect / fully robust。
- 未写 real telescope validation。
- 未写 operational robustness / field-proven robustness。
- 未写 phase120 generalization is solved。
- 未把 12f best beta 写成 deployable automatic gating。

其中几处表述值得保留：

```text
not automatic OCS fallback
not automatic switching
controlled simulation benchmark
oracle late-fusion upper bound
phase120 is not solved
rare large outliers remain
```

## 5. 建议整合时修正

1. Related Work 仍有大量 `[CITATION: ...]` 与 `[to verify]`，最终 v0.2 不应直接保留过多裸占位；需要结合已核验 bibliography 处理。
2. Methods 目前是压缩版候选稿，缺少最终可复现细节表；整合时建议加一张 protocol table，列 split、target、metric、OCS standardization、12c linear degradation、12f beta direction。
3. 4.6 中 U2/U3/U4 负结果可保留，但主文篇幅可能过重；若 Claude 候选稿更精简，可把 U2/U3/U4 下放 Supplementary。
4. 12e 和 12g 在 GPT 稿中已经进入 4.3/4.7 和 Limitations；最终整合时建议主文只保留一句加 limitation，完整表放 Supplementary。
5. Abstract 稍长，后续可压缩，但目前作为候选稿可接受。

## 6. 当前阶段状态

GPT 侧候选稿已收到并通过 Codex 单边审阅。下一步：

```text
等待 Claude 输出：
03_投稿定稿/Claude交互/Claude输出/01_Claude输出_v0.2_Acta_ASR主投优先版.md
```

Claude 输出返回后，Codex 再做 Claude 单边审阅、GPT-vs-Claude 对比，并最终生成：

```text
03_投稿定稿/manuscript_md/主稿_v0.2_Acta_ASR主投优先版.md
```
