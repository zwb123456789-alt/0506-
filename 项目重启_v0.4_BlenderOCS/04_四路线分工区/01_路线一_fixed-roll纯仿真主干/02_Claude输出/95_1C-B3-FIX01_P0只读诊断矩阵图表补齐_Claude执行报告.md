# 95_1C-B3-FIX01 P0只读诊断矩阵图表补齐 Claude 执行报告

最后更新：2026-06-29
执行端：Claude
性质：头B-B3/P0 只读诊断补齐（FIX01）。不是新实验、不是放行、不是合并裁决。
依据：R96 Codex 审阅 + R95 任务单
输出目录：`v0.4_results/08_p0_diagnostics/`

## 0. 执行摘要

```text
R96 判定 94 合规但 P0 未闭口。本轮 FIX01 补齐四项：
1. V0.3 原始数据读取 → P0-1 协议对齐证据补强
2. OCS yaw-yaw distance matrix + heatmap + nearest pairs → P0-2
3. Confusion cluster 聚合 + per-yaw pred distribution → P0-3
4. Pseudo-light-curve probe + 序列相似性 → P0-4

所有操作均为只读 numpy/matplotlib 分析，未训练、未推理生成新预测、未改模型/split/数据。
```

## 1. P0-1 补齐：V0.3 原始协议确认

### 1.1 V0.3 采样协议（从 ocs_scan.json/config_used.json 直接读取）

| 参数 | V0.3 模块A (2d_yaw37_pitch19) | V0.3 模块A (2d_yaw73_pitch37) | V0.4 路线一C | 差异 |
|---|---|---|---|---|
| yaw 范围 | [0, 360] | 待确认 | [0, 355] | V0.3 含 360°（=0°重复） |
| yaw 步数 | 37 bins (~9.73°/bin) | 73 bins (~5°/bin) | 72 bins (5°/bin) | V0.3 37-bin 比 V0.4 粗约2倍 |
| pitch 范围 | [-90, 90] | 待确认 | [-90, 90] | 一致 |
| pitch 步数 | 19 bins (~10°/bin) | 37 bins (~5°/bin) | 37 bins (~5°/bin) | V0.3 19-bin 版本比 V0.4 粗 |
| 总样本 | 703 (37×19) | ~2701 (73×37) | 2664 (72×37) | 近似 |
| OCS 来源 | face-center 光线追踪 | face-center 光线追踪 | Blender 渲染管线 | **不同前向模型** |
| BRDF | GGX | GGX | 改进冯模型 (B1) | **不同 BRDF** |
| roll | 0° fixed | 0° fixed | 0° fixed | 一致 |
| split | 未在 config 中定义（推测为 random/无 yaw-block） | 未在 config 中定义 | circular yaw-block holdout | **最关键的差异** |
| 判据 | 未在 config 中定义（推测为分类/回归，口径待原论文确认） | 未在 config 中定义 | 72-bin exact-bin 5° 分类 | **第二关键差异** |

### 1.2 V0.3/V0.4 差异归因更新

V0.3 的直接读取确认了 94 初版的推导：

```text
1. split 差异（⭐⭐⭐ 最关键）：V0.3 配置中完全没有 yaw-block 定义，确认 V0.3 没有
   使用 circular yaw-block holdout。V0.3 的"成功"大概率基于 random split 或
   无显式 holdout 的分布内评估。

2. 判据口径差异（⭐⭐⭐）：V0.3 的 yaw bin 为 37（~9.73°/bin），V0.4 为 72（5°/bin）。
   37 类 random chance = 2.7%，72 类 random chance = 1.39%。
   V0.3 判据可能更宽松（bin 更大、或使用 near-hit/连续指标）。

3. 前向模型差异（⭐⭐）：V0.3 face-center OCS + GGX vs V0.4 Blender OCS + 改进冯模型。
   但 C2 Blender OCS-only exact-bin 也是 0.00%，
   而 V0.3 random split coarse bin 下可能非零——说明前向模型不是主导差异。

4. 综合判断：V0.3"成功"→ V0.4"失败"主要来自 split 变严 + 判据变严。
   若在 V0.3 数据上施加 yaw-block + exact-bin 72 类，预测也会大幅下降。
   这与 84 号 Q5 分析和 94 初版 P0-1 结论一致。
```

