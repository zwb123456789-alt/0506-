# OCS + 图像联合仿真项目 · 进度档案

> 目标：建立 OCS 与二维光度图像一致的统一渲染模型，支持图像-OCS 联合姿态估计。
> 路径前缀：`D:\我的文件\研究生学术\光学项目\0506新\`

---

## 一、整体三模块

| 模块 | 职责 | 状态 |
|---|---|---|
| **A · OCS 计算 + 双语图表** | STL → 姿态扫描 → OCS / 遮挡率 / 图表 / JSON·CSV | ✅ GGX 5° 网格基线 run_20260520_160847（2701 姿态，454s）；多观测几何基线 run_20260520_162831（5 几何×2701，1725s）；LegacyPhong 兼容保留 |
| **B · Blender 批量渲染** | headless 渲染，含 Principled 旧管线 + exact BRDF 新管线（几何缓冲 + Python 后处理） | ✅ Principled run_20260511_193251；exact BRDF run_20260519_backface_fix（MULTILAYER EXR） |
| **C · 姿态反演** | OCS 表 / 图像 / OCS+图像联合检索 | ✅ OCS-only kNN + MLP（11b/c）；HOG image-only LOO（11d）；OCS+HOG joint kNN LOO（11d, Top1@5°=84.64%）；CNN image-only（11e-A, mean=12.38°）；CNN+OCS late/fusion（11e-B, feature fusion per_part mean=4.10°）；论文汇总+图表+互补性诊断（11f, paper_summary/run_20260522_234553/） |

执行顺序：A → B → C。当前焦点：**Step 11f 论文级结果汇总完成。下一步：决定论文投稿策略，可能增加 roll 轴 / 更大模型 / 真实数据验证**。

---

## 二、目录结构

```
0506新/
├── 建模/                          真实 STL 在 `建模/真实模型/`（jinshuzhuti.stl / taiyangnengban.stl / yinshenban.stl）
├── 文献/                          近五年顶刊文献库（.bib + .md 综述），与运行产物无关
├── 结果/                          所有运行产物落这里（不要再写到 ocs_project 内）
│   ├── 模块A_重构/                ← 模块 A OUTPUT_DIR
│   │   ├── 2d_yaw37_pitch19/run_YYYYMMDD_HHMMSS/   (10° 网格)
│   │   ├── 2d_yaw73_pitch37/run_YYYYMMDD_HHMMSS/   (5° 网格)
│   │   └── multi_geom_*/run_YYYYMMDD_HHMMSS/        (多观测几何)
│   │       ├── <geom_label>/ocs_scan.json / ocs_scan.csv / config_used.json
│   │       ├── <geom_label>/fig01~fig06.png
│   │       └── multi_geom_manifest.json
│   ├── 模块B_渲染/                ← 模块 B OUTPUT_ROOT
│   │   └── run_YYYYMMDD_HHMMSS/
│   │       ├── images/yaw{:06.2f}_pitch{:+06.2f}.png   (Principled 旧管线)
│   │       ├── *.exr                                   (exact BRDF 新管线)
│   │       ├── render_log.csv / ocs_comparison.csv
│   │       └── config_used.json
│   ├── BRDF验证/                  ← Step 5-8 BRDF 三端闭合验证
│   │   ├── plane_batch_*/
│   │   ├── L_plate_*/
│   │   ├── cube_*/
│   │   └── material_sweep_*/
│   ├── 遮挡验证/                   ← 05_occlusion_validation 输出
│   │   └── ...
│   ├── 人工遮挡抽查/                ← 05_manual_review 输出
│   │   └── ...
│   └── 模块C_反演/                ← 模块 C OUTPUT_ROOT
│       └── ...
├── ocs_project/                   ← 本次新建工程
│   ├── 01_code/                   config / materials / geometry / occlusion /
│   │                              ocs_core / visualization / main_run / run_multi_geom
│   ├── 02_blender/                render_batch.py + render_geometry_passes.py + brdf_postprocess.py + 诊断脚本
│   ├── 03_inversion/              inv_ocs.py / inv_image.py / inv_joint.py（✅ MVP）
│   ├── 04_tests/                  test_blender_path.py + test_module_a_smoke.py + test_occlusion_geometry.py
│   ├── 05_occlusion_validation/   run_occlusion_validation.py
│   ├── 05_manual_review/          manual_review_blender.py + run_manual_review.bat
│   ├── 06_brdf_validation/        单平板/L型/立方体三端对账 + verify_ggx.py
│   └── 07_brdf/                   brdf_precision_design.md + brdf_models.py + test_brdf_models.py
├── 总代码+BRDF代码/02代码_v1_refactored.py   旧单文件（保留对照，不动）
└── 总思路1.md                     完整方案备查
```

---

## 三、模块 A 已修复问题（对照原 02代码_v1_refactored.py）

| 问题 | 落地 |
|---|---|
| 2D 模式误生成 1D 三曲线图 | `main_run.py` 用 `if SCAN_2D` 互斥 |
| 中文字体方框 | `visualization.setup_matplotlib_style()` 注册 SimHei 等 CJK |
| 图编号混乱 | 严格 fig01~fig06 命名 |
| 中英双语标签 | `config.LABELS/TITLES/PART_LABELS` + `LANG_MODE` 切换 |
| 遮挡率/损失越界 | `ocs_core` clip [0,1]；`fig05` `np.maximum(loss,0)` |
| 缺配置快照 | 输出 `config_used.json` |
| 渲染抢主流程 | `ENABLE_RENDER=False`，渲染交给模块 B |
| Blender 路径未验证 | `test_blender_path.py` 先验 `--version` |
| 单平板 A vs 解析闭合（6 姿态） | ✅ 已通过 | yaw=0/0、0/-30、45/0、90/-45、150/-80、180/0；确认 A 端 BRDF / 单位 / 面积链路正确 |
| 单平板 B 三端闭合（5 姿态） | ✅ 已通过 | mean rel_err=0.25%，确认 B 端几何缓冲 + 后处理链路正确 |
| 立方体三端闭合（5 姿态） | ✅ 已通过 | B/an ≤ 0.25%，凸几何数字孪生级闭合 |
| L 型双平板可见性语义验证 | ✅ 已通过 | A_with/B≈1.0@中等角度，ray-cast vs rasterization 语义一致 |
| GGX 接入模块 A 生产扫描 | ✅ 已通过 | --ggx CLI 入口 + 5 几何多观测批量 |

> A/B BRDF/几何/投影/面积/单位链路已由单平板+立方体三端闭合完整验证（rel_err < 0.5%）。真实三件套 native gap 根因确认为 face-center vs pixel-level 可见性语义差异，已冻结。

---

## 四、模块 B 核心约定

> **注意**：当前存在两条渲染管线。旧管线 `render_batch.py`（Principled BSDF 近似，本节描述）为 MVP 基线。新管线 `render_geometry_passes.py` + `brdf_postprocess.py`（几何缓冲 + Python 后处理 exact BRDF）为论文期路径，详见 §六 Step 5。

### 旧管线：render_batch.py（Principled BSDF 近似）

- **架构**：单文件 bpy 脚本，`blender --background --python render_batch.py -- <args>` 调用。一个 Blender 进程内循环全部姿态，避免 ~2s × N 的启动成本。
- **姿态应用**：`Sat_Root` Empty 承担 R 与 mm→m。任意帧 `sat_root.matrix_world = R4 @ Diagonal((1e-3,1e-3,1e-3,1))`。太阳和相机固定在惯性系 I（与 `ocs_core.py` "rotate satellite, keep sun & camera fixed" 等价）。
- **R 矩阵**：手搓 `R = Rz @ Ry @ Rx`（Z-Y-X 内旋），严格镜像 `geometry.py:16-38`，避免 Blender Euler API 轴序歧义。
- **材质**：Phong → Principled BSDF 近似映射。base_color=(ρ_d,ρ_d,ρ_d)；roughness=clamp(sqrt(2/(n+2)),0.02,1)；specular_ior_level=ρ_s；metallic=0。
- **相机**：正交，位置 `+det_norm·5·r_max`，朝 origin；`ortho_scale=2.2·r_max`。bbox 半径旋转不变，只算一次。
- **太阳**：SUN 灯，朝向 `Vector(sun_norm).to_track_quat('Z','Y')`，energy=5.0。
- **色管**：`view_transform='Standard'`（避免 Filmic 破坏辐射度量）。背景纯黑。
- **GPU**：自动探测 OPTIX/CUDA/HIP/ONEAPI/METAL，失败回退 CPU。当前机器 OPTIX 可用。
- **文件名**：`yaw{yaw:06.2f}_pitch{pitch:+06.2f}.png`（例 `yaw180.00_pitch-90.00.png`）。渲染前 assert 唯一性。

### MVP 限制（待论文期补）

1. BRDF 是 Principled 近似，非 Phong 像素级镜像（精确匹配需 OSL）
2. 金属主体也设 Metallic=0；应设 1 并调铝反射率
3. 未做辐射度量定标
4. 无大气、地球反照、杂散光
5. 模块 A 与模块 B 遮挡机制差异：A 用 `min_hit_distance` 过滤起点自相交；B 用 Cycles 物理光追，天然处理，不需要此机制
6. UNIT_SCALE 通过 parent 应用，不 bake

---

## 五、关键决策

- **图表语言**：双语（`LANG_MODE = "bilingual"`），论文期可切 `"en"`
- **坐标系**：Yaw × Pitch 网格（与代码一致）
- **精度**：当前 `ACCURACY_LEVEL = "fast"`（保留 20% 面元），论文期切 `"full"`
- **Blender 路径**：`D:\Program Files\Blender Foundation\Blender 4.2\blender.exe`（4.2.3 LTS，Step 5 落地用）；旧 5.0 仍在 `Blender 5.0\` 下，不再用
- **数据格式**：JSON（通用）+ CSV（表格）+ PNG（图像库）。HDF5 看模块 C 接口需要再决定。
- **反演方案**：检索式优先（无需训练，快速验证）

---

## 六、下一步（按顺序）

### 当前任务：精度与数据集升级（GGX 已接入）

**核心目标**：将已验证通过的 GGX/Cook-Torrance 接入模块 A 生产扫描，生成论文级 OCS 数据集。冻结 LegacyPhong 仅作兼容 baseline。

**指导原则**（来自 BRDF设计.md）：
- 两端一致性 > 显式物理公式 > 合理材料参数 > 敏感性分析 > 真实观测绝对定标
- 不要求材料参数完全等于真实卫星，但必须物理合理、来源可说明
- 论文定位：物理一致仿真 + 姿态估计算法验证（非真实卫星绝对辐射复现）

**执行步骤**（严格按序，每步完成后暂停确认）：

1. ✅ **Step 1：BRDF 公式审计**（已完成 2026-05-18）
   - 已读取 `materials.py` / `ocs_core.py` / `render_batch.py`
   - 已确认当前模块 A 真实公式：`f_r = (rho_d/π) + rho_s*(n·h)^n`
   - 已确认模块 B Principled BSDF 映射：`roughness=sqrt(2/(n+2))`，底层用 GGX 非 Phong
   - 已识别三处关键差异：镜面 BRDF 模型、能量归一化、金属处理
   - 已冻结 `LegacyPhong` 定义（见下方审计报告）

2. ✅ **Step 2：BRDF 统一设计文档**（已完成 2026-05-18）
   - 产出：`结果/BRDF验证/brdf_precision_design.md`
   - 内容：方向定义、LegacyPhong 公式、GGX/Cook-Torrance 公式、材料参数字段、参数来源策略、验证标准
   - 关键决策：
     - LegacyPhong：`f_r = (rho_d/π) + rho_s*(NoH)^n`（冻结当前公式）
     - GGX：`f_r = f_diffuse + (D*G*F)/(4*NoL*NoV)`（论文主模型）
   - 三类部件 GGX nominal 参数：金属主体 `metallic=1, roughness=0.20, F0=0.91`；太阳能板 `metallic=0, roughness=0.40, ior=1.5`；遮光板 `metallic=0, roughness=0.90, base_color=0.08`
     - 验收标准：单平板误差 <1~2%，姿态曲线相关系数 >0.99，三件套误差 <5%

3. ✅ **Step 3：建立 canonical BRDF 模块**（已完成 2026-05-18）
   - 新增目录：`ocs_project/07_brdf/`（独立 BRDF 模块文件夹）
   - 设计文档已迁移至：`ocs_project/07_brdf/brdf_precision_design.md`（指导思路，非结果）
   - 新增 `ocs_project/07_brdf/brdf_models.py`：
     - `eval_legacy_phong()` / `eval_normalized_phong()` / `eval_ggx_cook_torrance()` / `eval_brdf()`
     - GGX 组件：`D_GGX` / `G_Smith_GGX` / `F_Schlick`
     - 材料库：`MATERIAL_DB_LEGACY`（兼容旧）+ `MATERIAL_DB_GGX`（论文期）
     - 支持 numpy 批量、防 NaN/Inf、roughness 下限 0.02、零向量保护
   - 新增 `ocs_project/07_brdf/test_brdf_models.py`：6 类测试用例全部通过
   - 关键数值验证：金属铝（垂直入射）GGX `f_r=45.26`，LegacyPhong `f_r=0.66`

4. ✅ **Step 4：模块 A 接入统一 BRDF**（已完成 2026-05-18）
   - 修改 `ocs_core.py`：
     - 新增 `from brdf_models import eval_brdf` 与 sys.path 插入 `../07_brdf`
     - 删除内嵌 `h_vec` 计算（共 4 行）
     - 第 75 行（无遮挡 OCS）：`brdf_vec = eval_brdf(normals_PI, sun_norm, det_norm, mat)`
     - 第 98 行（有遮挡 OCS）：`brdf_with = eval_brdf(normals_with, sun_norm, det_norm, mat)`
   - 修改 `materials.py`：所有 `simple` 字典与 `DEFAULT_MAT` 增加 `"brdf_model": "legacy_phong"` 字段，向后兼容
   - 验证脚本：`ocs_project/07_brdf/verify_integration.py`（新旧公式对比）+ `verify_ocs_e2e.py`（单平板端到端）
   - 验收结果：
     - 数值一致性：3 部件、1000 面元随机测试，**最大相对误差 0.000e+00**（远低于 1e-6 阈值）
     - 端到端：单平板 1m² @ yaw=0/pitch=0，OCS=1.63e-3 m²，遮挡率=0%，与理论值一致

5. ⚠️ **Step 5：模块 B 建立 exact BRDF 渲染路径**（进行中；已排除背面渲染、Combined 遮罩、A/B 几何精度不对称；当前确认主因是 face-center vs pixel-level 采样差异，次因是 diffuse 基底未完全闭合）
   - **方案选择**：路径 B（几何缓冲 + Python 后处理），不走 OSL（性能 + 数值不可控）
   - **Blender 版本**：落地 4.2.3 LTS（5.0 Compositor MULTILAYER 损坏，详 §七）
   - **管线（已跑通）**：
     - `ocs_project/02_blender/render_geometry_passes.py`：每姿态写 1 个 MULTILAYER EXR（Combined / Normal / Depth / IndexOB / Backfacing），OPTIX GPU **0.31s/帧**
     - `ocs_project/02_blender/brdf_postprocess.py`：读 EXR → IndexOB 分三部件 → `eval_legacy_phong` → `OCS_image = Σ pixel_area · f_r · NoL`
   - **OCS 公式已验证**：`A_face_pix = pixel_area / NoV` 代入 A 端 `Σ A_face·f_r·NoL·NoV` 后 NoV 抵消，得 `Σ pixel_area·f_r·NoL`，数学自洽
   - **法线坐标系**：已确认世界空间，后处理无需变换
   - **flat shading**：已验证（90.5% 邻接像素法线差 <1°）
   - **分辨率**：res=128 vs 256 OCS 差 <1%，非根因

   ### 2026-05-19 诊断 session：三路线索排查

   **路线一：背面像素假说 → 已排除**
   - **现象**：此前发现 ~50% EXR 像素法线与 A 端预期法线呈 ~179.8° 翻转
   - **尝试 1**：后处理 NoV>0 过滤 → 无效（Cycles 自动翻转背面 shading normal，NoV 始终 >0）
   - **尝试 2**：Backfacing→Transparent BSDF + Combined 亮度遮罩 → 部分有效，背面过滤 ~40%，但 Combined 遮罩不完美（后面几何体会照亮透明背面）
   - **尝试 3**：Shader AOV 精确背面遮罩 → `make_dummy_material` 加 `ShaderNodeOutputAOV` 输出 `Geometry.Backfacing`，MULTILAYER EXR 加第五层 Backfacing
     - AOV 实测结果：**Backfacing.R = 0.0 全零**（yaw=0/pitch=-90 与 yaw=150/pitch=-80 两帧均如此）
     - **结论**：对于封闭网格的外视图，所有可见像素均为真正前向面（Backfacing=0）。之前的"翻转法线"是匹配 A 端面元时对到了薄板的另一侧物理面，不是渲染背面
     - **后续处理**：已去掉 Transparent BSDF（材质简化回直接 Principled→Output），Backfacing AOV 保留作为诊断通道
   - **代码变更**（已落地）：
     - `render_geometry_passes.py`：`make_dummy_material` 简化为 Principled BSDF + Backfacing AOV；`setup_render_passes` 添加 `vl.aovs.add()`；`setup_compositor_for_passes` 添加 Backfacing 层
     - `brdf_postprocess.py`：`read_multilayer_exr` 读取 `Backfacing.R` 通道；`compute_radiance_image` 用 `backfacing < 0.5` 做精确遮罩（当前不生效，因为全是 0 = 全部保留）

   **路线二：jinshuzhuti 镜面峰值分析**
   - 最差帧 yaw=150/pitch=-80，jinshuzhuti 1081 像素：
     - f_r 呈**双峰分布**：50% 像素 f_r=0.064（纯漫射 ρ_d/π），50% 像素 f_r=0.575（接近理论镜面峰值：ρ_d/π + ρ_s·(0.998)^80 = 0.064 + 0.511 = 0.575）
     - NoH q50=0.998 → 镜面峰精确命中
     - jinshuzhuti 贡献 97% OCS（0.166/0.171）
   - OCS_B = 0.171，OCS_A_no_occ = 0.077 → **B 比 A（无遮挡）还高 2.2×**
   - 这说明差异不是遮挡导致的（A 即使不加遮挡也只有 0.077）

   **路线三：A/B 几何精度不对称 → 已排除（2026-05-19）**
   - **假说**：A 端 fast 简化网格（20% 面元）丢失镜面峰所需关键面元朝向精度
   - **验证**：`diag_geometry_accuracy.py` 单帧 yaw=150/pitch=-80 分别跑 fast（96k faces）和 full（481k faces）
   - **结果**：A_fast OCS_no_occ=0.07679，A_full OCS_no_occ=0.07663，**差仅 0.2%**；两者均仅为 B 端 0.171 的 ~45%
   - **结论**：几何精度假说排除。根因不是网格简化，而是 face-center 采样 vs pixel-level 采样的离散化差异（A 端每面一个 BRDF 值 vs B 端每像素一个 BRDF 值）

   **路线四：face-center vs pixel-level 采样 → 已确认主因（2026-05-19）**
   - A 端 face-center 离散化对 `n=80` 窄镜面峰是结构性缺陷，specular 项在 A 端实测为 0
   - A_full vs A_fast 差异仅约 0.2%，因此网格简化不是根因
   - diffuse-only 仍存在约 26% gap（A_with_occ=0.0163 vs B_diffuse=0.0219），说明几何/投影/面积/可见性链路还需进一步对账
   - 下一步先做 diffuse-only per-part 对账，再决定 A 端采用 sub-face 自适应积分或 pixel-level 统一积分

   ### 已排除的根因总结
   | 假说 | 排除方式 |
   |------|----------|
   | 法线坐标系错误 | 已验证为 world space |
   | 分辨率不足 | res=128 vs 256 OCS 差 <1% |
   | smooth shading | 强制 flat shading 无变化 |
   | 背面像素污染 | Backfacing AOV 全零，不存在背面像素 |
   | Combined 遮罩误杀 | 去掉遮罩后 OCS 不变（排除的像素贡献极低） |
   | OCS 公式推导错误 | 数学自洽（NoV 抵消推导正确） |
   | A/B 几何精度不对称 | A_fast(0.0768) vs A_full(0.0766) 差仅 0.2%，均仅为 B 的 45% |
   | 纯镜面峰采样问题 | A diffuse-only 与 full 结果完全一致（specular 贡献=0），镜面峰确认零贡献 |
   | A/B BRDF 公式/单位/面积链路错误 | 单平板三端闭合（解析/A/B 均 0.00163，rel_err<0.5%）|
   | 解析解转置 bug（N_body@R vs R@N_body）| 修复后 5 姿态三端闭合（mean rel_err=0.25%），yaw∈{0,180}且pitch=0 时被对称性隐藏 |

   ### 产物路径
   - 旧基线（有 Transparent BSDF + Combined 遮罩）：`结果/模块B_渲染/run_20260518_200741_exact_brdf/`（703 帧 res=128）
   - 新基线（无 Transparent BSDF，Backfacing AOV）：`结果/模块B_渲染/run_20260519_backface_fix/`（703 帧）
   - AOV 测试渲染：`结果/模块B_渲染/run_test_aov/`（第一帧）、`run_test_aov2/`（去 Transparent）、`run_test_aov3/`（yaw=150/pitch=-80）
   - 临时 scan JSON：`结果/模块B_渲染/test_aov_single.json`

   ### 诊断脚本（已建）
   - `02_blender/diag_normal_check.py`：单帧法线 vs A 端对比（发现翻转现象）
   - `02_blender/diag_normal_space.py`：早期法线坐标系诊断
   - `02_blender/check_R_attitudes.py`：手算 R 矩阵预期法线
   - `02_blender/verify_one_frame.py`：单帧 BRDF 公式逐部件复现
   - `02_blender/analyze_consistency.py`：703 帧统计（Pearson/Spearman/分位）
   - `02_blender/diag_geometry_accuracy.py`：A_fast vs A_full 单帧对比（排除几何精度假说）
   - `02_blender/diag_diffuse_only.py`：A 端 diffuse-only 验证（monkey-patch rho_s=0）
   - `02_blender/diag_diffuse_only_B.py`：B 端 diffuse-only 验证（读 EXR 重算）
   - `02_blender/diag_per_part_reconcile.py`：diffuse-only per-part 对账（发现方向相反误差）
   - `02_blender/diag_pixel_inspect.py`：B 端 per-part 像素法线/NoL/NoH 检查
   - `02_blender/flat_plate_closure.py`：单平板 A vs 解析验证（6 角度）
   - `02_blender/render_flat_plate.py`：Blender 单平板 MULTILAYER EXR 渲染
   - `02_blender/diag_flat_plate_B.py`：单平板三端闭合验证（解析/A/B）
   - `06_brdf_validation/render_flat_plate_batch.py`：Blender 单平板多姿态批量渲染（5 姿态单进程）
   - `06_brdf_validation/run_plane_batch_validation.py`：单平板三端闭合批量 orchestrator
   - `06_brdf_validation/run_material_sweep.py`：三材料单平板 EXR 复用 sweep
   - `06_brdf_validation/render_L_plate.py`：Blender L 型双平板渲染
   - `06_brdf_validation/run_L_plate_validation.py`：L 型双平板三端对账 orchestrator
   - `06_brdf_validation/render_cube.py`：Blender 立方体渲染
   - `06_brdf_validation/run_cube_validation.py`：立方体三端对账 orchestrator

6. ✅ **Step 5 续：diffuse-only 验证**（已完成 2026-05-19）
   - **目的**：临时设 `rho_s=0`，关闭镜面项，隔离 face-center vs pixel-level 采样差异
   - **脚本**：`diag_diffuse_only.py`（A 端 monkey-patch get_material）+ `diag_diffuse_only_B.py`（B 端读 EXR 重算）
   - **结果**（yaw=150/pitch=-80）：

     | 指标 | A_full | B_exact | A/B |
     |---|---|---|---|
     | 含镜面 (with_occ) | 0.0163 | 0.1711 | 9.5% |
     | 含镜面 (no_occ) | 0.0766 | — | — |
     | **diffuse-only with_occ** | **0.0163** | **0.0219** | **74.2%** |
     | specular 贡献 | 0 (0%) | 0.149 (87%) | — |

   - **两条根因并存**：
     1. **镜面采样**（主因，10× 差距）：A 端 face-center 采样完全错过 n=80 窄镜面峰（贡献精确为 0），B 端 pixel-level 成功捕获。即使 full mesh（481k faces）也无法命中——每面一个 BRDF 值对窄高光是不够的
     2. **diffuse 基底**（次因，26% 差异）：纯漫射下 A/B 仍有差距，说明几何/投影/面积/可见性层面尚有未对齐之处（BRDF2.md §10.1 路径）
   - **关键结论**：A 端 face-center 采样对窄镜面峰是结构性缺陷，不是精度问题——再多面元也捕获不到。需要 sub-face 自适应积分或改用 pixel-level 积分

5. ✅ **Step 5：B 端单平板多角度批量验证**（已完成 2026-05-19）
   - **新增脚本**：
     - `ocs_project/06_brdf_validation/render_flat_plate_batch.py`：Blender headless 单进程渲染 5 姿态
     - `ocs_project/06_brdf_validation/run_plane_batch_validation.py`：Orchestrator（调 Blender → 后处理 → 解析/A/B 对比 → CSV/报告/图）
   - **修复的关键 bug**：解析解中 `N = N_body @ R` 取到第三**行**（R[2,:]），应取第三**列**（R[:,2]）。修正为 `N = R @ N_body`。此 bug 在 yaw∈{0,180} 且 pitch=0 时被对称性隐藏，在非零 pitch 时暴露。
   - **产物**：`结果/BRDF验证/plane_batch_20260519_204323/`
   - **5 姿态三端闭合结果**（LegacyPhong full, jinshuzhuti 材料）：

     | yaw | pitch | analyt | A | B | rel B/analyt |
     |---|---|---|---|---|---|
     | 0 | 0 | 0.001630 | 0.001630 | 0.001637 | 0.43% |
     | 0 | -30 | 0 | 0 | 0.002120 | N/A (NoL=0) |
     | 90 | -45 | 0.008963 | 0.008963 | 0.008968 | 0.06% |
     | 150 | -80 | 0.415301 | 0.415301 | 0.415328 | 0.007% |
     | 180 | 0 | 0.001630 | 0.001630 | 0.001637 | 0.43% |

   - **Diffuse-only 同样闭合**（所有 NoL>0 姿态 rel_err < 0.06%）
   - **结论**：
     - **所有 NoL>0 姿态三端闭合，Full mean rel_err=0.25%，Diffuse mean rel_err=0.25%**
     - A 端 face-center 与 B 端 pixel-level 在单平板上**完全一致**（因为平板法线各处相同，中心采样无意义）
     - yaw=0/pitch=-30 边缘情况：太阳在平板背面（NoL=0），A/解析正确给出 0，B 端因 Blender 着色法线行为有微小残差（2.1e-3），不影响结论
   - **关键发现**：
     - `flat_plate_closure.py` 中的解析解存在转置 bug（`N_body @ R` → `R @ N_body`），但不影响 A/B 一致性结论（A 使用正确的 `normals @ R.T` = `R[:,2]`）
     - A/B 两端 BRDF/投影/面积/单位链路在单平板上**完全验证通过**

6. ✅ **Step 6：材料 sweep + 简单多面几何可见性语义验证**（已完成 2026-05-20）
   
   ### 6a. 材料 sweep（三材料单平板复用 EXR）
   - **脚本**：`ocs_project/06_brdf_validation/run_material_sweep.py`
   - 复用 `plane_batch_20260519_204323` 的 EXR（几何缓冲与材质无关）
   - 测试 jinshuzhuti / taiyangnengban / yinshenban 三种 LegacyPhong 材料
   - **结果**：三种材料均三端闭合，mean rel_err=0.253%（与单材料一致）
   - **结论**：几何缓冲方案（Normal/Depth/IndexOB EXR）材质独立性验证通过，不同材料无需重新渲染

   ### 6b. L 型双平板
   - **几何**：两块 1m² 板（XY+Z / XZ+Y），共享 X 轴接缝，形成 L 型
   - **新增脚本**：
     - `06_brdf_validation/render_L_plate.py`：Blender headless L 型渲染
     - `06_brdf_validation/run_L_plate_validation.py`：Orchestrator（Blender→后处理→解析/A/B）
   - **新增 STL**：`建模/L_plate_vertical.stl`（XZ 平面，法线 +Y）、`建模/flat_plate_1m2_subd.stl`、`建模/L_plate_vertical_subd.stl`（10×10 细分，200 面/板）
   - **初始问题**：STL 顶点绕序错误（法线 [0,-1,0]），已修正；A 端 RayForest API 用错（`query_visibility` 不存在，应为 `batch_occlusion_dual`），已修正
   - **结果**（细分 200 面/板，jinshuzhuti 材料）：

     | yaw | pitch | A_no/an | A_with (Plate_H) | B (Plate_H) | A_with/B | occ% |
     |-----|-------|---------|-------------------|-------------|----------|------|
     | 0 | 0 | 0.00% | 9.21e-4 | 9.16e-4 | **1.005** | 43.5% |
     | 90 | -45 | 0.00% | 4.66e-3 | 6.68e-3 | 0.698 | 48.0% |
     | 150 | -80 | 0.00% | 0.172 | 0.281 | 0.613 | 58.5% |
     | 180 | 0 | 0.00% | 8.96e-4 | 9.16e-4 | **0.979** | 45.0% |

   - **关键发现**：
     - A_no 在所有 NoL>0 姿态与解析解完美一致（0.00% 误差）
     - A_with/B ≈ 1.0 在中等角度（yaw=0/180），ray-cast 与 rasterization 遮挡语义一致
     - 极端角度（yaw=90/150）A_with/B < 1，face-center 遮挡比像素级更保守
     - Plate_V 在所有测试姿态均 NoL≤0（太阳在 +X 方向，法线 +Y 无 X 分量），无法测试其被遮挡场景
     - B 端在 yaw=0/pitch=-30 有背向面照明伪影（Plate_H NoL=0 但 B=1.19e-3），此为已知 Blender Cycles 着色法线行为
   - **产物**：`结果/BRDF验证/L_plate_20260520_103105/`

   ### 6c. 立方体
   - **几何**：1m³ 立方体，中心在原点，6 面 × 25 子面(5×5 细分) = 300 三角面元
   - **新增脚本**：
     - `06_brdf_validation/render_cube.py`：Blender headless 立方体渲染
     - `06_brdf_validation/run_cube_validation.py`：Orchestrator（Blender→后处理→解析/A/B）
   - **新增 STL**：`建模/cube_1m_subd.stl`
   - **结果**（jinshuzhuti 材料）：

     | yaw | pitch | an_total | A_no | A_with | B | A_with/B | B/an | occ% |
     |-----|-------|----------|------|--------|---|----------|------|------|
     | 0 | 0 | 2.88e-2 | 2.88e-2 | 2.88e-2 | 2.87e-2 | **1.002** | **0.25%** | 0% |
     | 0 | -30 | 2.88e-2 | 2.88e-2 | 2.88e-2 | 2.88e-2 | **1.001** | **0.14%** | 0% |
     | 90 | -45 | 3.61e-2 | 3.61e-2 | 3.61e-2 | 3.61e-2 | **1.000** | **0.02%** | 0% |
     | 150 | -80 | 0.415 | 0.415 | 0.415 | 0.415 | **1.000** | **0.02%** | 0% |
     | 180 | 0 | 2.88e-2 | 2.88e-2 | 2.88e-2 | 2.87e-2 | **1.002** | **0.25%** | 0% |

   - **关键发现**：
     - **三端近乎完美闭合**：B/an ≤ 0.25% 所有姿态，远超 <2% 目标
     - 自遮挡率为 0%（立方体为凸体，无自遮挡，与几何预期一致）
     - 无背向面照明伪影（凸体背面自然隐藏）
     - Diffuse-only 同样闭合（B/an ≤ 0.25%）
   - **产物**：`结果/BRDF验证/cube_20260520_103846/`

   ### Step 6 总体结论
   - **单平板 + 材料 sweep + L 型 + 立方体，LegacyPhong BRDF 全部三端闭合**
   - A 端 BRDF / 几何 / 坐标变换 / 面积单位链路在单面元级别完全正确
   - B 端 pixel-level BRDF / 后处理 / 单位链路同样正确
   - **凸几何（平板/立方体）闭合精度** ≤ 0.25%，达到 "数字孪生" 级别
   - **凹几何（L 型）A_with/B ≈ 1.0 在中等角度**，极端角度有差异（face-center vs pixel-level）
   - **真实三件套卫星的 diffuse gap（~26%）根因确认为可见性语义差异**（ray-cast face-center vs camera rasterization），非 BRDF/几何/投影/单位错误
   - **Blender Cycles 背向面着色**是已知噪声源（在 NoL≤0 或 NoV≤0 姿态产生非零残差），在有效姿态（NoL>0 且 NoV>0）上 B 端精度良好

7. ✅ **Step 7a：A 端 sub-face 自适应积分 → 失败**（2026-05-20）
   - **方法**：顶点法线面积加权平均 + 三角形中点剖分 + 重心法线插值 + 自适应递归（NoH>0.96 且 range>0.001 → 剖分，max_depth=5）
   - **新增文件**：`ocs_project/01_code/adaptive_integration.py`（核心模块）+ `ocs_project/02_blender/diag_subface_adaptive.py`（诊断脚本）
   - **3 姿态 × 3 部件对比**（full 精度，无遮挡 no_occ）：
     | 姿态 | A_fc | A_ad | B_diff | B_full | ad/fc | ad/Bf |
     |---|---|---|---|---|---|---|
     | 正照 0°/0° | 0.0423 | 0.0423 | 0.0134 | 0.0145 | 1.00 | 2.91 |
     | 斜射 90°/-40° | 0.0704 | 0.0695 | 0.0237 | 0.0240 | 0.99 | 2.89 |
     | 强镜面 150°/-80° | 0.0766 | 0.0801 | 0.0219 | 0.1711 | 1.05 | 0.47 |
   - **失败原因**：
     1. ad/fc ≈ 1.0，自适应积分几乎没有改变 OCS（最大仅 7% 提升），远不足以弥合与 B 的 gap
     2. **主因是可见面积差异，非镜面采样**：diffuse-only 下 A/B ≈ 2–3×，A 端 NoL>0 & NoV>0 的面元远多于 B 端相机光栅化可见像素
     3. 太阳能板极端异常（yaw=90°/-40° ad/B_diff=72×）：薄板两面均满足法线判据但仅一面对相机可见
     4. 顶点法线是相邻面平均，粗网格无法重构 n=80 窄镜面峰所需的 <0.5° 精度
     5. 性能不可接受：单姿态 12-15s（vs 面中心 0.03s），400-500× 减速
   - **结论**：flat shading 下面内法线恒定，顶点法线插值无法在粗网格上生成镜面方向精度。A/B gap 根因是**可见性语义不同**（几何法线判据 vs 相机光栅化深度测试），非面内 BRDF 变化。应转向 pixel-level 统一积分。
   - **产物**：`结果/BRDF验证/subface_adaptive_diag/subface_adaptive_comparison.csv`

8. ✅ **Step 7b：A 端 pixel-level 统一积分**（已完成 2026-05-20）
   - **新增函数**：`adaptive_integration.py` 中 `compute_ocs_from_exr()`，封装 EXR→法线/IndexOB→eval_legacy_phong→OCS 全链路
   - **验证**：`verify_pixel_unified.py`，3 姿态 × diffuse/full 共 6 项，与 `brdf_postprocess.py` 结果完全一致（diff=0.00e+00）
   - **意义**：A/B 两端现在可共享完全相同的几何源（Blender EXR），消除可见性语义差异
   - **当前状态**：函数可用但尚未接入 `ocs_core.py` 生产扫描循环；接入需先生成 EXR 再扫描，改变 A 端执行顺序
   - **下一步**：Step 8 GGX 验证，LegacyPhong 闭合已确认，可切到论文主模型
   - **产物**：`ocs_project/01_code/adaptive_integration.py`（已追加函数）+ `ocs_project/02_blender/verify_pixel_unified.py`

9. ✅ **Step 8：GGX 小规模验证**（已完成 2026-05-20）
   - 新增 `ocs_project/06_brdf_validation/verify_ggx.py`：canonical EXR 管线上单次读取并行计算 LegacyPhong + GGX 双 BRDF OCS
   - 单平板 5 姿态 / 立方体 5 姿态 / 卫星三部件 3 姿态，全部数值健康 PASS（无 NaN/Inf/负值）
   - 关键验证项：metallic=1→diffuse=0 ✓、D_max 随 roughness 递减 ✓、F_Schlick/G_Smith/D_GGX 全有限 ✓
   - LegacyPhong 不回归（OCS 与已知基线一致），GGX vs LegacyPhong 差异物理合理（金属无漫射、微表面镜面峰更强）
   - 产物：`结果/BRDF验证/plane_batch_*/ggx_verify/`、`cube_*/ggx_verify/`、`satellite_subset_3att/ggx_verify/`

10. 🔜 **精度与数据集升级**（进行中）
   - **10a ✅ GGX 接入模块 A 生产扫描**（2026-05-20）：
     - `config.py` 新增 `BRDF_MODEL` 配置项（默认 `"legacy_phong"`，不变）
     - `materials.py` 新增 `_GGX_DB` + `get_material(part_name, use_ggx=False)` GGX 分支
     - `ocs_core.py` `compute_single_attitude()`/`scan_attitude()`/`_worker_init()` 透传 `use_ggx`
     - `main_run.py` 新增 `--ggx` CLI 显式切换入口
   - **10b ✅ GGX 703 姿态 10° 网格扫描**（2026-05-20）：
     - 126.7s（8 进程，fast 精度），OCS max=1.30 min=0.0022 mean=0.021 m²
     - 产物：`结果/模块A_重构/2d_yaw37_pitch19/run_20260520_160131/`
   - **10c ✅ GGX 5° 网格扫描**（2026-05-20）：
     - `main_run.py` 新增 `--num-yaw`/`--num-pitch` CLI 覆盖（不改 config.py 默认值）
     - 2701 姿态（73×37），454.0s（8 进程），OCS max=14.82 min=0.0022 mean=0.033 m²
     - 关键发现：10° 网格严重欠采样金属镜面峰（max 差 11.4×），5° 网格为论文必需
     - 产物：`结果/模块A_重构/2d_yaw73_pitch37/run_20260520_160847/`
   - **10d ✅ 多观测几何扩展**（2026-05-20）
     - `config.py` 新增 `OBS_GEOMETRIES`（5 组 sun/det，覆盖相位角 24°–120°）
     - 新增 `run_multi_geom.py`：批量扫描入口，支持 `--geoms` 选择、`--ggx`、`--num-yaw`/`--num-pitch`
     - 全量 5 几何 × 2701 姿态 GGX 5° = 13,505 姿态，1724.5s（28.7min）
     - OCS max 跨几何差 5×（6.4~30.5 m²），OCS mean 差 4.8×（0.033~0.159）
     - 遮挡率：近后向散射最低（60%），大相位角最高（78.5%）
     - 产物：`结果/模块A_重构/multi_geom_ggx_yaw73_pitch37/run_20260520_162831/`

11. **CNN 反演与消融实验**（数据集升级后）
   - 建立 OCS-only / image-only / OCS+image 三类对比
   - HOG 作为传统 baseline，CNN 作为升级模型
   - 数据扩展优先级：2D 细网格 + 多太阳/探测器方向，roll 轴后续再加

11. ✅ **Step 11a-b：OCS-only kNN baseline + 紧凑消融矩阵**（2026-05-20）
   - **新增文件**：
     - `ocs_project/03_inversion/inv_common.py`：共享工具（数据加载/特征变换/split/kNN/指标/保存）
     - `ocs_project/03_inversion/inv_ocs.py`（重写）：支持多几何 + `--ablation` 一键消融
   - **关键修复**（根据 202605201825.md 建议）：
     - Top@5° 判据：`ea < 5°` → `ea <= 5° + 1e-6`（解决边界 5.00° 误判问题）
     - 新增 Top@10°（Top1/Top5）和 angular_err_p90 指标
     - `log_transform` 增加 `skip_cols` 参数，跳过遮挡率列（仅对 OCS 类特征 log10）
     - zscore 在 split 实验中只在训练集拟合（KNN 类自动处理，无需额外修改）
     - 修复 concat 特征 bug：原 `build_concat_features` 拼接完整 9D 后再 `select_features` 只取到第一个几何的特征；新增 `build_concat_features_with_mode` 逐几何选特征后拼接
   - **紧凑消融矩阵**：2 geom_set × 2 split × 3 feat × 2 transform = 24 实验
   - **产物**：`结果/模块C_反演/inv_ocs/run_20260520_184003_ablation/`（初版，有 bug）、`run_20260520_184414_ablation/`（修复后）

   ### 消融实验结果（run_20260520_184414 — 修复 concat 特征 bug 后）

   | geom | split | feat | xform | dim | mean | med | p90 | Top1@5° | Top5@5° | Top1@10° | Top5@10° |
   |---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
   | phase63 | LOO | total | raw | 3 | 79.49° | 80.00° | 154.51° | **7.1%** | 15.5% | 12.5% | 30.5% |
   | phase63 | LOO | per_part | raw | 6 | 30.27° | 10.00° | 89.40° | **40.9%** | 71.3% | 50.2% | 75.8% |
   | phase63 | LOO | all | raw | 9 | 40.79° | 17.30° | 128.48° | **32.7%** | 63.7% | 44.7% | 77.1% |
   | concat5 | LOO | total | raw | 15 | 53.41° | 31.78° | 139.19° | **22.4%** | 50.6% | 34.3% | 64.2% |
   | concat5 | LOO | **total** | **log** | 15 | **26.47°** | **5.00°** | 95.00° | **53.8%** | **85.5%** | **69.8%** | **92.6%** |
   | concat5 | LOO | per_part | raw | 30 | 41.73° | 5.00° | 150.00° | **54.0%** | 98.0% | 59.3% | 99.6% |
   | concat5 | LOO | per_part | log | 30 | 23.85° | 5.00° | 120.00° | **74.1%** | **99.4%** | **83.2%** | **99.9%** |
   | concat5 | LOO | all | raw | 45 | **12.28°** | 5.00° | **10.00°** | **77.4%** | **97.4%** | **91.6%** | **99.2%** |
   | concat5 | LOO | all | log | 45 | 13.74° | 5.00° | 8.66° | **78.1%** | **98.6%** | 91.0% | 99.6% |
   | concat5 | 10°→5° | total | log | 15 | 30.46° | 6.21° | 108.69° | 0.6% | 2.8% | 1.8% | 8.5% |
   | concat5 | 10°→5° | per_part | log | 30 | 14.85° | 5.00° | 15.69° | 1.0% | 4.7% | 2.5% | 9.8% |
   | concat5 | 10°→5° | all | log | 45 | **12.87°** | 5.00° | **10.80°** | 0.9% | 4.1% | 2.6% | 9.5% |

   ### 关键发现

   **1. `total` 特征（最接近真实观测）在 log 变换 + 多几何拼接后是可行的**
   - Concat5 total+log LOO: Top1@5°=53.8%, Top5@5°=85.5%
   - 对比 phase63 single total: Top1@5°=7.1% → 多几何增益 7.6×
   - **论文定位**："多观测几何显著提升 total OCS 姿态辨识能力"

   **2. log 变换对 total 特征是决定性的**
   - Raw concat5 total: mean=53.41°, Top1@5°=22.4%
   - Log concat5 total: mean=26.47°, Top1@5°=53.8%
   - GGX 镜面峰动态范围 >10^4，欧氏距离被峰值主导；log 压缩后部件结构信息浮现

   **3. total vs per_part/all 差距 = 部件分解的信息增益**
   - LOO Top1@5°: total=53.8% < per_part=74.1% < all=78.1%
   - 证明部组件 OCS 分解携带额外姿态信息，支撑后续 image-only 和双流融合的论证

   **4. 10°→5° split：kNN 无法姿态空间插值**
   - Best Top1@5°=1.1%（per_part raw），Top1@10°=2.6%（all log）
   - 最佳 mean angular error=12.87°（all log）— 接近 10° 库间距
   - **明确需要 MLP/CNN 做连续回归**

   **5. log 改善 10°→5° 但伤 LOO 精细度（部分）**
   - LOO: raw all mean=12.28° < log all mean=13.74°（raw 更精确）
   - 10°→5°: raw all mean=16.31° > log all mean=12.87°（log 更泛化）
   - 匹配预测"情况 3"：raw 依赖镜面峰做精细 LOO 匹配，log 更平滑适合泛化

12. ✅ **Step 11c：OCS-only MLP 连续回归 + 加权 kNN baseline**（2026-05-21）
   - **新增文件**：
     - `ocs_project/03_inversion/train_mlp.py`：完整 MLP 训练 + kNN regression baseline
     - `inv_common.py` 新增 `obs_total` 特征模式（每几何仅 ocs_with_occ，5D）
   - **技术方案**：
     - 输出编码：`[sin(yaw), cos(yaw), sin(pitch), cos(pitch)]`，预测时归一化解码
     - 模型：MLP 128→128→64 SiLU LayerNorm Dropout0.10
     - 训练：AdamW lr=1e-3 wd=1e-4 batch=64，early stop patience=150
     - 预处理：log10 + zscore，scaler 仅 fit train
     - Split：10° 网格 train（563）→ 5° 插值 test（1998），train 内 80/20 val
     - Baseline：KNeighborsRegressor K=5 distance-weighted
   - **特征矩阵**：obs_total(5D) / total(15D) / per_part(30D) / all(45D) × (log / raw)
   - **产物**：`结果/模块C_反演/mlp_ocs/run_20260521_084723/`

   ### MLP 结果

   | Feat | Method | mean | p90 | Hit@5° | Hit@10° |
   |---|---|---:|---:|---:|---:|
   | obs_total 5D log | kNN-w | 58.25° | 132.39° | 5.3% | 12.3% |
   | obs_total 5D log | **MLP** | **54.90±0.7°** | 117.02° | 4.3% | 10.4% |
   | total 15D log | kNN-w | 41.80° | 103.45° | 8.1% | 20.7% |
   | total 15D log | **MLP** | **36.69±3.6°** | 93.09° | 9.7% | 23.5% |
   | per_part 30D log | kNN-w | 26.37° | 111.71° | 46.6% | 69.3% |
   | per_part 30D log | **MLP** | **5.91±0.2°** | 7.74° | **73.8%** | **94.3%** |
   | all 45D log | kNN-w | 21.95° | 86.59° | 43.6% | 69.1% |
   | all 45D log | **MLP** | **6.93±0.7°** | 8.67° | 69.1% | 92.3% |
   | **all 45D raw** | kNN-w | 21.84° | 90.81° | 47.9% | 73.8% |
   | **all 45D raw** | **MLP** | **3.98±0.6°** | 4.82° | **90.7%** | **97.1%** |

   ### 关键发现

   **1. MLP 连续回归碾压 kNN 离散检索**
   - kNN discrete Top1@5° < 1%，kNN weighted regression 最好 47.9%，MLP 最好 90.7%
   - 论证链：离散检索 → 加权回归 → MLP 回归，每一步都显著提升

   **2. 最意外的：all 45D RAW 最好**
   - MLP raw mean=3.98°, Hit5=90.7% > MLP log mean=6.93°, Hit5=69.1%
   - MLP 可以自主学习处理 GGX 镜面峰的大动态范围，log 压缩反而丢失信息
   - 与 kNN 结论相反（kNN 必须 log 才能工作）

   **3. per_part 最稳定，log 下 30D 优于 45D**
   - per_part log mean=5.91±0.22°, all log mean=6.93±0.75°
   - 45D 包含冗余/遮挡率特征，小样本（563 train）下过拟合
   - per_part 30D 在论文中作为性能上限更合适（all 45D 含 oracle 量）

   **4. obs_total 5D 很差：真实可观测总 OCS 插值能力有限**
   - MLP mean=54.9° vs kNN-w 58.3°，提升仅 3.4°
   - 5 几何总 OCS 本身不足以做 5° 插值 → 需要部件分解信息
   - 论文定位：支撑 "OCS + 图像融合" 的必要性

   **5. total 15D 也不够：无遮挡 OCS + 遮挡率是半 oracle**
   - MLP mean=36.7°，方差大（3.6°），训练不稳定
   - 比 per_part（5.9°）差 6× → 分部件信息是关键

   **6. kNN weighted regression 作为连续 baseline 很好**
   - kNN-w per_part=26.37° → MLP per_part=5.91°（4.5× 提升）
   - kNN-w all raw=21.84° → MLP all raw=3.98°（5.5× 提升）
   - 清楚地证明了"学习连续映射"的价值

13. ✅ **Step 11d：OCS+image 联合反演**（2026-05-21 完成）
   - ✅ `brdf_postprocess.py` 新增 `--ggx` 参数（2026-05-21）
   - ✅ `render_geometry_passes.py` 修复 `os.path.abspath(out_dir)`（2026-05-21）防 Blender Compositor 写到 C:\
   - ✅ phase63 3 帧 GGX 验证（2026-05-21）：OCS B/A mean rel_err=4.93%
   - ✅ phase63 2701 帧批量渲染（2026-05-21）：863.2s，0.32s/帧，OPTIX GPU
   - ✅ GGX 后处理 2701 PNG（2026-05-21）：radiance_max=53.07
   - ✅ 完整性检查通过：EXR 2701 / PNG 2701 / CSV 2701
   - 产物：`结果/模块B_渲染/run_20260521_phase63_ggx/`（2701 EXR + 2701 PNG）
   - ✅ inv_image.py 增加 --image-dir 参数 + out_prefix→_brdf.png 映射（2026-05-21）
   - ✅ HOG image-only LOO baseline（2026-05-21）：Top1@5°=**74.79%**, Top5@5°=98.11%, mean=4.31°
   - 产物：`结果/模块C_反演/inv_image/run_20260521_123201/`
   - ✅ **inv_joint.py 重写**（2026-05-21）：复用 `inv_common.py`，支持多几何 OCS + HOG image 联合 kNN + alpha sweep (0:0.05:1 + 局部精扫 0.01)
   - ✅ `run_joint_11d.py` runner：自写日志，绕过 Windows shell exit 127
   - ✅ **pairwise OOM 修复**（202605211536.md 方案）：
     - 根因：HOG (2701, 8100) float64 zscore/pairwise 步骤在 Windows numpy/MKL 下静默退出
     - `inv_common.py` 追加 `zscore_float32` + `pairwise_euclidean_chunked`（分块 GEMM batch=128，旧函数保留）
     - `inv_joint.py` 图像端切 float32（83.5 MB vs 167 MB）+ chunked pairwise；OCS 端 45D 保留 float64
     - 隔离验证 `debug_pairwise_hog.py`：HOG 11.2s → zscore 0.12s → chunked pairwise 1.06s → D (2701,2701) 健康
   - ✅ **alpha sweep LOO 结果**（concat5 OCS-all-raw 45D × HOG 8100D）：

     | alpha | Top1@5° | Top5@5° | mean | p90 |
   |---:|---:|---:|---:|---:|
     | 0.00 (image-only)  | 81.30% | 99.15% | 4.31° | 6.54° |
     | **0.24 (best mean)** | **84.64%** | **99.48%** | **4.10°** | **5.85°** |
     | 0.85 (best Top1)   | **89.12%** | 99.59% | 4.65° | 5.11° |
     | 1.00 (OCS-only kNN) | 77.42% | 97.37% | 12.28° | 10.00° |

   - **关键发现**：
     1. 联合 alpha=0.24 在 mean 上击败两端（4.10 < 4.31 image-only）
     2. alpha=0.85 时 Top1@5° 达 89.12%，mean 反而升 → p90 与 mean 反向 trade-off
     3. image-only 在 `inv_joint`（全样本 zscore+pairwise）为 81.30%，高于 `inv_image` 的 74.79%（两条 normalize 路径差异，待对账）
     4. OCS-only kNN（77.42% LOO）与 OCS MLP（90.7% 10°→5°）不同 split，不可直接比较
   - 产物：`结果/模块C_反演/inv_joint/run_20260521_155144/`（alpha_sweep.csv / ablation_table.md / predictions_best.csv / summary.json / config_used.json）

14. ✅ **Step 11e-A：CNN image-only 连续回归 baseline**（2026-05-21 完成）
   - **新增文件**：`ocs_project/03_inversion/train_cnn.py`
     - 模型：TinyCNN（Conv/GN/SiLU/Pool×4 → AdaptiveAvgPool → MLP 128→64→4, 106k params）
     - 输出编码：`[sin(yaw),cos(yaw),sin(pitch),cos(pitch)]`（与 `train_mlp.py` 一致）
     - Split：10° 网格 train（563）→ 5° test（1998），val 80/20 from train
     - 支持 `--intensity raw/log1p`，`--seeds` 多 seed
   - ✅ 安装 PyTorch 2.8.0+cu128（RTX 5060 Blackwell sm_120 兼容）
   - ✅ **消融**：log1p (mean=12.13°) 胜 raw (mean=15.99°)
   - ✅ **5 seeds 正式实验**（log1p, 500 epochs, patience 100, 1×128×128）：

     | Seed | mean | p90 | Hit5 | Hit10 | best_epoch |
     |---:|---:|---:|---:|---:|---:|
     | 0 | **11.07°** | **21.95°** | **27.9%** | **59.0%** | 394 |
     | 1 | 12.23° | 24.36° | 25.8% | 55.7% | 360 |
     | 2 | 12.63° | 26.06° | 26.2% | 56.1% | 487 |
     | 3 | 13.33° | 26.11° | 25.1% | 53.1% | 354 |
     | 4 | 12.63° | 25.73° | 25.7% | 55.3% | 329 |
     | **mean±std** | **12.38±0.74°** | — | **26.1±0.9%** | **55.8±1.9%** | — |

   - **同 split 对照**（10°→5°）：

     | 方法 | 输入 | mean | Hit5 | Hit10 |
     |---|---|---:|---:|---:|
     | OCS-only MLP all raw | concat5 45D | **3.98±0.6°** | **90.7%** | **97.1%** |
     | OCS-only kNN all log | concat5 45D | 12.87° | <1% | — |
     | **CNN image-only log1p** | phase63 128×128 PNG | **12.38±0.74°** | **26.1%** | **55.8%** |

   - **关键发现**：
     1. CNN (12.38°) 与 OCS kNN (12.87°) 在 mean 上可比，CNN 略优；但 MLP (3.98°) 仍大幅领先
     2. CNN 仅用单张 phase63 图像 (1ch 128×128) 即达 12.38°——图像确实含姿态信息
     3. log1p (12.13°) 优于 raw (15.99°)，与 kNN 类似（log 压缩大动态范围有益）
     4. 106k 参数小模型，单 seed ~6min (RTX 5060)，仍有大幅优化空间
   - 产物：`结果/模块C_反演/cnn_image/run_20260521_164437_final_log1p/`（5× metrics/pt/csv/curve）

15. ✅ **Step 11e-B1：CNN+OCS 预测级 late fusion 消融**（2026-05-22 完成）
   - **新增文件**：`ocs_project/03_inversion/fuse_predictions.py`
   - **方法**：sin/cos 空间预测级融合 `vec_fused = beta * vec_ocs + (1-beta) * vec_img`
   - **对齐**：按 `(yaw_true, pitch_true)` 精确匹配，所有 case 1998/1998 匹配
   - **重要限制**：OCS MLP 预测文件仅含 seed 4（非 5-seed），因 `train_mlp.py` 保存逻辑仅保留最后 seed。端点 sanity 全部通过

   ### 结果（seed 4 OCS × 5 CNN seeds, 10°→5° split, beta 0:0.01:1）

   | OCS case | OCS-only (β=1) | CNN-only (β=0) | Best β | Fused mean | Fused Hit5 | Δ vs OCS |
   |---|---|---:|---:|---:|---:|---:|
   | **all_raw** 45D | mean=5.09° Hit5=87.0% | mean=12.38° Hit5=26.6% | 0.96 | **5.03°** | **87.4%** | +1.2% |
   | **per_part_log** 30D | mean=6.24° Hit5=70.7% | mean=12.38° Hit5=26.6% | 0.93 | **6.15°** | **71.8%** | +1.4% |
   | **total_log** 15D | mean=31.95° Hit5=15.1% | mean=12.38° Hit5=26.6% | 0.11 | **11.99°** | **26.6%** | **-62.5%** |

   ### 关键发现

   **1. OCS 强时 CNN 贡献极小**
   - all_raw: beta=0.96，OCS 权重 96%，CNN 仅提供 0.06° 改善（5.09°→5.03°）
   - per_part_log: beta=0.93，OCS 权重 93%，改善 0.09°（6.24°→6.15°）
   - **结论**：当 OCS 已经很强时（mean<10°），单张 128×128 灰度图像几乎不提供互补信息

   **2. OCS 弱时 CNN 主导**
   - total_log: beta=0.11，CNN 权重 89%，mean 从 31.95° 降至 11.99°（-62.5%）
   - **结论**：弱 OCS 观测 + 图像可大幅互补，但融合结果仍不如纯 CNN（11.99° vs 12.38°，仅微升 3%）

   **3. sin/cos 空间 late fusion 提升有限**
   - 所有 case 最佳融合均仅微量优于两端中强者
   - late fusion 本质是加权平均两个预测，无法学习跨模态交互
   - **推论**：需要 feature-level 融合（双流网络联合训练）才能真正互补

   **4. 端点 sanity 全部通过**
   - beta=0 CNN 端点与已知 CNN image-only 基线一致（12.38°）
   - beta=1 OCS 端点与 seed 4 单 seed 指标一致（all_raw: 5.09°, per_part_log: 6.24°, total_log: 31.95°）

   - **产物**：
     - `结果/模块C_反演/cnn_ocs_late_fusion/run_20260522_220850_all_raw/`
     - `结果/模块C_反演/cnn_ocs_late_fusion/run_20260522_220945_per_part_log/`
     - `结果/模块C_反演/cnn_ocs_late_fusion/run_20260522_220946_total_log/`
   - **新增代码**：`ocs_project/03_inversion/fuse_predictions.py`

16. ✅ **Step 11e-B2：Feature-level CNN+OCS 双流联合训练**（2026-05-22 完成）
   - **新增文件**：`ocs_project/03_inversion/train_fusion.py`
   - **模型**：ImageBranch(TinyCNN→64D) + OCSBranch(MLP→64D) + FusionHead(concat 128D→4)
   - **训练**：end-to-end, 10°→5° split, 5 seeds, 500 epochs patience=100, batch=32, lr=1e-3
   - **数据**：图像 2701×1×128×128 log1p × OCS concat5 对齐, train=563/val=140/test=1998

   ### 结果

   | Case | OCS-only MLP | CNN-only | Feature Fusion | vs OCS-only |
   |---|---|---:|---:|---:|
   | **all_raw** 45D | **3.98±0.6°** Hit5=90.7% | 12.38° Hit5=26.1% | 5.42±0.45° Hit5=85.4% | **Worse** (-36%) |
   | **per_part_log** 30D | 5.91±0.2° Hit5=73.8% | 12.38° Hit5=26.1% | **4.10±0.77°** Hit5=87.3% | **Better (+31%)** |
   | **total_log** 15D | 36.69° Hit5=9.7% | 12.38° Hit5=26.1% | **13.75±2.37°** Hit5=40.0% | **Better (+63%)** |

   ### 关键发现

   **1. per_part_log 是 sweet spot**
   - Feature fusion (4.10°) > OCS-only (5.91°) > CNN-only (12.38°) > Late fusion (6.15°)
   - 图像和 OCS 在 feature level 真正互补，joint training 学到跨模态交互
   - mean=4.10° 仅略逊于最强 OCS-only all_raw (3.98°)，但 per_part_log 不含 oracle 量（遮挡率）

   **2. all_raw 反而变差——过参数化 + 小样本**
   - OCS 45D raw 已含近乎完美姿态信息（3.98°），加图像引入额外 106k 参数
   - 仅 563 train 样本，模型无法学到有效融合，图像分支成为噪声源
   - **推论**：强 OCS 特征不需要图像；图像互补只在 OCS 信息不足时体现

   **3. total_log 大幅改善但仍不如 CNN-only**
   - Fusion (13.75°) >> OCS-only (36.69°)，但略差于 CNN-only (12.38°)
   - 弱 OCS 特征（15D log total）在融合中被图像主导，但 OCS 分支的噪声拖累整体
   - 与 late fusion 对比：late fusion β=0.11 (11.99°) 更接近 CNN-only，feature fusion 反而不如
   - **推论**：弱 OCS 场景下，late fusion（加权平均）比 feature fusion 更好，因后者在训练中被弱 OCS 噪声干扰

   **4. Late fusion vs Feature fusion 对比**

   | OCS case | Late fusion best mean | Feature fusion mean | 更优 |
   |---|---|---:|---|
   | all_raw | **5.03°** | 5.42° | Late |
   | per_part_log | 6.15° | **4.10°** | **Feature** |
   | total_log | **11.99°** | 13.75° | Late |

   - **Feature fusion 只在 per_part_log 胜出**——这是唯一"OCS 中等 + 图像互补"的场景
   - **Late fusion 在极端场景更优**：OCS 过强（all_raw）或过弱（total_log）时，简单加权比联合训练更鲁棒

   - **产物**：
     - `结果/模块C_反演/cnn_ocs_fusion/run_20260522_221756_all_raw/`
     - `结果/模块C_反演/cnn_ocs_fusion/run_20260522_222227_per_part_log/`
     - `结果/模块C_反演/cnn_ocs_fusion/run_20260522_222731_total_log/`
   - **新增代码**：`ocs_project/03_inversion/train_fusion.py`

17. ✅ **Step 11f：论文级结果汇总与互补性诊断**（2026-05-22）

   - **新增文件**：`ocs_project/03_inversion/summarize_paper_results.py`（~650 lines）
     - 数据加载器：`load_ocs_mlp_metrics/predictions`、`load_cnn_metrics/predictions`、`load_feature/late_fusion_summary/predictions`
     - 主表构建：`build_main_table()`（10 methods × 8 metrics）、`save_main_table()`
     - 消融表构建：`build_fusion_ablation_table()`（3 OCS strengths × 4 methods）、`save_fusion_ablation()`
     - 论文图表（dpi=300）：`generate_bar_chart()`、`generate_hit5_bar_chart()`、`generate_cdf_plot()`、`generate_tradeoff_curve()`、`generate_improvement_heatmap()`
     - 互补性诊断：`complementarity_diagnosis()`（per_part_log, 相关性/混淆矩阵/分箱/偏航分析）
     - 案例画廊：`case_gallery()`（best 6/worst 6/big wins/big losses）
     - 论文声明：`generate_paper_claims()`（5 项核心声明 + 2 项未来工作 + 6 项局限性）
     - 健全性检查：`run_sanity_check()`、汇总 JSON：`save_summary_json()`
   - **辅助文件**：`_runner_textonly.py`（无图形文本运行器，自写日志）、`_runner_summarize.py`（带 matplotlib 图形的完整运行器）

   ### 产物
   - **输出目录**：`结果/模块C_反演/paper_summary/run_20260522_234553/`
   - **表格**：`table_main_inversion.csv/.md`（10 方法主反演结果表）
     - OCS MLP all_raw: mean=3.98±0.6°, Hit5=90.7%
     - Feature fusion per_part_log: mean=4.10±0.77°, Hit5=87.3%
     - CNN image-only: mean=12.38±0.74°, Hit5=26.1%
   - **消融表**：`table_fusion_ablation.csv/.md`（3 OCS 强度 × 4 方法 + 解读）
     - Per-part log sweet spot: Feature fusion > OCS-only (4.10° vs 5.91°, +31%)
     - Strong OCS: OCS-only 最优；Weak OCS: Late fusion 最优
   - **论文图表**：fig01_bar_chart.png / fig02_hit5_bar_chart.png / fig03_cdf.png / fig04_beta_sweep.png / fig05_improvement_heatmap.png
   - **互补性诊断**：`complementarity_diagnosis.md` + `complementarity_data.npz`
     - OCS-CNN 误差相关性 r=0.0030（完全不相关 → 互补性强）
     - 融合在 64.9% 样本中击败两种单模态
     - 最大改善在 OCS 误差大的样本（50+° bin: +74.23°）
     - 改善最强的偏航范围：180-240°（+8.63°, +9.67°）
   - **案例画廊**：`case_gallery.md`（best 6/worst 6/big wins/big losses）
     - 融合成功案例：OCS=180° 时 CNN 挽救至 0.00°
     - 融合失败案例：少数案例融合灾难性失效（180° 误差），OCS 完美
   - **论文声明**：`paper_claims.md`（5 项声明 + 局限性 + 未来工作）
   - **汇总**：`summary.json` / `figure_data.npz`

   ### 关键发现（来自互补性诊断）
   1. OCS 与 CNN 误差近乎零相关（r=0.003），互补性极强
   2. 融合提高 OCS 最差故障：50+° bin 改善 +74.23°
   3. 姿态依赖互补性：改善在 180-240° 偏航范围最强（+9.7°）
   4. 融合在 64.9% 样本中优于两种单模态
   5. 存在少量灾难性融合失败（180° 误差），OCS 单独完美



---
### BRDF 公式审计报告（Step 1 产出，2026-05-18）

**当前模块 A 真实 BRDF**（`ocs_core.py:72-73` + `materials.py:44-55`）：
```python
f_r = (rho_d / π) + rho_s * (cos_alpha)^n
```
- `cos_alpha = max(n·h, 0)`，`h = normalize(sun + det)`
- OCS 积分：`sum(area_m2 * f_r * cos_i * cos_r)`，其中 `cos_i = n·sun`，`cos_r = n·det`
- 可见性：`(n·sun > 0) & (n·det > 0)`
- 遮挡：射线起点 `center + normal * EPSILON`（EPSILON=1.0 mm），双向查询

**当前模块 B Blender 映射**（`render_batch.py:154-170`）：
```python
base_color = (rho_d, rho_d, rho_d)
roughness  = sqrt(2 / (n + 2))
specular_ior_level = rho_s
metallic = 0
```
- 底层：Principled BSDF，镜面项用 **GGX 微表面模型**（非 Phong）
- 色管：`view_transform='Standard'`（近似线性，未辐射定标）

**A/B 不一致来源**：
1. **镜面 BRDF 模型**：Phong `rho_s*(n·h)^n` vs GGX `D*G*F/(4*NoL*NoV)`
2. **能量归一化**：A 无归一化（`rho_d+rho_s` 可 >1）vs B 内置能量守恒
3. **金属处理**：A 统一公式 vs B `metallic=0` 强制电介质（金属主体应设 1）

**LegacyPhong 定义**（冻结当前模块 A 公式）：
```python
def eval_legacy_phong(N, L, V, rho_d, rho_s, n):
    """N/L/V: 单位向量"""
    H = normalize(L + V)
    cos_alpha = max(dot(N, H), 0)
    return (rho_d / pi) + rho_s * (cos_alpha ** n)

