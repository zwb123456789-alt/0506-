# 47 1C-E24：多折 circular yaw_block 方案设计 Claude 执行报告

最后更新：2026-06-24  
执行端：Claude  
依据审阅：`04_Codex审阅/R45_Codex_审阅_1C-E23通过并建议进入多折yaw_block方案.md`

**状态：纯方案设计。不运行训练，不生成 split manifest。**

---

## 0. 设计摘要

```text
方案：k=5 折 circular yaw_block split
每折 test：14-15 个 yaw bin（严格 holdout，跨折不重叠）
每折 val：7 个 yaw bin（与 test 相邻，验证用）
每折 train：50-51 个 yaw bin（剩余全部）
训练模式：image_only baseline（≤20 epochs, lr=1e-3, seed=42）
预计 GPU 时间：~150 min（RTX 5060, 5 折 × 30 min/折）
```

---

## 1. Circular Yaw-Block Split 设计

### 1.1 设计原则

```text
P1. 每折 test 的 yaw 区间互不重叠，覆盖全部 72 个 yaw bin
P2. 每折内部 train ∩ test = 0, train ∩ val = 0, val ∩ test = 0
P3. 0°/355° seam 处使用 circular 滑动窗口，不产生边界偏置
P4. 每折 val 取与 test 相邻的 yaw bin（模拟 "已知邻近 yaw → 泛化到目标 yaw"）
P5. Pitch 在所有 split 中全覆盖（37/37 pitch bins）
P6. Split manifest 格式与现有 `split_manifest_yaw_block.json` 兼容
```

### 1.2 Yaw bin 分配

总 yaw bin：0-71（对应 0°:5°:355°，共 72 bin）。

k=5 时，72 / 5 = 14.4。分配：2 折各 15 test bin，3 折各 14 test bin。总计 2×15 + 3×14 = 72。val 统一为 7 bin/折。

Circular 滑动窗口策略——test 窗口在圆上等距分布，val 在 test 低 yaw 侧相邻：

```text
           test bins    val bins     train bins
           (count)      (count)      (count)
Fold 0:    57–71 (15)   50–56 (7)    0–49 (50)
Fold 1:    0–13  (14)   65–71 (7)    14–64 (51)    ← val wraps around
Fold 2:    14–27 (14)   7–13  (7)    28–71 + 0–6 (51)
Fold 3:    28–41 (14)   21–27 (7)    42–71 + 0–20 (51)
Fold 4:    42–56 (15)   35–41 (7)    57–71 + 0–34 (50)
```

转换为角度：

| Fold | Test yaw 范围 | Test bin 数 | Val yaw 范围 | Train yaw 范围 | Train bin 数 |
|---|---|---|---|---|---|
| 0 | 285°–355° | 15 | 250°–280° | 0°–245° | 50 |
| 1 | 0°–65° | 14 | 325°–355° | 70°–320° | 51 |
| 2 | 70°–135° | 14 | 35°–65° | 140°–355° + 0°–30° | 51 |
| 3 | 140°–205° | 14 | 105°–135° | 210°–355° + 0°–100° | 51 |
| 4 | 210°–280° | 15 | 175°–205° | 285°–355° + 0°–170° | 50 |

关键特性：

- **0°/355° seam 无偏置**：Fold 1 的 val 跨过 seam（325°–355°），Fold 1 的 test 从 0° 开始。这确保 seam 处与其他 yaw 区间被同等对待。
- **Test 区间互斥**：Fold i test ∩ Fold j test = ∅ for all i≠j。5 折覆盖全部 72 bin。
- **现有 FIX01 对照**：Fold 0 与现有 `split_manifest_yaw_block.json` 几乎一致（FIX01: test=320–355° 8 bin, val=285–315° 7 bin）。Fold 0 的方案略有不同（test=285–355° 15 bin, val=250–280° 7 bin），这是为了确保 5 折等距覆盖。

### 1.3 样本量估算

每个 yaw bin 有 37 个样本（37 pitch × 1 roll = 37）。

| Fold | Train 样本 | Val 样本 | Test 样本 | 总计 |
|---|---|---|---|---|
| 0 | 50×37 = **1850** | 7×37 = **259** | 15×37 = **555** | 2664 |
| 1 | 51×37 = **1887** | 7×37 = **259** | 14×37 = **518** | 2664 |
| 2 | 51×37 = **1887** | 7×37 = **259** | 14×37 = **518** | 2664 |
| 3 | 51×37 = **1887** | 7×37 = **259** | 14×37 = **518** | 2664 |
| 4 | 50×37 = **1850** | 7×37 = **259** | 15×37 = **555** | 2664 |

