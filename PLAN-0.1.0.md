# Resanity 0.1.0 插件优化计划

状态：待执行
目标版本：0.1.0
计划基线：2026-08-14 当前工作区
项目路径：/Users/xiaweiqi/Documents/resanity

## 1. 目标

0.1.0 的目标不是把 Resanity 扩展成通用研究框架，而是交付一个边界清楚、可安装、可卸载、可验证的 DSH 原生插件。

建议产品定义：

> 面向散户投资研究的认知校验与复盘插件：把模糊问题转成可查证主张，在正式交付前检查证据闭环，并把关键判断沉淀为可复查的认知锚。

0.1.0 应完成一条最小闭环：

1. DSH 能稳定发现并加载 Resanity Skill。
2. Agent 依照 Skill 完成研究语义工作。
3. Agent 在正式交付前调用 Resanity 的机械审计工具。
4. 用户可以把关键判断保存为认知锚。
5. 用户可以手动检查认知锚，并选择是否开启提醒。

## 2. 已确定的产品和架构决策

### 2.1 版本

- 当前目标版本按 0.1.0 管理。
- package.json 当前写有 1.0.0，但不在本计划创建时直接修改。
- 修改版本前必须确认同名 npm 包是否已经发布过 1.0.0；如果已经发布，不得在同一包名下倒退到 0.1.0。
- 可以先生成 0.1.0-rc.1 安装包做干净环境验证，通过后再准备 0.1.0。

### 2.2 插件优先

- 0.1.0 只做好 Resanity 插件。
- 不做投资研究场景 bundle，不组合其他 Provider，不承担完整 harness 配置。
- 允许增加一个只负责激活插件的最小 cordis.patch.yml。它是安装胶水，不是场景 bundle。

### 2.3 语义与机械职责分离

- report.md 是研究语义的唯一事实源。
- 模型负责问题拆解、证据解释、反方审计和结论表达。
- 插件只负责可确定检查：时间、引用、证据闭环、来源 lineage、哈希、receipt 和配置。
- 插件不得自动修改研究结论、补写证据、重试研究、提高证据等级或生成交易动作。

### 2.4 方法状态

- 0.1.0 的工程可运行不代表研究方法已经验证有效。
- 在完成当前版本的真实案例验证前，README 保留 UNBENCHMARKED_CURRENT。
- 测试通过、插件加载成功、receipt 完整都不能被描述为结论正确、存在 Alpha 或适合交易。

## 3. 当前基线

### 3.1 已有能力

- Cordis Skill provider，使用 DSH bundled skill rank。
- /resanity-check 认知锚检查命令。
- 定时扫描认知锚和操作系统通知。
- /resanity-tushare 凭据命令。
- tools/anchor_check.py 认知锚检查器。
- tools/research_check.py 正式报告机械审计器。
- JavaScript 插件测试和 Python 检查器测试。

### 3.2 已确认的工程基线

- npm test 当前通过。
- JavaScript 插件测试通过。
- 15 个 Python 测试通过。
- npm pack --dry-run 可成功生成约 228 KB、35 个文件的包。

### 3.3 当前工作区状态

计划创建时存在以下用户修改，不得重置或覆盖：

- 已修改：EXAMPLES.md、README.md、SKILL.md、anchors/README.md、lib/index.js、package.json、test/plugin.test.mjs、tools/anchor_check.py。
- 新增未跟踪：ARCHITECTURE.md、test/test_anchor_check.py、test/test_research_check.py、tools/research_check.py、validation/。

新会话开始实现前，必须先阅读这些 diff，确认哪些属于 0.1.0 基线。不要通过 git reset、checkout 或覆盖文件来获得干净工作区。

## 4. 0.1.0 的插件边界

### 插件负责

- 分发和注册 Resanity Skill。
- 暴露报告机械审计工具及人工命令。
- 扫描认知锚。
- 在用户显式启用后发送去重提醒。
- 校验自身配置。
- 遵守 Cordis 注册、释放、热重载和错误处理规则。
- 提供可重复的安装、测试和打包路径。

### 插件不负责

- 判断投资结论是否正确。
- 管理第二份研究语义状态。
- 建立候选晋级或研究状态机。
- 固定多 Agent 角色和研究轮次。
- 自动搜索、自动重试或自动修订报告。
- 证券推荐、下单、仓位管理和收益承诺。
- 通用行情平台或数据 Provider 编排。

### 后续版本再考虑

- DSH 原生市场观察工具。
- 统一 credential reference。
- 场景 bundle。
- UI、跨设备同步或协作能力。
- 更多研究领域的适配。

## 5. 目标运行结构

0.1.0 保持单 npm 包和单 Cordis 插件：

