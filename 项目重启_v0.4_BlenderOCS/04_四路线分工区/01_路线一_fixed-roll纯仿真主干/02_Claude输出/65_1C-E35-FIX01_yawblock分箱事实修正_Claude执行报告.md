# 65_1C-E35-FIX01_yawblock分箱事实修正_Claude执行报告

执行端：Claude  
任务编号：1C-E35-FIX01  
任务名称：修正 E35 材料包中的 yaw-block split 分箱事实  
执行日期：2026-06-26  

---

## 0. 执行裁决

```text
1C-E35-FIX01：COMPLETED
错误定位：E35 Part 2 Figure 2 与实际 C2 split manifest 不一致
修正范围：Figure 2 plan/caption、Claim boundary checklist、Results skeleton 相关部分
Table 1/2/3 主体数值：无需修改（R62 口径正确）
```

本报告是窄范围修正，只修正 yaw-block split 分箱事实错误，不重写全部 E35 材料包。

---

## 1. 问题定位

### 1.1 E35 原错误表述

**E35 Part 2 Figure 2 设计中写成**：
```text
每个 fold test 7 bins
5 x 7 = 35 test bins
covers ~49% of yaw space (35/72 bins)
Fold 4 wraps across 0°/360° boundary
```

**E35 Part 3 Claim boundary checklist 中列为红灯**：
```text
❌ "C2 covers all yaw angles." (只测试了 5 x 7 = 35 bins，约 49% 覆盖)
```

### 1.2 实际 C2 split 事实（来自 R64）

Codex 核验了实际使用的 split manifest：

```text
v0.4_results/03_training_baseline/e25_multifold_yawblock/
  split_manifest_circ_yawblock_fold0.json
  split_manifest_circ_yawblock_fold1.json
  split_manifest_circ_yawblock_fold2.json
  split_manifest_circ_yawblock_fold3.json
  split_manifest_circ_yawblock_fold4.json
```

**实际 split 摘要**：

| Fold | Val yaw bins | Test yaw bins | Train yaw unique | Val yaw unique | Test yaw unique | Test samples |
|:----:|:------------|:-------------|:----------------:|:--------------:|:---------------:|:------------:|
| 0 | 65-71 (325-355°) | 0-14 (0-70°) | 50 | 7 | 15 | 555 |
| 1 | 8-14 (40-70°) | 15-29 (75-145°) | 50 | 7 | 15 | 555 |
| 2 | 23-29 (115-145°) | 30-43 (150-215°) | 51 | 7 | 14 | 518 |
| 3 | 37-43 (185-215°) | 44-57 (220-285°) | 51 | 7 | 14 | 518 |
| 4 | 51-57 (255-285°) | 58-71 (290-355°) | 51 | 7 | 14 | 518 |

**关键事实**：
- Test bins per fold: 15, 15, 14, 14, 14（不是统一 7 bins）
- Total test bins across 5 folds: 15 + 15 + 14 + 14 + 14 = **72 bins**
- Coverage: **72/72 yaw bins**（不是 35/72）
- **每个 yaw bin 在 5-fold 中恰好作为 test 出现一次**

### 1.3 错误影响范围

错误的"5×7=35 bins, 49% coverage"表述会影响：
1. Figure 2 设计图与 caption
2. Claim boundary checklist 红灯项
3. 方法描述的准确性
4. 对"C2 is incomplete coverage"的误判

---

## 2. 修正内容

### 2.1 Figure 2 Plan 修正版

**用途**: 说明 5-fold circular yaw-block holdout 的跨 yaw 泛化测试设计。

