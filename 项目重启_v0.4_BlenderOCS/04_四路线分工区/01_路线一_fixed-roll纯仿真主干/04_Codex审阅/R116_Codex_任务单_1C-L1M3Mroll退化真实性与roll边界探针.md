# R116 Codex 任务单：1C-L1M3/M-roll 退化真实性与 roll 边界探针

最后更新：2026-07-01  
任务类型：给执行端 Claude 的长程执行提示词  
上游阶段门：R115 已通过 L1(M2) clean / P-INT 第一阶段  
执行端报告必须写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/104_1C-L1M3Mroll_退化真实性与roll边界探针_Claude执行报告.md
```

本文件是 Codex 调度/提示词文件，保留在 `04_Codex审阅/`。执行端不得把报告、结果或裁决文件写入 `04_Codex审阅/`。

---

## 0. 给 Claude 的总提示词

你现在执行路线一 C 的下一阶段长程任务：

```text
1C-L1M3Mroll_退化真实性与roll边界探针
```

R115 已接收 L1(M2) clean / P-INT 第一阶段正结果：在 model-known / fixed-roll / clean / P-INT 条件下，OCS-only 多观测总光度向量随 `L1-G1 -> L1-G3 -> L1-G5` 呈单调增益；P-EXT yaw-block stress test 仍坍缩。你本轮不要重复证明 L1(M2) clean 正结果，不要回到 single-frame 负结果补实验。

本轮目标是围绕 R115 暴露的缺口继续推进，但要控制范围：

```text
1. 补齐 R115 指出的审计缺口：跨几何量纲一致性核验 + val per-attitude 输出。
2. 启动 M3 physically degraded 真实性轴：先 smoke，再做小矩阵。
3. 执行 M-roll fixed-roll 边界探针：只检验有限 roll 扰动是否推翻当前 fixed-roll 结论。
4. 为 D3/P-DB/conformal 置信一致性做准备或小 smoke，不写成正式概率校准完成。
```

如果上下文、输出长度或文件写入受限，必须按 `Part 1/2/3...` 分段输出或分段写入，直到任务报告和交付清单完整。

---

## 1. 必读文件

先按顺序读取并在报告中列出“已读文件清单”。只引用关键结论，不要复述大段历史。

```text
CLAUDE.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R113_Codex_审阅_102通过_B6判据轴闭口并放行L1M2阶段门.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R115_Codex_审阅_103通过_L1M2多几何OCS第一阶段正结果.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/01_路线一C后续技术路线执行框架_R113通过.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/05_L1M2多几何OCS第一阶段正结果_R115通过.md
```

同时定位并按需读取 103/L1M2 的执行包与代码：

```text
02_Claude输出/103_1C-L1M2_多几何OCS主线长程执行_Claude执行报告.md
v0.4_results/11_l1m2_multigeometry_ocs/
06_v0.4_code/02_blender/render_l1m2_multigeometry.py
06_v0.4_code/05_postprocess/run_l1m2_multigeometry_postprocess.py
06_v0.4_code/07_training/build_l1m2_geometry_registry.py
06_v0.4_code/07_training/dataset_l1m2_multigeometry.py
06_v0.4_code/07_training/train_l1m2_multigeometry.py
06_v0.4_code/07_training/postprocess_l1m2_metrics.py
06_v0.4_code/07_training/run_l1m2_matrix.sh
```

必要时回看旧入口，但不要展开无关历史：

```text
06_v0.4_code/00_config/config_v0_4.py
06_v0.4_code/02_blender/render_full_2664_shadow.py
06_v0.4_code/05_postprocess/run_full_postprocess.py
06_v0.4_code/07_training/train_b6_circular_regression.py
```

---

## 2. 总体交付路径

所有新结果写入：

```text
v0.4_results/12_l1m3_degraded_mroll/
```

建议新增或派生脚本：

```text
06_v0.4_code/07_training/export_l1m2_val_samples.py
06_v0.4_code/07_training/audit_l1m2_geometry_scale_consistency.py
06_v0.4_code/07_training/degrade_l1m3_images.py
06_v0.4_code/07_training/train_l1m3_degraded.py
06_v0.4_code/07_training/run_l1m3_degraded_matrix.sh
06_v0.4_code/02_blender/render_mroll_probe.py
06_v0.4_code/05_postprocess/run_mroll_probe_postprocess.py
06_v0.4_code/07_training/run_mroll_probe_matrix.sh
06_v0.4_code/07_training/postprocess_l1m3_mroll_metrics.py
```

如果能在不破坏旧脚本的情况下复用 L1M2 脚本，也可以通过新增 wrapper / CLI 参数实现。禁止覆盖旧结果目录，禁止改写已经通过的 R115 结果文件。

命令环境必须遵守：

```text
Blender:
"D:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --background --python "<script>"

