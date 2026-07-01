# P1-A 阶段门判断矩阵

最后更新：2026-06-29

## 0. 阶段门裁决

基于 P1-A 只读指标重算结果，当前阶段门判断：

```text
✅ P1-A 第一阶段（只读指标重算）已完成。
⚠️ P1-A 指标重构有限价值，但不支持"模型补救成功"或"外推问题已解决"。
🔍 建议路径：P1-A 结果可作为论文指标重构材料，不建议进入训练侧改进。
```

## 1. 核心发现总结

| 指标维度 | 发现 | 相对 Random Baseline | 阶段门信号 |
|---|---|---|---|
| **Exact-bin (72 类)** | C2/C3 均为 **0.00%** | Random = 1.39% | ⭐⭐⭐ 严格负结果，确认 yaw-block 外推失败 |
| **Circular MAE (bins)** | C2=17.85, C3_img=16.29, C3_joint=16.28 | Random=18.05 | ⚠️ 略优于随机，但边际改善极小（0.2-1.8 bins） |
| **Within-6 bins (30°)** | C2=16.1%, C3_img=25.6%, C3_joint=26.5% | Random=18.1% | ⚠️ C3 比 C2 提升约 10%，但仍接近随机水平 |
| **Coarse45 (45°, 8 类)** | C2=11.7%, C3_img=18.0%, C3_joint=18.2% | Random=12.5% | ⚠️ C3 比 random 提升 5-6%，比 C2 提升 6-7% |
| **Coarse90 (90°, 4 类)** | C2=24.0%, C3_img=25.1%, C3_joint=24.6% | Random=25.0% | ❌ 与随机基线无实质差异 |

## 2. 对 R99 必须回答问题的判断

### Q1. exact-bin 0% 下，circular MAE / median AE 是否仍明显优于 random？

**答：不明显优于 random。**

- C2 baseline_4dim: circular MAE = 17.85 bins，random = 18.05 bins，**仅优 0.2 bins (1.1%)**
- C3 image_only: circular MAE = 16.29 bins，random = 18.05 bins，**优 1.76 bins (9.7%)**
- C3 joint: circular MAE = 16.28 bins，random = 18.05 bins，**优 1.77 bins (9.8%)**

结论：C3 相比 random 有约 10% 的边际改善，但绝对误差仍高达 16-17 bins（80-85°），不能读成"外推成功"。C2 OCS-only 与 random 几乎无差异。

### Q2. within-1/2/3/6 bins 是否高于 chance/random baseline？

**答：C3 在 within-1/2/3 略高于 random，within-6 高约 7-8%。**

| Within-k | C2 | C3_img | C3_joint | Random | C3 vs Random |
|---|---|---|---|---|---|
| Within-1 bin (5°) | 3.6% | 6.6% | 6.7% | 4.2% | +2.4-2.5% |
| Within-2 bins (10°) | 5.7% | 12.3% | 13.0% | 6.9% | +5.4-6.1% |
| Within-3 bins (15°) | 8.2% | 17.1% | 17.7% | 9.7% | +7.4-8.0% |
| Within-6 bins (30°) | 16.1% | 25.6% | 26.5% | 18.1% | +7.5-8.4% |

结论：C3 在 within-1/2/3/6 均高于 random 5-8%，显示精细角度区分能力略优于随机。但绝对值仍低（within-3 仅 17-18%），不能读成"精确外推已实现"。

### Q3. coarse45/coarse90 是否稳定高于 chance/random baseline？

**答：coarse45 C3 高于 random 约 5-6%，coarse90 与 random 无实质差异。**

- **Coarse45 (45°, 8 类)**：
  - C2 = 11.7%, C3_img = 18.0%, C3_joint = 18.2%
  - Random = 12.5%
  - C3 高于 random 5.5-5.7%，C2 **低于** random
- **Coarse90 (90°, 4 类)**：
  - C2 = 24.0%, C3_img = 25.1%, C3_joint = 24.6%
  - Random = 25.0%
  - 三者与 random 无实质差异（-1% 至 +0.1%）

结论：coarse45 C3 略优于 random，但 coarse90 已退化到 random 水平。这支持 R82/E45B 的"粗粒度外推存在弱信号、细粒度外推失败"叙事，但不支持"粗粒度外推成功"。

### Q4. C3 image_only 与 joint 相比 C2 OCS-only 是否有任何一致提升？

**答：C3 相比 C2 有一致但有限的提升。**

