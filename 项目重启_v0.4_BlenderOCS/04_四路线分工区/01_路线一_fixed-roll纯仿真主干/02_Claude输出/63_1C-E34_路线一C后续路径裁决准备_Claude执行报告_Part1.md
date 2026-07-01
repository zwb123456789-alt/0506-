# 63_1C-E34_路线一C后续路径裁决准备_Claude执行报告

执行端：Claude  
任务编号：1C-E34  
任务名称：路线一 C 后续路径裁决准备  
执行日期：2026-06-26  

---

## 0. 执行裁决

```text
1C-E34：COMPLETED
路径 A 决策材料：COMPLETE
路径 B 决策材料：COMPLETE
两路径对比与风险评估：COMPLETE
```

本报告整理两个候选路径的决策材料，不运行训练、不改代码、不写论文正文，仅供 Codex 裁决参考。

---

## 1. 任务依据

### 1.1 输入文件

```text
依据文件：
- CLAUDE.md
- R62_Codex_审阅_1C-E33-FIX01通过并形成C1C2稳定证据包.md
- R61_Codex_审阅_1C-E33需FIX01_判据基线与C3边界修正.md
- 62_1C-E33-FIX01_判据基线与C3边界修正_Claude执行报告.md
- 61_1C-E33_C1C2证据包与claim边界整理_Claude执行报告_Part1.md
- 61_1C-E33_C1C2证据包与claim边界整理_Claude执行报告_Part2.md

稳定证据：
- v0.4_results/04_ocs_features/feature_definitions.json
- v0.4_results/05_c2_screening/c2_screening_summary.json
```

### 1.2 当前状态确认

**已关闭**：
- C1/C2 证据包整理
- C2 OCS-only null result（已接受为稳定证据）

**未放行**：
- C3 joint 复验
- 后验 OCS-only 架构/特征搜索
- 论文正文正式改写
- 三轴小项目、路线二/三/四扩展

---

## 2. 路径 A：接受 C2 Null Result，准备 Results 草案材料

### 2.1 路径 A 核心定位

**科学定位**：
```text
接受 C2 OCS-only null result 为路线一 C Phase 0 的稳定负结果，
围绕该负结果整理 Results 表格、图表、段落骨架和 claim 边界，
不追求 OCS-only positive，转而聚焦"可观测性边界"与"为后续对照实验建立 baseline"。
```

**论文 claim 定位**：
```text
在 model-known 条件下，低维 OCS-only 特征（1-13D）通过固定 MLP 架构
未显示跨 yaw holdout 泛化能力，建立了 OCS 单通道的可观测性边界基线。
该负结果为预注册、受控、完整的 null result，具有方法学价值。
```

### 2.2 路径 A 交付物清单

**2.2.1 表格草案（已完成，需转为论文格式）**

基于 E33 + FIX01，以下表格已有数据基础：

**Table 1: OCS Feature Configuration Overview**
- 14 个配置的 config_name, claim_class, dim, feature_keys
- 需增加：归因边界说明（sub-type a vs b）

**Table 2: C2 OCS-Only Screening Results**
- 13 个配置的 yaw_acc, yaw_cmae, within_3_bins_rate, pitch_acc
- 需应用 FIX01 修正：within-3 chance-level 9.72%, pitch 二级诊断

**Table 3: C2 Results Grouped by Claim Class**
- 按 photometric OCS / visibility control / mixed 分组汇总
- 需应用 FIX01 修正：随机基线说明

**2.2.2 图表草案（需生成图注和 caption）**

基于 E33-FIX01 优化后的图表规划：

**Figure 1: Feature Extraction Pipeline**
- 内容：OCS manifest → raw features → 13 configs 流程图
- Caption 要点：预注册完整性、常量自检

**Figure 2: Circular Yaw-Block Holdout Strategy**
- 内容：5-fold circular yaw_block 示意图
- Caption 要点：跨 yaw 泛化评估设计

**Figure 3: Yaw CMAE vs Within-3-Bins Rate**
- 内容：scatter plot，按 claim_class 分组着色
- Caption 要点：局部 coarse localization 但未转化为 exact-bin accuracy

**Figure 4: Pitch Accuracy by Config (Grouped by Claim Class)**
- 内容：pitch_acc grouped bar chart
- Caption 要点：二级诊断指标

**2.2.3 Results 段落骨架（非正文，仅结构）**

**建议 Results 章节结构**：

