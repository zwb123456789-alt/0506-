# 29 1C-E12 Phase 0 Step 7 全量前规划与风险清单（Claude执行报告）

生成时间：2026-06-24  
任务编号：1C-E12  
执行端：Claude  
审阅状态：待Codex审阅

---

## 一、任务概述

### 1.1 任务定位

本任务为 Phase 0 Step 7：全量 2664 姿态生成前的规划与风险评估。**不进入全量生成**，只输出规划清单与候选任务拆分。

### 1.2 依据文件

- `CLAUDE.md` §1.1（执行环境与命令规则）
- `R27_Codex_审阅_1C-E11-FIX01通过并放行Phase0_Step6.md`
- `13_v0.4前向模型冻结规范_最终冻结版.md`
- `14_v0.4数据与manifest字段规范_最终冻结版.md`
- `06_v0.4_code/05_postprocess/run_phase0_step6_small_trial.py`
- `v0.4_results/00_validation/phase0_step6_small_trial/phase0_step6_small_trial_summary.json`

### 1.3 Phase 0 Step 6 已完成项确认

根据 Step 6 summary 和 R27 审阅：

| 项目 | 状态 | 说明 |
|---|---|---|
| B0 BRDF/image 后处理模块 | ✅ 已建立 | `image_response_v0_4.py`, `ocs_integration_v0_4.py` |
| OCS 积分模块 | ✅ 已建立 | `compute_ocs_from_brdf_response()` |
| 5 姿态 small-run | ✅ 已完成 | yaw180/150/000/090/300, pitch +000/+025/+000/+000/-025 |
| 四类像素统计 | ✅ 已输出 | camera_visible, nol_positive, sun_visible, contributing |
| I_scale 策略 | ✅ 已确定 | 固定复用 Step 5 值 0.544（small-run 用） |
| pixel_area_m2 对齐 | ✅ 已修正 | ortho_scale = 2.2 × r_max |
| linear EXR 输出 | ✅ 已验证 | 含 V_sun_macro 的 I_linear |
| log1p PNG 输出 | ✅ 已验证 | α=10.0, 8-bit 训练输入 |
| per-frame OCS JSON | ✅ 已验证 | ocs_total, ocs_per_part, 像素统计 |

### 1.4 边界声明

- 本任务**不进入全量 2664 姿态生成**
- 本任务**不训练模型**
- 本任务**不改写论文正文**
- 本任务**不修改 CLAUDE.md、13/14 冻结文件**
- 本任务输出需经 Codex 审阅通过后才能放行 Phase 1

---

## 二、全量前缺口清单

### 2.1 数据生成缺口

| 编号 | 缺口项 | 当前状态 | 影响 |
|---|---|---|---|
| G1 | 全量 2664 姿态 camera-view EXR | 只有 Step 4/5 的 25 姿态 | 阻塞全量 OCS/image 生成 |
| G2 | 全量 2664 姿态 sun-view depth EXR | 只有 Step 4 的 20 姿态 | 阻塞全量 V_sun_macro 生成 |
| G3 | 全量 2664 姿态 V_sun_macro_mask | 只有 Step 4 的 20 姿态 | 阻塞全量 BRDF 后处理 |
| G4 | 全量 2664 姿态 BRDF/OCS/image 后处理产物 | 只有 Step 6 的 5 姿态 | 阻塞 manifest 生成 |

### 2.2 工具链缺口

| 编号 | 缺口项 | 功能 | 优先级 |
|---|---|---|---|
| T1 | Manifest builder | 从 per-frame OCS JSON 汇总成 ocs_manifest_v0.4.json | P0（必做） |
| T2 | Image manifest builder | 从 BRDF 后处理产物生成 image_manifest_v0.4.json | P0（必做） |
| T3 | Manifest consistency checker | 14 号 §8.1 的六项一致性检查 | P0（必做） |
| T4 | Corpus-level I_scale calculator | 扫描全量 linear EXR 计算全局最大值 | P0（必做） |
| T5 | Split file generator | 生成 train/val/test split JSON（coarse-to-fine） | P0（必做） |
| T6 | Batch render orchestrator | 全量 2664 姿态 Blender 渲染调度（断点续传） | P1（推荐） |
| T7 | Batch postprocess orchestrator | 全量 2664 姿态 BRDF 后处理调度 | P1（推荐） |

