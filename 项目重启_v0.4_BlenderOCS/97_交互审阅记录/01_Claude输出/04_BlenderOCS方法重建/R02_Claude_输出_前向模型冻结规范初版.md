# 04 v0.4 前向模型冻结规范（Claude 生成）

生成时间：2026-06-08
输入来源：
- `04_BlenderOCS方法重建/00_公式与Blender分工说明.md`
- `04_BlenderOCS方法重建/01_模块A_B与统一前向模型对比决策.md`
- `04_BlenderOCS方法重建/02_Blender采样选择与现实目标说明.md`
- `03_全项目排查/07_相似方法坑专项排查报告_Claude.md`
- `03_全项目排查/08_Codex复审意见_相似方法坑专项排查.md`（CR2-001～CR2-008 已吸收）
- `04_BlenderOCS方法重建/03_v0.4前向模型冻结问题清单_Claude.md`
- `98_外部材料备份/03_关键代码快照/02_blender/brdf_postprocess.py`
- `98_外部材料备份/03_关键代码快照/03_inversion/train_cnn.py`

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
         │                    Σ A_pix·f_r·NoL   I_linear = f_r·NoL
         │                 per-part + total     (per pixel)
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

**Blender 不做的事**：
- 不使用 Blender Principled BSDF / Combined pass 作为最终亮度模型
- 不依赖 Blender shading normal 的自动翻转行为
- 不使用 Backfacing AOV 作为 OCS 积分判据

### 2.2 Python 公式负责

| 职责 | 说明 |
|---|---|
| GGX/Cook-Torrance BRDF | `f_r = f_diffuse + f_specular`，参数来自 `MATERIAL_DB_GGX` |
| NoL / NoV / NoH 几何项 | 显式计算，`NoL = max(dot(N, L), 0)`, `NoV = max(dot(N, V), 0)` |
| OCS 积分 | `OCS = Σ pixel_area_projected · f_r · NoL` |
| per-part OCS | 按 IndexOB 分区累计 |
| 图像线性响应 | `I_linear = f_r · NoL`（per pixel，不含 pixel_area） |
| log1p 变换与 PNG 输出 | 见第七节 |
| 退化模型 | noise/blur/downsample/background/starfield 均为后处理压力测试 |

### 2.3 反演代码负责

| 职责 | 说明 |
|---|---|
| OCS 特征构建 | 从 OCS manifest 读取 per-part OCS → per_part_log 30D 特征 |
| 图像加载与预处理 | PNG → 反量化 → log1p 变换 → 网络输入 |
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
- **yaw 范围**：[0°, 360°)，步长 5°，共 73 个值
- **pitch 范围**：[-90°, 90°]，步长 5°，共 37 个值
- **总姿态数**：73 × 37 = 2701（5° 网格）

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
- 如果使用 Tangent pass（将来可能需要），必须确认输出的坐标系（世界/切线）

---

## 四、Geometry Pass 字段

### 4.1 每个 EXR 帧包含

| 字段 | 通道 | 数据类型 | 含义 |
|---|---|---|---|
| Normal | (R, G, B) = (X, Y, Z) | float32 | 世界坐标表面法线 |
| Depth | V（单通道） | float32 | Blender 默认 1e10 = 无穷远；depth < 1e9 为物体像素 |
| IndexOB | V（单通道） | int32 | 0=背景, 1=jinshuzhuti, 2=taiyangnengban, 3=yinshenban |
| Backfacing | R（单通道，AOV） | float32 | 0.0=正面, 1.0=背面（仅用于 sanity check，不进入 OCS 积分逻辑） |

### 4.2 Camera Visibility Mask 定义

```
camera_visible_pixel := (Depth < 1e9) AND (IndexOB > 0)
```

**注意**：Backfacing AOV 对封闭网格外视图始终为 0（已确认）。不依赖 Backfacing AOV 做运行时背面过滤。如果将来渲染场景包含非封闭网格或内部视图，需重新评估。

### 4.3 可选字段（sun-side visibility 实现后）

如果实现 sun-side visibility（见第六节），需增加：
- **Sun Shadow pass**（方案 A）或 **per-pixel sun-ray visibility flag**（方案 B），记录于 EXR 额外通道或单独 JSON。

