# R61 Codex 审阅：1C-E33 需 FIX01，修正判据基线与 C3 边界

最后更新：2026-06-26  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  61_1C-E33_C1C2证据包与claim边界整理_Claude执行报告_Part1.md
  61_1C-E33_C1C2证据包与claim边界整理_Claude执行报告_Part2.md

v0.4_results/05_c2_screening/c2_screening_summary.json
v0.4_results/04_ocs_features/feature_definitions.json
```

---

## 0. 裁决

```text
1C-E33：NEEDS FIX01
C1/C2 证据包主体：基本完整
C2 表格数值：基本对齐 summary
Claim 边界：主体方向正确，但需修正判据表述
C3 论证框架：可保留为待裁决框架，但需移除“推荐放行”式口吻
C3 joint 复验：NOT RELEASED
论文正文正式改写：NOT RELEASED
三轴小项目、路线二/三/四扩展：NOT RELEASED
```

E33 主体工作是有价值的：它把 C1/C2 证据、C2 表格草案、claim 边界和后续 image/joint 对照框架放到了一起，表格主要数值与 `c2_screening_summary.json` 对齐。但目前不能直接通过，因为有两类会污染后续论文表达的问题：

1. `within-3-bins` 随机基线写错，且相关文字把部分结果误判为“略高于随机”。
2. `pitch_acc` 被错误套用了 C2 的 `yaw_acc` weak-positive 判据。
3. C3 论证框架中出现了 Claude “推荐放行 C3”和“启动三轴/路线二”的口吻，超出 E33 只做论证框架的边界。

因此需要一次窄范围 FIX01：只修正判据、随机基线、pitch 解释和 C3 边界，不重跑训练、不改代码、不扩展实验。

---

## 1. 上下文恢复

本轮已读取：

```text
CLAUDE.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
  R60_Codex_审阅_1C-E32通过并接受C2_OCS-only负结果.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  61_1C-E33_C1C2证据包与claim边界整理_Claude执行报告_Part1.md
  61_1C-E33_C1C2证据包与claim边界整理_Claude执行报告_Part2.md
04_四路线分工区/00_总览与裁决/00_路线冻结文件区/
  24_v0.4项目论文主线最终冻结稿_OCS口径形态与mismatch账面对齐版.md
03_项目说明与规划材料/03_专家意见/
  00_专家三方向质疑原文_20260617.txt
03_项目说明与规划材料/04_GEO数据库说明/
  01_GEO真实光度数据库信息整合_供回看确认.md
