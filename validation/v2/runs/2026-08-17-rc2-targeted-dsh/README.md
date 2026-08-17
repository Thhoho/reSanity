# Resanity 2.0.0-rc.2 targeted DSH validation

Status: `TARGETED_VALIDATION_PARTIAL_EXTERNAL_QUOTA`. Method status remains
`UNBENCHMARKED_CURRENT`.

The frozen RC2 Skill hash
`0704f56286ad6de61ba9c6e1954fb7b38a0c0a8e02f22bfc1ede5422a857c381`
was installed into an isolated `headless-resanity` DSH profile and matched the
canonical checkout. Four explicitly authorized cases ran through
`deepseek-official/deepseek-v4-pro` at reasoning effort `max`, concurrency 2,
with zero automatic retries.

Two sessions were mechanically complete and passed manual semantic review:

- `C03-technical-debug` kept the release, vendor, and interaction hypotheses
  co-active because the available observations were compatible rather than
  discriminating. It also used the regional and upload-path counterexamples to
  reject the claim that all uploads failed.
- `O03-investing-exposure` separated aggregate company demand, revenue, margin,
  and cash observations from a same-lineage liquid-cooling chain. The liquid-
  cooling-specific exposure remained `NOT_EVALUABLE`. A 31st tool attempt was
  denied by the validation guard, but the session still delivered a readable
  report.

Two sessions ended with DSH exit code 1 after the DeepSeek provider returned
`QUOTA: Insufficient Balance`; neither was retried:

- `O01-product-passkey` stopped during research. It retained three source
  snapshots but produced no report, so its dated-status repair is not
  evaluated.
- `O02-policy-outcome` successfully wrote a 10.8 KB `REPORT.md` before the
  provider rejected the next model step. DSH stdout contained only process
  speech, so host delivery is incomplete. The recovered artifact is improved
  over RC1, but it is not accepted: its root mixes `NOT_ESTABLISHED` with a
  claim of falsity and relies in part on a document with no visible publication
  date for an as-of-constrained conclusion.

The result validates two targeted behaviors but is not a four-case pass, a
stable-release gate, a final A/B, or evidence of broad research effectiveness.
RC2 remains a local release candidate; no tag, push, publish, or automatic
rerun occurred.
