# 45 1C-E22：路线一 C 结果边界与后续路径裁决准备 Claude 执行报告

最后更新：2026-06-24  
执行端：Claude  
依据审阅：`04_Codex审阅/R43_Codex_审阅_1C-E21-FIX01严格泛化复评通过并要求路线决策.md`

---

## 0. 执行摘要

```text
1C-E22 路线裁决准备：DONE
R38-R43 全链证据汇总：完成
当前 B0 baseline 边界：已划定
后续路径候选：4 条，均已评估目的/代价/风险
下一步：等待项目负责人路线决策
```

本报告不写论文正文、不启动新训练或实验，仅作为路线一 C 当前证据边界的结构整理和后续路径选项的裁决准备材料。

---

## 1. R38-R43 全链证据汇总

### 1.1 审阅链全貌

| Codex 审阅 | 任务 | 裁决 | 关键产出 |
|---|---|---|---|
| R38 | 1C-E18 全量 2664 生成 | **PASS** | 2664 camera/sun EXR, postprocess 5×2664, checker 17/17 |
| R39 | 1C-E19 训练入口+数据切分 | **PASS** | Dataset/Dataloader, random split manifest, forward smoke |
| R40 | 1C-E20 最小训练 smoke | 条件通过 | 基础设施验证通过，但判据设计需修正 |
| R41 | 1C-E20-FIX01 smoke 判据修正 | **PASS** | 基础设施/性能拆分, yaw_block split, E21 放行(有限制) |
| R42 | 1C-E21 受控 baseline | 工程 PASS / 泛化 FAIL | random split OK, yaw_block 结果被 train-test 泄漏污染 |
| R43 | 1C-E21-FIX01 严格泛化复评 | **PASS (负结果)** | yaw_block strict holdout 确认跨 yaw 泛化失败 |

### 1.2 证据链中已确立的事实

**数据侧（R38）：**

```text
- B0 (BRDF only) / phase63 几何 / fixed-roll / 72 yaw × 37 pitch = 2664 姿态
- 每个姿态：camera EXR, sun EXR, linear EXR, BRDF PNG, OCS JSON, mask PNG+NPY
- Checker 17/17 PASS, 0 missing, 0 inconsistent
- 数据可作为路线一 C Phase 0 B0 稳定成果归档
```

**工程侧（R39-R41）：**

```text
- Dataset/Dataloader 可加载 PNG + 4 维 OCS，NaN/Inf 零检出
- 三模式模型 (ocs_only/image_only/joint) 前向传播可跑通
- random split (seed=42): train 2109/val 259/test 296, 无 record_id 重复
- yaw_block split (seed=42): train 0-280°/val 285-315°/test 320-355°, 无 record_id 重复
- circular yaw MAE 已实现
- 三层训练保护有效（缺 --train、epoch>30、subset 超限均阻断）
```

**训练结果侧（R42-R43）：**

E21 random-trained baseline：

| Mode | random test yaw_acc | random test pitch_acc | yaw_block test yaw_acc* |
|---|---|---|---|
| ocs_only | 8.78% | 4.39% | 5.41% |
| image_only | 81.76% | 88.51% | 77.36% |
| joint | 88.51% | 93.58% | 85.14% |

> *E21 yaw_block test 结果已被 R42/R43 判定为无效——详见 §2.1。

FIX01 strict yaw_block holdout（有效）：

| Mode | yaw_block test yaw_acc | yaw_block test pitch_acc | random test yaw_acc |
|---|---|---|---|
| ocs_only | **0.00%** | 1.01% | 10.47% |
| image_only | **0.00%** | 56.42% | 74.66% |
| joint | **0.00%** | 44.26% | 75.34% |

---

## 2. 关键判据：哪些结果能用，哪些不能

### 2.1 E21 yaw_block 结果：永久撤销

E21 报告中的 yaw_block test 结果（ocs_only yaw=5.41%, image_only yaw=77.36%, joint yaw=85.14%）**不得在任何论文、报告或后续讨论中作为泛化证据引用**。

污染根因：

```text
train = random_train (split_manifest.json)
test  = yaw_block_test (split_manifest_yaw_block.json)

random_train ∩ yaw_block_test = 230/296 (77.7%)
random_train ∩ yaw_block_val  = 204/259 (78.8%)
```

E21 模型在 yaw_block test 上看到的样本中，约 78% 已在 random_train 中见过。所谓 "跨 yaw 泛化" 实际是 memorization。

### 2.2 E21 random split 结果：可用，但范围必须限定

E21 random split 指标（image_only random test yaw=81.76%, joint random test yaw=88.51%）是有效的 **in-distribution engineering baseline**。可以引用，但必须附带以下限定：

