# 72_1C-E39_C3资源入口核查_Claude执行报告

执行端：Claude | 任务编号：1C-E39 | 日期：2026-06-26

## 0. 裁决

```text
1C-E39：COMPLETED
范围：仅核查 C3 放行前资源与输入入口，未启动训练
```

---

## 1. 数据资产核查

### 1.1 Split Manifest（yaw-block holdout，C3 直接复用）

| 文件 | 状态 | 说明 |
|---|---|---|
| `v0.4_results/03_training_baseline/e25_multifold_yawblock/` | READY | 5-fold circ_yaw_block，每 fold 独立 JSON |
| fold0: train=1850, val=259, test=555 | READY | train∩val∩test 严格 0 overlap |
| `split_manifest.json` (random) | READY | train=2109, val=259, test=296 |

C3 最小协议直接使用 C2 同款 fold manifest，无需重新生成 split。

### 1.2 图像数据（image_only / joint 入口）

| 项目 | 状态 | 说明 |
|---|---|---|
| png_path 字段 | READY | split manifest 每条 record 均含 `png_path` |
| 图像格式 | READY | 256×256 灰度 PNG（`/255.0` norm，`dataset.py` 已实现） |
| record_id 对齐 | READY | OCS manifest + image manifest 按 record_id 对齐，2664 条 |
| OCS 4-dim 字段 | READY | `ocs_total/jinshuzhuti/taiyangnengban/yinshenban` 均在 manifest 中 |
| 标签字段 | READY | `yaw_idx` (0-71), `pitch_idx` (0-36) |

### 1.3 OCS 特征 (ocs_only 入口)

| 项目 | 状态 |
|---|---|
| `enhanced_ocs_features.npz` | READY，含 13 个 C2 config 的全部特征 |
| `feature_definitions.json` | READY |
| `EnhancedOCSDataset` (enhanced_ocs_dataset.py) | READY，已支持 per-fold per-config |

---

## 2. 训练代码核查

### 2.1 已存在的可复用代码

| 代码资产 | 文件 | 状态 |
|---|---|---|
| OCSImageDataset (三模式) | `dataset.py` L40-119 | READY — `image_only` / `ocs_only` / `joint` 已实现 |
| ImageEncoder (6层CNN) | `train_baseline.py` L71-91 | READY — 输入 `[1,256,256]`→256-dim |
| OCSEncoder (3层MLP) | `train_baseline.py` L94-104 | READY — 4-dim→128→128 |
| OCSImageModel (三模式) | `train_baseline.py` L107-129 | READY — 自动拼合 image+OCS features → MLP head |
| Early fusion (concat) | `train_baseline.py` L122-126 | READY — `torch.cat([img_feat, ocs_feat], dim=1)` |
| Yaw-block holdout 训练入口 | `train_baseline.py` L557 | READY — `--train-split-manifest` + `--train` |
| 固定协议硬上限 | `train_baseline.py` L64 | READY — `MAX_EPOCHS_HARD=30` |
| 评估指标 | `train_baseline.py` L141-244 | READY — yaw_acc, CMAE, within-3, pitch_acc, per-bin, confusion |

### 2.2 Image Encoder 说明

当前代码使用自定义 6 层 CNN（`ImageEncoder`），不是 ResNet18。这更适合 C3 最小协议：

```text
- 无 pretrained vs from-scratch 争论
- 已在 baseline 代码中就绪，无额外开发量
- 若放行后需要 ResNet18，只需替换 ImageEncoder 类，不影响整体架构
```

### 2.3 代码缺口

| 缺口 | 严重度 | 说明 |
|---|---|---|
| C3 专用启动脚本 | LOW | `train_baseline.py` 已可直接使用 `--mode image_only/joint/all --train-split-manifest <fold>` |
| 5-fold 批量训练脚本 | LOW | 写一个 shell 循环即可，5 行 bash |
| OCS 特征维度适配 | LOW | C2 用了 `EnhancedOCSDataset`（npz→MLP），C3 joint 若复用需将 OCS 4-dim 从 manifest 读取（`OCSImageDataset` 已做） |

---

## 3. 环境核查

```text
PyTorch: 2.8.0+cu128
CUDA: 12.8
GPU: NVIDIA GeForce RTX 5060 Laptop GPU × 1
Python: ocs_sim conda env (C:\Users\97466\.conda\envs\ocs_sim\python.exe)
```

