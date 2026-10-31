# 用户手册

## 1. 首次准备

安装 Python 3.12 或更新版本与 Git。每位用户在自己的 Garmin Connect
[Personal API 页面](https://connect.garmin.com/app/settings/personalApiToken)
创建个人密钥；不要使用维护者或其他人的密钥。

默认时区 UTC。请通过 `init` 设置自己的 IANA 时区，例如中国
`Asia/Shanghai`、迪拜 `Asia/Dubai`。目标可自行修改；不会更改核心菜单。

## 2. 安装（Windows PowerShell）

```powershell
git clone https://github.com/1838337544m-droid/garmin-assistant-api.git
cd garmin-assistant-api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\garmin-assistant.exe init --timezone Asia/Shanghai --goal-km 10 --goal-minutes 60
.\.venv\Scripts\garmin-assistant.exe auth
.\.venv\Scripts\garmin-assistant.exe doctor --live
```

`auth` 在终端隐藏输入密钥；不把密钥粘贴到 AI 聊天或写入命令参数。
若 `python` 不存在，可使用已安装的 `py -3.12` 创建虚拟环境。

## 3. 安装（macOS/Linux）

```sh
git clone https://github.com/1838337544m-droid/garmin-assistant-api.git
cd garmin-assistant-api
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/garmin-assistant init --timezone Asia/Shanghai --goal-km 10 --goal-minutes 60
.venv/bin/garmin-assistant auth
.venv/bin/garmin-assistant doctor --live
```

确认 `python3 --version` 至少 3.12。上述流程不要求激活虚拟环境。
客户端下载路径和命令请使用 `client-config` 生成的绝对路径。

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
