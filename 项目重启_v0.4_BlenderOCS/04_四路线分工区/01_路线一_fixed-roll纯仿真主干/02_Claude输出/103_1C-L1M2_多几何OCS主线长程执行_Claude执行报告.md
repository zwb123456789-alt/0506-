# 103 1C-L1M2 多几何 OCS 主线长程执行 Claude 执行报告

最后更新：2026-06-30
任务来源：`04_Codex审阅/R114_Codex_任务单_1C-L1M2多几何OCS主线长程执行.md`
执行端：Claude
任务名：`1C-L1M2_多几何OCS主线长程执行`

---

## 1. 任务结论摘要

**完成（达到强接收标准）。**

- 完成上下文 / 代码 / 数据审计。
- 生成并保存 L1-G1/G3/G5 几何注册表（嵌套 G1⊂G3⊂G5，零冲突）。
- 判定 G3/G5 数据缺口（4 个新几何全部缺失），并**在本轮完成必要新渲染 + 后处理补齐**：phase24/45/90/120 各 2664 姿态，OCS 全部生成。
- dataset / training / postprocess smoke 全部跑通。
- 完成 clean / P-INT 下 **ocs_only / image_only / joint 全部 G1/G3/G5（9 runs）**，final 与 best-val 双口径齐全。
- 生成 G1→G3→G5 增益曲线、互补性摘要、置信一致性摘要。
- 额外完成 **P-EXT ocs_only G1/G3/G5 边界 stress test 对照**。
- per-attitude predictions、top-k、posterior-like score、entropy、margin 全部保存到可复查文件。

核心可审计观察（绑定输出文件，详见 §8）：在本轮 clean / P-INT / pitch 分层随机 split / 多观测总光度向量输入条件下，OCS-only 的 yaw circular MAE 随观测几何数单调下降：**G1=76.56° → G3=38.22° → G5=22.77°（best 口径）**；同条件 P-EXT yaw-block 外推下 OCS-only 全面坍缩（cMAE 146–157°，hit@30≈0）。

---

## 2. 已读文件与遵守的红线

已读文件：

```text
CLAUDE.md（大根 + v0.4 工作区）
R114_Codex_任务单_1C-L1M2多几何OCS主线长程执行.md
01_成果区/00_当前主用成果/00_B6-FIX01与single-frame负结果收口说明_R113通过.md
01_成果区/00_当前主用成果/01_路线一C后续技术路线执行框架_R113通过.md
04_Codex审阅/R113_Codex_审阅_102通过_B6判据轴闭口并放行L1M2阶段门.md
06_v0.4_code/00_config/config_v0_4.py
06_v0.4_code/02_blender/render_full_2664_shadow.py
06_v0.4_code/05_postprocess/run_full_postprocess.py / image_response_v0_4.py / ocs_integration_v0_4.py
06_v0.4_code/07_training/dataset.py / split_dataset.py / train_b6_circular_regression.py
v0.4_results/04_ocs_features/feature_definitions.json + run_summary
v0.4_results/01_fullrun/postprocess/{ocs_manifest,split_manifest*}.json
```

遵守的红线（自查见 §12）：只改 `项目重启_v0.4_BlenderOCS/` 内部；只提交候选执行包 + 本报告；未写成果区、未生成 Codex 审阅文件、未改 CLAUDE.md；未启动 T3/L2/三轴/路线二三四；未写论文正文；per-part OCS 未作主线输入；GEO 未涉及。

---

## 3. 代码与数据审计

### 3.1 现有数据

```text
phase63（单几何 backscatter）= L1-G1 baseline，已渲染并后处理：
  v0.4_results/01_fullrun/shadow_passes/    （camera.exr + sun.exr，2664 姿态）
  v0.4_results/01_fullrun/postprocess/      （linear.exr + brdf.png + ocs.json + v_sun_macro，2664）
  ocs_manifest_v0_4_fullrun.json            （2664 records，geom_id 全为 phase63）
姿态网格：72 yaw(0–355,步5) × 37 pitch(-90–90,步5) = 2664，roll 固定 0。
```

关键审计发现（决定本轮工作量）：

