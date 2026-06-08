# 07 v0.4 前向模型冻结规范（Claude 修订版）

生成时间：2026-06-08
修订基准：Codex 复审意见 CR3-001 ～ CR3-011（`06_Codex复审意见_前向模型冻结规范.md`）
上版文件：`04_v0.4前向模型冻结规范_Claude.md`（已由本修订版取代）

---

## 一、v0.4 前向模型总图

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
    pixel-level visibility                  │
         │                            ┌─────┴─────┐
    每帧 EXR 输出                    │           │
    (不含材质亮度)              OCS 积分      图像线性响应
         │               Σ A_pix·f_r·NoL·V_sun  I_linear = f_r·NoL
         │               per-part + total      (per pixel)
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

**一句话总结**：Blender 负责几何采样（"看见哪里"），Python 负责物理散射（"如何反光"），反演代码负责特征组织与模型训练。OCS 和图像来自同一前向模型。

---

## 二、Blender / Python / 反演代码分工

### 2.1 Blender 负责（geometry pass only）

| 职责 | 说明 |
|---|---|
| STL 导入与姿态变换 | 三部件（jinshuzhuti / taiyangnengban / yinshenban）统一管理 |
| 正交投影相机 | ortho_scale = 2.2 × r_max（r_max 为几何包围球半径）；分辨率 256×256 |
| depth pass | 像素级相机可见性判定（depth < 1e9 → object pixel） |
| normal pass | 逐像素世界坐标法线（N_world，未归一化，需 Python 端归一化） |
| IndexOB pass | 部件分区：0=背景, 1=jinshuzhuti, 2=taiyangnengban, 3=yinshenban |
| 视角可见性（camera visibility） | 光栅化 depth-buffer 自然处理：被其他部件或自身背面遮挡的面元不出现在像素中 |
| sun shadow pass（v0.4 主线） | 额外 sun-view 渲染，输出 per-pixel sun-ray visibility flag（见 §6） |

**Blender 不做的事**：
- 不使用 Blender Principled BSDF / Combined pass 作为最终亮度模型
- 不依赖 Blender shading normal 的自动翻转行为
- 不使用 Backfacing AOV 作为 OCS 积分判据

### 2.2 Python 公式负责

| 职责 | 说明 |
|---|---|
| GGX/Cook-Torrance BRDF | `f_r = f_diffuse + f_specular`，参数来自 `materials.py` 的 `_GGX_DB` |
| NoL / NoV / NoH 几何项 | 显式计算，`NoL = max(dot(N, L), 0)`, `NoV = max(dot(N, V), 0)` |
| OCS 积分 | `OCS = Σ A_pix · f_r · NoL · V_sun_macro`（见 §5） |
| per-part OCS | 按 IndexOB 分区累计 |
| 图像线性响应 | `I_linear = f_r · NoL`（per pixel，不含 A_pix） |
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

**Yaw 网格**（CR3-002 已修正）：

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

**归一化要求**：所有方向向量（sun_dir, det_dir, sun_dir per geom）在 BRDF 计算前均须归一化为单位向量。`ocs_core.py` 和 `brdf_postprocess.py` 均需调用 `vector /= np.linalg.norm(vector)`。

### 3.4 法线坐标系

- Blender EXR Normal pass 输出**世界坐标法线**（已在旧 `brdf_postprocess.py` 中确认）
- Python 端读取后显式归一化：`N_world = N_world / ||N_world||`（防数值漂移）

---

## 四、Geometry Pass 字段

### 4.1 每个 EXR 帧包含

| 字段 | 通道 | 数据类型 | 含义 |
|---|---|---|---|
| Normal | (R, G, B) = (X, Y, Z) | float32 | 世界坐标表面法线 |
| Depth | V（单通道） | float32 | Blender 默认 1e10 = 无穷远；depth < 1e9 为物体像素 |
| IndexOB | V（单通道） | int32 | 0=背景, 1=jinshuzhuti, 2=taiyangnengban, 3=yinshenban |
| Backfacing | R（单通道，AOV） | float32 | 0.0=正面, 1.0=背面（仅用于 sanity check，不进入 OCS 积分逻辑） |
| SunShadow（v0.4 主线新增） | V（单通道） | float32 | 0.0=sun-occluded, 1.0=sun-visible；baseline（未实现 sun shadow 时）全为 1.0 |

