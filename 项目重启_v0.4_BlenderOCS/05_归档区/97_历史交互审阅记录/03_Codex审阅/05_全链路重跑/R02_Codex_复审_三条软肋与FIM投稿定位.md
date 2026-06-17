# Codex 复审意见：v0.4 主线三条软肋、FIM 策略与投稿定位

生成时间：2026-06-09

## 1. 复审对象

本次复审对象为：

```text
97_交互审阅记录/01_Claude输出/Claude方案_v0.4主线三条软肋与解决办法_附FIM策略与投稿定位.md
```

对照基准：

```text
24_v0.4项目论文主线最终冻结稿_OCS口径形态与mismatch账面对齐版.md
25_v0.4主线冻结原因备案_为什么采用24号.md
04_BlenderOCS方法重建/13_v0.4前向模型冻结规范_最终冻结版.md
04_BlenderOCS方法重建/14_v0.4数据与manifest字段规范_最终冻结版.md
05_全链路重跑/00_重跑任务清单.md
06_论文v0.4重写接入/00_论文v0.4重写接入说明.md
```

复审重点：

1. 三条“软肋”是否真实存在。
2. 解决方案是否应进入当前下一步“v0.4 信息量与置信指标实现规范”。
3. FIM / CRLB 是否可作为主线理论承重。
4. 投稿定位是否与作者最新“越高越好、以 `文献/00投稿目标/` 较高期刊为目标”一致。
5. 是否需要同步 24/25/13/14 或启动集。

## 2. 总体判断

**部分采纳，但不能原样并入主线文件。**

Claude 方案对当前 v0.4 主线的判断总体有价值，尤其是：

- 识别出 posterior-like distribution 与 consistency 指标尚未代码级闭合，这是当前真正阻塞代码实施的核心问题。
- 指出 L1 跨几何 OCS 向量需要明示 quasi-static / attitude-compensated 前提，这个提醒正确。
- 对 FIM / CRLB 采用“降级-稳定-升级”的策略，与 24 号既定红线基本一致。
- 强调科学新颖性不能只靠误差表，而要靠同源双通道、可观测性、置信一致性和共模退化对照，这与 24 号主线相容。

但该方案也有几处需要压稳：

1. 不应把 13/14 判定为“过时、需重写”。更准确的结论是：13/14 仍然是前向模型、manifest/source_data 底座；当前缺的是单独的“信息量与置信指标实现规范”，以及后续对 05 重跑清单/代码输出 schema 的增量同步。
2. 不应立即冻结“2664 类 softmax 网格分类”为唯一主口径。它是强候选，但会牵涉 split 设计、未见姿态泛化、closed-grid candidate scoring 与 learned model evaluation 的边界，必须在指标规范中先定义清楚。
3. 投稿定位不能从作者最新“以较高期刊为目标，越高越好”收窄成“主攻 AST、冲 TGRS、保底 Acta/ASR”。AST 可作为现实稳健层之一，但不是当前最终目标上限。
4. Progress in Aerospace Sciences、预警名单、学位目录等投稿判断具有时效性，正式投稿前必须查官方来源；当前复审不把这些判断写成最终事实。

结论：这份 Claude 方案可作为下一份“v0.4 信息量与置信指标实现规范”的重要输入，但不直接改写 24/25，不重写 13/14，不改变已经冻结的高目标投稿策略。

## 3. 主要问题 / Codex CR 编号

### CR-SOFT-001（P0）：把 13/14 说成“过时需重写”会误伤已冻结底座

Claude 方案 §4.1 写道：

```text
两份已冻结、已过复审的方法文件，撑不起 24 号主线的证据链。
13/14 号确实过时，重写规范是下一步工作。
```

复审判断：

这个判断前半句有道理，后半句过重。

13/14 的冻结对象是：

- 统一前向模型。
- Blender geometry pass / sun shadow / BRDF 后处理。
- OCS/image manifest。
- source_data 六子版本可追踪。
- 旧 v0.3 结果混用防线。

