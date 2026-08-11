# ECDLP computational lab implementation contract

ID: `ECDLP-LAB-001`
Status: planned_owner_directed_engineering_program
Kind: experiment-infrastructure | validation | ops
Hypothesis: none
Scientific authorization: none
Owner direction: 2026-08-11
Execution model: one umbrella task, ordered phases `P00` through `P10`

## 1. Outcome

Build a small, reproducible computational laboratory that can evaluate future
classical ECDLP method candidates on deterministic synthetic toy groups. The
laboratory must provide:

- a neutral executable BSGS and seeded-rho reference;
- independently validated toy-curve inputs;
- a safe, resumable campaign runner;
- provenance, cost, operation-count, and validation receipts;
- scaling diagnostics that cannot silently become asymptotic claims;
- an isolated SageMath/Singular/PARI/SymPy workbench;
- a narrow p-adic/theta precision-conformance layer;
- a profile-gated native acceleration path;
- content-addressed local artifacts and dry-run remote job bundles.

This task builds engineering infrastructure only. It does not select, execute,
retain, or promote a scientific hypothesis and it does not modify the current
plain single-target secp256k1 decision.

## 2. Repository facts this contract must preserve

The repository is not empty. The lab must adapt existing assets instead of
creating a parallel research system.

| Existing asset | Current role | Lab rule |
|---|---|---|
| `experiments/framework/candidate_run.schema.json` and `candidate_contract.py` | Canonical candidate evidence gate | Do not replace or widen its authorization enums |
| `experiments/framework/ec_oracle.py` | Independent toy EC result verifier, limited to fields of at most 32 bits | Use for output validation; never add DLP search to it |
| `experiments/engine/cost_contract.schema.json` | Canonical full-cost vocabulary | Reuse its cost meanings; do not invent conflicting units |
| `experiments/engine/{run,instance_result,instance_validation,validator_*}.schema.json` | Research Engine candidate lifecycle | Read-only reference; lab records never become Engine records automatically |
| `experiments/ml_structure_probe/p1_toy_scaling/curve_math.py` | Deterministic stdlib toy-curve arithmetic and order-certificate producer | Reuse through a narrow adapter |
| `experiments/ml_structure_probe/p1_toy_scaling/validate_curves.py` | Independent catalog validation pattern | Reuse its validation logic, not producer arithmetic |
| committed P1 catalog | 40 prime-order `y^2=x^3+7` curves at 13, 16, 20, and 24 field bits | Import as immutable legacy input; never regenerate or rewrite it |
| `run_assay.py` BSGS/rho implementation and committed assay result | Existing matched generic baseline evidence | Preserve as immutable historical implementation and golden comparison |
| `experiments/p0_glv_semaev/manifest.py` and runs | Legacy experiment provenance | Do not rewrite historical manifests; reuse lessons through new code |
| `scripts/hypothesis_space_campaign.py` | Policy-coupled deterministic receipts, locks, resume, and replay | Reuse patterns only; do not import its scientific policy or run namespace |
| efficient-endomorphism, summation-polynomial, and division-polynomial producers and validators | Existing exact/symbolic replay assets | Reference and adapt; do not fork formula implementations silently |
| draft PR #356, `research/theta-screen-002` at `7a76a73` | Unmerged bounded theta/Kummer/Jacobi screen | Treat as upstream pending; never copy it silently into the lab |

The top ML README contains an old reference to a 12-bit rung. The package
config, schema, package README, and committed catalog are authoritative: the
current retained sizes are 13, 16, 20, and 24 bits.

## 3. Current preflight state

Observed on `main` commit `be7a2715768ef5a120e0db2b8851e3a143b3670e` on
2026-08-11:

- `scripts/check_repo_artifacts.py`: pass;
- `scripts/check_status_consistency.py`: pass;
- `scripts/check_scientific_semantics.py`: pass;
- `scripts/check_generated_fixpoint.py --check`: pass on a clean checkout;
- the lab task was not yet included in the small agent bundle;
- PR #356 is draft, open, mergeable, unmerged, and red;
- PR #356 CI fails on stale source-registry output and a parent-funnel root
  mismatch within that branch;