**内容设计（修正版）**:
```text
[Diagram: Circular yaw grid]

72-bin yaw grid (5° resolution, 0°-360°)
Arranged in circular layout:
  Bin 0 (0°-5°) → Bin 1 (5°-10°) → ... → Bin 71 (355°-360°) → [wraps to Bin 0]

5-Fold Circular Yaw-Block Holdout:

Fold 0:
  Train: Bins 15-64 (50 unique yaw bins)
  Val:   Bins 65-71 (7 bins, 325°-355°)
  Test:  Bins 0-14 (15 bins, 0°-70°)

Fold 1:
  Train: Bins 0-7, 30-71 (50 unique yaw bins)
  Val:   Bins 8-14 (7 bins, 40°-70°)
  Test:  Bins 15-29 (15 bins, 75°-145°)

Fold 2:
  Train: Bins 0-22, 44-71 (51 unique yaw bins)
  Val:   Bins 23-29 (7 bins, 115°-145°)
  Test:  Bins 30-43 (14 bins, 150°-215°)

Fold 3:
  Train: Bins 0-36, 58-71 (51 unique yaw bins)
  Val:   Bins 37-43 (7 bins, 185°-215°)
  Test:  Bins 44-57 (14 bins, 220°-285°)

Fold 4:
  Train: Bins 0-50 (51 unique yaw bins)
  Val:   Bins 51-57 (7 bins, 255°-285°)
  Test:  Bins 58-71 (14 bins, 290°-355°)

Key properties:
- Each fold tests one contiguous held-out yaw block
- Test block sizes: fold 0-1 = 15 bins each, fold 2-4 = 14 bins each
- Validation bins: 7 bins adjacent to test block (on the leading edge)
- Training bins exclude both validation and test blocks
- **Aggregate coverage: 15+15+14+14+14 = 72 bins = full yaw space**
- **Each yaw bin appears in exactly one test block across the five folds**
- Circular layout: fold 0 val wraps from bin 71 to bin 0
```

**数据来源**:
- v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold*.json
- R64 审阅核验表

**Caption 草案（修正版）**:

**Figure 2. Five-fold circular yaw-block holdout strategy.**

The yaw space (72 bins, 5° resolution) is partitioned into five non-overlapping test blocks. Each fold trains on approximately 50-51 yaw bins, validates on 7 adjacent bins (on the leading edge of the test block), and tests on 14-15 held-out bins. **Across the five folds, the test blocks collectively cover all 72 yaw bins exactly once**, ensuring full yaw-space evaluation. Within each fold, the model never sees the held-out test yaw bins during training. This design evaluates unseen-yaw-bin generalization under strict block holdout; it is not random cross-validation.

**图注要点（修正版）**:
- **Aggregate test coverage: 72/72 bins (100% yaw space)**
- **Per-fold test: one contiguous block (14-15 bins)**
- Adjacent validation bins: 7 bins on leading edge of test block
- Training excludes val + test bins
- Design rationale: tests whether OCS features generalize to completely unseen yaw blocks
- **Not random CV**: strict yaw-block holdout strategy
- Circular layout naturally handles 0°/360° boundary (fold 0 val wraps)

---

### 2.2 Results Skeleton 3.2 修正

**原 E35 Part 2 表述**（若有提到 35/72 或 49%）:
```text
（检查后发现 E35 Part 2 Results skeleton 3.2 未明确写 35/72 或 49%，
只写了 5-fold circular yaw-block holdout 和 exact-bin yaw accuracy，
因此该部分无需大幅修正）
```

**建议补充**（若后续展开 skeleton 为正文时）:
- 在描述 holdout strategy 时明确说明"aggregate 5-fold covers all 72 yaw bins"
- 避免说"部分 yaw space"或"约一半 yaw bins"
- 标准表述参考 R64 第 4 节

---

### 2.3 Claim Boundary Checklist 修正

**E35 Part 3 原红灯项（错误）**:
```text
❌ "C2 covers all yaw angles." (只测试了 5×7=35 bins，约 49% 覆盖)
```

**FIX01 修正为黄灯限定项**:

#### 可以写（绿灯）：
- ✅ "Across the five circular yaw-block folds, the test blocks collectively cover all 72 yaw bins exactly once."
- ✅ "C2 evaluates generalization to unseen yaw bins with full yaw-space coverage when aggregating the five folds."
- ✅ "Every yaw bin in the 72-bin grid appears in a test block once across the five folds."

#### 必须限定（黄灯）：
- ⚠️ 写"C2 covers all yaw angles"时，必须说明：
  - "Aggregate coverage across five folds = 72/72 bins"
  - "Each individual fold tests one contiguous held-out yaw block (14-15 bins)"
  - "Full yaw coverage holds only after aggregating all five folds, not within each fold"
  
