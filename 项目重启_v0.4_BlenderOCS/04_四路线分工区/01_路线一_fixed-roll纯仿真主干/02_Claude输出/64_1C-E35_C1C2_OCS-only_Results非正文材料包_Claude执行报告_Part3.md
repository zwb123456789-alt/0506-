## 8. Claim Boundary Checklist

### 8.1 用途

明确列出 C1/C2 Results 中可写、不可写、必须限定的表述，防止过度外推。

### 8.2 可写 Claim（绿灯）

**关于 C2 结果本身**:
- ✅ "All 13 OCS-only configurations achieved 0.00% exact-bin yaw accuracy under fixed-protocol circular yaw-block holdout."
- ✅ "C2 represents a pre-registered, fixed-protocol null result."
- ✅ "No OCS-only configuration (1-13D) demonstrated cross-yaw generalization under the current MLP architecture and holdout strategy."
- ✅ "Within-3-bins rates ranged from 2.75% to 15.57%, with visibility control configs showing the highest coarse localization."
- ✅ "Pitch exact-bin accuracy ranged from 2.56% to 4.37%, serving as a secondary diagnostic metric."

**关于方法学价值**:
- ✅ "C2 establishes a controlled OCS-only baseline for future image-only and joint-channel comparisons."
- ✅ "The null result has methodological value as a pre-registered negative outcome."
- ✅ "C2 defines an observability boundary for low-dimensional OCS features under fixed-protocol evaluation."

**关于 claim class 归因**:
- ✅ "Pure photometric OCS features (sub-type a) without pixel-count dependency all failed to generalize."
- ✅ "Visibility-normalized photometric OCS features (sub-type b, containing density terms) also failed to generalize."
- ✅ "Visibility control features (geometry-only) did not enable exact-bin yaw generalization despite higher within-3 rates."
- ✅ "Mixed OCS+visibility features showed no synergy, with all mixed configs also yielding null results."

**关于范围限定**:
- ✅ "C2 is limited to phase63 fixed-roll data, where roll is constant."
- ✅ "C2 evaluates circular yaw-block holdout generalization, not random split or other holdout strategies."
- ✅ "C2 uses a fixed MLP architecture (3-layer, 128 hidden units) with no hyperparameter search."
- ✅ "C2 does not preclude success with alternative architectures, richer feature engineering, or different training protocols."

---

### 8.3 不可写 Claim（红灯）

**关于物理结论**:
- ❌ "OCS photometry contains no attitude information."
- ❌ "OCS is physically uninformative for pose estimation."
- ❌ "OCS will fail in all pose estimation tasks."
- ❌ "This proves OCS cannot contribute to attitude determination."

**关于架构/特征泛化**:
- ❌ "All possible OCS feature engineering approaches have been exhausted."
- ❌ "Deep neural networks cannot learn from OCS."
- ❌ "No model architecture can extract pose information from OCS."
- ❌ "This result applies to all feature spaces derived from OCS."

**关于与图像通道的比较**:
- ❌ "OCS is inferior to image-based pose estimation." (C2 没有 image 对照)
- ❌ "Image channels will necessarily outperform OCS." (未测试)
- ❌ "OCS+image fusion will fail." (未测试 C3)
- ❌ "C2 proves image-only methods are sufficient." (未测试)

**关于真实系统外推**:
- ❌ "C2 results apply to real unknown-target attitude inversion systems."
- ❌ "OCS-based methods should not be deployed in operational systems."
- ❌ "This validates OCS failure in real telescopic observations."
- ❌ "GEO photometric databases cannot provide attitude supervision." (不在 C2 范围内)

**关于数据与协议**:
- ❌ "C2 covers all yaw angles." (只测试了 5×7=35 bins，约 49% 覆盖)
- ❌ "C2 represents optimal training." (固定协议，无超参搜索)
- ❌ "Within-3 random baseline is 8.3%." (FIX01 修正为 9.72%)
- ❌ "Pitch accuracy can be judged by yaw weak-positive 3% threshold." (pitch 判据独立)

---

### 8.4 必须限定的 Claim（黄灯，需加限定语）

