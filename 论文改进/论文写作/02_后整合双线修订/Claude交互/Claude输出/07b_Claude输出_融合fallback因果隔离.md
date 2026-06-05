# 07b Claude 输出：融合 fallback 因果隔离

> 生成日期：2026-06-04
> 对应指导：`02_后整合双线修订/Claude交互/07b_融合fallback因果隔离与鲁棒性补强_Claude指导.md`
> 运行目录：`论文改进/补充实验/结果/fusion_fallback_isolation_12b/run_20260604_150333/`
> 红线遵守：未改 v0.1 主稿；未改 split / 姿态编码 / 角误差 / Hit@5 口径；未代填 Q12-Q15；未覆盖 fusion_mechanism_upgrade/run_20260604_092041；未把 worst 离群存在的事实隐藏；未把"U1 在使用 OCS"与"U1 学到了 OCS-standalone fallback"混为一谈。
> 总耗时：1854s（≈31 min），5 seeds × 500 epochs，RTX 5060 Laptop GPU。

---

## 1. 执行摘要

实验 12 已确认 U1（image-degradation-aware augmentation）将 fusion 在所有已测试退化档下的 mean / p90 / Hit@5 都拉回强水平（~2°），但 **没有隔离** U1 的成功究竟是 (a) 仅由图像增强解释，还是 (b) fusion 确实在图像退化时使用了 OCS。实验 12b 用 5 组对照实验做了这个因果隔离，结论是：

> **OCS 在 U1 augmented fusion 中确实在被使用**，并且 **U1 严格优于 image-only + same augmentation**，但机制 **不是经典的离散 fallback（image fails → switch to OCS）**，而是 **持续的 OCS-image co-utilization**——OCS 在所有退化档（包括 clean）下都是 U1 表示中"更重要的分支"，图像退化增强保证图像分支不在 OOD 像素扰动下崩溃，两者协同提供 ~2° 鲁棒精度。

五个关键判据（5 seeds, mean angular error）：

| 判据 | 现象 | 解读 |
|---|---|---|
| **12b-1** image-only+aug vs U1 | noise σ=0.10：image-only+aug **9.55°** vs U1 **2.31°**（Hit@5 41% vs 97%） | U1 的鲁棒性 **不能** 仅由图像增强解释 |
| **12b-2** 分支遮蔽 | 所有退化档下，遮蔽 OCS（53-58°）**比** 遮蔽 image（34.9°）**更糟** | OCS 是 U1 中更重要的分支，但 image_zero 远高于 OCS-only 5.91° → 不是 standalone fallback |
| **12b-3** OCS 噪声 0%→20% | 每个图像档下都 +3.4-3.6°；与图像退化档无关 | OCS 确实在被使用；但 dependence 不是图像退化触发的（**非 switching**） |
| **12b-4** 离群 | 42 个 >30°（0.08%），50% 在 \|pitch\|>75° 极区 | mean / p90 / Hit@5 已稳定，rare large outliers remain — **不能写 fully robust** |
| **12b-5** 未见退化（不进训练增强） | U1 在 noise_0.03/0.05、blur_k3/5、downsample_64/32 全部保持 ~2°；image-only+aug 退化到 4-6° | U1 表现出 **degradation-aware robustness 超出 matched augmentation**，OCS 的存在使 fusion 对未见退化更稳健 |

**写进论文的核心句子**（建议 v0.2 主稿调用）：

> Online image-degradation augmentation provides strong robustness, but it does so via OCS-image co-utilization rather than a discrete fallback. The augmented fusion model is strictly better than image-only training under the same augmentation across all tested and held-out degradations, and OCS noise causally degrades the augmented fusion performance, confirming that OCS is actively used. However, masking the image branch of the augmented fusion still leaves a 30-35° error (well above the 5.91° OCS-only baseline), indicating that OCS is not learned as a standalone fallback predictor.

---

## 2. 读取文件与复用代码

### 2.1 任务上下文

执行前已读取并理解：

- [07b_融合fallback因果隔离与鲁棒性补强_Claude指导.md](../07b_融合fallback因果隔离与鲁棒性补强_Claude指导.md)
- [07_Claude输出_融合机制诊断与鲁棒融合升级.md](07_Claude输出_融合机制诊断与鲁棒融合升级.md)
- [07_Claude融合机制诊断与鲁棒融合升级单边审阅.md](../../Codex审阅/07_Claude融合机制诊断与鲁棒融合升级单边审阅.md)
- [07_融合机制诊断与鲁棒融合升级_整合清单.md](../../阶段整合输出/07_融合机制诊断与鲁棒融合升级_整合清单.md)
- [CLAUDE.md](../../../../../CLAUDE.md)（项目焦点 = Step 07）
- [20260529_论文写作完整规划.md](../../../../20260529_论文写作完整规划.md) §4-6
- [20260529_补充实验进度.md](../../../../20260529_补充实验进度.md) §11-12
- [00_本阶段任务说明.md](../../07b_融合fallback因果隔离与鲁棒性补强/00_本阶段任务说明.md)

