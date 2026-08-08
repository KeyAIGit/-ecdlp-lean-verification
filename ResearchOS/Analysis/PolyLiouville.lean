/-
Built polynomial-growth Liouville package: promotion of the independently
accepted L1-L5 statement surface in
`domains/riemann-hypothesis/POLY_LIOUVILLE_CONTRACT.md` (acceptance record:
`notes/reviews/POLY_LIOUVILLE_ACCEPTANCE_2026_08_07.md`; promotion record:
`notes/reviews/POLY_LIOUVILLE_PROMOTION_2026_08_08.md`).

The package proves five generic statements about entire functions of
polynomial growth. L1, the statement carrying all the analysis: if
`f : ℂ → F` is `Differentiable ℂ` into a Banach space and satisfies
`‖f z‖ ≤ C * (1 + ‖z‖) ^ n` everywhere, then `iteratedDeriv k f c = 0` for
every `k > n` and every centre `c` — the Cauchy estimate over growing radii,
killed by a polynomial-division limit. L2, the Banach-valued collapse: such
an `f` equals its degree-`n` Taylor sum at every centre, obtained by
uniqueness of `HasSum` against the pinned entire Taylor series. L3, the
packaging over `ℂ → ℂ`: such an `f` is `Polynomial.eval` of some
`p : Polynomial ℂ` with `p.natDegree ≤ n`. L4 and L5 are the degree-0 and
degree-1 corollaries (bounded ⇒ constant, linear growth ⇒ affine); L4 is a
sanity anchor, since the pinned bounded-family Liouville theorem
(`Differentiable.exists_const_forall_eq_of_bounded`, Liouville.lean:123)
proves the same thing by a different route.

