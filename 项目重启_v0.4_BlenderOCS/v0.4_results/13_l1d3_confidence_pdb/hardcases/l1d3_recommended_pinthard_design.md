# P-INT-hard / stronger degraded 下一步设计建议（R118 子任务 E）

最后更新：2026-07-01  

**本文件只写下一步设计建议，不放行训练。作者/Codex 决定是否启动。**

## 1. 现状观察（绑定本轮输出）

```text
- ocs_only G5 hard-case（跨退化）：73 例，集中在 P-DB margin 低 / nearest 距离高的姿态。
- disagreement-hard（neural 与 P-DB 一对一错）：748 例，是互补空间的核心候选。
- image_only/joint 在本轮 mild/moderate 下 hit@30 仍高，image-hard 较少 → 图像天花板未被本级退化触及。
- P-DB ocs_only 在 clean/mild 上 top1 hit@30 高于 neural ocs_only 回归（见子任务 B/C），
  说明多观测总光度向量含 yaw 信息未被神经回归充分利用。
```

## 2. 候选 split / 子集定义

```text
- subset-A（disagreement 核心）：disagreement-hard ∪ ocs-hard 的 G5 姿态，作为 P-INT-hard 难例池。
- subset-B（ambiguous-flux）：候选 yaw 分散姿态，用于检验 top-k / posterior 是否能表达多峰。
- 对照 robust-easy：低难度姿态，验证难例定义不是纯噪声。
```

## 3. 是否需要更强 degraded / 补 joint-full M-roll

```text
- 建议增设 degraded-severe（更强 PSF/更低 photon/更大 flux 噪声）以触及图像天花板，
  才能检验 joint 是否显现强互补；本轮 mild/moderate 未触及。
- joint/full-2664 M-roll 成本高（R117 估 10–11h），建议仅在 disagreement subset 上按需补，
  不铺全量。
```

## 4. 预计训练矩阵与成本（粗估，仅供裁决参考）

```text
- P-INT-hard 难例微调/评估：G5 × {ocs_only,joint} × {moderate,severe} ≈ 4 run，沿用现 backbone。
- degraded-severe 需新渲染或在现有 EXR 上加噪：若纯后处理加噪则无需重渲，成本可控。
- 不做开放超参搜索、不换 backbone。
```

## 5. 建议的下一阶段门指标

```text
- 主指标：joint 在 degraded-severe / P-INT-hard 上相对 image_only 的 yaw hit@30 增量是否显著为正。
- 辅指标：P-DB top1 与 neural 的 oracle_hit@30 差距是否收窄（互补是否被模型吸收）。
- conformal set_size 是否随几何数继续单调收紧。
```
