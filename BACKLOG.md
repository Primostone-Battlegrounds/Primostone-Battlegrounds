# Backlog

本入口与 [backlog/tasks](backlog/tasks/) 组成唯一工作权威，状态和依赖以 GitHub `main` 的任务文件为准。[OpenHarness Backlog 契约](https://github.com/FurinyaDev/OpenHarness/blob/aebb0c2255a5df275491009285c1a23d03f90771/docs/backlog-profile.md) · [Backlog.md 1.53.0 参考解析器](https://github.com/MrLesk/Backlog.md/blob/fd20f71493fb4eda44b021aa89f257956f17fb71/src/markdown/parser.ts)

候选规则以 [规则与接口基线](docs/architecture/product-baseline.md) 为准。实现 UI 前读 [棋阵界面和原创美术](docs/architecture/ui-art-direction.md)。源码取样与验证见 [社区实现调研](docs/architecture/community-implementations.md)；迭代与发行验收见 [发布路线](docs/architecture/release-roadmap.md)。

| 阶段 | 版本与交付 |
| --- | --- |
| Gate 0 | `0.0.1`，六项实机实验证据和 [G0-VERIFY](backlog/tasks/g0-7%20-%20G0-VERIFY.md) 独立复核合入。 |
| M0 | `0.1.0`，确定性 Lua 核心，两席终局及快照重放验证。 |
| M1 | `0.2.0`，1 真人 + 1 AI 的垂直切片，有原创规则与样例美术。`0.3.0`，1 真人 + 7 AI、40–50 个原创随从、完整界面与单人恢复。 |
| M2 | `0.4.0`，四人私有试玩、权威协议、隐私、重连、PC 和移动发布候选。 |

OpenHarness 规定原生 ID 为字母前缀加数字。`g0-7` 是 `G0-VERIFY` 的任务 ID，GitHub PR 使用 `Work-Item: g0-7`。模型字段在原生契约中对应如下。

| 项目所需字段 | 唯一存放位置 |
| --- | --- |
| `id`、`milestone`、`type`、`priority` | 任务文件同名前置字段 |
| `depends_on` | `dependencies` |
| `exclusive_files` | `modified_files` 为逐条精确路径，另含任务自己的文件 |
| `acceptance_criteria`、`verification_evidence` | 任务正文的 `Acceptance criteria` 和 `Verification evidence` |

## 从无历史 Session 开始

1. 按 [README](README.md) 安装并读取 `entry`。确认 Bootstrap PR 已经独立审查、问题已解决并实际合入，且 main 原生检查与审批规则生效。
2. 读取 `origin/main` 对应任务。`Blocked` 表示环境、能力或证据缺口；解除条件满足后由维护者的任务编排 PR 修改状态和明确映射执行者。`To Do` 或 `In Progress` 仍须满足全部传递依赖为 Done。待分配任务不可认领；有多人并行时由编排 PR 补充真实 GitHub 登录映射，一个任务只配一个执行者。
3. 在工作前观察远端任务分支、全部打开的 PR、合入记录。使用 `git ls-remote --heads origin 'refs/heads/task/*' 'refs/heads/codex/backlog-*'` 和 `gh pr list --state open --json number,headRefName,baseRefName,author,url`。现有同任务分支或 PR 表示任务已被占用；历史分支、续接和移交由维护者协调。任务完成仍以目标分支合并为准。
4. 对依赖已合入、已分配且无冲突的任务，用 GitHub 创建引用接口原子认领 `task/<id>`。创建成功后再次核对全部 PR、最新目标分支及独占文件。认领先于实现，每个独立工作树只由一个 Session 写入。OpenHarness 在隔离工作树中绑定原分支。
5. 向目标仓库发出一个任务 PR，正文有且仅有一行 `Work-Item: <id>`，并提供可复查验收证据。完成状态在同一 PR 中提交，其他 Session 只有在确认 `main` 上的结果及实际 merge SHA 后才将其视为 Done。维护者独立审批源码、证据和控制面；已批准后可按 OpenHarness 流程 `integrate --pr N`，之后 `release`。任务拆分、版本计划、依赖调整和分配通过独立维护 PR 审查。维护 PR 只变更计划和控制，使用真实测试证据，保持 Gate 0 状态及开发限制。

认领时把 `TASK_ID`、`CHANGE_NAME` 和 `TASK_WORKTREE` 设为已验证的任务 ID、短名和当前 Session 的独立路径，在仓库根目录执行。

```sh
git fetch --prune origin
gh api --method POST repos/Primostone-Battlegrounds/Primostone-Battlegrounds/git/refs -f "ref=refs/heads/task/${TASK_ID}" -f "sha=$(git rev-parse origin/main)"
```

GitHub POST 成功才获得认领权。引用已存在或请求失败时重新同步并选择任务。成功并完成并发复查后创建本地工作树。

```sh
git fetch origin "refs/heads/task/${TASK_ID}:refs/remotes/origin/task/${TASK_ID}"
git worktree add --track -b "task/${TASK_ID}" "${TASK_WORKTREE}" "origin/task/${TASK_ID}"
cd "${TASK_WORKTREE}"
python3 -m openharness --repo . workspace --task "${TASK_ID}" --change "${CHANGE_NAME}" --bind
```

OpenHarness 将工作树绑定到整个 Backlog 的摘要。其他任务合入或维护 PR 调整分配后，仍在进行的任务可能需要复绑。先在最新 `origin/main` 核对该任务仍归当前执行者、依赖已完成且工作范围未改变。在原任务工作树提交未保存的改动，将最新 `main` 合入任务分支并解决冲突。在干净工作树用原 ID 和 change 名运行 `python3 -m openharness --repo . workspace --task <id> --change <short-name> --bind`，再运行 `preflight` 和候选验证。推送到原分支，重新获取当前 head 的检查和独立审批。任务已被移交或完成时由维护者协调。

## Gate 0 证据与解除条件

目前六项实验以及 `G0-VERIFY` 均为 `Blocked`。先安排创作账号、区服、版本匹配的原神客户端与编辑器、PC 和移动真机以及四人私有试玩环境。Worker 只构建任务所需探针；按任务正文定量验收。一项必要实验无法实测或失败就保持 `Blocked`，记录缺失环境或能力和复测步骤。

每个实验证据文件 `docs/verification/gate0/<id>.md` 至少记录日期、区服、编辑器和游戏构建号、设备/系统、探针提交、GIL SHA-256、准备步骤、阈值、每项观测结果、失败样本及复现步骤。通过后填写独立的三行 `Result: PASS`、`Platform evidence: https://…` 和 `Verification pull request: https://github.com/Primostone-Battlegrounds/Primostone-Battlegrounds/pull/<number>`。原始日志、导出摘要及录屏需可供复核。证据公开范围由维护者按平台权限控制，账号和敏感数据留在仓库之外。

`g0-7` 的报告同样包含这三行，另对六个已合并实验各写一行 `Experiment evidence: <id> <sha256>`。SHA-256 来自 `main` 上对应报告的原始 Git blob，例如 `git show 'origin/main:docs/verification/gate0/g0-1.md' | sha256sum`。检查会核对每项报告、合入其完成状态的 PR、汇总摘要，以及合入前由作者之外的审查者对汇总 PR 最终 head 提交的 GitHub APPROVED。汇总合入 `main` 后才能启动下游。独立 Reviewer 需查看原始材料并在实机抽测，机器核对用于确认审批及证据对应的提交。

## 变更规模

生产增删之和最多 400 行，最多 10 个文件，包含工程控制脚本、配置和可执行探针。Markdown 文档与 `tests/` 验证材料不计入生产数；所有变更仍按任务所有权审查。大型 GIL/录像留在可复核的证据存储。实际改动超限时先更新依赖和所有权，将交付改成可独立验收的 PR。
