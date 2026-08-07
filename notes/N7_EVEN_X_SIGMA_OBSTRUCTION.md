# N7 `even_x_algebra`: the verdict splits, and the residual half gets a proof

**Date:** 2026-08-07. **Supersedes in scope (not in substance):** the single-verdict reading of
`notes/N7_EVEN_X_DOUBLING_ANALYSIS.md` (2026-07-22) §"No finite / local certificate", and the
`BARRIERS.md` entry that scopes `blocker-n7-certificates` as "two doubling identities".

## Summary

`even_x_algebra` (`Ecdlp/Targets/n7_uniform_carrier_induction.lean:357-367`) reduces to two
univariate identities, with `A := Φ(k).eval x`, `B := ΨSq(k).eval x`:

* **(I)** `ΨSq(2k).eval x = 4·B·(A³ + 7·B³)`
* **(II)** `Φ(2k).eval x = A⁴ − 56·A·B³`

The 2026-07-22 record gives both the same verdict — no finite certificate, strong induction
required. **That is right for (II) and wrong for (I).** The two halves separate cleanly:

| | route | verdict |
|---|---|---|
| **(I)** | `ψ_even` at a point + the Carrier `y`-conjunct + `y ≠ 0` | **finite algebra.** No induction. |
| **(II)** | — | **not in the ideal**, and now provably, not merely empirically. |

## (I) is finite algebra

Writing `w_j := (secp256k1.ψ j).evalEval x y`, Mathlib's `WeierstrassCurve.ψ_even`
(`DivisionPolynomial/Basic.lean:430`), whose point-level form is already in this repo as
`ψ_even_evalEval` (`Ecdlp/Proved/DivisionPolynomialPointDoubling.lean:33`), gives
`w_{2k}·(2y) = w_k · N_k` with `N_k := w_{k+2}w_{k-1}² − w_{k-2}w_{k+1}²` the ω numerator.
The Carrier `y`-conjunct at `k` is `Y_k·(4y)·w_k³ = N_k`. Squaring and using `4y² = 4(x³+7)`
turns (I) into

> **CORE-I** `N_k² = 16·y²·(A³ + 7·B³)`

which is finite algebra over `hcurvek`, `hXk·B = A`, and `hden`.

**The missing ingredient was never a lemma.** `hYk` is already in scope at the call site
(`n7_uniform_carrier_induction.lean:477`, obtained from the strong IH) and simply not passed at
`:495`; `even_x_algebra`'s signature takes no `Equation x y`, no `y ≠ 0`, and no `hYk`, because
it was left out of the 2026-07-21 soundness refactor that gave `odd_x_algebra`,
`even_y_algebra` and `odd_y_algebra` the `Carrier` coupling — `addX Xk Xk sk = sk² − 2Xk` is
invariant under `Y_k ↦ −Y_k`, so it was a genuine theorem without it. It still is: (I) and (II)
were checked to hold at an `x` with `x³+7` a non-residue, i.e. off the curve. But *no point
bridge applies to the statement as written*, since `ΨSq_eval_eq_ψ_evalEval_sq`
(`Ecdlp/Proved/DivisionPolynomialPointBridge.lean:40`) needs `Equation x y`. **A signature
refactor is a precondition for any route through the bridges**, and `y ≠ 0` is dischargeable at
the call site (`y = 0` ⇒ `2•P = 0` ⇒ `(2k)•P = 0`, contradicting `hn`).

## (II) is blocked by a parity involution — a proof, not a remainder

Let `σ` negate `w_{k±1}` and `w_{k±2}` and fix `w_k`, `x`, `y` (hence `Y_k ↦ −Y_k`,
`s_k ↦ −s_k`). Verified numerically at `k = 9` over `𝔽_1000003` on `y² = x³ + 7` at
`P = (2, 579196)`:

| relation | residual at the true window | residual after `σ` |
|---|---|---|
| `A = x·w_k² − w_{k+1}w_{k-1}`, `B = w_k²` | — | **unchanged** (`σA = A`, `σB = B`) |
| `ψ_succ_mul_ψ_pred` at `k`: `w_{k+1}w_{k-1} = x·B − A` | 0 | **0** |
| Somos-4 at `k` | fixed value | **same value** (σ-invariant) |
| **CORE-I**: `N_k² = 16y²(A³+7B³)` | 0 | **0** |
| **the residual**: `S(k) = 6x²·w_k w_{k+1} w_{k-1} − (4x³+28)·w_k³` | 0 | **812987 ≠ 0** |

where `S(k) := w_{k+2}w_{k-1}² + w_{k-2}w_{k+1}²` — the **sum**, where the ω numerator `N_k` is
the **difference**. So `σ` preserves every relation the doubling/ω identities put in play and
falsifies the one the goal needs. **CORE-II is therefore not in the ideal those relations
generate, however the certificate is arranged.** This is a non-membership proof; the
2026-07-22 record had a nonzero CAS remainder modulo a bounded Somos window, which is evidence
for the same conclusion but not a proof of it.

The orthogonality is structural, not accidental: `Ecdlp/Proved/OmegaNumeratorUniform.lean`'s
`psi_omega_numerator` pins the difference `N_k`, and `φ_ψ_diff`
(`Ecdlp/Proved/DivisionPolynomialEllSequence.lean:46`) likewise gives only the difference
`Φ(k−1)ΨSq(k+1) − Φ(k+1)ΨSq(k−1) = ψ(2k)ψ(2)`. **The sum is what is missing**, and
`U² − D² = 4·Φ(k+1)Φ(k−1)·P²` leaves the same one-bit ambiguity. The single relation whose
σ-image breaks is `ψ_succ_mul_ψ_pred` at index `k+1`
(`Ecdlp/Proved/DivisionPolynomialPointDiff.lean:61`), and it imports `Φ(k+1)` — a new univariate
unknown that induction at `k` alone does not control.

## Consequences for the registry

1. **Re-scope `blocker-n7-certificates`** from "two doubling identities" to **one `+`-companion
   lemma**: `S(k) = 6x²·w_k w_{k+1} w_{k-1} − Ψ₂Sq(x)·w_k³`, by `normEDSRec'` over the `k±2`
   window in the `Ecdlp/Proved/NormEDSSomos4.lean` idiom. Equivalent forms that also close (II):
   `[Φ(k−1)ΨSq(k+1) + Φ(k+1)ΨSq(k−1)]·ΨSq(k) = 2(A³+7B³) + 2B³(x³+7) − 2P²(A+xB)` with
   `P := xB − A`, or the product form `Φ(k+1)Φ(k−1)·ΨSq(k)²`. Both are *secant* content —
   `x((k±1)P)` symmetric functions from `kP ± P` — structurally `odd_x_algebra`'s business, not
   the tangent doubling `even_x_algebra` names in its `needs`.
2. **Prerequisite, and it is cheap:** refactor `even_x_algebra` to take `hxy`, `hy`, `hYk`
   (the call site already holds all three), and add the imports
   `DivisionPolynomialPointDoubling`, `DivisionPolynomialPointDiff`, `DivisionPolynomialDoubling`,
   `NormEDSSomos4` — none is in the stem's current import list.
3. `even_x_algebra` remains torsion-bridge-independent. This note changes nothing about
   `nsmul_eq_zero_iff_psi_evalEval_zero`, which is a separate wall.

## What this note does not claim

Nothing here closes `even_x_algebra`, and nothing here is kernel-checked — the stem still
carries its `sorry`, and the numerical work above is Python over a 20-bit toy prime, not Lean.
The claim is exactly: the obligation splits into a half that is finite algebra and a half that
provably is not reachable from the relations currently in play, and the second half has an
identified single companion lemma. Landing either half is future work.
