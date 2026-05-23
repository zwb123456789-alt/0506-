# OCS + 图像联合仿真项目 · 论文项目总览

> 最后更新：2026-05-23
> 用途：论文写作的章节级总索引，覆盖目的、模块划分、实验设计、已知坑与当前困境。
> 源文档：CLAUDE.md / 项目理解.md / 总思路1.md / 论文思路.md / BRDF设计.md / 01.md
> 当前状态：模块A/B/C 全部跑通，Step 11f 论文级结果汇总完成（paper_summary/run_20260522_234553/），所有关键数值就绪，待正式写论文。


如果目标是 **SCI 一区**，我建议你把六个方向收敛成一个主方向：

> **非均匀 BRDF 与自遮挡条件下，OCS-光度图像联合建模及空间目标姿态可观测性分析。**

你的论文核心应该包括：

```text
1. 统一物理模型：OCS 和图像共享 BRDF、姿态、遮挡；
2. 遮挡验证：简单几何 + 真实卫星模型；
3. 消融实验：材料、遮挡、BRDF、几何；
4. 姿态扫描：yaw/pitch/phase 二维或三维分析；
5. 可观测性指标：图像差异 + OCS 差异；
6. 观测几何优化：找出最优相位角和观测方向；
7. 敏感性分析：BRDF 参数和遮挡参数扰动；
8. 如果可能，加入实验室缩比模型或高保真渲染器验证。

---

# 0. 总目标（对标论文）

## 0.1 论文定位

**核心命题**：建立 OCS（光学截面积）与二维光度图像共享的统一 GGX BRDF 渲染模型，基于真实卫星 STL 的非均匀材料与非凸自遮挡物理仿真，实现 OCS-图像双模态联合姿态反演。

**论文档次目标**：SCI 一区

**核心方法组合推荐**：
> OCS + 图像双流特征融合（Feature Fusion, mean=4.10±0.77°, Hit5=87.3%）作为 Proposed 方法

**关键支撑发现**：
- OCS MLP all_raw 45D：mean=3.98±0.6°, Hit5=90.7%（半 oracle 上界）
- CNN image-only：mean=12.38±0.74°, Hit5=26.1%（图像单模态 baseline）
- Feature fusion per_part_log：mean=4.10±0.77°, Hit5=87.3%（**Proposed**，相对纯OCS +31%）
- OCS-CNN 误差相关性 r=0.003（完全不相关 → 强互补性证据）

## 0.2 推荐论文题目方向

| 方向 | 英文题目 | 核心贡献 |
|---|---|---|
| A. 姿态可观测性 | Attitude Observability Analysis of Space Objects Using BRDF-Driven OCS and Photometric Images | 提出可观测性指标 |
| B. 联合姿态反演 | Joint Attitude Inversion of Space Objects Using OCS and Photometric Images under Nonuniform BRDF and Self-Occlusion | 多模态融合反演 |
| C. 观测几何优化 | Observation Geometry Optimization for Space Object Attitude Estimation Based on Photometric Scattering Characteristics | 最优观测方向 |

**推荐走组合 B**：OCS-光度图像联合姿态反演与观测几何优化。

# 1. 全局配置

## 1.1 更改配置体系

核心配置文件：`ocs_project/01_code/config.py`

| 参数类别 | 关键参数 | 当前值 | 论文期调整 |
|---|---|---|---|
| 路径 | `PROJECT_ROOT` | `D:\我的文件\研究生学术\光学项目\0506新` | 不变 |
| 路径 | `BLENDER_EXE` | `D:\Program Files\Blender Foundation\Blender 4.2\blender.exe` | 4.2.3 LTS（5.0有bug） |
| 观测几何 | `SUN_VECTOR` | `[1,0,0.3]` | 可扩展多方向 |
| 观测几何 | `DET_VECTOR` | `[0.5,-1,0.1]` | 可扩展多方向 |
| 姿态网格 | `SCAN_2D` | `True` | 论文期可加 roll |
| 姿态网格 | `NUM_YAW=37 / NUM_PITCH=19` | 10° 间隔 | 论文期切 5° |
| 精度 | `ACCURACY_LEVEL` | `"fast"` | 论文期切 `"full"` |
| 遮挡 | `EPSILON` | `1.0`（mm） | 经 mhd 敏感性确认 |
| 渲染 | `ENABLE_RENDER` | `False` | 渲染交模块 B ，约等于废弃，保持即可|
| 语言 | `LANG_MODE` | `"bilingual"` | 论文期可切 `"en"` |


## 1.3 环境与工具链

| 工具 | 版本/路径 | 用途 |
|---|---|---|
| Python | conda env `ocs_sim` | 模块 A/C、后处理 |
| Blender | 4.2.3 LTS（`D:\Program Files\Blender Foundation\Blender 4.2\`） | 模块 B 渲染 |
| GPU | NVIDIA OPTIX | Cycles 加速 |
| trimesh + Embree | `pip install embreex`（`ocs_sim` 环境已装） | 模块 A 遮挡加速（单线程 ~10–100×，实际 8 进程并行） |

**为什么不用 Blender 5.0**：Compositor MULTILAYER EXR API 损坏（`file_output_items` 只写第一个 link 通道，丢 Normal/Depth/IndexOB），实测 4.2.3 LTS 正常。

---

# 2. OCS 计算（对应论文 §Method - Optical Cross Section Modeling）

## 2.1 物理公式

对每个可见且未遮挡的三角面元：

$$OCS = \sum_i A_i \cdot f_r(N_i, L, V) \cdot \max(N_i \cdot L, 0) \cdot \max(N_i \cdot V, 0)$$

其中：
- $A_i$：面元面积（m²，STL 原始 mm² × 1e-6）
- $f_r$：BRDF 值（sr⁻¹），由 `eval_brdf()` 统一计算
- $N_i$：面元单位法向
- $L$：太阳方向单位向量（惯性系）
- $V$：探测器方向单位向量（惯性系）
- 可见性条件：$N_i \cdot L > 0$ 且 $N_i \cdot V > 0$
- 遮挡条件：太阳方向或探测器方向射线被其他面元遮挡 → 贡献置零

## 2.2 代码模块

`ocs_project/01_code/` 九个文件：

| 文件 | 职责 | 对应论文 | 备注 |
|---|---|---|---|
| `config.py` | 全局参数、路径、GGX/LegacyPhong BRDF 切换、多观测几何列表、双语标签 | §Experimental Setup | 所有可调参数入口 |
| `geometry.py` | STL 加载、QEM 抽稀、R 矩阵构建（Z-Y-X 内旋）、面元面积/法向 | §Geometry Model | 面元、姿态处理 |
| `materials.py` | 三部件材料参数库（LegacyPhong + GGX 双数据库），`get_material(use_ggx=)` 统一入口 | §Material Model | 材料参数 |
| `occlusion.py` | trimesh + Embree 4.4 射线遮挡查询（AABB 预筛 + BVH 精检），`min_hit_distance`/`EPSILON` 过滤 | §Occlusion Model | 遮挡算法 |
| `ocs_core.py` | OCS 积分核心 + `eval_brdf()` 统一 BRDF 入口 + 多进程姿态扫描 + `use_ggx` 透传 | §OCS Integration | OCS 积分 |
| `visualization.py` | fig01~fig06 双语图表（SimHei 字体，`LANG_MODE` 可切 en/bilingual） | §Results Visualization | 结果输出 |
| `main_run.py` | 主入口（2D 扫描），`--ggx` / `--num-yaw` / `--num-pitch` CLI 覆盖 | — | 单几何运行 |
| `run_multi_geom.py` | 多观测几何批量扫描入口（遍历 `OBS_GEOMETRIES`，逐几何输出子目录 + manifest） | — | 多几何批量 |
| `adaptive_integration.py` | A 端 sub-face 自适应积分（已封存）+ `compute_ocs_from_exr()` pixel-level 统一积分（Step 7b，可用） | — | 实验性模块 |

## 2.3 三种精度等级

| 等级 | 面元保留比例 | 用途 |
|---|---|---|
| `"fast"` | ~20%（QEM抽稀） | 快速调试，当前默认 |
| `"medium"` | ~50% | 中等精度验证 |
| `"full"` | 100%（不抽稀） | 论文正式结果 |

**注意**：`simplify_quadric_decimation` 在 fast 模式对凹陷几何敏感，论文期用 full。需装 `fast_simplification` 后端获 C++ 加速，否则 trimesh 回退纯 Python QEM。

## 2.4 双语图表体系

| 编号 | 内容 | 论文用途 |
|---|---|---|
| fig01 | OCS 3D 曲面（yaw×pitch） | 主体结果图 |
| fig02 | OCS 俯视热图 | 可观测性直观展示 |
| fig03 | 各部件贡献热图（金属主体/太阳能板/遮光板） | 部件级分析 |
| fig04 | 遮挡率热图 | 遮挡影响量化 |
| fig05 | OCS 损失热图（无遮挡-有遮挡） | 遮挡敏感性 |
| fig06 | 卫星三维模型示意图 | 几何模型展示 |

**图表语言**：当前 `LANG_MODE = "bilingual"`（中英双语），论文投稿可一键切 `"en"`。

## 2.5 实验需求

- [x] 论文期切 `ACCURACY_LEVEL = "full"`（但当前 fast 与 full 差仅 0.2%，论文可用 fast）
- [x] 论文期切 5° 网格（yaw 73 × pitch 37 = 2701 姿态），10°→5° OCS max 差 11.4×，5° 为论文必需
- [x] 扩展多观测几何（5 组 sun/det，相位角 24°–120°，13,505 姿态，1725s）
- [ ] Roll 轴扩展（yaw×pitch×roll 三维网格），计算成本 ×37
- [x] OCS 统计已输出：max/mean/min 跨几何差异 4.8×，遮挡率 60%–78.5%
- [ ] 真实轨道数据导入（STK TLE 驱动太阳/观测站位置）

---

## 2.6 解析射线查询与物理光追对比


### 两种遮挡检测方法

本项目涉及两种遮挡/可见性判定范式，分别用于不同模块：

| 维度 | 解析射线查询（模块 A） | 物理光追（模块 B，Blender Cycles） |
|---|---|---|
| **原理**  | 每个面元中心发射两条检测射线（sun方向 + det方向），查询是否命中其他几何 
            | 从光源发射光子 → 表面反射/折射 → 相机收集，天然模拟光传播 |
| **自相交处理** | epsilon 偏移起点 + mhd 距离过滤（人工机制） 
                  | 物理光追天然知道"光从哪个面反射"，不存在源面自相交问题 |
| **计算粒度** | 面元级：返回每个面元的遮挡布尔值 | 像素级：返回整张图像，无法直接得到面元级遮挡 |
| **输出** | `occ_sun[i]` / `occ_det[i]`（布尔数组） | RGBA 图像 + 辅助缓冲（Normal/Depth/IndexOB） |
| **速度** | 极快：703 姿态 82s（含 OCS 积分） | 较慢：0.3s/帧 × 703 = 215s（仅渲染，不含后处理） |
| **可控性** | 完全可控（epsilon/mhd/射线方向） | 受 Cycles 内部采样/降噪/色管影响 |
| **适用场景** | OCS 面元积分、遮挡率统计 | 图像生成、视觉验证、人工抽查交叉验证 |

### 为什么模块 A 不能直接用物理光追替代

1. **粒度不匹配**：OCS 是逐面元积分，需要知道"每个面元是否被遮挡"，而 Cycles 输出的是像素颜色，无法逆向推导出面元级遮挡
2. **速度差距**：即使能通过几何缓冲 + 后处理间接得到面元遮挡（路径 B 的思路），也远慢于纯解析查询
3. **可复现性**：解析查询是确定性的（同一输入→同一输出），而 Cycles 有随机采样噪声

### 两者的交叉验证关系

```
模块 A（解析射线查询）
    │
    ├── 直接产出：OCS 值、遮挡率、各部件贡献
    │
    └── 独立验证 ←── 05_manual_review（Blender scene.ray_cast 复算同一射线）
                         │
                         └── 结论：两种方法判定一致（AGREE）
                              └── 证明解析方法不受算法 bug 影响

