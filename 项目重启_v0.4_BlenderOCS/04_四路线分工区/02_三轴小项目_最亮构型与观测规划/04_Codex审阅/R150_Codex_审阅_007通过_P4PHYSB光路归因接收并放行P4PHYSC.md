# R150 Codex 审阅：007 通过，P4-PHYS-B 光路归因接收并放行 P4-PHYS-C

最后更新：2026-07-06  
审阅对象：

```text
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/02_Claude输出/007_P4PHYS_B_top1_light_path_attribution_Claude执行报告.md
v0.4_results/24_three_axis_p4phys_b_light_path_attribution/
```

## 1. 裁决

007 / 24 包 **接收，达到强接收标准**。R149 要求的 top-1 物理光路归因已完成，可以放行下一阶段：

```text
P4-PHYS-C：高亮机制普遍性检验
```

但本接收只表示 fixed `phase63/L1-G1` 下已确认 top-1 的光路机制被解释清楚，不表示所有 sun/view 几何下的全局最亮机制已经成立，也不表示三轴小项目已经闭口。

## 2. 接收证据

24 包完整存在，007 报告存在，gate matrix 与 redline self-check 全部 PASS。关键链路可审计：

```text
top-1 EXR 使用 23A 真正 top-1：
v0.4_results/23A_three_axis_p4phys_top1_roll_confirmation/render/shadow_passes/phase63/roll+015/yaw2450_pitchp0275_roll+015_camera.exr

未误用 23B smoke 样本：
yaw2425_pitchp0225_roll+015
```

逐像素重算 OCS 与 `ocs.json` 一致：

```text
R1_top1 rel_diff = 5.488e-08
R4_robust rel_diff = 4.180e-09
R3_neg rel_diff = 3.872e-09
```

top-1 per-part 贡献清楚：

```text
金属主体 0.19849659，占 95.024%
隐身板   0.00877461，占 4.201%
太阳能板 0.00161930，占 0.775%
```

光路几何解释成立：金属主体贡献像素的加权法向与半程向量夹角约 `0.57°`，反射方向与探测器夹角约 `1.06°`，金属贡献像素中 `N·H >= 0.99` 占 `81.34%`，支持“金属主体大面元近镜面对齐探测器”的解释。

## 3. 接收的科学结论

可以接收为当前阶段稳定结论：

```text
1. fixed phase63/L1-G1 top-1 的主高亮机制是金属主体大面元近镜面对齐探测器。
2. 该机制表现为面状近饱和高亮，不是离散单点 glint；可写 saturation-associated 或 near-specular surface highlight。
3. top-1 超过 R4 的小增量主要来自隐身板附加受照面：
   top-1 隐身板 0.008775 vs R4 隐身板 0.000931；
   差额 0.00784 约等于 top-1 - R4 总差 0.00774。
4. R3 负面对照暗的原因是近镜面几何破坏：
   加权法向偏半程向量约 12.45°，反射方向偏探测器约 21.78°，镜面项显著变弱。
```

其中第 3 点只接收为 **B 阶段 top-1 与 R4 最小对照内的决定性增量解释**，不得直接升级为“所有高亮姿态均由隐身板增量排序决定”。是否普遍成立必须由 P4-PHYS-C 检验。

## 4. 边界与不接收项

必须保留：

```text
1. 本结论只限 fixed phase63/L1-G1 sun/view 与当前局部 top-1。
2. material-level 仍为 proxy；当前只有 object/part 与 B0 材料参数级解释。
3. 不能写成所有 sun/view 几何下的全局最亮。
4. 不能写成高亮机制普遍性已经证明。
5. 不能据此启动 R128、路线二/三/四、训练或论文正文最终改写。
```

关于 material pass 的裁决：

```text
material pass 不列为 P4-PHYS-C 前置。
```

理由：P4-PHYS-C 的主要问题是“同类几何签名是否普遍对应高亮”，目前 `IndexOB + part/material proxy + B0 参数` 足以完成机制普遍性筛查。若 P4-PHYS-C 之后需要写材料级正式 claim，或发现 part proxy 无法区分关键面元，再单独下发 material pass / material-ID 渲染增强任务。

## 5. 下一步

下发：

```text
R151_Codex_任务单_P4PHYS-C_高亮机制普遍性检验.md
```

P4-PHYS-C 的核心任务不是再找新的 top-1，而是复用已有 20/21/23A/23B 包，计算机制签名并检验：

```text
具有“金属主体近镜面对齐 + 可能的隐身板附加增量”的姿态，是否普遍处于高亮候选；
不具有该签名的姿态是否系统性更暗；
top-1 的光路解释能否上升为一类高亮机制。
```

P4-PHYS-C 仍不得扩展 sun/view、不得新增渲染、不得训练、不得启动 R128。

