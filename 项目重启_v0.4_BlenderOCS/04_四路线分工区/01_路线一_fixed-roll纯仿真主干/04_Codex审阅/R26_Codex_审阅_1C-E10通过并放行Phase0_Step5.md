# R26 Codex 审阅：1C-E10 通过并放行 Phase 0 Step 5

最后更新：2026-06-23  
审阅端：Codex  
审阅对象：Claude 提交的 `26_1C-E10_Phase0_Step5_V_sun_macro图像影响验证_Claude执行报告.md`

## 1. 审阅结论

```text
1C-E10：PASS
Phase 0 Step 5：COMPLETE
允许进入 Phase 0 Step 6
不得进入全量 2664 姿态生成
```

本轮已完成 R25 要求的最小完整 Step 5：在 5 个已渲染 Step 4 姿态上，实现并运行 `V_sun_macro` 对图像响应的乘法影响验证。结果显示 5 个姿态全部 PASS，且 yaw000/yaw150 提供了非空的 shadowed-and-valid 像素验证，不是空集平凡通过。

## 2. 核验证据

### 2.1 文件与产物

脚本存在：

```text
06_v0.4_code/10_validation/validate_v_sun_macro_on_image.py
```

结果目录存在并包含 32 个文件：

```text
v0.4_results/00_validation/v_sun_macro_image_check/
```

Claude 执行报告位于标准目录：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/26_1C-E10_Phase0_Step5_V_sun_macro图像影响验证_Claude执行报告.md
```

### 2.2 Summary 核验

目标文件：

```text
v0.4_results/00_validation/v_sun_macro_image_check/v_sun_macro_image_check_summary.json
```

核验结果：

```text
overall_status = COMPLETE
depth_epsilon_m_final = 0.7952109582768545
i_scale_step5 = 0.5444863931551639
i_scale_policy = fixed = max(I_without_vsun over 5 attitudes); no per-frame normalization
brdf_branch = B0_phong_like_provisional_baseline
```

5 个固定姿态均为 PASS：

| 姿态 | valid | shadowed_valid | zero violations | preserve violations |
|---|---:|---:|---:|---:|
| yaw180_pitch+000_roll+000 | 2213 | 0 | 0 | 0 |
| yaw150_pitch+025_roll+000 | 3488 | 53 | 0 | 0 |
| yaw000_pitch+000_roll+000 | 1951 | 66 | 0 | 0 |
| yaw090_pitch+000_roll+000 | 2785 | 0 | 0 | 0 |
| yaw300_pitch-025_roll+000 | 2972 | 0 | 0 | 0 |

### 2.3 独立 EXR/PNG 读回复核

Codex 独立读取 `npy`、`EXR` 和 `PNG` 后核验：

```text
overall= COMPLETE
i_scale= 0.5444863931551639
yaw180_pitch+000_roll+000 uniq=[0.0, 1.0] shadow_nonzero=0  shadow_max=0.0 visible_diff=0.0 png_err=0.00195957
yaw150_pitch+025_roll+000 uniq=[0.0, 1.0] shadow_nonzero=53 shadow_max=0.0 visible_diff=0.0 png_err=0.00193843
yaw000_pitch+000_roll+000 uniq=[0.0, 1.0] shadow_nonzero=66 shadow_max=0.0 visible_diff=0.0 png_err=0.00195405
yaw090_pitch+000_roll+000 uniq=[0.0, 1.0] shadow_nonzero=0  shadow_max=0.0 visible_diff=0.0 png_err=0.00195922
yaw300_pitch-025_roll+000 uniq=[0.0, 1.0] shadow_nonzero=0  shadow_max=0.0 visible_diff=0.0 png_err=0.00195084
```

判定：

- `V_sun_macro` 只含 0/1。
- `V_sun_macro == 0` 且 `I_without_vsun > 0` 的像素中，`I_with_vsun` 读回最大值为 0。
- `V_sun_macro == 1` 且 `I_without_vsun > 0` 的像素中，`I_with_vsun == I_without_vsun`。
- PNG 与 EXR 的 log1p 映射误差在 8-bit 量化范围内。

## 3. 阶段门判定

Phase 0 Step 5 的核心验收项已满足：

- 5 个指定姿态全部完成。
- 使用 `DEPTH_EPSILON_M_FINAL = 0.7952109582768545 m` 生成 `V_sun_macro`。
- 生成并验证含/不含 `V_sun_macro` 的局部 `I_linear`。
- 固定 `I_scale_step5`，未使用 per-frame normalization。
- yaw000/yaw150 存在非空 shadowed-and-valid 像素，证明乘法影响可观测。
- 未重渲染 EXR，未进入全量 2664 姿态，未训练模型，未改写论文正文。

因此：

```text
Phase 0 Step 5 = COMPLETE
```

## 4. 非阻断边界记录

本轮 `f_r` 明确为 Step 5 validation proxy：

```text
B0 phong_like_provisional_baseline via IndexOB
NOT full BRDF post-processing chain
NOT Step 6
```

该边界表述正确。Step 6 仍需正式处理 BRDF/OCS/image 后处理模块化试跑、OCS 积分、manifest 字段与一致性检查入口，不能把 Step 5 产物直接写成完整后处理链路。

## 5. 下一步：Phase 0 Step 6

允许进入 Phase 0 Step 6。建议继续保持小规模受控执行，不进入全量 2664 姿态。

Step 6 目标应为：

```text
正式 BRDF/OCS/image 后处理模块化试跑
```

最小范围建议：

- 复用 1C-E10 的 5 个姿态或缩小为 3 个代表姿态。
- 实现/整理 B0 后处理模块入口。
- 输出 per-frame `I_linear`、log1p PNG、OCS JSON 和必要统计字段。
- 不生成训练集，不训练模型，不进入全量生成。

## 6. 给 Claude 的下一步短提示词

```text
你是 Claude 执行端，只执行，不做 Codex 审阅或阶段裁决。

