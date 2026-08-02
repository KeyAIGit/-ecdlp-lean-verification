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

Execution lock for the `post-task026-decision-review` phase: no experiment is
executable or receives compute. `TASK-026` has reached its independently
validated terminal state and its singleton authorization is consumed. The
only admitted successor work is formulation and review of a source-faithful,
non-executable `HYP-M16-SOLVER-SLOPE-001` proposal; execution still requires
a separate dated authorization. The ML qualification contracts, `TASK-013`,
and `TASK-008` remain maintenance/intake references.

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
experiment, or enter native Research Engine calibration. A native candidate
experiment still requires an immutable candidate, validator evidence, and the
normal dated authorization path. The separate ML-P1E contract below authorizes
only a route-neutral engineering scaling qualification.

### ML-P1E toy-scaling qualification under TASK-013

State: active_engineering_qualification
Parent task: TASK-013
Kind: data | research | experiment-infrastructure
Hypothesis: none
Owner direction: 2026-07-27
Why it matters: P0 retained a bounded null for direct full-length scalar
prediction on secp256k1. Before replacing direct regression with explicit
mechanism or program search, the repository needs to determine whether the
same model families show transferable behavior as the field and group grow
together on independently held-out, structurally similar toy curves.
Authorized scope:
- route-neutral engineering qualification
  `ML-P1E-TOY-SCALING-2026-07-27-R2`;
- exact curves `y^2=x^3+7` at 13, 16, 20, and 24 field bits;
- explicit exclusion of all 40 field primes from the invalidated first
  catalog, bound by a committed SHA-256 list;
- ten independently certified prime-order curves per size, split into three
  train, four development, and three physically blind curves;
- six GLV-orbit-separated generators per curve;
- complete scalar-bit prediction from public curve, generator, and point data;
- 14 preregistered architectures, seven seeds, fixed controls, and matched
  generic BSGS/Pollard-rho baselines;
- physically separate development and blind data shards;
- one architecture selected at 13/16 bits, never reselected by 20-bit results,
  and committed with its complete selection ledger before blind shards open.
The replacement starts at 13 bits because the exact 12-bit family cannot
supply ten field-prime curve instances disjoint from the retired catalog.
Prohibited scope:
- secp256k1 evaluation;
- 28- or 32-bit execution;
- native Research Engine outcomes;
- route promotion or calibration;
- asymptotic, subgeneric, or key-recovery claims;
- treating model weights as an attack mechanism.
Expected output:
- deterministic curve catalog with exact independent point counts;
- roughly 1.1 million unique deterministic synthetic records;
- independent full replay of every `[d]G=Q` relation and exact
  scalar-to-split/generator allocation;
- complete selection and evaluation ledgers with no silently omitted fit;
- deliberate-leak canaries and five negative controls before blind opening;
- frozen raw predictions independently replayed against an exact public
  scalar-bit prior;
- group-law-verified beam recovery and per-target generic solver evidence;
- a bounded report whose conclusions apply only to the exact toy catalog.
Exit criteria:
- source, configuration, catalog, manifest, validations, and preregistration
  are hash-bound and committed before selection;
- selection opens only development shards on a clean source tree;
- all 219 selection/confirmation/control fits complete;
- all control gates pass before a blind-authorization recipe is emitted;
- the recipe and complete selection artifacts are committed before evaluation;
- a separate producer-independent selection validator passes from the
  committed selection artifacts without opening any dataset shard, and its
  report is committed before evaluation;
- all 28 frozen evaluation fits complete without recipe or dependency drift;
- the independent result validator passes from raw float32 predictions;
- any apparent transferable signal remains untrusted until converted into an
  explicit executable mechanism and admitted through the normal candidate
  lifecycle.
Files allowed to edit:
- `experiments/ml_structure_probe/p1_toy_scaling/`;
- `experiments/ml_structure_probe/reports/p1_toy_scaling/`;
- this task contract;
- the ML structure-probe package index.
Raw ignored files:
- `experiments/ml_structure_probe/artifacts/p1_toy_scaling/`.
How to verify:
- `python -m py_compile experiments/ml_structure_probe/p1_toy_scaling/*.py`;
- `python experiments/ml_structure_probe/p1_toy_scaling/test_p1.py`;
- independent curve, dataset, and result validators;
- repository artifact and status consistency gates.

This contract does not modify `experiments/HYPOTHESES.yaml`, native candidate
snapshots, owner-decision records, Research Engine outcomes, route evidence, or
exploration/promotion flags.

### TASK-013 - Build and calibrate Research Engine v0

Status: maintenance_non_executable_during_task026
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
- All ten hypotheses and historical runs normalized without rewriting
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

Status: maintenance_non_executable_during_task026
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

Status: completed_non_executable_scoped_blocker
Kind: theorem | data | research | review
Hypothesis: none. This task closes the semantic domain needed before a later
solving-cost contract can be meaningful; it is not a solver candidate.
Desk priority: `CELL-M-PKC-SMOOTH-M16` / `RSI-D8BBA6340789`
Cost quantity: `CQ-SEMAEV-S17-SYSTEM-COST`
Authorization: none
Outcome: `scoped_blocker`
Retention: `zero_retention_success`
Completed on: 2026-07-27
Artifact: `experiments/engine/pkc_smooth_m16_exceptional_fibers/artifact.json`
Artifact ID: `PKC-SMOOTH-M16-EXCEPTIONAL-FIBERS-001`
Artifact SHA-256: `578db732807a452e26de03dcd338d62c25a7d90490a62bbf427b1f96c3a869cf`
Why it matters: TASK-016 disproved the naive global affine substitution and
isolated two independent exceptional mechanisms: identity prefixes and
extension-only or non-liftable fibers. The next useful result is a complete
set-theoretic classification of those fibers and a recovery domain, not a
choice from an unbounded hypothesis space and not a solving-degree estimate.
Decision boundary:
- Keep the direct S17 relation, the homogeneous projective S3 tree, its affine
  chart, and base-field recovery as separate predicates.
- Restrict every local and projective theorem to the nonsingular curve
  `y^2=x^3+7` over fields of characteristic not in `{2,3,7}`.
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

Recorded result:
- For the nonsingular curve `y^2=x^3+7` in characteristic not in `{2,3,7}`,
  the homogeneous projective S3 caterpillar now has an exact set-theoretic
  signed-point bridge over the algebraic closure and, after external
  base-field liftability is imposed, over the base field.
- Identity inputs, repeated non-two-torsion tangents, repeated rational
  two-torsion, external non-lifts, internal extension-only prefixes,
  duplicates, topology permutations, and GLV lift signs have explicit
  recovery dispositions. Only the projective irrelevant pair `[0:0]` is
  excluded; coordinate-equality loci remain.
- The control replay fixes 120 coordinate orders, 240 normalized sign
  preimages, 239 projective fibers, 238 affine fibers, one identity fiber,
  and one normalized row `14P-R=O`. The secp256k1 M16 replay checks both the
  raw sixteen-leaf group identity and the duplicate-compressed GLV row.
- The direct S17 predicate remains unfrozen, and no reverse theorem above S4
  exists in the current repository. Therefore the result is a scoped blocker,
  not a direct-S17 bridge or a solving-cost result.
- Assurance is `certificate_replayed`, source independence is
  `not_established`, and calibration is `excluded_nonexperimental`.
  `CQ-SEMAEV-S17-SYSTEM-COST` stays `partial` while solving cost is
  `unpriced`; `B-PKC-M16-COMPLETE-COST-BRIDGE` is narrowed but stays open, and
  the M16 cell stays open, seed-eligible, non-executable, and unselected. No
  hypothesis, experiment, authorization, route promotion, rank, yield, or
  cost claim is created.

### TASK-018 - Freeze recursive projective S17 and prove the reverse projection

Status: completed_non_executable_scoped_blocker
Kind: theorem | data | research | review
Hypothesis: none. This task fixes the remaining mathematical predicate and
reverse implication needed before any later cost contract can be meaningful;
it is not a solver candidate.
Desk priority: `CELL-M-PKC-SMOOTH-M16` / `RSI-D8BBA6340789`
Cost quantity: `CQ-SEMAEV-S17-SYSTEM-COST`
Authorization: none
Outcome: `scoped_blocker`
Retention: `zero_retention_success`
Completed on: 2026-07-28
Artifact: `experiments/engine/pkc_smooth_m16_projective_bridge/artifact.json`
Artifact ID: `PKC-SMOOTH-M16-PROJECTIVE-S17-BRIDGE-001`
Artifact SHA-256: `3164cb89adac7622b4d08d781061ea386dc64e754236e48c838a3dac23040715`
Evidence claim: `SC-PKC-M16-PROJECTIVE-S17-BRIDGE-RESULT`
Why it matters: TASK-017 proves the complete set-theoretic projective S3-tree
semantics and recovery domain. TASK-018 was required to freeze the exact
recursive projective S17 object before any attempt to certify its universal
reverse projection or price a solver.
Decision boundary:
- Freeze one recursive projective S17 definition with explicit base cases,
  elimination variable order, homogeneous coordinates, fixed degrees, and the
  literal Sylvester determinant under the frozen coefficient, argument, and
  row order, with coefficient unit 1 in that definition and no primitive or
  content normalization. Projective rescaling follows the declared
  multidegree.
