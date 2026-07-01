# R95 Codex 任务单：1C-B3 P0只读诊断与V0.3-V0.4协议对齐

最后更新：2026-06-29
执行设计端：Codex
执行端：Claude
性质：头B-B3 / P0 只读诊断任务单。本文只定义 Claude 下一步执行范围、输入、输出、红线和验收标准；不直接执行诊断、不放行训练、不放行新数据、不放行模型改正、不触发头A/头B大合并裁决。

## 0. 本轮裁决

```text
1. 93_1C-B2_方法总结与阶段门候选_Claude整合稿.md 已作为头B-B2 方法总结与阶段门候选接收。
2. 93 不再作为待 Codex 审阅稿，不再要求 Claude 对 93 返工。
3. 当前不触发头A/头B大合并裁决。
4. 当前进入头B-B3：P0 只读诊断与 V0.3/V0.4 协议对齐。
5. Claude 下一步只按本 R95 任务单执行，不自行扩展阶段门。
```

关键判断：头B尚未闭口。必须先完成 P0 只读诊断，再依据诊断结果决定是否逐项放行 P1-A 判据改正、P1-B 非朴素 fusion、P2 formal light-curve sequence。大合并裁决应等头B完成诊断与必要方法改进闭口后再做。

## 1. 上游依据

```text
总流程：
04_四路线分工区/00_总览与裁决/04_Codex审阅/
R05_Codex_当前任务顺序_按86两头并行与合并审阅执行.md

原始调度：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
86_后续路线结构_两头并行与合并审阅说明_Claude整理.md

头B-B1：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
R91_Codex_文献检索_1C-B1六方向方法约束与PDF入库.md

头B-B2：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
93_1C-B2_方法总结与阶段门候选_Claude整合稿.md

B2 收窄依据：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
R92_Codex_审阅_1C-B2文献方法总结与后续方法规划.md
R93_Codex_PDF精读确认_1C-B2相关方法可采纳性.md
R94_Codex_PDF补读筛选_1C-B2阶段门边界确认.md

头A收口依据：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
R90_Codex_审阅_1C-A3-FIX01通过_头A桥接材料稳定.md
```

93 的使用方式：作为头B-B2的已接收方法地图，用来约束 P0/P1/P2 的阶段顺序与论文叙事边界；不是放行文件，不等同于允许新训练或新数据。

## 2. Claude 输出文件要求

Claude 应输出：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
94_1C-B3_P0只读诊断与V0.3-V0.4协议对齐_Claude执行报告.md
```

输出性质：只读诊断执行报告。若某些输入文件缺失或路径无法确认，Claude 应列出缺口清单，不得用假设结果补齐。

## 3. 总目标

P0 的目的不是修复结果，而是定位 R04 负结果的主要来源，并保护 R04 负结果链的可复现性。

P0 应回答：

```text
1. V0.3 与 V0.4 差异主要来自 split、判据、数据形态、指标口径、模型能力，还是解释口径？
2. yaw-block 失败是否对应 OCS/image/joint 输入签名重叠？
3. exact-bin 0% 是否被严格分类判据放大？
4. naive early fusion 负结果是否只能否定 early concat，而不能否定 image 与 OCS 的所有互补可能？
5. 是否存在足够证据支持后续进入 P1-A、P1-B 或 P2？
```

## 4. 执行红线

Claude 本轮不得执行以下事项：

```text
不得训练模型。
不得新渲染。
不得生成新数据。
不得修改 split。
不得修改模型结构、loss、输出头、超参、seed。
不得改写 R04 代码、数据、成果链或历史结果。
不得改论文正文。
不得修改 CLAUDE.md。
不得触发头A/头B大合并裁决。
不得将 pseudo-light-curve probe 写成正式 light-curve experiment。
不得写 yaw 物理不可观测。
不得写 image 与 OCS 普遍不互补。
不得写 single-frame failed, so replaced by sequence。
```

允许事项：

```text
读取现有 md/csv/json/log/npz/npy/png/pdf 索引与成果文件。
整理现有结果表。
读取现有模型输出或 embedding 文件；若无现成 embedding，只能使用已有可导出的只读特征或列出缺口。
生成只读统计表、距离矩阵、诊断图和案例清单。
新增诊断报告与只读派生产物，但必须记录输入路径、输出路径和未触碰训练流程声明。
```

## 5. P0-1 protocol alignment

### 要回答的问题

V0.3/V0.4、random split/yaw-block、exact-bin/near-hit、fold/bin、指标口径是否一致？如果不一致，哪些差异可能解释 R04 负结果或前后叙事变化？

### 只读输入

Claude 应优先检索并列出实际使用的输入路径：

```text
R04 负结果链相关成果、报告、指标表、训练日志、评估日志。
V0.3/V0.4 相关 split、manifest、metrics、summary、result csv/json。
E45B/E45C/E45D 相关指标重构、图表与 SI 资产文件。
93、R92、R93、R94 中涉及口径收窄的条目。
```

### 分析方法

```text
1. 建立协议对齐表：
   项目 | V0.3口径 | V0.4口径 | 是否一致 | 影响范围 | 证据路径

