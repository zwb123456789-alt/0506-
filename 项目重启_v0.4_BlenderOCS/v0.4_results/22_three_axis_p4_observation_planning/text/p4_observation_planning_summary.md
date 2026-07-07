# P4 Observation Planning Summary

最后更新：2026-07-06  
来源：R137 P4 observation planning synthesis  
结果包：`v0.4_results/22_three_axis_p4_observation_planning/`

---

## 一句话结论

在 phase63 / L1-G1 model-known 仿真条件下，三轴姿态空间的观测规划可分为四类角色：
**高信息-roll敏感区（R1，首选）、亮-信息折中区（R4边界，推荐）、低信息负面对照区（R3）、dark/neutral 参照区（R2/R5，降权）**。
最亮姿态（yaw147.5/+12.5，brightness_rank=1/107）的 info_rank=104/107，不可作为最优观测目标。

---

## 核心观测规划建议

### 1. 高信息-roll敏感区（R1）— 首选观测目标

| 候选 | yaw | pitch | roll_sens | info_rank | p4_utility |
|------|-----|-------|-----------|-----------|-----------|
| C01  | 247.5 | +37.5 | 3.804 | 7/107 | 0.462 |
| C02  | 247.5 | +40.0 | 3.803 | 8/107 | 0.460 |
| C07  | 245.0 | +35.0 | 3.853 | 24/107 | 0.440 |
| C08  | 245.0 | +32.5 | 3.855 | 26/107 | 0.435 |

**适用场景：** roll-aware 观测设计；joint 信息互补性测试；R128 接口候选  
**注意：** 全区 glint+saturation 风险高；模拟下可用，真实仪器需额外评估

### 2. 亮-信息折中区（R4 边界）— 综合最优

| 候选 | yaw | pitch | info_rank | brightness_rank | glint/sat | p4_utility |
|------|-----|-------|-----------|-----------------|-----------|-----------|
| C09  | 155.0 | +20.0 | 1/107 | 31/107 | 无 | 0.427 |
| C10  | 152.5 | +20.0 | 11/107 | 24/107 | 无 | 0.415 |

**C09 是综合最优候选：** 信息 proxy 最高、亮度中等、无 glint/saturation 风险  
**注意：** "最高信息"仍为 proxy 级指标；不等同于模型级可分性

### 3. 最亮构型（R4 核心）— 仅作参考上限

| 姿态 | brightness_rank | info_rank | 风险 | 规划建议 |
|------|-----------------|-----------|------|---------|
| yaw147.5/+12.5 | 1/107（最亮） | 104/107（极低信息） | VERY HIGH（sat+glint） | 不作主规划落点；仅亮度基准参考 |

### 4. 低信息负面对照区（R3）

| 候选 | yaw | pitch | info_rank | connectivity | 用途 |
|------|-----|-------|-----------|--------------|------|
| C11  | 57.5 | +62.5 | 39/107 | 0.60 | 负面对照 |
| C12  | 55.0 | +60.0 | 48/107 | 0.60 | 负面对照 |

**适用场景：** 验证观测规划有效性；退化测试负面基准

### 5. Dark/Neutral 对照（R2/R5，降权）

- C13-C14（R2，yaw280-285/pitch-85）：dark 极值参照
- C15-C16（R5，yaw210/pitch-5~-10）：neutral 背景参照
- utility ≤ 0.001；不作任何正向观测推荐

---

## brightness ≠ information：P4 综合确认

| 姿态 | brightness_rank | info_rank | 含义 |
|------|-----------------|-----------|------|
| yaw147.5/+12.5 | 1/107（最亮） | 104/107（极低） | 最亮点信息最差 |
| yaw155/+20 | 31/107（中等） | 1/107（最高proxy） | 信息最高点亮度中等 |

该边界在 P1（smoke）→P2（5°网格）→P3（2.5°加密）三级验证中始终成立，加密后更尖锐。

---

## 图表索引

| 图名 | 内容 | 文件 |
|------|------|------|
| p4_observation_role_map | 候选姿态角色分布图（yaw/pitch，按角色着色） | figures/p4_observation_role_map.png |
| p4_brightness_information_decoupling_summary | brightness vs information rank 散点 | figures/p4_brightness_information_decoupling_summary.png |
| p4_planning_candidate_panel | 4角色候选 Panel（2×2子图） | figures/p4_planning_candidate_panel.png |
| p4_stage_evidence_flow | P1→P2→P3→P4 阶段门证据流图 | figures/p4_stage_evidence_flow.png |

---

## 指标与边界说明

所有分析使用以下 proxy 级指标：

- **OCS brightness（ocs_mean/ocs_roll0）：** 模型已知条件下亮度量化
- **neighbor_contrast_ypr：** 局部三轴邻域 OCS 变化幅度；proxy 级局部信息指标
- **roll_sensitivity_score：** OCS 随 roll 变化的相对幅度；proxy 级 roll 敏感性
- **region_utility_score：** 0.4×norm_info + 0.3×norm_rollsens + 0.3×norm_brightness − 0.2×risk_frac

**不可升格为：** P-DB / margin / entropy / conformal set_size / 模型级反演可分性

---

*本摘要为 P4 观测规划综合的可解释文本材料。供 Codex 005 审阅裁决三轴小项目是否阶段性收口。*
