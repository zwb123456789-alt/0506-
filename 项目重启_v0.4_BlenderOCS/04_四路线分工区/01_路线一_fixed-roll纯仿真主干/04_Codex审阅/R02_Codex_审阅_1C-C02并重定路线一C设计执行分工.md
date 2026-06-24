# R02 Codex：审阅 1C-C02 并重定路线一 C 设计执行分工

最后更新：2026-06-22

## 1. 文件性质

本文是对 Claude 输出：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/03_路线一C_单姿态smoke_test与资源估计_Claude输出.md
```

的 Codex 审阅与重规划文件。

本文同时吸收作者新裁决：

```text
后续 Codex 负责设计、审阅、规划和闸门判定；
Claude 只负责按 Codex 已定提示词执行；
Claude 不再负责路线设计、技术裁决或阶段放行。
```

本文不修改 `CLAUDE.md`、13/14/24/25、路线冻结文件、路线总览或任何代码文件。若后续需要同步策略到 `CLAUDE.md` 或总览，应另行列出拟修改范围并经作者确认。

## 2. 总体结论

Claude 的 1C-C02 输出只能作为候选材料参考，不能作为路线一 C 正式设计稿，也不能作为进入实际执行的依据。

原因不是它完全不可用，而是角色边界错位：它继续承担了“设计 smoke test 与资源估计”的工作，并在若干关键技术口径上作出裁决或默认假设。根据作者最新裁决，这类设计、裁决和闸门判定应由 Codex 完成；Claude 后续只执行 Codex 已冻结的任务清单。

本轮 Codex 判定：

```text
1C-C02 Claude 输出：不通过为正式设计稿；
可吸收为参考材料；
不进入 1C-C03 Claude 设计；
由 Codex 重新给出路线一 C smoke test 设计、资源估计边界和执行分工。
```

## 3. 审阅发现

### 3.1 角色错位：Claude 仍在做设计

Claude 输出中大量内容属于设计、裁决和下一阶段放行判断，例如：

- 设计 smoke test 调用链；
- 估算 G1/G3/G5 与 roll sensitivity 资源；
- 判定“可以进入 1C-C03”；
- 给出多几何和 roll sensitivity 的写作表述；
- 给出执行路径 A/B/C。

这些内容后续应由 Codex 负责，不能再交由 Claude 主导。

后续固定分工：

| 角色 | 允许 | 不允许 |
|---|---|---|
| Codex | 设计、审阅、规划、红线检查、闸门判定、生成 Claude 执行提示词 | 未经作者确认直接修改冻结文件或代码 |
| Claude | 按 Codex 提示词读取文件、盘点、执行指定命令、生成执行记录 | 自行设计路线、自行裁决技术口径、自行放行下一阶段 |

### 3.2 BRDF 主线冲突未处理干净

路线一 C 最新裁决是：

```text
五参数冯 / Phong-like BRDF 与书中典型材料参数作为主 BRDF 锚点；
GGX / Cook-Torrance 作为 mismatch、现代 PBR 对照和鲁棒性分支。
```

但 13/14 最终冻结规范仍大量以 `ggx_cook_torrance` 为 v0.4 主模型口径，例如：

```text
13 §9：GGX/Cook-Torrance BRDF 主模型
14 OCS manifest：brdf_model = "ggx_cook_torrance"
14 source_data：brdf_model = "ggx_cook_torrance"
```

这是 2026-06-22 路线一 C 新裁决与旧 13/14 方法冻结文件之间的明确冲突。Claude 无权消解该冲突。后续应由 Codex 在执行层先作临时覆盖口径：

```text
执行路线一 C 时，BRDF 主线按路线一 C 新裁决采用 Phong-like / 五参数冯；
GGX 保留为 mismatch / 对照分支；
13/14 中以 GGX 为主模型的字段和文字暂记为待受控小修冲突点；
未经作者确认，不直接改 13/14。
```

是否小修 13/14，应在路线一 C 代码任务清单确认后另行受控处理。

### 3.3 OCS 积分口径出现误写风险

Claude 输出中出现：

```text
ocs_total = sum(I_linear[u, v] for all pixels) * solid_angle_per_pixel
```

该写法不符合 13 号冻结规范。路线一 C 在未正式修改 13 号前，应沿用 13 号的像素离散 OCS 口径：

```text
OCS = Σ_{p ∈ visible} A_pix · f_r(p) · NoL(p) · V_sun_macro(p)
I_linear(p) = f_r(p) · NoL(p) · V_sun_macro(p)
A_pix = (ortho_scale / resolution)^2
```

因此，后续执行提示词必须禁止引入未冻结的 `solid_angle_per_pixel` 作为 OCS 积分口径。

### 3.4 depth_epsilon 初始值沿用了旧口径

Claude 输出多处使用：

```text
depth_epsilon_m = 0.05m
```

但 13 号最终冻结版明确为：

```text
depth_epsilon_m_initial = 1e-3 m
depth_epsilon_m_final 由 20 姿态 shadow validation 校准后确定
```

后续所有 smoke test、depth round-trip 和 shadow validation 设计必须采用：

```text
初始候选：1e-3 m
最终值：校准后写入 manifest
```

不得再默认 0.05m。

### 3.5 资源估计过实

Claude 给出了小时级、GB 级甚至多日级估计。当前没有正式 v0.4 代码区、没有实际 smoke test 运行记录、没有确认的并行策略和硬件环境，因此这些估计只能作为粗略 envelope，不得作为任务排期或资源裁决依据。

后续 Codex 资源估计应分为三层：

```text
R0：未运行前的数量级 envelope；
R1：单姿态 smoke test 后的实测校准估计；
R2：3 姿态 / 20 姿态 gate 后的全量生成估计。
```

当前只能使用 R0，不得把 R0 写成执行承诺。

### 3.6 “是否进入 1C-C03”不能由 Claude 判定

Claude 输出末尾自行判定：

```text
可以进入 1C-C03 设计阶段。
```

后续不采用该判定。阶段放行只由 Codex 给出。

本轮 Codex 判定：

```text
不继续让 Claude 设计 1C-C03；
由 Codex 重写 smoke test 与几何/可见性校验设计；
之后 Claude 只执行 Codex 指定的文件定位、代码盘点或受控实现任务。
```

## 4. 可吸收内容

Claude 1C-C02 中可保留为参考的部分：

1. 将路径标注为 `[拟议路径，待作者/Codex确认]` 的意识是正确的。
2. 将历史快照标注为 `[历史快照参考，不直接运行]` 是正确的。
3. smoke test 的六段流程可作为粗粒度框架：
   - camera-view geometry pass；
   - sun-view depth pass；
   - V_sun_macro reprojection；
   - BRDF 后处理与 OCS 积分；
   - manifest 单条记录；
   - smoke test report。
4. G1/G3/G5、roll sensitivity 与三轴小项目的边界说明总体方向正确，但以后由 Codex 写入正式设计。

不可直接采用的部分：

1. `solid_angle_per_pixel` OCS 积分口径。
2. `depth_epsilon_m = 0.05m` 初始值。
3. 将 13/14 的 GGX 主模型口径和路线一 C 的 Phong-like 主锚点混合处理而不列冲突。
4. 由 Claude 自行判定阶段放行。
5. 过于实化的资源时间表。

## 5. Codex 版路线一 C smoke test 正式设计

### 5.1 设计定位

路线一 C smoke test 不是实验结果，不是论文结果，也不是全量重跑的替代品。它只回答：

```text
在正式 v0.4 代码区尚未建立前，路线一 C 的最小同源前向链路应如何被执行和验证；
一旦作者确认创建代码区和输出区，Claude 应按哪些具体步骤实现/运行；
哪些硬 gate 不通过时不得进入全量生成。
```

### 5.2 最小样本

| 项 | Codex 设计 |
|---|---|
| 目标模型 | 三部件真实模型：`jinshuzhuti`、`taiyangnengban`、`yinshenban`；STL 具体路径待确认 |
| 姿态 | `yaw=45°`、`pitch=30°`、`roll=0°`；roll 明确为 fixed-roll 受控变量 |
| 几何 | 单几何 phase63 / G1 baseline；具体 sun/det 向量以后从冻结配置或历史 config 中确认 |
| 分辨率 | 256×256，作为 gate 验证分辨率 |
| ortho_scale | `2.2 × r_max`，沿用 13 号规范 |
| BRDF 主线 | Phong-like / 五参数冯主锚点；若代码尚未实现，先实现，不得用 GGX 冒充主线 |
| GGX | 仅作为后续 mismatch / 对照分支，不进入 smoke test 主线成功判据 |
| visibility | 优先 Level 2：`camera_visible_nol_plus_sun_shadow_pass`；若 gate 失败，整体降级 Level 1 |
| depth_epsilon | 初始 `1e-3 m`；最终由 20 姿态 shadow validation 校准 |

### 5.3 最小链路

正式 smoke test 的最小链路冻结为：

```text
Step 0：确认代码区 / 输出区 / 文件创建范围
Step 1：camera-view geometry pass
Step 2：sun-view depth pass
Step 3：depth round-trip sanity check
Step 4：V_sun_macro reprojection
Step 5：Phong-like BRDF 后处理与 OCS 积分
Step 6：image linear response + log1p PNG
Step 7：单条 OCS manifest + image manifest
Step 8：smoke_test_report.md
```

注意：`depth round-trip` 必须在完整 V_sun_macro 之前执行。Claude 输出中把 round-trip 放到后续 1C-C03 容易导致执行顺序松动；Codex 这里明确将其提前为 smoke test 内部硬 gate。

### 5.4 OCS 与图像公式

路线一 C smoke test 主线公式：

```text
I_linear(p) = f_r(p) · NoL(p) · V_sun_macro(p)
OCS = Σ A_pix · f_r(p) · NoL(p) · V_sun_macro(p)
A_pix = (ortho_scale / resolution)^2
```

其中：

```text
f_r(p) = Phong-like / 五参数冯主锚点
NoL(p) = max(N(p) · L, 0)
V_sun_macro(p) ∈ {0, 1}
```

禁止在 smoke test 主线中使用：

```text
solid_angle_per_pixel
GGX 作为主线 BRDF
Blender Principled BSDF / Combined pass 作为最终亮度
旧 face-center OCS
```

### 5.5 Manifest 临时字段策略

由于 14 号当前仍以 `brdf_model = "ggx_cook_torrance"` 为旧主线字段示例，路线一 C smoke test 的 manifest 设计应采用临时过渡策略：

```text
brdf_model = "phong_like_five_param"    # 路线一 C 主线
brdf_branch = "main_anchor"
brdf_reference = "book_material_params_or_project_confirmed_params"
ggx_branch = "mismatch_control"         # 后续对照分支
```

这属于对路线一 C 新裁决的执行层覆盖。是否正式写入 14 号，需要后续受控小修。

### 5.6 输出目录口径

14 号规范中输出根目录是：

```text
项目重启_v0.4_BlenderOCS/v0.4_results/
```

Claude 输出和前期讨论中出现：

```text
07_v0.4_results/
```

两者存在命名冲突。Codex 判定：

```text
在未小修 14 号前，正式执行优先沿用 14 号的 v0.4_results/；
若作者更希望使用 07_v0.4_results/ 以匹配当前顶层编号结构，应作为受控小修点列出；
Claude 不得自行选择输出根目录。
```

同理，新代码区 `06_v0.4_code/` 只是拟议路径，需作者确认后创建。

## 6. Phase 0 gate 重新定义

路线一 C Phase 0 gate 应按以下顺序：

```text
G0：代码区/输出区创建确认
G1：单姿态 camera-view geometry pass
G2：单姿态 sun-view depth pass
G3：3 点 depth round-trip
G4：单姿态 V_sun_macro reprojection
G5：单姿态 Phong-like BRDF + OCS/image 同源输出
G6：单条 OCS/image manifest 字段检查
G7：20 姿态 shadow validation + depth_epsilon_m_final 校准
G8：5 姿态 V_sun_macro 对图像影响验证
```

进入全量生成的最低要求：

```text
G0-G7 必须通过；
G8 强烈建议通过；
若 G7 失败，不允许以 Level 2 进入全量；
只能修复后重测，或整体降级 Level 1 并记录原因。
```

## 7. 资源估计策略

当前阶段只允许 R0 级估计：

```text
R0 = 未运行前的数量级 envelope，用于判断是否可能跑；
R1 = smoke test 实测后估计，用于判断 G1/G3/G5；
R2 = 20 姿态 gate 后估计，用于全量排期。
```

Claude 1C-C02 中的小时/GB 级数字全部降级为 R0 草估，不作为正式排期。

Codex 当前建议：

1. 不在正式文档中承诺 G5 需要多少小时。
2. 先执行单姿态 smoke test，记录真实耗时和文件大小。
3. 再执行 3 姿态几何检查和 20 姿态 shadow validation。
4. 用实测平均值和方差外推 G1/G3/G5。

## 8. 后续 Claude 执行策略

从本文之后，Claude 提示词必须采用“执行型”而非“设计型”。

### 8.1 Claude 允许做

- 按 Codex 给定路径读取文件。
- 按 Codex 给定清单检查文件是否存在。
- 按 Codex 给定脚本/命令执行。
- 记录输出、错误、耗时和文件大小。
- 根据错误日志做局部定位，但不改变路线设计。

### 8.2 Claude 不允许做

- 自行决定新代码区路径。
- 自行决定输出根目录。
- 自行决定 BRDF 主线。
- 自行放行 1C-C03 或 Phase 0 gate。
- 自行扩大到 G1/G3/G5 或训练。
- 自行修改冻结文件。

### 8.3 下一条 Claude 提示词方向

不再让 Claude 设计 1C-C03。

下一条 Claude 提示词应是执行型：

```text
1C-E01：按 Codex 指定清单，核对历史快照中可复用代码的真实内容和依赖，不作设计裁决。
```

它只应输出：

```text
1. 文件存在性；
2. 关键函数/变量列表；
3. 与 Codex 设计不一致之处；
4. 依赖库清单；
5. 不进行修改。
```

## 9. 待作者确认事项

进入代码执行前，需要作者确认：

1. 是否创建新代码区：

```text
项目重启_v0.4_BlenderOCS/06_v0.4_code/
```

2. 输出根目录采用哪个：

```text
方案 A：v0.4_results/      # 与 14 号一致
方案 B：07_v0.4_results/   # 与当前顶层编号结构更一致，但需小修 14 号
```

3. 是否同意路线一 C 执行层临时覆盖 13/14 的 GGX 主线字段：

```text
Phong-like / 五参数冯 = 主锚点
GGX = mismatch / 对照
```

4. 是否后续受控小修 13/14 中的 BRDF 主线字段和输出目录字段。

5. 是否让 Codex 下一步生成 `1C-E01` Claude 执行提示词。

## 10. 最终判定

```text
Claude 1C-C02：不作为正式设计稿通过；
Codex 已在本文重定正式设计边界；
后续不再让 Claude 做设计；
进入执行前，需先确认代码区、输出区、BRDF 冲突处理和是否小修 13/14；
下一步建议由 Codex 生成 1C-E01 执行型 Claude 提示词。
```

