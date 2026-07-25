# Hypothesis proposals

This directory accepts structured answers to generated seeds from
`data/research_engine_state.json`. A proposer may be a human, a model, or a
hybrid workflow, but its output is untrusted.

Every JSON file must satisfy `../hypothesis_proposal.schema.json` and the
stronger deterministic checks in `scripts/hypothesis_generation_lib.py`.
The declared premise fingerprint is recomputed, evidence paths must resolve,
the mechanism signature is recomputed from the full transformation and cost
identity, and every evidence digest must match the named file at the frozen
source commit. Each primary-source id must already belong to the selected
route. The proposal must state a premise counterfactual, null model, competing
mechanism, complete outcome matrix, and stay inside the plain single-target
threat model and toy-only scope. Novelty is split into
`new_to_repository`, `new_to_reviewed_corpus`, and globally `unverified`; the
last status cannot be promoted by this Engine.

The JSON Schemas document exchange shape. The dependency-free manual validator
in `scripts/hypothesis_generation_lib.py` is the executable authority, and
schema-parity regression tests require their top-level fields to match.

A proposal is not a hypothesis-registry entry and authorizes no run. It must
receive all five digest-bound reviews under `../proposal_reviews/`. Even a
quality-cleared proposal becomes only a generated draft; the existing
preregistration, validator, selector, and dated decision contracts still apply.

No proposal is committed in the initial generation cycle. Zero retained
proposals is an acceptable result.
