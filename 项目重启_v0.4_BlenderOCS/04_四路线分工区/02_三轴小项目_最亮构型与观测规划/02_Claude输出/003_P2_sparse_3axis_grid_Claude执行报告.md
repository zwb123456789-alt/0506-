# 003 P2 sparse 3-axis grid Claude 执行报告

最后更新：2026-07-03  
执行端：Claude  
任务单：`04_Codex审阅/R133_Codex_任务单_P2_sparse_3axis_grid.md`  
上游阶段门：R132 通过 002，P1 seed-roll smoke 接收，放行 P2 sparse 3-axis grid  
结果包：`v0.4_results/20_three_axis_p2_sparse_grid/`

---

## 1. 任务结论摘要

**完成（达强接收标准）。** 1000 个非零 roll 渲染单位全部 RENDERED，1000 个后处理单位全部 COMPLETE，roll=0 baseline 125/125 复用 `01_fullrun`。7 张指标/候选表、4 张图表（png+pdf）、summary.md 全部完成。gate matrix 16/16 PASS，consistency 12/12 PASS，redline 14/14 PASS。P2 链路跑通，P1 观察在局部三轴邻域中得到验证，brightness≠information 边界维持，P3 refinement candidates 14 个（规模受控）。

---

## 2. 已读文件与红线遵守

已读（R133 必读顺序）：

- `CLAUDE.md`（大根目录 + v0.4 子目录）
- `R132_Codex_审阅_002通过_P1_seed_roll_smoke接收并放行P2_sparse_grid.md`
- `01_成果区/00_当前主用成果/01_P1_seed_roll_smoke_R132通过.md`
- `01_成果区/00_当前主用成果/02_三轴小项目后续技术路线执行框架_R132通过.md`
- P1 三张数据表（`p1_roll_sensitivity_summary.csv`、`p1_brightness_information_smoke.csv`、`p1_next_step_recommendations.csv`）
- P1 脚本（`p1_render_seed_roll.py`、`p1_postprocess_seed_roll.py`、`b_c_metrics.py`、`d_figures.py`、`a_p1_input_audit.py`、`e_audit_manifest.py`、`run_p1_all.sh`）
- 原始 driver（`render_full_2664_shadow.py`、`run_full_postprocess.py`）
- P1 预注册矩阵（`p1_seed_roll_pre_registered_matrix.csv`）

红线遵守：只做 phase63/L1-G1 单几何；1000 非零 roll 渲染单位 < 2500 上限；未训练、未启动 P3/P4/R128/路线二三四；未改旧脚本、未改旧目录 10-19；roll=0 未重渲；输出仅写 20 号包 + 本报告，未写成果区、未生成 Codex 审阅文件、未改 CLAUDE.md；未把 P2 写成三轴小项目完成；未声称真实未知目标反演系统。

---

## 3. 新增脚本、渲染、后处理与结果目录

### 3.1 新增脚本（均在 `20_.../scripts/`，派生 wrapper 不改旧脚本）

| 脚本 | 说明 |
|------|------|
| `a_p2_preregister.py` | 子任务A：区域定义、预注册矩阵、input manifest、redline precheck |
| `p2_render_sparse_grid.py` | 派生自 `render_full_2664_shadow.py`；覆盖姿态生成为 125 pose×roll，输出到 20 号包 |
| `p2_postprocess_sparse_grid.py` | 派生自 `run_full_postprocess.py`；覆盖 SHADOW/OUTPUT/GEOM 到 20 号包 |
| `run_p2_all.sh` | 8 roll 批次编排（每 roll 一次 Blender 渲染 125 pose + 一次后处理） |
| `b_c_metrics.py` | 子任务B/C：render/postprocess manifest + 三轴指标全集 |
| `d_figures.py` | 子任务D：4 张图表 |
| `e_audit_manifest.py` | 子任务E：验收矩阵、manifest、一致性、红线自检、codex checklist |

### 3.2 结果目录 `v0.4_results/20_three_axis_p2_sparse_grid/`

