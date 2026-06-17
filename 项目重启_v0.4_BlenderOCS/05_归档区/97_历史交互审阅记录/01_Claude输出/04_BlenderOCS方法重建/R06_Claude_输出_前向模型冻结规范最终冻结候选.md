# 10 v0.4 前向模型冻结规范（最终冻结候选）

生成时间：2026-06-08
修订基准：Codex 复审意见 CR4-001 ～ CR4-008（`09_Codex复审意见_前向模型冻结规范修订版.md`）
上版文件：`07_v0.4前向模型冻结规范_Claude修订版.md`（已由本最终冻结候选版取代）

---

## 一、v0.4 前向模型总图（CR4-001 已修正）

```text
           同一 STL 几何 + 同一姿态 (yaw, pitch)
           同一太阳/观测方向向量 (sun_dir, det_dir)
                          │
         ┌────────────────┴────────────────┐
         │                                 │
    Blender Cycles                    Python 公式
    (geometry pass only)              (explicit BRDF + OCS)
         │                                 │
    正交投影相机                      GGX/Cook-Torrance BRDF
    depth / normal / IndexOB           f_r(N, L, V; material_params)
    Position / WorldCoord                    │
    pixel-level visibility            ┌─────┴─────┐
         │                            │           │
    Sun Shadow Pass               OCS 积分      图像线性响应
    (shadow_mapping_method)   Σ A_pix·f_r·NoL·  I_linear(p) = f_r(p)·
         │                     V_sun_macro      NoL(p)·V_sun_macro(p)
         │                    per-part + total   (per pixel)
         │                         │           │
         └─────────┬───────────────┘           │
                   │                    log1p 变换 + 8-bit PNG
           Blender-derived                     │
           OCS manifest                  训练输入
           (canonical OCS)              (image-only / fusion)
                   │
        ┌──────────┼──────────┐
        │          │          │
   OCS-only    fusion    image-only
   (MLP)      (concat5)   (ResNet-18)
```

**一句话总结**（CR4-001 修正）：OCS 和图像线性响应均含 `V_sun_macro`，来自同一统一前向物理模型。若 visibility 降级为 `camera_visible_nol`，则 `V_sun_macro ≡ 1`，自然退化回旧公式。

**与旧版（07_Claude修订版）的关键差异**：
- 总图中图像线性响应从 `I_linear = f_r·NoL` 改为 `I_linear = f_r·NoL·V_sun_macro`
- Blender 分工新增 Position/WorldCoord pass 和 Sun Shadow Pass

---

## 二、Blender / Python / 反演代码分工

### 2.1 Blender 负责（geometry pass + sun shadow pass）

| 职责 | 说明 |
|---|---|
| STL 导入与姿态变换 | 三部件（jinshuzhuti / taiyangnengban / yinshenban）统一管理 |
| 正交投影相机（camera-view） | ortho_scale = 2.2 × r_max（r_max 为几何包围球半径）；分辨率 256×256 |
| depth pass | 像素级相机可见性判定（depth < 1e9 → object pixel） |
| normal pass | 逐像素世界坐标法线（N_world，未归一化，需 Python 端归一化） |
| IndexOB pass | 部件分区：0=背景, 1=jinshuzhuti, 2=taiyangnengban, 3=yinshenban |
| **Position/WorldCoord pass**（CR4-002 新增） | 逐像素世界坐标（用于 sun shadow reprojection） |
| **Sun Shadow Pass**（CR4-002 新增） | 见 §6 可执行定义 |
| 视角可见性（camera visibility） | 光栅化 depth-buffer 自然处理：被其他部件或自身背面遮挡的面元不出现在像素中 |

**Blender 不做的事**：
- 不使用 Blender Principled BSDF / Combined pass 作为最终亮度模型
- 不依赖 Blender shading normal 的自动翻转行为
- 不使用 Backfacing AOV 作为 OCS 积分判据

### 2.2 Python 公式负责

