# 105 1C-L1D3 置信一致性与 P-DB 正式评估 Claude 执行报告

最后更新：2026-07-01  
任务来源：`04_Codex审阅/R118_Codex_任务单_1C-L1D3置信一致性与PDB正式评估.md`  
上游阶段门：R117 已通过 104，接收 L1M3 degraded / M-roll / D3 准备材料  
执行端：Claude  
任务名：`1C-L1D3_置信一致性与PDB正式评估`

---

## 1. 任务结论摘要

**完成（达到强接收标准）。**

- 子任务 A：正式输入 manifest 与字段审计完成，104 行 run×split×select 全部字段完整，零缺口。
- 子任务 B：P-DB / template retrieval 正式评估，完成 clean / degraded-mild / degraded-moderate 的 G1/G3/G5 × neg-L2/cosine/zscore-neg-L2 × val/test 全矩阵，含 matched-degraded 与 clean-template 两种口径（90 组合摘要 + 24975 per-query 行 + 810 分层行）。
- 子任务 C：neural vs P-DB 一致性、互补四象限、置信 decile、risk-coverage，覆盖 ocs_only/image_only/joint × final/best × clean/mild/moderate（46 相关性行 + 46 互补行 + 13616 per-attitude 合并行）。
- 子任务 D：split-conformal + Mondrian conformal 正式评估，覆盖 neural 与 P-DB，α∈{0.05,0.10,0.20}（192 摘要行 + 512 Mondrian 行）。
- 子任务 E：五类 hard-case 索引（ocs-hard/image-hard/disagreement-hard/ambiguous-flux/robust-easy 全覆盖，1231 行）+ P-INT-hard 设计建议。
- 6 张图表全部生成。

核心可审计观察（绑定输出文件，详见 §6–§9）：

```text
1. P-DB 多几何单调性在所有退化级别保持（test, matched-degraded, neg-L2, top1 yaw hit@30）：
   clean    G1=0.291 G3=0.821 G5=0.949
   mild     G1=0.270 G3=0.774 G5=0.892
   moderate G1=0.230 G3=0.625 G5=0.780  → 随几何单调增、随退化优雅收缩。
2. P-DB(检索) 在 ocs_only 证据链上强于 neural 回归：clean G5 P-DB top1 cMAE=8.19° hit@30=0.949，
   而 neural ocs_only best cMAE=22.77° hit@30=0.811。说明多观测总光度向量含 yaw 信息
   未被神经回归充分利用（可作为非神经证据链）。
3. neural 与 P-DB 的 yaw error 几乎不相关（clean G5 spearman: ocs_only=0.066/image=-0.085/joint=0.013），
   互补空间存在：clean G5 ocs_only 象限 both✓=237 / neural_only=3 / pdb_only=44 / both✗=12，
   oracle(either)hit@30=0.960 高于任一单独证据链。
4. conformal set_size 随几何单调收紧（neural ocs_only clean α=0.10）：G1=321.8° → G3=245.7° → G5=126.2°；
   joint 最紧(12.9°)、P-DB(10.0°)，coverage 多接近 target 0.90。image_only 系统性略欠覆盖(0.83–0.85)。
```

---

## 2. 已读文件与遵守的红线

已读文件：

```text
CLAUDE.md（大根 + v0.4 工作区）
R118_Codex_任务单_1C-L1D3置信一致性与PDB正式评估.md
R117_Codex_审阅_104通过_L1M3退化真实性与Mroll边界探针.md
R115_Codex_审阅_103通过_L1M2多几何OCS第一阶段正结果.md（引用结论）
R113_Codex_审阅_102通过_B6判据轴闭口并放行L1M2阶段门.md（引用结论）
02_Claude输出/104_1C-L1M3Mroll_退化真实性与roll边界探针_Claude执行报告.md
06_v0.4_code/07_training/build_d3_confidence_inputs.py
06_v0.4_code/07_training/dataset_l1m2_multigeometry.py
06_v0.4_code/07_training/train_l1m2_multigeometry.py
06_v0.4_code/07_training/degrade_l1m3_images.py
06_v0.4_code/07_training/train_l1m3_degraded.py（确认退化 flux 口径）
v0.4_results/11_l1m2_multigeometry_ocs/（runs、samples_*.npz、audit）
v0.4_results/12_l1m3_degraded_mroll/（degraded runs、audit、d3 smoke）
```

