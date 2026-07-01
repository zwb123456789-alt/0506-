# R81 Codex 审阅：主指标叙事地雷与 E45B 指标重构放行

最后更新：2026-06-27  
审阅端：Codex  
性质：方法学叙事审阅 / R80 后续修正裁决

## 0. 裁决

```text
新增意见：ACCEPTED
R80 结论：不推翻，但需要提升“主指标叙事修正”的优先级
1C-E45B：RELEASED
任务性质：D 类，只读指标重构与 framing 说明
新训练：NOT RELEASED
模型 / split / 超参 / seed 修改：NOT RELEASED
论文正文正式改写：NOT RELEASED
```

这条意见补中了 R80 只说了一半的问题：R80 已经把 exact-bin yaw=0% 定位为 holdout yaw block 外推失败，但还没有足够明确地指出，**exact-bin yaw accuracy 不应继续作为论文叙事中的主证据指标**。后续论文骨架应从“exact-bin 全 0”转向：

```text
extrapolation gap:
在 fixed-roll + circular yaw-block 外推设定下，
模型无法把 yaw 泛化到未见弧段；真正稳健的证据是 circular MAE、within-k、coarse-bin 与随机基线的对照。
```

## 1. 代码证据核验

| 议题 | 证据路径 | Codex 判断 |
|---|---|---|
| yaw 是 72 类分类 | `06_v0.4_code/07_training/train_baseline.py` 中 `predictor = Linear(dim, n_yaw + n_pitch)`，forward 后切分为 `yaw_logits[:, :72]` | 成立 |
| exact-bin yaw_acc 是 argmax 分类命中 | `compute_all_metrics` 对 `yaw_logits.argmax` 与 `yaw_true` 做相等判断 | 成立 |
| circular yaw-block 会把连续 test yaw bin 整块从 train 移除 | `06_v0.4_code/07_training/split_dataset.py` 的 `split_circ_yaw_block`：`train_bins = all - test_bins - val_bins` | 成立 |
| pitch 没有同等 yaw-block 外推结构 | 当前主失败模式主要施加在 yaw 维度；pitch 类在 train/test 分布中保留更多分布内条件 | 成立 |
| 已有连续/近邻指标 | `train_baseline.py` 已输出 `yaw_circular_mae_deg`、`within_1/3/5_bins`；E45A 又补了 `within_6`、coarse-bin、混淆矩阵 | 成立 |
| random split 可学 | R77/R78 成果区已记录 random split yaw_acc 约 65-70% | 成立 |
| last-epoch checkpoint | 训练记录 best epoch，但保存的是训练结束时模型 state | 成立，应作为方法限制说明 |
| val 子集取前 N 条 | `make_infinite` 使用 val dataset 的前 `max_n` 子集 | 成立，只影响 val 监控，不直接推翻 test 结论 |

说明：上表使用当前文件结构核验，具体行号可能随后续编辑漂移；后续引用应优先写“文件 + 函数/字段名”，避免把行号当成长期稳定证据。

## 2. 方法学判断

当前 exact-bin yaw=0.00% 不能被写成干净的物理不可观测性发现。更准确的解释是：

```text
72-way yaw softmax 分类头在 circular yaw-block 协议下，被要求命中训练阶段完全未出现过的一整段 yaw 类；
exact-bin 0% 因此高度受实验设计与分类表述影响。
```

这并不削弱负结果，反而让负结果更准确：

```text
不是 “OCS / image 物理上不含 yaw 信息”，
而是 “当前 fixed-protocol 模型在未见 yaw 弧段上存在严重 extrapolation gap”。
```

因此，后续 Results / SI 的证据层级应调整为：

```text
主叙事证据：yaw circular MAE、within-k、coarse-bin、随机基线 / chance baseline 对照
辅助哨兵指标：exact-bin yaw accuracy = 0.00%，用于说明严格分类命中失败，不单独承载物理 claim
机制解释证据：E45A 的 holdout-prediction ratio = 0.0
```

## 3. 对既有成果口径的修正

R77/R78/R80 的负结果不推翻，但需要在后续论文材料中降级 exact-bin 的叙事位置：