### 2.3 BRDF 分支缺口

| 编号 | 分支 | 当前状态 | 路线一 C 定位 |
|---|---|---|---|
| B0 | phong_like_provisional_baseline | ✅ Step 6 已验证 | 工程 smoke test / 兜底 baseline |
| B1 | 书中改进冯模型 | ❌ 尚未实现 | **主线 Method 优先目标**（需确认公式） |
| B2 | GGX Cook-Torrance | ❌ 尚未实现 | 对照与 mismatch 分支 |

### 2.4 Multi-Geom 扩展缺口

当前只实现 single-geom phase63。Multi-geom concat5（其余 4 组 sun/det）暂未实现，根据 14 号 §1.3 属于"第二层扩展"，不阻塞 Phase 1。

### 2.5 训练链缺口

| 编号 | 缺口项 | 说明 |
|---|---|---|
| TR1 | OCS-only MLP 训练脚本 | 未准备 |
| TR2 | Image-only ResNet-18 训练脚本 | 未准备 |
| TR3 | Fusion (concat1) 训练脚本 | 未准备 |
| TR4 | 退化实验脚本 | 未准备 |

---

## 三、Step 7 候选任务拆分

### 3.1 Phase 0 后续步骤（全量生成前）


#### Step 7a: Manifest Builder + Consistency Checker（工具链验证）

**目标**：在 Step 6 的 5 姿态产物上验证 manifest 工具链。

**输入**：
- Step 6 的 5 个 per-frame OCS JSON
- Step 6 的 5 个 linear EXR + log1p PNG
- Step 4/5 的 camera/sun 矩阵、depth_epsilon_m_final

**输出**：
- `ocs_manifest_v0.4_step6trial.json`（5 records）
- `image_manifest_v0.4_step6trial.json`（5 records）
- manifest consistency check 通过报告

**验收标准**：
1. OCS manifest 包含 14 号 §3.1 的所有必需字段
2. Image manifest 包含 14 号 §3.2 的所有必需字段
3. Consistency checker 验证六项一致性（14 号 §8.1）通过
4. `record_id` 跨 manifest 对齐无误

**工具清单**：
- `build_ocs_manifest_v0_4.py`
- `build_image_manifest_v0_4.py`
- `check_manifest_consistency_v0_4.py`

#### Step 7b: Corpus-Level I_scale 计算流程确定

**目标**：明确全量 corpus-level I_scale 的计算与冻结流程。

**流程设计**：
1. 全量 2664 姿态 BRDF 后处理完成后
2. 运行 `compute_corpus_i_scale.py`，扫描所有 `*_linear.exr` 的全局最大值
3. 记录为 `I_scale_corpus`（预期量级 ~0.5-1.0）
4. 写入 image manifest 的 `preprocessing.I_scale`
5. 用 `I_scale_corpus` 重新生成所有 log1p PNG（覆盖原 PNG）
6. 冻结 `I_scale_corpus`，后续不再修改
7. 所有训练实验从冻结后的 PNG 读取

**注意事项**：
- 当前 Step 6 使用的 `i_scale_smallrun = 0.544` 只是 Step 5 的 5 姿态最大值，**不能用于全量**
- `I_scale_corpus` 必须在全量 BRDF 后处理完成后计算，不能提前估算
- 计算后必须重新生成 PNG，确保所有训练输入使用同一 I_scale

#### Step 7c: B0 全量生成资源评估与失败恢复策略

**目标**：评估 B0 全量 2664 姿态生成的资源需求与风险。

**资源评估**：见 §4。

**失败恢复策略**：见 §5。

