# 27 1C-E11 Phase 0 Step 6 BRDF/OCS/image 后处理模块化试跑 — Claude 执行报告

生成时间：2026-06-23  
任务编号：1C-E11  
执行端：Claude  
依据：R26 Codex 审阅（Phase 0 Step 5 通过并放行 Step 6）

---

## 1. 执行总结

### 1.1 状态

```text
Phase 0 Step 6: COMPLETE
```

5 个试跑姿态全部完成 BRDF/OCS/image 后处理，产物可读，统计字段完整，无阻断项。

### 1.2 本轮范围

- **试跑姿态**：复用 Step 5 的 5 个姿态（yaw000/yaw090/yaw150/yaw180/yaw300）
- **BRDF 分支**：B0 phong_like_provisional_baseline（工程 baseline）
- **输入**：复用 Step 4 的 camera/sun EXR，未重渲染
- **输出**：每姿态生成 I_linear.exr + log1p PNG + per-frame OCS JSON + 四类像素统计
- **I_scale 策略**：固定使用 Step 5 的 `i_scale_step5 = 0.5444863931551639`，无 per-frame normalization

### 1.3 本轮边界

- **明确标注**：本轮是 **B0 small-run**，不是全量 corpus，不是训练输入最终 manifest
- **未进入**：全量 2664 姿态生成、训练、论文改写、冻结文件修改
- **BRDF 状态**：B0 作为工程 baseline，GGX 对照分支和 B1 书中改进冯模型待后续升级

---

## 2. 实现内容

### 2.1 模块化后处理代码

创建了两个独立后处理模块：

#### 2.1.1 图像响应模块

```text
06_v0.4_code/05_postprocess/image_response_v0_4.py
```

核心功能：
- `compute_brdf_response()`: 从 camera/sun EXR 计算 BRDF 响应
  - 读取 Position/Depth/Normal/IndexOB passes
  - 生成 V_sun_macro（复用 Step 5 的 sun shadow reprojection）
  - 计算 NoL/NoV 并过滤有效像素（NoV > eps AND NoL > eps）
  - 逐像素计算 f_r（B0 phong-like，按 IndexOB 映射部件材料）
  - 计算 `I_linear = f_r · NoL · V_sun_macro`（13 §8.2 / CR4-001）
  - 返回四类像素统计（CR4-006）
- `apply_log1p_transform()`: 应用 log1p 变换（13 §8.2 Step 3）
- `write_image_outputs()`: 写出 I_linear.exr + log1p PNG

遵循规范：
- 13 号 §8.2（图像响应链）
- 13 号 §9.2（有效像素规则：NoV > 1e-6 AND NoL > 1e-6）
- 14 号 §3.2（image manifest 字段）

#### 2.1.2 OCS 积分模块

```text
06_v0.4_code/05_postprocess/ocs_integration_v0_4.py
```

核心功能：
- `compute_ocs_from_brdf_response()`: 从 BRDF 响应积分 OCS
  - 识别贡献像素（valid_response AND V_sun_macro == 1）
  - 计算 OCS 总量：`OCS = Σ A_pixel · I_linear`
  - 按 IndexOB 拆分 per-part OCS 和像素数
  - 返回四类像素统计
- `write_ocs_json()`: 写出 per-frame OCS JSON（符合 14 号 manifest record 格式）

遵循规范：
- 13 号 §6.2（OCS 公式）
- 14 号 §3.1（ocs_manifest 字段：record_id / 四类像素统计 / per-part OCS）

### 2.2 Phase 0 Step 6 主执行脚本

```text
06_v0.4_code/05_postprocess/run_phase0_step6_small_trial.py
```

执行流程：
1. 读取 Step 4/5 参数（r_max / depth_epsilon_m_final / i_scale_step5）
2. 对每个试跑姿态：
   - 调用 `compute_brdf_response()` 计算 BRDF 响应
   - 调用 `write_image_outputs()` 写出 I_linear.exr + log1p PNG
   - 调用 `compute_ocs_from_brdf_response()` 积分 OCS
   - 调用 `write_ocs_json()` 写出 per-frame OCS JSON
