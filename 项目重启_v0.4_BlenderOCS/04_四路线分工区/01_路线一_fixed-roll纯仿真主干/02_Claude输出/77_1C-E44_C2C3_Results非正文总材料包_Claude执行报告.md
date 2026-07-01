# 77_1C-E44_C2C3_Results非正文总材料包_Claude执行报告

执行端：Claude  
任务编号：1C-E44  
执行日期：2026-06-26  

---

## 0. 任务状态

```text
1C-E44：COMPLETED
本报告整合成果区 08/09/10/11 的稳定事实，不运行训练，不改代码，不写论文正文段落
```

---

## 1. 成果区来源

| 成果区文件 | 内容 | 状态 |
|-----------|------|------|
| 08_C1C2_OCS-only证据包与claim边界_R62通过 | C1/C2 稳定证据 + claim 边界 | R62 |
| 09_C1C2_OCS-only_Results非正文材料包_E35_R65通过 | Table 1-3 + Figure 1-4 plan + Results skeleton | R65 |
| 10_C1C2_OCS-only图表与SI资产_E36_R69通过 | Figure 2 + S2 per-fold table | R69 |
| 11_C2C3三通道负结果证据包_E43_R77通过 | C3 per-fold + 三通道对照 + claim | R77 |

---

## 2. 三通道核心数值（单一事实源）

| 通道 | 协议 | Fold/Run 数 | mean yaw_acc | mean pitch_acc | mean yaw_cmae |
|------|------|:---:|:---:|:---:|:---:|
| C2 enhanced OCS-only | 13 configs × MLP | 13 × 5 | 0.00% | 2.56–4.37% | 80–120° |
| C3 image_only | fixed 6-layer CNN | 5 | 0.00% | 21.20% | 81.44° |
| C3 joint | CNN + raw 4-dim OCS early fusion | 5 | 0.00% | 19.42% | 81.39° |

稳定结论：

```text
在已执行的 C2/C3 三条固定协议通道与 circular yaw-block holdout 下，
cross-yaw exact-bin yaw accuracy 全部为 0.00%。
```

---

## 3. Table / Figure / SI 总清单

### 3.1 表格清单

| 编号 | 内容 | 数据来源 | 状态 |
|------|------|----------|------|
| Table 1 | OCS feature configuration overview（14 configs: name, class, dim, feature_keys） | feature_definitions.json | E35 已有草案 |
| Table 2 | C2 OCS-only screening results（13 configs: yaw_acc, yaw_cmae, within-3, pitch_acc） | c2_screening_summary.json | E35 已有草案 |
| Table 3 | C2 results grouped by claim_class（photometric / visibility / mixed） | c2_screening_summary.json | E35 已有草案 |
| Table 4 | C3 formal per-fold results（image_only + joint, 10 rows） | c3_image/joint_formal_5fold | E43 已有草案 |
| Table 5 | C2/C3 three-channel comparison（含 OCS 口径标注列） | 综合 08/11 | E43 已有草案 |
| S2 | C2 per-fold supplementary table（65 rows） | c2_screening per-fold JSON | E36 已生成 |

### 3.2 图表清单

| 编号 | 内容 | 数据来源 | 状态 |
|------|------|----------|------|
| Figure 1 | Feature extraction pipeline 流程图 | feature_definitions.json | E35 提议，待生成 |
| Figure 2 | Circular yaw-block holdout strategy 示意图 | split_manifest | E36 已生成（PNG+PDF） |
| Figure 3 | Yaw CMAE vs within-3 scatter（按 claim_class 着色） | c2_screening_summary.json | E35 提议，待生成 |
| Figure 4 | Pitch accuracy by config grouped bar chart | c2_screening_summary.json | E35 提议，待生成 |
| Figure 5 | C2/C3 three-channel yaw_acc 对照（全 0，紧凑图/suppl） | 综合 | R77 建议降级为 suppl |

**Figure 优先级建议**：

