# R48 Codex 审阅：1C-E25-FIX01 成果包补正通过

最后更新：2026-06-25  
审阅端：Codex  
被审阅材料：

- `02_Claude输出/49_1C-E25-FIX01_成果包补正_Claude执行报告.md`
- `v0.4_results/03_training_baseline/e25_multifold_yawblock/e25_multifold_summary.json`
- `v0.4_results/03_training_baseline/e25_multifold_yawblock/e25_overlap_report.json`
- `06_v0.4_code/07_training/split_dataset.py`
- `06_v0.4_code/07_training/train_baseline.py`

---

## 0. 结论

```text
1C-E25-FIX01：PASS
成果包补正：PASS
主结论保持不变：
5-fold circular yaw_block cross-validation 下 yaw_acc mean=0.00%, std=0.00%
```

R47 要求的 4 个 finding 已全部闭合，且补正后的成果包与代码改动说明一致，可作为路径 B 的稳健负结果证据包继续使用。

---

## 1. 审阅要点

### 1.1 总汇总 JSON

已确认存在：

- `v0.4_results/03_training_baseline/e25_multifold_yawblock/e25_multifold_summary.json`

内容与执行报告一致，包含：

- 5 个 fold 的逐折结果
- `yaw_acc_mean = 0.0`
- `yaw_acc_std_population = 0.0`
- `yaw_acc_std_sample = 0.0`
- `pitch_acc_std_population = 0.0567997929...`，即 5.68%
- `pitch_acc_std_sample = 0.0635040991...`，即 6.35%

### 1.2 overlap report

已确认存在：

- `v0.4_results/03_training_baseline/e25_multifold_yawblock/e25_overlap_report.json`

其结论与执行报告一致：

- 5 个 fold 的 `train/val/test` 内部重叠均为 0
- `overall_strict = true`
- cross-fold test coverage 覆盖 `72/72` yaw bins
- duplicates = 0

### 1.3 代码改动清单

两处代码改动与执行报告一致：

- `split_dataset.py`
  - 新增 `circ_yaw_block` 切分
  - 支持 `--n-folds` / `--fold`
  - 输出 E25 专用 fold manifest
- `train_baseline.py`
  - 新增 strict holdout / overlap check 支持
  - 支持 `--train-split-manifest`
  - 支持额外 eval manifest
  - 支持 `--device auto`、`--num-workers`、`pin_memory`

---

## 2. 结论边界

本轮仅确认成果包补正完整，不重新训练，不改原始训练数值，不扩展到 `ocs_only` / `joint`，也不触发 B1 / GGX / 三轴 / 路线二三四。

---

## 3. 残余风险

审阅基于现有落盘文件与代码 diff，没有重新跑训练。若后续有人手工改写 JSON 或报告，需重新做一次文件级复核。