### 3.2 Phase 1: B0 Baseline 全量生成与训练

#### Phase 1 Step 1: 全量 2664 姿态 Blender 渲染

**范围**：
- 2664 姿态 × camera-view EXR（Normal/Depth/IndexOB/Position）
- 2664 姿态 × sun-view depth EXR

**工具**：
- `render_batch_camera_view.py`（调度 Blender 批量渲染）
- `render_batch_sun_view.py`（调度 Blender 批量渲染）

**验收**：
- 所有 EXR 文件存在且完整（depth < 1e9 像素数 > 0）
- 渲染日志记录所有失败姿态

#### Phase 1 Step 2: 全量 2664 姿态 Sun Shadow Reprojection

**范围**：
- 2664 姿态 × V_sun_macro_mask（uint8 0/1）

**工具**：
- 复用 Step 4 的 `validate_sun_shadow.py` 逻辑
- 新增 `batch_sun_shadow_reprojection.py`

**验收**：
- 所有 V_sun_macro_mask 生成成功
- 像素统计合理（n_pixels_sun_visible 在合理范围）

#### Phase 1 Step 3: 全量 2664 姿态 BRDF/OCS/Image 后处理

**范围**：
- 2664 姿态 × (linear EXR + per-frame OCS JSON)

**工具**：
- 复用 Step 6 的 `image_response_v0_4.py` 和 `ocs_integration_v0_4.py`
- 新增 `batch_brdf_postprocess.py`

**验收**：
- 所有 linear EXR 和 OCS JSON 生成成功
- 四类像素统计已输出

#### Phase 1 Step 4: Corpus-Level I_scale 计算与 PNG 生成

**范围**：
- 计算 `I_scale_corpus`
- 生成 2664 姿态 × log1p PNG

**工具**：
- `compute_corpus_i_scale.py`
- `batch_generate_log1p_png.py`

**验收**：
- `I_scale_corpus` 已冻结
- 所有 PNG 使用同一 I_scale

#### Phase 1 Step 5: Manifest 生成与一致性检查

**范围**：
- `ocs_manifest_v0.4.json`（2664 records）
- `image_manifest_v0.4.json`（2664 records）

**工具**：
- Step 7a 验证的 manifest builder 和 consistency checker

**验收**：
- Manifest 一致性检查通过
- 所有 2664 records 的 `record_id` 对齐

#### Phase 1 Step 6: Split 文件生成

**范围**：
- `split_ctf_v1.json`（coarse-to-fine, train/val/test）

**工具**：
- `generate_split_coarse_to_fine.py`

**验收**：
- Split 文件符合 14 号 §6.2 规范
- Train/val/test 无重叠

#### Phase 1 Step 7: B0 OCS-Only / Image-Only / Fusion 训练

**范围**：
- B0 OCS-only MLP 训练
- B0 image-only ResNet-18 训练
- B0 fusion (concat1) 训练

**工具**：
- `train_ocs_only.py`
- `train_image_only.py`
- `train_fusion.py`

**验收**：
- 训练完成，生成 summary.json
- source_data.json 记录完整
- 一致性检查通过

### 3.3 Phase 2: B1 主线 Method（待确认）

**前置条件**：作者确认书籍改进冯模型公式与材料对应关系。

**范围**：
- B1 BRDF 模块实现
- 复用 Phase 1 的 geometry/shadow passes
- 重新运行 BRDF 后处理、I_scale 计算、manifest 生成、训练

### 3.4 Phase 3: GGX 对照（可选）

**范围**：
- GGX BRDF 模块实现
- 复用 Phase 1 的 geometry/shadow passes
- 重新运行 BRDF 后处理、I_scale 计算、manifest 生成、训练

---

## 四、Corpus-Level I_scale 计算流程

### 4.1 流程图

