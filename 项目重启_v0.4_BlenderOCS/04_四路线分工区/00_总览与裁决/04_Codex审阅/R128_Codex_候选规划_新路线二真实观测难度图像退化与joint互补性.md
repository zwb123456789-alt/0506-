# R128 Codex 候选规划：新路线二真实观测难度图像退化与 joint 互补性

最后更新：2026-07-01  
性质：候选路线规划，供作者审阅  
状态：**不改目录结构，不移动原路线二/三，不放行新实验，不更新 CLAUDE.md。**

## 0. 本文件目的

作者提出：在路线一 C 与三轴小项目之后，新增一个优先路线二，主题为：

```text
将图像退化到更接近真实观测难度，
重新检验 OCS 与图像的 joint 互补性，
并探索比 early concat 更聪明的图像-光度联合对比方法。
```

同时，原路线二“GEO 真实光度锚点”和原路线三“暗室缩比独立验证”暂不删除，候选顺延到后续位置。本文只做规划梳理与可行性审阅，不执行结构调整。

## 1. 候选路线定位

建议新路线二暂命名为：

```text
路线二：真实观测难度图像退化与 OCS-image 互补性验证
```

一句话定位：

```text
在路线一 C 已证明 L1 多几何 OCS 具有姿态可观测性、三轴小项目给出高信息/低信息姿态与观测规划后，
进一步把图像通道压到有真实依据的观测难度区间，
检验 OCS 是否能在图像不再近饱和时提供可测的互补增益，
并建立更合理的图像-光度联合推断方法。
```

它不是：

```text
真实未知目标姿态反演系统；
真实望远镜验证已经完成；
强行把图像打残以制造 joint 增益；
把 image-derived patch 光度混写为 independent OCS；
替代 GEO 真实光度锚点或暗室验证。
```

## 2. 为什么需要这条新路线

路线一 C 当前已经形成清晰边界：

```text
1. OCS-only L1-G1/G3/G5 多几何总光度向量在 P-INT 下有稳定单调增益。
2. clean 与 degraded-severe 下 image_only 仍接近饱和。
3. joint 相对 image_only 的 hit@30 增量很小，强互补性不能宣称已证明。
4. P-EXT yaw-block 外推仍坍缩。
```

因此当前 joint 互补性未被证明，不一定是 OCS 没价值，也可能是：

```text
当前图像通道太理想；
P-INT 内插协议让 image_only 太接近天花板；
early concat 融合方式太弱；
缺少真实观测难度约束；
缺少局部/部位级图像光度与全局 OCS 的结构化对比。
```

新路线二的核心价值是把问题从：

```text
joint 为什么没赢 image_only？
```

转为：

```text
在什么真实图像退化条件下，OCS 才从“单独有信息”变成“对图像真正互补”？
如果互补仍不成立，失败边界在哪里？
```

## 3. 与三轴小项目的关系

建议执行顺序仍保持：

```text
路线一 C -> 三轴小项目 -> 新路线二
```

原因：

```text
三轴小项目负责在 yaw/pitch/roll 空间中找最亮构型、高信息姿态、低信息区域和观测规划。
新路线二可以优先选择三轴小项目输出的高信息/低信息/易混淆姿态区域作为真实退化与 joint 互补性测试集。
```

三轴小项目提供：

```text
1. 哪些姿态/几何组合最亮或最暗。
2. 哪些姿态虽然亮但信息量低。
3. 哪些姿态最易混淆。
4. 哪些几何值得观测，哪些不值得。
```

新路线二接收这些区域后进一步问：

```text
真实观测难度下，图像在这些区域是否失效？
OCS 多几何向量是否能救回图像失效区域？
局部图像光度结构和独立 OCS 是否能形成更强一致性/冲突判据？
```

## 4. 三个核心研究目标

### 4.1 目标一：真实观测难度图像退化

从路线一 C 的 clean / severe 仿真退化，升级为有真实依据的观测难度模型。