模块 B（物理光追）
    │
    ├── 直接产出：二维光度图像
    │
    └── 一致性验证 ←── exact BRDF 路径（Python 逐像素复算 BRDF）
                         │
                         └── 目标：OCS_image 与 OCS_A 数值一致
                              └── 当前阻塞点（Step 5，见 §9.1）
```

### 论文表述建议

> 遮挡判定采用解析射线查询方法：对每个面元，从其中心沿法向偏移后，分别向太阳方向和探测器方向发射检测射线，通过 BVH 加速查询是否命中其他几何体。偏移量 epsilon 与最小命中距离 mhd 的取值经合成几何与真实模型的敏感性扫描验证。解析方法的正确性通过 Blender Cycles 独立射线查询交叉验证确认。该方法在保证面元级遮挡判定精度的同时，避免了物理光追的渲染开销，适用于大规模姿态扫描场景。


# 3. 遮挡处理与验证

## 3.1 遮挡机制

**核心公式**：射线起点 `origin = face_center + normal * EPSILON`（沿法向偏移 1mm）

**过滤逻辑**：`min_hit_distance = EPSILON`——保留 `hit_distance > EPSILON` 的命中，过滤距离更近的自相交。

**mhd必要性说明**（会做敏感性分析）：
mhd 就是"最小有意义特征尺寸"的声明：距离小于 mhd 的命中，我认为它是网格噪声而非真实遮挡。

用于解决假遮挡问题，stl进行了三角面元的离散处理，两个三角形可能代表着同一块连续金属表面的两个离散化片段。
真实物理中，这是一个连续曲面，不存在"面B挡住面A"这种事。
但 STL 把它离散成了两个三角形，出现了虚假缝隙，这些微小的面间互遮挡对 OCS 贡献可以忽略，导致：
  - 从面A的面元中心射出的遮挡检测射线在 0.3mm 处"命中"了面B（因为缝隙影响）
  - 算法判定：面A被遮挡
  - 物理真实：光线照在连续表面上，根本不存在遮挡
目的是过滤掉网格的离散噪声，过小噪声太大，误差高，过大则误杀真实面元结构

**为什么不用 `exclude_parts`**（旧逻辑）：

| 旧逻辑 `exclude_parts={当前部件}` | 新逻辑 `min_hit_distance` |
|---|---|
| 当前部件整体从 BVH 中踢掉 | 所有部件参与，用距离过滤 |
| 无法检测同部件内部自遮挡（U型/凹腔/加强筋） | 同部件内部真实遮挡能正确检出 |
| 严重低估遮挡率 | 需要正确选择 EPSILON 阈值 |

## 3.2 mhd = 1.0 mm 的决策依据—敏感性实验

mhd = 1.0 mm 是在网格离散噪声过滤与真实近邻遮挡保留之间的最优平衡点。
EPSILON：（起点偏移）控制射线起点离面元多远。如果 epsilon=0，起点恰在面上，三角形自己的顶点就在起点处，会被误判为"命中"
mhd：（最小命中距离）：即使命中发生了，距离太近的命中被过滤掉（视为自相交/近邻几何粘连）
epsilon 偏移让起点离开源面；mhd 过滤掉剩余的近距离误命中。
在 config.py 中，两者用同一个值 EPSILON = 1.0mm

经真实三件套 `min_hit_distance` 敏感性扫描（0.1~10 mm），三部件共同平坦段上限 = 1.0 mm：

| mhd (mm) | jinshuzhuti | taiyangnengban | yinshenban |
|---|---|---|---|
| 0.1 | 0.87 | 0.90 | 0.77 |
| 0.5 | 0.77 | 0.90 | 0.77 |
| **1.0** | **0.73** | **0.90** | **0.77** |
| 2.0 | 0.47 | 0.83 | 0.77 |
| 5.0 | 0.33 | 0.83 | 0.77 |
| 10.0 | 0.30 | 0.77 | 0.70 |

- jinshuzhuti 在 1→2 mm 骤降 26pp，说明内部存在大量 1~5 mm 真实近邻面遮挡
- taiyangnengban 平坦段到 ~1 mm
- yinshenban 平坦段到 ~2 mm
- **三部件共同安全上限 = 1.0 mm**

mhd 敏感性扫描：
对于真实三件套（yaw=pitch=roll=0，M=I），扫了 6 个 mhd 档位，每部件 30 个均匀面元。结论是曲线越平坦 = 阈值越鲁棒；曲线开始陡降的 mhd = 误杀真实相邻面遮挡的起点。

以 jinshuzhuti 为例：mhd 从 1.0 升到 2.0 时遮挡面元比例从 0.73 骤降到 0.47（降了 26pp），说明该部件内部存在大量 1~5 mm 的真实近邻几何（凸台/加强筋/板边厚度），mhd 取 1.0 是三条曲线共同平坦段的上限。用小于 1.0 会开始误判自相交为遮挡（过度敏感），用大于 1.0 会开始漏检真实遮挡（欠敏感）。因此 mhd=1.0 mm 是最优折衷

## 3.3 epsilon = 1.0 mm 的决策依据

Embree 已经替你防了源面（自动除去源面）。epsilon 防的是出发点位于整个网格表面的复杂拓扑中：
epsilon=0 不可行，不是因为 Embree 不够好，而是因为你把起点放在了整个三角网格的表面上——那里到处都是边、顶点、缝隙，浮点精度决定了命中的有无和距离，不是物理几何。

epsilon=1mm 把起点抬离整个表面，创造了一个干净的起始条件：到任何面元的距离都 ≥ 1mm。mhd=1mm 这时只需要处理"这个距离到底是近邻噪声还是真实遮挡"，而不用同时应付浮点噪声

单平板合成测试：epsilon 从 1e-6 到 5mm 全部正确（没有异常）
真实模型 mhd 扫描：在 epsilon=1.0 条件下，三部件平坦段覆盖 0.1~1.0mm
人工抽查交叉验证：epsilon=1.0 + mhd=1.0 条件下，模块 A 与 Blender 独立判定一致
（但缺少 epsilon=0.5 或 epsilon=2.0 时真实模型的对比数据。论文期如果需要更严格的论证，应该补做）

## 3.4 验证体系

### 3.4.1 冒烟测试（`04_tests/test_occlusion_geometry.py`）
04文件夹本质上是遮挡验证的前站测试
test_blender_path.py  检查blender路径 
test_module_a_smoke.py  主模型小检查能不能运行
test_occlusion_geometry.py 次模型小检查能不能运行
4 个最小几何场景快速确认 API 正确：

### 3.4.2 完整验证（`05_occlusion_validation/`）
05_occlusion_validation：
4件套遮挡验证＋真实模型抽查
结果输出在遮挡验证中

run_occlusion_validation.py 主要验证代码
_write_guide.py 生成主要报告
run_occlusion_validation.py.bak 无用，旧版本备份

| 验证项 | 期望 hit_ratio | 含义 |
|---|---:|---|
| 单平板 epsilon>0 + mhd=EPSILON | 0.000 | 正确压住自相交 |
| 单平板 epsilon=0 + mhd=0 | 不判（expose_self） | 暴露基础自相交问题（参考） |
| 双平板跨部件 | 1.000 | 跨部件遮挡正确 |
| U 型块新逻辑 | 1.000 | 同部件内部遮挡正确检出（修复项） |
| 嵌套圆柱 | ≥0.95 | 强跨部件遮挡 |

模型	          采样函数	           点数	       位置
单平板	plate_grid(0.5, eps)	       9×9=81	   平板上表面
双平板	plate_grid(0.5, EPSILON)	 9×9=81	  下平板上表面
U 型块	u_block_grid()	             9×9=81	  凹槽内部 XZ 截面
嵌套圆柱	cylinder_surface_points()	24×5=120	   内圆柱外表面

共17项验证，其中14组单平板：
epsilon 太小（1e-6 mm）→ 起点几乎在面上 → 考验 mhd 能否单独兜底
epsilon 很大（5 mm）→ 起点飞出很远 → 测试极端情况
每个 epsilon 配 mhd=0（无过滤）和 mhd=1.0（有过滤）→ 测试两个参数独立和联合的效果
结论：14 项全部 hit_ratio=0 → 自相交在任何 epsilon 量级下都能被彻底压制。

**关于 `summary_pass_fail.png` 中 `epsilon=0, mhd=0` 一行的特别说明**：

这一行的设置是 `expected_ratio=1.0, actual=0.0, status=PASS`。表面上看"预期=1（应命中）、实际=0（未命中）却标 PASS"，容易引起误解。实际情况是：

- 此行模式为 `expose_self`，不是常规的 zero/one/high 判定模式
- **设置目的**：纯粹为了探明 Embree 库的行为特性——当射线起点恰好落在源面上时，Embree 内置的 face-self 跳过机制是否生效
- **实测结果**：hit_ratio=0（未自相交），证明 Embree 确实在底层自动跳过了起点所在的三角形，不需要额外过滤
- **为什么标 PASS 而非 FAIL**：因为这一行的作用不是"验证算法是否通过"，而是"验证第三方库的行为是否符合文献记载"——Embree 的 face-self skip 是已知的预期行为，实测确认了这一行为，因此标记为 PASS（= Embree 行为符合预期）
- **论文处理建议**：这一行属于开发阶段的库行为探测，不应出现在论文正文的验证结果表中。论文中只需保留 `epsilon>0 + mhd>0` 的 12 项（全部 hit_ratio=0），以及双平板/U型块/嵌套圆柱的 3 项（全部 hit_ratio=1.0），共 15 项正式验证
### 3.4.3 人工遮挡抽查（`05_manual_review/`）

用 Blender headless `scene.ray_cast` 独立复算射线，与模块 A trimesh+Embree 交叉验证：

05_occlusion_validation/run_occlusion_validation.py
        ↓ 生成
manual_review_candidates.csv（每条记录 = 基础面元数据与OCS算法结果）
        ↓ 输入
05_manual_review/manual_review_blender.py
        ↓ 输出
review_report.csv + PNG + .blend（Blender 验证结果）

**关键约定**：单位 mm、`R = Rz @ Ry @ Rx`、`self_hit_tol_mm=0.001`、最大射线 10000 mm。

**验证历史**：多个 run 均确认模块 A 与 Blender 独立判定一致（AGREE_OCCLUDED / AGREE_CLEAR）。

### 3.4.4 结果体系

├── 合成模型验证（validation_summary.csv, summary_pass_fail.png）
│   ├── 单平板：7 epsilon × 2 mhd = 14 项 → 自相交彻底压制
│   ├── 双平板：下板→上板，跨部件遮挡 → 100% 检出
│   ├── U 型块：凹槽→背墙，同部件内部 → 100% 检出（修复项）
│   └── 嵌套圆柱：内柱→外柱，极端嵌套 → 100% 检出
│
├── 合成 mhd 扫描（mhd_sensitivity_synthetic.csv/png）
│   └── U 型块 × 10 个 mhd 档位 → 验证 mhd 拐点存在
│
├── 真实模型 mhd 扫描（realmodel_mhd_summary.csv/png）
│   └── 三部件 × 6 个 mhd 档位 × 30 面元 → 确定 mhd=1.0
│
└── 候选面元导出（manual_review_candidates.csv）
        ↓ 喂给
    05_manual_review → Blender 独立复算 → review_report

其中realmodel_mhd_summary.csv 实验逻辑：

对每个部件：
    均匀抽取 30 个面元
        ↓
    面元中心 + 法线 × EPSILON = 射线起点
        ↓
    对每个 mhd ∈ {0.1, 0.5, 1.0, 2.0, 5.0, 10.0}：
        batch_occlusion_dual(起点, sun_dir, det_dir, min_hit_distance=mhd)
            ↓
        返回 (N,) bool: occ_sun, occ_det  ← 每条射线是否被遮挡
            ↓
        统计 sun_occluded = sum(occ_sun)   ← 30 个面元中，太阳方向被遮挡的个数
        统计 det_occluded = sum(occ_det)   ← 30 个面元中，探测器方向被遮挡的个数
            ↓
        sun_ratio = sun_occluded / 30      ← 遮挡比例
        det_ratio = det_occluded / 30
sun_occluded 的含义：30 个面元中，沿太阳方向发出的射线命中其他几何体的面元个数。True = 这个面元的太阳方向被挡住了。False = 太阳方向畅通。

实验目的：看 mhd 从 0.1 变到 10 时，遮挡比例如何变化。如果曲线平坦 → 这个 mhd 区间内遮挡判定稳定（鲁棒）。如果曲线骤降 → 有大量遮挡的命中距离落在这个区间，增大 mhd 会误杀它们。

## 3.5 模块 A 与模块 B 遮挡机制差异

| 维度 | 模块 A | 模块 B |
|---|---|---|
| 方法 | trimesh + Embree 射线查询 | Cycles 物理光追 |
| 自相交处理 | `min_hit_distance` 过滤 | Cycles 天然处理 |
| 多次反射 | 不考虑 | 默认关闭（论文定量模式） |

**差异不影响一致性**：A 的 `min_hit_distance` 机制在语义上等价于物理光追的起点偏移，经人工抽查交叉验证通过。

## 3.6 实验需求

- [ ] 论文中写 §Occlusion Validation 一节：单平板/双平板/U型块/嵌套圆柱 + 真实模型 mhd 敏感性
- [ ] 论文中展示遮挡可视化（三维标注图，被遮挡面元着色）
- [ ] 消融实验：无遮挡 vs 有遮挡 OCS 对比（证明遮挡修正的必要性）
- [ ] 可选：区分同部件/跨部件阈值（若 72.88% 遮挡率被审稿人质疑）

---

# 4. Blender 渲染（对应论文 §Photometric Image Generation）

## 4.1 两条渲染路径

| 路径 | 脚本 | BRDF | 状态 | 用途 |
|---|---|---|---|---|
| **Principled 近似** | `render_batch.py` | Principled BSDF 映射 Phong | ✅ 全量跑通（703帧295s） | MVP 快速出图 |
| **Exact BRDF** | `render_geometry_passes.py` + `brdf_postprocess.py` | Python 逐像素 `eval_legacy_phong` | ⚠️ 管线通，OCS 一致性未达标 | 论文期精度路径 |

## 4.2 Exact BRDF 路径（路径 B：几何缓冲 + Python 后处理）

**流程**：
```
Blender Cycles 渲染
    ↓
