# 49 1C-E25-FIX01：成果包补正 Claude 执行报告

最后更新：2026-06-25  
执行端：Claude  
依据审阅：`04_Codex审阅/R47_Codex_审阅_1C-E25条件通过并要求成果包补正.md`  
状态：**只补产物，未重训**

---

## 0. FIX 摘要

```text
Finding 1：缺少 e25_multifold_summary.json       → FIXED
Finding 2：每折 overlap report 为空              → FIXED
Finding 3：报告代码改动清单不完整                  → FIXED（§4）
Finding 4：pitch_acc std 统计口径 + 编码问题      → FIXED（§5）
主结论：yaw_acc mean=0.00%, std=0.00% 不变
```

---

## 1. Finding 1 — 生成总汇总 JSON

**问题**：R46 要求输出 `e25_multifold_summary.json`，但 E25 未落地。

**处理**：从现有 5 折 `e21_fix01_baseline_results.json` 和 `e21_fix01_detail_image_only.json` 聚合生成。

**产物**：[e25_multifold_summary.json](../../../v0.4_results/03_training_baseline/e25_multifold_yawblock/e25_multifold_summary.json)

内容结构：

```json
{
  "task": "1C-E25 multi-fold circular yaw_block",
  "config": { "k_folds": 5, "mode": "image_only", ... },
  "per_fold": {
    "fold_0": { "test_yaw_range": "0-70 deg", "test_n_bins": 15,
                "test_primary": { "yaw_acc": 0.0, "pitch_acc": 0.2252, ... }, ... },
    ...
  },
  "aggregate": {
    "yaw_acc_mean": 0.0,
    "yaw_acc_std_population": 0.0,
    "yaw_acc_std_sample": 0.0,
    "pitch_acc_mean": 0.2068,
    "pitch_acc_std_population": 0.0568,
    "pitch_acc_std_sample": 0.0635,
    "folds_with_yaw_gt_0": 0,
    "conclusion": "5-fold cross-validation: mean yaw_acc=0.00%, all folds=0%."
  }
}
```

---

## 2. Finding 2 — 补写 Overlap 证据

**问题**：每折 `e21_fix01_overlap_report.json` 为 `{}`（空 JSON），且缺少总 overlap report。

**处理**：从 5 个 `split_manifest_circ_yawblock_fold*.json` 重新计算 record_id overlap。

**产物**：

- 总报告：[e25_overlap_report.json](../../../v0.4_results/03_training_baseline/e25_multifold_yawblock/e25_overlap_report.json)
- 每折报告：
  - `fold0/e21_fix01_overlap_report.json`
  - `fold1/e21_fix01_overlap_report.json`
  - `fold2/e21_fix01_overlap_report.json`
  - `fold3/e21_fix01_overlap_report.json`
  - `fold4/e21_fix01_overlap_report.json`

Overlap 结果（全部通过）：

| Fold | train&val | train&test | val&test | Strict |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | true |
| 1 | 0 | 0 | 0 | true |
| 2 | 0 | 0 | 0 | true |
| 3 | 0 | 0 | 0 | true |
| 4 | 0 | 0 | 0 | true |

跨折 test 覆盖：**72/72 yaw bins，重复 0**。

---

## 3. Finding 3 — 代码改动清单补全

### 3.1 `split_dataset.py` 改动

新增 `--method circ_yaw_block` 支持：

- 新增函数 `split_circ_yaw_block(table, n_folds=5, fold=0, val_size=7)`：将 72 yaw bin 在圆周上等距分为 k 个 test 窗口，每折 test 窗口互斥、合计覆盖全部 yaw bin
- 新增 CLI 参数：`--n-folds`（默认 5）、`--fold`（0..4）
- 修改 `main()` 分支：`circ_yaw_block` 方法自动输出到 `e25_multifold_yawblock/` 目录
- 约 +50 行

### 3.2 `train_baseline.py` 改动（FIX01 阶段已落地，E25 复用）

FIX01 阶段（E21-FIX01）已对 `train_baseline.py` 做以下改动，E25 直接复用：

- **`--train-split-manifest`**：显式指定训练用 split manifest
- **`--eval-random-manifest` / `--eval-yaw-block-manifest`**：额外评估 manifest
- **`check_record_overlap()` / `check_cross_manifest_overlap()`**：overlap 检查函数
- **`--device auto`**：自动检测 CUDA GPU（默认）
- **`--num-workers 4`**：多线程 DataLoader（默认）
- **`pin_memory=True`**：GPU 加速数据传输
- **`--skip-overlap-check`**：可选跳过 overlap 检查（E25 使用）

约 +120 行改动（含 overlap 函数 ~60 行、CLI 参数 ~20 行、device/workers 逻辑 ~30 行、data loading 重构 ~10 行）。

### 3.3 E25 代码资产总结

```text
06_v0.4_code/07_training/split_dataset.py  ← E25 新增 circ_yaw_block 方法
06_v0.4_code/07_training/train_baseline.py  ← E21-FIX01 增强版，E25 复用
```

---

## 4. Finding 4 — 统计口径修正

### 4.1 pitch_acc std

从原始 JSON `test_primary.pitch_acc` 直接计算：

```text
pitch_acc values: [0.2252, 0.1351, 0.1853, 0.1834, 0.3050]

population std (ddof=0) = 0.0568 → 5.68%
sample std     (ddof=1) = 0.0635 → 6.35%
```

E25 报告中写 `pitch_acc std = 5.80%` 有误。正确值应使用 **population std = 5.68%**（描述 5 折本身的离散度，不推广到更大总体）。若需推广到"重复 5-fold CV 的预期方差"则用 sample std = 6.35%。

**E25 主结论不受此修正影响**：yaw_acc mean=0.00%, std=0.00%（两种统计口径均为 0）。

### 4.2 编码问题

E25 报告源文件为 UTF-8 编码，在支持 UTF-8 的编辑器中显示正常。Windows 终端 GBK 编码下部分特殊字符（连接符、度符号、数学符号）显示为乱码，不影响源文件内容。后续终端输出可设置 `PYTHONIOENCODING=utf-8` 缓解。

---

## 5. 补正后产物清单

```text
v0.4_results/03_training_baseline/e25_multifold_yawblock/
├── split_manifest_circ_yawblock_fold0.json      ← E25 原产物
├── split_manifest_circ_yawblock_fold1.json      ← E25 原产物
├── split_manifest_circ_yawblock_fold2.json      ← E25 原产物
├── split_manifest_circ_yawblock_fold3.json      ← E25 原产物
├── split_manifest_circ_yawblock_fold4.json      ← E25 原产物
├── e25_multifold_summary.json                   ← [FIX01 新增]
├── e25_overlap_report.json                      ← [FIX01 新增]
├── fold0/
│   ├── checkpoint_image_only.pt                 ← E25 原产物
│   ├── e21_fix01_baseline_results.json          ← E25 原产物
│   ├── e21_fix01_detail_image_only.json         ← E25 原产物
│   └── e21_fix01_overlap_report.json            ← [FIX01 补写]
├── fold1/ ... (同上)
├── fold2/ ... (同上)
├── fold3/ ... (同上)
└── fold4/ ... (同上)
```

---

## 6. 红线确认

- [x] 不重训（纯聚合已有数据）
- [x] 不改原始训练结果数值
- [x] 不跑 ocs_only/joint
- [x] 不做超参搜索
- [x] 不写论文正文
- [x] 不启动 B1/GGX/三轴/路线二/路线三/路线四
- [x] 不改冻结文件
- [x] 不写 04_Codex审阅/
- [x] E25 主结论不变：yaw_acc mean=0.00%, std=0.00%
