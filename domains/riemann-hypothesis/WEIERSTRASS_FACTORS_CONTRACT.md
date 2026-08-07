# Weierstrass elementary factors / canonical product contract: draft v1

Status: **DRAFT v1 (2026-08-07) — non-built review artifact, offered for STAGE ONE
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

Working name: `WeierstrassFactors.lean` (drafts lane; eventual module path is a
stage-two decision). Statement surface: **W1 – W12**, comprising **exactly 28
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
`summable_norm_weierstrassFactor_sub_one`. The only case-insensitive
"weierstrass" hits at the pin are `PowerSeries.IsWeierstrassFactorization*` in
`RingTheory/PowerSeries/WeierstrassPreparation.lean` — unrelated commutative
algebra (Weierstrass *preparation*, not elementary factors).

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
-- NumberTheory/ModularForms/DedekindEta.lean:89–95 —
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
noncomputable def analyticOrderAt (f : 𝕜 → E) (z₀ : 𝕜) : ℕ∞
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
  filter-based). Consequently **nothing in this package can even express an
  enumeration of zeta zeros**, let alone consume one: the statements are about
  a generic family `a`, full stop.
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

### 1.3 The Cotangent dodge — and why this contract must not repeat it

The in-tree template for everything through analyticity is the Euler sine
product (`Analysis/SpecialFunctions/Trigonometric/Cotangent.lean`, re-verified
this session): `sineTerm` (:78), `multipliable_sineTerm` (:94),
`euler_sineTerm_tprod` (:99), the compact-majorant argument
`sineTerm_bound_aux` (:105), `multipliableUniformlyOn_euler_sin_prod_on_compact`
(:118), and `HasProdLocallyUniformlyOn_euler_sin_prod` (:132). Note what that
development does at every step that would touch a zero of `sin`: it restricts
to `ℂ_ℤ`, the complement of the integers (`sineTerm_ne_zero` at :80 takes
`hx : x ∈ ℂ_ℤ`; the `HasProdUniformlyOn` statement at :125 takes `hZ2 : Z ⊆
ℂ_ℤ`; the locally-uniform statement at :132 is on `ℂ_ℤ`). The
Weierstrass-shaped content — *the product is entire and its zero set and local
orders are exactly those of the factor family* — is exactly what is dodged.

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
is finite, and the companion signature `analyticOrderAt_weierstrassProduct_ne_top`
makes the non-degeneracy explicit rather than burying it in `untop₀` junk.

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

Denominator convention: `(k + 1 : ℂ)` is the `ℕ`-cast of `k + 1 ≥ 1`, never
zero, so no division junk arises anywhere in the definition.

### Pinned dependencies (W1)

`Complex.exp_zero`, `Complex.exp_add` (`Analysis/Complex/Exponential.lean`,
namespace `Complex`, :347–:509); `Finset.sum_range_succ` (Mathlib core
BigOperators). Not load-bearing beyond name resolution.

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
  `(-z)^(k+1)`) is `rw`-fragile. Fallback: `induction p` with
  `logTaylor_succ` (LogBounds.lean:73 region) and `Finset.sum_range_succ`.
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

```lean
  have h := Complex.norm_log_one_sub_inv_add_logTaylor_neg_le p hz   -- LogBounds.lean:231
  -- h : ‖log (1 - z)⁻¹ + logTaylor (p + 1) (-z)‖ ≤ ‖z‖ ^ (p + 1) * (1 - ‖z‖)⁻¹ / (p + 1)
  rw [Complex.log_inv _ (Complex.slitPlane_arg_ne_pi
        ((sub_eq_add_neg 1 z) ▸ Complex.mem_slitPlane_of_norm_lt_one
          ((norm_neg z).symm ▸ hz))),                                -- log (1-z)⁻¹ = -log (1-z)
      logTaylor_neg_eq] at h                                         -- W4
  -- h : ‖-log (1 - z) + -∑ …‖ ≤ …
  simpa [← neg_add, norm_neg] using h
```

The slit-plane discharge is copied move-for-move from the pin's own proof of
:231 (LogBounds.lean:234–235 uses exactly
`log_inv _ <| slitPlane_arg_ne_pi <| mem_slitPlane_of_norm_lt_one <|
(norm_neg z).symm ▸ hz` after `sub_eq_add_neg`).

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

- **S1W-LOG** (MEDIUM): the `▸`-chain feeding the slit-plane fact is
  defeq-sensitive (`1 - z` vs `1 + -z`). Fallback: prove
  `(1 : ℂ) - z ∈ Complex.slitPlane` as a standalone `have` via
  `rw [sub_eq_add_neg]; exact Complex.mem_slitPlane_of_norm_lt_one (by
  rwa [norm_neg])`, then feed it. The final `simpa [← neg_add, norm_neg]`
  must merge `-a + -b` to `-(a + b)`; if it misfires, `rw [← neg_add] at h;
  rwa [norm_neg] at h`.

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
5. Assemble: `‖E_p z - 1‖ = ‖exp L - 1‖ ≤ 2 * ‖L‖ ≤ 2 * (‖z‖^(p+1) * 2 / (p+1))
   = 4 / (p+1) * ‖z‖^(p+1)` — `gcongr` + `ring_nf`.

