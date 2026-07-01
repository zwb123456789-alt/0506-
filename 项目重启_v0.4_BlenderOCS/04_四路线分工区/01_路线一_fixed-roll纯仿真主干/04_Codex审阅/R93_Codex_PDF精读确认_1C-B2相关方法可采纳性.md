# R93 Codex PDF 精读确认：1C-B2 相关方法可采纳性

最后更新：2026-06-29
执行端：Codex
性质：对 R92 后续补充 PDF 精读的确认稿。本文只确认文献方法依据，不放行训练、不生成数据、不改代码、不改 split/模型/超参/seed、不改论文正文、不改成果区、不改 CLAUDE.md。

## 0. 结论

```text
PDF 精读结论：R92 的方向成立，且优先级应进一步收紧
首选下一步：P0 只读诊断，而非直接训练或新渲染
第一批可采纳方法：signature distance / confusion cluster / 伪光变 probe / 协议对齐核查
第一批 C 类候选：角度连续判据，其次非朴素 fusion
暂不建议直接启动：正式 light-curve sequence 新数据线、完整 CRLB、复杂 BRDF/散射参数反演
```

## 1. 精读后的方法确认

### 1.1 Wetterer & Jah 2009 支持什么

该文完整支持把本项目后续主线从“单帧 OCS 分类”升级到“光度序列 + 动态/可观测性诊断”的方向。其方法结构是：

```text
light curve time history
facet forward model
simplified Cook-Torrance reflectance
quaternion-based UKF
state includes attitude, angular velocity, optionally reflection parameters
```

对本项目最关键的是失败模式：当初始姿态偏差过大时，不同 rotation-axis positions 可产生 near-identical light curves；作者明确将其称为 classical observability issue。Fig. 4 中多个初始轴收敛到不同解簇，和当前 yaw-block 外推失败高度对应。

可采纳：

```text
1. 把 yaw-block 失败写成可观测性/歧义问题，而不是模型偶然失败。
2. 把 light-curve sequence 设为治本方向。
3. 保留 Cook-Torrance/BRDF 同族前向模型叙事。
4. 允许 surface-reflection parameters 作为未来状态/不确定性维度，但不在当前阶段展开。
```

不可越界：

```text
1. 不能说 Wetterer & Jah 证明单帧 OCS 可定姿。
2. 不能说它证明真实数据已经能精确定姿；文中真实 AEOS 数据部分反而提示测量模型不足。
3. 不能直接照搬 UKF 为下一步主模型；它更适合作为物理/可观测性依据。
```

### 1.2 Gerwe & Idell 2003 支持什么

该文确认 Fisher/CRLB 是合适的可观测性语言，但也提示完整 CRLB 不能轻率做。它要求概率测量模型、噪声模型、局部导数和 nuisance parameters。作者明确说明 CRLB 往往偏乐观，真实不确定性会抬高下界。

可采纳：

```text
1. P0 做 Fisher-lite / signature-distance 诊断。
2. 用 yaw-yaw 距离矩阵和局部差分敏感性解释何处信息不足。
3. 用多视角/多几何减少 blind spots 的思想解释为什么 sequence 或多几何覆盖可能有效。
4. 把 pitch>yaw 各向异性写成姿态分量与观测几何耦合差异。
```

暂不建议：

```text
1. 直接做完整 CRLB 并作为强理论结果。
2. 忽略噪声、BRDF、形状、传感器误差后给出“理论下界”。
3. 把 CRLB 结果写成全局唯一性证明；它主要是局部下界/局部信息分析。
```

### 1.3 Kaasalainen I/II 支持什么

Kaasalainen I/II 确认 lightcurve inversion 的核心不是“某个强模型”，而是足够好的 lightcurves、多个观测几何、合适的约束和对歧义的克制。重要细节包括：

```text
1. convex inversion 可在多几何 lightcurves 下稳定。
2. nonconvex inversion 失去唯一性，局部极小和初值重要。
3. 多几何覆盖比单纯点数更重要。
4. 散射律过复杂会导致不稳定和不现实参数。
5. 大凹陷在光变中的指纹可能很弱，光变天然有平滑效应。
```

可采纳：

```text
1. 单帧 OCS 必须作为 lightcurve 的低信息下界，而不是等价替代。
2. 后续正式 light-curve sequence 应强调多几何/多时刻覆盖。
3. P0 伪光变 probe 只能作为“是否值得做正式序列”的预检。
4. 不要在本阶段引入复杂 BRDF 参数反演；先保持散射模型可控。
```

不可越界：

```text
1. 不能把小行星 shape inversion 直接等同于航天器姿态估计。
2. 不能声称 lightcurve 一定给唯一姿态。
3. 不能用“更多点”替代“更多几何覆盖”。
```

### 1.4 ChiNet 与 Pasqualetto 2021 支持什么

ChiNet 支持两个方法原则：序列比单帧更合理，多模态必须做可分离消融。Pasqualetto 2021 支持融合/滤波中不确定性和耦合结构的重要性，尤其是 feature covariance、tightly/loosely coupled architecture 的比较。

可采纳：

