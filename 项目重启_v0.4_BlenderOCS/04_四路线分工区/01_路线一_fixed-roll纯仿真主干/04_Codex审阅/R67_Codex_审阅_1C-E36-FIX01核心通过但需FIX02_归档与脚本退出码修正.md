# R67 Codex 审阅：1C-E36-FIX01 核心通过，但需 FIX02 修正归档与脚本退出码

最后更新：2026-06-26  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  67_1C-E36-FIX01_执行总结.md

06_v0.4_code/08_visualization/
  generate_figure2_fixed.py
  extract_s2_pure_python.py

v0.4_results/05_c2_screening/
  supplementary_table_s2_per_fold_results.csv
  supplementary_table_s2_first10_rows.md
```

同时发现详细报告实际落在错误嵌套路径：

```text
06_v0.4_code/08_visualization/项目重启_v0.4_BlenderOCS/04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  67_1C-E36-FIX01_图表脚本与S2提取修正_Claude执行报告.md
```

---

## 0. 裁决

```text
1C-E36-FIX01: CORE PASS, NEEDS FIX02
Figure 2 split logic: PASS
Figure 2 rendered output: PASS
Figure 2 script exit code: NOT ACCEPTED
S2 extraction script: PASS
S2 CSV output: PASS
Detailed report archive path: NOT ACCEPTED
C3: NOT RELEASED
论文正文正式改写: NOT RELEASED
训练/新实验/训练代码修改: NOT RELEASED
```

E36-FIX01 已修复 R66 的两个核心技术问题：Figure 2 不再使用错误的 Wedge/radians 单环方案，已改为 5-row strip chart；S2 提取脚本已从 `final_metrics.test` 读取真实 per-fold 指标，并生成 65 行 CSV。

但当前仍有两个资产验收问题，不能直接进入成果区稳定状态：

1. `generate_figure2_fixed.py` 在 Windows GBK 控制台下因 `print("✓ ...")` 触发 `UnicodeEncodeError`，脚本生成图后以 exit code 1 退出。作为可执行脚本资产，必须返回 0。
2. 详细修正报告落到了 `06_v0.4_code/08_visualization/项目重启_v0.4_BlenderOCS/.../02_Claude输出/` 的错误嵌套路径，不在规定的 Claude 输出区。

因此本轮不再要求科学内容返工，只要求一次机械 FIX02。

---

## 1. 已通过核验

### 1.1 S2 数据提取通过

Codex 实际运行：

```text
C:\Users\97466\.conda\envs\ocs_sim\python.exe 06_v0.4_code/08_visualization/extract_s2_pure_python.py
```

运行结果：

```text
Extracted 65 fold results (13 configs x 5 folds)
All yaw_acc = 0.00% (verified)
CSV saved to v0.4_results/05_c2_screening/supplementary_table_s2_per_fold_results.csv
Markdown first10 saved to v0.4_results/05_c2_screening/supplementary_table_s2_first10_rows.md
```

Codex 复核 CSV：

```text
rows = 65
unique_configs = 13
folds = 0,1,2,3,4
yaw_nonzero = 0
first row:
  baseline_4dim fold0
  yaw_acc_pct = 0.00
  yaw_cmae_deg = 75.60
  yaw_within3_pct = 6.67
  pitch_acc_pct = 2.70
  yaw_correct_count = 0
  pitch_correct_count = 15
  n_test = 555
