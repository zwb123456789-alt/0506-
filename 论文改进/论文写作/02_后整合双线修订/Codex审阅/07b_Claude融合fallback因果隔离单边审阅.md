# Codex 审阅：07b Claude 融合 fallback 因果隔离

> 审阅日期：2026-06-04  
> 审阅对象：`Claude交互/Claude输出/07b_Claude输出_融合fallback因果隔离.md`  
> 代码：`论文改进/补充实验/代码/run_fusion_fallback_isolation_12b.py`  
> 结果目录：`论文改进/补充实验/结果/fusion_fallback_isolation_12b/run_20260604_150333/`  
> 审阅结论：通过，可进入 v0.2 审慎整合；机制表述必须降调为 OCS-image co-utilization，不得写成 OCS standalone fallback。

## 1. 总体结论

Claude 的 07b 输出完成了任务说明要求的 12b-1 至 12b-5 五组对照，且代码与结果目录能够支撑主要数值。Codex 审阅后认为：

1. 12b 可以作为正文/补充材料的新增证据进入 v0.2。
2. U1 的强鲁棒性不能仅由 image-only same augmentation 解释。
3. OCS 在 U1 augmented fusion 中是活跃输入，OCS 遮蔽和 OCS 噪声都会显著劣化结果。
4. 12b 不支持“OCS standalone fallback”或“图像失效后自动切换到 OCS”的强说法。
5. 正确机制应写成：退化感知训练让融合模型形成 OCS-image co-utilization 的鲁棒联合表示；OCS 提供 active joint constraint，但不是独立 fallback predictor。
6. rare large outliers 仍然存在，必须保留在 Limitations 或 Supplementary 中；不得写 near-perfect / fully robust。

## 2. 代码与实验条件审阅

已核查脚本关键路径与逻辑：

- 数据：phase63 exact BRDF 图像，log1p，128x128。
- OCS：concat5 per_part 30D，log10 + zscore，仅用 train 统计量拟合。
- Split：`split_coarse_to_fine(..., coarse_step=10.0)`，run.log 显示 train_pool=703，tr=563，val=140，test=1998。
- Target encoding：复用 `rf.encode_target`，即 `[sin(yaw), cos(yaw), sin(pitch), cos(pitch)]`。
- 指标：复用 `rf.compute_metrics`，主误差为 great-circle angular error，Hit@5/Hit@10 口径未漂移。
- Seeds：0-4，共 5 seeds。
- U1 训练：复用实验 12 的 `RobustFusionModel` 与 `AUG_DEGS`，`augment=True, p_drop_image=0, p_drop_ocs=0`。
- Image-only same augmentation：ResNet image-only 使用同一 `AUG_DEGS` 与同一 clean validation early stopping 逻辑。
- Held-out degradation：`noise_0.03`, `noise_0.05`, `blur_k3`, `blur_k5`, `downsample_64`, `downsample_32`，未进入训练增强。

需要降调的技术口径：

- 12b-2 的 `image_zero` / `ocs_zero` 是特征层遮蔽或 train-mean 替换，不是重新训练/评估真正的单模态模型。因此可证明 U1 联合表示依赖 OCS 或图像分支，但不能把遮蔽结果直接解释成某一单模态的真实独立性能。
- 12b-3 的 OCS 噪声是 raw per_part feature relative perturbation 后用 train log-zscore 统计量重新标准化；它可作为 U1 fusion head 对 OCS 输入扰动敏感性的因果测试，但不能和实验 6 的 OCS-only 端到端噪声鲁棒性直接等同。
- 结果目录未保存模型权重，只保存 CSV/JSON/log/summary。由于脚本、seeds 和配置完整，审阅不将其列为阻断项；如后续要做图或 case study，可考虑补存 state_dict。

## 3. 结果核验

### 3.1 Image-only same augmentation 是否足以解释 U1 成功

不够。

关键结果：

| 条件 | image-only+aug | U1 aug fusion | 判读 |
|---|---:|---:|---|
| clean | 2.63 deg | 1.95 deg | U1 更优 |
| noise 0.01 | 2.80 deg | 1.95 deg | U1 更优 |
| noise 0.10 | 9.55 deg | 2.31 deg | U1 明显更优 |
| bright 0.50 | 2.76 deg | 1.98 deg | U1 更优 |
| bright 1.50 | 2.76 deg | 2.00 deg | U1 更优 |

结论：图像退化增强是 U1 成功的重要原因，但不是充分解释。U1 相对 image-only+aug 的增益，尤其 noise 0.10 下 9.55 deg vs 2.31 deg，支持 OCS 或融合结构提供额外约束。

### 3.2 U1 是否在图像退化时真正使用 OCS

支持“使用 OCS”，但不支持“单独回退到 OCS”。

关键结果：

| 条件 | normal | image_train_mean | ocs_train_mean |
|---|---:|---:|---:|
| clean | 1.95 deg | 30.87 deg | 56.48 deg |
| noise 0.01 | 1.95 deg | 30.87 deg | 56.45 deg |
| noise 0.10 | 2.31 deg | 30.87 deg | 58.56 deg |

判读：

