# 109 路线一 C 闭口后增强实验清账执行报告

任务单：`04_Codex审阅/R126_Codex_任务单_1C闭口后增强实验清账_multiSeed_PINTHard_MrollFull_ConformalAlpha.md`
最后更新：2026-07-01
结果包：`v0.4_results/17_route1c_postclosure_enhancement_sweep/`

---

## 1. 任务结论摘要

**完成（强接收）。** R126 列出的四类闭口后增强实验全部执行完毕并形成可审计的 17 号证据包：

- A. multi-seed sanity：6 个新 run 全完成，3/3 seed 保持完整几何单调增益。
- C. P-INT-hard subset + degraded-severe：C1 六子集分区重算完成；C2 degraded-severe **9/9 run 全完成**。
- D. M-roll full-2664：4 个 roll × 2664 姿态**全渲染 + 全后处理 + distribution-shift 评估完成**。
- E. conformal alpha：α=0.05/0.10/0.20 三档敏感性表/图完成。
- F. 增强项总验收矩阵、数字一致性（11/11 PASS）、manifest、红线自检（12/12 PASS）完成。

四类增强项均不推翻 R125 闭口结论；主结论获增强，边界维持不变。本轮未启动三轴小项目，交 R127 裁决。

---

## 2. 已读文件与遵守红线

已读必读文件：

```text
CLAUDE.md（大根目录 + 项目重启_v0.4_BlenderOCS/CLAUDE.md）
01_成果区/00_当前主用成果/01_路线一C后续技术路线执行框架_R113通过.md
04_Codex审阅/R117_Codex_审阅_104通过_L1M3退化真实性与Mroll边界探针.md
04_Codex审阅/R119_Codex_审阅_105通过_L1D3置信一致性与PDB正式评估.md
04_Codex审阅/R123_Codex_审阅_107通过_1C-ResultsSI图表与写作准备包.md
04_Codex审阅/R125_Codex_审阅_108通过_路线一C实验主干闭口并放行三轴小项目准备.md
01_成果区/00_当前主用成果/10_路线一C实验主干闭口_D2D4M5_R125通过.md
```

按需读取的代码与结果入口：

```text
06_v0.4_code/07_training/{train_l1m2_multigeometry,train_l1m3_degraded,degrade_l1m3_images,
  eval_l1d3_conformal,eval_mroll_probe,l1d3_common,dataset_l1m2_multigeometry}.py
06_v0.4_code/02_blender/{render_mroll_probe,render_full_2664_shadow}.py
06_v0.4_code/05_postprocess/run_mroll_probe_postprocess.py
v0.4_results/{01_fullrun,11_l1m2_multigeometry_ocs,12_l1m3_degraded_mroll,13_l1d3_confidence_pdb,16_route1c_closure_d2d4_m5}
```

红线遵守：见 `audit/redline_self_check.csv`（12/12 PASS）。要点——只读 10-16 号旧结果与旧脚本、不改旧脚本/split/网格/backbone；新增派生 wrapper 与汇总脚本；报告写入本路线 `02_Claude输出/`，未写成果区、未生成 Codex 审阅文件、未改 CLAUDE.md、未启动三轴小项目。

---

## 3. 新增脚本、训练、渲染、结果目录清单

新增派生脚本（`06_v0.4_code/07_training/`，同时复制到 17 号包 `scripts/`）：

```text
postclosure_preflight_audit.py            子任务A 只读审计
postclosure_multiseed_train.py            子任务B wrapper（split seed 固定42，仅变 model seed）
postclosure_multiseed_synthesis.py        子任务B 汇总
postclosure_pint_hard_subset.py           子任务C1 hard 子集分区重算
postclosure_degraded_severe_train.py      子任务C2 wrapper（注入 degraded-severe 档）
postclosure_degraded_severe_synthesis.py  子任务C2 汇总
run_mroll_full2664_matrix.sh              子任务D 渲染+后处理编排
postclosure_mroll_full2664_eval.py        子任务D full-2664 评估
postclosure_conformal_alpha.py            子任务E α 敏感性复算
postclosure_synthesis.py                  子任务F 总验收 + 审计收口
```

新增训练：15 个 run（B: 6 个 multi-seed ocs_only；C2: 9 个 degraded-severe），均 P-INT / seed 或 model-seed 明确、max-epochs=30、未改超参。

新增渲染：M-roll full-2664，phase63 × roll∈{-30,-15,+15,+30}，各补齐至 2664 姿态（渲染产物写入既有探针目录 `12_l1m3_degraded_mroll/mroll/`，未覆盖 312 子集，skip_existing 增量渲染）。

结果目录结构（`v0.4_results/17_route1c_postclosure_enhancement_sweep/`）：

```text
audit/         preflight 4 文件 + numeric_consistency + generated_files_manifest + redline_self_check
multiseed/runs/    6 个新 run
pint_hard_degraded_severe/runs/  9 个 degraded-severe run
mroll_full2664/    predictions_*.csv + render/postprocess manifest + 姿态列表
conformal_alpha/   conformal_alpha_metrics.csv
tables/  figures/  text/  scripts/  logs/
```

