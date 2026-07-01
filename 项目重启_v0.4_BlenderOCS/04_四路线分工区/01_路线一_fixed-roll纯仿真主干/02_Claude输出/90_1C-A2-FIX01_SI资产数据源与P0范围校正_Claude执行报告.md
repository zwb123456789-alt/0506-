# 90_1C-A2-FIX01：SI 资产数据源与 P0 范围校正执行报告

执行时间：2026-06-29  
任务编号：1C-A2-FIX01（头A 第二步修正）  
执行端：Claude  
审阅依据：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
  R87_Codex_审阅_1C-A2需FIX01_SI资产数据源与范围校正.md
```

---

## 1. 任务目标

按 R87，对 88 号 SI 资产补齐需求评估中的数据源路径和 P0 资产范围进行校正。R87 正确指出 88 中使用了不存在的路径（`training_log.csv`、`split_metadata.json`、`final_metrics.test`）和错误的 C3 目录（`06_c3_joint_imaging` 应为 `06_c3_preflight`）。

---

## 2. 已修正的路径对照

### 2.1 数据源路径修正

| 88 原路径（已废止） | FIX01 校正路径 | 数据内容 |
|---|---|---|
| `v0.4_results/05_c2_screening/*/training_log.csv` | `v0.4_results/05_c2_screening/*/<config>_fold*_checkpoint.pt` | C2 训练历史在 checkpoint.pt 的 `history` 字段中（30 epochs） |
| `v0.4_results/06_c3_joint_imaging/c3_fold*/training_log.csv` | `v0.4_results/06_c3_preflight/c3_image_formal_5fold/fold*/checkpoint_image_only.pt`<br>`v0.4_results/06_c3_preflight/c3_joint_formal_5fold/fold*/checkpoint_joint.pt` | C3 训练历史在 checkpoint.pt 的 `history` 字段中；val 为嵌套 dict（`['val']['primary']` 等） |
| `v0.4_results/*/split_metadata.json` | `v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold*.json`<br>`v0.4_results/06_c3_preflight/c3_*_formal_5fold/fold*/e21_fix01_overlap_report.json` | split manifest 含 per-sample yaw_idx 分配；overlap report 含严格 overlap 诊断 |
| `v0.4_results/06_c3_joint_imaging/c3_fold*/final_metrics.test` | `v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.json`<br>`v0.4_results/06_c3_preflight/c3_*_formal_5fold/fold*/e21_fix01_detail_*.json` | C3 per-fold 完整指标 |

### 2.2 其他可用数据文件（供参考）

```text
v0.4_results/05_c2_screening/*/*_fold*_result.json          ← C2 per-fold 最终指标（不含逐 epoch 曲线）
v0.4_results/05_c2_screening/supplementary_table_s2_per_fold_results.csv  ← Table S2（E36 产出）
v0.4_results/06_c3_preflight/c3_image_formal_5fold/fold*/e21_fix01_baseline_results.json  ← C3 fold 汇总
v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c2_extended_metrics.json        ← C2 extended（65 runs）
v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.csv          ← C3 extended CSV
```

---

## 3. P0 资产范围校正

### 3.1 Figure S3 口径

R87 指出 `C2 result.json` 不含逐 epoch 训练曲线，不应声称 `training_log.csv` 已具备。

**实际发现**（A2-GEN 执行时已验证）：
- C2 checkpoint.pt 中的 `history` 字段包含完整的 30-epoch train loss + val metrics
- 通过 `torch.load` 可读取，不需要 `training_log.csv`
- Figure S3 C2 部分**仍可生成**完整的逐 epoch 曲线

**FIX01 校正**：
- ✓ Figure S3 保留为 P0，包含 C2（3 configs）+ C3（image 5 + joint 5）
- ✓ 明确数据源为 checkpoint.pt 的 `history` 字段
- ✓ 不声称存在 `training_log.csv`

### 3.2 Figure S4 口径

**FIX01 校正**：
- ✓ Figure S4 保留为 P0
- ✓ 数据源改为 split manifest + overlap report
- ✓ 不声称存在 `split_metadata.json`

### 3.3 Table S3 口径

**FIX01 校正**：
- ✓ Table S3 保留为 P0
- ✓ 数据源优先使用 `c3_extended_metrics.json/csv`
- ✓ 不声称存在 `final_metrics.test`

---

## 4. 88 号文件修正清单

对 `88_1C-A2_SI资产补齐需求评估_Claude执行报告.md` 进行了以下修正：

| 修正段落 | 修正内容 |
|---------|---------|
| 文件头 | 标注 FIX01 校正版，添加 R87 依据 |
| §3.2 数据可用性核查 | 替换全部不存在的路径为真实路径；添加已废止路径清单 |
| §4.1（Figure S3） | 添加数据源说明（checkpoint.pt history 字段）；注明 C2 result.json 无逐 epoch 曲线但 checkpoint 有 |
| §4.1（Figure S4） | 添加数据源（split manifest + overlap report） |
| §5.1 允许操作 | 替换 `training_log.csv`/`split_metadata.json`/`final_metrics.test` 为真实文件名 |
| §7.3 工作量估算 | 替换数据路径 |
| §9 下一步提示词 | 替换全部数据源路径；添加完整路径清单和 R87 依据 |

---

## 5. 与 A2-GEN（89 号）的关系

**重要说明**：A2-GEN（89 号）已在 FIX01 之前执行，但**实际使用的是正确的数据源**（checkpoint.pt history、split manifest、c3_extended_metrics.json），因为我们在执行过程中进行了实时核查和调试。

| 项 | 88 原声明 | A2-GEN 实际使用 | 是否一致 |
|----|---------|---------------|:---:|
| C2 训练曲线数据 | training_log.csv | checkpoint.pt history (torch.load) | ✗（路径不同，但 A2-GEN 用对了） |
| C3 训练曲线数据 | 06_c3_joint_imaging/ | 06_c3_preflight/ checkpoint_*.pt | ✗（目录不同，但 A2-GEN 用对了） |
| Split 数据 | split_metadata.json | split_manifest_circ_yawblock_fold*.json | ✗（文件名不同，但 A2-GEN 用对了） |
| C3 per-fold 指标 | final_metrics.test | c3_extended_metrics.json | ✗（文件名不同，但 A2-GEN 用对了） |

**结论**：89 号 A2-GEN 产物（Figure S3/S4/Table S3）是基于真实存在的数据生成的，不存在虚构数据源问题。88 号评估文件的数据源路径错误已在本次 FIX01 中全部校正。

---

## 6. C3 路径纠正

| 88 原路径 | FIX01 校正 |
|---------|----------|
| `v0.4_results/06_c3_joint_imaging/` | `v0.4_results/06_c3_preflight/` |

C3 正式 5-fold 结果目录结构：

```text
v0.4_results/06_c3_preflight/
├── c3_image_formal_5fold/
│   ├── fold0/
│   │   ├── checkpoint_image_only.pt
│   │   ├── e21_fix01_baseline_results.json
│   │   ├── e21_fix01_detail_image_only.json
│   │   └── e21_fix01_overlap_report.json
│   ├── fold1/ ...
│   └── fold4/ ...
└── c3_joint_formal_5fold/
    ├── fold0/
    │   ├── checkpoint_joint.pt
    │   ├── e21_fix01_baseline_results.json
    │   ├── e21_fix01_detail_joint.json
    │   └── e21_fix01_overlap_report.json
    ├── fold1/ ...
    └── fold4/ ...
