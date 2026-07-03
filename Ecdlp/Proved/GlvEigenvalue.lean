import Mathlib
import Ecdlp.Proved.GlvMonoidHom
import Ecdlp.Proved.GlvMinPoly

/-!
# The GLV eigenvalue property, conditional on cyclicity of the point group

This is the frontier node the GLV files pointed at but had not reached: that the *geometric*
endomorphism `φ = glvHom` — the map `(x, y) ↦ (β·x, y)` — acts on the rational points as
multiplication by a **scalar** `[k]`, the eigenvalue that the practical GLV method calls `λ`.

The bridge that makes this reachable is a structural fact about secp256k1: its group of
rational points is **cyclic** (it has prime order `n` and cofactor `1`). And *any* additive
endomorphism of a cyclic group is multiplication by a fixed integer `k` (Mathlib's
`MonoidHom.map_cyclic`, here in additive form via `IsAddCyclic.exists_generator`). Feeding the
operator identity `φ² + φ + 1 = 0` (`glvHom_minpoly`) through that scalar shows `k² + k + 1`
annihilates every point — i.e. `k² + k + 1 ≡ 0` modulo the group order (the eigenvalue relation
`λ² + λ + 1 ≡ 0 (mod n)` proved arithmetically in `CubeRoot.lean` as `glv_lambda_eigenvalue`).

**Honesty about the hypothesis.** Cyclicity of `E(𝔽_p)` is taken as an explicit instance
argument `[IsAddCyclic …]`, *not* proved here: establishing it requires the cardinality
`#E(𝔽_p) = n`, i.e. point-counting (Hasse bound / Frobenius trace), which Mathlib does not have
for a 256-bit curve. So this theorem is a genuine **reduction**: it proves the entire GLV
eigenvalue property *elementarily, modulo the one deep input* (the group's order and cyclic
structure), and isolates exactly that input as the remaining barrier. The two appearances of
`X² + X + 1` live at different moduli — `β` mod `p` (on coordinates), `k` mod `n` (on the
group) — and this node is the additive-group half of that story. No new axioms.
-/

namespace Ecdlp.Curve

open WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **GLV eigenvalue property (conditional on cyclicity).** If the secp256k1 point group is
cyclic, then the GLV endomorphism `glvHom` is multiplication by a fixed integer `k`, and that
`k` satisfies `k² + k + 1 ≡ 0` on the group (annihilates every point) — the abstract form of
the eigenvalue relation `λ² + λ + 1 ≡ 0 (mod n)`. The scalar `k` is the GLV `λ`; proving it is
one specific value would need the group order `n`, which is the point-counting barrier. -/
theorem secp256k1_glvHom_eq_zsmul [IsAddCyclic secp256k1.toAffine.Point] :
    ∃ k : ℤ, (∀ P, glvHom P = k • P) ∧ ∀ P, (k ^ 2 + k + 1) • P = 0 := by
  obtain ⟨g, hg⟩ := IsAddCyclic.exists_generator (α := secp256k1.toAffine.Point)
  obtain ⟨k, hk⟩ := AddSubgroup.mem_zmultiples_iff.mp (hg (glvHom g))
  -- `glvHom` is multiplication by `k`: check it on the generator, extend `ℤ`-linearly.
  have hscalar : ∀ P, glvHom P = k • P := by
    intro P
    obtain ⟨a, ha⟩ := AddSubgroup.mem_zmultiples_iff.mp (hg P)
    rw [← ha, map_zsmul, ← hk, smul_smul, smul_smul, mul_comm]
  refine ⟨k, hscalar, ?_⟩
  intro P
  -- Feed `φ² + φ + 1 = 0` through the scalar: `k²·P + k·P + P = 0`.
  have hmin := DFunLike.congr_fun glvHom_minpoly P
  simp only [AddMonoidHom.add_apply, AddMonoidHom.comp_apply, AddMonoidHom.id_apply,
    AddMonoidHom.zero_apply] at hmin
  rw [show glvHom P = k • P from hscalar P] at hmin
  rw [show glvHom (k • P) = k • (k • P) from hscalar (k • P)] at hmin
  have hexp : (k ^ 2 + k + 1) • P = k • (k • P) + k • P + P := by
    rw [add_zsmul, add_zsmul, one_zsmul, pow_two, ← smul_smul]
  rw [hexp]; exact hmin

end Ecdlp.Curve
