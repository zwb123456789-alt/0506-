# P4-PHYS-E sun/view 3×3 组合小网格：R156 通过但需局部加密

最后更新：2026-07-06  
来源：010 Claude 执行报告与 27 号结果包  
Codex 审阅：`R156_Codex_审阅_010通过_NEED_LOCAL_STEP_REFINEMENT并放行P4PHYSF.md`  
状态：已接收为稳定诊断成果；不得作为三轴小项目收口结论  

## 稳定结论

P4-PHYS-E 补齐了 `sun_offset ∈ {-7,0,+7}` 与 `view_offset ∈ {-7,0,+7}` 的 3×3 组合小网格，复用 26 包已有 camera/sun EXR，0 新增渲染。9 个组合几何 × 14 个固定姿态 = 126 组合全部完成；H00 / pure sun / pure view 共 70 个锚点与 26 包 G0-G4 精确一致，机制重算 126/126 通过。

本轮裁决标签为：

```text
NEED_LOCAL_STEP_REFINEMENT
```

原因是全 126 组合的最高 OCS 出现在组合角落：

```text
Hsp_vm(sun+7, view-7) / C_R3
OCS = 0.22555675
metal% = 99.51
near_specular_metal = 0
```

该值超过 baseline `A_top1`：

```text
H00_baseline / A_top1
OCS = 0.20889048
```

## 可引用事实

逐几何最亮点中 8/9 仍落在 top-1 roll 邻域簇，说明 R154 的 pure sun / pure view 迁移规律并非完全失效；但 `Hsp_vm` 角落由原负对照 `C_R3` 领先，打破了“最高点总在 A_top1 / D5 / D6 邻域”的收口条件。

全 126 组合仍由金属主体主导：

```text
dominant_part = 金属主体：126/126
metal% 范围：87.6–99.51
near_specular_metal = 29/126
```

因此应写成：金属主导在该局部组合网格内稳定，但严格近镜面对齐只在 baseline / 同号扰动附近成立；反对角组合中可出现非近镜面的金属宽瓣/几何因子高亮。

## 不能写成

```text
三轴小项目已经完成
baseline A_top1 是 sun/view 组合小网格最高点
top-1 roll 邻域跨所有 sun/view 组合稳定保持最亮
R3 是跨组合几何稳定负对照
严格 near_specular_metal 在所有组合中稳定
全 sun/view 全局规律
真实材料层归因
真实未知目标三轴姿态反演系统
```

## 下一步

按 R156 裁决，下一步进入 R157 / P4-PHYS-F：只围绕 `Hsp_vm(sun+7, view-7)` 角落做受控局部姿态与小几何加密，判定 `C_R3` 领先是真局部峰、采样边界效应，还是需要继续二级 refinement。
