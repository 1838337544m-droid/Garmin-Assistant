# Garmin 助手（API）版本

用自己的 Garmin Personal API 密钥，在本机同步运动与健康数据，让 AI 结合
长跑训练、恢复研究和经典模型提供有出处的建议。

**不需要 Garmin 密码；不托管他人账号；不附带维护者的个人数据。**
本项目独立开发，不隶属 Garmin。

[安装与用户手册](docs/USER_GUIDE.md) · [豆包/GPT/Claude 接入](docs/CLIENTS.md) ·
[更新与发布](docs/MAINTENANCE.md) · [参考与验证范围](docs/REFERENCES.md) · [更新记录](CHANGELOG.md)

## 快速安装

需要 Python 3.12+ 和 Git。在 PowerShell 中：

```powershell
git clone https://github.com/1838337544m-droid/garmin-assistant-api.git
cd garmin-assistant-api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\garmin-assistant.exe init --timezone Asia/Shanghai
.\.venv\Scripts\garmin-assistant.exe auth
.\.venv\Scripts\garmin-assistant.exe doctor --live
```

`auth` 隐藏输入你自己的个人密钥。默认目标为 10 公里/60 分钟，可在
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
