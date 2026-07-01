# 93_1C-B2 方法总结与阶段门候选（整合稿）

最后更新：2026-06-29
执行端：Claude
性质：头B `B-2` 收口交付物。把 87 号 B-2 方法总结与 R92/R93/R94 三份 Codex 审阅的收窄口径整合为单一"方法总结 + 阶段门候选"。**这是 Claude 整合的执行结果与候选规划，不是审阅、不是放行、不是裁决。**
读者：Codex / 作者。
输入：87（B-2 原稿）、R92（B-2 审阅+四篇核读）、R93（PDF 精读确认）、R94（PDF 补读阶段门边界确认）；上游 R91/85/84/R90/R05/05。

> 本文件不启动训练、不生成数据、不改 split/模型/超参/seed、不改代码、不改论文正文、不改成果区、不改 CLAUDE.md。
> 全文严格区分两层：**【方法判断】**（Claude/Codex 技术意见）与 **【放行状态】**（项目是否已正式放行）。除非显式标注"已放行"，一律为未放行候选。
> 相对 87 号，本稿已吸收 R92/R93/R94 的四处关键收窄（见第 4 节），口径以三份 Codex 审阅为准。

---

## 0. 执行摘要

```text
1. 当前 C2/C3 负结果应定位为 protocol-defined yaw extrapolation gap，
   不是 yaw 物理不可观测；单帧多维 OCS 是 light-curve 谱系的退化/降维信息形态。
2. 核心文献证据锁定为三组：Wetterer & Jah 2009（同族可观测性歧义）、
   Gerwe & Idell 2003（Fisher/CRLB 可观测性语言）、Kaasalainen I/II（序列/多几何/歧义边界）。
   其余补读文献强化阶段门与论文边界，但不推翻主结论（R94）。
3. 阶段门顺序确定为：P0 只读诊断 → P1 单项 C 类改正（判据 / 非朴素 fusion）→ P2 光变序列（暂缓）→ P3 不确定性（暂缓）。
4. 唯一"现在最值得做、可申请放行"的是 P0 只读诊断包；P1/P2/P3 全部需 P0 证据后另设阶段门。
5. 所有改正必须保 R04 负结果链可复现，全部走副本/新脚本，不原地覆盖。
```

---

## 1. 方法总结

### 1.1 文献谱系核心证据（Codex 确认）

三组核心证据（R92/R93/R94 共同锁定）：

```text
A. Wetterer & Jah 2009（最贴近本项目）
   - 结构：light curve 序列 + facet 前向模型 + 简化 Cook-Torrance + 四元数 UKF。
   - 关键失败模式：对称目标下不同自转轴产生近乎相同 light curve（经典可观测性问题，Fig.4 解簇）。
   - 对项目：当前 yaw-block 外推失败的最佳文献镜像；BRDF 同族，支撑"沿同族物理模型升维"而非凭空换信息源。
   - 不可越界：不证明单帧 OCS 可定姿；其真实 AEOS 数据部分反提示测量模型不足；UKF 不直接当下一步主模型。

B. Gerwe & Idell 2003（可观测性工具箱）
   - 提供 Cramér-Rao / Fisher information 框架；不同姿态分量有不同最佳观测视角，多视角减少 blind spots。
   - 对项目：把"某 yaw 区难估"从训练现象升级为局部信息量不足；解释 pitch>yaw 各向异性。
   - 收窄：完整 CRLB 需概率测量/噪声模型、局部导数、nuisance parameters；当前阶段先做 Fisher-lite / signature-distance proxy，CRLB 往往偏乐观。

C. Kaasalainen I/II（序列/多几何/歧义边界）
   - 充分多 lightcurves + 多几何可稳定求 convex shape/pole/period；非凸失唯一性、初值重要；多几何覆盖比同分布点数更关键；散射律过复杂会不稳定。
   - 对项目：单帧 OCS 是 lightcurve 的低信息下界而非等价物；后续序列应强调多几何覆盖；不在本阶段引入复杂 BRDF 反演。
   - 不可越界：小行星 shape inversion ≠ 航天器姿态估计；lightcurve 不保证唯一姿态；"更多点"不能替代"更多几何覆盖"。
```

支撑/边界文献（强化阶段门与论文措辞，不改主结论，R93/R94）：

