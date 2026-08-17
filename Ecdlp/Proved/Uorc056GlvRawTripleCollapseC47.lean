import Mathlib

/-!
# UORC-056 C47 GLV raw-triple collapse

The executable replay establishes on the declared j=0 elliptic curves

    Phi(alpha Q)   = beta * Phi(Q),
    Phi(alpha^2 Q) = beta^2 * Phi(Q).

This file kernel-checks the elementary algebraic consequence: when
`beta^2 + beta + 1 = 0`, the three GLV values form one rank-one public state,
their discrete C3 Fourier transform has only one nonzero mode, and their
product is the cube of the first value.

The division-polynomial CM-weight induction and pointwise elliptic-curve
identities are replayed by Python and are not mislabeled here as fully
formalized. No nonlinear decoder of `Phi`, parity oracle, or unrestricted
circuit lower bound is claimed.
-/

namespace Ecdlp.Uorc056GlvRawTripleCollapseC47


def glvTriple
    {R : Type*} [CommRing R]
    (beta phi : R) : R × R × R :=
  (phi, beta * phi, beta ^ 2 * phi)


theorem cube_eq_one_of_relation
    {R : Type*} [CommRing R]
    (beta : R)
    (hbeta : beta ^ 2 + beta + 1 = 0) :
    beta ^ 3 = 1 := by
  have hfactor : beta ^ 3 - 1 = (beta - 1) * (beta ^ 2 + beta + 1) := by
    ring
  rw [hbeta, mul_zero] at hfactor
  exact sub_eq_zero.mp hfactor


theorem glvModeZero
    {R : Type*} [CommRing R]
    (beta phi : R)
    (hbeta : beta ^ 2 + beta + 1 = 0) :
    phi + beta * phi + beta ^ 2 * phi = 0 := by
  calc
    phi + beta * phi + beta ^ 2 * phi =
        (beta ^ 2 + beta + 1) * phi := by ring
    _ = 0 := by rw [hbeta, zero_mul]


theorem glvModeOne
    {R : Type*} [CommRing R]
    (beta phi : R)
    (hbeta : beta ^ 2 + beta + 1 = 0) :
    phi + beta ^ 2 * (beta * phi) + beta * (beta ^ 2 * phi) =
      3 * phi := by
  have hcube := cube_eq_one_of_relation beta hbeta
  calc
    phi + beta ^ 2 * (beta * phi) + beta * (beta ^ 2 * phi) =
        (1 + beta ^ 3 + beta ^ 3) * phi := by ring
    _ = 3 * phi := by rw [hcube]; ring


theorem glvModeTwo
    {R : Type*} [CommRing R]
    (beta phi : R)
    (hbeta : beta ^ 2 + beta + 1 = 0) :
    phi + beta * (beta * phi) + beta ^ 2 * (beta ^ 2 * phi) = 0 := by
  have hcube := cube_eq_one_of_relation beta hbeta
  have hfour : beta ^ 4 = beta := by
    calc
      beta ^ 4 = beta ^ 3 * beta := by ring
      _ = beta := by rw [hcube, one_mul]
  calc
    phi + beta * (beta * phi) + beta ^ 2 * (beta ^ 2 * phi) =
        (1 + beta ^ 2 + beta ^ 4) * phi := by ring
    _ = (beta ^ 2 + beta + 1) * phi := by rw [hfour]; ring
    _ = 0 := by rw [hbeta, zero_mul]


theorem glvTripleProduct
    {R : Type*} [CommRing R]
    (beta phi : R)
    (hbeta : beta ^ 2 + beta + 1 = 0) :
    phi * (beta * phi) * (beta ^ 2 * phi) = phi ^ 3 := by
  have hcube := cube_eq_one_of_relation beta hbeta
  calc
    phi * (beta * phi) * (beta ^ 2 * phi) = beta ^ 3 * phi ^ 3 := by ring
    _ = phi ^ 3 := by rw [hcube, one_mul]


/-- The first coordinate recovers the underlying state, while the other two
coordinates are fixed public rescalings. -/
theorem glvTriple_first
    {R : Type*} [CommRing R]
    (beta phi : R) :
    (glvTriple beta phi).1 = phi := by
  rfl


def secpP : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F


def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def secpBeta : Nat :=
  0x7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE


def secpLambda : Nat :=
  0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72


theorem secpBetaCube : secpBeta ^ 3 % secpP = 1 := by
  native_decide


theorem secpBetaNontrivial : secpBeta % secpP ≠ 1 := by
  native_decide


theorem secpLambdaRelation :
    (secpLambda ^ 2 + secpLambda + 1) % secpN = 0 := by
  native_decide


theorem declaredPointActionChecks : 294 * 2 = 588 := by
  native_decide


theorem declaredFourierChecks : 294 * 3 = 882 := by
  native_decide

end Ecdlp.Uorc056GlvRawTripleCollapseC47
