# 阶段4：高轨几何到 OCS 接口设计

最后更新：2026-06-07

---

## 1. 设计目标

设计从高轨/STK几何数据到现有 OCS 扫描代码的输入接口，支持：

1. 单个观测时刻的 OCS 计算
2. 时间序列的离散化处理
3. 距离仅用于星等换算，不进入 OCS 积分
4. 清晰的坐标系定义和转换规则

---

## 2. 坐标系定义

### 2.1 本体坐标系 M（Body Frame）

- **定义**：固连于卫星 STL 模型的坐标系
- **原点**：STL 模型的几何中心或用户定义参考点
- **轴向**：按 STL 设计文档约定（需在具体实施时明确）
- **存储**：STL mesh 顶点、法向、三角形中心均在 M 系表达
- **代码中**：mesh 始终保持在 M 系，不做复制或变换

### 2.2 惯性坐标系 I（Inertial Frame）

- **定义**：固定的参考坐标系，用于表达太阳方向、观测方向、卫星姿态
- **候选**：
  - ECI（地心惯性系，J2000）
  - 或用户自定义的固定参考系
- **约定**：太阳方向 `sun_direction_I` 和探测器方向 `det_direction_I` 始终在 I 系表达
- **代码中**：旋转矩阵 `R: M→I`，`R.T: I→M`

### 2.3 方向向量物理含义（关键约定）

**必须严格遵守**：

```
sun_direction_I = normalize(r_sun_I - r_sat_I)
```
表示**从卫星指向太阳**的单位向量。

```
det_direction_I = normalize(r_obs_I - r_sat_I)
```
表示**从卫星指向观测者/探测器**的单位向量。

```
range_km = ||r_obs_I - r_sat_I||
```
表示卫星到观测者的斜距（千米）。

**理由**：现有代码 `ocs_core.py` 通过以下逻辑筛选可见面元：

```python
dot_sun = np.dot(normals_I, sun_norm)
dot_det = np.dot(normals_I, det_norm)
primary_idx = np.where((dot_sun > 0) & (dot_det > 0))[0]
```

若 `sun_norm` 和 `det_norm` 表示**从卫星/面元指向太阳和观测者**的出射方向，则 `dot > 0` 筛选出法向朝向太阳和观测者的面元（物理正确）。

若传入反向向量（如"太阳→卫星"或"观测者→卫星"），可见面筛选会整体错误，OCS 和最亮姿态均会偏离。

**从 STK 或外部工具提取数据时**：必须在接口层完成上述转换，确保输入向量符合"卫星→太阳"和"卫星→观测者"约定。

### 2.4 坐标系转换

```
卫星姿态（yaw, pitch, roll）→ 旋转矩阵 R（M→I）
太阳/探测器方向（I 系）→ 反向变换到 M 系 → 射线查询
```

现有代码实现（`geometry.py` 第 16-41 行）：

```python
R = euler_to_matrix(yaw, pitch, roll, degrees=True)
# R: M→I (Z-Y-X 内旋顺序)
# R.T: I→M
sun_dir_M = sun_norm @ R.T
det_dir_M = det_norm @ R.T
```

---

## 3. 输入 Schema

### 3.1 单时刻输入（JSON 格式）

```json
{
  "time_utc": "2026-06-15T12:34:56.789Z",
  "sun_direction_I": [0.866, 0.0, 0.5],
  "det_direction_I": [0.5, -0.866, 0.1],
  "satellite_attitude": {
    "yaw_deg": 45.0,
    "pitch_deg": 10.0,
    "roll_deg": 0.0,
    "convention": "ZYX_intrinsic"
  },
  "range_km": 38000.0,
  "label": "GEO_2026_165_1234"
}
```

**字段说明**：

