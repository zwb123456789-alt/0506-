# Codex 复审意见：v0.4 前向模型冻结规范修订版

最后更新：2026-06-08

复审对象：

```text
04_BlenderOCS方法重建/07_v0.4前向模型冻结规范_Claude修订版.md
04_BlenderOCS方法重建/08_v0.4数据与manifest字段规范_Claude修订版.md
```

## 1. 总体判断

这轮修订已经把上一轮 CR3 的主要硬问题基本收回：

- GGX 材料参数已改回 `_GGX_DB`。
- yaw 网格已改为训练/manifest 72 个唯一 yaw，绘图 seam 可复制 360°。
- `sun_visibility` enum 已从易误解的 `camera_only` 改为 `camera_visible_nol` 等三层命名。
- OCS 公式已加入 `V_sun_macro`。
- 版本字段已拆成 geometry / BRDF / visibility / OCS integration / image preprocess / dataset。
- 旧结果全封存、新结果重跑、禁止 latest-run 自动发现等原则已经写入。

但两份修订版还不能直接作为最终冻结规范进入代码阶段。现在剩下的问题更具体：不是“大方向不对”，而是 **统一前向模型一旦进入实现，会在 sun shadow pass、图像生成链和 manifest 字段上再次分叉**。

结论：可以进入最后一轮“最终冻结候选”小修；暂时不要进入代码阶段。

## 2. 为什么必须按“更完整的统一前向物理模型”推进

本轮 CR4 看起来比“只替换采样模型”多了很多要求，原因是 v0.4 的目标已经不是局部修补旧 OCS CSV，而是建立一个能支撑 OCS-only、image-only、fusion 和退化实验解释的统一 synthetic forward model。

如果只做最小替换：

```text
旧 OCS face-center sampling → Blender pixel-level OCS
```

工程上可以跑通，但论文和实验解释会留下硬伤：图像是否仍沿用旧响应链、sun-side visibility 是否只进入 OCS、fusion 是否混合两套前向定义、退化实验的 clean image 是否与 OCS 同源，都无法稳固回答。

因此，当前选择更完整模型有以下立论基础：

| 角度 | 论证 |
|---|---|
| 现实观测贴近性 | 真实光学观测是对可见投影表面成像，而不是对三角面中心采样。Blender pixel-level geometry pass 更接近 projected image formation。 |
| 物理一致性 | 同一表面点的 BRDF、`NoL`、camera visibility 和 sun-side macro visibility 应同时决定 OCS 积分和图像亮度。 |
| 反演准确性 | v0.4 不预设误差一定下降；它追求的是纠正观测定义后得到更可信的反演证据。若误差下降，可解释为 corrected OCS signature 更稳定；若不下降，也代表更严格物理定义下的结果。 |
| 模态公平性 | OCS 与 image 的比较应来自同一前向模型下的不同读出方式：OCS 是积分读出，image 是空间分布读出。 |
| fusion 可解释性 | fusion 提升应来自低维光度约束与空间图像结构互补，而不是来自两套仿真链路误差混合。 |
| 退化实验可信度 | noise/blur/downsample/background/starfield 应作用在同源 clean image 上，OCS 作为同源低维观测保持不变。 |
| 论文防守性 | 可以写成 observation-consistent synthetic forward model，而不是“模块 A/B 分别生成两个模态”。 |
| 工程可追踪性 | manifest 记录 geometry、BRDF、visibility、OCS integration、image preprocess 和 dataset 版本，避免 latest-run 和旧结果混用。 |

所以 CR4-001 到 CR4-008 的目的不是扩大项目，而是保证“更贴近现实、反演证据更可信、统一前向模型”这三句话立得住脚。

## 3. 主要问题