遵守的红线（自查见 §11）：只改 `项目重启_v0.4_BlenderOCS/` 内部；新结果全部写入 `v0.4_results/13_l1d3_confidence_pdb/`，未覆盖 R115/R117 结果目录；未改任何旧脚本、旧 metrics/test 文件；报告写入 `02_Claude输出/105`；未写成果区、未生成 Codex 审阅文件、未改 CLAUDE.md；未启动新训练、新渲染、backbone 更换或开放超参搜索；P-DB/conformal/posterior-like 严格按工程口径标注。

---

## 3. 新增 / 修改脚本清单

均为**新增，未修改任何旧脚本**（旧结果链不受影响）：

```text
06_v0.4_code/07_training/l1d3_common.py                        新增：共享模块（split/退化flux/检索/指标）
06_v0.4_code/07_training/build_l1d3_pdb_templates.py           新增：子任务A 输入索引+字段审计
06_v0.4_code/07_training/eval_l1d3_pdb_retrieval.py            新增：子任务B P-DB 正式评估
06_v0.4_code/07_training/eval_l1d3_confidence_consistency.py   新增：子任务C neural vs P-DB 一致性
06_v0.4_code/07_training/eval_l1d3_conformal.py                新增：子任务D split/Mondrian conformal
06_v0.4_code/07_training/build_l1d3_hardcase_index.py          新增：子任务E hard-case 索引+设计建议
06_v0.4_code/07_training/plot_l1d3_confidence_pdb.py           新增：图表生成
```

复用原则：`l1d3_common.py` 通过 import 复用 `dataset_l1m2_multigeometry.build_multigeometry_table/fit_flux_transform/apply_flux_transform`、`train_l1m2_multigeometry.split_pint/split_pext/yaw_circ_err`、`degrade_l1m3_images.DEGRADE_LEVELS/degrade_flux_vector`。退化 flux 严格按训练同口径（`degrade_flux_vector(flux, params, record_id, salt="flux")`）确定性复现，保证 P-DB 与 neural 在同一退化观测上对齐。命令环境统一 `"C:\Users\97466\.conda\envs\ocs_sim\python.exe"`。

派生自 R117 `build_d3_confidence_inputs.py`：本轮不覆盖它，另起 `l1d3_common.py` + 五个正式脚本，行为向上兼容（P-DB neg-L2 clean G5 top1 hit@30=0.949 与 R117 smoke 逐值一致，验证口径未漂移）。

---

## 4. 新生成结果目录清单

全部位于 `v0.4_results/13_l1d3_confidence_pdb/`（未覆盖 `11_l1m2` / `12_l1m3`）：

```text
audit/
  l1d3_input_manifest.csv (104 数据行)      A 正式输入索引 + 字段完整性
  l1d3_input_manifest.json                  A 机读摘要 + 上游 leakage 引用
  l1d3_input_audit.md                       A 人读审计报告
pdb/
  l1d3_pdb_template_manifest.csv            B template 库清单（train-only）
  l1d3_pdb_retrieval_summary.csv (90 行)    B 组合摘要
  l1d3_pdb_retrieval_per_query.csv (24975)  B per-query top1/topk
  l1d3_pdb_retrieval_strata.csv (810)       B yaw-sector/pitch-bin 分层
  l1d3_pdb_key_findings.md                  B 关键结论
consistency/
  l1d3_neural_pdb_joined_per_attitude.csv (13616)  C per-attitude 合并
  l1d3_error_correlation_summary.csv (46)   C 错误相关性
  l1d3_complementarity_cases.csv (46)       C 互补四象限
  l1d3_confidence_deciles.csv (640)         C 置信 decile
  l1d3_risk_coverage.csv (1280)             C risk-coverage
  l1d3_consistency_key_findings.md          C 关键结论
conformal/
  l1d3_conformal_summary.csv (192)          D split-conformal
  l1d3_conformal_per_sample.csv (18944)     D per-sample 覆盖标记(α=0.10)
  l1d3_mondrian_summary.csv (512)           D Mondrian 分层
  l1d3_conformal_key_findings.md            D 关键结论
  figures/conformal_setsize.png
hardcases/
  l1d3_hardcase_index.csv (1231)            E 五类 hard-case
  l1d3_hardcase_summary.md                  E 计数摘要
  l1d3_recommended_pinthard_design.md       E 下一步设计建议（不放行）
figures/
  pdb_gain_curve.png / neural_vs_pdb_error_scatter.png / confidence_decile_error.png
  risk_coverage_curves.png / complementarity_quadrants.png
```

