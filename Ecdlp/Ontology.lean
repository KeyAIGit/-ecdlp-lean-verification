import Mathlib
import Ecdlp.Secp256k1Verified

/-!
# ECDLP ontology (minimal)

Kernel-checked vocabulary that the open-conjecture stems in `Ecdlp/Targets/`
and future promoted proofs build on. Intentionally small and safe: type
abbreviations over `ZMod` plus the verified secp256k1 constants re-exported
under a stable namespace. The generator (`scripts/generator.py`) proposes
statements against this vocabulary; the Lean kernel decides truth.
-/

namespace Ecdlp.Ontology

/-- A scalar modulo the group order `n` — the exponent ring of the ECDLP. -/
abbrev Scalar (n : ℕ) := ZMod n

/-- A base-field element of `F_p`. -/
abbrev FieldElt (p : ℕ) := ZMod p

/-- secp256k1 field characteristic `p`, from the verified base. -/
abbrev secpP : ℕ := Secp256k1.p

/-- secp256k1 group order `n`, from the verified base. -/
abbrev secpN : ℕ := Secp256k1.n

end Ecdlp.Ontology
