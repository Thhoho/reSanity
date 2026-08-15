# DSH 架构冒烟验证

> 目的：用新版 DeepSeek Harness（DSH）判断“模型拥有全部研究语义 + 极薄确定性外壳”是否比旧复杂状态机更好。
> 这只是 4 题先导试验，不能把项目状态从 `UNBENCHMARKED_CURRENT` 改成已验证。

## 先分开回答两个问题

1. **语义/产品问题**：同一模型、同一宿主、同一课题下，新方法是否给出更正确、更可用于决策、成本更低的报告？
2. **工程兼容问题**：DSH 能否让新方法保存报告与审计收据，并由无语义检查器机械闭合？

不要在 A/B 主试验里要求某一臂额外生成收据，否则比较的任务已经不同。先跑 4 题 A/B，再单独跑一次薄壳兼容检查。

## 1. 冻结运行条件

运行前把以下信息填入 [run-log-template.md](run-log-template.md)：

- DSH 版本与启动命令；
- provider、精确 model ID、reasoning/effort 档位；
- Web、shell、文件系统和子代理是否可用；
- 两个方法的 `SKILL.md` SHA-256；
- 每臂最多 3 次发现驱动重定向；T 臂 runner 另冻结 30 次总工具调用、15 次 Web 搜索、150000 非缓存 token 与 900 秒硬墙钟上限；
- 统一截止日：`2026-08-14`，时区：`Asia/Shanghai`。

冻结后不要看完第一题就修改 Skill、提示词、模型设置或工具权限。任何改动都要另开一次验证。

本次建议冻结对象见 [methods.md](methods.md)。正式运行时重新计算 hash；不一致就停，不要把不同版本混成一个结果。

### 不计分的安装预检

每个正式工作区只放一份方法。候选臂至少复制 `SKILL.md`、`scripts/` 和 `tools/research_check.py`；旧臂从冻结 commit 导出完整受控文件，不复制 `.runs`、历史工作区或未跟踪状态。示意：

```bash
# T：把候选方法资源复制到每个 T 工作区
mkdir -p <T-workspace>/.dsh/skills/resanity/scripts <T-workspace>/.dsh/skills/resanity/tools
cp /Users/xiaweiqi/Documents/resanity/SKILL.md <T-workspace>/.dsh/skills/resanity/
cp /Users/xiaweiqi/Documents/resanity/scripts/*.py <T-workspace>/.dsh/skills/resanity/scripts/
cp /Users/xiaweiqi/Documents/resanity/tools/research_check.py <T-workspace>/.dsh/skills/resanity/tools/

# L：从冻结 commit 导出旧方法的全部受控资源
mkdir -p <L-workspace>/.dsh/skills/trade-nothing
git -C /Users/xiaweiqi/Documents/trade-nothing archive 186bc8cab05117046c3963143bf7b16a17152a04 | tar -x -C <L-workspace>/.dsh/skills/trade-nothing
```

正式计分前，分别在两个预检工作区开启一次不计分的新会话：

```text
请使用 skill 工具加载 <resanity 或 trade-nothing>。只返回加载到的 skill 名称和正文第一个 H1 标题，不执行研究，也不写文件。
```

再确认两边看到完全相同的 Web/search/fetch 工具与权限。预检失败可以修安装；修好后丢弃预检会话，再冻结环境。正式案例开始后，激活失败和权限差异不再补救。

## 2. 两个对照臂

| 臂 | 方法 | 激活方式 | 测量含义 |
|---|---|---|---|
| `L` | 旧 Trade Nothing v0.18 复杂状态机 | 显式调用 `skill({name: "trade-nothing"})`，按 `-deepthink2`、3 轮上限执行 | 原系统的完成率、质量和运行负担 |
| `T` | 当前 reSanity 薄方法 | 显式调用 `skill({name: "resanity"})`，3 轮上限执行 | 模型全语义 + 薄边界的完成率、质量和运行负担 |

每个工作区只能出现一个待测 Skill。不要同时暴露两个方法，也不要在旧 Trade Nothing 仓库、当前 reSanity 仓库或存有历史报告/锚的目录里直接运行。

DSH 项目级 Skill 放在：

```text
<workspace>/.dsh/skills/resanity/SKILL.md
<workspace>/.dsh/skills/trade-nothing/SKILL.md
```

每个“案例 × 臂”使用独立空工作区和全新会话。只给待测 Skill 读取其随包资源的权限，不给它读取另一个臂、评分规则、旧报告、锚库或其他案例结果的权限。

## 3. DSH 运行方式

新版 DSH 目前是开发者预览。推荐先用 Web UI 手工跑，便于确认 Skill 是否真的加载：

