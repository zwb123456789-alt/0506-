# 106 路线一 C 阶段性 Results 非正文证据包 Claude 执行报告

最后更新：2026-07-01  
任务：R120 Codex 任务单 `1C_stage_results_evidence_pack`  
上游阶段门：R119 通过 105（L1D3 置信一致性与 P-DB 正式评估）  
交付目录：`v0.4_results/14_route1c_stage_results_pack/`

---

## 1. 任务结论摘要

**完成。** R120 六个子任务 A/B/C/D/E/F 全部交付，最低接收标准与强接收标准的可核验项均满足。本轮为 Results 非正文证据整理，未新训练、未新渲染、未新后处理矩阵、未改旧脚本/旧结果、未写论文正文、未写成果区、未生成 Codex 审阅文件、未改 CLAUDE.md。

> 说明：`tables/` 与 `text/` 下的 claim 边界表、待补实验建议表等文件在本会话开始前已由上一轮同任务存在初版；本轮对全部交付物逐一核对口径、补齐 CSV/MD 配套、复制现有图并生成 manifest，确保内容与 R113/R115/R117/R119 一致。

## 2. 已读文件与遵守的红线

已读：
- `CLAUDE.md`（大根目录总控）、`项目重启_v0.4_BlenderOCS/CLAUDE.md`（v0.4 权威入口）
- `04_Codex审阅/R113 / R115 / R117 / R119`、本轮任务单 `R120`
- 成果区 `00 / 01 / 05 / 06 / 07`（当前主用成果）
- `13_l1d3_confidence_pdb/hardcases/l1d3_recommended_pinthard_design.md`
- 结果目录 10/11/12/13 结构与关键 CSV/JSON/PNG 清单

遵守红线：仅改动项目根目录内部文件；报告写入 `02_Claude输出/`，未写 `04_Codex审阅/`；未自行放行/扩展路线设计/技术裁决；所有 claim 限定 model-known simulated；负向观察（P-EXT 坍缩、joint 天花板、neural margin 弱、image_only 欠覆盖）全部保留不淡化。

## 3. 新增脚本清单

无。本轮为整理/汇总/复制/制表任务，仅用 shell 做路径核验与图复制（`cp`，加 `copy_` 前缀，不覆盖原图），未新增或修改任何 `.py` 脚本，未改旧脚本、旧 metrics、旧 samples 或旧结果目录。

## 4. 新生成结果目录清单

```text
v0.4_results/14_route1c_stage_results_pack/
  tables/  route1c_evidence_chain.csv, route1c_figure_plan.csv,
           route1c_claim_boundary_table.csv, route1c_next_experiment_options.csv
  text/    route1c_evidence_chain.md, route1c_figure_plan.md,
           route1c_results_narrative_skeleton.md,
           route1c_claim_boundary_table.md, route1c_next_experiment_options.md
  figures/ copy_R115_l1m2_gain_curve_best.png, copy_R115_l1m2_complementarity_hit30.png,
           copy_R119_pdb_gain_curve.png, copy_R119_complementarity_quadrants.png,
           copy_R119_neural_vs_pdb_error_scatter.png, copy_R119_risk_coverage_curves.png,
           copy_R119_confidence_decile_error.png
  audit/   route1c_stage_results_manifest.csv, route1c_stage_results_manifest.md
```

## 5. 证据链总表摘要（子任务 A）

四条主链覆盖 R113/R115/R117/R119，每链含 accepted_claim / boundary / key_numbers / 数据源 / paper_use / risk_level：
- 链1（R113）single-frame 负结果收口与 B6 判据轴闭口 — SI+limitation，low。
- 链2（R115）clean/P-INT 多几何 OCS 单调增益（cMAE 76.56→22.77°）— main+SI，low。
- 链3（R117）degraded 真实性与 M-roll fixed-roll 边界 — main+SI+limitation，low。
- 链4（R119）D3/P-DB/conformal 置信一致性与互补证据 — main+SI+limitation，medium（措辞易过度解读）。
- 三条独立口径（clean/退化/非神经检索）交叉验证 OCS-only 多几何单调增益方向一致。

## 6. 图表与 SI 清单摘要（子任务 B）

