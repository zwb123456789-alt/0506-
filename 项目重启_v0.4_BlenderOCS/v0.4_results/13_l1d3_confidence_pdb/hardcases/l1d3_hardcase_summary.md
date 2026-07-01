# R118 子任务 E：Hard-case 候选索引摘要

最后更新：2026-07-01  

**hard-case index 是后续 P-INT-hard / stronger degraded 的候选输入，不是阶段门放行。**

## 1. 各类 hard-case 计数（select=best，全 deg×geom）

| label | 计数 |
|:--|--:|
| ocs-hard | 121 |
| image-hard(image_only) | 2 |
| image-hard(joint) | 0 |
| disagreement-hard | 748 |
| ambiguous-flux | 148 |
| robust-easy | 351 |

## 2. 按退化等级分布（关键类，G5）

| degrade | ocs-hard | disagreement | ambiguous-flux | robust-easy |
|:--|--:|--:|--:|--:|
| clean | 28 | 47 | 20 | 79 |
| degraded-mild | 29 | 61 | 26 | 78 |
| degraded-moderate | 16 | 82 | 34 | 62 |

## 3. 定义与阈值（可审计）

```text
阈值均基于该 (deg,geom) 层 ocs_only 分布分位数，非直觉手挑：
  ocs-hard      : neural_yaw_err>P75 且 (pdb_margin<P25 或 pdb_nearest_distance>P75)
  image-hard    : image_only/joint neural_yaw_err>30°
  disagreement  : neural hit@30 与 pdb hit@30 不一致（一对一错）
  ambiguous-flux: pdb_cand_yaw_spread>P75 且 nearest_distance<P50（候选分散但都近）
  robust-easy   : neural_yaw_err≤15° 且 pdb_yaw_err≤15° 且 pdb_margin>P50（对照）
```
