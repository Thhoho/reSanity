# Resanity v2 DSH final A/B — three-role AI panel

Release-candidate evidence only. Method status remains `UNBENCHMARKED_CURRENT`.

## Frozen identity and collection

- Candidate `SKILL.md` SHA-256: `5541240637eae5367ba8fbbacd180f69d7a4f1900e59efa03104acbaf7419a94`
- Core profile SHA-256: `1b41daea2a6a196b02e95c7d697ede40bd9003b30ca63554555d5e93eab8a1db`
- Investing profile SHA-256: `778b62c2ac949e4ade6185d3e64c366937892698e303b15403ab66eb30263906`
- DSH collection summary SHA-256: `af849c871ba6a02141a9e75e0a592c5319b2caf9a4c1aaf49b02f50f246362b6`
- Complete pairs: 8/8; candidate profile match: 100%; automatic retries: 0; pair-signature failures: 0.

The full DSH collection and blinded reviewer packets are retained outside the source repository.
This directory stores the compact adjudication required for version management; it is not a replacement
for the raw sessions or independent human review.

## Panel result

Three independent, blank-context AI roles reviewed blinded arms before identity reveal:

- Candidate case wins: 6/8; baseline case wins: 2/8.
- Reviewer-case ballots: candidate 16, baseline 7, tie 1.
- Candidate factual P0 negative regressions: 0.
- Median non-cached-input ratio: `1.18103`, below the `1.25` ceiling.
- Numeric adjudication: `MEETS_LIMITED_AB_LINE_BY_THREE_ROLE_AI_PANEL`.
- Clean pass: **no**.

## Known defects retained in `2.0.0-rc.1`

1. `O02`: candidate output stopped at a tool-call/source-table fragment instead of a usable report.
2. `C03`: candidate overweighted the supplier cause and discounted the feature-flag path without discriminating evidence.
3. `O01`: candidate used an undated mutable page for historical state, misstated the WebAuthn Level 3 status, and missed a scoped 26% observation in a saved source.
4. `O03`: candidate described company aggregates as a closed order-to-cash chain without same-order lineage.

`I01` was the clearest positive: the candidate preserved `NOT_EVALUABLE` instead of turning missing disclosure into zero economic exposure.

## Boundary

This supports a bounded comparative advantage on the tested cases and an RC checkpoint only. The reviewers
were AI roles rather than independent humans, report style may partially reveal treatment, and known prelayer
failures are not erased. Do not claim broad research effectiveness, Alpha, PMF, or stable release readiness.
