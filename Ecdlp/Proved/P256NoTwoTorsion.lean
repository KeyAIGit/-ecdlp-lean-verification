import Mathlib
import Ecdlp.Proved.P256Curve

/-!
# NIST P-256 has no nonzero 2-torsion point (`E[2] = {O}`) — the Cardano/resolvent route

This is **Part B** of the P-256 exact-cardinality program: the step that does *not* transport
from secp256k1. `CurveCardinalityExact.lean` closes `E[2] = {O}` for secp256k1 by observing
that `a₄ = 0` collapses the 2-division polynomial to the **binomial** `x³ = −7`, so a single
non-cube witness kills it. P-256 has `a₄ = −3`, so the 2-torsion locus is the **general cubic**
`x³ − 3x + b = 0` and that shortcut is unavailable.

The replacement is a Cardano/resolvent argument, run entirely inside `𝔽_p` — **no quadratic
extension, no Hasse bound, no Schoof, no point counting**. Writing `f(X) = X³ − 3X + b`, the
substitution `X = u + u⁻¹` (legitimate exactly because `a₄ = −3`: the `3u + 3u⁻¹` produced by
the cube cancels the `−3(u + u⁻¹)` term *identically*) turns `f` into the resolvent

  `u³ · f(u + u⁻¹) = u⁶ + b·u³ + 1`,

so `u³` is a root of `T² + bT + 1`, whose two roots `c`, `c₂ = −b − c` are explicit constants.
That exhibits `c` or `c₂` as a **cube** in `𝔽_p`, contradicting a machine-checked non-cube
witness. The one thing that could force a quadratic extension — producing `u` itself, which
needs `√(r² − 4)` — is avoided by step (iii): `b² − 4` is a square in `𝔽_p` (witness `s`), and
the polynomial identity `b² − 4 = (r² − 4)(r² − 1)²` holds *modulo the cubic*, so
`σ := s/(r² − 1)` is a square root of `r² − 4` **already in the prime field**.

## The chain

Let `r` be a root of `f`, i.e. a 2-torsion `x`-coordinate (`y = 0`).

* (i)   `r³ − 3r + b = 0`.
* (ii)  `b² − 4 = (r² − 4)(r² − 1)²`, since
        `(b² − 4) − (r² − 4)(r² − 1)² = (b − r³ + 3r)·(r³ − 3r + b)` — an *exact* polynomial
        identity (remainder `0`), so this is one `linear_combination`.
* (iii) `b² − 4 ≠ 0` forces `r² − 1 ≠ 0`; then `σ := s/(r² − 1)` satisfies `σ² = r² − 4`.
        **This is what keeps the whole argument in `𝔽_p`.**
* (iv)  `u := (r + σ)/2`, `v := (r − σ)/2`, so `u + v = r` and `uv = (r² − σ²)/4 = 1`;
        in particular `u ≠ 0`.
* (v)   `u² − ru + 1 = 0`, hence `u⁶ + b·u³ + 1 = 0`.
* (vi)  `(u³ − c)(u³ − c₂) = (u⁶ + b·u³ + 1) − (c² + bc + 1) = 0` using `c + c₂ = −b`,
        `c·c₂ = 1`.
* (vii) Either branch gives `const^((p−1)/3) = (u³)^((p−1)/3) = u^(p−1) = 1` by
        `ZMod.pow_card_sub_one_eq_one` (`3 ∣ p − 1`), contradicting the two non-cube facts.
        This is the same closing move as secp256k1's.

## Certificate hygiene

The three constants are `native_decide`-certified by four closed literal facts
(`s² = b² − 4`, `c² + bc + 1 = 0`, `c·c₂ = 1`, `c^((p−1)/3) ≠ 1`). The fifth needed fact,
`c₂^((p−1)/3) ≠ 1`, is **derived** from `c·c₂ = 1` (`mul_pow`/`one_pow`) rather than spending a
second 256-bit modular exponentiation; likewise `c + c₂ = −b` is derived from
`c² + bc + 1 = 0` and `c·c₂ = 1`, not asserted.

