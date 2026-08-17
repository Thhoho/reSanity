# Resanity（散修）

<p align="center"><img src="assets/logo.svg" width="96" alt="散修：锚 + 对勾"/></p>

> 散修，修出你的 Sanity。
>
> **积极的信心，谨慎的动作。**

**一个首先为散户投资研究设计的认知管理 Skill：帮你查证、帮你避坑、帮你记住、帮你复盘。**

它面对的核心场景不是“预测下一只会涨的股票”，而是散户做公司、行业和题材研究时最常遇到的几类问题：消息到底是真是假，技术或政策怎样传到公司收入与现金，市场已经相信了什么，自己的判断要被哪个事实更新。

Resanity 把会改变投资决策的判断拆成四个问题：**观察到什么、可以推出什么、不能推出什么、对决策有什么影响**。模型保留问题定义、证据解释、结论和下一步等研究语义；代码只做 hash、引用、as-of、来源血缘、预算和安装身份等机械检查。

它不是荐股工具，不是行情软件，也不替用户下单、设仓位或承诺收益。它希望做的是：在题材最热时多问一句证据，在结论最顺时找出最弱环节，在验证日到来时记得更新判断，在复盘时说清自己到底错在哪一环。

当前正式代码版本是 **`0.2.1`**；当前方法状态仍是 **`UNBENCHMARKED_CURRENT`**。工程测试、机械收据或有限 A/B 通过不等于研究有效，不证明 Alpha、收益或 PMF。

## 为什么需要散修

市场里不缺信息，缺的是经过边界检查的判断；不缺观点，缺的是能被后续事实更新的观点。

- 刷到“某题材要起飞”的帖子时，先找公告、定期报告和具名客户等原始材料，把官方口径、市场转述和推断分开。
- 看到订单、产能或政策利好时，逐段检查它是否真的走到交付、验收、收入、毛利和回款，而不是把产业相关性直接写成利润。
- 研究过的公司到了财报、验收或政策落地日时，用“更新锚”只复核会改变原判断的事实，不必重做整份研究。
- 复盘亏损或错判时，保留“当时相信什么、基于什么证据、哪个条件后来失效”，避免把教训压成一句情绪。

## 它怎样工作

投资研究首先把主题还原成经济暴露链：

```text
需求或政策
→ 工程/产品可行性
→ 具名客户与合同
→ 交付
→ 验收、起租或计费
→ 收入
→ 毛利
→ 回款与自由现金
```

前一段成立不能自动证明后一段。每条真正承重的判断使用原子主张卡记录观察、推断边界、不能推出的更强结论和决策影响；结论强度服从最弱的承重主张。需要比较路径时再画基准、上行和下行可能性，不为格式强行制造三种对称答案。

最小输出是一句根结论、1–5 张关键主张卡和一个最低成本的下一验证。只有问题需要时才加入价格/预期对照、载体比较、认知锚或正式证据表。

## 直接使用

投资研究是默认目标场景，可以直接问：

```text
这家公司和热门题材之间，是概念映射，还是已经形成可归属的收入和现金？
```

```text
截至今天，这家公司从产品验证到收入和现金的哪一段已经被一手证据闭合？
```

```text
这个行业真正稀缺的环节和利润池在哪里？市场价格已经计入了哪些预期？
```

结果不保证给出可买标的。证据不足时，`WATCH_ONLY`、`NOT_EVALUABLE` 或“暂不动作，等待某项验证”都是有效结论。

### 实验性泛化

原子主张卡、可能性地图、来源血缘和 as-of 边界在产品、政策和技术排障等问题上具有可复用潜力，因此 0.2 允许用户**显式调用** Resanity 做小范围实验：

```text
请使用 Resanity，为这个产品方案画可能性地图，并审计三条承重主张。
```

这不是已经验证的通用能力。当前设计、真实使用和较多案例仍以投资研究为主；非投资场景不自动触发，不套用价格、估值、利润池或候选载体等投资合同，也不把一次成功回答当成泛化证据。医疗诊断和法律判断需要独立协议，不属于当前通用实验范围。

## 0.2 的结构变化

- 保留一个 canonical `resanity` Skill；
- `SKILL.md` 只放通用原子主张协议和路由；
- 投资、认知锚和正式审计分别放在条件加载的 `references/`；
- 投资研究可以自动触发，非投资实验必须由用户明确调用；
- 回答按问题选择模块，不强制每次生成完整报告；
- 锚使用 `active / refuted / realized / archived` 生命周期，代码只读和提醒；
- 正式验证绑定 active locator、canonical Skill hash 与 profile hash，避免验证 A、实际加载 B；
- 正式收据绑定主张时态、来源日期依据和覆盖截止日，阻断用事后当前页回填历史状态。

完整边界见 [ARCHITECTURE.md](ARCHITECTURE.md)。

## 文件结构

```text
SKILL.md                        canonical 核心协议与路由
references/investing.md         散户投资研究 profile 与完整报告格式
references/anchors.md           认知锚生命周期与文件协议
references/formal-audit.md      正式机械审计与身份绑定
tools/skill_identity.py         active/canonical/profile 身份检查
tools/research_check.py         报告机械检查
tools/anchor_check.py           只读锚日期检查
lib/index.js                    可选 DSH 插件
validation/v2/                  当前分层验证协议
```

`validation/v2` 中的 `v2` 是验证协议/schema 代际，不是 Resanity 产品 2.0，也不包含旧候选运行记录。

