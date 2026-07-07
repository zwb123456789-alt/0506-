# 子任务A：中间量可用性审计摘要

## 1. 结论

- P-INT 三通道 × G1/G3/G5：9/9 个 run 可用（应为 9）。
- P-EXT ocs_only × G1/G3/G5：3/3 个 run 可用（P-EXT 按预注册只产 ocs_only stress test，image/joint 缺失属设计，不是缺陷）。
- neural top-k：可用（posterior_like_top5_idx，宽度5）；candidate_grid(2664×2)可用于把 grid idx 还原为 yaw/pitch。
- P-DB per_query：24975 行，含 topk10_idx / nearest_distance / margin，可对齐 record_id。
- joined_per_attitude / complementarity / hardcase_index 均存在，字段满足 D4 与 D2 需求。

## 2. 三个门的可行性判定

- **D2 三通道互补性**：可完整完成。三通道 per-attitude 齐全，neural top-5 与 P-DB top-10 均可用，可做 top-k overlap/Jaccard，不必降级。
- **D4 可观测性地图**：可完整完成。yaw/pitch 真值 + 四通道误差 + hardcase labels 现成。
- **M5 三协议对比**：可完成。P-INT(三通道)、P-EXT(ocs_only)、P-DB(retrieval) 指标齐全；P-EXT 仅 ocs_only 属设计，对比时明确标注。

## 3. 缺口与降级说明

- P-EXT 无 image_only/joint：非缺陷，P-EXT 是 ocs_only yaw-block stress test。M5 中 P-EXT 列只填 ocs_only，其余标 N/A(by design)。
- neural top-k 只到 top-5，P-DB 到 top-10：D2 的 neural×pdb overlap 统一取 min(k)=top-5 口径，并在表中标注。
- top1_score/entropy/margin 已存，但均由 posterior_like 分布导出，属 model-known simulated，不得写成真实概率校准。

## 4. 输入文件清单

- 见 `audit/input_file_manifest.csv`，共 40 条，含 sha1_8 指纹用于复核。