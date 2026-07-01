# R118 子任务 C：neural vs P-DB 一致性 / 互补 / 置信排序关键结论

最后更新：2026-07-01  

**置信为工程分数（neural margin / P-DB retrieval margin），非真实 Bayesian posterior。correct 判据 = yaw circular error ≤ 30°。**

## 1. neural vs P-DB yaw error 相关性（test, best, G5）

| degrade_level | mode | neural cMAE | pdb cMAE | pearson | spearman |
|:--|:--|--:|--:|--:|--:|
| clean | ocs_only | 22.77 | 8.19 | 0.341 | 0.066 |
| clean | image_only | 8.57 | 8.19 | 0.008 | -0.085 |
| clean | joint | 3.20 | 8.19 | -0.082 | 0.013 |
| degraded-mild | ocs_only | 27.83 | 17.42 | 0.430 | 0.237 |
| degraded-mild | image_only | 3.50 | 17.42 | -0.067 | -0.055 |
| degraded-mild | joint | 1.88 | 17.42 | -0.011 | -0.060 |
| degraded-moderate | ocs_only | 38.46 | 34.71 | 0.417 | 0.326 |
| degraded-moderate | image_only | 2.71 | 34.71 | -0.040 | 0.003 |
| degraded-moderate | joint | 2.02 | 34.71 | -0.015 | 0.040 |

## 2. 互补四象限（test, best, G5, neural vs P-DB neg-L2）

| degrade_level | mode | both✓ | neural_only | pdb_only | both✗ | oracle_hit@30 |
|:--|:--|--:|--:|--:|--:|--:|
| clean | ocs_only | 237 | 3 | 44 | 12 | 0.960 |
| clean | image_only | 279 | 15 | 2 | 0 | 1.000 |
| clean | joint | 281 | 15 | 0 | 0 | 1.000 |
| degraded-mild | ocs_only | 214 | 11 | 50 | 21 | 0.929 |
| degraded-mild | image_only | 264 | 32 | 0 | 0 | 1.000 |
| degraded-mild | joint | 264 | 32 | 0 | 0 | 1.000 |
| degraded-moderate | ocs_only | 166 | 17 | 65 | 48 | 0.838 |
| degraded-moderate | image_only | 231 | 65 | 0 | 0 | 1.000 |
| degraded-moderate | joint | 231 | 65 | 0 | 0 | 1.000 |

## 3. 置信排序有效性（risk-coverage，test G5 ocs_only best, neural margin）

| coverage | yaw cMAE | yaw hit@30 |
|--:|--:|--:|
| 0.2 | 24.28 | 0.831 |
| 0.5 | 23.66 | 0.831 |
| 0.8 | 23.22 | 0.810 |
| 1.0 | 22.77 | 0.811 |

## 4. 读法与口径

```text
- 相关性/互补是同一 test split 上不同证据链的一致性分析，不是 joint 强互补性证明。
- oracle_hit@30（either_correct）是 neural∪P-DB 的上界，代表两条证据链的潜在互补空间，
  不代表可无监督地选中正确一方。
- risk-coverage：若 cMAE 随 coverage 降低而下降、hit@30 上升，说明该置信分数可用于选择性预测。
- 置信是工程分数，不是真实概率；不写成 Bayesian posterior 或真实观测不确定度。
```
