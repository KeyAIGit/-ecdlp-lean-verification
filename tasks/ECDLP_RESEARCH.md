# ECDLP research queue

This queue owns work that changes the evidence, uncertainty, or formal boundary
of the plain single-target secp256k1 ECDLP program. Product traffic, site work,
pilot activity, and portability rehearsals do not count as progress here.

Canonical start order:

1. Read `STATUS.md`.
2. Read `repo/ECDLP_DECISION_SUBSTRATE.json`.
3. Read `repo/RESEARCH_ENGINE_V0.json`.
4. Read this queue.
5. Load `repo/FORMAL_SUBSTRATE.json` only for a selected formal dependency.

## Active tasks

### ML-P0 qualification under TASK-013

State: active_engineering_qualification
Parent task: TASK-013
Kind: data | research | experiment-infrastructure
Hypothesis: none; P0 is a route-neutral engineering qualification
Why it matters: Direct pair regression is unlikely to discover a usable ECDLP
algorithm by scale alone, but ML can widen the search for representation-specific
signals and explicit mechanisms. Before such output may enter proposal intake,
the repository needs deterministic synthetic data, split isolation, canaries,
nulls, independent-path arithmetic replay, and bounded streaming probes.
Inputs:
- owner direction dated 2026-07-27 to design and begin an ML research lane
- `notes/ML_STRUCTURE_DISCOVERY_PLAN.md`
- `experiments/ml_structure_probe/`
- the generic-group scope and candidate lifecycle
- Takhanov et al., *Intractability of Learning the Discrete Logarithm with
  Gradient-Based Methods*
Expected output:
- A reproducible generator for one million synthetic secp256k1 scalar/public
  point pairs, with no wallet or external key material.
- Separate train, validation, and test derivation domains.
- A validator that checks every artifact hash and independently recomputes a
  deterministic public-key sample without importing the producer.
- Streaming linear probes over scalar bits/residues, positive canaries, and a
  permutation null.
- A budgeted AutoML controller that compares multiple model and representation
  families by successive halving, selects only on validation, evaluates one
  finalist per task on test, and retains a complete run ledger.
- A staged plan in which ML observations must become explicit mechanisms before
  they can enter the normal proposal and candidate gates.
Exit criteria:
- `python experiments/ml_structure_probe/test_probe.py` passes.
- The million-pair configuration completes within the declared 8-worker,
  8-GB-memory engineering budget and its validator passes.
- Both canaries cross the preregistered threshold and the permutation null does
  not.
- The AutoML run records every attempted method and parameter set, and no
  scientific task uses test feedback for further tuning.
- Primary AutoML finalists are frozen and replayed on a second independently
  derived one-million-pair dataset before the retained P0 conclusion.
- Any apparent scalar signal is labelled untrusted and creates no hypothesis,
  route promotion, or scientific outcome.
- P0 makes no learnability, hardness, recovery, or asymptotic claim.
Files allowed to edit:
- `experiments/ml_structure_probe/`
- `notes/ML_STRUCTURE_DISCOVERY_PLAN.md`
- this task contract
- experiment index, source registry generator, and generated source registry
  directly affected by the new primary source
Files that must be regenerated:
- `data/source_registry.json`
How to verify:
- `python -m py_compile experiments/ml_structure_probe/*.py`
- `python experiments/ml_structure_probe/test_probe.py`
- `python scripts/gen_source_registry.py --check`
- repository artifact and status consistency gates

This owner-directed P0 does not supersede TASK-010, authorize a candidate
experiment, or enter native Research Engine calibration. A P1 toy-scaling run
requires an immutable candidate, validator evidence, and the normal dated
authorization path.

### TASK-013 - Build and calibrate Research Engine v0

Status: active
Kind: research | data | experiment | ops
Hypothesis: engine-level selection policy; bounded candidates remain tied to
their named hypotheses
Why it matters: The repository needs a closed evidence -> generation ->
adversarial proposal review -> selection -> bounded exploration -> validation
-> retention loop without weakening the independent promotion gate. Creative
model output remains untrusted; deterministic gates compile it into a candidate
or retain its exact blockers.
Inputs:
- `repo/RESEARCH_ENGINE_V0.json`
- `repo/ECDLP_TYPED_EVIDENCE_V0.json`
- `repo/ECDLP_DECISION_SUBSTRATE.json`
- `experiments/HYPOTHESES.yaml`
- historical experiment artifacts under `experiments/`
Expected output:
- Separate exploration and promotion gates.
- A typed evidence layer that joins claim-level sources, target properties,
  mechanism requirements, scoped barriers, and cost quantities before any
  creative synthesis.
