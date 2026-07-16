import Mathlib
import Ecdlp.Proved.CoprimeCommonRoot
import Ecdlp.Proved.Secp256k1Curve
import Ecdlp.Proved.Secp256k1PrimeP

/-!
# The evaluation bridge: division polynomials at a point ↔ scalar `normEDS` (nodes L2, L3 of B1)

Toward the counting half of `#E[n] = n²` (node N10(i) of the `ψₙ ↔ E[n]` bridge,
`notes/DIVISION_POLY_TORSION_MAP.md`), this file connects Mathlib's division polynomials
`ΨSq`/`Φ`, **evaluated at a point** `x₀`, to the scalar elliptic divisibility sequence
`normEDS`. The point of the bridge: after it, everything left in the B1 coprimality /
N5 program is a statement about the *scalar* sequence `normEDS β c d`, with no polynomials,
no curve, and no evaluation — the shape of the remaining problem changes.

## The identities

Fix a curve `W` over a commutative ring, a point `x₀`, and `β` with `β² = Ψ₂Sq(x₀)`
(a square root of the 2-division value — over an algebraically closed field one always
exists, so the descent below is unconditional there). Write
`w k := normEDS β (Ψ₃.eval x₀) (preΨ₄.eval x₀) k`. Then

* `eval_preΨ_eq_preNormEDS`  — `(preΨ n).eval x₀ = preNormEDS (β⁴) (Ψ₃ x₀) (preΨ₄ x₀) n`
* `eval_ΨSq_eq_normEDS_sq`   — `(ΨSq n).eval x₀ = w n ^ 2`
* `eval_Φ_eq_normEDS`        — `(Φ n).eval x₀ = x₀ * w n ^ 2 − w (n+1) * w (n−1)`

These are pure consequences of Mathlib's twist conventions for `preΨ`/`ΨSq`/`Φ` and
`normEDS`; the certificate `scripts/certs/eval_bridge_check.py` (prints `CERT_OK`)
records the even/odd twist algebra. No `native_decide`, no pasted constants, no new axioms.

## The descent

Over an integral domain, a common root of `Φ n` and `ΨSq n` forces two *consecutive*
`normEDS` terms to vanish (`normEDS_consecutive_eq_zero_of_eval_eq_zero`). Composed with
the L1 field↔closure bridge (`Ecdlp.DivisionPoly.exists_common_root_of_not_isCoprime`),
`¬ IsCoprime (Φ n) (ΨSq n)` over `k` yields consecutive `normEDS` zeros over `k̄`
(`exists_normEDS_consecutive_eq_zero_of_not_isCoprime`), instantiated for secp256k1 over
`𝔽̄_p`. This turns the coprimality obligation `gcd(Φₙ, ΨSqₙ) = 1` (node N5) into a
statement purely about the scalar EDS.

The `EvalBridge`/`LocalStructure`/`Descent` sections are curve-agnostic (Mathlib + L1
only) — candidates for upstreaming alongside the eventual counting half.
-/

namespace Ecdlp.Curve

open Polynomial

section EvalBridge

variable {K : Type*} [CommRing K] (W : WeierstrassCurve K) {x₀ β : K}

/-- **L2, base.** `preΨ` evaluated at `x₀` is the scalar `preNormEDS` with the 2-division
value pulled back through `β² = Ψ₂Sq(x₀)`. Naturality of `preNormEDS` under the evaluation
ring hom, with Mathlib's `preΨ = preNormEDS (Ψ₂Sq²) Ψ₃ preΨ₄`. -/
theorem eval_preΨ_eq_preNormEDS (hβ : β ^ 2 = W.Ψ₂Sq.eval x₀) (n : ℤ) :
    (W.preΨ n).eval x₀ = preNormEDS (β ^ 4) (W.Ψ₃.eval x₀) (W.preΨ₄.eval x₀) n := by
  have h := map_preNormEDS (Polynomial.evalRingHom x₀) (W.Ψ₂Sq ^ 2) W.Ψ₃ W.preΨ₄ n
  simp only [coe_evalRingHom, map_pow] at h
  have hb : (W.Ψ₂Sq.eval x₀) ^ 2 = β ^ 4 := by rw [← hβ]; ring
  simp only [WeierstrassCurve.preΨ, coe_evalRingHom] at *
  rw [h, hb]

