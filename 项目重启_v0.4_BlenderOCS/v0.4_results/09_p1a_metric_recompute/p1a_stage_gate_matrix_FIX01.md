# P1-A 阶段门判断矩阵（FIX01 更新版）

最后更新：2026-06-29
依据：R100 Codex 审阅

## 0. 阶段门裁决（FIX01 后）

```text
✅ P1-A 第一阶段（含分层）只读指标重算已完成。
⚠️ P1-A 指标重构有限价值，分层后发现强 fold/yaw-block 异质性。
❌ 不支持进入 P1-A 第二阶段（训练侧改进）。
🔍 建议：P1-A 作为论文指标重构 + 异质性诊断材料，不进入训练侧改进。
```

## 1. FIX01 新增分层发现

### 1.1 Yaw-block 分层（最重要新发现）

每个 fold 的 test 集是一段连续 yaw 弧段（circular yaw-block）。分层后发现**强烈异质性**：

| Channel | Fold | Test Yaw Block | Circular MAE | Within-6 | Coarse45 |
|---|---|---|---|---|---|
| C2 | 0 | [0,70°] | 15.12 | 13.3% | 13.3% |
| C2 | 1 | [75,145°] | 16.46 | 16.0% | 16.8% |
| C2 | 2 | [150,215°] | **23.58** | **0.0%** | **0.0%** |
| C2 | 3 | [220,285°] | **7.50** | **42.9%** | **28.6%** |
| C2 | 4 | [290,355°] | **26.59** | 8.1% | **0.0%** |
| C3_img | 0 | [0,70°] | 20.89 | 31.5% | 31.5% |
| C3_img | 1 | [75,145°] | 14.43 | 18.9% | 14.1% |
| C3_img | 2 | [150,215°] | 21.57 | 16.4% | 20.7% |
| C3_img | 3 | [220,285°] | 14.69 | 26.1% | 23.6% |
| C3_img | 4 | [290,355°] | 9.86 | 34.9% | **0.0%** |
| C3_joint | 0 | [0,70°] | 20.16 | 34.2% | 34.2% |
| C3_joint | 1 | [75,145°] | 15.15 | 18.0% | 13.7% |
| C3_joint | 2 | [150,215°] | 19.03 | 17.6% | 19.5% |
| C3_joint | 3 | [220,285°] | 17.71 | 27.2% | 23.4% |
| C3_joint | 4 | [290,355°] | 9.34 | 35.5% | **0.0%** |

**关键发现**：
1. **C2 异质性极强**：fold3 [220,285°] circular MAE 仅 7.5 bins（within-6=42.9%），但 fold2/fold4 退化到 23-27 bins（差于 random 18）。说明 OCS 在某些 yaw 弧段几乎可用、在另一些完全失败。
2. **C3 异质性较弱但仍明显**：MAE 在 9.3-21.6 bins 间波动。
3. **Coarse45 在某些 block 为 0.0%**：C2 fold2/fold4、C3 fold4 的 coarse45 = 0，说明这些 yaw 弧段连 45° 粗粒度都完全错。
4. **异质性来源**：test yaw block 离最近 train yaw 的"角度间隙"和该弧段 OCS 签名的局部可分性共同决定。这与 P0 的 OCS 签名重叠诊断一致——某些弧段恰好靠近可区分的 OCS 区域。

### 1.2 Pitch 分层

| Channel | Pitch Band | N | Circular MAE | Within-6 | Coarse45 |
|---|---|---|---|---|---|
| C2 | negative(≤-30°) | 936 | 18.61 | 15.5% | 12.0% |
| C2 | near_zero(-25..25°) | 792 | 18.72 | 14.4% | 10.9% |
| C2 | positive(≥30°) | 936 | **16.20** | **17.9%** | 12.5% |
| C3_img | negative(≤-30°) | 936 | 16.15 | 28.1% | 19.0% |
| C3_img | near_zero(-25..25°) | 792 | 16.07 | 26.1% | 18.4% |
| C3_img | positive(≥30°) | 936 | 16.72 | 22.5% | 16.9% |
| C3_joint | negative(≤-30°) | 936 | 16.15 | 29.1% | 18.5% |
| C3_joint | near_zero(-25..25°) | 792 | 16.14 | 24.7% | 18.3% |
| C3_joint | positive(≥30°) | 936 | 16.63 | 25.4% | 18.2% |

**关键发现**：
1. **C2 在 positive pitch（≥30°）略优**：circular MAE=16.20 vs negative/near_zero(~18.6-18.7)。可能高 pitch 下太阳能板朝向变化使 OCS 略可分。
2. **C3 pitch 间较均匀**：MAE 在 16.1-16.7 间，pitch 不是 C3 的主导分层因素。
3. **pitch 异质性远小于 yaw-block 异质性**：yaw-block MAE 跨度 7.5-26.6（差 19 bins），pitch MAE 跨度仅 16.1-18.7（差 2.6 bins）。

