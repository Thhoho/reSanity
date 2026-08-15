# 完整验证评分卡

## 1. 宿主门禁

直接从 `summary.json` 与每行 `host/run-meta.json` 抄录，不接受报告自报：

| Run | 一次完成 | Skill=1 | 环境 | 预算 | 写入契约 | 原始会话 | 结果 |
|---|---|---|---|---|---|---|---|

任一失败保留原始结果，不补跑、不人工改报告。

## 2. Contract / Longitudinal

逐项对照 [semantic-gates.md](semantic-gates.md)，每行只记 `PASS / FAIL / NOT_AUDITED` 和一条可定位证据。`N07/N08` 额外记录根事实结论是否一致。A01 额外保存 T0/T1/T2 锚文件 diff。

## 3. Field P0 闸门

对每题最承重 3 条事实逐条用截至 as-of 的一手/原始来源核验：

| 检查项 | 结果 | URL、发布日期与影响 |
|---|---|---|
| 决定性事实错误 | PASS / P0 | |
| 遗漏会改变根结论/行动的重大官方披露 | PASS / P0 | |
| 使用 as-of 之后的信息 | PASS / P0 | |
| 同源转载或传闻升级为 FACT | PASS / P0 | |
| 披露沉默升级为现实否定/经济零值 | PASS / P0 | |
| 编造客户、订单、收入、产能、价格或估值 | PASS / P0 | |

P0 只用于会改变根结论或真实行动的独立根因；其余重大问题记 `MAJOR_NON_P0`，同一根因不重复计数。

## 4. Field 决策效用（每项 0–2，总分 16）

| 维度 | 分数 | 证据/理由 |
|---|---:|---|
| 根结论清楚且受最弱证据约束 | | |
| 承重事实与最弱环节找对 | | |
| 因果链到公司收入/利润/现金 | | |
| 事实、叙事、定价严格分开 | | |
| 反证/替代解释真的能改变判断 | | |
| 价格未知时诚实降级，不制造 setup | | |
| 下一验证低成本、具名、有触发器 | | |
| 来源日期、对象层级和血缘可追溯 | | |

不要奖励篇幅、表格、引用数、术语或“看起来完整”。

## 5. 成本分布

分别统计 contract、field、longitudinal 的中位数与 p90：非缓存 token、工具调用、Web 搜索、墙钟、失败率。不要只看均值，也不要把缓存 token 与非缓存 token 混在一起。

## 6. 允许的结论

- `FULL_T_REGRESSION_PASS`：全部宿主门禁 + contract 8/8 + longitudinal 3/3 + field 无 P0 且至少 8/10 达到 12/16。
- `MECHANICAL_PASS_SEMANTIC_FAIL`：外壳闭合但任一语义硬门禁失败。
- `INCOMPLETE_RUN`：少任一行、环境漂移、session 不唯一或人工补跑。
- `UNBENCHMARKED_CURRENT`：未完成强通用提示的同 hash 配对 A/B；即使 `FULL_T_REGRESSION_PASS` 也继续保持。
