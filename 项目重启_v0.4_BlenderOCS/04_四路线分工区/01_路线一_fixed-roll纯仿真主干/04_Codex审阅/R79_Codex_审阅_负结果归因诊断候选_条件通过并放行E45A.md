# R79 Codex 审阅：负结果归因诊断候选条件通过，并放行 E45A

最后更新：2026-06-27  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  78_负结果归因诊断方案候选_判据敏感性对照与档A推理重聚合_Claude候选.md
```

## 0. 裁决

```text
候选方向：ACCEPTED WITH BOUNDARY CORRECTION
正式任务编号：1C-E45A
任务性质：负结果归因诊断 / 档 A-min 推理重聚合
档 A-min：RELEASED WITH GATES
档 B 新训练：NOT RELEASED
论文正文正式改写：NOT RELEASED
三轴小项目 / 路线二 / 路线三 / 路线四：NOT RELEASED
```

Claude 候选提出的“判据敏感性 + 推理重聚合”方向是必要的。R77/R78 已稳定三通道 exact-bin yaw 0.00% 负结果，但仍需要进一步区分：

```text
是 strict circular yaw-block + 72-bin exact 分类判据过严，
还是当前固定协议下确实无法形成跨 yaw-block 可用的 yaw 信息。
```

因此，允许进入一个很窄的 E45A 诊断任务。但 E45A 不是训练任务，不是后验补救任务，也不是修改主判据任务。它只允许在已训练 checkpoint 上做只读推理复算与后处理敏感性分析。

## 1. 必须修正的事实

Claude 候选中写：

```text
C2 共 14 config × 5 fold = 70 checkpoint
```

该表述不正确。稳定口径和目录核查均为：

```text
C2 = 13 configs × 5 folds = 65 checkpoints
```

13 个配置为：

```text
baseline_4dim
R_ratio_2d
R_ratio_3d
I_interpart_1d
N_density_3d
L_logratio_3d
M1_ratio_log_5d
M3_density_ratio_5d
M4_log_density_ratio_9d
P_pixelfrac_3d
M5_pixelfrac_only_4d
M2_ratio_pixelfrac_5d
M6_all_nongeo_13d
```

E45A 报告和脚本不得再写 14/70。

## 2. E45A 放行范围

允许：

```text
1. 新建独立诊断脚本，不改训练脚本主体逻辑。
2. 读取已存在 checkpoint、manifest、result/detail JSON。
3. 复算 test split 上逐样本 yaw/pitch prediction 与 truth。
4. 先复现现有 exact-bin yaw_acc、pitch_acc、yaw_cmae。
5. 复现通过后，计算探索性 secondary diagnostics：
   - coarse-bin accuracy：30 deg / 45 deg
   - within-k：k = 1, 2, 3, 6
   - yaw CMAE distribution
   - yaw confusion matrix
6. 输出逐样本 npz/jsonl、汇总 json/csv、简短 Claude 执行报告。
```

建议代码目录：

```text
06_v0.4_code/09_diagnostics/
```

建议结果目录：

```text
v0.4_results/07_negative_diagnosis/e45a_inference_regroup/
```

建议 Claude 报告：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  79_1C-E45A_负结果归因诊断_档A推理重聚合_Claude执行报告.md
```

## 3. 先行门

E45A 必须先完成 exact-bin 复现门：

```text
对 C3 image_only 5 folds、C3 joint 5 folds、C2 13 configs × 5 folds，
复算 exact-bin yaw_acc、pitch_acc、yaw_cmae，
并与 R62/R77/R78 稳定数值或对应 result/detail JSON 对齐。
```

通过标准：

```text
yaw_acc 必须逐 fold 对齐到 0.00%。
pitch_acc 与 yaw_cmae 允许存在浮点级微小差异，但不得出现口径级偏差。
若发现 last-epoch checkpoint 与现有 JSON 指标不一致，必须停止扩展判据计算，
只报告差异来源、涉及 fold/config、checkpoint epoch 与 result JSON 口径。
```

只有先行门通过后，才允许计算 coarse-bin、within-k 和 confusion matrix。

## 4. Claim 边界

E45A 可写：

```text
This is an exploratory sensitivity analysis of the already accepted fixed-protocol negative result.
```

