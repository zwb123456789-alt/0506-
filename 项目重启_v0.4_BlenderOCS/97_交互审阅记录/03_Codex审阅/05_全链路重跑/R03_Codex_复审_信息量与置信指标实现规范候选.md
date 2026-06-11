# Codex 复审意见：v0.4 信息量与置信指标实现规范候选稿

生成时间：2026-06-09

## 1. 复审对象

```text
05_全链路重跑/v0.4_信息量与置信指标实现规范_Claude候选.md
```

对照基准：

```text
24_v0.4项目论文主线最终冻结稿_OCS口径形态与mismatch账面对齐版.md
25_v0.4主线冻结原因备案_为什么采用24号.md
04_BlenderOCS方法重建/13_v0.4前向模型冻结规范_最终冻结版.md
04_BlenderOCS方法重建/14_v0.4数据与manifest字段规范_最终冻结版.md
05_全链路重跑/00_重跑任务清单.md
97_交互审阅记录/03_Codex审阅/05_全链路重跑/R02_Codex_复审_三条软肋与FIM投稿定位.md
```

## 2. 总体判断

**小修后可以冻结。**

Claude 候选稿总体方向正确，已经把 CR-SOFT-002 的关键问题处理到位：v0.4 反演范式不再等同于 2664 类 softmax，而是冻结为：

```text
closed-grid candidate scoring
+ posterior-like distribution over the same 2664 candidate grid
+ distance/kernel likelihood 或 template likelihood 作为主实现口径
+ softmax grid classification 作为 learned-scoring 增强对照
```

这与 24 号主线、25 号备案和 R02 复审意见一致。候选稿也正确保留了 13/14 作为前向模型与 manifest/source_data 底座，没有把指标规范写成对 13/14 的重写。

但目前不建议原样冻结。原因不是主线错，而是有几处实现级表述容易在代码阶段被误读为硬门槛或已闭合定义，尤其是 ECE/reject 阈值、image 模板/嵌入来源、图表必出清单。它们需要在候选稿中降一档，写成 phase0 标定项或论文结果支撑项。

## 3. 主要问题

### P1-1：ECE_thr=0.10 与 G3 不应成为代码前硬 gate

候选稿在 §3.4 与 §5.3 写到：

```text
G3 验证集上 calibration 可接受（ECE 低于设定阈，§5.3）。
主口径 G3 gate：验证集 ECE ≤ ECE_thr（阈值待确认，建议 phase0 后定，初值 0.10）。
```

这个方向对，但冻结前需要改口径。现在 0.10 只是经验初值，不能作为 v0.4 成败门槛，也不能作为是否进入代码阶段的硬 gate。否则代码阶段会出现一个账面风险：主口径物理上成立，但因为尚未标定的 ECE 阈值不过，就被错误判为范式失败。

建议修成：

```text
G3 为 calibration diagnostic / phase0 acceptance check，不是代码前硬 gate。
ECE_thr 仅为 phase0 初始观察值，最终阈值由验证集 reliability diagram、NLL/ECE 曲线和 risk-coverage 结果共同标定。
若 ECE 暂不达标，优先记录为 calibration limitation，并排查 τ/h、特征尺度、模板来源；不得直接推翻 closed-grid candidate scoring 范式。
```

同理，§6.5 的 `reject_decision`、coverage、risk-coverage 工作点也应明确为验证集后标定，不在本规范阶段写死。

### P1-2：image template / image embedding 来源还没有完全闭合

候选稿多处使用：

```text
image-only 网络的嵌入向量（penultimate embedding）
image clean 嵌入
clean 前向签名（OCS clean L1 向量 / image clean 嵌入）
```

OCS 侧 clean L1 模板是闭合的，因为它直接来自前向模型。image 侧则还差一个实现边界：如果 image embedding 来自尚未训练的 image-only 网络，那么 template likelihood 的模板来源、训练 split、防止标签泄漏、clean/degraded 是否共用同一 encoder，都需要写清楚。

建议在候选稿中补一段：

```text
image template likelihood 的 embedding encoder 必须在每个 split 内单独定义、训练或冻结；
query image 与 candidate clean image 必须通过同一 encoder / 同一 feature_config 得到嵌入；
不得用 test query 或 test label 信息更新候选模板；
若 phase0 尚无可靠 learned encoder，则 image 主口径先降级为 deterministic image signature 或仅保留 image 分支为待标定项，OCS_A_L1 的 distance/kernel likelihood 先行闭合。
```

这个小修很关键。否则 image 主口径表面上与 OCS 同构，实际却把“还未训练的网络嵌入”提前当成已闭合物理签名。

### P1-3：`js_thr`、`ang_thr`、`low_confidence_flag` 等拒识阈值需要统一标注为标定项

