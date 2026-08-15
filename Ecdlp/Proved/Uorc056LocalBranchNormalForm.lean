import Mathlib

/-!
# UORC-056 C30 local quadratic-branch normal form

This file kernel-checks the rank-two algebra identities used by C30.
For a quadratic branch `z` with `z^2 = F`, every regular rational expression
reduces to an even coefficient plus an odd coefficient times `z`.  The file
checks multiplication, conjugation, the branch-difference formula, recovery
from a nonzero odd coefficient, public unit-gauge equivalence, and the
fractional-linear rationalization identities.

It does not formalize the finite-etale product decomposition of the concrete
kernel algebra, the squarefreeness of `K_H`, elliptic curves, the frozen Python
replay, or a circuit lower bound.
-/

namespace Ecdlp.Uorc056LocalBranchNormalForm

variable {K : Type*} [Field K]

/-- Rank-two normal form `even + odd * z`. -/
structure QuadPair (K : Type*) where
  even : K
  odd : K

/-- Evaluate a rank-two normal form at one quadratic branch. -/
def QuadPair.eval (q : QuadPair K) (z : K) : K :=
  q.even + q.odd * z

/-- Multiplication after reducing `z^2` to the public even value `F`. -/
def QuadPair.mul (F : K) (left right : QuadPair K) : QuadPair K where
  even := left.even * right.even + left.odd * right.odd * F
  odd := left.even * right.odd + left.odd * right.even

/-- The quadratic branch involution. -/
def QuadPair.conj (q : QuadPair K) : QuadPair K where
  even := q.even
  odd := -q.odd

/-- The public norm of a rank-two element. -/
def QuadPair.norm (F : K) (q : QuadPair K) : K :=
  q.even ^ 2 - q.odd ^ 2 * F

/-- Pair multiplication evaluates to ordinary multiplication once `z^2=F`. -/
theorem eval_mul
    (F z : K)
    (left right : QuadPair K)
    (hF : z ^ 2 = F) :
    (left.mul F right).eval z = left.eval z * right.eval z := by
  simp [QuadPair.mul, QuadPair.eval]
  rw [← hF]
  ring

/-- Conjugating the pair is the same as replacing `z` by `-z`. -/
theorem eval_conj
    (q : QuadPair K)
    (z : K) :
    q.conj.eval z = q.eval (-z) := by
  simp [QuadPair.conj, QuadPair.eval]
  ring

/-- Multiplication by the conjugate gives the public quadratic norm. -/
theorem eval_mul_conj
    (F z : K)
    (q : QuadPair K)
    (hF : z ^ 2 = F) :
    q.eval z * q.eval (-z) = q.norm F := by
  simp [QuadPair.eval, QuadPair.norm]
  rw [hF]
  ring

/-- The complete branch-sensitive part of `e + o*z` is `2*o*z`. -/
theorem branchDifference
    (e o z : K) :
    (e + o * z) - (e + o * (-z)) = 2 * o * z := by
  ring

/-- In odd characteristic and away from `z=0`, a collision of the two branches
forces the odd coefficient to vanish. -/
theorem oddCoefficient_eq_zero_of_collision
    (e o z : K)
    (h2 : (2 : K) ≠ 0)
    (hz : z ≠ 0)
    (hcollision : e + o * z = e + o * (-z)) :
    o = 0 := by
  have hzero : (2 : K) * o * z = 0 := by
    rw [← branchDifference e o z]
    exact sub_eq_zero.mpr hcollision
  rcases mul_eq_zero.mp hzero with hleft | hright
  · rcases mul_eq_zero.mp hleft with htwo | ho
    · exact False.elim (h2 htwo)
    · exact ho
  · exact False.elim (hz hright)

/-- A nonzero odd coefficient makes the certificate constant-cost equivalent
to the original branch. -/
theorem recoverBranch
    (e o z : K)
    (ho : o ≠ 0) :
    (e + o * z - e) / o = z := by
  field_simp [ho]
  ring

/-- Multiplication by a public nonzero gauge does not compress the branch. -/
theorem recoverFromUnitGauge
    (u z : K)
    (hu : u ≠ 0) :
    (u * z) / u = z := by
  field_simp [hu]

/-- Rationalizing a fractional-linear certificate produces its even and odd
rank-two coefficients. -/
theorem mobiusNumeratorNormalForm
    (a b c d F z : K)
    (hF : z ^ 2 = F) :
    (a + b * z) * (c - d * z) =
      (a * c - b * d * F) + (b * c - a * d) * z := by
  rw [← hF]
  ring

/-- The conjugate denominator is branch-even. -/
theorem mobiusDenominatorNorm
    (c d F z : K)
    (hF : z ^ 2 = F) :
    (c + d * z) * (c - d * z) = c ^ 2 - d ^ 2 * F := by
  rw [← hF]
  ring

/-- If the fractional-linear determinant and norm denominator are nonzero,
its odd coefficient is nonzero and therefore retains the full branch. -/
theorem mobiusOddCoefficient_ne_zero
    (a b c d F : K)
    (hdet : b * c - a * d ≠ 0)
    (hnorm : c ^ 2 - d ^ 2 * F ≠ 0) :
    (b * c - a * d) / (c ^ 2 - d ^ 2 * F) ≠ 0 := by
  exact div_ne_zero hdet hnorm

/-- A branch-even certificate collides identically. -/
theorem evenCertificate_collision
    (e z : K) :
    e + 0 * z = e + 0 * (-z) := by
  ring

/-- Arithmetic regression certificate for the frozen C30 corpus. -/
theorem frozenMarkedGeneratorTotal :
    30 + 78 + 66 + 126 + 138 = 438 := by
  native_decide

/-- Each marked generator is checked on the half-kernel. -/
theorem frozenGaugeEvaluationTotal :
    30 * 15 + 78 * 39 + 66 * 33 + 126 * 63 + 138 * 69 = 23130 := by
  native_decide

/-- All nonzero marked scalar queries in the five-curve corpus. -/
theorem frozenScalarEvaluationTotal :
    30 ^ 2 + 78 ^ 2 + 66 ^ 2 + 126 ^ 2 + 138 ^ 2 = 46260 := by
  native_decide

end Ecdlp.Uorc056LocalBranchNormalForm