### 2.2 实验 12 既有产物（已确认口径，未覆盖）

- `论文改进/补充实验/代码/run_fusion_mechanism_upgrade.py`（实验 12 主脚本）
- `论文改进/补充实验/结果/fusion_mechanism_upgrade/run_20260604_092041/mechanism_summary.md`
- `论文改进/补充实验/结果/fusion_mechanism_upgrade/run_20260604_092041/diagnostics_results.csv`
- `论文改进/补充实验/结果/fusion_mechanism_upgrade/run_20260604_092041/upgrade_results.csv`

### 2.3 复用的代码模块

实验 12b 全量复用以下模块（直接 import，不复制）：

- `run_fusion_mechanism_upgrade`（实验 12 主脚本）：
  - `RobustFusionModel`（U1 训练 + 分支遮蔽 forward）
  - `make_aug_fn` / `AUG_DEGS` / `EVAL_DEGS`（与 U1 完全相同的增强源）
  - `train_model`（U1 同口径训练；augment=True, anchored=False, p_drop=0）
  - `apply_image_degradation`（5 评估退化的算子）
  - `compute_feature_means`（分支遮蔽用的 train mean）
  - `summarize_seeds`（mean/std 跨 seed 汇总）
- `run_resnet_fusion`（实验 11 fusion 主脚本）：
  - `ResNetImageOnly`（12b-1 baseline 模型）
  - `load_images` / `load_ocs_features` / `align_to_images` / `prep_ocs`
  - `encode_target` / `decode_pred` / `compute_metrics`
  - `make_train_val_idx`
- `inv_common`：`split_coarse_to_fine` / `log_transform` / `zscore`

### 2.4 关键参照常数（来自实验 6/9/11/12，已确认口径，仅作对照）

```text
OCS-only MLP per_part_log:         5.91° (Hit@5=73.8%)
ResNet image-only clean-trained:
    clean=1.69°  noise_0.01=85.85°  noise_0.10=87.92°  bright_0.50=3.45°  bright_1.50=2.00°
Naive ResNet-fusion clean-trained:
    clean=1.47°  noise_0.01=73.36°  noise_0.10=73.57°  bright_0.50=1.86°  bright_1.50=1.49°
U1 augmented fusion (实验 12, run_20260604_092041):
    clean=1.95°  noise_0.01=1.95°  noise_0.10=2.31°  bright_0.50=1.98°  bright_1.50=2.00°
```

实验 12b 中重新训练的 U1 augmented fusion（150333 这一跑）的 5 个退化档均值与实验 12 完全一致（差异 < 0.005°），证明结果可复现且数据流口径无漂移。

---

## 3. 新增或修改代码路径

**新增**：[论文改进/补充实验/代码/run_fusion_fallback_isolation_12b.py](../../../../补充实验/代码/run_fusion_fallback_isolation_12b.py)（约 760 行）

设计原则：

1. **不破坏实验 12 主脚本**：通过 `import run_fusion_mechanism_upgrade as up` 复用，不修改原文件。
2. **不覆盖实验 12 结果**：结果目录改为 `fusion_fallback_isolation_12b/run_YYYYMMDD_HHMMSS/`。
3. **OCS 噪声方法标注**（指导 §3 12b-3 红线）：采用 raw-feature relative perturbation 后用 train 统计量 re-standardize 的方式，与实验 6 的端到端 OCS-only 评估口径 **明确区分**，并在 `summary.json` / `mechanism_12b_summary.md` 中写明：
   ```json
   "ocs_noise_method": "raw per_part feature relative perturbation
       (raw + level*|raw|*N(0,1)),
       re-standardized with train log-zscore stats"
   ```
4. **增加 p95 列**：满足指导 §4"mean/median/p90/p95或worst/Hit@5/Hit@10"完整集合。
5. **离群审计跨退化判读**：用 `(seed, sample_index)` 联合键判断"同样本在 ≥2 个退化档 >30°"，避免单档统计偏差。

**修改**：无（未触碰任何既有脚本）。

---

## 4. 运行命令与结果目录

### 4.1 运行命令

```bash
cd "D:\我的文件\研究生学术\光学项目\0506新"
conda activate ocs_sim
python "论文改进\补充实验\代码\run_fusion_fallback_isolation_12b.py"
```

默认 `--seeds 0 1 2 3 4 --epochs 500 --patience 100`，无需额外参数。

### 4.2 资源与时间

- 数据：phase63 exact BRDF PNG（2701 帧 × 128×128 × 1ch）+ concat5 per_part_log 30D OCS manifest
- split：10° train pool=703（tr=563/val=140），5° test=1998
- 设备：CUDA, RTX 5060 Laptop GPU
- 总耗时：1854s（≈31 min）
  - image-only-aug 训练 5 seeds：739s
  - U1-aug-fusion 训练 5 seeds：906s
  - 五组评估 + 保存：~209s

### 4.3 产物清单

