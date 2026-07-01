# 76_1C-E43_C3正式结果证据包与claim边界_Claude执行报告

执行端：Claude  
任务编号：1C-E43  
执行日期：2026-06-26  
协议：R76 放行，Option B-min

---

## 0. 任务状态

```text
1C-E43：COMPLETED
C3 formal 5-fold result：STABLE NEGATIVE RESULT
本报告只整理证据，不运行训练，不改代码，不写论文正文
```

---

## 1. C3 per-fold 数值

### 1.1 C3 image_only（6-layer CNN, raw 4-dim manifest OCS 不参与）

| Fold | test_n | yaw_acc | pitch_acc | yaw_cmae | within_3 |
|------|--------|---------|-----------|----------|----------|
| 0 (test: 0-70°) | 555 | 0.00% | 21.80% | 104.5° | 20% |
| 1 (test: 75-145°) | 555 | 0.00% | 15.68% | 72.1° | 14% |
| 2 (test: 150-215°) | 518 | 0.00% | 15.83% | 107.9° | 11% |
| 3 (test: 220-285°) | 518 | 0.00% | 24.52% | 73.4° | 20% |
| 4 (test: 290-355°) | 518 | 0.00% | 28.19% | 49.3° | 21% |

Aggregate：**yaw_acc = 0.00%**（5/5 folds），pitch_acc = 21.20%，yaw_cmae = 81.44°

### 1.2 C3 joint（image + raw 4-dim manifest OCS, early fusion）

| Fold | test_n | yaw_acc | pitch_acc | yaw_cmae | within_3 |
|------|--------|---------|-----------|----------|----------|
| 0 | 555 | 0.00% | 27.03% | 100.8° | 20% |
| 1 | 555 | 0.00% | 13.87% | 75.8° | 14% |
| 2 | 518 | 0.00% | 18.15% | 95.2° | 16% |
| 3 | 518 | 0.00% | 13.51% | 88.5° | 18% |
| 4 | 518 | 0.00% | 24.52% | 46.7° | 21% |

Aggregate：**yaw_acc = 0.00%**（5/5 folds），pitch_acc = 19.42%，yaw_cmae = 81.39°

### 1.3 协议一致性确认

| 参数 | image_only | joint |
|------|-----------|-------|
| Manifest | circ_yawblock_fold0-4 | 同 |
| Epochs | 20 | 20 |
| LR | 0.001 | 0.001 |
| Seed | 42 | 42 |
| Batch size | 32 | 32 |
| Optimizer | Adam | Adam |
| Params | 3,865,613 | 3,913,229 |
| Overlap | strict (5/5) | strict (5/5) |
| Val-max | 0 | 0 |

---

## 2. C2 / C3 对照表

| 维度 | C2 enhanced OCS-only | C3 image_only | C3 joint |
|------|---------------------|---------------|----------|
| 数据源 | enhanced_ocs_features.npz | manifest JSONL PNG | manifest JSONL PNG + 4-dim raw OCS |
| OCS 特征 | 1-13 dim（ratios, logs, densities, pixel frac） | 无（纯图像） | 4-dim raw（ocs_total, ocs_jinshuzhuti, ocs_taiyangnengban, ocs_yinshenban） |
| 模型 | MLP_3layer | 6-layer CNN | CNN + MLP encoder early fusion |
| Config 数 | 13 | 1（固定架构） | 1（固定架构） |
| Folds | 5 | 5 | 5 |
| mean yaw_acc | 0.00%（全部 configs） | 0.00% | 0.00% |
| mean pitch_acc | 2.56–4.37% | 21.20% | 19.42% |
| mean yaw_cmae | 80–120° | 81.44° | 81.39° |
| 状态 | R62 通过 | R76 通过 | R76 通过 |

**关键区分**：

```text
C2 enhanced OCS  ≠  C3 joint 中的 raw 4-dim OCS。
C2 使用预注册增强特征（ratios/logs/densities/pixel fracs 等衍生量）；
C3 joint 的 OCS 编码器接收的是 manifest 中直接记录的 4 维原始积分 OCS 值。
二者不可写成同一 OCS-only 结果链，必须在论文 Table/Figure/Methods 中分开标注。
```

---

## 3. 诊断 Warning 解释

所有 10 个训练均出现 `primary val_loss significantly larger than train_loss — possible overfit` warning。该 warning 的含义：

