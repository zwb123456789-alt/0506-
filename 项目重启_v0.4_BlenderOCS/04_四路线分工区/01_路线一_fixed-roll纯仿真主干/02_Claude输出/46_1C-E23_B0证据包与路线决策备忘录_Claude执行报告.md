# 46 1C-E23：B0 证据包与路线决策备忘录 Claude 执行报告

最后更新：2026-06-24  
执行端：Claude  
依据审阅：`04_Codex审阅/R44_Codex_审阅_1C-E22通过并建议进入B0证据包整理.md`

---

## 0. 备忘录定位

本文件是路线一 C Phase 0 B0 的 **stable evidence packet + route decision memorandum**。它不包含新实验、新训练或论文正文，只汇总 R38-R43 审阅链已通过的证据、划定 claim 边界、整理不可用结果黑名单，并为后续路径提供执行前置条件清单。

后续论文写作、实验设计或路线扩展，**应以本备忘录为依据**，不再追溯 R38-R43 原始审阅文件中的已撤回结论。

---

## 1. B0 Evidence Packet 索引

### 1.1 数据资产（原位，不复制）

| 资产 | 路径 | 状态 | 可用性 |
|---|---|---|---|
| Fullrun shadow passes | `v0.4_results/01_fullrun/shadow_passes/` | 2664 camera EXR + 2664 sun EXR | 稳定，可引用 |
| Postprocess 产物 | `v0.4_results/01_fullrun/postprocess/` | 5 × 2664 (linear_exr, brdf_png, ocs_json, mask_png, mask_npy) | 稳定，可引用 |
| Fullrun summary | `v0.4_results/01_fullrun/postprocess/fullrun_postprocess_summary.json` | COMPLETE, 0 blockers, 0 missing | 稳定，可引用 |
| OCS manifest | `v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_fullrun.json` | 2664 records | 稳定，可引用 |
| Image manifest | `v0.4_results/01_fullrun/postprocess/image_manifest_v0_4_fullrun.json` | 2664 records | 稳定，可引用 |
| Checker report (original) | `v0.4_results/01_fullrun/postprocess/consistency_check_report_fullrun.json` | 17/17 PASS | 稳定，可引用 |
| Checker report (Codex rerun) | `v0.4_results/01_fullrun/postprocess/consistency_check_report_fullrun_codex_rerun.json` | 17/17 PASS | 稳定，可引用 |

数据生成参数：

```text
几何：phase63
BRDF：B0 (phong-like provisional / BRDF only)
Roll：fixed at 0°
姿态网格：72 yaw × 37 pitch = 2664
yaw：0:5:355°, pitch：-90:5:+90°
```

### 1.2 Split 资产

| 资产 | 路径 | 方法 | Seed | 记录数 | 无重复 | 可用性 |
|---|---|---|---|---|---|---|
| Random split | `split_manifest.json` | random stratified-by-pitch | 42 | 2664 | yes | 工程 baseline / sanity |
| Yaw block split | `split_manifest_yaw_block.json` | yaw_block | 42 | 2664 | yes | 严格泛化评估 |

Yaw block split 划分：

```text
train: yaw 0–280° (57 unique, 2109 records)
val:   yaw 285–315° (7 unique, 259 records)
test:  yaw 320–355° (8 unique, 296 records)
train ∩ val = 0, train ∩ test = 0, val ∩ test = 0
```

### 1.3 代码资产

| 资产 | 路径 | 状态 | 可用性 |
|---|---|---|---|
| Dataset loader | `06_v0.4_code/07_training/dataset.py` | 三模式 (ocs_only/image_only/joint) | 稳定 |
| Split 生成 | `06_v0.4_code/07_training/split_dataset.py` | random + yaw_block | 稳定 |
| Smoke 测试 | `06_v0.4_code/07_training/train_smoke.py` | infra/perf 已拆分 | 稳定 |
| Baseline 训练 | `06_v0.4_code/07_training/train_baseline.py` | E21/FIX01 入口，含 GPU 加速与 overlap 检查 | 稳定 |
| Model 架构 | 同上文件内 | ImageEncoder (CNN) + OCSEncoder (MLP) + OCSImageModel | 工程可用 |