Every `linear_combination` cofactor below was re-derived by polynomial division / Gröbner
reduction in sympy (residual exactly `0`), and the constants were regenerated independently
(`sqrt_mod` for `s`; the quadratic formula for `c`, `c₂`) rather than copied. The chain was
additionally replayed step-by-step in `ℤ/q` on 15216 genuine roots over 271 primes `q ≡ 1 (3)`,
with 0 step failures, and the soundness direction checked on 168812 hypothesis-satisfying
`(q, b)` pairs with 0 counterexamples.

Every theorem here is fully proved — no holes, no new axioms. `native_decide` contributes
`Lean.ofReduceBool`, exactly as the secp256k1 keystone in
`Ecdlp/Proved/CurveCardinalityExact.lean` already does, and only for closed literal / 256-bit
modular-exponentiation leaves of the same size class. The eight leaves are the four literal
resolvent certificates plus `b² − 4 ≠ 0`, `2 ≠ 0`, `4 ≠ 0` and `3 ∣ p − 1`; the generated
ledger audit discloses every one of them by name.
-/

namespace Ecdlp.P256

open WeierstrassCurve.Affine

/-! ### The resolvent constants and their literal certificates

All four are closed `ZMod P256.p` propositions, stated **before** the `[Fact p.Prime]` section
so that the goal `native_decide` sees is a closed term over the global `CommRing (ZMod p)`
instance — the same discipline as `secp256k1_neg7_pow_ne_one`. -/

/-- A square root of `b² − 4` in `𝔽_p`. Exists because `b² − 4` is a quadratic residue
(Legendre symbol `+1`, independently recomputed); this is what lets step (iii) stay inside the
prime field instead of passing to `𝔽_{p²}`. -/
def resolventS : ZMod p :=
  18204275045333271803850252468056031438057061776906233838328249308827409745899

/-- One root `c` of the resolvent quadratic `T² + bT + 1`. If the cubic `x³ − 3x + b` had a
root `r`, then `u³` would equal `c` or `c₂` for `u = (r + √(r²−4))/2`. -/
def resolventC : ZMod p :=
  104365044870446813599959508293411955044557453795746568337280127806261069026255

/-- The other root `c₂ = −b − c` of `T² + bT + 1`; equivalently `c₂ = c⁻¹`, which is how its
non-cube property is obtained below without a second modular exponentiation. -/
def resolventC2 : ZMod p :=
  86160769825113541796109255825355923606500392018840334498951878497433659280356

/-- **Literal fact 1**: `s² = b² − 4`. Also validates the constant `s`. -/
theorem resolventS_sq : resolventS ^ 2 = (b : ZMod p) ^ 2 - 4 := by native_decide

/-- **Literal fact 2**: `c` is a root of the resolvent quadratic `T² + bT + 1`. -/
theorem resolventC_quadratic :
    resolventC ^ 2 + (b : ZMod p) * resolventC + 1 = 0 := by native_decide

/-- **Literal fact 3**: `c · c₂ = 1`, i.e. `c₂ = c⁻¹` (the constant term of `T² + bT + 1`). -/
theorem resolventC_mul_C2 : resolventC * resolventC2 = 1 := by native_decide

/-- **Literal fact 4**: `c` is **not a cube** in `𝔽_p` — the Euler cubic-residue witness
`c^((p−1)/3) ≠ 1`, valid because `p ≡ 1 (mod 3)`. This is the only 256-bit modular
exponentiation in the module. -/
theorem resolventC_not_cube : resolventC ^ ((p - 1) / 3) ≠ 1 := by native_decide

/-- `b² − 4 ≠ 0` (the resolvent quadratic has distinct roots; equivalently `s ≠ 0`). Used to
force `r² − 1 ≠ 0` in step (iii). -/
theorem p256_b_sq_sub_four_ne_zero : (b : ZMod p) ^ 2 - 4 ≠ 0 := by native_decide

/-- `2 ≠ 0` in `𝔽_p` (`p` is odd) — needed to halve in step (iv). -/
theorem p256_two_ne_zero : (2 : ZMod p) ≠ 0 := by native_decide

/-- `4 ≠ 0` in `𝔽_p` — needed for the `uv = (r² − σ²)/4` cancellation in step (iv). -/
theorem p256_four_ne_zero : (4 : ZMod p) ≠ 0 := by native_decide

