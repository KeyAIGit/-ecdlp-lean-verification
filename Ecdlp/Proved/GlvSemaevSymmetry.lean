import Mathlib
import Ecdlp.Proved.CubeRoot
import Ecdlp.Proved.GlvAutomorphism
import Ecdlp.Proved.GlvMonoidHom
import Ecdlp.Proved.SemaevFour

/-!
# GLV covariance of the third and fourth Semaev polynomials

For a cube root of unity `β`, simultaneous scaling of every `x`-coordinate has the
following exact effect on the `a = 0` Semaev polynomials:

* `S₃(βx₁, βx₂, βx₃) = β S₃(x₁, x₂, x₃)`;
* `S₄(βx₁, βx₂, βx₃, βx₄) = S₄(x₁, x₂, x₃, x₄)`.

The `S₄` theorem uses the exact `resultant _ _ 2 2` normalization from
`SemaevFour.lean`, including degenerate quadratic slices. These identities establish
the diagonal action only; they do not classify the full coordinatewise stabilizer and
do not assert invariance of a generic fixed-target slice.
-/

namespace Ecdlp.Semaev

open Polynomial

variable {F : Type*} [CommRing F]

/-- The closed formula for the resultant of two quadratic coefficient triples. -/
private def quadraticResultant
    (f₂ f₁ f₀ g₂ g₁ g₀ : F) : F :=
  f₂ ^ 2 * g₀ ^ 2
    - f₂ * f₁ * g₁ * g₀
    - 2 * f₂ * f₀ * g₂ * g₀
    + f₂ * f₀ * g₁ ^ 2
    + f₁ ^ 2 * g₂ * g₀
    - f₁ * f₀ * g₂ * g₁
    + f₀ ^ 2 * g₂ ^ 2

/-- The fixed-size `2 × 2` resultant is the closed quadratic formula, even when an
actual polynomial degree drops below two. -/
private theorem resultant_quadratic
    (f₂ f₁ f₀ g₂ g₁ g₀ : F) :
    (C f₂ * X ^ 2 + C f₁ * X + C f₀).resultant
        (C g₂ * X ^ 2 + C g₁ * X + C g₀) 2 2
      = quadraticResultant f₂ f₁ f₀ g₂ g₁ g₀ := by
  let f : F[X] := C f₂ * X ^ 2 + C f₁ * X + C f₀
  let g : F[X] := C g₂ * X ^ 2 + C g₁ * X + C g₀
  have hsylvester :
      f.sylvester g 2 2 =
        !![g₀, 0, f₀, 0;
           g₁, g₀, f₁, f₀;
           g₂, g₁, f₂, f₁;
           0, g₂, 0, f₂] := by
    ext i j
    induction j using Fin.addCases with
    | left j =>
        fin_cases i <;> fin_cases j <;>
          norm_num [f, g, Polynomial.sylvester, Fin.addCases, Fin.castAdd, Fin.castLE,
            Fin.addNat, Polynomial.coeff_X]
    | right j =>
        fin_cases i <;> fin_cases j <;>
          norm_num [f, g, Polynomial.sylvester, Fin.addCases, Fin.castAdd, Fin.castLE,
            Fin.addNat, Polynomial.coeff_X]
  change f.resultant g 2 2 = quadraticResultant f₂ f₁ f₀ g₂ g₁ g₀
  rw [Polynomial.resultant, hsylvester, Matrix.det_succ_row_zero]
  simp [Fin.sum_univ_succ, Matrix.det_fin_three, quadraticResultant, Fin.succAbove]
  ring_nf

/-- The exact fixed-size resultant definition of `S₄` reduced to its six quadratic
slice coefficients. -/
private theorem S₄_zero_a_explicit
    (b x₁ x₂ x₃ x₄ : F) :
    S₄ 0 b x₁ x₂ x₃ x₄ =
      quadraticResultant
        ((x₁ - x₂) ^ 2)
        (-(2 * ((x₁ + x₂) * (x₁ * x₂) + 2 * b)))
        ((x₁ * x₂) ^ 2 - 4 * b * (x₁ + x₂))
        ((x₃ - x₄) ^ 2)
        (-(2 * ((x₃ + x₄) * (x₃ * x₄) + 2 * b)))
        ((x₃ * x₄) ^ 2 - 4 * b * (x₃ + x₄)) := by
  simpa only [S₄, S₃poly, add_zero, sub_zero] using
    resultant_quadratic
      ((x₁ - x₂) ^ 2)
      (-(2 * ((x₁ + x₂) * (x₁ * x₂) + 2 * b)))
      ((x₁ * x₂) ^ 2 - 4 * b * (x₁ + x₂))
      ((x₃ - x₄) ^ 2)
      (-(2 * ((x₃ + x₄) * (x₃ * x₄) + 2 * b)))
      ((x₃ * x₄) ^ 2 - 4 * b * (x₃ + x₄))