```text
1. 当前 early concat negative result 只能否定 naive concat。
2. fusion 应至少做 image-only / OCS-only / early concat / late or decision-level fusion 的并列消融。
3. 若做 mid fusion，需维度平衡、归一化或 gating，防高维图像分支淹没 OCS。
4. 若讲 trustworthy，最低限度要有 uncertainty/calibration/agreement，而不是把 exact-bin 0% 说成拒识。
```

不可越界：

```text
1. ChiNet 的 RGBT channel concat 不等于本项目 image+OCS concat 一定有效。
2. Pasqualetto 的 monocular keypoint/PnP/MEKF 不能直接当作 OCS 融合模型依据。
3. 这些文献支持“不要用一次 naive fusion 下普遍结论”，不支持“fusion 必然提升”。
```

### 1.5 Kumar 2025 与 Tang 2025 补充什么

Kumar 2025 确认真实 SSA 场景下 light curve sequential comparison 是长期监测非合作目标姿态/自旋变化的有效工具，并结合 digital twin 做 light curve inversion。但其目标偏“长期自旋/状态演化”，不是单次精确定姿。

Tang 2025 确认深度学习可从光变数据中学习复杂映射，但仍依赖 light curves、观测几何、仿真训练和拟合验证。它可支撑“序列/深度模型可作为候选”，但不支撑当前马上换强 backbone。

可采纳：

```text
1. Kumar 支撑 P0/P2 的 sequence 主线和数字孪生对照思想。
2. Tang 支撑光变数据 + 深度模型的可行性，但更适合作为 P2 后文献，不作为 P1 立即行动依据。
```

## 2. 方法优先级的最终建议

### P0：现在最值得做

```text
P0-1 协议对齐核查
确认 V0.3/V0.4、random split/yaw-block、exact-bin/near-hit 的口径差异。

P0-2 signature distance
计算 OCS-only、image embedding、joint embedding 的 yaw-yaw 距离矩阵。

P0-3 confusion cluster
按真实 yaw、预测 yaw、pitch、fold 聚簇，找近似等价解簇。

P0-4 伪光变 probe
固定 pitch/几何条件，把现有 yaw 序列串起来，只做描述性可分性分析。
```

验收产物建议：

```text
1. 一张方法表：每项只读诊断回答哪个问题。
2. 三类图：distance heatmap、confusion cluster map、伪光变曲线示例。
3. 一张结论表：失败更像判据问题、几何盲区、信息形态不足，还是模型容量问题。
```

### P1：只在 P0 后逐项放行

```text
P1-A circular regression / sin-cos regression / von-Mises
目的：剥离 exact-bin 判据放大效应。

P1-B non-naive fusion
目的：回答 image 与 OCS 是否互补。
最低配置：late fusion 或 decision-level fusion；再考虑 gated/mid fusion。
```

### P2：暂不直接开

```text
P2 light-curve sequence 正式数据线
进入条件：
1. P0 证明单帧签名存在歧义或信息盲区；
2. P1-A 后 yaw-block 仍有显著外推鸿沟；
3. 新数据协议、几何采样、噪声/退化、inverse-crime 防护写清楚；
4. 明确单帧 OCS 是 lower bound，sequence 是 higher information layer。
```

## 3. 论文方法叙事的推荐版本

推荐写法：

```text
Current results identify a protocol-defined yaw extrapolation gap under single-frame OCS/image inputs. This gap is consistent with known photometric attitude ambiguities caused by symmetry and limited viewing geometry. We therefore treat single-frame OCS as an information lower bound and design a staged path toward observability diagnostics, continuous angular criteria, non-naive multimodal fusion, and eventually light-curve sequence modeling.
```

中文对应：

```text
当前结果揭示的是单帧 OCS/图像输入在 yaw-block 外推协议下的可辨识性鸿沟，而不是 yaw 的物理不可观测。该现象与光变定姿文献中由对称性和观测几何不足导致的歧义一致。因此，单帧 OCS 应作为信息下界保留；下一步应先做可观测性只读诊断，再逐项评估连续角度判据、非朴素融合，并最终决定是否进入正式光变序列建模。
```

## 4. 本轮精读 PDF

```text
JGCD_2009_Wetterer_Jah_attitude_determination_light_curves.pdf
JOSAA_2003_Gerwe_Idell_orientation_Cramer_Rao.pdf
Icarus_2001_Kaasalainen_lightcurve_inversion_I_shape.pdf
Icarus_2001_Kaasalainen_lightcurve_inversion_II_complete_inverse_problem.pdf
TAES_2022_Rondao_ChiNet_multimodal_spacecraft_pose.pdf
Kumar_2025_Light_curves_sequential_comparison_ActaAstronautica_10.1016-j.actaastro.2025.04.018.pdf
AandA_2025_Tang_asteroid_shape_inversion_deep_learning.pdf
Acta_2021_PasqualettoCassinis_CNN_pose_tightly_loosely_coupled.pdf
```

## 5. 最终裁决建议

```text
建议：接受 R92，并以 R93 作为精读确认补充。
下一步：只放行 P0 只读诊断包。
暂缓：新训练、新渲染、完整 CRLB、正式 light-curve sequence。
```

