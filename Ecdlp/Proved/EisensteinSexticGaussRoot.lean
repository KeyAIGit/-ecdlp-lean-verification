import Mathlib

/-!
# Eisenstein sextic Gauss root

This file formalizes the elementary algebraic identities used by
`EISENSTEIN-SEXTIC-GAUSS-ROOT-036`.

A normalized projector scaled by an inverse sextic character has cube equal to
the quadratic component and sixth power equal to one.  A sextic character also
splits into its cubic and quadratic components as `psi = psi^4 * psi^3`.

The file does not formalize elliptic Gauss sums, complex multiplication, Hecke
characters, modular forms, secp256k1 nonvanishing, or complexity.
-/

namespace Ecdlp.ParityLift

/-- Normalizing a nonzero sextic eigenprojector and cubing recovers its
quadratic component. -/
theorem normalizedSexticCube_recoversQuadratic
    {K : Type*} [Field K]
    (projected base psiInv quadratic : K)
    (hprojected : projected = psiInv * base)
    (hbase : base ≠ 0)
    (hcube : psiInv ^ 3 = quadratic) :
    (projected / base) ^ 3 = quadratic := by
  have hratio : projected / base = psiInv := by
    rw [hprojected]
    field_simp
  rw [hratio, hcube]

/-- The sixth power of a sextic eigenprojector is generator-blind. -/
theorem sexticProjector_sixthPower_eq_base
    {K : Type*} [Field K]
    (projected base psiInv : K)
    (hprojected : projected = psiInv * base)
    (hsix : psiInv ^ 6 = 1) :
    projected ^ 6 = base ^ 6 := by
  rw [hprojected]
  calc
    (psiInv * base) ^ 6 = psiInv ^ 6 * base ^ 6 := by ring
    _ = base ^ 6 := by rw [hsix, one_mul]

/-- A sextic character is the product of its order-three and order-two
components. -/
theorem sextic_eq_cubic_mul_quadratic
    {K : Type*} [Field K]
    (psi : K)
    (hsix : psi ^ 6 = 1) :
    psi = psi ^ 4 * psi ^ 3 := by
  calc
    psi = psi ^ 6 * psi := by rw [hsix, one_mul]
    _ = psi ^ 4 * psi ^ 3 := by ring

end Ecdlp.ParityLift
