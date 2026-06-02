# Claude 输出：全文压缩与期刊风格

> 生成日期：2026-06-02  
> 基于：最终整合版 v0.1 + 前三阶段整合清单 + 02b bib 修订  
> 目标期刊参考：Acta Astronautica / Advances in Space Research（正文 8000-10000 词）  
> 输出目的：供 Codex 审阅整合为 v0.2 语言压缩方案

---

## 1. 全文字数估算与压缩目标

| 章节 | 当前估算词数 | 目标词数 | 压缩率 | 说明 |
|---|---:|---:|---:|---|
| Abstract | ~280 | 200-250 | 10-30% | 当前略长，但信息密度高；可压缩重复边界声明 |
| Introduction | ~700 | 550-600 | 15-20% | 有重复问题陈述 |
| Related Work (含 Table 1) | ~1100 | 800-900 | 20% | 每小节末尾定位句可压缩 |
| Method | ~1800 | 1400-1500 | 15-20% | §3.5 遮挡细节可移补充材料 |
| Results | ~2200 | 1800-2000 | 10-15% | §4.4 TinyCNN 诊断可压缩 |
| Discussion | ~1600 | 1200-1300 | 20% | §5.2-5.3 重复 Results 解释 |
| Conclusion | ~250 | 200 | 20% | 与 Abstract 部分重复 |
| **总计** | **~7930** | **~6400** | **~20%** | 目标：7000±500 词正文（不含 references/captions） |

---

## 2. 逐章压缩审计

### 2.1 Abstract

| 位置 | 当前问题 | 风险 | 建议处理 | 可替换文本 | 不能删除的边界 |
|---|---|---|---|---|---|
| Abstract 第 1 句 | "remains difficult because scalar photometric signatures and resolved photometric images encode different, observation-dependent attitude cues" 过长 | Low | 压缩 | "remains challenging because scalar and resolved optical modalities encode different attitude information" | — |
| Abstract 第 3-4 句 | "This physically consistent setting enables..." 与前句重复"unified" | Low | 压缩 | 合并为一句："From this model, we benchmark OCS-only, image-only, late-fusion, and feature-fusion inversion." | — |
| Abstract "defining an idealized upper-bound condition..." | 必须保留的边界声明 | — | 保留 | — | 不能删除 clean-image = upper bound 限定 |
| Abstract 末句 "Real optical telescope validation..." | 必须保留的边界声明 | — | 保留 | — | 不能删除 no real validation 声明 |

### 2.2 Introduction

| 位置 | 当前问题 | 风险 | 建议处理 | 可替换文本 | 不能删除的边界 |
|---|---|---|---|---|---|
| §1 ¶1-¶2 | 两段都在说"OCS 和 image 不同"；¶2 是 ¶1 的展开，可压缩 | Low | 压缩 | 将 ¶2 压至 2 句嵌入 ¶1 末尾 | — |
| §1 ¶3 "The central unresolved question..." | 核心科学问题，不应压缩 | — | 保留 | — | 不能删除"cannot be answered cleanly if...inconsistent assumptions" |
| §1 ¶3 "Real ground-based optical observations are affected by..." | 列举过长（9 项退化源） | Low | 压缩 | 改为"affected by atmospheric, sensor, and calibration effects" + 一个引用 | 不能删除退化存在的事实 |
| §1 ¶4 四条贡献 | 贡献 3 和 4 表述冗长 | Low | 压缩 | 各压缩为 1 句（去掉"should not be read as"等解释性从句） | 不能删除 clean-image ≠ field 限定 |
| §1 末段 "The present study does not use..." | 边界声明 | — | 保留 | — | 不能删除 |

### 2.3 Related Work