Python:
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" "<script>"
```

不要假设系统默认 `python` 或 `blender` 可用。中文路径必须加英文双引号。

---

## 3. 子任务 A：补齐 R115 审计缺口

### A1. val per-attitude 输出补齐

R115 抽查发现正式 run 有：

```text
metrics_val_*.json
metrics_test_*.json
samples_test_final/best.csv/.npz
```

但缺少：

```text
samples_val_final.csv/.npz
samples_val_best.csv/.npz
```

本轮必须优先补齐。最低要求：

```text
1. 对 R115 的 9 个 P-INT 正式 run 补导出 samples_val_final/best。
2. 对 3 个 P-EXT ocs_only run 若 checkpoint 与 split 足够，也补导出 samples_val_final/best；若成本高，至少报告原因。
3. val/test 的字段结构保持一致，包含 record_id、yaw/pitch true/pred/error、geometry_group、mode、protocol、top-k、posterior-like、entropy、margin。
4. 输出补齐索引表。
```

建议输出：

```text
v0.4_results/12_l1m3_degraded_mroll/audit/l1m2_val_samples_recovery_summary.csv
v0.4_results/12_l1m3_degraded_mroll/audit/l1m2_val_samples_recovery_summary.json
```

如果由于旧 checkpoint、代码状态或 split manifest 不足以复现 val samples，不要静默跳过；必须列出缺口、证据路径和建议修复方式。

### A2. 跨几何量纲一致性核验

R115 已接收 L1M2，但要求补显式审计表。本轮必须生成跨几何量纲一致性核验：

```text
1. 各几何 phase24/45/63/90/120 的总光度分布：mean/std/min/max/percentiles。
2. 各几何 contributing pixels 或有效像素分布。
3. r_max、pixel_area、i_scale、depth_epsilon、resolution、log1p/z-score 参数来源。
4. train-only transform 参数与 val/test 泄漏检查。
5. 每个 attitude 在 L1-G1/G3/G5 中的 record_id/yaw/pitch/roll 对齐检查。
6. 明确说明这是 simulated multi-view geometry，不是路线二真实跨时间多几何。
```

建议输出：

```text
v0.4_results/12_l1m3_degraded_mroll/audit/l1m2_geometry_scale_consistency.csv
v0.4_results/12_l1m3_degraded_mroll/audit/l1m2_geometry_scale_consistency.md
v0.4_results/12_l1m3_degraded_mroll/audit/l1m2_transform_leakage_check.json
```

---

## 4. 子任务 B：M3 degraded 真实性轴

### B1. 设计原则

degraded 轴用于检验 L1 多几何 OCS 与 image/joint 在物理合理退化下是否仍有价值。不得复用 B6 的粗增广包作为正式 degraded 模型。

允许的退化类型：

```text
PSF / Gaussian blur
Poisson shot noise + Gaussian read noise
背景常量 + 线性梯度
低分辨率 / 下采样再上采样
测光误差 / flux multiplicative noise
```

本轮优先做受控小矩阵，不做开放超参搜索。建议预注册两个等级：

```text
degraded-mild:
  blur_sigma_px = 0.75
  read_noise_sigma = 0.01
  flux_noise_frac = 0.03
  background_level = low

degraded-moderate:
  blur_sigma_px = 1.25
  read_noise_sigma = 0.02
  flux_noise_frac = 0.08
  background_level = moderate + weak gradient
```

如果执行端发现这些参数与图像量纲不匹配，可按实际数据 scale 做小幅调整，但必须在 report 中列出原因、最终参数和样例图/数值摘要。

### B2. 最低执行矩阵

先 smoke：

```text
degraded smoke:
  geometry_group: L1-G5
  protocol: P-INT
  degradation: degraded-mild
  modes: ocs_only, image_only, joint
  epochs: 1 或小子集
