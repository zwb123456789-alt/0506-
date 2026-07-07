# R131 Codex 任务单：P1 seed-roll scan smoke

最后更新：2026-07-01  
任务类型：给执行端 Claude 的长程 smoke 任务提示词  
上游阶段门：R130 已通过 001，三轴小项目准备阶段门设计接收  
当前状态：放行 P1 seed-roll scan smoke；不放行全量三轴渲染/训练

执行端报告必须写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/002_P1_seed_roll_scan_smoke_Claude执行报告.md
```

所有新结果写入：

```text
v0.4_results/19_three_axis_p1_seed_roll_scan/
```

本文件是 Codex 调度/提示词文件，保留在本路线 `04_Codex审阅/`。执行端不得把报告、结果或裁决文件写入 `04_Codex审阅/`。

---

## 0. 给 Claude 的总提示词

你现在执行三轴小项目第一阶段 smoke：

```text
three_axis_p1_seed_roll_scan_smoke
```

R130 已接收 18 号准备包并放行 P1 smoke。你的任务是围绕 18 号包预注册的 12 个代表 seed 与 8 个非零 roll 做最小受控渲染/后处理/汇总，验证三轴小项目的 roll 扫描链路是否可执行，并初步观察 brightness、local contrast 和 roll sensitivity 如何随 roll 变化。

本轮不是三轴小项目完整执行，不是 P2/P3/P4，不训练 roll-aware 模型，不启动 R128。

---

## 1. 当前允许与禁止

允许：

```text
1. 读取 18 号包的 P1 预注册矩阵与 seed 表。
2. 新增派生脚本、wrapper、汇总脚本、制图脚本。
3. 使用 Blender 对 phase63 / L1-G1 的 96 个 seed-roll 姿态做 smoke 渲染。
4. 做必要后处理，提取 OCS total、image usability、local contrast、glint/saturation flag、roll sensitivity。
5. 复用 roll=0 既有结果作为 baseline，不重渲 roll=0。
6. 输出 CSV/JSON/PNG/PDF/MD/log/audit。
```

禁止：

```text
1. 不启动 P2/P3/P4。
2. 不做全量三轴渲染。
3. 不训练任何模型，不做 roll-aware 训练。
4. 不改旧脚本、旧 metrics、旧 samples、旧结果目录 10-18。
5. 不改姿态网格、OBS_GEOMETRIES、split、backbone 或超参。
6. 不启动 R128、新路线二、GEO 真实数据处理、路线二/三/四或 T3/L2。
7. 不写成果区，不生成 Codex 审阅文件，不改 CLAUDE.md。
8. 不把 smoke 结果写成三轴小项目已完成。
```

若发现 `render_mroll_probe.py` 或后处理入口不足以安全复用，只能新增派生 wrapper 或在 19 号包内写明阻塞；不得修改旧脚本。

---

## 2. 必读文件

按顺序读取并在报告列出：

```text
CLAUDE.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R129_Codex_任务单_三轴小项目准备阶段门设计.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R130_Codex_审阅_001通过_三轴小项目准备阶段门接收并放行P1_seed_roll_smoke.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/00_三轴小项目准备阶段门设计_R130通过.md
v0.4_results/18_three_axis_planning_preflight/text/next_task_draft_P1_seed_roll_scan.md
v0.4_results/18_three_axis_planning_preflight/tables/p1_seed_roll_pre_registered_matrix.csv
v0.4_results/18_three_axis_planning_preflight/seeds/three_axis_seed_candidates.csv
```

按需读取：

```text
v0.4_results/18_three_axis_planning_preflight/
v0.4_results/17_route1c_postclosure_enhancement_sweep/
v0.4_results/12_l1m3_degraded_mroll/
v0.4_results/01_fullrun/
06_v0.4_code/02_blender/render_mroll_probe.py
06_v0.4_code/05_postprocess/run_mroll_probe_postprocess.py
06_v0.4_code/07_training/postclosure_mroll_full2664_eval.py
```

---

## 3. 总体交付结构

建议结构：

```text
v0.4_results/19_three_axis_p1_seed_roll_scan/
  audit/
  render/
  postprocess/
  metrics/
  figures/
  tables/
  text/
  scripts/
  logs/
```

执行报告写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/002_P1_seed_roll_scan_smoke_Claude执行报告.md
```

---

## 4. 子任务 A：P1 输入审计与执行矩阵锁定

必须输出：

```text
audit/p1_input_manifest.csv
audit/p1_locked_run_matrix.csv
audit/code_entrypoint_audit.csv
audit/redline_precheck.csv
```

要求：

```text
1. 从 18 号包读取 96 行 P1 预注册矩阵。
2. 确认 12 个 seed、8 个非零 roll、phase63 几何。
3. 确认 roll=0 baseline 来源，不重渲。
4. 确认 render/postprocess/eval 入口。
5. 若发现矩阵重复、seed 缺失或 roll 缺失，停止并报告阻塞。
```

---

## 5. 子任务 B：96 单位 seed-roll smoke 渲染与后处理

对象：