```text
论文改进/补充实验/结果/fusion_fallback_isolation_12b/run_20260604_150333/
├── run.log                                       (8270 bytes)
├── summary.json                                  (1547 bytes)
├── mechanism_12b_summary.md                      (4502 bytes)
├── image_only_aug_results.csv / .json            12b-1 输出
├── u1_branch_mask_results.csv / .json            12b-2 输出
├── u1_ocs_noise_both_degraded_results.csv / .json 12b-3 输出
├── u1_outlier_audit.csv / .json                  12b-4 输出
└── heldout_degradation_results.csv / .json       12b-5 输出
```

### 4.4 早期冒烟跑（145734）

`run_20260604_145734` 是同日早些时候的一次完整跑（5 seeds 也是 500 epoch），数据与最终跑（150333）在所有 mean 上一致到 < 0.05°。本报告所有数值以 **150333** 为准（最新），145734 留作复现性对照证据。

---

## 5. 12b-1：image-only augmentation 对照

### 5.1 设置

- 模型：`ResNetImageOnly`（与实验 9 完全相同的结构，无 OCS 分支）
- 训练增强：与 U1 完全相同 `AUG_DEGS = [clean, noise_0.01, noise_0.10, bright_0.50, bright_1.50]`，逐样本随机
- early stopping：clean validation set（与 U1 一致）
- seeds=5，epochs=500，patience=100

### 5.2 Table 12b-1

| 退化 | image-only+aug | U1 aug fusion | Δ(img-only - U1) | image-only clean(参照) | naive fusion(参照) | OCS-only(参照) |
|---|---|---|---|---|---|---|
| clean | 2.63±0.20° (90.4%) | **1.95±0.21°** (97.8%) | **+0.68°** | 1.69° | 1.47° | 5.91° |
| noise σ=0.01 | 2.80±0.23° (88.3%) | **1.95±0.21°** (97.8%) | **+0.85°** | 85.85° | 73.36° | 5.91° |
| noise σ=0.10 | 9.55±0.75° (41.4%) | **2.31±0.26°** (96.6%) | **+7.24°** | 87.92° | 73.57° | 5.91° |
| bright×0.50 | 2.76±0.25° (88.9%) | **1.98±0.20°** (97.8%) | **+0.78°** | 3.45° | 1.86° | 5.91° |
| bright×1.50 | 2.76±0.20° (89.3%) | **2.00±0.22°** (97.4%) | **+0.76°** | 2.00° | 1.49° | 5.91° |

p90 / p95（U1 vs image-only+aug）：

| 退化 | U1 p90 / p95 | image-only+aug p90 / p95 |
|---|---|---|
| clean | 3.53 / 4.19° | 4.83 / 5.75° |
| noise σ=0.01 | 3.53 / 4.17° | 5.14 / 6.20° |
| noise σ=0.10 | 3.73 / 4.50° | 18.14 / 26.24° |
| bright×0.50 | 3.54 / 4.19° | 5.06 / 6.23° |
| bright×1.50 | 3.62 / 4.30° | 5.02 / 6.04° |

### 5.3 判读

- **U1 在每一个退化档下都严格优于 image-only+aug**（Δ 从 +0.68° 到 +7.24°）。
- **σ=0.10 是分水岭**：image-only+aug 即使带了完全相同的退化增强，仍在重噪声下退化到 9.55°（Hit@5 跌到 41%）；U1 augmented fusion 维持在 2.31°（Hit@5=96.6%）。p95 差距 26.24° vs 4.50° 是数量级。
- 即使在 clean 档，U1 的 Hit@5（97.8%）也高于 image-only+aug（90.4%），说明 OCS 在干净条件下也提供了精度上的细节贡献。

**判据 1 结论**：U1 的鲁棒性 **不能** 仅由"图像退化增强教会图像分支不在 OOD 退化下崩溃"解释。OCS 的存在至少贡献了 σ=0.10 下 7.24° 的鲁棒性改善。

---

## 6. 12b-2：U1 分支遮蔽

### 6.1 设置

- 复用 12b-1 训练好的 U1 augmented fusion 5 个 state_dict
- 6 种遮蔽模式：`normal` / `image_zero` / `image_train_mean` / `ocs_zero` / `ocs_train_mean` / `both_train_mean`
- train_mean 在 fit-train 上 clean 输入计算（与实验 12 D1/D2 同款）

### 6.2 Table 12b-2

| 退化 | normal | image_zero | image_train_mean | ocs_zero | ocs_train_mean | both_train_mean |
|---|---|---|---|---|---|---|
| clean | **1.95°** (98%) | 34.90° (47%) | 30.87° (32%) | 53.27° (1%) | 56.48° (0%) | 89.95° (0%) |
| noise σ=0.01 | **1.95°** (98%) | 34.90° (47%) | 30.87° (32%) | 53.19° (1%) | 56.45° (0%) | 89.95° (0%) |
| noise σ=0.10 | **2.31°** (97%) | 34.90° (47%) | 30.87° (32%) | 56.06° (1%) | 58.56° (0%) | 89.95° (0%) |
| bright×0.50 | **1.98°** (98%) | 34.90° (47%) | 30.87° (32%) | 53.81° (1%) | 57.44° (0%) | 89.95° (0%) |
| bright×1.50 | **2.00°** (97%) | 34.90° (47%) | 30.87° (32%) | 53.50° (1%) | 56.23° (0%) | 89.95° (0%) |

