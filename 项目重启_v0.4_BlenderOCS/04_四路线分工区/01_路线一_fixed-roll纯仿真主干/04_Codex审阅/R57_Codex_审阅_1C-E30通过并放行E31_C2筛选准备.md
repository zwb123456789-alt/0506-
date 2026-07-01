# R57 Codex 审阅：1C-E30 通过并放行 E31

最后更新：2026-06-25  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/57_1C-E30_C1特征提取正式执行_Claude执行报告.md
v0.4_results/04_ocs_features/feature_definitions.json
v0.4_results/04_ocs_features/feature_extraction_run_summary.json
v0.4_results/04_ocs_features/enhanced_ocs_features.npz
```

---

## 0. 裁决

```text
1C-E30：PASS
C1 OCS 特征提取运行产物：PASS
E31 C2 筛选准备：RELEASED
C2 正式训练筛选：NOT RELEASED
C3 joint 复验：NOT RELEASED
```

E30 已成功完成 C1 特征提取正式执行。预注册定义未被覆盖，运行态 summary 与 npz 特征矩阵一致，record_id 与 fullrun manifest 顺序一致，14 个配置矩阵均通过 shape / dtype / finite 检查。

当前只放行 `1C-E31`：C2 OCS-only 筛选准备，包括读取增强特征、设计/编写 C2 训练脚本、制定结果输出 schema 和 dry-run/静态检查。不得直接启动 C2 训练筛选。

---

## 1. 审阅检查结果

### 1.1 文件完整性

`v0.4_results/04_ocs_features/` 当前包含：

```text
feature_definitions.json              10033 bytes, 2026-06-25 16:58:39
feature_extraction_run_summary.json    6387 bytes, 2026-06-25 17:11:00
enhanced_ocs_features.npz            595218 bytes, 2026-06-25 17:11:00
```

`feature_definitions.json` 时间戳早于运行产物，预注册定义未被覆盖。

### 1.2 Summary 验证

运行态 summary 关键字段：

```text
n_records = 2664
expected_n_records = 2664
record_count_match = true
record_id_unique = true
record_id_count = 2664
sanity_check.is_constant = true
sanity_check.unique_values = 1
sanity_check.value = 0.4522487223148346
```

通过。

### 1.3 NPZ 实物审计

只读审计结果：

```text
expected_names_equal_npz_names = True
n_records_def_summary_manifest_npz = 2664 / 2664 / 2664 / 2664
record_ids_unique = True
record_ids_match_manifest_order = True
summary_record_count_match = True
summary_record_id_unique = True
issues = []
```

`record_ids` 与 `ocs_manifest_v0_4_fullrun.json` 中 `records` 顺序完全一致。

### 1.4 配置矩阵检查

14 个配置全部为 `float32`，shape 与预注册定义一致，无 NaN/Inf：

```text
baseline_4dim              (2664, 4)   finite True
R_ratio_2d                 (2664, 2)   finite True
R_ratio_3d                 (2664, 3)   finite True
I_interpart_1d             (2664, 1)   finite True
N_density_3d               (2664, 3)   finite True
L_logratio_3d              (2664, 3)   finite True
M1_ratio_log_5d            (2664, 5)   finite True
M3_density_ratio_5d        (2664, 5)   finite True
M4_log_density_ratio_9d    (2664, 9)   finite True
P_pixelfrac_3d             (2664, 3)   finite True
M5_pixelfrac_only_4d       (2664, 4)   finite True
M2_ratio_pixelfrac_5d      (2664, 5)   finite True
M6_all_nongeo_13d          (2664, 13)  finite True
constant_check_1d          (2664, 1)   finite True
```

`constant_check_1d` 唯一值：

```text
[0.4522487223148346]
```

符合 phase63 fixed-roll 常量自检预期。

### 1.5 归因边界仍有效

预注册 definitions 中 N/M3/M4 description 保持 visibility-normalized 口径：

```text
N_density_3d / M3_density_ratio_5d / M4_log_density_ratio_9d
均不得写成 pure photometric-only evidence。
```

P/M5 仍为 `visibility control`，M2/M6 仍为 `mixed OCS+visibility`，`constant_check_1d` 不参与 C2。

---

## 2. E31 放行范围

放行 `1C-E31`：

```text
C2 OCS-only 筛选准备
```

允许：

```text
读取 enhanced_ocs_features.npz
读取 feature_definitions.json / feature_extraction_run_summary.json
读取已存在的 circ_yawblock split manifests
编写 C2 OCS-only 筛选脚本
编写 enhanced feature dataset / loader
制定 per-config 结果 JSON schema
制定 c2_screening_summary.json schema
做静态检查、import 检查、单 batch/dry-run 检查
```

禁止：

```text
正式训练 13 个配置
生成 C2 训练结果
启动 C3 joint 复验
改 feature_definitions.json
改 enhanced_ocs_features.npz
改 manifest / split manifest
写论文正文
启动 B1/GGX
启动三轴小项目
启动路线二/三/四
```

E31 通过 Codex 审阅后，才可放行 E32 C2 正式筛选。

---

## 3. E31 技术要求

E31 需要优先解决训练前接口，不得把 C2 当作普通“直接跑训练”：

```text
1. 数据对齐：
   - 按 record_id 将 split manifest 中的 train/val/test 对齐到 npz record_ids。
   - 若有缺失、重复或顺序错位，必须报错退出。

