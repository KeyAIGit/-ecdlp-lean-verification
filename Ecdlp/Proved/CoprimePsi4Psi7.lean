import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.FourDivisionPolynomial
import Ecdlp.Proved.CoprimePsi3Psi7

/-!
# `preΨ₄` and `preΨ' 7` are coprime for secp256k1 — `E[4] ⊥ E[7]`

The (primitive) 4- and 7-division polynomials of `E : Y² = X³ + 7` share no root: no nonidentity
point is simultaneously 4-torsion and 7-torsion (`4 = 7` impossible). Equivalently
`gcd(preΨ₄, ψ₇) = 1`. Explicit extended-Euclid Bézout certificate over `𝔽_p`
(`Res(preΨ₄,ψ₇) = 2⁹⁶·3⁷²·7⁴⁸`, prime support `{2,3,7}`); both polynomials on exponents `≡ 0 (mod 3)`.
With `CoprimePsi4Psi5` this completes `preΨ₄ ⊥ {2,3,5,7}` — full mutual disjointness of the
`{2,3,4,5,7}`-torsion loci. No new axioms beyond `native_decide`.
-/

namespace Ecdlp.Curve

open Polynomial

/-- Bézout cofactor coefficients (extended-Euclid over `𝔽_p`, reduced to `ZMod p`):
`u` (cofactor of secp256k1.preΨ₄) and `v` (cofactor of (secp256k1.preΨ' 7)), with `u·secp256k1.preΨ₄ + v·(secp256k1.preΨ' 7) = 1`. -/
private def U21 : ZMod Secp256k1.p :=
  35304469875353268497525175574631223173762867441676870391032677387522548450151
private def U18 : ZMod Secp256k1.p :=
  22973882440308699226233185239977791558659283115912682864244298960720530753742
private def U15 : ZMod Secp256k1.p :=
  7163352528738782471473658234641255278820886601573509053218187657589131273257
private def U12 : ZMod Secp256k1.p :=
  106886262779581822445166666219028369948929682131435732616581848827415251929200
private def U9 : ZMod Secp256k1.p :=
  12754216079417002493050638285769674845471739530148473894841772240885716500065
private def U6 : ZMod Secp256k1.p :=
  27385774807750645873281027838220757558157292508465620230682709359619154654374
private def U3 : ZMod Secp256k1.p :=
  36236359976056597586934002628612890346411079449963445681935640232188607171837
private def U0 : ZMod Secp256k1.p :=
  103874026680148269467023074639983302401329641429074483207080888312172963779996
private def V3 : ZMod Secp256k1.p :=
  56079916742651177814176226983641312152222029111315502196537854465227177398050
private def V0 : ZMod Secp256k1.p :=
  86794935951053302939401441601510221486261773393362768849038796007009159573306

/-- **`preΨ₄` and `preΨ' 7` are coprime for secp256k1 — `E[4] ⊥ E[7]`.** `IsCoprime secp256k1.preΨ₄ (secp256k1.preΨ' 7)` via an explicit Bézout certificate over `𝔽_p`;
`native_decide` residue equations on the `X³`-lattice. Sibling of `CoprimePsi5Psi7`/`CoprimePsi3Psi7`. -/
theorem secp256k1_isCoprime_preΨ₄_preΨ₇ :
    IsCoprime secp256k1.preΨ₄ (secp256k1.preΨ' 7) := by
  refine ⟨C U21 * X ^ 21 + C U18 * X ^ 18 + C U15 * X ^ 15 + C U12 * X ^ 12 + C U9 * X ^ 9 + C U6 * X ^ 6 + C U3 * X ^ 3 + C U0,
    C V3 * X ^ 3 + C V0, ?_⟩
  rw [secp256k1_preΨ₄, secp256k1_preΨ₇]
  have e0 : (- 784 * U0 + 377801998336 * V0 : ZMod Secp256k1.p) = 1 := by native_decide
  have e3 : (280 * U0 - 784 * U3 - 661153497088 * V0 + 377801998336 * V3 : ZMod Secp256k1.p) = 0 := by native_decide
  have e6 : (2 * U0 + 280 * U3 - 784 * U6 - 330576748544 * V0 - 661153497088 * V3 : ZMod Secp256k1.p) = 0 := by native_decide
  have e9 : (2 * U3 + 280 * U6 - 784 * U9 - 26142548992 * V0 - 330576748544 * V3 : ZMod Secp256k1.p) = 0 := by native_decide
  have e12 : (2 * U6 + 280 * U9 - 784 * U12 - 2228742656 * V0 - 26142548992 * V3 : ZMod Secp256k1.p) = 0 := by native_decide
  have e15 : (2 * U9 + 280 * U12 - 784 * U15 - 284585728 * V0 - 2228742656 * V3 : ZMod Secp256k1.p) = 0 := by native_decide
  have e18 : (2 * U12 + 280 * U15 - 784 * U18 - 2101904 * V0 - 284585728 * V3 : ZMod Secp256k1.p) = 0 := by native_decide
  have e21 : (2 * U15 + 280 * U18 - 784 * U21 + 27608 * V0 - 2101904 * V3 : ZMod Secp256k1.p) = 0 := by native_decide
  have e24 : (2 * U18 + 280 * U21 + 7 * V0 + 27608 * V3 : ZMod Secp256k1.p) = 0 := by native_decide
  have e27 : (2 * U21 + 7 * V3 : ZMod Secp256k1.p) = 0 := by native_decide
  have key : (C U21 * X ^ 21 + C U18 * X ^ 18 + C U15 * X ^ 15 + C U12 * X ^ 12 + C U9 * X ^ 9 + C U6 * X ^ 6 + C U3 * X ^ 3 + C U0)
        * (2 * X ^ 6 + 280 * X ^ 3 - 784)
      + (C V3 * X ^ 3 + C V0)
        * (7 * X ^ 24 + 27608 * X ^ 21 - 2101904 * X ^ 18 - 284585728 * X ^ 15 - 2228742656 * X ^ 12 - 26142548992 * X ^ 9 - 330576748544 * X ^ 6 - 661153497088 * X ^ 3 + 377801998336)
      = C (- 784 * U0 + 377801998336 * V0)
        + C (280 * U0 - 784 * U3 - 661153497088 * V0 + 377801998336 * V3) * X ^ 3
        + C (2 * U0 + 280 * U3 - 784 * U6 - 330576748544 * V0 - 661153497088 * V3) * X ^ 6
        + C (2 * U3 + 280 * U6 - 784 * U9 - 26142548992 * V0 - 330576748544 * V3) * X ^ 9
        + C (2 * U6 + 280 * U9 - 784 * U12 - 2228742656 * V0 - 26142548992 * V3) * X ^ 12
        + C (2 * U9 + 280 * U12 - 784 * U15 - 284585728 * V0 - 2228742656 * V3) * X ^ 15
        + C (2 * U12 + 280 * U15 - 784 * U18 - 2101904 * V0 - 284585728 * V3) * X ^ 18
        + C (2 * U15 + 280 * U18 - 784 * U21 + 27608 * V0 - 2101904 * V3) * X ^ 21
        + C (2 * U18 + 280 * U21 + 7 * V0 + 27608 * V3) * X ^ 24
        + C (2 * U21 + 7 * V3) * X ^ 27 := by
    simp only [map_add, map_sub, map_mul, map_neg, map_ofNat]; ring
  rw [key, e0, e3, e6, e9, e12, e15, e18, e21, e24, e27]
  simp

end Ecdlp.Curve
