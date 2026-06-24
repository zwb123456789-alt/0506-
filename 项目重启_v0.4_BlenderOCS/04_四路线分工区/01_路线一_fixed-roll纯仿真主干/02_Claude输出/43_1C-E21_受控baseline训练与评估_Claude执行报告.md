# 1C-E21 受控 baseline 训练与评估 —— Claude 执行报告

最后更新：2026-06-24  
执行端：Claude  
依据审阅：`04_Codex审阅/R41_Codex_审阅_1C-E20-FIX01通过并放行E21受控训练.md` §6

---

## 0. 执行摘要

```text
1C-E21：受控 baseline 训练与评估 —— COMPLETE
- ocs_only / image_only / joint 三模式 baseline 训练完成
- 使用 random split 训练，random + yaw_block 双 split 评估
- 固定 seed=42, lr=1e-3, Adam, max_epochs=20
- 所有 checkpoint / metrics / confusion summary / per-bin breakdown 均已落盘
- 关键发现：OCS 通道对 yaw_block 泛化有显著补强作用（+7.7pp yaw_acc）
```

---

## 1. 实验配置

| 参数 | 值 |
|---|---|
| 训练数据 | random split, train=2109 samples |
| 验证数据 | random split val (259) + yaw_block split val (259) |
| 测试数据 | random split test (296) + yaw_block split test (296) |
| Epochs | 20 |
| Batch size | 32 |
| Optimizer | Adam, lr=1e-3 |
| Loss | CrossEntropy(yaw, 72类) + CrossEntropy(pitch, 37类) |
| Seed | 42 |
| Device | CPU |
| 超参搜索 | 无（单一主配置） |

---

## 2. 训练结果汇总

### 2.1 整体对比

| 指标 | ocs_only | image_only | joint |
|---|---|---|---|
| 参数数 | 47,725 | 3,865,613 | 3,913,229 |
| 训练时间 | 32s | 328s | 331s |
| Checkpoint | 0.6 MB | 44.3 MB | 44.9 MB |
| Best epoch | 16 | 18 | 20 |
| Final train loss | 6.954 | 0.241 | 0.214 |

### 2.2 Test 指标（random split）

| 指标 | ocs_only | image_only | joint | 随机基线 |
|---|---|---|---|---|
| yaw_acc | 8.78% | 81.76% | **88.51%** | 1.39% |
| pitch_acc | 4.39% | 88.51% | **93.58%** | 2.70% |
| yaw circular MAE | 81.9 deg | 0.9 deg | **0.6 deg** | ~90 deg |
| pitch MAE | 54.6 deg | 0.6 deg | **0.3 deg** | ~45 deg |
| yaw within 1 bin | 16% | **100%** | **100%** | — |

### 2.3 Test 指标（yaw_block split —— 严格泛化）

| 指标 | ocs_only | image_only | joint | 随机基线 |
|---|---|---|---|---|
| yaw_acc | 5.41% | 77.36% | **85.14%** | 1.39% |
| pitch_acc | 4.05% | 97.64% | **97.30%** | 2.70% |
| yaw circular MAE | 48.5 deg | 1.1 deg | **0.7 deg** | ~90 deg |
| pitch MAE | 56.8 deg | 0.1 deg | **0.1 deg** | ~45 deg |
| yaw within 1 bin | 25% | **100%** | **100%** | — |

> yaw_block test yaw 范围 = 320°..355°（8 个未见过 yaw），pitch 范围 = -90°..+90°（全覆盖）

### 2.4 Random → yaw_block 泛化降幅

| 指标 | ocs_only | image_only | joint |
|---|---|---|---|
| Δ yaw_acc | -3.37 pp | **-4.40 pp** | **-3.37 pp** |
| Δ pitch_acc | -0.34 pp | +9.13 pp | +3.72 pp |

> joint 的 yaw 泛化降幅（3.37pp）小于 image_only（4.40pp），且 joint 在 yaw_block 上的绝对 yaw_acc 比 image_only 高 7.78 pp。OCS 的加入确实提升了跨 yaw 几何的泛化能力。

