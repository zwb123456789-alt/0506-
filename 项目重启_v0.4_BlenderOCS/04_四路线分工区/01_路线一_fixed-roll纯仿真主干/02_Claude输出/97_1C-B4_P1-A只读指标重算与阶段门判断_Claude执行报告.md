# 97_1C-B4 P1-A只读指标重算与阶段门判断 Claude 执行报告

最后更新：2026-06-29
执行端：Claude
性质：头B-B4/P1-A 只读指标重算（第一阶段），不是训练、不是模型改进、不是外推补救成功。
依据：R99 Codex 裁决
输出目录：`v0.4_results/09_p1a_metric_recompute/`

## 0. 执行摘要

```text
R99 放行 P1-A 第一阶段只读指标重算。本轮任务：
1. 读取既有 C2/C3 per-sample predictions (argmax bin)
2. 重算 circular MAE、within-k、coarse45/coarse90、random baseline
3. 按 channel 聚合统计，生成阶段门判断矩阵

核心发现：
- Exact-bin 0% 严格负结果确认
- Circular MAE：C3 略优于 random 1-2 bins（9-10%），C2 与 random 无差异
- Within-6 bins：C3=25-27%，高于 random（18%）约 7-8%
- Coarse45：C3=18%，高于 random（12.5%）约 5-6%
- Coarse90：C2/C3 均与 random（25%）无实质差异
- C3 相比 C2 一致提升 6-10%，但 image_only 与 joint 无差异

结论：P1-A 结果支持作为论文指标重构材料，不支持训练侧改进。
```

## 1. 输入文件确认

### 1.1 可用文件

| 配置 | 文件模式 | Folds | 总样本 | 包含字段 |
|---|---|---|---|---|
| C2 baseline_4dim | `c2_baseline_4dim_fold{0-4}_samples.npz` | 5 | 2664 | record_id, yaw_pred_bin, yaw_true_bin, pitch_pred/true |
| C3 image_only | `c3_image_only_fold{0-4}_samples.npz` | 5 | 2664 | record_id, yaw_pred_bin, yaw_true_bin, pitch_pred/true |
| C3 joint | `c3_joint_fold{0-4}_samples.npz` | 5 | 2664 | record_id, yaw_pred_bin, yaw_true_bin, pitch_pred/true |

**位置**：`v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c2_samples/` 和 `c3_samples/`

### 1.2 缺失项

```text
❌ logits / probabilities：现有 samples.npz 只包含 argmax 预测的 bin，不包含 softmax 或 logit 输出。
   → 无法计算 soft circular expected yaw、top-k circular alternatives、entropy。
   → 按 R99 要求，本轮只记录缺口，不加载 checkpoint 做 forward。

❌ split manifest yaw block 标签：现有 samples.npz 只有 record_id，未标注属于哪个 train/test yaw block。
   → 无法按 yaw block 分层诊断（例如"某些 test block 错误率更高"）。
   → 需后续只读脚本读取 split manifest 并标注。

❌ pitch 分层统计：当前聚合跨所有 pitch，未按 pitch 范围分组。
   → 可从 record_id 解析 pitch，需后续扩展。
```

本轮基于已有 argmax bin 预测完成可做部分。

---

## 2. P1-A 指标定义

### 2.1 Circular 指标

**Circular error (bins)**：考虑 yaw 0-71 bins 的循环性质，计算最短角度距离。

```python
circular_error = min(|pred - true|, 72 - |pred - true|)
```

- **Circular MAE (bins)**：循环误差的平均值
- **Circular Median AE (bins)**：循环误差的中位数

**转换到角度**：1 bin = 5°，因此 circular MAE = 17.85 bins ≈ 89.25°

### 2.2 Within-k 指标

**Within-k bins**：预测在真值 ±k bins 循环邻域内的比例。

- Within-1 bin = 预测误差 ≤ 5°
- Within-2 bins = 预测误差 ≤ 10°
- Within-3 bins = 预测误差 ≤ 15°
- Within-6 bins = 预测误差 ≤ 30°

### 2.3 Coarse-bin 指标

将 72 个 5° bins 粗化为更大的 bin，计算粗粒度分类准确率。

