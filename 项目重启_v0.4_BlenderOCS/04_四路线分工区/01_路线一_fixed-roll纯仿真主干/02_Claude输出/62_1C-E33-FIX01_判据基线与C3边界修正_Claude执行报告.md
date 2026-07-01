# 62_1C-E33-FIX01_判据基线与C3边界修正_Claude执行报告

执行端：Claude  
任务编号：1C-E33-FIX01  
任务名称：修正 C1/C2 证据包中的判据基线、pitch 解释和 C3 边界  
执行日期：2026-06-26  

---

## 0. 执行裁决

```text
1C-E33-FIX01：COMPLETED
Within-3-bins 随机基线修正：COMPLETE
Pitch_acc 解释修正：COMPLETE
C3 边界修正：COMPLETE
图表规划优化：COMPLETE
```

本报告针对 E33 原报告（Part1 + Part2）中的三个 Major 问题和一个 Minor 问题进行修正，不重写全部内容，仅提供修正段落和替换说明。

---

## 1. 任务依据

### 1.1 输入文件

```text
依据文件：
- CLAUDE.md
- R61_Codex_审阅_1C-E33需FIX01_判据基线与C3边界修正.md
- 61_1C-E33_C1C2证据包与claim边界整理_Claude执行报告_Part1.md
- 61_1C-E33_C1C2证据包与claim边界整理_Claude执行报告_Part2.md
- v0.4_results/05_c2_screening/c2_screening_summary.json
```

### 1.2 修正范围

根据 R61 Codex 审阅，需修正：

**Major 1：Within-3-bins 随机基线错误**
- 位置：E33 Part1 第 3.4 节、Part2 第 5.1 节
- 问题：写"略高于随机 8.3%"，应为 9.72%（7/72 bins）

**Major 2：Pitch_acc 不能套用 yaw 判据**
- 位置：E33 Part1 第 4.2 节
- 问题：写"远低于 weak_positive 阈值 3%"，C2 判据仅适用于 yaw

**Major 3：C3 框架不得出现"推荐放行"口吻**
- 位置：E33 Part2 第 6.5 节
- 问题：写"Claude 建议：推荐放行 C3"，越界裁决

**Minor 1：全 0 bar chart 价值有限**
- 位置：E33 Part2 第 7.2 节
- 建议：降级为 supplement

---

## 2. 修正 1：Within-3-bins 随机基线（Major 1）

### 2.1 原表述（E33 Part1 第 3.4 节）

```text
❌ 原文：
"yaw within-3-bins rate 范围 2.75%-15.57%，略高于随机（8.3%），但未转化为精度"
```

### 2.2 修正后表述

```text
✅ 修正：
"yaw within-3-bins rate 范围 2.75%-15.57%。在 72-bin yaw 网格下，若 within-3-bins 
按 circular distance ≤ 3 计算（包含 exact bin），则 chance-level 为 7/72 = 9.72%。
13 个配置中，部分低于该基线（如 I_interpart_1d: 2.75%），部分高于该基线
（如 M5_pixelfrac_only_4d: 15.57%），整体显示局部 coarse localization 信号，
但均未转化为 exact-bin yaw accuracy。"
```

### 2.3 修正原因

**错误分析**：
- 72 yaw bins，circular distance ≤ 3 包含：exact bin + 左右各 3 bins = 7 bins
- 随机基线：7 / 72 = 9.72%，不是 8.3%
- 8.3% 约等于 6/72，可能是不含 exact bin 的 ±3 邻近窗口，但与指标定义不符

**修正内容**：
- 随机基线改为 9.72%
- 删除"略高于随机"的笼统表述
- 改为具体分析：部分配置低于基线，部分高于基线
- 定性为"局部 coarse localization"，不过度解读

### 2.4 相关位置的连带修正

**E33 Part2 第 5.1 节（可写边界）中的相关表述**：

