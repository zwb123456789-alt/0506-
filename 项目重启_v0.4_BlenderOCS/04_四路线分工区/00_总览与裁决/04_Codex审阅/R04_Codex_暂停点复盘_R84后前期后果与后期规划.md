# R04 Codex 暂停点复盘：R84 后前期后果与后期规划

最后更新：2026-06-29  
审阅端：Codex  
性质：暂停点战略复盘与后续工作规划；不放行新训练、论文正文正式改写、三轴小项目、路线二/三/四扩展。

## 0. 当前真实暂停点

当前不应再按 `CLAUDE.md` 中的“E45C 后、E45D 前”理解实际进度。经目录核查，真实状态是：

```text
R83：E45C 图表/SI 规划体系已通过并稳定
R84：E45D 图表预生成草案已审阅，判定 NEEDS FIX01
Claude 83：E45D-FIX01 已执行并写入报告
Codex：尚未对 E45D-FIX01 作正式通过/返工裁决
```

因此，当前暂停点定义为：

```text
E45D-FIX01 已执行、但尚未通过 Codex 审阅的暂停点。
```

本文件不替代 E45D-FIX01 的正式审阅，不判定其 PASS。后续若恢复执行，第一步必须先审阅：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
83_1C-E45D-FIX01_FigureS5样本数与版式修正_Claude执行报告.md
```

## 1. 前期工作造成的真实后果

### 1.1 科学后果

路线一 C 没有得到“OCS 或 joint 明显提升姿态反演”的正结果。相反，当前稳定结果指向：

```text
fixed-roll + circular yaw-block holdout 下，
C2 OCS-only、C3 image_only、C3 joint 均不能可靠外推到未见连续 yaw 弧段。
```

这不是项目失败，而是主线从“反演成功率论文”转向“可观测性、泛化边界与置信一致性论文”的关键证据。当前最稳的科学表述是：

```text
random split 表明分布内 yaw 信息可学；
circular yaw-block 下 continuous / near-hit 指标接近随机或仅弱高于随机；
因此当前固定协议揭示的是 extrapolation gap，而不是 yaw 信息不存在。
```

### 1.2 方法后果

前期流程最有价值的成果不是某个模型精度，而是建立了可审计的负结果链：

```text
C1/C2 OCS-only 证据包
C2/C3 三通道负结果证据包
E45A 失败模式归因诊断
E45B 指标重构与 extrapolation-gap 叙事
E45C 图表/SI 规划体系
E45D 图表预生成草案及 FIX01 修正
```

其中 E45A 的核心价值是把 exact-bin yaw=0.00% 从“物理不可观测”重新定位为：

```text
strict cross-yaw extrapolation + 72-bin exact 判据下，
预测系统性坍缩到训练可见 yaw 区间，未进入 holdout yaw 块。
```

这使负结果可解释、可写、可防守。

### 1.3 写作后果

论文主图表体系已经从“Figure 5 全 0 exact-bin”纠偏到：

```text
Figure 3：yaw CMAE / within-6 / coarse45 vs chance baseline
Figure 4：pitch anisotropy
Table 2：R82 指标重构主表
Figure S5：exact-bin sentinel + holdout-prediction diagnostic
```

这次纠偏很重要：如果仍把 exact-bin 0% 作为正文主图，论文会显得像一个单指标失败报告；改用 CMAE、within-k、coarse-bin 与 chance/random baseline 后，叙事才是“外推鸿沟与指标层级”。

### 1.4 流程后果

前期阶段门总体有效，但流程已有两个风险：

```text
1. 状态文件容易滞后：CLAUDE.md 已落后于 R84/Claude83 的真实状态。
2. 局部图表错误仍可能进入草案：R84 发现 Figure S5 样本数硬编码与总样本数矛盾。
```

这说明后续不能为了赶写作跳过 Codex 审阅；图表阶段也必须核查事实一致性。

## 2. 当前不能做的事

在 E45D-FIX01 未正式审阅通过前，暂不建议做：

```text
论文正文正式改写
S1/S2/S3/S4 批量预生成
档 B 新训练
raw 4-dim OCS-only
--mode all
后验架构 / 超参 / 特征补救
三轴小项目
路线二 / 三 / 四扩展
CLAUDE.md 同步更新
```

尤其不能用新训练去“补一个正结果”。当前负结果链的价值正在于固定协议和可审计边界；若此时后验补救，容易把论文从稳健负结果变成追结果。

## 3. 后期工作总原则

后期应按“先封口、再写桥、后扩展”的顺序推进。

```text
封口：把 E45D-FIX01 图表事实错误审阅干净，稳定图表草案。
写桥：把负结果如何服务 24 号三问写成桥接说明，而不是直接改正文。
扩展：只有在路线一 C 证据链闭合后，才讨论三轴小项目、路线二真实光度锚点、路线三暗室增强。
```

后续主叙事不应再问“怎样证明模型一定能反演姿态”，而应问：

```text
在 model-known 条件下，哪些姿态信息能被学到；
哪些信息只能分布内学习、不能跨连续 yaw 弧段外推；
哪些指标能提示低置信、拒识或观测规划边界。
```

## 4. 推荐后续顺序

### Step 1：正式审阅 E45D-FIX01

目标：只判断 Claude83 是否修正 R84 指出的事实问题。

必须核查：

```text
Figure S5(b) 样本数是否来自 JSON n_samples 聚合
C2 / image_only / joint 是否为 34,632 / 2,664 / 2,664
总数是否为 39,960
Figure S5 是否无文字遮挡
Figure 4 是否增加顶部留白
脚本是否只改可视化逻辑，未触碰训练、模型、split、超参或 seed
```

若通过，再形成路线一 `R85` 审阅文件，并允许 E45D 成果摘要进入路线一成果区。

### Step 2：同步状态文件

只有 E45D-FIX01 通过后，才同步 `CLAUDE.md`。同步内容应只保留：

```text
E45D 图表/表格预生成草案已稳定
当前下一步变为写作桥接或剩余 SI 资产规划
档 B、后验补救、三轴、路线二/三/四仍未放行
```

不要把 R80-R85 的历史全过程搬入 `CLAUDE.md`。

### Step 3：写“负结果服务 24 号三问”的桥接文件

建议在路线一 `04_Codex审阅/` 或 `02_Claude输出/` 先形成非正文桥接材料，回答：

```text
What can be known：
  random split 可学与 yaw-block 外推失败共同定义可知边界。

