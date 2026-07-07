# P4-PHYS-D sun/view 小矩阵扩展成果摘要（R154 通过）

最后更新：2026-07-06  
来源：

```text
02_Claude输出/009_P4PHYS_D_sunview_small_matrix_Claude执行报告.md
v0.4_results/26_three_axis_p4phys_d_sunview_small_matrix/
04_Codex审阅/R154_Codex_审阅_009通过_P4PHYSD小矩阵接收并放行P4PHYSE.md
```

## 1. 稳定结论

P4-PHYS-D 已完成 fixed `phase63/L1-G1` baseline 邻域的 `sun±7° / view±7°` 小矩阵检验。接收标签：

```text
SUNVIEW_DEPENDENT_BUT_MECHANISTIC
```

含义：

```text
最亮姿态随小幅 sun/view 几何变化迁移；
迁移目标仍落在 top-1 roll 邻域候选；
高亮仍由金属主体近镜面对齐探测器的连续机制解释。
```

## 2. 关键数值

5 个几何下的逐几何最亮候选：

| 几何 | 最亮姿态 | OCS | metal% | 严格 nsm |
|---|---|---:|---:|---:|
| G0 baseline | A_top1 | 0.20889049 | 95.02 | 1 |
| G1 sun+7° | D5_roll125 | 0.19528240 | 94.66 | 0 |
| G2 sun-7° | D6_roll175 | 0.19493062 | 94.78 | 0 |
| G3 view+7° | D6_roll175 | 0.20491531 | 94.86 | 1 |
| G4 view-7° | D5_roll125 | 0.18548740 | 94.64 | 0 |

原 baseline top-1 在扰动几何下仍是高亮候选，但不再逐几何最亮：

```text
G1/G2/G3/G4 rank = 7/4/4/6
```

全 70 个 `(几何, 姿态)` 组合均为金属主体主导：

```text
metal% = 92.71-99.26
```

## 3. 解释边界

可写：

```text
baseline 邻域小矩阵表明，最亮姿态对 sun/view 变化敏感，但高亮迁移仍保留金属主体近镜面对齐探测器的连续机制。
```

不可写：

```text
baseline top-1 是所有 sun/view 下的全局最亮；
strict near_specular_metal 二值标签在所有几何下稳定；
R4 在所有扰动几何下都满足二值同机制标签；
material-level attribution 已完成；
三轴小项目已经最终闭口。
```

R3 继续作为负面对照：5 个几何下均 `near_specular_metal=0` 且 rank=14；但 G1/G4 中绝对 OCS 上升到约 0.13，因此写作时只说“在本候选集内仍为最低/非近镜面对照”，不说“绝对黑暗”。

## 4. 下一步

R154 放行：

```text
P4-PHYS-E：sun/view 3×3 组合小网格补齐
```

下一步优先复用 26 包已有 camera/sun EXR，补齐 `sun_offset ∈ {-7,0,+7}` 与 `view_offset ∈ {-7,0,+7}` 的组合几何，不做全 sun/view 全姿态搜索。

