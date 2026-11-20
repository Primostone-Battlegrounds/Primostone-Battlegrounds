# Backlog

本入口与 [backlog/tasks](backlog/tasks/) 组成唯一工作权威，状态、依赖、分配和独占文件仅以 GitHub `develop` 的已合入任务文件为准。[OpenHarness Backlog 契约](https://github.com/FurinyaDev/OpenHarness/blob/aebb0c2255a5df275491009285c1a23d03f90771/docs/backlog-profile.md) · [GitFlow 与 AI 评审](docs/architecture/gitflow.md)

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

1. 按 [README](README.md) 安装并读取 `entry`。确认 Bootstrap 已经独立 AI 复核、问题解决且实际合入，main/develop 保护有效，迁移和三条 PR 路径验证完成。
2. 读取 `origin/develop` 对应任务。`Blocked` 表示环境、能力或证据缺口；解除条件满足后由独立维护 PR 修改状态并映射真实执行者。`To Do` 或 `In Progress` 仍须全部传递依赖真实合入为 Done；未分配任务不可认领。
3. 工作前核对全部远端分支、打开的 PR、合入记录：`git ls-remote --heads origin 'refs/heads/task/*'`、`gh pr list --state open --json number,headRefName,baseRefName,author,url`。同任务分支已存在时必须协调续接或移交。
4. 依赖合入且无独占路径冲突后，从已验证的 develop 提交用 GitHub POST 原子创建 `refs/heads/task/<id>`；失败就重新同步。再次检查目标漂移、全部 PR 与路径占用后，用独立 worktree 跟踪该引用，并运行 `workspace --task <id> --change <short-name> --bind`。每棵工作树仅一个 Session 写入。OpenHarness 不提供远端租约；新增冲突先走依赖调整 PR。
5. 任务 PR 只回 develop，正文有且仅有一行 `Work-Item: <id>`，提交同一任务的完成状态和真实证据。只有 develop 的实际 merge SHA 才算 Done。另一个 subagent / AI 审查最终 head，记录协议见 GitFlow；通过 CI 后按 OpenHarness `integrate --pr N`，之后 `release`（此命令释放工作树，不等于发布版本）。计划、依赖、分配调整走独立维护 PR。

认领时把 `TASK_ID`、`CHANGE_NAME` 和 `TASK_WORKTREE` 设为已验证的任务 ID、短名和当前 Session 的独立路径，在仓库根目录执行。

```sh
git fetch --prune origin
gh api --method POST repos/Primostone-Battlegrounds/Primostone-Battlegrounds/git/refs -f "ref=refs/heads/task/${TASK_ID}" -f "sha=${VERIFIED_DEVELOP_SHA}"
```

GitHub POST 成功才获得认领权。引用已存在或请求失败时重新同步并选择任务。成功并完成并发复查后创建本地工作树。

```sh
git fetch origin "refs/heads/task/${TASK_ID}:refs/remotes/origin/task/${TASK_ID}"
git worktree add --track -b "task/${TASK_ID}" "${TASK_WORKTREE}" "origin/task/${TASK_ID}"
cd "${TASK_WORKTREE}"
python3 -m openharness --repo . workspace --task "${TASK_ID}" --change "${CHANGE_NAME}" --bind
```

OpenHarness 将工作树绑定到整个 Backlog 摘要。目标变更后，在最新 origin/develop 核对任务仍归当前执行者、依赖完成且范围未变；提交当前工作，将最新 develop merge 进任务分支并解决冲突。干净工作树用原 ID 和 change 名重新 `workspace --bind`，运行 preflight 和候选验证。推送原分支，重新获得最新 head 的 AI 评审与真实 CI。已移交或完成时由维护者协调。

## Gate 0 证据与解除条件

目前六项实验以及 `G0-VERIFY` 均为 `Blocked`。先安排创作账号、区服、版本匹配的原神客户端与编辑器、PC 和移动真机以及四人私有试玩环境。Worker 只构建任务所需探针；按任务正文定量验收。一项必要实验无法实测或失败就保持 `Blocked`，记录缺失环境或能力和复测步骤。

每个实验证据文件 `docs/verification/gate0/<id>.md` 至少记录日期、区服、编辑器和游戏构建号、设备/系统、探针提交、GIL SHA-256、准备步骤、阈值、每项观测结果、失败样本及复现步骤。通过后填写独立的三行 `Result: PASS`、`Platform evidence: https://…` 和 `Verification pull request: https://github.com/Primostone-Battlegrounds/Primostone-Battlegrounds/pull/<number>`。原始日志、导出摘要及录屏需可供复核。证据公开范围由维护者按平台权限控制，账号和敏感数据留在仓库之外。

`g0-7` 的报告同样包含这三行，另对六个已合并实验各写一行 `Experiment evidence: <id> <sha256>`。SHA-256 来自 develop 上对应报告的原始 Git blob，例如 `git show 'origin/develop:docs/verification/gate0/g0-1.md' | sha256sum`。检查核对每项实验及汇总的实际任务 PR 合并记录和最终 head 的独立 AI 评审。AI 必须审阅原始实机材料；实机操作和抽测由有环境的操作者执行，模型输出不能替代观测。汇总经首次 `release/0.0.1` 实际进入 main，且报告摘要一致后，才允许启动 M0–M2。

## 变更规模

生产增删之和最多 400 行，最多 10 个文件，包含工程控制脚本、配置和可执行探针。Markdown 文档与 `tests/` 验证材料不计入生产数；所有变更仍按任务所有权审查。大型 GIL/录像留在可复核的证据存储。实际改动超限时先更新依赖和所有权，将交付改成可独立验收的 PR。
