# P3 local refinement 指标定义

任务：R135 P3 local refinement
结果包：`v0.4_results/21_three_axis_p3_local_refinement/`
上游：R134 接收 P2 sparse grid（20 号包）

本轮在 P2 sparse 3-axis grid（5 度）基础上，对 primary 区域（R1/R4/R3）做 **2.5 度局部加密**；
R2/R5 仅保留少量 5 度对照点。所有指标口径与 P1/P2/路线一 C fullrun 一致，量纲可比。

## 1. 坐标与 label 编码

- 内部主键：deci-degree（度×10）整数。2.5 度 = 25 deci-degree。
- label 半度安全编码：`yaw{deci:04d}_pitch{p|m}{deci:04d}_roll{roll:+04d}`，
  例：`yaw2450_pitchp0300_roll+015`（yaw245.0, pitch+30.0, roll+15），
  `yaw1475_pitchp0125_roll-060`（yaw147.5, pitch+12.5, roll-60）。
- 整数 5 度点（yaw%50==0 且 pitch%50==0）额外保留 fullrun 兼容 label，用于 roll=0 复用定位。

## 2. 复用与新渲染

- 整数 5 度点、roll=0：复用 `01_fullrun`（不重渲）。
- 半度点 roll=0：fullrun 无此网格，**新渲染**（在 manifest 中 source=21_pack，不静默缺失）。
- 全部非零 roll：新渲染。
- 几何 phase63 / L1-G1：SUN=[1,0,0.3] DET=[0.5,-1,0.1]；r_max、i_scale、pixel_area、
  depth_epsilon 全部沿用 fullrun driver 默认值。

## 3. 基础指标（与 P1/P2 同口径）

| 指标 | 定义 |
|------|------|
| `ocs_total` | 单帧 OCS 总光度（后处理 `*_ocs.json`）。 |
| `brightness_rank` | 每个 roll 下 N=107 pose 按 ocs_total 的排名（1=最亮）。 |
| `pixel_local_contrast` | 单帧受照像素 std/mean（image-level）。 |
| `neighbor_contrast_ypr` | 三轴 (yaw±2.5, pitch±2.5, roll±1 档) 邻域内 OCS 的相对散布 (max-min)/mean。**P3 邻域步长 2.5 度**（P2 为 5 度）。 |
| `roll_sensitivity_score` | 固定 (yaw,pitch)，OCS 随 9 个 roll 的相对散布 (max-min)/mean。 |
| `rank_shift_vs_roll0` | 该 pose 在某 roll 下 brightness_rank 相对 roll=0 的漂移。 |
| `glint_flag` | 单帧 p99.9/median > 8.0 → 1。 |
| `saturation_flag` | 单帧 (>=0.98·max) 像素比例 > 0.01 → 1。 |
| `image_usable` | 受照像素 >= 50 → 1。 |

## 4. P3 特有稳定性指标（区域级，`p3_stability_assessment.csv`）

| 指标 | 定义 | 用途 |
|------|------|------|
| `local_peak_migration_deg` | 区域内 ocs_mean 最亮 pose 与该区域整数网格（近似 P2 峰）最亮点的欧氏距离（度）。 | 判断最亮点是否在 2.5 度加密下迁移。 |
| `local_information_stability` | 区域内 neighbor_contrast_ypr(pose 均值) 的 `1 - 变异系数(CV)`，越接近 1 越稳定。 | 判断高信息边界是否稳定可利用。 |
| `low_info_connectivity` | 区域内 neighbor_contrast_ypr 低于全局中位数的 pose 比例，越高越连通/成片。 | 判断低信息区是否连通（负面对照价值）。 |

## 5. 区域效用与 P4 规划效用

- `region_utility_score`（区域级，与 P2 同公式，便于跨阶段对比）：
  ```
  utility = 0.4·norm_info + 0.3·norm_rollsens + 0.3·norm_brightness − 0.2·risk_frac
  ```
  norm_* 基于全体 P3 pose 分布的 min-max 归一化；risk_frac = 触发 glint 或 saturation 的 pose 比例。

- `p4_planning_utility_score`（pose 级，P3 新增，供 P4 观测规划候选排序）：
  ```
  p4 = 0.35·norm_info + 0.25·norm_rollsens + 0.25·norm_brightness − 0.15·risk
  ```
  risk = any_glint or any_saturation。相比 region utility 更强调信息量，弱化风险惩罚，
  以便在 P4 中呈现亮-信息-roll敏感三者的折中候选。

## 6. 边界声明

- `neighbor_contrast_ypr` 仍是 **smoke/proxy 级**三轴局部信息指标（局部邻域 OCS 变化幅度），
  不是模型级信息量证明。P-DB / margin / entropy / conformal set_size / roll-aware neural model
  需单独阶段门，不在 P3 默认任务内启动。
- P3 为局部加密验证，不是三轴小项目最终结论，不构成真实未知目标姿态反演系统。
- 最亮构型不等于最优观测/反演姿态；brightness ≠ information 边界在 2.5 度加密下继续检验。
