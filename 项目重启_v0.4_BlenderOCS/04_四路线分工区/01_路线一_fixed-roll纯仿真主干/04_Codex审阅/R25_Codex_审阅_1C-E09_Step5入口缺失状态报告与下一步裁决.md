# R25 Codex 审阅：1C-E09 Step 5 入口缺失状态报告与下一步裁决

最后更新：2026-06-23  
审阅端：Codex  
审阅对象：Claude 提交的 `25_1C-E09_Phase0_Step5_入口缺失状态报告.md`

## 1. 审阅结论

```text
1C-E09 状态报告：ACCEPTED
Phase 0 Step 5：NOT_COMPLETE
下一步任务：1C-E10，实现并运行 5 姿态 V_sun_macro 对图像影响验证
不得进入全量 2664 姿态生成
```

Claude 对“当前无法直接执行 Step 5”的判断基本成立：`06_v0.4_code/10_validation/validate_v_sun_macro_on_image.py` 尚不存在，`03_brdf/`、`04_sun_shadow/`、`05_postprocess/` 规划模块也尚未形成完整实现。

但状态报告中有两点需要 Codex 更正：

1. `13 §12.7` 已定位，完整路径为：

```text
04_四路线分工区/00_总览与裁决/00_路线冻结文件区/04_BlenderOCS方法重建_全局方法冻结文件/13_v0.4前向模型冻结规范_最终冻结版.md
```

2. Step 5 不能降级为“只验证 V_sun_macro mask 物理合理性”。§12.7 明确要求：

```text
选 5 个姿态，生成含 V_sun_macro 和不含 V_sun_macro 的 I_linear 对比，
确认 sun-shadowed 像素亮度正确归零，且线性 EXR 和 log1p PNG 同步。
```

因此，下一步应执行一个受控的最小完整 Step 5：只在 5 个已渲染的 Step 4 姿态上实现并运行验证脚本，不进入全量生成，不训练模型。

## 2. 对 Q1-Q5 的 Codex 裁决

### Q1. Claude 是否应实现验证脚本？

裁决：是。

实现目标脚本：

```text
06_v0.4_code/10_validation/validate_v_sun_macro_on_image.py
```

该脚本作为 Phase 0 Step 5 的验证入口，允许在脚本内部复用或抽取 `validate_shadow_consistency_fixed.py` 中的 camera-view → sun-view reprojection 逻辑。当前不要求补齐完整 `03_brdf/04_sun_shadow/05_postprocess` 模块体系。

### Q2. 5 个代表姿态如何选择？

裁决：从 Step 4 已渲染的 20 个姿态中选择 5 个，不新增渲染。

基于 `shadow_validation_summary.json` 的 shadow ratio 与误差覆盖，固定选择：

| 姿态 | 选择理由 |
|---|---|
| `yaw180_pitch+000_roll+000` | 最高 shadow ratio，约 0.847 |
| `yaw150_pitch+025_roll+000` | 高遮挡且 `abs_p99` 最大，约 1.335 m |
| `yaw000_pitch+000_roll+000` | 典型基准姿态，中等遮挡 |
| `yaw090_pitch+000_roll+000` | 低遮挡侧向姿态，sun-visible 比例高 |
| `yaw300_pitch-025_roll+000` | 最低 shadow ratio，约 0.192 |

这 5 个姿态覆盖：强遮挡、误差边界、典型基准、低遮挡、最低遮挡。

### Q3. 是否依赖 BRDF 后处理实现？

裁决：不依赖完整 BRDF 后处理模块，但必须生成 Step 5 局部 `I_linear` 对比产物。

当前路线一 C Phase 0 采用 B0 `phong_like_provisional_baseline` 作为工程 baseline。Step 5 只需验证 `V_sun_macro` 对图像响应的乘法影响，不要求完成全量 `image_response_v0.4.py`、corpus-level `I_scale` 或 manifest 体系。

可接受的最小实现：

```text
I_without_vsun(p) = f_r(p) * NoL(p)
I_with_vsun(p)    = f_r(p) * NoL(p) * V_sun_macro(p)
```

有效像素条件：

```text
NoV > 1e-6 AND NoL > 1e-6 AND camera foreground
```

如果 IndexOB 到部件材料映射暂不稳定，允许本轮使用统一 fallback B0 材料或 `f_r=1` 的 geometry-response proxy，但必须在报告中明确标注为 Step 5 validation proxy，不能写成最终 BRDF 后处理链路。优先使用 `materials_v0_4.py` 中的 B0 fallback。

### Q4. `13 §12.7` 路径是什么？

裁决：见上文路径。Claude 后续必须读取该文件 §12.7 及其前置 §9.2 有效像素规则。

### Q5. Step 5 与 Step 6 边界是什么？

裁决：

- Step 5：小规模验证 `V_sun_macro` 是否正确影响图像响应。只跑 5 个姿态，生成含/不含 mask 的 `I_linear` 与 log1p PNG 对比，验证 sun-shadowed 像素归零和 EXR/PNG 同步。
- Step 6：正式 BRDF/OCS/image 后处理模块化试跑，包含更完整的 B0 后处理、OCS 积分、manifest 字段与后续一致性检查入口。

Step 5 可以实现验证脚本内部的局部图像响应逻辑，但不得自称完成 Step 6 或完整后处理链路。

## 3. 输入与输出约束

### 3.1 输入

必须复用 Step 4 已有文件：

