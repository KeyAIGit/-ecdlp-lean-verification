# TASK-019 fixed-degree projective resultant kernel certificate

This is a non-run certificate. It binds the narrow Lean theorems for
fixed-formal-degree binary resultants to the literal TASK-018 Sylvester
convention and independently replays small arithmetic fixtures. It does not
expand or evaluate S17, materialize the M16 system, run a solver, or estimate
cost.

## Kernel-bound result

For positive formal degrees `m,n`, degree bounds
`natDegree f <= m`, `natDegree g <= n`, and an algebraically closed field,
the Mathlib fixed-degree resultant is zero exactly when
`f.homogenize m` and `g.homogenize n` have a common pair `(U,V)` with
`U != 0 or V != 0`.

The theorem deliberately includes zero polynomials and retained leading zero
coefficients. Its two witness branches are:

- `V != 0`: dehomogenize to `x=U/V` and use `[x:1]`;
- `V=0`: both retained leading coefficients vanish and the valid
  representative is `[1:0]`.

The literal TASK matrix has:

- descending `U`-degree coefficients;
- `n` shifted rows of `f`, then `m` shifted rows of `g`;
- descending monomial columns;
- argument order `(f,g,m,n)`;
- ordinary determinant and coefficient unit exactly `1`.

Lean proves that this matrix is the transpose of Mathlib's Sylvester matrix
with both axes reversed by `Fin.revPerm`. Transposition and the same
permutation on both axes preserve the determinant exactly. The end-to-end
corollary therefore states the common-projective-root equivalence directly
for the literal TASK determinant.

## Independent fixtures

`validate.py` uses only the Python standard library. It reconstructs each
matrix, computes its determinant by the Leibniz formula, enumerates
`P1(F5)`, and checks witnesses.

The registered controls include:

- both degree-two forms dropping degree, with the only common root `[1:0]`;
- a one-sided degree drop whose fixed resultant is nonzero;
- zero-left, zero-right, and both-zero forms;
- exact-degree forms with a unique affine common root;
- an odd `(1,1)` control detecting argument order, row order, coefficient
  order, and a changed unit;
- a recurrence-shaped `(4,2)` full-matrix control;
- a parameter specialization whose fixed resultant is
  `9*s^2-12*s` and whose `s=0` fiber retains `[1:0]`.

The parameter fixture demonstrates the mechanism of retained formal degree.
It is not presented as the missing frozen recursive `C_r` specialization
theorem.

## Exact remaining blocker

The generic fixed-degree theorem and literal matrix bridge are kernel-bound.
The following remain `open_exact_blocker`:

1. exact specialization of the frozen recursive `C_r` definition at formal
   degrees `(2^(r-2),2)`, including affine output and `[1:0]`;
2. the downstream generic C16 forward binding;
3. the universal reverse induction from C16 to C2.

Consequently this certificate does not claim `RecS17 iff GeoCat`, a
base-field rational or recovery implication, scheme equality, multiplicity
preservation, relation yield, rank, solving cost, route promotion, or
experiment authorization.

## Verification

Run the independent certificate and all rehashed semantic fault injections:

```text
python3 experiments/engine/pkc_smooth_m16_projective_resultant_kernel/validate.py
python3 experiments/engine/pkc_smooth_m16_projective_resultant_kernel/test_validate.py
```

Run the actual Lean gate separately. The Python validator intentionally does
not invoke Lean:

```text
lake build Ecdlp.Proved.FixedDegreeProjectiveResultant \
  Ecdlp.Proved.TaskSylvesterConvention
```

The source audit must reject `sorry`, `admit`, `axiom`, `unsafe`, and
`sorryAx`. `#print axioms` for every public theorem may contain only the
standard kernel assumptions recorded in `artifact.json`.
