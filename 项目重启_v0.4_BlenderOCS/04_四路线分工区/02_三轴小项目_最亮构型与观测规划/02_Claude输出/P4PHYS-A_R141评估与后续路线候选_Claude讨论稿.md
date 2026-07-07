# P4-PHYS-A / R141 评估与后续路线候选（Claude 讨论稿）

最后更新：2026-07-06
文件性质：Claude 候选讨论材料，非 Codex 审阅、非阶段门裁决、非成果区结论。
定位说明：本文只列评估意见、证据路径、路线候选和待裁决问题；是否采纳、是否落成正式任务单，交 Codex / 作者裁决。按分工规则，路线设计与技术裁决属 Codex 职责，本文不自行放行、不扩展路线为既定事实。

---

## 0. 已读依据

```text
CLAUDE.md（大根 + v0.4）
04_四路线分工区/02_三轴小项目_最亮构型与观测规划/00_路线冻结文件区/01_三轴小项目_最亮构型与观测规划指导文件.md
04_Codex审阅/R138_Codex_补充校正_三轴小项目最亮构型主目标与roll遍历口径.md（经 CLAUDE.md 引用确认口径）
04_Codex审阅/R139_Codex_审阅_005不通过_旧P4需按最亮构型光路机制返工.md
04_Codex审阅/R140_Codex_任务单_P4PHYS最亮构型物理光路归因长程任务.md
04_Codex审阅/R141_Codex_任务单_P4PHYS-A_top1与roll局部确认.md
v0.4_results/21_three_axis_p3_local_refinement/tables/{p3_local_refinement_metrics,p3_high_brightness_refined_candidates,p3_region_summary}.csv
```

23A 包与 006A 报告当前不存在（`v0.4_results/23A_*` 无文件），故本文按“R141 尚未执行”的前提评估。

---

## 1. R141 评估

### 1.1 妥当之处

```text
1. 未把 R140 一次性执行到底，先做 top-1 + roll 局部确认，逻辑正确：top-1 未稳前做物理光路归因无意义。
2. 明确限定为“当前采样网格内 single-pose top-1”，不写成连续空间全局最亮；与红线（不夸大为真实反演）一致。
3. 禁止项完整遮断 R128、路线二/三/四、全网格新渲染、成果区改写、CLAUDE.md 改动；符合现阶段红线。
```

### 1.2 与实表核验的结论

用 P3 明细表交叉验证 R139/R141 的 top-1 候选：

```text
single-pose 单点最大（p3_local_refinement_metrics.csv）：
  R1_high_info, yaw=245.0, pitch=+30.0, roll=+15, ocs_total ≈ 0.2084
  top-2: yaw=245.0, pitch=+32.5, roll=+15, ocs_total ≈ 0.2079   （与 top-1 相对差约 0.2%）

R4 亮区（p3_high_brightness_refined_candidates.csv）：
  yaw=147.5, pitch=+12.5, ocs_roll0 ≈ 0.2011（R4 内 brightness_rank=1），与 R1 单点相对差约 3.5%

区域平均（p3_region_summary.csv）：
  R4 mean_ocs = 0.0976 > R1 mean_ocs = 0.0456（R4 约为 R1 两倍）
  R4 norm_brightness = 0.444 > R1 norm_brightness = 0.157
  R1 mean_roll_sensitivity = 3.50（极尖锐） vs R4 = 0.093（近平坦）
  R4 glint=0、saturation 有但 image_usable_all=1；R1 roll 峰尖锐
```

推论：**single-pose 单点最大是 R1，但与 R4 仅差约 3.5%，而区域平均层面 R4 明显更亮且 roll 鲁棒。** 现有表已足以提示 R141 §6-B 的问题“R4 是否接近 top-1” 答案为“接近（僅差）”，R141 把它列为首个决策任务是对的。

### 1.3 待补的三点

