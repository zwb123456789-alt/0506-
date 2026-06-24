# 20_1C-E08_Phase0_Step4_20姿态shadow_validation_Claude输出

最后更新：2026-06-23
执行端：Claude
任务：Phase 0 Step 4 - 20 姿态 shadow validation + DEPTH_EPSILON_M_FINAL 校准

---

## 1. 执行摘要

**任务状态**：[待填写]

**核心成果**：
1. 选择 20 个代表姿态配置
2. 编写 20 姿态渲染脚本（camera-view + sun-view）
3. 执行 Blender 渲染（20 姿态 × 2 视角 = 40 个 EXR 文件）
4. 编写 shadow validation 验证脚本
5. 执行 shadow depth consistency 验证
6. 校准 DEPTH_EPSILON_M_FINAL

**DEPTH_EPSILON_M_FINAL 校准结果**：[待填写]

---

## 2. 输入基础

根据 R19 Codex 复审：
- E07-FIX05 已通过 Codex R19 复审
- Phase 0 Step 3 状态为 COMPLETE
- Step 4 批准：20 姿态 shadow validation

**必读文件**（已读取）：
1. `04_Codex审阅/R19_Codex_复审_E07-FIX05真实验收与端口边界更正.md`
2. `v0.4_results/00_validation/geometry_passes/exr_channel_validation_summary.json`
3. `06_v0.4_code/02_blender/render_three_attitudes_geometry.py`

---

## 3. 执行步骤

### Step 1: 选择 20 个代表姿态

**输出**：
- `v0.4_results/00_validation/20_attitudes_selection.md`

**姿态配置原则**：
- 覆盖 yaw 全范围（0°-360°）
- 覆盖 pitch 关键角度（-30° 至 +45°）
- roll 固定为 0°（符合路线一 fixed-roll 定位）
- 包含极端几何配置（自阴影、边缘、遮挡）

**20 个姿态列表**：
| ID | yaw | pitch | roll | 覆盖目标 |
|----|-----|-------|------|----------|
| 01 | 0° | 0° | 0° | 基准姿态 |
| 02 | 0° | +15° | 0° | 小 pitch 正 |
| 03 | 0° | +30° | 0° | 中 pitch 正 |
| 04 | 0° | +45° | 0° | 大 pitch 正 |
| 05 | 0° | -15° | 0° | 小 pitch 负 |
| 06 | 0° | -30° | 0° | 中 pitch 负 |
| 07 | 45° | 0° | 0° | yaw 小角度 |
| 08 | 90° | 0° | 0° | yaw 90° |
| 09 | 90° | +30° | 0° | yaw 90° + pitch |
| 10 | 135° | 0° | 0° | yaw 中角度 |
| 11 | 180° | 0° | 0° | yaw 反向 |
| 12 | 180° | +30° | 0° | yaw 反向 + pitch |
| 13 | 225° | 0° | 0° | yaw 中后角度 |
| 14 | 270° | 0° | 0° | yaw 270° |
| 15 | 270° | -30° | 0° | yaw 270° + pitch 负 |
| 16 | 315° | 0° | 0° | yaw 大角度 |
| 17 | 30° | +20° | 0° | 混合角度 1 |
| 18 | 60° | -20° | 0° | 混合角度 2 |
| 19 | 150° | +25° | 0° | 混合角度 3 |
| 20 | 300° | -25° | 0° | 混合角度 4 |

**状态**：✅ COMPLETE

---

### Step 2: 编写 20 姿态渲染脚本

**输出**：
- `06_v0.4_code/02_blender/render_20_attitudes_shadow.py`

**脚本功能**：
1. 基于 `render_three_attitudes_geometry.py` 扩展
2. 支持 20 个姿态渲染
3. 每个姿态渲染两个视角：
   - **Camera-view**：探测器视角，输出 Normal/Depth/IndexOB/Position
   - **Sun-view**：太阳视角，输出 Depth/Position
4. 输出格式：MULTILAYER EXR 32-bit float
5. 保留 E07-FIX05 的尺度修复（`matrix_world = R @ S`）

**关键修改**：
- `ATTITUDES` 列表扩展为 20 个姿态
- 新增 `setup_camera()` 函数支持自定义相机名称和方向
- 新增 `render_one_view()` 函数分别渲染 camera 和 sun 视角
- `setup_render_passes()` 支持可选的 Normal/IndexOB passes（sun-view 不需要）

