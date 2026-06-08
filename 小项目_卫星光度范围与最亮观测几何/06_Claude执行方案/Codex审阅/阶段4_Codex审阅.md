# 阶段4 Codex审阅：高轨几何到 OCS 接口设计

审阅时间：2026-06-07

审阅对象：

- `Claude输出/阶段4_高轨几何到OCS接口设计.md`

## 审阅结论

**暂不直接通过。需要小修后进入下一阶段。**

阶段4整体方向是对的：

- 明确了本体坐标系 `M` 与惯性坐标系 `I`；
- 正确识别现有代码旋转矩阵 `R: M→I`、`R.T: I→M`；
- 正确提出距离只进入星等后处理，不进入 OCS 积分；
- 输入/输出 schema 基本完整；
- 明确阶段4只设计接口、不实施、不改原代码。

但有两个必须修正的问题，否则后续阶段5一旦实施，容易出现方向符号错误或违反原大项目保护规则。

## 必改问题

### 1. 输入方向向量的物理含义没有锁死

位置：

- `§2.2 惯性坐标系 I`
- `§3.1 单时刻输入`
- `§7.3 坐标系一致性检查`

当前写法只说：

```text
sun_direction_I
det_direction_I
```

但没有明确这两个向量到底是：

```text
卫星 → 太阳 / 卫星 → 观测者
```

还是：

```text
太阳 → 卫星 / 观测者 → 卫星
```

这不是文字细节，而是 OCS 计算的核心约定。现有代码在 `ocs_core.py` 中使用：

```python
dot_sun = np.dot(normals_I, sun_norm)
dot_det = np.dot(normals_I, det_norm)
primary_idx = np.where((dot_sun > 0) & (dot_det > 0))[0]
```

因此 `sun_norm` 和 `det_norm` 必须表示**从卫星/面元指向太阳、从卫星/面元指向观测者**的出射方向。若传入反向向量，可见面筛选会整体错误，OCS 和最亮姿态都会偏掉。

建议在文档中明确写入：

```text
sun_direction_I = normalize(r_sun_I - r_sat_I)，表示从卫星指向太阳的单位向量。
det_direction_I = normalize(r_obs_I - r_sat_I)，表示从卫星指向观测者/探测器的单位向量。
range_km = ||r_obs_I - r_sat_I||，表示卫星到观测者的斜距。
```

若来自 STK 或轨道外部工具，必须在接口层完成上述转换，而不是直接把 STK 导出的任意位置/视线向量塞进 OCS。

### 2. 输出目录不能写到原大项目 `结果/模块A_重构`

位置：

- `§6.3 目录结构`
- `§9.2 需新增包装层`
- `§10 推荐实施步骤`

当前目录结构写为：

```text
结果/模块A_重构/高轨时间序列/{mission_name}/
```

这不符合用户此前锁定的项目保护规则：原大项目文件夹不能删改、不能添加。阶段5如果按这个路径实施，会向原大项目 `结果/模块A_重构` 添加新结果文件。

建议改为小项目内部路径，例如：

```text
小项目_卫星光度范围与最亮观测几何/05_阶段4_高轨几何接口/结果/{mission_name}/
```

或：

```text
小项目_卫星光度范围与最亮观测几何/07_阶段4输出_高轨OCS接口/{mission_name}/
```

如果阶段5确实要调用原大项目代码，只能**只读调用代码和 STL**，输出必须落在小项目文件夹中。

## 建议修改问题

### 3. `range_km = 36000` 示例容易误导

位置：

- `§3.1 单时刻输入`
- `§3.2 时间序列输入`
- `§4 输出 Schema`

当前示例使用：

```json
"range_km": 36000.0
```

但 GEO 的 `35786 km` 是轨道高度，不是地面观测者到卫星的斜距。地面站到 GEO 卫星的斜距随经纬度、仰角、星下点经度变化，常见量级约 `3.6e4-4.2e4 km`。

建议字段说明改为：

```text
range_km = observer-to-satellite slant range，目标-观测者斜距，不是轨道高度。
示例值仅为近似量级。
```

示例中可写：

```json
"range_km": 38000.0
```

或保留 36000 但明确标注“近似斜距示例，不是 GEO altitude”。

### 4. 相位角定义应与向量符号绑定

位置：

- `§4.1 geometry_derived`
- `§7.3 坐标系一致性检查`

当前写：

```text
phase = arccos(sun·det)
```

这个公式只有在 `sun_direction_I` 与 `det_direction_I` 都定义为**卫星指向太阳/观测者**时才成立。建议加一句：

```text
phase_angle_deg = arccos(dot(sun_direction_I, det_direction_I))，
其中两向量均以卫星为起点。
```

### 5. 阶段3范围对照不能作为通过/失败标准

位置：

- `§10 推荐实施步骤`

当前写：

```text
与阶段3文献范围对照：用典型 GEO 距离和相位角，检查计算星等是否落在阶段3调研的 11-15 mag 范围内
```

建议改成：

```text
与阶段3文献范围做 sanity check：记录是否接近 11-15 mag；若偏离，不直接判定代码错误，而是检查 STL尺度、BRDF参数、精度抽稀、相位角、姿态和星等换算假设。
```

原因是当前 OCS 绝对星等未经真实观测标定，阶段3文献范围不能反过来硬约束仿真结果。

### 6. 输出字段命名需标注“包装层重命名”

位置：

- `§4.1 单时刻输出`
- `§9.1 现有代码可直接复用`

现有 `compute_single_attitude` 返回：

```python
"ocs_no_occ"
"ocs_with_occ"
"occlusion_ratio"  # 0-1
"part_contrib"
```

阶段4输出 schema 写：

```json
"ocs_no_occ_m2"
"ocs_with_occ_m2"
"occlusion_ratio_percent"
```

这可以接受，但需说明：

```text
输出 schema 中的 `_m2` 和 `_percent` 字段由包装层从现有代码返回值转换/重命名得到；核心函数返回字段保持不变。
```

否则阶段5实现时容易误以为要改 `ocs_core.py`。

## 通过项

### 1. 坐标转换方向与代码一致

文档写：

```python
R = euler_to_matrix(yaw, pitch, roll, degrees=True)
sun_dir_M = sun_norm @ R.T
det_dir_M = det_norm @ R.T
```

这与现有代码一致。

### 2. 距离只用于星等换算是正确的

文档没有把 `range_km` 塞进 OCS 积分，这是正确的。

### 3. 绝对星等被标注为条件估算

文档在 `magnitude_estimate` 中列出：

- V-band approximation；
- no atmospheric extinction；
- nominal GGX BRDF parameters；
- STL geometry at 1:1 scale；
- caution：未经真实观测标定。

这个处理符合阶段1公式审计口径。

### 4. 时间序列接口可用

时间序列 schema 能支持多个时刻、多个相位角、不同距离和不同姿态。对于后续高轨最亮几何搜索是够用的。

## 修正后建议结论

阶段4修完上述两项必改问题后，可以判定：

```text
阶段4通过，可进入阶段5包装层设计/实施。
```

阶段5开始前必须锁定：

```text
sun_direction_I = 卫星 → 太阳
det_direction_I = 卫星 → 观测者
range_km = 卫星到观测者斜距
所有新增输出写入小项目文件夹，不写入原大项目结果目录
```

