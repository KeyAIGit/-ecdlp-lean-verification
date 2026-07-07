import Mathlib

/-!
# NIST P-256 as a Mathlib elliptic curve

Demonstrates that the grounding built for secp256k1 (`Secp256k1Curve.lean`) is **curve-agnostic**:
the same machinery makes NIST **P-256** (`secp256r1`, `y² = x³ − 3x + b` over `𝔽_p`,
`p = 2²⁵⁶ − 2²²⁴ + 2¹⁹² + 2⁹⁶ − 1`) a `WeierstrassCurve` and — under the published primality of `p`
(a hypothesis `[Fact p.Prime]`, not an axiom) — a genuine `EllipticCurve`, with a verified rational
point (the standard generator `G`). All coordinate facts are machine-checked by `native_decide`.

The generator-on-curve check simultaneously **validates every constant** (`p`, `b`, `Gx`, `Gy`): if
any were mistyped, `Gy² = Gx³ − 3Gx + b` would fail in `𝔽_p`.

**Structural contrast with secp256k1.** P-256 has `c₄ ≠ 0` (here `c₄ = 144`), hence `j ≠ 0`: it has
**no** complex multiplication by `ℤ[ζ₃]` and **no** GLV endomorphism. secp256k1's `j = 0` / CM
structure (the source of its `λ` endomorphism, `GlvNoGo.lean`) is therefore a *special* feature of
that curve, not a generic one — P-256 is grounded here precisely to make that distinction concrete.
No new axioms; fully kernel-checked (`native_decide` additionally trusts the compiler).
-/

namespace Ecdlp.P256

/-- The NIST P-256 field prime `p = 2²⁵⁶ − 2²²⁴ + 2¹⁹² + 2⁹⁶ − 1`. -/
def p : ℕ := 2 ^ 256 - 2 ^ 224 + 2 ^ 192 + 2 ^ 96 - 1

/-- The P-256 curve coefficient `b` (the `a₆` of `y² = x³ − 3x + b`). -/
def b : ℕ := 41058363725152142129326129780047268409114441015993725554835256314039467401291

/-- The `x`-coordinate of the standard P-256 generator `G`. -/
def Gx : ℕ := 48439561293906451759052585252797914202762949526041747995844080717082404635286

/-- The `y`-coordinate of the standard P-256 generator `G`. -/
def Gy : ℕ := 36134250956749795798585127919587881956611106672985015071877198253568414405109

/-- NIST P-256 as a short Weierstrass curve `y² = x³ − 3x + b` over `𝔽_p`. -/
def P256 : WeierstrassCurve (ZMod p) where
  a₁ := 0
  a₂ := 0
  a₃ := 0
  a₄ := -3
  a₆ := (b : ZMod p)

/-- The P-256 discriminant is nonzero in `𝔽_p` (machine-checked) — the curve is nonsingular. -/
theorem P256_Δ_ne_zero : P256.Δ ≠ 0 := by native_decide

/-- The `c₄` invariant of P-256 is nonzero (`c₄ = 144`, machine-checked): unlike secp256k1
(`c₄ = 0`, `j = 0`), P-256 has `j ≠ 0` and hence no CM-by-`ℤ[ζ₃]` / GLV endomorphism. -/
theorem P256_c₄_ne_zero : P256.c₄ ≠ 0 := by native_decide

/-- **The P-256 base point lies on the curve.** The standard generator `G = (Gx, Gy)`, cast into
`𝔽_p`, satisfies P-256's Weierstrass equation — a genuine rational point of the Mathlib
`EllipticCurve`. This one `native_decide` also validates the constants `p`, `b`, `Gx`, `Gy`.
(A pure `ZMod p` computation — needs no primality, hence stated before the `[Fact p.Prime]`.) -/
theorem P256_generator_equation :
    P256.toAffine.Equation (Gx : ZMod p) (Gy : ZMod p) := by
  rw [WeierstrassCurve.Affine.equation_iff]
  simp only [P256]
  native_decide

variable [Fact (Nat.Prime p)]

/-- NIST P-256 is a genuine elliptic curve: its discriminant is a unit in `𝔽_p`. This makes
Mathlib's group law on `P256.toAffine.Point` available for it, exactly as for secp256k1. -/
instance : P256.IsElliptic := by
  refine ⟨?_⟩
  rw [isUnit_iff_ne_zero]
  exact P256_Δ_ne_zero

end Ecdlp.P256