**关于 OCS 失败**:
- ⚠️ 写"OCS features failed"时，必须加：
  - "under the current fixed-protocol MLP evaluation"
  - "in the 1-13D low-dimensional feature space tested"
  - "on phase63 fixed-roll data with circular yaw-block holdout"

**关于 photometric OCS 归因**:
- ⚠️ 写"photometric OCS null result"时，必须区分：
  - Sub-type (a): "direct OCS photometric values or ratios/logs without pixel-count dependency"
  - Sub-type (b): "OCS photometric values normalized by visibility pixel counts"
  - 不能笼统说"photometric OCS failed"而不分 a/b

**关于 within-3 解释**:
- ⚠️ 写"within-3 rates above chance"时，必须说明：
  - "chance-level = 7/72 = 9.72%"
  - "coarse localization within ±3 bins, but no exact-bin hits"
  - 不能写成"slightly better than random 8.3%"

**关于 coarse localization**:
- ⚠️ 写"visibility features show coarse localization"时，必须说明：
  - "within-3 rates of 14.8%-15.6%, above the 9.72% chance baseline"
  - "but this did not translate to exact-bin yaw generalization (0.00% yaw_acc)"
  - 不能暗示"coarse localization = partial success"而不提及 exact-bin 失败

**关于预注册**:
- ⚠️ 写"pre-registered protocol"时，必须明确：
  - "features, constants, claim classes, and holdout strategy were pre-registered before feature extraction"
  - "no post-hoc hyperparameter tuning or feature selection"
  - 不能暗示"pre-registered = optimal"或"no further improvement possible"

**关于后续工作**:
- ⚠️ 写"future work"时，可以提及但不能断言：
  - "Independent image-only and joint OCS+image comparisons (C3) are needed to evaluate channel complementarity." (候选，未放行)
  - "Alternative architectures (CNNs, Transformers) may extract richer representations." (探索方向)
  - "Three-axis free-tumbling scenarios may alter observability." (路线扩展)
  - 但不能写成"we will do C3"或"C3 is under review"（未获 Codex 放行）

---

### 8.5 写作检查表（逐条核对）

在写作 Results 正文（若后续放行）时，逐条检查：

**数值与定义检查**:
- [ ] Yaw accuracy 全部标注为 0.00%，无四舍五入为 0.0% 或 <0.01%
- [ ] Within-3 chance-level 写为 7/72 = 9.72%，不写 8.3%
- [ ] Pitch accuracy 标注为"secondary diagnostic"，不作为独立成功判据
- [ ] Yaw CMAE 单位为 degrees，pitch accuracy 单位为 %
- [ ] 5-fold 标注清楚，不写成 5-fold cross-validation（是 holdout，不是 CV）

**归因边界检查**:
- [ ] Photometric OCS 分 sub-type (a) / (b)，不笼统写"photometric OCS"
- [ ] Visibility control 不归因为 OCS photometric
- [ ] Mixed configs 不单独归因为 OCS 或 visibility，需注明"combined"

**范围限定检查**:
- [ ] 每次写"OCS failed"都加上"under fixed-protocol MLP + yaw-block holdout"
- [ ] 不写"OCS in general"或"OCS as a channel"
- [ ] 不外推到真实未知目标、operational systems、GEO database

**C3 边界检查**:
- [ ] 不写"we will do C3"
- [ ] 不写"C3 is planned/ongoing/under review"
- [ ] 只能写"future independent comparisons may include..."或"C3 remains a candidate path"

**红线最终检查**:
- [ ] 无"OCS 物理无信息"表述
- [ ] 无"真实系统验证"或"operational-ready"表述
- [ ] 无"proves OCS will always fail"表述
- [ ] 无"image must be better"表述（未测试）

---

## 9. 执行总结

### 9.1 E35 交付物清单

**Part 1（已完成）**:
- Table 1: OCS Feature Configuration Overview（14 configs，含 sub-type 标注）
- Table 2: C2 OCS-Only Screening Results（13 configs，R62 稳定口径）
- Table 3: C2 Results Grouped by Claim Class（按 claim class 分组汇总）

