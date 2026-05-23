下面是一份可直接保存为：

```text
BRDF_AI_STRATEGY.md
```

或合并进现有 `CLAUDE.md` 的指导策略文件。

```md
# OCS + 图像联合仿真项目 · BRDF 精确化 AI 指导策略

> 当前阶段：论文期精度升级  
> 当前任务：解决模块 A OCS 计算端与模块 B Blender 图像渲染端 BRDF 不一致问题  
> 核心目标：建立一个 OCS 与二维光度图像共享的统一前向散射模型，支撑图像-OCS 联合姿态估计实验。

---

## 1. 项目总目标

本项目不是单纯生成好看的卫星图片，而是建立：

```text
同一 STL 几何
    ↓
同一姿态定义
    ↓
同一太阳方向与探测器方向
    ↓
同一遮挡语义
    ↓
同一 BRDF 模型与材料参数
    ↓
OCS 标量计算 + 二维图像渲染
    ↓
OCS-only / image-only / OCS+image 姿态反演实验
```

因此，BRDF 精确化的核心不是“Blender 看起来像”，而是：

> 模块 A 与模块 B 必须使用同一个 BRDF 数学模型和同一套材料参数。

---

## 2. 当前问题

当前 MVP 状态：

| 模块 | 当前做法 | 问题 |
|---|---|---|
| 模块 A：OCS 计算 | 使用 Python 中的 Phong / Blinn-Phong 类 BRDF | 是当前真实 OCS 计算模型 |
| 模块 B：Blender 渲染 | 使用 Principled BSDF 近似 Phong | 只是视觉近似，不是同一公式 |
| 结果 | 两端 BRDF 不一致 | 不能作为论文中的严格统一前向模型 |

MVP 限制第 1 条已经标注：

> BRDF 是 Principled 近似，非 Phong 像素级镜像；精确匹配需 OSL 或其他精确渲染路径。

本阶段需要解决该问题。

---

## 3. 关于“是否必须使用真实材料参数”

结论：

> 不一定必须与真实材料完全一致，取决于论文实验目标。

### 3.1 如果目标是仿真算法验证

不需要和真实卫星材料完全一样。

需要满足：

1. 材料参数物理合理；
2. 参数来源可说明；
3. OCS 端和图像端使用同一套参数；
4. 做材料参数敏感性分析；
5. 不声称“完全复现真实卫星绝对光度”。

此时论文可以表述为：

> 本文构建物理一致的仿真数据集，用于验证 OCS 与图像联合姿态估计方法。

---

### 3.2 如果目标是与真实观测亮度 / 真实 OCS 绝对值对比

则需要尽量接近真实材料参数。

参数来源应优先来自：

1. 实测 BRDF 数据；
2. 文献；
3. 材料手册；
4. 实际观测数据反标定；
5. 公开光学常数数据库，例如铝的 `eta, k`。

此时还需要辐射定标、大气、望远镜响应、曝光、传感器噪声等额外建模。

---

### 3.3 当前项目推荐定位

当前阶段推荐定位为：

```text
物理一致仿真 + 姿态估计算法验证
```

而不是：

```text
真实卫星绝对辐射复现
```

因此：

- 不要求材料参数完全等于真实卫星；
- 但不能随意设置；
- 应使用文献合理值或典型材料参数；
- 必须做敏感性 / 鲁棒性分析。

推荐论文策略：

```text
主实验：使用一套文献合理的 nominal 材料参数
消融实验：扰动 rho_d / F0 / roughness / metallic
结论：分析材料不确定性对姿态估计误差的影响
```

---

## 4. BRDF 精确化总路线

采用“双层 BRDF 策略”。

---

### 4.1 第一层：LegacyPhong 精确镜像

目的：

> 先解决当前模块 A 与模块 B 不一致的问题。

做法：

1. 审计当前 `ocs_core.py` 中真实使用的 BRDF 公式；
2. 把它冻结为 `LegacyPhong`；
3. 不管它是否完全物理严格，先保证 Python OCS 端和图像端能精确复现同一公式；
4. 用它作为历史 baseline 和工程一致性验证。

需要确认：

- 当前 Phong 是 `N·H` 还是 `R·V`；
- 是否包含归一化项；
- 是否乘了 `cos(theta_i)`；
- 是否乘了 `cos(theta_r)`；
- OCS 积分中面积权重如何处理；
- 遮挡后哪些面元被置零。

---

### 4.2 第二层：GGX / Cook-Torrance 论文主模型

目的：

> 提升物理可信度，用作论文主 BRDF 模型。

推荐模型：

```text
f_r = f_diffuse + f_specular
```

其中：

```text
f_diffuse = (1 - metallic) * rho_d / pi
```

```text
f_specular =
D_GGX(NoH, alpha)
* G_Smith_GGX(NoL, NoV, alpha)
* F(VoH)
/
max(4 * NoL * NoV, eps)
```

方向定义：

```text
N：表面单位法向
L：从表面点指向太阳的单位方向
V：从表面点指向探测器 / 相机的单位方向
H：normalize(L + V)

