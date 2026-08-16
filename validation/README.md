# Resanity 验证入口

> 当前状态：`UNBENCHMARKED_CURRENT`。验证协议不执行研究语义，不把工程通过解释成效果、Alpha 或 PMF。

## 当前 v2

v2 从根因重建为七层：

1. core contract；
2. investing profile；
3. open network；
4. anchor lifecycle；
5. trigger；
6. install identity；
7. same-hash final A/B。

源码仓库入口是 `validation/v2/README.md` 与 `validation/v2/suite.json`。当前仓库只冻结源合同和未来运行入口，没有 v2 语义成绩；npm tarball 不包含内部 suite 和 prompts。

在包含 `.git` 和内部 suites 的源码 checkout 中先运行机械源检查（npm tarball 故意不带内部 prompts）：

```sh
python3 tools/validation_source_check.py
```

需要一次执行测试、Skill 校验、身份、锚只读 smoke 与打包检查时，运行：

```sh
npm run validate:v2 -- --active-skill /actual/loaded/resanity/SKILL.md \
  --host codex --output /tmp/resanity-v2-mechanical-receipt.json
```

它验证 v1 历史文件未漂移、v2 七层与案例资产齐全、trigger 有正反样本、最终 A/B 仍为 `NOT_RUN`。它不调用模型、不评分报告。

## v1 历史基线

`dsh-pilot/` 与 `dsh-full/` 是提交 `746c21d9af3ba76221f16c9ba5c73730b017346b` 冻结的 v1 原始证据和 runner。它们保持原样，只能表述为 v1 历史基线，不能作为 v2 成绩。

旧套件仍可用于复现历史工程合同，但其中投资化 prompt、21 会话矩阵和旧 Skill hash 不得与 v2 混跑或合并计分。

## 正式报告收据

v2 使用 [receipt-template.json](receipt-template.json) 的 `resanity.audit-receipt.v2`。宿主计量仍使用无语义的 [host-receipt-template.json](host-receipt-template.json) `resanity.host-receipt.v1`。

正式检查必须同时传 canonical 与实际加载路径：

```sh
python3 tools/research_check.py <receipt.json> --strict \
  --skill <canonical>/SKILL.md \
  --active-skill <actual-loaded>/SKILL.md
```

## 状态边界

- `VALIDATION_SOURCE_OK`：源合同机械闭合；
- `AUDIT_RECEIPT_OK`：一份报告的机械收据闭合；
- `V2_LAYER_PASS`：某层完成预冻结语义评审；
- `V2_FINAL_AB_PASS`：同 hash、同宿主、强通用基线的最终配对 A/B 达标；
- `UNBENCHMARKED_CURRENT`：最终 A/B 未完成时持续保持。

这些状态都不证明真实收益、Alpha、PMF 或长期认知改善。
