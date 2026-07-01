# 99_1C-B5 头A头B合并裁决准备 Claude 执行报告

最后更新：2026-06-29
执行端：Claude
性质：头A/头B合并裁决**准备**材料。不是裁决、不是放行、不是论文正文、不是成果区归档。
依据：R101_Codex_审阅_1C-B4-FIX01通过_P1-A闭口并放行合并裁决准备.md（§6 允许/禁止事项）
输出路径：`02_Claude输出/99_1C-B5_头A头B合并裁决准备_Claude执行报告.md`

> 本文件不训练、不新渲染、不生成新数据、不改 split/模型/loss/head/超参/seed、不 checkpoint forward、不启动 P1-B/P2、不写成果区、不正式改写论文正文、不触发真实目标/望远镜/operational-ready claim。
> 全文只引用既有稳定审阅的路径与结论，不复述上游长背景。所有"建议/候选"均为待裁决项，不构成放行。

---

## 0. 执行摘要

```text
1. 头A 已在 R90 收口：负结果证据链 + 图表/SI 草案 + 负结果到 24 号三问桥接，三问口径稳定。
2. 头B 已逐级闭口：B-1 文献检索（R91）、B-2 方法总结与阶段门候选（93/R92R93R94）、
   B-3/P0 只读诊断（R98）、B-4/P1-A 第一阶段指标重构（R101）。
3. 两头结论一致收敛到同一主叙事：protocol-defined yaw extrapolation gap，
   而非 yaw 物理不可观测；单帧 OCS 是 light-curve 谱系的低信息下界。
4. 本报告把两头稳定结论整理为四列表（可进入论文叙事 / 只作诊断材料 /
   禁止 claim / 暂缓路线），给出 Figure/SI/Results 承接候选与成果区同步建议清单。
5. 当前仅做合并裁决准备；是否触发正式合并裁决、是否同步成果区、是否放行 P1-B/P2，
   全部留给 Codex/作者裁定。
```

---

## 1. 头A 稳定结论汇总（R90 收口）

头A 目标（R05）：负结果证据链 + 图表/SI 资产 + 负结果到 24 号三问桥接说明。当前状态：

```text
A-1 E45D-FIX02 图表/表格预生成草案：DONE（R86），成果区 16
A-2 P0 SI 资产草案：DONE（R88），成果区 17
A-3 负结果 -> 24 号三问桥接材料：DONE（R90），成果区 18
```

### 1.1 三问当前稳定回答（R90 接收口径）

```text
What can be known：
  fixed-roll + 当前图像模型 + circular yaw-block 下，pitch 指标稳定高于 chance
  （within-3 ~52-56% vs chance ~19%）；
  yaw 在 random split 分布内可学（exact-bin ~65-70%，E45A/R80），
  但无法跨 circular yaw-block 未见弧段外推（exact-bin = 0.00%）；
  C2 OCS-only 在当前特征/模型/协议下未检出高于 chance 的可区分信号。

When complementary：
  当前 fixed-roll + circular yaw-block + early concat fusion 下，
  joint 未观察到自动互补增益（yaw CMAE 与 image-only 同为 81.4°，pitch 略低）；
  构成互补研究的 fixed-protocol null-result 基准，不是 fusion 普适无用。

When trustworthy：
  exact-bin yaw = 0.00% 仅作诊断性 sentinel，标记 strict classifier
  在 circular yaw-block 外推下的失败；可启发后续 reject/confidence gate 设计，
  但当前尚未实现/验证 calibrated rejection、conformal、ECE 或 posterior-like agreement。
```

### 1.2 头A 稳定数值（Table 2 精炼，circular yaw-block 5-fold）

| 指标 | random/chance | C2 OCS-only | C3 image_only | C3 joint |
|---|---:|---:|---:|---:|
| exact-bin yaw | 1.39% | 0.00% | 0.00% | 0.00% |
| yaw within-6 | 18.06% | 18.89% | 25.57% | 26.51% |
| yaw coarse45 | 12.50% | 14.53% | 17.96% | 18.16% |
| pitch within-3 | 18.92% | 17.75% | 56.07% | 51.77% |

