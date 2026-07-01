# 102_1C-B6-FIX01 多折补齐与 fold-matched baseline 修正执行报告

最后更新：2026-06-30
执行端：Claude
任务单依据：R109（及 R104/R105/R106/R107/R108）
任务性质：长程执行（代码+命令+日志+指标+结果），非方案盘点。

## 0. 结论先行

**完成。** R109 最低完成标准（no-aug image_only/joint/ocs_only 5-fold 全部完成 + final/best 双口径可审计 + fold-matched P1-A 对照表 + 阶段门判断）已全部达成；augmentation 第二优先级（image_only/joint standard 5-fold）也已完成。共 25 run 全部 exit 0，无失败/跳过。

一句话核心修正：**R108 关于"口径错误"的判断被证实。** 在 fold-matched P1-A baseline 下，no-aug 的 circular regression（B6）相对 exact-bin baseline（P1-A）**不是更差，而是 per-fold mean 稳定更好**：

```text
image_only no-aug: per-fold mean yaw cMAE  62.6°(final)/60.3°(best) vs P1-A fold-mean 81.4° → mean delta -18.8°/-21.2°
joint      no-aug: per-fold mean yaw cMAE  68.8°(final)/72.7°(best) vs P1-A fold-mean 81.4° → mean delta -12.6°/-8.7°
```

101 之所以得出"B6 比 baseline 更差"，正是因为它把 **B6 fold0**（恰好是 B6 表现最差的 fold，cMAE≈107–111°）对 **P1-A 5-fold pooled**（≈81.6°）。fold0 不能代表协议。

但更强的判断仍**不能**给出：B6 no-aug 绝对 cMAE 仍在 60–73°（coarse90≈0.43–0.51，仅略高于 chance 0.25），**yaw 外推没有被实质解决**，只是回归头比 exact-bin 分类略好。pitch 在 image/joint 多数 fold 明显改善。augmentation 是 **fold-依赖** 现象（多数 fold 恶化，joint fold3/4 反而改善），不能写全局结论。

## 1. 输入与上下文

读取的关键文件：

```text
CLAUDE.md（v0.4 工作区）
04_Codex审阅/R104、R105、R106、R107、R108
02_Claude输出/101_1C-B6_...Claude执行报告.md
06_v0.4_code/07_training/train_b6_circular_regression.py（FIX01 前）
06_v0.4_code/07_training/postprocess_b6_circular_metrics.py（FIX01 前）
v0.4_results/09_p1a_metric_recompute/p1a_channel_fold_metrics.csv（fold-matched 主对照）
v0.4_results/09_p1a_metric_recompute/p1a_channel_pooled_metrics.csv（pooled 补充）
v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold{0..4}.json（split，未改）
```

环境：`ocs_sim` Python（C:\Users\97466\.conda\envs\ocs_sim），torch 2.8.0+cu128，GPU=RTX 5060 Laptop（CUDA 可用）。注：`conda run -n ocs_sim` 触发本机 conda 插件报错，改用 env 内 `python.exe` 绝对路径直接调用，等价无影响。

## 2. 代码改动

仅在现有 B6 两脚本上扩展，未重写训练框架，未改 split/姿态网格/几何/backbone 容量。

### 2.1 train_b6_circular_regression.py（FIX01 增量）

- **best-val checkpoint**：训练循环中以 `val_yaw_cmae_deg` 最小为主选择指标追踪 best epoch（并行记录 val_pitch_mae 于日志但不参与选择，未做调参搜索）；深拷贝 best 权重。
- **final + best 双口径输出**：抽出 `eval_and_dump(tag, ckpt_name)`，对 final-epoch 与 best-val 各产出可区分文件：
  ```text
  metrics_val_final.json / metrics_test_final.json / samples_test_final.{npz,csv} / checkpoint_final.pt
  metrics_val_best.json  / metrics_test_best.json  / samples_test_best.{npz,csv}  / checkpoint_best.pt
  ```
  metrics JSON 内含 `select` 与 `best_epoch` 字段。
