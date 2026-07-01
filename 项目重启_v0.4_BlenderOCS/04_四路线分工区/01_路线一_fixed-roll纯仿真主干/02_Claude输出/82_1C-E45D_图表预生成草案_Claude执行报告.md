# 1C-E45D 图表/表格预生成草案 — Claude 执行报告

最后更新：2026-06-27
执行端：Claude
依据审阅：R83 Codex 审阅（E45C 通过，图表/SI 规划体系校正稳定 §5）
性质：D 类图表生成（不训练、不改模型、不写论文正文）

## 0. 执行声明

本报告只读取 E45A JSON 数值资产，生成图表草案和表格。未触发训练、代码修改、split/模型/超参变更或论文正文正式改写。

## 1. 输出资产清单

```text
06_v0.4_code/08_visualization/
  generate_e45d_figures.py               # 新增可视化脚本
  Figure3_yaw_extrapolation_gap_draft.png  # P0 主图
  Figure3_yaw_extrapolation_gap_draft.pdf
  Figure4_pitch_anisotropy_draft.png       # P1 辅助图
  Figure4_pitch_anisotropy_draft.pdf
  FigureS5_sentinel_diagnostic_draft.png   # P1 SI 双 panel
  FigureS5_sentinel_diagnostic_draft.pdf
  Table2_indicator_reconstruction_draft.md  # P0 主表
  Table2_indicator_reconstruction_draft.csv
```

所有图表数值与 R82 §3 / E45B 成果区 Table 完全一致，来源均为 E45A JSON。

## 2. 数值验证

从 E45A JSON 实时聚合的均值与 R82 稳定表对照：

| 指标 | R82 值 | E45D 脚本输出 | 一致 |
|---|---|---|---|
| C2 yaw CMAE | 96.97 deg | 96.97 deg | ✅ |
| C2 yaw within-3 | 9.96% | 9.96% | ✅ |
| C2 yaw within-6 | 18.89% | 18.89% | ✅ |
| C2 yaw coarse45 | 14.53% | 14.53% | ✅ |
| C2 pitch exact | 3.03% | 3.03% | ✅ |
| C2 pitch within-3 | 17.75% | 17.75% | ✅ |
| C3 image_only yaw CMAE | 81.44 deg | 81.44 deg | ✅ |
| C3 image_only yaw within-6 | 25.57% | 25.57% | ✅ |
| C3 image_only yaw coarse45 | 17.96% | 17.96% | ✅ |
| C3 image_only pitch exact | 21.20% | 21.20% | ✅ |
| C3 image_only pitch within-3 | 56.07% | 56.07% | ✅ |
| C3 joint yaw CMAE | 81.39 deg | 81.39 deg | ✅ |
| C3 joint yaw within-6 | 26.51% | 26.51% | ✅ |
| C3 joint yaw coarse45 | 18.16% | 18.16% | ✅ |
| C3 joint pitch exact | 19.42% | 19.42% | ✅ |
| C3 joint pitch within-3 | 51.77% | 51.77% | ✅ |

全部一致。误差线为 SEM（standard error of the mean），C2 基于 65 runs，C3 基于 5 folds。

## 3. 各图设计说明

### Figure 3（Yaw extrapolation gap 主图，三 panel）

- **(a) Yaw Circular MAE**：越低越好。C2 96.97 deg 差于 chance 90 deg；C3 image/joint 81.4 deg 略优于 chance。
- **(b) Yaw Within-6 Bins**：越高越好。C2 18.9% 贴近 chance 18.1%；C3 image/joint 25.6-26.5% 微高于 chance。
- **(c) Yaw Coarse-45° Accuracy**：越高越好。C2 14.5% 接近 chance 12.5%；C3 image/joint 18.0-18.2% 略高于 chance。

每 panel 均标注 chance 参考线。设计遵循 R83 裁决：CMAE / within-6 / coarse45 分开为独立 panel，避免混排误导。

### Figure 4（Pitch anisotropy，双 panel）

- **(a) Pitch Exact-Bin Accuracy**：C3 image/joint 21.2%/19.4% 远超 chance 2.7%。C2 OCS-only 仅 3.0%。
- **(b) Pitch Within-3 Bins**：C3 image/joint 56.1%/51.8% 远超 chance 18.9%。C2 OCS-only 仅 17.8%。

展示 fixed-roll 设定下 yaw/pitch 各向异性：图像通道可学到 pitch 姿态信息，但 yaw 在 cross-block holdout 下无法外推。

### Figure S5（哨兵 + 诊断，双 panel）

- **(a) Exact-Bin Yaw Accuracy — Sentinel Indicator**：三通道均为 0.00%，标注醒目。chance 1.39% 参考线。
- **(b) E45A Holdout-Prediction Diagnostic**：全部 39,960 测试样本中，0 个预测 yaw bin 落入 holdout 块，确认预测系统性坍缩到训练可见 yaw 区间。

Figure S5 只承担哨兵与失败模式归档，不承载物理不可观测 claim。

### Table 2（指标重构主表）

包含 7 个指标 × 3 通道 + chance + random split reference，均标注 SEM。数值格式与 R82 §3 一致。CSV 可直接导入 LaTeX/Excel。

## 4. 已知限制

```text
1. C3 SEM 基于 5 folds（n=5），image_only 和 joint 的 coarse45 SEM 较大（5.3-5.6%），
   因为 coarse45 的 per-fold 方差高。这不是错误，而是 fold 间外推难度差异的真实反映。
2. C2 SEM 基于 65 runs，精度较高。
3. Figure S5(b) 的总样本数为近似值（65×555 和 5×555），实际 per-fold n_samples 略有不同
   （518-555），图表中标注了 "≈" 和具体脚注。
4. 图表为 draft 质量，未做期刊级排版优化（字体大小、颜色空间、图例位置等需投稿前精修）。
```

## 5. 数据来源

| 数据 | 来源 |
|---|---|
| C2 65-run per-config/fold | `v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c2_extended_metrics.json` |
| C3 image_only/joint 5-fold | `v0.4_results/07_negative_diagnosis/e45a_inference_regroup/c3_extended_metrics.json` |
| Chance baselines | R82 §3 / E45B 成果区 |
| Random split reference | R77 §5 |

## 6. 红线确认

```text
✅ 未训练
✅ 未改任何代码（仅新增可视化脚本，只读 JSON 输入）
✅ 未改 split / 模型 / 超参 / seed
✅ 未启动档 B、raw 4-dim OCS-only 或 --mode all
✅ 未写论文正文正式段落
✅ 未改成果区
✅ 未外推真实 GEO、三轴姿态、暗室实验或所有模型
✅ 输出位置：图表进 06_v0.4_code/08_visualization/，执行报告进 02_Claude输出/
✅ 可视化脚本可复现：任何时候重新运行 generate_e45d_figures.py 即可
```

## 7. 待 Codex 审阅事项

1. Figure 3 三 panel 的指标选择和面板设计是否与 R83 裁决一致。
2. Table 2 的 SEM 标注格式是否满足投稿要求。
3. Figure S5 的双 panel 哨兵+诊断是否准确传达了 extrapolation gap 的机制解释。
4. E45D 通过后，是否放行后续 S1/S2/S3/S4（C2 分布箱线图、CMAE vs within-6 散点、training curves、overlap 热图）的预生成。
