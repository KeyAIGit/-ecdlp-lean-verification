# Polynomial-growth Liouville contract (UPSTREAM-POOL item 4): draft v1

Status: **DRAFT v1 (2026-08-07) — non-built review artifact, offered for STAGE ONE
(INDEPENDENT CONTRACT ACCEPTANCE) ONLY. NOT Lean-checked.** No declaration below
has been elaborated; no `lake build` has been run against any of it. Under the one
invariant, the Lean kernel via CI is the sole judge of every statement in this
contract, and this document carries no kernel verdict of any kind.

**Two-stage gate (same constraint as `MULTIPLICITY_CONTRACT.md`).** Stage one is
*independent contract acceptance*: a review of the statement surface L1–L5 only.
It produces **no built module, no ledger row, no registry or axiom-audit entry,
and no kernel verdict**. Stage two — if this pool item is ever worked at all —
is a separate built change whose verdict is delivered by CI (or, for the
intended upstream destination, by Mathlib CI). Current repository CI does not
elaborate anything in the drafts lane: `lakefile.toml:2` declares
`defaultTargets = ["Ecdlp", "ResearchOS"]`, the build step at
`.github/workflows/ci.yml:420` runs `lake build` over those targets, and the
no-incomplete-proof scan at `:359` covers only `Ecdlp.lean Ecdlp/ ResearchOS/
ResearchOS.lean`. **No green CI run on an acceptance PR is evidence of anything
about this draft.**

**Ordering and authority.** This contract designs statements for
`UPSTREAM_POOL.md` §4 ("Polynomial-growth Liouville"), a **generic complex
analysis** item whose natural home is upstream Mathlib. The RH queue
(`tasks/RIEMANN_HYPOTHESIS.md`) is the authority for the RH lane; its current
dated decision has `RH-002` as the sole ACTIVE task and authorizes no route
execution. `repo/ECDLP_DECISION_SUBSTRATE.json` governs the ECDLP lane, selects
no route, and is not the authority here. This document is an offered artifact,
not an active task, and not authorization to work a route or a barrier.

Working name (if ever drafted in-repo): `drafts/PolyLiouville.lean` — the drafts
lane, outside every lake target. Intended eventual upstream home: an addition to
`Mathlib/Analysis/Complex/Liouville.lean`, or a new
`Mathlib/Analysis/Complex/PolynomialLiouville.lean` if the import growth
(TaylorSeries + Polynomial) into `Liouville.lean` is unwelcome — a Mathlib
reviewer's call, recorded as friction, not decided here.

Statement surface: **L1 – L5**, comprising **exactly 5 public signatures**,
every one spelled explicitly in a `lean` statement block in §2. No signature of
this package is mandated in prose only.

Scope: the missing statement family identified by `UPSTREAM_POOL.md` §0 row 5
(re-verified this session: every statement in the pinned `Liouville.lean`
hypothesises `IsBounded (range f)`; no degree conclusion exists anywhere in the
file): *an entire function bounded by `C * (1 + ‖z‖) ^ n` is a polynomial of
degree at most `n`*, factored through the vanishing-coefficient lemma that
carries all the analysis, plus the degree-0 corollary (which must recover
pinned Liouville — the sanity anchor) and the degree-1 corollary. It contains
**no** growth-order definition, **no** Hadamard product, **no** zero counting,
**no** statement about `riemannZeta` or any specific function, and **no** claim
of progress on the Riemann Hypothesis or on any barrier row.

Pinned Mathlib: `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0),
toolchain `leanprover/lean4:v4.31.0`, re-verified this session via
`git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD`; repo agreement
re-verified at `lake-manifest.json:8` (`"rev": "fabf563a…"`). Every `file:line`
locator below is from that exact tree (paths relative to the `Mathlib/` root of
the pin) unless prefixed `repo:`. Every ingredient inherited from
`UPSTREAM_POOL.md` §4.2 was **re-verified rather than trusted** this session;
the re-verification corrected three of its citations (§Locator corrections).

## Locator corrections against `UPSTREAM_POOL.md` §4.2 (all re-derived)

| Pool citation | Status at the pin | Correction |
|---|---|---|
| `Complex.taylorSeries_eq_of_entire'` "TaylorSeries.lean:139" | line 139 is the *body* of `taylorSeries_eq_of_entire` | `taylorSeries_eq_of_entire` is at **:137**, the primed `ℂ→ℂ` form at **:143** |
| `Polynomial.eval_finset_sum` | **deprecated at the pin** (`Eval/Defs.lean:347`, `@[deprecated (since := "2026-04-08")]`) | current name **`Polynomial.eval_finsetSum`**, `Eval/Defs.lean:343`. The deprecated alias still elaborates but will trip the deprecation linter upstream; do not write it |
| `hasSum_sum_of_ne_finset_zero` "used in-tree at CPolynomialDef.lean:72,215" | true, but the declaration site matters | it is the `@[to_additive]` twin of `hasProd_prod_of_ne_finset_one`, **`Topology/Algebra/InfiniteSum/Defs.lean:295`**, and at this pin it carries the new **`SummationFilter`** shape: hypothesis `[L.LeAtTop]` on the summation filter (§0, §PL-2a) |

The remaining §4.2 rows check out verbatim: the Cauchy estimate at
`Liouville.lean:44` (already `n`-indexed), the bounded Liouville family at
`Liouville.lean:114/:123/:128/:135`, `hasSum_taylorSeries_of_entire` at
`TaylorSeries.lean:129` under `[CompleteSpace E]` (variable line `:35`), and
`Polynomial.div_tendsto_atTop_zero_of_degree_lt` at
`Analysis/Polynomial/Basic.lean:161` (inside `namespace Polynomial`, opened
`:32`).

## Candidate fields

- **Mechanism.** The honest primary formulation is the **vanishing-coefficient
  lemma L1**: for `k > n`, `iteratedDeriv k f c = 0`, obtained by letting
  `R → ∞` in the pinned, already-`k`-indexed Cauchy estimate
  `Complex.norm_iteratedDeriv_le_of_forall_mem_sphere_norm_le`
  (Liouville.lean:44) applied on spheres `sphere c R` of growing radius: on
  such a sphere `‖z‖ ≤ ‖c‖ + R`, so the growth hypothesis gives the boundary
  bound `C * (1 + ‖c‖ + R) ^ n`, the estimate gives
  `‖iteratedDeriv k f c‖ ≤ k.factorial * (C * (1 + ‖c‖ + R) ^ n) / R ^ k`, and
  the right side tends to `0` (degree `n < k`;
  `Polynomial.div_tendsto_atTop_zero_of_degree_lt`,
  Analysis/Polynomial/Basic.lean:161). Everything after L1 is bookkeeping: the
  entire-Taylor `HasSum` (TaylorSeries.lean:129) collapses to the partial sum
  over `Finset.range (n+1)` by `hasSum_sum_of_ne_finset_zero`
  (InfiniteSum/Defs.lean:295) and `HasSum.unique` (InfiniteSum/Defs.lean:326),
  giving the Banach-valued finite Taylor form L2; the `Polynomial ℂ` packaging
  L3 is `eval_finsetSum` + `natDegree_sum_le_of_forall_le`; L4/L5 are
  small-degree corollaries via `eq_C_of_natDegree_le_zero` and
  `exists_eq_X_add_C_of_natDegree_le_one`.
- **Expected information gain.** Fills `UPSTREAM_POOL.md` §0 row 5 as a
  concrete, fully-pinned statement surface, and provides the L4 sanity anchor
  (degree 0 must recover `Differentiable.exists_const_forall_eq_of_bounded`,
  Liouville.lean:123). No information about the truth of RH, about ζ/ξ, or
  about any barrier is produced.
