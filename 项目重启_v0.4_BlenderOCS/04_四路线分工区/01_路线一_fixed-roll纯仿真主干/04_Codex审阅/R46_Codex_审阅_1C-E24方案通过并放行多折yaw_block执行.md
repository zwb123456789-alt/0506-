# R46 Codex 审阅：1C-E24 多折 circular yaw_block 方案设计

最后更新：2026-06-24  
审阅端：Codex  
被审阅报告：`02_Claude输出/47_1C-E24_多折circular_yaw_block方案设计_Claude执行报告.md`

---

## 0. 裁决

```text
1C-E24：PASS
k=5 circular yaw_block 方案：PASS
fold 覆盖与互斥性：PASS
训练协议：PASS WITH LIMITS
下一步：1C-E25，生成多折 split 并执行 image_only 受控训练
论文正文改写：NOT RELEASED
B1 / GGX / 三轴 / 其他路线：NOT RELEASED
```

结论：E24 方案设计合格。5 折 test yaw 窗口覆盖全部 72 个 yaw bin，跨折 test 互斥无缺口；每折内部 train/val/test yaw bin 互斥；pitch 在所有 split 中保持 37/37 全覆盖。Codex 同意进入路径 B 的受控执行阶段。

下一步放行 `1C-E25`：先实现 `circ_yaw_block` split 生成并做 overlap gate；只有 overlap gate 全部通过后，才允许运行 5 折 `image_only` baseline 训练。不得扩展到 joint/ocs_only、大规模超参搜索、论文正文、B1/GGX/三轴。

---

## 1. Codex 核验

### 1.1 报告在位

```text
02_Claude输出/47_1C-E24_多折circular_yaw_block方案设计_Claude执行报告.md
```

报告明确本轮为纯方案设计：

```text
不运行训练
不生成 split manifest
不写论文正文
不启动 B1/GGX/三轴/路线二/三/四
```

### 1.2 Fold 覆盖核验

Codex 按 E24 报告给出的 fold 设计复算：

```text
fold0: test=15, val=7, train=50, testSamples=555, valSamples=259, trainSamples=1850
fold1: test=14, val=7, train=51, testSamples=518, valSamples=259, trainSamples=1887
fold2: test=14, val=7, train=51, testSamples=518, valSamples=259, trainSamples=1887
fold3: test=14, val=7, train=51, testSamples=518, valSamples=259, trainSamples=1887
fold4: test=15, val=7, train=50, testSamples=555, valSamples=259, trainSamples=1850
```

跨折 test：

```text
all_test_unique = 72
all_test_total  = 72
missing         = none
dup             = 0
```

每折 test/val overlap：

```text
overlaps_tv = 0 for fold0..fold4
```

该设计满足 R45 要求。

### 1.3 Seam 处理

Fold 1：

```text
test = 0°–65°
val  = 325°–355°
train = 70°–320°
```

这确实让 0/355 seam 进入 circular 逻辑，而不是把 seam 当作普通线性边界处理。Codex 接受该设计。

---

## 2. 通过范围

本轮通过：

- k=5 fold 数选择；
- 14/15 yaw bin test 分配；
- 7 yaw bin val 设计；
- train/val/test yaw 互斥；
- test 覆盖全圆 72 yaw bin；
- 每折 pitch 全覆盖；
- 仅跑 image_only 的训练协议；
- 输出目录规划；
- overlap gate 规划。

本轮未执行：

- split manifest 生成；
- 5 折训练；
- 指标汇总；
- 论文正文写作。

---

## 3. 执行边界

E25 允许：

1. 修改 `split_dataset.py`，新增 `--method circ_yaw_block`、`--n-folds`、`--fold`；
2. 生成 5 个 proposal/正式 split manifest；
3. 对每折执行 overlap 检查；
4. 若且仅若 5 折 overlap gate 全部通过，运行 `image_only` baseline；
5. 每折训练上限 20 epochs；
6. 单一配置：`lr=1e-3`、`seed=42`、`batch_size=32`；
7. 输出每折 checkpoint、detail JSON、summary JSON；
8. 汇总 5 折 mean/std。

E25 禁止：

- 训练 `ocs_only` 或 `joint`；
- 大规模超参搜索；
- 更改 B0 数据；
- 生成 B1/GGX 数据；
- 启动三轴/路线二/路线三/路线四；
- 写论文正文；
- 修改冻结文件 13/14/24/25；
- 将 E21 泄漏结果作为泛化证据。

---

## 4. E25 验收门槛

E25 报告必须包含：

1. `split_dataset.py` 修改说明；
2. 5 个 split manifest 路径；
3. 每折 train/val/test yaw 范围、yaw bin 数、样本数；
4. 每折 pitch 覆盖；
5. 每折内部 overlap：train∩val、train∩test、val∩test，必须为 0；
6. 跨折 test coverage：72/72 yaw bins，重复 0；
7. 每折 image_only 指标：yaw_acc、pitch_acc、circular yaw MAE、pitch MAE、within 1/3/5 bins；
8. 5 折均值 ± 标准差；
9. 若任一折 yaw_acc > 0，列出对应 yaw 区间并做谨慎解释；
10. 若所有折 yaw_acc≈0，说明 strict yaw 泛化失败为稳健负结果；
11. 红线确认。

---

## 5. 给 Claude 的下一步指令摘要

```text
执行 1C-E25：多折 circular yaw_block split 生成与 image_only 受控训练。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R46_Codex_审阅_1C-E24方案通过并放行多折yaw_block执行.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/47_1C-E24_多折circular_yaw_block方案设计_Claude执行报告.md
- 06_v0.4_code/07_training/split_dataset.py
- 06_v0.4_code/07_training/train_baseline.py
- v0.4_results/01_fullrun/postprocess/split_manifest.json

任务：
1. 修改 split_dataset.py，新增 circ_yaw_block 方法，支持 --n-folds 5 和 --fold 0..4。
2. 生成 5 个 split manifest：
   v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold0.json
   ...
   split_manifest_circ_yawblock_fold4.json
3. 先做 overlap gate：
   - 每折 train∩val=0, train∩test=0, val∩test=0
   - 跨折 test coverage=72/72 yaw bins, duplicate=0
   - pitch coverage=37/37
4. overlap gate 全部通过后，运行 image_only baseline，max_epochs=20, lr=1e-3, seed=42。
5. 每折输出 checkpoint/detail JSON；最终输出 e25_multifold_summary.json。
6. 报告写入：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/48_1C-E25_多折yaw_block训练结果_Claude执行报告.md

红线：
- 只跑 image_only。
- 不跑 ocs_only/joint。
- 不做超参搜索。
- 不写论文正文。
- 不启动 B1/GGX/三轴/路线二/三/四。
- 不改冻结文件 13/14/24/25。
- 不写 04_Codex审阅/。
- 不把 E21 泄漏结果当泛化证据。
- 不把 B1 与 GGX 混写。
```

