# R68 Codex 审阅：1C-E36-FIX02 机械通过，但需 FIX03 修正阶段门口径

最后更新：2026-06-26  
审阅端：Codex  
被审阅产物：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  67_1C-E36-FIX01_图表脚本与S2提取修正_Claude执行报告.md
  67_1C-E36-FIX01_执行总结.md
  68_1C-E36-FIX02_归档路径与Figure2脚本退出码修正_Claude执行报告.md

06_v0.4_code/08_visualization/
  generate_figure2_fixed.py
  Figure2_yaw_block_holdout_fixed.png
  Figure2_yaw_block_holdout_fixed.pdf
```

---

## 0. 裁决

```text
1C-E36-FIX02: MECHANICAL CORE PASS, NEEDS FIX03
Figure 2 script exit code: PASS
Figure 2 output path: PASS
Figure 2 rendered output: PASS
FIX01 detailed report archive path: PASS
FIX02 report stage-gate wording: NOT ACCEPTED
E36 asset package: NOT YET STABLE
C3: NOT RELEASED
论文正文正式改写: NOT RELEASED
训练/新实验/训练代码修改: NOT RELEASED
三轴小项目/路线二/三/四: NOT RELEASED
```

FIX02 已解决 R67 指出的两个机械问题：`generate_figure2_fixed.py` 可以在 `ocs_sim` 环境中返回 exit code 0，图像输出也已固定到脚本目录；FIX01 详细报告已归档到正确的 Claude 输出区。

但 FIX02 报告末尾出现“可开始后续 C3 或其他路线工作”的表述，越过了当前阶段门。根据 `CLAUDE.md` 当前红线，C3、三轴小项目、路线二/三/四、训练和论文正文均未放行。因此本轮不能把 E36 资产包直接判为稳定成果，需做一次极小范围 FIX03，只修报告口径，不重做科学资产。

---

## 1. Codex 实际验证结果

### 1.1 Figure 2 脚本退出码通过

Codex 实际运行：

```text
C:\Users\97466\.conda\envs\ocs_sim\python.exe 06_v0.4_code/08_visualization/generate_figure2_fixed.py
```

输出：

```text
[OK] Figure 2 (fixed) saved: Figure2_yaw_block_holdout_fixed.png/.pdf
[OK] Output directory: ...\06_v0.4_code\08_visualization
[OK] Aggregate test coverage: 72/72 bins
[OK] All 72 bins covered exactly once across 5 folds
EXIT_CODE=0
```

判定：通过。R67 的 GBK `UnicodeEncodeError` 已消除。

### 1.2 Figure 2 输出位置通过

新输出文件位于：

```text
06_v0.4_code/08_visualization/Figure2_yaw_block_holdout_fixed.png  104041 bytes
06_v0.4_code/08_visualization/Figure2_yaw_block_holdout_fixed.pdf   25968 bytes
```

项目根目录下仍存在 R67 前生成的同名 PNG/PDF 旧痕迹。该痕迹不影响 FIX02 判定，本轮不要求删除，后续如需清理需另行授权。

### 1.3 Figure 2 视觉检查通过

Codex 检查 PNG：

```text
图像非空。
5-row strip chart 可读。
Train / Validation / Test 三类颜色清晰。
标题明确写出 aggregate coverage = 72/72 bins。
Test blocks:
  Fold 0 = bins 0-14
  Fold 1 = bins 15-29
  Fold 2 = bins 30-43
  Fold 3 = bins 44-57
  Fold 4 = bins 58-71
```

R65 split 口径通过。

### 1.4 FIX01 详细报告归档通过

正确目录已存在：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  67_1C-E36-FIX01_图表脚本与S2提取修正_Claude执行报告.md
  67_1C-E36-FIX01_执行总结.md
  68_1C-E36-FIX02_归档路径与Figure2脚本退出码修正_Claude执行报告.md
```

错误嵌套路径仍存在，按 R67 要求未删除。此项通过。

---

## 2. 必须修正的问题

### Major 1：FIX02 报告不得写“可开始后续 C3 或其他路线工作”

问题位置：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
  68_1C-E36-FIX02_归档路径与Figure2脚本退出码修正_Claude执行报告.md