```

---

## 7. A2-GEN 进入建议

R87 要求 FIX01 通过后再决定是否进入 A2-GEN。但由于 A2-GEN 实际已执行且产物基于真实数据源生成，当前建议：

**选项 1（推荐）**：R87 直接审阅已生成的 89 号 A2-GEN 产物（Figure S3/S4/Table S3），若通过，A-2 闭合进入 A-3。

**选项 2**：若 Codex 认为必须先走 FIX01→正式放行→重新 A2-GEN 的流程，可重新运行 A2-GEN 脚本（脚本无需修改，数据源正确），产物一致性保证。

**无论哪种选项，88 号评估文件的数据源路径已通过 FIX01 校正完毕。**

---

## 8. 红线遵守确认

| 红线项 | 状态 | 说明 |
|--------|:---:|------|
| 不训练 | ✓ | 仅读取已有文件 |
| 不推理 | ✓ | 无推理调用 |
| 不生成新数据 | ✓ | 纯文件内容修正 |
| 不生成正式图表资产 | ✓ | 本轮只修正评估文件文本 |
| 不改 split/模型/超参/seed | ✓ | 未触及 |
| 不写论文正文 | ✓ | 仅修正评估报告 |
| 不启动档 B/raw 4-dim/--mode all | ✓ | 未涉及 |
| 不外推真实 GEO/三轴/暗室 | ✓ | 未涉及 |

---

## 9. 修改文件清单

| 文件 | 修改类型 | 说明 |
|------|---------|------|
| 88_1C-A2_SI资产补齐需求评估_Claude执行报告.md | Edit（7 处） | 数据源路径与 P0 范围校正 |
| 90_1C-A2-FIX01_SI资产数据源与P0范围校正_Claude执行报告.md | 新建 | 本 FIX01 执行报告 |

---

## 10. 给 Claude 的下一步短提示词

```text
A2-FIX01 已完成：88 号评估文件数据源路径和 P0 范围已按 R87 全部校正。

待 Codex 审阅 FIX01 后：
- 若 FIX01 通过：确认 A2-GEN（89 号）产物可用 → A-2 闭合 → 进入 A-3
- 若需 FIX02：按 R88 进一步修正

当前 89 号 A2-GEN 产物（Figure S3/S4/Table S3）已基于真实数据源生成，可直接作为审阅对象。
```

---

**1C-A2-FIX01 完成**。88 号评估文件数据源路径已全部校正为真实存在的文件。