- A generator that emits seeds only from unresolved typed cells without treating
  combinatorial novelty as scientific novelty.
- A zero-cost desk-decision path for scoped applicability and closure results,
  separate from experiment outcomes and predictive calibration.
- Digest-bound proposal and five-role adversarial-review contracts that can
  produce at most three non-executable hypothesis drafts per cycle.
- Eight-outcome result taxonomy, with formal `proved` separated from empirical
  `supported`, and a five-class gap taxonomy.
- All nine hypotheses and historical runs normalized without rewriting
  provenance.
- Deterministic selector with boolean hard rejection, preregistered expected
  information gain per normalized budget, dependency order, and retrospective
  no-reopen tests.
- An ordered queue of at most three toy-only explorations; an empty queue is
  required when no proposal clears every scientific gate.
- Append-only outcome events that regenerate hypothesis and route evidence
  state.
Exit criteria:
- Promotion and exact-target work remain disabled.
- Generated seeds and drafts never authorize work; zero retained drafts is a
  valid cycle result.
- Quality-cleared drafts bind the exact proposal and five review digests.
  Mechanism, validator, and bounded-experiment candidates must bind that
  registered draft before lifecycle evaluation.
- The legacy candidate set is code-anchored and hash-frozen. It cannot be edited
  into admissibility; new execution remains closed until a deterministic
  compiler binds a typed cell to a quality-cleared proposal.
- A desk decision cannot close a wider route, enter predictive calibration, or
  authorize execution.
- Exact known-premise duplicates, semantic re-encodings identified by review,
  threat-model drift, missing fixed-target semantics, missing recovery, hidden
  preprocessing, proxy-only metrics, prose-only scientific packets, and
  missing validator plans cannot clear.
- Every selected exploration has a mechanism or named validator role,
  prediction, baseline, fixed budget, stop condition, and independent
  validator.
- Validator path and artifact independence require registered verification;
  source independence requires a third-party human attestation. A design-only
  validator is never lifecycle-ready.
- Every native matrix instance binds a hashed result to an independently
  recomputed classification from raw artifacts through a source-commit-bound
  pure validator. The allowed instance outcomes and exhaustive aggregate
  precedence are frozen before execution; the request contains neither the
  claimed value, terminal outcome, nor result digest.
- A named mechanism is not selectable until its exact map, algebraic
  presentation, exceptional locus, relation semantics, recovery path, and
  implementation identity are frozen.
- Native predictive calibration excludes migrated historical outcomes.
- Historical no-reopen cases reject known dead ends without claiming
  predictive selector calibration.
- A new outcome event deterministically updates the generated engine state and
  knowledge graph.
- All repository gates and generated-artifact checks pass.
Files allowed to edit:
- `repo/RESEARCH_ENGINE_V0.json`
- `repo/ECDLP_TYPED_EVIDENCE_V0.json`
- `repo/HYPOTHESIS_GENERATION_V0.json`
- `repo/ECDLP_DECISION_SUBSTRATE.json`
- `experiments/engine/`
- `experiments/HYPOTHESES.yaml`
- `data/research_engine_state.json`
- task, generator, validator, graph, site, and CI files directly affected by
  the engine contract
Files that must be regenerated:
- `data/typed_evidence_state.json`
- `data/research_engine_state.json`
- every derived artifact named by `repo/ARTIFACTS.yaml`
How to verify:
- `python scripts/build_typed_evidence_state.py --check`
- `python scripts/test_typed_evidence.py`
- `python scripts/build_research_engine_state.py --check`
- `python scripts/check_research_engine.py`
- `python scripts/test_research_engine.py`
- `python scripts/check_ecdlp_decision_substrate.py`
- the full repository gate battery

### TASK-008 - Maintain evidence-gated candidate intake

Status: active
Kind: research | data | ops
Hypothesis: none; intake evaluates proposals before hypothesis promotion
Why it matters: New progress must enter through source-pinned mathematical
evidence or a concrete mechanism, not by silently reviving a parked route.
Generated research seeds reduce dependence on one agent noticing an
intersection, while adversarial compilation prevents fluent text from becoming
authorization.
Inputs:
- new primary literature, author artifacts, or a concrete candidate proposal
- `repo/ECDLP_DECISION_SUBSTRATE.json`
- `data/attack_registry.json`
- `repo/RESEARCH_ENGINE_V0.json`
Expected output:
- A dated evidence delta tied to one route, threat model, and gap class.
- A generated seed or structured proposal tied to one route, one primary threat
  model, source anchors, a novel premise fingerprint, and an exact uncertainty.
- Five digest-bound review dispositions when a proposal seeks quality
  clearance.
