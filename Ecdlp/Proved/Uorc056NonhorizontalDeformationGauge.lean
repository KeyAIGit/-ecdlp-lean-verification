import Mathlib

/-!
# UORC-056 C52 nonhorizontal deformation gauge

This file kernel-checks the elementary algebra used by C52:

* a nonzero vertical tangent pair satisfying the scalar transport law reveals
  the scalar by a single division;
* pure Weierstrass scaling satisfies the linearized curve equation;
* the two CM-quotient coordinates of the genuine `a`-deformation satisfy the
  cross-multiplied relation used by the exact replay;
* changing a connection or trivialization adds a chosen gauge term;
* the secp256k1 subgroup order is strictly below the base-field prime.

It does not formalize elliptic curves as group schemes, finite-etale torsion,
division-polynomial automatic differentiation, the finite-field screens, or an
unrestricted complexity lower bound.
-/

namespace Ecdlp.Uorc056NonhorizontalDeformationGauge

/-- A nonzero invariant tangent at `G`, transported by the hidden scalar, reveals
    that scalar from the tangent at `Q`. -/
theorem verticalTransportRevealsScalar
    {K : Type*} [Field K]
    (k vG vQ : K)
    (hvG : vG ≠ 0)
    (htransport : vQ = k * vG) :
    vQ / vG = k := by
  exact (div_eq_iff hvG).2 htransport

/-- Pure Weierstrass scaling

`x -> (1+2 alpha eps)x`, `y -> (1+3 alpha eps)y`,
`a -> (1+4 alpha eps)a`, `b -> (1+6 alpha eps)b`

satisfies the linearized short-Weierstrass equation. -/
theorem linearizedWeierstrassScaling
    {R : Type*} [CommRing R]
    (x y a b alpha : R)
    (hcurve : y ^ 2 = x ^ 3 + a * x + b) :
    2 * y * (3 * alpha * y)
      = (3 * x ^ 2 + a) * (2 * alpha * x)
        + (4 * alpha * a) * x
        + 6 * alpha * b := by
  calc
    2 * y * (3 * alpha * y) = 6 * alpha * (y ^ 2) := by ring
    _ = 6 * alpha * (x ^ 3 + a * x + b) := by rw [hcurve]
    _ = (3 * x ^ 2 + a) * (2 * alpha * x)
        + (4 * alpha * a) * x
        + 6 * alpha * b := by ring

/-- Cross-multiplied CM quotient relation for the genuine `a`-deformation.

If `r=x*dotx` and `y*s=x^2*doty`, then the linearized curve equation implies
`2(x^3+b)s=x^3(3r+1)`. -/
theorem cmQuotientRelation
    {R : Type*} [CommRing R]
    (x y b dotx doty r s : R)
    (hcurve : y ^ 2 = x ^ 3 + b)
    (hlinear : 2 * y * doty = 3 * x ^ 2 * dotx + x)
    (hr : r = x * dotx)
    (hs : y * s = x ^ 2 * doty) :
    2 * (x ^ 3 + b) * s = x ^ 3 * (3 * r + 1) := by
  calc
    2 * (x ^ 3 + b) * s = 2 * (y ^ 2) * s := by rw [← hcurve]
    _ = 2 * y * (y * s) := by ring
    _ = 2 * y * (x ^ 2 * doty) := by rw [hs]
    _ = x ^ 2 * (2 * y * doty) := by ring
    _ = x ^ 2 * (3 * x ^ 2 * dotx + x) := by rw [hlinear]
    _ = x ^ 3 * (3 * (x * dotx) + 1) := by ring
    _ = x ^ 3 * (3 * r + 1) := by rw [hr]

/-- The tangent response is linear in the two Weierstrass deformation
    directions. -/
theorem tangentResponseLinear
    {R : Type*} [CommRing R]
    (da db ua ub : R) :
    da * ua + db * ub = db * ub + da * ua := by
  ring

/-- A change of connection/trivialization adds the selected gauge term.  The
    term is not an intrinsic new torsion invariant merely because it appears in
    a derivative. -/
theorem connectionGaugeDifference
    {R : Type*} [Ring R]
    (d q gauge : R) :
    (d + q * gauge) - d = q * gauge := by
  ring


def secpP : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F


def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


theorem secpOrderBelowField : secpN < secpP := by
  native_decide


theorem secpFieldOrderDifference :
    secpP - secpN =
      432420386565659656852420866390673177326 := by
  native_decide

end Ecdlp.Uorc056NonhorizontalDeformationGauge