---

## 五、OCS 积分定义

### 5.1 连续形式

```
OCS = ∫_{S_visible} f_r(ω_i, ω_o, N(x)) · cos(θ_i) · dA_projected
```

其中：
- `S_visible`：相机可见的目标表面（camera-visible pixels，见 §4.2）
- `f_r`：GGX/Cook-Torrance BRDF（见第八节）
- `cos(θ_i) = NoL = max(n·sun, 0)`
- `dA_projected`：面元在像平面上的投影面积（正交投影下为常数 pixel_area）

### 5.2 像素离散形式（正交投影）

正交投影下，面元表面积 `dA` 与投影像素面积 `dA_projected` 的关系：

```
dA_projected = dA · |cos(θ_o)| = dA · NoV
⇒ dA = dA_projected / NoV
```

代入 OCS 连续定义：

```
OCS = ∫ f_r · NoL · dA_projected
    = ∫ f_r · NoL · (NoV · dA)
    = ∫ f_r · NoL · dA_projected          [NoV 不出现：已被 dA = dA_projected/NoV 代换抵消]
```

注意这一步的等价变换：`OCS = ∫ f_r · NoL · NoV · dA` 与 `OCS = ∫ f_r · NoL · dA_projected` 等价，但后者更直接（不需要对每个像素算 NoV）。

最终像素离散公式（**推荐使用**）：

```
OCS = Σ_{p ∈ visible} pixel_area_projected · f_r(p) · NoL(p)
```

其中：
- `pixel_area_projected = (ortho_scale / resolution)²`（常数，正交换算，单位 m²）
- `f_r(p)` = GGX/Cook-Torrance BRDF 值（标量）
- `NoL(p) = max(N(p) · L, 0)`

### 5.3 NoV 抵消的成立条件

1. **正交投影**：所有像素的 `pixel_area_projected` 为同一常数（不需要逐像素的 NoV 除法）
2. **NoV > 0**：NoV ≤ 0 的像素 OCS 贡献显式为 0（见 §5.4）
3. **无 fractional coverage**：假设像素全部覆盖目标（边缘像素见 §5.5）

### 5.4 NoL/NoV 边界条件

| 条件 | 处置 | 原因 |
|---|---|---|
| NoV ≤ 0 | 像素 OCS 贡献 = 0，f_r = 0 | 该像素为背面/切面，物理上接收不到入射光或反射不到相机 |
| NoL ≤ 0 | 像素 OCS 贡献 = 0（通过 `NoL = max(n·sun, 0)` 自然归零） | 太阳在表面背后，该处不被照亮 |

**实现方式**：在 `compute_radiance_image()` 中，先用 `NoV > 0` 过滤像素，再对保留的像素计算 `NoL = max(n·sun, 0)` 和 `f_r`。

**与 Blender Cycles 的关系**：
- 旧记录显示 Blender Cycles 在 NoL≤0 或 NoV≤0 时 shading normal 会自动翻转产生非零残差（如 yaw=0/pitch=-30 时 B=2.1e-3）
- v0.4 不依赖 Blender Combined/shading 亮度，而是从 Normal pass 读取几何法线后用 Python 显式计算 BRDF
- 因此 NoL≤0 / NoV≤0 的过滤完全由 Python 端控制，不受 Cycles 着色法线行为影响

### 5.5 pixel_area_projected 与边缘像素处理

**pixel_area_projected 定义**：

```
pixel_area_projected = (ortho_scale / resolution)²
```

其中 `ortho_scale = 2.2 × r_max`。
- 例：r_max ≈ 1.473 m，ortho_scale = 3.24 m，resolution = 256 → pixel_area = (3.24/256)² = 1.6015×10⁻⁴ m²

**常数 pixel_area 的有效范围**：正交投影下，所有像素覆盖相同的目标平面面积（不随像素位置变化）。

**边缘像素 fractional coverage**：
- 目标边缘的像素仅部分覆盖目标表面，其余为背景
- v0.4 不做 fractional coverage 修正，接受为已知舍入误差
- 估计误差：256×256 分辨率边缘像素占比约 4×256/65536 ≈ 1.6%，总 OCS 影响 < 2%
- 方法文件中记录此简化假设