来源：92_1C-A3-FIX01（R90 通过）。

---

## 2. 头B 稳定结论汇总（B1/B2/B3-P0/B4-P1-A）

### 2.1 B-1 文献检索（R91，DONE）

```text
三组核心证据（R92/R93/R94 共同锁定）：
  - Wetterer & Jah 2009：对称目标不同自转轴产生近乎相同 light curve
    → 当前 yaw-block 外推失败的最佳文献镜像（BRDF 同族）。
  - Gerwe & Idell 2003：Fisher/CRLB 可观测性框架，多视角减少 blind spots
    → 把"某 yaw 区难估"升级为局部信息量不足，解释 pitch>yaw 各向异性。
  - Kaasalainen I/II：多几何覆盖比同分布点数更关键，单帧是 lightcurve 低信息下界。
PDF 入库 30 篇；BibTeX 已增量补齐。
```

### 2.2 B-2 方法总结与阶段门候选（93，R92/R93/R94 收窄）

```text
阶段门顺序：P0 只读诊断 → P1 单项 C 类改正（P1-A 判据 / P1-B 非朴素 fusion）
            → P2 光变序列（暂缓）→ P3 不确定性（暂缓）。
唯一"现在最值得做、可申请放行"的是 P0；P1/P2/P3 均需上一级证据后另设阶段门。
推荐论文方法叙事：staged path（只读诊断 → 连续判据/非朴素 fusion → 序列建模），
                  单帧 OCS 视为受控仿真下的信息下界。
```

### 2.3 B-3/P0 只读诊断（96_FIX02，R98 闭口）

P0 当前可稳定支持（R98 §4）：

```text
1. exact-bin 0% 不是"yaw 信息完全不存在"的证据。
2. exact-bin 5deg 分类判据在 yaw-block 外推协议下显著放大失败。
3. 当前 4D OCS yaw 签名存在强重叠和平滑性，支持输入签名/可辨识性不足解释。
4. C3 image_only 与 joint 在当前 early concat/判据下未改善 exact-bin diagonal。
5. pseudo-light-curve probe 暂未给出足够证据直接进入 P2。
6. V0.3/V0.4 因 split/bin/判据/前向模型口径不同，不可直接横向写成同一成功/失败链。
```

P0 残余边界（R98 §3，必须随材料保留）：

```text
- 2/72、3/72 不得写成模型 top-5 confidence，只能作 confusion row 频次副产物。
- OCS distance 只证明当前 4D OCS 聚合签名 yaw 维重叠，不得泛化到所有 image/joint embedding。
- V0.3 split 只能写"已检索文件未见 yaw-block 定义，需日志/脚本最终确认"。
- pseudo-sequence 是 single-pitch、no-evolution probe，不能证明 formal sequence 无价值。
```

### 2.4 B-4/P1-A 第一阶段指标重构（98_FIX01，R101 闭口）

```text
pooled（理论 baseline 18.0 bins）：
  C2: exact 0%, CMAE 17.79, within-6 16.0%, coarse45 11.8%
  C3 image_only: CMAE 16.33, within-6 25.6%, coarse45 18.1%
  C3 joint:      CMAE 16.32, within-6 26.5%, coarse45 18.3%
本轮最重要新发现 —— yaw-block 强位置依赖异质性：
  C2 fold3 [220,285°]: CMAE 7.50, within-6 42.9%（弱可用）
  C2 fold2 [150,215°]: CMAE 23.58, within-6 0.0%（失败）
  C2 fold4 [290,355°]: CMAE 26.59, coarse45 0.0%（失败）
  pitch 影响远小于 yaw-block（pitch MAE 跨度 2.6 vs yaw-block 跨度 19 bins）。
R101 裁决：P1-A 第一阶段闭口；不进入第二阶段训练侧改进。
```

---

## 3. 合并裁决四列表（核心交付物）

下表整合头A/头B所有稳定结论，按用途分为四列。**这是合并裁决的输入候选，不是裁决本身。**

