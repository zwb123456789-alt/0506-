# 006A P4-PHYS-A top-1 与 roll 局部确认执行报告

最后更新：2026-07-06  
执行依据：R145_Codex_长任务提示词_执行R141生成23A006A.md  
结果包：`v0.4_results/23A_three_axis_p4phys_top1_roll_confirmation/`

---

## 1. 任务边界

本轮只确认固定 phase63/L1-G1 sun/view 几何下的 yaw/pitch/roll 三轴 single-pose top-1 与 roll/pitch 局部加密。

```text
几何固定：phase63 / L1-G1
SUN = [1, 0, 0.3]
DET = [0.5, -1, 0.1]
```

**不是**所有 sun/view 几何下的全局最亮构型搜索。

---

## 2. 输入与脚本

读取文件：

- P1 `19_three_axis_p1_seed_roll_scan/tables/p1_seed_roll_ocs_table.csv`（108 行）
- P2 `20_three_axis_p2_sparse_grid/tables/p2_sparse_grid_metrics.csv`（1125 行）
- P3 `21_three_axis_p3_local_refinement/tables/p3_local_refinement_metrics.csv`（963 行）
- R139–R145 Codex 审阅文件（均已读取，见 `audit/read_files_manifest.csv`）

执行脚本（均在 `23A/scripts/`）：

```text
p4physA_step1_audit_and_topN.py       任务 A/B
p4physA_step2_rollprofile_decision.py 任务 B/C/D
p4physA_prepare_refinement_matrix.py  任务 E 矩阵准备
p4physA_render_refinement.py          任务 E 渲染
p4physA_postprocess_refinement.py     任务 E 后处理
p4physA_collect_refined_metrics.py    任务 E 指标收集
p4physA_step3_FG_decision.py          任务 F/G
p4physA_step4_gate_and_audit.py       §6 验收
```

---

## 3. 现有采样 top-1 / top-N

P1/P2/P3 合并去重后（优先级 P3 > P2 > P1），sampled-grid 口径下：

| 排名 | region | yaw | pitch | roll | ocs_total |
|------|--------|-----|-------|------|-----------|
| top-1 | R1_high_info | 245.0 | +30.0 | +15 | **0.208377** |
| top-2 | R1_high_info | 245.0 | +32.5 | +15 | 0.207910 |
| top-3 | R1_high_info | 245.0 | +35.0 | +15 | 0.206267 |
| R4 top | R4_bright_info_boundary | 147.5 | +12.5 | −15 | 0.201822 |

Codex 核验值均 **MATCH**（偏差 < 1e-5）。

- top-1 vs top-2 相对差：**0.224%**（< 5%，触发加密门）
- top-1 vs R4 top 相对差：**3.146%**（< 5%，触发加密门）

---

## 4. Roll profile 与加密决策

**R1 yaw=245.0 pitch=+30.0 roll profile**（P3 档位 −60 至 +60）：

| roll | ocs_total |
|------|-----------|
| −60 | 0.029717 |
| −45 | 0.021436 |
| −30 | 0.023280 |
| −15 | 0.026256 |
| 0 | 0.040841 |
| **+15** | **0.208377** |
| +30 | 0.040846 |
| +45 | 0.025590 |
| +60 | 0.021980 |

roll=+15 相对邻档（±15°）高 **5.10 倍**。glint_flag=0，saturation_flag=1，正确写作 **roll-sharp / saturation-associated high-brightness candidate**，不直接称为 glint 尖峰。

**R4 yaw=147.5 pitch=+12.5 roll profile**：所有 roll 档 ocs 在 0.191–0.202 之间，roll_sensitivity 极低，为 **roll-robust 高亮区**。

加密触发门（4 个均满足）：

| 触发门 | 值 | 阈值 | 触发 |
|--------|-----|------|------|
| top-1 vs top-2 相对差 | 0.224% | < 5% | ✓ |
| top-1 vs R4 top 相对差 | 3.146% | < 5% | ✓ |
| R1 roll 尖峰比 | 5.10× | > 3× | ✓ |
| 未采样 roll（+10/+12.5/+17.5/+20） | True | — | ✓ |

**结论：必须执行局部加密。**

---

## 5. 局部加密执行结果

**Smoke**：roll=+5，3 个姿态，RENDERED=3，FAILED=0 → **PASS**。

**正式矩阵**：R1 top 簇 3×4×7=84 点 + R4 对照 5 点 = 89 点（75 新渲 + 14 复用 P3）。