---

## 六、Sun-Side Visibility / Self-Shadow：三方案与决策建议

### 6.1 问题定义

> 论文是否写"含自遮挡/阴影"？如果写，如何实现 sun-ray 方向每个像素是否被其他部件遮挡的判定？

如果论文声称"self-occlusion"或"shadowing"，v0.4 必须实现 sun-side visibility（不仅是 camera visibility）。否则必须在论文中清楚限定为 "viewer-side (camera) visibility only, without explicit sun-side self-shadowing treatment"。

### 6.2 三方案对比

| | 方案 A：Blender Shadow Pass | 方案 B：Python Ray-Cast | 方案 C：Viewer-Side Only |
|---|---|---|---|
| **实现方式** | 额外渲染 sun-view EXR（shadow map），在 BRDF 后处理中交叉比对 | 复用旧 trimesh+Embree ray-cast，对每个 camera-visible 像素向 sun 方向发 shadow ray | 不实现 sun-side self-shadow，OCS 仅使用 camera-visible pixels |
| **实现成本** | 需修改 Blender 渲染脚本，额外 sun-view 渲染（每姿态 2× EXR），总渲染时间约 2× | 需要将旧 `occlusion.py` 的面中心射线逻辑改造为 pixel-level 射线（2701 姿态 × 256² 像素 ≈ 1.77×10⁸ 射线），计算量大 | 零额外实现成本 |
| **精度/一致性** | 最高：shadow pass 与几何 pass 使用同一场景、同一精度 | 中：trimesh ray-cast 精度取决于 ray 方向和三角形交叉算法，可能与 Blender depth-buffer 不完全一致 | 最低但定义清晰 |
| **验证方式** | 选 20 个关键姿态（包含极端遮挡），手动比对 OCS with/without sun shadow 的 per-part 变化 | 与方案 A 交叉验证（选 10 个姿态比对 Blender shadow pass vs Python ray-cast 的一致性） | 不适用 |
| **论文写作后果** | 可写 "self-shadowing / sun-side occlusion is explicitly modeled via Blender shadow pass" | 可写 "sun-ray self-shadowing is computed via Embree-accelerated ray-casting on the pixel-level visible surface samples" | 必须写 "visibility is defined by camera-viewer-side depth-buffer only; sun-side self-shadowing is not explicitly modeled and left for future work" |
| **对 OCS 数值的影响** | 太阳被遮挡的像素贡献归零，OCS 整体下降（复杂几何下降更明显）；per-part 比例改变 | 同 A（但如果 ray-cast 与 Blender 不一致，会有系统性偏差） | OCS 只包含 camera-visible 的像素贡献，太阳被遮挡但不影响相机可见性的像素仍计入 |

### 6.3 当前推荐：优先评估方案 A，方案 C 为保底

**推荐优先级**：A > B > C

1. **方案 A（Blender Shadow Pass）作为首选**：
   - 与 geometry pass 同源（Blender 同一场景），一致性问题最小
   - 渲染时间翻倍但可接受（2701×2 ≈ 5402 帧，批量化）
   - 若论文需要写"含自遮挡/阴影"，这是最严谨的方案

2. **方案 B（Python Ray-Cast）作为备选**：
   - 如果方案 A 的 Blender 脚本修改工作量过大
   - 但需要额外验证 Python ray-cast 与 Blender depth-buffer 的一致性

3. **方案 C（Viewer-Side Only）作为保底**：
   - 如果不实现 sun shadow，论文关键词从 "self-occlusion/shadowing" 改为 "camera-viewer-side visibility"
   - 不能只因复杂度直接选 C（Codex CR2-002）

**需要作者/Codex 决策**：是否同意优先实现方案 A？如果方案 A 实施中遇到阻塞，降级为方案 C 的阈值是什么？

---

## 七、Clean Image 线性响应与 log1p/PNG/训练输入

### 7.1 旧代码链审计结果

审计了 `brdf_postprocess.py`（写入端）和 `train_cnn.py`（读取端），发现旧链存在**两端编码不一致**：

