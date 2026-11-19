---
id: g0-7
title: "G0-VERIFY"
status: Blocked
assignee: []
dependencies: ["g0-1", "g0-2", "g0-3", "g0-4", "g0-5", "g0-6"]
milestone: G0
type: verification
priority: high
modified_files: ["docs/verification/gate0/g0-7.md"]
---

## G0-VERIFY

生产改动预算（变更行 / 文件） 0 / 0

**解除本任务阻塞所需条件**　六项实机实验各自具有可复查 PASS 证据并经各自 PR 合入 main，且可安排独立复核。

## Acceptance criteria

- [ ] 在 main 上逐个核对六个任务及其证据的版本、提交、GIL 摘要和验收矩阵。不同版本或未测场景保持 Blocked，改版后复测受影响项。
- [ ] 汇总选定运行路径、权威节点及同步粒度、保存范围、PC 和移动端预算、最小输入与重放协议。独立 Reviewer 复看原始证据并按干净导入说明抽测。因此节点无任何平台必需项为失败、未知或未测。
- [ ] 由独立 Reviewer 在当前 PR head 上给出 GitHub APPROVED，解决审查问题后把 `g0-7` 改为 Done 的 PR 实际合入 main。以合并提交及 main 当前任务内容解锁。

## Verification evidence

- 在 `docs/verification/gate0/g0-7.md` 留档并索引可复查的原始证据。
- 汇总文件列六个已合并实验 PR、证据 SHA 或校验和、采样版本与可访问链接。
- 独立审批和最终 merge SHA 由 GitHub PR 及 main 历史提供。