| 字段 | 类型 | 单位/约定 | 必需 | 说明 |
|---|---|---|---|---|
| `time_utc` | string (ISO 8601) | UTC | 可选 | 观测时刻，用于追溯和命名，不进入 OCS 计算 |
| `sun_direction_I` | array[3] (float) | 无单位向量（惯性系 I） | **必需** | **从卫星指向太阳**的方向向量，代码会自动归一化。若从位置矢量提取：`normalize(r_sun_I - r_sat_I)` |
| `det_direction_I` | array[3] (float) | 无单位向量（惯性系 I） | **必需** | **从卫星指向观测者/探测器**的方向向量，代码会自动归一化。若从位置矢量提取：`normalize(r_obs_I - r_sat_I)` |
| `satellite_attitude.yaw_deg` | float | 度 | **必需** | 偏航角（绕 Z 轴） |
| `satellite_attitude.pitch_deg` | float | 度 | **必需** | 俯仰角（绕 Y 轴） |
| `satellite_attitude.roll_deg` | float | 度 | **必需** | 滚转角（绕 X 轴） |
| `satellite_attitude.convention` | string | 固定为 `"ZYX_intrinsic"` | 推荐 | 欧拉角旋转约定，与 `geometry.euler_to_matrix` 一致 |
| `range_km` | float | 千米 | **必需（用于星等）** | **卫星到观测者的斜距**（slant range），不是轨道高度。**仅用于星等换算**，不进入 OCS 积分。示例值 38000.0 为 GEO 典型斜距量级 |
| `label` | string | 用户自定义 | 推荐 | 用于输出文件命名和追溯 |

### 3.2 时间序列输入（JSON 格式）

