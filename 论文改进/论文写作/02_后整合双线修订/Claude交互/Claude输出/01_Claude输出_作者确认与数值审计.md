# Claude 输出：作者确认与数值审计报告

> 生成日期：2026-06-01  
> 基于：最终整合版 v0.1  
> 审计范围：全文逐章结构化审计  
> 输出目的：供 Codex 审阅整合为 v0.2 修订依据  
> 证据来源：CLAUDE.md（项目进度档案）、20260529_补充实验进度.md、20260529_论文写作完整规划.md

---

## 1. Title / Abstract / Keywords

| ID | 位置 | 原文/数值 | 类型 | 风险 | 当前状态 | 需要作者提供 | 建议处理 |
|---|---|---|---|---|---|---|---|
| T001 | Title | "BRDF-Driven Optical Cross Section and Photometric Image Simulation for Space Object Attitude Inversion: A Controlled Benchmark Study" | 作者确认 | Low | 待确认 | 是否保留"Controlled Benchmark Study"副标题；规划文件建议备选标题去掉副标题 | 保留当前或采用规划文件 §3.1 推荐标题 |
| A001 | Abstract | "ResNet-18 image-only model reaches 1.69 +/- 0.07 deg mean angular error with Hit@5 = 97.6%" | 数值核验 | Medium | 需核验 | 核对 `补充实验/结果/resnet_baseline/run_20260601_082852/` 中 5 seeds 均值与标准差 | 补证后保留 |
| A002 | Abstract | "1% Gaussian image noise degrades performance to 85.85 +/- 3.00 deg with Hit@5 = 2.2%" | 数值核验 | Medium | 需核验 | 核对 `resnet_robustness/run_20260601_143957/` 中 sigma=0.01 结果 | 补证后保留 |
| A003 | Abstract | "worst-case reduction from 9.9 deg to 6.6 deg" | 数值核验 | Medium | 需核验 | 核对 `resnet_fusion/run_20260601_113332/` A1 vs A2 worst-case | 补证后保留 |
| A004 | Abstract | "defining an idealized upper-bound condition for image-based inversion rather than field performance" | 可保留 | Low | 已确认 | — | 保留，措辞符合写作红线 |
| A005 | Abstract | "OCS-image fusion reduces selected clean-image tail errors" | 表述过强 | Low | 可保留 | — | 可保留，但建议加"in this benchmark" |
| K001 | Keywords | "Space object attitude inversion; optical cross section; BRDF; photometric image simulation; multi-modal fusion; controlled benchmark" | 作者确认 | Low | 待确认 | 目标期刊是否对关键词数有限制（通常 4-6 个） | 保留或精简至 5 个 |

---

## 2. Introduction

| ID | 位置 | 原文/数值 | 类型 | 风险 | 当前状态 | 需要作者提供 | 建议处理 |
|---|---|---|---|---|---|---|---|
| I001 | §1 ¶1 | `[CITATION: optical space object characterization]` | 引用核验 | High | 待确认 | 提供具体文献（如 Linares 2014、Hall 2012 或其他综述） | 必须填入真实引用 |
| I002 | §1 ¶2 | `[CITATION: optical light-curve attitude inversion]` | 引用核验 | High | 待确认 | 提供光变曲线姿态反演代表文献 | 必须填入真实引用 |
| I003 | §1 ¶2 | `[CITATION: image-based spacecraft pose estimation]` | 引用核验 | High | 待确认 | 提供图像姿态估计代表文献（如 Sharma 2020、Kisantal 2020 等） | 必须填入真实引用 |
| I004 | §1 ¶3 | `[CITATION: BRDF-based space object photometry]` | 引用核验 | High | 待确认 | 提供 BRDF 卫星光度学文献（如 Cognion 2013 或 Yang 2024） | 必须填入真实引用 |
| I005 | §1 ¶3 | `[CITATION: ground-based optical observation degradation]` | 引用核验 | High | 待确认 | 提供地基光学观测退化相关文献 | 必须填入真实引用 |
| I006 | §1 ¶4 | "This paper makes four contributions" | 可保留 | Low | 已确认 | — | 四条贡献与规划文件 §4 一致，保留 |
| I007 | §1 ¶4 | "The present study does not use real optical telescope images..." | 可保留 | Low | 已确认 | — | 边界声明完整，保留 |
| I008 | §1 全段 | Introduction 整体长度约 4 段 | 作者确认 | Low | 待确认 | 目标期刊对 Introduction 长度是否有偏好（当前约 700 词，适中） | 保留当前长度 |

---

## 3. Related Work and Table 1