- **Claim boundary.** All of L1–L5 are unconditional consequences of pinned
  Mathlib theorems; **no repo theorem is a prerequisite of anything here**, and
  nothing here is a prerequisite of any repo theorem. The package contains
  zero `def`s. Nothing touches growth order, canonical products, zero
  enumeration, counting, or any route's research obligation. Full statement in
  §Claim boundary.
- **Death condition (stop rule).** Stop or split if a proof would need a new
  axiom, an unproved conjecture, a growth-order *definition*, a
  maximum-modulus or three-circles input, or a new definition of any kind; and
  do not present this pool item as closing `S1-GROWTH` or any other barrier
  row. Full list in §Death conditions.

Proposed module preamble (name-resolution review only):

```lean
import Mathlib.Analysis.Complex.Liouville        -- Cauchy estimate :44, bounded family
import Mathlib.Analysis.Complex.TaylorSeries     -- hasSum_taylorSeries_of_entire
import Mathlib.Analysis.Polynomial.Basic         -- div_tendsto_atTop_zero_of_degree_lt
import Mathlib.Algebra.Polynomial.BigOperators   -- natDegree_sum_le_of_forall_le
import Mathlib.Algebra.Polynomial.Degree.SmallDegree -- exists_eq_X_add_C_of_natDegree_le_one

open Nat Filter Metric Polynomial
open scoped Topology
```

`open Nat` mirrors `TaylorSeries.lean:33` so the `i !` notation in L2 resolves.
`Mathlib.Algebra.Polynomial.Eval.Defs` (for `eval_finsetSum`) and
`Mathlib.Topology.Algebra.InfiniteSum.Defs` arrive transitively.

Name-collision scan (grep over the pinned tree this session): **zero hits** for
all five proposed names — `iteratedDeriv_eq_zero_of_norm_le_pow`,
`taylorSum_eq_of_norm_le_pow`, `exists_polynomial_of_norm_le_pow`,
`exists_const_forall_eq_of_norm_le`, `exists_affine_of_norm_le_pow_one`. A
repo-side scan also returns zero hits. The package introduces **no new
definitions** — five theorems over pinned objects only.

---

## 0. Exact pinned interface (quoted from the tree at the pin)

```lean
-- Analysis/Complex/Liouville.lean:44 — THE analytic input, already k-indexed.
-- Section variables (:31-32): {F : Type v} [NormedAddCommGroup F] [NormedSpace ℂ F].
theorem norm_iteratedDeriv_le_of_forall_mem_sphere_norm_le [CompleteSpace F] {c : ℂ} {R C : ℝ}
    {f : ℂ → F} (n : ℕ) (hR : 0 < R) (hf : DiffContOnCl ℂ f (ball c R))
    (hC : ∀ z ∈ sphere c R, ‖f z‖ ≤ C) :
    ‖iteratedDeriv n f c‖ ≤ n.factorial * C / R ^ n
-- Its own proof body uses `mem_sphere_iff_norm.1 hz` at :47 — the sphere-membership
-- rewrite L1 needs is precedented in the very file being extended.

-- Analysis/Complex/Liouville.lean:114, :123, :128, :135 — the bounded-only family
-- (namespace Differentiable, E → F). :123 is the L4 sanity anchor.
theorem apply_eq_apply_of_bounded (hf : Differentiable ℂ f) (hb : IsBounded (range f)) …
theorem exists_const_forall_eq_of_bounded (hf : Differentiable ℂ f)
    (hb : IsBounded (range f)) : ∃ c, ∀ z, f z = c
theorem exists_eq_const_of_bounded … : ∃ c, f = const E c
theorem eq_const_of_tendsto_cocompact …

-- Analysis/Complex/TaylorSeries.lean:35 (file variables), :124 (section `entire`
-- variables: ⦃f : ℂ → E⦄ (hf : Differentiable ℂ f) (c z : ℂ) — hf, c, z EXPLICIT,
-- so L2's application `hasSum_taylorSeries_of_entire hf c z` is the right arity),
-- :129, :137, :143.
-- NOTE the smul-shape and the (z - c) ^ n factor ORDER: (n !)⁻¹ • (z-c)^n • deriv.
variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E] [CompleteSpace E] ⦃f : ℂ → E⦄
lemma hasSum_taylorSeries_of_entire (hf : Differentiable ℂ f) (c z : ℂ) :
    HasSum (fun n : ℕ ↦ (n ! : ℂ)⁻¹ • (z - c) ^ n • iteratedDeriv n f c) (f z)   -- :129
lemma taylorSeries_eq_of_entire :
    ∑' n : ℕ, (n ! : ℂ)⁻¹ • (z - c) ^ n • iteratedDeriv n f c = f z              -- :137
lemma taylorSeries_eq_of_entire' {f : ℂ → ℂ} (hf : Differentiable ℂ f) :
    ∑' n : ℕ, (n ! : ℂ)⁻¹ * iteratedDeriv n f c * (z - c) ^ n = f z              -- :143

-- Topology/Algebra/InfiniteSum/Defs.lean:106 — HasProd/HasSum carry a SummationFilter
-- parameter at this pin, DEFAULTED to `unconditional β`. The Taylor HasSum above uses
-- the default. All finite-collapse/uniqueness lemmas are stated over L with a class
-- hypothesis; the default instances discharge them silently — but only if nothing
-- disturbs the default (§PL-2a).
def HasProd (f : β → α) (a : α) (L := unconditional β) : Prop
-- :295, additive twin `hasSum_sum_of_ne_finset_zero` via @[to_additive]:
theorem hasProd_prod_of_ne_finset_one (hf : ∀ b ∉ s, f b = 1) [L.LeAtTop] :
    HasProd f (∏ b ∈ s, f b) L
-- :323 variables, :326 (additive twin `HasSum.unique`):
variable [T2Space α] [L.NeBot]
theorem HasProd.unique {a₁ a₂ : α} : HasProd f a₁ L → HasProd f a₂ L → a₁ = a₂

-- Topology/Algebra/InfiniteSum/SummationFilter.lean:168, :171, :173 — the default
-- filter and BOTH instances the collapse + uniqueness pair needs. Nothing to build.
@[simps] def unconditional : SummationFilter β where filter := atTop
instance : (unconditional β).LeAtTop := ⟨le_rfl⟩
instance : (unconditional β).NeBot := ⟨atTop_neBot⟩

-- Analysis/Calculus/IteratedDeriv/Defs.lean:55, :227
def iteratedDeriv (n : ℕ) (f : 𝕜 → F) (x : 𝕜) : F
theorem iteratedDeriv_eq_iteratedFDeriv : …

-- Analysis/Calculus/DiffContOnCl.lean:42
theorem Differentiable.diffContOnCl (h : Differentiable 𝕜 f) : DiffContOnCl 𝕜 f s

-- Analysis/Polynomial/Basic.lean:161 (namespace Polynomial, opened :32) — the R → ∞ kill
theorem div_tendsto_atTop_zero_of_degree_lt (hdeg : P.degree < Q.degree) :
    Tendsto (fun x => eval x P / eval x Q) atTop (𝓝 0)

-- Polynomial degree/eval API
theorem natDegree_sum_le (f : ι → S[X]) : …                 -- BigOperators.lean:61
lemma natDegree_sum_le_of_forall_le {n : ℕ} (f : ι → S[X])
    (h : ∀ i ∈ s, natDegree (f i) ≤ n) :
    natDegree (∑ i ∈ s, f i) ≤ n                            -- BigOperators.lean:65
theorem natDegree_C_mul_X_pow_le (a : R) (n : ℕ) :
    natDegree (C a * X ^ n) ≤ n                             -- Degree/Defs.lean:365
theorem degree_X_pow : degree ((X : R[X]) ^ n) = n          -- Degree/Defs.lean:514
theorem natDegree_X_pow : natDegree ((X : R[X]) ^ n) = n    -- Degree/Defs.lean:518
theorem eval_finsetSum (s : Finset ι) (g : ι → R[X]) (x : R) :
    (∑ i ∈ s, g i).eval x = ∑ i ∈ s, (g i).eval x           -- Eval/Defs.lean:343
@[deprecated (since := "2026-04-08")] alias eval_finset_sum := eval_finsetSum  -- :347
theorem eq_C_of_natDegree_le_zero (h : natDegree p ≤ 0) :
    p = C (coeff p 0)                                       -- Degree/Operations.lean:479
theorem eq_X_add_C_of_natDegree_le_one (h : natDegree p ≤ 1) :
    p = C (p.coeff 1) * X + C (p.coeff 0)                   -- Degree/SmallDegree.lean:43
theorem exists_eq_X_add_C_of_natDegree_le_one (h : natDegree p ≤ 1) :
    ∃ a b, p = C a * X + C b                                -- Degree/SmallDegree.lean:50

-- Order/limit glue
@[mono, gcongr, bound]
theorem pow_le_pow_left₀ (ha : 0 ≤ a) (hab : a ≤ b) : ∀ n, a ^ n ≤ b ^ n
                                                 -- Algebra/Order/GroupWithZero/Basic.lean:470
theorem le_of_tendsto / ge_of_tendsto (via @[to_dual] at :130)
                                                 -- Topology/Order/OrderClosed.lean:131
theorem eventually_gt_atTop [Preorder α] [NoTopOrder α] (a) : ∀ᶠ x in atTop, a < x
                                                 -- Order/Filter/AtTopBot/Defs.lean:61

-- Normed-group glue (additive names via @[to_additive])
theorem mem_sphere_iff_norm : b ∈ sphere a r ↔ ‖b - a‖ = r
              -- Analysis/Normed/Group/Basic.lean:885-886 (attr := simp high), twin of
              -- mem_sphere_iff_norm'; the multiplicative primed form is the source
theorem norm_le_norm_add_norm_sub' (u v) : ‖u‖ ≤ ‖v‖ + ‖u - v‖
              -- Basic.lean:182 (twin of norm_le_norm_add_norm_div'); in-tree additive
              -- uses confirmed (e.g. Analysis/Normed/Algebra/Spectrum.lean)
lemma norm_le_zero_iff : ‖a‖ ≤ 0 ↔ a = 0
              -- Basic.lean:990-991 (to_additive (attr := simp) of norm_le_zero_iff')
lemma isBounded_iff_forall_norm_le : IsBounded s ↔ ∃ C, ∀ x ∈ s, ‖x‖ ≤ C
              -- Analysis/Normed/Group/Bounded.lean:71-72 (to_additive twin)
```

