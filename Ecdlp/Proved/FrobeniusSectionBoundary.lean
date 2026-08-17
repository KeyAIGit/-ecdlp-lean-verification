import Mathlib
import Ecdlp.Proved.GlvNormalizationRigidityScope

/-!
# Mixed-weight and Frobenius-section boundary

This file records the algebraic core of `GLOBAL-MONODROMY-SECTION-009`.
It does not formalize generalized division polynomials, the Frobenius isogeny,
line bundles, or a discrete-log algorithm.

The proved statements isolate two exact facts.

1. Once two sections are compared by a public trivialization, a pencil is one
   reference section multiplied by a public weight-zero coefficient.  Thus a
   mixed-weight pencil can cancel the standard GLV carry only when that
   coefficient itself supplies the carry.
2. On a Frobenius-fixed rational subgroup, `pi-1` kills every point and `pi+1`
   acts as doubling.  At the residual-weight level, an odd-degree kernel jet
   has odd weight, while the corresponding nonkernel quotient has weight
   `N+1`, which is even.
-/

namespace Ecdlp.ParityLift

/-- A public comparison `A = B * ratio` turns a seemingly mixed-weight pencil
into the reference section `B` times a weight-zero coefficient. -/
theorem pencil_factor_of_public_comparison
    {R : Type*} [CommRing R] (A B ratio c : R)
    (hcompare : A = B * ratio) :
    A + c * B = B * (ratio + c) := by
  rw [hcompare]
  ring

/-- In an additive sign law, if the reference section contributes
`carry + residue` and the final output is `residue`, the extra coefficient must
contribute `-carry`. -/
theorem coefficient_must_cancel_carry
    {A : Type*} [AddCommGroup A]
    (section coefficient carry residue : A)
    (hsection : section = carry + residue)
    (houtput : section + coefficient = residue) :
    coefficient = -carry := by
  calc
    coefficient = -(carry + residue) + ((carry + residue) + coefficient) := by
      abel
    _ = -(carry + residue) + residue := by
      rw [← hsection, houtput]
    _ = -carry := by
      abel

/-- For binary characters, negation is the identity.  Hence a coefficient that
turns `carry + residue` into `residue` must itself equal `carry`. -/
theorem binary_coefficient_must_supply_carry
    (section coefficient carry residue : ZMod 2)
    (hsection : section = carry + residue)
    (houtput : section + coefficient = residue) :
    coefficient = carry := by
  have h := coefficient_must_cancel_carry
    section coefficient carry residue hsection houtput
  simpa using h

/-- Abstract fixed-point form of the Frobenius-minus-one collapse. -/
theorem endomorphism_sub_identity_on_fixed_point
    {A : Type*} [AddCommGroup A]
    (F : A →+ A) (Q : A) (hfixed : F Q = Q) :
    F Q - Q = 0 := by
  rw [hfixed, sub_self]

/-- Abstract fixed-point form of the Frobenius-plus-one restriction: it is
ordinary doubling on the fixed subgroup. -/
theorem endomorphism_add_identity_on_fixed_point
    {A : Type*} [AddCommMonoid A]
    (F : A →+ A) (Q : A) (hfixed : F Q = Q) :
    F Q + Q = 2 • Q := by
  rw [hfixed, two_nsmul]

/-- An odd degree `N` is represented by the evenness of `N-1`.  The leading
kernel jet therefore has odd residual weight. -/
theorem odd_degree_kernelJetWeight
    (N : ℤ) (hodd : Even (N - 1)) :
    Even (N - 1) :=
  hodd

/-- For a nonkernel generalized multiplication quotient, the two residual EDS
sources have total weight `N+1`.  If `N` is odd, this weight is even. -/
theorem odd_degree_nonkernelResidualWeight_even
    (N : ℤ) (hodd : Even (N - 1)) :
    Even (N + 1) := by
  rcases hodd with ⟨r, hr⟩
  refine ⟨r + 1, ?_⟩
  rw [show N = (N - 1) + 1 by ring, hr]
  ring

/-- Combining compatibility with an odd kernel-jet residual weight reproduces
exactly the basic GLV carry multiplier. -/
theorem compatibleFrobeniusKernelJet_forcesBasicCarry
    (epsilon a b gamma c : ℤ)
    (hcompat : residualWeightCompatible epsilon a b)
    (hkernelOdd : Even (epsilon - 1)) :
    Even (((a + b) * gamma + c) - (gamma + c)) :=
  compatibleOddResidual_forcesBasicCarry
    epsilon a b gamma c hcompat hkernelOdd

/-- If a nonkernel Frobenius section has residual weight `N+1` with odd `N`,
that residual weight is even and cannot be the required odd `R3` anchor. -/
theorem odd_degree_nonkernel_cannot_have_oddResidual
    (N : ℤ) (hodd : Even (N - 1)) :
    ¬ Even ((N + 1) - 1) := by
  have heven : Even (N + 1) :=
    odd_degree_nonkernelResidualWeight_even N hodd
  intro hoddWeight
  have hone : Even (1 : ℤ) := by
    rcases heven with ⟨r, hr⟩
    rcases hoddWeight with ⟨s, hs⟩
    refine ⟨r - s, ?_⟩
    calc
      (1 : ℤ) = (N + 1) - ((N + 1) - 1) := by ring
      _ = (r - s) + (r - s) := by rw [hr, hs]; ring
  exact Int.not_even_one hone

end Ecdlp.ParityLift