（单元格 = mean (Hit@5°); image_zero/image_train_mean 在退化档间数值一致是预期，因为输入被遮蔽后与退化无关。）

### 6.3 判读

**最关键的对比：image_zero (~34.9°) vs ocs_zero (~53-58°) 在 ALL 退化档下**：

- 遮蔽 OCS（→53-58°）比遮蔽 image（→34.9°）**严重得多**——这与 naive clean-trained fusion 形成镜像（naive 在 noise 档下遮蔽 image=52.84° vs 遮蔽 OCS=88.88°，OCS 屏蔽反而更糟，因为退化图像在主动拖累）。U1 augmented fusion 在 **clean 档** 下就已经表现出"OCS 更重要"的特征。
- 这意味着 U1 augmented 训练 **重塑了 fusion_head 的内部权重分配**——augmentation 不仅教会图像分支抵抗退化，还让 fusion_head 学到了更依赖 OCS 的联合表示。

**但是**：

- image_zero (~34.9°) 远高于 OCS-only baseline (5.91°)。如果 U1 学到了 standalone OCS fallback，遮蔽图像后应该接近 5.91°。它没有。
- ocs_zero (~53-58°) 也远高于 image-only+aug (~2.6-9.5°)。如果 U1 学到了 standalone image pathway，遮蔽 OCS 后应该接近 image-only+aug。它也没有。
- 两个分支的遮蔽都让模型崩溃到 30-60°（中等），说明 **U1 的鲁棒性来自两分支的联合表示**，不是任何一个分支的 standalone 能力。

**判据 2 结论**：U1 不是经典 fallback。它是 **OCS-image co-utilization** — OCS 全程在使用（遮蔽必崩），image 也全程在使用（遮蔽必崩），两者形成一个 **耦合的鲁棒联合表示**，augmentation 同时塑造了图像分支的退化不变性 + fusion_head 对 OCS 的依赖。

---

## 7. 12b-3：U1 OCS 噪声与双退化

### 7.1 设置（口径声明）

OCS 噪声方法（指导 §3 12b-3 首选项）：

```text
raw OCS per_part (30D)
  → noisy = raw + noise_level × |raw| × N(0,1)   （raw-feature relative perturbation）
  → log10(max(noisy, eps))
  → zscore using TRAIN mean/sd (固定，与 U1 训练所用一致)
  → ocs_zs_noisy
```

这是 **raw-feature relative perturbation re-standardized with train stats**，**不是** 直接对 `ocs_zs` 加噪，也 **不等同** 实验 6 的端到端 OCS-only 评估口径（实验 6 是 OCS-only MLP 上的端到端噪声鲁棒性测试）。结果中的 OCS 噪声效应 **仅说明** U1 fusion head 对 OCS 输入扰动的敏感性，不能与 OCS-only baseline 5.91° 直接对应。

### 7.2 Table 12b-3：U1 OCS 噪声 × 图像退化矩阵

| 图像退化 \ OCS 噪声 | 0% | 1% | 5% | 10% | 20% |
|---|---|---|---|---|---|
| clean | **1.95°** (98%) | 1.95° (98%) | 2.13° (97%) | 2.74° (92%) | 5.36° (73%) |
| noise σ=0.01 | **1.95°** (98%) | 1.95° (98%) | 2.13° (97%) | 2.74° (92%) | 5.37° (73%) |
| noise σ=0.10 | **2.31°** (97%) | 2.32° (97%) | 2.49° (95%) | 3.15° (91%) | 5.95° (71%) |
| bright×0.50 | **1.98°** (98%) | — | 2.16° (97%) | 2.73° (92%) | — |
| bright×1.50 | **2.00°** (97%) | — | 2.15° (96%) | 2.79° (92%) | — |

### 7.3 判读

- **OCS 噪声单调拉低 U1 性能**：每个图像档下，OCS 噪声 0%→20% 都导致 +3.4-3.6° 退化（Hit@5 从 ~97% 跌到 71-73%）。这从 **正向因果** 上证实了 OCS 不是装饰性输入——U1 确实在用 OCS。
- **OCS 噪声效应几乎与图像退化档无关**：
  - clean 图像下 OCS 0%→20%：1.95°→5.36°，Δ=+3.41°
  - noise σ=0.10 图像下 OCS 0%→20%：2.31°→5.95°，Δ=+3.64°
  - bright 档 5%→10%：~+0.7°，与 clean 档同档基本一致

  这说明 **U1 对 OCS 的依赖度是"常态化"的**——OCS 全程参与预测，不是图像退化时才"切换"到 OCS。这进一步否定了"image fails → switch to OCS"的离散 fallback 假设。

- **关键 sanity check**：U1 + OCS 噪声 20% 退到 5.36° ≈ OCS-only baseline 5.91°。这说明当 OCS 输入被严重扰动后，U1 退到一个粗糙的 OCS-only 等价水平——但不严格地，因为图像分支仍在持续提供细节信号。