/-- **L2a.** `ΨSq` evaluated at `x₀` is the square of the scalar `normEDS`. -/
theorem eval_ΨSq_eq_normEDS_sq (hβ : β ^ 2 = W.Ψ₂Sq.eval x₀) (n : ℤ) :
    (W.ΨSq n).eval x₀ = normEDS β (W.Ψ₃.eval x₀) (W.preΨ₄.eval x₀) n ^ 2 := by
  rcases Int.even_or_odd n with hn | hn
  · have hodd : ¬ Even n → False := fun h => h hn
    simp only [WeierstrassCurve.ΨSq, normEDS, if_pos hn, eval_mul, eval_pow, mul_one,
      eval_preΨ_eq_preNormEDS W hβ n]
    rw [← hβ]; ring
  · have hne : ¬ Even n := by simpa [Int.not_even_iff_odd] using hn
    simp only [WeierstrassCurve.ΨSq, normEDS, if_neg hne, eval_mul, eval_pow, mul_one,
      eval_preΨ_eq_preNormEDS W hβ n]

/-- **L2b.** `Φ` evaluated at `x₀` is `x₀ · w² − w₊·w₋` for consecutive scalar `normEDS`
values `w₊ = w(n+1)`, `w₋ = w(n−1)`. -/
theorem eval_Φ_eq_normEDS (hβ : β ^ 2 = W.Ψ₂Sq.eval x₀) (n : ℤ) :
    (W.Φ n).eval x₀
      = x₀ * normEDS β (W.Ψ₃.eval x₀) (W.preΨ₄.eval x₀) n ^ 2
        - normEDS β (W.Ψ₃.eval x₀) (W.preΨ₄.eval x₀) (n + 1)
          * normEDS β (W.Ψ₃.eval x₀) (W.preΨ₄.eval x₀) (n - 1) := by
  have hΨ := eval_ΨSq_eq_normEDS_sq W hβ n
  have hp1 := eval_preΨ_eq_preNormEDS W hβ (n + 1)
  have hm1 := eval_preΨ_eq_preNormEDS W hβ (n - 1)
  rcases Int.even_or_odd n with hn | hn
  · -- n even ⇒ n±1 odd, so `normEDS (n±1) = preNormEDS (n±1)` (no β twist)
    have h1 : ¬ Even (n + 1) := by simp [Int.even_add_one, hn]
    have h2 : ¬ Even (n - 1) := by simp [Int.even_sub_one, hn]
    simp only [WeierstrassCurve.Φ, if_pos hn, eval_sub, eval_mul, eval_X, one_mul,
      hΨ, normEDS, if_neg h1, if_neg h2, mul_one, hp1, hm1]
  · -- n odd ⇒ n±1 even, so `normEDS (n±1) = preNormEDS (n±1) * β`
    have hne : ¬ Even n := by simpa [Int.not_even_iff_odd] using hn
    have h1 : Even (n + 1) := by simp [Int.even_add_one, hne]
    have h2 : Even (n - 1) := by simp [Int.even_sub_one, hne]
    simp only [WeierstrassCurve.Φ, if_neg hne, eval_sub, eval_mul, eval_X,
      hΨ, normEDS, if_pos h1, if_pos h2, hp1, hm1]
    rw [← hβ]; ring

end EvalBridge

section LocalStructure

variable {K : Type*} [CommRing K] [IsDomain K] (W : WeierstrassCurve K) {x₀ β : K}

/-- **The descent, local form.** Over an integral domain, if `ΨSq n` and `Φ n` both vanish
at `x₀`, then the scalar EDS has two *consecutive* zeros: `w n = 0` together with
`w (n−1) = 0` or `w (n+1) = 0`. (A vanishing `ΨSq` forces `w n = 0` since `ΨSq = w²`;
then `Φ = x·w² − w₊w₋` collapses to `−w₊w₋`, and a domain has no zero divisors.) -/
theorem normEDS_consecutive_eq_zero_of_eval_eq_zero (hβ : β ^ 2 = W.Ψ₂Sq.eval x₀) {n : ℤ}
    (hΨ : (W.ΨSq n).eval x₀ = 0) (hΦ : (W.Φ n).eval x₀ = 0) :
    normEDS β (W.Ψ₃.eval x₀) (W.preΨ₄.eval x₀) n = 0 ∧
      (normEDS β (W.Ψ₃.eval x₀) (W.preΨ₄.eval x₀) (n - 1) = 0 ∨
        normEDS β (W.Ψ₃.eval x₀) (W.preΨ₄.eval x₀) (n + 1) = 0) := by
  have hwn : normEDS β (W.Ψ₃.eval x₀) (W.preΨ₄.eval x₀) n = 0 := by
    have h := eval_ΨSq_eq_normEDS_sq W hβ n
    rw [hΨ] at h
    exact pow_eq_zero_iff (two_ne_zero).mp h.symm
  refine ⟨hwn, ?_⟩
  have hΦ' := eval_Φ_eq_normEDS W hβ n
  rw [hΦ, hwn] at hΦ'
  have hprod : normEDS β (W.Ψ₃.eval x₀) (W.preΨ₄.eval x₀) (n + 1)
      * normEDS β (W.Ψ₃.eval x₀) (W.preΨ₄.eval x₀) (n - 1) = 0 := by
    linear_combination -hΦ'
  rcases mul_eq_zero.mp hprod with h | h
  · exact Or.inr h
  · exact Or.inl h

