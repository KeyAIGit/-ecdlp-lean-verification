import Mathlib
import Ecdlp.Proved.NormEDSSomos4
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.DivisionPolynomialDegree

/-!
# The preΨ Somos-4 relation for secp256k1

Mathlib defines `WeierstrassCurve.preΨ n = preNormEDS (W.Ψ₂Sq ^ 2) W.Ψ₃ W.preΨ₄ n`.
This file derives the Somos-4 recurrence for `secp256k1.preΨ` from the landed
`Ecdlp.NormEDS.normEDS_somos4` (the `normEDS`-level Somos-4 over any `CommRing`).

The bridge is a square-root descent: over `S := AdjoinRoot (X² - C a)` (with
`a = Ψ₂Sq`) the root `b` satisfies `b² = a`, hence `b⁴ = a²`, so
`normEDS b c d n = preNormEDS (b⁴) c d n · (Even n ? b : 1) = ι(preΨ n) · (Even n ? b : 1)`.
Substituting this into `normEDS_somos4 b …` and pulling the result back through the
injective structure map `ι = algebraMap A S` (injective because `X² - C a` has degree
`2 ≠ 0` over the integral domain `A`) yields the `preNormEDS`-level identity, with the
even branch clearing a common `b²` factor (`a ≠ 0`, `A` a domain).

Everything is unconditional for secp256k1: the base ring `A = (ZMod p)[X]` is an
integral domain via the global `Fact (Nat.Prime Secp256k1.p)` instance
(`Ecdlp.Proved.Secp256k1PrimeP`), and `secp256k1_Ψ₂Sq_ne_zero` supplies `a ≠ 0`.
Fully kernel-checked; no proof holes; no new axioms.