| Coarse 名称 | Bin Width | 粗化后类别数 | 角度粒度 |
|---|---|---|---|
| coarse15 | 3 bins | 24 类 | 15° |
| coarse30 | 6 bins | 12 类 | 30° |
| coarse45 | 9 bins | 8 类 | 45° |
| coarse60 | 12 bins | 6 类 | 60° |
| coarse90 | 18 bins | 4 类 | 90° |

### 2.4 Random Baseline

**随机预测基线（理论值）**：

- Exact-bin (72 类)：1/72 = 1.39%
- Within-k bins：(2k+1)/72
  - Within-1：3/72 = 4.17%
  - Within-6：13/72 = 18.06%
- Coarse-bin：1/n_coarse_classes
  - Coarse45 (8 类)：1/8 = 12.5%
  - Coarse90 (4 类)：1/4 = 25.0%
- Circular MAE：约 18.05 bins（Monte Carlo 模拟）

---

## 3. P1-A 核心结果

### 3.1 跨 Fold 聚合统计

| Channel | N Samples | Exact-bin | Circular MAE (bins) | Within-6 bins | Coarse45 | Coarse90 |
|---|---|---|---|---|---|---|
| C2_baseline_4dim | 2664 | **0.00%** | 17.85 ± 7.51 | 16.1% ± 16.2% | 11.7% ± 12.1% | 24.0% ± 16.9% |
| C3_image_only | 2664 | **0.00%** | 16.29 ± 4.91 | 25.6% ± 7.9% | 18.0% ± 11.8% | 25.1% ± 15.6% |
| C3_joint | 2664 | **0.00%** | 16.28 ± 4.30 | 26.5% ± 8.6% | 18.2% ± 12.6% | 24.6% ± 14.9% |
| **Random baseline** | — | 1.39% | 18.05 | 18.1% | 12.5% | 25.0% |

**关键观察**：

1. **Exact-bin 0%**：C2/C3 均严格为 0，确认 yaw-block + exact-bin 72 类协议下外推完全失败。
2. **Circular MAE**：C3 略优于 random 1.76-1.77 bins（~9%），C2 仅优 0.2 bins（~1%）。
3. **Within-6 bins**：C3 (25-27%) 高于 random (18%) 约 7-8%，C2 (16%) 低于 random。
4. **Coarse45**：C3 (18%) 高于 random (12.5%) 约 5-6%，C2 (11.7%) 低于 random。
5. **Coarse90**：C2/C3 均与 random (25%) 无实质差异（-1% 至 +0.1%）。

### 3.2 C2 vs C3 对比

| 指标 | C2 → C3_img 提升 | C2 → C3_joint 提升 | 解释 |
|---|---|---|---|
| Circular MAE | -1.56 bins (-8.7%) | -1.57 bins (-8.8%) | C3 略优 |
| Within-6 bins | **+9.5%** | **+10.4%** | C3 显著优于 C2 |
| Coarse45 | **+6.3%** | **+6.4%** | C3 显著优于 C2 |
| Coarse90 | +1.0% | +0.6% | 提升消失 |

**结论**：
- C3 图像通道相比 C2 OCS-only 在 circular MAE、within-6、coarse45 均有一致提升（6-10%）。
- 这确认**图像通道携带更多姿态信息**，但在当前架构+协议下仍无法实现有效外推。
- C2 OCS-only 在多数指标上接近或低于 random，再次确认 OCS 4D 签名在 yaw-block 下几乎无区分能力。

### 3.3 C3 image_only vs joint

| 指标 | C3_image | C3_joint | 差异 |
|---|---|---|---|
| Circular MAE | 16.29 bins | 16.28 bins | **-0.01 bins** |
| Within-6 bins | 25.6% | 26.5% | **+0.9%** |
| Coarse45 | 18.0% | 18.2% | **+0.2%** |

**结论**：
- Image_only 与 joint 几乎无差异（MAE 差 0.01 bins，within-6 差 0.9%）。
- 再次确认 **early concat fusion 无互补增益**，与 P0-3 的 confusion 诊断一致。

---

## 4. 详细指标展开

### 4.1 Within-k Curve（所有 k=0-36）

