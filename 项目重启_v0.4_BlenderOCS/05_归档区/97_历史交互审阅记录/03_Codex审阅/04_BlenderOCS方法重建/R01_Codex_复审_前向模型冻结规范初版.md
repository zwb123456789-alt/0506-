# Codex 复审意见：v0.4 前向模型冻结规范

最后更新：2026-06-08

复审对象：

```text
04_BlenderOCS方法重建/04_v0.4前向模型冻结规范_Claude.md
04_BlenderOCS方法重建/05_v0.4数据与manifest字段规范_Claude.md
```

## 1. 总体判断

Claude 这轮比前两轮明显更接近可执行规范：它已经把 `camera-visible mask`、`NoL/NoV`、`pixel_area_projected`、`sun-side visibility`、`log1p/PNG`、`manifest/source_data` 都放进了冻结框架里，也发现了旧图像链的一个关键隐患：旧写入端是 gamma 2.2 PNG，训练端又叠加 log1p，方法描述曾把它简化成 log1p。

但当前两份文件还不能作为最终冻结规范。原因不是框架不对，而是有几处会直接影响代码实现和实验口径的硬问题：材料参数写错、yaw 网格定义自相矛盾、sun visibility 命名和版本字段还不够严谨。

结论：可以进入“冻结规范修订版”阶段；不能直接进入代码阶段。

## 2. 主要问题

| 编号 | 严重度 | 对应位置 | 问题 | Codex 判断 | 修正要求 |
|---|---|---|---|---|---|
| CR3-001 | P0 | `04` §8.2 材料参数 | GGX 材料参数写错。文件中写 solar `base_color=0.5, roughness=0.50`、dark `base_color=0.3, roughness=0.60`，但备份 `materials.py` 中 `_GGX_DB` 为：金属 `base_color=0.91, roughness=0.20, F0=0.91`；太阳能板 `base_color=0.15, roughness=0.40, ior=1.5`；隐身板 `base_color=0.08, roughness=0.90, ior=1.5`。 | 这是硬错误。材料参数一错，OCS、图像、fusion 全部重跑都会跑偏。 | 按 `98_外部材料备份/03_关键代码快照/01_code/materials.py` 的 `_GGX_DB` 修正。规范中不要手写未经核对的参数。 |
| CR3-002 | P0 | `04` §3.2 姿态定义 | 写了 yaw `[0°, 360°)`、步长 5°、共 73 个值。数学上 `[0,360)` 步长 5° 是 72 个值；73 个值意味着包含 360°，且 0°/360° 姿态重复。 | 这是数据划分和姿态标签的隐性大坑。若 0/360 重复进入 train/test，可能产生泄漏或图表 seam 处理混乱。 | 方法冻结必须决定：训练/反演唯一姿态网格用 72 yaw（0..355），还是保留 73 yaw 仅用于 heatmap seam。建议训练 manifest 用唯一 72 yaw，绘图可复制 0° 为 360° seam。 |
| CR3-003 | P0 | `04` §6、`05` §2.1 `sun_visibility` enum | `camera_only` 容易被误解成“不考虑太阳方向”。前向规范已要求 `NoL<=0` 贡献置零，所以它不是纯 camera-only。 | 命名会把刚修正的 CR2-001 又绕回坑里。 | enum 改为更准确的：`camera_visible_nol`、`camera_visible_nol_plus_sun_shadow_pass`、`camera_visible_nol_plus_python_raycast`。 |
| CR3-004 | P0 | `04` §6 D1 | Claude 推荐优先评估 Blender Shadow Pass，这是合理方向，但仍未把 D1 冻结成可执行决策。 | v0.4 重启的核心是统一前向物理。这里不能一直悬空。 | Codex 建议：v0.4 主线优先实现 `camera_visible_nol_plus_sun_shadow_pass`；若 Blender shadow pass 在小规模验证中不可行，再降级到 `camera_visible_nol` 并在论文中明确边界。 |
| CR3-005 | P1 | `05` §4.2、§6 | 把 `v0.4_method_version` 同时用于几何/BRDF/visibility/log1p/训练配置，会让版本语义过载。log1p α 变化不应伪装成 OCS 前向模型改变。 | 版本字段需要拆开，否则后续 source_data 难以追踪到底是物理前向变了，还是图像预处理变了。 | 拆成：`geometry_version`、`brdf_version`、`visibility_version`、`ocs_integration_version`、`image_preprocess_version`、`dataset_version`。可以保留一个总 `method_version`，但不能只靠它判断一致性。 |
| CR3-006 | P1 | `04` §7、`05` §2.2 | v0.4 图像链定义更清楚了，但 D3/D4 未收回：`α=10` 和 `I_max_global` 仍待确认。 | 可以进入代码原型，但不能进入正式全链路重跑。 | 建议冻结初版策略：保留 linear EXR 为 canonical raw；PNG 训练图由 `I_log=log1p(alpha*I/I_scale)/log1p(alpha)` 生成；`alpha=10` 作为初始值，必须在正式重跑前做 quick ablation；`I_scale` 推荐使用 v0.4 clean corpus 全局最大值，并记录。 |
| CR3-007 | P1 | `04` §5 OCS 公式 | 公式框架可接受，但需要显式加入 macro sun visibility 乘子。 | 如果最终实现 sun shadow，公式必须能自然容纳；否则代码和论文会再分叉。 | 写成：`OCS = Σ A_pix * f_r * NoL * V_sun_macro`，其中 baseline `V_sun_macro=1`，sun-shadow pass 下为 0/1。 |
| CR3-008 | P1 | `05` §1.3 | 写“2701 帧 × 5 geom”作为 v0.4 必须生成范围，但 D2 仍未决定主表用 single-geom 还是 multi-geom。 | 2701 本身也和 yaw 73 问题绑定。不能把未决实验范围写成已冻结生成范围。 | 改成 schema/计划：single-geom baseline 与 multi-geom extension 分开。先冻结 pose grid 和 geom list，再写生成数量。 |
| CR3-009 | P1 | `04` §12 D2 | multi-geometry OCS vs single-geometry image 的公平性仍未给推荐。 | 这是论文主叙事风险。 | Codex 建议：主表必须包含 single-geometry OCS/image/fusion 公平基线；multi-geometry concat5 作为“多观测几何增强”单独报告，不能和 single image baseline 混作唯一主结论。 |
| CR3-010 | P2 | `05` §8.2 路径规则 | 写“不在路径中包含中文”，但 v0.4 工作区根路径本身是中文。 | 这个规则不现实。真正要避免的是 run 子目录、文件名、脚本参数中的空格和特殊字符。 | 改为：v0.4 内部生成目录和文件名使用 ASCII；允许上级工作区中文路径，但脚本必须使用 `pathlib` / 引号 / UTF-8。 |
| CR3-011 | P2 | `05` §4.3 split_id 示例 | 示例 `split_coarse_to_fine_42_10deg_train_v1` 仍可能被误读为推荐 seed=42。 | Claude 已提醒，但最好彻底去掉具体数字。 | 示例改成 `split_{method}_{seedlabel}_{desc}_v{n}`，实际 seed 只在 split 文件生成时写入。 |

