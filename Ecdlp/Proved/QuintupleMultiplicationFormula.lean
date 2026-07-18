import Mathlib
import Ecdlp.Proved.DivisionPolynomial
import Ecdlp.Proved.FourDivisionPolynomial
import Ecdlp.Proved.ThreeTorsionCard
import Ecdlp.Proved.ThreeTorsionBridge
import Ecdlp.Proved.FiveTorsionBridge
import Ecdlp.Proved.MultiplicationFormula
import Ecdlp.Proved.CoprimePsi2Psi5
import Ecdlp.Proved.CoprimePsi3Psi5

/-!
# N7@5: the multiplication-by-5 `x`-coordinate formula — `x(5•P) = Φ₅(x)/ΨSq₅(x)`

The point-level `n = 5` case of the division-polynomial multiplication formula
`x([n]P) = Φₙ(x)/ΨSqₙ(x)` for secp256k1 — node **N7@5** of the `ψₙ ↔ E[n]` bridge,
extending `n = 2` (`MultiplicationFormula.lean`) and `n = 3`
(`TripleMultiplicationFormula.lean`) to the rung `n = 5` whose generic branch is a
**chord between two multiples** (`5P = 3P + 2P`), the prototype of the general N7
addition step: two slope eliminations (`s5`, then `s3`) instead of one.

**Main theorem** (`secp256k1_quintuple_x_eq_Φ₅_div_ΨSq₅`): whenever `5 • P` is an
affine point `(X, Y)`, its `x`-coordinate is `X = (Φ 5).eval x / (ΨSq 5).eval x` —
with **no side conditions** beyond `5 • P ≠ O` (encoded by the hypothesis itself):
* generic branch: `5P = 3P + 2P` through tangent-chord-chord; the core certificate
  chain `quint_x_core` eliminates the chord slope `s5` (one `hBF5` step), then the
  chord slope `s3` (three brick identities `hs3Y`/`hs3E`/`hs3D` assembled in `hs3F`),
  then closes with a master certificate `hmaster` in `(x, y, s2)` only; the chord
  denominator `x(3P) − x(2P) ≠ 0` comes from `5P ≠ O` via `five_core` and the
  5-torsion bridge (`FiveTorsionBridge.lean`);
* 2-torsion branch (`y = 0`): `2P = O` so `5P = P` and `X = x`; `Ψ₂Sq(x) = 0`
  collapses `Φ₅ − x·ΨSq₅` (divisible by `Ψ₂Sq`), with `ΨSq₅(x) ≠ 0` from the
  `Ψ₂Sq ⊥ preΨ₅` Bézout certificate (`CoprimePsi2Psi5.lean`);
* 3-torsion branch (`3P = O`): `5P = 2P` so `X = Φ₂/Ψ₂Sq`
  (`secp256k1_double_x_eq_Φ₂_div_Ψ₂Sq`); `Ψ₃(x) = 0` makes
  `Φ₂·ΨSq₅ − Φ₅·Ψ₂Sq` divisible by `Ψ₃`, with `ΨSq₅(x) ≠ 0` from the
  `Ψ₃ ⊥ preΨ₅` Bézout certificate (`CoprimePsi3Psi5.lean`).

**Eval-lemma route.** Mathlib v4.31 has no `Φ_five`/`ΨSq_five`, so the `private`
evaluations are derived from the definitional recurrences exactly as the proven
rungs do: `preΨ' 6` via `preΨ'_even` at `m = 0` (on top of `secp256k1_preΨ₅` from
`CoprimePsi3Psi5.lean`), `Φ 5` via `Φ_ofNat` at `n = 4`, and `ΨSq 5` via
`ΨSq_ofNat` — no fallback to unproven literals was needed.

Every `linear_combination` certificate, the ground-truth polynomials (recomputed
from the EDS recurrence from scratch), and the final formula are symbolically and
numerically cross-checked in `scripts/certs/quint_mult_formula_check.py`
(`CERT_OK`); nothing from the script enters the proofs — the kernel re-checks
everything. No `native_decide` in this file, no new axioms (the imported Bézout
certificates carry their documented `native_decide` residue-checks).
-/

namespace Ecdlp.Curve

open Polynomial WeierstrassCurve.Affine

