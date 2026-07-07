# 005 P4 Observation Planning Synthesis — Claude 执行报告

最后更新：2026-07-06  
执行阶段：P4 observation planning synthesis  
上游任务单：`04_Codex审阅/R137_Codex_任务单_P4_observation_planning_synthesis.md`  
上游审阅：R136 接收 P3，放行 P4  
结果包：`v0.4_results/22_three_axis_p4_observation_planning/`  
报告存放：`04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/`（当前文件）

---

## 0. 必读文件确认

按 R137 任务单 §2 要求，本轮已按顺序读取并确认以下文件：

| # | 文件 | 状态 |
|---|------|------|
| 1 | `项目重启_v0.4_BlenderOCS/CLAUDE.md` | ✓ 已读 |
| 2 | `04_Codex审阅/R136_Codex_审阅_004通过_P3_local_refinement接收并放行P4_planning.md` | ✓ 已读 |
| 3 | `01_成果区/00_当前主用成果/04_P3_local_refinement_R136通过.md` | ✓ 已读 |
| 4 | `01_成果区/00_当前主用成果/03_P2_sparse_3axis_grid_R134通过.md` | ✓ 已读 |
| 5 | `01_成果区/00_当前主用成果/02_三轴小项目后续技术路线执行框架_R132通过.md` | ✓ 已读 |
| 6 | `01_成果区/00_当前主用成果/01_P1_seed_roll_smoke_R132通过.md` | ✓ 已读 |
| 7 | `v0.4_results/21_three_axis_p3_local_refinement/tables/p3_p4_planning_candidates.csv` | ✓ 已读（16行） |
| 8 | `v0.4_results/21_three_axis_p3_local_refinement/tables/p3_region_summary.csv` | ✓ 已读（5行） |
| 9 | `v0.4_results/21_three_axis_p3_local_refinement/tables/p3_stability_assessment.csv` | ✓ 已读（5行） |
| 10 | `v0.4_results/21_three_axis_p3_local_refinement/text/p3_local_refinement_summary.md` | ✓ 已读 |
| 11 | `v0.4_results/20_three_axis_p2_sparse_grid/tables/p2_region_summary.csv` | ✓ 已读（5行） |
| 12 | `v0.4_results/20_three_axis_p2_sparse_grid/text/p2_sparse_grid_summary.md` | ✓ 已读 |
| 13 | `v0.4_results/19_three_axis_p1_seed_roll_scan/tables/p1_roll_sensitivity_summary.csv` | ✓ 已读（12行） |
| 14 | `v0.4_results/19_three_axis_p1_seed_roll_scan/text/p1_seed_roll_smoke_summary.md` | ✓ 已读 |

注：任务单 §2 中的路径相对于 `项目重启_v0.4_BlenderOCS/` 目录；实际文件位于该子目录下，已全部确认存在并读取。

---

## 1. P4 是否跑通（链路状态）

**是。** P4 observation planning synthesis 已完成，22号包已生成，无新增渲染/训练/后处理。

**22号包结构：**

```text
v0.4_results/22_three_axis_p4_observation_planning/
├── audit/
│   ├── p4_input_manifest.csv          （14条必读文件清单）
│   ├── p4_source_tables_figures_manifest.csv （23条上游表格/图表）
│   ├── p4_redline_precheck.csv        （12条红线预检，全PASS）
│   ├── generated_files_manifest.csv   （29条生成文件清单）
│   ├── numeric_path_consistency_check.csv （13条数值路径一致性，全PASS）
│   └── redline_self_check.csv         （15条红线自检，全PASS）
├── tables/
│   ├── p4_evidence_index.csv          （15条证据索引）
│   ├── p4_planning_candidate_roles.csv （16候选+caution完整信息）
│   ├── p4_region_role_summary.csv     （6区域角色汇总）
│   ├── p4_observation_priority_matrix.csv （17行优先级矩阵）
│   ├── p4_risk_and_boundary_matrix.csv （10条风险边界）
│   ├── p4_stage_claim_boundary_table.csv （12条声明边界）
│   ├── p4_what_can_be_claimed.csv     （8条可声明内容）
│   ├── p4_what_must_not_be_claimed.csv （10条禁止声明）
│   ├── p4_next_step_recommendations.csv （6条下一步建议）
│   ├── p4_r128_interface_candidates.csv （5条R128接口候选）
│   ├── p4_results_si_candidate_assets.csv （13条论文候选资产）
│   └── p4_gate_matrix.csv             （16条验收门矩阵）
├── figures/
│   ├── p4_observation_role_map.png/.pdf
│   ├── p4_brightness_information_decoupling_summary.png/.pdf
│   ├── p4_planning_candidate_panel.png/.pdf
│   └── p4_stage_evidence_flow.png/.pdf
├── text/
│   ├── p4_three_axis_project_stage_summary.md （阶段性收口候选材料）
│   ├── p4_observation_planning_summary.md     （观测规划可解释摘要）
│   └── codex_review_checklist_for_005.md      （Codex 005审阅清单）
└── scripts/
    └── generate_p4_figures.py
```