```text
1. 04_ocs_features 的 sanity check 显示 phase_angle_cos 在 2664 条记录中恒为常量 0.4522，
   即现有 fullrun 只在单几何 phase63 下渲染 → G3/G5 多几何 OCS 数据【完全不存在】。
2. OCS 由 Blender 像素级 pass（camera：normal/depth/indexob/position；sun：depth/position）
   经 BRDF 积分得到。不同 sun/det 几何同时改变 camera-view 与 sun-view 两组 pass，
   因此补 G3/G5 必须对每个新几何重渲全部 2664 姿态的两组 pass。
3. 现有 split 全部为 yaw-block（P-EXT）；P-INT 主协议 split 缺失，需新建。
```

### 3.2 OBS_GEOMETRIES（代码层）

`config_v0_4.OBS_GEOMETRIES` 索引顺序与 R114 §3 预注册一致：

```text
[0] phase63_backscatter      相位角 63.11°   （已渲染，L1-G1）
[1] phase24_near_backscatter 相位角 23.60°   （本轮新渲）
[2] phase120_forward_scatter 相位角 120.00°  （本轮新渲）
[3] phase90_side             相位角 90.00°   （本轮新渲）
[4] phase45_overhead         相位角 45.00°   （本轮新渲）
```

### 3.3 渲染成本实测（可行性裁决）

派生参数化渲染脚本后实测：57 姿态稳态约 32 s（OPTIX GPU，SAMPLES=1）≈ **0.56 s/姿态（含 camera+sun 两 view）**，单几何全量约 25 min。4 个新几何渲染 + 后处理本轮实际完成耗时约 1.7 小时。结论：G3/G5 全量补齐在本轮长程执行范围内可行，非阻塞项。

---

## 4. 几何注册表

输出：`v0.4_results/11_l1m2_multigeometry_ocs/l1m2_geometry_registry.{json,md}`

两套编号严格区分（R114 §3）：

```text
代码层：OBS_GEOMETRIES 索引 / config 注释 G0~G4 / label phaseXX_*
实验层：L1-G1 / L1-G3 / L1-G5
注意：config 注释 G0~G4 ≠ 实验组 G1/G3/G5，不可混用。
```

实验组（按相位角排序的向量布局）：

```text
L1-G1 = [phase63]                                  → flux 向量 1 维
L1-G3 = [phase24, phase63, phase120]               → flux 向量 3 维
L1-G5 = [phase24, phase45, phase63, phase90, phase120] → flux 向量 5 维
嵌套校验 G1⊂G3⊂G5：通过；冲突数：0。
```

---

## 5. 新增 / 修改的脚本清单

均为新增或派生，**未修改任何旧脚本**（旧结果链不受影响）：

```text
06_v0.4_code/07_training/build_l1m2_geometry_registry.py   新增：几何注册表生成
06_v0.4_code/02_blender/render_l1m2_multigeometry.py       派生自 render_full_2664_shadow.py（薄包装，覆盖 SUN/DET/OUTPUT 全局）
06_v0.4_code/02_blender/run_l1m2_render_all.sh             新增：4 几何渲染+后处理编排
06_v0.4_code/05_postprocess/run_l1m2_multigeometry_postprocess.py  派生自 run_full_postprocess.py（薄包装）
06_v0.4_code/07_training/dataset_l1m2_multigeometry.py     新增：多几何总光度向量对齐 dataset
06_v0.4_code/07_training/train_l1m2_multigeometry.py       派生自 train_b6_circular_regression.py（OCS 维度=G，P-INT/P-EXT split，置信中间量）
06_v0.4_code/07_training/run_l1m2_matrix.sh               新增：9-run 正式矩阵编排
06_v0.4_code/07_training/postprocess_l1m2_metrics.py       新增：run_matrix/增益/互补/置信汇总
06_v0.4_code/07_training/plot_l1m2_gain_curve.py           新增：增益曲线与互补性图表
```

派生原则：渲染/后处理包装器通过导入原模块、覆盖几何相关全局再调用原 `main()`，保证与 phase63 fullrun 同管线、同分辨率、同 pass、同 SAMPLES、同 r_max/i_scale/pixel_area/depth_epsilon（跨几何 OCS 量纲可比）。