| 位置 | 当前问题 | 风险 | 建议处理 | 可替换文本 | 不能删除的边界 |
|---|---|---|---|---|---|
| §2.1-2.4 每节末尾 | 每节都有 2-3 句"本文定位句"，4 节共 ~10 句定位 | Medium | 压缩 | 每节保留 1 句定位；删除重复的"The present study/work" | — |
| §2.1 第 1 句 | "governed by the coupled effects of target geometry, surface material, illumination direction, viewing direction, phase angle, and visibility" 6 项列举过长 | Low | 压缩 | "governed by geometry, material reflectance, illumination-viewing geometry, and visibility" | — |
| §2.3 "Such work highlights both the power..." | 评论性过强 | Low | 降调 | 改为"illustrating both the potential and the sim-to-real transfer challenge" | — |

### 2.4 Method

| 位置 | 当前问题 | 风险 | 建议处理 | 可替换文本 | 不能删除的边界 |
|---|---|---|---|---|---|
| §3.1 整段 | 与 Abstract/Introduction 三重重复框架描述 | Medium | 压缩 | 保留"four stages"列表，删去前 3 句重复性介绍 | — |
| §3.5 遮挡细节 | epsilon/min_hit_distance/ray-origin-offset 描述占 ~150 词 | Medium | 移到补充材料 | 正文保留 1 句"analytical ray-based visibility with validated epsilon settings (details in Supplementary)"；细节移补充 | 不能删除自遮挡存在的事实 |
| §3.8 "To handle angular periodicity..." | 仍为占位 | — | 暂不处理 | — | 不能删除；等作者确认后填入 |
| §3.9 整段 | 可压缩为 3-4 句（当前 ~120 词，信息密度低） | Low | 压缩 | — | 不能删除 10°→5° split 定义和 seed 信息 |

### 2.5 Results

| 位置 | 当前问题 | 风险 | 建议处理 | 可替换文本 | 不能删除的边界 |
|---|---|---|---|---|---|
| §4.1 第 1 段 | 再次描述框架设置（已在 §3.1 和 §1 描述过） | Medium | 压缩 | 删去前 3 句，直接从"Before evaluating..."开始 | — |
| §4.2 末段 "The OCS-only results support two conclusions..." | 合理总结，但可压缩 | Low | 压缩 | 合并为 1 句 | 不能删除"not every OCS representation has the same operational meaning" |
| §4.4 ¶3 TinyCNN/OCS 诊断 | ~120 词的旧实验诊断；与 ResNet 主线不一致 | Medium | 移到补充材料 | 正文保留 1 句"Earlier TinyCNN/OCS experiments support conditional complementarity (Supplementary)" | 不能删除 r=0.003 是 TinyCNN pair 的限定 |
| §4.5 图像退化详细列举 | sigma=0.03/0.05/0.10 重复同一结论 | Low | 压缩 | 正文保留 sigma=0.01 和 sigma=0.10 两端，中间用"similarly poor (85-88°)"概括 | — |
| §4.6 | 当前近乎空壳 | — | 暂不处理 | 等作者确认后填入 | — |

### 2.6 Discussion

| 位置 | 当前问题 | 风险 | 建议处理 | 可替换文本 | 不能删除的边界 |
|---|---|---|---|---|---|
| §5.1 | 与 §4 结论重复 | Medium | 压缩 | 删去前 2 句，直接从"This framing changes..."开始 | 不能删除"conditional complementarity" |
| §5.2 "understandable because the clean rendered images preserve stable visual cues..." | 合理但过长 | Low | 压缩 | 压缩为 2 句 | 不能删除"should be interpreted as optimistic upper-bound" |
| §5.3 ¶1 和 ¶2 | 重复"OCS 不是上限但有别的价值" | Medium | 压缩 | 合并为 1 段 3 句 | 不能删除"does not imply immunity to all real observational errors" |
| §5.4 | 与 §4.4 重复 fusion 结果解释 | Medium | 压缩 | 只保留新解读（tail behavior > mean），删重复数字 | — |
| §5.5 | 独立的实践建议段落，可保留但压缩 | Low | 压缩 | 4 点建议压缩为 3 句 | — |
| §5.6 Limitations | 必须保留且不能压缩 | — | 保留 | — | 全段不能删除 |

### 2.7 Conclusion

