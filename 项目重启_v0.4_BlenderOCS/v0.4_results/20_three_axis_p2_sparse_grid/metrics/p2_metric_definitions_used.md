# P2 sparse 3-axis grid 指标定义

最后更新：2026-07-03
任务：R133 P2 sparse 3-axis grid
结果包：`v0.4_results/20_three_axis_p2_sparse_grid/`

本文件记录 P2 子任务 C 实际使用的指标定义。所有量纲与 `01_fullrun` baseline
一致（phase63 / L1-G1，SUN=[1,0,0.3]，DET=[0.5,-1,0.1]，i_scale 与 pixel_area
沿用 fullrun）。roll=0 单位复用 `01_fullrun`，非零 roll 单位来自 20 号包。

这些指标是 model-known simulated 条件下的可观测性 proxy，不是真实未知目标反演
成功率，也不是最终概率校准。

## 单帧指标（每个 yaw/pitch/roll 单位）

- `ocs_total`
  单帧 OCS 总光度，直接取自后处理 `*_ocs.json` 的 `ocs_total`。单位与 fullrun 一致。

- `n_pixels_camera_visible` / `n_pixels_contributing`
  相机可见像素数 / 对 OCS 有贡献（受照且法向为正）像素数，取自 `*_ocs.json`。

- `pixel_local_contrast`
  单帧图像像素级对比：`std(I_lit) / mean(I_lit)`，其中 `I_lit` 为 linear.exr 中
  radiance > 0 的像素。与 P1 `local_contrast` 同口径。反映单帧内部结构对比，
  是最弱一级的 smoke 信息 proxy。

- `mean_lit`
  受照像素平均 radiance。

- `image_usable`（flag）
  受照像素数 >= 50 记 1，否则 0。判断该单帧是否具备最低图像可用性。

- `glint_flag`
  `percentile(I_lit,99.9) / median(I_lit) > 8.0` 记 1。高光/镜面 glint 风险。

- `saturation_flag`
  接近单帧最大值（>= 0.98 * max）的像素比例 > 1% 记 1。饱和风险。

## 亮度排名与漂移

- `brightness_rank`
  在**同一个 roll** 下，对 125 个 pose 按 `ocs_total` 降序排名（1 = 最亮）。
  每个 roll 独立排名。

- `rank_shift_vs_roll0`
  同一 pose 在某 roll 下的 `brightness_rank` 减去其 roll=0 时的 `brightness_rank`。
  正值表示该 roll 下相对变暗（排名下降），负值表示相对变亮。反映 roll 是否
  改变了 pose 之间的相对亮度序。

## 三轴邻域与 roll 敏感度

- `neighbor_contrast_ypr`
  三轴 (yaw, pitch, roll) 邻域内 OCS 的相对散布：`(max-min)/mean`，邻域取网格上
  相邻的 yaw±5 / pitch±5（限网格内存在的点）× roll 相邻档（当前 roll 及其相邻
  两档）。这是 P2 新增的**局部三轴信息 proxy**：在局部三轴邻域中 OCS 变化越大，
  说明该点对姿态扰动越敏感，携带的可观测信息越多。
  作为本轮首选信息 proxy（高于 pixel_local_contrast）。仍是 smoke/proxy 级，
  不等于 P-DB / margin / entropy 等模型级信息量指标（后者需模型，本轮未放行）。

- `roll_sensitivity_score`
  固定 (yaw, pitch)，OCS 随 9 个 roll 的相对散布：`(max-min)/mean`。反映纯 roll
  维度的敏感度。与 P1 `roll_sensitivity_score` 同口径（P1 为固定 seed 下的定义）。

## 区域级

- `mean_ocs` / `mean_neighbor_contrast` / `mean_roll_sensitivity`
  区域内所有 pose 对应 pose 级均值（pose 级均值先对 9 roll 取 nanmean）再对区域内
  pose 取 nanmean。

- `risk_frac`
  区域内触发 glint 或 saturation（在任一 roll 下）的 pose 比例。

- `usable_frac`
  区域内在所有 roll 下都 image_usable 的 pose 比例。

- `region_utility_score`
  区域综合效用，归一化后线性组合：
  ```
  utility = 0.4 * norm_info + 0.3 * norm_roll_sens + 0.3 * norm_brightness - 0.2 * risk_frac
  ```
  其中 `norm_*` 为对应区域均值在**全体 pose 分布**上做 min-max 归一化到 [0,1]。
  该权重强调局部三轴信息（0.4），兼顾 roll 敏感度与亮度（各 0.3），并对 glint/
  饱和风险做惩罚（-0.2）。这是一个供 P3 优先级排序的启发式，不是最终价值判定，
  权重可在 P3/P4 阶段门重新校准。

## 候选清单口径

- `p2_high_brightness_candidates`：按 pose `ocs_mean` 降序前 20。
- `p2_high_information_candidates`：按 pose `neighbor_contrast_mean` 降序前 20。
- `p2_low_information_regions`：按 pose `neighbor_contrast_mean` 升序前 20。
- `p2_p3_refinement_candidates`：每区域取最亮 / 信息最高 / roll 最敏感三类代表
  pose，去重合并（附 `p3_reason`）。规模受控，供 Codex 裁决是否放行 P3。

## 红线

- 以上全部为 model-known simulated 可观测性 proxy，不是真实反演成功率。
- `neighbor_contrast_ypr` 与 `pixel_local_contrast` 是 smoke/proxy 信息量，不等于
  P-DB / margin / entropy / conformal 等模型级指标。
- `region_utility_score` 是启发式排序，不是最终观测规划结论。
- 最亮构型不等于高信息构型；本轮延续该边界。
