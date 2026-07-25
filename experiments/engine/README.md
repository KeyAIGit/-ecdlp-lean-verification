# Research Engine v0

This directory contains append-only outcome events for bounded ECDLP
exploration. The policy and candidate queue live in
`repo/RESEARCH_ENGINE_V0.json`; `data/research_engine_state.json` is generated
from that policy, `experiments/HYPOTHESES.yaml`, the decision substrate, and the
events under `outcomes/`.

## Hypothesis generation

`repo/HYPOTHESIS_GENERATION_V0.json` adds the proposal side of the loop:

```text
evidence axes -> generated seed -> untrusted proposal -> five adversarial
reviews -> quality-cleared draft -> existing candidate gate
```

The generator crosses only compatible target features, mechanism primitives,
and unresolved cost-changing questions that share one route, the primary threat
model, and an explicit compatibility tag. It currently emits three
source-grounded questions. A seed is not evidence and never authorizes a run.

Model- or human-authored proposals live under `proposals/`. The Engine derives
hard rejections rather than trusting proposer labels, recomputes premise
fingerprints, groups duplicate structured mechanism identities, flags lexical
near-duplicates, rejects exact known-premise duplicates, requires a null model,
a competing explanation, fixed-target semantics and a recovery map, prices
preprocessing and amortization, and binds evidence hashes to the proposal's
source commit. Reviews live under
`proposal_reviews/` and cover algebra, cryptanalysis, prior art, cost, and
validator design. The first round is blind, provenance records model family and
session, and the independent roles cannot share the proposer family. This is
still an attestation rather than proof of intellectual independence. A blocking
review is retained; it is never averaged into a score.

Quality clearance does not prove truth or global novelty. It creates only a
non-executable hypothesis draft. The normal candidate preregistration,
independent validator, selector, and dated decision contracts remain mandatory.
Zero retained drafts is an acceptable successful cycle.

An outcome event records what a run actually established. It never overwrites a
prior event, promotes a route, authorizes exact-target work, or claims a
secp256k1 break. The allowed terminal outcomes are:

- `proved`
- `supported`
- `historical_structural_confirmation`
- `falsified`
- `bounded_negative`
- `inapplicable`
- `inconclusive`
- `resource_exhausted`

The eight migrated v0 outcomes are pinned by id and canonical JSON digest in
`repo/RESEARCH_ENGINE_V0.json`, then bound as one reviewed root in validator
code. A coordinated event plus policy-metadata relabel therefore fails the
Engine gate. An intentional re-baseline remains possible only through an
explicit event, policy, and validator-code change visible in review. New work
appends native events instead.

A historical structural confirmation records a source-scoped check of an
already-known identity. It is not a preregistered positive prediction and can
never unlock a dependency, enter predictive calibration, or trigger route
review. Native `supported` remains reserved for a preregistered prediction.

A native run is accepted only when its candidate is in the selected portfolio,
all dependency outcomes explicitly unlock it, its route/hypothesis/threat model
match the candidate, its exact curve and seed are frozen in preregistration,
its source commit resolves in Git, and its validated run envelope has the
recorded SHA-256. The envelope must live under `runs/` and bind the full frozen
candidate-policy hash, preregistration hash, exact executed matrix prefix,
candidate-run manifest,
result artifacts, and independent validation artifacts. Every executed matrix
instance has its own hashed result record and a separately hashed validation
record. `proved` is reserved for a formal target accepted by its proof kernel
or deterministic logical verifier. A positive toy or calibration result is
`supported`, never `proved`.

The validator code hash must resolve at the frozen source commit, must be
distinct from the producer, and must implement the fixed
`python-pure-json-v3` protocol. Before execution, the Engine parses its AST and
rejects imports, object attributes, loops, comprehensions, file/process/network
access, dynamic code, recursion, and every call except a small allowlist of pure
builtins. It parses only preregistered hashed JSON artifact roles. A scientific
validator must recompute from raw artifacts; comparing two producer-authored
summary fields is not independent validation.

Each validator emits exactly one of the six empirical outcomes for every
executed matrix instance. The preregistration freezes an exhaustive allowed set
and a deterministic precedence under `exact-instance-outcome-v1`. The Engine,
not the researcher, aggregates those recomputed classifications into the
terminal event label. The replay request contains neither the supported value,
the producer's claimed value, the terminal outcome, nor the result digest. The
validator output binds the request SHA-256. Recomputed output must equal both
the separately hashed output artifact and the producer record. Post-hoc metric
substitution, outcome relabelling, current-checkout dependencies, and edited
outer hashes are rejected.

Outcome events record independence on three separate axes. `path` says whether
the validator path is mechanically distinct, `artifact` says whether raw data
was recomputed or a fresh cross-check was performed, and `source` is an
explicit review attestation about shared decisive logic. Distinct paths and
hashes do not prove source independence. Native decisive outcomes require all
three axes to clear; migrated history may retain weaker, explicitly labelled
evidence without unlocking native work.

The lower-level run-envelope schemas retain an `independent` boolean only as a
path-separation check. It must not be read as artifact or source independence;
the terminal outcome event carries the three-axis scientific claim.
Framework fixtures are never accepted as native evidence. Implemented
scientific validators must live under `experiments/engine/validators/`; the
selector derives `missing_independent_validator` for every other path. No
scientific validator is implemented in v0 yet. Time, memory,
workers, and actual field bit length must remain inside both candidate and
global exploration budgets. One candidate id has at most one native terminal
event; reopening requires a new candidate id. The generated `execution_queue`
is the authority for what is ready now. A pending validator is a hard gate, so
its candidate cannot be selected.

Admissibility is boolean. Eligible candidates are ordered by preregistered
expected information gain divided by normalized resource budget. The prior and
`P(outcome | live/dead)` distributions are subjective v0 inputs, are frozen
before a native run, and are calibrated with Brier scores only after native
outcomes. Migrated historical outcomes are excluded from predictive
calibration.

Run:

```text
python scripts/build_research_engine_state.py
python scripts/check_research_engine.py
python scripts/test_research_engine.py
```

Promotion remains governed by `repo/ECDLP_DECISION_SUBSTRATE.json`.
