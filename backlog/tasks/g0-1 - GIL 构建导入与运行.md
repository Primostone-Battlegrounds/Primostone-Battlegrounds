---
id: g0-1
title: "GIL 构建导入与运行"
status: Blocked
assignee: []
dependencies: []
milestone: G0
type: experiment
priority: high
modified_files: ["experiments/gate0/build/probe.lua", "experiments/gate0/build/recipe.md", "docs/verification/gate0/g0-1.md"]
---

## GIL 构建导入与运行

生产改动预算（变更行 / 文件） 70 / 1

**解除本任务阻塞所需条件**　具备目标区服的创作权限、目标 PC 原神客户端和匹配版本的编辑器及千星沙箱。

## Acceptance criteria

- [ ] 用一个计数器和一个文本控件制作最小工程。记录从受版本控制的脚本、节点图手动装配及映射步骤。用官方工具导出 .gil，再导入到全新槽位，进入原神实际试玩并确认交互。
- [ ] 由另一位操作者在干净槽位按说明重建并复现实验。记录版本、区服、手工步骤、导出 SHA-256、发布或受邀试玩所需权限及同版本回滚方法。
- [ ] 成功标准为两次构建、两次导入试玩均显示正确标识与递增计数，重启后仍可重新导入。脚本映射或来源无法复现则继续 Blocked。

## Verification evidence

- 在 `docs/verification/gate0/g0-1.md` 留档并索引可复查的原始证据。
- 留导入前后的录像、编辑器及原神版本截图、两次导出摘要和可访问的原始产物索引。
