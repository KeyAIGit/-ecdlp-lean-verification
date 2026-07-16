import Mathlib
import Ecdlp.Proved.TripleDivisionPolynomial
import Ecdlp.Proved.MultiplicationFormula

/-!
# The multiplication-by-3 `x`-coordinate formula for secp256k1 — `x(3•P) = Φ₃/ΨSq₃`

Node **N7@3** of the `ψₙ ↔ E[n]` bridge (`notes/DIVISION_POLY_TORSION_MAP.md`): the point-level
tripling formula connecting Mathlib's division polynomials `Φ₃`/`ΨSq₃` (recorded concretely in
`TripleDivisionPolynomial.lean`) to the actual elliptic-curve group law, extending the base case
`n = 2` in `MultiplicationFormula.lean`.

For a point `P = (x,y)` on `y² = x³ + 7` with `y ≠ 0` (not 2-torsion, tangent defined),
`Ψ₃(x) = 3x⁴+84x ≠ 0` (not 3-torsion, so `3•P ≠ O` and the denominator is nonzero), and the
chord-tangent slopes `s₂` (doubling: `2y·s₂ = 3x²`) and `s₃` (secant `2P→P`) — exactly the
parametrisation of `FiveTorsionBridge.lean` — the `x`-coordinate of `3•P`,
`s₃² − (s₂²−2x) − x`, equals `Φ₃(x)/ΨSq₃(x)`.

