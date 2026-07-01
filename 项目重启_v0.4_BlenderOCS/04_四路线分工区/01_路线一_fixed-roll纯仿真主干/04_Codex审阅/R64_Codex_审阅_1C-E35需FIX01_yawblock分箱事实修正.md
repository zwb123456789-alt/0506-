# R64 Codex 审阅：1C-E35 需 FIX01，修正 yaw-block 分箱事实

最后更新：2026-06-26  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  64_1C-E35_C1C2_OCS-only_Results非正文材料包_Claude执行报告_Part1.md
  64_1C-E35_C1C2_OCS-only_Results非正文材料包_Claude执行报告_Part2.md
  64_1C-E35_C1C2_OCS-only_Results非正文材料包_Claude执行报告_Part3.md
```

---

## 0. 裁决

```text
1C-E35: NEEDS FIX01
主表数值与 R62 口径: ACCEPTED
Claim 边界总体方向: ACCEPTED WITH ONE REQUIRED CORRECTION
Figure 2 yaw-block split 描述: NOT ACCEPTED
C3: NOT RELEASED
论文正文正式改写: NOT RELEASED
训练/代码/新实验: NOT RELEASED
```

E35 总体完成了 R63 要求的非正文材料包：Table 1/2/3 草案、Figure 1-4 plan、Results skeleton、Supplementary checklist 与 Claim boundary checklist 均已形成，且没有启动 C3、训练、代码修改或论文正文正式段落。

但是 E35 Part 2 的 Figure 2 circular yaw-block holdout 分箱描述与实际 C2 使用的 split manifests 不一致；Part 3 中“C2 只测试 5 x 7 = 35 bins、约 49% yaw space”的红线判断也因此错误。该问题会直接影响方法图、图注和 claim 边界，必须做一次窄范围 FIX01。

---

## 1. 已通过部分

### 1.1 C2 数值表格通过

Codex 抽查 `v0.4_results/05_c2_screening/c2_screening_summary.json`，确认 Table 2 的核心数值与 R62 稳定口径一致：

```text
13 configs x 5 folds = 65 runs
65 result JSON files
65 checkpoint files
all mean_test_yaw_acc = 0.00%
all mean_test_yaw_correct_count = 0.0
within-3 chance-level = 7/72 = 9.72%
pitch_acc is secondary diagnostic only
```

抽查到的 aggregate 指标如下：

| Config | yaw_acc (%) | yaw_correct | yaw_CMAE (deg) | within-3 (%) | pitch_acc (%) |
|---|---:|---:|---:|---:|---:|
| baseline_4dim | 0.00 | 0.0 | 89.25 | 8.16 | 2.56 |
| R_ratio_2d | 0.00 | 0.0 | 84.15 | 6.31 | 2.56 |
| R_ratio_3d | 0.00 | 0.0 | 80.36 | 10.45 | 2.62 |
| I_interpart_1d | 0.00 | 0.0 | 107.78 | 2.75 | 2.69 |
| N_density_3d | 0.00 | 0.0 | 120.26 | 3.96 | 3.41 |
| L_logratio_3d | 0.00 | 0.0 | 83.17 | 7.70 | 3.18 |
| M1_ratio_log_5d | 0.00 | 0.0 | 83.05 | 7.83 | 3.07 |
| M3_density_ratio_5d | 0.00 | 0.0 | 97.47 | 10.51 | 3.15 |
| M4_log_density_ratio_9d | 0.00 | 0.0 | 115.74 | 12.05 | 4.37 |
| P_pixelfrac_3d | 0.00 | 0.0 | 98.15 | 14.79 | 2.66 |
| M5_pixelfrac_only_4d | 0.00 | 0.0 | 95.75 | 15.57 | 2.59 |
| M2_ratio_pixelfrac_5d | 0.00 | 0.0 | 98.25 | 14.74 | 3.23 |
| M6_all_nongeo_13d | 0.00 | 0.0 | 107.18 | 14.60 | 3.30 |

因此 Table 2/3 的主结论可以保留：C2 是 fixed-protocol OCS-only null result。

### 1.2 R62/FIX01 口径基本遵守

E35 已正确使用：

```text
within-3 chance-level = 7/72 = 9.72%
pitch_acc = secondary diagnostic
C3 = candidate only / not released
OCS failure claims require fixed-protocol MLP + phase63 fixed-roll + yaw-block holdout limitation
```

E35 没有把 null result 外推成“OCS 物理无信息”、真实未知目标姿态反演失败或 image 通道必然更好。这一点通过。

---

## 2. 必须修正的问题

### Major 1：Figure 2 的 fold 分箱与实际 manifest 不一致

E35 Part 2 写成：

```text
每个 fold test 7 bins
5 x 7 = 35 test bins
covers ~49% of yaw space
Fold 4 wraps across 0/360 boundary
```

这与实际 C2 使用的 `e25_multifold_yawblock` split manifest 不一致。Codex 读取以下文件：

```text
v0.4_results/03_training_baseline/e25_multifold_yawblock/
  split_manifest_circ_yawblock_fold0.json
  split_manifest_circ_yawblock_fold1.json
  split_manifest_circ_yawblock_fold2.json
  split_manifest_circ_yawblock_fold3.json
  split_manifest_circ_yawblock_fold4.json