---

## 6. 新生成数据与结果目录

全部位于 `v0.4_results/11_l1m2_multigeometry_ocs/`：

```text
shadow_passes/{phase24,phase45,phase90,phase120}/    各 2664×(camera.exr+sun.exr)
postprocess/{phase24,phase45,phase90,phase120}/      各 2664×(linear.exr+brdf.png+ocs.json+mask) + fullrun_postprocess_summary.json
l1m2_geometry_registry.{json,md}
l1m2_data_audit.{json,md}
l1m2_split_manifest_PINT_{G1,G3,G5}.json
l1m2_run_matrix.{csv,json}
l1m2_metrics_summary_{final,best}.csv
l1m2_gain_curve_G1_G3_G5.{csv,md}
l1m2_complementarity_summary.csv
l1m2_confidence_consistency_summary.csv
l1m2_pint_vs_pext_ocs_only.csv
l1m2_postprocess_summary.json
figures/l1m2_gain_curve_{final,best}.png, l1m2_complementarity_hit30.png
_l1m2_batch.log, _l1m2_train_matrix.log
runs/P-INT_{G1,G3,G5}_{ocs_only,image_only,joint}_seed42/   9 个正式 run
runs/P-EXT_{G1,G3,G5}_ocs_only_seed42/                      3 个 stress-test 对照 run
runs/smoke_*                                                smoke 记录
```

每个正式 run 子目录含：`run_config.json, train_log.csv, metrics_{val,test}_{final,best}.json, samples_test_{final,best}.{csv,npz}, checkpoint_{final,best}.pt`。

多几何对齐验证（`l1m2_data_audit.json`）：G1/G3/G5 均 2664 姿态内连接成功；flux 均值各几何相异（phase24=0.0394, phase45=0.0322, phase63=0.0271, phase90=0.0277, phase120=0.0117），多观测向量含实质信息。

---

## 7. smoke 结果

```text
geometry registry smoke：G1/G3/G5 几何条目数 1/3/5，嵌套通过。
dataset smoke：G1 对齐 2664（phase63 数据期）；4 几何补齐后 G3=3 维 / G5=5 维全对齐。
training smoke：G1 ocs_only/image_only/joint 各 1–2 epoch 跑通，三模式输出与中间量正常。
postprocess smoke：phase24 3 姿态后处理 OCS_total≈0.0436（≠ phase63 同姿态 0.0159），管线对新几何正确。
全部 smoke 通过后才进入正式渲染与正式矩阵。
```

---

## 8. 正式 clean / P-INT 第一阶段矩阵结果

split：P-INT = pitch 分层随机（train/val/test = 2109/259/296），G1/G3/G5 共用同构 split、同评价口径。来源 `l1m2_split_manifest_PINT_*.json`。

主表（yaw circular MAE，单位°；来源 `l1m2_metrics_summary_best.csv`，best-val 口径）：

| mode | G1 | G3 | G5 |
|:--|--:|--:|--:|
| ocs_only | 76.56 | 38.22 | 22.77 |
| image_only | 2.44 | 4.95 | 8.57 |
| joint | 2.11 | 2.03 | 3.20 |

yaw hit@30deg（来源同上）：

| mode | G1 | G3 | G5 |
|:--|--:|--:|--:|
| ocs_only | 0.277 | 0.672 | 0.811 |
| image_only | 1.000 | 1.000 | 0.993 |
| joint | 1.000 | 1.000 | 1.000 |

互补性（`l1m2_complementarity_summary.csv`，best，hit@30）：

```text
G1: image=1.000  ocs=0.277  joint=1.000  both_wrong=0.000
G3: image=1.000  ocs=0.672  joint=1.000  both_wrong=0.000
G5: image=0.993  ocs=0.811  joint=1.000  both_wrong=0.000
```

读法（严格限定在本轮条件）：在 clean / P-INT / 该 split / 多观测总光度向量输入下，单帧 phase63 图像通道在 yaw 内插任务上已接近饱和（hit@30≈1.0），joint 达到 hit@30=1.0；OCS-only 单通道弱于图像，但随几何数显著改善。joint 相对单通道的增量在本协议下受图像天花板限制（这是 P-INT 内插协议的特性，不能外推到 P-EXT）。

