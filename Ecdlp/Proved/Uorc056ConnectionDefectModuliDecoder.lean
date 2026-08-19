import Mathlib

/-!
# UORC-056 C53 connection defect and moduli-tangent decoder boundary

This file kernel-checks the elementary algebra used by C53.  It does not
formalize elliptic curves as group schemes, finite-etale lifting, the
finite-field replay, or an unrestricted circuit lower bound.
-/

namespace Ecdlp.Uorc056ConnectionDefectModuliDecoder

/-- Vertical scalar of the connection defect at one multiplier. -/
def connectionDefect {R : Type*} [Ring R]
    (cImage multiplier cSource : R) : R :=
  cImage - multiplier * cSource

/-- Connection defects form the expected multiplier cocycle.  C53 uses this
    identity only over commutative base fields. -/
theorem connectionDefect_cocycle
    {R : Type*} [CommRing R]
    (cAB cB cP a b : R) :
    connectionDefect cAB (a * b) cP
      = connectionDefect cAB a cB
        + a * connectionDefect cB b cP := by
  simp only [connectionDefect]
  ring

/-- Changing the connection by a vertical gauge changes the defect by the
    corresponding coboundary. -/
theorem connectionDefect_gauge
    {R : Type*} [CommRing R]
    (cQ cG fQ fG k : R) :
    connectionDefect (cQ + fQ) k (cG + fG)
      - connectionDefect cQ k cG
      = fQ - k * fG := by
  simp only [connectionDefect]
  ring

/-- With an anchor-zero gauge, the defect is just the direct query state. -/
theorem anchorZeroDefect
    {R : Type*} [Ring R]
    (cQ k : R) :
    connectionDefect cQ k 0 = cQ := by
  simp [connectionDefect]

/-- A nonzero-anchor exact defect reveals the full multiplier in the field. -/
theorem nonzeroAnchorDefectRevealsMultiplier
    {K : Type*} [Field K]
    (cQ cG delta k : K)
    (hcG : cG ≠ 0)
    (hdelta : delta = connectionDefect cQ k cG) :
    (cQ - delta) / cG = k := by
  apply (div_eq_iff hcG).2
  rw [hdelta]
  simp [connectionDefect]

/-- The charged tangent pair factors into an ordinary endpoint coordinate
    ratio and a sign-neutral moduli factor. -/
theorem chargedNeutralFactorization
    {K : Type*} [Field K]
    (rq rg xq xg yq yg : K)
    (hrg : rg ≠ 0) (hxq : xq ≠ 0) (hxg : xg ≠ 0)
    (hyq : yq ≠ 0) (hyg : yg ≠ 0) :
    ((rq / (xq * yq)) / (rg / (xg * yg)))
        * ((xq / yq) / (xg / yg))
      = (rq / rg) * (yg ^ 2 / yq ^ 2) := by
  field_simp

/-- Substituting the curve equations turns the neutral factor into the C53
    `T,R` normal form. -/
theorem chargedNeutralCurveForm
    {K : Type*} [Field K]
    (rq rg tq tg yq yg b : K)
    (_hrg : rg ≠ 0) (_hyq : yq ≠ 0)
    (_hyg : yg ≠ 0)
    (hq : yq ^ 2 = tq + b)
    (hg : yg ^ 2 = tg + b) :
    (rq / rg) * (yg ^ 2 / yq ^ 2)
      = (rq / rg) * ((tg + b) / (tq + b)) := by
  rw [hq, hg]

/-- Equal public states cannot decode opposite target signs in characteristic
    different from two. -/
theorem equalStateCannotDecodeOpposite
    {S K : Type*} [Field K]
    (decode : S → K) (left right : S)
    (hsame : left = right)
    (hleft : decode left = 1)
    (hright : decode right = -1)
    (htwo : (2 : K) ≠ 0) :
    False := by
  have hone : (1 : K) = -1 := by
    calc
      (1 : K) = decode left := hleft.symm
      _ = decode right := by rw [hsame]
      _ = -1 := hright
  have hz : (2 : K) = 0 := by
    calc
      (2 : K) = 1 - (-1) := by ring
      _ = 0 := sub_eq_zero.mpr hone
  exact htwo hz

/-- Public secp256k1 constants satisfy `n < p`, so a recovered base-field
    multiplier in `[1,n-1]` is the canonical scalar. -/
def secpP : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

def secpN : Nat :=
  0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

theorem secpOrderBelowField : secpN < secpP := by
  native_decide

end Ecdlp.Uorc056ConnectionDefectModuliDecoder
