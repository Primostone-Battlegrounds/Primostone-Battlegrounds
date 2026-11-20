# Bootstrap 验证记录

- 目标仓库基础提交为 `911a10c5d847f19815c31eac008669c3ee338289`（`main`）。本次 PR 范围为工程入口、研究、Backlog 及验收检查。
- OpenHarness `aebb0c2255a5df275491009285c1a23d03f90771` 上游执行 `python -m unittest discover -s tests`，170 通过，2 跳过；使用同一 SHA 的安装器生成 cooperative 配置与入口。
- AutoTavern `1c2086a997afde46d68c6c5992cab194ddcfce88`，Rust 1.98.1。运行 `cargo test --locked -p taverngym --test games --test mechanics --test persistence --test combat_analytics --test recruit_batches --test patch_3702`，六个套件共 466 个测试通过，0 失败，0 跳过。这些是参考实现的测试结果。
- Gate 0 为 `Blocked`。本环境没有目标 PC/手机上的原神试玩、配套创作账号或四端联机条件。导入、运行、同步、恢复与性能等待真机实录。
- 查询 `main` 的 GitHub 有效规则返回空列表。初次提交期间创建分支与 fork 返回 HTTP 403。账号的仓库角色与 GitHub App 安装范围共同决定连接器的写入权限。GitHub Actions 与有效 Ruleset 以 PR 和仓库的实时状态为准。
- 本地项目验收通过。OpenHarness 的 `verify` 在临时合并工作树运行同一 Backlog 校验，工作树干净且结果绑定本地候选。30 个任务包含 41 条依赖、76 条不同的独占路径，图无环，重叠路径均有先后依赖，23 项下游任务全部传递依赖 G0-VERIFY。
- 最大单任务估算为 350 行 / 3 个生产文件。Bootstrap 相对目标基础提交的实际规模为 359 行 / 4 个生产文件，40 个改动路径主要是任务及文档。`git diff --check` 与 `actionlint 1.7.7` 通过。
- 用临时 Git 仓库执行 19 个正反例。覆盖 PR head 不匹配、依赖缺失和环、路径冲突、跳过 Gate、缺失及错绑证据、提前下游变更、超出 400 行或 10 文件、本人审批、过时审批、Gate 未合入、错误执行者和分支。Gate 通过场景使用模拟的 GitHub API 响应，仅验证判定逻辑。
- 独立架构复核后补强 Gate 0 的 PASS 记录、实验报告摘要与合入 PR 的对应关系、审批时点，以及任务 PR 保留本任务记录的检查。并行任务绑定过期后的续接流程写入 Backlog。临时 Git 验证覆盖明确 FAIL、漏填摘要、实验 PR 未合入、合入后审批和任务自删等新增反例。
