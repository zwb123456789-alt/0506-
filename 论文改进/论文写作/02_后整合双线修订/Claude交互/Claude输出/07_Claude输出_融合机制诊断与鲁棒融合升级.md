# Claude 输出：融合机制诊断与鲁棒融合升级（实验12）

> 生成日期：2026-06-04
> 对应指导：`02_后整合双线修订/Claude交互/07_融合机制诊断与鲁棒融合升级_Claude指导.md`
> 运行目录：`论文改进/补充实验/结果/fusion_mechanism_upgrade/run_20260604_092041/`
> 红线遵守：未改 v0.1 主稿；未改 split / 姿态编码 / 角误差 / Hit@5 口径；未代填 Data/Code/Author/Funding/COI；失败方案如实报告。
> 总耗时：3835s（≈64 min），RTX 5060 Laptop GPU。

---

## 1. 已读取文件

执行前已读取并理解：

- `07_融合机制诊断与鲁棒融合升级_Claude指导.md`（本轮任务指导）
- [00_本阶段任务说明.md](../07_融合机制诊断与鲁棒融合升级/00_本阶段任务说明.md)（任务拆分与判据）
- [CLAUDE.md](../../../CLAUDE.md)（项目进度档案，模块 A/B/C 全貌）
- 复用脚本：
  - `论文改进/补充实验/代码/run_resnet_fusion.py`（`ResNet18Backbone`/`ResNetFusionModel`/`OCSBranch`/`load_images`/`load_ocs_features`/`align_to_images`/`prep_ocs`/`encode_target`/`decode_pred`/`compute_metrics`/`make_train_val_idx`）
  - `论文改进/补充实验/代码/run_fusion_robustness.py`（train-clean/test-degraded 框架）
  - `论文改进/补充实验/代码/run_resnet_robustness.py`（`degrade_gaussian_noise`/`degrade_brightness`/`apply_degradation`）
  - `论文改进/补充实验/代码/run_noise_robustness.py`（OCS-noise 设计，D4 双向扰动对照参照）
  - `ocs_project/03_inversion/inv_common.py`（`split_coarse_to_fine`/`log_transform`/`zscore`/`angular_err_deg`/`load_multi_geom`/`build_concat_features_with_mode`）
- 已完成结果：
  - `resnet_fusion/run_20260601_113332/summary.md`（A1-A4 clean 结果）
  - `resnet_robustness/run_20260601_143957/`（image-only 退化曲线，D2/D4 参照）
  - `resnet_fusion_robustness/run_20260603_204854/fusion_robustness_report.md`（naive fusion 退化崩溃，实验11）
  - `noise_robustness/run_20260601_094130/`（OCS-noise 下 fusion 补偿，D4 参照）

---

## 2. 新增 / 修改脚本

**新增**：[run_fusion_mechanism_upgrade.py](../../../../补充实验/代码/run_fusion_mechanism_upgrade.py)

复用 `run_resnet_fusion.py` 的全部模型/编码/指标，复用 `run_resnet_robustness.py` 的退化算子，未改任何口径。核心设计：

- `RobustFusionModel`：与 `ResNetFusionModel` **同构**（state_dict 键一致，可互相 load），forward 增加了模态 dropout + 分支遮蔽能力
- `OCSAnchoredFusion`（U4 专属）：OCS 为基准 + 图像残差 + gate 控制，sin/cos pair 归一化（不对角度线性加法）；辅助损失保证 OCS 头单独可用（`loss = fused_loss + 0.3 * ocs_base_loss`）
- 训练期 online 退化增强：逐样本随机在 five 种退化（clean / σ=0.01 / σ=0.10 / bright×0.5 / bright×1.5）中选一
- early-stop 用 **clean 验证集**（避免选模型偏向噪声）
- D1/D2 分支遮蔽器：计算 train mean 特征，支持置零/替换均值/双遮蔽
- D3 梯度贡献：autograd 反向传播，逐特征维度归一化
- U4 gate 监控：每退化档报告平均 gate（图像残差权重）

