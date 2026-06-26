import Mathlib
import Ecdlp.Proved.Secp256k1Curve

/-!
# OPEN TARGET — torsion via division polynomials (rung 4 toward the Weil pairing)

Open stem (one `sorry`, **not** built by `lake build`, **not** gated). Records, as
well-formed Lean, the first genuinely hard rung of `notes/FOUNDATIONS.md`: the
bridge between the division polynomials (which Mathlib has) and the `n`-torsion
points (the gateway to the Weil pairing, which Mathlib lacks).

Stated here specialised to the 2-torsion of secp256k1, the simplest instance of the
general criterion `ψₙ(x_P) = 0 ⟺ [n]P = O`. The general, both-directions statement
over `ℕ` is the open foundation; this concrete fragment is the prover-loop entry
point. See `notes/FOUNDATIONS.md` for the full ladder.
-/

namespace Ecdlp.Targets.WeilPairing

open Polynomial

/-- TARGET. An order-2 point of secp256k1 sits at `Y = 0`, and its `x`-coordinate is
a root of the 2-division polynomial `Ψ₂Sq`: if `(x, 0)` satisfies the Weierstrass
equation, then `Ψ₂Sq` vanishes at `x`. (The general `ψₙ`-vanishing ⟺ `n`-torsion
equivalence — both directions, all `n` — is the open rung toward the Weil pairing.) -/
theorem secp256k1_Ψ₂Sq_root_of_two_torsion (x : ZMod Secp256k1.p)
    (hx : Ecdlp.Curve.secp256k1.toAffine.Equation x 0) :
    Ecdlp.Curve.secp256k1.Ψ₂Sq.eval x = 0 := by
  sorry

end Ecdlp.Targets.WeilPairing
