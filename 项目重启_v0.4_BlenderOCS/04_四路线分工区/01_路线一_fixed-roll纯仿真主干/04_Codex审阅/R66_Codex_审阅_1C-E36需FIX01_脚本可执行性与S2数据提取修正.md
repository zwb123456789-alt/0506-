# R66 Codex 审阅：1C-E36 需 FIX01，修正脚本可执行性与 S2 数据提取

最后更新：2026-06-26  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  66_1C-E36_C1C2_OCS-only图表与SI资产生成_Claude执行报告_Part1.md
  66_1C-E36_C1C2_OCS-only图表与SI资产生成_Claude执行报告_Part2.md
  66_1C-E36_C1C2_OCS-only图表与SI资产生成_Claude执行报告_Part3.md
```

---

## 0. 裁决

```text
1C-E36: NEEDS FIX01
Table 1/2/3 主体: ACCEPTED WITH MINOR CAVEATS
Figure 1/3/4 资产规格: ACCEPTED AS DRAFT
Figure 2 Python script: NOT ACCEPTED
Supplementary Table S2 extraction script/sample: NOT ACCEPTED
C3: NOT RELEASED
论文正文正式改写: NOT RELEASED
训练/新实验/训练代码修改: NOT RELEASED
```

E36 完成了 R65 要求的资产组织：主表、主图规格、SI 表格草案和资产索引均已覆盖；R65 的 yaw-block 稳定口径也基本遵守，即 Figure 2 数据表已使用 aggregate 72/72 yaw bins、per-fold test block 14-15 bins。

但是 E36 同时声称提供了可用于生成图表和 SI 的脚本草案。Codex 抽查后确认：Figure 2 脚本存在实质绘图错误；Supplementary Table S2 数据提取脚本不能正确读取实际 fold result JSON 的指标层级，且示例表含占位/不实 per-fold 数值。该问题会直接影响后续图表/SI 资产生成，因此必须做一次窄范围 FIX01。

---

## 1. 已通过部分

### 1.1 Table 1/2/3 主体可保留

Table 1 LaTeX 与 Markdown 中 `constant_check_1d` 的 C2 状态均为不参与，符合 `feature_definitions.json`：

```text
config_id = 14
config_name = constant_check_1d
c2_participant = false
c2_exclusion_configs = ["constant_check_1d"]
```

Table 2/3 主数值沿用 R62 稳定口径，未发现新的数值性错误：

```text
13 configs x 5 folds = 65 runs
all yaw_acc = 0.00%
within-3 chance-level = 7/72 = 9.72%
pitch_acc = secondary diagnostic
```

Minor caveat：Markdown 中部分符号在终端显示为乱码，后续正式资产生成时应统一为 ASCII 或 LaTeX-safe 表达，例如 `+/-`、`deg`、`Yes/No`，避免复制到论文或 README 后出现编码损坏。

### 1.2 R65 split 口径基本遵守

E36 Figure 2 数据表已正确写为：

```text
Fold 0: test bins 0-14
Fold 1: test bins 15-29
Fold 2: test bins 30-43
Fold 3: test bins 44-57
Fold 4: test bins 58-71
Total test coverage = 15 + 15 + 14 + 14 + 14 = 72/72 bins
```

旧错误 `35/72`、`49% coverage`、`5x7 test bins` 未作为最终口径出现。

---

## 2. 必须修正的问题

### Major 1：Figure 2 Matplotlib 脚本的 Wedge 角度单位错误

E36 Part 2 Figure 2 脚本中：

```python
theta = np.deg2rad(bin_id * bin_width)
width = np.deg2rad(bin_width)
wedge = Wedge((0, 0), 1.0, theta, theta + width, ...)
```

`matplotlib.patches.Wedge` 的 `theta1/theta2` 参数使用 degrees，不是 radians。当前脚本把 5 deg bin 转成约 0.087 deg，实际渲染会把每个 bin 画得极窄，圆环分块图不可信。

此外，脚本在 `projection='polar'` 的 axes 上直接 `add_patch(Wedge(...))`，坐标变换语义不清；同时在单一圆环上叠加 5 个 folds 的 test 和 validation block，会产生语义遮挡，因为一个 bin 可以在某 fold 是 validation、在另一个 fold 是 test。若要展示 5-fold split，建议使用：

```text
方案 A：5 个同心环，每个 fold 一环，颜色区分 train/val/test；
方案 B：5 行 strip chart，每行 72 bins，颜色区分 train/val/test；
方案 C：单环只展示 aggregate test coverage，再另附 fold table。
```

推荐 FIX01 使用方案 A 或 B。不要继续使用当前单环叠加 5 folds 的 Wedge 写法。

### Major 2：Supplementary Table S2 提取脚本读取了错误 JSON 层级

E36 Part 3 S2 脚本写为：

```python
'Yaw Acc (%)': fold_data.get('test_yaw_acc', 0.0) * 100,
'Yaw CMAE (deg)': fold_data.get('test_yaw_circular_mae_deg', 0.0),
'Within-3 (%)': fold_data.get('test_yaw_within_3_bins_rate', 0.0) * 100,
'Pitch Acc (%)': fold_data.get('test_pitch_acc', 0.0) * 100,
'Yaw Correct Count': fold_data.get('test_yaw_correct_count', 0),
'Pitch Correct Count': fold_data.get('test_pitch_correct_count', 0)
```

实际 fold result JSON 的 test 指标位于：

```text
final_metrics.test.yaw_acc
final_metrics.test.pitch_acc
final_metrics.test.yaw_circular_mae_deg
final_metrics.test.yaw_within_3_bins_rate
final_metrics.test.yaw_correct_count
final_metrics.test.pitch_correct_count
```

Codex 抽查：

```text
v0.4_results/05_c2_screening/baseline_4dim/baseline_4dim_fold0_result.json
final_metrics.test.yaw_circular_mae_deg = 75.60360431671143
final_metrics.test.yaw_within_3_bins_rate = 0.06666667014360428
final_metrics.test.pitch_acc = 0.027027027681469917
final_metrics.test.yaw_correct_count = 0
final_metrics.test.pitch_correct_count = 15
```

因此 E36 的 S2 脚本若直接运行，会输出默认 0 或错误值，不能作为 SI 数据提取资产通过。

### Major 3：Supplementary Table S2 示例行含占位/不实 per-fold 数值

E36 Part 3 S2 示例表写：

```text
baseline_4dim fold0: Yaw CMAE = 89.25, Within-3 = 3.57, Pitch Acc = 2.70
```

其中 `89.25` 是 `baseline_4dim` 的 5-fold aggregate yaw CMAE，不是 fold0 值；fold0 真实 `yaw_circular_mae_deg` 为约 `75.60`，within-3 约 `6.67%`，pitch acc 约 `2.70%`。

FIX01 中若不能生成真实 65 行，就不要放“前 10 行示例数值”；可改为列结构示例，或用脚本实际输出的真实前 10 行。

### Major 4：summary JSON 编码/路径容错未处理

Codex 在本机使用 Python 按 `encoding='utf-8'` 读取 `c2_screening_summary.json` 时遇到编码异常。原因是 summary 中包含历史乱码绝对路径。E36 的脚本应避免依赖这些绝对路径，或使用容错读取：

```python
json.loads(path.read_text(encoding="utf-8", errors="replace"))
```

更稳妥的做法是从项目根目录拼接相对路径：

```python
result_path = base / "v0.4_results" / "05_c2_screening" / config_name / f"{config_name}_fold{fold_id}_result.json"
```

不要直接信任 `summary['results_summary'][...]['fold_results'][...]['result_path']` 中的绝对路径。

---

## 3. FIX01 范围

E36-FIX01 只需修正脚本可执行性与 S2 数据提取，不需要重写全部 E36。

必须修正：

```text
1. Figure 2 绘图脚本：
   - 改为可执行的 Matplotlib 方案。
   - 推荐 5-row strip chart 或 5-ring concentric chart。
   - 明确 train/val/test 颜色。
   - 使用 R65 fold bins，aggregate 72/72 coverage。
   - 输出 PNG/PDF/SVG 至候选资产目录或在报告中给出完整可复制脚本。

