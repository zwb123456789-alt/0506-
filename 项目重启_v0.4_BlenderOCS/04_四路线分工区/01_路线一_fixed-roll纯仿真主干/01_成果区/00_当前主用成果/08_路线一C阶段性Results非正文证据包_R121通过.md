# 路线一 C 阶段性 Results 非正文证据包成果摘要（R121 通过）

最后更新：2026-07-01  
来源报告：`02_Claude输出/106_1C阶段性Results非正文证据包_Claude执行报告.md`  
Codex 审阅：`04_Codex审阅/R121_Codex_审阅_106通过_1C阶段性Results非正文证据包.md`  
证据包目录：`v0.4_results/14_route1c_stage_results_pack/`

## 1. 成果定位

本成果是路线一 C 阶段性 Results 非正文证据包，用于把 R113/R115/R117/R119 的已通过成果整理成后续写作、图表、SI、claim 边界和待补实验的稳定依据。

它不是论文正文，不是投稿摘要，不是路线一 C 整体闭口，也不放行新训练、新渲染、T3/L2、三轴小项目或路线二/三/四扩展。

## 2. 包内主交付

证据包位于：

```text
v0.4_results/14_route1c_stage_results_pack/
```

核心文件：

```text
tables/route1c_evidence_chain.csv
text/route1c_evidence_chain.md
tables/route1c_figure_plan.csv
text/route1c_figure_plan.md
text/route1c_results_narrative_skeleton.md
tables/route1c_claim_boundary_table.csv
text/route1c_claim_boundary_table.md
tables/route1c_next_experiment_options.csv
text/route1c_next_experiment_options.md
audit/route1c_stage_results_manifest.csv
audit/route1c_stage_results_manifest.md
figures/copy_R115_*.png
figures/copy_R119_*.png
```

Codex 复核 manifest 共 60 行，非 PENDING 项缺失 0；106 报告和 7 张复用图副本均实测存在。

## 3. 可用结论

当前可稳定组织为四条证据链：

1. R113：single-frame / yaw-block 下的负结果是条件性负结果；B6 关闭判据/输出头补救轴，但不等于光度无用或路线一 C 失败。
2. R115：model-known / fixed-roll / clean / P-INT 下，OCS-only 多观测总光度向量随 L1-G1 -> L1-G3 -> L1-G5 单调增益。
3. R117：OCS-only 多几何增益在 mild/moderate 物理退化下保持；M-roll 中 ±15° 未直接推翻 fixed-roll，±30° 明显敏感。
4. R119：P-DB 作为 simulated template retrieval 证明多观测总光度向量含可检索 yaw 信息；conformal set_size 随几何收紧。

所有可写 claim 必须限定为 model-known simulated。P-DB 必须写为 template retrieval；conformal 必须写为当前 simulated split 下的校准/集合宽度结果。

## 4. 必须保留的负向观察

后续 Results/SI 中不得淡化：

```text
P-EXT yaw-block strict extrapolation 仍坍缩；
clean P-INT 下 image_only 近饱和，joint 增益受天花板限制；
degraded final 口径存在 G5 joint moderate 检查点敏感；
neural margin risk-coverage 近平坦，置信区分度弱；
image_only conformal 略欠覆盖；
P-DB oracle 只是上界，不代表可无监督选中正确一方。
```

## 5. 禁止扩大

不得把本成果写成：

```text
真实未知目标姿态反演系统已经实现；
真实望远镜验证、field-proven 或 operational-ready；
GEO 数据库有三轴姿态真值；
P-EXT yaw-block 已解决；
joint 强互补性已证明；
Bayesian posterior 或最终概率校准已完成；
P-DB 是真实观测反演成功率；
路线一 C 整体闭口；
三轴小项目、T3/L2 或路线二三四扩展已启动。
```

## 6. 下一步使用

优先推荐 Option A：基于本证据包正式整理 Results/SI 图表与写作准备包，只做轻量制图、表格组织和受控文本草案，不新训练、不新渲染、不新增科学结论。

Option B（degraded-severe / P-INT-hard）和 Option C（joint/full-2664 M-roll）均需另行 Codex 阶段门；不能由 R121 自动放行。
