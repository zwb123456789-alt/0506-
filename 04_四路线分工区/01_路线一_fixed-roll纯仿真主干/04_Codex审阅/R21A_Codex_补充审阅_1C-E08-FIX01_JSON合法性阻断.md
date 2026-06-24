# R21A Codex 补充审阅：1C-E08-FIX01 JSON 合法性阻断

最后更新：2026-06-23  
审阅端：Codex  
审阅对象：Claude 提交的 `1C-E08-FIX01_shadow_validation修复与重验证`

## 1. 补充结论

```text
1C-E08-FIX01：PARTIAL_PASS，但仍不放行
Phase 0 Step 4：暂不放行
DEPTH_EPSILON_M_FINAL：暂不批准写入冻结 manifest
不得进入 Phase 0 Step 5
```

在 R21 已记录的两个阻断项之外，本次复核新增一个阻断项：当前 `shadow_validation_summary.json` 不是严格合法 JSON，不能作为稳定验证产物进入成果区。

## 2. 新增阻断项 B4：summary JSON 不能被标准解析器读取

文件：

```text
v0.4_results/00_validation/shadow_validation/shadow_validation_summary.json
```

核验命令：

```powershell
$p = "v0.4_results\00_validation\shadow_validation\shadow_validation_summary.json"
Get-Content $p -Raw | ConvertFrom-Json
```

结果：

```text
INVALID_JSON
Unrecognized escape sequence.
```

直接原因：`camera_exr` / `sun_exr` 等 Windows 路径字段中出现未正确转义的反斜杠序列，且路径字符串存在中文编码异常片段。该文件虽然肉眼能看到 `pass_count`、`depth_epsilon_suggested`、`depth_error` 等字段，但不能被标准 JSON 工具稳定读取，因此不能作为后续自动化流程输入。

## 3. FIX02 必须同时修复三类问题

Claude 执行端在 `1C-E08-FIX02` 中必须完成：

1. 重新写出合法 JSON：

```text
v0.4_results/00_validation/shadow_validation/shadow_validation_summary.json
```

要求：

```text
必须能被 PowerShell ConvertFrom-Json 读取
必须能被 Python json.load 读取
不得包含未转义的 Windows 反斜杠
建议路径字段使用相对路径，或使用 pathlib/JSON 库自动序列化
不得手工拼接 JSON 字符串
```

2. 重新生成校准报告：

```text
v0.4_results/00_validation/shadow_validation/depth_epsilon_calibration_report.md
```

要求：

```text
DEPTH_EPSILON_M_FINAL = 0.7952109582768545 m
calibration_method = mean(abs_p99) across all attitudes
不得再把 0.7485 m 作为推荐最终阈值
不得再使用 sun depth 标准差 3-sigma 作为最终校准依据
```

3. 修复 Claude 执行报告路径：

标准目录必须是：

```text
04_四路线分工区/01_路线一_fixed-roll纯仿真主干/02_Claude输出/
```

不得再写入嵌套重复项目根目录：

```text
项目重启_v0.4_BlenderOCS/项目重启_v0.4_BlenderOCS/
```

## 4. 给 Claude 的追加返工提示词

```text
你是 Claude 执行端，只执行，不做 Codex 审阅或阶段裁决。

任务：执行 1C-E08-FIX02，在 R21 的基础上追加修复 JSON 合法性问题。

必须读取：
1. CLAUDE.md
2. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R21_Codex_审阅_1C-E08-FIX01部分通过但报告与路径不合格返工单.md
3. 04_四路线分工区/01_路线一_fixed-roll纯仿真主干/04_Codex审阅/R21A_Codex_补充审阅_1C-E08-FIX01_JSON合法性阻断.md

必须完成：
1. 用 JSON 标准库重新序列化 shadow_validation_summary.json，确保 ConvertFrom-Json 和 Python json.load 均可读取。
2. 不要手工拼接 JSON 字符串。
3. Windows 路径字段必须合法转义；优先使用相对路径。
4. 重新生成 depth_epsilon_calibration_report.md，使用 DEPTH_EPSILON_M_FINAL = 0.7952109582768545 m。
5. 把 Claude 执行报告写入标准 02_Claude输出 目录。

禁止：
1. 不得进入 Phase 0 Step 5。
2. 不得重渲染 40 个 EXR，除非发现 summary 与脚本输出不可恢复地不一致。
3. 不得写入 04_Codex审阅/。
4. 不得生成 Codex/R22/验收/最终放行名义的文件。
5. 不得修改 CLAUDE.md、冻结文件或成果区文件。

完成后输出：
- 修复后的 shadow_validation_summary.json
- 修复后的 depth_epsilon_calibration_report.md
- 标准路径下的 Claude FIX02 执行报告
```

## 5. 本轮分流

本轮不生成成果区稳定成果索引。`1C-E08-FIX01` 保持部分通过但不放行，等待 Claude 提交 FIX02 后由 Codex 再审。
