# Codex 最终复审意见：v0.4 前向模型冻结候选

最后更新：2026-06-08

复审对象：

```text
04_BlenderOCS方法重建/10_v0.4前向模型冻结规范_最终冻结候选.md
04_BlenderOCS方法重建/11_v0.4数据与manifest字段规范_最终冻结候选.md
```

## 1. 总体判断

这轮最终冻结候选已经把 CR4 的主体技术问题基本收回：

- OCS 和 image 均改为同源公式：`f_r · NoL · V_sun_macro`。
- sun shadow pass 已从概念描述推进到 camera-view world point + sun-view depth reprojection 的可执行数据流。
- manifest 增加了 shadow pass 路径、reprojection 参数、camera/sun 矩阵、`record_id` 和像素统计。
- multi-geom 扩展已要求每个 geom 都生成 sun shadow pass 与 BRDF/OCS 后处理。
- GGX 有效像素 `NoV > eps` 且 `NoL > eps` 的数值规则已写入。

但现在仍不能进入代码阶段。剩下两个 P0 必须先修掉：

1. **“为什么选择完整统一前向模型，而不是只替换 OCS 采样”的正式立论没有进入 `10/11` 主体。**  
   这正是作者刚刚强调的重点。`09` 已经写清了，但 `10` 直接从总图开始，`11` 也没有解释为什么 manifest/source_data 需要比一个 OCS CSV 更严格。

2. **sun shadow reprojection 的矩阵方向写反了。**  
   Blender 的 `camera.matrix_world` 通常表示 camera local → world。把世界点变换到相机坐标应使用 `matrix_world.inverted()`；把相机坐标变换到世界坐标才使用 `matrix_world`。当前 `10` 中 `P_sun_cam = sun_camera_matrix_world · P_world` 和 `P_world = camera_matrix_world.inverse() · P_cam` 都是高风险错误。

结论：进入一次“小修最终冻结版”，不是重写大方向。修完这两处 P0 和几个 P1/P2 schema 语义问题，再交 Codex 短复审；通过后进入 `05_全链路重跑` 代码阶段。

## 2. 主要问题

