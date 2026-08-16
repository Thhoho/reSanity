# 2026-08-16 DSH frozen-candidate prelayers

This note records the first same-identity DSH prelayer collection for the r8 candidate. Raw artifacts remain outside the repository at `/private/tmp/resanity-v2-dsh-prelayers.swWtuP/collection-r6`; this note is an evidence index, not a copied score.

## Frozen identity and host

- Candidate Skill SHA-256: `9ea841eca8edec0fc96b89c580ea12a7a73530e2ba75179d8b308f90c4cf4f64`
- Core profile: `b2cfede41b14e9a38bd0aad25d430c5e7611be890d302e5b077e155b28cd94c0`
- Investing profile: `9a89a3a968975cb93e6e9de943fbbbf957ca9ae4d80e933ea8785babda1f5c7e`
- Anchors profile: `e4872576ad499f0de60bac71619f4f67abbf891ee9c72781d74ef5c52d94c60c`
- Formal-audit profile: `33ef2d1deb624ee43231357cb96120d0a56304869355a87b495418ed05a818ac`
- Host: DSH headless `0.1.0-rc.6`, `deepseek-official/deepseek-v4-pro`, reasoning `max`, workspace-write, approval ask
- Automatic retries: 0; subagent and workflow entry points disabled

## Result

The collection produced 24 raw sessions. Twenty-two satisfied the frozen host contract. Manual layer review recorded:

- core contract: PASS (3/3)
- investing profile: FAIL
- open network: FAIL (O02 used 31 tool calls and O03 used 34 against a frozen limit of 30)
- anchor lifecycle: PASS (6/6)
- trigger: PASS (5/5 positive and 5/5 negative)
- install identity: PASS

The investing blocker is decision-bearing: I01 correctly states the missingness boundary in a later claim card, but its root conclusion still says attributable exposure "has not formed" / there is "no attributable exposure". The packet only supports not evidenced and `NOT_EVALUABLE`.

The external review summary is `collection-r6/reviews/review-summary.json`. Its status is `PRELAYERS_BLOCKED`; it must not be converted into `PRELAYERS_PASS`, and the final paired A/B must not start from this evidence.

## Separate Tushare feature smoke

A fresh read-only request against Tushare Pro passed the as-of, QFQ, provider-lineage, series-hash, receipt-hash, credential-redaction, and latest-session-alignment checks. It establishes a working structured price/valuation observation adapter only; it does not establish research effectiveness or an investment conclusion.

## Candidate iteration after review

The repository candidate after this review adds two thin protocol clarifications: missing evidence cannot become negative reality in any title/root/summary/table, and one-shot research treats tool budgets as hard ceilings while retaining one canonical snapshot per upstream source. These edits create a new candidate identity; none of the r8 semantic results may be presented as scores for the new identity.
