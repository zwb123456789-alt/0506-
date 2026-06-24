# 1C-E01 历史快照代码真实内容与依赖核对报告（Claude 执行输出）

生成时间：2026-06-22
任务编号：1C-E01
执行者：Claude

---

## 0. 上下文恢复确认

已完成轻量上下文恢复，确认以下要点：

1. **当前科学主线**：model-known 条件下，独立 OCS 光度通道与图像成像通道共享同一物理前向模型时，跨几何 OCS 多观测光度向量与图像通道对姿态信息的可观测性、互补性和置信一致性研究。

2. **路线一 C 定位**：保留 v0.4 pixel-level OCS-image 同源前向架构；以五参数冯 / Phong-like BRDF 与书中典型材料参数作为主 BRDF 锚点；以 GGX / Cook-Torrance 作为 BRDF mismatch、现代 PBR 对照和鲁棒性分支；主实验仍为 fixed-roll yaw-pitch controlled benchmark。

3. **当前阶段**：路线一 C 代码入口盘点阶段，Phase 0 门控验证前的准备工作。

4. **本轮禁止事项**：不修改任何代码、不创建任何目录、不运行任何程序、不设计 smoke test、不裁决 BRDF 主线、不放行下一阶段。

---

## 1. 执行范围与禁止事项确认

本轮任务严格限定为**历史快照代码真实内容核对**，具体范围：

**允许做的**：
- 读取历史快照代码文件
- 核对文件存在性、大小、行数
- 列出关键函数、变量、类定义
- 记录依赖库清单
- 标注与 Codex 设计的差异
- 列出禁止迁移清单和待审阅问题

**严格禁止**：
- ❌ 不创建 `06_v0.4_code/` 或 `07_v0.4_results/`
- ❌ 不复制任何历史快照代码
- ❌ 不修改任何代码、配置、总览、冻结文件或 CLAUDE.md
- ❌ 不运行 Blender、不运行训练、不运行任何测试
- ❌ 不设计 smoke test 或下一步执行方案
- ❌ 不裁决 BRDF 主线（五参数冯 vs GGX）
- ❌ 不把历史快照写成当前正式可运行入口
- ❌ 所有判断只能写成"核对结果"，不能写"建议下一步怎么设计"

---

## 2. 文件存在性总表

| 文件路径 | 存在性 | 大小/行数 | 角色判定 |
|---|---|---|---|
| `01_code/config.py` | ✅ 存在 | 182 行 | 可复用参考（需修改） |
| `01_code/materials.py` | ✅ 存在 | 67 行 | 可复用参考 |
| `01_code/geometry.py` | ✅ 存在 | 159 行 | 可复用参考 |
| `01_code/ocs_core.py` | ✅ 存在 | 263 行 | 历史禁用（face-center） |
| `01_code/main_run.py` | ❌ 不存在 | - | - |
| `01_code/run_multi_geom.py` | ✅ 存在 | 309 行 | 可复用参考（需大幅改造） |
| `02_blender/render_geometry_passes.py` | ✅ 存在 | 529 行 | 可复用参考（需升级） |
| `02_blender/brdf_postprocess.py` | ✅ 存在 | 480 行 | 可复用参考（需大幅修改） |
| `02_blender/render_batch.py` | ❌ 不存在 | - | - |
| `03_inversion/inv_common.py` | ✅ 存在 | 501 行 | 可复用参考（需升级） |
| `03_inversion/train_mlp.py` | ✅ 存在 | 500 行 | 反演参考（需升级） |
| `03_inversion/train_cnn.py` | ✅ 存在 | 464 行 | 反演参考（需升级） |
| `03_inversion/train_fusion.py` | ✅ 存在 | 613 行 | 反演参考（需升级） |

**说明**：
- `main_run.py` 和 `render_batch.py` 在列表中但实际不存在于快照目录
- 所有存在的文件均为 Python `.py` 格式
- 总共核对了 11 个实际存在的代码文件

---

## 3. 逐文件核对结果

### A. config.py

**关键变量表**：