---

## 1. Primary-formulation decision

### Decision: **the vanishing-coefficient lemma L1 (`iteratedDeriv k f c = 0` for `k > n`) is primary; the `Polynomial ℂ` statement L3 is packaging.**

Justification, stated so a reviewer can reject it cheaply:

1. **L1 is where all the analysis lives, and every analytic ingredient is
   pinned.** The Cauchy estimate at Liouville.lean:44 is already indexed by the
   derivative order `k` and already uniform in the radius `R` (hypotheses only
   `0 < R`, `DiffContOnCl` on `ball c R`, a sphere bound). Growing radii cost
   nothing: an entire `f` is `DiffContOnCl` on every ball
   (`Differentiable.diffContOnCl`, DiffContOnCl.lean:42, with `s := ball c R`
   at any `R`). L1 is stated at an **arbitrary center `c`**, not just `0`,
   because the estimate is; this is free and makes L2 centre-generic.
2. **L1 is Banach-valued; L3 cannot be.** `[CompleteSpace F]` is forced by the
   Cauchy estimate and by `hasSum_taylorSeries_of_entire`
   (TaylorSeries.lean:35). The `Polynomial ℂ` packaging in L3 needs
   scalar-valued `f` for `Polynomial.eval`; L2 keeps the Banach-valued finite
   Taylor form so the general-codomain content is not silently dropped at the
   packaging step.
3. **`natDegree ≤ n`, not `degree ≤ n`, in L3.** The pinned bounding tools are
   `natDegree_sum_le_of_forall_le` (BigOperators.lean:65) and
   `natDegree_C_mul_X_pow_le` (Degree/Defs.lean:365) — both `natDegree`-shaped;
   `natDegree` avoids `WithBot ℕ` bookkeeping at the zero polynomial. A
   `degree`-shaped twin is derivable downstream via `degree_le_of_natDegree_le`
   plus a cast and is deliberately **not** part of the surface.
4. **Junk-value audit.** `analyticOrderAt`-style junk does not arise: L1's
   conclusion is an equation in `F`, and every tool used is total or has its
   hypotheses supplied (`0 < R` from `eventually_gt_atTop 0`;
   `T2Space`/`NeBot` for `HasSum.unique` from the normed-space topology and
   `SummationFilter.lean:173`). The only sign condition, `0 ≤ C`, is **derived,
   not assumed**: `hC` at `z = 0` gives `0 ≤ ‖f 0‖ ≤ C * (1 + 0) ^ n = C`.
   Callers may pass any real `C`.
5. **Rejected alternative carrier:** stating the conclusion as
   `CPolynomialOn ℂ f univ` / `HasFiniteFPowerSeriesOnBall`
   (Analysis/Analytic/CPolynomialDef.lean:62/:79/:94/:99). That carrier is
   pinned and would express "is a polynomial function" without `Polynomial ℂ`,
   but it costs `FormalMultilinearSeries` bookkeeping, does not directly give a
   `natDegree` bound against the `Polynomial` API that downstream consumers
   (and the L4/L5 corollaries) want, and buys nothing L2 does not already give.
   Recorded as **DEFERRED-PL-1**: a `CPolynomialOn` twin is a natural upstream
   companion, not part of this surface.

### API-shape trap (pre-registered, cost one CI cycle if missed)

At this pin `HasSum f a` elaborates as `HasSum f a (unconditional ℕ)` — the
third argument is a **defaulted `SummationFilter`** (InfiniteSum/Defs.lean:106).
The three lemmas L2 composes — `hasSum_taylorSeries_of_entire` (default filter),
`hasSum_sum_of_ne_finset_zero` (`[L.LeAtTop]`), `HasSum.unique`
(`[T2Space α] [L.NeBot]`) — must all be instantiated at the **same** `L`. Using
the default everywhere, the instances at `SummationFilter.lean:171/:173`
discharge both class hypotheses silently. Do **not** write an explicit `L`
anywhere in L2; if unification produces a metavariable for the filter, pin it
with `(L := unconditional ℕ)` on the `hasSum_sum_of_ne_finset_zero` call only.

---

## 2. Statement list L1 – L5

Legend: `[PIN]` provable from pinned Mathlib alone. Every statement below is
`[PIN]`; no repo theorem and no merged-package prerequisite occurs anywhere in
this package.

---

### L1. Vanishing-coefficient lemma `[PIN]` — *the statement that carries all the analysis*

### Statement

```lean
/-- If an entire function grows at most like `C * (1 + ‖z‖) ^ n`, then all its iterated
derivatives of order greater than `n` vanish, everywhere. Cauchy estimate over growing
radii. -/
theorem Complex.iteratedDeriv_eq_zero_of_norm_le_pow
    {F : Type*} [NormedAddCommGroup F] [NormedSpace ℂ F] [CompleteSpace F]
    {f : ℂ → F} {C : ℝ} {n : ℕ} (hf : Differentiable ℂ f)
    (hC : ∀ z : ℂ, ‖f z‖ ≤ C * (1 + ‖z‖) ^ n)
    {k : ℕ} (hnk : n < k) (c : ℂ) :
    iteratedDeriv k f c = 0
```

### Proof skeleton