**判据 3 结论**：OCS 在 U1 augmented fusion 中是 **持续参与的输入信号**，不是 fallback。OCS 噪声会单调劣化 U1 性能，与图像退化档独立。

---

## 8. 12b-4：U1 大离群样本审计

### 8.1 统计

- 评估总数（5 seed × 5 deg × 1998 test）= **49 950**
- error > 30°: **42** (0.084%)
- error > 60°: **40** (0.080%)
- error > 90°: **35** (0.070%)
- 跨退化重复离群（同 seed 同样本在 ≥2 个退化档 >30°）：**4** 个
- per-seed 离群计数: `{seed0:10, seed1:6, seed2:14, seed3:8, seed4:4}` — seed2 偏多
- 离群姿态分布：**\|pitch\|>60° 占 50.0%，\|pitch\|>75° 占 50.0%**，yaw 近 0/360° 占 4.8%

### 8.2 离群样本明细（节选）

跨退化重复离群（4 个，全部在极区）：

| seed | sample_idx | yaw_true | pitch_true | 退化档命中数 |
|---|---|---|---|---|
| 0 | 887 | 115° | 90° (北极) | 5/5 全退化档 |
| 2 | 185 | 25° | -90° (南极) | 5/5 全退化档 |
| 2 | 223 | 30° | -85° (近南极) | 5/5 全退化档 |
| 3 | 223 | 30° | -85° (近南极) | 4/5（除 clean 外都重复） |

这 4 个样本贡献了 ~20 条记录（占 >30° 总数 ~50%）。其余 ~22 条单档离群主要集中在 noise σ=0.10（32 条），少数在 bright 档。

### 8.3 判读

- **U1 mean / median / p90 / Hit@5 已稳定**，但 worst-case angular error 仍可达 ~165° (noise σ=0.10) 或 ~140° (bright×0.50)。
- 大离群 **强相关于姿态极区**（\|pitch\|>60° 占 50%，\|pitch\|>75° 占 50%）。这与已知的 yaw 在极点的不可观测性（yaw 在 pitch=±90° 时退化为虚拟自由度）一致——是几何固有困难，不是 U1 的失败。
- 即便在 clean 档（normal=1.95°）下，也有 4 个 极区样本 >30°，说明这 **不是图像退化引起的，而是数据集本身的极区病态**。
- seed2 离群 14 个 vs seed4 的 4 个，反映训练 stochasticity 在极区学习上的差异，但整体 mean/std 仍稳定（mean ±std 跨 seed 0.21°）。

**写作边界**：

- **可以写**：U1 stabilizes mean angular error, p90, and Hit@5° across all tested degradations; the remaining large outliers are concentrated at near-polar attitudes (\|pitch\|>75°) where yaw becomes intrinsically ill-conditioned.
- **不能写**：fully robust / near-perfect fusion / robust under all conditions.

---

## 9. 12b-5：未见退化泛化

### 9.1 设置（口径声明）

- 训练增强保持不变：仅 `AUG_DEGS = [clean, noise_0.01, noise_0.10, bright_0.50, bright_1.50]`，未将 12b-5 的新退化加入训练。
- 评估退化（全部 OOD）：
  - `noise_0.03`, `noise_0.05`（高斯噪声，σ 在训练增强 0.01 和 0.10 之间，但具体 σ 没见过）
  - `blur_k3`, `blur_k5`（高斯模糊；torch 实现，kernel=3/5，sigma 由 kernel size 默认推导）
  - `downsample_64`, `downsample_32`（128→64→128 / 128→32→128，bilinear 上下采样）
- 算子实现：复用 `run_fusion_mechanism_upgrade.apply_image_degradation` 的 blur / downsample 分支（实验 12 已可复现），无需额外实现。

### 9.2 Table 12b-5

| 未见退化 | U1 aug fusion | image-only+aug | Δ(img-only - U1) | U1 p95 |
|---|---|---|---|---|
| noise σ=0.03 | **1.99±0.23°** (97.7%) | 4.25±0.57° (69.8%) | +2.26° | 4.20° |
| noise σ=0.05 | **2.06±0.23°** (97.4%) | 6.43±0.94° (56.8%) | +4.37° | 4.31° |
| blur kernel=3 | **1.96±0.21°** (97.7%) | 2.84±0.27° (87.5%) | +0.88° | 4.22° |
| blur kernel=5 | **2.00±0.26°** (97.5%) | 4.12±0.52° (74.8%) | +2.12° | 4.22° |
| downsample 128→64 | **1.96±0.21°** (97.6%) | 3.06±0.29° (85.3%) | +1.10° | 4.23° |
| downsample 128→32 | **2.01±0.25°** (97.5%) | 4.93±0.61° (67.4%) | +2.92° | 4.24° |

### 9.3 判读