When complementary：
  当前 joint 相比 image_only 没有实质增益，说明早期融合不是自动互补。

When trustworthy：
  holdout yaw 块预测比例为 0.0，支持把此类输出标记为低置信/不可外推，而不是强行反演。
```

该桥接文件不是论文正文，不写 Abstract / Introduction / Discussion。

### Step 4：再决定是否补齐剩余 SI 资产

若 E45D 稳定，下一批只建议做低风险图表资产：

```text
Figure S1：C2 65-run yaw CMAE distribution by config
Figure S2：Yaw CMAE vs within-6 scatter
Figure S3：training curves
Figure S4：overlap diagnostic
Table S2/S3：per-fold detail
```

这些仍属于图表/表格资产，不应引入新训练或新模型判断。

### Step 5：论文正文只在材料闭合后启动

正文改写的启动条件：

```text
E45D 或后续 SI 资产稳定
桥接文件完成
主图表编号和主表数值冻结
CLAUDE.md 同步
```

正文顺序建议先写 Results，不先写 Abstract/Introduction/Discussion。原因是当前证据链强在结果和边界，先写宏大定位容易 claim 膨胀。

## 5. 路线二与真实数据的后期位置

路线二不应被用来证明“真实监督姿态反演”。GEO 数据库有：

```text
真实光度
几何
型号
时间序列
```

但没有：

```text
目标三轴姿态真值
```

所以路线二最合适的位置是：

```text
真实光度锚点 / sim-to-real 分布与趋势校准 / 多几何现实性证据
```

它能回答专家对仿真真实性的质疑，但不能替路线一提供真实姿态标签。路线二后续应服务三件事：

```text
1. 证明真实工程中确实存在多帧多几何光度序列。
2. 检查仿真光度与真实光度在量级、分布、趋势上的差距。
3. 把“光度常用于异常监测而非精确定姿”写成现实边界，而不是项目缺陷。
```

## 6. 路线一需要怎样站得住脚

路线一后续不必改成“真实未知目标姿态反演”。它应更明确地站在以下位置：

```text
idealized but physically consistent synthetic benchmark
known-geometry / model-known target
information and extrapolation boundary study
confidence-aware rejection / observation-planning precursor
```

需要收紧的地方：

```text
不说当前模型能可靠姿态反演。
不说 OCS 与 image 已证明互补。
不说 exact-bin 0% 代表 yaw 物理不可观测。
不说仿真数值可直接匹配真实 GEO。
不说固定 roll 结果能外推三轴。
```

可以强化的地方：

```text
固定协议下的负结果可审计。
random split 与 yaw-block 对比揭示分布内学习和跨弧段外推的差异。
pitch 强于 yaw，说明 fixed-roll 空间中存在各向异性。
joint 没有自动带来增益，反而给 fusion 方法设计提供反例边界。
holdout-prediction diagnostic 可服务低置信/拒识逻辑。
```

## 7. 最终建议

当前最好的后期路线不是“扩大战场”，而是“把失败模式写成科学边界”。具体执行判断：

```text
先审 E45D-FIX01。
通过后稳定 E45D 成果摘要并同步 CLAUDE.md。
随后写负结果到 24 号三问的桥接材料。
再补齐必要 SI 资产。
最后才进入 Results 正文草稿。
```

三轴小项目、路线二和路线三仍然重要，但它们应在路线一 C 完成“可审计边界论文”的主体闭合后再接入。否则会把一个已经能站住的外推鸿沟结果，重新拖回“我要证明真实姿态反演能成功”的高风险叙事里。