- A pass/fail result for the relevant exploration or promotion gate.
- Either no disposition change or an explicit proposed decision delta.
Exit criteria:
- Scope and provenance are complete.
- Conditioned, leakage, quantum, and plain-input claims remain distinct.
- Intake alone cannot authorize promotion or exact-target work.
Files allowed to edit:
- canonical evidence and decision registries
- directly stale architecture, status, source, and generated view files
Files that must be regenerated:
- every affected derived artifact
How to verify:
- `python scripts/check_ecdlp_decision_substrate.py`
- `python scripts/check_research_engine.py`
- the full repository gate battery

### TASK-009 - Resolve the bounded GLV-Semaev structural uncertainty

Status: completed_bounded_structural
Structural lane: completed
Decision: RS-2026-07-24-001
Iteration: GLV-SEMAEV-ITER-001
Route: R-GLV-SEMAEV
Hypothesis: HYP_GLV_SEMAEV_001
Foundation: F-SEMAEV-ELIMINATION
Kind: theorem | research | data | ops
Why it matters: The exact coordinatewise C3 action on S3 and S4 decides whether
the naive invariant quotient has the symmetry it claims. This bounded
structural uncertainty is now resolved; it was not route promotion or an
experiment hypothesis run.
Inputs:
- `RS-2026-07-24-001`
- the exact resultant definition of S4 and existing S3/S4 and GLV modules
- the retained P0-P4 evidence without reinterpretation or deletion
- deterministic symbolic certificates and an independent replay path
Expected output:
- The full finite classification of coordinatewise C3 semi-invariant actions
  on S3 and S4, with polynomial equality kept distinct from zero-variety
  equality.
- The `S4` fixed-target transport/classification and the point-group GLV
  relation bijection. `S3` has no fixed-target classification claim.
- Only completed covariance identities in the smallest kernel-checkable Lean
  package; any impractical stabilizer classification remains outside the
  verified ledger with its exact blocker.
- A dated bounded result: diagonal-only no-go, exact larger quotient, or the
  smallest unresolved lemma.
Exit criteria:
- The work answers only `GLV-SEMAEV-ITER-001`.
- `HYP_GLV_SEMAEV_001` remains parked as an experiment and its completed
  structural lane records no promotion.
- Every other route, hypothesis, and conditional foundation remains outside
  the structural lane.
- Promotion and exact-target work remain disabled.
- No general msolve, Sage, F4, parameter sweep, or secp256k1 discrete-log run
  is authorized.
- Lean results pass kernel, axiom, and no-`sorry` gates.
Files allowed to edit:
- `experiments/glv_semaev_symmetry/`
- `Ecdlp/Proved/GlvSemaevSymmetry.lean`
- `Ecdlp.lean`
- `VERIFIED.md`
- `notes/GLV_SEMAEV_ITERATION_001.md`
- the canonical governance paths bound to this decision
- directly affected generated views, but only after source work is complete
Files that must be regenerated:
- every affected derived artifact
How to verify:
- independent symbolic certificate replay
- `lake build`
- no-`sorry` and axiom audit
- `python scripts/check_ecdlp_decision_substrate.py`
- status consistency and affected experiment/framework tests
- the full repository gate battery

### TASK-010 - Independent adversarial audit at a stable checkpoint

Status: completed_accepted
Kind: review | research | ops
Hypothesis: none
Lifecycle: RESEARCH-ENGINE-V0.2-SANITATION-001
Completed on: 2026-07-27
Acceptance commit: `85f85d4ca0b9dba323bfdd05ce8750d6db4732ac`
Why it matters: The independent audit found reproducibility, lifecycle,
calibration, semantic-drift, and authorization defects. This task repairs those
findings before Research Engine v0.2 is treated as stable.
Inputs:
- protected baseline `fed55d84675fd96e5f40204b9f5f49baa8c01172`
- `notes/reviews/RESEARCH_ENGINE_V0_2_BASELINE_AUDIT.md`
- `notes/reviews/RESEARCH_ENGINE_V0_2_ORACLE_INTAKE.md`
- `notes/RESEARCH_ENGINE_V0_TO_V0_2.md`
- `notes/reviews/PR246_DISPOSITION.md`
- `repo/RESEARCH_ENGINE_V0_2_ACCEPTANCE.json`
- `repo/RESEARCH_ENGINE_LIFECYCLE_V0.json`
- policy, generated state, outcome events, and retrospective fixtures
- architecture, formal trust, route decisions, and residual risks
Expected output:
- A repaired, reproducible Research Engine and non-executable generation plane.
- Claim-level truth state, immutable candidate snapshots, and separate lifecycle.
- Derived scientific contracts, scenario scoring, and exhaustive portfolio logic.
- A release or revision recommendation backed by the required regression tests.
Exit criteria:
- Every blocking finding is resolved or explicitly accepted with rationale.
- The review does not silently edit canonical state or promote a route.
- All affected checks are rerun after finding resolution.
- Eight historical outcome files and their review root remain byte-identical.
- All 19 owner regression cases resolve to passing fault-injection tests.
- Shadow intake is generated, non-executable, and retains zero authorization.
- No experiment is authorized and no route is promoted.
Files allowed to edit:
- review packet and files required to resolve accepted findings
Files that must be regenerated:
- all derived artifacts touched by accepted findings
How to verify:
- full local gates and GitHub CI