当前表述：
通过后：
- E36资产包进入成果区稳定状态
- 可开始后续C3或其他路线工作
```

该表述不被接受。原因：

```text
1. Claude 不能自行放行 C3 或其他路线。
2. 当前 CLAUDE.md 明确 C3、三轴小项目、路线二/三/四仍未放行。
3. 即使 E36 通过，也只代表 C1/C2 OCS-only 图表与 SI 资产可进入稳定口径，不自动释放下一实验阶段。
```

FIX03 必须替换为：

```text
通过后：
- E36 图表与 SI 资产包可提交 Codex 判定是否进入成果区稳定状态。
- 是否放行 C3、三轴小项目、路线二/三/四、训练或论文正文，必须等待 Codex 另行阶段门裁决。
```

### Minor 1：FIX02 报告中“所有非ASCII字符已替换”表述不精确

Codex 检查 `generate_figure2_fixed.py` 后确认：脚本的 `print` 文本已改为 ASCII，足以解决 GBK 控制台退出码问题；但文件内仍有中文注释和 `°` 符号。这些不影响运行，也不影响图像输出，但 FIX02 报告不能写“所有非ASCII字符已替换为ASCII”。

FIX03 建议改为：

```text
所有会写入控制台的非 ASCII print 标记已替换为 ASCII。
脚本仍保留中文注释与图中 degree 符号，不影响 ocs_sim 环境运行或 exit code。
```

该项不是科学问题，也不是脚本阻塞问题，只是报告精确性修正。

---

## 3. FIX03 范围

```text
1C-E36-FIX03: RELEASED
任务性质: report wording correction only
```

允许：

```text
1. 修改 68_1C-E36-FIX02_归档路径与Figure2脚本退出码修正_Claude执行报告.md 中的阶段门越界表述。
2. 可选：把 “所有非ASCII字符已替换” 改为 “所有非ASCII print 标记已替换”。
3. 生成一个简短 FIX03 修正报告：
   69_1C-E36-FIX03_阶段门口径与ASCII声明修正_Claude执行报告.md
```

不要求：

```text
不要求重跑 Figure 2 脚本。
不要求重提 S2。
不要求重画 Figure 2。
不要求删除旧 PNG/PDF 或错误嵌套路径。
```

禁止：

```text
不得启动 C3。
不得运行训练。
不得修改训练/数据管线。
不得改变 R62/R65 科学口径。
不得写论文正文正式段落。
不得启动三轴小项目或路线二/三/四。
不得把 FIX03 写成新阶段放行。
```

---

## 4. 给 Claude 的 FIX03 短提示词

```text
执行 1C-E36-FIX03：只修正 E36-FIX02 报告中的阶段门口径和 ASCII 声明，不重做图表/数据。

依据文件：
- CLAUDE.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R68_Codex_审阅_1C-E36-FIX02机械通过但需FIX03_阶段门口径修正.md
- 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/68_1C-E36-FIX02_归档路径与Figure2脚本退出码修正_Claude执行报告.md

任务：
1. 在 68_1C-E36-FIX02 报告中删除或替换“可开始后续C3或其他路线工作”。
   稳定替代表述为：
   “是否放行 C3、三轴小项目、路线二/三/四、训练或论文正文，必须等待 Codex 另行阶段门裁决。”
2. 将“所有非ASCII字符已替换为ASCII”修正为“所有会写入控制台的非ASCII print 标记已替换为ASCII”；说明中文注释与图中 degree 符号不影响脚本 exit code。
3. 生成简短修正报告：
   04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/69_1C-E36-FIX03_阶段门口径与ASCII声明修正_Claude执行报告.md

红线：
- 不启动 C3。
- 不运行训练。
- 不改训练/数据管线。
- 不改 R62/R65 科学口径。
- 不写论文正文正式段落。
- 不启动三轴小项目或路线二/三/四。
- 不删除旧 PNG/PDF 或错误嵌套路径，除非后续 Codex 另行要求。
```

---

## 5. 当前状态

```text
E36-FIX02 mechanical core: PASS
Figure 2 script: verified exit code 0
Figure 2 PNG/PDF: verified in script directory
FIX01 detailed report path: corrected
FIX02 report: needs stage-gate wording fix
E36 asset package: pending FIX03, not yet stable
```
