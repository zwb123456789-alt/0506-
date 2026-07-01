# 87_1C-E45D-FIX02：Figure S5 小柱标签版式修正执行报告

执行时间：2026-06-29  
任务编号：1C-E45D-FIX02  
执行端：Claude  
审阅依据：R85_Codex_审阅_1C-E45D-FIX01需FIX02_FigureS5小柱标签版式修正.md

---

## 1. 任务目标

修正 Figure S5(b) 版式拥挤问题：C3 image_only / C3 joint 小柱顶部的灰色样本数标签（2,664）与柱内红色 "0 in holdout (0.0%)" 标注距离过近，存在视觉挤压/遮挡风险。

**红线约束**：
- 不训练
- 不改 split / 模型 / 超参 / seed
- 不改 Figure 3 / Figure 4 / Table 2 指标口径
- 不启动档 B、raw 4-dim OCS-only 或 --mode all
- 不写论文正文正式段落

---

## 2. 修正方案

采用 **R85 推荐的方案 A**：删除 Figure S5(b) 柱顶灰色样本数标签。

**理由**：
- x 轴标签已包含完整样本数信息：
  ```text
  C2 OCS-only (65 runs, 34,632 samples)
  C3 image_only (5 folds, 2,664 samples)
  C3 joint (5 folds, 2,664 samples)
  ```
- 保留柱内红色 "0 in holdout (0.0%)" 标注和底部总注释
- 信息不丢失，版式最干净

---

## 3. 代码修改

### 3.1 修改位置

文件：`06_v0.4_code/08_visualization/generate_e45d_figures.py`

修改函数：`make_figure_s5()` 中的 Figure S5(b) 部分

### 3.2 删除代码

删除第 319-321 行（原代码）：

```python
# Total count annotation above each bar
for i, t in enumerate(total):
    ax2.text(i, t + total_sum * 0.02, f"{t:,}", ha="center",
             fontsize=9, color="gray")
```

### 3.3 保留内容

**保留**以下关键元素：
1. x 轴标签中的样本数（第 305-309 行）
2. 柱内红色 "0 in holdout (0.0%)" 标注（第 324-326 行）
3. 底部总注释（第 337-340 行）
4. 真实样本数聚合逻辑（从 JSON `n_samples` 字段）

### 3.4 文档字符串更新

更新脚本开头文档字符串，标记为 FIX02：

```python
"""
1C-E45D-FIX02: 图表/表格预生成草案 (版式修正版)
================================================
...
FIX02 修正 (R85):
  - Figure S5(b) 删除柱顶灰色样本数标签，消除与柱内红色 "0 in holdout" 标签的拥挤
  - 样本数信息保留在 x 轴标签中：65 runs, 34,632 samples / 5 folds, 2,664 samples
...
"""
```

---

## 4. 执行结果

### 4.1 脚本运行成功

执行命令：
```bash
cd /d/我的文件/研究生学术/光学项目/0506新/项目重启_v0.4_BlenderOCS/06_v0.4_code/08_visualization
/c/Users/97466/.conda/envs/ocs_sim/python.exe generate_e45d_figures.py
```

### 4.2 样本数核查通过

脚本输出确认样本数正确（从 JSON 聚合）：
```text
C2 OCS-only total samples: 34,632
C3 image_only total samples: 2,664
C3 joint total samples: 2,664
Grand total: 39,960
```

### 4.3 生成文件清单

所有图表和表格已重新生成：

