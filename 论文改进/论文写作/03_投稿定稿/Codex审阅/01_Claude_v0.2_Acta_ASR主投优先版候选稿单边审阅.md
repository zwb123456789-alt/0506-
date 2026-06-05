# Codex 审阅：Claude v0.2 Acta/ASR 主投优先版候选稿

> 审阅日期：2026-06-05  
> 审阅对象：`03_投稿定稿/Claude交互/Claude输出/01_Claude输出_v0.2_Acta_ASR主投优先版.md`  
> 对照任务：`03_投稿定稿/01_v0.2_Acta_ASR主投优先版/00_本阶段任务说明.md`  
> 结论：通过，可作为 v0.2 Acta/ASR 主投优先版的主要结构和语言底稿；最终整合时需修正一处 U1 分支遮蔽标签方向，并继续保留作者确认占位。

## 1. 总体判定

Claude 候选稿完整覆盖本阶段要求：

1. 以 v0.1 为基础，没有覆盖 v0.1，也没有启动 CJA/AST 或 TAES/JGCD 文本。
2. 一次性整合 07、07b、07c，而不是只接 07c。
3. Results 已重排为 clean fusion / degradation-aware fusion / sensitivity / synthetic stress tests 的顺序。
4. Methods 补入 split、target encoding、metric、OCS train-only standardization、12c 线性强度域退化、12d phase24/phase120、12f beta=image weight 等关键协议。
5. Discussion 和 Limitations 明确降调：U1 是 coupled OCS-image co-utilization，不是 OCS standalone fallback。
6. Q12-Q14、引用元数据、Euler convention、target encoding、angular metric 等仍保留 `[需要作者确认]` 或 `[to verify]`，没有由 AI 代填。

因此，Claude 候选稿可以进入 GPT-vs-Claude 整合决策。

## 2. 关键数值核查

通过核查的主要锚点：

| 证据项 | Claude 候选稿状态 | 判定 |
|---|---|---|
| ResNet image-only clean = 1.69 +/- 0.07 deg, Hit@5 = 97.6% | 正确 | 通过 |
| ResNet + concat5 `per_part_log` clean = 1.47 +/- 0.07 deg, Hit@5 = 99.7%, worst 9.9 -> 6.6 deg | 正确 | 通过 |
| practical OCS-only `per_part_log` = 5.91 +/- 0.22 deg | 正确 | 通过 |
| `all_raw` = 3.98 +/- 0.60 deg, semi-oracle | 正确 | 通过 |
| naive fusion noise sigma=0.01 about 73-75 deg | 正确 | 通过 |
| Experiment 12 clean branch masking: normal 1.57, image-masked 52.84, OCS-masked 18.14 | 正确 | 通过 |
| Experiment 12 noisy branch masking: normal 75.08, image-masked 52.84, OCS-masked 88.88 | 正确 | 通过 |
| U1 clean 1.95, noise sigma=0.10 2.31 | 正确 | 通过 |
| image-only same augmentation at noise sigma=0.10 = 9.55 | 正确 | 通过 |
| 12c read/background/starfield/combined_medium U1 about 2 deg; combined_severe 13.88 | 正确 | 通过 |
| 12d phase24 11.34/6.85, phase120 83.08/79.71 | 正确 | 通过 |
| 12e original 1.69 -> centered 2.88 | 正确 | 通过 |
| 12f noise best beta=0, internal OCS-only 6.58 | 正确，并与 5.91 分离 | 通过 |
| 12g outliers >30 deg = 42/49,950 = 0.084% | 正确 | 通过 |

## 3. 必须修正的问题

### 3.1 U1 分支遮蔽方向在一处正文与表格中写反

12b 的正确含义为：

| 条件 | normal | image_train_mean | ocs_train_mean |
|---|---:|---:|---:|
| clean | 1.95 deg | 30.87 deg | 56.48 deg |
| noise 0.01 | 1.95 deg | 30.87 deg | 56.45 deg |
| noise 0.10 | 2.31 deg | 30.87 deg | 58.56 deg |

其中：

- `image_train_mean` = 遮蔽图像分支，正确结果为 30.87 deg。
- `ocs_train_mean` = 遮蔽 OCS 分支，正确结果为约 56-59 deg。

Claude 候选稿在 4.5 文字中有一处写成“masking the OCS branch ... 30.87, masking the image branch ... 56-59”，方向相反。最终 v0.2 必须改为：

```text
masking the image branch degrades U1 to 30.87 deg, while masking the OCS branch degrades it to about 56-59 deg.
```

对应 Table 4 也应补齐或修正 U1 的 image-branch masked 与 OCS-branch masked 行。

### 3.2 Abstract 可略压缩

Claude 摘要完整但偏长。最终整合可保留其完整逻辑，同时吸收 GPT 候选稿更短的 claim-evidence 表达。

### 3.3 OCS-noise table 建议下放 Supplementary

Claude 将 OCS-noise fusion-gain 放在 4.6 主文中是可行的，但 v0.2 主文已经新增 Table 4/5/6。为避免主线过重，建议最终主稿只在 4.6 简述 OCS-noise 敏感性，将完整表放 Supplementary S3。

## 4. 红线审阅

| 红线 | Claude 状态 | 判定 |
|---|---|---|
| 不写 fusion automatically robust | 未触犯；明确 naive fusion collapses | 通过 |
| 不写 U1 automatically switches to OCS | 未触犯；写成 co-utilization | 通过 |
| 不写 OCS standalone fallback | 未触犯；多处显式否定 | 通过 |
| 不写 near-perfect / fully robust | 未触犯；保留 rare outliers、combined_severe、phase120 | 通过 |
| 不写真实望远镜验证已完成 | 未触犯；明确无 real telescope validation | 通过 |
| 不写 operational robustness / field-proven robustness | 未触犯；最终整合时继续避免该措辞 | 通过 |
| 不写 phase120 generalization solved | 未触犯；phase120 是 failure case | 通过 |
| 不写 obs-aug 是成功通用策略 | 未触犯；U2/U3/U4 为负或部分结果 | 通过 |
| 不写 12f beta 是可部署自动门控 | 未触犯；写成 oracle upper bound | 通过 |
| 不混用 5.91 与 6.58 | 未触犯；6.58 标为 12f internal reference | 通过 |

## 5. 整合建议

最终 v0.2 建议：

1. 以 Claude 候选稿作为主结构和语言底稿。
2. 吸收 GPT 的较短标题表达、claim-evidence map 和 remaining checks。
3. 修正 U1 分支遮蔽标签方向。
4. 保留 Claude 的 Methods 3.9-3.11、Results 4.4-4.7、Discussion 5.4-5.6。
5. Q12-Q14、引用元数据、Euler convention、target encoding、angular error formula、0% OCS-noise table values、kNN Hit@10 等继续占位。

结论：Claude 候选稿通过单边审阅，可进入最终整合。