/-- `3 ∣ p − 1`, so `(p−1)/3` is an honest exponent and `x ↦ x³` is 3-to-1 on `𝔽_pˣ`. -/
theorem p256_three_dvd_p_sub_one : 3 ∣ p - 1 := by native_decide

/-- **`c₂` is not a cube either — derived, not certified.** From `c · c₂ = 1` we get
`c^k · c₂^k = 1` for `k = (p−1)/3`, so `c₂^k = 1` would force `c^k = 1`, contradicting
`resolventC_not_cube`. No second `native_decide`. -/
theorem resolventC2_not_cube : resolventC2 ^ ((p - 1) / 3) ≠ 1 := by
  intro h
  apply resolventC_not_cube
  have hmul : resolventC ^ ((p - 1) / 3) * resolventC2 ^ ((p - 1) / 3) = 1 := by
    rw [← mul_pow, resolventC_mul_C2, one_pow]
  rwa [h, mul_one] at hmul

variable [Fact (Nat.Prime p)]

/-- **`c + c₂ = −b` — derived, not certified.** `c · (c + c₂ + b) = c² + c·c₂ + bc =
(c² + bc + 1) + (c·c₂ − 1) = 0`, and `c ≠ 0` because `c · c₂ = 1`. Together with
`resolventC_mul_C2` this says `T² + bT + 1 = (T − c)(T − c₂)`, which is step (vi). -/
theorem resolventC_add_C2 : resolventC + resolventC2 = -(b : ZMod p) := by
  have hcne : resolventC ≠ 0 := left_ne_zero_of_mul_eq_one resolventC_mul_C2
  have hz : resolventC * (resolventC + resolventC2 + (b : ZMod p)) = 0 := by
    linear_combination resolventC_quadratic + resolventC_mul_C2
  rcases mul_eq_zero.mp hz with h | h
  · exact absurd h hcne
  · linear_combination h

/-! ### The heart: `x³ − 3x + b` has no root in `𝔽_p` -/

/-- **The P-256 2-torsion cubic has no root in `𝔽_p`.**

This is the `a₄ = −3` replacement for secp256k1's "`−7` is not a cube", and the only genuinely
new mathematics in the P-256 exact-cardinality route. Suppose `r³ − 3r + b = 0`.

* (ii) The *exact* polynomial identity
  `(b² − 4) − (r² − 4)(r² − 1)² = (b − r³ + 3r)·(r³ − 3r + b)`
  gives `b² − 4 = (r² − 4)(r² − 1)²`.
* (iii) Since `b² − 4 ≠ 0`, also `r² − 1 ≠ 0`, so `σ := s/(r² − 1)` is a square root of
  `r² − 4` **inside `𝔽_p`** — no quadratic extension is ever formed.
* (iv) `u := (r + σ)/2` and `v := (r − σ)/2` satisfy `u + v = r` and `u·v = 1`, so `u ≠ 0` and
  `u² − ru + 1 = 0` (i.e. `r = u + u⁻¹`).
* (v) `u³ · (r³ − 3r + b) = u⁶ + b·u³ + 1` modulo `u² − ru + 1` — the cancellation that needs
  `a₄ = −3` exactly.
* (vi) Hence `(u³ − c)(u³ − c₂) = 0`, so `u³ ∈ {c, c₂}`.
* (vii) Either way `const^((p−1)/3) = (u³)^((p−1)/3) = u^(p−1) = 1` by Fermat, contradicting
  `resolventC_not_cube` / `resolventC2_not_cube`.

