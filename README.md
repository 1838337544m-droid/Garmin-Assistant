# Garmin Assistant (API edition) | Garmin 助手（API）版本
[English version](#english-version) | [中文版本](#中文版本)

## English version

### Start here — no coding needed

**[Install with AI](docs/INSTALL_WITH_AI.md#english-version)** ·
**[Download Windows installer](https://github.com/1838337544m-droid/Garmin-Assistant/releases/latest)** ·
**[Step-by-step setup](docs/EASY_INSTALL.md#english-version)**

With a local AI agent, copy the installation prompt. Otherwise download the release's
**Windows-Installer.zip**, extract all files and double-click **Install.cmd**.
The local setup window lets you choose English/中文, enter your key privately and select a client.
Internet is required. Ordinary web chats cannot install local software by receiving a prompt.

Use your own Garmin Personal API key to sync activity and health data locally,
then ask an AI for running and recovery guidance with research citations and classic training frameworks.

**No Garmin password. No shared accounts. No maintainer health data included.**
This independent project is not affiliated with or endorsed by Garmin.

[Installation and user guide](docs/USER_GUIDE.md) · [Doubao / GPT / Claude setup](docs/CLIENTS.md) ·
[Updates and releases](docs/MAINTENANCE.md) · [References and verification](docs/REFERENCES.md) · [Changelog](CHANGELOG.md)

### First use

On first key setup or first interaction with the MCP, the assistant asks you to choose a language:

> Welcome to Garmin Assistant! / 欢迎首次使用佳明助手！
>
> Please choose your language / 请选择语言：
> **1. 中文　2. English**

The choice is saved. Before selection, 1/2 selects a language; afterwards numbers select functions.
Core menus, AI reply instructions and next-day reports support the selected language.
Switch any time with `garmin-assistant language en` or `garmin-assistant language zh`.
MCP cannot independently open a chat popup: the client presents the welcome at first interaction.

### Quick installation — Windows PowerShell

Install Python 3.12+ and Git. Open PowerShell and run **one line at a time**:

```powershell
git clone https://github.com/1838337544m-droid/Garmin-Assistant.git garmin-assistant-api
cd garmin-assistant-api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\garmin-assistant.exe init --timezone America/New_York
```

Set your own IANA timezone rather than copying the example blindly. Default is UTC.
The initial goal is 10 km in under 60 minutes; change it with `--goal-km` and `--goal-minutes`.
For complete Windows and macOS/Linux instructions, see the [beginner user guide](docs/USER_GUIDE.md).

Run authentication **separately**:

```powershell
.\.venv\Scripts\garmin-assistant.exe auth
```

At `Garmin Personal API key (hidden):`, paste your complete personal key once into
**PowerShell**, then press **Enter**. **No characters or asterisks appear; that is normal.**
Do not paste your key into an AI chat. First use then asks for 1 (Chinese) or 2 (English).
`"saved": true` means the key was stored, not yet verified. Only after that, run:

```powershell
.\.venv\Scripts\garmin-assistant.exe doctor --live
```

`"garmin_status": "ok"` confirms a successful Garmin read. Never paste the authentication
and diagnostic commands together while the program is asking for the key.

### Function menu

| ID | Core function |
|---|---|
| 1 | Sync data and fill the interval since the previous successful sync |
| 2 | Assess tomorrow's training |
| 3 | View activities and activity details |
| 4 | View sleep, heart rate and HRV |
| 5 | Read steps, stress and Body Battery over a date range |
| 6 | Refresh running and rehabilitation research |
| 7 | View sync status and the function menu |

Core IDs 1–7 are stable. Hide them without removing the tools; say **Show original function menu**
or **显示原有功能菜单** to restore them. Custom prompt workflows retain IDs starting at **100**.
They cannot override core tools and do not execute arbitrary third-party code.

### AI client compatibility

| Client | Connection offered by this edition |
|---|---|
| Claude Desktop / Claude Code | Local stdio MCP configuration |
| GPT / Codex environments with local execution | Register the generated absolute command as a local MCP |
| Ordinary ChatGPT web/mobile | Generate a report locally and upload it; no remote OAuth connector is provided |
| Doubao editions that expose local MCP | Configure stdio through that edition's supported entry point |
| Ordinary Doubao chat / clients without local MCP | Upload a locally generated report; no automatic local sync |

Use `client-config` to generate paths for your actual installation. See the [client guide](docs/CLIENTS.md).
This release is not a hosted service, browser extension or prelisted official client application.

### Data and evidence

- Initial sync requests 93 days; later syncs fill gaps and revisit overlapping dates. Missing records and failures are explicit.
- Next-day assessment syncs first. Research is refreshed after 7 days since the last successful search, or on demand.
- HRV, sleep, resting heart rate and recent running are interpreted against personal references. Unknown symptoms remain unknown.
- Reports cite classic fitness–fatigue, intensity-distribution and Daniels frameworks alongside applicable recent research.
- Newly retrieved papers require appraisal; they do not automatically rewrite training rules.
- Advice is provisional until the morning recheck, not medical clearance, an injury-risk probability or a fastest-progress guarantee.

Keys, settings, history, reports and custom menus are outside the source checkout, so code updates preserve them.
Tool results go to your connected AI provider; choose a client that fits your privacy preferences.

### Updates, extensions and self-check

Releases are published periodically. Users choose when to update; the project does not silently download and execute new code.
See [maintenance and rollback](docs/MAINTENANCE.md). MIT allows modification and forks;
the immutable core is an official-release/extension compatibility contract, not a prohibition on editing open-source code.

```sh
python -m pip install -e ".[dev]"
python -m pytest -q
python scripts/check_release.py
python -m build
```

CI runs synthetic tests on Windows, macOS and Linux without personal Garmin credentials.
See [verification scope](docs/REFERENCES.md) and [self-check records](docs/SELF_CHECK.md).

---

## 中文版本

### 从这里开始：不需要懂代码

**[交给 AI 安装](docs/INSTALL_WITH_AI.md#中文版本)** ·
**[下载 Windows 安装包](https://github.com/1838337544m-droid/Garmin-Assistant/releases/latest)** ·
**[一步步安装说明](docs/EASY_INSTALL.md#中文版本)**

如果 AI 能操作你的电脑，复制安装指令即可；否则在发布页下载 **Windows-Installer.zip**，
完整解压后双击 **Install.cmd**。本地窗口会让你选择中文／English、私密输入密钥并选择客户端。
安装需要联网；普通网页聊天不能只凭收到一段指令就在电脑上安装软件。

用自己的 Garmin Personal API 密钥，在本机同步运动与健康数据，让 AI 结合
长跑训练、恢复研究和经典模型提供有出处的建议。

**不需要 Garmin 密码；不托管他人账号；不附带维护者的个人数据。**
本项目独立开发，不隶属 Garmin。

[安装与用户手册](docs/USER_GUIDE.md) · [豆包/GPT/Claude 接入](docs/CLIENTS.md) ·
[更新与发布](docs/MAINTENANCE.md) · [参考与验证范围](docs/REFERENCES.md) · [更新记录](CHANGELOG.md)

[英文快速入门](docs/ENGLISH_QUICKSTART.md)

## 首次使用 / First use

首次保存密钥或在 AI 中首次调用本助手时，会看到：

```text
欢迎首次使用佳明助手！
Welcome to Garmin Assistant!

请选择语言 / Please choose your language:
1. 中文
2. English
```

选择后会保存语言偏好，后续使用相应语言的核心菜单、AI 回复和明日建议报告。
语言选择完成前，“1/2”表示语言；完成后才按功能菜单编号操作。
随时说“切换为英文 / Switch to English”，或执行 `garmin-assistant language en`。
切回中文用 `garmin-assistant language zh`。核心编号和用户扩展不会改变。
MCP 无法自行向聊天窗口推送消息；客户端按连接指令在首次交互中展示欢迎语。

## 快速安装

需要 Python 3.12+ 和 Git。在 PowerShell 中：

```powershell
git clone https://github.com/1838337544m-droid/Garmin-Assistant.git garmin-assistant-api
cd garmin-assistant-api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\garmin-assistant.exe init --timezone Asia/Shanghai
```

接下来**单独运行**：

```powershell
.\.venv\Scripts\garmin-assistant.exe auth
```

看到 `Garmin Personal API key (hidden):` 后，在 **PowerShell 窗口**
按 **Ctrl+V** 粘贴你自己的整串个人密钥，再按 **回车**。
**输入不会显示字符或星号，这是正常现象；只粘贴一次。**
首次运行会接着显示双语欢迎语；输入 `1` 选中文或 `2` 选 English，再按回车。
看到 `"saved": true` 只是保存成功，再单独运行连接检查：

```powershell
.\.venv\Scripts\garmin-assistant.exe doctor --live
```

检查结果中 `"garmin_status": "ok"` 表示已成功读取 Garmin。不要把密钥
粘贴到 AI 聊天中，也不要把 `auth` 和检查命令一起粘贴。
不熟悉命令行请按[零基础分步说明](docs/USER_GUIDE.md#第四步输入个人密钥最容易误解的一步)操作。

默认目标为 10 公里/60 分钟，可在
`init` 中用 `--goal-km`、`--goal-minutes` 修改。请配置自己的时区（默认 UTC）。
macOS/Linux 对应命令与说明见[用户手册](docs/USER_GUIDE.md)。

## 功能菜单

| 编号 | 核心功能 |
|---|---|
| 1 | 同步数据、补齐询问间隔 |
| 2 | 分析明天是否适合运动 |
| 3 | 查看运动记录与详情 |
| 4 | 查看睡眠、心率和 HRV |
| 5 | 区间步数、压力和 Body Battery |
| 6 | 更新长跑训练和康复文献 |
| 7 | 同步状态与功能菜单 |

核心编号固定，可以隐藏，不能被自定义工作流覆盖。随时输入
**显示原有功能菜单** 恢复 1–7；自定义功能仍保留。
自定义工作流从 **100** 起编号，不自动执行第三方代码。

## 平台接入

| 平台 | 本版接入方式 |
|---|---|
| Claude Desktop / Claude Code | 本地 stdio MCP 配置；桌面版也可按客户端支持的扩展机制自行封装 |
| GPT / Codex，支持本地 MCP 的桌面环境 | 用生成的绝对命令添加本地 MCP |
| 普通 ChatGPT 网页/手机聊天 | 本地生成报告后上传；本版不提供远程 OAuth 连接器 |
| 豆包工作等具有本地 MCP 入口的版本 | 按该版本入口配置 stdio；不能推断所有豆包版本都支持 |
| 普通豆包聊天 / 无本地 MCP 的客户端 | 生成报告后上传分析，不能自动同步本机 |

通过 `client-config` 生成实际安装路径配置，见[平台手册](docs/CLIENTS.md)。
本版没有提供云端服务、浏览器插件或一键上架的官方应用。

## 数据和依据

- 初次同步默认 93 天，后续填补间隔并复查重叠日期；缺失及失败明确标识。
- 每次明日分析先同步；文献成功检索满 7 天再联网更新，也可手动立即更新。
- 结合个人 HRV、睡眠、静息心率及近期跑步负荷；不知道的症状不当作没有。
- 引用经典适能—疲劳、强度分配、Daniels 分类及近期适用研究。
- 新论文标为待评估；不会因出现新文章就自动改写训练规则。
- 明日结果是预建议，晨起应复评；不作医疗放行、伤病概率或最快达标保证。

配置、密钥、缓存、报告与自定义菜单均位于个人数据目录，更新源码不会
覆盖。工具结果会发送给所连接的 AI，请按自己的隐私偏好选择平台。

## 更新与扩展

维护者不定期发布版本；用户主动更新，不静默下载执行新代码。
固定编号、独立配置和数据目录用于保留用户偏好。
升级、回滚与发版步骤见[维护手册](docs/MAINTENANCE.md)。
MIT 开源许可允许修改和 fork；“核心不变”是官方发行版及扩展接口的
兼容约定，不是禁止别人修改源码。详见 [贡献说明](CONTRIBUTING.md)。

## 自检

```sh
python -m pip install -e ".[dev]"
python -m pytest -q
python scripts/check_release.py
python -m build
```

仓库 CI 在 Windows/macOS/Linux 运行合成测试，不使用真实 Garmin 密钥。
实际完成的测试范围和客户端限制见[参考与自检](docs/REFERENCES.md)。
