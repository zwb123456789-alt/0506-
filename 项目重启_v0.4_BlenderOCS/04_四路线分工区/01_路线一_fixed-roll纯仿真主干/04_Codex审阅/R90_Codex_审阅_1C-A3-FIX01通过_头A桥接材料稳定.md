# R90_Codex 审阅：1C-A3-FIX01 通过，头A桥接材料稳定

最后更新：2026-06-29  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
92_1C-A3-FIX01_桥接材料claim边界收窄_Claude执行报告.md
```

## 0. 裁决

```text
1C-A3-FIX01：PASS
成果分流：允许形成成果区稳定摘要
性质：桥接说明材料，非论文正文正式段落
新训练 / 推理：未发现
新图表 / 表格生成：未发现
模型 / split / 超参 / seed 修改：未发现
三轴小项目 / 路线二 / 路线三 / 路线四扩展：NOT RELEASED
```

92 号完成了 R89 要求的 claim 边界收窄。A-3 可作为头A“负结果 -> 24 号三问”桥接材料稳定。

## 1. R89 要求核查

### 1.1 Sentinel / 拒识口径已收窄

92 号已将 91 号中过强的“系统知道自己不知道”“拒绝输出”“应当拒识”等正向表述，改为：

```text
exact-bin yaw = 0.00% 是 strict classifier + circular yaw-block 外推场景下的诊断性 sentinel；
它提示当前协议下 exact-bin 分类发生失败；
可以启发后续 reject / confidence gate 设计；
但当前尚未实现或验证真正的拒识机制。
```

该口径符合 R82/R86/R88 稳定边界。

### 1.2 Figure S3 口径已收窄

92 号不再写“排除训练失败”。修正为：

```text
Figure S3 提供训练过程透明度；
training loss 下降且未见数值发散；
但不排除优化不足、过拟合、模型结构限制或特征表达不足。
```

该口径符合 R88 对 S3 的限制。

### 1.3 OCS-only 口径已收窄

92 号将 “OCS 未携带可区分信息” 改为：

```text
C2 OCS-only 在当前特征、几何采样、模型和固定协议下，
未检出稳定高于 chance 的 yaw/pitch 可区分信息。
```

该表述保留 fixed-protocol negative evidence，同时避免扩大为 OCS 通道本身不携带姿态信息。

### 1.4 Pitch 与共同失效口径已收窄

92 号已将 pitch 表述限定为：

```text
fixed-roll + 当前图像模型 + circular yaw-block 协议下，pitch 指标稳定高于 chance。
```

同时将“共同失效区域”改为：

```text
protocol-defined extrapolation failure regime
```

并明确这不是已定位的物理低信息区域。

## 2. 接受的稳定桥接口径

A-3 对 24 号三问的当前稳定回答为：

```text
What can be known：
  fixed-roll 条件下 pitch 指标高于 chance；
  yaw 在 random split 分布内可学，但无法跨 circular yaw-block 未见弧段外推；
  C2 OCS-only 在当前特征、模型和协议下未检出高于 chance 的可区分信号。

When complementary：
  当前 fixed-roll + circular yaw-block + early fusion 协议下，
  joint 未观察到自动互补增益；
  这是互补研究的 fixed-protocol null-result 基准，不是 fusion 普适无用结论。

When trustworthy：
  exact-bin yaw=0.00% 仅作为诊断性 sentinel，
  标记 strict classifier 在 circular yaw-block 外推下的失败；
  可启发后续 confidence / reject gate 设计，
  但当前尚未实现 calibrated rejection、conformal prediction、ECE 或 posterior-like agreement。
```

## 3. 使用边界

允许写：

```text
头A 已形成 fixed-protocol 负结果证据链、图表/SI 草案和三问桥接说明。
当前负结果为 24 号三问提供 lower-bound 约束和 null-result 基准。
Yaw 主叙事是 extrapolation gap，不是 yaw unobservability。
Pitch 结论限于 fixed-roll/current protocol。
Early fusion no automatic gain 限于当前协议和 fusion 方式。
Exact-bin yaw=0.00% 是诊断性 sentinel，不是已实现拒识机制。
```

不得写：

```text
yaw 物理不可观测。
OCS 通道本身不携带姿态信息。
fusion 永久无用。
系统已经知道自己不知道或已实现拒识。
当前结果可外推真实 GEO、三轴自由姿态或暗室实验。
当前负结果已完整回答 24 号三问。
```

## 4. 头A状态

按 R05，头A 目标是：

```text
负结果证据链 + 图表/SI 资产 + 负结果到 24 号三问的桥接说明
```

当前状态：

```text
A-1 E45D-FIX02 图表/表格预生成草案：DONE，R86 通过
A-2 P0 SI 资产草案：DONE，R88 通过
A-3 负结果 -> 24 号三问桥接材料：DONE，R90 通过
```

因此，**头A 主线收口已达到 R05 设定的闭合口**。后续不应直接启动新训练或正文正式改写，而应与头B文献/方法线合并审阅，重新裁定下一阶段入口。

## 5. 成果区摘要

对应成果区稳定摘要：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/
18_A3负结果到24号三问桥接材料_R90通过.md
```

## 6. 下一步建议

按 R05，下一步应进入：

```text
头A/头B 合并审阅准备：
  1. 确认头A闭合材料：R86、R88、R90 及成果区 16/17/18。
  2. 检查头B 84/85 后续文献线是否已有输出。
  3. 若头B尚未完成，则继续 B-1 文献检索/方法总结，不启动新训练。
  4. 待两头都清楚后，再做合并 Codex 审阅 / 总裁决，重定下一阶段入口。
```

仍未放行：

```text
论文正文正式改写
档 B 新训练
raw 4-dim OCS-only
--mode all
后验架构 / 超参 / 特征补救
单帧多维 OCS vs 光变曲线正式实验设计
三轴小项目或路线二/三/四扩展
```

## 7. CLAUDE.md 同步

本轮不立即修改 `CLAUDE.md`。建议待头A/头B合并审阅完成并产生新的稳定下一步后，再受控同步最新状态、下一步和必要红线。

