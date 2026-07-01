# R104 Codex 审阅：100 通过，头B转入 A 类同门真改进阶段

最后更新：2026-06-29
审阅端：Codex
对象：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
100_1C-B5_头B后续技术路线与V0.3协议坐实_Claude执行报告.md
```

前置更正依据：

```text
R102_Codex_更正_R101撤回合并裁决准备放行并标定头B状态.md
R103_Codex_审阅_99合并裁决准备不通过_需按R102重做头B收口盘点.md
```

## 0. 裁决

```text
100 通过。
100 接收为 99 的替代材料，可作为头B后续技术路线与 V0.3 协议更正依据。
当前不进入头A/头B合并裁决，也不进入合并裁决准备。
头B尚未完成，下一步转入 1C-B6：A类同门真改进阶段。
```

回答作者当前问题：

```text
100 可以解决当前处境的“方向问题”：
它把工作从过早闭口/合并叙事，拉回到还缺真实实施结果的技术路线。

但 100 本身不是实施结果。
它只能作为后续技术指导与阶段门依据，不能当作头B完成证明。
```

因此，从 R104 起，后续 Claude 不能再只交“收口叙事/合并准备/材料分级”型报告。下一步必须面向脚本、配置、预注册实验矩阵和实测输出。

## 1. 100 的关键价值

100 相比 99 的实质改正有三点。

第一，它明确撤回了“P1-A 第一阶段只读指标重算 = 头B可合并”的误读：

```text
P1-A 第一阶段只是同一批已训练分类模型的指标重算。
它不能回答“改 loss / 输出头后，yaw 外推是否仍失败”。
```

第二，它把 V0.3 协议坐实，从而纠正 94/96 中基于“模块A”的误判：

```text
V0.3 真实协议 = 10°→5° coarse-to-fine 插值 holdout
              + sin/cos 连续回归
              + great-circle angular error / Hit@5 / Hit@10
              + 多几何 concat5 face-center OCS。

不是 random split + 分类 exact-bin。
```

第三，它把头B剩余工作重新归到可执行技术轴：

```text
T1  [84-A1] 判据真改进：classification exact-bin -> continuous/circular regression。
T1' [84-A2] 图像噪声/数据增广：loader-level noise/augmentation，不新渲染。
T2  [84-B1] 非朴素 fusion：T1 后再裁定。
T3  [84-C1] 多几何/light-curve sequence：最重门，T1 后若仍需要再开。
T4/T5 backbone/uncertainty：暂缓。
```

这正好回应当前最核心的问题：头B不能只拿诊断和叙事闭合，必须至少完成一次“真改进训练侧”尝试。

## 2. V0.3 协议更正是否接收

接收。

我复核了 100 给出的关键证据链，核心判断站得住：

```text
ocs_project/03_inversion/inv_common.py
  存在 split_coarse_to_fine()，说明 10° 网格 train -> 5° 插值 test 是旧反演协议的一部分。

论文改进/论文写作/03_投稿定稿/manuscript_md/主稿_v0.3_Acta_ASR润色版.md
  可检出 ResNet image-only 1.69±0.07 deg、
  fusion 1.47±0.07 deg、
  OCS-only per_part_log 5.91±0.22 deg、
  sin/cos 输出编码、great-circle angular error、Hit@5/Hit@10 等口径。

论文改进/补充实验/结果 与 ocs_project/03_inversion
  多处结果和脚本支持 concat5 / per_part_log / 10to5 / regression 这条旧协议链。
```

正式更正如下：

```text
94/96/P0-1 中对 V0.3 的“random split / 分类 / yaw_acc”式描述，不再作为当前依据。
V0.3 只可作为方法级先验或设计启发。
V0.3 face-center OCS 不得与 v0.4 Blender-derived OCS 写成同一结果链。
```

这项更正不推翻 R98 对 v0.4 自身诊断的结论：

```text
v0.4 当前 exact-bin 0%、signature overlap、yaw-block 外推失败、预测坍缩等诊断仍成立。
```

它改变的是“下一步该怎么试”，不是把 v0.4 负结果改写成成功。

## 3. 当前头B准确状态

截至 R104，头B状态应标定为：

```text
已完成：
1. B1 文献/方法约束。
2. B2 方法总结与阶段门候选。
3. B3/P0 只读诊断。
4. B4/P1-A 第一阶段只读指标重算。
5. B5/100 V0.3 协议坐实与剩余技术路线盘点。

未完成：
1. 训练侧 continuous/circular 判据改进。
2. 图像噪声/增广是否作为 A 类同门的实测对照。
3. 非朴素 fusion。
4. formal 多几何/light-curve sequence。
5. 更强 backbone、uncertainty、embedding/logits 导出等后续项。
```

一句话：

```text
头B还没有整体完成；它刚从“只读诊断与指标重算”转入“必须拿出真改进实施结果”的阶段。
```

## 4. 下一步放行：1C-B6 A类同门真改进

放行下一步：

```text
1C-B6_A类同门判据真改进与图像噪声增广阶段门
```

这一步不是再写一份路线报告，而是技术实施阶段。最低目标：

```text
T1 必做：
  在 v0.4 当前 split / 数据 / 特征 / 几何 / backbone 不变的前提下，
  将 exact-bin 分类训练改为 continuous/circular regression 或 regression+classification 双头。

T1' 建议同门纳入：
  在不新渲染的前提下，加入 loader-level 图像噪声/亮度/轻微平移增广，
  做 noise-off vs noise-on 的边际对照。