| 变量名 | 值/类型 | 与路线一 C 设计差异 |
|---|---|---|
| `NUM_YAW` | 73 | ❌ **不一致**：包含 360° 重复，路线一 C 要求 72（不含重复） |
| `NUM_PITCH` | 37 | ✅ 一致：-90° 到 +90°，步长 5° |
| `OBS_GEOMETRIES` | 5 组几何 | ✅ 存在：phase63/phase24/phase45/phase90/phase120 |
| `BRDF_MODEL` | `"ggx"` | ⚠️ **冲突**：默认 GGX，但路线一 C 主线应为 Phong-like |
| `BLENDER_EXE` | 硬编码路径 | ⚠️ 需修改为用户机器实际路径 |
| `PROJECT_ROOT` | `D:\我的文件\研究生学术\光学项目\0506新` | ⚠️ 旧项目根路径 |
| `OUTPUT_DIR` | `结果/模块A_重构` | ⚠️ 旧输出目录，不符合 14 号规范 |
| `UNIT_SCALE` | `1e-3` (mm → m) | ✅ 一致 |
| `EPSILON` | `1.0` mm | ✅ 面元法向偏移 |
| `SUN_VECTOR` | `[1.0, 0.0, 0.3]` | ✅ 存在默认值 |
| `DET_VECTOR` | `[0.5, -1.0, 0.1]` | ✅ 存在默认值 |

**与 Codex 设计不一致之处**：
1. **P0 冲突**：`NUM_YAW = 73` 包含 0° 和 360° 重复，与 13 号规范要求的 72 个唯一姿态不符
2. **P0 冲突**：`BRDF_MODEL = "ggx"` 默认为 GGX，与路线一 C 主线"五参数冯为主锚点、GGX 为对照"不符
3. **P1 需修改**：输出路径指向旧 `结果/模块A_重构/`，不符合 14 号规范的 `v0.4_results/` 或 `07_v0.4_results/`

**可复用程度**：中等，需修改后可用

---

### B. materials.py

**材料参数表**：

| 材料 | Legacy Phong 参数 | GGX 参数 | 来源标注 |
|---|---|---|---|
| `jinshuzhuti` | rho_d=0.20, rho_s=0.60, n=80 | base_color=0.91, metallic=1.0, roughness=0.20, F0=0.91 | 无书中参数对齐证据 |
| `taiyangnengban` | rho_d=0.15, rho_s=0.10, n=20 | base_color=0.15, metallic=0.0, roughness=0.40, ior=1.5 | 无书中参数对齐证据 |
| `yinshenban` | rho_d=0.08, rho_s=0.02, n=10 | base_color=0.08, metallic=0.0, roughness=0.90, ior=1.5 | 无书中参数对齐证据 |

**关键函数**：
- `get_material(part_name, use_ggx=False)` - 根据标志返回 Phong 或 GGX 参数
- `brdf_value(normal, sun_dir, det_dir, mat)` - 仅支持 Legacy Phong 的 BRDF 计算

**核对结果**：
1. **Legacy Phong 参数**：存在且完整，公式为 `f_r = rho_d/π + rho_s·(N·H)^n`
2. **GGX 参数**：存在 `_GGX_DB`，包含 base_color/metallic/roughness/F0/ior
3. **无书中对齐证据**：文件中无任何注释或文档表明这些参数已与书籍知识库材料参数对齐
4. **Phong-like 与 Legacy Phong**：从公式看，Legacy Phong 的 `f_r = rho_d/π + rho_s·(N·H)^n` 很可能就是路线一 C 要求的"五参数冯 / Phong-like"，但需要 Codex 确认是否完全等价

**可复用程度**：较高，材料参数数据库结构完整

**待 Codex 审阅问题**：
- Legacy Phong 公式是否等同于书中的"五参数冯 / Phong-like BRDF"？
- 材料参数是否需要与书籍知识库对齐？如果需要，具体参数值是什么？

---

### C. geometry.py

**关键函数表**：

| 函数名 | 功能 | 依赖库 |
|---|---|---|
| `euler_to_matrix(yaw, pitch, roll)` | 欧拉角转旋转矩阵，Z-Y-X 内旋 | numpy |
| `load_meshes(part_files, accuracy_level)` | STL 加载与抽稀 | trimesh, tqdm |
| `_load_as_mesh(filepath)` | 加载 STL，处理 Scene/Trimesh | trimesh |
| `_simplify_mesh(mesh, target_faces)` | 网格抽稀，兼容多版本 trimesh | trimesh |

**坐标系与旋转顺序核对**：
- **旋转顺序**：`R = Rz @ Ry @ Rx`（Z-Y-X 内旋）
- **与 13 号规范对比**：13 号规范明确为 `R = Rz(yaw) · Ry(pitch) · Rx(roll)`
- **✅ 一致性**：旋转顺序完全一致

**单位转换**：
- STL 文件单位：mm
- 加载后缩放：`sat_root.scale = (UNIT_SCALE, UNIT_SCALE, UNIT_SCALE)`，其中 `UNIT_SCALE = 1e-3`
- 最终单位：m（米）

**依赖库**：
- `numpy`
- `trimesh` - STL 加载、网格操作、simplify
- `tqdm` - 进度条显示

**可复用程度**：高，核心几何加载逻辑可直接复用

---