Train/val/test 比例稳定：train ≈ 69-71%, val ≈ 10%, test ≈ 19-21%。

### 1.4 Pitch 覆盖

所有 split 的 pitch 覆盖完全相同：37/37 pitch bins (-90°:5°:+90°)。这是因为切分在 yaw 维度上进行，每个 yaw bin 内包含全部 37 个 pitch。

```text
每折 train: pitch 37/37, yaw 50-51/72
每折 val:   pitch 37/37, yaw 7/72
每折 test:  pitch 37/37, yaw 14-15/72
```

这意味着 pitch 不是泛化测试的障碍——pitch 信息在训练中已全覆盖，strict holdout 仅针对 yaw。

---

## 2. 与现有 FIX01 的对照关系

| | FIX01 (E21-FIX01) | 多折 Fold 0 | 多折 Fold 1-4 |
|---|---|---|---|
| Train yaw | 0–280° (57 bin) | 0–245° (50 bin) | 各异 |
| Test yaw | 320–355° (8 bin) | 285–355° (15 bin) | 各异，覆盖全圆 |
| Val yaw | 285–315° (7 bin) | 250–280° (7 bin) | 各异 |
| 泛化类型 | 低→高 yaw | 低→高 yaw | 全圆各方向 |
| 与 FIX01 可比 | — | 部分可比（更宽 test） | 互补（覆盖 FIX01 未测的方向） |

**解释**：

- Fold 0 的 train=0–245°, test=285–355° 是 FIX01 的 "加强版"（train yaw 范围更窄、test yaw 范围更宽），使泛化测试更严苛。
- Fold 1 的 test=0–65° 测试 "高 yaw 知识 → 低 yaw 泛化" 的反方向。
- Fold 2-4 覆盖中间 yaw 区间的泛化。
- 所有折的结论可聚合为 "跨未见 yaw 泛化" 的 cross-validation 级证据。

---

## 3. Overlap 检查规则

### 3.1 每折内部 overlap

对每折 i 的 split manifest 使用 `train_baseline.py` 内置的 `check_record_overlap()`：

```text
要求：train_i ∩ val_i = 0
      train_i ∩ test_i = 0
      val_i ∩ test_i = 0
```

按 yaw bin 分配方案，这些条件自动满足（train/val/test 的 yaw bin 互不重叠）。

### 3.2 跨折 test overlap

5 折的 test yaw bins 覆盖全部 72 bin 且互不重叠：

```text
Fold 0 test (57-71) ∩ Fold 1 test (0-13)  = 0
Fold 0 test (57-71) ∩ Fold 2 test (14-27) = 0
...对所有 i≠j: test_i ∩ test_j = 0
```

### 3.3 跨折 train/test overlap 与 leakage 检查

给定 Fold i 的 train 与 Fold j 的 test 在 yaw bin 层面有重叠（例如 Fold 0 的 train 包含 bin 0-49，Fold 1 的 test 包含 bin 0-13）。这是设计上的期望行为——不同折之间会共享样本，但**同一折内部 train 与 test 不重叠**。每折是一个独立的 strict holdout 实验。

```text
规则：每折内部必须 0 overlap。
跨折 overlap 正常，且用于验证 yaw bin 覆盖的完备性。
```

---

## 4. 训练协议

### 4.1 模式与配置

沿用 FIX01 的受控边界，但只跑 image_only（最高性价比验证 yaw 泛化）：

```text
mode:        image_only
max_epochs:  20
lr:          1e-3
seed:        42 (per fold)
batch_size:  32
device:      auto (GPU)
num_workers: 4
val_max:     0 (full val，因为每折 val 仅 259 samples)
```

只跑 image_only 的理由：
- ocs_only 在 FIX01 中 yaw_acc=0%，多折不会改变结论；
- joint 在 FIX01 strict holdout 上 pitch 反而不如 image_only；
- image_only 是最干净的单通道 yaw 泛化测试，5 折结果可直接进入论文消融章。

### 4.2 输出目录结构

