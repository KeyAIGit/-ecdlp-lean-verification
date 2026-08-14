import Mathlib

/-!
# UORC-056 V16 sector-factor reconciliation

This file kernel-checks the ring identities and the fixed natural-number
arithmetic used by V16.

It does not formalize elliptic curves, polynomial interpolation, the floor-sum
derivation, root-count transfer, or a public evaluator. Those statements remain
separate executable and mathematical obligations.
-/

namespace Ecdlp.SectorFactorReconciliation

variable {R : Type*} [CommRing R]

/-- The complementary sector bit is parity times the three-sign carry. -/
theorem sector_eq_parity_mul_carry
    (s0 s1 s2 : R)
    (h0 : s0 ^ 2 = 1) :
    s1 * s2 = s0 * (s0 * s1 * s2) := by
  calc
    s1 * s2 = (s0 ^ 2) * (s1 * s2) := by rw [h0]; ring
    _ = s0 * (s0 * s1 * s2) := by ring

/-- The product of three point-function/residue bridges splits into the
public C3 norm and the odd EDS residue aggregate. -/
theorem carry_residue_bridge
    (s0 s1 s2 C0 C1 C2 r0 r1 r2 : R)
    (h0 : s0 = C0 * r0)
    (h1 : s1 = C1 * r1)
    (h2 : s2 = C2 * r2) :
    s0 * s1 * s2 = (C0 * C1 * C2) * (r0 * r1 * r2) := by
  rw [h0, h1, h2]
  ring

/-- If both the new carry and the legacy public/residue bridge equal
`C3 * R3`, and `R3` is a sign, then the two carry names are identical. -/
theorem legacy_carry_reconciliation
    (c g C3 R3 : R)
    (hc : c = C3 * R3)
    (hg : C3 = g * R3)
    (hR3 : R3 ^ 2 = 1) :
    c = g := by
  rw [hc, hg]
  calc
    (g * R3) * R3 = g * (R3 ^ 2) := by ring
    _ = g := by rw [hR3]; ring

/-- The sector bit is the two-rotation point-function/residue product. -/
theorem sector_residue_pair
    (s1 s2 C1 C2 r1 r2 : R)
    (h1 : s1 = C1 * r1)
    (h2 : s2 = C2 * r2) :
    s1 * s2 = (C1 * C2) * (r1 * r2) := by
  rw [h1, h2]
  ring

/-- Every idempotent gives a plus/minus-one involution by `J = 2e - 1`. -/
theorem involution_of_idempotent
    (e : R)
    (he : e ^ 2 = e) :
    (2 * e - 1) ^ 2 = 1 := by
  calc
    (2 * e - 1) ^ 2 = 4 * e ^ 2 - 4 * e + 1 := by ring
    _ = 1 := by rw [he]; ring

/-- At a positive-sector root `Kplus = 0`, the factor witness numerator
`Kminus - Kplus` equals its denominator `Kminus + Kplus`. -/
theorem rationalWitnessAtPlus
    (Kplus Kminus : R)
    (hplus : Kplus = 0) :
    Kminus - Kplus = Kminus + Kplus := by
  rw [hplus]
  ring

/-- At a negative-sector root `Kminus = 0`, the same numerator is the
negative of its denominator. -/
theorem rationalWitnessAtMinus
    (Kplus Kminus : R)
    (hminus : Kminus = 0) :
    Kminus - Kplus = -(Kminus + Kplus) := by
  rw [hminus]
  ring

/-- Elementary arithmetic core of the direct field-valued rational degree
barrier: both sign-fiber root counts bound the common degree. -/
theorem directSignDegreeLowerBound
    (plusRoots minusRoots degree : Nat)
    (hplus : plusRoots <= degree)
    (hminus : minusRoots <= degree) :
    max plusRoots minusRoots <= degree :=
  max_le hplus hminus

def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def secpSectorCorrelation : Nat := 208

def secpSectorPlusDegree : Nat :=
  28948022309329048855892746252171976963209391069768726095651290785379540373636

def secpSectorMinusDegree : Nat :=
  28948022309329048855892746252171976963209391069768726095651290785379540373532

def secpUniformBranchDegree : Nat :=
  14474011154664524427946373126085988481604695534884363047825645392689770186870

def secpMinorityBranchDegree : Nat :=
  14474011154664524427946373126085988481604695534884363047825645392689770186766

def secpDirectRationalDegreeLowerBound : Nat :=
  secpSectorPlusDegree

theorem secpSectorFactorPartition :
    secpSectorPlusDegree + secpSectorMinusDegree = (secpN - 1) / 2 := by
  native_decide

theorem secpSectorFactorDifference :
    secpSectorPlusDegree - secpSectorMinusDegree = 104 := by
  native_decide

theorem secpCorrelationMatchesFactorDifference :
    2 * (secpSectorPlusDegree - secpSectorMinusDegree)
      = secpSectorCorrelation := by
  native_decide

theorem secpFourBranchPartition :
    secpUniformBranchDegree + 3 * secpMinorityBranchDegree
      = (secpN - 1) / 2 := by
  native_decide

theorem secpPlusBranchDecomposition :
    secpUniformBranchDegree + secpMinorityBranchDegree
      = secpSectorPlusDegree := by
  native_decide

theorem secpMinusBranchDecomposition :
    2 * secpMinorityBranchDegree = secpSectorMinusDegree := by
  native_decide

theorem secpDirectDegreeAtLeastTwoPow253 :
    2 ^ 253 <= secpDirectRationalDegreeLowerBound := by
  native_decide

theorem secpDirectDegreeBelowTwoPow254 :
    secpDirectRationalDegreeLowerBound < 2 ^ 254 := by
  native_decide

end Ecdlp.SectorFactorReconciliation