```text
❌ 原文：
"yaw within-3-bins rate 范围 2.75%-15.57%，略高于随机（8.3%），但未转化为 exact-bin accuracy"

✅ 修正：
"yaw within-3-bins rate 范围 2.75%-15.57%（chance-level 9.72%），显示局部 coarse 
localization，但未转化为 exact-bin accuracy"
```

**E33 Part1 第 3.2 节（baseline_4dim 示例）中的相关表述**：

```text
❌ 原文：
"Within_3_bins_rate ≈ 8.2%，略高于随机的 8.3%，说明预测有轻微聚集但未命中正确 bin"

✅ 修正：
"Within_3_bins_rate ≈ 8.2%（略低于 chance-level 9.72%），说明预测有轻微聚集但未命中 exact bin"
```

---

## 3. 修正 2：Pitch_acc 解释（Major 2）

### 3.1 原表述（E33 Part1 第 4.2 节）

```text
❌ 原文：
"Pitch Acc Range (%): 2.56 - 4.37
汇总结论：
- Pitch acc 整体微弱（2.56-4.37%），远低于 weak_positive 阈值（3%）"
```

### 3.2 修正后表述

```text
✅ 修正：
"Pitch Acc Range (%): 2.56 - 4.37
汇总结论：
- Pitch acc 仅作为二级诊断指标（2.56-4.37%）；部分配置 pitch exact-bin accuracy 
  达到约 3-4%，但 C2 成败判据由跨 yaw holdout 泛化决定，这些 pitch 值不改变 
  C2 null result 判定。"
```

### 3.3 修正原因

**错误分析**：
1. C2 的 strong / weak / null 判据是为 `yaw_acc` 设定的主判据
2. Pitch 不是主要目标轴，不应直接套用 yaw 的 weak_positive 3% 阈值
3. 多个配置的 pitch mean 已高于 3%（如 M4: 4.37%, N_density_3d: 3.41%），"远低于 3%"数值上也不成立

**修正内容**：
- 删除"远低于 weak_positive 阈值 3%"
- 明确 pitch 只是二级诊断指标
- 强调 C2 判据由 yaw 泛化决定

### 3.4 相关位置的连带修正

**E33 Part1 第 3.2 节（所有配置的通用特征）**：

```text
❌ 原文：
"Pitch acc ≈ 1-4% (微弱信号，不足 weak_positive)"

✅ 修正：
"Pitch acc ≈ 1-4%（二级诊断，非 C2 主判据）"
```

**E33 Part2 第 5.1 节（可写的具体表述 - 结果层面）**：

增加一条明确说明：

```text
5. "Pitch exact-bin accuracy 作为二级诊断指标，部分配置达到 3-4%，但不影响 
   C2 null result 判定（C2 主判据为 yaw 跨 holdout 泛化）"
```

---

## 4. 修正 3：C3 边界（Major 3）

### 4.1 原表述（E33 Part2 第 6.5 节）

```text
❌ 原文：
"Claude 建议：

优先级 1（推荐）：
放行 C3 作为独立对照实验，明确目标为 OCS-only vs image-only vs joint 对照。
先执行 image-only baseline (single architecture, e.g., ResNet18) 和 
simple joint (early fusion) 各 5 folds，评估是否达到 weak_positive。

优先级 2（备选）：
接受 C2 null result，暂不启动 C3，转向：
- 整理 C1/C2 为论文 Results 草稿
- 启动三轴小项目（最亮构型、高信息姿态）
- 引入路线二 GEO 真实光度锚点"
```

### 4.2 修正后表述

```text
✅ 修正：
"当前状态与待 Codex 裁决选项：

C3、三轴小项目、路线二/三/四、论文正文正式改写均未放行。
本报告仅提供 C3 论证框架和后续路径候选，不构成执行建议。

若 Codex 另行放行 C3，可采用的最小对照设计：
- 目标：OCS-only vs image-only vs joint 独立对照（不由 C2 触发）
- 架构：image-only baseline (e.g., ResNet18) + simple joint (early fusion)
- 评估：各 5 folds circular yaw_block holdout
- 判据：与 C2 一致（strong/weak/null）

待 Codex 裁决的其他路径选项：
- 选项 A：放行 C3 对照实验
- 选项 B：接受 C2 null，整理论文 Results，待后续路线
- 选项 C：补救 OCS-only（exploratory，另立任务）

当前不推荐、不放行任何路径，仅列出候选供裁决参考。"
```

