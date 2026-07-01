# R56 Codex 审阅：1C-E29-FIX02 通过并放行 E30

最后更新：2026-06-25  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/56_1C-E29-FIX02_M4口径残留修正_Claude执行报告.md
v0.4_results/04_ocs_features/feature_definitions.json
06_v0.4_code/07_training/feature_extract_ocs.py
```

---

## 0. 裁决

```text
1C-E29-FIX02：PASS
E29 C1 脚本与预注册定义：PASS
E30 C1 特征提取正式执行：RELEASED
C2 OCS-only 筛选：NOT RELEASED
C3 joint 复验：NOT RELEASED
```

FIX02 已闭合 R55 指出的 M4 旧口径残留。`1C-E29` 的脚本编写、schema 分离和 claim 边界补正链条完成，可以进入 `1C-E30`：运行 C1 特征提取脚本并做运行态自检。

---

## 1. 审阅检查结果

### 1.1 配置与 schema 不变性

静态比对 `feature_extract_ocs.py::CONFIGS` 与 `feature_definitions.json::configs`：

```text
configs_equal      = True
n_configs          = 14
expected_n_records = 2664
```

14 个配置的核心字段保持不变：

```text
config_id
config_name
claim_class
dim
c2_participant
group
feature_keys
```

### 1.2 旧口径残留已清除

重点配置 description 当前为：

```text
N_density_3d:
Per-pixel average OCS (OCS photometric values normalized by visibility pixel counts).
Positive results represent photometric signal modulated by geometry,
not pure photometric-only evidence.

M3_density_ratio_5d:
Compact combination: per-pixel densities (visibility-normalized) + raw ratios.
Includes OCS photometric values normalized by visibility pixel counts.

M4_log_density_ratio_9d:
Extended combination: log features + density features + raw ratios.
Includes OCS photometric values normalized by visibility pixel counts;
positive results must not be claimed as pure photometric-only evidence.
```

检查结果：

```text
bad_photometric_ocs_only = False
```

`photometric-OCS-only` 残留已移除。N/M3/M4 的 description 已与 FIX01 claim class 边界对齐。

### 1.3 运行产物未提前生成

`v0.4_results/04_ocs_features/` 当前仅包含：

```text
feature_definitions.json
```

未发现：

```text
enhanced_ocs_features.npz
feature_extraction_run_summary.json
```

红线遵守合格。

### 1.4 脚本语法通过

已用指定 Python 环境静态编译：

```powershell
C:\Users\97466\.conda\envs\ocs_sim\python.exe -m py_compile 06_v0.4_code/07_training/feature_extract_ocs.py
```

结果：PASS。未运行脚本入口。

---

## 2. E30 放行范围

放行 `1C-E30`：

```text
C1 OCS 特征提取正式执行
```

允许：

```text
运行 06_v0.4_code/07_training/feature_extract_ocs.py
生成 v0.4_results/04_ocs_features/enhanced_ocs_features.npz
生成 v0.4_results/04_ocs_features/feature_extraction_run_summary.json
验证 feature_definitions.json 未被覆盖
验证 constant_check_1d 为常量
验证 n_records = 2664
验证 record_count_match = true
验证 record_id_unique = true
验证 14 个配置矩阵 shape 正确
```

仍然禁止：

```text
启动 C2 训练筛选
启动 C3 joint 复验
修改 manifest / split manifest
改动特征公式或配置
写论文正文
启动 B1/GGX
启动三轴小项目
启动路线二/三/四
```

E30 完成后必须提交 Codex 审阅。只有 C1 运行产物通过审阅后，才可讨论是否放行 C2。

---

## 3. 给 Claude 的 E30 短提示词

```text
执行 1C-E30：C1 OCS 特征提取正式执行。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R56_Codex_审阅_1C-E29-FIX02通过并放行E30_C1正式执行.md
- 06_v0.4_code/07_training/feature_extract_ocs.py
- v0.4_results/04_ocs_features/feature_definitions.json

任务：
1. 使用指定环境运行脚本：
   C:\Users\97466\.conda\envs\ocs_sim\python.exe 06_v0.4_code/07_training/feature_extract_ocs.py
2. 验证输出：
   - v0.4_results/04_ocs_features/enhanced_ocs_features.npz
   - v0.4_results/04_ocs_features/feature_extraction_run_summary.json
3. 验证 feature_definitions.json 未被覆盖，仍保留预注册字段。
4. 检查并报告：
   - n_records = 2664
   - record_count_match = true
   - record_id_unique = true
   - constant_check_1d / phase_angle_cos unique_values = 1
   - 14 个配置的矩阵 shape；constant_check_1d 不参与 C2
   - NPZ 中 record_ids 数量与 manifest 对齐
5. 输出执行报告：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/57_1C-E30_C1特征提取正式执行_Claude执行报告.md

红线：
- 不启动 C2 训练。
- 不启动 C3 joint 复验。
- 不改 manifest / split manifest。
- 不改特征公式或配置。
- 不写论文正文。
- 不启动 B1/GGX、三轴小项目、路线二/三/四。
```

