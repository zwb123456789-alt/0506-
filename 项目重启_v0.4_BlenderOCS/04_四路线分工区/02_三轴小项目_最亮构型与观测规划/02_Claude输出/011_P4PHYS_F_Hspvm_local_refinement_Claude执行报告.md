# 011_P4PHYS_F_Hspvm_local_refinement_Claude执行报告

生成时间：2026-07-06
执行依据：R157 任务单（P4-PHYS-F：Hsp_vm 角落局部姿态与几何加密）
结果包：`v0.4_results/28_three_axis_p4phys_f_hspvm_local_refinement/`
性质：Claude 执行报告，非裁决；建议标签与停机规则分析仅供 Codex/作者落判。

---

## 1. smoke 是否通过

通过。R3L_smoke（yaw=55, pitch=60, roll=+20）@ Hsp_vm 的 camera(view-7)/sun(sun+7) EXR 渲染成功，IndexOB/Normal/Position/Depth 通道可读，OCS 积分正常（OCS=0.029054，contributing=4670），无 failed。smoke 通过后才启动正式矩阵。

## 2. 新增渲染规模

**76 units ≤ 80 上限**：Stage B 52（26 新姿态 × camera+sun）+ Stage C 24（6 姿态 × cam_vm5/cam_vm9/sun_sp5/sun_sp9）。渲染脚本内置累计预算核验，日志 `logs/p4physF_*_render.log` 记录 cumulative=76。中心点 C_R3 与 5 个旧姿态的 sun+7/view-7 EXR 全部复用 26 包，未重渲。

## 3. Stage1：固定 Hsp_vm 姿态局部网格最高点

3×3×3 网格（yaw{35,55,75} × pitch{45,60,75} × roll{-20,0,+20}）27 姿态全部 COMPLETE。

**最高点：yaw=35, pitch=75, roll=-20，OCS=0.27080873**。
- 超过原 C_R3（0.22555675）**+20.1%**；超过 A_top1 baseline（0.20889048）**+29.6%**。
- 关键剖面：roll=0 平面上 C_R3 邻域平坦（y55/p45=0.22385，C_R3=0.22556，y55/p75=0.22570），真正的上升方向是 **(yaw↓, pitch↑, roll↓)** 斜对角；沿该方向 y35/p60/r-20=0.17062 → y35/p75/r-20=0.27081 陡升。
- C_R3 复用锚点：与 27 包 Hsp_vm 值 rel_diff=0（精确复现）。

## 4. Stage2：sun/view microgrid 最高点

6 姿态（C_R3 / Stage1_best / A_top1 / D5 / D6 / B_R4）× 9 几何（sun{+5,+7,+9} × view{-9,-7,-5}）54 组合全部 COMPLETE。

**全表最高：sp5_vm7 / Stage1_best（yaw35/pitch75/roll-20），OCS=0.27193961**。

## 5. 最高点是否在边界

**双边界均未闭合：**
- 姿态：Stage1 最高点在 yaw=35（下边界）、pitch=75（上边界）、roll=-20（下边界）三轴角落；
- 几何：Stage2 最高在 sun_offset=+5（microgrid 朝 baseline 方向的边缘），提示 sun 回向 baseline 可能继续上升。

按 R157 §5/§9：本轮不得收口，不自行扩大第二轮网格，交回 Codex。

## 6. 各对照姿态核心变化

| 姿态 | @sp7_vm7 (Hsp_vm) | microgrid 内变化 |
|---|---|---|
| Stage1_best (y35/p75/r-20) | 0.27081 | 峰值 0.27194 @ sp5_vm7；9 几何中 8 个仍为该几何下最高 |
| C_R3 (y55/p60/r0) | 0.22556（与 27 包精确一致） | 不再是任何几何下的最高点，降为次级对照 |
| A_top1 (y245/p27.5/r+15) | 与 27 包一致 | 在 microgrid 内保持中等亮度，未反超 |
| D5/D6（top-1 roll 邻域） | 与 27 包一致 | 未反超 |
| B_R4 | 与 27 包一致 | 保持鲁棒中亮对照 |