- PR #356 still requires an independent Sage replay and an explicit owner
  disposition before merge.

Every red gate must be reproduced against clean `main` before attribution. A
new hand-authored document can change the generated source registry and thereby
invalidate a frozen funnel binding even when it contains no scientific result.
The lab contract must not be merged until the clean-tree gate remains green,
and no mismatch may be mislabeled as inherited or weakened away.

## 4. Canonical placement

All new laboratory implementation belongs under the already classified
reproducible-experiment surface:

```text
experiments/ecdlp_lab/
  README.md
  contracts/
  core/
  curves/
  methods/
    python/
    sage/
    padic_theta/
    native/
  orchestration/
  analysis/
  env/
    docker/
    locks/
  remote/
    storage/
    jobs/
    providers/
  fixtures/
  replay_fixtures/
  tests/
  .work/                 # ignored raw runs and build products
```

Operator entrypoints may live under `scripts/lab_*.py`. A path-scoped workflow
may live at `.github/workflows/lab-ci.yml` and must be classified in
`repo/AUTOMATION_INVENTORY.json` in the same phase.

Do not create top-level `research_lab/`, `results/`, `environments/`, or
`infrastructure/`. Do not create a generic `certificates/` directory: CAS
producer output is not a proof certificate merely because it is exact.

## 5. Immutable denylist

No phase in this umbrella task may edit:

- `repo/ECDLP_DECISION_SUBSTRATE.json`;
- `repo/RESEARCH_ENGINE_V0.json` or `repo/RESEARCH_ENGINE_LIFECYCLE_V0.json`;
- other `repo/RESEARCH_ENGINE*`, typed-evidence, or research-claim policies;
- `experiments/HYPOTHESES.yaml`;
- `experiments/engine/proposals/`, `proposal_reviews/`, `outcomes/`, or `runs/`;
- existing P0/P1 run manifests, result bundles, raw predictions, or reports;
- generated scientific state under `data/` except outputs changed through an
  existing required generator because a permitted documentation file changed;
- `VERIFIED.md`, `VERIFIED_RESEARCHOS.md`, `Ecdlp/Proved/`, or theorem imports;
- PR #356 historical result files or note by copying or rewriting them from the
  lab branch.

If implementation requires changing one of these paths, stop that phase and
create a separate owner-reviewed task. This contract does not supply the
missing authority.

## 6. Lab record boundary

A lab execution uses:

```text
record_kind                 = lab_engineering_fixture
hypothesis_id               = null
candidate_id                = null
authorization_id            = null
native_research_outcome     = false
route_effect                = none
retention_class             = engineering_only
```

A lab fixture is not an `exploration`, `promotion`, Engine native run, or
scientific outcome. Lab code must never write to Engine event directories or
generated scientific state.

The engineering runner has a non-configurable safety ceiling:

- subgroup order is at most 32 bits;
- every curve and target vector resolves to a digest-bound committed lab or
  read-only legacy synthetic catalog;
- arbitrary curve parameters, arbitrary target points, URLs, wallet material,
  unknown catalog digests, and secp256k1-sized groups are rejected before
  method dispatch;
- the ceiling cannot be raised by config, environment, CLI, plugin, or backend.

The lab may export a neutral, content-addressed bundle. There is no submit,
compile-candidate, register-hypothesis, or promote command. A future Engine
adapter requires a separately reviewed candidate and authorization task.

## 7. Contract decomposition

Use JSON as the canonical configuration format. Core offline validation must
depend only on Python 3.12 standard library. YAML may be a later optional input
adapter but never the hashed source of truth.

Define only lab-specific contracts:

1. `campaign_config`: requested matrix, budgets, and allowed method IDs.
2. `target_vector`: public curve/generator/target identity and private expected
   scalar receipt split at generation time.