```lean
  -- C is nonnegative, derived (Decision point 4): specialise hC at 0.
  have hC0 : 0 ≤ C := le_trans (norm_nonneg (f 0)) (by simpa using hC 0)
  -- Step 1: the radius-parametrised estimate.
  have key : ∀ R : ℝ, 0 < R →
      ‖iteratedDeriv k f c‖ ≤ k.factorial * (C * (1 + ‖c‖ + R) ^ n) / R ^ k := by
    intro R hR
    refine norm_iteratedDeriv_le_of_forall_mem_sphere_norm_le k hR hf.diffContOnCl ?_
    intro z hz
    have hz' : ‖z - c‖ = R := mem_sphere_iff_norm.mp hz          -- Liouville.lean:47 precedent
    have hzb : ‖z‖ ≤ ‖c‖ + R := by
      calc ‖z‖ ≤ ‖c‖ + ‖z - c‖ := norm_le_norm_add_norm_sub' z c
        _ = ‖c‖ + R := by rw [hz']
    calc ‖f z‖ ≤ C * (1 + ‖z‖) ^ n := hC z
      _ ≤ C * (1 + ‖c‖ + R) ^ n := by gcongr; · linarith [norm_nonneg z]
        -- gcongr fires mul_le_mul + pow_le_pow_left₀ (GroupWithZero/Basic.lean:470,
        -- @[gcongr]); side goals 0 ≤ C (hC0), 0 ≤ 1 + ‖z‖, 1 + ‖z‖ ≤ 1 + ‖c‖ + R (hzb).
  -- Step 2: the R → ∞ kill via the pinned polynomial-division limit.
  have hlim : Filter.Tendsto
      (fun R : ℝ => k.factorial * (C * (1 + ‖c‖ + R) ^ n) / R ^ k)
      Filter.atTop (nhds 0) := by
    have h := Polynomial.div_tendsto_atTop_zero_of_degree_lt
      (P := Polynomial.C ((k.factorial : ℝ) * C) * (Polynomial.C (1 + ‖c‖) + Polynomial.X) ^ n)
      (Q := Polynomial.X ^ k) (by
        -- degree P ≤ n < k = degree Q
        refine lt_of_le_of_lt ?_ ?_
        · calc Polynomial.degree _ ≤ 0 + n • (1 : WithBot ℕ) := by
                gcongr  -- degree_mul_le, degree_C_le, degree_pow_le, degree_add_le, degree_X_le
          _ ≤ (n : WithBot ℕ) := by simp
        · rw [Polynomial.degree_X_pow]; exact_mod_cast hnk)
    refine h.congr' ?_
    filter_upwards [Filter.eventually_gt_atTop (0 : ℝ)] with R hR
    simp [Polynomial.eval_mul, Polynomial.eval_pow, Polynomial.eval_add,
      Polynomial.eval_C, Polynomial.eval_X, mul_assoc]
    ring_nf
  -- Step 3: squeeze.
  rw [← norm_le_zero_iff]
  exact ge_of_tendsto hlim
    ((Filter.eventually_gt_atTop (0 : ℝ)).mono fun R hR => key R hR)
```

### Pinned dependencies (L1)

- `Complex.norm_iteratedDeriv_le_of_forall_mem_sphere_norm_le` —
  Liouville.lean:44, verified verbatim (`[CompleteSpace F]`, `(n) (hR : 0 < R)
  (hf : DiffContOnCl ℂ f (ball c R)) (hC : ∀ z ∈ sphere c R, ‖f z‖ ≤ C) :
  ‖iteratedDeriv n f c‖ ≤ n.factorial * C / R ^ n`).
- `Differentiable.diffContOnCl` — DiffContOnCl.lean:42 (arbitrary `s`, so it
  specialises to every `ball c R` with no side goal).
- `mem_sphere_iff_norm` — Normed/Group/Basic.lean:885-886 (`@[to_additive
  (attr := simp high)]` twin); used in exactly this position by
  Liouville.lean:47 itself.
- `norm_le_norm_add_norm_sub'` — Basic.lean:182 (additive twin).
- `pow_le_pow_left₀` — GroupWithZero/Basic.lean:470, carries `@[gcongr]`.
- `Polynomial.div_tendsto_atTop_zero_of_degree_lt` —
  Analysis/Polynomial/Basic.lean:161; degree chain from `degree_mul_le`,
  `degree_C_le`, `degree_pow_le`, `degree_add_le`, `degree_X_le`,
  `degree_X_pow` (Degree/Defs.lean:514).
- `ge_of_tendsto` — OrderClosed.lean:130-131 (`@[to_dual]` of `le_of_tendsto`);
  `eventually_gt_atTop` — AtTopBot/Defs.lean:61; `norm_le_zero_iff` —
  Basic.lean:990-991.

### Obligations (L1)

- **PL-1a** (LOW). The `gcongr` discharge in Step 1: the goal
  `C * (1 + ‖z‖) ^ n ≤ C * (1 + ‖c‖ + R) ^ n` must fire `mul_le_mul_of_nonneg_left`
  + `pow_le_pow_left₀` with side goals `0 ≤ C`, `0 ≤ 1 + ‖z‖`,
  `1 + ‖z‖ ≤ 1 + ‖c‖ + R`. Fallback (term mode):
  `mul_le_mul_of_nonneg_left (pow_le_pow_left₀ (by positivity) (by linarith) n) hC0`.
- **PL-1b** (MEDIUM). Step 2's `eval` reconciliation: the polynomial-route limit
  concludes about `fun R => eval R P / eval R Q`, and the `simp; ring_nf` closer
  must turn that into the literal bound expression
  `k.factorial * (C * (1 + ‖c‖ + R) ^ n) / R ^ k` — note `(1 + ‖c‖) + R`
  (polynomial shape) versus `1 + ‖c‖ + R` (goal shape) are the *same term* only
  up to `add_assoc`, which `ring_nf` normalises; a bare `rw` will not. The
  degree chain is now an explicit term chain (Annex A finding A1 removed the
  `gcongr` step, which could not fire: none of `degree_mul_le`/`degree_C_le`/
  `degree_pow_le_of_le`/`degree_add_le`/`degree_X_le` is `@[gcongr]`-tagged at
  the pin); its residual risks are the `WithBot ℕ` arithmetic
  (`0 + ↑n * 1 ≤ ↑n` via `simp`; `(0 : WithBot ℕ) ≤ 1` via `zero_le_one` — if
  the `ZeroLEOneClass (WithBot ℕ)` instance does not fire, close with
  `by norm_num` or `by decide`) and the `degree_pow_le_of_le` conclusion shape
  `b * a` (Degree/Defs.lean:406), which is multiplication, not the `n •` smul
  of `degree_pow_le` (:402). **Fallback route
  (elementary, no Polynomial):** for `R ≥ max 1 (1 + ‖c‖)` bound
  `(1 + ‖c‖ + R) ^ n ≤ (2 * R) ^ n`, so the whole expression is
  `≤ (k.factorial * C * 2 ^ n) * (R ^ k)⁻¹ * R ^ n`, and squeeze with
  `tendsto_pow_atTop` + `Tendsto.inv_tendsto_atTop` on `R ^ (k - n)`; this
  trades the eval reconciliation for `Nat`-subtraction bookkeeping
  (`pow_sub₀`-style, needing `R ≠ 0` and `n ≤ k`). Either route is acceptable;
  the contract does not mandate one.
- **PL-1c** (LOW). Direction check on the squeeze: `ge_of_tendsto (lim) (h : ∀ᶠ
  R, b ≤ g R) : b ≤ a` with `b := ‖iteratedDeriv k f c‖`, `a := 0`. If the
  `to_dual`-generated orientation differs at elaboration, use
  `le_of_tendsto_of_tendsto tendsto_const_nhds hlim` shape instead
  (OrderClosed.lean:469).

