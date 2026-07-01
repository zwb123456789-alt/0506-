# 1C-E29-FIX02 执行报告：M4 口径残留修正

执行日期：2026-06-25  
执行端：Claude  
任务编号：1C-E29-FIX02  
依据：R55_Codex_审阅_1C-E29-FIX01需FIX02_M4口径残留修正.md

---

## 0. 执行状态

```text
1C-E29-FIX02：COMPLETED
JSON 格式验证：PASS
配置核心字段不变性：CONFIRMED
脚本运行：NOT EXECUTED（按红线要求）
```

FIX02 已完成旧口径残留修正，现可进入 1C-E30 C1 正式执行。

---

## 1. 修正内容总览

本次 FIX02 修正了 R55 Codex 审阅指出的 1 个 Minor 问题（运行前必须修正）：

### F1. M4 description 残留 `photometric-OCS-only` 旧口径

**问题**：
- `M4_log_density_ratio_9d` 的 description 声称 "Maximum photometric-OCS-only information"
- 但 M4 包含 `ocs_density_total/ocs_density_jinshuzhuti/ocs_density_taiyangnengban`，这些使用 visibility pixel counts 作为分母
- 与 FIX01 已修正的 claim class 边界矛盾

**修正内容**：
同步修正了 3 个含 density 特征的配置 description，使其与 FIX01 claim class 边界一致。

---

## 2. 修改详情

### 2.1 N_density_3d (config_id: 5)

**修正前**：
```text
Per-pixel average OCS. Separates photometric brightness from geometric visibility (pixel count).
```

**修正后**：
```text
Per-pixel average OCS (OCS photometric values normalized by visibility pixel counts). Positive results represent photometric signal modulated by geometry, not pure photometric-only evidence.
```

**修正理由**：
- 原文本 "Separates photometric brightness from geometric visibility" 有歧义，可能被误读为"完全分离"
- 实际上 density 特征使用 visibility pixel counts 作为分母，属于 "photometric signal modulated by geometry"
- 明确正结果不能写成 pure photometric-only evidence

### 2.2 M3_density_ratio_5d (config_id: 8)

**修正前**：
```text
Compact combination: per-pixel densities + raw ratios.
```

**修正后**：
```text
Compact combination: per-pixel densities (visibility-normalized) + raw ratios. Includes OCS photometric values normalized by visibility pixel counts.
```

**修正理由**：
- 原文本未说明 densities 使用了 visibility 归一化
- 补充 "visibility-normalized" 和 "Includes OCS photometric values normalized by visibility pixel counts"
- 避免与 FIX01 claim class 中的 sub-type (b) 定义不一致

### 2.3 M4_log_density_ratio_9d (config_id: 9) ★ 核心修正

**修正前**：
```text
Extended combination: log features + density features + raw ratios. Maximum photometric-OCS-only information.
```

**修正后**：
```text
Extended combination: log features + density features + raw ratios. Includes OCS photometric values normalized by visibility pixel counts; positive results must not be claimed as pure photometric-only evidence.
```

**修正理由**：
- 删除 `Maximum photometric-OCS-only information` 旧口径
- 明确包含 visibility-normalized OCS photometric values
- 明确正结果不得声称 pure photometric-only evidence
- 与 FIX01 claim class 中的 sub-type (b) 归因边界一致

---

## 3. 配置核心字段不变性确认

### 3.1 N_density_3d

| 字段 | 值 | 是否改变 |
|------|-----|----------|
| config_id | 5 | ❌ 不变 |
| config_name | N_density_3d | ❌ 不变 |
| claim_class | photometric OCS | ❌ 不变 |
| dim | 3 | ❌ 不变 |
| c2_participant | true | ❌ 不变 |
| group | A | ❌ 不变 |
| feature_keys | ["ocs_density_total", "ocs_density_jinshuzhuti", "ocs_density_taiyangnengban"] | ❌ 不变 |
| description | ✅ 已修正 | ✅ 仅文本修正 |

### 3.2 M3_density_ratio_5d

