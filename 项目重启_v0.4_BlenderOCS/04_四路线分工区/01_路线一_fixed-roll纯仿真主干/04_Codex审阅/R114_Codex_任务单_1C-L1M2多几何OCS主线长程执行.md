# R114 Codex 任务单：1C-L1M2 多几何 OCS 主线长程执行

最后更新：2026-06-30  
任务类型：给执行端 Claude 的长程执行提示词  
上游阶段门：R113 已放行 L1(M2) 多几何 OCS 主线  
执行端报告必须写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/103_1C-L1M2_多几何OCS主线长程执行_Claude执行报告.md
```

本文件是 Codex 调度/提示词文件，保留在 `04_Codex审阅/`。执行端不得把报告、结果或裁决文件写入 `04_Codex审阅/`。

---

## 0. 给 Claude 的总提示词

你现在执行路线一 C 的下一阶段长程任务：

```text
1C-L1M2_多几何OCS主线长程执行
```

这不是路线再规划，也不是 single-frame 负结果补实验。R113 已经裁定：B6-FIX01 关闭的是 `single-frame 判据/输出头补救轴`，旧 single-frame 负结果不再继续扩展；但这不关闭路线一 C 整体，也不触发头A/头B大合并裁决。你本轮要把路线一 C 转入 24 号主线定义的 L1(M2)：跨几何多观测总光度向量。

如果上下文、输出长度或文件写入受限，必须按 `Part 1/2/3...` 分段输出或分段写入，直到任务报告和交付清单完整。

---

## 1. 必读文件

先按顺序读取并在报告中列出“已读文件清单”。只需引用关键结论，不要复述大段历史。

```text
CLAUDE.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R113_Codex_审阅_102通过_B6判据轴闭口并放行L1M2阶段门.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/00_B6-FIX01与single-frame负结果收口说明_R113通过.md
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/00_当前主用成果/01_路线一C后续技术路线执行框架_R113通过.md
```

同时定位并按需读取以下代码入口：

```text
06_v0.4_code/00_config/config_v0_4.py
06_v0.4_code/02_blender/render_full_2664_shadow.py
06_v0.4_code/05_postprocess/run_phase1_fullrun.py
06_v0.4_code/05_postprocess/run_full_postprocess.py
06_v0.4_code/06_manifest/build_image_manifest_v0_4.py
06_v0.4_code/06_manifest/build_ocs_manifest_v0_4.py
06_v0.4_code/06_manifest/check_manifest_consistency_v0_4.py
06_v0.4_code/07_training/dataset.py
06_v0.4_code/07_training/enhanced_ocs_dataset.py
06_v0.4_code/07_training/feature_extract_ocs.py
06_v0.4_code/07_training/split_dataset.py
06_v0.4_code/07_training/train_baseline.py
06_v0.4_code/07_training/train_entry.py
06_v0.4_code/07_training/train_b6_circular_regression.py
```

需要回看既有数据/结果时，优先检查：

```text
v0.4_results/01_fullrun/
v0.4_results/03_training_baseline/
v0.4_results/04_ocs_features/
v0.4_results/09_p1a_metric_recompute/
v0.4_results/10_b6_circular_regression_fix01/
```

---

## 2. 本轮目标

完成 L1(M2) 的第一轮可审计执行包：

```text
从现有 phase63/G1 单几何总光度基线出发，
构建或核验 G1/G3/G5 跨几何总光度向量，
在 P-INT 主协议下完成 clean 第一阶段受控实验，
并为后续互补性、置信一致性、可观测性地图保存中间量。
```

最低必须回答：

```text
1. 现有代码与数据是否足以支持 G1/G3/G5？
2. 若不足，缺的是新渲染、后处理、manifest、split，还是训练数据组织？
3. L1 多几何总光度向量能否形成可训练输入？
4. 在 clean / P-INT 下，G1 -> G3 -> G5 是否给 OCS-only 带来可审计增益曲线？
5. image_only 与 joint 是否能被同一 split / 同一评价口径对齐比较？
6. per-attitude predictions、top-k、posterior-like score、entropy、margin、overlap/JS 是否已保存到可复查文件？
```

---

## 3. 几何预注册与编号冲突处理

`01_路线一C后续技术路线执行框架_R113通过.md` 使用实验层命名：

```text
G1 = phase63 单几何
G3 = phase63 + 低相位角 + 高相位角
G5 = config 预留 5 组观测几何全集
```

但 `config_v0_4.py` 中 `OBS_GEOMETRIES` 注释可能使用代码层编号：

```text
OBS_GEOMETRIES[0] = phase63_backscatter       # 代码注释中可能称 G0 baseline
OBS_GEOMETRIES[1] = phase24_near_backscatter
OBS_GEOMETRIES[2] = phase120_forward_scatter
OBS_GEOMETRIES[3] = phase90_side
OBS_GEOMETRIES[4] = phase45_overhead
```

本轮必须先生成几何注册表，避免混号。建议采用：

```text
实验组名 L1-G1 = [phase63_backscatter]，即现有 phase63 baseline / OBS_GEOMETRIES[0]
实验组名 L1-G3 = [phase24_near_backscatter, phase63_backscatter, phase120_forward_scatter]
实验组名 L1-G5 = [phase24_near_backscatter, phase45_overhead, phase63_backscatter, phase90_side, phase120_forward_scatter]
```

要求：

```text
1. 在报告中明确区分“实验组名 L1-G1/G3/G5”和“代码 OBS_GEOMETRIES 索引/注释”。
2. 输出 geometry registry，建议路径：
   v0.4_results/11_l1m2_multigeometry_ocs/l1m2_geometry_registry.json
   v0.4_results/11_l1m2_multigeometry_ocs/l1m2_geometry_registry.md
