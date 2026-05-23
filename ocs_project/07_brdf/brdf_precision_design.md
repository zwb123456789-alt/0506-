# BRDF 精确化统一设计文档

> 项目：OCS + 图像联合仿真  
> 阶段：论文期精度升级  
> 日期：2026-05-18  
> 目标：建立 OCS 与图像共享的统一 BRDF 模型

---

## 1. 设计目标

### 1.1 核心原则

```text
同一 STL 几何
    ↓
同一姿态定义
  ↓
同一太阳方向与探测器方向
    ↓
同一遮挡语义
    ↓
同一 BRDF 模型与材料参数  ← 本文档解决此项
    ↓
OCS 标量计算 + 二维图像渲染
    ↓
OCS-only / image-only / OCS+image 姿态反演实验
```

### 1.2 优先级

```text
两端一致性 > 显式物理公式 > 合理材料参数 > 敏感性分析 > 真实观测绝对定标
```
### 1.3 论文定位

**物理一致仿真 + 姿态估计算法验证**（非真实卫星绝对辐射复现）

- 不要求材料参数完全等于真实卫星
- 但参数必须物理合理、来源可说明
- 必须做材料参数敏感性分析

---

## 2. 方向定义（统一约定）

### 2.1 坐标系

- **惯性系 I**：太阳、探测器方向固定在此系
- **本体系 M**：卫星 STL 几何定义在此系
- **旋转矩阵 R**：M → I，`R = Rz(yaw) @ Ry(pitch) @ Rx(roll)`（Z-Y-X 内旋）

### 2.2 方向向量（单位向量）

| 符号 | 含义 | 系 | 备注 |
|---|---|---|---|
| **L** | 从表面点指向太阳 | I | 光源方向 |
| **V** | 从表面点指向探测器/相机 | I | 观测方向 |
| **N** | 表面单位法向量 | I | 旋转后法向 `N_I = N_M @ R` |
| **H** | 半程向量 `normalize(L + V)` | I | Phong/GGX 共用 |

### 2.3 角度余弦（非负截断）

```python
NoL = max(dot(N, L), 0)  # 入射角余弦
NoV = max(dot(N, V), 0)  # 出射角余弦
NoH = max(dot(N, H), 0)  # 半程角余弦
VoH = max(dot(V, H), 0)  # 用于 Fresnel
LoH = max(dot(L, H), 0)  # 等价于 VoH（L/V 对称）
```

### 2.4 可见性规则

**只有当 `NoL > 0` 且 `NoV > 0` 时，该面元或像素才产生直接太阳散射贡献。**

---

## 3. BRDF 模型定义

### 3.1 LegacyPhong（历史 baseline）

**用途**：冻结当前模块 A 公式，作为工程一致性验证基准。

**公式**：
```python
f_r = (rho_d / π) + rho_s * (NoH)^n
```

**参数**：
- `rho_d`：漫反射系数（diffuse albedo）
- `rho_s`：镜面反射系数（specular albedo）
- `n`：Phong 指数（specular sharpness）

**特点**：
- 经验公式，非物理严格
- 无能量守恒归一化
- `rho_d + rho_s` 可 > 1
- 不区分金属/电介质

**OCS 积分**：
```python
ocs = sum(
    area_m2 * f_r * NoL * NoV
    for each face where (NoL > 0) and (NoV > 0) and not occluded
)
```

---

### 3.2 NormalizedPhong（可选过渡）

**用途**：在 LegacyPhong 基础上加能量守恒归一化。

**公式**：
```python
f_diffuse  = rho_d / π
f_specular = rho_s * ((n + 2) / (2 * π)) * (NoH)^n
f_r = f_diffuse + f_specular
```

**归一化项**：`(n + 2) / (2 * π)` 保证镜面项在半球积分 ≈ 1。

**特点**：
- 仍是 Phong 高光形状
- 但加了物理归一化
- 可作为 LegacyPhong → GGX 的中间验证

---

### 3.3 GGX / Cook-Torrance（论文主模型）

**用途**：物理可信的微表面 BRDF，论文定量实验主模型。

**公式**：
```python
f_r = f_diffuse + f_specular
```

#### 3.3.1 漫反射项

```python
f_diffuse = (1 - metallic) * (rho_d / π)
```