**写入端**（`brdf_postprocess.py` line 404-411）：
```python
scale = max(radiance_max_global, 1e-12)       # 全局最大值（2701 帧）
write_png_gamma(path, rad, scale=scale, gamma=2.2)
# write_png_gamma 内部：
#   img = clip(linear / scale, 0, 1)
#   img = pow(img, 1/2.2)
#   uint8 = img * 255
```
→ PNG 存储的是 **gamma 2.2 编码**（不是 log1p）

**读取端**（`train_cnn.py` line 74-81）：
```python
arr = np.asarray(img, dtype=np.float32) / 255.0        # → [0, 1]
if intensity_mode == "log1p":
    arr = np.log1p(10.0 * arr) / np.log1p(10.0)       # log1p(10×) / log1p(10)
```
→ 训练时先除以 255 得到 [0,1]，再应用 `log1p(10·x) / log1p(10)` 变换

**不一致性**：
- 写入端用 gamma 2.2（非线性编码）
- 读取端在 gamma 解码后（通过 /255 隐式完成？实际上 /255 不是 gamma 解码）又加了一层 log1p
- 这意味着训练输入经历了 gamma 2.2 + log1p 双重非线性，而方法描述只提了 log1p

### 7.2 v0.4 重新定义：统一的线性→训练输入链

v0.4 废弃旧的 gamma PNG + log1p 混合链，采用以下完整定义：

**Step 1：线性辐亮度生成**
```
I_linear(p) = f_r(p) · NoL(p)    [per pixel, arbitrary units proportional to radiance]
```
- 范围：取决于姿态和材料，约 [0, ~50] a.u.

**Step 2：全局归一化**
```
I_norm(p) = I_linear(p) / I_max_global
```
- `I_max_global` = 全部 2701 帧中的最大 I_linear 值
- `I_norm ∈ [0, 1]`

**Step 3：log1p 变换**
```
I_log(p) = log1p(α · I_norm(p)) / log1p(α)
```
- `α = 10.0`（基于旧消融实验：log1p mean error 12.13° vs raw 15.99°；需要 v0.4 重新确认）
- `I_log ∈ [0, 1]`

**Step 4：8-bit PNG 存储（训练输入）**
```
PNG(p) = clip(round(I_log(p) · 255), 0, 255)
```
- PNG 直接作为训练输入（load 时除以 255 即得 I_log）
- v0.4 不再使用 gamma 2.2 编码（与旧 brdf_postprocess.py 不同）

**Step 5：训练时加载**
```python
arr = np.asarray(img, dtype=np.float32) / 255.0    # → I_log ∈ [0, 1]
# 直接作为网络输入（不再做额外 log1p 变换，因为 PNG 本身就是 log1p 编码）
```

**Step 6：退化实验的作用域**
- 噪声/模糊等退化在**线性空间**施加：
  ```
  I_linear_degraded = degrade(I_linear)   # 在线性辐亮度上操作
  I_log_degraded = log1p(α · I_linear_degraded / I_max_global) / log1p(α)
  ```
- 不在 log1p 空间加噪（噪声在线性空间有明确物理含义）
- 不在 8-bit 量化后加噪（避免量化误差与退化混淆）

### 7.3 log1p 的物理动机

```
log1p 变换的动机：
1. 压缩动态范围（I_linear 跨 2+ 个数量级）
2. 保持亮度单调性（log1p 是单调递增函数）
3. 不保持亮度间距（非线性压缩暗区更宽、亮区更窄，对 CNN 有帮助）
4. α = 10.0 的选择是经验性的——使暗区（I_norm << 0.1）的 log1p 梯度不过于平坦
   - log1p(10·0.01) ≈ 0.095，log1p(10·0.001) ≈ 0.00995
   - 暗区仍有足够动态范围用于姿态识别
```

### 7.4 v0.4 需要重新确认的参数