3. `work_unit`: one fully expanded deterministic unit.
4. `method_request`: sanitized public input delivered to the method process.
5. `method_result`: candidate scalar or bounded failure plus backend counters.
6. `telemetry`: observational time, RSS, platform, and tool versions.
7. `validation_receipt`: independent output and provenance validation.
8. `analysis_summary`: deterministic normalized comparison and warnings.
9. `artifact_ref`: digest, size, media type, role, and optional location.

Do not duplicate the full candidate or Engine schemas. Add a machine-readable
mapping/gap document showing where each lab field agrees with the existing
candidate, cost, result, validation, and provenance vocabulary.

### Canonical hashing

- UTF-8 JSON, sorted keys, compact separators, no insignificant whitespace.
- Reject NaN, infinity, negative zero, duplicate keys, and unknown fields.
- Use integers for nanoseconds, bytes, and counters. Use decimal strings where
  a non-integer value must enter a hashed semantic payload.
- `work_unit_id` is derived from canonical JSON and cannot be supplied freely.
- `campaign_id` and `work_unit_id` are semantic identities. A retry changes
  only a derived `attempt_id`; a code, config, method, validator, curve, or
  vector digest change creates a different work unit.
- Observational telemetry is outside the deterministic semantic digest.
- Canonical clean runs bind the 40-hex source commit, clean-tree state, source
  snapshot digest, producer dependency hashes, validator dependency hashes,
  inputs, and config.
- Dirty-tree runs are development-only and non-retainable. If allowed locally,
  bind the exact diff digest.

### Anti-cheat split

The target-generation seed and expected scalar belong only in a private
fixture-generation receipt and the independent validator input. The method
subprocess receives only public `(curve, G, Q, subgroup_order)` data, a separate
algorithm seed, and an explicitly public interval when applicable. It must
never receive the scalar, its derivation seed, a target-answer file, a DLP
oracle, or an unpriced lookup table.

## 8. Method and cost model

The primary cross-backend unit is a group-law invocation. Also record, with
backend-labelled semantics:

- nontrivial additions and doublings;
- inversions, multiplications, squarings, and negations that the implementation
  explicitly performs;
- table entries and estimated algorithmic table bytes;
- restarts, collisions, noninvertible collisions, and distinguished points;
- offline setup and online target work separately;
- reusable setup, amortization target count, workers, CPU/GPU hours, storage,
  money, implementation/reviewer effort, and empirical success probability.

Do not pretend Python `pow` internals expose field-multiplication counts. Keep
estimated algorithmic memory separate from measured process RSS. Field counters
from affine, projective, Python, Rust, or GPU implementations are not directly
equal unless a conversion is explicitly justified.

The primary scaling variable is `log2(subgroup_order)`, not a nominal catalog
label or only the field bit length.

## 9. Ordered phases

Only the first incomplete phase whose dependencies are green is actionable.
Later phases remain blocked. Every phase is a separately reviewable and
revertible PR from current `main`.

### P00: health, inventory, and upstream reconciliation

Status: ready
Allowed paths: task/router/bundle documentation and generated routing views

Deliverables:

- Record a clean baseline gate report at current `main`.
- Verify that adding the contract and routing files leaves the source-registry
  and generated-fixpoint chain green without modifying frozen funnel policy.
- Inventory every reused source and immutable output with path, role, digest,
  mutation policy, and owning validator.
- Record PR #356 state, head/base commits, CI, independent-replay status, and
  owner disposition. Do not merge it as part of the lab task.
- Include this contract in the small agent bundle through
  `scripts/export_agent_bundle.py`, then regenerate `bundles/MANIFEST.json` only
  through the generator.

Exit criteria:

- current `main` passes the complete existing health battery;
- the reuse inventory has no unclassified or silently mutable legacy input;
- bundle check passes;
- PR #356 is either `upstream_pending`, `accepted_on_main`, or `parked`, with
  evidence for that exact state.

