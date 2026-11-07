# Changelog | 更新记录
[English version](#english-version) | [中文版本](#中文版本)

## English version

### 0.1.8 — Windows redirected settings files

- Retry atomic settings and Claude configuration saves using resolved file paths when Windows Store Python reports a cross-volume rename for redirected files.

### 0.1.7 — Setup access diagnostics

- Setup identifies the affected data or client configuration file and distinguishes access denial from a file in use. On Windows, it reports the process integrity level when available and explains how to reopen setup under the normal user account.
- The bilingual AI installation instructions explain how to hand off setup when the AI cannot write to user files. [Issue #1](https://github.com/1838337544m-droid/Garmin-Assistant/issues/1)

### 0.1.6 — Setup diagnostics

- Saving the same client connection twice succeeds. Switching an existing connection to a different installation still asks for explicit replacement and creates a backup.
- **Save and check Garmin** verifies the credentials independently of AI client registration. Setup reports which step failed and keeps the key field available for correction if settings could not be saved.

### 0.1.5 — DeepSeek chat

- Added local chat with DeepSeek Flash and V4 Pro using the existing Garmin tools.
- Added the DeepSeek setup choice and Windows Start-menu shortcut. The chat uses a separate DeepSeek API key and asks before sending questions and tool results to DeepSeek.

### 0.1.4 — Guided local installation

- Added English/Chinese AI installation prompts and two README entry points.
- Added a Windows release ZIP: double-click launcher, Python/Tk detection, optional per-user WinGet install and versioned venv.
- Added a local setup wizard for language, masked API key, timezone and running goal.
- Added backup-preserving Claude configuration and Codex CLI registration; Doubao remains conditional config export.
- Added a separate live Garmin check, Start-menu setup shortcut and installer CI smoke checks.
- Core menu and training/data behavior are unchanged. The unsigned script installer is not an official store extension.

### 0.1.3 — 2026-10-31

- Reorganized public documentation into English-first and Chinese-second sections.
- Added **English version | 中文版本** navigation directly beneath the README title and document titles.
- Translated installation, client setup, updates, references, security, contribution and self-check guidance.
- Updated release presentation to bilingual titles; runtime behavior and core functions are unchanged.

### 0.1.2 — 2026-10-31

- Added a bilingual first-use welcome with explicit Chinese/English selection and persistent preference.
- Added welcome/language CLI commands and MCP tools; health reads wait until a language is selected.
- Localized core menus, AI reply instructions and next-day reports; raw Garmin fields/custom text remain unchanged.
- Preserved core IDs, reserved English core names and urgent-symptom priority; added an English quickstart.
- Documented that MCP prompts on first interaction rather than independently pushing chat messages.

### 0.1.1 — 2026-10-31

- Clarified beginner installation, hidden key entry, key storage versus connection checks, and failure handling.
- Separated authentication and diagnostics to prevent the next command being pasted as a key.
- Updated the homepage and macOS/Linux guidance.

### 0.1.0 — 2026-10-31

- First public release using the official Garmin Personal API/client.
- Added local history sync, next-day advice, weekly research discovery and classic-framework citations.
- Added configurable timezone/goals, stable hideable core IDs 1–7, and independent custom IDs >=100.
- Stored personal state separately from code; documented Windows/macOS/Linux installation and client/report-upload routes.

---

## 中文版本

### 0.1.8 — Windows 重定向设置文件

- Windows 商店版 Python 报告跨卷重命名时，改用文件实际所在路径重试原子保存，修复本机设置和 Claude 配置的保存问题。

### 0.1.7 — 设置权限诊断

- 设置窗口指出受影响的数据或客户端配置文件，区分权限不足与文件占用。Windows 可读取时显示进程完整性级别，并说明如何用平常登录的账户重新打开设置。
- 中英文 AI 安装说明补充了受限环境下由用户自行完成设置的步骤。[Issue #1](https://github.com/1838337544m-droid/Garmin-Assistant/issues/1)

### 0.1.6 — 安装自检

- 重复保存同一客户端连接可以正常完成。切换到另一个安装时，仍需明确勾选替换，并先备份原配置。
- **保存并检查 Garmin** 可独立验证凭据。设置窗口分别报告本机设置、实时读取和客户端注册结果，保存失败时保留密钥输入以便修正。

### 0.1.5 — DeepSeek 聊天

- 新增 DeepSeek Flash 和 V4 Pro 本地聊天入口，复用现有佳明工具。
- 设置窗口新增 DeepSeek 选项，Windows 新增开始菜单快捷方式。聊天使用独立的 DeepSeek API 密钥，发送问题和工具结果前会询问用户。

### 0.1.4 — 本地引导安装

- 新增中英双语 AI 安装指令和 README 两个安装入口。
- 新增 Windows 发布 ZIP：双击启动、检查 Python/Tk、可选为当前用户通过 WinGet 安装 Python，使用独立版本环境。
- 新增本地设置窗口：语言、隐藏密钥输入、时区和跑步目标。
- Claude 配置合并和 Codex CLI 接入前备份；豆包仍为取决于客户端支持情况的配置导出。
- 新增独立 Garmin 连接检查、开始菜单设置快捷方式和安装器 CI 冒烟检查。
- 核心菜单及训练／数据逻辑不变。安装包是未签名脚本，不是平台官方商店扩展。

## 0.1.3 — 2026-10-31

- GitHub 首页和公开文档统一为英文在上、中文在下。
- README 标题下第一行增加 English version | 中文版本 跳转，中文入口使用中文。
- 安装、平台接入、更新、参考、安全、贡献和自检说明补充英文内容。
- 发布标题改为双语；程序行为和核心功能保持不变。

## 0.1.2 — 2026-10-31

- 首次使用显示中英双语欢迎语，请用户选择 1. 中文 / 2. English，不自动代选。
- 保存语言偏好；新增 welcome/language 命令及 MCP 欢迎、切换语言工具。
- 选择语言前不读取健康数据；MCP 在首次交互中展示，不能独立向聊天窗口推送消息。
- 核心菜单、AI 回复语言指令和明日建议报告支持英文；原始 Garmin 字段与用户工作流不改写。
- 保留核心 1–7，阻止英文核心名称被扩展覆盖，英文建议保留紧急症状优先级。
- 补充英文快速入门和首次语言选择说明。

## 0.1.1 — 2026-10-31

- 补充零基础安装步骤：打开 PowerShell、逐行执行、密钥获取、隐藏输入、
  保存与连接验证的区别、失败处理，并拆开认证和检查命令避免误粘贴。
- 首页及 macOS/Linux 安装说明同步补充密钥输入提示。

## 0.1.0 — 2026-10-31

- 首个公开版，使用 Garmin 官方 Personal API 和官方 Python 客户端。
- 本地同步、区间历史、明日跑步预建议、每七天文献更新和经典模型引用。
- 可配置时区与跑步目标；默认 UTC，10 公里/60 分钟。
- 核心菜单 1–7 可隐藏；“显示原有功能菜单”恢复，不删除自定义功能。
- 自定义提示词工作流采用 100 起的稳定编号，不能覆盖核心工具。
- 配置与用户数据独立于源码；支持 Windows/macOS/Linux 的安装流程。
- 提供 GPT/Codex、Claude、豆包接入说明以及无本地 MCP 时的报告导入方式。