end LocalStructure

section Descent

/-- A square root of `Ψ₂Sq(x₀)` always exists over an algebraically closed field. -/
theorem exists_sq_eq_eval_Ψ₂Sq {K : Type*} [Field K] [IsAlgClosed K]
    (W : WeierstrassCurve K) (x₀ : K) : ∃ β : K, β ^ 2 = W.Ψ₂Sq.eval x₀ :=
  IsAlgClosed.exists_pow_nat_eq (W.Ψ₂Sq.eval x₀) (by norm_num)

/-- **The descent, global form (node N5 reduced to scalar EDS).** If `Φ n` and `ΨSq n`
are **not** coprime over a field `k`, then over any algebraically closed extension `K`
the scalar EDS `normEDS` (built from the mapped curve's data at some point `x₀`, with
`β² = Ψ₂Sq(x₀)`) has two consecutive zeros. Composes L1 (`exists_common_root_…`) with
the local descent above. -/
theorem exists_normEDS_consecutive_eq_zero_of_not_isCoprime
    {k K : Type*} [Field k] [Field K] [IsAlgClosed K] (φ : k →+* K)
    (W : WeierstrassCurve k) (n : ℤ) (h : ¬ IsCoprime (W.Φ n) (W.ΨSq n)) :
    ∃ (x₀ β : K), β ^ 2 = (W.map φ).Ψ₂Sq.eval x₀ ∧
      normEDS β ((W.map φ).Ψ₃.eval x₀) ((W.map φ).preΨ₄.eval x₀) n = 0 ∧
        (normEDS β ((W.map φ).Ψ₃.eval x₀) ((W.map φ).preΨ₄.eval x₀) (n - 1) = 0 ∨
          normEDS β ((W.map φ).Ψ₃.eval x₀) ((W.map φ).preΨ₄.eval x₀) (n + 1) = 0) := by
  obtain ⟨x₀, hΦ0, hΨ0⟩ :=
    Ecdlp.DivisionPoly.exists_common_root_of_not_isCoprime φ φ.injective h
  rw [← WeierstrassCurve.map_Φ] at hΦ0
  rw [← WeierstrassCurve.map_ΨSq] at hΨ0
  obtain ⟨β, hβ⟩ := exists_sq_eq_eval_Ψ₂Sq (W.map φ) x₀
  exact ⟨x₀, β,
    hβ, normEDS_consecutive_eq_zero_of_eval_eq_zero (W.map φ) hβ hΨ0 hΦ0⟩

end Descent

section Secp256k1

/-- secp256k1 base-changed to the algebraic closure of its prime field. -/
noncomputable def secp256k1Bar : WeierstrassCurve (AlgebraicClosure (ZMod Secp256k1.p)) :=
  secp256k1.map (algebraMap (ZMod Secp256k1.p) (AlgebraicClosure (ZMod Secp256k1.p)))

/-- **secp256k1 instantiation of the descent.** A non-coprimality of `Φ n`/`ΨSq n` over
`𝔽_p` produces two consecutive scalar-`normEDS` zeros over `𝔽̄_p` — the N5 obligation for
secp256k1, reduced to the scalar sequence. -/
theorem secp256k1_exists_normEDS_consecutive_eq_zero_of_not_isCoprime (n : ℤ)
    (h : ¬ IsCoprime (secp256k1.Φ n) (secp256k1.ΨSq n)) :
    ∃ (x₀ β : AlgebraicClosure (ZMod Secp256k1.p)),
      β ^ 2 = secp256k1Bar.Ψ₂Sq.eval x₀ ∧
      normEDS β (secp256k1Bar.Ψ₃.eval x₀) (secp256k1Bar.preΨ₄.eval x₀) n = 0 ∧
        (normEDS β (secp256k1Bar.Ψ₃.eval x₀) (secp256k1Bar.preΨ₄.eval x₀) (n - 1) = 0 ∨
          normEDS β (secp256k1Bar.Ψ₃.eval x₀) (secp256k1Bar.preΨ₄.eval x₀) (n + 1) = 0) :=
  exists_normEDS_consecutive_eq_zero_of_not_isCoprime
    (algebraMap (ZMod Secp256k1.p) (AlgebraicClosure (ZMod Secp256k1.p))) secp256k1 n h

/-- **N4, monic half.** The multiplication-by-`n` numerator `Φ n` is monic (Mathlib's
`leadingCoeff_Φ` is unconditional), so its degree is genuine and `Φ n ≠ 0`. -/
theorem secp256k1_Φ_monic (n : ℤ) : (secp256k1.Φ n).Monic :=
  secp256k1.leadingCoeff_Φ n

end Secp256k1

end Ecdlp.Curve