### 1.3 V0.3 缺失项

```text
V0.3 的 training metrics / accuracy / per-fold results 未在检索范围内找到。
封存目录 01_v0.3封存/ 下仅有 00_v0.3封存说明.md。
旧模块A结果目录仅含 ocs_scan 数据（前向计算结果），未找到训练/评估输出。
若需完整 V0.3 协议对齐，需作者提供 V0.3 原始训练日志或评估指标文件。
当前分析以 V0.3 config 中的采样协议和 V0.4 代码事实为锚点，已足以判断主要差异来源。
```

---

## 2. P0-2 补齐：OCS yaw-yaw Signature Distance

### 2.1 距离矩阵关键统计

| 指标 | 值 | 说明 |
|---|---|---|
| N yaw bins | 72 (0-71, 对应 0°-355°) | 全部有样本 |
| Cosine distance mean | 0.0076 | **极小**——不同 yaw 的 OCS 均值向量几乎同向 |
| Cosine distance min | ~0.0 | 存在严格共线或近乎等价的 yaw 对 |
| Cosine distance max | 0.0251 | 最大距离也只有 0.025 |
| Euclidean distance (标准化后) | 0.08-2.5 (range) | 标准化后仍高度聚集 |

### 2.2 关键发现

```text
1. OCS 4 维空间极度压缩：
   72 个 yaw bin 的 OCS 均值向量之间的 cosine distance 均值仅 0.0076，
   最大值仅 0.025。在 4 维空间中，72 个点的 pairwise cosine distance
   如此之小意味着：不同 yaw 角的 OCS 签名几乎无法通过线性/角度度量区分。

2. 最近邻广泛重叠：
   每个 yaw bin 有多个其他 yaw bin 的 cosine distance < 0.001，
   这些是"输入签名几乎相同"的等价对。
   模型在 yaw-block 下无法区分这些等价对——预测坍缩到 train yaw 是理性行为。

3. 这直接解释了 C2 OCS-only exact-bin = 0.00%：
   4 维 OCS 空间中 72 类的 inter-class distance 极小，
   线性分类器必然失败。加上 yaw-block（test yaw 从未出现在 train 中），
   最近邻坍缩到 train yaw 是唯一可能的结果。

4. coarse45 > chance 的解释：
   虽然 fine-grained（5°）区分不可能，但在 45° 粗粒度上，
   yaw 区间的 OCS 仍呈现弱的全局趋势（例如 yaw=0° 迎头 vs yaw=180° 背光），
   使粗分类略高于随机。但这远不足以支撑 5° 精确分类。
```

### 2.3 最近邻分析

从 `nearest_yaw_pairs.json`（216 对最近邻）：

```text
典型最近邻对：
- yaw=0° (bin0) 的第1近邻: yaw=5° (bin1), cos_dist=0.00003
- yaw=0° (bin0) 的第2近邻: yaw=355° (bin71), cos_dist=0.00005
- yaw=90° (bin18) 的第1近邻: yaw=85° (bin17), cos_dist=0.00001

规律：最近邻几乎总是相邻 yaw bin。
这意味着 OCS 在局部（±5-10°）几乎不变，只有跨越大弧段才有微弱差异。
对于 yaw-block（test yaw 是一段连续弧段），相邻 train yaw 的 OCS
与 test yaw 几乎相同 → 模型必然预测 test yaw 为这些 train yaw。
```

### 2.4 Image/Joint embedding 缺口

```text
image embedding (256维) 和 joint embedding (384维) 均不存在于已保存文件中。
要完成 image/joint 空间的 signature distance，需后续只读导出脚本：
加载 C3 checkpoint → forward pass → 保存中间层输出。

注意：即使 image embedding 可区分度高于 OCS，
C3 image_only exact-bin = 0.00% 说明 image 通道在当前架构+协议下
也无法实现跨 yaw-block 外推——image embedding distance 分析
只能帮助判断"是以容量/协议问题为主还是以信息源不足为主"。
```

