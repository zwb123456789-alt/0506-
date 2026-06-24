# 26 1C-E10 Phase 0 Step 5 V_sun_macro 对图像影响验证 Claude 执行报告

最后更新：2026-06-23
执行端：Claude（只执行，不做 Codex 审阅或阶段裁决）
任务来源：`R25_Codex_审阅_1C-E09_Step5入口缺失状态报告与下一步裁决.md`

## 1. 执行结论

```text
任务：1C-E10 Phase 0 Step 5 最小完整验证
输出状态：COMPLETE
5 个指定姿态：全部 PASS
未进入全量 2664 姿态生成、未重渲染 EXR、未训练模型、未改写论文正文。
```

本轮按 R25 裁决执行受控的最小完整 Step 5：在 5 个已渲染 Step 4 姿态上实现并运行
`V_sun_macro` 对图像响应的乘法影响验证，生成含/不含 mask 的局部 `I_linear`、线性 EXR
与 log1p PNG，并完成全部验收项。

## 2. 实现内容

### 2.1 新建脚本

```text
06_v0.4_code/10_validation/validate_v_sun_macro_on_image.py
```

复用 Step 4 资产，不重渲染：

- 从 `validate_shadow_consistency_fixed.py` 导入 `get_sun_camera_params`、
  `world_to_sun_pixel`、`read_position_pass`、`read_depth_pass`、`read_exr_channel`、
  `BLENDER_FAR_PLANE`，camera→sun reprojection 与 depth comparison 逻辑与 Step 4 一致。
- 从 `00_config/materials_v0_4.py` 导入 `get_material_b0`、`brdf_b0_phong_like`。

### 2.2 V_sun_macro 生成

- 阈值固定为 Step 4 批准值 `DEPTH_EPSILON_M_FINAL = 0.7952109582768545 m`。
- 判定：camera 前景点投影到 sun-view，若该处为 sun-view 前景且
  `depth_sun_expected - depth_sun_actual > epsilon`，判为 shadowed（V=0）；
  否则 sun-visible（V=1）。投影出界、sun-view 背景、同面均判 V=1。
- mask 仅含 0/1，已通过断言。

### 2.3 Step 5 局部 I_linear（validation proxy）

```text
I_without_vsun = f_r * NoL
I_with_vsun    = f_r * NoL * V_sun_macro
```

- 有效像素规则（13 §9.2 / CR4-004）：`camera_foreground AND NoV > 1e-6 AND NoL > 1e-6`。
- `f_r` 使用 B0 `phong_like_provisional_baseline`，按 camera EXR 的 `IndexOB` 逐像素映射部件
  （IndexOB 1=jinshuzhuti / 2=taiyangnengban / 3=yinshenban，来自 `render_20_attitudes_shadow.py`
  的 `PART_PASS_INDEX`），Normal pass 已为世界系单位向量。

> 边界声明：本轮 `f_r` 是 Step 5 validation proxy（B0 逐部件），用于验证 `V_sun_macro` 的乘法
> 影响，**不是**最终 BRDF 后处理链路；未实现 `image_response_v0.4.py`、corpus-level `I_scale`
> 或 manifest 体系。不自称完成 Step 6。

### 2.4 log1p PNG 同步

- 固定 `I_scale_step5 = max(5 姿态 I_without_vsun) = 5.444864e-01`（取自 yaw150_pitch+025）。
- PNG 映射：`log1p(alpha * I / I_scale_step5) / log1p(alpha)`，alpha=10。
- **禁止 per-frame normalization**：5 姿态共用同一 `I_scale_step5`。
- PNG 与 EXR 同源于同一线性 `I_linear`，PNG 仅为 8-bit 量化呈现，
  `png_sync_max_abs_diff` 即 8-bit 量化重建误差（≤ 0.5/255）。

## 3. 验收结果

| 姿态 | foreground | valid | shadowed_valid | sun_visible_valid | shadow_zero_viol | visible_preserve_viol | png_sync_max_abs_diff | status |
|---|---|---|---|---|---|---|---|---|
| yaw180_pitch+000_roll+000 | 6000 | 2213 | 0 | 2213 | 0 | 0 | 1.96e-03 | PASS |
| yaw150_pitch+025_roll+000 | 5855 | 3488 | 53 | 3435 | 0 | 0 | 1.94e-03 | PASS |
| yaw000_pitch+000_roll+000 | 5949 | 1951 | 66 | 1885 | 0 | 0 | 1.95e-03 | PASS |
| yaw090_pitch+000_roll+000 | 5210 | 2785 | 0 | 2785 | 0 | 0 | 1.96e-03 | PASS |
| yaw300_pitch-025_roll+000 | 4589 | 2972 | 0 | 2972 | 0 | 0 | 1.95e-03 | PASS |