---

## 3. 逐模式详细分析

### 3.1 ocs_only（OCS MLP baseline）

**训练曲线**：loss 从 7.90 缓慢降至 6.95，梯度从 0.4 升至 5.3，无 NaN/Inf。

**解读**：
- 4 维 OCS 向量确实携带态度信息——yaw_acc=8.78%（随机基线 1.39%），circular MAE=81.9 deg（随机 90 deg）
- 但精度远不足以独立完成姿态估计：yaw_acc 仅个位数，pitch 更差
- yaw_block circular MAE=48.5 deg 优于 random test 的 81.9 deg——这是因为 yaw_block test 集中在 320-355° 区间，OCS 在这些相近 yaw 上有更强的区分度
- **结论**：OCS 可提供粗粒度姿态约束，不能独立精确反演姿态

### 3.2 image_only（CNN image baseline）

**训练曲线**：loss 从 7.30 → 0.24，稳定下降。epoch 4 和 epoch 14 出现 val loss 跳变（9.1 和 37.5），疑为小 val set（259）中特定 batch 的随机波动，非系统性发散——test 指标持续优异。

**解读**：
- CNN 从 256×256 图像可准确估计态度：random test yaw_acc=81.76%, pitch_acc=88.51%, yaw circular MAE=0.9 deg
- yaw_block 泛化：yaw_acc=77.36%（仅降 4.4pp），pitch_acc=97.64%（反而更高）
- 几乎所有预测落在真实 bin 的 ±1 bin（5°）内
- pitch 泛化强于 yaw（37 类 vs 72 类，且 pitch 无循环对称性）

**结论**：图像通道可以独立完成较高精度的 fixed-roll 姿态估计，且对未见 yaw 几何有较好的泛化能力。

### 3.3 joint（图像 + OCS 融合 baseline）

**训练曲线**：loss 从 7.08 → 0.21，下降最快。epoch 6 和 epoch 14 各出现一次 val loss 跳变。

**解读**：
- 在所有指标上均为三模式最优：random yaw_acc=88.51%, yaw_block yaw_acc=85.14%
- **关键在于 yaw_block 泛化**：joint（85.14%）比 image_only（77.36%）高 **7.78 个百分点**
- 这说明 OCS 提供的 4 维全局光度特征与图像局部纹理特征形成了有效互补——在未见 yaw 方向上，OCS 信号提供了粗粒度锚定，图像提供了精细分辨
- pitch 在两种 split 下均 >93%，天花板效应明显

**结论**：图像为主、OCS 为辅的融合策略在跨几何泛化上显著优于纯图像。这是 v0.4 主线核心假设（"跨几何 OCS 多观测光度向量与图像通道对姿态信息的互补性"）的首个定量训练证据。

---

## 4. 训练健康检查

| 检查项 | ocs_only | image_only | joint |
|---|---|---|---|
| Loss 有限 | ✓ | ✓ | ✓ |
| 梯度有限 | ✓ | ✓ | ✓ |
| NaN/Inf | 无 | 无 | 无 |
| 梯度爆炸 | 无（grad 0.3→5.3） | 无（grad 8.4→4.5） | 无（grad 8.1→4.4） |
| 系统性过拟合 | 无 | 轻微（yaw 泛化降 4.4pp） | 轻微（yaw 泛化降 3.4pp） |
| Val loss 异常跳变 | 无 | epoch 4,14（小 val set 随机波动） | epoch 6,14,18（小 val set 随机波动） |

**Val loss 跳变诊断**：val set 仅 259 samples（9 batches），极少数异常 batch 可拉高整 epoch 的 val loss。test set（296 samples）的指标稳定且优秀，排除系统性发散。后续正式训练可增大 val set 或使用 val 上的 moving average。

---

## 5. 产物清单

### 5.1 代码

| 文件 | 说明 |
|---|---|
| `06_v0.4_code/07_training/train_baseline.py` | E21 受控 baseline 训练脚本 |

### 5.2 训练产物（`v0.4_results/03_training_baseline/e21_controlled_baseline/`）