```json
{
  "mission_name": "GEO_orbit_track_2026_Q2",
  "stl_geometry": {
    "jinshuzhuti": "path/to/jinshuzhuti.stl",
    "taiyangnengban": "path/to/taiyangnengban.stl",
    "yinshenban": "path/to/yinshenban.stl"
  },
  "brdf_model": "ggx",
  "accuracy_level": "fast",
  "time_series": [
    {
      "time_utc": "2026-06-15T12:00:00.000Z",
      "sun_direction_I": [0.866, 0.0, 0.5],
      "det_direction_I": [0.5, -0.866, 0.1],
      "satellite_attitude": {"yaw_deg": 45.0, "pitch_deg": 10.0, "roll_deg": 0.0},
      "range_km": 38000.0,
      "label": "t0000"
    },
    {
      "time_utc": "2026-06-15T12:05:00.000Z",
      "sun_direction_I": [0.870, 0.0, 0.493],
      "det_direction_I": [0.52, -0.854, 0.1],
      "satellite_attitude": {"yaw_deg": 46.2, "pitch_deg": 10.1, "roll_deg": 0.0},
      "range_km": 38010.0,
      "label": "t0001"
    }
  ]
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|---|---|---|
| `mission_name` | string | 任务名称，用于输出目录命名 |
| `stl_geometry` | object | STL 文件路径字典（部件名 → 路径） |
| `brdf_model` | string | BRDF 模型选择（`"ggx"` / `"legacy_phong"`） |
| `accuracy_level` | string | 精度级别（`"fast"` / `"medium"` / `"full"`） |
| `time_series` | array[object] | 每个时刻的观测几何（格式同 3.1） |

---

## 4. 输出 Schema

### 4.1 单时刻输出（JSON 格式）

**注**：输出 schema 中的 `_m2` 和 `_percent` 后缀由包装层从现有代码返回值转换/重命名得到；核心函数 `compute_single_attitude` 返回字段保持不变（`ocs_no_occ`, `ocs_with_occ`, `occlusion_ratio` 为 0-1）。

```json
{
  "input_echo": {
    "time_utc": "2026-06-15T12:34:56.789Z",
    "sun_direction_I_normalized": [0.866, 0.0, 0.5],
    "det_direction_I_normalized": [0.485, -0.840, 0.097],
    "satellite_attitude": {"yaw_deg": 45.0, "pitch_deg": 10.0, "roll_deg": 0.0},
    "range_km": 36000.0,
    "label": "GEO_2026_165_1234"
  },
  "geometry_derived": {
    "phase_angle_deg": 63.4,
    "range_m": 3.8e7
  },
  "ocs_results": {
    "ocs_no_occ_m2": 14.82,
    "ocs_with_occ_m2": 12.35,
    "occlusion_ratio_percent": 16.7,
    "visible_faces_no_occ": 1245,
    "visible_faces_with_occ": 1038
  },
  "part_contribution": {
    "jinshuzhuti": {
      "ocs_no_occ_m2": 3.21,
      "ocs_with_occ_m2": 2.85,
      "visible_faces_no_occ": 345,
      "visible_faces_with_occ": 298
    },
    "taiyangnengban": {
      "ocs_no_occ_m2": 10.12,
      "ocs_with_occ_m2": 8.76,
      "visible_faces_no_occ": 782,
      "visible_faces_with_occ": 658
    },
    "yinshenban": {
      "ocs_no_occ_m2": 1.49,
      "ocs_with_occ_m2": 0.74,
      "visible_faces_no_occ": 118,
      "visible_faces_with_occ": 82
    }
  },
  "magnitude_estimate": {
    "formula_used": "m = m_sun - 2.5*log10(OCS/R^2)",
    "m_sun_V_band": -26.74,
    "m_apparent_V_noatm": 8.12,
    "assumptions": [
      "V-band approximation",
      "no atmospheric extinction",
      "nominal GGX BRDF parameters",
      "STL geometry at 1:1 scale"
    ],
    "caution": "绝对星等估算未经真实观测标定，仅作量级参考"
  },
  "computation_metadata": {
    "brdf_model": "ggx",
    "accuracy_level": "fast",
    "total_faces_before_decimation": 12450,
    "total_faces_after_decimation": 2490,
    "computation_time_seconds": 1.23,
    "code_version": "ocs_project_v1.0_ggx"
  }
}
```

### 4.2 时间序列输出（CSV 格式）

文件命名：`{mission_name}_ocs_timeseries.csv`

```csv
time_utc,label,yaw_deg,pitch_deg,roll_deg,phase_angle_deg,range_km,ocs_no_occ_m2,ocs_with_occ_m2,occlusion_ratio_percent,m_apparent_V_noatm,ocs_jinshuzhuti_m2,ocs_taiyangnengban_m2,ocs_yinshenban_m2
2026-06-15T12:00:00.000Z,t0000,45.0,10.0,0.0,63.4,36000.0,14.82,12.35,16.7,8.12,3.21,10.12,1.49
2026-06-15T12:05:00.000Z,t0001,46.2,10.1,0.0,63.2,36010.0,14.95,12.48,16.5,8.11,3.25,10.18,1.52
```

---

## 5. 距离使用规则

### 5.1 核心原则

**距离 `range_km` 仅用于星等换算后处理，不进入 OCS 积分。**

### 5.2 理由

现有 OCS 代码（`ocs_core.py` 第 78/101 行）计算的是：

```
OCS = Σ_f  A_f · s² · f_r · (N·L) · (N·V)
```

这是一个与距离无关的**几何-材料属性**，量纲为面积（m²）。

星等换算公式（阶段1审计，第 104-113 行）：

```
m = m_sun - 2.5 log10(OCS / R²)
```

距离 `R` 只在星等换算时作为分母出现。

### 5.3 实施建议

1. OCS 积分模块（`ocs_core.compute_single_attitude`）**不接受** `range_km` 参数
2. 星等换算在后处理模块独立完成：

```python
def compute_apparent_magnitude(ocs_m2, range_m, m_sun=-26.74):
    """
    星等换算（V 波段近似，无大气消光）。
    
    参数：
        ocs_m2: OCS 值（m²）
        range_m: 目标-观测站距离（米）
        m_sun: 太阳视星等（V 波段默认 -26.74）
    
    返回：
        m_apparent: 视星等估算
    """
    if ocs_m2 <= 0 or range_m <= 0:
        return None
    return m_sun - 2.5 * np.log10(ocs_m2 / (range_m ** 2))
