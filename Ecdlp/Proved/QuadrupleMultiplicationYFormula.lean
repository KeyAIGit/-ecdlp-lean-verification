/-
# Multiplication-by-4 y-coordinate for secp256k1 in division-polynomial form (N7 carrier_four)

The `y`-coordinate companion of `QuadrupleMultiplicationFormula` (which pins `x(4P)`). Whenever
`4 . P` is an affine point `(X, Y)`, `Y . psi4^3 = omega4(x)` -- i.e. `Y = omega4/psi4^3`, the `n=4`
analogue of `MultiplicationYFormula` (`y(2P)=omega2/(2y)^3`) and `MultiplicationYTripleFormula`
(`y(3P)=omega3/psi3^3`). Here `psi4 = (2x^6+280x^3-784)(2y)` and `omega4` is the degree-24
y-division polynomial numerator anchored in `OmegaRecurrenceAnchors` (`secp256k1_omega_recurrence_four`:
`psi6 psi3^2 - psi2 psi5^2 = 4y omega4`).

Route: `4P = 2.(2P)` by two doublings (slopes `s2` at `P`, `s4` at `2P`); the core algebraic
lemma `quad_y_core` turns the double-slope tower into `Y4 . psi4^3 = omega4` via three CAS-designed
`linear_combination` certificates (a `y(2P)`-doubling at `2P`, an `x`-bridge, and the `psi4 = 2Y2.8y^3`
relation), assembled with the exact identity `(2Y2)^3 . 4096 y^12 = psi4^3` (no cancellation needed).
Kernel-checked; no `native_decide`.

