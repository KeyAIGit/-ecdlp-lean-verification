import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.FourDivisionPolynomial
import Ecdlp.Proved.CoprimePsi3Psi5
import Ecdlp.Proved.MultiplicationFormula

/-!
# N7@4: the multiplication-by-4 `x`-coordinate formula — `x(4•P) = Φ₄(x)/ΨSq₄(x)`

The point-level `n = 4` case of the division-polynomial multiplication formula
`x([n]P) = Φₙ(x)/ΨSqₙ(x)` for secp256k1 — node **N7@4** of the `ψₙ ↔ E[n]` bridge,
and the **first EVEN rung** beyond the `n = 2` base case
(`MultiplicationFormula.lean`). Unlike the odd rungs `n = 3, 5`
(`TripleMultiplicationFormula.lean`, `QuintupleMultiplicationFormula.lean`), whose
generic branch is a **chord between two multiples**, `4P = 2•(2P)` is a
**doubling of a doubling**: two *tangent* slopes in series (`s2` at `P`, then `s4`
at `2P`), no chord. This completes the small-`n` ladder `n = 2, 3, 4, 5`.

**Main theorem** (`secp256k1_quadruple_x_eq_Φ₄_div_ΨSq₄`): whenever `4 • P` is an
affine point `(X, Y)`, its `x`-coordinate is `X = (Φ 4).eval x / (ΨSq 4).eval x` —
with **no side conditions** beyond `4 • P ≠ O` (encoded by the hypothesis itself):
* generic branch: `P` and `2P` are both non-2-torsion, so `2P = (X2, Y2)` and
  `4P = 2•(2P)` are built by two applications of `Point.add_self_of_Y_ne`; the core
  certificate chain `quad_x_core` first applies the `n = 2` doubling algebra at `2P`
  (`hInner`: `x(4P)·Ψ₂Sq(X2) = X2⁴ − 56·X2`), then the algebraic **bridge**
  `hBridge` rewrites `(X2⁴ − 56X2)·ΨSq₄(x)` back to `Φ₄(x)·Ψ₂Sq(X2)` purely in
  `(x, y, s2)`, and `hkey` assembles the two and cancels the auxiliary factor
  `Ψ₂Sq(X2)·(2y)⁸ ≠ 0`. The denominator `ΨSq₄(x) = preΨ₄(x)²·Ψ₂Sq(x)` is nonzero
  because `Ψ₂Sq(x) = 4y² ≠ 0` (`P` non-2-torsion) and `preΨ₄(x) = Y2·16y³ ≠ 0`
  (`hY2pre`, since `2P` non-2-torsion means `Y2 ≠ 0`);
* `P` 2-torsion (`y = negY`): `2P = O`, so `4P = O`, contradicting the affine `4P`
  hypothesis — dispatched by `Point.some_ne_zero`;
* `2P` 2-torsion (`Y2 = negY X2 Y2`): `4P = 2•(2P) = O`, likewise contradicts an
  affine `4P`.

**Eval-lemma route.** As in the `n = 3, 5` rungs, the `private` evaluations are
derived from Mathlib's `Φ_ofNat` (at `n = 3`, odd → `if_neg`) and `ΨSq_ofNat` (at
`n = 4`, even → `if_pos`), unfolding `preΨ' 4 = preΨ₄`, `preΨ' 3 = Ψ₃`, and
`preΨ' 5` (repo `secp256k1_preΨ₅`) into their concrete secp256k1 forms; `ΨSq₄`
carries the even-index `Ψ₂Sq` factor.

Every `linear_combination` certificate, the ground-truth polynomials (recomputed
from the EDS recurrence from scratch and cross-checked against Mathlib's `Φ_four` /
`ΨSq_four` closed forms), `Φ₄` monic of degree `16 = 4²`, `ΨSq₄` of degree `15`,
and the final formula are symbolically and numerically cross-checked (explicit
double-of-double EC arithmetic on two primes) in
`scripts/certs/quad_mult_formula_check.py` (`CERT_OK`); nothing from the script
enters the proofs — the kernel re-checks everything. Largest single certificate:
`hBridge` (122-monomial cofactor). No `native_decide` in this file, no new axioms.
-/

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

