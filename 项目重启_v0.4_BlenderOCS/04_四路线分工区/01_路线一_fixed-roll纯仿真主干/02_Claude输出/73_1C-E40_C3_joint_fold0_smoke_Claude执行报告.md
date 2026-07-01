# 73_1C-E40_C3_joint_fold0_smoke_Claude执行报告

执行端：Claude | 任务编号：1C-E40 | 日期：2026-06-26

## 0. 裁决

```text
1C-E40：COMPLETED
Joint fold0 1-epoch smoke: PASS
C3 正式 5-fold: NOT RELEASED
Image_only 正式重训: NOT RELEASED
Ocs_only 正式训练: NOT RELEASED
```

---

## 1. Joint Fold0 1-Epoch Smoke

### 1.1 命令

```powershell
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" ^
  "06_v0.4_code/07_training/train_baseline.py" ^
  --train --mode joint --max-epochs 1 ^
  --train-split-manifest v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold0.json ^
  --outdir v0.4_results/06_c3_preflight/e40_joint_fold0_smoke ^
  --device cuda --val-max 128 --num-workers 0 --seed 42
```

### 1.2 运行结果

```text
Exit code: 0
Elapsed: 3.5s
Parameters: 3,913,229
Epochs: 1/1
OOM: NO
CUDA error: NONE
```

### 1.3 输出文件

| 文件 | 大小 | 状态 |
|---|---|---|
| `checkpoint_joint.pt` | 44.9 MB | WRITTEN |
| `e21_fix01_baseline_results.json` | 3.0 KB | WRITTEN |
| `e21_fix01_detail_joint.json` | 44.7 KB | WRITTEN |
| `e21_fix01_overlap_report.json` | 1.1 KB | WRITTEN |

### 1.4 管线验证

```text
Dataloader (image + OCS 联合加载):            PASS
CNN ImageEncoder (6-layer, 256×256→256-dim):  PASS
OCSEncoder (4-dim→128→128):                   PASS
Early fusion (concat 256+128→384→MLP head):   PASS
CUDA forward/backward:                        PASS
Checkpoint 写入:                               PASS
Overlap check:                                PASS (strict, 0 overlap)
Overlap report 写入:                           PASS
```

### 1.5 Smoke metrics（仅管线完整性，不解释、不进入论文证据）

```text
Train loss: 6.55
Test (primary yaw_block): yaw_acc=0.0000, pitch_acc=0.0378
Key metrics 存在于 JSON: YES
```

---

## 2. E25 Image-Only 5-Fold 历史结果登记

### 2.1 文件清单

| Fold | Checkpoint | Baseline JSON | Detail JSON | Overlap Report |
|---|---|---|---|---|
| fold0 | 44.3 MB ✓ | ✓ | ✓ | ✓ |
| fold1 | 44.3 MB ✓ | ✓ | ✓ | ✓ |
| fold2 | 44.3 MB ✓ | ✓ | ✓ | ✓ |
| fold3 | 44.3 MB ✓ | ✓ | ✓ | ✓ |
| fold4 | 44.3 MB ✓ | ✓ | ✓ | ✓ |

全部 5 fold 文件齐全。

### 2.2 口径（按 R73）

```text
E25 image_only 5-fold 结果仅登记为"复用候选"。
这些结果是 E21 FIX01 阶段产物，使用 --mode image_only；
OCS 输入来源和训练架构可能与正式 C3 的 image-only 口径不同。
不得直接将 E25 结果宣称为 C3 正式 image baseline。
是否复用需 Codex 后续口径确认。
```

---

## 3. 当前阶段门

```text
C3 joint fold0 smoke: PASS
C3 formal 5-fold training: NOT RELEASED
正式 image-only / ocs_only / joint 三通道对比: NOT RELEASED
E25 image_only 复用: CANDIDATE ONLY, NOT RELEASED
论文正文: NOT RELEASED
三轴小项目 / 路线二三四: NOT RELEASED
```

## 4. 红线

```text
本报告期间：未启动正式 C3 5-fold、未运行 image_only 正式重训、
未运行 ocs_only、未修改代码或数据管线、未将 smoke 指标作为论文证据、
未写论文正文、未放行其他路线。
```