```text
- 融合：Rondao ChiNet 2022 + Pasqualetto 2021 + Linares 2014（MMAE 模型库）
  → 仅支撑"序列/多模态/可分离消融纪律"与 late/decision-level/model-bank/uncertainty-aware fusion，
    不支撑"image 与 OCS 必然互补"；early concat 负结果只否定 naive 拼接。
- sim-to-real：SPEED+ 2022 / SPNv2 2024 / Bechini 2023
  → Blender 纯仿真结果只能写成 protocol-defined simulation evidence；
    合成数据须声明无噪/受控渲染边界；扩展数据应先定义噪声/曝光/阴影/材质扰动，而非只扩样本量；
    在线/自监督适配须报样本级退化风险，不只报均值。
- 真实光度/BRDF：Fankhauser 2023 / Lu 2024
  → 材料/BRDF/地球反照光是不确定源与 nuisance factors；当前不做完整 BRDF 反演。
- 光变定姿补读：Piergentili 2017 / Clark 2022 / Aerospace 2025 joint / Kumar 2025 / Tang 2025
  → 共同支持"先诊断/不要先复杂化 BRDF/序列才是治本但需先证据"；
    Tang/Kumar 更适合作 P2 后文献，不作 P1 立即行动依据。
```

### 1.2 当前结果在文献谱系中的定位

```text
- 单帧多维 OCS：light-curve 的退化/降维形态（抹去时间/几何演化维）；
  不是真实采集姿态信息的标准方式；正向价值是信息下界与对照基线。
- 图像通道：6 层灰度 CNN、零噪声、无增广（84 号代码事实），属理想合成初级形态；
  pitch 在当前协议下稳定高于 chance（R90），承载部分姿态信息，但严格限定当前协议。
- early fusion：image 256 + OCS 128 → concat 384 → 单线性头，图像数值上淹没 OCS；
  其负结果只定位为"该 naive early fusion 在当前协议下无自动增益"。
- yaw-block 负结果：random split 分布内 yaw 可学（~50–70%）；circular yaw-block 下
  continuous/near-hit 接近或仅弱高于随机 → protocol-defined extrapolation gap。
- exact-bin yaw=0.00%：strict classifier + circular yaw-block 外推下的 diagnostic sentinel，
  不是物理不可观测、不是已实现拒识。
```

### 1.3 能说明 / 不能说明（claim 边界）

能说明（fixed-protocol 内成立）：

```text
- 在单帧标量 OCS + 分类 exact-bin + naive early fusion + 零噪声图像 + circular yaw-block 协议下：
  yaw 无法跨未见弧段外推；C2 OCS-only 未检出稳定高于 chance 的可区分信号；
  naive early fusion 无自动互补增益；pitch 高于 chance 但存在 pitch>yaw 各向异性。
```

不能说明（红线，禁止外推）：

```text
- 不能说 yaw 物理不可观测；不能说 OCS 通道本身不携带姿态信息。
- 不能说 image 与 OCS 普遍不互补 / fusion 普遍无效。
- 不能说 exact-bin 0% 是真实拒识机制。
- 不能说结论可迁移真实 GEO / 三轴自由姿态 / 暗室实验。
```

---

## 2. 阶段门候选（吸收 R92/R93/R94 收窄口径）

四级阶段门顺序：**P0 只读诊断 → P1 单项 C 类改正 → P2 光变序列 → P3 不确定性**。
仅 P0 为"现在最值得做、可申请放行"；P1/P2/P3 均需上一级证据后另设阶段门。

### 2.1 P0 只读诊断包（建议作为下一阶段唯一首入口）

```text
P0-1 协议对齐核查
  目的：判定 V0.3↔V0.4 差异来自 split / 判据 / 数据形态 / 模型能力中的哪一项。
  范围：核查 V0.3/V0.4、random split / yaw-block、exact-bin / near-hit、fold/bin 定义是否完全一致。
  产出：同口径重聚合表（不宣称恢复成功）。

P0-2 signature distance
  目的：判定 yaw-block 失败是否对应输入签名近似重合。
  范围：计算 OCS-only / image embedding / joint embedding 的 yaw-yaw 距离矩阵。
  产出：yaw-yaw 距离热图。

P0-3 confusion cluster
  目的：寻找近似等价解簇（对称或近似等价弧段）。
  范围：按真 yaw / 预测 yaw / pitch / fold 聚类。
  产出：混淆簇图、近邻对案例。

P0-4 pseudo-light-curve probe（只能叫 probe，不叫 light-curve experiment）
  目的：单帧 vs 伪序列"信息差是否存在"的零成本预检。
  范围：固定 pitch/几何，把现有 yaw-ordered 单帧样本串成伪序列，只做描述性可分性分析
        （如最近邻 / 线性可分性对比）。
  产出：伪光变曲线示例图 + 描述性可分性对比。
```