```

smoke 通过后执行正式小矩阵：

```text
protocol: P-INT
geometry_group: L1-G1, L1-G3, L1-G5
degradation: clean, degraded-mild, degraded-moderate
modes:
  ocs_only: L1-G1/G3/G5 必做
  image_only: L1-G1 和 L1-G5 必做；G3 可视资源补
  joint: L1-G1 和 L1-G5 必做；G3 可视资源补
select: final + best-val
seed: 42；如资源允许，再补 seed 7 或 123 做稳定性 smoke
```

注意：

```text
1. clean 不需要重跑时可引用 R115 指标，但 degraded 汇总表必须标明 clean 来源。
2. OCS-only degraded 应只对 total-flux vector 施加测光误差，不把图像噪声错误地作用到 OCS。
3. image_only degraded 应对输入图像施加图像退化。
4. joint degraded 应同时使用 degraded image 与带测光误差的 total-flux vector；若只退化其中一支，必须另标为 ablation。
```

建议输出：

```text
v0.4_results/12_l1m3_degraded_mroll/degraded/l1m3_degraded_run_matrix.csv
v0.4_results/12_l1m3_degraded_mroll/degraded/l1m3_degraded_metrics_summary_final.csv
v0.4_results/12_l1m3_degraded_mroll/degraded/l1m3_degraded_metrics_summary_best.csv
v0.4_results/12_l1m3_degraded_mroll/degraded/l1m3_degraded_gain_and_drop_summary.md
v0.4_results/12_l1m3_degraded_mroll/degraded/figures/
```

每个正式 run 仍需保存：

```text
run_config.json
train_log.csv
metrics_val_final/best.json
metrics_test_final/best.json
samples_val_final/best.csv/.npz
samples_test_final/best.csv/.npz
checkpoint_final/best.pt
```

---

## 5. 子任务 C：M-roll fixed-roll 边界探针

### C1. 定位

M-roll 只是路线一 C 的 fixed-roll 边界探针，用来回答：

```text
当前 fixed-roll clean/P-INT 结论是否被少量 roll 扰动直接推翻？
```

M-roll 不是三轴小项目，不启动三轴最亮构型/观测规划，不写成真实三轴姿态反演系统。

### C2. 预注册 roll 设置

建议采用小探针：

```text
roll = 0 deg baseline
roll = +15 deg
roll = -15 deg
roll = +30 deg
roll = -30 deg
```

优先选择：

```text
geometry_group: L1-G5
protocol: P-INT
modes: image_only, joint
optional: ocs_only 如果多几何 total flux 能低成本生成
attitudes: 优先全 2664；如成本过高，先用覆盖 yaw/pitch 的 stratified subset，并明确 subset 不能当正式结论。
```

如果渲染成本可控，执行 full 2664；如果不可控，先做 subset smoke 并报告预计全量成本。

### C3. 输出要求

建议输出：

```text
v0.4_results/12_l1m3_degraded_mroll/mroll/mroll_geometry_registry.json
v0.4_results/12_l1m3_degraded_mroll/mroll/mroll_data_audit.md
v0.4_results/12_l1m3_degraded_mroll/mroll/mroll_run_matrix.csv
v0.4_results/12_l1m3_degraded_mroll/mroll/mroll_metrics_summary_best.csv
v0.4_results/12_l1m3_degraded_mroll/mroll/mroll_roll_sensitivity_summary.md
v0.4_results/12_l1m3_degraded_mroll/mroll/figures/
```

结论口径只能写：

```text
在本轮 roll 设置、几何组、协议和数据规模下，roll 扰动对 fixed-roll 结论的影响如何。
```

禁止写：

```text
三轴姿态反演已解决；
三轴小项目已完成；
真实未知目标 roll 可反演。
```

---

## 6. 子任务 D：D3/P-DB/conformal 准备

本轮不要求完成正式 P-DB 或 conformal prediction 阶段门，但必须为后续准备可用材料。

最低要求：

```text
1. 基于补齐的 samples_val_*，生成 val/test 分开的置信一致性输入索引。
2. 明确当前 posterior-like 是工程候选分数，不是真实 Bayesian posterior。
3. 如果低成本可行，做一个 P-DB/template retrieval smoke：
   - 使用 train grid 的 L1-G5 total-flux vector 作为 template 库；
   - 用 cosine 或 L2 相似度输出 top-k；
   - 只报告 top-k candidate 与误差，不写真实反演成功率。