### 4.2 Camera Visibility Mask 定义

```
camera_visible_pixel := (Depth < 1e9) AND (IndexOB > 0)
```

**注意**：Backfacing AOV 对封闭网格外视图始终为 0（已确认）。不依赖 Backfacing AOV 做运行时背面过滤。

---

## 五、OCS 积分定义

### 5.1 连续形式

```
OCS = ∫_{S_visible} f_r(ω_i, ω_o, N(x)) · cos(θ_i) · V_sun_macro(x) · dA_projected
```

其中：
- `S_visible`：相机可见的目标表面（camera-visible pixels，见 §4.2）
- `f_r`：GGX/Cook-Torrance BRDF（见 §8）
- `cos(θ_i) = NoL = max(n·sun, 0)`
- `V_sun_macro(x)`：宏观太阳方向可见性乘子（CR3-007）
  - baseline（未实现 sun shadow）：`V_sun_macro ≡ 1`
  - sun shadow pass 实现后：`V_sun_macro ∈ {0, 1}`（0 = 太阳方向被遮挡）
- `dA_projected`：面元在像平面上的投影面积（正交投影下为常数 pixel_area）

### 5.2 像素离散形式（正交投影）

正交投影下，面元表面积 `dA` 与投影像素面积 `dA_projected` 的关系：

```
dA_projected = dA · |cos(θ_o)| = dA · NoV
⇒ dA = dA_projected / NoV
```

代入 OCS 连续定义：

```
OCS = ∫ f_r · NoL · V_sun_macro · dA_projected
    = ∫ f_r · NoL · V_sun_macro · (NoV · dA)
    = ∫ f_r · NoL · V_sun_macro · dA_projected        [NoV 不出现]
```

最终像素离散公式（**v0.4 使用**）：

```
OCS = Σ_{p ∈ visible} A_pix · f_r(p) · NoL(p) · V_sun_macro(p)
```

其中：
- `A_pix = (ortho_scale / resolution)²`（常数，正交换算，单位 m²）
- `f_r(p)` = GGX/Cook-Torrance BRDF 值（标量）
- `NoL(p) = max(N(p) · L, 0)`
- `V_sun_macro(p) ∈ {0, 1}` 见 §6

### 5.3 NoV 抵消的成立条件

1. **正交投影**：所有像素的 `A_pix` 为同一常数（不需要逐像素的 NoV 除法）
2. **NoV > 0**：NoV ≤ 0 的像素 OCS 贡献显式为 0（见 §5.4）
3. **无 fractional coverage**：假设像素全部覆盖目标（边缘像素见 §5.5）

### 5.4 NoL/NoV 边界条件

| 条件 | 处置 | 原因 |
|---|---|---|
| NoV ≤ 0 | 像素 OCS 贡献 = 0，f_r = 0 | 该像素为背面/切面，BRDF 公式中分母含 NoV |
| NoL ≤ 0 | 像素 OCS 贡献 = 0（通过 `NoL = max(n·sun, 0)` 自然归零） | 太阳在表面背后，该处不被照亮 |

**实现方式**：在 `compute_radiance_image()` 中，先用 `NoV > 0` 过滤像素，再对保留的像素计算 `NoL = max(n·sun, 0)` 和 `f_r`。不依赖 Blender Cycles 的 shading normal 自动翻转行为。

### 5.5 A_pix 定义与边缘像素处理

**A_pix 定义**：

```
A_pix = (ortho_scale / resolution)²
```

其中 `ortho_scale = 2.2 × r_max`。
- 例：r_max ≈ 1.473 m，ortho_scale = 3.24 m，resolution = 256 → A_pix = (3.24/256)² = 1.6015×10⁻⁴ m²