- Skill provider：读取、验证并注册 SKILL.md。
- Research check adapter：把现有确定性检查器暴露为模型工具和人工命令。
- Anchor service：发现、解析和检查 anchors 目录。
- Reminder adapter：显式启用、去重、可释放的通知。
- Plugin assembly：集中声明 Config、inject、commands、tools、timer 和 disposer。

不要为了形式完整提前拆成多个 npm package，也不要增加没有独立演进需求的 Service Definition / Provider / Consumer 能力缝。

## 6. 实施阶段

### 阶段 0：冻结真实基线

- [ ] 阅读当前 git diff 和所有未跟踪文件。
- [ ] 确认 SKILL.md、ARCHITECTURE.md、research_check.py 和 validation/ 是本次 0.1.0 的有效输入。
- [ ] 确认 npm 上同名包的发布状态。
- [ ] 确认最终 npm 包名；Skill 名继续保持 resanity。
- [ ] 只在发布准备阶段把 package.json 版本调整为 0.1.0 或 0.1.0-rc.1。
- [ ] 不自动提交、推送、打 tag 或发布。

完成条件：新会话能够说明当前 diff 的来源和保留策略，没有丢失用户修改。

### 阶段 1：修复插件基础质量

- [ ] 解析并注册 SKILL.md 的 whenToUse。
- [ ] 内置 SKILL.md 损坏或 frontmatter 无效时加载失败并给出明确诊断，不再静默返回空 Skill 列表。
- [ ] 为 checkIntervalHours 增加有限正数校验。
- [ ] 为 reminderWindowDays 增加非负整数校验。
- [ ] 为 anchorsDirs 增加数组、路径和重复项处理规则。
- [ ] 显式声明插件使用的 timer、skills、agents 等依赖关系。
- [ ] 所有 provider、command、tool、timer 都通过 Cordis effect 注册，并能在卸载或热重载时释放。
- [ ] 修正文档和代码中能力数量不一致等当前状态描述。

完成条件：错误配置在加载期失败；插件卸载后不残留 provider、command、tool 或 timer。

### 阶段 2：交付核心工具 resanity_research_check

- [ ] 将 tools/research_check.py 作为 0.1.0 的确定性规则源。
- [ ] 暴露模型可调用的 resanity_research_check 工具。
- [ ] 增加 /resanity-check-report <report-path> 人工命令。
- [ ] 工具默认只读检查，不修改报告，不触发搜索或重试。
- [ ] 如果 receipt 写入属于必要操作，将其设计为独立、显式的动作；检查动作不得隐式覆盖已有文件。
- [ ] 返回稳定的机器可读状态和面向用户的可修复诊断。
- [ ] 诊断至少覆盖 as_of、C/E 对应关系、来源 lineage、哈希、receipt 和预算限制。
- [ ] subprocess 调用必须异步、有超时、检查退出状态，并在插件释放时正确终止。
- [ ] 不在 JavaScript 中复制一套研究检查规则；避免 Python 与 JavaScript 语义漂移。
- [ ] 增加通过、失败、文件缺失、检查器异常、超时和释放测试。

完成条件：Agent 可以在正式交付前调用一次工具并得到可行动的检查结果；工具结果不声称研究正确。

### 阶段 3：收紧认知锚和通知

- [ ] 保留手动 /resanity-check。
- [ ] systemNotifications 默认值改为 false。
- [ ] 用户显式启用通知后才允许调用操作系统通知程序。
- [ ] 对逾期提醒按认知锚状态变化或自然日去重，避免固定间隔重复轰炸。
- [ ] 通知调用改为异步、有超时、检查失败但不阻断锚检查结果。
- [ ] 继续覆盖跨年日期、过去的 M/D、无效日期、重复 anchorsDir 和 Agent cwd 变化。
- [ ] 明确认知锚文件是用户语义资产，插件只读取和提示，不自动改变判断内容。

完成条件：默认安装无系统通知副作用；启用后提醒可预测、可关闭、不重复轰炸。

### 阶段 4：处理 Tushare 和凭据边界

Tushare 不是 0.1.0 的核心卖点。推荐方案是把 /resanity-tushare 从 0.1.0 默认插件能力和主 README 中移出，保留 Python 脚本通过环境变量供高级用户使用；DSH credential 和市场观察工具在后续版本统一设计。

如果决定保留当前命令，则以下事项全部是发布阻断项：

- [ ] 校验请求改用 HTTPS。
- [ ] 明确无效的 token 不落盘、不覆盖已有有效 token。
- [ ] 网络不可达与 token 无效使用不同状态。
- [ ] token 不进入 prompt、命令回显、日志或测试快照。
- [ ] 凭据文件权限和原子写入有测试。
- [ ] 说明为什么没有使用 DSH ctx.credentials，以及后续迁移路径。

不能保留“半集成但不安全”的中间状态。

### 阶段 5：安装和打包