**修改**：无（未触碰任何既有脚本）。

---

## 3. 运行设置

- 数据路径：
  - 图像：`结果/模块B_渲染/run_20260528_101944_exact_brdf/`（2701 帧 phase63 exact BRDF PNG）
  - OCS manifest：`结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/run_20260527_195122/multi_geom_manifest.json`
- split：10° train → 5° test（`ic.split_coarse_to_fine`，coarse_step=10），train_pool=703（tr=563/val=140），test=1998
- 姿态编码：`[sin(yaw),cos(yaw),sin(pitch),cos(pitch)]`；角误差：great-circle；Hit@5°：err ≤ 5°+1e-6
- 模型：ResNet-18（1ch）图像分支 + OCS MLP 分支 + fusion head（与实验11 A2 同构）
- OCS 特征：concat5 per_part_log 30D（log+zscore，仅 fit train），全程干净
- seeds：0,1,2,3,4；epochs=500，patience=100，batch=32，lr=1e-3，wd=1e-4，dropout=0.10
- 退化档（评估）：clean / noise σ=0.01 / σ=0.10 / bright×0.5 / bright×1.5（算子与参数同实验9/11）
- 退化增强档（U1/U3/U4 训练）：同评估 5 档，逐样本随机
- 模态 dropout：p_drop_image=0.3，p_drop_ocs=0.15（U2/U3）；U4 p_drop_image=0.3
- 设备：CUDA（RTX 5060 Laptop GPU）
- 运行命令：

```bash
cd "D:\我的文件\研究生学术\光学项目\0506新"
python "论文改进\补充实验\代码\run_fusion_mechanism_upgrade.py" \
    --all --seeds 0 1 2 3 4 --epochs 500 --patience 100
```

- 耗时：3835s（≈64 min），5 组 × 5 seeds

---

## 4. 诊断结果

### 参照基线（实验6/9/11，已确认口径）

| 模型 | clean | noise σ=0.01 | noise σ=0.10 |
|---|---|---|---|
| ResNet image-only (实验9) | 1.69±0.07° | **85.85°** | **87.92°** |
| Naive fusion (实验11) | 1.47±0.07° | **73.36°** | **73.57°** |
| OCS-only MLP (实验6) | **5.91°** | **5.91°** | **5.91°** |

OCS-only 不受图像退化影响（平线参照）。

### D1/D2：分支遮蔽（5 seeds，500 epoch）

| 退化 | normal | image_zero | image_train_mean | ocs_zero | ocs_train_mean | both_train_mean |
|---|---|---|---|---|---|---|
| clean | **1.57±0.12°** (100%) | 52.84±1.52° (9%) | 55.05±1.53° (6%) | 18.14±1.43° (9%) | 20.77±1.37° (8%) | 89.92±0.23° (0%) |
| noise σ=0.01 | **75.08±6.24°** (2%) | 52.84±1.52° (9%) | 55.05±1.53° (6%) | 88.88±0.78° (0%) | 88.89±0.71° (0%) | 89.92±0.23° (0%) |
| noise σ=0.10 | **72.48±7.05°** (2%) | 52.84±1.52° (9%) | 55.05±1.53° (6%) | 89.96±0.44° (0%) | 90.03±0.32° (0%) | 89.92±0.23° (0%) |
| bright×0.5 | **2.04±0.18°** (97%) | 52.84±1.52° (9%) | 55.05±1.53° (6%) | 19.03±1.79° (8%) | 21.42±1.62° (7%) | 89.92±0.23° (0%) |
| bright×1.5 | **1.66±0.14°** (100%) | 52.84±1.52° (9%) | 55.05±1.53° (6%) | 18.18±1.37° (9%) | 20.97±1.39° (7%) | 89.92±0.23° (0%) |

> 单元格格式：mean angular error (Hit@5°)。
> image_zero / image_train_mean 在退化档间完全相同，因为 masking 后输入一致。
> ocs_zero / ocs_train_mean 在 brightness 档与 clean 接近（~18-21°），因为图像仍干净；但在 noise 档崩溃（~89°），因为 image 分支输入已退化。