### P01: lab contracts, canonical JSON, and path-scoped CI

Status: blocked_by_P00
Allowed paths: `experiments/ecdlp_lab/contracts/`, `core/`, `fixtures/`,
`tests/`, `experiments/README.md`, `.github/workflows/lab-ci.yml`,
`repo/AUTOMATION_INVENTORY.json`

Deliverables:

- Implement the eight contracts from section 7 and dependency-free semantic
  validators.
- Implement canonical JSON and content hashing.
- Add positive and adversarial fixtures.
- Add a path-scoped, no-schedule, no-paid-resource lab workflow.
- PR checks run only the bounded Python suite. Sage and native jobs are manual
  or capability-gated and cannot report a fabricated pass.

Required negative fixtures:

- unknown field, NaN/infinity/negative zero, malformed digest;
- absolute path, `..`, symlink escape, duplicate JSON key;
- missing provenance, dirty run marked retainable, self-validation;
- hidden precomputation, target scalar in method request, shared target seed;
- candidate/hypothesis/authorization ID supplied to a lab fixture;
- attempted write or conversion to an Engine run.
- exact secp256k1 parameters, a 33-bit subgroup, an external target point, and
  an unknown catalog/vector digest.

Exit criteria:

- stdlib-only offline tests pass in under 60 seconds and 512 MiB;
- `experiments/framework/test_framework.py` remains green;
- automation inventory and repository artifact checks pass.

### P02: lab fixture catalog and independent curve validation

Status: blocked_by_P01
Allowed paths: `experiments/ecdlp_lab/curves/`, `fixtures/`, `tests/`

Deliverables:

- Add a read-only adapter for the existing 40-curve P1 catalog.
- Add a very small CI fixture catalog whose generation is deterministic and
  bounded to at most 16 field bits.
- Distinguish `field_bits` and `subgroup_order_bits`.
- Define precise families:
  - `j0_glv_like`: secp-shaped toy curves with verified public beta/lambda;
  - `random_non_cm_prime_subgroup`: non-j=0 controls with subgroup and cofactor;
  - `j0_no_fp_glv_control`: a named j=0 control where the expected base-field
    efficient-endomorphism property is absent and validated.
- Record full curve order when certified, subgroup order, cofactor, generator,
  family property, and exact order-certificate type and inputs.

Validation rules:

- producer arithmetic may adapt P1 `curve_math.py`;
- validator arithmetic must use `experiments/framework/ec_oracle.py` or another
  producer-independent implementation;
- for a cofactor-one prime order `N`, verify primality, nonzero `G`, `[N]G=O`,
  and the Hasse uniqueness condition `2N > upper` instead of enumerating all
  points at 28 or 32 bits;
- the program does not execute or commit new 28/32-bit scientific catalogs;
  those sizes may be represented only as future configuration.

Exit criteria:

- repeated small-fixture generation is byte-identical;
- corruption of `p`, `a`, `b`, order, cofactor, generator, endomorphism
  constants, or
  certificate is rejected independently;
- existing P1 artifacts are byte-for-byte unchanged.

### P03: reference BSGS and ordinary seeded rho

Status: blocked_by_P02
Allowed paths: `experiments/ecdlp_lab/methods/python/`, `core/`, `fixtures/`,
`tests/`

Deliverables:

- Implement a dependency-light neutral BSGS and a frozen seeded ordinary rho
  specification.
- Carry `derived_from` locators to the existing P1 implementations and compare
  against committed legacy baseline candidates/results without rewriting the
  legacy runner.
- Use a counting wrapper that delegates EC results to the selected curve
  arithmetic and applies the frozen counter vocabulary.
- Verify every returned scalar through the independent EC oracle.
- Report BSGS cold-start table construction separately from reusable-table
  online cost.
- Record rho restarts, cycles, and noninvertible collisions.

Exit criteria:

- known-scalar positive tests pass across the small fixture families;
- wrong target, wrong order, forced cycle, zero denominator, timeout, and
  bounded-memory failures are covered;
