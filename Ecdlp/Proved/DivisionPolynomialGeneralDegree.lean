import Mathlib
import Ecdlp.Proved.DivisionPolynomial

/-!
# N4: the general-`n` degree / monic layer of secp256k1's division polynomials

Mathlib provides, for any Weierstrass curve over a `Nontrivial` / `NoZeroDivisors` base, the
degrees and leading coefficients of the canonical division-polynomial sequences `Φₙ` and `ΨSqₙ`
(`Mathlib.AlgebraicGeometry.EllipticCurve.DivisionPolynomial.Degree`). This file instantiates that
layer for secp256k1 over `𝔽_p` — node **N4** on the `ψₙ ↔ E[n]` critical path
(`notes/DIVISION_POLY_TORSION_MAP.md`): the numerator `Φₙ` of the multiplication-by-`n`
`x`-coordinate map `x ∘ [n] = Φₙ / ΨSqₙ` is **monic of degree `n²`**, and the denominator `ΨSqₙ`
has degree `n² − 1` (for `n ≠ 0`).

The repo previously carried only the fixed-`n` polynomials (`Φ₂`, `Φ₃`, `Ψ₂Sq`, `Ψ₃`); this is the
uniform statement for **all `n`**. It supplies the **degree half** of the eventual `#E[n] = n²`
count (node N10). The **separability half** — uniform coprimality `gcd(Φₙ, ΨSqₙ) = 1` (N5 → N10) —
is the remaining open gate and is deliberately **not** claimed here.

Pure Mathlib instantiation over the field `𝔽_p` (`Fact (Nat.Prime p)` ⇒ `Field`, hence `Nontrivial`
and `NoZeroDivisors`); no new axioms, no `native_decide`.
-/

namespace Ecdlp.Curve

open Polynomial

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **N4: `Φₙ` for secp256k1 is monic of degree `n²`** (all `n : ℤ`). The numerator of the
multiplication-by-`n` `x`-coordinate map. -/
theorem secp256k1_Φ_natDegree (n : ℤ) : (secp256k1.Φ n).natDegree = n.natAbs ^ 2 :=
  secp256k1.natDegree_Φ n

/-- `Φₙ` for secp256k1 is monic (leading coefficient `1`), for every `n`. -/
theorem secp256k1_Φ_monic (n : ℤ) : (secp256k1.Φ n).Monic :=
  secp256k1.leadingCoeff_Φ n

/-- `Φₙ` for secp256k1 is nonzero, for every `n`. -/
theorem secp256k1_Φ_ne_zero (n : ℤ) : secp256k1.Φ n ≠ 0 :=
  secp256k1.Φ_ne_zero n

/-- **`ΨSqₙ` for secp256k1 has degree `n² − 1`** for `n ≠ 0` in `𝔽_p`. The denominator of the
multiplication-by-`n` `x`-coordinate map. -/
theorem secp256k1_ΨSq_natDegree {n : ℤ} (h : (n : ZMod Secp256k1.p) ≠ 0) :
    (secp256k1.ΨSq n).natDegree = n.natAbs ^ 2 - 1 :=
  secp256k1.natDegree_ΨSq h

/-- `ΨSqₙ` for secp256k1 is nonzero for `n ≠ 0` in `𝔽_p`. -/
theorem secp256k1_ΨSq_ne_zero {n : ℤ} (h : (n : ZMod Secp256k1.p) ≠ 0) :
    secp256k1.ΨSq n ≠ 0 :=
  secp256k1.ΨSq_ne_zero h

end Ecdlp.Curve