---

## 5. 输入索引与审计复核结果（子任务 A）

`build_l1d3_pdb_templates.py` 产出 `audit/l1d3_input_manifest.{csv,json}` + `l1d3_input_audit.md`：

```text
- 索引 104 行（run × split × select），字段完整 104，文件缺失 0，字段缺口 0。
- 每行含 source/protocol/geometry_group/mode/degrade_level/split/select/path/n_samples/字段完整性。
- clean 源标清为 11_l1m2（R115；val 由 R117-A1 checkpoint+确定性split 恢复，Δcmae=0.0）；
  degraded 源标清为 12_l1m3（R116；退化观测按 record_id 确定性复现）。
- val/test 严格分开；报告与所有脚本中，校准/阈值/quantile 只用 val，test 仅最终评估。
- posterior-like（top5 score/entropy/margin）在 manifest 与所有输出中标注为工程候选分数，非 Bayesian posterior。
- 上游 l1m2_transform_leakage_check.json 引用入 manifest.json（train-only transform 无泄漏、split 无交集）。
```

矩阵覆盖（test/best 存在性）：ocs_only 覆盖 clean/mild/moderate × G1/G3/G5；image_only/joint 覆盖 clean × G1/G3/G5 与 mild/moderate × G1/G5（degraded 侧无 G3 image/joint run，如实标注）；P-EXT 仅 ocs_only × G1/G3/G5。

---

## 6. P-DB / template retrieval 正式评估结果（子任务 B）

`eval_l1d3_pdb_retrieval.py`。template 库只取 train split 多观测总光度向量。

**多几何单调性（test, matched-degraded, neg-L2, top1 yaw hit@30）：**

| degrade_level | G1 | G3 | G5 |
|:--|--:|--:|--:|
| clean | 0.291 | 0.821 | 0.949 |
| degraded-mild | 0.270 | 0.774 | 0.892 |
| degraded-moderate | 0.230 | 0.625 | 0.780 |

**相似度对比（test, G5, matched-degraded, top1 yaw cMAE° / hit@30）：**

| degrade_level | neg-L2 | cosine | zscore-neg-L2 |
|:--|:--|:--|:--|
| clean | 8.19 / 0.949 | 19.12 / 0.878 | 见 CSV |
| degraded-mild | 17.42 / 0.892 | — | — |
| degraded-moderate | 34.71 / 0.780 | — | — |

（完整三相似度 × 三退化 × 三几何见 `l1d3_pdb_retrieval_summary.csv`。）

**top-k-best 上界（test, G5, neg-L2, yaw hit@30）：** clean top10-best=1.000；mild=0.997；moderate=0.973。表示正确姿态几乎总落在 top-10 候选内（oracle 上界，非可无监督选中）。

**clean-template 退化迁移探针（test G5, neg-L2, top1 yaw hit@30）：** mild matched=0.892 vs clean-template=0.919；moderate matched=0.780 vs clean-template=0.801。clean 模板库更干净，退化 query 检索 clean 模板反而略优。

严格口径：P-DB 是 model-known simulated template retrieval，top-k 是候选姿态检索，不是 Bayesian posterior，也不是真实观测反演成功率。

---

## 7. neural vs P-DB 一致性 / 互补 / 置信排序结果（子任务 C）

`eval_l1d3_confidence_consistency.py`。按 record_id join neural 与 P-DB。

**错误相关性（test, best, G5）：**

| degrade_level | mode | neural cMAE | pdb cMAE | spearman |
|:--|:--|--:|--:|--:|
| clean | ocs_only | 22.77 | 8.19 | 0.066 |
| clean | image_only | 8.57 | 8.19 | -0.085 |
| clean | joint | 3.20 | 8.19 | 0.013 |

neural 与 P-DB error 几乎不相关，说明二者在不同姿态出错。

**互补四象限（test, best, G5, neural vs P-DB neg-L2）：**

| degrade_level | mode | both✓ | neural_only | pdb_only | both✗ | oracle_hit@30 |
|:--|:--|--:|--:|--:|--:|--:|
| clean | ocs_only | 237 | 3 | 44 | 12 | 0.960 |
| clean | joint | 281 | 15 | 0 | 0 | 1.000 |
| degraded-moderate | ocs_only | 166 | 17 | 65 | 48 | 0.838 |

