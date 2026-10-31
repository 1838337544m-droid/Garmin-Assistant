# 豆包、GPT、Claude 安装接入

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
退出并重新打开客户端，检查服务状态，再说“显示原有功能菜单”。

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
3. 客户端能调用 `garmin_function_menu`，看到核心 1–7。
4. 同步后能返回间隔起止与缺失信息。
5. 添加自定义功能、隐藏 1–7，再输入“显示原有功能菜单”，原菜单恢复且扩展仍在。

只有实际完成这些步骤的客户端才算端到端验证；文档配置示例不能代替验收。