| 编号 | 严重度 | 对应位置 | 问题 | Codex 判断 | 修正要求 |
|---|---|---|---|---|---|
| CR4-001 | P0 | `07` §1、§2.2、§7.2 | OCS 已写成 `Σ A_pix·f_r·NoL·V_sun_macro`，但图像线性响应仍写成 `I_linear = f_r·NoL`，没有乘 `V_sun_macro`。 | 这会破坏“OCS 和图像来自同一统一前向物理模型”。如果 OCS 使用 sun-side self-shadow，而图像不使用，fusion 会再次混用两个物理定义。 | 图像线性响应必须改成 `I_linear(p)=f_r(p)·NoL(p)·V_sun_macro(p)`。若降级为 `camera_visible_nol`，则 `V_sun_macro≡1`，自然退化回 `f_r·NoL`。所有图、公式、EXR/PNG 说明、退化实验链都要同步。 |
| CR4-002 | P0 | `07` §2.1、§4.1、§6.3 | `sun shadow pass` 写成“额外 sun-view 渲染，输出 per-pixel sun-ray visibility flag”，后面又写“读取 sun-view EXR → `V_sun_macro`”。但 sun-view 像素网格与 camera-view 像素网格不是同一个网格，不能直接当作 camera-view 每像素遮挡 mask。 | 这是代码阶段最大风险点。要得到 camera-view 每个可见像素的 sun-side visibility，必须先知道该相机像素对应的 3D 世界点，再投影到 sun-view depth 中比较深度，或采用同相机视角的 shadow AOV。 | 冻结规范必须明确二选一：A. **推荐主线**：camera-view Position/WorldCoord pass + sun-view depth reprojection，输出 camera-view 对齐的 `V_sun_macro_mask`；B. Blender 同相机视角 Shadow AOV，若能直接输出与 camera-view 对齐的阴影。不能只写“读取 sun-view EXR 得到 mask”。 |
| CR4-003 | P0 | `08` §2.1、§9.2 | OCS manifest 和目录结构没有保存 sun-shadow 相关路径和重投影元数据。当前只有 `exr_path` / `png_path`，没有 `sun_depth_exr_path`、`sun_visibility_mask_path`、camera/sun 投影矩阵、depth tolerance 等字段。 | 如果主线使用 Level 2，manifest 必须能证明每个 OCS/image 结果到底用了哪张 sun shadow 依据。否则后续审计时只看到结果，看不到遮挡来源。 | 在 manifest/schema/目录结构中加入：`camera_exr_path`、`sun_depth_exr_path`、`sun_visibility_mask_path`、`position_exr_path` 或 `world_position_reconstruction`、`camera_matrix_world`、`sun_camera_matrix_world`、`ortho_scale_m`、`depth_epsilon_m`、`shadow_mapping_method`。 |
| CR4-004 | P1 | `07` §5.4、§8.1 | GGX `f_specular` 分母含 `4·NoL·NoV`，但实现说明只说先过滤 `NoV > 0`，`NoL` 通过 `max` 归零。若在 `NoL=0` 或极小值时先计算 BRDF，再乘 NoL，可能出现除零、inf 或 NaN。 | 这是数值实现坑。旧链里 `NoL` 乘法能把背光面归零，但 GGX 分母不允许先算出非法值。 | 规范中写清楚：有效像素必须满足 `NoV > eps` 且 `NoL > eps`；无效像素 `f_r=0, I_linear=0, OCS contribution=0`。建议 `eps=1e-6` 写入 `brdf_version` 或实现常量。 |
| CR4-005 | P1 | `08` §1.3 | Multi-Geometry 扩展只写“其余 4 组 sun/det 几何”的 geometry pass、OCS manifest、OCS-only、fusion，没有写其余 4 组也需要 sun shadow pass 与 BRDF postprocess。 | 如果 multi-geom OCS concat5 仍采用 Level 2 visibility，那么每个 geom 都需要对应的 sun-side visibility 和 BRDF 后处理。否则 single-geom 和 multi-geom 的 visibility 版本会不一致。 | Multi-Geometry 扩展应写为：每个 geom 都生成 camera geometry pass、sun shadow pass、BRDF/OCS 后处理；image 侧仍可只取 phase63，作为 fusion 多几何增强的固定设定。 |
| CR4-006 | P1 | `08` §2.1、§2.2 | OCS manifest / image manifest 缺少稳定 record key，也没有清楚区分 camera-visible 像素数、contributing 像素数、sun-visible 像素数。 | 后续做 per-attitude 审计、异常差异表、图像/OCS 对齐时，需要稳定 key 和像素统计。只靠 yaw/pitch/geom 组合可以推断，但最好显式记录。 | 每条 record 增加 `record_id`，例如 `{geom_id}_yaw{yyy}_pitch{ppp}`；像素统计拆成 `n_pixels_camera_visible`、`n_pixels_nol_positive`、`n_pixels_sun_visible`、`n_pixels_contributing`，per-part 同理可选。 |
| CR4-007 | P2 | `08` §5.2、§5.4 | §5.2 仍写 `{seedlabel}=实际 seed 值（如 42）`，但 §5.4 又说禁止写 `42` 或任何数字；`split_method` schema 里也有 `e.g. 'coarse_to_fine'`。 | 这不是物理错误，但和“不要把示例误读为默认值”的管理目标冲突。 | 删除所有具体 seed 数字示例。可以写 `{seedlabel}=实际 seed 的字符串标签，由 split 文件生成时写入`。`split_method` 可写 enum 候选，不要在 schema 里写成默认例子。 |
| CR4-008 | P2 | `08` §3.2 | `method_version` 示例 `v0.4-1.0.1.0.1.0.1.0.1.0` 可读性差，容易看不出哪个段对应哪个子版本。 | 不是阻塞项，但后续 source_data 审计会难读。 | 汇总标签建议改成带字段名的短格式，例如 `v0.4-g1.0-b1.0-vis2.0-ocs1.0-img1.0-ds1.0`。一致性检查仍以子版本字段为准。 |

