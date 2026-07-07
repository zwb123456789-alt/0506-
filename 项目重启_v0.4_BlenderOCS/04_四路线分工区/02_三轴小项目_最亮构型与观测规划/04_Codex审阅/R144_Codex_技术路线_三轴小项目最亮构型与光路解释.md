# R144 Codex 技术路线：三轴小项目最亮构型与光路解释

最后更新：2026-07-06  
文件性质：Codex 侧技术路线文件，不是 Claude 执行报告，不是阶段门接收结论，不直接启动实验。  
基础材料：`P4PHYS-A_R141评估与后续路线候选_Claude讨论稿.md`、R141、R142、R143、三轴小项目指导文件与 P3 明细表核验结果。  

## 1. 唯一最高目标

本小项目只服务一个最高目标：

```text
在已知卫星模型和前向光学模型下，
找出卫星在哪个 yaw/pitch/roll 姿态、哪个太阳入射几何、哪个探测器观测几何下最亮；
并解释这束最亮光从哪里入射，照到卫星哪个部位、哪种材料/表面，
再沿什么方向进入探测器。
```

所有其它内容都降为辅助：

```text
高信息姿态：只用于标注最亮点附近是否有观测/反演价值。
低信息区：只用于负面对照。
观测规划：只用于后续实验选择，不替代“找最亮”。
utility / information / roll sensitivity：只作为辅助风险标签，不能取代 brightness top-1。
```

因此技术路线必须按以下顺序推进：

```text
先确认 single-pose top-1 最亮点；
再解释该点的入射-表面/材料-探测器光路；
再检验同类光路机制是否普遍对应一片高亮姿态/几何；
最后才把高信息、低信息、观测规划、路线二/三接口作为辅助回接。
```

## 2. 当前证据与必须修正的口径

P1/P2/P3 当前只覆盖固定 sun/view 几何：

```text
phase63 / L1-G1
SUN = [1, 0, 0.3]
DET = [0.5, -1, 0.1]
```

所以现阶段不能声称已找到所有 sun/view 下的全局最亮构型，只能先解决：

```text
固定 phase63/L1-G1 sun/view 下，yaw/pitch/roll 三轴姿态空间中的最亮点。
```

P3 明细表给出的当前 sampled-grid top-1 候选为：

```text
R1_high_info
yaw = 245.0
pitch = +30.0
roll = +15
ocs_total = 0.208377
glint_flag = 0
saturation_flag = 1
```

但该点还不能直接作为最终结论：

```text
top-1 与 top-2 仅差 0.224%；
top-1 与 R4 最高 single-pose 仅差 3.15%；
R1 在 roll=+15 呈尖峰，roll=0 和 roll=+30 均约 0.04084；
现有 roll 档位只覆盖 {-60,-45,-30,-15,0,+15,+30,+45,+60}。
```

所以 Claude 讨论稿中“需要加密”的判断采纳；但以下表述必须修正：

```text
1. R4 是 roll-robust 高亮区和机制对照，不是与 R1 并列的 top-1，除非后续数据实际超过 R1。
2. R1 当前不能直接称为 glint 尖峰；表中 glint_flag=0、saturation_flag=1，只能写作 roll-sharp / saturation-associated high-brightness candidate。
3. R4 的 single-pose 最高点不是 roll0，而是 yaw147.5 / pitch+12.5 / roll=-15；roll0 只可作为 R4 鲁棒性说明的一部分。
```

## 3. 总体技术路线

### A. 固定几何 top-1 确认

目标：

```text
在固定 phase63/L1-G1 sun/view 下，确认 yaw/pitch/roll single-pose 最亮点。
```

执行内容：

```text
1. 重聚合 P1/P2/P3 top-1/top-N。
2. 输出 R1 top 簇 roll profile。
3. 输出 R4 鲁棒亮区 roll profile。
4. 明确 P1/P2/P3 量纲与几何可比性。
5. 围绕 R1 top 簇做局部 roll/yaw/pitch 加密。
```

推荐加密矩阵：

```text
yaw   = {242.5, 245.0, 247.5}
pitch = {27.5, 30.0, 32.5, 35.0}
roll  = {+5, +10, +12.5, +15, +17.5, +20, +25}
```

R4 仅作少量对照：

```text
中心：yaw=147.5, pitch=+12.5
roll = {-30, -15, 0, +15, +30}
```

通过标准：

```text
新 top-1 不在加密矩阵边界；
相邻 yaw/pitch/roll 未显示继续上升趋势；
R1/R4 角色明确；
报告明确该结论仅限固定 phase63/L1-G1 几何。
```

若 top-1 落在边界，只沿边界方向追加一小圈，不扩成全局暴力遍历。

### B. 最亮点物理光路归因

进入条件：

```text
A 阶段确认 fixed-geometry top-1 稳定。
```

目标：

```text
解释 top-1 的光从哪里来、照到哪里、经什么材料/表面响应、如何进入探测器。
```

优先级：

