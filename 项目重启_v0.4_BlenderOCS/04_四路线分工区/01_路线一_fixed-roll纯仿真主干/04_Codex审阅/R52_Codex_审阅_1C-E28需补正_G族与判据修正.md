# R52 Codex 审阅：1C-E28 需补正，G 族与判据修正

最后更新：2026-06-25  
审阅端：Codex  
被审阅报告：`02_Claude输出/52_1C-E28_OCS特征增强方案设计_Claude执行报告.md`

---

## 0. 裁决

```text
1C-E28：NEEDS FIX
C 方案设计方向：基本可行
C1 代码实现：NOT RELEASED
C2 训练筛选：NOT RELEASED
C3 joint 复验：NOT RELEASED
下一步：1C-E28-FIX01，仅修正方案，不写代码、不抽特征、不训练
```

E28 完成了 OCS manifest 字段盘点、派生特征族设计、预注册配置和 C1/C2/C3 阶段协议，整体方向可继续。但当前方案存在两个必须补正的问题：`G` 几何特征族在当前 phase63 数据中实际为常量，不能按报告中口径解释；`yaw_acc > 0%` 触发 C3 的判据过宽，容易产生偶然命中或多配置筛选偏差。

---

## 1. 审阅通过项

### 1.1 manifest 字段盘点基本正确

Codex 抽查 `v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_fullrun.json` 后确认，报告列出的字段基本存在：

- `ocs_total`
- `ocs_per_part`
- `n_pixels_camera_visible`
- `n_pixels_nol_positive`
- `n_pixels_sun_visible`
- `n_pixels_contributing`
- `n_pixels_per_part`
- `sun_dir`
- `det_dir`
- `yaw_deg`
- `pitch_deg`

其中 `yaw_deg` / `pitch_deg` 只能作为标签或分析字段，不得作为输入特征。E28 已正确标注这一红线。

### 1.2 R / I / N / L 特征族方向基本成立

以下设计可以保留：

- `R`：per-part / total 比率；
- `I`：部件间比值；
- `N`：按像素数归一化的 OCS density；
- `L`：log / log-ratio 稳定化；
- `M`：非几何特征组合。

但后续实现时必须明确：

- 所有 epsilon、clip、zero fallback 是预注册常数；
- 标准化只能使用训练集统计量；
- 不得根据 C2 中间结果删减配置；
- 不得用 test split 统计量参与任何归一化或特征选择。

---

## 2. Finding 1：G 族几何特征在当前数据中是常量

Codex 对当前 OCS manifest 做了文件级抽查：

```text
unique sun_dir = 1
unique det_dir = 1
unique geom_id = 1 (phase63)
unique yaw_deg = 72
unique pitch_deg = 37
```

因此，在当前 B0 phase63 fullrun 数据中：

```text
sun_dir / det_dir 是全数据集常量，不随 yaw/pitch 变化。
```

这意味着 E28 中关于 `G1 phase_angle_cos`、`G2 sun_z`、`G3 det_z` 的解释不成立：

- 它们不会提供 yaw 相关几何先验；
- 它们不会编码 yaw；
- 它们作为模型输入只会是常量列；
- 若后续把它们做成非零信息源，说明实现中可能错误地使用了标签、坐标变换或其他泄漏字段。

处理要求：

```text
1. E28-FIX01 必须把 G 族改为“常量字段 sanity check / 不进入 C2 主评估”。
2. 不得把 G 族写成 OCS+geometry baseline。
3. 不得把 sun_dir/det_dir 转到 body frame，除非明确承认需要 yaw/pitch 标签；当前阶段禁止这样做。
4. 预注册 14 配置中应移除 G_geometry_3d，或保留为“expected-constant negative control”，但不计入 C2 筛选。
```

---

## 3. Finding 2：P 族像素计数不是 OCS 光度特征

E28 将 `P` 族标注为纯几何像素占比，这个判断本身可以保留；但其论文口径必须收窄。

这些字段来自可见性/贡献像素统计，属于：

```text
visibility / projected geometry features
```

而不是严格意义上的：

```text
photometric OCS features
```

处理要求：

```text
1. P 族必须单独标为 visibility-only control。
2. P 与 R/N/L 混合后的 M2/M5/M6 不得被称为 OCS-only。
3. 若 P 或含 P 的 mixed 配置取得正结果，只能写成“visibility-derived geometry information helps”，不能写成“OCS photometric channel helps”。
4. 只有不含 P/G 的 R/I/N/L/M 配置，才可作为 photometric-OCS-derived feature 讨论。
```

