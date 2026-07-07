# 007 (P4-PHYS-B) Codex 审阅检查清单

供 Codex 审阅 007 报告与 24 包时逐项核对。

## 最低接收项（R149 §9）
- [ ] 24 包存在：`v0.4_results/24_three_axis_p4phys_b_light_path_attribution/`（audit/tables/figures/text/scripts/logs）。
- [ ] 007 报告存在：`02_Claude输出/007_P4PHYS_B_top1_light_path_attribution_Claude执行报告.md`。
- [ ] top-1 路径正确：使用 23A `yaw2450_pitchp0275_roll+015_camera.exr`，未误用 23B smoke `yaw2425_pitchp0225_roll+015`。见 `audit/exr_path_manifest.csv`。
- [ ] per-part 贡献清楚：金属 95.0% / 隐身 4.2% / 太阳能 0.8%。见 `tables/p4physB_top1_ocs_per_part.csv`。
- [ ] IndexOB/Normal/Position/Depth 读取链路可审计：`audit/exr_channel_availability.csv`（三姿态各 8 通道 readable=YES）。
- [ ] 光路解释区分 direct 与 proxy：见 `text/p4physB_top1_light_path_explanation.md §5`。
- [ ] R4/R3 最小对照完成：`text/p4physB_R1_R4_R3_minimal_contrast.md` + 对照表 + 对比图。
- [ ] 未训练/未启 R128/未扩展 sun/view/未写成果区或 CLAUDE.md：`audit/redline_self_check.csv` 全 PASS。

## 强接收项
- [ ] top-1 主贡献部件与 ocs_per_part / IndexOB 像素归因一致：`audit/numeric_path_consistency_check.csv` rel_diff<1e-4。
- [ ] 法向-太阳-探测器几何给出清楚高亮物理解释：加权金属法向 vs 半程向量 0.57°、反射-探测器 1.06°、N·H≥0.99 占 81%。
- [ ] 机制签名 seed：`tables/p4physB_mechanism_signature_seed.csv`。
- [ ] material-level 归因是否需新增 material pass：报告明确"需要"（当前仅 proxy）。

## 关键数字复核锚点
- top-1 ocs_total = 0.20889048278（23A ocs.json；重算 rel_diff=5.5e-8）。
- top-1 − R4 差 0.00774 ≈ 隐身板贡献差 0.00784（增量来源结论）。
- R3 反射-探测器夹角 21.8°、(N·H)^80 均值 0.11 → 负面对照成立。

## 审阅关注点（待 Codex 裁决）
1. "隐身板附加受照面是 top-1 超过 R4 的决定性增量"这一结论是否接受为 P4-PHYS-B 级（仅最小对照），或要求 P4-PHYS-C 复核。
2. 是否放行 P4-PHYS-C 机制普遍性检验（本轮仅给 seed + 计划）。
3. material pass 是否列为 P4-PHYS-C 前置。