这些仍然有效，不应重写或降级。当前问题是 24 号主线新增了 observability、posterior-like distribution、consistency、top-k、entropy、JS divergence、image-derived OCS_B 等指标需求，而 13/14 的 `summary.json` 仍偏传统误差表。这是**指标层增量缺口**，不是前向模型冻结失败。

必须修正为：

```text
13/14 继续作为前向模型与 manifest/source_data 底座；
新增并冻结“v0.4 信息量与置信指标实现规范”；
该规范定义反演范式、posterior-like distribution、候选分布保存字段、
consistency 指标、A/B 口径字段、F1/L1/F2/L2 形态字段；
随后再增量同步 05_全链路重跑与代码输出 schema。
```

不得在没有新失败证据的情况下推翻 13/14。

### CR-SOFT-002（P0）：2664 类 softmax 可作为候选，但不能直接冻结为唯一主口径

Claude 方案推荐：

```text
OCS-only / image-only / fusion 三个模型必须输出同一离散姿态网格上的候选分布；
A. 网格分类（推荐主口径）：末层 2664-d softmax。
```

复审判断：

“同一姿态候选网格上的 posterior-like distribution”是正确要求，但“2664 类 softmax 分类”不能未经 split 设计就直接冻结。

原因：

1. 如果训练集并不包含所有 2664 个姿态类别，标准 softmax 分类无法合理预测未见类别。
2. 如果为了分类而让所有类别都参与训练，再做随机样本 split，需要明确这不是姿态外推测试，而是 closed-grid candidate discrimination。
3. 当前数据结构常常是每姿态每几何一条记录，样本重复度有限；分类、度量学习、模板匹配、kNN likelihood 或能量评分的适用边界不同。
4. 24 号需要的是“候选分布可比”，不一定要求所有模型都必须是同一种分类网络。

指标规范必须先区分两个层面：

```text
1. closed-grid candidate scoring:
   给定候选姿态网格，对每个候选生成分数 / likelihood / posterior-like score。
   该层用于 entropy、top-k、JS、consistency。

2. learned model evaluation:
   训练模型如何从 OCS/image/fusion 输入产生候选分数。
   可选 grid classification、metric learning、kNN likelihood、energy score 或 calibrated regression-to-grid。
```

建议：

- 不要在当前复审中拍死 A。
- 在“信息量与置信指标实现规范”中列出至少两套可执行候选：
  - A：closed-grid classification / soft-label classification。
  - B：kNN / template likelihood / distance-kernel posterior-like distribution。
- 主口径应以“能稳定输出同一候选网格上的可比较分布”为准，而不是以某个网络末层形式为准。
- 若选择 softmax 分类，必须同步定义 split 策略、类别覆盖、label smoothing / angular soft label、calibration 与 ECE 计算方式。

### CR-SOFT-003（P1）：L1 quasi-static 假设应采纳，但 Δθ 曲线不能写成“零成本物理验证”

Claude 方案对软肋 1 的判断成立：

```text
L1 跨几何多观测光度向量隐含短时间窗内姿态准静态或已补偿假设。
```

这确实应进入下一步规范或 24 号后续补充条款。建议采用如下红线：

```text
L1 跨几何 OCS 向量必须声明为短时间窗内受控多几何采样，
窗口内姿态准静态或已由姿态传播/补偿修正。
不得隐含瞬时多通道同时观测。
自转、曝光积分、运动模糊和轨道时变几何归入 L2 / Future Work。
```

但 Claude 方案称“Δθ 敏感性曲线零额外数据”，需要收紧：

- 若只用已有网格邻域替换或插值，这是**离散敏感性后处理**，不是完整物理时间窗仿真。
- 它可用于回答“L1 对姿态漂移的敏感边界”，但不能声称已经模拟真实自转光变。
- 若后续要更真实，需要 L2 时域光变曲线、曝光积分、姿态动力学和轨道时变几何，这仍属于 Future Work。

建议采纳为指标规范中的可选分析：

