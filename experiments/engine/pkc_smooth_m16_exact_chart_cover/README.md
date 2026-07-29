# TASK-023 exact chart-polynomial cover certificate

This directory is a source-bound non-run certificate for the exact
chart-polynomial cover proved in:

```text
Ecdlp/Proved/FrozenProjectiveChartSystem.lean
```

The certificate binds the exact source SHA-256:

```text
4f7b95453d8fafba3ec9cae0a9bbad5d8f782c6c0202f6e7cf37e17981b63019
```

It does not run a polynomial solver, enumerate the production cover, search
for a key, estimate rank or yield, or authorize an experiment.

## Fixed-mask system

For an infinity mask:

```text
I : Finset (Fin 14)
```

slot `i` uses exactly one of two canonical representatives:

```text
i in I      -> [1:0]
i notin I   -> [X_i:1]
```

The scalar variable index for a fixed mask is:

```text
{i : Fin 14 // i notin I}
```

The Lean theorem `card_chartVar` proves that the number of variables is:

```text
14 - I.card
```

There are no guard variables and no guard equations. Every fixed mask has
exactly fifteen literal `H` equations. The source proves:

- one base equation, total degree at most 2;
- thirteen step equations, total degree at most 4;
- one final equation, total degree at most 2;
- every equation, uniformly, total degree at most 4.

These are degree ceilings. Infinity substitutions and coefficient
cancellation can lower the degree of a specialized equation.

The literal polynomial semantics is:

```text
forall e : ChartEquation,
  MvPolynomial.eval x (chartPolynomialEquation q y I e) = 0
```

The finite cover existentially quantifies both the mask and its assignment:

```text
exists (I : InfinityMask) (x : ChartVar I -> K),
  FrozenChartPolynomialSystem q y I x
```

## Kernel-bound results

The digest-bound source provides these named results:

- `card_chartEquation`;
- `card_chartVar`;
- `chartPolynomialEquation_base_totalDegree_le_two`;
- `chartPolynomialEquation_step_totalDegree_le_four`;
- `chartPolynomialEquation_final_totalDegree_le_two`;
- `chartPolynomialEquation_totalDegree_le_four`;
- `frozenProjectiveChain_iff_chartPolynomialCover`;
- `frozenGuardedProjectiveSystem_iff_chartPolynomialCover`;
- `frozenRecS17_iff_chartPolynomialCover_over`.

The first cardinality theorem uses `native_decide` and therefore discloses
compiler trust. The other listed theorems are kernel-checked with the standard
Lean assumptions already allowed by the project. The validator rejects
`sorry`, `admit`, custom `axiom`, and `unsafe` tokens in the exact bound
source.

The cover is exactly equivalent to the stage-14 projective witness chain and
to the previous guarded polynomial system. After an injective coefficient
map into an algebraically closed target field, it is also equivalent to the
source frozen `RecS17` statement. No descent of target witnesses to the source
field is claimed.

## Why 16384 masks are not materialized

The logical cover has `2^14 = 16384` possible masks. The theorem quantifies
over `I` directly. Neither the proof contract nor the certificate requires a
list of 16384 systems.

The validator checks only the cardinality identity `14 - I.card` for mask
cardinalities from 0 through 14. It never constructs the production powerset.

## Independent F5 fixture

The deterministic fixture enumerates all 24 nonzero pairs over the field with
five elements and normalizes them to the six points of `P^1(F5)`:

- five affine points `[x:1]`;
- the infinity point `[1:0]`;
- four nonzero scalar representatives per projective point;
- `[0:0]` rejected.

It then exhausts a reduced three-slot product with `6^3 = 216` chains. All
eight reduced masks occur. For every fixed mask the number of chains is:

```text
5^(3 - |I|)
```

Aggregated by mask cardinality:

```text
|I| = 0: 125
|I| = 1:  75
|I| = 2:  15
|I| = 3:   1
```

This fixture checks the representative partition, chart encode/decode
bijection, infinity retention, reduced product-cover combinatorics, and the
variable-count rule. The validator separately carries the nine literal
coordinate-exponent patterns of `HValue` and independently derives the
family degree ceilings `2/4/2`.

## Fault injections

`test_validate.py` applies exactly 60 semantic mutations, all of which must
be rejected. They cover:

- source and upstream SHA bindings;
- mask type, membership meaning, and representatives;
- variable counts and endpoint cases;
- the `1 + 13 + 1 = 15` equation inventory;
- all degree ceilings and the literal `H` fixture;
- equivalence direction and infinity retention;
- F5 projective classes, chains, masks, and distributions;
- forbidden production-mask materialization;
- theorem names, proof statuses, and compiler-trust disclosure;
- solver, rank, authorization, route, and boundary claims.

## Verification

From the repository root:

```text
python3 experiments/engine/pkc_smooth_m16_exact_chart_cover/validate.py \
  --require-final-source-binding
python3 experiments/engine/pkc_smooth_m16_exact_chart_cover/test_validate.py
sha256sum -c \
  experiments/engine/pkc_smooth_m16_exact_chart_cover/artifact.sha256
```

The validator checks the artifact sidecar, both TASK-022 dependencies, the
exact TASK-023 source SHA, all named declarations, the literal source shape,
the F5 fixture, and the degree fixture.

## Exact nonclaims

This certificate makes no claim about:

- enumeration or materialization of all 16384 production masks;
- base-field descent;
- relation independence, yield, or rank;
- solving degree, fill-in, memory, runtime, recovery, or complete cost;
- solver, parameter sweep, exact-target, or discrete-log execution;
- experiment authorization, retention, promotion, or rejection.

The representation barrier is closed. The cost cell remains open and
non-executable.
