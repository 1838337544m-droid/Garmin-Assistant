# Release Design and Implementation | 发布设计与实施
[English version](#english-version) | [中文版本](#中文版本)

## English version

Goal: an independently installable, updatable local MCP release, retaining the seven core functions.
Users can hide them, add separate prompt workflows and restore the original menu without losing extensions.

Architecture: a Python package, stdio MCP and local CLI. Settings, keys, databases, reports and menu
preferences live outside the source checkout. Documentation follows common auth/serve/quickstart/changelog
patterns while preserving this project's own implementation. Clients without local stdio use report upload.

1. Copy only allowlisted source and synthetic tests, not real health data, keys or private history documents.
2. Add portable configuration, timezones, goals, standard installation and CLI diagnostics.
3. Use immutable core definitions/reserved IDs and separate extension IDs; never override core tools.
4. Test hiding/restoration, persistence, conflicts, directory isolation and existing sync/analysis behavior.
5. Document Doubao/GPT/Claude routes, official references and actual verification limits.
6. Add versioning, updates, builds, CI, release auditing and independent code review.
7. Create the authorized public GitHub repository, push clean source and publish releases.

Application-level locking cannot prevent forks or source edits. Custom functions are prompt workflows,
not arbitrary executable Python plugins; these interface constraints are consistent with MIT licensing.

---

## 中文版本

目标：独立、可安装、可反复更新的本地 MCP 分享；保留原有七类核心功能，
允许隐藏和添加提示词工作流，用“显示原有功能菜单”恢复核心菜单。

方案：独立 Python package + stdio MCP + 本地 CLI。配置、密钥、数据库、
报告和自定义菜单均放用户数据目录，代码更新不覆盖。参考现有 GitHub 项目
的 auth/serve/quickstart/changelog 模式，保留本项目自己的实现。
不把不支持本地 stdio 的网页聊天端描述为已支持；提供报告文件导入路线。

1. 仅复制允许清单内源码和合成测试，不复制真实健康数据或个人历史文档。
2. 加入可移植配置、时区和训练目标；标准安装入口及 CLI 自检。
3. 核心菜单采用不可变定义及保留编号；扩展编号独立，不能覆盖核心工具。
4. 测试隐藏/恢复、跨版本持久化、扩展冲突、目录隔离和原有同步/分析行为。
5. 文档覆盖豆包/GPT/Claude，清楚标注验证方式、官方来源及限制。
6. 添加版本、更新手册、打包、CI、发布和泄漏自检；独立代码审查。
7. 在授权 GitHub 账号创建公开仓库，推送清理后的源码并发布首个版本。

限制：应用内核心锁定不能阻止公开源码被修改或 fork；自定义功能是用户
提示词工作流，不执行任意第三方 Python。MIT 许可与此应用层约束不冲突。