P0 验收口径：

```text
- 不训练、不改 split、不生成新数据、不改模型/超参/seed。
- 只回答"信息在哪里不足、歧义是否成簇、是否值得做序列"。
- 建议产物（R93）：方法表（每项诊断回答哪个问题）+ 三类图（distance heatmap /
  confusion cluster map / 伪光变示例）+ 结论表（失败更像判据问题 / 几何盲区 /
  信息形态不足 / 模型容量问题）。
```

### 2.2 P1 单项 C 类改正（P0 后逐项放行，禁止一次全堆）

```text
P1-A 判据 / 损失改正（更底层、更便宜，建议先做）
  问题：exact-bin 分类是否放大了 yaw-block 失败？
  候选：sin-cos / circular regression、circular distance、von-Mises / NLL、near-hit / top-k angular band；
        或 regression + classification 双头。
  必须保留：exact-bin sentinel 作附指标，便于与 R04 链对照。
  指标：延续 E45B 重构口径（circular MAE / within-k° / coarse-bin vs chance）+ 连续角误差。

P1-B 非朴素 fusion 改正
  问题：image 与 OCS 是否互补（而非 naive concat 是否碰巧增益）？
  候选：late / decision-level fusion、model-bank / probabilistic fusion、mid fusion + 模态维度平衡、gated fusion。
  必做消融：image-only / OCS-only / early concat / late-or-decision fusion 并列，逐项报边际贡献。
  必做：模态维度平衡（防 image 256 淹没 OCS 128）。

执行顺序：先 P1-A 再 P1-B。理由：判据问题更底层、更便宜，更可能直接改变"0% 是否代表失败"的解释。
```

### 2.3 P2 正式 light-curve sequence（暂缓，满足条件后另设最重门）

进入条件（R92 3.3 / R93 / R94，四到五条）：

```text
1. P0 证明单帧签名存在 yaw 等价簇或低距离混淆 / 几何盲区；
2. P1-A 后 yaw-block 仍存在显著外推鸿沟；
3. 新数据协议写清多时刻/多几何采样、噪声/退化、BRDF、遮挡、预配准；
4. 明确 inverse-crime 防护（前向模型、噪声、几何采样、train/test yaw-block 全部预注册）；
5. 明确 single-frame OCS 是 lower information layer，sequence 是 higher information layer。

配套：序列模型（1D-CNN / LSTM / Transformer）；主对比为单帧 OCS vs light-curve sequence
      在同一姿态量、同一 split 协议下的 yaw 外推可分性。
论文定位：lower bound vs higher information layer 的【层级对比】，不写成"single-frame failed, so replaced by sequence"。
```

### 2.4 P3 不确定性 / 置信（暂缓，信息源/融合未升级前增益有限）

```text
- 校准 / ECE（Guo 2017）：第一步可测置信指标。
- conformal prediction / prediction set（Angelopoulos & Bates 2023）：把 sentinel 升级为有覆盖保证的拒识。
- 双通道 agreement / disagreement：24 号三问 trustworthy 支柱的置信代理。
- 前置条件：依赖 P1-A/B 已落地；信息源未改时单独做校准增益有限。
- 暂缓档：更强 backbone（ResNet/ViT/预训练）、偏振 / 多光谱新信息维。
```

---

## 3. R04 负结果链保护与执行纪律

```text
- 所有改正（判据 / fusion / 信息源 / 不确定性）全部走副本 / 新脚本，不原地改 R04 代码/数据/成果链。
- 每个 C 类阶段门为独立可放行单元，逐项记录边际贡献，使改进成为可发表消融，而非调参追结果。
- 84 号已警告：一次性全堆 = 把预注册负结果污染成调参追结果。
- 若新增脚本仅限只读分析（P0），必须记录输入 JSON/CSV、输出路径，并声明未触碰训练流程。
```

---

## 4. 相对 87 号的四处关键收窄（吸收 R92）

```text
1. "P0 判据/损失"降级：凡涉及训练目标 / loss / 输出头变化，归入 P1（C 类阶段门），不再叫 P0。
   → 本稿 P0 仅含四项只读诊断，判据改正已移入 P1-A。
2. "伪光变曲线"严格降级为 probe：由现有 yaw 排序样本拼接，不等价真实时间序列观测，
   不得叫 light-curve experiment。
3. Fisher/CRLB 收窄：当前阶段先做 Fisher-lite / signature-distance proxy；
   完整 CRLB 需明确噪声模型、观测模型、参数化与 nuisance parameters，且 CRLB 偏乐观。
4. ChiNet / 融合文献收窄：仅支撑"序列 / 多模态 / 可分离消融纪律"，
   不支撑"OCS 与图像必然互补"。
```

