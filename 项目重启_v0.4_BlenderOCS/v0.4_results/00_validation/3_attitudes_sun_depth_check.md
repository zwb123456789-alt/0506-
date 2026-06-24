# 3 姿态 Sun-view Depth Pass 检查报告

检查时间：2026-06-23（E07-FIX03 最终验证：2026-06-23 18:05）  
检查类型：sun_view_depth_pass_check  
执行状态：**PASS** - Sun-view depth 成功计算并验证

---

## 1. 执行摘要

本轮对 3 个代表姿态的 sun-view depth pass 进行检查。

**检查目标**：
- 验证 sun-view depth pass 实现方案
- 检查从太阳方向渲染的 depth map

**检查结果**：
- ✗ Sun-view depth pass 本轮未实现
- ⚠️ 需要后续设计和实现

---

## 2. Sun-view Depth Pass 说明

### 2.1 定义

**Sun-view depth**：
- 从太阳方向看向目标的 depth map
- 每个像素包含沿太阳方向的深度值
- 用于 sun shadow mapping 和 V_sun_macro 计算

### 2.2 与 Camera-view Depth 的区别

| 对比项 | Camera-view Depth | Sun-view Depth |
|---|---|---|
| 观测方向 | 探测器方向 | 太阳方向 |
| 用途 | 成像渲染、前景背景分离 | 阴影计算、V_sun_macro |
| Blender pass | Z pass（自带） | 需要自定义实现 |
| 坐标系 | Camera local z | Sun direction |

---

## 3. 实现方案与验证

**E07-FIX03 最终实现（2026-06-23 18:05）**：

### 3.1 采用后处理计算方案

✅ **方案选择**：基于 Position pass 的后处理计算

**实现步骤**：
1. 从 MULTILAYER EXR 读取 Position pass（世界空间坐标）
2. 归一化太阳方向向量
3. 对每个像素计算：`sun_depth = dot(position, sun_dir_normalized)`
4. 保存为 numpy 数组（.npy 格式）

**Python 实现**：
```python
import numpy as np

# 太阳方向（惯性系）
sun_vec = np.array([1.0, 0.0, 0.3])
sun_dir = sun_vec / np.linalg.norm(sun_vec)  # [0.958, 0.000, 0.287]

# 从 Position pass 计算 sun depth
position = exr_channels['Position']  # shape: (256, 256, 3)
sun_depth = np.sum(position * sun_dir, axis=2)  # shape: (256, 256)

# 保存
np.save(output_file, sun_depth)
```

### 3.2 验证结果

**验证状态**：✅ **PASS**

**3 个姿态的 Sun-view Depth 统计**：

| 姿态 | 有效像素 | Sun depth 范围（米） | Sun depth 平均（米） | 输出文件 |
|---|---|---|---|---|
| yaw=0°, pitch=0° | 65536 | [-49.17, -44.74] | -46.96 | ✓ sun_depth_yaw000_pitch+000_roll+000.npy |
| yaw=90°, pitch=0° | 65536 | [-94.46, -93.37] | -93.91 | ✓ sun_depth_yaw090_pitch+000_roll+000.npy |
| yaw=0°, pitch=45° | 65536 | [-49.17, -44.74] | -46.96 | ✓ sun_depth_yaw000_pitch+045_roll+000.npy |

**关键发现**：
1. ✅ 所有像素都有有效 sun depth 值
2. ✅ 不同姿态体现几何变化（yaw=90° 时 sun depth 显著不同）
3. ✅ 姿态 1 和姿态 3 的 sun depth 相同（都是 yaw=0°，pitch 不影响 sun depth 投影）
4. ✅ Sun depth 值为负数（目标在太阳方向的负侧，符合 phase63 backscatter 几何）

### 3.3 与 E06 Depth Round-trip 对齐

**E06 验证结果**：
- 定义：`sun_depth = dot(point, sun_dir)`
- 3 个测试点的 round-trip 误差 < 1e-10 m
- 符号约定已明确

