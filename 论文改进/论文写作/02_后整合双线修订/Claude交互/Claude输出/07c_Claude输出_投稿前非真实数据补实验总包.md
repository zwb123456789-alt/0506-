# 07c Claude 输出：投稿前非真实数据补实验总包（实验 12c-12g）

> 执行端：Claude  
> 完成日期：2026-06-05  
> 任务来源：`Claude交互/07c_真实观测风格退化与期刊分流补强_Claude指导.md`、`07c_投稿前非真实数据补实验总包_立项清单.md`  
> 状态：实验 12c-12g 全部完成（5 seeds，10°→5° split）。**未生成 v0.2、未改 v0.1、未推进三档投稿写作。本文件为执行端原始输出，待 Codex 审阅后再决定 v0.2 吸收方式。**

---

## 0. 一句话结论

退化感知 U1 fusion 在训练未见的 observation-style 退化下保持 ~2°，clean-trained image-only 崩到 60-88°，OCS-only 平 6.58°；显式 late-fusion 在噪声下回到 OCS 端（6.58° vs naive 73°）；图像模型跨 phase 明显退化（phase120 +81°）；clean-image 性能部分依赖固定框定（居中 1.69→2.88°）；rare large outliers <0.1% 集中极区。**两个诚实负结果：obs-aug 反而更差；跨 phase120 与 combined_severe 无方法全鲁棒。**

---

## 1. 关键文件路径（供 Codex 审阅）

### 1.1 新增脚本（`论文改进/补充实验/代码/`）

| 实验 | 脚本 |
|---|---|
| 12c | `run_observation_style_degradation_12c.py` |
| 12d | `run_cross_phase_generalization_12d.py` |
| 12e | `run_centered_control_12e.py` |
| 12f | `run_late_fusion_beta_sweep_12f.py` |
| 12g | `build_outlier_gallery_12g.py` |

### 1.2 结果目录与 summary.md（`论文改进/补充实验/结果/`）

| 实验 | 结果目录 | summary 文件 |
|---|---|---|
| 12c | `observation_style_degradation_12c/run_20260604_222508/` | `…/summary.md` |
| 12d | `cross_phase_generalization_12d/run_20260604_234811/` | `…/summary.md` |
| 12e | `centered_control_12e/run_20260604_213911/` | `…/summary.md` |
| 12f | `late_fusion_beta_sweep_12f/run_20260604_220802/` | `…/summary.md` |
| 12g | `outlier_gallery_12g/run_20260604_213526/` | `…/gallery_12g_summary.md`（注意：12g 命名不同） |

各 summary.md 完整相对路径：

```text
论文改进/补充实验/结果/observation_style_degradation_12c/run_20260604_222508/summary.md
论文改进/补充实验/结果/cross_phase_generalization_12d/run_20260604_234811/summary.md
论文改进/补充实验/结果/centered_control_12e/run_20260604_213911/summary.md
论文改进/补充实验/结果/late_fusion_beta_sweep_12f/run_20260604_220802/summary.md
论文改进/补充实验/结果/outlier_gallery_12g/run_20260604_213526/gallery_12g_summary.md
```

### 1.3 12d 渲染前置与产物

- scan_json（复用 phase63 的 2701 姿态，仅改 sun/det）：`结果/模块B_渲染/_scan_json_12d/ocs_scan_phase24.json`、`ocs_scan_phase120.json`
- 渲染产物（各 2701 张 brdf_images，res=256，GGX 后处理，与 phase63 训练图像 `run_20260528_101944_exact_brdf` 同管线）：
  - `结果/模块B_渲染/run_20260604_223032_phase24/`
  - `结果/模块B_渲染/run_20260604_223032_phase120/`

### 1.4 每实验产物清单

- 12c：`summary.md/.json`、`obs_degradation_results.csv/.json`、`degradation_config.csv/.json`、`run.log`
- 12d：`summary.md/.json`、`cross_phase_results.csv/.json`、`run.log`
- 12e：`summary.md`、`summary.csv`、`summary.json`、`image_only_original_per_seed.csv`、`image_only_centered_per_seed.csv`、`run.log`
- 12f：`summary.md/.json`、`beta_sweep_summary.csv`、`beta_sweep_per_seed.csv`、`per_sample_base_predictions.npz`（逐样本 img4d/ocs4d，可复算任意 β）、`run.log`
- 12g：`gallery_12g_summary.md`、`outlier_full_table.csv`（42 条）、`threshold_summary.csv/.json`、`fig1-4*.png`、`run.log`

实际执行顺序（按效率）：12g → 12e → 12f →（12c 训练 ∥ phase24/120 渲染并行）→ 12d。Blender(OPTIX) 与 PyTorch 训练全程并行未互崩，省约 50 min 串行时间。