## Queued scientific activation

The Research Engine architecture is frozen after `TASK-010` unless a concrete
blocking defect is demonstrated. The following tasks use the engine; they do
not create v0.3 schemas. All proposal seeds remain non-executable. The
conditional native phase of `TASK-014` requires a separate dated owner
decision.

### TASK-014 - Run the first post-v0.2 scientific activation cycle

Status: evidence_closed_phase_d_blocked
Kind: literature | applicability | cost | data | theorem | structural | research
Hypothesis: none during evidence closure; the desk phase owns
`RQ-PKC-SMOOTH-ARITY-COST-001`, while the parallel structural workstream owns
`RQ-GLV-CONNECTED-SYSTEM-RIGIDITY-001`
Why it matters: A new prime-field Semaev/Petit proposal cannot be assessed
honestly without claim-level source boundaries and a full-cost bridge.
Yokoyama and Amadori are now bound to inspected primary artifacts and exact
extracts; Kudo CANS 2018 remains full-text unread. The deterministic
smooth-subgroup desk screen resolves the two arithmetic predicates but leaves
solving degree, recovery, relation independence, and total work unknown, so it
does not justify a solver or native experiment.
Current cycle disposition:
- direct Petit smooth-subgroup instance: arithmetic predicates pass together
  first at `m=16`, but the total mechanism remains `inconclusive` and no native
  run is authorized
- auxiliary-curve instance: `parked` with no retained exact candidate
- connected-system GLV workstream: stopped before Lean work because no
  decision-critical theorem and no source-independent review survived
- Phase D: blocked with zero retained candidates
Inputs:
- Yokoyama, Yasuda, Takahashi, and Kogure, *Complexity bounds on
  Semaev's naive index calculus method for ECDLP*, JMC 14 (2020),
  DOI `10.1515/jmc-2019-0029`
- Kudo, Yokota, Takahashi, and Yasuda, *Acceleration of Index Calculus
  for Solving ECDLP over Prime Fields and Its Limitation*, CANS 2018
- Amadori, Pintore, and Sala, *On the Discrete Logarithm Problem for
  Prime-Field Elliptic Curves*
- Petit, Kosters, and Messeng, PKC 2016
- `data/source_registry.json`
- `repo/ECDLP_TYPED_EVIDENCE_V0.json`
- `CELL-M-PKC-SMOOTH-M16`
- `EDD-2026-07-25-003`
- exact secp256k1 public parameters
- the matched plain Semaev baseline
- historical P3/P4 evidence
- `Ecdlp/Proved/GlvSemaevSymmetry.lean`
- `experiments/glv_semaev_symmetry/`
- `notes/GLV_SEMAEV_ITERATION_001.md`
- the exact recursive `S3` presentations used by prime-field proposals
Expected output:
- Phase A, evidence closure:
  - A claim-level Yokoyama source card with exact assumptions, theorem or
    proposition anchors, bounded conclusion, and explicit exclusions for
    structured factor bases.
  - A lawfully obtained and hashed Kudo full text, or an explicit unresolved
    acquisition record. No novelty claim is allowed while it remains unread.
  - An Amadori claim extract with sections, algorithm, assumptions, recovery,
    and cost model, or a downgrade of `full_text_inspected`.
  - A comparison matrix for naive Semaev, Amadori, Kudo, both PKC 2016
    constructions, P3, and P4.
- Phase B, desk screen:
  - Exact, reproducible values for arities `m = 10..20`, including the
    source-validated factor-base threshold and relation-yield expression. The
    expression `D^m / (m! p)` is anchored to PKC 2016 Section 3.2 and remains
    a heuristic expectation in that paper's unit-cost model, not a theorem
    about relation independence or total attack cost.
  - Four representations: direct `S_(m+1)`, sequential `S3`, balanced `S3`,
    and a source-faithful low-degree membership/addition-chain encoding.
  - For each representation: variables, equations, multidegrees, monomial
    support, recovery branches, exceptional components, conservative matrix
    and memory bounds, relation count, sparse linear algebra, offline/online
    work, and amortization.
  - A producer and a separate small validator that recomputes decisive
    arithmetic without importing producer conclusions.
  - One scoped desk disposition: `bounded_negative`, `inapplicable`,
    `inconclusive`, or `mechanism_specified_not_authorized`.