```
render/shadow_passes/phase63/roll±NNN/  ：2000 EXR（1000 camera + 1000 sun）
postprocess/phase63/roll±NNN/           ：1000 linear.exr + 1000 ocs.json + 8 summary
audit/                                  ：7 文件（preregister_summary.json, manifests, precheck, consistency, redline, generated_files）
tables/                                 ：9 文件（预注册矩阵、region定义、metrics、region汇总、4类候选、gate matrix、next steps）
metrics/                                ：p2_metric_definitions_used.md
figures/                                ：8 文件（4张图 × png+pdf）
text/                                   ：p2_sparse_grid_summary.md, codex_review_checklist_for_003.md
logs/                                   ：p2_render_postprocess.log
```

---

## 4. 子任务A：P2 sparse grid 预注册

**区域设计（5 区域，全部对齐 5 度网格）：**

| 区域 | 中心 yaw | 中心 pitch | pitch 范围 | P1 来源 |
|------|---------|-----------|-----------|---------|
| R1_high_info | 240 | +25 | +15..+35 | high-info-seed yaw240 系 |
| R2_dark_rollsens | 285 | -75 | -85..-65 | dark/roll-sensitive-seed yaw285 系 |
| R3_low_info | 65 | +70 | +60..+80 | low-info/ocs-hard-seed yaw065 系 |
| R4_bright_robust | 150 | +15 | +5..+25 | bright/robust-easy-seed yaw150 系 |
| R5_neutral | 200 | 0 | -10..+10 | fullrun 中性背景对照 |

网格：yaw ±{0,5,10} × pitch ±{0,5,10} × roll {-60,-45,-30,-15,0,+15,+30,+45,+60}。

**规模核算：** 5 区域 × 25 pose = 125 唯一 (yaw,pitch) 点（无区域间重叠）× 9 roll = 1125 单位；非零 roll 渲染单位 1000 < 2500 上限。roll=0 全部 125 点在 `01_fullrun` 中可复用（0 缺失）。

- `audit/p2_input_manifest.csv`：8 资产全部存在（PASS）
- `tables/p2_sparse_grid_pre_registered_matrix.csv`：1125 行（125 pose × 9 roll）
- `tables/p2_region_definition.csv`：5 区域定义
- `audit/p2_redline_precheck.csv`：13/13 PASS

---

## 5. 子任务B：渲染与后处理完成情况

渲染：8 个 roll 批次各 125/125 RENDERED，exit=0；camera 1000 + sun 1000 = 2000 EXR。GPU OPTIX。

后处理：8 个 roll 批次各 OVERALL COMPLETE 125/125；ocs.json 1000 + linear.exr 1000；无 blocker，无失败姿态。

- `render/p2_render_manifest.csv`（1000 行，camera/sun 全 True）
- `postprocess/p2_postprocess_manifest.csv`（1000 行，ocs_json 全 True）
- image_usable = 1（全部 1125 pose-roll 单位）

---

## 6. 子任务C：三轴指标与区域汇总

产出：7 表 + 1 定义文档（`tables/` + `metrics/p2_metric_definitions_used.md`）。

### 6.1 指标表概况

- `p2_sparse_grid_metrics.csv`（1125 行）：ocs_total、brightness_rank、rank_shift_vs_roll0、pixel_local_contrast、**neighbor_contrast_ypr**（新增三轴局部信息 proxy）、roll_sensitivity_score、glint/saturation/image_usable。全部无 nan，ocs 全 > 0。
- `p2_region_summary.csv`（5 行）：区域均值、risk_frac、utility 评分。
- 候选清单：high_brightness 前 20、high_information 前 20、low_information 前 20、P3 refinement 14 个。

### 6.2 关键数值

**区域效用排名（region_utility_score）：**

| 区域 | utility | mean_ocs | mean_nc | mean_roll_sens | risk_frac |
|------|---------|----------|---------|----------------|-----------|
| R4_bright_robust | **0.251** | 8.65e-02 | 1.199 | 0.088 | 0.48 |
| R1_high_info | **0.234** | 3.94e-02 | 1.068 | 2.661 | 1.00 |
| R3_low_info | 0.063 | 2.62e-02 | 0.798 | 1.512 | 1.00 |
| R2_dark_rollsens | -0.037 | 2.02e-02 | 0.626 | 0.845 | 1.00 |
| R5_neutral | -0.149 | 1.70e-02 | 0.274 | 0.435 | 1.00 |

**P1 观察在局部邻域是否保持：**

