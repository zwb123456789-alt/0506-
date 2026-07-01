# R88_Codex 审阅：1C-A2-FIX01 与 A2-GEN 通过，P0 SI 资产草案稳定

最后更新：2026-06-29  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
89_1C-A2-GEN_P0_SI资产生成_Claude执行报告.md
90_1C-A2-FIX01_SI资产数据源与P0范围校正_Claude执行报告.md

06_v0.4_code/08_visualization/
generate_a2_si_assets.py
FigureS3_training_curves_draft.png/.pdf
FigureS4_overlap_diagnostic_draft.png/.pdf
TableS3_c3_per_fold_detail_draft.md/.csv
```

## 0. 裁决

```text
1C-A2-FIX01：PASS
1C-A2-GEN：PASS，作为 P0 SI 资产草案接收
性质：D 类既有结果读取 + 图表/表格草案生成
新训练 / 推理：未发现
模型 / split / 超参 / seed 修改：未发现
论文正文正式改写：未发现
流程偏差：89 号 A2-GEN 先于 R87 要求的 FIX01 放行执行，已记录；本轮因数据源真实且产物通过核查，不要求重跑
```

90 号已将 88 号中的错误数据源口径校正为真实路径；89 号虽然流程上提前执行，但实际使用了真实存在的数据源，产物可作为 A-2 的 P0 SI 草案稳定。

## 1. R87 要求核查

### 1.1 数据源修正通过

90 号已删除或废止以下错误口径：

```text
training_log.csv
split_metadata.json
final_metrics.test
v0.4_results/06_c3_joint_imaging/
```

并改为以下真实数据源：

```text
v0.4_results/05_c2_screening/*/*_fold*_checkpoint.pt
v0.4_results/06_c3_preflight/c3_image_formal_5fold/fold*/checkpoint_image_only.pt
v0.4_results/06_c3_preflight/c3_joint_formal_5fold/fold*/checkpoint_joint.pt
v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold*.json
v0.4_results/06_c3_preflight/*formal_5fold/fold*/e21_fix01_overlap_report.json
v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.json/.csv
```

Codex 复核：上述路径均与当前工作区实际结构一致。

### 1.2 Figure S3 口径修正通过

R87 要求不得在没有证据时声称 C2 逐 epoch 曲线存在。90 号给出修正：C2 的逐 epoch history 不在 `*_result.json`，而在 `*_checkpoint.pt` 的 `history` 字段中。89 号脚本实际使用 `torch.load(...checkpoint.pt)` 读取 C2/C3 history。

该口径可接受。但后续 caption / A-3 文本须避免把 S3 写成“无过拟合证据充分”。当前可写为：

```text
Figure S3 shows that the training losses decrease for the selected C2 configurations and C3 folds, while validation pitch metrics are reported over epochs.
```

不得写为：

```text
Figure S3 证明模型无过拟合。
Figure S3 证明模型已学到最优表示。
C2 validation pitch accuracy 已稳定收敛到高水平。
```

原因：S3(b) 中 C2 validation pitch accuracy 仍是低水平波动；C3 detail 文件中也存在 possible-overfit warning。因此 S3 只能支撑“训练过程被记录且 loss 非发散”，不能支撑强收敛/无过拟合 claim。

### 1.3 Figure S4 口径修正通过，但图注需收窄

89 号 Figure S4 图像实际展示 fold0 的 yaw-bin Train/Val/Test 覆盖。Codex 额外核查：

```text
split_manifest fold0-4：train/val/test yaw-bin overlap 均为 0，union 均为 72 bins
C3 image formal 5fold overlap report：train_val/train_test/val_test overlap 均为 0，is_strict = true
C3 joint formal 5fold overlap report：train_val/train_test/val_test overlap 均为 0，is_strict = true
```

因此 Figure S4 可作为 representative fold 可视化，配套文本可说明 all formal folds were checked by manifest / overlap reports。不得把图本身写成“展示所有 fold”。

### 1.4 Table S3 数值通过

Codex 逐字段比对：

```text
source: v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.json
table:  06_v0.4_code/08_visualization/TableS3_c3_per_fold_detail_draft.csv
rows:   10 vs 10
maxdiff: 0
```

Table S3 与源 JSON 完全一致，可作为 C3 image_only 5 folds + joint 5 folds 的 per-fold 透明度表。

## 2. 产物核查

### 2.1 脚本边界

`generate_a2_si_assets.py` 是独立新增脚本，未修改既有 `generate_figure2_fixed.py` 或 `generate_e45d_figures.py`。脚本主要行为为：

```text
读取 checkpoint history
读取 split manifest
读取 c3_extended_metrics.json
生成 S3/S4 图和 S3 表
```

未发现训练、推理、模型保存、split 改写、超参修改或 seed 改写行为。

非阻断问题：

```text
脚本仍含 DEBUG print。
脚本使用项目绝对路径。
torch.load 读取 checkpoint 作为草案阶段可接受；后续若整理为长期脚本，可考虑去掉 debug、参数化 project root。
```

### 2.2 图像文件核查

Codex 对 PNG 做了像素统计和目检：

```text
FigureS3_training_curves_draft.png：4170 x 3000，非空，四面板完整
FigureS4_overlap_diagnostic_draft.png：4261 x 1134，非空，fold0 yaw-bin 覆盖图完整
```

Figure S3/S4 作为草案图可接收。后续投稿级精修时再统一处理配色、字号、图注和是否压缩信息量。

## 3. 接受的稳定草案资产

```text
06_v0.4_code/08_visualization/
  generate_a2_si_assets.py
  FigureS3_training_curves_draft.png
  FigureS3_training_curves_draft.pdf
  FigureS4_overlap_diagnostic_draft.png
  FigureS4_overlap_diagnostic_draft.pdf
  TableS3_c3_per_fold_detail_draft.csv
  TableS3_c3_per_fold_detail_draft.md
