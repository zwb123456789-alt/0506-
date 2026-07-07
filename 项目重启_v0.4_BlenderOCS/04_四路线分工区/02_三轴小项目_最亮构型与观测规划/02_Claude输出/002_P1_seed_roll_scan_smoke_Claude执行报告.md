# 002 P1 seed-roll scan smoke Claude 执行报告

最后更新：2026-07-01
执行端：Claude
任务单：`04_Codex审阅/R131_Codex_任务单_P1_seed_roll_scan_smoke.md`
上游阶段门：R130 通过 001，放行 P1 seed-roll scan smoke
结果包：`v0.4_results/19_three_axis_p1_seed_roll_scan/`

## 1. 任务结论摘要

**完成（达强接收标准）。** 96 个非零 roll 渲染单位全部 RENDERED，96 个后处理单位全部 COMPLETE，roll=0 baseline 12/12 对齐 `01_fullrun`。roll 曲线、roll sensitivity、brightness rank shift、glint/saturation flag、3 张图 + summary 全部完成。gate matrix 无 FAIL，consistency 11/11 PASS，redline 12/12 PASS。P1 smoke 链路可执行，已初步观察到最亮构型 roll 稳健、高 |pitch| 暗构型 roll 敏感、brightness 与 information 解耦。

## 2. 已读文件与红线遵守

已读（R131 必读顺序）：
- `CLAUDE.md`（大根目录 + v0.4 子目录）
- `R129` 任务单、`R130` 审阅、成果摘要 `00_三轴小项目准备阶段门设计_R130通过.md`
- 18 号包：`next_task_draft_P1_seed_roll_scan.md`、`p1_seed_roll_pre_registered_matrix.csv`、`three_axis_seed_candidates.csv`、`code_entrypoint_audit.csv`
- 代码入口：`render_full_2664_shadow.py`、`render_mroll_probe.py`、`run_full_postprocess.py`、`run_mroll_probe_postprocess.py`、`image_response_v0_4.py`（头）、`config_v0_4.py`

红线遵守：只做 phase63/L1-G1 单几何、96 单位 smoke；未训练、未启动 P2/P3/P4/R128/路线二三四/T3/L2；未改旧脚本、未改旧目录 10-18、未改姿态网格/OBS_GEOMETRIES/split/backbone/超参；roll=0 未重渲；输出仅写 19 号包 + 本报告，未写成果区、未生成 Codex 审阅文件、未改 CLAUDE.md。

## 3. 新增脚本、渲染、后处理与结果目录清单

新增脚本（均在 `19_.../scripts/`，派生 wrapper 不改旧脚本）：
- `p1_render_seed_roll.py`：派生自 `render_full_2664_shadow.py`，覆盖姿态生成为 12 seed×roll、输出到 19 号包。
- `p1_postprocess_seed_roll.py`：派生自 `run_full_postprocess.py`，覆盖 SHADOW/OUTPUT/GEOM 到 19 号包，参数继承 fullrun。
- `run_p1_all.sh`：8 roll 批次编排（每 roll 一次 Blender 渲染 12 seed + 一次后处理）。
- `a_p1_input_audit.py` / `b_c_metrics.py` / `d_figures.py` / `e_audit_manifest.py`：审计、指标、图表、验收。

结果目录 `v0.4_results/19_three_axis_p1_seed_roll_scan/`（约 54 MB）：
- `render/shadow_passes/phase63/roll±NNN/`：192 EXR（96 camera + 96 sun）+ 8 render_metadata.json。
- `postprocess/phase63/roll±NNN/`：96 linear.exr + 96 ocs.json + mask/png + 8 summary。
- `audit/`（7）、`metrics/`（1）、`figures/`（6）、`tables/`（6）、`text/`（2）、`logs/`（3）。

## 4. P1 输入审计与矩阵锁定（子任务 A）

- `p1_input_manifest.csv`：8 项输入资产全部存在；12/12 roll=0 baseline 就位。
- `p1_locked_run_matrix.csv`：锁定 96 行（12 seed × 8 非零 roll），几何 phase63(L1-G1)，roll=0 复用 01_fullrun。
- `p1_code_entrypoint_audit.csv`：渲染/后处理 driver 只读复用，wrapper 新增，config phase63 SUN[1,0,0.3]/DET[0.5,-1,0.1] 与 baseline 一致。
- `p1_redline_precheck.csv`：10/10 PASS（矩阵 96 行、12 seed、8 roll、baseline 就位、单几何、仅写 19 号包等）。

