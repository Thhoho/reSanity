# Passkey Source Snapshots

As-of boundary: 2026-07-31.
Snapshot created: 2026-08-16 Asia/Shanghai.
Scope: sources used for the load-bearing claims in `passkey-friction-audit.md`.

## E1 - Apple Support: About the security of passkeys

- Publisher: Apple Support
- Public date: 2024-09-16
- URL: https://support.apple.com/en-us/102195
- Kind: first-party product/security documentation
- Lineage key: apple-support-passkey-security-2024-09-16
- Key observed facts:
  - Apple describes passkeys as password replacements designed for passwordless sign-in, with public-key cryptography and no private key disclosed to the server.
  - Apple states passkeys sync across Apple devices through iCloud Keychain.
  - Apple states passkeys are recoverable through iCloud Keychain escrow if all associated devices are lost, but recovery requires Apple account authentication, SMS response, and device passcode; after failed attempts the record may lock and then be destroyed.

## E2 - Chrome for Developers: Chrome to sync passkeys on Google Password Manager between desktop and Android

- Publisher: Google / Chrome for Developers
- Public date: 2024-09-19
- URL: https://developer.chrome.com/blog/passkeys-gpm-desktop?hl=en
- Kind: first-party product documentation / product update
- Lineage key: google-chrome-gpm-passkey-sync-2024-09-19
- Key observed facts:
  - Before the update, Chrome passkeys had important sync boundaries: iCloud Keychain synced within Apple devices, Android GPM synced across Android, and Windows passkeys were saved locally to Windows Hello.
  - The update allows signed-in Chrome on macOS, Windows, Linux, and ChromeOS to create passkeys in Google Password Manager and use them across those platforms, with requirements such as TPM on Windows and beta status for ChromeOS at publication.
  - On a new device, users need either a Google Password Manager PIN or Android device unlock method to access synced passkeys.

## E3 - Google for Developers: Passkey support on Android and Chrome

- Publisher: Google for Developers
- Last updated: 2025-05-19 UTC
- URL: https://developers.google.com/identity/passkeys/supported-environments?hl=en
- Kind: first-party product/platform support documentation
- Lineage key: google-android-chrome-passkey-support-2025-05-19
- Key observed facts:
  - Google states passkeys are managed by password managers and synchronized across devices.
  - Google Password Manager stores and synchronizes passkeys on Android and Chrome across multiple operating systems.
  - Android apps support passkeys on Android 9 or higher through Credential Manager; Android 14 or higher allows users to choose other passkey providers.
  - Chrome supports cross-device authentication across platforms, and Chrome on Windows, macOS, Linux, Android, and ChromeOS supports passkeys.

## E4 - Microsoft Learn: Reference for passkeys on Windows

- Publisher: Microsoft Learn
- Last updated: 2025-02-19
- URL: https://learn.microsoft.com/en-us/windows/apps/develop/security/reference
- Kind: first-party product/platform support documentation
- Lineage key: microsoft-windows-passkey-reference-2025-02-19
- Key observed facts:
  - Microsoft states passkeys can be used in all supported Windows client versions.
  - Native passkey management is available starting with Windows 11 version 22H2 plus KB5030310 or later.
  - Windows 11 version 23H2 supports FIDO Cross-Device Authentication at OS level for apps and browsers.
  - Windows Hello PIN is a fallback when facial recognition or fingerprint recognition is not configured or available.

## E5 - FIDO Alliance: State of Passkeys 2026 release

- Publisher: FIDO Alliance
- Public date: 2026-05-07
- URL: https://fidoalliance.org/fido-alliance-reports-accelerating-global-passkey-adoption-on-world-passkey-day-2026/?query-cdbd12d0-page=3
- Kind: original survey release and adoption estimate
- Lineage key: fido-state-passkeys-2026-release-2026-05-07
- Key observed facts:
  - FIDO reports research covering 11,000 consumers and 1,400 enterprise decision-makers across ten countries, conducted by Sapio Research in April 2026.
  - Reported consumer figures: 90% aware of passkeys; 75% enabled a passkey on at least one account; 49% use passkeys regularly when available.
  - FIDO estimates 5 billion passkeys in use worldwide, based on public data plus internal deployment data.
  - Friction remains in the baseline environment: 47% of consumers say they are likely to abandon a purchase or sign-in when they cannot remember their password.
  - Workforce respondents that deployed passkeys report fewer password reset tickets at 35%, but 57% of organizations still rely on phishable primary day-to-day employee sign-in methods.

## E6 - FIDO Alliance: Passkey Index 2025 launch

- Publisher: FIDO Alliance
- Public date: 2025-10-14
- URL: https://fidoalliance.org/fido-alliance-launches-passkey-index-revealing-significant-passkey-uptake-and-business-benefits/?query-cdbd12d0-page=2
- Kind: original aggregate deployment/utilization data from participating service providers
- Lineage key: fido-passkey-index-2025-2025-10-14
- Key observed facts:
  - The index aggregates anonymized data from nine FIDO member organizations that deployed passkeys for one to three years, including Amazon, Google, LY Corporation, Mercari, Microsoft, NTT DOCOMO, PayPal, Target, and TikTok.
  - In the participating services, average account eligibility was 93%, account enrollment was 36%, and 26% of sign-ins used passkeys.
  - Reported passkey sign-in performance: 8.5 seconds average sign-in time versus 31.2 seconds for other methods; 93% success rate versus 63% for other methods.
  - Reported operational effect: 81% reduction in login-related help desk incidents among index companies.

## E7 - FIDO Alliance: World Passkey Day 2025 consumer study and availability release

- Publisher: FIDO Alliance
- Public date: 2025-05-01
- URL: https://fidoalliance.org/fido-alliance-champions-widespread-passkey-adoption-and-a-passwordless-future-on-world-passkey-day-2025/?query-cdbd12d0-page=3
- Kind: original consumer survey release and availability estimate
- Lineage key: fido-world-passkey-day-2025-release-2025-05-01
- Key observed facts:
  - SurveyMonkey online poll conducted April 13-14, 2025 among 1,389 adults in the U.S., U.K., China, South Korea, and Japan, weighted by demographics; modeled error estimate +/- 3.5 percentage points.
  - Reported consumer figures: 74% aware of passkeys; 69% enabled passkeys on at least one account; among those who used passkeys, 38% enabled them whenever possible.
  - FIDO reported passkey availability reached 48% of the world's top 100 websites, calculated from public information and FIDO deployment data.

## E8 - FIDO Alliance: Microsoft case study

- Publisher: FIDO Alliance case study with Microsoft-provided deployment metrics
- Public date: 2025-04-25
- URL: https://fidoalliance.org/case-study-microsoft/
- Kind: deployment case study / original operator-reported metrics
- Lineage key: fido-microsoft-case-study-2025-04-25
- Key observed facts:
  - Microsoft Account began rolling out passkey support across consumer-facing services in 2023.
  - Microsoft reports more than one million passkeys registered daily at the time of the case study.
  - Microsoft reports passkey users were three times more successful than password users, with 95% success versus 30%; passkey sign-ins were eight times faster than password plus MFA flows.
  - Microsoft reports passwordless-preferred UX reduced password use by more than 20%.
