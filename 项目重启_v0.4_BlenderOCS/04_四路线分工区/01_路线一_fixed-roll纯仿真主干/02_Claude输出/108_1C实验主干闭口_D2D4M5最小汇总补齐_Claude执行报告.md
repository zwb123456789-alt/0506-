# 108 路线一 C 实验主干闭口：D2/D4/M5 最小汇总补齐 Claude 执行报告

最后更新：2026-07-01
任务来源：`04_Codex审阅/R124_Codex_任务单_1C实验主干闭口_D2D4M5最小汇总补齐.md`
交付目录：`v0.4_results/16_route1c_closure_d2d4_m5/`

---

## 1. 任务结论摘要

**完成。** 在不新训练、不新渲染、不改旧脚本、不改旧结果的前提下，用现有 11/13 号中间量补齐了 R113 技术路线中尚未独立闭口的三个汇总门：

- **D2 三通道互补性**：闭口完成，含 top-k overlap（未降级）。
- **D4 可观测性地图**：闭口完成。
- **M5 三协议对比门**：闭口完成。

对照 R113 M1-M5/M-roll 生成闭口候选总表：**本轮未发现硬 BLOCKER**，实验主干具备闭口候选条件。唯一实质裁决点是 multi-seed 稳健性是否作为闭口前置。本报告为闭口候选包，**不自行宣布路线一 C 闭口，不启动三轴小项目**，等待 Codex R125 裁决。

一处诚实负向结论必须前置：**clean/P-INT 下 joint 相对最佳单通道无稳定正增量（max +0.0068），joint 与 image 在 G1/G3 命中完全一致**，是 image 通道饱和的天花板效应，joint 强互补性未闭口，需 P-INT-hard 才能判定。

---

## 2. 已读文件与遵守红线

已读：`CLAUDE.md`、`01_成果区/00_当前主用成果/01_路线一C后续技术路线执行框架_R113通过.md`、`R121`、`R123`、`08/09 成果区摘要`、`R124 任务单`。按需读取 11/12/13 号结果目录与字段。

遵守 R124 §1 禁止项：仅读现有 CSV/NPZ/JSON、仅写 16 号新目录、未改 10-15 号任何文件、未写成果区/未生成 Codex 审阅文件/未改 CLAUDE.md。

---

## 3. 新增脚本清单（全部新文件，未改旧脚本）

| 脚本 | 用途 |
|---|---|
| `scripts/a_intermediate_audit.py` | 子任务A 中间量可用性审计 |
| `scripts/b_d2_complementarity.py` | 子任务B D2 三通道互补性 |
| `scripts/c_d4_observability.py` | 子任务C D4 可观测性地图 |
| `scripts/d_m5_protocol.py` | 子任务D M5 三协议对比门 |
| `scripts/e_gate_matrix.py` | 子任务E 闭口候选总表 |
| `scripts/f_audit_redline.py` | 子任务F 审计与红线自检 |

均只读既有结果并写入 16 号包，不 import 旧训练/渲染代码。

---

## 4. 中间量可用性审计摘要（子任务A）

- P-INT 三通道 × G1/G3/G5：**9/9 run 可用**（best+final+npz+metrics）。
- P-EXT ocs_only × G1/G3/G5：**3/3 可用**；P-EXT 无 image/joint 属预注册设计（ocs_only yaw-block stress test），非缺陷。
- **neural top-k 可用**：npz 内含 `posterior_like_top5_idx`(296×5) 与 `candidate_grid`(2664×2, yaw72×pitch37)，D2 top-k overlap 无需降级。
- P-DB per_query 24975 行、summary 齐全，含 top1/topk cMAE 与 hit@30。
- 输出：`audit/intermediate_availability_audit.csv/.md`、`audit/input_file_manifest.csv`（40 条含 sha1 指纹）。

关键对齐说明：11 号 record_id 带几何前缀（`G1_yaw..._pitch...`）；同几何内三通道 record_id 完全一致（D2/M5 直接对齐），跨几何增益（D4）用去前缀的姿态键对齐，296 姿态全交。

---

## 5. D2 三通道互补性闭口摘要（子任务B）

口径：P-INT / best / clean；yaw hit@30；top-k overlap 取 top-5 grid idx Jaccard。

三通道 yaw hit@30：

| geom | image_only | ocs_only | joint |
|---|---|---|---|
| G1 | 1.000 | 0.277 | 1.000 |
| G3 | 1.000 | 0.672 | 1.000 |
| G5 | 0.993 | 0.811 | 1.000 |

- joint − best_single：G1=0, G3=0, G5=+0.0068 → **joint 无稳定正增量**。
- image_only|joint disagreement：G1/G3=0、G5=0.0068 → **clean 下 joint 实质退化为 image 分支**。
- oracle 并集（ocs∪joint、all3）均达 1.0，说明存在 case 级互补信息，但为 oracle 上界，非无监督可达。
- 诚实结论：**joint 强互补性未闭口，是 image 饱和的天花板效应而非确证短板，需 P-INT-hard / degraded-severe 裁决**。
- 输出：`tables/d2_*.csv`（5 表）、`figures/d2_*`（3 图）、`text/d2_complementarity_closure_summary.md`。

