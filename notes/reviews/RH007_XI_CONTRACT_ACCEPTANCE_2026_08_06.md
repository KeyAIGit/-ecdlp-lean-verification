# RH-007 xi-contract acceptance record

Date: 2026-08-06

Reviewed baseline:

- repository `main` at `a29ebfc26d1ab60d8997801321c22f0ca284a7eb`;
- final reviewed `XI_PACKAGE_CONTRACT.md` SHA-256
  `39f3d27b1aca877b4c53f86c5f5048ea87ccecc8afc69b55ab73e91d3fed8677`
  (Git blob `d1e949e5c3ebe9882fda42137c4f1da5350c1386`);
- final reviewed non-built `drafts/RiemannXi.lean` SHA-256
  `70b9389675e946a950065b8fc972b6dc046ac0efd6496246e86d3224005dbc67`
  (Git blob `a60b7a963d9237e4e7d536b2e0ce8a0134ad95db`);
- built target bridge SHA-256
  `5c7463ff055908c3a4fff411959ef10e13b4a3e2b1e7e17a7dc785fe646800bc`
  (Git blob `d149dc351fd961c7dce00191c6418c516b581ce6`);
- pinned Mathlib revision
  `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`.

Decision: **ACCEPT WITH APPLIED EDITORIAL FIXES**.

This decision accepts only the mathematical statement surface of
`XI_PACKAGE_CONTRACT.md`: eleven contract clauses and twelve public
declarations, because X4 contains two endpoint theorems. It does not claim
that the non-built Lean draft elaborates, does not promote a module, does not
close `S1-XI`, and provides no evidence for or against RH.

The applied fixes changed only version/status/gate-boundary prose and comments:
the contract title and obligation-register heading now say v2; closing
`S1-XI` is explicitly conditional on later promotion and kernel verification;
the surface count distinguishes eleven clauses from twelve declarations; the
draft header records the already-closed bridge/source gates and states
explicitly that inline proof bodies are candidate code until the kernel checks
them. No declaration name, binder, hypothesis, conclusion, or proof body
changed.

## Review basis

1. `RH-006` dispositioned all 59 source rows and accepted its two amendments.
2. The pinned theorem `completedRiemannZeta_eq` was re-read directly; its sign
   is `Lambda = Lambda0 - 1/s - 1/(1-s)`.
3. The exact pinned interfaces for `GammaR`, its zero set, zeta
   nonvanishing, the canonical `RiemannHypothesis`, complex
   differentiability, and `analyticOrderAt` were independently rechecked.
4. All twelve X1-X11 declarations match between this contract,
   `TARGET_BRIDGE_CONTRACT.md` Annex A, and the non-built draft.
5. Bridge prerequisite `riemannZeta_zero_mem_critical_strip` is already in
   the kernel-checked module merged through PR #299.
6. The draft contains no `sorry`, `admit`, custom `axiom`, `unsafe`,
   `partial`, or competing RH proposition.

## Statement disposition

| clause | declaration surface | disposition |
|---|---|---|
| X1 | `riemannXi` | ACCEPT. The frozen entire normalization avoids a totalized exceptional product. |
| X2 | `differentiable_riemannXi` | ACCEPT. Global differentiability follows from the pinned entire completion and polynomial closure. |
| X3 | `riemannXi_one_sub` | ACCEPT. Both the polynomial factor and pole-removed completion are invariant under `s -> 1-s`. |
| X4 | `riemannXi_zero`, `riemannXi_one` | ACCEPT. Both endpoint values come directly from the entire formula and equal `1/2`. |
| X5 | `riemannXi_eq_of_ne` | ACCEPT. The sign and both endpoint exclusions are exact. |
| X6 | `riemannXi_eq_zero_iff_riemannZeta_eq_zero` | ACCEPT. The full `GammaR` zero classification is used with exhaustive cases. |
| X7 | `riemannXi_ne_zero_of_one_le_re` | ACCEPT. X4 handles `s = 1`; all other points use X6 and pinned zeta nonvanishing. |
| X8 | `riemannXi_ne_zero_of_re_le_zero` | ACCEPT. Reflection maps the closed left half-plane to the closed right half-plane. |
| X9 | `riemannXi_zero_mem_critical_strip` | ACCEPT. X7 and X8 give strict localization without a hidden trivial-zero hypothesis. |
| X10 | `riemannHypothesis_iff_riemannXi_zeros_re_eq_half` | ACCEPT. The left side is the canonical pinned target and both directions prove the X6 exclusions. |
| X11 | `analyticOrderAt_riemannXi_eq_riemannZeta` | ACCEPT. A local analytic nonvanishing cofactor transports order only on the open strip. |

