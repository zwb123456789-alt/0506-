# R87_Codex 审阅：1C-A2 需 FIX01，先校正 SI 资产数据源与范围

日期：2026-06-29  
审阅对象：`02_Claude输出/88_1C-A2_SI资产补齐需求评估_Claude执行报告.md`  
阶段：头 A / A-2，SI 资产补齐需求评估  
裁决：**不通过，需 1C-A2-FIX01 后再决定是否进入 A2-GEN**

## 1. 阶段判定

88 的高层方向是合理的：A-2 只应评估路线一 C 收口前还缺哪些最小必要 SI 资产，不应扩展到论文正文、重训练、模型改进或完整 SI 精修。

但 88 不能作为下一步 A2-GEN 的直接执行依据。核心问题是其“数据可用性核查”过于确信，且列出的多个输入路径或文件模式在当前工作区中不存在。如果直接照 88 执行，Claude 很可能基于错误路径生成悬空的 Figure S3/S4/Table S3 方案。

因此本轮只放行 **FIX01 数据源与资产范围校正**，不放行 A2-GEN。

## 2. 关键核查结果

本轮只读现有结果文件，没有训练、推理、改 split、改模型或生成新图表。

实际文件情况如下：

| 88 声称的数据源 | 核查结论 |
|---|---|
| `v0.4_results/05_c2_screening/*/training_log.csv` | 不存在。C2 screening 下未发现 `training_log.csv`。 |
| `v0.4_results/06_c3_joint_imaging/c3_fold*/training_log.csv` | 路径不存在。当前 C3 正式结果在 `v0.4_results/06_c3_preflight/`。 |
| `v0.4_results/*/split_metadata.json` | 不存在。可用的是 `03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold*.json` 以及各 fold 的 overlap report。 |
| `v0.4_results/06_c3_joint_imaging/c3_fold*/final_metrics.test` | 不存在。 |
| `v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.json/.csv` | 存在，可作为 Table S3 的优先数据源。 |

实际可用的关键文件模式：

```text
v0.4_results/05_c2_screening/*/*_fold*_result.json
v0.4_results/05_c2_screening/supplementary_table_s2_per_fold_results.csv
v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold*.json
v0.4_results/06_c3_preflight/c3_image_formal_5fold/fold*/e21_fix01_detail_image_only.json
v0.4_results/06_c3_preflight/c3_joint_formal_5fold/fold*/e21_fix01_detail_joint.json
v0.4_results/06_c3_preflight/c3_image_formal_5fold/fold*/e21_fix01_overlap_report.json
v0.4_results/06_c3_preflight/c3_joint_formal_5fold/fold*/e21_fix01_overlap_report.json
v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.csv
v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.json
```

## 3. 对 P0 资产的修正判断

### Figure S3

88 将 Figure S3 定为 “C2 + C3 training curves”，但这个口径目前不能直接成立。

- C3 正式 5-fold 的 `e21_fix01_detail_*.json` 中确有 `train_loss_curve` 与 `val_loss_curves`，可支持 C3 image_only 5 folds + joint 5 folds 的训练曲线草案。
- C2 screening 的 65 个 `*_result.json` 目前只看到 `training_summary`、`final_metrics` 和配置/最终指标，未发现 `train_loss_curve` 或 `val_loss_curves`。
- 因此 Figure S3 不得继续写成“C2+C3 全部训练曲线已具备”。FIX01 必须改为以下二选一：
  1. 若能找到真实逐 epoch C2 曲线文件，列出确切路径与字段；
  2. 若找不到，则将 S3 改为 “C3 training curves + C2 training summary / convergence proxy”，并明确 C2 不展示逐 epoch 曲线。

### Figure S4

Figure S4 的必要性可以保留，但数据源要改。

可用数据不是 `split_metadata.json`，而是：

```text
v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold*.json
v0.4_results/06_c3_preflight/*formal_5fold/fold*/e21_fix01_overlap_report.json
```

S4 应定位为 strict yaw-block holdout / overlap diagnostic 的可视化或表格式诊断草案，重点证明 train/val/test overlap 为 0、协议为 strict，而不是虚构不存在的 metadata 文件。

### Table S3

Table S3 可以保留为 P0，且现有数据源明确：

```text
v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.csv
v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.json
```

该文件已包含 C3 image_only 5 folds + joint 5 folds 的 per-fold 指标，包括 `yaw_exact_acc`、`yaw_circular_mae_deg`、`yaw_within_3/6_bins_rate`、`yaw_coarse_45deg_acc`、pitch 指标和 `n_samples`。88 中的 `final_metrics.test` 路径应删除。

## 4. 必须修正的问题

1. 不得再声称 `training_log.csv`、`split_metadata.json`、`final_metrics.test` “已具备”，除非 FIX01 给出真实存在的路径。
2. 不得使用 `v0.4_results/06_c3_joint_imaging/` 作为 C3 正式结果路径；应统一改为 `v0.4_results/06_c3_preflight/` 下的 image/joint formal 5-fold。
3. Figure S3 的 P0 定义必须收窄或分层：C3 曲线可做，C2 曲线需先证明数据存在；否则只能做 C2 training summary / convergence proxy。
4. Figure S4 的数据源必须改为 split manifest + overlap report。
5. Table S3 的数据源必须改为 `c3_extended_metrics.csv/json`。
6. 88 给出的下一步 Claude 提示词不能沿用，需先生成修正版提示词。

## 5. 下一步给 Claude 的短提示词

```text
请执行 1C-A2-FIX01：修正 88 号 SI 资产补齐需求评估中的数据源路径与 P0 资产范围。

输入文件：
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/88_1C-A2_SI资产补齐需求评估_Claude执行报告.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R87_Codex_审阅_1C-A2需FIX01_SI资产数据源与范围校正.md

必须核查并写入报告：
1. 列出真实存在的 C2/C3/SI 数据源文件模式，不得使用不存在的 training_log.csv、split_metadata.json、final_metrics.test。
2. C3 正式路径应使用：
   - v0.4_results/06_c3_preflight/c3_image_formal_5fold/fold*/e21_fix01_detail_image_only.json
   - v0.4_results/06_c3_preflight/c3_joint_formal_5fold/fold*/e21_fix01_detail_joint.json
   - v0.4_results/06_c3_preflight/*formal_5fold/fold*/e21_fix01_overlap_report.json
3. Table S3 数据源应使用：
   - v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.csv/json
4. 重新判断 Figure S3：
   - 若找到 C2 逐 epoch 曲线，列出确切路径和字段；
   - 若找不到，将 Figure S3 改为 C3 training curves + C2 training summary / convergence proxy，不得声称 C2 training curves 已具备。
5. 重新给出是否进入 A2-GEN 的建议，但只能基于真实存在文件。

输出：
- 写入 02_Claude输出/89_1C-A2-FIX01_SI资产数据源与P0范围校正_Claude执行报告.md

红线：
- 不训练、不推理、不生成新数据、不改 split / 模型 / 超参 / seed。
- 不生成 Figure S3/S4/Table S3 正式资产；本轮只修正评估与执行依据。
- 不写论文正文正式段落。
- 不启动档 B、raw 4-dim OCS-only、--mode all、三轴小项目、路线二/三/四。
- 不外推真实 GEO、三轴姿态或暗室实验。
```

## 6. 当前阶段状态

A-2 尚未通过。当前应先执行 `1C-A2-FIX01`，由 Claude 修正 88 的数据源和 P0 范围；Codex 审阅 FIX01 通过后，才可决定是否进入 A2-GEN 生成 Figure S3/S4/Table S3 草案。

