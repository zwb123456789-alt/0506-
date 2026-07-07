# 004 P3 local refinement Claude 执行报告

最后更新：2026-07-03
任务单：`04_Codex审阅/R135_Codex_任务单_P3_local_refinement.md`
执行端：Claude
结果包：`v0.4_results/21_three_axis_p3_local_refinement/`

---

## 0. 结论速览

R135 P3 local refinement 已按强接收标准完成。在 P2 sparse grid（5 度）基础上对 primary
区域 R1/R4/R3 做 **2.5 度局部加密**，R2/R5 保留少量 5 度对照点。107 唯一 pose × 9 roll = 963
pose-roll 单位，新渲染 921（< 2000 上限），整数点 roll=0 复用 fullrun。gate 19/19、
consistency 13/13、redline 15/15 全 PASS。R135 §5 五问全部得到回答，P4 planning candidates
16 个已就绪。未启动 P4/R128/训练，未写成果区，未改 CLAUDE.md。

---

## 1. 必读文件（已按序读取）

```text
CLAUDE.md（大根 + v0.4 子目录）
R134_Codex_审阅_003通过_P2_sparse_grid接收并放行P3_local_refinement.md
01_成果区/00_当前主用成果/03_P2_sparse_3axis_grid_R134通过.md
01_成果区/00_当前主用成果/02_三轴小项目后续技术路线执行框架_R132通过.md
20_pack: p2_p3_refinement_candidates.csv / p2_sparse_grid_metrics.csv / p2_region_summary.csv /
         p2_next_step_recommendations.csv / p2_sparse_grid_summary.md
（并读取 P2 全套脚本与 fullrun render/postprocess driver 以复用链路）
```

---

## 2. 关键设计决策：2.5 度真加密 + 半度安全 label

R135 §3 允许 2.5 或 5 度步长。核查发现：若统一 5 度，P3 网格与 P2 几乎完全重叠，缺乏
refinement 价值；故 primary 区（R1/R4/R3）采用 **2.5 度真加密**，R2/R5 用 5 度对照点。

技术核查结论：

- 渲染 driver `euler_to_matrix4` 用 `math.radians(float)`，浮点姿态可直接渲染。
- 后处理 driver `process_one_attitude` 用 label 定位并命名所有输出，label 唯一即无碰撞。
- fullrun 是完整 5 度整数网格（2664 点），**无 2.5 度点**。

据此设计半度安全 label 编码（度×10 整数）：

```text
整数点: yaw245.0/+30.0 -> yaw2450_pitchp0300_roll+015（并保留 fullrun 兼容 label 供 roll=0 复用）
半度点: yaw147.5/+12.5 -> yaw1475_pitchp0125_roll-060
```

复用与新渲染规则：

```text
整数 5 度点 & roll=0     : 复用 01_fullrun（42 点，不重渲）
半度点 & roll=0          : fullrun 无网格 -> 新渲染（65 点），manifest 标注 source=21_pack，不静默缺失
全部非零 roll            : 新渲染（856 单位）
```

该决策经作者确认后执行（2.5 度真加密 + 先 smoke 再全量）。

---

## 3. 子任务 A：预注册

脚本 `scripts/a_p3_preregister.py`。产出：

```text
audit/p3_input_manifest.csv
tables/p3_local_refinement_pre_registered_matrix.csv
tables/p3_region_definition.csv
audit/p3_redline_precheck.csv
audit/p3_preregister_summary.json
```

规模：

```text
区域 5（primary=3, control=2）
  R1_high_info      : yaw240-250 × pitch+30-40（2.5 度）-> 25 pose
  R4_bright_info_boundary: yaw145-160 × pitch+10-25（2.5 度）-> 49 pose
  R3_low_info_connectivity: yaw55-65 × pitch+60-70（2.5 度）-> 25 pose
  R2_control        : yaw280/285 × pitch-85/-80（5 度）-> 4 pose
  R5_control        : yaw205/210 × pitch-10/-5（5 度）-> 4 pose
唯一 pose 107（整数 42 + 半度 65），无区域间重叠
pose-roll 单位 963；新渲染 921（非零 roll 856 + 半度 roll0 65）< 2000 上限
整数点 roll=0 fullrun 覆盖 42/42 OK
redline precheck 13/13 PASS
```