```text
全量 2664 姿态 BRDF 后处理完成
    ↓
运行 compute_corpus_i_scale.py
    扫描所有 *_linear.exr
    计算全局 max(I_linear)
    ↓
I_scale_corpus = max(I_linear)
    ↓
写入 image_manifest.preprocessing.I_scale
    ↓
用 I_scale_corpus 重新生成所有 log1p PNG
    ↓
冻结 I_scale_corpus（不再修改）
    ↓
所有训练从冻结 PNG 读取
```

### 4.2 I_scale 策略

根据 13 号 §8.2：

```
I_scale = v0.4 clean corpus 全局最大 I_linear 值
```

- **全局归一化**：所有姿态使用同一 I_scale
- **不使用 per-frame normalization**（Step 6 已确认此策略）
- **预期量级**：~0.5-1.0（基于 Step 5 的 i_scale_step5 = 0.544）

### 4.3 实现工具

`compute_corpus_i_scale.py`：

```python
import numpy as np
import OpenEXR
import Imath
from pathlib import Path

def compute_corpus_i_scale(linear_exr_dir):
    """扫描所有 linear EXR，计算全局最大值"""
    max_i_linear = 0.0
    for exr_path in Path(linear_exr_dir).glob("*_linear.exr"):
        exr_file = OpenEXR.InputFile(str(exr_path))
        header = exr_file.header()
        dw = header['dataWindow']
        size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
        
        # 读取 R 通道（假设 I_linear 存储在 R）
        r_str = exr_file.channel('R', Imath.PixelType(Imath.PixelType.FLOAT))
        r = np.frombuffer(r_str, dtype=np.float32).reshape(size[1], size[0])
        
        max_i_linear = max(max_i_linear, np.max(r))
    
    return max_i_linear
```

---

## 五、B0/B1/GGX 分支顺序建议

### 5.1 路线一 C 定位回顾

根据 CLAUDE.md §3：

```text
路线一 C = 必选主干，v0.4 pixel-level 同源架构 
         + B1 书中改进冯模型待确认主线 
         + B0 工程 baseline 
         + GGX 对照
```

### 5.2 分支顺序建议

| 阶段 | 分支 | 定位 | 理由 |
|---|---|---|---|
| **Phase 1** | **B0** | 工程 smoke test / 兜底 baseline | Step 6 已验证，可立即进入全量；验证全链路正确性 |
| **Phase 2** | **B1** | **主线 Method 优先目标** | 需等待作者确认书籍公式；确认后作为正式 Method |
| **Phase 3** | **GGX** | 对照与 mismatch 分支 | B0/B1 完成后再决定是否需要 |

### 5.3 B0 → B1 → GGX 的优势

1. **工程风险控制**：B0 先跑通全链路，发现 manifest/训练/一致性检查的潜在问题
2. **资源优化**：B1/GGX 可复用 B0 的 geometry/shadow passes，只需重新运行 BRDF 后处理
3. **科学主线清晰**：B1 确认后作为主线 Method，B0 作为兜底，GGX 作为对照
4. **时间管理**：B0 不阻塞 B1 公式确认，可并行推进

---

## 六、全量生成资源与失败恢复策略

### 6.1 资源评估

#### 6.1.1 计算资源

| 项目 | 单姿态耗时 | 总耗时（2664 姿态） | 说明 |
|---|---|---|---|
| Camera-view EXR 渲染 | 1-5 min | 44-220 小时 | 取决于 Blender Cycles 采样数 |
| Sun-view depth EXR 渲染 | 1-5 min | 44-220 小时 | 同 camera-view |
| Sun shadow reprojection | <10 s | <7.4 小时 | Python 后处理 |
| BRDF/OCS 后处理 | <10 s | <7.4 小时 | Python 后处理 |
| **总计（串行）** | **2-10 min** | **88-440 小时 = 4-18 天** | 不含训练 |

#### 6.1.2 存储资源

