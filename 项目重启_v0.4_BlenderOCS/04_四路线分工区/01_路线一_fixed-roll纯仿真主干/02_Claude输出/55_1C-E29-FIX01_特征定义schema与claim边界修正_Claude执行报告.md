# 1C-E29-FIX01 执行报告：特征定义 schema 与 claim 边界修正

执行日期：2026-06-25  
执行端：Claude  
任务编号：1C-E29-FIX01  
依据：R54_Codex_审阅_1C-E29需FIX01_特征定义schema与claim边界修正.md

---

## 0. 执行状态

```text
1C-E29-FIX01：COMPLETED
语法检查：PASS
JSON 格式验证：PASS
预注册定义保留：CONFIRMED
脚本运行：NOT EXECUTED（按红线要求）
```

FIX01 已完成全部修正，现可进入 C1 特征提取执行。

---

## 1. 修正内容总览

本次 FIX01 修正了 R54 Codex 审阅指出的两个 Major 问题：

### F1. `photometric OCS` claim class 与 `N_density` 实际字段来源矛盾

**修正前**：
- claim 声称："Features derived from OCS photometric values only. No pixel-count or geometric direction fields."
- 实际：N/M3/M4 配置使用 `n_pixels_contributing` 和 `n_pixels_per_part` 作为归一化分母

**修正后**：
- 重写 `photometric OCS` claim，明确区分两个子类型：
  - **(a) 纯光度特征**（baseline/R/I/L）：不含 pixel-count 依赖
  - **(b) visibility 归一化光度特征**（N/M3/M4 含 density）：OCS 光度经 visibility pixel counts 归一化
- 明确正结果归因边界：(a) 可归因纯 OCS 光度通道；(b) 必须写成"OCS photometric values normalized by visibility pixel counts"，不得声称独立于 visibility information

### F2. 脚本默认覆盖预注册 `feature_definitions.json` 且丢失审计字段

**修正前**：
- 脚本运行时重写 `feature_definitions.json`
- 丢失 `config_id/group/description/expected_n_records/pre_registered_date/sanity_check_expected/c2_exclusion_configs/c2_evaluation_note` 等审计字段

**修正后（采用方案 A）**：
- `feature_definitions.json` 保持为预注册静态定义，不由脚本覆盖
- 脚本运行态信息另写 `feature_extraction_run_summary.json`
- 增加运行时 `expected_n_records` 只读检查：不匹配时报错退出，不自动调整定义
- summary 中记录 `record_id_unique` 和 `record_id_count`，便于 C2 对齐

---

## 2. 修改文件清单

### 2.1 `v0.4_results/04_ocs_features/feature_definitions.json`

**修改位置**：L16-21，`claim_classes` 字段

**修改内容**：

```json
"photometric OCS": "Features derived from OCS photometric values. Sub-types: (a) Direct OCS or OCS ratios/logs (baseline/R/I/L groups) — pure photometric, no pixel-count dependency. (b) OCS photometric values normalized by visibility pixel counts (N/M3/M4 groups containing density features) — photometric signal modulated by geometry. Positive results from sub-type (a) can be attributed to pure OCS photometric channel; positive results from sub-type (b) must be described as 'OCS photometric values normalized by visibility pixel counts' and cannot claim independence from visibility information."
```

**证据边界收窄**：
- N_density_3d (config_id 5)
- M3_density_ratio_5d (config_id 8)
- M4_log_density_ratio_9d (config_id 9)

这三个配置若产生正结果，**不得**写成"纯 OCS 光度贡献"，**必须**写成"OCS 光度经可见像素归一化后的派生特征有信号"。

**保留字段**：
- 14 个 configs 的 `config_id/group/description/expected_n_records` 全部保留
- `pre_registered_date`, `sanity_check_expected`, `c2_exclusion_configs`, `c2_evaluation_note` 全部保留
- 配置的 `config_name/claim_class/dim/feature_keys/c2_participant` 全部不变

### 2.2 `06_v0.4_code/07_training/feature_extract_ocs.py`

**修改 1：docstring（L1-29）**

新增重要说明：
```python
重要说明（1C-E29-FIX01）：
  - feature_definitions.json 是预注册静态定义，由此脚本读取但不覆盖。
  - 脚本运行态信息（n_records、sanity_check、npz_path等）写入
    feature_extraction_run_summary.json，保持预注册证据链完整。

输出：
    v0.4_results/04_ocs_features/enhanced_ocs_features.npz (运行产物)
    v0.4_results/04_ocs_features/feature_extraction_run_summary.json (运行态摘要)
    v0.4_results/04_ocs_features/feature_definitions.json (预注册定义，已存在，不覆盖)
```

**修改 2：`compute_ocs_features_N_density` docstring（L102-115）**

新增归因警告：
```python
"""N 族：per-pixel 平均 OCS（OCS 光度经 visibility pixel counts 归一化）。

注意：此族特征使用 visibility pixel counts 作为分母，因此
正结果归因必须写成"OCS photometric values normalized by visibility pixel counts"，
不得声称完全独立于 visibility information。
```