- [ ] README 使用真实的 dsh plugin --profile <name> add <package> 流程。
- [ ] 不再把手工创建 node_modules symlink 作为普通用户主安装方式。
- [ ] 增加只负责激活 Resanity 的最小 cordis.patch.yml 和 package manifest。
- [ ] 该 manifest 不组合其他插件，不定义场景 preset，因此不视为场景 bundle。
- [ ] 补齐 package.json 的 repository、homepage、bugs、keywords、engines 和必要的发布元数据。
- [ ] 明确 Node 和 DSH RC 兼容范围。
- [ ] 从 npm files 中排除内部 validation/dsh-pilot prompts、fact gates 和 scorecards。
- [ ] 保留运行所需的 SKILL.md、脚本、模板和用户文档。
- [ ] 检查打包后的路径解析，禁止依赖仓库源码目录或当前工作目录偶然存在的文件。

完成条件：从 tarball 安装到干净临时 profile 后，不需要手工 symlink 即可加载插件。

### 阶段 6：真实组合测试

- [ ] 使用真实 Cordis Context 验证加载和释放。
- [ ] 使用真实 DSH Loader/profile 验证组合。
- [ ] 从 npm pack 生成的 tarball 做安装 smoke test。
- [ ] 验证 Skill 能被发现，且 description 和 whenToUse 正确。
- [ ] 验证 command、tool 和 timer 的注册及 disposer。
- [ ] 验证无效配置、损坏 SKILL、缺少通知程序、检查器异常和进程超时。
- [ ] 如果保留凭据命令，验证无效 token 不会覆盖旧值。
- [ ] 保留当前 JavaScript 和 Python 单元测试。
- [ ] 运行 npm test。
- [ ] 使用独立临时 npm cache 运行 npm pack --dry-run，检查 tarball 文件清单。

完成条件：单元测试、真实 Loader 组合测试和打包安装测试全部通过。

### 阶段 7：文档与发布准备

- [ ] README 首屏使用新的准确定位。
- [ ] 清楚说明 Skill、插件工具、认知锚和可选脚本之间的关系。
- [ ] 明确非目标：不荐股、不交易、不保证收益、不自动改结论。
- [ ] 把 UNBENCHMARKED_CURRENT 与工程版本号分开表达。
- [ ] 提供一条完整示例：研究问题 → 报告 → research check → 修复 → 认知锚。
- [ ] 更新 EXAMPLES.md 和 anchors/README.md，使其与实际命令和文件路径一致。
- [ ] 检查 npm tarball，不包含秘密、缓存、实验输出或内部验证 prompt。
- [ ] 准备 0.1.0-rc.1 本地安装包。
- [ ] 获得用户明确授权后，才允许 commit、push、tag 或 npm publish。

## 7. 建议的变更切片

以下是建议的变更顺序，不代表自动获得提交或推送授权：

1. 基线整理与版本、包名决策。
2. Skill provider、Config 和 Cordis 生命周期修复。
3. resanity_research_check 工具及命令。
4. 认知锚和通知副作用收紧。
5. Tushare 去留与凭据安全处理。
6. 安装 manifest、package allowlist 和元数据。
7. 真实 DSH Loader、tarball 安装测试。
8. README、EXAMPLES 和 0.1.0 发布说明。

每个切片都应包含对应测试和文档，不把全部风险堆到最后一次发布提交。

## 8. 0.1.0 发布验收标准

只有同时满足以下条件，才进入发布候选：

- 干净 DSH profile 能从打包产物安装并激活插件。
- Resanity Skill 的 description 和 whenToUse 均正确。
- Agent 能调用 resanity_research_check。
- 检查工具默认不修改报告、不搜索、不重试。
- 错误配置加载失败并给出明确诊断。
- 默认安装不发送系统通知。
- 启用通知后具有去重和关闭机制。
- 插件卸载或热重载后没有残留 effect 或子进程。
- 不泄露 Tushare token 或其他凭据。
- tarball 不包含内部验证语料和无关开发文件。
- 所有相关测试通过。
- README 保留方法有效性的证据边界。

## 9. 明确延后

以下内容不进入 0.1.0：

- 投资场景 bundle。
- 固定多 Agent 研究编排。
- 研究状态机、候选晋级和第二语义数据库。
- 自动重试、自动补证据、自动改结论。
- 交易、下单、仓位和收益评估。
- Web UI 和云同步。
- 以“通用认知平台”替换散户投资研究定位。

## 10. 新会话启动提示

可以用下面这段话启动新的优化会话：

> 在 /Users/xiaweiqi/Documents/resanity 中，按照 PLAN-0.1.0.md 开始优化 Resanity 插件。先阅读 SKILL.md、ARCHITECTURE.md、README.md、lib/index.js、package.json、tools/research_check.py，以及当前 git diff；保留所有用户未提交修改。先完成阶段 0 的基线确认，然后执行阶段 1 和阶段 2。不要自动 commit、push、tag 或 publish，也不要扩展到场景 bundle。