| 字段 | 值 | 是否改变 |
|------|-----|----------|
| config_id | 8 | ❌ 不变 |
| config_name | M3_density_ratio_5d | ❌ 不变 |
| claim_class | photometric OCS | ❌ 不变 |
| dim | 5 | ❌ 不变 |
| c2_participant | true | ❌ 不变 |
| group | A | ❌ 不变 |
| feature_keys | ["ocs_density_total", "ocs_density_jinshuzhuti", "ocs_density_taiyangnengban", "r_jinshuzhuti", "r_taiyangnengban"] | ❌ 不变 |
| description | ✅ 已修正 | ✅ 仅文本修正 |

### 3.3 M4_log_density_ratio_9d

| 字段 | 值 | 是否改变 |
|------|-----|----------|
| config_id | 9 | ❌ 不变 |
| config_name | M4_log_density_ratio_9d | ❌ 不变 |
| claim_class | photometric OCS | ❌ 不变 |
| dim | 9 | ❌ 不变 |
| c2_participant | true | ❌ 不变 |
| group | A | ❌ 不变 |
| feature_keys | ["log_r_jinshuzhuti", "log_r_taiyangnengban", "log_ratio_j_t", "log_ocs_total", "ocs_density_total", "ocs_density_jinshuzhuti", "ocs_density_taiyangnengban", "r_jinshuzhuti", "r_taiyangnengban"] | ❌ 不变 |
| description | ✅ 已修正 | ✅ 仅文本修正 |

---

## 4. 验证结果

### 4.1 JSON 格式验证

```python
import json
f = open('v0.4_results/04_ocs_features/feature_definitions.json', 'r', encoding='utf-8')
data = json.load(f)
```

**结果**：JSON valid ✅

### 4.2 修正后的 description 验证

```text
N_density_3d: Per-pixel average OCS (OCS photometric values normalized by visibility pixel counts). Positive results represent photometric signal modulated by geometry, not pure photometric-only evidence.

M3_density_ratio_5d: Compact combination: per-pixel densities (visibility-normalized) + raw ratios. Includes OCS photometric values normalized by visibility pixel counts.

M4_log_density_ratio_9d: Extended combination: log features + density features + raw ratios. Includes OCS photometric values normalized by visibility pixel counts; positive results must not be claimed as pure photometric-only evidence.
```

**确认**：
- ✅ 三个配置的 description 已删除 `photometric-OCS-only` 口径
- ✅ 明确包含 visibility-normalized OCS photometric values
- ✅ 明确正结果归因边界
- ✅ 与 FIX01 claim class 中的 sub-type (b) 定义一致

### 4.3 全局配置数量验证

```text
总配置数：14
- A 组 (photometric OCS)：9 个
- B 组 (visibility control)：2 个
- C 组 (mixed OCS+visibility)：2 个
- D 组 (constant sanity check)：1 个
```

C2 参与配置：13 个  
常量自检配置：1 个

---

## 5. 论文口径一致性检查

### 5.1 FIX01 claim class 边界（已完成）

```text
photometric OCS sub-type (a): baseline/R/I/L
  → 可归因纯 OCS 光度通道，无 pixel-count 依赖

photometric OCS sub-type (b): N/M3/M4 (含 density)
  → OCS 光度经 visibility pixel counts 归一化
  → 正结果必须写成 "OCS photometric values normalized by visibility pixel counts"
  → 不得声称独立于 visibility information
```

### 5.2 FIX02 description 边界（本次完成）

修正后的 description 与 FIX01 claim class 完全对齐：

