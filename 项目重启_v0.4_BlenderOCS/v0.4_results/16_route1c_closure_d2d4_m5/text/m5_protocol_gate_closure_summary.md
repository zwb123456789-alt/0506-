# 子任务D：M5 三协议对比门闭口摘要

口径：clean；neural best；P-DB neg-L2 matched-degraded test；yaw hit@30 / cMAE；model-known simulated。

## 1. 三协议 × 几何 (yaw hit@30)

| method | G1 | G3 | G5 |
|---|---|---|---|
| P-INT ocs_only | 0.277 | 0.6723 | 0.8108 |
| P-EXT ocs_only | 0.0 | 0.0811 | 0.0 |
| P-DB top1 | 0.2905 | 0.8209 | 0.9493 |
| P-INT image_only(对照) | 1.0 | 1.0 | 0.9932 |

## 2. 协议边界

- **P-INT**：多几何 OCS-only 单调增益，成立（simulated）。
- **P-EXT**：strict yaw-block 仍坍缩，多几何不能救外推——不得写成已解决。
- **P-DB**：model-known simulated template retrieval，检索命中随几何提升，证明多观测光度向量含可检索 yaw 信息；top-k 是 oracle 上界，非无监督成功率。
- **image_only 对照**：clean 下近饱和，仅作通道对照，不能掩盖 OCS 主线，也不能据此宣称 joint 强互补。

## 3. 闭口结论

- M5 三协议对比门可闭口为：P-INT 正结果 / P-EXT 坍缩 / P-DB 可检索信息，三者边界清晰互不冲突。
- 三协议共同支撑「多观测 OCS 含姿态信息」，但都限定 model-known simulated / current split / seed=42。