```

3. 时间序列输出 CSV 中同时记录 `range_km` 和 `m_apparent_V_noatm`，便于追溯

---

## 6. 文件命名规范

### 6.1 单时刻输出

```
{label}_ocs_result.json
```

例如：`GEO_2026_165_1234_ocs_result.json`

### 6.2 时间序列输出

```
{mission_name}_ocs_timeseries.csv
{mission_name}_ocs_timeseries.json
{mission_name}_config_used.json
```

例如：
- `GEO_orbit_track_2026_Q2_ocs_timeseries.csv`
- `GEO_orbit_track_2026_Q2_ocs_timeseries.json`
- `GEO_orbit_track_2026_Q2_config_used.json`

### 6.3 目录结构

**重要**：输出必须写入小项目文件夹，不得写入原大项目 `结果/模块A_重构`（保护规则）。

推荐路径：

```
小项目_卫星光度范围与最亮观测几何/07_阶段4输出_高轨OCS接口/{mission_name}/
├── {mission_name}_ocs_timeseries.csv
├── {mission_name}_ocs_timeseries.json
├── {mission_name}_config_used.json
└── individual_results/
    ├── {label}_ocs_result.json
    ├── ...
```

或简化为：

```
小项目_卫星光度范围与最亮观测几何/结果/{mission_name}/
```

**与原大项目的关系**：
- 可以**只读调用**原大项目代码（`ocs_core.py`, `geometry.py` 等）和 STL 文件
- **不得**向原大项目 `结果/模块A_重构` 写入任何新文件或目录
- 所有输出落在小项目文件夹内

---

## 7. 质量检查清单

### 7.1 输入检查

| 检查项 | 判定准则 | 失败时处理 |
|---|---|---|
| `sun_direction_I` / `det_direction_I` 非零 | `norm > 1e-9` | 拒绝输入，返回错误 |
| `range_km` > 0 | `range_km > 0` | 拒绝输入，返回错误 |
| 相位角合理性 | `0° ≤ phase ≤ 180°` | 警告（但不阻塞） |
| 姿态角范围 | yaw [0,360), pitch [-90,90], roll (-∞,+∞) | 警告（但允许超范围） |
| STL 文件存在 | 文件路径可访问 | 拒绝输入，返回错误 |

### 7.2 输出检查

| 检查项 | 判定准则 | 失败时处理 |
|---|---|---|
| OCS ≥ 0 | `ocs_with_occ_m2 ≥ 0` | 逻辑错误，记录并警告 |
| 遮挡率 ∈ [0, 100] | `0 ≤ occlusion_ratio ≤ 100` | 逻辑错误，记录并警告 |
| OCS(with_occ) ≤ OCS(no_occ) | `ocs_with_occ ≤ ocs_no_occ` | 逻辑错误，记录并警告 |
| 星等有限 | `m_apparent` 不是 NaN/Inf | 若 OCS=0 或 R=0，返回 None |

### 7.3 坐标系一致性检查

| 检查项 | 方法 | 说明 |
|---|---|---|
| 太阳/探测器方向已归一化 | 输出 JSON echo 字段记录归一化后的值 | 避免用户误传未归一化向量 |
| 欧拉角约定一致 | 输出 JSON 记录 `convention: "ZYX_intrinsic"` | 与 `geometry.euler_to_matrix` 保持一致 |
| 相位角自洽 | `phase_angle_deg = arccos(dot(sun_direction_I, det_direction_I))`，其中两向量均**以卫星为起点**（即"卫星→太阳"和"卫星→观测者"） | 若与用户预期不符，提示坐标系定义问题 |

---

## 8. 与阶段1公式审计的衔接

### 8.1 阶段1审计结论回顾

| 项 | 阶段1结论 | 阶段4接口对应 |
|---|---|---|
| **相对星等差可靠** | `Delta m = -2.5 log10(OCS_2/OCS_1)` ✅ | 时间序列 CSV 中 `ocs_with_occ_m2` 列可直接用于计算 Delta m |
| **绝对星等条件可用** | `m = m_sun - 2.5 log10(OCS/R²)` ⚠️ | 输出 JSON `magnitude_estimate` 字段提供估算，但标注 `caution` 和 `assumptions` |
| **距离不进入 OCS 积分** | OCS 是几何-材料属性，与 R 无关 ✅ | `range_km` 仅在后处理星等换算中使用（§5） |
| **BRDF 模型** | GGX 具有明确物理形式 ⚠️ | 输出 JSON `computation_metadata.brdf_model` 记录使用的 BRDF |
| **待确认项 C1-C5** | STL 尺寸、BRDF 参数、波段、m_sun、大气消光 | 输出 JSON `magnitude_estimate.assumptions` 和 `caution` 字段明确列出 |

### 8.2 阶段4新增约束

1. **坐标系明确化**：阶段1未细化坐标系定义，阶段4明确 M（本体）/ I（惯性）及转换规则（§2）
2. **时间序列支持**：阶段1仅审计单姿态公式，阶段4扩展为时间序列离散化（§3.2, §4.2）
3. **输出可追溯性**：阶段4要求输出 JSON echo 输入、记录相位角、归一化方向、计算元数据（§4.1）

### 8.3 待阶段5实施时注意

- 阶段4只设计接口，不写代码
- 阶段5实施时需新建包装脚本（如 `run_high_orbit.py`），调用现有 `ocs_core.compute_single_attitude` 并按本接口格式输入/输出
- 不修改 `ocs_core.py` / `geometry.py` / `config.py` 的核心逻辑，仅在包装层做 I/O 转换

---

## 9. 与现有代码的衔接点

### 9.1 现有代码可直接复用

| 模块 | 文件 | 复用方式 |
|---|---|---|
| 坐标系转换 | `geometry.py :: euler_to_matrix` | 直接调用，输入 yaw/pitch/roll，输出 R |
| OCS 积分 | `ocs_core.py :: compute_single_attitude` | 传入 `(meshes, ray_forest, sun_dir, det_dir, R)` |
| 材料 BRDF | `materials.py :: get_material` + `brdf_models.py :: eval_brdf` | 按 `brdf_model` 参数选择 GGX/LegacyPhong |
| STL 加载 | `geometry.py :: load_meshes` | 传入 `PART_FILES` 字典 |

### 9.2 需新增包装层

```python
# 伪代码示例（不实施）
def process_single_observation(input_json):
    # 1. 解析输入
    sun_I = np.array(input_json["sun_direction_I"])
    det_I = np.array(input_json["det_direction_I"])
    att = input_json["satellite_attitude"]
    R = euler_to_matrix(att["yaw_deg"], att["pitch_deg"], att["roll_deg"])
    
    # 2. 调用现有 OCS 核心
    result = compute_single_attitude(meshes, ray_forest, sun_I, det_I, R)
    
    # 3. 星等换算（后处理）
    range_m = input_json["range_km"] * 1000
    m_app = compute_apparent_magnitude(result["ocs_with_occ"], range_m)
    
    # 4. 组装输出 JSON
    output = {
        "input_echo": {...},
        "ocs_results": result,
        "magnitude_estimate": {"m_apparent_V_noatm": m_app, ...},
        ...
    }
    return output
