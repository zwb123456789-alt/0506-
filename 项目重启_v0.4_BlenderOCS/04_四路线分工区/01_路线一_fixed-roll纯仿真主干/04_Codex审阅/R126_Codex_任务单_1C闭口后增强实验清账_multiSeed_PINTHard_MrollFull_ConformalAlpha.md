# R126 Codex 任务单：路线一 C 闭口后增强实验清账

最后更新：2026-07-01  
任务类型：给执行端 Claude 的长程增强实验提示词  
上游阶段门：R125 已裁定路线一 C 实验主干闭口  
作者偏好：为防止后期补实验遗忘，先完成剩余增强实验并经 Codex 验收，再进入三轴小项目

执行端报告必须写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/109_1C闭口后增强实验清账_multiSeed_PINTHard_MrollFull_ConformalAlpha_Claude执行报告.md
```

所有新结果写入：

```text
v0.4_results/17_route1c_postclosure_enhancement_sweep/
```

本文件是 Codex 调度/提示词文件，保留在 `04_Codex审阅/`。执行端不得把报告、结果或裁决文件写入 `04_Codex审阅/`。

---

## 0. 给 Claude 的总提示词

你现在执行路线一 C 的闭口后增强实验清账任务：

```text
1C_postclosure_enhancement_sweep
```

R125 已经裁定路线一 C 实验主干在当前 model-known simulated / fixed-roll / L1 多几何范围内闭口。本轮不是推翻 R125，也不是启动三轴小项目，而是按作者偏好，把 R125 中列为 ENHANCEMENT 的剩余实验集中做完，形成可验收的 17 号增强证据包。

本轮目标：

```text
A. multi-seed sanity：确认 L1-G1/G3/G5 OCS-only 多几何主结论对训练随机种子不敏感。
B. P-INT-hard / degraded-severe：在更难但物理合理的退化条件下复查 image 天花板与 joint 互补性。
C. M-roll full-2664：把 R117 的 roll 分布漂移探针从 312 分层子集扩展到 full-2664 姿态。
D. conformal alpha sensitivity：补齐 alpha=0.05/0.10/0.20 的轻量敏感性表与图。
E. 统一生成增强项验收矩阵：把哪些结论增强、哪些仍为负向观察、哪些仍需未来方向分清楚。
```

完成后只提交 17 号包和 109 执行报告。作者会把 109 交给 Codex 做 R127 审阅。R127 通过前，不得启动三轴小项目。

---

## 1. 本轮允许与禁止

允许：

```text
1. 新训练：仅限本任务明确列出的 multi-seed sanity 与 degraded-severe / P-INT-hard 小矩阵。
2. 新渲染：仅限 M-roll full-2664 所需的 phase63 roll={-30,-15,+15,+30} 姿态补齐。
3. 新增派生脚本、配置、wrapper、汇总与制图脚本。
4. 读取并复用 10-16 号结果和既有训练/渲染入口。
5. 生成新的 CSV/JSON/NPZ/PNG/PDF/MD/log/audit 文件。
```

禁止：

```text
1. 不改旧脚本、旧 metrics、旧 samples、旧结果目录 10-16。
2. 不改 split 定义，不改姿态网格，不改 OBS_GEOMETRIES 语义，不做开放超参搜索。
3. 不换 backbone，不引入未预注册的大模型结构。
4. 不把 P-INT-hard / degraded-severe 写成真实观测验证。
5. 不把 M-roll full-2664 写成三轴小项目已经完成。
6. 不把 P-DB/conformal 写成真实概率或 Bayesian posterior。
7. 不写成果区，不生成 Codex 审阅文件，不改 CLAUDE.md。
8. 不写最终论文正文、投稿摘要或投稿稿。
9. 不启动三轴小项目、T3/L2、路线二/三/四扩展。
```

若上下文、输出长度或文件写入受限，必须按 `Part 1/2/3...` 分段输出或分段写入，直到报告和交付清单完整。

---

## 2. 必读文件

按顺序读取，并在执行报告中列出已读文件清单：

```text
CLAUDE.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/01_路线一C后续技术路线执行框架_R113通过.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R117_Codex_审阅_104通过_L1M3退化真实性与Mroll边界探针.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R119_Codex_审阅_105通过_L1D3置信一致性与PDB正式评估.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R123_Codex_审阅_107通过_1C-ResultsSI图表与写作准备包.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R125_Codex_审阅_108通过_路线一C实验主干闭口并放行三轴小项目准备.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/10_路线一C实验主干闭口_D2D4M5_R125通过.md
```

按需读取：

```text
v0.4_results/11_l1m2_multigeometry_ocs/
v0.4_results/12_l1m3_degraded_mroll/
v0.4_results/13_l1d3_confidence_pdb/
v0.4_results/16_route1c_closure_d2d4_m5/
06_v0.4_code/
```

---

## 3. 总体交付结构

建议结构：

```text
v0.4_results/17_route1c_postclosure_enhancement_sweep/
  multiseed/
  pint_hard_degraded_severe/
  mroll_full2664/
  conformal_alpha/
  synthesis/
  figures/
  tables/
  scripts/
  logs/
  audit/
