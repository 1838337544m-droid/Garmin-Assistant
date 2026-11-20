# 本地 Garmin MCP

已接入 Garmin 官方 Personal API，通过 stdio 在本机运行。

## 版权与使用

本仓库原创代码、文档与测试版权归 **1838337544m-droid © 2026** 所有，保留全部权利；
未经书面许可，不得复制、修改、分发、托管、销售或制作衍生版本。详情见
[LICENSE](LICENSE)、[COPYRIGHT.md](COPYRIGHT.md) 和 [AUTHORS.md](AUTHORS.md)。

第三方 Python 依赖不属于本项目，仍受其各自许可约束；发布包含依赖的安装包前，
请按 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 核对所需声明。本项目独立开发，
不隶属或获得 Garmin 认可。

未经事先书面批准不接受外部贡献，规则见 [CONTRIBUTING.md](CONTRIBUTING.md)；对外分享前
使用 [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)，并在 [VERSION_HISTORY.md](VERSION_HISTORY.md)
保留版本与归档校验记录。

## 怎么用

本服务已注册到 Codex 的全局 MCP 配置，名称为 `garmin_local`。
重新启动 Codex 后，在 MCP 设置中确认它已启用，然后可以直接问：

- “用本地 Garmin 数据看看我今天的睡眠。”
- “查询最近 7 天的步数和压力变化。”
- “列出最近三次运动，查看最近一次的详情。”
- “刷新 Garmin，读取最新数据。”

你不需要手动启动 Python。Codex 会启动本地服务进程。
其他 AI 客户端需要单独添加相同的 stdio 命令，不会自动共享 Codex 配置。

程序：`D:/garmin/local-mcp/.venv/Scripts/python.exe`

参数：`D:/garmin/local-mcp/server.py`

## 同步行为

提问时按需读取 Garmin，查询结果保存在本机 SQLite。
同一查询在 15 分钟内复用缓存；`refresh=true` 强制更新。
查询失败时，有缓存则返回 `stale` 并带上原读取时间；无缓存则返回错误。
空结果表示没有可用数据，不能解释成零。日期默认按 Asia/Dubai 确定，
数据中的 Garmin 日历日期、时间戳和单位保持原样。

这里没有设置定时任务或后台通知，也不会自动下载整个账户的历史数据。
未查询的数据不会持续采集。较长时间的趋势通过范围查询和运动分页获取。
手表必须先同步到 Garmin Connect，本服务才能读到新数据。

## 文件位置

- 个人密钥：`D:/garmin/API.txt`（保留原文件，只包含密钥）
- 缓存和访问令牌：`%LOCALAPPDATA%/GarminLocalMCP/`
- MCP 配置：`C:/Users/User/.codex/config.toml`
- 验证报告：本目录 `verification-report.json`（只有状态及大小，没有健康数值或密钥）

密钥文件及缓存目录已设置当前 Windows 用户和 SYSTEM 的访问权限。
密钥不会写入 MCP 配置或传给模型。服务仅访问 Garmin 官方 Personal API 主机。
官方 SDK 自动更新访问令牌；个人密钥到期后需要在 Garmin 网站重新创建，
将新密钥替换到 `API.txt`，然后让 AI 强制刷新。更新后建议重启 Codex。
若换成另一个 Garmin 账户，先退出 Codex，再移走本地缓存目录，避免使用旧账户缓存。

## 提供的工具

| 工具 | 用途 |
|---|---|
| garmin_status | 缓存覆盖和同步状态，不联网 |
| garmin_daily_summary | 指定日期的健康日汇总 |
| garmin_sleep | 睡眠和可用的分期数据 |
| garmin_heart_rate | 指定日期心率 |
| garmin_hrv | 指定日期心率变异性 |
| garmin_range | 步数、压力、Body Battery 范围查询 |
| garmin_activities | 运动记录列表，支持日期过滤和分页 |
| garmin_activity_detail | 指定运动详情 |

全部为只读工具。可用字段受 Garmin Personal API、设备和已同步记录限制。
没有实现训练准备度、写入训练计划或手表实时数据。

## 新增：同步与明日训练建议

新增三个工具（重启 Codex 后加载）：

| 工具 | 用途 |
|---|---|
| garmin_sync_data | 首次回填 93 天；之后重取最近 7 天重叠区间并同步新日期；full=true 完整重取 |
| garmin_assess_tomorrow | 自动同步、检查文献缓存，结合个人 HRV/睡眠/静息心率及跑步记录给出明日预建议 |
| garmin_update_research | 联网更新长跑训练、恢复及回跑康复论文候选资料 |

直接说“同步 Garmin 数据”“分析明天是否适合运动”“更新长跑训练和康复文献”即可。
训练目标已设为 **10 公里跑进 60 分钟**。日常轻松跑以谈话强度为准，
不要求每次都按目标比赛配速跑，也不承诺最快达标周数。