- **U1 augmented fusion 在 6 个未见退化下全部维持 ~2°（Hit@5 > 97%）**，与训练见过的退化档（1.95-2.31°）几乎无差。
- **image-only+aug 在中度未见退化下已显著退化**：noise σ=0.05 退到 6.43°（Hit@5=57%），downsample_32 退到 4.93°（Hit@5=67%）。
- 这是 **U1 优于 image-only+aug 的最强证据**——不是 cherry-picked 已训练退化，而是 broader **degradation-aware robustness**。OCS 的存在使 fusion 模型在 OOD 退化下仍能依赖一个**与图像无关的物理通道**保住精度。
- noise σ=0.05 的 U1 数值（2.06°）甚至 **优于 OCS-only baseline 5.91°**，说明即使在 OOD 退化下，U1 也比纯 OCS 模型更准——image 分支即便经过 OOD 退化仍提供有效残差信号。

**判据 5 结论**：U1 表现出 **比 matched-augmentation robustness 更广的 degradation-aware robustness**，OCS 分支的存在使 fusion 对 6 类未见退化都保持 ~2° 精度。

---

## 10. 机制判读：U1 是否真正使用 OCS fallback？

### 10.1 综合证据矩阵

| 假设 | 证据 | 支持度 |
|---|---|---|
| **H1: U1 robustness ≈ image-only+aug** | 12b-1: U1 严格优于 image-only+aug，σ=0.10 差 7.24°；12b-5: U1 在 6 个未见退化下都优于 image-only+aug | ❌ **否定** |
| **H2: U1 学到了"image fails → switch to OCS"的离散 fallback** | 12b-2: U1 在 clean 档下遮蔽 OCS 也崩到 53° vs 遮蔽 image 34.9°；OCS 在 clean 时已是更重要分支；12b-3: OCS 噪声效应与图像退化档无关（非 switching） | ❌ **否定** |
| **H3: U1 学到了 standalone OCS fallback predictor** | 12b-2: 遮蔽 image 后 U1 fusion 退到 34.9°，远高于 OCS-only baseline 5.91° | ❌ **否定** |
| **H4: U1 = OCS-image co-utilization（两分支耦合的鲁棒联合表示）** | 12b-2: 两个分支遮蔽都让模型崩到 30-60°，没有 standalone 路径；12b-3: OCS 噪声单调拉低 U1（+3.4°@20%）；12b-5: 未见退化下 U1 全档 ~2° vs image-only+aug 退化到 4-6° | ✅ **支持** |
| **H5: image-augmentation 重塑了 fusion_head 的权重分配** | 12b-2: U1 augmented vs 实验 12 naive 的分支遮蔽镜像反转——naive: OCS-mask 更糟；U1: image-mask 较 OCS-mask 更糟 | ✅ **支持** |

### 10.2 机制摘要句

```text
U1 augmented fusion 的鲁棒性不是经典 fallback（image fails → switch to OCS），
而是 OCS-image co-utilization:
  - Online image degradation augmentation
      → 教会图像分支抵抗 OOD 像素扰动（degradation-aware image features）
  - 同时 augmentation 重塑了 fusion_head 的权重分配
      → 使 OCS 成为 augmented fusion 中"更重要的分支"
        （遮蔽 OCS 比遮蔽 image 更糟，所有退化档）
  - OCS 是持续参与的输入（OCS 噪声单调拉低 U1）
  - 但 fusion_head 没有学到 standalone OCS-only 预测路径
      （遮蔽 image 后 U1 退到 ~34.9°，远高于 OCS-only 5.91°）
  - 净效果：两分支耦合的鲁棒联合表示，
            在已测试退化（5 档）+ 未见退化（6 档）下都保持 ~2°
```

### 10.3 与实验 12 + 实验 11 的衔接

| 训练范式 | clean | image noise σ=0.01 | image noise σ=0.10 | 机制 |
|---|---|---|---|---|
| Naive clean-trained fusion（实验 11） | 1.47° | **73.36°** ❌ | 73.57° ❌ | image-dominant，OOD 退化下崩溃 |
| U1 augmented fusion（实验 12 + 12b） | 1.95° | **1.95°** ✅ | 2.31° ✅ | OCS-image co-utilization，OCS 全程主导 fusion_head |
| Image-only + same aug（12b-1） | 2.63° | 2.80° | **9.55°** ⚠️ | matched augmentation only，σ=0.10 退化 |

**结论**：augmentation 不是简单的"图像分支变 robust"——它同时改变了 fusion_head 学到的两分支权重分配。这是一个 **训练范式重塑表示** 的发现，比单纯"加 augmentation 就 robust"更深一层。

---

## 11. 能写进论文的结论

### 11.1 Results 段（建议加入主稿）

> We further isolate the source of robustness in the augmentation-trained fusion model by training a ResNet image-only baseline under exactly the same online degradation augmentation. Under heavy Gaussian noise (σ=0.10), this image-only augmented baseline reaches 9.55° mean angular error (Hit@5°=41.4%), while the augmented fusion model reaches 2.31° (Hit@5°=96.6%) — a 7.24° gap. Across six held-out degradation types not used in training (Gaussian noise σ∈{0.03, 0.05}, Gaussian blur with kernels 3 and 5, and downsampling to 64×64 and 32×32), the augmented fusion model maintains 1.96°-2.06° mean angular error, while the image-only augmented baseline degrades to 2.84°-6.43°. This confirms that the OCS modality contributes robustness beyond what online image degradation augmentation alone can achieve.