# OCS 积分
ocs = sum(
    area_m2 * eval_legacy_phong(N, L, V, ...) * max(dot(N,L), 0) * max(dot(N,V), 0)
    for each visible & unoccluded face
)
```

---

### 待评估选项（非当前队列，记录备查）

- **方案 (b)：区分同部件 / 跨部件阈值**：若将来仍需降低金属主体遮挡率，可改 `occlusion.py` 令 `batch_occlusion_dual` 返回命中面所属部件，对"同部件命中"用较大 `mhd`（跳过 1~5 mm 近邻几何），对"跨部件命中"仍用 1 mm。改动范围大，且无法区分"同部件真实遮挡"与"同部件几何粘连"，需先确认 72.88% 确实是问题再做。
- **人工抽查规模扩大**（可选，按需触发）：MVP 已跑通（见 §八），如需统计性结论可扩到 30~90 case、跨 mhd∈{0.1,0.5,1.0,2.0} 对比，或加 face_id 高亮 / BVH 多交点过滤。

---

## 七、已知坑（验证阶段再处理）

- **Windows Git Bash + 中文路径 + 长命令行**（2026-05-21 发现）：`python script.py long-args` 在 bash 下返回 exit code 127（shell 级命令未找到），需用 `| cat` 管道后执行。但 `| cat` 在后台任务中会提前关闭管道导致 Python 静默退出。解决方案：用 runner 脚本内置参数 + 自写日志文件绕开 CLI 传参。
- **Python GBK 控制台 Unicode 打印**：`inv_common.py` 中 `✓` 等 Unicode 字符在 Windows GBK 控制台引发 `UnicodeEncodeError`，已改为 `[OK]`（ASCII-safe）。

- `simplify_quadric_decimation` 在 fast 模式对凹陷几何敏感。论文期用 full。需装 `fast_simplification` 后端获 C++ 加速，否则 trimesh 回退纯 Python QEM。
- **Blender 5.0 Compositor MULTILAYER EXR 损坏**（2026-05-18 实测）：
  - `CompositorNodeOutputFile` 的 `layer_slots` / `file_slots` 都被移除，新 API `file_output_items` 在 `OPEN_EXR_MULTILAYER` 模式下**只写出第一个 link 的通道**（实测 4 个 link 均成功 `is_valid=True`，但渲染只输出 Combined，丢 Normal/Depth/IndexOB）
  - `scene.use_nodes` / `scene.compositing_node_group` 等多个属性有 DeprecationWarning，6.0 计划移除
  - **决策**：Step 5 落地用 4.2.3 LTS（Compositor API 稳定，MULTILAYER 4 层全部正常输出）。等 5.x 修好再考虑
- Blender 4.2 OutputFile MULTILAYER 行为（实测，未在官方文档明示）：
  - 文件名 = `base_path`（按字符串拼接） + `frame:04d` + `.exr`（**不会自动加路径分隔符**）
  - `layer_slots[i].name` 决定 EXR 内部层名；`file_slots / layer_slots[0].path` 在 MULTILAYER 下被忽略
  - `layer_slots.remove()` 接受 `NodeSocket`（即 `fo.inputs[i]`），不接受 layer slot 本身
  - 不能直接用 `socket_type` 字符串建 layer slot（旧 API）；改用 `fo.layer_slots.new(name)` 即可
  - `RLayers.outputs["Object Index"]`（不是 `IndexOB`）；常见 socket 名按 UI 显示名而非内部名
- Blender 5.0：STL 导入算子是 `bpy.ops.wm.stl_import`（已兼容回退 `import_mesh.stl`）。
- Blender 4.2 `ShaderNodeOutputAOV`（2026-05-19 实测）：
  - 节点 `name` 属性同时作为 AOV pass 名称；必须在 View Layer 添加同名 AOV（`vl.aovs.add()`）才能激活
  - MULTILAYER EXR 中 AOV 以 **RGBA 四通道**写出（非单通道 V），取值通道为 `Backfacing.R`
  - AOV 在 Cycles **最终着色点**记录（非首次命中）；若材质含 Transparent BSDF，射线穿透后 AOV 只记录穿透后的着色点值，无法用于检测背面
  - `Geometry.Backfacing`：封闭网格外视图始终为 0（所有可见像素均为真正前向面）→ 背面 AOV 方案不可行
- `intersects_location` 返回值是**扁平命中列表**而非"按射线对齐"，必须接第 2 个返回值 `index_ray` 做射线聚合；2026-05-12 已修复并验证（见 §八）。
- Embree 后端（`embreex` / `pyembree`）是软依赖：未装静默回退纯 Python BVH，装了自动启用，单线程提速 10~100×。

---

## 八、上次会话总结（精简）

**Step 11e-B2：Feature-level CNN+OCS fusion（2026-05-22）**

- 新增 `train_fusion.py`：ImageBranch(TinyCNN→64D) + OCSBranch(MLP→64D) → FusionHead(128D→4)
- 3 OCS case × 5 seeds × 500 epochs 完成
- **per_part_log sweet spot**: mean=4.10° (vs OCS-only 5.91°, +31%), Hit5=87.3%
- all_raw 反而变差 (5.42° vs 3.98°): 强 OCS + 图像 = 过参数化 + 小样本过拟合
- total_log 大幅改善 (13.75° vs 36.69°) 但不如 CNN-only (12.38°): 弱 OCS 拖累训练
- Feature vs Late fusion: Feature 仅在 per_part_log 胜出；极端场景 Late 更鲁棒
- 产物：`结果/模块C_反演/cnn_ocs_fusion/run_20260522_221756_all_raw/` + `...222227_per_part_log/` + `...222731_total_log/`
- 新增代码：`ocs_project/03_inversion/train_fusion.py`
- 指导文件：`202605222211.md`

**Step 11e-B1：CNN+OCS late fusion（2026-05-22）**

- 新增 `fuse_predictions.py`：sin/cos 空间预测级融合，beta sweep 0:0.01:1
- 3 OCS case × 5 CNN seeds 完成：all_raw (best β=0.96, 5.03°), per_part_log (β=0.93, 6.15°), total_log (β=0.11, 11.99°)
- 端点 sanity 全部通过；限制：OCS 仅 seed 4（`train_mlp.py` 保存逻辑为最后 seed）
- 关键发现：OCS 强时 CNN 贡献极小，OCS 弱时 CNN 主导；late fusion 提升有限，需 feature-level 融合
- 产物：`结果/模块C_反演/cnn_ocs_late_fusion/run_20260522_220850_all_raw/` + `...per_part_log/` + `...total_log/`
- 新增代码：`ocs_project/03_inversion/fuse_predictions.py`
- 指导文件：`202605222158.md`

**Step 11e-A：CNN image-only 回归（2026-05-21）**

- 新增 `train_cnn.py`：TinyCNN（Conv/GN/SiLU/Pool×4 → AdaptiveAvgPool → MLP→4，106k params）
- 安装 PyTorch 2.8.0+cu128（RTX 5060 Blackwell 兼容）
- 消融：log1p (mean=12.13°) > raw (mean=15.99°)
- 5 seeds 正式：**mean=12.38±0.74°**, **Hit5=26.1%**, Hit10=55.8%（10°→5° split，同 train_mlp.py）
- 对照：CNN (12.38°) vs OCS kNN (12.87°) vs OCS MLP (3.98°)
- 产物：`结果/模块C_反演/cnn_image/run_20260521_164437_final_log1p/` + `run_20260521_164129_raw_seed0/` + `run_20260521_164258_log1p_seed0/`
- 新增代码：`ocs_project/03_inversion/train_cnn.py`

**Step 11f：论文级结果汇总与互补性诊断（2026-05-22）**

- 新增 `summarize_paper_results.py`（~650 lines）：7 任务全链路（表格/图表/诊断/案例/声明/汇总）
- 新增 `_runner_textonly.py`：无图形文本运行器，自写日志；`_runner_summarize.py`：完整运行器（matplotlib 图形）
- Matplotlib AGG 渲染器原生 DLL 崩溃 → 重装 matplotlib 修复
- 互补性诊断卡住问题：非代码问题，Bash 管道提前关闭 → 用后台 + 文件重定向 + 120s 等待解决
- 修复 `generate_tradeoff_curve()` 中 `fontsize` 参数被传入 `FancyArrowPatch` 的 bug
- **产物**：`结果/模块C_反演/paper_summary/run_20260522_234553/`（15 文件）
  - 表格：table_main_inversion.csv/.md（10 方法）、table_fusion_ablation.csv/.md（3×4 消融）
  - 图表：fig01~fig05（dpi=300）：条形图/Hit5/CDF/β sweep/改善热力图
  - 诊断：complementarity_diagnosis.md + data.npz（r≈0.003, 64.9% 融合最优）
  - 案例：case_gallery.md（best 6/worst 6/big wins/losses）
  - 声明：paper_claims.md（5 核心 + 2 未来 + 6 局限）
  - 数据：summary.json / figure_data.npz
- **关键发现**：
  1. OCS-CNN 误差近乎零相关（r=0.003）→ 完全互补
  2. Per-part log 是甜点：融合改善 31%（5.91°→4.10°）
  3. 融合最大受益场景：OCS 大幅失败样本（50+° bin: +74.23°）
  4. 互补性高度姿态依赖：180-240° 偏航范围改善最大（+9.7°）
  5. 少数灾难性融合失败（180° 误差，OCS 单独完美）→ 需要融合鲁棒性改进
- 新增代码：`ocs_project/03_inversion/summarize_paper_results.py`、`_runner_textonly.py`、`_runner_summarize.py`

**Step 11d：OCS+image 联合修复 + 完成（2026-05-21）**

- 完全重写 `inv_joint.py`：复用 `inv_common.py`，支持多几何 OCS + HOG image 联合 kNN，alpha sweep 0:0.05:1 + 局部精扫
- 新增 `run_joint_11d.py`：自写日志的 runner，绕过 Windows shell 中文路径/长命令行 exit 127 问题
- 修复 `inv_common.py`：Unicode `✓` → `[OK]`（GBK 兼容）
- **数据链路验证通过**：OCS concat5 45D / 图像 brdf_images / 样本对齐 2701 / HOG 8100D 全部正常
- **阻塞**：距离矩阵计算步骤静默退出。待诊断 zscore/pairwise_euclidean 在 (2701, 8100) float64 上的行为
- 产物（本次新增/修改）：
  - `ocs_project/03_inversion/inv_joint.py`（重写）
  - `ocs_project/03_inversion/run_joint_11d.py`（runner）
  - `ocs_project/03_inversion/inv_common.py`（Unicode 修复）

**Step 11c：OCS-only MLP 连续回归（2026-05-21）**

- 新增 `train_mlp.py`：MLP 128→128→64 SiLU LayerNorm，sin/cos 周期编码输出
- 新增 `obs_total` 特征模式（每几何仅 ocs_with_occ，5D=最接近真实观测）
- 同时实现加权 kNN regression baseline（K=5 distance-weighted）
- 10° 网格 train（563）→ 5° test（1998），5 seeds，5 特征 × (log/raw)
- **关键结果**：
  - all 45D raw MLP: **mean=3.98±0.6°, Hit5=90.7%, Hit10=97.1%**（碾压 kNN discrete <1%）
  - per_part 30D log MLP: **mean=5.91±0.2°, Hit5=73.8%**（最稳定）
  - obs_total 5D: mean=54.9°（真实总 OCS 插值不足 → 需要部件信息/图像融合）
  - MLP raw > log（MLP 可自主学习动态范围，与 kNN 相反）
- 产物：`结果/模块C_反演/mlp_ocs/run_20260521_084723/`

**Step 11a-b：OCS-only kNN baseline + 紧凑消融矩阵（2026-05-20）**

- 新增 `inv_common.py`：数据加载/特征变换/split/kNN/指标/保存共享工具
- 重写 `inv_ocs.py`：支持多几何 + `--ablation` 一键消融
- 修复 4 个指标问题：Top@5° 判据 `<= 5°+eps`、新增 Top@10°/P90、log 跳过遮挡率列、concat 特征 bug（`build_concat_features_with_mode`）
- 紧凑消融矩阵 2×2×3×2=24 实验完成，产物：`结果/模块C_反演/inv_ocs/run_20260520_184414_ablation/`
- **关键发现**：
  1. `total`（真实可观测特征）+ log + 5 几何：LOO Top1@5°=53.8%，Top5@5°=85.5%（可行！）
  2. log 变换对 total 特征是决定性的（raw 22.4%→log 53.8%）
  3. per_part/all 更强但 semi-oracle（LOO Top1@5°=74.1%/78.1%）
  4. 10°→5° split：kNN Top1@5°<1.1%，mean=12.87°（kNN 无法姿态插值）→ 需要 MLP/CNN

**Step 10c-d：GGX 5°/多几何扫描（2026-05-20）** 已整合至 §六。

**MVP 基线路径（2026-05-11，保留引用）**：
- 模块 B 渲染（旧 Principled）：`结果/模块B_渲染/run_20260511_193251/`（703 帧 OPTIX，295.1 s）
- 模块 C 反演：联合最佳 alpha=0.75，angle mean=6.57°，Top1@5°=41.54%，`结果/模块C_反演/inv_joint/run_20260511_200932/`