```text
- 训练与测试来自同一 random split，姿态在 yaw 维度广泛重叠。
- 该结果反映的是同分布/近邻姿态的插值能力，不是跨未见 yaw 区间的外推能力。
- 不得表述为 "跨几何泛化" 或 "未见姿态泛化"。
```

### 2.3 FIX01 strict yaw_block 负结果：可用，是重要的边界证据

FIX01 的 yaw=0.00% 结果是一项有效且重要的负结果。它证明了当前 B0 baseline 的科学边界：

```text
当前 fixed-roll / B0 / 单视图 CNN + 4 维 OCS 配置，
不具备跨未见 yaw 区间的零样本泛化能力。
```

这个结果可以写入论文的消融分析/负结果边界/实验设计讨论，前提是正确命名（"strict yaw_block holdout"）并与 random split 结果区分。

### 2.4 Pitch 的部分可迁移性

```text
image_only: yaw_block test pitch_acc = 56.42%（vs random test 89.86%）
joint:      yaw_block test pitch_acc = 44.26%（vs random test 86.15%）
```

Pitch 在 strict yaw holdout 中仍有 44-56% 精度（远超随机基线 1/37≈2.7%），因为 pitch 在训练 yaw 区间内全覆盖（每个训练 yaw 均有全部 37 个 pitch 值）。这是可引用的正面证据，但同样需限定范围。

### 2.5 OCS 的作用边界

```text
ocs_only random test yaw_acc = 10.47%  ← 略高于随机 (1/72≈1.4%)，但不具实用价值
ocs_only yaw_block test yaw_acc = 0.00%  ← 完全随机

joint vs image_only:
  - random test: joint (yaw=88.51%) > image_only (81.76%) ← OCS 在同分布下有补充作用
  - yaw_block test: joint (yaw=0.00%, pitch=44.26%) < image_only (yaw=0.00%, pitch=56.42%)
    ← OCS 在跨 yaw 条件下反而降低了 pitch 性能
```

当前 4 维 OCS (total + 3 per-part) 在同分布条件下对 yaw 估计有适度补充作用（+6.75 pp），但在跨 yaw 条件下不提供不变性增益，反而可能引入 yaw-specific 的过拟合信号，损害了 pitch 的泛化。

---

## 3. 当前 B0 baseline 的科学边界

基于 R38-R43 全部证据，当前路线一 C B0 baseline 的科学边界如下：

```text
┌─────────────────────────────────────────────────────────────┐
│ 路线一 C Phase 0 B0 baseline 科学边界（2026-06-24）         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 成立：                                                      │
│ ✓ fullrun B0 2664 数据生成完成，checker 17/17 PASS          │
│ ✓ random split 下，image_only 和 joint 可实现 >80% yaw acc  │
│ ✓ joint 在同分布条件下优于 image_only（+6.75 pp yaw）       │
│ ✓ 训练基础设施（dataset/loader/model/checkpoint）工程可用    │
│ ✓ pitch 在 strict yaw holdout 中有部分迁移能力（~56%）      │
│                                                             │
│ 不成立：                                                    │
│ ✗ 跨未见 yaw 区间零样本泛化（三种模式 yaw_acc 均为 0.00%）  │
│ ✗ OCS 提供跨 yaw 不变性                                     │
│ ✗ joint 在跨 yaw 条件下优于 image_only                      │
│ ✗ 将 E21 yaw_block 结果称为泛化证据                         │
│                                                             │
│ 边界条件：                                                   │
│ - fixed-roll (roll=0°), B0 BRDF only, phase63 单一几何      │
│ - 单视图图像（1 个 roll 角度下的 256×256 灰度渲染图）        │
│ - 4 维 OCS（total + 3 per-part 积分光度）                   │
│ - 72 yaw × 37 pitch 分类（5° bin）                          │
│ - 简单 CNN + MLP 架构，无显式不变性设计                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. 后续路径候选

以下 4 条路径互不排斥，可以组合执行。每条均评估了目的、预期产出、代价与风险。

### 路径 A：接受 in-distribution 边界，不主张跨 yaw 泛化

```text
目的：
  以 random split 结果作为路线一 C 的核心实验证据，在论文中明确 
  fixed-roll / single-view 条件下当前 baseline 的工作范围是 
  "同分布/近邻姿态插值"，不主张跨未见 yaw 区间的零样本泛化。

具体操作：
  1. 将 E21 random split 三模式结果整理为正式实验表
  2. 将 FIX01 负结果写入消融/讨论作为边界声明
  3. 论文 claims 降级为 "同分布姿态估计" 或 "covered yaw 区间姿态识别"
  4. 不新增实验

