# R129 Codex 任务单：三轴小项目准备阶段门设计

最后更新：2026-07-01  
任务类型：给执行端 Claude 的长程准备任务提示词  
上游阶段门：R127 已通过 109，路线一 C 主干与闭口后增强项清账完成  
当前状态：正式进入三轴小项目准备阶段，但**不直接启动全量三轴渲染/训练**

执行端报告必须写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/001_三轴小项目准备阶段门设计_Claude执行报告.md
```

所有新候选材料写入：

```text
v0.4_results/18_three_axis_planning_preflight/
```

本文件是 Codex 调度/提示词文件，保留在本路线 `04_Codex审阅/`。执行端不得把报告、结果或裁决文件写入 `04_Codex审阅/`。

---

## 0. 给 Claude 的总提示词

你现在执行三轴小项目的准备阶段门设计任务：

```text
three_axis_planning_preflight
```

路线一 C 已由 R125/R127 闭口；R128 只是三轴小项目完成后再回看的候选路线结构调整记忆，当前不执行。你的任务不是启动 R128，也不是改路线结构，而是为“三轴小项目：最亮构型与光路解释”生成可审阅的准备包。

本轮目标：

```text
1. 读取路线一 C 已通过成果与三轴小项目指导文件。
2. 从路线一 D4 地图、hardcase、M-roll full-2664、OCS/image/P-DB/conformal 结果中提取可作为三轴搜索种子的信息。
3. 定义三轴小项目的指标、采样策略、资源估计和阶段门矩阵。
4. 设计第一阶段可执行任务，不直接做全量三轴渲染或训练。
5. 输出 18 号准备包和 001 执行报告，交 Codex 审阅。
```

---

## 1. 当前允许与禁止

允许：

```text
1. 只读路线一 C 已通过结果包 11-17。
2. 新增只读审计、规划、统计、抽样和制图脚本。
3. 从既有 yaw/pitch/fixed-roll、M-roll full-2664、hardcase index、D4 地图中筛选三轴搜索种子。
4. 生成 CSV/JSON/MD/PNG/PDF 规划材料。
5. 做极轻量 smoke 级可行性检查，例如读取姿态网格、估算渲染数量、检查 Blender 脚本可参数化程度。
```

禁止：

```text
1. 不启动全量三轴渲染。
2. 不启动三轴训练。
3. 不改旧脚本、旧 metrics、旧 samples、旧结果目录 10-17。
4. 不改姿态网格、OBS_GEOMETRIES 语义、split 定义、backbone 或超参。
5. 不启动 R128 新路线二、真实图像难度审计、GEO 真实数据处理、路线二/三/四扩展或 T3/L2。
6. 不写成果区，不生成 Codex 审阅文件，不改 CLAUDE.md。
7. 不把三轴小项目写成真实未知目标三轴姿态反演系统。
8. 不把最亮姿态写成最优反演姿态；必须区分 brightness 与 information。
```

若输出过长或文件写入受限，必须按 `Part 1/2/3...` 分段写入，直到报告和交付清单完整。

---

## 2. 必读文件

按顺序读取，并在执行报告中列出：

```text
CLAUDE.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/00_路线冻结文件区/01_三轴小项目_最亮构型与观测规划指导文件.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R125_Codex_审阅_108通过_路线一C实验主干闭口并放行三轴小项目准备.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R127_Codex_审阅_109通过_闭口后增强实验清账完成并放行三轴小项目准备.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/10_路线一C实验主干闭口_D2D4M5_R125通过.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/11_路线一C闭口后增强实验清账_R127通过.md
```

按需读取：

```text
v0.4_results/16_route1c_closure_d2d4_m5/
v0.4_results/17_route1c_postclosure_enhancement_sweep/
v0.4_results/13_l1d3_confidence_pdb/
v0.4_results/12_l1m3_degraded_mroll/
v0.4_results/11_l1m2_multigeometry_ocs/
06_v0.4_code/01_geometry/
06_v0.4_code/02_blender/
06_v0.4_code/05_postprocess/
06_v0.4_code/07_training/
```

注意：R128 仅作为“后续回看记忆”，本轮不读取也可；若读取，只能在报告中写“本轮不执行 R128”。

---

## 3. 总体交付结构

建议结构：

```text
v0.4_results/18_three_axis_planning_preflight/
  audit/
  seeds/
  metrics/
  sampling/
  resources/
  figures/
  tables/
  text/
  scripts/
  logs/
