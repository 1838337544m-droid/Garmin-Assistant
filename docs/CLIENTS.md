# Doubao / GPT / Claude Setup | 豆包／GPT／Claude 接入
[English version](#english-version) | [中文版本](#中文版本)

## English version

### DeepSeek API

1. Install Garmin Assistant v0.1.5 or later. In **Garmin Assistant Setup**, choose **DeepSeek API**, save your Garmin settings and check the Garmin connection.
2. Open **Garmin Assistant DeepSeek** from the Windows Start menu. On macOS/Linux or a manual installation, run `garmin-assistant deepseek` from the installed environment.
3. Choose **Flash** (`deepseek-flash`) or **V4 Pro** (`deepseek-v4-pro`). Type `yes` after reading the data-sharing notice, then enter your DeepSeek API key at the hidden terminal prompt. The key can also be supplied with `DEEPSEEK_API_KEY`.
4. Select a numbered function or ask a question. Try **4** for tomorrow’s training plan. Type `/quit` to exit.

This terminal client uses the DeepSeek API's non-thinking tool-calling mode. It sends recent chat history, relevant Garmin health and activity results (which may include location), and custom workflows you select by number. DeepSeek bills API usage to your account. Garmin and DeepSeek require separate credentials. Keep the Garmin key in local setup and enter the DeepSeek key only at the credential prompt. Your model key is held for the session. [DeepSeek API platform](https://platform.deepseek.com/) · [Official model and tool support](https://api-docs.deepseek.com/quick_start/pricing/)

To preselect a model, use `garmin-assistant deepseek --model deepseek-v4-pro` or pass `deepseek-flash`. The existing MCP connection can also be used by a compatible local host configured separately for DeepSeek. [DeepSeek’s Codex configuration guide](https://api-docs.deepseek.com/quick_start/agent_integrations/codex/)

For guided connection, use the [local setup wizard](EASY_INSTALL.md#english-version).
It can merge Claude configuration or invoke the installed Codex CLI after a backup.
The manual examples below remain available. This project still does not ship an `.mcpb` extension.

Checked on 2026-10-31. Complete the [general installation](USER_GUIDE.md) first.
MCP is a tool protocol: pasting a Markdown guide into chat does not give the AI access to your computer.

### 1. Generate configuration for this computer

Windows:

```powershell
.\.venv\Scripts\garmin-assistant.exe client-config --client claude
.\.venv\Scripts\garmin-assistant.exe client-config --client codex
.\.venv\Scripts\garmin-assistant.exe client-config --client doubao
```

On macOS/Linux use `.venv/bin/garmin-assistant`. No key values are embedded. Copy only the
`mcpServers` configuration; the top-level `note` is explanatory, not a client setting.
Keep the generated nonsecret data-directory/key-file paths with the configuration.

### 2. Claude

#### Claude Desktop

Use the client's local MCP/developer configuration entry point and merge the generated `mcpServers`
entry without overwriting other servers. Windows commonly uses
`%APPDATA%/Claude/claude_desktop_config.json`; macOS commonly uses
`~/Library/Application Support/Claude/claude_desktop_config.json`. The file opened by the client's
**Edit Config** command is authoritative; Store editions may use different paths.

Restart the client and say **Start Garmin Assistant**. Choose 1 (Chinese) or 2 (English) at first use,
then say **Show original function menu**. Configuration shape:

```json
{
  "mcpServers": {
    "garmin-assistant": {
      "command": "ABSOLUTE_PATH_TO_VENV_PYTHON",
      "args": ["-m", "garmin_assistant", "serve"]
    }
  }
}
```

Use actual paths and environment entries generated on your machine. This project does not ship
an `.mcpb` desktop extension and is not claimed to be listed in the official directory.
[Official local MCP guide](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop).

#### Claude Code

```sh
claude mcp add garmin-assistant -- ABSOLUTE_PATH_TO_VENV_PYTHON -m garmin_assistant serve
```

Quote paths containing spaces. Check your installed client's help for supported options.

### 3. GPT / Codex

In a Codex/desktop environment that supports local MCP, use the argv returned by
`client-config --client codex`, including its nonsecret `--env` path settings.
The general command structure is:

```sh
codex mcp add garmin-assistant -- ABSOLUTE_PATH_TO_VENV_PYTHON -m garmin_assistant serve
codex mcp get garmin-assistant
```

You can also add the command in MCP server settings and restart.
[Official MCP configuration](https://learn.chatgpt.com/docs/extend/mcp).

**Ordinary ChatGPT web chat does not gain access to local configuration files this way.**
Remote custom connectors are a separate network path; this edition has no remote authentication server.
Instead:

1. Run `garmin-assistant tomorrow` locally and wait for synchronization and report generation.
2. Upload the Markdown report from the path returned in the terminal.
3. Explain your goal, current symptoms/fatigue and the question. Generate a new local report for new data.

A report upload is not an automatic-sync installation.
See [OpenAI custom MCP documentation](https://developers.openai.com/api/docs/guides/custom-mcp-server) for the separate remote mechanism.

### 4. Doubao

First distinguish a Doubao Work/client edition with local tool execution from ordinary web/mobile chat.
The [Doubao developer platform](https://open.doubao.com/) describes Skill/Plugin/MCP concepts;
this does not prove every account or edition has a generic local stdio entry point.

If the client actually provides **Local MCP / Add server**, use the command and arguments returned by
`client-config --client doubao`. If it only accepts a remote URL, a local Python path is not suitable;
use the report-upload route instead.

#### Optional third-party CLI route

[Fullstop000/doubao-cli](https://github.com/Fullstop000/doubao-cli) documents local MCP registration.
Its desktop route requires a supported macOS client; its Headless route supports Linux/macOS.
This project has not verified that bridge in Windows Doubao and does not treat it as an official installer
or install it automatically.

Only if you have independently installed/trust that CLI, signed in and meet its platform requirements:

```sh
doubao mcp register garmin-assistant --command ABSOLUTE_PATH_TO_VENV_PYTHON --arg -m --arg garmin_assistant --arg serve
doubao mcp list --json
```

Follow that project's current README for connector IDs, per-message binding and permission settings.
Do not expose your key or start an unauthenticated public tunnel to make this work.

#### Ordinary Doubao chat

Generate a local `tomorrow` report and upload it. MCP is not required, but each update is a new manual
snapshot. Core actions still execute through the local CLI or a connected MCP.

### 5. Acceptance checklist

1. `doctor` shows the version, your timezone and whether a key is configured.
2. After language selection, `doctor --live` returns a successful Garmin read or explicit no-data status.
3. First call `garmin_welcome` and choose a language; `garmin_function_menu` then shows IDs 1–4.
4. Sync returns the gap dates and missing-record information.
5. Add a custom function, hide 1–4, then request the original menu: it returns without deleting the extension.

Only clients where these steps were actually completed count as end-to-end verified. A configuration
example alone is not proof of client compatibility.

---

## 中文版本

### DeepSeek API 接入

1. 安装佳明助手 v0.1.5 或更新版本。在 **Garmin Assistant Setup** 中选择 **DeepSeek API**，保存 Garmin 设置并检查连接。
2. 从 Windows 开始菜单打开 **Garmin Assistant DeepSeek**。macOS、Linux 或手动安装的用户可在已安装环境中运行 `garmin-assistant deepseek`。
3. 选择 **Flash**（`deepseek-flash`）或 **V4 Pro**（`deepseek-v4-pro`）。阅读数据发送说明，输入 `yes` 后，在终端隐藏输入框填写 DeepSeek API 密钥。也可通过环境变量 `DEEPSEEK_API_KEY` 提供密钥。
4. 输入编号或自然语言提问。例如输入 **4** 选择明天的运动项目。输入 `/quit` 退出。

此终端客户端使用 DeepSeek API 的非思考模式调用工具。发送内容包括最近的问答、用到的 Garmin 健康和活动结果（可能含位置），以及你按编号选中的自定义流程。模型用量由 DeepSeek 账户计费。Garmin 与 DeepSeek 使用不同的密钥，请分别填写在本机设置和终端密钥提示中。模型密钥仅供当前会话使用。[DeepSeek API 平台](https://platform.deepseek.com/) · [官方模型及工具支持](https://api-docs.deepseek.com/quick_start/pricing/)

可用 `garmin-assistant deepseek --model deepseek-v4-pro` 直接选定模型，也可将模型名换成 `deepseek-flash`。如果已在兼容的本地客户端中配置 DeepSeek，也可以继续使用原有 Garmin MCP 接入。[DeepSeek 官方 Codex 接入说明](https://api-docs.deepseek.com/quick_start/agent_integrations/codex/)

想减少手动配置，可使用[本地设置窗口](EASY_INSTALL.md#中文版本)，
在备份后自动合并 Claude 配置或调用已安装的 Codex CLI。下面保留手动方式，尚未提供 `.mcpb` 扩展。

核对日期：2026-10-31。先完成[通用安装](USER_GUIDE.md)，再选你的客户端。
MCP 是工具协议，不是把 Markdown 指南粘贴到聊天后就获得本机权限。

## 1. 生成本机配置

Windows：

```powershell
.\.venv\Scripts\garmin-assistant.exe client-config --client claude
.\.venv\Scripts\garmin-assistant.exe client-config --client codex
.\.venv\Scripts\garmin-assistant.exe client-config --client doubao
```

macOS/Linux 用 `.venv/bin/garmin-assistant`。输出不含个人密钥。
JSON 配置只复制 `mcpServers` 内容，`note` 是说明，不是客户端配置字段。

## 2. Claude

### Claude Desktop

按客户端的本地 MCP/开发者配置入口，合并生成的 `mcpServers` 条目，
不要覆盖其它服务。Windows 通常为 `%APPDATA%/Claude/claude_desktop_config.json`，
macOS 通常为 `~/Library/Application Support/Claude/claude_desktop_config.json`；
以客户端“编辑配置”打开的实际文件为准，商店版目录可能不同。
退出并重新打开客户端，检查服务状态，再说“开始使用佳明助手”。
首次会显示中英双语欢迎语，请先回复 `1`（中文）或 `2`（English），
选好语言后再说“显示原有功能菜单 / Show original function menu”。

示例结构（把 Python 路径换成 `client-config` 输出）：

```json
{
  "mcpServers": {
    "garmin-assistant": {
      "command": "ABSOLUTE_PATH_TO_VENV_PYTHON",
      "args": ["-m", "garmin_assistant", "serve"]
    }
  }
}
```

本项目未发布 `.mcpb` 桌面扩展，也没有宣称已进入官方扩展目录。
官方说明：[Claude 本地 MCP](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)。

### Claude Code

```sh
claude mcp add garmin-assistant -- ABSOLUTE_PATH_TO_VENV_PYTHON -m garmin_assistant serve
```

将绝对路径用引号括起以处理空格。这里是配置示例，实际 Claude Code
可用参数以所装版本帮助为准。

## 3. GPT / Codex

支持本地 MCP 的 Codex/桌面环境可使用 `client-config --client codex`
输出的 argv：

```sh
codex mcp add garmin-assistant -- ABSOLUTE_PATH_TO_VENV_PYTHON -m garmin_assistant serve
codex mcp get garmin-assistant
```

也可在设置中的 MCP servers 添加命令，重启后使用。
官方说明：[本地 MCP 配置](https://learn.chatgpt.com/docs/extend/mcp)。

**普通 ChatGPT 网页聊天不能据此读取本地配置文件。** 远程自定义连接器
是另一条网络接入路径，本版没有远程认证服务器。请改用以下报告方式：

1. 本机执行 `garmin-assistant tomorrow`，等待同步和报告生成。
2. 找到终端返回的 Markdown 报告路径，上传到你的聊天。
3. 说明目标、伤痛/疲劳和需要分析的内容。新的日期要重新在本机生成报告。

报告上传不等于安装了自动同步。远程 MCP 机制参见
[OpenAI 自定义 MCP](https://developers.openai.com/api/docs/guides/custom-mcp-server)。

## 4. 豆包

首先确认是具有本地工具执行能力的“豆包工作”等客户端，还是普通网页/手机聊天。
[豆包开放平台](https://open.doubao.com/)列出 Skill/Plugin/MCP 等接入概念，
但不能由此认定任意账号或版本都有通用本地 stdio 入口。

若当前客户端确实提供“本地 MCP / 添加服务器”，使用
`client-config --client doubao` 的命令与参数；确认状态后再调用菜单。
若只有远程 URL 输入框，不应填本机 Python 路径，改用报告上传方式。

### 可选第三方 CLI 路线（需自行确认环境）

[Fullstop000/doubao-cli](https://github.com/Fullstop000/doubao-cli) 的 README
公开本地 MCP 注册机制，桌面路径要求其支持的 macOS 环境/客户端，
Headless 路径为 Linux/macOS。本项目未在 Windows 豆包里验证该桥接，
也不把第三方 CLI 当成官方安装器或自动安装它。

在你已安装并信任该 CLI、账号已登录且平台条件符合后，可按其说明：

```sh
doubao mcp register garmin-assistant --command ABSOLUTE_PATH_TO_VENV_PYTHON --arg -m --arg garmin_assistant --arg serve
doubao mcp list --json
```

后续消息绑定 connector-id 及权限设置按该项目当前 README 操作。
不要为了接入而公开自己的密钥或启动无认证公网隧道。

### 普通豆包聊天

运行本地 `tomorrow`，上传报告并请豆包分析。这条路径不需要 MCP，
但每次要手动生成新快照。核心菜单的执行仍需本地 CLI 或已连接的 MCP。

## 5. 接入验收

1. `doctor` 能显示版本、自己的时区和 `key_configured`。
2. `doctor --live` 返回 `garmin_status: ok` 或明确的无数据状态。
3. 首次先调用 `garmin_welcome` 选择语言，然后调用 `garmin_function_menu` 看到主菜单 1–4。
4. 同步后能返回间隔起止与缺失信息。
5. 添加自定义功能、隐藏 1–4，再输入“显示原有功能菜单”，原菜单恢复且扩展仍在。

只有实际完成这些步骤的客户端才算端到端验证；文档配置示例不能代替验收。
