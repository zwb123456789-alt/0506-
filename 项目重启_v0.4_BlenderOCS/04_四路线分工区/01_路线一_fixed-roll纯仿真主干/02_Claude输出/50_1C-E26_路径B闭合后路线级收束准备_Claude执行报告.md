# 50 1C-E26：路径 B 闭合后路线级收束准备 Claude 执行报告

最后更新：2026-06-25  
执行端：Claude  
依据提示词：`04_Codex审阅/R49_Codex_提示词_1C-E26路径B闭合后路线级收束准备.md`

**状态：纯路线收束准备。不训练、不写论文、不放行后续执行。**

---

## 0. 收束摘要

```text
路线一 C Phase 0 B0 baseline 的三阶段证据链已闭合：

  Phase 1 (R38-R41)：数据生成 + 训练基础设施 → PASS
  Phase 2 (R42-R43)：random split baseline + strict yaw_block 单折 → PASS (含负结果)
  Phase 3 (R44-R48)：证据包整理 + 5-fold cross-validation + 成果补正 → PASS

当前状态：B0 image_only baseline 的跨 yaw 泛化边界已通过 5-fold CV 稳健确立。
后续可选 D1 (B1 fullrun/对比) 与 C (OCS 特征增强)，但均需独立 Codex 审阅放行。
论文正文改写、B1/GGX/三轴/路线二三四 仍不放行。
```

---

## 1. 路径 B 闭合证据清单

### 1.1 路径 B 执行链

| 阶段 | 任务 | Codex 审阅 | 裁决 |
|---|---|---|---|
| 方案设计 | 1C-E24：k=5 circular yaw_block 方案 | R46 | PASS |
| Split 生成 | circ_yaw_block 5 折 manifest | — | overlap gate PASS |
| 训练执行 | 5 折 image_only 训练 (GPU) | — | 完成 |
| 结果报告 | 1C-E25：多折训练结果 | R47 | CONDITIONAL PASS |
| 成果补正 | 1C-E25-FIX01：汇总 JSON + overlap report | R48 | PASS |

### 1.2 闭合的证据

**数据与 split（不可变）：**

```text
- 5 个 split_manifest_circ_yawblock_fold*.json
- 每折 train/val/test yaw bin 互斥，record_id 零重叠
- 跨折 test 覆盖 72/72 yaw bins，0 重复
- Pitch 37/37 全覆盖
```

**训练结果（不可变）：**

```text
- 5 个 fold*/checkpoint_image_only.pt
- 5 个 fold*/e21_fix01_baseline_results.json
- 5 个 fold*/e21_fix01_detail_image_only.json
- 1 个 e25_multifold_summary.json (聚合)
- 1 个 e25_overlap_report.json (总 overlap 证据)
```

**核心数值：**

| 指标 | 均值 | std (pop) | std (sample) | 范围 |
|---|---|---|---|---|
| yaw_acc | **0.00%** | 0.00% | 0.00% | 0.00% — 0.00% |
| pitch_acc | 20.68% | 5.68% | 6.35% | 13.51% — 30.50% |
| yaw_cmae | 83.5 deg | 24.9 deg | 27.8 deg | 45.2 — 114.9 deg |
| pitch_mae | 36.1 deg | 5.8 deg | 6.5 deg | 26.5 — 44.9 deg |

**代码资产：**

```text
- split_dataset.py：circ_yaw_block 方法（E25 新增）
- train_baseline.py：strict holdout + GPU 加速 + overlap check（E21-FIX01 增强，E25 复用）
```

---

## 2. 可引用结论与禁止结论

### 2.1 推荐引用口径（可直接用于论文消融章）

**5-fold yaw 泛化失败（strong negative evidence）：**

```text
"在 B0 fixed-roll image-only baseline 上，5-fold circular yaw-block
cross-validation 评估显示：跨未见 yaw 区间的 yaw 分类准确率稳定为
mean = 0.00%, std = 0.00%（5 folds，每折 strict holdout test 覆盖
72 个 yaw bin 中互不重叠的 14-15 bin）。当前 CNN + 单视图 B0 图像通道
不具备跨未见 yaw 区间的 zero-shot 泛化能力。"
```