### 3.1 可进入论文叙事（fixed-protocol 内成立，已被 R80/R82/R90/R98/R101 稳定）

| 编号 | 结论 | 稳定依据 | 拟承接位置 |
|---|---|---|---|
| N1 | protocol-defined yaw extrapolation gap 是主叙事：random split 分布内 yaw 可学（~65-70%），circular yaw-block 外推失败 | R80/R90/R98 | Results 主线 + Discussion |
| N2 | fixed-roll 下 pitch 指标稳定高于 chance（within-3 ~52-56% vs ~19%），存在 pitch>yaw 各向异性 | R90/R101 | Results pitch 小节 |
| N3 | early concat fusion 在当前协议下无自动互补增益（null-result 基准） | R77/R90/R98 | Results fusion 小节 |
| N4 | yaw-block 外推失败具有协议性、**位置依赖**特征（C2 fold3 弱可用 vs fold2/fold4 失败） | R101 | Results / Discussion（降级措辞） |
| N5 | 单帧 OCS 是 light-curve 谱系的低信息下界；后续序列升级是 higher-information layer | R91/R92/93 | Introduction / Discussion / 方法叙事 |
| N6 | 当前结果与光变定姿、CRLB、小行星光变反演文献中的对称性/几何歧义一致 | R91/R93/R94 | Related Work / Discussion |

### 3.2 只作诊断材料（透明度/支撑，不单独承载主 claim）

| 编号 | 材料 | 稳定依据 | 用途 |
|---|---|---|---|
| D1 | exact-bin yaw = 0.00% 诊断性 sentinel | R82/R90/R98 | 标记 strict classifier 外推失败；启发后续 gate 设计，非已实现拒识 |
| D2 | OCS yaw-yaw distance heatmap、nearest yaw pairs | R98 | 证明当前 4D OCS 聚合签名 yaw 维重叠；不泛化到 image/joint embedding |
| D3 | C3 confusion maps、diagonal_exact_stats（diag_sum=0） | R98 | confusion 频次描述；2/72、3/72 不得写成 top-5 confidence |
| D4 | pseudo-light-curve probe（pitch=0） | R98 | 暂缓 P2 依据；不能证明 formal sequence 无价值 |
| D5 | Figure S3 训练过程透明度（loss 下降、未发散） | R88/R90 | 提供训练透明度；不排除优化不足/过拟合/结构限制 |
| D6 | Figure S4 circular yaw-block fold0 覆盖、Table S3 per-fold 明细 | R88 | 协议透明度 + 结果透明度 |
| D7 | yaw-block 分层 / pitch 分层指标表（P1-A FIX01） | R101 | 异质性诊断；支撑 N4 位置依赖 |
| D8 | pooled weighted vs per-fold mean（差异<0.1 bins） | R101 | 口径稳健性说明 |

### 3.3 禁止 claim（红线，两头一致）

```text
F1. yaw 物理不可观测。
F2. OCS 通道本身不携带姿态信息（只能写：当前特征/几何采样/模型/协议下未检出高于 chance 的信号）。
F3. image 与 OCS 普遍不互补 / fusion 普遍无效（只否定当前 naive early concat）。
F4. exact-bin 0% 是真实/已校准的拒识机制（只是诊断性 sentinel）。
F5. 系统"知道自己不知道" / 已实现 reject。
F6. Figure S3 排除了训练失败 / 证明模型无过拟合 / 已学到最优表示。
F7. pitch 在任何条件下均可学（必须带 fixed-roll + 当前协议限定）。
F8. 已定位姿态空间物理低信息区域 / "共同失效区域"（应写 protocol-defined extrapolation failure regime）。
F9. 结果可外推真实 GEO / 三轴自由姿态 / 暗室实验 / operational-ready / 真实望远镜验证。
F10. 当前负结果已完整回答 24 号三问（只是 lower-bound 约束 + null-result 基准）。
F11. V0.3 与 V0.4 写成同一成功/失败链（split/bin/判据/前向模型口径不同）。
F12. 某些弧段"OCS 几乎可用"写成局部成功（应写"局部弱可用信号"）。
```