- **输出目录改为** `v0.4_results/10_b6_circular_regression_fix01/`，不覆盖 101 的 `10_b6_circular_regression/` fold0 原始结果。
- 编码器容量、损失（sin/cos MSE + 单位范数惩罚）、decode、增广包（ControlledImageAug：gaussian σ=0.01 / brightness ±10% / integer shift ≤2px）均与 101 一致，未改。

### 2.2 postprocess_b6_circular_metrics.py（重写）

- 读 `10_b6_circular_regression_fix01/`，对 final/best 各生成全套表。
- **新增 fold-matched 主对照** `b6_foldmatched_vs_p1a_{final,best}.csv`：每个 B6 run 只对 P1-A **同 fold、同对应通道**：
  ```text
  image_only -> C3_image_only ; joint -> C3_joint ; ocs_only -> C2_baseline_4dim
  ```
  cMAE 统一为度（P1-A 原单位 bin ×5°）；输出 `delta = B6 - P1A`（负=B6 更好）。
- **pooled 仅作补充** `b6_pooled_vs_p1a_{final,best}.csv`：按 (mode,aug) 跨 fold 拼接样本重算，对 P1-A pooled。
- per-fold mean / best-worst fold / best-worst yaw-block 写入 `b6_fix01_postprocess_summary.json` 的 `aggregate_per_mode_aug`。
- yaw-block / pitch-band 分层 final/best 各一套。

### 2.3 批处理脚本

`06_v0.4_code/07_training/run_b6_fix01_matrix.sh`：按 R109 优先级顺序（先 no-aug 5-fold×3，后 standard 5-fold×2）串行调度，逐 run 记录起止与 rc。

## 3. 实验矩阵

| 优先级 | mode | aug | fold | run 数 |
|---|---|---|---|---|
| P1（必跑） | image_only / joint / ocs_only | none | 0..4 | 15 |
| P2（尽量） | image_only / joint | standard | 0..4 | 10 |
| 合计 | | | | **25** |

固定超参（全矩阵一致，无搜索）：max_epochs=20、lr=1e-3、seed=42、batch=32、norm_weight=0.1。smoke：image_only fold0 2-epoch subset 验证 best-val 双口径产物落盘后清理。

## 4. 运行命令与日志

smoke：
```bash
PYEXE=C:/Users/97466/.conda/envs/ocs_sim/python.exe
$PYEXE 06_v0.4_code/07_training/train_b6_circular_regression.py --train --mode image_only --fold 0 --aug none --max-epochs 2 --smoke
```

正式矩阵（后台串行，25 run）：
```bash
bash 06_v0.4_code/07_training/run_b6_fix01_matrix.sh
# 内部对每个 (mode,fold,aug)：
$PYEXE 06_v0.4_code/07_training/train_b6_circular_regression.py --train --mode <mode> --fold <fold> --aug <aug> --max-epochs 20
```

后处理：
```bash
$PYEXE 06_v0.4_code/07_training/postprocess_b6_circular_metrics.py
```

运行状态：**25/25 run exit 0，rc 非零数=0，无 NaN/Inf**。批次日志 `v0.4_results/10_b6_circular_regression_fix01/_batch_fix01.log`。总墙钟 09:52→11:53（约 2.0 h），单 run 平均 264 s。无失败命令、无跳过项。

## 5. 结果文件清单

```text
v0.4_results/10_b6_circular_regression_fix01/
  _batch_fix01.log
  <run>/ ×25                              （每个含：run_config.json / train_log.csv /
                                            metrics_{val,test}_{final,best}.json /
                                            samples_test_{final,best}.{npz,csv} /
                                            checkpoint_{final,best}.pt）
  b6_run_metrics_summary_final.csv         b6_run_metrics_summary_best.csv
  b6_foldmatched_vs_p1a_final.csv          b6_foldmatched_vs_p1a_best.csv     ← 主裁决
  b6_pooled_vs_p1a_final.csv               b6_pooled_vs_p1a_best.csv          ← 补充
  b6_yawblock_stratified_final.csv         b6_yawblock_stratified_best.csv
  b6_pitchband_stratified_final.csv        b6_pitchband_stratified_best.csv
  b6_fix01_postprocess_summary.json        （per-fold mean / best-worst fold / best-worst yaw-block）
```