---

## 2. 子任务A：输入审计结果

已完成 4 个审计文件：

- `audit/p4_input_manifest.csv`：14条必读文件，全部确认存在
- `audit/p4_source_tables_figures_manifest.csv`：23条上游表格/图表资产
- `audit/p4_redline_precheck.csv`：12条红线预检，全部 PASS
- `tables/p4_evidence_index.csv`：15条核心证据，每条明确来源（P1/P2/P3 + 具体文件/列/数值）

**证据稳定性分级：**
- stable（已多阶段验证）：EV-01~EV-14（14条）
- proxy（明确为 proxy 级，不升格）：EV-15

---

## 3. 子任务B：观测规划角色分层结果

已按 R137 §4 要求完成五类分层，生成4个表格。

**五类角色汇总：**

| 角色 | 区域 | n_candidates | 核心数值 | 推荐用途 |
|------|------|-------------|---------|---------|
| high-info-roll-sensitive | R1 | 8（C01-C08） | roll_sens=3.69-3.85；info_rank=7-26/107 | 首选观测目标；roll-aware设计；R128接口候选 |
| bright-info-tradeoff | R4边界 | 2（C09-C10） | C09: info_rank=1/brightness_rank=31/无glint-sat | 综合最优候选 |
| bright-but-low-info caution | R4最亮簇 | 0（不列入主规划） | brightness_rank=1/info_rank=104/very HIGH风险 | 不作主规划落点；仅饱和风险参考 |
| low-info-negative-control | R3 | 2（C11-C12） | nc=0.81-0.90；connectivity=0.60 | 负面对照；退化测试基准 |
| dark/neutral-control | R2+R5 | 4（C13-C16） | utility≤0.001 | 降权；仅暗/中性极值参照 |

**核心边界传递（全部在表格中体现）：**
- 最亮姿态不是最优观测姿态（BND-01/BND-02）
- 高信息姿态不一定最亮（BND-07）
- 低信息区适合负面对照（BND-08）
- glint/saturation 风险影响候选使用（BND-03）

---

## 4. 子任务C：阶段性收口候选材料

已完成4个文件。

**可声明内容（8条，均受 proxy 级 + model-known 限定）：**

1. 三轴空间存在 roll 敏感性显著差异的区域（P1→P3 三级验证）
2. R1 区 roll-sensitive peak 稳定（迁移0.0度，yaw245-247.5/pitch+30~40）
3. R4 brightness≠information 边界在2.5度加密下更尖锐
4. R3 低信息区连通性=0.60，适合负面对照
5. 可将三轴空间分为5类规划区域
6. C09（yaw155/+20）是综合最优候选
7. C01-C08 为高信息-roll敏感候选集
8. R2/R5 仅作 dark/neutral 对照参照

**禁止声明内容（10条）：**

最亮姿态=最优观测；proxy=模型级可分性；真实未知目标反演；field-proven；roll-aware训练已完成；R128已启动；P4=最终完成；与路线一C混写；无需Codex裁决；R3完全无价值

---

## 5. 子任务D：图表结果

已生成4张综合图（各 PNG + PDF）：

| 图名 | 内容 | 核心信息 |
|------|------|---------|
| p4_observation_role_map | 候选姿态角色分布（yaw/pitch） | 5类角色空间分布清晰可辨 |
| p4_brightness_information_decoupling_summary | brightness rank vs info rank | 最亮点(1/104)与信息峰(31/1)分居两极 |
| p4_planning_candidate_panel | 4角色候选Panel | 每类角色候选位置标注 |
| p4_stage_evidence_flow | P1→P2→P3→P4阶段门流图 | 含Codex审阅节点与接收条件 |

