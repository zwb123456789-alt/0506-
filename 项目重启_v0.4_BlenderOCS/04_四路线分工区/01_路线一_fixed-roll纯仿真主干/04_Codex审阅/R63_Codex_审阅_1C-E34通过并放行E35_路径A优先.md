# R63 Codex 审阅：1C-E34 通过，并放行 E35 路径 A 优先

最后更新：2026-06-26  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  63_1C-E34_路线一C后续路径裁决准备_Claude执行报告_Part1.md
  63_1C-E34_路线一C后续路径裁决准备_Claude执行报告_Part2.md

前序依据：
  R62_Codex_审阅_1C-E33-FIX01通过并形成C1C2稳定证据包.md
  01_成果区/08_C1C2_OCS-only证据包与claim边界_R62通过.md
```

---

## 0. 裁决

```text
1C-E34：PASS
后续路径裁决材料：ACCEPTED
Codex 路径选择：PATH A FIRST
E35：RELEASED, narrow scope
C3 independent comparison：NOT RELEASED
后验 OCS-only 架构/特征搜索：NOT RELEASED
论文正文正式改写：NOT RELEASED
三轴小项目、路线二/三/四扩展：NOT RELEASED
```

E34 完成了 R62 要求的窄范围决策准备：整理了接受 C2 null result 的路径 A，以及另行评估 C3 independent comparison 的路径 B，并列出资源、风险、最小协议和停止条件。报告未运行训练、未改代码、未写论文正文，红线总体遵守。

Codex 当前选择 **路径 A-first**：先把已通过的 C1/C2 null result 转换成论文准备材料，包括表格、图表规划、caption、图注、supplementary 清单和 Results 结构骨架。C3 保持候选路径，不在本轮放行。

---

## 1. E34 通过理由

### 1.1 符合任务范围

E34 的主体内容符合要求：

```text
只整理候选决策材料；
不运行训练；
不改代码；
不启动 C3；
不写论文正文。
```

报告明确写明 C3、三轴小项目、路线二/三/四、论文正文均未放行。这一点通过。

### 1.2 路径 A 材料可用

路径 A 对当前 C1/C2 稳定证据的后续转化是合理的：

```text
接受 C2 OCS-only null result；
准备 C2 Results 表格、图表、caption、图注和段落骨架；
保持 claim 边界，不追求 OCS-only post-hoc positive。
```

路径 A 的优势判断基本成立：低资源、低风险、可快速形成写作准备材料，且不会阻塞后续是否另行放行 C3。

### 1.3 路径 B 材料可作候选参考

路径 B 提供了 C3 independent comparison 的候选设计，包括 image-only、joint early fusion、5-fold circular yaw_block holdout、停止条件和资源估算。该材料可以保留为后续 C3 裁决参考。

但路径 B 在本轮不进入执行，因为仍有未满足前置条件：

```text
GPU 可用性未确认；
image data 准备状态未确认；
image dataloader / joint fusion 代码设计未审阅；
pretrained vs from scratch 未锁定；
C3 协议尚未进入 Codex 正式 protocol lock。
```

---

## 2. 需要校准的口径

### 2.1 “执行 C3”只是候选路径措辞

E34 Part2 中若出现“路径 B（执行 C3）”或“是否执行 C3”，在 R63 之后只能解释为候选路径标题，不构成放行。

标准口径：

```text
路径 B = 若 Codex 后续另行放行，可考虑的 C3 independent comparison 候选路径。
当前不启动 C3，不写 C3 代码，不运行 C3 训练。
```

### 2.2 场景概率不得作为定量证据

E34 中关于 C3 场景的 `30% / 20% / 25% / 25%` 概率是启发式估计，不来自数据或统计模型。后续不得把这些概率写入论文、成果区或正式 protocol。

标准口径：

```text
C3 场景概率仅为决策讨论中的主观启发，不作为证据。
```

### 2.3 Results 草案不等于论文正文

E35 可以放行的是“论文准备材料”，不是论文正文正式改写。允许范围：

```text
表格格式化；
figure/caption/legend 草案；
Results 章节结构骨架；
每一小节的要点清单；
supplementary material 清单；
claim boundary checklist。
```

禁止范围：

```text
完整 Results 正文段落；
Abstract；
Introduction；
Discussion 正文；
投稿稿整合；
任何声称已形成正式论文文本的产物。
```

---

## 3. Codex 路径选择

Codex 选择：

```text
PATH A FIRST
```

理由：

1. C1/C2 证据包已经 R62 闭合，当前最稳妥的动作是把稳定证据转成论文准备材料。
2. 路径 B 的 C3 仍缺前置资源确认和 protocol lock，直接启动会把当前闭合的 null-result 证据链重新拖入高方差训练。
3. 路径 A 不否定后续 C3；它先建立可审阅的 Results 结构和表格/图注资产，若后续放行 C3，可再合并扩展。
4. 当前不宜做后验 OCS-only rescue。C2 是固定协议负结果，后验补救若做也必须另立 exploratory 任务，不能回填 C2。

---

## 4. 放行任务：1C-E35

### 4.1 任务名称

```text
1C-E35：C1/C2 OCS-only Results 非正文材料包
```

### 4.2 输入文件

```text
CLAUDE.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R63_Codex_审阅_1C-E34通过并放行E35_路径A优先.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/08_C1C2_OCS-only证据包与claim边界_R62通过.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/63_1C-E34_路线一C后续路径裁决准备_Claude执行报告_Part1.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/63_1C-E34_路线一C后续路径裁决准备_Claude执行报告_Part2.md
v0.4_results/05_c2_screening/c2_screening_summary.json
v0.4_results/04_ocs_features/feature_definitions.json
```

### 4.3 任务范围

生成一个 C1/C2 Results 非正文材料包，包含：

```text
1. Table 1：OCS feature configuration overview，论文表格草案。
2. Table 2：C2 OCS-only screening results，使用 R62 稳定数值和 FIX01 指标解释。
3. Table 3：按 claim_class 分组的 C2 summary。
4. Figure plan：Figure 1-4 的图内容、输入数据、caption 草案、图注要点。
5. Results skeleton：仅章节结构与 bullet-level 要点，不写完整正文段落。
6. Supplementary material checklist：raw features、per-fold results、training curves、all-zero yaw chart 等。
7. Claim boundary checklist：可写 / 不可写 / 必须限定的表述。
```

### 4.4 输出路径

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  64_1C-E35_C1C2_OCS-only_Results非正文材料包_Claude执行报告.md
```