---

## 2. 主结果表

### 2.1 实验12c — Observation-style 退化（mean°，括号 Hit@5）
退化在近似线性强度域施加：`lin=expm1(norm·log1p(10))/10 → 退化 → log1p`。train 线性 max=0.925。**合成退化压力测试，非真实望远镜验证。**

| 退化档 | img_clean | img_same_aug | img_obs_aug | **U1 fusion** | U2 fusion obs_aug | OCS_only |
|---|---|---|---|---|---|---|
| clean | 1.72 (98%) | 2.68 | 1.88 | 1.95 (98%) | 1.68 | 6.58 (65%) |
| blur_sig1.5 | 2.83 | 3.09 | 1.99 | 1.98 | 1.78 | 6.58 |
| photon_g100 | 13.08 | 3.94 | 2.29 | **2.01** | 1.74 | 6.58 |
| read_0.005 | 87.30 | 3.26 | 61.84 | **1.95** | 33.46 | 6.58 |
| background_0.005 | 78.57 | 7.55 | 60.42 | **2.12** | 33.08 | 6.58 |
| starfield | 86.39 | 14.56 | 64.20 | **2.20** | 34.43 | 6.58 |
| saturate_0.8 | 1.72 | 2.68 | 1.88 | 1.95 | 1.68 | 6.58 |
| downsample_64 | 2.92 | 3.22 | 2.10 | 1.97 | 1.72 | 6.58 |
| combined_mild | 87.47 | 2.92 | 2.03 | 1.95 | 1.62 | 6.58 |
| combined_medium | 88.99 | 6.48 | 68.18 | **1.98** | 38.64 | 6.58 |
| combined_severe | 88.85 | 64.33 | 82.14 | **13.88** | 48.99 | **6.58** |

### 2.2 实验12d — 跨 phase 泛化（训练 phase63，测试 phase24/120，test=1998）

| phase | image_only | fusion_concat5 |
|---|---|---|
| phase63（同分布） | 1.69±0.09 (98%) | 1.57±0.12 (100%) |
| phase24（近后向，几何接近） | 11.34±0.23 (23%) | 6.85±0.87 (46%) |
| phase120（前向散射，几何迥异） | 83.08±1.74 (1%) | 79.71±1.42 (4%) |

跨 phase Δ（相对 phase63）：image_only phase24 +9.65°/phase120 +81.39°；fusion phase24 +5.28°/phase120 +78.14°。

### 2.3 实验12e — 质心居中控制

| case | mean±std | median | p90 | worst | Hit@5 | Hit@10 |
|---|---|---|---|---|---|---|
| original | 1.69±0.07 | 1.42 | 3.31 | 9.9 | 97.6% | 99.9% |
| centered | 2.88±0.14 | 2.23 | 5.42 | 53.8 | 87.4% | 97.9% |

corr(centroid_x, yaw)：原始 **0.665** → 居中后 -0.019（centroid_x std 11.53→0.29）；Δmean=+1.19°；居中平移 |dx| mean=10.1px。

### 2.4 实验12f — Late-fusion β sweep（β=image 权重；融合在单位 sin-cos 4D / A5 口径）

| 退化 | β=0(OCS) | β=0.3 | β=0.5 | β=0.7 | β=1(img) | best β | best | naive fusion(参照) | U1(参照) |
|---|---|---|---|---|---|---|---|---|---|
| clean | 6.58 | 5.24 | 3.72 | 2.06 | 1.72 | 0.9 | 1.67 | 1.47 | 1.95 |
| noise_0.01 | 6.58 | 20.45 | 48.86 | 75.46 | 85.93 | **0.0** | **6.58** | 73.36 | 1.95 |
| noise_0.10 | 6.58 | 21.67 | 50.63 | 77.17 | 89.12 | **0.0** | **6.58** | 73.57 | 2.31 |
| bright_0.50 | 6.58 | 5.34 | 4.08 | 2.83 | 3.18 | 0.8 | 2.81 | 1.86 | 1.98 |
| bright_1.50 | 6.58 | 5.28 | 3.81 | 2.20 | 1.94 | 0.9 | 1.87 | 1.49 | 2.0 |

### 2.5 实验12g — Outlier audit（复用 12b 42 条 / 全 49,950 评估）

| 阈值 | 计数 | 占比 |
|---|---|---|
| >30° | 42 | 0.084% |
| >60° | 40 | 0.080% |
| >90° | 35 | 0.070% |
| >150° | 17 | — |

姿态：**50% 位于 |pitch|>75° 极区**，26% 在 |pitch|=90° 极点；退化档：noise_0.10=25 主导；跨退化重复离群 4 个唯一 (seed,sample)：(0,887)、(2,185)、(2,223)、(3,223)。

