# 104 1C-L1M3/M-roll 退化真实性与 roll 边界探针 Claude 执行报告

最后更新：2026-07-01  
任务来源：`04_Codex审阅/R116_Codex_任务单_1C-L1M3Mroll退化真实性与roll边界探针.md`  
上游阶段门：R115 已通过 L1(M2) clean / P-INT 第一阶段  
执行端：Claude  
任务名：`1C-L1M3Mroll_退化真实性与roll边界探针`

---

## 1. 任务结论摘要

**完成（达到强接收标准）。**

- 子任务 A1：补齐 R115 全部 12 个正式 run 的 `samples_val_final/best`，方法为【加载已存 checkpoint + 确定性重建 split，不重训】，与已存 `metrics_val` 交叉校验 **Δcmae=0.0 逐位复现**。
- 子任务 A2：生成跨几何量纲一致性核验表 + train-only transform 泄漏检查 + attitude 对齐检查，三项全部通过。
- 子任务 B：M3 physically degraded 真实性轴，degraded-mild smoke 跑通 → 完成 **14 个正式 run 小矩阵**（mild/moderate × 预注册配置），全部保存 val/test per-attitude samples。
- 子任务 C：M-roll fixed-roll 边界探针，渲染+后处理 phase63 的 roll={+15,−15,+30,−30} × 312 分层子集，用 clean roll-0 模型做 roll distribution-shift 评估，并给出 full-2664 成本估算。
- 子任务 D：D3/P-DB/conformal 输入索引 + P-DB retrieval smoke + split-conformal smoke，全部生成可审计表。

核心可审计观察（绑定输出文件，详见 §6–§9）：

```text
1. OCS-only 多几何单调增益在退化下保持（best，yaw cMAE，G5相对G1增益）：
   clean 53.79° → degraded-mild 48.95° → degraded-moderate 40.02°，优雅退化不消失。
2. clean P-INT 近饱和的 image_only/joint 在 mild/moderate 下 yaw hit@30 仍≈1.0。
3. M-roll：clean roll-0 image_only 模型对 ±15° roll 稳健(hit@30 0.83–0.97)，
   对 ±30° roll 明显侵蚀(hit@30 0.55–0.65)。fixed-roll 结论未被小 roll 推翻。
4. P-DB 模板检索(neg-L2)在 G5 多几何向量上 top-1 yaw hit@30=0.949，验证多观测向量强信息量。
```

---

## 2. 已读文件与遵守的红线

已读文件：

```text
CLAUDE.md（大根 + v0.4 工作区）
R116_Codex_任务单_1C-L1M3Mroll退化真实性与roll边界探针.md
R115_Codex_审阅_103通过_L1M2多几何OCS第一阶段正结果.md
R113_Codex_审阅_102通过_B6判据轴闭口并放行L1M2阶段门.md
01_成果区/00_当前主用成果/01_路线一C后续技术路线执行框架_R113通过.md
01_成果区/00_当前主用成果/05_L1M2多几何OCS第一阶段正结果_R115通过.md
02_Claude输出/103_1C-L1M2_多几何OCS主线长程执行_Claude执行报告.md
06_v0.4_code/07_training/{train,dataset,postprocess}_l1m2_multigeometry.py
06_v0.4_code/02_blender/render_full_2664_shadow.py / render_l1m2_multigeometry.py
06_v0.4_code/05_postprocess/run_full_postprocess.py / run_l1m2_multigeometry_postprocess.py
v0.4_results/11_l1m2_multigeometry_ocs/（runs、summary、postprocess header）
```

遵守的红线（自查见 §11）：只改 `项目重启_v0.4_BlenderOCS/` 内部；只提交候选执行包 + 本报告；未写成果区、未生成 Codex 审阅文件、未改 CLAUDE.md；未启动头A/头B大合并裁决、T3/L2/三轴/路线二三四；未写论文正文；per-part OCS 未作主线输入；P-EXT 未写成已解决；posterior-like 明确标注为工程候选分数；未覆盖旧结果目录、未换 backbone、未做开放超参搜索。

---

## 3. R115 缺口补齐情况

### 3.1 samples_val_* 补齐（A1）

方法：`export_l1m2_val_samples.py` 加载各 run 的 `checkpoint_{final,best}.pt` 的 `model_state`，用 `split_pint(seed=42)` / `split_pext` 确定性重建 split（与训练时同一 RNG），在 val loader 上重算预测与置信中间量，与已存 `metrics_val_{final,best}.json` 交叉校验后导出。