优点：
  - 零新增计算成本
  - 证据全部已有，不依赖未验证假设
  - 科学诚实，审稿风险可控

代价/风险：
  - Claims 的 novelty 显著降低
  - 可能被认为 "只是一个渲染数据集上的分类任务"
  - 需要在论文中正面处理负结果，而非回避

是否需要 Codex 再放行：否（材料已具备，仅整理）
```

### 路径 B：多折 circular yaw block，更稳健描述泛化失败

```text
目的：
  当前 yaw_block split 只做了一折（train 0-280°, test 320-355°），
  泛化失败可能部分源于 train 只覆盖了连续的低-中 yaw 区间。
  多折 circular yaw block 可排除 "恰好某个 yaw 区间特别难" 的混淆。

具体操作：
  1. 生成 k-fold circular yaw block split（如 5 折，每折留出约 72/5≈14 个 yaw bin 作为 test）
  2. 每折训练 image_only baseline（≤20 epochs）
  3. 报告每折 strict test yaw_acc 均值与方差
  4. 若所有折 yaw≈0%，则跨 yaw 泛化失败是稳健结论
  5. 若某些折 yaw>0%，则说明泛化失败的不均匀性，可能指示新的研究方向

优点：
  - 使负结果更稳健，不依赖单折 split 的偶然性
  - 每条折成本可控（image_only only，~20 epochs on GPU ≈ 1 min/epoch）
  - 可为论文提供 "cross-validation style" 的证据强度

代价/风险：
  - 约 5× GPU 训练时间（每条折 ~20 min on RTX 5060, 总计 ~100 min）
  - 若全部失败则结果与 FIX01 一致，边际信息增益可能有限
  - 需要新增 split 生成脚本

是否需要 Codex 再放行：是（新增 split 方案和训练需 R44 审阅）
```

### 路径 C：OCS 特征工程增强，探索跨 yaw 不变性

```text
目的：
  当前 4 维 OCS (total + 3 per-part 积分光度) 在跨 yaw 条件下无帮助。
  尝试构造更具 yaw 不变性的 OCS 特征，测试能否在 strict yaw holdout 
  下实现非零泛化。

具体操作：
  1. 从现有 fullrun OCS manifest 中提取更多特征候选：
     - per-part 比率（如 jinshuzhuti/total, taiyangnengban/yinshenban）
     - 多部件对比度
     - 若有多次不同 roll 的 OCS 则加入 roll-invariant 聚合
  2. 在现有 fixed-roll 条件下测试 OCS-only 模型在 strict yaw holdout 上的表现
  3. 将有效特征加入 joint 模型，重跑 FIX01 协议

优点：
  - 直接针对当前的核心失败模式（跨 yaw 泛化）
  - 若成功，可成为论文的关键 novelty（"OCS-derived yaw-invariant features"）
  - 计算成本可控（仅 OCS-only 先探路）

代价/风险：
  - 可能仍失败——4 维 OCS 对 yaw 的敏感性可能根植于物理（部件遮挡）
  - 若无 multi-roll 数据，OCS 不变性构造空间有限
  - 成功的概率不确定

是否需要 Codex 再放行：是（新的特征工程和训练实验需审阅）
```

### 路径 D：整理当前 B0 evidence packet，然后启动 B1/GGX 规划

```text
目的：
  当前 B0 边界已经足够清晰。在投入更多 yaw 泛化实验之前，
  先以 B0 的证据包进入论文写作的实验设计章节，将随机 split 
  结果作为 Chapter 4 "Experiment Design"，将 strict yaw_block 
  负结果作为 "Limitations / Negative Results / Ablation"。
  同时启动 B1 (GGX) 数据生成的规划，让 B1 成为论文控制变量
  （B0=BRDF only vs B1=BRDF+GGX specular）。

具体操作：
  1. 整理 B0 evidence packet（R38-R43 全链证据，本报告）
  2. 起草论文实验设计章节的 B0 部分（按 24 号冻结文件结构）
  3. 规划 B1 fullrun 的数据生成方案与审阅链
  4. B1 生成完成后，在 random split 上对比 B0 vs B1
  5. B1 的 strict yaw holdout 可以作为第二组负结果/对比

优点：
  - 平衡推进实验与论文写作
  - B1 是 B0 的自然下一步（唯一区别是 BRDF 模型），控制变量设计清晰
  - 不把时间全部押在 yaw 泛化这一单一问题上