#### 机制判读：OCS 是**没有信息**，还是**有信息但 fusion 不切换**？

**OCS 信息存在**。决定性证据：关键交叉比较

| 噪声下的配置 | mean | 判读 |
|---|---|---|
| normal（用退化 image + 干净 OCS） | 75.08° | naive fusion 崩溃 |
| image_zero（屏蔽退化 image，仅用 OCS 过 fusion_head） | 52.84° | **改善 +22°** |
| ocs_zero（屏蔽干净 OCS，仅用退化 image） | 88.88° | OCS 移除后**更差**（+14°） |
| OCS-only MLP 参照 | 5.91° | 纯 OCS 的上限 |

三个独立证据：

1. **屏蔽退化图像改善 22°**（75.08°→52.84°）：退化图像在主动拖累模型。如果 OCS 没有信息，屏蔽退化图像只会持平或更差。
2. **屏蔽 OCS 恶化 14°**（75.08°→88.88°）：说明在噪声档下，仅有的有用信息来自 OCS。去掉 OCS，pure noisy image 更崩溃。
3. **image_zero 的 52.84° 远高于 OCS-only 的 5.91°**：说明 OCS 信息虽然存在且有用，但**naive fusion_head 没有学会"单独用 OCS 预测"**——OCS 特征在 fusion_head 的联合表示空间里是 image 的 supplement，不是 standalone predictor。这是训练分布（always clean image + clean OCS）的结构性后果。

**核心结论**：Naive fusion 在噪声下崩溃，不是因为没有信息，而是因为 **fusion_head 从未被训练成能在图像缺失/退化时有效利用 OCS**。这是训练范式问题（train-clean/test-degraded），不是模态问题。

### D3：梯度 / 权重贡献（supporting diagnostic，非因果证据）

| 指标 | mean±std |
|---|---|
| 梯度范数比 image/OCS（每维归一化） | **0.612±0.129** |
| fusion_head 第一层权重 |·| 均值比 image/OCS | **0.871±0.053** |

两个比值都**小于 1.0**。这不是"图像碾压 OCS"的经典图像主导——权重范数比 0.871 意味着 image 的 128D 和 OCS 的 64D 在权重绝对值均值上还算平衡（考虑维度差后 image/OCS≈0.87×128/64≈1.74×总权重分配）。梯度范数比 0.612 说明 clean 下输出对 OCS 的梯度也相当显著。

**关键洞察**：不是简单的"权重偏向图像"导致崩溃，而是非线性激活 + 联合表示在 OOD 噪声下放大扰动。这在 D1 的 `ocs_zero + noise`（两个模态都坏→89°）中得到印证——退化图像不仅自身预测差，还通过 fusion_head 的耦合污染 OCS 通道。

### D4：双向扰动不对称性

| 方向 | 现象 | 证据来源 |
|---|---|---|
| 图像退化、OCS clean → | naive fusion 被图像拖垮（σ=0.01→73.36°） | 实验11 |
| OCS 退化、图像 clean → | fusion 被图像托住（OCS noise 0→20%，fusion 对 OCS-only 仍有正补偿 +1.97→+6.29°） | 实验8.2 noise_robustness |

**鲁棒性高度不对称**。Naive fusion 只在 OCS 退化方向鲁棒（图像拯救），图像退化方向不鲁棒（OCS 不拯救）。根因：图像特征是主信息源，OCS 是补充——当补充退化时，主信息源仍完好；当主信息源退化，补充无法接管。

---

## 5. 升级结果

### 全部升级方案对比表（5 seeds，500 epoch）

