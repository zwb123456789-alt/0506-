# 001 三轴小项目准备阶段门设计 Claude 执行报告

最后更新：2026-07-01
任务来源：`04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R129_Codex_任务单_三轴小项目准备阶段门设计.md`
交付包：`v0.4_results/18_three_axis_planning_preflight/`

---

## 1. 任务结论摘要

**完成。** 已按 R129 完成三轴小项目准备阶段门设计，生成 18 号准备包（34 个文件）与本报告。
本轮只做准备与规划，**未启动任何三轴渲染/训练**，未启动 R128 / 路线二三四，未写成果区，未改 CLAUDE.md。

一致性检查 14/14 PASS，红线自检 10/10 PASS，输入资产 16/16 OK。

---

## 2. 已读文件与红线遵守

必读（R129 §2）：
- `CLAUDE.md`（大根目录 + v0.4 权威入口）
- `00_路线冻结文件区/01_三轴小项目_最亮构型与观测规划指导文件.md`
- 成果区 `10_路线一C实验主干闭口_D2D4M5_R125通过.md`、`11_路线一C闭口后增强实验清账_R127通过.md`

按需读（R129 §2）：
- `v0.4_results/16_route1c_closure_d2d4_m5/`（D4 地图、D2 通道、M5 协议）
- `v0.4_results/17_route1c_postclosure_enhancement_sweep/`（M-roll full-2664、conformal alpha、渲染日志）
- `v0.4_results/13_l1d3_confidence_pdb/`（hardcase index、PDB、conformal、joined）
- `v0.4_results/11_l1m2_multigeometry_ocs/`（geometry registry、phase24/45/90/120 OCS）
- `v0.4_results/01_fullrun/`（phase63=L1-G1 OCS 基线）
- `06_v0.4_code/01_geometry/`、`02_blender/`（roll 可参数化审计）

**R128 本轮不执行**（仅作为三轴小项目完成后再回看的记忆）。

红线遵守：全部脚本只读打开既有数据，所有产物写入 18 号包；未改旧脚本/metrics/samples/结果目录 10-17；未改姿态网格/OBS_GEOMETRIES/split/backbone/超参；报告写入 `02_Claude输出/`。

---

## 3. 新增脚本与结果目录清单

结果目录：`v0.4_results/18_three_axis_planning_preflight/`

脚本（`scripts/`，7 个，均只读可复现）：
- `a_input_audit.py` — 输入审计与可复用资产索引
- `b_metric_registry.py` — 三轴指标 registry + 派生指标（local_contrast/glint_flag）
- `c_seed_extraction.py` — 9 类三轴搜索种子提取
- `c_figures.py` — 种子图 + brightness-vs-information 图
- `d_sampling_resources.py` — P1-P4 采样阶段矩阵与资源估计
- `e_p1_matrix.py` — P1 seed-roll scan 预注册矩阵
- `f_audit_manifest.py` — manifest / 一致性 / 红线自检

各子目录文件数：audit 7、seeds 4、metrics 1、sampling 1、resources 2、figures 4、tables 6、text 4、scripts 7、logs 1（reference：见 `audit/generated_files_manifest.csv`）。

---

## 4. 输入审计与可复用资产索引（子任务A）

- `audit/input_manifest.csv`：16 资产，全部 OK。OCS 亮度源覆盖五何 roll=0，各 2664：
  phase63（`01_fullrun`）、phase24/45/90/120（`11_l1m2`）。
- `audit/route1c_reusable_assets.md`：D4 地图、hardcase/PDB/conformal/joined、M-roll 边界先验的复用接口。
- `audit/code_entrypoint_audit.csv`：**`render_mroll_probe.py` 已证明 Blender 渲染可参数化到 roll 轴**
  （R116 已注入非零 roll、生成 `roll{+NNN}` label），是三轴渲染可行性关键依据；attitude_grid/postprocess/training 均可扩展但需新增 roll 字段（本轮不做）。
- `audit/redline_precheck.csv`：8 项前置红线 PASS。

---

## 5. 三轴指标定义（子任务B）

- `metrics/three_axis_metric_spec.md`：9+2 指标落为可计算字段，分 A-direct / B-derived / C-need-roll 三档。
- `tables/three_axis_metric_registry.csv`：11 指标，含 concept、公式/字段、来源包、可用性、roll 扩展需求、info_class。
- `text/brightness_vs_information_boundary.md`：**实证 corr(log 亮度, G1→G5 gain) ≈ -0.088**，
  亮度与可救回性几乎无正相关；glint_flag=1 共 3 个姿态。明确 brightness ≠ information。

派生（只读计算，未新渲染）：`seeds/attitude_master_derived.csv` 含 local_contrast 与 glint_flag。

---

## 6. 三轴搜索种子提取（子任务C）

- `seeds/three_axis_seed_candidates.csv`：66 seed，覆盖全部 9 类。
- `seeds/attitude_master_fixedroll.csv`：2664 姿态主表（复现基础）。
- `seeds/seed_selection_rules.md`、`text/seed_set_summary.md`：规则与摘要。
- `figures/seed_map_fixedroll.png/.pdf`、`figures/brightness_vs_information.png/.pdf`。