- Work on the nonsingular curve `y^2=x^3+7` over fields of characteristic not
  in `{2,3,7}`; do not transfer the TASK-017 theorem to characteristic seven.
- Keep the recursive S17 predicate, the homogeneous S3 caterpillar, its affine
  chart, and recovery as separate predicates until both implications are
  proved on a named field and domain.
- Any future equivalence claim must be only set-theoretic unless radicality,
  scheme equality, or multiplicity preservation is independently proved.
- Do not infer degree of regularity, fill-in, memory, rank, yield, or total
  work from recursive polynomial degree or input size.
- CANS 2018 remains `full_text_unread`; the auxiliary-curve search remains
  parked; `zero_retention_success` remains a valid outcome.
Inputs:
- `experiments/engine/pkc_smooth_m16_exceptional_fibers/artifact.json`
- `experiments/engine/pkc_smooth_m16_semantic_bridge/artifact.json`
- `data/source_claim_extracts/petit_kosters_messeng2016.json`
- `Ecdlp/Proved/SemaevThree.lean`
- `Ecdlp/Proved/SemaevFour.lean`
- `repo/ECDLP_TYPED_EVIDENCE_V0.json`
- `CELL-M-PKC-SMOOTH-M16`
- `B-PKC-M16-COMPLETE-COST-BRIDGE`
Recorded result:
- The certificate freezes the recursive projective S17 contract with explicit
  base cases, fixed-degree recurrence, and the literal Sylvester determinant
  under the frozen coefficient, argument, and row order, with coefficient
  unit 1 in that definition and no primitive or content normalization.
  Projective rescaling follows the declared multidegree. It does not expand,
  evaluate, or materialize S17.
- The forward projective-tree algebraic argument is recorded, but the generic
  C16 forward implication is not computationally replayed or kernel checked.
  Bounded S4/S5 forward/reverse fixtures, including the F5/F25 cases and
  exhaustive cases over primes 5, 11, and 13, are replayed as finite checks.
- These S5 fixtures do not establish the universal reverse projection above
  S4. That implication remains unproved, not false. Its narrow missing bridge
  is a kernel-checked fixed-degree projective resultant common-root theorem
  together with a lemma that specialization of recursive symbolic `C_r`,
  including output `[1:0]`, agrees with the fixed resultant at the previous
  step.
- Assurance is `certificate_replayed`, source independence is
  `not_established`, and calibration is `excluded_nonexperimental`.
  `CQ-SEMAEV-S17-SYSTEM-COST` stays `partial`; solving cost, rank, and yield
  stay `unpriced`. `B-PKC-M16-COMPLETE-COST-BRIDGE` is narrowed but stays
  open, and the M16 cell stays open, seed-eligible, non-executable, and
  unselected.
- No hypothesis, experiment authorization, route promotion, S17
  materialization, solver run, exact-target computation, or cost claim is
  created.

### TASK-019 - Kernelize fixed-degree projective resultants and reverse projection

Status: completed_non_executable_scoped_blocker
Kind: theorem | data | research | review
Hypothesis: none. This task tested the theorem-level bridge required by the
remaining universal reverse implication; it was not a solver candidate.
Desk priority: `CELL-M-PKC-SMOOTH-M16` / `RSI-D8BBA6340789`
Cost quantity: `CQ-SEMAEV-S17-SYSTEM-COST`
Authorization: none
Outcome: `scoped_blocker`
Retention: `zero_retention_success`
Completed on: 2026-07-28
Artifact:
- `experiments/engine/pkc_smooth_m16_projective_resultant_kernel/artifact.json`
- ID `PKC-SMOOTH-M16-PROJECTIVE-RESULTANT-KERNEL-001`
- SHA-256 `0b9d8b48953aae2defa28ade67992084cecca3a01b43490bc338a0fd5ce97c5a`
Why it matters: TASK-018 freezes the recursive projective S17 contract,
records its forward algebraic argument, and replays bounded S4/S5
forward/reverse fixtures, but finite fixtures cannot replace a universal
proof. TASK-019 isolates which part of that gap is generic resultant algebra
and which part still depends on the actual frozen recursion.
Inputs:
- `experiments/engine/pkc_smooth_m16_projective_bridge/artifact.json`
- `experiments/engine/pkc_smooth_m16_exceptional_fibers/artifact.json`
- `Ecdlp/Proved/SemaevThree.lean`
- `Ecdlp/Proved/SemaevFour.lean`
- `repo/ECDLP_TYPED_EVIDENCE_V0.json`
- `CELL-M-PKC-SMOOTH-M16`
- `B-PKC-M16-COMPLETE-COST-BRIDGE`
Recorded result:
- `Ecdlp.ProjectiveResultant.fixedDegree_resultant_eq_zero_iff_common_projective_root`
  is kernel checked. For positive formal degrees over an algebraically closed
  field, with explicit actual-degree bounds, the fixed resultant vanishes
  exactly when the two fixed-degree homogenizations share a non-irrelevant
  projective root. Zero forms and degree drops are included; the affine chart
  is `[x:1]`, the infinity witness is `[1:0]`, and `[0:0]` is excluded.
- The mapped and injective-base-change variants keep the coefficient map and
  formal degrees explicit. They prove generic fixed-resultant compatibility;
  they do not instantiate the frozen recursive symbolic `C_r`.
- `Ecdlp.TaskSylvester.taskSylvester_eq_reindex_transpose` and
  `det_taskSylvester_eq_resultant` kernel-check the literal TASK-018 matrix:
  first `n` shifted descending rows of `f`, then `m` of `g`, with descending
  columns. Simultaneous row/column reversal and transpose preserve the
  determinant exactly, so the coefficient unit is `1`; no primitive or
  content normalization is inserted. The end-to-end determinant/common-root
  theorem is also kernel checked.
- The non-run certificate independently binds the theorem statements and
  convention fixtures to TASK-018. Assurance is
  `kernel_bound_non_run_certificate`, source independence is
  `not_established`, calibration is `excluded_nonexperimental`, cost is
  `partial`, the barrier is `narrowed_open`, and retention is
  `zero_retention_success`. Its typed evidence claim is
  `SC-PKC-M16-PROJECTIVE-RESULTANT-KERNEL-RESULT`.
- The exact remaining blockers are the specialization theorem for the actual
  frozen recursive `C_r` at formal degrees `(2^(r-2), 2)`, including affine
  output and `[1:0]`, and the downstream universal reverse induction
  `C16 → C2`. Neither is refuted; neither is implied by the generic map
  theorem.
- `CQ-SEMAEV-S17-SYSTEM-COST` remains `partial`; solving cost, rank, and yield
  remain `unpriced`; `B-PKC-M16-COMPLETE-COST-BRIDGE` remains open; the route
  remains `open_parked`; and the M16 cell remains open, non-executable, and
  unselected. No S17 materialization, solver, exact-target computation,
  experiment authorization, cost claim, hypothesis retention, or route
  promotion is created.

### TASK-020 - Kernelize frozen recursive C_r specialization

Status: completed_non_executable_scoped_blocker
Kind: theorem | research | review
Hypothesis: none. This task tested the exact recursive-specialization bridge
left by TASK-019; it was not a solver candidate.
Desk priority: `CELL-M-PKC-SMOOTH-M16` / `RSI-D8BBA6340789`
Cost quantity: `CQ-SEMAEV-S17-SYSTEM-COST`
Authorization: none
Outcome: `scoped_blocker`
Retention: `zero_retention_success`
Completed on: 2026-07-28
Artifact:
- `experiments/engine/pkc_smooth_m16_frozen_cr_specialization/artifact.json`
- ID `PKC-SMOOTH-M16-FROZEN-CR-SPECIALIZATION-001`
- SHA-256 `d025053b9f882c88086fd5f04bcbd9627c72987e263e9b55af6024794305acbe`
Why it matters: TASK-019 proved the generic fixed-degree resultant theorem,
but that theorem did not name or constrain the actual frozen recursive
symbolic family. TASK-020 binds the real recursion before any universal
projective witness extraction is attempted.
Inputs:
- `experiments/engine/pkc_smooth_m16_projective_resultant_kernel/artifact.json`
- `experiments/engine/pkc_smooth_m16_projective_bridge/artifact.json`
- `Ecdlp/Proved/FixedDegreeProjectiveResultant.lean`
- `Ecdlp/Proved/TaskSylvesterConvention.lean`
- the frozen recursive projective `C_r` contract from TASK-018
- `CELL-M-PKC-SMOOTH-M16`
- `B-PKC-M16-COMPLETE-COST-BRIDGE`
Recorded result:
- `Ecdlp.FrozenProjectiveSemaev.frozenC` is the literal frozen left-fold
  family: stage `s` is `C_(s+2)`, stage `14` is `C16`, the new leaf is
  `Q_(s+3)`, and every successor uses formal degrees `(2^(s+1), 2)`.
- `specialize_frozenC_succ_over` kernel-checks exact specialization after an
  explicit coefficient map. The result is the literal TASK-018 Sylvester
  determinant with coefficient unit exactly `1`, unchanged argument and row
  order, and no primitive, content, monic, or actual-degree normalization.
  Same-field, affine `[y:1]`, and infinity `[1:0]` forms are separate
  corollaries, while `[0:0]` is excluded.