```

实际 split 摘要为：

| Fold | Val yaw bins | Test yaw bins | Train yaw unique | Val yaw unique | Test yaw unique | Test samples |
|---:|---|---|---:|---:|---:|---:|
| 0 | 65-71 (325-355 deg) | 0-14 (0-70 deg) | 50 | 7 | 15 | 555 |
| 1 | 8-14 (40-70 deg) | 15-29 (75-145 deg) | 50 | 7 | 15 | 555 |
| 2 | 23-29 (115-145 deg) | 30-43 (150-215 deg) | 51 | 7 | 14 | 518 |
| 3 | 37-43 (185-215 deg) | 44-57 (220-285 deg) | 51 | 7 | 14 | 518 |
| 4 | 51-57 (255-285 deg) | 58-71 (290-355 deg) | 51 | 7 | 14 | 518 |

因此实际 test coverage 是：

```text
15 + 15 + 14 + 14 + 14 = 72 yaw bins
覆盖 72/72 yaw bins, not 35/72
每个 yaw bin 在 5-fold 中恰好作为 test 出现一次
```

E35 的 Figure 2 不能继续使用“5 x 7 = 35 test bins”或“约 49% yaw space tested”。

### Major 2：“C2 covers all yaw angles” 不能列为红灯 claim

E35 Part 3 将以下表述列入不可写：

```text
"C2 covers all yaw angles." (只测试了 5 x 7 = 35 bins, 约 49% 覆盖)
```

这条必须改。基于实际 manifest，C2 的 5-fold test blocks 在 aggregate 意义上覆盖全部 72 个 yaw bins；但单个 fold 只测试一个连续 yaw block。

推荐改成黄灯限定表述：

```text
可以写：
"Across the five circular yaw-block folds, every yaw bin appears in the test set once."

必须限定：
"Each individual fold tests one contiguous held-out yaw block; full yaw coverage only holds after aggregating all five folds."

不可写：
"Every model was trained and tested on all yaw angles within each fold."
"The protocol is random 5-fold cross-validation."
```

### Major 3：Figure 2 caption 对“nearby yaw”隔离的表述需收紧

E35 Figure 2 caption 写到：

```text
preventing the model from seeing nearby yaw angles during training
```

实际 split 中，validation block 位于 test block 前侧，training set 排除 val/test，但 test block 后侧的相邻 yaw bin 可能属于 train。例如 fold0 test 0-70 deg，train 从 75 deg 开始。因此不能笼统写成“preventing seeing nearby yaw angles”。

推荐改成：

```text
The model never sees the held-out test yaw bins during training.
An adjacent validation block is reserved on one side of each test block; training excludes both validation and test bins.
This is a strict unseen-yaw-bin block holdout, not a full two-sided gap around the test block.
```

---

## 3. FIX01 范围

E35-FIX01 只需修正 yaw-block 分箱事实，不需要重写全部 E35。

必须修正：

```text
1. Part 2 Figure 2 plan:
   - 删除 5 x 7 = 35 test bins
   - 删除 covers ~49% yaw space
   - 删除 Fold 4 wraps across 0/360 boundary 的错误表述
   - 改为实际 5-fold bins 表
   - 改为 aggregate test coverage = 72/72 bins