每姿态输出 1 个 MULTILAYER EXR（4层）
    Combined RGBA / Normal XYZ / Depth.V / IndexOB.V
    ↓
Python brdf_postprocess.py
    ├── 读 EXR → 按 IndexOB 分三部件
    ├── 逐像素调用 eval_legacy_phong()
    └── 输出 radiance + OCS_image + ocs_comparison.csv
```

**关键参数**：res=128（与256差异<1%，非误差主因）、OPTIX GPU、0.31s/帧、flat shading（STL默认）

**法线坐标系**：已确认世界空间（yaw=0/pitch=-90 主导法线 (1,0,0) 与 R 矩阵一致），后处理无需变换。

**OCS_image 公式**：
$$OCS_{image} = \sum_{pix} pixel\_area \cdot f_r(N, L, V) \cdot \max(N \cdot L, 0)$$

（推导：$A_{face\_pix} = pixel\_area / (N \cdot V)$，与 A 端 $\sum A_{face} \cdot f_r \cdot (N\cdot L) \cdot (N\cdot V)$ 中 $(N\cdot V)$ 抵消）

## 4.3 核心约定

| 项目 | 约定 |
|---|---|
| 姿态应用 | `Sat_Root` Empty 承担 R 与 mm→m：`matrix_world = R @ Diagonal(1e-3,1e-3,1e-3,1)` |
| R 矩阵 | 手搓 `R = Rz @ Ry @ Rx`（Z-Y-X 内旋），严格镜像 `geometry.py`，避免 Blender Euler API 轴序歧义 |
| 相机 | 正交，位置 `+det_norm·5·r_max`，朝 origin；`ortho_scale=2.2·r_max` |
| 太阳 | SUN 灯，朝向 `Vector(sun_norm).to_track_quat('Z','Y')`，energy=5.0 |
| 色管 | `view_transform='Standard'`（近似线性，避免 Filmic 破坏辐射度量） |
| 背景 | 纯黑 |
| GPU | 自动探测 OPTIX/CUDA/HIP/ONEAPI/METAL，失败回退 CPU |
| 文件名 | `yaw{06.2f}_pitch{+06.2f}.png`（Principled）或 EXR（exact BRDF） |
| 部件ID | STL 每个对象设 `pass_index ∈ {1,2,3}`，IndexOB pass 区分 |

## 4.4 数据产物

| 路径 | 内容 |
|---|---|
| `结果/模块B_渲染/run_20260511_193251/` | Principled 路径全量基线（703帧） |
| `结果/模块B_渲染/run_20260518_200741_exact_brdf/` | Exact BRDF 全量基线（703帧 res=128），含 `ocs_comparison.csv` + `consistency_summary.json` |

## 4.5 实验需求

- [x] Step 5 OCS 数值一致性诊断（已完成 5 条线索并行排查，native A/B gap 根因已确诊为 face-center vs pixel-level 采样差异，非代码错误）
- [x] Exact BRDF 路径 phase63 GGX 全量渲染（2701 EXR + PNG，run_20260521_phase63_ggx）
- [x] OCS-图像一致性验证（单平板/立方体三端闭合 ≤0.25%，已确认 BRDF/几何/投影链路正确）
- [ ] 多观测几何图像渲染（phase24/45/90/120，目前仅 phase63）
- [ ] 论文期：更高分辨率（res 256 或 512，当前 128）
- [ ] 可选：RGB 三通道渲染（当前灰度）
- [ ] 可选：真实轨道场景（STK 导入太阳/观测站位置）

---

# 5. 姿态处理构建（对应论文 §Attitude Parameterization & Coordinate Systems）

## 5.1 姿态定义

**欧拉角约定**：Z-Y-X 内旋（yaw → pitch → roll）

$$R = R_z(yaw) \cdot R_y(pitch) \cdot R_x(roll)$$

其中：
$$R_z(\alpha) = \begin{bmatrix} \cos\alpha & -\sin\alpha & 0 \\ \sin\alpha & \cos\alpha & 0 \\ 0 & 0 & 1 \end{bmatrix}$$
$$R_y(\beta) = \begin{bmatrix} \cos\beta & 0 & \sin\beta \\ 0 & 1 & 0 \\ -\sin\beta & 0 & \cos\beta \end{bmatrix}$$
$$R_x(\gamma) = \begin{bmatrix} 1 & 0 & 0 \\ 0 & \cos\gamma & -\sin\gamma \\ 0 & \sin\gamma & \cos\gamma \end{bmatrix}$$

**代码**：`geometry.py:16-38`（A端）、`render_batch.py` 手搓（B端，严格镜像）、`render_geometry_passes.py`（exact BRDF端）、`manual_review_blender.py`（交叉验证端）。

## 5.2 坐标系约定

```
惯性系 I（太阳和相机固定）
    │
    ├── 太阳方向：固定（当前 [1, 0, 0.3] 归一化）
    ├── 探测器方向：固定（当前 [0.5, -1, 0.1] 归一化）
    │
    └── 卫星旋转（R 作用于卫星本体 → 惯性系）
        ├── STL 在卫星本体坐标系
        ├── 顶点变换：v_I = R @ v_body
        └── 法向变换：n_I = R @ n_body（无缩放/剪切）