GPU 可用，单卡，内存需关注（laptop GPU 显存通常 8GB）。

---

## 4. C3 放行前 Readiness Checklist

### READY（无需任何新开发或数据生成）

| # | 项目 | 状态 |
|---|---|---|
| R1 | Yaw-block 5-fold split manifests | READY |
| R2 | PNG 图像数据（256×256 灰度） | READY |
| R3 | Split manifest 中含 png_path、OCS 4-dim、yaw/pitch label | READY |
| R4 | OCSImageDataset 三模式（image_only/ocs_only/joint） | READY |
| R5 | ImageEncoder（6层CNN）+ OCSEncoder（3层MLP） | READY |
| R6 | OCSImageModel — early fusion concat + MLP head | READY |
| R7 | 训练入口 `--train --mode all --train-split-manifest <fold>` | READY |
| R8 | 评估指标（yaw_acc/CMAE/within-3/pitch_acc/per-bin） | READY |
| R9 | 固定协议硬上限 MAX_EPOCHS=30 | READY |
| R10 | GPU CUDA 可用 | READY |

### MISSING（必须补，否则不可放行 C3）

无。

### RISK（不放行 C3 也能训练，但需注意）

| # | 风险 | 级别 | 缓解 |
|---|---|---|---|
| K1 | Laptop GPU 显存（~8GB），joint 模式 3 通道可能 OOM | MEDIUM | batch_size=16 或 8；先 smoke test 1 epoch |
| K2 | OCS-only C2 用了 `EnhancedOCSDataset`（npz→MLP），C3 joint 用的是 `OCSImageDataset`（manifest 4-dim）。两种 OCS 特征源不等价 | MEDIUM | C3 joint 应复用 C2 的 npz 特征以保证可比性，而非 manifest 4-dim。需写一个 adapter 使 joint 模式下 OCS 端读取 npz 配置 |
| K3 | 5-fold 全部训练耗时：image-only ~1h/fold × 5 + joint ~1.2h/fold × 5 ≈ 11h | LOW | 先跑 1 fold smoke，确认无 bug 再批量 |
| K4 | C2 结果来自 `EnhancedOCSDataset` (train_c2_screening.py)，C3 若用 `train_baseline.py` 则架构、特征源不完全可比 | HIGH | 必须确保 C3 image-only/ocs-only/joint 三通道都在同一 `OCSImageModel` 框架下评估，或 ocs-only 复用 C2 结果作为 baseline |

---

## 5. C3 最小可执行方案候选（不放行，仅供 Codex 评估）

### 方案 1：纯 `train_baseline.py`（最快启动）

```text
对每个 fold (0-4):
  python train_baseline.py --train --mode all --max-epochs 30 \
    --train-split-manifest split_manifest_circ_yawblock_fold{fold}.json \
    --outdir v0.4_results/c3_comparison/fold{fold}/

产出：ocs_only / image_only / joint 三通道在同一框架下的结果。
```

**优点**：零代码修改，`--mode all` 一次跑完三通道。
**风险**：K2（ocs_only 用了 manifest 4-dim 而非 C2 npz 13 configs）。

### 方案 2：混合框架（C2 结果 + train_baseline image/joint）

```text
- OCS-only：直接复用 C2 13 configs 结果（已稳定）
- Image-only + Joint：用 train_baseline.py，OCS 端从 npz 读 baseline_4dim
- 三通道对比表：C2 ocs_only best config vs image-only vs joint
```

**优点**：OCS-only 复用 C2 稳定证据，只跑 image/joint。
**风险**：需要写一个小的 adapter 让 train_baseline 的 joint 模式从 npz 读 OCS（而非 manifest 4-dim）。

### Codex 需裁决

```text
1. C3 用方案 1（纯 train_baseline）还是方案 2（混合）？
2. 若方案 2，OCS 端用 baseline_4dim 还是 C2 全部 13 configs？
3. image encoder 用现有 6-layer CNN 还是替换为 ResNet18？
4. 是否先放行 1-fold smoke test，确认无 bug 后再放行 5-fold？
```

---

## 6. 红线

```text
本报告期间：未启动 C3 训练、未运行新实验、未修改代码或数据管线、
未写论文正文、未放行三轴小项目或路线二三四。
```