```

执行报告写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/001_三轴小项目准备阶段门设计_Claude执行报告.md
```

---

## 4. 子任务 A：输入审计与可复用资产索引

目标：确认三轴小项目可从哪些路线一 C 结果继承信息。

必须输出：

```text
audit/input_manifest.csv
audit/route1c_reusable_assets.md
audit/code_entrypoint_audit.csv
audit/redline_precheck.csv
```

至少检查：

```text
1. D4 可观测性地图、救回区、ambiguous-flux、overconfident-error、P-EXT 坍缩区。
2. hardcase index 中 ocs-hard / image-hard / disagreement-hard / robust-easy。
3. M-roll full-2664 中 ±15° 稳健与 ±30° 敏感区域。
4. P-DB / conformal / posterior-like / top-k / entropy / margin 等中间量是否可复用为三轴指标。
5. Blender 渲染脚本是否支持 roll 参数、是否可扩展到三轴采样。
6. 后处理和训练入口需要哪些字段才能支持 yaw/pitch/roll。
```

---

## 5. 子任务 B：三轴指标定义

目标：把指导文件中的概念指标落为可计算字段。

必须输出：

```text
metrics/three_axis_metric_spec.md
tables/three_axis_metric_registry.csv
text/brightness_vs_information_boundary.md
```

指标至少包括：

```text
brightness / OCS magnitude：找最亮、最暗、glint 风险。
local contrast：姿态邻域可区分性。
nearest-neighbor ambiguity：光度或图像签名最近邻混淆。
candidate entropy / margin：候选集中程度。
top-k stability：局部扰动下最优候选是否稳定。
OCS-image overlap / JS：通道一致或冲突。
saturation / glint flag：亮但不可用风险。
geometry utility score：观测几何是否值得投入。
roll sensitivity score：fixed-roll 结论在 roll 方向是否迁移。
```

必须明确：

```text
最亮姿态 != 高信息姿态；
高亮但饱和/glint/局部不稳定可标为高风险；
低亮但局部可分性强可标为高信息候选；
真实未知目标姿态反演成功率不是本小项目指标。
```

---

## 6. 子任务 C：三轴搜索种子提取

目标：从路线一 C 结果中筛出首批三轴搜索种子，而不是盲目全空间扫描。

建议种子类别：

```text
bright-seed：fixed-roll 下最亮/高 OCS 姿态。
dark-seed：最暗/低信号姿态。
high-info-seed：OCS/P-DB/conformal 指标显示高可分、高置信姿态。
low-info-seed：ambiguous-flux、nearest-neighbor 混淆、large set_size 姿态。
image-hard-seed：image_only 失败或欠覆盖区域。
ocs-hard-seed：OCS-only 失败区域。
disagreement-seed：OCS 与 image 候选冲突区域。
roll-sensitive-seed：M-roll ±30° 误差显著上升区域。
robust-easy-seed：多通道均稳定区域，用作正对照。
```

必须输出：

```text
seeds/three_axis_seed_candidates.csv
seeds/seed_selection_rules.md
figures/seed_map_fixedroll.png/.pdf
text/seed_set_summary.md
```

每个 seed 至少包含：

```text
record_id 或 yaw/pitch；
来源类别；
来源文件；
关键指标；
为什么值得三轴 roll 扩展；
建议 roll 扫描范围；
风险标记。
```

---

## 7. 子任务 D：采样策略与资源估计

目标：设计从小到大的三轴执行阶段，给出算力/渲染/存储估计。

建议阶段：

```text
P1 seed-roll scan：围绕种子点扫描 roll，例如 roll ∈ {-60,-45,-30,-15,0,15,30,45,60}。
P2 sparse 3-axis grid：粗三轴网格或随机/拉丁超立方采样。
P3 local refinement：围绕最亮、高信息、低信息候选局部加密。
P4 最亮构型与光路解释综合：输出 single-pose 最亮 yaw/pitch/roll + sun/view 构型、入射-表面/材料-探测器光路解释，并保留 utility map 作为辅助标注。
```