---

## 4. 子任务 B：渲染与后处理

脚本 `scripts/p3_render_local_refinement.py`（Blender wrapper，派生自 fullrun driver）、
`scripts/p3_postprocess_local_refinement.py`（ocs_sim python wrapper）、
`scripts/run_p3_all.sh`（9 roll 批次编排）。产出：

```text
render/p3_render_manifest.csv（921 行，camera/sun 全 True）
postprocess/p3_postprocess_manifest.csv（921 行，ocs 全 True）
logs/p3_render_postprocess.log
```

执行结果：

```text
9 roll 批次全部 exit=0
新渲染 camera 921 / sun 921 / linear 921 / ocs 921
量纲 r_max=1.472605, i_scale=5.44e-01, pixel_area=1.60e-04（与 fullrun/P2 一致）
image_usable = 963/963；无失败、无静默跳过
smoke（roll+15 2 个半度点）先行验证链路通过后再全量
```

---

## 5. 子任务 C：稳定性指标

脚本 `scripts/b_c_metrics.py`。产出：

```text
tables/p3_local_refinement_metrics.csv（963 行）
tables/p3_region_summary.csv
tables/p3_stability_assessment.csv
tables/p3_high_brightness_refined_candidates.csv
tables/p3_high_information_refined_candidates.csv
tables/p3_low_information_connectivity.csv
tables/p3_p4_planning_candidates.csv
metrics/p3_metric_definitions_used.md
```

计算指标：ocs_total、brightness_rank、neighbor_contrast_ypr（2.5 度邻域）、
roll_sensitivity_score、rank_shift、glint/saturation flag、image_usable、
local_peak_migration、local_information_stability、low_info_connectivity、
p4_planning_utility_score。

### R135 §5 五问回答

```text
Q1 R4 最亮点是否迁移：
   P2(5度)最亮 yaw150/+15；P3 加密后迁移到 yaw147.5/+12.5（迁移 3.54 度，更低 yaw/pitch 角落）。
   最亮前 5 名落在 yaw145-150 × pitch+10~15 半度点，最亮簇仍连片。5 度网格低估了亮度峰确切位置。

Q2 R4 高信息边界点是否稳定/可作折中候选：
   info rank=1 仍稳定在 yaw155/+20（nc=1.198），相邻半度点 rank2-5 紧随（nc≈1.13-1.20）成片。
   brightness_rank=31、无 glint/sat -> 可作亮-信息折中候选纳入 P4。

Q3 R1 roll-sensitive peak 是否稳定：
   完全稳定（迁移 0.0 度）。峰在 yaw245-247.5 × pitch+30~40，roll_sens≈3.69-3.85，
   mean_rs=3.497（全区最高），info_stability=0.947。高|pitch|/yaw240 系 roll 敏感性确认。

Q4 R3 低信息区是否连通/可作负面对照：
   较连通。low_info_connectivity=0.60，info_stability=0.92，mean_nc=0.771（primary 最低）。
   适合作观测规划负面对照。

Q5 R2/R5 是否仅对照定位/应降权：
   是。R2 utility=0.001、R5 utility=-0.162，仅 dark/neutral 对照，P4 主规划应降权。
```

### 区域 utility（P3 加密后）

```text
R1_high_info      utility=0.457 mean_rs=3.497（roll 最敏感）
R4_bright_info_boundary utility=0.302 mean_ocs=9.76e-02（最亮）rs=0.093（roll 稳健）
R3_low_info_connectivity utility=0.195 mean_nc=0.771（低信息，连通）
R2_control        utility=0.001
R5_control        utility=-0.162
排名 R1 > R4 > R3 > R2 > R5，与 P2 一致（归一化基准为 P3 分布，序不变）。
```

