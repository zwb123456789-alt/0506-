# R118 子任务 B：P-DB / template retrieval 正式评估关键结论

最后更新：2026-07-01  

**P-DB 是 model-known simulated template retrieval，不是真实反演系统；top-k 是候选姿态检索，不是 Bayesian posterior，也不是真实观测成功率。**

## 1. 多几何单调性（test, matched-degraded, neg-L2, top1 yaw hit@30）

| degrade_level | G1 | G3 | G5 |
|:--|--:|--:|--:|
| clean | 0.290 | 0.821 | 0.949 |
| degraded-mild | 0.270 | 0.774 | 0.892 |
| degraded-moderate | 0.230 | 0.625 | 0.780 |

## 2. 相似度对比（test G5 matched-degraded, top1 yaw cMAE° / hit@30）

| degrade_level | neg-L2 | cosine | zscore-neg-L2 |
|:--|:--|:--|:--|
| clean | 8.19 / 0.949 | 19.12 / 0.878 | 10.35 / 0.939 |
| degraded-mild | 17.42 / 0.892 | 30.29 / 0.814 | 16.89 / 0.895 |
| degraded-moderate | 34.71 / 0.780 | 52.57 / 0.665 | 33.11 / 0.794 |

## 3. top-k-best 上界（test G5 matched-degraded, neg-L2, yaw hit@30）

| degrade_level | top1 | top3 | top5 | top10 |
|:--|--:|--:|--:|--:|
| clean | 0.949 | 0.997 | 0.997 | 1.000 |
| degraded-mild | 0.892 | 0.973 | 0.990 | 0.997 |
| degraded-moderate | 0.780 | 0.922 | 0.956 | 0.973 |

## 4. clean-template 退化迁移探针（test G5, neg-L2, top1 yaw hit@30）

template=clean，query=degraded，检验退化观测检索 clean 模板的稳健性。

| degrade_level | matched-degraded | clean-template |
|:--|--:|--:|
| degraded-mild | 0.892 | 0.919 |
| degraded-moderate | 0.780 | 0.801 |

## 5. 严格口径与读法

```text
- template 只来自 train split，val/test 不进 template 库（无检索泄漏）。
- matched-degraded：template 与 query 同 degrade_level；clean-template：template clean、query degraded。
- zscore-neg-L2 的 z-score 参数仅在 train（template 域）上拟合。
- top1 是单候选检索误差；topk-best 是候选集合内 oracle 上界，不代表可无监督选中。
- 结论只能写为：多观测总光度向量在 model-known 模拟条件下含可检索 yaw 信息，
  且该信息随几何数增加、随退化优雅收缩；不得写成真实观测反演成功率。
```