分析时可附上当前疼痛/疲劳评分、疾病、步行痛、局部骨痛、胸痛/晕厥情况
以及计划距离。未提供的项目保留“未知”，不会默认没有症状。
今晚睡眠未知，所以明日结果始终是预建议，明早同步后应复评。

数据历史保存在解析后的 `%LOCALAPPDATA%/GarminLocalMCP/history.sqlite3`。
Windows Store Python 可能将该目录映射到 WpSystem 下；程序会解析真实路径。
增量同步会保留更早的历史；成功更新区间按 Garmin 当前记录校正，
失败区间保留原数据并报告 partial。full=true 可校正更早日期的修改/删除。

中文报告及 JSON 保存到 `D:/garmin/reports/readiness_日期.md` 和同名 JSON。
报告目录含健康数据，已经限制为当前 Windows 用户和 SYSTEM 可访问。
迁移电脑时，历史数据库和个人报告都是可选项，API.txt 仍然需要妥善传输。

文献更新优先使用 PubMed API，失败时通过 EMBL-EBI Europe PMC 获取 PubMed
收录论文。只发送文献检索词，不发送健康数据。默认分析时至多每 7 天
重新检索一次，手动更新可立即检索。成功/失败时间与来源会记录在报告中。
预置 6 篇经过核验的 2024–2026 年文献作为解释依据；新检索论文属于
待评估候选，不会自动改写判断规则。该检索不是穷尽式系统综述。

无需额外 AI API 密钥；数值筛查与初步建议在本地执行，由聊天中的 AI
结合数据、引用和你的主观信息解释。规则是可解释的训练辅助，
不等同于医学放行、精确伤病预测或 Garmin 官方训练准备度。

也可以在本目录用命令行：

```powershell
.\.venv\Scripts\python.exe cli.py sync
.\.venv\Scripts\python.exe cli.py sync --days 93 --full
.\.venv\Scripts\python.exe cli.py tomorrow
.\.venv\Scripts\python.exe cli.py research
```

`tomorrow --no-sync --no-research` 可离线查看辅助报告，但会明确显示
数据未在本次确认更新，不据此批准质量训练。没有新增定时后台任务。

## 多运动能力处方（2026-11-20）

每次评估会同时生成离线 HTML 日报。多项目结果返回 `report_html` 路径；
旧跑步报告的同名 `.html` 文件也可直接用浏览器打开。页面包含能力总结、
数据缺项、研究来源和运动选择区。选择区生成可复制的 MCP 请求，
不会在浏览器中自行计算或保存新的处方。页面无需网络字体或外部脚本。

使用 `garmin_set_athlete_profile` 保存长期主项与目标，再调用 `garmin_assess_session`
选择明天的项目：running、cycling、swimming、climbing 或 other。配置写入本地，
Garmin 数据工具仍只读。游泳需提供 shoulder_pain=false 和 swimming_alone=false，
否则降级恢复。攀岩不能从 Garmin 推断指力、肌腱或皮肤准备度。

新报告包含行动、能力总结、依据、缺项与降级条件，每次保存为独立文件。
首期骑车、游泳和攀岩提供保守方向，不生成质量课或未经核验的配速、瓦数、等级、时长。
专项研究尚待核验；原跑步工具及旧报告格式保留。

## 每次分析的固定流程（2026-10-31）

1. 先补齐上次完整同步后至今的健康和运动数据，重查 7 天重叠区间；
   即使间隔超过默认 93 天，也尝试补齐整个间隔，分析仍使用近期 93 天。
   接口无法提供的记录或同步失败会明确报告，不保证 Garmin 保留所有历史。
2. 文献成功检索距本次满 7 天就重新检索，未满可复用；可强制刷新。
   检索失败保留旧文献并标注状态，不能把旧结果说成最新检索。
3. 结合长跑/恢复研究与 Banister–Morton 适能—疲劳框架、Seiler 强度分配、
   Daniels 强度分类，附出处、年份、具体用途和适用限制。
   未拟合个人模型参数、完整强度分布或 VDOT 时，不声称已经算出。
4. 回答末尾返回现有功能菜单；菜单只列出已实现功能。

`garmin_function_menu` 可随时查看菜单和规则，不联网。
当前共 12 个 MCP 工具、7 类用户功能。重启客户端以加载新增菜单工具和流程指令。

## 检查与维护

在本目录打开 PowerShell：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe verify_live.py
codex mcp get garmin_local
```

`verify_live.py` 通过真实 MCP 子进程检查认证及各类数据读取，
会更新查询缓存，但只输出结果状态和数据大小。

移除 Codex 中的注册（不删除文件）：

```powershell
codex mcp remove garmin_local
```

首次修改前的配置备份位于 `C:/Users/User/.codex/config.toml.garmin-backup-*`。

参考：
- https://developer.garmin.com/gc-developer-program/personal/personal-api/
- https://github.com/garmin/connect-personal-api-python
