# 51 1C-E27：论文实验设计规划与后续路线优先级 Claude 执行报告

最后更新：2026-06-25  
执行端：Claude  
依据审阅：`04_Codex审阅/R50_Codex_审阅_1C-E26通过并放行E27实验设计规划.md`

**状态：纯设计规划。不训练、不改代码、不改数据、不写论文正文、不放行任何方向执行。**

---

## 0. 规划摘要

```text
本报告是路线一 C Phase 0 的论文实验章设计规划。
基于 R38→R48 十轮 Codex 审阅已闭合的 B0 baseline 证据链，
规划实验章结构、B0 证据到图表/表格/source-data 的映射，
标出 D1/C/D2 的证据缺口，并给出后续优先级建议。

本报告不是论文正文。所有章节标题、表格设计和图表描述
均为规划级草案，需要在后续 Codex 审阅中逐项确认后，
才能进入正文写作阶段。
```

---

## 1. 论文实验章结构设计（规划草案）

### 1.1 当前可规划的实验章结构

基于 v0.4 主线定位——"model-known 条件下，独立 OCS 光度通道与图像成像通道共享同一物理前向模型时，跨几何 OCS 多观测光度向量与图像通道对姿态信息的可观测性、互补性和置信一致性研究"——实验章建议分为以下模块：

```text
Experiment Section（论文实验部分）规划结构：

§E.1  实验设置与数据生成
  §E.1.1  仿真平台与物理前向模型
  §E.1.2  姿态网格与数据规模
  §E.1.3  数据质量验证（checker）

§E.2  单视图图像通道的姿态估计基线
  §E.2.1  模型架构与训练协议
  §E.2.2  同分布基线结果（random split）
  §E.2.3  跨 yaw 泛化评估（strict yaw-block holdout）
  §E.2.4  5-fold circular yaw-block cross-validation

§E.3  OCS 光度通道的信息贡献
  §E.3.1  OCS-only 姿态估计能力
  §E.3.2  Image+OCS 联合估计与通道互补性
  §E.3.3  OCS 特征的 yaw 不变性分析

§E.4  消融与边界分析
  §E.4.1  训练/测试分布偏移的影响
  §E.4.2  Pitch vs Yaw 的可迁移性差异
  §E.4.3  单视图 fixed-roll 条件的固有限制

§E.5  [待补] BRDF 材料参数对比（B0 vs B1）
  → 依赖 D1 执行

§E.6  [待补] OCS 特征增强与不变性探索
  → 依赖 C 执行
```

### 1.2 章节状态标注

| 章节 | 状态 | B0 证据覆盖 | 需要新实验 |
|------|------|------------|-----------|
| §E.1 实验设置与数据生成 | **可规划** | ✓ 完整 (R38) | 否 |
| §E.2.1 模型架构与训练协议 | **可规划** | ✓ 完整 (R39/R41) | 否 |
| §E.2.2 同分布基线 | **可规划** | ✓ 完整 (R42) | 否 |
| §E.2.3 跨 yaw 泛化单折 | **可规划** | ✓ 完整 (R43) | 否 |
| §E.2.4 5-fold CV | **可规划** | ✓ 完整 (R48) | 否 |
| §E.3.1 OCS-only | **可规划** | ✓ 完整 (FIX01) | 否 |
| §E.3.2 Image+OCS joint | **可规划** | ✓ 完整 (R42/FIX01) | 否 |
| §E.3.3 OCS yaw 不变性 | **可规划** | ✓ 完整 (FIX01 负结果) | 否 |
| §E.4 消融与边界 | **可规划** | ✓ 完整 | 否 |
| §E.5 B0 vs B1 对比 | **仅框架** | ✗ 无 B1 数据 | **是 (D1)** |
| §E.6 OCS 特征增强 | **仅框架** | ✗ 无增强实验 | **是 (C)** |

---

## 2. B0 证据到实验章/图表/表格/Source-Data 映射