```text
待补点1（sun/view 缺席）：
  指导文件与 R140 §1 主目标是“yaw/pitch/roll + sun/view 构型最亮”，
  但 R141 §6-D 加密只含 yaw/pitch/roll，sun/view 未列为变量。
  若 P1–P3 的 sun/view 固定，则当前 top-1 只是“该 sun/view 下的姿态 top-1”，
  不足以直接称主目标意义上的“最亮构型”。
  建议：006A 至少用一句明确 P1–P3 中 sun/view 是固定还是变量；
        若固定，登记为 P4-PHYS-B 及以后的必修残课题。

待补点2（“最亮”定义暗含吸附到单点最大）：
  R1（单点0.2084、roll 峰尖锐=3.50）与 R4（区域平均更亮、roll 鲁棒≈0.09）物理上是两类。
  R1 单点像“局部 glint / 数值尖峰”嫌疑较大，正是 R141 §6-C 判定“需加密”的情形；
  R4 则 roll 鲁棒、观测更稳定。
  若 P4-PHYS-B 只归因 R1 单点，可能漏掉更现实的高亮机制（R4）。
  建议：006A 阶段把“single-pose top-1（R1）”与“roll-robust brightest region（R4）”并置为 top-1 级双候选。

待补点3（加密要否阈值未定量）：
  R141 §6-C 决策规则只有“差很小 / 尖锐”等定性表述，缺可复现数值门。
  建议加数值门，例如：
    - top-1 与 top-2 的 ocs_total 相对差 < 5% → 需加密；
    - roll 曲线 +15 处若可能被 +10/+20 的插值峰超过 → 需加密。
  按现数据 R1(0.2084) vs top-2(0.2079) 相对差约 0.2%，几乎必然触发“需加密”。
```

---

## 2. 后续路线候选：P4-PHYS-A → 收口的四段阶段门

保持现红线（诊断渲染仅限 top 近邻且受上限约束、不训练、不启动 R128、不写成果区）。

### 段阶 0：R141/006A 内即时补正（不新增阶段门）

```text
- top-1 以 R1 单点 / R4 鲁棒区“双候选”确定，而非只取单点最大。
- 用一句明确 P1–P3 的 sun/view 是固定还是变量；固定则登记为 B 段必修残课题。
- 加密要否用数值门（相对差5% + roll 峰插值检查）判定；预期触发 R1 top 簇 roll ∈{+5,+10,+12.5,+15,+17.5,+20} 加密，R4 仅少量对照，总诊断单位 ≤150。
- §6-E 可行性预检：把现有可用字段（n_pixels_contributing、mean_lit、glint_flag、saturation_flag）与缺失字段（per-part、per-material、法线 normal、探测器方向）明确分列。
```

### 段阶 A→B 门：P4-PHYS-B 物理光路归因（对应 R140 §6-C）

```text
- 先用现有 EXR/NPY 做像素级归因；若无法给出 per-part/per-material，
  则仅对 top-1/少数候选做 object-ID / material-ID / normal pass 诊断渲染
  （R140 ≤300 单位内，先 1 姿态 smoke 估规模）。
- 核心输出：太阳入射方向（目标坐标/相机坐标）、主贡献部件与材料、
  贡献属镜面 glint / 漫反射 / 遮挡边界、反射方向与视线-法向关系。
- 关键科学分叉：判定 R1 与 R4 是否同一机制。
```

### 段阶 B→C 门：P4-PHYS-C 高亮机制普遍性（对应 R140 §6-D）

```text
- 以 B 段机制签名（dominant_part + material + incident_bin + view_bin + glint 状态）
  检验 top-N 是否属同一机制簇，统计亮度中位/分布/rank。
- 裁定 R1 单点是“孤立尖锐 glint 尖峰”还是“一片高亮机制”。
- 待检验假设：普遍高亮机制更可能出现在 roll 鲁棒的 R4 侧。
```

### 段阶 C→收口：P4-PHYS-D 综合与辅助回接（对应 R140 §6-E/F）

```text
- 旧 22 号包 C09 / C01-08 / R3 降为辅助标注回接。
- 若“最亮构型 + 光路解释 + 机制普遍性”齐备，交 Codex 裁决三轴小项目阶段性收口。
- 收口通过后方进入 R128（新路线二候选规划）再评估。
```

### 一句话要点

```text
R141 方向正确，但若把主目标吸附到“single-pose 单点最大=R1 的尖锐峰”存在风险：
数据上 R4 鲁棒亮区与 R1 仅差约 3.5% 且观测更稳。
建议 A 段并置 R1/R4，B/C 段物理切分“尖锐尖峰 vs 一片高亮机制”，
这是把小项目稳妥落到“最亮构型及其光路机制”的最短路径。
```

---

## 3. 待 Codex / 作者裁决的问题清单

```text
Q1 是否采纳“R1 单点 / R4 鲁棒区”双候选口径，替代单点最大唯一 top-1？
Q2 是否接受把加密要否改为数值门（相对差5% + roll 峰插值检查）？
Q3 sun/view 在 P1–P3 是否为固定量？若固定，是否同意登记为 P4-PHYS-B 必修残课题？
Q4 是否采纳 A→B→C→收口 四段阶段门作为 R140 的落地拆分？
Q5 R1 若判为局部 glint/数值尖峰，是否允许其不作为唯一主结论，而与 R4 机制并列陈述？
```

（本文为候选讨论稿，结论以 Codex 审阅与作者裁决为准。）
