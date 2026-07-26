# Claude adversarial review brief: Research Engine v0

> **FROZEN HISTORICAL SNAPSHOT.** This brief describes a pre-merge branch and
> is retained for provenance only. Current remediation is governed by
> `RESEARCH-ENGINE-V0.2-SANITATION-001`, `TASK-010`, and
> `notes/reviews/RESEARCH_ENGINE_V0_2_BASELINE_AUDIT.md`.

## Role

Act as an independent adversarial research reviewer. Do not merge, rewrite the
architecture, or optimize for agreement with the implementer. Review the actual
branch and return severity-ranked findings with exact file/line references.

Repository: `KeyAIGit/-ecdlp-lean-verification`

Branch: `agent/research-engine-v0`

Base: `origin/main` at `1a1b5ddba7e9a6e3d40f189892e83529f5bc6616`

## Objective under review

Research Engine v0 turns the existing evidence/decision control plane into a
bounded selection and memory loop:

`preregistered candidate -> deterministic selection -> bounded toy run ->
independent validation -> review-anchored outcome -> generated feedback`

It does not generate new mathematical mechanisms autonomously.

It must not claim or imply a secp256k1 break, a subgeneric algorithm, route
promotion, or permission for exact-target work.

The current generated state should say:

- 9 normalized hypotheses;
- 8 migrated historical outcome events;
- 6 candidate proposals;
- 3 mechanism/validator candidates retained at intake;
- 3 closed rejection/canary examples;
- 0 selected explorations;
- 0 ready candidates;
- 0 native Engine outcomes;
- exploration authorized;
- promotion unauthorized;
- no selected attack route.

An empty queue is intentional. The branch must not manufacture activity when no
proposal has both an exact mechanism and an independent raw-artifact validator.

## Consolidation context

Claude's parallel prototype at `origin/claude/research-engine-v0`
(`b1bc926`) was reviewed before this packet. Its strongest design elements were
integrated here: boolean gates before valuation, mutual-information-based
expected information gain, preregistered priors/likelihoods, and Brier
calibration that excludes post-hoc historical migrations. This branch also
adopts `supported` for positive empirical outcomes, an intentionally attractive
multi-target canary that must be rejected before scoring, explicit separation
of threat-model/decision/evidence axes, and per-outcome decision deltas.

The parallel `engine/` tree is not a second source of truth and should not be
merged beside this implementation. This branch retains the repository's
existing canonical hypothesis, decision, experiment-framework, review-anchored-event,
run-envelope, generated-graph, and site surfaces. Review whether that
consolidation preserved the useful model without importing a gate bypass or
creating duplicate ownership.

## Canonical files

Read these first:

1. `repo/RESEARCH_ENGINE_V0.json`
2. `scripts/research_engine_lib.py`
3. `scripts/test_research_engine.py`
4. `data/research_engine_state.json`
5. `repo/ECDLP_DECISION_SUBSTRATE.json`
6. `experiments/engine/outcome.schema.json`
7. `experiments/engine/run.schema.json`
8. `experiments/engine/instance_result.schema.json`
9. `experiments/engine/instance_validation.schema.json`
10. `experiments/engine/validator_request.schema.json`
11. `experiments/engine/validator_output.schema.json`
12. `experiments/engine/validators/README.md`
13. `experiments/framework/fixtures/pure_engine_validator.py` (protocol test
    only; never scientific evidence)
14. `experiments/engine/outcomes/*.json`
15. `experiments/engine/runs/README.md`
16. `experiments/HYPOTHESES.yaml`
17. `tasks/ECDLP_RESEARCH.md`
18. `tasks/KEYAI_PRODUCT.md`

Then inspect the generated graph, status, site, CI, and the full branch diff.

## Non-negotiable invariants

1. Exploration and promotion are separate gates.
2. Only preregistered toy or validator-calibration work may be ready.
3. Direct secp256k1 work, expensive scaling, and public complexity claims remain
   closed.
4. A native outcome must match its candidate's route, hypothesis, threat model,
   exact preregistered curve, field scope, resource budget, run-manifest hash,
   full candidate-policy hash, full frozen matrix or strict early-stop prefix,
   a hashed result and independently recomputed validation for every executed
   instance, validator code hash at the source commit, preregistered raw JSON
   roles, capability-restricted pure-validator replay from a request that
   contains neither the claimed value, terminal outcome, nor result digest, an
   exhaustive instance-outcome taxonomy and deterministic aggregate
   precedence, strict output binding to the request hash,
   result/validation artifact hashes, real Git commit, and dependency outcome
   requirements.
5. Generated feedback may close, park, block, or reopen exploration state. It
   may not promote a route.
6. Every terminal outcome is retained, including negative, inconclusive, and
   resource-exhausted results.
7. The eight migrated outcomes are a validator-code-anchored digest baseline; native runs
   append new events and cannot rewrite that baseline.
8. Product work and ECDLP research have separate queues and KPIs.
9. The 486-claim frontier is a classified selected corpus, not 40 years of
   complete ECDLP literature.
10. `proved` is formal; a positive toy result is `supported` and can trigger
    only its declared dependency or decision review.