```

对应成果区稳定摘要：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/
17_A2_P0_SI资产草案_R88通过.md
```

## 4. Claim 边界

允许写：

```text
A2 补齐了 P0 SI 草案资产：Figure S3、Figure S4 和 Table S3。
Figure S3 提供 C2 代表性配置与 C3 formal folds 的训练过程可视化，显示训练 loss 下降且未见发散。
Figure S4 展示 fold0 的 circular yaw-block train/val/test yaw-bin 覆盖；Codex 另核查所有 formal folds 的 overlap report 均为 strict。
Table S3 给出 C3 image_only 和 joint 的 10 行 per-fold 指标，补齐三通道结果透明度。
```

不得写：

```text
Figure S3 证明无过拟合。
Figure S3 证明模型已学到最优表示。
Figure S4 图本身展示了所有 folds。
Table S3 的 fold 间变异性可外推未知真实目标。
A2 证明 yaw 物理不可观测。
A2 证明 fusion 永久无用。
```

## 5. 当前下一步

头 A 当前状态：

```text
A-1 E45D-FIX02 图表/表格预生成草案：DONE，R86 通过
A-2 P0 SI 资产评估、FIX01 数据源校正、S3/S4/Table S3 草案：DONE，R88 通过
```

下一步按 R05 进入：

```text
A-3：写“负结果 -> 24 号三问”桥接材料
```

A-3 只写桥接说明材料，不写论文正文正式段落。重点回答：

```text
What can be known：fixed-roll 条件下 pitch 有一定可观测性，yaw 在 circular holdout 外推下失败。
When complementary：image-only / OCS-only / joint 的互补边界应以 extrapolation gap 和 per-fold 指标为限。
When trustworthy：exact-bin yaw=0 仅为 strict classifier sentinel，可信结论应落在 fixed-protocol negative evidence 和 extrapolation gap。
```

仍未放行：

```text
论文正文正式改写
档 B 新训练
raw 4-dim OCS-only
--mode all
后验架构 / 超参 / 特征补救
单帧多维 OCS vs 光变曲线正式实验设计
三轴小项目或路线二/三/四扩展
```

## 6. 给 Claude 的下一步短提示词

```text
请执行 1C-A3：写“负结果 -> 24 号三问”桥接材料。

依据：
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R88_Codex_审阅_1C-A2-FIX01与A2-GEN通过_P0_SI资产草案稳定.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/16_E45D图表表格预生成草案_R86通过.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/17_A2_P0_SI资产草案_R88通过.md
- 04_四路线分工区/00_总览与裁决/00_路线冻结文件区/24_v0.4项目论文主线最终冻结稿_OCS口径形态与mismatch账面对齐版.md

任务：
1. 写一份桥接材料，不写论文正文正式段落。
2. 回答 24 号三问：
   - What can be known
   - When complementary
   - When trustworthy
3. 使用 R82/R86/R88 的稳定口径：extrapolation gap、pitch 强于 yaw、early fusion no automatic gain、exact-bin yaw 仅作 sentinel。
4. 明确 A2 图表/SI 资产只支持 fixed-protocol negative evidence，不外推真实 GEO、三轴姿态或暗室实验。

输出：
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/91_1C-A3_负结果到24号三问桥接材料_Claude执行报告.md

红线：
- 不训练、不推理、不生成新图表/表格。
- 不改 split / 模型 / 超参 / seed。
- 不写论文正文正式段落，只写桥接说明材料。
- 不启动档 B、raw 4-dim OCS-only、--mode all、三轴小项目、路线二/三/四。
- 不声称 yaw 物理不可观测，不声称 fusion 永久无用，不外推真实 GEO / 三轴 / 暗室。
- 若输出过长，按 Part 1/2/3 分段写入，直到文件完整。
```