### 4.3 修正原因

**错误分析**：
- E33 任务是"给出论证框架"，不是阶段门裁决
- Claude 不得把"放行 C3"作为推荐结论
- 不得把三轴小项目、路线二写成可直接启动的下一步

**修正内容**：
- 删除"Claude 建议：优先级 1（推荐）"的裁决口吻
- 改为"若 Codex 另行放行，可采用的候选设计"
- 明确 C3、三轴、路线二/三/四、论文正文均未放行
- 路径 A/B/C 改为"待 Codex 裁决选项"，不写成执行建议

### 4.4 相关位置的连带修正

**E33 Part2 第 6.1 节（为什么需要 Image/Joint 对照）末尾增加**：

```text
"注：本节仅论证 C3 对照实验的科学理由，不构成放行建议。C3 是否执行、何时执行，
由 Codex 另行裁决。"
```

**E33 Part2 第 9.2 节（待 Codex 裁决的问题）前增加声明**：

```text
"以下问题仅作为待裁决选项列出，E33 不对任何选项做推荐或放行判断。"
```

---

## 5. 修正 4：图表规划优化（Minor 1）

### 5.1 原表述（E33 Part2 第 7.2 节）

```text
❌ 原文：
"Figure 3：C2 Yaw Accuracy by Config (Bar Chart)
- 内容：13 个配置的 test_yaw_acc（全部 0.00%）+ error bar
- 用途：直观展示 null result"
```

### 5.2 修正后表述

```text
✅ 修正：
"Figure 3：C2 Yaw CMAE and Within-3-Bins Rate (Scatter Plot)
- 内容：X 轴 yaw_cmae，Y 轴 within_3_bins_rate，每个 config 一个点，
  按 claim_class 分组着色
- 用途：展示虽有局部 coarse localization（部分配置 within-3 > 9.72%）
  但未转化为 exact-bin accuracy 的失败模式

注：原 Figure 3（13 个配置全为 0 的 yaw_acc bar chart）降级为 Supplementary 
Figure S3 或直接合并进 Table 2，主文优先展示更有信息量的 CMAE / within-3 分布。"
```

### 5.3 修正后主文图表清单

**主文拟用图表**（优先级顺序）：

**Figure 1**：Feature Extraction Pipeline（方法可视化）  
**Figure 2**：Circular Yaw_Block Holdout Strategy（5-fold 示意）  
**Figure 3**：Yaw CMAE vs Within-3-Bins Rate Scatter（失败模式分析）  
**Figure 4**：Pitch Accuracy vs Config (Grouped by Claim Class)（二级诊断）  
**Figure 5（如果 C3 执行）**：Channel Comparison (OCS / Image / Joint)  

**降级到 Supplementary 的图表**：
- **Supplementary Figure S3**：C2 Yaw Accuracy by Config (全 0 bar chart)
- **Supplementary Figure S4**：Per-Fold Strip Plot（显示 fold-level 分布）

### 5.4 修正原因

**问题分析**：
- 13 个配置全为 0 的 bar chart 信息量低
- 主文应优先展示有变异的指标（CMAE / within-3）
- Scatter plot 更能展示配置间差异和失败模式

**修正内容**：
- 将全 0 yaw_acc bar chart 降级为 supplement
- 主文 Figure 3 改为 CMAE vs within-3 scatter
- 增加 claim_class 分组着色，增强归因分析

---

## 6. 修正汇总表

### 6.1 修正清单

