# R62 Codex 审阅：1C-E33-FIX01 通过，并形成 C1/C2 稳定证据包

最后更新：2026-06-26  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  62_1C-E33-FIX01_判据基线与C3边界修正_Claude执行报告.md

前序依据：
  R61_Codex_审阅_1C-E33需FIX01_判据基线与C3边界修正.md
  61_1C-E33_C1C2证据包与claim边界整理_Claude执行报告_Part1.md
  61_1C-E33_C1C2证据包与claim边界整理_Claude执行报告_Part2.md
  v0.4_results/05_c2_screening/c2_screening_summary.json
```

---

## 0. 裁决

```text
1C-E33-FIX01：PASS
C1/C2 证据包：PASS WITH FIX01 CORRECTIONS
C2 OCS-only null result：ACCEPTED AS STABLE EVIDENCE
成果区稳定证据包：RELEASED
C3 joint 复验：NOT RELEASED
后验 OCS-only 架构/特征补救：NOT RELEASED
论文正文正式改写：NOT RELEASED
三轴小项目、路线二/三/四扩展：NOT RELEASED
```

E33-FIX01 已按 R61 要求修正三个 Major 问题和一个 Minor 图表规划问题。修正后的 E33 证据包可以作为路线一 C 当前阶段的稳定成果进入 `01_成果区/`，但其权威口径必须以 FIX01 修正后的表述为准。

---

## 1. FIX01 审阅结论

### 1.1 within-3-bins 随机基线

R61 要求将原先的 `8.3%` 随机基线修正为：

```text
72-bin yaw grid 下，若 within-3-bins 按 circular distance <= 3 且包含 exact bin 计算，
chance-level = 7 / 72 = 9.72%。
```

FIX01 已完成该修正，并把 `within-3-bins rate = 2.75%-15.57%` 重新解释为局部 coarse localization 信号，而不是 exact-bin yaw success。该解释通过。

注意：后续写作不得再笼统写“略高于随机 8.3%”。若提及随机基线，必须写 `9.72%`；若不想引入随机比较，也可以只写 within-3 显示局部邻域聚集但未转化为 exact-bin yaw accuracy。

### 1.2 pitch_acc 解释

R61 要求删除将 `pitch_acc` 套用 C2 yaw weak-positive `3%` 判据的表述。

FIX01 已改为：

```text
Pitch exact-bin accuracy 仅作二级诊断指标；部分配置达到约 3-4%，
但 C2 成败判据由跨 yaw holdout 泛化决定，这些 pitch 值不改变 C2 null result。
```

该修正通过。后续写作中 pitch 可以作为辅助现象呈现，但不得作为 C2 通过/不通过的主判据。

### 1.3 C3 边界

R61 要求删除 Claude “推荐放行 C3”的阶段门口吻。

FIX01 已将 C3 改写为：

```text
若 Codex 另行放行 C3，可采用的候选最小对照设计；
当前 C3、三轴小项目、路线二/三/四、论文正文均未放行。
```

该修正通过。C3 论证框架可以保留为候选设计材料，但不得视作已放行实验，也不得由 Claude 自动进入训练或代码修改。

### 1.4 图表规划

R61 的 Minor 建议是将 13 个全 0 的 yaw_acc bar chart 降级。

FIX01 已将全 0 bar chart 降级为 Supplementary 或并入表格，并建议正文优先使用 `yaw_cmae` vs `within-3` scatter 或 grouped summary。该调整通过。

---

## 2. 稳定证据口径

### 2.1 C1

C1 预注册与配置完整性可以作为稳定证据保留：

```text
C1：14 个配置完成预注册完整性验证。
C2：其中 13 个配置进入正式 OCS-only 筛选。
```

### 2.2 C2

C2 稳定结论为：

```text
13 configs x 5 folds = 65 runs
fixed_protocol_no_hyperparam_search
all mean_test_yaw_acc = 0.00%
all mean_test_yaw_correct_count = 0
```

分组结论为：

```text
photometric OCS：null
visibility control：null
mixed OCS+visibility：null
```

补充诊断：

```text
yaw within-3-bins rate：2.75%-15.57%，chance-level = 9.72%
pitch exact-bin accuracy：2.56%-4.37%，secondary diagnostic only
```

C2 判定：

```text
在 phase63 fixed-roll circular yaw-block holdout 与固定 MLP 协议下，
当前低维 OCS-only / visibility / mixed non-image features 未达到跨 yaw exact-bin 泛化。
```

---

## 3. 可写与不可写边界

### 3.1 可写

后续论文 Results / Discussion 候选表述可以写：

```text
Under the preregistered fixed MLP protocol and circular yaw-block holdout,
all 13 OCS-only feature configurations yielded 0.00% exact-bin yaw accuracy
across five folds.
```

中文口径：

```text
在预注册固定协议与 circular yaw-block holdout 下，13 个 OCS-only 低维特征配置在 5-fold 筛选中均未取得 exact-bin yaw 泛化命中，构成受控负结果。
```

### 3.2 不可写

不得写成：

```text
OCS 光度在物理上不含姿态信息。
OCS 在所有模型、架构、特征工程或所有任务下都失败。
OCS 已被证明不如图像通道。
该结果可外推到真实未知目标姿态反演。
GEO 真实光度数据库可提供三轴姿态监督标签。
```

---

## 4. 成果区分流

本次通过后，Codex 将形成一个精简稳定成果本体，进入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/
  08_C1C2_OCS-only证据包与claim边界_R62通过.md
```

该成果区文件不是重写 E33 全文，而是把 C1/C2 证据、FIX01 修正和 claim 边界压缩成后续可引用的稳定口径。后续如写论文 Results 草案，应优先引用该成果区文件和 `c2_screening_summary.json`，不要直接沿用 E33 原始报告中被 FIX01 替换的旧句子。

---

## 5. 阶段门状态

```text
C1/C2 evidence package：CLOSED
C2 OCS-only screening：CLOSED AS NULL RESULT
E33-FIX01：CLOSED
C3：NOT RELEASED
Paper Results prose：NOT RELEASED
New training / hyperparameter / architecture search：NOT RELEASED
```

R62 只关闭 C1/C2 证据包整理与 FIX01 修正，不放行任何新训练。

---

## 6. 建议下一步

当前不建议让 Claude 直接启动 C3 或论文正文。可放行一个窄范围的规划任务：

```text
1C-E34：路线一 C 后续路径裁决准备
目标：整理两个候选路径的决策材料，不运行训练、不改代码、不写论文正文。
路径 A：接受 C2 null result，准备 Results 表格/图注/段落骨架的非正文草案。
路径 B：评估 C3 independent comparison 是否值得另行放行，列资源、风险、最小协议和停止条件。
输出：Claude 候选材料进入 02_Claude输出，交回 Codex 再裁决。
```

在作者或 Codex 后续明确放行前，C3 仍为候选设计，不是执行任务。

