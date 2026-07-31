# Featherless API audit - 2026-07-31

## Scope

This is an integration audit, not a model-quality result and not scientific
evidence. It checks whether the existing `FEATHERLESS_API_KEY` repository secret
can reach Featherless from a GitHub-hosted runner without generating tokens.
The secret value was not read or written to an artifact.

## Reproduction

- Repository workflow: `.github/workflows/prover-smoke-test.yml`
- Manual run: `30649531680`
- Run URL: <https://github.com/KeyAIGit/-ecdlp-lean-verification/actions/runs/30649531680>
- Trigger: `workflow_dispatch` on `main`, one attempt per configured prover model
- Models reached by the workflow: Pythagoras-Prover-4B,
  Goedel-Prover-V2-32B, and Kimina-Prover-Distill-8B

All three provider steps failed before inference. The raw Pythagoras step reported
HTTP 403 with Cloudflare error code 1010. No completion was returned and no proof
was accepted. The workflow previously appeared green only because provider failures
were marked `continue-on-error`; that masking has been removed.

## Decision

The GitHub-hosted path is `network_policy_blocked`. This result does not show that
the secret, subscription, or models are invalid. Featherless remains the preferred
flat-subscription drafting provider, but it may be used only after the executing
host passes the zero-token plan/model probe in `scripts/featherless_api_probe.py`.
Direct DeepSeek and Moonshot/Kimi APIs remain explicit fallbacks, not requirements.
No model weights should be downloaded to the laptop or committed to Git.

The optional drafter in `scripts/hypothesis_model_drafter.py` remains disabled by
default. Even after a host passes the probe, a live response is an untrusted,
non-executable fragment and cannot clear assurance, independence, recommendation,
authorization, route-promotion, or exact-target gates.
