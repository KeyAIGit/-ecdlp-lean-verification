import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.DivisionPolynomialDegree

/-!
Open conjecture stem (NOT built, NOT imported — see `Ecdlp/Targets/README.md`).

Torsion-tower rung above `ψ₁₁`: the secp256k1 13-division polynomial
`ψ₁₃ = preΨ' 13` (odd index ⇒ no `ψ₂` factor) should have degree
`(13² − 1)/2 = 84`, bounding the 13-torsion `x`-coordinates (`#E[13] ≤ 169`).
Expected route: the proved uniform bound `secp256k1_odd_preΨ_natDegree`
(`Ecdlp/Proved/OddTorsionBound.lean`) or the concrete `SevenTorsion.lean`
pattern at `n = 13`. Registry: `targets/thirteen_torsion_degree.json`.
-/

namespace Ecdlp.Curve

open Polynomial

theorem secp256k1_preΨ₁₃_natDegree : (secp256k1.preΨ' 13).natDegree = 84 := by
  sorry

end Ecdlp.Curve