```text
1. 先审计已有 EXR/NPY/JSON 是否能支持像素级、part/material、normal/depth 归因。
2. 若已有字段不足，才对 top-1 和少量对照姿态做 object-ID / material-ID / normal / depth pass 诊断渲染。
3. 若 pass 难以实现，可采用 per-object 或 per-material isolation 诊断，但必须标注为 proxy。
```

必须输出的物理量：

```text
太阳入射方向；
探测器视线方向；
主贡献部件；
主贡献材料/表面；
入射角、观测角、法向关系；
反射/散射路径是否接近镜面方向；
亮度是否受 saturation、遮挡边界或数值峰影响。
```

通过标准：

```text
至少能把 top-1 的主要光度贡献追溯到明确的部件/材料/表面或明确说明字段缺口；
直接计算与 proxy 判断分开写；
不得编造 part/material/surface 归因。
```

### C. 高亮机制普遍性检验

进入条件：

```text
B 阶段已经得到 top-1 的光路机制签名。
```

机制签名建议：

```text
dominant_part
dominant_material
incident_angle_bin
view_angle_bin
normal/reflection alignment
glint/saturation state
occlusion/boundary state
```

目标：

```text
判断 top-1 的光路机制是否普遍对应高亮姿态/几何，还是只是孤立峰。
```

检验对象：

```text
top-N 姿态；
R1 加密邻域；
R4 鲁棒亮区；
旧 22 号包中的 C01-C09 只作辅助回接；
R3/R2/R5 作负面或暗/中性对照。
```

通过标准：

```text
若同机制候选普遍高亮：给出高亮机制物理解释句。
若同机制候选不普遍：说明 top-1 是否是局部 roll 尖峰、saturation-associated peak、遮挡边界或其它数值/几何偶然峰。
```

### D. sun/view 几何扩展

进入条件：

```text
A/B/C 阶段已经形成固定几何下的 top-1、光路解释和机制普遍性判断。
```

目标：

```text
从 fixed sun/view top-1 推进到完整目标中的 yaw/pitch/roll + sun/view 最亮构型。
```

原则：

```text
不做 yaw/pitch/roll/sun/view 全变量无差别暴力展开；
先围绕 B/C 阶段识别出的高亮机制设计 sun/view 采样；
优先改变太阳入射方向和探测器方向中最可能影响该机制的角度；
保留少量机制负面对照。
```

该阶段完成后，才可写：

```text
在所采样的 sun/view 几何集合内，最亮 yaw/pitch/roll/sun/view 构型为 ...
```

仍不得无证据外推为连续全空间绝对最亮。

### E. 收口与外部接口

收口条件：

```text
1. fixed-geometry top-1 已确认。
2. top-1 光路/材料/表面/探测器路径已解释或字段缺口已明确。
3. 同类机制是否普遍高亮已检验。
4. sun/view 扩展的边界已说明。
5. 高信息/低信息/观测规划已被降为辅助标注。
```

路线二接口：

```text
只验证真实 GEO 光度趋势或几何覆盖现实性；
不得要求 GEO 提供三轴姿态真值；
不得写成真实未知目标姿态反演验证。
```

路线三接口：

```text
优先暗室验证仿真预测的最亮姿态是否实测仍高亮；
验证 roll-aware 最亮点是否相对 fixed-roll 迁移；
高信息/低信息只作解释辅助。
```

## 4. roll 遍历口径

当前不是“全空间暴力遍历 roll”，而是分层遍历：

```text
第一层：围绕 fixed-geometry top-1 候选做局部 roll 加密。
第二层：若新 top-1 落在边界，只沿边界方向追加。
第三层：光路机制确定后，只在同机制候选和 sun/view 扩展候选中继续扫 roll。
第四层：只有当多个区域出现接近 top-1 且机制不同，才设计更大范围 roll 补采样。
```

这样既承认 roll 对最亮姿态是必要变量，也避免在目标尚未聚焦时把资源耗尽在全局网格爆炸上。

## 5. 当前直接落点

本技术路线不改变当前直接下一步：

```text
仍应先完成 R141 / 23A / 006A：
固定 phase63/L1-G1 sun/view 下的 top-1 与 roll 局部确认。
```

R141 执行时应同时读取：

```text
R142_Codex_审阅_R141讨论稿部分采纳但不替代006A执行.md
R143_Codex_规划_R141_R142后固定几何最亮姿态确认执行方案.md
本 R144 技术路线文件
```

但本文件本身不是新任务单，不要求 Claude 立即启动额外阶段。

## 6. 红线

```text
不训练任何模型。
不启动 R128。
不启动路线二/三/四。
不写成果区。
不改 CLAUDE.md。
不覆盖 19/20/21/22。
不把 fixed sun/view top-1 写成所有 sun/view 的全局最亮。
不把高信息姿态写成最亮主目标。
不把 R4 鲁棒亮区写成并列 top-1，除非新数据实际支持。
不把 glint、材料、部件、法向、探测器路径归因写成已知，除非有直接字段或明确 proxy 证据。
```

