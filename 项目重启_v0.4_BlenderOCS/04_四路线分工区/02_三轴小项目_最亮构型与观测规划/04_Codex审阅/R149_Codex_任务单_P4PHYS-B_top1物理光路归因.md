# R149 Codex 任务单：P4-PHYS-B top-1 物理光路归因

最后更新：2026-07-06  
任务类型：给 Claude 的长程执行任务  
上游依据：R148 接收 006B / 23B，fixed phase63/L1-G1 top-1 局部闭口  
本轮目标：解释 fixed-geometry top-1 的入射-表面/材料-探测器光路  

## 1. 本轮目标

R148 已确认 fixed phase63/L1-G1 sun/view 下当前 top-1 为：

```text
yaw=245.0
pitch=27.5
roll=+15
ocs_total=0.2088904828
```

本轮 P4-PHYS-B 的目标是回答：

```text
这一个最亮姿态下，光从哪里入射，
主要照到卫星哪个部位、哪种材料/表面 proxy，
这些亮度贡献如何沿探测器方向被接收。
```

本轮只做 fixed-geometry top-1 物理光路归因和最小对照，不做完整机制普遍性统计，不扩展 sun/view。

## 2. 重要边界

必须写清：

```text
1. 本轮仍限定 phase63/L1-G1，SUN=[1,0,0.3]，DET=[0.5,-1,0.1]。
2. 结果不是所有 sun/view 几何的全局最亮光路解释。
3. material-level 若无 material pass，只能写作 material proxy 或 object/part-level attribution。
4. 不得把 EXR 通道可读性写成归因已经自动完成。
5. 不得启动 R128、路线二/三/四、训练或论文正文最终改写。
```

## 3. 输出位置