```text
旧风险口径：
三通道 cross-yaw exact-bin yaw accuracy 全为 0.00%，因此 fixed-protocol yaw 泛化为 null。

修正后口径：
在 circular yaw-block 外推设定下，三通道 exact-bin yaw 均为 0.00%；
但 exact-bin 是严格分类哨兵指标，主要反映未见 yaw 类外推失败。
更有论文说服力的证据是 circular MAE、within-k、coarse-bin 与随机基线共同显示：
模型仅保留弱粗定位信号，无法形成可靠跨 yaw 弧段外推。
```

必须避免：

```text
不可写 “yaw 信息不存在”
不可写 “OCS/image 物理不可观测 yaw”
不可把 exact-bin 0% 单独作为主图/主结论
不可用 E45A 证明 fusion 永久无价值
```

可写：

```text
random split 约 65-70% 表明分布内 yaw 信息可被模型学习；
circular yaw-block 下连续指标接近随机，说明问题在跨弧段外推，而不是信息完全不存在。
```

## 4. 放行 1C-E45B

正式放行一个 D 类窄任务：

```text
任务编号：1C-E45B
任务名称：指标重构与 extrapolation-gap framing 说明
任务性质：只读整理已有结果，不训练、不改代码、不改 split、不改模型
输出位置：02_Claude输出/
```

E45B 只允许做：

```text
1. 读取 R77/R78/R80 已稳定成果和既有 JSON/CSV。
2. 整理 C2/C3 三通道的 yaw circular MAE、within-k、coarse-bin、exact-bin、pitch 对照。
3. 明确随机 / chance baseline：
   - yaw exact chance = 1/72
   - yaw circular MAE uniform expectation 约 90 deg
   - yaw within-3 chance = 7/72
   - yaw within-6 chance = 13/72
   - yaw coarse45 chance = 1/8
4. 形成一张“exact-bin vs continuous/near-hit metrics vs chance”的对照表。
5. 写一段方法学说明草稿，核心词为 extrapolation gap，不写 unobservability。
6. 列出 Figure/Table 调整建议：Figure 5 不再做 exact-bin 全 0 主图；优先展示 CMAE / within-k / coarse45 与 chance 对照。
```

E45B 不允许做：

```text
不训练
不改训练代码
不改 split
不改模型头
不做 circular regression
不做 random/interleaved 新训练
不写论文正文正式段落
不改成果区
不外推真实 GEO / 三轴姿态 / 暗室实验
```

## 5. 给 Claude 的短提示词

```text
执行 1C-E45B：指标重构与 extrapolation-gap framing 说明。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R80_Codex_审阅_1C-E45A通过_负结果归因诊断稳定.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R81_Codex_审阅_主指标叙事地雷与E45B指标重构放行.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/11_C2C3三通道负结果证据包_E43_R77通过.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/12_C2C3_Results非正文总材料包_E44_R78通过.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/13_E45A负结果归因诊断_R80通过.md
- v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.json
- v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c2_extended_metrics.json

任务：
1. 只读取已有结果，不训练、不改代码、不改 split、不改模型。
2. 整理一张 C2/C3 三通道指标重构表：exact-bin、yaw CMAE、within-3、within-6、coarse45、pitch exact/within-3，并列 chance/random baseline。
3. 明确写出：exact-bin yaw=0% 是 strict classifier + circular yaw-block 外推下的哨兵指标，不应单独承载物理不可观测 claim。
4. 把主叙事改为 extrapolation gap：random split 可学，circular yaw-block 外推失败，连续指标接近随机但有弱粗定位残留。
5. 给出 Figure/Table 调整建议：Figure 5 exact-bin 全 0 降级，正文优先展示 CMAE/within/coarse vs chance。
6. 输出简短报告到：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
   80_1C-E45B_指标重构与extrapolation-gap叙事说明_Claude执行报告.md

红线：
- 不训练。
- 不改任何代码、split、模型、超参、seed。
- 不写论文正文正式段落。
- 不把结果写成 unobservability。
- 不外推真实 GEO、三轴姿态、暗室实验或所有模型。
- 不改成果区，成果区分流等 Codex 审阅后再定。
```

## 6. 下一步

当前优先级调整为：

```text
1. 先执行 E45B 指标重构与叙事修正。
2. Codex 审阅 E45B。
3. 若通过，再决定 E45A/E45B 诊断资产如何进入 Results/SI 图表体系。
4. 档 B 新训练仍不放行，除非另行预注册。
```

这一步比补图更靠前，因为它决定负结果的论文地基：从容易被审稿人攻击的 exact-bin 0% 叙事，转为更稳的外推鸿沟叙事。