```text
v0.4_results/03_training_baseline/e24_multifold_yawblock/
├── split_manifest_circ_yawblock_fold0.json
├── split_manifest_circ_yawblock_fold1.json
├── split_manifest_circ_yawblock_fold2.json
├── split_manifest_circ_yawblock_fold3.json
├── split_manifest_circ_yawblock_fold4.json
├── e24_overlap_report.json                        ← 5 折 overlap 汇总
├── fold0/
│   ├── checkpoint_image_only.pt
│   ├── e24_fold0_results.json
│   └── e24_fold0_detail_image_only.json
├── fold1/
│   └── ...
├── fold2/
│   └── ...
├── fold3/
│   └── ...
├── fold4/
│   └── ...
└── e24_multifold_summary.json                     ← 5 折汇总
```

### 4.3 汇总报告结构 (`e24_multifold_summary.json`)

```json
{
  "task": "1C-E24 multi-fold circular yaw_block",
  "config": {
    "k_folds": 5,
    "mode": "image_only",
    "max_epochs": 20,
    "lr": 0.001,
    "seed": 42
  },
  "per_fold": {
    "fold_0": {
      "test_yaw_range": "285–355 deg",
      "test_n_bins": 15,
      "train_n": 1850, "val_n": 259, "test_n": 555,
      "overlap_strict": true,
      "results": {}
    }
    // ... fold_1 to fold_4
  },
  "aggregate": {
    "mean_yaw_acc": null,
    "std_yaw_acc": null,
    "mean_pitch_acc": null,
    "std_pitch_acc": null,
    "mean_yaw_cmae": null,
    "folds_with_yaw_gt_0": null,
    "conclusion": null
  }
}
```

### 4.4 训练脚本扩展

`train_baseline.py` 已支持 `--train-split-manifest`，可直接复用于多折训练。每折运行：

```powershell
python train_baseline.py --train --mode image_only --max-epochs 20 \
    --train-split-manifest split_manifest_circ_yawblock_fold0.json \
    --eval-random-manifest split_manifest.json \
    --outdir e24_multifold_yawblock/fold0
```

无需修改训练脚本。

### 4.5 Split 生成脚本扩展

需要在 `split_dataset.py` 中新增方法 `--method circ_yaw_block`：

```python
# 新增 CLI:
#   python split_dataset.py --method circ_yaw_block --n-folds 5 --fold 0
#   python split_dataset.py --method circ_yaw_block --n-folds 5 --fold 1
#   ...

def split_circ_yaw_block(table, n_folds=5, fold=0):
    """
    k-fold circular yaw_block split。
    每折 test 为圆周上等距分布的一个连续 yaw 窗口，
    val 为 test 相邻的 yaw 窗口，train 为其余。
    """
    yaw_bins = sorted(set(r["yaw_idx"] for r in table))  # 0..71
    n_yaw = len(yaw_bins)

    # 每折 test bin 数：尽量均匀
    test_sizes = []
    base = n_yaw // n_folds   # 14
    extra = n_yaw % n_folds   # 2 (fold 0 和 fold 4 多 1 个)
    for i in range(n_folds):
        test_sizes.append(base + (1 if i < extra else 0))
    # test_sizes = [15, 14, 14, 14, 15]

    val_size = 7  # 固定，约 10% of 72

    # Fold i: test 窗口从 start_bin 开始
    start_bin = sum(test_sizes[:fold]) % n_yaw
    test_end = (start_bin + test_sizes[fold]) % n_yaw

    # 处理 circular
    if test_end > start_bin:
        test_bins = set(range(start_bin, test_end))
    else:
        test_bins = set(range(start_bin, n_yaw)) | set(range(0, test_end))

    # val: test 窗口的低 yaw 侧相邻 7 bin (circular)
    val_start = (start_bin - val_size) % n_yaw
    if val_start < start_bin:
        val_bins = set(range(val_start, start_bin))
    else:
        val_bins = set(range(val_start, n_yaw)) | set(range(0, start_bin))

    train_bins = set(yaw_bins) - test_bins - val_bins

    train = [r for r in table if r["yaw_idx"] in train_bins]
    val = [r for r in table if r["yaw_idx"] in val_bins]
    test = [r for r in table if r["yaw_idx"] in test_bins]
    return train, val, test
```

---

## 5. 计算成本估算

基于 image_only 在 RTX 5060 GPU 上的实测数据（FIX01 smoke: 1 epoch ≈ 36s, 20 epochs ≈ 731s on CPU → GPU 预计 ~30-40s/epoch）：

| 项目 | 单折 | 5 折总计 |
|---|---|---|
| Training (20 epochs) | ~10 min | ~50 min |
| Final eval (3 test sets) | ~1 min | ~5 min |
| Overlap check | <1 s | <5 s |
| Split generation | <5 s | <30 s |
| **总计** | **~11 min** | **~55 min** |