### 2.1 总映射表

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                B0 证据 → 论文实验章 映射表（规划草案）                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ 表 T1：数据生成参数与 checker 结果                                            │
│   章节：§E.1                                                               │
│   内容：姿态网格 (72 yaw × 37 pitch = 2664)、BRDF (B0 phong-like)、          │
│         phase63、fixed-roll、渲染通道列表                                     │
│   Source data：                                                              │
│     → v0.4_results/01_fullrun/postprocess/fullrun_postprocess_summary.json   │
│     → v0.4_results/01_fullrun/postprocess/                                   │
│       consistency_check_report_fullrun_codex_rerun.json                       │
│   形式：表格（参数列表 + PASS/FAIL 状态）                                      │
│                                                                              │
│ 表 T2：同分布 baseline 结果（三模式对比）                                       │
│   章节：§E.2.2 / §E.3.1 / §E.3.2                                           │
│   内容：random split 下 image_only / ocs_only / joint 的                      │
│         yaw_acc、pitch_acc、yaw_circular_mae                                  │
│   Source data：                                                              │
│     → v0.4_results/03_training_baseline/e21_controlled_baseline/              │
│       (random split 部分，非 yaw_block 部分)                                   │
│     → v0.4_results/03_training_baseline/e21_fix01_yawblock_strict/            │
│       (FIX01 random test 指标)                                                │
│   形式：表格（3 mode × 3 metric，标注 "random split, in-distribution only"）   │
│   引用限定：必须标注 "同分布测试，不反映跨 yaw 泛化能力"                         │
│                                                                              │
│ 表 T3：strict yaw-block holdout 结果（单折 + 5 折汇总）                        │
│   章节：§E.2.3 / §E.2.4                                                     │
│   内容：                                                                    │
│     (a) 单折 strict yaw_block：三模式 yaw_acc / pitch_acc / yaw_cmae         │
│     (b) 5-fold circular yaw_block：yaw_acc mean ± std, pitch_acc mean ± std  │
│   Source data：                                                              │
│     → v0.4_results/03_training_baseline/e21_fix01_yawblock_strict/            │
│     → v0.4_results/03_training_baseline/e25_multifold_yawblock/               │
│       e25_multifold_summary.json                                              │
│   形式：表格（3 mode × 单折指标 + 5-fold aggregate row for image_only）       │
│   引用限定：不得写成 "泛化证据"；明确这是 "跨 yaw 泛化失败" 的稳健负结果        │
│                                                                              │
│ 图 F1：5-fold yaw block 划分示意图                                             │
│   章节：§E.2.4                                                             │
│   内容：circular yaw 轴上 5 折 test bin 分布（72 bins, 每折 14-15 bins,       │
│         跨折 0 重叠）                                                         │
│   Source data：                                                              │
│     → v0.4_results/03_training_baseline/e25_multifold_yawblock/               │
│       e25_overlap_report.json (per-fold test_yaw_bins)                        │
│   形式：示意图/堆叠色块图（yaw 0-355°, 5 种颜色标注 fold 0-4 test 区间）       │
│                                                                              │
│ 图 F2：per-fold yaw_acc 柱状图（全零 + 误差棒）                                 │
│   章节：§E.2.4                                                             │
│   内容：5 折 yaw_acc 均 = 0.00%，标注 random split 对照线 (~65-75%)           │
│   Source data：                                                              │
│     → e25_multifold_summary.json (per_fold.*.test_primary.yaw_acc)            │
│     → e25_multifold_summary.json (per_fold.*.test_random.yaw_acc) 作对照      │
│   形式：分组柱状图（strict test vs random test, 5 folds）                      │
│                                                                              │
│ 图 F3：per-fold pitch_acc 柱状图                                               │
│   章节：§E.2.4 / §E.4.2                                                     │
│   内容：5 折 pitch_acc (13.5%-30.5%)，标注 random split 对照 (~71-77%)        │
│   Source data：                                                              │
│     → e25_multifold_summary.json (per_fold.*.test_primary.pitch_acc)          │
│     → e25_multifold_summary.json (per_fold.*.test_random.pitch_acc) 作对照    │
│   形式：分组柱状图                                                             │
│                                                                              │
│ 表 T4：yaw_block holdout 下 pitch 可迁移性分析                                  │
│   章节：§E.4.2                                                             │
│   内容：random split pitch_acc vs strict yaw_block pitch_acc 对比，           │
│         单折 + 5 折汇总，退化幅度分析                                          │
│   Source data：同 T2 + T3 的 pitch 指标                                       │
│   形式：表格（pitch_acc drop from random to strict, per mode）                 │
│                                                                              │
│ 表 T5：训练工程指标（附录）                                                      │
│   章节：附录                                                                  │
│   内容：模型参数量 (3.8M)、训练时间、GPU 配置、epoch 数、                       │
│         overlap 检查结果、checker 17/17 明细                                  │
│   Source data：                                                              │
│     → e25_multifold_summary.json (per_fold.elapsed_s, config)                 │
│     → e25_overlap_report.json (overall_strict: true)                          │
│     → consistency_check_report_fullrun_codex_rerun.json (17 items)            │
│   形式：表格                                                                  │
│                                                                              │
│ 表 T6：不可用结果黑名单（不进入正文，仅备 Codex 审阅对照）                        │
│   章节：不进入论文                                                            │
│   内容：E21 yaw_block 泄漏结果 (77.7% train-test overlap)、                   │
│         撤回的泛化 claim                                                      │
│   用途：确保论文中不会意外引用已撤回结果                                         │
│   Source data：E23 备忘录 §3                                                  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Source-Data 索引（固定路径，供论文写作时引用）