/-- The quadratic resultant is invariant when both coefficient triples receive
the GLV weights `(β², 1, β)`. -/
private theorem quadraticResultant_weighted_invariant
    (β f₂ f₁ f₀ g₂ g₁ g₀ : F) (hβ : β ^ 3 = 1) :
    quadraticResultant
        (β ^ 2 * f₂) f₁ (β * f₀)
        (β ^ 2 * g₂) g₁ (β * g₀)
      = quadraticResultant f₂ f₁ f₀ g₂ g₁ g₀ := by
  simp only [quadraticResultant]
  linear_combination
    ((-f₂ * f₁ * g₁ * g₀ + f₂ * f₀ * g₁ ^ 2
        + f₁ ^ 2 * g₂ * g₀ - f₁ * f₀ * g₂ * g₁)
      + (β ^ 3 + 1)
        * (f₂ ^ 2 * g₀ ^ 2 - 2 * f₂ * f₀ * g₂ * g₀ + f₀ ^ 2 * g₂ ^ 2)) * hβ

/-- Diagonal cube covariance of `S₃` over an arbitrary commutative ring. -/
theorem S₃_diagonal_cube_covariance
    (b β x₁ x₂ x₃ : F) (hβ : β ^ 3 = 1) :
    S₃ 0 b (β * x₁) (β * x₂) (β * x₃)
      = β * S₃ 0 b x₁ x₂ x₃ := by
  simp only [S₃, zero_add, sub_zero]
  linear_combination
    (β * ((x₁ - x₂) ^ 2 * x₃ ^ 2
      - 2 * (x₁ + x₂) * (x₁ * x₂) * x₃
      + (x₁ * x₂) ^ 2)) * hβ

/-- Since `β³ = 1` makes `β` a unit, diagonal scaling preserves the zero condition
of `S₃` in both directions, without requiring a domain. -/
theorem S₃_diagonal_cube_zero_iff
    (b β x₁ x₂ x₃ : F) (hβ : β ^ 3 = 1) :
    S₃ 0 b (β * x₁) (β * x₂) (β * x₃) = 0
      ↔ S₃ 0 b x₁ x₂ x₃ = 0 := by
  rw [S₃_diagonal_cube_covariance b β x₁ x₂ x₃ hβ]
  have hβinv : β ^ 2 * β = 1 := by
    simpa [pow_succ] using hβ
  constructor
  · intro h
    calc
      S₃ 0 b x₁ x₂ x₃ = (β ^ 2 * β) * S₃ 0 b x₁ x₂ x₃ := by rw [hβinv, one_mul]
      _ = β ^ 2 * (β * S₃ 0 b x₁ x₂ x₃) := by ring
      _ = 0 := by rw [h, mul_zero]
  · intro h
    rw [h, mul_zero]

/-- Diagonal cube invariance of the exact fixed-size resultant definition of `S₄`. -/
theorem S₄_diagonal_cube_invariant
    (b β x₁ x₂ x₃ x₄ : F) (hβ : β ^ 3 = 1) :
    S₄ 0 b (β * x₁) (β * x₂) (β * x₃) (β * x₄)
      = S₄ 0 b x₁ x₂ x₃ x₄ := by
  rw [S₄_zero_a_explicit b (β * x₁) (β * x₂) (β * x₃) (β * x₄),
    S₄_zero_a_explicit b x₁ x₂ x₃ x₄]
  have h₂12 :
      (β * x₁ - β * x₂) ^ 2 = β ^ 2 * (x₁ - x₂) ^ 2 := by
    ring
  have h₁12 :
      -(2 * ((β * x₁ + β * x₂) * ((β * x₁) * (β * x₂)) + 2 * b))
        = -(2 * ((x₁ + x₂) * (x₁ * x₂) + 2 * b)) := by
    linear_combination (-2 * (x₁ + x₂) * (x₁ * x₂)) * hβ
  have h₀12 :
      ((β * x₁) * (β * x₂)) ^ 2 - 4 * b * (β * x₁ + β * x₂)
        = β * ((x₁ * x₂) ^ 2 - 4 * b * (x₁ + x₂)) := by
    linear_combination (β * (x₁ * x₂) ^ 2) * hβ
  have h₂34 :
      (β * x₃ - β * x₄) ^ 2 = β ^ 2 * (x₃ - x₄) ^ 2 := by
    ring
  have h₁34 :
      -(2 * ((β * x₃ + β * x₄) * ((β * x₃) * (β * x₄)) + 2 * b))
        = -(2 * ((x₃ + x₄) * (x₃ * x₄) + 2 * b)) := by
    linear_combination (-2 * (x₃ + x₄) * (x₃ * x₄)) * hβ
  have h₀34 :
      ((β * x₃) * (β * x₄)) ^ 2 - 4 * b * (β * x₃ + β * x₄)
        = β * ((x₃ * x₄) ^ 2 - 4 * b * (x₃ + x₄)) := by
    linear_combination (β * (x₃ * x₄) ^ 2) * hβ
  rw [h₂12, h₁12, h₀12, h₂34, h₁34, h₀34]
  exact quadraticResultant_weighted_invariant β
    ((x₁ - x₂) ^ 2)
    (-(2 * ((x₁ + x₂) * (x₁ * x₂) + 2 * b)))
    ((x₁ * x₂) ^ 2 - 4 * b * (x₁ + x₂))
    ((x₃ - x₄) ^ 2)
    (-(2 * ((x₃ + x₄) * (x₃ * x₄) + 2 * b)))
    ((x₃ * x₄) ^ 2 - 4 * b * (x₃ + x₄)) hβ

