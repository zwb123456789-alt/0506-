# Codex 最终短复审意见：v0.4 方法冻结通过

最后更新：2026-06-08

复审对象：

```text
04_BlenderOCS方法重建/13_v0.4前向模型冻结规范_最终冻结版.md
04_BlenderOCS方法重建/14_v0.4数据与manifest字段规范_最终冻结版.md
```

## 1. 总体判断

通过。`13/14` 已经可以作为 v0.4 方法冻结依据，进入代码阶段。

本轮 CR5 关键问题已关闭：

- `13` 已新增独立章节，明确论证为什么 v0.4 选择完整统一前向模型，而不是只替换 OCS 采样。
- `14` 已新增独立章节，说明为什么完整统一模型需要严格 manifest/source_data，而不是只记录一个 OCS CSV。
- sun shadow reprojection 的矩阵方向已修正为：
  - `camera_matrix_world`: camera local -> world
  - `world_to_camera_matrix = inverse(camera_matrix_world)`
  - `sun_camera_matrix_world`: sun camera local -> world
  - `world_to_sun_camera_matrix = inverse(sun_camera_matrix_world)`
- 未验证的 depth 编码公式已移除，改为要求 depth round-trip sanity check。
- image manifest 中 `v_sun_macro_applied` 的模糊语义已改为 `v_sun_macro_mode` + `v_sun_macro_applied_to_image`。
- `visibility_level` 字段名残留已改为 `sun_visibility`。
- `depth_epsilon_m` 已改为校准后最终值，初始值只作为验证候选。

## 2. 仍需在代码阶段验证的风险

以下不是方法冻结阻塞项，但必须在代码阶段第一批验证：

| 风险 | 代码阶段处置 |
|---|---|
| Blender Depth pass 的符号、单位、local z 方向 | 先做 3 个已知点 round-trip sanity check |
| Position/WorldCoord AOV 是否可直接输出 | 先试 Position AOV；不可行则用 depth + camera matrix 重建 |
| sun-view depth reprojection 是否与 camera-view mask 对齐 | 先跑 20 姿态 shadow validation，不直接全量 |
| `depth_epsilon_m_final` 取值 | 由 20 姿态验证校准后写入 manifest |
| `05_全链路重跑/00_重跑任务清单.md` 仍含旧口径 | 代码阶段第一步应更新任务清单，统一到 `13/14` 的最终冻结口径 |

## 3. 是否进入代码阶段

可以进入代码阶段，但不要直接全量重跑。

下一步应让 Claude 做 **代码阶段资产盘点与实施计划**：

1. 根据 `13/14` 更新 `05_全链路重跑/00_重跑任务清单.md`。
2. 盘点 V0.4 备份中的旧代码资产，判断哪些可复用、哪些必须重写。
3. 制定第一批最小可验证代码任务：depth round-trip、Position/WorldCoord、sun shadow reprojection、20 姿态验证。
4. 暂不全量生成 2664 × 5 数据，也不训练模型。

---

## 附录：下一步 Claude 提示词

你现在位于：

```text
项目重启_v0.4_BlenderOCS/
```

请先阅读本文件：

```text
04_BlenderOCS方法重建/15_Codex最终短复审意见_方法冻结通过.md
```

本次任务进入代码阶段，但第一步只做 **代码资产盘点、任务清单更新、实施计划**。不要写正式代码，不要全量重跑实验，不要修改外部旧目录。

### 必读文件

```text
CLAUDE.md
00_只打开本文件夹时的启动说明.md
00_v0.4总控流程.md
04_BlenderOCS方法重建/13_v0.4前向模型冻结规范_最终冻结版.md
04_BlenderOCS方法重建/14_v0.4数据与manifest字段规范_最终冻结版.md
04_BlenderOCS方法重建/15_Codex最终短复审意见_方法冻结通过.md
05_全链路重跑/00_重跑任务清单.md
98_外部材料备份/00_备份清单.md
98_外部材料备份/03_关键代码快照/01_code/materials.py
98_外部材料备份/03_关键代码快照/02_blender/brdf_postprocess.py
```

按需读取代码快照目录，不要一次性全文读取所有旧代码：

```text
98_外部材料备份/03_关键代码快照/
```

### 本次必须完成

1. 更新或重写：

```text
05_全链路重跑/00_重跑任务清单.md
```

要求：

- 删除或修正旧口径，例如 yaw73、`multi_geom_blender_ocs_yaw73_pitch37`、局部替换 OCS 的表述。
- 改为最终冻结口径：72 yaw × 37 pitch = 2664 姿态，绘图 seam 才复制 360°。
- 写清 v0.4 主线顺序：
  1. 代码资产盘点
  2. depth round-trip sanity check
  3. camera-view geometry pass / Position pass
  4. sun-view depth pass
  5. sun shadow reprojection 生成 `V_sun_macro_mask`
  6. 20 姿态 shadow validation 与 `depth_epsilon_m_final` 校准
  7. BRDF/OCS/image 后处理
  8. manifest 生成与一致性检查
  9. single-geom 主线数据集
  10. multi-geom 扩展数据集
  11. OCS-only / image-only / fusion 训练
  12. 退化与补充实验

2. 新建：

```text
05_全链路重跑/01_代码阶段资产盘点与实施计划_Claude.md
```

必须包含：

- 可复用代码资产清单：哪些旧代码可以参考，哪些不能直接复用。
- 必须新写或重构的模块清单。
- 代码阶段建议目录结构，建议放在 V0.4 内部，不写外部旧目录。
- 每个模块的输入、输出、manifest 字段。
- 第一批最小验证任务，不全量重跑。
- 进入正式全量重跑前的 gate 条件。

3. 新建：

```text
05_全链路重跑/02_第一批最小验证任务清单_Claude.md
```

必须包含：

- 3 个已知点 depth round-trip sanity check。
- 3 个姿态 camera geometry pass 检查。
- 3 个姿态 Position/WorldCoord 检查。
- 3 个姿态 sun-view depth pass 检查。
- 5 个姿态 V_sun_macro 对图像影响检查。
- 20 个代表姿态 sun shadow validation。
- 每个验证任务的通过标准、失败处理、输出文件位置。

### 严格限制

- 不要写正式代码。
- 不要启动全量渲染。
- 不要训练模型。
- 不要修改外部旧目录。
- 不要复用旧结果作为 v0.4 主结果。
- 不要把 `13/14` 已冻结的物理定义再改成未冻结状态。

完成后只总结：更新了哪些文件、新建了哪些文件、代码阶段第一步是否仍有需要 Codex 审阅的风险点。
