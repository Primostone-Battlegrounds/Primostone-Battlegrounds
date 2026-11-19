---
id: g0-6
title: "PC 与移动端预算和交互"
status: Blocked
assignee: []
dependencies: ["g0-2"]
milestone: G0
type: experiment
priority: high
modified_files: ["experiments/gate0/perf/probe.lua", "experiments/gate0/perf/recipe.md", "docs/verification/gate0/g0-6.md"]
---

## PC 与移动端预算和交互

生产改动预算（变更行 / 文件） 170 / 1

**解除本任务阻塞所需条件**　目标 PC、拟支持的低档移动设备和真实客户端帧时间及交互观察手段。

## Acceptance criteria

- [ ] 建立空关卡对照，用 8 座、每座 7 假实体和 50 条目录记录合成压力。测正常负载和 2 倍事件压力，各设备每档三次、每次 10 分钟，记录耗时、峰值资源、图或脚本执行限制。
- [ ] 暂用项目验收线为默认画质 PC p95 帧时间 ≤ 16.7 ms、低档移动 ≤ 33.4 ms，输入到反馈 p95 ≤ 150 ms，结算暂停 ≤ 250 ms，无脚本限额、崩溃及持续内存增长。2 倍压力无挂起且可恢复，参数调整需在复核前明示理由并重新实测。
- [ ] 真机验证选择、买卖占位卡、触摸排序、取消及确认，覆盖触控冲突、安全区和较小屏幕。记录最小内存和控件预算或可核验代理量。

## Verification evidence

- 在 `docs/verification/gate0/g0-6.md` 留档并索引可复查的原始证据。
- 附设备型号、系统与画质、空关卡及负载 CSV、采样方法及 UI 录屏。