| 文件 | 格式 | 位置 |
|------|------|------|
| Figure3_yaw_extrapolation_gap_draft | png/pdf | 06_v0.4_code/08_visualization/ |
| Figure4_pitch_anisotropy_draft | png/pdf | 06_v0.4_code/08_visualization/ |
| **FigureS5_sentinel_diagnostic_draft** | **png/pdf** | **06_v0.4_code/08_visualization/** |
| Table2_indicator_reconstruction_draft | md/csv | 06_v0.4_code/08_visualization/ |

**关键修改项**：Figure S5 的 png 和 pdf 文件已按 FIX02 要求更新。

### 4.4 指标数值核查

Table 2 数值与 R82 稳定表一致：

| 通道 | yaw exact | yaw CMAE | yaw within-6 | yaw coarse45 | pitch exact | pitch within-3 |
|------|-----------|----------|--------------|--------------|-------------|----------------|
| C2 OCS-only | 0.00% | 97.0° | 18.89% | 14.53% | 3.03% | 17.75% |
| C3 image_only | 0.00% | 81.4° | 25.57% | 17.96% | 21.20% | 56.07% |
| C3 joint | 0.00% | 81.4° | 26.51% | 18.16% | 19.42% | 51.77% |

---

## 5. 修正效果

### 5.1 Figure S5(b) 版式改进

**修正前（FIX01）**：
- 柱顶有灰色 "2,664" 标签
- 柱内有红色 "0 in holdout (0.0%)" 标签
- 两组文字距离过近，视觉拥挤

**修正后（FIX02）**：
- 删除柱顶灰色样本数标签
- 保留柱内红色 "0 in holdout (0.0%)" 标签
- x 轴标签仍完整显示样本数
- 版式干净，无视觉遮挡

### 5.2 信息完整性

修正后 Figure S5(b) 仍保留完整信息：
1. **样本数**：x 轴标签 "65 runs, 34,632 samples" / "5 folds, 2,664 samples"
2. **holdout 诊断**：柱内红色 "0 in holdout (0.0%)"
3. **总结论**：底部注释 "Across all 39,960 test samples, zero predictions fall inside the corresponding holdout yaw block"

### 5.3 其他图表未实质变更

Figure 3、Figure 4、Table 2 因脚本统一重跑而时间戳更新，但指标设计、数值、版式均未变化。

---

## 6. 红线遵守确认

| 红线项 | 状态 | 说明 |
|--------|------|------|
| 不训练 | ✓ | 未触发任何训练代码 |
| 不改 split/模型/超参/seed | ✓ | 仅修改可视化脚本 |
| 不改 Figure 3/4/Table 2 口径 | ✓ | 指标设计和数值完全一致 |
| 不启动档 B/raw 4-dim/--mode all | ✓ | 未涉及 |
| 不写论文正文正式段落 | ✓ | 仅生成图表草案 |
| 不外推真实 GEO/三轴/暗室 | ✓ | 未涉及 |
| 不改成果区 | ✓ | 图表仍在 08_visualization/ 草案区 |

---

## 7. 待审阅事项

提交 Codex 审阅：

### 7.1 核心审阅点

1. **版式改进有效性**：Figure S5(b) 小柱标签拥挤问题是否已彻底解除？
2. **信息完整性**：删除柱顶标签后，样本数信息是否仍清晰可读？
3. **脚本一致性**：修改是否局限于 Figure S5 版式，未波及其他图表逻辑？

### 7.2 样本数核查

请验证以下数值链：
- JSON 聚合：34,632 / 2,664 / 2,664（total 39,960）
- x 轴标签：与 JSON 聚合一致
- 底部注释：与 JSON 聚合一致

### 7.3 阻断判定

如果 Figure S5(b) 版式仍存在视觉问题，请指出具体位置并建议进一步修正方案（方案 B 或 C）。

---

## 8. 下一步建议

如果 FIX02 通过 Codex 审阅：

1. 稳定 E45D 图表/表格草案到成果区
2. 更新 CLAUDE.md 当前状态为 "E45D-FIX02 通过"
3. 启动 E45C 图表/SI 规划稿（Figure 5、S1/S2/S3/S4/S5 编号体系确认）

如果仍需修正：
- 继续执行 FIX03（采用方案 B：移高灰色标签 + 增加 y-axis headroom；或方案 C：移红色标注到 legend/caption）

---

## 9. 文件清单

### 9.1 修改文件

| 文件 | 修改内容 | 行号 |
|------|----------|------|
| 06_v0.4_code/08_visualization/generate_e45d_figures.py | 删除 Figure S5(b) 柱顶灰色样本数标签代码 | 319-321（删除） |
| 06_v0.4_code/08_visualization/generate_e45d_figures.py | 更新文档字符串为 FIX02 | 1-18 |

### 9.2 生成产物

| 文件 | 类型 | 位置 |
|------|------|------|
| FigureS5_sentinel_diagnostic_draft.png | 图表 | 06_v0.4_code/08_visualization/ |
| FigureS5_sentinel_diagnostic_draft.pdf | 图表 | 06_v0.4_code/08_visualization/ |
| Figure3_yaw_extrapolation_gap_draft.png | 图表（时间戳更新） | 06_v0.4_code/08_visualization/ |
| Figure3_yaw_extrapolation_gap_draft.pdf | 图表（时间戳更新） | 06_v0.4_code/08_visualization/ |
| Figure4_pitch_anisotropy_draft.png | 图表（时间戳更新） | 06_v0.4_code/08_visualization/ |
| Figure4_pitch_anisotropy_draft.pdf | 图表（时间戳更新） | 06_v0.4_code/08_visualization/ |
| Table2_indicator_reconstruction_draft.md | 表格（时间戳更新） | 06_v0.4_code/08_visualization/ |
| Table2_indicator_reconstruction_draft.csv | 表格（时间戳更新） | 06_v0.4_code/08_visualization/ |

### 9.3 本执行报告

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
87_1C-E45D-FIX02_FigureS5小柱标签版式修正_Claude执行报告.md
```

---

## 10. 执行总结

**1C-E45D-FIX02 已完成**，关键修正：

- ✓ 删除 Figure S5(b) 柱顶灰色样本数标签（34,632 / 2,664 / 2,664）
- ✓ 保留 x 轴标签中的样本数信息
- ✓ 保留柱内红色 "0 in holdout (0.0%)" 标注
- ✓ 保留底部总注释
- ✓ 样本数聚合逻辑未变（从 JSON `n_samples` 字段）
- ✓ Figure 3 / Figure 4 / Table 2 指标口径未变
- ✓ 所有红线遵守

**待审阅**：Figure S5(b) 版式改进是否达到稳定进入成果区的标准。
