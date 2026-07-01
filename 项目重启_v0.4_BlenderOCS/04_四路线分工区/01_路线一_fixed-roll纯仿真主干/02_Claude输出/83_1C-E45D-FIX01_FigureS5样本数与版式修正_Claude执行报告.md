# 1C-E45D-FIX01 Figure S5 样本数与版式修正 — Claude 执行报告

最后更新：2026-06-27
执行端：Claude
依据审阅：R84 Codex 审阅（E45D NEEDS FIX01 §3）
性质：D 类图表修正（不训练、不改模型、不改 split）

## 0. 执行声明

本报告只修正 E45D 图表草案的 Figure S5 样本数和版式问题，以及 Figure 4 顶部留白。未触发训练、模型变更、split 修改、超参调整或论文正文改写。

## 1. 修正内容

### 1.1 Figure S5(b) 样本数修正

| 通道 | 修正前（硬编码） | 修正后（JSON n_samples 聚合） | 数据来源 |
|---|---|---|---|
| C2 OCS-only | 36,075 (65×555) | **34,632** | `c2_extended_metrics.json` 逐条目 `n_samples` 求和 |
| C3 image_only | 2,775 (5×555) | **2,664** | `c3_extended_metrics.json` `mode==image_only` 的 `n_samples` 求和 |
| C3 joint | 2,775 (5×555) | **2,664** | `c3_extended_metrics.json` `mode==joint` 的 `n_samples` 求和 |
| **Total** | **41,625（矛盾）** | **39,960（一致）** | — |

修正前分通道柱值相加 = 41,625，但图中底部文字写 "Across all 39,960 test samples"。修正后三柱相加 = 39,960，与 E45A 真实总样本数和图中底部 footnote 完全一致。

修正方法：`load_data()` 函数在遍历 JSON 时累积 `n_samples`，返回 `(data_dict, sample_counts)`。`make_figure_s5()` 接收 `sample_counts` 参数，不再硬编码。

### 1.2 Figure S5(b) 版式修正

| 问题 | 修正前 | 修正后 |
|---|---|---|
| 文本遮挡 | "0 in holdout" 在柱顶标注 + 底部红字注释，两者重叠 | "0 in holdout" 在柱内 45% 高度处；总注释移到图外 `fig.text()` 作为 footnote，不会被柱体遮挡 |
| 分类标签 | "65 runs × 555±" 等含 ± 的模糊标注 | 标注实际样本数："65 runs, 34,632 samples" / "5 folds, 2,664 samples" |

### 1.3 Figure 4 y 轴留白修正

```text
修正前：ax.set_ylim(bottom=0) — 21.2% 标签紧贴上边框
修正后：ax.set_ylim(bottom=0, top=max_val * 1.25) — 顶部留白 25%
```

## 2. 重新生成的文件

```text
06_v0.4_code/08_visualization/
  generate_e45d_figures.py                    # 修正后脚本
  Figure3_yaw_extrapolation_gap_draft.png      # 重新生成（无变更）
  Figure3_yaw_extrapolation_gap_draft.pdf
  Figure4_pitch_anisotropy_draft.png           # 重新生成（+y轴留白）
  Figure4_pitch_anisotropy_draft.pdf
  FigureS5_sentinel_diagnostic_draft.png       # 重新生成（+样本数+版式）
  FigureS5_sentinel_diagnostic_draft.pdf
  Table2_indicator_reconstruction_draft.md     # 重新生成（无变更）
  Table2_indicator_reconstruction_draft.csv
```

Figure 3 和 Table 2 数值未变，仅因脚本统一重跑而覆盖时间戳。

## 3. 验证：修正前后数值一致性

全部 yaw/pitch 指标均值与 R82 稳定表一致，sample_counts 聚合与 E45A 事实一致：

```text
C2 OCS-only total samples: 34,632
C3 image_only total samples:   2,664
C3 joint total samples:        2,664
Grand total:                  39,960
```

## 4. 脚本修改清单

| 修改点 | 描述 |
|---|---|
| `load_data()` | 遍历 JSON 时累积 `n_samples`；返回 `(data_dict, sample_counts)` |
| `make_figure_s5()` | 新增 `sample_counts` 参数；`total` 数组从 `sample_counts` 取；分类标签包含实际样本数；底部注释移到 `fig.text()` 图外 |
| `make_figure4()` | `set_ylim(bottom=0, top=max_val*1.25)` 替代 `set_ylim(bottom=0)` |
| `main()` | 解包 `data, sample_counts = load_data()`；传 `sample_counts` 到 `make_figure_s5()` |
| 文档字符串 | 更新为 `1C-E45D-FIX01` 并列出修正项 |

## 5. 红线确认

```text
✅ 未训练
✅ 未改 split / 模型 / 超参 / seed
✅ 未改任何训练、推理或数据生成代码（仅修改可视化脚本的数据读取和显示逻辑）
✅ 未启动档 B、raw 4-dim OCS-only 或 --mode all
✅ 未写论文正文正式段落
✅ 未改成果区
✅ 未外推真实 GEO、三轴姿态、暗室实验或所有模型
✅ 所有图表数值与 R82 稳定表一致
✅ Figure S5(b) 样本数 34,632 / 2,664 / 2,664 从 JSON n_samples 字段聚合，总注释 39,960 与分通道柱值相加一致
✅ 文本遮挡已消除
✅ 输出位置：图表进 06_v0.4_code/08_visualization/，执行报告进 02_Claude输出/
```

## 6. 参考审阅

```text
R84: 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
     R84_Codex_审阅_1C-E45D需FIX01_FigureS5样本数与版式修正.md
R83: 图表/SI 规划体系校正
R82: 指标重构与外推鸿沟叙事
```
