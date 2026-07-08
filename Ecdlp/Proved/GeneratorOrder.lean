import Ecdlp.Proved.GlvEndomorphism
import Ecdlp.Proved.Secp256k1PrimeP
import Ecdlp.Proved.Secp256k1PrimeN

/-!
# The secp256k1 base point: exact order `n` and the GLV eigenvalue at `G`

Two kernel-verified facts about the SEC2 generator `G = (Gx, Gy)`, realized as an element
of Mathlib's elliptic-curve point group `secp256k1.toAffine.Point`:

* `secp256k1_generator_addOrderOf : addOrderOf secp256k1G = Secp256k1.n` — `G` has *exact*
  order `n` (the published prime group order), so `⟨G⟩` is cyclic of order `n`. This is the
  **weak point-counting keystone**: it pins the cryptographic subgroup without computing
  `#E(𝔽_p)` (no Hasse/Schoof), which `notes/POINT_COUNTING_KEYSTONE.md` had billed as the
  multi-month-blocked node.
* `secp256k1_glvPoint_generator : glvPoint secp256k1G = (Secp256k1.lam : ℕ) • secp256k1G` —
  the GLV endomorphism acts as the scalar `[λ]` **at the generator** (the eigenvalue
  identity that `GlvEigenvalue.lean` could only state *conditional on* whole-group
  cyclicity). The other cube root `λ²` is ruled out (checked false).

Both are decided by native evaluation of the Mathlib group law over `𝔽_p` (fast
double-and-add — `Point.add`/`nsmul` reduce). Like every `native_decide` fact in this repo
they additionally **trust the Lean compiler** via `Lean.ofReduceBool` (catalogued in
`TRUST_REPORT.md`); they are not kernel-pure. They do **not** give the *strong* keystone
`#E(𝔽_p) = n` (cofactor 1), which still needs the Hasse bound, absent from Mathlib — this
is the base-point subgroup `⟨G⟩`, not the whole rational-point group.
-/

open WeierstrassCurve.Affine

namespace Ecdlp.Curve

/-- The secp256k1 base point `G = (Gx, Gy)` as an element of the Mathlib point group. -/
def secp256k1G : secp256k1.toAffine.Point :=
  Point.some (Secp256k1.Gx : ZMod Secp256k1.p) (Secp256k1.Gy : ZMod Secp256k1.p)
    secp256k1_generator_nonsingular

/-- `n • G = 0`: the published prime order annihilates the base point (native-evaluated). -/
theorem secp256k1_generator_nsmul_n_eq_zero :
    (Secp256k1.n : ℕ) • secp256k1G = 0 := by native_decide

/-- The base point is not the group identity (it is an affine point). -/
theorem secp256k1_generator_ne_zero : secp256k1G ≠ 0 :=
  Point.some_ne_zero _

/-- **The secp256k1 base point has exact order `n`** (the published prime group order), so
`⟨G⟩` is cyclic of order `n` — the weak point-counting keystone (no Hasse / `#E` needed). -/
theorem secp256k1_generator_addOrderOf :
    addOrderOf secp256k1G = Secp256k1.n :=
  addOrderOf_eq_prime secp256k1_generator_nsmul_n_eq_zero secp256k1_generator_ne_zero

/-- **The GLV endomorphism acts as `[λ]` at the generator:** `glvPoint G = λ • G`.
Unlike `secp256k1_glvHom_eq_zsmul` (conditional on whole-group cyclicity) this is the
unconditional coordinate identity at `G` itself, native-evaluated; the other cube root
`λ²` is ruled out. -/
theorem secp256k1_glvPoint_generator :
    glvPoint secp256k1G = (Secp256k1.lam : ℕ) • secp256k1G := by native_decide

end Ecdlp.Curve
