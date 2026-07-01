## 5. C2 Null Result 的 Claim 边界草案

### 5.1 可写边界（论文可接受表述）

**核心 Claim**：
```text
在 model-known, fixed-roll, phase63 条件下，使用 circular yaw_block holdout 评估时，
OCS-only 低维特征（1-13 维）通过固定 3-layer MLP 架构未显示跨 yaw 泛化能力。
```

**可写的具体表述**：

1. **方法层面**：
   - "我们在预注册的固定协议下测试了 13 个 OCS-only 特征配置"
   - "使用 3-layer MLP (hidden_dim=128) 和 5-fold circular yaw_block holdout"
   - "训练集覆盖 6 个离散 yaw 值，测试集评估未见 yaw 角度的泛化能力"

2. **结果层面**：
   - "所有 13 个配置的 test yaw exact-bin accuracy 均为 0.00%"
   - "Photometric OCS 特征（纯光度）未达到跨 yaw 泛化"
   - "Visibility control 特征（纯几何）同样未达到跨 yaw 泛化"
   - "Mixed OCS+visibility 特征未能结合两类信息实现泛化"
   - "yaw within-3-bins rate 范围 2.75%-15.57%，略高于随机（8.3%），但未转化为 exact-bin accuracy"

3. **归因层面**：
   - "Sub-type (a) 纯 OCS 光度特征（不依赖 pixel-count）未显示姿态判别能力"
   - "Sub-type (b) visibility-normalized OCS 特征同样未达到泛化"
   - "低维 OCS-only 特征在严格 yaw holdout 下不足以支撑当前形式的姿态反演头"

4. **边界条件声明**：
   - "该结果在固定 MLP 协议和当前特征集合下获得"
   - "不排除其他架构（CNN/Transformer）或更复杂特征工程可能改善性能"
   - "该负结果为 model-known 条件下受控仿真结果，不外推至真实未知目标"

5. **科学价值**：
   - "该 null result 为受控、预注册、完整的负结果，具有科学价值"
   - "明确了 OCS-only 单通道在 pixel-level 同源架构下的可观测性边界"
   - "为后续 image 或 joint 通道对照实验提供 baseline"

### 5.2 不可写边界（必须避免的表述）

**禁止的过度推广**：

1. ❌ "OCS 光度通道在物理上不含姿态信息"
   - 原因：物理光度分布必然携带姿态信息；负结果仅表明当前方法未能提取

2. ❌ "OCS 光度在所有模型、所有特征、所有架构下都无法用于姿态反演"
   - 原因：仅测试了 3-layer MLP + 13 个低维特征配置

3. ❌ "OCS 单通道完全失败"
   - 原因：未测试 image-level OCS representation（如 OCS spatial map CNN）

4. ❌ "证明 OCS 不如图像通道"
   - 原因：未运行 image 或 joint 对照实验

5. ❌ "该结果适用于真实未知目标在轨姿态反演"
   - 原因：model-known 条件，仿真数据，不外推至真实场景

6. ❌ "Visibility 特征比 photometric OCS 更有效"
   - 原因：所有配置均为 0.00% yaw_acc，无显著差异

7. ❌ "Phase63 fixed-roll 几何不利于 OCS"
   - 原因：未进行跨几何对比实验

8. ❌ "后续无需尝试 OCS 改进"
   - 原因：负结果不等于终局判断；其他架构/特征/几何仍可探索

### 5.3 必要的限定语（Qualifiers）

论文表述中必须包含的限定：

1. **协议限定**：
   - "在固定 MLP 协议下"
   - "使用预注册的特征集合"
   - "未进行超参数搜索或架构优化"

2. **数据限定**：
   - "在 phase63 fixed-roll 几何下"
   - "model-known 条件"
   - "2664 条 Blender 渲染样本"

3. **任务限定**：
   - "跨 yaw circular block holdout"
   - "exact-bin classification 任务"
   - "OCS-only 单通道输入"

4. **结论限定**：
   - "在当前设置下"
   - "低维 OCS-only 特征"
   - "不排除其他方法可能改善"

### 5.4 推荐的论文 Results 段落结构

**建议结构**：