/-- **The secp256k1 6-division polynomial (odd part) is
`preΨ' 6 = 3X¹⁶ + 4704X¹³ − 131712X¹⁰ − 7639296X⁷ − 12907776X⁴ − 103262208X`.**
Mathlib's even recursion `preΨ'_even` at `m = 0` collapses to
`Ψ₃·(preΨ' 5 − preΨ₄²)`; substituting the concrete secp256k1 forms and `ring`
finishes. -/
private theorem secp256k1_preΨ₆ :
    secp256k1.preΨ' 6
      = 3 * X ^ 16 + 4704 * X ^ 13 - 131712 * X ^ 10 - 7639296 * X ^ 7
        - 12907776 * X ^ 4 - 103262208 * X := by
  rw [show (6 : ℕ) = 2 * (0 + 3) from rfl, WeierstrassCurve.preΨ'_even,
    WeierstrassCurve.preΨ'_one, WeierstrassCurve.preΨ'_two, WeierstrassCurve.preΨ'_three,
    WeierstrassCurve.preΨ'_four, secp256k1_preΨ₅, secp256k1_Ψ₃, secp256k1_preΨ₄]
  simp only [map_ofNat]
  ring

/-- `preΨ' 5` evaluated at `x` (the univariate 5-division polynomial). -/
private theorem preΨ₅_eval (x : ZMod Secp256k1.p) :
    (secp256k1.preΨ' 5).eval x
      = 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656 := by
  rw [secp256k1_preΨ₅]
  simp only [eval_add, eval_sub, eval_mul, eval_pow, eval_X, eval_ofNat]

/-- `Φ 5` evaluated: the degree-`25 = 5²` numerator of `x(5•P)`. Derived from
Mathlib's `Φ_ofNat` at `n = 4` (`Φ 5 = X·preΨ'5² − preΨ'6·preΨ₄·Ψ₂Sq`). -/
private theorem Φ₅_eval (x : ZMod Secp256k1.p) :
    (secp256k1.Φ 5).eval x
      = x ^ 25 - 14560 * x ^ 22 + 2465680 * x ^ 19 + 125894720 * x ^ 16
        + 7022444800 * x ^ 13 + 58687354880 * x ^ 10 + 330094858240 * x ^ 7
        + 877040353280 * x ^ 4 - 1889009991680 * x := by
  rw [show (5 : ℤ) = ((4 : ℕ) + 1 : ℤ) from rfl, WeierstrassCurve.Φ_ofNat,
    if_pos (by decide : Even 4), if_pos (by decide : Even 4),
    WeierstrassCurve.preΨ'_four, secp256k1_preΨ₅, secp256k1_preΨ₆,
    secp256k1_preΨ₄, secp256k1_Ψ₂Sq]
  simp only [mul_one, eval_add, eval_sub, eval_mul, eval_pow, eval_X, eval_C, eval_ofNat]
  ring

/-- `ΨSq 5` evaluated: the degree-24 denominator of `x(5•P)` (`= (preΨ'5)²` since
`5` is odd). -/
private theorem ΨSq₅_eval (x : ZMod Secp256k1.p) :
    (secp256k1.ΨSq 5).eval x
      = 25 * x ^ 24 + 26600 * x ^ 21 + 6958000 * x ^ 18 - 68051200 * x ^ 15
        - 2787464960 * x ^ 12 + 9637806080 * x ^ 9 + 315638149120 * x ^ 6
        + 674646425600 * x ^ 3 + 377801998336 := by
  rw [show (5 : ℤ) = ((5 : ℕ) : ℤ) from rfl, WeierstrassCurve.ΨSq_ofNat,
    if_neg (by decide : ¬ Even 5), mul_one, secp256k1_preΨ₅]
  simp only [eval_pow, eval_add, eval_sub, eval_mul, eval_X, eval_ofNat]
  ring

variable [Fact (Nat.Prime Secp256k1.p)]

/-- **Core certificate chain for N7@5.** With `s2` the tangent slope at `P = (x, y)`
(`s2·2y = 3x²`), `s3` the chord slope from `2P` to `P`, and `s5` the chord slope
from `3P` to `2P` (all in cleared form), and both chord denominators nonzero
(`hd : x(2P) − x ≠ 0`, `hd5 : x(3P) − x(2P) ≠ 0`), the chord `x`-coordinate
`x(5P) = s5² − x(3P) − x(2P)` equals `Φ₅(x)/ΨSq₅(x)`. The chain (designed in
`scripts/certs/quint_mult_formula_check.py`, re-verified by the kernel):
`hBF5` eliminates `s5`; `hs3Y`/`hs3E`/`hs3D` eliminate `s3` brick by brick
(assembled in `hs3F`); `hmaster` is the master certificate in `(x, y, s2)` only;
`hquint`/`hquintsq` convert the chord denominator into `preΨ₅(x)²`; `hkey`
assembles everything and the auxiliary `(x(2P)−x)²·(2y)¹⁶` is cancelled. -/
theorem quint_x_core (x y s2 s3 s5 : ZMod Secp256k1.p)
    (hcurve : y ^ 2 = x ^ 3 + 7) (hy : y ≠ 0)
    (h2 : (2 : ZMod Secp256k1.p) ≠ 0)
    (hl2 : s2 * (2 * y) = 3 * x ^ 2)
    (hd : s2 ^ 2 - 3 * x ≠ 0)
    (hl3 : (s2 ^ 2 - 3 * x) * s3 = -(s2 * (s2 ^ 2 - 3 * x) + y) - y)
    (hd5 : s3 ^ 2 - 2 * s2 ^ 2 + 3 * x ≠ 0)
    (hl5 : (s3 ^ 2 - 2 * s2 ^ 2 + 3 * x) * s5
      = -(s3 * (s3 ^ 2 - 2 * s2 ^ 2 + 3 * x)) + 2 * (s2 * (s2 ^ 2 - 3 * x) + y)) :
    s5 ^ 2 - (s3 ^ 2 - s2 ^ 2 + x) - (s2 ^ 2 - 2 * x)
      = (x ^ 25 - 14560 * x ^ 22 + 2465680 * x ^ 19 + 125894720 * x ^ 16
          + 7022444800 * x ^ 13 + 58687354880 * x ^ 10 + 330094858240 * x ^ 7
          + 877040353280 * x ^ 4 - 1889009991680 * x)
        / (25 * x ^ 24 + 26600 * x ^ 21 + 6958000 * x ^ 18 - 68051200 * x ^ 15
          - 2787464960 * x ^ 12 + 9637806080 * x ^ 9 + 315638149120 * x ^ 6
          + 674646425600 * x ^ 3 + 377801998336) := by
  have h2y : (2 : ZMod Secp256k1.p) * y ≠ 0 := mul_ne_zero h2 hy
  have h64 : (64 : ZMod Secp256k1.p) ≠ 0 := by
    rw [show (64 : ZMod Secp256k1.p) = 2 ^ 6 by norm_num]
    exact pow_ne_zero 6 h2
  -- `(x(3P) − x(2P))·(x(2P) − x)²` in `(x, y, s2)` only (chord brick for `X3 − X2`)
  have hs3D : (s3 ^ 2 - 2 * s2 ^ 2 + 3 * x) * (s2 ^ 2 - 3 * x) ^ 2
      = (-(s2 * (s2 ^ 2 - 3 * x) + y) - y) ^ 2
        - (2 * (s2 ^ 2 - 2 * x) + x) * (s2 ^ 2 - 3 * x) ^ 2 := by
    linear_combination
      ((s2 ^ 2 - 3 * x) * s3 + (-(s2 * (s2 ^ 2 - 3 * x) + y) - y)) * hl3
  -- the ψ₅ certificate (`five_core`'s `hmaster` shape, cofactors re-verified)
  have hpsi5 : ((-(s2 * (s2 ^ 2 - 3 * x) + y) - y) ^ 2
        - (2 * (s2 ^ 2 - 2 * x) + x) * (s2 ^ 2 - 3 * x) ^ 2) * (64 * y ^ 6)
      = -(5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656) := by
    linear_combination
      (-32 * s2 ^ 5 * y ^ 5 - 48 * s2 ^ 4 * x ^ 2 * y ^ 4 - 72 * s2 ^ 3 * x ^ 4 * y ^ 3
        + 288 * s2 ^ 3 * x * y ^ 5 - 108 * s2 ^ 2 * x ^ 6 * y ^ 2 + 432 * s2 ^ 2 * x ^ 3 * y ^ 4
        + 128 * s2 ^ 2 * y ^ 6 - 162 * s2 * x ^ 8 * y + 648 * s2 * x ^ 5 * y ^ 3
        - 672 * s2 * x ^ 2 * y ^ 5 - 243 * x ^ 10 + 972 * x ^ 7 * y ^ 2 - 1008 * x ^ 4 * y ^ 4
        - 384 * x * y ^ 6) * hl2
      + (724 * x ^ 9 - 2192 * x ^ 6 * y ^ 2 - 7728 * x ^ 6 + 832 * x ^ 3 * y ^ 4
        + 7616 * x ^ 3 * y ^ 2 + 65856 * x ^ 3 + 256 * y ^ 6 + 1792 * y ^ 4 + 12544 * y ^ 2
        + 87808) * hcurve
  -- `(x(3P) − x(2P))·(x(2P) − x)²·64y⁶ = −preΨ₅(x)`: the chord denominator is `ψ₅`
  have hquint : (s3 ^ 2 - 2 * s2 ^ 2 + 3 * x) * ((s2 ^ 2 - 3 * x) ^ 2 * (64 * y ^ 6))
      = -(5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656) := by
    linear_combination (64 * y ^ 6) * hs3D + hpsi5
  have hpre5ne : 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656
      ≠ 0 := by
    intro hc
    rw [hc, neg_zero] at hquint
    exact mul_ne_zero hd5
      (mul_ne_zero (pow_ne_zero 2 hd) (mul_ne_zero h64 (pow_ne_zero 6 hy))) hquint
  have hdenne : (25 : ZMod Secp256k1.p) * x ^ 24 + 26600 * x ^ 21 + 6958000 * x ^ 18
      - 68051200 * x ^ 15 - 2787464960 * x ^ 12 + 9637806080 * x ^ 9
      + 315638149120 * x ^ 6 + 674646425600 * x ^ 3 + 377801998336 ≠ 0 := by
    rw [show (25 : ZMod Secp256k1.p) * x ^ 24 + 26600 * x ^ 21 + 6958000 * x ^ 18
        - 68051200 * x ^ 15 - 2787464960 * x ^ 12 + 9637806080 * x ^ 9
        + 315638149120 * x ^ 6 + 674646425600 * x ^ 3 + 377801998336
        = (5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656) ^ 2 by ring]
    exact pow_ne_zero 2 hpre5ne
  rw [eq_div_iff hdenne]
  -- eliminate the chord slope `s5`: `x(5P)·(X3−X2)²` in `(x, y, s2, s3)` only
  have hBF5 : (s5 ^ 2 - (s3 ^ 2 - s2 ^ 2 + x) - (s2 ^ 2 - 2 * x))
        * (s3 ^ 2 - 2 * s2 ^ 2 + 3 * x) ^ 2
      = (-(s3 * (s3 ^ 2 - 2 * s2 ^ 2 + 3 * x)) + 2 * (s2 * (s2 ^ 2 - 3 * x) + y)) ^ 2
        - ((s3 ^ 2 - s2 ^ 2 + x) + (s2 ^ 2 - 2 * x))
          * (s3 ^ 2 - 2 * s2 ^ 2 + 3 * x) ^ 2 := by
    linear_combination
      ((s3 ^ 2 - 2 * s2 ^ 2 + 3 * x) * s5
        + (-(s3 * (s3 ^ 2 - 2 * s2 ^ 2 + 3 * x)) + 2 * (s2 * (s2 ^ 2 - 3 * x) + y))) * hl5
  -- eliminate the chord slope `s3` brick by brick: `(Y3−Y2)·d³`, `(X3+X2)·d²`
  have hs3Y : (-(s3 * (s3 ^ 2 - 2 * s2 ^ 2 + 3 * x)) + 2 * (s2 * (s2 ^ 2 - 3 * x) + y))
        * (s2 ^ 2 - 3 * x) ^ 3
      = (s2 * (s2 ^ 2 - 3 * x) + 2 * y) ^ 3
        - (2 * s2 ^ 2 - 3 * x) * ((s2 ^ 2 - 3 * x) ^ 2 * (s2 * (s2 ^ 2 - 3 * x) + 2 * y))
        + 2 * ((s2 * (s2 ^ 2 - 3 * x) + y) * (s2 ^ 2 - 3 * x) ^ 3) := by
    linear_combination
      ((2 * s2 ^ 2 - 3 * x) * (s2 ^ 2 - 3 * x) ^ 2
        - (((s2 ^ 2 - 3 * x) * s3) ^ 2
          + (-(s2 * (s2 ^ 2 - 3 * x) + y) - y) * ((s2 ^ 2 - 3 * x) * s3)
          + (-(s2 * (s2 ^ 2 - 3 * x) + y) - y) ^ 2)) * hl3
  have hs3E : (s3 ^ 2 - x) * (s2 ^ 2 - 3 * x) ^ 2
      = (s2 * (s2 ^ 2 - 3 * x) + 2 * y) ^ 2 - x * (s2 ^ 2 - 3 * x) ^ 2 := by
    linear_combination
      ((s2 ^ 2 - 3 * x) * s3 + (-(s2 * (s2 ^ 2 - 3 * x) + y) - y)) * hl3
  -- assemble: `[x(5P)·(X3−X2)²]·(x(2P)−x)⁶ = G(x, y, s2)` — no `s3`, no `s5`
  have hs3F : ((-(s3 * (s3 ^ 2 - 2 * s2 ^ 2 + 3 * x)) + 2 * (s2 * (s2 ^ 2 - 3 * x) + y)) ^ 2
        - ((s3 ^ 2 - s2 ^ 2 + x) + (s2 ^ 2 - 2 * x)) * (s3 ^ 2 - 2 * s2 ^ 2 + 3 * x) ^ 2)
        * (s2 ^ 2 - 3 * x) ^ 6
      = ((s2 * (s2 ^ 2 - 3 * x) + 2 * y) ^ 3
          - (2 * s2 ^ 2 - 3 * x) * ((s2 ^ 2 - 3 * x) ^ 2 * (s2 * (s2 ^ 2 - 3 * x) + 2 * y))
          + 2 * ((s2 * (s2 ^ 2 - 3 * x) + y) * (s2 ^ 2 - 3 * x) ^ 3)) ^ 2
        - ((s2 * (s2 ^ 2 - 3 * x) + 2 * y) ^ 2 - x * (s2 ^ 2 - 3 * x) ^ 2)
          * ((-(s2 * (s2 ^ 2 - 3 * x) + y) - y) ^ 2
            - (2 * (s2 ^ 2 - 2 * x) + x) * (s2 ^ 2 - 3 * x) ^ 2) ^ 2 := by
    linear_combination
      ((-(s3 * (s3 ^ 2 - 2 * s2 ^ 2 + 3 * x)) + 2 * (s2 * (s2 ^ 2 - 3 * x) + y))
          * (s2 ^ 2 - 3 * x) ^ 3
        + ((s2 * (s2 ^ 2 - 3 * x) + 2 * y) ^ 3
          - (2 * s2 ^ 2 - 3 * x) * ((s2 ^ 2 - 3 * x) ^ 2 * (s2 * (s2 ^ 2 - 3 * x) + 2 * y))
          + 2 * ((s2 * (s2 ^ 2 - 3 * x) + y) * (s2 ^ 2 - 3 * x) ^ 3))) * hs3Y
      - (s3 ^ 2 - 2 * s2 ^ 2 + 3 * x) ^ 2 * (s2 ^ 2 - 3 * x) ^ 4 * hs3E
      - ((s2 * (s2 ^ 2 - 3 * x) + 2 * y) ^ 2 - x * (s2 ^ 2 - 3 * x) ^ 2)
        * ((s3 ^ 2 - 2 * s2 ^ 2 + 3 * x) * (s2 ^ 2 - 3 * x) ^ 2
          + ((-(s2 * (s2 ^ 2 - 3 * x) + y) - y) ^ 2
            - (2 * (s2 ^ 2 - 2 * x) + x) * (s2 ^ 2 - 3 * x) ^ 2)) * hs3D
  -- the repo's standard doubling identities (as in `triple_x_core`)
  have hId : (s2 ^ 2 - 3 * x) * (4 * y ^ 2) = -(3 * x ^ 4 + 84 * x) := by
    linear_combination (s2 * (2 * y) + 3 * x ^ 2) * hl2 - 12 * x * hcurve
  have hIdsq : (s2 ^ 2 - 3 * x) ^ 2 * (16 * y ^ 4) = (3 * x ^ 4 + 84 * x) ^ 2 := by
    linear_combination ((s2 ^ 2 - 3 * x) * (4 * y ^ 2) - (3 * x ^ 4 + 84 * x)) * hId
  -- square of `hquint`: trades the chord denominator for `preΨ₅(x)²`
  have hquintsq : (s3 ^ 2 - 2 * s2 ^ 2 + 3 * x) ^ 2
        * ((s2 ^ 2 - 3 * x) ^ 4 * (4096 * y ^ 12))
      = (5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656) ^ 2 := by
    linear_combination
      ((s3 ^ 2 - 2 * s2 ^ 2 + 3 * x) * ((s2 ^ 2 - 3 * x) ^ 2 * (64 * y ^ 6))
        - (5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656)) * hquint
  -- the master certificate in `(x, y, s2)` (sympy-designed cofactors, kernel-verified)
  have hmaster : (((s2 * (s2 ^ 2 - 3 * x) + 2 * y) ^ 3
          - (2 * s2 ^ 2 - 3 * x) * ((s2 ^ 2 - 3 * x) ^ 2 * (s2 * (s2 ^ 2 - 3 * x) + 2 * y))
          + 2 * ((s2 * (s2 ^ 2 - 3 * x) + y) * (s2 ^ 2 - 3 * x) ^ 3)) ^ 2
        - ((s2 * (s2 ^ 2 - 3 * x) + 2 * y) ^ 2 - x * (s2 ^ 2 - 3 * x) ^ 2)
          * ((-(s2 * (s2 ^ 2 - 3 * x) + y) - y) ^ 2
            - (2 * (s2 ^ 2 - 2 * x) + x) * (s2 ^ 2 - 3 * x) ^ 2) ^ 2)
        * (2 * y) ^ 16
      = (x ^ 25 - 14560 * x ^ 22 + 2465680 * x ^ 19 + 125894720 * x ^ 16
          + 7022444800 * x ^ 13 + 58687354880 * x ^ 10 + 330094858240 * x ^ 7
          + 877040353280 * x ^ 4 - 1889009991680 * x) * (3 * x ^ 4 + 84 * x) ^ 2 := by
    linear_combination
      (32768 * s2 ^ 15 * x * y ^ 15 + 49152 * s2 ^ 14 * x ^ 3 * y ^ 14
        + 393216 * s2 ^ 14 * y ^ 16 + 73728 * s2 ^ 13 * x ^ 5 * y ^ 13
        - 196608 * s2 ^ 13 * x ^ 2 * y ^ 15 + 110592 * s2 ^ 12 * x ^ 7 * y ^ 12
        - 294912 * s2 ^ 12 * x ^ 4 * y ^ 14 - 6946816 * s2 ^ 12 * x * y ^ 16
        + 165888 * s2 ^ 11 * x ^ 9 * y ^ 11 - 442368 * s2 ^ 11 * x ^ 6 * y ^ 13
        - 2162688 * s2 ^ 11 * x ^ 3 * y ^ 15 + 1966080 * s2 ^ 11 * y ^ 17
        + 248832 * s2 ^ 10 * x ^ 11 * y ^ 10 - 663552 * s2 ^ 10 * x ^ 8 * y ^ 12
        - 3244032 * s2 ^ 10 * x ^ 5 * y ^ 14 + 53673984 * s2 ^ 10 * x ^ 2 * y ^ 16
        + 373248 * s2 ^ 9 * x ^ 13 * y ^ 9 - 995328 * s2 ^ 9 * x ^ 10 * y ^ 11
        - 4866048 * s2 ^ 9 * x ^ 7 * y ^ 13 + 30965760 * s2 ^ 9 * x ^ 4 * y ^ 15
        - 28835840 * s2 ^ 9 * x * y ^ 17 + 559872 * s2 ^ 8 * x ^ 15 * y ^ 8
        - 1492992 * s2 ^ 8 * x ^ 12 * y ^ 10 - 7299072 * s2 ^ 8 * x ^ 9 * y ^ 12
        + 46448640 * s2 ^ 8 * x ^ 6 * y ^ 14 - 237895680 * s2 ^ 8 * x ^ 3 * y ^ 16
        + 2621440 * s2 ^ 8 * y ^ 18 + 839808 * s2 ^ 7 * x ^ 17 * y ^ 7
        - 2239488 * s2 ^ 7 * x ^ 14 * y ^ 9 - 10948608 * s2 ^ 7 * x ^ 11 * y ^ 11
        + 69672960 * s2 ^ 7 * x ^ 8 * y ^ 13 - 171048960 * s2 ^ 7 * x ^ 5 * y ^ 15
        + 172621824 * s2 ^ 7 * x ^ 2 * y ^ 17 + 1259712 * s2 ^ 6 * x ^ 19 * y ^ 6
        - 3359232 * s2 ^ 6 * x ^ 16 * y ^ 8 - 16422912 * s2 ^ 6 * x ^ 13 * y ^ 10
        + 104509440 * s2 ^ 6 * x ^ 10 * y ^ 12 - 256573440 * s2 ^ 6 * x ^ 7 * y ^ 14
        + 665911296 * s2 ^ 6 * x ^ 4 * y ^ 16 - 30408704 * s2 ^ 6 * x * y ^ 18
        + 1889568 * s2 ^ 5 * x ^ 21 * y ^ 5 - 5038848 * s2 ^ 5 * x ^ 18 * y ^ 7
        - 24634368 * s2 ^ 5 * x ^ 15 * y ^ 9 + 156764160 * s2 ^ 5 * x ^ 12 * y ^ 11
        - 384860160 * s2 ^ 5 * x ^ 9 * y ^ 13 + 552960000 * s2 ^ 5 * x ^ 6 * y ^ 15
        - 536346624 * s2 ^ 5 * x ^ 3 * y ^ 17 + 1048576 * s2 ^ 5 * y ^ 19
        + 2834352 * s2 ^ 4 * x ^ 23 * y ^ 4 - 7558272 * s2 ^ 4 * x ^ 20 * y ^ 6
        - 36951552 * s2 ^ 4 * x ^ 17 * y ^ 8 + 235146240 * s2 ^ 4 * x ^ 14 * y ^ 10
        - 577290240 * s2 ^ 4 * x ^ 11 * y ^ 12 + 829440000 * s2 ^ 4 * x ^ 8 * y ^ 14
        - 1218576384 * s2 ^ 4 * x ^ 5 * y ^ 16 + 133693440 * s2 ^ 4 * x ^ 2 * y ^ 18
        + 4251528 * s2 ^ 3 * x ^ 25 * y ^ 3 - 11337408 * s2 ^ 3 * x ^ 22 * y ^ 5
        - 55427328 * s2 ^ 3 * x ^ 19 * y ^ 7 + 352719360 * s2 ^ 3 * x ^ 16 * y ^ 9
        - 865935360 * s2 ^ 3 * x ^ 13 * y ^ 11 + 1244160000 * s2 ^ 3 * x ^ 10 * y ^ 13
        - 1159004160 * s2 ^ 3 * x ^ 7 * y ^ 15 + 904790016 * s2 ^ 3 * x ^ 4 * y ^ 17
        - 8912896 * s2 ^ 3 * x * y ^ 19 + 6377292 * s2 ^ 2 * x ^ 27 * y ^ 2
        - 17006112 * s2 ^ 2 * x ^ 24 * y ^ 4 - 83140992 * s2 ^ 2 * x ^ 21 * y ^ 6
        + 529079040 * s2 ^ 2 * x ^ 18 * y ^ 8 - 1298903040 * s2 ^ 2 * x ^ 15 * y ^ 10
        + 1866240000 * s2 ^ 2 * x ^ 12 * y ^ 12 - 1738506240 * s2 ^ 2 * x ^ 9 * y ^ 14
        + 1452736512 * s2 ^ 2 * x ^ 6 * y ^ 16 - 268173312 * s2 ^ 2 * x ^ 3 * y ^ 18
        + 9565938 * s2 * x ^ 29 * y - 25509168 * s2 * x ^ 26 * y ^ 3
        - 124711488 * s2 * x ^ 23 * y ^ 5 + 793618560 * s2 * x ^ 20 * y ^ 7
        - 1948354560 * s2 * x ^ 17 * y ^ 9 + 2799360000 * s2 * x ^ 14 * y ^ 11
        - 2607759360 * s2 * x ^ 11 * y ^ 13 + 1605795840 * s2 * x ^ 8 * y ^ 15
        - 784465920 * s2 * x ^ 5 * y ^ 17 + 25165824 * s2 * x ^ 2 * y ^ 19
        + 14348907 * x ^ 31 - 38263752 * x ^ 28 * y ^ 2 - 187067232 * x ^ 25 * y ^ 4
        + 1190427840 * x ^ 22 * y ^ 6 - 2922531840 * x ^ 19 * y ^ 8
        + 4199040000 * x ^ 16 * y ^ 10 - 3911639040 * x ^ 13 * y ^ 12
        + 2408693760 * x ^ 10 * y ^ 14 - 1081147392 * x ^ 7 * y ^ 16
        + 221773824 * x ^ 4 * y ^ 18) * hl2
      + (-43046712 * x ^ 30 + 71744544 * x ^ 27 * y ^ 2 + 301196448 * x ^ 27
        + 632946240 * x ^ 24 * y ^ 4 - 201015360 * x ^ 24 * y ^ 2 - 2093515200 * x ^ 24
        - 2938337280 * x ^ 21 * y ^ 6 - 4631639040 * x ^ 21 * y ^ 4
        - 686407680 * x ^ 21 * y ^ 2 + 16927626240 * x ^ 21 + 5829258240 * x ^ 18 * y ^ 8
        + 15936721920 * x ^ 18 * y ^ 6 + 31735065600 * x ^ 18 * y ^ 4
        + 21732480000 * x ^ 18 * y ^ 2 + 25557396480 * x ^ 18
        - 6767861760 * x ^ 15 * y ^ 10 - 24868085760 * x ^ 15 * y ^ 8
        - 79821987840 * x ^ 15 * y ^ 6 - 200412979200 * x ^ 15 * y ^ 4
        - 126569963520 * x ^ 15 * y ^ 2 + 4776909742080 * x ^ 15
        + 4967055360 * x ^ 12 * y ^ 12 + 22506946560 * x ^ 12 * y ^ 10
        + 94254612480 * x ^ 12 * y ^ 8 + 358340935680 * x ^ 12 * y ^ 6
        + 1276320890880 * x ^ 12 * y ^ 4 + 5662899486720 * x ^ 12 * y ^ 2
        + 48661282897920 * x ^ 12 - 2259025920 * x ^ 9 * y ^ 14
        - 12262440960 * x ^ 9 * y ^ 12 - 63294013440 * x ^ 9 * y ^ 10
        - 301441351680 * x ^ 9 * y ^ 8 - 1232065658880 * x ^ 9 * y ^ 6
        - 3271346749440 * x ^ 9 * y ^ 4 + 9020986490880 * x ^ 9 * y ^ 2
        + 247730167480320 * x ^ 9 + 554434560 * x ^ 6 * y ^ 16
        + 3550740480 * x ^ 6 * y ^ 14 + 22543073280 * x ^ 6 * y ^ 12
        + 141616742400 * x ^ 6 * y ^ 10 + 878023802880 * x ^ 6 * y ^ 8
        + 5353112862720 * x ^ 6 * y ^ 6 + 31920413736960 * x ^ 6 * y ^ 4
        + 184583262044160 * x ^ 6 * y ^ 2 + 1020065395507200 * x ^ 6
        - 47185920 * x ^ 3 * y ^ 18 - 330301440 * x ^ 3 * y ^ 16
        - 2312110080 * x ^ 3 * y ^ 14 - 16184770560 * x ^ 3 * y ^ 12
        - 113293393920 * x ^ 3 * y ^ 10 - 793053757440 * x ^ 3 * y ^ 8
        - 5551376302080 * x ^ 3 * y ^ 6 - 38859634114560 * x ^ 3 * y ^ 4
        - 272017438801920 * x ^ 3 * y ^ 2 - 1904122071613440 * x ^ 3) * hcurve
  -- assemble, then cancel the auxiliary `(x(2P)−x)²·(2y)¹⁶ ≠ 0`
  have hkey : ((s5 ^ 2 - (s3 ^ 2 - s2 ^ 2 + x) - (s2 ^ 2 - 2 * x))
        * (25 * x ^ 24 + 26600 * x ^ 21 + 6958000 * x ^ 18 - 68051200 * x ^ 15
          - 2787464960 * x ^ 12 + 9637806080 * x ^ 9 + 315638149120 * x ^ 6
          + 674646425600 * x ^ 3 + 377801998336))
        * ((s2 ^ 2 - 3 * x) ^ 2 * (2 * y) ^ 16)
      = (x ^ 25 - 14560 * x ^ 22 + 2465680 * x ^ 19 + 125894720 * x ^ 16
          + 7022444800 * x ^ 13 + 58687354880 * x ^ 10 + 330094858240 * x ^ 7
          + 877040353280 * x ^ 4 - 1889009991680 * x)
        * ((s2 ^ 2 - 3 * x) ^ 2 * (2 * y) ^ 16) := by
    linear_combination
      (-(s5 ^ 2 - (s3 ^ 2 - s2 ^ 2 + x) - (s2 ^ 2 - 2 * x))
        * ((s2 ^ 2 - 3 * x) ^ 2 * (2 * y) ^ 16)) * hquintsq
      + 268435456 * y ^ 28 * (s2 ^ 2 - 3 * x) ^ 6 * hBF5
      + 268435456 * y ^ 28 * hs3F
      + 4096 * y ^ 12 * hmaster
      + (-(4096 * y ^ 12)
        * (x ^ 25 - 14560 * x ^ 22 + 2465680 * x ^ 19 + 125894720 * x ^ 16
          + 7022444800 * x ^ 13 + 58687354880 * x ^ 10 + 330094858240 * x ^ 7
          + 877040353280 * x ^ 4 - 1889009991680 * x)) * hIdsq
  exact mul_right_cancel₀ (mul_ne_zero (pow_ne_zero 2 hd) (pow_ne_zero 16 h2y)) hkey

/-- **N7@5 — the multiplication-by-5 `x`-coordinate formula for secp256k1.**
Whenever `5 • P` is an affine point `(X, Y)`, its `x`-coordinate equals Mathlib's
`Φ₅/ΨSq₅` evaluated at `x(P)` — with no side conditions: the generic case goes
through the tangent-chord-chord construction (`5P = 3P + 2P`) and `quint_x_core`;
the 2-torsion case (`5P = P`) holds because `Ψ₂Sq(x) = 0` collapses
`Φ₅ − x·ΨSq₅`, with `ΨSq₅(x) ≠ 0` from the `Ψ₂Sq ⊥ preΨ₅` Bézout certificate;
the 3-torsion case (`5P = 2P`) reduces to the `n = 2` formula, with the
cross-multiplied difference divisible by `Ψ₃` and `ΨSq₅(x) ≠ 0` from the
`Ψ₃ ⊥ preΨ₅` Bézout certificate. -/
theorem secp256k1_quintuple_x_eq_Φ₅_div_ΨSq₅
    {x y X Y : ZMod Secp256k1.p} (h : secp256k1.toAffine.Nonsingular x y)
    {h' : secp256k1.toAffine.Nonsingular X Y}
    (hEq : (5 : ℕ) • (Point.some x y h) = Point.some X Y h') :
    X = (secp256k1.Φ 5).eval x / (secp256k1.ΨSq 5).eval x := by
  rw [Φ₅_eval, ΨSq₅_eval]
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
  · -- 2-torsion branch: `2P = O`, so `5P = P` and `X = x`.
    have h2P : (2 : ℕ) • (Point.some x y h) = 0 := by
      rw [two_nsmul]; exact Point.add_self_of_Y_eq hy0
    have h5P : (5 : ℕ) • (Point.some x y h) = Point.some x y h := by
      rw [show (5 : ℕ) = 1 + 2 + 2 from rfl, add_nsmul, add_nsmul, one_nsmul, h2P,
        add_zero, add_zero]
    rw [h5P, Point.some.injEq] at hEq
    rw [← hEq.1]
    -- on 2-torsion, `y = 0` hence `Ψ₂Sq(x) = 4x³ + 28 = 0`
    have hy00 : y = 0 := by
      rw [hnegY] at hy0
      have h2y0 : (2 : ZMod Secp256k1.p) * y = 0 := by linear_combination hy0
      rcases mul_eq_zero.mp h2y0 with hc | hc
      · exact absurd hc h2
      · exact hc
    have hΨ2z : (4 : ZMod Secp256k1.p) * x ^ 3 + 28 = 0 := by
      rw [hy00] at hcurve
      linear_combination -4 * hcurve
    -- `preΨ₅(x) ≠ 0`: a common root of `Ψ₂Sq` and `preΨ₅` would contradict Bézout
    have hpre5ne : 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656
        ≠ 0 := by
      intro hc
      obtain ⟨u, v, huv⟩ := secp256k1_isCoprime_Ψ₂Sq_preΨ₅
      have hev := congrArg (Polynomial.eval x) huv
      simp only [Polynomial.eval_add, Polynomial.eval_mul, Polynomial.eval_one] at hev
      rw [secp256k1_Ψ₂Sq_eval, preΨ₅_eval, hΨ2z, hc] at hev
      simp at hev
    have hdenne : (25 : ZMod Secp256k1.p) * x ^ 24 + 26600 * x ^ 21 + 6958000 * x ^ 18
        - 68051200 * x ^ 15 - 2787464960 * x ^ 12 + 9637806080 * x ^ 9
        + 315638149120 * x ^ 6 + 674646425600 * x ^ 3 + 377801998336 ≠ 0 := by
      rw [show (25 : ZMod Secp256k1.p) * x ^ 24 + 26600 * x ^ 21 + 6958000 * x ^ 18
          - 68051200 * x ^ 15 - 2787464960 * x ^ 12 + 9637806080 * x ^ 9
          + 315638149120 * x ^ 6 + 674646425600 * x ^ 3 + 377801998336
          = (5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656) ^ 2 by ring]
      exact pow_ne_zero 2 hpre5ne
    rw [eq_div_iff hdenne]
    linear_combination
      (6 * x ^ 22 + 10248 * x ^ 19 + 1051344 * x ^ 16 - 55845888 * x ^ 13
        - 2061556224 * x ^ 10 + 2168506368 * x ^ 7 - 18793721856 * x ^ 4
        + 80957571072 * x) * hΨ2z
  · -- `y ≠ negY`, so `y ≠ 0` and `P` is not 2-torsion
    have hy : y ≠ 0 := fun h0 => hy0 (by rw [hnegY, h0]; ring)
    have h2y : (2 : ZMod Secp256k1.p) * y ≠ 0 := mul_ne_zero h2 hy
    by_cases h3 : (3 : ℕ) • (Point.some x y h) = 0
    · -- 3-torsion branch: `3P = O`, so `5P = 2P` and `X = x(2P) = Φ₂/Ψ₂Sq`.
      have h34 : 3 * x ^ 4 + 84 * x = 0 := by
        have := (secp256k1_three_nsmul_eq_zero_iff x y h).mp h3
        rwa [secp256k1_psi3_evalEval] at this
      have h5P2 : (5 : ℕ) • (Point.some x y h) = (2 : ℕ) • (Point.some x y h) := by
        rw [show (5 : ℕ) = 2 + 3 from rfl, add_nsmul, h3, add_zero]
      set s2 := secp256k1.toAffine.slope x x y y with hs2def
      set X2 := secp256k1.toAffine.addX x x s2 with hX2def
      set Y2 := secp256k1.toAffine.addY x x y s2 with hY2def
      have hns2 : secp256k1.toAffine.Nonsingular X2 Y2 :=
        nonsingular_add h h (fun hxy => hy0 hxy.2)
      have hP2 : (2 : ℕ) • (Point.some x y h) = Point.some X2 Y2 hns2 := by
        rw [two_nsmul]; exact Point.add_self_of_Y_ne hy0
      rw [h5P2, hP2, Point.some.injEq] at hEq
      rw [← hEq.1, hX2def, hs2def, secp256k1_double_x_eq_Φ₂_div_Ψ₂Sq x y hcurve hy0,
        secp256k1_Φ₂_eval, secp256k1_Ψ₂Sq_eval]
      -- goal: `(x⁴ − 56x)/(4x³ + 28) = Φ₅(x)/ΨSq₅(x)`, cross-multiply
      have hd2ne : (4 : ZMod Secp256k1.p) * x ^ 3 + 28 ≠ 0 := by
        intro hcz
        exact mul_ne_zero h2y h2y (by linear_combination 4 * hcurve + hcz)
      -- `preΨ₅(x) ≠ 0`: a common root of `Ψ₃` and `preΨ₅` would contradict Bézout
      have hpre5ne : 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656
          ≠ 0 := by
        intro hc
        obtain ⟨u, v, huv⟩ := secp256k1_isCoprime_Ψ₃_preΨ₅
        have hev := congrArg (Polynomial.eval x) huv
        simp only [Polynomial.eval_add, Polynomial.eval_mul, Polynomial.eval_one] at hev
        rw [secp256k1_Ψ₃_eval, preΨ₅_eval, h34, hc] at hev
        simp at hev
      have hdenne : (25 : ZMod Secp256k1.p) * x ^ 24 + 26600 * x ^ 21 + 6958000 * x ^ 18
          - 68051200 * x ^ 15 - 2787464960 * x ^ 12 + 9637806080 * x ^ 9
          + 315638149120 * x ^ 6 + 674646425600 * x ^ 3 + 377801998336 ≠ 0 := by
        rw [show (25 : ZMod Secp256k1.p) * x ^ 24 + 26600 * x ^ 21 + 6958000 * x ^ 18
            - 68051200 * x ^ 15 - 2787464960 * x ^ 12 + 9637806080 * x ^ 9
            + 315638149120 * x ^ 6 + 674646425600 * x ^ 3 + 377801998336
            = (5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656) ^ 2 by ring]
        exact pow_ne_zero 2 hpre5ne
      rw [div_eq_div_iff hd2ne hdenne]
      linear_combination
        (7 * x ^ 24 + 27608 * x ^ 21 - 2101904 * x ^ 18 - 284585728 * x ^ 15
          - 2228742656 * x ^ 12 - 26142548992 * x ^ 9 - 330576748544 * x ^ 6
          - 661153497088 * x ^ 3 + 377801998336) * h34
    · -- generic branch: `5P = 3P + 2P` through tangent-chord-chord, then the core.
      have hYd : y - secp256k1.toAffine.negY x y ≠ 0 := sub_ne_zero.mpr hy0
      have h5Pne : (5 : ℕ) • (Point.some x y h) ≠ 0 := by
        rw [hEq]; exact Point.some_ne_zero h'
      have hpre5ne : 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3 - 614656
          ≠ 0 := fun hc => h5Pne ((secp256k1_five_nsmul_eq_zero_iff x y h).mpr
        (by rw [secp256k1_psi5_evalEval x y hcurve]; exact hc))
      have hΨ3ne : 3 * x ^ 4 + 84 * x ≠ 0 := fun hc =>
        h3 ((secp256k1_three_nsmul_eq_zero_iff x y h).mpr
          (by rw [secp256k1_psi3_evalEval]; exact hc))
      have h64 : (64 : ZMod Secp256k1.p) ≠ 0 := by
        rw [show (64 : ZMod Secp256k1.p) = 2 ^ 6 by norm_num]
        exact pow_ne_zero 6 h2
      set s2 := secp256k1.toAffine.slope x x y y with hs2def
      set X2 := secp256k1.toAffine.addX x x s2 with hX2def
      set Y2 := secp256k1.toAffine.addY x x y s2 with hY2def
      have hsl2 : s2 * (2 * y) = 3 * x ^ 2 := by
        rw [hs2def, slope_of_Y_ne rfl hy0, div_mul_eq_mul_div, div_eq_iff hYd]
        simp only [secp256k1, WeierstrassCurve.Affine.negY]
        ring
      have hId : (s2 ^ 2 - 3 * x) * (4 * y ^ 2) = -(3 * x ^ 4 + 84 * x) := by
        linear_combination (2 * s2 * y + 3 * x ^ 2) * hsl2 + (-12 * x) * hcurve
      have hd : s2 ^ 2 - 3 * x ≠ 0 := by
        intro hc
        apply hΨ3ne
        have := hId
        rw [hc, zero_mul] at this
        linear_combination this
      have hx2val : X2 = s2 ^ 2 - 2 * x := by
        rw [hX2def]; simp only [WeierstrassCurve.Affine.addX, secp256k1]; ring
      have hx2x : X2 - x = s2 ^ 2 - 3 * x := by rw [hx2val]; ring
      have hx2ne : X2 ≠ x := by rw [← sub_ne_zero, hx2x]; exact hd
      have hy2val : Y2 = -(s2 * (s2 ^ 2 - 3 * x) + y) := by
        rw [hY2def]
        simp only [WeierstrassCurve.Affine.addY, WeierstrassCurve.Affine.negAddY,
          WeierstrassCurve.Affine.negY, WeierstrassCurve.Affine.addX, secp256k1]
        ring
      have hns2 : secp256k1.toAffine.Nonsingular X2 Y2 :=
        nonsingular_add h h (fun hxy => hy0 hxy.2)
      have hP2 : (2 : ℕ) • (Point.some x y h) = Point.some X2 Y2 hns2 := by
        rw [two_nsmul]; exact Point.add_self_of_Y_ne hy0
      set s3 := secp256k1.toAffine.slope X2 x Y2 y with hs3def
      set X3 := secp256k1.toAffine.addX X2 x s3 with hX3def
      set Y3 := secp256k1.toAffine.addY X2 x Y2 s3 with hY3def
      have hx3val : X3 = s3 ^ 2 - (s2 ^ 2 - 2 * x) - x := by
        rw [hX3def]
        simp only [WeierstrassCurve.Affine.addX, secp256k1]
        rw [hx2val]; ring
      have hns3 : secp256k1.toAffine.Nonsingular X3 Y3 :=
        nonsingular_add hns2 h (fun hxy => hx2ne hxy.1)
      have hP3 : (3 : ℕ) • (Point.some x y h) = Point.some X3 Y3 hns3 := by
        rw [show (3 : ℕ) = 2 + 1 from rfl, add_nsmul, one_nsmul, hP2]
        exact Point.add_some (fun hxy => hx2ne hxy.1)
      have hsl3s : s3 * (X2 - x) = Y2 - y := by
        rw [hs3def, slope_of_X_ne hx2ne]
        exact div_mul_cancel₀ _ (sub_ne_zero.mpr hx2ne)
      have hl3 : (s2 ^ 2 - 3 * x) * s3 = -(s2 * (s2 ^ 2 - 3 * x) + y) - y := by
        have hstep := hsl3s
        rw [hy2val, hx2x] at hstep
        linear_combination hstep
      -- `X3 ≠ X2` from `5P ≠ O`, via `five_core` (the 5-torsion bridge)
      have hxiff : X2 = X3 ↔ 5 * x ^ 12 + 2660 * x ^ 9 - 11760 * x ^ 6 - 548800 * x ^ 3
          - 614656 = 0 := by
        rw [hx3val, hx2val, eq_comm]
        exact five_core x y s2 s3 h64 hcurve hy (by linear_combination hsl2) hd hl3
      have hx32ne : X3 ≠ X2 := fun hc => hpre5ne (hxiff.mp hc.symm)
      have hx3x2 : X3 - X2 = s3 ^ 2 - 2 * s2 ^ 2 + 3 * x := by
        rw [hx3val, hx2val]; ring
      have hd5 : s3 ^ 2 - 2 * s2 ^ 2 + 3 * x ≠ 0 := by
        rw [← hx3x2]; exact sub_ne_zero.mpr hx32ne
      have hy3val : Y3 = -(s3 * (s3 ^ 2 - 2 * s2 ^ 2 + 3 * x)) + s2 * (s2 ^ 2 - 3 * x)
          + y := by
        rw [hY3def]
        simp only [WeierstrassCurve.Affine.addY, WeierstrassCurve.Affine.negAddY,
          WeierstrassCurve.Affine.negY, WeierstrassCurve.Affine.addX, secp256k1]
        rw [hx2val, hy2val]; ring
      set s5 := secp256k1.toAffine.slope X3 X2 Y3 Y2 with hs5def
      set X5 := secp256k1.toAffine.addX X3 X2 s5 with hX5def
      set Y5 := secp256k1.toAffine.addY X3 X2 Y3 s5 with hY5def
      have hx5val : X5 = s5 ^ 2 - (s3 ^ 2 - s2 ^ 2 + x) - (s2 ^ 2 - 2 * x) := by
        rw [hX5def]
        simp only [WeierstrassCurve.Affine.addX, secp256k1]
        rw [hx3val, hx2val]; ring
      have hns5 : secp256k1.toAffine.Nonsingular X5 Y5 :=
        nonsingular_add hns3 hns2 (fun hxy => hx32ne hxy.1)
      have hP5 : (5 : ℕ) • (Point.some x y h) = Point.some X5 Y5 hns5 := by
        rw [show (5 : ℕ) = 3 + 2 from rfl, add_nsmul, hP3, hP2]
        exact Point.add_some (fun hxy => hx32ne hxy.1)
      have hsl5s : s5 * (X3 - X2) = Y3 - Y2 := by
        rw [hs5def, slope_of_X_ne hx32ne]
        exact div_mul_cancel₀ _ (sub_ne_zero.mpr hx32ne)
      have hl5 : (s3 ^ 2 - 2 * s2 ^ 2 + 3 * x) * s5
          = -(s3 * (s3 ^ 2 - 2 * s2 ^ 2 + 3 * x)) + 2 * (s2 * (s2 ^ 2 - 3 * x) + y) := by
        have hstep := hsl5s
        rw [hx3x2, hy3val, hy2val] at hstep
        linear_combination hstep
      rw [hP5, Point.some.injEq] at hEq
      rw [← hEq.1, hx5val]
      exact quint_x_core x y s2 s3 s5 hcurve hy h2 (by linear_combination hsl2) hd hl3
        hd5 hl5

end Ecdlp.Curve