- Workstream C, parallel GLV connected-system rigidity:
  - A precise graph- or hypergraph-level statement for connected systems of
    exact local `S3` constraints.
  - A paper proof or a smallest counterexample, distinguishing polynomial
    covariance, zero-variety preservation, target-fibre transport,
    internal-variable phases, and exceptional components.
  - Independent adversarial review before Lean work.
  - If the statement survives, a narrow kernel-checked theorem package; if
    not, a scoped negative or counterexample record.
- Phase D, conditional native outcome:
  - This phase remains blocked unless Phase B retains an exact cost-changing
    mechanism, five digest-bound reviews and at least one external scientific
    review exist, and a separate dated owner decision authorizes one frozen
    toy candidate.
  - If unlocked, retain one toy-only native result with a matched baseline,
    fixed seeds and budgets, raw artifacts, two independent relation
    validators, and an engine-derived terminal label.
Exit criteria:
- Every scientific statement resolves to a primary-source anchor and read
  status.
- The Yokoyama result is represented as a scoped conditional lower bound for
  the naive class, not a no-go for Petit, Amadori, Kudo, or all structured
  factor bases.
- Amadori read status agrees across canonical and generated layers.
- Every desk number is integer/rational or carries an explicit interval and
  assumption; no decorative precision.
- The desk comparison uses full cost and a matched plain single-target
  baseline.
- A negative result closes only the tested construction, arity, and
  representation.
- The GLV theorem is limited to coordinatewise scalar `C3` and connected
  exact `S3` systems. It says nothing about arbitrary birational maps,
  geometric automorphisms, solving degree, or all GLV-Semaev algorithms.
- Certificate-backed exhaustiveness is not relabelled as a Lean theorem.
- No Sage, msolve, F4, Groebner scaling sweep, or secp256k1 DLP run occurs.
- Phase D remains blocked unless all explicit authorization prerequisites are
  satisfied. If run later, `secp256k1` remains a forbidden target and the
  outcome is retained even when negative or resource-exhausted.
Files allowed to edit:
- source and typed-evidence registries
- literature/source-card records
- a dated review note and comparison matrix
- a dedicated desk-screen directory under `experiments/engine/`
- a dedicated structural note or certificate directory
- a narrowly scoped Lean module only after the statement and proof are stable
- only after separate authorization, one candidate/run directory and its
  independent validator
- directly affected generators, tests, and generated views
Files that must be regenerated:
- all affected engine, source, typed-evidence, claim, graph, status, bundle,
  and site views
How to verify:
- source-registry and typed-evidence checks
- cross-registry semantic gate
- independent arithmetic replay and formula/threshold fault injection
- independent symbolic or finite-model counterexample search
- adversarial mathematical review
- certificate replay where used
- `lake build`, no-`sorry`, and full axiom audit for any Lean promotion
- decision-substrate and candidate-lifecycle checks
- raw-artifact replay and external review if Phase D is ever authorized
- generated-fixpoint and bundle checks
- independent claim-anchor review

Operational release criterion: v0.2 may be described as exercised as a
research machine only after three native outcomes, at least one external
scientific review, and at least one evidence-driven candidate decision change.
This is an operational milestone, not evidence of an ECDLP breakthrough.

### TASK-015 - Map the bounded hypothesis frontier and select one desk question

Status: completed_non_executable_scoped_blocker
Kind: literature | cost | data | research | review
Hypothesis: none. `CELL-M-PKC-SMOOTH-M16` is a research-question cell, not a
hypothesis, candidate, experiment, or selected attack route.
Desk priority: `CELL-M-PKC-SMOOTH-M16` / `RSI-D8BBA6340789`
Authorization: none
Outcome: `scoped_blocker`
Retention: `zero_retention_success`
Why it matters: The mathematical idea space is open-ended, but the actionable
frontier can be made finite relative to a versioned evidence snapshot,
mechanism grammar, route model, target properties, recovery contract, and cost
quantities. The existing knowledge graph already supplies that projection.
Choosing the exact M16 desk-cost cell avoids both a free-form idea search and
an unbounded auxiliary-curve search.
Decision boundary:
- WCC 2017 is a separate inspected source. It does not replace unread CANS
  2018 and supplies no novelty claim.
