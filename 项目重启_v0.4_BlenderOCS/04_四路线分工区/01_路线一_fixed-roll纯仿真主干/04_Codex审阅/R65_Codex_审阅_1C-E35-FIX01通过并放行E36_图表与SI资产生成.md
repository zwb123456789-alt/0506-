# R65 Codex 审阅：1C-E35-FIX01 通过，并放行 E36 图表与 SI 资产生成

最后更新：2026-06-26  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  65_1C-E35-FIX01_yawblock分箱事实修正_Claude执行报告.md
```

前序依据：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
  R64_Codex_审阅_1C-E35需FIX01_yawblock分箱事实修正.md

04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  64_1C-E35_C1C2_OCS-only_Results非正文材料包_Claude执行报告_Part1.md
  64_1C-E35_C1C2_OCS-only_Results非正文材料包_Claude执行报告_Part2.md
  64_1C-E35_C1C2_OCS-only_Results非正文材料包_Claude执行报告_Part3.md
```

---

## 0. 裁决

```text
1C-E35-FIX01: PASS
E35 + FIX01 合并材料包: ACCEPTED
C1/C2 OCS-only Results 非正文材料包: STABLE
E36 图表与 SI 资产生成: RELEASED, narrow scope
C3 independent comparison: NOT RELEASED
论文正文正式改写: NOT RELEASED
训练/代码/新实验: NOT RELEASED
三轴小项目、路线二/三/四扩展: NOT RELEASED
```

E35-FIX01 已完成 R64 要求的窄范围修正：Figure 2 yaw-block split 分箱、caption、claim boundary checklist 与标准口径均已改为实际 C2 split manifest 对应事实。E35 原材料包中 Table 1/2/3、Figure 1/3/4 plan、Results skeleton、Supplementary checklist 和 claim 边界总体方向可保留；使用时必须以 E35-FIX01 替换 E35 Part 2 的 Figure 2 段落，并替换 E35 Part 3 中关于 yaw coverage 的红灯/黄灯表述。

---

## 1. 通过理由

### 1.1 R64 三个 Major 已修正

R64 要求修正：

```text
1. Figure 2 中错误的 7-bin test、5 x 7 = 35 bins、49% coverage、Fold 4 wrap 表述。
2. "C2 covers all yaw angles" 不能列为红灯，需改为 aggregate 5-fold coverage 限定表述。
3. "preventing nearby yaw angles" 需收紧为 held-out test yaw bins never seen during training。
```

FIX01 已改为：

```text
Fold 0: val bins 65-71, test bins 0-14, train bins 15-64
Fold 1: val bins 8-14,  test bins 15-29, train bins 0-7 and 30-71
Fold 2: val bins 23-29, test bins 30-43, train bins 0-22 and 44-71
Fold 3: val bins 37-43, test bins 44-57, train bins 0-36 and 58-71
Fold 4: val bins 51-57, test bins 58-71, train bins 0-50

Total test coverage = 15 + 15 + 14 + 14 + 14 = 72/72 yaw bins
```

该表与实际 manifest 摘要一致：

| Fold | Train yaw unique | Val yaw unique | Test yaw unique | Test samples | Val yaw range | Test yaw range |
|---:|---:|---:|---:|---:|---|---|
| 0 | 50 | 7 | 15 | 555 | 325-355 deg | 0-70 deg |
| 1 | 50 | 7 | 15 | 555 | 40-70 deg | 75-145 deg |
| 2 | 51 | 7 | 14 | 518 | 115-145 deg | 150-215 deg |
| 3 | 51 | 7 | 14 | 518 | 185-215 deg | 220-285 deg |
| 4 | 51 | 7 | 14 | 518 | 255-285 deg | 290-355 deg |

### 1.2 Claim 边界修正到位

FIX01 已将错误红灯项：

```text
"C2 covers all yaw angles." (只测试 35/72 bins)
```

改为合理的限定口径：

```text
Across the five circular yaw-block folds, the test blocks collectively cover all 72 yaw bins exactly once.
Each individual fold tests one contiguous held-out yaw block.
Full yaw coverage holds only after aggregating all five folds, not within each fold.
```

这符合 R64 要求。后续写作中允许写 aggregate 5-fold covers all 72 yaw bins，但必须同时说明 single fold 只测试一个连续 holdout block。

### 1.3 红线未越界

FIX01 未启动 C3、未运行训练、未改代码、未写论文正文正式段落、未扩展到三轴小项目或路线二/三/四。Table 2 的 R62 稳定数值未被改动。

---

## 2. 稳定合并规则

E35 作为材料包使用时，按以下方式合并：

```text
保留:
  E35 Part 1: Table 1/2/3 草案
  E35 Part 2: Figure 1, Figure 3, Figure 4 plan
  E35 Part 2: Results skeleton, Supplementary checklist
  E35 Part 3: 除 yaw coverage 条目外的 claim boundary checklist

替换:
  E35 Part 2 Section 5.2 Figure 2 全段
  E35 Part 3 中 "C2 covers all yaw angles" 相关红灯/黄灯表述

替换来源:
  65_1C-E35-FIX01_yawblock分箱事实修正_Claude执行报告.md
```

后续禁止再使用以下旧表述：

```text
5 x 7 = 35 test bins
35/72 yaw coverage
~49% yaw space tested
Fold 4 wraps across 0/360 boundary
C2 only tested about half of yaw space
preventing the model from seeing nearby yaw angles during training
```

后续标准口径：

