# 路线一 C 单姿态 smoke test 与资源估计方案（Claude 输出）

生成时间：2026-06-22
任务编号：1C-C02
执行者：Claude
状态：设计阶段，未执行

## 0. 上下文恢复确认

已完成轻量上下文恢复，确认以下要点：

### 0.1 当前科学主线

```text
model-known 条件下，独立 OCS 光度通道与图像成像通道共享同一物理前向模型时，
跨几何 OCS 多观测光度向量与图像通道对姿态信息的可观测性、互补性和置信一致性研究。
```

### 0.2 路线一 C 定位

```text
保留 v0.4 pixel-level OCS-image 同源前向架构；
以五参数冯 / Phong-like BRDF 与书中典型材料参数作为主 BRDF 锚点；
以 GGX / Cook-Torrance 作为 BRDF mismatch、现代 PBR 对照和鲁棒性分支；
主实验仍为 fixed-roll yaw-pitch controlled benchmark；
反演降级为可观测性、互补性和置信一致性的验证工具。
```

### 0.3 本轮任务边界

**本轮只做"设计 smoke test 与资源估计"，不执行。**

禁止事项：
- 不创建 `06_v0.4_code/` 代码区
- 不创建 `07_v0.4_results/` 输出区
- 不复制历史快照代码
- 不修改任何代码、配置、总览、冻结文件或 CLAUDE.md
- 不实际运行 Blender
- 不进入全量生成
- 不训练模型
- 不把 smoke test 结果写成实验结论

所有路径若涉及尚未创建的新代码区或输出区，必须标注为：`[拟议路径，待作者/Codex确认]`

所有历史快照代码路径必须标注为：`[历史快照参考，不直接运行]`


## 1. 一句话结论

**当前可以"设计 smoke test 与资源估计方案"，但不能直接执行。**

原因：
1. **设计可行**：已有 1C-C01-R1 代码入口盘点清单，明确了可复用/禁用/待新建资产三分表，设计所需的概念性输入输出定义已清楚。
2. **不能执行**：
   - v0.4 正式代码区（`06_v0.4_code/`）尚未创建
   - v0.4 输出根目录（`07_v0.4_results/`）尚未创建
   - 关键新模块（sun-view depth 渲染、reprojection、五参数冯 BRDF）尚未实现
   - 历史快照代码需要改造后才能使用，不能直接运行
   - 环境准备（Blender版本、Python环境、依赖库）尚未确认

**本方案输出后，必须经 Codex 审阅通过，并由作者确认创建代码区、实现关键模块后，才能进入实际执行阶段（Phase 0 gate）。**


## 2. smoke test 最小输入设计

### 2.1 设计目标

单姿态 smoke test 的目标是验证 v0.4 pixel-level OCS-image 同源前向链路能否在概念和流程上端到端闭合，不追求数值精度或全量覆盖。

通过标准：
1. camera-view geometry pass 能渲染出完整的 Normal/Depth/IndexOB/Position 通道
2. sun-view depth pass 能渲染出物理合理的 sun-view depth
3. V_sun_macro reprojection 能生成二值 mask，与图像尺寸一致
4. BRDF 后处理与 OCS 积分能产生 OCS > 0 且 per-part OCS 合理
5. 生成的图像非全黑/全白，I_linear 数值范围合理
6. manifest 字段符合 14 号规范，包含 BRDF、几何、姿态、路径、版本等可审计字段
7. 输出文件路径、命名、格式符合 13 号规范约定

### 2.2 最小输入配置表

| 配置项 | 值 | 状态 | 备注 |
|---|---|---|---|
| **目标模型** | "真实模型"三部件（jinshuzhuti + taiyangnengban + yinshenban） | [待确认] STL 文件位置 | 优先使用已有稳定模型；若 STL 路径未确认，需作者提供 |
| **姿态** | yaw=45°, pitch=30°, roll=0° | 可用 | fixed-roll 受控变量，yaw/pitch 选择中等值避免极端几何 |
| **观测几何** | G1 / phase63 backscatter | 可用 | 历史基线几何，sun/view 夹角 63°，backscatter 方向 |
| **sun 矢量** | [归一化，具体值待13号规范或历史配置] | [待确认] | 需从 phase63 定义或历史 config.py 中提取 |
| **view 矢量** | [归一化，具体值待13号规范或历史配置] | [待确认] | 需从 phase63 定义或历史 config.py 中提取 |
| **BRDF 主模式** | 五参数冯 / Phong-like | [待实现] | f_r = rho_d/π + rho_s·(N·H)^n；若尚未实现，只能先标注为待实现，不能用 GGX 顶替 |
| **BRDF 材料参数** | 书中典型空间材料参数 | [待确认] | 需从书籍知识库或 materials.py 对齐后提供 |
| **分辨率** | 256×256 | 可用 | 最小验证分辨率，避免过大耗时 |
| **正交投影范围** | ortho_scale = 2.2 × r_max | 可用 | 历史配置参考值，确保模型完整可见 |
| **输出根目录** | `07_v0.4_results/00_smoke_test/` | [拟议路径，待作者/Codex确认] | 当前不存在 |
| **代码根目录** | `06_v0.4_code/` | [拟议路径，待作者/Codex确认] | 当前不存在 |

### 2.3 最小输入状态总结

**已明确可用**：
- 姿态配置（yaw/pitch/roll 数值）
- 分辨率（256×256）
- 正交投影范围（ortho_scale = 2.2）
- 观测几何层级（G1 / phase63）

**待作者/Codex确认**：
- 目标模型 STL 文件的具体路径
- phase63 几何的 sun/view 矢量具体数值
- 五参数冯 BRDF 实现是否已存在，若未实现，当前 smoke test 是否允许暂用 GGX 作为临时替代（但必须明确标注为非主线）
- 书中材料参数表的具体来源或数值
- v0.4 代码区和输出区的创建路径

**待新建/实现**：
- 五参数冯 BRDF 模块（若当前未实现）
- sun-view depth 渲染脚本
- V_sun_macro reprojection 脚本
- corpus-level I_scale 统计脚本（两阶段流程）
- 符合 14 号规范的 manifest builder


## 3. 概念调用链

以下是单姿态 smoke test 的概念性调用链，用于说明路线一 C pixel-level OCS-image 同源前向链路的完整流程。**所有路径均为拟议或历史参考，当前不可直接运行。**

### 3.1 步骤 1：camera-view geometry pass 渲染

**功能**：渲染观测相机视角的几何通道（Normal, Depth, IndexOB, Position）

**输入**：
- 目标模型 STL 文件 [待确认路径]
- 姿态：yaw=45°, pitch=30°, roll=0°
- 观测矢量 view [待确认具体数值]
- 分辨率：256×256
- 正交投影范围：ortho_scale = 2.2

**输出**：
- `yaw045_pitch030_0001.exr` [拟议输出路径] `07_v0.4_results/00_smoke_test/00_geometry_passes/yaw045_pitch030_0001.exr`
  - 包含通道：Normal (RGB)、Depth (float32)、IndexOB (uint8)、Position (XYZ, float32)

**参考历史快照**：
- [历史快照参考] `03_项目说明与规划材料/05_参考材料/01_关键代码快照/02_blender/render_geometry_passes.py`
- 需升级项：增加 Position AOV、记录 camera 矩阵、输出到符合 13 号规范的路径结构

**待新建模块**：
- [拟议路径，待确认] `06_v0.4_code/02_blender/render_camera_geometry.py`

**通过标准**：
- EXR 文件存在且可读
- Normal 通道非全零，归一化向量合理
- Depth 通道非全零，数值范围在 [0, ortho_scale] 内
- IndexOB 通道能区分三部件（主体、太阳能板、遮阳板）
- Position 通道记录世界坐标，数值范围与模型尺寸一致

**失败时优先检查项**：
1. Blender 版本是否支持所需 AOV
2. STL 文件路径是否正确
3. 姿态旋转矩阵是否正确应用
4. 正交相机设置是否合理
5. EXR 输出格式是否正确配置


### 3.2 步骤 2：sun-view depth pass 渲染

**功能**：渲染太阳光源视角的深度通道，用于后续阴影判断

**输入**：
- 目标模型 STL 文件 [待确认路径]
- 姿态：yaw=45°, pitch=30°, roll=0°
- 太阳矢量 sun [待确认具体数值]
- 分辨率：256×256
- 正交投影范围：ortho_scale = 2.2

**输出**：
- `yaw045_pitch030_sun_depth.exr` [拟议输出路径] `07_v0.4_results/00_smoke_test/00b_sun_depth_passes/yaw045_pitch030_sun_depth.exr`
  - 包含通道：Depth (float32)