种子类别与代表：

| 类别 | n | 代表 | 关键指标 |
|---|---:|---|---|
| bright-seed | 8 | yaw145_pitch+015 | ocs_total=0.178 |
| dark-seed | 8 | yaw285_pitch-070 | ocs_total=0.0106 |
| high-info-seed | 8 | yaw240_pitch+030 | gain=179.2° |
| low-info-seed | 8 | yaw065_pitch+070 | cand_spread=86.5 |
| ocs-hard-seed | 8 | yaw065_pitch+075 | ocs_g5_err=171.8° |
| image-hard-seed | 2 | yaw165_pitch-020 | image-hard(image_only) |
| disagreement-seed | 8 | yaw250_pitch-010 | disagreement-hard |
| roll-sensitive-seed | 8 | yaw285_pitch-085 | d(err30-err15)=131.2° |
| robust-easy-seed | 8 | yaw150_pitch+010 | ocs_total=0.175 |

每个 seed 含 record_id/yaw/pitch、来源类别、来源文件、关键指标、为何值得 roll 扩展、建议 roll 范围、风险标记。全部可追溯到 11/13/16/17 号结果。

image-hard 仅 2 个，因 clean/P-INT 下 image_only 近饱和、该标签本就极少（约 3 条），非提取遗漏。

---

## 7. 采样策略与资源估计（子任务D）

- `sampling/three_axis_sampling_plan.md`、`tables/three_axis_stage_matrix.csv`：P1-P4 阶段，每阶段列姿态/几何/是否新渲染/是否新训练/预计输出/最低接收/停止扩展条件。
- `resources/render_train_storage_estimate.csv`（基于 17 号 M-roll 实测 ≈1.0 s/姿态、0.26 MB/姿态）：

| 阶段 | 渲染单位 | 渲染估计 | 存储估计 |
|---|---:|---:|---:|
| P1 seed-roll scan | 96 | ~0.03 h | ~25 MB |
| P2 sparse 3-axis grid | 3744 | ~1.0 h | ~1.0 GB |
| P3 local refinement | ~32400 | ~9.0 h | ~8.5 GB |
| P4 planning synthesis | 0 | 0 | 0 |

- `resources/compute_risk_register.md`：三轴空间爆炸、P3 存储膨胀、渲染速率漂移、roll-aware 训练未放行、split 污染、中文路径、环境错配等风险与缓解。

本轮只设计，未执行 P1-P4。

---

## 8. 第一阶段 P1 seed-roll scan 任务草案（子任务E）

- `text/next_task_draft_P1_seed_roll_scan.md`：可直接作为下一轮 Claude 任务基础。
- `tables/p1_seed_roll_pre_registered_matrix.csv`：12 类别代表种子 × 8 非零 roll = 96 渲染单位（roll=0 复用不重渲）。
- `tables/p1_expected_outputs.csv`：OCS(roll) 曲线、contrast(roll)、roll sensitivity、图像可用性 flag、汇总图与结论。

P1 限定：仅少量种子；仅 phase63（L1-G1）smoke；不训练 roll-aware 模型；只算 OCS magnitude / 图像可用性 / local contrast / roll sensitivity；smoke 通过后交 Codex 另行放行正式 P1。

---

## 9. 总验收矩阵、manifest、一致性与红线自检（子任务F）

- `tables/three_axis_preflight_gate_matrix.csv`：输入齐、指标可算、种子覆盖、采样可执行、资源合理、P1 可下达、brightness/information 区分——全 PASS；待裁决事项指向 checklist。
- `tables/allowed_forbidden_claims_three_axis.csv`：allowed 6 / forbidden 8。
- `audit/generated_files_manifest.csv`：34 文件。
- `audit/numeric_path_consistency_check.csv`：**14/14 PASS**（seed 总数 66、9 类齐、master 2664、P1=96、registry=11、种子可追溯等）。
- `audit/redline_self_check.csv`：**10/10 PASS**。
- `text/codex_review_checklist_for_001.md`：Codex 审阅清单。

---

## 10. 交给 Codex 的裁决问题

1. 001 准备包是否通过、是否进入成果区。
2. 三轴指标 registry、66 seed（9 类）、P1-P4 采样计划是否接收。
3. 是否放行 P1 seed-roll scan smoke（96 渲染单位，仅 phase63）。
4. P1 先 smoke 还是直接放行正式 P1；roll-aware 训练（C 类）放行时机。
5. 是否需要先补读 `05_postprocess` / `07_training` 的 roll 字段改造。
6. R128 是否继续挂起到三轴小项目完成后再回看。
7. P1 输出目录建议 `19_three_axis_p1_seed_roll_scan/` 是否采纳。

---

## 附：成功判据对照

最低接收（8 项）与强接收（5 项）均满足：18 号包结构清楚、输入 manifest 与可复用索引完成、指标 registry 完成、9 类 seed 齐全（含 bright/high-info/low-info/hardcase/roll-sensitive）且可追溯到 16/17/13/12/11、P1-P4 采样计划含停止/扩展与资源估计、P1 草案可直接下达、manifest/一致性/红线自检完成、报告写入正确路径且未越红线。