```text
数据生成侧：
  v0.4_results/01_fullrun/postprocess/fullrun_postprocess_summary.json
  v0.4_results/01_fullrun/postprocess/consistency_check_report_fullrun_codex_rerun.json
  v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_fullrun.json
  v0.4_results/01_fullrun/postprocess/image_manifest_v0_4_fullrun.json

Split 资产：
  v0.4_results/01_fullrun/postprocess/split_manifest.json              (random)
  v0.4_results/01_fullrun/postprocess/split_manifest_yaw_block.json    (strict single-fold)

训练结果侧：
  v0.4_results/03_training_baseline/e21_controlled_baseline/           (random split results)
  v0.4_results/03_training_baseline/e21_fix01_yawblock_strict/         (strict single-fold)
  v0.4_results/03_training_baseline/e25_multifold_yawblock/            (5-fold CV)
    ├── e25_multifold_summary.json                                     (聚合指标)
    └── e25_overlap_report.json                                        (overlap 证据)

代码资产（附录引用）：
  06_v0.4_code/07_training/dataset.py                                  (Dataset/Dataloader)
  06_v0.4_code/07_training/split_dataset.py                            (split 生成)
  06_v0.4_code/07_training/train_baseline.py                           (训练入口 + 模型)
```

---

## 3. 证据缺口分析：D1 / C / D2 分别补什么

### 3.1 缺口总览

```text
当前 B0 证据覆盖的实验章：§E.1 — §E.4（完整）
当前 B0 证据未覆盖的实验章：§E.5（B0 vs B1 对比）、§E.6（OCS 特征增强）

三项后续方向各自填补的缺口：
  D1 (B1 fullrun)：    §E.5 的 BRDF 材料参数控制变量对比
  C (OCS 特征增强)：    §E.6 的 OCS 派生特征不变性探索
  D2 (GGX mismatch)：   §E.5 的远期扩展对照（非主干，优先级低）
```

### 3.2 方向 D1：B1 书中改进冯模型 fullrun / 对比

