# R160 Codex 任务单：P4-PHYS-G 三轴小项目总收口材料包

最后更新：2026-07-06  
任务类型：给 Claude 的 D/A 类只读整理任务  
上游依据：R158 接收 011/28，P4-PHYS-F 按受控采样包络收口  
本轮目标：不新增实验，把 P4-PHYS-A/B/C/D/E/F 的稳定证据整理为三轴小项目可写作的总收口材料包。  

## 1. 本轮目标

P4-PHYS-A 到 F 已形成以下稳定链条：

```text
R148：fixed phase63/L1-G1 下 top-1 = yaw245/pitch27.5/roll+15，OCS=0.20889048。
R150：fixed top-1 主机制为金属主体大面元近镜面对齐，隐身板小增量只解释排序差。
R152：fixed 几何下近镜面金属机制为 PARTIAL_GENERALITY。
R154：pure sun / pure view 小矩阵中最亮姿态迁移，但仍由金属主体连续机制解释。
R156：3×3 sun/view 组合角落 Hsp_vm 中 C_R3 反超，暴露角落宽瓣机制。
R158：Hsp_vm 局部加密显示受控包络最高 = yaw35/pitch75/roll-20 @ sp5_vm7，OCS≈0.27194；停止继续追角落。
```

本轮 P4-PHYS-G 只做总收口整理，不渲染、不训练、不新增搜索。目标是生成一份可供 Codex 最终审阅的三轴小项目材料包，回答：

```text
1. 当前可写的最亮构型到底是哪一个，边界怎么写。
2. 近镜面机制与宽瓣/几何因子机制如何并列而不互相矛盾。
3. 哪些结论可以进 Results/SI，哪些只能进 Limitations/Boundary。
4. Fig.8 / Table / SI dataset 应如何组织。
```

## 2. 输出位置

新结果包写入：

```text
v0.4_results/29_three_axis_p4phys_g_closure_pack/
```

执行报告写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/012_P4PHYS_G_closure_pack_Claude执行报告.md
```

建议目录：

```text
audit/
tables/
figures/
text/
scripts/
logs/
```

## 3. 必读文件

按顺序读取：

```text
CLAUDE.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R144_Codex_技术路线_三轴小项目最亮构型与光路解释.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R148_Codex_审阅_006B通过_fixed几何top1闭口并放行P4PHYSB.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R150_Codex_审阅_007通过_P4PHYSB光路归因接收并放行P4PHYSC.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R152_Codex_审阅_008通过_PARTIAL_GENERALITY并放行P4PHYSD.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R154_Codex_审阅_009通过_P4PHYSD小矩阵接收并放行P4PHYSE.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R156_Codex_审阅_010通过_NEED_LOCAL_STEP_REFINEMENT并放行P4PHYSF.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R158_Codex_审阅_011通过_P4PHYSF采样包络收口并停止追角落.md
04_四路线分工区/00_总览与裁决/02_Claude输出/017_论文骨架表_持续维护_Claude输出.md
04_四路线分工区/00_总览与裁决/02_Claude输出/018_术语映射表_内部名到论文名_持续维护_Claude输出.md
```

读取数据表：

```text
v0.4_results/23B_three_axis_p4phys_pitch_boundary_followup/
v0.4_results/24_three_axis_p4phys_b_light_path_attribution/
v0.4_results/25_three_axis_p4phys_c_mechanism_generality/
v0.4_results/26_three_axis_p4phys_d_sunview_small_matrix/
v0.4_results/27_three_axis_p4phys_e_sunview_3x3_cross_grid/
v0.4_results/28_three_axis_p4phys_f_hspvm_local_refinement/
```

只读这些包，不得修改 20/21/23A/23B/24/25/26/27/28。

## 4. 必做输出

### A. 证据索引

```text
audit/input_manifest.csv
audit/source_table_manifest.csv
audit/redline_precheck.csv
tables/p4physG_evidence_trace.csv
```

必须列出每个 claim 对应的上游 R 编号、报告、结果表与关键数值。

### B. 统一结论表

```text
tables/p4physG_brightest_configuration_summary.csv
tables/p4physG_mechanism_taxonomy.csv
tables/p4physG_claim_boundary_table.csv
tables/p4physG_si_dataset_map.csv
```

必须包含：

```text
fixed geometry top-1：A_top1 / yaw245 pitch27.5 roll+15 / OCS=0.20889048
controlled envelope brightest：yaw35 pitch75 roll-20 @ sp5_vm7 / OCS≈0.27194
机制 1：near-specular large-facet alignment
机制 2：metal wide-lobe / geometric-factor highlight
不可写边界：全局最亮、真实材料级、真实未知目标反演
```

### C. 图表与文本草案

```text
figures/p4physG_mechanism_taxonomy_schematic.png
figures/p4physG_mechanism_taxonomy_schematic.pdf
text/p4physG_results_paragraph_draft.md
text/p4physG_fig8_caption_draft.md
text/p4physG_limitations_boundary_text.md
text/p4physG_next_step_recommendation.md
```

图只做整理型 schematic，可复用已有图表元素或简洁矢量图，不得伪造新实验图。

### D. Codex 审阅接口

```text
tables/p4physG_gate_matrix.csv
audit/redline_self_check.csv
audit/generated_files_manifest.csv
text/codex_review_checklist_for_012.md
```

## 5. 红线

```text
不得新增渲染。
不得训练。
不得启动 R128。
不得启动路线二/三/四。
不得做任何新 sun/view/pose 搜索。
不得把 28 包最高点写成全局最亮。
不得把 nsm=0 的宽瓣机制写成严格近镜面。
不得把 B0 proxy 写成真实 material-level attribution。
不得写论文正文最终稿，只能写 Results 段落草案、caption 草案和边界文本草案。
不得改 CLAUDE.md、成果区或 Codex 文件。
```

## 6. 报告要求

012 报告保持简洁，只写：

```text
1. 输入包与表格是否齐全。
2. 统一后的 top-1 / controlled-envelope brightest / 两类机制。
3. 哪些 claim 可写，哪些必须禁写。
4. Fig.8 与 SI dataset 建议。
5. 是否 0 新增渲染、0 训练。
6. 红线自查。
```

不得复述 P4-PHYS-A/B/C/D/E/F 全部历史，只列必要路径与数值。
