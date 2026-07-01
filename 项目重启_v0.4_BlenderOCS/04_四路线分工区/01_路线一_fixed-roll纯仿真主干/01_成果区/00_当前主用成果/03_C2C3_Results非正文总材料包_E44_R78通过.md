# C2/C3 Results 非正文总材料包（E44 + R78 稳定版）

最后更新：2026-06-26  
状态：R78 Codex 审阅通过  
性质：路线一 C Results 规划资产，不是论文正文正式段落

## 1. 稳定来源

```text
成果区稳定文件：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/01_成果区/
  08_C1C2_OCS-only证据包与claim边界_R62通过.md
  09_C1C2_OCS-only_Results非正文材料包_E35_R65通过.md
  10_C1C2_OCS-only图表与SI资产_E36_R69通过.md
  11_C2C3三通道负结果证据包_E43_R77通过.md

Codex 审阅：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/
  R78_Codex_审阅_1C-E44通过_C2C3_Results非正文总材料包稳定.md

Claude 输出：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  77_1C-E44_C2C3_Results非正文总材料包_Claude执行报告.md
```

若本文件与 E44 Claude 原报告存在口径差异，以本文件和 R78 为准。

## 2. 三通道核心数值

| 通道 | 协议/输入 | Fold/Run 数 | mean yaw_acc | mean pitch_acc | mean yaw_cmae |
|---|---|---:|---:|---:|---:|
| C2 enhanced OCS-only | 13 configs x fixed MLP | 13 x 5 | 0.00% | 2.56-4.37% | 80.36-120.26 deg |
| C3 image_only | fixed 6-layer CNN | 5 | 0.00% | 21.20% | 81.44 deg |
| C3 joint | CNN + raw 4-dim OCS early fusion | 5 | 0.00% | 19.42% | 81.39 deg |

稳定结论：

```text
在已执行的 C2/C3 三条固定协议通道与 circular yaw-block holdout 下，
cross-yaw exact-bin yaw accuracy 全部为 0.00%。
```

限定范围：

```text
phase63 fixed-roll data
circular yaw-block holdout
C2 fixed MLP enhanced OCS-only protocol
C3 fixed 6-layer CNN image_only protocol
C3 fixed early-fusion image + raw 4-dim OCS joint protocol
```

## 3. Table 清单

| 编号 | 内容 | 数据来源 | 状态 |
|---|---|---|---|
| Table 1 | OCS feature configuration overview | feature_definitions.json | E35 草案 |
| Table 2 | C2 OCS-only screening results | c2_screening_summary.json | E35 草案 |
| Table 3 | C2 grouped results by claim_class | c2_screening_summary.json | E35 草案 |
| Table 4 | C3 formal per-fold results | c3_image/joint_formal_5fold | E43 草案 |
| Table 5 | C2/C3 three-channel comparison with OCS input spec | 成果区 08/11 | E43 草案 |
| S2 | C2 per-fold supplementary table, 65 rows | c2 per-fold JSON | E36 已生成 |

编号为候选体系，不是最终投稿编号。

## 4. Figure 清单

| 编号 | 内容 | 数据来源 | 状态 | 优先级 |
|---|---|---|---|---|
| Figure 1 | Feature extraction pipeline | feature_definitions.json | 待生成 | Methods 候选 |
| Figure 2 | Circular yaw-block holdout strategy | split_manifest | 已生成 PNG/PDF | 正文优先 |
| Figure 3 | Yaw CMAE vs within-3 scatter | c2_screening_summary.json | 待生成 | 正文候选 |
| Figure 4 | Pitch accuracy by config grouped bar chart | c2_screening_summary.json | 待生成 | 二级诊断 |
| Figure 5 | C2/C3 three-channel yaw_acc comparison | 综合 08/11 | 待决定 | 建议降级 |

Figure 5 全 0 yaw_acc 图信息量低，建议降级为 supplementary 或紧凑嵌入，不作为正文主图。

## 5. SI 清单

| 编号 | 内容 | 状态 |
|---|---|---|
| S1 | Raw feature definitions and pre-registered constants | E35 已有 |
| S2 | C2 per-fold results table, 65 rows | E36 已生成 CSV |
| S3 | C3 per-fold detail, 10 folds x key fields | 待提取/待作者确认 |
| S4 | Training curves, C2 65 runs + C3 10 runs | 待提取/待作者确认 |
| S5 | Overlap reports, C2 + C3 strict status | JSON 已有，待整理 |

本文件不等于完整 SI 资产包。S3/S4/S5 是否生成和何时生成需另行确认或放行。

## 6. OCS 口径速查

```text
C2 enhanced OCS-only != C3 joint raw 4-dim OCS
```

| 项 | C2 enhanced OCS | C3 raw 4-dim OCS |
|---|---|---|
| 数据源 | enhanced_ocs_features.npz | manifest JSONL |
| 内容 | ratios, logs, densities, pixel fracs, 1-13 dim | ocs_total, ocs_jinshuzhuti, ocs_taiyangnengban, ocs_yinshenban |
| 参与通道 | C2 OCS-only | C3 joint OCS encoder input |
| 标注 | enhanced OCS features | raw 4-dim OCS from manifest |

不得合并为同一 OCS-only 结果链。

## 7. Claim 速查

可写：

```text
C2/C3 三通道在 cross-yaw exact-bin 泛化上全部返回 0.00%，构成 fixed-protocol controlled negative result。
Joint early fusion 未改善 exact-bin yaw accuracy 超越 image_only。
Pitch accuracy 与 within-3 是二级诊断，不改变 yaw-based null verdict。
Random split yaw_acc 约 65-70% 说明分布内可学；失败模式是跨 yaw 泛化。
```

不可写：

```text
OCS 或图像通道在物理上不含姿态信息。
joint、图像或 OCS 在所有模型下无效。
结果外推到真实 GEO、三轴姿态或暗室实验。
C2 enhanced OCS 与 C3 raw 4-dim OCS 是同一结果链。
E25 = C3 正式 image baseline。
该结果否定 OCS+图像互补性假设本身。
```

诊断措辞：

```text
possible overfit -> train/val loss separation 与 cross-yaw domain shift 相容
pitch_acc 较高 -> 二级诊断，不改变 yaw-based null verdict
within-3 -> coarse localization 辅助诊断，不替代 exact-bin accuracy
```

## 8. 作者待确认事项

```text
1. Figure 5：降级为 supplementary / 紧凑嵌入正文 / 暂不使用？
2. S3/S4：现在提取 / 写作阶段再提取？
3. 编号体系：统一 Table 1-5 + Figure 1-5 / C2 与 C3 分组编号？
```

## 9. 当前未放行

```text
new training
raw 4-dim ocs_only
--mode all
post-hoc architecture or hyperparameter search
new figure/table generation beyond existing assets
论文正文正式改写
三轴小项目、路线二/三/四扩展
```
