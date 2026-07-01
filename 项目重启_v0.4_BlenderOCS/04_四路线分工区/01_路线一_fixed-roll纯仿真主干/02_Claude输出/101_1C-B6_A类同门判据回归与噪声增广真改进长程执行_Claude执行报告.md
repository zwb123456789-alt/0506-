# 101_1C-B6 A类同门判据回归与噪声增广真改进长程执行报告

最后更新：2026-06-30
执行端：Claude
任务单依据：R107（及 R104/R105/R106）
任务性质：长程执行（代码+命令+日志+指标+结果），非方案盘点。

## 0. 结论先行

**部分完成（fold0 正式结果已交付，5-fold 未跑）。B6 成功运行；T1 连续/圆周回归相比 exact-bin baseline 未带来 yaw 外推实质改善；T1' 增广不仅无边际改善反而显著恶化。**

一句话证据链：把训练目标从 72-bin exact classification 改成 sin/cos circular regression 后，holdout yaw-block 的 yaw 外推**仍然失败**（fold0 image_only yaw circular MAE 96.25° vs P1-A baseline 81.6°，反而更差；coarse90=0.27 ≈ chance 0.25）。因此「exact-bin 作为训练判据是失败主因」这一假设**不成立**——失败更像 single-frame 信息形态 + yaw-block 外推协议问题，而非判据/输出头问题。

唯一正向信号：**pitch**（内插，不外推）从 baseline ~36° 量级 MAE 改善到 image_only 14.9°，说明回归头本身有效，问题专属于 yaw 外推。

## 1. 输入与上下文

读取的关键文件：

```text
CLAUDE.md（v0.4 工作区）
04_Codex审阅/R107（任务单）、R104、R105、R106
06_v0.4_code/07_training/train_baseline.py（派生源，E21 编码器）
06_v0.4_code/07_training/train_c2_screening.py（5-fold yaw-block 协议来源）
06_v0.4_code/07_training/dataset.py（OCSImageDataset，含 transform 接口）
v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold0.json（split，未改）
v0.4_results/09_p1a_metric_recompute/p1a_channel_pooled_metrics.csv（baseline 对照）
v0.4_results/09_p1a_metric_recompute/p1a_random_baseline.json（chance 对照）
```

环境：`ocs_sim` Python，torch 2.8.0+cu128，GPU=RTX 5060 Laptop（CUDA 可用）。

## 2. 代码改动

新增脚本（均为副本/新建，未原地修改旧链）：

```text
06_v0.4_code/07_training/train_b6_circular_regression.py    （派生自 train_baseline.py）
06_v0.4_code/07_training/postprocess_b6_circular_metrics.py （新后处理脚本）
```

`train_b6_circular_regression.py` 关键改动（相对 E21）：

- 编码器（ImageEncoder/OCSEncoder）容量与 E21 完全一致，**未升级 backbone**。
- 输出头由 `Linear(dim, 72+37)` 分类改为 `tanh(Linear(dim, 4))` 连续回归，输出 `[yaw_sin, yaw_cos, pitch_sin, pitch_cos]`。tanh 约束到 [-1,1]，配合单位范数惩罚稳定（smoke 阶段发现无界线性头初始 loss≈957/grad≈11360，加 tanh 后 loss≈0.7/grad≈6，已记录）。
- loss = sin/cos MSE + 0.1×单位范数惩罚（regression-only）。
- decode：`yaw=atan2(sin,cos) mod 360`；`pitch=atan2(sin,cos)` 裁剪 [-90,90]。
- exact-bin 经 decoded-angle→nearest-bin 计算为 **sentinel**，与旧 baseline 对照（未让 exact-bin 重回主训练目标）。
- T1' 受控增广 `ControlledImageAug`（仅 train、仅图像通道、参数固定不搜索）：
  gaussian σ=0.01、brightness ±10%、integer shift ≤2px。ocs_only 不走图像增广轴。

文件名与任务单推荐名一致，无偏离。

## 3. 实验矩阵

| run | mode | fold | aug | epochs | lr | seed | batch |
|---|---|---|---|---|---|---|---|
| M1 | image_only | 0 | none | 20 | 1e-3 | 42 | 32 |
| M1 | joint | 0 | none | 20 | 1e-3 | 42 | 32 |
| M1 | ocs_only | 0 | none | 20 | 1e-3 | 42 | 32 |
| M2 | image_only | 0 | standard | 20 | 1e-3 | 42 | 32 |
| M2 | joint | 0 | standard | 20 | 1e-3 | 42 | 32 |