2. Supplementary Table S2 extraction script：
   - 从 final_metrics.test 读取指标。
   - 处理 c2_screening_summary.json 编码/路径问题。
   - 输出 65 rows。
   - 至少在报告中给出真实前 5-10 行，不能用占位值。

3. 删除或替换 E36 Part 3 中的占位 per-fold 示例表。

4. 在资产索引中把 Figure 2 与 S2 状态从“完成”改为“FIX01 修正后完成”，并说明是否实际运行脚本。
```

可以保留：

```text
Table 1/2/3 LaTeX 与 Markdown 主体
Figure 1 DOT 草案
Figure 3 scatter 脚本草案
Figure 4 pitch bar 脚本草案
Table S1 raw feature definitions 主体
Figure S1 all-zero yaw bar 草案
R65 split 标准口径
```

---

## 4. 建议修正实现

### 4.1 Figure 2 推荐脚本结构

建议使用 5 行 x 72 bin strip chart：

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

folds = [
    {"fold": 0, "val": range(65, 72), "test": range(0, 15), "train": list(range(15, 65))},
    {"fold": 1, "val": range(8, 15), "test": range(15, 30), "train": list(range(0, 8)) + list(range(30, 72))},
    {"fold": 2, "val": range(23, 30), "test": range(30, 44), "train": list(range(0, 23)) + list(range(44, 72))},
    {"fold": 3, "val": range(37, 44), "test": range(44, 58), "train": list(range(0, 37)) + list(range(58, 72))},
    {"fold": 4, "val": range(51, 58), "test": range(58, 72), "train": list(range(0, 51))},
]

mat = np.zeros((5, 72), dtype=int)  # 0 train, 1 val, 2 test
for f in folds:
    mat[f["fold"], list(f["val"])] = 1
    mat[f["fold"], list(f["test"])] = 2

cmap = ListedColormap(["#eeeeee", "#9ecae1", "#3182bd"])
fig, ax = plt.subplots(figsize=(7.2, 1.8))
ax.imshow(mat, aspect="auto", cmap=cmap, interpolation="nearest")
ax.set_yticks(range(5))
ax.set_yticklabels([f"Fold {i}" for i in range(5)])
ax.set_xticks(range(0, 72, 6))
ax.set_xticklabels([str(i) for i in range(0, 72, 6)])
ax.set_xlabel("Yaw bin (5 deg per bin)")
ax.set_title("Five-fold circular yaw-block holdout")
```