- `previousSliceAtOver_frozenC_natDegree_le` proves uniformly that the output
  slice of `C_(s+2)` has degree at most `2^(s+1)`. At a successor, the
  determinant has two rows constant in the new output and `2^(s+1)` rows of
  degree at most two, so no recursive degree hypothesis is needed.
- The uniform bound discharges the last hypothesis of the one-step resultant
  theorem. Both same-field and coefficient-map variants now state
  unconditionally that one frozen successor vanishes exactly when its
  predecessor slice and local literal `H` slice share a non-irrelevant
  projective root over an algebraically closed target field.
- All 23 public theorems in the module depend only on `propext`,
  `Classical.choice`, and `Quot.sound`; there is no `sorry`, `admit`, custom
  axiom, or `unsafe`.
- The independent certificate binds all stages `C2` through `C16`, the
  literal nine-term `H` including `-28`, fixed degrees, matrix dimensions,
  affine and infinity branches, theorem names, source hashes, and
  non-execution boundary. Its validator passes and all 73 semantic mutations
  are rejected. The typed evidence claim is
  `SC-PKC-M16-FROZEN-CR-SPECIALIZATION-RESULT`.
- The exact remaining theorem blocker is projective evaluation and recursive
  witness-chain assembly: a root of the fixed homogenized predecessor slice
  must be identified with specialization of the actual projective `C_r`, then
  recursively extracted from `C16` through `C2`. This is open, not refuted.
- `CQ-SEMAEV-S17-SYSTEM-COST` remains `partial`; solving cost, rank, and yield
  remain `unpriced`; `B-PKC-M16-COMPLETE-COST-BRIDGE` remains open; the route
  remains `open_parked`; and no S17 materialization, solver, exact-target
  computation, experiment authorization, cost claim, hypothesis retention,
  or route promotion is created.

### TASK-021 - Kernelize universal frozen C16-to-C2 projective witness extraction

Status: completed_non_executable_kernel_result
Kind: theorem | research | review
Hypothesis: none. This is the smallest exact theorem task left by TASK-020;
it is not a solver candidate or a cost experiment.
Desk priority: `CELL-M-PKC-SMOOTH-M16` / `RSI-D8BBA6340789`
Cost quantity: `CQ-SEMAEV-S17-SYSTEM-COST`
Authorization: none
Outcome: `closed_exact_theorem`
Retention: `zero_retention_success`
Completed on: 2026-07-28
Artifact:
- `experiments/engine/pkc_smooth_m16_frozen_projective_witness/artifact.json`
- ID `PKC-SMOOTH-M16-FROZEN-PROJECTIVE-WITNESS-001`
- SHA-256 `89c645545d89334473d51654a41ff7ec2364857d034c64ce08d505337fa1e2d4`
Why it matters: TASK-020 returns a non-irrelevant common projective root of
the fixed homogenized predecessor and local slices at every vanishing
successor. To recurse, those homogenized evaluations must be identified with
the actual projective frozen-family specialization, including `[1:0]`, and
the witnesses must be assembled into one exact chain.
Decision boundary:
- Prove the projective evaluation bridge for each valid pair `[U:V]`: the
  declared-degree homogenization of the predecessor output slice evaluates
  to the actual `frozenC` specialization, and the degree-two homogenized local
  slice evaluates to the literal `HValue`.
- Define only the minimal `FrozenProjectiveChain`: base `C2 = H`; a successor
  contains one valid projective intermediate, the predecessor chain, and the
  local `H` equation.
- Prove for every stage `s` and explicit coefficient map that
  `specializeOver φ q y (frozenC k s) = 0` is equivalent to that chain.
  Instantiate `s = 14` to obtain the universal `C16 → C2` witness extraction
  with infinity allowed at every level.
- If exact projective homogeneity or a top-coefficient identity is missing,
  isolate and kernel-check the smallest lemma rather than replacing it with
  an affine-only argument or finite fixture.
- Do not claim base-field liftability, `RatCat_Fp`, recovery, direct-S17
  equivalence, radicality, scheme equality, multiplicity preservation,
  relation yield, rank, solving degree, fill-in, memory, or total work.
- Do not expand or evaluate S17, materialize the M16 system, run a solver,
  parameter sweep, exact-target search, or discrete-log computation.
Recorded result:
- `projectiveOutputAtOver_frozenC_isHomogeneous` proves exact homogeneity of
  the actual universal binary output at declared degree `2^(s+1)`. The proof
  uses the literal Sylvester row split: two degree-zero predecessor rows and
  `2^(s+1)` degree-two local rows.
- `homogenize_previousSliceAtOver_frozenC` identifies the declared-degree
  predecessor homogenization with that actual universal binary output.
  `eval_homogenize_previousSliceAtOver_frozenC` then gives exact direct
  projective specialization for every valid pair. Separate affine and
  `[1:0]` corollaries compile.
- `homogenize_localSliceAt` and `eval_homogenize_localSliceAt` give the exact
  degree-two local bridge to literal `HValue`, again with separate affine and
  `[1:0]` corollaries.
- `FrozenProjectiveChain` is minimal: the base is `C2 = H`; each successor
  adds one valid projective intermediate, the predecessor chain, and one
  literal local `H` equation.
- `specializeOver_frozenC_eq_zero_iff_projectiveChain` proves the all-stage
  equivalence after every explicit coefficient map into an algebraically
  closed target field. No injectivity assumption is used.
- `specializeOver_frozenC16_eq_zero_iff_projectiveChain` instantiates stage
  `14`: leaves are `q 0` through `q 15` and the chain has fourteen
  existential intermediate projective slots. `[0:0]` is excluded by
  `ProjectivePair`; `[1:0]` is allowed at every level.
- The complete public module was built and independently replayed. Its axiom
  audit contains only `propext`, `Classical.choice`, and `Quot.sound`; there
  is no `sorry`, `admit`, custom axiom, or `unsafe`.
- The independent non-run certificate binds the source digests, theorem
  declarations, stage and leaf schedule, affine and infinity fixtures,
  algebraic-closure boundary, and non-execution disposition. Its validator
  passes and all 29 semantic mutations are rejected. The typed evidence
  claim is `SC-PKC-M16-FROZEN-PROJECTIVE-WITNESS-RESULT`.
- This theorem closes only the frozen-family projective witness-chain gap.
  It does not prove direct `RecS17 iff GeoCat`, base-field descent, `RatCat`,
  `Recover`, S17 materialization, relation yield, rank, solving degree,
  memory, recovery cost, or total work.
- `CQ-SEMAEV-S17-SYSTEM-COST` remains `partial`;
  `B-PKC-M16-COMPLETE-COST-BRIDGE` remains open; the route remains
  `open_parked`; no hypothesis, solver, experiment authorization, exact
  target computation, cost claim, or route promotion is created.
Inputs:
- `Ecdlp/Proved/FrozenRecursiveProjectiveSemaev.lean`
- `Ecdlp/Proved/FixedDegreeProjectiveResultant.lean`
- `experiments/engine/pkc_smooth_m16_frozen_cr_specialization/artifact.json`
- `experiments/engine/pkc_smooth_m16_projective_bridge/artifact.json`
- `CELL-M-PKC-SMOOTH-M16`
- `B-PKC-M16-COMPLETE-COST-BRIDGE`
Expected output:
- A kernel-checked projective homogenization/specialization bridge for the
  actual frozen family and local `H`.
- A kernel-checked all-stage chain equivalence and its `C16` corollary; or the
  smallest exact missing projective-homogeneity lemma.
- One narrow non-run certificate only if a new theorem result is obtained.
Exit criteria:
- The proof uses the actual `frozenC`, covers every valid `[U:V]`, excludes
  `[0:0]`, permits `[1:0]` at every recursive stage, and introduces no hidden
  normalization.
- Finite S4/S5 fixtures are not substituted for the universal proof.
- `CQ-SEMAEV-S17-SYSTEM-COST` stays `partial`, the complete-cost barrier stays
  open, the route stays `open_parked`, and authorization stays false.
Files allowed to edit:
- one narrow witness-chain Lean module and direct theorem dependencies
- one dedicated non-run TASK-021 certificate directory if the theorem closes
- directly affected canonical task and proof ledgers
Files that must be regenerated:
- only generated views directly affected by the final recorded result
How to verify:
- narrow Lean build, no-`sorry`, and exhaustive axiom audit
- affine and infinity projective-evaluation fixtures
- certificate validator and fault tests if a certificate is created
- scientific-semantic, non-execution, generated-fixpoint, and full CI gates

### TASK-022 - Materialize the frozen stage-14 guarded projective system