*Honesty note.* L1 is **not** a pin gap in the analytic sense: every analytic
ingredient exists at the pin, already in the right shape (the estimate is
`k`-indexed and radius-uniform). What is absent at the pin is the *assembled
statement* — `UPSTREAM_POOL.md` §0 row 5, re-verified this session by reading
`Liouville.lean` in full: every Liouville-type conclusion there rests on
`IsBounded (range f)` (`:114`/`:123`/`:128`) or the stronger cocompact-limit
hypothesis (`:135`), and no growth-to-degree statement exists anywhere in the
file. L1 must not be presented as "Mathlib cannot do Cauchy estimates"; it is
the missing one-quantifier-stronger corollary.

---

### L2. Banach-valued finite Taylor form `[PIN]` — *the collapse seam*

### Statement

```lean
/-- An entire function of polynomial growth of degree at most `n` equals its Taylor
polynomial of degree `n` at every centre. Banach-valued. -/
theorem Complex.taylorSum_eq_of_norm_le_pow
    {F : Type*} [NormedAddCommGroup F] [NormedSpace ℂ F] [CompleteSpace F]
    {f : ℂ → F} {C : ℝ} {n : ℕ} (hf : Differentiable ℂ f)
    (hC : ∀ z : ℂ, ‖f z‖ ≤ C * (1 + ‖z‖) ^ n) (c z : ℂ) :
    f z = ∑ i ∈ Finset.range (n + 1), (i ! : ℂ)⁻¹ • (z - c) ^ i • iteratedDeriv i f c
```

The summand is written in the **exact smul-shape and factor order of
`hasSum_taylorSeries_of_entire`** (TaylorSeries.lean:129-130:
`(n !)⁻¹ • (z - c) ^ n • iteratedDeriv n f c`), deliberately, so that the two
`HasSum` witnesses below are about the *syntactically identical* function and
`HasSum.unique` applies with no congruence step.

### Proof skeleton

```lean
  have h1 : HasSum (fun i : ℕ ↦ (i ! : ℂ)⁻¹ • (z - c) ^ i • iteratedDeriv i f c) (f z) :=
    hasSum_taylorSeries_of_entire hf c z                       -- TaylorSeries.lean:129
  have h2 : HasSum (fun i : ℕ ↦ (i ! : ℂ)⁻¹ • (z - c) ^ i • iteratedDeriv i f c)
      (∑ i ∈ Finset.range (n + 1), (i ! : ℂ)⁻¹ • (z - c) ^ i • iteratedDeriv i f c) :=
    hasSum_sum_of_ne_finset_zero fun i hi ↦ by                 -- InfiniteSum/Defs.lean:295
      have hni : n < i := by
        simpa [Finset.mem_range, Nat.lt_succ_iff, not_le] using hi
      rw [iteratedDeriv_eq_zero_of_norm_le_pow hf hC hni c]    -- L1
      simp                                                     -- smul_zero twice
  exact h1.unique h2                                           -- InfiniteSum/Defs.lean:326
```

### Pinned dependencies (L2)

L1; `Complex.hasSum_taylorSeries_of_entire` — TaylorSeries.lean:129
(`[CompleteSpace E]` from :35); `hasSum_sum_of_ne_finset_zero` —
`@[to_additive]` twin of `hasProd_prod_of_ne_finset_one`,
InfiniteSum/Defs.lean:295, hypothesis `[L.LeAtTop]`; `HasSum.unique` —
`@[to_additive]` twin of `HasProd.unique`, InfiniteSum/Defs.lean:326, under
`[T2Space α] [L.NeBot]` (variables :323); default-filter instances
`(unconditional ℕ).LeAtTop` / `.NeBot` — SummationFilter.lean:171/:173.
`T2Space F` holds for every normed group.

### Obligations (L2)

- **PL-2a** (MEDIUM — **the riskiest obligation of the package**). The
  three-lemma `HasSum` seam under the new `SummationFilter` API (§1 API-shape
  trap): `h1`, `h2`, and `.unique` must share the defaulted
  `unconditional ℕ` filter, with instance resolution — not unification —
  supplying `LeAtTop` and `NeBot`. This exact three-lemma composition has an
  in-tree precedent *pair* (CPolynomialDef.lean:72 and :215 use
  collapse + `.unique` against a `HasSum` from elsewhere) but **not** against
  `hasSum_taylorSeries_of_entire`, and nothing here was elaborated. If default
  arguments leave a filter metavariable, pin `(L := unconditional ℕ)` at the
  `hasSum_sum_of_ne_finset_zero` call. If `.unique` dot-notation fails to
  resolve on the additive side, write `HasSum.unique h1 h2` fully qualified.
- **PL-2b** (LOW). The membership arithmetic `i ∉ Finset.range (n+1) → n < i`:
  fallback `by omega` after `Finset.mem_range` + `not_lt`.
- **PL-2c** (LOW). The vanishing rewrite must produce `(i !)⁻¹ • (z-c)^i • 0`
  then close by `smul_zero`; if `rw` stumbles on the binder-free occurrence,
  use `simp [iteratedDeriv_eq_zero_of_norm_le_pow hf hC hni c]` directly.

---

### L3. Main statement: polynomial packaging `[PIN]`

### Statement

```lean
/-- **Liouville, polynomial-growth form**: an entire function bounded by
`C * (1 + ‖z‖) ^ n` is a polynomial of degree at most `n`. -/
theorem Complex.exists_polynomial_of_norm_le_pow
    {f : ℂ → ℂ} {C : ℝ} {n : ℕ} (hf : Differentiable ℂ f)
    (hC : ∀ z : ℂ, ‖f z‖ ≤ C * (1 + ‖z‖) ^ n) :
    ∃ p : Polynomial ℂ, p.natDegree ≤ n ∧ ∀ z : ℂ, f z = p.eval z
```

### Proof skeleton

```lean
  refine ⟨∑ i ∈ Finset.range (n + 1),
      Polynomial.C ((i ! : ℂ)⁻¹ * iteratedDeriv i f 0) * Polynomial.X ^ i, ?_, ?_⟩
  · -- degree bound: pure bookkeeping
    refine Polynomial.natDegree_sum_le_of_forall_le _ _ fun i hi ↦ ?_   -- BigOperators.lean:65
    exact (Polynomial.natDegree_C_mul_X_pow_le _ i).trans               -- Degree/Defs.lean:365
      (Nat.lt_succ_iff.mp (Finset.mem_range.mp hi))
  · -- evaluation: L2 at c = 0, then push eval through the finite sum
    intro z
    rw [taylorSum_eq_of_norm_le_pow hf hC 0 z]                          -- L2
    rw [Polynomial.eval_finsetSum]                                      -- Eval/Defs.lean:343
    refine Finset.sum_congr rfl fun i _ ↦ ?_
    -- LHS summand: (i !)⁻¹ • (z - 0) ^ i • iteratedDeriv i f 0   (ℂ-smul on ℂ)
    -- RHS summand: eval z (C ((i !)⁻¹ * iteratedDeriv i f 0) * X ^ i)
    simp only [Polynomial.eval_mul, Polynomial.eval_C, Polynomial.eval_pow,
      Polynomial.eval_X, smul_eq_mul, sub_zero]
    ring
```

### Pinned dependencies (L3)

L2; `Polynomial.natDegree_sum_le_of_forall_le` — BigOperators.lean:65;
`Polynomial.natDegree_C_mul_X_pow_le` — Degree/Defs.lean:365;
`Polynomial.eval_finsetSum` — Eval/Defs.lean:343 (**not** the deprecated
`eval_finset_sum`, :347); `Polynomial.eval_mul/eval_C/eval_pow/eval_X`;
`smul_eq_mul` (ℂ as algebra over itself); `Finset.sum_congr`.

### Obligations (L3)