## 2. Baseline 修正（R100 3.3）

| Metric | 修正前 (Monte Carlo) | 修正后 (理论值) | 差异 |
|---|---|---|---|
| Circular MAE (bins) | 18.0528 | **18.0** | 0.05 |

理论推导：72-bin circular distance d 取值 0-36，d=1..35 各出现 2 次、d=0 和 d=36 各 1 次，期望 = Σ(d·count)/72 = **18.0**。

后续材料统一使用理论值 18.0。差异不改变任何结论。

## 3. Pooled vs Per-fold 聚合口径（R100 3.4）

| Channel | Pooled MAE | Per-fold mean MAE | 差异 |
|---|---|---|---|
| C2_baseline_4dim | 17.79 | 17.85 | -0.06 |
| C3_image_only | 16.33 | 16.29 | +0.04 |
| C3_joint | 16.32 | 16.28 | +0.04 |

**说明**：
- 主表先前用 **per-fold unweighted mean ± fold std**。
- FIX01 新增 **pooled sample-level weighted metrics**（`p1a_channel_pooled_metrics.csv`）。
- 两者差异 < 0.1 bins（fold 样本数 555/555/518/518/518 接近），不改变结论。

## 4. 对 R99 Q5 的更新回答

### Q5. 错误是否集中在特定 yaw block、pitch 或 fold？（FIX01 已回答）

**答：是，错误高度集中在特定 yaw block，pitch 影响较小。**

1. **Yaw-block 是主导异质性来源**：
   - C2 best block (fold3, [220,285°]): MAE=7.5, within-6=42.9%
   - C2 worst block (fold4, [290,355°]): MAE=26.6, within-6=8.1%, coarse45=0%
   - 跨 block MAE 跨度达 19 bins。

2. **某些 block coarse45=0**：C2 fold2/fold4、C3 fold4 连 45° 粗粒度都完全错。

3. **Pitch 影响小**：C2 positive pitch 略优，但跨 pitch MAE 跨度仅 2.6 bins。

4. **诊断意义**：这证明 yaw-block 外推失败不是均匀的——它取决于 test 弧段相对 train 弧段的位置和该弧段 OCS 的局部可分性。这强化了 P0 的"输入签名重叠 + 协议性外推鸿沟"叙事，而非"yaw 物理普遍不可观测"。

## 5. 阶段门最终判断（FIX01 后）

| 后续路径 | 是否支持 | 理由 |
|---|---|---|
| a. 论文指标重构 + 异质性诊断材料 | ✅ 支持 | 分层揭示 yaw-block 强异质性，丰富 extrapolation gap 叙事 |
| b. logits/checkpoint 只读导出 | ⚠️ 条件支持 | 若需 soft prediction 分析可申请，但当前 argmax 分层已足够诊断 |
| c. 训练侧 continuous/circular head | ❌ 不支持 | 整体 circular MAE 仅优 random 1-2 bins，异质性说明问题在输入/协议非判据 |
| d. 停止 P1-A | ✅ 建议采纳 | P1-A 已完成论文材料 + 异质性诊断，训练侧改进边际收益低 |

## 6. claim 边界（R100 3.5 收窄版）

```text
✅ 可写：
- exact-bin 0% 是 yaw-block 外推严格负结果（哨兵指标）。
- C3 image-based 输出在 circular/within-k/coarse45 指标上弱优于 C2 OCS-only，
  提示图像通道在当前模型输出中保留了更多可用姿态线索。
- yaw-block 外推失败高度异质，集中在特定 yaw 弧段。
- image_only 与 joint 无差异，early concat 无可用互补增益。

❌ 不得写：
- 图像通道信息量已被强证明（未做 embedding/logit/输入信息量分析）。
- 模型外推已成功。
- joint fusion 实现互补。
- yaw 物理普遍不可观测。
- V0.3 与 V0.4 可直接横比。
```

## 7. 关联文件

```text
R100_Codex_审阅_1C-B4_P1-A初版合规但需FIX01分层与baseline修正.md
v0.4_results/09_p1a_metric_recompute/p1a_channel_pooled_metrics.csv
v0.4_results/09_p1a_metric_recompute/p1a_pitch_stratified_metrics.csv
v0.4_results/09_p1a_metric_recompute/p1a_yaw_block_stratified_metrics.csv
v0.4_results/09_p1a_metric_recompute/p1a_baseline_corrected.md
```
