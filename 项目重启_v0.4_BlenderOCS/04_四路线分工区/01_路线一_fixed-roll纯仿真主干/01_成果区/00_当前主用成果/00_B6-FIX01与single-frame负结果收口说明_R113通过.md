# B6-FIX01 与 single-frame 负结果收口说明

最后更新：2026-06-30  
状态：R113 Codex 审阅通过，作为路线一 C 后续依据  
来源：

```text
04_Codex审阅/R113_Codex_审阅_102通过_B6判据轴闭口并放行L1M2阶段门.md
02_Claude输出/102_1C-B6-FIX01_多折补齐与foldmatched修正_Claude执行报告.md
v0.4_results/10_b6_circular_regression_fix01/
```

## 1. 这组负结果到底怎么做的

当前负结果来自路线一 C 的 single-frame / fixed-roll / yaw-block 压力测试链。

基础数据为：

```text
yaw: 0° 到 355°，每 5° 一个点，共 72 个 yaw
pitch: -90° 到 +90°，每 5° 一个点，共 37 个 pitch
roll: 固定 0°
总样本: 2664
每个样本: 一张灰度图像 + 同姿态 OCS 光度特征 + yaw/pitch 标签
```

评价协议为 yaw-block 5-fold：每折留出连续 yaw 弧段作测试。该协议是严格外推 stress test，不是路线一 C 的全部主线。

前序稳定结果包括：

```text
C2: 4维 per-part OCS-only
C3: image_only 与 image+OCS early concat
P1-A: 对同一批分类模型做 circular MAE / within-k / coarse-bin / yaw-block 分层重算
B6-FIX01: 将 exact-bin 分类头改为 sin/cos circular regression，并按 R109 补齐 5-fold、final/best-val、fold-matched P1-A 对照
```

## 2. 证据链怎么搭起来

### 2.1 C2/C3 证明 single-frame yaw-block 外推没有稳定成功

前序 C2/C3 5-fold 结果已经稳定为负：

```text
C2 OCS-only:
  exact-bin yaw = 0.00%
  circular MAE ≈ 88.97°
  coarse45 ≈ 11.82%
  coarse90 ≈ 24.44%

C3 image_only:
  exact-bin yaw = 0.00%
  circular MAE ≈ 81.63°
  coarse90 ≈ 25.41%

C3 joint:
  exact-bin yaw = 0.00%
  circular MAE ≈ 81.58°
  coarse90 ≈ 24.85%
```

这些结果说明：当前 single-frame / fixed-roll / yaw-block 整段外推协议下，4维 per-part OCS、单帧图像和 naive early concat joint 都没有形成稳定 yaw 外推。

### 2.2 P1-A/E45 系列证明 exact-bin 是过严哨兵，但不能单独解释失败

P1-A 与 E45B 将评价口径从 exact-bin 扩展为：

```text
circular MAE
within-k
coarse45 / coarse90
yaw-block stratification
pitch-band stratification
```

结论是：

```text
exact-bin yaw=0.00% 不能读成 yaw 信息完全不存在；
但 relaxed metrics 下 yaw 仍弱，且 yaw-block 异质性强。
```

因此 exact-bin 只能作为 sentinel 指标，不再作为论文主叙事指标。

### 2.3 B6-FIX01 证明训练头不是主要失败原因

B6-FIX01 在不改 split、姿态网格、几何采样、backbone 容量、不新渲染的前提下，将训练头从 exact-bin 分类改为：

```text
[yaw_sin, yaw_cos, pitch_sin, pitch_cos] continuous/circular regression
```

并补齐：

```text
image_only / joint / ocs_only, aug=none, fold=0..4
image_only / joint, aug=standard, fold=0..4
final-epoch 与 best-val 两套口径
fold-matched P1-A baseline 对照
```

关键 no-aug fold-matched 结果：

| mode | final B6 cMAE | final delta vs P1-A | best B6 cMAE | best delta vs P1-A |
|---|---:|---:|---:|---:|
| image_only | 62.635° | -18.806° | 60.273° | -21.167° |
| joint | 68.797° | -12.596° | 72.740° | -8.653° |
| ocs_only | 130.875° | +41.623° | 143.805° | +54.553° |

