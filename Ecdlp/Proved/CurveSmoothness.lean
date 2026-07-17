import Mathlib
import Ecdlp.Proved.Secp256k1Curve

/-!
# General smoothness of `Y²Z = X³ + b·Z³` and the secp256k1 specialization

**Claim `FBL-PURE-001`.** Over an arbitrary field `K`, the projective plane curve
`Y²Z = X³ + b·Z³` is nonsingular whenever `2`, `3` and `b` are all nonzero in `K`.
We prove it directly from the homogeneous cubic `F = Y²Z − X³ − b·Z³` and its three
partial derivatives (the Jacobian criterion), handling the two charts separately:

* **Chart (i), the affine chart `Z ≠ 0`.** A common zero of `F`, `∂F/∂X = −3X²` and
  `∂F/∂Y = 2YZ` forces `X = 0` (as `3 ≠ 0`) and `Y = 0` (as `2 ≠ 0`, `Z ≠ 0`); then
  `F = −b·Z³ = 0` with `b ≠ 0`, `Z ≠ 0` is impossible.
* **Chart (ii), the point at infinity `[0:1:0]` (the locus `Z = 0`).** On the curve
  `Z = 0` forces `X³ = 0`, i.e. `X = 0`; a projective point has some nonzero
  coordinate, so `Y ≠ 0`, whence `∂F/∂Z = Y² − 3b·Z² = Y² ≠ 0`.

The heart is `jacobian_core`, a self-contained field-algebra lemma. We then package
it against Mathlib's genuine projective partial derivatives: `nonsingular_iff`
(`WeierstrassCurve.Projective`) unfolds `Nonsingular` to exactly
`∂F/∂X ≠ 0 ∨ ∂F/∂Y ≠ 0 ∨ ∂F/∂Z ≠ 0`, where the partials are `pderiv`-defined, so we
obtain smoothness in Mathlib's own vocabulary. This is the direct two-chart Jacobian
criterion the task asks for, and it exhibits the two charts. As a cross-check we also
record the discriminant `Δ = −432·b²` (`curveB_Δ`); for `b = 7` this is `−21168`,
matching `secp256k1_Δ_ne_zero`.

Specializing to `b = 7`, `K = ZMod Secp256k1.p` recovers smoothness of secp256k1.

Everything here is symbolic (kernel-checked `ring`/`linear_combination`); no
`native_decide`. The only `decide`s are three tiny `¬ (p ∣ m)` decisions (`m ∈ {2,3,7}`)
used to see `2,3,7 ≠ 0` in `𝔽_p` — the repository's `ZMod`-nonvanishing idiom.

DRAFT-origin note: authored without a local Lean toolchain (CI is the verifier); every
Mathlib name was checked against the pinned Mathlib commit, and CI is the judge.
-/

namespace Ecdlp.Curve

/-- The short Weierstrass curve `Y² = X³ + b` (`a₁ = a₂ = a₃ = a₄ = 0`, `a₆ = b`),
whose projective closure is `Y²Z = X³ + b·Z³`. -/
def curveB {K : Type*} [CommRing K] (b : K) : WeierstrassCurve K where
  a₁ := 0
  a₂ := 0
  a₃ := 0
  a₄ := 0
  a₆ := b

/-! ## Route (a) cross-check: the discriminant `Δ = −432·b²` -/

/-- **The discriminant of `curveB b` is `−432·b²`.** (`b₂ = b₄ = b₈ = 0`, `b₆ = 4b`,
so `Δ = −27·b₆² = −432·b²`.) The route-(a) discriminant view. For `b = 7` this is
`−21168`, matching `secp256k1_Δ_ne_zero`. -/
theorem curveB_Δ {K : Type*} [CommRing K] (b : K) :
    (curveB b).Δ = -(432 * b ^ 2) := by
  simp only [WeierstrassCurve.Δ, WeierstrassCurve.b₂, WeierstrassCurve.b₄,
    WeierstrassCurve.b₆, WeierstrassCurve.b₈, curveB]
  ring