| 职责 | 说明 |
|---|---|
| GGX/Cook-Torrance BRDF | `f_r = f_diffuse + f_specular`，参数来自 `materials.py` 的 `_GGX_DB` |
| NoL / NoV / NoH 几何项 | 显式计算，`NoL = max(dot(N, L), 0)`, `NoV = max(dot(N, V), 0)` |
| V_sun_macro 计算 | 从 camera-view pixel → world point → sun-view depth comparison 得到（见 §6.3） |
| OCS 积分 | `OCS = Σ A_pix · f_r · NoL · V_sun_macro`（见 §5） |
| per-part OCS | 按 IndexOB 分区累计 |
| **图像线性响应**（CR4-001 修正） | `I_linear(p) = f_r(p) · NoL(p) · V_sun_macro(p)` |
| log1p 变换与 PNG 输出 | 见 §7 |
| 退化模型 | noise/blur/downsample/background/starfield 均为后处理压力测试 |

### 2.3 反演代码负责

| 职责 | 说明 |
|---|---|
| OCS 特征构建 | 从 OCS manifest 读取 per-part OCS → per_part_log 30D 特征 |
| 图像加载与预处理 | PNG → 反量化 → 网络输入（PNG 本身已是 log1p 编码） |
| 模型训练 | OCS MLP / ResNet-18 image-only / fusion (concat5 late fusion) |
| 实验结果汇总 | 所有对比实验、补充实验、退化实验从同一 manifest 和 split 文件读取 |

---

## 三、坐标系与姿态定义

### 3.1 世界坐标系

- 右手系
- Blender 默认：+Z 为 up，+Y 为 front
- Python 端与 Blender 端使用同一世界坐标系

### 3.2 姿态定义

- **姿态参数**：(yaw, pitch)，roll ≡ 0
- **旋转顺序**：Z-Y-X 内旋：`R = Rz(yaw) · Ry(pitch) · Rx(0)`

**Yaw 网格**：

| 用途 | 网格 | 数量 | 说明 |
|---|---|---|---|
| **训练/反演/OCS manifest** | yaw ∈ [0°, 355°]，步长 5° | **72 个唯一值** | 0° 和 360° 是同一姿态，不在训练集中重复 |
| **绘图 heatmap seam** | yaw ∈ [0°, 360°]，步长 5° | 73 个值（0° 复制为 360°） | 仅用于可视化，使 heatmap 在 0°/360° 处自然闭合 |

**Pitch 网格**：[-90°, 90°]，步长 5°，共 37 个值。

**总训练姿态数**：72 × 37 = **2664**（不含 360° 重复）。

**姿态正方向**：
- yaw：从 +Z（up）轴向原点看，逆时针为正
- pitch：从 +Y（front）轴向原点看，绕 +X 旋转，目标"抬头"为正

### 3.3 太阳/观测方向

- `sun_dir` 和 `det_dir` 在世界坐标中定义，使用前归一化为单位向量
- 多观测几何（multi-geom）：5 组 sun/det 配置，相位角覆盖 24°~120°
- 单观测几何（single-geom/phase63）：1 组 sun/det，相位角 63°

**归一化要求**：所有方向向量在 BRDF 计算前均须归一化为单位向量。

### 3.4 法线坐标系

- Blender EXR Normal pass 输出**世界坐标法线**
- Python 端读取后显式归一化：`N_world = N_world / ||N_world||`

---

## 四、Geometry Pass 字段（CR4-002 新增 Position/WorldCoord）

### 4.1 每个 camera-view EXR 帧包含

| 字段 | 通道 | 数据类型 | 含义 |
|---|---|---|---|
| Normal | (R, G, B) = (X, Y, Z) | float32 | 世界坐标表面法线 |
| Depth | V（单通道） | float32 | Blender 默认 1e10 = 无穷远；depth < 1e9 为物体像素 |
| IndexOB | V（单通道） | int32 | 0=背景, 1=jinshuzhuti, 2=taiyangnengban, 3=yinshenban |
| **Position** | **(R, G, B) = (X, Y, Z)**（CR4-002 新增） | **float32** | **逐像素世界坐标，正交投影下由 depth 反投影得到。若 Blender 不支持直接输出 Position AOV，则在 Python 端由 depth + camera 矩阵重建（见 §6.5）** |
| Backfacing | R（单通道，AOV） | float32 | 0.0=正面, 1.0=背面（仅用于 sanity check） |