**参考历史快照**：
- 无直接参考，需从 render_geometry_passes.py 改造

**待新建模块**：
- [拟议路径，待新建] `06_v0.4_code/02_blender/render_sun_depth.py`

**通过标准**：
- EXR 文件存在且可读
- Depth 通道非全零
- 深度值物理合理（无负值，范围在正交投影尺度内）
- sun-view 渲染的可见表面应与 camera-view 有部分重叠但不完全相同

**失败时优先检查项**：
1. sun-view 相机设置是否正确（位置、朝向、投影参数）
2. 太阳矢量是否归一化
3. 渲染视锥是否覆盖整个模型
4. Blender scene 设置是否与 camera-view 一致（除相机位置外）


### 3.3 步骤 3：V_sun_macro reprojection

**功能**：将 camera-view 像素反投影到世界坐标，再投影到 sun-view，通过深度比较判断太阳可见性，生成 V_sun_macro mask

**输入**：
- 步骤 1 输出：`yaw045_pitch030_0001.exr` (Depth, Position)
- 步骤 2 输出：`yaw045_pitch030_sun_depth.exr` (Depth)
- camera 投影矩阵 [需从步骤 1 记录]
- sun 投影矩阵 [需从步骤 2 记录]
- depth_epsilon_m：初始值 0.05m（待 20 姿态 shadow validation 校准）

**输出**：
- `yaw045_pitch030_v_sun_macro.npy` [拟议输出路径] `07_v0.4_results/00_smoke_test/01_sun_shadow_reprojection/yaw045_pitch030_v_sun_macro.npy`
  - shape: (256, 256), dtype: uint8, 值域: {0, 1}
  - 0 = 被遮挡（sun-shadowed），1 = 太阳可见
- `yaw045_pitch030_v_sun_macro.png` [拟议输出路径] 可视化图像

**参考历史快照**：
- 无直接参考

**待新建模块**：
- [拟议路径，待新建] `06_v0.4_code/04_sun_shadow/sun_shadow_reprojection.py`

**算法概要**（依据 13 号规范 §7.3.2）：
```python
for each pixel (u, v) in camera-view:
    if camera_depth[u, v] == background:
        V_sun_macro[u, v] = 0  # 背景不计入
        continue
    
    # 1. camera depth → world position
    P_world = camera_unproject(u, v, camera_depth[u, v], camera_matrix)
    
    # 2. world → sun-view pixel
    (u_sun, v_sun) = sun_project(P_world, sun_matrix)
    
    # 3. 读取 sun-view depth
    d_sun_query = sun_depth[u_sun, v_sun]
    d_sun_expected = distance(P_world, sun_camera_origin)
    
    # 4. 深度比较
    if d_sun_expected <= d_sun_query + depth_epsilon_m:
        V_sun_macro[u, v] = 1  # 太阳可见
    else:
        V_sun_macro[u, v] = 0  # 被遮挡
```

**通过标准**：
- npy 文件存在，shape = (256, 256), dtype = uint8
- 值域严格为 {0, 1}
- png 可视化图像中，遮挡区域与模型几何结构合理对应
- 背景像素应为 0
- 目视检查：太阳能板正面应为 1，背面应为 0（若可见）

**失败时优先检查项**：
1. camera/sun 矩阵是否正确记录和传递
2. depth_epsilon_m 是否过大或过小
3. 坐标变换是否正确（特别是 camera → world → sun 的链式变换）
4. 边界处理是否正确（out-of-bounds 像素应如何处理）


### 3.4 步骤 4：BRDF 后处理与 OCS 积分

**功能**：计算 pixel-level BRDF，应用 V_sun_macro mask，积分得到 OCS，生成线性图像和 log1p 归一化图像

**输入**：
- 步骤 1 输出：`yaw045_pitch030_0001.exr` (Normal, IndexOB)
- 步骤 3 输出：`yaw045_pitch030_v_sun_macro.npy`
- 五参数冯 BRDF 参数 [待确认]：rho_d, rho_s, n (specular exponent) for each part
- sun 矢量、view 矢量
- 像素面积 pixel_area_m2（从正交投影计算）

**输出**：
- `yaw045_pitch030_linear.exr` [拟议输出路径] `07_v0.4_results/00_smoke_test/02_brdf_postprocess/yaw045_pitch030_linear.exr`
  - I_linear (float32)：未归一化的线性辐射亮度
- `yaw045_pitch030_brdf.png` [拟议输出路径] `07_v0.4_results/00_smoke_test/02_brdf_postprocess/yaw045_pitch030_brdf.png`
  - log1p 归一化后的 uint8 可视化图像
- `yaw045_pitch030_ocs.json` [拟议输出路径] `07_v0.4_results/00_smoke_test/02_brdf_postprocess/yaw045_pitch030_ocs.json`
  - per-frame OCS：ocs_total, ocs_per_part (dict: {part_name: ocs_value})

**参考历史快照**：
- [历史快照参考，需大幅修改] `03_项目说明与规划材料/05_参考材料/01_关键代码快照/02_blender/brdf_postprocess.py`
- 需修改项：
  1. 从 face-center 改为 pixel-level
  2. 加入 V_sun_macro 到 BRDF 和 OCS 计算
  3. 实现五参数冯公式：f_r = rho_d/π + rho_s·(N·H)^n
  4. 实现 corpus-level I_scale 两阶段流程（当前 smoke test 只做单帧，可暂用 per-frame normalization，但需标注）

**待新建模块**：
- [拟议路径，待新建/改造] `06_v0.4_code/03_brdf/phong_five_param.py`
- [拟议路径，待新建/改造] `06_v0.4_code/05_postprocess/ocs_integration_v0.4.py`
- [拟议路径，待新建/改造] `06_v0.4_code/05_postprocess/image_response_v0.4.py`

**BRDF 计算公式**（五参数冯主线）：
```python
N = Normal[u, v]
L = sun_vector (归一化)
V = view_vector (归一化)
H = normalize(L + V)

NoL = dot(N, L)
NoH = dot(N, H)

if V_sun_macro[u, v] == 0 or NoL <= 0:
    f_r = 0  # 被遮挡或背光
else:
    f_r = rho_d / pi + rho_s * pow(NoH, n)

I_linear[u, v] = f_r * NoL * E_sun * pixel_area_m2
```

**OCS 积分公式**：
```python
ocs_total = sum(I_linear[u, v] for all pixels) * solid_angle_per_pixel

ocs_per_part[part_name] = sum(I_linear[u, v] for pixels where IndexOB == part_id) * solid_angle_per_pixel
```

**通过标准**：
- I_linear.exr 存在，数值范围合理（如 0.01 ~ 10.0，具体取决于 E_sun 和材料参数）
- brdf.png 存在，非全黑/全白，能看到模型轮廓和明暗变化
- ocs.json 存在，ocs_total > 0
- ocs_per_part 合理：通常 主体 > 太阳能板 > 遮阳板（取决于材料和几何）
- V_sun_macro = 0 的像素对应的 I_linear 应为 0

**失败时优先检查项**：
1. V_sun_macro 是否正确应用到 BRDF 计算
2. NoL 是否正确计算（负值应置零）
3. 五参数冯公式是否正确实现
4. rho_d, rho_s, n 参数是否合理
5. E_sun（太阳辐照度）是否设置
6. pixel_area_m2 和 solid_angle_per_pixel 是否正确计算


### 3.5 步骤 5：单条 manifest 生成

**功能**：生成符合 14 号规范的单条 OCS manifest 和 image manifest，用于校验字段完整性和可审计性

**输入**：
- 步骤 4 所有输出文件路径
- 姿态、几何、BRDF 参数
- 软件版本、随机种子、生成时间等元信息

**输出**：
- `smoke_test_manifest_ocs.json` [拟议输出路径] `07_v0.4_results/00_smoke_test/03_manifests/smoke_test_manifest_ocs.json`
- `smoke_test_manifest_image.json` [拟议输出路径] `07_v0.4_results/00_smoke_test/03_manifests/smoke_test_manifest_image.json`

**参考历史快照**：
- [历史快照参考，需升级] `03_项目说明与规划材料/05_参考材料/01_关键代码快照/03_inversion/inv_common.py`
- 需升级项：manifest schema 升级到 14 号规范

**待新建模块**：
- [拟议路径，待新建] `06_v0.4_code/06_manifest/ocs_manifest_builder.py`
- [拟议路径，待新建] `06_v0.4_code/06_manifest/image_manifest_builder.py`

