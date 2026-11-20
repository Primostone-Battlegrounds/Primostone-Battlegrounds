# 规则基线与千星奇域差异

## 固定参考

本项目是原创自动战斗游戏。核心特色是元素附着与反应驱动的编队决策。初期只围绕招募与自动战斗；单人目标为一名真人与七名 AI、40–50 种原创随从，四人联机在平台验证后交付。

规则参考为 AutoTavern TavernGym 1.1.0，提交 `1c2086a997afde46d68c6c5992cab194ddcfce88`，对应模拟器所标注的客户端 `37.0.2.256589` 与服务端规则 `37.0.2`。该提交没有单独的 1.1.0 发布标签。`v1.0.0` 标签解析到 `fb61201a557ddd36a411cf44aac51ce4d9b606ce`，是 36.6.3 的历史参考。同一仓库的 TavernBench 标注、样本状态及统计仍对应 36.6.3，保留作历史资料。这里的具体行为均来自同一固定 SHA。 [版本声明][cargo] · [补丁说明][patch] · [项目说明][at-readme]

## 核心流程与机制

| 范围 | 固定版本的可观察行为 | Primostone 采用范围 |
| --- | --- | --- |
| 英雄选择 | `Game::new` 初始化各座位候选及 `Pending::HeroSelect`。默认两选项，具体候选受配置、参赛种族和可用英雄影响。选齐后开启招募。待选项阻止普通动作。 | 采用先选择后招募和合法动作边界。英雄、数值、技能和候选发放为项目配置。 [flow][flow-init] · [actions][actions] |
| 招募阶段 | 淘汰座位跳过。`start_turn_player` 清理限次，补金、减少升级费、处理临时修正、刷新商店、触发回合事件。`end_turn` 拒绝未完成选项，保存战团。最后一名存活玩家结束时才触发战斗。 | M0 保留阶段合法性、操作顺序和提交屏障。回合定时及多端同时提交顺序在 Gate 0 实测后确定。 [flow][flow-turn] |
| 经济与商店 | 初始 3 金，按回合 +1、自然补金上限 10。默认买随从 3、卖出通常 1、刷新 1。冻结逐槽标记，切换整店，下一回合保留冻结槽并处理解冻，普通技能外每回合有按键上限。升级扣金、重置到下一档费用并发出升级事件；商店品阶决定可抽范围。 | 复用补金、合法扣费、返池、刷新、冻结、升级等语义。费用、槽位、次数和档位做项目参数。特殊英雄、法术槽和改价规则按项目范围另定。 [config][config] · [recruit][recruit-turn] · [flow][flow-turn] |
| 公共池 | 商店随从抽取按剩余份数加权。每个实例记所持池份数，满池或额外生成另有分支。商店、手牌、战团、金色及可回收附着物的所有权影响守恒。出售、刷新和淘汰返还所持份数；空池允许抽不到。 | 采用份数账本与单一权威提交，明确生成物来源及跨座争用顺序。各档初始份数是平衡参数。 [recruit][draw] · [state][state] · [invariants][invariants] |
| 三连与金色 | 在合格的战团和手牌普通实例间检查，正在战斗、结束当前回合及部分选项期间暂缓。金色合成移交份数和部分修正，打出才产生高一档发现奖励。通配合成、锁定、挪动增益和金色数值有特殊分支。 | M1 采用三合一、稳定选择和明确成长保留。金色强度及奖励为原创规则，通配例外与 Discover 奖励系本项目范围待决。 [engine][triples] · [mechanics][mech-triple] |
| 战斗与随机目标 | 双方战团复制后，按随从数、商店档位、随机依次选先手。开战钩子先行。双方轮换、左到右选择可攻击单位、在可见存活的嘲讽目标中优先随机，否则在可见存活敌方中随机。对攻伤害同批，之后发出延迟伤害事件并处理死亡。 | 采用战团快照、稳定攻击和目标候选顺序。用独立逻辑给出空候选、上限和异常结果。记录种子、随机游标及事件序号。 [combat][combat] · [targets][targets] |
| 战斗事件 | `Ctx::emit` 先事件所属侧，再另一侧。侧内玩家持久效果、英雄能力等先于战团与手牌监听。死亡整批移除再按阶段执行死亡事件、亡语、复生和复仇等。运行时用深度与攻击上限保护；截断通过诊断字段区分。 | 借鉴明确的阶段及同时性，定义有界事件处理及临时/持久效果边界。平台层只播放结果，保护触发不作为正常平局。参考源码中未公开的服务端先后约定只代表模拟器。 [engine][emit] · [deaths][deaths] · [combat][combat] |
| 结算与淘汰 | 赢家的商店档位加存活随从档位决定伤害，回合和存活人数影响上限。Armor 先于 Health 承伤。回合结束集中处理死亡和名次，招募致死可以即时淘汰。奇数存活用最近淘汰者的最终战团作幽灵，优先回避两个近期对手。并列按生命与护甲、后按席位稳定处理。 | 采用唯一结算、返池与常量化名次策略。单人八席阶段明确幽灵、同分和超时策略。伤害曲线、护甲、上限及重遇窗口由产品规则约定。 [combat][combat] · [flow][flow-result] |
| 英雄技能 | `Script` 定义主动、被动和事件钩子。主动技能检查可用次数、冷却、费用、目标，确认目标前可取消且未收费。 | 采用合法动作加目标确认；先交付少量原创主动与被动技能。 [recruit][hero-power] · [actions][actions] · [script][script] |
| AI 对手 | `SoloEnv` 驱动七个其他座位。可行动时机器人从合法动作中用廉价启发式买卖、升级、上场并处理待选项。随机与游戏种子相连并有行为上限。训练产出的 TavernAgent、权重及训练实现未随项目发布。 | 自写启发式 AI，按座位投影取输入，配置动作预算。同一输入和随机流可复现。 [env][env] · [bot][bot] · [项目说明][at-readme] |

