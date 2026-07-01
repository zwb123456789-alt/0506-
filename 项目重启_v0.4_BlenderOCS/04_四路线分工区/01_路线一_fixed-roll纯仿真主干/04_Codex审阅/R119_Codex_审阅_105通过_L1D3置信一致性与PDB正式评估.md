# R119 Codex 审阅：105 通过，L1D3 置信一致性与 P-DB 正式评估接收

最后更新：2026-07-01  
审阅对象：`02_Claude输出/105_1C-L1D3_置信一致性与PDB正式评估_Claude执行报告.md`  
结果目录：`v0.4_results/13_l1d3_confidence_pdb/`  
上游阶段门：R117 已通过 L1M3 degraded / M-roll / D3 准备材料

## 1. 审阅结论

105 按 R118 完成输入审计、P-DB/template retrieval、neural vs P-DB 一致性、split/Mondrian conformal 与 hard-case index 五组任务，证据链完整、路径分流正确、红线自查合格。Codex 判定为：**通过，进入路线一 C 当前主用成果区。**

本轮接收的是 model-known simulated 条件下的 D3 置信一致性与 P-DB 正式评估。它不等于真实未知目标姿态反演验证，不等于最终概率校准完成，不触发路线一 C 整体闭口，也不启动三轴小项目、T3/L2 光变正式训练或路线二/三/四扩展。

## 2. 接收证据

1. 输入审计通过。`audit/l1d3_input_manifest.csv` 共 104 行，文件缺失 0、字段缺口 0；clean 来源、degraded 来源、val/test 分离、posterior-like 工程口径均已标注。
2. P-DB 正式评估通过。`pdb/l1d3_pdb_retrieval_summary.csv` 显示 test / matched-degraded / neg-L2 下，top1 yaw hit@30 随 G1->G3->G5 单调上升，且随退化强度优雅下降：clean G5=0.949、mild G5=0.892、moderate G5=0.780。
3. P-DB 与 neural ocs_only 互补证据接收。clean G5 中 P-DB top1 cMAE=8.19°、hit@30=0.949，强于 neural ocs_only best cMAE=22.77°、hit@30=0.811；二者 yaw error Spearman≈0，oracle_hit@30=0.960。
4. Conformal 正式评估接收。`conformal/l1d3_conformal_summary.csv` 显示 ocs_only clean α=0.10 的 set_size 随几何收紧：G1=321.8°、G3=245.7°、G5=126.2°，coverage 多接近 target=0.90。
5. 诚实负向观察接收。neural margin 的 risk-coverage 曲线近乎平坦，说明当前工程置信分数区分度弱；image_only conformal 存在系统性略欠覆盖，不能写成置信排序已经强可用。
6. Hard-case index 接收为下一阶段候选输入。`hardcases/l1d3_hardcase_index.csv` 给出 ocs-hard、image-hard、disagreement-hard、ambiguous-flux、robust-easy 五类，共 1231 行；它是候选索引，不是阶段门放行。

## 3. 六个裁决问题

Q1 P-DB 结论：接收“多观测总光度向量含可检索 yaw 信息，且 P-DB 与 neural ocs_only 回归构成互补证据链”为可写结论。P-DB 可升级为正式 D3 分支之一，但必须写为 model-known simulated template retrieval，不得写成真实观测反演成功率。

Q2 置信排序：接收“当前工程置信分数，尤其 neural margin，区分度有限”为诚实负向结论。本轮不下“置信排序强可用”的强结论；后续若要用选择性预测，应在 P-INT-hard 或 stronger degraded 上重新评估，或设计更明确的置信头。

Q3 Conformal：接收 set_size 随几何数收紧为可写结论；image_only 欠覆盖只能写成当前 val->test 分布或误差形态存在偏移，留待更细分 Mondrian-by-mode、更多 val 校准或更难协议复核，不得淡化。

Q4 Clean-template 退化迁移：接收为观察，即退化 query 检索 clean template 略优于 matched-degraded，提示 clean 模板库更干净且退化观测仍可稳健匹配。两种口径都保留，后续不得混写。

Q5 degraded G3 image/joint 缺口：接收本轮以现有 R116 矩阵通过；不要求补训。若后续需要 degraded G3 image/joint，必须另行由 Codex 放行，不得补写到本轮结论中。

Q6 hard-case / 下一步：接收 hard-case index 作为 P-INT-hard / stronger degraded 候选依据。是否启动 degraded-severe 或 P-INT-hard 小矩阵，需要 R120 另行任务单；R119 本身不放行新训练。

## 4. 后续边界

R119 后，路线一 C 在当前主线中形成了更完整的证据链：R113 关闭 single-frame 判据补救轴，R115 接收 clean/P-INT 多几何 OCS 正结果，R117 接收退化真实性与 M-roll 边界，R119 接收 D3/P-DB/conformal 置信一致性正式评估。

下一步建议优先做路线一 C 的阶段性 Results 非正文证据包，把 R113/R115/R117/R119 串成可审稿的结果叙事与图表清单；同时保留 R119 hard-case index 作为后续 degraded-severe / P-INT-hard 小矩阵训练的候选输入。未另行放行前，不启动新训练、三轴小项目或论文正文正式改写。