### brightness ≠ information 在加密下更尖锐

```text
R4 最亮点 yaw147.5/+12.5 的 info_rank = 104/107（几乎最低信息）；
info rank=1 在 yaw155/+20，其 brightness_rank = 31/107；
二者分处 R4 区不同角落。brightness≠information 边界在 2.5 度加密下维持并更清晰分离。
```

---

## 6. 子任务 D：图表与解释

脚本 `scripts/d_figures.py`。产出（png+pdf 各 5 张）：

```text
figures/p3_refined_brightness_map.png/.pdf
figures/p3_refined_information_proxy_map.png/.pdf
figures/p3_peak_migration_panel.png/.pdf
figures/p3_low_info_connectivity_panel.png/.pdf
figures/p3_planning_candidate_scatter.png/.pdf
text/p3_local_refinement_summary.md
```

---

## 7. 子任务 E：验收矩阵与下一步

脚本 `scripts/e_audit_manifest.py`。产出：

```text
tables/p3_gate_matrix.csv（19/19 PASS）
tables/p3_next_step_recommendations.csv
audit/generated_files_manifest.csv
audit/numeric_path_consistency_check.csv（13/13 PASS）
audit/redline_self_check.csv（15/15 PASS）
text/codex_review_checklist_for_004.md
```

P4 planning candidates 16 个（受控）：

```text
high-info-roll-sensitive（R1，8 个）：yaw245-247.5 × pitch+30~40，p4_utility 0.44-0.46
bright-info-tradeoff（R4，2 个）：yaw155/+20（info峰）、yaw152.5/+20
low-info-negative-control（R3，2 个）：yaw55-57.5 × pitch+60~62.5
dark/neutral-control（R2/R5，4 个）：降权对照
```

---

## 8. 成功判据对照

强接收标准：

```text
1. P3 预注册矩阵全部完成                     ✓（107 pose × 9 roll，规模受控）
2. R1/R4/R3 形成稳定性判断                   ✓（peak 迁移/roll 敏感/连通性均量化）
3. P4 planning candidates 明确且规模可控     ✓（16 个，分角色）
4. 图表与 summary 能直接支撑 Codex 裁决 P4    ✓（5 图 + summary + checklist）
```

---

## 9. 红线自检

```text
只做 phase63/L1-G1 单几何                              ✓
只做 P3 local refinement 受控规模（921 新渲染）          ✓
未训练/无 roll-aware 训练                              ✓
未改旧脚本/旧结果目录 10-20（只读 fullrun/P2）           ✓
整数点 roll=0 复用 fullrun、半度点 roll=0 新渲染不静默缺失 ✓
未改姿态网格步长定义/OBS_GEOMETRIES/split/backbone/超参  ✓（2.5 度为 P3 新增局部加密）
未启动 P4/R128/路线二三四/T3/L2                         ✓
未写成果区/未生成 Codex 审阅文件/未改 CLAUDE.md          ✓
未把 P3 写成三轴小项目完成/真实反演系统                  ✓
最亮构型未写成最优观测姿态（brightness≠info 维持）       ✓
neighbor_contrast_ypr 未升格为模型级信息量              ✓（仍标注 smoke/proxy 级）
```

---

## 10. 待 Codex 裁决

```text
1. 004 P3 执行报告与 21 号包是否通过、是否升级为当前主用成果摘要。
2. 是否放行 P4 observation planning synthesis。
3. 2.5 度加密（含半度点新渲染）方案与复用说明是否接收。
4. P4 planning candidates（16 个）规模是否合理。
5. R128 是否继续挂起到 P4 完成后再回看。
```

本轮只做 P3 local refinement，只提交 21 号包与本 004 报告，不自行升级成果区、不生成 Codex
审阅文件、不修改 CLAUDE.md、不启动 P4/roll-aware 训练/R128。