2. 配置过滤：
   - 只训练 c2_participant=true 的 13 个配置。
   - constant_check_1d 必须排除，只允许作为自检信息进入 summary。

3. 标准化：
   - 每个 fold / 每个配置只用 train split 统计 mean/std。
   - val/test 只能使用 train mean/std。
   - 不得使用全量 2664 的 mean/std。

4. 协议固定：
   - 使用 E25 的 5-fold circular yaw_block split manifests。
   - 训练参数必须预注册在脚本和输出 summary 中。
   - 不做超参搜索，不根据中间结果删减配置。

5. 输出规划：
   - 每个配置、每个 fold 的结果路径必须预先固定。
   - 总汇总 JSON 必须列出 13 个配置全部结果。
   - visibility / mixed / photometric OCS 的 claim class 必须保留到结果文件。
```

---

## 4. 给 Claude 的 E31 短提示词

```text
执行 1C-E31：C2 OCS-only 筛选准备。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R57_Codex_审阅_1C-E30通过并放行E31_C2筛选准备.md
- v0.4_results/04_ocs_features/feature_definitions.json
- v0.4_results/04_ocs_features/feature_extraction_run_summary.json
- v0.4_results/04_ocs_features/enhanced_ocs_features.npz
- v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold*.json

任务：
1. 只做 C2 筛选准备，不正式训练。
2. 编写 C2 OCS-only 筛选脚本和数据 loader：
   - 读取 enhanced_ocs_features.npz
   - 按 record_id 对齐 split manifest
   - 只纳入 c2_participant=true 的 13 个配置
   - 排除 constant_check_1d
   - per fold/per config 使用 train-only mean/std 标准化
3. 固定训练协议、输出目录和 JSON schema：
   - per-config/per-fold 结果 JSON
   - c2_screening_summary.json
   - claim_class 与 feature_keys 必须写入结果
4. 可以做静态检查、import 检查、单 batch/dry-run 检查；不得跑正式训练。
5. 输出执行报告：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/58_1C-E31_C2筛选准备_Claude执行报告.md

红线：
- 不正式训练 13 个配置。
- 不生成 C2 结果。
- 不启动 C3。
- 不改 feature_definitions.json / enhanced_ocs_features.npz / manifest / split manifest。
- 不写论文正文。
- 不启动 B1/GGX、三轴小项目、路线二/三/四。
```