- 金属 `metallic=1` 时无漫反射
- 电介质 `metallic=0` 时保留全部漫反射

#### 3.3.2 镜面项

```python
f_specular = (D * G * F) / max(4 * NoL * NoV, eps)
```

其中：

**D：GGX 法向分布函数**
```python
def D_GGX(NoH, alpha):
    a2 = alpha * alpha
    denom = NoH * NoH * (a2 - 1.0) + 1.0
    return a2 / (π * denom * denom)
```

**G：Smith-GGX 几何遮蔽项**
```python
def G1_GGX(NoX, alpha):
    a2 = alpha * alpha
    return 2.0 * NoX / (NoX + sqrt(a2 + (1.0 - a2) * NoX * NoX))

def G_Smith_GGX(NoL, NoV, alpha):
    return G1_GGX(NoL, alpha) * G1_GGX(NoV, alpha)
```

**F：Schlick Fresnel 近似**
```python
def F_Schlick(VoH, F0):
    return F0 + (1.0 - F0) * (1.0 - VoH)^5
```

- `F0`：垂直入射时的反射率
- 电介质：`F0 = ((ior - 1) / (ior + 1))^2`
- 金属：`F0` 直接设置（如铝 ≈ 0.91）

#### 3.3.3 粗糙度

```python
alpha = roughness * roughness
```

- `roughness`：感知粗糙度（线性）
- `alpha`：GGX 参数（平方映射，更符合感知）
- 下限：`roughness >= 0.02`（避免数值不稳定）

---

## 4. 材料参数字段

### 4.1 统一材料表结构

```python
MATERIAL = {
    "name": str,            # 部件名称
    "brdf_model": str,        # "legacy_phong" / "normalized_phong" / "ggx"
    
    # Legacy Phong 参数
    "rho_d": float,           # 漫反射系数 [0, 1]
    "rho_s": float,           # 镜面反射系数 [0, 1]
    "n": float,             # Phong 指数 [1, 1000]
    
    # GGX 参数
    "base_color": (R,G,B),    # 基础颜色（当前阶段灰度，R=G=B）
    "metallic": float,        # 金属度 [0, 1]
    "roughness": float,       # 粗糙度 [0.02, 1]
    "F0": float,         # 垂直入射反射率（金属用）
    "ior": float,           # 折射率（电介质用）
    
    # 可选高级参数（后续扩展）
    "anisotropy": float,      # 各向异性 [0, 1]
    "eta": float,           # 复折射率实部
    "k": float,               # 复折射率虚部（消光系数）
}
```

### 4.2 参数等级

| 等级 | 含义 | 当前是否需要 |
|---|---|---|
| Level 0 | 自洽仿真参数，只要求两端一致 | 可用于调试 |
| Level 1 | 文献合理参数 / 典型材料参数 | **推荐作为论文主实验** |
| Level 2 | 实测或反标定材料参数 | 后续真实观测对比再做 |

**当前项目推荐**：Level 1 + 参数敏感性分析

---

## 5. 三类部件材料参数策略

### 5.1 jinshuzhuti（金属主体）

**物理特性**：铝合金/镀铝外壳

**LegacyPhong 参数**（当前）：
```python
rho_d = 0.20
rho_s = 0.60
n = 80
```

**GGX 参数**（推荐）：
```python
base_color = (0.91, 0.91, 0.91)  # 铝反照率
metallic = 1.0                 # 金属
roughness = 0.15 ~ 0.30           # 抛光铝 0.15，氧化铝 0.30
F0 = 0.91                         # 铝垂直入射反射率
```

**参数来源**：
- 铝 F0 ≈ 0.91：文献典型值（可见光波段）
- roughness：抛光铝 0.1~0.2，氧化铝 0.3~0.5
- 建议先用 `roughness=0.20` 作为 nominal 值

### 5.2 taiyangnengban（太阳能电池板）

**物理特性**：玻璃盖片 + 半导体，低漫反射、较强方向性反射

**LegacyPhong 参数**（当前）：
```python
rho_d = 0.15
rho_s = 0.10
n = 20
```

**GGX 参数**（推荐）：
```python
base_color = (0.15, 0.15, 0.15)  # 低反照率
metallic = 0.0                    # 电介质
roughness = 0.30 ~ 0.50           # 玻璃表面
ior = 1.5             # 玻璃折射率
F0 = 0.04                # 从 ior 计算：((1.5-1)/(1.5+1))^2
```