### 3.4 暂缓路线（需另设阶段门，当前不放行）

| 编号 | 暂缓项 | 进入条件 | 依据 |
|---|---|---|---|
| H-P1A2 | P1-A 第二阶段训练侧（continuous/circular head 重训） | 不放行：MAE 仅优 random 1-2 bins，异质性来自输入/协议而非判据 | R101 |
| H-P1B | P1-B 非朴素 fusion（late/decision/gated，模态维度平衡消融） | 需 P0/P1-A 证据 + 单独阶段门 | 93/R98 |
| H-P2 | P2 formal light-curve sequence | 需满足 93 §2.3 四到五条进入条件 + inverse-crime 预注册 | 93/R98 |
| H-P3 | P3 不确定性/置信（ECE/conformal/agreement） | 依赖 P1-A/B 落地，信息源未改时增益有限 | 93/R91 |
| H-EXP | checkpoint forward / embedding-logits 导出 | D 类只读，可另设但不阻塞主链 | R98/R101 |
| H-EXT | 三轴小项目 / 路线二/三/四扩展 | 路线一 C 闭合后按 CLAUDE.md 顺序 | CLAUDE.md |

---

## 4. Figure / SI / Results 承接候选（不正式改写正文）

下表给出"哪条稳定结论由哪个图表/SI 承接"的候选映射，供合并裁决与后续正文规划使用。

| 资产 | 编号/来源 | 服务结论 | 服务三问 |
|---|---|---|---|
| Figure 3 | E45D（成果区16） | N1 yaw extrapolation gap 主图（CMAE/within-6/coarse45 三通道 vs chance） | What can be known |
| Figure 4 | E45D（成果区16） | N2 pitch anisotropy | What can be known |
| Table 2 | E45D（成果区16） | N1+N2+N3 三通道全指标对照 | What can be known + When complementary |
| Figure S3 | A2（成果区17） | D5 训练透明度 | 方法透明度 |
| Figure S4 | A2（成果区17） | D6 协议透明度 | 方法透明度 |
| Table S3 | A2（成果区17） | D6 per-fold 明细 | 结果透明度 |
| Figure S5 | E45D（成果区16） | D1 exact-bin sentinel 诊断 | When trustworthy |
| 新候选 SI-A | P0 08_p0_diagnostics | D2/D3/D4 distance heatmap + confusion maps + pseudo-light-curve probe | What can be known（签名重叠/歧义诊断） |
| 新候选 SI-B | P1-A 09_p1a_metric_recompute | D7/D8 yaw-block/pitch 分层 + pooled 口径 | What can be known（N4 位置依赖） |

承接说明：

```text
1. 现有成果区 16/17/18 已覆盖 Figure 3/4/S3/S4/S5 + Table 2/S3 + 三问桥接，可直接作为合并裁决的正文骨架候选。
2. P0（08_p0_diagnostics）与 P1-A（09_p1a_metric_recompute）产物当前在诊断区，
   尚未进成果区；是否升格为 SI-A/SI-B 由合并裁决决定（见 §5）。
3. N4 yaw-block 位置依赖是 P1-A 新增、尚无对应正式 Figure 的结论，
   合并裁决可决定是否新增一张 per-block 异质性图（D 类只读，不重训）。
```

---

## 5. 成果区同步建议清单（不自行同步）

按 CLAUDE.md §5/§6 红线，成果区写入须经作者确认。以下为**建议清单**，不自行执行：

