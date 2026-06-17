# Codex 复审意见：代码阶段准备文档

生成时间：2026-06-08

## 1. 复审对象

本次复审对象为方法冻结通过后进入代码阶段的三份准备文档：

```text
05_全链路重跑/00_重跑任务清单.md
05_全链路重跑/01_代码阶段资产盘点与实施计划_Claude.md
05_全链路重跑/02_第一批最小验证任务清单_Claude.md
```

对照基准：

```text
04_BlenderOCS方法重建/13_v0.4前向模型冻结规范_最终冻结版.md
04_BlenderOCS方法重建/14_v0.4数据与manifest字段规范_最终冻结版.md
```

重点检查项：

1. 是否与 13/14 冻结规范一致：72 yaw、OCS/image 同源公式、sun shadow reprojection 矩阵方向、manifest schema。
2. gate 机制是否合理：depth round-trip + 20 姿态验证后再全量生成。
3. 代码模块划分是否遗漏关键环节。
4. 第一批验证任务是否覆盖主要风险。
5. 降级预案是否明确。

## 2. 总体判断

**需小修。**

未发现 P0 问题。三份文档整体已经能够承接方法冻结后的代码阶段，且主线方向与 13/14 一致。但存在 2 个 P1 级文档口径问题：一个会放松 Level 2 shadow gate，另一个会让图像归一化实现存在 per-frame/per-corpus 混用风险。

修正这 2 个 P1 后，Claude 可以进入代码实施。

## 3. 主要问题 / Codex CR 编号

### CR-CODE-001（P1）：20 姿态 gate 被局部放松，和冻结规范冲突

问题位置：

```text
05_全链路重跑/02_第一批最小验证任务清单_Claude.md
§六 失败场景与降级预案
```

当前写法中包含：

```text
20 姿态中 < 3 个失败 | 排除失败姿态，用其余姿态校准 depth_epsilon | manifest 记录排除姿态列表
20 姿态中 >= 3 个失败 | 降级为 Level 1
```

这与 13 冻结规范冲突。13 §12.6 的口径是：

```text
如果任一验证失败，根据失败模式降级为 camera_visible_nol，并记录降级原因。
```

复审判断：

- 20 姿态验证是 Level 2 sun shadow reprojection 进入全量生成的 gate。
- 失败姿态可以保留为诊断样本，但不能从 gate 中剔除后继续宣称 Level 2 全量通过。
- 若允许 `<3 个失败仍继续 Level 2`，后续 manifest 会记录 `sun_visibility = camera_visible_nol_plus_sun_shadow_pass`，但验证事实上不是全姿态通过，会削弱方法冻结中 gate 的约束力。

必须整改：

1. 删除“排除失败姿态，用其余姿态校准 depth_epsilon”的通过逻辑。
2. 改为：任一姿态失败时，不允许以 Level 2 进入全量生成；必须修正实现并重测，或整体降级为 Level 1。
3. 若失败姿态用于诊断，可写入 validation report 的失败记录，但不能作为 manifest 中继续 Level 2 的排除列表。

### CR-CODE-002（P1）：图像 I_scale 全局归一化缺少明确代码环节

问题位置：

```text
05_全链路重跑/01_代码阶段资产盘点与实施计划_Claude.md
§2.3.5 image_response_v0.4.py
§四 实施顺序建议
```

13 §8.2 与 §15 明确要求：

```text
I_scale = v0.4 clean corpus 全局最大 I_linear 值
```

14 §3.2 也要求 image manifest 记录：

```text
preprocessing.I_scale = global max I_linear of clean corpus
```

当前 01 文档把 `linear.exr` 与 `log1p 8-bit PNG` 放在同一步输出，虽然文字中提到 `I_scale 全局最大`，但没有把“先统计全局 I_scale，再统一编码 PNG”拆成可执行模块或步骤。实际实施时容易出现以下错误：

- 每帧单独归一化，破坏图像之间的绝对亮度可比性。
- 先输出 PNG 后才统计全局最大值，导致 PNG 与 manifest 的 `I_scale` 不一致。
- quick ablation 的 α 候选建立在不稳定归一化上。

必须整改：

1. 在 `05_postprocess/` 或 `06_manifest/` 中明确新增一个 clean corpus intensity 统计步骤，例如 `compute_clean_corpus_iscale.py` 或在 `image_response_v0.4.py` 中分为 two-pass。
2. 实施顺序改为：

