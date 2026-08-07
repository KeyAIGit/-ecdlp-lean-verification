/-
DRAFTS-LANE MIRROR — RH multiplicity/divisor package (S1-MULTIPLICITY), M1-M17.

This file is the drafts-lane copy of the built module
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean`, implementing
`domains/riemann-hypothesis/MULTIPLICITY_CONTRACT.md` (statement surface
independently accepted 2026-08-07, RH-009). From the first `import` below
through end of file it is byte-identical to the built module; only this
leading header differs. It is NOT part of any lake target and is not itself
kernel-checked: the kernel's verdict applies to the built copy, and any
proof-only repair must be applied to both copies before a new CI run. A
statement change stops promotion and returns to contract review.

Pinned Mathlib: fabf563a7c95a166b8d7b6efca11c8b4dc9d911f (v4.31.0).
-/
import ResearchOS.AnalyticNumberTheory.RiemannHypothesis.Xi     -- riemannXi, X11 (built, merged)
import ResearchOS.AnalyticNumberTheory.RiemannHypothesis.Conj   -- the Z9 order legs (built, merged, PR #307)
import Mathlib.NumberTheory.LSeries.RiemannZeta -- riemannZeta, differentiableAt_riemannZeta (M16)
import Mathlib.Analysis.Analytic.Order          -- analyticOrderAt; :561 comp-of-deriv-ne-zero (M2)
import Mathlib.Analysis.Calculus.Deriv.Add      -- deriv_const_sub_id (:449), the -1 derivative (M2)
import Mathlib.Analysis.Meromorphic.Divisor     -- MeromorphicOn.divisor, its _apply/_nonneg lemmas
import Mathlib.Analysis.Meromorphic.NormalForm  -- meromorphicNFOn, zero_set_eq_divisor_support
import Mathlib.Analysis.Complex.CauchyIntegral  -- Complex.analyticOnNhd_univ_iff_differentiable

-- Deviation from the contract's proposed preamble (which is flagged there as
-- "name-resolution review only"): `Mathlib.NumberTheory.LSeries.RiemannZeta` is
-- listed EXPLICITLY rather than relied on transitively through
-- `Xi.lean:20` (`Mathlib.NumberTheory.LSeries.ZetaZeros`), because M4/M6/M8 and all
-- of Block E name `riemannZeta` and M16 names `differentiableAt_riemannZeta`
-- (RiemannZeta.lean:137) directly. `Mathlib.Topology.LocallyFinsupp`
-- (`apply_eq_zero_of_notMem` :197, `FunLike` :125, pointwise `LE` :401) and
-- `Mathlib.Algebra.Order.WithTop.Untop0` (`untop₀` :30) are direct `public import`s
-- of `Mathlib/Analysis/Meromorphic/Divisor.lean` (:11 and :8 respectively; the
-- block runs :8-:11). `Mathlib.Data.ENat.Basic` (`ENat.map_eq_top_iff` :526) is
-- NOT a direct import of that file; it is reached through the transitive
-- `public import` closure (verified this session: the closure of the six Mathlib
-- imports below contains `Mathlib.Data.ENat.Basic`; the exact module count is
-- not restated here, since two independent BFS runs disagreed on it). Because
-- the pin uses the Lean module system (`module` / `public import` at
-- Divisor.lean:6, :8-:11), visibility here is a closure property, not an
-- import-line property. None of the three is re-listed.
-- `Mathlib.Analysis.Calculus.InverseFunctionTheorem.Analytic` (the `CompleteSpace ℂ`
-- / `CharZero ℂ` machinery consumed inside Order.lean:561) arrives via
-- Order.lean:10 — note :10, NOT :9, which is `Mathlib.Analysis.Calculus.Deriv.Pow`
-- (contract finding A6).

open Complex
-- `open Complex` is the house convention of both built siblings (Xi.lean:27,
-- Conj.lean:44) AND is load-bearing here: every inline fallback recorded below
-- spells `Complex`-namespace lemmas unqualified (`conj_re`, `one_re`, `sub_re`,
-- `continuous_re`, `analyticOnNhd_univ_iff_differentiable`), exactly as the two
-- in-tree call sites of the last of these do. The primary spellings are
-- nevertheless fully qualified, so a lost `open` degrades to a fallback, not a
-- break.
open Filter
-- Carried from the contract preamble and from Xi.lean:27 / Conj.lean:46. Not
-- load-bearing for any primary step below (no `∀ᶠ`/`=ᶠ` goal is written here);
-- kept because `IsOpen.mem_nhds` in M16 and `analyticOrderAt`'s own
-- characterizations are stated in `Filter` terms and a fallback that has to
-- inspect them should not need a preamble edit.
open scoped Real Topology ComplexConjugate
-- Carried verbatim from the contract preamble. `Topology` supplies the `𝓝`
-- notation appearing in `DifferentiableOn.analyticAt`'s hypothesis
-- (CauchyIntegral.lean:625) used in M16; `ComplexConjugate` supplies the `conj`
-- notation in which `Complex.conj_re` (Data/Complex/Basic.lean:467) is stated;
-- `Real` is inherited house style (no `π` occurs below).

/-! ## Block A — reflection order transport for ξ (barrier exit item (a))

## M1. Function-level reflection glue `[PIN]`

Deliberately mirrors `riemannXi_comp_conj` (repo:`Conj.lean:292`) so that M3
has the same one-rewrite shape as `analyticOrderAt_riemannXi_conj`
(repo:`Conj.lean:452`). The `∘`-form is what
`analyticOrderAt_comp_of_deriv_ne_zero` (Order.lean:561) consumes. -/

theorem riemannXi_comp_one_sub :
    riemannXi ∘ (fun s : ℂ => 1 - s) = riemannXi := by
  funext s
  simpa only [Function.comp_apply] using riemannXi_one_sub s
  -- OBLIG S1M-1 (LOW): the `∘`-form must elaborate against Order.lean:561's `f ∘ g`.
  -- `Function.comp_apply` beta-reduces `(riemannXi ∘ fun s => 1 - s) s` to
  -- `riemannXi (1 - s)`, which is exactly repo:`Xi.lean:61`.
  -- Fallback (contract-recorded):
  --   funext s; show riemannXi (1 - s) = riemannXi s; exact riemannXi_one_sub s

/-! ## M2. Generic precomposition-order lemma for an affine reflection `[GEN]` `[PIN]`

HONESTY NOTE (contract §M2, reproduced): this is a CONVENIENCE WRAPPER, not a
missing-Mathlib gap. Unlike `S1C-ORD` — where `starRingEnd ℂ` is
antiholomorphic, `AnalyticAt ℂ (starRingEnd ℂ) z` is FALSE, and
repo:`Conj.lean:336/357` genuinely had to be hand-built — `fun w => c - w` is
ℂ-analytic with `deriv = -1 ≠ 0`, so the order-transport content is already at
the pin at Order.lean:561, whose own junk-value branch is discharged
internally at :566-567 via `analyticAt_comp_iff_of_deriv_ne_zero`
(InverseFunctionTheorem/Analytic.lean:40). M2's only engineering value is that
it isolates the two rewrite-fragile steps in one place. Registered as
obligation S1M-ORD at severity LOW; if it fails to elaborate, M3's independent
route (recorded at M3) does not use it and M2 is droppable.

BINDER AUDIT. Order.lean:525 constrains the composed map by
`variable {f : 𝕜 → E} {g : 𝕜 → 𝕜} {z₀ : 𝕜}`, so `g` must be `ℂ → ℂ`
(`fun w : ℂ => c - w` is) while `f` may stay `ℂ → E`. The section variables of
Analysis/Analytic/Order.lean are `{𝕜 E : Type*} [NontriviallyNormedField 𝕜]
[NormedAddCommGroup E] [NormedSpace 𝕜 E]` — re-read at the pin: there is NO
`[CompleteSpace E]`, so M2's binders below are exactly the pinned requirement.
`[CompleteSpace ℂ]` (Analysis/Complex/Basic.lean:124) and `[CharZero ℂ]`
(Data/Complex/Basic.lean:773) are instances on the BASE FIELD; nothing to
build. -/

theorem analyticOrderAt_comp_const_sub {E : Type*} [NormedAddCommGroup E]
    [NormedSpace ℂ E] (f : ℂ → E) (c z : ℂ) :
    analyticOrderAt (f ∘ (fun w : ℂ => c - w)) (c - z) = analyticOrderAt f z := by
  have hg : AnalyticAt ℂ (fun w : ℂ => c - w) (c - z) := by fun_prop
    -- OBLIG S1M-2c (LOW, contract finding A1): `fun_prop` is used rather than the
    -- term form because `analyticAt_id` is stated for `(id : E → E)` at
    -- **Linear.lean:156** (`@[fun_prop]` at :155 — NOT in Constructions.lean) and
    -- `AnalyticAt.sub` (Constructions.lean:187, `@[to_fun (attr := fun_prop)]` at
    -- :186) is a Pi-operation, so `analyticAt_const.sub analyticAt_id` matches the
    -- lambda only up to `Pi.instSub`/`id` unfolding — the same defeq risk the repo
    -- logged as OBLIG X2-a at repo:`Xi.lean:46`.
    -- Fallback 1 (in-Mathlib precedent that the term form does elaborate:
    --   Constructions.lean:857, `analyticAt_const.sub (analyticAt_const.mul analyticAt_id)`):
    --   exact analyticAt_const.sub analyticAt_id
    -- Fallback 2 (the `@[to_fun]`-generated lambda twin):
    --   exact analyticAt_const.fun_sub analyticAt_id
  have hg' : deriv (fun w : ℂ => c - w) (c - z) ≠ 0 := by
    rw [deriv_const_sub_id]                    -- Deriv/Add.lean:449 : deriv (c - ·) x = -1
    exact neg_ne_zero.mpr one_ne_zero
    -- OBLIG S1M-2b (LOW): `(fun w : ℂ => c - w)` must be the same term
    -- `deriv_const_sub_id` is stated at (`(c - ·)`, i.e. `fun x => c - x`; binder
    -- name is irrelevant). Re-read at the pin, inside `section Sub`
    -- (Deriv/Add.lean:341-476) with `{x : 𝕜}` the section variable, so `x := c - z`
    -- is inferred from the goal.
    -- Fallback 1 (preferred — the `@[simp]` twin `deriv_const_sub_id'` at
    --   Deriv/Add.lean:453, `deriv (c - ·) = fun _ => -1`, closes the whole `≠ 0`
    --   goal in one step): `simp [deriv_const_sub_id']`.
    -- Fallback 2 (`((hasDerivAt_id (c - z)).const_sub c).deriv`, via
    --   `HasDerivAt.const_sub`, Deriv/Add.lean:434,
    --   `(c : F) (hf : HasDerivAt f f' x) : HasDerivAt (fun x => c - f x) (-f') x`):
    --   this is a REPLACEMENT FOR THE `rw [deriv_const_sub_id]` STEP ONLY — it
    --   produces the equation `= -1`, so `exact neg_ne_zero.mpr one_ne_zero` must
    --   still follow. Note its lambda elaborates as `fun x => c - id x`, not the
    --   goal's `fun w : ℂ => c - w`; `rw` should still match (keyed on `deriv`,
    --   then `isDefEq` unfolds the reducible `id`), but Fallback 1 is strictly safer.
  simpa only [sub_sub_cancel] using
    analyticOrderAt_comp_of_deriv_ne_zero (f := f) hg hg'   -- Order.lean:561
  -- BETA-REDEX HAZARD, resolved (contract finding A2 — this is why the closer is
  -- `simpa only`, never `rw`). Order.lean:561 concludes
  -- `analyticOrderAt (f ∘ g) z₀ = analyticOrderAt f (g z₀)`. Instantiated here the
  -- RHS point argument is the BETA-REDEX `(fun w : ℂ => c - w) (c - z)`, NOT the
  -- syntactic term `c - (c - z)`. `rw [sub_sub_cancel]` matches syntactically and
  -- can therefore fail outright, and `rw [sub_sub_cancel] at h` on a `have`-bound
  -- instance has the identical defect. `simpa only` beta-reduces first (simp
  -- normalizes with beta/eta) and only then fires `sub_sub_cancel`
  -- (`a - (a - b) = b`, the `@[to_additive (attr := simp)]` twin of
  -- `div_div_cancel`, Algebra/Group/Basic.lean:933) — which is the whole
  -- orientation content of the reflection leg, at `c = 1` the identity
  -- `1 - (1 - z) = z`.
  -- OBLIG S1M-2a (MEDIUM), LOWCONF. Two things must go right at once: the goal head
  -- must match the literal `f ∘ g` of :561 (`f` is supplied by name to remove the
  -- higher-order choice), and the redex must reduce before `sub_sub_cancel` fires.
  -- Fallback (contract-recorded, note `simp only` and NOT `rw`):
  --   have h := analyticOrderAt_comp_of_deriv_ne_zero (f := f)
  --     (g := fun w : ℂ => c - w) (z₀ := c - z) hg hg'
  --   simp only [sub_sub_cancel] at h
  --   exact h
  -- Second fallback, if `simp only` still declines to see through the redex:
  --   have h := analyticOrderAt_comp_of_deriv_ne_zero (f := f) hg hg'
  --   beta_reduce at h
  --   rwa [sub_sub_cancel] at h
  -- Third fallback (force the redex away by ascription before rewriting):
  --   have h : analyticOrderAt (f ∘ (fun w : ℂ => c - w)) (c - z)
  --       = analyticOrderAt f (c - (c - z)) :=
  --     analyticOrderAt_comp_of_deriv_ne_zero (f := f) hg hg'
  --   rwa [sub_sub_cancel] at h

