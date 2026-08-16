# DSH prelayers r9 review

This directory records the manual layer review for the fresh DSH collection at
`/private/tmp/resanity-v2-dsh-prelayers.swWtuP/collection-r9`. Raw reports, source
snapshots, session logs, and host receipts remain outside the repository. The review
is bound to Skill SHA-256
`a40d87daade14f5b1462ccc9a6ec217a68168b09dcf41dffd60da6d5b625f4d4` and collection
summary SHA-256
`66f7fec4ad7ea59ee19ee86ec48092781165175a48789b37b8d3b0504e2a65ee`.

The collection produced all 24 one-shot sessions with zero automatic retries. Twenty-one
sessions satisfied the frozen host contract. `T07-coding`, `O02-policy-outcome`, and
`O03-investing-exposure` exceeded the 30-call ceiling and are mechanically incomplete.
The investment missingness repair passed manual review, and the anchor lifecycle passed
all six longitudinal cases. Open-network source discipline, semantic lineage, snapshot
discipline, and tool budgets remain blocking. Trigger selection itself was 5/5 positive
and 0/5 negative, but the layer is not a full pass because `T07` violated the host budget.

The gate is `PRELAYERS_BLOCKED`. These receipts are engineering and research-process
evidence only; they do not establish effectiveness, Alpha, PMF, or a recommendation, and
they do not authorize the final paired A/B.

After this review, the repository candidate added a hard source-eligibility boundary,
same-lineage requirements for investment exposure chains, an `N-4` active tool-call
reserve, and a neutral budget preface for trigger sessions that do not load Resanity. The
new candidate Skill SHA-256 is
`df5ac6178520b00bc9e1e876907ad519fb37be0d632d4213f4bb1bfbd20640d2`.
It passed the zero-model DSH profile-pair dry-run only. No r9 report is a score for this
new identity, and a new paid prelayer collection has not been started.
