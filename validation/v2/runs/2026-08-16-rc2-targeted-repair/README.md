# Resanity 2.0.0-rc.2 targeted repair

Status: `RC2_LOCAL_RELEASE_CANDIDATE_TARGETED_VALIDATION_FAIL`. Method status remains
`UNBENCHMARKED_CURRENT`.

## Scope

RC2 narrows four defects found by the frozen RC1 three-role blind panel without adding a
research state machine or case-specific answers:

1. Delivery is terminal and user-readable even when a write or budget fails. DSH collection
   runners now mark leaked tool protocol as `report_tool_protocol_leak` instead of complete.
2. Possibility maps separate compatible evidence from discriminating evidence; hypotheses stay
   co-active until a falsifying observation or effective, scoped, sensitive experiment can rank them.
3. Saved primary sources must be read for relevant sections, tables, and attachments before a
   report claims a measure is absent; dated source labels govern standards and product status.
4. The same-lineage requirement now explicitly forbids calling aggregate company backlog,
   period revenue, profit, and cash a closed order-to-cash chain at consolidated level.

## Frozen identity

- canonical `SKILL.md`: `0704f56286ad6de61ba9c6e1954fb7b38a0c0a8e02f22bfc1ede5422a857c381`
- core profile: `76c184f2f873a975b0327b15288ae483600fd66b3000214966741647fc2838da`
- investing profile: `3a1f7f9f8d2b5ae695753efd011738cf24acf4841e599756fd79a53cd1895de8`
- anchors profile: `71e0097037831ef836841242f3e57931d0af6cb28f1b3d0ccfb351728ad80faa`
- formal-audit profile: `f1e7997e21fd5fab6625b52d1cabb1dee4324cbecaa8b1360f59f03ced61b3aa`

## Completed gates

- `npm test`: plugin, budget guard, and 62 Python tests passed.
- Skill Creator `quick_validate.py`: passed.
- v1 validation source contract: 66 files, zero drift.
- RC2 tarball install identity: canonical and active Skill hashes matched; DSH profile-pair dry-run passed.
- RC1 O02 failed output replay: now returns `report_tool_protocol_leak`.
- package dry-run: 27 files; internal `validation/v2` corpus excluded.

## Behavior boundary

After explicit authorization, a fresh four-case DSH run launched C03/O01/O02/O03 with the same
model, budgets, neutral task prompts, zero automatic retries, and the isolated RC2 tarball. C03 and
O03 completed and passed manual semantic review. O01 and O02 ended after DeepSeek returned
`QUOTA: Insufficient Balance`; O01 produced no report, while O02 left a recoverable formal file but
did not complete terminal host delivery. See `../2026-08-17-rc2-targeted-dsh/` for the bound hashes
and review.

After an explicitly authorized same-identity rerun, O02 passed and O01 failed its as-of source
boundary. The cumulative RC2 targeted result is C03/O02/O03 pass and O01 fail: 3/4 semantic
passes. RC2 is a local release candidate, not a stable release and not a claim of broad research
effectiveness, Alpha, or PMF. See
`../2026-08-17-rc2-targeted-dsh-rerun-o01-o02/` for the rerun receipt.