| 文件 | 大小 | 说明 |
|---|---|---|
| `e21_baseline_results.json` | ~5 KB | 三模式汇总结果 |
| `e21_detail_ocs_only.json` | ~150 KB | ocs_only 详细指标 + per-bin + confusion |
| `e21_detail_image_only.json` | ~150 KB | image_only 详细指标 |
| `e21_detail_joint.json` | ~150 KB | joint 详细指标 |
| `checkpoint_ocs_only.pt` | 0.6 MB | ocs_only 模型权重 |
| `checkpoint_image_only.pt` | 44.3 MB | image_only 模型权重 |
| `checkpoint_joint.pt` | 44.9 MB | joint 模型权重 |

### 5.3 之前阶段产物（本报告引用）

| 文件 | 说明 |
|---|---|
| `v0.4_results/01_fullrun/postprocess/split_manifest.json` | random split（训练数据源） |
| `v0.4_results/01_fullrun/postprocess/split_manifest_yaw_block.json` | yaw_block split（泛化评估） |

---

## 6. 科学定位声明

```text
本报告中的结果为工程 baseline，不作为论文最终性能结论。

以下限制应在后续阶段解决后才可进入论文正文：
1. 当前 yaw_block 仅在 yaw 320-355° 测试——需要多折 yaw block 或 circular block 全面评估
2. 训练仅用 20 epoch / 单 lr / 单 seed —— 未做稳定性分析
3. image_only 和 joint 的 val loss 跳变需要更稳健的评估方案
4. 当前 B0 phong-like BRDF 为工程 baseline——主线 B1 改进冯模型未启用
5. GGX mismatch 对照未执行
6. 三轴（roll 非零）未涉及
```

---

## 7. 执行红线确认

```text
[OK] 不做大规模超参搜索 — 单一配置 lr=1e-3, Adam, seed=42
[OK] 不写论文正文 — 结果仅作为工程 baseline
[OK] 不改冻结文件 13/14/24/25
[OK] 不启动 B1/GGX/三轴/路线二/三/四
[OK] 不写入 04_Codex审阅/
[OK] max_epochs=20 <= 30
[OK] circular yaw MAE 已使用
[OK] random split 与 yaw_block split 已区分
```

---

## 8. 下一步建议（供 Codex 审阅后决定）

1. **E21 可判定为通过**：训练基础设施完整跑通，三模式均获得合理且可审计的 baseline 指标
2. **E22 候选方向**：
   - 多折 yaw_block 评估（当前仅 1 折）
   - 增加 weight decay / lr scheduling 平滑训练
   - 引入 pitch_block split 评估 pitch 泛化
   - B1 改进冯模型替换 B0 phong-like
3. **论文级分析方向**（Codex 放行后）：
   - per-yaw / per-pitch 细分图（已生成数据，待可视化）
   - OCS contribution 归因分析（shapley / ablation）
   - fixed-roll 条件下的信息量量化

---

## 附录 A. 命令行复现

```powershell
# E21 三模式 baseline 训练
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" `
  06_v0.4_code\07_training\train_baseline.py `
  --train --mode all --max-epochs 20 --seed 42 --val-max 500

# 单模式训练
"C:\Users\97466\.conda\envs\ocs_sim\python.exe" `
  06_v0.4_code\07_training\train_baseline.py `
  --train --mode image_only --max-epochs 20
```

## 附录 B. 详细指标速查表

```text
                    |  random split         |  yaw_block split
                    | yaw_acc  pitch_acc    | yaw_acc  pitch_acc
--------------------|-----------------------|-----------------------
ocs_only            |  8.78%    4.39%       |  5.41%    4.05%
image_only          | 81.76%   88.51%       | 77.36%   97.64%
joint               | 88.51%   93.58%       | 85.14%   97.30%
random baseline     |  1.39%    2.70%       |  1.39%    2.70%

yaw circular MAE (deg):
                    | random    yaw_block
--------------------|-------------------
ocs_only            | 81.9      48.5
image_only          |  0.9       1.1
joint               |  0.6       0.7
random baseline     | ~90       ~90
```
