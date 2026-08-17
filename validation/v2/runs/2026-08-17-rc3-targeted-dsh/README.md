# Resanity 0.2.0 pre-publication DSH forward validation

Status: `TARGETED_FORWARD_PASS_4_OF_4`. Method status remains
`UNBENCHMARKED_CURRENT`.

The pre-publication `2.0.0-rc.3` candidate introduced a declared claim/source temporal compatibility gate after RC2
O01 used post-as-of live product pages to backfill historical recovery and
platform state. A fresh isolated DSH profile loaded the new canonical Skill
SHA-256 `07ccd997071f1a2e555735fb1a980aec5e9279e902a16911590da61f07375709`.
The baseline and candidate profiles differed only by the `resanity` treatment;
automatic retries and subagents were disabled.

Four new sessions ran concurrently through `deepseek-official/deepseek-v4-pro`
at reasoning effort `max`, with new workspaces, raw sessions, prompts, source
snapshots, host receipts, and zero automatic retries. All four were mechanically
complete, invoked Resanity exactly once, produced a readable stdout report, and
needed no recovered workspace report:

- `C03-technical-debug`: 1 tool execution, 98.338 seconds, no external source.
- `O01-product-passkey`: 26 tool executions, 10 source files, 595.397 seconds.
- `O02-policy-outcome`: 28 tool executions, 8 source files, 627.722 seconds.
- `O03-investing-exposure`: 26 tool executions, 10 source files, 697.810 seconds.

Manual semantic review passed all four cases:

- `C03` rejects the universal upload-failure claim, keeps version, regional
  supplier, and interaction hypotheses separate, limits the failed feature-flag
  rollback to its actual coverage, and gives one diagnostic action without
  investment-profile leakage.
- `O01` fixes the RC2 blocker. Adoption, recovery/cross-device, platform, and
  support-cost claims are carried only by dated 2024-2026 FIDO/Google original
  publications or versioned PDFs. Undated current pages and unavailable archive
  snapshots are not used to backfill 2026-07-31 state. The report keeps the
  missing consumer recovery metric explicit.
- `O02` relies on the original DOE Program Notices 26-1, 26-2, and 26-3, each
  explicitly effective 2026-05-29, for the rules-still-changing finding. The
  live DOE tracker and post-as-of Georgia updates do not carry historical state;
  missing launch and issuance totals remain `INSUFFICIENT`, not zero.
- `O03` keeps company-level delivery, revenue, gross margin, and cash facts
  separate from unreported liquid-cooling attribution. Liquid-cooling exposure
  and relative pricing remain `NOT_EVALUABLE`; the dated single-source price
  input is disclosed and not upgraded to a relative-pricing conclusion.

The complete collection remains under
`/private/tmp/resanity-v2-rc3-dsh.z4P543/targeted`; hashes and review findings are
frozen in `review-summary.json`. This is a targeted repair and adjacent-regression
line, not the full same-hash A/B, broad effectiveness evidence, Alpha/PMF proof,
or a method-stability gate. The formal `0.2.0` release keeps the same frozen
Skill/profile identity; changing the package version and release documentation
does not transfer evidence from a different method hash or imply broad validity.
