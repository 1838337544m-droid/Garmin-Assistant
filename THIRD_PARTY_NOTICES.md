# Third-party Notices | 第三方来源与依赖
[English version](#english-version) | [中文版本](#中文版本)

## English version

This is an independent project, not an official Garmin product. Garmin and Garmin Connect are trademarks
of their respective owners. Each user uses their own key for the official Personal API.

Runtime dependencies include Garmin's `garmin-connect-personal-api-python` (Apache-2.0), MCP Python SDK
(MIT), HTTPX (BSD-3-Clause), and tzdata under its included license. Dependencies are installed from package indexes, not
embedded in this source repository. Check installed metadata for transitive dependency licenses.

The following projects were examined for public installation/update patterns, not copied implementations:

- [Mason-Levyy/garmin-personal-mcp](https://github.com/Mason-Levyy/garmin-personal-mcp): separate authentication, stdio, quickstart and changelog.
- [Sinfjell/garmin-mcp](https://github.com/Sinfjell/garmin-mcp): client-specific configuration, capability and privacy explanations.
- [Fullstop000/doubao-cli](https://github.com/Fullstop000/doubao-cli): optional third-party Doubao registration, not official compatibility assurance.

Papers are cited by title, date and URL; paywalled full text is not redistributed. Retrieved abstracts
support personal evidence screening. Reports distinguish reviewed references from unappraised candidates.
See [sources and verification](docs/REFERENCES.md).

---

## 中文版本

本项目不隶属 Garmin，不是 Garmin 官方产品。Garmin/Garmin Connect
商标归各自权利人所有。使用官方 Personal API，各用户仅使用自己的密钥。

运行时使用 Garmin 官方 `garmin-connect-personal-api-python`（Apache-2.0）、
MCP Python SDK（MIT）、HTTPX（BSD-3-Clause）以及 tzdata（其自带许可）。安装器从包索引安装依赖，
源码仓库不内嵌这些依赖的代码。具体传递依赖许可请查所安装版本元数据。

参考项目只用于研究公开的安装/更新模式，未复制其实现：
- [Mason-Levyy/garmin-personal-mcp](https://github.com/Mason-Levyy/garmin-personal-mcp)：独立认证、stdio、快速入门和更新记录。
- [Sinfjell/garmin-mcp](https://github.com/Sinfjell/garmin-mcp)：客户端配置分节、能力范围与隐私说明。
- [Fullstop000/doubao-cli](https://github.com/Fullstop000/doubao-cli)：第三方豆包本地 MCP 注册方式；不是豆包官方保证。

论文按标题、日期和链接引用，不分发付费全文。新检索摘要仅用于个人
证据筛选，报告区分已核验依据与未评估候选。出处详见 [参考模式与自检](docs/REFERENCES.md)。