### 4.2 Camera Visibility Mask 定义

```
camera_visible_pixel := (Depth < 1e9) AND (IndexOB > 0)
```

---

## 五、OCS 积分定义

### 5.1 连续形式

```
OCS = ∫_{S_visible} f_r(ω_i, ω_o, N(x)) · cos(θ_i) · V_sun_macro(x) · dA_projected
```

其中：
- `S_visible`：相机可见的目标表面（camera-visible pixels）
- `f_r`：GGX/Cook-Torrance BRDF（见 §8）
- `cos(θ_i) = NoL = max(n·sun, 0)`
- `V_sun_macro(x)`：宏观太阳方向可见性乘子 ∈ {0, 1}
- `dA_projected`：面元在像平面上的投影面积（正交投影下为常数 pixel_area）

### 5.2 像素离散形式（正交投影）—— CR4-001 联动，图像同步

**OCS 离散公式**：

```
OCS = Σ_{p ∈ visible} A_pix · f_r(p) · NoL(p) · V_sun_macro(p)
```

**图像线性响应**（CR4-001 修正——与 OCS 同源）：

```
I_linear(p) = f_r(p) · NoL(p) · V_sun_macro(p)
```

**一致性声明**（CR4-001 关）：OCS 积分和图像线性响应使用完全相同的 `f_r(p)`、`NoL(p)`、`V_sun_macro(p)`。若 visibility 降级为 `camera_visible_nol`，则 `V_sun_macro ≡ 1`，两者同步退化。

其中：
- `A_pix = (ortho_scale / resolution)²`（常数，正交换算，单位 m²）
- `f_r(p)` = GGX/Cook-Torrance BRDF 值（标量）
- `NoL(p) = max(N(p) · L, 0)`
- `V_sun_macro(p) ∈ {0, 1}` 见 §6

### 5.3 NoV 抵消的成立条件

1. **正交投影**：所有像素的 `A_pix` 为同一常数
2. **NoV > 0**：NoV ≤ 0 的像素 OCS 贡献显式为 0（见 §5.4）
3. **无 fractional coverage**：假设像素全部覆盖目标（边缘像素见 §5.5）

### 5.4 NoL/NoV 边界条件

| 条件 | 处置 | 原因 |
|---|---|---|
| NoV ≤ 0 | 像素 f_r = 0, I_linear = 0, OCS contribution = 0 | 该像素为背面/切面，BRDF 分母含 NoV |
| NoL ≤ 0 | 像素 f_r = 0, I_linear = 0, OCS contribution = 0 | 太阳在表面背后，该处不被照亮 |

### 5.5 A_pix 定义与边缘像素处理

```
A_pix = (ortho_scale / resolution)²
```

其中 `ortho_scale = 2.2 × r_max`。

**边缘像素 fractional coverage**：
- 目标边缘的像素仅部分覆盖目标表面，其余为背景
- v0.4 不做 fractional coverage 修正，接受为已知舍入误差
- 方法文件中记录此简化假设

---

## 六、Sun-Side Visibility / Self-Shadow（CR4-002 可执行定义）

### 6.1 导航：三种可见性层次

| 层次 | 名称 | enum 值 | 含义 |
|---|---|---|---|
| Level 1 | Camera-visible + NoL | `camera_visible_nol` | 像素对相机可见，且 `NoL > 0` 时有贡献（`NoL ≤ 0` 贡献归零）。`V_sun_macro ≡ 1` |
| Level 2 | + Blender sun shadow reprojection | `camera_visible_nol_plus_sun_shadow_pass` | Level 1 + camera-view pixel → world point → sun-view depth comparison → V_sun_macro ∈ {0,1} |
| Level 3 | + Python ray-cast | `camera_visible_nol_plus_python_raycast` | Level 1 + Python trimesh+Embree ray-cast 逐像素判定 sun-ray 遮挡 |

### 6.2 冻结决策：主线使用 Level 2

**v0.4 主线优先实现 `camera_visible_nol_plus_sun_shadow_pass`**。