```markdown
3. Results

3.1 C1: OCS Feature Extraction and Pre-Registration Validation
  - Feature configuration overview (Table 1)
  - Pre-registration integrity check (constant sanity check passed)
  - Claim class definitions and attribution boundaries

3.2 C2: OCS-Only Baseline Screening Under Fixed Protocol
  - Training protocol and holdout strategy (Figure 2)
  - Screening results overview (Table 2, Table 3)
  - Null result verdict: all configs 0.00% yaw exact-bin accuracy
  - Diagnostic observations: within-3-bins, pitch accuracy

3.3 Failure Mode Analysis
  - Yaw CMAE and coarse localization patterns (Figure 3)
  - Pitch diagnostic signals (Figure 4)
  - Attribution by claim class: photometric / visibility / mixed

3.4 Observability Boundary Interpretation
  - C2 establishes a controlled null baseline for OCS-only low-dim features
  - Does not preclude alternative architectures or richer feature engineering
  - Sets the stage for future image-only and joint-channel comparisons
```

**2.2.4 Claim 边界文档（已完成）**

基于 E33-FIX01 的可写/不可写边界，已形成稳定口径（见 FIX01 报告第 6 节）。

### 2.3 路径 A 工作量与时间估算

**已完成工作**（基于 E33 + FIX01）：
- ✅ C1/C2 证据包整理
- ✅ 表格数据汇总（13 个配置完整数据）
- ✅ Claim 边界草案
- ✅ 图表规划方案

**待完成工作**（如放行路径 A）：
- [ ] 将表格转为论文 LaTeX/Word 格式（~2 小时）
- [ ] 生成 6 个图表的 caption 和图注（~3 小时）
- [ ] 编写 Results 段落骨架的详细文字（非正文，~4 小时）
- [ ] 生成 Supplementary Material 清单（~2 小时）

**总工作量估算**：~11 小时（单人连续工作）

### 2.4 路径 A 优势

**科学优势**：
1. ✅ 接受负结果，符合预注册精神
2. ✅ 建立 OCS-only baseline，为后续对照实验铺垫
3. ✅ 可快速形成 Results 草案，推进论文写作

**资源优势**：
4. ✅ 无需新训练，零计算资源消耗
5. ✅ 数据和表格已完备，直接转化即可
6. ✅ 低风险，不依赖未知实验结果

**路线优势**：
7. ✅ 可与三轴小项目、路线二 GEO 锚点并行
8. ✅ 不阻塞其他路线推进
9. ✅ 为后续 C3（如放行）提供清晰对照基线

### 2.5 路径 A 局限

**科学局限**：
1. ⚠️ 只有 OCS-only null，缺乏 image/joint 对照
2. ⚠️ 无法直接证明 OCS 与 image 的互补性
3. ⚠️ 论文 novelty 依赖"负结果的方法学价值"

**写作局限**：
4. ⚠️ Results 相对单薄（只有 C2 null）
5. ⚠️ Discussion 需要谨慎，避免过度解释
6. ⚠️ 可能被审稿人质疑"为什么不做 image 对照"

**路线局限**：
7. ⚠️ 路线一 C 主线未完全闭合（缺 image/joint）
8. ⚠️ 若后续仍需 C3，则当前 Results 需要补充

### 2.6 路径 A 风险评估

**低风险项**：
- ✅ 证据链完整，Codex 已通过
- ✅ 表格数据无误，已机器核验
- ✅ Claim 边界明确，不过度外推

**中风险项**：
- ⚠️ 论文投稿时可能被要求补 image 对照
- ⚠️ 负结果的接受度依赖期刊和审稿人

**风险缓解**：
- 在 Discussion 中明确说明 C2 是 baseline screening
- 强调预注册和方法学价值
- 预留 C3 为 future work 或 under review

---

## 3. 路径 B：评估 C3 独立对照实验

### 3.1 路径 B 核心定位

**科学定位**：
```text
在 C2 OCS-only null result 基础上，执行独立的 image-only 和 joint (OCS+image) 
对照实验，评估：
1. Image-only 是否能实现跨 yaw 泛化
2. Joint 是否优于单通道（互补性验证）
3. OCS vs Image 的通道归因
```

**论文 claim 定位**：
```text
若 C3 结果为 image > OCS 且 joint > image：
  论文主线为 OCS 与 image 的互补性与融合增益
若 C3 结果为 image > OCS 但 joint ≈ image：
  论文主线为 image 主导，OCS 贡献有限
若 C3 结果为全部 null：
  论文主线为当前架构/任务设置的反思
```

### 3.2 路径 B 实验设计

**3.2.1 C3 最小协议**

**输入通道**：
- OCS-only：已完成（C2，13 configs，全 null）
- Image-only：待执行（单架构，如 ResNet18）
- Joint：待执行（early fusion，OCS features + image features → MLP）

**架构选择**：
- **Image-only**: ResNet18（预训练 ImageNet 或 from scratch）
- **Joint**: 
  - Early fusion: concat OCS baseline_4dim + ResNet18 features → MLP head
  - 不做 late fusion / attention fusion（最小协议）

