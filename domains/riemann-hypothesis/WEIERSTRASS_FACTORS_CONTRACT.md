# Weierstrass elementary factors / canonical product contract: draft v1.2

Status: **DRAFT v1.2 (2026-08-07; v1 and v1.1 same day — v1.1 corrected in place per the
red-team re-verification recorded in Annex B; v1.2 folds in the two drafting
passes recorded in Annex C, which retire the missing-lemma half of the
registered product-lemma obligation by a whole-tree absence check, and reduce
the computation half to a located assembly sketch (UNVERIFIED — no kernel);
S1W-ORD is re-priced as an estimate, not a finding) — non-built review artifact, offered for STAGE ONE
(INDEPENDENT CONTRACT ACCEPTANCE) ONLY. NOT Lean-checked.** No declaration below
has been elaborated; no `lake build` has been run against any of it. Under the one
invariant, the Lean kernel via CI is the sole judge of every statement in this
contract, and this document carries no kernel verdict of any kind.

**Two-stage gate (same regime as `MULTIPLICITY_CONTRACT.md`).** Stage one is
*independent contract acceptance*: a review of the statement surface W1–W12 only.
It produces **no built module, no ledger row, no registry or axiom-audit entry,
and no kernel verdict**. Stage two would be a separate built promotion PR whose
verdict is delivered by CI. Current CI does not elaborate anything in the drafts
lane: `lakefile.toml:2` declares `defaultTargets = ["Ecdlp", "ResearchOS"]`, the
build step at `.github/workflows/ci.yml:420` runs `lake build` over those
targets, and the no-incomplete-proof scan at `:359` covers only `Ecdlp.lean
Ecdlp/ ResearchOS/ ResearchOS.lean`. **No green CI run on an acceptance PR is
evidence of anything about this draft.**

**Lane authority.** The RH queue (`tasks/RIEMANN_HYPOTHESIS.md`, decision update
2026-08-07 at `:14`) — not `repo/ECDLP_DECISION_SUBSTRATE.json`, which governs
the ECDLP lane — is the authority for this lane. This document is an **offered
artifact**, not an active task, not a queue slot, and not authorization to work
a route. It closes **no barrier**, selects **no route**, and makes **no claim
about the truth of the Riemann Hypothesis**.

**Editorial-fix pass (2026-08-08, `RH-015`).** This document has been updated in
place against the stage-one acceptance record
`notes/reviews/WEIERSTRASS_ACCEPTANCE_2026_08_08.md` (three lenses,
ACCEPT_WITH_EDITORIAL_FIXES, zero blocking findings, no lens asking for a
signature change). **No public signature changed**: every edit lands in prose,
comments, proof skeletons, locators, obligation text, the risk register, the
claim boundary, or the annexes. Every locator written or corrected in that pass
was re-opened at the pin and its signature re-read; findings that did not
survive re-reading were withdrawn rather than applied, and the two fixes that
would have required a signature change (a binder rename in
`analyticOrderAt_finsetProd`, and the addition of a 29th `_fun_`-form signature)
were **not** applied — they are recorded below as returning the surface to
contract review. The statement surface accepted on 2026-08-08 is the statement
surface as it stands here.

Working name: `WeierstrassFactors.lean` (drafts lane). Destination shelf at
stage two is `ResearchOS/Analysis/` with a new `analysis-generic` ledger prefix
registered in `scripts/gen_researchos_registry.py` `PREFIX_DOMAINS` (:46–:54)
and `DOMAIN_SUBTREES` (:60–:63) — **NOT**
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/` and **NOT** an `RH-`
prefix, per `VERIFIED_RESEARCHOS.md:20-25` ("`MB-`, `HK-`, `PL-`, `TC-` and
`GO-` → `analysis-generic` … rows must cite files under `ResearchOS/Analysis/`,
and nothing on that shelf is owned by, or counts toward, any conjecture
program") and the `ResearchOS/Analysis/ThreeCircles.lean:37-42` precedent
("Module placement: `ResearchOS/Analysis/`, deliberately NOT
`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/`"). The exact module
basename remains a stage-two decision; the shelf does not.
Statement surface: **W1 – W12**, comprising **exactly 28
public signatures** (2 `def`s + 26 lemmas/theorems), every one spelled explicitly
in a `lean` statement block in §2. The W-numbers are section labels, not a
declaration count: several sections carry more than one signature. No signature
of this package is mandated in prose only.

Scope: the generic Weierstrass elementary-factor layer identified by
`UPSTREAM_POOL.md` §2 (scout B): the elementary factor `E_p`, its nonvanishing
off `1`, consumption of the pinned log bound, locally uniform convergence of the
canonical product over a summable-power zero family at **fixed finite genus
`p`**, analyticity of the limit, and — the point of this contract — the **zero
set and local analytic order of the product**, stated on **all of ℂ**, with no
domain restriction. It contains **no** zeta or xi symbol, **no** zero
enumeration, **no** counting function, **no** growth theorem (`S1-GROWTH` is
untouched), **no** genus-selection/Hadamard existence theorem, and **no** claim
of progress on RH.

Pinned Mathlib: `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0), verified
this session via `git -C /workspace/leanprover-community/mathlib4 rev-parse
HEAD`. Every `file:line` locator below is from that exact tree (paths relative
to the `Mathlib/` root of the pin) unless prefixed `repo:`. Every locator was
re-verified against the tree during drafting; §0 quotes the load-bearing
interface verbatim. Three of the pool's §2 locators were **corrected** during
re-verification; see §1.4 and Annex A.

Repo prerequisites: **none.** No statement below consumes any repo-local
theorem. This is deliberate: the package is generic and must remain promotable
(in principle) as Mathlib-upstream material without dragging repo symbols.

## Candidate fields

- **Mechanism.** `weierstrassFactor p z := (1 - z) * exp (∑ k ∈ Finset.range p,
  z ^ (k+1) / (k+1))` is the only genuinely new definition; the second `def`
  (`weierstrassProduct`) is a `tprod` of factors. The estimate layer is
  **consumption, not creation**: the classically hard bound is already pinned as
  `Complex.norm_log_one_sub_inv_add_logTaylor_neg_le` (LogBounds.lean:231), and
  W5–W6 repackage it through `Complex.log_inv` (Log.lean:137) and
  `Complex.norm_exp_sub_one_le` (Exponential.lean:439). Convergence runs through
  the pinned criterion `Summable.hasProdUniformlyOn_one_add`
  (MultipliableUniformlyOn.lean:87) compact-by-compact via
  `hasProdLocallyUniformlyOn_of_forall_compact` (UniformOn.lean:196).
  Analyticity of the limit is pinned: `TendstoLocallyUniformlyOn.differentiableOn`
  (LocallyUniformLimit.lean:135) applies **by defeq** to
  `HasProdLocallyUniformlyOn` (UniformOn.lean:152), with the in-tree precedent
  `DedekindEta.lean:91` using exactly this dot-notation unfolding. The zero-set
  and order layer runs through the **pointwise** complement split
  `Multipliable.tprod_mul_tprod_compl` (InfiniteSum/Basic.lean:752) — *not*
  through the pool's conjectured `HasProdLocallyUniformlyOn.mul_compl`; §1.4
  re-derives what is actually needed — plus `analyticOrderAt_mul`
  (Order.lean:497) and one small new generic lemma
  (`analyticOrderAt_finsetProd`, W12).
- **Expected information gain.** A generic, reusable elementary-factor layer
  that states the zero set and local order of a canonical product on all of ℂ —
  precisely the statement shape the in-tree Euler sine product development
  (Cotangent.lean:132) routes around by restricting to `ℂ_ℤ` (§1.3). Lowers the
  future cost of any canonical-product argument. No information about the truth
  of RH is produced, and no barrier row changes.
- **Claim boundary.** Every statement W1–W12 is over generic data
  (`p : ℕ`, `a : ι → ℂ` with `ι` an arbitrary type). Nothing consumes or
  mentions `riemannZeta`, `riemannXi`, any zero enumeration, any counting
  function, or any growth bound. Generic pinned-Mathlib machinery lowers the
  cost of a barrier exit but **never retires a row**
  (`MULTIPLICITY_CONTRACT.md` finding A4 regime); in particular
  `S1-GLOBAL-ZEROS` (whose blocked-need column names "canonical product") and
  `S1-GROWTH` (`MATHLIB_CAPABILITY_MAP.md:387-388`) remain exactly as open
  after this package as before it.
- **Death condition (stop rule).** Stop or split if a proof would need a new
  axiom, an unproved conjecture, any zeta/xi input, a growth or counting bound,
  a genus-selection (Hadamard/diagonal) argument, or a domain restriction on
  the zero-set/order statements (the Cotangent dodge). Full list in §Death
  conditions. A clean blocker is preferable to a dodged statement.

Proposed module preamble (name-resolution review only):

```lean
import Mathlib.Analysis.SpecialFunctions.Complex.LogBounds   -- logTaylor, the :231 bound
import Mathlib.Analysis.Complex.Exponential                  -- norm_exp_sub_one_le, exp_ne_zero
import Mathlib.Analysis.SpecialFunctions.Complex.Log         -- log_inv, exp_log
import Mathlib.Analysis.SpecialFunctions.Log.Summable        -- multipliable_one_add_of_summable, tprod_one_add_ne_zero_of_summable
import Mathlib.Analysis.Normed.Module.MultipliableUniformlyOn -- Summable.hasProdUniformlyOn_one_add
import Mathlib.Topology.Algebra.InfiniteSum.UniformOn        -- HasProdLocallyUniformlyOn
import Mathlib.Analysis.Complex.LocallyUniformLimit          -- TendstoLocallyUniformlyOn.differentiableOn
import Mathlib.Analysis.Analytic.Order                       -- analyticOrderAt, _mul, _comp_of_deriv_ne_zero
import Mathlib.Analysis.Complex.CauchyIntegral               -- analyticOnNhd_univ_iff_differentiable

open Complex Filter Function Set
open scoped Topology
```

Name-collision scan (grep over the pinned tree this session): **zero hits** for
`weierstrassFactor`, `weierstrassProduct`, `norm_log_one_sub_add_sum_le`,
`analyticOrderAt_finsetProd`, `logTaylor_neg_eq`, `finite_setOf_apply_eq`,
`eventually_cofinite_le_norm`, `analyticAt_tprod_compl`,
`summable_norm_weierstrassFactor_sub_one`. All nine re-run at the pin during the
2026-08-08 editorial pass: still zero hits each.

The only case-insensitive **`weierstrassFactor`** hits at the pin are
`PowerSeries.IsWeierstrassFactorization*` in
`RingTheory/PowerSeries/WeierstrassPreparation.lean` — unrelated commutative
algebra (Weierstrass *preparation*, not elementary factors). Note the search
string: it is `weierstrassFactor`, **not** the bare `weierstrass`. Bare
case-insensitive `weierstrass` matches 42 files under `Mathlib/` at the pin
(45 across the whole pinned tree, which also holds `Archive/`,
`Counterexamples/` and `MathlibTest/`). Among them: `WeierstrassCurve` occurs
**371 times on 349 lines across 19 files** under `AlgebraicGeometry/EllipticCurve`,
plus four more occurrences in `NumberTheory/Height/EllipticCurve.lean`;
`Topology/ContinuousMap/StoneWeierstrass.lean` and
`Topology/ContinuousMap/Weierstrass.lean` both exist;
`Analysis/SpecialFunctions/Elliptic/Weierstrass.lean` exists and references
`analyticOrderAt` at :1021; and `Analysis/Complex/LocallyUniformLimit.lean` — a
file this contract depends on — carries a `section Weierstrass` at :111–:164.
The narrower scan deliberately excludes all of these as unrelated; the nine
declared names are the claim, and they are clean — re-run at the pin
**and at current Mathlib master on 2026-08-09**, zero hits both times. The
master-side run, together with a module-level and file-level duplication check,
is recorded in `UPSTREAM_DUPLICATION_CHECK_2026_08_09.md`; note in particular
that it establishes what has LANDED upstream and explicitly does **not** cover
the in-flight PR queue, which is unreachable from the session that ran it.

*Count corrected 2026-08-09.* This paragraph previously said "353 times across
`AlgebraicGeometry/EllipticCurve`". That figure is not producible for that
directory under any counting method; 353 is the whole-`Mathlib/` matching-LINE
count, so both the unit and the scope were wrong. Recorded rather than silently
fixed because the wrong number entered the contract inside a review finding's
own *recommended fix text* — a correction can carry an error as easily as the
thing it corrects.

---

## 0. Exact pinned interface (quoted from the tree at the pin)

```lean
-- Analysis/SpecialFunctions/Complex/LogBounds.lean. namespace Complex spans :32–:290,
-- so all three are Complex.*. logTaylor is `noncomputable def` (the pool's §0 row said
-- plain def — CORRECTED; the `noncomputable` modifier sits on the preceding line :67).
def logTaylor (n : ℕ) : ℂ → ℂ := fun z ↦ ∑ j ∈ Finset.range n, (-1) ^ (j + 1) * z ^ j / j
                                                                                      -- :68
lemma norm_log_sub_logTaylor_le (n : ℕ) {z : ℂ} (hz : ‖z‖ < 1) :
    ‖log (1 + z) - logTaylor (n + 1) z‖ ≤ ‖z‖ ^ (n + 1) * (1 - ‖z‖)⁻¹ / (n + 1)     -- :142

-- :231 — THE log bound this contract consumes. Already a theorem at the pin.
lemma norm_log_one_sub_inv_add_logTaylor_neg_le (n : ℕ) {z : ℂ} (hz : ‖z‖ < 1) :
    ‖log (1 - z)⁻¹ + logTaylor (n + 1) (-z)‖ ≤ ‖z‖ ^ (n + 1) * (1 - ‖z‖)⁻¹ / (n + 1)

-- Analysis/SpecialFunctions/Complex/Log.lean:137, :41 (namespace Complex)
theorem log_inv (x : ℂ) (hx : x.arg ≠ π) : log x⁻¹ = -log x
theorem exp_log {x : ℂ} (hx : x ≠ 0) : exp (log x) = x

-- Analysis/Complex/Basic.lean:689; Analysis/SpecialFunctions/Complex/Arg.lean:544
lemma mem_slitPlane_of_norm_lt_one {z : ℂ} (hz : ‖z‖ < 1) : 1 + z ∈ slitPlane
lemma slitPlane_arg_ne_pi {z : ℂ} (hz : z ∈ slitPlane) : z.arg ≠ Real.pi

-- Analysis/Complex/Exponential.lean:439 (inside namespace Complex, :347–:509), :160
theorem norm_exp_sub_one_le {x : ℂ} (hx : ‖x‖ ≤ 1) : ‖exp x - 1‖ ≤ 2 * ‖x‖
theorem exp_ne_zero : exp x ≠ 0

-- Analysis/SpecialFunctions/ExpDeriv.lean:97 (namespace Complex, `@[simp]`; 𝕜 over ℂ)
theorem differentiable_exp : Differentiable 𝕜 exp

-- Topology/Algebra/InfiniteSum/UniformOn.lean:44, :152, :159, :196, :256.
-- Section variables (:30): {α β ι : Type*} [CommMonoid α] {f : ι → β → α} {g : β → α}
-- {s : Set β} [UniformSpace α]; the locally-uniform block adds [TopologicalSpace β].
def HasProdUniformlyOn : Prop := HasProd (UniformOnFun.ofFun {s} ∘ f) (UniformOnFun.ofFun {s} g)
def HasProdLocallyUniformlyOn : Prop := TendstoLocallyUniformlyOn (∏ i ∈ ·, f i ·) g atTop s
def MultipliableLocallyUniformlyOn : Prop := ∃ g, HasProdLocallyUniformlyOn f g s
lemma hasProdLocallyUniformlyOn_of_forall_compact (hs : IsOpen s) [LocallyCompactSpace β]
    (h : ∀ K ⊆ s, IsCompact K → HasProdUniformlyOn f g K) : HasProdLocallyUniformlyOn f g s
theorem HasProdLocallyUniformlyOn.tprod_eqOn [T2Space α]
    (h : HasProdLocallyUniformlyOn f g s) : Set.EqOn (∏' i, f i ·) g s

-- Analysis/Normed/Module/MultipliableUniformlyOn.lean. namespace Summable spans :80–:157,
-- so both are Summable.*. Variables (:24, :82, :126): {u : ι → ℝ} {K : Set α},
-- [NormedCommRing R] [NormOneClass R] [CompleteSpace R] [TopologicalSpace α] {f : ι → α → R};
-- :130 additionally requires [LocallyCompactSpace α]. ℂ satisfies all of these.
lemma hasProdUniformlyOn_one_add (hK : IsCompact K) (hu : Summable u)
    (h : ∀ᶠ i in cofinite, ∀ x ∈ K, ‖f i x‖ ≤ u i) (hcts : ∀ i, ContinuousOn (f i) K) :
    HasProdUniformlyOn (fun i x ↦ 1 + f i x) (fun x ↦ ∏' i, (1 + f i x)) K        -- :87
lemma hasProdLocallyUniformlyOn_one_add (hK : IsOpen K) (hu : Summable u)
    (h : ∀ᶠ i in cofinite, ∀ x ∈ K, ‖f i x‖ ≤ u i) (hcts : ∀ i, ContinuousOn (f i) K) :
    HasProdLocallyUniformlyOn (fun i x ↦ 1 + f i x) (fun x ↦ ∏' i, (1 + f i x)) K -- :130

-- Analysis/Complex/LocallyUniformLimit.lean:135. Declared `_root_.`; φ is any [NeBot]
-- filter — for HasProdLocallyUniformlyOn, φ = (atTop : Filter (Finset ι)), which is
-- NeBot unconditionally (Order/Filter/AtTopBot/Basic.lean:66, Finset ι is a nonempty
-- SemilatticeSup). hF is a condition on the FINITE PARTIAL PRODUCTS.
theorem _root_.TendstoLocallyUniformlyOn.differentiableOn [φ.NeBot]
    (hf : TendstoLocallyUniformlyOn F f φ U) (hF : ∀ᶠ n in φ, DifferentiableOn ℂ (F n) U)
    (hU : IsOpen U) : DifferentiableOn ℂ f U

-- In-tree precedent that dot notation resolves THROUGH the def (generalized field
-- notation unfolds HasProdLocallyUniformlyOn to TendstoLocallyUniformlyOn):
-- NumberTheory/ModularForms/DedekindEta.lean:88–:93 (docstring :88, `lemma
-- differentiableOn_tprod_one_sub_pow` :89, chain :91, continuation :92–:93;
-- :94 is blank and :95 opens the NEXT lemma's docstring — range corrected
-- 2026-08-08) —
--   multipliableLocallyUniformlyOn_one_sub_pow.hasProdLocallyUniformlyOn.differentiableOn
--     (.of_forall fun _ ↦ by simpa [Finset.prod_fn] using
--       DifferentiableOn.finsetProd (fun _ _ ↦ by fun_prop)) Metric.isOpen_ball

-- Analysis/SpecialFunctions/Log/Summable.lean. namespace Complex spans :25–:53,
-- namespace Real :55–:100; the NormedRing section (:119–:224) is at ROOT, with
-- variables (:132) {R : Type*} [NormedCommRing R] [NormOneClass R] {f : ι → R}.
lemma multipliable_one_add_of_summable [CompleteSpace R]
    (hf : Summable fun i ↦ ‖f i‖) : Multipliable fun i ↦ (1 + f i)                -- :169
lemma tprod_one_add_ne_zero_of_summable [CompleteSpace R] [NormMulClass R]
    (hf : ∀ i, 1 + f i ≠ 0) (hu : Summable (‖f ·‖)) : ∏' i : ι, (1 + f i) ≠ 0     -- :216

-- Topology/Algebra/InfiniteSum/Basic.lean:379, :752 (both @[to_additive]).
-- NOTE the SummationFilter framework at the pin: ∏' is notation for the
-- `unconditional` filter (Defs.lean:158); tprod_fintype (:481) needs [L.LeAtTop],
-- satisfied by `unconditional`.
-- NOTE (Annex C item 1, extended 2026-08-08): tprod_mul_tprod_compl (:752) sits
-- under TWO omitted section variables, not one — `variable [T2Space α]` at
-- Basic.lean:696, AND `variable [ContinuousMul α]` at :713 inside
-- `section ContinuousMul` (:711 open, :769 close); the enclosing `section tprod`
-- (:432) supplies [CommMonoid α] [TopologicalSpace α] at :434. So the real
-- ambient instance set for :752 is
--   [CommMonoid α] [TopologicalSpace α] [T2Space α] [ContinuousMul α].
-- All discharged for α = ℂ by instance; no statement impact. mul_compl (:379)
-- is via HasProd.mul_isCompl (:373) and needs no T2 — but it is NOT
-- hypothesis-free either: it sits inside `section HasProd` (:36–:430) under
-- `variable [ContinuousMul α]` (declared :319). "Needs no T2" is right;
-- "needs nothing" would not be.
theorem HasProd.mul_compl {s : Set β} (ha : HasProd (f ∘ (↑) : s → α) a)
    (hb : HasProd (f ∘ (↑) : (sᶜ : Set β) → α) b) : HasProd f (a * b)
protected theorem Multipliable.tprod_mul_tprod_compl {s : Set β}
    (hs : Multipliable (f ∘ (↑) : s → α)) (hsc : Multipliable (f ∘ (↑) : ↑sᶜ → α)) :
    (∏' x : s, f x) * ∏' x : ↑sᶜ, f x = ∏' x, f x
theorem tprod_fintype [L.LeAtTop] [Fintype β] (f : β → α) : ∏'[L] b, f b = ∏ b, f b -- :481

-- Topology/Algebra/InfiniteSum/Group.lean:300, :365 (both @[to_additive]; the
-- multiplicative forms need [CommGroup α], which ℂ-under-× is NOT — this contract
-- uses ONLY the additive twins Summable.subtype / Summable.tendsto_cofinite_zero,
-- on ℝ-valued norm families, where [AddCommGroup ℝ] holds. See obligation S1W-SUB.)
theorem Multipliable.subtype (hf : Multipliable f) (p : β → Prop) :
    Multipliable (f ∘ (↑) : Subtype p → α)
theorem Multipliable.tendsto_cofinite_one (hf : Multipliable f) : Tendsto f cofinite (𝓝 1)

-- Analysis/Analytic/Order.lean:47 (def), :133/:137, :175, :188, :328, :497, :561.
-- :488 section variables for the mul block: {f g : 𝕜 → 𝕜} — both factors FIELD-valued.
-- QUOTED WITH ITS BODY (the v1.2 quote gave only the header — corrected
-- 2026-08-08). The junk branch is load-bearing for how §1.5 may be read: the
-- file's own docstring at :46 says "If `f` isn't analytic at `z₀`, then
-- `analyticOrderAt f z₀` returns a junk value of `0`." The non-analytic junk
-- value is 0, NOT ⊤.
noncomputable def analyticOrderAt (f : 𝕜 → E) (z₀ : 𝕜) : ℕ∞ :=          -- :47–:51
  if hf : AnalyticAt 𝕜 f z₀ then
    if h : ∀ᶠ z in 𝓝 z₀, f z = 0 then ⊤
    else ↑(hf.exists_eventuallyEq_pow_smul_nonzero_iff.mpr h).choose
  else 0
protected lemma AnalyticAt.analyticOrderAt_eq_zero (hf : AnalyticAt 𝕜 f z₀) :
    analyticOrderAt f z₀ = 0 ↔ f z₀ ≠ 0                                           -- :133
protected lemma AnalyticAt.analyticOrderAt_ne_zero (hf : AnalyticAt 𝕜 f z₀) :
    analyticOrderAt f z₀ ≠ 0 ↔ f z₀ = 0                                           -- :137
lemma analyticOrderAt_congr (hfg : f =ᶠ[𝓝 z₀] g) :
    analyticOrderAt f z₀ = analyticOrderAt g z₀                                    -- :175
theorem AnalyticAt.analyticOrderAt_eq_one_of_zero_deriv_ne_zero {x : 𝕜}
    (hf : AnalyticAt 𝕜 f x) (hfx : f x = 0) (hf' : deriv f x ≠ 0) :
    analyticOrderAt f x = 1                                                        -- :328
theorem analyticOrderAt_mul (hf : AnalyticAt 𝕜 f z₀) (hg : AnalyticAt 𝕜 g z₀) :
    analyticOrderAt (f * g) z₀ = analyticOrderAt f z₀ + analyticOrderAt g z₀       -- :497
lemma analyticOrderAt_comp_of_deriv_ne_zero (hg : AnalyticAt 𝕜 g z₀) (hg' : deriv g z₀ ≠ 0)
    [CompleteSpace 𝕜] [CharZero 𝕜] :
    analyticOrderAt (f ∘ g) z₀ = analyticOrderAt f (g z₀)                          -- :561

-- Analysis/Calculus/Deriv/Add.lean:449; Analysis/Calculus/Deriv/Mul.lean:593, :530
theorem deriv_const_sub_id (c : 𝕜) : deriv (c - ·) x = -1
theorem deriv_div_const (d : 𝕜') : deriv (fun x => c x / d) x = deriv c x / d
theorem DifferentiableOn.finsetProd (hd : ∀ i ∈ u, DifferentiableOn 𝕜 (f i) s) : …

-- Analysis/Complex/CauchyIntegral.lean:678 (namespace Complex, so
-- Complex.analyticOnNhd_univ_iff_differentiable at root)
theorem analyticOnNhd_univ_iff_differentiable {f : ℂ → E} :
    AnalyticOnNhd ℂ f univ ↔ Differentiable ℂ f

-- Algebra/BigOperators/Pi.lean:51
theorem Finset.prod_fn (s : Finset ι) (g : ι → ∀ a, M a) : ∏ i ∈ s, g i = fun a ↦ ∏ i ∈ s, g i a
```