这比单环叠加更清楚，也不会出现 test/val 遮挡。

### 4.2 S2 推荐读取逻辑

```python
import json
from pathlib import Path
import pandas as pd

base = Path(".").resolve()
summary_path = base / "v0.4_results" / "05_c2_screening" / "c2_screening_summary.json"
summary = json.loads(summary_path.read_text(encoding="utf-8", errors="replace"))

rows = []
for cfg in summary["results_summary"]:
    config_name = cfg["config_name"]
    for fr in cfg["fold_results"]:
        fold_id = fr["fold_id"]
        result_path = base / "v0.4_results" / "05_c2_screening" / config_name / f"{config_name}_fold{fold_id}_result.json"
        fold_data = json.loads(result_path.read_text(encoding="utf-8", errors="replace"))
        test = fold_data["final_metrics"]["test"]
        rows.append({
            "config_name": config_name,
            "fold_id": fold_id,
            "yaw_acc_pct": test["yaw_acc"] * 100,
            "yaw_cmae_deg": test["yaw_circular_mae_deg"],
            "yaw_within3_pct": test["yaw_within_3_bins_rate"] * 100,
            "pitch_acc_pct": test["pitch_acc"] * 100,
            "yaw_correct_count": test["yaw_correct_count"],
            "pitch_correct_count": test["pitch_correct_count"],
            "n_test": test["n_samples"],
        })

df = pd.DataFrame(rows)
assert len(df) == 65, len(df)
assert (df["yaw_acc_pct"] == 0).all()
df.to_csv("supplementary_table_s2_per_fold_results.csv", index=False)
```

FIX01 可以采用等价实现，但必须满足字段层级正确、65 行、yaw_acc 全 0 三项。

---

## 5. 下一步放行

```text
1C-E36-FIX01: RELEASED
任务性质: narrow correction only
C3: NOT RELEASED
论文正文正式改写: NOT RELEASED
训练/新实验/训练代码修改: NOT RELEASED
```

E36-FIX01 完成并通过后，才可把 E36 资产包分流进成果区。当前 E36 不进入成果区稳定状态。

---

## 6. 给 Claude 的 E36-FIX01 短提示词

```text
执行 1C-E36-FIX01：修正 E36 图表/SI 资产包中的脚本可执行性与 S2 数据提取问题。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R66_Codex_审阅_1C-E36需FIX01_脚本可执行性与S2数据提取修正.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/66_1C-E36_C1C2_OCS-only图表与SI资产生成_Claude执行报告_Part1.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/66_1C-E36_C1C2_OCS-only图表与SI资产生成_Claude执行报告_Part2.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/66_1C-E36_C1C2_OCS-only图表与SI资产生成_Claude执行报告_Part3.md
- v0.4_results/05_c2_screening/c2_screening_summary.json
- v0.4_results/05_c2_screening/{config}/{config}_fold{id}_result.json
- v0.4_results/03_training_baseline/e25_multifold_yawblock/split_manifest_circ_yawblock_fold*.json

任务：
1. 生成一个 FIX01 修正报告，不重写全部 E36。
2. 修正 Figure 2 Python 绘图脚本：不要用当前 Wedge radians 写法；推荐 5-row strip chart 或 5-ring chart；必须使用 R65 split bins，显示 train/val/test，aggregate coverage = 72/72。
3. 修正 Supplementary Table S2 提取脚本：从 final_metrics.test 读取 yaw_acc、yaw_circular_mae_deg、yaw_within_3_bins_rate、pitch_acc、yaw_correct_count、pitch_correct_count、n_samples。
4. 处理 c2_screening_summary.json 的编码/绝对路径问题；推荐从项目根目录拼接相对 result 路径。
5. 给出真实提取后的前 5-10 行示例，或明确报告脚本未运行且不提供示例数值；不得使用占位 per-fold 数值。
6. 更新资产索引中 Figure 2 和 S2 的状态说明。

输出到：
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  67_1C-E36-FIX01_图表脚本与S2提取修正_Claude执行报告.md

红线：
- 不启动 C3。
- 不运行训练。
- 不改现有训练/数据管线代码。
- 不做后验 OCS-only 架构/超参/特征搜索。
- 不写 Results/Abstract/Introduction/Discussion 正文正式段落。
- 不启动三轴小项目或路线二/三/四。
- 不再使用 35/72、49% coverage、5x7 test bins、Fold 4 wrap 等旧错误 split 表述。
```