Status: completed_non_executable_kernel_result
Kind: theorem | research | review
Hypothesis: none. This is the smallest exact representation task left by
TASK-021; it is not a solver candidate or a cost experiment.
Desk priority: `CELL-M-PKC-SMOOTH-M16` / `RSI-D8BBA6340789`
Cost quantity: `CQ-SEMAEV-S17-SYSTEM-COST`
Authorization: none
Outcome: `closed_exact_theorem`
Retention: `zero_retention_success`
Completed on: 2026-07-29
Artifact:
- `experiments/engine/pkc_smooth_m16_guarded_projective_system/artifact.json`
- ID `PKC-SMOOTH-M16-GUARDED-PROJECTIVE-SYSTEM-001`
- SHA-256 `3445da55b44a71d0f40ee60206c90f2ef1798c28abd125542ce3acbeeb8e1d46`
Source:
- `Ecdlp/Proved/FrozenProjectiveGuardSystem.lean`
- SHA-256 `37feeef48e77437b44b6ae6dd4750782e19ecd824e3ea2e73b657e2fb8296fb9`
Typed claim:
- `SC-PKC-M16-GUARDED-PROJECTIVE-SYSTEM-RESULT`
Why it matters: TASK-021 proves an exact recursive chain of fourteen valid
projective witnesses, but the existential `ProjectivePair` representation is
not yet a finite scalar polynomial inventory. A guard
`A*U + B*V - 1 = 0` expresses exactly that `(U,V)` is not `[0:0]` over a
field while retaining `[1:0]`. The target representation is one literal finite
`MvPolynomial` family:
`∃ assignment : GuardVar → K, ∀ e : GuardedEquation,
MvPolynomial.eval assignment (guardedEquation q y e) = 0`.
Decision boundary:
- Work only with the already proved frozen stage-14 predicate
  `specialize q y (frozenC k 14) = 0`.
- Use an explicit injective coefficient map from a source field `k` to an
  algebraically closed target field `K`. Target witnesses need not descend
  to `k`; base-field descent is not claimed.
- Materialize fourteen raw `(U,V,A,B)` slots, fifteen literal `H` equations,
  and fourteen nonzero-pair guards.
- Prove only a total-degree upper bound. Do not state that every equation has
  exact degree four in every characteristic.
- Keep raw variable and equation counts distinct from dimension, relation
  independence, rank, or solver complexity.
- Do not expand or evaluate direct `S17`, emit solver input, run a solver,
  parameter sweep, exact-target search, or discrete-log computation.
Recorded result:
- `GuardCoordinate`, `GuardVar`, and `GuardedEquation` give the finite raw
  indices. `card_guardVar_fourteen` records 56 variables and
  `card_guarded_equations_fourteen` records 29 equation-family members.
  These two cardinality theorems use `native_decide` and therefore disclose
  compiler trust through `Lean.ofReduceBool`.
- `guardEquation` is the literal polynomial
  `A_i*U_i + B_i*V_i - 1`. `guardEquation_excludes_zero` rejects `[0:0]`,
  while `guardEquation_preserves_infinity` retains `[1:0]`.
- `guardedEquation` enumerates one base `H`, thirteen internal `H` steps,
  one final `H`, and fourteen guards. The inventory is fifteen `H` equations
  plus fourteen guards.
- `guardedEquation_totalDegree_le_four` proves only the uniform upper bound
  `totalDegree <= 4`; coefficient cancellation may lower actual degree in a
  particular characteristic.
- `FrozenGuardedProjectiveSystem` is literally one assignment satisfying
  every polynomial indexed by `GuardedEquation`.
  `frozenProjectiveChain_iff_guardedProjectiveSystem` proves this finite
  family is exactly the TASK-021 chain over a field; it is not a parallel
  recursive syntax.
- `frozenRecS17_iff_guardedProjectiveSystem_over` proves that, after an
  injective field map into an algebraically closed target, source-field
  vanishing of `frozenC k 14` is equivalent to the guarded target system.
- The result materializes the literal finite guarded polynomial family for
  the frozen recursive predicate only. It does not produce an expanded direct
  `S17`, descend target witnesses, remove chart/gauge or guard redundancy,
  establish independent relations, or determine yield, rank, solving degree,
  fill-in, memory, recovery cost, or total work.
- `CELL-M-PKC-SMOOTH-M16` remains `open_non_executable`;
  `CQ-SEMAEV-S17-SYSTEM-COST` remains `partial`;
  `B-PKC-M16-COMPLETE-COST-BRIDGE` remains open; the route remains
  `open_parked`; no hypothesis, solver, experiment authorization, exact
  target computation, cost claim, or route promotion is created.
Inputs:
- `Ecdlp/Proved/FrozenRecursiveProjectiveWitness.lean`
- `experiments/engine/pkc_smooth_m16_frozen_projective_witness/artifact.json`
- `CELL-M-PKC-SMOOTH-M16`
- `B-PKC-M16-COMPLETE-COST-BRIDGE`
Expected output:
- A kernel-checked literal finite guarded `MvPolynomial` family for the actual
  frozen stage-14 predicate.
- Exact raw counts and a degree upper bound, with compiler trust disclosed
  for finite-cardinality facts.
- One narrow non-run certificate bound to the Lean source digest.
Exit criteria:
- The source uses `Field k`, an injective `k -> K`, and
  `[Field K] [IsAlgClosed K]`.
- `[0:0]` is excluded and `[1:0]` is retained.
- The representation has fourteen slots, 56 raw variables, fifteen `H`
  equations, fourteen guards, and total degree at most four.
- The M16 cell and complete-cost barrier remain open and authorization stays
  false.
Files allowed to edit:
- one narrow guarded-system Lean module and direct import
- one dedicated non-run TASK-022 certificate directory
- directly affected canonical task, proof, evidence, and decision ledgers
Files that must be regenerated:
- only generated views directly affected by the final recorded result
How to verify:
- narrow and full Lean builds, built-source no-`sorry`, and exhaustive axiom
  audit
- exact source and artifact digest checks
- exhaustive finite-field guard fixture plus certificate fault tests
- typed-evidence, decision-substrate, scientific-semantic,
  generated-fixpoint, and full CI gates

### TASK-023 - Replace guarded projective redundancy by an exact chart cover

Status: completed_non_executable_kernel_result
Kind: theorem | research | review
Hypothesis: none. This is an exact representation refinement of TASK-022,
not a solver candidate, relation-yield claim, or cost experiment.
Desk priority: `CELL-M-PKC-SMOOTH-M16` / `RSI-D8BBA6340789`
Cost quantity: `CQ-SEMAEV-S17-SYSTEM-COST`
Authorization: none
Outcome: `closed_exact_theorem`
Retention: `zero_retention_success`
Completed on: 2026-07-29
Artifact:
- `experiments/engine/pkc_smooth_m16_exact_chart_cover/artifact.json`
- ID `PKC-SMOOTH-M16-EXACT-CHART-COVER-001`
- SHA-256 `934809fabbb8c98c5ed9356a0a1f3367a23f8fbc1bc86239069942537fd678ed`
Source:
- `Ecdlp/Proved/FrozenProjectiveChartSystem.lean`
- SHA-256 `4f7b95453d8fafba3ec9cae0a9bbad5d8f782c6c0202f6e7cf37e17981b63019`
Typed claim:
- `SC-PKC-M16-EXACT-CHART-COVER-RESULT`
Why it matters: TASK-022 gives an exact finite polynomial system, but its
four `(U,V,A,B)` scalars and one guard per projective slot retain both
projective-scale and guard-witness redundancy. Every valid projective pair
over a field lies in exactly the needed two-chart cover: the infinity branch
uses `[1:0]`, while the affine branch uses `[X:1]`. Selecting one branch for
each of fourteen intermediate slots leaves, for a fixed mask `I`,
exactly `14 - |I|` scalar variables and fifteen literal `H` equations.
Decision boundary:
- Work only with the already proved stage-14 frozen predicate, TASK-021
  projective chain, and TASK-022 guarded system.
- Use `InfinityMask := Finset (Fin 14)`. For `i` in the mask, fix the slot to
  `[1:0]`; otherwise represent it by one scalar `[X_i:1]`.
- Materialize a literal fixed-mask `MvPolynomial` family indexed by one base,
  thirteen internal steps, and one final equation.
- Prove exact equivalence between the chart-polynomial cover, the projective
  chain, the guarded representation, and the injective base-change frozen
  stage-14 predicate.
- Prove only degree upper bounds: base at most two, internal step at most
  four, final at most two, and hence a uniform ceiling of four.
- Count variables and equations only as representation inventory. Do not
  infer dimension, independence, rank, relation yield, or solving cost.
- Do not enumerate or materialize all `2^14` masks in Lean. A finite-set
  existential is the cover.
- Do not emit solver input, run a solver, perform a parameter sweep, search an
  exact target, or compute a discrete logarithm.
Recorded result:
- `InfinityMask := Finset (Fin 14)` selects the distinguished infinity
  representative `[1:0]`; every other slot is represented by one affine
  scalar `[X_i:1]`. Normalization is proved through a nonzero projective
  scaling factor, so `[0:0]` is never introduced.
- `FrozenChartPolynomialSystem` is a literal fixed-mask `MvPolynomial` family
  indexed by `ChartEquation`. `card_chartEquation` records exactly fifteen
  equations and uses `native_decide`; `card_chartVar` proves by an ordinary
  kernel proof that a mask `I` has exactly `14 - I.card` variables.