**参数来源**：
- 玻璃 ior ≈ 1.5：标准值
- roughness：光滑玻璃 0.1~0.2，磨砂玻璃 0.4~0.6
- 建议先用 `roughness=0.40` 作为 nominal 值

### 5.3 yinshenban（遮光板）

**物理特性**：低反射率黑色涂层

**LegacyPhong 参数**（当前）：
```python
rho_d = 0.08
rho_s = 0.02
n = 10
```

**GGX 参数**（推荐）：
```python
base_color = (0.08, 0.08, 0.08)  # 低反照率
metallic = 0.0                  # 电介质
roughness = 0.80 ~ 0.95           # 粗糙涂层
ior = 1.5                 # 涂层折射率
F0 = 0.04                     # 从 ior 计算
```

**参数来源**：
- 黑色涂层反照率 0.05~0.10：文献典型值
- roughness：粗糙涂层 0.7~0.95
- 建议先用 `roughness=0.90` 作为 nominal 值

---

## 6. 参数来源策略

### 6.1 推荐来源优先级

1. **文献典型值**（当前阶段推荐）
   - 材料手册（如 Palik 光学常数数据库）
   - 光学文献（如 BRDF 测量论文）
   - 计算机图形学标准材料库（如 Disney BRDF、Substance）

2. **实测 BRDF 数据**（后续真实观测对比）
   - 实验室 BRDF 测量
   - 真实观测数据反标定

3. **合理假设**（调试阶段）
   - 物理合理范围内
   - 必须在论文中说明假设依据

### 6.2 论文表述建议

```text
本文材料参数采用文献合理值。金属主体使用铝的典型光学参数（F0=0.91，
roughness=0.20）；太阳能电池板使用玻璃盖片参数（ior=1.5，roughness=0.40）；
遮光板使用低反射率涂层参数（base_color=0.08，roughness=0.90）。通过
材料参数敏感性分析评估参数不确定性对姿态估计结果的影响。
```

---

## 7. 工程实现架构

### 7.1 canonical BRDF 模块

**新增文件**：`ocs_project/01_code/brdf_models.py`

**职责**：
- 提供统一 BRDF 计算接口
- 所有模块（OCS / 图像渲染 / 验证）调用此模块
- 避免多处复制公式
**接口设计**：
```python
def eval_legacy_phong(N, L, V, rho_d, rho_s, n):
    """LegacyPhong BRDF"""
    pass

def eval_normalized_phong(N, L, V, rho_d, rho_s, n):
    """NormalizedPhong BRDF"""
    pass

def eval_ggx_cook_torrance(N, L, V, base_color, metallic, roughness, F0=None, ior=None):
  """GGX/Cook-Torrance BRDF"""
    pass

def eval_brdf(N, L, V, material: dict):
    """统一入口，根据 material["brdf_model"] 分发"""
    model = material["brdf_model"]
    if model == "legacy_phong":
        return eval_legacy_phong(N, L, V, material["rho_d"], material["rho_s"], material["n"])
    elif model == "ggx":
        return eval_ggx_cook_torrance(N, L, V, ...)
    else:
        raise ValueError(f"Unknown BRDF model: {model}")
```

**要求**：
1. 支持 numpy 批量计算（N/L/V 可以是 (3,) 或 (N,3)）
2. 所有方向向量归一化检查
3. 对 `NoL <= 0` 或 `NoV <= 0` 返回 0
4. 防止 NaN / Inf（除零保护、roughness 下限）
5. 单元测试覆盖极端角度

### 7.2 模块 A 修改原则

**当前问题**：`ocs_core.py:72-73` 内嵌 BRDF 公式

**修改目标**：
```python
# 旧代码（删除）
# brdf_vec = (mat["rho_d"] / np.pi) + mat["rho_s"] * (cos_alpha_vec ** mat["n"])

# 新代码
from brdf_models import eval_brdf
brdf_vec = eval_brdf(normals_PI, sun_norm, det_norm, mat)
```

**验收标准**：
- LegacyPhong 接入前后 OCS 数值一致（相对误差 < 1e-6）
- 不改变遮挡逻辑
- 不改变可见性筛选

