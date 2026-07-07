# R156 Codex 审阅：010/27 通过，但三轴小项目不得收口

最后更新：2026-07-06  
审阅对象：`010_P4PHYS_E_sunview_3x3_cross_grid_Claude执行报告.md`  
结果包：`v0.4_results/27_three_axis_p4phys_e_sunview_3x3_cross_grid/`  
上游任务：R155 / P4-PHYS-E sun/view 3×3 组合小网格补齐  
Codex 裁决：`NEED_LOCAL_STEP_REFINEMENT`  

## 1. 审阅结论

010 报告与 27 包通过 Codex 审阅，接收为 P4-PHYS-E 的有效诊断结果；但本轮结果明确不支持三轴小项目收口，也不支持写成 baseline top-1 或 top-1 roll 邻域在 sun/view 组合扰动下稳定保持全局最高。

本轮核心裁决为：

```text
NEED_LOCAL_STEP_REFINEMENT
```

原因是 3×3 组合网格的全表最高点出现在角落几何 `Hsp_vm(sun+7, view-7)`，且由原负对照 `C_R3` 领先，脱离 top-1 roll 邻域簇。这不是 R154 的 pure sun / pure view 小矩阵已经覆盖的情况，必须进入局部姿态与几何加密。

## 2. 核验结果

Codex 已核验以下关键链路：

```text
27 包存在：audit / tables / figures / text / scripts / logs / postprocess 齐全
render/ 目录不存在：符合 0 新增渲染口径
postprocess：126/126 COMPLETE
metrics：9 几何 × 14 姿态 = 126 行
postprocess json/npy：126 + 126
reuse EXR：126 行记录，每行 camera/sun 均 OK；等价 252 个 EXR 引用全部可达
锚点一致性：H00 / pure sun / pure view 共 70/70，max rel_diff = 0
机制重算一致性：126/126 OK，max rel_diff = 1.443e-7
redline_self_check：11/11 PASS
```

两个非阻塞小瑕疵需要记录：27 包实际文件数为 282，而 `generated_files_manifest.csv` 记录 281，原因是清单未计入自身；`p4physE_gate_matrix.csv` 中 `010_report_exists` 仍为 finalize 时的 `PENDING`，但本地 010 报告已存在。这两个属于落盘顺序/清单口径问题，不影响本轮数值和科学裁决；后续 F 包应避免同类 stale gate。

## 3. 关键科学事实

逐几何最亮点：

```text
H00_baseline : A_top1       OCS=0.20889049  nsm=1  in-cluster=YES
Hsp_v0       : D5_roll125   OCS=0.19528240  nsm=0  in-cluster=YES
Hsm_v0       : D6_roll175   OCS=0.19493062  nsm=0  in-cluster=YES
Hs0_vp       : D6_roll175   OCS=0.20491531  nsm=1  in-cluster=YES
Hs0_vm       : D5_roll125   OCS=0.18548740  nsm=0  in-cluster=YES
Hsp_vp       : A_top1       OCS=0.21039591  nsm=1  in-cluster=YES
Hsp_vm       : C_R3         OCS=0.22555675  nsm=0  in-cluster=NO
Hsm_vp       : D6_roll175   OCS=0.14991522  nsm=0  in-cluster=YES
Hsm_vm       : D2           OCS=0.20011107  nsm=1  in-cluster=YES
```

因此：

```text
全表最高 = Hsp_vm / C_R3 / OCS=0.22555675
baseline A_top1 = 0.20889048
逐几何 top 落入 top-1 roll 邻域簇 = 8/9
near_specular_metal = 29/126
dominant_part 全部为金属主体
metal% 范围 = 87.6–99.51
```

这说明 R154 的“pure sun / pure view 下迁移仍在 top-1 roll 邻域”不能直接外推到 sun/view 同时扰动。组合反对角暴露了一个新的局部角落效应：`C_R3` 在 `Hsp_vm` 下不是近镜面对齐（`avgN_vs_H≈5.385°`, `reflect_vs_det≈9.966°`, `nsm=0`），但由于金属主体高占比和宽瓣/几何因子仍成为全表最高。

## 4. 对 R154 结论的修正边界

R154 的 `SUNVIEW_DEPENDENT_BUT_MECHANISTIC` 仍在 pure sun / pure view 小矩阵内成立；但 R156 必须新增以下限制：

```text
1. A_top1 不是 3×3 组合小网格全局最高。
2. D5/D6 仍解释 pure-shift 边上的迁移，但不能覆盖所有组合角落。
3. R4 不是跨组合几何稳定的同机制高亮对照；在反对角明显掉到约 0.10。
4. R3 不是跨组合几何稳定负对照；在 Hsp_vm 成为全表最高。
5. 金属主体主导稳定，但严格 near_specular_metal 不稳定，只在同号扰动附近成立。
6. 当前结果只能称为 ±7° 3×3 局部组合网格诊断，不能写成全 sun/view 全局规律。
```

## 5. 阶段裁决

接收：

```text
010 报告
27 号包
P4-PHYS-E 的 3×3 组合小网格诊断结果
```

不接收为：

```text
三轴小项目收口
baseline A_top1 全局最亮结论
top-1 roll 邻域跨 sun/view 组合稳定结论
R3 全局负对照结论
严格 near_specular_metal 全组合稳定结论
真实 material-level attribution
```

下一步放行：

```text
R157 / P4-PHYS-F：Hsp_vm 角落局部姿态与几何加密
```

## 6. 后续红线

P4-PHYS-F 只能围绕 `Hsp_vm(sun+7, view-7)` 及其极小邻域做局部加密，不得升级为全 sun/view 全姿态搜索。仍不得训练、不得启动 R128、不得启动路线二/三/四、不得写论文正文、不得把三轴小项目写成完成状态、不得把 B0 proxy 写成真实材料层归因。