```

执行报告写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/109_1C闭口后增强实验清账_multiSeed_PINTHard_MrollFull_ConformalAlpha_Claude执行报告.md
```

---

## 4. 子任务 A：运行前审计与复现实验入口定位

先做只读审计，确认可以复用哪些训练、退化、渲染、conformal 入口。

必须输出：

```text
audit/preflight_input_manifest.csv
audit/code_entrypoint_audit.csv
audit/planned_run_matrix.csv
audit/preflight_redline_check.csv
```

必须说明：

```text
1. multi-seed 训练入口、split 固定方式、seed 控制点。
2. degraded-severe 的 transform 函数与参数写入位置。
3. M-roll full-2664 缺哪些 roll/姿态/后处理文件，是否需要新渲染。
4. conformal alpha 是否可直接由 13/15 号现有预测重算。
5. 预计新增 run 数、渲染数、训练数、主要耗时风险。
```

若发现旧入口不足以安全复用，只能新增派生脚本或 wrapper；不得修改旧脚本。

---

## 5. 子任务 B：multi-seed sanity

目标：补路线一 C 主结论的最小训练随机性稳健性，不改变 split 与姿态网格。

预注册口径：

```text
协议：P-INT clean
通道：ocs_only
几何：L1-G1, L1-G3, L1-G5
split：沿用 R115/R125 的确定性 split，split seed 固定为 42
训练随机种子：在 seed=42 之外新增 seed={7,123}
运行数：3 几何 × 2 新训练种子 = 6 个新 run
```

若代码中训练 seed 与 split seed 不可分离，必须在报告中明确；优先通过 wrapper 固定 split 并只改变模型初始化/数据加载随机性。

输出：

```text
multiseed/runs/...                  # 每个新 run 的 metrics、samples、checkpoint 索引或日志
tables/multiseed_ocs_metrics.csv
tables/multiseed_monotonicity_check.csv
figures/multiseed_ocs_gain_curve.png/.pdf
text/multiseed_sanity_summary.md
```

接收判断：

```text
1. 主看 yaw cMAE 与 hit@30 的 G1->G3->G5 趋势。
2. 若新增 seeds 均保持 G5 优于 G3 优于 G1，写“multi-seed sanity 支持主结论”。
3. 若存在轻微非单调但 G5 仍显著优于 G1，写“主结论基本稳健但几何阶梯局部波动”。
4. 若新增 seeds 推翻 G1->G5 增益，必须标为严重风险，交 R127 裁决。
```

---

## 6. 子任务 C：P-INT-hard / degraded-severe 小矩阵

目标：在 clean/P-INT image 天花板之外，复查 joint 是否存在可见增量；若仍无增量，也要形成诚实负结论。

本轮不做开放式 P-INT-hard 设计。采用两层口径：

```text
C1. hard-attitude subset：直接使用 R125 D4/hardcase 表，把 evaluation 分为 easy / ambiguous-flux / overconfident-error / OCS-hard / image-hard / disagreement-hard 子集，先用既有 clean/degraded 预测做分区重算。
C2. degraded-severe：新增一档物理合理 severe 退化，并训练/evaluate image_only / ocs_only / joint。
```