3. 如果代码实际几何、已有数据或 manifest 与上述预注册不一致，不得自行改写路线定义；必须列出冲突证据路径、影响范围和建议交回 Codex 裁决。
```

---

## 4. 执行范围

允许执行：

```text
1. 代码/数据审计：定位现有 phase63 数据、OBS_GEOMETRIES、render/postprocess/manifest/training 入口。
2. 新增 L1(M2) 专用脚本或数据集封装，优先复制/派生旧脚本，不破坏旧结果链。
3. 必要的新渲染、后处理、manifest 生成和 split 对齐，用于补齐 G3/G5。
4. clean 第一阶段训练与评估。
5. OCS-only / image_only / joint 的可审计 baseline。
6. posterior-like / top-k / entropy / margin / overlap / JS / per-attitude error 等中间量保存。
7. 小规模 smoke 与正式第一阶段矩阵。
```

本轮不要求一次铺满所有 degraded、P-DB、P-EXT、M-roll，但必须为它们保留接口和报告计划。若资源允许，可做小 smoke；不得把未完成 smoke 写成正式结论。

禁止执行：

```text
1. 不启动头A/头B大合并裁决。
2. 不把 B6 写成路线一 C 整体闭口。
3. 不写论文正文，不写成果区新结论。
4. 不启动 T3/L2 光变正式训练。
5. 不启动三轴小项目、路线二、路线三、路线四扩展。
6. 不把 v0.4 写成真实未知目标姿态反演系统。
7. 不把 GEO 数据写成有三轴姿态真值的监督反演数据集。
8. 不把 per-part OCS 当作现实主线输入；它最多是 F2 semi-oracle / diagnostic。
9. 不做开放式超参搜索，不换大 backbone，不覆盖旧结果目录。
```

---

## 5. 数据与代码交付建议

所有新结果写入：

```text
v0.4_results/11_l1m2_multigeometry_ocs/
```

建议新增或派生脚本：

```text
06_v0.4_code/07_training/dataset_l1m2_multigeometry.py
06_v0.4_code/07_training/train_l1m2_multigeometry.py
06_v0.4_code/07_training/postprocess_l1m2_metrics.py
06_v0.4_code/07_training/run_l1m2_matrix.sh
```

如果需要补齐多几何渲染/后处理/manifest，可新增或派生：

```text
06_v0.4_code/02_blender/render_l1m2_multigeometry.py
06_v0.4_code/05_postprocess/run_l1m2_multigeometry_postprocess.py
06_v0.4_code/06_manifest/build_l1m2_multigeometry_manifest.py
06_v0.4_code/06_manifest/check_l1m2_multigeometry_consistency.py
```

命令环境必须遵守：

```text
Blender:
"D:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --background --python "<script>"

