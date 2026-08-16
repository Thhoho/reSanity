已保存快照：[research/passkey-friction-claim-snapshots-2026-07-31.md](/private/tmp/resanity-v2-validation-r5.QWgQrz/open-network-r-codex-gpt-5.5/workspaces/O01-product-passkey/research/passkey-friction-claim-snapshots-2026-07-31.md)

**根结论**

截至 2026-07-31，“passkey 已经显著降低消费者登录摩擦”有较强支持；“已经消除消费者登录摩擦”不成立。证据显示：主流平台和头部服务已可用，采用进入大众阶段，登录速度、成功率和支持事件都有改善；但覆盖不等于实际可用，采用不等于默认使用，恢复、跨设备、旧设备、Windows 同步和站点实现仍保留明显摩擦。

**主张卡 1：技术可用**

主张：passkey 的基础技术已经足以支持无密码消费者登录，但不是自动消除摩擦的完整产品方案。  
观察到什么：WebAuthn Level 3 定义了基于公钥、RP 作用域、用户代理中介的认证模型；passkey 平台认证器支持可发现凭据和用户验证，从而可实现无用户名或无密码登录路径。W3C 文档为 2026 年候选推荐快照。  
可以推出什么：技术层已经具备替代密码的标准化能力。  
不能推出什么：不能推出每个网站都正确实现、每个用户设备都顺畅、或恢复流程无摩擦。  
对决策的影响：支持“技术可用”，但削弱“摩擦已消除”。  
证据边界：`INFERENCE`。来源：W3C WebAuthn Level 3

**主张卡 2：平台覆盖**

主张：消费者主流平台覆盖已广，但默认能力仍不均一。  
观察到什么：passkeys.dev 2026-05-20 设备矩阵显示，Android、ChromeOS、iOS/iPadOS、macOS 已列出 synced passkeys 能力；Windows synced passkeys 标为 planned，Windows 23H2+ 支持跨设备认证客户端；第三方凭据管理器支持也按平台版本不同而异。 Microsoft 文档显示 Windows 11 22H2 + KB5030310 有原生 passkey 管理，23H2 起 OS 级支持 CDA；iOS/iPadOS 不支持与 Windows 的 persistent linking。  
可以推出什么：多数现代消费者设备已有可用路径。  
不能推出什么：不能推出跨 Apple、Google、Microsoft、第三方管理器的体验一致，也不能推出 Windows 用户获得与 iCloud/Google Password Manager 同等的同步体验。  
对决策的影响：平台覆盖支持“可规模部署”，但覆盖差异保留用户摩擦。  
证据边界：`INFERENCE`。

**主张卡 3：用户采用**

主张：passkey 已进入大规模采用，但尚未达到“消费者登录默认被 passkey 接管”。  
观察到什么：FIDO 2026 报告称 5 billion passkeys active use，10 国 11,000 名经常登录线上服务的成年人调查中，90% 熟悉 passkey，75% 至少在部分账户启用。 FIDO Passkey Index 2025 覆盖 Amazon、Google、Microsoft、PayPal、Target、TikTok 等九家早期部署服务商，报告平均 93% 账户 eligible、36% enrolled、26% sign-ins 使用 passkey。 Google 2024 报告其 passkey 已用于超过 10 亿次认证、覆盖超过 4 亿 Google Accounts。  
可以推出什么：采用已经不是实验状态，头部服务中有真实使用。  
不能推出什么：75% “启用过”不能推出日常所有登录都用 passkey；26% sign-ins 在早期部署服务商中也说明多数登录仍走其他方式。  
对决策的影响：强烈支持“摩擦被减少”，不支持“已经消除”。  
证据边界：`INFERENCE`。

**主张卡 4：恢复 / 跨设备体验**

主张：恢复和跨设备是“摩擦未消除”的最弱环节。  
观察到什么：passkeys.dev 的 bootstrapping 指南说明，如果 passkey 调用不成功，RP 应回退到 legacy authentication 和可能的 account recovery；跨设备认证后，建议创建本地 passkey，因为以后会更顺畅。它还提示部分桌面或旧笔记本在 `userVerification=required` 时可能反复要求系统密码。 Apple 文档说明 iCloud Keychain 可恢复，但恢复需要 Apple Account、SMS、设备 passcode，并有锁定和十次失败销毁 escrow 记录的边界。  
可以推出什么：生态已经设计了恢复和跨设备方案，但这些方案仍包含额外步骤、失败路径和平台差异。  
不能推出什么：不能推出用户不会丢失访问权、不会回到密码/短信、或客服恢复需求消失。  
对决策的影响：这是反驳“消除摩擦”的核心证据。  
证据边界：`INFERENCE`。

**主张卡 5：支持成本**

主张：已有证据显示 passkey 能降低登录相关支持成本，但该结论只适用于已部署且上报数据的组织。  
观察到什么：FIDO Passkey Index 2025 报告 passkey 登录平均 8.5 秒，其他方式 31.2 秒；成功率 93% 对比 63%；登录相关 help desk incidents 降低 81%。 Dashlane case study 报告 passkey authentication opportunity 转化率 92%，password autofill opportunity 为 54%，且 passkey 错误和客户问题较少。  
可以推出什么：在成熟实现和已采用用户中，登录摩擦和支持负担明显下降。  
不能推出什么：不能推出所有消费者站点都会获得同等 81% 支持事件下降，也不能推出恢复、设备迁移、教育成本已经消失。  
对决策的影响：支持“降低摩擦”的强版本，但仍不足以证明“消除”。  
证据边界：`INFERENCE`。

**可能性地图**

最可能：passkey 在头部平台和头部消费者服务中显著降低日常登录摩擦，但摩擦转移到启用、恢复、跨设备和例外路径。

次可能：对已启用 passkey 且设备/浏览器/凭据管理器匹配的用户，某些服务上的登录摩擦接近被消除。

self-countercase：如果只观察 Google、Apple 生态内、已启用 passkey 的高频用户，结论会显得更强；但这不是全体消费者登录场景。

**唯一下一验证**

拿一个横跨 Apple、Android、Windows、第三方密码管理器的消费者服务，按真实登录事件分桶：`passkey 成功登录`、`passkey 失败后回退`、`新设备/恢复`、`客服介入`。只需要这一个服务的事件漏斗，就能直接检验“摩擦降低”到底停在日常登录，还是也覆盖恢复和跨设备。