- WCC 2017 studies favorable `m=2` examples on selected 12.1-22.0-bit primes
  and explicitly makes no asymptotic claim. Its timing and speedup numbers do
  not transfer to secp256k1 `m=16` or S17.
- The M16 arithmetic predicates are already resolved. TASK-015 may address
  only the remaining null cost fields.
- `CELL-M-PKC-AUXILIARY-CURVE` remains parked until a primary source supplies
  a finite family or search domain with a completeness criterion.
Inputs:
- `repo/HYPOTHESIS_GENERATION_V0.json`
- `repo/ECDLP_TYPED_EVIDENCE_V0.json`
- `data/typed_evidence_state.json`
- `data/research_engine_state.json`
- `data/research_engine_shadow_intake.json`
- `data/knowledge_graph.json`
- `data/source_claim_extracts/yokota_kudo_yasuda2017_wcc.json`
- `data/source_claim_extracts/petit_kosters_messeng2016.json`
- `experiments/engine/pkc_smooth_desk_screen/artifact.json`
- `CQ-SEMAEV-S17-SYSTEM-COST`
Expected output:
- One generated finite hypothesis-space projection using the existing
  knowledge graph, with typed cell identity kept distinct from the three
  shared synthesis axes.
- One source card for WCC 2017 and an explicit CANS 2018 unread boundary.
- One residual desk contract for M16 covering symbolic direct-S17, recursive-S3,
  and source-faithful factor-base presentations without materializing a
  polynomial system or invoking a solver.
- Separate treatment of the source map's degree-13441 component and any
  equivalent low-degree exponentiation-circuit encoding, including recovery
  semantics and exceptional components.
- Exact symbolic degree, monomial-support, memory, preprocessing, recovery,
  independence, and total-cost bounds where derivable; otherwise the smallest
  explicit blocker.
- A terminal disposition of exact desk bridge, scoped blocker, or
  `zero_retention_success`.
Exit criteria:
- The knowledge graph remains schema 4.0 and no parallel atlas or Research
  Engine v0.3 is created.
- WCC claims attach only to broad prime-field total-cost evidence, not to the
  M16 cost quantity, auxiliary-curve property, or either typed cell.
- CANS 2018 remains `full_text_unread`.
- M16 remains an open, seed-eligible, non-executable cell until its complete
  cost bridge is independently reviewed.
- Auxiliary-curve applicability remains unknown and unselected.
- No materialized S17 or recursive system, solver execution, Sage, msolve, F4,
  parameter sweep,
  secp256k1 discrete-log computation, route promotion, novelty claim, or
  asymptotic claim is authorized.
- Zero retained hypotheses is an accepted result.
Files allowed to edit:
- source and typed-evidence registries
- the existing hypothesis-space guide and knowledge-graph generator
- the TASK-014 comparison note only as an explicitly dated TASK-015 addendum
- the current phase gates in `repo/ECDLP_DECISION_SUBSTRATE.json`, while
  `route_selection` remains unchanged
- `scripts/research_engine_lib.py` only for recognizing the current closed
  desk-priority mode, and the existing generated decision-view builder
- this task contract and append-only decision log
- directly affected tests and generated views
- a later dedicated symbolic desk artifact, but no solver or run directory
Files that must be regenerated:
- source, typed-evidence, claim, engine, shadow-intake, graph, status, decision,
  bundle, and site views
How to verify:
- source-registry and typed-evidence checks
- WCC/CANS non-conflation fault injection
- knowledge-graph edge and rendered-projection checks
- scientific-semantic and decision-substrate gates
- generated fixpoint and full repository CI

Recorded result:
- `experiments/engine/pkc_smooth_m16_symbolic_desk/artifact.json` fixes the
  exact source-chain, recursive-S3, quadratic-circuit, direct-recovery, and
  conditional matrix-template counts without materializing a system.
- `CQ-SEMAEV-S17-SYSTEM-COST` moves from `missing` to `partial`.
- `B-PKC-M16-COMPLETE-COST-BRIDGE` records the remaining open blocker.
- M16 remains open, seed-eligible, non-executable, and unselected; no desk
  closure, hypothesis retention, experiment authorization, or route promotion
  is created.

### TASK-016 - Fix the source-faithful M16 ideal and recovery semantics