### 7.3 模块 B 修改原则

**当前问题**：Principled BSDF 只是视觉近似，不是定量模型

**修改目标**：支持两类渲染模式

| 模式 | 用途 | 实现路径 |
|---|---|
| `principled_preview` | 快速预览，不做定量分析 | 保留当前 Principled BSDF |
| `exact_brdf` | 论文定量渲染 | OSL shader 或几何缓冲 + Python 后处理 |

#### 路径 A：OSL Shader（优先尝试）

**优点**：
- 保留 Blender 渲染流程
- 利用 Cycles 几何、相机、阴影机制
- 与当前模块 B 比较接近

**风险**：
- OSL 可能只能 CPU 渲染
- 自定义 BRDF 与 Cycles 能量、阴影、采样机制需要验证
- 渲染速度可能下降

**实现**：
```osl
// legacy_phong.osl
shader legacy_phong(
    vector N = N,
    vector L = normalize(vector(1, 0, 0.3)),
    vector V = -I,
    float rho_d = 0.2,
    float rho_s = 0.6,
    float n = 80,
    output closure color BSDF = 0
)
{
    vector H = normalize(L + V);
    float NoH = max(dot(N, H), 0.0);
    float NoL = max(dot(N, L), 0.0);
    float NoV = max(dot(N, V), 0.0);
    
    if (NoL > 0 && NoV > 0) {
        float brdf = (rho_d / M_PI) + rho_s * pow(NoH, n);
        BSDF = brdf * emission();  // 或用 diffuse() + microfacet()
    }
}
```

#### 路径 B：几何缓冲 + Python 后处理（回退方案）

**流程**：
```text
Blender 输出：
法线 / 深度 / 世界坐标 / 材料 ID / 可见面
    ↓
Python 使用 brdf_models.py 逐像素计算辐射
    ↓
使用同一遮挡逻辑判断太阳可见性
    ↓
输出线性图像（EXR / numpy array）
```

**优点**：
- 最容易保证与模块 A 数学一致
- 不依赖 Blender Principled
- 不依赖 OSL closure 细节
- 便于图像积分与 OCS 对比

**风险**：
- 工程量略大
- 需要处理像素坐标、深度、法线、材料 ID

---

## 8. 定量渲染约束

定量模式（`exact_brdf`）必须满足：

1. **色彩管理**：`view_transform='Standard'`（不用 Filmic）
2. **输出格式**：优先线性 EXR / numpy array（不用 gamma PNG 做误差评估）
3. **背景**：纯黑（RGB=0）
4. **环境光**：禁止不受控环境光
5. **间接光**：禁止不受控多次反射（或显式建模）
6. **随机种子**：固定（保证可复现）
7. **法线**：与模块 A 保持一致（优先 flat face normal）
8. **可见性**：保持 `NoL > 0` 且 `NoV > 0` 规则
9. **几何一致性**：相机、太阳方向、姿态矩阵必须与模块 A 完全一致
10. **遮挡一致性**：Blender 光追遮挡 vs 模块 A `min_hit_distance` 机制需对齐验证

---

## 9. 验证标准

BRDF 精确化不能只看图像效果，必须做数值验证。

### 9.1 数学单元测试

**验证对象**：
- `eval_legacy_phong()`
- `eval_normalized_phong()`
- `eval_ggx_cook_torrance()`

**测试用例**：
1. 正常角度（NoL=0.5, NoV=0.7, NoH=0.8）
2. 掠射角（NoL=0.01, NoV=0.99）
3. 垂直入射（NoL=1.0, NoV=1.0, NoH=1.0）
4. 边界条件（NoL=0, NoV=0）
5. 极端粗糙度（roughness=0.02, roughness=1.0）
6. 极端 Phong 指数（n=1, n=1000）

**验收标准**：
- 无 NaN
- 无 Inf
- 非负
- 极端角度稳定
- Python 与 Blender/OSL 或后处理公式一致（相对误差 < 1e-5）

### 9.2 单平板解析验证

**场景**：
```text
单平板（1m × 1m）
固定太阳方向：L = normalize([1, 0, 0.3])
固定相机方向：V = normalize([0.5, -1, 0.1])
平板法向：N = [0, 0, 1]
```

