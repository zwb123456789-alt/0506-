# R50 Codex 审阅：1C-E26 通过并放行 E27 实验设计规划

最后更新：2026-06-25  
审阅端：Codex  
被审阅报告：`02_Claude输出/50_1C-E26_路径B闭合后路线级收束准备_Claude执行报告.md`

---

## 0. 裁决

```text
1C-E26：PASS
路径 B 收束准备：PASS
B0 baseline 证据包状态：闭合
论文正文改写：NOT RELEASED
B1 / GGX / 三轴 / 路线二三四：NOT RELEASED
下一步：1C-E27，论文实验设计规划与后续路线优先级裁决准备
```

E26 完成了 R49 要求：把 E24 -> E25 -> E25-FIX01 的执行链、证据边界、可引用结论、禁止结论和后续待裁决问题整理为路线级收束材料。报告没有启动新训练、没有改代码、没有改数据结果，也没有写论文正文，范围控制合格。

---

## 1. 审阅通过项

### 1.1 路径 B 证据链闭合

E26 对路径 B 的闭合证据梳理准确：

- R46：E24 多折 circular yaw_block 方案通过；
- R47：E25 多折训练结果条件通过；
- R48：E25-FIX01 成果包补正通过；
- 总结论保持为 `5-fold circular yaw_block cross-validation, yaw_acc mean=0.00%, std=0.00%`。

该结论只覆盖：

```text
B0 / fixed-roll / image_only / single-view / phase63 / current CNN baseline
```

不得外推到 B1、GGX、OCS-only、joint、三轴、真实未知目标或真实望远镜场景。

### 1.2 可引用与禁止结论边界合格

E26 将可引用结论与禁止结论分开，符合 R49 要求。尤其是以下边界必须保留：

- random split 只能作为 in-distribution sanity / baseline；
- strict yaw_block 与 5-fold circular yaw_block 才能作为跨 yaw 泛化负结果证据；
- E21 旧 yaw_block 泄漏结果不得再作为泛化证据；
- 路径 B 的负结果不代表所有模型或所有物理模型失败。

### 1.3 后续方向拆分合格

E26 对 D1、C、D2 的拆分基本正确：

- `D1 = B1 fullrun / 对比`，服务 B0 vs B1 的控制变量比较；
- `C = OCS 特征增强探索`，使用现有 B0 数据做低成本特征方案探索；
- `D2 = GGX / BRDF mismatch 对照`，优先级低于 D1，且不能与 B1 混写。

这些方向均保持 `NOT RELEASED`，符合当前阶段门。

---

## 2. Q1-Q4 裁决

### Q1：B0 baseline 是否足够支撑论文消融章？

裁决：

```text
YES, for experiment-design planning.
NOT YET, for final manuscript writing.
```

B0 证据链已经足够进入论文实验设计规划：可以规划哪些图表、表格、消融结果和 source-data 索引进入实验章。但还不放行正文写作，因为 B1/C/D1 的去留和章节位置尚未完成总设计。

### Q2：下一步优先 D1 还是 C？

裁决：

```text
先做 E27 实验设计规划；
E27 后优先评估 C 的低成本方案，再决定是否启动 D1。
```

理由：

- C 只依赖现有 B0 数据，计算成本低，能快速判断 OCS 派生特征是否存在挽回空间；
- D1 是正式主线对比所需方向，但需要先完成 B1 材料参数、渲染方案、checker 和 fullrun 方案审阅，成本更高；
- 直接启动 D1 前，需要知道论文实验章究竟缺什么证据，避免盲目渲染。

注意：这不是放行 C 的执行，只是确定 E27 后的优先级倾向。

### Q3：5-fold 是否扩展到 joint 或 OCS-only？

裁决：

```text
NOT RELEASED.
```

当前不补跑 joint / OCS-only 的 5-fold。理由：

- image_only 5-fold 已足够证明当前单视图图像通道的跨未见 yaw 泛化失败；
- FIX01 单折已给出 OCS-only / joint 的负面边界；
- 再跑 10 个 fold 的边际信息有限，会推迟路线收束；
- 若 E27 判定论文消融章必须补齐全模式 5-fold，再另行设计 E28 方案，不直接执行。

### Q4：是否放行论文实验设计规划？

裁决：

```text
YES.
```

仅放行实验设计规划，不放行论文正文写作。E27 应输出“实验章结构与证据映射”，用于回答：

- B0 现有结果在实验章中放哪里；
- 哪些结论进入主文，哪些放消融或附录；
- D1 / C / D2 分别补什么证据缺口；
- 下一步应先设计 C 还是 D1；
- 哪些图表、表格、JSON、checkpoint 和 source-data 需要固定索引。

---

## 3. E27 放行范围

允许：

```text
1. 规划论文实验章结构；
2. 建立 B0 证据与实验章节/图表/表格的映射；
3. 标出 D1、C、D2 的证据缺口；
4. 给出下一步路线优先级建议；
5. 输出路线规划报告到 Claude 输出区。
```

禁止：

```text
1. 写论文正文段落；
2. 新训练；
3. 改代码；
4. 改数据结果；
5. 启动 B1/GGX 渲染；
6. 启动 OCS 特征增强实验；
7. 启动三轴小项目；
8. 启动路线二/三/四；
9. 修改冻结文件、成果区或 CLAUDE.md。
```

---

## 4. 给 Claude 的下一步短提示词

```text
执行 1C-E27：论文实验设计规划与后续路线优先级裁决准备。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R50_Codex_审阅_1C-E26通过并放行E27实验设计规划.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/50_1C-E26_路径B闭合后路线级收束准备_Claude执行报告.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/46_1C-E23_B0证据包与路线决策备忘录_Claude执行报告.md
- v0.4_results/03_training_baseline/e25_multifold_yawblock/e25_multifold_summary.json
- v0.4_results/03_training_baseline/e25_multifold_yawblock/e25_overlap_report.json

任务：
1. 不训练、不改代码、不改数据、不写论文正文。
2. 规划论文实验章结构，只写“设计规划”，不写可直接投稿的正文。
3. 建立 B0 证据与实验章图表/表格/source-data 的映射。
4. 标出 D1(B1 fullrun)、C(OCS 特征增强)、D2(GGX/mismatch) 分别补什么证据缺口。
5. 给出下一步优先级建议，但不得自行放行任何方向执行。
6. 输出到：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/51_1C-E27_论文实验设计规划与后续路线优先级_Claude执行报告.md

红线：
- 不写论文正文。
- 不启动 B1/GGX。
- 不启动 OCS 特征增强实验。
- 不启动三轴小项目。
- 不启动路线二/三/四。
- 不把 B0/image_only/fixed-roll 结果外推到真实未知目标姿态反演。
- 若输出过长，按 Part 1/2/3... 分段写入，直到文件完整。
```

