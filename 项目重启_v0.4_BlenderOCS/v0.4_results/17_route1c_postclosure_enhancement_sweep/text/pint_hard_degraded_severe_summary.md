# R126 子任务 C：P-INT-hard / degraded-severe 摘要

最后更新：2026-07-01  

本文件含 C1（hard-attitude subset 分区重算）与 C2（degraded-severe 训练）两部分。

**严格口径：model-known simulated；不得写成真实观测反演成功。**

## C1. clean P-INT hard-attitude subset（best-val，复算自 R119/R125 hardcase index）

| subset | n(joint) | ocs_only cMAE/hit30 | image_only cMAE/hit30 | joint cMAE/hit30 | pdb cMAE/hit30 |
|:--|--:|:--|:--|:--|:--|
| all | 379 | 45.031/0.5356 | 6.087/0.9947 | 2.665/1.0 | 30.0/0.7704 |
| robust-easy | 117 | 6.734/1.0 | 7.975/0.9915 | 3.052/1.0 | 1.239/1.0 |
| ambiguous-flux | 20 | 39.931/0.7 | 9.266/1.0 | 2.937/1.0 | 25.75/0.85 |
| ocs-hard | 48 | 83.973/0.125 | 6.312/1.0 | 3.042/1.0 | 56.146/0.625 |
| image-hard | 2 | 15.842/1.0 | 31.087/0.0 | 0.974/1.0 | 0.0/1.0 |
| disagreement-hard | 223 | 63.145/0.3004 | 4.924/1.0 | 2.43/1.0 | 36.906/0.6996 |

### C1 观察：joint 相对最佳单通道（clean, hit@30）

```text
  all                 : joint hit@30=1.000  best_single=0.995  Δ=+0.005
  robust-easy         : joint hit@30=1.000  best_single=1.000  Δ=+0.000
  ambiguous-flux      : joint hit@30=1.000  best_single=1.000  Δ=+0.000
  ocs-hard            : joint hit@30=1.000  best_single=1.000  Δ=+0.000
  image-hard          : joint hit@30=1.000  best_single=1.000  Δ=+0.000
  disagreement-hard   : joint hit@30=1.000  best_single=1.000  Δ=+0.000

  读法：Δ>0 表示 joint 在该 hard 子集相对最佳单通道有可见增量；
        clean image_only 近饱和的子集里 joint 增量通常受天花板限制。
```

（C2 degraded-severe 部分见下方，由 degraded-severe 汇总脚本追加。）


---

## C2. degraded-severe 三通道（P-INT, best-val, seed42）

severe 预注册参数：blur σ=2.0px, downsample x4, bg 0.05+grad 0.04, Poisson peak 150, read 0.03, flux err 12%（物理合理，比 moderate 更强，非 B6 粗增广）。

完成 run：9/9。

| geom | ocs_only cMAE/hit30 | image_only cMAE/hit30 | joint cMAE/hit30 |
|:--|:--|:--|:--|
| G1 | 79.87/0.179 | 4.27/0.997 | 2.28/1.000 |
| G3 | 57.87/0.473 | 3.66/1.000 | 2.04/1.000 |
| G5 | 51.88/0.507 | 3.88/0.997 | 2.22/1.000 |

### C2 joint 增量（相对最佳单通道，best-val）

| geom | joint hit30 | best_single hit30 | Δhit30 | joint cMAE | best_single cMAE | ΔcMAE(增益) |
|:--|--:|--:|--:|--:|--:|--:|
| G1 | 1.0 | 0.9966 | +0.0034 | 2.277 | 4.273 | +1.996 |
| G3 | 1.0 | 1.0 | +0.0000 | 2.036 | 3.656 | +1.620 |
| G5 | 1.0 | 0.9966 | +0.0034 | 2.222 | 3.876 | +1.654 |

### C2 裁决

```text
- image_only 在 severe 下是否仍近饱和(hit@30>0.95 全几何)：True
- joint 是否稳定优于最佳单通道(Δhit30>0.005 全几何)：False
- 结论：joint 强互补性仍未被支持
- 无论结果如何，不写真实观测反演成功。
```

### C2 disagreement oracle（三通道逐样本取最优上界）

| geom | ocs hit30 | image hit30 | joint hit30 | single-oracle hit30 | 3ch-oracle hit30 |
|:--|--:|--:|--:|--:|--:|
| G1 | 0.1791 | 0.9966 | 1.0 | 1.0 | 1.0 |
| G3 | 0.473 | 1.0 | 1.0 | 1.0 | 1.0 |
| G5 | 0.5068 | 0.9966 | 1.0 | 1.0 | 1.0 |

oracle 是通道级选择上界（非可实现预测器），用于判断通道互补的理论上限。