主图 5（Fig.1-5）+ SI 5（SI-1 至 SI-5）+ 可选补充 2。每候选绑定现有数据源并标 allowed/forbidden reading。现有图 7 张已复制入 `figures/`（保留原图与来源路径）；需新绘 6 项仅给绑定源与重绘说明，本轮不出正式图（本轮边界为整理非正式出图）。

## 7. Results 非正文叙事骨架摘要（子任务 C）

claim ledger 覆盖 6 段：problem framing → clean/P-INT 可观测性 → degraded/M-roll 真实性 → P-DB/conformal 置信一致性 → negative observations → remaining gaps。每条 claim 附 evidence path / allowed wording / forbidden wording / usable in。全文为 outline，无正式论文段落。

## 8. claim 边界表摘要（子任务 D）

可写 8 条（W1-W8，均带证据路径与数字、限定 model-known simulated）；不可写 14 条（F1-F14，含真实反演/望远镜验证/GEO 姿态真值/P-EXT 已解决/joint 强互补/Bayesian posterior/整体闭口/三轴启动/per-part 现实输入/image_only 覆盖良好/扩展已启动等）。与 CLAUDE.md 第 6 节红线逐条对齐。

## 9. 待补实验与下一阶段建议摘要（子任务 E）

四选项 A/B/C/D，每项含 goal/input/computation/cost/stage-gate/risk/enables/cannot-claim：
- A 先整理 Results/SI（低成本，不新训练）；
- B degraded-severe / P-INT-hard 小矩阵（C 类改动，须 Codex 另行走阶段门）；
- C joint/full-2664 M-roll 子集扩展（约 10-11h，仅边界）；
- D 阶段性闭口前 minimal sanity check（多 seed/一致性核验）。
未自行放行任何选项。

## 10. manifest 与可复查索引摘要（子任务 F）

`audit/route1c_stage_results_manifest.csv/md` 收录五类：Codex 审阅（R113-R120）、Claude 报告（102-106）、成果区（00/01/05/06/07）、结果目录（10-14）、关键 CSV/JSON/PNG/MD 与本包交付物。41 条现有路径脚本核验 **缺失 0**；106 报告为本轮写入项。

## 11. 未完成项与阻塞项

- 无阻塞。
- 需新绘的 6 项图（Fig.1 概念图、Fig.3、SI-1/2/3/4）本轮按任务边界只给数据源绑定与重绘说明，未出正式图，留待正式 Results 阶段（Option A）。
- 本报告 106 写入后，manifest 中 106 的 PENDING 状态即变为实际存在。

## 12. 红线自查

- [x] 未新训练/新渲染/新后处理大矩阵；
- [x] 未改旧脚本/旧 metrics/旧 samples/旧结果目录（图仅复制加前缀）；
- [x] 未写论文正文/投稿摘要/最终稿；
- [x] 未写成果区、未生成 Codex 审阅文件、未改 CLAUDE.md；
- [x] 未启动头A/头B大合并裁决；未把路线一 C 写成整体闭口；
- [x] 未启动 T3/L2、三轴小项目、路线二/三/四；
- [x] 未把 P-DB 写成真实反演成功率、未把 conformal 写成最终概率校准、未把 P-EXT 写成已解决；
- [x] 全部 claim 限定 model-known simulated，负向观察保留。

## 13. 交给 Codex 审阅的裁决问题清单

1. 证据链总表将链4（R119）风险等级标为 medium（P-DB/conformal 措辞易被过度解读），其余为 low，是否认可该分级？
2. 图表清单把 Fig.2/Fig.4/Fig.5 定为可直接复用现有图、Fig.1/Fig.3/SI-1/2/3/4 需新绘，本轮未出正式图。是否在下一轮（Option A）授权 Claude 正式出图，或由作者另行制图？
3. claim 边界表在 R120 明列项外补充了 F11-F14（头A/头B大合并、per-part 现实输入、image_only 覆盖、扩展未放行）。是否认可这些补充边界？
4. 待补实验建议 Option B（degraded-severe/P-INT-hard）与 Option C（joint M-roll）均为 C 类改动，是否需要 R121 或后续任务单单独下达阶段门，还是先执行 Option A？
5. 本证据包位于 `v0.4_results/14_route1c_stage_results_pack/`（结果目录），未写入成果区。若 Codex 审阅通过，是否将其升级/镜像进 `01_成果区/` 作为阶段性 Results 依据？
