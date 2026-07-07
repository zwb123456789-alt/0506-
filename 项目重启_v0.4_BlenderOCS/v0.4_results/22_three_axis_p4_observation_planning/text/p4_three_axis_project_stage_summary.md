# 三轴小项目阶段性收口候选材料（P4 synthesis）

最后更新：2026-07-06  
来源：R137 P4 observation planning synthesis  
结果包：`v0.4_results/22_three_axis_p4_observation_planning/`  
上游：R136 接收 P3，放行 P4

---

## 1. 项目定位与边界

三轴小项目的目标是：

> 在 yaw / pitch / roll 三轴姿态空间中，寻找最亮构型、高信息姿态、低信息区域和观测规划建议，把路线一 C 的 fixed-roll 可观测性证据扩展为 roll-aware 的观测规划工具。

**核心边界（贯穿全程）：**

- model-known simulated 条件；phase63 / L1-G1 几何；不外推到真实未知目标
- 最亮姿态 ≠ 最高信息姿态（brightness ≠ information）
- neighbor_contrast_ypr 等指标为 proxy 级，不等同于模型级可分性
- 本项目不提供真实未知目标三轴姿态反演成功率

---

## 2. 各阶段成果链

### S0 准备（18号包，R130接收）

- 定义 11 个三轴指标；66 个固定 roll 种子候选；P1-P4 阶段矩阵

### P1 seed-roll smoke（19号包，R132接收）

- 12 seed × 8 非零 roll = 96 渲染单位（smoke级）
- **核心观察（smoke级）：**
  - bright-seed（yaw145/150,pitch+15）roll_sensitivity≈0.05-0.07，亮度漂移≤1；但 local_contrast 末位，有 saturation 风险
  - high-info yaw240 系 roll_sensitivity≈3.2-3.6；暗但 roll 敏感
  - brightness ≠ information 在 smoke 层面已分离

### P2 sparse 3-axis grid（20号包，R134接收）

- 5 区域 × 125 pose × 9 roll；1000 新渲染
- **核心观察（区域级 proxy）：**
  - R4_bright_robust：utility=0.251，mean_roll_sens=0.088，最亮+roll稳健
  - R1_high_info：utility=0.234，mean_roll_sens=2.661，高信息+roll敏感
  - R3_low_info：utility=0.063，低信息连通
  - R2/R5：utility≤0，对照级
  - P2 brightness rank=1（yaw150/+15）vs info rank=60；info rank=1（yaw155/+20）vs brightness rank=13

### P3 local refinement（21号包，R136接收）

- 107 pose × 9 roll = 963 单位；921 新渲染（2.5度加密）
- **P3 五问结论（稳定）：**
  - R4 最亮点迁移：yaw150/+15 → yaw147.5/+12.5（3.54度），亮度rank=1但info_rank=104/107
  - R4 高信息边界稳定：yaw155/+20，info_rank=1/nc=1.198/brightness_rank=31
  - R1 roll-sensitive peak 完全稳定（迁移0.0度）：yaw245-247.5/pitch+30~40，roll_sens≈3.69-3.85
  - R3 低信息连通性=0.60，stability=0.92，适合负面对照
  - R2/R5 降权；P4应不以其为主规划落点

---

## 3. P4 观测规划建议综合

### 3.1 高信息-roll敏感区（R1，首选）

- **候选姿态：** C01-C08，yaw245-247.5 × pitch+30~40
- **核心数值（P3 2.5度加密）：** roll_sensitivity_score = 3.69-3.85；info_rank = 7-26/107
- **p4_planning_utility_score：** 0.435-0.462（最高）
- **适用场景：** 最优信息观测设计；roll-aware 观测设计候选；R128 joint 互补性测试候选
- **注意：** 全区 glint=1，多点 saturation=1；模拟下 image_usable=1，真实仪器需额外评估

### 3.2 亮-信息折中区（R4 边界点，推荐）

