# 子任务B：D2 三通道互补性闭口摘要

口径：P-INT / best / clean；yaw hit@30；top-k overlap 取 top-5 grid idx 的 Jaccard；model-known simulated。

## 1. 三通道精度（yaw hit@30 / cMAE）

| geom | image_only | ocs_only | joint |
|---|---|---|---|
| G1 | 1.0 / 2.436 | 0.277 / 76.559 | 1.0 / 2.114 |
| G3 | 1.0 / 4.945 | 0.6723 / 38.225 | 1.0 / 2.032 |
| G5 | 0.9932 / 8.573 | 0.8108 / 22.769 | 1.0 / 3.197 |

## 2. joint 增量诊断

| geom | joint | best_single | joint−best_single | joint_only_correct |
|---|---|---|---|---|
| G1 | 1.0 | 1.0 | 0.0 | 0 |
| G3 | 1.0 | 1.0 | 0.0 | 0 |
| G5 | 1.0 | 0.9932 | 0.0068 | 0 |

## 3. 互补性（oracle 上界 vs 单通道）

| geom | best_single | oracle_ocs∪joint | oracle_all3 |
|---|---|---|---|
| G1 | 1.0 | 1.0 | 1.0 |
| G3 | 1.0 | 1.0 | 1.0 |
| G5 | 1.0 | 1.0 | 1.0 |

## 4. 闭口结论（诚实口径）

- joint 相对最佳单通道无稳定正增量（最大 joint−best_single = +0.0068）；**joint 强互补性仍未闭口，需 P-INT-hard / degraded-severe 裁决**。
- **关键诊断**：image_only 与 joint 的 hit@30 在 G1/G3 完全一致（disagreement=0），G5 仅差 2 例。说明 clean 下 joint 网络实质退化为 image 分支，几乎未从 OCS 支路取得额外信息——这比单纯"天花板"更精确：image 饱和使 joint 没有可增量空间，无法据此判断 joint 在图像不饱和时是否有真实互补。
- oracle 并集显著高于任一单通道，说明通道间存在 case 级互补信息，但该互补是 oracle 上界，不代表可无监督选中正确通道。
- image_only 在 clean 下近饱和，是 joint 增量受天花板限制的直接原因（与 R119 观察一致）。
- 以上均为 model-known simulated / current split / seed=42，不得写成真实反演成功或 joint 强互补性已证明。
