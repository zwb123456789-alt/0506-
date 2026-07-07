# 路线一 C 实验主干闭口候选总结（供 Codex R125 裁决）

状态：闭口候选包，等待 Codex R125 裁决；Claude 不自行宣布闭口，不启动三轴小项目。

## 1. 逐模块状态（对照 R113 M1-M5/M-roll）

| 模块 | 状态 | 分类 |
|---|---|---|
| M1/F1 单几何下界 | DONE | 非BLOCKER(已完成) |
| M2/L1 多几何主线 | DONE | 非BLOCKER(已完成) |
| M3 clean/degraded 真实性 | DONE(mild/moderate) | 非BLOCKER(mild/moderate完成), severe=ENHANCEMENT |
| M4-D1 per-part 归因 | DONE(diagnostic) | 非BLOCKER(诊断性) |
| M4-D2 互补性 | DONE(closed this round) | 闭口完成；joint 强互补=ENHANCEMENT(需P-INT-hard) |
| M4-D3 置信一致性 | DONE | 非BLOCKER(已完成) |
| M4-D4 可观测性地图 | DONE(closed this round) | 闭口完成 |
| M5 三协议对比门 | DONE(closed this round) | 闭口完成 |
| M-roll 边界探针 | DONE(probe) | 非BLOCKER(探针完成), full-2664=ENHANCEMENT |
| L2/T3 光变时序 | NOT_STARTED(by design) | FUTURE_ROUTE |
| 三轴小项目 | NOT_STARTED | FUTURE_ROUTE(候选下一阶段) |
| multi-seed/fold 稳健性 | NOT_DONE | 裁决点：接受交叉验证 or ENHANCEMENT(minimal multi-seed sanity) |

## 2. 本轮新闭口的三个门

- **D2 三通道互补性**：完成 top-k overlap / disagreement / oracle 增量。结论诚实：clean 下 image 饱和、joint 相对最佳单通道无稳定正增量（max +0.0068），joint 与 image 在 G1/G3 完全一致——joint 强互补性未闭口，是天花板效应而非确证短板，需 P-INT-hard 才能判定。
- **D4 可观测性地图**：完成误差地图、低/中/高区分类、几何增益地图（G1→G5 平均救回 53.8°、228/296 姿态改善）、易混淆区（ambiguous-flux 236、过自信错误 98）、P-EXT 坍缩区、hardcase 交叉统计。可作三轴小项目接口。
- **M5 三协议对比门**：P-INT 单调增益 / P-EXT 坍缩 / P-DB 可检索，边界矩阵与 claim 表完成。

## 3. 实验主干闭口判断（候选）

- 按 R113 闭口时序，M1/M2/M3(mild-moderate)/M4(D1-D4)/M5/M-roll(探针) 均已有通过审阅或本轮闭口的证据。
- **本轮未发现新的 BLOCKER**：D2/D4/M5 都是可用现有中间量完成的汇总门，已完成。
- 唯一需作者/Codex 裁决的实质点是 **multi-seed 稳健性**：是否接受当前多证据链交叉验证作为主干闭口条件，还是要求 minimal multi-seed sanity（属 C 类新训练）。
- joint 强互补性、degraded-severe、M-roll full-2664 均为 ENHANCEMENT，不阻塞实验主干闭口。