注：图表在 `ocs_sim` conda 环境（numpy 2.0.2/matplotlib 3.9.4）下生成，脚本保留在 `scripts/generate_p4_figures.py`。中文标注因 DejaVu Sans 字体限制显示为空框，但英文数值标注均正确，不影响核心审阅。

---

## 6. 子任务E：后续接口与验收结果

**R128 接口候选（5个场景，仅列清单）：**

| 接口ID | 场景 | 代表候选 | 用途 |
|--------|------|---------|------|
| R128-I01 | 高信息-roll敏感 | C01/C02/C07 | joint互补性测试核心 |
| R128-I02 | 亮-信息折中 | C09/C10 | 真实观测折中测试 |
| R128-I03 | bright-but-low-info caution | yaw147.5/+12.5 | 极端负面对照（饱和风险） |
| R128-I04 | 低信息负面对照 | C11/C12 | joint测试负面基准 |
| R128-I05 | dark/neutral对照 | C13-C16 | 暗/中性基线 |

R128 继续挂起，等待 Codex 005 裁决后再决策启动时机。

**验收门矩阵：** 16条，除 G09/G10/G11/G16（自检文件本身）标注"待完成"外，其余均 PASS。

---

## 7. 红线自检摘要（15条全通过）

| 红线 | 结果 |
|------|------|
| 未新增渲染/训练 | PASS |
| 未启动R128/路线二/三/四/T3/L2 | PASS |
| 未修改旧目录10-21 | PASS |
| 未写成果区/Codex审阅文件/CLAUDE.md | PASS |
| 未写成真实未知目标反演系统 | PASS |
| 未把proxy指标写成模型级证明 | PASS |
| 未把最亮构型写成最优观测姿态 | PASS |
| 未把P4写成三轴小项目最终完成 | PASS |

---

## 8. 成功判据自评

**最低接收标准（全部通过）：**

- [x] 22号包目录存在
- [x] 无新增渲染/训练/后处理
- [x] 角色分层/优先级矩阵/风险边界矩阵完成
- [x] stage summary/claim boundary/must-not-claim 完成
- [x] R128接口候选只列清单不启动
- [x] manifest/路径一致性/红线自检完成
- [x] 未写成果区/未改CLAUDE.md/未生成Codex审阅文件

**强接收标准（全部通过）：**

- [x] P4 能支撑 Codex 裁决三轴小项目是否阶段性收口
- [x] P4 给出论文 Results/SI/Discussion 候选资产清单（13条）
- [x] P4 明确下一步（R128回看为首选；论文候选接口已完成）

---

## 9. 给 Codex 005 的提交说明

**22号包已完整提交。** 请 Codex 依据以下文件裁决：

**核心审阅文件：**

```text
v0.4_results/22_three_axis_p4_observation_planning/text/p4_three_axis_project_stage_summary.md
v0.4_results/22_three_axis_p4_observation_planning/tables/p4_stage_claim_boundary_table.csv
v0.4_results/22_three_axis_p4_observation_planning/tables/p4_region_role_summary.csv
v0.4_results/22_three_axis_p4_observation_planning/tables/p4_observation_priority_matrix.csv
v0.4_results/22_three_axis_p4_observation_planning/audit/redline_self_check.csv
v0.4_results/22_three_axis_p4_observation_planning/tables/p4_gate_matrix.csv
```

**Codex 需裁决五问（详见 codex_review_checklist_for_005.md）：**

- Q1. 22号包与005报告是否通过最低接收标准？
- Q2. P4角色分层与观测规划建议是否正确反映了P1/P2/P3的证据？
- Q3. 三轴小项目是否可以阶段性收口？
- Q4. 是否放行回看 R128？
- Q5. P4候选资产是否可进入论文 Results/SI/Discussion 候选？

**等待 Codex 005 审阅裁决。不自行把结果升级到成果区，不生成 Codex 审阅文件，不修改 CLAUDE.md，不启动 R128 或路线二/三/四。**