```text
12 个代表 seed
roll ∈ {-60,-45,-30,-15,+15,+30,+45,+60}
geom = phase63 / L1-G1
总计 96 个新渲染单位
```

必须输出：

```text
render/p1_render_manifest.csv
postprocess/p1_postprocess_manifest.csv
tables/p1_seed_roll_ocs_table.csv
logs/p1_render_postprocess.log
```

要求：

```text
1. 每个 seed-roll 必须有 record_id/yaw/pitch/roll/category/source_seed。
2. 渲染参数继承路线一 C / M-roll smoke 可用配置。
3. 后处理至少提取 OCS total、图像路径、基本图像可用性。
4. 若 Blender/GPU/路径问题导致部分失败，报告必须列出失败姿态与原因；不得静默跳过。
```

---

## 6. 子任务 C：roll 曲线与三轴 smoke 指标

必须输出：

```text
tables/p1_roll_curve_metrics.csv
tables/p1_roll_sensitivity_summary.csv
tables/p1_brightness_information_smoke.csv
metrics/p1_metric_definitions_used.md
```

至少计算：

```text
ocs_total by roll；
delta_ocs_vs_roll0；
relative_brightness_rank_shift；
local_contrast along roll；
glint / saturation risk flag；
roll_sensitivity_score；
image_usable flag；
```

判断口径：

```text
1. bright seed 是否仍保持高亮，或最亮点随 roll 迁移。
2. high-info / low-info seed 的 roll 曲线是否与 brightness 解耦。
3. roll-sensitive seed 是否在 smoke 中表现出更大变化。
4. dark seed 是否持续低信号或出现 roll-induced brightening。
5. robust-easy seed 是否稳定。
```

---

## 7. 子任务 D：图表与可解释摘要

必须输出：

```text
figures/p1_seed_roll_brightness_curves.png/.pdf
figures/p1_category_roll_sensitivity_panel.png/.pdf
figures/p1_roll_heatmap_seed_by_roll.png/.pdf
text/p1_seed_roll_smoke_summary.md
```

摘要必须回答：

```text
1. P1 smoke 链路是否跑通。
2. 最亮点是否随 roll 迁移。
3. 是否出现“亮但不高信息”或“暗但变化敏感”的例子。
4. 哪些 seed 类别值得进入 P1 正式或 P2。
5. 是否需要调整后续三轴采样计划。
```

---

## 8. 子任务 E：验收矩阵与下一步建议

必须输出：

```text
tables/p1_smoke_gate_matrix.csv
tables/p1_next_step_recommendations.csv
audit/generated_files_manifest.csv
audit/numeric_path_consistency_check.csv
audit/redline_self_check.csv
text/codex_review_checklist_for_002.md
```

验收矩阵至少包含：

```text
96 渲染单位是否完成；
后处理是否完成；
OCS total 是否可用；
roll=0 baseline 是否对齐；
图像路径是否有效；
roll 曲线是否可计算；
是否满足 P1 正式扩展条件；
是否需要返工。
```

---

## 9. 执行报告结构

报告必须包含：

```text
1. 任务结论摘要：完成 / 部分完成 / 阻塞。
2. 已读文件与红线遵守。
3. 新增脚本、渲染、后处理与结果目录清单。
4. P1 输入审计与矩阵锁定。
5. 96 单位渲染与后处理完成情况。
6. roll 曲线与三轴 smoke 指标。
7. 图表与可解释摘要。
8. 验收矩阵、manifest、数字/路径一致性、红线自检。
9. 交给 Codex 的裁决问题。
```

---

## 10. 成功判据

最低接收标准：

```text
1. 19 号包目录存在，结构清楚。
2. P1 locked run matrix 96 行。
3. 至少完成 12 seed × 4 roll 的保底 smoke，或明确阻塞原因。
4. roll=0 baseline 来源清楚。
5. OCS total / image path / image usable 至少一套可审计。
6. manifest、路径一致性、红线自检完成。
7. 报告写入正确路径，未写成果区、未改 CLAUDE.md、未启动 P2/P3/P4/R128。
```

强接收标准：

```text
1. 96/96 渲染单位完成。
2. 96/96 后处理完成。
3. roll 曲线、roll sensitivity、brightness rank shift、glint/saturation flag 完成。
4. 三张图 + summary 完成。
5. gate matrix 可让 Codex 直接裁决是否放行 P1 正式扩展或进入 P2 sparse grid。
```

---

## 11. 最后提醒

本轮只做 P1 seed-roll scan smoke。完成后只提交 19 号包和 002 执行报告。不要自行把结果升级到成果区，不要生成 Codex 审阅文件，不要修改 `CLAUDE.md`，不要启动全量三轴渲染/训练，不要启动 R128。

Codex 后续将裁决：

```text
1. 002 P1 smoke 是否通过；
2. 是否放行 P1 正式扩展或 P2 sparse 3-axis grid；
3. 是否需要修正 seed 类别或采样计划；
4. 是否出现最亮构型迁移、高信息构型迁移或低信息区域扩展的早期证据；
5. R128 是否继续挂起。
```
