# 12_1C-E06_depth_round_trip_Claude输出

任务编号：1C-E06  
任务名称：Phase 0 Step 2 - Depth Round-Trip Sanity Check  
执行时间：2026-06-23  
执行状态：✅ 完成

---

## 1. 任务接收

### 1.1 任务来源

- Codex 审阅文件：`R10_Codex_审阅_1C-E05单姿态smoke_test.md`
- 前置任务：1C-E05 单姿态 smoke test（有条件通过）

### 1.2 任务边界（R10 明确指定）

**允许范围**：
- 只执行 Phase 0 Step 2
- 只验证 3 个已知点的 camera/sun depth round-trip
- 只做数学验证，不实际调用 Blender
- 可写入 `06_v0.4_code/10_validation/depth_round_trip_check.py`
- 可写入 `v0.4_results/00_validation/depth_round_trip_report.md`

**禁止范围**：
- 不进入 20 姿态 shadow validation
- 不校准 DEPTH_EPSILON_M_FINAL
- 不运行全量 2664 姿态
- 不训练模型
- 不修改 13/14/24/25、CLAUDE.md、书籍知识库
- 不把 B0 写成书中五参数冯
- 不把 depth round-trip 写成路线一结果或论文结论

---

## 2. 执行策略

### 2.1 问题分析

发现现有 `depth_round_trip_check.py` 文件会实际调用 Blender 渲染，**超出 R10 边界**。

R10 明确要求：
- "只做数学验证"
- "未生成 Blender Depth pass EXR 文件"
- "未实际调用 Blender 渲染"

### 2.2 解决方案

1. 备份现有 Blender 版本脚本为 `depth_round_trip_check_OLD_blender_version.py`
2. 重新编写符合 R10 要求的**纯数学验证脚本**
3. 不调用 Blender，不生成 EXR
4. 只做 3 个已知点的 round-trip 误差计算

---

## 3. 实现细节

### 3.1 测试点选择

选择 3 个代表性点（本体坐标系）：

```python
test_points_body_mm = {
    "P1_metal_front":  np.array([700.0,   0.0,   0.0]),  # 金属主体前端
    "P2_solar_center": np.array([  0.0, -300.0,  0.0]),  # 太阳能板中心
    "P3_dark_top":     np.array([  0.0,   0.0, 400.0]),  # 隐身板顶部
}
```

### 3.2 Camera Depth 定义

```python
def compute_camera_depth(point_world, camera_z_world):
    """
    camera depth = -dot(point, z_camera)
    
    - 相机看向 -z 方向
    - depth 是正值（距离）
    - z_camera 指向远离相机
    """
    camera_z_world = normalize(camera_z_world)
    depth = -np.dot(point_world, camera_z_world)
    return depth
```

### 3.3 Sun Depth 定义

```python
def compute_sun_depth(point_world, sun_dir_world):
    """
    sun depth = dot(point, sun_dir)
    
    - sun_dir 指向太阳
    - sun_depth 可以为正或负
    """
    sun_dir_world = normalize(sun_dir_world)
    sun_depth = np.dot(point_world, sun_dir_world)
    return sun_depth
```

### 3.4 Camera Depth Round-Trip

```
正向：point_world → camera_depth, pixel_xy_ndc
反向：camera_depth, pixel_xy_ndc → point_recovered
误差：||point_world - point_recovered||
```

实现：
- 构造 camera 坐标系（x, y, z 轴）
- 正交投影：NDC = 2 * dot(point, camera_x/y) / ortho_scale
- 反投影：point = pixel_ndc * ortho_scale/2 * camera_x/y - depth * camera_z

### 3.5 Sun Depth Round-Trip

```
正向：point_world → sun_depth, sun_xy
反向：sun_depth, sun_xy → point_recovered
误差：||point_world - point_recovered||
```

实现：
- 构造垂直于 sun 的坐标系（sun_x, sun_y, sun_dir）
- 投影：sun_xy = [dot(point, sun_x), dot(point, sun_y)]
- 反投影：point = sun_depth * sun_dir + sun_xy[0] * sun_x + sun_xy[1] * sun_y

---

## 4. 执行过程

### 4.1 文件操作

1. **备份旧脚本**：
   ```bash
   mv depth_round_trip_check.py depth_round_trip_check_OLD_blender_version.py
   ```

2. **创建新脚本**：
   - 文件：`06_v0.4_code/10_validation/depth_round_trip_check.py`
   - 功能：纯数学验证，不调用 Blender
   - 修复：移除 emoji 字符，避免 Windows GBK 编码问题

