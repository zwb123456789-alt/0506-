# R54 Codex 审阅：1C-E29 需 FIX01

最后更新：2026-06-25  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/54_1C-E29_C1特征提取脚本编写_Claude执行报告.md
06_v0.4_code/07_training/feature_extract_ocs.py
v0.4_results/04_ocs_features/feature_definitions.json
```

---

## 0. 裁决

```text
1C-E29：NEEDS FIX01
C1 脚本编写：未放行执行
C2 OCS-only 筛选：NOT RELEASED
C3 joint 复验：NOT RELEASED
```

E29 的主结构、14 个配置数量、A/B/C/D 分层、G 常量自检、P visibility control、mixed OCS+visibility 分层总体符合 R53。但当前版本存在 2 个需要在运行特征提取前修正的问题：

1. `photometric OCS` 的元数据 claim 过强，和 `N_density` 实际使用像素计数字段矛盾。
2. 脚本默认运行会重写 `feature_definitions.json`，且运行态 schema 会丢失预注册文件中的 `config_id/group/description/expected_n_records` 等审计字段。

这两个问题都属于 C1 运行前必须修正的证据边界/可追溯性问题。当前不得运行 `feature_extract_ocs.py`，不得进入 C2 训练。

---

## 1. 已通过检查

### 1.1 语法检查通过

已用项目指定环境执行静态语法编译：

```powershell
C:\Users\97466\.conda\envs\ocs_sim\python.exe -m py_compile 06_v0.4_code/07_training/feature_extract_ocs.py
```

结果：通过。未运行特征抽取入口。

### 1.2 配置数量与顺序一致

静态比对 `feature_extract_ocs.py::CONFIGS` 与 `feature_definitions.json::configs`：

```text
script_configs = 14
json_configs   = 14
configs_equal  = True
```

13 个 C2 参与配置 + 1 个 constant check 配置的名称、claim_class 和 feature_keys 一致。

### 1.3 manifest 字段存在

只读抽查 `v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_fullrun.json` 首条记录，确认脚本所需字段存在：

```text
records = 2664
ocs_total / ocs_per_part / n_pixels_camera_visible / n_pixels_sun_visible /
n_pixels_contributing / n_pixels_per_part / sun_dir / det_dir 均存在。
```

---

## 2. Findings

### F1. `photometric OCS` claim class 与 `N_density` 实际字段来源矛盾

严重级别：Major  
位置：

```text
06_v0.4_code/07_training/feature_extract_ocs.py:102-123
06_v0.4_code/07_training/feature_extract_ocs.py:450-454
v0.4_results/04_ocs_features/feature_definitions.json:16-18
v0.4_results/04_ocs_features/feature_definitions.json:103-116
```

问题：

`N_density` 的公式实际使用像素计数字段作为分母：

```text
ocs_density_total = ocs_total / n_pixels_contributing
ocs_density_part  = ocs_part / n_pixels_per_part
```

但当前 claim class 文本把 `photometric OCS` 定义为：

```text
Features derived from OCS photometric values only. No pixel-count or geometric fields.
```

这与 `N_density_3d`、`M3_density_ratio_5d`、`M4_log_density_ratio_9d` 的实际特征来源矛盾。若后续这些配置出现正结果，当前元数据会把结果过度归因成“纯 OCS 光度通道”，而忽略它们使用了 visibility count 进行归一化。

要求修正：

1. 不改变已预注册的公式和配置表。
2. 修正 `photometric OCS` 的 claim class 文本，使其不再声称所有 A 组特征都“不含 pixel-count”。
3. 对 A 组内部增加字段来源说明：
   - `baseline/R/I/L`：direct/integrated OCS 或 OCS ratio/log derived。
   - `N` 以及含 `N` 的 `M3/M4`：OCS photometric values normalized by visibility pixel counts。
4. 论文口径必须收窄：
   - `N/M3/M4` 若正结果，只能写成“OCS 光度经可见像素归一化后的派生特征有信号”；
   - 不得写成“完全不含 visibility information 的纯 OCS 光度贡献”。

### F2. 脚本默认会覆盖预注册 `feature_definitions.json` 且丢失审计字段

严重级别：Major  
位置：

```text
06_v0.4_code/07_training/feature_extract_ocs.py:431-484
06_v0.4_code/07_training/feature_extract_ocs.py:545-573
v0.4_results/04_ocs_features/feature_definitions.json:48-264
```

问题：

当前仓库中的 `feature_definitions.json` 是预注册定义，包含：

```text
config_id
group
description
expected_n_records
pre_registered_date
sanity_check_expected
c2_exclusion_configs
c2_evaluation_note
```

但脚本默认执行时会在同一路径重写 `feature_definitions.json`，运行态生成的 schema 只保留 `config_name/claim_class/dim/feature_keys/c2_participant`，会丢失上述预注册审计字段。

这会破坏 C2 之前的预注册证据链：第一次正式运行脚本就可能把“预注册定义文件”替换成“运行结果摘要式定义文件”。

要求修正，二选一即可：

方案 A（推荐）：

```text
feature_definitions.json = 保持为预注册静态定义，不由抽取脚本默认覆盖。
脚本运行时另写：
  feature_extraction_run_summary.json