Python:
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" "<script>"
```

不要假设系统默认 `python` 或 `blender` 可用。中文路径必须加英文双引号。

---

## 6. 第一阶段实验矩阵

优先完成 clean / P-INT：

```text
协议：P-INT
真实性：clean
几何组：L1-G1, L1-G3, L1-G5
通道：ocs_only, image_only, joint
split：优先复用既有 5-fold yaw-block / fold split 结构；如必须新增 P-INT split，需说明原因并保存 split 文件。
评价：final 与 best-val 口径都保留；主表以同一口径对齐。
```

P-EXT 仅作为 stress-test 边界保留，不再独占主线。若能低成本复用既有 yaw-block split，可输出附表；若成本高，本轮只写清楚保留接口。

degraded 本轮只允许作为第二优先级：

```text
clean 正式第一阶段完成后，再做 degraded smoke 或计划表。
不要复用 B6 的粗增广包作为正式 degraded 模型。
正式 degraded 候选应是 PSF/模糊、Poisson/read noise、背景/梯度、低分辨率、测光误差等物理合理退化。
```

---

## 7. 模型与输入要求

OCS 主线输入必须是总光度向量：

```text
F1 / L1-G1: [total_flux_phase63]
L1-G3: [total_flux_phase24, total_flux_phase63, total_flux_phase120]
L1-G5: [total_flux_phase24, total_flux_phase45, total_flux_phase63, total_flux_phase90, total_flux_phase120]
```

允许对总光度向量做清晰记录的标准化，例如 log1p、z-score、min-max；但必须保存 transform 参数和 train/val/test 泄漏检查说明。

不允许把 `total + 3 per-part` 的 4 维 OCS 当成现实主线。若要做 per-part 诊断，只能单独标为：

```text
F2 semi-oracle / diagnostic，不进入主 claim，不替代 L1 总光度向量。
```

image_only 的图像来源：

```text
优先使用 phase63 / L1-G1 对应图像作为固定图像 baseline。
若尝试多几何图像输入，必须单独标明为额外 exploratory，不得混入 L1 总光度主线。
```

joint 的主线含义：

```text
image_phase63 + L1 total-flux vector
```

不要把 joint 写成“真实多传感器在轨系统”，它只是同源仿真下的互补性工具。

---

## 8. 必须保存的输出文件

至少保存：

```text
v0.4_results/11_l1m2_multigeometry_ocs/
  l1m2_geometry_registry.json
  l1m2_geometry_registry.md
  l1m2_data_audit.json
  l1m2_data_audit.md
  l1m2_split_manifest_*.json
  l1m2_run_matrix.csv
  l1m2_run_matrix.json
  l1m2_metrics_summary_final.csv
  l1m2_metrics_summary_best.csv
  l1m2_gain_curve_G1_G3_G5.csv
  l1m2_gain_curve_G1_G3_G5.md
  l1m2_confidence_consistency_summary.csv
  l1m2_postprocess_summary.json
  _l1m2_batch.log
```

每个正式 run 子目录至少保存：

```text
run_config.json
train_log.csv
metrics_val_final.json
metrics_test_final.json
metrics_val_best.json
metrics_test_best.json
samples_val_final.csv/.npz
samples_test_final.csv/.npz
samples_val_best.csv/.npz
samples_test_best.csv/.npz
checkpoint_final.pt
checkpoint_best.pt
```

`samples_*.csv/.npz` 至少包含或可反查：

```text
record_id
yaw_true_deg
pitch_true_deg
yaw_pred_deg
pitch_pred_deg
yaw_circular_error_deg
pitch_abs_error_deg
geometry_group
mode
fold
posterior_like_scores 或候选分数
top1/top3/top5 candidate ids
entropy
margin
```

若 posterior-like/top-k 不是网络原生输出，必须说明构造方式。例如可在训练网格/template 上用距离或相似度构造候选分布，但不得写成真实 Bayesian posterior。

互补性/一致性文件至少要能支持后续计算：

```text
image vs OCS vs joint 的 top-k overlap
image vs OCS 的 disagreement
JS divergence 或可替代的分布距离
entropy / margin 与 error 的关系
按 yaw/pitch 区域分层的误差地图
```

---

## 9. 审计与 smoke 要求

正式训练前必须先做：

```text
1. geometry registry smoke：确认 G1/G3/G5 每个姿态的几何条目数量正确。
2. manifest consistency smoke：确认同一 attitude 在不同几何下 record_id/yaw/pitch/roll 可对齐。
3. dataset smoke：分别加载 ocs_only/image_only/joint 一个 batch，记录 tensor shape。
4. training smoke：至少 1 个 fold、1 个 epoch、ocs_only L1-G3 或 L1-G5 跑通。
5. postprocess smoke：至少生成一个 samples_test_*.csv/.npz 并能计算 yaw/pitch error。
```

若 smoke 未通过，不要继续正式矩阵；报告阻塞点、报错日志、已生成文件和建议修复路径。

---

## 10. 执行报告结构

报告写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/103_1C-L1M2_多几何OCS主线长程执行_Claude执行报告.md
```