101 原始 `10_b6_circular_regression/` 未被触碰。

## 6. 指标结果

### 6.1 fold-matched 主对照（no-aug，yaw cMAE 度；delta<0 表示 B6 优于 P1-A 同 fold）

| mode | fold | B6 final | B6 best | P1-A fold | delta(final) | delta(best) |
|---|---|---:|---:|---:|---:|---:|
| image_only | 0 | 111.32 | 94.43 | 104.46 | +6.86 | −10.03 |
| image_only | 1 | 35.68 | 64.56 | 72.14 | −36.46 | −7.58 |
| image_only | 2 | 42.50 | 42.50 | 107.87 | −65.37 | −65.37 |
| image_only | 3 | 95.64 | 52.17 | 73.45 | +22.20 | −21.28 |
| image_only | 4 | 28.04 | 47.72 | 49.30 | −21.26 | −1.58 |
| **image_only mean** | | **62.63** | **60.27** | **81.44** | **−18.81** | **−21.17** |
| joint | 0 | 107.21 | 107.21 | 100.79 | +6.42 | +6.42 |
| joint | 1 | 36.11 | 65.00 | 75.76 | −39.65 | −10.75 |
| joint | 2 | 93.42 | 88.91 | 95.15 | −1.74 | −6.25 |
| joint | 3 | 78.81 | 65.20 | 88.54 | −9.73 | −23.34 |
| joint | 4 | 28.44 | 37.38 | 46.72 | −18.28 | −9.34 |
| **joint mean** | | **68.80** | **72.74** | **81.58** | **−12.60** | **−8.65** |
| ocs_only | 0 | 112.06 | 160.10 | 75.60 | +36.45 | +84.49 |
| ocs_only | 1 | 127.67 | 127.68 | 82.32 | +45.35 | +45.35 |
| ocs_only | 2 | 122.89 | 125.61 | 117.88 | +5.01 | +7.73 |
| ocs_only | 3 | 147.70 | 161.59 | 37.50 | +110.20 | +124.09 |
| ocs_only | 4 | 144.05 | 144.05 | 132.95 | +11.10 | +11.10 |
| **ocs_only mean** | | **130.88** | **143.81** | **89.21** | **+41.62** | **+54.55** |

读法：
- **image/joint no-aug：B6 per-fold mean 稳定优于 fold-matched P1-A**（mean delta 全为负）。撤回 101 的"image/joint B6 比 baseline 更差"表述。
- **但绝对仍未解决 yaw 外推**：image/joint mean cMAE 仍 60–73°，远未达"可用"（hit@30 pooled≈0.31，coarse90≈0.43–0.51 vs chance 0.25）。circular regression 把 cMAE 拉低但没有把 yaw 找回。
- **ocs_only 明确退化**（mean delta +42~+55°），4-dim OCS 在 yaw-block 外推下无方向信息，与既有负结果一致。

### 6.2 pooled 补充对照（仅参考，非主裁决）

| mode | aug | select | B6 pooled cMAE | P1-A pooled | delta | B6 coarse90 |
|---|---|---|---:|---:|---:|---:|
| image_only | none | final | 62.94 | 81.63 | −18.69 | 0.512 |
| image_only | none | best | 60.81 | 81.63 | −20.82 | 0.433 |
| joint | none | final | 68.88 | 81.58 | −12.71 | 0.476 |
| joint | none | best | 73.11 | 81.58 | −8.47 | 0.363 |
| ocs_only | none | final | 130.57 | 88.97 | +41.60 | 0.018 |
| image_only | standard | final | 130.34 | 81.63 | +48.71 | 0.019 |
| joint | standard | best | 82.24 | 81.58 | +0.66 | 0.331 |