```bash
npx @deepseek-ai/dsh web
```

在 Web UI 中选择对应空工作区，新建会话，粘贴该臂对应的完整 prompt。第一步必须能看到模型调用 `skill` 工具并成功加载正确名称；没有加载就记作 `ACTIVATION_FAILURE`，不要补发第二条消息挽救。

也可用官方 headless profile；它会为每次任务建立一个新的持久会话并只打印最终答案：

```bash
npx @deepseek-ai/dsh --profile headless "<完整 prompt>"
```

无论用哪种方式，都保存原始会话/会话 ID、最终回答、开始结束时间以及 DSH 可见的 token 和工具计量。模型不得自报这些数字；结束后由宿主适配器生成 `resanity.host-receipt.v1`。不要手工润色报告。

### 平衡运行顺序

降低缓存、熟练度和时间漂移：

| 案例 | 先跑 | 后跑 |
|---|---|---|
| `C01` | `L` | `T` |
| `C02` | `T` | `L` |
| `C03` | `L` | `T` |
| `C04` | `T` | `L` |

尽量在同一天完成一对；一臂失败也不重跑，失败本身进入结果。

## 4. 四个诊断案例

完整可复制提示在 `prompts/`：

| 案例 | 要击中的能力 | 为什么能区分架构 |
|---|---|---|
| `C01` 长鑫当前真相 | 官方披露完整性、HBM 边界、治理/融资重大事实 | 检查旧门禁是否增加真实召回，还是只增加流程负担 |
| `C02` AI 数据中心利润池 | 宽主题拆解、利润池、公司经济暴露、定价 | 检查模型自由路由是否比固定对象更会抓真正矛盾 |
| `C03` 商业航天政策传导 | 政策到订单、收入、利润的因果链 | 防止把政策目标、概念标签直接变成买入结论 |
| `C04` HBM 负面核验 | `NO_RESULT`、传闻隔离、最早验证信号 | 检查没有复杂状态机后是否仍会诚实停下 |

### C04 规则修复后的定向回归（不计分）

修改“否定承重主张”纪律后，先不要把旧 T 臂分数与新 Skill 混用。用新 hash、两个独立空工作区和两个全新会话各跑一次：

1. 重跑 `prompts/C04-T-thin.md`，验证成功取得裁决文件时确实直读正文；
2. 跑 `prompts/C04F-T-unreadable.md`，验证裁决文件不可读时诚实降级。

`C04F-T` 仅在以下条件全部满足时通过：

- 实际尝试读取 `./decision-document.pdf`，失败后不重试同一路径或换命令重复读取；
- 根结论标 `INSUFFICIENT`，并把 `[E2]`、`[E3]` 视为同一血缘的 `SINGLE_SOURCE`；
- 只闭合“当前封闭证据包无法裁决”的证据边界，并紧邻给出 `检索结论` 与 `现实边界`；不写“事实不存在、官方否定、反向证据、尚未进入产品布局、若存在必披露、否定命题已闭合”；
- 不使用 Web、外部语料、模型记忆或人工补写。

`C04-T` 通过时，报告只能把直读结果表述为“在已声明的公开文件/检索范围内未获一手证实”，不得把文件未披露升级为现实不存在、公司明示否认或产品布局结论。保存两次运行的原始会话、最终回答、Skill hash、工具/耗时计量；成功路径若产生来源快照，由宿主计算 SHA-256。正式验证仍使用 `resanity.audit-receipt.v1` 的 `sources[].snapshot_sha256`，不另造语义状态或第二套收据。

两项通过后才冻结新 hash。低成本修复检查可以只重跑新 T 臂的 C01–C04，并把旧 L 视为历史参照；若要形成新的严格 A/B 结论，必须重新配对运行 L/T，不能把不同 Skill hash 的 T 臂报告合并计分。

## 5. 评分顺序

先复制最终报告并随机命名为 `Report X/Y`，隐藏目录名、Skill 名、运行日志和方法身份。格式可能泄露方法，因此只能叫**身份遮蔽**，不是双盲。

按 [scorecard.md](scorecard.md) 做两道闸：

1. **事实闸门**：先按 [fact-gates.md](fact-gates.md) 建立不知道臂身份的一手来源索引，再独立核验每份报告最承重的 3 条事实，并检查已知重大官方披露。出现 P0 错误、重大遗漏、越过 as-of、把传闻冒充事实，不能靠文风或总分抵消。
2. **决策效用**：在事实闸门之后比较根结论、最弱环节、反证、定价边界和下一步验证。不要奖励长度、表格数量或术语密度。

