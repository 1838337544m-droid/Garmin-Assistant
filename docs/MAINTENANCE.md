# Updates, Releases and Rollback | 更新、发布与回滚
[English version](#english-version) | [中文版本](#中文版本)

## English version

### User updates

Installed using the Windows ZIP? Download the new release's Windows installer, run it, then
select **Replace an existing Garmin entry** in the setup window to switch the client to the new runtime.
See [guided updates](EASY_INSTALL.md#english-version). The Git commands below are for source installations.

Settings, keys, databases and extensions are in a separate personal data directory.
For a backup, stop the MCP, confirm the directory with `doctor`, and copy it.

In the original clone, first check for your own changes to tracked files:

```sh
git status
git pull --ff-only
python -m pip install -e .
garmin-assistant --version
garmin-assistant doctor
```

Use the Python and executable from your installation's `.venv`, then restart the AI client.
If you edited source, preserve it on a branch or resolve the changes yourself; do not force-reset it.
Ordinary custom workflows belong in `add-function`, not in tracked source files.

### Maintainer release process

1. Update code/docs, `CHANGELOG.md`, `pyproject.toml`, and `src/garmin_assistant/__init__.py`. Versions must match.
2. Run tests, release-file auditing and package builds; check core IDs and restoration.
3. Commit and push, then wait for Windows/macOS/Linux CI success.
4. Push a `vX.Y.Z` tag. `release.yml` builds source/wheel files and SHA256 checksums and creates the bilingual GitHub Release.
5. Share the repository or Releases/latest URL so users can find the current version and instructions.

```sh
python -m pytest -q
python scripts/check_release.py
python -m build
git add src tests docs README.md CHANGELOG.md pyproject.toml scripts .github
git commit -m "Release vX.Y.Z"
git push
git tag vX.Y.Z
git push origin vX.Y.Z
```

This project does not automatically publish to PyPI or require users to execute remote update scripts.
The GitHub release workflow uses the repository-provided GITHUB_TOKEN, not a stored personal key.

### Compatibility and rollback

1. Patch releases fix issues; minor releases add compatible features. Core contracts/data-format breaks require major-version explanation.
2. Current settings/menu schema is version 1; unknown versions must fail rather than clear preferences.
3. Keep old tags/releases. Back up data before rollback; older code is not guaranteed to read future formats.
4. Clone an old tag into a separate directory, create its own `.venv`, and test against copied data before switching clients.
5. Do not delete custom workflows, renumber core actions or move user extensions into source.

---

## 中文版本

## 用户更新

通过 Windows ZIP 安装的用户：下载新版安装包并运行，在设置窗口勾选“替换已有佳明连接条目”，
即可将客户端切换到新版运行环境。详见[引导更新说明](EASY_INSTALL.md#中文版本)，下方 Git 命令适用于源码安装。

配置、密钥、数据库和扩展都在个人数据目录，源码更新不覆盖。
需要备份时先退出 MCP，用 `doctor` 确认目录，再复制该目录。

在原克隆目录，确认没有自行修改受版本控制的文件：

```sh
git status
git pull --ff-only
python -m pip install -e .
garmin-assistant --version
garmin-assistant doctor
```

上面的 Python/命令须替换为安装用的 `.venv` 路径。重启 AI 客户端。
若存在个人源码修改，先另存分支或自行处理，不用 reset/强制覆盖。
普通扩展应通过 `add-function`，无需编辑仓库文件。

## 维护者发版

1. 修改代码与文档，更新 `CHANGELOG.md` 和两个版本位置：`pyproject.toml`
   与 `src/garmin_assistant/__init__.py`。版本必须一致。
2. 执行 `pytest`、发布文件扫描、构建，检查核心编号与恢复操作。
3. 提交并推送；等待 Windows/macOS/Linux CI 全通过。
4. 打 `vX.Y.Z` 标签并推送；`release.yml` 构建源码包和 wheel，附 SHA256，
   通过 GitHub CLI 创建名为“Garmin Assistant (API edition) | Garmin 助手（API）版本 vX.Y.Z”的双语 Release。
5. 分享仓库首页或 Releases/latest 链接，用户始终能找到当前版本和说明。

```sh
python -m pytest -q
python scripts/check_release.py
python -m build
git add src tests docs README.md CHANGELOG.md pyproject.toml scripts .github
git commit -m "Release vX.Y.Z"
git push
git tag vX.Y.Z
git push origin vX.Y.Z
```

本项目没有自动向 PyPI 发布，也没有要求用户自动执行远程更新脚本。
GitHub release workflow 仅需仓库自带的 GITHUB_TOKEN，不需要保存个人密钥。

## 兼容与回滚

1. 补丁版本修复问题；次版本增加兼容功能；改变数据格式或核心契约需主版本说明。
2. 当前 settings/menu schema_version 为 1；未知版本应报错而不是清空偏好。
3. 保留旧版本标签和 Release。回滚前备份数据，不承诺新数据格式可由旧版读取。
4. 可在新的目录克隆旧标签，另建 `.venv`，用副本数据测试后再切换客户端。
5. 不自动删除用户自定义工作流，不重排核心编号，也不把扩展写入源码。