Proof (mirroring `five_core`): squaring the secant relation `hℓ3` clears `s₃` into
`(s₂²−3x)·s₃ = W` where `W = −(s₂(s₂²−3x)+y)−y`, giving the `s₃`-free master identity
`(W² − ((s₂²−2x)+x)(s₂²−3x)²)·ΨSq₃ = Φ₃·(s₂²−3x)²`, which is a `linear_combination` of the
slope relation and the curve equation after clearing `(2y)⁴` (both `(s₂²−3x)²` and `(2y)⁴`
nonzero). The certificate cofactors are CAS-derived (`scripts/certs/`); the Lean kernel checks
the `ring` identity. No `native_decide`.
-/

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Multiplication-by-3 `x`-coordinate formula for secp256k1 — `x(3•P) = Φ₃(x)/ΨSq₃(x)`**
(node N7@3). With the chord-tangent slopes `s₂` (`2y·s₂ = 3x²`) and `s₃`
(`(s₂²−3x)·s₃ = −(s₂(s₂²−3x)+y)−y`) of `FiveTorsionBridge`, the tripled `x`-coordinate
`s₃² − (s₂²−2x) − x` equals `(Φ 3)(x)/(ΨSq 3)(x)` in Mathlib's canonical division polynomials. -/
theorem secp256k1_triple_x_eq_Φ₃_div_ΨSq₃
    (x y s2 s3 : ZMod Secp256k1.p)
    (hy : y ≠ 0)
    (hcurve : y ^ 2 = x ^ 3 + 7)
    (hΨ3 : 3 * x ^ 4 + 84 * x ≠ 0)
    (hd : s2 ^ 2 - 3 * x ≠ 0)
    (hsl2 : 2 * y * s2 = 3 * x ^ 2)
    (hℓ3 : (s2 ^ 2 - 3 * x) * s3 = -(s2 * (s2 ^ 2 - 3 * x) + y) - y) :
    s3 ^ 2 - (s2 ^ 2 - 2 * x) - x
      = (secp256k1.Φ 3).eval x / (secp256k1.ΨSq 3).eval x := by
  rw [secp256k1_Φ₃_eval, secp256k1_ΨSq₃_eval]
  have h2 : (2 : ZMod Secp256k1.p) ≠ 0 := by
    have hnd : ¬ Secp256k1.p ∣ 2 := by decide
    have h2n : ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; exact hnd
    simpa using h2n
  have hden_ne : (9 * x ^ 8 + 504 * x ^ 5 + 7056 * x ^ 2 : ZMod Secp256k1.p) ≠ 0 := by
    have heq : (9 * x ^ 8 + 504 * x ^ 5 + 7056 * x ^ 2 : ZMod Secp256k1.p)
        = (3 * x ^ 4 + 84 * x) ^ 2 := by ring
    rw [heq]; exact pow_ne_zero 2 hΨ3
  rw [eq_div_iff hden_ne]
  have hd2 : (s2 ^ 2 - 3 * x) ^ 2 ≠ 0 := pow_ne_zero 2 hd
  have h2y4 : ((2 * y) ^ 4 : ZMod Secp256k1.p) ≠ 0 := pow_ne_zero 4 (mul_ne_zero h2 hy)
  -- Step A: square `hℓ3` to clear `s₃` (`(s₂²−3x)·s₃ = W`).
  have hstepA : (s3 ^ 2 - (s2 ^ 2 - 2 * x) - x) * (s2 ^ 2 - 3 * x) ^ 2
      = (-(s2 * (s2 ^ 2 - 3 * x) + y) - y) ^ 2 - ((s2 ^ 2 - 2 * x) + x) * (s2 ^ 2 - 3 * x) ^ 2 := by
    linear_combination ((s2 ^ 2 - 3 * x) * s3 + (-(s2 * (s2 ^ 2 - 3 * x) + y) - y)) * hℓ3
  -- Step B: the `s₃`-free master identity, cleared by `(2y)⁴`.
  have hstepB : ((-(s2 * (s2 ^ 2 - 3 * x) + y) - y) ^ 2 - ((s2 ^ 2 - 2 * x) + x) * (s2 ^ 2 - 3 * x) ^ 2)
        * (9 * x ^ 8 + 504 * x ^ 5 + 7056 * x ^ 2)
      = (x ^ 9 - 672 * x ^ 6 + 2352 * x ^ 3 + 21952) * (s2 ^ 2 - 3 * x) ^ 2 := by
    have hcleared : (((-(s2 * (s2 ^ 2 - 3 * x) + y) - y) ^ 2 - ((s2 ^ 2 - 2 * x) + x) * (s2 ^ 2 - 3 * x) ^ 2)
          * (9 * x ^ 8 + 504 * x ^ 5 + 7056 * x ^ 2)
        - (x ^ 9 - 672 * x ^ 6 + 2352 * x ^ 3 + 21952) * (s2 ^ 2 - 3 * x) ^ 2)
          * (2 * y) ^ 4 = 0 := by
      linear_combination
        (64*s2^3*x^9*y^3 + 9408*s2^3*x^6*y^3 + 37632*s2^3*x^3*y^3 - 175616*s2^3*y^3 + 96*s2^2*x^11*y^2 + 288*s2^2*x^8*y^4 + 14112*s2^2*x^8*y^2 + 16128*s2^2*x^5*y^4 + 56448*s2^2*x^5*y^2 + 225792*s2^2*x^2*y^4 - 263424*s2^2*x^2*y^2 + 144*s2*x^13*y + 48*s2*x^10*y^3 + 21168*s2*x^10*y - 32256*s2*x^7*y^3 + 84672*s2*x^7*y + 112896*s2*x^4*y^3 - 395136*s2*x^4*y + 1053696*s2*x*y^3 + 216*x^15 + 72*x^12*y^2 + 31752*x^12 - 864*x^9*y^4 - 48384*x^9*y^2 + 127008*x^9 - 48384*x^6*y^4 + 169344*x^6*y^2 - 592704*x^6 - 677376*x^3*y^4 + 1580544*x^3*y^2) * hsl2
        + (-648*x^14 - 864*x^11*y^2 - 90720*x^11 + 576*x^8*y^4 + 60480*x^8*y^2 + 254016*x^8 + 32256*x^5*y^4 - 677376*x^5*y^2 + 451584*x^2*y^4) * hcurve
    have hz := (mul_eq_zero.mp hcleared).resolve_right h2y4
    linear_combination hz
  -- Combine: `X3·ΨSq₃·d² = Φ₃·d²`, then cancel `d² ≠ 0`.
  have hfinal : (s3 ^ 2 - (s2 ^ 2 - 2 * x) - x) * (9 * x ^ 8 + 504 * x ^ 5 + 7056 * x ^ 2)
        * (s2 ^ 2 - 3 * x) ^ 2
      = (x ^ 9 - 672 * x ^ 6 + 2352 * x ^ 3 + 21952) * (s2 ^ 2 - 3 * x) ^ 2 := by
    calc (s3 ^ 2 - (s2 ^ 2 - 2 * x) - x) * (9 * x ^ 8 + 504 * x ^ 5 + 7056 * x ^ 2)
            * (s2 ^ 2 - 3 * x) ^ 2
        = ((s3 ^ 2 - (s2 ^ 2 - 2 * x) - x) * (s2 ^ 2 - 3 * x) ^ 2)
            * (9 * x ^ 8 + 504 * x ^ 5 + 7056 * x ^ 2) := by ring
      _ = ((-(s2 * (s2 ^ 2 - 3 * x) + y) - y) ^ 2 - ((s2 ^ 2 - 2 * x) + x) * (s2 ^ 2 - 3 * x) ^ 2)
            * (9 * x ^ 8 + 504 * x ^ 5 + 7056 * x ^ 2) := by rw [hstepA]
      _ = (x ^ 9 - 672 * x ^ 6 + 2352 * x ^ 3 + 21952) * (s2 ^ 2 - 3 * x) ^ 2 := hstepB
  exact mul_right_cancel₀ hd2 hfinal

end Ecdlp.Curve