## 3. 可以采纳的内容

| 内容 | 采纳方式 |
|---|---|
| Blender/Python/反演三分工 | 可作为最终规范基础 |
| OCS 连续/离散公式大框架 | 可采纳，但需加入 `V_sun_macro` 和修正 yaw 网格 |
| `NoL<=0` / `NoV<=0` 贡献置零 | 可采纳 |
| 发现旧图像链 gamma + log1p 混合问题 | 重要发现，必须保留 |
| v0.4 重新定义 linear -> log1p -> PNG | 可采纳，但参数策略需收回 |
| 禁止 latest-run 自动发现 | 可采纳，必须进入代码规范 |
| source_data / figure_source_data 思路 | 可采纳，但版本字段需拆分 |

## 4. Codex 给出的决策建议

| 问题 | Codex 建议 |
|---|---|
| D1 sun-side visibility | 主线优先实现 Blender sun-shadow pass；若小规模验证不可行，再降级为 camera_visible_nol，并限制论文表述 |
| D2 单几何 vs 多几何 | 主表放 single-geometry 公平基线；multi-geometry concat5 单独作为增强设置 |
| D3 log1p α | α=10 作为初始默认；正式重跑前做 quick ablation，候选 α={5,10,20} + raw |
| D4 I_scale / I_max_global | 使用 v0.4 clean corpus 全局最大值作为 `I_scale`；按 method/preprocess version 记录 |
| D5 LegacyPhong appendix | 不作为 v0.4 主线必做；仅保留为历史/可选附录，不阻塞代码 |
| D6 材料敏感性 | 主实验后做小规模 ±20% roughness / F0 敏感性；不阻塞第一轮主链路 |
| D7 分辨率 ablation | 做代表姿态子集 128/256/512 sanity check；不要求全量三分辨率 |
| D8 split 策略 | 主结果使用 coarse-to-fine 插值 split；随机 split 作为补充。具体 seed 由 split 文件生成时记录 |
| C1 seed 占位 | 正确，不应在规范中填默认值；移除 `42` 示例 |
| C2 输出目录 | 推荐放在 `项目重启_v0.4_BlenderOCS/v0.4_results/`，保证以后只打开 V0.4 文件夹也能继续 |