- **PL-3a** (MEDIUM). The per-summand reconciliation: the L2 shape is
  `(i !)⁻¹ • (z - 0) ^ i • D` (two nested smuls, power of `z - 0`, factor order
  coefficient·power·derivative) while the eval shape is
  `((i !)⁻¹ * D) * z ^ i`. `smul_eq_mul` + `sub_zero` + `ring` must close the
  commutation/reassociation. This is the "real bookkeeping" step
  `UPSTREAM_POOL.md` §4.3 named. Fallback: prove a one-line `have hsummand :
  ∀ (a b w : ℂ) (i : ℕ), a • (w - 0) ^ i • b = a * b * w ^ i := by intros; simp
  [smul_eq_mul, sub_zero]; ring` and rewrite with it before `eval_finsetSum`.
- **PL-3b** (LOW). `natDegree_sum_le_of_forall_le` binder order
  (`(f) (h)` after section variables `s`): if the underscore application
  misfires, name the Finset explicitly:
  `Polynomial.natDegree_sum_le_of_forall_le (s := Finset.range (n+1)) …`.
- **PL-3c** (LOW). The conclusion's `∀ z, f z = p.eval z` is deliberately
  pointwise, not `f = p.eval ·` (funext form) and not `f = ⇑(Polynomial.aeval …)`;
  a funext twin is derivable by `funext` downstream and is not part of the
  surface.

---

### L4. Degree-0 corollary `[PIN]` — *the sanity anchor: must recover pinned Liouville*

### Statement

```lean
/-- Degree-0 case: recovers Liouville's theorem. Sanity anchor against
`Differentiable.exists_const_forall_eq_of_bounded` (Liouville.lean:123). -/
theorem Complex.exists_const_forall_eq_of_norm_le
    {f : ℂ → ℂ} {C : ℝ} (hf : Differentiable ℂ f) (hC : ∀ z : ℂ, ‖f z‖ ≤ C) :
    ∃ c : ℂ, ∀ z : ℂ, f z = c
```

### Proof skeleton

```lean
  obtain ⟨p, hdeg, hev⟩ := exists_polynomial_of_norm_le_pow (n := 0) hf
    (fun z ↦ by simpa using hC z)                 -- (1 + ‖z‖) ^ 0 = 1, pow_zero + mul_one
  refine ⟨p.coeff 0, fun z ↦ ?_⟩
  rw [hev z, Polynomial.eq_C_of_natDegree_le_zero hdeg]   -- Degree/Operations.lean:479
  simp                                                     -- eval_C
```

### Pinned dependencies (L4)

L3; `Polynomial.eq_C_of_natDegree_le_zero` — Degree/Operations.lean:479;
`pow_zero`, `mul_one`, `Polynomial.eval_C`.

Cross-check (the reason L4 exists): the *same statement* already follows from
the pinned bounded family — `Differentiable.exists_const_forall_eq_of_bounded`
(Liouville.lean:123) via `isBounded_iff_forall_norm_le`
(Normed/Group/Bounded.lean:71-72, range-membership massage). L4 being derivable
**both** ways is the package's self-check; if the L3-route and the pinned-route
statements ever disagree in shape, the L3 route is wrong. This mirrors the
`UPSTREAM_POOL.md` §4.1 note ("a useful sanity target").

### Obligations (L4)

- **PL-4a** (LOW). The `n := 0` specialisation massage
  `C * (1 + ‖z‖) ^ 0 = C`: `simpa` must fire `pow_zero` + `mul_one`. Fallback:
  `by rw [pow_zero, mul_one]; exact hC z`.

---

### L5. Degree-1 corollary `[PIN]`

### Statement

```lean
/-- Degree-1 case: an entire function of at most linear growth is affine. -/
theorem Complex.exists_affine_of_norm_le_pow_one
    {f : ℂ → ℂ} {C : ℝ} (hf : Differentiable ℂ f)
    (hC : ∀ z : ℂ, ‖f z‖ ≤ C * (1 + ‖z‖)) :
    ∃ a b : ℂ, ∀ z : ℂ, f z = a * z + b
```

### Proof skeleton

```lean
  obtain ⟨p, hdeg, hev⟩ := exists_polynomial_of_norm_le_pow (n := 1) hf
    (fun z ↦ by simpa using hC z)                 -- (1 + ‖z‖) ^ 1 = 1 + ‖z‖, pow_one
  obtain ⟨a, b, hp⟩ := Polynomial.exists_eq_X_add_C_of_natDegree_le_one hdeg
                                                   -- Degree/SmallDegree.lean:50
  refine ⟨a, b, fun z ↦ ?_⟩
  rw [hev z, hp]
  simp                                             -- eval_add, eval_mul, eval_C, eval_X
```

### Pinned dependencies (L5)

L3; `Polynomial.exists_eq_X_add_C_of_natDegree_le_one` —
Degree/SmallDegree.lean:50 (existential form; the coefficient-explicit
`eq_X_add_C_of_natDegree_le_one` at :43 is the fallback if the existential's
witness order fights the goal).

### Obligations (L5)

- **PL-5a** (LOW). `pow_one` massage, dual of PL-4a.
- **PL-5b** (LOW). The eval simp set must produce `a * z + b` in that literal
  operand order from `eval z (C a * X + C b)`; if `simp` normalises to
  `a * z + b` differently, close with `ring` after.

---

## 3. Dependency map

```
pinned Cauchy estimate (Liouville.lean:44)  ┐
pinned div_tendsto (Polynomial/Basic.lean:161) ├─→ L1 (vanishing coefficients; Banach)
pinned glue (sphere/norm/gcongr/tendsto)    ┘        │
pinned Taylor HasSum (TaylorSeries.lean:129) ────────┤
pinned SummationFilter collapse+unique       ────────┴─→ L2 (finite Taylor sum; Banach)
                                                          │
pinned Polynomial eval/natDegree API ─────────────────────┴─→ L3 (main; ℂ → ℂ)
                                                               ├─→ L4 (degree 0; anchors
                                                               │    to Liouville.lean:123)
                                                               └─→ L5 (degree 1)
```

No cycle; L1 is the unique analytic node. Dropping L4/L5 costs nothing
structurally (they consume L3 only) but forfeits the sanity anchor; dropping L2
and inlining it into L3 is possible but forfeits the Banach-valued form —
neither drop is recommended.

---

## Claim boundary

- **Every statement L1–L5 is generic**: quantified over an arbitrary `f` with a
  hypothesis on `f` alone. Nothing mentions `riemannZeta`,
  `completedRiemannZeta`, `riemannXi`, an `LSeries`, a strip, a line, or the
  zero set of any specific function. The package is route-neutral by
  construction, exactly as `UPSTREAM_POOL.md` demands of pool items.