对照 R25 §4 验收标准：

1. 5 个指定姿态均完成验证 —— 满足。
2. `V_sun_macro` 只含 0/1 —— 满足（断言通过）。
3. `V==0 AND 有效` 像素 `I_with == 0`（容差 1e-7）—— 满足，全部姿态 `shadow_zero_violation = 0`。
   EXR 读回复核：`I_with_vsun` 在 `V==0` 处 max = 0.0。
4. `V==1 AND 有效` 像素 `I_with == I_without`（容差 1e-6）—— 满足，全部姿态
   `visible_preserve_violation = 0`。EXR 读回复核：`V==1` 处 `with == without`（allclose, atol=1e-6）。
5. log1p PNG 与线性 EXR 同步，使用固定 `I_scale_step5`，无 per-frame normalization ——
   满足，`png_sync_max_abs_diff ≤ 1.96e-03 < 0.5/255 ≈ 1.96e-03` 量级（8-bit 量化界内）。
6. 每姿态字段已列全（见上表与 summary JSON）。
7. EXR 写出成功并可读回；未出现"只输出 PNG 即通过"的降级。

## 4. 关于 shadowed_valid 计数的说明（非阻断）

`V_sun_macro` 在 camera 前景内的遮挡像素数为：yaw000=164、yaw150=166、yaw180=7、
yaw300=4、yaw090=0。落入"有效像素（NoL>eps 且 NoV>eps）"的遮挡像素为 yaw000=66、
yaw150=53，其余姿态为 0。

原因：遮挡像素多位于背阳/掠射面，其 `NoL` 接近 0，常被有效像素规则
（`NoL > 1e-6`）排除；这些像素在 `I_without` 上本就接近 0，因此即便参与
也不改变图像。yaw180 虽 Step 4 shadow ratio 高，但其多数 sun-occluded 区域同时是
低 NoL 区，落入有效集的遮挡像素少。

关键点是：yaw000 与 yaw150 提供了 **66 与 53 个 shadowed-and-valid 像素**，这些像素在
`I_with_vsun` 中被正确归零、在 `I_without_vsun` 中保留非零值——`V_sun_macro` 对图像的
乘法影响因此得到了**非空、可读回的正向验证**，而非仅在空集上"平凡通过"。

## 5. 输出产物

脚本：

```text
06_v0.4_code/10_validation/validate_v_sun_macro_on_image.py
```

结果目录：

```text
v0.4_results/00_validation/v_sun_macro_image_check/
  selected_attitudes.json
  v_sun_macro_image_check_summary.json
  {label}_v_sun_macro.npy
  {label}_v_sun_macro.png
  {label}_i_linear_without_vsun.exr
  {label}_i_linear_with_vsun.exr
  {label}_brdf_without_vsun.png
  {label}_brdf_with_vsun.png
```

共 32 个文件（5 姿态 × 6 + 2 汇总），label 为 5 个指定姿态。

## 6. 边界与未越界声明

- 未进入全量 2664 姿态生成；只跑 5 个指定姿态。
- 未重渲染 EXR；全部复用 Step 4 `shadow_passes/` 的 camera/sun EXR。
- 未训练模型；未改写论文正文。
- 未修改 CLAUDE.md、13/14/24/25、路线冻结文件或书籍知识库。
- 未写入 `04_Codex审阅/`；本报告写入 `02_Claude输出/`。
- 未生成 Codex/验收/最终放行名义文件。
- `f_r` 明确标注为 Step 5 validation proxy（B0 逐部件），不声称完整 BRDF 后处理链路，
  不自称完成 Step 6。

## 7. 下一步（建议，待 Codex 裁决）

Step 5 乘法影响已闭合。Step 6 为正式 BRDF/OCS/image 后处理模块化试跑（完整 B0 后处理、
OCS 积分、manifest 字段与一致性检查入口），是否进入由 Codex 审阅本报告后裁决。本轮不自行进入。