## 4. 已关闭的上一轮 CR3

| CR3 编号 | 状态 | 说明 |
|---|---|---|
| CR3-001 | 已关闭 | 材料参数已与 `_GGX_DB` 一致。 |
| CR3-002 | 已关闭 | yaw 训练网格 72、绘图 seam 73 的区别已写清。 |
| CR3-003 | 已关闭 | `sun_visibility` enum 已改名。 |
| CR3-004 | 基本关闭 | D1 已写为主线优先 Blender sun shadow pass，但实现路径仍需按 CR4-002/003 细化。 |
| CR3-005 | 已关闭 | 版本字段已拆分。 |
| CR3-006 | 已关闭 | linear EXR、log1p、α quick ablation、I_scale 全局最大值策略已写入。 |
| CR3-007 | 已关闭但需联动 | OCS 公式已加 `V_sun_macro`，但图像链还未同步，见 CR4-001。 |
| CR3-008 | 部分关闭 | single-geom 主线 / multi-geom 扩展已拆分，但 multi-geom 的 shadow/BRDF 生成范围缺项，见 CR4-005。 |
| CR3-009 | 已关闭 | 主表 single-geometry 公平基线、multi-geometry 单独报告已写入。 |
| CR3-010 | 已关闭 | 输出目录放在 V0.4 内，路径规则现实可行。 |
| CR3-011 | 部分关闭 | `split_id` 模板已改，但仍残留 `42` 示例，见 CR4-007。 |

## 5. 是否可以进入代码阶段

暂时不建议进入代码阶段。

原因很明确：当前剩余问题集中在 **sun-side visibility 的可执行定义**。如果现在开始写代码，很容易出现三种新分叉：

1. OCS 用 `V_sun_macro`，图像不用。
2. sun-view depth 渲染出来了，但没有严谨映射到 camera-view 像素。
3. manifest 只记录了结果文件，没有记录 shadow pass 来源和重投影参数。

这些不是“以后补文档”的小问题，而是会决定 v0.4 是否真的实现统一前向物理模型。

建议下一步让 Claude 生成两份“最终冻结候选”文件，把 CR4-001 到 CR4-008 关掉。关掉后，Codex 再做一次短复审；若无 P0/P1，再进入 `05_全链路重跑` 的代码任务清单。

---

## 附录：下一步 Claude 提示词

你现在位于：

```text
项目重启_v0.4_BlenderOCS/
```

请先阅读本文件：

```text
04_BlenderOCS方法重建/09_Codex复审意见_前向模型冻结规范修订版.md
```

本次任务是生成 v0.4 前向模型与 manifest 规范的“最终冻结候选”。不要写代码，不要重跑实验，不要修改外部旧目录。

### 必读文件

```text
CLAUDE.md
00_只打开本文件夹时的启动说明.md
00_v0.4总控流程.md
04_BlenderOCS方法重建/07_v0.4前向模型冻结规范_Claude修订版.md
04_BlenderOCS方法重建/08_v0.4数据与manifest字段规范_Claude修订版.md
04_BlenderOCS方法重建/09_Codex复审意见_前向模型冻结规范修订版.md
98_外部材料备份/03_关键代码快照/01_code/materials.py
98_外部材料备份/03_关键代码快照/02_blender/brdf_postprocess.py
```

### 必须先补充的立论

在两个最终冻结候选文件中，必须专门写清楚：为什么 v0.4 不是只替换 OCS 采样，而是选择更完整的统一前向物理模型。论证必须覆盖以下角度：

```text
1. 现实观测贴近性：pixel-level projected visible surface 比 face-center sampling 更接近成像采样。
2. 物理一致性：OCS 和 image 都由同一 BRDF、NoL、V_sun_macro 和 camera visibility 定义。
3. 反演准确性：不承诺必然降低误差，但能让反演结果更可信地反映修正后的观测定义。
4. 模态公平性：OCS 是积分读出，image 是空间分布读出，二者应来自同一前向模型。
5. fusion 可解释性：fusion 提升应来自观测互补，而不是两套仿真误差混合。
6. 退化实验可信度：退化只作用在同源 clean image 上，OCS 作为同源低维观测保持一致。
7. 论文防守性：支撑 observation-consistent synthetic forward model 的写法。
8. 工程可追踪性：manifest/source_data 记录所有版本，避免旧结果和 latest-run 混用。
```

这部分不能只写成口号，必须明确回应：“为什么不只是把采样模型换一下再跑一遍”。

### 必须逐条修正

请逐条吸收本文件 CR4-001 到 CR4-008，尤其注意：