可写：

```text
The exact-bin yaw result remains the primary fixed-protocol verdict; coarse-bin and within-k metrics are secondary diagnostics.
```

不可写：

```text
coarse-bin / within-k 若高于 exact-bin，就推翻 R77/R78 null result。
coarse-bin / within-k 若高于随机，就证明模型可以可靠反演 yaw。
判据敏感性结果可以替代预注册 exact-bin 主判据。
E45A 可以证明 OCS/image 互补性成立或不成立。
E45A 可以外推到真实 GEO、三轴姿态或暗室实验。
```

稳定解释框架：

```text
E45A 只用于解释失败模式：
strict exact-bin failure 是否伴随 coarse localization；
预测是否坍缩到训练可见 yaw 区间；
image_only 与 joint 在同一 fold、同一判据下是否表现一致或分离。
```

## 5. 不放行范围

```text
不放行档 B：random split / interleaved holdout 新训练。
不放行修改 split、模型、训练超参、batch size、epoch、lr、seed。
不放行 raw 4-dim OCS-only 训练。
不放行 --mode all。
不放行后验架构搜索、特征补救、超参补救。
不放行论文正文正式段落。
不放行三轴小项目、路线二、路线三或路线四扩展。
```

如 E45A 显示 coarse-bin / within-k 有明显信号，只能作为“后续是否设计预注册补充实验”的依据，不能直接回头改写 R77/R78 主结论。

## 6. 给 Claude 的 E45A 短提示词

```text
执行 1C-E45A：负结果归因诊断的档 A-min 推理重聚合。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R70_Codex_规则_Claude执行端已知问题与规避规则.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R77_Codex_审阅_1C-E43通过_C2C3三通道负结果证据包稳定.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R78_Codex_审阅_1C-E44通过_C2C3_Results非正文总材料包稳定.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R79_Codex_审阅_负结果归因诊断候选_条件通过并放行E45A.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/11_C2C3三通道负结果证据包_E43_R77通过.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/12_C2C3_Results非正文总材料包_E44_R78通过.md

任务：
1. 新建独立诊断脚本，建议放入 06_v0.4_code/09_diagnostics/；不得修改训练脚本主体逻辑。
2. 读取已存在 checkpoint、manifest、result/detail JSON，对 C2 13 configs × 5 folds、C3 image_only 5 folds、C3 joint 5 folds 做 test split 只读推理复算。
3. 先复现 exact-bin yaw_acc、pitch_acc、yaw_cmae，并与现有 JSON/R77/R78 口径对齐。
4. 若 exact-bin 复现未对齐，立即停止，只报告差异，不计算扩展判据。
5. 若复现对齐，再计算 coarse-bin 30/45 deg、within-k(k=1,2,3,6)、yaw CMAE distribution、yaw confusion matrix。
6. 输出逐样本预测与汇总表到：
   v0.4_results/07_negative_diagnosis/e45a_inference_regroup/
7. 输出简短执行报告到：
   /d/我的文件/研究生学术/光学项目/0506新/项目重启_v0.4_BlenderOCS/04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/79_1C-E45A_负结果归因诊断_档A推理重聚合_Claude执行报告.md

硬性修正：
- C2 是 13 configs × 5 folds = 65 checkpoints，不是 14 × 5 = 70。

红线：
- 不训练。
- 不改 split、模型、训练超参、batch size、epoch、lr、seed。
- 不运行 raw 4-dim OCS-only 训练，不运行 --mode all。
- 不做后验架构/超参/特征补救。
- 不写论文正文正式段落。
- 不外推真实 GEO、三轴姿态、暗室实验或所有模型。
- coarse-bin / within-k / confusion matrix 只能写成 exploratory secondary diagnostics，不能替代 R77/R78 exact-bin 主结论。
```

## 7. 后续闸门

Claude 完成 E45A 后，作者应把 E45A 输出路径交回 Codex。Codex 只审阅：

```text
1. exact-bin 复现门是否通过；
2. coarse / within / confusion 是否按同一 fold、同一通道、同一判据成对比较；
3. 是否出现越界 claim；
4. 是否有必要进入档 B 新训练讨论。
```

档 B 是否放行必须另行 Codex 审阅，不因本 R79 自动放行。
