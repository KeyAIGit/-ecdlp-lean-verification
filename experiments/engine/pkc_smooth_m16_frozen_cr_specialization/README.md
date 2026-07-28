# TASK-020 frozen recursive specialization kernel certificate

This directory is a narrow, deterministic, non-run certificate for the
actual frozen recursive family introduced in
`Ecdlp.Proved.FrozenRecursiveProjectiveSemaev`.

It binds the following kernel-checked facts:

- `frozenC R s` is the form named `C_(s+2)`, with `frozenC R 14 = C16`;
- the base form is the literal homogeneous triquadratic `H`, including the
  final three coefficients `-28`;
- every successor is the fixed left-fold resultant at formal degrees
  `(2^(s+1), 2)`;
- specialization after an explicit coefficient map is the literal TASK-018
  Sylvester determinant with coefficient unit exactly `+1`;
- affine output `[y:1]` and infinity output `[1:0]` are both retained;
- every specialized predecessor slice has degree at most `2^(s+1)`;
- over an algebraically closed target field, one frozen successor vanishes
  exactly when its two fixed-degree operands have a common valid projective
  root.

The projective root predicate excludes only `[0:0]`. Degree drops, zero
leading coefficients, affine roots, and the root `[1:0]` remain in scope.
Formal degrees are never replaced by actual degrees. No primitive-part,
content, monic, sign, or variable-dependent normalization is performed.

## Independent replay

`validate.py` uses only the Python standard library. It does not import Lean,
the producer, or repository mathematical helpers. It:

1. checks exact SHA-256 bindings to TASK-018, TASK-019, and the two Lean
   source modules;
2. checks that every named declaration occurs in the digest-bound source and
   that the new module contains no `sorry`, `admit`, `axiom`, or `unsafe`;
3. reconstructs every stage from `C2` through `C16`;
4. recomputes every successor's formal degrees, Sylvester size, row-degree
   sum, and output-degree bound;
5. independently evaluates the nine literal terms of `H`;
6. constructs fixed `(2,2)` Sylvester matrices over the integers, maps them
   to F5, computes determinants, and enumerates all of `P1(F5)`;
7. checks separate affine-root and infinity-root fixtures;
8. checks a nonzero control whose result changes if the `-28` block is
   removed.

The fixtures illustrate the mechanism and convention. The universal claims
come from the digest-bound Lean theorems, not from finite testing.

## Exact remaining blocker

The recursive specialization barrier is closed one step at a time, including
the universal output-degree bound and the unconditional common-root
interface. The remaining exact blocker is the universal reverse induction
from `C16` down to `C2`: recovered common projective roots must be bound back
to predecessor frozen-form specializations and assembled into the full
fourteen-node internal projective tree.

This certificate does not claim a direct `RecS17 iff GeoCat` theorem, expand
or evaluate `C16` or `S17`, materialize the M16 system, run a solver, estimate
rank, yield, memory, or cost, authorize an experiment, or promote a route.

## Verification

Run the independent validator and all rehashed semantic fault injections:

```text
python3 experiments/engine/pkc_smooth_m16_frozen_cr_specialization/validate.py
python3 experiments/engine/pkc_smooth_m16_frozen_cr_specialization/test_validate.py
```

Run the Lean gate separately:

```text
lake build Ecdlp.Proved.FrozenRecursiveProjectiveSemaev
```

The Python validator intentionally does not invoke Lean. The external axiom
audit for every public theorem may contain only `propext`,
`Classical.choice`, and `Quot.sound`, and must never contain `sorryAx`.