**训练协议**：
- 5-fold circular yaw_block holdout（与 C2 相同）
- Max epochs: 30（与 C2 相同）
- Batch size: 32
- Optimizer: Adam, lr=1e-3
- 无超参搜索（固定协议）

**判据**（与 C2 一致）：
- Strong positive: yaw_acc >= 10%
- Weak positive: yaw_acc >= 3% + 额外验证
- Null result: yaw_acc < 3%

**3.2.2 C3 训练规模**

**运行数量**：
- Image-only: 1 架构 × 5 folds = 5 runs
- Joint: 1 架构 × 5 folds = 5 runs
- 总计：10 runs

**时间估算**：
- Image-only: ~3-4 小时/fold（ResNet18 from scratch）
- Joint: ~3-4 小时/fold
- 总计：~30-40 小时（GPU 连续训练）

**计算资源**：
- GPU: 1 × RTX 3090 或同等算力
- 存储: ~5 GB（checkpoints + results）

### 3.3 路径 B 停止条件

**Early stop 条件**（节省资源）：

**条件 1：Image-only 前 2 folds 均 null**
- 若 fold0, fold1 的 image-only yaw_acc < 3%
- 则评估是否继续剩余 3 folds
- 或直接判定 image-only 也为 null，转向路径 A

**条件 2：Image-only positive 但 joint 前 2 folds 无增益**
- 若 image-only yaw_acc > 10%，但 joint 前 2 folds 的 yaw_acc ≈ image-only
- 则评估 OCS 是否有贡献
- 或完成全部 5 folds 以确认

**条件 3：全部 null**
- 若 image-only 和 joint 均 < 3%
- 则判定当前任务设置/架构存在问题
- 转向路径 A 或反思架构/任务

### 3.4 路径 B 预期场景与对应 Claim

| 场景 | Image-only | Joint | OCS-only | 论文 Claim | 路线价值 |
|------|------------|-------|----------|-----------|---------|
| 场景 1 | > 10% | > image | 0% | OCS+image 互补，joint 优于单通道 | ⭐⭐⭐⭐⭐ |
| 场景 2 | 3-10% | > image | 0% | 弱互补，joint 有增益 | ⭐⭐⭐⭐ |
| 场景 3 | > 10% | ≈ image | 0% | Image 主导，OCS 无显著增益 | ⭐⭐⭐ |
| 场景 4 | < 3% | < 3% | 0% | 全部 null，架构/任务需反思 | ⭐⭐ |

**场景 1-2**：路线一 C 主线成立（互补性），论文价值高  
**场景 3**：OCS 贡献有限，需讨论原因，论文价值中等  
**场景 4**：全部失败，需转向路径 A 或重新设计任务

### 3.5 路径 B 优势

**科学优势**：
1. ✅ 完整对照链：OCS-only / image-only / joint
2. ✅ 直接验证互补性假设
3. ✅ 通道归因明确

**论文优势**：
4. ✅ Results 更丰富（3 通道对比）
5. ✅ 若场景 1-2，论文 novelty 显著提升
6. ✅ 符合路线一 C 原始主线定位

**路线优势**：
7. ✅ 路线一 C 主线完整闭合
8. ✅ 为三轴小项目、路线二提供更强基础

### 3.6 路径 B 局限

**时间局限**：
1. ⚠️ 需 30-40 小时 GPU 训练
2. ⚠️ 延迟论文 Results 生成 1-2 周

**资源局限**：
3. ⚠️ 需 GPU 资源（1 × RTX 3090）
4. ⚠️ 需代码开发（image dataloader, joint fusion）

**风险局限**：
5. ⚠️ 场景 3-4 的风险：image 无增益或全部 null
6. ⚠️ 若全部 null，前期投入成本沉没

### 3.7 路径 B 风险评估

**高风险项**：
- ⚠️ **场景 4 风险**：image-only 也 null，全部失败
  - 概率：中等（phase63 fixed-roll 可能不利于图像）
  - 后果：C3 时间成本沉没，仍需回到路径 A
  - 缓解：前 2 folds early stop，降低沉没成本

**中风险项**：
- ⚠️ **场景 3 风险**：image 成功但 OCS 无贡献
  - 概率：中等
  - 后果：OCS 互补性不成立，论文价值降低
  - 缓解：在 Discussion 中分析 OCS 失败原因

**低风险项**：
- ✅ 训练稳定性：ResNet18 成熟架构
- ✅ 数据完整性：已有 2664 条样本
- ✅ 协议遵守：固定协议，无超参搜索

**风险缓解策略**：
1. **Early stop**: 前 2 folds 结果不理想时及时停止
2. **最小协议**: 只做 ResNet18 + early fusion，不扩展架构搜索
3. **预案准备**: 若 C3 null，直接转路径 A，不做后验补救

---

（待续 Part 2：两路径对比、资源评估与建议）