| ID | 位置 | 原文/数值 | 类型 | 风险 | 当前状态 | 需要作者提供 | 建议处理 |
|---|---|---|---|---|---|---|---|
| R001 | §2.1 | "Yang et al., 2024/2025, to verify" | 引用核验 | High | 待确认 | 确认具体文献：Yang 2024 Photonics 还是 Yang 2025？提供完整书目信息（卷/页/DOI） | 核实后替换占位 |
| R002 | §2.1 | "Lu/Yao, 2024, to verify" | 引用核验 | High | 待确认 | 确认 Lu 或 Yao 2024 Universe 的完整书目信息 | 核实后替换占位 |
| R003 | §2.1 | "Fankhauser et al., 2023, to verify" | 引用核验 | High | 待确认 | 确认 Fankhauser 2023 AJ 的完整书目信息 | 核实后替换占位 |
| R004 | §2.2 | "Wang et al., 2024, to verify" | 引用核验 | High | 待确认 | 确认 Wang 2024 ASR 的完整书目信息 | 核实后替换占位 |
| R005 | §2.2 | "Burton et al., 2024, to verify" | 引用核验 | High | 待确认 | 确认 Burton 2024 ASR 的完整书目信息 | 核实后替换占位 |
| R006 | §2.2 | "Kumar et al., 2025, to verify" | 引用核验 | High | 待确认 | 确认 Kumar 2025 Acta Astronautica 的完整书目信息 | 核实后替换占位 |
| R007 | §2.3 | "Dickinson 2025 RIT PhD, to verify" | 引用核验 | Medium | 待确认 | 确认 Dickinson 2025 是否为 PhD 论文；是否有对应期刊/会议版本更适合引用 | 核实后决定保留或替换 |
| R008 | §2.4 | "Liu et al., 2024 Remote Sensing, to verify" | 引用核验 | High | 待确认 | 确认 Liu 2024 Remote Sensing 的完整书目信息 | 核实后替换占位 |
| R009 | Table 1 全表 | 所有 `[to verify]` 标记的单元格（约 30+ 处） | 引用核验 | High | 待确认 | 逐条核实每篇文献的：目标/数据、BRDF 模型、自遮挡、图像分支、标量分支、姿态反演、融合、验证类型 | 必须全部核实或标注"无法确认"后删除该列内容 |
| R010 | Table 1 | 表格是否应放正文还是补充材料 | 作者确认 | Medium | 待确认 | 目标期刊对正文表格数量/大小的限制；Table 1 有 9 列 9 行，较宽 | 若期刊限制严格，建议移至补充材料 |
| R011 | §2 整体 | Related Work 四小节结构 | 可保留 | Low | 已确认 | — | 结构与规划文件 §6.3 一致，保留 |
| R012 | §2.1 | "Semi-empirical pBRDF / Cook-Torrance-related models" 对 Yang 的描述 | 引用核验 | Medium | 待确认 | 确认 Yang 文献是否确实使用 pBRDF/Cook-Torrance 相关模型 | 核实后保留或修正描述 |

---

## 4. Method