| 项目 | 单姿态大小 | 总大小（2664 姿态） |
|---|---|---|
| Camera-view EXR | ~10 MB | ~26 GB |
| Sun-view depth EXR | ~10 MB | ~26 GB |
| V_sun_macro_mask (NPY) | ~64 KB | ~170 MB |
| Linear EXR | ~10 MB | ~26 GB |
| Log1p PNG | ~100 KB | ~266 MB |
| Per-frame OCS JSON | ~2 KB | ~5.3 MB |
| **总计** | **~30 MB** | **~78 GB** |

#### 6.1.3 并行化潜力

- **Blender 渲染**：可并行（每个姿态独立）
- **Python 后处理**：可并行（每个姿态独立）
- **瓶颈**：GPU 数量（Blender Cycles）、CPU 核心数（Python 后处理）

若 4 GPU 并行 Blender 渲染，总耗时可缩短至 **1-4.5 天**。

### 6.2 失败恢复策略

#### 6.2.1 分批处理


**策略**：每 100 姿态一批，生成 checkpoint。

**实现**：
```python
for batch_id, attitudes in enumerate(batch_iterator(all_attitudes, batch_size=100)):
    render_batch(attitudes, batch_id)
    validate_batch(batch_id)
    checkpoint_batch(batch_id)
```

**优势**：
- 单批失败不影响其他批
- 可分批提交到不同 GPU
- 便于进度跟踪

#### 6.2.2 断点续传

**策略**：检查已存在的 EXR，跳过已完成姿态。

**实现**：
```python
def render_batch_with_resume(attitudes, output_dir):
    for att in attitudes:
        exr_path = output_dir / f"{att.label}_camera.exr"
        if exr_path.exists() and validate_exr(exr_path):
            print(f"[SKIP] {att.label} already rendered")
            continue
        render_attitude(att, output_dir)
```

**优势**：
- 脚本中断后可从断点继续
- 避免重复渲染

#### 6.2.3 失败日志

**策略**：记录每个失败姿态的错误信息。

**实现**：
```python
failed_attitudes = []
for att in attitudes:
    try:
        render_attitude(att)
    except Exception as e:
        failed_attitudes.append({"attitude": att.label, "error": str(e)})

with open("failed_attitudes.json", "w") as f:
    json.dump(failed_attitudes, f, indent=2)
```

**优势**：
- 便于定位问题姿态
- 可单独重跑失败姿态

#### 6.2.4 验证机制

**策略**：每批完成后验证 EXR 完整性。

**验证项**：
1. EXR 文件存在
2. 文件大小 > 0
3. 可正常打开
4. depth < 1e9 像素数 > 0（非空场景）
5. IndexOB > 0 像素数 > 0（目标可见）

**实现**：
```python
def validate_exr(exr_path):
    if not exr_path.exists():
        return False, "File not found"
    if exr_path.stat().st_size == 0:
        return False, "Empty file"
    try:
        exr_file = OpenEXR.InputFile(str(exr_path))
        depth = read_depth_pass(exr_file)
        n_object_pixels = np.sum(depth < 1e9)
        if n_object_pixels == 0:
            return False, "No object pixels"
        return True, "OK"
    except Exception as e:
        return False, str(e)
```

#### 6.2.5 备份策略

**策略**：每完成一批，备份到另一目录。

**实现**：
```bash
rsync -av --progress v0.4_results/00_geometry_passes/ /backup/00_geometry_passes/
```

**优势**：
- 防止意外删除
- 便于回滚

### 6.3 风险清单与缓解措施

| 风险编号 | 风险描述 | 严重度 | 缓解措施 |
|---|---|---|---|
| R1 | Blender 渲染中途崩溃 | 高 | 分批处理 + 断点续传 |
| R2 | 磁盘空间不足（78 GB） | 中 | 提前清理旧结果 + 监控磁盘 |
| R3 | 某些极端姿态渲染失败 | 中 | 失败日志 + 单独重跑 |
| R4 | EXR 文件损坏 | 低 | 验证机制 + 备份 |
| R5 | Python 后处理内存溢出 | 低 | 逐姿态处理（不批量加载） |
| R6 | I_scale 计算错误 | 低 | 人工抽查 max I_linear 合理性 |
| R7 | Manifest 字段缺失 | 高 | Step 7a 先验证 5 姿态 |
| R8 | OCS/image 版本混用 | 高 | 一致性检查 mandatory |


