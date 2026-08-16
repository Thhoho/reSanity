# Passkey Friction Claim - Source Snapshots

As-of boundary: 2026-07-31.
Snapshot created: 2026-08-16 Asia/Shanghai.
Scope: dated public sources only; no undated mutable current pages and no post-as-of retrospective data used to backfill the as-of judgment.

## E1 - Apple Developer News

Publisher: Apple Developer
Title: Q&A with the passkeys team
Publication date: 2023-05-15
URL: https://developer.apple.com/news/?id=21mnmxow
Line refs from browser snapshot: turn4view3 L130-L159
Kind: first-party product documentation / implementation Q&A
Lineage key: apple-developer-passkeys-qa-2023-05-15

Key facts preserved:
- Apple states passkeys replace passwords and offer faster, easier, more secure sign-in for apps and websites.
- Supported Apple baseline: iOS 16 on iPhone 8+, iPadOS 16 on listed iPads, macOS Ventura, tvOS 16; Safari 16 on macOS Monterey and Big Sur.
- If biometrics are unavailable, device passcode or system password can authenticate.
- Lost-device section states passkeys are end-to-end encrypted through iCloud Keychain and require biometrics or device passcode to decrypt.
- Account recovery remains independent of authentication; apps and websites can keep existing recovery methods, such as email links.

## E2 - Microsoft Learn

Publisher: Microsoft Learn
Title: Reference for passkeys on Windows
Last updated: 2025-02-19
URL: https://learn.microsoft.com/en-us/windows/apps/develop/security/reference
Line refs from browser snapshot: turn4view0 L24-L43, L85
Kind: first-party product documentation
Lineage key: microsoft-windows-passkeys-reference-2025-02-19

Key facts preserved:
- Passkeys can be used in all supported versions of Windows clients.
- Windows 11 version 22H2 with KB5030310 or later has native passkey management.
- Windows 11 version 23H2 supports FIDO Cross-Device Authentication globally at OS level for all apps and browsers.
- Persistent linking is available between Android authenticators and Windows 11 23H2+; iOS/iPadOS do not support persistent linking.
- Windows Hello uses available screen unlock for verification; PIN fallback is available when biometrics are not configured or available.

## E3 - Android Developers Blog

Publisher: Android Developers Blog
Title: Simple and secure sign-in on Android with Credential Manager and passkeys
Publication date: 2023-10-25
URL: https://android-developers.googleblog.com/2023/10/simple-and-secure-sign-in-on-android-with-credential-manager-passkeys.html
Line refs from browser snapshot: turn4view1 L21-L44
Kind: first-party product documentation / launch announcement
Lineage key: google-android-credential-manager-passkeys-2023-10-25

Key facts preserved:
- Credential Manager public release was announced for 2023-11-01.
- Android Credential Manager unifies passwords, passkeys, and federated sign-in in one interface.
- Google describes passkey sign-in as selecting the account and confirming with device face scan, fingerprint, or PIN.
- The post states apps reduced sign-in time by 50% after implementing passkeys.
- Uber and WhatsApp were named as already integrated with Credential Manager and passkeys.

## E4 - passkeys.dev Device Support

Publisher: passkeys.dev, by members of the W3C Web Identity & Credentials Adoption CG and FIDO Alliance
Title: Device Support
Last updated: 2026-05-20
URL: https://passkeys.dev/device-support/
Line refs from browser snapshot: turn4view4 L0-L20, L68-L93, L168-L170
Kind: implementation reference matrix
Lineage key: passkeys-dev-device-support-2026-05-20

Key facts preserved:
- The matrix represents default capabilities out of the box.
- Synced passkeys are listed for Android 9+, ChromeOS 129+, iOS/iPadOS 16+, macOS 13+, browser extensions on Ubuntu, and planned on Windows.
- Cross-device authentication client support is listed for Android 9+, ChromeOS 108+, iOS/iPadOS 16+, macOS 13+, Chrome/Edge on Ubuntu, and Windows 11 23H2+.
- Third-party credential manager support is listed for Android 14+, iOS/iPadOS 17+, macOS 14+, browser extensions on ChromeOS/Ubuntu, and Windows 11 25H2+.

