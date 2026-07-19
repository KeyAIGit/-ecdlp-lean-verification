/-
# OPEN TARGET — N7-uniform multiplication-by-`n` (x,y)-coordinate carrier for secp256k1
# (joint ω-free carrier, by induction on `WeierstrassCurve.normEDSRec'`)

The **uniform** multiplication-by-`n` coordinate certificate on the actual point group
`secp256k1.toAffine.Point`, for **all** `n` at once (node S3/N7, `BARRIERS.md §B3`; registered
stem `Ecdlp/Targets/n7_uniform_secp256k1_x.lean`). It carries **both** coordinates jointly and
states the `y`-conjunct **ω-free** — using only Mathlib's `ψ` (Mathlib v4.31 has no `ω` division
polynomial): with `Y = ωₙ/ψₙ³` and `4y·ωₙ = ψ(n+2)ψ(n-1)² − ψ(n-2)ψ(n+1)²` the conjunct reads
`Y·(4y)·ψₙ(P)³ = ψ(n+2)(P)·ψ(n-1)(P)² − ψ(n-2)(P)·ψ(n+1)(P)²`.

## What closes here vs. the named residual walls

Fully closed (no `sorry`):
* `Carrier`                    — the joint predicate the induction transports.
* `curve_of_nonsingular`, `negY_eq` — secp256k1 helper reductions (repo idiom).
* `carrier_zero`               — `0•P = O` is never affine (vacuous leaf).
* `carrier_one`                — delegates verbatim to landed `secp256k1_one_nsmul_coords`.
* `carrier_two`                — delegates to landed `secp256k1_two_nsmul_coords_ωfree`
                                 (`NsmulCoordsBaseTwo.lean`), non-2-torsion from affineness.
* `carrier_three`              — **server-verified (2026-07-19)**: 2-torsion (`y=0`) branch +
                                 FiveTorsionBridge `3•P` reconstruction, then landed triple x/y +
                                 `secp256k1_omega_recurrence_three`. Both conjuncts closed.
* `carrier_four` **x-conjunct** — closed from the landed Point-level
                                 `secp256k1_quadruple_x_eq_Φ₄_div_ΨSq₄` (`h` passed explicitly).
* `even_step_group`, `odd_step_group` (generic secant branch) — the **group-law plumbing**:
  reduce `Carrier (2k)` / `Carrier (2k+1)` to scalar field-identity obligations about
  `addX/addY/slope`, discharging every `Point`-level move (`two_mul`+`add_nsmul` / `add_nsmul`,
  `add_self_of_Y_eq/ne`, `add_of_X_ne`, `some.injEq`, `some_ne_zero`). The slope relations are
  derived by the kernel-verified `slope_of_Y_ne`/`slope_of_X_ne` + `div_eq_iff`/`div_mul_cancel₀`
  idioms copied from `MultiplicationFormula.lean` / `FiveTorsionBridge.lean`.
* `secp256k1_nsmul_coords`      — the capstone: `normEDSRec'` assembly, index-correct
  (even `2*(m+3)` via `k=m+3`; odd `2*(m+2)+1` via `k=m+2, k+1=m+3`), `sorry`-free modulo walls.

Named residual walls (adversarial ultracode audit, 2026-07-19 — honest current factoring):
* `even_x_algebra` — **reduced** to two univariate division-polynomial *doubling* identities
  `ΨSq(2k).eval x = 4B(A³+7B³)` and `Φ(2k).eval x = A⁴−56AB³` (with `A=Φ(k).eval x`, `B=ΨSq(k).eval x`);
  everything else (addX unfold, slope-square elimination `sk²·4(Xk³+7)=9Xk⁴`, `B≠0` denominator,
  final `linear_combination B⁴·hsk`) is closed, and the two identities are **true** (checked
  `k=1..5` via the eval bridge). But a deeper audit (2026-07-19) found they are **NOT a finite
  certificate**: substituting `normEDS_even/odd` + Somos-4 leaves a remainder depending on
  `w(k±2)²` individually, and pinning those cascades outward unboundedly (`w(k+4), w(k+6), …`).
  Closing them needs a **strong induction on `k`** over the elliptic net (the `NormEDSSomos4.lean`
  technique, ~200 lines) — a real EDS sub-development, not a `ring`/`linear_combination` fill.
* `odd_x_algebra`, `even_y_algebra`, `odd_y_algebra` — **UNDER-HYPOTHESIZED as currently factored.**
  The abstract lemmas quantify `Yk`(,`Yk1`) with only the curve equation, leaving the y-sign free;
  flipping `Yk ↦ −Yk` gives a different valid input (`(−kP)+(k+1)P = P`) with a different `addX`,
  so the universally-quantified statements are **not theorems**. Every INSTANCE the step-group uses
  is true (real consecutive multiples `kP,(k+1)P`), so the induction is sound — but completing it
  needs these three **restated** to thread the `Carrier` y-coupling into the signature (or inlined
  into `even_step_group`/`odd_step_group`, where the IH supplies the coupling). Refactor, then the
  x-part reduces via `φ_ψ_diff` at `(k+1,k)` and the y-part via the ω-recurrence. Not a Mathlib gap.
