# R85 Codex 审阅：1C-E45D-FIX01 需 FIX02，Figure S5 小柱标签版式修正

最后更新：2026-06-29  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
83_1C-E45D-FIX01_FigureS5样本数与版式修正_Claude执行报告.md

06_v0.4_code/08_visualization/
generate_e45d_figures.py
Figure3_yaw_extrapolation_gap_draft.png/.pdf
Figure4_pitch_anisotropy_draft.png/.pdf
FigureS5_sentinel_diagnostic_draft.png/.pdf
Table2_indicator_reconstruction_draft.md/.csv
```

## 0. 裁决

```text
1C-E45D-FIX01：NEEDS FIX02
成果分流：暂不进入成果区
性质：D 类图表/表格预生成修正
新训练：未发现
模型 / split / 超参 / seed 修改：未发现
论文正文正式改写：未发现
阻断点：Figure S5(b) 的小柱灰色样本数标签与红色 "0 in holdout" 标注仍存在视觉拥挤/遮挡风险
```

E45D-FIX01 已修正 R84 指出的核心事实错误：Figure S5(b) 样本数不再使用 `65*555 / 5*555` 硬编码，而是从 JSON 的 `n_samples` 聚合。数值核查通过。

但 Figure S5(b) 中 C3 image_only 与 C3 joint 两个小柱的顶部灰色 `2,664` 标签，与柱内红色 `0 in holdout (0.0%)` 标注过近，视觉上仍有遮挡/挤压风险。作为图表资产草案可继续修，但不宜直接稳定进入成果区。

## 1. 已通过部分

### 1.1 样本数事实修正通过

Codex 直接聚合 JSON 字段核查：

```text
c2_extended_metrics.json:
  C2 OCS-only n_samples sum = 34,632
  runs = 65

c3_extended_metrics.json:
  C3 image_only n_samples sum = 2,664
  runs = 5

  C3 joint n_samples sum = 2,664
  runs = 5

Grand total = 39,960
```

这与 Claude83 报告一致，也与 Figure S5(b) 总注释一致。

脚本中未检出旧硬编码痕迹：

```text
65 * 555
5 * 555
36075
2775
41625
```

### 1.2 脚本可执行性通过

Codex 使用指定 Python 环境重跑：

```text
C:\Users\97466\.conda\envs\ocs_sim\python.exe
06_v0.4_code/08_visualization/generate_e45d_figures.py
```

脚本完整生成：

```text
Figure3_yaw_extrapolation_gap_draft.png/.pdf
Figure4_pitch_anisotropy_draft.png/.pdf
FigureS5_sentinel_diagnostic_draft.png/.pdf
Table2_indicator_reconstruction_draft.md/.csv
```

### 1.3 Table 2 数值通过

`Table2_indicator_reconstruction_draft.md` 与 R82 稳定表一致：

```text
C2 OCS-only:
  yaw exact = 0.00%
  yaw CMAE = 97.0 deg
  yaw within-3 = 9.96%
  yaw within-6 = 18.89%
  yaw coarse45 = 14.53%
  pitch exact = 3.03%
  pitch within-3 = 17.75%

C3 image_only:
  yaw exact = 0.00%
  yaw CMAE = 81.4 deg
  yaw within-3 = 17.12%
  yaw within-6 = 25.57%
  yaw coarse45 = 17.96%
  pitch exact = 21.20%
  pitch within-3 = 56.07%

C3 joint:
  yaw exact = 0.00%
  yaw CMAE = 81.4 deg
  yaw within-3 = 17.74%
  yaw within-6 = 26.51%
  yaw coarse45 = 18.16%
  pitch exact = 19.42%
  pitch within-3 = 51.77%
```

### 1.4 Figure 3 / Figure 4 目检通过

Figure 3：

```text
三 panel 结构符合 R83：
  yaw CMAE
  yaw within-6
  yaw coarse45
数值标注未见阻断性遮挡。
```

Figure 4：

```text
pitch exact / pitch within-3 两 panel 正确。
y-axis 顶部留白已增加。
柱顶标签未贴边，R84 指出的顶部留白问题已解决。
```

## 2. 阻断问题

### 2.1 Figure S5(b) 小柱标签仍拥挤

Figure S5(b) 中：

```text
C3 image_only:
  灰色样本数标签 2,664
  红色柱内标签 0 in holdout (0.0%)