**边缘像素 fractional coverage**：
- 目标边缘的像素仅部分覆盖目标表面，其余为背景
- v0.4 不做 fractional coverage 修正，接受为已知舍入误差
- 估计误差：256×256 分辨率边缘像素占比约 1.6%，总 OCS 影响 < 2%
- 方法文件中记录此简化假设

---

## 六、Sun-Side Visibility / Self-Shadow（冻结决策）

### 6.1 导航：三种可见性/贡献层次

为避免命名混淆（CR3-003），v0.4 将 sun-side visibility 拆分为三个递进层次：

| 层次 | 名称 | enum 值 | 含义 |
|---|---|---|---|
| Level 1 | Camera-visible + NoL | `camera_visible_nol` | 像素对相机可见，且 `NoL > 0` 时有贡献（`NoL ≤ 0` 贡献归零） |
| Level 2 | + Blender sun shadow pass | `camera_visible_nol_plus_sun_shadow_pass` | Level 1 + Blender 额外 shadow pass 逐像素判定 sun-ray 是否被几何遮挡 |
| Level 3 | + Python ray-cast | `camera_visible_nol_plus_python_raycast` | Level 1 + Python trimesh+Embree ray-cast 逐像素判定 sun-ray 遮挡 |

**关键澄清**：Level 1 不是"不考虑太阳方向"——`NoL ≤ 0` 的像素贡献已被置零。它只是不额外判定 sun-ray 是否被其他部件遮挡。

### 6.2 冻结决策：主线使用 Level 2（Blender sun shadow pass）

**决策**（CR3-004 收回）：**v0.4 主线优先实现 `camera_visible_nol_plus_sun_shadow_pass`**。

理由：
- v0.4 重启的核心目标是统一前向物理模型，sun-side self-shadow 是其中一部分
- Blender shadow pass 与 geometry pass 同源（同一场景、同一精度），一致性问题最小
- 如果 sun shadow 不实现，论文必须写 "camera-viewer-side visibility only, without explicit sun-side self-shadowing treatment"，这削弱了物理完整性
- 0603 汇报已写了"自遮挡模型"

**降级预案**：
1. 先用 20 个代表姿态（覆盖高/低遮挡、边缘姿态）做 Blender sun shadow pass 小规模验证
2. 如果 Blender shadow pass 在技术上不可行（如渲染脚本修改工作量过大、渲染时间不可接受），则降级为 `camera_visible_nol`
3. 降级时必须：论文关键词改为 "camera-viewer-side visibility"；在 §11 写作边界中显式声明未实现 sun-side self-shadow；保留 sun shadow 为 future work

**Python ray-cast（Level 3）** 作为备选但不在 v0.4 主线优先级。若 Blender shadow pass 不可行但论文又必须写 sun shadow，再评估 Python ray-cast。

### 6.3 实现要点

**几何 pass 渲染（不变）**：
- 相机方向：正交投影，depth/normal/IndexOB
- 每姿态 1 帧 EXR

**sun shadow pass 渲染（新增）**：
- 相机位置改为太阳方向（正交投影，保持同一 ortho_scale）
- 输出：Depth.V 通道 → 比对 camera-view depth 与 sun-view depth，判定遮挡
- 或使用 Blender Shadow AOV / Light Path node
- 每姿态额外 1 帧 EXR

**Python 后处理**：
- 读取 camera-view EXR → `mask_obj`, `f_r`, `NoL`
- 读取 sun-view EXR → `V_sun_macro`（0/1 mask）
- `OCS = Σ A_pix · f_r · NoL · V_sun_macro`

### 6.4 OCS 公式中的 V_sun_macro

在 baseline（未实现 sun shadow）下所有像素 `V_sun_macro ≡ 1`，公式退化为 `OCS = Σ A_pix · f_r · NoL`，与前版公式一致。sun shadow 实现后，`V_sun_macro` 从 sun shadow pass 读取。

---

## 七、Clean Image 线性响应与 log1p/PNG/训练输入

### 7.1 旧链问题确认