保守估计（含数据加载 I/O 开销）：**~150 min（2.5 小时）**。

对比：
- FIX01 CPU 三模式：~1538s（~26 min）→ GPU 预计大幅缩短
- B1 fullrun 2664 渲染：以天计
- 路径 C OCS 特征实验：<30 min

路径 B 的计算成本处于 "可在一个下午完成" 的量级。

---

## 6. 预期结果与解读框架

### 6.1 如果 5 折 yaw_acc 全部为 0%

```text
结论：跨未见 yaw 零样本泛化失败是稳健的，不依赖特定 yaw 留出区间。
含义：
  - 当前 CNN + fixed-roll + B0 架构确实不具备 yaw 不变性。
  - 负结果可作为论文消融章的 strong negative evidence。
  - 后续优先转向 D1（B1 对比）或 C（OCS 特征增强），
    不在 yaw 泛化方向上继续投入。
```

### 6.2 如果部分折 yaw_acc > 0%

```text
结论：yaw 泛化存在角度依赖性——某些 yaw 区间比其他区间更容易泛化。
含义（举例）：
  - 若 Fold 0 (test=285–355°) yaw=0% 但 Fold 1 (test=0–65°) yaw>0%：
    → 模型在低 yaw 区间学到的特征可以泛化到未见低 yaw，但不能跨越到高 yaw。
  - 若某折 yaw>0%：
    → 定位哪些 yaw 区间的图像特征更具跨 yaw 可迁移性，
      可作为后续 C（OCS 特征）或 D1（B1）的靶向指导。
```

### 6.3 汇总指标

```text
报告内容（per fold + aggregate）：
  - yaw_acc, pitch_acc, yaw_circular_mae, pitch_mae
  - yaw error bin distribution (within_0/1/3/5 bins)
  - per-yaw breakdown (只在 seen yaw 上有意义)
  - overlap verification
  - 5 折均值 ± 标准差
```

---

## 7. 红线确认

- [x] 不运行训练（纯方案设计）
- [x] 不生成 split manifest（如需生成测试代码，标记为 PROPOSAL）
- [x] 不写论文正文
- [x] 不启动 B1/GGX/三轴/路线二/三/四
- [x] 不改冻结文件 13/14/24/25
- [x] 不写 04_Codex审阅/
- [x] 不把 E21 泄漏结果当泛化证据
- [x] 不把 B1 与 GGX 混写

---

## 附录 A：circ_yaw_block 伪代码

```python
def generate_circ_yaw_block_folds(table, n_folds=5, val_size=7):
    """
    生成 k-fold circular yaw_block split manifests。
    返回 list of (train, val, test) tuples。
    """
    yaw_bins = sorted(set(r["yaw_idx"] for r in table))  # 0..71
    n_yaw = len(yaw_bins)

    # 每折 test bin 分配
    test_sizes = [n_yaw // n_folds + (1 if i < n_yaw % n_folds else 0)
                  for i in range(n_folds)]

    folds = []
    for fold in range(n_folds):
        # test window
        start = sum(test_sizes[:fold]) % n_yaw
        end = (start + test_sizes[fold]) % n_yaw
        if end > start:
            test_bins = set(range(start, end))
        else:
            test_bins = set(range(start, n_yaw)) | set(range(0, end))

        # val window (adjacent, low-yaw side, circular)
        val_start = (start - val_size) % n_yaw
        if val_start < start:
            val_bins = set(range(val_start, start))
        else:
            val_bins = set(range(val_start, n_yaw)) | set(range(0, start))

        train_bins = set(yaw_bins) - test_bins - val_bins

        train = [r for r in table if r["yaw_idx"] in train_bins]
        val = [r for r in table if r["yaw_idx"] in val_bins]
        test = [r for r in table if r["yaw_idx"] in test_bins]
        folds.append((train, val, test))

    return folds
```

## 附录 B：与现有单折 yaw_block 的差异

| | FIX01 单折 | E24 多折 |
|---|---|---|
| 折数 | 1 | 5 |
| Test yaw 覆盖 | 320–355° (8 bin) | 全部 72 bin (5 折合计) |
| 泛化方向 | 仅低→高 | 全圆周各方向 |
| 证据强度 | 单点观测 | cross-validation |
| 论文用途 | 初步负结果 | 消融章稳健负结果/分析 |
| 代码改动 | 无（已完成） | `split_dataset.py` 新增 ~30 行 |
| 训练改动 | 无 | 无（复用 `train_baseline.py`） |
