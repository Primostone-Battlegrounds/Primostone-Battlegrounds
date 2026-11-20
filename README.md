# Primostone: Battlegrounds

> **已终止（2026-11-20）**：Primostone /《原石战场》停止研发、测试、发布和运营，不再投入 Agent 资源。原因包括千星奇域 PvP 玩家匹配规模风险、创作者 Lv3 的存档及天梯权限限制，以及负责人持续投入兴趣不足。本仓库只保留历史资料。后续所有工作指引均已停用。见 [项目终止决定](BACKLOG.md#项目终止决定2026-11-20)。

以元素反应为核心的原创自动战斗项目，目标平台为《原神》千星奇域。本仓库保存项目终止前的工程初始化及平台验证研究。

- [工作入口与 Gate 0](BACKLOG.md)
- [参考规则、原创设计与平台差异](docs/architecture/requirements-and-gaps.md)
- [Bootstrap 验证记录](docs/verification/bootstrap.md)
- [GitFlow、AI 独立评审与发布](docs/architecture/gitflow.md)

## 历史工程入口（已停用）

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
git fetch origin develop main
python3 -m openharness --repo . verify --head HEAD --base origin/develop
python3 tools/check_bootstrap.py --base origin/develop
```

### GitHub 接入与升级

Bootstrap 独立 AI 复核并解决问题后，维护者确认 main/develop 的有效 Ruleset 和三条 PR 路径。规则要求 PR、线程解决、跟上目标、来自 GitHub Actions App `15368` 的真实 `Architecture checks`。独立 subagent / AI 的最终 head 评审由 CI 核对，不要求第二个 GitHub 账号批准。仅允许 merge commit，禁止直推、强推、删除，绕过为空。cooperative 模式自身仅提供客户端保障，CI 维护者仍属信任边界，不宣称无法被恶意控制面修改绕过。[固定版本工作模式](https://github.com/FurinyaDev/OpenHarness/blob/aebb0c2255a5df275491009285c1a23d03f90771/docs/cooperative-workflow.md)

升级时以独立控制 PR 同步本入口和工作流的不可变 SHA，核对上游源码、当前配置兼容性和候选验证。已发布 `v0.3.0` 的自动升级协议仅支持 strict 生成物，此 cooperative 安装由项目 PR 管理，不启用 Renovate 或额外发布任务。[上游升级机制](https://github.com/FurinyaDev/OpenHarness/blob/aebb0c2255a5df275491009285c1a23d03f90771/docs/consumer-upgrades.md)