```markdown
### 3.2 OCS-Only Baseline Results (C2 Screening)

We evaluated 13 pre-registered OCS-only feature configurations under 
a fixed 3-layer MLP protocol and circular yaw-block holdout. 
All configurations yielded 0.00% test yaw exact-bin accuracy across 
5 folds (Table X).

**Photometric OCS features** (9 configs, including both direct OCS ratios 
and visibility-normalized densities) failed to generalize across yaw. 
**Visibility control features** (2 configs) showed similar null results, 
indicating that pixel-count information alone was insufficient. 
**Mixed OCS+visibility features** (2 configs) did not combine the two 
channels effectively under the current architecture.

While yaw within-3-bins rates ranged 2.75%-15.57% (slightly above random 8.3%), 
none achieved exact-bin accuracy. Pitch accuracy was weak (2.56%-4.37%), 
well below the 3% threshold for weak-positive results.

This null result, obtained under a pre-registered protocol without 
hyperparameter search, establishes a controlled baseline for assessing 
the observability of OCS-only low-dimensional features under strict 
cross-yaw generalization. It does not preclude potential improvements 
with alternative architectures (e.g., CNNs, Transformers) or more 
sophisticated feature engineering.
```

---

## 6. Image/Joint 对照实验论证框架

### 6.1 为什么需要 Image/Joint 对照

**当前状态**：
- C2 OCS-only：null result（0.00% yaw_acc）
- 问题：无法判断这是 OCS 通道本身的局限，还是方法/架构的局限

**对照实验的价值**：

1. **互补性论证**：
   - 如果 image-only 或 joint 表现更好 → 证明 OCS 与 image 的互补性
   - 如果 joint 优于单通道 → 论文主线成立

2. **通道归因**：
   - Image-only vs OCS-only → 分离通道贡献
   - Joint vs OCS-only / Image-only → 量化融合增益

3. **失败模式分析**：
   - 如果 image/joint 也失败 → 问题可能在架构/任务设置
   - 如果 image 成功但 OCS 失败 → OCS 特征工程需改进

### 6.2 C3 Joint 复验的触发条件

**R60 明确**：C3 不由 C2 自动触发，需另行 Codex 审阅。

**触发理由（需 Codex 评估）**：

**选项 A：作为独立对照实验**
```text
不是因为 C2 达到 positive 触发 C3，
而是作为路线一 C 论文中 OCS-only negative 与 image/joint complementarity 的独立对照实验。
```

**选项 B：先补救 OCS-only**
```text
在启动 C3 前，先尝试改进 OCS-only 架构/特征：
- 尝试更深 MLP / CNN / Transformer
- 尝试更复杂特征工程（如 temporal OCS sequences）
- 如果仍为 null，再启动 C3 对照
```

**选项 C：接受 null result，转向其他路线**
```text
接受 C2 null result 为路线一 C 的 Phase 0 结论，
转向三轴小项目或路线二/三，暂不执行 C3。
```

### 6.3 C3 实验设计框架（如果放行）

**C3 目标**：
- 评估 image-only 和 joint (OCS+image) 在相同 yaw_block holdout 下的性能
- 对比 OCS-only / image-only / joint 的 yaw 泛化能力

**C3 输入通道**：
- **OCS-only**：已完成（C2，13 个配置，全部 null）
- **Image-only**：待执行（baseline CNN/ViT）
- **Joint**：待执行（early fusion / late fusion / attention fusion）

**C3 架构选择**（需 Codex 审阅）：
- Image-only：ResNet18 / EfficientNet-B0 / ViT-Tiny
- Joint：
  - Early fusion：concat OCS features + image features → MLP
  - Late fusion：separate OCS head + image head → weighted avg
  - Attention fusion：cross-attention between OCS + image

**C3 判据**（与 C2 一致）：
- Strong positive：yaw_acc ≥ 10%
- Weak positive：yaw_acc ≥ 3% + 额外验证
- Null result：yaw_acc < 3%

**C3 预期场景**：

| 场景 | Image-only | Joint | 论文 Claim |
|------|------------|-------|-----------|
| 场景 1 | > 10% | > image-only | OCS+image 互补，joint 优于单通道 |
| 场景 2 | 3-10% | > image-only | 弱互补，joint 有增益 |
| 场景 3 | > 10% | ≈ image-only | Image 主导，OCS 无显著增益 |
| 场景 4 | < 3% | < 3% | 全部 null，问题在架构/任务 |

**场景 1-2**：论文主线成立（互补性）  
**场景 3**：OCS 贡献有限，需讨论 OCS 特征改进  
**场景 4**：需反思架构/任务设置，或转向其他路线

### 6.4 C3 启动的前置条件（供 Codex 评估）

**必要条件**：
1. C1/C2 证据包整理完成（本报告）
2. Codex 审阅通过 C1/C2 证据链
3. 明确 C3 的科学目标（对照 or 互补性验证）
4. 确定 C3 的架构选择和判据

**可选前提**：
1. 是否需要先尝试改进 OCS-only（选项 B）
2. 是否需要先完成三轴小项目（观测规划）
3. 是否需要先引入路线二 GEO 锚点（真实光度分布）

