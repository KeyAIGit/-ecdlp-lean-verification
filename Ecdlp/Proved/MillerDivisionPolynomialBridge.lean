import Mathlib
import Ecdlp.Proved.WeilDivisorClass
import Ecdlp.Proved.ThreeTorsionBridge
import Ecdlp.Proved.FiveTorsionBridge
import Ecdlp.Proved.SevenTorsionBridge

/-!
# Bridge between the division-polynomial tower and the Miller/divisor tower (secp256k1)

Two independent ladders in this repository describe the same `n`-torsion condition on secp256k1
from opposite ends:

* the **division-polynomial tower** (`ThreeTorsionBridge`, `FiveTorsionBridge`,
  `SevenTorsionBridge`): for `n ∈ {3,5,7}` a nonzero affine point `P = (x,y)` is `n`-torsion iff
  the `n`-division polynomial vanishes at it, `n • P = 0 ↔ (ψ n).evalEval x y = 0` — an elementary
  root condition on the coordinates;
* the **Miller/divisor tower** (`WeilDivisorClass`, rung 1): `P` is `n`-torsion iff its
  Abel–Jacobi class is `n`-torsion in the ideal class group, `n • P = 0 ↔ n • toClass P = 0` —
  i.e. iff the degree-0 divisor `n·([P] − [O])` is **principal**, the existence precondition for
  the Weil pairing's Miller function `f_P`.

Composing the two equivalences at their shared middle term `n • P = 0` welds the towers together:
**the coordinate `x` is a root of the division polynomial `ψ n` iff the Miller divisor
`n·([P] − [O])` is principal.** This is a purely diagrammatic step — `Iff.trans` of two proven
rungs — but it is the first result that lets a computable coordinate condition (`ψ n = 0`, a
polynomial identity in `ZMod p`) *decide* the divisor-theoretic principality that the Weil
construction needs, without any new torsion analysis. It records that the two foundations built
here are not parallel but coincident.

Honest scope: this connects the two `n`-torsion characterisations for the concrete primes
`n = 3,5,7` where the division-polynomial bridge is proven; it does **not** yet produce the
Miller function `f_P` from a `ψ n` root (that is rung 2, `secp256k1_miller_function_exists`,
which takes `n • P = 0` as input — this bridge just supplies that input from `ψ n = 0`). No new
axioms; fully kernel-checked.
-/

namespace Ecdlp.Weil

open WeierstrassCurve.Affine WeierstrassCurve.Affine.Point

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **ψ₃ root ⟺ Miller divisor `3·([P] − [O])` principal.** For a nonzero affine point
`P = (x,y)` of secp256k1, the 3-division polynomial vanishes at `P` iff the Abel–Jacobi class of
`P` is 3-torsion in the class group — i.e. iff `3·([P] − [O])` is principal. Welds the
division-polynomial 3-torsion bridge to divisor-class rung 1 at their shared middle `3 • P = 0`. -/
theorem secp256k1_psi3_root_iff_class_torsion
    (x y : ZMod Secp256k1.p) (h : Ecdlp.Curve.secp256k1.toAffine.Nonsingular x y) :
    (Ecdlp.Curve.secp256k1.ψ 3).evalEval x y = 0 ↔ (3 : ℕ) • toClass (Point.some x y h) = 0 :=
  (Ecdlp.Curve.secp256k1_three_nsmul_eq_zero_iff x y h).symm.trans
    (secp256k1_torsion_iff_principal (Point.some x y h) 3)

/-- **ψ₅ root ⟺ Miller divisor `5·([P] − [O])` principal.** The `n = 5` analogue of
`secp256k1_psi3_root_iff_class_torsion`. -/
theorem secp256k1_psi5_root_iff_class_torsion
    (x y : ZMod Secp256k1.p) (h : Ecdlp.Curve.secp256k1.toAffine.Nonsingular x y) :
    (Ecdlp.Curve.secp256k1.ψ 5).evalEval x y = 0 ↔ (5 : ℕ) • toClass (Point.some x y h) = 0 :=
  (Ecdlp.Curve.secp256k1_five_nsmul_eq_zero_iff x y h).symm.trans
    (secp256k1_torsion_iff_principal (Point.some x y h) 5)

/-- **ψ₇ root ⟺ Miller divisor `7·([P] − [O])` principal.** The `n = 7` analogue of
`secp256k1_psi3_root_iff_class_torsion`. -/
theorem secp256k1_psi7_root_iff_class_torsion
    (x y : ZMod Secp256k1.p) (h : Ecdlp.Curve.secp256k1.toAffine.Nonsingular x y) :
    (Ecdlp.Curve.secp256k1.ψ 7).evalEval x y = 0 ↔ (7 : ℕ) • toClass (Point.some x y h) = 0 :=
  (Ecdlp.Curve.secp256k1_seven_nsmul_eq_zero_iff x y h).symm.trans
    (secp256k1_torsion_iff_principal (Point.some x y h) 7)

end Ecdlp.Weil