审计了旧 `brdf_postprocess.py` 和 `train_cnn.py`，确认旧链存在编码不一致：
- 写入端：gamma 2.2 PNG（`write_png_gamma`）
- 读取端：`/255` 后叠加 `log1p(10·x)/log1p(10)`
- 实际经历了 gamma 2.2 + log1p 双重非线性，而方法描述只提了 log1p

### 7.2 v0.4 统一图像响应链

**Step 1：线性辐亮度生成**
```
I_linear(p) = f_r(p) · NoL(p)    [per pixel, arbitrary units proportional to radiance]
```

**Step 2：全局归一化**
```
I_norm(p) = I_linear(p) / I_scale
```
- `I_scale` = v0.4 clean corpus 全局最大 I_linear 值（CR3-006 收回）
- `I_norm ∈ [0, 1]`

**Step 3：log1p 变换**
```
I_log(p) = log1p(α · I_norm(p)) / log1p(α)
```
- `α = 10.0` 作为初始默认值（CR3-006 收回）
- 正式全链路重跑前做 quick ablation（候选 α ∈ {5, 10, 20} + raw）
- `I_log ∈ [0, 1]`

**Step 4：8-bit PNG 存储（训练输入）**
```
PNG(p) = clip(round(I_log(p) · 255), 0, 255)
```
- PNG 直接作为训练输入（load 时除以 255 即得 I_log）
- v0.4 不再使用 gamma 2.2 编码

**Step 5：训练时加载**
```python
arr = np.asarray(img, dtype=np.float32) / 255.0    # → I_log ∈ [0, 1]
# 直接作为网络输入（PNG 本身已是 log1p 编码）
```

**Step 6：退化实验的作用域**
- 噪声/模糊等退化在**线性空间**（I_linear）施加：
  ```
  I_linear_degraded = degrade(I_linear)
  I_log_degraded = log1p(α · I_linear_degraded / I_scale) / log1p(α)
  ```

### 7.3 log1p 的物理动机

```
1. 压缩动态范围（I_linear 跨 2+ 个数量级）
2. 保持亮度单调性（log1p 是单调递增函数）
3. 非线性压缩暗区更宽、亮区更窄，对 CNN 有帮助
4. α = 10.0 是经验性初始值——使暗区（I_norm << 0.1）的 log1p 梯度不过于平坦
```

### 7.4 原始线性辐亮度数据保留

- **保留 EXR（线性浮点 float32）作为 canonical raw data**
- 每次 brdf_postprocess 输出：
  - `{key}_linear.exr`：I_linear per pixel（浮点，lossless）
  - `{key}_brdf.png`：I_log 8-bit PNG（训练输入）
- 如果将来需要不同的 α 或 I_scale，从 EXR 重新生成 PNG，不需重新渲染 Blender

---

## 八、GGX/Cook-Torrance BRDF 主模型

### 8.1 模型公式

v0.4 主线 BRDF = GGX/Cook-Torrance microfacet model：

```
f_r(N, L, V) = f_diffuse + f_specular

f_diffuse = (base_color / π) · (1 - metallic) · (1 - F0)

f_specular = D_GGX(N, H, roughness) · G_Smith(N, L, V, roughness) · F_Schlick(H, V, F0)
             ─────────────────────────────────────────────────────────────────────────
                                        4 · NoL · NoV
```

其中：
- `H = normalize(L + V)`：half vector
- `D_GGX`：GGX/Trowbridge-Reitz normal distribution function
- `G_Smith`：Smith height-correlated shadowing-masking function
- `F_Schlick`：Schlick approximation of Fresnel reflectance
- 所有项使用 `max(NoL, 0)` 和 `max(NoV, 0)`

### 8.2 材料参数（CR3-001 已修正）

以下参数来自 `materials.py` 的 `_GGX_DB`，与 `brdf_models.py` 的 `MATERIAL_DB_GGX` 一致：

| 参数 | jinshuzhuti | taiyangnengban | yinshenban |
|---|---|---|---|
| base_color | 0.91 | 0.15 | 0.08 |
| metallic | 1.0 | 0.0 | 0.0 |
| roughness | 0.20 | 0.40 | 0.90 |
| F0 | 0.91 | — | — |
| ior | — | 1.5 | 1.5 |

