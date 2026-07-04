import Mathlib

/-!
# A dependence relation among points recovers the discrete logarithm

The algebraic core of the Jacobson–Xedni "point-dependence" idea, stated as a neutral
reduction (no attack procedure, just the underlying group identity): if a target point
`Q = x • P` and the base point `P` satisfy a nontrivial integer relation `a • P + b • Q = 0`
whose `Q`-coefficient `b` is invertible modulo `n := addOrderOf P`, then the discrete
logarithm `x = log_P Q` is determined modulo `n` by `x ≡ -a · b⁻¹`.

Corpus claim `jacobson-xedni-dependence-recovers-log-003`. Generated as a Layer-3 target
and closed by the Lean kernel (`addOrderOf_dvd_iff_zsmul_eq_zero` + `ZMod` arithmetic).
-/

namespace Ecdlp

/-- **Dependence relation recovers the discrete log.** For `Q = x • P` in any additive
commutative group, a nontrivial integer relation `a • P + b • Q = 0` with `b` invertible
modulo `n = addOrderOf P` pins down `x ≡ -a · b⁻¹ (mod n)`. -/
theorem jacobson_xedni_dependence_recovers_log
    {G : Type*} [AddCommGroup G] (P Q : G) (x a b : ℤ)
    (hQ : Q = x • P) (hrel : a • P + b • Q = 0)
    (hu : IsUnit ((b : ZMod (addOrderOf P)))) :
    (x : ZMod (addOrderOf P))
      = (-(a : ZMod (addOrderOf P))) * Ring.inverse ((b : ZMod (addOrderOf P))) := by
  subst hQ
  have hz : (a + b * x) • P = 0 := by
    have h := hrel; rw [smul_smul, ← add_smul] at h; exact h
  have hdvd : (addOrderOf P : ℤ) ∣ (a + b * x) := by
    rwa [← addOrderOf_dvd_iff_zsmul_eq_zero] at hz
  have hcast : (a : ZMod (addOrderOf P)) + b * x = 0 := by
    have h0 : ((a + b * x : ℤ) : ZMod (addOrderOf P)) = 0 := by
      rw [ZMod.intCast_zmod_eq_zero_iff_dvd]; exact_mod_cast hdvd
    push_cast at h0; linear_combination h0
  have hbx : (b : ZMod (addOrderOf P)) * x = -a := by linear_combination hcast
  have hinv : Ring.inverse (b : ZMod (addOrderOf P)) * b = 1 := Ring.inverse_mul_cancel _ hu
  calc (x : ZMod (addOrderOf P))
      = Ring.inverse (b : ZMod (addOrderOf P)) * b * x := by rw [hinv, one_mul]
    _ = Ring.inverse (b : ZMod (addOrderOf P)) * ((b : ZMod (addOrderOf P)) * x) := by ring
    _ = Ring.inverse (b : ZMod (addOrderOf P)) * (-a) := by rw [hbx]
    _ = (-(a : ZMod (addOrderOf P))) * Ring.inverse (b : ZMod (addOrderOf P)) := by ring

end Ecdlp