**14 号规范必需字段**（OCS manifest，依据 14 号规范 §3.1）：
```json
{
  "sample_id": "yaw045_pitch030_phase63_phong",
  "yaw": 45.0,
  "pitch": 30.0,
  "roll": 0.0,
  "phase_angle": 63.0,
  "sun_vector": [x, y, z],
  "det_vector": [x, y, z],
  "ocs_total": 0.xxxx,
  "ocs_per_part": {"jinshuzhuti": 0.xx, "taiyangnengban": 0.xx, "yinshenban": 0.xx},
  "brdf_model": "phong_five_param",
  "brdf_params": {"rho_d": [...], "rho_s": [...], "n": [...]},
  "geometry_pass_path": "relative/path/to/yaw045_pitch030_0001.exr",
  "sun_depth_path": "relative/path/to/yaw045_pitch030_sun_depth.exr",
  "v_sun_macro_path": "relative/path/to/yaw045_pitch030_v_sun_macro.npy",
  "linear_image_path": "relative/path/to/yaw045_pitch030_linear.exr",
  "depth_epsilon_m": 0.05,
  "blender_version": "x.x.x",
  "code_version": "v0.4_smoke_test",
  "generated_at": "2026-06-22T..."
}
```

**14 号规范必需字段**（image manifest，依据 14 号规范 §3.2）：
```json
{
  "sample_id": "yaw045_pitch030_phase63_phong",
  "yaw": 45.0,
  "pitch": 30.0,
  "roll": 0.0,
  "phase_angle": 63.0,
  "sun_vector": [x, y, z],
  "det_vector": [x, y, z],
  "image_path": "relative/path/to/yaw045_pitch030_brdf.png",
  "linear_image_path": "relative/path/to/yaw045_pitch030_linear.exr",
  "geometry_pass_path": "relative/path/to/yaw045_pitch030_0001.exr",
  "brdf_model": "phong_five_param",
  "brdf_params": {"rho_d": [...], "rho_s": [...], "n": [...]},
  "normalization": "log1p_corpus_level",
  "i_scale_corpus": null,
  "resolution": 256,
  "blender_version": "x.x.x",
  "code_version": "v0.4_smoke_test",
  "generated_at": "2026-06-22T..."
}
```

**通过标准**：
- 两个 manifest JSON 文件存在且可解析
- 所有 14 号规范必需字段存在
- 路径字段指向的文件确实存在
- 姿态、几何、BRDF 参数与实际输入一致
- 可通过 manifest 完整追溯生成过程

**失败时优先检查项**：
1. 14 号规范字段是否遗漏
2. 路径是否为相对路径
3. 数值精度是否合理
4. BRDF 参数是否完整记录


### 3.6 步骤 6：smoke test report 生成

**功能**：汇总上述所有步骤的通过/失败状态，生成人类可读的测试报告

**输出**：
- `smoke_test_report.md` [拟议输出路径] `07_v0.4_results/00_smoke_test/smoke_test_report.md`

**内容建议**：
```markdown
# 路线一 C 单姿态 smoke test 报告

执行时间：2026-06-22
姿态：yaw=45°, pitch=30°, roll=0°
几何：phase63
BRDF：五参数冯

## 通过/失败汇总
- [ ] 步骤 1：camera geometry pass
- [ ] 步骤 2：sun-view depth pass
- [ ] 步骤 3：V_sun_macro reprojection
- [ ] 步骤 4：BRDF 后处理与 OCS 积分
- [ ] 步骤 5：manifest 生成
- [ ] 步骤 6：字段完整性检查

## 关键输出
- ocs_total: 0.xxxx
- ocs_per_part: {...}
- I_linear 数值范围: [min, max]
- V_sun_macro 遮挡率: xx%

## 待修正问题
（记录失败步骤的诊断信息）
```

**通过标准**：
- 所有步骤通过
- 关键输出数值物理合理
- 无明显几何/BRDF/可见性错误

**失败时优先检查项**：
- 参考各步骤的"失败时优先检查项"


## 4. 预期输出文件结构

以下是单姿态 smoke test 的预期输出文件结构。**所有路径均为拟议路径，待作者/Codex确认。**

### 4.1 完整文件树

```text
[拟议输出根目录，待确认] 07_v0.4_results/00_smoke_test/
├── 00_geometry_passes/
│   ├── yaw045_pitch030_0001.exr          # camera geometry pass (Normal, Depth, IndexOB, Position)
│   └── camera_matrix_yaw045_pitch030.npy  # camera 投影矩阵，供后续步骤使用
├── 00b_sun_depth_passes/
│   ├── yaw045_pitch030_sun_depth.exr     # sun-view depth pass
│   └── sun_matrix_yaw045_pitch030.npy    # sun 投影矩阵
├── 01_sun_shadow_reprojection/
│   ├── yaw045_pitch030_v_sun_macro.npy   # V_sun_macro mask (256×256, uint8, {0,1})
│   └── yaw045_pitch030_v_sun_macro.png   # V_sun_macro 可视化
├── 02_brdf_postprocess/
│   ├── yaw045_pitch030_linear.exr        # I_linear (float32 未归一化线性辐射亮度)
│   ├── yaw045_pitch030_brdf.png          # log1p 归一化 uint8 可视化图像
│   └── yaw045_pitch030_ocs.json          # per-frame OCS (total + per_part)
├── 03_manifests/
│   ├── smoke_test_manifest_ocs.json      # 单条 OCS manifest (符合 14 号规范)
│   └── smoke_test_manifest_image.json    # 单条 image manifest (符合 14 号规范)
└── smoke_test_report.md                  # 通过/失败判据与诊断报告
```

### 4.2 文件大小估计（单姿态 256×256）

| 文件 | 估计大小 | 依据 |
|---|---|---|
| `yaw045_pitch030_0001.exr` | ~2-4 MB | 4 通道 float32：256×256×4×4 bytes ≈ 1 MB，EXR 压缩后约 2-4 MB |
| `camera_matrix_yaw045_pitch030.npy` | ~1 KB | 4×4 矩阵 float64 |
| `yaw045_pitch030_sun_depth.exr` | ~0.5-1 MB | 1 通道 float32 |
| `sun_matrix_yaw045_pitch030.npy` | ~1 KB | 4×4 矩阵 float64 |
| `yaw045_pitch030_v_sun_macro.npy` | ~65 KB | 256×256 uint8 ≈ 64 KB |
| `yaw045_pitch030_v_sun_macro.png` | ~10-50 KB | PNG 压缩 |
| `yaw045_pitch030_linear.exr` | ~0.5-1 MB | 1 通道 float32 |
| `yaw045_pitch030_brdf.png` | ~50-200 KB | uint8 RGB PNG |
| `yaw045_pitch030_ocs.json` | ~1 KB | JSON 文本 |
| `smoke_test_manifest_ocs.json` | ~2 KB | JSON 文本 |
| `smoke_test_manifest_image.json` | ~2 KB | JSON 文本 |
| `smoke_test_report.md` | ~5-10 KB | Markdown 文本 |
| **单姿态总计** | **~4-8 MB** | 主要存储为 EXR 格式 |

### 4.3 文件命名规范

依据 13 号规范和历史约定，建议文件命名遵循：

**姿态标识**：
- 格式：`yaw{YYY}_pitch{PPP}_roll{RRR}`
- YYY：yaw 角度（000-359，三位数，零填充）
- PPP：pitch 角度（000-089，两位数或三位数）
- RRR：roll 角度（固定 000）

**示例**：
- yaw=45°, pitch=30°, roll=0° → `yaw045_pitch030_roll000` 或简化为 `yaw045_pitch030`（当 roll=0 固定时可省略）

**序号**：
- geometry pass EXR 使用四位序号：`_0001.exr`
- 其他文件直接用姿态标识 + 文件类型后缀

### 4.4 目录创建顺序

若实际执行 smoke test，建议按以下顺序创建目录并写入文件：

1. 创建 `07_v0.4_results/00_smoke_test/`
2. 创建各子目录：`00_geometry_passes/`, `00b_sun_depth_passes/`, `01_sun_shadow_reprojection/`, `02_brdf_postprocess/`, `03_manifests/`
3. 依次执行步骤 1-6，输出到对应子目录
4. 最后在根目录生成 `smoke_test_report.md`

### 4.5 文件依赖关系图

