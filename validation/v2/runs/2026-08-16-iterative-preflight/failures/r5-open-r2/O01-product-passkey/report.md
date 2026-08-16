已保存来源快照：[source-snapshots.md](/private/tmp/resanity-v2-validation-r5.QWgQrz/open-network-r2-codex-gpt-5.5/workspaces/O01-product-passkey/research/passkey-friction-audit/source-snapshots.md)。

**根结论**

截至 `2026-07-31`，“passkey 已经消除消费者登录摩擦”不能成立。更可证的版本是：passkey 已在主流平台和部分大型服务中显著降低已注册用户、受支持设备和受支持流程里的登录摩擦；但尚不能推出“消费者登录摩擦已经被消除”。

**承重主张卡**

主张：技术可用性已足够广，能支撑大规模消费者使用。  
观察到什么：Apple 2023-05-15 文档列出 iOS 16、macOS Ventura、Safari 16 等支持，并说明可用 Face ID/Touch ID 或设备口令认证；Microsoft 2025-02-19 文档称 Windows 11 22H2+ 有原生 passkey 管理，Windows 11 23H2 支持系统级跨设备认证；Android 2023-10-25 宣布 Credential Manager 统一密码、passkey 和联合登录。Apple 还说明恢复仍由应用/网站自行维持。    
可以推出什么：主流平台已具备真实可部署基础。  
不能推出什么：不能推出所有消费者、所有浏览器、所有应用内 WebView 和所有恢复场景都无摩擦。  
对决策的影响：支持“技术可用”，不支持“摩擦已消除”。  
证据边界：`INFERENCE`

主张：平台覆盖仍有重要边界，尤其在跨设备、第三方管理器和恢复体验上。  
观察到什么：passkeys.dev 2026-05-20 矩阵显示默认能力因 Android、ChromeOS、iOS/iPadOS、macOS、Ubuntu、Windows 而异；Windows 上 synced passkeys 仍标为 planned，第三方 credential manager 支持也按系统版本分化。Microsoft 文档还指出 Android 到 Windows 11 23H2+ 可 persistent linking，但 iOS/iPadOS 不支持 persistent linking。   
可以推出什么：平台覆盖已广，但体验不一致。  
不能推出什么：不能把“多数主流平台可用”等同于“跨生态无缝”。  
对决策的影响：削弱“已经消除”的绝对表述。  
证据边界：`FACT`

主张：用户采用已进入大规模阶段，但没有达到可称为“摩擦消除”的普遍替代。  
观察到什么：Google 2024-05-02 报告 passkey 已用于超过 10 亿次认证、覆盖超过 4 亿个 Google Account；FIDO 2026-05-07 报告估计全球 50 亿 passkey active use，10 国消费者调查中 90% 熟悉、75% 至少在部分账户启用。   
可以推出什么：采用不是小众试验，已具备规模。  
不能推出什么：不能推出消费者主要登录场景已全面改用 passkey，也不能推出未启用者的摩擦已被解决。  
对决策的影响：支持“显著推进”，但不支持“已经消除”。  
证据边界：`SINGLE_SOURCE`

主张：在已支持且已触发 passkey 的流程中，登录效率和成功率明显更好。  
观察到什么：Dashlane 2023-10-24 案例显示 web passkey 认证机会转化率 92%，自动密码登录机会 54%；passkey 保存机会 63%，密码保存建议约 25%。FIDO Passkey Index 2025-10-14 汇总 9 家成员组织数据，称 passkey 登录平均 8.5 秒，其他方式 31.2 秒；成功率 93% 对 63%。   
可以推出什么：在这些样本和定义下，passkey 可大幅降低登录流程摩擦。  
不能推出什么：不能推出所有消费者服务都会复现这些结果；FIDO Index 是匿名聚合，Dashlane 是单一 operator case。  
对决策的影响：这是最强的支持证据，但仍只能支持“降低”，不是“消除”。  
证据边界：`INFERENCE`

主张：支持成本可能下降，但公开证据不足以证明消费者登录支持成本已系统性消失。  
观察到什么：FIDO Passkey Index 报告 login-related help desk incidents 降低 81%；Dashlane 报告 passkey 错误和客户问题不多，并同时列出多种可能解释。   
可以推出什么：已有部署者看到支持负担下降。  
不能推出什么：不能推出恢复、换机、账号丢失、跨生态迁移等支持需求已消失。  
对决策的影响：支持“支持成本改善”，但保留关键不确定性。  
证据边界：`INFERENCE`

**可能性地图**

最可能：passkey 已经把“已注册、设备支持、服务实现良好”的消费者登录摩擦显著压低。  
次可能：对大型平台用户，passkey 正在成为常用登录方式，但仍与密码、OTP、恢复邮件并存。  
较弱可能：在所有消费者场景中，passkey 已经消除登录摩擦。公开证据不足，且平台差异和恢复设计直接反驳该强表述。

**唯一下一验证**

获取一个或多个主流消费者服务在 `2026-07-31` 前已存在的、按日期切片的登录漏斗原始日志：passkey enrollment、passkey attempt、success、fallback、account recovery、support contact，并按平台/浏览器/新设备/换机/丢设备分组。这个验证最直接裁决“降低摩擦”与“消除摩擦”的差别。