引用时可直接指向：

```text
v0.4_results/03_training_baseline/e25_multifold_yawblock/e25_multifold_summary.json
```

**Pitch 部分迁移（正面但有限定）：**

```text
"pitch 在 strict yaw holdout 下仍有 20.68% 精度（随机基线 2.7%），但相比
random split 的 73.92% 大幅下降，说明 yaw 分布的缺失会连带削弱 pitch 估计。"
```

**训练工程可用性（纯工程）：**

```text
"训练基础设施（Dataset/Dataloader/三模式模型/checkpoint/
GPU 加速）在 2664 姿态 B0 fullrun 上工程可用。"
```

### 2.2 禁止结论（不得出现在论文中）

```text
X1 "OCS 通道显著提升跨 yaw 几何泛化"              ← R42/R43 已证伪
X2 "joint 在未见 yaw 上优于 image_only"            ← FIX01 负结果
X3 "本方法具备跨几何泛化能力"                      ← 5 折全 0%
X4 "E21 yaw_block 结果证明泛化"                    ← 泄漏伪影
X5 "4 维 OCS 提供姿态不变性特征"                   ← FIX01 负结果
X6 任何未标注 "in-distribution only" 的 yaw 泛化声称
X7 将 B0/image_only/fixed-roll 结果外推到真实望远镜
X8 将 B1 等同于 GGX                                ← R44 纠正
```

---

## 3. 当前 B0 baseline 完整证据边界（更新版）

在 E23 备忘录基础上，加入路径 B 的 5-fold 结果：

```text
┌──────────────────────────────────────────────────────────────┐
│ 路线一 C Phase 0 B0 baseline 证据边界（2026-06-25）          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ 已确立（Codex 审阅通过）：                                    │
│                                                              │
│ 数据侧：                                                      │
│ ✓ B0 fullrun 2664 数据 + checker 17/17 PASS     (R38)        │
│ ✓ 两个 split manifest：random + yaw_block        (R39/R41)   │
│ ✓ 5 个 circ_yaw_block split manifest            (E25)        │
│                                                              │
│ 工程侧：                                                      │
│ ✓ Dataset/Dataloader 三模式可用                  (R39)        │
│ ✓ 训练循环 + circular yaw MAE + GPU 加速         (R41/E25)   │
│ ✓ Checkpoint/metrics/detail JSON 落盘                         │
│                                                              │
│ 训练结果侧：                                                   │
│ ✓ random split in-distribution baseline          (R42)        │
│   image_only random test: yaw ~65-75% (varies by fold)       │
│ ✓ strict yaw_block single-fold: yaw=0.00%        (R43/FIX01) │
│ ✓ 5-fold circular yaw_block: yaw=0.00% ± 0.00%  (R48/E25)   │
│ ✓ pitch 部分可迁移: mean=20.68%                  (E25)        │
│                                                              │
│ 不成立：                                                      │
│ ✗ 跨未见 yaw 零样本泛化（单折 → 5 折均证实）                  │
│ ✗ 4 维 OCS 提供跨 yaw 不变性                                 │
│ ✗ joint 在 strict holdout 上优于 image_only      (FIX01)     │
│ ✗ E21 yaw_block 作为泛化证据（已永久撤回）       (R42)        │
│                                                              │
│ 边界条件：                                                     │
│ - B0 (phong-like BRDF only), phase63, fixed-roll             │
│ - 单视图 256x256 灰度图像                                     │
│ - 简单 CNN (3.8M params)，无显式不变性设计                     │
│ - 4 维 OCS (total + 3 per-part 积分光度)                      │
│ - 72 yaw x 37 pitch 分类 (5 deg bins)                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. 后续可选方向清单

以下方向均基于 E23 备忘录的路径框架。**本轮只做准备性描述，不放行执行。每个方向都需要独立的 Codex 审阅链。**

### 方向 D1：B1 书中改进冯模型 fullrun / 对比

```text
目的：
  将分支从 B0 (phong-like BRDF only) 推进到 B1 (书中改进冯模型)。
  保持 fixed-roll 和其他边界条件不变，形成 B0 vs B1 的控制变量对比。