### 1.4 训练结果资产

| 资产 | 路径 | 协议 | 可用性 | 备注 |
|---|---|---|---|---|
| E21 random baseline | `v0.4_results/03_training_baseline/e21_controlled_baseline/` | random train | 工程 baseline 可用 | yaw_block 结果不可用 |
| FIX01 strict holdout | `v0.4_results/03_training_baseline/e21_fix01_yawblock_strict/` | yaw_block train | 全部可用 | 负结果，边界证据 |

### 1.5 审阅链资产

| Codex 审阅 | 路径 | 裁决 | 关联数据 |
|---|---|---|---|
| R38 | `04_Codex审阅/R38_Codex_审阅_1C-E18全量通过成果归档但训练暂不放行.md` | PASS | fullrun 2664 data |
| R39 | `04_Codex审阅/R39_Codex_审阅_1C-E19通过并放行最小训练smoke.md` | PASS | dataset, split, smoke |
| R40 | `04_Codex审阅/R40_Codex_审阅_1C-E20训练smoke基础通过但暂不放行完整训练.md` | 条件通过 | smoke criteria fix needed |
| R41 | `04_Codex审阅/R41_Codex_审阅_1C-E20-FIX01通过并放行E21受控训练.md` | PASS | yaw_block split, E21 released |
| R42 | `04_Codex审阅/R42_Codex_审阅_1C-E21工程baseline通过但泛化结论需返工.md` | 工程 PASS / 泛化 FAIL | E21 leakage diagnosis |
| R43 | `04_Codex审阅/R43_Codex_审阅_1C-E21-FIX01严格泛化复评通过并要求路线决策.md` | PASS (负结果) | FIX01 strict holdout |
| R44 | `04_Codex审阅/R44_Codex_审阅_1C-E22通过并建议进入B0证据包整理.md` | PASS | E22 route decision prep |

### 1.6 Claude 执行报告资产

```text
02_Claude输出/39_1C-E18_全量2664生成与manifest_checker_Claude执行报告.md
02_Claude输出/40_1C-E19_训练入口与数据切分准备_Claude执行报告.md
02_Claude输出/41_1C-E20_最小训练smoke_Claude执行报告.md
02_Claude输出/42_1C-E20-FIX01_训练smoke判据修正_Claude执行报告.md
02_Claude输出/43_1C-E21_受控baseline训练与评估_Claude执行报告.md
02_Claude输出/44_1C-E21-FIX01_yawblock严格泛化复评_Claude执行报告.md
02_Claude输出/45_1C-E22_路线一C结果边界与后续路径裁决准备_Claude执行报告.md
02_Claude输出/46_1C-E23_B0证据包与路线决策备忘录_Claude执行报告.md  ← 本报告
```

---

## 2. 可用结果表（Verified / Citable）

以下结果已经 Codex 审阅通过，可在后续论文实验设计、消融与边界讨论中引用——**在正确限定范围内**。

### 2.1 E21 Random Split Baseline（in-distribution）

协议：random train → random val / random test。训练 20 epochs, lr=1e-3, seed=42, CPU。

| Mode | yaw_acc | pitch_acc | yaw_circular_mae |
|---|---|---|---|
| ocs_only | 8.78% | 4.39% | — |
| image_only | 81.76% | 88.51% | 9.3° (FIX01 run) |
| joint | 88.51% | 93.58% | 11.6° (FIX01 run) |

引用限定：

```text
✓ "random split 同分布条件下，joint 模型达到了 88.5% yaw accuracy"
✓ "image_only 与 joint 在 in-distribution 测试中均可学习 fixed-roll 姿态映射"
✓ "joint 在同分布条件下 yaw_acc 比 image_only 高 6.75 pp"
✗ 不得表述为 "跨几何泛化" 或 "未见姿态泛化"
```

### 2.2 FIX01 Strict Yaw-Block Holdout（valid negative result）