---

## 5. 推荐论文方法叙事（R92/R93/R94 一致版本，候选）

中文：

```text
当前结果揭示的是单帧 OCS/图像输入在 yaw-block 外推协议下的可辨识性鸿沟，
而不是 yaw 的物理不可观测。该现象与光变定姿、CRLB 与小行星光变反演文献中
由目标对称性和观测几何不足导致的歧义一致。因此，本文将单帧 OCS 视为受控仿真条件下的信息下界，
并将后续工作设计为阶段式路径：首先进行只读可观测性诊断，其次评估连续角度判据与非朴素多模态融合，
最后在诊断证据充分时再扩展到光变序列建模。
```

英文：

```text
The current results indicate a protocol-defined yaw extrapolation gap under single-frame OCS/image inputs,
rather than a physical unobservability of yaw itself. Prior work on photometric attitude estimation,
CRLB-based orientation analysis, and light-curve inversion shows that attitude identifiability depends
strongly on viewing geometry, temporal coverage, reflectance modeling, and target symmetry. We therefore
treat single-frame OCS as a controlled lower-information setting and propose a staged path: read-only
observability diagnostics, continuous angular criteria and non-naive multimodal fusion, followed by
light-curve sequence modeling only when the diagnostic evidence justifies the added complexity.
```

可写 claim / 不可写 claim 见 1.3 节。

---

## 6. 合并审阅与待裁决问题

按 R05，头A 已在 R90 收口（A-1/A-2/A-3 DONE，成果区 16/17/18）。头B 现状：

```text
B-1 文献检索：DONE（R91，PDF 入库 30 篇）
B-2 方法总结与阶段门候选：本整合稿（87 + R92/R93/R94 收口）
B-3 单帧 vs 光变曲线对比设计：87 号已给候选设计，未执行
B-4 模型改正候选：87 号已给候选设计，未执行
→ R05 合并审阅条件 2 已具备，可触发头A/头B合并审阅（待 Codex/作者确认）。
```

合并审阅建议只裁定以下问题（合并 R92 §5 与 87 号 §8.2，去重）：

```text
Q1. 是否正式放行 P0 只读诊断包（协议对齐 / signature distance / confusion cluster / 伪光变 probe）？
Q2. P0 输出目录、命名、验收表（方法表 + 三类图 + 结论表）由谁定稿？
Q3. P1-A 判据改正是否作为第一项 C 类阶段门？是否要求双头保留 exact-bin sentinel？
Q4. P1-B fusion 改正是否必须与 P1-A 解耦、分别报告边际贡献？
Q5. P2 light-curve sequence 是否采用本稿 2.3 节进入条件？inverse-crime 防护规格由谁定稿？
Q6. 可观测性诊断中哪些归 D 类只读（不设重门）、哪些必须建模另设门？
Q7. 置信一致性（24 号三问 trustworthy）最低可写实现门槛（ECE / conformal / agreement）由 Codex 定义验收口径？
Q8. 本 B-2 是否已满足 R05 合并审阅条件 2，可否即触发头A/头B合并审阅？
```

---

## 7. 红线自检

```text
- 本文件不启动训练、不生成数据、不改 split/模型/超参/seed、不改代码、不改正文、不改成果区、不改 CLAUDE.md。
- 未声称当前模型能可靠反演；未声称已证互补；未把 exact-bin 0% 当物理不可观测或已实现拒识。
- 未把 light-curve 文献等同当前单帧 OCS 结果；未把 modern fusion 文献当作 joint negative result 的反证。
- 未把 calibration/conformal 文献包装成系统已有拒识能力；未外推真实 GEO / 三轴 / 暗室。
- 全部"建议采用 / 优先级 / P0–P3 / B-3 / B-4"均为候选，未放行，需 Codex/作者按阶段门裁定。
- 本稿只整合 87 + R92/R93/R94，未新增超出三份审阅口径的方法主张。
```

## 8. 关联文件

```text
87（B-2 原稿）、R92（B-2 审阅+四篇核读）、R93（PDF 精读确认）、R94（PDF 补读阶段门边界确认）；
R91（B-1 文献约束）、85（文献补课）、84（暂停点复盘与代码事实）、
R90（头A桥接稳定）、R05（两头并行结构）、05（PDF 入库状态）。
```

