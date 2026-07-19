/-
# OPEN TARGET — N7-uniform x-coordinate formula for secp256k1 (Point level)

This is the **uniform** multiplication-by-`n` x-coordinate formula on the actual point
group `secp256k1.toAffine.Point`, for **all** `n` at once — the monolithic missing rung
(node S3/N7, `BARRIERS.md §B3`). The fixed cases `n = 2,3,4,5` are already proved as
per-`n` coordinate-level certificates (`MultiplicationFormula.lean`, `Triple`/`Quadruple`/
`QuintupleMultiplicationFormula.lean`); this states the general induction.

**Statement.** For a nonsingular affine `P = (x,y)` on secp256k1, if `n • P` is again an
affine point `(X, Y)` (equivalently `ψₙ(P) ≠ 0`, i.e. `P` is not `n`-torsion), then its
x-coordinate is `X = Φₙ(x)/ΨSqₙ(x)` in Mathlib's canonical univariate division polynomials.
The denominator is nonzero exactly because `n • P` is affine: `ΨSqₙ(x) = ψₙ(P)² ≠ 0` on the
curve (the eval bridge `eval_ΨSq_eq_normEDS_sq` + the torsion bridge).

**Why it is open.** Mathlib v4.31 has `Φ`/`ΨSq`/`ψ`/`φ` and their recurrences but **no**
`Point`↔`Ψ/Φ` connection and **no** `y`-coordinate (`ω`) division polynomial. A uniform proof
runs the induction `x([n+1]P) = addX(x([n]P), x, slope(x([n]P), x, y([n]P), y))` with
`x([n]P) = Φₙ/ΨSqₙ` and an `ω`-based `y([n]P) = ωₙ/ψₙ³` substituted — a single large rational
identity per step. Substrate landed toward this: the coordinate-ring translation
`φₙ·ΨSqₙ = Φₙ·ψₙ²` (`MultiplicationXCoordinateRing.lean`, S1) and the doubling divisibility
`ψₙ ∣ ψ₂ₙ` (`DivisionPolynomialDoubling.lean`, S2, the `ω` prerequisite).

Proof DAG (attack order): (S2′) define `ωₙ` — needs the `÷2` step, vacuous over `𝔽_p` since
`2` is a unit — → (S3a) `y([n]P) = ωₙ(P)/ψₙ(P)³` on Points → (S3b) the `x` induction above
→ THIS. Each arrow is a self-contained obligation; none is a single blind-CI rung.

This file is an **open stem** (one `sorry`), excluded from the built base and the no-`sorry`
gate. It is the registered, attackable Lean statement of the N7-uniform goal, not a claim
that it is proved.
-/
import Mathlib
import Ecdlp.Proved.DivisionPolynomial

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- OPEN: the uniform multiplication-by-`n` x-coordinate formula on secp256k1 points.
For nonsingular `P = (x,y)`, whenever `n • P = (X, Y)` is affine, `X = Φₙ(x)/ΨSqₙ(x)`. -/
theorem secp256k1_nsmul_x_eq_Φ_div_ΨSq
    (n : ℕ) (x y X Y : ZMod Secp256k1.p)
    (h : secp256k1.toAffine.Nonsingular x y)
    (h' : secp256k1.toAffine.Nonsingular X Y)
    (hn : n • (Point.some x y h) = Point.some X Y h') :
    X = (secp256k1.Φ n).eval x / (secp256k1.ΨSq n).eval x := by
  sorry

end Ecdlp.Curve