State: this package is GENERIC complex analysis over pinned Mathlib, with
zero repository prerequisites -- it imports no repo module. It mentions no
zeta function, no xi, no `completedRiemannZeta₀`, no `LSeries`, no critical
strip, and no zero of anything; all five statements quantify over an
arbitrary entire `f`. It closes NO barrier row of
`domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md` and no `S1-*` item;
in particular `S1-GROWTH` ("no zeta/xi vertical or order-one growth
theorem", `MATHLIB_CAPABILITY_MAP.md:388`) remains OPEN and untouched --
polynomial growth of a generic `f` does not reach that row's order-one
exponential ζ/ξ scope. The capability-map effect is INVENTORY ONLY (contract
death condition 6, inheriting `MULTIPLICITY_CONTRACT.md` finding A4: generic
machinery lowers the cost of a future exit but never retires a row). It
proves, disproves, advances, and evidences nothing about the Riemann
Hypothesis, in either direction, and selects no route.

Module placement: `ResearchOS/Analysis/`, deliberately NOT
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/`. The surface is
domain-neutral, so filing it under the RH subtree would present generic
machinery as RH-lane content; the ledger pins `riemann-hypothesis` rows to
that subtree for exactly that reason, and these rows are `PL-*` rows of the
domain-neutral `analysis-generic` lane instead -- the same shelf, and the
same reasoning, as the `MB-*` Mellin rows.

Kernel verdict: delivered by CI on this promotion change, never by this
header. `lake build` compiles the module, the no-incomplete-proof gate scans
it, the regenerated `ResearchOS/LedgerAxiomAudit.lean` + `check_axioms.py`
enforce the per-row `standard` axiom base, and
`gen_researchos_registry.py --check` enforces inverse coverage. If any gate
is red, no row is counted.

All five public declarations are ledgered as `PL-*` rows in
`VERIFIED_RESEARCHOS.md` and audited through the generated
`ResearchOS/LedgerAxiomAudit.lean` with axiom base `standard`.

Pinned Mathlib: fabf563a7c95a166b8d7b6efca11c8b4dc9d911f (v4.31.0).
-/
import Mathlib.Analysis.Complex.Liouville        -- Cauchy estimate :44, bounded family
import Mathlib.Analysis.Complex.TaylorSeries     -- hasSum_taylorSeries_of_entire
import Mathlib.Analysis.Polynomial.Basic         -- div_tendsto_atTop_zero_of_degree_lt
import Mathlib.Algebra.Polynomial.BigOperators   -- natDegree_sum_le_of_forall_le
import Mathlib.Algebra.Polynomial.Degree.SmallDegree -- exists_eq_X_add_C_of_natDegree_le_one

open Nat Filter Metric Polynomial
open scoped Topology

-- Preamble carried verbatim from the contract (§Candidate fields, "proposed
-- module preamble"). `open Nat` mirrors TaylorSeries.lean:33 so the `i !`
-- notation in L2 resolves. `Mathlib.Algebra.Polynomial.Eval.Defs`
-- (`eval_finsetSum` :343) and `Mathlib.Topology.Algebra.InfiniteSum.Defs`
-- (collapse :295, `.unique` :326) arrive transitively;
-- `Mathlib.Algebra.Polynomial.Degree.Operations` (`eq_C_of_natDegree_le_zero`
-- :479) arrives as a `public import` of `Degree/SmallDegree.lean` (:8).
--
-- NOTE (recorded deviation, name resolution only): the contract preamble opens
-- neither `Complex` nor a `namespace Complex` block — the five declarations
-- carry the `Complex.` prefix in their names instead, exactly as the contract
-- statement blocks spell them. Consequently every `Complex`-namespace lemma and
-- every cross-reference between L1-L5 below is written FULLY QUALIFIED
-- (`Complex.norm_iteratedDeriv_le_of_forall_mem_sphere_norm_le`,
-- `Complex.hasSum_taylorSeries_of_entire`, `Complex.iteratedDeriv_eq_zero_of_norm_le_pow`,
-- …); the contract's skeletons spell these unqualified, which cannot resolve at
-- the top level. Statements are untouched by this.

/-! ## L1. Vanishing-coefficient lemma `[PIN]` — the statement that carries all
the analysis (contract §2 L1). -/

/-- If an entire function grows at most like `C * (1 + ‖z‖) ^ n`, then all its iterated
derivatives of order greater than `n` vanish, everywhere. Cauchy estimate over growing
radii. -/
theorem Complex.iteratedDeriv_eq_zero_of_norm_le_pow
    {F : Type*} [NormedAddCommGroup F] [NormedSpace ℂ F] [CompleteSpace F]
    {f : ℂ → F} {C : ℝ} {n : ℕ} (hf : Differentiable ℂ f)
    (hC : ∀ z : ℂ, ‖f z‖ ≤ C * (1 + ‖z‖) ^ n)
    {k : ℕ} (hnk : n < k) (c : ℂ) :
    iteratedDeriv k f c = 0 := by
  -- C is nonnegative, derived (contract §1 decision point 4): specialise hC at 0.
  have hC0 : 0 ≤ C := le_trans (norm_nonneg (f 0)) (by simpa using hC 0)
  -- Step 1: the radius-parametrised estimate (Liouville.lean:44, already k-indexed).
  have key : ∀ R : ℝ, 0 < R →
      ‖iteratedDeriv k f c‖ ≤ k.factorial * (C * (1 + ‖c‖ + R) ^ n) / R ^ k := by
    intro R hR
    refine Complex.norm_iteratedDeriv_le_of_forall_mem_sphere_norm_le k hR
      hf.diffContOnCl ?_                         -- DiffContOnCl.lean:42, s := ball c R
    intro z hz
    have hz' : ‖z - c‖ = R := mem_sphere_iff_norm.mp hz  -- Liouville.lean:49 precedent
    have hzb : ‖z‖ ≤ ‖c‖ + R := by
      calc ‖z‖ ≤ ‖c‖ + ‖z - c‖ := norm_le_norm_add_norm_sub' z c  -- Basic.lean:182 twin
        _ = ‖c‖ + R := by rw [hz']
    calc ‖f z‖ ≤ C * (1 + ‖z‖) ^ n := hC z
      _ ≤ C * (1 + ‖c‖ + R) ^ n :=
        mul_le_mul_of_nonneg_left (pow_le_pow_left₀ (by positivity) (by linarith) n) hC0
        -- OBLIG PL-1a (LOW), discharged by the contract's registered term-mode
        -- fallback, applied verbatim after the kernel rejected the tactic closer.
        -- The first CI round used `by gcongr <;> linarith [norm_nonneg z]` and got
        -- TWO `linarith failed` errors at this position, cases h₁ and h₂. The RHS
        -- parses as `(1 + ‖c‖) + R`, so `gcongr` had a second sum to descend into
        -- on the right against only `1 + ‖z‖` on the left; it matched positionally
        -- one level too deep and split the intended `1 + ‖z‖ ≤ (1 + ‖c‖) + R` into
        -- the pair `1 ≤ 1 + ‖c‖` (case h₁, reported with `1 + ‖c‖ < 1 ⊢ False`) and
        -- `‖z‖ ≤ R` (case h₂, reported with `R < ‖z‖ ⊢ False`). Neither was closed.
        -- h₁ was merely under-supplied — the term list carried `norm_nonneg z` but
        -- the goal needs `norm_nonneg c`. h₂ is the fatal one: `‖z‖ ≤ R` is NOT
        -- provable here, since `hzb : ‖z‖ ≤ ‖c‖ + R` puts no bound of `R` on `‖z‖`
        -- once `c` is far from the origin. So the defect was the decomposition
        -- itself, not the discharger, and no stronger tactic and no longer term
        -- list would have been a legitimate repair.
        -- The term route names both steps and never exposes that split:
        -- mul_le_mul_of_nonneg_left (Order/GroupWithZero/Defs.lean:226, shape
        -- b ≤ c → 0 ≤ a → a * b ≤ a * c) over pow_le_pow_left₀
        -- (Order/GroupWithZero/Basic.lean:470, shape 0 ≤ a → a ≤ b → ∀ n, aⁿ ≤ bⁿ),
        -- with `positivity` closing `0 ≤ 1 + ‖z‖` and `linarith` closing
        -- `1 + ‖z‖ ≤ 1 + ‖c‖ + R` from hzb in one step. Statement unchanged.
  -- Step 2: the R → ∞ kill via the pinned polynomial-division limit
  -- (Polynomial.div_tendsto_atTop_zero_of_degree_lt, Analysis/Polynomial/Basic.lean:161).
  have hlim : Filter.Tendsto
      (fun R : ℝ => k.factorial * (C * (1 + ‖c‖ + R) ^ n) / R ^ k)
      Filter.atTop (nhds 0) := by
    -- OBLIG PL-1b, first half: degree P ≤ n < k = degree Q. Assembled as a chain
    -- of NAMED intermediate facts rather than one nested term (Annex A finding A1:
    -- the degree_*_le family carries no @[gcongr] at the pin, so this must be an
    -- explicit chain either way).
    --
    -- Repair note, first CI round: the same chain was written as
    -- `refine lt_of_le_of_lt ?_ ?_` followed by two focus bullets, and the whole
    -- `by` block came back as a bare `unsolved goals` with the original goal and
    -- no error inside it. `lt_of_le_of_lt`'s middle term `b` occurs in neither
    -- hypothesis position that `?_` fixes nor in the conclusion, so `refine` was
    -- left holding an undetermined natural metavariable of type `WithBot ℕ` — it
    -- aborts on that before the bullets ever run, which is exactly the silent
    -- shape observed. Every step below instead has its type written out, so no
    -- metavariable is ever floating; the statement is untouched.
    have hbase : (Polynomial.C (1 + ‖c‖) + (Polynomial.X : Polynomial ℝ)).degree ≤ 1 :=
      (Polynomial.degree_add_le _ _).trans
        (max_le (Polynomial.degree_C_le.trans zero_le_one) Polynomial.degree_X_le)
      -- degree_add_le Degree/Defs.lean:326; degree_C_le :153; degree_X_le :240.
      -- `zero_le_one : (0 : WithBot ℕ) ≤ 1` fires through `WithBot.zeroLEOneClass`
      -- (Algebra/Order/Monoid/Unbundled/WithTop.lean:451, re-read at the pin).
    have hpow : ((Polynomial.C (1 + ‖c‖) + (Polynomial.X : Polynomial ℝ)) ^ n).degree
        ≤ (n : WithBot ℕ) := by
      have hp := Polynomial.degree_pow_le_of_le (a := (1 : WithBot ℕ)) n hbase
      rwa [mul_one] at hp
      -- degree_pow_le_of_le :406 has conclusion `degree (p ^ b) ≤ ↑b * a`, a
      -- multiplication in WithBot ℕ — NOT the `n • degree p` smul shape of
      -- degree_pow_le at :402; the two must not be mixed.
    have hPle : (Polynomial.C ((k.factorial : ℝ) * C) *
        (Polynomial.C (1 + ‖c‖) + (Polynomial.X : Polynomial ℝ)) ^ n).degree
        ≤ (n : WithBot ℕ) := by
      have hmul := (Polynomial.degree_mul_le
        (Polynomial.C ((k.factorial : ℝ) * C))
        ((Polynomial.C (1 + ‖c‖) + (Polynomial.X : Polynomial ℝ)) ^ n)).trans
          (add_le_add Polynomial.degree_C_le hpow)
      rwa [zero_add] at hmul
      -- degree_mul_le Degree/Defs.lean:396, giving `≤ 0 + ↑n` before zero_add.
    have hdeg : (Polynomial.C ((k.factorial : ℝ) * C) *
        (Polynomial.C (1 + ‖c‖) + (Polynomial.X : Polynomial ℝ)) ^ n).degree
        < ((Polynomial.X : Polynomial ℝ) ^ k).degree := by
      rw [Polynomial.degree_X_pow]                -- Degree/Defs.lean:514
      exact lt_of_le_of_lt hPle (by exact_mod_cast hnk)
      -- here `lt_of_le_of_lt`'s middle term is pinned by hPle, so the metavariable
      -- that sank the first round cannot arise. Fallback — exact alternative text
      -- if the ℕ → WithBot ℕ cast is not found by exact_mod_cast (the in-tree
      -- precedent for `Nat.cast_lt` at this type is Degree/Lemmas.lean:79):
      --   exact lt_of_le_of_lt hPle (Nat.cast_lt.mpr hnk)
    have h := Polynomial.div_tendsto_atTop_zero_of_degree_lt
      (P := Polynomial.C ((k.factorial : ℝ) * C) * (Polynomial.C (1 + ‖c‖) + Polynomial.X) ^ n)
      (Q := Polynomial.X ^ k) hdeg
    refine h.congr' ?_                            -- Tendsto.congr', Order/Filter/Tendsto.lean:105
    filter_upwards [Filter.eventually_gt_atTop (0 : ℝ)] with R hR
    simp only [Polynomial.eval_mul, Polynomial.eval_pow, Polynomial.eval_add,
      Polynomial.eval_C, Polynomial.eval_X]
    ring
    -- OBLIG PL-1b (MEDIUM), the eval reconciliation: the polynomial-route limit
    -- concludes about `fun R => eval R P / eval R Q`; after `simp only` with the
    -- eval lemmas the goal is
    --   ↑k.factorial * C * (1 + ‖c‖ + R) ^ n / R ^ k
    --     = ↑k.factorial * (C * (1 + ‖c‖ + R) ^ n) / R ^ k
    -- — `(1 + ‖c‖) + R` (polynomial shape) and `1 + ‖c‖ + R` (goal shape) are
    -- already the same term by left-associated parsing, so only the mul
    -- re-association remains and `ring` closes it. (Recorded deviation from the
    -- skeleton's `simp [...(incl. mul_assoc)]` + `ring_nf` closer: a `simp` that
    -- already closes the goal would make a following `ring_nf` fail with "no
    -- goals"; `simp only` + `ring` is deterministic and performs the same
    -- add_assoc/mul_assoc normalisation the contract's PL-1b note asks for.)
    -- Contract-recorded FALLBACK ROUTE for the whole of Step 2 (elementary, no
    -- Polynomial — use if the eval reconciliation resists): for
    -- R ≥ max 1 (1 + ‖c‖) bound `(1 + ‖c‖ + R) ^ n ≤ (2 * R) ^ n`, so the whole
    -- expression is `≤ (k.factorial * C * 2 ^ n) * (R ^ k)⁻¹ * R ^ n`, and
    -- squeeze with `tendsto_pow_atTop` (Order/Filter/AtTopBot/Ring.lean:36) +
    -- `Tendsto.inv_tendsto_atTop` on `R ^ (k - n)`; this trades the eval
    -- reconciliation for Nat-subtraction bookkeeping (`pow_sub₀`-style, needing
    -- `R ≠ 0` and `n ≤ k`). Either route is contract-acceptable.
  -- Step 3: squeeze.
  rw [← norm_le_zero_iff]                         -- Basic.lean:990-991 additive twin
  exact ge_of_tendsto hlim
    ((Filter.eventually_gt_atTop (0 : ℝ)).mono fun R hR => key R hR)
  -- OBLIG PL-1c (LOW): direction check — `ge_of_tendsto (lim) (h : ∀ᶠ R, b ≤ g R)
  -- : b ≤ a` with b := ‖iteratedDeriv k f c‖, a := 0 (OrderClosed.lean:130-131,
  -- @[to_dual] of le_of_tendsto). Fallback — exact alternative text if the
  -- to_dual-generated orientation differs at elaboration (OrderClosed.lean:469):
  --   exact le_of_tendsto_of_tendsto tendsto_const_nhds hlim
  --     ((Filter.eventually_gt_atTop (0 : ℝ)).mono fun R hR => key R hR)

/-! ## L2. Banach-valued finite Taylor form `[PIN]` — the collapse seam
(contract §2 L2). The summand is written in the exact smul-shape and factor
order of `hasSum_taylorSeries_of_entire` (TaylorSeries.lean:129-130), so the two
`HasSum` witnesses are about the syntactically identical function and
`HasSum.unique` applies with no congruence step. -/

/-- An entire function of polynomial growth of degree at most `n` equals its Taylor
polynomial of degree `n` at every centre. Banach-valued. -/
theorem Complex.taylorSum_eq_of_norm_le_pow
    {F : Type*} [NormedAddCommGroup F] [NormedSpace ℂ F] [CompleteSpace F]
    {f : ℂ → F} {C : ℝ} {n : ℕ} (hf : Differentiable ℂ f)
    (hC : ∀ z : ℂ, ‖f z‖ ≤ C * (1 + ‖z‖) ^ n) (c z : ℂ) :
    f z = ∑ i ∈ Finset.range (n + 1), (i ! : ℂ)⁻¹ • (z - c) ^ i • iteratedDeriv i f c := by
  have h1 : HasSum (fun i : ℕ ↦ (i ! : ℂ)⁻¹ • (z - c) ^ i • iteratedDeriv i f c) (f z) :=
    Complex.hasSum_taylorSeries_of_entire hf c z   -- TaylorSeries.lean:129
  have h2 : HasSum (fun i : ℕ ↦ (i ! : ℂ)⁻¹ • (z - c) ^ i • iteratedDeriv i f c)
      (∑ i ∈ Finset.range (n + 1), (i ! : ℂ)⁻¹ • (z - c) ^ i • iteratedDeriv i f c) :=
    hasSum_sum_of_ne_finset_zero fun i hi ↦ by    -- InfiniteSum/Defs.lean:295
      have hni : n < i := by
        simpa [Finset.mem_range, Nat.lt_succ_iff, not_le] using hi
        -- OBLIG PL-2b (LOW) fallback — exact alternative text:
        --   have h' : ¬ i < n + 1 := fun h => hi (Finset.mem_range.mpr h)
        --   omega
      rw [Complex.iteratedDeriv_eq_zero_of_norm_le_pow hf hC hni c]   -- L1
      simp                                        -- smul_zero twice
      -- OBLIG PL-2c (LOW) fallback — exact alternative text, replacing the
      -- `rw`+`simp` pair, if `rw` stumbles on the binder-free occurrence:
      --   simp [Complex.iteratedDeriv_eq_zero_of_norm_le_pow hf hC hni c]
  exact h1.unique h2                              -- InfiniteSum/Defs.lean:326
  -- OBLIG PL-2a (MEDIUM — the riskiest obligation of the package): the
  -- three-lemma HasSum seam under the SummationFilter API (contract §1 API-shape
  -- trap). At this pin `HasSum f a` elaborates as `HasSum f a (unconditional ℕ)`
  -- (defaulted third argument, InfiniteSum/Defs.lean:106); h1
  -- (hasSum_taylorSeries_of_entire, default filter), h2
  -- (hasSum_sum_of_ne_finset_zero, hypothesis [L.LeAtTop]) and `.unique`
  -- ([T2Space α] [L.NeBot], variables :323) must all be instantiated at the SAME
  -- defaulted `unconditional ℕ`, with instance resolution — not unification —
  -- supplying LeAtTop and NeBot (both instances at SummationFilter.lean:171/:173;
  -- T2Space F holds for every normed group). No explicit `L` is written anywhere
  -- above, deliberately.
  -- Fallback 1 — exact alternative text if default arguments leave a filter
  -- metavariable (pin the filter ON THE COLLAPSE CALL ONLY, h2's proof term):
  --   hasSum_sum_of_ne_finset_zero (L := unconditional ℕ) fun i hi ↦ by
  -- Fallback 2 — exact alternative text if `.unique` dot-notation fails to
  -- resolve on the additive side (replaces the final line):
  --   exact HasSum.unique h1 h2
  -- If BOTH the primary seam and these fallbacks fail to elaborate, contract
  -- death condition 5 applies: stop and re-plan via the tsum route
  -- (Complex.taylorSeries_eq_of_entire, TaylorSeries.lean:137, plus tsum_eq_sum,
  -- InfiniteSum/Basic.lean:457 — itself [L.LeAtTop]-hypothesised, so the same
  -- seam) — and if that also fails, `UPSTREAM_POOL.md` §4.3's difficulty
  -- assessment must be corrected before any further attempt. Do not patch around.

/-! ## L3. Main statement: polynomial packaging `[PIN]` (contract §2 L3). -/

/-- **Liouville, polynomial-growth form**: an entire function bounded by
`C * (1 + ‖z‖) ^ n` is a polynomial of degree at most `n`. -/
theorem Complex.exists_polynomial_of_norm_le_pow
    {f : ℂ → ℂ} {C : ℝ} {n : ℕ} (hf : Differentiable ℂ f)
    (hC : ∀ z : ℂ, ‖f z‖ ≤ C * (1 + ‖z‖) ^ n) :
    ∃ p : Polynomial ℂ, p.natDegree ≤ n ∧ ∀ z : ℂ, f z = p.eval z := by
  refine ⟨∑ i ∈ Finset.range (n + 1),
      Polynomial.C ((i ! : ℂ)⁻¹ * iteratedDeriv i f 0) * Polynomial.X ^ i, ?_, ?_⟩
  · -- degree bound: pure bookkeeping
    refine Polynomial.natDegree_sum_le_of_forall_le _ _ fun i hi ↦ ?_  -- BigOperators.lean:65
    exact (Polynomial.natDegree_C_mul_X_pow_le _ i).trans              -- Degree/Defs.lean:365
      (Nat.lt_succ_iff.mp (Finset.mem_range.mp hi))
    -- OBLIG PL-3b (LOW) fallback — exact alternative text if the underscore
    -- application misfires (BigOperators.lean:45 has `(s : Finset ι)` explicit):
    --   refine Polynomial.natDegree_sum_le_of_forall_le (s := Finset.range (n + 1))
    --     _ fun i hi ↦ ?_
  · -- evaluation: L2 at c = 0, then push eval through the finite sum
    intro z
    rw [Complex.taylorSum_eq_of_norm_le_pow hf hC 0 z]                 -- L2
    rw [Polynomial.eval_finsetSum]                                     -- Eval/Defs.lean:343
    -- (NOT the deprecated `eval_finset_sum` alias at :347.)
    refine Finset.sum_congr rfl fun i _ ↦ ?_
    -- LHS summand: (i !)⁻¹ • (z - 0) ^ i • iteratedDeriv i f 0   (ℂ-smul on ℂ)
    -- RHS summand: eval z (C ((i !)⁻¹ * iteratedDeriv i f 0) * X ^ i)
    simp only [Polynomial.eval_mul, Polynomial.eval_C, Polynomial.eval_pow,
      Polynomial.eval_X, smul_eq_mul, sub_zero]
    ring
    -- OBLIG PL-3a (MEDIUM): the per-summand reconciliation — two nested smuls,
    -- power of `z - 0`, factor order coefficient·power·derivative on the left
    -- versus `((i !)⁻¹ * D) * z ^ i` on the right. `smul_eq_mul` firing on the
    -- ℂ-over-ℂ smul has the pin's own precedent at TaylorSeries.lean:146
    -- (`rw [mul_right_comm, smul_eq_mul, smul_eq_mul, mul_assoc]`, the proof of
    -- taylorSeries_eq_of_entire'). Fallback — exact alternative text (insert
    -- BEFORE the `rw [Polynomial.eval_finsetSum]` line, then rewrite with it):
    --   have hsummand : ∀ (a b w : ℂ) (i : ℕ), a • (w - 0) ^ i • b = a * b * w ^ i := by
    --     intros; simp [smul_eq_mul, sub_zero]; ring
    -- and close the per-summand goal with
    --   simp only [Polynomial.eval_mul, Polynomial.eval_C, Polynomial.eval_pow,
    --     Polynomial.eval_X, hsummand]

/-! ## L4. Degree-0 corollary `[PIN]` — the sanity anchor (contract §2 L4): the
same statement already follows from the pinned bounded family
(`Differentiable.exists_const_forall_eq_of_bounded`, Liouville.lean:123, via
`isBounded_iff_forall_norm_le`, Normed/Group/Bounded.lean:71-72); L4 being
derivable both ways is the package's self-check. -/

/-- Degree-0 case: recovers Liouville's theorem. Sanity anchor against
`Differentiable.exists_const_forall_eq_of_bounded` (Liouville.lean:123). -/
theorem Complex.exists_const_forall_eq_of_norm_le
    {f : ℂ → ℂ} {C : ℝ} (hf : Differentiable ℂ f) (hC : ∀ z : ℂ, ‖f z‖ ≤ C) :
    ∃ c : ℂ, ∀ z : ℂ, f z = c := by
  obtain ⟨p, hdeg, hev⟩ := Complex.exists_polynomial_of_norm_le_pow (n := 0) hf
    (fun z ↦ by simpa using hC z)                 -- (1 + ‖z‖) ^ 0 = 1, pow_zero + mul_one
    -- OBLIG PL-4a (LOW) fallback — exact alternative text for the massage:
    --   (fun z ↦ by rw [pow_zero, mul_one]; exact hC z)
  refine ⟨p.coeff 0, fun z ↦ ?_⟩
  rw [hev z, Polynomial.eq_C_of_natDegree_le_zero hdeg]  -- Degree/Operations.lean:479
  simp                                             -- eval_C, coeff_C_zero

/-! ## L5. Degree-1 corollary `[PIN]` (contract §2 L5). -/

/-- Degree-1 case: an entire function of at most linear growth is affine. -/
theorem Complex.exists_affine_of_norm_le_pow_one
    {f : ℂ → ℂ} {C : ℝ} (hf : Differentiable ℂ f)
    (hC : ∀ z : ℂ, ‖f z‖ ≤ C * (1 + ‖z‖)) :
    ∃ a b : ℂ, ∀ z : ℂ, f z = a * z + b := by
  obtain ⟨p, hdeg, hev⟩ := Complex.exists_polynomial_of_norm_le_pow (n := 1) hf
    (fun z ↦ by simpa using hC z)                 -- (1 + ‖z‖) ^ 1 = 1 + ‖z‖, pow_one
    -- OBLIG PL-5a (LOW) fallback — exact alternative text (dual of PL-4a):
    --   (fun z ↦ by rw [pow_one]; exact hC z)
  obtain ⟨a, b, hp⟩ := Polynomial.exists_eq_X_add_C_of_natDegree_le_one hdeg
                                                   -- Degree/SmallDegree.lean:50
  refine ⟨a, b, fun z ↦ ?_⟩
  rw [hev z, hp]
  simp                                             -- eval_add, eval_mul, eval_C, eval_X
  -- OBLIG PL-5b (LOW): the eval simp set must produce `a * z + b` in that literal
  -- operand order from `eval z (C a * X + C b)`. Fallback — exact alternative
  -- text REPLACING the `simp` line (do not append after it — that dies with
  -- "no goals" when the simp has already closed):
  --   simp only [Polynomial.eval_add, Polynomial.eval_mul, Polynomial.eval_C,
  --     Polynomial.eval_X]
  --   ring
  -- If the existential's witness order fights the goal, the coefficient-explicit
  -- `Polynomial.eq_X_add_C_of_natDegree_le_one` (Degree/SmallDegree.lean:43) is
  -- the contract-recorded fallback source for `hp`:
  --   refine ⟨p.coeff 1, p.coeff 0, fun z ↦ ?_⟩
  --   rw [hev z, Polynomial.eq_X_add_C_of_natDegree_le_one hdeg]
  --   simp