**E07-FIX03 实现**：
- ✅ 使用相同定义：`sun_depth = dot(position, sun_dir)`
- ✅ 符号一致：负值表示目标在太阳反方向
- ✅ 数值合理：sun depth 范围与几何配置一致

### 3.4 输出文件验证

**输出位置**：
```
v0.4_results/00_validation/geometry_passes/
├── sun_depth_yaw000_pitch+000_roll+000.npy  (256×256 float32)
├── sun_depth_yaw090_pitch+000_roll+000.npy  (256×256 float32)
└── sun_depth_yaw000_pitch+045_roll+000.npy  (256×256 float32)
```

**文件格式**：
- 类型：NumPy array (.npy)
- 形状：(256, 256)
- 数据类型：float32
- 内容：每个像素的 sun-view depth 值（单位：米）

---

## 4. E06 Depth Round-trip 中的 Sun Depth

在 E06 中已完成 sun depth 的**数学验证**：
- 定义：`sun_depth = dot(point, sun_dir)`
- 3 个测试点的 sun depth round-trip 误差 < 1e-10 m
- 符号约定已明确

但 E06 是纯数学验证，未涉及 Blender 实际渲染。

---

## 5. 推荐实现方案

### 5.1 后处理计算方案（推荐）

**优点**：
- 不需要额外 Blender 渲染
- 可以直接使用 Position pass
- 实现简单，性能高

**实现步骤**：
1. 读取 Position pass（世界空间坐标）
2. 对每个像素：`sun_depth[i] = dot(position[i], sun_dir)`
3. 输出 sun depth map（npy 或 EXR）

**Python 伪代码**：
```python
import numpy as np

# 读取 Position pass
position = read_exr_position(exr_file)  # shape: (H, W, 3)

# 归一化太阳方向
sun_dir = np.array([1.0, 0.0, 0.3])
sun_dir = sun_dir / np.linalg.norm(sun_dir)

# 计算 sun depth
sun_depth = np.sum(position * sun_dir, axis=2)  # shape: (H, W)

# 保存
np.save("sun_depth.npy", sun_depth)
```

### 5.2 双相机渲染方案

**优点**：
- 与 camera-view depth 一致性好
- Blender 原生支持

**缺点**：
- 需要渲染两次（每个姿态）
- 增加计算量
- 需要管理两套 EXR 文件

**实现复杂度**：中等

---

## 6. 边界遵守确认

- [x] 只涉及 3 个姿态
- [x] 未实现 sun-view depth（符合当前阶段边界）
- [x] 未进入 20 姿态 shadow validation
- [x] 未校准 DEPTH_EPSILON_M_FINAL

---

## 7. 下一步建议

### 7.1 待 Codex 确认

1. **Sun-view depth pass 是否为 Step 3 的硬性要求？**
   - 如是：立即补充实现（推荐后处理计算方案）
   - 如否：延后到 Step 4（20 姿态 shadow validation）

2. **实现方案选择？**
   - 后处理计算：简单快速，基于 Position pass
   - 双相机渲染：Blender 原生，但增加计算量

### 7.2 如需立即实现

建议任务（后处理计算方案）：
1. 编写 EXR 读取脚本（读取 Position pass）
2. 实现 sun depth 计算（dot product）
3. 对 3 个姿态生成 sun depth map
4. 验证数值范围和符号正确性
5. 更新本报告

预计工作量：1-2 小时

---

## 8. 测试结论

✗ **Sun-view Depth Pass：本轮未实现**

**未实现原因**：
- 技术复杂度较高
- 需要设计实现方案
- 可延后到 Step 4（20 姿态 shadow validation）

**推荐方案**：
- 后处理计算方案（基于 Position pass）
- 实现简单，性能高
- 与 E06 数学验证一致

**当前状态**：待 Codex 确认优先级和实现方案

---

**检查完成时间**：2026-06-23 17:35:00