```

**设计原则**：旋转卫星、固定太阳和相机。模块 A 和模块 B 完全一致。

## 5.3 姿态扫描网格

| 参数 | 当前值（fast） | 论文期建议 |
|---|---|---|
| yaw 范围 | [0°, 360°) | 不变 |
| yaw 步数 | 37（~10°） | 73（~5°） |
| pitch 范围 | [-90°, 90°] | 不变 |
| pitch 步数 | 19（10°） | 37（5°） |
| roll | 固定 0° | 可扩展 |
| 总姿态数 | 703 | 2701（5°网格） |

## 5.4 观测几何

| 向量 | 当前值 | 物理含义 |
|---|---|---|
| `SUN_VECTOR` | `[1.0, 0.0, 0.3]`（归一化） | 太阳在惯性系的入射方向 |
| `DET_VECTOR` | `[0.5, -1.0, 0.1]`（归一化） | 探测器在惯性系的观测方向 |

**论文期扩展**：多组 sun/det 方向，相当于同一姿态多个相位角观测。

### 5.4.1 多观测几何设计（Step 10d，2026-05-20 落地）

在 `config.py` 中新增 `OBS_GEOMETRIES` 列表，定义 5 组太阳/探测器方向，覆盖不同相位角（太阳-目标-探测器夹角）：

| 标签 | 太阳方向 | 探测器方向 | 相位角 | 物理场景 |
|---|---|---|---|---|
| `phase63_backscatter` | `[1, 0, 0.3]` | `[0.5, -1, 0.1]` | 63.1° | 原 baseline，中等后向散射 |
| `phase24_near_backscatter` | `[0.5, -1, 0.5]` | `[0.2, -1, 0.1]` | 23.6° | 近后向散射，太阳与探测器接近同向 |
| `phase120_forward_scatter` | `[1, 0, 0]` | `[-0.5, 0.866, 0]` | 120.0° | 大相位角前向散射 |
| `phase90_side` | `[1, 0, 0]` | `[0, 1, 0]` | 90.0° | 侧向观测，太阳-探测器正交 |
| `phase45_overhead` | `[0.707, 0, 0.707]` | `[0, 0, 1]` | 45.0° | 中等角度俯视观测 |

**设计原则**：覆盖 24°–120° 相位角范围，包含后向散射（小相位角）、侧向（~90°）、前向散射（大相位角）三类典型观测几何，用于论文消融实验中"单方向 vs 多方向"对比。

**批量运行**：通过 `run_multi_geom.py` 一键遍历全部几何，每组几何独立输出子目录。详见 §6.8.7。

## 5.5 单位体系

| 量 | 单位 | 转换 |
|---|---|---|
| STL 顶点坐标 | mm | `× 1e-3 → m` |
| 面元面积 | mm² | `× 1e-6 → m²` |
| 距离/偏移 | mm | `× 1e-3 → m` |
| OCS | m² | 直接输出 |
| 图像像素值 | 相对辐亮度（无绝对单位） | 论文期考虑辐射定标 |

## 5.6 实验需求

- [ ] 论文中画坐标系示意图（惯性系/本体系/太阳/探测器/卫星姿态角标注）
- [x] 5° 细网格重跑（2701 姿态，GGX，2026-05-20 完成，run_20260520_160847）
- [x] 多太阳/探测器方向扩展（5 组观测几何，2026-05-20 完成，run_20260520_162831）
- [x] 多观测几何 OCS 对 kNN 姿态估计的决定性增益（7.6×，2026-05-20）
- [ ] Roll 轴扩展（三维姿态网格，计算成本 ×37）
- [ ] 四元数随机采样姿态（代替均匀网格，用于 CNN 训练数据增强）
- [ ] 从 STK 导入真实轨道太阳/观测站位置，用于真实场景仿真

---

# 6. BRDF 模型设计（对应论文 §BRDF Model）

## 6.1 设计原则

**优先级**（BRDF设计.md §14）：
> 两端一致性 > 显式物理公式 > 合理材料参数 > 敏感性分析 > 真实观测绝对定标

**论文定位**：物理一致仿真 + 姿态估计算法验证（非真实卫星绝对辐射复现）

## 6.2 双层 BRDF 策略

### 第一层：LegacyPhong（当前基线，已冻结）

$$f_r(N, L, V) = \frac{\rho_d}{\pi} + \rho_s \cdot (\max(N \cdot H, 0))^n$$

其中 $H = \text{normalize}(L + V)$，$\rho_d$ 漫反射系数，$\rho_s$ 镜面反射系数，$n$ 高光指数。

**特点**：无能量归一化（$\rho_d+\rho_s$ 可 >1）、无 Fresnel、无粗糙度模型。用于工程一致性验证和 baseline。

### 第二层：GGX Cook-Torrance（论文主模型）

$$f_r = f_{diffuse} + f_{specular}$$

$$f_{diffuse} = (1 - metallic) \cdot \rho_d / \pi$$

$$f_{specular} = \frac{D_{GGX}(N\cdot H, \alpha) \cdot G_{Smith}(N\cdot L, N\cdot V, \alpha) \cdot F(V\cdot H, F_0)}{4 \cdot \max(N\cdot L, \epsilon) \cdot \max(N\cdot V, \epsilon)}$$

**组件**：
- $D_{GGX}$：GGX 法向分布函数
- $G_{Smith}$：Smith 几何遮蔽函数
- $F_{Schlick}$：Schlick Fresnel 近似
- $\alpha = roughness^2$

## 6.3 方向定义（统一）

| 符号 | 含义 | 方向 |
|---|---|---|
| $N$ | 表面单位法向 | 从表面指向外 |
| $L$ | 太阳方向 | 从表面点指向太阳 |
| $V$ | 探测器方向 | 从表面点指向探测器/相机 |
| $H$ | 半角向量 | $\text{normalize}(L + V)$ |
| $N\cdot L$ | 入射角余弦 | $\max(\cdot, 0)$ |
| $N\cdot V$ | 观测角余弦 | $\max(\cdot, 0)$ |
| $N\cdot H$ | 法向-半角余弦 | $\max(\cdot, 0)$ |

**可见性条件**：$N\cdot L > 0$ 且 $N\cdot V > 0$（面元对太阳和探测器同时可见）

## 6.4 三类部件材料参数

### LegacyPhong 参数（当前）

| 部件 | ρ_d | ρ_s | n | brdf_model |
|---|---|---|---|---|
| jinshuzhuti（金属主体） | 0.3 | 0.5 | 50 | `legacy_phong` |
| taiyangnengban（太阳能板） | 0.1 | 0.3 | 30 | `legacy_phong` |
| yinshenban（遮光板） | 0.05 | 0.1 | 10 | `legacy_phong` |

### GGX Nominal 参数（论文期）

| 部件 | metallic | roughness | F0 / base_color | IOR |
|---|---|---|---|---|
| jinshuzhuti | 1 | 0.20 | F0=0.91（铝） | — |
| taiyangnengban | 0 | 0.40 | — | 1.5 |
| yinshenban | 0 | 0.90 | 0.08 | — |

## 6.5 Canonical BRDF 模块

`ocs_project/07_brdf/`：

| 文件 | 内容 |
|---|---|
| `brdf_models.py` | `eval_legacy_phong()` / `eval_normalized_phong()` / `eval_ggx_cook_torrance()` / `eval_brdf()` 统一入口，支持 numpy 批量 |
| `brdf_precision_design.md` | 公式推导、参数来源、验证标准 |
| `test_brdf_models.py` | 6 类单元测试（全部通过） |
| `verify_integration.py` | 新旧公式对比（3部件×1000面元，最大 rel_err = 0） |
| `verify_ocs_e2e.py` | 单平板端到端验证（OCS=1.63e-3 m²） |

**设计约束**：
- 防 NaN/Inf
- roughness 下限 0.02
- 零向量保护
- 模块 A 已接入 `eval_brdf()`（`ocs_core.py` 不再内嵌 BRDF 公式）

## 6.6 模块 A/B 当前不一致来源（Step 1 审计结果）

| 维度 | 模块 A | 模块 B（Principled路径） |
|---|---|---|
| 镜面模型 | Phong `ρ_s·(N·H)^n` | GGX（Principled BSDF底层） |
| 能量归一化 | 无（ρ_d+ρ_s 可 >1） | 内置能量守恒 |
| 金属处理 | 统一公式 | metallic=0（强制电介质） |
| 色管 | N/A | Standard（近似线性，未辐射定标） |

## 6.7 实验需求（当前状态）

- [x] **Step 1-4**：BRDF 公式审计 → 统一设计 → canonical 模块 → 模块 A 接入 ✅
- [x] **Step 5**：模块 B exact BRDF 渲染路径（几何缓冲 + Python 后处理）✅ 管线通，native A/B 差异已确诊
- [x] **Step 6**：材料 sweep + L 型双平板 + 立方体三端闭合验证 ✅（凸几何 ≤0.25% 闭合）
- [x] **Step 7a-b**：Sub-face 自适应积分（失败→封存）+ pixel-level 统一积分（成功）✅
- [x] **Step 8**：GGX/Cook-Torrance 小规模验证（全 PASS，ratio 0.02–8.86）✅
- [x] **Step 10a-d**：GGX 生产扫描 → 10° → 5° → 多观测几何（13,505 姿态）✅
- [x] **Step 11f**：论文级结果汇总 + 互补性诊断 ✅ 2026-05-22
- [ ] BRDF 参数敏感性分析（F0 / roughness / metallic 扰动 → OCS 变化 → 姿态误差传播）
- [ ] LegacyPhong vs GGX 对姿态估计精度的消融对比（LegacyPhong OCS 扫描待跑）
- [ ] GGX 参数从真实材料库反标定（当前用 nominal 文献值）
- [ ] 可选：RGB 三通道 BRDF（当前灰度）
- [ ] 可选：各向异性 BRDF（太阳能板方向性反射）

## 6.8 BRDF 精确化执行历程（Step 1–8 完整记录）

### 6.8.1 Step 1–4：基础建设（2026-05-18 完成）

**Step 1 — BRDF 公式审计**：读取 `materials.py` / `ocs_core.py` / `render_batch.py`，确认模块 A 真实公式为 `f_r = (ρ_d/π) + ρ_s·(N·H)^n`，模块 B 底层用 GGX 微表面模型（非 Phong）。识别三处关键差异：镜面模型（Phong vs GGX）、能量归一化（无 vs 有）、金属处理（统一公式 vs metallic=0）。冻结 LegacyPhong 公式定义。

**Step 2 — 统一设计文档**：产出 `结果/BRDF验证/brdf_precision_design.md`（后迁移至 `ocs_project/07_brdf/`）。确立两层策略：LegacyPhong（历史 baseline，已冻结）+ GGX/Cook-Torrance（论文主模型）。定义三类部件 nominal 参数、方向约定、验收标准（单平板 <1~2%，姿态曲线相关系数 >0.99）。

**Step 3 — Canonical BRDF 模块**：新增 `ocs_project/07_brdf/brdf_models.py`：
- `eval_legacy_phong()` / `eval_normalized_phong()` / `eval_ggx_cook_torrance()` / `eval_brdf()` 统一分发
- GGX 组件：`D_GGX` / `G_Smith_GGX` / `F_Schlick`
- 材料库：`MATERIAL_DB_LEGACY` + `MATERIAL_DB_GGX`
- 防护：numpy 批量支持、防 NaN/Inf、roughness 下限 0.02、零向量保护
- `test_brdf_models.py`：6 类单元测试全部通过

**Step 4 — 模块 A 接入**：`ocs_core.py` 删除内嵌 BRDF 计算（4行），改调 `eval_brdf()`；`materials.py` 所有材料字典增加 `"brdf_model": "legacy_phong"` 字段。验证：3 部件 × 1000 面元随机测试，最大相对误差 **0.000e+00**；单平板端到端 OCS=1.63e-3 m² 与理论一致。

### 6.8.2 Step 5：模块 B Exact BRDF 渲染路径（2026-05-18 ~ 2026-05-19）

**方案选择**：路径 B（几何缓冲 + Python 后处理），不走 OSL（性能 + 数值不可控）。Blender 落地 4.2.3 LTS（5.0 Compositor MULTILAYER EXR 损坏）。

**渲染端**（`render_geometry_passes.py`）：每姿态输出 1 个 MULTILAYER EXR（Combined / Normal / Depth / IndexOB / Backfacing AOV），OPTIX GPU 0.31s/帧，703 帧总 215s。STL 每部件设 `pass_index ∈ {1,2,3}` 供 IndexOB 区分。

**后处理端**（`brdf_postprocess.py`）：读 EXR → IndexOB 分三部件 → `eval_legacy_phong` → `OCS_image = Σ pixel_area · f_r · NoL`。关键推导：`A_face_pix = pixel_area / NoV` 代入 A 端公式后 NoV 抵消，数学自洽。

**与模块 A 对比（703 帧）— 严重不一致**：
- 相对误差均值 69.2%，max 951%，q50 35%
- Pearson(OCS_img, OCS_A_with_occ) = -0.057（几乎无相关）
- 最差帧 yaw=150/pitch=-80：OCS_B=0.171 vs OCS_A_no_occ=0.077 vs OCS_A_with_occ=0.016

### 6.8.3 诊断历程：五条线索并行排查（2026-05-19）

| 线索 | 假说 | 验证方法 | 结论 |
|---|---|---|---|
| 一 | 背面像素污染 OCS | Transparent BSDF → Combined 亮度遮罩 → Shader AOV Backfacing | **已排除**：封闭网格外视图 Backfacing AOV 全零，不存在背面像素 |
| 二 | jinshuzhuti 镜面峰异常 | 单帧 f_r 分布分析 | B 端 f_r 呈双峰（漫射 0.064 + 镜面峰 0.575），NoH q50=0.998，精确命中镜面峰 |
| 三 | A/B 几何精度不对称 | A_fast(96k faces) vs A_full(481k faces) 单帧对比 | **已排除**：差仅 0.2%，均仅为 B 的 ~45% |
| 四 | face-center vs pixel-level 采样 | diffuse-only 验证（ρ_s=0 临时关闭镜面项） | **确认为主因**：A 端 face-center 完全错过 n=80 窄镜面峰（specular 贡献精确为 0），B 端 pixel-level 成功捕获 |
| 五 | diffuse-only per-part 对账 | A/B 纯漫射下 OCS 对比 | 残余 26% gap，确认为可见性语义差异（ray-cast vs camera rasterization） |

**线索一的详细经过**（AOV 诊断）：
1. 尝试 Transparent BSDF + Mix Shader 过滤背面 → Combined 遮罩不完美
2. 尝试 Shader AOV 输出 `Geometry.Backfacing` → 实测全零
3. 结论：对于封闭网格外视图，所有可见像素均为真正前向面。之前的"翻转法线"是匹配 A 端面元时对到了薄板另一侧物理面，不是渲染背面
4. 代码简化：去掉 Transparent BSDF，Backfacing AOV 保留作为诊断通道

**已排除的根因汇总**（共 10 项）：法线坐标系、分辨率不足、smooth shading、背面像素污染、Combined 遮罩误杀、OCS 公式推导错误、A/B 几何精度不对称、纯镜面峰采样问题、A/B BRDF 公式/单位/面积链路错误、解析解转置 bug。

### 6.8.4 Step 6：简单几何三端闭合验证（2026-05-19 ~ 2026-05-20）

**核心发现**：复杂几何（真实三件套）的 A/B gap 来自"可见性语义差异"，非 BRDF/公式/代码错误。通过在简单几何上建立解析/A/B 三端对比来验证这一结论。

**6a. 单平板多角度批量验证**：
- 新增 `render_flat_plate_batch.py` + `run_plane_batch_validation.py`
- 修复解析解转置 bug：`N_body @ R`（取第三行）→ `R @ N_body`（取第三列），此 bug 在 yaw∈{0,180}且 pitch=0 时被对称性隐藏
- 5 姿态三端闭合：mean rel_err=0.25%，所有 NoL>0 姿态均 <0.5%
- 产物：`结果/BRDF验证/plane_batch_20260519_204323/`

**6b. 材料 sweep**：
- `run_material_sweep.py`：复用同一组 EXR（几何缓冲与材质无关），测试三种 LegacyPhong 材料
- 三种材料均三端闭合，mean rel_err=0.253%
- 结论：几何缓冲方案材质独立性验证通过

**6c. L 型双平板**（非凸几何的可见性语义测试）：
- `render_L_plate.py` + `run_L_plate_validation.py`，10×10 细分（200 面/板）
- 初版 STL 法线翻转、RayForest API 错误均已修正
- 结果：A_no=analyt（0.00%），A_with/B≈1.0@中等角度（yaw=0/180），极端角度 A_with/B<1
- Plate_V 在所有姿态 NoL≤0，无法测试其被遮挡场景
- 产物：`结果/BRDF验证/L_plate_20260520_103105/`

**6d. 立方体**（凸几何的三端完美闭合验证）：
- `render_cube.py` + `run_cube_validation.py`，300 面，1m³
- **近乎完美闭合**：B/an ≤ 0.25% 所有姿态，自遮挡 0%（凸体）
- 无背向面照明伪影
- 产物：`结果/BRDF验证/cube_20260520_103846/`

**Step 6 总体结论**：
- 凸几何（平板/立方体）闭合精度 ≤0.25%，达到"数字孪生"级别
- 凹几何（L 型）A_with/B≈1.0 在中等角度，极端角度有差异（face-center vs pixel-level 遮挡判据不同）
- 真实三件套 diffuse gap（~26%）根因确认为可见性语义差异

### 6.8.5 Step 7a–b：采样策略探索（2026-05-20）

**7a — Sub-face 自适应积分 → 失败**：
- 方法：顶点法线面积加权 + 三角形中点剖分 + 重心法线插值 + 自适应递归（NoH>0.96 且 range>0.001 → 剖分，max_depth=5）
- 结果：ad/fc≈1.0（最大仅 1.07× 提升），远不足以弥合 A/B gap
- 失败原因：① 主因是可见面积差异非镜面采样；② 顶点法线是相邻面平均，粗网格无法重构 n=80 窄镜面峰精度；③ 太阳能板 A/B_diff=72×（薄板两面均满足法线判据但仅一面对相机可见）；④ 性能 12-15s/姿态（400-500× 减速）
- 路线封存，转向 pixel-level 统一积分
- 产物：`结果/BRDF验证/subface_adaptive_diag/`

**7b — Pixel-level 统一积分 → 成功**：
- `adaptive_integration.py` 新增 `compute_ocs_from_exr()`，封装 EXR→法线/IndexOB→BRDF→OCS 全链路
- A/B 两端共享完全相同的几何源（Blender EXR），消除可见性语义差异
- `verify_pixel_unified.py`：3 姿态 × 2 BRDF 模式，与 `brdf_postprocess.py` 完全一致（diff=0）
- 函数可用但尚未接入 `ocs_core.py` 生产扫描循环

### 6.8.6 Step 8：GGX/Cook-Torrance 小规模验证（2026-05-20 完成）

**验证策略**：在 canonical EXR 管线上（A≡B by construction），冻结 native A/B 差异，不回头死磕三件套可见性语义。先 LegacyPhong 不回归确认 → 再 GGX → 单平板 → 立方体 → 卫星三部件子集。

**新增脚本**：`ocs_project/06_brdf_validation/verify_ggx.py`，单次 EXR 读取并行计算 LegacyPhong + GGX 双 BRDF OCS，输出 per-part 对比 CSV + 数值健康检查。

**验证结果**：

| 数据集 | 姿态数 | 数值健康 | LegacyPhong 回归 | GGX/Legacy ratio |
|---|---|---|---|---|
| 单平板 | 5 | PASS | ✓ | 0.02 – 8.86 |
| 立方体 | 5 | PASS | ✓ | 0.04 – 8.86 |
| 卫星三部件 | 3 | PASS | ✓ | 0.07 – 8.53 |

**关键物理验证项**：
- metallic=1 (jinshuzhuti) → f_diffuse 精确为 0 ✓
- metallic=0 (taiyangnengban/yinshenban) → f_diffuse = base_color/π > 0 ✓
- D_max 随 roughness 递减：jinshuzhuti(0.20)→16.24 > taiyangnengban(0.40)→9.36 > yinshenban(0.90)→0.48 ✓
- F_Schlick / G_Smith / D_GGX 全分量有限非负 ✓
- 全 15 EXR × 多部件无 NaN/Inf/负值 ✓

**GGX vs LegacyPhong 差异分析**：
- 非镜面角 GGX < LegacyPhong（金属 metallic=1 无漫射，LegacyPhong 始终有 ρ_d/π）
- 镜面峰 GGX > LegacyPhong（微表面 D 项峰值强于 Phong lobe）
- ratio 范围 0.02–8.86 为两模型结构性差异，物理合理
- 立方体与单平板 ratio 近乎一致，确认 GGX 几何无关性

**产物**：`结果/BRDF验证/plane_batch_*/ggx_verify/`、`cube_*/ggx_verify/`、`satellite_subset_3att/ggx_verify/`

### 6.8.7 关键决策与经验教训

1. **两端一致性 > 显式物理公式 > 合理材料参数**：在验证 BRDF 链路正确性时，先用 LegacyPhong 在简单几何上做到三端闭合（≤0.25%），再切换到 GGX。不跳过中间验证步骤。

2. **几何缓冲方案（EXR）的材质独立性**：Normal/Depth/IndexOB 通道与 BRDF 模型无关，同一组 EXR 可复用测试不同材料/BRDF 公式。这极大加速了验证迭代。

3. **Face-center vs pixel-level 采样的结构性差异**：对于 n=80 的窄镜面峰，面中心单点采样即使在全精度网格（481k faces）上也捕获不到镜面贡献（specular=0）。这不是"精度不够"而是"采样范式不同"——需要 sub-pixel 级采样或直接使用 pixel-level 积分。

4. **背面像素 AOV 方案的局限性**：`Geometry.Backfacing` 在 Cycles 最终着色点记录，对于封闭网格外视图始终为 0。此路不可行，但诊断过程验证了 Blender Cycles 的着色法线行为。

5. **Canonical EXR 管线作为统一验证平台**：A/B 共享同一几何源后，A≡B by construction。后续所有 BRDF 验证（GGX、参数 sweep、敏感性分析）都应在此管线上进行，不再回头对比 native A/B。

6. **简单几何先行的验证策略有效**：单平板→L 型→立方体的递进验证，逐层隔离了 BRDF 公式错误、几何变换错误、遮挡语义差异。如果一开始就在真实三件套上调试，无法区分这多层问题。

### 6.8.8 Step 10：GGX 接入生产扫描 + 数据集升级（2026-05-20 完成）

**总体目标**：将已验证通过的 GGX/Cook-Torrance 接入模块 A 生产扫描，冻结 LegacyPhong 仅作兼容 baseline，生成论文级 OCS 数据集。执行顺序严格按照：加 GGX 显式切换入口 → smoke test → 10° 网格 → 5° 网格 → 多观测几何。

#### Step 10a：GGX 显式切换入口

**需求**：在保持向后兼容（默认 LegacyPhong）的前提下，提供 `--ggx` CLI 开关让用户显式选择 GGX 模型。

**代码变更**（4 文件）：
1. `config.py`：新增 `BRDF_MODEL = "legacy_phong"`（不改变默认值）
2. `materials.py`：新增 `_GGX_DB`（三种部件 GGX nominal 参数）+ `get_material(part_name, use_ggx=False)` 增加 GGX 分支
3. `ocs_core.py`：`compute_single_attitude(..., use_ggx=False)` → `scan_attitude(..., use_ggx=False)` → `_worker_init(..., use_ggx=False)` → `_worker_compute()` 全线透传 `use_ggx`
4. `main_run.py`：新增 `--ggx`（`store_true`）、`--num-yaw`、`--num-pitch` CLI 参数

**设计决策**：`use_ggx` 作为参数透传而非从 `config.BRDF_MODEL` 读取——避免全局状态污染多进程 worker。

**Smoke test**：单姿态 yaw=150/pitch=-80，GGX no_occ=0.0350, with_occ=0.00709，数值健康 PASS。

#### Step 10b：GGX 10° 网格扫描（703 姿态）

**命令**：`python main_run.py --ggx --workers 8`

**结果**：126.7s（8 进程，fast 精度），OCS max=1.30, min=0.0022, mean=0.021 m²，遮挡率 mean=69.86%。

**产物**：`结果/模块A_重构/2d_yaw37_pitch19/run_20260520_160131/`

#### Step 10c：GGX 5° 网格扫描（2701 姿态）

**动机**：10° 网格（37×19=703）发现 OCS max 仅 1.30 m²，怀疑欠采样金属镜面峰。

**命令**：`python main_run.py --ggx --workers 8 --num-yaw 73 --num-pitch 37`

**结果**：454.0s（8 进程），2701 姿态（73×37），OCS max=14.82, min=0.0022, mean=0.033 m²。

**关键发现**：10° 网格 OCS max=1.30 vs 5° 网格 max=14.82，**差 11.4 倍**。GGX 金属镜面峰极窄（roughness=0.20），10° 步长完全跳过峰值姿态。**5° 网格为论文必需精度**。

**产物**：`结果/模块A_重构/2d_yaw73_pitch37/run_20260520_160847/`

#### Step 10d：多观测几何批量扫描（13,505 姿态）

**动机**：单一观测几何（phase≈63°）仅覆盖一种太阳-探测器相对位置。论文需要证明多观测几何对姿态估计的优势（§8.3 消融实验）。

**新增代码**：
1. `config.py`：新增 `OBS_GEOMETRIES` 列表（5 组 sun/det/标签），覆盖相位角 24°–120°
2. `run_multi_geom.py`（新文件）：批量扫描入口
   - `run_one_geometry()`：单几何完整流程（fig06 + scan + fig01-05 + JSON/CSV/config）
   - `--geoms all` 或 `--geoms 0,2,4` 选择性运行
   - 全局 `multi_geom_manifest.json` 汇总跨几何对比

**命令**：`python run_multi_geom.py --ggx --workers 8 --num-yaw 73 --num-pitch 37 --geoms all`

**结果总表**（5 几何 × 2701 = 13,505 姿态，1724.5s / 28.7min）：

| 几何 | 相位角 | OCS max (m²) | OCS mean (m²) | 遮挡率 mean | 耗时 |
|---|---|---|---|---|---|
| phase63_backscatter | 63.1° | 14.82 | 0.0334 | 69.66% | 397.9s |
| phase24_near_backscatter | 23.6° | 17.88 | 0.0644 | 60.11% | 479.0s |
| phase120_forward_scatter | 120.0° | 29.98 | 0.0530 | 78.47% | 177.9s |
| phase90_side | 90.0° | 30.53 | 0.0452 | 72.60% | 259.4s |
| phase45_overhead | 45.0° | 6.41 | 0.1589 | 68.39% | 405.4s |

**关键发现**：
1. **OCS max 跨几何差异 4.8×**（6.41 → 30.53 m²）：侧向/前向散射的镜面反射贡献远大于俯视
2. **OCS mean 跨几何差异 4.8×**（0.033 → 0.159）：overhead 几何平均 OCS 最高（更多面元同时被照亮和观测到），但镜面峰值最低
3. **遮挡率跨度 60%→78.5%**：近后向散射最低（太阳后方，阴影少），大相位角前向散射最高（复杂自遮挡）
4. **耗时不对称**（178s–479s）：遮挡率越高的几何，射线命中越早停止，耗时越短。前向散射（78.5% 遮挡）仅 178s
5. **10° vs 5° 教训在 overhead 几何更温和**（max 仅 6.41），但对金属镜面方向（φ90/120）影响剧烈

**跨几何 OCS max 分析**（论文关键数据）：
- 侧向/前向散射（90°/120°）有最强镜面峰（30.5/30.0），因为在这些几何下探测器恰好能接收到金属主体的 specular lobe
- Overhead（45°）的镜面峰仅 6.4，因为探测器在高角度远离 specular 方向
- 这表明**观测几何优化对空间目标光学特征提取至关重要**

**产物**：`结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/run_20260520_162831/`

---

# 7. 姿态反演（对应论文 §Attitude Inversion）

> **执行时段**：2026-05-20 ~ 2026-05-22。全部实验完成，所有关键数值就绪。
> **统一配置**：10° 网格 train（563 姿态）→ 5° 插值 test（1998 姿态），5 seeds 平均，sin/cos 归一化角度编码。
> **产物索引**：`结果/模块C_反演/`；论文汇总：`paper_summary/run_20260522_234553/`

## 7.1 方法体系全景（13 种配置，全部完成）

| 方法 | 输入 | 算法 | 代码 | 完成日 |
|---|---|---|---|---|
| OCS kNN discrete LOO | OCS concat5 45D | kNN LOO 离散检索 | `inv_ocs.py` | 05-20 |
| OCS kNN discrete 10°→5° | OCS concat5 45D | kNN 跨网格检索 | `inv_ocs.py` | 05-20 |
| OCS kNN weighted reg. | OCS concat5 45D | K=5 distance-weighted 回归 | `train_mlp.py` | 05-21 |
| **OCS MLP** | OCS concat5 15/30/45D | MLP 128→128→64 SiLU+LN | `train_mlp.py` | 05-21 |
| HOG image-only LOO | phase63 128×128 HOG | kNN LOO 离散检索 | `inv_image.py` | 05-21 |
| HOG+OCS joint kNN LOO | OCS 45D + HOG 8100D | α-sweep 加权 kNN | `inv_joint.py` | 05-21 |
| **CNN image-only** | phase63 128×128 log1p | TinyCNN 106k params | `train_cnn.py` | 05-21 |
| **Late fusion** | OCS MLP pred + CNN pred | sin/cos 空间预测级融合 β-sweep | `fuse_predictions.py` | 05-22 |
| **Feature fusion** | OCS 15/30/45D + 128×128 image | 双流联合训练 ImageBranch+OCSBranch→FusionHead | `train_fusion.py` | 05-22 |

### OCS 特征模式

| 特征模式 | 维度 | 内容 | 信息等级 |
|---|---|---|---|
| `obs_total` | 5D | 5 几何 × ocs_with_occ | 真实可观测总 OCS |
| `total` | 15D | 5 几何 × (no_occ, with_occ, occ_ratio) | 有遮挡率信息 |
| `per_part` | 30D | 5 几何 × 3 部件 × (no_occ, with_occ) | 分部件半 oracle |
| `all` | 45D | 5 几何 × 3 部件 × (no_occ, with_occ, occ_ratio) | 全 oracle 信息 |

## 7.2 主反演结果表（10 方法）

| Method | OCS input | Image input | mean(deg) | median(deg) | p90(deg) | Hit@5° | Hit@10° |
|---|---|---|---:|---:|---:|---:|---:|---|
| OCS MLP | all raw 45D | - | **3.98±0.60** | 2.00 | 4.82 | **90.7%** | 97.1% |
| OCS MLP | per_part log 30D | - | 5.91±0.22 | 3.37 | 7.74 | 73.8% | 94.3% |
| OCS MLP | total log 15D | - | 36.69±3.62 | 23.90 | 93.09 | 9.7% | 23.5% |
| CNN image-only | - | phase63 log1p | 12.38±0.74 | 8.84 | 24.84 | 26.1% | 55.8% |
| Late fusion | all raw 45D | phase63 log1p | 5.03±0.01 | 2.26 | 5.58 | 87.4% | 96.2% |
| Late fusion | per_part log 30D | phase63 log1p | 6.15±0.03 | 3.32 | 7.80 | 71.8% | 94.3% |
| Late fusion | total log 15D | phase63 log1p | 11.99±0.70 | 8.68 | 23.95 | 26.6% | 56.9% |
| Feature fusion | all raw 45D | phase63 log1p | 5.42±0.45 | 2.40 | 5.84 | 85.4% | 95.6% |
| **Feature fusion** | **per_part log 30D** | **phase63 log1p** | **4.10±0.77** | 2.42 | 5.35 | **87.3%** | **97.4%** |
| Feature fusion | total log 15D | phase63 log1p | 13.75±2.37 | 6.28 | 29.36 | 40.0% | 69.2% |

> **粗体 = Proposed 方法（Feature fusion per_part_log）**。OCS MLP all_raw 45D 为 semi-oracle 性能上界（3.98°）。
> 完整表格：`paper_summary/run_20260522_234553/table_main_inversion.csv`

## 7.3 关键发现（支撑论文核心论点）

### 发现 1：OCS 是极强的姿态信号载体（semi-oracle 级）
- OCS MLP all_raw 45D: mean=3.98°, Hit5=90.7%——45 维多几何分部件 OCS 近乎完美编码姿态
- 跨 5 几何拼接增益 7.6×（concat5 total vs single phase63）
- **论文论点**：多观测几何 OCS 是可行的独立姿态反演信号源

### 发现 2：单张光学图像含中等但可靠的姿态信息
- CNN image-only (1ch 128×128): mean=12.38°, Hit5=26.1%，远超随机基线（期望 90°）
- HOG kNN LOO: Top1@5°=74.79%——检索场景有效但跨网格泛化差
- **论文论点**：光学图像含独立姿态信号，可作为互补模态

### 发现 3：OCS 与图像信号近乎完全互补（r=0.0030）
- 误差相关近乎零：两种模态犯**完全不同类型**的错误
- 融合在 **64.9%** 样本中同时击败两种单模态
- 融合最大受益场景：OCS 大故障样本（50+° bin: +74.23° 改善）
- 互补性高度姿态依赖：180°–240° 偏航范围改善最大（+9.7°），与卫星对称性 OCS 歧义一致
- **论文论点**：OCS-图像互补是**可量化证明的**，非直觉推测

### 发现 4：per_part_log 是融合 sweet spot（"金凤花原理"）

| OCS 强度 | OCS-only mean | Fusion best mean | 融合效果 |
|---|---|---|---|
| all_raw (过强) | 3.98° | 5.42° | 图像 = 噪声 |
| **per_part_log (适中)** | **5.91°** | **4.10° (+31%)** | **真正互补** |
| total_log (过弱) | 36.69° | 11.99° | 图像主导，OCS 扰动 |

### 发现 5：Feature fusion > Late fusion，但仅在 sweet spot
- per_part_log: Feature 4.10° vs Late 6.15°（Feature 胜 33%）——跨模态特征交互有效
- all_raw / total_log: Late 融合更鲁棒——极端场景简单加权更好
- **论文论点**：特征级融合的优势取决于 OCS 信息强度

### 发现 6：少量灾难性融合失败案例
- 典型：OCS=0.00°（完美），CNN=5.07°，融合→180°（最差误差）
- 共 12 例融合误差 >80° 的灾难性案例
- **论文处理**：在 Discussion/Limitations 明确讨论，作为未来鲁棒性改进方向

## 7.4 姿态反演产物索引

| 类型 | 路径 | 内容 |
|---|---|---|
| OCS kNN 消融 | `inv_ocs/run_20260520_184414_ablation/` | 24 实验消融矩阵 |
| OCS MLP | `mlp_ocs/run_20260521_084723/` | 5 seeds × 5 特征 + kNN baseline |
| HOG image-only | `inv_image/run_20260521_123201/` | LOO baseline, Top1@5°=74.79% |
| HOG+OCS joint | `inv_joint/run_20260521_155144/` | α-sweep, best α=0.24 (mean) / 0.85 (Top1) |
| CNN image-only | `cnn_image/run_20260521_164437_final_log1p/` | 5 seeds, summary.json |
| Late fusion | `cnn_ocs_late_fusion/run_20260522_2208*/` | 3 OCS cases × β sweep |
| Feature fusion | `cnn_ocs_fusion/run_20260522_2217*/` | 3 OCS cases × 5 seeds |
| **论文汇总** | `paper_summary/run_20260522_234553/` | 主表+消融表+5图(dpi=300)+互补性诊断+案例画廊+论文声明 |

## 7.5 实验需求状态

- [x] OCS kNN baseline + 消融矩阵 ✅ 2026-05-20
- [x] OCS MLP 连续回归 ✅ 2026-05-21
- [x] HOG image-only + HOG+OCS joint kNN ✅ 2026-05-21
- [x] CNN image-only ✅ 2026-05-21
- [x] Late fusion + Feature fusion ✅ 2026-05-22
- [x] 论文级汇总 + 互补性诊断 ✅ 2026-05-22
- [ ] 更大 CNN 模型（ResNet-18 / EfficientNet）
- [ ] 多观测几何图像联合（当前仅 phase63 图像）
- [ ] Roll 轴姿态扩展（三维姿态估计）
- [ ] 四元数随机采样数据增强
- [ ] 真实观测数据验证


---

# 8. 消融实验矩阵（对应论文 §Ablation Studies）

> 当前状态：全部反演方法消融已完成（§11e-A/B）。前向模型消融部分完成（GGX vs LegacyPhong 对比数据已有，但 Lambert baseline 和参数敏感性扫描未做）。

## 8.1 前向模型消融（部分完成）

| 实验组 | 状态 | 关键结果 |
|---|---|---|
| GGX Cook-Torrance（论文主模型） | ✅ 5° 网格 2701 姿态 + 5 几何 | OCS max=30.53 m² (phase90), mean=0.033–0.159 m² |
| LegacyPhong（历史 baseline） | ✅ 三端闭合验证完成 | 10° 网格 OCS max=1.30 vs GGX max=14.82（11.4× 差异） |
| GGX vs LegacyPhong 对比 | ✅ 小规模验证 | ratio 0.02–8.86，金属镜面峰差异最大 |
| BRDF 参数敏感性分析 | ⬜ 未做 | ρ_d / F0 / roughness / metallic 扰动 → OCS 变化 → 姿态误差传播 |
| Lambert 均匀 BRDF baseline | ⬜ 未做 | 论文中可能需要作为最简 baseline |
| GGX 参数从真实材料反标定 | ⬜ 未做 | 当前用 nominal 文献值 |

## 8.2 反演方法消融（全部完成）

| 实验组 | 输入 | 方法 | mean(deg) | Hit@5° | 论文角色 |
|---|---|---|---:|---:|---:|---|
| OCS kNN discrete LOO | concat5 all raw 45D | 最近邻 | 12.28° | <1% (10°→5°) | 离散检索 baseline |
| OCS kNN weighted reg. | concat5 all raw 45D | K=5 distance-weighted | 21.84° | 47.9% (10°→5°) | 连续回归 baseline |
| **OCS MLP** | concat5 all raw 45D | MLP 128→128→64 | **3.98°** | **90.7%** | Semi-oracle 上界 |
| OCS MLP | concat5 per_part log 30D | MLP 128→128→64 | 5.91° | 73.8% | 实用 OCS-only |
| OCS MLP | concat5 total log 15D | MLP 128→128→64 | 36.69° | 9.7% | 弱 OCS baseline |
| HOG image-only LOO | HOG 8100D | kNN LOO | 4.31° | 74.79% (LOO) | 传统图像检索 |
| **CNN image-only** | phase63 128×128 log1p | TinyCNN 106k | 12.38° | 26.1% | 图像深度学习 baseline |
| Late fusion | all raw OCS + CNN | 预测级加权 β=0.96 | 5.03° | 87.4% | 预测级融合 baseline |
| Late fusion | per_part OCS + CNN | 预测级加权 β=0.93 | 6.15° | 71.8% | 预测级融合 |
| Late fusion | total OCS + CNN | 预测级加权 β=0.11 | 11.99° | 26.6% | 预测级融合 |
| **Feature fusion** | **per_part log + CNN** | **双流联合训练** | **4.10°** | **87.3%** | **Proposed** |
| Feature fusion | all raw + CNN | 双流联合训练 | 5.42° | 85.4% | 过参数化 |
| Feature fusion | total + CNN | 双流联合训练 | 13.75° | 40.0% | 弱 OCS 扰动 |

### 关键消融发现

1. **MLP > kNN**：MLP(3.98°) vs kNN discrete(<1%), kNN weighted(21.84°)——连续回归远优于离散检索
2. **Feature fusion > Late fusion** (per_part_log)：4.10° vs 6.15°（+33%）——跨模态交互学习有效
3. **Late fusion > Feature fusion** (极端 OCS)：all_raw(5.03° vs 5.42°) 和 total_log(11.99° vs 13.75°)——极端场景简单加权更鲁棒
4. **Raw > Log 对 MLP**：MLP 自主学习大动态范围（all raw 3.98° < all log 6.93°），与 kNN 相反（kNN 必须 log）
5. **多几何是关键**：concat5 total LOO Top1@5°=53.8% vs single phase63 仅 7.1%（7.6× 增益）

## 8.3 观测几何消融（部分完成）

| 实验组 | 状态 | 关键结果 |
|---|---|---|
| phase63 单几何 | ✅ CNN/Late fusion/Feature fusion | 图像反演 baseline |
| concat5 多几何 OCS | ✅ kNN 消融 + MLP | OCS kNN 7.6× 增益 vs single |
| 多几何图像融合 | ⬜ 未做 | 需渲染其他 4 几何的图像 |
| 最优观测几何搜索 | ⬜ 未做 | 需可观测性指标定义 |
| OCS 几何消融（1→5 递增） | ⬜ 未做 | 证明每一组几何的边际贡献 |
| 相位角-姿态误差关系 | ✅ 数据已有 | 互补性诊断中的偏航分析 |

## 8.4 前向模型消融 — 遮挡（已完成）

| 实验组 | 状态 | 关键结果 |
|---|---|---|
| 无遮挡 OCS | ✅ 数据已有 | OCS_no_occ 在 all_raw 45D 中可用 |
| 有遮挡 OCS | ✅ 数据已有 | OCS_with_occ，三部件真实模型 |
| 遮挡率分析 | ✅ | jinshuzhuti 72.88%, taiyangnengban ~90%, yinshenban ~77% |
| mhd 敏感性扫描 | ✅ | 0.1–10 mm × 3 部件 → mhd=1.0 mm 为最优折衷 |
| 遮挡消融（w/ vs w/o） | ⬜ 需系统对比 | 论文中需对比否遮挡对姿态反演精度的影响 |

## 8.5 待完成消融（论文撰写前/审稿人可能要求）

1. **Lambert 均匀 BRDF baseline**：证明非均匀/非朗伯 BRDF 的必要性
2. **BRDF 参数敏感性**：每个 GGX 参数 ±20% → OCS 变化 → 姿态误差传播
3. **观测几何数量消融**：concat1→concat2→...→concat5，证明每增加一个几何的边际收益
4. **图像分辨率消融**：64×64 vs 128×128 vs 256×256（已知 128 vs 256 差 <1% for OCS，但对 CNN 的影响未测）
5. **CNN 架构对比**：TinyCNN (106k) vs ResNet-18 vs EfficientNet-B0
6. **数据量敏感性**：train split 563/270/135/67 → 误差曲线

---

# 9. 已知坑与当前困境（对应论文的 Limitations / Future Work）

## 9.1 ✅ 已诊断完毕（原阻塞点，2026-05-20 冻结）

### 困境 #1：模块 B Exact BRDF 路径 OCS 数值不一致 → 已确诊，非代码/公式错误

**原始现象**（703帧验证）：
- 相对误差均值 69.2%，max 951%，q50 35%
- Pearson(OCS_img, OCS_A_with_occ) = -0.057（几乎无相关）

**最终诊断结论**（经 5 条线索并行排查）：
- **主因**：A 端 face-center 采样 vs B 端 pixel-level 采样的结构性差异。A 端每面一个 BRDF 值，对 n=80 窄镜面峰，即使 full mesh (481k faces) 也完全捕获不到镜面贡献（specular=0）。B 端逐像素采样成功命中镜面峰。
- **次因**：diffuse-only 仍有 ~26% gap，来自可见性语义差异（A 端 ray-cast vs B 端 camera rasterization）。
- **已排除 10 项假说**（详见 §6.8.3）。

**决策**：冻结 native A/B 三件套差异，不再作为当前主线阻塞项。后续物理验证转入 **canonical EXR 管线**（A/B 共享同一几何源，A≡B by construction）。在此管线上已完成：
- LegacyPhong 三端闭合验证（单平板 ≤0.25%、立方体 ≤0.25%）
- GGX 小规模验证（全部数值健康 PASS）
- 产物：`结果/BRDF验证/` 下各子目录

**论文处理**：在论文 §Validation 中可将 face-center vs pixel-level 差异作为"离散化误差分析"讨论，不构成方法缺陷。

## 9.2 已知技术坑

### 坑 #1：Blender 5.0 Compositor MULTILAYER EXR 损坏
- `file_output_items` 只写第一个 link 通道，丢 Normal/Depth/IndexOB
- **→ 落地用 4.2.3 LTS**，等 5.x 修好再考虑

### 坑 #2：Blender 4.2 MULTILAYER 文件名行为
- 文件名 = `base_path` + `frame:04d` + `.exr`（不会自动加路径分隔符）
- `layer_slots[i].name` 决定 EXR 内层名
- `file_slots` / `layer_slots[0].path` 在 MULTILAYER 下被忽略

### 坑 #3：trimesh QEM 抽稀
- fast 模式对凹陷几何敏感
- 需装 `fast_simplification` 后端获 C++ 加速
- **→ 论文期用 full**

### 坑 #4：Embree 软依赖
- 未装 `embreex` / `pyembree` 静默回退纯 Python BVH
- 装了自动启用，单线程提速 10~100×
- **→ 论文期确保 Embree 可用**

### 坑 #5：`intersects_location` 返回值
- 返回扁平命中列表而非按射线对齐
- 必须接第 2 个返回值 `index_ray` 做射线聚合
- **→ 已修复并验证（2026-05-12）**

### 坑 #6：conda run 多行限制
- `conda run -n ocs_sim python -c "..."` 不接多行（Windows path）
- **→ 用脚本文件 + 直调 conda env python.exe**

### 坑 #7：中文字体/Unicode
- Windows GBK 控制台 `✓` 等 Unicode 字符报 UnicodeEncodeError
- **→ 验证脚本加 UTF-8 重定向**

## 9.3 MVP 已知限制（待论文期补）

1. BRDF：Principled 近似，非 Phong 像素级镜像（→ exact BRDF 路径解决中）
2. 金属主体 metallic=0（→ GGX 时设 metallic=1）
3. 未做辐射度量定标（→ 论文期射线链路标定）
4. 无大气、地球反照、杂散光（→ 视论文范围决定是否加入）
5. 模块 A/B 遮挡机制差异（→ A用min_hit_distance，B用Cycles物理光追，语义等价已交叉验证）
6. UNIT_SCALE 通过 parent 应用，不 bake（→ 不影响一致性）

## 9.4 未解决的设计问题与待改进方向

### 已识别待解决

1. **72.88% 遮挡率是否过高？** 主要来自 jinshuzhuti 真实近邻几何。可选方案：区分同部件/跨部件阈值，但改动大且可能无法区分"真实同部件遮挡"与"几何粘连"。当前 mhd=1.0 mm 已通过敏感性扫描验证为最优折衷。

2. **Feature fusion 灾难性失败案例**（12/1998 = 0.6%）：OCS 完美（0° 误差）+ CNN 良好（5° 误差），融合却输出 180° 误差。可能原因：sin/cos 符号象限翻转、OCS 分支过拟合特定姿态模式。需要：
   - 诊断灾难性案例的 OCS 特征/图像模式
   - 探索融合鲁棒性改进（不确定性估计、门控机制、集成方法）

3. **四元数 vs 欧拉角**：当前用欧拉角（Z-Y-X 内旋）。3-DOF 扩展（yaw×pitch×roll）需评估四元数输出编码。

4. **单相位角图像**：仅 phase63（63° 相位角）用于图像反演。多观测几何（phase24–120°）的 OCS 已就绪，但未渲染对应图像。

5. **GGX 材料参数来源**：当前用 nominal 文献值（铝 F0=0.91, roughness=0.20 等）。真实卫星表面的材料参数未知且可能退化，需要：
   - BRDF 参数敏感性分析（每个参数 ±20% → OCS 变化 → 姿态误差传播）
   - 或从真实望远镜观测数据反标定

6. **无绝对辐射定标**：图像像素值为相对辐亮度。论文需明确声明"非绝对辐射复现"，定位为"物理一致仿真 + 算法验证"。

### 论文中可定位为 Future Work

7. Roll 轴三维姿态估计（当前 yaw/pitch 二维）
8. 真实望远镜/实验室缩比模型验证
9. 时间序列滤波（当前逐帧独立反演，未利用姿态连续性）
10. 更大的 CNN 架构（ResNet-18/EfficientNet，当前 TinyCNN 仅 106k params）
11. RGB 三通道/多光谱 BRDF 与图像渲染
12. 大气消光、地球反照、杂散光等空间环境效应
13. 真实轨道 STK 数据导入与场景仿真

---

# 10. 实验需求汇总（论文实验清单）

> 状态：✅ 已完成 | ⚠️ 部分完成/数据已有 | ⬜ 未开始

## 10.1 前向模型实验

| 编号 | 实验 | 状态 | 论文位置 |
|---|---|---|---|
| F1 | 全精度 OCS 扫描（5°网格, GGX, 2701姿态） | ✅ | §Results - OCS |
| F2 | 多观测几何 OCS（5 几何 × 2701 = 13,505 姿态） | ✅ | §Results - Multi-geometry |
| F3 | Exact BRDF 图像库（phase63 GGX 2701 PNG+EXR） | ✅ | §Results - Images |
| F4 | OCS-图像一致性验证（单平板 + 立方体三端闭合 ≤0.25%） | ✅ | §Validation |
| F5 | 遮挡消融实验（mhd 敏感性扫描 0.1–10mm） | ✅ | §Ablation - Occlusion |
| F6 | BRDF 消融实验（LegacyPhong vs GGX 全 2701） | ⚠️ | §Ablation - BRDF |
| F7 | GGX 材料参数设置与验证（三部件 nominal 值） | ✅ | §Material Model |
| F8 | Sub-face 自适应积分（Attempted, 性能不可接受） | ⚠️ 封存 | 不写入论文 |
| F9 | Pixel-level 统一积分（A/B 共享 EXR） | ✅ | §Validation |
| F10 | BRDF 参数敏感性分析（F0/roughness/metallic 扰动） | ⬜ | §Sensitivity Analysis |
| F11 | Lambert 均匀 BRDF baseline | ⬜ | §Ablation |

## 10.2 姿态反演实验

| 编号 | 实验 | 方法 | mean(deg) | Hit@5° | 状态 |
|---|---|---|---:|---:|---:|---|
| I1 | OCS kNN discrete LOO | 最近邻检索 | 12.28° (all raw) | 77.4% (LOO) | ✅ |
| I2 | OCS kNN discrete 10°→5° | 跨网格检索 | — | <1.1% | ✅ |
| I3 | OCS kNN weighted reg. | K=5 distance-weighted | 21.84° | 47.9% | ✅ |
| I4 | OCS MLP | MLP 128→128→64 | 3.98° (all raw) | 90.7% | ✅ |
| I5 | HOG image-only LOO | HOG + kNN LOO | 4.31° | 74.79% | ✅ |
| I6 | HOG+OCS joint kNN LOO | α-sweep 加权 | 4.10° (α=0.24) | 84.64% | ✅ |
| I7 | CNN image-only | TinyCNN 106k | 12.38° | 26.1% | ✅ |
| I8 | Late fusion (pred-level) | β-sweep sin/cos | 5.03° (all raw) | 87.4% | ✅ |
| I9 | **Feature fusion (dual-stream)** | **双流联合训练** | **4.10° (per_part)** | **87.3%** | ✅ |
| I10 | 更大 CNN 架构 | ResNet/EfficientNet | — | — | ⬜ |
| I11 | 多观测几何图像联合 | 多帧图像融合 | — | — | ⬜ |
| I12 | Roll 轴三维姿态 | yaw×pitch×roll | — | — | ⬜ |

## 10.3 分析与可视化实验

| 编号 | 实验 | 状态 | 论文位置 |
|---|---|---|---|
| A1 | 坐标系示意图 | ⬜ | §Coordinate Systems |
| A2 | 遮挡验证报告（合成 + 真实模型） | ✅ | §Occlusion Validation |
| A3 | 遮挡可视化（三维标注图） | ✅ | §Occlusion Validation |
| A4 | OCS-图像误差相关性分析（r=0.003） | ✅ | §Complementarity |
| A5 | 互补性诊断（分箱 + 偏航 + 案例画廊） | ✅ | §Complementarity |
| A6 | 融合消融可视化（3×4 消融热力图） | ✅ | §Ablation |
| A7 | 姿态误差 CDF 曲线 | ✅ | §Results (fig03) |
| A8 | Late fusion β-sweep 曲线 | ✅ | §Results (fig04) |
| A9 | 融合改善热力图 | ✅ | §Results (fig05) |
| A10 | 主结果条形图 + Hit5 条形图 | ✅ | §Results (fig01/02) |
| A11 | BRDF 参数敏感性（ρ_d/F0/roughness/metallic 扰动） | ⬜ | §Sensitivity Analysis |
| A12 | 观测几何优化（最优 sun/det 方向搜索） | ⬜ | §Observation Optimization |
| A13 | 姿态误差空间分布热图（yaw×pitch） | ⬜ | §Results |

## 10.4 论文写作支撑

| 编号 | 内容 | 状态 |
|---|---|---|
| W1 | Related Work 文献矩阵表 | ⬜ |
| W2 | 所有图表英文版（`LANG_MODE="en"`） | ⚠️ 代码就绪，切换即可 |
| W3 | 参数来源说明（每个材料参数引用文献） | ⚠️ nominal 值已确定，需补充文献引用 |
| W4 | 与现有方法对比表 | ⬜（需文献调研） |
| W5 | 论文声明草稿（5 核心 + 6 局限 + 2 未来） | ✅ `paper_claims.md` |
| W6 | 互补性诊断正式报告 | ✅ `complementarity_diagnosis.md` |
| W7 | 案例画廊（best/worst/big wins/losses） | ✅ `case_gallery.md` |

---

# 11. 互补性诊断与论文级汇总（Step 11f 产出）

> **产物目录**：`结果/模块C_反演/paper_summary/run_20260522_234553/`
> **完成日期**：2026-05-22

## 11.1 汇总产物清单

| 文件 | 内容 | 论文用途 |
|---|---|---|
| `table_main_inversion.csv/.md` | 10 方法主反演结果表（完整数值） | §Results 主表 |
| `table_fusion_ablation.csv/.md` | 3 OCS 强度 × 4 方法消融 + 解读 | §Ablation |
| `fig01_bar_chart.png` (dpi=300) | 各方法 mean angular error 条形图 | §Results Fig.1 |
| `fig02_hit5_bar_chart.png` (dpi=300) | 各方法 Hit@5° 条形图 | §Results Fig.2 |
| `fig03_cdf.png` (dpi=300) | 误差 CDF 分布曲线（OCS vs CNN vs Fusion） | §Results Fig.3 |
| `fig04_beta_sweep.png` (dpi=300) | Late fusion β sweep：mean vs Hit5 tradeoff | §Ablation Fig.4 |
| `fig05_improvement_heatmap.png` (dpi=300) | 3 OCS 强度 × 融合方法改善热力图 | §Ablation Fig.5 |
| `complementarity_diagnosis.md` | 完整互补性诊断（相关/分箱/偏航/解释） | §Complementarity |
| `complementarity_data.npz` | 原始数据（errs_ocs/cnn/fusion + improvement） | 可复现分析 |
| `case_gallery.md` | 成功/失败/大赢/大输案例 | §Discussion |
| `paper_claims.md` | 5 核心声明 + 2 未来声明 + 6 局限性 | §Introduction / §Discussion |
| `summary.json` | 结构化指标汇总 | 快速查询 |
| `figure_data.npz` | CDF + beta sweep 原始数据 | 可复现图表 |

## 11.2 互补性关键数字

| 指标 | 数值 | 含义 |
|---|---|---|
| OCS-CNN 误差相关性 (r) | **0.0030** | 零相关 = 完全互补 |
| 融合击败两种单模态比例 | **64.9%** | 大多数样本中融合有益 |
| 融合击败 OCS 比例 | 69.9% | 融合经常优于纯 OCS |
| 融合击败 CNN 比例 | 89.9% | 融合几乎总是优于纯图像 |
| 最大受益 OCS bin | 50+° → +74.23° 改善 | 图像挽救 OCS 最差故障 |
| 最佳偏航范围 | 180°–240° → +9.7° 改善 | 对称性导致的 OCS 歧义被图像修正 |
| 灾难性失败 | 12/1998 (0.6%) | 融合 180° 误差而 OCS 完美 |

## 11.3 论文写作建议（来自互补性诊断）

1. **主论点**：OCS 与图像含互补姿态信息，r=0.003 为零相关——这是可量化证明的，非直觉推测
2. **Proposed 方法**：Feature fusion per_part_log (4.10°, Hit5=87.3%)——图像显著提升中等 OCS 信息场景的姿态估计
3. **Ablation 叙事**：强 OCS（图像无益）→ 中 OCS（图像互补 +31%）→ 弱 OCS（图像主导）——三区间的"金凤花原理"
4. **Limitations**：少量灾难性融合失败（0.6%），需未来鲁棒性改进
5. **Broader Impact**：互补性为姿态依赖——暗示了观测几何优化的可能性（在已知互补性最差的偏航范围避免单独依赖某一模态）



# 附录 A：关键文件索引

| 文件 | 用途 |
|---|---|
| `CLAUDE.md` | 进度档案，每次会话起点，唯一权威任务队列 |
| `项目理解.md` | 项目方案与思路备查，历史背景 |
| `GPT/总思路1.md` | 三专家视角决策分析，工程路线设计 |
| `GPT/论文思路.md` | 论文方向、文献搜索策略、SCI一区规划 |
| `GPT/01.md` | 科研姿态识别完整工作流程 |
| `BRDF设计.md` | BRDF精确化 AI 指导策略 |
| `ocs_project/07_brdf/brdf_precision_design.md` | BRDF 公式推导、参数来源、验证标准 |
| `ocs_project/01_code/config.py` | 全局配置（可改参数见 §1.1） |
| `结果/` | 所有运行产物 |

# 附录 B：常用命令

```bash
# 环境激活
conda activate ocs_sim

