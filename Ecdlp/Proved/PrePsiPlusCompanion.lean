import Mathlib
import Ecdlp.Proved.NormEDSIsElliptic
import Ecdlp.Proved.DivisionPolynomialDegree
import Ecdlp.Proved.FourDivisionPolynomial
import Ecdlp.Proved.ThreeTorsion

/-!
# The plus-companion relation for pre-normalized elliptic divisibility sequences

The invariant `EDSPort.invarNum / EDSPort.invarDenom` is constant along an
elliptic net.  Comparing it at an arbitrary index `m` and at index `2` gives the
five-term relation

`P(m - 1)^2 P(m + 2) + P(m - 2) P(m + 1)^2`.

For `P = preNormEDS (a^2) c d`, adjoining a square root `b` of `a` turns `P`
into `normEDS b c d` up to the standard parity twist.  The even branch descends
with a factor `a * c`; the odd branch is first multiplied by `b` and descends
with a factor `a^2 * c`.  Both factors cancel in the base integral domain.

The secp256k1 specialization uses the concrete polynomial identity

`preΨ₄ + Ψ₂Sq^2 = 6 * X^2 * Ψ₃`.

This is the missing plus-companion input for the N7 even-x algebra reduction.
-/

open Polynomial

namespace Ecdlp.Curve

/-- The plus-companion identity for `preNormEDS (a^2) c d`.

The proof compares the elliptic-net invariant at `m` and `2`, after adjoining a
square root of `a`.  It depends on the full net relation for `normEDS`, exposed
as `normEDS_net_eq_zero` by `Ecdlp.Proved.NormEDSIsElliptic`. -/
theorem preNormEDS_sq_plus_companion {A : Type*} [CommRing A] [IsDomain A]
    (a c d x : A) (ha : a ≠ 0) (hc : c ≠ 0)
    (hparam : d + a ^ 2 = 6 * x ^ 2 * c) (m : ℤ) :
    preNormEDS (a ^ 2) c d (m - 1) ^ 2 * preNormEDS (a ^ 2) c d (m + 2)
        + preNormEDS (a ^ 2) c d (m - 2) * preNormEDS (a ^ 2) c d (m + 1) ^ 2
      = 6 * x ^ 2 * preNormEDS (a ^ 2) c d m
          * preNormEDS (a ^ 2) c d (m + 1) * preNormEDS (a ^ 2) c d (m - 1)
        - (if Even m then a ^ 2 else 1) * preNormEDS (a ^ 2) c d m ^ 3 := by
  let f : A[X] := X ^ 2 - C a
  let b : AdjoinRoot f := AdjoinRoot.root f
  let ι : A →+* AdjoinRoot f := algebraMap A (AdjoinRoot f)

  have hb2 : b ^ 2 = ι a := by
    show (AdjoinRoot.root f) ^ 2 = algebraMap A (AdjoinRoot f) a
    have h0 : (Polynomial.aeval (AdjoinRoot.root f)) f = 0 := by
      rw [Polynomial.aeval_def, AdjoinRoot.algebraMap_eq]
      exact AdjoinRoot.eval₂_root f
    have h1 : (Polynomial.aeval (AdjoinRoot.root f)) (X ^ 2 - C a) = 0 := h0
    rw [map_sub, map_pow, Polynomial.aeval_X, Polynomial.aeval_C, sub_eq_zero] at h1
    exact h1

  have hb4 : b ^ 4 = ι (a ^ 2) := by
    have h : b ^ 4 = (b ^ 2) ^ 2 := by ring
    rw [h, hb2, ← map_pow]

  have hdeg : f.degree ≠ 0 := by
    have hfe : f = X ^ 2 - C a := rfl
    rw [hfe, Polynomial.degree_X_pow_sub_C (n := 2) (by norm_num) a]
    decide

  have hinj : Function.Injective ι := by
    show Function.Injective (algebraMap A (AdjoinRoot f))
    rw [AdjoinRoot.algebraMap_eq]
    exact AdjoinRoot.of.injective_of_degree_ne_zero (f := f) hdeg

  have hP : ∀ n : ℤ,
      ι (preNormEDS (a ^ 2) c d n) =
        preNormEDS (b ^ 4) (ι c) (ι d) n := by
    intro n
    rw [hb4, map_preNormEDS]

  have hN : ∀ n : ℤ,
      normEDS b (ι c) (ι d) n =
        ι (preNormEDS (a ^ 2) c d n) * (if Even n then b else 1) := by
    intro n
    simp only [normEDS]
    rw [← hP n]

  have hbase : ι d + b ^ 4 = 6 * ι x ^ 2 * ι c := by
    rw [hb4]
    simpa only [map_add, map_mul, map_pow, map_ofNat] using congrArg ι hparam

  have hnum2 :
      ι d * b + b ^ 3 * b ^ 2 = b * (6 * ι x ^ 2 * ι c) := by
    linear_combination b * hbase

  have hinv := EDSPort.invarNum_mul_invarDenom_of_net
    (W := normEDS b (ι c) (ι d))
    (fun p q r s => normEDS_net_eq_zero b (ι c) (ι d) p q r s)
    1 m 2
  simp [EDSPort.invarNum, EDSPort.invarDenom] at hinv
  rw [hnum2] at hinv
  rw [hN (m + 2), hN (m - 1), hN (m + 1), hN (m - 2), hN m] at hinv

  rcases Int.even_or_odd m with hm | hm
  · have hmz : m % 2 = 0 := Int.even_iff.mp hm
    have p2 : Even (m + 2) := Int.even_iff.mpr (by omega)
    have pm2 : Even (m - 2) := Int.even_iff.mpr (by omega)
    have p1 : ¬ Even (m + 1) := by rw [Int.even_iff]; omega
    have pm1 : ¬ Even (m - 1) := by rw [Int.even_iff]; omega
    rw [if_pos p2, if_neg pm1, if_neg p1, if_pos pm2, if_pos hm] at hinv
    simp only [mul_one, one_mul, one_pow] at hinv

    rw [if_pos hm]
    apply mul_left_cancel₀ ha
    apply mul_left_cancel₀ hc
    apply hinj
    simp only [map_add, map_sub, map_mul, map_pow, map_ofNat, map_one]
    rw [← hb2]
    linear_combination hinv

  · have hmz : m % 2 = 1 := Int.odd_iff.mp hm
    have p2 : ¬ Even (m + 2) := by rw [Int.even_iff]; omega
    have pm2 : ¬ Even (m - 2) := by rw [Int.even_iff]; omega
    have pm0 : ¬ Even m := by rw [Int.even_iff]; omega
    have p1 : Even (m + 1) := Int.even_iff.mpr (by omega)
    have pm1 : Even (m - 1) := Int.even_iff.mpr (by omega)
    rw [if_neg p2, if_pos pm1, if_pos p1, if_neg pm2, if_neg pm0] at hinv
    simp only [mul_one, one_mul, one_pow] at hinv

    rw [if_neg pm0]
    apply mul_left_cancel₀ (pow_ne_zero 2 ha)
    apply mul_left_cancel₀ hc
    apply hinj
    simp only [map_add, map_sub, map_mul, map_pow, map_ofNat, map_one]
    rw [← hb2]
    linear_combination b * hinv