如需让另一个模型协助身份遮蔽评审，使用 [judge-prompt.md](judge-prompt.md)，但最终 P0 事实核验仍应由人或独立的一手来源审计完成。

## 6. 冒烟结论规则

先导试验只允许四种结论：

- **值得扩到正式验证**：`T` 无 P0 负回归；至少 3/4 案例在决策效用上胜出，且中位 token/耗时不高于 `L` 的 1.10 倍；或决策效用不劣且中位成本至少降低 30%。
- **只证明更易运行**：`L` 因宿主/状态机失败、`T` 完成，但双方不足 3 个可比较报告。可以说兼容性和运行负担更好，不能说语义更好。
- **不值得继续**：`T` 有任一 P0 负回归，或在至少 2 个案例中决策效用明确落后。
- **不确定**：介于上述条件之间，或 Web/一手来源能力在两臂间不一致。

只有第一种结果才扩展为 [21 会话完整 T 回归](../dsh-full/README.md)；完整 T 回归通过后，再按 [上一级协议](../README.md) 对其中 10 个在线题加入“强通用研究提示”配对臂，检验新 Skill 是否不仅更易运行，也真正胜过同模型无 Skill 的强基线。

## 7. 单独验证薄壳兼容性

A/B 完成后，在新的 `T` 工作区运行 [shell-compat-prompt.md](shell-compat-prompt.md)。它要求 DSH 只执行一次非 strict 检查，并保存第一次结果；不得失败后补证据或改写报告。

判定：

- `AUDIT_RECEIPT_OK`：只说明 DSH 能完成机械闭合；
- `AUDIT_RECEIPT_FAILED`：记录原始错误码，属于兼容性结果；
- 没有 DSH 原始会话与规范化宿主收据时，不运行或声称通过 `--strict`；模型在没有宿主收据时填写 token、工具次数或耗时，checker 会失败而不是接受自报值。

## 8. 跑完带回来什么

请保留：

```text
dsh-version.txt
run-log.md
C01/{L,T}/report.md
C02/{L,T}/report.md
C03/{L,T}/report.md
C04/{L,T}/report.md
sessions/                  # DSH 原始会话导出或会话 ID 清单
shell-compat/              # report、receipt、checker-first-result
```

把这组产物交回来后，再做身份遮蔽、事实 P0 审计和最终架构判断；不要只发你觉得最好的一两份报告。

## 9. 当前修复版 T 臂的快速重跑

手工建目录容易把 DSH 留在项目仓库里，导致模型读到评分规则、旧报告或锚库。4 题低成本复核可运行 [run-final-t.sh](run-final-t.sh)，不要在 DSH 对话中只说“重跑验证脚本”。它现在只承担快速门禁；准备形成候选结论时必须运行 [完整套件](../dsh-full/README.md)。

先做一次不调用模型的机械预检（目标目录也必须是全新路径，用完不要拿它正式跑）：

```bash
bash /Users/xiaweiqi/Documents/resanity/validation/dsh-pilot/run-final-t.sh \
  --prepare-only /tmp/resanity-final-t-v2-preflight-2026-08-15
```

正式运行四个新 T 案例：

```bash
bash /Users/xiaweiqi/Documents/resanity/validation/dsh-pilot/run-final-t.sh \
  /Users/xiaweiqi/Documents/dsh-final-t-v2-2026-08-15
```

runner 会在任何模型调用前校验 Skill、DSH 版本、模型设置和 headless profile；为 `C01`–`C04` 各创建一个独立 cwd，只调用一次 DSH，不自动重试。会话存储通过运行时 patch 指向本次全新的 `sessions/`，不复用旧会话库。每题结束后自动保存：

```text
C01/T/prompt.md
C01/T/report.md
C01/T/headless-stderr.txt
C01/host/raw-session.jsonl.zstd
C01/host/session-metrics.json
C01/host/host-receipt.json
C01/host/run-meta.json
```

`host/` 在模型工作区之外，模型不能预先生成或覆盖宿主收据。runner 用 900 秒 timeout 执行墙钟上限，并在每题归档后从原始会话核验其余预算；模型新写文件也会被列为 contract failure。它仍会跑完四个一次性案例并保留全部失败证据，最后以非零状态结束，不自动重试。

其余三题同构；根目录还会保存 `environment.json`、`method-manifest.sha256`、`dsh-version.txt` 和 `run-log.md`。如果目标目录已经存在、运行环境漂移或新会话不唯一，runner 会停止且不会重跑。某题 DSH 返回非零、预算超限或写入额外文件时，原始失败都会留档；不要删除目录后补跑，直接把整个运行目录带回来判断。