候选退化因素：

```text
低分辨率 / 小目标像素尺度；
seeing-like PSF / 光学系统 PSF；
曝光时间与运动拖影；
背景天空、星点、杂散光、梯度背景；
shot noise / read noise / 量化噪声；
饱和 / blooming / gain-offset；
目标尺度、中心定位和裁剪误差；
BRDF / glint / phase mismatch；
真实相机动态范围与 FITS 统计。
```

最低要求：

```text
退化参数必须尽量来自真实 FITS、相机说明、GEO 数据统计或暗室/望远镜经验范围；
至少设计 mild / realistic / severe 三档；
不得只靠主观调参制造 joint 增益。
```

### 4.2 目标二：重新检验 joint 互补性

评价目标从“joint 是否比 image_only 高一点”升级为：

```text
当 image_only 从饱和区下降到可测困难区间时，
joint 是否稳定超过最佳单通道；
OCS 是否能救回 image-hard / ambiguity-hard / low-resolution-hard 子集；
joint 增益是否随退化强度呈合理变化；
OCS-image disagreement 是否能提示失败或低置信。
```

建议指标：

```text
best single vs joint delta；
image-hard subset recovery；
OCS-hard / image-hard / disagreement-hard 分层；
oracle single-channel vs oracle joint；
top-k overlap / JS divergence；
risk-coverage / selective prediction；
conformal set_size 与 coverage；
per-attitude rescue map；
failure region map。
```

可接收结论分三档：

```text
强正向：realistic 档下 joint 稳定优于最佳单通道，且主要救回 image-hard 区域。
中性：只有 severe 或人为困难档下 joint 增益明显，说明互补性存在但现实窗口有限。
负向：真实依据退化下 image 仍近饱和或 joint 无增益，说明当前 OCS 更适合作为可观测性/置信边界而非强融合增益来源。
```

### 4.3 目标三：探索更聪明的 joint 方法

不应只依赖 early concat。建议分层探索：

#### A. Posterior-level fusion

```text
image branch 输出候选姿态分布；
OCS branch 输出候选姿态分布；
在同一姿态网格上做 score-level / posterior-like fusion；
分析 top-k overlap、JS divergence、entropy 与 error 的关系。
```

优点：直接服务 24 号的 consistency-as-confidence 主线。

#### B. Consistency gating / reject option

```text
image 与 OCS 一致且分布集中 -> 高置信；
image 高置信、OCS 低置信 -> 图像主导但保留 OCS 不可观测标记；
OCS 高置信、image 低置信 -> 可能是图像退化下的 OCS 救回；
二者高冲突 -> 拒识、降置信或触发 mismatch 检查。
```

优点：即使 joint 不提高平均精度，也可能提高“什么时候该相信”的能力。

#### C. Patch / mosaic photometry

```text
将真实难度图像分成若干块；
提取每块局部亮度、局部对比和空间亮度分布；
与仿真中对应姿态/几何的局部投影亮度模式比较；
用块级光度结构辅助姿态候选排序。
```

注意：patch photometry 来自图像，因此属于 image-derived local photometry，不是 independent OCS。它的价值是构造图像内部的“空间-光度结构”对比，而不是替代独立光度通道。

#### D. Part-aware photometric matching

```text
若模糊图像仍能粗分主体、太阳翼或高亮区域，
比较部位/区域相对亮度、亮斑位置、亮暗比例与仿真预测；
将其作为姿态候选过滤或重排序依据。
```

注意：真实图像中按部位分割未必可靠；若使用分割，应先作为 semi-oracle / diagnostic 或弱监督模块，不能直接写成可运营输入。

#### E. Independent OCS + image-derived photometry A/B 对照

```text
OCS_A：独立非成像光度通道，多几何总光度向量。
OCS_B：从退化图像中提取的总光度或局部光度。
```

对照问题：

