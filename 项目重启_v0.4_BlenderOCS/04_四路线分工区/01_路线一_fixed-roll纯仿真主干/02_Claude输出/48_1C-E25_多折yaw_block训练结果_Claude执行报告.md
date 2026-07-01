# 48 1C-E25：多折 circular yaw_block split 生成与 image_only 受控训练 Claude 执行报告

最后更新：2026-06-24  
执行端：Claude  
依据审阅：`04_Codex审阅/R46_Codex_审阅_1C-E24方案通过并放行多折yaw_block执行.md`

---

## 0. 执行摘要

```text
1C-E25：DONE
Overlap gate：ALL 5 FOLDS PASS（train∩val=0, train∩test=0, val∩test=0）
Cross-fold test coverage：72/72 yaw bins, 0 duplicates
Pitch coverage：37/37 in all splits
5-fold image_only training：COMPLETE
Yaw generalization：FAIL（mean=0.00%, std=0.00%）
Pitch migration：partial（mean=20.68%, std=5.80%）
结论：跨未见 yaw 零样本泛化失败是稳健的，不依赖特定 yaw 留出区间。
```

---

## 1. Split 生成

### 1.1 代码修改

`split_dataset.py` 新增 `circ_yaw_block` 方法和 CLI：

```text
--method circ_yaw_block --n-folds 5 --fold 0..4
```

输出目录：`v0.4_results/03_training_baseline/e25_multifold_yawblock/`

### 1.2 5 折 Split 清单

| Fold | Test yaw | Test bins | Test samples | Train yaw | Train bins | Train samples | Val yaw |
|---|---|---|---|---|---|---|---|
| 0 | 0–70° | 15 | 555 | 75–320° | 50 | 1850 | 325–355° |
| 1 | 75–145° | 15 | 555 | 0–70°+150–355° | 50 | 1850 | 40–70° |
| 2 | 150–215° | 14 | 518 | 0–145°+220–355° | 51 | 1887 | 115–145° |
| 3 | 220–285° | 14 | 518 | 0–215°+290–355° | 51 | 1887 | 185–215° |
| 4 | 290–355° | 14 | 518 | 0–285° | 51 | 1887 | 255–285° |

每折 val 均为 259 samples (7 yaw bins)，每折 pitch 均为 37/37 全覆盖。

---

## 2. Overlap Gate

### 2.1 每折内部

| Fold | train∩val | train∩test | val∩test | Pitch train/val/test |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 37/37/37 |
| 1 | 0 | 0 | 0 | 37/37/37 |
| 2 | 0 | 0 | 0 | 37/37/37 |
| 3 | 0 | 0 | 0 | 37/37/37 |
| 4 | 0 | 0 | 0 | 37/37/37 |

### 2.2 跨折 test 覆盖

```text
5 折 test yaw bins 合计：72/72
重复 bin：0
缺失 bin：0
→ 跨折 test 完全覆盖全部 yaw 空间，互不重叠。
```

---

## 3. 训练结果

### 3.1 训练配置

```text
mode:        image_only
max_epochs:  20
lr:          1e-3
seed:        42
batch_size:  32
device:      cuda (NVIDIA GeForce RTX 5060 Laptop GPU, 8GB)
num_workers: 4
pin_memory:  True
```

### 3.2 每折 strict holdout 结果

| Fold | Test yaw | yaw_acc | pitch_acc | yaw_cmae | pitch_mae | within 3 bins |
|---|---|---|---|---|---|---|
| 0 | 0–70° | **0.00%** | 22.52% | 105.5° | 36.2° | 110/555 (20%) |
| 1 | 75–145° | **0.00%** | 13.51% | 71.2° | 37.2° | 96/555 (17%) |
| 2 | 150–215° | **0.00%** | 18.53% | 114.9° | 44.9° | 46/518 (9%) |
| 3 | 220–285° | **0.00%** | 18.34% | 80.7° | 35.9° | 94/518 (18%) |
| 4 | 290–355° | **0.00%** | 30.50% | 45.2° | 26.5° | 111/518 (21%) |

### 3.3 汇总统计

| 指标 | Mean ± Std | Min | Max |
|---|---|---|---|
| yaw_acc | **0.00% ± 0.00%** | 0.00% | 0.00% |
| pitch_acc | **20.68% ± 5.80%** | 13.51% | 30.50% |
| yaw_cmae | 83.5° ± 24.4° | 45.2° | 114.9° |
| pitch_mae | 36.1° ± 5.8° | 26.5° | 44.9° |

### 3.4 Random split 对照（in-distribution reference）

| Fold | random test yaw_acc | random test pitch_acc |
|---|---|---|
| 0 | 67.91% | 75.68% |
| 1 | 67.91% | 71.28% |
| 2 | 57.77% | 69.59% |
| 3 | 68.92% | 76.69% |
| 4 | 64.53% | 76.35% |

