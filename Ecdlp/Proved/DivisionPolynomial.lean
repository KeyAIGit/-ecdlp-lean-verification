import Mathlib
import Ecdlp.Proved.Secp256k1Curve

/-!
# secp256k1 meets Mathlib's division polynomials (the torsion foundation)

The **division polynomials** `ψₙ` are the gateway to the `n`-torsion subgroup `E[n]`:
a point `P` is `n`-torsion iff `ψₙ` vanishes at its `x`-coordinate. They are the
foundation on which the Weil pairing, the structure `E[n] ≅ (ℤ/n)²`, and the MOV/FR
transfer are all built. Mathlib formalizes the `ψₙ` (`Mathlib.AlgebraicGeometry.
EllipticCurve.DivisionPolynomial`) but **not** the Weil pairing or isogenies (see
`notes/FOUNDATIONS.md` for the roadmap and the precise gap).

This file is the first **bridge node**: it instantiates Mathlib's `b`-invariants and
the 2-division polynomial `Ψ₂Sq` for the concrete secp256k1 curve `Y² = X³ + 7`,
connecting our curve to that foundation. Everything here is a polynomial/ring
identity over `𝔽_p` — unconditional (no `[Fact p.Prime]`, no axioms).

`Ψ₂Sq` (congruent to `ψ₂²`) is the **2-torsion polynomial**: its roots are exactly
the `x`-coordinates of the points of order 2. For secp256k1 it is `4X³ + 28 =
4(X³ + 7)`, so the 2-torsion `x`-coordinates are precisely the roots of `X³ + 7` —
the curve equation at `Y = 0`, as expected.
-/

namespace Ecdlp.Curve

open Polynomial

/-- secp256k1 has `b₂ = 0` (since `a₁ = a₂ = 0`). -/
theorem secp256k1_b₂ : secp256k1.b₂ = 0 := by
  simp only [WeierstrassCurve.b₂, secp256k1]; norm_num

/-- secp256k1 has `b₄ = 0` (since `a₃ = a₄ = 0`). -/
theorem secp256k1_b₄ : secp256k1.b₄ = 0 := by
  simp only [WeierstrassCurve.b₄, secp256k1]; norm_num

/-- secp256k1 has `b₆ = 28` (`= 4·a₆ = 4·7`). -/
theorem secp256k1_b₆ : secp256k1.b₆ = 28 := by
  simp only [WeierstrassCurve.b₆, secp256k1]; norm_num

/-- secp256k1 has `b₈ = 0` (every term carries an `a₁…a₄` factor). -/
theorem secp256k1_b₈ : secp256k1.b₈ = 0 := by
  simp only [WeierstrassCurve.b₈, secp256k1]; norm_num

/-- **The secp256k1 2-division polynomial is `Ψ₂Sq = 4X³ + 28 = 4(X³ + 7)`.** Its
roots are the `x`-coordinates of the order-2 points: the roots of `X³ + 7` (the
curve at `Y = 0`). This is the first concrete instance of Mathlib's torsion
machinery for secp256k1 — the entry point to `E[n]` and (eventually) the Weil
pairing. -/
theorem secp256k1_Ψ₂Sq : secp256k1.Ψ₂Sq = C 4 * X ^ 3 + C 28 := by
  rw [WeierstrassCurve.Ψ₂Sq, secp256k1_b₂, secp256k1_b₄, secp256k1_b₆]
  simp only [mul_zero, C_0, zero_mul, add_zero]

/-- **The secp256k1 3-division polynomial is `Ψ₃ = 3X⁴ + 3·28·X = 3X⁴ + 84X`.** Its
roots are the `x`-coordinates of the order-3 points — the 3-torsion `E[3]`. For
secp256k1 this torsion is structurally special: the curve has `j = 0` / complex
multiplication by `ℤ[ζ₃]` (the source of the GLV endomorphism `λ`), so the order-3
structure is exactly the CM that `CubeRoot.lean` / `Secp256k1Order.lean` exploit. -/
theorem secp256k1_Ψ₃ : secp256k1.Ψ₃ = 3 * X ^ 4 + 3 * C 28 * X := by
  rw [WeierstrassCurve.Ψ₃, secp256k1_b₂, secp256k1_b₄, secp256k1_b₆, secp256k1_b₈]
  simp only [mul_zero, C_0, zero_mul, add_zero]

end Ecdlp.Curve
