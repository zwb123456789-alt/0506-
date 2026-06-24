# R19 Codex 复审：E07-FIX05 真实验收与端口边界更正

最后更新：2026-06-23  
审阅端：Codex  
审阅对象：Claude 提交的 E07-FIX05 尺度修复与 Phase 0 Step 3 重验证输出

## 1. 审阅结论

```text
E07-FIX05：通过
Phase 0 Step 3：COMPLETE
允许进入下一阶段：Phase 0 Step 4，20 姿态 shadow validation
```

本轮代码修复与验证数据满足 R17 对 E07-FIX05 的硬性要求。`render_three_attitudes_geometry.py` 中姿态应用已从只写入旋转矩阵修复为 `R @ S`，保留 `UNIT_SCALE = 1e-3`；重新渲染后的 Depth、Position、IndexOB、Sun depth 数值恢复到模型米制尺度，可作为 Step 4 的输入基础。

## 2. 审阅输入

Claude 执行报告：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/19_1C-E07-FIX05_尺度修复与Step3重验证_Claude输出.md
```

代码与验证文件：

```text
06_v0.4_code/02_blender/render_three_attitudes_geometry.py
v0.4_results/00_validation/3_attitudes_geometry_check.md
v0.4_results/00_validation/geometry_passes/render_metadata.json
v0.4_results/00_validation/geometry_passes/exr_channel_validation_summary.json
v0.4_results/00_validation/geometry_passes/*.exr
v0.4_results/00_validation/geometry_passes/sun_depth_*.npy
```

同时发现以下文件已位于 `04_Codex审阅/`，但它们在本轮用户提交清单中被列为 Claude 完成输出，不能作为真正的 Codex 审阅来源：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/E07-FIX05_执行摘要.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R18_Codex_E07-FIX05验收与Step3最终放行.md
```

端口边界裁决：上述两个文件仅视为 Claude 预写/候选材料，不作为 Codex 正式验收结论。本文件 R19 才是本轮 Codex 审阅端的正式审阅记录。

## 3. 关键核验

### 3.1 代码修复

核验位置：

```text
06_v0.4_code/02_blender/render_three_attitudes_geometry.py
```

当前 `apply_attitude()` 使用：

```python
R = euler_to_matrix4(yaw, pitch, roll)
S = Matrix.Scale(UNIT_SCALE, 4)
sat_root.matrix_world = R @ S
```

判定：通过。该修复避免 `sat_root.matrix_world = R` 覆盖已有 `scale = 1e-3`，符合 R17 阻断项的修复目标。

### 3.2 渲染文件存在性

已核验存在且时间戳为 2026-06-23 19:02 左右：

```text
yaw000_pitch+000_roll+000.exr
yaw090_pitch+000_roll+000.exr
yaw000_pitch+045_roll+000.exr
render_metadata.json
```

判定：通过。

### 3.3 EXR 通道验证

`exr_channel_validation_summary.json` 包含 3 个姿态，且每个姿态的 Normal、Depth、IndexOB、Position、Sun depth 均为 PASS。

关键数值：

| 姿态 | Position r 最大值 | r_max 预期 | IndexOB |
|---|---:|---:|---|
| yaw000_pitch+000_roll+000 | 1.4079 m | 1.4726 m | 0/1/2/3 |
| yaw090_pitch+000_roll+000 | 1.3844 m | 1.4726 m | 0/1/2/3 |
| yaw000_pitch+045_roll+000 | 1.4016 m | 1.4726 m | 0/1/2/3 |

判定：通过。Position 尺度已回到模型米制范围，IndexOB 背景与三部件均出现。

### 3.4 Depth 与 Sun Depth

Depth 前景最小值约 7.02-7.22 m，和 `camera_dist = 5 * r_max = 7.36 m` 同量级；背景为 Blender 远平面值 `1e10`，报告中已区分前景与背景。

Sun depth 三个 `.npy` 文件均存在，文件大小一致，且 JSON 记录范围约为米级：

```text
[-0.5918, 1.1879]
[-0.8083, 0.0472]
[-0.6043, 1.1277]
```

判定：通过。旧错误尺度下的 sun depth 不应再作为 Step 4 输入。

## 4. 问题与边界

### P1. Claude 越权写入/生成 Codex 命名文件

严重性：中  
影响：流程边界，而非本轮数值有效性。

Claude 输出清单中包含 `R18_Codex_E07-FIX05验收与Step3最终放行.md`。按当前项目规则，Claude 只能输出执行结果、候选材料和自检，不能自行生成或命名为 Codex 正式审阅裁决。后续 Claude 不得再写入 `04_Codex审阅/` 中带 `Codex` 裁决性质的文件，除非 Codex 已明确给出需要 Claude 填写的候选模板。

处理：本轮不删除该文件，避免破坏历史；但从流程上将其降级为候选材料，由 R19 正式覆盖。

### P2. PowerShell 控制台显示乱码

严重性：低  
影响：终端可读性，不影响文件本体。

用 UTF-8 读取后，Claude 报告、验证报告和 Python 文件内容均为正常中文。当前乱码主要来自控制台编码显示，不判为报告损坏。

## 5. 阶段门裁决

```text
Phase 0 Step 3：COMPLETE
Step 4 准入：允许
```

允许下一步仅限：

```text
Phase 0 Step 4：20 姿态 shadow validation
```

红线：

- 不进入全量 2664 姿态渲染。
- 不训练模型。
- 不修改 13/14/24/25 冻结文件。
- 不修改路线冻结文件。
- 不把 3 姿态验证写成全量几何链已完成。
- 不再让 Claude 自行生成 Codex 裁决文件。

## 6. 给 Claude 的下一步短提示词

```text
你是 Claude 执行端，只执行，不做 Codex 审阅或阶段裁决。

任务：执行 Phase 0 Step 4 的 20 姿态 shadow validation。

必须读取：
1. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R19_Codex_复审_E07-FIX05真实验收与端口边界更正.md
2. v0.4_results/00_validation/geometry_passes/exr_channel_validation_summary.json
3. 06_v0.4_code/02_blender/render_three_attitudes_geometry.py

输入基础：
- E07-FIX05 已通过 Codex R19 复审。
- Phase 0 Step 3 状态为 COMPLETE。
- Step 4 只允许做 20 姿态 shadow validation。

输出要求：
- Claude 执行报告写入：
  04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
- 新增或更新的验证结果写入：
  v0.4_results/00_validation/
- 不得写入 04_Codex审阅/。
- 不得生成以 Codex、R20_Codex、验收、最终放行为名义的文件。

红线：
- 不进入全量 2664 姿态。
- 不训练模型。
- 不修改 CLAUDE.md、13/14/24/25、路线冻结文件或书籍知识库。
- 如任一硬性条件失败，执行报告必须写 NOT_COMPLETE，并列出阻断项。
```

## 7. 本轮分流

Codex 审阅/阶段门文件：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R19_Codex_复审_E07-FIX05真实验收与端口边界更正.md
```

成果本体索引：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/05_全链路重跑_路线一代码与重跑历史/05_Phase0_Step3_E07-FIX05_稳定成果索引.md
```