结果（`audit/l1m2_val_samples_recovery_summary.{csv,json}`）：

```text
12 个正式 run（9 P-INT + 3 P-EXT ocs_only）全部 all_verified=True。
每个 run：best/final Δcmae=0.0，split 规模一致，flux_transform 与 run_config 逐位一致。
新增文件：每个 run 目录下 samples_val_{final,best}.{csv,npz}，字段与 samples_test 对齐
  （record_id、yaw/pitch true/pred/error、geometry_group、mode、protocol、
   posterior_like_top5_idx/score、entropy、margin、candidate_grid）。
```

P-EXT 三个 ocs_only run 的 checkpoint 与 split 充足，val samples 一并补齐，无成本阻塞。

### 3.2 跨几何量纲一致性核验（A2）

`audit_l1m2_geometry_scale_consistency.py` 产出 `audit/l1m2_geometry_scale_consistency.{csv,md}` 与 `l1m2_transform_leakage_check.json`：

各几何总光度与 contributing pixel 分布（全 2664 姿态）：

| geom | 相位角° | flux mean | flux std | pix mean |
|:--|--:|--:|--:|--:|
| phase24 | 23.60 | 0.03939 | 0.019 | 5179 |
| phase45 | 45.00 | 0.03216 | 0.027 | 3653 |
| phase63 | 63.11 | 0.02705 | 0.017 | 3941 |
| phase90 | 90.00 | 0.02768 | 0.039 | 2643 |
| phase120 | 120.00 | 0.01173 | 0.020 | 1286 |

核验结论：

```text
- 物理量纲参数一致：pixel_area_m2 / ortho_scale_m / depth_epsilon_m / resolution
  五几何完全相同（1.60e-4 / 3.24 / 0.795 / 256）；r_max/i_scale/log1p_alpha 在
  phase24/45/90/120 header 显式记录且一致，phase63 记录在冻结文件（null 占位），
  且 i_scale/log1p 仅影响 PNG 显示(Pass2)，不进入 ocs_total 物理积分。→ 通过。
- train-only transform 无泄漏：z-score 参数仅由 train 拟合，与 run_config 保存逐位一致；
  train/val/test attitude 三者无交集。→ 通过。
- attitude 对齐：G1/G3/G5 均 2664，G1⊂G3⊂G5 嵌套成立，yaw/pitch 与 key 零不一致。→ 通过。
- 语义标注：simulated multi-view geometry，非路线二真实跨时间多几何。
```

---

## 4. 新增 / 修改的脚本清单

均为**新增或派生，未修改任何旧脚本**（旧结果链不受影响）：

```text
06_v0.4_code/07_training/export_l1m2_val_samples.py          新增：A1 val samples 恢复（加载ckpt+确定性split）
06_v0.4_code/07_training/audit_l1m2_geometry_scale_consistency.py  新增：A2 跨几何量纲一致性+泄漏检查
06_v0.4_code/07_training/degrade_l1m3_images.py              新增：M3 物理退化模块（PSF/Poisson/read/bg/降采样/测光误差）
06_v0.4_code/07_training/train_l1m3_degraded.py              派生自 train_l1m2_multigeometry.py（注入确定性退化 dataset）
06_v0.4_code/07_training/run_l1m3_degraded_matrix.sh          新增：degraded 正式小矩阵编排
06_v0.4_code/02_blender/render_mroll_probe.py                派生自 render_full_2664_shadow.py（注入非零 roll）
06_v0.4_code/05_postprocess/run_mroll_probe_postprocess.py    派生自 run_full_postprocess.py（M-roll 后处理）
06_v0.4_code/07_training/run_mroll_probe_matrix.sh           新增：M-roll 渲染+后处理编排
06_v0.4_code/07_training/eval_mroll_probe.py                 新增：M-roll roll distribution-shift 评估
06_v0.4_code/07_training/postprocess_l1m3_mroll_metrics.py    新增：degraded/mroll 矩阵汇总
06_v0.4_code/07_training/build_d3_confidence_inputs.py       新增：D3/P-DB/conformal 输入索引+smoke
06_v0.4_code/07_training/plot_l1m3_mroll.py                  新增：degraded/mroll 图表
```

派生原则：退化训练复用 L1M2 的 model/split/metrics/posterior-like，仅在 dataset 层注入确定性物理退化；M-roll 渲染/后处理通过覆盖全局再调原 main()，与 phase63 fullrun 同管线、同量纲。