科学问题：
  改进冯模型的 BRDF 是否改变图像通道对姿态的映射特性？
  在 strict yaw_block holdout 下，B1 的 yaw 泛化失败是否与 B0 一致？

执行内容（草案）：
  1. 确认 B1 材料参数（三部件分别对应书中数据）
  2. 设计 B1 Blender 渲染方案
  3. 生成 B1 fullrun（2664 或 1/4 subset 686）
  4. B1 checker → Codex 审阅
  5. 在 random split + strict yaw_block 上训练对比 B0 vs B1

前置条件：
  - B1 材料参数确认
  - Blender 渲染方案 + 试渲染通过 Codex 审阅
  - B1 fullrun checker 通过（类似 R38 流程）

预计成本：Blender 逐姿态渲染，2664 姿态以天计
风险：B1 仍受 fixed-roll 约束，跨 yaw 泛化失败可能重现
红线：B1 是书中改进冯模型，不可写成 GGX
状态：NOT RELEASED — 需独立 Codex 审阅链
Codex 审阅需要：是（方案 → 渲染 → checker → 训练对比，多轮）
```

### 方向 C：OCS 特征增强探索

```text
目的：
  从现有 B0 fullrun OCS manifest 构造更具 yaw 不变性的 OCS 特征，
  测试能否在 strict yaw_block holdout 下实现非零 yaw 泛化。

科学问题：
  在 fixed-roll 条件下，是否存在可从 4 维积分 OCS 派生的 yaw-invariant 特征？
  若能找到，joint 模型能否在 strict holdout 下恢复部分跨 yaw 泛化？

执行内容（草案）：
  1. 从 OCS manifest 提取候选特征：
     - per-part 比率 (jinshuzhuti/total, taiyangnengban/yinshenban, etc.)
     - 归一化 OCS (除以 total)
     - 多部件对比度
  2. OCS-only 模型快速筛选有效特征（strict yaw_block test）
  3. 若某特征组合 yaw_acc > 0%，加入 joint 模型复验

前置条件：
  - 特征设计方案通过 Codex 审阅
  - 特征提取脚本通过审阅
  - 只使用现有 B0 fullrun 数据，不重新渲染

预计成本：少量 GPU（OCS-only 训练极快，~40s/epoch on CPU）
风险：fixed-roll 下 4 维 OCS 对 yaw 的敏感性根植于物理（部件遮挡模式），
      派生特征的改进空间可能有限
状态：NOT RELEASED — 需独立 Codex 审阅链
Codex 审阅需要：是（特征方案 → OCS-only 筛选 → joint 复验）
```

### 方向 D2：GGX 或其他 BRDF mismatch 对照

```text
目的：B0 (phong-like) 与 GGX 的跨 BRDF 泛化评估

状态：远期方向，优先级低于 D1。需要独立的 Codex 审阅论证科学价值。
红线：GGX ≠ B1，不可混写。
```

### 方向 A（已闭合）

```text
B0 evidence packet 整理：已在 E23 完成，经 R44 审阅通过。
路径 B 的 5-fold 结果已纳入证据包（E25/E25-FIX01，R47/R48 通过）。
```

---

## 5. 路线级待裁决问题清单

以下问题影响下一步方向选择，需项目负责人 + Codex 共同裁决。**每条标注了裁决对后续路径的影响。**

### Q1：B0 baseline 证据是否足够支撑论文消融章？

```text
当前：B0 evidence packet 包含 random split baseline + 5-fold yaw_block 负结果。
问题：在写论文实验/消融章之前，是否还需要更多 B0 证据？
影响：
  - 若足够 → 可直接进入论文实验设计阶段（不放行正文写作，只放行章节规划）
  - 若不够 → 确认还需要什么（如 joint 5-fold / OCS-only 5-fold 等其他对照）