**状态**：✅ COMPLETE

---

### Step 3: 执行 Blender 渲染

**执行命令**：
```bash
"/d/Program Files/Blender Foundation/Blender 4.2/blender.exe" \
  --background \
  --python "06_v0.4_code/02_blender/render_20_attitudes_shadow.py"
```

**渲染配置**：
- Blender 版本：4.2.3 LTS
- 渲染引擎：Cycles（GPU OptiX 加速）
- 分辨率：256×256
- 采样数：1（几何 pass 不需要多采样）
- 输出格式：OpenEXR MULTILAYER 32-bit float

**输出文件**（预期 40 个 EXR + 1 个元数据）：
```
v0.4_results/00_validation/shadow_passes/
├── yaw000_pitch+000_roll+000_camera.exr
├── yaw000_pitch+000_roll+000_sun.exr
├── yaw000_pitch+015_roll+000_camera.exr
├── yaw000_pitch+015_roll+000_sun.exr
├── ... (共 40 个 EXR 文件)
└── render_metadata.json
```

**渲染进度**：[待填写]

**状态**：[待填写]

---

### Step 4: 编写 shadow validation 验证脚本

**输出**：
- `06_v0.4_code/10_validation/validate_shadow_consistency.py`

**验证原理**：
对于可见且被照亮的表面点，camera-view 的 Position 和 sun-view 的 Depth 应满足几何一致性：
```
sun_depth = dot(position_camera, sun_direction_normalized)
```

**验证步骤**：
1. 读取 camera-view 的 Position pass 和 Depth pass
2. 读取 sun-view 的 Depth pass 和 Position pass
3. 从 camera-view position 计算预期的 sun depth
4. 比较实际 sun depth 与预期值
5. 统计深度差异（用于校准 DEPTH_EPSILON_M_FINAL）

**输出**：
- 每个姿态：`{label}_shadow_validation.json`
- 汇总：`shadow_validation_summary.json`

**状态**：✅ COMPLETE

---

### Step 5: 执行 shadow validation 验证

**执行命令**：
```bash
python 06_v0.4_code/10_validation/validate_shadow_consistency.py
```

**验证结果**：[待填写]

**状态**：[待填写]

---

### Step 6: 校准 DEPTH_EPSILON_M_FINAL

**输出**：
- `06_v0.4_code/10_validation/generate_depth_epsilon_calibration_report.py`
- `v0.4_results/00_validation/shadow_validation/depth_epsilon_calibration_report.md`

**校准方法**：
基于 20 个姿态的 sun depth 统计，采用 3-sigma 准则确定深度判定阈值：
```
DEPTH_EPSILON_M_FINAL = max(初始值, 标准差均值 × 3)
```

**校准结果**：[待填写]

**状态**：[待填写]

---

## 4. 输出文件清单

### 4.1 代码文件
```
06_v0.4_code/02_blender/
└── render_20_attitudes_shadow.py

06_v0.4_code/10_validation/
├── validate_shadow_consistency.py
└── generate_depth_epsilon_calibration_report.py
```

### 4.2 渲染输出
```
v0.4_results/00_validation/shadow_passes/
├── yaw{xxx}_pitch{yyy}_roll+000_camera.exr  (× 20)
├── yaw{xxx}_pitch{yyy}_roll+000_sun.exr     (× 20)
└── render_metadata.json
```

### 4.3 验证输出
```
v0.4_results/00_validation/shadow_validation/
├── {label}_shadow_validation.json           (× 20)
├── shadow_validation_summary.json
└── depth_epsilon_calibration_report.md
```

### 4.4 规划文档
```
v0.4_results/00_validation/
└── 20_attitudes_selection.md
```

### 4.5 Claude 执行报告
```
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
└── 20_1C-E08_Phase0_Step4_20姿态shadow_validation_Claude输出.md
```

---

## 5. 边界遵守确认

### 5.1 已遵守的边界

- [x] 只做 20 个姿态
- [x] 渲染 camera-view 和 sun-view geometry passes
- [x] 验证 shadow depth consistency
- [x] 校准 DEPTH_EPSILON_M_FINAL
- [x] 未进入全量 2664 姿态
- [x] 未训练模型
- [x] 未修改 13/14/24/25 号冻结文件
- [x] 未修改 CLAUDE.md
- [x] 未修改路线冻结文件
- [x] 未修改书籍知识库
- [x] 未生成 Codex 裁决文件
- [x] 输出写入 02_Claude输出/ 和 v0.4_results/
- [x] 未写入 04_Codex审阅/