---

## 6. D4 可观测性地图闭口摘要（子任务C）

- 误差地图：ocs_only G1/G3/G5、image_only/joint/P-DB G5，yaw×pitch 散点。
- 几何增益：OCS-only G1→G5 平均 yaw 误差改善 **53.8°**（中位 47.3°），**228/296 姿态被多几何救回**（>5°），40 个变差。量化了 L1 单调增益的姿态空间来源。
- 易混淆/低信息区：ambiguous-flux（P-DB 最近邻相似但判错）236 例、neural 过自信错误 98 例（佐证 R119 margin 弱）、P-EXT yaw-block 坍缩区 296 例。
- 区域分类表 + hardcase 交叉统计（36 区 × label）完成。
- D4 地图可作三轴小项目「高信息姿态/低信息区」接口，但本轮不启动。
- 输出：`tables/d4_*.csv`（4 表）、`figures/d4_*`（4 图）、`text/d4_observability_map_closure_summary.md`。

---

## 7. M5 三协议对比门摘要（子任务D）

yaw hit@30（clean）：

| method | G1 | G3 | G5 |
|---|---|---|---|
| P-INT ocs_only | 0.277 | 0.672 | 0.811 |
| P-EXT ocs_only | 0.000 | 0.081 | 0.000 |
| P-DB top1 | 0.291 | 0.821 | 0.949 |

- **P-INT**：多几何 OCS 单调增益，成立（simulated）。
- **P-EXT**：strict yaw-block 仍坍缩，多几何不能救外推——未解决。
- **P-DB**：model-known simulated template retrieval，检索命中随几何提升（甚至强于 neural 回归，与 R119 一致）；top-k 是 oracle 上界，非真实成功率。
- 三协议边界清晰互不冲突，M5 门可闭。
- 输出：`tables/m5_*.csv`（3 表）、`figures/m5_protocol_comparison_panel.*`、`text/m5_protocol_gate_closure_summary.md`。

---

## 8. 路线一 C 实验主干闭口候选总表摘要（子任务E）

`tables/route1c_closure_gate_matrix.csv`（12 模块）：

- M1/M2/M3(mild-moderate)/M4(D1-D4)/M5/M-roll(探针) 均有通过审阅或本轮闭口证据。
- **硬 BLOCKER = 0**。
- 半 BLOCKER（裁决点）：multi-seed sanity——接受多证据链交叉 or 要求 minimal multi-seed（C 类）。
- ENHANCEMENT：P-INT-hard/degraded-severe、M-roll full-2664、conformal α 敏感性 SI。
- FUTURE_ROUTE：三轴小项目、L2/T3、路线二/三/四。
- 输出：`text/route1c_experimental_closure_candidate_summary.md`、`text/remaining_blockers_vs_enhancements.md`。

---

## 9. 数字一致性与 manifest 摘要（子任务F）

- `audit/numeric_consistency_check.csv`：**21 项 PASS / 0 CONFLICT**。16 号表中 hit@30/cMAE 直接回读 11 号 metrics_test_best.json 与 13 号 pdb summary。
- `audit/generated_files_manifest.csv`：**44 个本轮文件**，含 sha1_8 指纹；8 张 PNG 均非空（31KB–268KB）。

---

## 10. 未完成项、阻塞项、增强项

- 未完成硬项：无。三门全闭。
- 阻塞项：无硬 BLOCKER。
- 增强项（需另行 C 类阶段门）：P-INT-hard/degraded-severe（补 joint 互补性）、M-roll full-2664、multi-seed sanity、conformal α SI。

---

## 11. 红线自检

`audit/redline_self_check.csv`：**10/10 PASS**。未训练/渲染、未改旧文件、未写成果区、未写正文、未启动小项目/后续路线、未把 P-EXT 写成已解决、未把 P-DB 写成真实成功率、未把 conformal 写成最终校准、保留 joint 无增量诚实结论、仅写闭口候选等待 Codex。

---

## 12. 交给 Codex R125 的裁决问题清单

1. D2/D4/M5 三门是否接收为闭口。
2. 路线一 C 实验主干是否可正式闭口（本轮无硬 BLOCKER）。
3. multi-seed sanity 是否作为闭口前置（唯一实质裁决点）。
4. joint 强互补性未闭口为天花板效应，是否放行 P-INT-hard / degraded-severe 增强阶段门。
5. 是否可进入三轴小项目准备阶段（D4 地图已可作接口）。
6. 论文写作与实验闭口次序确认：R113 §8 为「实验闭口→启动三轴小项目」，论文正文非小项目前置。

（详见 `text/codex_review_checklist_for_108.md`）
