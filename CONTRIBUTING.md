# Contributing and Core Compatibility | 贡献与核心兼容
[English version](#english-version) | [中文版本](#中文版本)

## English version

```sh
python -m pip install -e ".[dev]"
python -m pytest -q
python scripts/check_release.py
```

Submit synthetic tests only; never upload personal keys, real activities or health reports.
Core IDs and meanings are a compatibility contract: extensions may add separate functions but may not
rename, remove or override core actions. Hiding is display preference, not permission revocation.

For ordinary customization use `add-function`, without editing source. Propose new APIs, algorithms
or executable tools through a PR explaining evidence, tests and migration. Threshold changes need
their own evidence and uncertainty record; a new paper alone does not justify automatic replacement.

MIT permits modification and forks. The core compatibility rule governs official releases and the
extension interface, not a legal or technical ban on changing open-source code.

---

## 中文版本

```sh
python -m pip install -e ".[dev]"
python -m pytest -q
python scripts/check_release.py
```

提交只使用合成数据的测试。不得上传个人密钥/真实活动/健康报告。
核心七类功能的编号和含义是兼容契约：扩展不能重命名、删除或覆盖，
只能添加独立功能。隐藏是展示偏好，不是撤销权限；用户需要时仍可调用核心工具。

普通用户添加功能请用 `add-function`，无需改源码。需要新 API、算法或
可执行工具时提交 PR，并说明依据、测试和迁移方案。规则阈值变化需要
单独记录证据及不确定性，不能仅因出现新论文就自动替换。

MIT 许可允许自行修改和 fork。这里的核心兼容是官方发行版及扩展接口
约定，不是对他人修改开源代码的技术或法律封锁。