/-- The secp256k1 parameters satisfy the invariant's specialization equation. -/
private theorem secp256k1_preΨ_plus_companion_parameter :
    secp256k1.preΨ₄ + secp256k1.Ψ₂Sq ^ 2 =
      6 * X ^ 2 * secp256k1.Ψ₃ := by
  rw [secp256k1_preΨ₄, secp256k1_Ψ₂Sq, secp256k1_Ψ₃]
  ring

/-- The plus-companion relation for the secp256k1 pre-division polynomials. -/
theorem secp256k1_preΨ_plus_companion (m : ℤ) :
    secp256k1.preΨ (m - 1) ^ 2 * secp256k1.preΨ (m + 2)
        + secp256k1.preΨ (m - 2) * secp256k1.preΨ (m + 1) ^ 2
      = 6 * X ^ 2 * secp256k1.preΨ m * secp256k1.preΨ (m + 1)
          * secp256k1.preΨ (m - 1)
        - (if Even m then secp256k1.Ψ₂Sq ^ 2 else 1) *
            secp256k1.preΨ m ^ 3 := by
  have key := preNormEDS_sq_plus_companion
    secp256k1.Ψ₂Sq secp256k1.Ψ₃ secp256k1.preΨ₄ X
    secp256k1_Ψ₂Sq_ne_zero secp256k1_Ψ₃_ne_zero
    secp256k1_preΨ_plus_companion_parameter m
  simpa only [WeierstrassCurve.preΨ] using key

end Ecdlp.Curve
