import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.Secp256k1PrimeP

/-!
# Separability of the 2-torsion cubic `X³ + C 7`, and its exact closure root count

The `n = 2` analogue of `DivisionPolynomialSeparable.lean`. The affine 2-torsion of
`secp256k1 : Y² = X³ + 7` is `{(x, 0) : x³ + 7 = 0}` (a 2-torsion point is fixed by
negation, i.e. `y = -y`, i.e. `y = 0` in characteristic `≠ 2`; on the curve this forces
`x³ + 7 = 0`). So the 2-torsion `x`-locus is the root set of the **cubic** `X³ + 7`, not of
an odd division polynomial — no multiplication formula is needed here. (Equivalently
`Ψ₂Sq = 4(X³ + 7)`, `DivisionPolynomial.lean`, has the same root set since `4 ≠ 0`.)

The content of this file, mirroring the odd-`n` separability harvest:

* **`secp256k1_cubic_separable`** — `X³ + 7` is separable over `𝔽_p`. `Polynomial.Separable`
  is *defined* as `IsCoprime f (derivative f)`, so a Bézout certificate `u·(X³+7) + v·(3X²) = 1`
  *is* the separability proof. The certificate is trivial: `3·(X³+7) − X·(3X²) = 21`, so with
  `u = 7⁻¹ = C u₀` and `v = −21⁻¹·X = C v₀ · X` one has `u·(X³+7) + v·(3X²) = 1`. The two
  residue facts `7·u₀ = 1` and `u₀ + 3·v₀ = 0` in `ZMod p` (cofactors from
  `scripts` extended-Euclid over `𝔽_p`, printing `CERT_OK`) are discharged by `native_decide`,
  exactly the `CoprimePsi2Psi3.lean` Bézout-cert style.
* **`secp256k1_cubic_roots_card_bar` / `secp256k1_cubic_roots_nodup_bar`** — over `𝔽̄_p` the
  mapped cubic splits (`IsAlgClosed.splits`) with `natDegree = 3` roots, all distinct
  (`nodup_roots` from separability): **exactly `3` distinct roots**. This is the 2-torsion
  `x`-locus at full size, the counting input to `#E[2](𝔽̄_p) = 4` (`TwoTorsionStructure.lean`).

Separability holds because `p ∤ 21`: the derivative `3X²` is nonzero (needs `char ≠ 3`) and
vanishes only at `x = 0`, where `x³ + 7 = 7 ≠ 0` (needs `char ≠ 7`); the secp256k1 prime is
coprime to `21`, so the cubic is separable. No new axioms beyond the compiler trust of
`native_decide` (the same dependency the division-polynomial coprimality layer already carries).
-/

namespace Ecdlp.Curve

open Polynomial

/-- The base-change hom `𝔽_p →+* 𝔽̄_p` (same map `secp256k1Bar` is built from). -/
private noncomputable abbrev φac :
    ZMod Secp256k1.p →+* AlgebraicClosure (ZMod Secp256k1.p) :=
  algebraMap (ZMod Secp256k1.p) (AlgebraicClosure (ZMod Secp256k1.p))

/-- Bézout cofactor constants (extended-Euclid over `𝔽_p`): `u₀ = 7⁻¹`, `v₀ = −21⁻¹`, so
`(C u₀)·(X³+7) + (C v₀ · X)·(3X²) = 1`. Verified (`7·u₀ = 1`, `u₀ + 3·v₀ = 0`) by the
`scripts` cert (`CERT_OK`). -/
private def u₀ : ZMod Secp256k1.p :=
  99250362203413881791632272864589635302802843999120483462392214863921858289997
private def v₀ : ZMod Secp256k1.p :=
  5513909011300771210646237381366090850155713555506693525688456381328992127222

/-- `derivative (X³ + 7) = C 3 · X²` — the derivative of the concrete 2-torsion cubic. -/
private lemma secp256k1_cubic_derivative :
    derivative (X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]) = C 3 * X ^ 2 := by
  simp only [derivative_add, derivative_C, add_zero, derivative_X_pow, Nat.cast_ofNat,
    Nat.reduceSub]

/-- **`X³ + 7` is coprime to its derivative** — the Bézout certificate, which is *by
definition* separability (`Polynomial.Separable f := IsCoprime f (derivative f)`). -/
theorem secp256k1_cubic_isCoprime_derivative :
    IsCoprime (X ^ 3 + C 7 : (ZMod Secp256k1.p)[X])
      (derivative (X ^ 3 + C 7 : (ZMod Secp256k1.p)[X])) := by
  refine ⟨C u₀, C v₀ * X, ?_⟩
  rw [secp256k1_cubic_derivative]
  have e1 : (7 * u₀ : ZMod Secp256k1.p) = 1 := by native_decide
  have e0 : (u₀ + 3 * v₀ : ZMod Secp256k1.p) = 0 := by native_decide
  have key : C u₀ * (X ^ 3 + C 7) + C v₀ * X * (C 3 * X ^ 2)
      = C (u₀ + 3 * v₀) * X ^ 3 + C (7 * u₀) := by
    simp only [map_add, map_mul, map_ofNat]; ring
  rw [key, e0, e1]
  simp

/-- **`X³ + 7` is separable over `𝔽_p`** (the `n = 2` analogue of
`secp256k1_Ψ₃_separable`). Definitional reuse of the Bézout certificate. -/
theorem secp256k1_cubic_separable :
    (X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).Separable :=
  secp256k1_cubic_isCoprime_derivative

/-- **`X³ + 7` has degree `3`.** The `X³` term dominates the constant `C 7` (the
`natDegree_add_eq_left_of_natDegree_lt` pattern of `secp256k1_Ψ₂Sq_natDegree`). -/
theorem secp256k1_cubic_natDegree :
    (X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).natDegree = 3 := by
  rw [natDegree_add_eq_left_of_natDegree_lt]
  · exact natDegree_X_pow 3
  · rw [natDegree_X_pow, natDegree_C]; norm_num

/-- **`X³ + 7` has exactly `3` roots over `𝔽̄_p`** (with multiplicity — and they are
distinct, `secp256k1_cubic_roots_nodup_bar`): the 2-torsion `x`-locus at full size. A
separable polynomial of known degree over `𝔽_p` splits with `natDegree`-many roots over the
algebraic closure (`IsAlgClosed.splits`, `splits_iff_card_roots`). -/
theorem secp256k1_cubic_roots_card_bar :
    ((X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φac).roots.card = 3 := by
  have hsplit : ((X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φac).roots.card
      = ((X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φac).natDegree :=
    (Polynomial.splits_iff_card_roots).mp (IsAlgClosed.splits _)
  rw [hsplit, Polynomial.natDegree_map_eq_of_injective (RingHom.injective φac),
    secp256k1_cubic_natDegree]

/-- The closure roots of `X³ + 7` are pairwise distinct (separability survives base change,
`nodup_roots`). -/
theorem secp256k1_cubic_roots_nodup_bar :
    ((X ^ 3 + C 7 : (ZMod Secp256k1.p)[X]).map φac).roots.Nodup :=
  Polynomial.nodup_roots (secp256k1_cubic_separable.map)

end Ecdlp.Curve
