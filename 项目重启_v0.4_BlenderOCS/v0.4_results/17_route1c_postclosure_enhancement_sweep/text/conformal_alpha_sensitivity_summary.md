# R126 子任务 E：Conformal α 敏感性摘要

最后更新：2026-07-01  

数据来源：`v0.4_results/13_l1d3_confidence_pdb/conformal/l1d3_conformal_summary.csv`（既有输出已含 α=0.05/0.10/0.20，本轮不新训练，仅复算重组）。

**严格口径：以下为 split-conformal 在当前 simulated split 上的工程覆盖与 set size；coverage≈target 只说明该 split 校准自洽，不是 Bayesian posterior，也不是最终概率校准。**

## 1. clean P-INT best：coverage / set_size(°) vs α（neural 三通道）

| channel | geom | α=0.05 cov/ss | α=0.10 cov/ss | α=0.20 cov/ss |
|:--|:--|:--|:--|:--|
| neural/ocs_only | G1 | 0.976/352.0 | 0.899/321.8 | 0.774/252.1 |
| neural/ocs_only | G3 | 0.939/322.9 | 0.912/245.7 | 0.818/161.1 |
| neural/ocs_only | G5 | 0.960/207.6 | 0.902/126.2 | 0.801/56.2 |
| neural/image_only | G1 | 0.953/14.6 | 0.892/10.0 | 0.838/8.3 |
| neural/image_only | G3 | 0.936/27.0 | 0.865/21.0 | 0.774/14.7 |
| neural/image_only | G5 | 0.943/47.7 | 0.835/32.3 | 0.777/24.8 |
| neural/joint | G1 | 0.960/12.2 | 0.912/9.2 | 0.794/6.6 |
| neural/joint | G3 | 0.956/12.4 | 0.922/10.0 | 0.862/6.9 |
| neural/joint | G5 | 0.939/14.5 | 0.902/12.9 | 0.811/10.3 |

## 2. clean P-INT：P-DB neg-L2 coverage / set_size(°) vs α

| geom | α=0.05 cov/ss | α=0.10 cov/ss | α=0.20 cov/ss |
|:--|:--|:--|:--|
| G1 | 0.976/350.0 | 0.909/340.0 | 0.818/320.0 |
| G3 | 0.973/350.0 | 0.895/320.0 | 0.818/50.0 |
| G5 | 0.963/200.0 | 0.929/10.0 | 0.878/0.0 |

## 3. 走势观察

```text
- α 增大（目标覆盖降低）→ set_size 单调收窄，符合 split-conformal 预期。
- 固定 α，set_size 随几何 G1->G3->G5 收紧（多观测光度向量信息量增加）。
- neural ocs_only coverage 在 α=0.10 附近接近 target；image_only clean 系统性略欠覆盖
  （与 R119/R123 结论一致，写作时保留 image_only 欠覆盖）。
- degraded mild/moderate 附表见 conformal_alpha_metrics.csv，趋势一致但整体 set_size 更大。
```