```text
L1_quasi_static_sensitivity:
  perturbation_deg: [...]
  construction: grid-neighbor / interpolation / regenerated-forward-pass
  metric: entropy / top-k confusion / nearest-neighbor ambiguity / consistency decay
  limitation: not a time-domain light-curve simulation
```

### CR-SOFT-004（P1）：FIM / CRLB 只能作为可升级层，不能作为代码前硬 gate

Claude 方案的 FIM/CRLB 分层策略基本正确：

```text
降级：离散稳健指标 / Fisher-like local sensitivity。
稳定：检查 visibility、shadow mask、边缘像素、GGX 峰附近的数值梯度稳定性。
升级：仅在梯度稳定局部区域引入正式 FIM / D-optimality / CRLB。
```

这与 24 号红线一致：

```text
不把 FIM / CRLB / conformal prediction 写成已经闭合的强理论结果，
除非后续实现和验证支撑。
```

必须保持：

- FIM/CRLB 不是当前进入代码的硬 gate。
- 不把 CRLB 写成全文理论主轴。
- 若只得到部分光滑姿态子集的 FIM，应明确是局部理论佐证，不覆盖阴影边界、遮挡突变和强 glint 区域。
- 若梯度稳定性不通过，论文仍可用离散 observability 指标成立。

可采纳写法：

```text
FIM tier is optional and conditional.
The main observability evidence is based on discrete candidate-grid metrics.
FIM/CRLB is reported only where differentiability and numerical stability are verified.
```

### CR-SOFT-005（P1）：投稿定位不能收窄成“主攻 AST”

Claude 方案 §7 给出：

```text
主攻 AST，冲刺 TGRS，保底 Acta/ASR。
```

这与作者 2026-06-09 最新确认不完全一致。当前冻结口径是：

```text
最终投稿目标以外部 文献/00投稿目标/ 中列出的较高期刊为参照，
目标尽量向上冲刺，越高越好。
```

因此：

- AST 可以作为现实稳健层或高水平 SCI 目标之一。
- TGRS、AIAA Journal、TAES、JGCD、Optics Express 等仍应保留为高水平冲刺候选。
- Nature / Science / 子刊 / NSR / Science Bulletin / Engineering / PRL / Progress in Aerospace Sciences 等可作为最高质量牵引与上探参照，不能在当前阶段直接排除为“无关”或“够不到”后从目标文件中降级。
- 也不能因为冲高刊而扩大 claim。高目标只牵引质量，不改变 24 号红线。

投稿策略应保持 24/25 与 06 号接入文件的新口径：

```text
高目标牵引、证据强度定档。
先按较高期刊要求设计问题、指标、图表和审稿防线；
再根据 v0.4 结果、指标闭合程度、文献对话质量、
是否有真实/半真实锚点决定最终投稿位。
```

### CR-SOFT-006（P2）：期刊目录、预警名单和期刊收稿类型需要投稿前核验

Claude 方案中涉及：

- 学位认定期刊分级目录。
- 中科院预警名单。
- Progress in Aerospace Sciences 是否只收综述或邀稿。
- ASR / MDPI 等是否存在预警风险。

这些信息具有时效性。当前复审不应把它们写成最终事实。投稿前必须以：

- 学校/学院当年成果认定目录。
- 期刊官网 author guidelines。
- 当年中科院预警名单。
- Web of Science / JCR / 中科院分区官方数据。

为准。

在当前项目文件中，只保留“投稿前核验”原则，不把具体排除判断写死。

## 4. 可以采纳的内容

以下内容建议进入下一步“v0.4 信息量与置信指标实现规范”或其前置讨论：