/-- `Φ 4` evaluated: the degree-`16 = 4²` monic numerator of `x(4•P)`. Derived from
Mathlib's `Φ_ofNat` at `n = 3` (`Φ 4 = X·preΨ'4²·Ψ₂Sq − preΨ'5·preΨ'3`). -/
private theorem Φ₄_eval (x : ZMod Secp256k1.p) :
    (secp256k1.Φ 4).eval x
      = x ^ 16 - 3808 * x ^ 13 + 144256 * x ^ 10 + 2985472 * x ^ 7 + 38108672 * x ^ 4
          + 68841472 * x := by
  rw [show (4 : ℤ) = ((3 : ℕ) + 1 : ℤ) from rfl, WeierstrassCurve.Φ_ofNat,
    if_neg (by decide : ¬ Even 3), if_neg (by decide : ¬ Even 3),
    WeierstrassCurve.preΨ'_four, WeierstrassCurve.preΨ'_three,
    secp256k1_preΨ₅, secp256k1_preΨ₄, secp256k1_Ψ₃, secp256k1_Ψ₂Sq]
  simp only [mul_one, eval_add, eval_sub, eval_mul, eval_pow, eval_X, eval_C, eval_ofNat]
  ring

/-- `ΨSq 4` evaluated: the degree-15 denominator of `x(4•P)`
(`= preΨ₄² · Ψ₂Sq`, the even-index square carrying the 2-division factor). -/
private theorem ΨSq₄_eval (x : ZMod Secp256k1.p) :
    (secp256k1.ΨSq 4).eval x
      = 16 * x ^ 15 + 4592 * x ^ 12 + 332416 * x ^ 9 + 351232 * x ^ 6 - 9834496 * x ^ 3
          + 17210368 := by
  rw [show (4 : ℤ) = ((4 : ℕ) : ℤ) from rfl, WeierstrassCurve.ΨSq_ofNat,
    if_pos (by decide : Even 4), WeierstrassCurve.preΨ'_four,
    secp256k1_preΨ₄, secp256k1_Ψ₂Sq]
  simp only [eval_mul, eval_pow, eval_add, eval_sub, eval_C, eval_X, eval_ofNat]
  ring

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Core certificate chain for N7@4.** With `s2` the tangent slope at `P = (x, y)`
(`s2·2y = 3x²`) and `s4` the tangent slope at `2P = (X2, Y2)`
(`s4·2Y2 = 3X2²`, with `X2 = s2²−2x`, `Y2 = −(s2·(s2²−3x)+y)`), and `2P` not
2-torsion (`Y2 ≠ 0`, i.e. `s2·(s2²−3x)+y ≠ 0`), the doubled-doubled `x`-coordinate
`x(4P) = s4²−2X2` equals `Φ₄(x)/ΨSq₄(x)`. The chain (designed in
`scripts/certs/quad_mult_formula_check.py`, re-verified by the kernel):
`hInner` applies the `n = 2` doubling identity at `2P`; `hY2pre` (`Y2·16y³ = preΨ₄`)
gives `preΨ₄(x) ≠ 0`; `hBridge` rewrites `(X2⁴−56X2)·ΨSq₄` into `Φ₄·Ψ₂Sq(X2)` in
`(x, y, s2)` only; `hkey` assembles them and cancels `Ψ₂Sq(X2)·(2y)⁸ ≠ 0`. -/
theorem quad_x_core (x y s2 s4 : ZMod Secp256k1.p)
    (hcurve : y ^ 2 = x ^ 3 + 7) (hy : y ≠ 0)
    (h2 : (2 : ZMod Secp256k1.p) ≠ 0)
    (hl2 : s2 * (2 * y) = 3 * x ^ 2)
    (hY2 : s2 * (s2 ^ 2 - 3 * x) + y ≠ 0)
    (hcurve2 : (-(s2 * (s2 ^ 2 - 3 * x) + y)) ^ 2 = (s2 ^ 2 - 2 * x) ^ 3 + 7)
    (hl4 : s4 * (2 * (-(s2 * (s2 ^ 2 - 3 * x) + y))) = 3 * (s2 ^ 2 - 2 * x) ^ 2) :
    s4 ^ 2 - 2 * (s2 ^ 2 - 2 * x)
      = (x ^ 16 - 3808 * x ^ 13 + 144256 * x ^ 10 + 2985472 * x ^ 7 + 38108672 * x ^ 4
          + 68841472 * x)
        / (16 * x ^ 15 + 4592 * x ^ 12 + 332416 * x ^ 9 + 351232 * x ^ 6 - 9834496 * x ^ 3
          + 17210368) := by
  have h2y : (2 : ZMod Secp256k1.p) * y ≠ 0 := mul_ne_zero h2 hy
  have h4 : (4 : ZMod Secp256k1.p) ≠ 0 := by
    rw [show (4 : ZMod Secp256k1.p) = 2 ^ 2 by norm_num]; exact pow_ne_zero 2 h2
  have h16 : (16 : ZMod Secp256k1.p) ≠ 0 := by
    rw [show (16 : ZMod Secp256k1.p) = 2 ^ 4 by norm_num]; exact pow_ne_zero 4 h2
  -- `Ψ₂Sq(x) = 4x³ + 28 = 4y² ≠ 0` (P not 2-torsion)
  have hΨ2ne : (4 : ZMod Secp256k1.p) * x ^ 3 + 28 ≠ 0 := by
    intro hcz
    exact mul_ne_zero h2y h2y (by linear_combination 4 * hcurve + hcz)
  -- `Y2 · 16y³ = preΨ₄(x)` — so `preΨ₄(x) = 0` would force `Y2 = 0`
  have hY2pre : -(s2 * (s2 ^ 2 - 3 * x) + y) * (16 * y ^ 3)
      = 2 * x ^ 6 + 280 * x ^ 3 - 784 := by
    linear_combination
      (-8 * s2 ^ 2 * y ^ 2 - 12 * s2 * x ^ 2 * y - 18 * x ^ 4 + 24 * x * y ^ 2) * hl2
      + (56 * x ^ 3 - 16 * y ^ 2 - 112) * hcurve
  have hpre4ne : (2 : ZMod Secp256k1.p) * x ^ 6 + 280 * x ^ 3 - 784 ≠ 0 := by
    rw [← hY2pre]
    exact mul_ne_zero (neg_ne_zero.mpr hY2) (mul_ne_zero h16 (pow_ne_zero 3 hy))
  have hΨSq4ne : (16 * x ^ 15 + 4592 * x ^ 12 + 332416 * x ^ 9 + 351232 * x ^ 6 - 9834496 * x ^ 3
          + 17210368) ≠ 0 := by
    rw [show (16 * x ^ 15 + 4592 * x ^ 12 + 332416 * x ^ 9 + 351232 * x ^ 6 - 9834496 * x ^ 3
          + 17210368)
        = (2 * x ^ 6 + 280 * x ^ 3 - 784) ^ 2 * (4 * x ^ 3 + 28) by ring]
    exact mul_ne_zero (pow_ne_zero 2 hpre4ne) hΨ2ne
  -- `n = 2` doubling identity applied at `2P`: `x(4P)·Ψ₂Sq(X2) = X2⁴ − 56·X2`
  have hInner : (s4 ^ 2 - 2 * (s2 ^ 2 - 2 * x)) * (4 * (s2 ^ 2 - 2 * x) ^ 3 + 28)
      = (s2 ^ 2 - 2 * x) ^ 4 - 56 * (s2 ^ 2 - 2 * x) := by
    linear_combination
      (2 * (-(s2 * (s2 ^ 2 - 3 * x) + y)) * s4 + 3 * (s2 ^ 2 - 2 * x) ^ 2) * hl4
      - 4 * s4 ^ 2 * hcurve2
  -- `Ψ₂Sq(X2) = 4X2³ + 28 = 4Y2² ≠ 0` (2P not 2-torsion)
  have hΨ2X2 : 4 * (s2 ^ 2 - 2 * x) ^ 3 + 28
      = 4 * (-(s2 * (s2 ^ 2 - 3 * x) + y)) ^ 2 := by
    linear_combination -4 * hcurve2
  have hZne : (4 * (s2 ^ 2 - 2 * x) ^ 3 + 28) * (2 * y) ^ 8 ≠ 0 := by
    rw [hΨ2X2]
    exact mul_ne_zero (mul_ne_zero h4 (pow_ne_zero 2 (neg_ne_zero.mpr hY2)))
      (pow_ne_zero 8 h2y)
  -- the bridge: `(X2⁴ − 56X2)·ΨSq₄(x) = Φ₄(x)·Ψ₂Sq(X2)` in `(x, y, s2)`
  -- (scaled by `(2y)⁸` for polynomial cofactors; sympy-designed, kernel-verified)
  have hBridge : ((s2 ^ 2 - 2 * x) ^ 4 - 56 * (s2 ^ 2 - 2 * x))
        * (16 * x ^ 15 + 4592 * x ^ 12 + 332416 * x ^ 9 + 351232 * x ^ 6 - 9834496 * x ^ 3
          + 17210368) * (2 * y) ^ 8
      = (x ^ 16 - 3808 * x ^ 13 + 144256 * x ^ 10 + 2985472 * x ^ 7 + 38108672 * x ^ 4
          + 68841472 * x)
        * (4 * (s2 ^ 2 - 2 * x) ^ 3 + 28) * (2 * y) ^ 8 := by
    linear_combination
      (2048 * s2 ^ 7 * x ^ 15 * y ^ 7 + 587776 * s2 ^ 7 * x ^ 12 * y ^ 7
         + 42549248 * s2 ^ 7 * x ^ 9 * y ^ 7 + 44957696 * s2 ^ 7 * x ^ 6 * y ^ 7
         - 1258815488 * s2 ^ 7 * x ^ 3 * y ^ 7 + 2202927104 * s2 ^ 7 * y ^ 7
         + 3072 * s2 ^ 6 * x ^ 17 * y ^ 6 + 881664 * s2 ^ 6 * x ^ 14 * y ^ 6
         + 63823872 * s2 ^ 6 * x ^ 11 * y ^ 6 + 67436544 * s2 ^ 6 * x ^ 8 * y ^ 6
         - 1888223232 * s2 ^ 6 * x ^ 5 * y ^ 6 + 3304390656 * s2 ^ 6 * x ^ 2 * y ^ 6
         + 4608 * s2 ^ 5 * x ^ 19 * y ^ 5 - 16896 * s2 ^ 5 * x ^ 16 * y ^ 7
         + 1322496 * s2 ^ 5 * x ^ 16 * y ^ 5 - 2752512 * s2 ^ 5 * x ^ 13 * y ^ 7
         + 95735808 * s2 ^ 5 * x ^ 13 * y ^ 5 - 414253056 * s2 ^ 5 * x ^ 10 * y ^ 7
         + 101154816 * s2 ^ 5 * x ^ 10 * y ^ 5 - 1888223232 * s2 ^ 5 * x ^ 7 * y ^ 7
         - 2832334848 * s2 ^ 5 * x ^ 7 * y ^ 5 - 9441116160 * s2 ^ 5 * x ^ 4 * y ^ 7
         + 4956585984 * s2 ^ 5 * x ^ 4 * y ^ 5 - 52870250496 * s2 ^ 5 * x * y ^ 7
         + 6912 * s2 ^ 4 * x ^ 21 * y ^ 4 - 25344 * s2 ^ 4 * x ^ 18 * y ^ 6
         + 1983744 * s2 ^ 4 * x ^ 18 * y ^ 4 - 4128768 * s2 ^ 4 * x ^ 15 * y ^ 6
         + 143603712 * s2 ^ 4 * x ^ 15 * y ^ 4 - 621379584 * s2 ^ 4 * x ^ 12 * y ^ 6
         + 151732224 * s2 ^ 4 * x ^ 12 * y ^ 4 - 2832334848 * s2 ^ 4 * x ^ 9 * y ^ 6
         - 4248502272 * s2 ^ 4 * x ^ 9 * y ^ 4 - 14161674240 * s2 ^ 4 * x ^ 6 * y ^ 6
         + 7434878976 * s2 ^ 4 * x ^ 6 * y ^ 4 - 79305375744 * s2 ^ 4 * x ^ 3 * y ^ 6
         + 10368 * s2 ^ 3 * x ^ 23 * y ^ 3 - 38016 * s2 ^ 3 * x ^ 20 * y ^ 5
         + 2975616 * s2 ^ 3 * x ^ 20 * y ^ 3 + 52224 * s2 ^ 3 * x ^ 17 * y ^ 7
         - 6193152 * s2 ^ 3 * x ^ 17 * y ^ 5 + 215405568 * s2 ^ 3 * x ^ 17 * y ^ 3
         + 2408448 * s2 ^ 3 * x ^ 14 * y ^ 7 - 932069376 * s2 ^ 3 * x ^ 14 * y ^ 5
         + 227598336 * s2 ^ 3 * x ^ 14 * y ^ 3 + 1464336384 * s2 ^ 3 * x ^ 11 * y ^ 7
         - 4248502272 * s2 ^ 3 * x ^ 11 * y ^ 5 - 6372753408 * s2 ^ 3 * x ^ 11 * y ^ 3
         + 10250354688 * s2 ^ 3 * x ^ 8 * y ^ 7 - 21242511360 * s2 ^ 3 * x ^ 8 * y ^ 5
         + 11152318464 * s2 ^ 3 * x ^ 8 * y ^ 3 + 86858268672 * s2 ^ 3 * x ^ 5 * y ^ 7
         - 118958063616 * s2 ^ 3 * x ^ 5 * y ^ 5 + 264351252480 * s2 ^ 3 * x ^ 2 * y ^ 7
         + 15552 * s2 ^ 2 * x ^ 25 * y ^ 2 - 57024 * s2 ^ 2 * x ^ 22 * y ^ 4
         + 4463424 * s2 ^ 2 * x ^ 22 * y ^ 2 + 78336 * s2 ^ 2 * x ^ 19 * y ^ 6
         - 9289728 * s2 ^ 2 * x ^ 19 * y ^ 4 + 323108352 * s2 ^ 2 * x ^ 19 * y ^ 2
         + 3612672 * s2 ^ 2 * x ^ 16 * y ^ 6 - 1398104064 * s2 ^ 2 * x ^ 16 * y ^ 4
         + 341397504 * s2 ^ 2 * x ^ 16 * y ^ 2 + 2196504576 * s2 ^ 2 * x ^ 13 * y ^ 6
         - 6372753408 * s2 ^ 2 * x ^ 13 * y ^ 4 - 9559130112 * s2 ^ 2 * x ^ 13 * y ^ 2
         + 15375532032 * s2 ^ 2 * x ^ 10 * y ^ 6 - 31863767040 * s2 ^ 2 * x ^ 10 * y ^ 4
         + 16728477696 * s2 ^ 2 * x ^ 10 * y ^ 2 + 130287403008 * s2 ^ 2 * x ^ 7 * y ^ 6
         - 178437095424 * s2 ^ 2 * x ^ 7 * y ^ 4 + 396526878720 * s2 ^ 2 * x ^ 4 * y ^ 6
         + 23328 * s2 * x ^ 27 * y - 85536 * s2 * x ^ 24 * y ^ 3 + 6695136 * s2 * x ^ 24 * y
         + 117504 * s2 * x ^ 21 * y ^ 5 - 13934592 * s2 * x ^ 21 * y ^ 3
         + 484662528 * s2 * x ^ 21 * y - 71680 * s2 * x ^ 18 * y ^ 7
         + 5419008 * s2 * x ^ 18 * y ^ 5 - 2097156096 * s2 * x ^ 18 * y ^ 3
         + 512096256 * s2 * x ^ 18 * y + 4472832 * s2 * x ^ 15 * y ^ 7
         + 3294756864 * s2 * x ^ 15 * y ^ 5 - 9559130112 * s2 * x ^ 15 * y ^ 3
         - 14338695168 * s2 * x ^ 15 * y - 2280800256 * s2 * x ^ 12 * y ^ 7
         + 23063298048 * s2 * x ^ 12 * y ^ 5 - 47795650560 * s2 * x ^ 12 * y ^ 3
         + 25092716544 * s2 * x ^ 12 * y - 22164144128 * s2 * x ^ 9 * y ^ 7
         + 195431104512 * s2 * x ^ 9 * y ^ 5 - 267655643136 * s2 * x ^ 9 * y ^ 3
         - 196375216128 * s2 * x ^ 6 * y ^ 7 + 594790318080 * s2 * x ^ 6 * y ^ 5
         - 422962003968 * s2 * x ^ 3 * y ^ 7 - 123363917824 * s2 * y ^ 7 + 34992 * x ^ 29
         - 128304 * x ^ 26 * y ^ 2 + 10042704 * x ^ 26 + 176256 * x ^ 23 * y ^ 4
         - 20901888 * x ^ 23 * y ^ 2 + 726993792 * x ^ 23 - 107520 * x ^ 20 * y ^ 6
         + 8128512 * x ^ 20 * y ^ 4 - 3145734144 * x ^ 20 * y ^ 2 + 768144384 * x ^ 20
         + 6709248 * x ^ 17 * y ^ 6 + 4942135296 * x ^ 17 * y ^ 4
         - 14338695168 * x ^ 17 * y ^ 2 - 21508042752 * x ^ 17 - 3421200384 * x ^ 14 * y ^ 6
         + 34594947072 * x ^ 14 * y ^ 4 - 71693475840 * x ^ 14 * y ^ 2
         + 37639074816 * x ^ 14 - 33246216192 * x ^ 11 * y ^ 6
         + 293146656768 * x ^ 11 * y ^ 4 - 401483464704 * x ^ 11 * y ^ 2
         - 294562824192 * x ^ 8 * y ^ 6 + 892185477120 * x ^ 8 * y ^ 4
         - 634443005952 * x ^ 5 * y ^ 6 - 185045876736 * x ^ 2 * y ^ 6) * hl2
      +
      (-104976 * x ^ 28 + 279936 * x ^ 25 * y ^ 2 - 29393280 * x ^ 25
         - 248832 * x ^ 22 * y ^ 4 + 31352832 * x ^ 22 * y ^ 2 - 1975228416 * x ^ 22
         + 73728 * x ^ 19 * y ^ 6 + 8709120 * x ^ 19 * y ^ 4 + 7242504192 * x ^ 19 * y ^ 2
         + 11522165760 * x ^ 19 - 11934720 * x ^ 16 * y ^ 6 - 7644865536 * x ^ 16 * y ^ 4
         + 3840721920 * x ^ 16 * y ^ 2 - 16131032064 * x ^ 16 + 2702278656 * x ^ 13 * y ^ 6
         - 46430060544 * x ^ 13 * y ^ 4 + 172064342016 * x ^ 13 * y ^ 2
         + 34392637440 * x ^ 10 * y ^ 6 - 382365204480 * x ^ 10 * y ^ 4
         + 260574806016 * x ^ 7 * y ^ 6 + 79305375744 * x ^ 4 * y ^ 6) * hcurve
  -- assemble, then cancel `Ψ₂Sq(X2)·(2y)⁸ ≠ 0`
  have hkey : ((s4 ^ 2 - 2 * (s2 ^ 2 - 2 * x))
        * (16 * x ^ 15 + 4592 * x ^ 12 + 332416 * x ^ 9 + 351232 * x ^ 6 - 9834496 * x ^ 3
          + 17210368))
        * ((4 * (s2 ^ 2 - 2 * x) ^ 3 + 28) * (2 * y) ^ 8)
      = (x ^ 16 - 3808 * x ^ 13 + 144256 * x ^ 10 + 2985472 * x ^ 7 + 38108672 * x ^ 4
          + 68841472 * x)
        * ((4 * (s2 ^ 2 - 2 * x) ^ 3 + 28) * (2 * y) ^ 8) := by
    linear_combination
      ((16 * x ^ 15 + 4592 * x ^ 12 + 332416 * x ^ 9 + 351232 * x ^ 6 - 9834496 * x ^ 3
          + 17210368) * (2 * y) ^ 8) * hInner + hBridge
  rw [eq_div_iff hΨSq4ne]
  exact mul_right_cancel₀ hZne hkey

/-- **N7@4 — the multiplication-by-4 `x`-coordinate formula for secp256k1.**
Whenever `4 • P` is an affine point `(X, Y)`, its `x`-coordinate equals Mathlib's
`Φ₄/ΨSq₄` evaluated at `x(P)` — with no side conditions: the generic case builds
`4P = 2•(2P)` by two doublings and closes via `quad_x_core`; if `P` is 2-torsion
then `2P = O` so `4P = O`, and if `2P` is 2-torsion then `4P = 2•(2P) = O`, both
contradicting the affine `4P` hypothesis (`Point.some_ne_zero`). -/
theorem secp256k1_quadruple_x_eq_Φ₄_div_ΨSq₄
    {x y X Y : ZMod Secp256k1.p} (h : secp256k1.toAffine.Nonsingular x y)
    {h' : secp256k1.toAffine.Nonsingular X Y}
    (hEq : (4 : ℕ) • (Point.some x y h) = Point.some X Y h') :
    X = (secp256k1.Φ 4).eval x / (secp256k1.ΨSq 4).eval x := by
  rw [Φ₄_eval, ΨSq₄_eval]
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
  · -- `P` is 2-torsion: `2P = O`, so `4P = O`, contradicting the affine `4P`.
    have h2P : (2 : ℕ) • (Point.some x y h) = 0 := by
      rw [two_nsmul]; exact Point.add_self_of_Y_eq hy0
    have h4P : (4 : ℕ) • (Point.some x y h) = 0 := by
      rw [show (4 : ℕ) = 2 + 2 from rfl, add_nsmul, h2P, add_zero]
    rw [h4P] at hEq
    exact absurd hEq.symm (Point.some_ne_zero h')
  · have hy : y ≠ 0 := fun h0 => hy0 (by rw [hnegY, h0]; ring)
    have h2y : (2 : ZMod Secp256k1.p) * y ≠ 0 := mul_ne_zero h2 hy
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
    -- `2P` lies on the curve (from its `Nonsingular` witness)
    have hcurve2 : Y2 ^ 2 = X2 ^ 3 + 7 := by
      have he : secp256k1.toAffine.Equation X2 Y2 := hns2.1
      rw [WeierstrassCurve.Affine.equation_iff] at he
      simp only [secp256k1] at he
      linear_combination he
    have hnegY2 : secp256k1.toAffine.negY X2 Y2 = -Y2 := by
      simp [WeierstrassCurve.Affine.negY, secp256k1]
    by_cases hY2eq : Y2 = secp256k1.toAffine.negY X2 Y2
    · -- `2P` is 2-torsion: `4P = 2•(2P) = O`, contradiction.
      have h4P : (4 : ℕ) • (Point.some x y h) = 0 := by
        rw [show (4 : ℕ) = 2 + 2 from rfl, add_nsmul, hP2,
          Point.add_self_of_Y_eq hY2eq]
      rw [h4P] at hEq
      exact absurd hEq.symm (Point.some_ne_zero h')
    · -- generic branch: build `4P = 2•(2P)` by a second doubling, then the core.
      have hY2ne0 : Y2 ≠ 0 := fun h0 => hY2eq (by rw [hnegY2, h0]; ring)
      have hY2' : s2 * (s2 ^ 2 - 3 * x) + y ≠ 0 :=
        fun hc => hY2ne0 (by rw [hy2val, hc, neg_zero])
      set s4 := secp256k1.toAffine.slope X2 X2 Y2 Y2 with hs4def
      set X4 := secp256k1.toAffine.addX X2 X2 s4 with hX4def
      set Y4 := secp256k1.toAffine.addY X2 X2 Y2 s4 with hY4def
      have hYd2 : Y2 - secp256k1.toAffine.negY X2 Y2 ≠ 0 := sub_ne_zero.mpr hY2eq
      have hsl4 : s4 * (2 * Y2) = 3 * X2 ^ 2 := by
        rw [hs4def, slope_of_Y_ne rfl hY2eq, div_mul_eq_mul_div, div_eq_iff hYd2]
        simp only [secp256k1, WeierstrassCurve.Affine.negY]
        ring
      have hx4val : X4 = s4 ^ 2 - 2 * X2 := by
        rw [hX4def]; simp only [WeierstrassCurve.Affine.addX, secp256k1]; ring
      have hns4 : secp256k1.toAffine.Nonsingular X4 Y4 :=
        nonsingular_add hns2 hns2 (fun hxy => hY2eq hxy.2)
      have hP4 : (4 : ℕ) • (Point.some x y h) = Point.some X4 Y4 hns4 := by
        rw [show (4 : ℕ) = 2 + 2 from rfl, add_nsmul, hP2]
        exact Point.add_self_of_Y_ne hY2eq
      rw [hP4, Point.some.injEq] at hEq
      rw [← hEq.1, hx4val, hx2val]
      have hcurve2' := hcurve2
      rw [hy2val, hx2val] at hcurve2'
      have hsl4' := hsl4
      rw [hy2val, hx2val] at hsl4'
      exact quad_x_core x y s2 s4 hcurve hy h2 hsl2 hY2' hcurve2' hsl4'

end Ecdlp.Curve