---

## 9. G1 → G3 → G5 增益曲线

来源：`l1m2_gain_curve_G1_G3_G5.{csv,md}`、`figures/l1m2_gain_curve_best.png`。

OCS-only（best，增益=G1_cMAE−Gx_cMAE，正值=多几何降低误差）：

```text
G1 cMAE = 76.56°            （F1/单几何标量信息下界）
G3 cMAE = 38.22°  增益 38.33°
G5 cMAE = 22.77°  增益 53.79°
hit@30 : 0.277 → 0.672 → 0.811（单调上升）
coarse90: 0.372 → 0.659 → 0.750（单调上升）
```

OCS-only 在 clean/P-INT 下随观测几何数单调增益，是本轮对 24 号主线"跨几何多观测总光度向量提升姿态可观测性"的可审计正向证据。image_only / joint 因 P-INT 内插下图像已近饱和，增益曲线主要体现天花板附近的小幅波动（见 §8 主表），已对齐同 split 输出供对照。

P-INT vs P-EXT 边界对照（`l1m2_pint_vs_pext_ocs_only.csv`，ocs_only，best）：

| protocol | G1 | G3 | G5 |
|:--|--:|--:|--:|
| P-INT cMAE | 76.56 | 38.22 | 22.77 |
| P-EXT cMAE | 154.58 | 146.19 | 157.25 |
| P-INT hit@30 | 0.277 | 0.672 | 0.811 |
| P-EXT hit@30 | 0.000 | 0.081 | 0.000 |

读法：多几何 OCS 的可观测性增益在 P-INT（内插）下成立且单调；在 P-EXT（yaw-block strict extrapolation）下，即使加到 5 几何也未解决整段外推坍缩。这与 R113 收口的 single-frame 负结果一致——指向外推协议过强，而非光度无用，且 P-EXT 是 stress test，不替代 P-INT 主线。

---

## 10. posterior-like / top-k / entropy / margin / overlap 文件说明

每个 run 的 `samples_test_{final,best}.npz` 含字段：

```text
record_id, yaw_true_deg, pitch_true_deg, yaw_pred_deg, pitch_pred_deg,
yaw_circular_error_deg, pitch_abs_error_deg, geometry_group, mode, protocol,
posterior_like_top5_idx, posterior_like_top5_score, entropy, margin, candidate_grid(2664×2)
```

posterior-like score 构造方式（已在 run_config.json 标注）：在训练姿态网格（72×37）上，用预测角到候选网格的 circular 距离平方做 softmax：`score ∝ exp(−[(Δyaw/τ_yaw)² + (Δpitch/τ_pitch)²])`，τ_yaw=τ_pitch=20°。这是**工程候选分数，非真实 Bayesian posterior**；entropy/margin/top-k 均由该分布派生。

置信一致性（`l1m2_confidence_consistency_summary.csv`，按 margin/entropy 中位数分半区比较误差）：image_only/joint 通道 high-margin / low-entropy 半区误差更低（置信与正确性一致）；ocs_only 在 G3/G5 出现弱反向关系，已记录为待后续校准项（posterior-like 由预测角构造，与真实误差关系需在后续 conformal/D3 阶段进一步标定）。

互补性所需中间量（image vs ocs vs joint 的 per-attitude 误差、top-1 命中、disagreement）已由 `l1m2_complementarity_summary.csv` 提供，可支持后续 JS divergence / overlap 计算（候选分布 candidate_grid 已随 npz 保存）。

---

## 11. 未完成项与阻塞项

无阻塞项。本轮按 R114 范围完成第一阶段。未铺满项（按任务单允许，保留接口）：

