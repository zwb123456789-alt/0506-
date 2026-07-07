# 三轴采样计划（three_axis_sampling_plan）

最后更新：2026-07-01
来源：R129 子任务 D；矩阵见 `tables/three_axis_stage_matrix.csv`，估计见 `resources/render_train_storage_estimate.csv`。
基准来自 17 号 M-roll full-2664 实测渲染日志（约 1.0 s/姿态渲染+后处理，0.26 MB/姿态足迹）。

**本轮只设计，不执行 P1-P4。**

## 阶段总览

| 阶段 | 目标 | 姿态×几何×roll 规模 | 新渲染 | 新训练 | 渲染估计 | 存储估计 |
|---|---|---|---|---|---|---|
| P1 seed-roll scan | 种子点扫 roll，验证迁移 | 12 seed × 8 roll × 1 geom = 96 | 是(仅非零roll) | 否 | ~0.03 h | ~25 MB |
| P2 sparse 3-axis grid | 粗三轴网格 | 24yaw×13pitch×4roll×3geom = 3744 | 是 | 可选* | ~1.0 h | ~1.0 GB |
| P3 local refinement | 候选局部加密 | ~30候选×27邻域×8roll×5geom ≈ 32400 | 是 | 可选* | ~9.0 h | ~8.5 GB |
| P4 planning synthesis | utility map 汇总 | 不新增采样 | 否 | 否 | 0 | 0 |

\* roll-aware 训练必须另行 Codex 放行（C 类变更）。

## 各阶段接收 / 停止 / 扩展条件

### P1 seed-roll scan
- 姿态数：12 种子（从 66 中选类别代表）× roll{-60..+60 step15}，roll=0 复用。
- 几何：仅 phase63（L1-G1）做 smoke。
- 输出：每种子的 OCS magnitude(roll)、图像渲染可用性、local contrast、roll sensitivity 曲线。
- 最低接收：96 个非零 roll 渲染完成，OCS/图像非空，roll 迁移曲线可画。
- 停止/扩展：最亮点与可分点若在 roll 下不迁移 → 缩减 roll 范围；若显著迁移 → 进 P2 扩几何。

### P2 sparse 3-axis grid
- 稀疏 yaw(step15=24)×pitch(step15=13)×roll{-60..60 step30=4}×L1-G3。
- 输出：三轴高亮/高信息候选集初稿，utility map 粗图。
- 最低接收：三轴覆盖，候选集含高亮+高信息+低信息三类。
- 停止/扩展：候选集稳定 → P3；空间过大 → 改自适应/拉丁超立方采样。

### P3 local refinement
- 对最亮/高信息/低信息候选做邻域 step5-10° 加密，L1-G5。
- 输出：最亮构型 + 最优可观测姿态精定位。
- 最低接收：每类候选局部加密完成，定位收敛。
- 停止/扩展：收敛 → P4；不收敛 → 回 P2 补采样。

### P4 observation planning synthesis
- 汇总 P1-P3，不新增采样。
- 输出：observation planning utility map，值得/低价值/风险几何清单，路线二/三接口说明。
- 最低接收：utility map + 三类几何清单 + 接口说明。
- 停止/扩展：交 Codex 审阅是否作为三轴小项目成果。

## 红线
- P1-P4 均不在本轮执行；P1 需 Codex 放行 smoke 后再启动，正式 P1/P2/P3 各自另行放行。
- roll-aware 训练、split 变化、backbone/超参变化属 C 类，必须完整阶段门。
- 不把最亮姿态写成最优反演姿态；不把三轴计划写成真实反演系统。