ocs_only 上 P-DB 检索显著补充 neural 回归（pdb_only≫neural_only）；joint 单帧图像已近饱和，互补空间小。

**置信排序（risk-coverage，test G5 clean）：** neural margin 的 risk-coverage 曲线接近平坦（cov=0.2 时 cMAE=24.3° vs cov=1.0 时 22.8°），说明 **neural margin 作为工程置信分数区分度弱**；P-DB retrieval margin 略有区分（cov=0.6 时 cMAE=8.99° 优于全量 8.19° 附近波动）。此为诚实负向观察，如实记录，不夸大置信可用性。

---

## 8. split-conformal / Mondrian conformal 结果（子任务 D）

`eval_l1d3_conformal.py`。有限样本修正 quantile level=ceil((n+1)(1-α))/n；只用 val 校准。

**split-conformal（test, best, α=0.10）coverage / set_size(°)：**

| method/mode | degrade | G1 | G3 | G5 |
|:--|:--|:--|:--|:--|
| neural/ocs_only | clean | 0.899/322 | 0.912/246 | 0.902/126 |
| neural/joint | clean | — | — | 0.902/12.9 |
| neural/image_only | clean | — | — | 0.835/32.3 |
| pdb-neg-L2 | clean | — | — | 0.929/10.0 |

关键观察：
- coverage 多接近 target 0.90，split-conformal 在本 simulated split 下自洽。
- set_size 随几何单调收紧（neural ocs_only clean：G1=321.8° → G3=245.7° → G5=126.2°），与 OCS 多观测信息量增益一致。
- set_size 排序 P-DB(10.0°) ≈ joint(12.9°) < image_only(32.3°) ≪ ocs_only(126.2°)，与通道信息量一致。
- image_only 系统性略欠覆盖（clean/mild G5≈0.83–0.85），提示其 val→test 的 yaw error 分布有轻微偏移，已如实标注，非校准 bug。

**Mondrian（yaw-sector 分层，α∈{0.10,0.20}）：** 512 行，`fallback_pooled=0`（每 sector 的 val 样本均 ≥10，无需回退 pooled）。分层 coverage 见 `l1d3_mondrian_summary.csv`。

严格口径：conformal 是当前 simulated split 的误差覆盖区间，不是真实天文观测不确定度；coverage≈target 只说明该 split 下校准自洽，非最终概率校准完成。

---

## 9. hard-case / P-INT-hard 候选索引与下一步建议（子任务 E）

`build_l1d3_hardcase_index.py`，基于子任务 C 的 per-attitude 合并表，阈值均为该层分布分位数（可审计，非直觉手挑）。

五类计数（select=best，全 deg×geom）：

```text
ocs-hard             : 121   （neural_err>P75 且 P-DB margin<P25 或 nearest>P75）
disagreement-hard    : 748   （neural 与 P-DB hit@30 一对一错）
ambiguous-flux       : 148   （P-DB 候选 yaw 分散但都近）
image-hard(image)    : 2     （image_only/joint yaw err>30°，本级退化极少）
robust-easy          : 351   （neural 与 P-DB 都 ≤15° 且 P-DB margin>P50，对照）
```

设计建议（`l1d3_recommended_pinthard_design.md`，只建议不放行）：新增 degraded-severe 以触及图像天花板检验 joint 强互补；disagreement subset 作为 P-INT-hard 难例池；joint/full-2664 M-roll 按需补不铺全量；下一阶段门主指标 = joint 在 severe/P-INT-hard 上相对 image_only 的 yaw hit@30 增量。

---

## 10. 未完成项与阻塞项

无阻塞项。达到 R118 §10 强接收标准全部 5 条。范围内主动收敛项：

```text
- degraded 侧 image_only/joint 无 G3 run（源自 R116 矩阵未跑 G3 degraded image/joint），
  本轮如实标注缺口，未补训（红线：本轮不启动新训练）。
- P-DB clean-template 迁移探针仅做 G5 neg-L2 代表口径（R118 §4 允许 optional）；
  完整 clean-template × 全几何 × 全相似度可后续按需扩。
- confidence decile / risk-coverage 主用 neural margin 与 P-DB margin；entropy 作为备用置信已存 joined 表，未单独铺曲线。
```

