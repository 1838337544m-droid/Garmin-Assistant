# Self-check Records | 自检记录
[English version](#english-version) | [中文版本](#中文版本)

## English version

### Version 0.1.0 — local verification

Date: 2026-10-31. Windows, Python 3.13.

| Check | Result |
|---|---|
| Fresh virtual-environment installation | Passed |
| Synthetic suite | 50 tests and 7 subcases passed |
| Dependency consistency (`pip check`) | Passed |
| Source and wheel builds | Passed; SHA256 included |
| Local stdio discovery | 16 tools |
| Add extension → hide core → restore original → retain extension | Passed through actual MCP calls |
| Delete a core function | Rejected |
| Concurrent custom additions | All 16 retained with unique sequential IDs |
| Custom goal/timezone | Persistence, reload and non-UTF-8 terminal regressions passed |
| Official Garmin connection | Passed with an external key path; validation data was not committed |
| Release-file auditing | No known key pattern, private absolute path, database or health report found |

See repository Actions for cross-platform synthetic results. These do not establish end-to-end support
for every Doubao/GPT/Claude client edition. See [client limits](CLIENTS.md). Pattern scanning cannot rule out every unknown secret format.

### Version 0.1.2 — language and first-use verification

The local suite increased to 62 tests and 7 subcases. Actual stdio first-use checks discover 18 tools;
before language choice, health tools return the bilingual welcome without reading health data.
An explicit English choice changes menus while preserving IDs. Synthetic regressions cover terminal
authentication prompts, saved language switching, English reports, urgent-symptom priority and guarding
live diagnostics before language selection.

Immediate popups depend on the client. The project prompts at first interaction; MCP cannot independently push chat messages.

### Version 0.1.3 — bilingual documentation checks

The README and public guides place English above Chinese, with language links directly below each
document title. Navigation, local links, code-fence balance and the release-file audit are checked before publication.
Runtime behavior is unchanged by this documentation release.

---

## 中文版本

日期：2026-10-31；Windows，Python 3.13。

| 检查 | 结果 |
|---|---|
| 独立虚拟环境安装 | 通过 |
| 合成测试 | 50 项及 7 个子用例通过 |
| 依赖一致性 pip check | 通过 |
| 源码包、wheel 构建 | 通过，附 SHA256 |
| 本地 stdio MCP 工具发现 | 16 个工具 |
| 添加扩展→隐藏核心→恢复原菜单→保留扩展 | 通过真实 MCP 调用 |
| 删除核心功能 | 被拒绝 |
| 多进程并发添加工作流 | 16 个扩展均保留，ID 连续且不重复 |
| 自定义目标与时区 | 配置、重载和非 UTF-8 终端回归测试通过 |
| 官方 Garmin API 连接 | 通过；密钥从仓库外读取，验证数据未加入仓库 |
| 待发布文件检查 | 无已知密钥格式、私人绝对路径、数据库、健康报告 |

跨系统合成测试结果请查看仓库 Actions；不能将它等同于所有豆包/GPT/Claude
客户端版本均已端到端验证。具体安装边界见 [CLIENTS.md](CLIENTS.md)。
模式扫描只作辅助，不能证明排除一切未知秘密格式。

## 0.1.2 语言与首次使用自检

本机完整测试更新为 62 项及 7 个子用例通过。新增实际 stdio 首次调用验证：
18 个 MCP 工具；语言未选择时健康工具返回双语欢迎，不读取数据；明确选择
English 后菜单切换并保留原有编号。终端认证提示、语言切换保存、英文报告、
紧急症状优先级及未选语言的在线诊断保护均有合成回归测试。
客户端是否在连接时立即弹出消息仍取决于宿主；程序保证首次交互提示，
不声称 MCP 可主动推送聊天消息。

## 0.1.3 双语文档检查

README 和公开文档统一为英文在上、中文在下，标题下紧接语言导航。
发布前检查导航、本地链接、代码框配对和待发布文件；本版不改变运行逻辑。
