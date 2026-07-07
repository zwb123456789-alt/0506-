# P1 seed-roll smoke 说明（R132 通过，R138 后按最亮构型口径校正）

最后更新：2026-07-06  
来源审阅：`04_Codex审阅/R132_Codex_审阅_002通过_P1_seed_roll_smoke接收并放行P2_sparse_grid.md`  
结果包：`v0.4_results/19_three_axis_p1_seed_roll_scan/`

## 0. 最新最高口径

按 2026-07-06 修订后的三轴小项目冻结指导文件，P1 的作用是验证 roll 轴扫描链路是否能服务于最亮构型搜索：

```text
找出最亮 yaw/pitch/roll + sun/view 姿态-观测几何构型，
并解释光从哪里入射、照到卫星哪个部位/材料/表面、如何进入探测器。
```

P1 中“高信息/低信息/roll sensitivity”只作为辅助观察，不替代最亮构型主目标。

## 1. 稳定结论

P1 seed-roll smoke 已通过。96 个 phase63 / L1-G1 seed-roll 渲染单位与后处理全部完成，roll=0 baseline 复用 `01_fullrun`，三轴小项目的最小 roll 扫描链路已经跑通。

接收范围：

```text
12 seed × 8 非零 roll；
OCS total / roll 曲线 / roll sensitivity / rank shift / glint-saturation flag；
部分高亮 seed 在 roll 下较稳健但低对比、有饱和风险；
高 |pitch| 暗构型 roll 敏感；
brightness 与 information 在 smoke 层面继续解耦，但不改变“找最亮构型”主目标。
```

## 2. 关键观察

```text
bright-seed / robust-easy：OCS span_rel 约 5-7%，rank shift <= 1，但 local contrast 排名靠后。
high-info yaw240 系：roll_sensitivity_score 约 3.2-3.6。
low-info / ocs-hard yaw065 系：roll_sensitivity_score 约 1.5-1.6。
roll-sensitive / dark yaw285 系：roll_sensitivity_score 约 0.77-1.07。
```

这些观察只作为 smoke 级证据，不能写成三轴最终结论。

## 3. 下一步

R132 放行：

```text
P2 sparse 3-axis grid
```

限定：

```text
受控稀疏三轴网格；
不训练；
不启动 P3 local refinement；
不启动 R128；
输出 20 号包和 003 Claude 报告后再由 Codex 审阅。
```