- golden differential comparison with legacy BSGS/rho results passes;
- no method receives target-generation secrets.

Kangaroo and endomorphism-quotient rho are not part of this phase:

- kangaroo is an interval-conditioned method and must later declare a public
  scalar interval and the conditioned threat model;
- endomorphism-quotient rho requires a verified beta/lambda, a specified orbit
  canonicalization,
  coefficient transport, and differential tests. A label-only `glv_rho`
  implementation is forbidden.

### P04: safe, resumable campaign runner

Status: blocked_by_P03
Allowed paths: `experiments/ecdlp_lab/orchestration/`, `core/`, `fixtures/`,
`tests/`, `scripts/lab_*.py`

Deliverables:

- Expand campaign configs into unique canonical work units.
- Resolve method IDs only through a committed allowlist. Never execute a raw
  command from JSON and never use `shell=True`.
- Run method, validator, and analysis in separate process boundaries.
- Use create-only receipts, writer locks, atomic writes, process groups,
  timeout tree-kill, bounded parallelism, deterministic resume, and replay.
- The coordinator owns a hash-chained JSONL event log. This is tamper-evident
  replay structure, not a claim that a normal filesystem is physically
  append-only.
- Resolve every file beneath an explicit artifact root; reject path traversal
  and symlink escapes.
- Scrub credential-like environment variables before method execution.
- Fail closed when requested hard memory enforcement is unavailable. On native
  Windows require WSL2 or Docker for enforced resource limits.
- Follow `notes/EXECUTION_SECURITY.md`.

Required fault injections:

- malicious method ID and path traversal;
- inherited secret canary;
- orphan child process after timeout;
- duplicate work identity and concurrent writer;
- torn JSON/JSONL and partial artifact;
- producer crash, validator disagreement, corrupted digest, and resume;
- truncated or tampered event chain, stale-code resume, and a late worker
  result arriving after timeout;
- requested memory limit on an unsupported host.

Exit criteria:

- a tiny local smoke campaign completes from public method inputs;
- interruption and replay create one canonical semantic result per work unit;
- validator shares no decisive method logic;
- the runner has no Engine writer or submission path.

### P05: equal-success comparison and scaling diagnostics

Status: blocked_by_P04
Allowed paths: `experiments/ecdlp_lab/analysis/`, `fixtures/`, `tests/`

Deliverables:

- Make operation counts primary and wall time secondary.
- Compare at fixed success targets, including 0.50 and a separately reported
  0.95 target, over independent algorithm seeds.
- Normalize expected operations and disclose failures, censoring, restarts,
  preprocessing, amortization, workers, and memory.
- Fit multiple simple cost models or retain `model_undecided`; do not force a
  linear exponent model.
- Include the diagnostic model
  `log2(T)=alpha*log2(subgroup_order)+beta*log2(log2(order))+c`, with clustered
  uncertainty by curve and seed, residuals, leave-one-size-out sensitivity, and
  outlier/censoring policy.
- Emit deterministic JSON and concise Markdown.

Exit criteria:

- planted-slope fixtures recover their known diagnostic behavior;
- constant-factor, too-few-size, narrow-range, timeout-censored, and unstable
  fits trigger warnings;
- every engineering smoke output is hard-labelled
  `insufficient_for_asymptotic_inference`, irrespective of its fitted alpha;
- no toy result is extrapolated to 256 bits.

### P06: isolated SageMath/CAS workbench and theta upstream adapter

Status: blocked_by_P05; theta adapter also requires a recorded PR #356 state
Allowed paths: `experiments/ecdlp_lab/methods/sage/`, `env/docker/`,
`replay_fixtures/`, `tests/`; if PR #356 is accepted, only a new wrapper around
its files, not rewriting its historical outputs

Deliverables:

- Use importable Python modules with `from sage.all import ...`, invoked by
  `sage -python`.
