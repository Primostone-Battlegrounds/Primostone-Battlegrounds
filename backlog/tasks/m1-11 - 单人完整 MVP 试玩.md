---
id: m1-11
title: "单人完整 MVP 试玩"
status: To Do
assignee: []
dependencies: ["m1-15", "m1-17", "m1-18", "m1-19", "m1-20", "m1-21"]
milestone: M1
type: verification
priority: high
modified_files: ["src/platform/session.lua", "tests/platform/mvp_test.lua", "docs/verification/m1-mvp.md"]
---

## 单人完整 MVP 试玩

生产改动预算（变更行 / 文件） 210 / 1

## Acceptance criteria

- [ ] 把已验收子系统接入单人平台会话。真人可完成一局对七个 AI 的完整流程，能查看单位与领队效果并复盘结算。接入领队技能、教学、反馈和恢复；核对 40–50 个条目的素材覆盖及 100 局固定种子报告。
- [ ] 固定种子批量跑通遗留异常，真机验证完整三局含退出后的恢复。

## Verification evidence

- 1+7 真人试玩，PC 与移动合计三局，覆盖检查点退出恢复、回放、目录清单、批跑种子和 GIL SHA。