不纳入当前 MVP 的参考系统包括饰品与任务、伙伴、酒馆法术、Dark Gift、Timewarp、Deity、特殊 7 阶系统和参考卡牌目录。TavernGym `ContentMode::Implemented` 仅容纳有实现或仅依赖关键字的项目，`AllVanilla` 将未实现文字效果当白板。内容覆盖以该提交为准。 [内容覆盖][coverage] · [配置][config]

## 元素反应的原创边界

- 候选事件接口由 `ApplyAura`、`ReactionResolved`、伤害和死亡事件组成。附着记录元素、来源及可消耗层数。按显式的交互阶段和实体顺序决定反应，事件写出来源、消耗及结果。攻击与基础互伤共享同一批次，反应何时影响死亡由规则表在 M1 定稿，显示层只读已结算轨迹。
- 第一批使用两个原创组合，分别覆盖消耗型单体增益和有界邻位传播。待定事项包括同元素覆盖或堆叠、同批双方附着优先级、伤害取整、附着是否跨回合、复生与金色修正、传播扇出和深度。先定稿书面规则与反例，人数、数值和反应名称都由项目决定。参考模拟器的种族 Elemental、原神现有即时战斗反应与本项目反应分别属于不同规则域。
- 验收不变量包括附着消耗不低于零、一次有序输入结果唯一、失效目标不再被引用、反应不会无界自触发、临时状态不会跨战斗泄漏、同一结算不会因播放或重连重复发生。用确定性轨迹与 PC、移动真机效果核验。

## 平台差异与验证

官方指南的 7.1 更新列出客户端控件和客户端脚本、API 及客户端与服务器节点图；官方教程提供 `.gil` 导入导出，编辑器菜单包含多人试玩及局内存档。该资料是能力入口，部署版本、区服开放情况、Lua 数值语义、脚本加载方式、权威执行能力、存档作用域及资源上限需要对实际目标重新验证。 [7.1 更新][official-release] · [官方综合指南][official-guide] · [导入导出][official-gil] · [官方编辑器界面][official-editor]

| Rust 参考实现 | 千星奇域缺口与验证 |
| --- | --- |
| Rust 强类型、枚举与 `Vec`，显式 `u64`/`u128` 和整型回绕稳定。全局一条 xoshiro256** 随机流经 SplitMix64 派生，`below` 使用整数乘积采样，池抽取另有加权取模。 | Lua 数字精度、整数溢出、位操作、有序迭代、模块加载和可运行的执行侧由 `g0-2` 证实。`g0-3` 以多端向量锁定项目随机算法和序列化，不照搬 64/128 位实现。 [rng][rng] · [draw][draw] |
| 内存可直接克隆。serde 持久化规则、随机状态及战团，读入检查配置与卡表指纹。部分缓存及临时帧重建。 | 使用明确版本的整数域和排序编码。`g0-4` 验证有权状态的编码、容量、损坏拒绝、恢复范围和重启续跑。`.gil` 是关卡产物。 [engine][game] · [官方导出][official-gil] |
| 环境直接调用 `Game::apply`，规则模拟与 Python 多环境分工，数据可共享进程内读取。 | 先验证客户端输入到权威节点的能力，再定 Lua 共享核心能在哪运行。候选为纯 Lua 规则规范、有限节点适配与客户端投影。若权威执行须移植到节点图，先通过等价探针和资源预算，无法闭环时 Gate 保持阻塞。`g0-5` 验证四人消息顺序、可见性、延迟、重连及权威失败恢复。 [参考架构][at-arch] · [官方项目文档][official-guide] |
| `Ctx` 内存监听、事件递归、批量测试和可选战斗帧；桌面 CPU、进程与真实客户端预算无共同尺度。 | 收集事件吞吐、最大队列、日志/快照尺寸、分批执行、GC 相关停顿代理、PC 和移动帧/输入耗时。`g0-6` 在目标设备验证，避免全对象高频广播与完整帧常驻。 [参考架构][at-arch] |
| Cargo 固定工具链与 Cargo.lock 支撑可复现构建。 | `g0-1` 以官方工具实测脚本映射及 `.gil` 全程；首次兼容手工操作，只有经核验的构建能力才纳入自动化。 [工具链][toolchain] · [导入导出][official-gil] |