- Pin the Sage container by immutable image digest, not only a mutable tag.
- Run the container as a non-root user with networking disabled, a read-only
  root filesystem, no host credentials, and only explicit input/output mounts.
- Separate capability state (`available`, `unavailable`, `error`, `untested`)
  from verification state (`passed`, `failed`, `skipped_missing_capability`).
  A missing backend is never a pass. A `--require-backend sage` gate fails
  closed when Sage was required but unavailable.
- Adapt existing summation-polynomial, efficient-endomorphism, and
  division-polynomial producers and validators through narrow wrappers rather
  than reimplementing formulas.
- Treat Sage as producer. Replay tiny decisive identities through SymPy, PARI,
  or exact stdlib Python where possible.
- Capability-probe FLINT, NTL, and GAP only. Integrate one only when a named
  operation requires it. Magma remains unavailable without a user-supplied
  license and is never a required gate.

PR #356-specific rules:

- If still unmerged, record `upstream_pending` and do not copy its scripts.
- If accepted on `main`, wrap `verify_secp.py` and
  `singular_factorbase.py`; preserve its note and frozen SymPy results.
- The existing `sagemath/sagemath:10.9` launcher is historical and mutable.
  Add a pinned wrapper rather than silently rewriting its provenance.
- Harden new runs with config/source/image digests, separate telemetry, output
  schema, and independent replay.
- Do not call eight sampled field checks a universal proof. Distinguish sampled
  checks, symbolic identities, probabilistic primality settings, and formal
  proof precisely.
- Include the surviving direct/composed/projective Singular comparison only as
  bounded representation diagnostics.

Exit criteria:

- Python-only validation handles absent Sage honestly;
- when Sage is actually available, the bounded replay emits conforming receipts;
- no output is labelled `proved` merely because Sage or Singular produced it;
- no PR #356 conclusion changes canonical route state through this phase.

### P07: p-adic/theta precision conformance and mechanism gate

Status: blocked_by_P06
Allowed paths: `experiments/ecdlp_lab/methods/padic_theta/`,
`replay_fixtures/`, `tests/`

Current mathematical boundary:

- the direct formal-log route is blocked for the prime-to-p secp256k1 subgroup;
- PR #356 reports that the tested Kummer plus efficient-endomorphism action
  collapses to the
  existing cubic mechanism at its stated scope;
- no alternative public p-adic theta observable with recovery and cost bounds
  is currently specified.

Deliverables:

- Define a method-design worksheet, not a `THETA-DECOMP-*` hypothesis.
- The worksheet requires domain/codomain, public computability, exact p-adic
  prime, ring/field, absolute/relative/capped precision model, theta series,
  truncation, convergence condition such as `v_p(q)>0`, precision-loss law,
  reconstruction claim, scalar-separation claim, and bit-complexity cost.
- Implement only tiny arithmetic-conformance fixtures: p-adic values,
  valuations, precision propagation, one explicitly defined truncated theta
  q-series/constant, and exact modular or rational replay.
- Freeze the first demonstrator as the finite Laurent sum
  `Theta_N(z,q)=sum_{m=-N}^{N} q^(m^2) z^(2m)` over a documented small p-adic
  field with unit `z`, `v_p(q)>0`, fixed `N`, and a stated tail/precision bound.
  This is a precision-conformance fixture only, not an ECDLP observable.
- Every operation records input precision, output precision, lost precision,
  valuation assumptions, truncation error bound, and failure reason.
- Add circularity guards against hidden scalars, DLP oracles, target-specific
  precomputation, and unpriced reconstruction.

Decision gate:

- If no source-grounded observable satisfies the worksheet, complete this phase
  with a `no_mechanism_to_implement` record after the arithmetic fixtures.
- Do not invent a decomposition mechanism under infrastructure authority.
- The capability does not reopen `R-ANOMALOUS-PADIC`, establish secp256k1
  applicability, or create an Engine seed.

Exit criteria:

- precision-loss and insufficient-precision tests fail closed;
- tiny fixtures replay exactly outside the Sage producer where claimed;
- all preprocessing and reconstruction work is visible;
- no scalar-linked method is implemented without a future authorized task.

