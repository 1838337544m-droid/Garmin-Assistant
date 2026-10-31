# Changelog | 更新记录
[English version](#english-version) | [中文版本](#中文版本)

## English version

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