读法：

```text
image/joint 的 circular regression 相对 exact-bin 分类 baseline 在 cMAE 上稳定改善；
但绝对 yaw 外推仍远未解决，coarse90 仍只有限高于 chance；
ocs_only 明确退化，4维 per-part OCS 不能支撑当前 yaw-block 外推。
```

因此，训练头/判据不是主要失败原因。更准确地说：

```text
更合适的输出头能改善指标读数，但救不回 single-frame yaw-block 外推。
```

但这是"较稳定"判断，而非"完全确定"：尚未做 backbone/容量轴与多帧轴的对照。"判据/输出头不是主因"是在已测的 single-frame 判据轴上的稳定结论，不等于排除了所有非信息形态的其它因素。

## 3. 当前可以收口的结论

可以稳定写成：

```text
在当前 single-frame / fixed-roll / yaw-block 整段外推 / naive fusion 或 per-part OCS 诊断输入条件下，
单帧图像、4维 per-part OCS 与 early-concat joint 均未得到稳定 yaw 外推。

exact-bin 评价口径过严，不能把 0% 写成 yaw 信息完全不存在；
continuous/circular regression 能改善 image/joint 的 cMAE；
但 yaw 外推仍表现为远端 block 坍缩和强位置依赖。

因此，这条负结果主要指向 single-frame 信息形态不足与 yaw-block 外推协议过强，
而不是单纯 exact-bin 判据造成。
```

## 4. 当前不能写成什么

禁止写成：

```text
光度无用；
yaw 物理不可观测；
图像无姿态信息；
所有融合方法无效；
多几何 OCS 已失败；
光变/时序路线已失败；
路线一 C 整体失败；
真实未知目标姿态反演系统已被验证或否定。
```

尤其要保留三条边界：

```text
1. 当前 C2 的 4维 per-part OCS 是 semi-oracle / diagnostic，不是现实主线输入。
2. 24 号主线 OCS 是 L1 跨几何多观测总光度向量，尚未由 C2/C3/B6 否定。
3. yaw-block 是 strict extrapolation stress test，不应独占路线一 C 主线。
```

## 5. 阶段门结论

```text
B6-FIX01 关闭：single-frame 同门判据/训练头补救轴。
B6-FIX01 支持：头B旧负结果追因阶段性收束，旧 single-frame 负结果不再继续扩展。
B6-FIX01 不支持：触发头A/头B大合并裁决、关闭路线一 C 整体、替代 L1 多几何主线、替代 roll sensitivity、替代 consistency-as-confidence。
```

下一步应转入：

```text
L1(M2): G1/G3/G5 跨几何多观测 OCS 主线
```

原因是当前结果已经足够说明：继续在 single-frame 判据轴上纠缠，收益有限；路线一 C 必须回到 24 号定义的 F1/L1/G1/G3/G5、image、互补性、置信一致性和 roll sensitivity。

更短的执行口径：

```text
头B阶段性收束：
B6-FIX01 已关闭 single-frame 判据/训练头追因轴；
旧 single-frame 负结果不再扩展；
后续路线一 C 转入 L1(M2) 多几何 OCS 主线。
```

## 6. 可引用路径

```text
04_Codex审阅/R77_Codex_审阅_1C-E43通过_C2C3三通道负结果证据包稳定.md
04_Codex审阅/R78_Codex_审阅_1C-E44通过_C2C3_Results非正文总材料包稳定.md
04_Codex审阅/R82_Codex_审阅_1C-E45B通过_指标重构与外推鸿沟叙事稳定.md
04_Codex审阅/R108_Codex_审阅_101_B6长程执行部分接收但不闭口需FIX01.md
04_Codex审阅/R109_Codex_任务单_1C-B6-FIX01多折补齐与foldmatched修正.md
04_Codex审阅/R113_Codex_审阅_102通过_B6判据轴闭口并放行L1M2阶段门.md
02_Claude输出/102_1C-B6-FIX01_多折补齐与foldmatched修正_Claude执行报告.md
v0.4_results/10_b6_circular_regression_fix01/
```