| 位置 | 当前问题 | 风险 | 建议处理 | 可替换文本 | 不能删除的边界 |
|---|---|---|---|---|---|
| Conclusion ¶1 | 与 Abstract 第 1-2 句近乎重复 | Low | 压缩 | 用 1 句概述贡献，不重复框架描述 | — |
| Conclusion ¶2 | 合理的数值总结 | — | 保留 | — | 不能删除 1.69°/85.85°/6.6° 数字 |
| Conclusion ¶3 | 未来工作 | — | 保留 | — | 不能删除 "does not include real optical telescope validation" |

---

## 3. 章节级压缩路线（A）

| 章节 | 压缩策略 | 预计节省 |
|---|---|---|
| Abstract | 压缩 2 处冗长从句；保留全部边界声明 | ~30 词 |
| Introduction | 合并 ¶1-¶2 重复；压缩退化源列举；压缩贡献 3/4 | ~100 词 |
| Related Work | 每节只保留 1 句定位句；压缩列举 | ~200 词 |
| Method §3.1 | 删去重复框架介绍 | ~80 词 |
| Method §3.5 | 遮挡细节移补充材料 | ~120 词 |
| Results §4.1 | 删去重复框架描述 | ~80 词 |
| Results §4.4 | TinyCNN 诊断段移补充材料 | ~120 词 |
| Results §4.5 | 中间噪声级概括 | ~40 词 |
| Discussion §5.1-5.4 | 删重复、合并段落 | ~300 词 |
| Conclusion | 压缩重复框架句 | ~50 词 |
| **总计** | | **~1120 词** |

预计压缩后正文 ~6800 词，符合 Acta Astronautica / ASR 篇幅要求。

---

## 4. 术语统一与禁用表述（B）

### 4.1 推荐统一术语

| 概念 | 推荐术语 | 避免使用 |
|---|---|---|
| 仿真光度图像 | clean rendered photometric images | synthetic images / simulated images（太泛） |
| OCS 特征 | OCS signatures / OCS features | light curve（本文不是时序） |
| ResNet 结果性质 | clean-image upper-bound condition | best result / state-of-the-art / field performance |
| 融合增益 | conditional complementarity | universal superiority / always better / fusion dominance |
| OCS 噪声实验 | controlled OCS noise | realistic noise / field noise |
| 图像噪声实验 | controlled image degradation / stress test | realistic degradation / atmospheric model |
| all_raw 特征 | semi-oracle / diagnostic upper bound | operational / practical / realistic OCS |
| per_part_log 特征 | practical component-level OCS | best OCS / recommended OCS |
| 姿态任务 | yaw-pitch inversion under fixed roll | full pose estimation / 3-DOF recovery |
| 引用名（已修正） | Yang et al. 2025; Burton et al. 2024; Yi et al. 2024 | Yang 2024; Hanada 2024; Liu 2024 RS |

### 4.2 禁用/慎用表述

| 禁用表述 | 原因 | 安全替代 |
|---|---|---|
| "demonstrates real-world performance" | 无真实验证 | "demonstrates performance under controlled rendered imagery" |
| "fusion is universally/always superior" | 结果是条件性的 | "fusion provides conditional complementarity" |
| "OCS is robust" (无限定) | OCS 仅对图像像素退化不敏感 | "OCS is independent of image-pixel degradation in this benchmark" |
| "state-of-the-art" | 无 SOTA 对比基准 | "strong image-based upper bound" |
| "comprehensive degradation model" | 仅做高斯噪声和亮度缩放 | "controlled stress test" |
| "novel" / "first" / "pioneering" | 无法证实 | "unified" / "controlled" / "systematic" |
| "validated" (无限定) | 无外部实验验证 | "verified through analytical closure tests and rendering consistency" |

---

## 5. 可直接合并的局部替换文本（C）

### 替换 1：Abstract 第 1 句压缩

**原文**：
> Accurate attitude estimation of non-cooperative space objects from optical observations remains difficult because scalar photometric signatures and resolved photometric images encode different, observation-dependent attitude cues.

