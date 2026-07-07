# P4-PHYS-C 机制普遍性检验（R152 通过）

最后更新：2026-07-06  
来源审阅：`04_Codex审阅/R152_Codex_审阅_008通过_PARTIAL_GENERALITY并放行P4PHYSD.md`  
结果包：

```text
v0.4_results/25_three_axis_p4phys_c_mechanism_generality/
```

## 1. 接收结论

R152 已接收 008 / 25 包。fixed `phase63/L1-G1` 下的机制普遍性裁决为：

```text
PARTIAL_GENERALITY
```

可稳定使用的结论：

```text
金属主体近镜面对齐探测器是 fixed phase63/L1-G1 下高亮候选的普遍机制。
```

关键证据：

```text
near_specular_metal base rate = 15.7%
top 10% 候选 16/16 满足，富集 ×6.36
top 25% 候选 24/40 满足，富集 ×3.82
满足组 mean OCS = 0.201656
未满足组 mean OCS = 0.063034
```

隐身板增量结论：

```text
不是普遍高亮机制；
是 R1 roll+15 亮簇伴随特征；
主要解释 top-1 相对 R4 的排序增量。
```

## 2. 边界

不得写成：

```text
所有 sun/view 几何下的全局高亮机制；
所有不满足 near_specular_metal 的姿态都暗；
隐身板增量是普遍高亮机制；
material-level attribution 已完成；
三轴小项目已经最终闭口。
```

正确表述是：

```text
金属近镜面对齐机制在固定几何下的高亮 top 分位强富集，并使候选总体显著更亮。
```

## 3. 后续

R152 放行下一阶段：

```text
P4-PHYS-D sun/view 小矩阵扩展阶段门
```

当前任务入口：

```text
04_Codex审阅/R153_Codex_任务单_P4PHYS-D_sunview小矩阵扩展阶段门.md
```

material pass 不作为 P4-PHYS-D 前置，仅保留为后续材料级 claim 的可选增强。