- `chartPolynomialEquation_base_totalDegree_le_two`,
  `chartPolynomialEquation_step_totalDegree_le_four`, and
  `chartPolynomialEquation_final_totalDegree_le_two` prove family-specific
  upper bounds `2/4/2`. The uniform degree-four theorem is only a ceiling;
  infinity substitutions or coefficient cancellation may lower a concrete
  degree.
- `frozenProjectiveChain_iff_chartPolynomialCover` proves exact equivalence
  with the TASK-021 chain.
  `frozenGuardedProjectiveSystem_iff_chartPolynomialCover` proves exact
  equivalence with TASK-022 while removing its guard and projective-scale
  redundancy branchwise.
  `frozenRecS17_iff_chartPolynomialCover_over` binds the same cover to the
  source frozen stage-14 predicate after the existing injective map into an
  algebraically closed target. Target witnesses need not descend to the
  source field.
- The logical cover quantifies over `2^14` possible masks, but neither Lean
  nor the certificate enumerates or materializes those 16384 branches.
- The source target builds in Lean with 1941 jobs. A narrow axiom audit shows
  only `propext`, `Classical.choice`, and `Quot.sound`, except that
  `card_chartEquation` additionally discloses its `native_decide` marker.
- The independent source-bound certificate validates all 24 nonzero F5
  coordinate pairs, six projective points, 216 reduced three-slot chains,
  all eight reduced masks, and the nine literal `H` exponent patterns. Its
  final validator, eight tests, sidecar, and exactly 60 semantic mutations
  pass.
- This closes only exact chart/gauge representation redundancy. It does not
  establish independent relations, dimension, relation yield, rank, solving
  degree, fill-in, memory, recovery, runtime, or complete cost.
- `CELL-M-PKC-SMOOTH-M16` remains `open_non_executable`;
  `CQ-SEMAEV-S17-SYSTEM-COST` remains `partial`;
  `B-PKC-M16-COMPLETE-COST-BRIDGE` remains open; the route remains
  `open_parked`; no hypothesis, solver, experiment authorization, exact
  target computation, cost claim, or route promotion is created.
Inputs:
- `Ecdlp/Proved/FrozenProjectiveGuardSystem.lean`
- `experiments/engine/pkc_smooth_m16_guarded_projective_system/artifact.json`
- `CELL-M-PKC-SMOOTH-M16`
- `B-PKC-M16-COMPLETE-COST-BRIDGE`
Expected output:
- One kernel-checked chart-cover module with a literal fixed-mask polynomial
  family and exact equivalence theorems.
- Exact fixed-mask counts and degree ceilings, with any compiler-trusted
  finite-cardinality fact explicitly disclosed.
- One narrow source-bound non-run certificate if the theorem closes.
Exit criteria:
- `[1:0]` is retained, `[0:0]` is never introduced, and normalization uses
  only a proved nonzero projective scale.
- Every fixed mask has `14 - |I|` variables, exactly fifteen equations, and
  degree ceilings `2/4/2`.
- The chart-polynomial cover is iff the TASK-021 chain, TASK-022 guarded
  system, and source frozen stage-14 predicate after the existing injective
  algebraically closed base change.
- `CELL-M-PKC-SMOOTH-M16` stays `open_non_executable`;
  `CQ-SEMAEV-S17-SYSTEM-COST` stays `partial`;
  `B-PKC-M16-COMPLETE-COST-BRIDGE` stays open; no hypothesis, solver,
  experiment authorization, cost claim, exact-target work, or route promotion
  is created.
Files allowed to edit:
- one narrow chart-cover Lean module and direct import
- one dedicated non-run TASK-023 certificate directory
- directly affected canonical task, proof, evidence, and decision ledgers
Files that must be regenerated:
- only generated views directly affected by the final recorded result
How to verify:
- narrow and full Lean builds, built-source no-`sorry`, and exhaustive axiom
  audit
- exact source and artifact digest checks
- chart-normalization fixtures plus certificate semantic fault tests
- typed-evidence, decision-substrate, scientific-semantic,
  generated-fixpoint, and full CI gates

### TASK-024 - Prove necessary infinity-stratum pruning

Status: completed_non_executable_kernel_result
Kind: theorem | research | review
Hypothesis: none. This is a necessary-mask refinement of TASK-023, not a
solver candidate, relation-yield claim, or cost experiment.
Desk priority: `CELL-M-PKC-SMOOTH-M16` / `RSI-D8BBA6340789`
Cost quantity: `CQ-SEMAEV-S17-SYSTEM-COST`
Authorization: none
Outcome: `closed_exact_theorem`
Retention: `zero_retention_success`
Completed on: 2026-07-29
Artifact:
- `experiments/engine/pkc_smooth_m16_infinity_strata/artifact.json`
- ID `PKC-SMOOTH-M16-INFINITY-STRATA-001`
- SHA-256 `54b0f3c5f2f1880b1f805911df21b72e5427b18871f14907ac17a1d8b48bdd39`
Source:
- `Ecdlp/Proved/FrozenProjectiveInfinityStrata.lean`
- SHA-256 `1314477f9821da87d2017837abca4fec957ae9998390a231e93532230129a22c`
Typed claim:
- `SC-PKC-M16-INFINITY-STRATA-RESULT`
Why it matters: TASK-023 proves an exact cover over all `2^14 = 16384`
affine/infinity masks but does not distinguish masks that cannot occur. The
local triquadratic `H` identities at `[1:0]` expose exact necessary
conditions. With affine external inputs, adjacent infinity slots would force
an external projective `v` coordinate to vanish, so every solution mask is a
separated subset of the fourteen-slot path. This reduces the exact logical
cover to 987 masks without a solver or production enumeration.
Decision boundary:
- Work only with the TASK-023 chart system and its literal polynomial cover.
- Prove all three one-infinity identities as squared projective
  determinants, plus the two-recursive-endpoint identity
  `H([1:0],q,[1:0]) = q.v^2`.
- Under the explicit assumption that every external input is affine, prove
  that no solution mask contains adjacent infinity slots.
- Record the necessary endpoint determinant conditions for selected boundary
  infinity slots.
- Prove that nonzero endpoint determinants force slots 0 and 13 to be affine,
  leaving the 377 separated masks on the twelve interior slots.
- Prove that an isolated infinity slot forces an existing affine neighbor to
  the normalized coordinate `q.u / q.v`.
- Restrict the exact chart and chart-polynomial covers only by proved
  necessary predicates. Do not claim the predicates are sufficient.
- Do not enumerate the production mask family, emit solver input, run a
  solver, estimate rank or relation yield, search an exact target, or compute
  a discrete logarithm.
Recorded result:
- `HValue_third_infinity`, `HValue_first_infinity`, and
  `HValue_middle_infinity` identify each one-infinity specialization with a
  squared projective determinant.
- `HValue_first_third_infinity` proves that two adjacent recursive infinity
  slots expose the intervening input's `v` coordinate squared.
- `frozenChartSystem_separatedInfinityMask` proves that affine external
  inputs make every solution mask separated.
- `frozenChartSystem_endpointCompatibleInfinityMask` records the exact
  determinant equations forced by infinity at the first or last slot.
- The left- and right-infinity neighbor theorems prove the normalized
  coordinate forced on an affine neighbor.
- `frozenChartCover_iff_admissibleChartCover` and
  `frozenProjectiveChain_iff_admissibleChartPolynomialCover` prove that the
  necessary-mask restriction loses no solution under the affine-input
  assumption.
- With nonzero endpoint determinants,
  `frozenChartCover_iff_interiorChartCover` further removes both boundary
  infinity slots.
- `card_infinityMask`, `card_separatedInfinityMask`, and
  `card_interiorSeparatedInfinityMask` record exact counts 16384, 987, and
  377. These three facts use `native_decide`; the identities, necessity
  results, forced-neighbor results, and cover equivalences use ordinary
  kernel-checked proofs.
- The source target builds in Lean with 1942 jobs. Its narrow axiom audit
  contains only the standard `propext`, `Classical.choice`, and `Quot.sound`
  dependencies for structural results, with the compiler-trust marker
  separately disclosed for the three cardinalities.
- The independent source-bound certificate derives both path counts by
  recurrence, checks all four infinity identities and the forced-neighbor
  fixture over F5 and F7, validates upstream and source hashes, and rejects
  exactly 49 semantic mutations.
- This closes only necessary infinity-mask pruning. It does not supply a
  sufficient or unique mask selector, relation independence, yield, rank,
  solving degree, fill-in, memory, recovery, runtime, or complete cost.
- `CELL-M-PKC-SMOOTH-M16` remains `open_non_executable`;
  `CQ-SEMAEV-S17-SYSTEM-COST` remains `partial`;
  `B-PKC-M16-COMPLETE-COST-BRIDGE` remains open; the route remains
  `open_parked`; no hypothesis, solver, experiment authorization, exact
  target computation, cost claim, or route promotion is created.
Inputs:
- `Ecdlp/Proved/FrozenProjectiveChartSystem.lean`
- `experiments/engine/pkc_smooth_m16_exact_chart_cover/artifact.json`
- `CELL-M-PKC-SMOOTH-M16`
- `B-PKC-M16-COMPLETE-COST-BRIDGE`
Expected output:
- One kernel-checked infinity-stratum module with exact local identities,
  necessary mask constraints, forced-neighbor theorems, and exact restricted
  cover equivalences.