**替换为**：
> Attitude estimation of non-cooperative space objects from optical observations remains challenging because scalar and resolved photometric modalities encode different attitude information.

### 替换 2：Introduction ¶3 退化源列举压缩

**原文**：
> Real ground-based optical observations are affected by atmospheric seeing, tracking error, sensor noise, optical blur, limited resolution, background contamination, phase-angle variation, and calibration uncertainty

**替换为**：
> Real ground-based optical observations are affected by atmospheric, sensor, and calibration effects that degrade image quality

### 替换 3：§4.1 删去重复框架开头

**原文**（前 3 句）：
> The unified forward model provides a physically consistent basis for comparing scalar OCS signatures and rendered photometric images. The benchmark uses a real satellite STL geometry with three component groups: metal body, solar panel, and baffle/shade. These components are assigned nonuniform GGX/Cook-Torrance material settings, and the same attitude definition, illumination direction, viewing direction, BRDF, and visibility assumptions are used to generate both OCS signatures and photometric images.

**替换为**：
> Before evaluating attitude inversion, we verified the numerical consistency and visibility behavior of the forward model described in Section 3.

### 替换 4：§4.5 中间噪声级概括

**原文**：
> Increasing the noise level to sigma = 0.03, 0.05, and 0.10 gives similarly poor mean errors of 85.49 deg, 85.97 deg, and 87.92 deg, with Hit@5 decreasing to 1.5%, 1.2%, and 1.0%, respectively.

**替换为**：
> Higher noise levels (σ = 0.03–0.10) yield similarly collapsed performance (mean 85–88°, Hit@5 ≤ 1.5%).

### 替换 5：§5.1 删去重复开头

**原文**（前 2 句）：
> The main finding is that scalar OCS signatures and resolved photometric images provide different attitude constraints when they are generated from the same BRDF-driven physical model. The benchmark is not simply a comparison of neural architectures.

**替换为**：
> The benchmark isolates how two optical modalities behave when geometry, material, BRDF, and visibility are held consistent.

---

## 6. 作者确认项保护清单（D）

以下占位/边界声明在语言压缩中**绝对不能被删除或改写为事实**：

| # | 占位/边界 | 位置 | 原因 |
|---:|---|---|---|
| 1 | `[需要作者确认：Euler order / rotation matrix convention]` | §3.2 | 方法可复现性 |
| 2 | `[需要作者确认：exact target encoding]` | §3.8 | 模型输出定义 |
| 3 | `[需要作者确认：angular error formula]` | §3.9 | 指标定义 |
| 4 | `[需要作者确认：phase63 fairness and cross-phase values]` | §3.3 | 实验范围 |
| 5 | `[需要作者确认：which ablations have final numbers]` | §4.6 | 结果完整性 |
| 6 | `[需要作者确认：0% OCS noise table values]` | §4.5/Table 4 | 表格完整性 |
| 7 | `[需要作者确认]` kNN Hit@10 | Table 2 | 数值精确性 |
| 8 | "defining an idealized upper-bound condition...rather than field performance" | Abstract | 写作红线 |
| 9 | "The present study does not use real optical telescope images..." | §1/§5.6/§6 | 写作红线 |
| 10 | "These are controlled stress tests, not complete atmosphere/sensor models" | §4.5/§5 | 写作红线 |
| 11 | "conditional complementarity rather than universal superiority" | §4.4/§5/§6 | 写作红线 |
| 12 | "semi-oracle upper bound" 对 all_raw 的限定 | §3.6/§4.2/Table 2 | 写作红线 |
| 13 | "computed for TinyCNN/OCS pair; not ResNet" 对 r=0.003 的限定 | §4.4 | 写作红线 |
| 14 | Data Availability / Author Contributions / CoI 占位 | 末尾 | 投稿硬性要求 |

---

*第 4 阶段 Claude 侧输出完成。本报告不重写全文，只给结构化压缩建议和安全局部替换。所有建议交由 Codex 审阅后决定是否纳入 v0.2。*