```text
STL 模型 + 姿态 + 几何参数
    ↓
[步骤 1] camera geometry pass
    ↓ (yaw045_pitch030_0001.exr, camera_matrix.npy)
    ├──→ [步骤 3] reprojection (需要 camera depth + Position)
    └──→ [步骤 4] BRDF 计算 (需要 Normal + IndexOB)
    
[步骤 2] sun-view depth pass
    ↓ (yaw045_pitch030_sun_depth.exr, sun_matrix.npy)
    └──→ [步骤 3] reprojection (需要 sun depth)

[步骤 3] V_sun_macro reprojection
    ↓ (v_sun_macro.npy)
    └──→ [步骤 4] BRDF 计算 (需要 V_sun_macro mask)

[步骤 4] BRDF 后处理与 OCS 积分
    ↓ (linear.exr, brdf.png, ocs.json)
    └──→ [步骤 5] manifest 生成

[步骤 5] manifest 生成
    ↓ (manifest_ocs.json, manifest_image.json)
    └──→ [步骤 6] smoke test report

[步骤 6] smoke test report
    ↓ (smoke_test_report.md)
    └──→ 人工审阅与 Codex 审阅
```


## 5. 通过 / 失败判据

### 5.1 总体通过标准

**单姿态 smoke test 通过，当且仅当以下所有条件满足：**

1. ✅ 所有步骤（1-6）成功执行，无异常退出
2. ✅ 所有预期输出文件存在且可读
3. ✅ 关键数值物理合理（见 §5.2）
4. ✅ manifest 字段完整性检查通过（见 §5.3）
5. ✅ 可见性/阴影/几何一致性检查通过（见 §5.4）

### 5.2 关键数值物理合理性判据

| 检查项 | 通过标准 | 失败时处理 |
|---|---|---|
| **EXR 文件生成** | 文件存在，所有通道完整，无 NaN/Inf | 检查 Blender 版本、STL 路径、渲染脚本 |
| **Normal 通道** | 归一化向量，‖N‖ ≈ 1.0（允许 ±0.01 误差） | 检查 Normal AOV 配置 |
| **Depth 通道 (camera)** | 非负，范围在 [0, ortho_scale] 内 | 检查相机设置 |
| **Depth 通道 (sun)** | 非负，范围合理 | 检查 sun-view 相机设置 |
| **IndexOB 通道** | 能区分三部件（值域如 {1, 2, 3}） | 检查 STL 是否正确分组 |
| **Position 通道** | 世界坐标，数值范围与模型尺寸一致（如 ±10 m） | 检查坐标系设置 |
| **V_sun_macro 值域** | 严格 {0, 1}，无中间值 | 检查 reprojection 算法，阈值判断 |
| **V_sun_macro 遮挡率** | 合理范围（如 20%-80%），不应全 0 或全 1 | 检查 depth_epsilon_m、几何、sun 方向 |
| **OCS total** | ocs_total > 0 | 检查 BRDF 参数、NoL、V_sun_macro 应用 |
| **OCS per_part** | 所有部件 OCS > 0，合理顺序（如主体 > 帆板 > 遮阳板） | 检查 IndexOB 映射、BRDF 参数 |
| **I_linear 数值范围** | 正值，范围如 0.01 ~ 10.0（取决于 E_sun 和材料） | 检查 BRDF 计算、E_sun 设置 |
| **brdf.png 图像** | 非全黑/全白，能看到模型轮廓和明暗变化 | 检查 log1p 归一化、alpha 参数 |

### 5.3 manifest 字段完整性判据

**OCS manifest 必需字段**（依据 14 号规范 §3.1）：
- ✅ `sample_id`, `yaw`, `pitch`, `roll`
- ✅ `phase_angle`, `sun_vector`, `det_vector`
- ✅ `ocs_total`, `ocs_per_part`
- ✅ `brdf_model`, `brdf_params`
- ✅ `geometry_pass_path`, `sun_depth_path`, `v_sun_macro_path`, `linear_image_path`
- ✅ `depth_epsilon_m`, `blender_version`, `code_version`, `generated_at`

**image manifest 必需字段**（依据 14 号规范 §3.2）：
- ✅ `sample_id`, `yaw`, `pitch`, `roll`
- ✅ `phase_angle`, `sun_vector`, `det_vector`
- ✅ `image_path`, `linear_image_path`, `geometry_pass_path`
- ✅ `brdf_model`, `brdf_params`
- ✅ `normalization`, `i_scale_corpus` (smoke test 可为 null)
- ✅ `resolution`, `blender_version`, `code_version`, `generated_at`

**字段一致性**：
- OCS manifest 和 image manifest 中的姿态、几何、BRDF 参数必须一致
- 路径字段指向的文件必须存在
- 数值精度合理（如 yaw/pitch/roll 保留 1 位小数）

### 5.4 可见性/阴影/几何一致性判据

| 检查项 | 通过标准 | 失败时处理 |
|---|---|---|
| **V_sun_macro 与图像对齐** | V_sun_macro 的形状 (256, 256) 与 camera geometry pass 一致 | 检查分辨率配置 |
| **V_sun_macro = 0 的像素** | 对应 I_linear 应为 0 或接近 0 | 检查 BRDF 计算中 V_sun_macro 是否正确应用 |
| **阴影边界合理性** | V_sun_macro 的 0/1 边界应与模型几何结构对应（如遮阳板遮挡区域） | 目视检查 v_sun_macro.png，对比 brdf.png |
| **背景像素处理** | 背景像素（Depth = max 或 IndexOB = 0）对应的 V_sun_macro 应为 0，I_linear 应为 0 | 检查背景判断逻辑 |
| **NoL < 0 像素处理** | Normal 背向太阳的像素（NoL < 0）对应的 I_linear 应为 0 | 检查 BRDF 计算中 NoL 判断 |
| **部件边界** | IndexOB 边界清晰，不同部件之间无混叠 | 检查 STL 模型质量、Blender 渲染抗锯齿设置 |

### 5.5 失败时诊断流程

**若 smoke test 失败，按以下优先级诊断：**

**P0（阻塞性错误）**：
1. EXR 文件无法生成 → 检查 Blender 安装、STL 路径、渲染脚本语法
2. V_sun_macro 全为 0 或全为 1 → 检查 depth_epsilon_m、sun/camera 矩阵、reprojection 算法
3. OCS = 0 → 检查 BRDF 参数、V_sun_macro 应用、NoL 计算

**P1（数值异常）**：
4. I_linear 数值范围异常（如全为 0.001 或 1000） → 检查 E_sun、pixel_area_m2、BRDF 参数
5. ocs_per_part 不合理（如主体 < 遮阳板） → 检查 IndexOB 映射、材料参数分配

**P2（可视化问题）**：
6. brdf.png 全黑或全白 → 检查 log1p 归一化、alpha 参数、I_linear 动态范围
7. V_sun_macro.png 与几何不符 → 目视检查，调整 depth_epsilon_m

### 5.6 通过后进入条件

**smoke test 通过后，不立即进入全量生成。必须先完成：**

1. ✅ smoke test 通过（本方案 §5.1-5.4）
2. ⬜ depth round-trip 验证通过（1C-C03 任务，3 已知点双向变换误差 < 1 像素）
3. ⬜ 20 姿态 shadow validation 通过（1C-C03 任务，depth_epsilon_m 校准完成）
4. ⬜ Codex 审阅通过 smoke test 输出
5. ⬜ 作者确认是否进入 Phase 1（3 姿态扩展验证）或直接进入 G1 主实验规划

**只有完成上述所有条件，才能通过 Phase 0 gate，进入后续实验规划。**


## 6. 资源估计表

以下资源估计基于历史快照运行记录、Blender 渲染经验估计和路线一成果区规划文件。**所有估计均为粗略级别，实际耗时和存储需求取决于硬件配置、Blender 版本和代码实现质量。**

### 6.1 单姿态资源估计（256×256 分辨率）

| 步骤 | 耗时估计 | 输出大小 | 主要依赖 | 不确定性来源 |
|---|---|---|---|---|
| **步骤 1：camera geometry pass** | 5-30 秒 | ~2-4 MB | Blender 渲染引擎、模型复杂度 | Blender 版本、GPU 加速、模型面数 |
| **步骤 2：sun-view depth pass** | 5-30 秒 | ~0.5-1 MB | Blender 渲染引擎 | 同上 |
| **步骤 3：V_sun_macro reprojection** | 1-5 秒 | ~65 KB (npy) + ~50 KB (png) | NumPy 矩阵运算 | 算法实现效率 |
| **步骤 4：BRDF 后处理与 OCS** | 2-10 秒 | ~1.5 MB (exr+png+json) | CPU/NumPy 计算 | BRDF 公式复杂度、是否向量化 |
| **步骤 5：manifest 生成** | < 1 秒 | ~4 KB (2 个 JSON) | JSON 序列化 | 可忽略 |
| **步骤 6：smoke test report** | < 1 秒 | ~10 KB (markdown) | 文本生成 | 可忽略 |
| **单姿态总计** | **15-80 秒** | **~4-8 MB** | Blender + Python + NumPy | Blender 渲染是主要瓶颈 |