---

## 1. Design decisions

### 1.1 This package introduces definitions — deliberately

`MULTIPLICITY_CONTRACT.md` prides itself on zero `def`s; this contract is the
opposite regime and says so up front. `UPSTREAM_POOL.md` §0 rows 2–3 confirm the
pin has **no** elementary factor and **no** canonical product (`rg -i
"elementaryFactor|weierstrassFactor"`, `rg -i "canonicalProduct"`: zero relevant
hits). The blocker identified by scout B is precisely the *definitional and
bookkeeping* layer, not the estimate. So the package contributes exactly two
`noncomputable def`s (`weierstrassFactor`, `weierstrassProduct`) and nothing
else definitional: no genus function, no exponent of convergence, no `Entire`
predicate, no divisor pullback.

### 1.2 Fixed finite genus, generic index type, no enumeration

All product statements are over `{ι : Type*} {p : ℕ} {a : ι → ℂ}` with exactly
three hypotheses, named once and reused verbatim:

```lean
variable {ι : Type*} {p : ℕ} {a : ι → ℂ}
-- (hane : ∀ i, a i ≠ 0)
-- (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1))
```

- **`ι` is an arbitrary type.** No `[Countable ι]`, no `[Encodable ι]`, no
  `ℕ`-indexing. None of the pinned dependencies needs one (`Summable` over an
  arbitrary index forces countable support internally; `tprod` is
  filter-based). The statements are about a generic family `a`, full stop.

  **Countability is nevertheless a consequence, not an assumption** (correction
  applied 2026-08-08; the earlier text claimed the package "cannot even express
  an enumeration", which is stronger than the mathematics supports). Under
  `hane`, `‖a i‖ > 0` for **every** `i`, so `‖a i‖⁻¹ ^ (p+1) > 0` for every `i`
  and the `hsum` family has full support; a summable ℝ-valued family with full
  strictly-positive support has countable index type (additive twin of
  `Multipliable.countable_mulSupport`, `Topology/Algebra/InfiniteSum/Group.lean:388`,
  `@[to_additive]` on :387, hypotheses `[FirstCountableTopology G] [T1Space G]`
  — both instances for ℝ). So on every non-vacuous instance of the hypothesis
  pair, `ι` is countable and an injection `ι → ℕ` exists. Nothing in the
  statement surface becomes false and no signature is affected; what must be
  dropped is only the rhetoric. The accurate boundary claim is the one already
  in claim boundary 2 — **no statement introduces, requires, or produces an
  enumeration, ordering, or counting of anything** — and that remains exactly
  true: derived countability is not an enumeration, and no proof or statement
  here constructs one. Note also that `Countable` is a `Prop` whose field is an
  existence claim (`Data/Countable/Defs.lean:40`); extracting an actual
  injection needs `Classical.choice`, so "an injection exists" and "the package
  can express an enumeration" are different statements and only the first is
  derivable here.

  **Sharper, and this is the form to carry (2026-08-09).** The consequence is
  not merely that `ι` is countable — it is that over an **uncountable** index
  the hypothesis pair `hane ∧ hsum` is **contradictory**. Every one of the
  twelve signatures carrying both is therefore **vacuously true** over every
  uncountable `ι`, and the advertised "`ι` is an arbitrary type" generality is
  apparent rather than real on those instances. Two consequences for stage two:
  a prover may legitimately discharge any of W7–W12 over an uncountable index
  by deriving `False`, which type-checks and is worthless; and the honest
  description of the generality is "arbitrary index, non-vacuous only when
  countable", not "arbitrary index".

  Countability also follows from the package's own W7, two lines after it and
  without the external lemma: `eventually_cofinite_le_norm hane hsum n` makes
  `{i | ‖a i‖ < n}` finite for each `n : ℕ`, and `ι` is the countable union of
  those over `n` by Archimedes. Anyone who has W7 has `Countable ι`.
- **Genus is a fixed parameter `p`,** with the summable-power hypothesis
  `hsum`. The pool's W5 (genus chosen on the diagonal, hypothesis-free
  existence theorem — the Weierstrass product *theorem*) is **excluded**: it is
  a different, harder statement (geometric-majorant bookkeeping per radius) and
  nothing in this contract needs it. Recorded as **DEFERRED-W1**.
- `hsum` implies the escape-to-infinity property (W7); it is not assumed
  separately. `hane` is honest: `weierstrassFactor p (z / a i)` at `a i = 0`
  would be the junk value `E_p(z/0) = E_p(0) = 1` — the statements would
  *elaborate* without `hane` but would silently ignore vanishing entries, so
  `hane` is kept on every product statement. (Death condition 6.)

- **Where `hane` is load-bearing, exactly** (map added 2026-08-08; leaving this
  unstated risked a stage-two prover "strengthening" W8–W10 by dropping a
  hypothesis it believed decorative, which is precisely the junk-powered
  generality death condition 6 forbids):

  - **ESSENTIAL in W7 (both signatures), W11, and ONE of W12's five signatures.**
    Without `hane` these are outright FALSE, not merely unprovable. **Three
    different witnesses are needed — corrected 2026-08-09, the single bundled
    witness below does not break all three.** In every case take `w = z = 0`,
    where `0 / a i = 0` for *every* `i` (`zero_div`), so all factors collapse to
    `weierstrassFactor p 0 = 1` and `weierstrassProduct p a 0 = ∏' i, 1 = 1 ≠ 0`.

    - **W11** — a **single** zero suffices. `ι = PUnit`, `a ≡ 0`: `hsum` is
      `Summable (fun _ ↦ 0)` and holds; `∃ i, a i = 0` is true while the product
      is `1 ≠ 0`, so the iff is `False ↔ True`.
    - **W12's fourth signature** (`analyticOrderAt_weierstrassProduct`) — needs
      a **finite nonempty** zero fiber. With `ι = PUnit`, `a ≡ 0`: the product
      is the constant `1`, order `0`, while `Nat.card {i | a i = 0} = 1`. The
      earlier text's "`Nat.card {i | a i = 0} ≥ 1`" does not follow from
      `a i₀ = 0`: if the fiber is **infinite**, `Nat.card_eq_zero_of_infinite`
      (`SetTheory/Cardinal/Finite.lean:68`) makes the count `0`, which
      *coincides* with the true order and the statement holds. An infinite-fiber
      witness refutes W11 but not the capstone.
    - **W7 (both signatures)** — needs an **infinite** zero fiber, and the
      single-zero witness does NOT break it. `‖a i‖⁻¹ ^ (p+1) = 0` whenever
      `a i = 0` (`inv_zero`, then `zero_pow` with `p+1 ≠ 0`), so `{i | a i = 0}`
      may be infinite with `hsum` still holding. Take `ι = ℕ`, `a ≡ 0`: then
      `eventually_cofinite_le_norm` fails for any `R > 0` and
      `finite_setOf_apply_eq` fails at `w = 0`. With a merely *finite* zero
      fiber both W7 signatures remain true.

    Scope note: `hane` is essential in exactly one of W12's five signatures.
    Signatures 1–3 do not mention the family `a` at all, and signature 5
    (`analyticOrderAt_weierstrassProduct_ne_top`) is **true without `hane`** —
    the surviving subfamily's product is entire and not identically zero, and if
    analyticity failed, `analyticOrderAt`'s junk value is `0 ≠ ⊤` anyway
    (`Analysis/Analytic/Order.lean:47-52`).
  - **PROVABLY REDUNDANT in W8, W9 and W10 (all seven signatures there), and
    retained only for statement uniformity across the block.** When `a i = 0`
    the factor is the constant `weierstrassFactor p 0 = 1`, the tail term
    `‖weierstrassFactor p (z / a i) - 1‖` is `0`, and the majorant term
    `‖a i‖⁻¹ ^ (p+1)` is `0` too, so those indices are inert on both sides of
    every bound; the surviving subfamily satisfies `hane` by construction and
    `hsum` by restriction. W10's third signature needs nothing extra: its own
    hypothesis `∀ i, a i ≠ w` already supplies `hane` at the only point where
    it would bite (`w = 0`).
  - **"Redundant" is a claim about statement TRUTH only — the proof route does
    not survive the deletion** (added 2026-08-09; the word "provably" in the
    2026-08-08 text invited the opposite reading). W8's own skeleton, step 3,
    consumes `eventually_cofinite_le_norm hane hsum (2*R+1)` — that is W7, which
    the bullet above declares FALSE without `hane`. So a prover who deletes
    `hane` from W8 on the strength of the redundancy claim gets a true statement
    whose supplied proof no longer type-checks.

    A repaired route exists and was checked against the pinned interface: for
    `i` in the zero fiber both sides of the bound are `0` with no appeal to W6
    at all; the exception set is `{i ∉ fiber : ‖a i‖ < 2R+1}`, finite by W7
    applied to the surviving subfamily through `Summable.subtype`
    (`Topology/Algebra/InfiniteSum/Group.lean:300`); and the consuming lemma
    `Summable.hasProdUniformlyOn_one_add`
    (`Normed/Module/MultipliableUniformlyOn.lean:87`) imposes no nonvanishing
    side condition, its `cofinite`-eventual hypothesis absorbing the finite
    exception set directly. That is a real subtype-restriction argument, not a
    hypothesis deletion. This **strengthens** death condition 6 rather than
    weakening it.

  - **The same junk convention does opposite work in the two halves of this
    map.** `z / 0 = 0` together with `E_p 0 = 1` is exactly what makes `hane`
    deletable in W8–W10 (vanishing indices go inert on both sides) and exactly
    what makes W7, W11 and W12's fourth signature false without it (the product
    is manufactured nonzero at a point the statement asserts is a zero). One
    observation, two opposite consequences.

  - **Consequence for stage two:** dropping `hane` from W8–W10 is a permitted
    *mathematical* observation and a **forbidden edit** — see death condition 6,
    which is a policy about W8–W10 specifically, not a vague prohibition.

### 1.3 The Cotangent dodge — and why this contract must not repeat it

The in-tree template for everything through analyticity is the Euler sine
product (`Analysis/SpecialFunctions/Trigonometric/Cotangent.lean`, re-verified
this session): `sineTerm` (:78), `multipliable_sineTerm` (:94),
`euler_sineTerm_tprod` (:99), the compact-majorant argument
`sineTerm_bound_aux` (:105, **`private` at the pin — pattern only, not
importable**; re-read 2026-08-08: `private lemma sineTerm_bound_aux (hZ :
IsCompact Z) : ∃ u : ℕ → ℝ, Summable u ∧ ∀ j z, z ∈ Z → ‖sineTerm z j‖ ≤ u j`),
`multipliableUniformlyOn_euler_sin_prod_on_compact`
(:118), and `HasProdLocallyUniformlyOn_euler_sin_prod` (:132). Note what that
development does at every step that would touch a zero of `sin`: it restricts
to `ℂ_ℤ`, the complement of the integers (`sineTerm_ne_zero` at :80 takes
`hx : x ∈ ℂ_ℤ`; the `HasProdUniformlyOn` statement at :125 takes `hZ2 : Z ⊆
ℂ_ℤ`; the locally-uniform statement at :132 is on `ℂ_ℤ`). The
Weierstrass-shaped content — *the product is entire and its zero set and local
orders are exactly those of the factor family* — is exactly what is dodged.

**`ℂ_ℤ` CANNOT BE WRITTEN outside the two files that define it** (found
2026-08-09; no lens caught it). It is `local notation`, not scoped notation:
`Cotangent.lean:34` and `Analysis/Complex/IntegerCompl.lean:27` each declare
`local notation "ℂ_ℤ" => integerComplement`, and `local` means the notation dies
at the end of its own file. `open scoped Complex` does not bring it in and
nothing else will. Every appearance of `ℂ_ℤ` in this contract — here, in the
W8 dependency list, and in Annex B — is a QUOTATION of pinned source, never
text to type. Anything this package needs to say about that set must be written
with the underlying definition, `Complex.integerComplement`
(`Analysis/Complex/IntegerCompl.lean:23`,
`def Complex.integerComplement := (Set.range ((↑) : ℤ → ℂ))ᶜ`).

This is the same failure class as the `private` marker two paragraphs up — a
name a stage-two builder would reasonably type and lose a CI round to — and it
sits inside quotes a review lens certified as clean. Recorded to make the point
that certifying a locator as line-exact says nothing about whether the name at
that locator is reachable.

This contract's W8–W9 are stated on `Set.univ`, and W11–W12 are stated at an
**arbitrary `w : ℂ`, including the zeros**. Any weakening of W8, W9, W11 or W12
to the complement of the zero set is death condition 1 — it would reproduce
the dodge and produce a package that adds nothing over Cotangent.

### 1.4 The product-lemma gap, re-derived — the pool's `mul_compl` is not the minimal missing lemma

**This section is the heart of the contract; the reviewer should read it
adversarially.**

`UPSTREAM_POOL.md` §2 Tier 4 names the blocker as a missing
`HasProdLocallyUniformlyOn.mul_compl`
(confirmed absent at the pin, §0 row 14 of the pool; re-confirmed this session:
`rg "HasProdLocallyUniformlyOn.mul_compl|HasProdUniformlyOn.mul_compl"` = 0
lines) and prices it at "weeks". Re-derivation against the pinned tree shows
the *locally-uniform* split is **not needed**. What the order computation at a
point `w` actually needs is:

1. **A pointwise, global function identity.** For any `S : Set ι`, and every
   `z : ℂ`,
   `weierstrassProduct p a z = (∏' i : S, E_p (z / a i)) * ∏' i : ↥Sᶜ, E_p (z / a i)`.
   This is `Multipliable.tprod_mul_tprod_compl` — **pinned**,
   `Topology/Algebra/InfiniteSum/Basic.lean:752` — applied at each `z`, with
   the two restricted multipliabilities obtained by restricting the **real**
   norm majorant via the additive `Summable.subtype`
   (`@[to_additive]` twin of `Multipliable.subtype`,
   `Topology/Algebra/InfiniteSum/Group.lean:300`) and re-entering ℂ through
   `multipliable_one_add_of_summable` (`Log/Summable.lean:169`). A function
   identity that holds at every `z` needs no uniform-convergence content at
   all. (W10, first signature.)
2. **Analyticity of the complement-tail at `w`.** This is a *subfamily
   instantiation* of the package's own W8+W9 — the family
   `fun i : ↥Sᶜ ↦ a i` satisfies `hane`/`hsum` by restriction
   (`Summable.subtype` again), and `weierstrassProduct p (a ∘ (↑))` is
   definitionally the tail function. No new convergence argument occurs. (W10,
   second signature.)
3. **Nonvanishing of the tail at `w`** when `S` is the fiber `{i | a i = w}`:
   every tail factor is `≠ 0` at `w` by W3, and
   `tprod_one_add_ne_zero_of_summable` (`Log/Summable.lean:216`) — **pinned** —
   kills the tail. (W10, third signature.)
4. **Order additivity across the split**: `analyticOrderAt_mul`
   (`Order.lean:497`) — **pinned** — plus its `Finset`-product iteration, which
   is genuinely absent at the pin but is a routine induction
   (`analyticOrderAt_finsetProd`, W12, tagged `[GEN]`).

**Consequence.** The genuinely missing *generic* lemmas shrink to (a)
`analyticOrderAt_finsetProd` (small) and (b) nothing else: the pool's second
gap row, `MultipliableLocallyUniformlyOn.differentiableOn` (§0 row 13), is
also **not a real gap** — `TendstoLocallyUniformlyOn.differentiableOn`
(LocallyUniformLimit.lean:135) applies to a `HasProdLocallyUniformlyOn`
hypothesis **by definitional unfolding**, and `DedekindEta.lean:91` is the
in-tree precedent doing exactly that (§0). What remains expensive is the
**assembly** of 1–4 into `analyticOrderAt_weierstrassProduct` — fiber
finiteness, `tprod`-to-`Finset.prod` conversion under the pin's
SummationFilter framework, and the beta/`Pi.mul` seams. That assembly is this
contract's named hardest obligation, **S1W-ORD** (HIGH), and it is bookkeeping,
not analysis — scout B's "the estimate is nearly free, the bookkeeping is not"
survives re-derivation with the bookkeeping *relocated* from a missing Mathlib
lemma into the package's own capstone proof.

**Corrections to the pool's §2 rows made during re-verification (full list in
Annex A):** `Complex.logTaylor` is `noncomputable def` (not plain `def`);
`MultipliableUniformlyOn` is at UniformOn.lean:51 (not part of the :44 row);
`Summable.hasProdLocallyUniformlyOn_one_add` requires `[LocallyCompactSpace α]`
(satisfied by ℂ) and `IsOpen K`, not compactness.

### 1.5 Carrier

Pointwise `analyticOrderAt : (ℂ → ℂ) → ℂ → ℕ∞` (Order.lean:47) is the only
order carrier. No `MeromorphicOn.divisor` statement is made: the divisor
interface is `MULTIPLICITY_CONTRACT.md`'s territory (ζ/ξ-specific), and a
generic divisor statement here would duplicate its bridge lemma for no exit
evidence. Recorded as **DEFERRED-W2**. The capstone W12 keeps `ℕ∞`, so the
`⊤` case is *stated away honestly*: the computed value `Nat.card {i | a i = w}`
is finite.