/-- **`curveB b` has `Δ ≠ 0` given `2, 3, b ≠ 0`** — since `Δ = −432·b²` and
`432 = 2⁴·3³`. The discriminant route to smoothness. -/
theorem curveB_Δ_ne_zero {K : Type*} [Field K] {b : K}
    (h2 : (2 : K) ≠ 0) (h3 : (3 : K) ≠ 0) (hb : b ≠ 0) :
    (curveB b).Δ ≠ 0 := by
  rw [curveB_Δ, neg_ne_zero]
  have h432 : (432 : K) = 2 ^ 4 * 3 ^ 3 := by norm_num
  rw [h432]
  exact mul_ne_zero (mul_ne_zero (pow_ne_zero 4 h2) (pow_ne_zero 3 h3))
    (pow_ne_zero 2 hb)

/-! ## The Jacobian criterion (algebraic core) -/

/-- **Jacobian criterion, algebraic core.** For a point `(X, Y, Z) ≠ (0,0,0)` on the
homogeneous cubic `F = Y²Z − X³ − b·Z³`, when `2, 3, b ≠ 0` not all three partials
`∂F/∂X = −3X²`, `∂F/∂Y = 2YZ`, `∂F/∂Z = Y² − 3b·Z²` vanish. Proved directly, splitting
on `Z = 0` (chart ii) vs `Z ≠ 0` (chart i). Pure field algebra. -/
theorem jacobian_core {K : Type*} [Field K] {b X Y Z : K}
    (h2 : (2 : K) ≠ 0) (h3 : (3 : K) ≠ 0) (hb : b ≠ 0)
    (hne : ¬(X = 0 ∧ Y = 0 ∧ Z = 0))
    (hEq : Y ^ 2 * Z - (X ^ 3 + b * Z ^ 3) = 0) :
    -(3 * X ^ 2) ≠ 0 ∨ 2 * Y * Z ≠ 0 ∨ Y ^ 2 - 3 * b * Z ^ 2 ≠ 0 := by
  have powz : ∀ (w : K) (n : ℕ), w ^ n = 0 → w = 0 := by
    intro w n hw
    by_contra hw'
    exact pow_ne_zero n hw' hw
  rcases eq_or_ne Z 0 with hZ | hZ
  · -- Chart (ii): the point-at-infinity locus `Z = 0`. Here `∂F/∂Z = Y² ≠ 0`.
    subst hZ
    have hX0 : X = 0 := powz X 3 (by linear_combination -hEq)
    have hYnz : Y ≠ 0 := fun hY => hne ⟨hX0, hY, rfl⟩
    exact Or.inr (Or.inr fun hc => hYnz (powz Y 2 (by linear_combination hc)))
  · -- Chart (i): the affine chart `Z ≠ 0`. Common zero ⇒ `X = Y = 0` ⇒ `−b·Z³ = 0`.
    by_contra hcon
    push_neg at hcon
    obtain ⟨hX, hY, _hZ'⟩ := hcon
    rw [neg_eq_zero] at hX
    have hX0 : X = 0 := by
      rcases mul_eq_zero.mp hX with h | h
      · exact absurd h h3
      · exact powz X 2 h
    rw [mul_assoc] at hY
    have hY0 : Y = 0 := by
      rcases mul_eq_zero.mp hY with h | h
      · exact absurd h h2
      · rcases mul_eq_zero.mp h with h' | h'
        · exact h'
        · exact absurd h' hZ
    rw [hX0, hY0] at hEq
    have hbz : b * Z ^ 3 = 0 := by linear_combination -hEq
    rcases mul_eq_zero.mp hbz with h | h
    · exact hb h
    · exact hZ (powz Z 3 h)

/-! ## General smoothness in Mathlib's projective vocabulary -/