**Part 2（已完成）**:
- Figure 1 plan: OCS Feature Extraction Pipeline（流程图 + caption 草案）
- Figure 2 plan: Circular Yaw-Block Holdout Strategy（5-fold 示意图 + caption 草案）
- Figure 3 plan: Yaw CMAE vs Within-3-Bins Rate（scatter plot + 数据表 + caption 草案）
- Figure 4 plan: Pitch Accuracy by Config（grouped bar chart + 数据表 + caption 草案）
- Results skeleton: 章节结构与 bullet 要点（3.1-3.5，不含完整段落）
- Supplementary material checklist: 优先级分级清单

**Part 3（当前）**:
- Claim boundary checklist: 可写/不可写/必须限定的表述清单
- 写作检查表: 逐条核对项
- 执行总结

### 9.2 关键口径确认

**C2 核心数值**（R62 稳定版）:
- 13 configs × 5 folds = 65 runs，全部 yaw_acc = 0.00%
- Within-3 chance-level = 7/72 = 9.72%（不再写 8.3%）
- Pitch accuracy = 二级诊断指标（不套用 yaw 判据）
- Yaw CMAE 范围：80.36°-120.26°
- Within-3 范围：2.75%-15.57%
- Pitch accuracy 范围：2.56%-4.37%

**归因边界**（FIX01 修正版）:
- Photometric OCS sub-type (a): 纯光度，无 pixel-count 依赖（6 configs）
- Photometric OCS sub-type (b): visibility-normalized photometric（3 configs）
- Visibility control: 纯几何，零光度信息（2 configs）
- Mixed: OCS+visibility 组合（2 configs）

**Claim 边界**（R62 通过版）:
- ✅ 可写：C2 固定协议 null result，方法学价值，observability boundary baseline
- ❌ 不可写：OCS 物理无信息，真实系统外推，架构泛化断言，图像通道比较
- ⚠️ 必须限定：加上 fixed-protocol MLP + yaw-block holdout + phase63 fixed-roll 限定语

### 9.3 材料包用途说明

本材料包是 **论文准备资产**，不是论文正文：

**直接可用部分**:
- Table 1/2/3 可直接转为 LaTeX/Word 表格格式
- Figure 1-4 caption 草案可作为图注初稿
- Supplementary checklist 可指导 SI 材料准备
- Claim boundary checklist 可作为写作红线检查清单

**需后续展开部分**（当前未放行）:
- Results skeleton 的 bullet 要点需展开为完整段落
- Figure 1-4 需实际绘制（当前只有 plan + 数据表）
- Supplementary material 需实际生成文件
- Abstract / Introduction / Discussion 需另行撰写（当前禁止）

**与 C3 的关系**:
- 本材料包基于路径 A（接受 C2 null，不启动 C3）
- 若后续 Codex 放行 C3，需合并 C3 结果扩展 Results
- 当前 C3 未放行，本材料包独立成立

### 9.4 红线遵守确认

**E35 禁止项检查**（全部遵守）:
- ✅ 未启动 C3
- ✅ 未运行训练
- ✅ 未改代码
- ✅ 未做后验 OCS-only 架构/特征搜索
- ✅ 未写 Results 正文完整段落（只写 bullet 骨架）
- ✅ 未写 Abstract / Introduction / Discussion 正文
- ✅ 未启动三轴小项目、路线二/三/四
- ✅ 未把 C2 null result 写成 OCS 物理无信息
- ✅ 未外推到真实未知目标姿态反演
- ✅ 未把 within-3 随机基线写成 8.3%（使用 9.72%）
- ✅ 未把 pitch_acc 套用 yaw weak-positive 3% 判据

### 9.5 下一步建议（供 Codex 裁决）

**若路径 A 继续推进**（当前选择）:
1. 审阅本材料包（E35 产物）
2. 若通过，可放行：
   - 将 Table 1/2/3 转为 LaTeX 格式
   - 绘制 Figure 1-4 实际图片
   - 生成 Supplementary S1/S2 表格
   - 将 Results skeleton bullet 展开为完整段落（需再次放行）
3. 后续考虑 Abstract / Introduction / Discussion 撰写（需再次放行）