| k (bins) | C2 | C3_img | C3_joint | Random | C3 vs Random |
|---|---|---|---|---|---|
| 0 (exact) | 0.0% | 0.0% | 0.0% | 1.4% | -1.4% |
| 1 (5°) | 3.6% | 6.6% | 6.7% | 4.2% | +2.4-2.5% |
| 2 (10°) | 5.7% | 12.3% | 13.0% | 6.9% | +5.4-6.1% |
| 3 (15°) | 8.2% | 17.1% | 17.7% | 9.7% | +7.4-8.0% |
| 6 (30°) | 16.1% | 25.6% | 26.5% | 18.1% | +7.5-8.4% |
| 12 (60°) | 32.8% | 45.3% | 46.2% | 34.7% | +10.6-11.5% |
| 18 (90°) | 50.2% | 62.5% | 63.1% | 51.4% | +11.1-11.7% |

**规律**：
- C3 在所有 k≥1 均高于 random 2-12%，k 越大提升越明显（但绝对值仍不高）。
- C2 在 k≤6 低于 random，k≥12 才略高于 random。
- Within-k curve 斜率：C3 > random > C2，说明 C3 预测集中度略优于 random，C2 更分散。

完整 within-k curve 保存在 `p1a_within_k_curve.csv`。

### 4.2 Coarse-bin Metrics（5 档粗化）

| Coarse Name | 角度粒度 | 类别数 | Random | C2 | C3_img | C3_joint |
|---|---|---|---|---|---|---|
| coarse15 | 15° | 24 类 | 4.2% | 1.4% | 3.3% | 4.2% |
| coarse30 | 30° | 12 类 | 8.3% | 7.0% | 10.5% | 11.4% |
| coarse45 | 45° | 8 类 | 12.5% | 11.7% | 18.0% | 18.2% |
| coarse60 | 60° | 6 类 | 16.7% | 20.2% | 19.1% | 19.9% |
| coarse90 | 90° | 4 类 | 25.0% | 24.0% | 25.1% | 24.6% |

**规律**：
- **Coarse45 是 C3 相对最优粒度**：C3=18% vs random=12.5%，提升约 5-6%。
- **Coarse15/30 C3 接近或低于 random**：说明 15-30° 粒度外推仍困难。
- **Coarse90 退化到 random**：C2/C3 均与 random 无差异，说明 90° 粗粒度已无信息。
- C2 在 coarse60 异常高（20.2%），但 std 极大（26.9%），不稳定，可能是某些 fold 偶然集中预测。

完整 coarse 统计保存在 `p1a_coarse_bin_metrics.csv`。

### 4.3 Circular Error Distribution（0-36 bins）

Circular error 分布直方图显示：

- **C2 baseline_4dim**：误差高度分散，峰值在 18-36 bins（90-180°），接近均匀分布。
- **C3 image_only / joint**：误差略集中在 10-25 bins（50-125°），但仍很平坦，未显示明显单峰。
- **Random baseline**：理论上应接近均匀分布（0-36 bins 等概率）。

完整分布保存在 `p1a_circular_error_distribution.csv`，可后续可视化。

---

## 5. 对 R99 必答问题的回答

### Q1. exact-bin 0% 下，circular MAE / median AE 是否仍明显优于 random？

**答：不明显优于 random。**

- C2: circular MAE = 17.85 bins，random = 18.05 bins，**仅优 0.2 bins (1.1%)**
- C3_img: circular MAE = 16.29 bins，random = 18.05 bins，**优 1.76 bins (9.7%)**
- C3_joint: circular MAE = 16.28 bins，random = 18.05 bins，**优 1.77 bins (9.8%)**

结论：C3 相比 random 有约 10% 的边际改善，但绝对误差仍高达 16-17 bins（80-85°），不能读成"外推成功"。C2 与 random 几乎无差异。

### Q2. within-1/2/3/6 bins 是否高于 chance/random baseline？

**答：C3 在 within-1/2/3 略高于 random，within-6 高约 7-8%。**

C3 在 within-1/2/3/6 均高于 random 5-8%，显示精细角度区分能力略优于随机。但绝对值仍低（within-3 仅 17-18%，within-6 仅 25-27%），不能读成"精确外推已实现"。

### Q3. coarse45/coarse90 是否稳定高于 chance/random baseline？

**答：coarse45 C3 高于 random 约 5-6%，coarse90 与 random 无实质差异。**

- Coarse45：C3=18% vs random=12.5%，提升 5.5-5.7%
- Coarse90：C2/C3 均与 random=25% 无差异（-1% 至 +0.1%）