pooled 与 fold-matched 结论方向一致（no-aug image/joint 优于 baseline）；保留为补充。

### 6.3 final vs best-val

best-val 不改变主结论方向（image/joint no-aug 仍优于 baseline；ocs/standard 仍差），但**逐 fold 数值有实质差异**，例如：

```text
image_only fold0: final cMAE 111.3 / coarse90 0.013  →  best (ep16) 94.4 / coarse90 0.193
joint standard fold3: final 38.1  →  best 30.2
```

说明 final-epoch 口径确实不稳（验证集波动大），best-val 给出更保守、对 augmentation 略友好的读数（image_only standard pooled：final 130.3 → best 107.1）。两套口径并存可审计。

## 7. yaw-block / pitch-band 分层

### 7.1 yaw-block：强外推距离依赖（跨 fold 复核）

best/worst yaw-block（per mode,aug，跨该组所有 fold 平均 cMAE）：

```text
image_only none:  best=[315,360) 21.6°   worst=[0,45) 141.2°   （final）
joint      none:  best=[315,360) 19.2°   worst=[0,45) 144.6°   （final）
joint      standard: best=[315,360) 10.5°  worst=[0,45) 155.2°  （final）
ocs_only   none:  best=[45,90) 80.0°    worst=[225,270) 158.3°  （final）
```

跨全部 5 fold 后，worst yaw-block 几乎恒为远端弧段、best 恒为邻近训练弧段。这把 101 fold0 的单折观察升级为 **5-fold 稳定的外推距离依赖**结论：失败不是均匀"yaw 物理不可观测"，而是远端外推坍缩、近端可内插。

### 7.2 pitch-band：image/joint 多数 fold 改善，但非完全稳定

no-aug pitch_mae（度）：
```text
image_only: f0 20.2 / f1 13.8 / f2 57.2 / f3 15.2 / f4 23.1
joint:      f0 14.4 / f1 13.3 / f2 12.8 / f3 34.5 / f4 14.9
ocs_only:   f0..f4 全部 46–54
```

image/joint **多数 fold** pitch_mae 13–23°（优于 P1-A baseline ~36°量级与 ocs ~46–54°），但 image fold2、joint fold3 退化到 34–57°。pitch 改善"多数存在但非每折稳定"。ocs_only pitch 始终崩。

## 8. 阶段门判断（逐条回答 R109 §6）

**1. 5-fold 下 circular regression 相对 fold-matched P1-A 是否有稳定 yaw 改善？**
分两层：(a) **相对 baseline 的 cMAE：是**——image/joint no-aug per-fold mean delta 稳定为负（−8.7~−21.2°），5 fold 中 image 4/5、joint 4/5 为负。(b) **绝对 yaw 外推：否**——mean cMAE 仍 60–73°、coarse90 仅略高于 chance，yaw 外推未被解决。结论：circular regression 是比 exact-bin 更合适的**输出头**，但不足以解决 yaw-block 外推。

**2. best-val 与 final-epoch 是否改变结论？**
不改变主方向（image/joint no-aug 优于 baseline、ocs/standard 差）。但逐 fold 数值差异实质存在，final-epoch 偏不稳；best-val 对 augmentation 略友好（image_only standard pooled 130→107）。两套并存，主裁决用 fold-matched，两口径一致支持上述结论。

**3. pitch 改善是否稳定存在？**
**多数稳定、非完全稳定。** image/joint 在 5 fold 中各 4/5 个 fold pitch_mae≤23°（优于 baseline），但 image fold2 / joint fold3 退化。ocs_only pitch 始终差。可写"回归头对可内插的 pitch 在多数 fold 有效"，不可写"pitch 全折稳定改善"。