| 修正项 | 位置 | 原表述关键词 | 修正关键词 | 状态 |
|--------|------|--------------|------------|------|
| Within-3 基线 | Part1 §3.4, Part2 §5.1 | 略高于随机 8.3% | Chance-level 9.72%, 局部 coarse localization | ✅ |
| Pitch 判据 | Part1 §3.2, §4.2, Part2 §5.1 | 远低于 weak_positive 3% | 二级诊断指标，不改变 C2 null result | ✅ |
| C3 边界 | Part2 §6.1, §6.5, §9.2 | Claude 建议推荐放行 C3 | 若 Codex 另行放行，待裁决选项 | ✅ |
| 图表规划 | Part2 §7.2 | Figure 3 全 0 bar chart | 降级为 supplement，改为 scatter | ✅ |

### 6.2 修正后的核心表述更新

**Within-3-bins 解释（标准表述）**：
```text
在 72-bin yaw 网格下，circular distance ≤ 3 的 chance-level 为 7/72 = 9.72%。
C2 结果中，within-3-bins rate 范围 2.75%-15.57%，部分配置低于基线，部分高于基线，
整体显示局部 coarse localization 信号，但均未转化为 exact-bin yaw accuracy。
```

**Pitch_acc 解释（标准表述）**：
```text
Pitch exact-bin accuracy 仅作为二级诊断指标。部分配置达到约 3-4%，但 C2 成败判据
由跨 yaw holdout 泛化决定，这些 pitch 值不改变 C2 null result 判定。
```

**C3 边界（标准表述）**：
```text
C3、三轴小项目、路线二/三/四、论文正文正式改写均未放行。
本报告仅提供 C3 论证框架和后续路径候选，不构成执行建议。
若 Codex 另行放行 C3，可采用 image-only baseline + simple joint (early fusion) 的
最小对照设计，评估 OCS-only vs image-only vs joint 在相同 yaw_block holdout 下的性能。
```

---

## 7. E33 可保留内容确认

根据 R61，以下 E33 内容**无需修正，可直接保留**：

### 7.1 C1 证据包部分（E33 Part1 第 2 节）
- ✅ C1 配置完整性（14 个配置，13 个参与 C2）
- ✅ C1 预注册验证（未被修改，常量自检通过）
- ✅ C1 配置分组（A/B/C/D 组，归因边界清晰）

### 7.2 C2 证据包部分（E33 Part1 第 3 节）
- ✅ C2 训练完成度（65/65 runs，固定协议）
- ✅ C2 null result 判定（13/13 configs yaw_acc = 0.00%）
- ✅ C2 归因分析（photometric OCS / visibility control / mixed 全部 null）

### 7.3 C2 表格主体（E33 Part1 第 4 节）
- ✅ 完整表格（13 个配置，数值与 summary 对齐）
- ✅ 分组汇总表（按 claim_class 分类）
- 注：仅需修正 within-3 和 pitch 的文字解释，表格数值本身无误

### 7.4 Claim 边界主体（E33 Part2 第 5 节）
- ✅ 可写边界：固定协议下 OCS-only null result
- ✅ 不可写边界：不过度外推到物理/真实/所有条件
- ✅ 必要限定语：协议/数据/任务限定
- 注：仅需修正 within-3 和 pitch 的具体表述

### 7.5 C3 论证框架主体（E33 Part2 第 6 节）
- ✅ C3 科学理由（互补性论证、通道归因、失败模式分析）
- ✅ C3 实验设计框架（输入通道、架构选择、判据、预期场景）
- ✅ C3 启动前置条件（必要条件、可选前提、资源评估）
- 注：仅需修正 6.5 节的"推荐放行"口吻

---

## 8. 红线符合性检查

### 8.1 禁止项检查

| 禁止项 | 状态 | 说明 |
|--------|------|------|
| 启动 C3 | ✅ 未违反 | 仅修正论证框架边界 |
| 做后验超参搜索 | ✅ 未违反 | 未涉及 |
| 做后验架构搜索 | ✅ 未违反 | 未涉及 |
| 改特征定义/数据 | ✅ 未违反 | 仅修正文字表述 |
| 写论文正文 | ✅ 未违反 | 仅修正证据包边界 |
| 启动 B1/GGX | ✅ 未违反 | 未涉及 |
| 启动三轴小项目 | ✅ 未违反 | 已删除"启动"口吻 |
| 启动路线二/三/四 | ✅ 未违反 | 已删除"启动"口吻 |