**若后续考虑路径 B（C3）**（当前未放行）:
1. 需 Codex 另行裁决 C3 前置条件（GPU、image data、protocol lock）
2. 若放行 C3，本材料包作为 C2 baseline 保留
3. C3 结果合并后，需重新整合 Results 章节

**若启动其他路线**（当前未放行）:
- 三轴小项目：需等路线一 C 主线稳定
- 路线二 GEO 锚点：可并行，不依赖 C3
- 路线三暗室实验：建议等路线一 C 闭合

### 9.6 当前状态声明

```text
E35：COMPLETED
材料包交付：COMPLETE
  - Table 1/2/3 草案：3 个表格完成
  - Figure 1-4 plan：4 个图规划完成
  - Results skeleton：5 个小节骨架完成
  - Supplementary checklist：完成
  - Claim boundary checklist：完成
路径 A 材料准备：READY FOR CODEX REVIEW
C3 / 论文正文 / 三轴小项目 / 路线二三四：NOT RELEASED
```

---

**执行端签名**：Claude  
**执行日期**：2026-06-26  
**下一步**：等待 Codex 审阅 E35 材料包，裁决后续放行范围

---

## 附录 A：数据完整性核验

### A.1 Table 2 数据溯源

所有 Table 2 数值均来自 `c2_screening_summary.json` 的 `aggregate_metrics` 字段，已机器核验：

| Config | mean_test_yaw_acc | std_test_yaw_acc | 数据源行号 |
|--------|-------------------|------------------|-----------|
| baseline_4dim | 0.0 | 0.0 | Line 75-76 |
| R_ratio_2d | 0.0 | 0.0 | Line 148-149 |
| R_ratio_3d | 0.0 | 0.0 | Line 222-223 |
| I_interpart_1d | 0.0 | 0.0 | Line 294-295 |
| N_density_3d | 0.0 | 0.0 | Line 368-369 |
| L_logratio_3d | 0.0 | 0.0 | Line 442-443 |
| M1_ratio_log_5d | 0.0 | 0.0 | Line 518-519 |
| M3_density_ratio_5d | 0.0 | 0.0 | Line 594-595 |
| M4_log_density_ratio_9d | 0.0 | 0.0 | Line 674-675 |
| P_pixelfrac_3d | 0.0 | 0.0 | Line 748-749 |
| M5_pixelfrac_only_4d | 0.0 | 0.0 | Line 823-824 |
| M2_ratio_pixelfrac_5d | 0.0 | 0.0 | Line 899-900 |
| M6_all_nongeo_13d | 0.0 | 0.0 | Line 983-984 |

**核验结果**：13 configs 全部 yaw_acc = 0.0，std = 0.0，与 R62 稳定口径一致。

### A.2 Within-3 Chance-Level 计算

```text
72-bin yaw grid, circular distance ≤ 3 bins (including exact bin)
Bins within distance ≤ 3: {-3, -2, -1, 0, +1, +2, +3} = 7 bins
Chance-level = 7 / 72 = 0.09722... = 9.72%
```

**FIX01 修正前**：错误使用 6/72 = 8.3%（未包含 exact bin）  
**FIX01 修正后**：正确使用 7/72 = 9.72%（包含 exact bin）

本材料包全部使用 9.72% 作为 within-3 chance-level baseline。

### A.3 Claim Class 分组核验

| Claim Class | Config IDs | N Configs | 来源 |
|------------|-----------|-----------|------|
| Photometric OCS (a) | 1, 2, 3, 4, 6, 7 | 6 | feature_definitions.json |
| Photometric OCS (b) | 5, 8, 9 | 3 | feature_definitions.json |
| Visibility control | 10, 11 | 2 | feature_definitions.json |
| Mixed OCS+visibility | 12, 13 | 2 | feature_definitions.json |
| Constant sanity check | 14 | 1 (excluded from C2) | feature_definitions.json |

**Sub-type 划分依据**:
- **(a)**: feature_keys 不含 `ocs_density_*` 字段
- **(b)**: feature_keys 含 `ocs_density_*` 字段（OCS photometric / pixel_count）

核验通过，分组无误。

---

**材料包完整性确认**：Part 1 + Part 2 + Part 3 全部完成。