4. 如果低成本可行，做 conformal smoke：
   - 使用 val set 校准 yaw error quantile；
   - 在 test set 报告 coverage / set size；
   - 明确这是 smoke，不是最终置信校准。
```

建议输出：

```text
v0.4_results/12_l1m3_degraded_mroll/d3/l1m3_confidence_inputs_index.csv
v0.4_results/12_l1m3_degraded_mroll/d3/pdb_template_retrieval_smoke.csv
v0.4_results/12_l1m3_degraded_mroll/d3/conformal_smoke_summary.md
```

若本轮资源不足，至少完成输入索引和设计说明，不要空泛写路线规划。

---

## 7. 本轮不得越界

禁止执行或表述：

```text
1. 不启动头A/头B大合并裁决。
2. 不把 B6 或 L1(M2) 第一阶段写成路线一 C 整体闭口。
3. 不写论文正文，不写成果区新结论。
4. 不启动 T3/L2 光变正式训练。
5. 不启动三轴小项目、路线二、路线三、路线四扩展。
6. 不把 v0.4 写成真实未知目标姿态反演系统。
7. 不把 GEO 数据写成有三轴姿态真值的监督反演数据集。
8. 不把 per-part OCS 当作现实主线输入。
9. 不把 P-EXT yaw-block 写成已解决。
10. 不把 posterior-like 写成真实 Bayesian posterior。
11. 不做开放式超参搜索，不换大 backbone，不覆盖旧结果目录。
```

允许写：

```text
1. R115 已接收 clean/P-INT 下 OCS-only L1-G1/G3/G5 单调增益。
2. degraded 和 M-roll 是当前边界与真实性检验，不是路线一 C 闭口。
3. P-DB/conformal 本轮若只做 smoke，只能写成后续置信一致性的准备。
```

---

## 8. 执行报告结构

报告写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/104_1C-L1M3Mroll_退化真实性与roll边界探针_Claude执行报告.md
```

报告必须包含：

```text
1. 任务结论摘要：完成 / 部分完成 / 阻塞。
2. 已读文件与遵守的红线。
3. R115 缺口补齐情况：samples_val_*、跨几何量纲一致性核验。
4. 新增或修改脚本清单：路径、用途、是否派生旧脚本。
5. 新生成数据和结果目录清单。
6. degraded smoke 与正式小矩阵结果。
7. M-roll smoke/正式探针结果。
8. D3/P-DB/conformal 准备或 smoke 结果。
9. 与 R115 clean/P-INT 基线的对照表：必须标明哪些是引用 R115，哪些是本轮新跑。
10. 未完成项与阻塞项：明确是资源、代码、数据、路线边界还是实验成本问题。
11. 红线自查。
12. 交给 Codex 审阅的问题清单。
```

报告不要写成论文正文，不要扩大战果。所有结论必须绑定到本轮输出文件路径。

---

## 9. 成功判据

最低接收标准：

```text
1. samples_val_* 或等价 val per-attitude 输出补齐，或给出不可补齐的实证阻塞。
2. 跨几何量纲一致性核验表完成。
3. degraded-mild 的 L1-G5 smoke 跑通。
4. 至少完成 degraded 小矩阵中的 OCS-only L1-G1/G3/G5。
5. M-roll 至少完成一个代表设置的 smoke，并给出全量成本评估或正式小矩阵结果。
6. D3/P-DB/conformal 至少完成输入索引，不再只有口头规划。
7. 报告路径和结果路径正确，未写成果区，未生成 Codex 审阅文件，未修改 CLAUDE.md。
```

强接收标准：

```text
1. degraded-mild 与 degraded-moderate 都完成 G1/G3/G5 的 ocs_only，并完成 G1/G5 的 image_only/joint。
2. M-roll 完成 L1-G5 下 roll={0,+15,-15,+30,-30} 的 image_only/joint 小矩阵。
3. P-DB retrieval smoke 与 conformal smoke 都生成可审计表。
4. 所有正式 run 均保存 val/test per-attitude samples。
```

---

## 10. 最后交付提醒

执行完成后，只提交候选执行包和 Claude 报告。不要自行把新训练结果升级到成果区，不要生成 Codex 审阅文件，不要修改 `CLAUDE.md`。作者会把你的报告路径交给 Codex，由 Codex 进行 R117 审阅或返工裁决。

