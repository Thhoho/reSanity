# Resanity

<p align="center"><img src="assets/logo.svg" width="96" alt="Resanity"/></p>

Resanity 是一个证据研究 Skill：把会改变决策的判断拆成“观察到什么、可以推出什么、不能推出什么、对决策有什么影响”。模型保留全部研究语义；代码只做 hash、引用、as-of、来源血缘、预算和安装身份等机械检查。

当前代码版本是 **`2.0.0-rc.1`**，发布通道为 release candidate；当前方法状态仍是
**`UNBENCHMARKED_CURRENT`**。测试通过或有限 A/B 达线不等于研究有效，不证明 Alpha、收益或 PMF。

## v2 有什么变化

- 保留一个 canonical `resanity` Skill；
- `SKILL.md` 只放通用原子主张协议和路由；
- 投资、认知锚、正式审计分别放在条件加载的 `references/`；
- 投资研究可自动触发，非投资任务只在用户明确要求 Resanity、可能性地图、承重主张审计或更新锚时触发；
- 回答按问题选择模块，不强制每次生成完整报告；
- 锚使用 `active / refuted / realized / archived` 生命周期，代码只读和提醒；
- 正式验证绑定 active locator、canonical Skill hash 与 profile hash，防止验证 A、实际加载 B。

完整边界见 [ARCHITECTURE.md](ARCHITECTURE.md)。

## 使用

投资研究可以直接提问：

```text
截至今天，这家公司从产品验证到收入和现金的哪一段已经被一手证据闭合？
```

非投资任务请显式调用：

```text
请使用 Resanity，为这个产品方案画可能性地图并审计三条承重主张。
```

最小输出是一句根结论、关键原子主张卡和唯一下一验证。只有问题需要时才加入投资对照、锚或正式证据表。

## 文件结构

```text
SKILL.md                        canonical 核心协议与路由
references/investing.md         投资 profile 与完整报告格式
references/anchors.md           锚生命周期与文件协议
references/formal-audit.md      正式机械审计与身份绑定
tools/skill_identity.py         active/canonical/profile 身份检查
tools/research_check.py         报告机械检查
tools/anchor_check.py           只读锚日期检查
lib/index.js                    可选 DSH 插件
validation/v2/                  v2 分层验证入口
```

## 安装与身份核对

把整个目录放到宿主的 Skill 目录，保证 references 和 tools 与 `SKILL.md` 同根。常见候选位置：

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

## 认知锚

只有用户明确要求时才读写工作目录的 `anchors/`。生命周期为：

- `active`：等待后续事实，参与提醒；
- `refuted`：被具名事实推翻，保留历史；
- `realized`：等待事件已经兑现；
- `archived`：决策结束或不再相关，但未被推翻。

提醒器只读 `active` 的日期触发器。插件默认不发送系统通知；显式开启后也不会自动更新锚。

## 正式报告

普通聊天不需要收据。需要保存正式报告或做 A/B 时，先读 `references/formal-audit.md`，生成 `resanity.audit-receipt.v2`，再运行：

```sh
python3 tools/research_check.py path/to/report.receipt.json \
  --skill /canonical/resanity/SKILL.md \
  --active-skill /actual/loaded/resanity/SKILL.md
```

正式验证增加 `--strict`。`AUDIT_RECEIPT_OK` 只代表机械合同闭合。

## DSH 插件（可选）

`lib/index.js` 提供 bundled Skill provider、`/resanity-check` 锚体检和可选 Tushare 凭据命令。项目/用户同名 Skill 可以遮蔽 bundled 副本，因此真实验证仍必须运行 identity check。

从本地 tarball 安装到指定 profile 时，使用 DSH 插件管理器；包内的最小
`cordis.patch.yml` 只激活 Resanity，不组合场景或其他插件：

```sh
dsh plugin --profile headless add /absolute/path/resanity-2.0.0-rc.1.tgz
```

安装成功后 `resanity` 应自动追加到该 profile 的 `dsh.profile.bundles`；不需要手工编辑
profile patch 或创建 `node_modules` symlink。

配置中的 `systemNotifications` 默认 `false`；只有用户显式开启时才调用操作系统通知。Tushare 只是投资 profile 的可选价格数据入口，不进入核心研究协议。

## 验证

```sh
npm test
python3 <skill-creator>/scripts/quick_validate.py .
python3 tools/validation_source_check.py
env npm_config_cache=/private/tmp/resanity-npm-cache npm pack --dry-run
```

v2 分层为 core contract、investing profile、open network、anchor、trigger、install identity 和最终同 hash A/B。`validation/dsh-pilot` 与 `validation/dsh-full` 是 v1 历史基线，不是 v2 成绩。
冻结候选在 2026-08-16 的 8 案例 DSH A/B 中经三角色盲化 AI 合议以 6:2 达到有限数值线，
但不是 clean pass；四项已知缺陷和适用边界见
[`validation/v2/runs/2026-08-16-dsh-final-ab-ai-panel/`](validation/v2/runs/2026-08-16-dsh-final-ab-ai-panel/README.md)。
8 案例 DSH headless 采集器入口为 `npm run validate:v2:ab:dsh -- --help`；其 dry-run
会先核对 B/R profile 差异、active Skill/profile hash、宿主 patch 与前六层收据，具体参数见
`validation/v2/README.md`。

## 边界

- 不自动补证据、重试研究、改写结论或晋级状态；
- 不建立研究状态机、语义数据库或固定多 Agent 编排；
- 不下单、不设仓位、不承诺回报；
- 不把工程收据、测试或包安装成功表述成研究正确。

## License

MIT © 2026 Resanity Contributors
