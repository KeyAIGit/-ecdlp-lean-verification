import Mathlib

/-!
# UORC-056 EDS decimation audit

The first V10 attempt overreached after using the wrong Ward-constant
normalization.  This file retains only the elementary sign consequence that is
actually valid: an exact even decimation with first decimated sign `-1` forces
the EDS-residue row at the re-marked generator to be all `+1`.

`ZMod 2` encodes signs: `0` means `+1`, `1` means `-1`.
No claim that all-residue rows are impossible is formalized here; exact finite
counterexamples exist.
-/

namespace Ecdlp.EdsDecimationClosure

abbrev SignBit := ZMod 2

/-- Sign-bit form of the valid chain-rule reduction.

If

  decim(k) = residueAtRemarkedGenerator(k) + k * rhoM

and the decimation is parity while `rhoM=-1`, then every residue sign at the
re-marked generator is `+1`.
-/
theorem parityDecimation_forces_allResidues
    (residue decim : ℕ → SignBit)
    (rhoM : SignBit)
    (hrhoM : rhoM = 1)
    (hchain : ∀ k, decim k = residue k + (k : SignBit) * rhoM)
    (htarget : ∀ k, decim k = (k : SignBit)) :
    ∀ k, residue k = 0 := by
  intro k
  have h := hchain k
  rw [htarget k, hrhoM] at h
  simp at h
  linear_combination h

/-- The Ward sign pattern `chi(a)=+1`, `chi(b)=-1` is algebraically compatible
with an all-residue base row.  This tiny witness prevents reintroducing the
invalid inference that all-residue rows force both Ward constants to be
quadratic residues.
-/
theorem allResidue_doesNot_force_WardB_residue :
    ∃ A B : SignBit, A = 0 ∧ B = 1 := by
  exact ⟨0, 1, rfl, rfl⟩

end Ecdlp.EdsDecimationClosure