结论：coarse45 C3 略优于 random，但 coarse90 已退化到 random 水平。这支持 R82/E45B 的"粗粒度外推存在弱信号、细粒度外推失败"叙事，但不支持"粗粒度外推成功"。

### Q4. C3 image_only 与 joint 相比 C2 OCS-only 是否有任何一致提升？

**答：C3 相比 C2 有一致但有限的提升。**

C3 相比 C2 在 circular MAE、within-6、coarse45 均有一致提升（6-10%），但在 coarse90 提升消失。这说明**图像通道相比 OCS 确实携带更多姿态信息**，但在当前架构+协议下仍无法实现有效外推。

Image_only 与 joint 几乎无差异，再次确认 **early concat fusion 无互补增益**。

### Q5. 错误是否集中在特定 yaw block、pitch 或 fold？

**答：当前只读指标重算未按 yaw block 或 pitch 分层，暂无法回答此问题。**

缺口：
- 现有 samples.npz 只有 record_id、pred_bin、true_bin，未包含 split manifest 的 yaw block 标签。
- 未按 pitch 分层统计。
- 若需分层诊断，需后续只读脚本：读取 split manifest → 标注 train/test yaw block → 按 block/pitch 重算指标。

可后续申请 D 类只读扩展，但不阻塞当前 P1-A 第一阶段闭口。

### Q6. P1-A 结果是否足以支持后续第二阶段？

**判断矩阵：**

| 后续路径选项 | 是否支持 | 理由 |
|---|---|---|
| a. 仅作为论文指标重构材料 | ✅ 支持 | C3 略优于 random，coarse45 C3=18% vs random=12.5%，可承接 R82/E45B 的 extrapolation gap 叙事 |
| b. 申请 logits/checkpoint 只读导出 | ⚠️ 条件支持 | 若需分析 soft prediction、expected yaw、top-k alternatives，可申请 logits 导出；但当前 argmax 指标已足够诊断 |
| c. 申请真正训练侧 continuous/circular head | ❌ 不支持 | Circular MAE 仅优 random 1-2 bins，改判据不太可能根本改变外推失败；P0 诊断已指向输入签名重叠和 yaw-block 协议本身 |
| d. 停止 P1-A，不再补救 | ✅ 建议采纳 | P1-A 指标重构完成论文叙事所需材料，训练侧改进边际收益低，不建议继续 |

---

## 6. 阶段门判断

### 6.1 P1-A 第一阶段裁决

```text
✅ 接收 P1-A 第一阶段结果为论文指标重构材料。
❌ 不支持进入 P1-A 第二阶段（训练侧 continuous/circular head）。
⚠️ 条件允许后续 D 类只读扩展（yaw block 分层、logits 导出），但不阻塞主链。
```

### 6.2 支持的论文叙事

P1-A 结果支持以下论文叙事：

```text
✅ exact-bin 0% 是 yaw-block 外推的严格负结果（哨兵指标）。
✅ circular MAE、within-k、coarse45 略优于 random，显示弱外推信号。
✅ C3 相比 C2 一致提升 6-10%，图像通道携带更多姿态信息。
✅ image_only 与 joint 无差异，early concat 无互补增益。
✅ coarse90 退化到 random，粗粒度外推有界。
✅ 当前负结果来自 protocol-defined yaw extrapolation gap，不是模型/特征完全失败。
```

### 6.3 不支持的论文叙事

P1-A 结果不支持以下论文叙事：

```text
❌ 模型外推问题已解决。
❌ circular/coarse 指标显示"成功外推"。
❌ joint fusion 实现互补。
❌ 改判据后 yaw-block 外推可行。
❌ V0.3 与 V0.4 可以直接横向比较。
```

### 6.4 为什么不建议 P1-A 第二阶段（训练侧改进）

```text
1. Circular MAE 仅优 random 1-2 bins（~10%），绝对误差仍 16-17 bins（80-85°）。
   改判据（exact-bin → circular regression）不太可能根本改变外推失败。

2. P0 诊断已指向根本原因：
   - OCS 签名重叠（cosine distance = 0.0076）
   - Yaw-block 协议下 test yaw 从未在 train 中出现
   - 输入可辨识性不足，改判据不改变输入

3. 训练侧改进成本高、收益低：
   - 需修改 loss、output head、重新训练 5-fold
   - 即使 circular MAE 降到 14-15 bins，仍是巨大误差（70-75°）
   - 不改变论文主叙事（外推仍失败），只改变指标呈现形式

4. P1-A 已完成论文所需材料：
   - Circular/coarse 指标支持 R82/E45B 的 extrapolation gap 叙事
   - C2/C3 对比支持图像通道信息量判断
   - 进一步改进边际价值低
```

