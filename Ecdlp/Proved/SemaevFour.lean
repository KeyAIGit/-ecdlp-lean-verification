import Mathlib
import Ecdlp.Proved.SemaevThree

/-!
# Semaev's 4th summation polynomial `S₄`

Builds Semaev's 4th summation polynomial as the **resultant**, over an auxiliary variable `X`,
of `S₃(x₁,x₂,X)` and `S₃(x₃,x₄,X)`:
`S₄(x₁,x₂,x₃,x₄) = Res_X(S₃(x₁,x₂,X), S₃(x₃,x₄,X))`.
This is the recursion index-calculus / Gröbner attacks over extension fields actually use:
`Sₙ = 0` encodes the existence of `n` curve points with prescribed `x`-coordinates summing to
`O`, and `S₄` is the first genuinely new rung above the base case `S₃`
(`Ecdlp/Proved/SemaevThree.lean`).

The construction rides on Mathlib's univariate resultant theory
(`Mathlib/RingTheory/Polynomial/Resultant/Basic.lean`): `S₃` as a degree-2 polynomial in its
third slot (`S₃poly`), then `Polynomial.resultant _ _ 2 2`. The forward direction — a **common
root** of the two cubics-in-`X` forces `S₄ = 0` — needs only the Bézout identity
`exists_mul_add_mul_eq_C_resultant`, valid over any commutative ring (no field, no algebraic
closure). As before this is a **construction, not an attack**: it computes nothing about any
specific discrete log; the value is the verified formalization.
-/

namespace Ecdlp.Semaev

open Polynomial

variable {F : Type*} [CommRing F]

/-- `S₃` viewed as a univariate polynomial in its third argument: the quadratic
`(x₁−x₂)²·X² − 2·((x₁+x₂)(x₁x₂+a)+2b)·X + ((x₁x₂−a)² − 4b(x₁+x₂))`. -/
noncomputable def S₃poly (a b x₁ x₂ : F) : F[X] :=
  C ((x₁ - x₂) ^ 2) * X ^ 2
    + C (-(2 * ((x₁ + x₂) * (x₁ * x₂ + a) + 2 * b))) * X
    + C ((x₁ * x₂ - a) ^ 2 - 4 * b * (x₁ + x₂))

/-- Evaluating `S₃poly` at `x₃` recovers `S₃ a b x₁ x₂ x₃` — the bridge to `SemaevThree`. -/
@[simp] theorem S₃poly_eval (a b x₁ x₂ x₃ : F) :
    (S₃poly a b x₁ x₂).eval x₃ = S₃ a b x₁ x₂ x₃ := by
  simp only [S₃poly, S₃, eval_add, eval_mul, eval_pow, eval_C, eval_X]; ring

/-- `S₃poly` has degree at most `2`. -/
theorem S₃poly_natDegree_le (a b x₁ x₂ : F) : (S₃poly a b x₁ x₂).natDegree ≤ 2 := by
  unfold S₃poly; compute_degree

/-- `S₃poly` is symmetric in `x₁, x₂` (its coefficients are). -/
theorem S₃poly_symm (a b x₁ x₂ : F) : S₃poly a b x₁ x₂ = S₃poly a b x₂ x₁ := by
  simp only [S₃poly]; ring_nf

/-- **Semaev's 4th summation polynomial** `S₄(x₁,x₂,x₃,x₄) = Res_X(S₃(x₁,x₂,X), S₃(x₃,x₄,X))`,
as the resultant (with explicit Sylvester sizes `2, 2`) of the two degree-2 slices of `S₃`. -/
noncomputable def S₄ (a b x₁ x₂ x₃ x₄ : F) : F :=
  (S₃poly a b x₁ x₂).resultant (S₃poly a b x₃ x₄) 2 2

/-- **Forward direction of `S₄` (common root ⟹ vanishing).** If `S₃(x₁,x₂,·)` and
`S₃(x₃,x₄,·)` share a root `X₀` — e.g. `X₀ = x(P₁+P₂) = x(P₃+P₄)` — then
`S₄(x₁,x₂,x₃,x₄) = 0`. Holds over any commutative ring (via the Bézout identity for the
resultant); no field or algebraic closure is needed. Composed with `S₃_eq_zero_of_chord`, a
common `x`-coordinate of a sum from each pair forces the 4-argument Semaev relation. -/
theorem S₄_eq_zero_of_common_root (a b x₁ x₂ x₃ x₄ X₀ : F)
    (h12 : S₃ a b x₁ x₂ X₀ = 0) (h34 : S₃ a b x₃ x₄ X₀ = 0) :
    S₄ a b x₁ x₂ x₃ x₄ = 0 := by
  obtain ⟨p, q, _, _, hpq⟩ := exists_mul_add_mul_eq_C_resultant
    (S₃poly a b x₁ x₂) (S₃poly a b x₃ x₄)
    (S₃poly_natDegree_le a b x₁ x₂) (S₃poly_natDegree_le a b x₃ x₄) (Or.inl (by norm_num))
  have hev := congrArg (eval X₀) hpq
  simp only [eval_add, eval_mul, eval_C, S₃poly_eval, h12, h34, zero_mul, add_zero] at hev
  exact hev.symm

