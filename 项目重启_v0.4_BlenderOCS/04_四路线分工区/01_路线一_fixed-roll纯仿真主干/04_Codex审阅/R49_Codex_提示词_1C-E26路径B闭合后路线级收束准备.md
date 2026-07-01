# R49 Codex 提示词：1C-E26 路径 B 闭合后路线级收束准备

最后更新：2026-06-25  
提示词生成端：Codex  
执行端：Claude

---

## 给 Claude 的短提示词

执行 `1C-E26`：路径 B 闭合后的路线级收束准备。

依据文件：

- `CLAUDE.md`
- `04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R48_Codex_审阅_1C-E25-FIX01成果包补正通过.md`
- `04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/46_1C-E23_B0证据包与路线决策备忘录_Claude执行报告.md`
- `04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R45_Codex_审阅_1C-E23通过并建议进入多折yaw_block方案.md`
- `v0.4_results/03_training_baseline/e25_multifold_yawblock/e25_multifold_summary.json`
- `v0.4_results/03_training_baseline/e25_multifold_yawblock/e25_overlap_report.json`

任务：

1. 不训练、不改代码、不改数据结果。
2. 写一份路线级收束准备报告，输出到：
   `04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/50_1C-E26_路径B闭合后路线级收束准备_Claude执行报告.md`
3. 报告必须包括：
   - 路径 B 已闭合的证据清单；
   - 可引用结论与禁止结论；
   - `5-fold circular yaw_block cross-validation, yaw_acc mean=0.00%, std=0.00%` 的推荐引用口径；
   - 后续可选方向清单，至少区分 `D1 = B1 fullrun / 对比` 与 `C`，但只做准备，不放行执行；
   - 进入下一步前需要 Codex 裁决的问题清单。

红线：

- 不写论文正文。
- 不启动 B1/GGX。
- 不启动三轴小项目。
- 不启动路线二/三/四。
- 不把 B0 / image_only / fixed-roll 结果外推到真实未知目标姿态反演。
- 不把路径 B 负结果写成 B1、GGX、OCS-only、joint 或三轴结论。
- 若输出过长，按 `Part 1/2/3...` 分段写入，直到文件完整。