**降级预案**：
1. 先用 20 个代表姿态做小规模验证（见 §10.6）
2. 如果 Blender sun shadow reprojection 在技术上不可行，降级为 `camera_visible_nol`
3. 降级时必须：论文写作边界显式声明未实现 sun-side self-shadow

### 6.3 Sun Shadow Pass 可执行数据流（CR4-002 修正——从概念描述改为可落地数据流）

**推荐主线方案 A：camera-view Position + sun-view depth reprojection**

```
Step 1：Blender camera-view 渲染
  输出：depth (H×W), normal (H×W×3), IndexOB (H×W),
        world_position (H×W×3, 由 depth + camera 矩阵重建，见 §6.5)
  已知：camera_matrix_world (Blender 相机世界变换矩阵)
         ortho_scale_m, resolution

Step 2：Blender sun-view 渲染（同一姿态、同一几何、同一 ortho_scale）
  相机旋转矩阵替换为 look_at(sun_dir)，正交投影参数不变
  输出：sun_depth (H×W)
  已知：sun_camera_matrix_world

Step 3：Python 端 sun shadow reprojection
  FOR each camera-visible pixel p:
    P_world = world_position[p]                         ← camera-view 3D 世界点
    P_sun_cam = sun_camera_matrix_world · P_world       ← 变换到 sun-view 相机空间
    (u_sun, v_sun) = project_ortho(P_sun_cam, ortho_scale, resolution)
    sun_depth_reproj = P_sun_cam.z                       ← 该世界点在 sun-view 中的深度
    sun_depth_actual = bilinear_sample(sun_depth, u_sun, v_sun)
    V_sun_macro[p] = (sun_depth_reproj <= sun_depth_actual + depth_epsilon)
  END FOR

Step 4：输出
  V_sun_macro_mask (H×W, uint8, 0/1)，与 camera-view 像素对齐
  写入 manifest 的 sun_visibility_mask_path
```

**备选方案 B：Blender 同相机视角 Shadow AOV**

如果 Blender 支持同一 camera-view 渲染时直接输出 Shadow AOV（在 camera-view 相机内部计算 sun light shadow），则不需要 reprojection。但需要验证：
- Blender Cycles Shadow AOV 是否与 camera-view 像素对齐
- 阴影判断是否与几何可见性一致（非材质光照）

**方案选择**：先尝试方案 A（reprojection），因为已有 `brdf_postprocess.py` 的 EXR 读取基础设施。如果 Sun Shadow AOV 更简单可靠，改为方案 B。

**实现优先级顺序**：
1. 先在 camera-view 渲染中尝试输出 Position/WorldCoord pass（Blender AOV 支持）
2. 如果 Blender 不支持 Position AOV，在 Python 端由 depth + camera 矩阵反投影
3. Sun-view 渲染 depth EXR（与 camera-view 相同 ortho_scale/resolution）
4. Python reprojection 生成 V_sun_macro_mask

### 6.4 反投影公式（备查）

如果 Blender 不支持直接输出 Position AOV，Python 端重建方式：

```
# 正交投影相机
x_ndc = (2 * u / resolution - 1)    # u ∈ [0, resolution-1]
y_ndc = (2 * v / resolution - 1)
# Blender ortho: z_ndc = 2 * depth / ortho_scale（需确认 Blender ortho depth 编码）

P_cam = (x_ndc * ortho_scale / 2, y_ndc * ortho_scale / 2, depth)
P_world = camera_matrix_world.inverse() · P_cam   # 从相机空间到世界空间
```

### 6.5 Depth Epsilon 设定

- `depth_epsilon_m = 1e-3` m（初始值，等价于 ~0.03% 像素尺度）
- 在 20 姿态验证中校准：确保 V_sun_macro 不因数值精度而错误标记
- 写入 manifest 字段 `depth_epsilon_m`

### 6.6 OCS 公式中的 V_sun_macro

在 baseline（未实现 sun shadow）下所有像素 `V_sun_macro ≡ 1`，公式退化为 `OCS = Σ A_pix · f_r · NoL`。sun shadow 实现后，`V_sun_macro` 从 sun shadow reprojection 得到。

---

## 七、Clean Image 线性响应与 log1p/PNG/训练输入（CR4-001 联动修正）