**4. augmentation 是否仍然负面，还是只是 fold0/实现包现象？**
**是 fold/实现-依赖现象，不能写全局结论。** standard 多数 fold 显著恶化（image_only 5/5 变差），但 **joint fold3/4 反而改善**（delta −58.3/−12.2，best 口径）；joint standard pooled best delta ≈ +0.66°（基本持平）。固定增广包（含 torch.roll wrap-shift）整体偏负但非一致有害。按 R109 要求，augmentation 保留为"当前固定包下多数 fold 负面"的受限表述。

**5. "训练判据/输出头不是主因"是否可从待确认改为较稳定判断？**
**可以改为较稳定判断（偏向"判据/输出头不是主因"）。** 证据：换 circular regression 后，相对 baseline 的 cMAE 普遍改善，但 yaw 外推绝对水平仍未解决、coarse90 仍近 chance、worst block 跨 5 fold 恒为远端弧段。即"换更合适的输出头能改善指标读数，但救不回外推" → 主因不在 exact-bin 判据，而在 single-frame 信息形态 + yaw-block 外推协议。注：这是"较稳定"而非"完全确定"——尚未做 backbone/容量轴与多帧轴的对照。

**6. B6 是否可以闭口；如果不能，缺口是什么？**
**B6 的 single-frame 判据轴可以闭口**（A 类同门真改进已完成：circular regression 多折 + fold-matched + final/best 双口径，结论稳定）。但**头B阶段门不宜在此宣布全面闭口**，缺口：(a) augmentation 仅 standard 固定包，未做 noise/brightness/shift 拆分 ablation（R108 §2.4 所列）；(b) 未触及多帧/多几何信息轴——而这正是 yaw 外推失败指向的方向。建议把 B6 闭口表述限定为"single-frame 同门判据轴闭口为负结果"，而非"头B闭口"。

**7. 是否建议进入 T2 或 T3（仅建议，不放行）？**
- **T3（稀疏 GEO 光度时序 / 多帧多几何）优先级最高**：5-fold 证据稳定指向 single-frame 信息形态不足 + 外推距离依赖，与 R105/R106 主线一致。建议 Codex 据此设计 T3 阶段门，但本报告**不放行**。
- **T2（非朴素 fusion）**：joint ≈ image_only（pooled cMAE 68.9 vs 62.9，joint 未优于 image），early-concat 之外 fusion 收益证据不足，建议**最多作为 T3 前可选中间步**，不单独优先。
- 不建议在 single-frame 内继续调判据救 yaw（本轮已给 5-fold 否定证据）。

## 9. 红线自检（逐条）

- 不新渲染：是，仅读现有 PNG/split。
- 不改 split：是，直接用 e25 fold0..4 manifest，未改。
- 不改姿态网格 / 几何采样：是。
- 不改旧结果链：是，写入新目录 `10_b6_circular_regression_fix01/`，未触碰 101 的 `10_b6_circular_regression/`、R04/R21/E25/C2/C3。
- backbone 容量未作主变量、不做超参搜索：是，编码器与 E21 一致，超参全固定。
- 不写成果区 / 不写论文正文：是，报告写入 `02_Claude输出/`。
- 不进入 T2/T3 正式执行、不触发头A/头B合并裁决、不自行放行、不宣布头B闭口：是，仅给建议。
- 不把 GEO 库写成 supervised attitude truth：是，本轮未触及 GEO 数据。
- 不把 augmentation fold0/单折现象写成全局结论：是，已降级为"当前固定包多数 fold 负面"。
- 不把 pooled baseline 当作主对照：是，主裁决用 fold-matched，pooled 仅补充。

## 10. 交给 Codex 的待审问题

1. B6 闭口边界：是否同意"single-frame 同门判据轴闭口为负结果"，而把"头B闭口"留到 multi-frame/T3 之后？
2. augmentation：是否要求补 noise/brightness/shift 拆分 ablation 才允许对增广轴下任何正式结论，还是接受当前"固定包多数 fold 负面、joint 部分 fold 例外"的受限表述？
3. 下一步放行方向：是否据本轮 5-fold 证据进入 T3 阶段门设计；T2 是否仅作 T3 前可选中间步。
