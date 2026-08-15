# 当前版本验证协议

> 状态：`UNBENCHMARKED_CURRENT`。本目录是验证协议，不是研究状态机，也不会执行模型调用。

DSH 验证分两层：改动过程中使用 [4 题快速门禁](dsh-pilot/README.md)；候选冻结后使用 [21 会话完整 T 回归](dsh-full/README.md)，其中含 8 个封闭语料契约、10 个真实在线课题和 3 个跨会话认知锚阶段。两者都不能替代本页要求的强基线配对 A/B；工程通过与当前方法有效性必须分开报告。

## 1. 冻结再跑

每次验证先记录：

```bash
git rev-parse HEAD
shasum -a 256 SKILL.md
git status --short
```

候选臂必须使用该次冻结的 `SKILL.md`。任何提示词改动都产生一个新候选版本；旧分数不能自动继承。

实际安装态也必须与冻结文件同 hash。不要在旧 Trade Nothing 仓库内跑裸臂；两个臂分别放进干净工作目录，避免自动读取旧 SKILL、锚或报告。

## 2. 最小对照设计

- 至少 10 个真实课题，覆盖公司事实核验、宽主题利润池、政策传导、负面/证伪案例、`NO_RESULT` 案例；当前冻结题面和宿主执行方式见 `dsh-full/`；
- 同一问题、as-of、模型、工具权限、搜索/抓取预算与时间上限；
- 基线使用强通用研究提示，不故意移除引用、反证或 as-of 等基本能力；
- 运行前冻结问题、关键事实面和评分 rubric，运行模型看不到答案；
- 两臂各只跑一次，不为失败臂自动重试；运行失败本身计入结果。
- 另跑封闭语料契约和跨会话锚回归，防止在线题偶然通过；这些回归只判候选自身稳定性，不进入 A/B 胜负分母。

每个课题/臂保存：

```text
<case>/<arm>/
  prompt.md
  report.md
  report.receipt.json
  sources/                 # 原始快照，strict 模式需要
  host-receipt.json        # 宿主结束后生成的规范化计量；strict 模式需要
  raw-session.jsonl.zstd   # 宿主原始会话；由 host receipt 绑定 hash
```

正式评分前运行：

```bash
python3 tools/research_check.py <case>/<arm>/report.receipt.json --strict
```

模型使用 `receipt-template.json`，只填写主张/来源索引、as-of 和预先声明的预算上限，不填写 `tokens_total`、`tool_calls` 或 `wall_seconds`。宿主结束后使用自己的无语义适配器生成 `host-receipt.json`；DSH 的命令是：

```bash
python3 validation/dsh-pilot/session-metrics.py --format host-receipt \
  raw-session.jsonl.zstd > host-receipt.json
```

规范格式见 `host-receipt-template.json`。正式收据再 hash 绑定该文件。校验器会解析规范化宿主收据、逐项核对 audit receipt 中任何运行数字和预算用量，并验证原始会话 hash；没有宿主收据却自报计量会失败。它仍不读取消息正文，也不判断研究语义。

## 3. 盲评

先完成机械校验，再复制匿名报告给评估者；不要把臂名、SKILL、收据或目录名交给评估者。格式本身可能泄露方法，因此“盲评”应描述为**身份遮蔽**，不能声称双盲。

建议分开评分：

1. 决定性事实正确率；
2. 承重事实遗漏数，尤其官方披露索引中的资本/治理事件；
3. 来源可追溯与独立血缘；
4. 反证与替代解释质量；
5. 定价/预期缺口是否真的可执行；
6. 一次阅读后的决策可用性；
7. token、工具次数、耗时与失败率。

不要把结构合规、报告长度或“有价格数字”本身计为研究价值。

P0 只用于会改变根结论或真实行动的错误/遗漏。复合技术或商业链条先拆阶段；只改写子判断的重大遗漏记 `MAJOR_NON_P0`。P0 按独立根因计数，同一底层问题命中多个检查项时不得重复计数。

## 4. 建议晋级线

当前版本只有同时满足以下条件，才从 `UNBENCHMARKED_CURRENT` 改为“当前版本通过有限方法验证”：

- 10/10 两臂均有完整原始产物，或失败被如实计入；
- 候选臂无决定性事实正确率、重大遗漏或证据纪律的 P0 负回归；
- 决策可用性至少 7/10 案例优于强基线；
- 中位 token 不高于基线 1.25 倍；
- strict 收据通过率 100%，且没有人工改写报告后再评分。

这仍不证明收益、Alpha、PMF 或长期认知改善。锚的长期价值需要在真实触发日继续观察“能否低成本更新、是否减少重复犯错”。