- 遮蔽 OCS 后性能大幅劣化，说明 OCS 在 U1 中不是装饰输入。
- 遮蔽图像后仍为约 30-35 deg，远高于 OCS-only 5.91 deg，说明 U1 没有学成 dedicated OCS-only fallback。
- `ocs_train_mean` 比 `image_train_mean` 更差可写成“U1 joint representation 对 OCS 特征更敏感”，但不能写成“OCS 单模态强于图像单模态”。

### 3.3 OCS 噪声/双退化是否支持 OCS active fallback

支持 active OCS involvement，不支持 strict active fallback。

关键结果：

| 图像条件 | OCS 0% | OCS 20% | 增量 |
|---|---:|---:|---:|
| clean | 1.95 deg | 5.36 deg | +3.41 deg |
| noise 0.01 | 1.95 deg | 5.37 deg | +3.42 deg |
| noise 0.10 | 2.31 deg | 5.95 deg | +3.64 deg |

判读：

- OCS 噪声单调拉低 U1 性能，说明 OCS 是因果活跃输入。
- OCS 噪声效应在 clean 和 image-degraded 条件下幅度接近，说明 OCS 不是在图像退化时才被触发，而是持续参与联合预测。
- 因此论文中应避免 “when images fail, the model switches to OCS” 的写法。

### 3.4 Rare large outliers 是否影响论文表述

会影响，必须保留限制。

结果：

- 总评估数：49,950。
- error > 30 deg：42 条，0.084%。
- error > 60 deg：40 条，0.080%。
- error > 90 deg：35 条，0.070%。
- 4 个 seed-sample 对跨退化重复离群。
- 离群样本 50% 位于 |pitch| > 75 deg。

判读：mean、p90 和 Hit@5 可以写为稳定，但 worst-case 和极区离群不能隐藏。主稿可写 rare large outliers concentrated near polar attitudes；不得写 fully robust 或 near-perfect。

### 3.5 未见退化泛化是否只是 matched augmentation robustness

不是严格的 matched augmentation robustness，但仍限于合成退化。

关键结果：

| 未见退化 | U1 aug fusion | image-only+aug |
|---|---:|---:|
| noise 0.03 | 1.99 deg | 4.25 deg |
| noise 0.05 | 2.06 deg | 6.43 deg |
| blur k3 | 1.96 deg | 2.84 deg |
| blur k5 | 2.00 deg | 4.12 deg |
| downsample 64 | 1.96 deg | 3.06 deg |
| downsample 32 | 2.01 deg | 4.93 deg |

判读：U1 对未训练的 noise/blur/downsample 退化保持约 2 deg，说明其鲁棒性超出了训练中完全匹配的 noise 0.01/noise 0.10/brightness 档。但这些仍是合成退化，不可写成真实望远镜泛化已验证。

## 4. 可进入 v0.2 的表述

建议写：

```text
The 12b controls show that image-degradation augmentation alone is insufficient to explain the U1 fusion robustness. Under the same online augmentation, the image-only ResNet degrades to 9.55 deg under noise sigma=0.10, whereas U1 fusion remains at 2.31 deg. Branch masking and OCS perturbation further show that OCS is an active component of the augmented fusion representation. However, the mechanism is not a standalone OCS fallback: masking the image branch still yields about 30-35 deg error, far from the dedicated OCS-only baseline of 5.91 deg. The evidence therefore supports degradation-aware OCS-image co-utilization rather than automatic modality switching.
```

中文整合口径：

```text
实验12b表明，U1 的鲁棒性不能由图像分支的同增强训练完全解释；OCS 在 U1 的联合表示中确实处于活跃状态。但 U1 并未学成图像失效时自动切换到 OCS-only 的独立 fallback，而是形成了依赖两分支共同存在的 OCS-image co-utilization。论文应写成“退化感知融合可利用 OCS 作为活跃联合约束”，而不是“OCS 自动托底”。
```

## 5. 禁止写入 v0.2 的表述

不得写：

- U1 proves OCS fallback.
- U1 learns an OCS-standalone fallback predictor.
- The model automatically switches to OCS when images fail.
- Image masking yields OCS-only performance.
- Fusion is automatically robust.
- Fully robust / near-perfect robustness.
- 12b validates real-world telescope performance.

## 6. v0.2 整合建议

1. Results 新增一个小节或补充表：`Degradation-aware fusion and modality-isolation controls`。
2. 主文保留 12b-1 与 12b-5 的压缩表，证明 U1 优于 image-only same augmentation 且对未见合成退化更稳。
3. 12b-2 与 12b-3 可放主文机制段或 Supplementary，但主文必须点明 OCS active co-utilization。
4. 12b-4 离群审计建议放 Supplementary，Discussion / Limitations 中引用其结论。
5. v0.2 可解除“12b 结果回来前不进入主稿修订”的冻结，进入审慎主稿整合；但 OCS fallback 论述必须采用降调版本。

## 7. 阶段判定

后整合 Step 07b 完成，Codex 审阅通过。下一步可进入 v0.2 主稿修订与图表/表格整合，但不覆盖 v0.1，建议新建：

```text
论文写作/03_投稿定稿/manuscript_md/主稿_v0.2_作者确认后修订稿.md
```

Q12-Q14 作者事实仍不由 Codex/GPT/Claude 代填。
