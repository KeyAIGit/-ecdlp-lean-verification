# TASK-024 infinity-stratum pruning certificate

This directory binds the non-run certificate for:

```text
Ecdlp/Proved/FrozenProjectiveInfinityStrata.lean
```

The source proves exact local identities for the distinguished projective
point `[1:0]`. For affine external inputs, two adjacent recursive slots cannot
both be infinity. Consequently the exact chart cover can be restricted from
all `2^14 = 16384` masks to the 987 separated masks of a fourteen-slot path.

If the two endpoint determinants are nonzero, slots 0 and 13 must also be
affine. The exact restricted cover then contains 377 masks. These endpoint
conditions are assumptions, not unconditional facts about every relation.

An isolated infinity slot also forces each existing affine neighbor to equal
the normalized current input coordinate `q.u / q.v`.

The three cardinality theorems use `native_decide` and disclose compiler trust.
The identities, necessity results, forced-neighbor results, and cover
equivalences are ordinary kernel-checked proofs.

The validator independently:

- derives 987 and 377 through the path-independent-set recurrence;
- checks all four infinity identities over `F5` and `F7`;
- exhausts the affine neighbor-forcing fixture over both fields;
- checks source and upstream SHA bindings;
- rejects semantic mutations and forbidden proof placeholders.

It does not run a polynomial solver, enumerate the production mask family,
estimate rank or relation yield, search for a key, or authorize an experiment.

Run:

```text
python3 experiments/engine/pkc_smooth_m16_infinity_strata/validate.py \
  --require-final-source-binding
python3 experiments/engine/pkc_smooth_m16_infinity_strata/test_validate.py
sha256sum -c \
  experiments/engine/pkc_smooth_m16_infinity_strata/artifact.sha256
```