```text
v0.4_results/00_validation/shadow_validation/shadow_validation_summary.json
v0.4_results/00_validation/shadow_passes/{label}_camera.exr
v0.4_results/00_validation/shadow_passes/{label}_sun.exr
```

不得重渲染 EXR。

### 3.2 输出目录

Step 5 结果写入：

```text
v0.4_results/00_validation/v_sun_macro_image_check/
```

建议输出：

```text
selected_attitudes.json
{label}_v_sun_macro.npy
{label}_v_sun_macro.png
{label}_i_linear_without_vsun.exr
{label}_i_linear_with_vsun.exr
{label}_brdf_without_vsun.png
{label}_brdf_with_vsun.png
v_sun_macro_image_check_summary.json
v_sun_macro_image_check_report.md
```

Claude 执行报告写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
```

## 4. 验收标准

1. 5 个指定姿态均完成验证。
2. `V_sun_macro` 只包含 0/1。
3. 对满足 `camera foreground AND NoV > eps AND NoL > eps AND V_sun_macro == 0` 的像素：

```text
I_with_vsun == 0
```

容差建议：

```text
abs(I_with_vsun) <= 1e-7
```

4. 对满足 `V_sun_macro == 1` 的有效像素：

```text
I_with_vsun == I_without_vsun
```

容差建议：

```text
abs(diff) <= 1e-6
```

5. log1p PNG 与线性 EXR 同步。允许使用 5 姿态验证集的固定 `I_scale_step5 = max(I_without_vsun)`，但禁止 per-frame normalization。
6. 报告必须列出每个姿态：

```text
foreground_count
valid_response_count
shadowed_valid_count
sun_visible_valid_count
shadow_zero_violation_count
visible_preserve_violation_count
png_sync_max_abs_diff
status
```

7. 若 EXR 写出失败，不能改为“只输出 PNG 并通过”。必须写 `NOT_COMPLETE` 并列阻断项。

## 5. 给 Claude 的下一步短提示词

```text
你是 Claude 执行端，只执行，不做 Codex 审阅或阶段裁决。

任务：执行 1C-E10，完成 Phase 0 Step 5 的最小完整验证：实现并运行 5 姿态 V_sun_macro 对图像影响检查。

必须读取：
1. CLAUDE.md 的 1.1 执行环境与命令规则
2. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R25_Codex_审阅_1C-E09_Step5入口缺失状态报告与下一步裁决.md
3. 04_四路线分工区/00_总览与裁决/00_路线冻结文件区/04_BlenderOCS方法重建_全局方法冻结文件/13_v0.4前向模型冻结规范_最终冻结版.md 的 §9.2 和 §12.7
4. v0.4_results/00_validation/shadow_validation/shadow_validation_summary.json
5. 06_v0.4_code/10_validation/validate_shadow_consistency_fixed.py
6. 06_v0.4_code/00_config/materials_v0_4.py

固定 5 个姿态：
- yaw180_pitch+000_roll+000
- yaw150_pitch+025_roll+000
- yaw000_pitch+000_roll+000
- yaw090_pitch+000_roll+000
- yaw300_pitch-025_roll+000

必须实现：
1. 新建脚本：
   06_v0.4_code/10_validation/validate_v_sun_macro_on_image.py
2. 复用 Step 4 的 camera/sun EXR，不重渲染。
3. 复用或抽取 validate_shadow_consistency_fixed.py 的 reprojection/depth comparison 逻辑，使用：
   DEPTH_EPSILON_M_FINAL = 0.7952109582768545 m
   生成 5 个姿态的 V_sun_macro mask。
4. 生成含/不含 V_sun_macro 的 Step 5 局部 I_linear：
   I_without_vsun = f_r * NoL
   I_with_vsun = f_r * NoL * V_sun_macro
   有效像素必须满足 NoV > 1e-6 且 NoL > 1e-6。
   如果部件材料映射不稳定，允许使用 B0 fallback 或 f_r=1 proxy，但报告必须明确标注 validation proxy，不能声称完整 BRDF 后处理。
5. 使用固定 I_scale_step5 = max(5 个姿态的 I_without_vsun) 生成 log1p PNG；禁止 per-frame normalization。
6. 写出：
   v0.4_results/00_validation/v_sun_macro_image_check/
   下的 npy/png/exr/json/md 结果。
7. 写执行报告到：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/

验收标准：
- 5 个姿态全部完成。
- V_sun_macro 只含 0/1。
- V_sun_macro == 0 的有效像素中 I_with_vsun 必须归零，容差 1e-7。
- V_sun_macro == 1 的有效像素中 I_with_vsun 与 I_without_vsun 一致，容差 1e-6。
- PNG 与 EXR 的 log1p 映射同步。

禁止：
- 不得进入全量 2664 姿态生成。
- 不得重渲染 EXR。
- 不得训练模型。
- 不得改写论文正文。
- 不得修改 CLAUDE.md、13/14/24/25、路线冻结文件或书籍知识库。
- 不得写入 04_Codex审阅/。
- 不得生成 Codex、验收、最终放行等名义文件。

输出状态：
- 若脚本实现并 5 姿态全部通过，写 COMPLETE。
- 若 EXR 写出、mask 生成、PNG 同步或材料映射任一项阻断，写 NOT_COMPLETE，并列阻断项。
```

## 6. 本轮分流

本轮是 Step 5 入口缺失状态报告审阅与下一步裁决，不更新 `CLAUDE.md`，不生成成果区稳定成果。

Codex 审阅文件：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R25_Codex_审阅_1C-E09_Step5入口缺失状态报告与下一步裁决.md
```