NoL = max(dot(N, L), 0)
NoV = max(dot(N, V), 0)
NoH = max(dot(N, H), 0)
VoH = max(dot(V, H), 0)
```

只有当：

```text
NoL > 0 且 NoV > 0
```

时，该面元或像素才产生直接太阳散射贡献。

---

## 5. 不再把 Principled BSDF 作为定量模型

Blender 的 Principled BSDF 可以保留为：

- 快速预览；
- 非定量渲染；
- 历史 MVP 对比。

但不能作为论文中的严格 BRDF 模型。

原因：

1. Principled BSDF 公式复杂且 Blender 版本相关；
2. 其 `roughness / specular / metallic` 参数无法精确等价于当前 OCS 端 Phong；
3. 不方便证明模块 A 和模块 B 数学一致；
4. PNG 输出还会受到色彩管理、gamma、tone mapping 影响。

论文定量模型必须是显式写出的 BRDF 公式。

---

## 6. 材料参数策略

### 6.1 参数等级

建议把材料参数分成三个等级：

| 等级 | 含义 | 当前是否需要 |
|---|---|---|
| Level 0 | 自洽仿真参数，只要求两端一致 | 可用于调试 |
| Level 1 | 文献合理参数 / 典型材料参数 | 推荐作为论文主实验 |
| Level 2 | 实测或反标定材料参数 | 后续真实观测对比再做 |

当前项目推荐：

```text
Level 1 + 参数敏感性分析
```

---

### 6.2 推荐材料参数字段

统一材料表中建议包含：

```text
name
brdf_model
rho_d
rho_s
F0
ior
eta
k
metallic
roughness
alpha
anisotropy
base_color
```

第一版可以先做灰度单通道。

如果后续要 RGB：

1. 先保证灰度一致；
2. 再扩展三通道；
3. 每个通道独立设置 `rho_d / F0 / eta / k`。

---

### 6.3 三类部件建议

| 部件 | 推荐处理 |
|---|---|
| `jinshuzhuti` 金属主体 | 使用 `metallic = 1`，优先铝的 GGX 参数 |
| `taiyangnengban` 太阳能板 | 使用低漫反射、较强方向性反射的介质/涂层模型 |
| `yinshenban` 遮光板 | 使用低反照率介质或涂层模型 |

注意：

> 当前阶段不要求完全等于真实卫星材料，但参数必须物理合理，并在论文中说明来源或设置依据。

---

## 7. 工程实现建议

### 7.1 建立 canonical BRDF 模块

建议新增：

```text
ocs_project/01_code/brdf_models.py
```

职责：

```text
eval_legacy_phong()
eval_normalized_phong()
eval_ggx_cook_torrance()
eval_brdf()
```

要求：

1. 支持 numpy 批量计算；
2. 所有方向向量归一化；
3. 对 `NoL <= 0` 或 `NoV <= 0` 返回 0；
4. 防止 NaN / Inf；
5. roughness 设置下限，例如 `roughness >= 0.02`；
6. 所有模块都调用这里，避免多处复制公式。

---

### 7.2 模块 A 修改原则

模块 A 的 `ocs_core.py` 不应继续手写 BRDF。

应改成：

```python
from brdf_models import eval_brdf
```

`ocs_core.py` 只负责：

1. 姿态旋转；
2. 面元法向；
3. 面元面积；
4. 太阳 / 探测器方向；
5. 遮挡；
6. 调用 BRDF；
7. 面元积分。

BRDF 公式本身必须从 `ocs_core.py` 中剥离。

---

### 7.3 模块 B 修改原则

模块 B 需要支持两类渲染模式：

| 模式 | 用途 |
|---|---|
| `principled_preview` | 快速预览，不做定量分析 |
| `exact_brdf` | 论文定量渲染，使用 canonical BRDF |

`exact_brdf` 有两条路线。

---

#### 路线 A：OSL Shader

优点：

- 保留 Blender 渲染流程；
- 可以利用 Cycles 的几何、相机、阴影机制；
- 与当前模块 B 比较接近。

风险：

- OSL 可能只能 CPU 渲染；
- 自定义 BRDF 与 Cycles 能量、阴影、采样机制需要验证；
- 渲染速度可能下降。

---

#### 路线 B：几何缓冲 + Python 后处理

流程：

```text
Blender 输出：
法线 / 深度 / 世界坐标 / 材料 ID / 可见面
    ↓