```text
OCS_A 是否在图像退化时保留独立信息？
OCS_B 是否与 image 共享 common-mode failure？
OCS_A 与 patch photometry 是否能共同诊断图像退化或姿态混淆？
```

## 5. 数据与现实依据

这条路线是否站得住，关键在“真实观测难度”不能凭空设定。

可用依据：

```text
GEO 数据库 FITS 图像：目标像素尺度、背景、SNR、饱和、星点、动态范围。
DET/IPD 测光表：真实光度范围和噪声统计。
PRE 几何表：真实 sun/view 几何分布。
相机系统说明：口径、视场、分辨率、帧率、量化位数。
暗室/望远镜样例：PSF、曝光、模糊、成像链经验范围。
```

必须保持的边界：

```text
GEO 数据库无三轴姿态真值，不能做真实监督姿态反演。
真实 FITS 可用于退化参数标定、图像难度统计、光度/背景分布锚定。
真实光度可用于趋势和分布锚定，不能直接验证姿态真值。
```

## 6. 推荐阶段门设计

### Phase 0：真实图像难度审计

目标：

```text
从真实 FITS 或数据库说明中统计目标尺寸、SNR、背景、动态范围、星点、饱和、PSF 近似范围。
输出 realistic degradation parameter card。
```

输出：

```text
real_image_difficulty_audit.md
realistic_degradation_parameter_card.csv
fits_statistics_summary.csv
allowed_forbidden_realism_claims.md
```

### Phase 1：退化模型构建与 sanity check

目标：

```text
把路线一/三轴图像退化到 mild/realistic/severe 三档；
确认退化后图像不是人为不可见，也不是仍过于理想。
```

输出：

```text
degradation_model_spec.md
degradation_visual_panel.png/.pdf
image_quality_metrics.csv
```

### Phase 2：baseline 互补性矩阵

目标：

```text
在 realistic degradation 下训练/评估 image_only、ocs_only、early_joint、posterior_fusion、consistency_gating。
```

输出：

```text
channel_comparison_metrics.csv
joint_increment_by_difficulty.csv
rescue_map_image_hard.csv
failure_region_map.png/.pdf
```

### Phase 3：patch / part-aware 方法试验

目标：

```text
在三轴小项目输出的高信息/低信息/易混淆区域中，
测试 patch photometry 或 part-aware matching 是否能改善候选排序或置信判断。
```

输出：

```text
patch_photometry_features.csv
patch_vs_global_ablation.csv
partaware_matching_smoke.md
```

### Phase 4：真实数据接口检查

目标：

```text
不做真实姿态反演成功率；
只检查真实 FITS 的退化统计、真实光度分布和真实几何覆盖是否支持路线二设定。
```

输出：

```text
real_data_interface_report.md
simulated_vs_real_image_difficulty_table.csv
simulated_vs_real_photometry_distribution_table.csv
```

## 7. 可能的路线顺序调整候选

若作者审阅后决定采纳，可将当前路线顺序候选改为：

```text
路线一 C：fixed-roll / L1 多几何 OCS 可观测性主干（已闭口）
三轴小项目：最亮构型、高信息姿态、低信息区域、观测规划（下一步）
新路线二：真实观测难度图像退化与 OCS-image joint 互补性
原路线二顺延为路线三：GEO 真实光度锚点
原路线三顺延为路线四：暗室缩比独立验证
原路线四顺延为路线五：LEO 光学特性与姿态运动未来方向
```

本文件不执行上述调整。若采纳，需另行由 Codex 生成结构调整裁决与入口文件修订清单，经作者确认后再改目录或总览。

## 8. 可行性审阅

Codex 初步判断：**可行，且值得作为小项目后的优先路线。**

理由：

```text
1. 它直接回应 R125/R127 的核心未闭口问题：joint 强互补性尚未证明。
2. 它不否定路线一 C，反而利用路线一 C 的 OCS 正结果和三轴小项目的可观测性地图。
3. 它能回应专家关于仿真真实性和真实图像观测难度的质疑。
4. 它把“图像太强导致 joint 没空间”转化为一个可验证的科学问题。
5. 它能自然连接后续 GEO 真实数据和暗室验证，但不要求它们提供姿态真值。
```