```text
填补的论文缺口：
  G1. B0 为 phong-like 工程 BRDF，论文 Method 章若以 B1（书中改进冯模型）
      为主线，则实验章缺少 B1 自身的 baseline 结果。
      → D1 填补 B1 的 random split baseline + strict yaw_block holdout。

  G2. B0 vs B1 的控制变量对比是论文核心消融之一：
      "BRDF 从简化 phong-like 变为书中改进冯模型后，图像通道的姿态
       映射特性是否改变？跨 yaw 泛化失败是否 BRDF 依赖？"
      → D1 填补这一控制变量对比。

  G3. 若 D1 发现 B1 的 yaw 泛化模式与 B0 显著不同（如 yaw_acc > 0%
      在 strict holdout 下），则 B1 本身成为重要正结果，可能改变
      论文叙事重心。
      → D1 填补"B0 负结果是否为 BRDF 简化所致"的排除性证据。

当前状态：NOT RELEASED
需要的新资产：
  - B1 材料参数确认文档（三部件分别对应书中数据）
  - B1 Blender 渲染方案 + 试渲染
  - B1 fullrun 2664（或 686 subset）shadow passes + postprocess
  - B1 checker report
  - B1 random split + strict yaw_block 训练结果
预计新增图表：
  - 表：B0 vs B1 材料参数对照
  - 表：B1 random split baseline（同 T2 格式）
  - 表：B1 strict yaw_block holdout（同 T3 格式）
  - 图：B0 vs B1 yaw_acc/pitch_acc 对比柱状图
```

### 3.3 方向 C：OCS 特征增强探索

```text
填补的论文缺口：
  G4. 当前 §E.3.3 的结论是"4 维积分 OCS 在 fixed-roll 单视图下不提供
      跨 yaw 不变性"。这是一个限定很强的负结果——它只否定了最简单的
      4 维积分 OCS，但未探索是否存在派生特征（per-part 比率、归一化、
      对比度等）可恢复部分跨 yaw 信息。
      → C 填补"OCS 不变性是否可通过特征工程改善"的探索性证据。

  G5. 若 C 发现某派生特征组合在 OCS-only strict holdout 下 yaw_acc > 0%，
      则可进入 joint 复验，确认图像+增强 OCS 联合是否能突破当前的
      yaw=0% 天花板。
      → C 填补"OCS 通道在 fixed-roll 下是否仍有未利用的姿态信息"。

  G6. 若 C 的所有尝试均 yaw_acc = 0%，则 §E.3.3 的负结果从
      "4 维积分 OCS 不提供" 升级为 "在合理特征工程范围内，OCS 在
      fixed-roll 单视图下不提供跨 yaw 不变性"——更强的边界结论。
      → 无论 C 成功与否，都是可发表的证据。

当前状态：NOT RELEASED
需要的新资产：
  - OCS 派生特征设计方案（Codex 审阅）
  - 特征提取脚本
  - OCS-only 筛选实验结果（strict yaw_block）
  - 若有候选特征 yaw_acc > 0%：joint 复验结果
预计新增图表：
  - 表：候选 OCS 派生特征列表与定义
  - 表/图：OCS-only 各特征组合 strict holdout 结果
  - （若成功）图：enhanced joint vs baseline joint 对比
```

### 3.4 方向 D2：GGX 或其他 BRDF mismatch 对照

```text
填补的论文缺口：
  G7. B0→GGX 跨 BRDF 泛化评估：若 B0 模型在 GGX 数据上性能显著下降，
      进一步确认图像通道的姿态映射对 BRDF 敏感。
      → D2 填补 BRDF mismatch 的系统性证据。

  G8. D2 与 D1 形成 BRDF 维度的完整对比矩阵：
      B0 (phong-like) → B1 (改进冯) → GGX (通用 microfacet)
      → D2 填补第三个 BRDF 数据点

当前状态：远期方向，NOT RELEASED
优先级：低于 D1 和 C
注意：D2 不是路线一 C 的主干（24 号冻结文件以 B0/B1 为主线），
      其科学价值需要在 Codex 审阅阶段单独论证。
预计新增图表：
  - 表：B0/GGX BRDF 参数对照
  - 图：B0 model on GGX data 性能衰减曲线
```

---

## 4. 后续路线优先级建议

### 4.1 推荐顺序

