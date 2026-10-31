# 参考分享模式、来源与验证范围

资料核对日期：2026-10-31。参考的是组织方式，不复制其他项目的实现或个人数据。

| 来源 | 参考点 | 本项目采用/限制 |
|---|---|---|
| [Mason-Levyy/garmin-personal-mcp](https://github.com/Mason-Levyy/garmin-personal-mcp) | 独立 auth、stdio、快速入门、版本记录 | 采用命令分工；仍使用本项目自己的同步、历史及建议模块 |
| [Sinfjell/garmin-mcp](https://github.com/Sinfjell/garmin-mcp) | 按客户端列安装与能力说明 | 区分本地 MCP 与网页报告方式；不复用非官方密码登录实现 |
| [Fullstop000/doubao-cli](https://github.com/Fullstop000/doubao-cli) | 豆包第三方 MCP 注册示例 | 仅列为可选路线，说明其系统限制和未验证状态 |
| [Claude 官方本地 MCP](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop) | 本地服务器/桌面扩展的区别 | 给出配置方式，不声称本项目已上架桌面扩展 |
| [OpenAI MCP 文档](https://learn.chatgpt.com/docs/extend/mcp) | 本地 stdio 与配置 | 区分有本地执行器的客户端和普通网页聊天 |
| [豆包开放平台](https://open.doubao.com/) | Skill/Plugin/MCP 概念 | 不能据此保证每种豆包客户端的安装能力 |
| [Garmin Personal API FAQ](https://developer.garmin.com/gc-developer-program/personal/personal-faq/) | 每人使用自己的个人密钥 | 无共享账号、无维护者代管多用户服务 |

## 自检范围

- 继承原有同步、区间缓存、失败保留、缺失处理、恢复判断与文献测试。
- 新增核心隐藏/恢复、扩展冲突、稳定编号、自定义目标、配置隔离测试。
- 本机验证 Windows 新虚拟环境安装、CLI、构建包、真实 stdio 工具发现与调用。
- GitHub CI 验证 Windows/macOS/Linux + Python 3.12/3.13 的合成测试。
- 发布包和待提交文件扫描密钥模式、私有路径、数据库及健康报告。

本项目未对所有豆包/GPT/Claude 产品版本做真人账号端到端验证。
MCP 协议测试通过不等于每个聊天客户端的安装入口均已验证；按手册验收。

## 运动科学出处

报告引用程序内的已核验文献与经典模型，并注明年份和具体应用。
核心解释包括 [Banister–Morton 适能—疲劳模型](https://pubmed.ncbi.nlm.nih.gov/2246166/)、
[Seiler 耐力强度分配](https://pubmed.ncbi.nlm.nih.gov/20861519/) 与
[Daniels’ Running Formula](https://us.humankinetics.com/products/daniels-running-formula-4th-edition)。
这些是解释框架；没有个人测试时不假装已拟合完整模型或获得 VDOT。