候选稿 §6.1 和 §6.5 定义了：

```text
conflict_flag = 1 if (JS_img_ocs > js_thr) and (ang_top1 > ang_thr)
low_confidence_flag / reject_decision
```

这些指标本身正确，而且是 24 号 “when trustworthy” 的核心。但冻结稿必须明说：`js_thr`、`ang_thr`、`h_thr`、`m_thr`、coverage 工作点不是作者现在拍板的常数，而是由验证集和 risk-coverage 曲线确定的参数。

建议把 §6.5 加一句硬约束：

```text
所有 reject/conflict 阈值均为 validation-calibrated thresholds；本规范只冻结指标定义、保存字段和标定流程，不冻结数值阈值。
```

这样后续重跑不会把“还没跑出来的论文结论”伪装成“代码前已知参数”。

### P2-1：“主线必出 / 审稿防线必出”图表清单建议降为“论文最小证据目标”

候选稿 §12.1 写到：

```text
F-OBS-1/3、F-AMB-1、F-COMP-1、F-CONF-1/2 为主线必出；
F-CTRL-1、F-MIS-1 为审稿防线必出；
F-DTH-1、F-FIM-1 为可选增强。
```

这对论文规划有价值，但作为代码前冻结规范略硬。现在还没有 phase0 结果，也没有资源估算；如果直接冻结为“必出”，会把实验计划写得比证据链更重。

建议改为三层：

```text
代码最小保存字段：必须保存，缺失则证据链断。
主线最小分析图：phase0 后优先生成，用于判断论文主线是否成立。
论文投稿目标图：若结果支持则进入主文；若结果不支持则转为补充材料、负结果或边界讨论。
```

其中 `F-OBS-1/3`、`F-COMP-1`、`F-CONF-1/2` 可以保留为优先主线图；`F-CTRL-1`、`F-MIS-1` 建议写成“高水平投稿强烈建议”，不要在代码前写成无条件必出。

### P2-2：“作者已拍板”建议改成“作者已确认高层范式”

候选稿开头和 §0.4 写到“作者已拍板”，并把范式与主口径排除在待确认项之外。这个账面方向可以保留，但语气建议收紧。

建议改为：

```text
作者已确认高层范式：closed-grid candidate scoring。
作者已确认主实现族：distance/kernel likelihood 或 template likelihood。
以下实现级子参数仍待 phase0 标定：核函数、带宽/温度、feature_space、template_source、reject 阈值、softmax 对照是否进入主表。
```

这样既保留你已经决定的 CR-SOFT-002 主线，又避免后续把每一个子参数都解释为作者已经最终拍板。

### P2-3：`is_primary_paradigm` 字段命名不够准确

§11.1 schema 中写：

```json
"is_primary_paradigm": "<bool: true for distance/template likelihood, false for softmax 增强口径>"
```

这里语义容易混。真正的 paradigm 是 `closed_grid_candidate_scoring`；distance/template/softmax 是 scoring_method 或 implementation route。

建议改名为：

```json
"is_primary_scoring_method": true
```

或者保留旧字段但补充：

```text
paradigm 固定指 closed_grid_candidate_scoring；
primary / enhanced 只描述 scoring_method 地位，不描述 paradigm 地位。
```

## 4. 可直接采纳的内容

以下内容已经足够好，可以进入最终冻结稿：

1. 不重写 13/14，只做 24 号新增反演输出和置信指标增量。
2. `candidate_grid = 72 × 37 = 2664`，0/360 不重复，画图可复制边界。
3. 角距离主用球面单位向量 geodesic distance，component periodic distance 仅诊断。
4. A/B 口径字段化：`A_independent_photometric` 为主线，`B_image_derived` 只作 common-mode 对照。
5. F1/L1/F2/L2 字段化：L1 主线，F1 信息下界，F2 semi-oracle diagnostic，L2 Future Work。
6. 反演范式两层化：closed-grid candidate scoring 与 learned model evaluation 分开。
7. softmax 不作为唯一主口径，仅为 learned-scoring 增强对照。
8. split 边界清楚区分 closed-grid discrimination、interpolation heldout、phase/geometry shift。
9. posterior-like distribution、entropy、margin、top-k、NLL、JS、overlap、risk-coverage 的指标链条完整。
10. L1 quasi-static / attitude-compensated 假设写得正确，Δθ 敏感性被限定为离散后处理。
11. FIM/CRLB 定位正确：可选升级层，不是代码 gate，离散指标保底。
12. 投稿口径保持 24/25 与 R02 的高目标上探策略，没有退回 AST 或 Acta/ASR 默认。

## 5. CR-SOFT-002 的最终定论