---

## 3. 协议一致性与两处口径备案

一致：`split_coarse_to_fine(coarse_step=10)`（tr563/val140/test1998）、target `[sin,cos,sin,cos]`、great-circle 角误差、mean/median/p90/p95/worst/Hit@5/Hit@10、OCS=concat5 per_part_log 30D 仅 fit train、5 seeds、未覆盖既有主结果。

需 Codex 备案：
1. 退化在 normalized-log1p 上精确反归一化（图像存储为 `log1p(10·raw)/log1p(10)`，非纯 log1p），保证「线性强度域退化」物理解释成立。
2. 12f OCS-only MLP 为本轮重训（12b 未存权重）= **6.58°**，略高于 exp6 的 5.91°（同架构、超参差异）；报告内以 6.58° 为本实验内部参照，注明 cf. 5.91°，**不得**与 5.91° 混用或写成性能升降。

---

## 4. 对第一档 Acta/ASR 主投优先版的写作影响

1. 新增「Observation-style degradation & cross-geometry sanity tests」节：12c 为承重证据，支撑 degradation-aware OCS-image co-utilization 主线，并把退化诚实限定为合成。
2. 12f：写「explicit inference-time weighting can provide a robustness path」（噪声下回到 OCS 端 6.58° vs naive 73°），比 naive feature fusion 清晰；须注明 best β 为 oracle/inference-time 上界。
3. 12d：把「image-only 1.69°」限定为 phase63 同分布上界；fusion 同样跨 phase 脆弱（concat5 OCS 不托住图像分布漂移）。
4. 12e：进 Limitation——clean-image 性能部分依赖固定框定（1.69→2.88°），但形状信息仍主导（居中后 Hit@5 87%），回应 centroid_x~yaw r=0.66。
5. 12g：进 Supplementary/Limitations——rare large outliers <0.1%、集中极区，防 fully robust 误读。

---

## 5. 对 CJA/AST 与 TAES/JGCD 的策略影响（不启动后两档）

本批数据足以支撑第一档「条件性互补 + 融合失效机制」主线，无需真实望远镜数据即可形成完整审稿防御。CJA/AST、TAES/JGCD 的差异化卖点（更强 fallback 设计 / 3-DOF / 真实数据）仍是缺口，待作者确认第一档完结后再评估。**本轮不产出** `主稿_v0.2_CJA_AST*` / `主稿_v0.2_TAES_JGCD*`。

---

## 6. ⚠️ 不能写入论文的过度结论清单

1. ❌ U1 / fusion **automatically robust** / **automatically switches to OCS**（U1 是退化感知联合表示；12f best β 是 oracle，非自动门控）。
2. ❌ **OCS standalone fallback**（沿用 12b：OCS 是 active joint constraint，非独立托底）。
3. ❌ **fully robust / near-perfect**（combined_severe 下 U1 退到 13.88°、有极区大离群；phase120 全员 ~80°）。
4. ❌ **real telescope validation / operational / field-proven robustness**（全为合成退化与合成跨几何 sanity test）。
5. ❌ 把 12f best-β 写成「部署即用的自适应加权」（须注明 inference-time 上界，部署需独立退化检测/加权策略）。
6. ❌ 把 obs-aug 写成有效方法（本轮 obs-aug 未带来增益甚至更差，只能作为「更真实增强 ≠ 更鲁棒」的诚实反例）。
7. ❌ 把 12f 重训 6.58° 与 exp6 5.91° 混用或写成性能升降。

---

## 7. 诚实负结果（提升可信度，须如实写）

- **obs-aug 反而更差**：U1(简单 gaussian+brightness 增强) 在 read/background 上 ~2°，而 U2(obs-aug) 33-49°、image-only obs-aug 60-68°。机制：简单 σ=0.10 高斯增强恰好覆盖加性 read noise；obs-aug 把容量摊薄到多种退化、每种见得少。→「更真实的增强不必然更鲁棒」。
- **无方法全鲁棒**：combined_severe（U1 13.88°）与 phase120（全员 ~80°）下没有任何方法保持强性能；此处 OCS-only 6.58° 反而最优，凸显 OCS 在严重退化下的价值，但不能写成「OCS 托底」。

---

## 8. 阶段判定与下一步

- 后整合 Step 07c 实验执行完成，等待 Codex 审阅代码逻辑、实验条件、结果表与机制解释，再生成 `阶段整合输出/07c_*_整合清单.md`。
- 审阅通过后再决定 v0.2 Results/Discussion/Supplementary 吸收；**不覆盖 v0.1**。
- Q12-Q14（Data/Code/Author/Funding/COI）仍保留作者占位，不由 AI 代填。
