/-
# The multiplication-by-3 `y`-coordinate formula for secp256k1 — `y(3•P) = ω₃/ψ₃³`

Companion to `TripleMultiplicationFormula.lean` (the `x`-coordinate `x(3•P) = Φ₃/ΨSq₃`).
The `y`-coordinate of the tripled point, in the same chord–tangent slope parametrisation
`s₂` (`2y·s₂ = 3x²`), `s₃` (secant `2P→P`) of `FiveTorsionBridge`/`TripleMultiplicationFormula`:
```
y(3•P) = s₃·(s₂² − s₃²) − y = ω₃ / ψ₃³,
```
with `ψ₃ = 3x⁴ + 84x` and the `n = 3` `y`-coordinate ("omega") division polynomial
`ω₃ = y·(x¹² + 1540x⁹ − 87024x⁶ − 109760x³ − 1229312)` (bivariate — the `y` factor is the
odd-`n` shape). Extends the `n = 2` `y`-formula (`MultiplicationYFormula.lean`); node S3a of
the N7-uniform build (`BARRIERS.md §B3`; target `n7_uniform_secp256k1_x`).

Mathlib has **no** `ω` division polynomial (open `TODO`). Proof mirrors the `x`-triple: Step A
uses `hℓ3` to clear `s₃` from `(s₃(s₂²−s₃²)−y)·(s₂²−3x)³` into an `s₃`-free expression in `W = −(s₂(s₂²−3x)+2y)`; Step B is the `s₃`-free master identity cleared by `(2y)³`, a certified
`linear_combination` of the slope and curve equations (CAS cofactors, `scripts/certs/`); then
cancel `(s₂²−3x)³ ≠ 0`. No `native_decide`.

