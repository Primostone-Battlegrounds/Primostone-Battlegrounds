# 酒馆战棋社区实现调研

公开仓库能核对社区如何建模招募、战斗、重放和信息展示。完整规则参考选用 AutoTavern 的固定版本；不同版本只比较对齐过的机械案例。以下来源提供实现或观测证据，项目自己的行为由 [规则与接口基线](product-baseline.md) 定义。调研以可分发的社区代码、文档和公开测试为基础。

## 源码范围和实测结果

| 来源与固定版本 | 读到的实现 | 证据与用于何处 |
| --- | --- | --- |
| AutoTavern TavernGym 1.1.0，客户端 37.0.2.256589，MIT 代码 | `flow.rs` 驱动各席选领队、招募屏障、配对和结算。`actions.rs` 输出精确合法动作。`recruit.rs` 按剩余份数抽取。`combat.rs` 从战团副本产生战斗事件，`engine.rs` 保存 RNG 和状态。 | 首选完整对局结构。用其池守恒、合法动作、单轮战斗与快照方法设计 m0-3/4/6/8/9、m1-4/10 的对照。客户端卡表与素材属于独立内容权利。 [版本](https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/docs/PATCH_37.0.2.md) · [架构](https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/docs/ARCHITECTURE.md) · [许可说明](https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/NOTICE) |
| Stone Ground Hearth Battles，Apache-2.0，2021 快照 | Python 把动作的校验与应用放在动作对象中。死亡及对应触发分队列处理，双方队列非空时可注入随机选择。重放从种子、排序后的席位和原始动作恢复回合。 | 四个选定套件实跑 373 通过。补充 m0-4 命令验证、m0-5 同批顺序、m0-9 回放输入，以及 m1-4 合法 AI。旧卡表与队列仲裁结果限于该快照。 [动作](https://github.com/JDBumgardner/stone_ground_hearth_battles/blob/05dba5d0c2c58b1c2f6a6011f5896e8d1b8f3617/hearthstone/simulator/agent/actions.py) · [队列](https://github.com/JDBumgardner/stone_ground_hearth_battles/blob/05dba5d0c2c58b1c2f6a6011f5896e8d1b8f3617/hearthstone/simulator/core/combat_event_queue.py) · [重放](https://github.com/JDBumgardner/stone_ground_hearth_battles/blob/05dba5d0c2c58b1c2f6a6011f5896e8d1b8f3617/hearthstone/simulator/replay/replay.py) |
| HSBRSIM 的 `hsbg-engine`，AutoTavern fork，Rust 子目录 MIT | 增加回合末部分场景镜像与稳定实体 ID 重映射。`mirror_snapshot.rs` 检查非法输入保持旧状态、混合池份额守恒、引用成组映射、单次推进。入口 README 仍写 37.0.0.255790，该提交的引擎数据 `meta` 与 fork 升级记录为 37.0.2.256589。 | 与 AutoTavern 同源。选定镜像夹具实跑 5 通过，覆盖整体验证后提交。部分注入明确有未知池差量，正式恢复必须验全量池守恒。对应 m0-8、m1-19、m2-7。 [fork 说明](https://github.com/Gallo13th/HSBRSIM/blob/328d0e0959055a6e80e25f92aad972981259b10c/rust/FORK.md) · [镜像夹具](https://github.com/Gallo13th/HSBRSIM/blob/328d0e0959055a6e80e25f92aad972981259b10c/rust/crates/hsbg-engine/tests/mirror_snapshot.rs) |
| twanvl C++ 战斗模拟器，MIT，2020 快照 | `battle.cpp` 实现战团、攻击轮换、双方伤害、批量死亡和光环重算；命令行接受文本战团，按多次采样输出分布。 | 串行构建和 `examples/run1.txt` 退出码 0，带出 8 个回合样本。只覆盖战斗，适合 m0-5/6 的小盘面用例。该项目自行标明触发顺序边界。 [战斗代码](https://github.com/twanvl/hearthstone-battlegrounds-simulator/blob/b02bc5ce8934c1a5aa1e39e04e4ac78d642fbb65/src/battle.cpp) · [已知限制](https://github.com/twanvl/hearthstone-battlegrounds-simulator/blob/b02bc5ce8934c1a5aa1e39e04e4ac78d642fbb65/README.md) |
| HearthSim `hslog` 1.20.0，MIT | `Power.log` 到实体及事件的解析层。固定输入测试覆盖缺失、重复时间戳、未知实体或操作和选项异常。 | `tests/test_parser.py` 实跑 32 通过。m1-14/18 借鉴不完整事件的显示行为，m2-7 检查乱序和负载形状。观察日志只能看到已经暴露的数据。 [解析器](https://github.com/HearthSim/hslog/blob/015c0dec197779c90cd3131ecda2c990292342b6/hslog/parser.py) · [测试](https://github.com/HearthSim/hslog/blob/015c0dec197779c90cd3131ecda2c990292342b6/tests/test_parser.py) |
| Hearthstone Deck Tracker v1.59.8 的 BobsBuddy 接线 | C# 源捕获战团快照、把可见实体转为模拟输入、用时限及样本数解释部分结果。项目引用独立 `BobsBuddy.dll`。 | 可见源码证明集成路径，不能从接线推断完整模拟器的实现、许可或实际服务端规则。用来检查 m1-14 显示中止及 m1-20 诊断的边界。 [调用与显示](https://github.com/HearthSim/Hearthstone-Deck-Tracker/blob/2698623dc0e91491671a614ae176f9db68831aa7/Hearthstone%20Deck%20Tracker/BobsBuddy/BobsBuddyInvoker.cs) · [依赖引用](https://github.com/HearthSim/Hearthstone-Deck-Tracker/blob/2698623dc0e91491671a614ae176f9db68831aa7/Hearthstone%20Deck%20Tracker/Hearthstone%20Deck%20Tracker.csproj) |
| Bob’s Ledger，MIT | `replay_review.py` 以阶段夹具重建买入决策，`live_replay.py` 从已结束记录走实际渲染数据，比较同阶段回放帧的精确性。 | 用于 m1-14/18 的“同输入同画面”和阶段展示测试。该工具只消费外部日志，备份或分享行为不进入项目范围。 [阶段重建](https://github.com/mharrell/bobs-ledger/blob/4026c44c3a72ac2062b4fce1ad761e69c65b098b/app/replay_review.py) · [帧验证入口](https://github.com/mharrell/bobs-ledger/blob/4026c44c3a72ac2062b4fce1ad761e69c65b098b/app/live_replay.py) |

### 复现命令

| 检查 | 本轮结果 |
| --- | --- |
| Stone Ground，Python 3.12.14，安装 `pytest autoslot boltons six hearthstone`，运行 `python -m pytest -q tests/test_combat_event_queue.py tests/test_combat.py tests/test_gameplay.py tests/test_tavern.py` | 373 通过，1 条旧异步接口弃用警告。 |
| twanvl，`git submodule update --init` 后 `make`、`./hsbg examples/run1.txt` | 串行构建与样例通过。首次并行 make 在生成 `enums.hpp` 时发生编译顺序问题。 |
| hslog，Python 3.12.14，安装 `pytest 'setuptools<81'` 并 `pip install -e .`，运行 `python -m pytest -q tests/test_parser.py` | 32 通过。测试程序取用公开日志夹具，实际解析样本提交为 `a8cb1ba24f0d275d653a7d987d2d9818fdc07302`。 |
| HSBRSIM，在 `rust/` 用 Rust 1.98.1 运行 `cargo test --locked -p hsbg-engine --test mirror_snapshot` | 5 通过。 |
| AutoTavern，Rust 1.98.1，`cargo test --locked -p taverngym --test games --test mechanics --test persistence --test combat_analytics --test recruit_batches --test patch_3702` | 本轮重跑六个套件 466 通过，与 Bootstrap 记录一致。 [Bootstrap 记录](../verification/bootstrap.md) |

## 转成 Primostone 的测试

| 原则 | 计划中的受验收行为 | 任务 |
| --- | --- | --- |
| 共享池在事务中提交 | 实例在商店、手牌、战团、合成和淘汰流转；生成物持有零份。两席抢最后一份时，只有一个成功。未付款和重复动作不改账本或随机游标。 | m0-3, m0-4, m1-6 |
| 触发顺序明确 | 社区实现对跨侧队列、起手和死亡结算存在版本差异。项目用固定优先级、候选单位、输入与事件轨迹验证同批互伤、相邻传播和上限。以注入同一选择序列比较共通用例。 | m0-5, m0-6, m1-1 |
| 复现与显示可独立验证 | 规则夹具保存开始状态、随机、命令和输出。播放只接受确认事件。续跑状态、播放终态和跳过终态分别核对，日志缺失由播放器明确处理。 | m0-8, m0-9, m1-14, m1-18, m1-19 |
| 权威跨端不靠观察日志 | 主节点重算合法动作与版本，发送白名单投影。覆盖异常座位、重发、私有字段泄漏、未知格式和重连。证据来自平台探针、真实四端和可复查原始记录。 | g0-2, g0-5, m2-1 至 m2-7 |

本项目交付原创代码、目录、文案、插画和音效。外部仓库许可、第三方资产权利和千星奇域获准资源分别记录。任何社区测试通过均只证明该参考项目的已执行样本。Gate 0 以目标区服、设备及客户端中的实测结果为准。
