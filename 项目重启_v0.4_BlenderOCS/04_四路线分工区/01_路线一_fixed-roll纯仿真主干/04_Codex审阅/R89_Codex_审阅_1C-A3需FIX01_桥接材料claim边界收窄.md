# R89_Codex 审阅：1C-A3 需 FIX01，桥接材料 claim 边界收窄

最后更新：2026-06-29  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
91_1C-A3_负结果到24号三问桥接材料_Claude执行报告.md
```

## 0. 裁决

```text
1C-A3：NEEDS FIX01
总体结构：可保留
数值主线：基本正确
三问映射：基本对齐 24 号
成果区分流：暂不进入成果区
主要问题：when trustworthy / sentinel 口径偏强，部分 negative evidence 表述超出 R82/R88 稳定边界
```

91 号已经完成了 A-3 的主体工作：把 fixed-roll + circular yaw-block 负结果整理到 24 号三问下，且没有训练、推理、改 split/模型/超参或写论文正文正式段落。  
但它将若干诊断性结果写成了偏操作化、偏机制闭合的判断。A-3 是后续论文写作的桥接地基，因此这些话术必须先收窄，否则容易在正文中膨胀成 unsupported claim。

## 1. 主要问题

### 1.1 “拒识 / 知道自己不知道”口径过强

91 号多处写到：

```text
系统"知道自己不知道"
valid sentinel
外推失败 -> 拒绝输出
系统应当拒识而非猜测
exact-bin sentinel 可以提供清晰的拒识信号
```

这些表述超出了当前证据。当前模型并没有实现 calibrated rejection、conformal prediction、ECE/reliability diagram、posterior-like agreement 或明确的 reject option。  
R82/R86/R88 稳定口径只是：

```text
exact-bin yaw = 0.00% 是 strict classifier + circular yaw-block 下的哨兵/诊断指标；
它提示当前协议下 exact-bin 分类失败；
不能单独承载可信拒识机制或物理不可观测 claim。
```

FIX01 必须统一改为：

```text
exact-bin yaw=0.00% 可作为诊断性 sentinel，提示 strict classifier 在 circular yaw-block 外推场景下发生失败；
它可以启发后续 reject / confidence gate 设计；
但当前尚未实现或验证真正的拒识机制。
```

不得再写“系统知道自己不知道”“应当拒识”“拒绝输出”作为已实现结论。

### 1.2 Figure S3 “排除训练失败”过强

91 号写到：

```text
Figure S3 ... loss 下降且未见发散，排除训练失败作为负结果原因
```

R88 已明确：Figure S3 只能说明训练过程被记录、training loss 下降且未见发散；C2 validation pitch accuracy 仍低水平波动，C3 detail 文件中也有 possible-overfit warning。  
因此不能写“排除训练失败”。应改为：

```text
Figure S3 提供训练过程透明度，显示 training loss 下降且未见数值发散；
但不能排除优化不足、过拟合、模型结构限制或特征表达不足。
```

### 1.3 “OCS 未携带可区分信息”需改成“当前协议未检出”

91 号写到：

```text
OCS 多观测光度向量（C2 口径）未携带可区分的 yaw 或 pitch 信息
```

这句话容易被读成物理层面的 OCS 信息不存在。R82/R88 允许的是 fixed-protocol negative evidence：

```text
C2 OCS-only 在当前特征、当前几何采样、当前模型和 circular yaw-block 协议下，未检出稳定高于 chance 的 yaw/pitch 可区分信息。
```

FIX01 应将所有类似表述改为“当前协议/当前 C2 特征和模型下未检出”，不得写成 OCS 通道本身不携带信息。

### 1.4 “pitch 稳定可学”需加 fixed-protocol 限定

91 号写：

```text
pitch 在各向异性下稳定可学
```

该结论方向正确，但应加限定：

```text
fixed-roll + current image model + circular yaw-block 协议下，pitch 指标稳定高于 chance。
```

不得泛化为三轴、真实目标、其他图像退化条件或任意模型下 pitch 可学。

### 1.5 “共同失效区域”应避免被读成物理区域图

91 号将 yaw circular holdout 下三通道接近 chance 写成“共同失效区域”。这可保留，但必须解释为：

```text
protocol-defined failure regime / unobserved yaw-arc extrapolation regime
```

而不是姿态空间中已经定位出的物理低信息区域。当前尚未做 per-geometry observability map 或三轴信息地图。

## 2. 可保留内容

以下内容可保留，只需按上面边界收窄措辞：

```text
1. 三问结构：What can be known / When complementary / When trustworthy。
2. Table 2 精炼指标。
3. yaw extrapolation gap 主叙事。
4. random split approx. 65-70% vs circular yaw-block exact-bin 0.00% 的对照。
5. pitch within-3 明显高于 chance 的 fixed-roll anisotropy。
6. early fusion no automatic gain。
7. A-1/A-2 图表资产与三问映射。
8. 24 号完整三问仍未被当前负结果完全回答的缺口清单。
```

## 3. FIX01 修改要求

请 Claude 生成 `91_...FIX01...` 修正版，而不是直接覆盖 91 号原件。

必须完成：

1. 全文替换强拒识口径：
   - 删除或改写“系统知道自己不知道”“应当拒识”“拒绝输出”“清晰拒识信号”。
   - 改为“诊断性 sentinel / 启发后续 reject gate / 尚未实现拒识机制”。
2. 收窄 Figure S3 口径：
   - 不写“排除训练失败”。
   - 写“training loss 下降且未见数值发散，但不排除优化/过拟合/结构限制”。
3. 收窄 OCS-only 口径：
   - 不写“OCS 未携带信息”。
   - 写“当前 C2 特征、几何采样、模型和固定协议下未检出稳定高于 chance 的可区分信息”。
4. 收窄 pitch 口径：
   - 所有 pitch 可学表述加 fixed-roll/current protocol 限定。
5. 收窄共同失效口径：
   - 改为 “protocol-defined extrapolation failure regime”，不要写成已经完成物理低信息区域定位。
6. 保留“不完整回答 24 号三问”的边界，并继续明确不能外推真实 GEO、三轴姿态或暗室实验。

## 4. 下一步给 Claude 的短提示词

```text
请执行 1C-A3-FIX01：修正 91 号桥接材料的 claim 边界。