```text
正文优先：Figure 2（holdout 策略）、Figure 3（CMAE scatter）
降级 suppl 或紧凑嵌入：Figure 5（全 0 yaw_acc bar chart）
Figure 1 为 Methods 示意，Figure 4 为二级诊断
```

### 3.3 SI 清单

| 编号 | 内容 | 状态 |
|------|------|------|
| S1 | Raw feature definitions and pre-registered constants | E35 已有 |
| S2 | C2 per-fold results table（65 rows） | E36 已生成 CSV |
| S3 | C3 per-fold detail（10 folds × detail JSON 关键字段） | 待提取 |
| S4 | Training curves（C2 65 runs + C3 10 runs） | 待提取 |
| S5 | Overlap reports（C2 + C3 all folds strict status） | 已有 JSON |

---

## 4. OCS 口径区分（关键）

```text
C2 enhanced OCS-only  ≠  C3 joint raw 4-dim OCS
```

| | C2 enhanced OCS | C3 raw 4-dim OCS |
|------|------|------|
| 数据源 | enhanced_ocs_features.npz | manifest JSONL |
| 内容 | ratios, logs, densities, pixel fracs（1-13 dim） | ocs_total, ocs_jinshuzhuti, ocs_taiyangnengban, ocs_yinshenban（4 dim） |
| 参与通道 | C2 OCS-only（13 configs） | C3 joint（OCS encoder 输入端） |
| 论文标注 | "enhanced OCS features" | "raw 4-dim OCS from manifest" |

后续 Methods/Results/Table/Figure 中必须分开标注，不得合并为同一 OCS-only 口径。

---

## 5. Claim 边界速查

### 可写

```text
1. C2/C3 三通道在 cross-yaw exact-bin 泛化上全部返回 0.00% —— controlled negative result。
2. joint early fusion 未改善 exact-bin yaw accuracy 超越 image_only。
3. pitch_acc 为二级诊断，不改变 yaw-based null verdict。
4. random split yaw_acc ~65-70% 确认分布内可学；失败模式是跨 yaw 泛化。
5. 结果限定于 phase63 fixed-roll / circular yaw-block / 固定协议范围。
```

### 不可写

```text
1. OCS 或图像通道在物理上不含姿态信息。
2. joint 融合/图像/OCS 在所有模型下无效。
3. 结果外推到真实 GEO / 三轴姿态 / 暗室实验。
4. C2 enhanced OCS 与 C3 raw 4-dim OCS 是同一结果链。
5. E25 = C3 正式 image baseline。
6. 该结果否定了 OCS+图像互补性假设本身（仅否定当前协议下 exact-bin yaw 互补）。
```

### 诊断措辞

```text
"possible overfit" → train/val loss separation 与 cross-yaw domain shift 相容
pitch_acc 较高 → 二级诊断，不改变 yaw-based null verdict
within-3 → 辅助 coarse localization 诊断，不替代 exact-bin accuracy
```

---

## 6. 作者待确认事项

1. 是否接受 Figure 5（全 0 bar chart）降级为 supplementary 或紧凑嵌入？
2. S3（C3 per-fold detail）和 S4（training curves）是否需要立即提取，还是等论文写作阶段再生成？
3. Table 4/5 是否与 Table 1-3 合并为统一编号体系（Table 1–5），还是分 C2/C3 两套？

---

## 7. 红线确认

| 红线 | 状态 |
|------|------|
| 不运行训练 | ✅ |
| 不运行 raw 4-dim ocs_only / --mode all | ✅ |
| 不修改代码/数据/split/模型/结果 JSON | ✅ |
| 不写论文正文正式段落 | ✅ |
| 不外推到真实 GEO/三轴/暗室/所有模型 | ✅ |
| C2 enhanced OCS ≠ C3 raw 4-dim OCS 已标注 | ✅ |
| 报告简短，不复述全历史 | ✅ |

---

**执行端签名**：Claude  
**下一步**：交 Codex 审阅 E44 总材料包
