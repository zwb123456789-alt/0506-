# 07b 阶段整合清单：融合 fallback 因果隔离与鲁棒性补强

> 生成日期：2026-06-04  
> 阶段状态：完成  
> Claude 输出：`Claude交互/Claude输出/07b_Claude输出_融合fallback因果隔离.md`  
> Codex 审阅：`Codex审阅/07b_Claude融合fallback因果隔离单边审阅.md`  
> 代码：`论文改进/补充实验/代码/run_fusion_fallback_isolation_12b.py`  
> 结果目录：`论文改进/补充实验/结果/fusion_fallback_isolation_12b/run_20260604_150333/`

## 1. 采用结论

实验 12b 可纳入 v0.2。它补齐了实验 12 的关键因果隔离：

- image-only same augmentation 不能完全解释 U1 的鲁棒性。
- OCS 在 U1 augmented fusion 中是活跃输入。
- U1 不具备 OCS standalone fallback；遮蔽图像后仍远高于 OCS-only 5.91 deg。
- 更准确的机制是 OCS-image co-utilization，而不是图像失效后自动切换到 OCS。
- U1 的 mean/p90/Hit@5 很稳，但 rare large outliers 仍存在。

## 2. 必须进入 v0.2 的证据

### 12b-1：image-only same augmentation 对照

| 条件 | image-only+aug | U1 aug fusion | 可写结论 |
|---|---:|---:|---|
| clean | 2.63 deg | 1.95 deg | U1 更优 |
| noise 0.01 | 2.80 deg | 1.95 deg | U1 更优 |
| noise 0.10 | 9.55 deg | 2.31 deg | U1 明显优于同增强图像模型 |
| bright 0.50 | 2.76 deg | 1.98 deg | U1 更优 |
| bright 1.50 | 2.76 deg | 2.00 deg | U1 更优 |

整合口径：U1 的恢复不是 pure image augmentation effect。

### 12b-2：U1 分支遮蔽

| 条件 | normal | image_train_mean | ocs_train_mean |
|---|---:|---:|---:|
| clean | 1.95 deg | 30.87 deg | 56.48 deg |
| noise 0.01 | 1.95 deg | 30.87 deg | 56.45 deg |
| noise 0.10 | 2.31 deg | 30.87 deg | 58.56 deg |

整合口径：U1 joint representation 对 OCS 特征敏感，OCS 活跃；但分支遮蔽是特征层诊断，不能当作单模态性能。

### 12b-3：OCS 噪声与双退化

| 图像条件 | OCS 0% | OCS 20% |
|---|---:|---:|
| clean | 1.95 deg | 5.36 deg |
| noise 0.01 | 1.95 deg | 5.37 deg |
| noise 0.10 | 2.31 deg | 5.95 deg |

整合口径：OCS 噪声单调劣化 U1，支持 OCS active involvement；但效应不随图像退化明显触发，因此不写 switching fallback。

### 12b-4：离群审计

| 阈值 | 数量 | 比例 |
|---|---:|---:|
| error > 30 deg | 42 / 49,950 | 0.084% |
| error > 60 deg | 40 / 49,950 | 0.080% |
| error > 90 deg | 35 / 49,950 | 0.070% |

整合口径：mean/p90/Hit@5 stabilized, rare large outliers remain; outliers are concentrated near polar attitudes.

### 12b-5：未见退化泛化

| 未见退化 | U1 aug fusion | image-only+aug |
|---|---:|---:|
| noise 0.03 | 1.99 deg | 4.25 deg |
| noise 0.05 | 2.06 deg | 6.43 deg |
| blur k3 | 1.96 deg | 2.84 deg |
| blur k5 | 2.00 deg | 4.12 deg |
| downsample 64 | 1.96 deg | 3.06 deg |
| downsample 32 | 2.01 deg | 4.93 deg |

整合口径：U1 robustness extends beyond exactly matched training degradations within synthetic perturbations; still not real-observation validation.

## 3. 主稿写法边界

可写：

- Degradation-aware fusion outperforms image-only training under the same augmentation.
- OCS is an active component of the augmented fusion representation.
- U1 is robust across tested and held-out synthetic degradations in mean/p90/Hit@5.
- The mechanism is coupled OCS-image co-utilization.

不可写：

- OCS automatically fallback.
- OCS standalone fallback is proven.
- U1 switches to OCS when images fail.
- Fully robust / near-perfect robust.
- Real telescope robustness is validated.

## 4. 建议进入 v0.2 的位置

1. Results 中接在实验 12 后，新增 `Controls for degradation-aware fusion robustness`。
2. 表格建议：正文压缩表放 12b-1 与 12b-5；12b-2/12b-3 可作为机制表或补充表。
3. Discussion 新增一段：co-utilization vs fallback 的机制澄清。
4. Limitations 保留：rare outliers, feature-level masking limitation, synthetic degradation limitation, no real telescope validation。

## 5. 下一步

进入 v0.2 主稿修订。仍不覆盖 v0.1，建议新建：

```text
论文写作/03_投稿定稿/manuscript_md/主稿_v0.2_作者确认后修订稿.md
```

Q12-Q14 作者事实继续占位，不由 Codex/GPT/Claude 代填。