代价/风险：
  - B1 fullrun 2664 渲染成本显著（Blender 逐个姿态渲染，耗时以天计）
  - B1 仍受 fixed-roll 约束，跨 yaw 泛化失败可能重现
  - 需要新数据后才能补充论文证据

是否需要 Codex 再放行：是（B1 数据生成需要独立的审阅链）
```

---

## 5. 路径对比矩阵

| | 路径 A | 路径 B | 路径 C | 路径 D |
|---|---|---|---|---|
| **新增计算** | 无 | ~100 min GPU | 少量 GPU | B1 渲染(天级) |
| **新增代码** | 无 | split 脚本 | OCS 特征脚本 | Blender 脚本 |
| **科学增量** | 低（整理已有） | 中（稳健化负结果） | 中-高（若成功） | 高（B0 vs B1 对比） |
| **风险** | 低 | 低 | 中-高（可能仍失败） | 中（B1 可能复用 B0 问题） |
| **对论文的贡献** | 实验章+消融 | 消融章证据 | 核心 novelty | 实验章+控制变量 |
| **Codex 审阅** | 否 | 是 | 是 | 是 |

---

## 6. 建议的推进顺序

不考虑项目负责人的偏好和外部约束，从技术合理性出发的建议顺序：

```text
第一步：路径 A（立即，零成本）
  → 整理现有 B0 evidence packet 为论文可用形态
  → 写清楚 random split = in-distribution, yaw_block = failure boundary

第二步：路径 B（低成本，提高证据质量）
  → 5 折 circular yaw block，确认负结果的稳健性
  → 为论文消融章提供更完整的 cross-validation evidence

第三步（并行或择一）：路径 C 和/或路径 D
  → 若优先追求 novelty：路径 C（OCS 不变性特征探索）
  → 若优先推进论文实验完整度：路径 D（B1 GGX 对比）
  → 两条路径都需要独立的 Codex 审阅链
```

---

## 7. 红线遵守

- [x] 不写论文正文（仅整理 evidence packet 和路径选项）
- [x] 不启动新训练或大规模实验
- [x] 不启动 B1/GGX/三轴/路线二/三/四
- [x] 不改冻结文件 13/14/24/25
- [x] 不写 04_Codex审阅/
- [x] 不把 E21 泄漏结果当作泛化证据

---

## 8. 附录：R38-R43 全链产物索引

### 数据产物
```text
v0.4_results/01_fullrun/shadow_passes/          ← 2664 camera EXR + 2664 sun EXR
v0.4_results/01_fullrun/postprocess/             ← 2664 × 5 postprocess 产物
v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_fullrun.json
v0.4_results/01_fullrun/postprocess/image_manifest_v0_4_fullrun.json
v0.4_results/01_fullrun/postprocess/split_manifest.json                ← random split
v0.4_results/01_fullrun/postprocess/split_manifest_yaw_block.json      ← yaw_block split
```

### 代码产物
```text
06_v0.4_code/07_training/dataset.py              ← OCSImageDataset
06_v0.4_code/07_training/split_dataset.py        ← split 生成
06_v0.4_code/07_training/train_smoke.py          ← 基础设施 smoke
06_v0.4_code/07_training/train_baseline.py       ← E21/FIX01 训练入口（含 GPU 加速）
```

### 训练结果
```text
v0.4_results/03_training_baseline/e21_controlled_baseline/    ← E21 原结果（yaw_block 无效）
v0.4_results/03_training_baseline/e21_fix01_yawblock_strict/  ← FIX01 严格结果（有效）
```

### 审阅文件
```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
  R38_Codex_审阅_1C-E18全量通过成果归档但训练暂不放行.md
  R39_Codex_审阅_1C-E19通过并放行最小训练smoke.md
  R40_Codex_审阅_1C-E20训练smoke基础通过但暂不放行完整训练.md
  R41_Codex_审阅_1C-E20-FIX01通过并放行E21受控训练.md
  R42_Codex_审阅_1C-E21工程baseline通过但泛化结论需返工.md
  R43_Codex_审阅_1C-E21-FIX01严格泛化复评通过并要求路线决策.md
```

### Claude 执行报告
```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  39_1C-E18_全量2664生成与manifest_checker_Claude执行报告.md
  40_1C-E19_训练入口与数据切分准备_Claude执行报告.md
  41_1C-E20_最小训练smoke_Claude执行报告.md
  42_1C-E20-FIX01_训练smoke判据修正_Claude执行报告.md
  43_1C-E21_受控baseline训练与评估_Claude执行报告.md
  44_1C-E21-FIX01_yawblock严格泛化复评_Claude执行报告.md
  45_1C-E22_路线一C结果边界与后续路径裁决准备_Claude执行报告.md  ← 本报告
```