协议：yaw_block train (0–280°) → yaw_block test (320–355°)。训练 20 epochs, lr=1e-3, seed=42, CPU。

| Mode | yaw_acc | pitch_acc | yaw_circular_mae |
|---|---|---|---|
| ocs_only | 0.00% | 1.01% | 98.3° |
| image_only | 0.00% | 56.42% | 41.0° |
| joint | 0.00% | 44.26% | 41.6° |

引用限定：

```text
✓ "严格 yaw_block holdout 下，当前 baseline 无法泛化到未见 yaw 区间 (320–355°)"
✓ "pitch 在未见 yaw 区间仍有 56.4% 精度，表明 pitch 信息可部分跨 yaw 迁移"
✓ "当前 4 维 OCS 特征不提供跨 yaw 不变性"
✗ 不得表述为 "OCS 提升跨 yaw 泛化"
✗ 不得表述为 "joint 在 yaw_block 上优于 image_only"
```

### 2.3 工程链可用性

```text
✓ Dataset/Dataloader：2664 records 可正常加载，NaN/Inf 零检出
✓ 三模式模型：前向/反向传播正常，梯度有限
✓ Checkpoint：保存/加载可工作
✓ Circular yaw MAE：已实现
✓ Overlap check：内置验证，train/val/test record_id 无重复
✓ GPU 加速：CUDA + 4 workers + pin_memory 可用
```

---

## 3. 不可用 / 撤回结果表（Blacklist）

以下结果**永久撤回**，不得在论文、报告或后续讨论中作为证据引用。

| 撤回项 | 来源 | 撤回原因 | Codex 依据 |
|---|---|---|---|
| E21 yaw_block test yaw_acc (所有模式) | `e21_controlled_baseline/` | random_train ∩ yaw_block_test = 77.7% record_id 重叠 | R42, R43 |
| "OCS 显著提升跨 yaw 几何泛化" | E21 报告 | train-test 泄漏伪影 | R42 |
| "joint 比 image_only 在 yaw_block 上高 7.78 pp" | E21 报告 | 同上 | R42 |
| "yaw_block split 为严格泛化评估" (指 E21 协议) | E21 报告 | E21 未用 yaw_block train，随机 train 在 yaw_block test 上评估不是严格泛化 | R42 |

**使用规则**：E21 `e21_controlled_baseline/` 目录中的 random split 结果仍可使用（见 §2.1），但同目录下的所有 yaw_block 指标均为无效。引用 E21 结果时，必须明确标注 "random split, in-distribution only"。

---

## 4. 当前可写 Claim 与禁止 Claim

### 4.1 可写 Claim（需附带限定语）

```text
C1. "在 model-known / fixed-roll / B0 条件下，基于单视图 CNN 的方法可在 
    random split 同分布测试中实现 >80% yaw accuracy。"
    限定：只适用 random split，不推广到未见 yaw 区间。

C2. "Joint (image + 4-dim OCS) 在同分布条件下优于 image_only，yaw_acc 
    提升约 6.8 pp。"
    限定：提升幅度只在 random split 下成立；strict holdout 下无此优势。

C3. "Pitch 估计在 strict yaw_block holdout 中仍有部分可迁移能力（56.4%），
    说明 pitch 信息比 yaw 信息更少依赖训练 yaw 覆盖。"
    限定：56.4% 远低于 random split 的 89.9%，不可表述为 "稳健泛化"。

C4. "当前 4 维 OCS (total + 3 per-part) 在 fixed-roll 单视图条件下不提供
    跨未见 yaw 区间的零样本泛化信息。"
    限定：明确是 "fixed-roll 单视图" 和 "4 维积分 OCS"，不是对所有 OCS 
    通道的否定。多 roll / 多观测 / 角度分辨 OCS 可能有不同表现。

C5. "在 B0 / phase63 / 72 yaw × 37 pitch / 2664 姿态的 full-run 数据生成
    中，checker 17/17 项全部通过。"
    无需限定（纯数据工程陈述）。
```

### 4.2 禁止 Claim