必须输出：

```text
sampling/three_axis_sampling_plan.md
tables/three_axis_stage_matrix.csv
resources/render_train_storage_estimate.csv
resources/compute_risk_register.md
```

每个阶段必须列：

```text
姿态数量；
几何数量；
是否需要新渲染；
是否需要新训练；
预计输出；
最低接收标准；
停止/扩展条件。
```

注意：本轮只设计，不执行 P1-P4。

---

## 8. 子任务 E：第一阶段任务草案

目标：形成下一轮可交给 Claude 执行的 P1 seed-roll scan 任务草案。

必须输出：

```text
text/next_task_draft_P1_seed_roll_scan.md
tables/p1_seed_roll_pre_registered_matrix.csv
tables/p1_expected_outputs.csv
```

P1 草案必须限定：

```text
只围绕少量种子点；
优先用 phase63 / L1-G1 或路线一代表几何做 smoke；
不训练 roll-aware 模型；
先计算 OCS magnitude、图像渲染可用性、local contrast、roll sensitivity；
若 smoke 通过，再由 Codex 另行放行正式 P1。
```

---

## 9. 子任务 F：总验收矩阵与红线

必须输出：

```text
tables/three_axis_preflight_gate_matrix.csv
tables/allowed_forbidden_claims_three_axis.csv
audit/generated_files_manifest.csv
audit/numeric_path_consistency_check.csv
audit/redline_self_check.csv
text/codex_review_checklist_for_001.md
```

总验收矩阵至少包含：

```text
输入资产是否齐；
指标是否可计算；
种子是否覆盖 bright / high-info / low-info / hardcase / roll-sensitive；
采样阶段是否可执行；
资源估计是否合理；
下一轮 P1 是否可直接下达；
哪些事项仍需 Codex 裁决。
```

---

## 10. 执行报告结构

报告必须包含：

```text
1. 任务结论摘要：完成 / 部分完成 / 阻塞。
2. 已读文件与红线遵守。
3. 新增脚本和结果目录清单。
4. 输入审计与可复用资产索引。
5. 三轴指标定义。
6. 三轴搜索种子提取。
7. 采样策略与资源估计。
8. 第一阶段 P1 seed-roll scan 任务草案。
9. 总验收矩阵、manifest、数字/路径一致性和红线自检。
10. 交给 Codex 的裁决问题。
```

---

## 11. 成功判据

最低接收标准：

```text
1. 18 号包目录存在，结构清楚。
2. 输入 manifest 与可复用资产索引完成。
3. 三轴指标 registry 完成。
4. 至少给出 5 类 seed 候选：bright、high-info、low-info、hardcase、roll-sensitive。
5. 给出分阶段采样计划与资源估计。
6. 给出下一轮 P1 seed-roll scan 草案。
7. manifest、路径一致性和红线自检完成。
8. 报告写入正确路径，未写成果区、未改 CLAUDE.md、未启动 R128 或路线二/三/四。
```

强接收标准：

```text
1. seed 候选覆盖全部建议类别，并能追溯到 16/17/13/12/11 号结果。
2. 指标定义能直接映射到已有字段或明确列出需新增字段。
3. 采样计划包含 P1-P4 阶段、停止/扩展条件和资源估计。
4. P1 seed-roll scan 草案可直接作为下一轮 Claude 长程任务基础。
5. 明确区分最亮、高信息、低信息和风险几何，避免写成真实反演系统。
```

---

## 12. 最后提醒

本轮只做三轴小项目准备阶段门设计。完成后只提交 18 号包和 001 报告。不要自行把结果升级到成果区，不要生成 Codex 审阅文件，不要修改 `CLAUDE.md`，不要启动三轴正式渲染/训练，不要启动 R128 新路线二。

Codex 后续将裁决：

```text
1. 001 准备包是否通过；
2. 三轴指标、seed、采样计划是否接收；
3. 是否放行 P1 seed-roll scan smoke/正式任务；
4. 是否需要先补读代码或补少量可行性 smoke；
5. R128 是否继续挂起到三轴小项目完成后再回看。
```