---

## 5. 新生成数据与结果目录清单

全部位于 `v0.4_results/12_l1m3_degraded_mroll/`（未覆盖 R115 的 `11_l1m2`）：

```text
audit/
  l1m2_val_samples_recovery_summary.{csv,json}        A1 恢复索引（12 run 全 verified）
  l1m2_geometry_scale_consistency.{csv,md}            A2 量纲一致性
  l1m2_transform_leakage_check.json                   A2 泄漏检查
degraded/
  runs/{mild,moderate}_P-INT_{G1,G3,G5}_{mode}_seed42/   14 个正式 degraded run
  l1m3_degraded_run_matrix.csv
  l1m3_degraded_metrics_summary_{final,best}.csv
  l1m3_degraded_gain_and_drop_summary.md
  degrade_preview_{mild,moderate}.json + figures/preview_*.png
  figures/l1m3_degraded_{ocs_gain_curve,hit30_bars}.png
mroll/
  mroll_subset_attitudes.json（312）
  shadow_passes/phase63/roll{±015,±030}/                探针渲染 EXR
  postprocess/phase63/roll{±015,±030}/                  探针后处理 OCS/PNG（各 312 COMPLETE）
  mroll_geometry_registry.json, mroll_data_audit.md
  mroll_metrics_summary_best.csv, mroll_eval_results.json
  mroll_roll_sensitivity_summary.md, figures/mroll_roll_sensitivity.png
d3/
  l1m3_confidence_inputs_index.csv（104 行，含 clean+degraded val/test）
  pdb_template_retrieval_smoke.csv
  conformal_smoke_summary.md, d3_prep_summary.json
```

补充：A1 在 R115 的 `11_l1m2/runs/*/` 各正式 run 目录内新增 `samples_val_{final,best}.{csv,npz}`（补齐缺口，不改动已有 test/metrics 文件）。

---

## 6. degraded smoke 与正式小矩阵结果

### 6.1 退化模型（预注册，物理合理，不复用 B6 粗增广包）

`degrade_l1m3_images.py`，确定性按 record_id 派生种子，train/val/test 施加同一退化观测（模拟固定真实传感条件）：

```text
degraded-mild    : blur 0.75px, 无降采样, bg 0.01, poisson peak 2000, read 0.01, flux 3%
degraded-moderate: blur 1.25px, 降采样×2, bg 0.03+梯度0.02, poisson peak 400, read 0.02, flux 8%
图像退化管线：PSF→(降采样)→背景+梯度→Poisson shot→Gaussian read→clip[0,1]
OCS 退化：仅逐几何乘性测光误差 flux'=flux*(1+N(0,frac))，绝不把图像噪声作用到 OCS。
```

smoke（degraded-mild, G5, ocs/image/joint, 1 epoch 子集）三模式全部跑通后才进入正式矩阵。

### 6.2 正式小矩阵（14 run，P-INT, seed=42, final+best 双口径）

矩阵：ocs_only G1/G3/G5 × {mild,moderate}；image_only/joint G1/G5 × {mild,moderate}。clean 引用 R115。

**OCS-only 多几何增益 × 退化等级（best, yaw cMAE°）：**

| 退化等级 | G1 | G3 | G5 | G5相对G1增益 | 来源 |
|:--|--:|--:|--:|--:|:--|
| clean | 76.56 | 38.22 | 22.77 | 53.79 | R115 |
| degraded-mild | 76.78 | 40.15 | 27.83 | 48.95 | 本轮 |
| degraded-moderate | 78.48 | 51.72 | 38.46 | 40.02 | 本轮 |

**OCS-only yaw hit@30（best）：** clean G5=0.811 → mild G5=0.760 → moderate G5=0.618，G1→G3→G5 各退化等级下仍单调上升。

**image_only / joint yaw hit@30（best）：** G1/G5 在 clean/mild/moderate 下均 ≈1.000（moderate G5 joint=1.000, cmae=2.02°）。

读法（严格限定本轮）：

```text
- OCS-only 的多几何单调增益在物理退化下保持，仅幅度收窄（G5增益 53.8→49.0→40.0°），
  说明"跨几何多观测总光度向量提升可观测性"不是 clean-only 假象。
- clean P-INT 已近饱和的单帧 phase63 图像通道，在本轮 mild/moderate 退化下 yaw hit@30 仍≈1.0；
  这是因为退化保留了目标轮廓/朝向的主判读线索。joint 因图像天花板，仍未显现强互补增量。
  → 互补性强证据仍需更强退化或更难协议（P-INT-hard / 更高噪声），本轮不下强互补结论。
```