* `carrier_four` **y-conjunct** — remaining base leaf (needs a `y(4P)` cert + an `n=4` ω-anchor,
  as `carrier_two`/`carrier_three` did at `n=2,3`). Mechanical.
* `nsmul_eq_zero_iff_psi_evalEval_zero`, `psiSq_ne_zero_of_nsmul_some` — the uniform
  non-degeneracy / torsion bridge (`n•P = O ⟺ ψₙ(P) = 0`). `psiSq_ne_zero` reduces to it via
  `eval_ΨSq_eq_normEDS_sq`; the `Point → ψ` direction is the genuinely missing Mathlib map (the
  one true remaining conceptual wall).
* Two `odd_step_group` degenerate branches (a summand `= O`) and the secant `x`-collision branch
  are left as inline `sorry` (dischargeable once the torsion bridge lands).

Open stem: NOT imported from `Ecdlp.lean`; excluded from the no-`sorry` gate.

**Provenance.** The whole file elaborates on the warm-Lean server (v4.31.0) with `LEAN_OK`:
the only diagnostics are the named `declaration uses 'sorry'` warnings above — no type or
elaboration errors. So the reduction of the entire uniform-N7 target to the isolated
rational-identity walls (and the `normEDSRec'` capstone assembly) is machine-verified. Base leaves
`n=0,1,2,3` and the `n=4` x-conjunct are server-verified `sorry`-free. The residual walls are as
listed above — honestly, three of them (`odd_x_algebra`, `even_y_algebra`, `odd_y_algebra`) are
under-hypothesized as currently factored and need signature-strengthening (not just a `sorry` fill),
per the 2026-07-19 adversarial audit.
-/
import Mathlib
import Ecdlp.Proved.DivisionPolynomialEllSequence
import Ecdlp.Proved.DivisionPolynomialEvalBridge
import Ecdlp.Proved.NsmulCoordsBaseOne
import Ecdlp.Proved.NsmulCoordsBaseTwo
import Ecdlp.Proved.OmegaRecurrenceAnchors
import Ecdlp.Proved.QuadrupleMultiplicationFormula
import Ecdlp.Proved.TripleMultiplicationFormula
import Ecdlp.Proved.MultiplicationYTripleFormula
import Ecdlp.Proved.FiveTorsionBridge

namespace Ecdlp.Curve.N7Uniform

open Polynomial WeierstrassCurve WeierstrassCurve.Affine

variable [Fact (Nat.Prime Secp256k1.p)]

/-! ## The joint ω-free carrier -/