**比较**：
```text
模块 A OCS 标量
vs
图像积分得到的 OCS-like 标量（sum(pixel_radiance * pixel_area)）
```

**验收标准**：
- 相对误差 < 1% ~ 2%

### 9.3 简单几何验证

**场景**：
1. 单平板
2. 双平板（L 型）
3. 立方体
4. 球或近似球

**比较**：
```text
模块 A OCS 姿态曲线
vs
图像积分 OCS-like 姿态曲线
```

**验收标准**：
- 姿态曲线相关系数 > 0.99
- 平均相对误差 < 3%

### 9.4 真实三件套抽样验证

**场景**：
```text
jinshuzhuti + taiyangnengban + yinshenban
抽样 20~50 个姿态（覆盖 yaw/pitch 范围）
```

**比较**：
```text
模块 A OCS 曲线
vs
图像积分 OCS-like 曲线
```

**验收标准**：
- 平均相对误差 < 5%
- 无明显姿态相关系统偏差
- 峰值位置一致

---

## 10. "精度足够"的定义

对于本项目，BRDF 精度足够并不等于"完全复现真实卫星材料"。

而是满足：

1. ✅ OCS 端与图像端模型一致
2. ✅ 参数物理合理
3. ✅ 参数来源可说明
4. ✅ 图像和 OCS 可数值对齐
5. ✅ 姿态估计结果不被 BRDF 系统误差主导
6. ✅ 材料不确定性通过敏感性实验说明

**论文表述**：
```text
本文关注统一光学前向模型下的图像-OCS 联合姿态估计。材料参数采用文献
合理值，并通过敏感性分析评估材料不确定性对姿态估计的影响。
```

---

## 11. 实施路线图

### Phase 1：LegacyPhong 一致性验证（当前优先）

1. 建立 `brdf_models.py`，实现 `eval_legacy_phong()`
2. 模块 A 接入，验证数值一致
3. 模块 B 建立 OSL shader 或几何缓冲路径
4. 单平板 + 简单几何验证
5. 真实三件套抽样验证

**验收**：相对误差 < 2%，相关系数 > 0.99

### Phase 2：GGX 主模型实施（LegacyPhong 通过后）

1. 实现 `eval_ggx_cook_torrance()`
2. 设置三类部件 GGX 材料参数（nominal 值）
3. 模块 A/B 同时切换到 GGX
4. 小姿态集验证（20~50 姿态）
5. 通过后重跑 medium/full 数据集

**验收**：与 LegacyPhong 相同标准

### Phase 3：材料参数敏感性分析（GGX 通过后）

1. 扰动 `roughness`（±20%）
2. 扰动 `F0`（±10%）
3. 扰动 `base_color`（±10%）
4. 分析姿态估计误差变化

**产出**：敏感性分析报告，论文消融实验章节

---

## 12. 禁止事项

AI 不应：

1. ❌ 继续把 Principled BSDF 说成精确 BRDF
2. ❌ 未审计当前公式就直接重写 BRDF
3. ❌ 未验证一致性就大规模重跑数据
4. ❌ 未说明参数来源就声称真实材料精确
5. ❌ 用 gamma PNG 做定量误差评估
6. ❌ 随意改 `config.py` 默认值
7. ❌ 覆盖已有结果
8. ❌ 在 OCS 端和图像端维护两套独立材料参数

---

## 13. 附录：参考文献

### 13.1 BRDF 模型

- Walter et al. (2007). "Microfacet Models for Refraction through Rough Surfaces." EGSR.
- Burley (2012). "Physically-Based Shading at Disney." SIGGRAPH Course Notes.
- Heitz (2014). "Understanding the Masking-Shadowing Function in Microfacet-Based BRDFs." JCGT.

### 13.2 材料参数

- Palik (1998). "Handbook of Optical Constants of Solids."
- Merl BRDF Database: https://www.merl.com/brdf/
- Substance Material Database: https://substance3d.adobe.com/

### 13.3 卫星光学

- Cognion (2013). "Observations and Modeling of GEO Satellites at Large Phase Angles." AMOS.
- Hall et al. (2019). "Satellite Characterization: Angles and Light Curves." Acta Astronautica.

---

**文档版本**：v1.0  
**最后更新**：2026-05-18  
**下一步**：实施 Phase 1 - LegacyPhong 一致性验证