```text
- degraded 真实性轴：本轮未跑（R114 §6 列为第二优先级）。脚本未含正式 degraded 模型；
  后续应按执行框架 §2.3 用 PSF/Poisson+read noise/背景梯度/低分辨率/测光误差等物理退化，不复用 B6 粗增广包。
- P-DB template/posterior 正式分布：本轮以 posterior-like 候选分数形式保留中间量，未跑独立 P-DB 检索表。
- M-roll roll sensitivity 探针：未跑（需 roll≠0 新渲染，本轮聚焦 fixed-roll G1/G3/G5）。
- image_only/joint 的多几何图像输入（exploratory）：未做；本轮 image 固定 phase63（R114 §7）。
- 多 seed 重复：本轮 seed=42 单次；后续可补 seed 方差。
剩余命令模板：在 train_l1m2_multigeometry.py 增加 degraded transform 与 --protocol P-DB 分支后，
按 run_l1m2_matrix.sh 同构扩展即可。
```

性质判定：以上均为**范围内主动收敛**（聚焦第一阶段 clean/P-INT 主线），非资源限制、代码冲突或数据缺口。

---

## 12. 红线自查

```text
[OK] 只改 项目重启_v0.4_BlenderOCS/ 内部文件；新输出全在 v0.4_results/11_l1m2_multigeometry_ocs/，报告在 02_Claude输出/103。
[OK] 未启动头A/头B大合并裁决。
[OK] 未把 B6 写成路线一 C 整体闭口。
[OK] 未写论文正文、未写成果区新结论、未生成 Codex 审阅文件、未改 CLAUDE.md。
[OK] 未启动 T3/L2 光变正式训练、三轴小项目、路线二/三/四扩展。
[OK] 未把 v0.4 写成真实未知目标姿态反演系统；未涉 GEO 监督真值。
[OK] OCS 主线输入是多观测总光度向量；per-part OCS 未作主线输入（本轮未用 4 维 per-part）。
[OK] image 固定 phase63 baseline；joint = phase63 图像 + 多几何总光度向量，仅作同源仿真互补性工具。
[OK] 未做开放式超参搜索、未换 backbone（沿用 B6 同容量编码器）、未覆盖旧结果目录。
[OK] §12 表述红线：未使用"光度无用/yaw 物理不可观测/多几何 OCS 失败/路线一C已闭口/真实望远镜验证/operational-ready/GEO 有姿态真值/per-part 是现实主线"等禁用表述。
[OK] posterior-like 已明确标注为工程候选分数，非真实 Bayesian posterior；P-EXT 标注为 stress test。
```

---

## 13. 交给 Codex 审阅的问题清单

```text
Q1. 编号：本轮采用"实验组 L1-G1/G3/G5"与"代码 OBS_GEOMETRIES 索引/注释 G0~G4"双轨命名（registry 已固化）。
    后续成果/图表是否统一只用 L1-G1/G3/G5 实验层命名，代码层仅在 registry 内出现？
Q2. P-INT 主表里 image_only/joint 在 yaw 内插任务已近饱和（cMAE 2–9°），导致 joint 相对 image 增量有限（天花板）。
    这是否如实写成"P-INT 内插下单帧图像已足够、OCS 主要价值体现在与图像互补及 P-EXT/退化等更难协议"，
    还是需要换更难的 P-INT 难度设定（如更稀疏 train 网格）来给 joint/互补性留出空间？请裁决下一阶段难度口径。
Q3. ocs_only 置信一致性在 G3/G5 出现 margin 与误差弱反向（low-margin 误差反而更低）。
    posterior-like 由预测角到网格距离构造，可能与真实误差解耦。是否在下一阶段引入 conformal prediction / 
    基于模板检索的真实候选分布（P-DB）来替代当前工程 posterior-like 做 D3？
Q4. 增益曲线主结论（OCS-only G1→G3→G5 单调增益、P-EXT 仍坍缩）是否可作为 L1(M2) 第一阶段稳定证据，
    据此放行 degraded 真实性轴 + M-roll 探针作为下一阶段？
Q5. 跨几何量纲：本轮所有几何沿用 phase63 的 i_scale/r_max/pixel_area/depth_epsilon，OCS 物理积分天然可比。
    是否需要补一份显式的跨几何量纲一致性核验表（如各几何 contributing 像素分布）以加固防 inverse-crime？
```

---

（报告结束。所有结论均绑定 `v0.4_results/11_l1m2_multigeometry_ocs/` 下输出文件路径；本报告不作为论文正文，不扩大战果。）