Status: completed_non_executable_scoped_blocker
Kind: theorem | data | research | review
Hypothesis: none. This task defines the mathematical object that a later cost
argument would have to price; it is not a solver candidate.
Desk priority: `CELL-M-PKC-SMOOTH-M16` / `RSI-D8BBA6340789`
Cost quantity: `CQ-SEMAEV-S17-SYSTEM-COST`
Authorization: none
Outcome: `scoped_blocker`
Retention: `zero_retention_success`
Completed on: 2026-07-27
Artifact: `experiments/engine/pkc_smooth_m16_semantic_bridge/artifact.json`
Artifact SHA-256: `963eea60097807ae0aa66a5d881b0c34bf0497ade53ed4d37d38861a73887c19`
Why it matters: TASK-015 showed that low input degree can be obtained only by
adding variables, while solving degree, fill-in, recovery, and rank remain
unknown. Those quantities are not meaningful until direct S17, the recursive
S3 tree, and the source-factor membership circuit are related by an exact
base-field semantics with every exceptional fiber accounted for.
Decision boundary:
- The membership-only layer is fixed: `x^564522 - 1` has exactly 564522 simple
  roots in the base field, and its triangular source-factor circuit has unique
  intermediate values and no denominator components.
- Membership square-freeness must not be promoted to radicality, saturation,
  or completeness of the combined recursive-S3 system.
- The exact usable lift count, recursive partial sums at the identity,
  tangent and repeated-coordinate fibers, extension-field lifts, permutation
  multiplicities, and compatible sign recovery were the scoped uncertainty.
- CANS 2018 remains a separate `full_text_unread` source and the
  auxiliary-curve search remains parked.
Inputs:
- `experiments/engine/pkc_smooth_m16_symbolic_desk/artifact.json`
- `data/source_claim_extracts/petit_kosters_messeng2016.json`
- `Ecdlp/Proved/SemaevThree.lean`
- `Ecdlp/Proved/SemaevFour.lean`
- `Ecdlp/Proved/CurveCardinalityExact.lean`
- `repo/ECDLP_TYPED_EVIDENCE_V0.json`
- `CELL-M-PKC-SMOOTH-M16`
- `B-PKC-M16-COMPLETE-COST-BRIDGE`
Expected output:
- One explicit source-faithful affine presentation for the direct S17,
  recursive-S3 tree, and the 24-gate source-factor membership circuit, with
  constants, variable order, projection maps, and target-sign convention.
- A proof or independently replayable certificate for the membership-only
  projection and its simple-root property.
- A smallest counterexample or exact bridge for direct versus recursive
  semantics over the base field, explicitly treating saturation, projective
  components, partial sums at the identity, tangencies, repeated roots, and
  extension-field lifts.
- A deterministic recovery contract covering sign classes, permutations,
  duplicate points, GLV orbit coefficients, and exact final curve checks.
- A terminal disposition of exact semantic bridge, scoped blocker, or
  `zero_retention_success`.
Exit criteria:
- Every claimed equivalence states its field, localization or saturation,
  nondegeneracy assumptions, projection, inverse recovery map, and excluded
  components.
- A finite counterexample closes only its stated presentation and branch.
- No direct S17 expansion, system materialization, Sage, msolve, F4, Groebner
  sweep, exact-target relation search, discrete-log computation, or route
  promotion occurs.
- M16 stays open and non-executable unless a later dated decision changes the
  gate after independent review.
- If the semantic bridge succeeds, solving degree, memory, relation rank, and
  sparse linear algebra move to a separate later cost task. They are not
  inferred from input degree.
Files allowed to edit:
- a dedicated non-run semantic certificate directory under
  `experiments/engine/`
- a dated structural note
- directly affected source, typed-evidence, task, test, and generated views
- a narrow Lean module only after the statement and independent certificate
  are stable
Files that must be regenerated:
- typed-evidence, engine, shadow-intake, graph, status, decision, bundle, and
  site views affected by the result
How to verify:
- independent producer/validator replay
- finite-field counterexample fault injection where used
- source-map and recovery-contract review
- typed-evidence, scientific-semantic, and decision-substrate gates
- `lake build`, no-`sorry`, and axiom audit only if a Lean theorem is added
- generated fixpoint and full repository CI

Recorded result:
- The fixed labeled affine left-fold is exact only after base-field
  liftability and nonidentity-prefix localization. That topology is not
  unconditionally interchangeable with the direct signed-relation semantics.
- An exact same-`m,D,H` control witness shows an intended signed relation whose
  fixed affine ordering loses the identity prefix. A separate same-parameter
  witness shows that `x^D=1` can admit an extension-only curve lift and an S3
  common root outside the base field.
- The control multiset has 120 unique orders and 240 direct sign preimages.
  Exactly two preimages in the first order are blocked by the affine identity
  prefix; 238 remain affine-admissible, and all normalize to `14P-R=O`.
- The homogeneous Kummer form and its identity and tangent specializations are
  replayed, but the global projective-tree/direct-S17 equivalence is only the
  next proof target. It is not asserted here.