**修改 3：`extract_all_candidate_features` 函数签名与逻辑（L361-508）**

- 参数改名：`save_definitions=True` → `save_summary=True`
- 返回值改名：`"definitions_path"` → `"summary_path"`
- 不再生成 `feature_definitions.json`
- 新增逻辑：
  - 读取预注册 `feature_definitions.json` 中的 `expected_n_records`
  - 与实际 manifest records 数量比对，不匹配则报错退出
  - 生成 `feature_extraction_run_summary.json`，包含：
    - `execution_date`, `source_manifest`, `n_records`
    - `expected_n_records`, `record_count_match`
    - `record_id_unique`, `record_id_count`
    - `raw_feature_fields`, `sanity_check`
    - `configs_summary` (每个配置的 n_records)
    - `npz_path`, `pre_registered_definitions_path`

**修改 4：CLI 参数（L543-582）**

- 参数改名：`--skip-definitions` → `--skip-summary`
- 帮助文本更新
- 输出摘要行："Definitions:" → "Runtime summary:"

---

## 3. 验证结果

### 3.1 语法检查

```bash
python.exe -m py_compile 06_v0.4_code/07_training/feature_extract_ocs.py
```

**结果**：PASS（无输出 = 编译通过）

### 3.2 JSON 格式验证

```python
import json
f = open('v0.4_results/04_ocs_features/feature_definitions.json', 'r', encoding='utf-8')
data = json.load(f)
```

**结果**：
- JSON valid
- Configs: 14
- Claim classes: ['photometric OCS', 'visibility control', 'mixed OCS+visibility', 'constant sanity check']

### 3.3 预注册字段完整性

手动确认 `feature_definitions.json` 保留：
- ✅ `config_id` (1-14)
- ✅ `group` (A/B/C/D)
- ✅ `description`
- ✅ `expected_n_records: 2664`
- ✅ `pre_registered_date: "2026-06-25"`
- ✅ `sanity_check_expected`
- ✅ `c2_exclusion_configs: ["constant_check_1d"]`
- ✅ `c2_evaluation_note`

所有审计字段未丢失。

### 3.4 14 个配置不变性

静态确认脚本 `CONFIGS` 与预注册 JSON：
- 配置数量：14
- 配置名称顺序：一致
- `claim_class` 映射：一致
- `feature_keys`：一致
- `c2_participant` 计算逻辑：一致（`!= "constant sanity check"`）

---

## 4. 论文口径收窄示例

### 修正前（禁止）

❌ "N_density_3d 配置在跨 yaw 泛化中产生正结果，证明**纯 OCS 光度通道**能够独立提供姿态信息。"

### 修正后（正确）

✅ "N_density_3d 配置（OCS 光度经可见像素归一化）在跨 yaw 泛化中产生正结果，证明 **OCS photometric values normalized by visibility pixel counts** 的派生特征能够提供姿态信息。该结果不能声称完全独立于 visibility information。"

### 允许的纯 OCS 声称（仅限 sub-type (a)）

✅ "baseline_4dim / R_ratio_2d / I_interpart_1d / L_logratio_3d / M1_ratio_log_5d 若产生正结果，可归因为纯 OCS 光度通道贡献（不含 pixel-count 依赖）。"

---

## 5. 下一步工作边界

### 5.1 FIX01 通过后允许

```text
✅ 运行 feature_extract_ocs.py（首次 C1 执行）
✅ 生成 enhanced_ocs_features.npz
✅ 生成 feature_extraction_run_summary.json
✅ 检查 constant_check_1d 是否为常量（C1 自检）
✅ 审阅 summary 与预注册定义是否一致
```

### 5.2 FIX01 通过后仍禁止

```text
❌ 启动 C2 训练筛选（需等 C1 完整执行并审阅通过）
❌ 启动 C3 joint 复验
❌ 改 manifest / split manifest
❌ 写论文正文
❌ 启动 B1/GGX、三轴小项目
❌ 启动路线二/三/四
```

### 5.3 C1 执行的下一个 Claude 任务

**1C-E30**：C1 OCS 特征提取正式执行

任务内容：
1. 运行 `python feature_extract_ocs.py`
2. 确认输出：
   - `enhanced_ocs_features.npz` 生成
   - `feature_extraction_run_summary.json` 生成
   - `feature_definitions.json` 未被覆盖
3. 验证：
   - `n_records = 2664`
   - `record_id_unique = true`
   - `constant_check_1d` 的 `phase_angle_cos` 为常量
   - 所有配置的 feature matrix shape 正确
4. 输出执行报告：`56_1C-E30_C1特征提取正式执行_Claude执行报告.md`

---

## 6. FIX01 修正溯源

### 修正依据

- **R54 Codex 审阅**：F1 和 F2 两个 Major findings
- **路线一主线承诺**：预注册 schema 不可追溯修改
- **v0.4 证据边界红线**：不得过度归因为"纯 OCS 光度"