3. **执行验证**：
   ```bash
   python depth_round_trip_check.py
   ```

### 4.2 执行结果

```
Camera Round-Trip 最大误差: 1.25e-16 m
Sun Round-Trip 最大误差: 1.11e-16 m
DEPTH_EPSILON_M_INITIAL: 1.00e-03 m

[OK] 所有 round-trip 误差在数值精度范围内（< 1e-10 m）
```

**结论**：所有测试点 round-trip 误差在机器精度范围内，数学定义正确。

---

## 5. 输出文件

### 5.1 代码文件

| 文件 | 状态 | 说明 |
|---|---|---|
| `06_v0.4_code/10_validation/depth_round_trip_check.py` | ✅ 已创建 | 纯数学验证脚本 |
| `06_v0.4_code/10_validation/depth_round_trip_check_OLD_blender_version.py` | ✅ 已备份 | 旧版本（调用 Blender） |

### 5.2 结果文件

| 文件 | 状态 | 说明 |
|---|---|---|
| `v0.4_results/00_validation/depth_round_trip_result.json` | ✅ 已生成 | JSON 格式验证结果 |
| `v0.4_results/00_validation/depth_round_trip_report.md` | ✅ 已生成 | 详细报告 |

### 5.3 Claude 输出

| 文件 | 状态 | 说明 |
|---|---|---|
| `04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/12_1C-E06_depth_round_trip_Claude输出.md` | ✅ 本文件 | Claude 执行报告 |

---

## 6. 验证结果摘要

### 6.1 Camera Depth Round-Trip

| 点 | 原始坐标 (m) | Depth (m) | 恢复坐标 (m) | 误差 (m) |
|---|---|---|---|---|
| P1 | [0.7000, 0.0000, 0.0000] | 0.31180 | [0.7000, 0.0000, 0.0000] | 1.25e-16 |
| P2 | [0.0000, -0.3000, 0.0000] | 0.26726 | [0.0000, -0.3000, 0.0000] | 5.73e-17 |
| P3 | [0.0000, 0.0000, 0.4000] | 0.03563 | [0.0000, 0.0000, 0.4000] | 0.00e+00 |

### 6.2 Sun Depth Round-Trip

| 点 | 原始坐标 (m) | Sun Depth (m) | 恢复坐标 (m) | 误差 (m) |
|---|---|---|---|---|
| P1 | [0.7000, 0.0000, 0.0000] | 0.67048 | [0.7000, 0.0000, 0.0000] | 1.11e-16 |
| P2 | [0.0000, -0.3000, 0.0000] | 0.00000 | [0.0000, -0.3000, 0.0000] | 0.00e+00 |
| P3 | [0.0000, 0.0000, 0.4000] | 0.11494 | [0.0000, 0.0000, 0.4000] | 5.55e-17 |

### 6.3 符号约定确认

✅ **Camera Depth**：
- 所有测试点 depth 均为正值
- 符号约定：depth = -dot(point, z_camera)
- z_camera 指向远离相机

✅ **Sun Depth**：
- Sun depth 可以为正、零或负
- 符号约定：sun_depth = dot(point, sun_dir)
- sun_dir 指向太阳

---

## 7. 边界遵守确认

### 7.1 已遵守的红线

✅ 只执行 Phase 0 Step 2  
✅ 只验证 3 个已知点  
✅ 只做数学验证，未调用 Blender  
✅ 未生成 EXR/PNG/npy 文件  
✅ 未进入 20 姿态 shadow validation  
✅ 未校准 DEPTH_EPSILON_M_FINAL  
✅ 未运行全量 2664 姿态  
✅ 未训练模型  
✅ 未修改 13/14/24/25 号文件  
✅ 未修改 CLAUDE.md  
✅ 未修改书籍知识库  
✅ 未把 B0 写成书中五参数冯  
✅ 未把 depth round-trip 写成路线一结果或论文结论  

### 7.2 文件写入范围

✅ 写入范围严格限定在 R10 允许的位置：
- `06_v0.4_code/10_validation/`
- `v0.4_results/00_validation/`
- `04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/`

---

## 8. 问题与处理

### 8.1 问题 1：现有脚本超出边界

**问题**：发现 `depth_round_trip_check.py` 会调用 Blender 渲染，生成 EXR 文件，超出 R10 边界。

**处理**：
- 备份旧版本为 `*_OLD_blender_version.py`
- 重新编写符合 R10 要求的纯数学验证脚本
- 记录在报告中：本轮未验证 Blender 实际行为