来源：`98_外部材料备份/03_关键代码快照/01_code/materials.py` line 40-44。
**注意**：以上为 nominal synthetic parameters，不代表真实卫星材料。`base_color` 为标量（灰度 BRDF），非 RGB 三元组。

### 8.3 LegacyPhong 的处理

- LegacyPhong **不作为** v0.4 主线 BRDF
- 不作为 v0.4 主线必做项（CR3-006 D5 收回）
- 保留 `eval_legacy_phong()` 函数，可在将来作为历史/可选附录
- 不阻塞 v0.4 代码和主链路

---

## 九、术语区分：Microfacet Shadowing-Masking vs Macro Geometric Occlusion

| 术语 | 推荐英文 | 尺度 | 定义 |
|---|---|---|---|
| Microfacet shadowing-masking | **G-term** 或 **microfacet shadowing-masking (G_Smith)** | 微表面（~μm） | GGX BRDF 内部 Smith 函数描述的微面元入射/出射遮挡概率 |
| Macro geometric occlusion | **Camera-viewer-side visibility** | 宏观几何（~cm~m） | 视线被其他部件阻挡 |
| Sun-side self-shadow | **Sun-side self-shadow** 或 **V_sun_macro** | 宏观几何 | 太阳方向的 ray 被目标自身几何遮挡 |

**论文中避免**：不加限定词用 "occlusion" 指代两个不同尺度；在 G-term 上下文中用 "self-shadowing" 不解释与几何阴影的区别。

---

## 十、必须做的 Sanity Checks

在 v0.4 代码完成后、重跑实验前：

### 10.1 坐标系与向量审计（3 姿态）

选取 (0°, 0°), (90°, -45°), (150°, -80°)，验证：法线方向、sun/det 向量一致性、可见像素数合理性。

### 10.2 薄板 Depth-Buffer 审计

选取 yaw=90°, pitch=-40°（旧记录中 72× 差异的姿态），检查太阳能板边缘 depth 连续性、无背面像素混入。

### 10.3 非水密 STL Depth 行为

3 个关键姿态检查部件边界 depth 连续性。

### 10.4 Per-Part OCS 比例与旧 OCS 差异审计

生成新旧 OCS per-part per-attitude 差异表，标记异常差异（> 3σ 或 > 2×）供 Codex 复审。

### 10.5 log1p α 参数确认（CR3-006）

用 v0.4 clean corpus 做 quick ablation：α ∈ {5, 10, 20} + raw，确认 α=10 仍然合适。I_scale 记录为当前 corpus 全局最大值。

### 10.6 Sun Shadow Pass 小规模验证（CR3-004）

选 20 个代表姿态做 Blender sun shadow pass，验证：渲染流程可行、V_sun_macro 物理合理、与 camera_visible_nol 的 OCS 差异可解释。如果不可行，降级为 camera_visible_nol。

---

## 十一、写作边界

1. **Synthetic forward model only**：无真实望远镜图像、无真实大气链路、无真实探测器标定。
2. **No real telescope validation**：不声称 field-proven robustness 或 operational deployment readiness。
3. **Nominal material parameters**：材料参数为名义合成值。
4. **Sun-side visibility 声明**：
   - 如果 sun shadow pass 实现成功：写 "sun-side self-shadowing is explicitly modeled via Blender shadow pass"
   - 如果降级：写 "visibility is defined by camera-viewer-side depth-buffer; sun-side self-shadowing is not explicitly modeled and is left for future work"
5. **Observation-consistent, not observation**：与真实光学观测形成一致但不等于真实观测。
6. **No inter-satellite occlusion**：仅建模单目标自身遮挡。

---

## 十二、已收回的 D1-D8 决策表

所有 Codex 给出明确建议的决策项，以下写入冻结（不再标"未冻结"）：