- **候选姿态：** C09（yaw155/+20，首选）+ C10（yaw152.5/+20，备选）
- **核心数值：** C09: info_rank=1/brightness_rank=31/nc=1.198/无glint/saturation
- **p4_planning_utility_score：** C09=0.427，C10=0.415
- **适用场景：** 综合最优观测候选（亮度可接受+信息最高+无成像风险）
- **注意：** 最亮点（yaw147.5/+12.5）≠ 本区最优；不可替代

### 3.3 最亮构型（R4 核心，仅作参考上限）

- **核心姿态：** yaw147.5/+12.5（brightness_rank=1/107）
- **info_rank=104/107（几乎最低信息）**；saturation+glint风险极高
- **规划作用：** 仅作亮度基准上限参考；不纳入 P4 主规划落点；适合暗室 saturation 测试

### 3.4 低信息负面对照区（R3，必要对照）

- **候选姿态：** C11（yaw57.5/+62.5）+ C12（yaw55/+60）
- **核心数值：** low_info_connectivity=0.60；nc 全区最低（0.814-0.901）
- **适用场景：** 验证观测规划有效性的负面对照；真实图像退化测试负面基准
- **注意：** 低信息≠无可观测性；仅作规划对比用途

### 3.5 dark/neutral 对照（R2/R5，降权）

- **候选姿态：** C13-C16（R2 yaw280-285/pitch-85；R5 yaw210/pitch-5~-10）
- **utility≤0.001；** 不作任何正向观测推荐；仅作极值参照

---

## 4. 核心物理结论（proxy级，model-known）

1. **brightness ≠ information** 是三轴空间中稳健的规划边界：在 2.5 度精细分辨率下，R4 最亮点与信息峰分处区域不同角落（yaw/pitch 各差 7.5 度），二者不重合。
2. **高信息区必然伴随 roll 敏感性：** R1 区 roll 敏感性（proxy）最高，同时具有最高局部信息 proxy；暗示 roll 对姿态可观测性有贡献。
3. **最亮构型 roll 稳健但信息价值低：** R4 核心最亮点 roll 稳健（roll_sens≈0.09），但局部信息 proxy 最低，伴随 saturation 风险。
4. **观测规划分层可行：** 5 类区域（高信息/亮折中/最亮caution/低信息对照/暗中性对照）在三轴姿态空间中结构清晰，可支撑差异化观测策略。

以上结论均受限于：proxy 级指标、model-known 条件、phase63 单几何、当前 2.5 度分辨率。

---

## 5. 阶段性收口判据评估

**最低接收标准（自评）：**

| 标准 | 状态 |
|------|------|
| 22号包目录存在 | ✓ |
| 无新增渲染/训练/后处理 | ✓ |
| 角色分层/优先级矩阵/风险边界矩阵完成 | ✓ |
| stage summary/claim boundary/must-not-claim 完成 | ✓ |
| R128接口候选只列清单不启动 | ✓ |
| manifest/路径一致性/红线自检完成 | ✓（E节完成后） |
| 未写成果区/未改CLAUDE.md/未生成Codex审阅文件 | ✓ |

**强接收标准（自评）：**

| 标准 | 状态 |
|------|------|
| P4能支撑Codex裁决三轴小项目是否阶段性收口 | ✓（本文件+p4_stage_claim_boundary_table.csv） |
| P4给出论文Results/SI/Discussion候选资产清单 | ✓（p4_results_si_candidate_assets.csv，E节） |
| P4明确下一步（R128/论文准备/补充诊断） | ✓（见下节） |

---

## 6. 下一步建议

三轴小项目 P4 综合完成后，建议 Codex 裁决以下问题：

1. **阶段性收口确认：** P1/P2/P3/P4 证据链是否足以支撑三轴小项目作为路线一 C 的 roll-aware 补充扩展进入论文候选材料。
2. **R128 回看时机：** 若三轴小项目收口，决定是否回看 R128（新路线二真实观测难度/图像退化/joint互补性）。
3. **论文候选接口：** P4 的候选资产（C09高信息折中/C01-C08高信息roll敏感集/C11-C12负面对照）是否直接进入 Results/SI/Discussion 候选。

*本文件为阶段性收口候选材料，最终收口需 Codex 005 审阅裁决。*