---

## 七、Manifest Builder / Consistency Checker 是否必须先做

### 7.1 判断结论

**必须先做**（在 Phase 0 Step 7a）。

### 7.2 理由

#### 理由 1：统一前向模型的可追踪性保障

14 号 §2（CR5-001 新增立论）强调：

> v0.4 是统一前向模型，OCS、image、fusion、退化实验、multi-geom 扩展全部来自同一条物理链路的不同读出。任何一处的几何、BRDF、可见性、OCS 积分、图像预处理或数据划分发生变化，都会同时影响多个模态的结果。

Manifest 是唯一能证明"OCS 与 image 同源"的机制。没有 manifest，就无法证明某个 fusion 结果用的 OCS 和 image 来自同一 visibility 层级、同一 BRDF 版本。

#### 理由 2：禁止 Latest-Run 自动发现

14 号 §7 明确禁止：

```python
# 禁止
manifest = sorted(glob.glob(MANIFEST_GLOB), key=os.path.getmtime, reverse=True)[0]
```

所有训练脚本必须显式传入 manifest 路径。如果没有 manifest builder，就无法生成训练入口。

#### 理由 3：一致性检查是防止混用的唯一保障

14 号 §8.1 列出六项一致性检查：

```
ocs_manifest.geometry_version       == image_manifest.geometry_version
ocs_manifest.brdf_version           == image_manifest.brdf_version
ocs_manifest.visibility_version     == image_manifest.visibility_version
ocs_manifest.sun_visibility         == image_manifest.sun_visibility
ocs_manifest.shadow_mapping_method  == image_manifest.shadow_mapping_method
```

如果在全量 2664 姿态生成后才发现一致性检查失败，代价极高。

#### 理由 4：Step 7a 可用 5 姿态低成本验证

Step 6 已有 5 姿态的 per-frame OCS JSON 和 image 产物，可以：
1. 先在 5 姿态上验证 manifest builder 正确性
2. 先在 5 姿态上验证 consistency checker 逻辑
3. 发现字段缺失或格式错误时，修正成本极低（只需改代码，不需重跑 2664 姿态）

### 7.3 Step 7a 具体任务

#### 任务 7a-1：实现 OCS Manifest Builder

**输入**：
- Step 6 的 5 个 per-frame OCS JSON
- Step 4/5 的 camera/sun 矩阵、depth_epsilon_m_final、r_max、ortho_scale_m

**输出**：
- ocs_manifest_v0.4_step6trial.json（5 records）

**必需字段**（14 号 §3.1）：
- geometry_version, brdf_version, visibility_version, ocs_integration_version
- sun_visibility, shadow_mapping_method, depth_epsilon_m
- 每个 record：record_id, yaw_deg, pitch_deg, geom_id, sun_dir, det_dir
- 每个 record：ocs_total, ocs_per_part, 四类像素统计
- 每个 record：camera_exr_path, sun_depth_exr_path, sun_visibility_mask_path
- 每个 record：camera_matrix_world, sun_camera_matrix_world

#### 任务 7a-2：实现 Image Manifest Builder

**输入**：
- Step 6 的 5 个 linear EXR + log1p PNG
- i_scale_smallrun, log1p_alpha

**输出**：
- image_manifest_v0.4_step6trial.json（5 records）

**必需字段**（14 号 §3.2）：
- geometry_version, brdf_version, visibility_version, image_preprocess_version
- sun_visibility, shadow_mapping_method（CR5-004 新增到 image 侧）
- preprocessing.log1p_alpha, preprocessing.I_scale, preprocessing.v_sun_macro_mode
- 每个 record：record_id, yaw_deg, pitch_deg, geom_id, png_path, exr_linear_path

#### 任务 7a-3：实现 Manifest Consistency Checker