degraded-severe 预注册参数必须物理合理，可在 smoke 后微调但必须写清楚。默认建议：

```text
PSF Gaussian sigma: 2.0 px
shot/read noise: SNR about 5-10 dB
background: stronger uniform sky + linear gradient
downsample: x4 then resize back if旧模型输入尺寸固定
photometric calibration error: 10-15%
record_id 派生 deterministic transform seed，保证通道/几何可对齐
```

不得复用 B6 粗增广包作为正式真实性模型。

预注册运行矩阵：

```text
协议：P-INT
退化：degraded-severe
通道：image_only, ocs_only, joint
几何：L1-G1, L1-G3, L1-G5
seed：42
运行数：9 个正式 run
```

若时间极端超限，允许先完成 G5 三通道 + G1/G3 ocs_only 的保底矩阵，但必须在报告中标明未达到强接收；默认目标仍是 9 run 全矩阵。

输出：

```text
pint_hard_degraded_severe/runs/...
tables/pint_hard_subset_metrics.csv
tables/degraded_severe_metrics.csv
tables/degraded_severe_joint_increment.csv
tables/degraded_severe_disagreement_oracle.csv
figures/degraded_severe_channel_comparison.png/.pdf
figures/pint_hard_subset_error_panel.png/.pdf
text/pint_hard_degraded_severe_summary.md
```

判断口径：

```text
1. 若 severe 下 image_only 不再饱和且 joint 稳定优于最佳单通道，可写“joint 增量在 severe hard condition 下可见”。
2. 若 severe 下 joint 仍无稳定增量，只能写“joint 强互补性仍未被支持”。
3. 无论结果如何，不得写真实观测反演成功。
```

---

## 7. 子任务 D：M-roll full-2664

目标：把 R117 的 M-roll 边界探针从 312 分层子集扩展为 full-2664 姿态，形成 fixed-roll 边界的完整增强证据。

预注册对象：

```text
几何：phase63 / L1-G1 代表几何
roll：{-30, -15, +15, +30}，roll=0 复用基准
姿态：每个 roll 全 2664 yaw×pitch 姿态
优先评估：用 R115/R125 clean roll=0 模型做 distribution-shift evaluation
通道：image_only, ocs_only, joint
```

执行顺序：

```text
1. 先做每个 roll 12-24 姿态 smoke 渲染/后处理/推理，检查路径、亮度、图像尺寸、OCS 字段、record_id。
2. smoke 通过后，补齐 full-2664 渲染与后处理。
3. 用既有 roll=0 clean 模型评估 roll±15/±30 distribution shift。
4. 若发现 ocs_only 对 roll 定义不敏感或字段不适用，仍需如实输出并解释物理原因。
```

不要求本轮训练 roll-aware 新模型；若 Claude 判断必须训练才能回答某个问题，只能列为后续建议，不能自行扩展。

输出：

```text
mroll_full2664/render_manifest.csv
mroll_full2664/postprocess_manifest.csv
mroll_full2664/predictions_*.csv/.npz
tables/mroll_full2664_metrics.csv
tables/mroll_full2664_delta_vs_roll0.csv
tables/mroll_full2664_failure_regions.csv
figures/mroll_full2664_hit_cmae_by_roll.png/.pdf
figures/mroll_full2664_error_maps.png/.pdf
text/mroll_full2664_summary.md
```

判断口径：

```text
1. ±15° 若保持较高 hit@30，可写 fixed-roll 结论对小 roll 扰动较稳健。
2. ±30° 若明显下降，可写 fixed-roll 边界对大 roll 敏感。
3. 不得写三轴小项目完成；这里只是路线一 C 的 roll sensitivity 增强探针。
```

---

## 8. 子任务 E：conformal alpha sensitivity

目标：补齐 R119/R123 中提到的 alpha 敏感性 SI，原则上不新训练。

alpha：

```text
alpha ∈ {0.05, 0.10, 0.20}
```

对象：