```

---

## 10. 推荐实施步骤（阶段5参考）

1. **验证坐标系**：用已知姿态（如 yaw=0, pitch=0, roll=0）+ 简单 sun/det 方向，手算预期可见面，与代码输出对比
2. **单时刻测试**：用一个 JSON 输入，验证输出 JSON 格式、字段完整性、星等量级合理性
3. **时间序列测试**：用 3-5 个时刻的模拟轨道数据，验证 CSV 输出、文件命名、追溯性
4. **边界测试**：
   - 相位角接近 0° / 180°（前向散射/后向散射）
   - 姿态极端（pitch=±90°）
   - 距离极值（LEO 500 km / GEO 36,000 km）
5. **与阶段3文献范围做 sanity check**：用典型 GEO 斜距（38,000 km）和相位角（63°），记录计算星等是否接近阶段3调研的 11-15 mag 范围；若偏离，**不直接判定代码错误**，而是检查 STL 尺度、BRDF 参数、精度抽稀、相位角、姿态和星等换算假设（当前 OCS 绝对星等未经真实观测标定，阶段3文献范围不能反过来硬约束仿真结果）

---

## 11. 待 Codex 审阅重点

1. **坐标系是否说清**：M 本体系、I 惯性系、转换约定（§2）
2. **距离是否只进入光度换算**：`range_km` 仅在后处理星等换算中使用，不进入 OCS 积分（§5）
3. **是否能支持多个相位角/时间点**：时间序列 schema（§3.2）和 CSV 输出（§4.2）已设计
4. **输入/输出 schema 是否完备**：字段、单位、必需性、说明（§3, §4）
5. **与阶段1公式审计的一致性**：星等公式、距离使用、待确认项标注（§8）
6. **质量检查清单是否覆盖关键风险**：输入合法性、输出自洽性、坐标系一致性（§7）

---

## 12. 不实施项（明确排除）

- ❌ 不写代码实现
- ❌ 不运行 OCS
- ❌ 不修改原大项目文件（`ocs_core.py` / `geometry.py` / `config.py`）
- ❌ 不做 STK 数据提取（假设输入 JSON 已由外部工具生成）
- ❌ 不做姿态优化搜索（留待阶段5/6）

---

## 13. 附录：术语对照

| 术语 | 英文 | 说明 |
|---|---|---|
| 本体坐标系 | Body Frame (M) | 固连于卫星 STL 的坐标系 |
| 惯性坐标系 | Inertial Frame (I) | 固定参考系（如 ECI J2000） |
| 旋转矩阵 | Rotation Matrix (R) | M→I 的变换矩阵 |
| 欧拉角 | Euler Angles | yaw（偏航）, pitch（俯仰）, roll（滚转） |
| 相位角 | Phase Angle | 太阳-目标-观测者夹角 |
| 视星等 | Apparent Magnitude | 观测者处的亮度（含距离效应） |
| OCS | Optical Cross Section | 光学散射截面（m²） |
| BRDF | Bidirectional Reflectance Distribution Function | 双向反射分布函数（sr⁻¹） |

---

## 14. Codex 审阅后修订记录

修订时间：2026-06-07

### 14.1 必改问题修正

**问题1：方向向量物理含义锁死**

- 新增 §2.3 明确：`sun_direction_I = normalize(r_sun_I - r_sat_I)`（从卫星指向太阳），`det_direction_I = normalize(r_obs_I - r_sat_I)`（从卫星指向观测者）
- 更新 §3.1 字段说明，明确方向向量含义和从位置矢量提取公式
- 理由：现有代码 `ocs_core.py` 通过 `dot(normals_I, sun_norm) > 0` 筛选可见面元，若传入反向向量会导致可见面筛选整体错误

**问题2：输出目录改到小项目内**

- 修正 §6.3，输出路径从原大项目 `结果/模块A_重构/高轨时间序列/` 改为小项目 `小项目_卫星光度范围与最亮观测几何/07_阶段4输出_高轨OCS接口/`
- 明确：可只读调用原大项目代码和 STL，但所有输出必须落在小项目文件夹内
- 理由：遵守项目保护规则，不得向原大项目添加新文件或目录

### 14.2 建议改进已采纳

- **range_km 示例与说明**：改为 38000.0（GEO 典型斜距），字段说明明确"slant range，不是轨道高度"
- **相位角定义与向量绑定**：§7.3 明确相位角公式中两向量均以卫星为起点
- **阶段3范围对照软化**：§10 改为 sanity check，不作为通过/失败标准，偏离时检查假设而非直接判定代码错误
- **输出字段重命名说明**：§4.1 标注 `_m2` / `_percent` 后缀由包装层转换，核心函数返回字段保持不变

### 14.3 修订后阶段5前置要求

阶段5实施前必须锁定：

```
sun_direction_I = 卫星 → 太阳
det_direction_I = 卫星 → 观测者
range_km = 卫星到观测者斜距（不是轨道高度）
所有新增输出写入小项目文件夹，不写入原大项目结果目录
```