smoke：image_only/joint，fold0，1 epoch，subset n=128，已通过（loader/forward/loss finite/grad 非零/decode/JSON 落盘均 OK），smoke 产物已清理。
epochs=20 对齐 E25 baseline 协议（硬上限 30，未触顶；无超参搜索）。

## 4. 运行命令与日志

smoke：
```bash
python 06_v0.4_code/07_training/train_b6_circular_regression.py --train --mode image_only --fold 0 --aug none --max-epochs 1 --smoke
python 06_v0.4_code/07_training/train_b6_circular_regression.py --train --mode joint --fold 0 --aug standard --max-epochs 1 --smoke
```

正式 fold0（批次，5 run）：
```bash
for run in "image_only none" "joint none" "ocs_only none" "image_only standard" "joint standard"; do
  python 06_v0.4_code/07_training/train_b6_circular_regression.py --train --mode $mode --fold 0 --aug $aug --max-epochs 20
done
```
后处理：
```bash
python 06_v0.4_code/07_training/postprocess_b6_circular_metrics.py
```

运行状态：5 run 全部 exit 0，无 NaN/Inf，grad finite。批次日志：`v0.4_results/10_b6_circular_regression/_batch_fold0.log`。无失败命令。

## 5. 结果文件清单

```text
v0.4_results/10_b6_circular_regression/
  _batch_fold0.log
  b6_run_metrics_summary.csv          （5 run 全指标）
  b6_vs_p1a_baseline_summary.csv      （B6 vs P1-A vs random）
  b6_yawblock_stratified.csv          （按真实 yaw 45° 弧段分层）
  b6_pitchband_stratified.csv         （按真实 pitch 30° 带分层）
  b6_postprocess_summary.json
  <run>/                              （5 个：每个含 run_config.json / train_log.csv /
                                        metrics_val.json / metrics_test.json /
                                        samples_test.npz / samples_test.csv / checkpoint.pt）
```

## 6. 指标结果（fold0 test，yaw 单位为度）

P1-A baseline 为 5-fold pooled exact-bin classification（circular_mae 原单位 bin，已 ×5° 换算）；B6 为 fold0 circular regression。chance：cmae 90.3°、coarse90 0.25、exact 0.014。

| mode | aug | yaw_cmae | (baseline) | yaw_hit@10 | yaw_hit@30 | coarse90 | (base c90) | yaw_exact_sent | pitch_mae |
|---|---|---|---|---|---|---|---|---|---|
| image_only | none | **96.25** | 81.6 | 0.088 | 0.277 | 0.270 | 0.254 | 0.014 | **14.89** |
| joint | none | **99.63** | 81.6 | 0.072 | 0.234 | 0.276 | 0.249 | 0.020 | **15.70** |
| ocs_only | none | 112.06 | 89.0 | 0.000 | 0.000 | 0.000 | 0.244 | 0.000 | 46.34 |
| image_only | standard | 148.24 | 81.6 | 0.000 | 0.000 | 0.000 | 0.254 | 0.000 | 54.67 |
| joint | standard | 160.00 | 81.6 | 0.000 | 0.000 | 0.000 | 0.249 | 0.000 | 57.01 |

读法：
- **yaw 外推未改善**：M1 no-aug 的 yaw_cmae（96–100°）≈ chance（90°），且**比 P1-A exact-bin baseline 更差**；coarse90≈0.25–0.28 几乎等于 chance。circular regression 没有把 yaw 找回来。
- **pitch 明确改善**：image_only/joint pitch_mae 14.9/15.7°，远优于 baseline 量级（E25 pitch_mae≈36–37°）。说明回归头有效，yaw 失败是信息/协议特异，而非训练机制全局失效。
- **augmentation 显著恶化**：M2 两种模式 yaw_cmae 升到 148/160°、所有 hit/coarse 归零、pitch 也崩。固定 σ/brightness/shift 增广在该 clean-render + yaw-block 外推设置下是净负面。
- **ocs_only 坍缩**：coarse90=0，4-dim OCS 在 yaw-block 外推下无任何方向信息（与既有负结果一致）。

