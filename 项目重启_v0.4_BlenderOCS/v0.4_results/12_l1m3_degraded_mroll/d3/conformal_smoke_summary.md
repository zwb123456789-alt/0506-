# Conformal / P-DB 置信一致性 smoke（R116 子任务 D）

最后更新：2026-07-01  

**这是 smoke，不是最终置信校准。posterior-like 是工程候选分数，非真实 Bayesian posterior。**

## 1. Split-conformal smoke（yaw circular error 区间）

方法：val 集校准 yaw circular error 的 (1−α) 分位 q，test 预测区间 = pred ± q，coverage = test true 命中比例，set_size = 2q（°）。

| run | α | q(°) | val_n | test_n | test_coverage | target(1−α) | set_size(°) |
|:--|--:|--:|--:|--:|--:|--:|--:|
| P-INT_G5_ocs_only | 0.10 | 55.98 | 259 | 296 | 0.892 | 0.90 | 111.95 |
| P-INT_G5_ocs_only | 0.20 | 27.74 | 259 | 296 | 0.801 | 0.80 | 55.48 |
| P-INT_G5_joint | 0.10 | 6.28 | 259 | 296 | 0.889 | 0.90 | 12.56 |
| P-INT_G5_joint | 0.20 | 5.14 | 259 | 296 | 0.807 | 0.80 | 10.27 |
| P-INT_G1_ocs_only | 0.10 | 159.48 | 259 | 296 | 0.892 | 0.90 | 318.96 |
| P-INT_G1_ocs_only | 0.20 | 124.13 | 259 | 296 | 0.760 | 0.80 | 248.25 |

读法：coverage 接近 target(1−α) 即 split-conformal 区间在本 smoke 下自洽；set_size 越小表示该通道置信区间越紧。这是最简单的 split-conformal，未做条件覆盖、mondrian 分层或 posterior 校准，仅为 D3 后续正式阶段准备接口。

## 2. P-DB template retrieval smoke

见 `pdb_template_retrieval_smoke.csv`：以 train grid L1-G5 clean 多几何总光度向量为 template 库，test 向量按 cosine / neg-L2 检索 top-k，仅报告 top-1 与 top-k-best 的姿态误差，不写真实未知目标反演成功率。