/-! ## M3. ξ reflection order transport `[PIN]` — *the reflection leg* -/

theorem analyticOrderAt_riemannXi_one_sub (s : ℂ) :
    analyticOrderAt riemannXi (1 - s) = analyticOrderAt riemannXi s := by
  simpa only [riemannXi_comp_one_sub] using
    (analyticOrderAt_comp_const_sub riemannXi 1 s)
  -- OBLIG S1M-3 (LOW): occurrence audit, mirroring repo:`Conj.lean:443-449`. M2 at
  -- `c := 1`, `z := s` gives
  --   `analyticOrderAt (riemannXi ∘ (fun w : ℂ => 1 - w)) (1 - s) = analyticOrderAt riemannXi s`.
  -- The rewrite target `riemannXi ∘ (fun w : ℂ => 1 - w)` occurs EXACTLY ONCE, in
  -- the function slot of the LHS, and ZERO times in the point argument `1 - s`
  -- (which mentions no `∘`); so M1 rewrites it to `riemannXi` and nothing else
  -- moves. M1's own binder is `fun s : ℂ => 1 - s`, alpha-equivalent to M2's
  -- `fun w : ℂ => 1 - w`, so the rewrite matches up to binder naming only.
  -- INDEPENDENT ROUTE (contract-recorded; use verbatim if M2 is dropped — it does
  -- not mention M2 at all):
  --   have hg : AnalyticAt ℂ (fun w : ℂ => 1 - w) s := by fun_prop
  --   have hg' : deriv (fun w : ℂ => 1 - w) s ≠ 0 := by
  --     rw [deriv_const_sub_id]; exact neg_ne_zero.mpr one_ne_zero
  --   have h := analyticOrderAt_comp_of_deriv_ne_zero (f := riemannXi) hg hg'
  --   rw [riemannXi_comp_one_sub] at h
  --   exact h.symm
  -- Why finding A2's beta-redex is HARMLESS on that route: there the redex sits in
  -- the point argument and is discharged by `exact`/`rwa`, which work up to defeq;
  -- no syntactic `rw` has to see through it. Only M2 needs a `sub_sub_cancel`
  -- rewrite AT the redex, which is why only M2's closer had to change.

/-! ## Block B — reflection order transport for ζ, **open strip only** (exit item (a))

## M4. ζ reflection order transport inside the open critical strip `[PIN]`

"WHERE THE Γ-FACTOR ALLOWS" — the strip hypotheses are NOT decoration. X11
(repo:`Xi.lean:248`) exists only on `0 < re s < 1` because ξ = (Γℝ-factor)·ζ·(unit)
holds with a NONVANISHING Γℝ cofactor only there (repo:`Xi.lean:239-246`, the
X11 docstring). Outside the strip the identity fails AS A STATEMENT ABOUT
ORDERS, not merely as a proof technique: `riemannZeta (-2) = 0`
(`riemannZeta_neg_two_mul_nat_add_one`, RiemannZeta.lean:171, at `n = 0`) forces
`analyticOrderAt riemannZeta (-2) ≠ 0` (`AnalyticAt.analyticOrderAt_ne_zero`,
Order.lean:137), while `riemannZeta 3 ≠ 0` (`riemannZeta_ne_zero_of_one_le_re`,
Nonvanishing.lean:410) forces `analyticOrderAt riemannZeta 3 = 0`
(`AnalyticAt.analyticOrderAt_eq_zero`, Order.lean:133). Since `1 - (-2) = 3`,
the naive global form of M4 is FALSE. Stating M4 without `h0`/`h1` is death
condition 6. Do NOT sharpen this to "the trivial zeros are simple": simplicity
is not pinned, is not needed here, and asserting it would contradict this
package's own "No simplicity" boundary (finding A7).

EXCEPTIONAL-POINT AUDIT (both sides, junk-value symmetric). Under
`0 < s.re < 1`: `s ≠ 1` and `s ≠ 0`, and `1 - s` lies in the open strip too
(`hre` below), so `1 - s ≠ 1` and `1 - s ≠ 0`. ζ is therefore analytic at BOTH
evaluation points (`differentiableAt_riemannZeta`, RiemannZeta.lean:137) and
the `analyticOrderAt` junk value `0` at non-analytic points
(`analyticOrderAt_of_not_analyticAt`, Order.lean:64) is never reached on either
side. The ζ pole at `1` and the Γℝ poles at `0, -2, -4, …` are all outside the
strip. For ξ the question does not arise: ξ is entire (repo:`Xi.lean:46`), and
`riemannXi 0 = riemannXi 1 = 1/2 ≠ 0` (repo:`Xi.lean:72,78`) forces
`analyticOrderAt riemannXi 0 = analyticOrderAt riemannXi 1 = 0` — consistent
with M3 at `s = 0`, the sharpest available self-check. -/

theorem analyticOrderAt_riemannZeta_one_sub {s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) :
    analyticOrderAt riemannZeta (1 - s) = analyticOrderAt riemannZeta s := by
  have hre : (1 - s).re = 1 - s.re := by simp [Complex.sub_re, Complex.one_re]
  have h0' : 0 < (1 - s).re := by rw [hre]; linarith
  have h1' : (1 - s).re < 1 := by rw [hre]; linarith
  calc analyticOrderAt riemannZeta (1 - s)
      = analyticOrderAt riemannXi (1 - s) :=
        (analyticOrderAt_riemannXi_eq_riemannZeta h0' h1').symm     -- X11 at 1-s
    _ = analyticOrderAt riemannXi s := analyticOrderAt_riemannXi_one_sub s   -- M3
    _ = analyticOrderAt riemannZeta s :=
        analyticOrderAt_riemannXi_eq_riemannZeta h0 h1              -- X11 at s
  -- OBLIG S1M-4 (LOW): the `re` arithmetic. `Complex.sub_re` (Data/Complex/Basic.lean:640)
  -- and `Complex.one_re` (:147) are both `@[simp]` at the pin (re-read this session),
  -- so `simp` alone would also close `hre`; they are named for auditability.
  -- Fallback if the `simp` set drifts: `have hre : (1 - s).re = 1 - s.re := by
  --   rw [Complex.sub_re, Complex.one_re]`, or drop `hre` and prove `h0'`/`h1'` by
  --   `simp only [Complex.sub_re, Complex.one_re]; linarith`.