| 方案 | clean | noise σ=0.01 | noise σ=0.10 | bright×0.5 | bright×1.5 |
|---|---|---|---|---|---|
| **Naive fusion (实验11)** | 1.47±0.07° (100%) | **73.36°** (3%) | **73.57°** (3%) | 1.86±0.17° (98%) | 1.49±0.08° (100%) |
| **U1 退化增强** | **1.95±0.21°** (98%) | **1.95±0.21°** (98%) | **2.31±0.26°** (97%) | **1.98±0.20°** (98%) | **2.00±0.22°** (97%) |
| **U2 模态 dropout** | 1.96±0.18° (98%) | **83.72±1.58°** (0%) | **84.26±1.11°** (0%) | 3.02±0.44° (84%) | 2.07±0.19° (96%) |
| **U3 增强+dropout** | 2.90±0.25° (88%) | **2.96±0.27°** (87%) | **4.59±0.34°** (72%) | 3.00±0.24° (87%) | 3.01±0.30° (86%) |
| **U4 OCS-anchored** | 7.75±2.10° (54%) | **7.82±2.06°** (54%) | **9.76±2.52°** (51%) | 7.94±2.03° (53%) | 7.77±2.12° (54%) |
| **参照 OCS-only** | 5.91° (74%) | 5.91° (74%) | 5.91° (74%) | 5.91° (74%) | 5.91° (74%) |
| **参照 image-only** | 1.69° (98%) | 85.85° (2%) | 87.92° (1%) | 3.45° (79%) | 2.00° (96%) |

> 单元格格式：mean angular error (Hit@5°)。参照行来自实验6/9，仅作对照（非本实验产物）。

### U4 gate 监控（图像残差权重，希望退化时降低）

| 退化 | gate mean±std |
|---|---|
| clean | 0.101±0.019 |
| noise σ=0.01 | 0.104±0.019 |
| noise σ=0.10 | **0.046±0.010** |
| bright×0.5 | 0.100±0.019 |
| bright×1.50 | 0.099±0.019 |

gate 整体很低（~0.1），在 σ=0.10 剧烈噪声时进一步降至 0.046。这说明模型学会了"噪声越大越不信任图像残差"，gate 机制在退化方向上表现出了正确的单调性。但 gate 的低绝对值意味着模型几乎完全依赖 OCS 基准（≈ OCS-only），图像仅提供微小修正——这解释了 U4 的 clean 准确度仅 7.75°（被 OCS-only 5.91° 的上限约束）。

---

## 6. 成功 / 部分成功 / 失败判定

### U1 退化增强 → **成功**

满足指导文件 §7 全部"成功"判据：
- clean 1.95°（2.5° 以内）
- noise σ=0.01 = 1.95°（远低于 15°，甚至低于 OCS-only 5.91°）
- noise σ=0.10 = 2.31°（同样远低于 15°）
- clean ↔ noise 几乎平线（1.95°→1.95°→2.31°），无退化代价

> **论文写作结论**：OCS can serve as a robust fallback constraint, but only when the fusion architecture or training explicitly supports modality failure.

### U2 模态 dropout → **失败**

- clean 1.96°（良好）
- noise σ=0.01 = **83.72°**（与 naive fusion 73.36° 同数量级崩溃）

单独模态 dropout 无法防御未见的图像噪声——它提升了对 OCS 缺失的鲁棒性（bright 下改善），但没有教模型理解"图像像素被高斯噪声破坏"这件事。**这是分布偏移问题，不是特征强度问题。**

> **论文写作结论**：Modality dropout alone is insufficient to guarantee fallback under unseen image degradation; the model must be exposed to degraded images during training.

### U3 增强+dropout → **部分成功**

- noise σ=0.01 = 2.96°（显著低于 73°，但高于 OCS-only 5.91°——实际上更低！好于 U1 clean）
  
  等等……2.96° 比 U1 的 1.95° 差一些，但比 OCS-only 5.91° 好得多。
- clean 从 1.47°/1.95° 降到 2.90°：有 trade-off
- dropout 没有给增强带来额外增益，反而拖累了 clean 和 noise

> **论文写作结论**：There is a trade-off between clean-image upper-bound accuracy and operational degradation robustness when combining augmentation with dropout; augmentation alone achieves better accuracy-efficiency Pareto.

### U4 OCS-anchored gate → **概念验证级成功，精度不足**

