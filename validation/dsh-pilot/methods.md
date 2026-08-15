# 冻结方法身份

以下是设计验证方案时观察到的对象，不替代运行当天复核。

| 臂 | 路径 | Git commit | `SKILL.md` SHA-256 |
|---|---|---|---|
| `T` | `/Users/xiaweiqi/Documents/resanity` | `0202042b3e95c7be40ac2109f914e99f07447556` + 未提交候选改动 | `8d9dfb8ada23a5390ed89b2f9d3b0fe426d37bce068baac3b5f69894d26e293d` |
| `L` | `/Users/xiaweiqi/Documents/trade-nothing` | `186bc8cab05117046c3963143bf7b16a17152a04` | `cd58fa908f59cd97fa8542d05f768a084ef56f2f4a20d9347836ade700ab7d8c` |

运行前复核：

```bash
shasum -a 256 /Users/xiaweiqi/Documents/resanity/SKILL.md
shasum -a 256 /Users/xiaweiqi/Documents/trade-nothing/SKILL.md
git -C /Users/xiaweiqi/Documents/resanity status --short
git -C /Users/xiaweiqi/Documents/trade-nothing status --short
```

`T` 当前是尚未提交的候选工作树，因此 commit 不能单独代表方法身份；本次以 `SKILL.md` hash 加完整工作树快照为准。验证期间任何 Skill 正文变化都产生新版本，已有结果不得沿用。

当前 final T runner 还会机械冻结实际随 Skill 暴露的三个辅助文件，避免只锁正文却混入不同工具版本：

| 文件 | SHA-256 |
|---|---|
| `scripts/free_market_observations.py` | `407689f7db484503c7934f79d79aa1b1bbe23f07bd7ed5e75eeed0f519cffb6d` |
| `scripts/tier1_providers.py` | `296276e3adb2a3cfd2233a5017c9677e0858ab2eca115b315aebb8a17cdaaa1e` |
| `tools/research_check.py` | `39a8c5e643bdd69140fab22bfd1da2de457e19a80c9673c1b93c8e9f7d4741f5` |

四个 `T` prompt 也由 [run-final-t.sh](run-final-t.sh) 内置 hash 冻结；运行目录的 `method-manifest.sha256` 和各题 `run-meta.json` 是本次实际安装副本的收据。