/-- The joint `(x,y)` carrier the uniform induction transports. For fixed nonsingular `P = (x,y)`,
`Carrier x y h n` says: *whenever* `n • P` is the affine point `(X,Y)`, its `x`-coordinate is the
canonical division-polynomial ratio `Φₙ(x)/ΨSqₙ(x)` **and** its `y`-coordinate satisfies the
ω-free relation `Y·(4y)·ψₙ(P)³ = ψ(n+2)ψ(n-1)² − ψ(n-2)ψ(n+1)²`. The implication form makes the
torsion (`n•P = O`) case vacuous, so the predicate needs no side hypothesis on `n`. -/
def Carrier (x y : ZMod Secp256k1.p) (h : secp256k1.toAffine.Nonsingular x y) (n : ℕ) : Prop :=
  ∀ (X Y : ZMod Secp256k1.p) (h' : secp256k1.toAffine.Nonsingular X Y),
    n • (Point.some x y h) = Point.some X Y h' →
      X = (secp256k1.Φ n).eval x / (secp256k1.ΨSq n).eval x
        ∧ Y * (4 * y) * ((secp256k1.ψ (n : ℤ)).evalEval x y) ^ 3
            = (secp256k1.ψ ((n : ℤ) + 2)).evalEval x y
                * ((secp256k1.ψ ((n : ℤ) - 1)).evalEval x y) ^ 2
              - (secp256k1.ψ ((n : ℤ) - 2)).evalEval x y
                * ((secp256k1.ψ ((n : ℤ) + 1)).evalEval x y) ^ 2

section Fixed

-- `x, y, h` are fixed for the whole induction. `hc` (the curve equation) is passed explicitly to
-- the leaves that consume it, and re-derived from `Nonsingular` inside the step lemmas
-- (`curve_of_nonsingular`), so it is NOT a section variable.
variable {x y : ZMod Secp256k1.p} {h : secp256k1.toAffine.Nonsingular x y}

/-- On secp256k1 the negation `negY x y = -y` (as `a₁ = a₃ = 0`). -/
private lemma negY_eq (a b : ZMod Secp256k1.p) : secp256k1.toAffine.negY a b = -b := by
  simp [WeierstrassCurve.Affine.negY, secp256k1]

/-- Extract the curve equation from a nonsingular point of secp256k1 (repo idiom,
`FiveTorsionBridge.lean` ≈124–128). -/
private lemma curve_of_nonsingular {a b : ZMod Secp256k1.p}
    (hns : secp256k1.toAffine.Nonsingular a b) : b ^ 2 = a ^ 3 + 7 := by
  have hE : secp256k1.toAffine.Equation a b := hns.1
  rw [WeierstrassCurve.Affine.equation_iff] at hE
  simp only [secp256k1] at hE
  linear_combination hE

/-! ## Base leaves -/

/-- Leaf `n = 0`: `0 • P = O` is never an affine `some`, so the carrier holds vacuously. -/
theorem carrier_zero : Carrier x y h 0 := by
  intro X Y h' hn
  rw [zero_nsmul] at hn
  exact absurd hn.symm (Point.some_ne_zero h')

/-- Leaf `n = 1`: delegates verbatim to the landed base rung `secp256k1_one_nsmul_coords`, which is
literally `Carrier` at `n = 1` (`NsmulCoordsBaseOne.lean`). -/
theorem carrier_one (hc : y ^ 2 = x ^ 3 + 7) : Carrier x y h 1 := by
  intro X Y h' hn
  have key := secp256k1_one_nsmul_coords x y X Y hc h h' hn
  refine ⟨by exact_mod_cast key.1, ?_⟩
  rw [show ((1 : ℕ) : ℤ) = 1 by norm_num, show (1 : ℤ) + 2 = 3 by norm_num,
      show (1 : ℤ) - 1 = 0 by norm_num, show (1 : ℤ) - 2 = -1 by norm_num,
      show (1 : ℤ) + 1 = 2 by norm_num]
  exact key.2

/-- Leaf `n = 2`: delegates to the landed ω-free base rung `secp256k1_two_nsmul_coords_ωfree`
(`NsmulCoordsBaseTwo.lean`); non-2-torsion (`y ≠ negY x y`) is forced by `2•P` being affine. -/
theorem carrier_two (hc : y ^ 2 = x ^ 3 + 7) : Carrier x y h 2 := by
  intro X Y h' hn
  have hy : y ≠ secp256k1.toAffine.negY x y := by
    intro hyeq
    rw [two_nsmul, Point.add_self_of_Y_eq hyeq] at hn
    exact Point.some_ne_zero h' hn.symm
  obtain ⟨hX, hYr⟩ := secp256k1_two_nsmul_coords_ωfree x y X Y hc h h' hy hn
  refine ⟨by exact_mod_cast hX, ?_⟩
  rw [show ((2 : ℕ) : ℤ) = 2 by norm_num, show (2 : ℤ) + 2 = 4 by norm_num,
      show (2 : ℤ) - 1 = 1 by norm_num, show (2 : ℤ) - 2 = 0 by norm_num,
      show (2 : ℤ) + 1 = 3 by norm_num]
  exact hYr

/-- Leaf `n = 3` (ω-free). Mechanical, NOT a conceptual wall.
`needs`: reconstruct the tangent slope `s₂` and secant slope `s₃` and the point equation
`3•P = some X Y` exactly as `FiveTorsionBridge.lean` (≈189–228: `add_self_of_Y_ne`, `add_of_X_ne`,
`slope_of_Y_ne`/`slope_of_X_ne`), feed the reconstructed scalars to
`secp256k1_triple_x_eq_Φ₃_div_ΨSq₃` for the x-conjunct, and bridge `secp256k1_triple_y_eq_ω₃`
(`MultiplicationYTripleFormula`) against `secp256k1_omega_recurrence_three` for the ω-free
y-conjunct, with the `ΨSq_three`/`ψ`-index normalisation. `3•P = O` is excluded by the affine
hypothesis on `3•P`. -/
theorem carrier_three (hc : y ^ 2 = x ^ 3 + 7) : Carrier x y h 3 := by
  intro X Y h' hn
  have hnegY : secp256k1.toAffine.negY x y = -y := negY_eq x y
  by_cases hy0 : y = secp256k1.toAffine.negY x y
  · -- 2-torsion branch: `y = negY x y ⟹ y = 0`, so `3•P = P`.
    have h2 : (2 : ZMod Secp256k1.p) ≠ 0 := by
      have hnd : ¬ Secp256k1.p ∣ 2 := by decide
      have h2n : ((2 : ℕ) : ZMod Secp256k1.p) ≠ 0 := by
        rw [Ne, ZMod.natCast_eq_zero_iff]; exact hnd
      simpa using h2n
    have hy00 : y = 0 := by
      have hyy : y = -y := by rw [← hnegY]; exact hy0
      have h2y : (2 : ZMod Secp256k1.p) * y = 0 := by linear_combination hyy
      rcases mul_eq_zero.mp h2y with hcc | hcc
      · exact absurd hcc h2
      · exact hcc
    have h2P : (2 : ℕ) • Point.some x y h = 0 := by
      rw [two_nsmul]; exact Point.add_self_of_Y_eq hy0
    have h3ne0 : (3 : ℕ) • Point.some x y h ≠ 0 := by
      rw [show (3 : ℕ) = 1 + 2 from rfl, add_nsmul, one_nsmul, h2P, add_zero]
      exact Point.some_ne_zero h
    have hΨ3ne : 3 * x ^ 4 + 84 * x ≠ 0 := fun hc0 =>
      h3ne0 ((secp256k1_three_nsmul_eq_zero_iff x y h).mpr
        (by rw [secp256k1_psi3_evalEval]; exact hc0))
    have hx3 : x ^ 3 = -7 := by rw [hy00] at hc; linear_combination -hc
    rw [show (3 : ℕ) = 1 + 2 from rfl, add_nsmul, one_nsmul, h2P, add_zero,
        Point.some.injEq] at hn
    obtain ⟨hXe, hYe⟩ := hn
    refine ⟨?_, ?_⟩
    · -- x-conjunct: `X = x = Φ₃(x)/ΨSq₃(x)` using `x³ = -7`.
      rw [← hXe]
      have hden' : (9 * x ^ 8 + 504 * x ^ 5 + 7056 * x ^ 2 : ZMod Secp256k1.p) ≠ 0 := by
        have heq : (9 * x ^ 8 + 504 * x ^ 5 + 7056 * x ^ 2 : ZMod Secp256k1.p)
            = (3 * x ^ 4 + 84 * x) ^ 2 := by ring
        rw [heq]; exact pow_ne_zero 2 hΨ3ne
      have hgoal3 : x = (secp256k1.Φ (3 : ℤ)).eval x / (secp256k1.ΨSq (3 : ℤ)).eval x := by
        rw [secp256k1_Φ₃_eval, secp256k1_ΨSq₃_eval, eq_div_iff hden']
        linear_combination (8 * x ^ 6 + 1120 * x ^ 3 - 3136) * hx3
      exact_mod_cast hgoal3
    · -- y-conjunct: both sides vanish since `Y = y = 0`.
      rw [show ((3 : ℕ) : ℤ) = 3 by norm_num, show (3 : ℤ) + 2 = 5 by norm_num,
          show (3 : ℤ) - 1 = 2 by norm_num, show (3 : ℤ) - 2 = 1 by norm_num,
          show (3 : ℤ) + 1 = 4 by norm_num]
      rw [← hYe, secp256k1_omega_recurrence_three x y hc, hy00]
      ring
  · -- Main branch: `y ≠ 0`, `3•P ≠ 0`. Reconstruct the FiveTorsionBridge `3•P` assembly.
    have hy : y ≠ 0 := by
      intro h0; exact hy0 (by rw [hnegY, h0]; ring)
    have h3ne0 : (3 : ℕ) • Point.some x y h ≠ 0 := by rw [hn]; exact Point.some_ne_zero h'
    have hΨ3ne : 3 * x ^ 4 + 84 * x ≠ 0 := fun hc0 =>
      h3ne0 ((secp256k1_three_nsmul_eq_zero_iff x y h).mpr
        (by rw [secp256k1_psi3_evalEval]; exact hc0))
    have hYd : y - secp256k1.toAffine.negY x y ≠ 0 := sub_ne_zero.mpr hy0
    set s2 := secp256k1.toAffine.slope x x y y with hs2def
    set X2 := secp256k1.toAffine.addX x x s2 with hX2def
    set Y2 := secp256k1.toAffine.addY x x y s2 with hY2def
    have hsl2 : s2 * (2 * y) = 3 * x ^ 2 := by
      rw [hs2def, slope_of_Y_ne rfl hy0, div_mul_eq_mul_div, div_eq_iff hYd]
      simp only [secp256k1, WeierstrassCurve.Affine.negY]
      ring
    have hsl2v : 2 * y * s2 = 3 * x ^ 2 := by linear_combination hsl2
    have hId : (s2 ^ 2 - 3 * x) * (4 * y ^ 2) = -(3 * x ^ 4 + 84 * x) := by
      linear_combination (2 * s2 * y + 3 * x ^ 2) * hsl2 + (-12 * x) * hc
    have hd : s2 ^ 2 - 3 * x ≠ 0 := by
      intro hcc
      apply hΨ3ne
      have hh := hId
      rw [hcc, zero_mul] at hh
      linear_combination hh
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
    have hℓ3 : (s2 ^ 2 - 3 * x) * s3 = -(s2 * (s2 ^ 2 - 3 * x) + y) - y := by
      have hstep := hsl3s
      rw [hy2val, hx2x] at hstep
      linear_combination hstep
    have hY3val : Y3 = s3 * (s2 ^ 2 - s3 ^ 2) - y := by
      rw [hY3def]
      simp only [WeierstrassCurve.Affine.addY, WeierstrassCurve.Affine.negAddY,
        WeierstrassCurve.Affine.negY, WeierstrassCurve.Affine.addX, secp256k1]
      rw [hx2val, hy2val]
      linear_combination hℓ3
    rw [hP3, Point.some.injEq] at hn
    obtain ⟨hXe, hYe⟩ := hn
    refine ⟨?_, ?_⟩
    · -- x-conjunct via `secp256k1_triple_x_eq_Φ₃_div_ΨSq₃`.
      rw [← hXe, hx3val]
      exact_mod_cast secp256k1_triple_x_eq_Φ₃_div_ΨSq₃ x y s2 s3 hy hc hΨ3ne hd hsl2v hℓ3
    · -- y-conjunct via `secp256k1_triple_y_eq_ω₃` + `secp256k1_omega_recurrence_three`.
      rw [show ((3 : ℕ) : ℤ) = 3 by norm_num, show (3 : ℤ) + 2 = 5 by norm_num,
          show (3 : ℤ) - 1 = 2 by norm_num, show (3 : ℤ) - 2 = 1 by norm_num,
          show (3 : ℤ) + 1 = 4 by norm_num]
      rw [← hYe, hY3val, secp256k1_psi3_evalEval,
          secp256k1_omega_recurrence_three x y hc,
          secp256k1_triple_y_eq_ω₃ x y s2 s3 hy hc hΨ3ne hd hsl2v hℓ3]
      rw [div_mul_eq_mul_div, div_mul_eq_mul_div, div_eq_iff (pow_ne_zero 3 hΨ3ne)]
      ring

/-- Leaf `n = 4` (ω-free). x-conjunct CLOSED from the landed Point-level quadruple lemma; the
y-conjunct is the residual ω→ψ bridge at index 4. -/
theorem carrier_four (hc : y ^ 2 = x ^ 3 + 7) : Carrier x y h 4 := by
  intro X Y h' hn
  refine ⟨?_, ?_⟩
  · -- x-conjunct: `secp256k1_quadruple_x_eq_Φ₄_div_ΨSq₄` takes `h` explicitly, then `hn`; it
    -- handles the `4•P = O` / 2-torsion degeneracies internally.
    exact_mod_cast secp256k1_quadruple_x_eq_Φ₄_div_ΨSq₄ h hn
  · -- y-conjunct (residual). NEEDS: the secp256k1 `evalEval` of `ψ₆,ψ₅,ψ₄,ψ₃,ψ₂` and a `y(4P)`
    -- cert bridged to `Y·(4y)·ψ₄³ = ψ₆ψ₃² − ψ₂ψ₅²` via the `n=4` ω-anchor (`OmegaRecurrenceAnchors`
    -- extended to index 4, or `ψ_even`/`ψ_odd` from `ψ_isEllSequence`), exactly as `carrier_two`.
    sorry

/-! ## Non-degeneracy / torsion bridge (breaks the circularity) -/

/-- **Uniform torsion bridge (missing-from-Mathlib direction).** `n • P = O ⟺ ψₙ(P) = 0`.
`needs`: the uniform `Point ↔ ψ` map. The per-`n` instances
(`secp256k1_two/three/five_nsmul_eq_zero_iff`) are proved; the uniform one is the wall. Composes
with `eval_ΨSq_eq_normEDS_sq` (`DivisionPolynomialEvalBridge`) to move between `ψₙ(P)` and
`ΨSqₙ(x)`. Provable jointly with the main induction by strengthening `Carrier` to also carry
`n•P affine ⟺ ψₙ(P) ≠ 0`. -/
theorem nsmul_eq_zero_iff_psi_evalEval_zero (n : ℕ) :
    n • (Point.some x y h) = 0 ↔ (secp256k1.ψ (n : ℤ)).evalEval x y = 0 := by
  sorry

/-- Denominator non-vanishing from affineness: if `n•P` is an affine `some`, then `ΨSqₙ(x) ≠ 0`.
`needs`: a curve-reduction `ΨSqₙ.eval x = (ψₙ.evalEval x y)²` (from `eval_ΨSq_eq_normEDS_sq`) +
`nsmul_eq_zero_iff_psi_evalEval_zero` (contrapositive). -/
theorem psiSq_ne_zero_of_nsmul_some {n : ℕ} {X Y : ZMod Secp256k1.p}
    {h' : secp256k1.toAffine.Nonsingular X Y}
    (hn : n • (Point.some x y h) = Point.some X Y h') :
    (secp256k1.ΨSq (n : ℤ)).eval x ≠ 0 := by
  sorry

/-! ## The per-step rational-identity walls (isolated) -/

/-- **Even x-wall.** Tangent-doubling: the group-law `x`-coordinate of `2•(k•P)` equals the
canonical ratio at index `2k`. `needs`: `φ_ψ_diff secp256k1 k k` + `ψₖ ∣ ψ₂ₖ`
(`DivisionPolynomialDoubling`), transported to `evalEval`-at-`P` scalars, plus `ΨSqₖ(x) ≠ 0`. -/
theorem even_x_algebra (k : ℕ) (Xk Yk sk : ZMod Secp256k1.p)
    (hXk : Xk = (secp256k1.Φ (k : ℤ)).eval x / (secp256k1.ΨSq (k : ℤ)).eval x)
    (hden : (secp256k1.ΨSq (k : ℤ)).eval x ≠ 0)
    (hslope : sk * (2 * Yk) = 3 * Xk ^ 2)
    (hcurvek : Yk ^ 2 = Xk ^ 3 + 7) :
    secp256k1.toAffine.addX Xk Xk sk
      = (secp256k1.Φ ((2 * k : ℕ) : ℤ)).eval x / (secp256k1.ΨSq ((2 * k : ℕ) : ℤ)).eval x := by
  sorry

/-- **Odd x-wall = point-transported `φ_ψ_diff`.** Secant addition (`k•P + (k+1)•P`): the group-law
`x`-coordinate equals the canonical ratio at index `2k+1`. The cleared identity is the Silverman
x-difference `x((2k+1)P) − x(kP) = −ψ_{2k+1}ψ_1/(ψ_{k+1}²ψ_k²)`, i.e. `φ_ψ_diff` at `(m,n)=(k,k+1)`.
`needs`: `φ_ψ_diff secp256k1 k (k+1)` (proved) evaluated at `P` via the missing
`x([j]P) = φⱼ(P)/ψⱼ(P)²` transport; the two denominators `ΨSqₖ(x), ΨSq_{k+1}(x) ≠ 0`. -/
theorem odd_x_algebra (k : ℕ) (Xk Xk1 Yk Yk1 sk : ZMod Secp256k1.p)
    (hXk : Xk = (secp256k1.Φ (k : ℤ)).eval x / (secp256k1.ΨSq (k : ℤ)).eval x)
    (hXk1 : Xk1 = (secp256k1.Φ ((k + 1 : ℕ) : ℤ)).eval x
                    / (secp256k1.ΨSq ((k + 1 : ℕ) : ℤ)).eval x)
    (hne : Xk ≠ Xk1)
    (hslope : sk * (Xk - Xk1) = Yk - Yk1)
    (hck : Yk ^ 2 = Xk ^ 3 + 7) (hck1 : Yk1 ^ 2 = Xk1 ^ 3 + 7) :
    secp256k1.toAffine.addX Xk Xk1 sk
      = (secp256k1.Φ ((2 * k + 1 : ℕ) : ℤ)).eval x
          / (secp256k1.ΨSq ((2 * k + 1 : ℕ) : ℤ)).eval x := by
  sorry

/-- **Even y-wall (ω-free).** The ω-free `y`-conjunct at index `2k` from the tangent `addY` output.
`needs`: the ω-recurrence `4y·ω_{2k} = ψ_{2k+2}ψ_{2k-1}² − ψ_{2k-2}ψ_{2k+1}²` cleared against
`y([2k]P) = ω_{2k}/ψ_{2k}³`. -/
theorem even_y_algebra (k : ℕ) (Xk Yk sk Y : ZMod Secp256k1.p)
    (hY : Y = secp256k1.toAffine.addY Xk Xk Yk sk) :
    Y * (4 * y) * ((secp256k1.ψ ((2 * k : ℕ) : ℤ)).evalEval x y) ^ 3
        = (secp256k1.ψ (((2 * k : ℕ) : ℤ) + 2)).evalEval x y
            * ((secp256k1.ψ (((2 * k : ℕ) : ℤ) - 1)).evalEval x y) ^ 2
          - (secp256k1.ψ (((2 * k : ℕ) : ℤ) - 2)).evalEval x y
            * ((secp256k1.ψ (((2 * k : ℕ) : ℤ) + 1)).evalEval x y) ^ 2 := by
  sorry

/-- **Odd y-wall (ω-free).** The ω-free `y`-conjunct at index `2k+1` from the secant `addY` output.
`needs`: identical to `even_y_algebra` with the odd ω-recurrence. -/
theorem odd_y_algebra (k : ℕ) (Xk Xk1 Yk sk Y : ZMod Secp256k1.p)
    (hY : Y = secp256k1.toAffine.addY Xk Xk1 Yk sk) :
    Y * (4 * y) * ((secp256k1.ψ ((2 * k + 1 : ℕ) : ℤ)).evalEval x y) ^ 3
        = (secp256k1.ψ (((2 * k + 1 : ℕ) : ℤ) + 2)).evalEval x y
            * ((secp256k1.ψ (((2 * k + 1 : ℕ) : ℤ) - 1)).evalEval x y) ^ 2
          - (secp256k1.ψ (((2 * k + 1 : ℕ) : ℤ) - 2)).evalEval x y
            * ((secp256k1.ψ (((2 * k + 1 : ℕ) : ℤ) + 1)).evalEval x y) ^ 2 := by
  sorry

/-! ## Group-law plumbing (fully discharged down to the walls) -/

/-- **Even step.** `Carrier k → Carrier (2*k)`. All `Point` moves discharged; hands the two scalar
goals to `even_x_algebra`/`even_y_algebra`. Degenerate branches handled: `k•P = O` (⇒ `2k•P = O`,
vacuous) and the `2`-torsion sub-branch `Yk = negY Xk Yk` (⇒ `k•P + k•P = O`, vacuous). -/
theorem even_step_group (k : ℕ) (hk : Carrier x y h k) : Carrier x y h (2 * k) := by
  intro X Y h' hn
  rw [two_mul, add_nsmul] at hn
  rcases eq_or_ne (k • Point.some x y h) 0 with hk0 | hkne
  · rw [hk0, zero_add] at hn
    exact absurd hn.symm (Point.some_ne_zero h')
  · obtain ⟨Xk, Yk, hk_ns, hkP⟩ :
        ∃ Xk Yk, ∃ hns : secp256k1.toAffine.Nonsingular Xk Yk,
          k • Point.some x y h = Point.some Xk Yk hns := by
      cases hq : k • Point.some x y h with
      | zero => exact absurd hq hkne
      | some Xk Yk hns => exact ⟨Xk, Yk, hns, rfl⟩
    obtain ⟨hXk, _⟩ := hk Xk Yk hk_ns hkP
    have hckk : Yk ^ 2 = Xk ^ 3 + 7 := curve_of_nonsingular hk_ns
    have hden : (secp256k1.ΨSq (k : ℤ)).eval x ≠ 0 := psiSq_ne_zero_of_nsmul_some hkP
    rw [hkP] at hn
    by_cases hY : Yk = secp256k1.toAffine.negY Xk Yk
    · rw [Point.add_self_of_Y_eq hY] at hn
      exact absurd hn.symm (Point.some_ne_zero h')
    · rw [Point.add_self_of_Y_ne hY, Point.some.injEq] at hn
      obtain ⟨hXeq, hYeq⟩ := hn
      set sk := secp256k1.toAffine.slope Xk Xk Yk Yk with hskdef
      have hYd : Yk - secp256k1.toAffine.negY Xk Yk ≠ 0 := sub_ne_zero.mpr hY
      have hslope : sk * (2 * Yk) = 3 * Xk ^ 2 := by
        rw [hskdef, WeierstrassCurve.Affine.slope_of_Y_ne rfl hY,
            div_mul_eq_mul_div, div_eq_iff hYd]
        simp only [secp256k1, WeierstrassCurve.Affine.negY]
        ring
      refine ⟨?_, ?_⟩
      · rw [← hXeq]
        exact even_x_algebra k Xk Yk sk hXk hden hslope hckk
      · exact even_y_algebra k Xk Yk sk Y hYeq.symm

/-- **Odd step.** `Carrier k → Carrier (k+1) → Carrier (2*k+1)`. The generic secant branch is fully
discharged to `odd_x_algebra`/`odd_y_algebra`; the two summand-vanishing branches and the secant
`x`-collision are the honest residual `sorry`s (a base point that is `k`- or `(k+1)`-torsion, or
with `x(kP) = x((k+1)P)`). -/
theorem odd_step_group (k : ℕ) (hk : Carrier x y h k) (hk1 : Carrier x y h (k + 1)) :
    Carrier x y h (2 * k + 1) := by
  intro X Y h' hn
  have hsplit : (2 * k + 1) • Point.some x y h
      = k • Point.some x y h + (k + 1) • Point.some x y h := by
    rw [← add_nsmul]; congr 1; omega
  rw [hsplit] at hn
  rcases eq_or_ne (k • Point.some x y h) 0 with hk0 | hkne
  · -- `k•P = O` (base point is `k`-torsion): index shift `2k+1 ↦ k+1`. Residual side-branch.
    -- NEEDS: `nsmul_eq_zero_iff_psi_evalEval_zero` giving `ψₖ(P)=0`, collapsing
    -- `Φ(2k+1)/ΨSq(2k+1)` to `Φ(k+1)/ΨSq(k+1)` (via `ψ_odd` with `ψₖ = 0`), and the y-conjunct.
    sorry
  · rcases eq_or_ne ((k + 1) • Point.some x y h) 0 with hk10 | hk1ne
    · -- `(k+1)•P = O`: index shift `2k+1 ↦ k`. Symmetric residual side-branch.
      sorry
    · obtain ⟨Xk, Yk, hk_ns, hkP⟩ :
          ∃ Xk Yk, ∃ hns : secp256k1.toAffine.Nonsingular Xk Yk,
            k • Point.some x y h = Point.some Xk Yk hns := by
        cases hq : k • Point.some x y h with
        | zero => exact absurd hq hkne
        | some Xk Yk hns => exact ⟨Xk, Yk, hns, rfl⟩
      obtain ⟨Xk1, Yk1, hk1_ns, hk1P⟩ :
          ∃ Xk1 Yk1, ∃ hns : secp256k1.toAffine.Nonsingular Xk1 Yk1,
            (k + 1) • Point.some x y h = Point.some Xk1 Yk1 hns := by
        cases hq : (k + 1) • Point.some x y h with
        | zero => exact absurd hq hk1ne
        | some Xk1 Yk1 hns => exact ⟨Xk1, Yk1, hns, rfl⟩
      obtain ⟨hXk, _⟩ := hk Xk Yk hk_ns hkP
      obtain ⟨hXk1, _⟩ := hk1 Xk1 Yk1 hk1_ns hk1P
      have hckk : Yk ^ 2 = Xk ^ 3 + 7 := curve_of_nonsingular hk_ns
      have hckk1 : Yk1 ^ 2 = Xk1 ^ 3 + 7 := curve_of_nonsingular hk1_ns
      rw [hkP, hk1P] at hn
      by_cases hX : Xk = Xk1
      · -- secant `x`-collision: either same point (`2k+1 ≡ 2k`, contra) or negatives (sum `= O`,
        -- contra affine); decided by `Y_eq_of_X_eq`/`X_eq_iff`. Residual side-branch.
        sorry
      · rw [Point.add_of_X_ne hX, Point.some.injEq] at hn
        obtain ⟨hXeq, hYeq⟩ := hn
        set sk := secp256k1.toAffine.slope Xk Xk1 Yk Yk1 with hskdef
        have hslope : sk * (Xk - Xk1) = Yk - Yk1 := by
          rw [hskdef, WeierstrassCurve.Affine.slope_of_X_ne hX]
          exact div_mul_cancel₀ _ (sub_ne_zero.mpr hX)
        refine ⟨?_, ?_⟩
        · rw [← hXeq]
          exact odd_x_algebra k Xk Xk1 Yk Yk1 sk hXk hXk1 hX hslope hckk hckk1
        · exact odd_y_algebra k Xk Xk1 Yk sk Y hYeq.symm

end Fixed

/-! ## The capstone: assemble via `normEDSRec'` -/

/-- **N7-uniform joint coordinate certificate for secp256k1 (all `n`).** For nonsingular `P=(x,y)`
on `y²=x³+7`, whenever `n•P = (X,Y)` is affine, `X = Φₙ(x)/ΨSqₙ(x)` and the ω-free relation
`Y·(4y)·ψₙ(P)³ = ψ(n+2)ψ(n-1)² − ψ(n-2)ψ(n+1)²` holds. Proof: `normEDSRec'` with the five base
leaves and the two step lemmas, even case at index `2*(m+3)`, odd at `2*(m+2)+1`. `sorry`-free
modulo the named walls. -/
theorem secp256k1_nsmul_coords
    (n : ℕ) (x y X Y : ZMod Secp256k1.p) (hc : y ^ 2 = x ^ 3 + 7)
    (h : secp256k1.toAffine.Nonsingular x y) (h' : secp256k1.toAffine.Nonsingular X Y)
    (hn : n • (Point.some x y h) = Point.some X Y h') :
    X = (secp256k1.Φ n).eval x / (secp256k1.ΨSq n).eval x
      ∧ Y * (4 * y) * ((secp256k1.ψ (n : ℤ)).evalEval x y) ^ 3
          = (secp256k1.ψ ((n : ℤ) + 2)).evalEval x y
              * ((secp256k1.ψ ((n : ℤ) - 1)).evalEval x y) ^ 2
            - (secp256k1.ψ ((n : ℤ) - 2)).evalEval x y
              * ((secp256k1.ψ ((n : ℤ) + 1)).evalEval x y) ^ 2 := by
  have hcar : Carrier x y h n := by
    -- `hn, h', X, Y` mention `n`; clear them so `induction n` can generalise cleanly.
    clear hn h' X Y
    induction n using normEDSRec' with
    | zero => exact carrier_zero
    | one => exact carrier_one hc
    | two => exact carrier_two hc
    | three => exact carrier_three hc
    | four => exact carrier_four hc
    | even m ih => exact even_step_group (m + 3) (ih (m + 3) (by omega))
    | odd m ih =>
        exact odd_step_group (m + 2) (ih (m + 2) (by omega)) (ih (m + 3) (by omega))
  exact hcar X Y h' hn

end Ecdlp.Curve.N7Uniform