11. Threat-model scope, substrate disposition, and evidence status remain
    separate axes.
12. A pending validator sets `missing_independent_validator=true`; a named
    quotient without its exact map and recovery contract sets
    `missing_exact_mechanism=true`. Neither candidate may be selected.

## Adversarial questions

### Gate bypass

- Can any edit or event make promotion true while the decision substrate stays
  `select_none`?
- Can a native event be accepted for an unselected, rejected, direct-target, or
  dependency-blocked candidate?
- Can recorded time, memory, worker count, field size, threat model, or hidden
  preprocessing bypass the declared limits?
- Can a terminal event be duplicated or ordered before its prerequisites?
- Can a framework regression fixture, cherry-picked matrix subset, unhashed
  result, or non-independent validator be relabelled as a native outcome?
- Can changing the current policy, validator code, or outer hashes detach a run
  from the exact candidate and validator frozen at `source_commit`?
- Can the validator recover the producer's claimed value directly or indirectly
  from the request, result digest, current checkout, imports, object
  introspection, file/process/network access, or dynamic code?
- Can the producer postselect the metric identity, per-instance outcome,
  aggregate precedence, or decisive artifact roles after seeing a result?
- Can any pending-validator or missing-mechanism candidate enter the selected
  queue?
- Can coordinated edits to a result, validation record, validator-output
  artifact, and every outer hash pass without the frozen validator reproducing
  the same classification?
- Can the same recomputed instance vector be relabelled as `falsified`,
  `bounded_negative`, or `inconclusive`?

### Selector

- Is selection deterministic under reordering?
- Is the high-prior, low-cost multi-target canary rejected mechanically before
  its information model can influence ranking?
- Are dependency semantics based on outcomes, not merely list position?
- Are mutual-information arithmetic, normalized budget cost, and tie breakers
  implemented exactly as declared?
- Can subjective priors/likelihoods or retrospective fixtures manufacture a
  favorable result? Confirm that migrated outcomes are excluded from predictive
  calibration and distinguish an implementation bug from a documented v0
  limitation.

### Scientific meaning

- Confirm that `RE0-002` is correctly demoted to
  `genuinely_open_question`/intake until it has an exact quotient map, rings,
  ideal, saturation/localization, orbit/stabilizer rules, relation semantics,
  recovery map, and implementation hash.
- Confirm that `RE0-003` cannot be selected merely because it names a scaling
  test downstream of an unspecified construction.
- Confirm that `RE0-001` is blocked until a validator reconstructs decisive
  Groebner/proxy/EC facts from raw artifacts. The framework fixture is not that
  validator.
- Determine whether the v3 capability boundary can express the necessary raw
  certificate checks. If not, specify the smallest deterministic protocol
  extension without weakening source/provenance binding.

### Historical migration

Compare all eight events against their cited original `README.md`, `RESULTS.md`,
run manifests, and validators.

Pay special attention to:

- whether `bounded_negative`, `inconclusive`, and `resource_exhausted` are used
  consistently;
- whether splitting the 24-bit cofactor-3 ambient-group P0 rows into
  `inapplicable` correctly repairs the original aggregate scope;
- whether P2/Ward is correctly `supported` only for its torsion identity;
- whether P4 is correctly `inconclusive` because validation is partial and
  `decisive_claim_validated=false`;
- whether a narrow negative is accidentally presented as a route-level no-go;
- whether missing historical resource measurements remain explicit;
- whether reopening conditions preserve every material residual uncertainty.

### Feedback and public truth

- After a hypothetical native outcome, do candidate state, execution queue,
  hypothesis evidence, route evidence, knowledge graph, status, agent bundles,
  and public site converge without manual optimistic edits?
- Could product activity, theorem volume, or site metrics be counted as
  cryptanalytic progress?
- Does any generated/public text imply that an intake candidate is selected or
  executable when the correct counts are zero selected and zero ready?
- Does any generated/public text describe the four historical no-reopen cases
  as predictive EIG calibration? The correct native calibration count is zero.

## Required verification

Run at least:

```text
python3 scripts/build_research_engine_state.py --check
python3 scripts/check_research_engine.py
python3 scripts/test_research_engine.py
python3 scripts/check_ecdlp_decision_substrate.py
python3 scripts/check_status_consistency.py
python3 scripts/check_generated_fixpoint.py --check
```

Also review the complete diff against `origin/main`. Passing checks are evidence
of internal consistency, not proof that the research semantics are sound.

## Output contract

Return:

1. Findings first, ordered `P0` to `P3`.
2. For every finding: exact file/line, concrete failure or counterexample,
   impact, and minimal remediation.
3. A separate list of residual scientific risks that are not implementation
   bugs.
4. A verdict on whether any candidate may run now.
5. Exact missing artifacts required to move RE0-001 or RE0-002 from intake to
   a frozen selectable candidate.
6. A verdict on the eight historical outcome labels.

If there are no blocking findings, say so explicitly. Do not approve promotion,
merge the branch, or infer progress toward practical secp256k1 ECDLP merely
because repository checks are green.
