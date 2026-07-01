# C1/C2 OCS-only 图表与 SI 资产稳定包（E36，R69 通过）

最后更新：2026-06-26  
状态：Codex R69 审阅通过

## 稳定资产

```text
06_v0.4_code/08_visualization/
  generate_figure2_fixed.py
  extract_s2_pure_python.py
  Figure2_yaw_block_holdout_fixed.png
  Figure2_yaw_block_holdout_fixed.pdf

v0.4_results/05_c2_screening/
  supplementary_table_s2_per_fold_results.csv
  supplementary_table_s2_first10_rows.md

04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  66_1C-E36_C1C2_OCS-only图表与SI资产生成_Claude执行报告_Part1.md
  66_1C-E36_C1C2_OCS-only图表与SI资产生成_Claude执行报告_Part2.md
  66_1C-E36_C1C2_OCS-only图表与SI资产生成_Claude执行报告_Part3.md
  67_1C-E36-FIX01_图表脚本与S2提取修正_Claude执行报告.md
  67_1C-E36-FIX01_执行总结.md
  68_1C-E36-FIX02_归档路径与Figure2脚本退出码修正_Claude执行报告.md
  69_1C-E36-FIX03_阶段门口径与ASCII声明修正_Claude执行报告.md
```

## 稳定口径

- Figure 2 使用 R65 split：five-fold aggregate test coverage = 72/72 yaw bins。
- S2 per-fold table 使用 65 行真实 C2 fold 结果，读取 `final_metrics.test`。
- C2 OCS-only 核心结果仍为 13 configs x 5 folds 全部 `yaw_acc = 0.00%`。
- Within-3 chance level 仍按 `7/72 = 9.72%`；pitch accuracy 仅作二级诊断。

## 红线

本成果包不放行 C3、训练、新实验、论文正文正式改写、三轴小项目或路线二/三/四。