This is the companion Somos-4 brick for the N7 even-doubling development (`even_x_algebra`):
the machine-checked (sympy/Gröbner) analysis shows the even-x doubling identities close by a
`normEDSRec'` induction whose steps consume exactly this relation. (It also corrects the repo's
registered `preps_somos4` prover target, whose odd coefficient was mis-stated as `Ψ₂Sq^4`; the
true value is `Ψ₂Sq^2`, since Mathlib's `normEDS` uses `preNormEDS (b^4)`.)
-/

open Polynomial

namespace Ecdlp.Curve

/-- **Somos-4 for `preNormEDS (a²) c d`** over any integral domain, with `a ≠ 0`.

This is the twist-removed (`preNormEDS`) form of `Ecdlp.NormEDS.normEDS_somos4`,
obtained by adjoining a square root `b` of `a` in `AdjoinRoot (X² - C a)` (so `b² = a`,
`b⁴ = a²`), rewriting `normEDS b c d n = preNormEDS (b⁴) c d n · (if Even n then b else 1)`
into the master Somos-4, and descending through the injective `algebraMap`. -/
theorem preNormEDS_sq_somos4 {A : Type*} [CommRing A] [IsDomain A]
    (a c d : A) (ha : a ≠ 0) (m : ℤ) :
    preNormEDS (a ^ 2) c d (m + 2) * preNormEDS (a ^ 2) c d (m - 2)
      = (if Even m then 1 else a ^ 2) * preNormEDS (a ^ 2) c d (m + 1)
          * preNormEDS (a ^ 2) c d (m - 1)
        - c * preNormEDS (a ^ 2) c d m ^ 2 := by
  -- Adjoin a square root `b` of `a`.
  let f : A[X] := X ^ 2 - C a
  let b : AdjoinRoot f := AdjoinRoot.root f
  let ι : A →+* AdjoinRoot f := algebraMap A (AdjoinRoot f)
  -- `b² = a` in the extension.
  have hb2 : b ^ 2 = ι a := by
    show (AdjoinRoot.root f) ^ 2 = algebraMap A (AdjoinRoot f) a
    have h0 : (Polynomial.aeval (AdjoinRoot.root f)) f = 0 := by
      rw [Polynomial.aeval_def, AdjoinRoot.algebraMap_eq]
      exact AdjoinRoot.eval₂_root f
    have h1 : (Polynomial.aeval (AdjoinRoot.root f)) (X ^ 2 - C a) = 0 := h0
    rw [map_sub, map_pow, Polynomial.aeval_X, Polynomial.aeval_C, sub_eq_zero] at h1
    exact h1
  -- `b⁴ = a²`.
  have hb4 : b ^ 4 = ι (a ^ 2) := by
    have h : b ^ 4 = (b ^ 2) ^ 2 := by ring
    rw [h, hb2, ← map_pow]
  -- The structure map is injective: `X² - C a` has degree `2 ≠ 0` over the domain `A`.
  have hdeg : f.degree ≠ 0 := by
    have hfe : f = X ^ 2 - C a := rfl
    rw [hfe, Polynomial.degree_X_pow_sub_C (n := 2) (by norm_num) a]
    decide
  have hinj : Function.Injective ι := by
    show Function.Injective (algebraMap A (AdjoinRoot f))
    rw [AdjoinRoot.algebraMap_eq]
    exact AdjoinRoot.of.injective_of_degree_ne_zero (f := f) hdeg
  -- `preNormEDS (a²) c d` pulls back through `ι` (using `b⁴ = a²`).
  have hP : ∀ n : ℤ, ι (preNormEDS (a ^ 2) c d n) = preNormEDS (b ^ 4) (ι c) (ι d) n := by
    intro n
    rw [hb4, map_preNormEDS]
  -- `normEDS b (ιc) (ιd) n = ι(preNormEDS (a²) c d n) · (if Even n then b else 1)`.
  have hN : ∀ n : ℤ, normEDS b (ι c) (ι d) n
      = ι (preNormEDS (a ^ 2) c d n) * (if Even n then b else 1) := by
    intro n
    simp only [normEDS]
    rw [← hP n]
  -- The master Somos-4 over the extension `S`, with each `normEDS` term expanded.
  have somos := Ecdlp.NormEDS.normEDS_somos4 b (ι c) (ι d) m
  rw [hN (m + 2), hN (m - 2), hN (m + 1), hN (m - 1), hN m] at somos
  rcases Int.even_or_odd m with hm | hm
  · -- m even: m±2, m even; m±1 odd. Coefficient collapses to `1` after clearing `b²`.
    have hmz : m % 2 = 0 := Int.even_iff.mp hm
    have p2 : Even (m + 2) := Int.even_iff.mpr (by omega)
    have pm2 : Even (m - 2) := Int.even_iff.mpr (by omega)
    have p1 : ¬ Even (m + 1) := by rw [Int.even_iff]; omega
    have pm1 : ¬ Even (m - 1) := by rw [Int.even_iff]; omega
    rw [if_pos p2, if_pos pm2, if_pos hm, if_neg p1, if_neg pm1] at somos
    rw [if_pos hm, one_mul]
    apply mul_left_cancel₀ ha
    apply hinj
    simp only [map_mul, map_sub, map_pow]
    rw [← hb2]
    linear_combination somos
  · -- m odd: m±2, m odd; m±1 even. Coefficient is `a² = b⁴`.
    have hmz : m % 2 = 1 := Int.odd_iff.mp hm
    have p2 : ¬ Even (m + 2) := by rw [Int.even_iff]; omega
    have pm2 : ¬ Even (m - 2) := by rw [Int.even_iff]; omega
    have pm0 : ¬ Even m := by rw [Int.even_iff]; omega
    have p1 : Even (m + 1) := Int.even_iff.mpr (by omega)
    have pm1 : Even (m - 1) := Int.even_iff.mpr (by omega)
    rw [if_neg p2, if_neg pm2, if_neg pm0, if_pos p1, if_pos pm1] at somos
    rw [if_neg pm0]
    apply hinj
    simp only [map_mul, map_sub, map_pow]
    rw [← hb2]
    linear_combination somos

/-- **The preΨ Somos-4 relation for secp256k1.** `secp256k1.preΨ` satisfies the
Somos-4 recurrence, the even/odd branches differing by the coefficient
`if Even m then 1 else Ψ₂Sq²`. Instantiates `preNormEDS_sq_somos4` at
`a = Ψ₂Sq, c = Ψ₃, d = preΨ₄` and folds `preNormEDS (Ψ₂Sq²) Ψ₃ preΨ₄ = preΨ`. -/
theorem secp256k1_preΨ_somos4 (m : ℤ) :
    secp256k1.preΨ (m + 2) * secp256k1.preΨ (m - 2)
      = (if Even m then 1 else secp256k1.Ψ₂Sq ^ 2) * secp256k1.preΨ (m + 1)
          * secp256k1.preΨ (m - 1)
        - secp256k1.Ψ₃ * secp256k1.preΨ m ^ 2 := by
  have key := preNormEDS_sq_somos4 secp256k1.Ψ₂Sq secp256k1.Ψ₃ secp256k1.preΨ₄
    secp256k1_Ψ₂Sq_ne_zero m
  -- `secp256k1.preΨ n` unfolds to `preNormEDS (Ψ₂Sq ^ 2) Ψ₃ preΨ₄ n`; `linear_combination`
  -- absorbs any regrouping of the products (the `ite` coefficient is a shared atom).
  simp only [WeierstrassCurve.preΨ]
  linear_combination key

end Ecdlp.Curve