```text
X1. "OCS 通道显著提升跨 yaw 几何泛化能力"          ← R42/R43 已证伪
X2. "joint 模型在未见 yaw 区间上优于 image_only"    ← FIX01 负结果
X3. "本方法具备跨几何泛化能力"                      ← 当前无证据
X4. "E21 yaw_block 结果证明……"                      ← 泄漏伪影
X5. "4 维 OCS 提供姿态不变性特征"                   ← FIX01 负结果
X6. "本系统可推广到真实望远镜观测"                   ← 超出 B0 baseline 范围
X7. 任何未标注 "in-distribution only" 的 yaw 泛化声称
X8. 任何将 B1 等同于 GGX 的表述                      ← R44 纠正
```

---

## 5. 后续路径执行前置条件

基于 E22 的四条路径，按 R44 要求将路径 D 拆分为 D1 和 D2。每条路径标注了执行前必须满足的条件和 Codex 放行状态。

### 路径 A：B0 evidence packet 整理（当前阶段）

```text
状态：EXECUTING（本报告即为路径 A 产出）
下一步：本备忘录完成后，路径 A 即闭合
需要 Codex 放行：否（已在 R44 放行范围内）
```

### 路径 B：多折 circular yaw block

```text
目的：将单折 yaw_block 负结果扩展为 k-fold cross-validation，排除单折偶然性
执行内容：
  1. 生成 k-fold circular yaw block split（建议 k=5）
  2. 每折训练 image_only baseline（≤20 epochs）
  3. 报告 per-fold strict test 指标（均值 ± 标准差）
产出：
  - 新的 split manifest(s)
  - per-fold 训练结果 JSON
  - 汇总报告
前置条件：
  P1. 本备忘录（路径 A）完成
  P2. split 生成脚本通过 Codex 审阅
  P3. 训练协议（epoch 上限、配置固定）通过 Codex 审阅
需要 Codex 放行：是（需 R45 审阅 split 方案与训练协议）
预计计算成本：~100 min GPU (RTX 5060)
风险：若全部 k 折 yaw≈0%，边际信息增益有限
```

### 路径 C：OCS 特征增强探索

```text
目的：从现有 OCS manifest 构造更具 yaw 不变性的特征
执行内容：
  1. 从 fullrun OCS manifest 提取 per-part 比率、对比度等候选特征
  2. 在 OCS-only 模型上测试 strict yaw_block holdout
  3. 若某特征组合 yaw_acc > 0%，加入 joint 模型复验
产出：
  - 新 OCS 特征定义与提取脚本
  - OCS-only / joint yaw_block 评估结果
前置条件：
  P1. 本备忘录完成
  P2. 特征设计方案通过 Codex 审阅（明确哪些特征、为何可能具备不变性）
  P3. 特征提取脚本通过 Codex 审阅
需要 Codex 放行：是（需 R46 审阅特征方案）
预计计算成本：少量 GPU（OCS-only 训练极快）
风险：fixed-roll 条件下 4 维 OCS 的 yaw 敏感性可能根植于物理（部件遮挡），
      增强特征的改进空间有限
```

### 路径 D1：B1 书中改进冯模型 fullrun

```text
目的：B0 (phong-like BRDF only) 与 B1 (书中改进冯模型) 的控制变量对比
执行内容：
  1. 确认 B1 材料参数（与三部件对应）
  2. 设计 B1 Blender 渲染方案
  3. 生成 B1 fullrun 2664（或与 B0 相同的姿态网格）
  4. 在 random split 和 strict yaw_block 上对比 B0 vs B1
产出：
  - B1 fullrun 数据（shadow passes + postprocess）
  - B1 manifest / checker
  - B0 vs B1 对比实验结果
前置条件：
  P1. 本备忘录完成
  P2. B1 材料参数确认（需与书中数据对应，三部件分别赋值）
  P3. Blender 渲染方案通过 Codex 审阅
  P4. 渲染完成后的 checker 通过 Codex 审阅（类似 R38 流程）
  P5. B0 vs B1 对比训练协议通过 Codex 审阅
需要 Codex 放行：是（需多轮审阅：方案 → 渲染 → checker → 训练对比）
预计计算成本：Blender 逐姿态渲染，2664 姿态预计以天计
风险：B1 仍受 fixed-roll 约束，跨 yaw 泛化失败可能重现；
      B1 材料参数若不准确，对比的科学价值下降
术语红线：B1 是 "书中改进冯模型"，不可写成 GGX
```

