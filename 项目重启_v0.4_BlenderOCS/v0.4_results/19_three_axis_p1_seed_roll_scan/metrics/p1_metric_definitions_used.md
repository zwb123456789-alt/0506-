# P1 seed-roll scan smoke —— 指标定义（p1_metric_definitions_used）

最后更新：2026-07-01
性质：R131 P1 smoke 实际使用的指标定义与计算口径。仅 smoke 级，不是三轴小项目最终指标体系。

## 几何与量纲

- 几何：phase63 / L1-G1，SUN=[1,0,0.3]，DET=[0.5,-1,0.1]，与 `01_fullrun` 一致。
- 不变量沿用 fullrun：`r_max=1.472605`，`i_scale`（来自 Step5），`pixel_area_m2`，`depth_epsilon_m_final`。
- roll=0 baseline 直接复用 `01_fullrun/postprocess`，不重渲。
- 因此 roll≠0 与 roll=0 的 OCS/图像量纲可比。

## 指标口径

- `ocs_total`：`*_ocs.json` 中 `ocs_total`，跨可见/受照像素积分的光度截面（OCS magnitude）。
- `delta_ocs_vs_roll0`：`ocs_total(roll) - ocs_total(roll=0)`（同一 seed）。
- `rel_delta_pct`：`delta / ocs_total(roll=0) × 100%`。
- `brightness_rank`：某 roll 下 12 个 seed 按 `ocs_total` 降序排名（1=最亮）。
- `rank_shift_vs_roll0`：`brightness_rank(roll) - brightness_rank(roll=0)`，衡量最亮构型是否随 roll 迁移。
- `local_contrast`：受照像素（linear.exr R 通道 > 0）辐亮度的 `std/mean`，作为 smoke 级“姿态邻域可区分性 / 图像信息量”代理。**不是**最终 information 指标。
- `mean_lit`：受照像素平均线性辐亮度。
- `image_usable`：受照像素数 ≥ 50 记为 1（图像非空、可用）。
- `glint_flag`：受照像素 `p99.9 / median > 8` 记为 1（高光尖峰 / glint 风险）。
- `saturation_flag`：受照像素中 `≥ 0.98×max` 占比 `> 1%` 记为 1（亮但可能饱和风险）。
- `ocs_span_rel` = `roll_sensitivity_score`：`(max−min)/mean`，对某 seed 在全部 9 个 roll（含 0）上的 `ocs_total`。越大越 roll 敏感。
- `ocs_std_rel`：同集合的 `std/mean`。
- `max_abs_rank_shift`：某 seed 在全部 roll 上相对 roll=0 的最大亮度排名漂移。

## 判据口径（smoke 级，仅观察不下结论）

- bright seed 是否随 roll 保持高亮 / 最亮点是否迁移：看 `brightness_rank` 与 `rank_shift_vs_roll0`。
- high-info / low-info 的 roll 曲线是否与 brightness 解耦：看 `p1_brightness_information_smoke.csv` 的 `brightness_info_decoupled`。
- roll-sensitive seed 是否变化更大：看 `ocs_span_rel`。
- dark seed 是否持续低信号或出现 roll-induced brightening：看 `ocs_total` by roll 曲线。
- robust-easy seed 是否稳定：看 `ocs_span_rel` 与 `max_abs_rank_shift` 是否最小。

## 红线

- `local_contrast` 只是 smoke 级 information proxy，不得写成正式可观测信息量或反演可分性。
- 本轮不训练、不计算 P-DB/conformal/margin/entropy 等需模型的量。
- 不把最亮姿态写成最优反演姿态；brightness 与 information 分列。
