# P4-PHYS 后续执行方案（基于 R141 / R142 / R143 的 Claude 执行蓝图）

最后更新：2026-07-06
文件性质：Claude 执行蓝图，忠实落地 R141（主任务单）+ R142（补充约束）+ R143（Codex 固定几何执行方案）。
定位说明：本文不新增路线裁决、不替代 Codex 阶段门、不自行放行。它把 R141/R142/R143 已确定的口径整理为一条可执行序列，供作者作为小项目后续指导；每个阶段门的接收仍以 Codex 审阅为准。

---

## 0. 已读依据

```text
CLAUDE.md（大根 + v0.4）
00_路线冻结文件区/01_三轴小项目_最亮构型与观测规划指导文件.md
04_Codex审阅/R138 / R139 / R140 / R141 / R142 / R143
v0.4_results/21_three_axis_p3_local_refinement/tables/{p3_local_refinement_metrics,p3_high_brightness_refined_candidates,p3_region_summary}.csv
```

---

## 1. 方案定位与不可动摇的边界

本方案只解决一件事的第一步：**在固定 sun/view 几何下，锁定 yaw/pitch/roll 三轴姿态空间中的 single-pose 最亮点，并判断是否需要局部加密。** 完整的“yaw/pitch/roll + sun/view 最亮构型 + 光路解释 + 机制普遍性”被拆成后续阶段门，不在本轮一次做完。

红线（贯穿全部阶段）：

```text
不训练、不启动 R128、不启动路线二/三/四/T3/L2。
不做全网格新渲染；诊断/加密渲染只围绕 top 近邻且受单位上限约束。
不改 19/20/21/22 号包，不改 06_v0.4_code 原文件（派生脚本只进 23A/后续包 scripts/）。
不写成果区、不生成 Codex 审阅文件、不改 CLAUDE.md。
不把 fixed sun/view 结果写成所有 sun/view 上的全局最亮构型。
不把 R4 鲁棒亮区替代 single-pose top-1，除非加密数据实际超过 R1。
在光路诊断完成前，不把 R1 峰称为 glint 机制（只能写 roll-sharp / saturation-associated 高亮峰）。
```

---

## 2. 已被 Codex 核验的事实锚点（R142/R143）

```text
固定几何：phase63 / L1-G1，SUN=[1,0,0.3]，DET=[0.5,-1,0.1]

当前 sampled-grid single-pose top-1（候选，非最终全局最亮）：
  region=R1_high_info, yaw=245.0, pitch=+30.0, roll=+15
  ocs_total=0.208377, glint_flag=0, saturation_flag=1

top-2：R1_high_info, yaw=245.0, pitch=+32.5, roll=+15, ocs_total=0.2079097
  → top-1 与 top-2 相对差 0.224%

R4 最高 single-pose：R4_bright_info_boundary, yaw=147.5, pitch=+12.5, roll=-15
  ocs_total=0.2018225  → top-1 与 R4 相对差 3.15%
  （注意：R4 单点最高在 roll=-15，不是 roll=0）

R1 roll 曲线尖锐：同一 yaw/pitch 下 roll=+15 达 0.208377，
  而 roll=0 与 roll=+30 均约 0.04084 → 连续 roll 峰值未锁定。
```

结论：现有离散 roll 档不足以严肃锁定最亮姿态，**本轮必然触发局部加密**（满足 R142 数值门）。

---

## 3. 阶段总览

```text
阶段 23A / 006A（本轮，R141+R142+R143）：固定几何下 top-1 + roll 局部加密确认。
阶段 P4-PHYS-B（后续门）：对稳定 top-1 做物理光路归因（入射/部位/材料/探测器路径）。
阶段 P4-PHYS-C（后续门）：高亮机制普遍性检验（同类机制是否普遍高亮）。
阶段 sun/view 扩展（后续门）：围绕已识别机制单独扩展 sun/view，回答完整主目标。
阶段 P4-PHYS-D / 收口（后续门）：综合 + 旧 22 号角色辅助回接 + 交 Codex 裁决三轴小项目收口。
```

每个阶段门必须由前一阶段的 Codex 审阅通过后才进入；本方案不预支任何后续门的放行。

---

## 4. 本轮执行：23A 包 / 006A 报告（落地 R143 §4）

### 4.1 输出位置

```text
报告：02_Claude输出/006A_P4PHYS_top1_roll_confirmation_Claude执行报告.md
结果：v0.4_results/23A_three_axis_p4phys_top1_roll_confirmation/
```

### 第 1 步：现有数据复核（只读重聚合，零渲染）

```text
重聚合 P1/P2/P3，输出 current sampled-grid 口径下：
  top-1 / top-N；
  R1 top 簇 roll profile；
  R4 鲁棒亮区 roll profile（单点最高记为 roll=-15）；
  P1/P2/P3 量纲/来源一致性核验；
  固定 sun/view 几何边界声明（phase63/L1-G1，SUN/DET 如上）。
top-1 只写成“fixed phase63/L1-G1 下、已有采样中的 single-pose top-1 candidate”。
```

### 第 2 步：加密触发门判定（R142 数值门）

```text
满足任一即触发局部加密：
  top-1 与 top-2/top-3 相对差 < 5%；
  或 top-1 与 R4 最高 single-pose 相对差 < 5%；
  或 top-1 roll profile 在相邻档出现尖峰；
  或未采样 roll（+10/+12.5/+17.5/+20）可能超过当前 +15。
按现数据（相对差 0.224% / 3.15% + roll 尖峰）→ 触发加密。
```

