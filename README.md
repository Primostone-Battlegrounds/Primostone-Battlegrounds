# Primostone: Battlegrounds

以元素反应为核心的原创自动战斗项目，目标平台为《原神》千星奇域。本仓库目前处于工程初始化与平台验证筹备阶段。

- [工作入口与 Gate 0](BACKLOG.md)
- [参考规则、原创设计与平台差异](docs/architecture/requirements-and-gaps.md)
- [Bootstrap 验证记录](docs/verification/bootstrap.md)

## 工程入口

OpenHarness 历史地址 `CHNISam/OpenHarness` 已迁移到 `FurinyaDev/OpenHarness`。最新发布的不可变版本为 `v0.3.0`（`636947668bbe654dcece449c520cb8df2c3a1bfa`）。本项目采用同一上游已合并但尚未发布的 cooperative 模式，固定主分支提交 `aebb0c2255a5df275491009285c1a23d03f90771`。使用 Python 3.11+、Git 2.38+ 及已认证的 `gh`。[迁移地址](https://github.com/CHNISam/OpenHarness) · [发布记录](https://github.com/FurinyaDev/OpenHarness/releases/tag/v0.3.0) · [固定版本 cooperative 文档](https://github.com/FurinyaDev/OpenHarness/blob/aebb0c2255a5df275491009285c1a23d03f90771/docs/cooperative-workflow.md)

从项目根目录执行。`OPENHARNESS_SRC` 应是项目外的工具目录。

```sh
OPENHARNESS_SRC="$(pwd)/../OpenHarness"
git clone https://github.com/FurinyaDev/OpenHarness.git "$OPENHARNESS_SRC"
git -C "$OPENHARNESS_SRC" checkout --detach aebb0c2255a5df275491009285c1a23d03f90771
export PYTHONPATH="$OPENHARNESS_SRC"
python3 -m openharness --repo . entry
```

检查已提交的本地候选，先更新目标引用。`verify` 在干净独立工作树运行 Backlog 验证。第二条检查按目标差异计算改动规模与 Gate 阻塞。GitHub Check 还读取 PR 身份和合入证据。

```sh
git fetch origin main
python3 -m openharness --repo . verify --head HEAD --base origin/main
python3 tools/check_bootstrap.py --base origin/main
```

### GitHub 接入与升级

Bootstrap PR 独立审查后合入 `main`，维护者在启动 Worker 前确认 `main` 规则生效。GitHub Ruleset 要求 PR、至少一位有权且非作者的审批、过时审批作废、审查线程解决以及 GitHub Actions 的 `Architecture checks` 通过且分支跟上目标。限制直推与绕过，保留 merge commit 方式供 OpenHarness 验证父提交。以第一条实际运行的 Check 核验来源应用，安装前在 GitHub 再观察有效规则。cooperative 模式自身只提供客户端级保障，无需原生 OpenHarness 部署或激活。若仓库的原生保护未启用，Worker 启动继续阻塞。[工作模式](https://github.com/FurinyaDev/OpenHarness/blob/aebb0c2255a5df275491009285c1a23d03f90771/docs/cooperative-workflow.md) · [GitHub Rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)

升级时以独立控制 PR 同步本入口和工作流的不可变 SHA，核对上游源码、当前配置兼容性和候选验证。已发布 `v0.3.0` 的自动升级协议仅支持 strict 生成物，此 cooperative 安装由项目 PR 管理，不启用 Renovate 或额外发布任务。[上游升级机制](https://github.com/FurinyaDev/OpenHarness/blob/aebb0c2255a5df275491009285c1a23d03f90771/docs/consumer-upgrades.md)