---

## 4. preflight 审计摘要

`audit/` 四文件完成。input_manifest 45 行，41 OK；4 项 MISSING 为 R119 Q5 已知的 degraded G3 image/joint 缺口（非本轮必需）。

关键入口结论：

```text
1. multi-seed：train_l1m2_multigeometry 的 split_pint(seed=args.seed) 使 split 与训练 seed 共用 --seed，
   不可分离。已用 wrapper 固定 split seed=42（与 R115/R125 同一 train/val/test），仅将模型初始化/训练随机性
   设为 model_seed∈{7,123}，保证 test 集合与 seed42 基线一致、可直接比较。
2. degraded-severe：wrapper 运行时向 DEGRADE_LEVELS 注入 severe 档（不改旧脚本 degrade_l1m3_images.py），
   复用 train_l1m3_degraded.main() 的确定性退化（record_id 派生种子）与训练/评估逻辑。
3. M-roll full-2664：现有仅 312 分层子集渲染；需对每 roll 补 ~2352 新姿态，共约 9408 帧。
   渲染 CYCLES/OptiX/256px/1 sample，实测约 1.8 帧/秒；已用 render_mroll_probe.py 全网格 + skip_existing 补齐。
4. conformal alpha：eval_l1d3_conformal.py 输出的 l1d3_conformal_summary.csv 已含 α=0.05/0.10/0.20 三档，
   可直接复算重组，无需新训练。
5. 预计新增：train 15 run、render ~9408 帧、recompute 1；主要耗时风险为 M-roll full 渲染（已后台完成）。
```

---

## 5. multi-seed sanity 结果（子任务 B）

口径：P-INT clean, ocs_only, L1-G1/G3/G5；split seed 固定=42，model seed∈{42(基线),7,123}；6 个新 run。

best-val 几何阶梯（`tables/multiseed_monotonicity_check.csv`）：

| seed | cMAE G1/G3/G5 | hit@30 G1/G3/G5 | 单调cMAE | 单调hit | G5优于G1 |
|:--|:--|:--|:--|:--|:--|
| 42(基线) | 76.56/38.22/22.77 | 0.277/0.672/0.811 | ✓ | ✓ | ✓ |
| 7 | 80.76/39.88/19.01 | 0.294/0.639/0.834 | ✓ | ✓ | ✓ |
| 123 | 76.76/38.20/20.10 | 0.274/0.659/0.834 | ✓ | ✓ | ✓ |

**接收判断：multi-seed sanity 支持主结论。** 3/3 seed 均满足完整单调 G1>G3>G5（cMAE）且 hit@30 单增；seed42 基线复现 R125（G5 cMAE 22.77、hit@30 0.811）。OCS 多几何单调增益对训练随机种子不敏感。

---

## 6. P-INT-hard / degraded-severe 结果（子任务 C）

### C1 hard-attitude subset（clean P-INT，best-val 复算自 R119/R125 hardcase index）

各子集 joint 相对最佳单通道 hit@30（`tables/pint_hard_subset_metrics.csv`）：clean 下 image_only 在 ambiguous-flux / ocs-hard / disagreement-hard 子集仍近饱和（hit@30≈1.0），joint 继承之，Δ≈0；仅 image-hard（n=1）显示 joint 救回 image。与 R125 D2「clean image 天花板下 joint 无稳定正增量」一致。

### C2 degraded-severe（P-INT，best-val，seed42，9/9 run）

severe 预注册参数：blur σ=2.0px、downsample ×4、bg 0.05+grad 0.04、Poisson peak 150、read 0.03、flux err 12%（物理合理，比 moderate 更强，非 B6 粗增广）。

| geom | ocs_only cMAE/hit30 | image_only cMAE/hit30 | joint cMAE/hit30 | joint 增量 Δhit30 |
|:--|:--|:--|:--|:--|
| G1 | 79.87/0.179 | 4.27/0.997 | 2.28/1.000 | +0.0034 |
| G3 | 57.87/0.473 | 3.66/1.000 | 2.04/1.000 | +0.0000 |
| G5 | 51.88/0.507 | 3.88/0.997 | 2.22/1.000 | +0.0034 |

**裁决：joint 强互补性仍未被支持。** 即便在 severe 强退化下，image_only 仍近饱和（hit@30≈0.997-1.0），joint 增量≤+0.0034，disagreement oracle 也显示单通道 oracle 已达 hit@30=1.0，三通道 oracle 无额外增益。附带正向观察：severe 下 ocs_only 仍保持 G1→G3→G5 单调增益（79.87→57.87→51.88），与主结论一致。**不写真实观测反演成功。**

---

## 7. M-roll full-2664 结果（子任务 D）

phase63 × roll∈{-30,-15,+15,+30} 各 2664 姿态**全渲染 + 全后处理**（render/postprocess manifest 均 2664/2664）。用 clean roll=0 模型做 distribution-shift 评估。