```text
ocs_only / image_only / joint
L1-G1/G3/G5
clean P-INT best 口径
若 degraded mild/moderate 现有预测可直接复算，也可加入；否则只做 clean 并说明。
```

输出：

```text
conformal_alpha/conformal_alpha_metrics.csv
tables/conformal_alpha_coverage_setsize.csv
figures/conformal_alpha_coverage_setsize.png/.pdf
text/conformal_alpha_sensitivity_summary.md
```

判断口径：

```text
只写 split-conformal 工程覆盖与 set size，不写 Bayesian posterior，不写最终概率校准。
```

---

## 9. 子任务 F：增强项总验收矩阵

把四类增强实验统一收口，供 Codex R127 审阅。

输出：

```text
tables/postclosure_enhancement_gate_matrix.csv
tables/allowed_forbidden_after_enhancement.csv
text/postclosure_enhancement_synthesis.md
text/codex_review_checklist_for_109.md
audit/numeric_consistency_check.csv
audit/generated_files_manifest.csv
audit/redline_self_check.csv
```

总验收矩阵至少包含：

```text
multi-seed sanity: 通过/风险/阻塞
P-INT-hard subset: 通过/风险/阻塞
degraded-severe: 通过/风险/阻塞
joint complementarity: 支持/不支持/仍待裁决
M-roll full-2664: 小 roll 稳健/大 roll 敏感/异常
conformal alpha: coverage 与 set_size 走势
对路线一 C 论文 claim 的影响
对三轴小项目启动的影响
```

---

## 10. 执行报告结构

报告必须包含：

```text
1. 任务结论摘要：完成 / 部分完成 / 阻塞。
2. 已读文件与遵守红线。
3. 新增脚本、配置、训练、渲染、结果目录清单。
4. preflight 审计摘要。
5. multi-seed sanity 结果。
6. P-INT-hard / degraded-severe 结果。
7. M-roll full-2664 结果。
8. conformal alpha sensitivity 结果。
9. 增强项总验收矩阵摘要。
10. 数字一致性、manifest 与红线自检。
11. 对 R125 结论的影响：增强/不变/提出风险。
12. 交给 Codex R127 的裁决问题清单。
```

---

## 11. 成功判据

最低接收标准：

```text
1. 17 号包目录存在，结构清楚。
2. preflight audit 完成。
3. multi-seed 至少完成 ocs_only G1/G3/G5 的 2 个新增 seed，或明确阻塞原因。
4. degraded-severe 至少完成 G5 三通道 + G1/G3 ocs_only，或明确阻塞原因。
5. M-roll full-2664 至少完成 smoke + 已存在/新增数据 manifest；若 full render 未完成，必须给出具体阻塞。
6. conformal alpha clean 口径完成。
7. generated manifest、numeric check、redline self-check 完成。
8. 报告写入正确路径，未写成果区、未生成 Codex 审阅文件、未改 CLAUDE.md。
```

强接收标准：

```text
1. multi-seed 6 个新 run 全完成，并给出单调性统计。
2. degraded-severe 9 个正式 run 全完成，并给出 joint 增量裁决所需表。
3. M-roll roll={-30,-15,+15,+30} full-2664 全完成，并形成 roll error maps。
4. conformal alpha 三档完成，并可直接进入 SI。
5. 增强项总验收矩阵能让 Codex R127 直接裁决“是否所有路线一 C 剩余增强项清账完毕，是否可进入三轴小项目”。
```

---

## 12. 最后交付提醒

执行完成后，只提交 17 号包与 109 执行报告。不要自行把结果升级到成果区，不要生成 Codex 审阅文件，不要修改 `CLAUDE.md`，不要启动三轴小项目。

R127 将裁决：

```text
1. multi-seed 是否支持主结论；
2. P-INT-hard / degraded-severe 是否支持 joint 互补性，或确认其仍不成立；
3. M-roll full-2664 是否完成 fixed-roll 边界增强；
4. conformal alpha sensitivity 是否可接收为 SI 增强；
5. R125 闭口结论是否需修正；
6. 是否可以正式进入三轴小项目阶段。
```