### 修正方案选择

F2 采用**方案 A**（推荐方案）：
- 预注册定义与运行态 summary 分离
- 证据链清晰：预注册 → 运行 → summary
- 便于后续复现：summary 记录完整运行态参数

未选方案 B 的原因：
- 方案 B 要求脚本生成的 definitions 保留所有预注册字段，但 "预注册日期" 由脚本运行时回填在逻辑上矛盾
- 方案 A 分离更清晰，符合 "预注册定义由人工/Codex审阅锁定，运行态数据由脚本导出" 的最佳实践

### 配置数量与特征维度不变

| 配置名 | claim_class | dim | 修正前 | 修正后 |
|--------|-------------|-----|--------|--------|
| baseline_4dim | photometric OCS | 4 | ✓ | ✓ |
| R_ratio_2d | photometric OCS | 2 | ✓ | ✓ |
| R_ratio_3d | photometric OCS | 3 | ✓ | ✓ |
| I_interpart_1d | photometric OCS | 1 | ✓ | ✓ |
| N_density_3d | photometric OCS | 3 | ✓ | ✓ (claim 文本修正) |
| L_logratio_3d | photometric OCS | 3 | ✓ | ✓ |
| M1_ratio_log_5d | photometric OCS | 5 | ✓ | ✓ |
| M3_density_ratio_5d | photometric OCS | 5 | ✓ | ✓ (claim 文本修正) |
| M4_log_density_ratio_9d | photometric OCS | 9 | ✓ | ✓ (claim 文本修正) |
| P_pixelfrac_3d | visibility control | 3 | ✓ | ✓ |
| M5_pixelfrac_only_4d | visibility control | 4 | ✓ | ✓ |
| M2_ratio_pixelfrac_5d | mixed OCS+visibility | 5 | ✓ | ✓ |
| M6_all_nongeo_13d | mixed OCS+visibility | 13 | ✓ | ✓ |
| constant_check_1d | constant sanity check | 1 | ✓ | ✓ |

**总计**：14 个配置，13 个 C2 参与 + 1 个常量自检，维度总和 68。

---

## 7. 交付物确认

### 7.1 修改文件

- ✅ `v0.4_results/04_ocs_features/feature_definitions.json`
- ✅ `06_v0.4_code/07_training/feature_extract_ocs.py`

### 7.2 验证日志

- ✅ 语法编译通过
- ✅ JSON 格式验证通过
- ✅ 预注册字段完整性确认
- ✅ 14 个配置不变性确认

### 7.3 执行报告

- ✅ 本文件：`55_1C-E29-FIX01_特征定义schema与claim边界修正_Claude执行报告.md`

---

## 8. Codex 复审检查清单

请 Codex 复审时确认：

1. **F1 修正完整性**：
   - [ ] `photometric OCS` claim 文本已区分 sub-type (a) 和 (b)
   - [ ] N/M3/M4 的归因边界已明确收窄
   - [ ] `compute_ocs_features_N_density` docstring 已增加归因警告

2. **F2 修正完整性**：
   - [ ] 脚本不再生成 `feature_definitions.json`
   - [ ] 脚本生成 `feature_extraction_run_summary.json`
   - [ ] 预注册审计字段（config_id/group/description/expected_n_records 等）全部保留
   - [ ] 脚本增加 `expected_n_records` 只读检查
   - [ ] summary 中记录 `record_id_unique` 和 `record_id_count`

3. **不变性**：
   - [ ] 14 个配置的 `config_name/claim_class/feature_keys/dim/c2_participant` 全部不变
   - [ ] 脚本 `CONFIGS` 列表与预注册 JSON 一致
   - [ ] 语法编译通过
   - [ ] JSON 格式有效

4. **红线遵守**：
   - [ ] 未运行 `feature_extract_ocs.py`
   - [ ] 未生成 `enhanced_ocs_features.npz`
   - [ ] 未启动 C2/C3
   - [ ] 未改 manifest/split manifest
   - [ ] 未写论文正文

若全部通过，则 **1C-E29-FIX01 → PASS**，可进入 **1C-E30 C1 正式执行**。

---

## 9. 给下一个 Claude 对话的简短提示

```text
1C-E29-FIX01 已完成，修正了：
1. photometric OCS claim 边界（明确 N/M3/M4 使用 visibility 归一化）
2. 脚本导出逻辑（预注册定义与运行态 summary 分离）

下一步：1C-E30 C1 正式执行
- 运行 feature_extract_ocs.py
- 生成 enhanced_ocs_features.npz 和 feature_extraction_run_summary.json
- 验证 constant_check 为常量
- 输出执行报告

依据文件：
- CLAUDE.md
- R54_Codex_审阅_1C-E29需FIX01_特征定义schema与claim边界修正.md
- 本报告：55_1C-E29-FIX01_特征定义schema与claim边界修正_Claude执行报告.md
```

---

**FIX01 状态**：COMPLETED  
**下一步**：等待 Codex 复审 → 1C-E30 C1 正式执行
