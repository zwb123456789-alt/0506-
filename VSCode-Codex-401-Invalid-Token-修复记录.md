# VS Code Codex 401 Invalid token 修复记录

日期：2026-06-01

## 问题现象

VS Code 里的 Codex 扩展反复重连，日志/界面显示：

```text
unexpected status 401 Unauthorized: Invalid token
url: https://www.relayai.tech/v1/responses
```

这个错误表示 VS Code Codex 发起请求时，后端 relay 不接受当前 token，或者 Codex 读取到的配置和预期配置不一致。

## 排查结论

本机存在两套配置入口：

1. Claude Code / ccswitch 使用：

```text
C:\Users\97466\.claude\settings.json
```

这里保存的是 `ANTHROPIC_*` 相关配置，例如：

```text
ANTHROPIC_AUTH_TOKEN
ANTHROPIC_BASE_URL
ANTHROPIC_MODEL
```

2. VS Code Codex 使用：

```text
C:\Users\97466\.codex\config.toml
C:\Users\97466\.codex\auth.json
```

VS Code Codex 读取的是 Codex 自己的 `.codex` 配置，不会自动跟随 `.claude\settings.json` 里的 ccswitch 结果。

因此，ccswitch 正常切换 Claude 配置，并不等于 VS Code Codex 也同步切换成功。

## 已做改动

### 1. 未修改 Claude 配置

没有写入或修改：

```text
C:\Users\97466\.claude\settings.json
C:\Users\97466\.claude\settings.local.json
```

检查时 `.claude\settings.json` 的时间戳仍是：

```text
2026-06-01 09:28:35
```

所以 Claude / ccswitch 原有配置没有被改动。

### 2. 未修改 ccswitch 原 provider 配置

没有修改 ccswitch 的应用目录或 provider 列表：

```text
C:\Users\97466\AppData\Roaming\com.ccswitch.desktop
C:\Users\97466\AppData\Local\com.ccswitch.desktop
```

只读取过这些目录用于确认 ccswitch 的配置来源，没有写入。

### 3. 修改了 VS Code Codex 配置

已备份原 Codex 配置：

```text
C:\Users\97466\.codex\config.toml.bak.1780279475225
```

已重写：

```text
C:\Users\97466\.codex\config.toml
```

当前关键配置为：

```toml
model_provider = "yunmian"
model = "gpt-5.5"

[model_providers.yunmian]
name = "yunmian"
base_url = "https://www.relayai.tech/v1"
wire_api = "responses"
requires_openai_auth = false
```

`api_key` 已写入配置文件，但不要在文档或聊天中明文传播。

### 4. 新增同步脚本

新增：

```text
C:\Users\97466\Documents\Codex\tools\Sync-CodexFromCcswitch.ps1
```

用途：重新生成 VS Code Codex 所需的 `.codex\config.toml` 和 `.codex\auth.json`。

默认同步到：

```text
provider: yunmian
model: gpt-5.5
base_url: https://www.relayai.tech/v1
wire_api: responses
```

### 5. 新增 PowerShell 快捷命令

在：

```text
C:\Users\97466\Documents\WindowsPowerShell\profile.ps1
```

新增：

```powershell
function sync-codex { & 'C:\Users\97466\Documents\Codex\tools\Sync-CodexFromCcswitch.ps1' @args }
```

以后可以在普通 PowerShell 中运行：

```powershell
sync-codex
```

## 后续如何使用

### 常规情况

如果只用 VS Code Codex 当前这套 `yunmian` 配置：

1. 打开 VS Code
2. 执行 `Developer: Reload Window`
3. 重新打开 Codex 侧边栏测试

### 使用 ccswitch 之后

如果你切换了 ccswitch，Claude Code 的配置会变，但 VS Code Codex 不一定自动变。

建议流程：

```powershell
sync-codex
```

然后在 VS Code 中执行：

```text
Developer: Reload Window
```

或者直接重启 VS Code。

## 注意事项

ccswitch 当前写入的是 Claude/Anthropic 风格配置，例如：

```text
ANTHROPIC_BASE_URL=https://ai.crantor.xyz
```

这类地址不能直接给 VS Code Codex 使用，除非该服务也支持 OpenAI Responses API：

```text
/v1/responses
```

VS Code Codex 当前需要 OpenAI-compatible Responses API 配置，因此使用：

```text
https://www.relayai.tech/v1
```

## 回滚方法

如果需要恢复原 Codex 配置，可以把备份复制回去：

```powershell
Copy-Item -LiteralPath 'C:\Users\97466\.codex\config.toml.bak.1780279475225' -Destination 'C:\Users\97466\.codex\config.toml' -Force
```

然后重启 VS Code 或执行：

```text
Developer: Reload Window
```

## 结论

1. 没有修改 Claude 相关配置。
2. 没有修改 ccswitch 里原来的 provider 配置。
3. 已修复 VS Code Codex 读取的 `.codex` 配置。
4. 之后再切换 ccswitch，如果 Codex 不正常，运行 `sync-codex` 再 reload VS Code。

