# R158 Codex 审阅：011/28 通过，P4-PHYS-F 按采样包络收口

最后更新：2026-07-06  
审阅对象：`011_P4PHYS_F_Hspvm_local_refinement_Claude执行报告.md`  
结果包：`v0.4_results/28_three_axis_p4phys_f_hspvm_local_refinement/`  
上游任务：R157 / P4-PHYS-F Hsp_vm 角落局部姿态与几何加密  
Codex 裁决：通过；停止继续追角落，按“受控采样包络内局部最优”收口搜索轴  

## 1. 审阅结论

011 报告与 28 包通过 Codex 审阅。数值链路、渲染预算、锚点一致性、机制复算与红线自查均满足 R157 要求。

本轮 Claude 建议标签为 `NEED_SECOND_STEP_REFINEMENT`，原因是最高点仍在姿态/几何边界；Codex 接收这个事实判断，但不继续放行下一轮追角落。结合 016 号已采纳的局部搜索停机规则，P4-PHYS-E 与 P4-PHYS-F 连续两轮加密都把最高点推向新边界，说明当前高亮区是沿宽瓣/几何因子方向延伸的脊状区域，而不是即将自然闭合的孤立峰。

因此，P4-PHYS-F 的阶段裁决为：

```text
CONTROLLED_ENVELOPE_LOCAL_OPTIMUM_STOP
```

后续写作口径固定为：

```text
在本项目受控采样包络内，最高亮构型为
yaw=35, pitch=75, roll=-20 @ sp5_vm7(sun+5, view-7)，OCS≈0.27194。
包络外沿 yaw↓ / pitch↑ / roll↓ / sun→baseline 方向是否存在更高值未检验。
```

不得写成全 sun/view/pose 空间全局最亮。

## 2. 核验结果

Codex 核验到：

```text
28 包存在：audit / render / postprocess / tables / figures / text / scripts / logs 齐全
新增渲染：76 units = Stage B 52 + Stage C 24，未超过 80 上限
postprocess：79 ocs.json + 79 v_sun_macro.npy
Stage1：27/27 COMPLETE
Stage2：54/54 COMPLETE
数值一致性：79/79 OK，max_rel_diff = 1.196e-7
27 包锚点一致性：5/5 rel_diff=0
redline_self_check：10/10 PASS
```

非阻塞小瑕疵：28 包实际 273 个文件，`audit/generated_files_manifest.csv` 记录 269 个，漏列了清单自身与 3 个 `text/` 文件。该问题不影响数值裁决，但后续正式收口包必须修正 manifest 生成口径。

## 3. 关键事实

Stage1 固定 Hsp_vm 的 C_R3 局部姿态网格：

```text
最高点 = yaw035_pitch+075_roll-020
OCS = 0.27080873
相对 C_R3(0.22555675) 增益 = +20.1%
相对 baseline A_top1(0.20889048) 增益 = +29.6%
边界状态 = yaw=35 下边界 / pitch=75 上边界 / roll=-20 下边界
```

Stage2 sun/view microgrid：

```text
最高点 = sp5_vm7 / yaw035_pitch+075_roll-020
sun_offset = +5
view_offset = -7
OCS = 0.27193961
边界状态 = sun_offset=+5，仍在 microgrid 边界
```

因此 P4-PHYS-F 没有把 E 轮角落峰闭成内部局部峰，而是揭示了更强的受控包络边界峰。

## 4. 机制裁决

全表最高点机制解释接收为：

```text
metal wide-lobe / geometric-factor highlight
```

机制量：

```text
dominant_part = 金属主体
metal_pct = 99.48%
weighted_NoL = 0.8097
weighted_NoV = 0.8756
weighted_NoL_NoV = 0.7090
avgN_vs_H = 3.554 deg
reflect_vs_det = 7.105 deg
near_specular_metal = 0
```

这说明高亮由金属主体宽瓣响应与 NoL·NoV 几何因子共同支撑，接近但不满足 R157 沿用的严格近镜面阈值（2°/4°）。因此论文中可以写“金属宽瓣/几何因子高亮”，不得写成严格近镜面对齐，也不得写成真实材料级归因。

## 5. 对三轴小项目的影响

R158 对前序结论的稳定修正如下：

```text
1. fixed 几何 top-1 A_top1 仍是 R148 固定几何范围内的 top-1，不再外推为 sun/view 组合最高。
2. R150 的近镜面机制仍解释 fixed top-1，但不是所有组合角落的唯一高亮机制。
3. R152/R154/R156/R158 共同形成两类机制：近镜面大面元对齐 + 金属宽瓣/几何因子高亮。
4. R3 不能再作为跨几何稳定负对照；其在角落区可转为高亮候选。
5. 三轴小项目的可写结论应是“受控采样包络内最亮构型与机制图谱”，不是全局最亮搜索完成。
```

## 6. 阶段门裁决

接收：

```text
011 报告
28 号包
P4-PHYS-F 的局部姿态/几何加密结果
受控采样包络内最高亮构型：yaw35/pitch75/roll-20 @ sp5_vm7，OCS≈0.27194
金属宽瓣/几何因子高亮机制解释
```

不接收为：

```text
全局 sun/view/pose 最亮结论
严格 near_specular_metal 结论
真实 material-level attribution
R3 全局负对照结论
继续无限追角落的依据
三轴小项目论文材料已自动完成
```

下一步放行一个只读收口材料包：

```text
R160 / P4-PHYS-G：三轴小项目 P4-PHYS 总收口材料包
```

该任务不得新增渲染，不得继续加密，只把 23A/23B/24/25/26/27/28 的稳定证据整理为可写作的 claim boundary、机制分类、图表素材与 SI 数据索引。
