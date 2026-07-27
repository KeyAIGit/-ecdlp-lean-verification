# Hypothesis proposal reviews

Reviews are adversarial records bound to the exact canonical SHA-256 of one
proposal. Required roles are:

- `algebra`
- `cryptanalysis_skeptic`
- `prior_art`
- `cost_model`
- `validator_design`

The proposer may not review its own proposal. Reviewer identities must be
distinct. Every first-round review must be blind to the other verdicts and
records model family, version, session, and prompt hash. The prior-art and
cryptanalysis-skeptic roles must explicitly attest source independence and
cannot share the proposer model family. At least two reviewer families must be
present. These fields are still metadata, not mechanical proof of intellectual
independence, so generated state labels them accordingly.

Any blocking review is retained rather than averaged into a score. Editing a
proposal invalidates every prior review digest.