### 7.1 旧链问题确认

旧链存在编码不一致：写入端 gamma 2.2 PNG，读取端 /255 后叠加 log1p，实际经历了 gamma 2.2 + log1p 双重非线性。

### 7.2 v0.4 统一图像响应链（CR4-001 修正——加入 V_sun_macro）

**Step 1：线性辐亮度生成**
```
I_linear(p) = f_r(p) · NoL(p) · V_sun_macro(p)    [per pixel]
```
若 visibility 降级为 `camera_visible_nol`，则 `V_sun_macro(p) ≡ 1`。

**Step 2：全局归一化**
```
I_norm(p) = I_linear(p) / I_scale
```
- `I_scale` = v0.4 clean corpus 全局最大 I_linear 值
- `I_norm ∈ [0, 1]`

**Step 3：log1p 变换**
```
I_log(p) = log1p(α · I_norm(p)) / log1p(α)
```
- `α = 10.0` 作为初始默认值
- 正式全链路重跑前做 quick ablation（候选 α ∈ {5, 10, 20} + raw）

**Step 4：8-bit PNG 存储（训练输入）**
```
PNG(p) = clip(round(I_log(p) · 255), 0, 255)
```

**Step 5：训练时加载**
```python
arr = np.asarray(img, dtype=np.float32) / 255.0    # → I_log ∈ [0, 1]
```

**Step 6：退化实验的作用域**
- 噪声/模糊等退化在**线性空间**（I_linear）施加

### 7.3 原始线性辐亮度数据保留

- **保留 linear EXR（float32）作为 canonical raw data**
- 每次 brdf_postprocess 输出：
  - `{key}_linear.exr`：I_linear per pixel（浮点，lossless）
  - `{key}_brdf.png`：I_log 8-bit PNG（训练输入）

---

## 八、GGX/Cook-Torrance BRDF 主模型（CR4-004 数值 eps 规则）

### 8.1 模型公式

```
f_r(N, L, V) = f_diffuse + f_specular

f_diffuse = (base_color / π) · (1 - metallic) · (1 - F0)

f_specular = D_GGX(N, H, roughness) · G_Smith(N, L, V, roughness) · F_Schlick(H, V, F0)
             ─────────────────────────────────────────────────────────────────────────
                                        4 · NoL · NoV
```

### 8.2 有效像素判定规则（CR4-004 修正——防除零/NaN）

**有效像素必须同时满足**：
```
NoV > eps   AND   NoL > eps
```

其中 `eps = 1e-6`（写入 `brdf_version` 说明）。

**无效像素处置**：
```
f_r = 0
I_linear = 0
OCS contribution = 0
```

**计算顺序**：
1. 先判定 `NoV > eps` 且 `NoL > eps`，过滤有效像素
2. 对有效像素计算 `f_r = f_diffuse + f_specular`
3. 再计算 `I_linear = f_r · NoL · V_sun_macro`
4. OCS = Σ A_pix · I_linear

**禁止**：先计算 `f_specular` 再检查 `NoL > eps`（分母 `4·NoL·NoV` 会在 NoL=0 或 NoV=0 时产生 inf/NaN）。

### 8.3 材料参数（与 `_GGX_DB` 一致）

| 参数 | jinshuzhuti | taiyangnengban | yinshenban |
|---|---|---|---|
| base_color | 0.91 | 0.15 | 0.08 |
| metallic | 1.0 | 0.0 | 0.0 |
| roughness | 0.20 | 0.40 | 0.90 |
| F0 | 0.91 | — | — |
| ior | — | 1.5 | 1.5 |

`base_color` 为标量（灰度 BRDF）。以上为 nominal synthetic parameters。

### 8.4 LegacyPhong 的处理

- LegacyPhong **不作为** v0.4 主线 BRDF
- 不作为 v0.4 主线必做项
- 保留 `eval_legacy_phong()` 函数

---

## 九、术语区分

| 术语 | 推荐英文 | 尺度 |
|---|---|---|
| Microfacet shadowing-masking | **G-term** 或 **microfacet shadowing-masking (G_Smith)** | 微表面 |
| Macro geometric occlusion | **Camera-viewer-side visibility** | 宏观几何 |
| Sun-side self-shadow | **Sun-side self-shadow** 或 **V_sun_macro** | 宏观几何 |

