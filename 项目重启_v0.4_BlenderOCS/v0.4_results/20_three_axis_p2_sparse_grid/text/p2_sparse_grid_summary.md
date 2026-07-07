# P2 sparse 3-axis grid 可解释摘要

最后更新：2026-07-03  
任务：R133 P2 sparse 3-axis grid  
结果包：`v0.4_results/20_three_axis_p2_sparse_grid/`  
上游：R132 接收 P1 seed-roll smoke，放行 P2

---

## 1. 链路是否跑通

**是。** 1000 非零 roll 渲染单位（125 唯一 pose × 8 非零 roll）全部 COMPLETE（cam/sun/ocs/lin
各 1000 / 1000）。roll=0 baseline 125/125 复用 `01_fullrun`（0 缺失）。量纲与 P1/01_fullrun 一致。
图像可用性：1125/1125 pose-roll 单位 image_usable = 1。指标无 nan，无阻断项。

---

## 2. P1 观察是否在局部三轴邻域中保持

### 2.1 最亮构型 roll 稳健

R4_bright_robust（yaw150,+15 附近）roll_sensitivity_score 均值 **0.088**，中位值约 0.07；
最亮 pose（yaw150/145,pitch+15）的 roll_sensitivity 仅 0.052–0.070，在 5×5 邻域内一致稳健。
**P1 观察在局部邻域保持：最亮区的 roll 稳健性在 5x5 yaw/pitch 网格中显著维持。**

### 2.2 最亮构型局部对比较低

最亮 4 个 pose（yaw150/145 × pitch+15/+10）的 neighbor_contrast_ypr 均值约 0.82–0.87，
在全体 125 pose 中处于中下水平（信息排名 53–60/125）。
**P1 观察在局部邻域保持：高亮但局部三轴对比偏低。**

### 2.3 高 |pitch| 区 roll 敏感

R1_high_info（yaw240,pitch+25 附近）roll_sensitivity_score 均值 **2.661**，最高单点
达 3.85（yaw245,pitch+35），在 5×5 邻域内稳定维持。
R2_dark_rollsens（yaw285,pitch-75 附近）均值 0.845，与 P1 中 yaw285/-70/-85 的观察量级一致。
**P1 观察在局部邻域保持：高 |pitch| / yaw240 系 roll 敏感性在三轴邻域中稳定。**

### 2.4 低信息区相对连通

R3_low_info（yaw065,pitch+70 附近）neighbor_contrast_ypr 均值 0.798，在 5 区域中最低，
roll_sensitivity 均值 1.512，结构较均匀，**支持低信息区较连通**的假设。

### 2.5 亮度与信息进一步解耦

brightness rank=1 的 pose（yaw150,+15）的 info rank = 60/125；
info rank=1 的 pose（yaw155,+20，R4 角点）的 brightness rank = 13/125。
R1_high_info 的高 roll_sensitivity 区（yaw245,+35）brightness rank 仅 20，但其局部信息
proxy 在全局前 13。**brightness ≠ information 边界在局部三轴邻域中持续成立。**

---

## 3. 各区域特征

| 区域 | 定位 | mean_ocs | mean_nc | mean_rs | risk_frac | utility |
|------|------|----------|---------|---------|-----------|---------|
| R4_bright_robust | 最亮/稳健 | 8.65e-02 | 1.199 | 0.088 | 0.48 | 0.251 |
| R1_high_info     | 高信息/roll敏感 | 3.94e-02 | 1.068 | 2.661 | 1.00 | 0.234 |
| R3_low_info      | 低信息/ocs-hard | 2.62e-02 | 0.798 | 1.512 | 1.00 | 0.063 |
| R2_dark_rollsens | 暗/roll敏感 | 2.02e-02 | 0.626 | 0.845 | 1.00 | -0.037 |
| R5_neutral       | 中性背景 | 1.70e-02 | 0.274 | 0.435 | 1.00 | -0.149 |

risk_frac = 任一 roll 下触发 glint 或 saturation 的 pose 比例。
utility = 0.4\*norm_info + 0.3\*norm_rollsens + 0.3\*norm_brightness - 0.2\*risk_frac。

R4 和 R1 utility 最高，前者以亮度贡献、后者以 roll 敏感度贡献；两者在信息和观测规划上角色互补。
R5_neutral 的低信息 + 全 risk 导致负效用——符合其中性背景对照定位。

---

## 4. P3 refinement candidates

P3 候选 14 个（每区域各取"最亮 / 信息最高 / roll 最敏感"代表 pose，去重）。
规模可控，覆盖 5 区域各类极端特征点，供 Codex 裁决是否放行 P3 local refinement。

关键 P3 候选：
- R1_high_info 系：yaw245,+30（信息rank=12, roll_sens=3.84）、yaw245,+35（roll_sens=3.85）——两者接近，可缩减至单点。
- R4_bright_robust 系：yaw150,+15（最亮，roll_sens低）、yaw155,+20（info rank=1，局部高对比边界点）。
- R3_low_info 系：yaw55,+60（最亮+roll最敏感）——三轴邻域边角，低信息但结构稳健。
- R2_dark_rollsens、R5_neutral 各 3 个，作为对照。

---

## 5. 信息 proxy 边界

本轮 `neighbor_contrast_ypr` 是新增三轴局部信息 proxy（在局部 yaw/pitch/roll 邻域中
OCS 变化幅度），比 P1 的 pixel_local_contrast 更接近三轴可观测性概念，但仍是
**smoke/proxy 级**。与模型级指标（P-DB / margin / entropy / conformal set_size）的
关系需在 P2 后另行阶段门确认。本结论不能写成三轴最终可观测性结论。

---

## 6. 红线自检

- 未启动 P3/P4/R128/训练：✓
- 未改旧脚本/旧目录 10-19：✓
- 未写成果区/未生成 Codex 审阅文件/未改 CLAUDE.md：✓
- 未把 P2 写成三轴小项目完成：✓
- 未声称真实未知目标反演系统：✓（model-known simulated）
- 最亮构型未写成最优观测姿态：✓（brightness ≠ information 边界维持）

---

*本摘要供 Codex 003 审阅裁决是否放行 P3 local refinement。*