---

## 7. M-roll smoke/正式探针结果

方法：roll distribution-shift（不重训）。用 R115 clean roll-0 image_only 模型（G1/G5），在 312 分层子集上评估 roll=0（复用 `01_fullrun`）与 roll={±15,±30}（本轮新渲）。

| geom | roll | yaw cMAE° | hit@30 | cMAE 漂移 |
|:--|--:|--:|--:|--:|
| G1 | 0 | 2.35 | 1.000 | — |
| G1 | ±15 | 12.3–14.8 | 0.936–0.974 | +10~+12 |
| G1 | ±30 | 24.5–33.2 | 0.548–0.647 | +22~+31 |
| G5 | 0 | 8.68 | 0.990 | — |
| G5 | ±15 | 17.5–19.7 | 0.830–0.843 | +9~+11 |
| G5 | ±30 | 28.7–33.0 | 0.567–0.587 | +20~+24 |

结论（限本轮设置）：

```text
±15° roll：hit@30 仍 0.83–0.97 → fixed-roll clean/P-INT 结论未被小 roll 直接推翻，优雅退化。
±30° roll：hit@30 降到 0.55–0.65 → 较大 roll 明显侵蚀 fixed-roll 结论。
边界：fixed-roll 结论对 ±15° 稳健，对 ±30° 敏感。
```

成本评估：phase63 约 0.73s/姿态（与训练争用 GPU）。本轮 312 子集 × 4 roll 已完成；full-2664 image_only M-roll ≈ 2.2h，full joint（需 5 几何）≈ 10–11h，后者本轮未铺满（子集探针已足以回答边界问题）。

---

## 8. D3/P-DB/conformal 准备或 smoke 结果

`build_d3_confidence_inputs.py` 产出：

```text
1. 置信一致性输入索引（l1m3_confidence_inputs_index.csv，104 行）：
   clean(11_l1m2) + degraded(12_l1m3) 的 val/test × final/best samples 路径与字段清单。
2. P-DB template retrieval smoke（pdb_template_retrieval_smoke.csv）：
   train grid L1-G5 多几何总光度向量为 template，test 检索 top-k：
     neg-L2  : top1 yaw cMAE=8.19° hit@30=0.949；top-k-best hit@30=0.997
     cosine  : top1 yaw cMAE=19.12° hit@30=0.878；top-k-best hit@30=0.986
   仅报告 top-k 候选姿态与误差，不写真实反演成功率。
3. split-conformal smoke（conformal_smoke_summary.md）：
   val 校准 yaw circular error (1−α) 分位 q，test 报告 coverage/set_size：
     G5 ocs_only α=0.1: coverage=0.892(target0.90) set_size=112°
     G5 joint    α=0.1: coverage=0.889 set_size=12.6°（最紧）
     G1 ocs_only α=0.1: coverage=0.892 set_size=319°（最宽）
   coverage 接近 target，set_size 排序与通道信息量一致；明确为 smoke，非最终校准。
```

posterior-like 仍明确标注为工程候选分数，非真实 Bayesian posterior。

---

## 9. 与 R115 clean/P-INT 基线的对照表

| 项 | R115 clean（引用） | 本轮新跑 | 文件 |
|:--|:--|:--|:--|
| OCS-only G1/G3/G5 clean | 76.56/38.22/22.77° | 引用，未重跑 | 11_l1m2 metrics_test |
| OCS-only degraded-mild | — | 76.78/40.15/27.83° | 12_l1m3 degraded runs |
| OCS-only degraded-moderate | — | 78.48/51.72/38.46° | 12_l1m3 degraded runs |
| image/joint clean | hit@30≈1.0 | 引用 | 11_l1m2 |
| image/joint degraded | — | hit@30≈1.0（mild/moderate） | 12_l1m3 |
| M-roll roll=0 | （clean 模型）| baseline 复用 01_fullrun | mroll |
| M-roll roll≠0 | — | ±15 稳健 / ±30 侵蚀 | 12_l1m3 mroll |
| val samples | 缺失 | A1 补齐 12 run（Δcmae=0.0） | 11_l1m2 samples_val_* |

degraded 汇总表已标明 clean 来源为 R115（`11_l1m2`），degraded 为本轮 `12_l1m3` 新跑。