| 编号 | 严重度 | 对应位置 | 问题 | Codex 判断 | 修正要求 |
|---|---|---|---|---|---|
| CR5-001 | P0 | `10` 整体；`11` 整体 | 上一轮明确要求最终冻结候选必须专门写清“为什么不是只替换 OCS 采样，而是选择更完整的统一前向物理模型”。但 `10` 从总图开始，没有独立立论章节；`11` 也没有解释为什么完整统一模型需要更严格的 manifest/source_data。 | 这是方法叙事硬缺口。你后续论文和项目脉络要靠这段立住：更贴近现实、反演证据更可信、统一前向模型，不是为了复杂而复杂。 | `10` 新增第 1 节：“为什么 v0.4 选择完整统一前向模型，而不是只替换 OCS 采样”；`11` 新增第 2 节：“为什么完整统一模型需要更严格的 manifest/source_data”。两节必须覆盖现实观测贴近性、物理一致性、反演准确性、模态公平性、fusion 可解释性、退化实验可信度、论文防守性、工程可追踪性。 |
| CR5-002 | P0 | `10` §6.3、§6.4 | sun shadow reprojection 的矩阵方向写反。`P_sun_cam = sun_camera_matrix_world · P_world` 错；若 `sun_camera_matrix_world` 是 Blender 相机世界矩阵，应使用其逆矩阵把 world 点转到 sun camera local。`P_world = camera_matrix_world.inverse() · P_cam` 也反了。 | 这是实现级硬错误。若照此写代码，`V_sun_macro_mask` 会系统性错位或完全错误。 | 明确矩阵约定：`camera_matrix_world` / `sun_camera_matrix_world` = camera local → world；`world_to_camera = inverse(camera_matrix_world)`；`world_to_sun_camera = inverse(sun_camera_matrix_world)`。公式应为：`P_world = camera_matrix_world @ P_cam_local`；`P_sun_local = inverse(sun_camera_matrix_world) @ P_world`。manifest 可同时记录 `camera_matrix_world` 和派生/可计算的 `world_to_camera_matrix`，但实现必须用正确方向。 |
| CR5-003 | P1 | `10` §6.3、§6.4 | 正交投影 depth 的符号、坐标轴和投影公式仍含糊。`sun_depth_reproj = P_sun_cam.z` 可能不等于 Blender Depth pass 的正向距离；`x_ndc/y_ndc` 也没有处理 Blender 相机 local 坐标中视线通常沿 `-Z` 的约定。 | 这不是叙事问题，是 shadow mask 可靠性的关键。即使矩阵方向修正，depth 符号不一致也会导致遮挡判断反。 | 不要写未验证的 `z_ndc = 2 * depth / ortho_scale`。改成“必须以 Blender 导出的 depth 定义为准”，并要求代码阶段先做 3 个已知点的 depth round-trip sanity check：camera pixel → world → camera local → projected pixel/depth 与原 EXR depth 一致；sun-view 同理。 |
| CR5-004 | P1 | `11` §7.1 | `image_manifest.v_sun_macro_applied == true (iff visibility_version ≥ level 2)` 语义不清。`visibility_version` 是字符串版本号，不应比较“≥ level 2”；而 Level 1 下公式也可以视为乘了恒等 `V_sun_macro ≡ 1`。 | 这个字段会让一致性检查含糊。v0.4 要避免的就是这种“看起来一致但语义不清”的字段。 | 建议改为两个字段：`v_sun_macro_mode: "identity" | "shadow_mask"` 和 `v_sun_macro_applied_to_image: true`。Level 1 时 mode=`identity`；Level 2 时 mode=`shadow_mask`。一致性检查比较 `sun_visibility`、`shadow_mapping_method`、`v_sun_macro_mode`。 |
| CR5-005 | P1 | `11` §2.1 | OCS manifest 中 `sun_depth_exr_path` 和 `sun_visibility_mask_path` 的说明写 `null if visibility_level = camera_visible_nol`，但 schema 中没有 `visibility_level` 字段，实际字段叫 `sun_visibility`。 | 小字段名不一致会在后续 schema/code 中留下坑。 | 全部改成 `null if sun_visibility == "camera_visible_nol"`。 |
| CR5-006 | P2 | `10` §6.5 | `depth_epsilon_m = 1e-3 m` 被写成初始固定值并给了百分比解释，但没有和模型尺度、depth pass 精度、边缘误差验证绑定。 | 可保留为初始候选，但不能写得像最终物理常数。 | 改为 `depth_epsilon_m_initial = 1e-3`，正式值由 20 姿态 shadow validation 校准后写入 manifest。 |

## 3. 已关闭的 CR4

| CR4 编号 | 状态 | 说明 |
|---|---|---|
| CR4-001 | 已关闭 | OCS 与 image 均加入 `V_sun_macro`。 |
| CR4-002 | 部分关闭 | 已给出可执行 reprojection 数据流，但矩阵方向和 depth 定义需按 CR5-002/003 修正。 |
| CR4-003 | 已关闭 | manifest 和目录结构已加入 shadow pass 路径与重投影参数。 |
| CR4-004 | 已关闭 | GGX eps 规则已写入。 |
| CR4-005 | 已关闭 | multi-geom 每 geom 都要求 sun shadow pass + BRDF/OCS 后处理。 |
| CR4-006 | 已关闭 | record_id 和像素统计拆分已写入。 |
| CR4-007 | 基本关闭 | seed 具体数字已清理；保留 `split_{method}_{seedlabel}_{desc}_v{n}` 格式可接受。 |
| CR4-008 | 已关闭 | method_version 已改成带字段名短格式。 |

## 4. 是否可以进入代码阶段

暂时不能。

这不是大返工，而是最后一道闸门。`10/11` 的大方向已经对了，但如果现在进代码，最危险的是 shadow reprojection 坐标变换直接写错；如果现在进论文叙事，最危险的是“为什么完整统一模型值得这些复杂度”没有写进最终冻结规范。

下一步让 Claude 生成两个小修版：

```text
04_BlenderOCS方法重建/13_v0.4前向模型冻结规范_最终冻结版.md
04_BlenderOCS方法重建/14_v0.4数据与manifest字段规范_最终冻结版.md
```

修完后 Codex 只做短复审；若无 P0/P1，再进入代码阶段。

---

## 附录：下一步 Claude 提示词

