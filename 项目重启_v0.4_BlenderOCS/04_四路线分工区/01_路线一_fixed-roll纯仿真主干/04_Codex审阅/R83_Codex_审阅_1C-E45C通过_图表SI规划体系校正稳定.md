# R83 Codex 审阅：1C-E45C 通过，图表/SI 规划体系校正稳定

最后更新：2026-06-27  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  81_1C-E45C_图表SI规划稿_Claude执行报告.md
```

## 0. 裁决

```text
1C-E45C：PASS WITH CODEX CORRECTION
成果分流：允许形成成果区稳定摘要
性质：D 类只读图表/SI 规划
新训练：NOT RELEASED
模型 / split / 超参 / seed 修改：NOT RELEASED
论文正文正式改写：NOT RELEASED
图表批量生成：NOT YET RELEASED，需进入下一阶段 E45D 单独执行
```

E45C 完成了 R82 要求的图表/SI 体系重排：主叙事从 exact-bin yaw=0.00% 转移到 yaw circular MAE、within-k、coarse-bin 与 chance/random baseline 的对照；S3/S4/S5 和正文/SI 编号体系已形成可执行框架。

但 Claude 稿中对 Figure 5 的表述存在轻微混乱：一处建议 Figure 5 不进正文，另一处又推荐正文 compact 双 panel。Codex 在本轮直接校正，不返工。

## 1. 红线核验

接受 Claude 的执行声明：

```text
未训练
未改代码
未改 split / 模型 / 超参 / seed
未生成新图或新表
未写论文正文正式段落
未改成果区
未外推真实 GEO / 三轴姿态 / 暗室实验 / 所有模型
```

输出位置正确：`02_Claude输出/`。本 R83 作为 Codex 审阅进入 `04_Codex审阅/`。

## 2. Codex 校正后的图表体系

### 2.1 正文 Figures

```text
Figure 1  OCS feature extraction pipeline                         Methods，后续写作阶段再生成
Figure 2  Circular yaw-block holdout strategy                    Methods/Results，现有资产直接引用
Figure 3  Yaw extrapolation gap 主图                              Results，P0
Figure 4  Pitch anisotropy 辅助图                                 Results，P1
```

本阶段不保留独立正文 Figure 5。exact-bin 0% 不能重新成为 standalone 正文图，否则会削弱 R82 已校正的主叙事层级。若后续排版确实需要，可只作为 Figure 3 的小 inset；默认进入 SI。

Figure 3 采用多 panel，而不是单 panel 多指标混排：

```text
Figure 3a  yaw CMAE vs chance
Figure 3b  yaw within-6 vs chance
Figure 3c  yaw coarse45 vs chance
```

原因：CMAE 是角度误差且越低越好，within-6 / coarse45 是命中率且越高越好，强行放入单 panel 容易误导。

### 2.2 正文 Tables

```text
Table 1  OCS feature configuration overview                       Methods，写作阶段精修
Table 2  R82 指标重构主表：yaw + pitch 全指标 x 三通道 vs chance   Results，P0
```

Claude 稿中的 Table 3（C3 formal per-fold summary）默认降级为 Supplementary Table。正文不需要再放一个 per-fold 表，除非作者后续明确希望增加正文表数量。

### 2.3 SI Figures

```text
Figure S1  C2 65-run yaw CMAE distribution by config
Figure S2  Yaw CMAE vs within-6 per-run / per-fold scatter
Figure S3  Training curves：C2 代表性 3-5 条 + C3 全 10 folds
Figure S4  Overlap diagnostic：train/test yaw-bin strict holdout status
Figure S5  Exact-bin sentinel + holdout-prediction diagnostic
```

Figure S5 采用双 panel：

```text
S5a  exact-bin yaw_acc = 0.00% 三通道哨兵指标
S5b  E45A holdout-prediction ratio = 0.0 机制诊断
```

它只承担哨兵与失败模式归档，不承载物理不可观测 claim。

### 2.4 SI Tables

采用更接近期刊习惯的命名：`Table S1-S5`，不采用 `ST1-ST5` 作为最终编号。

```text
Table S1  Raw OCS feature definitions and pre-registered constants
Table S2  C2 per-fold results, 65 rows
Table S3  C3 per-fold detail, 10 folds x key metrics
Table S4  C2 screening grouped results by claim_class
Table S5  C2 enhanced OCS vs C3 raw 4-dim OCS input spec comparison
```

## 3. 对 Claude 待确认问题的裁决

```text
1. Figure 5 方案：
   选 Codex 校正版：无 standalone 正文 Figure 5；exact-bin + holdout diagnostic 进入 Figure S5。

2. Figure 3 面板设计：
   选三 panel 设计：CMAE / within-6 / coarse45 分开展示。

3. Table 2 vs Table 3 归属：
   Table 2 留正文；C3 per-fold 摘要默认进入 Table S3。

4. S3 training curves 范围：
   C2 只选 3-5 个代表性 config；C3 展示 image_only 5 folds + joint 5 folds。

5. S1/S2 是否必要：
   暂保留为 P2 SI。S1 支撑 C2 分布，S2 支撑 per-run/per-fold 变异性；后续版面紧张时可合并。

6. 编号前缀：
   使用 Figure S1-S5 与 Table S1-S5。
```

## 4. 稳定后的下一阶段

下一步可进入 `1C-E45D`，但只放行到“图表/表格预生成”，仍然不得训练或改模型。

建议 E45D 范围：

```text
P0:
  - 生成 Figure 3 draft（yaw extrapolation gap 三 panel）
  - 生成 Table 2 markdown/csv draft（R82 指标重构主表）

P1:
  - 生成 Figure 4 draft（pitch anisotropy）
  - 生成 Figure S5 draft（exact-bin sentinel + holdout-prediction diagnostic）

仍不做：
  - 档 B 新训练
  - raw 4-dim OCS-only
  - --mode all
  - 后验架构 / 超参 / 特征补救
  - 论文正文正式改写
  - 三轴小项目或路线二/三/四扩展
```

E45D 若需要新增可视化脚本，必须只读取既有 E45A/R82 数值资产，输出图表草案和执行报告；不得改变任何训练结果、split、模型或数据生成流程。

## 5. 给 Claude 的下一步短提示词

```text
请执行 1C-E45D：图表/表格预生成草案。

关键依据：
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R83_Codex_审阅_1C-E45C通过_图表SI规划体系校正稳定.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R82_Codex_审阅_1C-E45B通过_指标重构与外推鸿沟叙事稳定.md
- v0.4_results/07_negative_diagnosis/e45a_inference_regroup/

任务范围：
1. 生成 Figure 3 draft：yaw CMAE / within-6 / coarse45 三 panel，三通道 vs chance baseline。
2. 生成 Table 2 draft：R82 指标重构主表，输出 markdown 和 csv。
3. 生成 Figure 4 draft：pitch exact / within-3 三通道 vs chance baseline。
4. 生成 Figure S5 draft：exact-bin sentinel + holdout-prediction diagnostic 双 panel。
5. 写执行报告到：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/

红线：
- 不训练。
- 不改 split / 模型 / 超参 / seed。
- 不启动档 B、raw 4-dim OCS-only 或 --mode all。
- 不写论文正文正式段落。
- 不外推真实 GEO、三轴姿态、暗室实验或所有模型。
- 若需要新增脚本，只能作为图表生成脚本，且必须清楚记录输入 JSON/CSV、输出路径和未触碰训练流程。
```
