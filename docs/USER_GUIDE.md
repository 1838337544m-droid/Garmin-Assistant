# 用户手册

## 1. 首次准备

安装 Python 3.12 或更新版本与 Git。下面的“命令”是复制到电脑终端执行的文字，
不是发给豆包、GPT 或 Claude 的聊天内容。终端就是 Windows PowerShell，
或 macOS/Linux 的“终端”应用。

每位用户需要自己的 Garmin **个人 API 密钥**。它是一长串字符，
不是 Garmin 登录密码，也不是邮箱验证码。获取方法：

1. 在浏览器登录你自己的 Garmin Connect 账号。
2. 打开 [Personal API 页面](https://connect.garmin.com/app/settings/personalApiToken)。
3. 选择 **Create Key（创建密钥）**，阅读条款、选择有效期并确认创建。
4. 复制网页刚显示的整串密钥。密钥只显示一次，请保存在自己的安全位置。
5. 暂时不要把密钥粘贴到聊天中，后面会有专门的隐藏输入步骤。

不要使用维护者或其他人的密钥，也不需要把自己的密钥发给维护者。

默认时区 UTC。请通过 `init` 设置自己的 IANA 时区，例如中国
`Asia/Shanghai`、迪拜 `Asia/Dubai`。目标可自行修改；不会更改核心菜单。

## 2. 安装（Windows PowerShell）

### 第一步：打开输入命令的窗口

按键盘 **Windows 键**，输入 `PowerShell`，打开 **Windows PowerShell**。
看到类似 `PS ... >` 的提示符后，就可以输入命令。
普通用户权限即可，不必以管理员身份运行。

以下每行命令都要**单独复制、粘贴、按回车**。等这一行运行结束，
再次出现 `PS ... >` 后，再执行下一行。代码框旁的复制按钮可能复制整个框，
新手可以用鼠标只选中一行复制。不要复制代码框的边框、行号或 `PS ... >`。

### 第二步：下载项目并安装

依次执行下面四行。`cd` 表示进入刚下载的项目文件夹；安装时输出很多文字是正常现象。

```powershell
git clone https://github.com/1838337544m-droid/garmin-assistant-api.git
cd garmin-assistant-api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

如果提示 `python` 找不到，先确认 Python 已安装；也可用已安装的
`py -3.12 -m venv .venv` 代替上面的第三行。提示 `git` 找不到则需先安装 Git。
若提示项目文件夹已存在，不要重复下载，进入你已有的项目文件夹后继续。

### 第三步：设置你的时区和目标

中国用户复制这一行后按回车：

```powershell
.\.venv\Scripts\garmin-assistant.exe init --timezone Asia/Shanghai --goal-km 10 --goal-minutes 60
```

迪拜用户把 `Asia/Shanghai` 改为 `Asia/Dubai`。这里的 `10` 和 `60` 表示
目标 10 公里、60 分钟，可按自己的目标修改。看到输出中有 `timezone` 和
`goal` 就表示设置已写入；它还没有开始读取 Garmin 数据。

### 第四步：输入个人密钥（最容易误解的一步）

**先只运行下面这一行，不要连同下一步的检查命令一起粘贴：**

```powershell
.\.venv\Scripts\garmin-assistant.exe auth
```

按回车后，PowerShell 会显示：

```text
Garmin Personal API key (hidden):
```

这句话的意思是：**现在程序正等待你输入 Garmin 个人 API 密钥。**

1. 回到 Garmin 网页或你自己的安全保存位置，复制整串个人密钥。
2. 切回这个 PowerShell 窗口，在提示后的光标处按 **Ctrl+V** 粘贴。
   如果该终端不支持 Ctrl+V，可尝试右键粘贴。
3. **屏幕不会显示密钥，也不会出现圆点或星号，这是正常的隐藏输入，
   不是程序卡住，也不是没有粘贴成功。** 不要因为没显示字符就反复粘贴。
4. 粘贴一次后，按 **回车** 提交。不加引号，不输入 `API.txt` 文件名，
   也不把密钥接在 `auth` 命令后面。
5. 首次保存后会出现中英双语欢迎语和 `1. 中文 / 2. English`。
   在终端输入 `1` 或 `2`，再按回车；以后会记住这个选择。
6. 输出中看到 `"saved": true`，表示密钥已保存在你电脑上。
   **这只表示保存成功，还需要下一步验证密钥能否连接 Garmin。**

如果粘贴错了或不确定是否重复粘贴，按 **Ctrl+C** 取消，再运行一次
`auth`，重新复制整串密钥、粘贴一次并按回车。

### 第五步：验证是否连接成功

等保存完成、再次出现 `PS ... >` 后，才执行这一行：

```powershell
.\.venv\Scripts\garmin-assistant.exe doctor --live
```

检查输出：

| 看到的内容 | 意思和下一步 |
|---|---|
| `"key_configured": true` | 找到了密钥；单看这一项还不能确认联网成功 |
| `"key_configured": false` | 没有找到密钥；在同一个系统用户和项目环境中重新运行 `auth` |
| `"garmin_status": "ok"` 且 `"status": "ok"` | 已成功读取 Garmin，可以按平台手册连接 AI |
| `"garmin_status": "no_data"` | 请求成功，但该日期没有可用记录；先同步手表，或稍后查其它日期 |
| `"garmin_status": "not_checked"` 且提示选择语言 | 先执行 `language zh` 或 `language en`，再重新运行检查；这次尚未读取健康数据 |
| `authentication_failed` | 密钥被拒绝；检查是否过期/撤销，重新创建或重新运行 `auth` |
| `garmin_fetch_failed` | 读取失败；可能是网络、密钥或 Garmin 服务问题，不能判断为连接成功 |

完成后按 [豆包／GPT／Claude 接入说明](CLIENTS.md)连接你的 AI。
**保存密钥不等于已经把工具安装进 AI 客户端。**

以后换一个 PowerShell 窗口，要先进入这个项目文件夹再运行以 `.\.venv` 开头的命令。
也可以在文件资源管理器打开项目文件夹，在地址栏输入 `powershell` 后按回车，
这样新窗口会直接在项目文件夹中打开。

## 3. 安装（macOS/Linux）

```sh
git clone https://github.com/1838337544m-droid/garmin-assistant-api.git
cd garmin-assistant-api
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/garmin-assistant init --timezone Asia/Shanghai --goal-km 10 --goal-minutes 60
```

接着**单独**执行认证命令：

```sh
.venv/bin/garmin-assistant auth
```

看到 `Garmin Personal API key (hidden):` 后粘贴自己的整串密钥，再按回车。
macOS 通常用 **Command+V**，Linux 终端通常用 **Ctrl+Shift+V**。
密钥不会显示，也没有星号；不要重复粘贴。输出 `"saved": true` 后再单独验证：

```sh
.venv/bin/garmin-assistant doctor --live
```

确认 `python3 --version` 至少 3.12。上述流程不要求激活虚拟环境。
验证结果的含义见 Windows 部分的表格；客户端路径请使用 `client-config`
生成的绝对路径。密钥输入是在终端内进行，不是在 AI 聊天输入框中进行。

## 首次语言选择与切换

首次使用显示：

```text
欢迎首次使用佳明助手！
Welcome to Garmin Assistant!

请选择语言 / Please choose your language:
1. 中文
2. English
```

终端 `auth` 在保存密钥后会提示输入 1/2。macOS/Linux 也一样。
若密钥通过文件或环境变量提前配置，AI 首次调用时会先问语言；选择前不读取健康数据。
MCP 连接本身不保证客户端立刻弹消息：可以在连接后说“开始使用佳明助手”，
客户端应先调用 `garmin_welcome`。第一条 1/2 回复只用于选语言，不能误当作功能。

语言会保存在个人设置中，升级保留。选择后核心菜单和聊天建议使用对应语言，
生成的明日建议也提供英文版本；原始 Garmin 字段名、论文标题和用户自定义文字保持原样。
随时说“切换为英文 / Switch to English”或“切换为中文 / Switch to Chinese”。
终端可执行 `garmin-assistant language en` / `garmin-assistant language zh`。
也可在初始化时显式指定 `init --language en`，这属于用户主动选择，不再重复询问。

## 4. 功能菜单

1. 同步数据：首次回填 93 天，之后补齐间隔并重查 7 天重叠区间。
2. 分析明天是否适合运动：先同步，再结合个人恢复与跑步目标。
3. 查看运动记录与详情。
4. 查看睡眠、心率和 HRV。
5. 查看区间步数、压力和 Body Battery。
6. 更新长跑训练和康复文献。
7. 查看同步状态或功能菜单。

在连接成功的 AI 中可直接回复编号；数字按菜单原编号解析。
隐藏后剩余编号不会重新从 1 排号，自定义编号从 100 起。

## 5. 每次分析

AI 应先补齐数据；默认明日分析自动执行同步。间隔很长时分段尝试回填，
Garmin 未提供的记录标为缺失，不能当作没运动或数值为零。
资料距上次成功检索满 7 天时重新检索长跑、恢复与康复论文；失败注明旧资料。
结合经典适能—疲劳框架、强度分配与 Daniels 分类并提供出处。
新论文是待评估候选，不代表程序自动验证或更新了训练规则。

主动补充疼痛、疲劳、疾病和明日计划距离。未提供的症状是未知。
明天的建议属于预建议，明早同步睡眠后复评；不保证最快达标时间，
不替代伤病诊疗。目标配速不直接作为每次轻松跑的训练配速。

## 6. 不连接 AI 也能用

以下示例中 `garmin-assistant` 请替换为你的虚拟环境可执行文件路径：

```sh
garmin-assistant sync
garmin-assistant tomorrow
garmin-assistant research
garmin-assistant menu
garmin-assistant menu --hide 1 2 3 4 5 6 7
garmin-assistant menu --original
```

生成的报告路径会输出到终端。没有本地 MCP 的 AI 网页端可以手动上传
该 Markdown/JSON 报告；它是当次快照，不能自行同步你电脑上的数据。

## 7. 自定义与隐藏

```sh
garmin-assistant add-function --name 我的周总结 --instructions "查询最近七天记录，比较跑量和恢复变化，附出处。"
```

隐藏核心：在 AI 中说“隐藏原有功能菜单”，或执行上述 `menu --hide`。
恢复：输入 **显示原有功能菜单**；AI 应调用
`garmin_function_menu(show_original=true)`。CLI 中可用
`garmin-assistant "显示原有功能菜单"`。自定义功能保留。

自定义项目是提示词工作流，需要 AI 理解和执行；不会变成任意 Python 插件。
它不能覆盖核心名称/工具、删除 1–7，也不能绕过证据、同步和症状规则。

## 8. 数据、更新与卸载

用 `doctor` 查看实际数据目录。可通过 `GARMIN_ASSISTANT_HOME` 指定其它目录。
目录包含设置、个人密钥、访问令牌、历史数据库、研究缓存、自定义菜单和报告。
默认不在源码仓库中。更新流程见 [维护与更新](MAINTENANCE.md)。
只删除源码/虚拟环境不会删除用户数据；彻底清除数据需在确认路径后
自行删除 `doctor` 显示的目录。不要在 Issue 粘贴目录内健康内容。

## 9. 故障排查

- 找不到命令：直接使用 `.venv` 下的绝对路径，不依赖 PATH。
- MCP 启动后等待：stdio 模式等待客户端消息是正常行为。
- 密钥错误：在 Garmin 网站重新创建，再运行 `auth` 和 `doctor --live`。
- 无睡眠/HRV：先同步手表，确认设备支持指标；缺失不能解释成零。
- 文献失败：查看研究状态，稍后手动 `research`；不影响已有记录保留。
- 更换 Garmin 账户：使用新的 `GARMIN_ASSISTANT_HOME`，不要复用旧账户历史。
- 手机/网页无法连本地命令：参照平台矩阵，选择报告导入路线。