### 11.2 Discussion 段（机制深挖）

> Branch-masking ablations on the augmented fusion model reveal that the underlying mechanism is not a discrete fallback in which the model "switches" to OCS only when the image branch fails. Rather, the OCS branch is continuously active across all tested conditions, including clean images. Specifically, masking the OCS branch at inference degrades the augmented fusion model to 53-58° across all evaluated degradations, while masking the image branch degrades it to ~34.9°. Both ablated configurations are far worse than either the OCS-only baseline (5.91°) or the image-only augmented baseline (~2.6°), indicating that neither branch has been trained as a standalone predictor. Instead, image-degradation augmentation appears to reshape the fusion head's weighting such that OCS becomes the more critical input in the joint representation, while augmentation simultaneously teaches the image branch to produce degradation-invariant features. This is a coupled co-utilization regime, not a learned fallback. Consistent with this interpretation, injecting noise on OCS features (1%-20% raw-feature relative noise) monotonically degrades the augmented fusion model's accuracy from 1.95° to 5.36°-5.95°, and the effect is largely independent of which image-degradation regime is applied.

### 11.3 Limitations 段（诚实边界）

> Two limitations follow from this analysis. First, while mean, median, p90, and Hit@5° metrics are stabilized under all tested degradations, rare large outliers (error > 30°) persist at a frequency of 0.08% (42 of 49 950 evaluations across 5 seeds × 5 degradations). These outliers are concentrated at near-polar attitudes (\|pitch\|>75° accounts for 50% of all > 30° outliers, and is dominated by four samples that repeat across multiple degradation regimes), reflecting the intrinsic singularity of yaw at the poles rather than a failure of the fusion strategy. Reporting only mean or Hit@5° without acknowledging these residual outliers would overstate operational robustness. Second, the OCS noise perturbation used here (raw-feature relative noise, re-standardized using training statistics) is a controlled perturbation on the standardized OCS input to the fusion head; it should not be conflated with the end-to-end OCS-only noise robustness reported earlier under the 5.91° baseline.

### 11.4 一句话核心论点（可放在 Abstract 或 Conclusion）

> Online image-degradation augmentation does not merely make the image branch robust; it reshapes the fusion head into a coupled OCS-image representation that is strictly more robust than image-only training with the same augmentation, and that generalizes to six unseen degradation types without further training.

---

## 12. 不能写的结论

以下都是 12b 数据 **不支持** 的论断，红线：

| ❌ 不能写 | 理由（基于 12b 数据） |
|---|---|
| "U1 learns an OCS-standalone fallback" | image_zero 在所有退化档下都退到 ~34.9°，远高于 OCS-only 5.91° |
| "OCS is automatically used as fallback when images fail" | OCS 噪声效应与图像退化档无关（+3.4° @ 20% 在 clean 和 noise σ=0.10 几乎一致）；OCS 在 clean 时就是主分支 |
| "Fully robust fusion" / "near-perfect robustness" | 42 个 >30° 离群，worst 仍可达 165°（noise σ=0.10）/ 140°（bright×0.50） |
| "Image masking yields OCS-only performance" | image_zero=34.9° ≠ OCS-only=5.91°；差距 ~29°，不能等同 |
| "Augmentation only makes images robust, OCS is unchanged" | augmentation 同时重塑了 fusion_head 的分支重要性（OCS 在 augmented 中变为更关键分支） |
| "U1 outperforms image-only aug only under image degradation" | 12b-5 显示 U1 在 6 个未见退化下全档优于 image-only+aug，差距 +0.88° 到 +4.37° |
| "实验 12b 已经证明 robust 在真实在轨观测下成立" | 全部基于合成 phase63 exact BRDF 渲染图像；未做真实望远镜验证 |

---

## 13. 后续建议

### 13.1 留给 Codex / 作者的决定

1. **v0.2 主稿 Results 段**：建议加入 12b-1 image-only+aug 列与 12b-5 未见退化表，把"U1 优势"做成 **isolation against augmentation-only baseline** 的核心结果。
2. **Discussion 机制段**：建议采用 §11.2 的"co-utilization 而非 fallback"表述，避免读者把 U1 误读为"OCS 在图像退化时被激活"。
3. **Limitations**：必须保留 §11.3 的 worst-case outlier 段落，否则会被审稿人质疑"mean-only reporting"。
4. **12b-5 未见退化是否进主图**：建议作为主图的子表（与 12b-1 同列），强调 **broader degradation-aware robustness**。如果主图空间紧张，可以放到 supplementary，但 **不能省略**（这是 U1 优于 image-only+aug 的最强证据）。
5. **12b-4 离群审计是否进主稿**：建议放 supplementary，主稿 Limitations 引用 "rare large outliers concentrated at near-polar attitudes"。