主要风险：

```text
1. 真实退化参数不足，路线会被质疑为人为造难题。
2. image-derived patch photometry 与 independent OCS 容易混写，必须严格标注口径。
3. 如果 realistic 档图像仍近饱和，joint 仍可能没有显著增益。
4. 如果 severe 档才有 joint 增益，结论只能写成互补性窗口有限。
5. 若引入 part-aware 分割，分割真值或部位对应会带来 semi-oracle 风险。
```

## 9. 建议写作口径

可写：

```text
We further evaluate OCS-image complementarity under realistic image-degradation regimes calibrated from real observation statistics.
```

```text
The goal is not to demonstrate field-ready pose inversion, but to identify when an independent multi-geometry photometric vector can rescue or qualify degraded image-based estimates.
```

```text
Patch-level image photometry is treated as an image-derived structural cue, while independent OCS remains a separate non-imaging photometric channel.
```

禁写：

```text
真实观测图像 + OCS 已完成姿态反演验证。
真实 GEO 数据证明 joint 反演成功率。
patch 光度就是 independent OCS。
人为强退化下的 joint 增益等同于真实工程互补性。
part-aware 光度可作为真实可运营部件 OCS 输入。
```

## 10. 下一步建议

作者若认可本规划，建议下一份文件不是直接改目录，而是先生成：

```text
R129_Codex_任务单_三轴小项目准备阶段门设计.md
```

三轴小项目完成后，再生成：

```text
Rxxx_Codex_任务单_新路线二Phase0真实图像难度审计.md
```

若作者希望先冻结路线顺序，则应另行生成：

```text
Rxxx_Codex_裁决_路线顺序调整候选采纳与目录修订清单.md
```

在作者确认前，不改目录结构，不移动原路线二/三，不同步 `CLAUDE.md`。

---

## 11. 待办记忆：三轴小项目完结后回看 R128 与路线结构调整

本节用于明确记录：**R128 及其对应的潜在路线结构调整当前只作为记忆保留，不在本轮执行。**

当前必须记住的候选文件是：

```text
04_四路线分工区/00_总览与裁决/04_Codex审阅/
R128_Codex_候选规划_新路线二真实观测难度图像退化与joint互补性.md
```

当前必须记住的候选结构调整是：

```text
路线一 C：fixed-roll / L1 多几何 OCS 可观测性主干（已由 R125/R127 闭口）
三轴小项目：最亮构型、高信息姿态、低信息区域、观测规划（下一步先执行）
候选新路线二：真实观测难度图像退化与 OCS-image joint 互补性
原路线二顺延为候选路线三：GEO 真实光度锚点
原路线三顺延为候选路线四：暗室缩比独立验证
原路线四顺延为候选路线五：LEO 光学特性与姿态运动未来方向
```

当前执行规则：

```text
1. 现在不改目录结构。
2. 现在不移动原路线二/三/四。
3. 现在不修改 CLAUDE.md、四路线总览或路线冻结文件来采纳该结构。
4. 现在不启动新路线二 Phase 0，不做真实图像难度审计。
5. 当前下一步仍是三轴小项目准备阶段门设计与执行。
```

触发回看条件：

```text
三轴小项目完成并经 Codex 审阅通过后，
必须回看本 R128 文件，
再裁决是否采纳“新路线二真实观测难度图像退化与 joint 互补性”为下一优先路线。
```

届时需要生成的文件候选：

```text
Rxxx_Codex_裁决_三轴小项目后路线结构调整_R128候选采纳或搁置.md
Rxxx_Codex_任务单_新路线二Phase0真实图像难度审计.md
```

届时需要裁决的问题：