## 5. 是否可以进入下一步

不能直接进入代码阶段。需要先让 Claude 生成修订版冻结规范，把 CR3-001 到 CR3-011 和上述决策建议收进去。

下一步产物建议：

```text
04_BlenderOCS方法重建/07_v0.4前向模型冻结规范_Claude修订版.md
04_BlenderOCS方法重建/08_v0.4数据与manifest字段规范_Claude修订版.md
```

修订版交回 Codex 复审后，如果材料参数、姿态网格、sun visibility、版本字段全部收口，再进入代码阶段。

---

## 附录：下一步 Claude 提示词

你现在位于：

```text
项目重启_v0.4_BlenderOCS/
```

请先阅读本文件：

```text
04_BlenderOCS方法重建/06_Codex复审意见_前向模型冻结规范.md
```

本次任务只生成前向模型冻结规范和数据/manifest 字段规范的修订版，不写代码、不重跑实验、不修改外部旧目录。

### 必读文件

```text
CLAUDE.md
00_只打开本文件夹时的启动说明.md
00_v0.4总控流程.md
04_BlenderOCS方法重建/04_v0.4前向模型冻结规范_Claude.md
04_BlenderOCS方法重建/05_v0.4数据与manifest字段规范_Claude.md
04_BlenderOCS方法重建/06_Codex复审意见_前向模型冻结规范.md
98_外部材料备份/03_关键代码快照/01_code/materials.py
98_外部材料备份/03_关键代码快照/02_blender/brdf_postprocess.py
```

### 必须修正

必须逐条吸收本文件 CR3-001 到 CR3-011，尤其：

1. 修正 GGX 材料参数，必须以 `materials.py` 中 `_GGX_DB` 为准。
2. 修正 yaw 网格定义，明确训练/反演唯一姿态网格与绘图 seam 的区别。
3. 修正 `sun_visibility` enum，禁止使用容易误解的 `camera_only`。
4. OCS 公式加入 `V_sun_macro`，baseline 下为 1，sun-shadow pass 下为 0/1。
5. 拆分版本字段：geometry / BRDF / visibility / OCS integration / image preprocess / dataset。
6. 收回 D1-D8 和 C1-C2，按 Codex 决策建议写入修订版。
7. 删除 `split_seed=42` 这类可能被误读的示例默认值。
8. 输出目录推荐写入 `项目重启_v0.4_BlenderOCS/v0.4_results/`。
9. 路径规则改为“生成目录和文件名使用 ASCII”，不要写“不允许中文路径”。

### 输出文件

请生成：

```text
04_BlenderOCS方法重建/07_v0.4前向模型冻结规范_Claude修订版.md
04_BlenderOCS方法重建/08_v0.4数据与manifest字段规范_Claude修订版.md
```

### 修订版文件 1 必须包含

```text
1. v0.4 前向模型总图
2. Blender / Python / 反演代码分工
3. 坐标系与姿态定义：唯一训练网格 vs 绘图 seam
4. Geometry pass 字段
5. OCS 连续公式
6. OCS 像素离散公式，含 V_sun_macro
7. pixel_area_projected 定义、NoV 抵消条件、edge pixel 处理
8. NoL/NoV 边界条件
9. sun-side visibility 冻结建议：优先 Blender sun-shadow pass，失败则降级并限制论文表述
10. 正确 GGX/Cook-Torrance 材料参数
11. G_Smith microfacet shadowing-masking 与 macro geometric occlusion 术语区分
12. clean image 线性响应与 log1p/PNG/训练输入关系
13. sanity checks
14. 写作边界
15. 已收回的 D1-D8 决策表
```

### 修订版文件 2 必须包含

```text
1. v0.4 所有旧结果全封存，所有主结果重跑
2. manifest 字段 schema
3. source_data.json 字段 schema
4. 拆分后的版本字段
5. run_id / split_id / seed 规则，禁止伪默认值
6. 禁止 latest-run 自动发现
7. OCS source 与 image source 一致性规则
8. 每个 summary / figure source data 必须记录的字段
9. 输出目录：项目重启_v0.4_BlenderOCS/v0.4_results/
10. 已收回的 C1-C2 决策表
```

### 严格限制

- 不要写代码。
- 不要重跑实验。
- 不要修改外部旧目录。
- 不要把旧结果作为 v0.4 主结果。
- 不要把未决定的问题写成已解决；本文件已给出建议的，按建议写成修订版候选决策。

完成后只总结：生成文件、吸收了哪些 Codex CR、仍需 Codex 复审的位置。