| 指标 | C2 → C3_img 提升 | C2 → C3_joint 提升 | 解释 |
|---|---|---|---|
| Circular MAE | -1.56 bins (-8.7%) | -1.57 bins (-8.8%) | C3 略优 |
| Within-6 bins | +9.5% | +10.4% | C3 显著优于 C2 |
| Coarse45 | +6.3% | +6.4% | C3 显著优于 C2 |
| Coarse90 | +1.0% | +0.6% | 提升消失 |

结论：C3 image/joint 相比 C2 OCS-only 在 circular MAE、within-6、coarse45 均有一致提升（6-10%），但在 coarse90 提升消失。这说明**图像通道相比 OCS 确实携带更多姿态信息**，但在当前架构+协议下仍无法实现有效外推。

Image_only 与 joint 几乎无差异（circular MAE 差 0.01 bins，within-6 差 0.9%），再次确认 **early concat fusion 无互补增益**。

### Q5. 错误是否集中在特定 yaw block、pitch 或 fold？

**答：当前只读指标重算未按 yaw block 或 pitch 分层，暂无法回答此问题。**

缺口：
- 现有 samples.npz 只有 record_id、pred_bin、true_bin，未包含 split manifest 的 yaw block 标签。
- 未按 pitch 分层统计。
- 若需分层诊断，需后续只读脚本：读取 split manifest → 标注 train/test yaw block → 按 block/pitch 重算指标。

### Q6. P1-A 结果是否足以支持后续第二阶段？

**判断矩阵：**

| 后续路径选项 | 是否支持 | 理由 |
|---|---|---|
| a. 仅作为论文指标重构材料 | ✅ 支持 | C3 略优于 random，coarse45 C3=18% vs random=12.5%，可承接 R82/E45B 的 extrapolation gap 叙事 |
| b. 申请 logits/checkpoint 只读导出 | ⚠️ 条件支持 | 若需分析 soft prediction、expected yaw、top-k alternatives，可申请 logits 导出；但当前 argmax 指标已足够诊断 |
| c. 申请真正训练侧 continuous/circular head | ❌ 不支持 | Circular MAE 仅优 random 1-2 bins，改判据不太可能根本改变外推失败；P0 诊断已指向输入签名重叠和 yaw-block 协议本身 |
| d. 停止 P1-A，不再补救 | ✅ 建议采纳 | P1-A 指标重构完成论文叙事所需材料，训练侧改进边际收益低，不建议继续 |

## 3. 阶段门建议

```text
✅ 接收 P1-A 第一阶段结果为论文指标重构材料。
✅ P1-A 支持以下论文叙事：
   - exact-bin 0% 是 yaw-block 外推的严格负结果；
   - circular MAE、within-k、coarse45 略优于 random，显示弱外推信号；
   - C3 相比 C2 一致提升 6-10%，图像通道携带更多姿态信息；
   - image_only 与 joint 无差异，early concat 无互补增益；
   - coarse90 退化到 random，粗粒度外推有界。

⚠️ 不支持以下论文叙事：
   - 模型外推问题已解决；
   - circular/coarse 指标显示"成功外推"；
   - joint fusion 实现互补。

❌ 不建议进入 P1-A 第二阶段（训练侧 continuous/circular head）：
   - Circular MAE 仅优 random 1-2 bins，改判据收益有限；
   - P0 诊断已指向输入签名重叠（OCS cos_dist=0.0076）和 yaw-block 协议本身；
   - 判据改进不改变输入可辨识性不足的根本问题。

⚠️ 条件允许后续 D 类只读导出（不阻塞主链）：
   - 若需分析 soft prediction、logits、embedding，可另设阶段门申请 checkpoint forward；
   - 若需按 yaw block/pitch 分层诊断，可另设只读脚本读取 split manifest 重算。

🔍 建议下一步：
   - 将 P1-A 结果纳入头B材料，不再进入 P1-A 训练侧改进；
   - 继续等待头A/头B大合并裁决，或直接进入论文指标重构与图表规划。
```

## 4. 关联文件

```text
R99_Codex_裁决_1C-B3闭口后放行P1-A只读指标重算.md
v0.4_results/09_p1a_metric_recompute/p1a_channel_fold_metrics.csv
v0.4_results/09_p1a_metric_recompute/p1a_channel_aggregated_stats.csv
v0.4_results/09_p1a_metric_recompute/p1a_coarse_bin_metrics.csv
v0.4_results/09_p1a_metric_recompute/p1a_circular_error_distribution.csv
v0.4_results/09_p1a_metric_recompute/p1a_within_k_curve.csv
v0.4_results/09_p1a_metric_recompute/p1a_random_baseline.md
```