### 8.2 问题 2：Windows GBK 编码

**问题**：脚本中的 emoji 字符（✅ ⚠️）导致 Windows GBK 编码错误。

**处理**：
- 替换所有 emoji 为 `[OK]` 和 `[WARN]`
- 避免使用 `→` 等特殊字符，改用 `->`

---

## 9. 与 R10 的对齐

R10 明确要求：

| R10 要求 | 本轮执行 | 状态 |
|---|---|---|
| 只做 Phase 0 Step 2 | ✅ 只做 Step 2 | ✅ |
| 只验证 3 个已知点 | ✅ 3 个点 | ✅ |
| 只做数学验证 | ✅ 纯数学验证 | ✅ |
| 不调用 Blender | ✅ 未调用 | ✅ |
| 不生成 EXR | ✅ 未生成 | ✅ |
| 不进入 20 姿态 | ✅ 未进入 | ✅ |
| 不校准 final epsilon | ✅ 未校准 | ✅ |
| 不运行全量姿态 | ✅ 未运行 | ✅ |
| 不训练模型 | ✅ 未训练 | ✅ |

**结论**：本轮完全符合 R10 指定的任务边界。

---

## 10. 后续建议

### 10.1 Codex 复审点

建议 Codex 复审以下内容：
1. 是否符合 R10 指定的任务边界
2. 数学验证的 round-trip 误差是否可接受
3. 符号和坐标系约定是否明确
4. 是否可以进入 Phase 0 Step 3（3 姿态几何检查）

### 10.2 下一步选项

**选项 A：按 Phase 0 顺序进入 Step 3**
- 3 姿态几何检查
- Camera geometry pass（Normal/Depth/IndexOB）
- 不进入 20 姿态

**选项 B：验证 Blender depth 实际行为**（需 Codex 明确授权）
- 单姿态 Blender 渲染
- 读取 Blender Depth pass EXR
- 验证 depth 符号/单位与数学定义一致性

**不建议**：直接跳到 20 姿态或全量生成

---

## 11. 重要说明

### 11.1 本轮验证范围

本轮**只验证了数学定义的正确性**，证明：
- Camera/sun depth 的数学公式正确
- Round-trip 算法在数值精度范围内一致
- 符号约定明确

### 11.2 本轮未验证

⚠️ **Blender 实际行为尚未验证**：
- Blender Depth pass 的实际符号约定
- Blender depth 单位（mm 还是 m）
- Blender depth Z 通道名称
- Shadow mapping 的实际 depth reprojection

### 11.3 与 E05 的关系

E05（单姿态 smoke test）验证了：
- STL 加载
- Blender 可调用性
- B0 材料参数

E06（depth round-trip）验证了：
- Depth 数学定义
- Round-trip 算法正确性

两者结合：为后续实际 Blender 渲染提供了理论基准和环境基础。

---

## 12. 最终检查清单

- [x] 读取 R10 审阅文件
- [x] 读取 phase0_entry_notes.md 中 Step 2 要求
- [x] 读取 config_v0_4.py、geometry_loader.py
- [x] 备份现有超出边界的脚本
- [x] 创建符合 R10 要求的纯数学验证脚本
- [x] 修复 Windows GBK 编码问题
- [x] 执行验证脚本
- [x] 生成 depth_round_trip_result.json
- [x] 生成 depth_round_trip_report.md
- [x] 生成本 Claude 执行报告
- [x] 报告说明未进入 20 姿态
- [x] 报告说明未全量生成
- [x] 报告说明未训练模型
- [x] 报告说明未调用 Blender
- [x] 报告说明未生成 EXR
- [x] 报告说明 Blender 实际行为需后续验证
- [x] 未修改 13/14/24/25、CLAUDE.md、书籍知识库
- [x] 未把 B0 写成书中五参数冯
- [x] 未把 depth round-trip 写成路线一结果

---

## 13. 总结

**1C-E06 任务状态：✅ 完成**

执行内容：
- Phase 0 Step 2: Depth Round-Trip Sanity Check（纯数学验证）
- 3 个已知点的 camera/sun depth round-trip 验证
- 符号、单位、坐标系约定确认

验证结果：
- Camera round-trip 最大误差：1.25e-16 m（数值精度范围内）
- Sun round-trip 最大误差：1.11e-16 m（数值精度范围内）
- **整体状态：PASS**

边界遵守：
- 完全符合 R10 指定的任务边界
- 未超出允许的文件写入范围
- 未进入禁止的操作范围

待 Codex 复审后，可进入 Phase 0 Step 3 或其他后续工作。