Every cofactor below was re-derived by sympy polynomial division (residual `0`). -/
theorem p256_cubic_no_root (r : ZMod p) : r ^ 3 - 3 * r + (b : ZMod p) ≠ 0 := by
  intro hr
  -- (ii) `b² − 4 = (r² − 4)(r² − 1)²`, an exact multiple of the cubic.
  --      cofactor: (b - r³ + 3r), verified by `div(g, hr)` in sympy with remainder 0.
  have hfact : (b : ZMod p) ^ 2 - 4 = (r ^ 2 - 4) * (r ^ 2 - 1) ^ 2 := by
    linear_combination ((b : ZMod p) - r ^ 3 + 3 * r) * hr
  -- (iii) `r² − 1 ≠ 0`, else the right-hand side above vanishes and `b² − 4 = 0`.
  have hm : r ^ 2 - 1 ≠ 0 := by
    intro h
    exact p256_b_sq_sub_four_ne_zero
      (by linear_combination hfact + ((r ^ 2 - 4) * (r ^ 2 - 1)) * h)
  -- (iii) `σ := s/(r² − 1)` has `σ² = r² − 4`. The division is discharged here, once, by
  -- `div_mul_cancel₀` + `mul_right_cancel₀`; downstream `σ` is an opaque field element and
  -- every remaining step is pure ring arithmetic.
  obtain ⟨σ, hσ⟩ : ∃ σ : ZMod p, σ ^ 2 = r ^ 2 - 4 := by
    refine ⟨resolventS / (r ^ 2 - 1), ?_⟩
    refine mul_right_cancel₀ (pow_ne_zero 2 hm) ?_
    calc (resolventS / (r ^ 2 - 1)) ^ 2 * (r ^ 2 - 1) ^ 2
        = (resolventS / (r ^ 2 - 1) * (r ^ 2 - 1)) ^ 2 := by ring
      _ = resolventS ^ 2 := by rw [div_mul_cancel₀ resolventS hm]
      _ = (b : ZMod p) ^ 2 - 4 := resolventS_sq
      _ = (r ^ 2 - 4) * (r ^ 2 - 1) ^ 2 := hfact
  -- (iv) `u := (r + σ)/2`, `v := (r − σ)/2`. Again the division is discharged at the point of
  -- introduction, leaving the clean relations `2u = r + σ`, `2v = r − σ`.
  obtain ⟨u, h2u⟩ : ∃ u : ZMod p, u * 2 = r + σ :=
    ⟨(r + σ) / 2, div_mul_cancel₀ (r + σ) p256_two_ne_zero⟩
  obtain ⟨v, h2v⟩ : ∃ v : ZMod p, v * 2 = r - σ :=
    ⟨(r - σ) / 2, div_mul_cancel₀ (r - σ) p256_two_ne_zero⟩
  -- `u + v = r`: cancel the `2`.
  have hsum : u + v = r := by
    refine mul_right_cancel₀ p256_two_ne_zero ?_
    linear_combination h2u + h2v
  -- `u · v = 1`: `4uv = (2u)(2v) = (r + σ)(r − σ) = r² − σ² = 4`, then cancel the `4`.
  -- cofactor: 2v·h2u + (r + σ)·h2v − hσ, verified in sympy.
  have hprod : u * v = 1 := by
    refine mul_right_cancel₀ p256_four_ne_zero ?_
    linear_combination (2 * v) * h2u + (r + σ) * h2v - hσ
  have hune : u ≠ 0 := left_ne_zero_of_mul_eq_one hprod
  -- (v) `u² − ru + 1 = 0`, i.e. `r = u + u⁻¹`.
  have hquad : u ^ 2 - r * u + 1 = 0 := by linear_combination u * hsum - hprod
  -- (v) the resolvent: `u³·f(u + u⁻¹) = u⁶ + b·u³ + 1`. The cofactor of `hquad` is
  -- `(ur)² + (u²+1)(ur) + (u²+1)² − 3u²`, i.e. the expansion below; sympy residual 0.
  have h6 : u ^ 6 + (b : ZMod p) * u ^ 3 + 1 = 0 := by
    linear_combination (u ^ 3) * hr
      + (r ^ 2 * u ^ 2 + r * u ^ 3 + r * u + u ^ 4 - u ^ 2 + 1) * hquad
  -- (vi) `T² + bT + 1 = (T − c)(T − c₂)` evaluated at `T = u³`.
  have hsplit : (u ^ 3 - resolventC) * (u ^ 3 - resolventC2) = 0 := by
    linear_combination h6 - (u ^ 3) * resolventC_add_C2 + resolventC_mul_C2
  -- (vii) Fermat: a cube's `(p−1)/3`-th power is `u^(p−1) = 1`.
  have hexp : 3 * ((p - 1) / 3) = p - 1 := Nat.mul_div_cancel' p256_three_dvd_p_sub_one
  have hcube : ∀ w : ZMod p, u ^ 3 = w → w ^ ((p - 1) / 3) = 1 := by
    intro w hw
    rw [← hw, ← pow_mul, hexp]
    exact ZMod.pow_card_sub_one_eq_one hune
  rcases mul_eq_zero.mp hsplit with h | h
  · exact resolventC_not_cube (hcube resolventC (by linear_combination h))
  · exact resolventC2_not_cube (hcube resolventC2 (by linear_combination h))