1. **软肋 2 的优先级判断**：posterior-like distribution、候选分布字段、consistency 指标和 A/B 口径字段是当前代码前最紧迫问题。
2. **同一候选姿态网格上的分布可比性**：OCS-only / image-only / fusion 必须能输出可比较的候选分数或 posterior-like distribution。
3. **summary / per-attitude 输出增量**：传统 mean error / Hit@5 保留为验证指标，但必须新增 top-k、entropy、margin、JS divergence、top-k overlap、consistency score、per-attitude candidate list 等字段。
4. **image-derived OCS_B 对照**：作为 common-mode failure 对照口径，不与 independent photometric channel 口径 A 混用。
5. **L1 quasi-static 红线**：L1 是短时间窗内受控多几何采样，不是瞬时多通道，也不是 L2 时域光变曲线。
6. **Δθ 敏感性分析**：可作为低成本边界分析，但必须标注为离散敏感性后处理。
7. **FIM/CRLB 三层策略**：离散指标保底，Fisher-like sensitivity 可选，正式 FIM/CRLB 需梯度稳定性验证后局部采用。
8. **科学新颖性三段承重墙**：
   - OCS/image 同源可比。
   - consistency-as-confidence 与 image-derived OCS_B 共模对照。
   - observation-geometry 信息量地图与观测规划价值。

## 5. 不建议采纳或必须改写的内容

以下内容不建议原样采纳：

1. “13/14 已过时、需要重写”。
   - 改为：13/14 仍有效，新增指标规范补足 24 号主线的反演输出与置信指标。
2. “2664 类 softmax 网格分类推荐主口径”。
   - 改为：closed-grid candidate scoring 是目标；softmax 分类、kNN likelihood、metric/energy score 都是候选实现，需先定义 split 与评估边界。
3. “Δθ 曲线零额外数据”。
   - 改为：可用已有网格做低成本敏感性后处理，但不是完整时域物理仿真。
4. “主攻 AST、冲刺 TGRS、保底 Acta/ASR”。
   - 改为：高目标牵引、证据强度定档；AST 是现实目标之一，不是当前目标上限。
5. 对具体期刊的硬排除。
   - 改为：投稿前根据官方目录和期刊官网核验。

## 6. 是否需要同步 24/25/13/14 与启动集

当前不建议直接同步 24/25/13/14。

理由：

- 24/25 已经冻结主线和投稿目标，Claude 方案不改变主线。
- 13/14 仍是有效方法底座，不应因指标缺口重写。
- 当前真正需要的是新建并冻结“v0.4 信息量与置信指标实现规范”。
- 本复审不是阶段通过结论，不需要把启动集改成“已完成指标规范”。

后续在指标规范完成并通过 Codex 复审后，才需要同步：

```text
CLAUDE.md
00_只打开本文件夹时的启动说明.md
00_v0.4总控流程.md
05_全链路重跑/00_重跑任务清单.md
06_论文v0.4重写接入/00_论文v0.4重写接入说明.md
99_归档索引/01_上下文读取与提示词维护规范.md
99_归档索引/02_项目文件夹职能规范.md
```

## 7. 建议的下一步文件

建议下一步由 Claude 或 Codex 生成：

```text
v0.4_信息量与置信指标实现规范.md
```

建议放置位置：

```text
05_全链路重跑/
```

建议职能：

```text
代码实施前的指标与反演输出冻结规范。
它不替代 13/14，而是连接 24 号主线与 05/06_v0.4_code 的反演、评估、source_data、summary 输出。
```

建议至少包含：

1. 规范边界：不改前向模型，不改 13/14 底座。
2. 姿态候选集定义：2664 grid、yaw/pitch、record_id、角距离。
3. 反演输出范式：
   - closed-grid candidate scoring。
   - learned model evaluation。
   - softmax / kNN / energy score 的可选实现与取舍。
4. split 与评估边界：
   - closed-grid discrimination。
   - interpolation / held-out pose generalization。
   - phase / geometry shift。
5. posterior-like distribution 定义：
   - score。
   - temperature / normalization。
   - calibration。
   - entropy。
   - margin。
6. consistency-as-confidence：
   - top-k overlap。
   - JS divergence。
   - conflict flag。
   - confidence score。
   - reject / low-confidence rule。