（完整数据见 `tables/p4physF_control_boundary_table.csv`）

## 7. 机制解释：近镜面还是宽瓣/几何因子

**金属宽瓣/几何因子高亮（metal wide-lobe / geometric-factor highlight），非严格近镜面：**
- 全表最高点：metal_pct=**99.5%**（金属主体绝对主导），nsm=**0**；
- avgN_vs_H=3.55°、reflect_vs_det=7.11°——接近但不满足严格 near_specular_metal 阈值（2°/4°）；
- R157 扩展诊断：weighted_NoL_NoV=**0.709**（对照 C_R3=0.707），weighted_NoL/NoV 均高——大面元同时正对太阳与探测器的几何因子增益叠加宽容差镜面瓣；
- 链路可信：79 组合逐像素重算 vs ocs.json 一致性 **79/79，max_rel=1.2e-07**；27 包 Hsp_vm 锚点 **5/5 rel_diff=0**。

按 R157 §7：写作口径为宽瓣/几何因子高亮，不得写成严格近镜面对齐，不得写真实 material-level attribution。

## 8. 建议标签（三选一）

**NEED_SECOND_STEP_REFINEMENT** —— 姿态与几何双边界未闭合；机制链未断裂（排除 MECHANISM_BREAK_OR_AUDIT_FAIL）；最高点在边界（排除 LOCAL_MAX_INTERNALIZED）。

**停机规则视角补充（供落判参考，非裁决）**：本轮是连续第二轮"加密后最高点仍在采样边界"（E 轮 3×3 角落 → F 轮姿态/几何双边界）。若采用 016 号工作流建议 1 的停机规则 c 条款（两轮加密仍现新边界即触发收口），本任务已满足触发条件，可按"**受控采样包络内局部最优 = yaw35/pitch75/roll-20 @ sp5_vm7，OCS≈0.2719，包络外沿 (yaw↓,pitch↑,roll↓,sun→baseline) 方向未检验**"表述收口搜索轴；宽瓣机制下高亮区呈脊状延伸，逐轮追角落没有自然终点，且三轴小项目的论文角色是机制解释章、不需要全局最优。备选路径 2（以新中心平移一轮 3×3×3，pitch 上限 90 有奇点风险）见 `text/p4physF_next_step_recommendation.md`。两条路径均由 Codex/作者裁决。

## 9. 红线自查

10/10 PASS（`audit/redline_self_check.csv`）：未训练；未启动 R128/路线二三四；仅 3×3×3 姿态网格 + 3×3 microgrid，非全搜索；76≤80；20/21/23A/23B/24/25/26/27 源包只读；未写成果区、未改 CLAUDE.md、未生成 Codex 名义文件；claim boundary 表明确禁止全局最亮与严格近镜面表述；边界情形未自行扩网格。

## 10. 交付物索引

```text
audit/    input_manifest / pose_local_grid_manifest / sunview_microgrid_manifest /
          render_plan_manifest / redline_precheck / stagec_poses.json /
          numeric_consistency_check / redline_self_check / generated_files_manifest(269 files)
render/   cam_vm7|sun_sp7（Stage B 52）+ cam_vm5|cam_vm9|sun_sp5|sun_sp9（Stage C 24）
postprocess/ 9 个几何目录 × ocs.json + v_sun_macro.npy
tables/   p4physF_smoke_metrics / stage1_pose_local_rank / stage1_best_summary /
          stage2_sunview_microgrid_rank / stage2_top_candidate_summary /
          mechanism_signature（含 weighted_NoL/NoV/NoL_NoV）/ control_boundary_table /
          gate_matrix / claim_boundary_table
figures/  p4physF_stage1_pose_slices.png/.pdf、p4physF_stage2_microgrid_heatmap.png/.pdf
text/     p4physF_result.md / p4physF_next_step_recommendation.md / codex_review_checklist_for_011.md
scripts/  p4physF_config / design_audit / render / postprocess / mechanism_analysis / finalize
logs/     smoke/stageB/stageC render 与 postprocess 日志
```
