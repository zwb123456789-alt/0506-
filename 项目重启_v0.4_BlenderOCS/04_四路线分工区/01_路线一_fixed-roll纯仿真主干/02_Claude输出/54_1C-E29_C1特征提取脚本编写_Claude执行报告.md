# 54 1C-E29：OCS 特征提取脚本编写 Claude 执行报告

最后更新：2026-06-25  
执行端：Claude  
依据审阅：`04_Codex审阅/R53_Codex_审阅_1C-E28-FIX01通过并放行E29_C1脚本编写.md`

**状态：脚本已编写，未运行。C2/C3 仍为 NOT RELEASED。**

---

## 0. 产物清单

```text
代码：
  06_v0.4_code/07_training/feature_extract_ocs.py    ← 特征提取脚本

数据定义：
  v0.4_results/04_ocs_features/feature_definitions.json  ← 预注册特征定义
```

## 1. 脚本结构

```text
feature_extract_ocs.py 包含以下函数族：

纯特征函数（per-record，无状态）：
  compute_ocs_features_baseline(rec)     → 4 维原始 OCS
  compute_ocs_features_R_ratio(rec)      → R 族：per-part/total 比率
  compute_ocs_features_I_interpart(rec)  → I 族：部件间比值
  compute_ocs_features_N_density(rec)    → N 族：per-pixel 平均 OCS
  compute_ocs_features_P_pixelfrac(rec)  → P 族：纯几何像素占比
  compute_ocs_features_L_log(rec, ...)   → L 族：log/log-ratio 稳定化
  compute_ocs_features_G_constant(rec)   → G 族：constant sanity check

编排函数：
  compute_all_raw_features(rec)          → 单条 record 全特征 OrderedDict
  build_config_matrix(name, keys, feats) → 构建指定配置的 (n, d) 矩阵

入口函数：
  extract_all_candidate_features(...)    → 主流程
  load_enhanced_features(npz_path)       → 供 C2 训练加载
  load_feature_definitions(json_path)    → 供 C2 训练加载

常量自检：
  run_constant_sanity_check(all_features) → 验证 phase_angle_cos 为常量
```

## 2. 预注册配置确认

```text
A 组 photometric OCS (9 configs, #01-#09):
  01 baseline_4dim          4-dim  对照基线
  02 R_ratio_2d             2-dim  两部件比率
  03 R_ratio_3d             3-dim  三部件比率
  04 I_interpart_1d         1-dim  部件间比值
  05 N_density_3d           3-dim  per-pixel 平均
  06 L_logratio_3d          3-dim  log 稳定化
  07 M1_ratio_log_5d        5-dim  比率+log 精简组合
  08 M3_density_ratio_5d    5-dim  密度+比率 精简组合
  09 M4_log_density_ratio_9d 9-dim 综合 photometric OCS

B 组 visibility control (2 configs, #10-#11):
  10 P_pixelfrac_3d         3-dim  纯几何像素占比
  11 M5_pixelfrac_only_4d   4-dim  扩展纯几何

C 组 mixed OCS+visibility (2 configs, #12-#13):
  12 M2_ratio_pixelfrac_5d  5-dim  比率+像素占比混合
  13 M6_all_nongeo_13d      13-dim 全量非几何特征

D 组 constant sanity check (1 config, #14):
  14 constant_check_1d      1-dim  常量自检（不参与 C2）
```

## 3. 关键设计决策

```text
1. 所有 epsilon/clip/fallback 硬编码为预注册常数，不从数据学习。
2. 不做任何归一化（标准化留给 C2 训练 per-fold）。
3. 特征计算为纯函数，无全局状态。
4. .npz 输出包含 record_ids 数组以支持与 split_manifest 的 record_id 对齐。
5. R 族在 ocs_total < EPSILON 时回退到 [1/3, 1/3, 1/3] 并设置 r_valid=0。
6. P 族独立于 OCS 光度值，仅使用像素计数字段。
7. G 族降级为 constant sanity check，不参与 C2。
```

## 4. 脚本未运行

- 脚本已编写完成但未执行。
- 需在 Codex 审阅通过后，由 Claude 在 C2 准备阶段运行以下验证：
  ```
  python feature_extract_ocs.py
  ```
- 运行后应确认：
  - 2664 records 全量处理无报错
  - constant sanity check 输出 PASS
  - feature_definitions.json 的 raw_feature_fields 与脚本输出一致

## 5. 红线确认

- [x] 不抽特征（脚本未运行）
- [x] 不训练
- [x] 不改 manifest
- [x] 不运行 C2/C3
- [x] 不写论文正文
- [x] 不启动 B1/GGX
- [x] 不启动三轴小项目
- [x] 不启动路线二/三/四
- [x] 所有常数预注册，未根据数据调整

## 6. 下一步

```text
本报告 + feature_extract_ocs.py + feature_definitions.json
→ 提交 Codex 审阅（R54 或后续编号）
→ 若通过：放行 C2 OCS-only strict yaw_block 筛选
```