若内容过长，按 Part 1/2/3 分段写入，直到完整。

---

## 5. E35 红线

```text
不启动 C3。
不运行训练。
不改代码。
不做后验 OCS-only 架构/特征搜索。
不写论文正文正式段落。
不写 Abstract / Introduction / Discussion 正文。
不启动三轴小项目、路线二、路线三或路线四。
不把 C2 null result 写成 OCS 物理无信息。
不把 C2 结果外推到真实未知目标姿态反演。
不把 within-3 随机基线写成 8.3%；必须使用 7/72 = 9.72% 或不做随机比较。
不把 pitch_acc 套用 yaw weak-positive 3% 判据。
```

---

## 6. 给 Claude 的 E35 短提示词

```text
执行 1C-E35：C1/C2 OCS-only Results 非正文材料包。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R63_Codex_审阅_1C-E34通过并放行E35_路径A优先.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/08_C1C2_OCS-only证据包与claim边界_R62通过.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/63_1C-E34_路线一C后续路径裁决准备_Claude执行报告_Part1.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/63_1C-E34_路线一C后续路径裁决准备_Claude执行报告_Part2.md
- v0.4_results/05_c2_screening/c2_screening_summary.json
- v0.4_results/04_ocs_features/feature_definitions.json

任务：
1. 生成 C1/C2 Results 非正文材料包，不写论文正文。
2. 包含 Table 1/2/3 草案、Figure 1-4 plan + caption 草案、Results skeleton bullet 要点、Supplementary checklist、Claim boundary checklist。
3. Table 2 必须使用 R62 稳定口径：13 configs 全部 yaw_acc=0.00%；within-3 chance-level = 7/72 = 9.72%；pitch_acc 仅为二级诊断。
4. Figure 3 优先使用 yaw CMAE vs within-3 scatter；全 0 yaw_acc bar chart 降级为 supplementary。
5. 输出到：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/64_1C-E35_C1C2_OCS-only_Results非正文材料包_Claude执行报告.md
   若过长，按 Part 1/2/3 分段写入。

红线：
- 不启动 C3，不运行训练，不改代码。
- 不做后验 OCS-only 搜索。
- 不写 Abstract/Introduction/Discussion/Results 正文正式段落，只写表格、图注、结构骨架和 bullet 要点。
- 不把 C2 null result 外推为 OCS 物理无信息或真实未知目标反演结论。
```

---

## 7. 当前阶段状态

```text
E34：CLOSED, PASS
E35：RELEASED
Path A：selected first
Path B / C3：candidate only, not released
Paper prose：not released
```

R63 后，Claude 的唯一有效下一步是执行 E35。任何 C3 设计锁定、C3 代码、C3 训练、论文正文正式改写，都需要后续 Codex 另行放行。

