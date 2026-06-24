# 28 1C-E11-FIX01 ortho_scale 因子修正 — Claude 执行报告

生成时间：2026-06-23  
任务编号：1C-E11-FIX01  
执行端：Claude  
前置任务：1C-E11 Phase 0 Step 6（初版存在阻断项）

---

## 1. 问题诊断

### 1.1 阻断项

Phase 0 Step 6 初版使用了错误的 ortho_scale 因子：

```python
# 错误代码（初版）
ortho_scale_m = 2.0 * r_max
```

正确规范要求：

```text
13 号冻结规范：ortho_scale = 2.2 × r_max
config_v0_4.py：ORTHO_SCALE_FACTOR = 2.2
validate_shadow_consistency_fixed.py：ortho_scale = 2.2 * r_max
```

### 1.2 影响范围

错误的 ortho_scale 因子导致 pixel_area_m2 偏小：

| 参数 | 初版（错误） | 修正后（正确） | 偏差 |
|---|---|---|---|
| ortho_scale_m | 2.0 × 1.4726 = 2.9452 | 2.2 × 1.4726 = 3.2397 | -9.09% |
| pixel_area_m2 | 0.0001324 | 0.0001602 | -17.36% |
| OCS 数值 | 偏小约 17.36% | 正确 | 需乘 1.21 |

所有 5 个姿态的 `ocs_total` 和 `ocs_per_part` 均偏小约 17.36%。

---

## 2. 修正内容

### 2.1 代码修正

文件：`06_v0.4_code/05_postprocess/run_phase0_step6_small_trial.py`

```diff
- ortho_scale_m = 2.0 * r_max
+ ortho_scale_m = 2.2 * r_max  # 13 号规范和 config_v0_4.py: ORTHO_SCALE_FACTOR = 2.2
```

修正位置：第 133 行。

### 2.2 重新执行

重新运行 `run_phase0_step6_small_trial.py`，更新：
- 5 个姿态的 `{label}_ocs.json`
- `phase0_step6_small_trial_summary.json`

图像产物（EXR/PNG）未变化，因为 ortho_scale 只影响 OCS 积分的 pixel_area_m2 因子，不影响图像响应计算。

---

## 3. 修正后结果

### 3.1 pixel_area_m2 验证

```json
{
  "ortho_scale_m": 3.239731375366906,
  "resolution": 256,
  "pixel_area_m2": 0.00016015410437830724
}
```

验证：
```text
ortho_scale_m = 2.2 × 1.4726051706213208 = 3.2397313753669076
pixel_area_m2 = (3.2397313753669076 / 256)^2 = 0.00016015410437830724 ✓
```

### 3.2 OCS 数值修正

以 yaw000_pitch+000_roll+000 为例：

| 参数 | 初版（错误） | 修正后（正确） | 比例 |
|---|---|---|---|
| ocs_total | 0.01191482 | 0.01441693 | 1.210000 |
| jinshuzhuti | 0.01134718 | 0.01373009 | 1.210000 |
| taiyangnengban | 0.00033778 | 0.00040871 | 1.210000 |
| yinshenban | 0.00022986 | 0.00027813 | 1.210000 |

修正比例 = (2.2 / 2.0)² = 1.21，与实际比例完全一致。

### 3.3 全部 5 姿态修正后 OCS

| 姿态 | OCS 总量（修正后） | 贡献像素数 |
|---|---|---|
| yaw180_pitch+000_roll+000 | 0.01574498 | 2213 |
| yaw150_pitch+025_roll+000 | 0.04763879 | 3435 |
| yaw000_pitch+000_roll+000 | 0.01441693 | 1885 |
| yaw090_pitch+000_roll+000 | 0.02226072 | 2785 |
| yaw300_pitch-025_roll+000 | 0.01779191 | 2972 |

OCS 最大值：0.04764（yaw150_pitch+025），最小值：0.01442（yaw000_pitch+000），跨度约 3.3 倍。

---

## 4. 修正验证

### 4.1 数值一致性

5 个姿态的 OCS JSON 和 summary 中的 `pixel_area_m2` 均已更新：
- ✓ `pixel_area_m2 = 0.00016015410437830724`（与预期完全匹配）
- ✓ 所有 OCS 数值按 1.21 倍修正
- ✓ 像素统计（n_pixels_camera_visible 等）未变化（正确，因为只改了积分因子）

### 4.2 代码规范对齐

修正后的代码与既有规范一致：
- ✓ 与 `config_v0_4.py` 的 `ORTHO_SCALE_FACTOR = 2.2` 对齐
- ✓ 与 `validate_shadow_consistency_fixed.py` 的 `ortho_scale = 2.2 * r_max` 对齐
- ✓ 与 13 号冻结规范的 `ortho_scale = 2.2 × r_max` 对齐

---

## 5. 产物状态

### 5.1 更新产物

| 产物类型 | 路径 | 状态 |
|---|---|---|
| 主执行脚本 | 06_v0.4_code/05_postprocess/run_phase0_step6_small_trial.py | 已修正 |
| Summary JSON | phase0_step6_small_trial_summary.json | 已更新 |
| 5 × OCS JSON | yaw{xxx}_ocs.json | 已更新 |
| 5 × I_linear EXR | yaw{xxx}_linear.exr | 未变化（正确） |
| 5 × log1p PNG | yaw{xxx}_brdf.png | 未变化（正确） |

### 5.2 稳定性确认

- ✓ 无新增阻断项
- ✓ `overall_status = "COMPLETE"`
- ✓ `blockers = []`
- ✓ 5 姿态全部 `status = "COMPLETE"`

---

## 6. 根因与防范

### 6.1 根因

初版代码直接写死 `ortho_scale_m = 2.0 * r_max`，未引用 `config_v0_4.py` 的 `ORTHO_SCALE_FACTOR`，也未检查既有验证脚本的实现。

### 6.2 防范建议

后续 Phase 0 Step 7 及全量生成时：
1. 优先从 `config_v0_4.py` 导入 `ORTHO_SCALE_FACTOR`，避免硬编码
2. 在代码注释中明确标注来源（"13 号规范 + config_v0_4.py"）
3. 小规模试跑后，用既有验证脚本（如 Step 4）的参数做交叉验证

---

## 7. 下一步

1C-E11-FIX01 已 **COMPLETE**，修正后的 Phase 0 Step 6 产物可提交 Codex 技术审阅。

审阅重点：
1. ✓ pixel_area_m2 是否符合 13 号规范（ortho_scale = 2.2 × r_max）
2. ✓ OCS 数值是否已修正为正确尺度
3. ✓ 代码是否与 config_v0_4.py / validate_shadow_consistency_fixed.py 对齐

---

## 8. 修正总结

| 项目 | 修正前 | 修正后 |
|---|---|---|
| ortho_scale_factor | 2.0（错误） | 2.2（正确） |
| pixel_area_m2 | 0.0001324 | 0.0001602 |
| OCS 尺度 | 偏小 17.36% | 正确 |
| 代码对齐 | 不符合规范 | 符合 13 号 + config_v0_4.py |
| 阻断项 | 1 项 | 0 项 |
| 状态 | NOT_PASS | COMPLETE |

---

**执行端签名**：Claude  
**执行时间**：2026-06-23  
**修正状态**：1C-E11-FIX01 = **COMPLETE** ✅  
**Phase 0 Step 6 最终状态**：已修正，可提交审阅