Python 使用 brdf_models.py 逐像素计算辐射
    ↓
使用同一遮挡逻辑判断太阳可见性
    ↓
输出线性图像
```

优点：

- 最容易保证与模块 A 数学一致；
- 不依赖 Blender Principled；
- 不依赖 OSL closure 细节；
- 便于图像积分与 OCS 对比。

风险：

- 工程量略大；
- 需要处理像素坐标、深度、法线、材料 ID。

推荐优先级：

```text
先评估 OSL；
若 OSL 不稳定或无法定量一致，则采用几何缓冲 + Python 后处理。
```

---

## 8. 定量渲染约束

定量模式必须满足：

1. 不用 Filmic；
2. 不用 gamma 后 PNG 做误差评估；
3. 优先输出线性 EXR / numpy array；
4. 背景为零；
5. 禁止不受控环境光；
6. 禁止不受控间接多次反射；
7. 固定随机种子；
8. 材质法线与模块 A 保持一致；
9. 优先使用 flat face normal；
10. 保持 `NoL > 0` 且 `NoV > 0` 规则；
11. 相机、太阳方向、姿态矩阵必须与模块 A 完全一致。

---

## 9. 验证标准

BRDF 精确化不能只看图像效果，必须做数值验证。

### 9.1 数学单元测试

验证：

```text
LegacyPhong
NormalizedPhong
GGXCookTorrance
```

要求：

- 无 NaN；
- 无 Inf；
- 非负；
- 极端角度稳定；
- Python 与 Blender/OSL 或后处理公式一致。

---

### 9.2 单平板解析验证

场景：

```text
单平板 + 固定太阳 + 固定相机
```

比较：

```text
模块 A OCS
图像积分得到的 OCS-like 标量
```

建议验收：

```text
相对误差 < 1% ~ 2%
```

---

### 9.3 简单几何验证

场景：

1. 单平板；
2. 双平板；
3. 立方体；
4. 球或近似球。

建议验收：

```text
姿态曲线相关系数 > 0.99
```

---

### 9.4 真实三件套抽样验证

场景：

```text
jinshuzhuti + taiyangnengban + yinshenban
```

比较：

```text
模块 A OCS 曲线
图像积分 OCS-like 曲线
```

建议验收：

```text
平均相对误差 < 5%
无明显姿态相关系统偏差
```

---

## 10. “精度足够”的定义

对于本项目，BRDF 精度足够并不等于“完全复现真实卫星材料”。

而是满足：

1. OCS 端与图像端模型一致；
2. 参数物理合理；
3. 参数来源可说明；
4. 图像和 OCS 可数值对齐；
5. 姿态估计结果不被 BRDF 系统误差主导；
6. 材料不确定性通过敏感性实验说明。

论文中可以说明：

> 本文关注统一光学前向模型下的图像-OCS联合姿态估计。材料参数采用文献合理值，并通过敏感性分析评估材料不确定性对姿态估计的影响。

---

## 11. AI 当前执行顺序

当前不要直接写 CNN，不要扩数据集，不要直接大规模重跑。

只执行 BRDF 精确化。

---

### Step 1：BRDF 公式审计

先申请读取：

```text
ocs_project/01_code/materials.py
ocs_project/01_code/ocs_core.py
ocs_project/02_blender/render_batch.py
```

目的：

1. 确认当前模块 A 真实 BRDF 公式；
2. 确认当前材料参数；
3. 确认 Blender Principled 映射方式；
4. 写出 `LegacyPhong` 定义；
5. 找出 A/B 不一致来源。

产出：

```text
brdf_formula_audit.md
```

---

### Step 2：BRDF 统一设计文档

产出：

```text
brdf_precision_design.md
```

内容包括：

1. 方向定义；
2. LegacyPhong 公式；
3. GGX/Cook-Torrance 公式；
4. 材料参数字段；
5. 参数来源策略；
6. 验证标准。

---

### Step 3：建立 canonical BRDF 模块

建议新增：

```text
ocs_project/01_code/brdf_models.py
```

包含：

```text
LegacyPhong
NormalizedPhong
GGXCookTorrance
```

默认先保持旧模型可复现。

---

### Step 4：模块 A 接入统一 BRDF

目标：

```text
ocs_core.py 不再内嵌 BRDF 公式，而是调用 brdf_models.py
```

验收：

```text
LegacyPhong 接入前后 OCS 数值一致或仅有浮点误差。
```

---

### Step 5：模块 B 建立 exact BRDF 渲染路径

优先尝试：

```text
OSL shader
```

如果 OSL 不适合定量一致，则回退：

```text
几何缓冲 + Python 后处理
```

保留：

```text
principled_preview
```

但它只用于快速预览，不用于论文定量结果。

---

### Step 6：建立 BRDF 验证套件

建议新增：

```text
ocs_project/06_brdf_validation/
```

输出到：

```text
结果/BRDF验证/run_YYYYMMDD_HHMMSS/
```

产物包括：

```text
brdf_formula_audit.md
brdf_precision_design.md
math_validation.csv
plane_validation.csv
satellite_subset_compare.csv
fig_ocs_vs_image_integral.png
brdf_validation_report.md
config_used.json
```

---

### Step 7：GGX 小规模验证

只有 LegacyPhong 一致性验证通过后，才进入 GGX。

步骤：

1. 设置 GGX 材料参数；
2. 金属主体使用 metallic 模型；
3. 太阳能板、遮光板使用合理介质/涂层参数；
4. 小姿态集验证；
5. 通过后再重跑 medium/full 数据集；
6. 再进入 CNN / 联合反演 / 消融实验。

---

## 12. 禁止事项

AI 不应：

1. 继续把 Principled BSDF 说成精确 BRDF；
2. 未审计当前公式就直接重写 BRDF；
3. 未验证一致性就大规模重跑数据；
4. 未说明参数来源就声称真实材料精确；
5. 用 gamma PNG 做定量误差评估；
6. 随意改 `config.py` 默认值；
7. 覆盖已有结果；
8. 在 OCS 端和图像端维护两套独立材料参数。

---

## 13. 推荐论文表述

可使用如下表述：

```text
本文建立了一个统一的光学前向仿真框架。OCS 标量与二维光度图像均由同一几何模型、同一姿态、同一太阳-观测几何、同一遮挡判定和同一 BRDF 模型生成。为保证工程一致性，本文首先复现历史 Phong 模型作为 Legacy baseline；随后采用更具物理意义的 GGX/Cook-Torrance 微表面模型作为主实验模型。材料参数采用文献合理值，并通过参数敏感性分析评估材料不确定性对姿态估计结果的影响。
```

---

## 14. 当前最优策略总结

一句话策略：

> 不必一开始追求真实材料完全一致；当前最重要的是让 OCS 和图像两端使用同一个显式 BRDF。论文主实验使用文献合理材料参数，并通过敏感性实验说明材料不确定性的影响。

优先级：

```text
两端一致性 > 显式物理公式 > 合理材料参数 > 敏感性分析 > 真实观测绝对定标
```

当前立即任务：

```text
审计现有 Phong 公式，冻结 LegacyPhong，设计 canonical BRDF，再实现 GGX 主模型。
```
```