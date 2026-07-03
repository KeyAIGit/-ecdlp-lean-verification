import Mathlib
import Ecdlp.Proved.Secp256k1Curve
import Ecdlp.Proved.GlvEndomorphism
import Ecdlp.Proved.GlvMonoidHom
import Ecdlp.Proved.GlvMinPoly

/-!
# The GLV endomorphism is a *nontrivial* order-3 automorphism of secp256k1

The GLV structure files already establish that the self-map `(x, y) ↦ (β·x, y)` is an
additive endomorphism `glvHom` of the secp256k1 point group, that it satisfies its minimal
polynomial `X² + X + 1 = 0` as an operator identity (`glvHom_minpoly`), and that its cube is
the identity (`glvPoint_cube_eq_id`). Those facts alone leave open the *degenerate*
possibility that `glvHom` is itself the identity (which would collapse `X² + X + 1` to a
statement about the zero endomorphism and make the "cube root of unity" claim vacuous).

Here we rule that out: `glvHom ≠ id`, witnessed on the SEC2 base point `G`, because
`β·Gx ≠ Gx` in `𝔽_p` (as `β ≠ 1` and `Gx ≠ 0`, a single machine-checked fact). Consequently
`glvHom` is a **primitive** cube root of unity: it has order *exactly* 3 in `Aut(E)` (its
cube is the identity and it is not the identity, and `3` is prime), so the subring `ℤ[β] ≅
ℤ[ω]` genuinely embeds in `End(E)` — the arithmetic content of "secp256k1 has complex
multiplication by the Eisenstein integers", which is *why* the GLV endomorphism exists.

We also record the point-level trace-zero identity `P + λ·P + λ²·P = 0` for every point `P`,
the pointwise reading of `glvHom_minpoly`. Needs only the machine-checked primality of `p`
(for the point group); no new axioms.
-/

namespace Ecdlp.Curve

open WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- `β·Gx ≠ Gx` in `𝔽_p`. Since `β` is a primitive cube root of unity (`β ≠ 1`) and the
generator abscissa `Gx ≠ 0`, scaling `Gx` by `β` moves it — a single machine-checked
residue fact. This is the arithmetic core of "the GLV endomorphism is nontrivial". -/
theorem secp256k1_beta_mul_Gx_ne_Gx :
    (Secp256k1.beta : ZMod Secp256k1.p) * (Secp256k1.Gx : ZMod Secp256k1.p)
      ≠ (Secp256k1.Gx : ZMod Secp256k1.p) := by
  have h : ¬ (((Secp256k1.beta * Secp256k1.Gx : ℕ) : ZMod Secp256k1.p)
      = ((Secp256k1.Gx : ℕ) : ZMod Secp256k1.p)) := by
    rw [ZMod.natCast_eq_natCast_iff]
    native_decide
  push_cast at h
  exact h

/-- **The GLV endomorphism is not the identity.** Evaluated on the base point `G = (Gx, Gy)`,
`glvHom G = (β·Gx, Gy) ≠ (Gx, Gy) = G` because `β·Gx ≠ Gx`. Together with `glvHom³ = id`
(`glvPoint_cube_eq_id`) and the minimal-polynomial identity `glvHom² + glvHom + id = 0`
(`glvHom_minpoly`), this pins the order of `glvHom` in `Aut(E)` at *exactly* 3: it is a
**primitive** cube root of unity, so `ℤ[β] ≅ ℤ[ω]` embeds nontrivially in `End(E)`. -/
theorem secp256k1_glvHom_ne_id :
    glvHom ≠ AddMonoidHom.id secp256k1.toAffine.Point := by
  intro h
  have hP : glvHom (Point.some (Secp256k1.Gx : ZMod Secp256k1.p)
      (Secp256k1.Gy : ZMod Secp256k1.p) secp256k1_generator_nonsingular)
      = Point.some (Secp256k1.Gx : ZMod Secp256k1.p)
          (Secp256k1.Gy : ZMod Secp256k1.p) secp256k1_generator_nonsingular := by
    rw [h]; rfl
  rw [glvHom_apply, glvPoint_some, Point.some.injEq] at hP
  exact secp256k1_beta_mul_Gx_ne_Gx hP.1

/-- **Point-level trace-zero identity: `P + λ·P + λ²·P = 0`.** The pointwise reading of the
operator identity `glvHom_minpoly` (`glvHom² + glvHom + id = 0`): applying `X² + X + 1` to any
point `P` returns the identity `O`. Equivalently, the three points on a `⟨λ⟩`-orbit sum to
zero — the additive shadow of `β² + β + 1 = 0`. -/
theorem secp256k1_glvPoint_orbit_sum (P : secp256k1.toAffine.Point) :
    P + glvPoint P + glvPoint (glvPoint P) = 0 := by
  have h := DFunLike.congr_fun glvHom_minpoly P
  simp only [AddMonoidHom.add_apply, AddMonoidHom.comp_apply, AddMonoidHom.id_apply,
    AddMonoidHom.zero_apply, glvHom_apply] at h
  rw [← h]; abel

end Ecdlp.Curve
