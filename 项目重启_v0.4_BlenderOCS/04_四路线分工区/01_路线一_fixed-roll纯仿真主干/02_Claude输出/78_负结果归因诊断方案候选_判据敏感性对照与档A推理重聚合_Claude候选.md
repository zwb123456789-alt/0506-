# 负结果归因诊断方案候选：判据敏感性对照与档 A 推理重聚合

- 编号：78（Claude 输出候选，非正式 E 编号）
- 性质：**执行候选 + 给 Codex 的放行请示**，不是放行、不是裁决、不是验收
- 待处理：交 Codex 审阅，由 Codex 决定是否放行、是否赋正式 E 编号
- 适用范围：路线一 C，phase63 fixed-roll，circular yaw-block holdout 体系

> 红线声明：本文件不构成任何放行或阶段门判断；档 A/档 B 均须经 Codex 放行后才能执行。本方案不外推真实 GEO / 三轴 / 暗室，所有结论仍限定 phase63 fixed-roll。

---

## 1. 背景与待解地基问题

当前三通道在 circular yaw-block holdout + 72-bin exact-yaw 判据下的稳定结论（R77/R78）：

| 通道 | yaw exact-acc | pitch acc | yaw CMAE |
|---|---|---|---|
| C2 enhanced OCS-only（13 config × 5 fold = 65 run） | 0.00% | 2.56–4.37% | 80.36–120.26° |
| C3 image-only（5 fold） | 0.00% | 21.20% | 81.44° |
| C3 joint（raw 4-dim early fusion，5 fold） | 0.00% | 19.42% | 81.39° |

对照事实：random split（分布内）yaw_acc ≈ 65–70%（可学），circular yaw-block holdout 下 exact-bin 归零。

**尚未闭环的核心问题**：当前 0% 无法区分以下两种成因，而它是论文成立的地基。

1. **判据成因**：cross-yaw holdout + 72-bin（5°）exact 分类，本质要求模型对未见过的整块 yaw 区间做精确外推，0% 可能由判据过严决定，而非物理决定。
2. **信息成因**：yaw 信息在该受控条件下确实不可跨域恢复。

辅助信号：pitch_acc 21.20% 远高于随机，yaw 为 0%——存在 **yaw/pitch 信息各向异性**，这本身是更可解释、更可发表的结构性发现，需要诊断证据支撑。

---

## 2. 诊断目标（要回答的 3 个问题）

- Q1 判据 vs 信息：放宽判据（coarse-bin / within-k / CMAE）后，circular holdout 下 yaw 是否仍≈随机？
- Q2 外推 vs 无信息：把整块 holdout 换成 interleaved holdout（邻域可见）后，yaw 精度能否恢复？能恢复 → 问题是"外推不能"而非"无信息"。
- Q3 互补性是否存在：在任一更宽容的 (split, 判据) 格子里，joint 是否相对 image-only 出现可观增益？

---

## 3. 对照矩阵设计（判据轴 × split 轴 × 三通道）

每个格子对 OCS-only / image-only / joint 三通道各评一次。

| split \ 判据 | exact-bin(72,5°) | coarse-bin(30°,45°) | within-k(±1/±2/±3/±6) | CMAE + 混淆矩阵 |
|---|---|---|---|---|
| circular yaw-block holdout（现有，最严） | 已知 0% | 待测 | within-3 已有 | CMAE 已有，混淆矩阵待测 |
| interleaved holdout（邻域可见，新） | 待测 | 待测 | 待测 | 待测 |
| random split（分布内上界，现有 65–70%） | 部分已知 | 待测 | 待测 | 待测 |

判据定义：

- exact-bin：72 bins，每 5°（现有）。
- coarse-bin：把预测/真值 bin 重映射到 12 bins(30°) 与 8 bins(45°) 再算 accuracy。
- within-k tolerance：circular 距离 ≤ k 个 bin 计为正确，k ∈ {1,2,3,6}。
- CMAE：circular mean absolute error（连续主指标，弱化分类判据偏置）。
- 混淆矩阵：完整 yaw 混淆矩阵，重点看预测是否系统性坍缩到训练见过的 yaw 区间（外推坍缩特征）。

---

## 4. 档 A：免训练推理重聚合（覆盖 circular holdout 整行 + 后处理判据）