- ⚠️ 写"yaw-block holdout"时，必须说明：
  - "This is unseen-yaw-bin block holdout, not random cross-validation"
  - "Training excludes the validation and test yaw bins within each fold"
  - "The model never sees the held-out test yaw bins during training"

#### 不可写（红灯）：
- ❌ "Every model was trained and tested on all yaw angles within each fold."
- ❌ "The protocol is random 5-fold cross-validation." (是 block holdout，不是 random CV)
- ❌ "C2 only tested 49% of yaw space." (实际是 100% aggregate coverage)
- ❌ "The model sees all nearby yaw angles during training." (test bins 完全 holdout)

---

### 2.4 Figure 2 Caption "Nearby Yaw" 表述收紧

**E35 原 caption 中的问题表述**:
```text
"preventing the model from seeing nearby yaw angles during training"
```

**问题**：实际 split 中，validation block 在 test block 前侧，training set 排除 val/test，但 test block 后侧的相邻 yaw bin 可能属于 train（例如 fold 0 test 0-70°，train 从 75° 开始，后侧相邻）。因此不能笼统说"preventing seeing nearby yaw angles"。

**FIX01 修正表述**:
```text
The model never sees the held-out test yaw bins during training. An adjacent validation block (7 bins) is reserved on the leading edge of each test block; training excludes both validation and test bins. This is a strict unseen-yaw-bin block holdout, not a full two-sided isolation gap around the test block.
```

**或更简洁版本**:
```text
Within each fold, the model never sees the held-out test yaw bins during training. Training excludes both validation and test bins, ensuring strict yaw generalization evaluation.
```

---

## 3. 标准口径（R64 修正版）

后续所有关于 C2 yaw-block split 的表述应遵循以下标准：

### 3.1 一句话摘要
```text
C2 used five circular yaw-block holdout folds on a 72-bin yaw grid, collectively covering all yaw bins exactly once across the five test blocks.
```

### 3.2 完整标准表述
```text
C2 used five circular yaw-block holdout folds on a 72-bin yaw grid (5° resolution).
Each fold held out one contiguous test yaw block (14-15 bins) and one adjacent validation block (7 bins).
Across the five folds, the test blocks collectively covered all 72 yaw bins exactly once.
Within each fold, training excluded the validation and test yaw bins.
This protocol evaluates unseen-yaw-bin generalization under fixed-roll phase63 data; it is not random cross-validation.
```

### 3.3 Fold 表（论文 Methods 或 SI）
```text
Fold 0: val bins 65-71 (325-355°), test bins 0-14 (0-70°),    train bins 15-64
Fold 1: val bins 8-14 (40-70°),    test bins 15-29 (75-145°), train bins 0-7 and 30-71
Fold 2: val bins 23-29 (115-145°), test bins 30-43 (150-215°), train bins 0-22 and 44-71
Fold 3: val bins 37-43 (185-215°), test bins 44-57 (220-285°), train bins 0-36 and 58-71
Fold 4: val bins 51-57 (255-285°), test bins 58-71 (290-355°), train bins 0-50

Total test coverage: 15 + 15 + 14 + 14 + 14 = 72 bins (full yaw space)
```

### 3.4 禁止表述
```text
❌ "5×7=35 test bins"
❌ "covers ~49% of yaw space"
❌ "Fold 4 wraps across 0°/360° boundary" (实际是 fold 0 val wraps)
❌ "partial yaw coverage"
❌ "approximately half of yaw angles tested"
```

---

## 4. 不需要修改的部分

以下 E35 内容经 R64 确认无误，**无需修改**：

### 4.1 Table 2/3 数值（R62 口径）
- ✅ 13 configs 全部 yaw_acc = 0.00%
- ✅ Within-3 chance-level = 7/72 = 9.72%
- ✅ Pitch accuracy = 2.56%-4.37%（secondary diagnostic）
- ✅ Yaw CMAE = 80.36°-120.26°
- ✅ Within-3 range = 2.75%-15.57%