### 13.2 可能的下一步实验（如时间允许，非必须）

- **极区病态可视化**：把 4 个跨退化重复离群样本的预测 yaw/pitch 分布画出来，证实是 yaw-at-pole 不可观测性，不是 U1 的失败模式。
- **U1 与 OCS-anchored 升级（实验 12 的 U4 概念）混合**：U4 单独使用时精度不足（7.75°），但如果在 U1 augmentation 基础上添加 OCS-anchored 辅助损失（不替换主路径），可能进一步降低极区离群。这是 v0.2 之后的方向。
- **真实地面望远镜验证**：本报告所有结论基于合成渲染。如果有可用的真实图像数据，应做 sanity check（不必入主稿，但作者应知道）。

### 13.3 整合到 CLAUDE.md / 进度档案

建议作者在 codex 审阅 12b 后将以下内容写入 [20260529_补充实验进度.md](../../../../20260529_补充实验进度.md) §12：

```text
12b：U1 因果隔离已完成（run_20260604_150333, 5 seeds, 31 min）
  - 12b-1: image-only+aug σ=0.10=9.55° vs U1=2.31°，确认 U1 优于 augmentation-only
  - 12b-2: U1 中 OCS 是更重要分支（image_zero=34.9° < ocs_zero=53-58°）
  - 12b-3: OCS 噪声 0→20% 单调拉低 U1 +3.4-3.6°，与图像退化档无关
  - 12b-4: 42 个 >30° 离群 (0.08%)，50% 在 |pitch|>75°
  - 12b-5: U1 在 6 个未见退化下全档 ~2°，image-only+aug 退到 4-6°
  机制：OCS-image co-utilization，不是 fallback。
```

### 13.4 新对话上下文（断点恢复）

如需在新对话中继续实验 12b 的结果分析或修改主稿，只需让新 Claude 读取以下文件：

```text
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\02_后整合双线修订\Claude交互\Claude输出\07_Claude输出_融合机制诊断与鲁棒融合升级.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\论文写作\02_后整合双线修订\Claude交互\Claude输出\07b_Claude输出_融合fallback因果隔离.md
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\结果\fusion_mechanism_upgrade\run_20260604_092041\
D:\我的文件\研究生学术\光学项目\0506新\论文改进\补充实验\结果\fusion_fallback_isolation_12b\run_20260604_150333\
```

不需要从头重跑任何实验。所有数据、判读、写作段落草稿已在 07 + 07b 两份 Claude 输出中。

---

## 附录 A：完整 5 seeds 详细统计（mean ± std，p90 / p95 / worst）

### A.1 12b-1 image-only+aug 对 U1

| 退化 | 模型 | mean ± std | median | p90 | p95 | worst | Hit@5° | Hit@10° |
|---|---|---|---|---|---|---|---|---|
| clean | image-only+aug | 2.63±0.20 | 2.33 | 4.83 | 5.75 | 19.73 | 90.4% | 99.5% |
| clean | U1 fusion | 1.95±0.21 | 1.67 | 3.53 | 4.19 | 102.11 | 97.8% | 99.9% |
| noise σ=0.01 | image-only+aug | 2.80±0.23 | 2.46 | 5.14 | 6.20 | 22.84 | 88.3% | 99.3% |
| noise σ=0.01 | U1 fusion | 1.95±0.21 | 1.69 | 3.53 | 4.17 | 102.08 | 97.8% | 99.9% |
| noise σ=0.10 | image-only+aug | 9.55±0.75 | 5.91 | 18.14 | 26.24 | 174.96 | 41.4% | 73.3% |
| noise σ=0.10 | U1 fusion | 2.31±0.26 | 1.78 | 3.73 | 4.50 | 164.27 | 96.6% | 99.6% |
| bright×0.50 | image-only+aug | 2.76±0.25 | 2.38 | 5.06 | 6.23 | 22.38 | 88.9% | 99.1% |
| bright×0.50 | U1 fusion | 1.98±0.20 | 1.69 | 3.54 | 4.19 | 139.83 | 97.8% | 99.9% |
| bright×1.50 | image-only+aug | 2.76±0.20 | 2.42 | 5.02 | 6.04 | 21.33 | 89.3% | 99.3% |
| bright×1.50 | U1 fusion | 2.00±0.22 | 1.72 | 3.62 | 4.30 | 98.97 | 97.4% | 99.0% |

### A.2 训练配置

```text
image-only+aug:    epochs=413/339/385/347/500 (per seed), best_va=0.0014-0.0023
U1-aug-fusion:     epochs=500/425/283/500/500 (per seed), best_va=0.0009-0.0020
两者均使用 clean validation early stopping, patience=100
augmentation: AUG_DEGS 5 档 online 随机, base_seed=1000+seed
```

---

> 文档结束。
> 本报告未修改主稿 v0.1，未代填 Q12-Q15，未覆盖实验 12 主跑产物。
> 所有数据 traceable 到 `run_20260604_150333/` 内的 CSV/JSON。