**硬件假设**：
- CPU：8 核心
- GPU：支持 CUDA 或 OptiX（Blender Cycles）
- 内存：16 GB
- 存储：SSD

**不确定性说明**：
- Blender 渲染耗时高度依赖于 GPU 加速和渲染引擎（Cycles vs Eevee）。若使用 CPU-only 渲染，耗时可能增加 5-10 倍。
- 模型面数：历史"真实模型"三部件总面数未确认，若面数 > 100k，渲染耗时可能显著增加。
- Python 后处理（步骤 3-4）可通过 NumPy 向量化优化，当前估计假设已向量化。

### 6.2 G1/G3/G5 多几何扩展估计

#### 6.2.1 姿态网格规模（fixed-roll yaw-pitch）

依据路线一冻结文件和历史配置：
- **NUM_YAW = 72**（不含 360°，5° 间隔）
- **NUM_PITCH = 37**（0° 到 180°，5° 间隔）
- **固定 roll = 0**
- **总姿态数 = 72 × 37 = 2664 姿态**

#### 6.2.2 G1 单几何 baseline

| 项目 | 值 | 说明 |
|---|---|---|
| **几何数** | 1（phase63） | single-geometry baseline |
| **姿态数** | 2664 | 72 × 37 fixed-roll 网格 |
| **总样本数** | 2664 | G1 下界 |
| **总耗时（Blender 渲染）** | **11-22 小时** | 2664 × (10-30秒) / 3600 |
| **总存储（EXR + 中间产物）** | **10-21 GB** | 2664 × (4-8 MB) |
| **manifest 文件** | ~10 MB | 2664 条 × 4 KB |

**备注**：
- G1 是路线一 C 必做的公平基线，用于排除多几何增益的干扰。
- 11-22 小时假设串行渲染；若 Blender 支持批量并行（多进程），可按 CPU 核心数线性加速。

#### 6.2.3 G3 少量几何增益验证

| 项目 | 值 | 说明 |
|---|---|---|
| **几何数** | 3（如 phase45, phase63, phase90） | 代表性 phase 角度 |
| **姿态数** | 2664 | 固定 |
| **总样本数** | 7992 | 2664 × 3 |
| **总耗时（Blender 渲染）** | **33-66 小时** | 7992 × (10-30秒) / 3600 |
| **总存储** | **32-64 GB** | 7992 × (4-8 MB) |

**备注**：
- G3 用于验证少量多几何是否能提升 OCS 可观测性。
- 3 个几何的选择依据：phase45（前向散射偏移）、phase63（历史基线）、phase90（侧向散射）。

#### 6.2.4 G5 完整主线候选

| 项目 | 值 | 说明 |
|---|---|---|
| **几何数** | 5（phase24/45/63/90/120） | 历史完整几何集 |
| **姿态数** | 2664 | 固定 |
| **总样本数** | 13320 | 2664 × 5 |
| **总耗时（Blender 渲染）** | **55-111 小时** | 13320 × (10-30秒) / 3600 |
| **总存储** | **53-106 GB** | 13320 × (4-8 MB) |

**备注**：
- G5 是路线一 C 的完整主线候选，覆盖前向、侧向、后向散射。
- 若 G3 已证明多几何增益明显，G5 作为主论文结果；若 G3 增益不明显，G5 可能降级为补充实验。

#### 6.2.5 资源汇总对比表

| 几何层级 | 样本数 | 耗时（串行） | 存储 | 作用 | 是否进入主线 |
|---|---|---|---|---|---|
| **G1** | 2664 | 11-22 h | 10-21 GB | single-geometry 公平基线 | ✅ 必做 |
| **G3** | 7992 | 33-66 h | 32-64 GB | 少量多几何增益验证 | ✅ 优先 |
| **G5** | 13320 | 55-111 h | 53-106 GB | 完整主线候选 | ✅ 主论文候选 |
| **G9** | 23976 | 100-200 h | 96-192 GB | 更密 phase 集合 | ⬜ 暂作扩展 |
| **G12** | 31968 | 133-266 h | 128-256 GB | 全 phase 覆盖 | ⬜ 不作为默认主线 |

### 6.3 roll sensitivity 探针规模估计

依据路线一冻结文件 §8：roll sensitivity 是主线必做探针，不是可选项，也不是三轴小项目的替代品。

#### 6.3.1 最小 roll sensitivity 实验设计

**目标**：验证 fixed-roll 结论是否被 roll 扰动推翻，量化三件事——
1. **signature 漂移幅度**：OCS 向量与图像随 roll 变化多大
2. **混淆结构稳定性**：roll≠0 时 yaw-pitch 混淆图是否被推翻
3. **最亮点迁移**：fixed-roll 条件下的最亮姿态在 roll≠0 时是否仍是最亮

**实验矩阵**：
- **姿态子集**：从 2664 姿态中选择代表性子集
  - 高亮姿态：~10 个（从 fixed-roll 结果中选 top-10 brightest）
  - 高混淆姿态：~10 个（从 fixed-roll 结果中选 top-10 confused）
  - 低亮/低信息姿态：~5 个
  - 边界姿态（pitch 接近 0° 或 180°）：~5 个
  - **子集总数：~30 姿态**
  
- **roll 扰动范围**：roll ∈ {0°, ±5°, ±10°, ±15°}
  - 0°：baseline（已有）
  - ±5°, ±10°, ±15°：6 个扰动值
  - **每个姿态需额外运行 6 次**
  
- **几何选择**：优先单几何（phase63），避免 roll × geometry 组合爆炸
  - 若资源允许，可扩展到 G3

**资源估计**：

| 项目 | 值 | 说明 |
|---|---|---|
| **姿态子集** | 30 | 代表性子集 |
| **roll 扰动值** | 7（包含 0°） | {0°, ±5°, ±10°, ±15°} |
| **几何数** | 1 (phase63) | 单几何优先 |
| **总样本数** | 210 | 30 × 7 × 1 |
| **总耗时** | **0.9-1.75 小时** | 210 × (10-30秒) / 3600 |
| **总存储** | **0.8-1.7 GB** | 210 × (4-8 MB) |

**若扩展到 G3**：
- 总样本数：630（30 × 7 × 3）
- 总耗时：2.6-5.25 小时
- 总存储：2.5-5 GB

**执行时机**：
- roll sensitivity 应在 fixed-roll 主实验（G1/G3/G5）完成后执行，因为需要从 fixed-roll 结果中选择代表性姿态子集。
- 不能与 G1/G3/G5 同时启动，否则无法选择高亮/高混淆姿态。

#### 6.3.2 roll sensitivity 与资源估计的关系

**重要判断**（来自路线一冻结文件 §8）：
- roll sensitivity 与资源估计是"且"的关系，不是"或"。
- 资源估计表明 full 3-DOF 全量数据规模过大（见 §6.4），这是不做 full 3-DOF 的依据。
- roll sensitivity 探针提供了 roll 扰动的定量边界，是答辩防线和高刊 rebuttal 弹药。
- 二者并行完成，不能相互替代。

### 6.4 full 3-DOF 全量为何不作为路线一 C 当前主实验

#### 6.4.1 full 3-DOF 全量规模估计

若要做完整三轴姿态网格：
- **NUM_YAW = 72**
- **NUM_PITCH = 37**
- **NUM_ROLL = 72**（假设 roll 也采用 5° 间隔，0° 到 355°）
- **总姿态数 = 72 × 37 × 72 = 191,808 姿态**

**G1 单几何 full 3-DOF**：

| 项目 | 值 |
|---|---|
| **样本数** | 191,808 |
| **总耗时（串行，按 20秒/姿态）** | **1065 小时 ≈ 44 天** |
| **总存储** | **767 GB - 1.5 TB** |

**G5 五几何 full 3-DOF**：

| 项目 | 值 |
|---|---|
| **样本数** | 959,040 |
| **总耗时（串行）** | **5328 小时 ≈ 222 天** |
| **总存储** | **3.8 - 7.5 TB** |

#### 6.4.2 为何不作为路线一 C 主实验

**原因 1：资源规模超出硕士论文合理范围**
- 44 天串行渲染时间，即使 8 核并行仍需 5.5 天（G1 单几何）
- 767 GB - 1.5 TB 存储需求超出常规工作站配置
- G5 五几何更不现实（222 天串行 / 27 天 8 核并行，3.8-7.5 TB 存储）