### 路径 D2：GGX 或其他 BRDF mismatch 对照

```text
目的：B0 (phong-like) 与 GGX (或其他 BRDF) 的错配对照实验
执行内容：
  1. 选择 GGX 参数（或与 B0 形成明确 mismatch）
  2. 生成 GGX fullrun（规模可小于 2664，如 subset）
  3. 对比 B0 模型在 GGX 数据上的性能衰减
产出：
  - GGX fullrun/subset 数据
  - B0→GGX 跨 BRDF 泛化评估
前置条件：
  P1. 本备忘录完成
  P2. GGX 参数和渲染方案通过 Codex 审阅
  P3. 如需新 Blender 材质节点，需独立验证
需要 Codex 放行：是（独立的审阅链，与 D1 分开）
预计计算成本：取决于 fullrun 还是 subset
风险：GGX 不是路线一 C 的主线（24 号冻结文件以 B0/B1 为主线）；
      GGX 对照的科学价值需要在审阅阶段单独论证
术语红线：GGX 不等于 B1，不可混写为 "B1/GGX"
```

---

## 6. 后续路径推荐顺序

基于 B0 证据包现状，Codex 与 Claude 达成一致的推荐：

```text
当前阶段（路径 A）：已完成
  → 本备忘录闭合路径 A

推荐下一步（路径 B）：
  → 低成本稳健化负结果，5 折 circular yaw block 确认为后续论文消融章提供
    cross-validation 级证据
  → 若项目负责人决定不投入 yaw 泛化方向，可跳过 B 直接进入 D1 论文主线

然后（路径 D1 为主，路径 C 为可选）：
  → D1 是 24 号冻结文件的主线对比（B0 vs B1），优先级高于 C 和 D2
  → C 是 novelty 探索，若成功则显著提升论文贡献，但成功概率不确定
  → D2 是远期对照，不急于在当前阶段启动

已排除的组合：
  ✗ 同时启动 B + C + D1 + D2（资源不足，审阅链过载）
  ✗ 跳过 B 直接写论文正文（claims 边界尚未被后续路径验证）
  ✗ 在未修正 B1/GGX 术语前启动 D（R44 明确禁止）
```

---

## 7. 红线确认

- [x] 不写论文正文
- [x] 不启动新训练或实验
- [x] 不启动 B1/GGX/三轴/路线二/三/四
- [x] 不改冻结文件 13/14/24/25
- [x] 不写 04_Codex审阅/
- [x] 不把 B1 与 GGX 混写（路径 D 已拆分为 D1/D2）
- [x] 不把 E21 泄漏结果当泛化证据（已列入 §3 黑名单）

---

## 附录 A：全链 Codex 审阅裁决速查

| Codex | 任务 | 裁决 |
|---|---|---|
| R38 | 全量 2664 数据生成 | PASS |
| R39 | 训练入口 + 数据切分 | PASS |
| R40 | 训练 smoke 初版 | 条件通过 |
| R41 | smoke 判据修正，E21 放行 | PASS |
| R42 | E21 baseline | 工程 PASS / 泛化 FAIL |
| R43 | FIX01 strict yaw_block 复评 | PASS (负结果) |
| R44 | E22 路线决策准备 | PASS |
| R45 | (待执行) B0 evidence packet | — |

## 附录 B：E21 泄漏诊断速查

```text
random_train ∩ yaw_block_train = 1672/2109 (79.3%)
random_train ∩ yaw_block_val   = 204/259  (78.8%)
random_train ∩ yaw_block_test  = 230/296  (77.7%)

→ E21 模型在 yaw_block test 上见过的 78% 样本已在训练集中
→ E21 yaw_block 结果不是泛化证据，是 memorization 伪影
```