### 第 3 步：R1 top 簇局部加密（主对象，先 smoke 再正式）

```text
yaw   ∈ {242.5, 245.0, 247.5}
pitch ∈ {27.5, 30.0, 32.5, 35.0}
roll  ∈ {+5, +10, +12.5, +15, +17.5, +20, +25}
规模：3 × 4 × 7 = 84 单位
先渲染 1 姿态 smoke 估规模与产物完整性，再跑全 84。
目的：确认 +15 是否仍为局部最大 / 峰是否迁移到 +10/+12.5/+17.5/+20 / yaw-pitch 是否小幅迁移。
```

### 第 4 步：R4 鲁棒亮区少量对照

```text
中心：yaw=147.5, pitch=+12.5
roll 对照：{-30, -15, 0, +15, +30}
资源允许时加邻域：yaw∈{145,147.5,150}, pitch∈{10,12.5,15}，roll 只留少量代表档。
角色：判断“R1 尖锐峰”与“R4 鲁棒高亮区”是否两类机制；不并列为 top-1。
总诊断单位（第3+4步）控制 ≤150；超限则优先保 R1 roll 细化，R4 只留少量对照。
```

### 第 5 步：停止/追加规则（R143 §4.4）

```text
新 top-1 在 R1 加密网格内部且相邻档无继续上升 → 停止加密，可进入 P4-PHYS-B。
新 top-1 从 +15 迁移到 +10/+12.5/+17.5/+20 但仍在内部 → 以新 top-1 为归因对象，停止加密。
新 top-1 落在边界（roll=+5 或 +25，或 yaw/pitch 边界）→ 只沿该方向追加一小圈，不扩展全局。
R4 对照实际超过 R1 → 重定义 fixed-geometry top-1 为 R4 新点，R1 记为尖锐高亮簇对照。
```

### 第 6 步：光路归因可行性预检（本轮只预检，不做归因）

```text
audit/p4physA_light_path_field_availability.csv
text/p4physA_next_physical_attribution_plan.md
明确：现有 EXR/NPY/JSON 能否做 part/material 归因；
      是否需新增 object/material/normal/depth pass；
      若需要，预计只对哪些姿态做诊断、规模多少。
```

### 006A 报告只回答四问

```text
1. 固定 sun/view 下当前采样内 top-1 是什么。
2. roll 现有遍历到什么程度，是否足以锁定 top-1。
3. 是否执行了局部加密；若执行，新 top-1 是否改变。
4. 下一步是进入 P4-PHYS-B 光路归因，还是继续小范围加密。
```

### 23A 包必备产物

```text
tables/  p4physA_existing_global_top1.csv、_topN.csv、source_pack_coverage.csv、
         top1_roll_profile.csv、topN_cluster_roll_profiles.csv、local_peak_stability.csv、
         refinement_need_decision.csv、refinement_candidate_matrix.csv、
         (若加密) refined_top1_metrics.csv、refined_roll_profile.csv、gate_matrix.csv
figures/ existing_topN_map、top1_roll_curve、top_cluster_roll_curves、(若加密) refined_top1_roll_curve（png+pdf）
text/    existing_top1_summary.md、refinement_decision.md、(若加密) refined_top1_summary.md、
         next_physical_attribution_plan.md、codex_review_checklist_for_006A.md
audit/   light_path_field_availability.csv、generated_files_manifest.csv、
         numeric_path_consistency_check.csv、redline_self_check.csv
```

---

## 5. 后续阶段门（不预支放行，仅列口径）

### P4-PHYS-B 物理光路归因（006A 通过后）

```text
对象：006A 确认稳定的 fixed-geometry top-1。
优先用现有像素级产物归因；不足时仅对 top-1/少数候选做 object-ID/material-ID/normal pass 诊断渲染（先 smoke）。
核心输出：太阳入射方向（目标/相机坐标）、主贡献部件与材料、
          贡献属镜面/漫反射/遮挡边界、反射方向与视线-法向关系。
关键判定：R1 尖锐峰与 R4 鲁棒区是否同一机制。
```

### P4-PHYS-C 高亮机制普遍性（B 通过后）

```text
以 B 段机制签名检验 top-N 是否属同一机制簇，统计亮度中位/分布/rank。
裁定 R1 单点是“孤立尖锐 saturation/glint 尖峰”还是“一片高亮机制”。
```

### sun/view 扩展门（C 通过后）

```text
先锁定固定几何 top-1 并完成其光路归因，再围绕已识别高亮机制单独设计 sun/view 扩展阶段门。
只有此门完成后，才能回答指导文件的完整“yaw/pitch/roll + sun/view 最亮构型”。
```

### P4-PHYS-D / 收口门

```text
旧 22 号包 C09/C01-08/R3 降为辅助标注回接。
最亮构型 + 光路解释 + 机制普遍性齐备后，交 Codex 裁决三轴小项目阶段性收口。
收口通过后方进入 R128 再评估。
```

---

## 6. 风险与注意

```text
1. R1 top-1 saturation_flag=1：可能是饱和/尖锐峰而非稳定物理最亮；加密+光路诊断前不得定性为 glint。
2. R4 单点最高在 roll=-15（非 roll=0/均值），006A 表述须用单点口径，勿沿用 roll0 说法。
3. 固定几何是硬边界：任何“最亮构型”结论都必须带 fixed phase63/L1-G1 前缀，直到 sun/view 扩展门完成。
4. 诊断渲染单位与 smoke-先行是硬约束，超上限须先降 R4 对照、保 R1 roll 细化。
```

（本文为执行蓝图候选，阶段门接收与放行以 Codex 审阅为准。）