报告必须包含：

```text
1. 任务结论摘要：完成 / 部分完成 / 阻塞。
2. 已读文件与遵守的红线。
3. 代码与数据审计：现有 phase63、OBS_GEOMETRIES、render/postprocess/manifest/training 入口。
4. 几何注册表：实验组 L1-G1/G3/G5 与代码 OBS_GEOMETRIES 索引的对应关系。
5. 新增或修改的脚本清单：路径、用途、是否派生旧脚本。
6. 新生成数据和结果目录清单。
7. smoke 结果。
8. 正式 clean / P-INT 第一阶段矩阵结果。
9. G1 -> G3 -> G5 增益曲线：至少 OCS-only，尽量包含 image_only / joint 对齐表。
10. posterior-like/top-k/entropy/margin/overlap/JS 文件说明。
11. 未完成项与阻塞项：明确是资源限制、代码冲突、数据缺口还是路线定义冲突。
12. 红线自查：逐条说明没有越界。
13. 交给 Codex 审阅的问题清单。
```

报告不要写成论文正文，不要扩大战果。所有结论都必须绑定到本轮输出文件路径。

---

## 11. 成功判据

本轮最低接收标准：

```text
1. 完成上下文、代码、数据审计。
2. 明确并保存 L1-G1/G3/G5 geometry registry。
3. G1/G3/G5 数据可用性被验证；若缺失，完成必要补齐或给出明确阻塞。
4. 至少一个 L1(M2) dataset smoke 和一个 training/postprocess smoke 跑通。
5. 至少完成 clean / P-INT / OCS-only 的 G1/G3/G5 对齐结果。
6. 优先完成 image_only 与 joint 对齐结果；若未完成，必须说明原因和剩余命令。
7. 输出 per-attitude predictions 与后续置信一致性所需中间量。
8. 所有新输出在 `v0.4_results/11_l1m2_multigeometry_ocs/`，报告在 `02_Claude输出/103...md`。
```

强接收标准：

```text
1. clean / P-INT 下 ocs_only, image_only, joint 全部完成 G1/G3/G5。
2. final 与 best-val 双口径齐全。
3. G1 -> G3 -> G5 增益曲线、互补性摘要、置信一致性摘要全部生成。
4. P-EXT 或 degraded 至少有 smoke，不作为主结论。
```

---

## 12. 本轮不得使用的表述

报告中禁止写：

```text
光度无用
yaw 物理不可观测
多几何 OCS 失败
路线一 C 已整体闭口
头A/头B 已大合并
真实未知目标姿态反演系统
真实望远镜验证
field-proven / operational-ready
GEO 数据库具备三轴姿态真值
per-part OCS 是现实可运营主线输入
```

允许写：

```text
在本轮 clean/P-INT/指定 split/指定输入条件下观察到的 G1/G3/G5 指标变化。
single-frame 负结果已由 R113 条件性收口，L1 多几何 OCS 尚需本轮验证。
P-EXT 是 stress test，不能替代 P-INT 主线。
posterior-like score 是工程候选分数，不是真实 Bayesian posterior。
```

---

## 13. 最后交付提醒

执行完成后，只提交候选执行包和 Claude 报告。不要自行把新训练结果升级到成果区，不要生成 Codex 审阅文件，不要修改 `CLAUDE.md`。作者会把你的报告路径交给 Codex，由 Codex 进行 R115 审阅或返工裁决。