2. 建立指标对齐表：
   指标 | 定义 | 分母/样本范围 | split/fold | 是否可横向比较 | 风险

3. 建立差异风险表：
   差异项 | 可能影响 | 是否足以解释 yaw-block 负结果 | 需后续验证
```

### 预期产出

```text
protocol_alignment_table.md 或 csv
metric_alignment_table.md 或 csv
protocol_risk_list.md
```

### 禁止事项

不得因口径差异直接宣布“恢复成功”或“旧结果无效”。只能写“可比较/不可比较/需谨慎比较/需后续阶段门验证”。

## 6. P0-2 signature distance

### 要回答的问题

yaw-block 失败是否对应不同 yaw 在 OCS-only、image embedding、joint embedding 中的签名近似重叠？

### 只读输入

Claude 应先查明是否存在现成：

```text
OCS 特征表或 OCS json/csv。
image-only embedding 或模型中间输出。
joint embedding 或 fusion 前后特征。
真实 yaw/pitch/fold/split 标注。
预测 yaw 或分类输出。
```

若没有现成 embedding，不得训练模型提取。可使用已保存的 logits、probability、summary feature、OCS 数值向量或报告“embedding 缺失，需后续单独阶段门/只读导出脚本”。

### 分析方法

```text
1. 对每类可用特征，按 yaw 聚合均值/中位数/样本级向量。
2. 计算 yaw-yaw 距离矩阵。
   可选距离：cosine、euclidean、correlation；需说明选择理由。
3. 分层检查 pitch、fold、split 是否改变低距离区域。
4. 输出最近邻 yaw 对与低距离簇。
```

### 预期产出

```text
signature_distance_method_table.md
ocs_yaw_distance_matrix.csv 或说明缺失
image_yaw_distance_matrix.csv 或说明缺失
joint_yaw_distance_matrix.csv 或说明缺失
distance_heatmap 路径清单
nearest_yaw_pairs.csv
```

### 判定口径

如果多个未见 yaw 弧段在输入签名空间中靠近已见 yaw 或彼此重叠，只能写“支持信息签名重叠/几何盲区解释”，不得写“yaw 物理不可观测”。

## 7. P0-3 confusion cluster

### 要回答的问题

R04 负结果是否集中在特定 yaw、pitch、fold、几何区域或近似等价解簇？

### 只读输入

```text
真实 yaw/pitch/fold。
预测 yaw/bin/logit/probability。
exact-bin、near-hit、circular metric 的现有结果。
错误样本或混淆矩阵。
```

### 分析方法

```text
1. 按 true yaw 与 predicted yaw 建立混淆表。
2. 按 pitch/fold 分层统计错误集中区域。
3. 找出高频混淆对、近似等价簇与代表样本。
4. 与 P0-2 的低距离 yaw 对交叉比对。
```

### 预期产出

```text
confusion_cluster_table.csv
confusion_cluster_map 路径清单
representative_failure_cases.md
distance_confusion_overlap_table.md
```

### 判定口径

若混淆簇与低距离簇高度重合，可写“更像输入签名/几何可辨识性不足”；若不重合，应保留“判据、模型容量、训练协议或输出头问题”的可能性。

## 8. P0-4 pseudo-light-curve probe

### 要回答的问题

在不生成新数据的前提下，把现有 yaw-ordered 单帧样本串联成伪序列，是否能观察到比单帧更清晰的可分性线索？

### 只读输入

```text
现有 yaw-ordered OCS 或亮度/OCS 相关输出。
固定 pitch 或近似固定几何条件下的样本。
yaw/pitch/fold/split 标注。
```

### 分析方法

```text
1. 只选择现有样本，不补点、不重渲染。
2. 固定 pitch/几何条件，按 yaw 排序串联。
3. 绘制 pseudo-light-curve 示例。
4. 做描述性比较：最近邻、曲线形态相似性、简单线性可分性或趋势可分性。
5. 明确其不等价于真实时间序列 light-curve。
```

### 预期产出

```text
pseudo_light_curve_probe_examples 路径清单
pseudo_sequence_similarity_table.csv 或 md
p2_entry_evidence_note.md
```

### 判定口径

若 probe 显示序列形态比单帧更可分，只能写“支持后续设计 P2 的价值”，不得写“已完成 light-curve experiment”。若 probe 仍不可分，应说明可能需要多几何、真实时间序列、噪声/BRDF建模或暂缓 P2。

## 9. P0 完成后的判定矩阵

Claude 执行报告必须给出以下矩阵：

| 诊断结果类型 | 主要证据 | 解释边界 | 下一步建议 |
|---|---|---|---|
| 协议/指标口径差异为主 | P0-1 | 只能说明不可直接横比或需重算口径 | 先修正报告口径或设计只读重算 |
| exact-bin 判据放大为主 | P0-1/P0-3 | 不等于模型完全失败 | 申请 P1-A 连续/圆周角度判据阶段门 |
| 输入签名重叠为主 | P0-2/P0-3 | 不等于 yaw 物理不可观测 | 申请更强可观测性诊断或 P2 前置设计 |
| yaw 几何盲区为主 | P0-2/P0-3/P0-4 | 限于当前 fixed-roll、当前采样协议 | 设计多几何/序列层证据门 |
| naive fusion 不足为主 | P0-2/P0-3 | 只能否定 early concat | 申请 P1-B late/decision/model-bank fusion 阶段门 |
| 模型容量不足为主 | P0-3 与距离不重合 | 不能直接通过堆模型解决 | 先定义独立模型容量阶段门 |
| 单帧信息源不足 | P0-2/P0-4 | 不能写 single-frame failed, so replaced by sequence | 满足条件后申请 P2 formal light-curve sequence |

## 10. 后续阶段门关系

```text
P1-A 连续/圆周角度判据改进：
  必须等 P0 证明 exact-bin 或分类判据可能放大失败后，另设 C 类阶段门。