```text
先生成全部 clean I_linear EXR / 或 dry-run 统计 I_linear 最大值
-> 计算并冻结 corpus-level I_scale
-> 用同一个 I_scale 统一生成 log1p PNG
-> image manifest 写入 preprocessing.I_scale
-> 再做 log1p alpha quick ablation
```

3. 明确禁止 per-frame normalization 作为主线训练输入；如保留 `I_scale_record`，只能作为审计字段或可选对照，不得覆盖全局 `I_scale` 主线。

### CR-CODE-003（P2）：P1 验证项与硬 gate 文字不够统一

问题位置：

```text
05_全链路重跑/02_第一批最小验证任务清单_Claude.md
§三 P1 验证任务（建议完成）
§八 gate 通过标准总结
```

当前 §三称 camera geometry、Position、sun depth、V_sun_macro 对图像影响为“P1/建议完成”，但 §八又写“必须全部满足才能进入全量生成”。这不会改变技术路线，但会让实施者误以为某些 gate 可以跳过。

建议整改：

- 将验证任务分为“硬 gate”和“辅助诊断”两类。
- 对进入全量生成必须完成的项目，统一写成“硬 gate”，不要再写“建议完成”。
- 若某项确实只是辅助诊断，应从 §八“必须全部满足”中移除。

### CR-CODE-004（P2）：20 姿态表中的“phase63 对应姿态”表述不清

问题位置：

```text
05_全链路重跑/02_第一批最小验证任务清单_Claude.md
§2.2 20 姿态选取策略
```

`phase63` 是 single-geom 的 sun/det 几何配置，不是 yaw/pitch 姿态本身。当前“phase63 对应姿态（yaw/pitch 取 phase63 几何）”容易让后续 Claude 混淆观测几何与目标姿态。

建议整改：

- 直接列出 20 个具体 `(yaw, pitch)`。
- 若要强调主线几何，应写成“在 phase63 sun/det 几何下测试以下典型 yaw/pitch 姿态”。

### CR-CODE-005（P2）：OCS_level2 与 OCS_level1 差异阈值宜标为启发式诊断

问题位置：

```text
05_全链路重跑/02_第一批最小验证任务清单_Claude.md
§2.2 检查内容，第 5 项
```

当前写法给出：

```text
高遮挡姿态下应 > 5%，低遮挡姿态下应 < 2%
```

这个阈值可作为 sanity check，但如果没有人工标注、raycast 参考或更明确的几何真值，不宜作为硬 gate 的绝对失败条件。

建议整改：

- 保留 `OCS_level2 <= OCS_level1` 作为硬约束。
- 将 `>5%`、`<2%` 写成启发式诊断阈值；若不满足，需要人工复核 mask 与几何直觉，而不是自动判失败。

## 4. 可以采纳的内容

以下内容与 13/14 冻结规范一致，可以保留：

1. 姿态网格已改为 72 yaw × 37 pitch = 2664，不重复 360°；heatmap seam 才复制 360°。
2. OCS 与图像公式均使用同源 `f_r`、`NoL`、`V_sun_macro`：

```text
OCS = Σ A_pix·f_r·NoL·V_sun_macro
I_linear = f_r·NoL·V_sun_macro
```

3. sun shadow reprojection 的矩阵方向使用：

```text
world_to_sun_camera = inverse(sun_camera_matrix_world)
P_sun_local = world_to_sun_camera @ P_world
```

4. manifest 字段与 14 对齐，包含 `sun_visibility`、`shadow_mapping_method`、`depth_epsilon_m`、`record_id`、camera/sun 矩阵、shadow mask 路径、image 侧 `v_sun_macro_mode`。
5. 禁止 latest-run 自动发现，要求显式传入 manifest/split/output 路径。
6. 代码模块划分总体完整，覆盖：

```text
config / geometry / blender pass / BRDF / sun shadow / OCS integration /
image response / manifest / dataset split / inversion / experiments / validation
```

7. gate 的总体方向正确：先 depth round-trip，再 20 姿态 shadow validation，之后才进入全量生成。
8. 降级预案方向正确：Level 2 不可行时整体降级为 `camera_visible_nol`，并在 manifest 与论文边界中诚实声明。

## 5. 必须修正内容

必须修正以下两项后再进入代码实施：

