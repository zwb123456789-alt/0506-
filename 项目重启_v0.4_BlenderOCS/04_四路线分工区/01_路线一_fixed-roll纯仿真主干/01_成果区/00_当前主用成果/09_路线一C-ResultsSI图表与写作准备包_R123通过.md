# 路线一 C Results/SI 图表与写作准备包成果摘要（R123 通过）

最后更新：2026-07-01  
来源报告：`02_Claude输出/107_1C-ResultsSI图表与写作准备包_Claude执行报告.md`  
Codex 审阅：`04_Codex审阅/R123_Codex_审阅_107通过_1C-ResultsSI图表与写作准备包.md`  
结果包目录：`v0.4_results/15_route1c_results_si_preparation_pack/`

## 1. 成果定位

本成果是路线一 C 的 Results/SI 图表与写作准备包，用于把 14 号阶段性证据包推进为可审阅的主图、SI、受控 Results 草案、数字核验和红线清单。

它不是最终论文正文，不是投稿摘要，不是路线一 C 整体闭口，也不放行新训练、新渲染、T3/L2、三轴小项目或路线二/三/四扩展。

## 2. 主交付

15 号包包含 36 个本轮文件：

```text
figures_main/Fig1-Fig5 (.png + .pdf)
figures_si/SI1-SI4 (.png + .pdf), SIx1/SIx2 (.png)
tables/main_figure_source_map.csv
tables/si_figure_source_map.csv
tables/SI5_manifest_table.csv
tables/paragraph_claim_evidence_map.csv
tables/claim_figure_table_map.csv
text/main_figure_captions_draft.md
text/si_captions_draft.md
text/results_candidate_draft_controlled.md
audit/numeric_consistency_check.csv/.md
audit/generated_files_manifest.csv/.md
audit/redline_self_check.csv
scripts/make_figures.py
scripts/make_audit.py
```

Codex 复核：36 个 manifest 文件缺失 0；11 张 PNG 尺寸正常且非空；数字核验 33 项 PASS、0 CONFLICT。

## 3. 可用内容

可以作为后续正式 Results 写作输入的材料：

1. 主图 Fig.1-Fig.5：协议示意、clean/P-INT 多几何 OCS 增益、degraded 增益保持、P-DB/neural 互补、conformal set_size 与负向观察。
2. SI 图表：B6 single-frame 收口、P-EXT stress test、M-roll 边界、hard-case index、manifest、P-DB/neural 误差散点、confidence decile。
3. 受控 Results 草案 R0-R5：每段绑定 evidence path、linked figures、allowed/forbidden wording 与 risk tag。
4. 数字核验与 redline self-check：用于后续正式写作时防止 claim 漂移。

## 4. 口径修正

后续统一使用以下 image_only conformal coverage 记法：

```text
image_only clean α=0.10 coverage:
L1-G1=0.892, L1-G3=0.865, L1-G5=0.835
概述：≈0.83-0.89，低于 target=0.90，属于略欠覆盖。
```

14 号骨架中的 `≈0.83-0.85` 视为较窄旧记法，不影响“image_only 欠覆盖”的结论。

## 5. 禁止扩大

不得把本成果写成：

```text
真实未知目标姿态反演系统已经实现；
真实望远镜验证、field-proven 或 operational-ready；
P-EXT yaw-block 已解决；
joint 强互补性已证明；
P-DB 是真实观测反演成功率；
conformal 是 Bayesian posterior 或最终概率校准；
路线一 C 整体闭口；
三轴小项目、T3/L2 或路线二三四扩展已启动。
```

## 6. 下一步使用

优先可做 Option A2：基于 15 号包由 Codex/作者推进正式 Results 段落与论文图表版本，仍不新增实验。

若要补强互补性或 roll 边界，则必须另行下达 degraded-severe / P-INT-hard 或 joint/full-2664 M-roll 阶段门。
