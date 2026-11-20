# GitFlow、独立 AI 评审与发布

## 分支与授权

| 分支 | 起点、用途与合入方向 |
| --- | --- |
| main | 默认分支；仅接 release/X.Y.Z 与已发布版本的 hotfix/ID。 |
| develop | 日常集成；唯一 Backlog、状态、分配及任务授权来源。 |
| task/ID | 项目的 feature 分支；从已验证的 develop 精确 SHA 原子认领，任务 PR 回 develop。 |
| release/X.Y.Z | 从验收通过的 develop 精确候选切出；冻结范围，发布 PR 回 main。修正通过 chore/release-fix-ID → release/X.Y.Z PR 审查。 |
| hotfix/ID | 从已发布的 main 切出，PR 回 main；发布兼容补丁后 main → develop 同步。 |

main/develop 的有效规则要求 PR、线程解决、跟上目标、GitHub Actions App **15368** 的 `Architecture checks`。仅 merge commit，禁止直推、强推、删除，绕过为空。release 分支创建时需套用相同规则后才接修正 PR。合并前回读规则和 PR 当前 head/base。

任务认领前检查 develop 上全部传递依赖的真实任务 PR 合并 SHA、分配、独占文件和远端全部分支/打开 PR。对已验证 SHA 执行：

```sh
gh api --method POST repos/Primostone-Battlegrounds/Primostone-Battlegrounds/git/refs -f "ref=refs/heads/task/${TASK_ID}" -f "sha=${VERIFIED_DEVELOP_SHA}"
```

POST 引用已存在即停止，不覆盖。成功后再次核对 develop 漂移及路径占用，独立 worktree 绑定原分支 `workspace --task ID --change NAME --bind`。PR 只有一行 `Work-Item: ID`。400 行生产增删 / 10 个生产文件预算适用于每个任务、维护和修正 PR；发布与同步核验完整来源，不能拿它们承载未审查任务。

## 独立评审协议

本项目的独立性是**实现会话之外的 subagent / AI**，不是另一个 GitHub 账号。主会话提供精确 head、base、需求和改动，评审者自行读差异、检查证据与测试，返回发现及验证。所有发现处理后复核最终 head。有平台操作的任务仍须操作者提供真实设备材料。

账号可将实际 AI 结果作为 GitHub **COMMENT review** 留档。正文协议如下；标识必须对应真实不同会话，不能由实现者自行宣布独立通过：

```text
AI-Review: PASS
Reviewed-Head: <40 位 PR head SHA>
Reviewer-Agent: subagent:<实际任务或会话 ID>
Implementer-Agent: opencode:<实现会话 ID>

## Findings
发现、解决状态及剩余限制；没有遗留项时明确记录。
## Verification
实际读过的范围、执行命令和结果，及未能实测的内容。
```

CI 读取有仓库写权限账号提交的最新 head 评审记录，核对 SHA、不同会话标识、PASS 和报告段落；后续 FAIL 或新推送使通过失效。账号信任通过 repository permission API 核对，不依赖对调用者可见性不同的组织 membership 字段。提交评审后，编排者必须用 `gh run rerun <当前 head 的原始 pull_request run ID>` 重跑真实 PR 检查；不得用 review 事件的同名绿灯代替，因为固定版 OpenHarness 只接受 `pull_request` 来源。重新评审后也执行此步骤。机器验证记录绑定，AI 会话真实性属于维护者信任边界；不要求原生 GitHub approving review，也不把模板本身当作评审。提醒如有需要用原生 review request，个人 Watch 由账号持有人选择。

## 发布契约与 SemVer

沿用 PR #2 的 [发布路线](release-roadmap.md)：0.0.1 为 Gate 0；0.1.0 核心；0.2.0 垂直切片；0.3.0 单人 MVP；0.4.0 四人试玩。0.x 次版本承载功能/实验契约变化，同次版本补丁仅兼容修复；1.x 后破坏/功能/修复分别升主/次/补丁。hotfix 必须对最新已发布稳定版升一个 PATCH。

release 分支的 `source` 必须是已验收且实际位于 develop 历史的精确 SHA。经过修正 PR 后确定 `candidate`，对该提交验收并保存真实产物，再单独提交 `docs/releases/X.Y.Z.json`。candidate 到发布 head 只能增加该清单。清单字段：

```json
{
  "version": "0.0.1",
  "source": "<40 位 develop SHA>",
  "candidate": "<40 位已验收产物 SHA>",
  "task_prs": [11, 12],
  "fix_prs": [],
  "artifacts": [{"name": "probe.gil", "sha256": "<64 位真实摘要>", "url": "https://<可复核产物>"}],
  "validation_evidence": "https://<精确候选的验收记录>"
}
```

示例为结构说明，不是有效证据。CI 回查 source 自上次 main 以来的 develop 首父提交，每项必须是已独立 AI 评审的实际 PR 合并；task_prs 精确覆盖其中全部任务 PR，修正必须来自该 release 分支已审查合入的 PR。修正与 hotfix 冻结 Backlog、任务授权和 CI 控制文件；不得完成或认领任务。任何非 Gate 0 修正同样要求首次 Gate 0 已进入 main。发布 PR 绑定精确候选、真实材料 URL 和 SHA-256；评审者复算产物摘要、核对设备/客户端/编辑器版本、兼容矩阵和回滚演练。CI 不把 URL 格式检查冒充产物验收。

发布 PR 合并之后，维护者回读实际 main merge SHA；确认该 SHA 的内容与验收 candidate 仅差清单，检查最终 CI，才创建不可变 `vX.Y.Z` 标签并发布，将清单、摘要、任务/修正 PR、候选和 main merge SHA 放入 GitHub Release。使用 `gh api .../git/refs` 原子创建标签，`gh release create vX.Y.Z --verify-tag --target <MAIN_MERGE_SHA> ...`；标签已存在时先核对，不移动标签。发布动作不能由普通 develop 合并触发。

随后发起 **main → develop** 同步 PR，同样经过 AI 评审和真实 CI，将全部发布修正与记录同步回来。hotfix 从已发布 main 切出，`Release-Version: X.Y.Z` 指定补丁版，清单 source 等于 main 基线；不得混入任务授权。补丁发布后也走 main → develop。下一次发布之前先完成同步。

## Gate 0 与迁移激活

六项实验及 g0-7 保持 Blocked，直到真实材料和独立复核满足原任务条件。实验及汇总任务先合 develop；首次 release/0.0.1 把汇总成果实际送入 main。M0–M2 的 CI 核对 g0-7 任务合并、最终 head 的独立 AI 评审、六项报告摘要和 main 实际包含同一证据。模拟、AI 报告、CI 绿灯都不能替代六项实机 PASS。

一次性迁移例外仅有 #3 `chore/gitflow-migration` 维护 PR（控制与文档，不得完成任务）和原目标 main 的 PR #2（保留原始规划提交祖先）。例外绑定不可重复使用的 PR 编号，合并后失效。PR #2 合入后必须同步回 develop，合并 Backlog 时保留 develop 授权模型及 AI 评审协议；不以机械覆盖覆盖任一侧的规划。

激活顺序：独立 AI 复核 Bootstrap 与迁移 → 真实 CI 与保护回读 → 维护 PR 合 main → main → develop 同步（任务目标设置生效）→ 实际任务/发布路径的拒绝及合法候选检查 → 才向 Worker 派发满足状态、分配、依赖和环境条件的任务。实机环境未齐时保留 Blocked。历史 Bootstrap 没有独立 GitHub APPROVED 不是门槛；需补的是实际 AI 复核及发现闭环。