This is the missing certificate for the `carrier_four` y-conjunct of the uniform N7 induction: with
it and `secp256k1_omega_recurrence_four`, the `n=4` base leaf of the joint omega-free `(x,y)` carrier
closes.
-/
import Mathlib
import Ecdlp.Proved.QuadrupleMultiplicationFormula

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Core double-slope identity for `y(4P)`.** With `s2` the tangent slope at `P=(x,y)` and `s4`
the tangent slope at `2P=(X2,Y2)` (`X2=s2^2-2x`, `Y2=-(s2(s2^2-3x)+y)`), the second-doubling
`y`-coordinate `Y4=-(s4(s4^2-3X2)+Y2)` satisfies `Y4 . psi4^3 = omega4(x)`, where
`psi4=(2x^6+280x^3-784)(2y)`. Sympy-designed `linear_combination` certificates; kernel-verified. -/
theorem quad_y_core (x y s2 s4 : ZMod Secp256k1.p)
    (hl2 : s2 * (2 * y) = 3 * x ^ 2)
    (hcurve : y ^ 2 = x ^ 3 + 7)
    (hcurve2 : (-(s2 * (s2 ^ 2 - 3 * x) + y)) ^ 2 = (s2 ^ 2 - 2 * x) ^ 3 + 7)
    (hl4 : s4 * (2 * (-(s2 * (s2 ^ 2 - 3 * x) + y))) = 3 * (s2 ^ 2 - 2 * x) ^ 2) :
    (-(s4 * (s4 ^ 2 - 3 * (s2 ^ 2 - 2 * x)) + (-(s2 * (s2 ^ 2 - 3 * x) + y)))) * ((2 * x ^ 6 + 280 * x ^ 3 - 784) * (2 * y)) ^ 3
      = x^24 + 8624*x^21 - 2875712*x^18 - 16946944*x^15 - 1054135040*x^12 - 35487778816*x^9 - 229379784704*x^6 - 701632282624*x^3 - 188900999168 := by
  have hDblY : (-(s4 * (s4 ^ 2 - 3 * (s2 ^ 2 - 2 * x)) + (-(s2 * (s2 ^ 2 - 3 * x) + y)))) * (2 * (-(s2 * (s2 ^ 2 - 3 * x) + y))) ^ 3
      = (s2 ^ 2 - 2 * x) ^ 6 + 140 * (s2 ^ 2 - 2 * x) ^ 3 - 392 := by
    linear_combination (3*s2^8 + 6*s2^7*s4 - 4*s2^6*s4^2 - 24*s2^6*x - 42*s2^5*s4*x + 24*s2^5*y + 24*s2^4*s4^2*x + 6*s2^4*s4*y + 36*s2^4*x^2 - 8*s2^3*s4^2*y + 96*s2^3*s4*x^2 - 120*s2^3*x*y - 36*s2^2*s4^2*x^2 - 24*s2^2*s4*x*y + 72*s2^2*x^3 + 12*s2^2*y^2 + 24*s2*s4^2*x*y - 72*s2*s4*x^3 + 144*s2*x^2*y - 4*s4^2*y^2 + 24*s4*x^2*y - 144*x^4 - 24*x*y^2) * hl4 + (20*s2^6 - 120*s2^4*x - 16*s2^3*y + 264*s2^2*x^2 + 48*s2*x*y - 224*x^3 - 8*y^2 - 56) * hcurve2
  have hbridge : ((s2 ^ 2 - 2 * x) ^ 6 + 140 * (s2 ^ 2 - 2 * x) ^ 3 - 392) * 4096 * y ^ 12
      = x^24 + 8624*x^21 - 2875712*x^18 - 16946944*x^15 - 1054135040*x^12 - 35487778816*x^9 - 229379784704*x^6 - 701632282624*x^3 - 188900999168 := by
    linear_combination (2048*s2^11*y^11 + 3072*s2^10*x^2*y^10 + 4608*s2^9*x^4*y^9 - 24576*s2^9*x*y^11 + 6912*s2^8*x^6*y^8 - 36864*s2^8*x^3*y^10 + 10368*s2^7*x^8*y^7 - 55296*s2^7*x^5*y^9 + 122880*s2^7*x^2*y^11 + 15552*s2^6*x^10*y^6 - 82944*s2^6*x^7*y^8 + 184320*s2^6*x^4*y^10 + 23328*s2^5*x^12*y^5 - 124416*s2^5*x^9*y^7 + 276480*s2^5*x^6*y^9 - 327680*s2^5*x^3*y^11 + 286720*s2^5*y^11 + 34992*s2^4*x^14*y^4 - 186624*s2^4*x^11*y^6 + 414720*s2^4*x^8*y^8 - 491520*s2^4*x^5*y^10 + 430080*s2^4*x^2*y^10 + 52488*s2^3*x^16*y^3 - 279936*s2^3*x^13*y^5 + 622080*s2^3*x^10*y^7 - 737280*s2^3*x^7*y^9 + 491520*s2^3*x^4*y^11 + 645120*s2^3*x^4*y^9 - 1720320*s2^3*x*y^11 + 78732*s2^2*x^18*y^2 - 419904*s2^2*x^15*y^4 + 933120*s2^2*x^12*y^6 - 1105920*s2^2*x^9*y^8 + 737280*s2^2*x^6*y^10 + 967680*s2^2*x^6*y^8 - 2580480*s2^2*x^3*y^10 + 118098*s2*x^20*y - 629856*s2*x^17*y^3 + 1399680*s2*x^14*y^5 - 1658880*s2*x^11*y^7 + 1105920*s2*x^8*y^9 + 1451520*s2*x^8*y^7 - 393216*s2*x^5*y^11 - 3870720*s2*x^5*y^9 + 3440640*s2*x^2*y^11 + 177147*x^22 - 944784*x^19*y^2 + 2099520*x^16*y^4 - 2488320*x^13*y^6 + 1658880*x^10*y^8 + 2177280*x^10*y^6 - 589824*x^7*y^10 - 5806080*x^7*y^8 + 5160960*x^4*y^10) * hl2 + (-531440*x^21 + 2302912*x^18*y^2 + 3728704*x^18 - 3995648*x^15*y^4 - 12391680*x^15*y^2 - 28976640*x^15 + 3469312*x^12*y^6 + 15577856*x^12*y^4 + 57765120*x^12*y^2 + 185889536*x^12 - 1507328*x^9*y^8 - 15239168*x^9*y^6 - 51279872*x^9*y^4 - 218466304*x^9*y^2 - 2355361792*x^9 + 262144*x^6*y^10 + 12730368*x^6*y^8 + 55394304*x^6*y^6 + 140492800*x^6*y^4 - 826097664*x^6*y^2 - 19000246272*x^6 - 4587520*x^3*y^10 - 33718272*x^3*y^8 - 247267328*x^3*y^6 - 1809547264*x^3*y^4 - 13217562624*x^3*y^2 - 96378060800*x^3 - 1605632*y^10 - 11239424*y^8 - 78675968*y^6 - 550731776*y^4 - 3855122432*y^2 - 26985857024) * hcurve
  have hY2c : 2 * (-(s2 * (s2 ^ 2 - 3 * x) + y)) * (8 * y ^ 3) = 2 * x ^ 6 + 280 * x ^ 3 - 784 := by
    linear_combination (-8*s2^2*y^2 - 12*s2*x^2*y - 18*x^4 + 24*x*y^2) * hl2 + (56*x^3 - 16*y^2 - 112) * hcurve
  have hcube : (2 * (-(s2 * (s2 ^ 2 - 3 * x) + y)) * (8 * y ^ 3)) ^ 3 = (2 * x ^ 6 + 280 * x ^ 3 - 784) ^ 3 := by
    rw [hY2c]
  have h2 : (2 * (-(s2 * (s2 ^ 2 - 3 * x) + y))) ^ 3 * 4096 * y ^ 12
      = ((2 * x ^ 6 + 280 * x ^ 3 - 784) * (2 * y)) ^ 3 := by
    linear_combination (8 * y ^ 3) * hcube
  rw [← h2]
  linear_combination (4096 * y ^ 12) * hDblY + hbridge