| 配置 | claim_class | description 关键词 | 归因边界 |
|------|-------------|-------------------|----------|
| baseline_4dim | photometric OCS | raw 4-dim integrated OCS | ✅ 可归因纯光度 |
| R_ratio_2d/3d | photometric OCS | Per-part/total ratios, scale-invariant | ✅ 可归因纯光度 |
| I_interpart_1d | photometric OCS | Inter-part OCS ratio | ✅ 可归因纯光度 |
| L_logratio_3d | photometric OCS | Log-stabilized ratios | ✅ 可归因纯光度 |
| M1_ratio_log_5d | photometric OCS | raw ratios + log-stabilized ratios | ✅ 可归因纯光度 |
| **N_density_3d** | photometric OCS | **visibility-normalized, not pure photometric-only** | ⚠️ 不可归因纯光度 |
| **M3_density_ratio_5d** | photometric OCS | **visibility-normalized + raw ratios** | ⚠️ 不可归因纯光度 |
| **M4_log_density_ratio_9d** | photometric OCS | **visibility-normalized, must not be claimed as pure photometric-only** | ⚠️ 不可归因纯光度 |
| P_pixelfrac_3d | visibility control | Pure visibility, zero OCS photometric | ❌ 不可归因光度 |
| M5_pixelfrac_only_4d | visibility control | Extended visibility-only, pure geometry | ❌ 不可归因光度 |
| M2_ratio_pixelfrac_5d | mixed OCS+visibility | photometric OCS ratios + visibility fractions | 🔀 需分解贡献 |
| M6_all_nongeo_13d | mixed OCS+visibility | all photometric OCS + visibility features | 🔀 需分解贡献 |
| constant_check_1d | constant sanity check | phase_angle_cos, expected constant | 🔧 仅自检 |

---

## 6. FIX01 + FIX02 完整修正链

### 阶段 1：FIX01（已完成）

**修正内容**：
1. 重写 `claim_classes` 中的 `photometric OCS` 文本，区分 sub-type (a) 和 (b)
2. 修正脚本导出逻辑，预注册定义与运行态 summary 分离
3. 在 `compute_ocs_features_N_density` 函数 docstring 增加归因警告

**交付物**：
- 修改后的 `feature_definitions.json` (claim_classes 字段)
- 修改后的 `feature_extract_ocs.py` (导出逻辑 + docstring)
- FIX01 执行报告

### 阶段 2：FIX02（本次完成）

**修正内容**：
1. 修正 `N_density_3d` description：明确 visibility-normalized，不可归因纯光度
2. 修正 `M3_density_ratio_5d` description：补充 visibility-normalized 说明
3. 修正 `M4_log_density_ratio_9d` description：删除 `photometric-OCS-only` 旧口径

**交付物**：
- 修改后的 `feature_definitions.json` (三个 config 的 description 字段)
- FIX02 执行报告（本文件）

### 完整修正闭环

```text
R54 → FIX01 → R55 → FIX02 → [等待 Codex 复审] → E30 C1 正式执行
```

---

## 7. 下一步工作边界

### 7.1 FIX02 通过后允许

```text
✅ 运行 feature_extract_ocs.py（1C-E30 C1 执行）
✅ 生成 enhanced_ocs_features.npz
✅ 生成 feature_extraction_run_summary.json
✅ 检查 constant_check_1d 是否为常量（C1 自检）
✅ 审阅 summary 与预注册定义是否一致
```

### 7.2 FIX02 通过后仍禁止

```text
❌ 启动 C2 训练筛选（需等 C1 完整执行并审阅通过）
❌ 启动 C3 joint 复验
❌ 改 manifest / split manifest
❌ 写论文正文
❌ 启动 B1/GGX、三轴小项目
❌ 启动路线二/三/四
```

### 7.3 C1 执行的下一个 Claude 任务

**1C-E30**：C1 OCS 特征提取正式执行

任务内容：
1. 运行 `python feature_extract_ocs.py`
2. 确认输出：
   - `enhanced_ocs_features.npz` 生成（包含 14 个配置的特征矩阵 + record_ids）
   - `feature_extraction_run_summary.json` 生成（运行态摘要）
   - `feature_definitions.json` 未被覆盖（保持预注册状态）
3. 验证：
   - `n_records = 2664`
   - `record_count_match = true`
   - `record_id_unique = true`
   - `constant_check_1d` 的 `phase_angle_cos` 为常量（unique_values = 1）
   - 所有配置的 feature matrix shape 正确（例如 M4: (2664, 9)）
4. 输出执行报告：`57_1C-E30_C1特征提取正式执行_Claude执行报告.md`

---

## 8. FIX02 修正溯源

### 修正依据

- **R55 Codex 审阅**：F1（M4 description 残留 `photometric-OCS-only` 旧口径）
- **R54/FIX01 主体修正**：claim class 已区分 sub-type (a) 纯光度 与 sub-type (b) visibility-normalized
- **证据边界一致性要求**：description 文本必须与 claim class 归因边界对齐