```text
优先级排序（从高到低）：

  P1 [当前]  E27 论文实验设计规划 → 本报告
             产出：实验章结构草案 + B0 证据映射 + 缺口分析
             下一步：本报告提交 Codex 审阅（R51）

  P2 [建议]  C：OCS 特征增强探索
             理由：
               - 零新渲染成本，仅使用现有 B0 fullrun OCS manifest
               - 计算开销极小（OCS-only 训练 ~40s/epoch on CPU）
               - 无论成败均产生可发表证据
               - 若成功，显著提升论文 novelty
               - 可在 D1 渲染期间并行进行
               - 为 D1 的 B1 fullrun 争取时间窗口
             前置条件：
               - E27 通过 Codex 审阅
               - C 的特征设计方案通过独立 Codex 审阅
             红线：
               - 不放行 B1/GGX 执行
               - 不把 C 的特征探索写成 "已找到 yaw-invariant OCS"
               - 不修改冻结文件

  P3 [建议]  D1：B1 书中改进冯模型 fullrun / 对比
             理由：
               - B1 是 24 号冻结文件的主线对比，论文 Method 章的核心支撑
               - B0 vs B1 控制变量对比是论文实验完整度的必需要素
               - 但渲染成本高（天级），需多轮 Codex 审阅
             前置条件：
               - E27 通过 Codex 审阅
               - B1 材料参数确认
               - Blender 渲染方案 + 试渲染通过 Codex 审阅
               - （建议）C 已完成，避免 B1 渲染期间实验章设计仍存不确定性
             红线：
               - B1 ≠ GGX，不可混写
               - B1 渲染前必须完成材料参数确认和渲染方案审阅
               - 不把 B1 写成 "真实材料"，明确是 "书中改进冯模型"

  P4 [远期]  D2：GGX / BRDF mismatch 对照
             理由：
               - 非主干方向，优先级低于 D1
               - 科学价值需单独论证
               - 论文主体可在 B0 + B1 + C 基础上完成
             前置条件：
               - D1 完成且论文实验章主体确定
               - 单独的 Codex 审阅论证科学价值
             红线：
               - GGX ≠ B1
               - 不阻塞论文主体闭合
```

### 4.2 推荐理由的详细论证

```text
为什么建议 P2=C 先于 P3=D1：

  1. 时间利用效率：
     D1 需要 Blender 逐姿态渲染 2664 帧，以天为单位。
     在此期间 Claude/Codex 不应空转等待。
     C 可在 D1 渲染期间完成，两者可并行推进。

  2. 论文设计的信息增益：
     C 的结果（无论正负）直接影响 §E.3.3 和 §E.6 的边界结论强度。
     若 C 找到有效 OCS 派生特征，论文的 contribution 显著提升；
     若 C 确认无效，§E.3.3 的负结果边界更清晰，论文仍然完整。
     先做 C 可避免 D1 完成后才发现实验章还缺 OCS 维度证据。

  3. 风险控制：
     C 是低成本探索——如果失败（最可能的结果），损失极小
     （<1h 计算 + 一轮 Codex 审阅）。
     D1 是高成本投入——如果 B1 材料参数不准确或渲染出问题，
     返工成本高。先完成 C 可为 D1 争取更多方案审阅时间。

  4. 不互斥：
     C 和 D1 不是二选一。C 完成后进入 D1，两者的证据共同
     支撑论文实验章。D2 作为远期方向不阻塞主体闭合。

为什么 D1 仍是必做（P3 而非取消）：

  - 24 号冻结文件明确 B1 为论文 Method 优先目标
  - B0 only 的论文缺少 BRDF 参数维度的控制变量对比
  - 若只有 B0 结果，Method 章的 B1 改进冯模型将没有
    对应的实验证据——这是论文结构的重大缺口

为什么 D2 是远期：

  - GGX 对照的科学价值远低于 B0 vs B1（B0 已经是 GGX 的
    近似简化，B0 vs B1 已经覆盖了 BRDF 对比维度）
  - 24 号冻结文件以 B0/B1 为主线，GGX 仅为侧枝
  - 不应让 D2 分散 D1 的资源
```

### 4.3 不放行的方向

```text
以下方向本次 E27 不放行，必须在各自独立 Codex 审阅链通过后才能执行：

  ✗ C：OCS 特征增强实验（需独立 Codex 审阅特征方案）
  ✗ D1：B1 fullrun 渲染（需独立 Codex 审阅材料参数 + 渲染方案）
  ✗ D2：GGX mismatch 对照（需独立 Codex 审阅科学价值论证）
  ✗ 论文正文写作（需 E27 通过 + C/D1 闭合后，再启动正文写作审阅链）
  ✗ B1/GGX 渲染
  ✗ 三轴小项目
  ✗ 路线二/三/四扩展
  ✗ joint 5-fold（R50 Q3 已裁决 NOT RELEASED）
  ✗ OCS-only 5-fold（R50 Q3 已裁决 NOT RELEASED）
  ✗ 修改冻结文件、成果区或 CLAUDE.md
```