```text
1. 三轴小项目是否已经提供高信息/低信息/易混淆姿态区域，足以支撑新路线二测试集选择？
2. 是否采纳新路线二作为三轴小项目后的优先路线？
3. 是否正式顺延原路线二/三/四，并修改目录、总览、CLAUDE.md 和相关冻结文件？
4. 是否先做 Phase 0 真实图像难度审计，再决定后续 joint 互补性矩阵？
5. 若真实 GEO/FITS 图像不可分辨，是否将新路线二降级或改写为点源/光度时序难度审计，而不是分辨图像 joint 路线？
```

一句话记忆：

```text
R128 是三轴小项目完成后的路线结构调整候选入口；
现在只记住，不执行。
```

---

## 附录 A：Claude 执行端反馈清单（作者豁免下追加）

说明：本附录由 Claude 在作者明确豁免 `CLAUDE.md` 1.1 节（Claude 输出不写入 `04_Codex审阅/`、不改 `Rxx_Codex` 命名文件）的前提下追加。内容为执行端对 R128 候选规划的反馈，不是 Codex 裁决，也不放行任何实验；正式任务单仍应由 Codex 另行下达。

### A.1 总体判断

作为方向规划：清晰且立得住。动机直接咬住 R125/R127 唯一未闭口问题（joint 强互补性未证明），边界干净（image-derived patch ≠ independent OCS），Phase 0–4 结构合理，可接收结论分强正向/中性/负向三档。认可"可行且值得优先"。

作为可执行技术路线：尚未到"清晰"，存在以下四个缺口。

### A.2 缺口一：Phase 0 缺 kill/branch 判据，且未正面处理 GEO 真实成像可分辨性前提

整条路线的合法性压在"退化参数来自真实依据"，这也是最可能拿不到数据的一环。更根本的问题：真实 GEO 目标在多数地基观测下欠分辨甚至近点源。若 Phase 0 审计出的真实图像难度是"目标仅几个像素/近点源"，则路线一 C 中"image_only 近饱和"的仿真前提无法映射到真实——不是"把好图像退化到真实难度"，而是"给一个本不存在分辨成像的场景硬造分辨图像通道"。

建议：Phase 0 必须显式给出 kill/branch 判据——若真实成像根本不可分辨，image 通道定义需重设（例如降级为点源光度/时序，而非分辨图像）。

### A.3 缺口二：循环论证风险只提名未给防护协议

第 8 节把"人为造难题"列为头号风险，但全文唯一防护是"参数来自真实 FITS"。缺两项：
- 退化档位（mild/realistic/severe 物理参数）必须**预注册**：先定参数再看 joint，不得反向调到 joint 赢为止。
- **主指标 + 阈值预注册**：现"强正向/中性/负向"三档只有定性描述，无量化边界，事后易被质疑为 p-hacking。

### A.4 缺口三：方法探索 4.3 一次摆五种（A–E），无优先级与取舍判据

五个方向不是一条路线，全做会使 Phase 2/3 失控。建议明确优先级：
- 优先：B（consistency gating）+ posterior fusion（A）——B 最贴 24 号 consistency-as-confidence 主线，与已有 conformal 证据链最连贯。
- 条件触发/后置：C（patch）、D（part-aware）、E（OCS_A/B 对照）——D/E 带分割 semi-oracle 风险，最该延后并严格标口径。

### A.5 缺口四：前置链是"未完成叠未完成"

本路线依赖三轴小项目输出的高信息/低信息/易混淆区域，而三轴小项目本身尚未设计、未执行。故现在展开 Phase 2/3 细节意义有限。

### A.6 顺序建议

同意 R128 第 10 节：下一份应落地的是 `R129_Codex_任务单_三轴小项目准备阶段门设计`，本路线 Phase 0 待三轴小项目完成后再启动。R128 作为"后续优先路线候选"挂起即可。这与 CLAUDE.md 当前红线及 R127"进入三轴小项目准备阶段门设计"一致。