/-- The secp256k1 GLV field factor is a cube root of unity in its base field. -/
private theorem secp256k1_beta_cube :
    (Secp256k1.beta : ZMod Secp256k1.p) ^ 3 = 1 := by
  have hβeig : (Secp256k1.beta : ZMod Secp256k1.p) ^ 2
      + (Secp256k1.beta : ZMod Secp256k1.p) + 1 = 0 := by
    have h0 :
        ((Secp256k1.beta ^ 2 + Secp256k1.beta + 1 : ℕ) :
          ZMod Secp256k1.p) = 0 := by
      rw [ZMod.natCast_eq_zero_iff]
      exact Nat.dvd_of_mod_eq_zero Secp256k1.beta_field_eigenvalue
    push_cast at h0
    linear_combination h0
  exact Ecdlp.Proved.cube_root_of_eigenvalue _ hβeig

/-- Exact `S₃` GLV covariance for secp256k1 (`a = 0`, `b = 7`). -/
theorem secp256k1_S₃_glv_covariance
    (x₁ x₂ x₃ : ZMod Secp256k1.p) :
    S₃ 0 7
        ((Secp256k1.beta : ZMod Secp256k1.p) * x₁)
        ((Secp256k1.beta : ZMod Secp256k1.p) * x₂)
        ((Secp256k1.beta : ZMod Secp256k1.p) * x₃)
      = (Secp256k1.beta : ZMod Secp256k1.p) * S₃ 0 7 x₁ x₂ x₃ :=
  S₃_diagonal_cube_covariance 7 _ x₁ x₂ x₃ secp256k1_beta_cube

/-- The corresponding secp256k1 `S₃ = 0` equivalence. -/
theorem secp256k1_S₃_glv_zero_iff
    (x₁ x₂ x₃ : ZMod Secp256k1.p) :
    S₃ 0 7
        ((Secp256k1.beta : ZMod Secp256k1.p) * x₁)
        ((Secp256k1.beta : ZMod Secp256k1.p) * x₂)
        ((Secp256k1.beta : ZMod Secp256k1.p) * x₃) = 0
      ↔ S₃ 0 7 x₁ x₂ x₃ = 0 :=
  S₃_diagonal_cube_zero_iff 7 _ x₁ x₂ x₃ secp256k1_beta_cube

/-- Exact `S₄` diagonal GLV invariance for secp256k1 (`a = 0`, `b = 7`). -/
theorem secp256k1_S₄_glv_invariant
    (x₁ x₂ x₃ x₄ : ZMod Secp256k1.p) :
    S₄ 0 7
        ((Secp256k1.beta : ZMod Secp256k1.p) * x₁)
        ((Secp256k1.beta : ZMod Secp256k1.p) * x₂)
        ((Secp256k1.beta : ZMod Secp256k1.p) * x₃)
        ((Secp256k1.beta : ZMod Secp256k1.p) * x₄)
      = S₄ 0 7 x₁ x₂ x₃ x₄ :=
  S₄_diagonal_cube_invariant 7 _ x₁ x₂ x₃ x₄ secp256k1_beta_cube

end Ecdlp.Semaev

namespace Ecdlp.Curve

open WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- Applying the GLV automorphism to every point gives an equivalent finite relation.
This is a bijective transport of a relation, not a reduction in relation count. -/
theorem secp256k1_glv_list_sum_eq_iff
    (points : List secp256k1.toAffine.Point)
    (R : secp256k1.toAffine.Point) :
    points.sum = R ↔ (points.map glvHom).sum = glvHom R := by
  have hmap : (points.map glvHom).sum = glvHom points.sum := by
    induction points with
    | nil =>
        simp only [List.map_nil, List.sum_nil, map_zero]
    | cons P points ih =>
        simp only [List.map_cons, List.sum_cons, ih, map_add]
  rw [hmap]
  constructor
  · exact congrArg glvHom
  · intro h
    apply glvPoint_bijective.1
    simpa only [glvHom_apply] using h

/-- Three-point specialization of `secp256k1_glv_list_sum_eq_iff`. -/
theorem secp256k1_glv_three_point_sum_eq_iff
    (P₁ P₂ P₃ R : secp256k1.toAffine.Point) :
    P₁ + P₂ + P₃ = R
      ↔ glvPoint P₁ + glvPoint P₂ + glvPoint P₃ = glvPoint R := by
  simpa only [List.map_cons, List.map_nil, List.sum_cons, List.sum_nil, add_zero,
    add_assoc, glvHom_apply] using
    (secp256k1_glv_list_sum_eq_iff [P₁, P₂, P₃] R)

end Ecdlp.Curve
