# Passkey Friction Claim Source Snapshots

As-of cutoff: 2026-07-31
Prepared: 2026-08-16
Scope: consumer login friction; no securities, valuation, or market-pricing framing.

## Snapshot S1: FIDO Alliance, The State of Passkeys 2026

- URL: https://fidoalliance.org/the-state-of-passkeys-2026-global-consumer-and-workforce-report/
- Public date: 2026-05-07.
- Source type: original FIDO research summary.
- Population/method: 11,000 adults who regularly log in to websites, apps, or online services across the US, UK, France, Germany, Australia, Singapore, Japan, South Korea, China, and India; online interviews by Sapio Research in April 2026; reported margin of error +/-0.9pp at 95% confidence.
- Key observations: FIDO reports 5 billion passkeys in active use; 90% consumer familiarity; 75% of consumers have enabled passkeys on at least some accounts.
- Weight: strongest broad consumer adoption source found before the cutoff.
- Boundary: survey and FIDO-reported usage aggregate; does not directly measure all login attempts, all consumers, all sites, recovery failures, or support contact rates.

## Snapshot S2: FIDO Alliance / Liminal, Passkey Index 2025

- URL: https://fidoalliance.org/fido-alliance-launches-passkey-index-revealing-significant-passkey-uptake-and-business-benefits/
- Public date: 2025-10-14.
- Source type: aggregate, anonymized deployment data from nine FIDO member service providers, plus Liminal organization survey.
- Provider scope named by FIDO: Amazon, Google, LY Corporation, Mercari, Microsoft, NTT DOCOMO, PayPal, Target, and TikTok.
- Key observations: average 93% account eligibility, 36% account passkey enrollment, and 26% of all sign-ins using passkeys among contributing providers; passkey login averaged 8.5 seconds versus 31.2 seconds for other methods; passkey success rate 93% versus 63% for other methods; 81% reduction in login-related help desk incidents.
- Weight: strongest direct friction/performance/support-cost source found before the cutoff.
- Boundary: early-adopting large providers, aggregate and anonymized; not a representative sample of all consumer services; details by provider, recovery flow, denominator construction, and variance are not visible in the public summary.

## Snapshot S3: passkeys.dev, Device Support

- URL: https://passkeys.dev/device-support/
- Public/update date shown: 2026-05-20.
- Source type: developer implementation reference maintained by members of the W3C Web Identity & Credentials Adoption CG and FIDO Alliance.
- Key observations: default out-of-box capabilities vary by OS/browser. Synced passkeys are listed for Android 9+, ChromeOS 129+, iOS/iPadOS 16+, macOS 13+, browser extensions on Ubuntu, and planned for Windows. Cross-device authentication support is asymmetric: Android/iOS can act as authenticators; Windows 23H2+ can act as client; third-party credential-manager support appears at different OS versions, including Windows 25H2+.
- Weight: strongest compact platform coverage map.
- Boundary: capability matrix, not measured real-world availability; installed OS versions, browser versions, enterprise policy, device hardware, and chosen credential provider can change the user experience.

## Snapshot S4: passkeys.dev, Bootstrapping

- URL: https://passkeys.dev/docs/use-cases/bootstrapping/
- Public/update context: available before cutoff.
- Source type: developer implementation guidance.
- Key observations: conditional UI requires relying-party implementation. If the passkey call does not succeed, the site should perform legacy authentication and may include account recovery. After cross-device authentication, the guidance recommends offering creation of a local passkey because future use is more seamless. It also warns that requiring user verification on some desktops or older laptops can produce repeated system-password prompts.
- Weight: strongest source for residual recovery/cross-device friction in the product flow.
- Boundary: guidance rather than deployment measurement; does not quantify consumer failure rates.

## Snapshot S5: Apple Support, About the security of passkeys

- URL: https://support.apple.com/en-us/102195
- Public date: 2024-09-16.
- Source type: first-party platform support documentation.
- Key observations: Apple states passkeys sync across Apple devices through iCloud Keychain; iCloud Keychain is end-to-end encrypted and recoverable if all devices are lost. Recovery requires Apple Account authentication, SMS to registered phone number, and device passcode; after several failed attempts the record is locked, and after ten failed attempts the escrow record is destroyed.
- Weight: strong first-party evidence for Apple recovery model and residual recovery constraints.
- Boundary: Apple ecosystem only; does not prove recovery outcomes across other platforms or mixed-device households.

## Snapshot S6: Microsoft Learn, Reference for passkeys on Windows

- URL: https://learn.microsoft.com/en-us/windows/apps/develop/security/reference
- Last updated: 2025-02-19.
- Source type: first-party platform developer documentation.
- Key observations: Windows 11 22H2 with KB5030310 or later has native passkey management; Windows 11 23H2 supports FIDO cross-device authentication globally at OS level; Android-to-Windows persistent linking is available, while iOS/iPadOS do not support persistent linking. If biometrics are unavailable, Windows passkey creation/authentication falls back to Windows Hello PIN.
- Weight: strong first-party evidence that Windows support is real but not uniformly equivalent to Apple/Android sync.
- Boundary: Windows platform only; page itself notes authorization limitations in retrieved view, but relevant public content is visible.

## Snapshot S7: Google, Passkeys update

- URL: https://blog.google/innovation-and-ai/technology/safety-security/google-passkeys-update-april-2024/
- Public date: 2024-05-02.
- Source type: first-party product announcement/data.
- Key observations: Google reported more than 1 billion passkey authentications across over 400 million Google Accounts, passkeys 50% faster than passwords, and daily passkey usage for Google Accounts exceeding SMS OTP plus authenticator-app OTP combined.
- Weight: strong single-provider scale and usage source.
- Boundary: Google Accounts only; does not imply all consumer services or all account recovery paths are frictionless.

## Snapshot S8: Google for Developers / Dashlane case study

- URL: https://developers.google.com/identity/passkeys/case-studies/dashlane
- Last updated: 2025-05-19.
- Source type: vendor case study with product telemetry.
- Key observations: Dashlane reported 92% conversion on passkey authentication opportunities versus 54% for password autofill opportunities; 63% passkey registration conversion versus about 25% password-save suggestion conversion; 6.8% average weekly growth of passkeys saved and used on web; few passkey errors and few customer questions.
- Weight: useful direct user-flow telemetry.
- Boundary: Dashlane user base and Dashlane UI; likely enriched for password-manager users; not representative of all consumers.