**资源评估**：
- C3 训练规模：3 通道（OCS/image/joint）× 5 folds ≈ 15 runs
- 如果测试多架构：× N 架构 = 15N runs
- 预估时间：单通道 ~2-4 小时/fold，总计 10-20 小时

### 6.5 当前建议（供 Codex 裁决）

**Claude 建议**：

**优先级 1（推荐）**：
```text
放行 C3 作为独立对照实验，明确目标为 OCS-only vs image-only vs joint 对照。
先执行 image-only baseline (single architecture, e.g., ResNet18) 和 
simple joint (early fusion) 各 5 folds，评估是否达到 weak_positive。
```

**优先级 2（备选）**：
```text
接受 C2 null result，暂不启动 C3，转向：
- 整理 C1/C2 为论文 Results 草稿
- 启动三轴小项目（最亮构型、高信息姿态）
- 引入路线二 GEO 真实光度锚点
```

**不推荐**：
```text
后验改 OCS-only 协议或做开放架构搜索。
原因：C2 是预注册固定协议筛选，后验搜索需另立任务，
且在全部配置 yaw_acc=0 的情况下，收益不明确。
```

---

## 7. 论文图表表格规划

### 7.1 Results 部分拟用表格

**Table 1：C1 Feature Configuration Overview**
- 内容：14 个配置的 config_name, claim_class, dim, feature_keys 简述
- 用途：展示预注册特征设计的完整性和分类逻辑

**Table 2：C2 OCS-Only Screening Results**
- 内容：13 个配置的 yaw_acc, yaw_cmae, within_3_bins_rate, pitch_acc（见 4.1）
- 用途：C2 null result 核心证据表

**Table 3：C2 Results Grouped by Claim Class**
- 内容：按 photometric OCS / visibility control / mixed 分组汇总（见 4.2）
- 用途：归因分析，证明所有 claim class 均为 null

**Table 4（如果 C3 执行）：Channel Comparison (OCS / Image / Joint)**
- 内容：3 通道的 yaw_acc, yaw_cmae, pitch_acc 对比
- 用途：互补性论证

### 7.2 Results 部分拟用图表

**Figure 1：Feature Extraction Pipeline**
- 内容：从 OCS manifest → raw features → 13 configs 的流程图
- 用途：方法可视化

**Figure 2：C2 Training Protocol and Split Strategy**
- 内容：circular yaw_block holdout 示意图（5 folds）
- 用途：展示跨 yaw 泛化评估设计

**Figure 3：C2 Yaw Accuracy by Config (Bar Chart)**
- 内容：13 个配置的 test_yaw_acc（全部 0.00%）+ error bar
- 用途：直观展示 null result

**Figure 4：C2 Yaw CMAE and Within-3-Bins Rate (Scatter Plot)**
- 内容：X 轴 yaw_cmae，Y 轴 within_3_bins_rate，每个 config 一个点
- 用途：展示虽有轻微聚集但未转化为 exact-bin accuracy

**Figure 5：Pitch Accuracy vs Yaw Accuracy (Scatter Plot)**
- 内容：X 轴 yaw_acc（全 0），Y 轴 pitch_acc（2.56-4.37%）
- 用途：展示 pitch 有微弱信号但不足 weak_positive

**Figure 6（如果 C3 执行）：Channel Comparison (Grouped Bar Chart)**
- 内容：OCS / Image / Joint 的 yaw_acc 对比
- 用途：互补性可视化

### 7.3 Supplementary Material 拟用内容

**Supplementary Table S1：C1 Raw Feature Fields (24 个)**
- 内容：raw_feature_fields 完整清单 + 计算公式

**Supplementary Table S2：C2 Per-Fold Results (65 个)**
- 内容：每个 fold 的完整指标（yaw_acc, pitch_acc, cmae, within_k, correct_count 等）

**Supplementary Figure S1：C2 Training Curves (Selected Configs)**
- 内容：典型配置的 train_loss / val_loss / val_yaw_acc 曲线（30 epochs）
- 用途：展示训练收敛但 val_yaw_acc 持续为 0

**Supplementary Figure S2：Confusion Matrix (Selected Configs)**
- 内容：yaw 预测的 confusion matrix（如果有预测分布数据）
- 用途：分析预测偏向性

---

## 8. 红线符合性检查

### 8.1 禁止项检查