| ID | 位置 | 原文/数值 | 类型 | 风险 | 当前状态 | 需要作者提供 | 建议处理 |
|---|---|---|---|---|---|---|---|
| M001 | §3.2 | `[需要作者确认：Euler order / rotation matrix convention]` | 方法细节未确认 | High | 待确认 | 明确报告：Z-Y-X 内旋（与 geometry.py:16-38 一致）；R = Rz(yaw) @ Ry(pitch) @ Rx(roll=0)；yaw 绕哪个轴、pitch 绕哪个轴 | 作者确认后写入正文 |
| M002 | §3.2 | "73 yaw samples and 37 pitch samples, giving 2701 yaw-pitch attitudes" | 数值核验 | Low | 可确认 | 73×37=2701 ✓（CLAUDE.md Step 10c 一致） | 保留 |
| M003 | §3.2 | "A coarser 10 deg grid is used for training" | 数值核验 | Low | 可确认 | 10° 网格：37×19=703 训练点中取 563 train + 140 val（CLAUDE.md Step 11c 一致） | 保留，但建议正文明确 train/val 数量 |
| M004 | §3.3 | "five sun-sensor geometries...phase-angle range is approximately 24 deg to 120 deg" | 数值核验 | Low | 可确认 | config.py OBS_GEOMETRIES 5 组，相位角 24°-120°（CLAUDE.md Step 10d 一致） | 保留 |
| M005 | §3.3 | `[需要作者确认：phase63 fairness and cross-phase values]` | 方法细节未确认 | Medium | 待确认 | Phase63 公平消融已完成（补充实验 #1）：单几何 OCS per_part=21.68°，fusion=6.79°。是否将此结果纳入正文 §4.6 或补充材料？ | 作者决定后填入或标注为补充材料 |
| M006 | §3.4 | "metallic=1, roughness=0.20, F0=0.91; metallic=0, roughness=0.40, ior=1.5; metallic=0, roughness=0.90, base_color=0.08" | 数值核验 | Low | 可确认 | 与 CLAUDE.md Step 2 和 brdf_precision_design.md 一致 | 保留 |
| M007 | §3.5 | "epsilon = 1.0 mm and min_hit_distance = 1.0 mm" | 数值核验 | Low | 可确认 | 与 CLAUDE.md §三 遮挡机制描述一致 | 保留 |
| M008 | §3.6 | OCS 公式 "OCS = sum_i A_i f_r(...) max(n_i.l,0) max(n_i.v,0) V_i(l) V_i(v)" | 数值核验 | Low | 可确认 | 与 ocs_core.py 实现一致（CLAUDE.md Step 1 审计报告） | 保留 |
| M009 | §3.6 | "`all_raw` may include additional quantities and are therefore treated as semi-oracle" | 可保留 | Low | 已确认 | — | 保留，符合写作红线（不把 all_raw 写成 operational） |
| M010 | §3.8 | `[需要作者确认：exact target encoding]` | 方法细节未确认 | High | 待确认 | 确认：输出为 [sin(yaw), cos(yaw), sin(pitch), cos(pitch)]，预测时归一化解码（CLAUDE.md Step 11c） | 作者确认后写入正文 |
| M011 | §3.8 | "A TinyCNN is used as a lightweight image baseline, while ResNet-18 is used as a stronger image model" | 方法细节未确认 | Medium | 待确认 | TinyCNN 结构：Conv/GN/SiLU/Pool×4 → AdaptiveAvgPool → MLP 128→64→4（106k params）；ResNet-18 修改：1ch input, 11.2M params。是否在正文或补充材料报告具体结构？ | 建议正文简述参数量，补充材料给完整结构 |
| M012 | §3.8 | "Feature fusion uses a two-branch architecture" | 方法细节未确认 | Medium | 待确认 | ImageBranch(TinyCNN/ResNet→64D) + OCSBranch(MLP→64D) → FusionHead(concat 128D→4)。正文是否需要报告具体维度？ | 建议正文简述，补充材料给完整超参 |
| M013 | §3.9 | `[需要作者确认：angular error formula]` | 方法细节未确认 | High | 待确认 | 确认角误差公式：是否为 arccos(cos(Δyaw)·cos(Δpitch))？还是球面距离？yaw 周期性如何处理？ | 作者确认后写入正文 |
| M014 | §3.9 | "10 deg -> 5 deg attitude split" | 数值核验 | Low | 可确认 | train=563（10°网格），test=1998（5°网格去除10°点）（CLAUDE.md Step 11c） | 保留，建议正文明确 563/1998 数量 |
| M015 | §3.8 | Late fusion "beta sweep" 未说明具体范围 | 方法细节未确认 | Low | 待确认 | beta sweep 0:0.01:1（CLAUDE.md Step 11e-B1）。正文是否需要报告？ | 建议正文简述 beta∈[0,1] 步长 0.01 |

---

## 5. Results and Tables 2-4

### 5.1 §4.1 Forward-model validation

| ID | 位置 | 原文/数值 | 类型 | 风险 | 当前状态 | 需要作者提供 | 建议处理 |
|---|---|---|---|---|---|---|---|
| N001 | §4.1 | "sub-percent agreement between analytical or facet-level OCS calculations and rendering-derived checks" | 数值核验 | Low | 可确认 | 单平板三端闭合 mean rel_err=0.25%，立方体 B/an≤0.25%（CLAUDE.md Step 5-6） | 保留，建议正文给出具体数字"<0.5%" |
| N002 | §4.1 | "occlusion rates fall roughly in the 60% to 78.5% range" | 数值核验 | Low | 可确认 | 补充实验 #4：phase24=60.1%, phase120=78.5%（补充实验进度文件） | 保留 |

### 5.2 §4.2 OCS-only inversion

| ID | 位置 | 原文/数值 | 类型 | 风险 | 当前状态 | 需要作者提供 | 建议处理 |
|---|---|---|---|---|---|---|---|
| N003 | §4.2 | "per_part_log: 5.91 +/- 0.22 deg, Hit@5=73.8%, Hit@10=94.3%" | 数值核验 | Medium | 需核验 | 核对 `mlp_ocs/run_20260521_084723/` per_part_log 5 seeds 结果 | 补证后保留 |
| N004 | §4.2 | "total_log: 36.69 +/- 3.6 deg, Hit@5=9.7%, Hit@10=23.5%" | 数值核验 | Medium | 需核验 | 同上目录 total_log 结果 | 补证后保留 |
| N005 | §4.2 | "all_raw 45D: 3.98 +/- 0.60 deg, Hit@5=90.7%, Hit@10=97.1%" | 数值核验 | Medium | 需核验 | 同上目录 all_raw 结果 | 补证后保留 |

