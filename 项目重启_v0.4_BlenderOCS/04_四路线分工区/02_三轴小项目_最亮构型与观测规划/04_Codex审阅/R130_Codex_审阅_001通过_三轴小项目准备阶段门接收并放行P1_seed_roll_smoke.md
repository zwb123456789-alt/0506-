# R130 Codex 审阅：001 通过，三轴小项目准备阶段门接收并放行 P1 seed-roll smoke

最后更新：2026-07-01  
审阅端：Codex  
审阅对象：

```text
02_Claude输出/001_三轴小项目准备阶段门设计_Claude执行报告.md
v0.4_results/18_three_axis_planning_preflight/
```

上游阶段门：R129 三轴小项目准备阶段门设计任务单

## 1. 审阅结论

001 执行报告与 18 号准备包通过。三轴小项目准备阶段门设计达到 R129 最低与强接收标准：

```text
输入资产审计：16/16 OK。
三轴指标 registry：11 指标，分 A-direct / B-derived / C-need-roll。
三轴搜索种子：66 seed，覆盖 9 类。
采样与资源计划：P1-P4 阶段矩阵完整。
P1 草案：12 种子 × 8 非零 roll = 96 渲染单位，可作为下一步 smoke 任务基础。
一致性检查：14/14 PASS。
红线自检：10/10 PASS。
```

Codex 裁定：**18 号准备包接收为三轴小项目当前主用准备成果；放行下一步 P1 seed-roll scan smoke。**

本次放行不等于三轴小项目完成，不放行全量三轴渲染，不放行 P2/P3/P4，不放行 roll-aware 训练，不启动 R128 新路线二或路线二/三/四扩展。

## 2. 完成度核验

18 号包结构完整：

```text
audit/
figures/
logs/
metrics/
resources/
sampling/
scripts/
seeds/
tables/
text/
```

Codex 抽查结果：

```text
generated_files_manifest.csv：36/36 exists=True
实际文件数：37（manifest 未计自身或生成时序差异，非阻塞）
numeric_path_consistency_check.csv：14/14 PASS
redline_self_check.csv：10/10 PASS
input_manifest.csv：16/16 OK
```

001 报告写入三轴小项目 `02_Claude输出/`，18 号包写入 `v0.4_results/18_three_axis_planning_preflight/`。未写成果区、未改 `CLAUDE.md`、未启动渲染/训练、未启动 R128。

## 3. 接收证据

### 3.1 输入审计与可复用资产

接收 16 项路线一 C 可复用资产索引。五个几何的 roll=0 OCS 亮度均有 2664 姿态来源：

```text
phase63：01_fullrun
phase24/45/90/120：11_l1m2_multigeometry_ocs
```

接收关键代码判断：`render_mroll_probe.py` 已在 R117/R127 证明可参数化到 roll 轴；三轴渲染在工程上具备可行入口，但后处理、训练和样本字段仍需在后续 P1/P2 阶段受控扩展。

### 3.2 三轴指标定义

接收 11 指标 registry，包括：

```text
brightness / OCS magnitude
local contrast
nearest-neighbor ambiguity
candidate entropy
margin
top-k stability
OCS-image overlap / JS
saturation / glint flag
geometry utility score
roll sensitivity score
```

接收 `brightness_vs_information_boundary.md` 的核心结论：fixed-roll 下 corr(log brightness, G1->G5 gain) 约 -0.088，说明“最亮不等于最高信息”这一小项目基本边界被数据支持。该结论仍需在 roll 扩展后复核。

### 3.3 三轴搜索种子

接收 66 个 seed，覆盖 9 类：

```text
bright-seed：8
dark-seed：8
high-info-seed：8
low-info-seed：8
ocs-hard-seed：8
image-hard-seed：2
disagreement-seed：8
roll-sensitive-seed：8
robust-easy-seed：8
```

image-hard-seed 仅 2 个不是遗漏，而是 clean/P-INT image_only 近饱和导致该类样本天然稀少。后续可在 R128 或真实退化路线中扩充 image-hard 场景；当前三轴 P1 smoke 不要求人为补足。

### 3.4 采样策略与资源估计

接收 P1-P4 阶段化设计：

```text
P1 seed-roll scan：96 渲染单位，约 0.03 h / 25 MB。
P2 sparse 3-axis grid：3744 渲染单位，约 1 h / 1.0 GB。
P3 local refinement：约 32400 渲染单位，约 9 h / 8.5 GB。
P4 最亮构型与光路解释综合：不新增渲染。
```

资源估计采用 17 号 M-roll full-2664 实测约 1 s/姿态作为基准，合理。P3 资源较重，后续必须等 P1/P2 结果后再裁决。

### 3.5 P1 seed-roll scan 草案

接收 P1 草案为下一轮任务基础：

```text
12 个代表种子；
8 个非零 roll：{-60,-45,-30,-15,+15,+30,+45,+60}；
roll=0 复用既有结果；
几何限定 phase63 / L1-G1；
总计 96 渲染单位；
不训练 roll-aware 模型；
只计算 OCS magnitude、image usability、local contrast、roll sensitivity 等 smoke 指标。
```

## 4. 对裁决问题的回答

Q1 001 准备包是否通过、是否进入成果区：通过，生成当前主用成果摘要。  
Q2 指标 registry、9 类 seed、P1-P4 采样计划是否接收：接收。  
Q3 是否放行 P1 seed-roll scan smoke：放行。  
Q4 P1 先 smoke 还是直接正式 P1：先 smoke，仅 96 单位、phase63、无训练。  
Q5 是否需要先补读代码 roll 字段改造：P1 smoke 允许由 Claude 审计并新增派生脚本；不得改旧脚本。后处理字段若不足，只能新增 19 号包内派生后处理/汇总脚本。  
Q6 R128 是否继续挂起：继续挂起到三轴小项目完成后再回看。  
Q7 P1 输出目录是否采纳 `19_three_axis_p1_seed_roll_scan/`：采纳。

## 5. 成果区升级

同意新增当前主用成果摘要：

```text
01_成果区/00_当前主用成果/00_三轴小项目准备阶段门设计_R130通过.md
```

18 号准备包本体仍保留在：

```text
v0.4_results/18_three_axis_planning_preflight/
```

## 6. 下一步

下一份任务单为：

```text
R131_Codex_任务单_P1_seed_roll_scan_smoke.md
```

任务边界：

```text
只执行 P1 smoke；
只做 96 个 phase63 seed-roll 渲染单位；
不训练；
不启动 P2/P3/P4；
不启动 R128；
不改旧结果目录 10-18；
输出 19 号包与 002 Claude 报告后，再由 Codex 审阅。
```