```text
- 模型在训练集上拟合良好（train_loss 持续下降），但 cross-yaw 验证集损失远高于训练损失。
- 这与跨 yaw 泛化失败一致：模型学到了训练 yaw 区间的特征-标签映射，
  但该映射在测试 yaw 区间不成立。
- 这不是传统"过拟合到噪声"的信号，而是"跨 yaw 域偏移"的预期表现。
- 不得将其解释为模型容量不足、需要更多训练或需要超参搜索的证据。
```

---

## 4. Claim 边界

### 4.1 可写

```text
1. 在 C3 正式固定协议（Option B-min, fixed CNN, early fusion joint, 20 epochs,
   circular yaw-block holdout）下，image_only 与 joint 均未取得 exact-bin yaw 跨块泛化：
   10/10 folds yaw_acc = 0.00%。

2. Joint early fusion（image + raw 4-dim OCS）未改善 exact-bin yaw accuracy 超越 image_only：
   两组 aggregate yaw_acc 均为 0.00%。

3. Pitch accuracy 在 image_only（21.20%）和 joint（19.42%）上显著高于
   C2 OCS-only 的 pitch range（2.56–4.37%），但 pitch 仅作为二级诊断，
   不改变 yaw-based null result。

4. C2 enhanced OCS-only、C3 image_only、C3 joint 三线在 cross-yaw exact-bin
   泛化上均返回 null result。该一致性不依赖任何特定特征工程或后验修正。

5. 当前结果约束于 phase63 fixed-roll、circular yaw-block split、
   固定协议参数范围内；报告的是 controlled negative result。
```

### 4.2 不可写

```text
1. "图像通道不含姿态信息"或"图像模型在所有任务下都失败"。
2. "OCS 没有任何价值"或"joint 融合被证明无增益"。
3. "C3 负结果证明真实卫星姿态反演不可行"。
4. "C2 enhanced OCS 与 C3 raw 4-dim joint OCS 是同一 OCS-only 结果链"。
5. "C3 负结果可以外推到 GEO 真实数据、三轴姿态、暗室实验或其他模型架构"。
6. "该结果否定了 OCS+图像互补性假设"——只否定当前固定协议下 exact-bin yaw 互补。
7. "E25 image_only 即 C3 image_only"——E25 为 E21 上下文产物，非 C3 正式 baseline。
```

### 4.3 诊断措辞边界

```text
- "possible overfit" warning → "train/val loss separation consistent with cross-yaw domain shift"
- pitch_acc 较高 → "pitch is a secondary diagnostic; does not alter yaw-based negative verdict"
- random split 中 yaw_acc 65-70% → "within-distribution yaw learning is confirmed;
  cross-yaw generalization is the specific failure mode, not an incapacity to learn yaw"
```

---

## 5. 后续 Results 表格/图表建议

### 5.1 建议表格

**Table 4**：C3 formal 5-fold per-fold results（image_only + joint）

- 列：fold, test yaw range, n, yaw_acc, pitch_acc, yaw_cmae, within-3 rate
- 分两组：image_only 和 joint

**Table 5**：C2/C3 cross-channel comparison

- 列：channel, OCS input spec, model, n_configs, mean yaw_acc, mean pitch_acc, mean yaw_cmae
- 行：C2 enhanced OCS-only, C3 image_only, C3 joint

### 5.2 建议图表

**Figure 5**：C2/C3 three-channel yaw_acc bar chart（全 0，需在 caption 中解释 null 含义）

**Figure 6**：C2 vs C3 pitch_acc scatter（显示 OCS-only 低、image/joint 高但均为二级指标）

---

## 6. 红线确认

| 红线 | 状态 |
|------|------|
| 不运行训练 | ✅ |
| 不运行 raw 4-dim ocs_only / --mode all | ✅ |
| 不修改代码、数据、split、模型或结果 JSON | ✅ |
| 不把 C3 null 外推到所有模型/GEO/三轴 | ✅ |
| 不写论文正文正式段落 | ✅ |
| 报告简短，不复述 C1/C2 全历史 | ✅ |
| C2 enhanced OCS 与 C3 raw 4-dim OCS 已明确区分 | ✅ |

---

**执行端签名**：Claude  
**下一步**：交 Codex 审阅 E43 证据包，决定是否进入 `01_成果区/`