### P08: profile gate and optional Rust backend

Status: blocked_by_P07
Allowed paths: `experiments/ecdlp_lab/methods/native/`, `env/locks/`,
`fixtures/`, `tests/`

Deliverables:

- Profile the reference CPU pipeline on engineering fixtures and identify the
  dominant bounded kernel.
- Commit a quantitative `build_rust`, `defer`, or `no_build` decision.
- A Rust build, if justified, is limited to 8-32-bit toy fields with `u128`
  intermediates, affine/projective arithmetic, the same file/JSON boundary,
  a pinned toolchain, `Cargo.lock`, and `cargo test --locked`.
- Keep the crate dependency-light and make the locked build/test path work
  offline after the declared toolchain and crates are provisioned.
- Differentially verify Rust point/scalar outputs against the independent
  Python oracle.
- Algorithm-level group counters must agree. Coordinate-dependent field
  counters remain backend-labelled.
- State explicitly that the implementation is not production signing code and
  is not side-channel hardened.

CUDA/C++ gate:

- Default outcome in this unauthorized smoke program is deferred.
- GPU code requires a measured dominant parallel kernel, a quantified expected
  benefit, available hardware, and separate owner authorization.
- Missing Rust/CUDA is `deferred_missing_capability`, not evidence that native
  acceleration is useless.

Exit criteria:

- a profile-backed decision exists;
- if Rust is built, unit/property/differential/malformed-input tests pass;
- Python-only independent validation remains canonical and functional.

### P09: content-addressed storage and dry-run remote jobs

Status: blocked_by_P08
Allowed paths: `experiments/ecdlp_lab/remote/`, `env/docker/`, `fixtures/`,
`tests/`, optional `scripts/lab_*.py`

Deliverables:

- Implement a local content-addressed store first.
- Keep artifact identity `{sha256,size,media_type,role}` independent of an
  optional location URI.
- Build a provider-neutral signed job bundle containing only reviewed committed
  code, public inputs, budgets, and output contract.
- Add deterministic dry-run templates for a secret-free lab worker.
- Separate producer/validator processes from uploader credentials.
- Enforce budget, region, instance allowlist, timeout, artifact-size ceiling,
  and automatic shutdown in every remote plan.
- Add provider-specific templates only: Alibaba OSS is not silently generic S3;
  Huawei OBS uses an S3-compatible endpoint only when explicitly configured.
- Slurm is a template after a real multi-node need. Do not add Ray without a
  demonstrated scheduler gap.

Security boundary:

- No test creates a paid resource, uploads data, or requires credentials.
- Do not repurpose the warm Lean server for arbitrary lab methods. The current
  bridge carries SSH/Git/model secrets, the documented box is tight for Sage,
  and arbitrary candidate execution is outside its trust boundary.
- Enabling Huawei, Alibaba, or another provider is a later credentialed action
  requiring an account, credits/budget, and explicit confirmation.

Exit criteria:

- local put/get and deterministic dry-run plans pass;
- corruption, missing object, path escape, interrupted transfer, budget
  overflow, and oversized artifact fail safely;
- no secret enters producer or validator environments.

### P10: end-to-end readiness and adversarial audit

Status: blocked_by_P09
Allowed paths: lab implementation, lab documentation, `experiments/README.md`,
task progress, required generated bundle artifacts

Deliverables:

- Provide one offline validation command and one tiny local end-to-end smoke
  command.
- Document exact setup for macOS, WSL2/Ubuntu, Linux CPU, optional NVIDIA,
  Sage container, and missing-capability behavior.
- Audit hidden precomputation, target leakage, shared decisive validator logic,
  secret inheritance, path escape, backend skipping, environment drift,
  non-deterministic hashing, false asymptotic inference, and scientific-state
  mutation.
- Produce a phase table with merged PR/commit, tests, capabilities, limits, and
  future authorization-dependent work.

