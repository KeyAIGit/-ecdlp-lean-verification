import Mathlib

/-!
# UORC-056 EDS decimation closure sign skeleton

This file formalizes the elementary sign algebra used in V10 after the
classical division-polynomial identities have been supplied.

`ZMod 2` encodes quadratic-character signs: `0` means `+1`, `1` means `-1`.
The file does not formalize elliptic curves, division polynomials, Ward's
quasi-periodicity, or the chain rule themselves. Those are source-locked in the
V10 mathematical note and independently replayed on frozen curves.
-/

namespace Ecdlp.EdsDecimationClosure

abbrev SignBit := ZMod 2

/-- For an even-index decimation, if the decimated sign is parity and the
first decimated term has sign `-1`, the multiplication chain rule forces the
residue row at the re-marked generator to be identically `+1`.

The hypothesis `hchain` is the sign-bit form

  decim(k) = sigma(k) + k * rhoM,

which comes from

  psi_(mk)(G) = psi_k([m]G) * psi_m(G)^(k^2)

and `k^2 = k (mod 2)`.
-/
theorem parityDecimation_forces_allResidues
    (sigma decim : ℕ → SignBit)
    (rhoM : SignBit)
    (hrhoM : rhoM = 1)
    (hchain : ∀ k, decim k = sigma k + (k : SignBit) * rhoM)
    (htarget : ∀ k, decim k = (k : SignBit)) :
    ∀ k, sigma k = 0 := by
  intro k
  have h := hchain k
  rw [htarget k, hrhoM] at h
  simp at h
  linear_combination h

/-- Ward quasi-periodicity together with one specialized EDS recurrence cannot
coexist with an all-residue row when the sign of `-1` is nontrivial.

`A` and `B` are the sign bits of Ward's constants `a` and `b`.  Under
`rho_2 = rho_(n-2) = rho_(n-1) = +1`, their defining formulas force
`A=B=0`.  Ward at `(s,k)=(1,1)` and `(2,1)` then forces the signs at `n+1`
and `2n+1` to be zero.  The recurrence

  psi_(2n+1) = - psi_(n+1)^3 psi_(n-1)

forces the latter sign to be one, a contradiction.
-/
theorem wardRecurrence_forbids_allResidues
    (rho : ℕ → SignBit)
    (n : ℕ)
    (A B : SignBit)
    (hrho1 : rho 1 = 0)
    (hrho2 : rho 2 = 0)
    (hrhoNm2 : rho (n - 2) = 0)
    (hrhoNm1 : rho (n - 1) = 0)
    (hA : A = rho (n - 2) + rho (n - 1) + rho 2)
    (hB : B = 2 * rho (n - 1) + rho 2 + rho (n - 2))
    (hWard1 : rho (n + 1) = A + B + rho 1)
    (hWard2 : rho (2 * n + 1) = 2 * A + 4 * B + rho 1)
    (hRecurrence :
      rho (2 * n + 1) = 1 + 3 * rho (n + 1) + rho (n - 1)) :
    False := by
  have hAzero : A = 0 := by
    rw [hA, hrhoNm2, hrhoNm1, hrho2]
    norm_num
  have hBzero : B = 0 := by
    rw [hB, hrhoNm1, hrho2, hrhoNm2]
    norm_num
  have hNp1 : rho (n + 1) = 0 := by
    rw [hWard1, hAzero, hBzero, hrho1]
    norm_num
  have h2Np1 : rho (2 * n + 1) = 0 := by
    rw [hWard2, hAzero, hBzero, hrho1]
    norm_num
  have h2Np1neg : rho (2 * n + 1) = 1 := by
    rw [hRecurrence, hNp1, hrhoNm1]
    norm_num
  rw [h2Np1] at h2Np1neg
  norm_num at h2Np1neg

/-- A compact corollary exposing the three-sign certificate used by the exact
replay.  If Ward's two consequences and the specialized recurrence hold with
`chi(-1)=-1`, the three neighboring residue signs cannot all be `+1`.
-/
theorem wardThreeSignCertificate
    (rho : ℕ → SignBit)
    (n : ℕ)
    (A B : SignBit)
    (hrho1 : rho 1 = 0)
    (hA : A = rho (n - 2) + rho (n - 1) + rho 2)
    (hB : B = 2 * rho (n - 1) + rho 2 + rho (n - 2))
    (hWard1 : rho (n + 1) = A + B + rho 1)
    (hWard2 : rho (2 * n + 1) = 2 * A + 4 * B + rho 1)
    (hRecurrence :
      rho (2 * n + 1) = 1 + 3 * rho (n + 1) + rho (n - 1)) :
    ¬ (rho 2 = 0 ∧ rho (n - 2) = 0 ∧ rho (n - 1) = 0) := by
  rintro ⟨hrho2, hrhoNm2, hrhoNm1⟩
  exact wardRecurrence_forbids_allResidues
    rho n A B hrho1 hrho2 hrhoNm2 hrhoNm1
    hA hB hWard1 hWard2 hRecurrence

end Ecdlp.EdsDecimationClosure
