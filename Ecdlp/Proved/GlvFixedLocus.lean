import Mathlib
import Ecdlp.Proved.GlvEndomorphism

/-!
# The fixed locus of the GLV automorphism of secp256k1

Complementary to `GlvOrderThree.lean` (`glvHom ≠ id`): where the order-3 automorphism
`φ : (x, y) ↦ (β·x, y)` moves points, and where it fixes them. An affine point `P = (x, y)`
is fixed by `φ` **iff `x = 0`**: `φ(P) = P` means `β·x = x`, i.e. `(β − 1)·x = 0`, and since
`β ≠ 1` (a primitive cube root of unity) in the field `𝔽_p`, this forces `x = 0`.

Geometrically this is the ramification locus of the degree-3 quotient `E → E/⟨φ⟩`: the only
affine points that could be fixed are those on the line `x = 0`, where `y² = 0³ + 7 = 7`.
Together with `glvHom ≠ id` this pins down the automorphism exactly — it is nontrivial, and
its only possible fixed affine points lie over `x = 0`. Needs only the machine-checked
primality of `p` (for the point group); no new axioms.
-/

namespace Ecdlp.Curve

open WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- `β ≠ 1` in `𝔽_p`: the GLV factor is a *primitive* cube root of unity, not `1`. A single
machine-checked residue fact (`β ≢ 1 (mod p)`). -/
theorem secp256k1_beta_ne_one : (Secp256k1.beta : ZMod Secp256k1.p) ≠ 1 := by
  have h : ¬ (((Secp256k1.beta : ℕ) : ZMod Secp256k1.p) = ((1 : ℕ) : ZMod Secp256k1.p)) := by
    rw [ZMod.natCast_eq_natCast_iff]
    native_decide
  simpa using h

/-- **Fixed-point locus of the GLV automorphism: `φ(P) = P ⟺ x_P = 0`.** For an affine point
`P = (x, y)` of secp256k1, `glvPoint P = P` holds iff `x = 0`. Forward: `β·x = x` gives
`(β − 1)·x = 0`, and `β ≠ 1` in the field forces `x = 0`. Backward: `β·0 = 0`. This is the
ramification locus of `E → E/⟨φ⟩`; with `secp256k1_glvHom_ne_id` it fully characterizes the
order-3 automorphism's action. -/
theorem secp256k1_glvPoint_fixed_iff
    (x y : ZMod Secp256k1.p) (h : secp256k1.toAffine.Nonsingular x y) :
    glvPoint (Point.some x y h) = Point.some x y h ↔ x = 0 := by
  rw [glvPoint_some, Point.some.injEq]
  constructor
  · rintro ⟨hx, -⟩
    have hfac : ((Secp256k1.beta : ZMod Secp256k1.p) - 1) * x = 0 := by
      linear_combination hx
    rcases mul_eq_zero.mp hfac with hb | hx0
    · exact absurd (sub_eq_zero.mp hb) secp256k1_beta_ne_one
    · exact hx0
  · rintro rfl
    exact ⟨mul_zero _, rfl⟩

end Ecdlp.Curve
