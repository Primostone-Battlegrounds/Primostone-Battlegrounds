# Primostone: Battlegrounds

- 从 [README](README.md) 安装固定版本 OpenHarness，按 [.harness/AGENT.md](.harness/AGENT.md) 进入工程。
- [BACKLOG.md](BACKLOG.md) 及其任务文件是工作权威。先核对目标分支和远端 PR，每个任务单独 worktree 与 PR。
- Bootstrap 合并且审查问题解决后才启动 Worker。`G0-VERIFY` 独立审批并实际合入 `main` 后才允许执行 M0–M2。
- 每个 PR 最多 400 行生产增删、10 个生产文件。验收以任务证据为准。