| 参数 | 旧值（参考） | v0.4 是否需要重新确认 |
|---|---|---|
| α (log1p scale) | 10.0 | 是——用新 Blender-derived OCS 重做一次 log1p vs raw 的 quick ablation |
| I_max_global | ~53.07 (LegacyPhong) / ~TBD (GGX) | 是——GGX BRDF 的 radiance 范围将与 LegacyPhong 不同 |
| log1p vs raw 的效果 | log1p 12.13° vs raw 15.99° | 是——但不预期结论会反转 |

### 7.5 原始线性辐亮度数据保留

- **保留 EXR（线性浮点 float32）作为 canonical raw data**
- 每次 brdf_postprocess 输出：
  - `{key}_linear.exr`：I_linear per pixel（浮点，lossless）
  - `{key}_brdf.png`：I_log 8-bit PNG（训练输入）
- 如果将来需要不同的预处理参数（α, I_max_global），从 EXR 重新生成 PNG，不需要重新渲染 Blender geometry pass
- EXR 文件体量：2701 帧 × ~20MB/帧 ≈ 54 GB（可接受）

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
- 所有项使用 `max(NoL, 0)` 和 `max(NoV, 0)`（见 §5.4）

### 8.2 材料参数

| 参数 | jinshuzhuti | taiyangnengban | yinshenban |
|---|---|---|---|
| base_color | (0.9, 0.9, 0.9) | (0.5, 0.5, 0.6) | (0.3, 0.3, 0.3) |
| metallic | 1.0 | 0.0 | 0.0 |
| roughness | 0.20 | 0.50 | 0.60 |
| F0 | 0.91 | — | — |
| ior | — | — | — |

来源：`brdf_models.py` 中的 `MATERIAL_DB_GGX`。
**注意**：以上为 nominal synthetic parameters，不代表真实卫星材料。

### 8.3 LegacyPhong 的处理

- LegacyPhong **不作为** v0.4 主线 BRDF
- 保留 `eval_legacy_phong()` 函数在 `brdf_models.py` 中
- 可在 Appendix 或 Supplementary 中做 GGX vs LegacyPhong 对照
- legacy phong 参数已记录于旧 `MATERIAL_DB`

---

## 九、术语区分：Microfacet Shadowing-Masking vs Macro Geometric Occlusion

以下术语表应在论文方法部分显式使用，防止审稿混淆：

| 术语 | 推荐英文 | 尺度 | 定义 |
|---|---|---|---|
| Microfacet shadowing-masking | **G-term** 或 **microfacet shadowing-masking (G_Smith)** | 微表面（~μm） | GGX BRDF 内部 Smith 函数描述的微面元之间入射/出射方向被遮挡的概率 |
| Macro geometric occlusion | **Camera-viewer-side visibility** 或 **geometric occlusion** | 宏观几何（~cm~m） | 太阳射线或视线被其他部件阻挡（如太阳能板遮挡主体） |
| Sun-side self-shadow | **Sun-side self-shadow** | 宏观几何 | 太阳方向的 ray 被目标自身几何遮挡（区别于 camera 方向遮挡） |

**论文中避免**：
- 不要用 "occlusion" 不加限定词指代两个不同尺度的概念
- 不要在 GGX 的 G-term 上下文中使用 "self-shadowing" 而不解释这与几何阴影不同

---

## 十、必须做的 Sanity Checks

在 v0.4 代码完成后、重跑实验前，必须完成以下 sanity checks：

### 10.1 坐标系与向量审计（3 姿态）

选取 3 个覆盖性姿态：(0°, 0°), (90°, -45°), (150°, -80°)，对每个姿态验证：

1. **法线方向**：从 Blender EXR Normal pass 提取目标中心的法线，与 Python 端从 STL 读取的对应面法线比对
2. **sun/det 向量**：确认 Python 与 Blender 使用相同的归一化方向向量
3. **可见像素数**：`obj_pixels` 是否合理（非零、不超过 total pixels、与姿态一致）

### 10.2 薄板 Depth-Buffer 审计

选取 yaw=90°, pitch=-40°（旧记录中 72× 差异的姿态），检查：
- 太阳能板边缘像素的 depth 连续性
- 是否存在背面像素混入（背面深度应 > 正面深度，IndexOB 应一致）
- 三部件边界的 depth 跳跃是否与几何一致

### 10.3 非水密 STL Depth 行为

