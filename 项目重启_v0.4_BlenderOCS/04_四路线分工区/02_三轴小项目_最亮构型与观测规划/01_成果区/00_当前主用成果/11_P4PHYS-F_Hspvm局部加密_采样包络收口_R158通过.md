# P4-PHYS-F Hsp_vm 局部加密：R158 通过并按采样包络收口

最后更新：2026-07-06  
来源：011 Claude 执行报告与 28 号结果包  
Codex 审阅：`R158_Codex_审阅_011通过_P4PHYSF采样包络收口并停止追角落.md`  
状态：已接收为稳定成果；不再继续追角落加密  

## 稳定结论

P4-PHYS-F 对 R156 暴露的 `Hsp_vm(sun+7, view-7) / C_R3` 角落进行受控局部加密。结果显示，最高点并非 C_R3 的微调，而是沿 `yaw↓ / pitch↑ / roll↓` 方向移动到姿态网格角落，并在 sun/view microgrid 中进一步落在几何边界。

Codex 裁决：

```text
CONTROLLED_ENVELOPE_LOCAL_OPTIMUM_STOP
```

本项目受控采样包络内的最高亮构型为：

```text
yaw = 35 deg
pitch = 75 deg
roll = -20 deg
geometry = sp5_vm7(sun+5 deg, view-7 deg)
OCS = 0.27193961
```

边界说明必须同时保留：

```text
包络外沿 yaw↓ / pitch↑ / roll↓ / sun→baseline 方向未检验；
该构型不是全局 sun/view/pose 空间最亮结论。
```

## 机制口径

最高点由金属主体宽瓣响应与几何因子共同解释：

```text
dominant_part = 金属主体
metal_pct = 99.48%
weighted_NoL_NoV = 0.7090
avgN_vs_H = 3.554 deg
reflect_vs_det = 7.105 deg
near_specular_metal = 0
```

可写成：

```text
金属宽瓣/几何因子高亮
```

不可写成：

```text
严格近镜面对齐
真实材料级归因
全局最亮搜索完成
```

## 证据链状态

```text
新增渲染：76 units ≤ 80
Stage1：27/27 COMPLETE
Stage2：54/54 COMPLETE
数值一致性：79/79 OK，max_rel_diff = 1.196e-7
27 包锚点一致性：5/5 rel_diff=0
红线自查：10/10 PASS
```

## 写作定位

P4-PHYS-A/B/C/D/E/F 合在一起可支持“三轴最亮构型与光路机制图谱”章节：fixed 几何下存在近镜面 top-1，sun/view 组合角落下出现更亮的金属宽瓣/几何因子构型。该章节只服务 model-known 仿真机制解释和观测规划边界，不构成真实未知目标三轴姿态反演系统。