---

## 十、Single-Geom 主线与 Multi-Geom 扩展的可见性一致性（CR4-005 修正）

### 10.1 一致性要求

**主线 single-geom（phase63）**：
- camera geometry pass → sun shadow pass → BRDF 后处理 → OCS/integration → manifest
- image 线性响应同样使用 `V_sun_macro(phase63)`
- 公平基线

**扩展 multi-geom（concat5, 其余 4 组 sun/det）**：
- **每个 geom** 都必须生成完整的 camera geometry pass + sun shadow pass + BRDF/OCS 后处理（CR4-005 修正——不能只给 phase63 做 shadow）
- image 侧仍只用 phase63（固定观测几何，作为 fusion 多几何增强的设定）
- 如果 multi-geom 采用 Level 2 visibility，则 5 组 geom 各有一致的 sun shadow 产物

### 10.2 禁止的不一致

- ❌ single-geom 使用 Level 2，某 multi-geom 使用 Level 1
- ❌ multi-geom 中只有 phase63 有 sun shadow pass，其余 4 组没有
- ❌ OCS concat5 混合使用不同 visibility 层级的 per-geom OCS

---

## 十一、必须做的 Sanity Checks

### 11.1 坐标系与向量审计（3 姿态）

选取 (0°, 0°), (90°, -45°), (150°, -80°)，验证法线方向、sun/det 向量一致性、可见像素数合理性。

### 11.2 薄板 Depth-Buffer 审计

选取 yaw=90°, pitch=-40°，检查太阳能板边缘 depth 连续性。

### 11.3 非水密 STL Depth 行为

3 个关键姿态检查部件边界 depth 连续性。

### 11.4 Per-Part OCS 比例与旧 OCS 差异审计

生成新旧 OCS per-part per-attitude 差异表，标记异常差异。

### 11.5 log1p α 参数确认

用 v0.4 clean corpus 做 quick ablation：α ∈ {5, 10, 20} + raw。

### 11.6 Sun Shadow Pass 20 姿态验证（CR4-002 可执行验证）

选 20 个代表姿态覆盖以下类别：
- 高遮挡姿态（部件互相遮蔽，如 yaw≈90° pitch 极端）
- 低遮挡姿态（部件分离，如 yaw≈0° pitch≈0°）
- 边缘姿态（|pitch| > 75°）
- 典型训练姿态（phase63）

验证项目：
1. Sun-view EXR 渲染成功，depth 数据完整
2. World position 重建正确（与已知 geometry 比对）
3. Camera-view → sun-view reprojection 坐标正确
4. Depth comparison 产生的 V_sun_macro_mask 物理合理
5. 与 `camera_visible_nol` 的 OCS 差异可解释（sun-shadowed 像素 OCS 减少量合理）
6. `depth_epsilon` 不会导致边缘像素误判

如果任一验证失败，根据失败模式降级为 `camera_visible_nol`，并记录降级原因。

### 11.7 V_sun_macro 对图像的影响验证

选 5 个姿态，生成含 V_sun_macro 和不含 V_sun_macro 的 I_linear 对比，确认 sun-shadowed 像素亮度正确归零，且线性 EXR 和 log1p PNG 同步。

---

## 十二、写作边界

1. **Synthetic forward model only**：无真实望远镜图像、无真实大气链路、无真实探测器标定。
2. **No real telescope validation**：不声称 field-proven robustness。
3. **Nominal material parameters**：材料参数为名义合成值。
4. **Sun-side visibility 声明**：
   - 如果 sun shadow pass 实现成功：写 "sun-side self-shadowing is explicitly modeled via Blender shadow pass reprojection"
   - 如果降级：写 "visibility is defined by camera-viewer-side depth-buffer; sun-side self-shadowing is not explicitly modeled and is left for future work"
5. **Observation-consistent, not observation**。
6. **No inter-satellite occlusion**：仅建模单目标自身遮挡。
7. **OCS 与图像必须同源**：论文中 OCS 和图像数据必须来自同一 `V_sun_macro` 层级。