/-- **N7@4 -- the multiplication-by-4 `y`-coordinate formula for secp256k1.**
Whenever `4 . P` is an affine point `(X, Y)`, `Y . psi4^3 = omega4(x)` with
`psi4=(2x^6+280x^3-784)(2y)`. The `y`-companion of `secp256k1_quadruple_x_eq_Phi4_div_PsiSq4`:
the generic case builds `4P=2.(2P)` by two doublings and closes via `quad_y_core`; the 2-torsion
degeneracies force `4P=O`, contradicting the affine `4P` hypothesis. -/
theorem secp256k1_quadruple_y
    {x y X Y : ZMod Secp256k1.p} (h : secp256k1.toAffine.Nonsingular x y)
    {h' : secp256k1.toAffine.Nonsingular X Y}
    (hEq : (4 : ℕ) • (Point.some x y h) = Point.some X Y h') :
    Y * ((2 * x ^ 6 + 280 * x ^ 3 - 784) * (2 * y)) ^ 3
      = x^24 + 8624*x^21 - 2875712*x^18 - 16946944*x^15 - 1054135040*x^12 - 35487778816*x^9 - 229379784704*x^6 - 701632282624*x^3 - 188900999168 := by
  have h2 : (2 : ZMod Secp256k1.p) ≠ 0 := by
    have : ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
      rw [Ne, ZMod.natCast_eq_zero_iff]; decide
    simpa using this
  have hcurve : y ^ 2 = x ^ 3 + 7 := by
    have he : secp256k1.toAffine.Equation x y := h.1
    rw [WeierstrassCurve.Affine.equation_iff] at he
    simp only [secp256k1] at he
    linear_combination he
  have hnegY : secp256k1.toAffine.negY x y = -y := by
    simp [WeierstrassCurve.Affine.negY, secp256k1]
  by_cases hy0 : y = secp256k1.toAffine.negY x y
  · have h2P : (2 : ℕ) • (Point.some x y h) = 0 := by
      rw [two_nsmul]; exact Point.add_self_of_Y_eq hy0
    have h4P : (4 : ℕ) • (Point.some x y h) = 0 := by
      rw [show (4 : ℕ) = 2 + 2 from rfl, add_nsmul, h2P, add_zero]
    rw [h4P] at hEq
    exact absurd hEq.symm (Point.some_ne_zero h')
  · have hy : y ≠ 0 := fun h0 => hy0 (by rw [hnegY, h0]; ring)
    have hYd : y - secp256k1.toAffine.negY x y ≠ 0 := sub_ne_zero.mpr hy0
    set s2 := secp256k1.toAffine.slope x x y y with hs2def
    set X2 := secp256k1.toAffine.addX x x s2 with hX2def
    set Y2 := secp256k1.toAffine.addY x x y s2 with hY2def
    have hsl2 : s2 * (2 * y) = 3 * x ^ 2 := by
      rw [hs2def, slope_of_Y_ne rfl hy0, div_mul_eq_mul_div, div_eq_iff hYd]
      simp only [secp256k1, WeierstrassCurve.Affine.negY]
      ring
    have hx2val : X2 = s2 ^ 2 - 2 * x := by
      rw [hX2def]; simp only [WeierstrassCurve.Affine.addX, secp256k1]; ring
    have hy2val : Y2 = -(s2 * (s2 ^ 2 - 3 * x) + y) := by
      rw [hY2def]
      simp only [WeierstrassCurve.Affine.addY, WeierstrassCurve.Affine.negAddY,
        WeierstrassCurve.Affine.negY, WeierstrassCurve.Affine.addX, secp256k1]
      ring
    have hns2 : secp256k1.toAffine.Nonsingular X2 Y2 :=
      nonsingular_add h h (fun hxy => hy0 hxy.2)
    have hP2 : (2 : ℕ) • (Point.some x y h) = Point.some X2 Y2 hns2 := by
      rw [two_nsmul]; exact Point.add_self_of_Y_ne hy0
    have hcurve2 : Y2 ^ 2 = X2 ^ 3 + 7 := by
      have he : secp256k1.toAffine.Equation X2 Y2 := hns2.1
      rw [WeierstrassCurve.Affine.equation_iff] at he
      simp only [secp256k1] at he
      linear_combination he
    have hnegY2 : secp256k1.toAffine.negY X2 Y2 = -Y2 := by
      simp [WeierstrassCurve.Affine.negY, secp256k1]
    by_cases hY2eq : Y2 = secp256k1.toAffine.negY X2 Y2
    · have h4P : (4 : ℕ) • (Point.some x y h) = 0 := by
        rw [show (4 : ℕ) = 2 + 2 from rfl, add_nsmul, hP2,
          Point.add_self_of_Y_eq hY2eq]
      rw [h4P] at hEq
      exact absurd hEq.symm (Point.some_ne_zero h')
    · have hY2ne0 : Y2 ≠ 0 := fun h0 => hY2eq (by rw [hnegY2, h0]; ring)
      set s4 := secp256k1.toAffine.slope X2 X2 Y2 Y2 with hs4def
      set X4 := secp256k1.toAffine.addX X2 X2 s4 with hX4def
      set Y4 := secp256k1.toAffine.addY X2 X2 Y2 s4 with hY4def
      have hYd2 : Y2 - secp256k1.toAffine.negY X2 Y2 ≠ 0 := sub_ne_zero.mpr hY2eq
      have hsl4 : s4 * (2 * Y2) = 3 * X2 ^ 2 := by
        rw [hs4def, slope_of_Y_ne rfl hY2eq, div_mul_eq_mul_div, div_eq_iff hYd2]
        simp only [secp256k1, WeierstrassCurve.Affine.negY]
        ring
      have hy4val : Y4 = -(s4 * (s4 ^ 2 - 3 * X2) + Y2) := by
        rw [hY4def]
        simp only [WeierstrassCurve.Affine.addY, WeierstrassCurve.Affine.negAddY,
          WeierstrassCurve.Affine.negY, WeierstrassCurve.Affine.addX, secp256k1]
        ring
      have hns4 : secp256k1.toAffine.Nonsingular X4 Y4 :=
        nonsingular_add hns2 hns2 (fun hxy => hY2eq hxy.2)
      have hP4 : (4 : ℕ) • (Point.some x y h) = Point.some X4 Y4 hns4 := by
        rw [show (4 : ℕ) = 2 + 2 from rfl, add_nsmul, hP2]
        exact Point.add_self_of_Y_ne hY2eq
      rw [hP4, Point.some.injEq] at hEq
      rw [← hEq.2, hy4val, hx2val, hy2val]
      have hcurve2' := hcurve2
      rw [hy2val, hx2val] at hcurve2'
      have hsl4' := hsl4
      rw [hy2val, hx2val] at hsl4'
      exact quad_y_core x y s2 s4 hsl2 hcurve hcurve2' hsl4'

end Ecdlp.Curve