/-! ## Block C — the composite ρ ↦ 1 − conj ρ (barrier exit item (b)) `[CONJ]`

## M5. ξ composite order transport `[CONJ]`

CONSUMES THE MERGED CONJUGATION PACKAGE: `analyticOrderAt_riemannXi_conj`
(repo:`Conj.lean:452`, PR #307, on `main`), a PACKAGE prerequisite, NOT pinned
Mathlib. It is a prerequisite that is already merged, not a blocker. -/

theorem analyticOrderAt_riemannXi_one_sub_conj (s : ℂ) :
    analyticOrderAt riemannXi (1 - (starRingEnd ℂ) s) = analyticOrderAt riemannXi s := by
  rw [analyticOrderAt_riemannXi_one_sub ((starRingEnd ℂ) s),   -- M3 at conj s
      analyticOrderAt_riemannXi_conj s]                        -- Conj.lean:452
  -- Occurrence audit: the first rewrite is supplied AT the point `conj s`, so its
  -- LHS `analyticOrderAt riemannXi (1 - conj s)` is the whole goal-LHS and matches
  -- once; the goal becomes `analyticOrderAt riemannXi (conj s) = analyticOrderAt
  -- riemannXi s`, which the second rewrite closes by `rfl`. No hypothesis is needed
  -- on either leg: M3 and Conj.lean:452 are both universally quantified in the point.

/-! ## M6. ζ composite order transport, open strip only `[CONJ]`

CONSUMES THE MERGED CONJUGATION PACKAGE: `analyticOrderAt_riemannZeta_conj`
(repo:`Conj.lean:440`, PR #307, on `main`).

COMPOSITE COMMUTATION CHECK (contract attack front 4). M5/M6 apply the
reflection leg AT `conj s` and then the conjugation leg AT `s`. Both legs are
universally quantified in their point argument, so the instantiation is
legitimate and the two rewrites commute: applying conjugation first (at
`1 - s`, via `analyticOrderAt_riemannXi_conj (1 - s)` plus
`(starRingEnd ℂ) (1 - s) = 1 - (starRingEnd ℂ) s`) reaches the same identity.
The order below is preferred only because it needs no `map_sub`/`map_one`
normalization step. The reflection map is an involution (`sub_sub_cancel`,
Algebra/Group/Basic.lean:933) and conjugation is an involution
(`Complex.conj_conj`), and they commute as maps on ℂ, so the group generated is
the Klein four-group acting on `{ρ, 1-ρ, conj ρ, 1-conj ρ}`; M7/M8 are exactly
the orbit statement. There is NO orientation subtlety:
`analyticOrderAt_comp_of_deriv_ne_zero` (Order.lean:561) is insensitive to the
SIGN of `deriv g z₀`, requiring only `≠ 0`, and `deriv (1 - ·) = -1`
(Deriv/Add.lean:449). -/

theorem analyticOrderAt_riemannZeta_one_sub_conj {s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) :
    analyticOrderAt riemannZeta (1 - (starRingEnd ℂ) s) = analyticOrderAt riemannZeta s := by
  have hc0 : 0 < ((starRingEnd ℂ) s).re := by rwa [Complex.conj_re]
  have hc1 : ((starRingEnd ℂ) s).re < 1 := by rwa [Complex.conj_re]
  rw [analyticOrderAt_riemannZeta_one_sub hc0 hc1,   -- M4 at conj s
      analyticOrderAt_riemannZeta_conj s]            -- Conj.lean:440
  -- The `hc0`/`hc1` idiom is verbatim the one already compiled at
  -- repo:`Conj.lean:310-311`; `Complex.conj_re` is Data/Complex/Basic.lean:467
  -- (`(conj z).re = z.re`, `@[simp]`, proved by `rfl`).

/-! ## M7. ξ fourfold order action `[CONJ]`

Deliberately shaped as the order-level analogue of `riemannZeta_fourfold_zero`
(repo:`Conj.lean:306`): the built conjugation package says the four points are
ZEROS TOGETHER; M7 says they are zeros OF THE SAME MULTIPLICITY. That upgrade
is the barrier's exit sentence — and it is multiplicity PRESERVATION, never a
multiplicity BOUND (no simplicity is claimed anywhere). -/

theorem analyticOrderAt_riemannXi_fourfold (s : ℂ) :
    analyticOrderAt riemannXi (1 - s) = analyticOrderAt riemannXi s ∧
    analyticOrderAt riemannXi ((starRingEnd ℂ) s) = analyticOrderAt riemannXi s ∧
    analyticOrderAt riemannXi (1 - (starRingEnd ℂ) s) = analyticOrderAt riemannXi s :=
  ⟨analyticOrderAt_riemannXi_one_sub s,
   analyticOrderAt_riemannXi_conj s,
   analyticOrderAt_riemannXi_one_sub_conj s⟩

/-! ## M8. ζ fourfold order action, open strip only `[CONJ]`

The conjugation leg needs NO strip hypothesis (repo:`Conj.lean:440` is
global); the two reflection legs do. The hypotheses are kept on the theorem
rather than weakening the middle conjunct. -/

theorem analyticOrderAt_riemannZeta_fourfold {s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) :
    analyticOrderAt riemannZeta (1 - s) = analyticOrderAt riemannZeta s ∧
    analyticOrderAt riemannZeta ((starRingEnd ℂ) s) = analyticOrderAt riemannZeta s ∧
    analyticOrderAt riemannZeta (1 - (starRingEnd ℂ) s) = analyticOrderAt riemannZeta s :=
  ⟨analyticOrderAt_riemannZeta_one_sub h0 h1,
   analyticOrderAt_riemannZeta_conj s,
   analyticOrderAt_riemannZeta_one_sub_conj h0 h1⟩

/-! ## Block D — the ξ divisor object and its symmetries (exit item (d))

## M9. ξ is analytic / meromorphic on every set `[PIN]`

Four pinned steps, no new analysis: `differentiable_riemannXi`
(repo:`Xi.lean:46`) → `Complex.analyticOnNhd_univ_iff_differentiable`
(CauchyIntegral.lean:678) → `AnalyticOnNhd.mono` (Analytic/Basic.lean:498) →
`AnalyticOnNhd.meromorphicOn` (Meromorphic/Basic.lean:475). `U` need not be
open, connected, bounded or compact: `MeromorphicOn.divisor` (Divisor.lean:39)
is TOTAL. -/

theorem analyticOnNhd_riemannXi (U : Set ℂ) : AnalyticOnNhd ℂ riemannXi U :=
  (Complex.analyticOnNhd_univ_iff_differentiable.mpr differentiable_riemannXi).mono
    (Set.subset_univ U)
  -- NAMESPACE: `analyticOnNhd_univ_iff_differentiable` is inside `namespace Complex`
  -- (CauchyIntegral.lean:173-770) — see the header's third trap. Written qualified;
  -- under the file's `open Complex` the bare name resolves too.
  -- OBLIG S1M-9 (LOW): CauchyIntegral.lean:678 is stated for `{f : ℂ → E}` with `E`
  -- the section's normed space (`[NormedAddCommGroup E] [NormedSpace ℂ E]
  -- [CompleteSpace E]`); `E := ℂ` must unify and its `CompleteSpace ℂ` instance is
  -- Analysis/Complex/Basic.lean:124. `AnalyticOnNhd.mono` is
  -- `{s t : Set E} (hf : AnalyticOnNhd 𝕜 f t) (hst : s ⊆ t)` — re-read at the pin,
  -- so the subset argument is `Set.subset_univ U : U ⊆ Set.univ`, in that direction.
  -- Fallback (contract-recorded, routes through CauchyIntegral.lean:625 instead):
  --   fun z _ => (differentiable_riemannXi.differentiableOn).analyticAt
  --     (isOpen_univ.mem_nhds (Set.mem_univ z))

theorem meromorphicOn_riemannXi (U : Set ℂ) : MeromorphicOn riemannXi U :=
  (analyticOnNhd_riemannXi U).meromorphicOn

/-! ## M10. Divisor evaluation bridge `[PIN]` — the carrier seam

This single lemma is the ONLY seam between the two carriers: it turns every
M1–M8 order identity into the corresponding M14/M15/M17 divisor identity by
`congrArg`. Note the `MeromorphicOn.` prefix (contract §1 naming trap,
re-confirmed at the pin: `namespace MeromorphicOn` spans Divisor.lean:28-468,
and :71 carries no `_root_`, unlike :83). -/

theorem riemannXi_divisor_apply {U : Set ℂ} {z : ℂ} (hz : z ∈ U) :
    MeromorphicOn.divisor riemannXi U z = ((analyticOrderAt riemannXi z).map (↑)).untop₀ :=
  MeromorphicOn.AnalyticOnNhd.divisor_apply (analyticOnNhd_riemannXi U) hz
  -- OBLIG S1M-10 (MEDIUM), LOWCONF: the `(↑)` in `.map (↑)` must elaborate as
  -- `Nat.cast : ℕ → ℤ` (so `ENat.map (↑) : ℕ∞ → WithTop ℤ`, and `.untop₀ : WithTop ℤ → ℤ`,
  -- Untop0.lean:30) IDENTICALLY on both sides of the equation and in the pinned
  -- lemma.
  -- Fallback 1 (STATEMENT-PRESERVING; route through the meromorphic `_apply`,
  --   Divisor.lean:68, exactly as Divisor.lean:71 is itself proved at the pin):
  --   by rw [MeromorphicOn.divisor_apply (meromorphicOn_riemannXi U) hz,
  --          ((analyticOnNhd_riemannXi U) z hz).meromorphicOrderAt_eq]
  --   (`AnalyticAt.meromorphicOrderAt_eq`, Meromorphic/Order.lean:279.)
  -- Fallback 2 (LAST RESORT — pinning the cast by hand in the statement's RHS,
  --   `((analyticOrderAt riemannXi z).map (Nat.cast : ℕ → ℤ)).untop₀`, CHANGES a
  --   frozen contract statement and therefore RETURNS TO CONTRACT REVIEW; it may
  --   not be applied as a CI repair.)

/-! ## M11. The ξ divisor is effective (non-negative) `[PIN]`

Semantic content: ξ has zeros and no poles — the divisor is a ZERO divisor.
The `≤` is the pointwise order instance at Topology/LocallyFinsupp.lean:401. -/

theorem riemannXi_divisor_nonneg (U : Set ℂ) :
    0 ≤ MeromorphicOn.divisor riemannXi U :=
  MeromorphicOn.AnalyticOnNhd.divisor_nonneg (analyticOnNhd_riemannXi U)
  -- Same naming trap as M10: Divisor.lean:177 is inside `namespace MeromorphicOn`
  -- and carries no `_root_`, so dot notation on the `AnalyticOnNhd` hypothesis does
  -- NOT resolve and the fully-qualified name is mandatory.

/-! ## M12. ξ has finite LOCAL ANALYTIC ORDER at every point `[PIN]` — **THE MAIN
     OBLIGATION (S1M-FIN)**

READING OF "ORDER" (fixed once, for this whole file). "Order" here always means
the LOCAL ANALYTIC ORDER AT A POINT (`analyticOrderAt`, `ℕ∞`-valued,
Analytic/Order.lean:47) or the LOCAL MEROMORPHIC ORDER AT A POINT
(`meromorphicOrderAt`, `WithTop ℤ`-valued, Meromorphic/Order.lean:47). The first
statement below says ξ's local analytic order at `z` is finite (`≠ ⊤`), i.e. ξ
does not vanish identically near `z`; the second says the same for the local
meromorphic order. NEITHER IS A STATEMENT ABOUT THE GROWTH ORDER OF AN ENTIRE
FUNCTION — that notion appears nowhere in this file, is a `S1-GLOBAL-ZEROS` /
Hadamard-side object, and is excluded by death condition 4.

WHY THIS MUST LAND BEFORE M13. `MeromorphicOn.divisor` composes
`meromorphicOrderAt` (junk `0` off meromorphy, Meromorphic/Order.lean:47) with
`WithTop.untop₀` (Untop0.lean:30, `untop₀_top = 0` at :41). So without M12
`divisor riemannXi U z = 0` conflates "z is not a zero" with "ξ vanishes
identically near z", and the M13 support statement is false-shaped. M12 is what
licenses reading the divisor as a MULTIPLICITY function at all — the
S1-MULTIPLICITY analogue of the S0-SEMANTIC totalization discharge `Xi.lean`
already performs. It needs NO zero-free region and NO growth input: the whole
content is `riemannXi 0 = 1/2 ≠ 0` (repo:`Xi.lean:72`) plus connectedness.

If S1M-FIN resists all recorded routes, death condition 5 applies: DROP M13
and reduce the divisor block to M9–M11 + M14/M15 (which need no `≠ ⊤`); do NOT
float the `≠ ⊤` hypothesis to the caller of M13 and then call the exit closed. -/

theorem analyticOrderAt_riemannXi_ne_top (z : ℂ) : analyticOrderAt riemannXi z ≠ ⊤ := by
  have hA : ∀ z₀ : ℂ, AnalyticAt ℂ riemannXi z₀ :=
    fun z₀ => analyticOnNhd_riemannXi Set.univ z₀ (Set.mem_univ z₀)
    -- `AnalyticOnNhd f s` unfolds to `∀ x, x ∈ s → AnalyticAt 𝕜 f x`
    -- (definition at Analytic/Basic.lean:117, body :118), so the two-argument
    -- application is literal, not defeq.
  intro htop
  have hzero : riemannXi = 0 :=
    (AnalyticOnNhd.analyticOrderAt_eq_top_iff_eq_zero z hA).mp htop
    -- NAMESPACE (header trap #2, also recorded in the contract): Order.lean:687 is
    -- inside `namespace AnalyticOnNhd` (:575-:700), so an unqualified spelling would
    -- not resolve. Signature re-read verbatim at the pin:
    -- `[PreconnectedSpace 𝕜] {f : 𝕜 → E} (z : 𝕜) (hf : ∀ z₀, AnalyticAt 𝕜 f z₀) :
    --  analyticOrderAt f z = ⊤ ↔ f = 0` — point EXPLICIT, analyticity hypothesis
    -- second.
  have h0 : riemannXi 0 = 0 := congrFun hzero 0
  -- The ascription needs `(0 : ℂ → ℂ) 0 ≡ (0 : ℂ)` by defeq (default transparency
  -- unfolds `Pi.instZero` — standard). Fallback if the ascription's Pi-zero defeq
  -- is refused: drop the ascription and normalize explicitly:
  --   have h0 := congrFun hzero 0
  --   rw [riemannXi_zero] at h0
  --   simp only [Pi.zero_apply] at h0
  --   norm_num at h0
  -- (`Pi.zero_apply` resolves at the pin; in-tree simp uses e.g.
  --  Probability/Moments/Basic.lean:67.)
  rw [riemannXi_zero] at h0        -- repo:`Xi.lean:72` : (1/2 : ℂ) = 0
  norm_num at h0
  -- OBLIG S1M-12a (MEDIUM), LOWCONF: `PreconnectedSpace ℂ` must resolve by INSTANCE
  -- SEARCH (`NormedSpace.instPathConnectedSpace`, Analysis/Normed/Module/Convex.lean:168,
  -- priority 100 → `ConnectedSpace` → `PreconnectedSpace`). Narrow check; do not
  -- assume — although the built conjugation sibling already forces the same instance
  -- (repo:`Conj.lean` Z3, OBLIG S1C-7) and is built and merged on `main` (PR #307),
  -- which is the strongest evidence available without a toolchain.
  -- FALLBACK ROUTE (contract-corrected under finding A3 — it needs a
  -- FINITE-LOCAL-ANALYTIC-ORDER WITNESS first (`analyticOrderAt riemannXi 0 ≠ ⊤`,
  -- never a growth order); the fifth argument of Order.lean:624 is NOT free):
  --   have hA0 : AnalyticAt ℂ riemannXi 0 := analyticOnNhd_riemannXi Set.univ 0 (Set.mem_univ 0)
  --   have hw : analyticOrderAt riemannXi 0 ≠ ⊤ := by
  --     rw [hA0.analyticOrderAt_eq_zero.mpr (by rw [riemannXi_zero]; norm_num)]
  --     simp
  --   exact AnalyticOnNhd.analyticOrderAt_ne_top_of_isPreconnected
  --     (analyticOnNhd_riemannXi Set.univ) isPreconnected_univ (Set.mem_univ 0)
  --     (Set.mem_univ z) hw
  -- (`AnalyticOnNhd.analyticOrderAt_ne_top_of_isPreconnected`, Order.lean:624, verified
  --  verbatim: `{x y : 𝕜} (hf) (hU : IsPreconnected U) (h₁x : x ∈ U) (hy : y ∈ U)
  --  (h₂x : analyticOrderAt f x ≠ ⊤)`; `AnalyticAt.analyticOrderAt_eq_zero`,
  --  Order.lean:133, is `protected` but dot notation still resolves.)
  -- SECOND FALLBACK: `AnalyticOnNhd.exists_analyticOrderAt_ne_top_iff_forall`
  -- (Order.lean:614), which needs `IsConnected U` (`isConnected_univ`) and the same
  -- witness `hw`.
  -- TWO ROUTES THAT DO NOT WORK AND MUST NOT BE RE-RECORDED (finding A3):
  --  (i) `IsOpen.forall_analyticOrderAt_eq_top_iff_eqOn_zero` (Order.lean:693) has
  --      shape `(∀ z ∈ s, analyticOrderAt f z = ⊤) ↔ EqOn f 0 s`; its forward
  --      direction consumes a UNIVERSALLY QUANTIFIED hypothesis while M12 supplies
  --      `⊤` at a SINGLE point. Not a drop-in.
  --  (ii) Order.lean:624 "with the witness point 0" is incomplete without producing
  --      `h₂x` from `riemannXi_zero` as above.
  -- OBLIG S1M-12b (LOW): the `(1/2 : ℂ) = 0` discharge. Fallbacks: `simp at h0`, or
  -- `exact absurd h0 (by norm_num)`.

theorem meromorphicOrderAt_riemannXi_ne_top (z : ℂ) : meromorphicOrderAt riemannXi z ≠ ⊤ := by
  rw [(analyticOnNhd_riemannXi Set.univ z (Set.mem_univ z)).meromorphicOrderAt_eq]
  exact fun h => analyticOrderAt_riemannXi_ne_top z (ENat.map_eq_top_iff.mp h)
  -- `AnalyticAt.meromorphicOrderAt_eq` (Meromorphic/Order.lean:279):
  -- `meromorphicOrderAt f x = (analyticOrderAt f x).map (↑)`. `ENat.map_eq_top_iff`
  -- (Data/ENat/Basic.lean:526, `namespace ENat` :53-:623) is `map f n = ⊤ ↔ n = ⊤`.
  -- PRECEDENT: Mathlib itself uses this lemma in exactly this position at
  -- Meromorphic/Order.lean:71, and `meromorphicOrderAt_eq`'s own proof uses
  -- `ENat.map_top` / `ENat.map_coe`, confirming the `.map` here is `ENat.map` and
  -- not `WithTop.map`.
  -- Fallback if `rw` inside the `≠` misfires:
  --   intro h
  --   rw [(analyticOnNhd_riemannXi Set.univ z (Set.mem_univ z)).meromorphicOrderAt_eq,
  --       ENat.map_eq_top_iff] at h
  --   exact analyticOrderAt_riemannXi_ne_top z h

/-! ## M13. Divisor support **is** the ξ zero set `[PIN]`

This is what makes "divisor" mean anything for this barrier: the capability-map
row says the zero set LOSES analytic multiplicity. M13 + M10 together say the
divisor is exactly the zero set DECORATED WITH ITS MULTIPLICITY. Without M13
the divisor is an uninterpreted `locallyFinsuppWithin` object.

NO GROWTH IS HIDDEN HERE (finding A10). The local-finiteness field
`supportLocallyFiniteWithinDomain'` of `Function.locallyFinsuppWithin`
(LocallyFinsupp.lean:48) is discharged INSIDE `MeromorphicOn.divisor` itself
(Divisor.lean:45-55, via `codiscrete_setOf_meromorphicOrderAt_eq_zero_or_top`
at :51), for EVERY `f` and EVERY `U` — verified by reading the definition body
at the pin. M9 contributes analyticity only; no Jensen inequality, no
order-one bound, nothing ζ/ξ-specific. Likewise
`MeromorphicNFOn.zero_set_eq_divisor_support` (NormalForm.lean:578) has
POINTWISE FINITE LOCAL MEROMORPHIC ORDER (`∀ u : U, meromorphicOrderAt f u ≠ ⊤`)
as its only hypothesis — never a growth order. -/

theorem riemannXi_divisor_support (U : Set ℂ) :
    Function.support (MeromorphicOn.divisor riemannXi U) = U ∩ riemannXi ⁻¹' {0} :=
  ((analyticOnNhd_riemannXi U).meromorphicNFOn.zero_set_eq_divisor_support
    (fun u => meromorphicOrderAt_riemannXi_ne_top (u : ℂ))).symm
  -- OBLIG S1M-13 (MEDIUM): two shape facts, both re-read at the pin.
  --  (a) NormalForm.lean:578's hypothesis is SUBTYPE-BOUND, `∀ u : U,
  --      meromorphicOrderAt f ↑u ≠ ⊤`, so the M12 instance needs the coercion `(u : ℂ)`.
  --  (b) Its conclusion is oriented `U ∩ f ⁻¹' {0} = Function.support (divisor f U)`,
  --      hence the trailing `.symm`.
  -- `AnalyticOnNhd.meromorphicNFOn` is NormalForm.lean:567; the file has NO
  -- `namespace` block at all (checked: only `open Topology WithTop` at :28), so both
  -- names are root names and BOTH dot notations above resolve.
  -- Fallback (contract-recorded): state M13 in the pinned orientation instead of
  -- flipping it — i.e. drop the `.symm` and swap the sides of the statement. That is
  -- a CONTRACT CHANGE and therefore returns to contract review; it is recorded here
  -- only so CI has a named exit.

/-! ## M14. Divisor reflection invariance `[PIN]`

DESIGN NOTE (DEFERRED-1). Stated POINTWISE, not as an equality of
`locallyFinsuppWithin` terms, because the pin has no pullback along a self-map:
exhaustive search of Topology/LocallyFinsupp.lean confirms the only
carrier-changing maps are `restrict` (:584), `restrictMonoidHom` (:625) and
`restrictLatticeHom` (:661) — no `comap`, no `map`, no pushforward — and there
is no `divisor_comp` in Meromorphic/Divisor.lean. Building one would be a NEW
DEFINITION carrying a nontrivial local-finiteness field obligation for a single
use (death condition 7). The `FunLike` coercion (LocallyFinsupp.lean:125) gives
exactly as much exit evidence for nothing.

OBLIG S1M-14a (LOW, informational): M14 needs NO `≠ ⊤` hypothesis. It is
`congrArg untop₀ ∘ congrArg (·.map ↑)` applied to M3, and equal orders give
equal `untop₀` regardless of finiteness. M12 is required for M13, NOT for
M14/M15 — this deliberately decouples the package's one HIGH obligation from
the exit-evidence symmetries. -/

theorem riemannXi_divisor_one_sub {U : Set ℂ}
    (hU : ∀ z : ℂ, (1 - z) ∈ U ↔ z ∈ U) (s : ℂ) :
    MeromorphicOn.divisor riemannXi U (1 - s) = MeromorphicOn.divisor riemannXi U s := by
  by_cases hs : s ∈ U
  · rw [riemannXi_divisor_apply ((hU s).mpr hs), riemannXi_divisor_apply hs,
        analyticOrderAt_riemannXi_one_sub s]                       -- M10, M10, M3
  · rw [Function.locallyFinsuppWithin.apply_eq_zero_of_notMem _ (fun h => hs ((hU s).mp h)),
        Function.locallyFinsuppWithin.apply_eq_zero_of_notMem _ hs]
  -- LocallyFinsupp.lean:197, re-read verbatim: `[Zero Y] {z : X}
  -- (D : locallyFinsuppWithin U Y) (hz : z ∉ U) : D z = 0` — `D` EXPLICIT, `z`
  -- implicit and inferred from `hz`. The `_` is the divisor; it is left to
  -- unification because the surrounding `rw` fixes it from the goal.
  -- LOWCONF: `rw` with a term whose `D` slot is still a metavariable. Fallback —
  -- supply `D` by name in both positions:
  --   have hns : (1 - s) ∉ U := fun h => hs ((hU s).mp h)
  --   rw [Function.locallyFinsuppWithin.apply_eq_zero_of_notMem
  --         (MeromorphicOn.divisor riemannXi U) hns,
  --       Function.locallyFinsuppWithin.apply_eq_zero_of_notMem
  --         (MeromorphicOn.divisor riemannXi U) hs]

theorem riemannXi_divisor_univ_one_sub (s : ℂ) :
    MeromorphicOn.divisor riemannXi Set.univ (1 - s)
      = MeromorphicOn.divisor riemannXi Set.univ s :=
  riemannXi_divisor_one_sub (fun z => by simp) s

theorem riemannXi_divisor_strip_one_sub (s : ℂ) :
    MeromorphicOn.divisor riemannXi {z : ℂ | 0 < z.re ∧ z.re < 1} (1 - s)
      = MeromorphicOn.divisor riemannXi {z : ℂ | 0 < z.re ∧ z.re < 1} s := by
  refine riemannXi_divisor_one_sub (fun z => ?_) s
  simp only [Set.mem_setOf_eq, Complex.sub_re, Complex.one_re]
  constructor <;> (rintro ⟨a, b⟩; exact ⟨by linarith, by linarith⟩)
  -- OBLIG S1M-14b (LOW): the strip-symmetry side goal
  -- `0 < 1 - z.re ∧ 1 - z.re < 1 ↔ 0 < z.re ∧ z.re < 1`. This is over `ℝ`, so
  -- `omega` is WRONG here (contract's own warning); `linarith` is the tool.
  -- Fallback (contract-recorded):
  --   constructor <;> intro h <;> exact ⟨by linarith [h.1, h.2], by linarith [h.1, h.2]⟩

/-! ## M15. Divisor conjugation and composite invariance `[CONJ]`

CONSUMES THE MERGED CONJUGATION PACKAGE (all six declarations): the
ξ-conjugation order leg is repo:`Conj.lean:452` (PR #307, on `main`) and the
composite leg is M5. Proof pattern is M14's with
`analyticOrderAt_riemannXi_conj` resp. M5 in place of M3; the obligation class
is the contract's S1M-15a / S1M-15b / S1M-15c (the M15 analogues of S1M-14a /
S1M-14b), with no package prerequisite left outstanding.

All six signatures — the two generic forms and the four `Set.univ`/open-strip
specializations — are spelled explicitly in the contract's M15 `lean` statement
block and are reproduced character-identically below. (An earlier revision of
the contract mandated the four specializations in prose only; that prose is
retired and must not be quoted as a live requirement.) They carry M14's carrier
sets (`Set.univ` and `{z : ℂ | 0 < z.re ∧ z.re < 1}`) and M14's `_univ_` /
`_strip_` naming; the strip is conj-stable because
`((starRingEnd ℂ) z).re = z.re` (`Complex.conj_re`,
Data/Complex/Basic.lean:467).

Together M14 + M15 give the ξ half of the capability-map's exit phrase
"multiplicity-preserving divisor symmetries" under `ρ ↦ 1-ρ`, `ρ ↦ conj ρ` and
`ρ ↦ 1 - conj ρ`, at the DIVISOR level rather than only at zero-membership
level. The ζ half is Block E (finding A5). -/

theorem riemannXi_divisor_conj {U : Set ℂ}
    (hU : ∀ z : ℂ, (starRingEnd ℂ) z ∈ U ↔ z ∈ U) (s : ℂ) :
    MeromorphicOn.divisor riemannXi U ((starRingEnd ℂ) s)
      = MeromorphicOn.divisor riemannXi U s := by
  by_cases hs : s ∈ U
  · rw [riemannXi_divisor_apply ((hU s).mpr hs), riemannXi_divisor_apply hs,
        analyticOrderAt_riemannXi_conj s]                          -- M10, M10, Conj.lean:452
  · rw [Function.locallyFinsuppWithin.apply_eq_zero_of_notMem _ (fun h => hs ((hU s).mp h)),
        Function.locallyFinsuppWithin.apply_eq_zero_of_notMem _ hs]
  -- Same `D`-metavariable fallback as M14.

theorem riemannXi_divisor_univ_conj (s : ℂ) :
    MeromorphicOn.divisor riemannXi Set.univ ((starRingEnd ℂ) s)
      = MeromorphicOn.divisor riemannXi Set.univ s :=
  riemannXi_divisor_conj (fun z => by simp) s

theorem riemannXi_divisor_strip_conj (s : ℂ) :
    MeromorphicOn.divisor riemannXi {z : ℂ | 0 < z.re ∧ z.re < 1} ((starRingEnd ℂ) s)
      = MeromorphicOn.divisor riemannXi {z : ℂ | 0 < z.re ∧ z.re < 1} s := by
  refine riemannXi_divisor_conj (fun z => ?_) s
  simp only [Set.mem_setOf_eq, Complex.conj_re]
  -- OBLIG S1M-15b (LOW): after `Complex.conj_re` both sides are literally
  -- `0 < z.re ∧ z.re < 1`. Pin precedent says the `simp only` WILL close the
  -- identical-sides `Iff` (`Set.inv_mem_inv`, Pointwise/Set/Basic.lean:203, closed
  -- by bare `simp only [mem_inv, inv_inv]`; likewise `left_mem_Icc`,
  -- Order/Interval/Finset/Basic.lean:129).
  -- Fallback (only if the simp only leaves the goal open — pin precedent
  -- Set.inv_mem_inv, Pointwise/Set/Basic.lean:203, says it will NOT):
  -- REPLACE the simp only line with:
  --   exact Iff.rfl
  -- (Complex.conj_re is rfl at the pin, so both memberships are defeq).
  -- Do NOT append after the simp only — that dies with "no goals" when the
  -- simp only has already closed.
  -- Robust alternative replacing the same line:
  --   constructor <;> intro h <;> simpa only [Set.mem_setOf_eq, Complex.conj_re] using h

theorem riemannXi_divisor_one_sub_conj {U : Set ℂ}
    (hU₁ : ∀ z : ℂ, (1 - z) ∈ U ↔ z ∈ U)
    (hU₂ : ∀ z : ℂ, (starRingEnd ℂ) z ∈ U ↔ z ∈ U) (s : ℂ) :
    MeromorphicOn.divisor riemannXi U (1 - (starRingEnd ℂ) s)
      = MeromorphicOn.divisor riemannXi U s := by
  by_cases hs : s ∈ U
  · have hcs : (starRingEnd ℂ) s ∈ U := (hU₂ s).mpr hs
    rw [riemannXi_divisor_apply ((hU₁ ((starRingEnd ℂ) s)).mpr hcs),
        riemannXi_divisor_apply hs,
        analyticOrderAt_riemannXi_one_sub_conj s]                  -- M10, M10, M5
  · have hns : (1 - (starRingEnd ℂ) s) ∉ U :=
      fun h => hs ((hU₂ s).mp ((hU₁ ((starRingEnd ℂ) s)).mp h))
    rw [Function.locallyFinsuppWithin.apply_eq_zero_of_notMem _ hns,
        Function.locallyFinsuppWithin.apply_eq_zero_of_notMem _ hs]
  -- Membership chain audit for `hns`: `h : (1 - conj s) ∈ U`;
  -- `hU₁ (conj s) : (1 - conj s) ∈ U ↔ conj s ∈ U` gives `conj s ∈ U`;
  -- `hU₂ s : conj s ∈ U ↔ s ∈ U` gives `s ∈ U`, contradicting `hs`. Both hypotheses
  -- are genuinely needed — neither symmetry alone stabilizes `1 - conj ·`.

theorem riemannXi_divisor_univ_one_sub_conj (s : ℂ) :
    MeromorphicOn.divisor riemannXi Set.univ (1 - (starRingEnd ℂ) s)
      = MeromorphicOn.divisor riemannXi Set.univ s :=
  riemannXi_divisor_one_sub_conj (fun z => by simp) (fun z => by simp) s

theorem riemannXi_divisor_strip_one_sub_conj (s : ℂ) :
    MeromorphicOn.divisor riemannXi {z : ℂ | 0 < z.re ∧ z.re < 1} (1 - (starRingEnd ℂ) s)
      = MeromorphicOn.divisor riemannXi {z : ℂ | 0 < z.re ∧ z.re < 1} s := by
  refine riemannXi_divisor_one_sub_conj (fun z => ?_) (fun z => ?_) s
  · simp only [Set.mem_setOf_eq, Complex.sub_re, Complex.one_re]
    constructor <;> (rintro ⟨a, b⟩; exact ⟨by linarith, by linarith⟩)
    -- OBLIG S1M-15c (LOW): this reflection side goal is S1M-14b's goal verbatim.
    -- It is over `ℝ`, so `omega` is WRONG and `linarith` is the tool. Fallback:
    --   constructor <;> intro h <;> exact ⟨by linarith [h.1, h.2], by linarith [h.1, h.2]⟩
  · simp only [Set.mem_setOf_eq, Complex.conj_re]
    -- OBLIG S1M-15b (LOW): after `Complex.conj_re` both sides are literally
    -- `0 < z.re ∧ z.re < 1`. Pin precedent says the `simp only` WILL close the
    -- identical-sides `Iff` (`Set.inv_mem_inv`, Pointwise/Set/Basic.lean:203;
    -- `left_mem_Icc`, Order/Interval/Finset/Basic.lean:129 — both closed by bare
    -- `simp only` with no `iff_self`).
    -- Fallback (only if the simp only leaves the goal open — pin precedent says
    -- it will NOT): REPLACE the simp only line with:
    --   exact Iff.rfl
    -- (Complex.conj_re is rfl at the pin, so both memberships are defeq).
    -- Do NOT append after the simp only — that dies with "no goals" when the
    -- simp only has already closed.
    -- Robust alternative replacing the same line:
    --   constructor <;> intro h <;> simpa only [Set.mem_setOf_eq, Complex.conj_re] using h
    -- Same fallback as the one recorded at `riemannXi_divisor_strip_conj` above.

/-! ## Block E — the ζ divisor on the open strip (exit item (d), ζ half)

Write `Ω := {z : ℂ | 0 < z.re ∧ z.re < 1}` — an INLINE SET-BUILDER LITERAL at
every use site below, never a `def` (the package contains zero `def`s).

WHY THIS BLOCK EXISTS (finding A5). The capability-map row
(repo:`domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md:386`) names its
remaining exit evidence as a "**zeta/xi** divisor interface and
multiplicity-preserving divisor symmetries". The original DEFERRED-3 dropped
the ζ half because "ζ has a pole at `1`, so its divisor is genuinely
meromorphic". That rationale is FALSE ON Ω: `1 ∉ Ω` because `(1 : ℂ).re = 1`
is not `< 1` (`Complex.one_re`, Data/Complex/Basic.lean:147), ζ is analytic on
Ω, and the ξ pattern transfers verbatim with no new analysis. What remains
deferred is only the ζ divisor on a set CONTAINING `1` (e.g. `Set.univ`, or the
closed strip), where `negPart ≠ 0` and `divisor_nonneg` fails — and the ζ
divisor outside the strip, where M4 is outright false.

## M16. ζ is analytic on Ω; the ζ divisor on Ω `[PIN]`

NO POLE BOOKKEEPING IS NEEDED AND NONE IS SMUGGLED IN.
`negPart (divisor riemannZeta Ω) = 0` follows from
`riemannZeta_divisor_strip_nonneg`; nothing here says anything about ζ's
divisor on a set containing `1`. -/

theorem analyticOnNhd_riemannZeta_strip :
    AnalyticOnNhd ℂ riemannZeta {z : ℂ | 0 < z.re ∧ z.re < 1} := by
  have hopen : IsOpen {z : ℂ | 0 < z.re ∧ z.re < 1} :=
    (isOpen_lt continuous_const Complex.continuous_re).and
      (isOpen_lt Complex.continuous_re continuous_const)
  intro z hz
  refine DifferentiableOn.analyticAt (fun w hw => ?_) (hopen.mem_nhds hz)
  exact (differentiableAt_riemannZeta (fun e => by simp [e] at hw)).differentiableWithinAt
  -- OBLIG S1M-16a (MEDIUM), LOWCONF: `IsOpen.and` (Topology/Basic.lean:116) is stated
  -- directly on set-builders, `IsOpen {x | p₁ x} → IsOpen {x | p₂ x} → IsOpen {x | p₁ x ∧ p₂ x}`,
  -- so its conclusion matches this goal with no `∩`-vs-`setOf` unfolding (it is
  -- *definitionally* `IsOpen.inter`, Topology/Defs/Basic.lean:96, so the swap costs
  -- nothing). This is the repo's own kernel-checked spelling at repo:`Xi.lean:308-310`
  -- (recorded there as "fix F3 (a) discharged syntactically"); do NOT "simplify" it
  -- back to `.inter`.
  -- Fallback 1 (the contract's M16 skeleton spelling; needs the `∩`-vs-set-builder defeq):
  --   have hopen : IsOpen {z : ℂ | 0 < z.re ∧ z.re < 1} :=
  --     (isOpen_lt continuous_const Complex.continuous_re).inter
  --       (isOpen_lt Complex.continuous_re continuous_const)
  -- Fallback 2 (make the `∩` syntactic first, `Set.setOf_and` = Data/Set/Basic.lean:214):
  --   have hopen : IsOpen {z : ℂ | 0 < z.re ∧ z.re < 1} := by
  --     simp only [Set.setOf_and]
  --     exact (isOpen_lt continuous_const Complex.continuous_re).inter
  --       (isOpen_lt Complex.continuous_re continuous_const)
  -- The `isOpen_lt` idiom (Topology/Order/OrderClosed.lean:556,
  -- `(hf : Continuous f) (hg : Continuous g) : IsOpen {b | f b < g b}`) is the repo's
  -- own, already compiled at repo:`Xi.lean:255` (the single-inequality
  -- `IsOpen {z : ℂ | 0 < z.re}`) and again as the two arguments of the `.and` at
  -- repo:`Xi.lean:308-310`; `Complex.continuous_re` is Analysis/Complex/Basic.lean:153.
  -- OBLIG S1M-16b (LOW): `w ≠ 1` from `hw`. `fun e => by simp [e] at hw` is the repo
  -- idiom compiled at repo:`Xi.lean:250-251` (also :214-215, :233-234, :318-319);
  -- it substitutes `w = 1`, reduces `(1 : ℂ).re` by the `@[simp]` `Complex.one_re`
  -- and closes on `1 < 1`. Fallback:
  --   fun e => by rw [e] at hw; simp only [Set.mem_setOf_eq, Complex.one_re] at hw;
  --               exact absurd hw.2 (lt_irrefl 1)
  -- `DifferentiableOn.analyticAt` is CauchyIntegral.lean:625, `protected` and
  -- explicitly `_root_`, so the bare name resolves; its `hz` argument is
  -- `s ∈ 𝓝 z`, supplied by `IsOpen.mem_nhds`.

theorem meromorphicOn_riemannZeta_strip :
    MeromorphicOn riemannZeta {z : ℂ | 0 < z.re ∧ z.re < 1} :=
  analyticOnNhd_riemannZeta_strip.meromorphicOn

theorem riemannZeta_divisor_strip_apply {z : ℂ} (hz : z ∈ {w : ℂ | 0 < w.re ∧ w.re < 1}) :
    MeromorphicOn.divisor riemannZeta {w : ℂ | 0 < w.re ∧ w.re < 1} z
      = ((analyticOrderAt riemannZeta z).map (↑)).untop₀ :=
  MeromorphicOn.AnalyticOnNhd.divisor_apply analyticOnNhd_riemannZeta_strip hz
  -- Same §1 naming trap and same S1M-10 `(↑) = Nat.cast` risk as M10; same two
  -- fallbacks, in the same order, including the contract-review gate on the
  -- cast-pinning one. Note the binder is spelled `w` here and `z` in M17 — the two
  -- set-builder literals are the same term up to bound-variable naming, so the
  -- rewrites in M17 match.

theorem riemannZeta_divisor_strip_nonneg :
    0 ≤ MeromorphicOn.divisor riemannZeta {w : ℂ | 0 < w.re ∧ w.re < 1} :=
  MeromorphicOn.AnalyticOnNhd.divisor_nonneg analyticOnNhd_riemannZeta_strip

/-! ## M16'. ζ has finite LOCAL ANALYTIC ORDER at every point of Ω `[PIN]` — free
     from X11 + M12

This costs NOTHING NEW: X11 (repo:`Xi.lean:248`) transports M12's finiteness of
the LOCAL ANALYTIC ORDER AT A POINT (first statement) and of the LOCAL
MEROMORPHIC ORDER AT A POINT (second statement) from ξ to ζ inside the strip; no
growth order of any function is involved anywhere in the transport. No
nonvanishing witness for ζ on Ω has to be produced, and in particular NO
zero-free region, NO growth bound and NO unproved analytic input enters. M12 and
M16' are the package's ONLY order-finiteness claims, and both are about the local
order at a point, never about a growth order. -/

theorem analyticOrderAt_riemannZeta_ne_top_of_mem_strip
    {z : ℂ} (h0 : 0 < z.re) (h1 : z.re < 1) : analyticOrderAt riemannZeta z ≠ ⊤ :=
  (analyticOrderAt_riemannXi_eq_riemannZeta h0 h1) ▸ analyticOrderAt_riemannXi_ne_top z
  -- OBLIG S1M-16c (LOW), LOWCONF: the `▸` direction, and the motive it computes.
  -- X11 is `analyticOrderAt riemannXi z = analyticOrderAt riemannZeta z`, and the
  -- transported term is `analyticOrderAt riemannXi z ≠ ⊤`, so `▸` must rewrite the
  -- ξ-side occurrence to the ζ side. Fallback (contract-recorded, tactic form with
  -- no motive inference):
  --   by rw [← analyticOrderAt_riemannXi_eq_riemannZeta h0 h1]
  --      exact analyticOrderAt_riemannXi_ne_top z

theorem meromorphicOrderAt_riemannZeta_ne_top_of_mem_strip
    {z : ℂ} (h0 : 0 < z.re) (h1 : z.re < 1) : meromorphicOrderAt riemannZeta z ≠ ⊤ := by
  rw [(analyticOnNhd_riemannZeta_strip z ⟨h0, h1⟩).meromorphicOrderAt_eq]
  exact fun h =>
    analyticOrderAt_riemannZeta_ne_top_of_mem_strip h0 h1 (ENat.map_eq_top_iff.mp h)
  -- Mirrors M12's second statement exactly (Meromorphic/Order.lean:279 +
  -- Data/ENat/Basic.lean:526). The `⟨h0, h1⟩` must elaborate against
  -- `z ∈ {z | 0 < z.re ∧ z.re < 1}`, which is `And` after `Set.mem_setOf_eq`
  -- (a `rfl` lemma). Fallback if the anonymous constructor is refused:
  --   have hzmem : z ∈ {w : ℂ | 0 < w.re ∧ w.re < 1} := Set.mem_setOf_eq ▸ ⟨h0, h1⟩
  --   rw [(analyticOnNhd_riemannZeta_strip z hzmem).meromorphicOrderAt_eq]

/-! ## M16''. ζ divisor support on Ω `[PIN]` -/

theorem riemannZeta_divisor_strip_support :
    Function.support (MeromorphicOn.divisor riemannZeta {z : ℂ | 0 < z.re ∧ z.re < 1})
      = {z : ℂ | 0 < z.re ∧ z.re < 1} ∩ riemannZeta ⁻¹' {0} :=
  (analyticOnNhd_riemannZeta_strip.meromorphicNFOn.zero_set_eq_divisor_support
    (fun u => meromorphicOrderAt_riemannZeta_ne_top_of_mem_strip u.2.1 u.2.2)).symm
  -- OBLIG S1M-16d (MEDIUM), LOWCONF: the subtype projections `u.2.1` / `u.2.2` must
  -- see through `u : ↥{z : ℂ | 0 < z.re ∧ z.re < 1}` — `u.2 : ↑u ∈ {z | …}`, whose
  -- whnf is the `And`. Fallback (contract-recorded):
  --   (fun u => by obtain ⟨w, hw⟩ := u
  --               exact meromorphicOrderAt_riemannZeta_ne_top_of_mem_strip hw.1 hw.2)
  -- Orientation: NormalForm.lean:578 is `U ∩ f ⁻¹' {0} = support`, hence `.symm`,
  -- exactly as in M13.

/-! ## M17. ζ divisor symmetries on Ω

OBLIG S1M-17 (LOW): the Ω-stability side goals are over `ℝ` — same class as
S1M-14b, same `linarith` discharge, and `omega` is wrong. Note that UNLIKE
M14/M15 for ξ, M17 cannot be stated for an arbitrary symmetric `U`: the ζ order
transport (M4) is itself strip-bound, so `Ω` is not a convenience choice but a
HYPOTHESIS CARRIER. Stating M17 over a general `U` would require M4 without
`h0`/`h1`, which is FALSE — death condition 6.

M17b and M17c consume the merged conjugation package
(`analyticOrderAt_riemannZeta_conj`, repo:`Conj.lean:440`, PR #307, on `main`,
plus M6). M17a consumes none of it. Neither is blocked on an unmerged PR. -/

theorem riemannZeta_divisor_strip_one_sub (s : ℂ) :
    MeromorphicOn.divisor riemannZeta {z : ℂ | 0 < z.re ∧ z.re < 1} (1 - s)
      = MeromorphicOn.divisor riemannZeta {z : ℂ | 0 < z.re ∧ z.re < 1} s := by
  have hrefl : ∀ z : ℂ, (1 - z) ∈ {w : ℂ | 0 < w.re ∧ w.re < 1}
      ↔ z ∈ {w : ℂ | 0 < w.re ∧ w.re < 1} := by
    intro z
    simp only [Set.mem_setOf_eq, Complex.sub_re, Complex.one_re]
    constructor <;> (rintro ⟨a, b⟩; exact ⟨by linarith, by linarith⟩)
  by_cases hs : s ∈ {z : ℂ | 0 < z.re ∧ z.re < 1}
  · obtain ⟨h0, h1⟩ := hs
    rw [riemannZeta_divisor_strip_apply ((hrefl s).mpr ⟨h0, h1⟩),
        riemannZeta_divisor_strip_apply ⟨h0, h1⟩,
        analyticOrderAt_riemannZeta_one_sub h0 h1]                 -- M16, M16, M4
  · rw [Function.locallyFinsuppWithin.apply_eq_zero_of_notMem _ (fun h => hs ((hrefl s).mp h)),
        Function.locallyFinsuppWithin.apply_eq_zero_of_notMem _ hs]
  -- DEVIATION from the contract's M17 proof skeleton, which wrote the negative
  -- branch as `rw [… (fun h => hs ?_), …]` with a synthetic hole INSIDE a `rw`
  -- argument and then discharged it as a following bullet. `rw` does not accept `?_`
  -- holes that create later goals (only `refine`/`exact` do), so the Ω-stability fact
  -- is hoisted into `hrefl` ABOVE the case split and reused in both branches. The
  -- mathematical content, the lemma set, and the statement are unchanged.
  -- Same `D`-metavariable fallback as M14 (supply
  -- `MeromorphicOn.divisor riemannZeta {z : ℂ | 0 < z.re ∧ z.re < 1}` by name).

theorem riemannZeta_divisor_strip_conj (s : ℂ) :
    MeromorphicOn.divisor riemannZeta {z : ℂ | 0 < z.re ∧ z.re < 1} ((starRingEnd ℂ) s)
      = MeromorphicOn.divisor riemannZeta {z : ℂ | 0 < z.re ∧ z.re < 1} s := by
  have hconj : ∀ z : ℂ, (starRingEnd ℂ) z ∈ {w : ℂ | 0 < w.re ∧ w.re < 1}
      ↔ z ∈ {w : ℂ | 0 < w.re ∧ w.re < 1} := by
    intro z
    simp only [Set.mem_setOf_eq, Complex.conj_re]
    -- After `Complex.conj_re` both sides are literally `0 < z.re ∧ z.re < 1`.
    -- Pin precedent proves `simp only` closes identical-sides residuals with no
    -- `iff_self` in the set: for `↔`, `left_mem_Icc` (Order/Interval/Finset/
    -- Basic.lean:129, `by simp only [mem_Icc, true_and, le_rfl]`); for `=`,
    -- `mul_div` (Algebra/Group/Basic.lean:335). This line WILL close the goal.
    -- Fallback (apply ONLY against an unsolved-goals failure, never speculatively;
    -- because `Complex.conj_re` is proved by `rfl` at the pin, the entire `hconj`
    -- Iff is definitional): if CI reports either an unsolved `P ↔ P` after the
    -- `simp only` OR "no goals" from an appended line, replace the two-line
    -- `hconj` tactic body wholesale with:
    --   intro z
    --   exact Iff.rfl
    -- This is correct in both failure worlds, whereas APPENDING `exact Iff.rfl`
    -- errors with "no goals" in the world where `simp only` already closed.
    -- Same fallback as the one recorded at `riemannXi_divisor_strip_conj`.
  by_cases hs : s ∈ {z : ℂ | 0 < z.re ∧ z.re < 1}
  · rw [riemannZeta_divisor_strip_apply ((hconj s).mpr hs),
        riemannZeta_divisor_strip_apply hs,
        analyticOrderAt_riemannZeta_conj s]                        -- M16, M16, Conj.lean:440
  · rw [Function.locallyFinsuppWithin.apply_eq_zero_of_notMem _ (fun h => hs ((hconj s).mp h)),
        Function.locallyFinsuppWithin.apply_eq_zero_of_notMem _ hs]
  -- The conjugation order leg needs NO strip hypothesis (Conj.lean:440 is global);
  -- the strip enters only as the divisor's carrier set, which is conj-stable by
  -- `Complex.conj_re`.

theorem riemannZeta_divisor_strip_one_sub_conj (s : ℂ) :
    MeromorphicOn.divisor riemannZeta {z : ℂ | 0 < z.re ∧ z.re < 1} (1 - (starRingEnd ℂ) s)
      = MeromorphicOn.divisor riemannZeta {z : ℂ | 0 < z.re ∧ z.re < 1} s := by
  have hrefl : ∀ z : ℂ, (1 - z) ∈ {w : ℂ | 0 < w.re ∧ w.re < 1}
      ↔ z ∈ {w : ℂ | 0 < w.re ∧ w.re < 1} := by
    intro z
    simp only [Set.mem_setOf_eq, Complex.sub_re, Complex.one_re]
    constructor <;> (rintro ⟨a, b⟩; exact ⟨by linarith, by linarith⟩)
  have hconj : ∀ z : ℂ, (starRingEnd ℂ) z ∈ {w : ℂ | 0 < w.re ∧ w.re < 1}
      ↔ z ∈ {w : ℂ | 0 < w.re ∧ w.re < 1} := by
    intro z
    simp only [Set.mem_setOf_eq, Complex.conj_re]
    -- After `Complex.conj_re` both sides are literally `0 < z.re ∧ z.re < 1`.
    -- Pin precedent proves `simp only` closes identical-sides residuals with no
    -- `iff_self` in the set: for `↔`, `left_mem_Icc` (Order/Interval/Finset/
    -- Basic.lean:129, `by simp only [mem_Icc, true_and, le_rfl]`); for `=`,
    -- `mul_div` (Algebra/Group/Basic.lean:335). This line WILL close the goal.
    -- Fallback (apply ONLY against an unsolved-goals failure, never speculatively;
    -- because `Complex.conj_re` is proved by `rfl` at the pin, the entire `hconj`
    -- Iff is definitional): if CI reports either an unsolved `P ↔ P` after the
    -- `simp only` OR "no goals" from an appended line, replace the two-line
    -- `hconj` tactic body wholesale with:
    --   intro z
    --   exact Iff.rfl
    -- This is correct in both failure worlds, whereas APPENDING `exact Iff.rfl`
    -- errors with "no goals" in the world where `simp only` already closed.
    -- Same fallback as the one recorded at `riemannZeta_divisor_strip_conj`.
  by_cases hs : s ∈ {z : ℂ | 0 < z.re ∧ z.re < 1}
  · obtain ⟨h0, h1⟩ := hs
    have hcs : (starRingEnd ℂ) s ∈ {w : ℂ | 0 < w.re ∧ w.re < 1} := (hconj s).mpr ⟨h0, h1⟩
    rw [riemannZeta_divisor_strip_apply ((hrefl ((starRingEnd ℂ) s)).mpr hcs),
        riemannZeta_divisor_strip_apply ⟨h0, h1⟩,
        analyticOrderAt_riemannZeta_one_sub_conj h0 h1]            -- M16, M16, M6
  · have hns : (1 - (starRingEnd ℂ) s) ∉ {z : ℂ | 0 < z.re ∧ z.re < 1} :=
      fun h => hs ((hconj s).mp ((hrefl ((starRingEnd ℂ) s)).mp h))
    rw [Function.locallyFinsuppWithin.apply_eq_zero_of_notMem _ hns,
        Function.locallyFinsuppWithin.apply_eq_zero_of_notMem _ hs]

/-! ## Closing boundary statement (contract §Claim boundary, restated in the file)

WHAT THIS PACKAGE SUPPLIES. The `S1-MULTIPLICITY` exit item "zeta/xi divisor
interface": M9–M13 for ξ on an arbitrary `U` (the divisor evaluates by analytic
order, is effective, has finite LOCAL ANALYTIC ORDER at every point, and its
support is exactly the ξ zero set) AND M16–M16'' for ζ on the open strip (the same four
properties, Ω-bound). The exit item "multiplicity-preserving divisor
symmetries": order level M3, repo:`Conj.lean:452`, M5 (and M7/M8); divisor
level M14, M15 (ξ, arbitrary symmetric `U`) and M17 (ζ, Ω only).

WHAT IT DOES NOT. It closes no barrier row, and no barrier row is claimed
closed here. The conjugation half of `S1-CONJ` is merged (PR #307), and
M15/M17c consume it at repo:`Conj.lean:440/452`; but the divisor-level
statements below are UNBUILT, so they retire nothing, and a merged prerequisite
is evidence about the prerequisite, never about this file.
`S1-MULTIPLICITY`'s row is scoped to THIS REPOSITORY's ζ/ξ layer: generic
pinned Mathlib machinery lowers the cost of an exit but NEVER retires a row,
and the earlier claim that the row is "stale" is retracted (finding A4, death
condition 9). An open row is not by itself authorization to work a route (death
condition 8). Authorization for this lane comes from the RH queue
`tasks/RIEMANN_HYPOTHESIS.md`, where `RH-002` is the sole ACTIVE task and no
route is selected; `repo/ECDLP_DECISION_SUBSTRATE.json` is the ECDLP lane's
substrate and is not the authority for this file. This file is an offered
statement implementation — not an active task, and not a claim that
`S1-MULTIPLICITY` is a selected target.

NO ZERO ENUMERATION (no index type, no ordering, no `ρ : ℕ → ℂ`, no `Finset` of
zeros, no `⋃`/`∑` over zeros). What this file has is exactly LOCAL FINITENESS of
the divisor's support — discharged inside `MeromorphicOn.divisor` itself
(Divisor.lean:45-55) for EVERY `f` and `U` — together with the identification of
that support with the zero set on the carrier region (M13 for ξ on `U`, M16'' for
ζ on Ω). NOTHING HERE ESTABLISHES, ASSERTS, OR IMPLIES THAT THE ξ OR ζ DIVISOR
SUPPORT IS INFINITE. Infinitude of the nontrivial zero set is not proved
anywhere in this file, is not needed by any M, and must not be written. (An
earlier revision of this paragraph claimed "on `Set.univ` and on Ω that support
is infinite and never a `Finsupp`"; that claim is WITHDRAWN as unsupported by
anything established here.) NO COUNTING (no `N(T)`, no `|ρ| ≤ T`
truncation, no zero-density, no `logCounting`;
`Function.locallyFinsuppWithin.finiteSupport` (LocallyFinsupp.lean:254) and
`divisor_ball_support_finite` (Divisor.lean:104) are compact-set statements and
are deliberately not invoked anywhere above — any such statement belongs to
`S1-GLOBAL-ZEROS`). NO SIMPLICITY (nothing here yields
`analyticOrderAt riemannXi ρ = 1` for any ρ; multiplicity-PRESERVATION is not a
multiplicity-BOUND, and this applies to the prose as well as to the
statements). NO GROWTH. NO NEW AXIOM AND NO INCOMPLETE-PROOF PLACEHOLDER
OF ANY KIND (the no-incomplete-proof CI gate scans this file; the generated
per-row axiom audit is the robust check). NO COMPILER-TRUST EXTENSIONS.
NO DEPENDENCE ON RH, GRH, Lindelöf, or any open statement —
`RiemannHypothesis` is not mentioned, and repo:`Xi.lean:208` (X10, the only
RH-mentioning prerequisite) is consumed by nothing above.

NOTHING HERE BEARS ON THE TRUTH OF THE RIEMANN HYPOTHESIS, and none of it may
be described as progress toward it. -/