### Pinned dependencies (W6)

W4, W5; `Complex.norm_exp_sub_one_le` —
`Analysis/Complex/Exponential.lean:439` (verified verbatim:
`(hx : ‖x‖ ≤ 1) : ‖exp x - 1‖ ≤ 2 * ‖x‖`, namespace `Complex`).

### Obligations (W6)

- **S1W-EST** (MEDIUM): pure `gcongr`/`linarith` bookkeeping over `ℝ` with a
  `(p + 1 : ℝ)`-cast in denominators (`Nat.cast_pos`, `div_le_div_iff₀`). No
  mathematical content; one CI cycle of cast-lemma whack-a-mole is priced in.
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
   `[LocallyCompactSpace ℂ]` holds — ℂ is proper). Fix `K` compact,
   `K ⊆ closedBall 0 R` with `R ≥ 0` (`IsCompact.isBounded` +
   `Bornology.IsBounded.subset_closedBall`).
2. Majorant `u i := 4 / (p+1) * (R ^ (p+1) * ‖a i‖⁻¹ ^ (p+1))`; summable from
   `hsum` by `Summable.mul_left`.
3. Eventual bound: by W7 (`eventually_cofinite_le_norm … (2 * R + 1)`),
   cofinitely many `i` have `2 * R + 1 ≤ ‖a i‖`; for those and any `x ∈ K`,
   `‖x / a i‖ ≤ R / (2R + 1) ≤ 1/2`, so W6 gives
   `‖weierstrassFactor p (x / a i) - 1‖ ≤ 4/(p+1) * ‖x / a i‖^(p+1) ≤ u i`
   (`norm_div`, `div_pow`, `gcongr`).
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
`sineTerm_bound_aux`.

### Obligations (W8)

- **S1W-CONV** (MEDIUM-HIGH): the `1 + (E - 1) = E` re-identification (step 5)
  is the same congr-seam Cotangent handles at :125–:130 via `congr_right` and
  a `tprod` rewrite, but here on **two** slots (family and limit). Beta-redex
  discipline as in `MULTIPLICITY_CONTRACT.md` finding A2: close with
  `simp only [add_sub_cancel]`-style congr lemmas, never bare `rw` under a
  binder. Fallback: state the criterion's raw conclusion as a `have` and
  convert with `HasProdLocallyUniformlyOn.congr`-analogues pointwise.
- **S1W-RAD** (LOW): the `R / (2R + 1) ≤ 1/2` and `R ≥ 0` bookkeeping;
  `positivity`/`linarith`.

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
`DedekindEta.lean:89–95` (quoted in §0); W2, W8.

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
and nonvanishing — Order.lean:133 again); step case `analyticOrderAt_mul` with
`AnalyticAt.finsetProd`-style closure (or `Finset.prod_fn` + `fun_prop`).
`Pi.mul`/`Finset.prod_apply` seams are the only content.

*Capstone.* Fix `w`. `S := {i | a i = w}`, `hS : S.Finite := finite_setOf_apply_eq
hane hsum w` (W7); `haveI := hS.fintype`.
1. Split (W10, first signature) at `S`, as a **function** identity via
   `funext`:
   `weierstrassProduct p a = F * T` where
   `F := fun z ↦ ∏' i : S, E_p (z / a i)`, `T := fun z ↦ ∏' i : ↥Sᶜ, E_p (z / a i)`.
2. `F` collapses to a `Finset.prod` (`tprod_fintype`, Basic.lean:481):
   `F = fun z ↦ ∏ i ∈ hS.toFinset, E_p (z / a i)` (attach/`toFinset`
   bookkeeping).
3. `analyticOrderAt_mul` at `w` (`F` analytic: finite product of W2 factors;
   `T` analytic: W10 second signature).
4. `analyticOrderAt F w = ∑ i ∈ hS.toFinset, 1 = hS.toFinset.card` by
   `analyticOrderAt_finsetProd` + the factor-at-`c` lemma (each `i ∈ S` has
   `a i = w`, `hane i`), then `hS.toFinset.card = Nat.card {i | a i = w}`
   (`Nat.card_coe_set_eq`, Data/Set/Card.lean:642, then
   `Set.ncard_eq_toFinset_card'`, Data/Set/Card.lean:649 — the name
   `Nat.card_eq_toFinset_card'` cited in draft v1 does not exist at the pin;
   corrected by Annex B item 2).
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
Basic.lean:481; `Complex.exp_ne_zero` — Exponential.lean:160; W2, W3, W7, W10.

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
insurance only.

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
| Euler sine template | Cotangent.lean:78–:135 | W8 pattern | yes (read in full) |
| Product-differentiable template | DedekindEta.lean:89–95 | W9 pattern | yes (verbatim) |

