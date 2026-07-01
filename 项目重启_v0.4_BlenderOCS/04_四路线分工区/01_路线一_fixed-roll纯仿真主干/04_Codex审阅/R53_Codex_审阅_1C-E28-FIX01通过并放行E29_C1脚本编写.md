# R53 Codex 审阅：1C-E28-FIX01 通过并放行 E29 C1 脚本编写

最后更新：2026-06-25  
审阅端：Codex  
被审阅报告：`02_Claude输出/53_1C-E28-FIX01_OCS特征方案补正_Claude执行报告.md`

---

## 0. 裁决

```text
1C-E28-FIX01：PASS
方案文本补正：PASS
C1 代码实现：NOT RELEASED
C2 训练筛选：NOT RELEASED
C3 joint 复验：NOT RELEASED
下一步：1C-E29，OCS 特征提取脚本编写
```

E28-FIX01 已把 R52 指出的四项问题闭合：G 族改为常量 sanity check，P 族改为 visibility control，mixed 配置按 claim class 分层，C2/C3 判据收紧。当前方案已经可以进入 C1 脚本编写阶段，但仍不能开始抽特征、训练或任何后续实验执行。

---

## 1. 审阅通过项

### 1.1 G 族修正合格

R53 确认修正成立：

- `sun_dir / det_dir` 在全量 2664 条记录中均为常量；
- 原 `G_geometry_3d` 已从 C2 主评估移除；
- 新增 `constant_check_1d` 仅用于 C1 代码自检；
- G 族不再冒充几何先验，不再作为 C2 主筛选特征。

### 1.2 P 族与 mixed 族 claim class 合格

修正后的分层清晰：

- `P` 归为 `visibility control`；
- `M2/M5/M6` 按混合类处理；
- `photometric OCS` 与 `visibility control` 不再混写；
- 若含 P 配置出现正结果，必须分解归因。

### 1.3 C2/C3 判据收紧合格

修正后的判据明显更稳健：

- `strong_positive` 继续以 `yaw_acc >= 10%` 为强信号；
- `weak_positive` 至少要求 `yaw_acc >= max(3%, 2x random chance)` 并配合额外 split / bootstrap / permutation 验证之一；
- 单样本命中不再可触发 C3；
- C3 仍必须经 Codex 审阅放行。

### 1.4 配置分层合格

新的 A/B/C/D 四组更适合后续报告：

- A：photometric OCS-derived
- B：visibility-derived control
- C：mixed OCS+visibility
- D：constant sanity check

这能避免后续把 mixed 或 visibility 结果误写成纯 OCS 贡献。

---

## 2. 可继续与禁止边界

E28-FIX01 现在可以进入 C1 脚本编写，但必须保持以下边界：

允许：

- 只写 OCS 特征提取脚本方案；
- 只实现字段读取、特征计算函数、配置导出；
- 只做常量 sanity check；
- 只做预注册配置的代码骨架。

禁止：

- 抽特征；
- 训练模型；
- 运行 C2/C3；
- 修改 manifest 或数据；
- 写论文正文；
- 启动 B1/GGX/三轴/路线二三四。

---

## 3. 下一步放行：1C-E29

放行 `1C-E29`：

```text
OCS 特征提取脚本编写
```

要求只做脚本实现，不运行脚本、不做实验。脚本应包含：

- `compute_ocs_features_<family>()`；
- `extract_all_candidate_features()`；
- `feature_definitions.json` 导出；
- constant sanity check 对应的只读验证逻辑；
- 预注册 13 个参与 C2 的配置 + 1 个常量检查配置。

---

## 4. 给 Claude 的下一步短提示词

```text
执行 1C-E29：OCS 特征提取脚本编写。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R53_Codex_审阅_1C-E28-FIX01通过并放行E29_C1脚本编写.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/53_1C-E28-FIX01_OCS特征方案补正_Claude执行报告.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/52_1C-E28_OCS特征增强方案设计_Claude执行报告.md
- v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_fullrun.json

任务：
1. 只写脚本，不抽特征、不训练、不运行任何实验。
2. 实现纯函数式 OCS 特征提取脚本：
   - `compute_ocs_features_<family>()`
   - `extract_all_candidate_features()`
   - feature definitions 导出
   - constant sanity check 逻辑
3. 输出 feature_definitions.json 和脚本文件，但不要执行。
4. 保持 13 个 C2 配置 + 1 个 constant check 配置的分层。
5. 所有标准化、epsilon、clip、fallback 都按预注册常数写死，不得根据中间结果调整。
6. 输出到：
   06_v0.4_code/07_training/feature_extract_ocs.py
   v0.4_results/04_ocs_features/feature_definitions.json

红线：
- 不抽特征。
- 不训练。
- 不改 manifest。
- 不运行 C2/C3。
- 不写论文正文。
- 不启动 B1/GGX。
- 不启动三轴小项目。
- 不启动路线二/三/四。
- 若输出过长，按 Part 1/2/3... 分段写入，直到文件完整。
```

