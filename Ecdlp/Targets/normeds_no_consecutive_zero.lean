import Mathlib
import Ecdlp.Proved.DivisionPolynomialEvalBridge
import Ecdlp.Proved.NormEDSIsElliptic
import Ecdlp.Proved.NormEDSSomos4

/-!
Open conjecture stem (NOT built, NOT imported — see `Ecdlp/Targets/README.md`).

**The N5 scalar obligation** (see `notes/DIVISION_POLY_TORSION_MAP.md` and the
TASK-005 memo in `notes/POINT_COUNTING_KEYSTONE.md`): the curve-specialized scalar
EDS `w := normEDS β (Ψ₃(x₀)) (preΨ₄(x₀))` with `β² = Ψ₂Sq(x₀)` over `𝔽̄_p` has no
two consecutive zeros at positive indices. Via the landed descent
(`secp256k1_exists_normEDS_consecutive_eq_zero_of_not_isCoprime`,
`Ecdlp/Proved/DivisionPolynomialEvalBridge.lean`) this closes node **N5**
(`IsCoprime (Φ n) (ΨSq n)`) for secp256k1, feeding the `#E[n] = n²` counting route
(N10/N11) behind `E[n] ≅ (ℤ/n)²` and the Weil-pairing non-degeneracy track.

Expected engine: the landed three-term machinery — `normEDS_isEllSequence`
(`NormEDSIsElliptic.lean`), `normEDS_somos4` (`NormEDSSomos4.lean`) — propagates a
consecutive-zero pair down the index range; the pairwise coprimality certificates
(`CoprimePsi2Psi3.lean` L5, `CoprimePsi3PrePsi4.lean` L6, `CoprimePsi2PrePsi4` L6b)
kill the low-index/degenerate cases (`β = 0` forces `Ψ₃(x₀) ≠ 0` and
`preΨ₄(x₀) ≠ 0`, etc.); `w 1 = 1` anchors the descent. Registry:
`targets/normeds_no_consecutive_zero.json`.
-/

namespace Ecdlp.Curve

open Polynomial

theorem secp256k1_normEDS_no_consecutive_zero
    (x₀ β : AlgebraicClosure (ZMod Secp256k1.p))
    (hβ : β ^ 2 = secp256k1Bar.Ψ₂Sq.eval x₀) {n : ℤ} (hn : 1 ≤ n) :
    ¬ (normEDS β (secp256k1Bar.Ψ₃.eval x₀) (secp256k1Bar.preΨ₄.eval x₀) n = 0 ∧
        normEDS β (secp256k1Bar.Ψ₃.eval x₀) (secp256k1Bar.preΨ₄.eval x₀) (n + 1) = 0) := by
  sorry

end Ecdlp.Curve