## Load-bearing checks

### X5 sign and X4 endpoints

For `s != 0` and `s != 1`, the pinned theorem gives

```text
s(s-1) * Lambda(s)
  = s(s-1) * Lambda0(s) - (s-1) - (-s)
  = 1 + s(s-1) * Lambda0(s).
```

The constant is `+1`. Therefore X1 agrees with
`s(s-1) * Lambda(s) / 2` away from the endpoints, while the entire formula
itself gives

```text
riemannXi(0) = 1/2
riemannXi(1) = 1/2.
```

Neither endpoint calculation evaluates a meromorphic product at a totalized
exceptional point.

### X6 gamma-zero split

The pinned theorem states

```text
GammaR(s) = 0  iff  exists n : Nat, s = -(2*n).
```

The natural-number cases are exhaustive:

- `n = 0` gives `s = 0`, excluded by `hs0`;
- `n = m+1` gives `s = -2*(m+1)`, excluded by `htriv`.

The trivial-zero hypothesis does not cover zero, and `hs0` does not replace
the trivial-zero hypothesis. The separate `hs1` exclusion is required by X5.

### X10 canonical target

The forward implication obtains every X6 exclusion from xi-side strip
localization. The reverse implication obtains them from the already-built
bridge P2. The statement uses `_root_.RiemannHypothesis` verbatim and
introduces no alternate target.

### X11 analytic-order transport

On `U = {z | 0 < re(z) and re(z) < 1}`, set

```text
u(z) = z * (z - 1) / 2 * GammaR(z).
```

Every point of `U` avoids `0`, `1`, and the `GammaR` zero set, giving a
neighborhood factorization `riemannXi = u * riemannZeta`. The pinned Gamma
differentiability and constant-base `cpow` results assemble analyticity of
`GammaR` on the right half-plane. Thus `u` is analytic and nonzero at the
base point, so the congruence, product, and unit-order laws give

```text
analyticOrderAt(riemannXi, s) = analyticOrderAt(riemannZeta, s).
```

The factorization is never asserted at `0`, `1`, or on a boundary line. X11
does not construct a divisor and does not close the remaining
`S1-MULTIPLICITY` obligations.

## Static review versus kernel verdict

The draft is intentionally outside every build target and refers to bridge P2
as a sibling dependency. The following remain elaboration risks until the
future built change runs the kernel:

- `id` versus lambda shapes in X2;
- endpoint simplification in X4;
- denominator clearing and a possible orphaned `ring` in X5;
- natural-number cast normalization in X6, X7, and X10;
- assembled `GammaR` differentiability and Pi-function/eta shapes in X11.

None justifies weakening a theorem statement or an exclusion. If the built
implementation requires such a change, promotion must stop and return to
contract review.

The later promotion change must explicitly import the built target bridge,
add the xi module to `ResearchOS.lean`, ledger all twelve declarations,
regenerate the ResearchOS registry and axiom audit, run a narrow compile and
full build, reject incomplete proofs, and pass both axiom audits. Only green
authoritative CI can turn these accepted statements into proved repository
declarations.

## Gate result

The independent contract-acceptance phase of `RH-007` is complete. A separate
promotion change is authorized to attempt kernel verification of exactly this
statement surface.

This acceptance alone does not close `S1-XI`, does not complete
`S1-MULTIPLICITY`, does not select an RH route, and does not change the truth
status of RH.