任务：执行 1C-E11 / Phase 0 Step 6，进行正式 BRDF/OCS/image 后处理模块化小规模试跑。

必须读取：
1. CLAUDE.md 的 1.1 执行环境与命令规则
2. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R26_Codex_审阅_1C-E10通过并放行Phase0_Step5.md
3. 04_四路线分工区/00_总览与裁决/00_路线冻结文件区/04_BlenderOCS方法重建_全局方法冻结文件/13_v0.4前向模型冻结规范_最终冻结版.md 的 §9.2、§11、§12.7
4. 04_四路线分工区/00_总览与裁决/00_路线冻结文件区/04_BlenderOCS方法重建_全局方法冻结文件/14_v0.4数据与manifest字段规范_最终冻结版.md 中 image/OCS manifest 相关字段
5. 06_v0.4_code/10_validation/validate_v_sun_macro_on_image.py
6. 06_v0.4_code/00_config/materials_v0_4.py

建议范围：
- 只做小规模试跑，优先复用 Step 5 的 5 个姿态；如实现风险高，可先选 3 个代表姿态并说明原因。
- 不重渲染 EXR，复用 Step 4 shadow_passes。
- 使用 B0 phong_like_provisional_baseline 作为当前工程 baseline。

必须实现或整理：
1. B0 后处理模块入口，建议路径：
   06_v0.4_code/05_postprocess/image_response_v0_4.py
   06_v0.4_code/05_postprocess/ocs_integration_v0_4.py
   如文件名因 Python import 限制需使用下划线，不使用点号。
2. 对每个试跑姿态输出：
   - I_linear EXR
   - log1p PNG
   - per-frame OCS JSON
   - n_pixels_camera_visible / n_pixels_nol_positive / n_pixels_sun_visible / n_pixels_contributing
3. 使用固定 I_scale_smallrun，不做 per-frame normalization。
4. 明确标注本轮是 B0 small-run，不是全量 corpus，不是训练输入最终 manifest。
5. 执行报告写入：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/

禁止：
- 不得进入全量 2664 姿态生成。
- 不得训练模型。
- 不得改写论文正文。
- 不得修改 CLAUDE.md、13/14/24/25、路线冻结文件或书籍知识库。
- 不得写入 04_Codex审阅/。
- 不得生成 Codex、验收、最终放行等名义文件。

输出状态：
- 若小规模 BRDF/OCS/image 后处理试跑完成且结果可读，写 COMPLETE。
- 若模块边界、EXR 写出、OCS 统计或 manifest 字段理解有阻断，写 NOT_COMPLETE，并列阻断项。
```

## 7. 本轮分流

Codex 审阅记录：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R26_Codex_审阅_1C-E10通过并放行Phase0_Step5.md
```

稳定 Step 5 结果：

```text
06_v0.4_code/10_validation/validate_v_sun_macro_on_image.py
v0.4_results/00_validation/v_sun_macro_image_check/v_sun_macro_image_check_summary.json
v0.4_results/00_validation/v_sun_macro_image_check/
```