---

## 十三、已收回的 D1-D8 决策表

| # | 问题 | 冻结决策 |
|---|---|---|
| D1 | sun-side visibility | 主线优先实现 Level 2（Blender sun shadow reprojection）；20 姿态验证；降级预案为 camera_visible_nol |
| D2 | 单几何 vs 多几何 | 主表含 single-geometry OCS/image/fusion 公平基线；multi-geometry concat5 单独报告 |
| D3 | log1p α | α=10 初始；quick ablation α∈{5,10,20}+raw |
| D4 | I_scale | 使用 v0.4 clean corpus 全局最大值 |
| D5 | LegacyPhong | 不作为 v0.4 主线必做项 |
| D6 | 材料敏感性 | 主实验后 ±20% roughness/F0 敏感性 |
| D7 | 分辨率 ablation | 128/256/512 sanity check |
| D8 | split 策略 | 主结果 coarse-to-fine 插值 split |

---

## 十四、与 Codex CR4 修正项对应关系

| CR4 编号 | 严重度 | 修正内容 | 本文件对应章节 |
|---|---|---|---|
| CR4-001 | P0 | 图像线性响应加入 V_sun_macro：`I_linear(p) = f_r(p)·NoL(p)·V_sun_macro(p)` | §1（总图）, §5.2, §7.2 |
| CR4-002 | P0 | Sun shadow pass 从概念描述改为可执行数据流：camera-view Position + sun-view depth reprojection | §4.1（新增 Position pass）, §6.3（完整数据流）, §11.6 |
| CR4-003 | P0 | （配套见文件 11）manifest 增加 shadow pass 路径和重投影参数 | 数据规范文件 §2.1, §9.2 |
| CR4-004 | P1 | GGX 有效像素判据：`NoV > eps` 且 `NoL > eps`，eps=1e-6 | §8.2 |
| CR4-005 | P1 | Multi-geom 每 geom 都要有 sun shadow pass + BRDF 后处理 | §10.1 |
| CR4-006 | P1 | （配套见文件 11）record_id + 像素统计拆分 | 数据规范文件 §2.1 |
| CR4-007 | P2 | （配套见文件 11）删除 seed 具体数字，修正 split_id 示例 | 数据规范文件 §5 |
| CR4-008 | P2 | （配套见文件 11）method_version 汇总标签改为带字段名短格式 | 数据规范文件 §3.2 |

**CR3 遗留状态**：
- CR3-007（已关闭但需联动）：图像链已同步 V_sun_macro（见 CR4-001）
- CR3-008（部分关闭）：multi-geom 的 shadow/BRDF 生成范围已补全（见 CR4-005）
- CR3-011（部分关闭）：seed 示例已全部清除（见 CR4-007）

---

## 十五、提交 Codex 最终复审清单

**本文件需与 `11_v0.4数据与manifest字段规范_最终冻结候选.md` 一并提交最终复审。**

### 15.1 提交文件

```
04_BlenderOCS方法重建/10_v0.4前向模型冻结规范_最终冻结候选.md  ← 本文件
04_BlenderOCS方法重建/11_v0.4数据与manifest字段规范_最终冻结候选.md  ← 配套文件
```

### 15.2 需要 Codex 重点审阅

| 优先级 | 章节 | 审阅要点 |
|---|---|---|
| P0 | §1（总图） | OCS 与图像是否均含 V_sun_macro |
| P0 | §5.2（OCS/图像公式） | V_sun_macro 是否一致出现在两处 |
| P0 | §6.3（sun shadow 数据流） | reprojection 数据流是否真正可执行、无隐藏假设 |
| P0 | §4.1（Position pass） | 世界坐标获取方式是否明确 |
| P1 | §8.2（GGX eps 规则） | 有效像素判据是否防除零 |
| P1 | §10.1（multi-geom 一致性） | CR4-005 是否完整收回 |
| P1 | §14（CR4 对应表） | 所有 CR4-001 至 CR4-008 是否逐条收回 |

### 15.3 Codex 审阅后下一步

若 P0/P1 全部收回，进入代码阶段：`05_全链路重跑/00_重跑任务清单.md`。
