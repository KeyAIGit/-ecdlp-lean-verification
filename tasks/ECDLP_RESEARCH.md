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

Status: active_non_executable_universal_recursive_extraction
Kind: theorem | research | review
Hypothesis: none. This is the smallest exact theorem task left by TASK-020;
it is not a solver candidate or a cost experiment.
Desk priority: `CELL-M-PKC-SMOOTH-M16` / `RSI-D8BBA6340789`
Cost quantity: `CQ-SEMAEV-S17-SYSTEM-COST`
Authorization: none
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
