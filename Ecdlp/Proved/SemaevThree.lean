import Mathlib
import Ecdlp.Proved.Secp256k1Curve

/-!
# Semaev's third summation polynomial `S₃`

Formalizes Semaev's 3rd summation polynomial for a short Weierstrass curve
`y² = x³ + a·x + b` and proves its **forward direction** in both nondegenerate cases:
whenever a field element `x₃` is the `x`-coordinate of the sum of two curve points
`(x₁,y₁), (x₂,y₂)` — the `x₁ ≠ x₂` "chord" case (`S₃_eq_zero_of_chord`) or the `x₁ = x₂`
"tangent"/doubling case (`S₃_eq_zero_of_tangent`) — the triple `(x₁,x₂,x₃)` is a root of
`S₃`. Equivalently: if three affine points with these `x`-coordinates satisfy
`P₁ + P₂ + P₃ = O`, then `S₃(x₁,x₂,x₃) = 0`.

Summation polynomials (Semaev, 2004) are the algebraic backbone of index-calculus /
Gröbner-basis attacks on ECDLP over extension fields; `Sₙ = 0` encodes the existence of
`n` curve points with prescribed `x`-coordinates summing to `O`, and `S₃` is their base
case. To our knowledge this is the first formalization of a Semaev summation polynomial in
Lean/Mathlib. It is a **construction** (a barrier item in `BARRIERS.md`, "Semaev
polynomials"), not an attack: the forward implication is a necessary condition, and by
itself computes nothing about any discrete log — it enriches the verified substrate.

**Certificate provenance (Fable → kernel).** The two ring identities driving the proof —
the cofactor identity `(x₁−x₂)²·S₃ = T² − 4·f₁·f₂` and the syzygy
`N = (2·y₁·y₂ − T) − (y₁²−f₁) − (y₂²−f₂)`, with `fᵢ = xᵢ³ + a·xᵢ + b`,
`T = (x₁+x₂)(x₁·x₂+a) + 2b − (x₁−x₂)²·x₃`, and `N = (x₁−x₂)²(x₁+x₂+x₃) − (y₂−y₁)²` —
were designed and verified by exact symbolic computation (sympy: Gröbner reduction plus an
independent iterated-resultant elimination) before transcription; here the Lean kernel
re-checks them via `linear_combination`/`ring`. The `y₁·y₂` cross term is eliminated by
conjugate multiplication, which is precisely why `S₃` is sign-symmetric — it captures the
`x`-coordinate of both `P₁+P₂` and `P₁−P₂` (the two roots of `S₃(x₁,x₂,·)`).
-/

namespace Ecdlp.Semaev

variable {F : Type*} [CommRing F]

/-- **Semaev's 3rd summation polynomial** for `y² = x³ + a·x + b`:
`S₃(x₁,x₂,x₃) = (x₁−x₂)²·x₃² − 2·((x₁+x₂)(x₁·x₂+a)+2b)·x₃ + ((x₁·x₂−a)² − 4b·(x₁+x₂))`.
It is symmetric in its three arguments (`S₃_symm₁₂`, `S₃_symm₂₃`), and — as proved below —
`S₃(x₁,x₂,x₃) = 0` whenever three affine points with those `x`-coordinates sum to `O`. -/
def S₃ (a b x₁ x₂ x₃ : F) : F :=
  (x₁ - x₂) ^ 2 * x₃ ^ 2
    - 2 * ((x₁ + x₂) * (x₁ * x₂ + a) + 2 * b) * x₃
    + ((x₁ * x₂ - a) ^ 2 - 4 * b * (x₁ + x₂))

/-- `S₃` is symmetric under swapping its first two `x`-arguments. -/
theorem S₃_symm₁₂ (a b x₁ x₂ x₃ : F) : S₃ a b x₁ x₂ x₃ = S₃ a b x₂ x₁ x₃ := by
  simp only [S₃]; ring

/-- `S₃` is symmetric under swapping its last two `x`-arguments — together with
`S₃_symm₁₂` this shows `S₃` is fully symmetric, as a summation polynomial must be. -/
theorem S₃_symm₂₃ (a b x₁ x₂ x₃ : F) : S₃ a b x₁ x₂ x₃ = S₃ a b x₁ x₃ x₂ := by
  simp only [S₃]; ring

variable {K : Type*} [Field K]

/-- **Forward direction of Semaev's `S₃` (chord case).** For a short Weierstrass curve
`y² = x³ + a·x + b` over a field: if `(x₁,y₁)` and `(x₂,y₂)` lie on the curve with
`x₁ ≠ x₂`, and `x₃` is the `x`-coordinate of their chord-sum — stated in the
cleared-denominator form `(x₁−x₂)²·(x₁+x₂+x₃) = (y₂−y₁)²`, i.e.
`x₃ = ((y₂−y₁)/(x₂−x₁))² − x₁ − x₂` — then `S₃(x₁,x₂,x₃) = 0`.

Contrapositively: a triple `(x₁,x₂,x₃)` that is **not** a root of `S₃` can never arise as
the `x`-coordinates of three collinear points of `E`. The proof is the certified two-step
elimination: `hchord` and the curve equations give `2·y₁·y₂ = T`; squaring and applying the
cofactor identity yields `(x₁−x₂)²·S₃ = T² − 4·f₁·f₂ = 0`, and `(x₁−x₂)² ≠ 0` cancels. -/
theorem S₃_eq_zero_of_chord (a b x₁ y₁ x₂ y₂ x₃ : K)
    (h₁ : y₁ ^ 2 = x₁ ^ 3 + a * x₁ + b) (h₂ : y₂ ^ 2 = x₂ ^ 3 + a * x₂ + b)
    (hx : x₁ ≠ x₂)
    (hchord : (x₁ - x₂) ^ 2 * (x₁ + x₂ + x₃) = (y₂ - y₁) ^ 2) :
    S₃ a b x₁ x₂ x₃ = 0 := by
  have hne : (x₁ - x₂) ^ 2 ≠ 0 := pow_ne_zero 2 (sub_ne_zero.mpr hx)
  -- Step 1 (syzygy `N ≡ 2·y₁·y₂ − T`, with `N = 0` by `hchord`): `2·y₁·y₂ = T`.
  have hT : 2 * y₁ * y₂
      = (x₁ + x₂) * (x₁ * x₂ + a) + 2 * b - (x₁ - x₂) ^ 2 * x₃ := by
    linear_combination hchord + h₁ + h₂
  -- Step 2 (cofactor identity, using `T² = 4·y₁²·y₂² = 4·f₁·f₂`): `(x₁−x₂)²·S₃ = 0`.
  have key : (x₁ - x₂) ^ 2 * S₃ a b x₁ x₂ x₃ = 0 := by
    simp only [S₃]
    linear_combination
      (-(((x₁ + x₂) * (x₁ * x₂ + a) + 2 * b - (x₁ - x₂) ^ 2 * x₃) + 2 * y₁ * y₂)) * hT
      + (4 * (x₂ ^ 3 + a * x₂ + b)) * h₁ + (4 * y₁ ^ 2) * h₂
  exact (mul_eq_zero.mp key).resolve_left hne

/-- **Forward direction of Semaev's `S₃` (tangent / doubling case).** The `x₁ = x₂`
companion of `S₃_eq_zero_of_chord`: if `(x₁,y₁)` is a curve point and `x₃` is the
`x`-coordinate of `2·(x₁,y₁)` — stated in the cleared-denominator doubling form
`4·y₁²·(x₃ + 2·x₁) = (3·x₁² + a)²`, i.e. `x₃ = ((3·x₁²+a)/(2·y₁))² − 2·x₁` — then
`S₃(x₁,x₁,x₃) = 0` (equivalently `2P + P₃ = O ⇒ S₃(x_P, x_P, x_{P₃}) = 0`).

Unlike the chord case there is no `y₁·y₂` cross term, so no cofactor cancellation is
needed: `S₃(x₁,x₁,x₃)` collapses (via `S₃_symm₁₂`/algebra) to `−4·f₁·x₃ + (x₁²−a)² − 8b·x₁`,
and substituting the doubling relation and the curve equation makes it vanish identically —
a single certified `linear_combination`. Together with `S₃_eq_zero_of_chord` this proves the
forward direction of `S₃` in every nondegenerate case. -/
theorem S₃_eq_zero_of_tangent (a b x₁ y₁ x₃ : K)
    (h₁ : y₁ ^ 2 = x₁ ^ 3 + a * x₁ + b)
    (hdbl : 4 * y₁ ^ 2 * (x₃ + 2 * x₁) = (3 * x₁ ^ 2 + a) ^ 2) :
    S₃ a b x₁ x₁ x₃ = 0 := by
  simp only [S₃]
  linear_combination (4 * x₃ + 8 * x₁) * h₁ - hdbl

/-- **Reverse direction of Semaev's `S₃` — the two roots.** As a polynomial in its third
argument `S₃` is quadratic with leading coefficient `(x₁−x₂)²`, and (on the curve) its two
roots are exactly the `x`-coordinates of `P₁+P₂` and `P₁−P₂`. So if `(x₁,y₁), (x₂,y₂)` lie on
`y² = x³ + a·x + b` with `x₁ ≠ x₂` and `S₃(x₁,x₂,x₃) = 0`, then `x₃` is one of those two:
`(x₁−x₂)²·x₃ = (y₂−y₁)² − (x₁+x₂)(x₁−x₂)²` (the cleared form of `x₃ = x(P₁+P₂)`) **or**
`(x₁−x₂)²·x₃ = (y₂+y₁)² − (x₁+x₂)(x₁−x₂)²` (the cleared `x₃ = x(P₁−P₂)`).

The proof is the certified master factorization `(x₁−x₂)²·S₃ = (D·x₃−R₊)(D·x₃−R₋)` (an exact
`ring` identity modulo the curve equations, cofactors from a sympy Gröbner + resultant
certificate); with `S₃ = 0` and `(x₁−x₂)² ≠ 0` in a field, one factor vanishes. -/
theorem S₃_root_of_eq_zero (a b x₁ y₁ x₂ y₂ x₃ : K)
    (h₁ : y₁ ^ 2 = x₁ ^ 3 + a * x₁ + b) (h₂ : y₂ ^ 2 = x₂ ^ 3 + a * x₂ + b)
    (hx : x₁ ≠ x₂) (hS : S₃ a b x₁ x₂ x₃ = 0) :
    (x₁ - x₂) ^ 2 * x₃ = (y₂ - y₁) ^ 2 - (x₁ + x₂) * (x₁ - x₂) ^ 2 ∨
    (x₁ - x₂) ^ 2 * x₃ = (y₂ + y₁) ^ 2 - (x₁ + x₂) * (x₁ - x₂) ^ 2 := by
  have hprod :
      ((x₁ - x₂) ^ 2 * x₃ - ((y₂ - y₁) ^ 2 - (x₁ + x₂) * (x₁ - x₂) ^ 2))
    * ((x₁ - x₂) ^ 2 * x₃ - ((y₂ + y₁) ^ 2 - (x₁ + x₂) * (x₁ - x₂) ^ 2)) = 0 := by
    have hid :
        ((x₁ - x₂) ^ 2 * x₃ - ((y₂ - y₁) ^ 2 - (x₁ + x₂) * (x₁ - x₂) ^ 2))
      * ((x₁ - x₂) ^ 2 * x₃ - ((y₂ + y₁) ^ 2 - (x₁ + x₂) * (x₁ - x₂) ^ 2))
      = (x₁ - x₂) ^ 2 * S₃ a b x₁ x₂ x₃ := by
      simp only [S₃]
      linear_combination
        (-(2 * (x₁ - x₂) ^ 2 * x₃ + 2 * (x₁ + x₂) * (x₁ - x₂) ^ 2
            + (y₂ ^ 2 - y₁ ^ 2) + (x₂ ^ 3 - x₁ ^ 3) + a * (x₂ - x₁))) * h₁
        + (-(2 * (x₁ - x₂) ^ 2 * x₃ + 2 * (x₁ + x₂) * (x₁ - x₂) ^ 2
            - (y₂ ^ 2 - y₁ ^ 2) - (x₂ ^ 3 - x₁ ^ 3) - a * (x₂ - x₁))) * h₂
    rw [hid, hS, mul_zero]
  rcases mul_eq_zero.mp hprod with h | h
  · exact Or.inl (sub_eq_zero.mp h)
  · exact Or.inr (sub_eq_zero.mp h)

/-- **Semaev's `S₃`, full characterization (iff).** Combining the forward direction
(`S₃_eq_zero_of_chord`) with the reverse (`S₃_root_of_eq_zero`): for points `(x₁,y₁), (x₂,y₂)`
on `y² = x³ + a·x + b` with `x₁ ≠ x₂`,
`S₃(x₁,x₂,x₃) = 0` **iff** `x₃` is the `x`-coordinate of `P₁+P₂` or of `P₁−P₂` (in cleared
form). The `+` disjunct is literally the chord hypothesis of the forward direction; the `−`
disjunct is the same with `y₂ ↦ −y₂` (the point `−P₂`). This is the complete statement of
`S₃` as the elimination of `y₁,y₂` from "three points sum to `O`". -/
theorem S₃_eq_zero_iff (a b x₁ y₁ x₂ y₂ x₃ : K)
    (h₁ : y₁ ^ 2 = x₁ ^ 3 + a * x₁ + b) (h₂ : y₂ ^ 2 = x₂ ^ 3 + a * x₂ + b)
    (hx : x₁ ≠ x₂) :
    S₃ a b x₁ x₂ x₃ = 0 ↔
      (x₁ - x₂) ^ 2 * (x₁ + x₂ + x₃) = (y₂ - y₁) ^ 2 ∨
      (x₁ - x₂) ^ 2 * (x₁ + x₂ + x₃) = (y₂ + y₁) ^ 2 := by
  constructor
  · intro hS
    rcases S₃_root_of_eq_zero a b x₁ y₁ x₂ y₂ x₃ h₁ h₂ hx hS with h | h
    · exact Or.inl (by linear_combination h)
    · exact Or.inr (by linear_combination h)
  · rintro (h | h)
    · exact S₃_eq_zero_of_chord a b x₁ y₁ x₂ y₂ x₃ h₁ h₂ hx h
    · exact S₃_eq_zero_of_chord a b x₁ y₁ x₂ (-y₂) x₃ h₁ (by linear_combination h₂) hx
        (by linear_combination h)

open Ecdlp.Curve

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Semaev's `S₃` for secp256k1 (`y² = x³ + 7`), forward direction.** Specialization of
`S₃_eq_zero_of_chord` to the secp256k1 curve (`a = 0`, `b = 7`): if `(x₁,y₁)` and `(x₂,y₂)`
satisfy `y² = x³ + 7` with `x₁ ≠ x₂`, and `x₃` is the `x`-coordinate of their chord-sum,
then `(x₁,x₂,x₃)` is a root of secp256k1's third Semaev summation polynomial. -/
theorem secp256k1_semaev_three_chord
    (x₁ y₁ x₂ y₂ x₃ : ZMod Secp256k1.p)
    (h₁ : y₁ ^ 2 = x₁ ^ 3 + 7) (h₂ : y₂ ^ 2 = x₂ ^ 3 + 7)
    (hx : x₁ ≠ x₂)
    (hchord : (x₁ - x₂) ^ 2 * (x₁ + x₂ + x₃) = (y₂ - y₁) ^ 2) :
    S₃ (0 : ZMod Secp256k1.p) 7 x₁ x₂ x₃ = 0 :=
  S₃_eq_zero_of_chord 0 7 x₁ y₁ x₂ y₂ x₃
    (by linear_combination h₁) (by linear_combination h₂) hx hchord

/-- **Semaev's `S₃` for secp256k1 (`y² = x³ + 7`), tangent/doubling case.** Specialization
of `S₃_eq_zero_of_tangent` to secp256k1 (`a = 0`, `b = 7`): if `(x₁,y₁)` satisfies
`y² = x³ + 7` and `x₃` is the `x`-coordinate of `2·(x₁,y₁)` (`4·y₁²·(x₃+2·x₁) = 9·x₁⁴`),
then `(x₁,x₁,x₃)` is a root of secp256k1's third Semaev summation polynomial. With
`secp256k1_semaev_three_chord`, secp256k1's `S₃` forward direction is complete. -/
theorem secp256k1_semaev_three_tangent
    (x₁ y₁ x₃ : ZMod Secp256k1.p)
    (h₁ : y₁ ^ 2 = x₁ ^ 3 + 7)
    (hdbl : 4 * y₁ ^ 2 * (x₃ + 2 * x₁) = (3 * x₁ ^ 2) ^ 2) :
    S₃ (0 : ZMod Secp256k1.p) 7 x₁ x₁ x₃ = 0 :=
  S₃_eq_zero_of_tangent 0 7 x₁ y₁ x₃
    (by linear_combination h₁) (by linear_combination hdbl)

open WeierstrassCurve.Affine in
/-- **Semaev's `S₃` for secp256k1, on actual curve points (chord case).** The point-group
form of `secp256k1_semaev_three_chord`: for genuine affine points of the Mathlib elliptic
curve `secp256k1.toAffine.Point`, if `P₁ + P₂ + P₃ = O` (the group identity) with
`x(P₁) ≠ x(P₂)`, then their `x`-coordinates `(x₁,x₂,x₃)` are a root of secp256k1's third
Semaev summation polynomial. This is the honest statement — the hypothesis is the actual
elliptic-curve group relation, not a raw coordinate equation. The proof unfolds Mathlib's
formalized chord addition (`Point.add_of_X_ne`, `slope_of_X_ne`, `addX`) to recover
`x₃ = x(P₁+P₂)`, clears the denominator, and applies `secp256k1_semaev_three_chord`. -/
theorem secp256k1_semaev_three_point
    {x₁ y₁ x₂ y₂ x₃ y₃ : ZMod Secp256k1.p}
    (h₁ : secp256k1.toAffine.Nonsingular x₁ y₁)
    (h₂ : secp256k1.toAffine.Nonsingular x₂ y₂)
    (h₃ : secp256k1.toAffine.Nonsingular x₃ y₃)
    (hx : x₁ ≠ x₂)
    (hsum : Point.some x₁ y₁ h₁ + Point.some x₂ y₂ h₂ + Point.some x₃ y₃ h₃ = 0) :
    S₃ (0 : ZMod Secp256k1.p) 7 x₁ x₂ x₃ = 0 := by
  rw [add_eq_zero_iff_eq_neg, Point.add_of_X_ne hx, Point.neg_some, Point.some.injEq] at hsum
  have hX := hsum.1
  rw [slope_of_X_ne hx] at hX
  have hd : x₁ - x₂ ≠ 0 := sub_ne_zero.mpr hx
  have hc₁ : y₁ ^ 2 = x₁ ^ 3 + 7 := by
    have he : secp256k1.toAffine.Equation x₁ y₁ := h₁.1
    rw [WeierstrassCurve.Affine.equation_iff] at he
    simp only [secp256k1] at he; linear_combination he
  have hc₂ : y₂ ^ 2 = x₂ ^ 3 + 7 := by
    have he : secp256k1.toAffine.Equation x₂ y₂ := h₂.1
    rw [WeierstrassCurve.Affine.equation_iff] at he
    simp only [secp256k1] at he; linear_combination he
  have hX2 : (y₁ - y₂) ^ 2 / (x₁ - x₂) ^ 2 = x₁ + x₂ + x₃ := by
    simp only [WeierstrassCurve.Affine.addX, secp256k1, div_pow] at hX
    linear_combination hX
  rw [div_eq_iff (pow_ne_zero 2 hd)] at hX2
  have hchord : (x₁ - x₂) ^ 2 * (x₁ + x₂ + x₃) = (y₂ - y₁) ^ 2 := by
    linear_combination -hX2
  exact secp256k1_semaev_three_chord x₁ y₁ x₂ y₂ x₃ hc₁ hc₂ hx hchord

open WeierstrassCurve.Affine in
/-- **Semaev's `S₃` for secp256k1, on actual curve points (tangent/doubling case).** The
`P₁ = P₂` companion of `secp256k1_semaev_three_point`: if `2•P₁ + P₃ = O` for genuine points
of `secp256k1.toAffine.Point` with `P₁` not `2`-torsion (`y₁ ≠ negY x₁ y₁`, i.e. `2·y₁ ≠ 0`),
then `S₃(x₁,x₁,x₃) = 0`. Together with `secp256k1_semaev_three_point`, the `S₃` forward
direction holds for Mathlib's formalized elliptic-curve group law in every nondegenerate case.
Unfolds the tangent doubling (`Point.add_of_Y_ne`, `slope_of_Y_ne`) to recover `x₃ = x(2P₁)`,
clears the denominator, and applies `secp256k1_semaev_three_tangent`. -/
theorem secp256k1_semaev_three_point_double
    {x₁ y₁ x₃ y₃ : ZMod Secp256k1.p}
    (h₁ : secp256k1.toAffine.Nonsingular x₁ y₁)
    (h₃ : secp256k1.toAffine.Nonsingular x₃ y₃)
    (hy : y₁ ≠ secp256k1.toAffine.negY x₁ y₁)
    (hsum : Point.some x₁ y₁ h₁ + Point.some x₁ y₁ h₁ + Point.some x₃ y₃ h₃ = 0) :
    S₃ (0 : ZMod Secp256k1.p) 7 x₁ x₁ x₃ = 0 := by
  rw [add_eq_zero_iff_eq_neg, Point.add_of_Y_ne hy, Point.neg_some, Point.some.injEq] at hsum
  have hX := hsum.1
  have hnegY : secp256k1.toAffine.negY x₁ y₁ = -y₁ := by
    simp [WeierstrassCurve.Affine.negY, secp256k1]
  have h2y : (2 : ZMod Secp256k1.p) * y₁ ≠ 0 := by
    have hd : y₁ - secp256k1.toAffine.negY x₁ y₁ ≠ 0 := sub_ne_zero.mpr hy
    rw [hnegY] at hd; intro hc; exact hd (by linear_combination hc)
  have hslope : secp256k1.toAffine.slope x₁ x₁ y₁ y₁ = 3 * x₁ ^ 2 / (2 * y₁) := by
    rw [WeierstrassCurve.Affine.slope_of_Y_ne rfl hy, hnegY]
    simp only [secp256k1, mul_zero, zero_mul, add_zero, sub_zero]
    rw [show y₁ - -y₁ = 2 * y₁ from by ring]
  have hc₁ : y₁ ^ 2 = x₁ ^ 3 + 7 := by
    have he : secp256k1.toAffine.Equation x₁ y₁ := h₁.1
    rw [WeierstrassCurve.Affine.equation_iff] at he
    simp only [secp256k1] at he; linear_combination he
  rw [hslope] at hX
  have hX2 : (3 * x₁ ^ 2) ^ 2 / (2 * y₁) ^ 2 = x₃ + 2 * x₁ := by
    simp only [WeierstrassCurve.Affine.addX, secp256k1, div_pow] at hX
    linear_combination hX
  rw [div_eq_iff (pow_ne_zero 2 h2y)] at hX2
  have hdbl : 4 * y₁ ^ 2 * (x₃ + 2 * x₁) = (3 * x₁ ^ 2) ^ 2 := by
    linear_combination -hX2
  exact secp256k1_semaev_three_tangent x₁ y₁ x₃ hc₁ hdbl

/-- **Semaev's `S₃` for secp256k1 (`y² = x³ + 7`), full characterization (iff).**
Specialization of `S₃_eq_zero_iff` to secp256k1: for points `(x₁,y₁), (x₂,y₂)` on the curve
with `x₁ ≠ x₂`, `S₃(x₁,x₂,x₃) = 0` iff `x₃` is the `x`-coordinate of `P₁+P₂` or of `P₁−P₂`
(cleared form). This is the complete `S₃` characterization for secp256k1 — forward and
reverse together. -/
theorem secp256k1_semaev_three_iff
    (x₁ y₁ x₂ y₂ x₃ : ZMod Secp256k1.p)
    (h₁ : y₁ ^ 2 = x₁ ^ 3 + 7) (h₂ : y₂ ^ 2 = x₂ ^ 3 + 7) (hx : x₁ ≠ x₂) :
    S₃ (0 : ZMod Secp256k1.p) 7 x₁ x₂ x₃ = 0 ↔
      (x₁ - x₂) ^ 2 * (x₁ + x₂ + x₃) = (y₂ - y₁) ^ 2 ∨
      (x₁ - x₂) ^ 2 * (x₁ + x₂ + x₃) = (y₂ + y₁) ^ 2 :=
  S₃_eq_zero_iff 0 7 x₁ y₁ x₂ y₂ x₃ (by linear_combination h₁) (by linear_combination h₂) hx

end Ecdlp.Semaev