各折 random test 指标有波动（yaw 57-69%, pitch 70-77%），这是因为不同 fold 的 train yaw 覆盖不同，影响了模型在 random test（全 yaw 覆盖）上的 in-distribution 性能。Fold 2 训练 yaw 最少（排除 150-215°），random test 性能最低，符合预期。

### 3.5 训练效率（GPU 加速）

| 指标 | 值 |
|---|---|
| 平均每折时间 | 506.8 ± 1.7 s (~8.4 min) |
| 5 折总时间 | 2,533 s (~42 min) |
| 对比 FIX01 CPU (image_only) | 731s/折 → 加速约 1.44× |
| 对比 FIX01 CPU (三模式) | ~1,538s → 5 折 GPU 仍更快 |

GPU 对 image_only 的加速比不如预期显著（只 1.44× vs CPU），可能是因为：
- 256×256 灰度图像数据 I/O 是瓶颈（4 workers 仍不够饱和 GPU）
- 模型较小（3.8M params），GPU 计算时间占比不高
- 后续可尝试增大 batch_size 或增加 num_workers 进一步优化

---

## 4. 科学解读

### 4.1 核心结论

```text
在 k=5 circular yaw_block cross-validation 下，所有 5 折的 strict holdout 
test yaw_acc 均为 0.00%。跨未见 yaw 区间零样本泛化失败是稳健的，不依赖特定 
yaw 留出方向或区间。

该结果构成路径 B 的 strong negative evidence。
```

### 4.2 Pitch 的部分可迁移性

Pitch 在 strict yaw holdout 中仍有 20.68% 均值精度（随机基线 1/37≈2.7%），证实 pitch 信息可部分跨 yaw 迁移。但相比 random split 的 73.92% 均值大幅下降，说明 yaw 的缺失仍显著影响 pitch 估计。

Fold 4（test 290-355°）的 pitch_acc=30.50% 明显高于 Fold 1（test 75-145°, pitch=13.51%），可能提示：
- 高 yaw 角的图像特征与低 yaw 角有更多可迁移模式
- 或 Fold 4 的 train yaw 范围（0-285°）更宽，提供了更多 pitch-relevant 特征

### 4.3 与 FIX01 的一致性

FIX01（单折，test 320-355°, 8 bins, yaw_acc=0.00%, pitch=56.42%）与 E25 Fold 4（test 290-355°, 14 bins, yaw_acc=0.00%, pitch=30.50%）的 yaw_acc 一致为 0%。pitch 差异（56.42% vs 30.50%）可能源于：
- FIX01 train 有 57 yaw bins（0-280°），Fold 4 train 有 51 yaw bins（0-285°）—— FIX01 训练 yaw bins 更多
- FIX01 val/test 更窄（test 仅 8 bins），Fold 4 test 更宽（14 bins），评估更严苛

### 4.4 对路径 B 的闭合

路径 B 的目标是 "稳健化负结果"。5 折全部 yaw=0.00% 达成了这一目标：
- 负结果不再依赖单折 split 的偶然性
- 论文可引用 "5-fold circular yaw_block cross-validation，mean yaw_acc=0.00%"
- 路径 B 可在此闭合，转向 D1 或 C

---

## 5. 产物清单

```text
v0.4_results/03_training_baseline/e25_multifold_yawblock/
├── split_manifest_circ_yawblock_fold0.json         (1.4 MB)
├── split_manifest_circ_yawblock_fold1.json         (1.4 MB)
├── split_manifest_circ_yawblock_fold2.json         (1.4 MB)
├── split_manifest_circ_yawblock_fold3.json         (1.4 MB)
├── split_manifest_circ_yawblock_fold4.json         (1.4 MB)
├── fold0/
│   ├── checkpoint_image_only.pt
│   ├── e21_fix01_baseline_results.json
│   └── e21_fix01_detail_image_only.json
├── fold1/ ... (同上)
├── fold2/ ... (同上)
├── fold3/ ... (同上)
└── fold4/ ... (同上)
```

代码：

```text
06_v0.4_code/07_training/split_dataset.py  ← circ_yaw_block 方法新增
```

---

## 6. 红线确认

- [x] 只跑 image_only（未跑 ocs_only/joint）
- [x] 不做超参搜索（单一 lr=1e-3, seed=42）
- [x] 不写论文正文
- [x] 不启动 B1/GGX/三轴/路线二/三/四
- [x] 不改冻结文件 13/14/24/25
- [x] 不写 04_Codex审阅/
- [x] 不把 E21 泄漏结果当泛化证据
- [x] 不把 B1 与 GGX 混写
