# Primostone: Battlegrounds

- 从 [README](README.md) 安装固定版本 OpenHarness，按 [.harness/AGENT.md](.harness/AGENT.md) 进入工程。
- `develop` 上的 [BACKLOG.md](BACKLOG.md) 及任务文件是唯一任务授权来源。任务从已验证的 develop 提交原子认领 `task/<ID>`，独立 worktree，PR 回 develop。先核对依赖实际合入、分配和独占路径。
- 默认分支 main 只接发布及已发布版本的 hotfix；完整流程和迁移例外见 [GitFlow](docs/architecture/gitflow.md)。保护与三条 PR 路径验证完成后才切换 Worker。
- 独立评审指另一个 subagent / AI 审查代码、测试、证据和控制面，不要求另一个 GitHub 账号批准。评审记录绑定最终 head；新推送必须重审，CI 校验记录。实现者不得自己冒充独立评审者。
- Bootstrap 已合并且 AI 复核问题解决后才启动 Worker。`G0-VERIFY` 保留六项真实实机证据及独立 AI 复核，首次成果实际进入 main 后才解锁 M0–M2。
- 任务和维护 PR 最多 400 行生产增删、10 个生产文件。验收以任务证据为准；发布 PR 另核对已审查合入的任务、精确候选和产物摘要。