- **No barrier row changes.** In particular `S1-GROWTH`
  (repo:`domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md:388`, "no zeta/xi
  vertical or order-one growth theorem") is **not** closed, advanced, or
  re-scoped by this contract, and must not be: L1–L5 contain no growth-order
  notion at all — the hypothesis `‖f z‖ ≤ C * (1 + ‖z‖) ^ n` is polynomial
  growth, a strictly weaker regime than the order-one exponential growth that
  row is about, and the row is scoped to this repository's ζ/ξ layer besides
  (the `MULTIPLICITY_CONTRACT.md` finding-A4 rule: generic pinned or
  generic-proposed Mathlib lowers cost, never retires a row). The same applies
  to every other row.
- **No route is selected, no RH claim is made.** An entire-function statement
  provable for all functions of polynomial growth carries no information about
  the truth of the Riemann Hypothesis, and this document must not be cited as
  progress toward it.
- **No repo coupling in either direction.** No statement here consumes a repo
  theorem; no repo theorem is promised a consumer here. If the package is ever
  built, its natural destination is upstream Mathlib
  (`UPSTREAM_POOL.md` §4 proposed home), not `ResearchOS/`.
- **What acceptance means.** Stage-one acceptance of L1–L5 is a review verdict
  on a statement surface: no module, no ledger row, no registry entry, no
  axiom-audit entry, no kernel verdict, no `targets/*.json` movement.
- **The `n`-uniformity claim is deliberately absent.** Nothing here states or
  implies a converse (a polynomial of degree `n` has growth exponent `n` —
  true but not needed), nor sharpness, nor anything about `degree p = n`.
  `natDegree p ≤ n` is the whole degree content.

---

## Death conditions

Stop and re-plan — do **not** patch around — if any of the following occurs.

1. **A new axiom would be needed.** No `axiom`, no `sorry`, no `admit`, no
   `native_decide` on an unproved side condition. The Lean kernel is the sole
   verifier.
2. **Any dependency on an unproved conjecture**, including one smuggled into a
   binder.
3. **A new definition starts to look necessary.** The package must contain
   zero `def`s. If a named "polynomial growth" predicate or a `maxModulus`-style
   definition creeps in, that is `UPSTREAM_POOL.md` §1 territory (a *different*
   pool item with its own unpinned obligations) and this package must not
   absorb it.
4. **A maximum-modulus, three-circles, or growth-order input appears.** L1's
   analysis is one Cauchy estimate plus a real limit. If a proof attempt
   reaches for `AbsMax`, `Hadamard.lean`, or any `limsup`, the formulation has
   drifted; return to the L1 skeleton.
5. **The `HasSum` seam (PL-2a) cannot be closed against the SummationFilter
   API.** Fallback *within* the death condition's stop-and-replan: restate L2's
   proof via `tsum` (`taylorSeries_eq_of_entire`, TaylorSeries.lean:137, plus
   `tsum_eq_sum` over the vanishing complement — `@[to_additive]` twin of
   `tprod_eq_prod`, InfiniteSum/Basic.lean:457, hypothesis `[L.LeAtTop]`, so
   the same SummationFilter seam as PL-2a applies to the fallback too) rather
   than `HasSum.unique`. If
   *both* routes fail to elaborate, the pool item's "cheap — close to a
   corollary" difficulty assessment is wrong and `UPSTREAM_POOL.md` §4.3 must
   be corrected before any further attempt.
6. **The statement is weakened to avoid the bookkeeping.** Do not replace L3's
   `Polynomial ℂ` conclusion with "all derivatives above `n` vanish" *alone*
   (that is L1, already in the surface) and then call the main statement
   delivered. The pool row asks for the polynomial conclusion; L3 is the
   deliverable shape.
7. **Sign or shape drift in the growth hypothesis.** `C * (1 + ‖z‖) ^ n` with
   derived `0 ≤ C` is the contract shape (the `1 +` base is load-bearing:
   `1 ≤ 1 + ‖z‖` keeps every monotonicity step one-sided, the same reason
   recorded at `UPSTREAM_POOL.md` §1.1 design choice 3). Do not switch to
   `‖z‖ ^ n` (false to apply at `z = 0` for `n ≥ 1` as a bound shape without a
   constant term) or add `0 ≤ C` as a hypothesis (junk the caller must
   discharge; it is derivable).
8. **A barrier row or route authorization is read out of this contract.** This
   is a pool-item statement design. `S1-GROWTH` and every other row stay
   exactly as they are; the RH queue and the decision substrate are the only
   authorities for what is worked next, and both currently authorize no route.

---

## ANNEX A: adversarial review record (2026-08-07)

Independent adversarial review of the draft-v1 statement surface. Mathlib
checkout re-verified by `git rev-parse HEAD` at
`/workspace/leanprover-community/mathlib4` →
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`; repo agreement re-verified at
`lake-manifest.json:8`. Every `file:line` in the contract was re-opened at that
revision; the repo-side citations were re-opened on the working tree. Attack
fronts assigned to this review: (1) the formal-multilinear-series vs
`Polynomial` bridge, (2) radius-to-infinity limit bookkeeping, (3) scope creep.

**Verdict: `SOUND_WITH_FIXES`.** Five findings (A1–A5), all resolved in place
above. The statement surface L1–L5 is unchanged — every fix is to a locator, a
proof skeleton, or prose; no signature moved. This verdict accepts a statement
surface only: it is not a Lean kernel verdict, it does not promote a module,
and it closes no barrier row.

### A. Findings resolved in place

| ID | Severity | Finding | Fix applied |
|---|---|---|---|
| **A1** | MEDIUM | L1 Step 2's degree chain closed with `by gcongr`, but **none** of `degree_mul_le` (Degree/Defs.lean:396), `degree_C_le` (:153), `degree_pow_le` (:402), `degree_add_le` (:326), `degree_X_le` (:240) carries `@[gcongr]` at the pin (attribute grep over `Degree/Defs.lean` and `Degree/Operations.lean`: zero attribute hits), and the goal `degree P ≤ 0 + n • 1` is a bound, not a gcongr congruence shape — the tactic has nothing to fire and the step fails outright, unlike the Step 1 norm `gcongr`, whose `pow_le_pow_left₀` really is tagged (`@[mono, gcongr, bound]`, GroupWithZero/Basic.lean:469-470). PL-1b under-scoped this as merely "untested" | Skeleton rewritten to an explicit term chain via `degree_pow_le_of_le` (Degree/Defs.lean:406); PL-1b restated with the residual `WithBot ℕ` risks and the `:406` mul-shape (`b * a`) vs `:402` smul-shape (`n • degree p`) distinction; L1 pinned-dependencies row given full locators |
| **A2** | LOW | The `mem_sphere_iff_norm.1 hz` precedent inside the pinned Cauchy estimate is at **Liouville.lean:49**, not `:47` as cited in three places (§0 quote comment, L1 skeleton comment, L1 pinned dependencies) | All three occurrences corrected to `:49` |
| **A3** | LOW | Scope paragraph and L1 Honesty note claimed "every statement in the pinned `Liouville.lean` hypothesises `IsBounded (range f)`" — false as universally quantified: the Cauchy estimates (`:44`, `:69`) hypothesise a sphere bound, and `eq_const_of_tendsto_cocompact` (`:135`) hypothesises a cocompact limit, not `IsBounded (range f)`. The load-bearing absence claim (no growth-to-degree conclusion anywhere in the file) is **correct** and was re-verified | Both passages reworded to quantify over the Liouville-type conclusions (`:114`/`:123`/`:128` bounded, `:135` cocompact) and keep the absence claim |
| **A4** | LOW | Death condition 5's fallback cited `tsum_eq_sum` with no locator and no SummationFilter caveat. At the pin it is the `@[to_additive]` twin of `tprod_eq_prod`, **InfiniteSum/Basic.lean:457**, hypothesis `[L.LeAtTop]` — the fallback therefore sits on the *same* PL-2a seam it is meant to escape (though `tsum_eq_sum` composes two lemmas where the primary route composes three) | Locator and caveat added to death condition 5 |
| **A5** | LOW | The §0 quote block gave TaylorSeries.lean:35 as "variables" but omitted `:124` (section `entire`: `⦃f⦄ (hf : Differentiable ℂ f) (c z : ℂ)`), the line that makes `hf`, `c`, `z` explicit — the fact L2's three-argument application depends on | `:124` added to the quote block with the binder detail spelled out |

### B. Citations re-verified as CORRECT (no change)

Pinned Mathlib — `Analysis/Complex/Liouville.lean` :44 (Cauchy estimate,
signature verbatim incl. `[CompleteSpace F]`, section variables `:32-33`),
:109 (`namespace Differentiable`), :114, :123, :128, :135 (bounded family).
`Analysis/Complex/TaylorSeries.lean` :33 (`open Nat`), :35 (variables incl.
`[CompleteSpace E]`), :122-:124 (section `entire`), :129, :137, :143 (statements
and smul-shape/factor-order verbatim; the locator-corrections table's `:137` /
`:143` against the pool's `:139` is right).
`Topology/Algebra/InfiniteSum/Defs.lean` :106 (`HasProd` with defaulted
`L := unconditional β`), :149/:194 (section variables `{L}`, `{f a s}` — all
implicit, consistent with PL-2a's `(L := unconditional ℕ)` fallback), :295
(`hasProd_prod_of_ne_finset_one` with `[L.LeAtTop]`), :323 (`[T2Space α]
[L.NeBot]`), :326 (`HasProd.unique`).
`Topology/Algebra/InfiniteSum/SummationFilter.lean` :168, :171, :173 (both
default-filter instances present).
`Analysis/Polynomial/Basic.lean` :32 (`namespace Polynomial`), :34 (explicit
`(P Q : 𝕜[X])`), :161 (`div_tendsto_atTop_zero_of_degree_lt` verbatim).
`Algebra/Polynomial/BigOperators.lean` :45 (`variable (s : Finset ι)` —
explicit, so L3's `natDegree_sum_le_of_forall_le _ _ fun i hi ↦ …` application
pattern is exactly the in-tree use at `:311`), :61, :65.
`Algebra/Polynomial/Degree/Defs.lean` :365, :514, :518.
`Algebra/Polynomial/Eval/Defs.lean` :343 (`eval_finsetSum`), :347 (deprecated
alias, date string `"2026-04-08"` verbatim).
`Algebra/Polynomial/Degree/Operations.lean` :479.
`Algebra/Polynomial/Degree/SmallDegree.lean` :43, :50.
`Algebra/Order/GroupWithZero/Basic.lean` :469-:470 (`@[mono, gcongr, bound]`
confirmed on `pow_le_pow_left₀`).
`Topology/Order/OrderClosed.lean` :130 (`@[to_dual ge_of_tendsto]`), :131,
:469 (`le_of_tendsto_of_tendsto` — PL-1c's fallback name is real).
`Order/Filter/AtTopBot/Defs.lean` :61. `Order/Filter/Tendsto.lean` :105
(`Tendsto.congr'`). `Order/Filter/AtTopBot/Ring.lean` :36 (`tendsto_pow_atTop`,
PL-1b fallback) and in-tree `Tendsto.inv_tendsto_atTop` uses confirmed.
`Analysis/Normed/Group/Basic.lean` :181-:182 (`@[to_additive]` on
`norm_le_norm_add_norm_div'`; additive use precedent
`Analysis/Normed/Algebra/Spectrum.lean:716`), :885-:886, :990-:991.
`Analysis/Normed/Group/Bounded.lean` :71-:72.
`Analysis/Calculus/DiffContOnCl.lean` :42.
`Analysis/Calculus/IteratedDeriv/Defs.lean` :55, :227.
`Analysis/Analytic/CPolynomialDef.lean` :62, :72, :79, :94, :99, :215 (the
collapse + `.unique` precedent pair is exactly as described, and `:215` passes
`(f := …) (s := …)` explicitly — consistent with the implicit binders found at
InfiniteSum/Defs.lean:194).