### 5.3 §4.3 Image-only inversion

| ID | 位置 | 原文/数值 | 类型 | 风险 | 当前状态 | 需要作者提供 | 建议处理 |
|---|---|---|---|---|---|---|---|
| N006 | §4.3 | "TinyCNN: 12.38 +/- 0.74 deg, Hit@5=26.1%" | 数值核验 | Medium | 需核验 | 核对 `cnn_image/run_20260521_164437_final_log1p/` 或新批次 `run_20260528_105418` | 补证后保留 |
| N007 | §4.3 | "ResNet-18: 1.69 +/- 0.07 deg, Hit@5=97.6%, Hit@10=99.9%" | 数值核验 | High | 需核验 | 核对 `resnet_baseline/run_20260601_082852/` 5 seeds 均值 | 补证后保留（核心数据） |
| N008 | §4.3 | "centroid displacement has a correlation with yaw (r=0.66)" | 数值核验 | Medium | 需核验 | 核对 `resnet_dataset_audit/run_20260601_105620/` 中 centroid_x vs yaw 相关系数 | 补证后保留 |
| N009 | §4.3 | "Mean intensity is nearly uncorrelated with attitude (r<0.02)" | 数值核验 | Low | 需核验 | 同上审计结果 | 补证后保留 |

### 5.4 §4.4 OCS-image fusion under clean images

| ID | 位置 | 原文/数值 | 类型 | 风险 | 当前状态 | 需要作者提供 | 建议处理 |
|---|---|---|---|---|---|---|---|
| N010 | §4.4 | "ResNet + concat5 per_part_log: 1.47 +/- 0.07 deg, P90=2.71, worst=6.6, Hit@5=99.7%" | 数值核验 | High | 需核验 | 核对 `resnet_fusion/run_20260601_113332/` A2 case | 补证后保留（核心数据） |
| N011 | §4.4 | "ResNet + phase63 per_part_log 6D: 1.61 +/- 0.07, P90=2.97, worst=7.4, Hit@5=99.2%" | 数值核验 | Medium | 需核验 | 同上 A3 case | 补证后保留 |
| N012 | §4.4 | "ResNet + concat5 all_raw 45D: 1.49 +/- 0.10, worst=18.7" | 数值核验 | Medium | 需核验 | 同上 A4 case | 补证后保留 |
| N013 | §4.4 | "TinyCNN/OCS feature fusion per_part_log: 4.10 +/- 0.77 deg" | 数值核验 | Low | 可确认 | CLAUDE.md Step 11e-B2 一致 | 保留 |
| N014 | §4.4 | "error correlation between OCS and CNN was r=0.003" | 表述过强 | Medium | 已确认 | — | 保留当前措辞（已标注为 TinyCNN/OCS 诊断，非 ResNet pair）；但建议正文加粗提醒"this diagnostic was computed for TinyCNN, not ResNet" |
| N015 | §4.4 | "OCS-only: 5.42 deg...OCS-only: 3.98 deg...CNN-only: 12.38 deg...fusion: 4.10 deg" 等 TinyCNN 时代数据 | 数值核验 | Low | 可确认 | 与 CLAUDE.md Step 11e-B2 一致 | 保留，但注意这些是 TinyCNN 实验，非 ResNet |

### 5.5 §4.5 Robustness under controlled degradation

| ID | 位置 | 原文/数值 | 类型 | 风险 | 当前状态 | 需要作者提供 | 建议处理 |
|---|---|---|---|---|---|---|---|
| N016 | §4.5 | "sigma=0.01: 85.85 +/- 3.00 deg, Hit@5=2.2%" | 数值核验 | High | 需核验 | 核对 `resnet_robustness/run_20260601_143957/` | 补证后保留（核心数据） |
| N017 | §4.5 | "sigma=0.03: 85.49 deg, Hit@5=1.5%" | 数值核验 | Medium | 需核验 | 同上 | 补证后保留 |
| N018 | §4.5 | "sigma=0.05: 85.97 deg, Hit@5=1.2%" | 数值核验 | Medium | 需核验 | 同上 | 补证后保留 |
| N019 | §4.5 | "sigma=0.10: 87.92 deg, Hit@5=1.0%" | 数值核验 | Medium | 需核验 | 同上 | 补证后保留 |
| N020 | §4.5 | "Brightness x0.50: 3.45 deg, Hit@5=78.7%" | 数值核验 | Medium | 需核验 | 同上 | 补证后保留 |
| N021 | §4.5 | "Brightness x0.75: 2.03; x1.25: 1.77; x1.50: 2.00" | 数值核验 | Low | 需核验 | 同上 | 补证后保留 |
| N022 | §4.5 Table 4 | `[需要作者确认]` OCS noise 0% 行的 OCS-only 和 fusion 数值 | 数值核验 | High | 待确认 | 补充实验 #6 已有结果：0% OCS-only=5.91±0.22°, fusion=3.93±0.46°, Hit@5 OCS=73.8%, Hit@5 fusion=86.3% | 填入这些数值 |
| N023 | §4.5 Table 4 | OCS noise 10% Hit@5 缺失 | 数值核验 | Medium | 待确认 | 补充实验 #6：OCS-only Hit@5=57.8%, fusion Hit@5=74.9% | 填入 |
| N024 | §4.5 Table 4 | OCS noise 20% Hit@5 缺失 | 数值核验 | Medium | 待确认 | 补充实验 #6：OCS-only Hit@5=35.8%, fusion Hit@5=59.6% | 填入 |
| N025 | §4.5 | "fusion gain increases from +1.97 deg at 0% to +3.30 deg at 10% and +6.29 deg at 20%" | 数值核验 | Medium | 可确认 | 补充实验 #6 Δmean 列一致：+1.97/+2.62(5%)/+3.30/+6.29 | 保留；注意正文跳过了 5% 级别，建议补入或说明 |

