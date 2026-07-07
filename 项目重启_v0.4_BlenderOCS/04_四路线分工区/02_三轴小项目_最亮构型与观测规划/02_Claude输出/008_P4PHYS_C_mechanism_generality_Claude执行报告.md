# 008 P4-PHYS-C 高亮机制普遍性检验 Claude 执行报告

任务依据：R151 任务单（P4-PHYS-C 高亮机制普遍性检验）
上游：R150 接收 007/24 包，top-1 金属近镜面主光路 + 隐身板小增量归因
执行日期：2026-07-06
输出包：`v0.4_results/25_three_axis_p4phys_c_mechanism_generality/`

---

## 0. 一句话结论

在 fixed phase63/L1-G1（SUN=[1,0,0.3], DET=[0.5,-1,0.1]）下，**金属主体近镜面对齐探测器**机制普遍对应高亮候选（top-10% 100% 满足、富集 ×6.36，满足组均亮度 0.2017 vs 未满足 0.0630）；但 top-1 相对 R4 的**隐身板增量绑定 R1 roll+15 亮簇、非普遍机制**。裁决 **PARTIAL_GENERALITY**。material 层仍为 B0 proxy。

## 1. 候选池规模与来源

- 复用既有 20/21/23A/23B + 01_fullrun（R3/R5 对照源），去重后 geometry-eligible=4353，分层采样 **n=159**（≤200）。
- 每候选三文件（camera EXR + v_sun_macro.npy + ocs.json）全部可定位（`audit/candidate_pool_manifest.csv`）；yaw/pitch/ocs_total 以 ocs.json 为准，roll 以 roll 目录名为准。
- 来源分布：P3=57、P2=46、01=32、23A=18、23B=6。
- region 覆盖：R1_top/R1_high_info/R1_pitch_boundary、R4_bright_robust/R4_bright_info_boundary、R3_low_info(_connectivity)、R2_dark_rollsens/R2_control、R5_neutral/R5_control 均含。
- force-include：top-1、R4、R3 均在池内。OCS 跨度 0.0106–0.2089（median 0.0344），覆盖高亮与低亮对照。

## 2. 机制签名如何定义

复用 24 包 `p4physB_light_path_attribution.py` 官方口径（read_normal/indexob/position/depth、get_material_b0/brdf_b0_phong_like、I_linear=f_r·NoL·V_sun、OCS=pixel_area·ΣI_linear、HSPEC=(S+D)/|S+D|）。每候选算 per-part OCS/占比、金属贡献像素 I 加权代表法向的 avgN_vs_H/sun/det、reflect_vs_det、weighted_NoH、pct_NoH≥0.99、mean_NoH^80。逐像素重算与 ocs.json 一致，**max rel_diff=1.5e-7**（`audit/numeric_consistency_sample_check.csv`）。

三判据（阈值取候选池分布 p25/p75 自然断层，非 top-1 定制，见 `text/p4physC_mechanism_rule_definition.md`）：
- `near_specular_metal` = metal_pct≥80 且 avgN_vs_H≤2° 且 reflect_vs_det≤4°。
- `strong_surface_highlight` = pct_NoH≥0.99 ≥50% 或 mean_NoH^80 ≥0.5。
- `dark_panel_increment` = dark_contrib≥0.004 或 dark_pct≥2%。

## 3. 近镜面金属机制是否普遍对应高亮

**是。** base rate 15.7%（25/159），但 top-10% 全 16 个满足（×6.36），top-25% 60% 满足（×3.82）。满足组 mean OCS 0.2017、未满足 0.0630（3.2 倍）。相关性 corr(OCS, reflect_vs_det)=−0.80、corr(OCS, pct_NoH≥0.99)=+0.95。不满足机制的候选系统性更暗。（`tables/p4physC_top_quantile_enrichment.csv`、`p4physC_brightness_by_mechanism.csv`）

## 4. 隐身板增量是普遍还是只解释 top-1 超 R4 的排序

**只解释排序，且该增量是 R1 roll+15 亮簇的共同特征，不是 top-1 独有、也不普遍到全部高亮。** 高亮候选（OCS≥0.18, n=49）中 roll+15 子组隐身板 mean 0.00839、95.7% 满足 dark_panel_increment；top-1 隐身板 0.00877≈roll+15 亮簇 median 0.00873。R4（roll=0）仅 0.00093——R4 是高亮候选里**缺**隐身板受照面的一方，故“top-1>R4”写成**排序增量**而非独立机制。（`tables/p4physC_dark_panel_increment_test.csv`）

## 5. R4 / R3 在机制统计中的角色

- R4：`near_specular_metal=1`，与 top-1 同高亮机制簇（镜面对齐略优），但缺隐身板增量——正是 top-1 排序超它的原因。
- R3：`near_specular_metal=0`，镜面几何破坏（reflect_vs_det≈47°），落在暗组，作为负锚点验证机制与亮度的分离。

## 6. 哪些 direct、哪些 proxy

- direct：per-part OCS、贡献像素、法向/半程向量/反射-探测器夹角、NoH 分布、IndexOB→部件（逐像素与 ocs.json 一致 rel_diff<1e-4）。
- proxy：material 层（B0 参数级，无 material pass）；avgN 为亮度加权代表面朝向；near-specular 为几何 proxy。

## 7. 是否建议进入 sun/view 扩展或补 material pass

建议按 PARTIAL_GENERALITY 放行 **P4-PHYS-D sun/view 扩展阶段门**（独立门，本轮不启动）；**material pass 列为可选增强**（隐身板增量的真实 material 归因需 material pass，本轮不自行启动）。不建议回退补池（n=159 已充分分离机制与暗组）。详见 `text/p4physC_next_step_recommendation.md`。

---

## 附：产物清单（详见 `audit/generated_files_manifest.csv`，共 32 个文件）

- scripts/：build_pool、mechanism_signature、generality_analysis（3）。
- audit/：input_manifest、candidate_pool_manifest、exr_json_availability、redline_precheck、numeric_consistency_sample_check、redline_self_check、generated_files_manifest（7）。
- tables/：candidate_pool、mechanism_signature_table、part_contribution_table、geometry_signature_table、mechanism_rule_table、candidate_mechanism_labels、brightness_by_mechanism、top_quantile_enrichment、dark_panel_increment_test、claim_boundary_table、gate_matrix（11）。
- figures/：ocs_vs_reflection_alignment、mechanism_enrichment_bar（各 png+pdf，4）。
- text/：mechanism_rule_definition、mechanism_generality_result、what_can_be_claimed、next_step_recommendation、codex_review_checklist_for_008（5）。
- logs/：build_pool_log、signature_log、analysis_log（3）。

红线自检全 PASS（`audit/redline_self_check.csv`）：不训练、不新增渲染、不扩展 sun/view、不搜新姿态、不改源包、不写成果区/CLAUDE.md、不生成 Codex 文件、固定几何不写成全局、material 仅 proxy。
