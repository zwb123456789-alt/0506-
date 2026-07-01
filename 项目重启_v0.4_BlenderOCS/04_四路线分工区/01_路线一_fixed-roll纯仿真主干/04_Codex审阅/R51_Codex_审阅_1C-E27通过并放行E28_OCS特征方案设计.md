# R51 Codex 审阅：1C-E27 通过并放行 E28 OCS 特征方案设计

最后更新：2026-06-25  
审阅端：Codex  
被审阅报告：`02_Claude输出/51_1C-E27_论文实验设计规划与后续路线优先级_Claude执行报告.md`

---

## 0. 裁决

```text
1C-E27：PASS
论文实验设计规划：PASS
B0 evidence packet：Phase 0 baseline 证据闭合
论文正文写作：NOT RELEASED
C / D1 / D2 执行：NOT RELEASED
下一步：1C-E28，OCS 特征增强方案设计
```

E27 完成了 R50 要求：只做实验章结构规划、B0 证据到图表/表格/source-data 的映射、D1/C/D2 证据缺口分析和后续优先级建议。报告没有训练、没有改代码、没有改数据、没有写论文正文，也没有自行放行任何后续方向。

---

## 1. 审阅通过项

### 1.1 实验章结构

E27 提出的 6 节实验章结构总体合理：

```text
E.1 实验设置与数据生成
E.2 单视图图像通道基线
E.3 OCS 光度通道信息贡献
E.4 消融与边界分析
E.5 B0 vs B1 对比
E.6 OCS 特征增强
```

需要保留两个标注：

- `E.1-E.4` 可由当前 B0 证据链支撑；
- `E.5/E.6` 只能作为条件章节或待补证据章节，不得在正文写作前写成已完成结果。

### 1.2 B0 证据映射

E27 的 T1-T6 与 F1-F3 图表规划基本合格。尤其是：

- `T1` 对应数据生成与 checker；
- `T2/T3` 对应 random 与 strict yaw_block；
- `F1-F3` 对应 5-fold yaw_block split、yaw 负结果与 pitch 迁移；
- source-data 路径基本完整；
- `T6` 黑名单只用于内部防误引，不进入论文正文。

### 1.3 后续方向优先级

Codex 接受 E27 的方向排序：

```text
P2 = C：OCS 特征增强方案
P3 = D1：B1 fullrun / B0 vs B1 对比
P4 = D2：GGX / mismatch 远期对照
```

但当前只放行 `C` 的“方案设计”，不放行特征提取脚本、训练筛选或 joint 复验。

---

## 2. Q_E27_1 至 Q_E27_6 裁决

### Q_E27_1：实验章结构是否合理？

裁决：

```text
YES, with labels.
```

结构合理，但必须在后续规划中标清：

- `E.1-E.4`：B0 已有证据支撑；
- `E.5`：依赖 D1；
- `E.6`：依赖 C；
- 这些仍是实验设计，不是论文正文。

### Q_E27_2：B0 证据映射是否完整？

裁决：

```text
YES, sufficient for planning.
```

当前映射足够支撑实验章规划。后续进入正文写作前，需要再做一次 source-data 索引清洁版，但本轮不启动。

### Q_E27_3：是否同意 P2=C -> P3=D1？

裁决：

```text
YES, for planning priority.
```

理由：

- C 使用现有 B0 OCS manifest，低成本；
- C 无论成功或失败，都会增强 `E.3/E.6` 的边界证据；
- D1 仍重要，但需材料参数与渲染方案先行审阅；
- C 与 D1 不互斥，C 可作为 D1 前的低成本信息增益。

### Q_E27_4：D2 是否现阶段搁置？

裁决：

```text
YES.
```

D2 暂时搁置。GGX 不进入当前主干闭合，不在 D1 前单独论证，除非后续 D1 完成后仍需要 BRDF mismatch 扩展。

### Q_E27_5：是否放行 C 的特征方案设计？

裁决：

```text
YES, design only.
```

放行 `1C-E28`：只设计 OCS 派生特征与筛选协议，不写代码、不抽特征、不训练、不复验。

E28 必须回答：

- 哪些 OCS 派生特征有物理含义；
- 哪些特征可能有 yaw-invariant 候选价值；
- 如何避免用标签泄漏或后验调参；
- 先跑 OCS-only 还是直接 joint；
- 成功/失败判据如何定义；
- 输出路径和产物清单是什么。

### Q_E27_6：Phase 0 是否可关闭？

裁决：

```text
YES, Phase 0 B0 baseline evidence is closed.
```

Phase 0 的 B0 baseline 证据链可以关闭。当前进入的是“后续路线准备”阶段，不等于放行 Phase 1 B1 fullrun，也不等于放行论文正文。

---

## 3. 下一步放行范围：1C-E28

允许：

```text
1. 设计 OCS 派生特征候选集；
2. 设计特征筛选协议；
3. 设计 OCS-only 与 joint 复验的阶段门；
4. 设计成功/失败判据；
5. 设计输出产物路径；
6. 形成可交给 Codex 审阅的方案报告。
```

禁止：

```text
1. 写代码；
2. 抽取特征；
3. 训练模型；
4. 修改数据或 manifest；
5. 运行 joint/OCS-only 复验；
6. 写论文正文；
7. 启动 B1/GGX；
8. 启动三轴小项目；
9. 启动路线二/三/四；
10. 修改 CLAUDE.md、冻结文件或成果区。
```

---

## 4. 给 Claude 的下一步短提示词

```text
执行 1C-E28：OCS 特征增强方案设计。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R51_Codex_审阅_1C-E27通过并放行E28_OCS特征方案设计.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/51_1C-E27_论文实验设计规划与后续路线优先级_Claude执行报告.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/46_1C-E23_B0证据包与路线决策备忘录_Claude执行报告.md
- v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_fullrun.json

任务：
1. 只做方案设计，不写代码、不抽特征、不训练、不改数据。
2. 设计 OCS 派生特征候选集，至少考虑：
   - per-part / total 比率；
   - 部件间比值；
   - 归一化 OCS；
   - contrast / balance 类指标；
   - total brightness 与形状比例分离；
   - 可能的 log/ratio 稳定化处理。
3. 为每类特征写明物理含义、可能贡献、泄漏风险和不适用条件。
4. 设计 C 的分阶段协议：
   - C0：只读 manifest 字段盘点；
   - C1：特征提取脚本方案；
   - C2：OCS-only strict yaw_block 筛选；
   - C3：若 C2 有非零 yaw_acc，再做 joint 复验。
5. 明确成功/失败判据：
   - 什么结果算值得继续；
   - 什么结果算负结果闭合；
   - 什么结果需要 Codex 返工。
6. 明确输出路径和产物清单。
7. 输出报告到：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/52_1C-E28_OCS特征增强方案设计_Claude执行报告.md

红线：
- 不写论文正文。
- 不写代码。
- 不运行特征提取或训练。
- 不启动 B1/GGX。
- 不启动三轴小项目。
- 不启动路线二/三/四。
- 不把方案设计写成已经验证的结论。
- 若输出过长，按 Part 1/2/3... 分段写入，直到文件完整。
```

