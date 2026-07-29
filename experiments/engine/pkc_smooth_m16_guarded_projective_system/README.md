# TASK-022 guarded projective-system certificate

This is a source-bound non-run certificate for the exact stage-14 scalar
encoding of the frozen projective witness chain. It does not invoke Lean, run
a polynomial solver, search a key, or estimate cryptographic cost.

## Kernel-bound result

For a `Field k`, an injective coefficient map `k ->+* K`, and an
algebraically closed `Field K`, the Lean source binds frozen `RecS17` to a
guarded scalar system over `K`. The same source proves that the guarded
system is equivalent to `FrozenProjectiveChain` at stage 14.

`FrozenGuardedProjectiveSystem` is defined directly as an existential
assignment `GuardVar -> K` on which every polynomial indexed by
`GuardedEquation` evaluates to zero. It is not a parallel recursive predicate
standing in for the literal polynomial family.

Each of the fourteen intermediate projective slots uses four scalar
variables:

```text
(U, V, A, B)
```

The guard is:

```text
A*U + B*V - 1 = 0
```

Such `A,B` exist exactly when `(U,V)` is nonzero. Therefore `[0:0]` is
excluded while the retained infinity representative `[1:0]` remains valid.

The resulting finite presentation has:

- 14 projective witness slots;
- 56 scalar variables;
- 15 `H` equations;
- 14 guard equations;
- 29 equations in total;
- total degree at most 4.

The degree statement is an upper bound. This certificate does not claim that
every equation, or the system as a whole, has exact total degree 4.

The two finite-cardinality theorems use `native_decide` and therefore disclose
compiler trust through `Lean.ofReduceBool`. The two equivalence theorems and
the degree upper-bound theorem use only the standard Lean assumptions listed
in `artifact.json`; no custom axiom or `sorryAx` is accepted.

## Independent finite-field fixture

`validate.py` exhaustively enumerates all `5^4 = 625` assignments
`(U,V,A,B)` over the field with five elements. It independently obtains:

- 120 solutions of the guard equation;
- all 24 nonzero coordinate pairs;
- exactly 5 guard completions per nonzero pair;
- `[1:0]` allowed;
- `[0:0]` rejected.

This is an `F5` finite-field fixture, not the F5 Groebner-basis algorithm.

## Exact boundary

Closed here:

- exact stage-14 guarded representation;
- exact equivalence with the frozen projective chain;
- exact variable and equation counts;
- total-degree ceiling 4;
- exact nonzero-pair guard semantics.

Still open and unpriced:

- base-field descent;
- a chart or gauge treatment that removes projective and guard redundancy;
- independent relation yield and rank;
- solving degree, fill-in, memory, and runtime;
- recovery validation and complete end-to-end cost.

No experiment, solver sweep, direct secp256k1 work, hypothesis retention, or
route promotion is authorized by this certificate.

## Verification

Run the independent certificate and its exactly 26 semantic fault injections:

```text
python3 experiments/engine/pkc_smooth_m16_guarded_projective_system/validate.py
python3 experiments/engine/pkc_smooth_m16_guarded_projective_system/test_validate.py
```

Run the Lean target separately:

```text
lake build Ecdlp.Proved.FrozenProjectiveGuardSystem
```

The validator checks the exact SHA-256 binding to the Lean source and refuses
a pending source digest in the canonical artifact.
