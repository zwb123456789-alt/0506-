# 70_1C-E37_C1C2闭合后下一阶段门裁决准备_Claude执行报告

执行端：Claude | 任务编号：1C-E37 | 日期：2026-06-26

---

## 0. 裁决

```text
1C-E37：COMPLETED
三路径材料已备齐。最终路径选择：DEFERRED TO CODEX
C3 / 训练 / 论文正文 / 三轴小项目 / 路线二三四：均 NOT RELEASED
```

---

## 1. C1/C2 已稳定成果（仅关键事实）

```text
C1：14 configs 预注册完整性通过。
C2：13 configs × 5 folds = 65 runs，fixed MLP + circular yaw-block holdout，
     all yaw_acc = 0.00%, all yaw_correct_count = 0。
裁决：FIXED-PROTOCOL NULL RESULT。
```

已稳定资产：证据包（R62）→ Results非正文材料包（R65）→ 图表SI资产（R69）→ 路径裁决材料（R63）。

不可动摇口径：`7/72=9.72%`、pitch 二级诊断、Figure 2 = 72/72 aggregate、C2 不证明 OCS 物理无信息。

---

## 2. 三路径总览

| 路径 | 代号 | 需要 GPU | 产出 |
|---|---|---|---|
| A | C3 image/joint 对照实验 | 是 | image-only + joint 结果，三通道对比 |
| B | 论文 Results/章节草案 | 否 | Methods 结构、Results skeleton、论文框架 |
| C | 暂缓 C3，推其他路线 | 否 | GEO 光度初探 / 三轴构型 / B1 公式确认 |

---

## 3. Path A：C3 对照实验

**目标**：在 C2 null 基础上跑 image-only + joint early fusion，评估三通道互补性。

**前置条件（未确认）**：
- GPU 可用性、image data pipeline 状态、image dataloader 是否存在
- Pretrained vs from scratch 未锁定

**最小协议**：ResNet18 + early fusion (concat OCS 4dim + ResNet features → MLP)，5-fold yaw-block（与 C2 同 split seed），30 epochs，无超参搜索。

**产出**：三通道对比总表。image positive + joint > image → 互补性成立；image positive + joint ≈ image → image 主导；all null → 全部失败。

**主要风险**：image data 未就绪 / GPU 不可用 / dataloader 不存在（HIGH）；若 image 也 null，C3 沉没 30-40h GPU；若 pretrained 与 fixed-protocol 原则冲突（MEDIUM）。

**禁止 claim**：不声称 image 一定优于 OCS / C3 必做 / 结果可外推真实目标。

---

## 4. Path B：论文框架草案

**目标**：以 C1/C2 稳定证据为材料，整理论文 Results 结构、Methods 大纲和章节级框架，只写 bullet 要点和 gap list，不写正式正文段落。

**产出**：Results subsection 结构 + 每节要点，Methods 大纲，Introduction 逻辑流，Discussion 可讨论/不可讨论清单，投稿前缺口列表。

**优势**：零 GPU、低风险、快速推进、不阻塞后续 C3。

**局限**：只有 OCS-only null，缺乏 image/joint 对照；可能被审稿人质疑"为什么不跑 image baseline"。

**主要风险**：内容单薄 / 审稿人对缺 image 对照敏感（MEDIUM）。

**禁止 claim**：不写正文段落、不声称互补性已验证、不声称方法已最终确定。

---

## 5. Path C：转向其他路线

**三个可推进方向**：

1. **GEO 真实光度初探**：光度趋势/分布 vs phase63 仿真对比，为三轴构型提供约束
2. **三轴小项目最亮构型**：姿态空间光度极值搜索、高/低信息区域划分
3. **B1 书中模型公式确认**：公式与 phase63 材质/光源对应关系核对

**优势**：推进外部锚点和 Method 升级，分散风险，不损失 C3 选项。

**局限**：论文主线 OCS-vs-image 核心问题仍未回答；GEO 无姿态真值。

**主要风险**：论文论证延期（HIGH）、GEO 数据质量不确定（MEDIUM）。

**禁止 claim**：不声称 GEO 替代 C3 / 三轴证明互补性 / B1 确认后不需要 image 对照。

---

## 6. 路径关系与推荐策略

三条路径不互斥。推荐三种组合：

```text
策略 A-first：先 Path B 暴露论据缺口 → 再裁决 Path A 或 Path C
策略 并行：  Path B + Path C 某方向（B1 或 GEO）并行，保留 Path A
策略 硬仗：  Path A first，若 image positive 则框架有力，若 null 则明确多模态 null report
```

当前所有路径均受约束：C3/训练/正文/三轴/路线二三四 = NOT RELEASED。

---

## 7. 待 Codex 裁决

```text
Q1：优先选择哪条路径或组合策略？
Q2：若 Path A，GPU/image data/dataloader/pretrained 由谁确认？
Q3：若 Path B，仅 Results 结构 vs 全论文框架？需要期刊格式约束吗？
Q4：若 Path C，优先方向：B1 vs GEO vs 三轴？
Q5：是否允许 Path B 与 Path C 子方向并行？
Q6：C1/C2 还有未闭合的口径问题吗？
```

---

## 8. 红线

```text
本报告期间：未启动 C3、未训练、未改代码、未写正文段落、
未放行三轴小项目或路线二三四、未外推 C2 null result、
未声称 image/joint 一定优于 OCS。本报告仅作裁决材料。
```