**原因 2：路线一 C 科学定位不要求 full 3-DOF**
- 路线一 C 的定位是"受控 fixed-roll yaw-pitch benchmark 下的可观测性、互补性和置信一致性研究"
- roll 作为显式固定的受控变量，通过 roll sensitivity 探针量化边界，这是合理的实验设计，而非简化或示弱
- 真正的三轴姿态搜索和观测规划由三轴小项目负责，不是路线一 C 的主线任务

**原因 3：数据规模与信息增益不成比例**
- full 3-DOF 将数据量从 2664 增加到 191,808（72 倍），但 roll 维度的信息增益是否值得这 72 倍成本，需要先通过 roll sensitivity 探针评估
- 若 roll sensitivity 显示 roll 扰动对可观测性结论影响有限，则 full 3-DOF 的必要性下降
- 若 roll sensitivity 显示 roll 显著改变可观测性地图，则应先优化 roll 采样策略（如自适应采样），而不是盲目全量

**原因 4：答辩与发刊策略**
- 硕士论文答辩委员关心的是"为什么固定 roll"和"roll≠0 会怎样"，这两个问题通过 roll sensitivity + 资源估计 + 后续路线（三轴小项目）可以清晰回答
- 高刊审稿人若质疑 fixed-roll，可用 roll sensitivity 数据反驳"并非忽略 roll，而是量化了 roll 边界"
- full 3-DOF 只会增加数据规模，不会显著提升论文的科学贡献和答辩说服力

**原因 5：三轴小项目作为后续自然扩展**
- 三轴小项目不是 full 3-DOF 全量，而是智能三轴搜索（种子点 + 局部扫描 + 稀疏采样 + 加密搜索）
- 三轴小项目的目标是最亮构型、高信息构型和观测规划，而不是完整三轴姿态空间覆盖
- 这是资源可控且科学价值更高的路径

#### 6.4.3 结论

**路线一 C 不做 full 3-DOF 全量，原因是：**
1. 资源规模超出硕士论文合理范围（44 天渲染，767 GB 存储）
2. 科学定位不要求 full 3-DOF（fixed-roll 是受控实验设计，不是简化）
3. roll sensitivity 探针 + 三轴小项目提供了资源可控且科学价值更高的路径
4. 答辩与发刊策略不需要 full 3-DOF 来支撑主线成立

**full 3-DOF 只在以下条件下考虑进入后续工作：**
- 三轴小项目完成后，发现需要更密集的三轴覆盖
- 路线二 GEO 真实光度锚点或路线三暗室闭环要求三轴验证
- 后续博士论文或独立项目扩展

### 6.5 训练与反演资源估计（粗略级别）

**说明**：路线一 C 的反演只作为可观测性验证工具，不作为真实反演成功率。以下估计用于规划训练资源，不进入本次 smoke test。

#### 6.5.1 数据集划分

假设 G5 主线（13320 样本）：
- 训练集：70% ≈ 9324 样本
- 验证集：15% ≈ 2000 样本
- 测试集：15% ≈ 2000 样本

#### 6.5.2 训练耗时估计（单模型）

| 模型 | 网络结构 | 单 epoch 耗时 | 收敛 epoch 数 | 总耗时 |
|---|---|---|---|---|
| **OCS-only MLP** | 5-layer MLP, input dim = OCS × G | ~30 秒 | 100-200 | 0.8-1.7 小时 |
| **image-only CNN** | ResNet18 / VGG16, input = 256×256 | ~10-30 分钟 | 50-100 | 8-50 小时 |
| **fusion (early)** | 同上 + OCS 拼接 | ~10-30 分钟 | 50-100 | 8-50 小时 |
| **fusion (late)** | 两路独立 + 融合层 | ~15-40 分钟 | 50-100 | 12-67 小时 |

**硬件假设**：单 GPU（如 RTX 3090 / A100）

#### 6.5.3 指标计算耗时

路线一 C 要求输出候选分布、entropy、margin、JS、overlap、reject/conflict 等指标（见 04_v0.4信息量与置信指标实现规范），而不是只给一个误差表。

| 指标 | 计算复杂度 | 估计耗时（测试集 2000 样本） |
|---|---|---|
| **top-k accuracy** | O(N) | < 1 分钟 |
| **candidate distribution** | O(N × K) | ~5 分钟（K = 候选姿态数） |
| **entropy / margin** | O(N × K) | ~5 分钟 |
| **JS divergence** | O(N × K) | ~10 分钟 |
| **overlap** | O(N × K) | ~10 分钟 |
| **reject / conflict rate** | O(N) | ~5 分钟 |
| **总计** | - | **~35 分钟** |

### 6.6 资源估计总结表

| 任务阶段 | 耗时 | 存储 | 关键依赖 | 是否阻塞后续 |
|---|---|---|---|---|
| **单姿态 smoke test** | 15-80 秒 | 4-8 MB | Blender + Python | ✅ 阻塞（Phase 0 gate） |
| **G1 主实验** | 11-22 小时 | 10-21 GB | Blender 批量渲染 | ✅ 阻塞（主线必做） |
| **G3 增益验证** | 33-66 小时 | 32-64 GB | 同上 | ✅ 阻塞（优先主线） |
| **G5 完整主线** | 55-111 小时 | 53-106 GB | 同上 | ✅ 主论文候选 |
| **roll sensitivity 探针** | 0.9-1.75 小时 | 0.8-1.7 GB | 需 G1/G3/G5 结果 | ✅ 主线必做（答辩防线） |
| **训练 OCS-only** | 0.8-1.7 小时 | ~1 GB | GPU | ⬜ 不阻塞前向模型验证 |
| **训练 image-only** | 8-50 小时 | ~5 GB | GPU | ⬜ 不阻塞前向模型验证 |
| **训练 fusion** | 12-67 小时 | ~5 GB | GPU | ⬜ 不阻塞前向模型验证 |
| **指标计算** | ~35 分钟 | ~100 MB | CPU/GPU | ⬜ 训练后执行 |

**关键路径总耗时**（串行，按 G5 + roll sensitivity）：
- 数据生成：55-111 小时
- roll sensitivity：0.9-1.75 小时
- 训练（三模型串行）：21-119 小时
- **总计：77-232 小时（3.2-9.7 天）**

**若 8 核并行渲染，数据生成可加速至 7-14 小时（G5）。**


## 7. G1/G3/G5 与 roll sensitivity 扩展估计

### 7.1 几何层级定义明确化

**重要边界说明**（依据路线一冻结文件 §7 和 R02 执行规划）：

#### 7.1.1 G1 = single-geometry 下界

**定义**：
- G1 使用单一观测几何（phase63 baseline）
- 目的：提供 OCS 可观测性的下界（worst-case baseline）
- 作用：排除多几何增益的干扰，纯粹评估单几何条件下姿态信息可提取性
- 对比对象：与 image-only 在同一几何下比较，回答"单几何条件下 OCS 是否携带姿态信息"

**不是**：
- 不是"最少工作量"或"偷懒"
- 不是"多几何太贵所以只做单几何"

**写作表述**（答辩/论文）：
```text
G1 single-geometry baseline serves as the lower bound of OCS observability.
We deliberately use a single fixed geometry (phase63) to isolate the 
information content of the photometric channel from multi-geometry gains, 
ensuring that any observed attitude discriminability is intrinsic to the 
OCS signature rather than relying on geometric diversity.
```

#### 7.1.2 G3 = 少量代表几何增益验证

**定义**：
- G3 使用 3 个代表性 phase 角度（如 phase45/63/90）
- 目的：验证少量多几何是否能显著提升 OCS 可观测性、降低混淆、提高置信
- 作用：回答"从 G1 到 G3，增益有多大？"

**选择依据**：
- phase45：前向散射偏移（forward-scattering bias）
- phase63：历史基线（backscatter 区域）
- phase90：侧向散射（side-scattering，specular 与 diffuse 竞争区）

**若 G3 增益明显**：
- G3 作为资源可控的多几何候选，可进入主论文主线
- G5 作为更充分的几何覆盖上探

**若 G3 增益不明显**：
- 说明 OCS 多观测增益有限，或需要更大几何跨度（如 phase24 到 phase120）
- G5 成为必要性更强的主线候选

#### 7.1.3 G5 = 完整主线候选

**定义**：
- G5 使用 5 个历史完整几何（phase24/45/63/90/120）
- 目的：覆盖前向、侧向、后向散射的完整 phase 范围
- 作用：提供充分的几何覆盖，作为主论文结果的完整候选

**优势**：
- 覆盖前向散射（phase24/45）、侧向（phase90）、后向（phase63/120）
- 能够评估不同 phase 区域对姿态可观测性的贡献差异
- 为后续观测规划提供"哪些几何值得观测"的依据