3. 生成总 summary JSON

---

## 3. 执行结果

### 3.1 产物路径

```text
v0.4_results/00_validation/phase0_step6_small_trial/
```

### 3.2 产物清单

每个姿态 3 个文件：

| 姿态 | I_linear EXR | log1p PNG | OCS JSON |
|---|---|---|---|
| yaw000_pitch+000_roll+000 | ✓ (5.3 KB) | ✓ (1.8 KB) | ✓ (552 B) |
| yaw090_pitch+000_roll+000 | ✓ (5.9 KB) | ✓ (1.8 KB) | ✓ (550 B) |
| yaw150_pitch+025_roll+000 | ✓ (7.7 KB) | ✓ (1.8 KB) | ✓ (553 B) |
| yaw180_pitch+000_roll+000 | ✓ (6.4 KB) | ✓ (1.8 KB) | ✓ (552 B) |
| yaw300_pitch-025_roll+000 | ✓ (6.2 KB) | ✓ (1.5 KB) | ✓ (556 B) |

总计：5 姿态 × 3 文件 = 15 个产物文件 + 1 个 summary JSON。

### 3.3 Summary 关键字段

```json
{
  "overall_status": "COMPLETE",
  "scope": "B0 small-run, NOT full corpus, NOT training input final manifest",
  "brdf_branch": "B0",
  "brdf_note": "B0 phong_like_provisional_baseline as engineering baseline",
  "depth_epsilon_m_final": 0.7952109582768545,
  "i_scale_smallrun": 0.5444863931551639,
  "i_scale_policy": "fixed = i_scale_step5 from Phase0 Step5; no per-frame normalization",
  "log1p_alpha": 10.0,
  "n_trial_attitudes": 5,
  "n_completed": 5,
  "blockers": []
}
```

路径：
```text
v0.4_results/00_validation/phase0_step6_small_trial/phase0_step6_small_trial_summary.json
```

---

## 4. 代表姿态数据示例

### 4.1 yaw000_pitch+000_roll+000

OCS JSON 内容：
```json
{
  "record_id": "phase63_yaw000_pitch+000",
  "yaw_deg": 0.0,
  "pitch_deg": 0.0,
  "geom_id": "phase63",
  "ocs_total": 0.01191481632793756,
  "ocs_per_part": {
    "jinshuzhuti": 0.011347180896154052,
    "taiyangnengban": 0.00033777909830496125,
    "yinshenban": 0.00022985633347854736
  },
  "n_pixels_camera_visible": 5949,
  "n_pixels_nol_positive": 1951,
  "n_pixels_sun_visible": 5785,
  "n_pixels_contributing": 1885,
  "n_pixels_per_part": {
    "jinshuzhuti": 1687,
    "taiyangnengban": 134,
    "yinshenban": 64
  }
}
```

像素统计解读：
- camera_visible（5949）：camera 前景像素数
- nol_positive（1951）：其中 NoL > eps 的像素数
- sun_visible（5785）：其中 V_sun_macro = 1 的像素数
- contributing（1885）：最终贡献到 OCS 的像素数（NoV > eps AND NoL > eps AND V_sun_macro = 1）

per-part 拆分显示金属主体占主导（1687 像素，OCS = 0.01135），太阳能板和隐身板贡献较小。

### 4.2 全部 5 姿态 OCS 范围

| 姿态 | OCS 总量 | 贡献像素数 |
|---|---|---|
| yaw180_pitch+000_roll+000 | 0.01301 | 2213 |
| yaw150_pitch+025_roll+000 | 0.03937 | 3435 |
| yaw000_pitch+000_roll+000 | 0.01191 | 1885 |
| yaw090_pitch+000_roll+000 | 0.01840 | 2785 |
| yaw300_pitch-025_roll+000 | 0.01470 | 2972 |