7. A/B 口径：
   - OCS_A independent photometric channel。
   - OCS_B image-derived OCS common-mode control。
   - 禁止混用规则。
8. F1/L1/F2/L2 形态字段：
   - F1 lower-bound baseline。
   - L1 main multi-observation vector。
   - F2 semi-oracle diagnostic。
   - L2 Future Work。
9. L1 quasi-static 假设与 Δθ 敏感性分析。
10. FIM/CRLB 降级-稳定-升级策略。
11. summary.json / per_attitude.csv / source_data.json 增量 schema。
12. 最小图表清单：
    - observability map。
    - entropy / ambiguity map。
    - consistency map。
    - conflict / reject cases。
    - mismatch boundary。
    - optional Δθ sensitivity。

## 8. 下一步 Claude 提示词

如果作者决定让 Claude 起草下一份指标规范，可直接使用以下提示词：

```text
请基于以下文件起草一份“v0.4 信息量与置信指标实现规范”：

必读：
1. CLAUDE.md
2. 00_只打开本文件夹时的启动说明.md
3. 00_v0.4总控流程.md
4. 24_v0.4项目论文主线最终冻结稿_OCS口径形态与mismatch账面对齐版.md
5. 25_v0.4主线冻结原因备案_为什么采用24号.md
6. 04_BlenderOCS方法重建/13_v0.4前向模型冻结规范_最终冻结版.md
7. 04_BlenderOCS方法重建/14_v0.4数据与manifest字段规范_最终冻结版.md
8. 05_全链路重跑/00_重跑任务清单.md
9. 97_交互审阅记录/01_Claude输出/Claude方案_v0.4主线三条软肋与解决办法_附FIM策略与投稿定位.md
10. 97_交互审阅记录/03_Codex审阅/05_全链路重跑/R02_Codex_复审_三条软肋与FIM投稿定位.md

任务：
起草一份代码实施前必须冻结的指标规范，建议文件名为：
05_全链路重跑/v0.4_信息量与置信指标实现规范_Claude候选.md

要求：
1. 不重写 13/14，不推翻前向模型冻结规范；只补足 24 号主线需要的反演输出、信息量、置信与一致性指标。
2. 明确区分 closed-grid candidate scoring 与 learned model evaluation。
3. 不直接把 2664 类 softmax 作为唯一主口径；列出 softmax、kNN likelihood、energy / distance-kernel score 的候选实现，并说明主口径选择条件。
4. 必须定义 posterior-like distribution、top-k candidates、entropy、margin、JS divergence、top-k overlap、consistency score、conflict flag、low-confidence / reject rule。
5. 必须定义 OCS_A independent photometric channel 与 OCS_B image-derived OCS common-mode control，禁止混用。
6. 必须定义 F1/L1/F2/L2 形态字段，其中 L1 为主线，F1 下界，F2 semi-oracle diagnostic，L2 Future Work。
7. 必须加入 L1 quasi-static / attitude-compensated 假设，并设计 Δθ 敏感性分析，但不得写成完整时域光变仿真。
8. FIM/CRLB 只写为可选升级层：离散指标保底，Fisher-like sensitivity 可选，正式 FIM/CRLB 需通过梯度稳定性验证后局部采用。
9. 给出 summary.json、per_attitude_results.csv/json、source_data.json 的增量 schema。
10. 给出最小图表与最小保存字段清单。
11. 投稿目标保持“以 文献/00投稿目标/ 中较高期刊为最终上探目标，越高越好；高目标牵引但不扩大 claim”，不要改成主攻 AST 或 Acta/ASR 默认优先。

输出只生成候选规范，不修改 24/25/13/14/启动集。
```

## 9. 一句话结论

Claude 方案方向有价值，但应“降火并入”：软肋 2 作为下一步指标规范的核心，软肋 1 作为 L1 假设与敏感性边界，软肋 3/FIM 作为可选理论增强；投稿目标仍按作者最新确认的高目标上探策略执行，不收窄为 AST 主攻，也不因冲高刊扩大 24 号主线之外的 claim。
