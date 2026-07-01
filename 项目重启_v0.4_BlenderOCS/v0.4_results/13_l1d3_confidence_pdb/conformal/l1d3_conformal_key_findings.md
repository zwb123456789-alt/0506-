# R118 子任务 D：Conformal 正式评估关键结论

最后更新：2026-07-01  

**conformal 输出是当前 simulated split 的误差覆盖区间，不是真实天文观测不确定度；coverage≈target 只说明该 split 下校准自洽，不是最终概率校准完成。**

## 1. split-conformal（test, best, α=0.10）coverage / set_size(°)

| method | degrade | G1 | G3 | G5 |
|:--|:--|:--|:--|:--|
| neural/ocs_only | clean | 0.899/322 | 0.912/246 | 0.902/126 |
| neural/ocs_only | degraded-mild | 0.905/320 | 0.939/276 | 0.895/149 |
| neural/ocs_only | degraded-moderate | 0.905/330 | 0.939/326 | 0.932/267 |
| neural/image_only | clean | 0.892/10 | 0.865/21 | 0.835/32 |
| neural/image_only | degraded-mild | 0.915/7 | — | 0.848/13 |
| neural/image_only | degraded-moderate | 0.912/16 | — | 0.932/11 |
| neural/joint | clean | 0.912/9 | 0.922/10 | 0.902/13 |
| neural/joint | degraded-mild | 0.888/7 | — | 0.892/7 |
| neural/joint | degraded-moderate | 0.845/7 | — | 0.882/8 |
| pdb-neg-L2 | clean | 0.909/340 | 0.895/320 | 0.929/10 |
| pdb-neg-L2 | degraded-mild | 0.973/350 | 0.956/340 | 0.905/180 |
| pdb-neg-L2 | degraded-moderate | 0.966/350 | 0.970/350 | 0.943/350 |

读法：coverage 应接近 target=0.90；set_size 越小表示该证据链区间越紧（信息量越高）。

## 2. set_size 随几何 / 退化变化（neural ocs_only best, α=0.10, set_size°）

| degrade | G1 | G3 | G5 |
|:--|--:|--:|--:|
| clean | 321.8 | 245.7 | 126.2 |
| degraded-mild | 320.2 | 276.0 | 148.8 |
| degraded-moderate | 330.5 | 325.8 | 267.3 |

## 3. Mondrian 分层回退情况

- Mondrian 行数：512；其中回退 pooled 校准（层内 val<10）：0

详见 `l1d3_mondrian_summary.csv`。

## 4. 严格口径

```text
- 只用 val 校准 quantile，test 仅评估；有限样本修正 level=ceil((n+1)(1-α))/n。
- coverage 接近 target 只代表该 simulated split 下 conformal 自洽。
- set_size 是 yaw 对称角度区间宽度（2q），不是真实观测置信度。
- P-DB conformal 用 top1 检索误差做 nonconformity，同样只是 split 内覆盖评估。
```