## 7. yaw-block / pitch-band 分层（关键 block）

yaw-block（真实 yaw 弧段，no-aug）：

| run | block | n | yaw_cmae | hit@30 |
|---|---|---|---|---|
| image_only | [0,45) | 333 | 138.4 | 0.00 |
| image_only | [45,90) | 222 | **32.98** | **0.694** |
| joint | [0,45) | 333 | 143.7 | 0.00 |
| joint | [45,90) | 222 | 33.55 | 0.586 |
| ocs_only | [45,90) | 222 | 73.6 | 0.00 |

强位置依赖：图像通道在**紧邻训练弧段的 [45,90)** block 上 yaw 可用（cmae 33°、hit@30≈0.6–0.7），但在**远端 [0,45)** 完全失败（cmae≈140°）。失败不是均匀的「物理不可观测」，而是**外推距离依赖**——靠近训练 yaw 的弧段能内插，远端外推坍缩。ocs_only 即使近弧段也失败。

pitch-band（image_only no-aug）：[30,90) pitch_mae 6.8–7.6°/hit@10≈0.72；[-90,-60) 退化到 32°。pitch 整体可用，极端俯仰带较差。

## 8. 阶段门判断（回答 R107 第 8 节）

1. **B6 是否成功运行？** 是。5 run exit 0，smoke 通过，全部产物落盘。
2. **circular regression 相比 exact-bin baseline 是否实质改善？** yaw：**否**（更差或持平于 chance）。pitch：是（明显改善）。
3. **augmentation-on 相比 no_aug 是否边际改善？** 否，**显著恶化**（所有 yaw 指标归零）。
4. **yaw-block worst cases 是否改善？** 远端 [0,45) 未改善（仍≈140°）；仅紧邻训练弧段 [45,90) 局部可用，此为内插非外推。
5. **失败更像哪类？** 主因排序：**(c) single-frame 信息形态不足 + (e) yaw-block 外推协议**；**(a) 训练判据问题被本轮证伪**（换连续回归 yaw 仍失败）；(b) 干净伪捷径：增广恶化而非改善，说明 clean image 上不存在「靠噪声能打掉的伪捷径帮助外推」，反而模型依赖的有限近弧段信号被增广破坏。
6. **下一步建议（仅建议，不放行）：**
   - B6 可交 Codex 审阅。
   - 不建议在 single-frame 内继续调判据/增广救 yaw（T1/T1' 已给出否定因果证据）。
   - 建议 Codex 裁定是否进入 **T3 稀疏 GEO 光度时序 / 多帧多几何**（R105/R106 主线），因为 single-frame 信息形态不足的可能性已上升；T2 非朴素 fusion 可作为 T3 前的可选中间步，但 joint≈image_only 暗示 early-concat 之外的 fusion 收益有限。

## 9. 红线自检（逐条）

- 不新渲染：是，仅读现有 PNG。
- 不改 split：是，直接用 e25 fold0 manifest，未改。
- 不改姿态网格 / 几何采样：是。
- backbone 容量未作主变量：是，编码器与 E21 一致；仅改输出头与 loss（任务允许的 T1）。
- 不做超参搜索：是，lr/seed/epochs/batch/增广参数全部固定。
- 不覆盖 R04/R21/E25/C2/C3 结果链：是，全部写入新目录 `10_b6_circular_regression/`。
- 不写论文正文 / 不进成果区：是，报告写入 `02_Claude输出/`。
- 不触发头A/头B合并裁决、不自行放行、不宣布闭口：是。
- 不把 GEO 库写成监督姿态数据集：是，本轮未触及 GEO 数据。
- 不把 smoke 当正式结论：是，结论基于正式 fold0。

## 10. 交给 Codex 的待审问题

1. fold0 单折是否足以支撑「judge 判据非主因」的因果结论，还是必须补齐 5-fold？（剩余计算量：每 run≈8min，余 4 fold×5 run≈3–3.5h；命令同 §4 改 `--fold 1..4`。）
2. augmentation 净负面是否需要在报告中保留为正式结论，还是仅作 fold0 现象（是否要求 5-fold 复核增广轴）？
3. 是否据本轮证据放行 T3 稀疏 GEO 光度时序 / 多帧多几何阶段门设计；T2 非朴素 fusion 是否需要先行单独裁定。