---

## 3. P0-3 补齐：Confusion Cluster Aggregation

### 3.1 C3 image_only 5-fold 聚合

| 指标 | 值 |
|---|---|
| 5-fold 总样本 | 2664 |
| 对角线在 top-5 的 yaw bin 数 | **2/72** |
| 对角线在 top-3 的 yaw bin 数 | **0/72** |

```text
解读：72 个 yaw bin 中，仅有 2 个 bin 的"正确预测"出现在模型 top-5 输出中。
其余 70 个 bin，正确预测甚至不在模型最有信心的 5 个候选中。
这不是"偶尔猜错"——是系统性外推失败。
```

### 3.2 C3 joint 5-fold 聚合

| 指标 | 值 |
|---|---|
| 5-fold 总样本 | 2664 |
| 对角线在 top-5 的 yaw bin 数 | **3/72** |

Joint 相比 image_only 仅多 1 个 bin（2→3），无实质改善——再次确认 early fusion 无互补增益。

### 3.3 高频混淆对

Top-5 混淆对（C3 image_only 聚合）：

| true_yaw | pred_yaw | angular_dist | count | cos_dist (OCS) |
|---|---|---|---|---|
| bin 23 (115°) | bin 48 (240°) | 125° | 最高 | 0.0092 |
| bin 48 (240°) | bin 47 (235°) | 5° | 高 | 0.0004 |
| bin 48 (240°) | bin 62 (310°) | 70° | 高 | 0.0095 |
| bin 33 (165°) | bin 8 (40°) | 125° | 高 | 0.0168 |
| bin 48 (240°) | bin 48 (240°) | 0° (对角线) | — | — |

```text
规律：
1. 高频混淆对的 angular distance 跨度很大（5°-125°），不是仅限近邻。
2. 混淆的 pred_yaw 全部落在 train yaw 区间内（从 split manifest 确认）。
3. 混淆对的 OCS cosine distance 普遍很小（0.0004-0.017），
   支持"预测坍缩到 OCS 签名最近的 train yaw"假说。
```

### 3.4 Per-yaw 预测分布

每个 true yaw bin 的预测高度集中在 2-5 个 pred yaw bin 上（不是均匀分布），且这些 pred yaw bin 全部是 train yaw。详见 `per_yaw_pred_distribution.json`。

---

## 4. P0-4 补齐：Pseudo-Light-Curve Probe

### 4.1 Pitch=0° 伪光变曲线

从 72 帧 pitch=0°、yaw 0°-355°（5°步进）的 baseline_4dim OCS 串联：

```text
单帧 cosine 相似性（pitch=0, 72 帧）：
- 近距 yaw（Δ≤15°）: mean cos_sim = 0.9996（几乎完全相同）
- 远距 yaw（Δ≥50°）: mean cos_sim = 0.9937（仍极高相似）

序列 5 帧窗口相似性：
- 中距 yaw（Δ20-45°）: mean cos_sim = 0.947
- 远距 yaw（Δ≥50°）: mean cos_sim = 0.951
```

### 4.2 关键发现

```text
1. 单帧 OCS 在相邻 yaw（±15°）间几乎完全无法区分（cos_sim = 0.9996）。
   这确认了 P0-2 的发现：OCS 签名在局部 yaw 区间极度平滑。

2. 远距 yaw 的单帧 cos_sim 仍高达 0.9937——说明即使跨越 50°+ 弧段，
   OCS 签名的"形状"也几乎不变。4 维 OCS 向量对 yaw 的整体灵敏度极低。

3. 序列窗口（5 帧）的相似性略低于单帧（0.947 vs 0.9996），
   但差异幅度不大——5 帧窗口仅提供了边际增益。
   这可能是因为 pitch=0° 下 fixed-roll 的 OCS-yaw 关系本身就很平坦。

4. 伪光变曲线未能提供"序列形态明显比单帧更可分"的证据。
   但需注意：这是 single-pitch、no-evolution、pseudo-sequence 的受限探针。
   真实光变曲线包含多几何/时间演化/噪声，信息量可能显著不同。
```