## 安装与身份核对

把整个目录放到宿主的 Skill 目录，保证 `references/` 和 `tools/` 与 `SKILL.md` 同根。常见候选位置：

| 宿主 | 项目副本 | 用户副本 |
|---|---|---|
| Codex | `<cwd>/.codex/skills/resanity/` | `~/.codex/skills/resanity/` |
| DSH | `<cwd>/.dsh/skills/resanity/` | `$DSH_HOME/skills/resanity/` 或 `~/.agents/skills/resanity/` |

宿主实际返回的 locator 始终优先于候选表。正式运行前检查：

```sh
python3 tools/skill_identity.py --host codex --cwd "$PWD" --profile core
python3 tools/skill_identity.py --host dsh --cwd "$PWD" --profile investing
```

如果宿主给出实际加载路径，追加 `--active-skill /actual/path/SKILL.md`。命令非零表示 active 副本或 profile 与 canonical 不一致。

## 养你的认知锚

只有用户明确要求时才读写工作目录的 `anchors/`。报告会过期，锚用来保留可证伪、可更新的判断：

| 散修概念 | 实际资产 | 含义 |
|---|---|---|
| 道基 | 认知锚 | 能被具名事实支持或推翻的判断 |
| 检验履历 | 证据变化 | 记录每次新事实怎样改变原判断 |
| 渡劫日 | 更新触发器 | 财报、交付、验收或规则生效等复核日期 |
| 走火入魔 | `refuted` 锚 | 连同推翻事实一起保留的错误判断 |

锚的生命周期为 `active / refuted / realized / archived`。提醒器只读 `active` 锚的日期触发器；说“更新锚”才会进入研究和更新，不会在后台自动改写判断。可选的 `journal/decisions.md` 用于记录当时相信什么、采取了什么动作及后来如何验证。

## 正式报告

普通聊天不需要收据。需要保存正式报告或做 A/B 时，先读 `references/formal-audit.md`，生成 `resanity.audit-receipt.v2`，再运行：

```sh
python3 tools/research_check.py path/to/report.receipt.json \
  --skill /canonical/resanity/SKILL.md \
  --active-skill /actual/loaded/resanity/SKILL.md
```

正式验证增加 `--strict`。`AUDIT_RECEIPT_OK` 只代表机械合同闭合，不代表结论正确。

## DSH 插件（可选）

`lib/index.js` 提供 bundled Skill provider、`/resanity-check` 锚体检和可选 Tushare 凭据命令。项目/用户同名 Skill 可以遮蔽 bundled 副本，因此真实验证仍必须运行 identity check。

从本地 tarball 安装到指定 profile：

```sh
dsh plugin --profile headless add /absolute/path/resanity-0.2.1.tgz
```

安装成功后 `resanity` 应自动追加到该 profile 的 `dsh.profile.bundles`。配置中的 `systemNotifications` 默认 `false`，只有用户显式开启时才调用操作系统通知。Tushare 只是投资 profile 的可选价格数据入口，不进入核心研究协议。

## 验证状态

开发和发布前运行：

```sh
npm test
python3 <skill-creator>/scripts/quick_validate.py .
python3 tools/validation_source_check.py
env npm_config_cache=/private/tmp/resanity-npm-cache npm pack --dry-run
```

当前源码树只保留可复用的机械与语义验证协议；候选过程记录和旧协议留在 Git 历史，不进入 0.2.1 发布树。机械门槛用于确认结构、身份、预算、来源资格和收据闭合，不能证明研究质量。

目前应这样理解验证范围：

- **散户投资研究**：目标场景，也是目前设计和案例积累最多的场景；但尚未证明 Alpha、收益改善或稳定有效性。
- **产品、政策、技术排障**：只做适当的泛化实验，用来观察通用核心是否值得继续；尚无足够基准证明跨领域效果。
- **高风险专业判断**：医疗诊断、法律判断等不在当前通用协议内。

8 案例 DSH headless 采集器入口为 `npm run validate:v2:ab:dsh -- --help`；其 dry-run 会先核对 B/R profile 差异、active Skill/profile hash、宿主 patch 与前六层收据，具体参数见 `validation/v2/README.md`。

## 边界

- 不荐股、不下单、不设仓位、不承诺回报；
- 不把“材料没有证明”写成“现实中不存在”；
- 不自动补证据、重试研究、改写结论或晋级锚状态；
- 不建立研究状态机、语义数据库或固定多 Agent 编排；
- 不把工程收据、测试或包安装成功表述成研究正确；
- 判断之后的行为和风险承担始终属于用户。

## FAQ

- **它能告诉我某只股票会涨吗？** 不能。它会告诉你当前价格已经相信了什么、要让上涨逻辑成立哪些事实必须为真、哪条尚未闭合，以及下一验证是什么。
- **证据不足也要给候选吗？** 不需要。没有可靠载体、价格锚或经济暴露闭环时，保留观察或不动作比强行推荐更符合方法目标。
- **没有 Tushare token 能用吗？** 能。Tushare 只是可选价格数据源，不影响核心研究协议。
- **数据存在哪里？** 认知锚和决策日志都是工作目录中的明文文件，可检查、可迁移，没有云端语义数据库。
- **它是投资顾问吗？** 不是。它是研究方法、认知账本和机械审计薄壳。

## License

MIT © 2026 Resanity Contributors
