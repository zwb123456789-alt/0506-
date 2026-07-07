# R152 Codex 审阅：008 通过，PARTIAL_GENERALITY 接收并放行 P4-PHYS-D

最后更新：2026-07-06  
审阅对象：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/008_P4PHYS_C_mechanism_generality_Claude执行报告.md
v0.4_results/25_three_axis_p4phys_c_mechanism_generality/
```

## 1. 裁决

008 / 25 包 **接收，达到强接收标准**。R151 要求的 fixed `phase63/L1-G1` 下高亮机制普遍性检验已完成。

正式接收结论标签：

```text
PARTIAL_GENERALITY
```

含义：

```text
金属主体近镜面对齐探测器是 fixed phase63/L1-G1 下高亮候选的普遍机制；
隐身板附加受照面不是普遍高亮机制，只解释 top-1 相对 R4 的排序增量。
```

据此放行下一阶段：

```text
P4-PHYS-D：sun/view 小矩阵扩展阶段门
```

## 2. 接收证据

25 包完整存在，008 报告存在，gate matrix 与 redline self-check 全部 PASS。候选池满足 R151 的强接收标准：

```text
候选池 n=159，<=200；
来源覆盖 01/P2/P3/23A/23B；
top-1、R4、R3 均 force-include；
候选 OCS 覆盖 0.01062832–0.20889048；
EXR / v_sun_macro.npy / ocs.json 全候选可定位。
```

数值链路可审计：

```text
机制签名复用 24 包口径；
抽样逐像素重算 vs ocs.json 最大 rel_diff ≈ 1.5e-7；
material 全程标注为 B0 proxy。
```

机制富集证据：

```text
near_specular_metal base rate = 25/159 = 15.7%
top 10%: 16/16 满足，富集 ×6.36
top 25%: 24/40 满足，富集 ×3.82
near_specular_metal=1 mean OCS = 0.201656
near_specular_metal=0 mean OCS = 0.063034
corr(OCS, pct_NoH>=0.99) ≈ +0.95
corr(OCS, reflect_vs_det) ≈ -0.80
```

隐身板增量证据：

```text
top-1 dark_panel_contrib ≈ 0.00877
R1 roll+15 高亮簇 median dark_panel_contrib ≈ 0.00873
R4 dark_panel_contrib ≈ 0.00093
```

因此隐身板增量可解释 top-1 超过 R4 的排序差异，但不能写成所有高亮候选的普遍机制。

## 3. 必须保留的限定

接收时增加一个写作限定：

```text
near_specular_metal=0 组是总体更暗，不是每个非机制点都暗。
```

原因：审阅中发现 near_specular_metal=0 组仍存在 rank 22–32 的高亮边缘点，OCS 可达约 0.199。这些点通常满足 `strong_surface_highlight` 或 `dark_panel_increment`，但因严格 `avgN_vs_H / reflect_vs_det` 阈值未进入 near_specular_metal。因此后续写作应采用：

```text
金属近镜面对齐机制在高亮 top 分位强富集，并使候选总体显著更亮。
```

不得写成：

```text
所有不满足 near_specular_metal 的姿态都暗。
```

## 4. 不接收项

不得接收为：

```text
1. 所有 sun/view 几何下的全局高亮机制。
2. 隐身板增量是普遍高亮机制。
3. material-level attribution 已完成。
4. 三轴小项目已经最终闭口。
5. 可启动 R128、路线二/三/四、训练或论文正文最终改写。
```

关于 material pass 的裁决：

```text
material pass 不列为 P4-PHYS-D 前置。
```

理由：D 阶段问题是“机制与 top-1 是否随 sun/view 改变而稳定或迁移”，当前 `part/material proxy + B0 参数` 足以完成阶段门。若 D 阶段后要写材料级正式 claim，再单独补 material pass。

## 5. 下一步

下发：

```text
R153_Codex_任务单_P4PHYS-D_sunview小矩阵扩展阶段门.md
```

P4-PHYS-D 的目标不是大规模全局搜索，而是用受控 sun/view 小矩阵回答：

```text
fixed phase63/L1-G1 下确认的 top-1 与金属近镜面高亮机制，
在少量相邻或代表性 sun/view 几何下是否保持、迁移或失效。
```

P4-PHYS-D 可新增少量渲染，但必须规模受控；不得启动 R128、训练、路线二/三/四或论文正文最终改写。