OCS 最大值出现在 yaw150_pitch+025（0.03937），最小值出现在 yaw000_pitch+000（0.01191），跨度约 3.3 倍。

---

## 5. 技术验证

### 5.1 有效像素规则（13 §9.2 / CR4-004）

已正确实现：
- 有效响应像素 = camera_foreground AND NoV > 1e-6 AND NoL > 1e-6
- 贡献像素 = valid_response AND V_sun_macro == 1
- 无效像素：f_r = 0, I_linear = 0, OCS contribution = 0

5 姿态均符合规则：`n_pixels_contributing <= n_pixels_nol_positive <= n_pixels_camera_visible`。

### 5.2 图像响应链（13 §8.2 / CR4-001）

已正确实现：
- Step 1：`I_linear(p) = f_r(p) · NoL(p) · V_sun_macro(p)`
- Step 2：全局归一化 `I_norm = I_linear / i_scale_smallrun`
- Step 3：log1p 变换 `I_log = log1p(α · I_norm) / log1p(α)`，α = 10
- Step 4：8-bit PNG 存储 `PNG = clip(round(I_log · 255), 0, 255)`

EXR 为 float32 线性辐亮度，PNG 为 log1p 映射后的训练输入格式。

### 5.3 OCS 积分公式（13 §6.2）

已正确实现：
- `OCS = Σ A_pixel · I_linear`，仅对贡献像素求和
- `pixel_area_m2 = (ortho_scale_m / resolution)^2 = 0.0001324 m²`
- per-part OCS 按 IndexOB 拆分，三部件求和等于 ocs_total（数值已验证）

### 5.4 Manifest 字段对齐（14 §3.1 / CR4-006）

OCS JSON 包含 14 号规定的所有必需字段：
- ✓ record_id（稳定唯一 key，格式 `{geom_id}_yaw{yyy}_pitch{ppp}`）
- ✓ yaw_deg / pitch_deg / geom_id
- ✓ ocs_total / ocs_per_part
- ✓ 四类像素统计（n_pixels_camera_visible / nol_positive / sun_visible / contributing）
- ✓ n_pixels_per_part

暂未写入的字段（留待全量 manifest 生成时补充）：
- sun_dir / det_dir
- camera_exr_path / position_exr_path / sun_depth_exr_path / sun_visibility_mask_path
- exr_path / png_path（图像侧）
- camera_matrix_world / sun_camera_matrix_world

---

## 6. 模块边界与后续扩展

### 6.1 本轮已实现

- ✓ B0 BRDF 后处理入口（image_response_v0_4.py）
- ✓ OCS 积分入口（ocs_integration_v0_4.py）
- ✓ per-frame I_linear EXR / log1p PNG / OCS JSON 输出
- ✓ 四类像素统计字段
- ✓ 固定 I_scale，无 per-frame normalization
- ✓ 小规模试跑脚本（5 姿态）

### 6.2 本轮边界标注

- **BRDF 分支**：B0 作为工程 baseline，不声称书中改进冯模型或 Torrance-Sparrow 五参数模型
- **试跑范围**：5 姿态，不是全量 2664 姿态，不是训练 corpus
- **I_scale 策略**：复用 Step 5 的固定值，不是 v0.4 clean corpus 全局最大值（后者需全量生成后确定）
- **Manifest 体系**：per-frame OCS JSON 符合 14 号字段规范，但完整 ocs_manifest.json / image_manifest.json 留待全量生成时构建

### 6.3 留待后续

Phase 0 Step 7 及全量生成前需补充：

1. **BRDF 分支升级**（不阻塞 Step 6）：
   - B1：书中改进冯模型（需作者确认三部件材料对应关系）
   - GGX：对照分支（已有材料参数，需实现 eval_ggx_cook_torrance 函数）