- 最亮构型 roll 稳健：R4 mean_roll_sensitivity = 0.088（全区域最低）；最亮4个 pose（yaw150/145,pitch+15/+10）roll_sensitivity 0.052–0.070。**保持。**
- 最亮构型局部对比偏低：亮度 rank=1 的 pose（yaw150,+15）info rank = 60/125。**保持。**
- 高|pitch|区 roll 敏感：R1 mean_roll_sensitivity = 2.661（全区域最高）；单点最高达 3.85（yaw245,+35）。**保持。**
- brightness ≠ information 解耦：brightness rank=1（yaw150,+15）vs info rank=1（yaw155,+20），两点不同。**保持，并在局部三轴邻域中量化。**

**roll_sensitivity_score 范围（与 P1 同口径）：**

| P1 smoke 观察 | P1 值 | P2 邻域均值 |
|--------------|-------|------------|
| high-info yaw240 系 | 3.2–3.6 | 2.661（R1 区域均值） |
| low-info yaw065 系 | 1.5–1.6 | 1.512（R3 区域均值） |
| roll-sensitive yaw285 系 | 0.77–1.07 | 0.845（R2 区域均值） |
| bright yaw145/150 系 | 5–7% span → 0.05–0.07 | 0.088（R4 区域均值） |

量级吻合，验证 P1 smoke 级观察在局部三轴邻域中稳定。

**rank_shift 范围：** -93 .. +107（roll 对亮度排名影响非常显著，说明 roll 轴确实改变 125 pose 间的相对亮度序，不能忽略 roll 影响）。

---

## 7. 子任务D：图表与可解释摘要

- `figures/p2_sparse_grid_brightness_map.png/pdf`：5 区域 yaw×pitch 亮度网格图（roll=0），可视化各区域亮度分布。
- `figures/p2_sparse_grid_information_proxy_map.png/pdf`：5 区域 yaw×pitch neighbor_contrast_ypr（pose 均值）信息图，可视化局部三轴信息 proxy 的空间分布。
- `figures/p2_region_roll_sensitivity_panel.png/pdf`：左：5 区域 roll_sensitivity 箱线图+散点；右：region_utility_score 条形图。
- `figures/p2_brightness_vs_information_scatter.png/pdf`：亮度 vs 信息 proxy 散点（marker 大小 ∝ roll_sensitivity），直接可视化 brightness≠information 解耦结构。
- `text/p2_sparse_grid_summary.md`：可解释摘要（链路、邻域验证、区域特征、P3候选、信息proxy边界、红线自检）。

---

## 8. 子任务E：验收矩阵、manifest、数字/路径一致性、红线自检

- `tables/p2_gate_matrix.csv`：16 项，**0 FAIL**（渲染后处理完成、OCS/指标可用、baseline 对齐、图像有效、指标表完整、P3候选规模受控、图表完成、红线遵守）。
- `tables/p2_next_step_recommendations.csv`：7 项建议（P3 区域优先级、信息 proxy 升级条件、R128 维持挂起）。
- `audit/generated_files_manifest.csv`：4057 非 EXR 产物逐一登记 + 3000 EXR 汇总登记。
- `audit/numeric_path_consistency_check.csv`：12/12 PASS。
- `audit/redline_self_check.csv`：14/14 PASS。
- `text/codex_review_checklist_for_003.md`：7 个 Codex 必答问题。

---

## 9. 交给 Codex 的裁决问题

1. 003 P2 sparse grid 执行报告是否通过？是否可升级为当前主用成果？
2. P2 sparse grid 链路与邻域验证结论是否作为三轴小项目 P2 阶段成果接收？
3. 是否放行 **P3 local refinement**？（建议优先区域：R1 yaw245±5/pitch+25–+35；R4 yaw155,+20±5 边界点。）
4. `neighbor_contrast_ypr` 是否被接收为 smoke/proxy 级三轴局部信息指标？P-DB/margin/entropy 升级是否需要在 P3 前另行阶段门？
5. region_utility_score 排名（R4 > R1 > R3 > R2 > R5）是否作为 P3 优先级参考接收？
6. P3 refinement candidates 规模（14 个，覆盖 5 区域）是否合理，是否需要裁剪或扩充？
7. R128 是否继续挂起到三轴小项目（含 P3/P4）完成后再回看？

（详见 `text/codex_review_checklist_for_003.md`。）