### 8.2 完成项检查

| 要求项 | 状态 | 说明 |
|--------|------|------|
| 修正 within-3 基线 | ✅ 已完成 | 改为 9.72%，局部 coarse localization |
| 修正 pitch 解释 | ✅ 已完成 | 改为二级诊断，不套用 yaw 判据 |
| 修正 C3 边界 | ✅ 已完成 | 删除"推荐放行"，改为待裁决选项 |
| 优化图表规划 | ✅ 已完成 | 全 0 bar chart 降级为 supplement |

---

## 9. 使用说明

### 9.1 如何应用本修正报告

本报告**不替代** E33 Part1 + Part2，而是提供**修正段落**。应用方式：

**方式 A：在 E33 原文基础上局部替换**
- 按第 2-5 节的修正内容，替换 E33 相应段落
- 保留 E33 其他未涉及的内容

**方式 B：生成 E33-FIX01 完整版**
- 由 Codex 或作者判断是否需要重新生成完整报告
- 如需重新生成，按本报告修正内容合并 E33 原文

**方式 C：作为补充附件**
- E33 Part1 + Part2 保留为初版
- 本报告作为 FIX01 补丁附件
- 论文写作时以 FIX01 修正为准

### 9.2 后续 Codex 审阅检查点

请 Codex 复审时确认：

**修正完整性**：
- [ ] Within-3-bins 随机基线已改为 9.72%
- [ ] Pitch_acc 不再套用 yaw weak_positive 3% 判据
- [ ] C3 框架已删除"推荐放行"口吻
- [ ] 全 0 bar chart 已降级为 supplement

**边界遵守**：
- [ ] C3、三轴、路线二/三/四、论文正文均未放行
- [ ] E33-FIX01 未启动任何新实验
- [ ] E33-FIX01 未修改代码/数据/特征定义

**科学准确性**：
- [ ] Within-3 解释为"局部 coarse localization"
- [ ] Pitch 明确为"二级诊断指标"
- [ ] C3 框架保留为"待裁决选项"

---

## 10. 执行总结

### 10.1 FIX01 交付物

**主报告**：
- 62_1C-E33-FIX01_判据基线与C3边界修正_Claude执行报告.md

**修正内容**：
1. Within-3-bins 随机基线：8.3% → 9.72%，局部 coarse localization
2. Pitch_acc 解释：删除 weak_positive 3% 判据，改为二级诊断指标
3. C3 边界：删除"推荐放行"，改为"若 Codex 另行放行的候选设计"
4. 图表规划：全 0 bar chart 降级为 supplement，主文改为 scatter

### 10.2 关键修正点

**Within-3-bins 标准表述**：
```text
72-bin yaw 网格，chance-level = 7/72 = 9.72%
C2 结果 2.75%-15.57%，显示局部 coarse localization，但未转化为 exact-bin accuracy
```

**Pitch_acc 标准表述**：
```text
Pitch 仅作二级诊断指标，部分配置 3-4%，但不改变 C2 null result（判据由 yaw 决定）
```

**C3 边界标准表述**：
```text
C3、三轴、路线二/三/四、论文正文均未放行
本报告仅提供论证框架，不构成执行建议
若 Codex 另行放行，可采用 image-only + joint (early fusion) 最小对照设计
```

### 10.3 后续路径（供 Codex 裁决）

**待裁决问题**：
1. E33-FIX01 修正是否充分？
2. C1/C2 证据包是否可进入成果区？
3. 是否放行 C3 独立对照实验？
4. 是否放行论文 Results 草稿生成？
5. 后续路径选择（C3 / 三轴 / 路线二 / 接受 null 收束）？

---

**执行端签名**：Claude  
**执行日期**：2026-06-26  
**下一步**：等待 Codex 审阅 E33-FIX01，裁决 C1/C2 证据包是否进入成果区及后续路径