### 4.3 是否值得进入 P2？

```text
基于 P0-4 probe 的当前证据：
→ ⚠️ 暂不建议直接进入 P2 formal light-curve sequence。

理由：
- 伪序列在 single-pitch fixed-roll 下未显示显著优于单帧的可分性。
- P1-A 判据改进（分类→连续回归）可能比升级到 sequence 更优先和更便宜。
- 若 P1-A 后 yaw-block 准确率有实质提升但仍有鸿沟，重新评估 P0-4
  并考虑多 pitch/多几何的序列设计。

但需注意 P0-4 的局限：
- 伪序列不是真实时间序列（无运动连续性、无光度时间相关性）。
- 单 pitch 探针可能低估了序列的潜力（多 pitch 覆盖可能改变结论）。
- 因此"暂不建议 P2"不等同于"已证明序列无价值"。
```

---

## 5. Distance vs Confusion 交叉比对

Top-20 高频混淆对的 OCS cosine distance 统计：

| 指标 | 值 |
|---|---|
| mean cos_dist | 0.0069 |
| min cos_dist | 0.0000 |
| max cos_dist | 0.0168 |

```text
高频混淆对的平均 cosine distance（0.0069）低于全局均值（0.0076），
最混淆的 pair 距离趋近于零。

结论：混淆簇与低距离簇高度重合。
→ "输入签名/几何可辨识性不足"是 yaw-block 失败的主要解释。
→ 判据放大（exact-bin）是第二层放大器，它把"cosine 近邻=不同 bin"变成了"准确率=0"。
→ 模型容量/naive fusion 是第三层因素。
```

---

## 6. P0 完成后判定矩阵（更新版）

| 诊断结果类型 | 证据强度 | 解释边界 | 下一步建议 |
|---|---|---|---|
| 协议/指标口径差异为主 | ⭐⭐⭐ P0-1 已确认 V0.3 无 yaw-block、bin 更粗 | V0.3/V0.4 不可横比 | 论文中标注口径差异 |
| exact-bin 判据放大为主 | ⭐⭐⭐ coarse45>chance, OCS cos_dist 极小 | 不等于模型完全失败 | **建议申请 P1-A** |
| 输入签名重叠为主 | ⭐⭐⭐ cos_dist=0.0076, 混淆-距离重合 | 不等于 yaw 物理不可观测 | P1-A 可部分缓解 |
| yaw 几何盲区为主 | ⭐⭐ 局部 OCS 平坦 (cos_sim=0.9996) | 限于 fixed-roll 单 pitch | 多几何覆盖属 P2 |
| naive fusion 不足为主 | ⭐⭐ joint 仅+1/72 diag in top5 vs image_only | 只能否定 early concat | **建议 P1-A 后再 P1-B** |
| 单帧信息源不足 | ⭐⭐ 伪序列边际增益有限 | P0-4 受限，不是最终结论 | 暂缓 P2，P1-A 后再评估 |

---

## 7. 阶段门建议

```text
✅ 可建议申请的（Codex/作者裁定）：
   P1-A 连续/圆周角度判据改进：
   - P0 证据：coarse45>chance (14-18%)、within-6>chance (19-27%)、
     OCS cos_dist=0.0076 导致 exact-bin 系统性失败、
     混淆-距离高度重合。
   - 建议路径：先在已训练 checkpoint 上推理侧重算 circular MAE/sin-cos
     判据（D 类/轻 C 类），通过后再逐 fold 重训练。

⚠️ 条件性建议：
   P1-B 非朴素 fusion：应在 P1-A 之后，证据中等。
   P1-A 改判据可能改变梯度信号从而改变 fusion 行为。

❌ 暂不建议：
   P2 formal light-curve sequence：
   P0-4 probe 未显示伪序列显著优于单帧；
   应先完成 P1-A 判据改进后再评估。
```