P1-B 非朴素 fusion：
  必须等 P0 显示 naive early concat 不足或模态互补仍有可能后，另设 C 类阶段门。

P2 formal light-curve sequence：
  必须等 P0/P1 证明单帧信息层不足且 sequence 增益有证据后，另设重阶段门。

P3 不确定性/置信：
  暂缓。若信息源与判据未升级，单独做 calibration/conformal 的论文增益有限。

头A/头B大合并裁决：
  暂缓。等头B完成 P0、必要 P1、是否进入 P2 的判断并形成闭口点后，再与头A合并裁决。
```

## 11. Claude 执行报告格式

Claude 输出的 `94_1C-B3...` 至少包含：

```text
1. 执行摘要
2. 输入文件清单与缺口清单
3. P0-1 protocol alignment 结果
4. P0-2 signature distance 结果
5. P0-3 confusion cluster 结果
6. P0-4 pseudo-light-curve probe 结果
7. P0 判定矩阵
8. 是否建议申请 P1-A / P1-B / P2 的证据说明
9. 未触碰训练、split、模型、数据生成、R04链的自查声明
10. 给 Codex/作者的待确认问题
```

如无法完成某个模块，必须说明：

```text
缺失输入是什么；
它位于哪个预期目录或应由谁确认；
本轮是否可用替代只读特征；
是否需要后续单独阶段门。
```

## 12. 给 Claude 的最短提示词

用户可直接把下面一段交给 Claude：

```text
请严格按 Codex R95 任务单执行：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R95_Codex_任务单_1C-B3_P0只读诊断与V0.3-V0.4协议对齐.md

输出：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/94_1C-B3_P0只读诊断与V0.3-V0.4协议对齐_Claude执行报告.md

只做 P0 只读诊断，不自行设计新阶段门，不训练、不新渲染、不生成新数据、不改 split、不改模型、不改 loss/输出头/超参/seed、不覆盖 R04 结果链、不改论文正文、不改 CLAUDE.md、不触发头A/头B大合并裁决。
```

## 13. Codex 验收口径

R95 的验收不看 Claude 是否给出“好结果”，只看：

```text
1. 是否完整记录输入文件和缺口。
2. 是否完成 P0-1 到 P0-4 的只读诊断或说明无法完成的原因。
3. 是否把诊断结果映射到 P1-A/P1-B/P2 的阶段门建议。
4. 是否保护 R04 负结果链。
5. 是否避免越界 claim。
6. 是否明确当前不是大合并裁决。
```