| # | 问题 | 冻结决策 | 来源 |
|---|---|---|---|
| D1 | sun-side visibility | 主线优先实现 Blender sun shadow pass（`camera_visible_nol_plus_sun_shadow_pass`）；20 姿态小规模验证；若不可行则降级为 `camera_visible_nol` | CR3-004 |
| D2 | 单几何 vs 多几何 | 主表必须包含 single-geometry OCS/image/fusion 公平基线；multi-geometry concat5 单独作为"多观测几何增强"报告，不与 single image baseline 混作唯一主结论 | CR3-009 |
| D3 | log1p α | α=10 作为初始默认；正式全链路重跑前做 quick ablation α∈{5,10,20}+raw | CR3-006 |
| D4 | I_scale | 使用 v0.4 clean corpus 全局最大值；按 image_preprocess_version 记录 | CR3-006 |
| D5 | LegacyPhong appendix | 不作为 v0.4 主线必做项；不阻塞代码和主链路 | CR3-006 |
| D6 | 材料敏感性 | 主实验后做小规模 ±20% roughness/F0 敏感性；不阻塞第一轮主链路 | CR3-006 |
| D7 | 分辨率 ablation | 代表姿态子集做 128/256/512 sanity check；不要求全量三分辨率 | CR3-006 |
| D8 | split 策略 | 主结果使用 coarse-to-fine 插值 split；随机 split 作为补充；具体 seed 在 split 文件生成时记录 | CR3-006 |

---

## 十三、与 Codex CR3 修正项对应关系

| CR3 编号 | 修正内容 | 本文件对应章节 |
|---|---|---|
| CR3-001 (P0) | 修正 GGX 材料参数 | §8.2 |
| CR3-002 (P0) | 修正 yaw 网格：训练用唯一 72 yaw，绘图用 73 yaw | §3.2 |
| CR3-003 (P0) | 修正 sun_visibility enum 命名 | §6.1 |
| CR3-004 (P0) | D1 冻结为优先实现 Blender sun shadow pass | §6.2, §12 D1 |
| CR3-006 (P1) | D3/D4 收回：α=10 初始 + I_scale 策略 | §7.2, §12 D3-D4 |
| CR3-007 (P1) | OCS 公式加入 V_sun_macro | §5.1, §5.2 |
| CR3-009 (P1) | D2 收回：主表含 single-geom 公平基线 | §12 D2 |
| CR3-010 (P2) | 路径规则改为 ASCII 生成目录，允许中文上级路径 | （见配套数据规范修订版） |

### 不再标"未冻结"的项

- D5-D8：全部按 Codex 建议收回（§12）
- 所有材料参数：以 `_GGX_DB` 为准

### 仍需小规模验证（不等同于"未冻结"）

- Sun shadow pass 20 姿态验证（§10.6）
- log1p α quick ablation（§10.5）
- 分辨率 sanity check（§10.1）

---

## 十四、提交 Codex 复审清单

**本文件需再次提交 Codex 复审**。提交时将以下内容一并发出：

### 14.1 提交文件

```
04_BlenderOCS方法重建/07_v0.4前向模型冻结规范_Claude修订版.md  ← 本文件
04_BlenderOCS方法重建/08_v0.4数据与manifest字段规范_Claude修订版.md  ← 配套文件
```

### 14.2 需要 Codex 重点审阅

| 优先级 | 章节 | 审阅要点 |
|---|---|---|
| P0 | §8.2 (材料参数) | 是否与 `_GGX_DB` 完全一致 |
| P0 | §3.2 (yaw 网格) | 72 vs 73 训练/绘图分离是否合理 |
| P0 | §6.1 (sun_visibility enum) | 新命名是否消除了 `camera_only` 的歧义 |
| P0 | §5.2 (OCS 公式含 V_sun_macro) | 公式是否正确 |
| P1 | §7.2 (图像响应链) | α=10/I_scale 策略是否可执行 |
| P1 | §12 (D1-D8 决策表) | 所有决策是否已收回，无遗留未冻结项 |

### 14.3 Codex 审阅后下一步

全部收回后，进入代码阶段：`05_全链路重跑/00_重跑任务清单.md`