### 4.2 Claim 边界总体方向（除 yaw coverage 红灯项外）
- ✅ 不外推为 OCS 物理无信息
- ✅ 不外推为真实未知目标姿态反演
- ✅ 不声称 image 通道必然更好（未测试 C3）
- ✅ OCS failure 必须加 fixed-protocol MLP + yaw-block holdout 限定
- ✅ Photometric OCS 分 sub-type (a) / (b)

### 4.3 其他 Figure Plans
- ✅ Figure 1: OCS Feature Extraction Pipeline（无涉及 split）
- ✅ Figure 3: Yaw CMAE vs Within-3 scatter（结果数据，不涉及 split 设计）
- ✅ Figure 4: Pitch Accuracy grouped bar（结果数据，不涉及 split 设计）

### 4.4 Supplementary Checklist
- ✅ 原清单中无 split 设计图错误
- 若后续生成 SI Figure: Split Design，使用 FIX01 修正版 Figure 2

---

## 5. 修正影响范围总结

### 5.1 需要替换的段落

**E35 Part 2 §5.2 Figure 2 全段**：
- 原"内容设计"段落 → 替换为本 FIX01 §2.1 修正版
- 原 caption 草案 → 替换为本 FIX01 §2.1 修正版 caption
- 原图注要点 → 替换为本 FIX01 §2.1 修正版图注要点

**E35 Part 3 §8.4 Claim boundary checklist 黄灯部分**：
- 删除原红灯项："C2 covers all yaw angles (只测试 35 bins...)"
- 添加本 FIX01 §2.3 的绿灯/黄灯/红灯修正版

### 5.2 需要检查的段落（若有 35/72 或 49% 提及）

**E35 Part 2 §6.2 Results skeleton 3.2**：
- 检查是否有"35/72"、"49%"、"部分 yaw space"表述
- 若有，替换为"aggregate 5-fold covers all 72 yaw bins"

**E35 Part 2 §7.2 Supplementary checklist**：
- 检查是否有 split design 相关项提到"35 bins"或"49% coverage"
- 若有，改为"72/72 bins aggregate coverage"

### 5.3 无需修改的部分（已确认）
- E35 Part 1 全部（Table 1/2/3）
- E35 Part 2 §5.1 Figure 1
- E35 Part 2 §5.3 Figure 3
- E35 Part 2 §5.4 Figure 4
- E35 Part 3 §8.2 可写 claim（绿灯项，无涉及 coverage 数值）
- E35 Part 3 §8.3 不可写 claim（红灯项，无涉及 coverage 数值，除已修正的一项）
- E35 Part 3 §9 执行总结（无涉及 split 细节）

---

## 6. 执行总结

### 6.1 FIX01 交付物

**修正内容**：
- ✅ Figure 2 plan 修正版（5-fold 实际 bins 表，72/72 aggregate coverage）
- ✅ Figure 2 caption 修正版（明确 aggregate 覆盖全部 72 bins）
- ✅ Figure 2 图注要点修正版（删除 35/72、49%、Fold 4 wrap 错误）
- ✅ Claim boundary checklist 修正版（"C2 covers all yaw angles"从红灯改为黄灯限定）
- ✅ "Nearby yaw" 表述收紧（不笼统说 preventing seeing nearby angles）
- ✅ 标准口径总结（R64 §4 全文）

**修正依据**：
- R64 Codex 审阅核验的实际 split manifest
- 5-fold test bins: 15+15+14+14+14 = 72 bins（不是 5×7=35）
- Aggregate coverage: 72/72 bins = 100%（不是 49%）

**未修改部分**（R64 确认通过）：
- Table 1/2/3 数值（R62 口径正确）
- Figure 1/3/4 plans（无涉及 split）
- Claim 边界总体方向（除 coverage 红灯项外）
- Supplementary checklist（无 split 错误）

### 6.2 窄范围修正确认

本 FIX01 是**窄范围修正**，只修正 yaw-block split 分箱事实，符合以下红线：

**遵守的红线**：
- ✅ 未启动 C3
- ✅ 未运行训练
- ✅ 未改代码
- ✅ 未写论文正文正式段落
- ✅ 未扩展到三轴小项目或路线二/三/四
- ✅ 未改 Table 2 的 R62 稳定数值（c2_screening_summary.json 无矛盾）
- ✅ 只修正 split 描述事实错误，未引入新内容