通道覆盖（受渲染范围约束，如实说明）：M-roll 只渲代表几何 phase63（R117/R126 §7 预注册），故 image_only 可评估 G1/G3/G5（图像固定用 phase63），ocs_only/joint 仅 G1（phase63 标量）；G3/G5 多几何 OCS 的 roll 版未渲染，不适用。

yaw hit@30（`tables/mroll_full2664_metrics.csv`）：

| 通道 | roll=0 | ±15° | ±30° |
|:--|:--|:--|:--|
| G1 image_only | 1.000 | +15:0.934 / −15:0.975 | +30:0.554 / −30:0.667 |
| G3 image_only | 0.999 | +15:0.854 / −15:0.945 | +30:0.526 / −30:0.648 |
| G5 image_only | 0.991 | +15:0.841 / −15:0.830 | +30:0.605 / −30:0.587 |
| G1 joint | 1.000 | +15:0.891 / −15:0.947 | +30:0.561 / −30:0.597 |
| G1 ocs_only | 0.292 | +15:0.241 / −15:0.246 | +30:0.169 / −30:0.250 |

**判断：fixed-roll 结论对 ±15° roll 扰动较稳健（hit@30 保持 0.83-0.97），对 ±30° roll 明显敏感（降至 0.53-0.67）。** 全 2664 结果确认并扩展 R117 的 312 子集探针。**不写三轴小项目完成**；这是路线一 C 的 roll sensitivity 增强探针。error maps 见 `figures/mroll_full2664_error_maps.png`。

---

## 8. conformal alpha sensitivity 结果（子任务 E）

α∈{0.05,0.10,0.20}，clean P-INT best，直接复用 13 号 conformal_summary（不新训练）。

G5 ocs_only/image_only/joint 的 set_size(°)（`tables/conformal_alpha_coverage_setsize.csv`）：

```text
ocs_only  : α0.05=207.6 / α0.10=126.2 / α0.20=56.2
image_only: α0.05=47.7  / α0.10=32.3  / α0.20=24.8
joint     : α0.05=14.5  / α0.10=12.9  / α0.20=10.3
```

走势：set_size 随 α 增大单调收窄，随几何 G1→G5 收紧；neural ocs_only 在 α=0.10 附近 coverage 接近 target，image_only clean 系统性略欠覆盖（与 R119/R123 一致，保留）。**只写 split-conformal 工程覆盖与 set size，不写 Bayesian posterior / 最终概率校准。**

---

## 9. 增强项总验收矩阵摘要（子任务 F）

`tables/postclosure_enhancement_gate_matrix.csv`：

```text
multi-seed sanity     : 通过（3/3 seed 完整单调）
P-INT-hard subset     : 通过（image 天花板普遍，joint≈image）
degraded-severe       : 通过（9/9 run）
joint complementarity : 不支持（clean 与 severe 下 image 近饱和，增量≤+0.0034）
M-roll full-2664      : 小 roll 稳健 / 大 roll 敏感
conformal alpha       : 通过（SI 增强）
对论文 claim 影响      : 增强不变（不修正 R125）
对三轴小项目影响       : 四类增强清账完毕，交 R127 裁决
```

---

## 10. 数字一致性、manifest 与红线自检

```text
audit/numeric_consistency_check.csv : 11/11 PASS（含 seed42 复现 R125、severe image 近饱和、
                                      joint 增量≤0.01、mroll ±15稳健/+30敏感、conformal 单调）
audit/generated_files_manifest.csv  : 260 个 17 号包文件，全部 exists=OK
audit/redline_self_check.csv        : 12/12 PASS
figures : 6 张 PNG 全部有效、可打开、非空（另有 6 份 PDF）
```

---

## 11. 对 R125 结论的影响

**增强/不变，未提出风险。**

```text
增强：OCS 多几何 G1->G3->G5 单调增益获 multi-seed(42/7/123) 稳健性支持；
      fixed-roll 边界获 full-2664 roll 敏感性完整刻画（±15稳健/±30敏感）；
      severe 退化下 OCS 单调增益仍保持。
不变：joint 天花板/强互补性未证明、P-EXT yaw-block 坍缩、image_only conformal 欠覆盖、
      neural margin 区分度弱等边界全部维持。
结论：无需修正 R125 闭口裁决；四类增强项均非闭口 blocker，现已清账完毕。
```

---

## 12. 交给 Codex R127 的裁决问题清单

见 `text/codex_review_checklist_for_109.md`：

```text
Q1 multi-seed 是否支持主结论？（建议：支持）
Q2 P-INT-hard/degraded-severe 是否支持 joint 互补性？（建议：不支持，维持负向观察）
Q3 M-roll full-2664 是否完成 fixed-roll 边界增强？（建议：完成，±15稳健/±30敏感）
Q4 conformal alpha 是否可接收为 SI 增强？（建议：可接收）
Q5 R125 闭口结论是否需修正？（建议：增强不变，无需修正）
Q6 是否可正式进入三轴小项目阶段？（交 R127 裁决）
```

R127 通过前，不启动三轴小项目。
