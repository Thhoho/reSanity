# 正式机械审计

只在用户要求保存正式报告、生成审计收据、做验证或检查安装身份时加载本文件。普通聊天不生成收据，也不得声称经过正式审计。

## 所有权边界

`report.md` 是唯一语义真相。模型负责主张、证据标签、结论、下一步与锚语义；确定性外壳只检查 hash、引用闭合、as-of、来源血缘、预算、来源快照和安装身份。外壳不得理解或改写结论、补证据、重试研究或晋级状态。

## 方法与安装身份

正式运行前先取得身份快照：

```sh
python3 <skill-root>/tools/skill_identity.py \
  --host <codex|dsh|generic> \
  --cwd <workspace> \
  --profile <core|investing|anchors|formal-audit|组合>
```

若宿主已返回实际加载的 Skill locator，追加 `--active-skill <path>`，以宿主结果优先。身份结果必须同时记录：

- `active_locator`：实际加载的 `SKILL.md`；
- `canonical_skill_sha256`：仓库 canonical `SKILL.md`；
- `active_skill_sha256`：实际加载文件；
- `profile_sha256`：核心文件与本次条件加载 references 的规范化组合 hash。

任何 active/canonical/profile 不一致都属于安装身份失败。不要在“验证 A、实际加载 B”的状态下继续评分。已知遮蔽优先级由身份工具显式列出：宿主报告的 locator 最高；否则项目副本高于用户副本，用户副本高于插件 bundled 副本。不同宿主无法确认时必须传入 `--active-skill`，不能猜。

## v2 审计收据

在报告中给决定性主张编号 `[C1]`、来源编号 `[E1]`，并在同目录生成 `resanity.audit-receipt.v2` JSON。使用 `validation/receipt-template.json`，把身份工具输出的 method 字段复制进去。

模型只填写：

- 报告、来源快照和提示的路径/hash；
- 主张与来源引用；
- 来源 publisher、发布日期、kind 和上游 lineage key；
- as-of 与预先声明的预算上限；
- 实际加载 locator 与方法/profile hash。

模型不得猜测或自报 token、工具调用数或耗时。宿主结束后从不可变原始会话生成 `resanity.host-receipt.v1`，正式收据只 hash 绑定该宿主收据。

## 机械检查

```sh
python3 <skill-root>/tools/research_check.py <receipt.json> \
  --skill <canonical-skill-root>/SKILL.md \
  --active-skill <actual-loaded-skill>/SKILL.md
```

正式 A/B 增加 `--strict`，要求实际 prompt、宿主收据、原始会话 hash 和来源快照。检查失败时保留稳定错误码，由模型或用户决定如何修正显式文件；检查器不改文件也不自动再跑。

`AUDIT_RECEIPT_OK` 只表示机械合同闭合。它不表示事实正确、研究有效、存在 Alpha、适合交易或达到 PMF。

## 证据机械字段

- `FACT`：声明一手/原始来源，或至少两个不同上游血缘。
- `SINGLE_SOURCE`：只有一个上游血缘，无论有多少转载页面。
- `INFERENCE`：来源支持前提，但推断文本属于模型。
- `HYPOTHESIS`：待检验路径，可以没有来源但必须可证伪。
- `NO_RESULT`：记录具名 locations、queries、date_from、date_to；只闭合该检索边界。
- `INSUFFICIENT`：写明具体 gap。

对否定主张，若裁决依赖具名一手文件的沉默，必须实际读取正文并声明检索对象/层级；读不到就用 `INSUFFICIENT`。只有一手明确否认，或完整证明适用披露规则的主体、事项、重要性阈值与期间，才可形成更强否定。机械检查只核对这些字段是否闭合，不判断模型的语义是否正确。
