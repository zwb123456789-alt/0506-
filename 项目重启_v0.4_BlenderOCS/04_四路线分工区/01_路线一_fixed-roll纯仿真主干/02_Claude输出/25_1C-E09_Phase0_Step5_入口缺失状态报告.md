# 1C-E09 Phase 0 Step 5 入口缺失状态报告

执行时间：2026-06-23  
执行者：Claude  
任务编号：1C-E09  
状态：**NOT_COMPLETE - 缺少脚本入口**

## 1. 执行摘要

**状态：NOT_COMPLETE**

Phase 0 Step 4 已通过 R24 Codex 审阅放行，`DEPTH_EPSILON_M_FINAL = 0.7952109582768545 m` 已确定。本轮尝试执行 Phase 0 Step 5，但发现**缺少执行入口脚本**。

## 2. 任务定义确认

根据已读取的文档，Phase 0 Step 5 的任务为：

```text
5 姿态 V_sun_macro 对图像影响检查
```

**具体要求**（来源：`01_代码阶段资产盘点与实施计划_Claude.md` §3.2）：

| 任务 | 模块 | 通过标准 | 详见 |
|---|---|---|---|
| 5 姿态 V_sun_macro 对图像影响检查 | `10_validation/validate_v_sun_macro_on_image.py` | sun-shadowed 像素归零，EXR/PNG 同步 | `13` §12.7 |

## 3. 缺失项清单

### 3.1 缺少执行脚本

预期脚本路径：

```text
06_v0.4_code/10_validation/validate_v_sun_macro_on_image.py
```

**实际情况**：该脚本不存在。

`06_v0.4_code/10_validation/` 目录下现有脚本：

```text
phase0_smoke_test.py
_depth_render.py
depth_round_trip_check_OLD_blender_version.py
depth_round_trip_check.py
three_attitude_geometry_check.py
validate_geometry_pass_exr.py
diagnose_position_coordinates.py
transform_position_to_world_space.py
generate_depth_epsilon_calibration_report.py
validate_shadow_consistency.py
validate_shadow_consistency_fixed.py
fix_shadow_validation_outputs.py
```

**结论**：`validate_v_sun_macro_on_image.py` 尚未实现。

### 3.2 缺少参考文档

任务定义中提到"详见 `13` §12.7"，但当前上下文中未明确 `13` 号文件的完整路径。根据命名规则，推测为：

```text
04_四路线分工区/00_总览与裁决/00_路线冻结文件区/13_<文件名>.md
```

但未能在已读取材料中定位到该文件的具体章节。

### 3.3 缺少前置依赖

Phase 0 Step 5 需要以下输入：

1. **5 个代表姿态的渲染结果**：
   - camera geometry pass (Normal/Depth/IndexOB/Position)
   - sun-view depth pass
   - V_sun_macro mask (.npy)

2. **BRDF 后处理结果**：
   - I_linear EXR（图像线性响应）
   - PNG（log1p 映射后的可视化）

3. **DEPTH_EPSILON_M_FINAL**：
   - 已确定为 `0.7952109582768545 m`

**当前不确定项**：
- 5 个代表姿态是否已完成渲染与 V_sun_macro 生成？
- BRDF 后处理脚本是否已实现？

## 4. 阻断项分析

### 4.1 主阻断项

**缺少 `validate_v_sun_macro_on_image.py` 脚本**

根据代码规划文档，该脚本应完成以下功能：

1. 读取 5 个姿态的：
   - camera_exr（Normal/Depth/IndexOB）
   - V_sun_macro_mask.npy
   - I_linear.exr（BRDF 后处理输出）
   - _brdf.png（log1p PNG）

2. 验证逻辑：
   - 对于 `V_sun_macro == 0` 的像素（sun-shadowed），检查 I_linear 是否归零
   - 对于 `V_sun_macro == 1` 的像素，检查 I_linear 是否非零（NoL > 0 且 NoV > 0 时）
   - 检查 PNG 与 EXR 的 log1p 映射一致性

3. 输出报告：
   - 通过/失败状态
   - 统计数据（shadowed 像素数、归零率、异常像素坐标）

### 4.2 次级阻断项

**可能缺少 BRDF 后处理实现**

Step 5 依赖 BRDF 后处理结果（`I_linear.exr` 和 `_brdf.png`），但根据 Phase 0 流程，BRDF 后处理应在 Step 6 之前完成。当前不确定以下脚本是否已实现：

```text
06_v0.4_code/05_postprocess/image_response_v0.4.py
```

### 4.3 前置姿态渲染状态不明

Step 5 需要 5 个代表姿态的完整渲染结果，但当前不确定：

- 这 5 个姿态具体是哪些？（是否与 Step 4 的 20 个姿态重叠？）
- 是否已完成渲染与 V_sun_macro 生成？

## 5. 建议的执行路径

### 5.1 立即可行路径

如果 Codex 期望 Claude 实现 `validate_v_sun_macro_on_image.py` 脚本，则应：

1. **确认前置条件**：
   - 明确 5 个代表姿态的选择标准（是否复用 Step 4 的部分姿态？）
   - 确认是否需要先实现 BRDF 后处理脚本
   - 确认是否需要先渲染这 5 个姿态