输入：
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/91_1C-A3_负结果到24号三问桥接材料_Claude执行报告.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R89_Codex_审阅_1C-A3需FIX01_桥接材料claim边界收窄.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R88_Codex_审阅_1C-A2-FIX01与A2-GEN通过_P0_SI资产草案稳定.md

任务：
1. 保留 91 号的三问结构和主要数值。
2. 收窄 when trustworthy / sentinel 口径：
   - 不写“系统知道自己不知道”“应当拒识”“拒绝输出”。
   - 改写为：exact-bin yaw=0.00% 是诊断性 sentinel，可启发后续 reject/confidence gate，但当前未实现或验证拒识机制。
3. 收窄 Figure S3 口径：
   - 不写“排除训练失败”。
   - 写 training loss 下降且未见数值发散，但不排除优化不足、过拟合、模型结构限制或特征表达不足。
4. 收窄 OCS-only 口径：
   - 不写 OCS 本身未携带可区分信息。
   - 写当前 C2 特征、几何采样、模型和固定协议下未检出稳定高于 chance 的 yaw/pitch 可区分信息。
5. 收窄 pitch 和共同失效口径：
   - pitch 只限 fixed-roll/current protocol。
   - “共同失效”改为 protocol-defined extrapolation failure regime。

输出：
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/92_1C-A3-FIX01_桥接材料claim边界收窄_Claude执行报告.md

红线：
- 不训练、不推理、不生成新图表/表格。
- 不改 split / 模型 / 超参 / seed。
- 不写论文正文正式段落，只修正桥接说明材料。
- 不启动档 B、raw 4-dim OCS-only、--mode all、三轴小项目、路线二/三/四。
- 不声称 yaw 物理不可观测，不声称 fusion 永久无用，不外推真实 GEO / 三轴 / 暗室。
- 若输出过长，按 Part 1/2/3 分段写入，直到文件完整。
```

## 5. 当前阶段状态

头 A：

```text
A-1 E45D-FIX02：DONE，R86 通过
A-2 P0 SI 资产：DONE，R88 通过
A-3 桥接材料：NEEDS FIX01
```

A-3-FIX01 通过后，才能判定头 A 主线闭合，并进入与头 B 文献线的合并审阅准备。