- Exact logical mask counts, with compiler trust explicitly disclosed.
- One narrow source-bound non-run certificate.
Exit criteria:
- Affine external inputs imply separated masks, giving 987 rather than 16384
  logical branches without production enumeration.
- Nonzero endpoint determinants imply the conditional 377-mask interior
  cover.
- The pruned covers are exactly equivalent to TASK-023 under their stated
  assumptions, and no sufficiency or solver claim is made.
- `CELL-M-PKC-SMOOTH-M16` stays `open_non_executable`;
  `CQ-SEMAEV-S17-SYSTEM-COST` stays `partial`;
  `B-PKC-M16-COMPLETE-COST-BRIDGE` stays open; no hypothesis, solver,
  experiment authorization, cost claim, exact-target work, or route promotion
  is created.
Files allowed to edit:
- one narrow infinity-stratum Lean module and direct import
- one dedicated non-run TASK-024 certificate directory
- directly affected canonical task, proof, evidence, and decision ledgers
Files that must be regenerated:
- only generated views directly affected by the final recorded result
How to verify:
- narrow and full Lean builds, built-source no-`sorry`, and exhaustive axiom
  audit
- exact source and artifact digest checks
- independent path-count and F5/F7 identity fixtures plus certificate fault
  tests
- typed-evidence, decision-substrate, scientific-semantic,
  generated-fixpoint, and full CI gates

### TASK-025 - Propagate infinity constraints to a conditional affine chart

Status: completed_non_executable_kernel_result
Kind: theorem | research | review
Hypothesis: none. This is a bounded propagation refinement of TASK-024, not a
solver candidate, relation-yield claim, or cost experiment.
Desk priority: `CELL-M-PKC-SMOOTH-M16` / `RSI-D8BBA6340789`
Cost quantity: `CQ-SEMAEV-S17-SYSTEM-COST`
Authorization: none
Outcome: `closed_exact_theorem`
Retention: `zero_retention_success`
Completed on: 2026-07-29
Artifact:
- `experiments/engine/pkc_smooth_m16_infinity_propagation/artifact.json`
- ID `PKC-SMOOTH-M16-INFINITY-PROPAGATION-001`
- SHA-256 `9330603ba1f0af9ee4902c263200709e2ec6f8c50d8d7eaab3b55bcba78e388f`
Source:
- `Ecdlp/Proved/FrozenProjectiveInfinityPropagation.lean`
- SHA-256 `7f868aab5b946a55a213ce26a461477321d6387830eed218c414f1e62853b4b4`
Typed claim:
- `SC-PKC-M16-INFINITY-PROPAGATION-RESULT`
Why it matters: TASK-024 conditionally leaves 377 interior separated masks
and proves that every isolated infinity fixes its adjacent affine
coordinates. TASK-025 substitutes those forced coordinates into the
neighboring literal `H` equations, extracts explicit exceptional polynomial
conditions, and proves that a precisely stated balanced nonvanishing condition
makes the empty infinity mask complete. A one-chart conclusion means only one
affine representation branch on that conditional locus, not one solution or
an ECDLP shortcut.
Decision boundary:
- Work only with the exact TASK-023 chart system, TASK-024 infinity
  identities and forced-neighbor theorems, and the existing literal `frozenC`
  family.
- Prove local distance-two propagation: two infinity slots at distance two
  force the corresponding consecutive external-input projective determinant
  to vanish.
- Prove local distance-three propagation: two infinity slots at distance
  three force the corresponding literal three-input `HValue` to vanish.
- Under explicit nonzero endpoint and local exceptional-polynomial
  assumptions, restrict the exact cover to the resulting mask predicates and
  record exact logical mask counts with the compiler-trust boundary disclosed.
  In particular, prove the cumulative conditional
  `377 -> 129 -> 69 -> 36` reduction and the independent boundary-only
  `129 -> 60` reduction without claiming that the remaining masks are
  realizable.
- Define explicit propagated prefix obstruction values by specializing the
  existing literal frozen prefixes after substituting the affine coordinate
  forced by an isolated infinity slot. Prove that selecting that infinity
  slot forces its obstruction value to vanish.
- Balance the global obstruction family into six prefix and six suffix
  values, covering all twelve internal slots with maximum frozen stage five.
- If pointwise nonvanishing of those twelve explicit obstruction values
  excludes every infinity slot, prove that the complete chart and
  chart-polynomial covers are exactly equivalent to the single empty-mask
  affine chart.
- Call this locus generic only if the relevant obstruction expressions are
  also proved nonzero as symbolic polynomials. Otherwise record a conditional
  affine locus and the exact symbolic-nonzeroness blocker; do not replace it
  with an unsupported probability statement.
- Do not enumerate or materialize the production mask family, expand direct
  `S17`, emit solver input, run a solver or parameter sweep, estimate
  yield/rank/cost, search an exact target, or compute a discrete logarithm.
Recorded result:
- `frozenChartSystem_gapTwoInfinity_forces_det_zero` proves over any field
  that infinity at slots `i` and `i + 2` forces
  `projectiveDet(q(i+2),q(i+3)) = 0`.
- `frozenChartSystem_gapThreeInfinity_forces_HValue_zero` proves over any
  field that infinity at slots `i` and `i + 3` forces the literal condition
  `HValue(q(i+2),q(i+3),q(i+4)) = 0`. The slot-one and slot-twelve theorems
  prove the two boundary-near literal `HValue` conditions.
- Under the named affine-input, endpoint, and local nonvanishing assumptions,
  the exact logical mask family contracts cumulatively
  `377 -> 129 -> 69 -> 36`. The separately useful boundary-only refinement
  contracts `129 -> 60`. These are candidate-mask family sizes, not counts of
  realizable masks.
- `card_gapTwoInteriorInfinityMask`,
  `card_gapThreeInteriorInfinityMask`,
  `card_boundaryPropagatedInfinityMask`, and
  `card_boundaryGapThreeInfinityMask` are the four new compiler-trusted
  `native_decide` count facts. The propagation identities, mask-necessity
  theorems, one-way resultant argument, and cover equivalences use ordinary
  Lean/Mathlib proofs.
- `specializeOver_frozenC_eq_zero_of_projectiveChain` proves the one-way
  projective-chain-to-literal-`frozenC` implication over any field. A
  prefix-only family gives twelve obstructions with possible stages through
  eleven; the balanced construction replaces it by six prefix and six suffix
  values and keeps the maximum frozen stage at five.
- With affine external inputs, nonzero endpoint determinants, and all twelve
  balanced obstruction values nonzero, every solution mask is empty. Both
  the semantic chart cover and the literal chart-polynomial cover are then
  exactly equivalent to the single empty-mask affine chart.
- `frozenRecS17_iff_affineChartPolynomialCover_over_of_balancedPropagatedRegular`
  binds the source stage-14 frozen equation to that target affine chart after
  the existing injective map into an algebraically closed field. Algebraic
  closure is needed only by the upstream source-equation/witness bridge; the
  propagation and empty-mask theorems hold over every field. No target
  witness descent to the source field is proved.
- Symbolic nonzeroness, nonemptiness, density, probability, or genericity of
  the regular locus is not proved. Neither are witness uniqueness, relation
  independence, yield, rank, solver behavior, solving degree, fill-in,
  memory, recovery, runtime, total cost, or an ECDLP shortcut.
- The source-bound certificate validates the exact source and upstream
  digests, independently derives the mask counts by recurrence, replays
  finite-field propagation fixtures, and passes 7 tests covering 101
  semantic mutations.
- `CELL-M-PKC-SMOOTH-M16` remains `open_non_executable`;
  `CQ-SEMAEV-S17-SYSTEM-COST` remains `partial`;
  `B-PKC-M16-COMPLETE-COST-BRIDGE` remains open; the route remains
  `open_parked`; no hypothesis, solver, experiment authorization, exact
  target computation, cost claim, route rejection, or route promotion is
  created. No successor execution is authorized by this closeout.
Inputs:
- `Ecdlp/Proved/FrozenProjectiveInfinityStrata.lean`
- `Ecdlp/Proved/FrozenRecursiveProjectiveWitness.lean`
- `experiments/engine/pkc_smooth_m16_infinity_strata/artifact.json`
- `CELL-M-PKC-SMOOTH-M16`
- `B-PKC-M16-COMPLETE-COST-BRIDGE`
Expected output:
- One narrow kernel-checked infinity-propagation module with explicit local
  exceptional conditions and exact restricted-cover equivalences.
- A conditional single all-affine-chart theorem only under explicit
  obstruction nonvanishing assumptions.
- One narrow source-bound non-run certificate if a theorem closes.
Exit criteria:
- Every claimed mask reduction is exact under named assumptions and loses no
  solutions.
- No generic-locus claim is made because symbolic nonzeroness and nonemptiness
  of the explicit regularity conditions remain unproved.
- "One chart" stays distinct from uniqueness of witnesses, relation
  independence, solver readiness, or reduced ECDLP asymptotics.
- `CELL-M-PKC-SMOOTH-M16` stays `open_non_executable`;
  `CQ-SEMAEV-S17-SYSTEM-COST` stays `partial`;
  `B-PKC-M16-COMPLETE-COST-BRIDGE` stays open; the route stays
  `open_parked`; no experiment, hypothesis retention, solver authorization,
  exact-target work, cost claim, route rejection, or route promotion is
  created.
