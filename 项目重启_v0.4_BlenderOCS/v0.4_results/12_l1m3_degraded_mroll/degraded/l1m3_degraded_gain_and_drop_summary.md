# L1M3 degraded 真实性轴：增益与退化 drop 汇总（R116 子任务 B）

最后更新：2026-07-01  

口径：yaw circular MAE（°）与 hit@30。clean 引用 R115（`11_l1m2`），
degraded 为本轮 `12_l1m3_degraded_mroll` 新跑。

## best 口径

### OCS-only 多几何增益（各退化等级下 G1→G3→G5 yaw cMAE）

| 退化等级 | G1 | G3 | G5 | G5相对G1增益 | 来源 |
|:--|--:|--:|--:|--:|:--|
| clean | 76.56 | 38.22 | 22.77 | 53.79 | R115 11_l1m2 |
| degraded-mild | 76.78 | 40.15 | 27.83 | 48.95 | 12_l1m3 |
| degraded-moderate | 78.48 | 51.72 | 38.46 | 40.02 | 12_l1m3 |

### image_only / joint 退化 drop（clean→degraded，yaw hit@30）

| geom | mode | clean hit@30 | mild hit@30 | moderate hit@30 |
|:--|:--|--:|--:|--:|
| G1 | image_only | 1.000 | 1.000 | 1.000 |
| G1 | joint | 1.000 | 1.000 | 1.000 |
| G5 | image_only | 0.993 | 1.000 | 1.000 |
| G5 | joint | 1.000 | 1.000 | 1.000 |

## final 口径

### OCS-only 多几何增益（各退化等级下 G1→G3→G5 yaw cMAE）

| 退化等级 | G1 | G3 | G5 | G5相对G1增益 | 来源 |
|:--|--:|--:|--:|--:|:--|
| clean | 78.31 | 38.56 | 22.77 | 55.54 | R115 11_l1m2 |
| degraded-mild | 78.25 | 40.76 | 27.83 | 50.42 | 12_l1m3 |
| degraded-moderate | 80.36 | 53.09 | 40.62 | 39.74 | 12_l1m3 |

### image_only / joint 退化 drop（clean→degraded，yaw hit@30）

| geom | mode | clean hit@30 | mild hit@30 | moderate hit@30 |
|:--|:--|--:|--:|--:|
| G1 | image_only | 0.963 | 1.000 | 1.000 |
| G1 | joint | 1.000 | 1.000 | 1.000 |
| G5 | image_only | 0.997 | 1.000 | 1.000 |
| G5 | joint | 1.000 | 1.000 | 0.189 |