你现在位于：

```text
项目重启_v0.4_BlenderOCS/
```

请先阅读本文件：

```text
04_BlenderOCS方法重建/12_Codex最终复审意见_前向模型冻结候选.md
```

本次任务是生成 v0.4 前向模型与 manifest 规范的最终冻结版。不要写代码，不要重跑实验，不要修改外部旧目录。

### 必读文件

```text
CLAUDE.md
00_只打开本文件夹时的启动说明.md
00_v0.4总控流程.md
04_BlenderOCS方法重建/00_公式与Blender分工说明.md
04_BlenderOCS方法重建/01_模块A_B与统一前向模型对比决策.md
04_BlenderOCS方法重建/02_Blender采样选择与现实目标说明.md
04_BlenderOCS方法重建/10_v0.4前向模型冻结规范_最终冻结候选.md
04_BlenderOCS方法重建/11_v0.4数据与manifest字段规范_最终冻结候选.md
04_BlenderOCS方法重建/12_Codex最终复审意见_前向模型冻结候选.md
```

### 必须修正

请逐条吸收本文件 CR5-001 到 CR5-006。

1. 在 `13` 中新增独立章节：

```text
为什么 v0.4 选择完整统一前向模型，而不是只替换 OCS 采样
```

这部分必须多角度论证，不要只写口号。至少覆盖：

```text
现实观测贴近性
物理一致性
反演准确性：不承诺必然降误差，但让结果更可信地反映修正后的观测定义
模态公平性：OCS 是积分读出，image 是空间分布读出
fusion 可解释性
退化实验可信度
论文防守性
工程可追踪性
```

2. 在 `14` 中新增独立章节：

```text
为什么完整统一模型需要更严格的 manifest/source_data，而不是只记录一个 OCS CSV
```

必须说明 manifest/source_data 是为了保证 OCS、image、fusion、退化实验和 multi-geom 扩展在 geometry、BRDF、visibility、OCS integration、image preprocess、dataset split 上可追踪、可复审、不可混用。

3. 修正 sun shadow reprojection 的矩阵方向。必须写清：

```text
camera_matrix_world: camera local -> world
sun_camera_matrix_world: sun camera local -> world
world_to_camera_matrix = inverse(camera_matrix_world)
world_to_sun_camera_matrix = inverse(sun_camera_matrix_world)

P_world = camera_matrix_world @ P_camera_local
P_sun_local = world_to_sun_camera_matrix @ P_world
```

禁止再写 `P_sun_cam = sun_camera_matrix_world · P_world`。

4. 修正正交投影 depth 说明。不要写未验证的 depth 编码公式。必须写：

```text
Blender Depth pass 的符号、单位和相机 local z 方向必须通过 depth round-trip sanity check 确认。
```

并加入 3 个已知点的 round-trip 检查：

```text
camera pixel -> world point -> camera local -> reprojected pixel/depth
sun-view world point -> sun camera local -> reprojected pixel/depth
```

5. 修正 image manifest 的 `v_sun_macro_applied` 语义。建议改为：

```json
"v_sun_macro_mode": "<enum: 'identity' | 'shadow_mask'>",
"v_sun_macro_applied_to_image": true
```

Level 1: `identity`；Level 2: `shadow_mask`。

6. 修正字段名：

```text
null if sun_visibility == "camera_visible_nol"
```

不要再写不存在的 `visibility_level`。

7. 修正 `depth_epsilon_m`：

```text
depth_epsilon_m_initial = 1e-3
depth_epsilon_m_final 写入 manifest，由 20 姿态验证校准
```

### 输出文件

请生成新的最终冻结版文件，不要覆盖 `10/11`：

```text
04_BlenderOCS方法重建/13_v0.4前向模型冻结规范_最终冻结版.md
04_BlenderOCS方法重建/14_v0.4数据与manifest字段规范_最终冻结版.md
```

### 严格限制

- 不要写代码。
- 不要重跑实验。
- 不要修改外部旧目录。
- 不要把旧结果作为 v0.4 主结果。
- 不要删除 CR4 已经收回的内容，只在其上修正 CR5。

完成后只总结：生成了哪些文件、吸收了哪些 CR5、还有哪些位置需要 Codex 最后短复审。
