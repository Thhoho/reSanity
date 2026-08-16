# 2026-08-16 Codex iterative preflight

This directory preserves raw Codex artifacts from architecture convergence. It is deliberately **not** a v2 benchmark result: the passing cases span four consecutive candidate hashes, DSH was not installed or run, and the paired final A/B was not started. `suite.json` therefore remains `NOT_RUN` and the method remains `UNBENCHMARKED_CURRENT`.

## Frozen runtime facts

- Host: Codex CLI `0.142.5`
- Model: `gpt-5.5`
- Candidate arm: `prompts/candidate-instruction.md`
- Task prompts: neutral prompts from `validation/v2/prompts/`
- Retries: no semantic case was automatically retried; a CLI launch rejected an incorrectly placed `--search` flag before a model session began, then the corrected command was run once
- Installation: isolated project/user copies under `/private/tmp`; no DSH install and no global `trade-nothing` overwrite

## Candidate sequence

| Candidate | `SKILL.md` SHA-256 | What changed | Preserved passing evidence |
| --- | --- | --- | --- |
| r5 | `be3665c85277d26d3ec96a1f35e981f3413c372c5997b4a9635a48603fea3f28` | thin protocol, routing, conservative trigger, as-of prompt correction | 5 closed cases, 10 trigger cases, 6 anchor sessions, O03 |
| r6 | `09f4fd43130b5b3d27fa6d1fc3e1fbe80754249e2cf70a5c1468957284423e03` | whole-claim label and complete snapshot closure made explicit | O01 |
| r7 | `d8c796f2f38c9329531d04dade6579a24c0ac5b00091c37561e3bd25cd6106a6` | one evidence-boundary label per card | no final pass; failure retained |
| r8 | `9ea841eca8edec0fc96b89c580ea12a7a73530e2ba75179d8b308f90c4cf4f64` | logical deduction explicitly remains `INFERENCE` | O02 |

The candidate at the end of this Codex-only preflight was r8. Its then-selected reference hashes were:

- `references/investing.md`: `c2aca2e6c3e2de33d7d1e87f5f0f0ce515331152ee57591ee99fb14f3f179170`
- `references/anchors.md`: `03cbcfb34d1c8ed272b3ea84a7368a669da5b309c8e809480f6dbaf42cef8bbd`
- `references/formal-audit.md`: `ee14f85c5cc104f439b9373c2f8531b910ef9830781042b8f32cc141739317bb`

## Provisional findings

- Closed core/profile: 5/5 sessions exited successfully. Manual review found complete atomic cards, no investment language in core cases, and `NOT_EVALUABLE` / bounded single-lineage conclusions in investing cases.
- Trigger: 10/10 matched the expected invocation class in Codex. Investment and explicit non-investment requests loaded Resanity; ordinary summary, coding, rewriting, translation, and general Q&A did not.
- Anchor: three two-session workspaces ended in `refuted`, `realized`, and `archived`; original propositions and history remained present. The read-only reminder checker produced no reminders for those non-active end states.
- Open network: O01, O02, and O03 each have a reviewed passing artifact, but at r6, r8, and r5 respectively. O03 retained valuation as `NOT_EVALUABLE`; O01 and O02 closed every report citation into the saved source snapshot and respected the 2026-07-31 publication boundary.
- Install identity: the preserved identity receipts match each candidate actually loaded. Repository unit tests cover host locator precedence, project shadowing, missing references, active hash drift, and selected profile hashes.

These findings justify continued engineering work only. They do not establish a frozen-candidate layer pass, research effectiveness, Alpha, PMF, or release readiness.

## Failures retained on purpose

`failures/` keeps the non-passing artifacts that drove the architecture changes:

1. r5 initial open run used an undated current program page for O02 and post-as-of historical market data for O03.
2. r5 open r2 fixed the date gate, but O01 mislabeled an interpretive claim as `FACT`; O02 also omitted a load-bearing Rhode Island source from its snapshot.
3. r6 O02 split one card's boundary into observation=`FACT` and conclusion=`INFERENCE` instead of assigning the whole claim one label.
4. r7 O02 used one label but still called a logical deduction from state counterexamples `FACT`.
5. r8 O02 assigned that universal-claim adjudication `INFERENCE`, retained `INSUFFICIENT` for missing nationwide outcome data, and closed E1-E9 into the snapshot.

## What must happen next

1. Freeze r8 (or a later reviewed hash) and rerun all first-six-layer Codex cases under that exact hash; earlier hashes cannot be pooled into a formal pass.
2. Keep DSH trigger/install identity `NOT_RUN` unless the user separately authorizes a DSH install. Do not infer DSH behavior from Codex.
3. Only after the prelayers are frozen, ask for explicit authorization to run the 8-case, two-arm final A/B. Preserve both failures and successes with identical task prompts, model, tools, as-of, budgets, and zero automatic retries.
