# brightness 与 information 边界说明

最后更新：2026-07-01
来源：R129 子任务 B；实证数据来自 `figures/brightness_vs_information.png` 与 `logs/brightness_info_corr.txt`。

## 1. 核心命题

**最亮姿态 ≠ 高信息姿态。** 这是三轴小项目区别于"找最亮点"的关键。

## 2. 实证证据（fixed-roll 基线）

- `corr(log10 OCS brightness(phase63), G1->G5 OCS gain) ≈ -0.088`。
  亮度与多几何可救回性（gain）几乎无正相关，甚至略负。
- 说明：一个姿态很亮，并不意味着多几何观测能更好地反演它的 yaw；
  反过来，一些亮度中等的姿态反而有很高的 G1->G5 救回增益（high-info-seed）。
- glint_flag=1 的姿态共 3 个（亮度 ≥P99 且贡献像素 ≤P10）：亮度由少数高光像素主导，
  属"亮但不稳定"，标为 high-risk，不进入高信息候选。

## 3. 三类姿态的判定口径

| 类型 | 亮度 | 信息量 | 处置 |
|---|---|---|---|
| 高亮高信息 | 高 | 高（gain 正、entropy 低、margin 大） | 优先观测候选 |
| 高亮低信息 | 高 | 低（glint / 饱和 / 局部不稳定 / gain≈0） | 标 high-risk，不作最优反演姿态 |
| 低亮高信息 | 中低 | 高（local contrast 高、多几何救回强） | 高信息候选，值得投入 |
| 低亮低信息 | 低 | 低（ambiguous-flux、候选弥散大） | 低价值观测区 |

## 4. 写作红线

- 不得写"最亮姿态就是最优反演姿态"。
- 不得把 brightness 排名当作 information/可反演性排名。
- brightness 用于"能否被探测到、是否 glint 风险"；
  information 用于"探测到之后能否区分姿态"。二者在指标 registry 中分列
  （`info_class` 字段：brightness / information / consistency / risk / planning）。