### 规则验证策略

- 共通规则用手工最小初态和单步指令，明确对齐容量、价格、钩子开关和目标候选。比较规范化阶段、区域、金币、池份数、目标、事件顺序和伤害。使用脚本化选择或选定可逐步对照的随机游标；同数字种子在不同算法下不能直接当作等价。对冻结、未付款取消、三连回收、攻击后批量死亡及单轮淘汰建立正反例。
- 读过的代表测试包括 `games.rs` 的同种子、快照往返、合法随机动作下不变量；`mechanics.rs` 中的 `buy_sell_gold`、`taunt_is_attacked_first`、`triple_makes_golden_and_reward_on_play`、`pool_is_conserved`、`hero_power_targeting_cancel_does_not_consume_use`、`every_masked_legal_action_applies`、`replay_frames_record_who_attacked_whom`；另读 `persistence.rs`、`recruit_batches.rs`、`combat_analytics.rs` 与 `patch_3702.rs` 对战团隔离、批次行为和版本例外的断言。 [games][games] · [mechanics][mechanics] · [persistence][persistence] · [recruit_batches][batches] · [combat_analytics][analytics] · [patch tests][patch-tests]
- 参考模拟器的未公布规则假设，例如事件跨来源顺序、幽灵策略与并列排名，作为明确标记的固定版本观察。项目需要规则决策时记录选择和重放向量。原创反应用不变量、确定性测试和真实游戏验证。
- 本轮六项平台实验均无实机结果。实际操作者需在原神账号、支持区服、匹配编辑器/客户端、设备和账号数量具备后按 [Backlog](../../BACKLOG.md) 执行。

## 许可证与内容来源

AutoTavern 的软件源代码及相关文档使用 MIT。后续如复制或实质改编，随分发保留原版权及许可文本并记录来源与 SHA。本轮以源码研究为主，没有移植 AutoTavern 代码。`.harness/AGENT.md` 由 OpenHarness 安装器生成，随工程保留其 MIT 通知。 [AutoTavern MIT][license] · [OpenHarness MIT][oh-license]

AutoTavern 的公开许可不替第三方授权。其卡表由游戏客户端数据及叠加规则生成，原始内容包未分发。本项目使用原创代码、随从 ID、文本、数值与占位图，授权前不复制第三方卡表、图像、音效、商标或文本包。进入千星奇域时，只使用创作工具明确授权的素材及范围，素材许可与代码许可分别记录。 [参考内容来源][at-arch] · [千星奇域创作指南][official-guide]

[cargo]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/Cargo.toml
[patch]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/docs/PATCH_37.0.2.md
[at-readme]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/README.md
[at-arch]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/docs/ARCHITECTURE.md
[coverage]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/docs/CONTENT.md
[flow-init]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/flow.rs#L90-L357
[flow-turn]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/flow.rs#L359-L827
[flow-result]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/flow.rs#L936-L1185
[actions]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/actions.rs#L131-L325
[config]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/config.rs#L225-L268
[recruit-turn]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/recruit.rs#L2057-L2151
[draw]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/recruit.rs#L95-L148
[hero-power]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/recruit.rs#L2152-L2221
[state]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/state.rs
[invariants]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/invariants.rs
[triples]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/engine.rs#L3447-L3680
[combat]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/combat.rs
[targets]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/combat.rs#L498-L523
[emit]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/engine.rs#L4526-L4612
[deaths]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/engine.rs#L1969-L2140
[game]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/engine.rs#L72-L170
[script]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/script.rs
[env]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/env.rs
[bot]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/bot.rs
[rng]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/src/rng.rs
[toolchain]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/rust-toolchain.toml
[games]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/tests/games.rs
[mechanics]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/tests/mechanics.rs
[mech-triple]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/tests/mechanics.rs#L210-L244
[persistence]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/tests/persistence.rs
[batches]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/tests/recruit_batches.rs
[analytics]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/tests/combat_analytics.rs
[patch-tests]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/crates/taverngym/tests/patch_3702.rs
[license]: https://github.com/MCG-NJU/AutoTavern/blob/1c2086a997afde46d68c6c5992cab194ddcfce88/LICENSE
[oh-license]: https://github.com/FurinyaDev/OpenHarness/blob/aebb0c2255a5df275491009285c1a23d03f90771/LICENSE
[official-release]: https://act.mihoyo.com/ys/ugc/tutorial/detail/mhiufi00ceh4
[official-guide]: https://act.mihoyo.com/ys/ugc/tutorial/detail/mh1w3z96rpne
[official-gil]: https://act.mihoyo.com/ys/ugc/tutorial/course/detail/mhjuwpiubrh0
[official-editor]: https://act.mihoyo.com/ys/ugc/tutorial/detail/mhn4bsi5lb58