**风险**：
- 若 G5 相比 G3 增益有限，可能被审稿人质疑"为何不用更多几何"
- 需要在论文中解释"G5 覆盖主要 BRDF 散射模式，进一步增密几何的边际收益递减"

#### 7.1.4 G9/G12 = 暂作扩展，不作为默认主线

**定义**：
- G9：更密 phase 集合（如 phase 20°-140°，间隔 15°）
- G12：全 phase 覆盖（间隔 10°-15°）

**为何不作为默认主线**：
- 资源规模增大（G9: 100-200 小时，G12: 133-266 小时）
- 边际信息增益递减：phase 角度从 5 个增加到 12 个，增益不一定线性
- 路线一 C 的重点是"证明 OCS 多观测向量携带姿态信息"，而不是"找到最优几何组合"
- 最优几何组合应由三轴小项目的 geometry utility score 回答

**进入条件**：
- G5 结果显示几何增益仍未饱和，需要更密集采样
- 审稿人或答辩委员明确要求更多几何覆盖
- 后续工作扩展（如博士论文、独立项目）

### 7.2 "多几何"的两种含义澄清

**重要警惕**（依据路线一冻结文件 §7 和专家质疑）：

路线一 C 的"多几何"容易被误解为"多台设备同步多角度观测同一目标"。必须在论文中显式区分：

#### 7.2.1 不主张的多几何（多设备同步观测）

```text
不现实的设定：多台望远镜在不同地理位置同步观测同一 GEO 目标，
协调观测时间窗口，获得同一时刻的多角度光度测量。
```

**为何不现实**：
- GEO 目标观测窗口受地理位置、天气、轨道几何约束
- 多站协调观测成本高、调度复杂
- 同步性难以保证（姿态可能在短时间内变化）

**路线一 C 不依赖这种设定。**

#### 7.2.2 主张的多几何（单目标多帧自然几何变化）

```text
现实的结构：同一目标在多次观测中，因 sun/view 相对几何的自然变化，
形成多个不同 phase 角度的光度测量。
```

**为何现实**：
- GEO 目标被持续监测时，sun/view 几何随时间自然变化（地球自转、轨道运动）
- 单站多夜观测即可积累不同几何的光度数据
- 这是 GEO 监测数据的固有结构，不需要专门多设备协调

**路线一 C 的多几何处理**：
1. **路线一 C 主实验**：先用 G1/G3/G5 受控几何进行 benchmark，控制变量，研究"多几何光度向量"的姿态信息结构
2. **路线二 GEO 真实光度锚点**：后续用 GEO 真实多帧数据验证"单目标多帧自然几何变化"确实存在，且 phase 覆盖与路线一 C 的 G5 几何范围可比
3. **论文表述**：明确写为"multi-observation photometric vector across varying sun/view geometries"，而不是"multi-station simultaneous observation"

**建议论文中加入的澄清句**：
```text
We emphasize that the multi-geometry OCS vector does not require simultaneous 
multi-station observation. Instead, it naturally arises from the temporal 
variation of sun/view geometry during repeated observations of the same target 
over multiple nights. Our controlled G1/G3/G5 benchmarks simulate this structure, 
and Route 2 (GEO photometric anchoring) will validate its realism using 
single-station multi-epoch real data.
```

### 7.3 roll sensitivity 是主线必做，不是三轴小项目替代品

**关键判断**（依据路线一冻结文件 §8）：

#### 7.3.1 roll sensitivity 的作用

**不是**：
- 不是"因为资源不够所以做一个小实验代替 full 3-DOF"
- 不是"可选的补充实验"
- 不是三轴小项目的简化版

**是**：
- 是硕士论文答辩的承重墙：答辩委员几乎必问"roll 固定为 0，roll≠0 时你的结论会不会被推翻"
- 是高刊 rebuttal 的弹药：审稿人若质疑 fixed-roll，可用 roll sensitivity 数据反驳"并非忽略 roll，而是量化了 roll 边界"
- 是后续路线（三轴小项目、路线三暗室）的定量依据

#### 7.3.2 roll sensitivity 回答三个问题

1. **signature 漂移幅度**：
   - OCS 向量在 roll ∈ {0°, ±5°, ±10°, ±15°} 时的变化量（如欧氏距离、cosine similarity）
   - 图像在 roll 扰动下的 SSIM、PSNR 变化
   - 回答："OCS/image signature 对 roll 的敏感度有多大"

2. **混淆结构稳定性**：
   - fixed-roll 条件下的高混淆姿态对（yaw1/pitch1 与 yaw2/pitch2 的 OCS 相似或图像相似）
   - 在 roll≠0 时，这些混淆对是否仍然混淆？还是 roll 扰动后可分性提升？
   - 回答："fixed-roll 下的混淆结论是否被 roll 推翻"

3. **最亮点迁移**：
   - fixed-roll 条件下的 top-10 最亮姿态
   - 在 roll≠0 时，这些姿态是否仍在 top-10？还是最亮点迁移到其他 yaw/pitch 组合？
   - 回答："fixed-roll 下的最亮构型是否稳定"

#### 7.3.3 roll sensitivity 与三轴小项目的边界

| 对比项 | roll sensitivity（路线一 C） | 三轴小项目 |
|---|---|---|
| **定位** | fixed-roll 结论的边界量化 | 真正的 roll-aware 三轴搜索 |
| **采样策略** | 代表性姿态子集（~30） + roll 扰动（7 值） | 种子点 + 稀疏采样 + 局部加密 |
| **目标** | 证明 fixed-roll 结论是否被 roll 推翻 | 寻找三轴最亮、高信息、低信息构型 |
| **样本规模** | 210（单几何） / 630（G3） | 数千到数万（智能采样，不是全量） |
| **执行时机** | 路线一 C 主实验后 | 路线一 C 完成后 |
| **输出** | 漂移幅度、稳定性判断、最亮点迁移 | 最亮构型、高信息构型、观测规划图 |
| **能否相互替代** | ❌ 不能 | ❌ 不能 |

**关键结论**：
- roll sensitivity 只负责"证明 fixed-roll 结论的稳定性边界"
- 三轴小项目负责"在三轴空间中搜索最优构型和观测规划"
- 二者互补，不能相互替代
- 后续 Claude 提示词不能把二者混写

### 7.4 full 3-DOF 只进入三轴小项目，不进入路线一 C 主实验

**明确区分**：

| 实验类型 | 路线一 C | 三轴小项目 |
|---|---|---|
| **主实验** | fixed-roll yaw-pitch 2664 姿态 | 智能三轴搜索（种子点 + 加密） |
| **探针实验** | roll sensitivity ~30 姿态 × 7 roll | 无（本身就是三轴） |
| **full 3-DOF 全量** | ❌ 不进入 | ⚠️ 只在必要时考虑 |

**三轴小项目也不一定做 full 3-DOF 全量**：
- 三轴小项目的重点是"智能搜索"，而不是"全空间覆盖"
- 采用策略：从 fixed-roll 高亮/高混淆姿态出发，局部扫描 roll；稀疏三轴候选池；候选区域加密
- 只有在"稀疏采样无法找到稳定最亮构型"时，才考虑局部加密到接近 full 3-DOF 密度
- 全局 full 3-DOF（191,808 姿态）只在"必须证明全空间最亮"或"后续博士论文"时考虑


## 8. 进入实际执行前的确认清单

以下清单列出了从"smoke test 设计通过"到"实际执行 smoke test"之间必须由作者/Codex 确认的事项。**未经确认，不得进入实际执行。**

### 8.1 代码区与输出区创建确认

- [ ] **Q1. v0.4 代码根目录创建**：确认创建 `06_v0.4_code/` 或其他路径，并确认目录结构（见 1C-C01-R1 §6.1）
- [ ] **Q2. v0.4 输出根目录创建**：确认创建 `07_v0.4_results/` 或其他路径，并确认子目录结构
- [ ] **Q3. 历史快照迁移策略**：确认哪些模块直接复用、哪些需改造、哪些从头编写（见 1C-C01-R1 §3 三分表）

### 8.2 BRDF 主锚点实现确认

- [ ] **Q4. 五参数冯模型实现**：确认五参数冯 BRDF 模块是否已实现，若未实现，是否先实现后再执行 smoke test，还是暂用 GGX 临时替代（但必须标注为非主线）
- [ ] **Q5. 材料参数对齐**：确认书中材料参数表的具体来源（页码/表格编号），或提供具体参数值（rho_d, rho_s, n for each part）
- [ ] **Q6. GGX 对照分支**：确认 GGX 对照分支的代码组织方式（独立文件还是同一文件中的函数）