| roll 批次 | 新渲染 | FAILED |
|-----------|--------|--------|
| +5  | 9（+3 smoke已有）| 0 |
| +10 | 12 | 0 |
| +12.5 | 12 | 0 |
| +15 | 3 | 0 |
| +17.5 | 12 | 0 |
| +20 | 12 | 0 |
| +25 | 12 | 0 |

后处理：COMPLETE=75/75，FAILED=0。

**Refined roll profile（R1 yaw=245.0 pitch=+30.0，加密 roll 档）**：

| roll | ocs_total |
|------|-----------|
| +5 | 0.084741 |
| +10 | 0.164953 |
| +12.5 | 0.197765 |
| **+15** | **0.208377** |
| +17.5 | 0.191569 |
| +20 | 0.157545 |
| +25 | 0.079649 |

峰值确认在 roll=+15，不在 +10 或 +12.5。

**Refined top-1**（全 89 点排名）：

| 排名 | yaw | pitch | roll | ocs_total | source |
|------|-----|-------|------|-----------|--------|
| 1 | 245.0 | **27.5** | +15 | **0.208890** | 23A new |
| 2 | 245.0 | 30.0 | +15 | 0.208377 | P3 reuse |
| 3 | 245.0 | 32.5 | +15 | 0.207910 | P3 reuse |

Refined top-1 从 pitch=30.0 迁移至 **pitch=27.5**，高出 0.246%。

---

## 6. 最终 fixed-geometry top-1 裁决

**Refined top-1**：yaw=245.0，pitch=**27.5**，roll=+15，ocs=0.208890

边界判断：

| 维度 | 结果 | 说明 |
|------|------|------|
| yaw=245.0 | 内部 | 加密矩阵 yaw∈{242.5,245.0,247.5} |
| pitch=27.5 | **下边界** | 加密矩阵 pitch∈{27.5,30.0,32.5,35.0} |
| roll=+15 | 内部 | 加密矩阵 roll∈{+5,...,+25} |

**裁决：pitch=27.5 是 pitch 下边界，且 ocs(27.5) > ocs(30.0)，峰值可能在 pitch < 27.5。**

按 R143 §4.4 规则：**不进入 P4-PHYS-B 光路归因**。

建议下一轮只追加 pitch∈{22.5, 25.0}，roll=+15，yaw=245.0（±242.5, 247.5 可选），约 2~6 个姿态，确认 pitch 方向是否继续上升。

R4（yaw=147.5, pitch=+12.5）最高 single-pose ocs=0.201822，未超过 R1 refined top-1（0.208890），R4 角色维持为 **roll-robust 高亮区机制对照**，不是 single-pose top-1。

---

## 7. 光路归因可行性预检

EXR 实际包含通道（23A 新渲染与 fullrun 一致）：

```text
ViewLayer.Combined.R/G/B/A
ViewLayer.Depth.Z
ViewLayer.IndexOB.X          ← per-object ID（可分解部件贡献）
ViewLayer.Normal.X/Y/Z       ← 法向信息
ViewLayer.Position.X/Y/Z     ← 3D 位置信息
```

字段可用性：

| 字段 | 可用 | 说明 |
|------|------|------|
| ocs_total | ✓ | 来自 *_ocs.json |
| per_part_ocs | ✓ | ocs_per_part（jinshuzhuti/taiyangnengban/yinshenban） |
| object_id | ✓ | IndexOB.X 已在 EXR |
| normal | ✓ | Normal.X/Y/Z 已在 EXR |
| depth | ✓ | Depth.Z 已在 EXR |
| position | ✓ | Position.X/Y/Z 已在 EXR |
| material_id | ✗ | 未单独输出材质 pass |

**P4-PHYS-B 最小诊断姿态集**（确认 pitch 边界后）：top-1 最终姿态 + R4 代表点（yaw=147.5, pitch=+12.5, roll=0）+ R3 负面对照（yaw=55.0, pitch=+60.0, roll=0）= 3 个。

---

## 8. 红线自检

- [x] 未训练任何模型
- [x] 未启动 R128
- [x] 未启动路线二 / 三 / 四
- [x] 未写成果区
- [x] 未改 CLAUDE.md
- [x] 未改 19/20/21/22 号包
- [x] 未生成 Codex 审阅文件
- [x] 未把 fixed sun/view 结果写成所有 sun/view 全局最亮
- [x] 未把 R4 写成并列 top-1（R4 未超过 R1 refined top-1）

---

## 验收状态

gate_matrix: 16/16 PASS（见 `tables/p4physA_gate_matrix.csv`）

**本轮达到最低接收标准，但未达到强接收标准（refined top-1 落在 pitch 下边界）。**

建议 Codex 审阅后下发追加 pitch 边界（22.5, 25.0）一小圈的任务单，确认后进入 P4-PHYS-B。
