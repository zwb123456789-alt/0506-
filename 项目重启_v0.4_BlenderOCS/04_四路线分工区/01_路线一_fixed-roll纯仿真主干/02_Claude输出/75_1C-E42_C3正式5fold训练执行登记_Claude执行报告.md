# 75_1C-E42_C3正式5fold训练执行登记_Claude执行报告

执行端：Claude  
任务编号：1C-E42  
执行日期：2026-06-26  
协议：R75 Option B-min

---

## 0. 执行状态

```text
1C-E42：COMPLETED
image_only 5 folds：全部通过
joint 5 folds：全部通过
总计 10/10 训练完成，CUDA OOM 无
```

---

## 1. 训练结果登记

### 1.1 image_only 5-fold

| Fold | Exit | Elapsed | yaw_acc | pitch_acc | yaw_cmae | Overlap | 文件齐全 |
|------|------|---------|---------|-----------|----------|---------|----------|
| 0 | 0 | 496s | 0.00% | 21.80% | 104.5° | strict ✓ | ✓ |
| 1 | 0 | 503s | 0.00% | 15.68% | 72.1° | strict ✓ | ✓ |
| 2 | 0 | 493s | 0.00% | 15.83% | 107.9° | strict ✓ | ✓ |
| 3 | 0 | 495s | 0.00% | 24.52% | 73.4° | strict ✓ | ✓ |
| 4 | 0 | 499s | 0.00% | 28.19% | 49.3° | strict ✓ | ✓ |

**Aggregate**: mean yaw_acc=0.00%（全部 5 folds），mean pitch_acc=21.20%，mean yaw_cmae=81.4°

### 1.2 joint 5-fold

| Fold | Exit | Elapsed | yaw_acc | pitch_acc | yaw_cmae | Overlap | 文件齐全 |
|------|------|---------|---------|-----------|----------|---------|----------|
| 0 | 0 | 495s | 0.00% | 27.03% | 100.8° | strict ✓ | ✓ |
| 1 | 0 | 493s | 0.00% | 13.87% | 75.8° | strict ✓ | ✓ |
| 2 | 0 | 498s | 0.00% | 18.15% | 95.2° | strict ✓ | ✓ |
| 3 | 0 | 510s | 0.00% | 13.51% | 88.5° | strict ✓ | ✓ |
| 4 | 0 | 498s | 0.00% | 24.52% | 46.7° | strict ✓ | ✓ |

**Aggregate**: mean yaw_acc=0.00%（全部 5 folds），mean pitch_acc=19.42%，mean yaw_cmae=81.4°

### 1.3 交叉对照速览

| 通道 | mean yaw_acc | mean pitch_acc | mean yaw_cmae |
|------|-------------|---------------|---------------|
| C2 OCS-only（R62） | 0.00% | 2.56–4.37% | 80–120° |
| C3 image_only | 0.00% | 21.20% | 81.4° |
| C3 joint | 0.00% | 19.42% | 81.4° |

---

## 2. 输出路径

```text
v0.4_results/06_c3_preflight/c3_image_formal_5fold/fold0-4/
  checkpoint_image_only.pt
  e21_fix01_baseline_results.json
  e21_fix01_detail_image_only.json
  e21_fix01_overlap_report.json

v0.4_results/06_c3_preflight/c3_joint_formal_5fold/fold0-4/
  checkpoint_joint.pt
  e21_fix01_baseline_results.json
  e21_fix01_detail_joint.json
  e21_fix01_overlap_report.json
```

---

## 3. 红线确认

| 红线 | 状态 |
|------|------|
| 不运行 --mode all | ✅ 只运行了 image_only 和 joint |
| 不运行 raw 4-dim ocs_only | ✅ 未运行 |
| 不修改代码/模型/数据/split/batch size/LR/seed/epochs | ✅ 全部使用 R75 命令模板 |
| E40 smoke / E25 不写成 C3 正式证据 | ✅ 本报告仅登记 C3 正式 5-fold 结果 |
| 不写论文正文/不扩展三轴/路线二三四 | ✅ 遵守 |
| OOM/CUDA error/缺文件/失败 | ✅ 无 |

---

**执行端签名**：Claude  
**下一步**：交 Codex 审阅 C3 正式 5-fold 结果