/-- **General smoothness (projective Jacobian criterion).** Over any field `K` with
`2, 3, b ≠ 0`, every projective point `P = [X:Y:Z] ≠ 0` on `Y²Z = X³ + b·Z³` is
nonsingular (`WeierstrassCurve.Projective.Nonsingular`). The proof rewrites
`Nonsingular` to Mathlib's three `pderiv`-defined partials via `nonsingular_iff`,
then discharges the disjunction with `jacobian_core`. -/
theorem curveB_toProjective_nonsingular {K : Type*} [Field K] {b : K}
    (h2 : (2 : K) ≠ 0) (h3 : (3 : K) ≠ 0) (hb : b ≠ 0)
    {P : Fin 3 → K} (hP : P ≠ 0)
    (hP_eq : (curveB b).toProjective.Equation P) :
    (curveB b).toProjective.Nonsingular P := by
  -- A projective representative has some nonzero coordinate.
  have hne : ¬(P 0 = 0 ∧ P 1 = 0 ∧ P 2 = 0) := by
    rintro ⟨h0, h1, h2'⟩
    apply hP
    funext i
    fin_cases i <;> assumption
  -- The curve equation as a bare polynomial identity in `P 0, P 1, P 2`.
  have hEqPoly : P 1 ^ 2 * P 2 - (P 0 ^ 3 + b * P 2 ^ 3) = 0 := by
    have h := (WeierstrassCurve.Projective.equation_iff P).mp hP_eq
    simp only [curveB] at h
    linear_combination h
  rw [WeierstrassCurve.Projective.nonsingular_iff]
  refine ⟨hP_eq, ?_⟩
  simp only [curveB]
  rcases jacobian_core h2 h3 hb hne hEqPoly with h | h | h
  · exact Or.inl fun hc => h (by linear_combination hc)
  · exact Or.inr (Or.inl fun hc => h (by linear_combination hc))
  · exact Or.inr (Or.inr fun hc => h (by linear_combination hc))

/-! ## Specialization to secp256k1 (`b = 7`, `K = ZMod Secp256k1.p`) -/

/-- secp256k1's projective model is definitionally `curveB 7` over `𝔽_p`. -/
theorem secp256k1_toProjective_eq :
    secp256k1.toProjective = (curveB (7 : ZMod Secp256k1.p)).toProjective := rfl

/-- **secp256k1 is smooth: every projective point on `Y²Z = X³ + 7·Z³` over `𝔽_p` is
nonsingular.** Instantiation of `curveB_toProjective_nonsingular` at `b = 7`, using
`2, 3, 7 ≠ 0` in `𝔽_p` (each via the repository's `ZMod.natCast_eq_zero_iff` / `¬ p∣m`
idiom). Stated under `[Fact p.Prime]` (makes `𝔽_p` a field) — a hypothesis, not an
axiom, per the repo convention. -/
theorem secp256k1_projective_nonsingular [Fact (Nat.Prime Secp256k1.p)]
    {P : Fin 3 → ZMod Secp256k1.p} (hP : P ≠ 0)
    (hP_eq : secp256k1.toProjective.Equation P) :
    secp256k1.toProjective.Nonsingular P := by
  have hchar2 : (2 : ZMod Secp256k1.p) ≠ 0 := by
    have h : ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; decide
    simpa using h
  have hchar3 : (3 : ZMod Secp256k1.p) ≠ 0 := by
    have h : ((3 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; decide
    simpa using h
  have hchar7 : (7 : ZMod Secp256k1.p) ≠ 0 := by
    have h : ((7 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; decide
    simpa using h
  rw [secp256k1_toProjective_eq] at hP_eq ⊢
  exact curveB_toProjective_nonsingular hchar2 hchar3 hchar7 hP hP_eq

/-- **The point at infinity `[0:1:0]` is nonsingular** — chart (ii), where
`∂F/∂Z = Y² = 1 ≠ 0`. Derived from the general theorem (`[0:1:0] ≠ 0`, and it lies on
the curve via `equation_zero`). -/
theorem secp256k1_infinity_nonsingular [Fact (Nat.Prime Secp256k1.p)] :
    secp256k1.toProjective.Nonsingular ![0, 1, 0] := by
  refine secp256k1_projective_nonsingular ?_ ?_
  · intro h
    simpa using congrFun h 1
  · exact WeierstrassCurve.Projective.equation_zero

end Ecdlp.Curve
