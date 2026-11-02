# Easy Installation Implementation Plan | 简易安装实施计划
[English version](#english-version) | [中文版本](#中文版本)

## English version

**Goal:** Provide an AI-readable installation entry and a Windows double-click installer with a local graphical setup wizard.

**Architecture:** A release ZIP contains the versioned wheel and readable Windows launchers. The launcher finds Python 3.12/3.13 with Tk, offers a per-user Python installation via WinGet if needed, creates a versioned private virtual environment, installs the wheel, and opens the setup wizard. Existing user data remains outside the app directory. The wizard stores a masked API key locally, sets language/timezone/goal, connects a selected client, and offers a live check.

**Tech Stack:** Python/Tkinter, PowerShell 5.1+, JSON, official Codex CLI, GitHub Actions.

**Spec:** The user-approved two-entry flow in this conversation: Install with AI; Download installer. English above Chinese, local credential entry, preserve core menu.

## Global Constraints

- Never request keys in AI chat, command arguments, or client configuration.
- Preserve and back up client settings before writing; require confirmation to replace an existing Garmin entry.
- Do not claim ordinary web chats can install local tools. Doubao export is conditional on client local MCP support.
- No automatic initial 93-day data fetch; show the menu after setup and let the user choose synchronization.
- Existing core functionality and data contracts remain unchanged.

## Review Focus

- Invalid client JSON must not be overwritten.
- Repeated installation must preserve unrelated servers, existing keys and personal data.
- Paths with spaces, non-ASCII characters and missing CLIs must behave clearly.
- Missing Python, Tk, internet or WinGet must produce actionable bilingual errors.
- A failed live Garmin check must not be presented as a successful connection.

## Tasks

- [x] Write failing tests for configuration merging, backups, replacement refusal, invalid JSON, local key handling and Codex failure.
- [x] Implement focused setup backend and Tk wizard; add CLI `setup` entry.
- [x] Add Windows launchers and release ZIP builder; exercise a real isolated install with no private data/client changes.
- [x] Add English/Chinese AI instructions and beginner docs; verify official client documentation and link both entries from README.
- [x] Run tests, package/security checks, GUI smoke check and fresh-context review; fix material findings.
- [ ] Publish v0.1.4 after all OS CI passes; verify release artifacts and checksums.

Validation: 72 tests plus 7 subtests pass locally. Tk forms and real Codex CLI registration passed in temporary directories. The Windows launcher installed the wheel with dependencies in a path containing spaces/non-ASCII characters. Review found a POSIX Claude config permissions regression; its failing test was added and the secure replacement fixed. A real CLI smoke check also found that an explicitly selected new CODEX_HOME must be created; its failing test now passes. Publication status is recorded by GitHub Actions and the v0.1.4 release, rather than assumed here.

## 中文版本

目标：提供“交给 AI 安装”和“下载后双击安装”两个入口。Windows 安装包包含固定版本软件包及可阅读启动脚本，自动准备独立运行环境，再打开本地图形设置窗口。

窗口负责语言、时区、目标、隐藏密钥输入和客户端接入。修改配置前备份，不覆盖其他服务；已有佳明条目需要用户明确选择替换。豆包只导出配置，不承诺所有版本都支持本地 MCP。普通网页聊天使用本地报告上传。

实施顺序：先测试配置安全行为，再实现窗口和启动器，测试隔离安装，补充双语说明，运行多平台检查并审查，最后发布 v0.1.4。用户的私有数据和现有本机服务不参与安装测试。

本地结果：72 项测试及 7 项子测试通过；Tk 表单、真实 Codex CLI 临时目录注册、含空格和中文路径的独立安装通过。审查发现的 POSIX 配置权限问题和真实 CLI 检查发现的新 CODEX_HOME 目录问题均先补失败测试再修复。最终发布状态以 GitHub Actions 和 v0.1.4 发布页为准。