执行报告写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/007_P4PHYS_B_top1_light_path_attribution_Claude执行报告.md
```

新结果包写入：

```text
v0.4_results/24_three_axis_p4phys_b_light_path_attribution/
```

建议目录结构：

```text
audit/
tables/
figures/
text/
scripts/
logs/
```

不得改写 19/20/21/22/23A/23B 包。

## 4. 必读文件

按顺序读取：

```text
CLAUDE.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/00_路线冻结文件区/01_三轴小项目_最亮构型与观测规划指导文件.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/01_成果区/00_当前主用成果/05_三轴小项目最亮构型与光路解释技术路线_R144依据.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R144_Codex_技术路线_三轴小项目最亮构型与光路解释.md
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/04_Codex审阅/R148_Codex_审阅_006B通过_fixed几何top1闭口并放行P4PHYSB.md
```

必须读取 top-1 与对照表：

```text
v0.4_results/23B_three_axis_p4phys_pitch_boundary_followup/tables/p4physA2_final_top1_decision.csv
v0.4_results/23B_three_axis_p4phys_pitch_boundary_followup/tables/p4physA2_combined_topN_with_23A.csv
v0.4_results/23B_three_axis_p4phys_pitch_boundary_followup/audit/p4physA2_exr_channel_smoke.csv
v0.4_results/23A_three_axis_p4phys_top1_roll_confirmation/tables/p4physA_refined_topN.csv
v0.4_results/23A_three_axis_p4phys_top1_roll_confirmation/tables/p4physA_R4_robust_bright_roll_profile.csv
v0.4_results/21_three_axis_p3_local_refinement/tables/p3_local_refinement_metrics.csv
```

必须审计代码/配置：

```text
06_v0.4_code/00_config/config_v0_4.py
06_v0.4_code/00_config/materials_v0_4.py
06_v0.4_code/01_geometry/geometry_loader.py
06_v0.4_code/05_postprocess/ocs_integration_v0_4.py
```

需要读取/验证 EXR 的脚本可新建在 `24.../scripts/`。

## 5. 必须使用的姿态对象

### 5.1 top-1 主对象

必须使用真正的 fixed-geometry top-1：

```text
label = yaw2450_pitchp0275_roll+015
yaw=245.0, pitch=27.5, roll=+15
source = 23A_new / final top-1 after 23B closure
```

对应 EXR：

```text
v0.4_results/23A_three_axis_p4phys_top1_roll_confirmation/render/shadow_passes/phase63/roll+015/yaw2450_pitchp0275_roll+015_camera.exr
v0.4_results/23A_three_axis_p4phys_top1_roll_confirmation/render/shadow_passes/phase63/roll+015/yaw2450_pitchp0275_roll+015_sun.exr
```

不得误用 23B smoke 样本 `yaw2425_pitchp0225_roll+015` 作为 top-1。

### 5.2 最小对照

R4 鲁棒亮区代表：

```text
yaw=147.5, pitch=12.5, roll=0
label = yaw1475_pitchp0125_roll+000
作用：roll-robust high-brightness mechanism contrast
```

R3 负面对照：

```text
yaw=55.0, pitch=60.0, roll=0
label = yaw0550_pitchp0600_roll+000
作用：low-info / low-brightness 或负面对照
```

如 R3/R4 对应 EXR 位于 P3 或 fullrun，请只读定位，不改原包；若需要复制索引/路径清单，写入 24 包 audit。

## 6. 允许与禁止

允许：

```text
1. 新建 24 包脚本、表格、图、审计文件。
2. 读取 EXR 的 IndexOB、Normal、Position、Depth、Combined 通道。
3. 读取 *_ocs.json 的 ocs_total 和 ocs_per_part。
4. 计算 top-1、R4、R3 的 per-part 光度贡献。
5. 计算太阳入射方向、探测器方向、表面法向与视线/入射方向的角度 proxy。
6. 若 object/material 映射不足，明确写字段缺口和 proxy 级别。
```

禁止：

```text
1. 不训练。
2. 不启动 R128。
3. 不启动路线二/三/四。
4. 不扩展 sun/view。
5. 不做新姿态搜索。
6. 不做 P4-PHYS-C 机制普遍性完整统计。
7. 不改 19/20/21/22/23A/23B 包。
8. 不写成果区，不改 CLAUDE.md，不生成 Codex 审阅文件。
9. 不编造 material-level 归因；没有 material pass 时必须标注为 proxy。
```

## 7. 必做子任务

### A. 输入与通道审计

输出：

```text
audit/input_manifest.csv
audit/exr_path_manifest.csv
audit/exr_channel_availability.csv
audit/object_material_mapping_audit.csv
audit/redline_precheck.csv
```

必须回答：

```text
1. top-1/R4/R3 的 EXR 与 ocs.json 路径是否可定位。
2. top-1 的 IndexOB/Normal/Position/Depth 是否可读取。
3. object ID 到部件名是否可映射。
4. material 信息能否直接获取；若不能，当前只能到 part/material-proxy 级。
```

### B. top-1 光度贡献分解

输出：

```text
tables/p4physB_top1_ocs_per_part.csv
tables/p4physB_top1_pixel_contribution_summary.csv
figures/p4physB_top1_part_contribution.png
figures/p4physB_top1_part_contribution.pdf
text/p4physB_top1_brightness_source_summary.md
```

必须回答：

```text
1. top-1 的 ocs_total 是多少。
2. 哪个部件贡献最大。
3. 金属主体/太阳能板/隐身板等贡献比例是多少。
4. 贡献判断来自 ocs_per_part、IndexOB 像素积分，还是两者一致。
```

### C. 入射-表面-探测器几何分析

输出：

```text
tables/p4physB_top1_light_path_geometry.csv
tables/p4physB_top1_normal_angle_stats.csv
tables/p4physB_top1_detector_alignment.csv
figures/p4physB_top1_normal_view_sun_angle_hist.png
figures/p4physB_top1_normal_view_sun_angle_hist.pdf
text/p4physB_top1_light_path_explanation.md
```

必须计算或说明：

```text
1. 太阳入射方向在当前坐标口径中的向量。
2. 探测器视线方向在当前坐标口径中的向量。
3. 主贡献像素/部件的法向与太阳方向夹角 proxy。
4. 主贡献像素/部件的法向与探测器方向夹角 proxy。
5. 镜面反射方向与探测器方向是否接近；若公式或 BRDF 参数不足，只写 proxy。
6. 是否存在 saturation-associated 风险。
```

### D. R4 / R3 最小对照

输出：

```text
tables/p4physB_control_part_contribution.csv
tables/p4physB_control_light_path_geometry.csv
figures/p4physB_top1_vs_R4_R3_contribution_compare.png
figures/p4physB_top1_vs_R4_R3_contribution_compare.pdf
text/p4physB_R1_R4_R3_minimal_contrast.md
```

必须回答：

```text
1. R4 鲁棒亮区是否由同一主部件/相似角度 proxy 主导。
2. R3 负面对照为什么暗或低信息。
3. R1 top-1 与 R4 是否像同一机制，或应留给 P4-PHYS-C 做普遍性检验。
```

注意：本轮只做最小对照，不做 top-N 机制普遍性完整统计。

### E. P4-PHYS-C 接口

输出：

```text
tables/p4physB_mechanism_signature_seed.csv
text/p4physB_next_mechanism_generality_plan.md
```

必须给出一个机制签名 seed，例如：

```text
dominant_part
dominant_material_proxy
sun_normal_angle_bin
view_normal_angle_bin
reflection_alignment_proxy
saturation/glint state
```

并说明 P4-PHYS-C 应如何检验同类机制是否普遍高亮。

## 8. 验收与报告

必须输出：

```text
tables/p4physB_gate_matrix.csv
audit/generated_files_manifest.csv
audit/numeric_path_consistency_check.csv
audit/redline_self_check.csv
text/codex_review_checklist_for_007.md
```

报告写入：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/007_P4PHYS_B_top1_light_path_attribution_Claude执行报告.md
```

报告必须简洁回答：

```text
1. fixed-geometry top-1 是什么。
2. 使用了哪些 EXR/JSON 字段。
3. 主贡献部件/材料 proxy 是什么。
4. 光从哪里入射、主要照到哪里、如何朝探测器方向形成高亮。
5. R4/R3 最小对照说明了什么。
6. 哪些是直接计算，哪些只是 proxy。
7. 是否建议进入 P4-PHYS-C 机制普遍性检验。
```

## 9. 接收标准

最低接收：

```text
1. 24 包存在。
2. 007 报告存在。
3. top-1 的 EXR/JSON 路径正确，不误用 23B smoke 样本。
4. per-part 贡献清楚。
5. IndexOB/Normal/Position/Depth 读取链路可审计。
6. 光路解释明确区分 direct 与 proxy。
7. R4/R3 最小对照完成。
8. 未训练、未启动 R128、未扩展 sun/view、未写成果区或 CLAUDE.md。
```

强接收：

```text
1. top-1 主贡献部件与 ocs_per_part / IndexOB 像素归因一致。
2. 法向-太阳-探测器几何能给出清楚的高亮物理解释。
3. 给出可用于 P4-PHYS-C 的机制签名 seed。
4. 明确指出 material-level 归因是否需要新增 material pass。
```