---

## Obligation register

| ID | Severity | Attaches to | One-line content |
|---|---|---|---|
| **S1W-ORD** | **HIGH — hardest in package** | W12 | capstone assembly: split → `tprod_fintype` → `analyticOrderAt_mul`/`finsetProd` → `Nat.card` cast chain |
| S1W-CONV | MEDIUM-HIGH | W8 | the `1 + (E - 1) = E` congr on family and limit slots |
| S1W-SPLIT | MEDIUM | W10 | three pointwise congr-seams + subfamily-defeq |
| S1W-PI | MEDIUM | W12 | `Pi.mul` / `Finset.prod_apply` / beta seams |
| S1W-LOG | MEDIUM | W5 | slit-plane `▸`-chain; `-a + -b` merge |
| S1W-EST | MEDIUM | W6 | ℝ-cast and `(p+1)`-denominator arithmetic |
| S1W-INV | MEDIUM | W7 | inverse-power comparison bookkeeping |
| S1W-4a | MEDIUM | W4 | `logTaylor` junk-term absorption + reindex |
| S1W-DIFF | LOW-MEDIUM | W9 | dot-notation defeq unfolding (precedented) |
| S1W-FILTER | LOW-MEDIUM | W10, W11 | SummationFilter (`unconditional`) hygiene |
| S1W-SUB | LOW | W7, W10 | additive-only `Summable.subtype` discipline (ℂ-under-× is no `CommGroup`) |
| S1W-GEN | LOW | W12 | `analyticOrderAt_finsetProd` induction; widening to `𝕜` permitted |
| S1W-SING | LOW | W11 | singleton-`tprod` collapse route choice |
| S1W-RAD | LOW | W8 | radius arithmetic |
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
  proposed upstream on its own merits, not smuggled in here.

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
   `S1-GLOBAL-ZEROS` (`:387`, blocked-need "canonical product") and
   `S1-MULTIPLICITY` (`:386`) remain OPEN and are not re-scoped by this
   document.
5. **No RH-truth claim.** Nothing here is evidence about the location of any
   zero of any specific function.
6. **No route.** This is an offered stage-one artifact in the sense of the RH
   queue; it does not select, advance, or imply a proof route.
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
   feature.
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
shape; hard greps were run for every "absent at the pin" claim and every
fallback lemma name in the proof skeletons; the four invited attack fronts
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
The claim-boundary assertion "nothing in this package can even express an
enumeration of zeta zeros" is accurate as to statement surface.

### Item 2 — locator defects found and fixed in place

| # | Draft v1 said | Pin says | Fix |
|---|---|---|---|
| 2a | `DedekindEta.lean:92` for the dot-notation chain (5 sites) | chain sits at **:91** (`multipliableLocallyUniformlyOn_one_sub_pow.hasProdLocallyUniformlyOn.differentiableOn`); :92 is the `.of_forall` continuation | all 5 sites corrected to :91; the `:89–95` range citations were already correct |
| 2b | `tprod_eq_mulSingle`, "Basic.lean:459 region" (S1W-SING) | **Basic.lean:495**, and it carries `[L.LeAtTop]` (satisfied by `unconditional`) | corrected in W11 obligations |
| 2c | "`Nat.card_eq_toFinset_card'`-family" (W12 step 4) | no such name at the pin; the pinned chain is `Nat.card_coe_set_eq` (Data/Set/Card.lean:642, `Nat.card ↥s = s.ncard`) + `Set.ncard_eq_toFinset_card'` (:649) | corrected in W12 skeleton |

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
`HasProdLocallyUniformlyOn.tprod_eqOn` (UniformOn.lean:256). Namespace-span
claims verified: LogBounds `namespace Complex` :32–:290; Exponential
:90–:198 and :347–:509 with the `Real` twin `exp_ne_zero` at :235 as warned;
CauchyIntegral `namespace Complex` opens :173 (contains :678); Complex/Basic
`namespace Complex` :566–:710 (contains :689); Arg :24–:663 (contains :544);
Log/Summable homonyms at :49/:94 take `Summable f` exactly as the W10
dependency note warns. Annex A items 1–5 all re-confirmed, including the pool's
"plain `def`" error (UPSTREAM_POOL.md:301, :848 vs the `noncomputable` modifier
on LogBounds.lean:67) and the `:87` docstring's "open compact" pin-side typo.

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