- `CQ-SEMAEV-S17-SYSTEM-COST` stays `partial`,
  `B-PKC-M16-COMPLETE-COST-BRIDGE` stays open but narrowed, and the M16 cell
  stays open, seed-eligible, non-executable, and unselected. No hypothesis,
  experiment, route promotion, cost advantage, or exact-target work follows.

### TASK-017 - Classify M16 exceptional fibers, liftability, and recovery domain

Status: active_non_executable_exceptional_fiber_classification
Kind: theorem | data | research | review
Hypothesis: none. This task closes the semantic domain needed before a later
solving-cost contract can be meaningful; it is not a solver candidate.
Desk priority: `CELL-M-PKC-SMOOTH-M16` / `RSI-D8BBA6340789`
Cost quantity: `CQ-SEMAEV-S17-SYSTEM-COST`
Authorization: none
Why it matters: TASK-016 disproved the naive global affine substitution and
isolated two independent exceptional mechanisms: identity prefixes and
extension-only or non-liftable fibers. The next useful result is a complete
set-theoretic classification of those fibers and a recovery domain, not a
choice from an unbounded hypothesis space and not a solving-degree estimate.
Decision boundary:
- Keep the direct S17 relation, the homogeneous projective S3 tree, its affine
  chart, and base-field recovery as separate predicates.
- Classify external non-lifts, internal extension-only roots, identity
  prefixes, repeated-coordinate tangent branches, rational two-torsion,
  duplicate roots, topology-dependent permutations, and GLV lift signs.
- Saturate only by projective irrelevant ideals that exclude `[0:0]`. Do not
  saturate by coordinate differences, because that removes valid tangent and
  duplicate strata.
- State only set-theoretic projection unless radicality, multiplicity, or
  scheme equality is independently proved.
- CANS 2018 remains `full_text_unread`; the auxiliary-curve search remains
  parked; `zero_retention_success` remains a valid outcome.
Inputs:
- `experiments/engine/pkc_smooth_m16_semantic_bridge/artifact.json`
- `data/source_claim_extracts/petit_kosters_messeng2016.json`
- `Ecdlp/Proved/SemaevThree.lean`
- `Ecdlp/Proved/SemaevFour.lean`
- `Ecdlp/Proved/CurveCardinalityExact.lean`
- `Ecdlp/Proved/GlvSubgroupEigenvalue.lean`
- `Ecdlp/Proved/GlvOrbit.lean`
- `repo/ECDLP_TYPED_EVIDENCE_V0.json`
- `CELL-M-PKC-SMOOTH-M16`
- `B-PKC-M16-COMPLETE-COST-BRIDGE`
Expected output:
- A frozen homogeneous caterpillar topology and exact projective predicate,
  including the identity tag and affine-chart localization.
- An independently replayable exceptional-fiber table with field, lift,
  multiplicity, projection, and recovery disposition for every named stratum.
- A deterministic base-field recovery certificate that distinguishes ordered
  topology tuples, coordinate multisets, signed point multisets, and
  GLV-normalized relation rows.
- Either a proved set-theoretic projective-tree/direct-S17 bridge on the stated
  domain or the smallest remaining counterexample with a narrowed blocker.
Exit criteria:
- Every accepted relation row has exact leaf lifts, target normalization,
  duplicate and GLV aggregation, topology multiplicity, and two final curve
  checks.
- Every rejected fiber has a named reason and cannot silently enter rank or
  yield accounting.
- No solving-degree, fill-in, memory, rank, sparse-linear-algebra, or full-cost
  claim starts until this task records a complete bridge or a new scoped
  blocker.
- No S17 expansion, materialized M16 solve, Sage, msolve, F4, Groebner sweep,
  exact-target relation search, discrete-log computation, experiment
  authorization, or route promotion occurs.
- M16 remains open and non-executable unless a later dated decision changes
  the gate after independent review.
Files allowed to edit:
- the TASK-016 semantic certificate directory or a successor non-run
  exceptional-fiber certificate directory under `experiments/engine/`
- directly affected source, typed-evidence, task, test, and generated views
- a narrow Lean module only after the statement and independent certificate
  are stable
Files that must be regenerated:
- typed-evidence, engine, shadow-intake, graph, status, decision, bundle, and
  site views affected by the result
How to verify:
- independent producer/validator replay
- finite-field and projective-specialization fault injection
- recovery-state, permutation, and GLV-normalization review
- typed-evidence, scientific-semantic, and decision-substrate gates
- `lake build`, no-`sorry`, and axiom audit only if a Lean theorem is added
- generated fixpoint and full repository CI