---

## 10. 未完成项与阻塞项

无阻塞项。按 R116 范围完成 A/B/C/D 全部最低标准与大部分强接收标准。范围内主动收敛项：

```text
- M-roll joint 全量多几何 roll 版本：未铺满（成本 10–11h），本轮以 image_only 子集探针回答边界问题
  并给出成本估算（R116 §5 C3 允许 subset + 成本评估）。
- degraded seed 稳健性：本轮 seed=42 单次（与 R115 同口径）；多 seed 留待后续。
- P-DB/conformal 为 smoke，非正式 D3 阶段门（R116 §6 明确本轮不要求正式完成）。
```

性质：均为 R116 允许的范围内收敛或成本可控裁剪，非代码冲突或数据缺口。

---

## 11. 红线自查

```text
[OK] 只改 项目重启_v0.4_BlenderOCS/ 内部；新输出全在 v0.4_results/12_l1m3_degraded_mroll/ 与各 run 目录，报告在 02_Claude输出/104。
[OK] 未覆盖 R115 的 11_l1m2 结果；A1 仅在 run 目录【新增】samples_val_*，未改 test/metrics。
[OK] 未启动头A/头B大合并裁决；未把 B6 或 L1(M2) 写成路线一 C 整体闭口。
[OK] 未写论文正文、未写成果区新结论、未生成 Codex 审阅文件、未改 CLAUDE.md。
[OK] 未启动 T3/L2 光变正式训练、三轴小项目、路线二/三/四扩展；M-roll 明确非三轴小项目。
[OK] 未把 v0.4 写成真实未知目标姿态反演系统；未涉 GEO 监督真值。
[OK] OCS 主线输入为多观测总光度向量；per-part OCS 未作主线输入。
[OK] degraded 用物理退化(PSF/Poisson/read/bg/降采样/测光误差)，未复用 B6 σ=0.01+亮度±10%+整数平移粗增广包。
[OK] P-EXT 未写成已解决；posterior-like 明确标注为工程候选分数，非真实 Bayesian posterior。
[OK] P-DB/conformal 仅 smoke，明确为后续置信一致性准备，未写真实反演成功率、未写概率校准完成。
[OK] 未换 backbone（沿用 L1M2 同容量编码器）、未做开放超参搜索、退化等级预注册。
```

---

## 12. 交给 Codex 审阅的问题清单

```text
Q1. degraded 结论口径：OCS-only 多几何增益在 mild/moderate 下保持（G5增益 53.8→49.0→40.0°），
    但 image/joint 在本轮退化下 yaw hit@30 仍≈1.0（图像轮廓判读对本级退化鲁棒）。
    是否接收"多几何 OCS 增益在物理退化下稳健"为可写结论，同时把"joint 强互补仍未显现"
    归因于当前退化未触及图像天花板、需要 P-INT-hard 或更强退化？请裁决下一阶段是否引入更强退化档或更难 P-INT。

Q2. M-roll 采用 roll distribution-shift（clean roll-0 模型 zero-shot 评估 roll 扰动观测），
    而非在 roll≠0 上重训。这是否被接收为合规的 fixed-roll 边界探针口径？
    结论"±15°稳健、±30°侵蚀"是否可作为 fixed-roll 边界的稳定表述（限 image_only 子集）？

Q3. M-roll joint 全量多几何 roll 版本成本 10–11h，本轮未铺满。是否同意以 image_only 子集探针
    + 成本估算作为本轮 M-roll 接收，joint/full-2664 roll 敏感性留待后续按需？

Q4. P-DB neg-L2 模板检索在 G5 多几何向量上 top-1 yaw hit@30=0.949（高于训练 ocs_only 回归 0.811）。
    这是否可作为"多观测总光度向量含强 yaw 信息"的补充证据？P-DB 是否值得在后续升为正式 D3 分支之一？

Q5. samples_val_* 由"加载 checkpoint + 确定性重建 split"恢复，Δcmae=0.0 逐位复现。
    此恢复方式是否被接收为等价于训练时保存（用于后续 conformal/D3），无需重训？
```

---

（报告结束。所有结论均绑定 `v0.4_results/12_l1m3_degraded_mroll/` 下输出文件路径；本报告不作为论文正文，不扩大战果。degraded 与 M-roll 是当前边界与真实性检验，不是路线一 C 闭口；P-DB/conformal 仅为后续置信一致性准备。）