```

我裁定 T1 不可省略。T1' 不应再被默认丢到遥远的 P2；本轮建议作为同门 A 类对照纳入，但可采用轻量矩阵，避免把 B6 变成大调参。

推荐最小实验矩阵：

```text
M0: existing exact-bin baseline, 只作已存在结果对照，不重训。
M1: circular regression, noise-off。
M2: circular regression, noise-on / augmentation-on。

模式优先级：
  image_only 与 joint 优先，因为 T1' 只影响图像通道；
  ocs_only 可作为 T1 判据对照，但不参与图像噪声轴。

fold：
  沿用现有 circular yaw-block 5-fold；
  若算力不足，可先做 1 fold smoke + 5-fold 正式跑的两级报告，但不得把 smoke 当正式结论。
```

## 5. B6 技术约束

B6 必须遵守：

```text
不改 split。
不改姿态网格。
不改几何采样。
不新渲染。
不改 backbone 容量作为主变量。
不做超参搜索。
不覆盖 R04/R21/E25/C2/C3 既有代码与结果链。
不写论文正文。
不进成果区。
不触发头A/头B合并裁决。
```

脚本落点应从当前 v0.4 训练区复制派生：

```text
06_v0.4_code/07_training/train_baseline.py
06_v0.4_code/07_training/train_c2_screening.py
06_v0.4_code/07_training/dataset.py
06_v0.4_code/07_training/enhanced_ocs_dataset.py
```

建议新建副本脚本，名称由 Claude 在 B6 中按实际代码定，但原则为：

```text
train_baseline_circular.py 或 train_b6_circular_regression.py
dataset_augmented.py 或在副本脚本内定义受控 transform
evaluate_b6_circular.py / postprocess_b6_yawblock.py
```

结果输出不得写入旧成果链，建议独立目录：

```text
v0.4_results/10_b6_circular_regression/
```

## 6. B6 必须产出的材料

Claude 下一步执行报告不得只写“建议”。必须至少交付：

```text
1. 读取并确认当前训练脚本、dataset、split manifest、checkpoint/result 目录。
2. 新脚本或补丁文件清单，说明哪些是副本，哪些是新后处理脚本。
3. 预注册实验矩阵：mode、fold、loss、output head、augmentation、seed、epochs、batch size。
4. 训练目标定义：
   - yaw 用 sin/cos 或 circular target；
   - pitch 用连续角度或 sin/cos，需说明裁剪/归一化；
   - 若双头，classification head 只作 sentinel，不得反客为主。
5. 指标定义：
   - yaw circular MAE；
   - within-k / Hit@5 / Hit@10；
   - coarse45/coarse90 vs random/chance；
   - exact-bin sentinel；
   - pitch MAE；
   - per-fold、yaw-block、pitch-band 分层。
6. noise/augmentation 定义：
   - 噪声类型、幅度、是否仅 train-time；
   - brightness/shift 是否启用；
   - 所有参数固定，不做搜索。
7. 实测输出：
   - smoke 通过记录；
   - 正式训练结果，或明确的技术阻塞日志；
   - yaw-block 对照表与样本级预测文件。
```

如果训练因环境或算力失败，报告必须写成“技术阻塞”，并提供命令、错误、已生成文件与下一步修复建议。不得把失败转写为“阶段闭口”。

## 7. B6 后的分叉裁决

B6 结束后再裁定头B是否能进入后续合并。分叉如下：

```text
若 M1/M2 显著优于 exact-bin baseline，且 yaw-block 指标出现实质改善：
  说明此前失败有显著判据/训练口径成分。
  头B可形成正向方法贡献，T2/T3 可降为 future work 候选。

若 M1/M2 仍接近 chance 或仍严重 yaw-block 坍缩：
  说明单帧信息/融合策略问题仍未解决。
  不能合并；至少继续裁定 T2 非朴素 fusion，必要时进入 T3 多几何/light-curve sequence。
```

注意：

```text
T1 done 本身不等于头B闭口。
只有 T1 的结果把问题推入“方法成功”或“必须继续找信息源”的明确分叉，才构成下一轮裁决依据。
```

## 8. 禁止继续误用的说法

从 R104 起禁止：

```text
不得说“P1-A 已闭口，所以头B已完成”。
不得说“100 已解决头B，只等合并”。
不得把 V0.3 结果写入 v0.4 结果链。
不得把只读指标重算写成方法改进成功。
不得把 exact-bin 0% 写成 yaw 物理不可观测。
不得把 early concat 无增益写成所有 fusion 无互补。
不得把还未做的 T2/T3 通过叙事暂缓直接抹掉。
```

## 9. 给 Claude 的下一步最短提示词

```text
请按 Codex R104 执行 1C-B6：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
R104_Codex_审阅_100通过_头B转入A类同门真改进阶段.md

目标：A类同门真改进阶段，不再写纯盘点报告。

必须做：
1. 读取当前 v0.4 训练脚本与 dataset：
   06_v0.4_code/07_training/train_baseline.py
   06_v0.4_code/07_training/train_c2_screening.py
   06_v0.4_code/07_training/dataset.py
   06_v0.4_code/07_training/enhanced_ocs_dataset.py
2. 以副本方式实现 T1 continuous/circular regression 或 regression+classification 双头。
3. 预注册并尽量同门实现 T1' 图像 noise/augmentation 对照；不新渲染。
4. split/特征/几何/backbone/seed/epoch 上限保持可追溯，不做超参搜索。
5. 输出到 v0.4_results/10_b6_circular_regression/。
6. 产出 smoke、训练命令、结果表、yaw-block 分层表、样本级预测文件、阶段门判断。

禁止：
不得进入头A/头B合并裁决；
不得写论文正文或成果区；
不得新渲染；
不得覆盖旧结果链；
不得把 smoke 当正式结论；
不得只交叙事性报告。
```

