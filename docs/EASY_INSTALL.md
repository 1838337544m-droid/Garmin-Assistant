# Easy Installation | 简易安装
[English version](#english-version) | [中文版本](#中文版本)

## English version

### Option 1 — Install with AI

Copy the [English installation prompt](INSTALL_WITH_AI.md#english-version) into an AI app that
can run commands on **your own computer**. It installs the local app and opens a local setup window.
Enter your key only in that window. Do not paste it into chat.

If the AI runs in a sandbox that restricts writes, ask it to finish the installation and hand off setup.
Open **Garmin Assistant Setup** from the Windows Start menu under your normal user account and save
the settings there. If the shortcut is missing, double-click the extracted **Install.cmd**.

If the AI cannot run commands on your computer, choose Option 2. Sending a link to an ordinary
web/mobile chat does not install software. Local Codex or another authorized local agent can follow
the instructions; it must follow its own permission prompts.

### Option 2 — Download, extract and double-click (Windows 10/11)

1. Open [Latest release](https://github.com/1838337544m-droid/Garmin-Assistant/releases/latest).
2. Under **Assets**, download **Garmin-Assistant-X.Y.Z-Windows-Installer.zip**.
   Do not choose the wheel, tar.gz or GitHub's automatically generated source ZIP.
3. Right-click the downloaded ZIP → **Extract All** → open the extracted folder.
4. Double-click **Install.cmd**. A terminal prepares an isolated environment; keep it open.
5. If Python 3.12/3.13 with Tcl/Tk is missing, a bilingual dialog offers a per-user installation
   of Python 3.12 through Microsoft's WinGet. Agree only if you want that installation;
   it accepts the Python package/source agreements. If WinGet is unavailable, install Python
   3.12/3.13 from [python.org](https://www.python.org/downloads/windows/) including Tcl/Tk, then retry.
6. When the **local setup window** opens, select **English** or **中文**.
7. Click **Open Garmin key page**, sign in on Garmin, and copy your **own** Personal API key.
   Paste it in the masked key field in the setup window. On later runs leave it blank to retain
   the stored key. This is an API key, not your Garmin account password.
8. Enter your IANA timezone, e.g. `America/New_York`, `Europe/London`, `Asia/Dubai`, or `Asia/Shanghai`.
   Default UTC is displayed, not a detected local timezone. Set your own running goal.
9. Select the client below and click **Save and connect**. Settings and the key are stored locally.
10. Click **Save and check Garmin** to verify the API key and live read independently of the AI client.
11. Restart the AI client. Say **Start Garmin Assistant**, then **Show function menu**.
    Choose **1** to sync data or **4** for tomorrow's training plan.

Internet access is needed to download dependencies and contact Garmin. Git is not required.
This is an **unsigned script-based installer**, not a signed EXE, official Garmin app, or official
platform store extension. Organization policies or Windows may block downloaded scripts.
Do not disable security controls; use your administrator's approved process or the [manual guide](USER_GUIDE.md).

### Choose your client

| Choice in setup | Result |
|---|---|
| Claude Desktop | Adds a local MCP entry, preserving other servers and backing up the original JSON file. |
| Codex CLI | Uses installed `codex mcp add`; backs up `CODEX_HOME/config.toml` or `~/.codex/config.toml` first. Missing CLI is reported as failure. |
| DeepSeek API | Saves Garmin settings for the local DeepSeek chat. Open **Garmin Assistant DeepSeek** from Start after setup. See [DeepSeek API](CLIENTS.md#deepseek-api). |
| Export only / 仅导出（豆包等） | Saves a nonsecret `client-config.json` in your personal data directory. Import it only if the client supports local stdio MCP. This does not automatically connect Doubao. |

For Claude, use the config file opened by the client's **Edit Config** command. The displayed path
is a common default; Microsoft Store editions can differ. Use **Browse** to select the correct file.
Switching an existing Garmin entry to a different installation requires the **Replace** checkbox. Repeated saves of the same entry succeed. The original config is kept beside the
file as a uniquely named `.bak`; this can contain other client settings, so keep it private.

An MCP entry is not proof that the client has loaded the tools. After restart, confirm the welcome
and IDs 1–4 are visible. Client extensions may be restricted by your plan or administrator.
[Claude's official local MCP guidance](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
and [OpenAI's official MCP guidance](https://learn.chatgpt.com/docs/extend/mcp) describe the client mechanisms.

### Later setup, updates and removal

- Open **Garmin Assistant Setup** from the Windows Start menu to change settings, reconnect a client,
  or retry the live check. The local window is independent of the AI chat window.
- For an update, download the new installer and follow the same steps. Select **Replace** to switch
  an existing Garmin connection to the new version. Unrelated client entries are kept.
- Runtime versions are stored under `%LOCALAPPDATA%\GarminAssistantAPI-App\X.Y.Z\venv`.
  Personal data uses the existing per-user location shown by `doctor`; it is outside the runtime.
  The installer does not erase old runtimes, keys, health data or custom menus.
- Close the AI client before removing an old runtime. To uninstall, first remove the Garmin MCP entry
  from your client, then delete its runtime folder and Start-menu shortcut. Delete personal data
  separately only if you want to erase it. Do not delete other client settings.
- macOS/Linux: use the AI prompt or [manual installation](USER_GUIDE.md); the Windows launcher does
  not run there. Tk is optional for CLI-only use but required for the setup window.

### If something fails

| What you see | Next step |
|---|---|
| Wheel or checksum missing | Extract all files into the same folder; download the release ZIP again if needed. |
| Python / Tk / WinGet unavailable | Install Python 3.12/3.13 including Tcl/Tk, then rerun Install.cmd. |
| pip download failure | Check internet/proxy restrictions and rerun the installer. Existing user data is preserved. |
| Save/connect failure | Check the timezone, goal, key, writable config path, existing-entry checkbox and client installation. No raw secret-bearing exception text is displayed. |
| Garmin not verified | Save first; check the API key and network. A cached/stale result is not live verification. |
| Saved but no AI tools | Restart the client, confirm the selected config file is correct and local MCP is supported. |

### Verification scope

Automated checks cover configuration preservation, backups, replacement refusal, invalid files,
key handling and process failures. Windows CI installs the release wheel in a separate runtime.
A local Tk smoke check exercises the language choice and settings form. These checks do not
claim that every client edition, administrator policy, clean-machine WinGet installation or
user-supplied Garmin account has been tested end to end.

---

## 中文版本

### 入口一：交给 AI 安装

如果 AI 的沙箱限制写入，让 AI 完成安装后把设置交给你。请用平常登录的 Windows 账户，
从开始菜单打开 **Garmin Assistant Setup** 并保存设置。如果找不到快捷方式，双击解压后的 **Install.cmd**。

将[中文安装指令](INSTALL_WITH_AI.md#中文版本)复制给**能操作你这台电脑**的 AI 应用。
AI 按说明安装本地程序并打开设置窗口，你只在这个窗口填写密钥，**不要发到聊天里**。

如果 AI 无法在你的电脑运行命令，请选入口二。普通网页／手机聊天不会因为收到链接就获得安装权限。
本地 Codex 等已获授权的 AI 工具可以执行安装，但仍需遵循其自身的权限提示。

### 入口二：下载、解压、双击安装（Windows 10/11）

1. 打开[最新版本下载页](https://github.com/1838337544m-droid/Garmin-Assistant/releases/latest)。
2. 找到 **Assets（附件）**，下载 **Garmin-Assistant-X.Y.Z-Windows-Installer.zip**。
   不要选择 wheel、tar.gz 或 GitHub 自动生成的源码 ZIP。
3. 右键下载的 ZIP → **全部解压缩** → 打开解压后的文件夹。
4. 双击 **Install.cmd**。终端窗口会准备独立运行环境，请先不要关闭。
5. 如果缺少包含 Tcl/Tk 的 Python 3.12/3.13，会出现中英双语询问窗口：是否通过微软 WinGet 为当前用户安装 Python 3.12。
   同意后会下载 Python 并接受软件包／来源协议。如果没有 WinGet，请从 [python.org](https://www.python.org/downloads/windows/)
   安装 Python 3.12/3.13，包含 Tcl/Tk，然后重新双击安装文件。
6. 出现**本地设置窗口**后，选择 **中文**或 **English**。
7. 点击“**打开 Garmin 密钥页面**”，在 Garmin 网站登录并复制你**自己的 Personal API key**。
   粘贴到设置窗口的密钥输入框，字符会被隐藏。以后修改设置时留空会保留已有密钥。
   此处填写 API 密钥，不是 Garmin 账号密码。
8. 填写 IANA 时区，例如中国 `Asia/Shanghai`、迪拜 `Asia/Dubai`、纽约 `America/New_York`。
   显示的默认 UTC 不是自动识别结果，请自行设置，并确认跑步目标。
9. 选择下面说明的客户端，点击“**保存并接入**”，配置和密钥会保存在本机。
10. 点击“**保存并检查 Garmin**”，独立于 AI 客户端验证密钥并实时读取数据。
11. 重启 AI 客户端，输入“**启动佳明助手**”，然后输入“**显示功能菜单**”。
    选择 **1** 同步数据，选择 **4** 获取明天运动建议。

需要联网下载依赖并访问 Garmin，不要求安装 Git。
这是**未签名的脚本安装包**，不是签名 EXE、Garmin 官方应用或平台商店官方扩展。
Windows 或组织策略可能阻止下载脚本；请遵循管理员认可的方式或使用[手动安装说明](USER_GUIDE.md#中文版本)，不要关闭安全防护。

### 客户端怎么选

| 设置窗口中的选择 | 实际操作 |
|---|---|
| Claude Desktop | 添加本地 MCP 条目，保留其他服务，修改前备份原 JSON 文件。 |
| Codex CLI | 调用已安装的 `codex mcp add`，先备份 `CODEX_HOME/config.toml` 或 `~/.codex/config.toml`；找不到 CLI 会明确失败。 |
| DeepSeek API | 保存佳明设置，随后从开始菜单打开 **Garmin Assistant DeepSeek**。详见 [DeepSeek 接入](CLIENTS.md#deepseek-api-接入)。 |
| Export only / 仅导出（豆包等） | 在个人数据目录导出不含密钥值的 `client-config.json`；仅供支持本地 stdio MCP 的客户端导入，不会自动连接豆包。 |

Claude 配置路径以客户端“**编辑配置 / Edit Config**”打开的文件为准。窗口显示的是常见默认路径，微软商店版可能不同，可点击“浏览”选择正确文件。
已有佳明条目指向另一个安装时，需勾选“**替换已有佳明连接条目**”。同一条目可重复保存。替换时原文件保存在旁边唯一命名的 `.bak` 备份中，可能包含其他客户端设置，请妥善保管。

配置写入后仍需重启客户端，确认欢迎信息和编号 1–4 的功能确实出现。套餐和管理员策略可能限制扩展。
客户端接入方式参考 [Claude 官方说明](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
与 [OpenAI 官方 MCP 说明](https://learn.chatgpt.com/docs/extend/mcp)。

### 以后怎么修改、更新和卸载

- 在 Windows 开始菜单打开 **Garmin Assistant Setup**，即可修改设置、重新接入客户端或检查连接。这个窗口独立于 AI 聊天窗口。
- 更新时下载新版安装包，再按以上步骤操作。已有佳明连接时勾选“替换”，将连接切换到新版；其他服务条目会保留。
- 运行环境位于 `%LOCALAPPDATA%\GarminAssistantAPI-App\X.Y.Z\venv`。
  个人数据仍使用 `doctor` 显示的原有目录，和运行环境分开保存；安装器不会删除旧版环境、密钥、健康数据或自定义菜单。
- 删除旧版环境前先退出 AI 客户端。卸载时先在客户端移除佳明 MCP 条目，再删除对应运行环境和开始菜单快捷方式。
  只有希望清除个人记录时才另行删除个人数据目录，不要删除客户端的其他配置。
- macOS/Linux 使用 AI 安装指令或[手动安装](USER_GUIDE.md#中文版本)，不能运行 Windows 启动器。纯命令行不要求 Tk，图形设置窗口需要 Tk。

### 出错时怎么办

| 看到的情况 | 处理方式 |
|---|---|
| 找不到 wheel 或校验失败 | 先把全部文件解压到同一文件夹，必要时重新下载发布 ZIP。 |
| 没有 Python / Tk / WinGet | 安装含 Tcl/Tk 的 Python 3.12/3.13，重新双击 Install.cmd。 |
| pip 下载失败 | 检查网络／代理限制后重试，已有个人数据会保留。 |
| 保存／接入失败 | 检查时区、目标、密钥、配置路径是否可写、是否勾选替换已有条目，以及客户端是否安装。界面不显示可能含私密内容的原始异常。 |
| Garmin 连接未验证 | 先保存，再检查密钥和网络；缓存或过期数据不代表实时验证成功。 |
| 保存后 AI 没有工具 | 重启客户端，确认配置路径正确，且该客户端支持本地 MCP。 |

### 自检范围

自动测试覆盖配置保留、备份、拒绝未经确认的替换、损坏配置、密钥处理和进程失败。
Windows CI 在独立环境实际安装发布包，本机 Tk 冒烟检查验证语言选择和设置表单。
这些检查不代表已端到端验证所有客户端版本、组织策略、全新电脑的 WinGet 安装或每位用户的 Garmin 账号。
