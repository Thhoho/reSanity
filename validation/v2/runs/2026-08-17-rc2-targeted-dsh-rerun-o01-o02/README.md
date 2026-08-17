# Resanity 2.0.0-rc.2 authorized O01/O02 DSH rerun

Status: `TARGETED_RERUN_ONE_PASS_ONE_FAIL`. Method status remains
`UNBENCHMARKED_CURRENT`.

After the operator restored DeepSeek balance and explicitly authorized a rerun,
fresh O01 and O02 sessions used the unchanged RC2 Skill hash
`0704f56286ad6de61ba9c6e1954fb7b38a0c0a8e02f22bfc1ede5422a857c381`.
The sessions ran concurrently through `deepseek-official/deepseek-v4-pro` at
reasoning effort `max`, with zero automatic retries and new workspaces,
session stores, prompts, raw sessions, and receipts. Neither session received
the earlier provider quota error.

Both sessions were mechanically complete:

- `O01-product-passkey`: 30 tool executions, 27 source files, one Resanity
  invocation, no timeout, retry, budget denial, or protocol leak.
- `O02-policy-outcome`: 30 tool executions, 15 source files, one Resanity
  invocation, no timeout, retry, budget denial, or protocol leak.

Manual semantic review produced one pass and one fail:

- `O02-policy-outcome` passes. Dated DOE Program Notices 26-1, 26-2, and 26-3
  are all effective 2026-05-29 and directly describe already-launched,
  not-yet-launched, or conditional-award jurisdictions. This is discriminating
  as-of evidence against the nationwide-completion claim. The report separately
  keeps absent issuance and installation results `INSUFFICIENT` and does not
  treat official silence as proof.
- `O01-product-passkey` fails the task's explicit as-of source boundary. Its
  main verdict is independently supported by dated primary deployment data
  (93% eligible, 36% enrolled, 26% of sign-ins), but the recovery and
  cross-ecosystem sections use Apple and Microsoft live documents captured on
  2026-08-17 and a FIDO specification index captured after the 2026-07-31
  as-of. The report labels those capture dates yet still uses the pages as
  direct historical evidence. Current undated product pages cannot be used to
  backfill the requested historical state without a dated version or archive.

Across the frozen RC2 targeted set, C03, O02, and O03 pass while O01 fails.
The cumulative result is 3/4 semantic passes, not a stable-release gate or a
final A/B. No additional rerun, Skill edit, tag, push, or publish occurred.