```

主线校准：

- v0.4 不是真实未知目标姿态反演系统。
- 主线是 model-known 条件下 OCS 光度通道与图像通道的可观测性、互补性和置信一致性。
- GEO 真实光度数据无三轴姿态真值，只能作为真实光度/几何锚点，不能写成监督姿态反演数据集。
- C3 未由 C2 自动触发；若未来启动，必须另经 Codex 放行。

---

## 2. 机器核验

Codex 重新从 `c2_screening_summary.json` 读取 E32 聚合结果，确认 E33 的主表数值基本正确：

```text
13 configs
all mean_test_yaw_acc = 0.00%
all std_test_yaw_acc = 0.00%
Yaw CMAE / within-3 / pitch_acc 数值与 summary 基本一致
```

示例：

```text
baseline_4dim：yaw=0.00±0.00, cmae=89.25±33.59, within3=8.16±7.11, pitch=2.56±1.05
M5_pixelfrac_only_4d：yaw=0.00±0.00, cmae=95.75±41.24, within3=15.57±6.76, pitch=2.59±0.44
M4_log_density_ratio_9d：yaw=0.00±0.00, cmae=115.74±28.17, within3=12.05±4.61, pitch=4.37±1.22
```

因此 E33 的主要问题不是表格抄错，而是解释文字和下一步边界。

---

## 3. 必须修正的问题

### Major 1：`within-3-bins` 随机基线写错

E33 Part 2 写道：

```text
yaw within-3-bins rate 范围 2.75%-15.57%，略高于随机（8.3%）
```

该表述不可靠。当前 yaw 分类为 72 bins；若 `within_3_bins` 按 circular bin distance `<= 3` 计算，则随机命中窗口包含：

```text
真值 bin 本身 + 左右各 3 个 bin = 7 bins
随机基线 = 7 / 72 = 9.72%
```

`8.3%` 只对应 `6 / 72`，更像是不含 exact bin 的 `±3` 邻近窗口，但 E31/R59 的指标语义和 result JSON 中的 `within_3_bin_count` 应按 `<= 3` 包含 exact bin 理解。因此 E33 不能写“随机 8.3%”。

修正要求：

- 将 `within-3-bins` 随机基线改为 `9.72%`，或删除随机基线比较。
- 若保留比较，必须写清楚：

```text
Under a 72-bin yaw grid, the chance-level within-3-bin rate is 7/72 = 9.72% when the exact bin is included.
```

- 重新解释 within-3 结果：13 个配置中有些低于 9.72%，有些高于 9.72%，整体只能称为“局部 weak localization / coarse clustering signal”，不能笼统说“略高于随机”。

### Major 2：`pitch_acc` 不能套用 C2 的 yaw weak-positive 判据

E33 Part 1 写道：

```text
Pitch acc 整体微弱（2.56-4.37%），远低于 weak_positive 阈值（3%）
```

这句话有两个问题：

1. C2 的 strong / weak / null 判据是为 `yaw_acc` 设定的主判据，不应直接套到 `pitch_acc`。
2. 表中多个 pitch mean 已经高于 3%，例如 `M4_log_density_ratio_9d = 4.37%`，所以“远低于 3%”在数值上也不成立。

修正要求：

- 删除“pitch 远低于 weak_positive 阈值 3%”。
- 改写为：

```text
Pitch accuracy is reported as a secondary diagnostic only. Several configurations show weak pitch exact-bin accuracy around 3-4%, but C2 success/failure is determined by yaw generalization; these pitch values do not alter the C2 null-result verdict.
```

中文可写：

```text
Pitch acc 仅作为二级诊断指标；部分配置在 pitch exact-bin 上达到约 3-4%，但 C2 的成败判据由跨 yaw holdout 泛化决定，因此不改变 C2 null result 判定。
```

### Major 3：C3 框架中不得出现 Claude “推荐放行 C3”的裁决口吻

E33 Part 2 中写有：

```text
Claude 建议：优先级 1（推荐）：放行 C3 作为独立对照实验
路径 A：执行 C3 对照实验 - 放行 image-only + joint
路径 B：启动三轴小项目，引入路线二 GEO 真实光度锚点
```

E33 的任务是“给出论证框架”，不是阶段门裁决。Claude 可以列出可选路径和利弊，但不能把“放行 C3”作为推荐结论，也不能把三轴小项目或路线二写成可直接启动的下一步。

修正要求：

- 将“推荐放行 C3”改为“若 Codex 另行放行 C3，可采用的最小对照设计”。
- 将“路径 A/B/C”改成“待 Codex 裁决选项”，不能写成执行建议。
- 明确当前状态：

```text
C3, 三轴小项目、路线二/三/四仍未放行；本报告只提供论证框架。
```

- 保留 C3 的科学理由可以，但必须写成：

```text
C3 would not be triggered by a positive C2 result; it would be a separate controlled comparison to test image-only and joint-channel behavior against the OCS-only null baseline.
```

### Minor 1：论文图表规划中的 “13 个全为 0 的 bar chart” 价值有限

E33 建议 Figure 3 为 13 个配置的 yaw_acc bar chart，全部为 0。该图可作为 supplementary，但主文中更有信息量的是：

- `yaw_cmae` vs `within_3_bin_rate` scatter。
- grouped table by claim_class。
- per-fold distribution 或 fold-level strip plot。

修正建议：

- 将全 0 yaw_acc bar chart 降级为 supplement 或合并进 Table 2。
- 主文优先保留 `CMAE / within-3 / pitch diagnostic` 图。

该项不阻塞 FIX01，但建议同步修正。

---

## 4. 可保留内容

以下内容可保留为 E33 的主体成果：

- C1 配置分组与归因边界。
- C2 13 配置表格主体。
- `yaw_acc = 0.00%` 的 null result 判定。
- “可写/不可写”边界清单中关于不过度外推的主体表述。
- C3 作为独立对照实验的论证框架，但必须去除“推荐放行/启动”的执行口吻。

特别是以下边界写法是正确的，应保留：

```text
不可写：OCS 光度在物理上不含姿态信息。
不可写：OCS 在所有模型/架构下都失败。
不可写：证明 OCS 不如图像通道。
不可写：外推至真实未知目标。
```

---

## 5. 阶段门判断

```text
E33 证据整理完整性：CONDITIONAL PASS
E33 表格数值：PASS
E33 判据解释：NEEDS FIX01
E33 C3 边界：NEEDS FIX01
C3：NOT RELEASED
论文正文正式改写：NOT RELEASED
```

在 FIX01 完成并通过前，不把 E33 作为稳定成果进入 `01_成果区/`，也不根据 E33 放行 C3、三轴小项目、路线二/三/四或论文正文改写。

---

## 6. 给 Claude 的 E33-FIX01 短提示词

```text
执行 1C-E33-FIX01：修正 C1/C2 证据包中的判据基线、pitch 解释和 C3 边界。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R61_Codex_审阅_1C-E33需FIX01_判据基线与C3边界修正.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/61_1C-E33_C1C2证据包与claim边界整理_Claude执行报告_Part1.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/61_1C-E33_C1C2证据包与claim边界整理_Claude执行报告_Part2.md
- v0.4_results/05_c2_screening/c2_screening_summary.json