Files allowed to edit:
- one narrow infinity-propagation Lean module and direct import
- one dedicated non-run TASK-025 certificate directory if a theorem closes
- directly affected canonical task, proof, evidence, and decision ledgers
Files that must be regenerated:
- only generated views directly affected by the final recorded result
How to verify:
- narrow and full Lean builds, built-source no-`sorry`, and exhaustive axiom
  audit
- exact source, upstream, and artifact digest checks
- independent finite-field propagation fixtures and certificate semantic
  fault tests
- typed-evidence, decision-substrate, scientific-semantic,
  generated-fixpoint, and full CI gates

### TASK-026 - Measure fixed-target balanced-regular yield on frozen toy E7 subgroups

Status: completed_independently_validated_terminal
Kind: experiment | research | review
Hypothesis: `HYP-M16-FIXED-TARGET-YIELD-001`
Decision: `HYP-SELECT-002`
Authorization:
`AUTH-HYP-M16-FIXED-TARGET-YIELD-001-20260730-01`
Authorization source commit:
`0b1b36851aa0f82c3a1bd587d385775923153d9c`
Model: classical representation-aware, synthetic toy data only
Route state: `R-PETIT-COMPOSED-MAPS` remains `open_parked`; the
`GLV_ORBIT_CLOSED` arm is a matched ablation, not the parent route
Promotion: false
Outcome event: `REO-2026-07-31-001`
Normalized outcome: `supported` for the exact enabling availability claim
Terminal: `CLASSIFY_AS_KNOWN_LOCAL_SIMPLIFICATION`
Authorization state: consumed; rerun authorized: false
Validator artifact:
`experiments/engine/pkc_smooth_m16_fixed_target_yield/artifact.json`
SHA-256:
`21a95ea4ea71c02d0199c331e549ca2e4ec2fbf7c1d8d70fe6651bea292d6413`
Observed result: all 3,000,000 primary trials and all 30 cells completed.
The run accepted 911 exact relations, of which 907 were affine regular.
Every curve-arm regularity gate passed. Orbit-minus-plain theta differences
were `-0.006987`, `-0.006329`, and `0.000000`; their intervals overlapped at
all three sizes and no size qualified for `H_NEW`. Thus the primary enabling
availability claim is supported, while the GLV-specific new-mechanism
explanation is bounded negative. This is not a solver, rank, recovery,
secp256k1, scaling, or ECDLP-complexity result.
Why it matters: TASK-025 proves that explicit endpoint and balanced
nonvanishing assumptions reduce the exact projective cover to one affine
chart, but it does not show that fixed-before-sampling targets admit enough
such relations to make that chart usable. This task performs the cheapest
precommitted test that can kill that continuation before any solver work.
It does not test a secp256k1 key, a faithful PKC factor base, solver scaling,
rank, recovery, or total ECDLP cost.
Decision boundary:
- Execute only the canonical singleton authorization in
  `repo/ECDLP_DECISION_SUBSTRATE.json`.
- Use exactly the three frozen `E_7` toy subgroup rows, two frozen arms, five
  frozen seeds, 384 stored coordinates, and the exact target-before-leaves
  chronology in `experiment_config.json`.
- Use only self-generated public toy targets. The target scalar is never
  exposed to or recorded by the runtime sampler.
- Cap the run at 3,000,000 primary trials, four CPU-hours, 4 GiB peak RSS,
  and 24 wall-clock hours. A completely replayed resource-capped prefix is a
  valid `PAUSE_INCONCLUSIVE` outcome and must be retained.
- Independently validate the raw transcript, frozen commitments, arithmetic,
  TASK-025 endpoint and balanced-regular labels, controls, summary, terminal
  decision, resource receipt, and authorization binding.
- Accept only the preregistered terminal values
  `PROMOTE_TO_SOLVER_SLOPE_TEST`,
  `CLASSIFY_AS_KNOWN_LOCAL_SIMPLIFICATION`,
  `KILL_AFFINE_M16_CONTINUATION`, `PAUSE_INCONCLUSIVE`, or
  `REJECT_AS_ARTIFACT`.
- Even `PROMOTE_TO_SOLVER_SLOPE_TEST` only permits a later proposal for
  `HYP-M16-SOLVER-SLOPE-001`; it does not authorize that solver test.
- Do not edit the five hash-bound source files, alter seeds or thresholds,
  run a solver, expand direct `S17`, target secp256k1, infer a 256-bit slope,
  promote the route, or discard an unfavorable result.
Bound source hashes:
- `PREREGISTRATION.md`:
  `e41164b1e8950aab60849e567949a230d592652d9b7ae2484eaed5dff7518cc5`
- `curve_table.json`:
  `a59ed1a8b597bc5d512438d09fbb4c970fff74dd704f8f88be4f7224775f5e0d`
- `experiment_config.json`:
  `34265beeba540ab03a5c738519eef7acaf1504a96a2f6e73b993c8af773a7c64`
- `run.py`:
  `7fe8bc7d4aff18e42fbfbb9c03ae9e5cec4bacc4c39eb00fb718096dd163384a`
- `validate.py`:
  `9f89bd4f1708f94235ff9f3c76de7db4dd7b05d42911e118b21d5f9592639d7c`
Inputs:
- `notes/reviews/HYP_SELECT_002.md`
- `experiments/engine/pkc_smooth_m16_fixed_target_yield/PREREGISTRATION.md`
- `experiments/engine/pkc_smooth_m16_fixed_target_yield/curve_table.json`
- `experiments/engine/pkc_smooth_m16_fixed_target_yield/experiment_config.json`
- `experiments/engine/pkc_smooth_m16_fixed_target_yield/run.py`
- `experiments/engine/pkc_smooth_m16_fixed_target_yield/validate.py`
- the exact singleton in `repo/ECDLP_DECISION_SUBSTRATE.json`
Expected output:
- `experiments/engine/pkc_smooth_m16_fixed_target_yield/run_manifest.json`
- `experiments/engine/pkc_smooth_m16_fixed_target_yield/raw/transcript.jsonl`
- `experiments/engine/pkc_smooth_m16_fixed_target_yield/summary.json`
- validator-owned
  `experiments/engine/pkc_smooth_m16_fixed_target_yield/artifact.json`
- validator-owned
  `experiments/engine/pkc_smooth_m16_fixed_target_yield/artifact.sha256`
- one outcome report and append-only decision/hypothesis transition entries
  that state what was and was not resolved
Exit criteria:
- Producer and independent validator both replay the exact approved singleton
  and all five readiness-source hashes before any primary trial is written.
- The run stops at the first scientific or resource terminal and preserves
  every completed cell plus at most one independently replayable partial
  final cell.
- The validator emits the canonical artifact only after complete replay and
  the artifact sidecar verifies.
- The outcome is classified by the exact Section 13 preregistration rules;
  controls may block `H_NEW` but cannot silently rewrite the primary
  fixed-target decision.
- The route stays `open_parked`, selected attack route stays null, native
  bounded exploration and promotion remain closed, and no result is
  described as a secp256k1 attack or complexity improvement.
Files allowed to edit:
- only canonical outcome paths under
  `experiments/engine/pkc_smooth_m16_fixed_target_yield/`
- directly affected append-only hypothesis, task, evidence, and decision
  ledgers after validation
- generated views required by those final source changes
Files that must not be edited:
- the five hash-bound source files listed above
- Lean theorem sources
- route definitions or promotion gates during execution
How to verify:
- `python3 experiments/engine/pkc_smooth_m16_fixed_target_yield/run.py --check-authorization`
- `python3 experiments/engine/pkc_smooth_m16_fixed_target_yield/validate.py --authorization`
- `python3 experiments/engine/pkc_smooth_m16_fixed_target_yield/test_validate.py`
- after execution, independent full replay plus `sha256sum -c artifact.sha256`
- decision-substrate, scientific-semantic, generated-fixpoint, artifact,
  branch-inventory, and full CI gates

### TASK-027 - Recompute the exact M16 factor-base census and current proposal regime

Status: completed_non_experimental_certificate
Kind: structural applicability | desk | review
Hypothesis: `HYP-M16-SOLVER-SLOPE-001` remains non-executable
Route state: `R-PETIT-COMPOSED-MAPS` remains `open_parked`
Authorization: none
Calibration: excluded_nonexperimental
Outcome: exact census confirmed; current proposal regime inapplicable only for
M16 exponent inference
Lifecycle: the census changes the scoped M16 evidence-cell identity. Immutable
proposal `HGP-M16-SOLVER-SLOPE-001` is retained as historical-only under
`stale_seed_snapshot`; the then-current seed `HGS-029AFA3EA451` required a new
source-grounded, non-executable draft.
Artifact:
- `experiments/engine/pkc_smooth_m16_regime_assurance_desk/artifact.json`
- ID `PKC-SMOOTH-M16-REGIME-ASSURANCE-DESK-001`
- SHA-256 `dc514544bf388562a3ebed312aef56bc87b00527f32ce6d131a2f5371dba2744`
Typed claim:
- `SC-PKC-M16-SECP-FACTOR-BASE-CENSUS`