### 8.3 sun visibility 实现确认

- [ ] **Q7. depth_epsilon_m 初始值**：确认初始值 0.05m，或提供其他初始值
- [ ] **Q8. sun-view 渲染脚本**：确认是否有已有参考代码，或需要从头编写
- [ ] **Q9. reprojection 算法验证顺序**：确认是否先做 depth round-trip（3 已知点），再做完整 reprojection

### 8.4 数据流程确认

- [ ] **Q10. corpus-level I_scale 两阶段流程**：确认单姿态 smoke test 是否暂用 per-frame normalization（标注为临时），或实现两阶段流程框架
- [ ] **Q11. manifest 生成时机**：确认是边生成边写入，还是全部姿态完成后统一生成
- [ ] **Q12. 历史数据保留策略**：确认项目根目录下 `ocs_project/` 和 `结果/` 是否保留、移动到归档区或清理

### 8.5 Phase 0 gate 确认

- [ ] **Q13. 20 姿态 shadow validation 姿态选择**：确认 20 个 yaw/pitch 组合清单，或由 1C-C03 任务提出候选
- [ ] **Q14. depth round-trip 的 3 已知点选择**：确认 3 个点的选择方式（手动标注 STL 顶点，或程序自动选择模型中心+边界点）
- [ ] **Q15. smoke test 通过后的后续步骤**：确认是立即进入全量生成，还是先完成其他 P1 验证任务

### 8.6 目标模型与几何确认

- [ ] **Q16. 目标模型 STL 文件路径**：提供"真实模型"三部件（jinshuzhuti + taiyangnengban + yinshenban）的具体文件路径
- [ ] **Q17. phase63 几何定义**：提供 phase63 的 sun_vector 和 det_vector 具体数值（归一化），或指向包含该定义的配置文件
- [ ] **Q18. STL 部件分组**：确认 STL 文件中三部件的 IndexOB 对应关系（如主体=1, 太阳能板=2, 遮阳板=3）

### 8.7 环境准备确认

- [ ] **Q19. Blender 版本**：确认使用的 Blender 版本（如 3.6 LTS / 4.0），确保支持 Position AOV 和所需渲染功能
- [ ] **Q20. Python 环境**：确认 Python 版本（建议 3.10+），创建 conda 环境或 venv
- [ ] **Q21. 依赖库安装**：确认 NumPy, OpenEXR (Python binding), PIL/Pillow, matplotlib 等依赖库版本
- [ ] **Q22. 硬件配置记录**：记录 CPU 核心数、GPU 型号、内存、存储，用于资源估计校准

### 8.8 路线一 C 与三轴小项目接口确认

- [ ] **Q23. roll sensitivity 实现时机**：确认是在路线一 C 主实验（G1/G3/G5）完成后规划，还是在代码框架设计时预留三轴扩展接口
- [ ] **Q24. 三轴小项目代码复用**：确认三轴小项目是否会复用路线一 C 的代码框架，是否需要在当前代码设计中考虑三轴扩展性

### 8.9 执行权限与文件创建确认

- [ ] **Q25. 文件创建范围**：明确本次 smoke test 执行允许创建哪些目录和文件，是否允许修改历史快照代码
- [ ] **Q26. 失败时回滚策略**：确认若 smoke test 失败，是否保留中间产物用于诊断，还是清理后重新执行


## 9. 是否可以进入 1C-C03 的判定

### 9.1 1C-C03 任务定义

**1C-C03 任务**：设计前向模型几何/可见性校验任务

**包含内容**：
1. depth round-trip 校验设计（3 已知点）
2. Position / WorldCoord 一致性校验设计
3. sun-view depth 物理合理性校验设计
4. V_sun_macro reprojection 对齐校验设计
5. 20 姿态 shadow validation 设计
6. visibility / mask / rendered image 对齐校验设计
7. manifest 字段可追踪性校验设计

### 9.2 进入 1C-C03 的前提条件

**可以进入 1C-C03，当且仅当：**

1. ✅ **1C-C01-R1 已完成**：代码入口盘点清单已明确（已完成）
2. ✅ **1C-C02 已完成**：本 smoke test 与资源估计方案已完成（当前文件）
3. ✅ **Codex 审阅本文件通过**：确认设计合理，无重大遗漏或红线违反
4. ✅ **1C-C03 只要求"设计校验任务"**：不要求实际执行校验

**判定：可以进入 1C-C03，因为：**
- 1C-C03 同样属于设计阶段，不涉及代码执行或文件创建
- smoke test 的概念调用链（本文 §3）已明确每步输出，1C-C03 可基于此设计校验任务
- 1C-C03 输出后，仍需 Codex 审阅，审阅通过后才能与 §8 确认清单一起进入实际执行

### 9.3 不能进入 1C-C03 的条件

**若要求"执行校验任务"，则必须先完成：**

1. ⬜ §8 确认清单（Q1-Q26）全部确认通过
2. ⬜ 代码区和输出区创建完成
3. ⬜ 关键新模块实现完成（sun-view depth 渲染、reprojection、五参数冯 BRDF）
4. ⬜ 单姿态 smoke test 实际执行并通过
5. ⬜ 才能进入校验任务的实际执行

### 9.4 1C-C03 后的路径

**1C-C03 设计完成并 Codex 审阅通过后：**

**路径 A（推荐）**：
1. 作者/Codex 确认 §8 确认清单（Q1-Q26）
2. 创建代码区和输出区
3. 实现关键新模块
4. 实际执行单姿态 smoke test（1C-C02 方案）
5. 实际执行几何/可见性校验（1C-C03 方案）
6. 两者都通过后，进入 Phase 1（3 姿态扩展验证）或 G1 主实验规划

**路径 B（若资源或时间受限）**：
1. 只执行 smoke test，跳过部分校验任务
2. 风险：几何/可见性基础可能有结构性错误，导致后续全量数据不可信
3. 不推荐，除非时间极度紧张

**路径 C（若发现设计有重大遗漏）**：
1. Codex 审阅指出 1C-C02 或 1C-C03 设计有问题
2. 返回修正设计，重新提交审阅
3. 审阅通过后再进入执行

### 9.5 最终判定

**✅ 可以进入 1C-C03 设计阶段。**

**前提**：
- 本 1C-C02 方案已完成
- Codex 审阅本方案并确认设计合理
- 1C-C03 只要求"设计校验任务"，不要求实际执行

**后续建议**：
1. 将本文件提交 Codex 审阅
2. Codex 审阅通过后，进入 1C-C03 任务，生成"前向模型几何与可见性校验方案"
3. 1C-C03 完成并审阅通过后，再启动 §8 确认清单的逐项确认
4. 全部确认完成后，进入 Phase 0 gate 实际执行阶段


---

## 附录：本方案生成依据与参考文件

**已读取文件**：
1. `CLAUDE.md`
2. `04_四路线分工区/01_路线一_fixed-roll纯仿真主干/00_路线冻结文件区/01_路线一_fixed-roll大论文主线与发刊答辩定位.md`
3. `04_四路线分工区/00_总览与裁决/04_Codex审阅/R02_Codex_各路线具体执行规划草案.md`
4. `04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/01_路线一C_代码入口盘点_smoke_test与几何校验_Claude提示词.md`
5. `04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/02b_路线一C_代码入口盘点清单_R1修正版_Claude输出.md`

**主要依据**：
- 13 号规范（v0.4 前向模型冻结规范）
- 14 号规范（v0.4 数据与 manifest 字段规范）
- 路线一冻结文件（fixed-roll 定位、roll sensitivity、G1/G3/G5 分层、答辩防线）
- R02 执行规划（1C-C01/C02/C03 任务边界、Phase 0 gate 通过标准）
- 1C-C01-R1 修正版（代码入口三分表、待确认问题清单、拟议操作清单）

**红线遵守确认**：
- ✅ 本轮只做设计，不执行
- ✅ 不创建任何目录或文件
- ✅ 不复制历史快照代码
- ✅ 不修改任何代码、配置、总览、冻结文件或 CLAUDE.md
- ✅ 不实际运行 Blender
- ✅ 不进入全量生成或训练
- ✅ 所有拟议路径均标注为 `[拟议路径，待作者/Codex确认]`
- ✅ 所有历史快照均标注为 `[历史快照参考，不直接运行]`
- ✅ 不把 smoke test 写成实验结果
- ✅ 不把路线一 C 写成真实未知目标完整姿态反演系统
- ✅ 不把 GGX 写成唯一主线可信来源
- ✅ 不跳过 roll sensitivity

---

**本文件完成。等待 Codex 审阅后，可进入 1C-C03 设计阶段。**