---

## 7. 未触碰声明

```text
✅ 未训练模型
✅ 未新渲染
✅ 未推理生成新预测（只读取已有 samples.npz）
✅ 未改 split / 模型 / loss / 超参 / seed
✅ 未覆盖 R04 负结果链
✅ 未改论文正文
✅ 未改 CLAUDE.md
✅ 未触发头A/头B大合并裁决
✅ 未写入成果区
✅ 未启动 P1-B
✅ 未启动 P2
✅ 未加载 checkpoint 做 forward（按 R99 要求，logits 缺失只记录缺口）

只做了：
- 读取既有 C2/C3 samples.npz（argmax predictions）
- numpy/pandas 计算 circular、within-k、coarse 指标
- 随机基线理论计算与 Monte Carlo 模拟
- 保存 csv/md 表格到诊断区
- 编写阶段门判断矩阵
```

---

## 8. 产出文件清单

### 8.1 报告
- `97_1C-B4_P1-A只读指标重算与阶段门判断_Claude执行报告.md`（本文件）

### 8.2 脚本
- `v0.4_results/09_p1a_metric_recompute/p1a_metric_recompute.py`

### 8.3 表格产物

| 文件 | 内容 | 大小/行数 |
|---|---|---|
| `p1a_channel_fold_metrics.csv` | Per-fold per-channel 指标（15 行） | 15 行 |
| `p1a_channel_aggregated_stats.csv` | 跨 fold 聚合统计（3 行） | 3 行 |
| `p1a_coarse_bin_metrics.csv` | 5 档粗化指标（5 行） | 5 行 |
| `p1a_circular_error_distribution.csv` | Circular error 分布（0-36 bins） | 37 行 |
| `p1a_within_k_curve.csv` | Within-k curve（k=0-36） | 37 行 |
| `p1a_random_baseline.json` | Random baseline 数值 | JSON |
| `p1a_random_baseline.md` | Random baseline 表格 | Markdown |
| `p1a_metric_recompute_summary.md` | 汇总摘要 | Markdown |
| `p1a_stage_gate_matrix.md` | 阶段门判断矩阵 | Markdown |

所有产物位于：`v0.4_results/09_p1a_metric_recompute/`

---

## 9. 给 Codex/作者的待确认问题

```text
Q1. P1-A 第一阶段是否闭口？
   本轮已完成只读指标重算、random baseline、阶段门矩阵。
   是否接收 P1-A 第一阶段闭口？

Q2. 是否同意不进入 P1-A 第二阶段（训练侧改进）？
   基于 circular MAE 仅优 random 1-2 bins、P0 诊断指向输入签名重叠、
   训练侧改进成本高收益低，建议不进入第二阶段。
   是否同意此判断？

Q3. 是否需要后续 D 类只读扩展？
   - Yaw block 分层诊断（需读取 split manifest 标注 train/test block）
   - Logits/probabilities 导出（需加载 checkpoint forward）
   - Pitch 分层统计
   若需要，可另设阶段门；若不需要，P1-A 就此闭口。

Q4. P1-A 产物是否需同步到成果区？
   当前所有产出在 v0.4_results/09_p1a_metric_recompute/（诊断区）。
   是否作为头B材料同步到成果区？

Q5. 下一步是否进入头A/头B大合并裁决？
   当前头A已由 R90 闭口，头B-B3/P0 已闭口，P1-A 第一阶段已完成。
   是否可触发头A/头B大合并裁决，或继续暂缓？
```

---

## 10. 关联文件

```text
R99_Codex_裁决_1C-B3闭口后放行P1-A只读指标重算.md
R98_Codex_审阅_1C-B3-FIX02通过_P0只读诊断闭口.md
96_1C-B3-FIX02_P0只读诊断图表与口径修正_Claude执行报告.md
v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c2_samples/
v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_samples/
v0.4_results/09_p1a_metric_recompute/ （所有产物）
```