**输入**：
- ocs_manifest_v0.4_step6trial.json
- image_manifest_v0.4_step6trial.json

**输出**：
- 一致性检查报告（PASS / FAIL + 具体错误）

**检查项**（14 号 §8.1）：
1. geometry_version 一致
2. brdf_version 一致
3. visibility_version 一致
4. sun_visibility 一致
5. shadow_mapping_method 一致
6. v_sun_macro_mode 与 sun_visibility 对应关系正确
7. 所有 record_id 在两个 manifest 中对齐

#### 任务 7a-4：Step 6 产物验证

在 5 姿态上运行上述三个工具，确保：
- Manifest 生成无错误
- 所有字段完整
- 一致性检查通过

**验收标准**：
- ocs_manifest_v0.4_step6trial.json 包含 5 records，所有字段符合 14 号 §3.1
- image_manifest_v0.4_step6trial.json 包含 5 records，所有字段符合 14 号 §3.2
- Consistency check 报告 PASS


---

## 八、不进入全量生成的边界声明

### 8.1 Phase 0 Step 7 边界

本任务（1C-E12）为 Phase 0 Step 7，**只输出规划清单，不执行全量生成**。

### 8.2 Phase 1 入口条件

进入 Phase 1（全量 2664 姿态生成）的前置条件：

1. **Phase 0 Step 7a 完成**：manifest builder 和 consistency checker 在 5 姿态上验证通过
2. **Codex 审阅 1C-E12 通过**：本报告经 Codex 审阅，确认规划合理、无遗漏缺口
3. **作者明确放行**：作者确认可以进入全量生成
4. **资源准备就绪**：磁盘空间（≥100 GB）、GPU 可用、备份目录已建立

### 8.3 禁止事项（重申）

在 Phase 0 Step 7 阶段：

- 不得进入全量 2664 姿态 Blender 渲染
- 不得运行全量 BRDF 后处理
- 不得计算 corpus-level I_scale（需全量数据）
- 不得生成 full manifest（只有 5 姿态 trial manifest）
- 不得训练模型
- 不得改写论文正文

---

## 九、Phase 0 Step 7 后续执行建议

### 9.1 立即可执行（Phase 0 Step 7a）

在 Codex 审阅本报告前，Claude 可先执行：

**任务**：Step 7a 的三个工具实现 + 5 姿态验证。

**理由**：
- Step 7a 使用已有的 Step 6 产物，不涉及新数据生成
- 工具实现是纯代码任务，不触碰红线
- 验证通过后，Phase 1 可直接复用这些工具

**输出**：
- build_ocs_manifest_v0_4.py
- build_image_manifest_v0_4.py
- check_manifest_consistency_v0_4.py
- ocs_manifest_v0.4_step6trial.json（5 records）
- image_manifest_v0.4_step6trial.json（5 records）
- Consistency check 报告

### 9.2 等待 Codex 审阅（本报告）

**审阅重点**：
1. 全量前缺口清单是否完整
2. Step 7a/7b/7c 任务拆分是否合理
3. B0 → B1 → GGX 顺序是否符合路线一 C 定位
4. 资源评估与失败恢复策略是否可行
5. Manifest builder 必须先做的理由是否充分

### 9.3 Codex 审阅通过后

**下一步**：
- 若 Codex 批准立即执行 Step 7a → Claude 执行 1C-E13（Step 7a 工具实现）
- 若 Codex 要求补充规划 → Claude 根据 Codex 反馈修订本报告
- 若 Codex 批准进入 Phase 1 → 等待作者明确放行指令

---

## 十、总结

### 10.1 全量前缺口清单（5 大类）

1. **数据生成缺口**（G1-G4）：全量 2664 姿态 EXR 和后处理产物
2. **工具链缺口**（T1-T7）：manifest builder、consistency checker、I_scale calculator、split generator、batch orchestrator
3. **BRDF 分支缺口**（B1/B2）：书中改进冯模型、GGX 尚未实现
4. **Multi-geom 缺口**：concat5 扩展暂未实现（不阻塞 Phase 1）
5. **训练链缺口**（TR1-TR4）：OCS-only/image-only/fusion 训练脚本未准备

