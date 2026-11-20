---
id: m1-11
title: "单人完整 MVP 试玩"
status: To Do
assignee: []
dependencies: ["m1-7", "m1-9", "m1-10"]
milestone: M1
type: verification
priority: high
modified_files: ["src/platform/session.lua", "tests/platform/mvp_test.lua", "docs/verification/m1-mvp.md"]
---

## 单人完整 MVP 试玩

生产改动预算（变更行 / 文件） 210 / 1

## Acceptance criteria

- [ ] 把已验收子系统接入单人平台会话。真人可完成一局对七个 AI 的完整流程，能查看单位与英雄效果并复盘结算。
- [ ] 固定种子批量跑通遗留异常，真机验证完整三局含退出后的恢复。

## Verification evidence

- 1+7 真人试玩、三局录像与回放、批跑种子和 GIL SHA。