2. **全量 Manifest 生成**（Step 7 或更后）：
   - 构建完整 ocs_manifest_v0_4.json（2664 records + 全局 version 字段）
   - 构建完整 image_manifest_v0_4.json（2664 records + preprocessing 字段）
   - 补充 camera_matrix_world / sun_camera_matrix_world（从 Blender 脚本提取）
   - 写入 sun_dir / det_dir / source EXR 路径

3. **一致性检查**（14 §8）：
   - 跨 OCS/image manifest 的 record_id 对齐验证
   - sun_visibility / shadow_mapping_method / v_sun_macro_mode 一致性验证

4. **Multi-geom 扩展**（主线后）：
   - 其余 4 组 sun/det 几何的 camera/sun EXR 渲染
   - 每 geom 独立 sun shadow pass + BRDF 后处理（13 §11.1 / CR4-005）

---

## 7. 依据文件

本轮执行严格遵循以下冻结规范：

1. **13_v0.4前向模型冻结规范_最终冻结版.md**
   - §8.2：图像响应链（I_linear = f_r · NoL · V_sun_macro）
   - §9.2：有效像素规则（NoV > eps AND NoL > eps，eps = 1e-6）
   - §11.1：single-geom 主线（phase63）
   - §12.7：V_sun_macro 对图像的影响验证（Step 5 已通过）

2. **14_v0.4数据与manifest字段规范_最终冻结版.md**
   - §3.1：ocs_manifest 字段（record_id / 四类像素统计 / per-part OCS）
   - §3.2：image_manifest 字段（v_sun_macro_mode / log1p_alpha / I_scale）

3. **R26_Codex_审阅_1C-E10通过并放行Phase0_Step5.md**
   - §5：下一步 Phase 0 Step 6
   - §6：给 Claude 的下一步短提示词（本轮任务规格）

---

## 8. 红线遵守

- ✓ 未进入全量 2664 姿态生成
- ✓ 未训练模型
- ✓ 未改写论文正文
- ✓ 未修改 CLAUDE.md、13/14 冻结文件、路线冻结文件或书籍知识库
- ✓ 未写入 `04_Codex审阅/`
- ✓ 未生成 Codex、验收、最终放行等名义文件
- ✓ 明确标注本轮是 B0 small-run，不是全量 corpus

---

## 9. 产物稳定性

本轮产物可作为 Phase 0 Step 6 完整交付：

| 产物类型 | 路径 | 状态 |
|---|---|---|
| 图像响应模块 | 06_v0.4_code/05_postprocess/image_response_v0_4.py | 稳定，可复用 |
| OCS 积分模块 | 06_v0.4_code/05_postprocess/ocs_integration_v0_4.py | 稳定，可复用 |
| Step 6 主脚本 | 06_v0.4_code/05_postprocess/run_phase0_step6_small_trial.py | 稳定，可复用 |
| 5 姿态产物 | v0.4_results/00_validation/phase0_step6_small_trial/ | 稳定，可审阅 |
| Summary JSON | phase0_step6_small_trial_summary.json | 完整，无阻断项 |

---

## 10. 下一步建议

Phase 0 Step 6 已 COMPLETE，可提交 Codex 审阅。建议审阅重点：

1. **模块边界**：image_response_v0_4.py / ocs_integration_v0_4.py 是否符合 13/14 号规范
2. **字段完整性**：per-frame OCS JSON 是否包含 14 号规定的必需字段
3. **I_scale 策略**：固定使用 Step 5 的 i_scale_step5 是否合理（全量 corpus 前的过渡方案）
4. **BRDF 分支状态**：B0 baseline 是否足够作为 smoke test / 最小链路闭合的工程基线

审阅通过后，可进入：
- Phase 0 Step 7：BRDF 分支升级（B1 / GGX）+ 全量 manifest 生成准备
- 或根据 Codex 裁决调整 Step 6 实现

---

**执行端签名**：Claude  
**执行时间**：2026-06-23  
**执行状态**：Phase 0 Step 6 = COMPLETE
