# 三轴搜索种子选择规则（seed_selection_rules）

最后更新：2026-07-01
来源：R129 子任务 C；生成脚本 `scripts/c_seed_extraction.py`（只读，可复现）。

## 1. 总原则

- 种子从路线一 C 已通过结果（11/13/16/17 + 01_fullrun）筛出，**不做盲目全空间扫描**。
- 全部基于 fixed-roll (roll=0) 基线；每类种子给出建议 roll 扫描范围，供 P1 使用。
- 每类默认取 top-8（`N=8`）；数据本身不足时取全部（如 image-hard 仅 2 个）。
- 主表 `seeds/attitude_master_fixedroll.csv`（2664 姿态）与派生表
  `seeds/attitude_master_derived.csv`（加 local_contrast / glint_flag）为复现基础。

## 2. 九类种子规则

| 类别 | 选择规则 | 来源字段 | 建议 roll 范围 |
|---|---|---|---|
| bright-seed | phase63 `ocs_total` 最高 top-N | 01_fullrun OCS | -60..+60 step15 |
| dark-seed | `ocs_total`>0 中最低 top-N | 01_fullrun OCS | -30..+30 step15 |
| high-info-seed | `gain_g1_to_g5` 最大 top-N | 16 D4 gain | -60..+60 step15 |
| low-info-seed | ambiguous-flux 且 `pdb_cand_yaw_spread` 最大 | 13 hardcase + joined | -30..+30 step15 |
| ocs-hard-seed | `ocs_g5_err` 最大 top-N（多几何仍难） | 16 D4 gain | -60..+60 step15 |
| image-hard-seed | hardcase 含 image-hard(image_only) | 13 hardcase | -30..+30 step15 |
| disagreement-seed | disagreement-hard 且 |gain| 最大 | 13 hardcase + 16 D4 | -45..+45 step15 |
| roll-sensitive-seed | M-roll `err(±30)-err(±15)` 最大 | 17 mroll (G1 ocs_only) | -30..+30 step15 加密 |
| robust-easy-seed | robust-easy 且亮度高（正对照） | 13 hardcase | -60..+60 step15 |

## 3. 为什么值得 roll 扩展

- bright/high-info：检验最亮点、高可分点在 roll 下是否迁移（fixed-roll 结论稳定性）。
- low-info/ocs-hard/image-hard/disagreement：检验困难区在 roll 下是否加剧或缓解。
- roll-sensitive：M-roll 已显示 ±30° 敏感，这些点最可能推翻 fixed-roll 结论，优先加密。
- robust-easy：正对照，提供 roll 稳健性基线。

## 4. 红线

- 种子是"值得进一步观测/扫描"的候选，不是"已验证的最优反演姿态"。
- 最亮 ≠ 高信息（见 `text/brightness_vs_information_boundary.md`）。
- 本轮只提取种子与建议范围，不执行任何 roll 渲染或训练。
