# 算力/渲染风险登记（compute_risk_register）

最后更新：2026-07-01
来源：R129 子任务 D。配合 `resources/render_train_storage_estimate.csv`。

## 风险项

| 风险 | 阶段 | 描述 | 缓解 |
|---|---|---|---|
| 三轴空间爆炸 | P2/P3 | 全三轴 72yaw×37pitch×N_roll×5geom 会到千万级，不可行 | 从种子出发，稀疏采样 + 局部加密，绝不全量爆扫 |
| P3 存储膨胀 | P3 | 上界估计 ~32400 渲染单位、~8.5 GB shadow_passes | 只对候选邻域加密；及时清理中间 pass，仅留 OCS json + 关键 EXR |
| 渲染速率漂移 | 全部 | 1.0 s/姿态为含 skip 的摊薄值，复杂几何可能更慢 | 每阶段先 smoke 计时，再外推；分批 --start-index/--count |
| roll-aware 训练未放行 | P2/P3 | roll 标签训练属 C 类变更，不能自行启动 | 训练列为"可选*"，必须另行 Codex 放行 |
| 数据泄漏 / split 污染 | P2/P3 若训练 | roll 扩展改变样本分布，可能破坏原 split | 保持原 yaw/pitch split 定义；roll 作为新增维度独立登记 |
| 中文/空格路径 | 全部 | 命令行路径含中文，未加引号会失败 | 所有命令路径加英文双引号（见 CLAUDE.md 1.1） |
| Blender/python 环境错配 | 全部 | 默认 blender/python 不可用 | 固定用 Blender 4.2 与 ocs_sim python 绝对路径 |

## 关键基准（实测）

- 来源：`17_.../logs/mroll_full2664_render.log`，phase63 四个 roll 档全量。
- 时间窗：16:58:33 → 18:55:43 ≈ 117 min，约 9376 张实渲（另有 skip）。
- 推算：≈ 0.75 s/张，取保守 1.0 s/张用于估计。
- 单几何单 roll 全量 shadow_passes ≈ 698 MB / 2664 姿态 ≈ 0.26 MB/姿态。

## 结论

- P1 seed-roll scan 极轻量（96 单位、~2 min、~25 MB），适合作为首个放行 smoke。
- P2 中等（~1 h、~1 GB），P3 最重（~9 h、~8.5 GB），均需分阶段放行并先 smoke 计时。
- 本轮不执行任何渲染/训练。