## 5. 96 单位渲染与后处理完成情况（子任务 B）

- 渲染：8 个 roll 批次各 12/12 RENDERED，exit=0；camera 96 + sun 96 = 192 EXR。GPU OPTIX。
- 后处理：8 个 roll 批次各 OVERALL COMPLETE 12/12；ocs.json 96 + linear.exr 96；无 blocker、无失败姿态。
- `render/p1_render_manifest.csv`（96 行，camera/sun 全 True）、`postprocess/p1_postprocess_manifest.csv`（96 行，ocs_json 全 True）。

## 6. roll 曲线与三轴 smoke 指标（子任务 C）

产出 3 表 + 1 定义（`tables/` + `metrics/p1_metric_definitions_used.md`）：
- `p1_seed_roll_ocs_table.csv`（108 行含 baseline）：ocs_total、可见/贡献像素、local_contrast、glint/saturation、image_usable。
- `p1_roll_curve_metrics.csv`（108 行）：delta_ocs_vs_roll0、rel_delta_pct、brightness_rank、rank_shift。
- `p1_roll_sensitivity_summary.csv`（12 行）：ocs_span_rel=roll_sensitivity_score、max_abs_rank_shift 等。
- `p1_brightness_information_smoke.csv`：brightness rank vs contrast rank 解耦标记。

关键数值（smoke 级）：
- 最亮 & roll 稳健：bright-seed（yaw145/150,p+15）、robust-easy（yaw150,p+10），OCS span_rel 5–7%，rank shift ≤1，但触发 saturation、contrast 排名垫底。
- roll 敏感：high-info（yaw240 系）span_rel 3.2–3.6；low-info/ocs-hard（yaw065 系）1.5–1.6；roll-sensitive/dark（yaw285 系高|pitch|）0.77–1.07；亮度排名漂移最大到 7；high-info 在 roll+15 出现 +200%~+290% roll-induced brightening。
- image_usable：全部 12 seed 在全部 roll 下 =1。

## 7. 图表与可解释摘要（子任务 D）

- `figures/p1_seed_roll_brightness_curves.png/pdf`：12 seed 的 OCS(roll) 曲线。
- `figures/p1_category_roll_sensitivity_panel.png/pdf`：按 roll_sensitivity 排序的条形（色=OCS at roll0）。
- `figures/p1_roll_heatmap_seed_by_roll.png/pdf`：seed×roll 的 rel_delta 热图，亮构型行近白、暗高|pitch|行 ±200%。
- `text/p1_seed_roll_smoke_summary.md`：回答链路是否跑通、最亮点是否迁移、亮但低信息/暗但敏感例子、值得进 P2 的类别、采样计划建议。

## 8. 验收矩阵、manifest、数字/路径一致性与红线自检（子任务 E）

- `tables/p1_smoke_gate_matrix.csv`：8 项，0 FAIL（96 渲染/后处理完成、OCS 可用、baseline 对齐、图像有效、曲线可算、满足 P1 正式扩展条件、无需返工）。
- `tables/p1_next_step_recommendations.csv`：P2 加密建议、seed 分级、proxy 升级、roll-aware 暂不。
- `audit/generated_files_manifest.csv`：438 非 EXR 产物逐一登记 + 288 EXR 汇总登记（render/postprocess manifest 已逐一列）。
- `audit/numeric_path_consistency_check.csv`：11/11 PASS。
- `audit/redline_self_check.csv`：12/12 PASS。

## 9. 交给 Codex 的裁决问题

1. 002 P1 smoke 是否通过、是否升级为当前主用成果。
2. 是否放行 P1 正式扩展或 P2 sparse 3-axis grid（本轮建议在 |pitch|≥70、yaw~240/285 邻域加密）。
3. 是否认可“最亮构型 roll 稳健但低对比/有饱和、高|pitch|暗构型 roll 敏感”作为最亮/高信息/低信息区早期证据。
4. information proxy 是否需在正式阶段升级为 P-DB/margin/entropy（需模型，本轮未做）。
5. 图像可用性判据（受照像素≥50）与 glint/saturation 阈值是否需调整。
6. R128 是否继续挂起到三轴小项目完成后再回看。

（详见 `text/codex_review_checklist_for_002.md`。）