```

S2 数据提取逻辑通过。

### 1.2 Figure 2 图像逻辑通过

Codex 实际运行：

```text
C:\Users\97466\.conda\envs\ocs_sim\python.exe 06_v0.4_code/08_visualization/generate_figure2_fixed.py
```

脚本在最后 `print("✓ ...")` 处报错退出，但图像文件已生成：

```text
Figure2_yaw_block_holdout_fixed.png
Figure2_yaw_block_holdout_fixed.pdf
```

Codex 视觉检查 PNG：图像非空，5-row strip chart 可读，train/val/test 三色清晰，test blocks 为：

```text
Fold 0: 0-14
Fold 1: 15-29
Fold 2: 30-43
Fold 3: 44-57
Fold 4: 58-71
```

R65 split 口径通过。

---

## 2. 必须修正的问题

### Major 1：Figure 2 脚本必须返回 exit code 0

当前错误：

```text
UnicodeEncodeError: 'gbk' codec can't encode character '\u2713'
```

触发位置：

```python
print("✓ Figure 2 (fixed) saved: Figure2_yaw_block_holdout_fixed.png/.pdf")
print(f"✓ Aggregate test coverage: {len(test_bins_all)}/72 bins")
print("✓ All 72 bins covered exactly once across 5 folds")
```

FIX02 必须改为 ASCII：

```python
print("[OK] Figure 2 (fixed) saved: Figure2_yaw_block_holdout_fixed.png/.pdf")
print(f"[OK] Aggregate test coverage: {len(test_bins_all)}/72 bins")
print("[OK] All 72 bins covered exactly once across 5 folds")
```

同时建议将图像输出路径改为脚本所在目录或明确的候选资产目录，避免运行时把图输出到任意当前工作目录。例如：

```python
out_dir = Path(__file__).resolve().parent
fig.savefig(out_dir / "Figure2_yaw_block_holdout_fixed.png", dpi=300, bbox_inches="tight")
fig.savefig(out_dir / "Figure2_yaw_block_holdout_fixed.pdf", bbox_inches="tight")
```

### Major 2：详细报告必须归档到正确 Claude 输出区

应存在：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  67_1C-E36-FIX01_图表脚本与S2提取修正_Claude执行报告.md
```

当前实际存在于错误嵌套路径：

```text
06_v0.4_code/08_visualization/项目重启_v0.4_BlenderOCS/04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  67_1C-E36-FIX01_图表脚本与S2提取修正_Claude执行报告.md
```

FIX02 必须把详细报告复制或重写到正确输出区。错误嵌套路径可以保留为误生成痕迹，暂不要求删除；不得使用破坏性清理。

---

## 3. FIX02 范围

```text
1C-E36-FIX02: RELEASED
任务性质: mechanical correction only
```

允许：

```text
1. 修改 generate_figure2_fixed.py 中的非 ASCII print 文本为 ASCII。
2. 可选：将 Figure2 输出路径固定到 06_v0.4_code/08_visualization/ 或明确候选资产目录。
3. 重新运行 generate_figure2_fixed.py，确认 exit code 0，并生成 PNG/PDF。
4. 将详细报告放到正确 Claude 输出区。
5. 生成一个很短的 FIX02 执行说明。
```

禁止：

```text
不得启动 C3。
不得运行训练。
不得修改现有训练/数据管线。
不得重写 Table 1/2/3 或改变 R62/R65 科学口径。
不得写论文正文正式段落。
不得启动三轴小项目或路线二/三/四。
```

---

## 4. 给 Claude 的 FIX02 短提示词

```text
执行 1C-E36-FIX02：机械修正 E36-FIX01 归档路径与 Figure 2 脚本退出码。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R67_Codex_审阅_1C-E36-FIX01核心通过但需FIX02_归档与脚本退出码修正.md
- 06_v0.4_code/08_visualization/generate_figure2_fixed.py
- 06_v0.4_code/08_visualization/extract_s2_pure_python.py

任务：
1. 将 generate_figure2_fixed.py 中所有非 ASCII print 文本改为 ASCII，例如把 "✓" 改成 "[OK]"。
2. 重新运行 generate_figure2_fixed.py，确认 exit code = 0，并报告 PNG/PDF 输出路径和文件大小。
3. 将详细报告 67_1C-E36-FIX01_图表脚本与S2提取修正_Claude执行报告.md 放到正确目录：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
4. 生成一个简短 FIX02 执行说明：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/68_1C-E36-FIX02_归档路径与Figure2脚本退出码修正_Claude执行报告.md

红线：
- 不启动 C3。
- 不运行训练。
- 不改训练/数据管线。
- 不改 R62/R65 科学口径。
- 不写论文正文正式段落。
- 不删除误生成路径，除非后续 Codex 另行要求。
```

---

## 5. 当前状态

```text
E36-FIX01: CORE PASS, pending FIX02
S2 CSV: verified
Figure 2 PNG/PDF: generated and visually checked
Figure 2 script: needs ASCII print fix for clean exit
Detailed report: needs correct archive path
E36 asset package: not yet stable until FIX02 passes
```
