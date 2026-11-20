---
id: m1-4
title: "合法动作驱动 AI"
status: To Do
assignee: []
dependencies: ["m0-7"]
milestone: M1
type: feature
priority: high
modified_files: ["src/rules/bot.lua", "tests/rules/bot_test.lua"]
---

## 合法动作驱动 AI

生产改动预算（变更行 / 文件） 240 / 1

## Acceptance criteria

- [ ] 启发式选择只读其座位的公开和私有视图及合法动作，用可注入随机流，有明确行动预算。覆盖默认选择和无动作可走时的收敛。

## Verification evidence

- 固定种子及四种动作选择样例，非法动作与超预算为零。