| 禁止项 | 状态 | 说明 |
|--------|------|------|
| 启动 C3 | ✅ 未违反 | 仅提供论证框架，未执行 |
| 做后验超参搜索 | ✅ 未违反 | 未涉及 |
| 做后验架构搜索 | ✅ 未违反 | 未涉及 |
| 改 feature_definitions.json | ✅ 未违反 | 仅读取，未修改 |
| 改 enhanced_ocs_features.npz | ✅ 未违反 | 仅读取，未修改 |
| 改 split manifests | ✅ 未违反 | 未涉及 |
| 写论文正文 | ✅ 未违反 | 仅整理证据和 claim 边界草案 |
| 启动 B1/GGX | ✅ 未违反 | 未涉及 |
| 启动三轴小项目 | ✅ 未违反 | 未涉及 |
| 启动路线二/三/四 | ✅ 未违反 | 未涉及 |

### 8.2 完成项检查

| 要求项 | 状态 | 说明 |
|--------|------|------|
| 读取 C1/C2 结果 | ✅ 已完成 | 4 个依据文件全部读取 |
| 整理 C1/C2 证据包 | ✅ 已完成 | 第 2、3 节 |
| 生成 C2 表格草案 | ✅ 已完成 | 第 4 节，2 个表格 |
| 明确可写/不可写边界 | ✅ 已完成 | 第 5 节，详细列出 |
| 给出 image/joint 论证框架 | ✅ 已完成 | 第 6 节，C3 框架 |
| 论文图表表格规划 | ✅ 已完成 | 第 7 节，6 图 4 表 |

---

## 9. 下一步裁决点（供 Codex）

### 9.1 当前阶段门状态

```text
E33 执行完整性：PASS
C1/C2 证据包整理：COMPLETE
C2 表格草案：COMPLETE
Claim 边界草案：COMPLETE
Image/Joint 论证框架：COMPLETE
```

### 9.2 待 Codex 裁决的问题

**问题 1：是否接受 C2 null result 为有效负结果？**
- 如果 YES → 可进入论文 Results 整理
- 如果 NO → 需说明原因并返工

**问题 2：是否放行 C3 joint 复验？**
- 如果 YES → 给出 C3 提示词和架构选择
- 如果 NO → 说明原因，转向其他路线

**问题 3：C3 如果放行，执行顺序如何？**
- 选项 A：先执行 image-only baseline，再决定 joint
- 选项 B：同时执行 image-only + joint (early fusion)
- 选项 C：先改进 OCS-only，再执行 C3

**问题 4：C1/C2 证据包是否需要补充？**
- 如果需要补充 → 列出补充项
- 如果充分 → 可讨论论文 Results 草稿生成

**问题 5：论文正文改写何时启动？**
- 选项 A：C3 完成后再统一改写
- 选项 B：先改写 C1/C2 部分，C3 后追加
- 选项 C：等待三轴小项目/路线二/三完成后统一改写

---

## 10. 执行总结

### 10.1 E33 交付物

**主报告**：
- 61_1C-E33_C1C2证据包与claim边界整理_Claude执行报告_Part1.md
- 61_1C-E33_C1C2证据包与claim边界整理_Claude执行报告_Part2.md

**核心内容**：
1. C1 证据包汇总（14 个配置，预注册完整性验证）
2. C2 证据包汇总（13 个配置，null result 判定）
3. C2 表格草案（2 个论文可用表格）
4. Claim 边界草案（可写/不可写/限定语）
5. Image/Joint 对照实验论证框架（C3 设计）
6. 论文图表表格规划（6 图 4 表 + 补充材料）

### 10.2 关键结论

**C2 Null Result**：
```text
在 model-known, phase63 fixed-roll, circular yaw_block holdout 条件下，
OCS-only 低维特征（1-13 维）通过固定 3-layer MLP 未显示跨 yaw 泛化能力。
所有 13 个配置的 test_yaw_acc = 0.00%。
```

**归因边界**：
- ✅ 可归因：当前固定协议下 OCS-only 特征未达到泛化
- ❌ 不可归因：OCS 光度在所有条件下完全无姿态信息

**科学价值**：
- 受控、预注册、完整的负结果
- 明确了 OCS-only 低维特征在当前架构下的可观测性边界
- 为后续 image/joint 对照实验提供 baseline

### 10.3 后续路径选择（供 Codex 裁决）

**路径 A：执行 C3 对照实验**
- 放行 image-only + joint (early fusion)
- 5-fold yaw_block holdout
- 评估互补性和融合增益

**路径 B：接受 null result，转向其他路线**
- 整理 C1/C2 为论文 Results 草稿
- 启动三轴小项目（最亮构型、观测规划）
- 引入路线二 GEO 真实光度锚点

**路径 C：补救 OCS-only（exploratory）**
- 尝试更深 MLP / CNN / Transformer
- 标注为 exploratory，不回填 C2 预注册结论
- 如仍 null，再执行路径 A 或 B

---

**执行端签名**：Claude  
**执行日期**：2026-06-26  
**下一步**：等待 Codex 审阅 E33 证据包，裁决后续路径