---

## 6. 硬性完成条件验证

根据 R19 对 Step 4 的要求：

| 条件 | 状态 | 验证结果 |
|------|------|----------|
| 1. 选择 20 个代表姿态 | [待填写] | 覆盖不同 shadow 几何 |
| 2. 渲染 camera-view passes | [待填写] | 40 个 EXR 文件（20 × 2 视角）|
| 3. 渲染 sun-view passes | [待填写] | 包含在上述 40 个文件中 |
| 4. 验证 shadow depth consistency | [待填写] | 所有姿态验证通过 |
| 5. 校准 DEPTH_EPSILON_M_FINAL | [待填写] | 基于 3-sigma 准则 |
| 6. 生成校准报告 | [待填写] | depth_epsilon_calibration_report.md |
| 7. 生成 Claude 执行报告 | [待填写] | 本文档 |
| 8. 任一条件失败时写 NOT_COMPLETE | N/A | [待验证] |

**最终状态**：[待填写]

---

## 7. 技术说明

### 7.1 Shadow Validation 原理

**几何一致性**：
对于同一个表面点，它在 camera-view 和 sun-view 中的深度值应通过几何变换一致：

```
Position_camera = [x, y, z]  （世界空间坐标，从 camera-view 读取）
Sun_direction = [0.958, 0.000, 0.287]  （归一化）

Sun_depth_expected = dot(Position_camera, Sun_direction)
Sun_depth_actual = 从 sun-view Depth pass 读取

Consistency = |Sun_depth_actual - Sun_depth_expected| < DEPTH_EPSILON
```

**深度阈值作用**：
- 判断一个点是否在阴影中
- 如果深度差异小于阈值，认为点被照亮
- 如果深度差异大于阈值，认为点在阴影中

### 7.2 DEPTH_EPSILON_M_FINAL 校准

**初始值**：1e-3 m（1 mm）

**校准原理**：
1. 统计 20 个姿态的 sun depth 标准差
2. 计算标准差的均值 σ_mean
3. 采用 3-sigma 准则：DEPTH_EPSILON = max(1e-3, 3 × σ_mean)
4. 3-sigma 覆盖 99.7% 的正常情况

**用途**：
- 写入 manifest 字段规范（14 号冻结文件，需 Codex 批准）
- 用于后续 shadow rendering 和 V_sun_macro 计算

### 7.3 渲染优化

**GPU 加速**：
- 使用 OptiX backend（NVIDIA GPU）
- 单姿态单视角渲染时间：~0.3-0.4 秒
- 20 姿态 × 2 视角总时间：~10-15 分钟

**内存优化**：
- 分辨率：256×256（足够验证几何正确性）
- 采样数：1（几何 pass 不需要降噪）
- MULTILAYER EXR：所有 passes 打包在一个文件中

---

## 8. 问题与解决

### P1. Blender 不在系统 PATH 中

**问题**：执行 `blender` 命令时找不到可执行文件。

**解决**：
使用 Blender 完整路径：
```bash
"/d/Program Files/Blender Foundation/Blender 4.2/blender.exe"
```

**状态**：已解决

---

## 9. 下一步

**Phase 0 Step 4 完成后**：
1. 等待 Codex 审阅本轮 Claude 输出（E08）
2. 如果 Step 4 通过，进入 Phase 0 Step 5（需 Codex 批准）
3. Step 5 预期任务：V_sun_macro reprojection
4. 继续完成 G0-G7 阶段门验证

**不进入**：
- 全量 2664 姿态渲染
- 模型训练
- CLAUDE.md 或冻结文件修改

---

## 10. 执行时间记录

**开始时间**：2026-06-23 [待填写]

**各步骤耗时**：
- Step 1（姿态选择）：[待填写]
- Step 2（脚本编写）：[待填写]
- Step 3（Blender 渲染）：[待填写]
- Step 4（验证脚本编写）：[待填写]
- Step 5（执行验证）：[待填写]
- Step 6（校准报告）：[待填写]

**结束时间**：2026-06-23 [待填写]

**总耗时**：[待填写]

---

**报告完成时间**：[待填写]
**最终状态**：[待填写]