2. Part 2 Figure 2 caption:
   - 改为 "every yaw bin appears in a test block once across five folds"
   - 改为 "single fold tests one contiguous held-out yaw block"
   - 收紧 "nearby yaw" 隔离表述

3. Part 3 Claim boundary checklist:
   - 删除或改写 "C2 covers all yaw angles" 红灯项
   - 加入 yellow-light 限定：aggregate 5-fold covers all yaw bins, per-fold does not

4. Results skeleton 3.2:
   - 若提到 35/72、49%、7-bin test block，全部替换为实际 split 信息
```

可以保留：

```text
Table 1/2/3 主体
Figure 1 plan
Figure 3 plan
Figure 4 plan
Supplementary checklist
within-3 = 9.72%
pitch_acc secondary diagnostic
C3 not released
OCS null-result claim boundary
```

---

## 4. 修正后标准口径

后续关于 split 的标准写法如下：

```text
C2 used five circular yaw-block holdout folds on a 72-bin yaw grid.
Each fold held out one contiguous test yaw block and one adjacent validation block.
Across the five folds, the test blocks collectively covered all 72 yaw bins exactly once.
Within each fold, training excluded the validation and test yaw bins.
This protocol evaluates unseen-yaw-bin generalization under fixed-roll phase63 data; it is not random cross-validation.
```

具体 fold 表：

```text
Fold 0: val bins 65-71, test bins 0-14, train bins 15-64
Fold 1: val bins 8-14,  test bins 15-29, train bins 0-7 and 30-71
Fold 2: val bins 23-29, test bins 30-43, train bins 0-22 and 44-71
Fold 3: val bins 37-43, test bins 44-57, train bins 0-36 and 58-71
Fold 4: val bins 51-57, test bins 58-71, train bins 0-50
```

---

## 5. 下一步放行

```text
1C-E35-FIX01: RELEASED
任务性质: narrow correction only
C3: NOT RELEASED
论文正文正式改写: NOT RELEASED
训练/代码/新实验: NOT RELEASED
```

E35-FIX01 完成后，Codex 再审。如果 FIX01 仅修正上述 split 问题且不引入新越界内容，E35 材料包可进入通过状态；之后再考虑是否放行 E36 进行实际图表/SI 文件生成。

---

## 6. 给 Claude 的 E35-FIX01 短提示词

```text
执行 1C-E35-FIX01：修正 E35 材料包中的 yaw-block split 分箱事实。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R64_Codex_审阅_1C-E35需FIX01_yawblock分箱事实修正.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/64_1C-E35_C1C2_OCS-only_Results非正文材料包_Claude执行报告_Part1.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/64_1C-E35_C1C2_OCS-only_Results非正文材料包_Claude执行报告_Part2.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/64_1C-E35_C1C2_OCS-only_Results非正文材料包_Claude执行报告_Part3.md
- v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold0.json
- v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold1.json
- v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold2.json
- v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold3.json
- v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold4.json

任务：
1. 生成一个 FIX01 修正报告，不重写全部 E35。
2. 修正 Figure 2 plan/caption 中错误的 7-bin test、5x7=35 bins、49% coverage、Fold 4 wrap 表述。
3. 使用 R64 给出的实际 fold 表：test bins 合计 72/72 yaw bins，每个 yaw bin across folds 作为 test 一次。
4. 修正 Claim boundary checklist：不要把 "C2 covers all yaw angles" 作为红灯；改成 aggregate 5-fold covers all yaw bins, per-fold tests one contiguous block 的限定表述。
5. 若 Results skeleton 或 supplementary checklist 中有 35/72、49%、7-bin test block，也一并修正。

输出到：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/65_1C-E35-FIX01_yawblock分箱事实修正_Claude执行报告.md

红线：
- 不启动 C3。
- 不运行训练。
- 不改代码。
- 不写论文正文正式段落。
- 不扩展到三轴小项目或路线二/三/四。
- 不改 Table 2 的 R62 稳定数值，除非发现与 c2_screening_summary.json 的直接矛盾。
```
