# 代码实施前文档审阅报告

生成时间：2026-06-08
审阅人：Claude（执行端）
审阅范围：进入代码全链路重跑前的准备文档
审阅触发：用户要求检查准备文档是否有缺漏或不足

---

## 1. 审阅对象

本报告对代码阶段准备文档做进入实施前的终审。审阅对象：

```text
04_BlenderOCS方法重建/13_v0.4前向模型冻结规范_最终冻结版.md
04_BlenderOCS方法重建/14_v0.4数据与manifest字段规范_最终冻结版.md
05_全链路重跑/00_重跑任务清单.md
05_全链路重跑/01_代码阶段资产盘点与实施计划_Claude.md
05_全链路重跑/02_第一批最小验证任务清单_Claude.md
97_交互审阅记录/03_Codex审阅/05_全链路重跑/R01_Codex_复审_代码阶段准备文档.md
```

对照基准：Codex R01 复审意见中 CR-CODE-001 ~ CR-CODE-005 的整改要求。

---

## 2. 总体判断

**结论：文档准备充分，没有阻塞性缺漏，可以进入代码实施。**

所有准备文档与 13/14 方法冻结规范一致。Codex R01 提出的 2 个 P1 问题、3 个 P2 问题已经全部修正，未发现新的缺漏。

---

## 3. Codex R01 整改项验证

### 3.1 P1 问题（均已修正）

| 编号 | 问题 | 整改要求 | 验证结果 |
|---|---|---|---|
| CR-CODE-001 | 20 姿态 gate 被局部放松 | 删除"< 3 个失败可排除"逻辑，改为任一失败必须修正或降级 | ✅ 已修正。02 文档当前版本明确：任一姿态失败 → 不允许 Level 2 → 修正实现并重测，或整体降级为 Level 1 |
| CR-CODE-002 | I_scale 全局归一化缺少明确代码环节 | 明确 two-pass 流程：先统计 corpus-level I_scale → 统一编码 PNG | ✅ 已修正。01 文档中 `image_response_v0.4.py` 已标注 two-pass 流程；实施顺序中已拆分为 Pass 1（统计 I_scale）→ Pass 2（统一生成 PNG）；明确禁止 per-frame normalization 作为主线 |

### 3.2 P2 问题（均已修正）

| 编号 | 问题 | 整改要求 | 验证结果 |
|---|---|---|---|
| CR-CODE-003 | P1 验证项与硬 gate 文字不统一 | 统一写成"硬 gate"和"辅助诊断"两类 | ✅ 已修正。02 文档 §三 改为"辅助诊断验证任务"，§八 gate 标准与之一致 |
| CR-CODE-004 | "phase63 对应姿态"表述不清 | 改为"在 phase63 sun/det 几何下测试以下典型 yaw/pitch 姿态" | ✅ 已修正。02 文档 §2.2 姿态选取策略已采用修正后的表述 |
| CR-CODE-005 | OCS_level2/level1 差异阈值缺少启发式标注 | 保留 OCS_level2 ≤ OCS_level1 硬约束，>5%/<2% 改为启发式诊断 | ✅ 已修正。02 文档 §2.2 检查内容第 5 项已标注为启发式阈值，不满足时需人工复核而非自动判失败 |

---

## 4. 文档一致性检查

### 4.1 与 13 冻结规范一致性

| 关键点位 | 13 规定 | 准备文档引用 | 一致 |
|---|---|---|---|
| 姿态网格 | 72 yaw × 37 pitch = 2664（不重复 360°） | 00/01/02 均使用 2664 | ✅ |
| OCS 公式 | Σ A_pix·f_r·NoL·V_sun_macro | 00/01 公式一致 | ✅ |
| 图像公式 | I_linear = f_r·NoL·V_sun_macro | 00/01 公式一致 | ✅ |
| 矩阵方向 | world_to_sun_camera = inverse(sun_camera_matrix_world) | 01/02 一致 | ✅ |
| sun_visibility 主线 | Level 2（camera_visible_nol_plus_sun_shadow_pass） | 00 主线一致，有 Level 1 降级预案 | ✅ |
| log1p α 初始值 | 10.0 | 00 §1.2 一致 | ✅ |
| eps | 1e-6 | 00 §1.2 一致 | ✅ |
| BRDF | GGX/Cook-Torrance | 00/01 一致 | ✅ |

