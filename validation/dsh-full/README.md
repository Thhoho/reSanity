# DSH 完整语义验证

> 默认状态：`UNBENCHMARKED_CURRENT`。本套件验证当前 reSanity 候选方法是否稳定守住语义边界；它不是研究状态机，也不把通过结果解释成 Alpha、收益或 PMF。

四题 pilot 只保留为十几分钟到一小时量级的快速门禁。完整验证默认执行 **21 个互相归档的全新 DSH 会话**，解决“一次碰巧答对”的问题：

| 阶段 | 会话数 | 回答什么 |
|---|---:|---|
| `contract` | 8 | 对象范围、披露沉默、同源转载、as-of、不可读文件、明示否认与措辞不变性是否稳定 |
| `field` | 10 | 真实在线研究中，事实召回、利润链、公司经济暴露、定价和行动边界是否可用 |
| `longitudinal` | 3 | 同一认知锚能否跨全新会话被验证、更新并在反证出现时失效，而不是被删除或硬拗 |

runner 只做五件机械工作：冻结输入、隔离工作区、每行调用一次 DSH、归档原始会话、核对宿主计量/文件写入。它不读懂报告，不按答案分支，不修报告，也不重试。

## 运行

先做不调用模型的完整检查：

```bash
python3 /Users/xiaweiqi/Documents/resanity/validation/dsh-full/run-full-t.py --check
```

可选的机械预检会创建一个不可继续使用的全新目录：

```bash
bash /Users/xiaweiqi/Documents/resanity/validation/dsh-full/run-full-t.sh \
  --prepare-only /tmp/resanity-full-preflight-2026-08-15
```

正式运行完整 21 会话；目标目录必须不存在，并位于项目仓库之外。推荐并发 3：

```bash
bash /Users/xiaweiqi/Documents/resanity/validation/dsh-full/run-full-t.sh \
  --jobs 3 \
  /Users/xiaweiqi/Documents/dsh-resanity-full-v3-2026-08-15
```

`--jobs` 允许 `1–8`，默认 `1`。8 个 contract 和 10 个 field 各有独立工作区与独立 session 根目录，可以进入并发池；`A01-T0 → T1 → T2` 共享认知锚工作区，runner 会把它们固定在同一依赖 lane 内串行执行，但该 lane 可以与其他独立题并行。`environment.json` 会冻结实际并发数和 lane 数。不要手工对同一运行目录启动多个 runner。

只为调试 runner 时可以指定一个阶段；这种结果不能冒充完整验证：

```bash
bash /Users/xiaweiqi/Documents/resanity/validation/dsh-full/run-full-t.sh \
  --phase contract /Users/xiaweiqi/Documents/dsh-resanity-contract-debug-2026-08-15
```

DSH 路径和 home 默认沿用已验证的 rc.6 环境；若位置变化，用 `DSH_BIN`、`DSH_HOME_BASE` 环境变量显式覆盖。suite 仍会从每个原始会话核对 provider、model、effort、权限、可用工具和首次 Skill 激活；位置变化不会放宽运行身份。

## 一次运行如何冻结

开始模型调用前，runner 会把以下内容复制到运行根目录的只读语义快照区，并记录 SHA-256：

- 当前 `SKILL.md` 与随包脚本；
- `suite.json`；
- 本次选中行的完整 prompts 和 fixtures；
- DSH 版本、settings、headless profile/patch；
- runner 与 `session-metrics.py`。

随后所有工作区都从该快照安装 Skill，不再读取可能变化的项目工作树。任何中断都保留为一次不完整运行；不要删除失败行后补跑，也不要在原目录 resume。修改 Skill、prompt、fixture、预算或运行设置都必须换全新根目录。

## 宿主硬门禁

每个会话分别核对：

- 正好产生一个新 session artifact；
- `skill` 实际调用一次，provider/model/effort/权限与 suite 一致；
- 非缓存 token、总工具调用、Web 搜索和墙钟没有超出该行预算；
- 模型没有在普通语义题中写文件；纵向锚题只允许修改 `anchors/*.md`、`anchors/index.md`、`journal/decisions.md`，删除文件永远失败；
- stdout 非空，宿主收据来自原始会话而不是模型自报；
- 零自动重试。

完整运行即使某题超预算或 DSH 返回非零，也继续保存其余独立题；最终以非零退出。环境身份或 session 归档异常同样不会触发补跑。并行只缩短总墙钟，不改变每题独立预算；评估成本时仍读取每题宿主收据，不能用整批总耗时替代单题耗时。

## 语义评分

宿主通过不代表语义通过。运行结束后按顺序做：

1. 对照 [semantic-gates.md](semantic-gates.md) 审核 8 个封闭语料题；必须 8/8 通过，`N07/N08` 根事实结论必须一致。
2. 在打开报告前，按 [fact-gates.md](fact-gates.md) 为 10 个在线题建立截至题目 as-of 的一手来源索引；每题核验最承重 3 条事实。
3. 使用 [scorecard.md](scorecard.md) 记录 P0、`MAJOR_NON_P0`、决策效用、成本以及纵向锚行为。
4. `A01-T0/T1/T2` 必须在三个全新 session 中保留同一锚的检验履历；T2 的明确反证必须使原锚标 `[失效]`，不得删除历史。

完整 T 回归的晋级线：21/21 宿主门禁通过；contract 8/8；纵向 3/3；field 无 P0、至少 8/10 决策效用达到 12/16，且 field 中位成本不超过冻结预算的 80%。这只允许说“当前候选通过完整 T 回归”。

若要回答“是否比强模型裸跑更好”，还要在同一 hash 下把 10 个 field prompts 与强通用研究提示做配对身份遮蔽 A/B；不能拿旧 hash、旧日期或旧模型结果拼接。正式方法状态的上层规则仍以 [../README.md](../README.md) 为准。

## 带回结果

至少保留整个根目录；核心文件是：

```text
environment.json
frozen-inputs/
frozen-method/
run-log.md
summary.json
runs/<run-id>/T/{prompt.md,report.md,headless-stderr.txt}
runs/<run-id>/host/{raw-session.*,session-metrics.json,host-receipt.json,run-meta.json,workspace-changes.json}
workspaces/A01/T/anchors/       # 纵向锚最终状态
```

不要只挑通过的报告带回来。
