# Backlog

本入口与 [backlog/tasks](backlog/tasks/) 组成唯一工作权威，状态和依赖以 GitHub `main` 的任务文件为准。[OpenHarness Backlog 契约](https://github.com/FurinyaDev/OpenHarness/blob/aebb0c2255a5df275491009285c1a23d03f90771/docs/backlog-profile.md) · [Backlog.md 1.53.0 参考解析器](https://github.com/MrLesk/Backlog.md/blob/fd20f71493fb4eda44b021aa89f257956f17fb71/src/markdown/parser.ts)

| 阶段 | 可交付结果 |
| --- | --- |
| Gate 0 | [导入和试玩](backlog/tasks/g0-1%20-%20GIL%20构建导入与运行.md) → [运行时](backlog/tasks/g0-2%20-%20运行时与平台%20API.md) → [重放](backlog/tasks/g0-3%20-%20确定性与战斗重放.md)、[恢复](backlog/tasks/g0-4%20-%20状态编码与恢复.md)、[四人](backlog/tasks/g0-5%20-%20四人同步与失败恢复.md)、[性能](backlog/tasks/g0-6%20-%20PC%20与移动端预算和交互.md) → [G0-VERIFY](backlog/tasks/g0-7%20-%20G0-VERIFY.md) |
| M0 | 纯 Lua 状态、随机、经济、招募、战斗、对局闭环和快照 |
| M1 | 可玩垂直切片先合入，再扩到 1 真人 + 7 AI、40–50 个原创随从的单人 MVP |
| M2 | 按实测平台路径实现四人联机、故障恢复以及 PC / 移动端验收 |

OpenHarness 规定原生 ID 为字母前缀加数字。`g0-7` 是 `G0-VERIFY` 的任务 ID，GitHub PR 使用 `Work-Item: g0-7`。模型字段在原生契约中对应如下。

| 项目所需字段 | 唯一存放位置 |
| --- | --- |
| `id`、`milestone`、`type`、`priority` | 任务文件同名前置字段 |
| `depends_on` | `dependencies` |
| `exclusive_files` | `modified_files` 为逐条精确路径，另含任务自己的文件 |
| `acceptance_criteria`、`verification_evidence` | 任务正文的 `Acceptance criteria` 和 `Verification evidence` |

## 从无历史 Session 开始

1. 按 [README](README.md) 安装并读取 `entry`。确认 Bootstrap PR 已经独立审查、问题已解决并实际合入，且 main 原生检查与审批规则生效。
2. 读取 `origin/main` 对应任务。`Blocked` 表示环境、能力或证据缺口；解除条件满足后由维护者的任务编排 PR 修改状态和明确映射执行者。`To Do` 或 `In Progress` 仍须满足全部传递依赖为 Done。初始任务均未分配；有多人并行时由编排 PR 补充真实 GitHub 登录映射，一个任务只配一个执行者。
3. 在工作前观察远端任务分支、打开的 PR、合入记录。使用 `git ls-remote --heads origin 'refs/heads/codex/backlog-*'` 与 `gh pr list --state open --base main --json number,headRefName,author,url`。已有同任务分支或 PR 时，原执行者续接或维护者协调移交。远端分支和 PR 可显示正在进行的工作，不能成为额外完成状态。
4. 对合法任务运行 `python3 -m openharness --repo . workspace --task <id> --change <short-name>`，进入返回的独立工作树。每个工作树只由一个 Session 写入。多个 Session 只能并行执行依赖互不阻塞且无路径冲突的任务。OpenHarness 不提供远端租约。出现未规划的文件重叠时先更新本 Backlog 依赖，等该变更合入再开工。
5. 向目标仓库发出一个任务 PR，正文有且仅有一行 `Work-Item: <id>`，并提供可复查验收证据。完成状态在同一 PR 中提交，其他 Session 只有在确认 `main` 上的结果及实际 merge SHA 后才将其视为 Done。维护者独立审批源码、证据和控制面；已批准后可按 OpenHarness 流程 `integrate --pr N`，之后 `release`。任务分配及控制变更通过独立维护 PR 审查。

## Gate 0 证据与解除条件

目前六项实验以及 `G0-VERIFY` 均为 `Blocked`。先安排创作账号、区服、版本匹配的原神客户端与编辑器、PC 和移动真机以及四人私有试玩环境。Worker 只构建任务所需探针；按任务正文定量验收。一项必要实验无法实测或失败就保持 `Blocked`，记录缺失环境或能力和复测步骤。

每个实验证据文件 `docs/verification/gate0/<id>.md` 至少记录日期、区服、编辑器和游戏构建号、设备/系统、探针提交、GIL SHA-256、准备步骤、阈值、每项观测结果、失败样本及复现步骤。增加独立的一行 `Platform evidence: https://…` 指向可访问的原始日志、导出摘要、录屏或证据索引。证据公开范围由维护者按平台权限控制，不把账号和敏感数据提交到仓库。

`g0-7` 的证据需索引六项已合并记录，并加入 `Verification pull request: https://github.com/Primostone-Battlegrounds/Primostone-Battlegrounds/pull/<number>`。独立 Reviewer 对最终 head 给出 GitHub APPROVED，并在原始材料中核对和抽测。实际 merge commit 必须能从 `main` 到达，且合入后才能启动下游任务。检查会验证合并记录、当前证据与当时一致、作者之外的最终 head 审批和 `main` 上的完成状态。机器核对结构和 GitHub 记录，平台能力通过与否由实际观测和独立复核决定。

## 变更规模

生产增删之和最多 400 行，最多 10 个文件，包含工程控制脚本、配置和可执行探针。Markdown 文档与 `tests/` 验证材料不计入生产数；所有变更仍按任务所有权审查。大型 GIL/录像留在可复核的证据存储。实际改动超限时先更新依赖和所有权，将交付改成可独立验收的 PR。