Exit criteria:

- fresh-clone Python-only offline validation passes;
- each actually available optional backend passes its real tests or reports an
  exact failure, never a synthetic success;
- deterministic semantic summaries reproduce byte-for-byte; observational
  telemetry may differ and is excluded from the semantic digest;
- the tiny smoke campaign stays within 60 seconds and 512 MiB on the CI host;
- all existing repository gates pass;
- an explicit diff guard confirms the immutable denylist was untouched;
- no Engine outcome, route state, hypothesis registry, verified ledger, or
  formal theorem changed.

## 10. Stable verification interface

The completed lab must expose commands equivalent to:

```bash
python3 -m unittest discover -s experiments/ecdlp_lab/tests -p 'test_*.py'
python3 -m experiments.ecdlp_lab.core.capabilities --json
python3 -m experiments.ecdlp_lab.core.validate --offline
python3 -m experiments.ecdlp_lab.orchestration.run_smoke \
  --config experiments/ecdlp_lab/fixtures/smoke.json \
  --output /tmp/ecdlp-lab-smoke
python3 experiments/framework/test_framework.py
python3 scripts/check_counts.py
python3 scripts/check_semantic_drift.py
python3 scripts/check_targets.py
python3 scripts/check_domains.py
python3 scripts/gen_result_registry.py --check
python3 scripts/gen_source_registry.py --check
python3 scripts/check_repo_artifacts.py
python3 scripts/check_automation_inventory.py
python3 scripts/export_agent_bundle.py --check
python3 scripts/check_status_consistency.py
python3 scripts/check_scientific_semantics.py
python3 scripts/check_generated_fixpoint.py --check
```

When the capability is actually available:

```bash
sage -python -m unittest discover \
  -s experiments/ecdlp_lab/methods/sage/tests -p 'test_*.py'
cargo test --locked \
  --manifest-path experiments/ecdlp_lab/methods/native/Cargo.toml
docker compose \
  -f experiments/ecdlp_lab/env/docker/compose.yml config
```

The final diff guard must compare against the phase base commit and reject any
change under the immutable denylist.

## 11. Sequential execution protocol for Codex

The full program is predefined, so Codex does not need repeated design
approval. Repository autonomy still requires one scoped unit per cycle and a
green reviewed PR before the next dependent phase.

For each phase:

1. Fetch and inspect current `main`, open PRs, and the dirty worktree.
2. Preserve all unfamiliar changes.
3. Health-gate current `main` and distinguish inherited failures from new ones.
4. Create one fresh phase branch from current `main`.
5. Implement only the first unblocked phase and its tests.
6. Run narrow gates, then the required repository gates.
7. Update this file's phase status and evidence.
8. Commit, push, open a scoped PR, and merge only after required CI is green.
9. Start the next phase from newly merged `main` and continue automatically.

Do not put all phases on one long-lived branch. Each phase must be independently
revertible. Optional-capability absence is recorded as
`implemented_unverified` or `deferred_missing_capability`, never `pass`.

Stop and ask the owner only for:

- paid remote resource creation or a credentialed upload;
- a new scientific candidate, experiment, or route decision;
- a trust-policy or public-claim change;
- merging/rewriting PR #356 without its required replay and owner disposition;
- a Lean/Mathlib pin change;
- destructive cleanup or conflict with unknown user work.

## 12. Out of scope

- recovering a real or synthetic 256-bit secp256k1 discrete logarithm;
- wallet, blockchain target, nonce-leak, or third-party key ingestion;
- registering a free-form theta hypothesis from the lab;
- writing Research Engine events or changing route dispositions;
- claiming below-generic-square-root scaling from engineering fixtures;
- building a broad isogeny, pairing, lattice, or quantum platform without a
  named mechanism dependency;
- mandatory CUDA, Ray, Slurm, Magma, or paid cloud work;
- treating Sage/Singular output as a Lean proof;
- moving lab output directly into `Ecdlp/Proved/`.
