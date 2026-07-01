# R86 Codex 审阅：1C-E45D-FIX02 通过，图表/表格预生成草案稳定

最后更新：2026-06-29  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
87_1C-E45D-FIX02_FigureS5小柱标签版式修正_Claude执行报告.md

06_v0.4_code/08_visualization/
generate_e45d_figures.py
Figure3_yaw_extrapolation_gap_draft.png/.pdf
Figure4_pitch_anisotropy_draft.png/.pdf
FigureS5_sentinel_diagnostic_draft.png/.pdf
Table2_indicator_reconstruction_draft.md/.csv
```

## 0. 裁决

```text
1C-E45D-FIX02：PASS
成果分流：允许形成成果区稳定摘要
性质：D 类图表/表格预生成草案
新训练：未发现
模型 / split / 超参 / seed 修改：未发现
论文正文正式改写：未发现
三轴小项目 / 路线二 / 路线三 / 路线四扩展：NOT RELEASED
```

E45D-FIX02 已完成 R85 要求：删除 Figure S5(b) 柱顶灰色样本数标签，保留 x 轴样本数与底部总注释，解除 C3 image_only / C3 joint 小柱标签拥挤问题。E45D 图表/表格预生成草案可稳定为路线一 C 当前图表资产入口。

## 1. 审阅核查

### 1.1 样本数核查通过

Codex 直接聚合 JSON 字段并重跑脚本，结果为：

```text
C2 OCS-only  = 34,632 samples, 65 runs
C3 image_only = 2,664 samples, 5 folds
C3 joint      = 2,664 samples, 5 folds
Grand total   = 39,960 samples
```

Figure S5(b) 的 x 轴标签与底部总注释均使用上述数值。

### 1.2 旧硬编码与旧标签逻辑未检出

Codex 搜索未检出：

```text
36075
2775
41625
Total count annotation
```

说明 R84/R85 指出的旧硬编码和柱顶样本数标签逻辑已移除。

### 1.3 脚本可执行性通过

使用环境：

```text
C:\Users\97466\.conda\envs\ocs_sim\python.exe
```

重跑脚本：

```text
06_v0.4_code/08_visualization/generate_e45d_figures.py
```

输出完整生成：

```text
Figure3_yaw_extrapolation_gap_draft.png/.pdf
Figure4_pitch_anisotropy_draft.png/.pdf
FigureS5_sentinel_diagnostic_draft.png/.pdf
Table2_indicator_reconstruction_draft.md/.csv
```

### 1.4 图表目检通过

Figure S5：

```text
S5a exact-bin sentinel 图保留 chance baseline 与 0.00% 标注。
S5b holdout-prediction diagnostic 图中柱顶灰色样本数标签已删除。
C3 image_only / C3 joint 小柱红色 "0 in holdout (0.0%)" 标注不再与样本数标签挤压。
样本数仍在 x 轴标签中保留，底部总注释保留 39,960 总样本口径。
```

Figure 3 / Figure 4：

```text
未见阻断性遮挡。
Figure 4 顶部留白仍满足 R84 要求。
```

### 1.5 Table 2 数值通过

`Table2_indicator_reconstruction_draft.md` 与 R82 稳定表一致：

```text
exact-bin yaw_acc:
  C2 = 0.00%
  C3 image_only = 0.00%
  C3 joint = 0.00%

yaw CMAE:
  C2 = 97.0 deg
  C3 image_only = 81.4 deg
  C3 joint = 81.4 deg

yaw within-6:
  C2 = 18.89%
  C3 image_only = 25.57%
  C3 joint = 26.51%

yaw coarse45:
  C2 = 14.53%
  C3 image_only = 17.96%
  C3 joint = 18.16%

pitch exact:
  C2 = 3.03%
  C3 image_only = 21.20%
  C3 joint = 19.42%

pitch within-3:
  C2 = 17.75%
  C3 image_only = 56.07%
  C3 joint = 51.77%
```

## 2. 接受的稳定资产

E45D 当前稳定图表/表格草案为：

```text
06_v0.4_code/08_visualization/
  Figure3_yaw_extrapolation_gap_draft.png
  Figure3_yaw_extrapolation_gap_draft.pdf
  Figure4_pitch_anisotropy_draft.png
  Figure4_pitch_anisotropy_draft.pdf
  FigureS5_sentinel_diagnostic_draft.png
  FigureS5_sentinel_diagnostic_draft.pdf
  Table2_indicator_reconstruction_draft.md
  Table2_indicator_reconstruction_draft.csv
  generate_e45d_figures.py
```

对应成果区稳定摘要：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/
16_E45D图表表格预生成草案_R86通过.md
```

## 3. Claim 边界

允许写：

```text
E45D 基于 R82/R83 稳定指标体系，形成 Figure 3、Figure 4、Figure S5 和 Table 2 草案。
Figure 3 支持 yaw extrapolation gap 的图表呈现。
Table 2 支持三通道指标重构与 chance baseline 对照。
Figure 4 支持 fixed-roll 下 pitch 强于 yaw 的各向异性表述。
Figure S5 只作为 exact-bin sentinel 与 holdout-prediction diagnostic，不承载物理不可观测 claim。
```

不得写：

```text
E45D 证明 yaw 物理不可观测。
E45D 证明 OCS/image 永久无互补价值。
E45D 可外推真实 GEO、三轴姿态、暗室实验或所有模型。
Figure S5 standalone 进入正文主图。
```

## 4. 当前下一步

按总览 R05，头A 已完成 A-1：

```text
A-1 E45D-FIX01/FIX02 审阅并稳定图表草案：DONE
```

下一步不自动进入新训练。建议按 R05 继续：

```text
头A：
  A-2 评估是否需要补齐必要 SI 资产与图表/表格收尾清单；
  A-3 写“负结果 -> 24 号三问”桥接材料，作为头A 真闭合口。

头B：
  并行启动 85 号文献检索。
```

仍未放行：

```text
论文正文正式改写
档 B 新训练
raw 4-dim OCS-only
--mode all
后验架构 / 超参 / 特征补救
单帧多维 OCS vs 光变曲线正式实验设计
三轴小项目或路线二/三/四扩展
```

## 5. CLAUDE.md 同步

按 R05，`CLAUDE.md` 不在本轮立即同步。建议待 A-2/A-3 入口或头A/头B合并审阅后，再受控同步最新状态与下一步。