2. **实现验证脚本**：
   - 基于 Step 4 的 `validate_shadow_consistency_fixed.py` 作为参考
   - 实现 V_sun_macro 对图像影响的验证逻辑
   - 输出标准化报告

3. **执行验证**：
   - 对 5 个姿态运行验证
   - 生成验证报告

### 5.2 推荐的分解顺序

如果前置依赖未完成，建议按以下顺序执行：

```text
Step 5a：选择 5 个代表姿态（高/低/边缘/典型 shadow 情况）
Step 5b：渲染这 5 个姿态的 camera + sun geometry pass
Step 5c：生成 5 个姿态的 V_sun_macro mask
Step 5d：实现并运行 BRDF 后处理（生成 I_linear EXR 和 PNG）
Step 5e：实现 validate_v_sun_macro_on_image.py
Step 5f：执行验证并生成报告
```

## 6. 当前可提供的信息

### 6.1 已确认的配置参数

- **DEPTH_EPSILON_M_FINAL**: `0.7952109582768545 m`
- **sun_vector**: `[1.0, 0.0, 0.3]`（归一化前）
- **det_vector**: `[0.5, -1.0, 0.1]`（归一化前）
- **resolution**: `256 × 256`
- **STL 路径**: `06_v0.4_code/00_assets/EnviSat.stl`

### 6.2 已有的代码资产

- `validate_shadow_consistency_fixed.py`：可作为参考框架
- Step 4 的 20 个姿态 shadow validation 结果：可复用部分姿态

### 6.3 Python 环境

- **路径**: `C:\Users\97466\.conda\envs\ocs_sim\python.exe`
- **已确认可用的包**: OpenEXR, NumPy, PIL/Pillow

## 7. 给 Codex 的问题清单

为了继续执行 Phase 0 Step 5，需要 Codex 明确以下问题：

### Q1: 脚本实现责任

Claude 是否应该实现 `validate_v_sun_macro_on_image.py` 脚本？还是该脚本应由其他渠道提供？

### Q2: 5 个代表姿态选择

5 个姿态应该如何选择？建议标准：

- 从 Step 4 的 20 个姿态中选择 5 个？
- 还是需要新的姿态组合？
- 选择标准是否为：高 shadow 覆盖、低 shadow 覆盖、边缘情况、典型情况、极端几何？

### Q3: BRDF 后处理前置依赖

Step 5 是否依赖 BRDF 后处理实现？如果是：

- `image_response_v0.4.py` 是否已实现？
- 还是 Step 5 可以先验证 V_sun_macro 物理合理性，暂时跳过对图像响应的验证？

### Q4: `13` 号文档路径

任务定义中提到的 "`13` §12.7" 的完整路径是什么？该章节是否包含 Step 5 的详细规范？

### Q5: Step 5 与 Step 6 的边界

原计划中 Step 5 是"V_sun_macro 对图像影响检查"，Step 6 是"BRDF/OCS/image 后处理 3 姿态试跑"。这两者的边界是否为：

- Step 5：验证 V_sun_macro 掩码的物理正确性（基于已有的 BRDF 输出）
- Step 6：首次完整运行 BRDF/OCS 后处理链路

还是：

- Step 5 只验证 V_sun_macro 掩码本身（不涉及 BRDF 后处理）？

## 8. 临时建议方案

如果 Codex 期望立即推进，建议采用以下最小化路径：

### 方案 A：仅验证 V_sun_macro 掩码物理合理性

**不依赖 BRDF 后处理**，只验证：

1. 从 Step 4 的 20 个姿态中选择 5 个代表姿态
2. 检查这 5 个姿态的 V_sun_macro mask：
   - 掩码值只包含 0 和 1
   - shadowed 像素的空间分布合理（与 sun-view depth 一致）
   - 边缘像素处理合理

**优点**：可立即执行，不依赖未实现的模块  
**缺点**：未验证 V_sun_macro 对图像响应的实际影响

### 方案 B：完整实现 Step 5（含 BRDF 后处理）

**依赖实现 BRDF 后处理**，完整验证 V_sun_macro 对图像的影响。

**优点**：一次性验证完整链路  
**缺点**：需要额外实现 BRDF 后处理脚本，时间成本高

## 9. 当前状态总结

**Phase 0 Step 5 = NOT_COMPLETE**

**阻断原因**：

1. 缺少执行入口脚本 `validate_v_sun_macro_on_image.py`
2. 5 个代表姿态选择标准不明确
3. BRDF 后处理前置依赖状态不明

**已完成项**：

- ✅ DEPTH_EPSILON_M_FINAL 已确定
- ✅ Step 4 的 20 个姿态 shadow validation 已通过
- ✅ Python 环境与工具链已确认

**待决策项**：

- Claude 是否应实现验证脚本？
- 5 个姿态如何选择？
- 是否依赖 BRDF 后处理？

## 10. 输出文件

本报告写入：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/25_1C-E09_Phase0_Step5_入口缺失状态报告.md
```

等待 Codex 审阅与决策。

---

**执行时间**：2026-06-23  
**执行者**：Claude  
**状态**：NOT_COMPLETE（缺少脚本入口与前置依赖确认）  
**下一步**：等待 Codex 明确 Q1-Q5 并提供执行指令