---

## 4. Finding 3：C2 触发 C3 的成功判据过宽

E28 当前写法：

```text
weak_positive: 0% < yaw_acc < 10% -> 触发 C3
```

这个判据过宽。yaw 是 72 类分类，随机命中率约为：

```text
1 / 72 = 1.39%
```

在多配置筛选下，只要任一配置出现一个或几个偶然命中，就可能触发 C3。当前 `>0%` 判据会把这种偶然命中误当成可继续信号。

处理要求：

```text
1. strong_positive 建议保持 yaw_acc >= 10%，且 yaw_cmae / within-k 指标同步改善。
2. weak_positive 不得只用 >0%；建议改为：
   - yaw_acc >= max(3%, 2x random chance)，且
   - yaw_cmae 优于 baseline，或 yaw_within_3_bins 明显优于 baseline，且
   - 至少在一个额外 split 或 bootstrap/permutation 检查中不是偶然波动。
3. 仅有单个样本命中不得触发 C3。
4. 多配置筛选必须报告全部 14 配置，不能只报告最好配置。
5. C3 触发前必须经过 Codex 审阅，不允许 Claude 自动触发。
```

---

## 5. Finding 4：预注册配置需要分层命名

当前 14 个配置可以保留大部分，但必须分层：

```text
A. photometric OCS-derived:
   baseline_4dim, R, I, N, L, M1, M3, M4

B. visibility-derived control:
   P, M5, 含 P 的 M2/M6

C. constant geometry sanity check:
   G_geometry_3d（建议不进入主筛选）
```

处理要求：

```text
1. E28-FIX01 应输出修正版配置表。
2. 每个配置必须标注 claim class：
   - photometric OCS
   - visibility control
   - mixed OCS+visibility
   - constant sanity check
3. 后续报告中所有结论必须按 claim class 分开写。
```

---

## 6. E28-FIX01 执行范围

允许：

```text
1. 修正 E28 方案文本；
2. 修改 G 族解释与配置表；
3. 收窄 P 族和 mixed 族的论文 claim；
4. 修正 C2/C3 成功/失败判据；
5. 输出修正版方案报告。
```

禁止：

```text
1. 写代码；
2. 抽取特征；
3. 训练模型；
4. 修改 manifest 或数据；
5. 运行 C1/C2/C3；
6. 写论文正文；
7. 启动 B1/GGX；
8. 启动三轴小项目；
9. 启动路线二/三/四。
```

---

## 7. 给 Claude 的下一步短提示词

```text
执行 1C-E28-FIX01：OCS 特征增强方案补正。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R52_Codex_审阅_1C-E28需补正_G族与判据修正.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/52_1C-E28_OCS特征增强方案设计_Claude执行报告.md
- v0.4_results/01_fullrun/postprocess/ocs_manifest_v0_4_fullrun.json

任务：
1. 只修正方案文本，不写代码、不抽特征、不训练。
2. 修正 G 族：当前 phase63 数据中 sun_dir/det_dir 为常量，只能作为常量 sanity check，不得作为几何先验或 C2 主评估特征。
3. 修正 P 族：P 是 visibility / projected geometry control，不是 photometric OCS；含 P 的 mixed 配置不得写成 OCS-only 结论。
4. 修正 C2 判据：
   - strong_positive: yaw_acc >= 10%，且 yaw_cmae / within-k 指标同步改善；
   - weak_positive: yaw_acc >= max(3%, 2x random chance)，且至少通过额外 split、bootstrap 或 permutation 检查之一；
   - 单个样本命中不得触发 C3；
   - C3 必须经 Codex 审阅后才可触发。
5. 输出修正版配置表，给每个配置标注 claim class：
   photometric OCS / visibility control / mixed OCS+visibility / constant sanity check。
6. 输出到：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/53_1C-E28-FIX01_OCS特征方案补正_Claude执行报告.md

红线：
- 不写论文正文。
- 不写代码。
- 不运行特征提取或训练。
- 不启动 B1/GGX。
- 不启动三轴小项目。
- 不启动路线二/三/四。
- 不把方案设计写成已验证结论。
- 若输出过长，按 Part 1/2/3... 分段写入，直到文件完整。
```

