# Quick Start | 快速入门
[English version](#english-version) | [中文版本](#中文版本)

## English version

For a guided setup, choose [Install with AI](INSTALL_WITH_AI.md#english-version) or
[Download Windows installer](EASY_INSTALL.md#english-version). The commands below are the manual alternative.

Read your own Garmin data locally, with running/recovery guidance and citations.
This is an independent project using Garmin's official Personal API. It does not
need your Garmin password and is not endorsed by Garmin.

## Install

Install Python 3.12+ and Git. On Windows, open PowerShell and run one line at a time:

```powershell
git clone https://github.com/1838337544m-droid/Garmin-Assistant.git garmin-assistant-api
cd garmin-assistant-api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\garmin-assistant.exe init --timezone America/New_York --goal-km 10 --goal-minutes 60
```

Choose your own IANA timezone, not necessarily the example above. Default is UTC.
On macOS/Linux use `python3` and `.venv/bin/garmin-assistant`.

Create your own key in [Garmin Connect Personal API settings](https://connect.garmin.com/app/settings/personalApiToken).
Then run this command **on its own**:

```powershell
.\.venv\Scripts\garmin-assistant.exe auth
```

At `Garmin Personal API key (hidden):`, paste the complete key once and press Enter.
No characters or asterisks appear: this is expected. Do not paste the next command
while the program is asking for the key. Use Ctrl+C to cancel and retry if needed.

First use shows a bilingual welcome. Enter **2** for **English** (1 selects Chinese).
Your selection is saved. `"saved": true` means the key was stored, not verified.
Next run:

```powershell
.\.venv\Scripts\garmin-assistant.exe doctor --live
```

`"garmin_status": "ok"` confirms a successful Garmin read; `no_data` means no record
for the selected day. Errors do not count as successful connection.

## Connect an AI client

Generate your local stdio configuration with `client-config --client claude` or
`client-config --client codex`. Use the absolute executable path and nonsecret
environment paths it returns. The top-level `note` is explanatory, not client config.

- Claude Desktop/Code: local stdio MCP configuration is supported by the relevant desktop/coding client.
- GPT/Codex local-execution environments: add the command as a local MCP server.
- Ordinary ChatGPT web/mobile: this edition has no remote OAuth server; generate a report locally and upload it instead.
- Doubao: use local MCP only in a client edition that actually exposes that capability. Otherwise upload a generated report.

See [client-specific setup and limits](CLIENTS.md). Product/account editions differ;
the project does not claim all clients have been tested end to end.

When first interacting with the MCP, the AI should call `garmin_welcome`. If it asks
for language, reply **2 / English** before selecting a function. MCP cannot force
an unsolicited chat popup just because a server was connected.

## Core functions

1. Sync data and fill the interval since the last successful sync.
2. Review 30 days of training and 90 days of health data.
3. Assess fatigue and recovery with personal trends and self-reported fatigue and soreness.
4. Plan tomorrow's swim, ride or run using your target distance and time.

The primary menu has IDs 1–4. **Show original function menu** or **显示原有功能菜单** displays
the previous seven commands. Custom prompt workflows retain IDs from 100 upward.

Switch at any time with `garmin-assistant language en` or `garmin-assistant language zh`.
Raw Garmin fields, paper titles and user-authored custom text are not rewritten.

## Important limits

Advice is provisional until the morning recheck. Unknown symptoms are not assumed
absent. The rules are coaching heuristics, not medical clearance or injury-risk
probabilities. Newly retrieved papers require appraisal; they do not automatically
change training rules. Connected AI providers receive the tool results you use.

Your key, settings, history and reports are outside the source checkout. Updating
the code preserves them. See [maintenance and rollback](MAINTENANCE.md).

---

## 中文版本

希望引导安装，可选择[交给 AI 安装](INSTALL_WITH_AI.md#中文版本)或
[下载 Windows 安装包](EASY_INSTALL.md#中文版本)。下方命令为手动方式。

本项目使用自己的 Garmin Personal API 密钥在本机同步数据，不需要 Garmin 密码，
也不是 Garmin 官方产品。完整零基础步骤见 [用户手册](USER_GUIDE.md#中文版本)。

### 安装与密钥

安装 Python 3.12+ 与 Git。在 PowerShell 逐行执行：

```powershell
git clone https://github.com/1838337544m-droid/Garmin-Assistant.git garmin-assistant-api
cd garmin-assistant-api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\garmin-assistant.exe init --timezone Asia/Shanghai --goal-km 10 --goal-minutes 60
```

macOS/Linux 使用 `python3` 和 `.venv/bin/garmin-assistant`。
在自己的 [Garmin 个人 API 页面](https://connect.garmin.com/app/settings/personalApiToken)创建密钥，
然后单独执行：

```powershell
.\.venv\Scripts\garmin-assistant.exe auth
```

看到隐藏输入提示后，完整粘贴一次自己的密钥并按回车；不显示字符或星号是正常现象。
首次欢迎时输入 **1** 选择中文，**2** 选择 English。看到 `"saved": true` 只表示保存成功。
随后单独执行 `doctor --live`，`"garmin_status": "ok"` 才表示成功读取。

### 连接、菜单和限制

用 `client-config` 生成本机配置，按 [平台手册](CLIENTS.md#中文版本)连接。
支持本地 MCP 的客户端可以调用工具；普通网页/手机聊天用本地报告上传方式，不能自动同步本机。
首次交互会问语言，选好后使用菜单编号：

1. 同步数据。
2. 查看近 30 天训练和近 90 天身体状态。
3. 结合个人趋势和自评疲劳、酸痛评估恢复。
4. 选择游泳、自行车或跑步，再填写距离和时间，获取明日建议。

输入 **显示原有功能菜单** 可查看原七项功能。自定义编号仍从 100 起。
切换语言可用 `language zh` 或 `language en`。原始数据、论文标题和用户工作流不改写。
建议需明早复评，不作医疗放行、受伤概率或最快达标保证。新论文需评估，
不会自动改写规则。所连接的 AI 会接收使用中的工具结果。
用户数据在源码之外，更新会保留；见 [维护与回滚](MAINTENANCE.md#中文版本)。
