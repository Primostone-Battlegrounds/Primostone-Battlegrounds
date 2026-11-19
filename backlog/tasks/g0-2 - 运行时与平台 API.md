---
id: g0-2
title: "运行时与平台 API"
status: Blocked
assignee: []
dependencies: ["g0-1"]
milestone: G0
type: experiment
priority: high
modified_files: ["experiments/gate0/runtime/probe.lua", "experiments/gate0/runtime/recipe.md", "docs/verification/gate0/g0-2.md"]
---

## 运行时与平台 API

生产改动预算（变更行 / 文件） 130 / 1

**解除本任务阻塞所需条件**　同版本实机、调试日志访问权限、可重建的 GIL 探针关卡。

## Acceptance criteria

- [ ] 分客户端脚本和节点图实测数值范围与回绕、表遍历、模块映射、调用栈、回调生命周期、时钟与定时、日志、UI 事件和可用信号。逐项记录 API 或节点名称、运行侧及失败行为。
- [ ] 用阶梯负载测量脚本大小、单次回调与事件吞吐、内存或可观察的替代指标、控件或图资源上限。每阶运行三次，记录第一个失败与稳定上限。不可直接测量的指标写明替代测法。
- [ ] 本地 UI 路径和权威节点路径均需证实可执行。对必需的受限能力，以实机验证过的等价路径闭环。缺失必需路径时维持 Blocked。

## Verification evidence

- 在 `docs/verification/gate0/g0-2.md` 留档并索引可复查的原始证据。
- 附 API 能力矩阵、各阶原始日志、失败错误码和保守资源预算。