定位：**只做前向推理 + 后处理，不重新训练**，因此不触碰"禁止新训练"红线；但仍会运行模型、产生新结果产物，故请 Codex 放行后再执行。

可行性依据（已只读核查）：

- 训练代码：`06_v0.4_code/07_training/`（C2 `train_c2_screening.py`；C3 `train_baseline.py`；split `split_dataset.py`）。
- checkpoint 全部在盘：C2 `v0.4_results/05_c2_screening/` 共 14 config × 5 fold = 70 个 `*_fold{0-4}_checkpoint.pt`；C3 `v0.4_results/06_c3_preflight/` 共 image 5 + joint 5 + smoke 1 个 `checkpoint_*.pt`。
- 权重存于 ckpt 的 `model_state`；split 由 manifest + `--train-split-manifest` 复现；yaw/pitch 均为分类 head，`evaluate()` 内存中本就有 `all_*_logits / all_*_true`。

档 A 任务：

1. 新增一个**独立只读推理脚本**（不改训练代码）：建模型 → `load_state_dict` → 按原 manifest 复现 test split → 前向 → `np.savez` 落盘逐样本 `(yaw_pred_bin, yaw_true_bin, pitch_pred_bin, pitch_true_bin)`（如有需要并存 logits）。
2. 后处理脚本：从逐样本预测计算 coarse-bin acc、within-k、CMAE 分布、完整混淆矩阵，按"通道 × 判据"汇总成表。
3. **内置一致性自检（先行门）**：先用推理脚本复算 exact-bin yaw/pitch acc，与现有 result.json / detail.json 对齐。对齐后才认为推理链可信，再扩展判据。
   - 注意：checkpoint 存的是 last-epoch 权重（非 best-epoch）；需确认现有落盘指标同为 last-epoch，否则先解释差异来源再继续。

档 A 预期判定：

- 若 coarse-bin / within-k 在 circular holdout 下 yaw 仍≈随机 → 支撑"yaw 不可跨域恢复"为强负结果，可写入正文。
- 若显著高于随机 → 原 0% 含 exact-bin 判据过严成分，结论与 framing 必须改写。

---

## 5. 档 B：需新训练放行（补全矩阵另两行）

定位：**触碰"禁止新训练"红线，须 Codex 显式放行**。建议档 A 完成、确有必要后再申请。

1. random split 三通道重训：检验分布内 joint 是否相对 image-only 出现互补增益（回答 Q3 的上界）。
2. interleaved holdout 三通道重训：每隔若干 bin 留出、邻域可见，检验内插能否恢复 yaw 精度（回答 Q2）。实现可仿照 `split_dataset.py:split_circ_yaw_block` 改 bin 选取，manifest 驱动。

---

## 6. 执行顺序建议

1. 先档 A（门槛最低，可能单独就回答 Q1 与地基问题）。
2. 档 A 出结果后再评估：是否需要档 B、是否改写主线 framing、是否调整投稿档位。
3. 全程不进入 E45 出图 / 正文 prose，直到归因结论稳定。

---

## 7. 给 Codex 的放行请示要点

- 请裁决：档 A（推理重聚合，无新训练）是否可放行执行、是否赋正式 E 编号。
- 请明确：档 A 的"内置一致性自检"作为先行门是否被接受为通过标准。
- 请裁决：档 B（random split + interleaved holdout 新训练）是否在档 A 之后有条件放行，还是暂缓。
- 请确认：本诊断产物（推理脚本、逐样本 npz、判据汇总表）的落盘路径与归属（建议 `02_Claude输出/` 候选，通过后再入 `01_成果区/`）。
- 红线维持：诊断结论仍限定 phase63 fixed-roll + cross-yaw holdout 体系，不外推真实 GEO / 三轴 / 暗室；不改训练代码逻辑；不启动论文正文改写。

---

## 8. 风险与注意

- last-epoch vs best-epoch：checkpoint 为 last-epoch 权重，复算指标须先对齐现有 json，避免把权重差异误读为判据效应。
- per-sample 落盘格式需统一（bin 索引 + 角度换算约定），供后处理与混淆矩阵复用。
- coarse-bin 重映射须用 circular 边界正确归并，避免跨 0°/360° 接缝错误。
- 互补性判定须 joint 与 image-only 在同一 split、同一折、同一判据下成对比较，不跨条件比较。
