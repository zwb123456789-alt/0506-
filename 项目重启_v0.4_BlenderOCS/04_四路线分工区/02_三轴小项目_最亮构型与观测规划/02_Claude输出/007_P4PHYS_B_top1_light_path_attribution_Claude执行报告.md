# 007 P4-PHYS-B top-1 物理光路归因 Claude 执行报告

任务依据：R149 任务单（P4-PHYS-B top-1 物理光路归因）
上游：R148 接收 006B/23B，fixed phase63/L1-G1 top-1 局部闭口
执行日期：2026-07-06
输出包：`v0.4_results/24_three_axis_p4phys_b_light_path_attribution/`

---

## 0. 一句话结论

固定 phase63/L1-G1 几何下的 top-1（yaw=245, pitch=27.5, roll=+15, OCS=0.20889）是一处**金属主体大面元近镜面对齐探测器**的面状近饱和高亮；它之所以微弱超过 roll-robust 的 R4，是因为 roll=+15 让**隐身板一片附加受照面**进入贡献，提供了决定性的小增量。该结论仅限当前固定几何与局部加密范围，material 层为 proxy。

## 1. fixed-geometry top-1 是什么

- 姿态：yaw=245.0, pitch=27.5, roll=+15（23A_new，23A+23B 合并后 top-1，未被 23B 追加点超过）。
- OCS：ocs_total = 0.20889048278（与 23A ocs.json 一致，逐像素重算相对误差 5.5e-8）。
- 固定几何：phase63/L1-G1，SUN=[1,0,0.3]、DET=[0.5,-1,0.1]（惯性系，三姿态共用）。
- **未误用** 23B smoke 样本 yaw2425_pitchp0225_roll+015（见 `audit/exr_path_manifest.csv`）。

## 2. 使用了哪些 EXR/JSON 字段

- camera EXR：`ViewLayer.IndexOB.X`（部件 ID 1/2/3，0=背景）、`Normal.X/Y/Z`（world-frame 法向）、`Position.X/Y/Z`、`Depth.Z`。三姿态各 8 通道 readable=YES（`audit/exr_channel_availability.csv`）。
- postprocess：`*_v_sun_macro.npy`（复用官方 shadow mask，精确复现 ocs.json，避免 epsilon 依赖）。
- `*_ocs.json`：ocs_total 与 ocs_per_part 作为一致性基准。
- 官方口径复用 `06_v0.4_code`：read_exr_channel/normal/indexob、get_material_b0/brdf_b0_phong_like、I_linear=f_r·NoL·V_sun、OCS=pixel_area·ΣI_linear。

## 3. 主贡献部件/材料 proxy

| 部件 | OCS(m²) | 占比 | 贡献像素 |
|---|---|---|---|
| 金属主体 | 0.198497 | **95.0%** | 2653 |
| 隐身板 | 0.008775 | 4.2% | 1408 |
| 太阳能板 | 0.001619 | 0.8% | 80 |

- 主贡献部件 = **金属主体**（直接：ocs_per_part 与 IndexOB 逐像素重算一致）。
- 材料 proxy = B0 金属高镜面（rho_s=0.60, Phong n=80）；**无 material pass，材料层只能到 proxy**。

## 4. 光从哪里入射、照到哪里、如何朝探测器高亮

- 入射 S=[0.958,0,0.287]，观测 D=[0.445,-0.891,0.089]，半程向量 H=[0.779,-0.581,0.236]，相位角≈63°。
- 金属贡献像素按 I_linear 加权平均法向 N̄：与 S 夹角 31°、与 D 夹角 32°、**与 H 仅 0.57°**、N·H=0.998。
- 理想反射方向 R 与探测器 D **仅差 1.06°**；金属贡献像素 **81%** 满足 N·H≥0.99；(N·H)^80 均值 0.81。
- 光路：太阳入射→金属主体一片法向≈H 的大面元（入射角~31°）→高镜面材料在近镜面条件产生强镜面瓣→反射方向几乎正对探测器→面状近饱和高亮（saturation_flag=1, glint_flag=0，面状而非离散 glint）。
- 达到 50% OCS 需 1153 像素（占贡献像素 27.8%）→ 一片面主导，非单点尖峰。

## 5. R4 / R3 最小对照说明了什么

| 对象 | OCS | 金属占比 | N̄·H角 | 反射-探测器角 | (N·H)^80 |
|---|---|---|---|---|---|
| R1 top-1 | 0.20889 | 95.0% | 0.57° | 1.06° | 0.81 |
| R4 鲁棒亮区 | 0.20115 | 98.8% | 0.19° | 0.33° | 0.84 |
| R3 负面 | 0.06626 | 98.5% | 12.45° | 21.78° | 0.11 |

- **R4 与 top-1 同一机制**：都是金属主体近镜面对齐探测器（R4 对齐甚至略优）。
- **top-1 超过 R4 的原因不在金属**（金属 0.19850 ≈ 0.19872，几乎相等），而在**隐身板**：top-1 隐身板 0.008775 vs R4 0.000931，差额 0.00784 ≈ top-1−R4 总差 0.00774。
- **R3 暗**：镜面几何被破坏（N̄ 偏 H 12.5°、反射偏探测器 21.8°、镜面项弱约 8 倍），只剩漫反射底座。

## 6. 哪些是直接计算，哪些是 proxy

- 直接：per-part OCS、贡献像素数、I_linear 分布、S/D/H 向量、逐像素与加权法向夹角、N·H 分布、反射方向-探测器夹角、IndexOB→部件映射。
- proxy：材料层（B0 参数级，无 material pass）；N̄ 为亮度加权代表面朝向；"近镜面/准 glint"为几何 proxy，未做 BRDF 分量能量解析。

## 7. 是否建议进入 P4-PHYS-C

**建议进入 P4-PHYS-C 机制普遍性检验**，本轮已给机制签名 seed（`tables/p4physB_mechanism_signature_seed.csv`）与检验计划（`text/p4physB_next_mechanism_generality_plan.md`）。两点需 Codex 裁决：
1. "隐身板附加受照面为 top-1 超 R4 的决定性增量"是否需 P4-PHYS-C 复核；
2. material pass 是否列为 P4-PHYS-C 前置（当前材料级仅 proxy）。

本轮严格不做：新训练、R128、路线二/三/四、sun/view 扩展、新姿态搜索、机制普遍性完整统计、成果区写入、CLAUDE.md 修改（`audit/redline_self_check.csv` 全 PASS）。

---

## 附：产物清单（详见 audit/generated_files_manifest.csv）

- tables/：ocs_per_part、pixel_contribution_summary、light_path_geometry、normal_angle_stats、detector_alignment、control_part_contribution、control_light_path_geometry、mechanism_signature_seed、gate_matrix（9 个 csv）。
- figures/：part_contribution、normal_view_sun_angle_hist、top1_vs_R4_R3_contribution_compare、I_linear_maps（各 png+pdf）。
- text/：brightness_source_summary、light_path_explanation、R1_R4_R3_minimal_contrast、next_mechanism_generality_plan、codex_review_checklist_for_007。
- audit/：input_manifest、exr_path_manifest、exr_channel_availability、object_material_mapping_audit、redline_precheck、numeric_path_consistency_check、redline_self_check、generated_files_manifest。
- scripts/：p4physB_light_path_attribution.py、p4physB_make_figures.py、p4physB_finalize_audit.py。
- logs/：p4physB_run_log.json。
