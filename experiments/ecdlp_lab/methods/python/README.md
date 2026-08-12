# P03 Python reference methods

This package contains bounded, dependency-light engineering references for
`bsgs_v1` and `ordinary_rho_xmod3_v1`.  They operate only on authenticated toy
fixtures of at most 32 bits.  They are baselines, not a secp256k1 attack and not
a scientific outcome.

## Public boundary

`dispatch.sanitize_method_request(record, resolved_fixture=...)` projects a
validated `method_request_v1` onto a frozen `PublicMethodInput`.  That value has
exactly the method id, algorithm seed, `p,a,b,G,Q,ell` and deterministic
budgets.  Request/work/catalog/fixture/target identifiers and bit metadata are
checked before projection but cannot cross the solver boundary as covert
channels.  Expected scalars, target derivation seeds, private receipts, legacy
source rows and non-null interval/precomputation objects are likewise not
representable.  Support for authenticated artifacts is owned by a later phase.

The caller resolves `resolved_fixture` through the committed catalog registry.
The method package never treats request bytes as catalog authority.  The
decisive candidate check remains separate: core validation uses only
`experiments/framework/ec_oracle.py`, not this package's arithmetic.

## Stable API

- `prepare_bsgs(backend, G, ell, budgets, ...) -> BsgsTable | SolverOutcome`
- `solve_bsgs(table, Q, budgets, ...) -> SolverOutcome`
- `solve_bsgs_cold(backend, G, Q, ell, budgets, ...) -> SolverOutcome`
- `solve_ordinary_rho(backend, G, Q, ell, seed, budgets, ...) -> SolverOutcome`
- `run_method(public_input, ...) -> SolverOutcome`

Direct `prepare_bsgs` to `solve_bsgs` reuse is an in-process trusted-only API.
`run_method` never accepts an externally supplied table.  P04 must require a
digest-authorized construction receipt before any serialized precomputation
artifact can become eligible for reuse.

The optional cancellation callback is cooperative and must return an exact
boolean.  P04 owns OS deadlines and RSS enforcement.

## Frozen accounting

Every completed affine `add` wrapper call is one `group_law_invocation`.
Equal non-infinity operands are a doubling; unequal non-infinity operands are
a nontrivial addition; identity calls are neither.  Negation is separate.
Field counters are null with `field_counter_semantics=not_instrumented`.

BSGS reports table construction plus stride multiplication in `offline_setup`,
failed giant advances in `online_target`, and optional candidate multiplication
in `method_self_check`.  Its `legacy_p1_group_operations` is exactly offline
plus online group calls and excludes self-check.  The table estimate is exactly
`len(table)*64`; it is not measured RSS.

Rho reports all walk arithmetic in `online_target` and candidate multiplication
in `method_self_check`.  `collisions` counts equal-point Floyd events and
`noninvertible_collisions` is their zero/non-coprime-denominator subset.
`restarts` counts transitions to another one of the four frozen attempts, so a
first-attempt success is 0 and four exhausted attempts are 3.  The historical
1024 bytes is an algorithmic estimate.  Replay-only Floyd/invalid-candidate
diagnostics are not serialized as contract counters.

Capacity checks are performed before allocation/backend calls where their cost
is statically known.  Group and step guards are atomic: an over-budget backend
call is never started and only completed operations appear in counters.

## Legacy derivation locators

Both specifications derive from
`experiments/ml_structure_probe/p1_toy_scaling/run_assay.py`, raw SHA-256
`6ab905adf8187729e818a92b047c83ff5f6b12d61fca95cfcd512cc3e24820c0`:

- BSGS: `bsgs_solve` and helper `counted_scalar_mul`.
- ordinary rho: `pollard_rho_solve`.

The package does not import that runner (or its numerical/ML dependencies).
The committed locator has raw SHA-256
`56f21ebfdcf12e11ebeb803d230883fd143852c10572fd3dbe0253e3eddf058a`;
its authoritative canonical semantic projection is
`d5b1295f7e02aa3829aaa680786b9f39896f6dc77df0b8a5cec7828e6b39380d`.