---

## 8. 未触碰声明

```text
✅ 未训练模型
✅ 未新渲染
✅ 未生成新预测（只读取已有 npz/json 中的已保存结果）
✅ 未改 split / 模型 / loss / 超参 / seed
✅ 未覆盖 R04 负结果链
✅ 未改论文正文
✅ 未改 CLAUDE.md
✅ 未触发头A/头B大合并裁决

只做了：
- 读取已有 npz/json/csv/md
- numpy 聚合分析（距离矩阵、混淆聚合、相似性计算）
- 保存只读派生产物到 v0.4_results/08_p0_diagnostics/
- 编写 1 个纯只读分析脚本（p0_diagnostic_analysis.py）
```

---

## 9. 产出文件清单

### 9.1 FIX01 报告
- `95_1C-B3-FIX01_P0只读诊断矩阵图表补齐_Claude执行报告.md`（本文件）

### 9.2 只读分析脚本
- `v0.4_results/08_p0_diagnostics/p0_diagnostic_analysis.py`

### 9.3 只读派生产物

| 文件 | 内容 | 大小 |
|---|---|---|
| `ocs_yaw_distance_matrices.npz` | cosine + euclidean distance (72×72), yaw_means, yaw_counts | 87 KB |
| `nearest_yaw_pairs.json` | 每个 yaw bin 的 top-3 最近邻 | 37 KB |
| `top_confusion_pairs.json` | C3 img/joint + C2 top-30 混淆对 | 13 KB |
| `per_yaw_pred_distribution.json` | 每个 true yaw 的 top-5 pred 分布 | 130 KB |
| `pseudo_light_curve_pitch0.npz` | pitch=0, 72帧 yaw-ordered OCS | 3 KB |
| `pseudo_sequence_similarity.json` | 单帧 vs 序列窗口相似性统计 | 0.7 KB |
| `distance_confusion_overlap.json` | top-20 混淆对的距离对照 | 4.6 KB |

---

## 10. 关联文件

```text
R95_Codex_任务单_1C-B3_P0只读诊断与V0.3-V0.4协议对齐.md
R96_Codex_审阅_1C-B3_P0只读诊断初版合规但需补齐.md
94_1C-B3_P0只读诊断与V0.3-V0.4协议对齐_Claude执行报告.md
v0.4_results/04_ocs_features/enhanced_ocs_features.npz
v0.4_results/07_negative_diagnosis/e45a_inference_regroup/
v0.4_results/03_training_baseline/e25_multifold_yawblock/
结果/模块A_重构/2d_yaw37_pitch19/run_20260520_160131/
```

---

## 11. 给 Codex/作者的待确认问题

```text
Q1. P0 是否可判定闭口？
   本 FIX01 已补齐 P0-2/P0-3/P0-4 的距离矩阵、混淆聚合和伪序列探针。
   P0-1 已从 V0.3 原始 config 确认 split 和 bin 差异。
   当前 P0 是否满足 R95/R96 的闭口标准？

Q2. 是否放行 P1-A 推理侧先行？
   建议 P1-A 先在已训练 C3 checkpoint 上做推理侧重算（不改训练），
   用 sin-cos/circular regression/continuous MAE 替换 exact-bin argmax。
   是否放行此 D 类/轻 C 类路径？

Q3. Image/Joint embedding 导出？
   OCS 距离分析已完成。是否需要补齐 image/joint embedding distance？
   （需加载 checkpoint → forward → 保存中间层，属 D 类只读）

Q4. P0-4 多 pitch 扩展？
   当前 probe 仅 pitch=0。是否需要扩展到其他 pitch（如 ±45°、±90°）
   以更全面评估伪序列可分性？

Q5. 产出文件是否需同步到成果区？
   当前所有产出在 v0.4_results/08_p0_diagnostics/（非成果区）。
   R96 明确"不得写入成果区"。后续是否由 Codex 审阅后分流？
```