在 3 个关键姿态（包含部件交界姿态）检查：
- 部件边界像素是否存在 depth 不连续（>1mm）
- 如果有，评估对 OCS 积分的影响

### 10.4 Per-Part OCS 比例与旧 OCS 差异审计

- 生成新旧 OCS 的 per-part per-attitude 差异表
- 确认差异可以解释（可见面积语义、薄板处理、GGX 参数等）
- 标记异常差异（> 3σ 或 > 2×）供 Codex 复审

### 10.5 log1p α 参数确认

- 用新 Blender-derived OCS 对应的 2701 帧图像数据，跑一次 quick ablation：log1p(α=5, 10, 20) vs raw 的 image-only mean error
- 确认 α=10 在新 OCS 口径下仍然合适

---

## 十一、写作边界

以下边界声明应在论文方法部分和 Discussion 中显式出现：

1. **Synthetic forward model only**：所有数据来自 synthetic Blender-derived pixel-level sampling + Python explicit GGX/Cook-Torrance BRDF。**无真实望远镜图像、无真实大气链路、无真实探测器标定**。
2. **No real telescope validation**：论文不声称 field-proven robustness 或 operational deployment readiness。
3. **Nominal material parameters**：材料参数为名义合成值，不代表真实卫星表面光学属性。
4. **Camera-viewer-side visibility baseline**：如果 v0.4 未实现 sun-side self-shadow（方案 C），必须写 "visibility is defined by camera-viewer-side depth-buffer only; sun-side self-shadowing is not explicitly modeled and is left for future work"。
5. **Observation-consistent, not observation**：v0.4 的 OCS 和图像来自同一前向物理模型，与真实光学观测形成一致（consistent with the image formation model），但不是真实观测。
6. **No inter-satellite occlusion**：前向模型仅建模单目标自身遮挡，不考虑编队/交会场景中的他星遮挡。

---

## 十二、未冻结项和需要作者/Codex 决策

以下项目**尚未冻结**，需要作者和/或 Codex 复审后再决定：

| # | 问题 | 涉及方 | 优先级 |
|---|---|---|---|
| D1 | **Sun-side visibility 方案选择**（A/B/C，见 §6） | 作者 + Codex | **最高** |
| D2 | **多观测几何 OCS (5-geom) 与单几何图像 (phase63) 的对比公平性**：主表用 single-geometry OCS baseline 还是 multi-geometry concat5？ | 作者 + Codex | **高** |
| D3 | **log1p α = 10.0 是否在新 OCS 口径下重新确认**，还是沿用旧 α=10.0 不用重跑？ | 作者 | **高**（影响图像存储格式） |
| D4 | **I_max_global 的归一化策略**：使用全局最大值（全 2701 帧），还是使用 per-geometry 最大值（不同 sun/det 组分开）？ | 作者 | **中** |
| D5 | **LegacyPhong appendix**：是否在 v0.4 附录中包含 GGX vs LegacyPhong 对照？ | 作者 | **低** |
| D6 | **材料参数敏感性分析**：v0.4 是否重新做 ±20% roughness sweep（因为 OCS 源变了），还是声明为 future work？ | 作者 | **中** |
| D7 | **分辨率 ablation**：是否在 v0.4 补充材料中包含 128 vs 256 vs 512 的 OCS 差异分析？ | 作者 | **低** |
| D8 | **split 策略**：v0.4 是否沿用 "coarse_to_fine 10° train / 5° test"，还是重新设计？ | 作者 + Codex | **高** |

**关于 D1 的特别说明**（Codex CR2-002）：
> D1 对 v0.4 的工作量有重大影响。方案 A 需要修改 Blender 渲染脚本；方案 C 不需要代码工作但会影响论文的声称范围。建议作者本周内做出决策，并告知 Claude/Codex 进入后续阶段。

---

## 十三、与旧坑位排查的对应关系