C3 joint:
  灰色样本数标签 2,664
  红色柱内标签 0 in holdout (0.0%)
```

这两组文字距离过近，在 PNG 目检中已经出现视觉挤压。虽然 R84 原先的底部注释遮挡已解除，但该图仍不够稳定，不能作为最终草案进入成果区。

## 3. FIX02 要求

请执行 `1C-E45D-FIX02`，只修正 Figure S5(b) 版式，不改训练、不改模型、不改 split。

必须完成：

```text
1. 修改 generate_e45d_figures.py 中 Figure S5(b) 的文字布局。

2. 解除 C3 image_only / C3 joint 小柱标签拥挤：
   可任选一种简洁方案：
   - 方案 A：删除柱顶灰色样本数标签，只保留 x 轴中的样本数；
   - 方案 B：把灰色样本数标签移到柱外更高处，并增加 y-axis headroom；
   - 方案 C：把 "0 in holdout (0.0%)" 移到统一 legend/caption，不放在小柱内部。

3. 保留已修正的真实样本数：
   C2 OCS-only = 34,632
   C3 image_only = 2,664
   C3 joint = 2,664
   total = 39,960

4. 重新生成：
   FigureS5_sentinel_diagnostic_draft.png
   FigureS5_sentinel_diagnostic_draft.pdf

5. 写执行报告到：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
   87_1C-E45D-FIX02_FigureS5小柱标签版式修正_Claude执行报告.md
```

建议采用方案 A：删除柱顶灰色样本数标签，因为 x 轴标签已经写明：

```text
65 runs, 34,632 samples
5 folds, 2,664 samples
5 folds, 2,664 samples
```

保留柱内红色 `0 in holdout (0.0%)` 和底部总注释即可，信息不丢失，版式最干净。

## 4. 可保留事项

FIX02 不需要重做：

```text
Figure 3 指标设计与数值
Figure 4 指标设计与数值
Table 2 markdown/csv 数值
Figure S5(b) 样本数聚合逻辑
```

若脚本统一重跑导致 Figure 3 / Figure 4 / Table 2 时间戳更新，可以接受，但 FIX02 的实质修改范围应限于 Figure S5 版式。

## 5. 暂不放行事项

在 FIX02 通过前，暂不放行：

```text
E45D 成果区稳定摘要
CLAUDE.md 同步更新
S1/S2/S3/S4 预生成
论文正文正式改写
档 B 新训练
raw 4-dim OCS-only
--mode all
后验架构 / 超参 / 特征补救
三轴小项目或路线二/三/四扩展
```

## 6. 给 Claude 的下一步短提示词

```text
请执行 1C-E45D-FIX02：只修正 Figure S5(b) 小柱标签版式。

关键依据：
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
  R85_Codex_审阅_1C-E45D-FIX01需FIX02_FigureS5小柱标签版式修正.md
- 06_v0.4_code/08_visualization/generate_e45d_figures.py

任务：
1. 修改 Figure S5(b) 的文字布局，消除 C3 image_only / C3 joint 小柱中灰色样本数标签与红色 "0 in holdout" 标签的拥挤/遮挡。
2. 推荐直接删除柱顶灰色样本数标签；样本数已在 x 轴标签中保留。
3. 必须继续使用 JSON n_samples 聚合后的样本数：
   C2 OCS-only = 34,632
   C3 image_only = 2,664
   C3 joint = 2,664
   total = 39,960
4. 重新生成 FigureS5_sentinel_diagnostic_draft.png/.pdf。
5. 写执行报告到：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
   87_1C-E45D-FIX02_FigureS5小柱标签版式修正_Claude执行报告.md

红线：
- 不训练。
- 不改 split / 模型 / 超参 / seed。
- 不启动档 B、raw 4-dim OCS-only 或 --mode all。
- 不写论文正文正式段落。
- 不改成果区。
- 不外推真实 GEO、三轴姿态、暗室实验或所有模型。
- 不改变 Figure 3、Figure 4、Table 2 的指标口径。
```