建议：B0 image_only 的证据链已足够（R38→R48, 10 轮审阅），可进入论文实验设计规划。
```

### Q2：下一步优先 D1（B1 fullrun）还是 C（OCS 特征增强）？

```text
D1 优势：B1 是 24 号冻结文件的主线对比，控制变量清晰，论文实验完整度贡献大
D1 代价：B1 fullrun 渲染成本高（天级），需多轮 Codex 审阅
C 优势：零渲染成本，若成功则是 significant novelty；计算开销极小
C 风险：成功概率不确定，fixed-roll 单视图下 OCS 不变性空间可能很有限
影响：
  - 若选 D1 → 启动 B1 材料参数确认 + Blender 方案审阅
  - 若选 C → 启动 OCS 特征方案设计 + OCS-only 筛选
  - 可以先 C 再 D1，两者不互斥
建议：优先 C（低成本探索，<30 min GPU），然后 D1（主线对比，天级渲染）。
```

### Q3：5-fold 是否需要扩展到 joint 或 OCS-only？

```text
当前：5-fold 只跑了 image_only（最干净的单通道 yaw 泛化测试）
问题：是否需要在 5-fold 协议下跑 joint 或 OCS-only 作为对照？
影响：
  - 若需要 → 新增 5 fold × 2 modes = 10 次训练（~100 min GPU）
  - 若不需要 → 论文只引用 image_only 5-fold，joint/OCS-only 只用 FIX01 单折
建议：不需要。OCS-only 5-fold 几乎必定全 0%（FIX01 单折 yaw=0%），边际信息增益低。
Joint 的 5-fold 意义也有限（FIX01 中 joint pitch 反而不如 image_only）。
当前证据已足够支撑 "image_only 不具备跨 yaw 泛化" 的结论。
```

### Q4：论文实验设计是否可以开始规划（不是正文写作）？

```text
当前：B0 evidence packet 完整，R38-R48 审阅链闭合
问题：是否可以放行论文实验设计章节的规划？
  1. 列出实验章节目录
  2. 标注每个实验对应的 B0 证据和数据来源
  3. 标注需要 B1/C/D2 补充的证据缺口
  4. 明确哪些结果可进入正文、哪些放入消融/附录
影响：
  - 若放行 → 启动论文实验设计规划（不放行正文写作）
  - 若不 → 继续在路线级收束，等待更多证据
建议：可放行实验设计规划。当前 B0 证据链已达 10 轮审阅，R38-R48。
对论文实验章的结构设计不消耗计算资源，且能反哺后续 D1/C 的执行优先级决策。
```

---

## 6. 全链审阅状态速查（R38 → R48）

| Codex | 任务 | 裁决 | 路径 |
|---|---|---|---|
| R38 | 1C-E18 fullrun 2664 数据生成 | PASS | — |
| R39 | 1C-E19 训练入口 + 数据切分 | PASS | — |
| R40 | 1C-E20 训练 smoke | 条件通过 | — |
| R41 | 1C-E20-FIX01 smoke 判据修正 | PASS | — |
| R42 | 1C-E21 baseline (泄漏诊断) | 工程 PASS / 泛化 FAIL | — |
| R43 | 1C-E21-FIX01 strict yaw_block 单折 | PASS (负结果) | — |
| R44 | 1C-E22 路线决策准备 → E23 | PASS | — |
| R45 | 1C-E23 证据包 → E24 | PASS | — |
| R46 | 1C-E24 多折方案 → E25 | PASS | — |
| R47 | 1C-E25 多折训练结果 | 条件通过 | **B** |
| R48 | 1C-E25-FIX01 成果包补正 | PASS | **B** |

路径 A：R44 → R45  
路径 B：R46 → R47 → R48 → **已闭合**

---

## 7. 红线确认

- [x] 不训练
- [x] 不改代码
- [x] 不改数据结果
- [x] 不写论文正文
- [x] 不启动 B1/GGX
- [x] 不启动三轴小项目
- [x] 不启动路线二/三/四
- [x] 不把 B0/image_only/fixed-roll 结果外推到真实未知目标姿态反演
- [x] 不把路径 B 负结果写成 B1、GGX、OCS-only、joint 或三轴结论