| 排查 ID | 本文件中的对应章节 | 处置状态 |
|---|---|---|
| METH-H1 (visible area 语义差异) | §2.1, §5.2, §6 | ✅ 已在统一前向模型中解决 |
| METH-H2 (薄板双面可见性) | §4.2, §10.2 | ✅ camera visibility 用 depth-buffer 解决；sanity check 待做 |
| METH-H3 (Blender backface shading) | §5.4 | ✅ Python 显式 NoL/NoV 过滤，不依赖 Blender shading |
| METH-H4 (log1p 链未冻结) | §7.2-7.4 | ✅ v0.4 重新定义，参数待确认 (D3) |
| METH-H5 (遮挡率定义变化) | §6, §9 | ✅ 术语区分已明确 |
| METH-S2 (NoV 抵消条件) | §5.3 | ✅ 成立条件已列出 |
| METH-S4 (edge pixel) | §5.5 | ✅ 接受已知误差 |
| METH-S5 (向量归一化) | §3.3 | ✅ 强制归一化要求已写入 |
| METH-S7 (latest-run) | 见文件 2（manifest 规范） | — |
| METH-S8 (线性数据不可恢复) | §7.5 | ✅ 保留 EXR raw data |
| METH-U1 (sun-side visibility 三路径) | §6 | 🔴 等作者/Codex 决策 (D1) |
| METH-U2 (术语混淆) | §9 | ✅ 术语表已定义 |
| METH-U3 (多几何公平性) | §12 (D2) | 🔴 等作者/Codex 决策 |
| METH-U4 (split seed) | 见文件 2 | 🔴 等 v0.4 重定义 |
| METH-U5 (非水密 STL) | §10.3 | ⚪ sanity check 待做 |

---

## 十四、提交 Codex 审阅清单

**本文件需提交 Codex 审阅**。提交时将以下内容一并发出：

### 14.1 提交文件

```
04_BlenderOCS方法重建/04_v0.4前向模型冻结规范_Claude.md  ← 本文件
04_BlenderOCS方法重建/05_v0.4数据与manifest字段规范_Claude.md  ← 配套文件
```

### 14.2 需要 Codex 重点审阅的章节

| 优先级 | 章节 | 审阅要点 |
|---|---|---|
| P0 | §5 (OCS 积分定义) | 连续→离散推导是否正确，NoV 抵消条件是否完整 |
| P0 | §6 (sun-side visibility 三方案) | 三方案评估是否公允，推荐优先级是否合理 |
| P0 | §7 (图像响应链) | 新定义的 linear→log1p→PNG 链是否有遗漏，α=10 审计来源是否正确 |
| P1 | §4 (geometry pass 字段) | camera visibility mask 定义是否与 CR2-001 口径一致 |
| P1 | §9 (术语区分) | 三组术语是否清晰无歧义，论文中是否可直接使用 |
| P2 | §5.4 (NoL/NoV 边界) | 是否完全解决了 CR2-004 的背向面着色问题 |
| P2 | §10 (sanity checks) | 审计项是否覆盖了所有已知坑位 |

### 14.3 需要 Codex 给出决策的问题（抄送作者）

以下 8 项在当前规范中标记为"未冻结"，需要 Codex 审阅后给出明确推荐方案或退回给作者决策：

| # | 问题 | 当前推荐 | 需要 Codex 做的 |
|---|---|---|---|
| D1 | sun-side visibility A/B/C | 优先评估 A，C 为保底 | 确认推荐；或改为直接选 C |
| D2 | 主表用 1-geom 还是 concat5 OCS | 未给出明确推荐 | 给出推荐并写入红线 |
| D3 | log1p α=10 是否重新确认 | 建议快速重做 ablation | 确认是否必须重做 |
| D4 | I_max_global 归一化策略 | 未给出推荐 | 给出推荐 |
| D5 | LegacyPhong appendix | 未给出推荐 | 给出去/留建议 |
| D6 | 材料敏感性分析重做 | 建议重做但可延后 | 确认优先级 |
| D7 | 分辨率 ablation | 建议做 | 给出去/留建议 |
| D8 | split 策略 | 未给出推荐 | 给出推荐方案 |

### 14.4 Codex 审阅后下一步

Codex 审阅通过并收回 D1-D8 决策后：
1. Claude 更新本文件（D1-D8 写死为已冻结决策）
2. 进入代码阶段：`05_全链路重跑/00_重跑任务清单.md`