```text
C2 used five circular yaw-block holdout folds on a 72-bin yaw grid.
Each fold held out one contiguous test yaw block and one adjacent validation block.
Across the five folds, the test blocks collectively covered all 72 yaw bins exactly once.
Within each fold, training excluded the validation and test yaw bins.
This protocol evaluates unseen-yaw-bin generalization under fixed-roll phase63 data; it is not random cross-validation.
```

---

## 3. 当前稳定结论

E35 + FIX01 支撑以下稳定非正文材料口径：

```text
1. C1: 14 个预注册 feature configs 完整，constant sanity check 用于 C1，不进入 C2。
2. C2: 13 configs x 5 folds = 65 runs，全部 yaw_acc = 0.00%，yaw_correct_count = 0。
3. Within-3 chance-level = 7/72 = 9.72%；within-3 只能解释为 coarse localization diagnostic。
4. Pitch accuracy = 2.56%-4.37%，仅为 secondary diagnostic，不改变 C2 null result。
5. C2 split: aggregate five-fold test blocks cover 72/72 yaw bins exactly once。
6. Claim 边界：只可写 fixed-protocol MLP + phase63 fixed-roll + low-dimensional OCS-only / visibility / mixed features under circular yaw-block holdout 的 null result。
```

不可写：

```text
OCS photometry contains no attitude information.
OCS fails under all architectures or feature spaces.
OCS is inferior to image channels.
C2 proves image-only or joint-channel outcomes.
C2 generalizes to real unknown-target operational systems.
```

---

## 4. 成果区分流

E35 + FIX01 已形成稳定材料包索引，进入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/
  09_C1C2_OCS-only_Results非正文材料包_E35_R65通过.md
```

Claude 原始输出仍保留在 `02_Claude输出/`，Codex 审阅与阶段门记录保留在 `04_Codex审阅/`。

---

## 5. 下一步放行：1C-E36

Codex 放行下一步，但仅限非正文资产生成：

```text
1C-E36: C1/C2 OCS-only 图表与 SI 资产生成
RELEASED, narrow scope
```

允许内容：

```text
1. 生成 Table 1/2/3 的 LaTeX 表格草案和 Markdown 稳定表格。
2. 生成 Figure 1-4 的实际绘图规格或可执行绘图脚本草案。
3. 生成 Supplementary Table S1/S2 草案：
   - S1 raw feature definitions
   - S2 per-fold C2 results
4. 生成 Figure 2 split design 的最终数据表，必须使用 R65 标准口径。
5. 输出一个资产索引，列出每个表/图/SI 的数据源、生成方式和待人工检查项。
```

禁止内容：

```text
不得写 Results 正文正式段落。
不得写 Abstract / Introduction / Discussion。
不得启动 C3。
不得运行训练。
不得做 OCS-only 后验模型/超参/特征搜索。
不得改已有训练代码或数据结果。
不得启动三轴小项目或路线二/三/四。
```

如果 E36 需要生成绘图脚本，只能作为图表资产生成辅助脚本，必须写入 Claude 输出区或后续 Codex 指定的候选资产目录，不得改动现有训练/数据管线代码。

---

## 6. 给 Claude 的 E36 短提示词

```text
执行 1C-E36：C1/C2 OCS-only 图表与 SI 资产生成。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R65_Codex_审阅_1C-E35-FIX01通过并放行E36_图表与SI资产生成.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/09_C1C2_OCS-only_Results非正文材料包_E35_R65通过.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/64_1C-E35_C1C2_OCS-only_Results非正文材料包_Claude执行报告_Part1.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/64_1C-E35_C1C2_OCS-only_Results非正文材料包_Claude执行报告_Part2.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/64_1C-E35_C1C2_OCS-only_Results非正文材料包_Claude执行报告_Part3.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/65_1C-E35-FIX01_yawblock分箱事实修正_Claude执行报告.md
- v0.4_results/05_c2_screening/c2_screening_summary.json
- v0.4_results/04_ocs_features/feature_definitions.json
- v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold*.json

任务：
1. 生成 Table 1/2/3 的 LaTeX 草案和 Markdown 稳定表格。
2. 生成 Figure 1-4 的实际图表资产规格；如需绘图脚本，只能作为候选辅助脚本，不得改训练/数据管线代码。
3. 生成 Supplementary Table S1/S2 草案：
   - S1 raw feature definitions
   - S2 per-fold C2 results
4. 生成 Figure 2 split design 的最终数据表，必须使用 R65 标准口径：
   aggregate five-fold test coverage = 72/72 yaw bins; per-fold test block = 14-15 bins.
5. 生成资产索引，列出每个表/图/SI 的数据源、生成方式和待人工检查项。

输出到：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  66_1C-E36_C1C2_OCS-only图表与SI资产生成_Claude执行报告.md

若输出过长，按 Part1/Part2/Part3 分段写入。

红线：
- 不启动 C3。
- 不运行训练。
- 不做后验 OCS-only 架构/超参/特征搜索。
- 不改现有训练代码或数据结果。
- 不写 Results/Abstract/Introduction/Discussion 正文正式段落。
- 不启动三轴小项目或路线二/三/四。
- 不再使用 35/72、49% coverage、5x7 test bins、Fold 4 wrap 等旧错误 split 表述。
```

---

## 7. 当前阶段状态

```text
E35: CLOSED, PASS after FIX01
E35-FIX01: CLOSED, PASS
C1/C2 Results 非正文材料包: STABLE
E36: RELEASED, narrow scope
C3 / paper prose / training / new experiments: NOT RELEASED
```
