# R82 Codex 审阅：1C-E45B 通过，指标重构与外推鸿沟叙事稳定

最后更新：2026-06-27  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  80_1C-E45B_指标重构与extrapolation-gap叙事说明_Claude执行报告.md
```

## 0. 裁决

```text
1C-E45B：PASS WITH CODEX CORRECTION
成果分流：允许形成成果区稳定摘要
性质：D 类只读指标重构与 framing 说明
新训练：NOT RELEASED
模型 / split / 超参 / seed 修改：NOT RELEASED
论文正文正式改写：NOT RELEASED
```

E45B 完成了 R81 要求的主任务：把论文主叙事从 “exact-bin yaw=0.00%” 调整为 “circular yaw-block 下的 extrapolation gap”，并明确 exact-bin 只能作为严格分类哨兵指标，不再单独承载物理不可观测 claim。

## 1. 红线核验

接受 Claude 的执行声明：

```text
未训练
未改代码
未改 split / 模型 / 超参 / seed
未写论文正文正式段落
未改成果区
未外推真实 GEO / 三轴姿态 / 暗室实验
```

输出位置正确：`02_Claude输出/`。本 R82 作为 Codex 审阅进入 `04_Codex审阅/`。

## 2. 关键校正

Claude 报告中 C2 yaw within-3 没有列出稳定均值，只写“见注”。Codex 直接从 E45A JSON 补算，避免无必要返工：

```text
来源：v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c2_extended_metrics.json
C2 65-run yaw within-3 mean = 0.0996
C2 65-run yaw within-3 median = 0.0739
chance within-3 = 7/72 = 0.0972
```

因此 C2 within-3 可写成：

```text
C2 OCS-only yaw within-3 ≈ 9.96%，约等于 chance 9.72%，中位数 7.39%。
```

这比 “—（见注）” 更清楚，也更支持 E45B 的主结论：C2 OCS-only 近邻 yaw 指标整体贴近随机。

## 3. 稳定指标表

| 指标 | chance | C2 OCS-only (65-run mean) | C3 image_only (5-fold mean) | C3 joint (5-fold mean) | random split reference |
|---|---:|---:|---:|---:|---:|
| exact-bin yaw_acc | 1.39% | 0.00% | 0.00% | 0.00% | approx. 65-70% |
| yaw CMAE | approx. 90.0 deg | 96.97 deg | 81.44 deg | 81.39 deg | n/a |
| yaw within-3 | 9.72% | 9.96% | 17.12% | 17.74% | n/a |
| yaw within-6 | 18.06% | 18.89% | 25.57% | 26.51% | n/a |
| yaw coarse45 | 12.50% | 14.53% | 17.96% | 18.16% | n/a |
| pitch exact | 2.70% | 3.03% | 21.20% | 19.42% | n/a |
| pitch within-3 | 18.92% | 17.75% | 56.07% | 51.77% | n/a |

解释：

- exact-bin yaw=0.00% 是 strict classifier + circular yaw-block 外推下的哨兵指标。
- C3 image_only / joint 在 yaw within-3、within-6、coarse45 上略高于 chance，可写成弱粗粒度残留信号。
- C2 OCS-only 的 yaw within-3 / within-6 / coarse45 基本贴近 chance。
- pitch 明显强于 yaw，支持 fixed-roll 设定下的 yaw/pitch 各向异性。
- joint 相比 image_only 没有实质互补增益，pitch 反而略低。

## 4. 稳定叙事

后续 Results/SI 的证据层级固定为：

```text
主叙事证据：
  yaw circular MAE、within-k、coarse-bin 与 chance/random baseline 对照

辅助哨兵指标：
  exact-bin yaw accuracy = 0.00%，说明严格分类命中失败

机制解释证据：
  E45A holdout-prediction ratio = 0.0
```

推荐核心表述：

```text
在 fixed-roll + circular yaw-block holdout 设定下，三通道模型均无法把 yaw 可靠外推到未见连续弧段。
Random split 约 65-70% 表明分布内 yaw 信息可被学习；
但 circular yaw-block 下 continuous / near-hit 指标接近随机或仅弱高于随机，
说明当前失败应写成 extrapolation gap，而不是 yaw unobservability。
```

不得写：

```text
yaw 信息不存在
OCS/image 物理不可观测 yaw
三通道无法学习任何 yaw 信息
exact-bin 0% 单独作为主图/主结论
E45A/E45B 证明 fusion 永久无价值
外推真实 GEO、三轴姿态、暗室实验或所有模型
```

## 5. 图表裁决

Figure 5 不再作为正文主图。

当前推荐：

```text
Figure 5 原 exact-bin 全 0 对比图：降级为 SI 或正文小 inset。
正文主图优先改为：yaw CMAE / within-6 / coarse45 vs chance baseline 的三通道对照。
正文主表可采用 R82 §3 的指标重构表。
Pitch exact / within-3 可作为 yaw/pitch anisotropy 的辅助图或表。
```

这意味着 R78 时代的三个版式问题仍需确认，但应在 E45B/R82 之后重新确认，不再按 “Figure 5 全 0 主图” 的旧前提决策。

## 6. 下一步

建议进入 `1C-E45C`，但只放行到“图表/SI 规划稿”，不直接生成全部图：

```text
1C-E45C 目标：
基于 R82 指标重构表，重排 Results/SI 图表体系：
- Figure 5 降级或替换方案
- S3/S4/S5 的新内容定义
- Table/Figure 编号体系
- 哪些图进入正文，哪些进入 SI
```

E45C 仍然不得训练、不得改模型/split、不得写论文正文正式段落。档 B 新训练仍不放行；若后续需要，只能另行预注册。
