import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.FourDivisionPolynomial
import Ecdlp.Proved.CoprimePsi3Psi5

/-!
# `preΨ₄` and `preΨ' 5` are coprime for secp256k1 — `E[4] ⊥ E[5]`

The 4- and 5-division polynomials of `E : Y² = X³ + 7` share no root: no nonidentity point is
simultaneously (primitive) 4-torsion and 5-torsion (a shared `x` would force `Q = ±P`, i.e.
`4 = 5`). Equivalently `gcd(preΨ₄, ψ₅) = 1`. Explicit extended-Euclid Bézout certificate over `𝔽_p`
(`Res(preΨ₄,ψ₅) = 2⁴⁸·3³⁶·7²⁴`, prime support `{2,3,7}` = the curve's bad-reduction primes); both
polynomials on exponents `≡ 0 (mod 3)`. Extends the `preΨ₄ ⊥ {2,3}` pairs (`CoprimePsi2PrePsi4`,
`CoprimePsi3PrePsi4`) toward full disjointness of the `{2,3,4,5,7}`-torsion loci. No new axioms
beyond `native_decide`.
-/

namespace Ecdlp.Curve

open Polynomial

/-- Bézout cofactor coefficients (extended-Euclid over `𝔽_p`, reduced to `ZMod p`):
`u` (cofactor of secp256k1.preΨ₄) and `v` (cofactor of (secp256k1.preΨ' 5)), with `u·secp256k1.preΨ₄ + v·(secp256k1.preΨ' 5) = 1`. -/
private def U9 : ZMod Secp256k1.p :=
  21896834932248132935881889391061076657228473720392915847185877512905550128919
private def U6 : ZMod Secp256k1.p :=
  84901562339755473583107551467197847817481285235818765513465859507841207910916
private def U3 : ZMod Secp256k1.p :=
  13438517959213249222243342566794052459825760965689424626376942960975387235656
private def U0 : ZMod Secp256k1.p :=
  6360566336338466790058738337301161898906475127687119460574261026301576566510
private def V3 : ZMod Secp256k1.p :=
  14399683874563985910361441245313150907762607444970946469017165796419546882765
private def V0 : ZMod Secp256k1.p :=
  87809340253361865798907064683023516122910603825961567104872347594261105440571

/-- **`preΨ₄` and `preΨ' 5` are coprime for secp256k1 — `E[4] ⊥ E[5]`.** `IsCoprime secp256k1.preΨ₄ (secp256k1.preΨ' 5)` via an explicit Bézout certificate over `𝔽_p`;
`native_decide` residue equations on the `X³`-lattice. Sibling of `CoprimePsi5Psi7`/`CoprimePsi3Psi7`. -/
theorem secp256k1_isCoprime_preΨ₄_preΨ₅ :
    IsCoprime secp256k1.preΨ₄ (secp256k1.preΨ' 5) := by
  refine ⟨C U9 * X ^ 9 + C U6 * X ^ 6 + C U3 * X ^ 3 + C U0,
    C V3 * X ^ 3 + C V0, ?_⟩
  rw [secp256k1_preΨ₄, secp256k1_preΨ₅]
  have e0 : (- 784 * U0 - 614656 * V0 : ZMod Secp256k1.p) = 1 := by native_decide
  have e3 : (280 * U0 - 784 * U3 - 548800 * V0 - 614656 * V3 : ZMod Secp256k1.p) = 0 := by native_decide
  have e6 : (2 * U0 + 280 * U3 - 784 * U6 - 11760 * V0 - 548800 * V3 : ZMod Secp256k1.p) = 0 := by native_decide
  have e9 : (2 * U3 + 280 * U6 - 784 * U9 + 2660 * V0 - 11760 * V3 : ZMod Secp256k1.p) = 0 := by native_decide
  have e12 : (2 * U6 + 280 * U9 + 5 * V0 + 2660 * V3 : ZMod Secp256k1.p) = 0 := by native_decide
  have e15 : (2 * U9 + 5 * V3 : ZMod Secp256k1.p) = 0 := by native_decide
  have key : (C U9 * X ^ 9 + C U6 * X ^ 6 + C U3 * X ^ 3 + C U0)
        * (2 * X ^ 6 + 280 * X ^ 3 - 784)
      + (C V3 * X ^ 3 + C V0)
        * (5 * X ^ 12 + 2660 * X ^ 9 - 11760 * X ^ 6 - 548800 * X ^ 3 - 614656)
      = C (- 784 * U0 - 614656 * V0)
        + C (280 * U0 - 784 * U3 - 548800 * V0 - 614656 * V3) * X ^ 3
        + C (2 * U0 + 280 * U3 - 784 * U6 - 11760 * V0 - 548800 * V3) * X ^ 6
        + C (2 * U3 + 280 * U6 - 784 * U9 + 2660 * V0 - 11760 * V3) * X ^ 9
        + C (2 * U6 + 280 * U9 + 5 * V0 + 2660 * V3) * X ^ 12
        + C (2 * U9 + 5 * V3) * X ^ 15 := by
    simp only [map_add, map_sub, map_mul, map_neg, map_ofNat]; ring
  rw [key, e0, e3, e6, e9, e12, e15]
  simp

end Ecdlp.Curve
