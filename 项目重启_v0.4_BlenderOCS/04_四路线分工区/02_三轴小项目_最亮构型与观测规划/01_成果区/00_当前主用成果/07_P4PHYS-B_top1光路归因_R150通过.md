# P4-PHYS-B top-1 光路归因（R150 通过）

最后更新：2026-07-06  
来源审阅：`04_Codex审阅/R150_Codex_审阅_007通过_P4PHYSB光路归因接收并放行P4PHYSC.md`  
结果包：

```text
v0.4_results/24_three_axis_p4phys_b_light_path_attribution/
```

## 1. 接收结论

R150 已接收 007 / 24 包。fixed `phase63/L1-G1` 下 top-1：

```text
yaw = 245.0
pitch = +27.5
roll = +15
ocs_total = 0.2088904828
```

其主高亮机制解释为：

```text
金属主体大面元近镜面对齐探测器，形成面状近饱和高亮。
```

关键证据：

```text
金属主体贡献约 95.0%；
金属贡献像素加权法向与半程向量夹角约 0.57°；
反射方向与探测器夹角约 1.06°；
N·H >= 0.99 的金属贡献像素占约 81.34%。
```

top-1 微弱超过 R4 的增量主要来自隐身板附加受照面：

```text
top-1 隐身板贡献 0.008775
R4 隐身板贡献    0.000931
差额 0.00784 ≈ top-1 - R4 总差 0.00774
```

## 2. 边界

该结论只表示：

```text
固定 phase63/L1-G1 sun/view 下，
已闭口 top-1 的光路机制得到解释。
```

不得写成：

```text
所有 sun/view 几何下的全局高亮机制；
高亮机制普遍性已经证明；
material-level attribution 已完成；
三轴小项目已经收口。
```

当前材料层仍为 `part/material proxy`，无 material pass。

## 3. 后续

R150 放行下一阶段：

```text
P4-PHYS-C 高亮机制普遍性检验
```

当前任务入口：

```text
04_Codex审阅/R151_Codex_任务单_P4PHYS-C_高亮机制普遍性检验.md
```

P4-PHYS-C 需要检验金属近镜面机制是否普遍对应高亮候选，以及隐身板增量是否只是 top-1 排序局部因素。