本轮可以把 CR-SOFT-002 冻结为以下口径：

```text
v0.4 的反演范式不是连续 yaw/pitch 回归，也不是单一路径的 2664-class softmax。

主范式是 closed-grid candidate scoring：
在 2664 个已知姿态候选上，为每个候选生成 score / likelihood，
再归一化为 posterior-like distribution。

主实现族是 distance/kernel likelihood 或 template likelihood：
OCS_A_L1 侧优先用 clean L1 signature 的距离/核似然闭合；
image 侧可用 image embedding/template likelihood，但 embedding 来源必须在 phase0 明确。

softmax grid classification 是 learned-scoring 增强对照：
只有在 split、类别覆盖、soft-label、temperature scaling 和 ECE 校准都写清时才纳入对照。
```

这个定论对论文是正向的：它把贡献从“训练一个 2664 类分类器”提升为“在同一候选网格上比较 OCS/image/fusion 的信息结构与置信一致性”。这更贴近 24 号主线，也更利于高水平 SCI/高目标投稿。

## 6. 冻结条件

候选稿完成以下小修后，可作为代码前指标规范冻结：

```text
1. 把 ECE_thr=0.10、G3、reject/conflict 阈值全部标注为 phase0 / validation 标定项，不作为代码前硬 gate。
2. 补充 image embedding / image template source 的实现边界，避免未训练 encoder 或 split 泄漏。
3. 将图表清单从“无条件必出”改为“最小保存字段 + 主线优先分析图 + 投稿目标图”三层。
4. 将“作者已拍板”改为“作者已确认高层范式与主实现族”，子参数仍待 phase0 标定。
5. 修正 `is_primary_paradigm` 命名或补充说明，避免 paradigm 与 scoring_method 混用。
```

完成后建议把文件名从候选稿改为：

```text
05_全链路重跑/v0.4_信息量与置信指标实现规范_最终冻结版.md
```

随后再同步：

```text
CLAUDE.md
00_只打开本文件夹时的启动说明.md
00_v0.4总控流程.md
05_全链路重跑/00_重跑任务清单.md
06_论文v0.4重写接入/00_论文v0.4重写接入说明.md
99_归档索引/01_上下文读取与提示词维护规范.md
99_归档索引/02_项目文件夹职能规范.md
```

同步前不建议启动 `06_v0.4_code/`。

## 7. 给 Claude 的修订提示词

```text
请基于 Codex R03 复审意见，对：

05_全链路重跑/v0.4_信息量与置信指标实现规范_Claude候选.md

做小修，目标是形成：

05_全链路重跑/v0.4_信息量与置信指标实现规范_最终冻结版.md

修订要求：

1. 保留主结论：v0.4 主反演范式为 closed-grid candidate scoring；主实现族为 distance/kernel likelihood 或 template likelihood；softmax grid classification 仅作 learned-scoring 增强对照，不作唯一主范式。
2. 不修改 24/25/13/14 与启动集。
3. 将 ECE_thr=0.10、G3 calibration、reject/conflict 阈值全部改写为 phase0 / validation-calibrated thresholds；本规范只冻结指标定义、保存字段和标定流程，不冻结数值阈值。
4. 在 image/template likelihood 处补充 image embedding / image template source 的实现边界：encoder 必须在 split 内定义、训练或冻结；query 和 candidate 使用同一 feature_config；不得用 test query 或 test label 更新模板；phase0 未闭合时允许 image 分支标为待标定，OCS_A_L1 先行闭合。
5. 将“主线必出 / 审稿防线必出”图表清单改成三层：代码最小保存字段、主线优先分析图、论文投稿目标图。不要把尚未有结果支撑的图写成无条件必出。
6. 将“作者已拍板”表述改为“作者已确认高层范式与主实现族”；核函数、温度/带宽、feature_space、template_source、reject 阈值、softmax 是否进主表等仍为 phase0 标定项。
7. 修正或解释 `is_primary_paradigm` 字段，避免把 paradigm 与 scoring_method 混用。推荐改为 `is_primary_scoring_method`。
8. 保留 L1 quasi-static、Δθ 离散后处理、FIM/CRLB 可选升级层、高目标投稿牵引但不扩大 claim 等原有正确内容。

输出只生成最终冻结版文件内容，不改动其他文件。
```

## 8. 一句话结论

Claude 候选稿已经把大方向走对了：CR-SOFT-002 应冻结为 closed-grid candidate scoring + distance/template likelihood 主口径，而不是 2664 类 softmax。现在需要的不是推翻，而是把阈值、image embedding、图表义务和字段命名这些实现账面小修干净；修完即可冻结，并进入 `06_v0.4_code/` 前的 phase0 代码准备。