## E5 - Google Security Blog

Publisher: Google Online Security Blog
Title: Your Google Account allows you to create passkeys on your phone, computer and security keys
Publication date: 2024-05-02
URL: https://security.googleblog.com/2024/05/passkeys-on-your-phone-computer-and-security-keys.html
Line refs from browser snapshot: turn1search1
Kind: first-party product adoption data
Lineage key: google-account-passkey-authentications-2024-05-02

Key facts preserved:
- Google reported more than 1 billion passkey authentications across over 400 million Google Accounts.
- Google described passkeys as usable in Google Account sign-in and storable on phone, computer, or security keys.

## E6 - Google Developers Blog / Dashlane Case Study

Publisher: Google Developers Blog; subject data from Dashlane
Title: Password manager Dashlane sees 70% increase in conversion rate for signing-in with passkeys compared to passwords
Publication date: 2023-10-24
URL: https://developers.googleblog.com/en/password-manager-dashlane-sees-70-increase-in-conversion-rate-for-signing-in-with-passkeys-compared-to-passwords/
Line refs from browser snapshot: turn3view2 L15-L22, L39-L70
Kind: product case study with original operator metrics
Lineage key: dashlane-passkey-conversion-case-2023-10-24

Key facts preserved:
- Dashlane had over 18 million users and 20,000 businesses in 180 countries.
- Passkey authentication opportunity conversion on web was 92% vs 54% for automatic password sign-in opportunities.
- Passkey registration opportunity conversion was 63% vs around 25% for password save suggestions.
- Dashlane observed 6.8% average weekly growth of passkeys saved and used on the web.
- Dashlane reported few passkey errors and few customer questions; the post explicitly lists several possible explanations.

## E7 - FIDO Alliance Passkey Index Launch

Publisher: FIDO Alliance
Title: FIDO Alliance Launches Passkey Index, Revealing Significant Passkey Uptake and Business Benefits
Publication date: 2025-10-14
URL: https://fidoalliance.org/fido-alliance-launches-passkey-index-revealing-significant-passkey-uptake-and-business-benefits/
Line refs from browser snapshot: turn3view1 L126-L158
Kind: aggregate original member data / methodology disclosure
Lineage key: fido-passkey-index-2025-10-14

Key facts preserved:
- Index data came from nine FIDO member organizations, including Amazon, Google, LY Corporation, Mercari, Microsoft, NTT DOCOMO, PayPal, Target, and TikTok.
- Average account eligibility was 93%; enrolled accounts were 36%; 26% of all sign-ins used passkeys.
- Passkey sign-ins averaged 8.5 seconds vs 31.2 seconds for other methods, a 73% reduction.
- Passkey sign-in success was 93% vs 63% for other methods.
- Login-related help desk incidents fell 81%.
- Methodology: confidential survey of nine FIDO member organizations, aggregate and anonymized.

## E8 - FIDO Alliance State of Passkeys 2026

Publisher: FIDO Alliance
Title: The State of Passkeys 2026: Global Consumer and Workforce Report
Publication date: 2026-05-07
URL: https://fidoalliance.org/the-state-of-passkeys-2026-global-consumer-and-workforce-report/
Line refs from browser snapshot: turn3view0 L30-L39
Kind: original commissioned survey / published methodology summary
Lineage key: fido-state-of-passkeys-2026-05-07

Key facts preserved:
- FIDO reported an estimated 5 billion passkeys in active use worldwide.
- Consumer awareness was 90%; 75% had enabled passkeys on at least some accounts.
- Consumer survey: 11,000 adults who regularly log in to websites, apps, or online services across ten countries, conducted online by Sapio Research in April 2026; margin of error +/- 0.9 percentage points at 95% confidence.
