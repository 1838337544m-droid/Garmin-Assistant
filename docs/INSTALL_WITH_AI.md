# Install with AI | 交给 AI 安装
[English version](#english-version) | [中文版本](#中文版本)

## English version

Copy the following block into a trusted AI agent that can execute local commands on your computer.
It is an instruction, not a credential. Do not append your API key.

```text
Install Garmin Assistant (API edition) locally from:
https://github.com/1838337544m-droid/Garmin-Assistant

Read docs/EASY_INSTALL.md and the release notes first. Use the latest published non-prerelease
GitHub Release, not an arbitrary main-branch snapshot. Follow your own execution/approval rules.
If you cannot execute commands on MY computer, say so clearly and give me the Windows installer
download page. Do not pretend installation succeeded or use a cloud sandbox as my local machine.

On Windows, download the release Windows-Installer.zip and SHA256SUMS.txt from that same release,
verify the ZIP SHA256, extract all files, inspect Install.ps1 and Install.cmd, then run Install.ps1.
The script installs a versioned private environment and opens a local setup window. Missing Python
may offer WinGet installation with my consent. Do not change machine-wide execution policy.
Do not edit my existing local Garmin/private project or client configuration yourself.

On macOS/Linux, use a dedicated per-user application folder and Python 3.12/3.13. Download the
release wheel and SHA256SUMS.txt, verify its hash, create an isolated venv, and install the wheel
using that venv's Python. Do not use sudo or modify system Python. Launch the installed
`python -m garmin_assistant setup` in a visible LOCAL window. If Tk or a graphical session is
unavailable, explain the missing requirement and link the manual guide; never ask for my API key
in chat or send a key through terminal automation, arguments or transcripts.

Let ME choose English/中文, timezone, goal and AI client and enter my own key only in the masked
local setup window. Never request, read, echo, transmit or commit my key/health data. Do not read
existing private credential files. Do not start public tunnels. The setup wizard preserves and
backs up client config and requires confirmation before replacing an existing Garmin entry.
If launching the GUI would block your command tool, start it as an explicitly interactive app.
If your Windows execution environment restricts writes to my user data or client configuration,
finish installation and hand off setup. Ask me to open Garmin Assistant Setup from the Windows
Start menu under my normal user account, or double-click the extracted Install.cmd if the shortcut is missing.

After I finish setup, verify the installed version and ask me to use Save and check Garmin.
Do not call a saved configuration a verified connection. Tell me to restart the selected AI client,
say Start Garmin Assistant, then Show function menu. Verify IDs 1–4 and preserve custom
functions. Do not automatically download health history until I choose to sync.
Ordinary web/mobile chats and Doubao editions without local stdio MCP cannot connect through a
Python path; use config export only when supported, otherwise explain the local-report upload route.
Report the installed version, runtime path, client integration state and any unverified step.
```

The fixed-version download, checksum and local permission checks matter: a repository link alone
does not grant an AI control of your computer. For visual installation steps, see [Easy installation](EASY_INSTALL.md).

---

## 中文版本

把下面整段文字复制给可信任、**能在你的电脑执行命令**的 AI 工具。
这是一段安装说明，不是凭据；请不要在后面附上自己的 API 密钥。

```text
请在我这台电脑本地安装“Garmin 助手（API）版本”，项目地址：
https://github.com/1838337544m-droid/Garmin-Assistant

先阅读 docs/EASY_INSTALL.md 和发布说明。使用 GitHub 最新正式 Release，不要随意用 main
分支快照代替。遵循你自己的执行／审批规则。若你不能在“我的电脑”执行命令，请明确说明，
给我 Windows 安装包下载页面，不要假装安装成功，也不要把云端沙盒当成我的本机。

Windows：从同一个正式 Release 下载 Windows-Installer.zip 和 SHA256SUMS.txt，核对 ZIP
的 SHA256，完整解压，检查 Install.ps1 和 Install.cmd，再运行 Install.ps1。脚本会安装
固定版本的独立运行环境并打开本地设置窗口。缺少 Python 时可由我选择是否通过 WinGet
安装。不要修改整台电脑的执行策略；不要自行改动我已有的佳明私有项目或客户端配置。

macOS/Linux：使用独立的个人应用目录和 Python 3.12/3.13。下载同一 Release 的 wheel
和 SHA256SUMS.txt，核对校验值，创建独立 venv，通过该 venv 的 Python 安装 wheel。
不要用 sudo，不修改系统 Python。运行已安装环境中的 python -m garmin_assistant setup，
打开一个我能看到的本地图形窗口。若缺少 Tk 或图形桌面，请解释所缺条件并给手动安装说明；
不要通过聊天、终端自动输入、命令参数或操作记录向我索取／传递 API 密钥。

让我在本地窗口选择中文／English、时区、跑步目标和客户端，并只在隐藏输入框填写自己的
API 密钥。不要索取、读取、打印、上传或提交我的密钥和健康数据，不读取原有私密凭据文件，
不创建公网隧道。设置窗口会保留并备份客户端配置，替换已有佳明条目前需要我的明确选择。
如果图形窗口会阻塞你的命令工具，请按用户交互应用方式启动。
如果你的 Windows 执行环境限制写入我的用户数据或客户端配置，请完成安装后把设置交给我。
请让我用平常登录的 Windows 账户从开始菜单打开 Garmin Assistant Setup；若找不到快捷方式，双击解压后的 Install.cmd。

我完成设置后，检查安装版本，提醒我点击“保存并检查 Garmin”验证实时读取。
提醒我重启所选 AI 客户端，输入“启动佳明助手”，再输入“显示功能菜单”，确认 1–4
功能可见并保留自定义功能。在我选择同步之前，不要自动下载健康历史数据。
普通网页／手机聊天、以及不支持本地 stdio MCP 的豆包版本，不能通过本机 Python 路径接入；
仅在客户端确实支持时使用配置导出，否则说明本地生成报告后上传的用法。
最后告诉我安装版本、程序路径、客户端接入状态和仍未验证的步骤。
```

安装需要固定版本下载、校验和本机权限。仅提供仓库链接，不会自动授予 AI 电脑操作权限。
详细步骤见[简易安装](EASY_INSTALL.md#中文版本)。