1. 修正 `02_第一批最小验证任务清单_Claude.md` 中 20 姿态失败处理逻辑：

```text
任一姿态失败 -> 不允许以 Level 2 进入全量生成
处理方式 -> 修正实现并重测，或整体降级 Level 1
失败姿态 -> 只作为诊断记录，不作为排除后继续通过的依据
```

2. 修正 `01_代码阶段资产盘点与实施计划_Claude.md` 中 image response / I_scale 实施流程：

```text
clean I_linear corpus 生成或统计
-> corpus-level I_scale 计算并冻结
-> 统一 log1p PNG 编码
-> image manifest 写入同一个 I_scale
-> α quick ablation
```

## 6. 是否可以进入下一阶段

当前不建议直接进入代码实施。

结论为：

```text
需小修 -> 修正 CR-CODE-001 与 CR-CODE-002 -> 可进入代码实施
```

CR-CODE-003 至 CR-CODE-005 为 P2，可与上述小修一并处理。若时间紧，至少完成 P1 两项后即可启动代码骨架搭建，但建议一次性修完，避免后续实施时反复解释 gate 语义。

## 7. 下一步 Claude 提示词

```text
你是本项目的 Claude 执行端。请只对 v0.4 当前文件夹内的代码阶段准备文档做小修，不要修改外部旧目录，不要启动全量渲染，不要训练模型。

项目根目录：
D:\我的文件\研究生学术\光学项目\0506新\项目重启_v0.4_BlenderOCS

请先读取：
1. CLAUDE.md
2. 00_只打开本文件夹时的启动说明.md
3. 00_v0.4总控流程.md
4. 04_BlenderOCS方法重建/13_v0.4前向模型冻结规范_最终冻结版.md
5. 04_BlenderOCS方法重建/14_v0.4数据与manifest字段规范_最终冻结版.md
6. 05_全链路重跑/00_重跑任务清单.md
7. 05_全链路重跑/01_代码阶段资产盘点与实施计划_Claude.md
8. 05_全链路重跑/02_第一批最小验证任务清单_Claude.md
9. 97_交互审阅记录/03_Codex审阅/05_全链路重跑/R01_Codex_复审_代码阶段准备文档.md

本次只做以下整改：

一、修正 20 姿态 shadow validation 的 gate 口径
- 在 05_全链路重跑/02_第一批最小验证任务清单_Claude.md 中删除或改写“20 姿态中 < 3 个失败可排除失败姿态继续校准”的逻辑。
- 改为：任一姿态验证失败时，不允许以 Level 2 进入全量生成；必须修正实现并重测，或整体降级为 Level 1 camera_visible_nol。
- 失败姿态可以记录在 validation report 中作为诊断证据，但不能作为 manifest 中排除后继续通过的依据。

二、补充 I_scale 全局归一化的两阶段实现流程
- 在 05_全链路重跑/01_代码阶段资产盘点与实施计划_Claude.md 中明确 image_response_v0.4.py 或新增统计模块的 two-pass 流程：
  1. 先生成或 dry-run 统计全部 clean I_linear；
  2. 计算并冻结 corpus-level I_scale；
  3. 使用同一个 I_scale 统一生成 log1p PNG；
  4. image manifest 写入 preprocessing.I_scale；
  5. 再做 log1p alpha quick ablation。
- 明确禁止 per-frame normalization 作为主线训练输入。若保留 I_scale_record，只作为审计或可选对照字段。

三、顺手修正 P2 文字一致性
- 将“P1 验证任务（建议完成）”与“必须全部满足才能进入全量生成”的表述统一，建议改为“硬 gate 验证任务”和“辅助诊断任务”。
- 将“phase63 对应姿态（yaw/pitch 取 phase63 几何）”改为“在 phase63 sun/det 几何下测试以下典型 yaw/pitch 姿态”，并尽量列出 20 个具体 yaw/pitch。
- 将 OCS_level2 与 OCS_level1 的 >5% / <2% 差异阈值标为启发式诊断，不作为无参考真值时的自动硬失败条件；保留 OCS_level2 <= OCS_level1 作为硬约束。

输出要求：
- 直接修改上述 01/02 两份文档；如 00_重跑任务清单中有同样 gate 口径残留，也同步小修。
- 不新增代码，不生成结果，不修改 13/14 冻结规范。
- 修完后给出修改摘要，并说明是否已满足“可进入代码实施”。
```