Repo — `lakefile.toml:2` (`defaultTargets`), `.github/workflows/ci.yml:359`
(no-incomplete-proof scan) and `:420` (`lake build`),
`domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md:388` (`S1-GROWTH` row
text verbatim: "no zeta/xi vertical or order-one growth theorem").
`UPSTREAM_POOL.md` locator-corrections table verified honest against the pool
itself: the pool really does cite `TaylorSeries.lean:139` (pool `:461`), really
does name deprecated `Polynomial.eval_finset_sum` (pool `:472`), and really does
locate the collapse lemma only by its in-tree uses (pool `:462`); all three
contract corrections stand.

### C. Attack fronts, disposition

1. **Formal-multilinear-series vs `Polynomial` bridge — held.** The package
   never touches `FormalMultilinearSeries`: at this pin the entire-Taylor
   lemmas (TaylorSeries.lean:129/:137) are already stated in `iteratedDeriv`
   form, so no coefficient extraction from an FMS (`p.coeff`,
   `changeOrigin`, `partialSum`) is needed anywhere on the L1→L2→L3 path; the
   `Polynomial ℂ` term in L3 is *constructed* explicitly as
   `∑ i ∈ range (n+1), C ((i !)⁻¹ * iteratedDeriv i f 0) * X ^ i`, not
   extracted. Re-verified that no reverse bridge exists at the pin to
   duplicate: `Analysis/Analytic/Polynomial.lean` is forward-only (polynomials
   are analytic — `AnalyticAt.aeval_polynomial` and friends); grep for a
   `∃ p : Polynomial` conclusion over `Analysis/Complex/` and
   `Analysis/Analytic/` returns zero hits; `CPolynomialAt`/`CPolynomialOn`
   never produce a `Polynomial` term. Decision point 5's rejection of the
   `CPolynomialOn` carrier and DEFERRED-PL-1 are accurate as written.
2. **Radius-to-infinity bookkeeping — one real defect (A1), rest held.**
   Squeeze orientation checked: `ge_of_tendsto hlim h : ‖iteratedDeriv k f c‖ ≤ 0`
   with `h : ∀ᶠ R in atTop, ‖iteratedDeriv k f c‖ ≤ bound R` is the correct
   instantiation of the `to_dual` twin at OrderClosed.lean:130-131, and
   `rw [← norm_le_zero_iff]` produces exactly that goal. `Tendsto.congr'`
   orientation checked (`f₁ =ᶠ f₂` with `f₁` the `eval` form: matches the
   `refine h.congr' ?_` use). `eventually_gt_atTop` supplies `0 < R` on the
   filter; `atTop : Filter ℝ` is `NeBot`, discharging `ge_of_tendsto`'s
   instance. The C-slot of the Cauchy estimate unifies with the compound bound
   `C * (1 + ‖c‖ + R) ^ n` because it is a bare implicit `{C : ℝ}`. The one
   defect was the unfireable degree-chain `gcongr` (A1, fixed).
3. **Scope creep — none found.** Five signatures, zero `def`s, no growth-order
   notion, no maximum-modulus input, no `riemannZeta`/`riemannXi`/`LSeries`
   token anywhere in the contract's Lean blocks; `S1-GROWTH` (capability map
   `:388`) is about order-one *exponential* growth of the ζ/ξ layer and is
   correctly left untouched by the claim boundary; the two-stage gate matches
   `MULTIPLICITY_CONTRACT.md`'s, and stage two's Mathlib-CI fork correctly
   re-derives locators rather than trusting this contract. Name-collision scan
   re-run at the pin and over the repo for all five proposed names: zero hits
   each.

### D. What this annex does not do

No statement was added or removed; no Lean file was created; nothing was
elaborated. Under the one invariant, every claim above is source reading
against the pinned tree, and only a stage-two build can turn any of L1–L5 into
a theorem.

---

## Two-stage gate and promotion ordering

Restated for this file, matching `MULTIPLICITY_CONTRACT.md`:

- **Stage one (this document):** independent contract acceptance of the L1–L5
  statement surface. Produces no built module, no ledger row, no registry or
  axiom-audit entry, and no kernel verdict. An acceptance PR must not carry a
  Lean draft into any built target.
- **Stage two (separate, unscheduled, unauthorized by this document):** a built
  change carrying the module and its verdicts. For this package stage two has a
  fork the multiplicity package did not have: the natural stage-two venue is an
  **upstream Mathlib PR** (per `UPSTREAM_POOL.md` §4 "Proposed home"), in which
  case the kernel verdict is delivered by Mathlib CI at whatever revision that
  PR targets — and the `file:line` locators of this contract, which are pinned
  to `fabf563a…`, must be re-derived against that revision as part of the PR,
  not trusted. If instead it is ever drafted in-repo, it goes to the drafts
  lane (`drafts/PolyLiouville.lean`), which current CI does not elaborate
  (header, above), and a green acceptance-PR run remains evidence of nothing.
- No Routine, target registration, or `targets/*.json` movement follows from
  stage one. Nothing in this file is a promotion.