均为范围内裁剪或上游矩阵限制，非代码冲突或数据缺口。

---

## 11. 红线自查

```text
[OK] 只改 项目重启_v0.4_BlenderOCS/ 内部；新输出全在 v0.4_results/13_l1d3_confidence_pdb/，报告在 02_Claude输出/105。
[OK] 未覆盖 11_l1m2 / 12_l1m3 结果目录；未改任何旧脚本、旧 metrics/test/samples 文件。
[OK] val/test 严格分开；conformal quantile 与 hard-case 阈值只用 val 或 test 自身分布，无 test 反调校准。
[OK] template 只来自 train split，val/test 未进 template 库（无检索泄漏）；zscore transform 仅 train 拟合。
[OK] 未启动头A/头B大合并裁决；未把 R113/R115/R117/R118 写成路线一 C 整体闭口。
[OK] 未写论文正文、未写成果区新结论、未生成 Codex 审阅文件、未改 CLAUDE.md。
[OK] 未启动 T3/L2 光变正式训练、三轴小项目、路线二/三/四扩展；未启动新训练/新渲染/backbone更换/开放超参搜索。
[OK] 未把 v0.4 写成真实未知目标姿态反演系统；P-DB 明确为 model-known simulated template retrieval，非真实反演成功率。
[OK] conformal 明确为当前 split 覆盖率与集合宽度，非真实 Bayesian posterior、非最终概率校准。
[OK] posterior-like/margin/entropy 全程标注为工程候选分数；P-EXT yaw-block 未写成已解决。
[OK] hard-case index 明确为后续 P-INT-hard/stronger degraded 候选输入，不是阶段门放行。
```

---

## 12. 交给 Codex 审阅的裁决问题清单

```text
Q1. P-DB(检索)在 ocs_only 证据链上强于 neural 回归（clean G5：P-DB top1 hit@30=0.949 vs neural 0.811；
    cMAE 8.19° vs 22.77°），且二者 yaw error 几乎不相关（spearman≈0）、oracle_hit@30=0.960。
    是否接收"多观测总光度向量含可检索 yaw 信息，且 P-DB 与 neural 回归构成互补证据链"为可写结论？
    P-DB 是否值得在后续升为正式 D3 分支之一（而非仅辅助探针）？

Q2. neural margin 的 risk-coverage 曲线近乎平坦（选择性预测收益弱），而 P-DB retrieval margin 略有区分度。
    是否接收"当前工程置信分数（尤其 neural margin）区分度有限，需在 P-INT-hard 上重估或引入更强置信头"
    为诚实负向结论？本轮不下"置信排序可用"的强结论是否合规？

Q3. split-conformal set_size 随几何单调收紧（G1=322° → G3=246° → G5=126°，ocs_only clean α=0.10），
    与 OCS 多观测信息量增益一致；但 image_only 系统性欠覆盖（G5≈0.83–0.85<0.90）。
    是否接收 set_size 单调性为可写结论，同时把 image_only 欠覆盖归因于 val→test 分布轻微偏移
    （非校准实现 bug），留待后续 Mondrian-by-mode 或更大 val 校准？

Q4. clean-template 退化迁移探针中，degraded query 检索 clean 模板略优于 matched-degraded
    （mild G5 hit@30 0.919 vs 0.892）。是否接收此为"clean 模板库更干净、退化观测仍可稳健检索"的
    可写观察？两种口径是否都保留供后续选择？

Q5. degraded 侧 image_only/joint 缺 G3 run（源自 R116 矩阵），本轮如实标注缺口未补训。
    是否同意本轮以现有矩阵接收，G3 degraded image/joint 留待后续（若需要）按红线另行放行？

Q6. hard-case index（disagreement-hard=748 / ocs-hard=121 / ambiguous-flux=148 / robust-easy=351）
    与 P-INT-hard 设计建议是否可作为下一阶段难例选择依据？是否需要在启动 P-INT-hard 前先补 degraded-severe？
```

---

（报告结束。所有结论均绑定 `v0.4_results/13_l1d3_confidence_pdb/` 下输出文件路径；本报告不作为论文正文，不扩大战果。P-DB 是 model-known simulated template retrieval，conformal 是当前 split 覆盖评估，置信一致性是工程分数与实际误差的一致性分析，hard-case index 是后续候选输入而非阶段门放行。）