其中记录 n_records、source_manifest、raw_feature_fields、sanity_check、npz_path 等运行态信息。
```

方案 B：

```text
脚本生成的 feature_definitions.json 必须完整保留现有预注册 schema：
config_id/group/description/expected_n_records/pre_registered_date/
sanity_check_expected/c2_exclusion_configs/c2_evaluation_note
全部不得丢失，并追加运行态 sanity_check。
```

无论选择 A 或 B，都必须保证再次运行脚本不会降低预注册文件的信息量。

---

## 3. 非阻断建议

以下不阻塞 FIX01，但建议一并处理：

1. 在脚本 docstring 中明确：`feature_definitions.json` 是预注册定义，`enhanced_ocs_features.npz` 是运行产物。
2. 增加 `expected_n_records = 2664` 的运行时只读检查；不匹配时只报错退出，不自动调整定义。
3. 运行态 summary 中记录 `record_id_unique=true/false` 和 `record_id_count`，便于 C2 与 split manifest 对齐。

---

## 4. 当前禁止边界

在 FIX01 通过前，禁止：

```text
运行 feature_extract_ocs.py
生成 enhanced_ocs_features.npz
启动 C2 训练筛选
启动 C3 joint 复验
改 manifest 或 split manifest
写论文正文
启动 B1/GGX
启动三轴小项目
启动路线二/三/四
```

允许：

```text
只修改 feature_extract_ocs.py 的元数据导出逻辑和 claim class 文本
只修改 feature_definitions.json 的说明性元数据
只更新 Claude FIX01 执行报告
```

---

## 5. 给 Claude 的 FIX01 短提示词

```text
执行 1C-E29-FIX01：修正 OCS 特征提取脚本的定义 schema 与 claim 边界。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R54_Codex_审阅_1C-E29需FIX01_特征定义schema与claim边界修正.md
- 06_v0.4_code/07_training/feature_extract_ocs.py
- v0.4_results/04_ocs_features/feature_definitions.json

任务：
1. 不运行脚本，不抽特征，不训练。
2. 修正 `photometric OCS` claim class 文本：
   - 不再声称 A 组所有特征都完全不含 pixel-count；
   - 明确 N/M3/M4 是 OCS 光度经 visibility pixel counts 归一化；
   - 正结果归因必须收窄，不得写成纯 OCS 光度贡献。
3. 修正 `feature_definitions.json` 与脚本导出逻辑：
   - 推荐保留 `feature_definitions.json` 为预注册静态定义；
   - 脚本运行态信息另写 `feature_extraction_run_summary.json`；
   - 或确保脚本生成的 definitions 完整保留 config_id/group/description/expected_n_records/pre_registered_date 等字段。
4. 保持 14 个配置的 config_name、claim_class、feature_keys、dim、c2_participant 不变。
5. 输出 FIX01 执行报告：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/55_1C-E29-FIX01_特征定义schema与claim边界修正_Claude执行报告.md

红线：
- 不运行 feature_extract_ocs.py。
- 不生成 enhanced_ocs_features.npz。
- 不启动 C2/C3。
- 不改 manifest/split manifest。
- 不写论文正文。
- 不启动 B1/GGX、三轴小项目、路线二/三/四。
```