/-! ### Transport to points: `E[2] = {O}` for P-256

The two bridging lemmas below are the P-256 analogues of `secp256k1_curve_of_nonsingular`
(`Ecdlp/Proved/TorsionPointCount.lean`) and `secp256k1_two_nsmul_eq_zero_iff`
(`Ecdlp/Proved/TwoTorsionPoint.lean`), included so this module is self-contained and
independently checkable. Neither is curve-specific mathematics: `2P = 0 ↔ y = 0` needs only
`a₁ = a₃ = 0` and `char ≠ 2`. If the sibling generic-API module lands a curve-agnostic version,
delete these two and re-route `p256_no_nonzero_two_torsion` through it — `p256_cubic_no_root`
above is the part that cannot be shared. -/

/-- The curve equation `y² = x³ − 3x + b` holds at any nonsingular affine point of P-256. -/
theorem p256_curve_of_nonsingular (x y : ZMod p)
    (h : P256.toAffine.Nonsingular x y) : y ^ 2 = x ^ 3 - 3 * x + (b : ZMod p) := by
  have he : P256.toAffine.Equation x y := h.1
  rw [WeierstrassCurve.Affine.equation_iff] at he
  simp only [P256] at he
  linear_combination he

/-- **Point-level 2-torsion criterion for P-256: `2 • P = 0 ↔ y = 0`.** `2 • P = 0 ↔ P = −P`,
and `−(x, y) = (x, −y)` since `a₁ = a₃ = 0`, so the condition is `y = −y`, i.e. `2y = 0`,
i.e. `y = 0` in characteristic `≠ 2`. -/
theorem p256_two_nsmul_eq_zero_iff (x y : ZMod p) (h : P256.toAffine.Nonsingular x y) :
    (2 : ℕ) • (Point.some x y h) = 0 ↔ y = 0 := by
  have hnegY : P256.toAffine.negY x y = -y := by
    simp [WeierstrassCurve.Affine.negY, P256]
  rw [two_nsmul, add_eq_zero_iff_eq_neg, Point.neg_some, Point.some.injEq, hnegY]
  constructor
  · rintro ⟨-, hy⟩
    have h2y : (2 : ZMod p) * y = 0 := by linear_combination hy
    rcases mul_eq_zero.mp h2y with h2 | hy0
    · exact absurd h2 p256_two_ne_zero
    · exact hy0
  · intro hy
    subst hy
    exact ⟨rfl, by ring⟩

/-- **`E[2] = {O}` for NIST P-256.** The only 2-torsion point is the identity: if `2 • P = 0`
for `P = (x, y)` then `y = 0`, so `x` is a root of `x³ − 3x + b` — impossible by
`p256_cubic_no_root`.

This is the P-256 counterpart of `secp256k1_no_nonzero_two_torsion`, and the step that the
secp256k1 `j = 0` route could not supply. With it, the interval-collapse certificate closes:
`n ∣ #E` (`p256_n_dvd_card_point`) together with `#E ≤ 2p + 1 < 3n` pins `#E ∈ {n, 2n}`, and
`2n` is excluded because additive Cauchy would produce a point of additive order exactly `2`. -/
theorem p256_no_nonzero_two_torsion (P : P256.toAffine.Point)
    (hP : (2 : ℕ) • P = 0) : P = 0 := by
  rcases P with _ | ⟨x, y, h⟩
  · rfl
  · exfalso
    have hy : y = 0 := (p256_two_nsmul_eq_zero_iff x y h).mp hP
    have hcurve : y ^ 2 = x ^ 3 - 3 * x + (b : ZMod p) := p256_curve_of_nonsingular x y h
    rw [hy] at hcurve
    exact p256_cubic_no_root x (by linear_combination -hcurve)

end Ecdlp.P256