### 6.3 关键数值修正对照

| 项目 | E35 原错误 | FIX01 修正 | 依据 |
|-----|-----------|-----------|------|
| Test bins per fold | 7 bins | 15, 15, 14, 14, 14 bins | R64 fold 表 |
| Total test bins | 35 bins | 72 bins | 15+15+14+14+14 |
| Yaw space coverage | ~49% (35/72) | 100% (72/72) | Aggregate 5-fold |
| Fold 4 wrap | "wraps 0/360" | Fold 0 val wraps | 实际 bins 65-71→0-14 |
| "C2 covers all yaw" | 红灯（错误） | 黄灯限定（正确） | Aggregate coverage |

### 6.4 后续使用建议

**直接替换部分**：
- 若引用 Figure 2，使用本 FIX01 §2.1 修正版
- 若引用 claim boundary，使用本 FIX01 §2.3 修正版
- 若描述 split protocol，使用本 FIX01 §3 标准口径

**E35 + FIX01 合并版**：
- E35 Part 1：保留原样
- E35 Part 2 §5.2：替换为 FIX01 §2.1
- E35 Part 2 其他：保留原样
- E35 Part 3 §8.4：更新为 FIX01 §2.3
- E35 Part 3 其他：保留原样

**论文写作时**（若后续放行）：
- Methods 描述 split：使用 R64/FIX01 标准口径（§3.2）
- Methods 或 SI 表格：使用 5-fold bins 表（§3.3）
- Figure 2 实际绘制：基于 FIX01 §2.1 设计
- 避免所有"35 bins"、"49% coverage"、"partial yaw"表述

### 6.5 当前状态声明

```text
E35-FIX01：✅ COMPLETED
Split 分箱事实修正：✅ COMPLETE
  - Figure 2 plan/caption 修正：完成
  - Claim boundary checklist 修正：完成
  - 标准口径总结：完成
E35 + FIX01 材料包：✅ READY FOR R65 CODEX REVIEW
C3 / 论文正文 / 训练 / 代码 / 三轴 / 路线二三四：⏸️ NOT RELEASED
```

---

**执行端签名**：Claude  
**执行日期**：2026-06-26  
**下一步**：等待 Codex R65 审阅 E35-FIX01 修正，若通过则 E35 材料包进入稳定状态

---

## 附录：E35 Part 2 Figure 2 完整替换文本

### 替换前（E35 原版，错误）
```text
### 5.2 Figure 2: Circular Yaw-Block Holdout Strategy

**用途**: 说明 5-fold circular yaw-block holdout 的跨 yaw 泛化测试设计。

**内容设计**:
[包含"5 x 7 = 35 test bins"、"covers ~49% of yaw space"、"Fold 4 wraps"等错误表述]

**Caption 草案**:
[包含"preventing the model from seeing nearby yaw angles during training"笼统表述]
```

### 替换后（FIX01 修正版，正确）
```text
### 5.2 Figure 2: Circular Yaw-Block Holdout Strategy

**用途**: 说明 5-fold circular yaw-block holdout 的跨 yaw 泛化测试设计。

**内容设计（修正版）**:
[见本 FIX01 报告 §2.1 完整修正版内容]
- 明确每个 fold 的实际 val/test/train bins
- Test bins: 15, 15, 14, 14, 14（不是统一 7）
- Aggregate coverage: 72/72 bins = 100%
- Fold 0 val wraps（不是 Fold 4）

**Caption 草案（修正版）**:
[见本 FIX01 报告 §2.1 修正版 caption]
- "Across the five folds, the test blocks collectively cover all 72 yaw bins exactly once"
- "Within each fold, the model never sees the held-out test yaw bins during training"
- 删除笼统的"nearby yaw angles"表述

**图注要点（修正版）**:
[见本 FIX01 报告 §2.1 修正版图注要点]
- Aggregate test coverage: 72/72 bins (100% yaw space)
- Per-fold test: one contiguous block (14-15 bins)
```

使用时直接复制本 FIX01 §2.1 的完整文本替换 E35 Part 2 §5.2 即可。