### 10.2 Step 7 候选任务拆分

- **Phase 0 Step 7a**：manifest builder + consistency checker（5 姿态验证）
- **Phase 0 Step 7b**：corpus-level I_scale 计算流程确定
- **Phase 0 Step 7c**：B0 全量生成资源评估
- **Phase 1**：B0 全量生成与训练（7 个 sub-steps）
- **Phase 2**：B1 主线 Method（待确认）
- **Phase 3**：GGX 对照（可选）

### 10.3 关键判断

1. **Manifest builder / consistency checker 必须先做**（在 Phase 0 Step 7a）
2. **Corpus-level I_scale 必须全量后计算**（不能提前估算）
3. **B0 → B1 → GGX 顺序符合路线一 C 定位**（B0 工程兜底，B1 主线，GGX 对照）
4. **全量生成资源需求**：88-440 小时（串行）/ 78 GB 存储
5. **失败恢复策略**：分批处理 + 断点续传 + 失败日志 + 验证机制 + 备份

### 10.4 不进入全量生成边界

- Phase 0 Step 7 只做规划，不执行全量生成
- Phase 1 入口需：Step 7a 完成 + Codex 审阅通过 + 作者明确放行

---

## 十一、附录：文件清单

### 11.1 已有文件（Phase 0 Step 6 产物）

```
06_v0.4_code/05_postprocess/image_response_v0_4.py
06_v0.4_code/05_postprocess/ocs_integration_v0_4.py
06_v0.4_code/05_postprocess/run_phase0_step6_small_trial.py
v0.4_results/00_validation/phase0_step6_small_trial/
  yaw180_pitch+000_roll+000_linear.exr
  yaw180_pitch+000_roll+000_brdf.png
  yaw180_pitch+000_roll+000_ocs.json
  (其余 4 姿态)
  phase0_step6_small_trial_summary.json
```

### 11.2 待生成文件（Phase 0 Step 7a）

```
06_v0.4_code/06_manifest/
  build_ocs_manifest_v0_4.py
  build_image_manifest_v0_4.py
  check_manifest_consistency_v0_4.py

v0.4_results/00_validation/phase0_step7a_manifest_trial/
  ocs_manifest_v0.4_step6trial.json
  image_manifest_v0.4_step6trial.json
  consistency_check_report.json
```

### 11.3 待生成文件（Phase 1）

```
06_v0.4_code/07_batch_render/
  render_batch_camera_view.py
  render_batch_sun_view.py
  batch_sun_shadow_reprojection.py
  batch_brdf_postprocess.py

06_v0.4_code/08_corpus_tools/
  compute_corpus_i_scale.py
  batch_generate_log1p_png.py

06_v0.4_code/09_split/
  generate_split_coarse_to_fine.py

06_v0.4_code/10_training/
  train_ocs_only.py
  train_image_only.py
  train_fusion.py

v0.4_results/
  00_geometry_passes/phase63/  (2664 EXR)
  00b_sun_depth_passes/phase63/  (2664 EXR)
  01_sun_shadow_reprojection/phase63/  (2664 NPY)
  02_brdf_postprocess/phase63/  (2664 EXR + PNG + JSON)
  03_manifests/
    ocs_manifest_v0.4.json
    image_manifest_v0.4.json
  04_splits/
    split_ctf_v1.json
  05_runs/
    run_B0_ocs_only/
    run_B0_image_only/
    run_B0_fusion/
```

---

**报告结束**

**生成时间**：2026-06-24  
**执行端**：Claude  
**任务编号**：1C-E12  
**输出路径**：04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/29_1C-E12_Phase0_Step7_全量前规划与风险清单_Claude执行报告.md

**下一步**：
- 等待 Codex 审阅本报告
- 若批准，执行 1C-E13（Phase 0 Step 7a 工具实现）