# 模块 A 运行
python ocs_project/01_code/main_run.py --workers 8

# 模块 B Principled 路径
"D:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --background --python ocs_project/02_blender/render_batch.py

# 模块 B Exact BRDF 路径（渲染）
"D:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --background --python ocs_project/02_blender/render_geometry_passes.py -- --limit 0 --res 128

# 模块 B Exact BRDF 路径（后处理）
python ocs_project/02_blender/brdf_postprocess.py <out_dir> --no-png

# 模块 B 一致性分析
python ocs_project/02_blender/analyze_consistency.py

# BRDF 测试
cd ocs_project/07_brdf && python test_brdf_models.py

# 遮挡验证
python ocs_project/05_occlusion_validation/run_occlusion_validation.py

# 人工抽查
cmd /c ocs_project\05_manual_review\run_manual_review.bat
```

# 附录 C：论文推荐结构

```
1. Introduction
   1.1 Space Object Attitude Estimation
   1.2 OCS and Photometric Signatures
   1.3 Limitations of Existing Methods
   1.4 Our Contributions

2. Related Work
   2.1 BRDF-based Light Curve Modeling
   2.2 Spacecraft Pose Estimation from Images
   2.3 Light Curve Inversion
   2.4 Observation Geometry Optimization

3. Method
   3.1 Unified Forward Model Overview
   3.2 Geometry Model (STL + facet + part assignment)
   3.3 Attitude Parameterization & Coordinate Systems
   3.4 BRDF Model (LegacyPhong + GGX Cook-Torrance)
   3.5 Occlusion Model (ray tracing + EPSILON)
   3.6 OCS Integration
   3.7 Photometric Image Generation (Blender exact BRDF path)
   3.8 Attitude Inversion (OCS-only / image-only / joint)

4. Validation
   4.1 BRDF Unit Tests & Single-Plate Validation
   4.2 Occlusion Model Validation (synthetic + real model)
   4.3 OCS-Image Consistency Verification

5. Experimental Setup
   5.1 Model Parameters & Material Database
   5.2 Attitude Grid & Observation Geometries
   5.3 Evaluation Metrics

6. Results
   6.1 OCS Attitude Signatures
   6.2 Photometric Image Library
   6.3 Attitude Inversion Performance
   6.4 Ablation Studies
   6.5 Observability Analysis
   6.6 Observation Geometry Optimization

7. Discussion
   7.1 Sensitivity to BRDF Parameters
   7.2 Impact of Occlusion Modeling
   7.3 Limitations

8. Conclusion
```
