import Mathlib
import Ecdlp.Secp256k1Verified
import Ecdlp.Proved.SevenNonResidue
import Ecdlp.Proved.RelativeResidueGauge
import Ecdlp.Proved.GlvNormalizationRigidityScope

/-!
# Arithmetic boundary for the Eisenstein root-phase screen

This file records the closed arithmetic facts used by
`EISENSTEIN-ROOT-PHASE-001`. It also imports the theorem-only parity-lift
support modules so that the isolated research branch kernel-checks them through
the existing `Ecdlp.lean` root. It does not construct an EDS-residue oracle,
formalize the extension-field cube-root lift, or make an asymptotic claim.
-/

namespace Ecdlp.ParityLift

/-- For coefficient residues modulo two, the Eisenstein norm
`a^2-a*b+b^2` vanishes only at the zero pair. Thus an even integral
Eisenstein norm forces both coefficients to be even and is consequently
divisible by four. The statement is a closed four-case finite check. -/
theorem eisensteinNorm_mod_two_zero_iff (a b : Fin 2) :
    ((((a.val : ℤ) ^ 2 - (a.val : ℤ) * (b.val : ℤ) + (b.val : ℤ) ^ 2) % 2 = 0)
      ↔ a = 0 ∧ b = 0) := by
  revert a b
  native_decide

/-- The secp256k1 field prime lies in the exact congruence class used by the
canonical `F_{p^2}` cube-subgroup lift. -/
theorem secp256k1_p_mod_thirtySix : Secp256k1.p % 36 = 7 := by
  native_decide

/-- In particular `p = 7 mod 9`, so `v_3(p^2-1)=1`. -/
theorem secp256k1_p_mod_nine : Secp256k1.p % 9 = 7 := by
  native_decide

/-- The cube subgroup of `F_{p^2}^*` has order prime to three for the fixed
secp256k1 prime. This is the arithmetic reason cubing is invertible on that
subgroup and the selected cube root is canonical. -/
theorem secp256k1_cubeSubgroupOrder_mod_three :
    (((Secp256k1.p ^ 2 - 1) / 3) % 3) = 1 := by
  native_decide

/-- Re-export the already proved nonsplitting input used to construct
`F_p[c]/(c^2-7)`. -/
theorem secp256k1_seven_nonsplit :
    ¬ IsSquare (7 : ZMod Secp256k1.p) :=
  Ecdlp.Curve.secp256k1_seven_not_isSquare

end Ecdlp.ParityLift