### 4.2 与 14 数据规范一致性

| 关键点位 | 14 规定 | 准备文档引用 | 一致 |
|---|---|---|---|
| OCS manifest schema | §3.1 字段（含 sun_visibility/shadow_mapping_method/depth_epsilon_m/record_id） | 01 §2.3.6 一致 | ✅ |
| image manifest schema | §3.2 字段（含 v_sun_macro_mode/v_sun_macro_applied_to_image/I_scale/log1p_alpha） | 01 §2.3.7 一致 | ✅ |
| 一致性检查 | §8.1 六字段断言 | 00 §五 完整列出 | ✅ |
| 禁止 latest-run | §7 | 00/01 均明确 | ✅ |
| source_data.json | 六子版本 | 01 §2.3.8 明确 | ✅ |
| two-pass I_scale | 全局 I_scale | 01 §2.3.5 + §四.5 已实现 | ✅ |

---

## 5. 文档完整性检查

### 5.1 核心方法冻结文件：齐全

- `13_v0.4前向模型冻结规范_最终冻结版.md` — 统一前向模型总图、Blender/Python/反演分工、所有可执行定义（depth、Position、sun shadow reprojection、OCS、image）、sanity check 列表、写作边界
- `14_v0.4数据与manifest字段规范_最终冻结版.md` — 封存原则、manifest schema（OCS/image）、数据集划分、禁止 latest-run、一致性检查、source_data.json 六子版本、输出目录结构

### 5.2 代码阶段准备文档：齐全

- `00_重跑任务清单.md` — 统一口径、冻结参数、禁止旧口径、5 个阶段主线顺序、gate 条件、产物管理、一致性检查清单、写作边界、术语统一
- `01_代码阶段资产盘点与实施计划_Claude.md` — 旧代码三类分类、10 个 v0.4 模块结构、每个模块的 I/O/manifest 字段、8 步实施顺序、gate 条件、风险与不确定性
- `02_第一批最小验证任务清单_Claude.md` — 6 个验证任务详述（深度、实现、输入、检查内容、通过标准、失败处理、产物）、执行顺序与依赖、降级预案、gate 通过标准总结

### 5.3 复审意见留存：齐全

- `R01_Codex_复审_代码阶段准备文档.md` — 复审对象、总体判断、5 个 CR 编号、必须修正内容、可以采纳的内容、进入下一阶段判定、下一步 Claude 提示词

---

## 6. 代码模块设计评审

### 6.1 模块划分评价

10 个模块划分（`00_config` ~ `10_validation`）完整覆盖了从配置、几何、Blender 渲染、BRDF、sun shadow、后处理、manifest、数据集、反演训练到补充实验的全链路。

### 6.2 关键设计点确认

| 设计点 | 状态 |
|---|---|
| 每个模块输入/输出/manifest 字段明确定义 | ✅ |
| 旧代码复用/重写/禁用分类清晰 | ✅ |
| 实施顺序从低成本到高成本（先验证再全量） | ✅ |
| gate 机制分层（P0 硬 gate → P1 辅助 → 可选） | ✅ |
| 降级预案有明确触发条件和后续操作 | ✅ |
| 风险表格覆盖主要不确定性并有缓解措施 | ✅ |

---

## 7. 已知风险与注意事项

以下风险点已有预案，但在实施中需注意：

### 7.1 Blender Position AOV 支持不确定

- **风险等级**：中
- **预案**：depth + camera_matrix 重建方案已写入 13 §7.4.1
- **建议**：Phase 0 优先验证 Position AOV 可用性，不做假设

### 7.2 depth_epsilon_m 校准可能无解

- **风险等级**：低
- **预案**：整体降级为 Level 1，manifest 记录降级原因，论文边界诚实声明
- **建议**：准备好降级后的论文边界声明模板，不等到失败后再临时起草

### 7.3 全量生成时间成本