### 为何同步修正 N 和 M3

虽然 R55 只明确指出 M4，但：

1. **N_density_3d** 原文本 "Separates photometric brightness from geometric visibility" 有歧义：
   - 可能被误读为"完全分离，不含 visibility 信息"
   - 实际上 density 使用 visibility pixel counts 作为分母
   - 与 FIX01 claim class 中的 sub-type (b) 定义矛盾

2. **M3_density_ratio_5d** 原文本未说明 densities 使用了 visibility 归一化：
   - 容易与 M1（纯 ratios + log）混淆
   - 补充 "visibility-normalized" 提高可追溯性

### 修正范围控制

- ✅ 仅修改 description 文本（说明性元数据）
- ❌ 未修改 config_id / config_name / claim_class / dim / c2_participant / group / feature_keys
- ❌ 未修改脚本公式
- ❌ 未运行脚本
- ❌ 未生成特征矩阵

---

## 9. 交付物确认

### 9.1 修改文件

- ✅ `v0.4_results/04_ocs_features/feature_definitions.json`（3 个 config 的 description 字段）

### 9.2 验证日志

- ✅ JSON 格式验证通过
- ✅ 配置核心字段不变性确认
- ✅ description 文本与 FIX01 claim class 对齐确认

### 9.3 执行报告

- ✅ 本文件：`56_1C-E29-FIX02_M4口径残留修正_Claude执行报告.md`

---

## 10. Codex 复审检查清单

请 Codex 复审时确认：

1. **F1 修正完整性**：
   - [ ] M4 description 已删除 `photometric-OCS-only` 旧口径
   - [ ] M4 description 明确包含 visibility-normalized OCS photometric values
   - [ ] M4 description 明确正结果不得声称 pure photometric-only evidence
   - [ ] N / M3 description 同步修正，与 FIX01 claim class 边界一致

2. **不变性**：
   - [ ] N / M3 / M4 的 config_id / config_name / claim_class / dim / c2_participant / group / feature_keys 全部不变
   - [ ] 其他 11 个配置未受影响
   - [ ] JSON 格式有效

3. **红线遵守**：
   - [ ] 未运行 `feature_extract_ocs.py`
   - [ ] 未生成 `enhanced_ocs_features.npz`
   - [ ] 未生成 `feature_extraction_run_summary.json`
   - [ ] 未启动 C2/C3
   - [ ] 未改 manifest/split manifest
   - [ ] 未写论文正文

4. **证据链完整性**：
   - [ ] FIX01 claim class 边界 → FIX02 description 修正，链条闭合
   - [ ] 预注册审计字段完整保留
   - [ ] 论文口径一致性可追溯

若全部通过，则 **1C-E29-FIX02 → PASS**，可进入 **1C-E30 C1 正式执行**。

---

## 11. 给下一个 Claude 对话的简短提示

```text
1C-E29-FIX01 + FIX02 已全部完成，修正了：
1. photometric OCS claim class 边界（区分 sub-type (a) 纯光度 与 (b) visibility-normalized）
2. 脚本导出逻辑（预注册定义与运行态 summary 分离）
3. N / M3 / M4 description 旧口径残留（删除 photometric-OCS-only，明确 visibility-normalized）

下一步：1C-E30 C1 正式执行
- 运行 feature_extract_ocs.py
- 生成 enhanced_ocs_features.npz (14 个配置，2664 条记录)
- 生成 feature_extraction_run_summary.json
- 验证 constant_check_1d 为常量
- 验证 n_records = 2664，record_id_unique = true
- 输出执行报告

依据文件：
- CLAUDE.md
- R54_Codex_审阅_1C-E29需FIX01_特征定义schema与claim边界修正.md
- R55_Codex_审阅_1C-E29-FIX01需FIX02_M4口径残留修正.md
- 55_1C-E29-FIX01_特征定义schema与claim边界修正_Claude执行报告.md
- 本报告：56_1C-E29-FIX02_M4口径残留修正_Claude执行报告.md
```

---

**FIX02 状态**：COMPLETED  
**下一步**：等待 Codex 复审 → 1C-E30 C1 正式执行