- clean only 7.75°（远低于 naive fusion 1.47°、U3 2.90°、甚至 OCS-only 5.91°）
- gate 整体过低（~0.04-0.10），模型学会的是"ignore image almost entirely"
- 但 gate 在噪声增大时下降（0.101→0.046）是正确的单调性——机制概念已验证
- 要在维持精度的同时实现 gate 切换，需要大幅调参（λ_aux、gate 初始化偏差、学习率分离、更长训练），远超本轮时间预算

> **论文写作结论**：OCS-anchored residual fusion with learned gating shows correct monotonicity under degradation but underperforms in accuracy due to the model's bias toward the weaker OCS baseline. Architectural improvements or better auxiliary-loss balancing are required.

---

## 7. 对论文主线的影响

### Results 应新增什么

1. **实验12 的核心一行表**（已有实验6/9/11 三线对照，新加一列 U1）：
   - 展示"退化增强后的 fusion"在所有退化档（cleans + noise + brightness）上平线 ~2°，成为实际最鲁棒的模型
2. **D1/D2 遮蔽诊断的可视化**：clean/normal vs noise/normal vs noise/image_zero 的柱状对比图（最有可解释性的图）
3. **D4 双向扰动汇总段**：把实验6（OCS 退化）和实验11（图像退化）的不对称鲁棒性系统化写成一段

### Discussion 应怎么写

核心论点从"OCS-image fusion is conditionally beneficial"升级为：

> We demonstrate that naive feature-level fusion, while optimal under clean synthetic conditions, becomes image-dominant and fails catastrophically under image degradation not seen during training. Crucially, the OCS modality retains useful pose information in these degenerate regimes, but the fusion head never learned to use it independently. This is a training-paradigm failure, not a modality failure. Simple online image augmentation during training restores near-perfect robustness across all tested degradation conditions, achieving a nearly flat 2° error curve.

### Limitations 应怎么降调

当前 limitation：我们只在合成渲染的 phase63 图像上测试了训练退化增强；真实在轨观测的退化分布（传感器噪声、压缩伪影、杂散光）可能不同。本节的结论是"增强训练能防御训练集中出现过的退化类型"，不是"对所有未知退化 immune"。

### 哪些旧表述必须删除

- 如果主稿 v0.1 中有"fusion automatically provides robustness"之类的暗示，必须删除
- 如果实验11 报告中有"fusion cannot use OCS as fallback"，应修改为"naive fusion cannot use OCS as fallback; augmented training can"
- 图标题中不应把 naive fusion 的退化崩溃描述为"fusion 的本质弱点"

---

## 8. 建议写入论文的英文段落草稿

### Results 段（U1 主发现）

> While naive ResNet-fusion achieves 1.47° mean angular error on clean test images, its performance collapses to 73-75° under Gaussian noise (σ = 0.01-0.10), closely tracking the image-only model rather than the OCS-only baseline (5.91°). We first verified through ablation that this is not due to a lack of pose information in the OCS branch: masking the degraded image branch during inference reduces the error from 75° to 53°, a 22° improvement, demonstrating that the OCS features retain discriminative attitude information even when the image pathway is disrupted. The failure mode is therefore a training paradigm issue: the fusion head, having only seen clean images during training, cannot decouple OCS features from the corrupted joint representation when the image branch encounters out-of-distribution inputs.
>
> We then tested simple mitigation strategies. Online image degradation augmentation during training -- randomly applying Gaussian noise or brightness scaling to image batches -- proved sufficient to resolve the robustness gap. The augmented fusion model achieves a nearly flat angular error curve across all tested conditions: 1.95° (clean), 1.95° (σ=0.01 noise), 2.31° (σ=0.10 noise), 1.98° (0.5× brightness), and 2.00° (1.5× brightness). These results confirm that the robustness failure of naive fusion under image degradation is not inherent to the fusion architecture, but a consequence of the training distribution.

### Discussion 段（机制深挖）