/-- **`S₄` is symmetric under swapping the two pairs** `(x₁,x₂) ↔ (x₃,x₄)` — from
`resultant_comm` with `(-1)^(2·2) = 1`. -/
theorem S₄_block_swap (a b x₁ x₂ x₃ x₄ : F) :
    S₄ a b x₁ x₂ x₃ x₄ = S₄ a b x₃ x₄ x₁ x₂ := by
  rw [S₄, S₄, resultant_comm]; norm_num

/-- **`S₄` is symmetric in `x₁, x₂`** (within the first pair), inherited from `S₃poly_symm`. -/
theorem S₄_symm₁₂ (a b x₁ x₂ x₃ x₄ : F) :
    S₄ a b x₁ x₂ x₃ x₄ = S₄ a b x₂ x₁ x₃ x₄ := by
  rw [S₄, S₄, S₃poly_symm a b x₁ x₂]

/-- **Cleared two-root master factorization of `S₃`'s polynomial slice**, as an identity in
`F[X]`: `(x₁−x₂)²·S₃poly = (D·X − R₊)·(D·X − R₋)` with `D = (x₁−x₂)²`,
`R₊ = (y₂−y₁)² − (x₁+x₂)D`, `R₋ = (y₂+y₁)² − (x₁+x₂)D`. This is the `F[X]` lift of the scalar
master identity behind `SemaevThree.S₃_root_of_eq_zero`; the roots of the RHS are the cleared
`x`-coordinates of `P₁±P₂`, exhibiting `S₃poly` as split with known roots. -/
theorem S₃poly_master_factor (a b x₁ y₁ x₂ y₂ : F)
    (h₁ : y₁ ^ 2 = x₁ ^ 3 + a * x₁ + b) (h₂ : y₂ ^ 2 = x₂ ^ 3 + a * x₂ + b) :
    C ((x₁ - x₂) ^ 2) * S₃poly a b x₁ x₂
      = (C ((x₁ - x₂) ^ 2) * X - C ((y₂ - y₁) ^ 2 - (x₁ + x₂) * (x₁ - x₂) ^ 2))
        * (C ((x₁ - x₂) ^ 2) * X - C ((y₂ + y₁) ^ 2 - (x₁ + x₂) * (x₁ - x₂) ^ 2)) := by
  have e1 : (C y₁ : F[X]) ^ 2 = (C x₁) ^ 3 + C a * C x₁ + C b := by
    have := congrArg (C : F → F[X]) h₁; simpa only [map_add, map_mul, map_pow] using this
  have e2 : (C y₂ : F[X]) ^ 2 = (C x₂) ^ 3 + C a * C x₂ + C b := by
    have := congrArg (C : F → F[X]) h₂; simpa only [map_add, map_mul, map_pow] using this
  simp only [S₃poly, map_add, map_sub, map_mul, map_pow, map_neg, map_ofNat]
  linear_combination
    (2 * (C x₁ - C x₂) ^ 2 * X + 2 * (C x₁ + C x₂) * (C x₁ - C x₂) ^ 2
        + ((C y₂) ^ 2 - (C y₁) ^ 2) + ((C x₂) ^ 3 - (C x₁) ^ 3) + C a * (C x₂ - C x₁)) * e1
    + (2 * (C x₁ - C x₂) ^ 2 * X + 2 * (C x₁ + C x₂) * (C x₁ - C x₂) ^ 2
        - ((C y₂) ^ 2 - (C y₁) ^ 2) - ((C x₂) ^ 3 - (C x₁) ^ 3) - C a * (C x₂ - C x₁)) * e2

open Ecdlp.Curve

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Semaev's `S₄` for secp256k1, forward direction.** If two on-curve pairs share the
`x`-coordinate of a pairwise sum (a common root of the two `S₃` slices), the secp256k1
4th Semaev polynomial vanishes. -/
theorem secp256k1_semaev_four_of_common_root
    (x₁ x₂ x₃ x₄ X₀ : ZMod Secp256k1.p)
    (h12 : S₃ (0 : ZMod Secp256k1.p) 7 x₁ x₂ X₀ = 0)
    (h34 : S₃ (0 : ZMod Secp256k1.p) 7 x₃ x₄ X₀ = 0) :
    S₄ (0 : ZMod Secp256k1.p) 7 x₁ x₂ x₃ x₄ = 0 :=
  S₄_eq_zero_of_common_root 0 7 x₁ x₂ x₃ x₄ X₀ h12 h34

end Ecdlp.Semaev