任务：
1. 不运行训练，不改代码，不启动 C3。
2. 生成一个 FIX01 修正报告，不必重写全部 E33。
3. 修正 within-3-bins 随机基线：
   - 72 yaw bins，within_3 若包含 exact bin，则 chance = 7/72 = 9.72%。
   - 删除或修正“略高于随机 8.3%”。
   - 改为：within-3 显示局部 coarse localization，但不能替代 exact yaw accuracy。
4. 修正 pitch_acc 解释：
   - pitch_acc 仅是二级诊断指标。
   - 不得把 C2 yaw weak-positive 的 3% 阈值直接用于 pitch。
   - 部分 pitch mean 约 3-4%，但不改变 C2 null result。
5. 修正 C3 论证框架：
   - 删除 Claude “推荐放行 C3”口吻。
   - 改为“若 Codex 另行放行，可采用的候选设计”。
   - 明确 C3、三轴小项目、路线二/三/四、论文正文均未放行。
6. 可选修正图表规划：
   - 将全 0 yaw_acc bar chart 降级为 supplement 或并入表格。
   - 主文优先考虑 yaw_cmae vs within-3 scatter / grouped summary。
7. 输出报告到：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/62_1C-E33-FIX01_判据基线与C3边界修正_Claude执行报告.md

红线：
- 不启动 C3。
- 不写论文正文。
- 不做后验 OCS-only 架构/特征搜索。
- 不启动 B1/GGX、三轴小项目、路线二/三/四。
- 不修改 feature_definitions.json / enhanced_ocs_features.npz / split manifests / result JSON。
```

---

## 7. 结论

E33 的主体方向正确，但目前有两个会直接影响论文表述的判据错误，以及一个 C3 阶段门口吻越界问题。先做 E33-FIX01，把这些地方收紧；通过后再决定是否把 C1/C2 证据包作为稳定成果归档，以及是否另立 C3 独立对照实验规划。