**Honest scope.** Fixed `n = 3` coordinate identity; the uniform `y([n]P)=ωₙ/ψₙ³` and the
general bivariate `ωₙ` remain the open target.
-/
import Mathlib
import Ecdlp.Proved.TripleDivisionPolynomial
import Ecdlp.Proved.MultiplicationYFormula

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Multiplication-by-3 `y`-coordinate formula for secp256k1 — `y(3•P) = ω₃/ψ₃³`** (node S3a).
With the chord-tangent slopes `s₂` (`2y·s₂ = 3x²`) and `s₃` (`(s₂²−3x)·s₃ = −(s₂(s₂²−3x)+y)−y`),
the tripled `y`-coordinate `s₃·(s₂²−s₃²)−y` equals `ω₃/(3x⁴+84x)³` with
`ω₃ = y·(x¹²+1540x⁹−87024x⁶−109760x³−1229312)`. -/
theorem secp256k1_triple_y_eq_ω₃
    (x y s2 s3 : ZMod Secp256k1.p)
    (hy : y ≠ 0)
    (hcurve : y ^ 2 = x ^ 3 + 7)
    (hΨ3 : 3 * x ^ 4 + 84 * x ≠ 0)
    (hd : s2 ^ 2 - 3 * x ≠ 0)
    (hsl2 : 2 * y * s2 = 3 * x ^ 2)
    (hℓ3 : (s2 ^ 2 - 3 * x) * s3 = -(s2 * (s2 ^ 2 - 3 * x) + y) - y) :
    s3 * (s2 ^ 2 - s3 ^ 2) - y
      = (y * (x ^ 12 + 1540 * x ^ 9 - 87024 * x ^ 6 - 109760 * x ^ 3 - 1229312)) / (3 * x ^ 4 + 84 * x) ^ 3 := by
  have h2 : (2 : ZMod Secp256k1.p) ≠ 0 := by
    have hnd : ¬ Secp256k1.p ∣ 2 := by decide
    have h2n : ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; exact hnd
    simpa using h2n
  have hden : ((3 * x ^ 4 + 84 * x) ^ 3 : ZMod Secp256k1.p) ≠ 0 := pow_ne_zero 3 hΨ3
  have hd3 : (((s2 ^ 2 - 3 * x) ^ 3) : ZMod Secp256k1.p) ≠ 0 := pow_ne_zero 3 hd
  have h2y3 : (((2 * y) ^ 3) : ZMod Secp256k1.p) ≠ 0 := pow_ne_zero 3 (mul_ne_zero h2 hy)
  rw [eq_div_iff hden]
  -- Step A: clear `s₃` using `hℓ3`.
  have hStepA : (s3 * (s2 ^ 2 - s3 ^ 2) - y) * (s2 ^ 2 - 3 * x) ^ 3
      = s2 ^ 2 * (s2 ^ 2 - 3 * x) ^ 2 * (-(s2 * (s2 ^ 2 - 3 * x) + 2 * y)) - (-(s2 * (s2 ^ 2 - 3 * x) + 2 * y)) ^ 3 - y * (s2 ^ 2 - 3 * x) ^ 3 := by
    linear_combination (-4*s2^3*y + 12*s2*x*y + s3^2*(-s2^4 + 6*s2^2*x - 9*x^2) + s3*(s2^5 - 6*s2^3*x + 2*s2^2*y + 9*s2*x^2 - 6*x*y) - 4*y^2) * hℓ3
  -- Step B: the `s₃`-free master identity, cleared by `(2y)³`.
  have hStepB : (s2 ^ 2 * (s2 ^ 2 - 3 * x) ^ 2 * (-(s2 * (s2 ^ 2 - 3 * x) + 2 * y)) - (-(s2 * (s2 ^ 2 - 3 * x) + 2 * y)) ^ 3 - y * (s2 ^ 2 - 3 * x) ^ 3) * (3 * x ^ 4 + 84 * x) ^ 3
      = (y * (x ^ 12 + 1540 * x ^ 9 - 87024 * x ^ 6 - 109760 * x ^ 3 - 1229312)) * (s2 ^ 2 - 3 * x) ^ 3 := by
    have hcleared : (((s2 ^ 2 * (s2 ^ 2 - 3 * x) ^ 2 * (-(s2 * (s2 ^ 2 - 3 * x) + 2 * y)) - (-(s2 * (s2 ^ 2 - 3 * x) + 2 * y)) ^ 3 - y * (s2 ^ 2 - 3 * x) ^ 3) * (3 * x ^ 4 + 84 * x) ^ 3 - (y * (x ^ 12 + 1540 * x ^ 9 - 87024 * x ^ 6 - 109760 * x ^ 3 - 1229312)) * (s2 ^ 2 - 3 * x) ^ 3) * (2 * y) ^ 3) = 0 := by
      linear_combination (320*s2^5*x^12*y^3 + 21056*s2^5*x^9*y^3 + 1110144*s2^5*x^6*y^3 + 7551488*s2^5*x^3*y^3 + 4917248*s2^5*y^3 + 480*s2^4*x^14*y^2 + 31584*s2^4*x^11*y^2 + 1665216*s2^4*x^8*y^2 + 11327232*s2^4*x^5*y^2 + 7375872*s2^4*x^2*y^2 + 720*s2^3*x^16*y - 1584*s2^3*x^13*y^3 + 47376*s2^3*x^13*y - 80640*s2^3*x^10*y^3 + 2497824*s2^3*x^10*y - 6943104*s2^3*x^7*y^3 + 16990848*s2^3*x^7*y - 39513600*s2^3*x^4*y^3 + 11063808*s2^3*x^4*y - 44255232*s2^3*x*y^3 + 1080*s2^2*x^18 - 2376*s2^2*x^15*y^2 + 71064*s2^2*x^15 + 1296*s2^2*x^12*y^4 - 120960*s2^2*x^12*y^2 + 3746736*s2^2*x^12 + 108864*s2^2*x^9*y^4 - 10414656*s2^2*x^9*y^2 + 25486272*s2^2*x^9 + 3048192*s2^2*x^6*y^4 - 59270400*s2^2*x^6*y^2 + 16595712*s2^2*x^6 + 28449792*s2^2*x^3*y^4 - 66382848*s2^2*x^3*y^2 - 1944*s2*x^17*y + 2808*s2*x^14*y^3 - 86184*s2*x^14*y + 78624*s2*x^11*y^3 - 10668672*s2*x^11*y + 16257024*s2*x^8*y^3 - 85349376*s2*x^8*y + 75866112*s2*x^5*y^3 - 99574272*s2*x^5*y + 132765696*s2*x^2*y^3 - 2916*x^19 + 4212*x^16*y^2 - 129276*x^16 - 3888*x^13*y^4 + 117936*x^13*y^2 - 16003008*x^13 - 326592*x^10*y^4 + 24385536*x^10*y^2 - 128024064*x^10 - 9144576*x^7*y^4 + 113799168*x^7*y^2 - 149361408*x^7 - 85349376*x^4*y^4 + 199148544*x^4*y^2) * hsl2 + (-3240*s2^2*x^17 - 190512*s2^2*x^14 - 9906624*s2^2*x^11 - 7112448*s2^2*x^8 + 8748*x^18 - 3888*x^15*y^2 + 326592*x^15 + 1728*x^12*y^4 + 45722880*x^12 + 145152*x^9*y^4 - 27433728*x^9*y^2 + 64012032*x^9 + 4064256*x^6*y^4 - 85349376*x^6*y^2 + 37933056*x^3*y^4) * hcurve
    have hz := (mul_eq_zero.mp hcleared).resolve_right h2y3
    linear_combination hz
  -- Combine and cancel `(s₂²−3x)³`.
  have hfinal : (s3 * (s2 ^ 2 - s3 ^ 2) - y) * (3 * x ^ 4 + 84 * x) ^ 3 * (s2 ^ 2 - 3 * x) ^ 3
      = (y * (x ^ 12 + 1540 * x ^ 9 - 87024 * x ^ 6 - 109760 * x ^ 3 - 1229312)) * (s2 ^ 2 - 3 * x) ^ 3 := by
    calc (s3 * (s2 ^ 2 - s3 ^ 2) - y) * (3 * x ^ 4 + 84 * x) ^ 3 * (s2 ^ 2 - 3 * x) ^ 3
        = ((s3 * (s2 ^ 2 - s3 ^ 2) - y) * (s2 ^ 2 - 3 * x) ^ 3) * (3 * x ^ 4 + 84 * x) ^ 3 := by ring
      _ = (s2 ^ 2 * (s2 ^ 2 - 3 * x) ^ 2 * (-(s2 * (s2 ^ 2 - 3 * x) + 2 * y)) - (-(s2 * (s2 ^ 2 - 3 * x) + 2 * y)) ^ 3 - y * (s2 ^ 2 - 3 * x) ^ 3) * (3 * x ^ 4 + 84 * x) ^ 3 := by rw [hStepA]
      _ = (y * (x ^ 12 + 1540 * x ^ 9 - 87024 * x ^ 6 - 109760 * x ^ 3 - 1229312)) * (s2 ^ 2 - 3 * x) ^ 3 := hStepB
  exact mul_right_cancel₀ hd3 hfinal

end Ecdlp.Curve