1. **统一前向模型必须一致**：图像线性响应也要乘 `V_sun_macro`。写成：
   ```text
   I_linear(p) = f_r(p) · NoL(p) · V_sun_macro(p)
   ```
   若降级为 `camera_visible_nol`，则 `V_sun_macro≡1`。

2. **sun shadow pass 必须可执行**：不能写成“读取 sun-view EXR 就得到 camera-view mask”。必须明确采用：
   ```text
   camera-view Position/WorldCoord pass + sun-view depth reprojection
   ```
   或者明确采用同 camera-view 对齐的 Blender Shadow AOV。如果选择前者，要写清：
   - camera 像素如何得到 3D world point；
   - world point 如何投影到 sun-view depth；
   - depth tolerance 如何设定；
   - 如何输出与 camera-view 对齐的 `V_sun_macro_mask`。

3. **manifest 必须记录 shadow 来源**：增加 `camera_exr_path`、`sun_depth_exr_path`、`sun_visibility_mask_path`、`position_exr_path` 或 world position 重建方式、camera/sun 矩阵、`depth_epsilon_m`、`shadow_mapping_method`。

4. **GGX 数值边界必须严谨**：有效像素写成 `NoV > eps` 且 `NoL > eps`，否则 `f_r=0`、`I_linear=0`、OCS contribution=0，避免 `4·NoL·NoV` 分母除零。

5. **multi-geometry 扩展必须完整**：如果 multi-geom OCS 使用 Level 2 visibility，那么每个 geom 都要有 camera geometry pass、sun shadow pass、BRDF/OCS 后处理。image 侧可以仍只用 phase63，但要写明这是 fusion 多几何增强设定。

6. **record schema 要方便审计**：每条 record 增加 `record_id`；像素统计区分 `n_pixels_camera_visible`、`n_pixels_nol_positive`、`n_pixels_sun_visible`、`n_pixels_contributing`。

7. **删除 seed 具体数字示例**：不要再出现 `42` 作为 seed 示例。`split_method` 也不要在 schema 中写成像默认值一样的例子。

8. **method_version 汇总标签改清楚**：建议使用：
   ```text
   v0.4-g{geometry}-b{brdf}-vis{visibility}-ocs{ocs}-img{image}-ds{dataset}
   ```
   但一致性检查仍以子版本字段为准。

### 输出文件

请生成新的文件，不要覆盖旧修订版：

```text
04_BlenderOCS方法重建/10_v0.4前向模型冻结规范_最终冻结候选.md
04_BlenderOCS方法重建/11_v0.4数据与manifest字段规范_最终冻结候选.md
```

### 文件 10 必须包含

```text
1. 为什么 v0.4 选择完整统一前向模型，而不是只替换 OCS 采样
2. v0.4 前向模型总图，OCS 与图像均包含 V_sun_macro
3. Blender / Python / 反演代码分工
4. 坐标系、姿态网格、sun/det 方向定义
5. Geometry pass 字段，明确是否加入 Position/WorldCoord pass
6. Sun shadow pass 的可执行定义：camera-view mask 如何由 sun-view depth 或 Shadow AOV 得到
7. OCS 连续公式与像素离散公式
8. 图像线性响应、linear EXR、log1p PNG、训练输入链
9. GGX/Cook-Torrance BRDF 与数值 eps 规则
10. single-geom 主线与 multi-geom 扩展的可见性一致性
11. sanity checks，尤其是 20 姿态 sun shadow pass 验证
12. 写作边界
13. CR4-001 到 CR4-008 对应修正表
```

### 文件 11 必须包含

```text
1. v0.4 旧结果全封存，所有主结果重跑
2. 为什么完整统一模型需要更严格的 manifest/source_data，而不是只记录一个 OCS CSV
3. OCS manifest schema，含 shadow pass 路径、重投影参数、record_id、像素统计
4. Image manifest schema，含 V_sun_macro 后的 linear EXR / log1p PNG 信息
5. source_data.json schema，含六个子版本字段
6. run_id / split_id / seed 规则，禁止具体 seed 示例
7. 禁止 latest-run 自动发现
8. OCS source 与 image source 一致性规则
9. single-geom 主线和 multi-geom 扩展的生成范围
10. v0.4_results 目录结构，单独体现 sun shadow / visibility mask 产物
11. CR4-001 到 CR4-008 对应修正表
```

### 严格限制

- 不要写代码。
- 不要重跑实验。
- 不要修改外部旧目录。
- 不要把旧结果作为 v0.4 主结果。
- 不要把 sun shadow pass 写成不可执行的概念描述；必须写成可落地的数据流。

完成后只总结：生成了哪些文件、吸收了哪些 CR4、还有哪些位置需要 Codex 最后复审。