- **风险等级**：中
- **数量**：2664 姿态 × 5 geom × 多个 pass（camera geometry + sun depth + shadow mask + BRDF linear EXR + log1p PNG）
- **预案**：先完成 single-geom 2664，multi-geom 延后
- **建议**：Phase 0 测量单姿态渲染时间，估算全量耗时

### 7.4 20 姿态验证迭代次数不确定

- **风险等级**：中
- **预案**：失败 → 诊断根因 → 修正 → 重测全部 20 姿态（不允许排除失败姿态后继续 Level 2）
- **建议**：先用 3 个代表姿态（低遮挡/高遮挡/边缘）快速迭代实现，稳定后再跑正式 20 姿态 gate

### 7.5 旧补充实验代码复用度低

- **风险等级**：高（01 文档已标记）
- **预案**：补充实验代码已标记为必须重写，实施顺序放在反演主线之后
- **建议**：在实现 08_inversion 时预留扩展接口，方便后续 09_experiments 复用

---

## 8. 可选的细微补充（不阻塞实施）

以下项目不影响代码启动，但建议在实施推进中逐步完善：

### 8.1 环境依赖文档化

当前文档未集中列出：
- Blender 4.2.3 LTS
- conda env: ocs_sim
- Python 3.12.7 + PyTorch 2.8.0+cu128 (RTX 5060)

**建议**：在 `06_v0.4_code/00_config/` 下新增 `requirements.txt` 或 `environment.yml`

### 8.2 硬件资源估算

当前文档未估算单个 EXR 渲染时间、全量生成总时间和存储空间。

**建议**：Phase 0 快速验证后测量单姿态实际耗时，更新实施计划中的时间估算。

### 8.3 验证失败诊断流程模板

虽然有降级预案，但没有失败时的标准诊断步骤。

**建议**：在 `v0.4_results/00_validation/` 下预先准备 `failure_diagnosis_template.md`

### 8.4 中间产物清理策略

全量生成会产生大量中间文件（EXR、npy、PNG），当前无清理规则。

**建议**：明确哪些是永久保留（manifest、source_data、model_best.pt），哪些可在确认后清理（中间 EXR 可在 manifest 生成后转为归档）。

---

## 9. 建议的实施优先级

按照从低成本验证到高成本全量生成的顺序，建议在当前文档基础上做以下微调：

```text
Phase 0：核心假设快速验证（1-2 天）
├── 验证 Blender Position AOV 是否可用
├── 用 1 个简单姿态 (0°, 0°) 跑通完整最小链路
├── 目视检查结果合理性
└── 测量单姿态渲染时间 → 估算全量耗时

Phase 1：depth round-trip sanity check（2-3 天）
├── 实现 render_camera_geometry.py
├── 实现 depth_round_trip_check.py
└── 3 已知点 camera/sun 双向 round-trip 通过

Phase 2：3 姿态快速迭代（3-4 天）
├── 选 3 个代表姿态：低遮挡 / 高遮挡 / 边缘
├── 实现 sun shadow reprojection
├── 确定 depth_epsilon 大致范围
└── 目视检查 V_sun_macro_mask 合理性

Phase 3：20 姿态正式 gate（2-3 天）
├── 渲染 20 姿态 camera/sun geometry pass
├── 正式校准 depth_epsilon_m_final
├── 完成验证 3/4/5/6 全部辅助诊断
└── gate 通过 → 进入全量生成；失败 → 修正或降级

Phase 4：全量生成（5-10 天）
├── single-geom 2664 全量（Pass 1 I_linear → I_scale → Pass 2 PNG）
├── multi-geom 扩展（2664 × 4）
├── manifest 生成与一致性检查
└── per-part OCS 比例审计 + log1p α ablation

Phase 5：反演训练与补充实验（10-15 天）
├── split 生成 → OCS-only / image-only / fusion 训练
├── 退化鲁棒实验
└── 补充实验 12b/12c/12f/12g
```

---

## 10. 最终结论

```text
文档准备充分 → 无阻塞性缺漏 → 可以进入代码实施
```

**下一步**：搭建 `06_v0.4_code/` 代码骨架，从 Phase 0 快速验证开始。
