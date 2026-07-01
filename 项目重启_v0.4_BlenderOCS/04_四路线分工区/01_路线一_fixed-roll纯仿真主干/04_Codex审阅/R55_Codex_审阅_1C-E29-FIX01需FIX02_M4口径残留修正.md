# R55 Codex 审阅：1C-E29-FIX01 需 FIX02

最后更新：2026-06-25  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/55_1C-E29-FIX01_特征定义schema与claim边界修正_Claude执行报告.md
06_v0.4_code/07_training/feature_extract_ocs.py
v0.4_results/04_ocs_features/feature_definitions.json
```

---

## 0. 裁决

```text
1C-E29-FIX01：NEEDS FIX02
C1 正式执行 E30：NOT RELEASED
C2 OCS-only 筛选：NOT RELEASED
C3 joint 复验：NOT RELEASED
```

FIX01 已基本闭合 R54 的两个 Major 问题：

```text
F1 photometric OCS claim class：主体修正合格
F2 预注册定义与运行态 summary 分离：合格
```

但 `feature_definitions.json` 仍有 1 处旧口径残留，会继续把含 density/pixel-count 归一化的配置写成 `photometric-OCS-only`。这是小范围文本返工，不涉及公式、配置、脚本逻辑或训练协议。

在该口径残留修正前，不放行 E30。

---

## 1. 已通过检查

### 1.1 语法检查通过

已执行：

```powershell
C:\Users\97466\.conda\envs\ocs_sim\python.exe -m py_compile 06_v0.4_code/07_training/feature_extract_ocs.py
```

结果：PASS。未运行特征抽取入口。

### 1.2 配置不变性通过

静态比对脚本 `CONFIGS` 与 `feature_definitions.json`：

```text
configs_equal = True
config_count  = 14
```

14 个配置的 `config_name / claim_class / feature_keys` 未发生漂移。

### 1.3 预注册审计字段保留

`feature_definitions.json` 保留：

```text
task
pre_registered_date
source_manifest
expected_n_records
pre_registered_constants
claim_classes
raw_feature_fields
configs
sanity_check_expected
c2_exclusion_configs
c2_evaluation_note
```

每个 config 保留：

```text
config_id
config_name
claim_class
dim
c2_participant
group
feature_keys
description
```

### 1.4 脚本不再覆盖预注册 definitions

`feature_extract_ocs.py` 已改为：

```text
读取 feature_definitions.json 的 expected_n_records
运行态输出 feature_extraction_run_summary.json
不再默认写 feature_definitions.json
summary 记录 record_id_unique / record_id_count / sanity_check / npz_path
```

该部分通过。

---

## 2. Finding

### F1. M4 description 仍保留 `photometric-OCS-only` 旧口径

严重级别：Minor，但运行前必须修正  
位置：

```text
v0.4_results/04_ocs_features/feature_definitions.json:181
```

当前文本：

```text
Extended combination: log features + density features + raw ratios.
Maximum photometric-OCS-only information.
```

问题：

`M4_log_density_ratio_9d` 包含：

```text
ocs_density_total
ocs_density_jinshuzhuti
ocs_density_taiyangnengban
```

这些 density 特征使用 `n_pixels_contributing / n_pixels_per_part` 作为 visibility pixel-count 分母。根据 R54 和 FIX01 主体修正，M4 不得再被描述为 `photometric-OCS-only`。

要求：

1. 将 M4 description 改为不含 `photometric-OCS-only` 的表述。
2. 建议文本：

```text
Extended combination: log features + density features + raw ratios. Includes OCS photometric values normalized by visibility pixel counts; positive results must not be claimed as pure photometric-only evidence.
```

3. 同步检查 `N_density_3d` 与 `M3_density_ratio_5d` 的 description，必要时补充 `visibility-normalized` 口径，避免后续读表误判。
4. 不改变任何 config 的：

```text
config_id
config_name
claim_class
dim
c2_participant
group
feature_keys
```

5. 不修改脚本公式，不运行脚本。

---

## 3. 当前禁止边界

FIX02 通过前，禁止：

```text
运行 feature_extract_ocs.py
生成 enhanced_ocs_features.npz
生成 feature_extraction_run_summary.json
启动 C2/C3
修改 manifest / split manifest
写论文正文
启动 B1/GGX
启动三轴小项目
启动路线二/三/四
```

允许：

```text
只修改 feature_definitions.json 中 description/claim 文本
只在必要时修改 feature_extract_ocs.py 注释或 docstring
只输出 FIX02 执行报告
```

---

## 4. 给 Claude 的 FIX02 短提示词

```text
执行 1C-E29-FIX02：修正 feature_definitions.json 中 M4 旧口径残留。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R55_Codex_审阅_1C-E29-FIX01需FIX02_M4口径残留修正.md
- v0.4_results/04_ocs_features/feature_definitions.json
- 06_v0.4_code/07_training/feature_extract_ocs.py

任务：
1. 不运行脚本，不抽特征，不训练。
2. 修正 `M4_log_density_ratio_9d` 的 description：
   - 删除 `photometric-OCS-only`；
   - 明确其包含 visibility pixel-count normalized OCS density；
   - 正结果不得写成 pure photometric-only evidence。
3. 同步检查并必要修正 `N_density_3d`、`M3_density_ratio_5d` 的 description，使其与 FIX01 的 claim class 边界一致。
4. 不改变任何配置的 `config_id/config_name/claim_class/dim/c2_participant/group/feature_keys`。
5. 输出执行报告：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/56_1C-E29-FIX02_M4口径残留修正_Claude执行报告.md

红线：
- 不运行 `feature_extract_ocs.py`。
- 不生成 `enhanced_ocs_features.npz`。
- 不生成 `feature_extraction_run_summary.json`。
- 不启动 C2/C3。
- 不改 manifest/split manifest。
- 不写论文正文。
```