Why it matters: the source heuristic used all `D=564522` subgroup
coordinates, while the exact curve factor base depends on whether
`x^3+7` is a square. This task resolves that target property and records
separate exact conditioned null comparators before any solver proposal can
interpret a toy slope. These comparators do not establish the actual group-sum
distribution and may leave additional zero-sum configurations uncounted. The
task also binds the immutable proposal's own statement that its current
at-most-24-bit ladder is calibration-only.

Recorded result:
- The exact quadratic-character sum over the subgroup is `2532`.
- Exactly `283527` subgroup coordinates lift, `280995` do not lift, and none
  has zero right-hand side; both signs give `567054` affine factor points.
- Explicit three-element GLV orbits give `94509` liftable x orbits,
  `189018` signed-point orbits, and `94509` orbit classes after pairing the two
  y signs by elliptic-curve point negation. Calling these classes usable
  factor-log columns would require additional relation and group-action
  semantics not asserted by this certificate.
- Exact rational models retain the source heuristic `D^16/(16!*p)`, signed
  multiset and distinct-point uniform-null comparators, and the ordered
  repeat probability without using floating-point values as evidence.
- The proposal's current `<=24`-bit ladder remains inapplicable to exponent
  inference. This is a property of that frozen execution regime, not a
  falsification of M16.

Decision boundary:
- This task performs exact public-parameter structural/applicability
  arithmetic only. It does not use a private or third-party target.
- Do not construct S17, run a solver, repeat TASK-026, perform a scaling
  sweep, compute a discrete logarithm, or authorize an experiment.
- Do not infer an actual group-sum distribution, relation independence, rank,
  solving degree, fill-in,
  recovery cost, sparse-linear-algebra cost, total attack cost, or an
  asymptotic advantage from the conditioned comparators.
- Keep `CELL-M-PKC-SMOOTH-M16` open, its complete-cost barrier unresolved,
  the route parked, and all promotion and exact-target gates closed.
- Kudo full-text status and global novelty are outside this certificate.

Independent replay:
- The producer finds one exact-order-`D` generator and enumerates `D/3`
  explicit GLV orbit representatives.
- The validator constructs the four prime-order components independently,
  multiplies them, enumerates all `D` subgroup elements, and recomputes the
  census, orbits, combinations, falling factorial, and reduced fractions
  without importing the producer.
- Path and artifact independence are checked. Source independence remains
  `not_established`.

How to verify:
- `python3 experiments/engine/pkc_smooth_m16_regime_assurance_desk/generate.py --check`
- `python3 experiments/engine/pkc_smooth_m16_regime_assurance_desk/validate.py`
- `python3 experiments/engine/pkc_smooth_m16_regime_assurance_desk/test_validate.py`
- `sha256sum -c experiments/engine/pkc_smooth_m16_regime_assurance_desk/artifact.sha256`
- typed-evidence, claim-level, scientific-semantic, generated-fixpoint,
  no-sorry, axiom-audit, docs-sync, and full CI gates

### TASK-028 - Close the source-faithful M16 mechanism and sound acceptance contract

Status: completed_nonexperimental_certificate
Kind: primary-source mechanism | recovery acceptance | desk review
Hypothesis: the published M16 input mechanism can be specified exactly without
pretending that generalized-root solving or complete cost is known
Route state: `R-PETIT-COMPOSED-MAPS` remains `open_parked`
Authorization: none
Calibration: excluded_nonexperimental
Outcome: `mechanism_specified_cost_unresolved`
Lifecycle: exact source claims and the versioned mechanism certificate produce
current seed `HGS-3266E42A729C`; the earlier submitted proposal remains an immutable,
historical-only stale snapshot.
Artifact:
- `experiments/engine/pkc_smooth_m16_source_faithful_mechanism/artifact.json`
- ID `PKC-M16-SOURCE-FAITHFUL-MECHANISM-RECOVERY-001`
- SHA-256 `79ee65104cfbd45ee902fbf59524a705e6db8590c8d5845a6a20cd63239c774c`

Why it matters: the typed cell previously cited a coarse source summary while
the exact map chain, System (4), recovery boundary, and partial cost formula
were distributed across prose and older certificates. This task binds those
facts to exact primary-source locators and separates source statements from
repository-derived completion semantics.

Recorded result:
- With factors `2,3,7,13441`, the literal source chain is
  `L1(x)=x^2`, `L2(x)=x^3`, `L3(x)=x^7`, and
  `L4(x)=1-x^13441`, hence `L=1-x^564522`.
- At arity sixteen the direct source System (4) has 64 factor coordinates,
  48 transition equations, 16 terminal equations, and one target-specialized
  `S17` relation, for 65 equation members.
- A quadratic addition-chain circuit may encode the same pointwise membership
  predicate, but no equality of ideals, solving degree, fill-in, or solving
  complexity follows from that equivalence.
- Algorithm 1 samples `(X,Y)=aP+bQ` and inserts `X` into System (4), while its
  printed Step 4c says `sum_i P_i=O` without explicitly binding the recovered
  relation to `(X,Y)`. For `R != O`, the canonical repository completion
  therefore accepts only an independently checked signed relation
  `sum_i epsilon_i P_i + epsilon_R R = O` and records the target sign. This is
  a sound acceptance filter, not a proof that every direct-System-(4) solution
  is recovered. If `R=O`, affine `X` is undefined and the sample must be
  resampled or handled separately.
- The source supplies the partial formula
  `P(p,16)+(16!*p/D^15)T(E,16,L)+D^omega`, but supplies no dedicated
  generalized-root algorithm or complete-cost theorem for `T`.

Decision boundary:
- Treat the map and System-(4) input as specified, not the solver or cost bridge.
- Treat the target-bound rule as a derived sound acceptance filter, not as a
  verbatim source claim or a complete direct-System-(4) recovery theorem.
- Restrict the displayed affine specialization to `R != O`; resample or handle
  the identity target separately.
- Keep source independence `not_established`, the M16 cell `open`, retention
  zero, and every solver, exact-target, experiment, promotion, and novelty gate
  closed.
- Do not infer recovery completeness, relation independence, rank, solving
  degree, recovery distribution, sparse-linear-algebra cost, or an ECDLP
  improvement.

How to verify:
- `python3 experiments/engine/pkc_smooth_m16_source_faithful_mechanism/generate.py --check`
- `python3 experiments/engine/pkc_smooth_m16_source_faithful_mechanism/validate.py`
- `python3 experiments/engine/pkc_smooth_m16_source_faithful_mechanism/test_validate.py`
- `sha256sum -c experiments/engine/pkc_smooth_m16_source_faithful_mechanism/artifact.sha256`
- typed-evidence, claim-level, scientific-semantic, generated-fixpoint,
  no-sorry, axiom-audit, docs-sync, and full CI gates

### TASK-029 - Attempt the source-grounded M16 complete-cost proposal

Status: completed by strict abstention on 2026-08-01

Kind: source-grounded proposal drafting | provenance replay | non-scientific memory

Hypothesis: the current typed evidence either supports one exact M16 complete-cost
proposal or must produce a source-bound abstention naming the smallest missing
mechanism and cost objects

Seed: `HGS-3266E42A729C`

Cell: `CELL-M-PKC-SMOOTH-M16`

Route: `R-PETIT-COMPOSED-MAPS` remains `open_parked`

Why it matters: an ungrounded model can turn an unspecified solver request into a
plausible-looking proposal. Retaining a verified abstention prevents that failure
from being repeated while keeping the unresolved route and cell scientifically open.

Question: does the current source-grounded packet support an exact,
non-executable `HYP-M16-SOLVER-SLOPE-001` proposal rather than a request to invent
an unspecified generalized-root solver?

Result:

- the exact source mechanism, fixed-target scope, partial cost expression, and
  sound acceptance filter are retained;
- no supplied claim specifies the generalized-root algorithm `A`, complete
  direct-System-(4) recovery, or a common-unit cost theorem;
- the correct output is `not_specified_due_to_abstention`;
- `HGA-M16-COST-BRIDGE-ABSTAIN-001` is immutable untrusted search memory only;
- proposal count, scientific outcomes, Brier calibration, ranker training,
  route/cell status, recommendation, authorization, and execution are unchanged.

Exact blockers:

- `MISSING-M16-GR-SOLVER-001`
- `MISSING-M16-COST-THEOREM-001`
- `missing_independent_validator_plan`
- `review_independence_unestablished`

The engine deterministically replays the seed/source/packet/fragment bindings and
fails closed under source-commit, typed-evidence, source-claim, fragment, or
authorization mutation. Future source-grounded prompts receive the attempt as
untrusted memory and must resolve its blockers rather than repeat them.

Canonical note:
`notes/TASK029_M16_COST_BRIDGE_ABSTENTION.md`

No TASK-026 rerun, solver, direct secp256k1 target, experiment, promotion, or
novelty claim is authorized.

How to verify:

- `python3 scripts/check_research_engine.py`
- `python3 scripts/test_research_engine.py`
- `python3 scripts/test_hypothesis_model_drafter.py`
- generated-fixpoint, artifact, scientific-semantic, no-sorry, axiom-audit,
  docs-sync, and full CI gates
