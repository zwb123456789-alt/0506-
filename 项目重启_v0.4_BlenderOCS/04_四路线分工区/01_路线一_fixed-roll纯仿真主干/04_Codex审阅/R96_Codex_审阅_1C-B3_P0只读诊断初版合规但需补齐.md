# R96 Codex 审阅：1C-B3 P0只读诊断初版合规但需补齐

最后更新：2026-06-29
审阅端：Codex
对象：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
94_1C-B3_P0只读诊断与V0.3-V0.4协议对齐_Claude执行报告.md
```

依据：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
R95_Codex_任务单_1C-B3_P0只读诊断与V0.3-V0.4协议对齐.md
```

## 0. 裁决

```text
94 合规接收为 B-3/P0 只读诊断初版。
但 P0 尚未闭口，不得写入成果区，不得触发头A/头B大合并裁决。

当前阶段应更新为：
头B-B3/P0 只读诊断初版已交付；P0-1 已形成口径对齐判断；
P0-2/P0-3/P0-4 已完成输入盘点、方法设计和部分判断，但距离矩阵、heatmap、混淆聚合、pseudo-light-curve 图仍待只读脚本补齐。
```

## 1. 合规检查

94 对 R95 的主要红线遵守情况：

| 项目 | 检查结果 | 说明 |
|---|---|---|
| 输出位置 | 通过 | 文件位于路线一 `02_Claude输出/`，没有写入 `04_Codex审阅/` 或 `01_成果区/` |
| 不训练 | 通过 | 报告声明未训练模型，且未给出新训练结果 |
| 不新渲染 | 通过 | 未生成新渲染数据 |
| 不生成新数据 | 通过 | 未生成新实验数据；只盘点现有 `npz/json/csv/md` |
| 不改 split/模型/loss/超参/seed | 通过 | 未修改训练协议或模型 |
| 不覆盖 R04 负结果链 | 通过 | 未改写 R04 代码、数据或成果链 |
| 不改论文正文 | 通过 | 未进入正文正式改写 |
| 不改 CLAUDE.md | 通过 | 报告自查声明未改 CLAUDE.md |
| 不触发大合并裁决 | 通过 | 明确当前不是合并裁决 |
| pseudo-light-curve 命名 | 通过 | 使用 probe 口径，没有写成正式 light-curve experiment |
| claim 边界 | 基本通过 | 未写 yaw 物理不可观测；未写 image 与 OCS 普遍不互补；未写 single-frame failed, so replaced by sequence |

结论：此前给 Claude 设定的生成文件与阶段边界限制仍在遵守。

## 2. 内容检查

94 已完成的有效内容：

```text
1. 明确 93 已作为头B-B2 方法总结接收，当前进入头B-B3/P0。
2. 建立了 V0.3/V0.4 的协议差异框架。
3. 指出 split 从 random/弱 holdout 到 circular yaw-block 是最关键差异。
4. 指出 exact-bin 5 deg 判据可能放大 yaw-block 失败。
5. 盘点了现有 enhanced_ocs_features.npz、per-sample prediction、confusion matrix、split manifest 等可用输入。
6. 识别出 image embedding 与 joint embedding 未保存，若要分析需后续只读导出脚本。
7. 给出了 P1-A、P1-B、P2 的初步阶段门建议。
```

94 的不足与边界：

```text
1. P0-1 可视为已形成初步协议对齐判断，但 V0.3 原始 metrics/split 文件尚未直接读取。
2. P0-2 尚未真正生成 yaw-yaw distance matrix、nearest yaw pairs 或 heatmap。
3. P0-3 尚未真正生成聚合 confusion cluster 表和 distance-confusion overlap 表。
4. P0-4 尚未真正生成 pseudo-light-curve 图或序列相似性表。
5. 因此 94 不能作为 P0 完成报告，只能作为 P0 初版/输入盘点/补齐任务依据。
```

## 2.1 审阅分类与篇幅控制

本轮属于 D 类只读诊断审阅，不是 A 类成果区归档审阅，也不是 C 类训练/模型/split 阶段门审阅。

因此本 R96 只裁决：

```text
94 是否合规；
94 是否可作为 P0 初版接收；
P0 还缺什么；
下一步是否只允许 D 类只读补齐。
```

后续对同类 D 类报告不得做无用全文复核，不得大段复述 Claude 报告。除非申请成果区归档、P1/P2 阶段门或论文 claim 使用，否则只做短审阅、缺口清单和下一步提示词。

## 3. 阶段判断

当前不能放行：

```text
P1-A 连续/圆周角度判据改进
P1-B 非朴素 fusion
P2 formal light-curve sequence
头A/头B大合并裁决
成果区归档
论文正文正式改写
```

当前可放行的只有下一轮 D 类只读补齐：

```text
1. 读取 V0.3 原始 metrics/split 文件，补齐 V0.3/V0.4 协议对齐证据。
2. 编写并运行只读 numpy/matplotlib 脚本，生成 OCS yaw-yaw distance matrix、heatmap、nearest yaw pairs。
3. 聚合现有 confusion matrices/per-sample predictions，生成 confusion cluster 表和代表失败案例。
4. 基于 enhanced_ocs_features.npz 与 record_ids 生成 pseudo-light-curve probe 图和序列相似性表。
```

这些补齐动作仍不得训练、不得推理生成新预测、不得改模型、不得改 split、不得新渲染、不得写入成果区。

## 4. 下一步

建议下一步由 Codex 另写短任务单，放行 Claude 执行：

```text
1C-B3-FIX01_P0只读诊断矩阵图表补齐
```

目标不是新实验，而是补齐 94 中“待生成”的只读派生产物。

建议输出：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
95_1C-B3-FIX01_P0只读诊断矩阵图表补齐_Claude执行报告.md
```

## 5. CLAUDE.md 同步建议

应同步更新 `项目重启_v0.4_BlenderOCS/CLAUDE.md`：

```text
当前状态：
头A已由R90收口；头B-B1由R91完成；头B-B2的93已接收；R95已给出B3/P0任务单；Claude 94已提交P0只读诊断初版；R96判定94合规但P0未闭口。

当前下一步：
不做大合并裁决，不进P1/P2，不进成果区；先补齐P0-2/P0-3/P0-4只读矩阵、图和表，并直接读取V0.3原始metrics/split文件完成协议对齐证据。
```
