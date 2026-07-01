# 1C-E45A 执行报告：负结果归因诊断（档 A-min 推理重聚合）

- 任务编号：1C-E45A（依据 R79 放行）
- 性质：负结果归因诊断 / 已训练 checkpoint 只读推理复算 + 后处理敏感性分析
- 不训练、不改训练脚本、不改 split/模型/超参；仅 exploratory secondary diagnostics

## 1. 任务状态

完成。先行门全通过，扩展判据与失败模式诊断已落盘。无越界 claim，结论仍限定 phase63 fixed-roll + circular yaw-block holdout。

## 2. 关键产物路径

诊断脚本（`06_v0.4_code/09_diagnostics/`）：

```text
e45a_recompute_c3.py     # C3 image_only/joint ×5fold 只读推理复算 + 先行门
e45a_recompute_c2.py     # C2 13configs×5fold=65 只读推理复算 + 先行门
e45a_postprocess.py      # 逐样本→coarse-bin/within-k/CMAE分布/72×72混淆矩阵
```

结果（`v0.4_results/07_negative_diagnosis/e45a_inference_regroup/`）：

```text
c3_gate_alignment.json/.csv    c2_gate_alignment.json/.csv     # 先行门对齐表
c3_samples/  c2_samples/                                       # 逐样本预测 npz（10 + 65）
c3_extended_metrics.json/.csv  c2_extended_metrics.json/.csv   # 扩展判据
c3_confusion/  c2_confusion/                                   # 72×72 yaw 混淆矩阵
```

## 3. 核心结果

### 3.1 先行门（exact-bin 1:1 复现）：全 PASS

- C2：65/65 run，yaw_acc/pitch_acc/yaw_cmae 与各折 result.json `final_metrics.test` 逐位对齐（cmae 小数点后 3 位一致）。
- C3：10/10 run，与各折 detail.json `final_eval.test_primary` 对齐。
- 复算复用训练脚本原始 `evaluate`/`compute_metrics`，口径一致，推理链可信。

### 3.2 扩展判据（chance 基线对照）

chance：yaw exact=0.0139，coarse30=0.0833，coarse45=0.1250，within1=0.0417，within3=0.0972，within6=0.1806。

C3（5 fold 均值）：

| 判据 | image_only | joint | chance |
|---|---|---|---|
| yaw exact | 0.0000 | 0.0000 | 0.0139 |
| yaw coarse30 | 0.1049 | 0.1141 | 0.0833 |
| yaw coarse45 | 0.1796 | 0.1816 | 0.1250 |
| yaw within3 | 0.1712 | 0.1774 | 0.0972 |
| yaw within6 | 0.2557 | 0.2651 | 0.1806 |
| yaw CMAE° | 81.44 | 81.39 | — |
| pitch exact | 0.2120 | 0.1942 | 0.0270 |
| pitch coarse30 | 0.4711 | 0.4285 | — |
| pitch within3 | 0.5607 | 0.5177 | — |

C2 OCS-only（65 run 均值）：yaw exact 0.0000，coarse30 0.0876，coarse45 0.1453，within3 0.0996，within6 0.1889，CMAE 96.97°，pitch exact 0.0303。C2 单点最好 baseline_4dim fold3：coarse30 0.2857、within6 0.4286。

### 3.3 失败模式诊断（R79 §4 指定）：预测坍缩到训练可见 yaw 区间

逐样本统计「预测 yaw bin 落在该折 holdout test 块内的比例」：

```text
C3 image_only / C3 joint / C2 baseline_4dim：全部 fold 均 = 0.000
（随机情形应≈ test 块占比 ≈ 0.194）
每折预测只用到 1–36 个不同 yaw bin（远窄于 72），且全部落在训练可见区间。
```

## 4. 诊断结论（exploratory secondary，不替代 R77/R78 主判据）

1. **exact-bin yaw=0% 的机制被定位**：模型对未见过的 holdout yaw 块从不预测其内部 bin，预测系统性坍缩到训练可见 yaw 区间，故 exact-bin（要求精确命中 holdout 块内 5° 格）必然为 0。这是 strict cross-yaw 外推 + exact-bin 判据的联合结果，**不能单独读作「yaw 光度/图像信息完全不存在」**。
2. **存在弱但高于随机的粗定位**：image/joint 的 coarse45（0.18）、within6（0.26）稳定高于 chance（0.125 / 0.18），C2 OCS-only 仅 baseline_4dim 等局部 config 偶有高于随机。说明跨 yaw-block 存在弱粗粒度 yaw 残留信息，但不足以支撑 exact-bin。
3. **yaw/pitch 各向异性显著**：pitch 在三通道均远高于随机（image pitch exact 0.21、within3 0.56），yaw 接近坍缩。fixed-roll(roll=0) 下 yaw 跨块外推困难、pitch 可部分恢复。
4. **joint vs image-only 无实质互补**：所有 yaw 判据上 joint 仅微高于 image_only（coarse30 0.114 vs 0.105），pitch 反而略低；在本设定、本判据下未观测到 OCS 对图像的互补增益。
5. **C2 OCS-only 弱于 C3 含图像通道**：yaw CMAE 96.97° vs 81.4°，coarse/within 各档均更低。

## 5. 需 Codex 裁决事项

1. exact-bin 先行门是否被接受为通过（C2 65/65、C3 10/10 逐位对齐）。
2. §4 结论是否在 exploratory secondary 边界内、有无越界表述需收窄。
3. 是否据「预测坍缩 + 弱粗定位 + yaw/pitch 各向异性」进入档 B 讨论（random split / interleaved holdout 新训练），还是暂缓。档 B 仍需另行审阅，本报告不自动触发。
4. 产物当前在 `02_Claude输出/` 与 `v0.4_results/07_negative_diagnosis/`；是否纳入 `01_成果区/` 由 Codex 分流决定。

## 6. 红线确认

- 未训练、未改训练脚本、未改 split/模型/超参/seed；未跑 raw 4-dim ocs_only、未跑 `--mode all`。
- 未做后验架构/超参/特征补救；未写论文正文正式段落。
- coarse-bin/within-k/混淆矩阵/坍缩指标均标注为 exploratory secondary diagnostics，未替代 R77/R78 exact-bin 主结论。
- 未外推真实 GEO、三轴姿态、暗室实验或全模型。