---

## 5. 待 Codex 裁决的问题

本报告提出以下问题供 R51 Codex 审阅裁决：

```text
Q_E27_1：论文实验章结构（§1.1）是否合理？
  是否需要调整章节顺序、合并/拆分某些节？
  是否需要增加或删减某些实验模块？

Q_E27_2：B0 证据映射（§2）是否完整？
  是否有遗漏的 B0 证据可进入论文？
  图表/表格的设计粒度是否合适？

Q_E27_3：推荐的优先级 P2=C → P3=D1 是否同意？
  是否同意先 C 后 D1？
  还是直接启动 D1 并把 C 作为 D1 完成后的可选增强？

Q_E27_4：D2 是否在现阶段搁置？
  还是需要在 D1 执行前完成 D2 的科学价值论证？

Q_E27_5：是否放行 C 的特征方案设计阶段（仅方案设计，不放行实验执行）？
  还是 C 的整个链（方案 → 筛选 → 复验）需要等 E27 通过后
  再独立启动 Codex 审阅链？

Q_E27_6：B0 evidence packet 是否已足够关闭 Phase 0，
  进入 Phase 1（B1 主线推进）的准备阶段？
  还是 Phase 0 仍有未闭合的证据缺口？
```

---

## 6. 红线确认

- [x] 不训练
- [x] 不改代码
- [x] 不改数据结果
- [x] 不写论文正文（本报告为设计规划，不含可直接投稿的正文段落）
- [x] 不启动 B1/GGX 渲染
- [x] 不启动 OCS 特征增强实验
- [x] 不启动三轴小项目
- [x] 不启动路线二/三/四
- [x] 不修改冻结文件、成果区或 CLAUDE.md
- [x] 不自行放行任何方向执行（仅给优先级建议）
- [x] 不把 B0/image_only/fixed-roll 结果外推到真实未知目标姿态反演
- [x] 不把 E21 泄漏结果当泛化证据
- [x] 不把 B1 与 GGX 混写
- [x] 不把路径 B 负结果外推到 B1、joint、OCS-only 或三轴结论

---

## 附录 A：B0 全证据链闭合状态确认

```text
R38 → 数据生成 (fullrun 2664)                        PASS
R39 → 训练入口 + 数据切分                              PASS
R40 → 训练 smoke                                     条件通过
R41 → smoke 判据修正                                   PASS
R42 → E21 random baseline (泄漏诊断)                   工程 PASS / 泛化 FAIL
R43 → E21-FIX01 strict yaw_block 单折                  PASS (负结果)
R44 → E22 路线决策准备 → E23                           PASS
R45 → E23 证据包 → E24                                 PASS
R46 → E24 多折方案 → E25                               PASS
R47 → E25 多折训练结果                                  条件通过
R48 → E25-FIX01 成果包补正                              PASS
R49 → E26 路线级收束准备提示词                           —
R50 → E26 路线级收束准备                                PASS

当前：E27 论文实验设计规划（本报告）
下一步：Codex 审阅本报告（R51）
```

## 附录 B：论文正文写作放行条件速查

```text
论文正文写作（任何段落）的放行条件：

  [ ] E27 实验设计规划通过 Codex 审阅
  [ ] C (OCS 特征增强) 完成并通过 Codex 审阅
  [ ] D1 (B1 fullrun + B0 vs B1 对比) 完成并通过 Codex 审阅
  [ ] 实验章完整证据链闭合（§E.1—§E.6 均可规划）
  [ ] 论文正文写作方案通过 Codex 审阅（独立的写作审阅链）

当前满足：第 1 项（E27 待审阅）
未满足：第 2-5 项
→ 论文正文写作仍为 NOT RELEASED
```