### 5.6 §4.6 Ablation and sensitivity

| ID | 位置 | 原文/数值 | 类型 | 风险 | 当前状态 | 需要作者提供 | 建议处理 |
|---|---|---|---|---|---|---|---|
| N026 | §4.6 | `[需要作者确认：which ablations have final numbers for main text]` | 作者确认 | High | 待确认 | 所有补充实验已完成。作者需决定哪些进正文、哪些进补充材料：phase63 公平(#1)、random split(#2)、BRDF 敏感性(#3)、遮挡 w/wo(#4)、roll 敏感性(#7) | 作者逐项决定 |
| N027 | §4.6 | "occlusion rates of roughly 60% to 78.5%" | 数值核验 | Low | 可确认 | 与 N002 一致 | 保留 |

### 5.7 Table 2 审计

| ID | 位置 | 原文/数值 | 类型 | 风险 | 当前状态 | 需要作者提供 | 建议处理 |
|---|---|---|---|---|---|---|---|
| N028 | Table 2 | "Weighted kNN all_raw Hit@10: `[需要作者确认]`" | 数值核验 | Medium | 待确认 | CLAUDE.md Step 11a-b：kNN all_raw LOO Hit@10=91.6%（但注意这是 LOO split，非 10°→5° split）。10°→5° split 下 kNN 结果见 Step 11c：kNN-w all_raw mean=21.84°, Hit@5=47.9% | 需确认 Table 2 中 kNN 用的是哪个 split；若为 10°→5° 则 Hit@10 需从实验日志提取 |
| N029 | Table 2 | 整表 6 行数值一致性 | 数值核验 | Medium | 需核验 | 逐行与实验日志交叉核对 | 补证后保留 |

### 5.8 Table 3 审计

| ID | 位置 | 原文/数值 | 类型 | 风险 | 当前状态 | 需要作者提供 | 建议处理 |
|---|---|---|---|---|---|---|---|
| N030 | Table 3 | A1-A4 全部数值 | 数值核验 | High | 需核验 | 核对 `resnet_fusion/run_20260601_113332/` 完整输出 | 补证后保留 |
| N031 | Table 3 | "A2 Hit@10=100%" | 数值核验 | Medium | 需核验 | 确认是否真为 100.0% 还是 99.95% 四舍五入 | 核实精确值 |

### 5.9 Table 4 审计

| ID | 位置 | 原文/数值 | 类型 | 风险 | 当前状态 | 需要作者提供 | 建议处理 |
|---|---|---|---|---|---|---|---|
| N032 | Table 4 | 图像退化行（sigma=0.01~0.10, brightness）全部数值 | 数值核验 | High | 需核验 | 核对 `resnet_robustness/run_20260601_143957/` | 补证后保留 |
| N033 | Table 4 | OCS noise 行格式"OCS-only -> fusion"不标准 | 作者确认 | Low | 待确认 | 建议拆为两列或两行，便于期刊排版 | 改写表格格式 |
| N034 | Table 4 | 缺少 OCS noise 1% 和 5% 行 | 作者确认 | Low | 待确认 | 补充实验 #6 有 1%/5% 数据。是否纳入？ | 建议至少加 5%（中间点），或全部纳入 |

---

## 6. Discussion

| ID | 位置 | 原文/数值 | 类型 | 风险 | 当前状态 | 需要作者提供 | 建议处理 |
|---|---|---|---|---|---|---|---|
| D001 | §5.1 | "scalar OCS signatures and resolved photometric images provide different attitude constraints" | 可保留 | Low | 已确认 | — | 保留，核心发现表述准确 |
| D002 | §5.2 | "under 1% Gaussian image noise, ResNet performance collapses from the clean-image upper-bound regime to a mean error above 85 deg" | 数值核验 | Low | 可确认 | 与 N016 一致（85.85°） | 保留 |
| D003 | §5.3 | "OCS is not the accuracy upper bound when clean resolved images are available" | 可保留 | Low | 已确认 | — | 保留，符合写作红线 |
| D004 | §5.3 | "Real OCS or light-curve measurements may be affected by photometric calibration error, atmospheric transparency variation..." | 可保留 | Low | 已确认 | — | 保留，正确限定 OCS 鲁棒性边界 |
| D005 | §5.4 | "worst-case error from 9.9 deg to 6.6 deg" | 数值核验 | Low | 可确认 | 与 N010/Table 3 一致 | 保留 |
| D006 | §5.4 | "ResNet + concat5 all_raw case achieves a similar mean error but a worse worst-case error of 18.7 deg" | 数值核验 | Low | 可确认 | 与 Table 3 A4 一致 | 保留 |
| D007 | §5.4 | "fusion gain increases from +1.97 deg at 0% OCS noise to +3.30 deg at 10% and +6.29 deg at 20%" | 数值核验 | Low | 可确认 | 与 N025 一致 | 保留 |
| D008 | §5.5 | "Hit@5, Hit@10, P90, and worst-case behavior may be as important as average error" | 可保留 | Low | 已确认 | — | 保留，合理的实践建议 |
| D009 | §5.6 | "does not use real optical telescope images with known attitude ground truth" | 可保留 | Low | 已确认 | — | 保留，边界声明 |
| D010 | §5.6 | "Gaussian image noise and brightness scaling do not fully represent atmospheric turbulence..." | 可保留 | Low | 已确认 | — | 保留，正确限定退化实验边界 |
| D011 | §5.4 | "the image branch remains clean in this OCS-noise setting" | 表述过强 | Low | 可保留 | — | 保留，已正确标注实验边界（图像保持 clean 时测 OCS 噪声） |
| D012 | §5 整体 | Discussion 未引用 BRDF 敏感性、roll 敏感性、phase63 公平消融等补充实验结果 | 作者确认 | Medium | 待确认 | 作者决定是否在 Discussion 中引用补充实验结论（如"金属 roughness 是最敏感参数"、"roll 变化导致 OCS 约 20% 变化"） | 建议在 §5.6 Limitations 中简要引用 |

---

## 7. Conclusion

| ID | 位置 | 原文/数值 | 类型 | 风险 | 当前状态 | 需要作者提供 | 建议处理 |
|---|---|---|---|---|---|---|---|
| C001 | §6 | "ResNet-18 reaching 1.69 +/- 0.07 deg under idealized imagery" | 数值核验 | Low | 可确认 | 与 N007 一致 | 保留 |
| C002 | §6 | "degrading to 85.85 +/- 3.00 deg under 1% Gaussian noise" | 数值核验 | Low | 可确认 | 与 N016 一致 | 保留 |
| C003 | §6 | "OCS-image fusion improves selected clean-image tail errors from 9.9 deg to 6.6 deg" | 数值核验 | Low | 可确认 | 与 N010 一致 | 保留 |
| C004 | §6 | "Future work should extend...calibrated materials, broader phase and roll conditions, explicit atmosphere and sensor modeling, and real optical observations" | 可保留 | Low | 已确认 | — | 保留，合理的未来工作方向 |
| C005 | §6 | Conclusion 未提及 OCS-only per_part_log 的具体数值 | 作者确认 | Low | 待确认 | 是否在 Conclusion 中加入 OCS-only 5.91° 作为对比锚点？ | 建议加入一句简要对比 |

---

## 8. Data Availability / Author Contributions / Conflict of Interest

| ID | 位置 | 原文/数值 | 类型 | 风险 | 当前状态 | 需要作者提供 | 建议处理 |
|---|---|---|---|---|---|---|---|
| S001 | Data Availability | `[需要作者确认：whether simulation data, STL-derived products, trained models, and scripts can be shared]` | 作者确认 | Medium | 待确认 | 决定数据共享策略：(a) 公开 GitHub 仓库 (b) 应要求提供 (c) 不公开 | 投稿前必须填写 |
| S002 | Author Contributions | `[需要作者确认：author list and CRediT roles]` | 作者确认 | High | 待确认 | 提供作者列表和 CRediT 分工 | 投稿前必须填写 |
| S003 | Conflict of Interest | `[需要作者确认：final conflict-of-interest wording]` | 作者确认 | Low | 待确认 | 确认无利益冲突声明措辞是否符合目标期刊要求 | 投稿前填写 |

---

## 9. References placeholders

| ID | 位置 | 原文/数值 | 类型 | 风险 | 当前状态 | 需要作者提供 | 建议处理 |
|---|---|---|---|---|---|---|---|
| REF01 | References | `[CITATION: optical space object characterization]` | 引用核验 | High | 待确认 | 提供 1-2 篇代表性综述或开创性文献 | 必须替换 |
| REF02 | References | `[CITATION: optical light-curve attitude inversion]` | 引用核验 | High | 待确认 | 提供光变曲线姿态反演文献 | 必须替换 |
| REF03 | References | `[CITATION: image-based spacecraft pose estimation]` | 引用核验 | High | 待确认 | 提供图像姿态估计文献 | 必须替换 |
| REF04 | References | `[CITATION: BRDF-based space object photometry]` | 引用核验 | High | 待确认 | 提供 BRDF 卫星光度学文献 | 必须替换 |
| REF05 | References | `[CITATION: ground-based optical observation degradation]` | 引用核验 | High | 待确认 | 提供地基光学退化文献 | 必须替换 |
| REF06 | References | `[CITATION: multi-modal fusion robustness]`（正文未出现但 References 列出） | 引用核验 | Medium | 待确认 | 确认是否需要此引用；若正文未引用则删除 | 核实后决定 |
| REF07 | References | 8 篇 `[to verify]` 文献的完整书目信息 | 引用核验 | High | 待确认 | 逐篇提供：作者全名、年份、标题、期刊/会议、卷/期/页/DOI | 必须全部核实 |

---

## 10. Figures and caption intents

| ID | 位置 | 原文/数值 | 类型 | 风险 | 当前状态 | 需要作者提供 | 建议处理 |
|---|---|---|---|---|---|---|---|
| F001 | Fig. 1 | "Unified OCS-image simulation and inversion pipeline" | 作者确认 | Medium | 待确认 | 图尚未制作；需确认最终框架图内容和风格 | 后续阶段（03_图表制作）处理 |
| F002 | Fig. 2 | "Satellite geometry and observation setup" | 作者确认 | Medium | 待确认 | 图尚未制作 | 后续阶段处理 |
| F003 | Fig. 3 | "OCS maps and occlusion diagnostics" | 作者确认 | Medium | 待确认 | 图尚未制作；数据源已有（模块 A 扫描结果） | 后续阶段处理 |
| F004 | Fig. 5 | "Image degradation robustness" | 作者确认 | Medium | 待确认 | 图尚未制作；数据源已有（resnet_robustness） | 后续阶段处理 |
| F005 | Fig. 6 | "OCS noise and fusion gain" | 作者确认 | Medium | 待确认 | 图尚未制作；数据源已有（noise_robustness） | 后续阶段处理 |
| F006 | Fig. 7 | "Sensitivity and ablation summary" | 作者确认 | Medium | 待确认 | 图尚未制作；需作者决定哪些 ablation 进正文图 | 后续阶段处理 |
| F007 | 全文 | 缺少 Fig. 4（主反演结果对比图） | 作者确认 | Medium | 待确认 | 规划文件 §9.1 列出 Fig. 4 为"主反演结果条形图"，但主稿 v0.1 无对应 caption intent | 后续阶段补充 |

---

## A. 高风险问题 Top 10

以下 10 项最影响投稿可信度，必须在 v0.2 前解决：

| 优先级 | ID | 问题 | 为什么高风险 |
|---:|---|---|---|
| 1 | M001 | Euler order / rotation matrix convention 未确认 | 审稿人必问的方法可复现性问题；写错会导致全部结果不可信 |
| 2 | M010 | Target encoding 未确认 | sin/cos 编码是否正确直接影响角误差计算和模型输出解释 |
| 3 | M013 | Angular error formula 未确认 | 指标定义不明确则所有数值表格失去意义 |
| 4 | REF01-07 | 5 个 CITATION 占位 + 8 篇 to verify 文献 | 无引用支撑的论文无法投稿；Table 1 全表依赖文献核实 |
| 5 | N007 | ResNet-18 1.69° 核心数值未交叉核验 | 论文最核心的 upper-bound 数据，必须与实验日志精确对应 |
| 6 | N010 | ResNet+OCS fusion 1.47° 核心数值未交叉核验 | 论文核心融合增益数据 |
| 7 | N016 | 1% noise 85.85° 核心数值未交叉核验 | 论文核心脆弱性证据 |
| 8 | N022 | Table 4 OCS noise 0% 行数值缺失 | 表格不完整无法投稿 |
| 9 | N026 | 作者未决定哪些 ablation 进正文 | §4.6 当前为空壳，无具体数值 |
| 10 | S002 | 作者列表和 CRediT 分工未确认 | 投稿硬性要求 |

---

## B. 可直接进入 v0.2 的修改建议

以下修改不涉及未确认事实，Codex 可安全执行：

| # | 修改内容 | 理由 |
|---:|---|---|
| 1 | Table 4 OCS noise 0% 行填入：OCS-only=5.91±0.22°, fusion=3.93±0.46°, Hit@5 OCS=73.8%, Hit@5 fusion=86.3%, gain=+1.97° | 补充实验 #6 已有确切数据 |
| 2 | Table 4 OCS noise 10% 行补 Hit@5：OCS=57.8%, fusion=74.9% | 同上 |
| 3 | Table 4 OCS noise 20% 行补 Hit@5：OCS=35.8%, fusion=59.6% | 同上 |
| 4 | §4.1 "sub-percent agreement" 改为 "agreement within 0.25% relative error" | 有精确数据支撑（CLAUDE.md Step 5-6） |
| 5 | §3.9 补充 train/test 具体数量："563 training attitudes (10° grid) and 1998 test attitudes (remaining 5° grid points)" | CLAUDE.md 和补充实验均确认 |
| 6 | §4.4 r=0.003 处加括号说明 "(computed for TinyCNN/OCS pair; a corresponding ResNet-pair analysis has not been performed)" | 避免审稿人误读为 ResNet 结论 |
| 7 | Abstract 中 "OCS-image fusion reduces selected clean-image tail errors" 改为 "OCS-image fusion reduces selected clean-image tail errors in this benchmark" | 限定范围，降低过度表述风险 |
| 8 | Table 4 格式：将 "OCS-only -> fusion" 拆为两行（OCS-only 一行 + Fusion 一行），每行独立报告 mean 和 Hit@5 | 期刊排版规范 |
| 9 | §4.5 补入 OCS noise 5% 数据行（OCS-only=7.27±0.65°, fusion=4.65±0.57°, gain=+2.62°） | 补充实验 #6 已有，使趋势更完整 |
| 10 | Fig. 4 caption intent 补入正文（位于 §4.3 和 §4.4 之间） | 规划文件要求，当前主稿遗漏 |

---

## C. 作者需要补充材料清单

| # | 材料 | 用途 | 紧急程度 |
|---:|---|---|---|
| 1 | Euler convention 和旋转矩阵定义的明确文字描述 | 填入 §3.2 | 必须（投稿前） |
| 2 | Angular error 公式的精确数学表达式 | 填入 §3.9 | 必须（投稿前） |
| 3 | Target encoding 确认（sin/cos 4D 输出 + 归一化解码） | 填入 §3.8 | 必须（投稿前） |
| 4 | 8 篇 `[to verify]` 文献的完整书目信息（作者/标题/期刊/卷/页/DOI） | 替换 Related Work 和 Table 1 占位 | 必须（投稿前） |
| 5 | 5 个 `[CITATION: ...]` 的具体文献选择 | 替换 Introduction 占位 | 必须（投稿前） |
| 6 | 目标期刊最终选择（Acta Astronautica / ASR / 其他） | 决定格式、长度、补充材料策略 | 必须（投稿前） |
| 7 | 作者列表和 CRediT 分工 | 填入 Author Contributions | 必须（投稿前） |
| 8 | 数据共享策略决定 | 填入 Data Availability | 必须（投稿前） |
| 9 | 决定哪些 ablation 进正文 vs 补充材料 | 完善 §4.6 | 高（v0.2 前） |
| 10 | ResNet-18 实验日志截图或 CSV 摘要（5 seeds 各 seed 指标） | 交叉核验 N007 | 高（v0.2 前） |
| 11 | ResNet-fusion 实验日志（A1-A4 各 seed 指标） | 交叉核验 N010-N012 | 高（v0.2 前） |
| 12 | ResNet 图像退化实验日志（各退化级别 5 seeds） | 交叉核验 N016-N021 | 高（v0.2 前） |
| 13 | OCS MLP 实验日志（per_part_log / all_raw / total_log 各 seed） | 交叉核验 N003-N005 | 中（v0.2 前） |
| 14 | Weighted kNN 在 10°→5° split 下的 Hit@10 精确值 | 填入 Table 2 | 中 |
| 15 | 是否补做 ResNet-pair OCS-image error correlation | 决定是否可在正文引用互补性证据 | 低（可选） |

---

## D. 审计统计

| 类别 | 数量 |
|---|---|
| 总审计项 | 78 |
| 作者确认 | 22 |
| 数值核验 | 38 |
| 引用核验 | 16 |
| 方法细节未确认 | 7 |
| 表述过强 | 2 |
| 可保留 | 15 |
| High 风险 | 22 |
| Medium 风险 | 28 |
| Low 风险 | 28 |

---

*审计完成。本报告不修改主稿，所有建议交由 Codex 审阅后决定是否纳入 v0.2。*