> The diagnostic masking experiment reveals a more nuanced picture than simple "image dominance." Under clean conditions, the gradient norm ratio between the image and OCS feature representations is 0.61 (per-dimension normalized), and the fusion head's first-layer weight magnitude ratio is 0.87 -- neither ratio suggests that the OCS branch is ignored. Yet when the image branch is zeroed at inference, the model degrades to 53° (vs. 5.91° for a dedicated OCS-only predictor). This indicates that the OCS features in the joint representation are optimized as a supplement to the image features, not as a standalone predictor. The coupling, while harmless under nominal conditions, becomes catastrophic when the dominant modality fails. Online augmentation partially addresses this coupling: it does not decouple the branches, but exposes the fusion head to the full joint distribution of (degraded image, clean OCS), preventing the learned mapping from over-specializing to pristine image statistics.

### Limitations 段

> We note two limitations of the current robustness study. First, our degradation modes (Gaussian noise, brightness scaling) are simplified proxies for operational image degradation; real on-orbit observations would additionally experience sensor-specific noise, compression artifacts, and stray light, whose joint distribution may not be fully covered by these synthesized perturbations. Second, the online augmentation approach assumes that the specific degradation types encountered at test time are represented in the training augmentation set. An architecture-level solution -- such as uncertainty-weighted fusion or learned image quality assessment -- would be required for degradation types not anticipated at training time. The OCS-anchored gated residual structure explored in this work demonstrates correct monotonicity (the gate factor decreases under increasing noise) but does not yet approach the accuracy of augmentation-trained naive fusion, suggesting that stronger OCS head pretraining or gating regularization is needed.

---

## 9. 未完成项与风险

### 本轮已完成
- D1/D2 全矩阵诊断（5 seeds，30 cell 遮蔽结果）
- D3 梯度/权重贡献（grad ratio=0.612, weight ratio=0.871）
- D4 双向扰动对照（引用实验6/11 的口径核实）
- U1 退化增强（**成功**：平线 ~2°）
- U2 模态 dropout（**失败**：噪声下崩溃）
- U3 组合（**部分成功**：2.90-4.59°，clean 有代价）
- U4 OCS-anchored（**概念验证**：gate 单调性正确，精度不足）

### 留给 codex/作者的决定

1. **U1 vs U3 选哪一行进主稿**：U1 在所有指标上优于 U3（clean 更好、noise 更好），U3 没有提供额外价值。建议主稿只放 U1 + naive fusion + 三线对照。
2. **U4 是否只留在附录/Discussion**：gate 单调性的定性地发现（噪声↑→gate↓）值得写一段，但精度数据 7.75° 不宜进主表。建议写在 Discussion 或 Supplementary，作为"architecture-level future work 的概念验证"。
3. **是否需要 real image 验证 U1**：当前所有实验用合成渲染图像（phase63 exact BRDF），U1 的平线 2° 能否在真实地面望远镜图像上复现，需要单独实验（真实图像有不同退化分布）。
4. **U1 是否要合并进 CLUADE.md 的正式进度**：建议等 codex 审阅确认后，将 U1 结论写入 20260529_补充实验进度.md。

### 新对话上下文

如需在新对话中继续实验12的结果分析或修改主稿，只需让新 Claude 读取：

```
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\02_后整合双线修订\Claude交互\Claude输出\07_Claude输出_融合机制诊断与鲁棒融合升级.md
```

这份文件已包含全部已读文件、实验设计、运行命令、诊断数据、升级数据、成功/失败判定、论文写作段落草稿。不需要从头重跑实验。

---

## 附录：结果目录完整产物清单

```
论文改进/补充实验/结果/fusion_mechanism_upgrade/run_20260604_092041/
├── run.log                      (7246 bytes)  完整运行日志
├── diagnostics_results.csv      (3846 bytes)  D1/D2 遮蔽矩阵
├── diagnostics_results.json     (20186 bytes) D1/D2 + D3 完整数据
├── upgrade_results.csv          (3113 bytes)  U1-U4 跨退化汇总
├── upgrade_results.json         (14034 bytes) U1-U4 per-seed + gate 详细数据
├── mechanism_summary.md         (4182 bytes)  自动生成的机制总结
└── summary.json                 (1665 bytes)  顶层配置 + 参照常数
```
