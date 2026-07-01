# R84 Codex 审阅：1C-E45D 需 FIX01，Figure S5 样本数与版式修正

最后更新：2026-06-27  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  82_1C-E45D_图表预生成草案_Claude执行报告.md

06_v0.4_code/08_visualization/
  generate_e45d_figures.py
  Figure3_yaw_extrapolation_gap_draft.png/.pdf
  Figure4_pitch_anisotropy_draft.png/.pdf
  FigureS5_sentinel_diagnostic_draft.png/.pdf
  Table2_indicator_reconstruction_draft.md/.csv
```

## 0. 裁决

```text
1C-E45D：NEEDS FIX01
成果分流：暂不进入成果区
性质：D 类图表/表格预生成
新训练：未发现
模型 / split / 超参 / seed 修改：未发现
论文正文正式改写：未发现
阻断点：Figure S5(b) 样本数硬编码导致分通道柱值与总样本数不一致，且图中文字遮挡
```

E45D 的主方向正确：Figure 3、Figure 4 和 Table 2 基本遵循 R83 裁决，数值与 R82 稳定表可复现。但 Figure S5(b) 存在事实性图表错误，不能直接通过。

## 1. 已通过部分

### 1.1 Figure 3

Figure 3 采用三 panel：

```text
Figure 3a  yaw CMAE vs chance
Figure 3b  yaw within-6 vs chance
Figure 3c  yaw coarse45 vs chance
```

这与 R83 裁决一致，避免了把不同量纲和不同方向的指标混在单 panel 中。数值与 R82 稳定表一致，可保留。

### 1.2 Table 2

`Table2_indicator_reconstruction_draft.md/.csv` 的主数值与 R82 稳定表一致。SEM 标注可以作为草案保留，但投稿前仍需作者决定是否改成 mean +/- SEM、mean (SEM) 或不展示 SEM。

### 1.3 Figure 4

Figure 4 的指标选择与 R83 一致：pitch exact 与 pitch within-3。图中数值正确，可保留为草案。FIX01 中建议顺手增加 y-axis headroom，避免柱顶数值贴近图框。

## 2. 阻断问题

### 2.1 Figure S5(b) 分通道样本数错误

脚本当前使用硬编码近似：

```python
total = [65 * 555, 5 * 555, 5 * 555]
```

对应图中柱值为：

```text
C2 OCS-only      36,075
C3 image_only     2,775
C3 joint          2,775
```

但 E45A JSON 中真实 `n_samples` 为：

```text
C2 OCS-only      34,632
C3 image_only     2,664
C3 joint          2,664
Total            39,960
```

当前 Figure S5(b) 图内又写了：

```text
Across all 39,960 test samples...
```

因此同一张图里出现了“分通道柱值相加 = 41,625”与“总样本数 = 39,960”的矛盾。这是事实性图表错误，必须修正。

### 2.2 Figure S5(b) 文本遮挡

Figure S5(b) 中 “Across all 39,960 test samples...” 注释与柱内 “0 in holdout” 文本发生明显遮挡。该图不能作为稳定草案进入成果区。

### 2.3 执行报告红线措辞需修正

Claude 报告写：

```text
未改任何代码（仅新增可视化脚本，只读 JSON 输入）
```

这句话自相矛盾。R83 已允许新增“图表生成脚本”，但报告应改成：

```text
未改训练、模型、split、超参或数据生成代码；仅新增只读图表生成脚本。
```

## 3. FIX01 要求

请执行 `1C-E45D-FIX01`，只修正 E45D 图表草案，不新增训练、不改模型、不改 split。

必须完成：

```text
1. 修改 generate_e45d_figures.py：
   - Figure S5(b) 的 total 不得再硬编码 65*555 / 5*555。
   - 必须从 c2_extended_metrics.json 与 c3_extended_metrics.json 的 n_samples 字段聚合：
       C2 OCS-only = sum(C2 n_samples)
       C3 image_only = sum(mode == image_only 的 n_samples)
       C3 joint = sum(mode == joint 的 n_samples)
   - 图中三根柱必须分别标注 34,632 / 2,664 / 2,664。
   - 图中总注释必须与三根柱相加一致：39,960。

2. 修正 Figure S5(b) 版式：
   - 消除底部红字和柱内文字遮挡。
   - 可以把总注释放到图外 caption-like footnote 区域，或改用更简洁的右上角文本框。
   - 保持 Figure S5 只作为 SI 哨兵/诊断图，不扩大 claim。

3. 顺手优化 Figure 4：
   - 增加 y-axis 顶部留白，避免 21.2% 等标签贴近上边框。

4. 更新执行报告：
   - 写入 02_Claude输出/83_1C-E45D-FIX01_FigureS5样本数与版式修正_Claude执行报告.md
   - 报告必须列出修正前后样本数：
       before: 36,075 / 2,775 / 2,775
       after: 34,632 / 2,664 / 2,664
   - 报告必须声明只改图表生成脚本和图表草案，未触碰训练/模型/split/超参/seed。
```

可保留：

```text
Figure3_yaw_extrapolation_gap_draft.png/.pdf
Table2_indicator_reconstruction_draft.md/.csv
Figure4_pitch_anisotropy_draft.png/.pdf 的指标设计
```

但 FIX01 执行后应重新生成：

```text
Figure4_pitch_anisotropy_draft.png/.pdf
FigureS5_sentinel_diagnostic_draft.png/.pdf
```

## 4. 暂不放行事项

在 FIX01 通过前，暂不放行：

```text
E45D 成果区稳定摘要
S1/S2/S3/S4 预生成
论文正文正式改写
档 B 新训练
raw 4-dim OCS-only
--mode all
后验架构 / 超参 / 特征补救
三轴小项目或路线二/三/四扩展
```

## 5. 给 Claude 的下一步短提示词

```text
请执行 1C-E45D-FIX01：修正 Figure S5 样本数与版式。

关键依据：
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R84_Codex_审阅_1C-E45D需FIX01_FigureS5样本数与版式修正.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R83_Codex_审阅_1C-E45C通过_图表SI规划体系校正稳定.md
- v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c2_extended_metrics.json
- v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.json

任务：
1. 修正 06_v0.4_code/08_visualization/generate_e45d_figures.py。
2. Figure S5(b) 的样本数必须从 JSON 的 n_samples 聚合，不得硬编码。
3. 分通道样本数必须为：
   - C2 OCS-only: 34,632
   - C3 image_only: 2,664
   - C3 joint: 2,664
   - total: 39,960
4. 消除 Figure S5(b) 文本遮挡。
5. 顺手增加 Figure 4 顶部留白。
6. 重新生成 Figure4 和 FigureS5 的 png/pdf。
7. 写执行报告到：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
   83_1C-E45D-FIX01_FigureS5样本数与版式修正_Claude执行报告.md

红线：
- 不训练。
- 不改 split / 模型 / 超参 / seed。
- 不启动档 B、raw 4-dim OCS-only 或 --mode all。
- 不写论文正文正式段落。
- 不外推真实 GEO、三轴姿态、暗室实验或所有模型。
- 只允许修正图表生成脚本、Figure4/FigureS5 草案和执行报告。
```