**What the `_ne_top` companion does and does not carry** (corrected 2026-08-08;
the earlier text said it "makes the non-degeneracy explicit rather than burying
it in `untop₀` junk", which over-reads the lemma). `analyticOrderAt`'s junk
value for a function that is **not** analytic at the point is `0`, not `⊤`
(Order.lean:47–:51, quoted with its body in §0; the file's own docstring at :46
says so). Therefore `analyticOrderAt f w ≠ ⊤` certifies nothing about
non-degeneracy on its own — every function that fails to be analytic at `w`
satisfies it. `analyticOrderAt_weierstrassProduct_ne_top` is a **corollary of
the capstone kept for API convenience**: the capstone proves the value equals
`(Nat.card {i | a i = w} : ℕ∞)`, which already carries both the analyticity
(W9) and the finiteness (W7), and `≠ ⊤` then follows by
`WithTop.natCast_ne_top` (Algebra/Order/Monoid/Unbundled/WithTop.lean:298,
re-read: `@[simp] lemma natCast_ne_top (n : ℕ) : (n : WithTop α) ≠ ⊤`). The
non-degeneracy content lives in the capstone, not in its companion. The
statement surface is unaffected — both signatures stand exactly as written.

---

## 2. Statement list W1 – W12

Legend: `[PIN]` provable from pinned Mathlib alone; `[GEN]` generic, natural
Mathlib upstream, absent at the pin (contributed by this package); `[DEF]`
definition. Hypothesis abbreviations `hane`, `hsum` as in §1.2.

---

### Block A — the elementary factor

## W1. Definition and evaluation `[DEF]` `[PIN]` — 4 signatures

### Statement

```lean
/-- The **Weierstrass elementary factor** of genus `p`:
`E p z = (1 - z) * exp (z + z ^ 2 / 2 + ⋯ + z ^ p / p)`. -/
noncomputable def weierstrassFactor (p : ℕ) (z : ℂ) : ℂ :=
  (1 - z) * Complex.exp (∑ k ∈ Finset.range p, z ^ (k + 1) / (k + 1))

@[simp] lemma weierstrassFactor_apply_zero (p : ℕ) : weierstrassFactor p 0 = 1

@[simp] lemma weierstrassFactor_genus_zero (z : ℂ) : weierstrassFactor 0 z = 1 - z

lemma weierstrassFactor_succ (p : ℕ) (z : ℂ) :
    weierstrassFactor (p + 1) z
      = weierstrassFactor p z * Complex.exp (z ^ (p + 1) / (p + 1))
```

### Proof skeleton

`weierstrassFactor_apply_zero`: `simp [weierstrassFactor, Complex.exp_zero]`
(every summand has a `0 ^ (k+1)` factor). `weierstrassFactor_genus_zero`:
`simp [weierstrassFactor]` (`Finset.range 0` sum is empty, `exp 0 = 1`).
`weierstrassFactor_succ`: `Finset.sum_range_succ`, `Complex.exp_add`, `ring`.

Denominator convention (elaborated shape corrected 2026-08-08): in
`∑ k ∈ Finset.range p, z ^ (k + 1) / (k + 1)` at type ℂ the denominator
elaborates as **`(↑k + 1 : ℂ)` — a cast of `k` plus one, not a cast of `k+1`**.
It is nonzero for every `k : ℕ`, so no division junk arises anywhere in the
definition. The distinction is not cosmetic: the pinned `Complex.logTaylor`
(LogBounds.lean:68, `∑ j ∈ Finset.range n, (-1) ^ (j + 1) * z ^ j / j`)
divides by `(↑j : ℂ)`, so after the `Finset.sum_range_succ'` reindex in W4 the
two sides meet as `↑(k+1)` against `↑k + 1` and need a cast bridge (S1W-4a).

### Pinned dependencies (W1)

`Complex.exp_zero` (:95), `Complex.exp_add` (:109) —
`Analysis/Complex/Exponential.lean`, namespace `Complex`, block **:90–:198**
(locator corrected 2026-08-08: the earlier ":347–:509" is the *other* `Complex`
block in that file, the one holding `norm_exp_sub_one_le` at :439; the
`namespace Complex` / `end Complex` pairs are 35/70, 90/198, 347/509, 704/711.
Name resolution is unaffected — both blocks are `Complex` — and W3 already
cites :90–:198 correctly for `exp_ne_zero` at :160, so this removes an internal
contradiction); `Finset.sum_range_succ` (Mathlib core BigOperators). Not
load-bearing beyond name resolution.

### Obligations (W1)

- **S1W-1** (LOW): the name `weierstrassFactor_genus_zero` deliberately avoids
  the pool's `weierstrassFactor_zero`, which reads as "value at zero" under
  Mathlib conventions and would collide in intent with
  `weierstrassFactor_apply_zero`. Reviewer may bikeshed; either name has zero
  pin collisions.

---

## W2. Differentiability and analyticity `[PIN]` — 2 signatures

### Statement

```lean
lemma differentiable_weierstrassFactor (p : ℕ) :
    Differentiable ℂ (weierstrassFactor p)

lemma analyticAt_weierstrassFactor (p : ℕ) (z : ℂ) :
    AnalyticAt ℂ (weierstrassFactor p) z
```

### Proof skeleton

Polynomial times `exp` of a polynomial: `fun_prop` (or explicit
`Differentiable.mul`, `Complex.differentiable_exp.comp`, `Differentiable.sum`).
`analyticAt_weierstrassFactor`:
`(Complex.analyticOnNhd_univ_iff_differentiable.mpr
(differentiable_weierstrassFactor p)) z (Set.mem_univ z)`.

### Pinned dependencies (W2)

`Complex.differentiable_exp` — `Analysis/SpecialFunctions/ExpDeriv.lean:97`
(`@[simp]`, stated for any `𝕜` normed-algebra over ℂ);
`Complex.analyticOnNhd_univ_iff_differentiable` —
`Analysis/Complex/CauchyIntegral.lean:678` (inside `namespace Complex`; the
bare spelling resolves only under this file's `open Complex` — the same
namespace trap `MULTIPLICITY_CONTRACT.md` §0 records for M9).

### Obligations (W2)

- **S1W-2** (LOW): `fun_prop` must see through the `Finset.sum` inside `exp`;
  fallback is `Differentiable.comp` with
  `Differentiable.fun_sum (fun k _ ↦ by fun_prop)`.

---

## W3. Nonvanishing off `1` `[PIN]` — 2 signatures

### Statement

```lean
@[simp] lemma weierstrassFactor_eq_zero_iff {p : ℕ} {z : ℂ} :
    weierstrassFactor p z = 0 ↔ z = 1

lemma weierstrassFactor_ne_zero {p : ℕ} {z : ℂ} (hz : z ≠ 1) :
    weierstrassFactor p z ≠ 0
```

### Proof skeleton

`weierstrassFactor` is `(1 - z) * exp (…)`; `mul_eq_zero`, `Complex.exp_ne_zero`
(Exponential.lean:160) kills the right factor, `sub_eq_zero` orients
`1 - z = 0 ↔ 1 = z`, `eq_comm` finishes. Second signature: `mt`
of the first.

### Pinned dependencies (W3)

`Complex.exp_ne_zero` — `Analysis/Complex/Exponential.lean:160` (namespace
`Complex`, block :90–:198 — note :235 is the `Real` twin; do not cite it);
`mul_eq_zero`, `sub_eq_zero` (core algebra).

### Obligations (W3)

- **S1W-3** (LOW): orientation `1 - z = 0 ↔ z = 1` needs `sub_eq_zero` then
  `eq_comm`; `simp` may normalize the other way. Fallback:
  `constructor <;> intro h <;> [skip; subst h] <;> simp_all`.

---

## W4. Bridge to `Complex.logTaylor`, and the branch-free exponential form `[PIN]` — 2 signatures

### Statement

```lean
/-- `logTaylor (p+1)` at `-z` is minus the exponent sum of `weierstrassFactor p`.
Pure algebra; this is the whole seam between W6 and the pinned log bound. -/
lemma logTaylor_neg_eq (p : ℕ) (z : ℂ) :
    Complex.logTaylor (p + 1) (-z) = -∑ k ∈ Finset.range p, z ^ (k + 1) / (k + 1)

/-- Branch-free exponential form: avoids `log_mul` and all argument bookkeeping. -/
lemma weierstrassFactor_eq_exp {p : ℕ} {z : ℂ} (hz : z ≠ 1) :
    weierstrassFactor p z
      = Complex.exp (Complex.log (1 - z) + ∑ k ∈ Finset.range p, z ^ (k + 1) / (k + 1))
```

### Proof skeleton

`logTaylor_neg_eq`: unfold `logTaylor` (LogBounds.lean:68:
`∑ j ∈ Finset.range n, (-1) ^ (j + 1) * z ^ j / j`); the `j = 0` term is
`(-1) * 1 / (0 : ℂ)` and Lean's `x / 0 = 0` convention kills it — this junk
absorption is load-bearing and must be stated in a comment in the built file.
Split `Finset.range (p+1)` via `Finset.sum_range_succ'` (the head-at-zero
variant), then termwise: `(-1)^(k+2) * (-z)^(k+1) / (k+1) = -(z^(k+1)/(k+1))`
by `neg_pow` and `ring`. `weierstrassFactor_eq_exp`: `Complex.exp_add`, then
`Complex.exp_log (sub_ne_zero.mpr (Ne.symm hz) : (1 : ℂ) - z ≠ 0)` on the left
factor, fold `weierstrassFactor`.

### Pinned dependencies (W4)

`Complex.logTaylor` — `Analysis/SpecialFunctions/Complex/LogBounds.lean:68`
(**`noncomputable def`**, inside `namespace Complex` :32–:290);
`Complex.exp_log` — `Analysis/SpecialFunctions/Complex/Log.lean:41`;
`Complex.exp_add`; `Finset.sum_range_succ'`; `neg_pow`.

### Obligations (W4)

- **S1W-4a** (MEDIUM): the `j = 0` junk-term absorption and the
  `range (p+1) → range p` reindex are exactly the "one `Finset.range` reindex"
  the pool priced; the skeleton above names the specific lemma
  (`Finset.sum_range_succ'`) but the sign bookkeeping (`(-1)^(k+2)`,
  `(-z)^(k+1)`) is `rw`-fragile. **Plus a cast bridge, named 2026-08-08:** the
  reindex leaves `logTaylor`'s `↑(k+1)` facing this package's `↑k + 1` (see
  W1's denominator convention), so a `Nat.cast_succ` / `push_cast` step is
  required in addition to the sign bookkeeping. Fallback: `induction p` with
  `logTaylor_succ` (**LogBounds.lean:75** — locator corrected 2026-08-08 from
  the drafted ":73 region"; re-read at the pin: `lemma logTaylor_succ (n : ℕ) :
  logTaylor (n + 1) = logTaylor n + (fun z : ℂ ↦ (-1) ^ (n + 1) * z ^ n / n)`)
  and `Finset.sum_range_succ`.
- **S1W-4b** (LOW): `sub_ne_zero.mpr (Ne.symm hz)` orientation (`1 - z ≠ 0`
  from `z ≠ 1` needs `1 ≠ z`).

---

## W5. The log bound, consumed `[PIN]` — 1 signature

### Statement

```lean
/-- The pinned estimate `LogBounds.lean:231`, restated on the exponent sum of
`weierstrassFactor`. Everything here except the statement shape is already a
theorem at the pin. -/
theorem norm_log_one_sub_add_sum_le (p : ℕ) {z : ℂ} (hz : ‖z‖ < 1) :
    ‖Complex.log (1 - z) + ∑ k ∈ Finset.range p, z ^ (k + 1) / (k + 1)‖
      ≤ ‖z‖ ^ (p + 1) * (1 - ‖z‖)⁻¹ / (p + 1)
```

### Proof skeleton

Primary skeleton (the `▸`-free form, **promoted from fallback to primary
2026-08-08** — see the failure analysis below):

```lean
  have h := Complex.norm_log_one_sub_inv_add_logTaylor_neg_le p hz   -- LogBounds.lean:231
  -- h : ‖log (1 - z)⁻¹ + logTaylor (p + 1) (-z)‖ ≤ ‖z‖ ^ (p + 1) * (1 - ‖z‖)⁻¹ / (p + 1)
  have hsp : (1 : ℂ) - z ∈ Complex.slitPlane := by
    rw [sub_eq_add_neg]
    exact Complex.mem_slitPlane_of_norm_lt_one (by rwa [norm_neg])
  rw [Complex.log_inv _ (Complex.slitPlane_arg_ne_pi hsp),           -- log (1-z)⁻¹ = -log (1-z)
      logTaylor_neg_eq] at h                                         -- W4
  -- h : ‖-log (1 - z) + -∑ …‖ ≤ …
  simpa [← neg_add, norm_neg] using h
```

**Why not the `▸`-chain** (failure-class (C) analysis, 2026-08-08; the drafted
skeleton was `Complex.log_inv _ (Complex.slitPlane_arg_ne_pi ((sub_eq_add_neg 1
z) ▸ Complex.mem_slitPlane_of_norm_lt_one ((norm_neg z).symm ▸ hz)))`). The
outer `▸` feeds `slitPlane_arg_ne_pi`, whose binder is **implicit** —
re-read at the pin, `Analysis/SpecialFunctions/Complex/Arg.lean:544`: `lemma
slitPlane_arg_ne_pi {z : ℂ} (hz : z ∈ slitPlane) : z.arg ≠ Real.pi`. The
expected type of the argument is therefore `?z ∈ slitPlane`, which contains a
metavariable. `Complex.log_inv` is Log.lean:137, `x` **explicit**: `theorem
log_inv (x : ℂ) (hx : x.arg ≠ π) : log x⁻¹ = -log x`.

**The failure this paragraph used to predict does not exist — refuted
2026-08-09 against the Lean 4.31.0 elaborator source.** The 2026-08-08 text
said `▸` "may simply unify `?z := 1 + -z` and leave the type unrewritten". No
such path is reachable. `elabSubst` opens with `tryPostponeIfHasMVars?`
(`Lean/Elab/BuiltinNotation.lean:457-458`), and that helper returns `none`
whenever the expected type contains a metavariable at all
(`Lean/Elab/Term/TermElabM.lean:1366-1373`, testing `hasExprMVar`). Returning
`none` forces the branch at BuiltinNotation.lean:524–537, which **ignores the
expected type entirely** and rewrites the HYPOTHESIS type forward: `kabstract`
finds `1 + -z` in `1 + -z ∈ slitPlane`, `mkEqSymm` flips the equation, and
`mkEqRec` delivers `1 - z ∈ Complex.slitPlane` — the type actually wanted. The
other branch (:478–:483) would `throwError` loudly rather than produce a wrong
type. There is no silent-misfire branch.

Two further notes, since the refuted paragraph is easy to half-repair. "Metavariable-headed" was itself inaccurate: `?z ∈ slitPlane` is headed by
`Membership.mem` and merely *contains* a metavariable — harmless only because
the guard tests `hasExprMVar` rather than the head. And the tempting alternative
explanation, that the outer application `log_inv _` pins `?z`, is also wrong:
`rw` elaborates its rule term with no expected type at all
(`Lean/Elab/Tactic/Rewrite.lean:28`, `elabTerm stx none true`), so nothing
downstream constrains it.

Note what the pin's own proof of :231 actually does (LogBounds.lean:233–:236,
re-read): it rewrites the **goal** with `sub_eq_add_neg` FIRST and only then
applies `log_inv _ <| slitPlane_arg_ne_pi <| mem_slitPlane_of_norm_lt_one <|
(norm_neg z).symm ▸ hz`. Only the *inner* `(norm_neg z).symm ▸ hz` is
precedented there; the outer `sub_eq_add_neg ▸` is this contract's own
invention and has no pin precedent. The `have hsp` form above reproduces the
pin's ordering without depending on `▸` unification.

### Pinned dependencies (W5)

- `Complex.norm_log_one_sub_inv_add_logTaylor_neg_le` —
  `Analysis/SpecialFunctions/Complex/LogBounds.lean:231`. **Verified verbatim
  this session** (quoted in §0). This is scout B's counterintuitive find: the
  classically hardest estimate of the entire package is already pinned.
- `Complex.log_inv` — `Analysis/SpecialFunctions/Complex/Log.lean:137`
  (`log x⁻¹ = -log x` under `x.arg ≠ π`).
- `Complex.mem_slitPlane_of_norm_lt_one` — `Analysis/Complex/Basic.lean:689`
  (stated for `1 + z`; used here at `-z` with `norm_neg` and
  `sub_eq_add_neg`).
- `Complex.slitPlane_arg_ne_pi` —
  `Analysis/SpecialFunctions/Complex/Arg.lean:544`.
- W4 (`logTaylor_neg_eq`).

### Obligations (W5)

- **S1W-LOG** (LOW — **re-priced 2026-08-09, down from MEDIUM**): the standalone
  `hsp : (1 : ℂ) - z ∈ Complex.slitPlane` `have` remains the *primary* route,
  because it mirrors the pin's own ordering at LogBounds.lean:233–:235 and
  because a named `have` with a closed type cannot half-succeed. But the reason
  the 2026-08-08 reordering gave — that the `▸`-chain "may unify instead of
  rewriting" — is **refuted**; the elaborator has no such branch (sources cited
  in the skeleton above). The `▸`-chain is a legitimate fallback, not a trap.

  The severity drop follows from removing that phantom. What remains is the
  final `simpa [← neg_add, norm_neg]`, which must merge `-a + -b` to `-(a + b)`;
  if it misfires, `rw [← neg_add] at h; rwa [norm_neg] at h`. That is ordinary
  simp-normal-form bookkeeping.

  Honest bound on the re-pricing: it rests on reading `elabSubst` and
  `tryPostponeIfHasMVars?`, not on running them. The branch selection is
  deterministic from source; what is not settled from source is whether
  `kabstract`'s head-keyed matching plus `isDefEq` on instance paths finds the
  occurrence in every instantiation. That residual is real but small, and it is
  a different risk from the one that was priced.

---

## W6. The Weierstrass estimate `[PIN]` — 1 signature

### Statement

```lean
/-- The sole input to the convergence criterion: `‖E p z - 1‖ ≤ 4/(p+1) · ‖z‖^(p+1)`
on `‖z‖ ≤ 1/2`. Deliberately NOT the sharp Rudin 15.8 bound on the closed unit
disc (see DEFERRED-W3). -/
theorem norm_weierstrassFactor_sub_one_le {p : ℕ} {z : ℂ} (hz : ‖z‖ ≤ 1 / 2) :
    ‖weierstrassFactor p z - 1‖ ≤ 4 / (p + 1) * ‖z‖ ^ (p + 1)
```

### Proof skeleton

`‖z‖ ≤ 1/2 < 1` gives `z ≠ 1` (norms), so W4's exponential form applies. Set
`L := Complex.log (1 - z) + ∑ …`. Then:

1. `hL : ‖L‖ ≤ ‖z‖ ^ (p+1) * (1 - ‖z‖)⁻¹ / (p+1)` — W5 with `hz.trans_lt (by norm_num)`.
2. `(1 - ‖z‖)⁻¹ ≤ 2` from `‖z‖ ≤ 1/2` (`inv_le_of_inv_le₀` / `div_le_iff₀`
   arithmetic; the pin's own file does this dance at LogBounds.lean:215–223).
3. `hL1 : ‖L‖ ≤ 1`: chain `‖L‖ ≤ (1/2)^(p+1) * 2 / (p+1) ≤ 1` (`p + 1 ≥ 1`,
   `(1/2)^(p+1) ≤ 1/2`).
4. `Complex.norm_exp_sub_one_le hL1 : ‖exp L - 1‖ ≤ 2 * ‖L‖` (Exponential.lean:439).
5. **Pre-combine steps 1 and 2 into one hypothesis before assembling.** This is
   not cosmetic; see the mechanism note below.

   ```lean
   have hinv : (1 - ‖z‖)⁻¹ ≤ 2 := …          -- Inv.inv-headed; the shape matters
   have hL2 : ‖L‖ ≤ ‖z‖ ^ (p+1) * 2 / (p+1) := hL.trans (by gcongr)
   ```

   The inner goal is `‖z‖^(p+1) * (1-‖z‖)⁻¹ / (p+1) ≤ ‖z‖^(p+1) * 2 / (p+1)`.
   `gcongr` descends the `HDiv` by `div_le_div_of_nonneg_right`
   (`Algebra/Order/GroupWithZero/Basic.lean:1199`, one varying argument, so the
   two-varying `div_le_div₀` at :1285 is never reached), then the `HMul` by
   `mul_le_mul_of_nonneg_left` (`GroupWithZero/Defs.lean:226`; the
   `@[gcongr high]` / `high - 1` monoid lemmas at
   `Algebra/Order/Monoid/Unbundled/Basic.lean:70, :81, :209` are tried first and
   fail `MulLeftMono ℝ` / `MulRightMono ℝ` synthesis). Side goals
   `0 ≤ ‖z‖^(p+1)` and `0 ≤ (↑p+1 : ℝ)` go to `positivity`.

   **Step 2 must be a NAMED `have`, and its type must be `Inv.inv`-headed**
   (tightened 2026-08-09 after an adversarial verifier found this unstated).
   The terminal goal is `(1 - ‖z‖)⁻¹ ≤ 2` and `gcongr`'s only closer for it is
   the forward discharger, which iterates over **local-context fvars** and
   assigns by `isDefEq` at REDUCIBLE transparency (`Core.lean:476`, :503–:509,
   :471). Two ways to lose a round here, both silent:
   - step 2 produced inline rather than bound — the discharger sees nothing, the
     goal is pushed and discarded, `gcongr` reports progress, and the `by` block
     fails with "unsolved goals";
   - step 2 bound in the shape its own cited `div_le_iff₀` naturally yields,
     `1 / (1 - ‖z‖) ≤ 2` — `HDiv`-headed against an `Inv.inv`-headed goal.
     `one_div` is not reducible unfolding, so `assignIfDefEq` fails and you land
     in the same state.

   Prefer the template `by gcongr ‖z‖ ^ (p+1) * ?_ / (↑p+1)` so the seam is
   named and a mismatch throws instead of vanishing.

6. Assemble as an explicit `calc`:

   ```lean
   calc ‖weierstrassFactor p z - 1‖
       = ‖Complex.exp L - 1‖         := by rw [hLform]          -- W4
     _ ≤ 2 * ‖L‖                     := Complex.norm_exp_sub_one_le hL1
     _ ≤ 2 * (‖z‖ ^ (p+1) * 2 / (p+1)) := mul_le_mul_of_nonneg_left hL2 (by norm_num)
     _ = 4 / (p+1) * ‖z‖ ^ (p+1)     := by field_simp; ring     -- with (p+1 : ℝ) ≠ 0
   ```

   `mul_le_mul_of_nonneg_left (hbc : b ≤ c) (ha : 0 ≤ a) : a * b ≤ a * c` —
   `Algebra/Order/GroupWithZero/Defs.lean:226` (`@[gcongr]` on :225; the
   relation comes FIRST and the nonnegativity second — note the lemma's own
   body applies the class field in the opposite order, which is the trap). A term is used rather than a
   tactic because the term cannot silently half-succeed. The registered
   alternative, if the term is ever inconvenient, is the TEMPLATE form
   `by gcongr 2 * ?_` — never a bare `gcongr`; see below for why the template
   matters. The closing line is a pure identity and needs
   `field_simp`/`ring` with `(p + 1 : ℝ) ≠ 0`, never `gcongr`.

**Mechanism, corrected 2026-08-09 — the 2026-08-08 note here was wrong, and
wrong in the dangerous direction.** That note said a single `gcongr` spanning
`2 * ‖L‖ ≤ 4/(p+1) * ‖z‖^(p+1)` "cannot" fire because "those two expressions
have different `*` / `/` node structure". They do not. `2 * ‖L‖` is
`HMul.hMul` at arity 6 and so is `4/(p+1) * ‖z‖^(p+1)`; the `/` sits inside an
argument, where `gcongr`'s shape gate never looks. That gate is
`lhsHead == rhsHead` on `Name`s — `Mathlib/Tactic/GCongr/Core.lean:712`, reading
heads through `constName?` (:224–:233) off sides that are explicitly not whnf'd
for `≤` (:704–:705).

So the bare `gcongr` **matches**. After the higher-priority lemmas fail instance
synthesis for `ℝ`, it applies `mul_le_mul`
(`Algebra/Order/GroupWithZero/Defs.lean:352`, alias of `mul_le_mul_of_nonneg'`
at :316) with all four slots free, discharges both side goals `0 ≤ ‖L‖` and
`0 ≤ 4/(p+1)` by `positivity`, and emits two main goals — one of which is

    2 ≤ 4 / (↑p + 1)

which is **FALSE for every `p ≥ 2`**. The tactic reports progress. A prover
chasing that goal is chasing something unprovable with no signal that the
decomposition was wrong. A predicted refusal costs a round; a silent wrong
split costs however long it takes someone to notice the goal is false.

Two consequences the old note did not license:

- **The `calc` split is mandatory for a stronger reason than shape.** `gcongr`
  is a single-relational-step tactic — docstring `Core.lean:747-750`, and its
  only transitivity move `rel_imp_rel` (:541–:558) is gated to implication goals
  at :720–:721. It cannot chain steps 1 and 2 for you, which is exactly why
  `hL2` must be pre-combined.
- **The `calc` as written on 2026-08-08 did not close.** Its middle line was
  `by gcongr`, which descends to `‖L‖ ≤ ‖z‖^(p+1) * 2/(p+1)` — heads
  `Norm.norm` arity 3 against `HDiv.hDiv` arity 6, a mismatch — and with no
  template that mismatch is pushed as a new goal and DISCARDED by the parent
  (:707–:713, :732–:733), so `gcongr` succeeds and the enclosing block fails
  with "unsolved goals". Steps 1 and 2 supplied a different expression and
  `gcongr` cannot bridge them. The fix that was applied therefore shipped a
  skeleton that could not work; `hL2` is what repairs it.

Prefer `gcongr <template with ?_>` over bare `gcongr` everywhere in this
contract. With a template the same mismatches `throwTacticEx` at :708/:711/:714
with "are not of the same shape", turning every silent residual into a hard
error at the exact seam.

### Pinned dependencies (W6)

W4, W5; `Complex.norm_exp_sub_one_le` —
`Analysis/Complex/Exponential.lean:439` (verified verbatim:
`(hx : ‖x‖ ≤ 1) : ‖exp x - 1‖ ≤ 2 * ‖x‖`, namespace `Complex`).

### Obligations (W6)

- **S1W-EST** (MEDIUM): pure `gcongr`/`linarith` bookkeeping over `ℝ` with a
  `(p + 1 : ℝ)`-cast in denominators (`Nat.cast_pos`, `div_le_div_iff₀`). No
  mathematical content; one CI cycle of cast-lemma whack-a-mole is priced in.
  **Folded in 2026-08-08, re-priced 2026-08-09:** the assembly must be a `calc`
  and the closing `= 4/(p+1) * ‖z‖^(p+1)` must go to `field_simp`/`ring` under
  `(p + 1 : ℝ) ≠ 0`. That instruction stands. Its 2026-08-08 justification does
  not: a bare `gcongr` across the whole chain does not refuse, it fires
  `mul_le_mul` and emits the FALSE goal `2 ≤ 4/(p+1)` with both side conditions
  discharged. Read the mechanism note in the skeleton before touching this
  step. The residual risk here is therefore not "one CI cycle of cast
  whack-a-mole" but a wrong-goal detour, which is why the step-6 middle line is
  a term and the pre-combined `hL2` of step 5 is required rather than
  suggested.
- **Anti-scope note.** The sharp `‖1 - E_p z‖ ≤ ‖z‖^(p+1)` on the closed unit
  disc (Rudin RCA 15.8) is **DEFERRED-W3 / death condition 5**: it needs
  coefficient-nonnegativity of `exp(∑ z^k/k)` with no Mathlib precursor, and
  nothing in W7–W12 needs it (pool Tier 5, re-endorsed).

---

### Block B — the canonical product: convergence

## W7. Product definition, escape to infinity, fiber finiteness `[DEF]`/`[PIN]` — 3 signatures

### Statement

```lean
/-- The **Weierstrass canonical product** of genus `p` over the zero family `a`. -/
noncomputable def weierstrassProduct (p : ℕ) (a : ι → ℂ) (z : ℂ) : ℂ :=
  ∏' i, weierstrassFactor p (z / a i)

/-- The zero family escapes every ball, cofinitely. Derived from `hsum`, not assumed. -/
lemma eventually_cofinite_le_norm (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) (R : ℝ) :
    ∀ᶠ i in Filter.cofinite, R ≤ ‖a i‖

/-- Every fiber of the zero family is finite. -/
lemma finite_setOf_apply_eq (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) (w : ℂ) :
    {i | a i = w}.Finite
```

### Proof skeleton

`eventually_cofinite_le_norm`: `hsum.tendsto_cofinite_zero` (the `@[to_additive]`
twin of `Multipliable.tendsto_cofinite_one`, Group.lean:365, valid since ℝ is an
additive commutative topological group) gives
`Tendsto (fun i ↦ ‖a i‖⁻¹ ^ (p+1)) cofinite (𝓝 0)`; take the eventual bound
below `((max R 1)⁻¹) ^ (p+1) > 0` and invert: for such `i`,
`‖a i‖⁻¹ ^ (p+1) < (max R 1)⁻¹ ^ (p+1)` forces `‖a i‖⁻¹ < (max R 1)⁻¹`
(`pow_lt_pow_iff_left₀`-family on nonnegatives) hence `max R 1 < ‖a i‖`
(`inv_lt_inv₀`, using `‖a i‖ > 0` from `hane` and `norm_pos_iff`), hence
`R ≤ ‖a i‖`. `finite_setOf_apply_eq`:
`{i | a i = w} ⊆ {i | ¬ (‖w‖ + 1 ≤ ‖a i‖)}`, and the latter is finite by
`Filter.eventually_cofinite.mp (eventually_cofinite_le_norm … (‖w‖ + 1))`.

### Pinned dependencies (W7)

`Summable.tendsto_cofinite_zero` —
`Topology/Algebra/InfiniteSum/Group.lean:365` (`@[to_additive]` on
`Multipliable.tendsto_cofinite_one`; **the multiplicative form needs
`[CommGroup α]` and does NOT apply to ℂ-under-multiplication — only the
additive ℝ-valued form is used, here and everywhere in this package**);
`Filter.eventually_cofinite`; `norm_pos_iff`; `inv_lt_inv₀`-family.

### Obligations (W7)

- **S1W-INV** (MEDIUM): the inverse-power arithmetic (step from
  `‖a i‖⁻¹ ^ (p+1) < ε ^ (p+1)` back to `‖a i‖ > ε⁻¹`) is elementary but
  lemma-name-fragile across `pow_lt_pow_left₀` / `inv_lt_inv₀` variants.
  Self-contained; a `nlinarith`/`positivity` fallback exists at every step.
- **S1W-SUB** (recorded here, used from W10 on) (LOW): all subtype
  restrictions of summability go through the **additive** `Summable.subtype`
  (to_additive twin of `Multipliable.subtype`, Group.lean:300) applied to
  ℝ-valued norm families — never through the multiplicative form, which
  demands a `CommGroup` that ℂ-under-`*` is not.

---

## W8. Locally uniform convergence on all of ℂ `[PIN]` — 2 signatures

### Statement

```lean
/-- Pointwise absolute convergence of the factor tails, every `z`. -/
lemma summable_norm_weierstrassFactor_sub_one (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) (z : ℂ) :
    Summable fun i ↦ ‖weierstrassFactor p (z / a i) - 1‖

/-- The canonical product converges locally uniformly on the whole plane —
`Set.univ`, not a zero-avoiding subdomain (contrast Cotangent.lean:132 on `ℂ_ℤ`). -/
theorem hasProdLocallyUniformlyOn_weierstrassProduct (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) :
    HasProdLocallyUniformlyOn (fun i z ↦ weierstrassFactor p (z / a i))
      (weierstrassProduct p a) Set.univ
```

### Proof skeleton

Compact-by-compact, the Cotangent pattern with the majorant swapped:

1. `hasProdLocallyUniformlyOn_of_forall_compact isOpen_univ` (UniformOn.lean:196;
   `[LocallyCompactSpace ℂ]` holds — ℂ is proper). Fix `K` compact and **bind
   the radius and the inclusion by name** — step 3 consumes `hKR`, and the
   2026-08-09 text referred to it before this line introduced it:
   `obtain ⟨R, hR0, hKR⟩ : ∃ R ≥ 0, K ⊆ Metric.closedBall 0 R := …`
   (`IsCompact.isBounded` + `Bornology.IsBounded.subset_closedBall`).
2. Majorant `u i := 4 / (p+1) * (R ^ (p+1) * ‖a i‖⁻¹ ^ (p+1))`; summable from
   `hsum` by `Summable.mul_left`.
3. Eventual bound: by W7 (`eventually_cofinite_le_norm … (2 * R + 1)`),
   cofinitely many `i` have `2 * R + 1 ≤ ‖a i‖`; for those and any `x ∈ K`,
   `‖x / a i‖ ≤ R / (2R + 1) ≤ 1/2`, so W6 gives
   `‖weierstrassFactor p (x / a i) - 1‖ ≤ 4/(p+1) * ‖x / a i‖^(p+1) ≤ u i`
   (`norm_div`, `div_pow`, then **an explicit normalization before `gcongr`**).

   **The normalization is not optional**, and the reason is stronger than the
   2026-08-08 note gave (re-verified 2026-08-09). After `norm_div` and `div_pow`
   the left inner term is `‖x‖^(p+1) / ‖a i‖^(p+1)`, an `HDiv` node, while
   `u i`'s inner term is `R^(p+1) * ‖a i‖⁻¹^(p+1)`, an `HMul` node. `gcongr`
   compares heads by `Name` equality (`Mathlib/Tactic/GCongr/Core.lean:712`) off
   sides it does not whnf for `≤` (:704–:705), so it will never relate the two.
   **And no lemma can ever bridge them**: the `@[gcongr]` attribute itself
   rejects, at declaration time, any lemma whose conclusion has differing heads
   (`Core.lean:266-267`). This is not a gap in the current library; it is closed
   by construction.

   Two corrections to how that note described the consequence:

   - **The symptom is "unsolved goals", not a `gcongr` error.** The OUTER node
     `4/(p+1) * _` matches on both sides, so `gcongr` descends, applies
     `mul_le_mul_of_nonneg_left`, and only then hits the mismatch — which,
     absent a template, is pushed as a new goal and discarded by the parent
     (:707–:713, :732–:733). `gcongr` reports success. Do not go looking for a
     `gcongr` diagnostic in the CI log; there will not be one.
   - **`rw [← div_pow]` is NOT one of the ways out and has been struck.** It
     turns the left inner term into `(‖x‖ / ‖a i‖)^(p+1)`, an `HPow` node, and
     the right stays `HMul` — one mismatch swapped for another.

   Two ways out survive; pick one at build time and keep it consistent:
   (i) insert `simp only [div_eq_mul_inv, ← inv_pow]` so both sides are the same
   node shape before calling `gcongr`; or (ii) state the majorant in step 2 as
   `u i := 4 / (p+1) * (R ^ (p+1) / ‖a i‖ ^ (p+1))`, so both sides read
   `c * (A / B)` — at the cost of moving the same `div_eq_mul_inv`/`inv_pow`
   bridge into the `Summable.mul_left` step, where `hsum` is stated with
   `‖a i‖⁻¹ ^ (p+1)`. The bridge is paid once either way; what must not happen
   is calling `gcongr` across it.

   Route (ii) is preferred. Route (i) fights the global simp normal form:
   `inv_pow` is `@[simp]` in the OPPOSITE direction (`a⁻¹ ^ n = (a ^ n)⁻¹`,
   `Algebra/Group/Basic.lean:414`), so `‖a i‖⁻¹ ^ (p+1)` — the shape `hsum` and
   the majorant are both stated in — is anti-normal, and any later plain `simp`
   will undo the normalization. Only `simp only` is safe near it.

   **Both routes bottom out at `‖x‖ ≤ R`, which this skeleton never derives.**
   Whichever normalization is chosen, `gcongr` descends through the constant
   factor and the `pow`, and its terminal goal is `‖x‖ ≤ R`. Its only closer
   there is the forward discharger (`Core.lean:464-509`), which iterates over
   local-context fvars and closes by `exact` / `Eq.subst`+`rfl` / `symm`, plus
   three further `@[gcongr_forward]` extensions at the pin — `le_of_lt`
   (`Order/Basic.lean:195`), `AntisymmRel` (`Order/Antisymmetrization.lean:98`)
   and `⊂ → ⊆` (`Order/RelClasses.lean:644`). None of them can manufacture
   `‖x‖ ≤ R` from `K ⊆ closedBall 0 R`, which is all step 1 supplies. Add the
   conversion explicitly before the call:

   ```lean
   have hxR : ‖x‖ ≤ R := mem_closedBall_zero_iff.mp (hKR hx)
   ```

   Omitting it reproduces the same silent residual described above, one level
   deeper. Prefer the TEMPLATE form `gcongr 4 / (↑p+1) * ?_` over a bare
   `gcongr` here: with a template every one of these mismatches becomes a hard
   error at the exact seam (`Core.lean:708`, :711, :714) instead of a discarded
   subgoal.
4. `Summable.hasProdUniformlyOn_one_add hK hu h hcts`
   (MultipliableUniformlyOn.lean:87) with
   `f i x := weierstrassFactor p (x / a i) - 1`; `hcts` by `fun_prop` from W2.
5. Limit and family identification: the criterion produces
   `HasProdUniformlyOn (fun i x ↦ 1 + f i x) (fun x ↦ ∏' i, (1 + f i x)) K`;
   rewrite `1 + (E - 1) = E` on both slots via `HasProdUniformlyOn.congr`
   (UniformOn.lean:73) and `HasProdUniformlyOn.congr_right` (:80) +
   `tprod_congr` (Basic.lean:471), folding `weierstrassProduct`.

`summable_norm_weierstrassFactor_sub_one`: same split at radius `‖z‖`;
cofinitely many factors are bounded by the summable tail (step 3 at `x = z`),
finitely many exceptions are absorbed by `Summable.of_norm_bounded_eventually`
/ summability-mod-finite.

### Pinned dependencies (W8)

`hasProdLocallyUniformlyOn_of_forall_compact` — UniformOn.lean:196;
`Summable.hasProdUniformlyOn_one_add` — MultipliableUniformlyOn.lean:87
(namespace `Summable` :80–:157; `cofinite`-eventual hypothesis matches step 3's
output **exactly** — no exceptional-index surgery needed);
`HasProdUniformlyOn.congr`/`congr_right` — UniformOn.lean:73/:80;
`tprod_congr` — InfiniteSum/Basic.lean:471; W2, W6, W7. In-tree template:
Cotangent.lean:105–:132 (`sineTerm_bound_aux` →
`multipliableUniformlyOn_euler_sin_prod_on_compact` →
`HasProdLocallyUniformlyOn_euler_sin_prod`), with our steps 2–3 replacing
`sineTerm_bound_aux`. **Heading caveat (2026-08-08): `sineTerm_bound_aux`
(Cotangent.lean:105) is `private` at the pin and is therefore NOT a pinned
dependency in the usable sense — it is a *pattern* to imitate, not a name to
`exact`.** It is listed here only because this contract's steps 2–3 replace it;
nothing in W8 may consume it. The other seven Cotangent anchors (:78
`noncomputable abbrev sineTerm`, :80 `sineTerm_ne_zero` with `hx : x ∈ ℂ_ℤ`,
:94, :99, :118, :125 with `hZ2 : Z ⊆ ℂ_ℤ`, :132 on `ℂ_ℤ`) are public and
line-exact (re-read 2026-08-08, all seven re-confirmed 2026-08-09).

**Two further caveats on that list, both found 2026-08-09.** First, `ℂ_ℤ` in
those three quotes is `local notation` and is unwritable outside Cotangent.lean
— see §1.3; the quotes are source text, not an interface. Second, `sineTerm`
(:78) is an `abbrev`, i.e. `@[reducible] def`, so it unfolds silently during
unification; treat it as a pattern whose shape will not survive `whnf`-sensitive
matching the way a plain `def` would. Nothing else the contract cites from
Cotangent.lean is `private`: the file has nine `private` declarations (:105,
:249, :289, :292, :302, :340, :346, :355, :380) and this contract names only
:105.

### Obligations (W8)

- **S1W-CONV** (MEDIUM-HIGH): the `1 + (E - 1) = E` re-identification (step 5)
  is the same congr-seam Cotangent handles at :125–:130 via `congr_right` and
  a `tprod` rewrite, but here on **two** slots (family and limit). Beta-redex
  discipline as in `MULTIPLICITY_CONTRACT.md` finding A2: close with
  `simp only [add_sub_cancel]`-style congr lemmas, never bare `rw` under a
  binder. Fallback: state the criterion's raw conclusion as a `have` and
  convert with `HasProdLocallyUniformlyOn.congr`-analogues pointwise.
- **S1W-RAD** (LOW → **MEDIUM, raised 2026-08-08**): the `R / (2R + 1) ≤ 1/2`
  and `R ≥ 0` bookkeeping (`positivity`/`linarith`) — **plus the step-3
  `div`-vs-`mul` normalization that must precede `gcongr`**, which the LOW
  rating did not cover and which is a named failure class, not arithmetic
  whack-a-mole. The obligation now reads: normalize the majorant comparison to
  a single node shape, *then* `gcongr`. If a build prefers to open this as a
  sibling obligation instead of widening S1W-RAD, that is a stage-two
  bookkeeping choice and changes nothing else.

---

### Block C — analyticity of the limit

## W9. The product is entire `[PIN]` — 2 signatures

### Statement

```lean
theorem differentiable_weierstrassProduct (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) :
    Differentiable ℂ (weierstrassProduct p a)

lemma analyticAt_weierstrassProduct (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) (z : ℂ) :
    AnalyticAt ℂ (weierstrassProduct p a) z
```

### Proof skeleton

```lean
  have h := hasProdLocallyUniformlyOn_weierstrassProduct hane hsum      -- W8
  -- HasProdLocallyUniformlyOn is DEFEQ to TendstoLocallyUniformlyOn (UniformOn.lean:152);
  -- generalized field notation resolves .differentiableOn through the def —
  -- in-tree precedent: DedekindEta.lean:91.
  have hd : DifferentiableOn ℂ (weierstrassProduct p a) Set.univ :=
    h.differentiableOn
      (.of_forall fun s ↦ by
        simpa [Finset.prod_fn] using
          DifferentiableOn.finsetProd
            (fun i _ ↦ ((differentiable_weierstrassFactor p).comp
              (by fun_prop)).differentiableOn))                        -- partial products
      isOpen_univ
  exact differentiableOn_univ.mp hd
```

`analyticAt_weierstrassProduct`: `Complex.analyticOnNhd_univ_iff_differentiable.mpr`
(CauchyIntegral.lean:678) applied to the first signature, evaluated at `z`.

### Pinned dependencies (W9)

`TendstoLocallyUniformlyOn.differentiableOn` —
`Analysis/Complex/LocallyUniformLimit.lean:135` (declared `_root_.`);
`Filter.atTop_neBot` — `Order/Filter/AtTopBot/Basic.lean:66` (discharges
`[φ.NeBot]` for `φ = atTop : Filter (Finset ι)`: `Finset ι` is a nonempty
directed order for **every** `ι`, including `ι` empty, via `⟨∅⟩`);
`DifferentiableOn.finsetProd` — `Analysis/Calculus/Deriv/Mul.lean:530`;
`Finset.prod_fn` — `Algebra/BigOperators/Pi.lean:51`; working template
`DedekindEta.lean:88–:93` (quoted in §0; range corrected 2026-08-08 from
":89–95" — the precedent lemma `differentiableOn_tprod_one_sub_pow` spans
docstring :88 to :93, :94 is blank, and :95 opens the next lemma's docstring);
W2, W8.

### Obligations (W9)

- **S1W-DIFF** (LOW-MEDIUM): the dot-notation unfolding
  `HasProdLocallyUniformlyOn → TendstoLocallyUniformlyOn` is precedented
  (DedekindEta.lean:91) but is resolution magic; if it fails here, the
  zero-cost fallback is
  `rw [hasProdLocallyUniformlyOn_iff_tendstoLocallyUniformlyOn] at h`
  (UniformOn.lean:162, an `Iff.rfl`) and a direct application. **This
  obligation replaces the pool's §0 row 13** (`MultipliableLocallyUniformlyOn.
  differentiableOn`, absent): no such new lemma is needed, and this contract
  does not propose one.

---

### Block D — zero set and local order (the point of the package)

## W10. The complement split, tail analyticity, tail nonvanishing `[PIN]` — 3 signatures

### Statement

```lean
/-- Pointwise-global complement split of the product: for ANY index set `S` and
EVERY `z`. This is the re-derived replacement for the pool's missing
`HasProdLocallyUniformlyOn.mul_compl` (§1.4): no uniform content is needed for a
function identity. -/
theorem weierstrassProduct_eq_tprod_mul_tprod_compl (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) (S : Set ι) (z : ℂ) :
    weierstrassProduct p a z
      = (∏' i : S, weierstrassFactor p (z / a i))
          * ∏' i : ↥Sᶜ, weierstrassFactor p (z / a i)

/-- The complement tail is an entire function of `z` — a subfamily instantiation
of W9, not a new convergence argument. -/
lemma analyticAt_tprod_compl (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) (S : Set ι) (z : ℂ) :
    AnalyticAt ℂ (fun w ↦ ∏' i : ↥Sᶜ, weierstrassFactor p (w / a i)) z

/-- If no zero sits at `w`, the whole product is nonzero at `w`. Applied to the
complement of the fiber, this is the tail-nonvanishing input to W12. -/
lemma weierstrassProduct_ne_zero_of_forall_ne (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) {w : ℂ} (h : ∀ i, a i ≠ w) :
    weierstrassProduct p a w ≠ 0
```

### Proof skeleton

*Split.* At fixed `z`: `hnorm := summable_norm_weierstrassFactor_sub_one hane
hsum z` (W8). Restrict: `hnorm.subtype (· ∈ S)` and `hnorm.subtype (· ∈ Sᶜ)`
(**additive** `Summable.subtype`, S1W-SUB), then
`multipliable_one_add_of_summable` (Log/Summable.lean:169, root name,
`[CompleteSpace ℂ]`) after the `1 + (E - 1) = E` congr on each subfamily.
Finish with `(Multipliable.tprod_mul_tprod_compl hS hSc).symm`
(InfiniteSum/Basic.lean:752), unfolding `weierstrassProduct`.

*Tail analyticity.* The subfamily `a ∘ ((↑) : ↥Sᶜ → ι)` satisfies
`hane ∘` and `hsum.subtype _`; `weierstrassProduct p (a ∘ (↑))` is
**definitionally** the tail function; apply W9's
`analyticAt_weierstrassProduct` to it.

*Nonvanishing.* Factors: `1 + (E_p(w / a i) - 1) ≠ 0` since
`E_p(w / a i) = 0 ↔ w / a i = 1` (W3) `↔ w = a i` (`div_eq_one_iff_eq` with
`hane i`), excluded by `h i`. Then `tprod_one_add_ne_zero_of_summable`
(Log/Summable.lean:216) with the pointwise summability from W8, plus the same
`1 + (E - 1)` congr.

### Pinned dependencies (W10)

`Multipliable.tprod_mul_tprod_compl` —
`Topology/Algebra/InfiniteSum/Basic.lean:752` (verified verbatim, §0);
`Summable.subtype` — additive twin at
`Topology/Algebra/InfiniteSum/Group.lean:300`;
`multipliable_one_add_of_summable` — `Log/Summable.lean:169` (**root** name;
the `Complex.`- and `Real.`-namespaced homonyms at :49/:94 take `Summable f`,
not `Summable ‖f‖` — citing the wrong one costs a CI cycle);
`tprod_one_add_ne_zero_of_summable` — `Log/Summable.lean:216`;
`div_eq_one_iff_eq` (GroupWithZero core); W3, W8, W9.

### Obligations (W10)

- **S1W-SPLIT** (MEDIUM): three congr-seams of the same `1 + (E - 1)` shape
  (S1W-CONV's pointwise cousin). Each is `tprod_congr` + `add_sub_cancel`;
  none needs uniform convergence. The defeq claim in the tail-analyticity
  skeleton (`weierstrassProduct p (a ∘ (↑)) = fun w ↦ ∏' i : ↥Sᶜ, …`) is
  `rfl` by unfolding both `weierstrassProduct` and `Function.comp`; if the
  elaborator disagrees, `show` the unfolded form.
- **S1W-FILTER** (LOW-MEDIUM): the pin's `tprod` runs through the
  SummationFilter framework (`∏'` = `unconditional`, Defs.lean:158); :752 is
  stated in plain `∏'` form (verified, §0), so no `[L.LeAtTop]` juggling
  arises here — but any drive-by "generalize to `∏'[L]`" during review is out
  of scope for this package.

---

## W11. The zero set, exactly `[PIN]` — 1 signature

### Statement

```lean
/-- The zero set of the canonical product is exactly the zero family — on all
of ℂ. This is the statement Cotangent.lean structurally avoids by working on
`ℂ_ℤ`. -/
theorem weierstrassProduct_eq_zero_iff (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) {z : ℂ} :
    weierstrassProduct p a z = 0 ↔ ∃ i, a i = z
```

### Proof skeleton

(⇐) Given `a i₀ = z`: split at `S := {i₀}` (W10); the head factor
`∏' i : ({i₀} : Set ι), …` collapses (`tprod` over a `Unique` subtype;
`tprod_fintype`/`tprod_eq_mulSingle`) to `E_p(z / a i₀) = E_p 1 = 0` by W3 and
`div_self (hane i₀)`; `zero_mul`.
(⇒) Contrapositive: no `i` has `a i = z`; W10's third signature gives
`weierstrassProduct p a z ≠ 0`.

### Pinned dependencies (W11)

W3, W10; `tprod_fintype` — InfiniteSum/Basic.lean:481 (`[L.LeAtTop]` holds for
the default `unconditional` filter); `div_self` (GroupWithZero core).

### Obligations (W11)

- **S1W-SING** (LOW): the singleton-`tprod` collapse; two candidate pinned
  routes (`tprod_fintype` with `Fintype ({i₀} : Set ι)` vs
  `tprod_eq_mulSingle`, Basic.lean:495, which also carries `[L.LeAtTop]` —
  satisfied by the default `unconditional` filter). Either works; pick at build
  time. (Locator corrected from ":459 region" by Annex B item 2.)

---

## W12. Local order of the product `[PIN]`+`[GEN]` — 5 signatures — **the capstone (S1W-ORD)**

### Statement

```lean
/-- The elementary factor has a SIMPLE zero at `1`. -/
lemma analyticOrderAt_weierstrassFactor_one (p : ℕ) :
    analyticOrderAt (weierstrassFactor p) 1 = 1

/-- Transported along `z ↦ z / c`: the factor `E_p(· / c)` has a simple zero at `c`. -/
lemma analyticOrderAt_weierstrassFactor_div {p : ℕ} {c : ℂ} (hc : c ≠ 0) :
    analyticOrderAt (fun z ↦ weierstrassFactor p (z / c)) c = 1

/-- `[GEN]` Order is additive over finite products of analytic functions. Absent at
the pin AS A NAME in the analytic carrier (only the binary `analyticOrderAt_mul`,
Order.lean:497, exists there); a routine `Finset.cons_induction`. NOTE (Annex B
item 1): the MEROMORPHIC twin `meromorphicOrderAt_prod` IS pinned
(Meromorphic/Order.lean:437, with `meromorphicOrderAt_fun_prod` at :456 already
handling the `Finset.prod_apply` seam), and the carrier bridge
`AnalyticAt.meromorphicOrderAt_eq` (:279) transfers it — so this lemma is
derivable by transfer instead of fresh induction. Natural Mathlib upstream
either way. -/
lemma analyticOrderAt_finsetProd {ι : Type*} (s : Finset ι) {f : ι → ℂ → ℂ} {z₀ : ℂ}
    (hf : ∀ i ∈ s, AnalyticAt ℂ (f i) z₀) :
    analyticOrderAt (∏ i ∈ s, f i) z₀ = ∑ i ∈ s, analyticOrderAt (f i) z₀

/-- **Zero set with multiplicity, at every point of ℂ.** The local analytic order
of the canonical product at `w` is the number of indices sitting at `w`. This is
the statement whose absence the Euler sine development routes around; it is
stated with NO domain restriction and NO nontriviality side condition. -/
theorem analyticOrderAt_weierstrassProduct (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) (w : ℂ) :
    analyticOrderAt (weierstrassProduct p a) w = (Nat.card {i | a i = w} : ℕ∞)

/-- Non-degeneracy, explicit: the product is nowhere locally identically zero.
Makes the `⊤`-case impossibility a named fact instead of `untop₀` junk. -/
lemma analyticOrderAt_weierstrassProduct_ne_top (hane : ∀ i, a i ≠ 0)
    (hsum : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)) (w : ℂ) :
    analyticOrderAt (weierstrassProduct p a) w ≠ ⊤
```

### Proof skeleton

*Factor at `1`.* `weierstrassFactor p = (fun z ↦ 1 - z) * (fun z ↦ exp (…))`
(as a `Pi.mul`; `funext`-`rfl` seam, see S1W-PI below). `analyticOrderAt_mul`
(Order.lean:497; both factors ℂ-valued as its :488 variables require):
- left: `AnalyticAt.analyticOrderAt_eq_one_of_zero_deriv_ne_zero`
  (Order.lean:328) with value `1 - 1 = 0` and
  `deriv (fun z ↦ 1 - z) 1 = -1 ≠ 0` (`deriv_const_sub_id`, Deriv/Add.lean:449
  — the same lemma `MULTIPLICITY_CONTRACT.md` M2 leans on);
- right: order `0` by `AnalyticAt.analyticOrderAt_eq_zero` (Order.lean:133)
  and `Complex.exp_ne_zero` (Exponential.lean:160).
Total: `1 + 0 = 1`.

*Factor at `c`.* `(fun z ↦ E_p (z / c)) = weierstrassFactor p ∘ (· / c)`.
`analyticOrderAt_comp_of_deriv_ne_zero` (Order.lean:561;
`[CompleteSpace ℂ]`, `[CharZero ℂ]` are instances):
`hg : AnalyticAt ℂ (· / c) c` by `fun_prop`; `hg' : deriv (· / c) c = c⁻¹ ≠ 0`
via `deriv_div_const` (Deriv/Mul.lean:593) with `deriv id = 1` and
`inv_ne_zero hc`. The evaluation point transports to `c / c = 1`
(`div_self hc` — a beta-redex sits in the point argument; it is discharged by
`exact`-defeq, harmless per the M3 analysis, finding-A2 regime). Then the
factor-at-`1` lemma.

*Finset product.* `Finset.cons_induction`; empty case
`analyticOrderAt (1 : ℂ → ℂ) z₀ = 0` (the constant-one function is analytic
and nonvanishing — Order.lean:133 again); step case `analyticOrderAt_mul`,
whose second `AnalyticAt` argument (analyticity of the remaining partial
product) is closed by the pinned **`Finset.analyticAt_prod`** —
`Analysis/Analytic/Constructions.lean:1081`, re-read 2026-08-08:

```lean
@[fun_prop]
theorem Finset.analyticAt_prod {α : Type*} {A : Type*} [NormedCommRing A]
    [NormedAlgebra 𝕜 A] {f : α → E → A} {c : E} (N : Finset α)
    (h : ∀ n ∈ N, AnalyticAt 𝕜 (f n) c) : AnalyticAt 𝕜 (∏ n ∈ N, f n) c
```

`[NormedCommRing ℂ]` and `[NormedAlgebra ℂ ℂ]` both hold, and its conclusion is
already in the **Pi-product form `∏ n ∈ N, f n`** — the same shape
`analyticOrderAt_mul` consumes — so it pre-solves part of S1W-PI rather than
adding to it. Its `fun`-form twin `Finset.analyticAt_fun_prod` (:1073, also
`@[fun_prop]`, same hypotheses `(N : Finset α) (h : ∀ n ∈ N, AnalyticAt 𝕜
(f n) c)` — it simply takes `α` from the file's section variable instead of
re-binding it — and concluding `AnalyticAt 𝕜 (fun z ↦ ∏ n ∈ N, f n z) c`) is
available if the lambda shape is wanted instead.

**Correction, 2026-08-08.** The drafted "`AnalyticAt.finsetProd`-style closure"
named a lemma that **does not exist at the pin**. Grepping
`AnalyticAt\.finsetProd|AnalyticAt\.fun_finsetProd` over all of Mathlib returns
nothing, and `finsetProd` has zero hits anywhere under `Mathlib/Analysis/Analytic/`;
the only nearby real name is `AnalyticAt.prod`
(Constructions.lean:338), which is the **pair** product
`fun x ↦ (f x, g x) : E → F × G`, not a `Finset` product. A drafter who typed
the drafted name would have lost a CI round. `Finset.analyticAt_prod` **is**
reachable from the declared preamble: `Mathlib.Analysis.Analytic.Order`
imports `Mathlib.Analysis.Analytic.IsolatedZeros` (Order.lean:8), which
`public import`s `Mathlib.Analysis.Analytic.Constructions` (IsolatedZeros.lean:8).
`Finset.prod_fn` + `fun_prop` remains available as the fallback.

*Capstone.* Fix `w`. `S := {i | a i = w}`, `hS : S.Finite := finite_setOf_apply_eq
hane hsum w` (W7); `haveI := hS.fintype`.
1. Split (W10, first signature) at `S`, as a **function** identity via
   `funext`:
   `weierstrassProduct p a = F * T` where
   `F := fun z ↦ ∏' i : S, E_p (z / a i)`, `T := fun z ↦ ∏' i : ↥Sᶜ, E_p (z / a i)`.
2. `F` collapses to a `Finset.prod` (`tprod_fintype`, Basic.lean:481):
   `F = fun z ↦ ∏ i ∈ hS.toFinset, E_p (z / a i)` (attach/`toFinset`
   bookkeeping).
3. `analyticOrderAt_mul` at `w`. `F` analytic: finite product of W2 factors,
   closed by **`Finset.analyticAt_prod`** (Analysis/Analytic/Constructions.lean:1081
   — locator supplied 2026-08-08; the drafted `AnalyticAt.finsetProd` does not
   exist at the pin, see the *Finset product* paragraph above), whose
   `∏ n ∈ N, f n` conclusion is already the Pi-product shape
   `analyticOrderAt_mul` consumes. `T` analytic: W10 second signature.
4. `analyticOrderAt F w = ∑ i ∈ hS.toFinset, 1 = hS.toFinset.card` by
   `analyticOrderAt_finsetProd` + the factor-at-`c` lemma (each `i ∈ S` has
   `a i = w`, `hane i`), then `hS.toFinset.card = Nat.card {i | a i = w}`
   (`Nat.card_coe_set_eq`, Data/Set/Card.lean:642, then
   **`Set.ncard_eq_toFinset_card`, Data/Set/Card.lean:644** — the name
   `Nat.card_eq_toFinset_card'` cited in draft v1 does not exist at the pin
   (Annex B item 2), and the primed `Set.ncard_eq_toFinset_card'` at :649
   cited by v1.2 is the **wrong one of the pair**: corrected 2026-08-08.

   The pair, both re-read at the pin:
   `theorem ncard_eq_toFinset_card (s : Set α) (hs : s.Finite := by toFinite_tac) :
   s.ncard = hs.toFinset.card` (:644) is about `Set.Finite.toFinset` — which is
   exactly what this skeleton builds, from `hS : S.Finite`; whereas
   `theorem ncard_eq_toFinset_card' (s : Set α) [Fintype s] : s.ncard =
   s.toFinset.card` (:649) is about the `Fintype`-based `Set.toFinset`.
   `Nat.card_coe_set_eq` (:642,
   `@[simp] theorem _root_.Nat.card_coe_set_eq (s : Set α) : Nat.card s =
   s.ncard := rfl`) was cited correctly and is unchanged.

   **The 2026-08-08 rationale for that swap is refuted (2026-08-09); the
   citation stands, the reasoning does not.** It claimed that citing :644
   "removes" a `Set.Finite.toFinset_eq_toFinset` hop from S1W-ORD. It relocates
   it. Three reasons, all against this skeleton's own text:

   - This skeleton is *already* on the `Fintype` route. Step 2 uses
     `tprod_fintype`, which needs `Fintype ↥S`, which is why
     `haveI := hS.fintype` sits in the capstone's opening line. The
     "alternative route" the old text relegated to a footnote is the route in
     force one step earlier.
   - `tprod_fintype` produces `∏ b : ↥S, …`, i.e. `Finset.univ` over the
     subtype — not a `toFinset` term at all. The lemma that lands on a
     `Finset ι` is `Finset.prod_set_coe (s : Set ι) [Fintype s] :
     (∏ i : s, f i) = ∏ i ∈ s.toFinset, f i`
     (`Algebra/BigOperators/Group/Finset/Basic.lean:469`), whose output is
     `s.toFinset` — the **primed** :649's subject. That lemma is the
     "attach/`toFinset` bookkeeping" hand-wave in step 2 and appears nowhere
     else in this contract; it belongs in the dependency table.
   - `haveI` (not `letI`) is what makes the hop unavoidable in either
     direction. `Set.Finite.toFinset h` is definitionally
     `@Set.toFinset _ _ h.fintype`, but `haveI` introduces an **opaque** fvar
     instance, so `S.toFinset` and `hS.toFinset` are not `rfl`-equal and closing
     the gap needs `Subsingleton.elim` — i.e. exactly
     `Set.Finite.toFinset_eq_toFinset`, which does exist under that name at
     `Data/Set/Finite/Basic.lean:78`. **Changing the opening line to
     `letI := hS.fintype` deletes the hop for real**; a citation swap cannot.

     The `haveI`/`letI` distinction is Lean's own, not a folk belief:
     `Lean/Elab/Binders.lean:957-961` shows both set `zeta := true` and differ
     only in `nondep`, and `Lean/LocalContext.lean:59-61` says in as many words
     that a `nondep := false` let-bound variable "is definitionally equal to its
     value" while `nondep := true` gives "an opaque value". Under `letI` the two
     `toFinset` terms become syntactically identical after zeta-delta, so
     nothing has to reduce `Classical.choice` and
     `Finite.fintype`'s `@[implicit_reducible]` (`Finite/Basic.lean:70`) cannot
     block it.

     Three caveats to carry with the `letI` advice, all verified 2026-08-09:
     `Set.Finite.toFinset` (:75) is a plain semireducible `def`, so the defeq
     needs **default** transparency — anything running `withReducible`, notably
     `gcongr`'s forward discharger (`Core.lean:476`), will not see it;
     `simp`'s `zetaDelta` defaults to **false**, so `simp` will not inline the
     `letI` value without `(config := { zetaDelta := true })`, a `show`, or a
     `rfl` step; and `letI` changes what `revert`/`generalize` see, since
     `LocalContext.lean:64-73` deliberately treats nondep let-decls like
     `cdecl`s and dependent ones differently.

   **A shorter chain exists that needs neither lemma, and it is the one to
   prefer.** With the `Fintype` instance already in scope,
   `∑ i : ↥S, 1 = Fintype.card ↥S` goes to `S.ncard` by
   `Set.fintypeCard_eq_ncard` (`Data/Set/Card.lean:655`, `@[simp]`), and
   `Nat.card_coe_set_eq` (:642, `@[simp]`, `rfl`) meets it there.

   **Read the next three paragraphs before using that sentence.** A first
   version of it, written 2026-08-09, said the chain "goes on to `Nat.card ↥S`"
   and that "both are `@[simp]`, so `simp` closes the card chain outright". An
   adversarial verifier refuted it the same day. It is corrected here rather
   than deleted, because the route is real and useful once stated properly.

   - **Direction.** `Nat.card_coe_set_eq` is `Nat.card ↥s = s.ncard`, so as a
     `@[simp]` lemma it rewrites `Nat.card` **into** `ncard`. Nothing at the pin
     rewrites `ncard` back. The chain does not continue to `Nat.card ↥S`; both
     sides of the goal normalise INTO `S.ncard` and meet there. Invisible to
     `simp`, fatal to any explicit `calc` or `rw` written the other way.
   - **The head of the chain is three more lemmas, not zero.**
     `∑ i : ↥S, 1 = Fintype.card ↥S` is done by none of the two cited: it needs
     `Finset.sum_const` (`Algebra/BigOperators/Group/Finset/Basic.lean:629`,
     `@[to_additive (attr := simp)]` on :628), then `nsmul_eq_mul`
     (`Algebra/Ring/Defs.lean:188`, `@[simp]` — legal at `ℕ∞` only because
     `CommSemiring` is derived at `Data/ENat/Basic.lean:44-50`) and `mul_one`,
     then `Finset.card_univ` (`Data/Fintype/Card.lean:104`, `@[simp]`). Five
     simp lemmas in total. The route is still `simp`-closable; the contract had
     simply not shown it.
   - **The route constrains step 2, and the earlier text contradicted itself.**
     It works on the subtype shape `∑ i : ↥S, (1 : ℕ∞)`, i.e. only if step 2
     stops at `tprod_fintype` and `Finset.prod_set_coe` is NOT applied. If step
     2 keeps `Finset.prod_set_coe` and step 4 stays on `∑ i ∈ hS.toFinset, 1`,
     **`simp` does not close the chain**: `Set.Finite.card_toFinset`
     (`Data/Set/Finite/Basic.lean:813`), `Set.ncard_eq_toFinset_card` (:644) and
     `Set.Finite.toFinset_eq_toFinset` (`Finite/Basic.lean:78`) are all
     non-simp, and `Set.toFinite_toFinset` (:83, `@[simp]` on :82) matches only
     the literal proof term `s.toFinite`. **Pick one route in step 2 and make step 4 match it.**
     Boasting that "no `Finset ι` ever appears" while step 2 was amended to
     route through `Finset.prod_set_coe` — whose output is a `Finset ι` — was
     the contradiction.

   Also: the sum lives in `ℕ∞` (`analyticOrderAt : ℕ∞`,
   `Analysis/Analytic/Order.lean:47`) while `Fintype.card ↥S : ℕ`, so the
   equation carries a `Nat.cast` throughout. Keep :644 and :649 as explicit
   fallbacks. :655 is absent from the dependency table and belongs there — note
   its `s` is **explicit**, via `variable (s) in` at :653.

   One further trap in :644 that the skeleton must not walk into: its
   finiteness argument is an autoparam, `(hs : s.Finite := by toFinite_tac)`.
   Writing `Set.ncard_eq_toFinset_card S` with the argument omitted fires
   `toFinite_tac`, which cannot discharge `{i | a i = w}.Finite`. Pass `hS`
   explicitly.
5. `analyticOrderAt T w = 0` by Order.lean:133 with `T w ≠ 0` (W10 third
   signature applied to the subfamily, whose members all have `a i ≠ w` by
   construction).
6. `|S| + 0 = |S|`, with the `ℕ∞`-cast of the `Finset.sum` of ones
   (`Finset.sum_const`, `nsmul_eq_mul`, `Nat.cast` discipline).

*Ne-top.* Immediate from the capstone: `(Nat.card _ : ℕ∞) ≠ ⊤`
(`ENat.coe_ne_top` / `WithTop.natCast_ne_top`).

### Pinned dependencies (W12)

`analyticOrderAt_mul` — Order.lean:497 (section variables :488 fix both
factors as `𝕜 → 𝕜`); `AnalyticAt.analyticOrderAt_eq_one_of_zero_deriv_ne_zero`
— Order.lean:328; `AnalyticAt.analyticOrderAt_eq_zero` — Order.lean:133;
`analyticOrderAt_comp_of_deriv_ne_zero` — Order.lean:561;
`analyticOrderAt_congr` — Order.lean:175 (available fallback if step 1 is run
as an eventual rather than global identity); `deriv_const_sub_id` —
Deriv/Add.lean:449; `deriv_div_const` — Deriv/Mul.lean:593; `tprod_fintype` —
Basic.lean:481; `Complex.exp_ne_zero` — Exponential.lean:160;
**`Finset.analyticAt_prod` — Analysis/Analytic/Constructions.lean:1081**
(`@[fun_prop]`; `N` explicit, `f`/`c` implicit; conclusion in Pi-product form
`∏ n ∈ N, f n`) and its lambda twin **`Finset.analyticAt_fun_prod` — :1073**
(conclusion `fun z ↦ ∏ n ∈ N, f n z`) — **both added 2026-08-08**, replacing
the phantom `AnalyticAt.finsetProd`; `Set.ncard_eq_toFinset_card` —
Data/Set/Card.lean:644 (the `Set.Finite.toFinset` form; :649 is the
`Fintype`/`Set.toFinset` alternative) and `Nat.card_coe_set_eq` — :642;
W2, W3, W7, W10.

**Added 2026-08-09** — four pinned names the capstone's own steps use or should
prefer, none of which was listed:

- `Set.fintypeCard_eq_ncard` — `Data/Set/Card.lean:655`, `@[simp]`,
  `Fintype.card s = s.ncard`. With :642 it closes the whole card chain by
  `simp`, so step 4 need touch neither :644 nor :649. This is now the preferred
  route.
- `Finset.prod_set_coe` — `Algebra/BigOperators/Group/Finset/Basic.lean:469`,
  `(s : Set ι) [Fintype s] : (∏ i : s, f i) = ∏ i ∈ s.toFinset, f i`. This is
  the lemma step 2's "attach/`toFinset` bookkeeping" actually needs; it lands on
  the `Fintype`-based `s.toFinset`, which is why the :644-vs-:649 argument above
  had the seam in the wrong place.
- `Set.Finite.toFinset_eq_toFinset` — `Data/Set/Finite/Basic.lean:78`,
  `{s : Set α} [Fintype s] (h : s.Finite) : h.toFinset = s.toFinset`. Needed
  whenever the two `toFinset`s meet under `haveI`; unnecessary under `letI`.
- `analyticAt_finprod` — `Analysis/Analytic/Constructions.lean:1113`,
  `@[fun_prop]` on :1112, root-level (**not** in the `Finset` namespace),
  hypothesis `∀ a` and conclusion on `∏ᶠ n, f n`. An alternative to step 3 that
  skips the `Set.Finite.toFinset` machinery entirely; the pin's own proof of it
  (:1116–:1119) shows the `finprod_eq_prod` / `Finset.analyticAt_prod` pattern.

The `Finset`-product analyticity family is eight lemmas, not two —
Constructions.lean :1051, :1065, :1073, :1081, :1088, :1094, :1100, :1106 —
covering `AnalyticWithinAt`, `AnalyticAt`, `AnalyticOn` and `AnalyticOnNhd` in
Pi and `_fun_` form. `Finset.analyticOnNhd_prod` (:1106) is the natural partner
for W9, which already lands in `AnalyticOnNhd` via
`Complex.analyticOnNhd_univ_iff_differentiable`.

Two precision notes on the 2026-08-08 additions. :1073 does not re-bind
`{α : Type*}` — it inherits `α` from the file-level `variable` at :31, so the
two are not textually "the same binders" even though the effective binder sets
match. And neither quote shows the ambient
`{𝕜} [NontriviallyNormedField 𝕜] {E} [NormedAddCommGroup E] [NormedSpace 𝕜 E]`
from :32–:33, all discharged by instance for ℂ. Also note the binder asymmetry
across the seam: `Finset.analyticAt_prod` takes `(N : Finset α)` **explicit**,
while `meromorphicOrderAt_prod` takes `{s : Finset ι}` **implicit**. The `[GEN]`
lemma follows the analytic side; a `_fun_` twin mirrored from
Meromorphic/Order.lean:456 would import the implicit convention and clash with
its own Pi-form sibling.

**Meromorphic-carrier fallback route (Annex B item 1, pinned):**
`meromorphicOrderAt_prod` — Meromorphic/Order.lean:437;
`meromorphicOrderAt_fun_prod` — Meromorphic/Order.lean:456;
`meromorphicOrderAt_mul` — Meromorphic/Order.lean (binary, above :437);
`AnalyticAt.meromorphicOrderAt_eq` — Meromorphic/Order.lean:279
(`meromorphicOrderAt f x = (analyticOrderAt f x).map (↑)`);
`MeromorphicAt.prod` — Meromorphic/Basic.lean:109. If the `ℕ∞` assembly of
S1W-ORD seizes up, steps 3–6 can be run in `WithTop ℤ` via the bridge and
transferred back once (injectivity of `ENat.map (↑· : ℕ → ℤ)` plus the `≠ ⊤`
companion signature). This changes no statement in W12; it is proof-route
insurance only. **Transfer-route completion (Annex C item 3, verified this
session): the injectivity/distribution steps the v1.1 text left unnamed are
themselves pinned** — `ENat.map_natCast_injective` (Data/ENat/Basic.lean:546;
its section needs `[AddMonoidWithOne α] [PartialOrder α] [AddLeftMono α]
[ZeroLEOneClass α] [CharZero α]`, all instances for α = ℤ), the `@[simp]` iff
form `ENat.map_natCast_inj` (:548), and `ENat.map_add` (:557, for
`AddHomClass F ℕ β` casts) to push `ENat.map` through the finite sum. Route (b)
of S1W-GEN is thus locator-complete end to end.

### Obligations (W12)

- **S1W-ORD** (HIGH) — **the named hardest obligation of this contract.** The
  capstone assembly, steps 1–6. Zero new analysis, six seams: the
  `funext`-lift of the pointwise split; the `tprod_fintype`/`toFinset`
  conversion under the SummationFilter framework; the `Pi.mul` vs
  `fun z ↦ F z * T z` defeq for `analyticOrderAt_mul` (whose statement is
  about `f * g`, not a lambda — the M-contract's finding-A2 discipline
  applies: `show`/`simp only`, never bare `rw` at a redex); the subtype
  fiber-to-`Nat.card` cast chain; the `ℕ∞` sum arithmetic; and the subfamily
  re-instantiation in step 5. Priced at the pool's Tier-4 "weeks" **minus**
  the phantom missing lemma: everything consumed is pinned or W1–W11.
  Fallback landscape: if the global function identity in step 1 resists
  `funext`, `analyticOrderAt_congr` (Order.lean:175) needs it only on a
  neighborhood filter, which the same pointwise argument supplies.
- **S1W-PI** (MEDIUM): the recurring `Pi.mul`/`Finset.prod_apply`/beta seams,
  isolated here because W12 hits all of them at once.

  **Partly pre-solved, partly still open — mapped 2026-08-08.** Pre-solved:
  `Finset.analyticAt_prod` (Constructions.lean:1081) delivers analyticity
  directly in the Pi-product form `∏ n ∈ N, f n` that `analyticOrderAt_mul`
  consumes, so the *analyticity* half of the seam needs no `Finset.prod_apply`
  hop. Still open: the `[GEN]` lemma `analyticOrderAt_finsetProd` is stated
  here in the Pi form `analyticOrderAt (∏ i ∈ s, f i) z₀`, while its capstone
  use site is the lambda `F = fun z ↦ ∏ i ∈ hS.toFinset, weierstrassFactor p
  (z / a i)`; bridging those is a `Finset.prod_apply` step inside S1W-ORD.

  Note what the pin does at exactly this seam: it ships **both** forms.
  `meromorphicOrderAt_prod` (Meromorphic/Order.lean:437) is paired with
  `meromorphicOrderAt_fun_prod` (:456, whose entire proof is
  `convert! meromorphicOrderAt_prod hf; exact (Finset.prod_apply _ s f).symm`),
  and `Finset.analyticAt_prod` (:1081) with `Finset.analyticAt_fun_prod`
  (:1073). Adding a matching `analyticOrderAt_fun_finsetProd` would close this
  seam where the pin chose to close it — **but that would be a 29th public
  signature, and adding one is a change to the accepted statement surface, so
  it is deliberately NOT done here.** It returns the surface to contract
  review; a stage-two builder who wants it must go that way, not add it in
  passing. Until then the `Finset.prod_apply` hop stays inside S1W-ORD, and
  `meromorphicOrderAt_fun_prod`'s two-line proof is the template for it.
- **S1W-GEN** (LOW): `analyticOrderAt_finsetProd` is the package's one `[GEN]`
  lemma; it has no ℂ-specific content and should be stated over
  `[NontriviallyNormedField 𝕜]` at build time if the induction goes through
  verbatim — contract states it over ℂ to keep the surface minimal, and
  widening is a permitted stage-two strengthening (not a statement change for
  consumers). Risk further reduced by Annex B item 1: the pinned
  `meromorphicOrderAt_prod` (Meromorphic/Order.lean:437) +
  `AnalyticAt.meromorphicOrderAt_eq` (:279) give a derivation by transfer if
  the direct induction misbehaves; `meromorphicOrderAt_prod`'s own proof
  (`Finset.induction` + binary `meromorphicOrderAt_mul` + `MeromorphicAt.prod`)
  is the in-tree template for the direct induction as well.

  **The transfer route is not free — priced 2026-08-09.**
  `AnalyticAt.meromorphicOrderAt_eq` (Order.lean:279, verified: the declaration
  is on :279 and its statement on :280) reads
  `meromorphicOrderAt f x = (analyticOrderAt f x).map (↑)`, so the transfer
  lands in `WithTop ℤ`, not `ℕ∞`. Recovering the `ℕ∞` equation needs
  injectivity of that map plus its commutation with `Finset.sum`. Modest work,
  but real, and it is not what "derivation by transfer" sounds like. Keep the
  route as a fallback, not as a cheaper primary.

  **The gap the `[GEN]` lemma fills is genuine, re-checked at master.** No
  `analyticOrderAt` Finset-product lemma exists anywhere in pinned Mathlib —
  `grep` for `analyticOrder` intersected with any product token returns zero
  lines across the whole tree, and all 54 `analyticOrder*` declarations live in
  the single file `Analysis/Analytic/Order.lean`, whose multiplicative family
  stops at binary `mul` and `pow`. That file also adopts no `_fun_` convention
  at all (`@[to_fun]` has zero hits in it), which is why finding 2's phrase "the
  pin ships both forms at exactly this seam" is locatively wrong even though its
  inference from four neighbouring files is sound. Two months of upstream work
  since the pin have not closed the gap either — see
  `UPSTREAM_DUPLICATION_CHECK_2026_08_09.md`.

- **S1W-SHADOW** (LOW, opened 2026-08-08): `analyticOrderAt_finsetProd` is the
  only signature in the package whose binder collides with the shared block.
  It re-binds `{ι : Type*}`, which §1.2 already declares as a section variable
  (`variable {ι : Type*} {p : ℕ} {a : ι → ℂ}`) that every other W7–W12
  signature relies on. This is not a truth defect — the statement is true for
  any index type, and it is the one signature in the block that is not about
  the family `a` — but shadowing a section variable inside one declaration of
  the same block is confusing to read and is the kind of thing that changes
  which variables get auto-included.

  **Resolution under the no-signature-change rule:** the signature stands
  exactly as written. At stage two, state this one `[GEN]` lemma in its **own
  `section`, opened before the §1.2 `variable` block and closed after the
  lemma**, so that the local `{ι : Type*}` binds in an empty ambient context
  and shadows nothing. That is a file-layout decision, not a statement change,
  and it leaves the signature character-identical. The alternative repair —
  renaming the local index type to `{κ : Type*}` — **would be a signature
  change and is therefore out of scope here**; it returns the surface to
  contract review and must not be applied in passing. (For context, the pin's
  own analogue `meromorphicOrderAt_prod`, Meromorphic/Order.lean:437, likewise
  binds `{ι : Type*}` locally; the issue here is the collision with §1.2, not
  the binder itself.)

---

## Pinned API dependencies table

| Symbol | Locator (pin) | Consumed by | Re-verified |
|---|---|---|---|
| `Complex.logTaylor` | LogBounds.lean:68 (`noncomputable def`) | W4 | yes (text) |
| `Complex.norm_log_one_sub_inv_add_logTaylor_neg_le` | LogBounds.lean:231 | W5 | yes (verbatim) |
| `Complex.log_inv` | Log.lean:137 | W5 | yes (verbatim) |
| `Complex.exp_log` | Log.lean:41 | W4 | yes (verbatim) |
| `Complex.mem_slitPlane_of_norm_lt_one` | Analysis/Complex/Basic.lean:689 | W5 | yes (verbatim) |
| `Complex.slitPlane_arg_ne_pi` | Arg.lean:544 | W5 | yes (verbatim) |
| `Complex.norm_exp_sub_one_le` | Exponential.lean:439 | W6 | yes (verbatim) |
| `Complex.exp_ne_zero` | Exponential.lean:160 | W3, W12 | yes |
| `Complex.differentiable_exp` | ExpDeriv.lean:97 | W2 | yes |
| `HasProdUniformlyOn` | UniformOn.lean:44 | W8 | yes (verbatim) |
| `HasProdLocallyUniformlyOn` (defeq `TendstoLocallyUniformlyOn`) | UniformOn.lean:152 | W8, W9 | yes (verbatim) |
| `hasProdLocallyUniformlyOn_of_forall_compact` | UniformOn.lean:196 | W8 | yes (verbatim) |
| `HasProdUniformlyOn.congr` / `.congr_right` | UniformOn.lean:73 / :80 | W8 | yes (headers) |
| `Summable.hasProdUniformlyOn_one_add` | MultipliableUniformlyOn.lean:87 | W8 | yes (verbatim) |
| `Summable.hasProdLocallyUniformlyOn_one_add` | MultipliableUniformlyOn.lean:130 | (route B only) | yes (verbatim) |
| `TendstoLocallyUniformlyOn.differentiableOn` | LocallyUniformLimit.lean:135 | W9 | yes (verbatim) |
| `Filter.atTop_neBot` | AtTopBot/Basic.lean:66 | W9 | yes |
| `DifferentiableOn.finsetProd` | Deriv/Mul.lean:530 | W9 | yes |
| `Finset.prod_fn` | BigOperators/Pi.lean:51 | W9, W12 | yes |
| `multipliable_one_add_of_summable` (root) | Log/Summable.lean:169 | W10 | yes (verbatim) |
| `tprod_one_add_ne_zero_of_summable` | Log/Summable.lean:216 | W10 | yes (verbatim) |
| `Multipliable.tprod_mul_tprod_compl` | InfiniteSum/Basic.lean:752 | W10 | yes (verbatim) |
| `Summable.subtype` (additive twin) | InfiniteSum/Group.lean:300 | W10 | yes (attr checked) |
| `Summable.tendsto_cofinite_zero` (additive twin) | InfiniteSum/Group.lean:365 | W7 | yes (attr checked) |
| `tprod_fintype` | InfiniteSum/Basic.lean:481 | W11, W12 | yes (verbatim) |
| `tprod_congr` | InfiniteSum/Basic.lean:471 | W8, W10 | yes (verbatim) |
| `analyticOrderAt` | Order.lean:47 | W12 | yes |
| `AnalyticAt.analyticOrderAt_eq_zero` | Order.lean:133 | W12 | yes (verbatim) |
| `analyticOrderAt_congr` | Order.lean:175 | W12 (fallback) | yes (verbatim) |
| `AnalyticAt.analyticOrderAt_eq_one_of_zero_deriv_ne_zero` | Order.lean:328 | W12 | yes (verbatim) |
| `analyticOrderAt_mul` | Order.lean:497 | W12 | yes (verbatim, incl. :488 vars) |
| `analyticOrderAt_comp_of_deriv_ne_zero` | Order.lean:561 | W12 | yes (verbatim) |
| `deriv_const_sub_id` | Deriv/Add.lean:449 | W12 | yes |
| `deriv_div_const` | Deriv/Mul.lean:593 | W12 | yes (verbatim) |
| `Complex.analyticOnNhd_univ_iff_differentiable` | CauchyIntegral.lean:678 | W2, W9 | yes |
| `Finset.analyticAt_prod` (Pi form `∏ n ∈ N, f n`) | Analytic/Constructions.lean:1081 | W12 | yes (verbatim, 2026-08-08) |
| `Finset.analyticAt_fun_prod` (lambda form) | Analytic/Constructions.lean:1073 | W12 (alternative) | yes (verbatim, 2026-08-08) |
| `Nat.card_coe_set_eq` | Data/Set/Card.lean:642 | W12 | yes (verbatim, 2026-08-08) |
| `Set.ncard_eq_toFinset_card` (`Set.Finite.toFinset` form) | Data/Set/Card.lean:644 | W12 | yes (verbatim, 2026-08-08) |
| `Set.ncard_eq_toFinset_card'` (`Fintype`/`Set.toFinset` form) | Data/Set/Card.lean:649 | W12 (alternative route only) | yes (verbatim, 2026-08-08) |
| Euler sine template | Cotangent.lean:78–:135 | W8 pattern | yes (read in full; :105 is `private`) |
| Product-differentiable template | DedekindEta.lean:88–:93 | W9 pattern | yes (verbatim; range corrected 2026-08-08) |

---

## Obligation register

### Where the real risk sits — read this before the table (added 2026-08-08)

The table below ranks the *statement surface's* difficulty. The stage-one
acceptance of 2026-08-08 found the difficulty is not distributed the way the
table implies, and the finding density is the evidence: of the twenty-four
non-blocking findings, **thirteen came from the pin-fidelity lens alone — the
largest crop of any contract reviewed in this programme — and they cluster in
the `W12` proof skeleton and in `§0`'s quoted interface.** Not one landed on a
signature; no lens asked for a signature change.

Read that pattern for what it is: **the statement surface is the sound part of
this document, and the PROOF PLAN is the least-verified part** — the opposite
of where this register puts the difficulty. Three of the thirteen were outright
wrong names or wrong lemmas that a drafter would have typed and lost a CI round
to (`AnalyticAt.finsetProd`, which does not exist; the primed
`Set.ncard_eq_toFinset_card'`, which is the wrong half of a pair; the `private`
`sineTerm_bound_aux`, listed under a heading reading "Pinned dependencies").
Three more were predicted tactic failures in skeletons written as if they would
just work (`gcongr` across a `/`-vs-`*` node mismatch in W8 step 3 and in W6
step 5; the `▸`-chain in W5). All are corrected in place above.

What a next drafter should therefore prepare for: **the skeletons are drafts,
not verified routes.** Every one of them is a source-shape judgement made with
no Lean toolchain in the container; the kernel has never seen any of it. Budget
the `W12` capstone and the `§0`-quoted seams as the places where surprises
live, treat each named locator as load-bearing and re-open it, and expect the
seam work — not the analysis — to consume the round. The severity column is
unchanged by this note; what changes is where a reader should look first.

| ID | Severity | Attaches to | One-line content |
|---|---|---|---|
| **S1W-ORD** | **HIGH — hardest in package** | W12 | capstone assembly: split → `tprod_fintype` → `analyticOrderAt_mul`/`finsetProd` → `Nat.card` cast chain. Annex C's re-pricing is an **estimate, not a finding**: estimated days of seam work rather than the pool's Tier-4 "weeks", from two untrusted drafting passes plus one re-verification, with **no kernel and no elaboration**. Severity stays HIGH precisely because it is unverified |
| S1W-CONV | MEDIUM-HIGH | W8 | the `1 + (E - 1) = E` congr on family and limit slots |
| S1W-SPLIT | MEDIUM | W10 | three pointwise congr-seams + subfamily-defeq |
| S1W-PI | MEDIUM | W12 | `Pi.mul` / `Finset.prod_apply` / beta seams |
| S1W-LOG | LOW | W5 | `-a + -b` merge (▸ risk refuted 2026-08-09) |
| S1W-EST | MEDIUM | W6 | ℝ-cast arithmetic; bare `gcongr` emits a FALSE goal |
| S1W-INV | MEDIUM | W7 | inverse-power comparison bookkeeping |
| S1W-4a | MEDIUM | W4 | `logTaylor` junk-term absorption + reindex |
| S1W-DIFF | LOW-MEDIUM | W9 | dot-notation defeq unfolding (precedented) |
| S1W-FILTER | LOW-MEDIUM | W10, W11 | SummationFilter (`unconditional`) hygiene |
| S1W-SUB | LOW | W7, W10 | additive-only `Summable.subtype` discipline (ℂ-under-× is no `CommGroup`) |
| S1W-GEN | LOW | W12 | `analyticOrderAt_finsetProd` induction; widening to `𝕜` permitted |
| S1W-SING | LOW | W11 | singleton-`tprod` collapse route choice |
| S1W-RAD | **MEDIUM** (raised 2026-08-08) | W8 | radius arithmetic **plus** the `div`-vs-`mul` normalization that must precede `gcongr` in step 3 |
| S1W-SHADOW | LOW (opened 2026-08-08) | W12 | `analyticOrderAt_finsetProd` re-binds `{ι : Type*}` over the §1.2 section variable; resolve by giving it its own `section` at build time, **not** by renaming the binder |
| S1W-1/2/3/4b | LOW | W1–W4 | naming, `fun_prop` reach, orientation glue |

### Deferred items (explicitly out of this package)

- **DEFERRED-W1**: the Weierstrass product **theorem** (diagonal genus
  `E_n(z / a n)`, hypothesis-free existence with prescribed orders — the
  pool's `exists_differentiable_analyticOrderAt_eq`). Different statement,
  different majorant scheme; nothing in W1–W12 needs it.
- **DEFERRED-W2**: any `MeromorphicOn.divisor` statement for
  `weierstrassProduct`. One bridge lemma away
  (`MeromorphicOn.AnalyticOnNhd.divisor_apply`, Divisor.lean:71) but it is the
  multiplicity contract's carrier decision, not this one's.
- **DEFERRED-W3**: the sharp `‖1 - E_p z‖ ≤ ‖z‖^(p+1)` on the closed unit
  disc (Rudin RCA 15.8; pool Tier 5). Not required by anything here.
- **DEFERRED-W4**: `HasProdLocallyUniformlyOn.mul_compl` itself. §1.4 shows
  this package does not need it; if some later consumer does, it should be
  proposed upstream on its own merits, not smuggled in here. **Strengthened by
  Annex C item 2 (negative result, verified this session):** the pin's only
  one-hypothesis complement split,
  `Multipliable.tprod_subtype_mul_tprod_subtype_compl`
  (Topology/Algebra/InfiniteSum/Group.lean:310), sits inside `section
  IsTopologicalGroup` under `variable [CommGroup α]` (Group.lean:32) — unusable
  for ℂ-under-×. The two-multipliability form at Basic.lean:752 is therefore
  genuinely the minimal pinned tool for W10's split, and the S1W-SUB
  additive-only discipline is necessary, not stylistic.

---

## Claim boundary

1. **Generic only.** Every hypothesis and conclusion in W1–W12 is about an
   arbitrary `p : ℕ` and `a : ι → ℂ` over an arbitrary type `ι`. The package
   consumes **nothing zeta-specific**: no `riemannZeta`, no `riemannXi`, no
   repo-local theorem, no nontrivial-zero fact, no functional equation.
2. **No enumeration.** No statement introduces, requires, or produces an
   enumeration, ordering, or counting of anything — least of all of zeta
   zeros. `ι` carries no `Countable`/`Encodable` instance anywhere.
3. **`S1-GROWTH` untouched.** No growth order, no `maxModulus`, no vertical
   or order-one bound, no Hadamard-type genus selection appears in any
   signature or any skeleton (`MATHLIB_CAPABILITY_MAP.md:388` row unchanged).
4. **No barrier closes.** Generic pinned-Mathlib-shaped machinery lowers the
   cost of a future exit but never retires a capability row
   (`MULTIPLICITY_CONTRACT.md` finding A4 / death condition 9 regime).
   `S1-GLOBAL-ZEROS` (`:387`, whose *blocks* column names "canonical product")
   and `S1-GROWTH` (`:388`) remain OPEN and are not re-scoped by this document.

   (**Corrected 2026-08-08.** The earlier text paired `S1-GLOBAL-ZEROS` with
   `S1-MULTIPLICITY` (`:386`) as also OPEN. `S1-MULTIPLICITY` was **CLOSED
   2026-08-07** by merged PR #313 (`2a20629`) —
   `MATHLIB_CAPABILITY_MAP.md:626` "Addendum 2026-08-07 (sixth): barriers
   `S1-MULTIPLICITY` and `S1-CONJ` CLOSED", :638 "This closes
   `S1-MULTIPLICITY`" — and the RH queue's dated decision agrees at
   `tasks/RIEMANN_HYPOTHESIS.md:42-44`. The severity-table row this contract
   cited at `:386` still reads "OPEN" and is **stale relative to its own
   file's addendum**; that is a defect in the capability map's table, not
   something this package may fix — declaring a row stale on the strength of
   this generic package is death condition 9. The error direction was
   conservative — it understated repository progress rather than claiming
   credit — but a stage-one acceptance must not ratify a status refuted by
   merged evidence. This package bears on neither barrier.)

   **In particular, `hsum` is a HYPOTHESIS on a generic family, not evidence.**
   W7's `Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1)` and its consequences
   (`eventually_cofinite_le_norm`, `finite_setOf_apply_eq`) have the same
   *shape* as two named items in the `S1-GLOBAL-ZEROS` exit-evidence column
   (`MATHLIB_CAPABILITY_MAP.md:387`: "finite divisor sums, weighted
   summability, …"), and a later reader wanting to claim partial progress will
   reach for W7 first. They must not. W7 establishes no weighted-summability
   fact about the zeros of any specific function, produces no divisor sum, and
   fixes no height cutoff — neither `|ρ| ≤ T` (Li) nor `|Im ρ| < T` (Weil),
   the two the row distinguishes. The exit-evidence column is untouched item by
   item.
5. **No RH-truth claim.** Nothing here is evidence about the location of any
   zero of any specific function.
6. **No route.** This is an offered stage-one artifact in the sense of the RH
   queue; it does not select, advance, or imply a proof route. Its
   cost-lowering effect is nonetheless **asymmetric**, and that is stated here
   rather than left to be discovered: canonical products are named at
   `MATHLIB_CAPABILITY_MAP.md:387` as blocking "Li sums, canonical product,
   explicit formula" (Routes A and C), while the package is inert for Route B
   — Nyman–Beurling/Báez-Duarte, whose blocked-need row `S2-NYMAN` (`:392`,
   "no specialized fractional-part `L²` objects or closure equivalence") names
   nothing product-shaped. Stating flat neutrality without naming the
   asymmetry invites two opposite misreadings: that the package is equally
   relevant to all three parked routes, or that its relevance to A and C is
   itself route progress. Both are wrong. **Lowering the cost of an exit for
   two of three parked routes is inventory, not selection, and must never be
   cited as route progress** (`MULTIPLICITY_CONTRACT.md` finding A4 regime;
   death condition 9). `RH-002`'s three `PARK` dispositions are untouched.
7. **No kernel verdict.** Zero declarations elaborated; every "provable from"
   is a claim about statement shape and pinned text, nothing more.

---

## Death conditions

Stop, split, or return to stage one if any of the following occurs:

1. **The Cotangent dodge.** Any pressure to restate W8, W9, W11, or W12 on a
   subdomain excluding the zero set (a `ℂ_ℤ`-style complement, a
   `∀ i, a i ≠ z` side condition on the order statement, or a
   "nontrivial product" hypothesis on W12). The undodged statements are the
   package's entire reason to exist.
2. A proof requiring a new axiom, an unproved conjecture, or any `sorry`
   surviving into a built module (the one invariant).
3. Any zeta/xi-specific input, any zero enumeration, or any growth/counting
   bound entering any proof (claim boundary 1–3 enforced as a stop rule).
4. Genus-selection creep: any need for the diagonal-genus construction or an
   exponent-of-convergence definition (that is DEFERRED-W1's package).
5. Estimate creep: any need for the sharp Rudin 15.8 bound (DEFERRED-W3), or
   any strengthening of W6 beyond `4/(p+1)` on `‖z‖ ≤ 1/2`.
6. Dropping `hane` by exploiting the `E_p(z/0) = 1` junk value to make a
   statement *look* stronger. Junk-powered generality is a defect, not a
   feature. **Concretely, and this is the whole of the rule** (sharpened
   2026-08-08; see the load-bearing map in §1.2): `hane` is *provably
   redundant* in **W8, W9 and W10**, and is retained there for statement
   uniformity across the block. That redundancy is a true observation and a
   forbidden edit — a stage-two prover who "strengthens" those seven
   signatures by deleting `hane` trips this condition. In **W7, W11 and the
   W12 capstone** `hane` is not redundant at all: without it those statements
   are false, with `a i₀ = 0` and `w = z = 0` as the witness. This condition is
   a policy about W8–W10 specifically, not a vague prohibition.
7. A `⊤`-valued escape in W12: if the capstone can only be closed by weakening
   to `untop₀`/`ℤ` and losing the `≠ ⊤` fact, stop — the `ℕ∞` statement is
   the honest one (§1.5).
8. New definitional surface beyond the two `def`s (a genus function, an
   `Entire` predicate, a divisor pullback, a named annulus): split into a
   separate contract.
9. Declaring any capability-map row stale, or any barrier narrowed, on the
   strength of this generic package.
10. Discovery that a cited pinned locator does not have the quoted shape at
    `fabf563a…` — return to stage one with a corrected contract before any
    build attempt.
11. **Filing this package under the RH subtree, or ledgering any of its rows
    with an `RH-` prefix** (added 2026-08-08). The surface is domain-neutral;
    the `analysis-generic` shelf is owned by no conjecture program, and
    `VERIFIED_RESEARCHOS.md:20-25` pins `riemann-hypothesis` rows to
    `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/` for exactly the reason
    that generic machinery filed there would read as RH-lane content. Correct
    destination: `ResearchOS/Analysis/`, with a new `analysis-generic` prefix
    registered in `scripts/gen_researchos_registry.py` (`PREFIX_DOMAINS`
    :46–:54, `DOMAIN_SUBTREES` :60–:63). Precedent:
    `ResearchOS/Analysis/ThreeCircles.lean:37-42`.
12. **Applying an editorial fix that requires a public signature change**
    (added 2026-08-08). No stage-one lens has asked for one. A fix that turns
    out to need a binder, hypothesis, or conclusion edit STOPS: the surface
    returns to contract review, because an acceptance record is valid only for
    the surface it accepted. Two such fixes are already parked this way —
    S1W-SHADOW's binder rename, and the 29th `_fun_`-form signature discussed
    under S1W-PI.

---

## ANNEX A: locator corrections against `UPSTREAM_POOL.md` §2 (re-verification, 2026-08-07)

All of the pool's §2.2 locators were re-checked against the pin this session.
Three corrections and two confirmations worth recording:

1. **Corrected.** `Complex.logTaylor` (LogBounds.lean:68) is a
   **`noncomputable def`** (modifier on :67), not a plain `def` as the pool's
   §2.2 table and its own §"Corrections to earlier scouting" item 1 assert.
   (The pool corrected an earlier note in the wrong direction.)
2. **Corrected.** `MultipliableUniformlyOn` is at UniformOn.lean:**51**;
   the pool's table lists only :44 (`HasProdUniformlyOn`) and :152/:159,
   leaving the impression :44 covers both.
3. **Corrected.** `Summable.hasProdLocallyUniformlyOn_one_add`
   (MultipliableUniformlyOn.lean:130) takes `IsOpen K` and
   `[LocallyCompactSpace α]` — it is not a compact-set criterion; the compact
   one is :87. The pool's prose conflates them ("open compact" in the :87
   docstring is a pin-side typo this contract does not repeat).
4. **Confirmed.** `norm_log_one_sub_inv_add_logTaylor_neg_le` is at
   LogBounds.lean:231 with exactly the quoted shape, and
   `norm_exp_sub_one_le` at Exponential.lean:439 — scout B's central claim
   (the estimate already exists at the pin) is **true**.
5. **Confirmed with reduction.** The two "absent" lemmas of the pool
   (`HasProdLocallyUniformlyOn.mul_compl`,
   `MultipliableLocallyUniformlyOn.differentiableOn`) are indeed absent as
   names — but §1.4 shows neither is needed: the first is replaced by the
   pinned pointwise split (Basic.lean:752) plus subfamily instantiation, the
   second by defeq dot-notation into LocallyUniformLimit.lean:135
   (precedent: DedekindEta.lean:91). The cost moves into S1W-ORD; it does not
   vanish.

---

## Two-stage gate and promotion ordering (abbreviated; full regime in `MULTIPLICITY_CONTRACT.md`)

**Stage one (this document):** independent acceptance of the statement surface
W1–W12. Produces no built module, no ledger row, no registry entry, no barrier
change, no kernel verdict. Reviewer attack fronts, invited explicitly: the
§1.4 re-derivation (is the pointwise split really sufficient for W12 step 1?),
the S1W-SUB `CommGroup` discipline, the SummationFilter hygiene (S1W-FILTER),
and every locator in the dependencies table.

**Stage two (separate, later, not requested here):** a built promotion PR
carrying the module, ledger rows, regenerated registry and axiom audit, with
verdict from CI under the one invariant. An acceptance PR must not carry a
promotion. Nothing in this lane may bypass the RH queue's single-ACTIVE-slot
discipline; this contract does not claim a slot.

**Return-to-stage-one condition:** death condition 10, or any statement-shape
change requested at stage two.

---

## ANNEX B: RED-TEAM RE-VERIFICATION (2026-08-07)

Independent adversarial re-verification of draft v1 against the pin
(`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`, re-confirmed via `git rev-parse
HEAD` this session). Method: every `file:line` locator in §0, §2, and the
dependencies table was re-printed from the tree and compared against the quoted
shape; hard greps were run for every "absent at the pin" claim and for the
fallback lemma names in the proof skeletons (**qualification added 2026-08-08:
this sweep was not in fact exhaustive — `AnalyticAt.finsetProd`, named in the
W12 skeleton, has zero hits at the pin and was not caught here; corrected in
place in the W12 skeleton and dependency table**); the four invited attack
fronts
(§Two-stage gate) were each pressed. Corrections were applied **in place**
(marked "Annex B item N" at the edit sites); this annex is the record. Same
regime as draft v1: **no kernel verdict, no built module, no barrier change.**

### Verdict

**ACCEPT AT STAGE ONE, AS CORRECTED.** All 47 spot-checked locators match the
pin verbatim (zero phantom citations; zero wrong-shape quotes among the
load-bearing §0 quotes). The four attack fronts resolve as follows — one
substantive finding (item 1, a missed pinned asset, favorable), three locator
defects (item 2, fixed in place), zero soundness defects. Death condition 10
is **not** triggered: no cited pinned locator lacked its quoted shape; the
item-2 defects sit in fallback-route prose, not in the §0 interface quotes or
the dependencies table.

### Attack front 1 — the product-lemma gap (§1.4)

**Claim survives.** `HasProdLocallyUniformlyOn.mul_compl` and
`HasProdUniformlyOn.mul_compl` have **zero hits** at the pin (re-grepped this
session; only three files in the entire tree even mention
`HasProdLocallyUniformlyOn`: UniformOn.lean, MultipliableUniformlyOn.lean,
Cotangent.lean — none contains a compl-split). The pool's §0 rows 13–14
(UPSTREAM_POOL.md:82–83) and its Tier-4 pricing prose (:339, "weeks") are
quoted accurately by §1.4. The re-derivation is sound as stated:
`analyticOrderAt` is a local invariant, so W12 needs the split only as a
*function identity plus analyticity of each factor at `w`* — which the
pointwise `Multipliable.tprod_mul_tprod_compl` (Basic.lean:752, re-verified
verbatim, stated in plain `∏'` with no `SummationFilter` side conditions;
`HasProd.mul_compl` at :379 likewise plain) delivers at every `z`, with tail
analyticity from subfamily-W9. The pool's Tier-4 objection ("the pointwise
split does not deliver an identity of analytic functions on a neighbourhood",
UPSTREAM_POOL.md:340–343) is answered, not dodged: an identity holding at
*every* point of ℂ between functions each analytic at `w` is exactly what
`analyticOrderAt_mul` consumes. No locally-uniform split is needed. DEFERRED-W4
stands.

### Attack front 2 — zero set of an infinite product (no-accumulation)

**In scope and honestly registered; not dodged.** The two classical
obligations behind an unrestricted zero-set/order statement are both carried
by named signatures, not assumed:

- *Non-accumulation.* `hsum` forces `‖a i‖⁻¹ ^ (p+1) → 0` along `cofinite`,
  i.e. the family escapes every ball cofinitely — that is precisely W7's
  `eventually_cofinite_le_norm` (derived, with a full skeleton, from the
  additive `Summable.tendsto_cofinite_zero`, Group.lean:365, `@[to_additive]`
  attribute re-verified on the pin). Fiber finiteness
  (`finite_setOf_apply_eq`) is its stated corollary. Nothing stronger is ever
  used: no step of W10–W12 needs "zeros avoid a punctured neighbourhood of
  `w`" — the fiber split plus tail-factor nonvanishing *at the single point
  `w`* suffices, and indices of `Sᶜ` are free to crowd `w` in norm without
  affecting any step.
- *A convergent product of nonzero factors could still vanish.* Closed by the
  pinned `tprod_one_add_ne_zero_of_summable` (Log/Summable.lean:216;
  `[NormMulClass ℂ]` discharged by `NormedDivisionRing.toNormMulClass`,
  Analysis/Normed/Field/Basic.lean:54–55). This is the exact lemma the
  Cotangent development uses only *off* the zero set; W10/W11 deploy it at
  arbitrary `w` against the fiber complement. The Cotangent-dodge description
  in §1.3 re-verified line-exact: `sineTerm` :78, `sineTerm_ne_zero` :80 (`hx
  : x ∈ ℂ_ℤ`), :94, :99, :105, :118, :125 (`hZ2 : Z ⊆ ℂ_ℤ`), :132 (on `ℂ_ℤ`)
  — quotations only; `ℂ_ℤ` is `local notation` (Cotangent.lean:34) and is
  unwritable outside its own file, see §1.3
  all correct.

### Attack front 3 — local-order additivity across the product

**Honestly registered (S1W-ORD, HIGH) — and draft v1 missed a pinned asset
(item 1 below).** The decomposition in §1.4/W12 is complete: every consumed
order lemma (`analyticOrderAt_mul` :497 with `𝕜 → 𝕜` section variables :488,
`_eq_zero` :133, `_eq_one_of_zero_deriv_ne_zero` :328,
`_comp_of_deriv_ne_zero` :561, `_congr` :175) re-verified verbatim. The one
`[GEN]` lemma is real but smaller than drafted:

1. **(Substantive, favorable.) Finite-product order additivity already exists
   at the pin in the meromorphic carrier.** `meromorphicOrderAt_prod`
   (Meromorphic/Order.lean:437) and `meromorphicOrderAt_fun_prod` (:456 —
   which even pre-solves the `Finset.prod_apply` seam S1W-PI worries about)
   are pinned, together with the carrier bridge
   `AnalyticAt.meromorphicOrderAt_eq` (:279:
   `meromorphicOrderAt f x = (analyticOrderAt f x).map (↑)`) and
   `MeromorphicAt.prod` (Meromorphic/Basic.lean:109). Draft v1's "genuinely
   absent at the pin" was true only of the *analytic-carrier name*;
   the mathematical content is pinned one bridge away. Consequence:
   `analyticOrderAt_finsetProd` (still worth stating, still `[GEN]`) is
   derivable by transfer, and S1W-ORD gains a second fallback route (run
   steps 3–6 in `WithTop ℤ`, transfer once). W12's docstring, pinned
   dependencies, and S1W-GEN were amended in place. Severity ratings
   unchanged: S1W-ORD remains HIGH — the seams it names (funext lift,
   `tprod_fintype`/`toFinset`, `Pi.mul` defeq, `Nat.card` cast chain) are
   untouched by this find.

### Attack front 4 — hidden dependence on an enumeration

**None found.** Variable blocks of every load-bearing file re-read at the pin:
UniformOn.lean:30 (`{α β ι : Type*}`), MultipliableUniformlyOn.lean:24/:82
(`{α ι : Type*}`, `namespace Summable` spans :80–:157 as claimed),
Log/Summable.lean:21 (`variable {ι : Type*}`), InfiniteSum/Basic.lean and
Group.lean generic. `grep Countable\|Encodable\|Denumerable` over all six
load-bearing files: one hit total (`Multipliable.countable_mulSupport`,
Group.lean:388 — unrelated, not consumed). The only `Fintype` in the package
is on the *finite fiber* via `Set.Finite.fintype` (choice, not enumeration).

**"None found" qualified, 2026-08-08.** No *assumed* or *constructed*
enumeration exists anywhere in the package — that part of this attack front
stands. But countability of `ι` is a **derived consequence** of the hypothesis
pair, not merely absent: `hane` makes every `‖a i‖⁻¹ ^ (p+1)` strictly
positive, so the `hsum` family has full support, and a summable ℝ-valued family
with full support has countable index type (additive twin of
`Multipliable.countable_mulSupport`, Group.lean:388 — the very lemma this
paragraph dismisses as "unrelated, not consumed", which remains true: it is not
consumed, it is merely *implied*). Accordingly the draft's rhetorical claim
that "nothing in this package can even *express* an enumeration of zeta zeros"
has been dropped from §1.2 as stronger than the mathematics supports. The
accurate boundary claim — claim boundary item 2, "no statement introduces,
requires, or produces an enumeration, ordering, or counting of anything" —
is unaffected and remains exactly true.

### Item 2 — locator defects found and fixed in place

| # | Draft v1 said | Pin says | Fix |
|---|---|---|---|
| 2a | `DedekindEta.lean:92` for the dot-notation chain (5 sites) | chain sits at **:91** (`multipliableLocallyUniformlyOn_one_sub_pow.hasProdLocallyUniformlyOn.differentiableOn`); :92 is the `.of_forall` continuation | all 5 sites corrected to :91. **Re-corrected 2026-08-08:** the accompanying `:89–95` range citations were *not* already correct — the precedent lemma spans docstring :88 to :93, :94 is blank and :95 opens the next lemma's docstring, so both range citations now read **:88–:93** |
| 2b | `tprod_eq_mulSingle`, "Basic.lean:459 region" (S1W-SING) | **Basic.lean:495**, and it carries `[L.LeAtTop]` (satisfied by `unconditional`) | corrected in W11 obligations |
| 2c | "`Nat.card_eq_toFinset_card'`-family" (W12 step 4) | no such name at the pin; the pinned chain is `Nat.card_coe_set_eq` (Data/Set/Card.lean:642, `Nat.card ↥s = s.ncard`) + `Set.ncard_eq_toFinset_card'` (:649) | corrected in W12 skeleton — **and re-corrected 2026-08-08**: the primed :649 is the `Fintype`/`Set.toFinset` form, whereas W12 builds `hS.toFinset` from `hS : S.Finite`, so the matching lemma is the **unprimed** `Set.ncard_eq_toFinset_card` at **:644**. :649 is kept only as the alternative for a `haveI := hS.fintype` route |

None of the three touches a statement, an obligation severity, or a §0 quote;
all three sit in fallback/bookkeeping prose. Remaining fallback names spot-
checked and confirmed at the pin: `Summable.of_norm_bounded_eventually`
(Analysis/Normed/Group/InfiniteSum.lean:180), `div_eq_one_iff_eq`
(Algebra/GroupWithZero/Units/Basic.lean:359, hypothesis `b ≠ 0` as used),
`pow_lt_pow_iff_left₀` (Algebra/Order/GroupWithZero/Basic.lean:642),
`inv_lt_inv₀` (:1222), `Summable.mul_left`
(Topology/Algebra/InfiniteSum/Ring.lean:45), `WithTop.natCast_ne_top`
(Algebra/Order/Monoid/Unbundled/WithTop.lean:298),
`Bornology.IsBounded.subset_closedBall` (Topology/MetricSpace/Bounded.lean:101),
`logTaylor_succ` (LogBounds.lean:75, "`:73` region" as drafted),
`Finset.sum_range_succ'` (core BigOperators, confirmed in use),
`hasProdLocallyUniformlyOn_iff_tendstoLocallyUniformlyOn` (UniformOn.lean:162),
`HasProdLocallyUniformlyOn.tprod_eqOn` (UniformOn.lean:256). **Added to this
list 2026-08-08** (the names that replace the phantom `AnalyticAt.finsetProd`,
both re-printed from the tree): `Finset.analyticAt_prod`
(Analysis/Analytic/Constructions.lean:1081, `@[fun_prop]`, `N` explicit,
`f`/`c` implicit, conclusion `AnalyticAt 𝕜 (∏ n ∈ N, f n) c`) and
`Finset.analyticAt_fun_prod` (:1073, conclusion
`AnalyticAt 𝕜 (fun z ↦ ∏ n ∈ N, f n z) c`); also `Set.ncard_eq_toFinset_card`
(Data/Set/Card.lean:644) and `Nat.card_coe_set_eq` (:642). Namespace-span
claims verified: LogBounds `namespace Complex` :32–:290; Exponential
:90–:198 and :347–:509 with the `Real` twin `exp_ne_zero` at :235 as warned;
CauchyIntegral `namespace Complex` opens :173 (contains :678); Complex/Basic
`namespace Complex` :566–:710 (contains :689); Arg :24–:663 (contains :544);
Log/Summable homonyms at :49/:94 take `Summable f` exactly as the W10
dependency note warns. Annex A items 1–5 all re-confirmed, including the pool's
"plain `def`" error (UPSTREAM_POOL.md:301, :848 vs the `noncomputable` modifier
on LogBounds.lean:67) and the `:87` docstring's "open compact" pin-side typo.
(Both pool locators re-opened 2026-08-08 and **confirmed correct as cited**:
`UPSTREAM_POOL.md:300` is the `|---|---|` table separator and **:301 is the row
carrying "(plain `def`)"**; :848 carries the companion prose claim. A
stage-one finding proposing ":301 → :302" was checked against the file and
**withdrawn** — the contract's citation was already right.)

### Scout B's grounding claim, settled

The counterintuitive pool claim — *the classically hard estimate already
exists at the pin* — is **confirmed at the strongest reading**:
`norm_log_one_sub_inv_add_logTaylor_neg_le` sits at LogBounds.lean:231–232
character-for-character as quoted in §0, and its own proof (:233–:236) performs
the identical slit-plane discharge W5's skeleton copies, so even the seam
lemmas are precedented in the pin's own text. The real blockers are, as
scouted, bookkeeping — now with one of them (finite-product order additivity)
found to be more pinned than the pool or draft v1 believed.

*This annex records a source-reading review only. No Lean was elaborated; the
kernel remains the sole judge at stage two. No barrier row changes, no route is
selected, and nothing here is a claim about the truth of RH.*

---

## ANNEX C: DRAFTING-PASS FOLD-IN — MISSING-LEMMA HALF RETIRED, COMPUTATION HALF A LOCATED SKETCH (2026-08-07; attribution corrected 2026-08-08)

**Attribution, stated accurately** (corrected 2026-08-08; the heading and this
preamble previously said "two independent scout reports" and leaned on that
phrase in the re-pricing). **Two model-drafted scout passes were run against
the pin; neither is a filed artifact, no record path exists for either — the
`notes/reviews/` directory contains no Weierstrass scout record — and neither
carries independent authority.** Everything asserted below rests on **this
updater's own re-verification against the pin**
(`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`, re-confirmed via `git rev-parse
HEAD`): ~40 locators re-printed from the tree before writing, zero mismatches
against this contract, and two mis-cites found *in the drafting passes
themselves* (item C5) corrected here rather than propagated. **Where the text
below says "both scouts", read "two drafting passes agreed" — corroboration
between untrusted drafters is not evidence**, per `CLAUDE.md`: "Every model is
a drafter only". The charge in both passes was the registered main obligation —
the "missing product lemma" plus the zero-set/local-order computation of the
locally-uniform infinite product.

Same regime as Annexes A–B: **no kernel verdict, no built module, no statement
change, no barrier change, no route, no RH-truth claim.** Statements W1–W12 are
untouched; only obligations, skeleton commentary, and this record gained detail
(edit sites marked "Annex C item N").

### Verdict on the registered main obligation: **MISSING-LEMMA HALF RETIRED; COMPUTATION HALF REDUCED TO A LOCATED SKETCH, UNVERIFIED**

(Heading split 2026-08-08. The single word "RESOLVED" was carrying two halves
of very different evidentiary weight. The missing-lemma half **is** genuinely
settled by reading: a whole-tree absence check is a checkable negative. The
computation half is a **sketch of an unelaborated proof** — no kernel has seen
it — and must not be read as an established fact.)

The obligation as registered (`UPSTREAM_POOL.md` §2 Tier 4): a missing
`HasProdLocallyUniformlyOn.mul_compl` priced at "weeks", plus the
zero-set/local-order computation. Disposition after both scouts and this
updater's re-verification:

1. **The "missing product lemma" is a phantom — agreed by both drafting passes
   and, decisively, re-verified here.** `mul_compl`/`add_compl` have zero
   hits in the uniform layer (`Topology/Algebra/InfiniteSum/UniformOn.lean`,
   `Analysis/Normed/Module/MultipliableUniformlyOn.lean` — both read in full
   by scout 1; grep re-run by this updater: 0 hits); only three files in the
   tree mention `HasProdLocallyUniformlyOn` (UniformOn.lean,
   MultipliableUniformlyOn.lean, Cotangent.lean — re-grepped). The §1.4
   re-derivation is **agreed by both drafting passes and re-read here**
   (agreement between drafters is not the evidence; the re-read is):
   `analyticOrderAt`
   is local, so W12 needs only the pointwise-global split
   `Multipliable.tprod_mul_tprod_compl` (Basic.lean:752, T2 **and
   ContinuousMul** per item C1) plus
   per-point analyticity — no uniform-layer split of any kind. DEFERRED-W4
   stands, now with the item-C2 negative result making the :752 form *minimal*,
   not merely sufficient.
2. **Exactly one generic lemma is genuinely missing at the pin** —
   `analyticOrderAt_finsetProd` (W12, `[GEN]`, statement unchanged) — **and it
   now has two locator-complete pinned derivation routes**: (a) direct
   `Finset.induction` on `analyticOrderAt_mul` (Order.lean:497), template =
   the pin's own proof of `meromorphicOrderAt_prod` (Meromorphic/Order.lean:440–449:
   `Finset.induction` + binary `meromorphicOrderAt_mul` + `MeromorphicAt.prod`,
   re-printed this session); (b) carrier transfer through
   `meromorphicOrderAt_fun_prod` (:456, which pre-solves the
   `Finset.prod_apply` seam via `convert!` — proof text re-verified) and
   `AnalyticAt.meromorphicOrderAt_eq` (:279), closed by the **newly verified**
   `ENat.map_natCast_injective` / `map_natCast_inj` / `ENat.map_add`
   (Data/ENat/Basic.lean:546/:548/:557 — item C3). S1W-GEN stays LOW.
3. **The zero-set/local-order computation decomposes into pinned ingredients
   plus assembly.** Both drafting passes produced the same four-move sketch,
   recorded as the S1W-ORD capstone sketch below; every cited ingredient was
   re-verified by this updater. **No step of the sketch is known to require new
   mathematics; whether the assembly closes is a kernel question no reading can
   settle** (wording corrected 2026-08-08 — the earlier "No new mathematics
   remains" stated a judgment about an unelaborated proof as an established
   fact). Re-pricing, as an **estimate and not a finding**: estimated days of
   seam work rather than the pool's Tier-4 "weeks" — an unverified estimate,
   and **S1W-ORD stays HIGH precisely because it is unverified**, and because
   it is still the hardest single proof in the package.

### The S1W-ORD capstone assembly sketch (agreed by both drafting passes, all locators re-verified by this updater; UNVERIFIED by any kernel)

At `w : ℂ`, `S := {i | a i = w}`, finite via the additive
`Summable.tendsto_cofinite_zero` (Group.lean:365, `@[to_additive]` re-checked)
→ W7 escape-to-infinity → fiber finiteness:

1. **Split as a function identity** (`funext`, every `z`): restrict
   `Summable (fun i ↦ ‖E_p(z / a i) − 1‖)` (W8) through the additive
   `Summable.subtype` (Group.lean:300) to `S` and `Sᶜ`; re-enter ℂ via
   `multipliable_one_add_of_summable` (Log/Summable.lean:169) modulo the
   `1 + (E−1) = E` congr (`tprod_congr`, Basic.lean:471); apply
   `Multipliable.tprod_mul_tprod_compl` (Basic.lean:752; `[T2Space ℂ]` by
   instance) pointwise. No uniform content — `analyticOrderAt_mul` consumes
   only a function identity plus two `AnalyticAt` facts at `w`.
2. **Head** collapses to a `Finset.prod` by `tprod_fintype` (Basic.lean:481;
   `[L.LeAtTop]` holds for `unconditional`); each factor has order 1 at `w` by
   `analyticOrderAt_comp_of_deriv_ne_zero` (Order.lean:561) +
   `AnalyticAt.analyticOrderAt_eq_one_of_zero_deriv_ne_zero` (:328) +
   `deriv_const_sub_id` (Deriv/Add.lean:449); analyticity of the head product
   itself by `Finset.analyticAt_prod` (Analysis/Analytic/Constructions.lean:1081
   — supplied 2026-08-08 in place of the phantom `AnalyticAt.finsetProd`); sum
   by `analyticOrderAt_finsetProd` → `Nat.card S` via `Nat.card_coe_set_eq`
   (Data/Set/Card.lean:642) + **`Set.ncard_eq_toFinset_card` (:644**, the
   `Set.Finite.toFinset` form this route actually builds; corrected 2026-08-08
   from the primed `Fintype`-based :649).
3. **Tail** is the subfamily's own canonical product (defeq, S1W-SPLIT),
   analytic at `w` by subfamily-W8+W9
   (`hasProdLocallyUniformlyOn_of_forall_compact` UniformOn.lean:196 +
   `Summable.hasProdUniformlyOn_one_add` MultipliableUniformlyOn.lean:87 +
   `TendstoLocallyUniformlyOn.differentiableOn` LocallyUniformLimit.lean:135
   by defeq, DedekindEta.lean:91 pattern), and **nonzero at `w`** by
   `tprod_one_add_ne_zero_of_summable` (Log/Summable.lean:216) since every
   tail factor avoids `w` — order 0 by Order.lean:133.
4. `analyticOrderAt_mul` (Order.lean:497): total = `Nat.card {i | a i = w} + 0`;
   the `≠ ⊤` companion by `WithTop.natCast_ne_top`
   (Algebra/Order/Monoid/Unbundled/WithTop.lean:298).

This is exactly W10–W12's existing skeleton with every previously-prose step
now carrying a re-verified locator. No statement changed.

### Delta items (edit sites marked in place)

- **C1 (minor amendment, §0; extended 2026-08-08).** The v1.1 quote of
  `Multipliable.tprod_mul_tprod_compl` omitted the section variable
  `variable [T2Space α]` at Basic.lean:696 (re-printed this session).
  **It omitted a second one as well, and C1's claim that T2 was the only
  omission was wrong:** :752 also sits inside `section ContinuousMul`
  (:711 open, :769 close) whose `variable [ContinuousMul α]` is declared at
  :713, so the real ambient instance set for :752 is
  `[CommMonoid α] [TopologicalSpace α] [T2Space α] [ContinuousMul α]` (the
  first two from `section tprod`'s `variable` at :434). Both extra instances
  are discharged for α = ℂ; **no statement impact** — but §0 claims to quote
  "the load-bearing interface verbatim", so the quote-comment now says so.
  Likewise `HasProd.mul_compl` (:379, via `HasProd.mul_isCompl` :373) needs no
  T2 — that part of C1 stands — but it is **not** hypothesis-free: it sits
  inside `section HasProd` (:36–:430) under `variable [ContinuousMul α]`
  declared at :319. "Needs no T2" is correct; "needs nothing" would not be.
- **C2 (negative result, DEFERRED-W4 strengthened).** The pin's one-hypothesis
  split `Multipliable.tprod_subtype_mul_tprod_subtype_compl` (Group.lean:310)
  sits under `variable [CommGroup α]` (Group.lean:32, `section
  IsTopologicalGroup` :30 — section structure walked this session): unusable
  for ℂ-under-×. Basic.lean:752 is genuinely minimal; S1W-SUB is necessary.
- **C3 (favorable, W12 fallback route completed).** The transfer route's
  previously-unnamed closing steps are pinned: `ENat.map_natCast_injective`
  (Data/ENat/Basic.lean:546), `ENat.map_natCast_inj` (:548, `@[simp]`),
  `ENat.map_add` (:557). Neither scout supplied these locators; found and
  verified by this updater. Route (b) of S1W-GEN is locator-complete.
- **C4 (confirmation, no edit).** The `:87` docstring's "open compact `K`"
  pin-side typo (MultipliableUniformlyOn.lean:85, hypothesis is `IsCompact K`
  only) re-confirmed — Annex A item 3 stands verbatim. The `_of_clog`
  criterion (MultipliableUniformlyOn.lean:59 region) requires nonvanishing on
  the whole set, so it cannot replace the zero-set statement (scout 1,
  consistent with §1.3's Cotangent-dodge analysis). Cotangent anchors
  :78/:80/:94/:99/:105/:118/:125/:132 all re-grepped this session — line-exact.
- **C5 (scout-report defects, NOT propagated).** Scout 1 cited "Defs.lean:77"
  for the `unconditional` `∏'` notation — the notation is at **Defs.lean:158**
  (this contract's existing citation; :74–:80 is the `HasProd` docstring
  describing the unconditional default) — and ":377" for `HasProd.mul_isCompl`,
  which sits at **:373**. Both re-printed this session. No contract text ever
  carried either error; recorded so the scout reports are not treated as
  locator-authoritative over this annex.

### What the obligation became, and the new riskiest step

- **Registered obligation → MISSING-LEMMA HALF RETIRED; COMPUTATION HALF A
  LOCATED SKETCH (UNVERIFIED).** No pinned route was "discovered" that removes
  the package (nothing at the pin states the zero-set/order of a canonical
  product — the Cotangent dodge is still the in-tree frontier). The
  missing-lemma half dissolved: a whole-tree absence check is a checkable
  negative, and it was run twice. The computation half now has a complete
  assembly *sketch* from pinned ingredients plus the single small `[GEN]`
  lemma with two locator-complete derivation routes — **a sketch, not a proof;
  nothing here has been elaborated, and the kernel remains the only thing that
  can turn "located" into "closed"** (wording corrected 2026-08-08).
- **New riskiest step: the S1W-ORD seam cluster, specifically the
  `funext`-lifted split feeding `analyticOrderAt_mul` through the `Pi.mul`
  vs `fun z ↦ F z * T z` defeq** (capstone steps 1→4), with the
  `tprod_fintype`/`toFinset` conversion under the SummationFilter framework
  as its immediate second. It is bookkeeping, not analysis; pinned fallback
  if the global identity resists: `analyticOrderAt_congr` (Order.lean:175)
  needs the identity only on a neighborhood filter. Highest surviving
  non-capstone obligation: S1W-CONV (MEDIUM-HIGH, the two-slot
  `1 + (E − 1) = E` congr in W8).

*This annex records a source-reading fold-in only. No Lean was elaborated; the
kernel remains the sole judge at stage two. No barrier row changes, no route is
selected, and nothing here is a claim about the truth of RH.*