| 候选 | 内容 | 建议处理 | 理由 |
|---|---|---|---|
| S-1 | 头A R90 桥接材料 | 已在成果区 18，无需重复 | 已归档 |
| S-2 | B-1 文献检索（R91）+ 30 篇 PDF 入库状态 | 建议同步为头B成果索引 | B-1 已 DONE，是稳定方法依据 |
| S-3 | B-2 方法总结与阶段门候选（93） | 建议同步（标注"候选规划，非放行"） | R92/R93/R94 已收窄稳定 |
| S-4 | B-3/P0 只读诊断包（96_FIX02 + 08_p0_diagnostics 图表表格） | 建议同步为头B-P0 稳定诊断材料 | R98 已闭口 |
| S-5 | B-4/P1-A 指标重构（98_FIX01 + 09_p1a_metric_recompute） | 建议同步为头B-P1-A 稳定诊断材料 | R101 已闭口 |
| S-6 | 本 99 号合并裁决准备报告 | 待合并裁决通过后，由 Codex 决定是否归档 | 当前是准备材料 |

```text
说明：S-2..S-5 均已分别通过 R91/R92R93R94/R98/R101 稳定，具备成果区归档资格；
      但 R101 §4 Q5 裁定"P1-A 产物暂不同步，先进入合并裁决准备，成果区同步由合并裁决后决定"。
      因此本清单仅列出候选，最终是否同步、归档编号与目录由合并裁决/作者确认。
```

---

## 6. 给合并裁决的待裁定问题（合并 93 §6 与本轮）

```text
Q1. 是否正式触发头A/头B合并裁决？（R05 合并条件 2 已具备：头A R90 收口、头B P0/P1-A 闭口）
Q2. 四列表（§3）是否被接收为合并裁决的稳定输入？是否需要增删条目？
Q3. N4 yaw-block 位置依赖是否新增一张 per-block 异质性 Figure（D 类只读，不重训）？
Q4. P0/P1-A 产物是否升格为 SI-A/SI-B？归档目录与编号由谁定稿？
Q5. 成果区同步清单（§5 S-2..S-5）是否放行？放行哪些、暂缓哪些？
Q6. 合并裁决后是否进入论文正文正式改写阶段门，还是继续按 CLAUDE.md 暂缓？
Q7. P1-B / P2 是否在合并裁决中明确进入条件，还是维持暂缓不动？
```

---

## 7. 红线自检

```text
✅ 未训练、未重训练、未 checkpoint forward。
✅ 未新渲染、未生成新数据集、未改 split。
✅ 未改模型/loss/head/超参/seed。
✅ 未启动 P1-A 第二阶段 / P1-B / P2 / P3。
✅ 未写入成果区（§5 仅为建议清单，未执行）。
✅ 未正式改写论文正文（§4 仅为承接候选映射）。
✅ 未触发真实目标/望远镜/operational-ready/GEO/三轴/暗室 claim。
✅ 未修改 CLAUDE.md、冻结文件或任何非本报告文件。
✅ 全文只引用既有稳定审阅路径与结论，未新增超出 R80/R82/R90/R91/R92R93R94/R98/R101 口径的主张。

本文件仅汇总既有稳定结论，形成合并裁决准备四列表与承接/同步候选；
所有"建议/候选/待裁定"项均交回 Codex/作者裁决，Claude 不自行放行。
```

## 8. 关联文件

```text
R101_Codex_审阅_1C-B4-FIX01通过_P1-A闭口并放行合并裁决准备.md（本轮依据）
R90_Codex_审阅_1C-A3-FIX01通过_头A桥接材料稳定.md（头A收口）
R91_Codex_文献检索_1C-B1六方向方法约束与PDF入库.md（B-1）
R92/R93/R94（B-2 收窄依据）
93_1C-B2_方法总结与阶段门候选_Claude整合稿.md（B-2）
R98_Codex_审阅_1C-B3-FIX02通过_P0只读诊断闭口.md（B-3/P0）
96_1C-B3-FIX02_P0只读诊断图表与口径修正_Claude执行报告.md（P0）
98_1C-B4-FIX01_P1-A分层指标与baseline口径修正_Claude执行报告.md（P1-A）
92_1C-A3-FIX01_桥接材料claim边界收窄_Claude执行报告.md（头A三问桥接）
成果区 16/17/18（E45D / A2-P0-SI / A3-桥接）
v0.4_results/08_p0_diagnostics/、v0.4_results/09_p1a_metric_recompute/（诊断产物）
```

