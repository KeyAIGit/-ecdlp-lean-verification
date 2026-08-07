# RH zero-set / compact divisor-sum slice contract (S1-GLOBAL-ZEROS neutral slice): draft v1

Status: **DRAFT v1 (2026-08-07) — non-built design artifact, statement surface
only. NOT Lean-checked.** No declaration below has been elaborated; no
`lake build` has been run against any of it. Under the one invariant, the Lean
kernel via CI is the sole judge of every statement in this contract, and this
document carries no kernel verdict of any kind. **This contract closes
nothing.** It does not close `S1-GLOBAL-ZEROS`, does not select a route (all
routes remain PARKED per the RH queue's dated decisions), and makes **no claim
about the truth of the Riemann Hypothesis**. It advances the barrier's single
route-neutral slice — the two halves N2 (zero-set discreteness package) and N1
(compact divisor sums) — without closing the barrier, and says so plainly.

**Queue position.** This is an offered artifact, not an active task. The RH
queue's sole ACTIVE task is `RH-010` (kernel promotion of the accepted
multiplicity surface; `tasks/RIEMANN_HYPOTHESIS.md:616`). This document does
not occupy a queue slot, does not authorize route work, and enters the queue
only by a future dated queue decision. The two-stage gate of
`MULTIPLICITY_CONTRACT.md` §Two-stage gate applies to it verbatim: independent
contract acceptance first, built promotion as a separate change, CI the sole
judge.

**Provenance.** The N1/N2 slice pair was identified by a workflow-internal
reconnaissance of `S1-GLOBAL-ZEROS` (not an on-disk artifact; see Annex N,
finding R2). The on-disk anchors this contract rests on instead are:

- `MULTIPLICITY_CONTRACT.md:1714–1723` (**DEFERRED-2**): "ξ zero-set
  discreteness / closedness / compact-finiteness / countability … Excluded to
  hold scope; it would also be the first step toward `S1-GLOBAL-ZEROS`, which
  is a different barrier." N2 is exactly that deferred item, stated.
- `MATHLIB_CAPABILITY_MAP.md:387` (the `S1-GLOBAL-ZEROS` row): remaining exit
  evidence "finite divisor sums, weighted summability, star convergence of
  `Σ 1/ρ`, existence of source-matched limits with multiplicity, including
  `|ρ| ≤ T` for Li and `|Im ρ| < T` for Weil, plus absolute convergence of the
  Weil scalar-product combination". N1 supplies only the first item's
  cutoff-free layer ("finite divisor sums"); everything after the first comma
  — weighted summability, star convergence, the `|ρ| ≤ T` and `|Im ρ| < T`
  truncations, Weil convergence — is route-shaped and is **deliberately not
  touched**. That is the precise sense in which this contract advances the
  barrier without closing it.

An internal adversarial review was run on the two designer sections during
consolidation (verdict `SOUND_WITH_FIXES`, six findings R1–R6, all applied in
place; see Annex N). That review accepts a statement surface only: it is not a
kernel verdict, it does not promote a module, and it does not close or weaken
any barrier row.

Working name: `ZeroSet.lean` (module
`ResearchOS.AnalyticNumberTheory.RiemannHypothesis.ZeroSet`), landing after
the built Mult module.
Statement surface: **N2-D1 – N2-D9 and N1.1 – N1.9, comprising exactly 23
public signatures** (D7 carries two, N1.6/N1.7/N1.8 carry two each, N1.9
carries three; N2-D8 and N1.1 are **one** statement — see the unification note
in §1 and Annex N finding R1). Every signature is spelled explicitly in a
`lean` block below; none is mandated in prose only. The package contains
**zero `def`s**: the ξ zero set is spelled inline as `riemannXi ⁻¹' {0}` at
every use site, deliberately matching M13's spelling
`U ∩ riemannXi ⁻¹' {0}` (a `riemannXiZeros` def in the style of the pinned
`riemannZetaZeros` would create a second spelling of the same set and a naming
seam against the accepted M13 surface), and the compact sum is a spelling
(`∑ᶠ z ∈ K, …`), not a definition.

Scope: (N2) the multiplicity-aware topology of the ξ zero set — closed and
discrete in the plane, finite intersection with **an arbitrary compact set**,
countable — and the same three predicates for the ξ divisor support on an
arbitrary carrier `U`; (N1) the ξ divisor summed over **an arbitrary compact
set** — well-defined, finite, nonnegative (a natural number up to cast),
monotone in the window, and invariant under the three symmetries `1 - s`,
`conj s`, `1 - conj s`. It contains **no** zero enumeration, **no** counting
function, **no** growth theorem, **no** density bound, **no** Hadamard
product, **no** Li coefficients, **no** summability or convergence statement,
and **no** zero-free-region content.

Pinned Mathlib: `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0),
re-verified during consolidation via
`git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD`. Every
`file:line` locator below is from that exact tree (paths relative to the
`Mathlib/` root) unless prefixed `repo:`; **every locator in this document was
re-verified by direct read of the pinned tree during the consolidation
adversarial review** (Annex N §B; four locators corrected, R2–R4).

Repo prerequisites (kernel-checked on `main`; xi package merged in PR #304
`afdae08`, conjugation package merged in PR #307 `c277b86`):

| Symbol | Location |
|---|---|
| `riemannXi` | repo:`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Xi.lean:41` |
| `differentiable_riemannXi` | repo:`…/Xi.lean:46` |
| `riemannXi_one_sub` | repo:`…/Xi.lean:61` |
| `riemannXi_zero` (`= 1/2`) | repo:`…/Xi.lean:72` |
| `riemannXi_ne_zero_of_one_le_re` | repo:`…/Xi.lean:157` |
| `riemannXi_zero_mem_critical_strip` | repo:`…/Xi.lean:192` |
| `riemannXi_comp_conj` | repo:`…/Conj.lean:292` |
| `analyticOrderAt_riemannXi_conj` | repo:`…/Conj.lean:452` |

Package prerequisites (**PACKAGE PREREQUISITES** — the M1–M17 surface of
`MULTIPLICITY_CONTRACT.md` was accepted at statement level under `RH-009` on
2026-08-07 and its kernel promotion `RH-010` is in flight; these are cited as
prerequisites, **never as pinned Mathlib, and never as already
kernel-checked**):

| M-statement | Signature consumed | Contract locator | Role here |
|---|---|---|---|
| M9 | `analyticOnNhd_riemannXi` | `MULTIPLICITY_CONTRACT.md:851` | reach the divisor (N1 block; N2 Block A derives its own analyticity inline from repo:`Xi.lean:46` and does **not** wait on it) |
| M10 | `riemannXi_divisor_apply` | `:882` | the carrier seam (used at `U` and at `Set.univ`); interpretively, divisor value at a support point = local analytic order |
| M11 | `riemannXi_divisor_nonneg` | `:910` | effectivity → sum nonnegativity, monotonicity |
| M12 | `analyticOrderAt_riemannXi_ne_top`, `meromorphicOrderAt_riemannXi_ne_top` | `:933` (obligation S1M-FIN) | **semantic license**: without finite local order, `untop₀` conflates "no zero" with "identically zero nearby" and the sums would not read as multiplicity counts; consumed transitively through M13 |
| M13 | `riemannXi_divisor_support` | `:1056` | **the load-bearing seam**: `Function.support (MeromorphicOn.divisor riemannXi U) = U ∩ riemannXi ⁻¹' {0}` for every `U` — what makes the topology package *multiplicity-aware* (D9, and the alternative route of the unified D8/N1.1) |
| M14 | `riemannXi_divisor_one_sub` | `:1091` | reflection leg of Block D |
| M15 | `riemannXi_divisor_conj`, `riemannXi_divisor_one_sub_conj` | `:1160` | conjugation/composite legs of Block D (these carry the M-package's own `[CONJ]` provenance, repo:`Conj.lean:452`, merged PR #307) |

M12 is cited as the **reading** of the sums (it appears in no proof skeleton
below); M9–M11, M13–M15 are proof-level dependencies of the statements tagged
`[MULT]`. Honesty note on conditionality: every `[MULT]` prerequisite is
itself, per the M-contract, an unconditional consequence of pinned Mathlib
plus kernel-checked `main` — so nothing below waits on anything outside the
pin and `main` **mathematically**; the dependency is an **ordering**
dependency (this contract's built module imports the built Mult module and
lands only after the `RH-010` promotion merges).

**The neutrality rule (load-bearing, stated once for the whole surface).**
Every compact-finiteness and sum statement below is parameterized by an
**arbitrary** `K : Set ℂ` (with `IsCompact K` exactly where finiteness demands
it), and every divisor statement by the **arbitrary** carrier `U : Set ℂ` the
M-package already uses. **No cutoff shape appears anywhere in a signature.**
Choosing between `{ρ | ‖ρ‖ ≤ T}` and `{ρ | |ρ.im| < T}` (or balls, boxes,
spheres, strips) is a route selection — the capability row itself names
`|ρ| ≤ T` as Li-shaped and `|Im ρ| < T` as Weil-shaped — and all routes are
PARKED. The pin contains shape-specific specials
(`divisor_sphere_support_finite`, Analysis/Meromorphic/Divisor.lean:83;
`divisor_ball_support_finite`, :104) which this package deliberately does
**not** mirror. Likewise no strip-restricted variant is stated: ξ is entire,
its zero set already lies in the open strip (repo:`Xi.lean:192`), so strip
variants are one-line corollaries a route can take later — stating them now
would begin shaping a cutoff. Proof-internal exhaustions (e.g. the closed-ball
fallback for D5) are permitted: **neutrality is a property of the statement
surface, not of proof internals**. A consumer route later specializes `K` in
one line; this contract never does.

## Candidate fields

- **Mechanism (N2).** ξ is entire (repo:`Xi.lean:46`) and not identically
  zero (`riemannXi 0 = 1/2`, repo:`Xi.lean:72`), so the pinned engine
  `AnalyticOnNhd.preimage_zero_mem_codiscrete` (Order.lean:682) yields that
  the complement of the ξ zero set is codiscrete in ℂ — **one lemma
  application, simpler than the pinned ζ precedent**, which must detour
  through `codiscreteWithin {1}ᶜ` and a punctured-plane connectivity lemma
  because ζ has the pole at 1 (ZetaZeros.lean:39–55). Closedness and
  discreteness split off by `mem_codiscrete'` (DiscreteSubset.lean:343)
  exactly as at ZetaZeros.lean:57/:60; finiteness on an arbitrary compact is
  `IsCompact.inter_right` + `IsCompact.finite` exactly as at
  ZetaZeros.lean:64–67; countability is the hereditarily-Lindelöf argument
  (Lindelof.lean:723 + :655), which the ζ precedent does not even state. The
  divisor half rides the pinned carrier: `MeromorphicOn.divisor riemannXi U`
  has discrete support by construction (LocallyFinsupp.lean:218) and closed
  support over closed `U` (:237); its compact-finiteness on **arbitrary** `U`
  is a ξ theorem, not a carrier theorem (boundary-accumulation note, §1).
- **Mechanism (N1).** The ξ divisor is summed over an arbitrary compact `K`
  in the **finsum** spelling `∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z`.
  Finiteness of `K ∩ support` is obtained ξ-specifically by comparing the
  `U`-divisor with the `Set.univ`-divisor (M10 twice), the `univ` divisor
  having globally locally finite support
  (`Function.locallyFinsupp.locallyFiniteSupport`, LocallyFinsupp.lean:115,
  because ξ is entire), closed by
  `LocallyFiniteSupport.finite_inter_support_of_isCompact`
  (LocallyFinsupp.lean:106). The finsum is converted to an honest
  `Finset.sum` by `finsum_mem_eq_sum` (additive twin of Finprod.lean:499–501);
  nonnegativity and `K`-monotonicity are `Finset.sum_nonneg` /
  `Finset.sum_le_sum_of_subset_of_nonneg` (Group/Finset.lean:119–120/:131–132)
  fed by M11; symmetry invariance is `finsum_mem_image` (twin of
  Finprod.lean:929–936) reindexing along the three involutions plus the
  M14/M15 pointwise divisor identities.
- **Expected information gain.** The route-neutral entry cost of
  `S1-GLOBAL-ZEROS`: every PARKED route (counting, Hadamard, explicit
  formula, Li, Weil, …) needs "the zeros are a closed discrete
  multiplicity-decorated set, finite on compacts, countable, with
  well-defined monotone symmetric finite sums over arbitrary compact
  windows" before it needs anything route-specific. Advancing this slice
  reduces the entry cost of every future route equally and closes none of
  them. No information about the truth of RH is produced.
- **Claim boundary (summary; full statement below).** D1–D7 and N1.9 are
  unconditional consequences of pinned Mathlib plus kernel-checked repo
  theorems on `main` — they wait on nothing. D8/N1.1, D9, N1.2–N1.8
  additionally consume M-package prerequisites and are **not provable at this
  pin until the `RH-010` promotion lands**. Nothing here states or implies a
  zero enumeration, an ordering of zeros, a counting asymptotic, a growth or
  density bound, or a summability/convergence fact.
- **Death conditions (headline; full list below).** Stop if any statement
  would need a zero enumeration, a counting function, a growth or density
  bound, a new axiom, or a new definition; stop if a cutoff shape appears in
  any signature; never inline-derive M-package content; and do not declare
  `S1-GLOBAL-ZEROS` (or any row) closed or weakened on the strength of this
  package.

Proposed preamble (name-resolution review only):

```lean
import ResearchOS.AnalyticNumberTheory.RiemannHypothesis.Xi    -- riemannXi, differentiable_riemannXi, riemannXi_zero
import ResearchOS.AnalyticNumberTheory.RiemannHypothesis.Mult  -- M9–M15 (PACKAGE PREREQUISITE; promotion RH-010 in flight)
import Mathlib.Analysis.Analytic.Order               -- AnalyticOnNhd.preimage_zero_mem_codiscrete
import Mathlib.Analysis.Complex.CauchyIntegral       -- Complex.analyticOnNhd_univ_iff_differentiable
import Mathlib.Analysis.Meromorphic.Divisor          -- MeromorphicOn.divisor
import Mathlib.Topology.DiscreteSubset               -- codiscrete, mem_codiscrete'
import Mathlib.Topology.Compactness.Lindelof         -- HereditarilyLindelofSpace.isLindelof
import Mathlib.Algebra.BigOperators.Finprod          -- finsum_mem_* (also transitive via LocallyFinsupp)
import Mathlib.Algebra.Order.BigOperators.Group.Finset -- sum_nonneg, sum_le_sum_of_subset_of_nonneg

open Complex Filter Function
open scoped Topology ComplexConjugate
```

Name-collision scan (re-run at the pin and over `ResearchOS/`, `Ecdlp/`,
`domains/riemann-hypothesis/drafts/` during the consolidation review): **zero
hits** for all 24 scanned stems — the 23 proposed names below plus the
superseded draft name `IsCompact.inter_riemannXi_divisor_support_finite`
(Annex N, R1). `riemannXi` itself has zero hits in pinned `Mathlib/`. The only
repo hit adjacent to these stems is M13's own `riemannXi_divisor_support` in
`MULTIPLICITY_CONTRACT.md` — a proper prefix of three proposed names, not a
collision. The only pinned near-hits are `divisor_support_finite_of_subset` /
`divisor_sphere_support_finite` / `divisor_ball_support_finite`
(Divisor.lean:91/:83/:104) — distinct names, discussed under D8/N1.1.

---

## 0. Exact pinned interface (quoted from the tree at the pin)

**The ζ precedent, in full** — `Mathlib/NumberTheory/LSeries/ZetaZeros.lean`
("Discreteness of the zeros of the Riemann zeta function"):

- :33 `def riemannZetaZeros : Set ℂ := riemannZeta ⁻¹' {0}`
- :39–43 (**private**) the codiscrete engine for ζ, forced through
  `codiscreteWithin {1}ᶜ` by the pole at 1
- :46–55 (**private**) `compl_riemannZetaZeros_mem_codiscrete`, patching the
  point 1
- :57–58 `lemma isClosed_riemannZetaZeros : IsClosed riemannZetaZeros := by
  simpa using (mem_codiscrete'.mp compl_riemannZetaZeros_mem_codiscrete).1`
- :60–61 `lemma isDiscrete_riemannZetaZeros : IsDiscrete riemannZetaZeros`
  (same shape, `.2`)
- :64–67 `lemma IsCompact.inter_riemannZetaZeros_finite {S : Set ℂ}
  (hS : IsCompact S) : (S ∩ riemannZetaZeros).Finite` — proof:
  `apply (hS.inter_right isClosed_riemannZetaZeros).finite` then
  `exact isDiscrete_riemannZetaZeros.mono Set.inter_subset_right`
- :70 `lemma tendsto_riemannZeta_cofinite_cocompact` via DiscreteSubset.lean:170

Both of the ζ file's codiscreteness lemmas are `private` — **nothing from
ZetaZeros.lean is reusable for ξ**; the file is precedent (shape and idiom),
not ingredient. The ingredients:

**Codiscreteness engine** — `Mathlib/Analysis/Analytic/Order.lean`
(namespace `AnalyticOnNhd` opens :575, closes :700):
- :682 `theorem preimage_zero_mem_codiscrete [ConnectedSpace 𝕜] {x : 𝕜}
  (hf : AnalyticOnNhd 𝕜 f Set.univ) (hx : f x ≠ 0) :
  f ⁻¹' {0}ᶜ ∈ codiscrete 𝕜` — the conclusion is `f ⁻¹' ({0}ᶜ)` (postfix `ᶜ`
  binds tighter); it equals `(f ⁻¹' {0})ᶜ` by `Set.preimage_compl`
  (Image.lean:83, `rfl`)
- :664 `preimage_zero_mem_codiscreteWithin` — the within-form the ζ file
  needs; **not needed for ξ** (no pole, no excluded point)

**Codiscrete → closed/discrete** — `Mathlib/Topology/DiscreteSubset.lean`
(all root-namespace; the file has section blocks only):
- :333 `def Filter.codiscrete`
- :343 `lemma mem_codiscrete' {S : Set X} : S ∈ codiscrete X ↔ IsOpen S ∧ IsDiscrete Sᶜ`
- :188 `theorem isClosed_and_discrete_iff` (alternate splitter)
- :170 `lemma IsClosed.tendsto_coe_cofinite_of_isDiscrete`
- :148 `tendsto_cofinite_cocompact_iff : Tendsto f cofinite (cocompact _) ↔
  ∀ K, IsCompact K → Set.Finite (f ⁻¹' K)` — certifies D6 as the filter form
  of the compact-parameterized statement, with the compact still universally
  quantified

**Discreteness carrier** — `Mathlib/Topology/Constructions.lean`:
- :262 `structure IsDiscrete (s : Set X) : Prop where to_subtype : DiscreteTopology ↥s`
- :614 `lemma IsDiscrete.mono {t : Set X} (hs : IsDiscrete s) (hst : t ⊆ s) : IsDiscrete t`

**Compact-finiteness** — `Mathlib/Topology/Compactness/Compact.lean`:
- :86 `theorem IsCompact.inter_right (hs : IsCompact s) (ht : IsClosed t) : IsCompact (s ∩ t)`
- :1046 `theorem IsCompact.finite (hs : IsCompact s) (hs' : IsDiscrete s) : s.Finite`

**Countability** — `Mathlib/Topology/Compactness/Lindelof.lean`:
- :655–656 `theorem IsLindelof.countable_of_isDiscrete (hs : IsLindelof s)
  (hs' : IsDiscrete s) : s.Countable` (consumes `IsDiscrete` directly;
  `.to_subtype` applied internally at :656)
- :723 `theorem HereditarilyLindelofSpace.isLindelof [HereditarilyLindelofSpace X] (s : Set X)`
- :738 `instance (priority := 100) SecondCountableTopology.toHereditarilyLindelof`
- Instance chain to `SecondCountableTopology ℂ`: `FiniteDimensional ℝ ℂ`
  (LinearAlgebra/Complex/FiniteDimensional.lean:27) →
  `FiniteDimensional.proper_real` (Analysis/Normed/Module/FiniteDimension.lean:532,
  priority 900) → `secondCountable_of_proper`
  (Topology/MetricSpace/ProperSpace.lean:64, priority 100)

**Divisor carrier** — `Mathlib/Topology/LocallyFinsupp.lean` (root level until
`namespace Function.locallyFinsuppWithin` opens at :119, closes :695) and
`Mathlib/Analysis/Meromorphic/Divisor.lean`:
- LocallyFinsupp.lean:48 `structure Function.locallyFinsuppWithin` with fields
  `supportWithinDomain'` (:52) and `supportLocallyFiniteWithinDomain'` (:54 —
  local finiteness **only at points of `U`**)
- :61 `abbrev Function.locallyFinsupp [Zero Y] := locallyFinsuppWithin (Set.univ : Set X) Y` (reducible)
- :91 `def LocallyFiniteSupport [Zero Y] (f : X → Y) : Prop := ∀ z : X, ∃ t ∈ 𝓝 z, Set.Finite (t ∩ f.support)` (root level)
- :106 `lemma LocallyFiniteSupport.finite_inter_support_of_isCompact {W : Set X} … (hW : IsCompact W) : (W ∩ f.support).Finite` — **THE arbitrary-compact finiteness input** (root level)
- :115 `lemma Function.locallyFinsupp.locallyFiniteSupport [Zero Y] (f : locallyFinsupp X Y) : LocallyFiniteSupport f.toFun` — global local finiteness, `U = univ` only
- :125 the `FunLike` instance; :130 `@[simp] lemma toFun_eq_coe … := rfl` (attr at :128)
- :140 `lemma supportWithinDomain (D : locallyFinsuppWithin U Y) : D.support ⊆ U`
- :218 `theorem discreteSupport [Zero Y] [T1Space X] (D : locallyFinsuppWithin U Y) : IsDiscrete D.support`
- :237 `theorem closedSupport [T1Space X] [Zero Y] (D : locallyFinsuppWithin U Y) (hU : IsClosed U) : IsClosed D.support`
- :254 `theorem finiteSupport [T2Space X] [Zero Y] (D : locallyFinsuppWithin U Y) (hU : IsCompact U) : Set.Finite D.support` — **note the hypothesis shape: compactness of the domain `U`, not of an intersecting test set; this is why D8/N1.1 cannot come from :254 alone**
- :401 the `LE` instance (pointwise); :404 `lemma le_def : D₁ ≤ D₂ ↔ (D₁ : X → Y) ≤ (D₂ : X → Y)`
- Divisor.lean:39 `noncomputable def MeromorphicOn.divisor (f : 𝕜 → E) (U : Set 𝕜) : Function.locallyFinsuppWithin U ℤ` (total; junk value 0 off `U` or without meromorphy)
- Divisor.lean:71 `MeromorphicOn.AnalyticOnNhd.divisor_apply` (= M10's bridge)
- Divisor.lean:91–99 `divisor_support_finite_of_subset (hf : MeromorphicOn f U) (hU : IsCompact U) (hV : V ⊆ U) : (divisor f V).support.Finite` — the pinned near-miss: it demands the **domain** sit inside a compact, the wrong quantifier shape for neutrality; but its proof (:94–98) is the exact support-comparison pattern N1.1 reuses
- Divisor.lean:83 / :104 `divisor_sphere_support_finite` / `divisor_ball_support_finite` — the pinned **shaped** specials this package deliberately does not mirror

**Sum API audit (the carrier question, answered).** An exhaustive scan of
`Topology/LocallyFinsupp.lean` (695 lines) at the pin: the carrier exposes
**no dedicated summation operation at all** — only `coe_sum` (:368) and
`coe_finsum` (:376), which distribute the coercion over sums *of carriers*,
not sums of values over a region — plus the finiteness suppliers quoted above.
The pinned *idiom* for summing divisor values over a region — used at
`Analysis/Complex/JensenFormula.lean:235,315`,
`Analysis/Complex/ValueDistribution/LogCounting/Basic.lean:97,109,166`,
`Analysis/SpecialFunctions/Integrability/LogMeromorphic.lean:48` — is
uniformly: **`∑ᶠ` (finsum) into ℤ/ℝ, finiteness discharged by
`finiteSupport` + a compactness fact, converted to `Finset.sum` via
`Set.Finite.toFinset`.** All of those pinned uses hard-wire closed balls,
spheres, or intervals; **none is parameterized by an arbitrary compact** —
which is exactly the gap N1 fills, without the shapes.

**finsum combinators** — `Mathlib/Algebra/BigOperators/Finprod.lean`, all as
`@[to_additive]` twins (attribute verified at each cited line; the additive
*names* are compiler-generated — obligation S1N1-SUM):
- :499–501 `finprod_mem_eq_prod (f) (hf : (s ∩ mulSupport f).Finite) : ∏ᶠ i ∈ s, f i = ∏ i ∈ hf.toFinset, f i` → `finsum_mem_eq_sum`
- :565–566 `finprod_mem_congr (h₀ : s = t) (h₁ : ∀ x ∈ t, f x = g x)` → `finsum_mem_congr` (in-tree additive usage precedent: Data/Set/Card/Arithmetic.lean:112)
- :929–936 `finprod_mem_image {s : Set β} {g : β → α} (hg : s.InjOn g) : ∏ᶠ i ∈ g '' s, f i = ∏ᶠ j ∈ s, f (g j)` → `finsum_mem_image` — **hypothesis-free on finiteness**
- fallbacks: `finprod_mem_eq_prod_of_subset` :495, `finprod_mem_eq_prod_of_inter_mulSupport_eq` :481, `finprod_mem_inter_mulSupport` :543

**Order/sum lemmas** — `Mathlib/Algebra/Order/BigOperators/Group/Finset.lean`
(namespace `Finset` :32):
- :119–120 `@[to_additive sum_nonneg] theorem one_le_prod'`
- :131–132 `@[to_additive (attr := gcongr) sum_le_sum_of_subset_of_nonneg] theorem prod_le_prod_of_subset_of_one_le' (h : s ⊆ t) (hf : ∀ i ∈ t, i ∉ s → 1 ≤ f i)` (additive name explicit in the attribute — **not** generated)

**Small glue** (each verified at the pin): `Set.preimage_compl` —
Data/Set/Image.lean:83 (`rfl`); `Set.inter_subset_right` —
Data/Set/Basic.lean:772 (implicit-argument form `{s t}` at this pin);
`Set.inter_subset_inter` — Basic.lean:814; `Set.Subset.rfl` — Basic.lean:268;
`Set.Finite.subset` — Data/Set/Finite/Basic.lean:497;
`Set.Finite.toFinset_subset_toFinset` — Finite/Basic.lean:149 (protected,
`@[gcongr, mono]` at :148; alias `toFinset_mono` :156);
`Set.Countable.mono {s₁ s₂} (h : s₁ ⊆ s₂) (hs : s₂.Countable)` —
Data/Set/Countable.lean:115 (subset argument **first**);
`Set.countable_iUnion` — Countable.lean:214; `Set.Finite.countable` —
Countable.lean:256; `Complex.analyticOnNhd_univ_iff_differentiable` —
Analysis/Complex/CauchyIntegral.lean:678 (namespace `Complex` opens :173);
`ConnectedSpace ℂ` via `NormedSpace.instPathConnectedSpace`
(Analysis/Normed/Module/Convex.lean:168, priority 100) +
`PathConnectedSpace.connectedSpace` (Topology/Connected/PathConnected.lean:607,
priority 100); `sub_sub_cancel` — additive twin of `div_div_cancel`,
Algebra/Group/Basic.lean:933 (attr `@[to_additive (attr := simp)]` :932);
`Function.Involutive.leftInverse` / `.rightInverse` / `.injective` —
Logic/Function/Basic.lean:1022 / :1028 / :1030;
`Set.injOn_of_injective` — Data/Set/Function.lean:295 (namespace `Set` :33);
`Set.mem_image_iff_of_inverse` — Data/Set/Image.lean:355 (namespace `Set`
:45–:1076); `Function.Involutive.image_eq_preimage_symm` — Image.lean:351
(declared `_root_.`); `starRingEnd_self_apply` —
Algebra/Star/Basic.lean:348; `map_sub` — additive twin of `map_div`,
Algebra/Group/Hom/Defs.lean:461 (applies to `starRingEnd ℂ` through
`RingHomClass`; explicit fallback `RingHom.map_sub`,
Algebra/Ring/Hom/Defs.lean:500); `map_one` — Hom/Defs.lean:234;
`Pi.zero_apply` — additive twin of `Pi.one_apply`,
Algebra/Notation/Pi/Defs.lean:49; `Int.toNat_of_nonneg` — Lean core, in scope
everywhere at the pin (usage precedent Mathlib/NumberTheory/Pell.lean:472).

---

## 1. Spelling and unification decisions

### Decision 1: zero defs; one spelling per object

The ξ zero set is `riemannXi ⁻¹' {0}` inline everywhere (M13's spelling).
Divisor support is spelled
`Function.support (MeromorphicOn.divisor riemannXi U)` in every signature —
the spelling M13's left-hand side uses — with the `D.support`-vs-`⇑D` seam
recorded as obligation N2-f; **one spelling must be fixed package-wide at
build time and recorded**. The compact sum is the spelling
`∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z : ℤ`, with N1.2 as the recorded
bridge to `Finset.sum`. No `def` anywhere (death condition 4).

### Decision 2: the D8/N1.1 unification (Annex N, finding R1)

The two designer halves each proposed the same proposition — for arbitrary
`U` and arbitrary compact `K`,
`(K ∩ Function.support (MeromorphicOn.divisor riemannXi U)).Finite` — under
two names and two proof routes. It is stated **once** below, as **N1.1 = N2-D8**,
under the name `riemannXi_divisor_inter_support_finite` (retained because
N1.2's *statement* names its proof term). The superseded draft name
`IsCompact.inter_riemannXi_divisor_support_finite` is not stated. Both proof
routes are recorded:

- **Primary (route via `Set.univ` comparison; M9+M10 only):** compare the
  `U`-divisor's support with the `univ`-divisor's support (M10 at `U` and at
  `Set.univ` — both evaluate to the same `untop₀`-order at points of `U`),
  then apply LocallyFinsupp.lean:115 + :106 to the `univ` divisor. Does not
  touch M13.
- **Alternative (route via M13):** rewrite the support to
  `U ∩ riemannXi ⁻¹' {0}` by M13 and shrink to D4's finite set
  `K ∩ riemannXi ⁻¹' {0}`.

Both routes consume only M-package prerequisites from the same `RH-010`
promotion, so the sequencing is identical; the primary route is primary
because it keeps the finiteness layer independent of M13's statement shape.

### Decision 3: the boundary-accumulation honesty note (why N1.1 is a ξ theorem, not a carrier theorem)

For a general `D : locallyFinsuppWithin U Y`, local finiteness of the support
is guaranteed **only at points of `U`** (LocallyFinsupp.lean:54). If `U` is
open and `K` is a compact meeting `∂U`, `K ∩ D.support` can be infinite — a
Blaschke-type divisor on the open unit disk with zeros accumulating at a
boundary point, against `K` = closed disk, is a counterexample. So the
fully-`K`-neutral statement (arbitrary compact `K`, **no** `K ⊆ U`
hypothesis) is *false generically* and *true for ξ* precisely because ξ is
entire: the `Set.univ` divisor dominates. This is the load-bearing use of
repo:`Xi.lean:46`. A generic `[GEN]` variant with the extra hypothesis
`K ⊆ U` is true by finite subcover, is **not at the pin** (scan of
LocallyFinsupp.lean confirms no such lemma), and is not needed here
(N-DEFERRED-1). **Do not state the hypothesis-free generic form: it is
false.**

---

## 2. Statement list

Legend: `[PIN]` provable from pinned Mathlib + kernel-checked `main` alone;
`[MULT: …]` additionally consumes the named M-package prerequisites (`RH-010`
promotion in flight — package prerequisites, not kernel-checked tonight);
`[GEN]` generic, natural Mathlib upstream.

### Block A — topology of the ξ zero set (N2-D1 … N2-D6)

## N2-D1. The complement of the ξ zero set is codiscrete `[PIN]` — the engine

```lean
theorem compl_riemannXi_zeroSet_mem_codiscrete :
    (riemannXi ⁻¹' {0})ᶜ ∈ Filter.codiscrete ℂ := by
  have hA : AnalyticOnNhd ℂ riemannXi Set.univ :=
    Complex.analyticOnNhd_univ_iff_differentiable.mpr differentiable_riemannXi
  have h0 : riemannXi 0 ≠ 0 := by rw [riemannXi_zero]; norm_num
  simpa only [Set.preimage_compl] using hA.preimage_zero_mem_codiscrete h0
```

Design note: strictly simpler than the ζ precedent (ZetaZeros.lean:39–55),
which needs the `codiscreteWithin {1}ᶜ` detour, a punctured-plane
connectivity lemma, and an `eventually_ne_zero` patch at the pole. ξ is entire
with no excluded point, so the `[ConnectedSpace 𝕜]` global lemma
Order.lean:682 applies in one stroke. Nonvanishing witness: `x := 0` via
`riemannXi_zero` (repo:`Xi.lean:72`); alternate witness
`riemannXi_ne_zero_of_one_le_re` (repo:`Xi.lean:157`) at `s := 2`, mirroring
the ζ file's witness choice.

Pinned dependencies: Order.lean:682 (namespace `AnalyticOnNhd` :575–:700; dot
notation on `hA` resolves); CauchyIntegral.lean:678; Image.lean:83;
DiscreteSubset.lean:333; repo:`Xi.lean:46`, repo:`Xi.lean:72`.

Obligations: **N2-a** (MEDIUM) — `ConnectedSpace ℂ` instance resolution
(Convex.lean:168 → PathConnected.lean:607); same class as the M-package's
S1M-12a; narrow instance check required, do not assume. **N2-b** (LOW) — the
pinned conclusion is `riemannXi ⁻¹' {0}ᶜ`; the stated form is
`Set.preimage_compl` away (a `rfl` at the pin), so `exact` may already close
it; fallback: state D1 in the pinned orientation and let D2/D3 do the flip.

**All-ingredients-pinned verdict: YES** (no package prerequisite).

## N2-D2 / N2-D3. The ξ zero set is closed and is discrete `[PIN]`

```lean
theorem isClosed_riemannXi_zeroSet : IsClosed (riemannXi ⁻¹' {0}) := by
  simpa using (mem_codiscrete'.mp compl_riemannXi_zeroSet_mem_codiscrete).1

theorem isDiscrete_riemannXi_zeroSet : IsDiscrete (riemannXi ⁻¹' {0}) := by
  simpa using (mem_codiscrete'.mp compl_riemannXi_zeroSet_mem_codiscrete).2
```

Verbatim the ζ idiom (ZetaZeros.lean:57–61) with the ξ engine substituted.

Pinned dependencies: D1; DiscreteSubset.lean:343 (root namespace — the ζ file
uses it unqualified at :58); Constructions.lean:262.

Obligations: **N2-c** (LOW) — the bare `simpa` normalization of
`isOpen_compl_iff`/`compl_compl`; precedent: the identical bare `simpa`
compiles at the pin at ZetaZeros.lean:58/:61; fallback `simpa only [...]`.

**All-ingredients-pinned verdict: YES.**

## N2-D4. Finite intersection with an ARBITRARY compact set `[PIN]` — the neutrality carrier

```lean
theorem IsCompact.inter_riemannXi_zeroSet_finite {K : Set ℂ} (hK : IsCompact K) :
    (K ∩ riemannXi ⁻¹' {0}).Finite := by
  apply (hK.inter_right isClosed_riemannXi_zeroSet).finite
  exact isDiscrete_riemannXi_zeroSet.mono Set.inter_subset_right
```

**Neutrality (load-bearing).** `K` is an arbitrary compact set — the exact
quantifier shape of the pinned ζ precedent (ZetaZeros.lean:64). No
instantiation at `Metric.closedBall`, no `{ρ | ‖ρ‖ ≤ T}`, no
`{ρ | |ρ.im| < T}` appears in this package: any such instantiation commits to
a cutoff geometry, which is a route selection, and all routes are PARKED. A
future dated route decision instantiates D4 at its chosen shape in one line;
this package refuses to make that choice for it.

Pinned dependencies: D2, D3; Compact.lean:86, :1046; Constructions.lean:614;
Basic.lean:772. Proof shape verbatim ZetaZeros.lean:65–67.

Obligations: **N2-h(i)** (LOW) — `Set.inter_subset_right` implicit-argument
form; the ζ precedent passes it bare in exactly this position
(ZetaZeros.lean:67), a mirrored idiom, not a guess.

**All-ingredients-pinned verdict: YES.**

## N2-D5. The ξ zero set is countable `[PIN]` — beyond the ζ precedent

```lean
theorem countable_riemannXi_zeroSet : (riemannXi ⁻¹' {0}).Countable :=
  (HereditarilyLindelofSpace.isLindelof (riemannXi ⁻¹' {0})).countable_of_isDiscrete
    isDiscrete_riemannXi_zeroSet
```

The pinned ζ file does **not** state countability; DEFERRED-2 names it
explicitly, so it is stated here. Two-lemma consequence of D3 in a
second-countable space; adds no route-shaped content — `Set.Countable`
produces the *existence* of an injection into ℕ, never a chosen listing, so
no enumeration and no ordering of zeros is introduced.

Pinned dependencies: D3; Lindelof.lean:723, :655; instance chain
FiniteDimensional.lean:27 → FiniteDimension.lean:532 → ProperSpace.lean:64 →
Lindelof.lean:738.

Obligations: **N2-d** (MEDIUM) — the four-link instance chain to
`HereditarilyLindelofSpace ℂ` must resolve by instance search; every link is a
priority-tagged instance at the pin, but this is the longest inference chain
in the package — narrow instance check required. **Fallback (statement
unchanged, proof-internal exhaustion — permitted by the neutrality rule):**
`riemannXi ⁻¹' {0} = ⋃ n : ℕ, (Metric.closedBall 0 n ∩ riemannXi ⁻¹' {0})` by
archimedean choice, then `Set.countable_iUnion` (Countable.lean:214) of the
D4-finite pieces via `Set.Finite.countable` (Countable.lean:256) and
`isCompact_closedBall`. The closed balls are proof scaffolding for a
shape-free statement, not a signature-level cutoff. **N2-c′** (LOW) —
`countable_of_isDiscrete` consumes `IsDiscrete` directly (Lindelof.lean:656);
no manual coercion.

**All-ingredients-pinned verdict: YES** (modulo pinned-instance-only search).

## N2-D6. Zeros escape every compact (filter form) `[PIN]` — optional

```lean
theorem tendsto_riemannXi_zeroSet_cofinite_cocompact :
    Filter.Tendsto ((↑) : (riemannXi ⁻¹' {0} : Set ℂ) → ℂ)
      Filter.cofinite (Filter.cocompact ℂ) :=
  isClosed_riemannXi_zeroSet.tendsto_coe_cofinite_of_isDiscrete
    isDiscrete_riemannXi_zeroSet
```

Marked **optional**: it repackages D4 as a filter statement — by
`tendsto_cofinite_cocompact_iff` (DiscreteSubset.lean:148) it is literally
"the preimage of every compact is finite", compact still universally
quantified, so still neutral. Included because the ζ precedent ships it
(ZetaZeros.lean:70) and downstream route work tends to want the filter form;
droppable without weakening the package.

Pinned dependencies: D2, D3; DiscreteSubset.lean:170; neutrality certificate
DiscreteSubset.lean:148.

Obligations: **N2-e** (LOW) — the subtype-coercion source ascription without a
zero-set def; fallback `show … from …` or a tactic-local `set`.

**All-ingredients-pinned verdict: YES.**

### Block B — topology of the ξ divisor support (N2-D7, N1.1 = N2-D8, N2-D9)

## N2-D7. The ξ divisor has discrete support (any `U`) and closed support (closed `U`) `[PIN]` — carrier level

```lean
theorem isDiscrete_riemannXi_divisor_support (U : Set ℂ) :
    IsDiscrete (Function.support (MeromorphicOn.divisor riemannXi U)) :=
  (MeromorphicOn.divisor riemannXi U).discreteSupport

theorem isClosed_riemannXi_divisor_support {U : Set ℂ} (hU : IsClosed U) :
    IsClosed (Function.support (MeromorphicOn.divisor riemannXi U)) :=
  (MeromorphicOn.divisor riemannXi U).closedSupport hU
```

Honesty note: these two are **carrier facts** — `locallyFinsuppWithin`
support is discrete by construction (LocallyFinsupp.lean:218) for the divisor
of *any* function whatsoever (Divisor.lean:39 is total, junk value 0 where
meromorphy fails). They acquire multiplicity **content** only through M13
(support = zero set) and M10 (value = order); stated here so the divisor side
is closed under the same three topological predicates as Block A. `U` is
arbitrary (D7a) or arbitrary-closed (D7b) — no shape.

Pinned dependencies: Divisor.lean:39; LocallyFinsupp.lean:218 (`[T1Space ℂ]`
from the metric instance), :237; repo:`Xi.lean:41` (the function only).

Obligations: **N2-f** (MEDIUM) — the `D.support` (dot, LocallyFinsupp.lean
:140/:218/:237) vs `Function.support ⇑D` (coercion, :125) spelling seam
against M13's spelling; the two must elaborate to the same term. Precedent
that the mixed spelling round-trips: Divisor.lean:91–99. Pick ONE spelling
package-wide at build time and record it (Decision 1).

**All-ingredients-pinned verdict: YES** (does not even need M9).

## N1.1 = N2-D8. Divisor support meets every compact in a finite set (arbitrary `U`, arbitrary `K`) `[MULT: M9, M10]` — the multiplicity-aware statement

```lean
theorem riemannXi_divisor_inter_support_finite (U : Set ℂ) {K : Set ℂ} (hK : IsCompact K) :
    (K ∩ Function.support (MeromorphicOn.divisor riemannXi U)).Finite
```

Primary proof skeleton (the `Set.univ`-comparison route, M9+M10 only — the
same support-comparison pattern Mathlib itself uses at Divisor.lean:94–98):

```lean
  apply Set.Finite.subset
    ((Function.locallyFinsupp.locallyFiniteSupport
        (MeromorphicOn.divisor riemannXi Set.univ)).finite_inter_support_of_isCompact hK)
  apply Set.inter_subset_inter Set.Subset.rfl
  intro z hz
  have hzU : z ∈ U := (MeromorphicOn.divisor riemannXi U).supportWithinDomain hz
  rw [Function.mem_support] at hz ⊢
  rw [riemannXi_divisor_apply (Set.mem_univ z)]      -- M10 at Set.univ
  rwa [riemannXi_divisor_apply hzU] at hz            -- M10 at U
```

Both M10 instances rewrite to the same RHS
`((analyticOrderAt riemannXi z).map (↑)).untop₀`, so the `≠ 0` fact
transports. Alternative skeleton (the M13 route):

```lean
  refine Set.Finite.subset hK.inter_riemannXi_zeroSet_finite ?_    -- N2-D4
  rw [riemannXi_divisor_support U]                                  -- M13 (PACKAGE PREREQUISITE)
  exact fun x hx => ⟨hx.1, hx.2.2⟩                                  -- K ∩ (U ∩ Z) ⊆ K ∩ Z
```

Why the pin alone does not suffice: the pinned carrier route (`finiteSupport`
:254 and its wrapper Divisor.lean:91) requires the **domain** compact or
compactly contained — the wrong quantifier shape for neutrality, since it
would force the statement to carry a compact domain (a cutoff on where the
divisor lives). Entirety of ξ (through M9/M10, or M13) removes that; this is
the load-bearing content of Decision 3. This is also the precise sense in
which the package is *multiplicity-aware*: with M13 the intersected set is
`K ∩ U ∩ riemannXi ⁻¹' {0}` — **every compact meets only finitely many
ξ-zeros of `U`** — and with M10 each of its finitely many points carries its
local analytic order as the divisor value (M12 guaranteeing that value is an
honest positive multiplicity, not `untop₀` junk). The finite set this
statement produces is the multiplicity-decorated zero data the Block-C sums
are indexed by.

Dependencies: **M9, M10 (primary route)** or **D4 + M13 (alternative route)**
— all PACKAGE PREREQUISITES from the same `RH-010` promotion;
LocallyFinsupp.lean:106, :115, :140; Finite/Basic.lean:497; Basic.lean:814,
:268.

Obligations: **N-SEQ** (**HIGH — the package's sequencing obligation**,
shared with D9 and every `[MULT]` statement): no proof route exists at this
pin without the M-package; if the `RH-010` promotion does not land, the only
alternative is re-deriving M9–M13 inline here, which would duplicate an
accepted surface — **forbidden. Land the `[MULT]` statements only after the
Mult module is kernel-checked and promoted; never split M-package content
into this package.** Not an analytic risk; purely ordering. **S1N1-1a**
(MEDIUM) — the finiteness term from :115/:106 is stated at
`(divisor … univ).toFun.support`, the goal at coercion-form support; defeq
via the `rfl`-simp `toFun_eq_coe` (:130), but `apply Set.Finite.subset` must
see through it; fallback `simp only [toFun_eq_coe]` on a `have`-bound copy.
**S1N1-1b** (LOW) — root-namespace resolution of
`LocallyFiniteSupport.finite_inter_support_of_isCompact` (:106 is above the
namespace block at :119; verified); fallback fully-qualified. **N2-h(ii)**
(LOW, alternative route only) — the nested-`And` membership term
`⟨hx.1, hx.2.2⟩`; fallback via `simp only [Set.mem_inter_iff]`. **N2-f**
applies (spelling seam; M13's equation is oriented support-to-zero-set, so
the alternative route's `rw` is forward, no `.symm`).

**All-ingredients verdict: pinned + M-package prerequisite (either route).
Becomes provable the moment the `RH-010` promotion merges; nothing else is
waited on.**

## N2-D9. Divisor support is countable (arbitrary `U`) `[MULT: M13]`

```lean
theorem countable_riemannXi_divisor_support (U : Set ℂ) :
    (Function.support (MeromorphicOn.divisor riemannXi U)).Countable := by
  rw [riemannXi_divisor_support U]                                  -- M13 (PACKAGE PREREQUISITE)
  exact Set.Countable.mono Set.inter_subset_right countable_riemannXi_zeroSet  -- N2-D5
```

Here M13 has no M13-free replacement that does not re-derive its content
(death condition 5), so D9 is the one statement genuinely pinned to the M13
seam.

Dependencies: D5 `[PIN]`; M13 (PACKAGE PREREQUISITE); Countable.lean:115
(subset argument **first** — the explicit application above is
argument-order-safe); Basic.lean:772.

Obligations: **N-SEQ** (HIGH, shared). **N2-i** (LOW) — `Set.Countable.mono`
argument order; dot form `countable_riemannXi_zeroSet.mono …` also elaborates
at this pin, explicit form recorded as primary.

**All-ingredients verdict: pinned + M13 package prerequisite.**

### Block C — the sum over an arbitrary compact is a well-defined finite (natural) number (N1.2 – N1.5)

## N1.2. The finsum over `K` is the honest finite sum `[MULT via N1.1]` — well-definedness bridge

```lean
theorem riemannXi_divisor_finsum_mem_eq_sum (U : Set ℂ) {K : Set ℂ} (hK : IsCompact K) :
    ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z
      = ∑ z ∈ (riemannXi_divisor_inter_support_finite U hK).toFinset,
          MeromorphicOn.divisor riemannXi U z :=
  finsum_mem_eq_sum _ (riemannXi_divisor_inter_support_finite U hK)
```

Pinned dependencies: `finsum_mem_eq_sum` — additive twin of Finprod.lean
:499–501 (`@[to_additive]` verified at :499); N1.1. `Set.Finite.toFinset` is
proof-irrelevant in its `Set.Finite` argument, so naming the N1.1 term in the
statement is stable.

Obligations: **S1N1-SUM** (**MEDIUM — the block's naming obligation**): the
additive names `finsum_mem_eq_sum` / `finsum_mem_image` are
**compiler-generated** by `@[to_additive]` (Finprod.lean:499/:929) and appear
nowhere in source at the pin (re-verified by grep during consolidation);
in-tree usage precedent exists for `finsum_mem_congr`
(Data/Set/Card/Arithmetic.lean:112) but not for the other two. Cost if a
generated name differs: one CI cycle. Fallbacks: twins of Finprod.lean
:495/:481/:543, or `#check` probing in the promotion PR. **S1N1-2** (LOW) —
eta between `support ⇑D` and `support (fun z => D z)` (definitional in
Lean 4); fallback: restate N1.1 with the lambda.

## N1.3. Nonnegativity `[MULT: M11]`, and N1.4. the natural-number reading

```lean
theorem riemannXi_divisor_finsum_mem_nonneg (U : Set ℂ) {K : Set ℂ} (hK : IsCompact K) :
    0 ≤ ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z

theorem riemannXi_divisor_finsum_mem_toNat (U : Set ℂ) {K : Set ℂ} (hK : IsCompact K) :
    ((∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z).toNat : ℤ)
      = ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z
```

Proof skeletons:

```lean
  -- N1.3
  rw [riemannXi_divisor_finsum_mem_eq_sum U hK]
  exact Finset.sum_nonneg fun z _ => by
    simpa using Function.locallyFinsuppWithin.le_def.mp (riemannXi_divisor_nonneg U) z
  -- N1.4
  exact Int.toNat_of_nonneg (riemannXi_divisor_finsum_mem_nonneg U hK)
```

N1.4 is the honest form of "the sum is a natural number": the ℤ-valued sum
equals the cast of its `toNat`. **No ℕ-valued definition and no named
counting object is introduced** (death condition 4; N-DEFERRED-2) — this is a
cast identity, not a counting function.

Pinned dependencies: `Finset.sum_nonneg` — Group/Finset.lean:119–120
(namespace `Finset` :32); LocallyFinsupp.lean:404 (`le_def`; the `LE`
instance :401 is the pointwise function order — exactly the order M11 is
stated in); `Pi.zero_apply` — Pi/Defs.lean:49; `Int.toNat_of_nonneg` — Lean
core (precedent Pell.lean:472). Package: M11.

Obligations: **S1N1-3** (LOW) — pointwise extraction from M11 crosses the
`FunLike` seam and the Pi order: `le_def.mp … : (0 : ℂ → ℤ) ≤ ⇑D`, applied at
`z` (Pi `≤` unfolds definitionally; `Pi.le_def` if not), then `Pi.zero_apply`
inside the `simpa`. Fallback: bind with `have` and `simpa using this`.

## N1.5. Monotonicity under `K₁ ⊆ K₂` `[MULT: M10, M11]`

```lean
theorem riemannXi_divisor_finsum_mem_mono (U : Set ℂ) {K₁ K₂ : Set ℂ}
    (hK₂ : IsCompact K₂) (hK : K₁ ⊆ K₂) :
    ∑ᶠ z ∈ K₁, MeromorphicOn.divisor riemannXi U z
      ≤ ∑ᶠ z ∈ K₂, MeromorphicOn.divisor riemannXi U z
```

Note the deliberate asymmetry: **only `K₂` need be compact** — `K₁` inherits
finiteness by inclusion (`K₁ ∩ support ⊆ K₂ ∩ support`), so both sums are
honest finite sums and no junk-value caveat arises. This is strictly more
`K`-neutral than requiring both compact.

Proof skeleton:

```lean
  have h₂ := riemannXi_divisor_inter_support_finite U hK₂
  have h₁ : (K₁ ∩ Function.support (MeromorphicOn.divisor riemannXi U)).Finite :=
    h₂.subset (Set.inter_subset_inter hK Set.Subset.rfl)
  rw [finsum_mem_eq_sum _ h₁, finsum_mem_eq_sum _ h₂]
  apply Finset.sum_le_sum_of_subset_of_nonneg
  · exact Set.Finite.toFinset_subset_toFinset.mpr (Set.inter_subset_inter hK Set.Subset.rfl)
  · intro z _ _
    simpa using Function.locallyFinsuppWithin.le_def.mp (riemannXi_divisor_nonneg U) z
```

Pinned dependencies: `Finset.sum_le_sum_of_subset_of_nonneg` — additive twin
**explicitly named in the attribute** at Group/Finset.lean:131 (`(h : s ⊆ t)
(hf : ∀ i ∈ t, i ∉ s → 0 ≤ f i)`, verified verbatim);
`Set.Finite.toFinset_subset_toFinset` — Finite/Basic.lean:149 (`@[gcongr,
mono]` at :148, re-verified; alias `toFinset_mono` :156); Basic.lean:814;
N1.1/N1.2 kit; package M10 (via N1.1), M11.

Obligations: **S1N1-5** (MEDIUM) — the two `toFinset`s in the post-`rw` goal
are attached to the specific proof terms `h₁`, `h₂`;
`toFinset_subset_toFinset.mpr` must unify its implicit `{hs} {ht}` with
exactly those (proof irrelevance guarantees the values; the elaborator must
pick them from the goal). Fallback: `gcongr` (both :131 and :148–149 carry
the attr — re-verified), or `Set.Finite.toFinset_mono` explicitly.

### Block D — invariance under the three symmetries, parameterized by `K` (N1.6 – N1.8)

Each symmetry gets two signatures: a **summand-transport** form (arbitrary
`K`, pure congruence from the M14/M15 pointwise divisor identities) and an
**enumeration-transport** ("image") form — *the* invariance statement:
pushing `K` through the symmetry does not change the sum. Neither form
requires `K` compact: `finsum_mem_congr` and `finsum_mem_image` are
hypothesis-free on finiteness (verified at Finprod.lean:565/:929), and on
infinite-support windows both sides take the same junk value, so the
equations are unconditionally true and unconditionally stated. **No separate
symmetric-`K` divisor signature is stated: after N1.9 rewrites the
enumeration set, the two sides are the same term; recording a variant
carrying an unused `hK` hypothesis would be a false dependency** (the
pointwise divisor symmetry is global — `K`-symmetry is never load-bearing at
the sum level, which is exactly why N1.9 is exported as a standalone set
identity).

## N1.6. Reflection `s ↦ 1 - s` `[MULT: M14]`

```lean
theorem riemannXi_divisor_finsum_mem_comp_one_sub {U : Set ℂ}
    (hU : ∀ z : ℂ, (1 - z) ∈ U ↔ z ∈ U) (K : Set ℂ) :
    ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U (1 - z)
      = ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z

theorem riemannXi_divisor_finsum_mem_image_one_sub {U : Set ℂ}
    (hU : ∀ z : ℂ, (1 - z) ∈ U ↔ z ∈ U) (K : Set ℂ) :
    ∑ᶠ z ∈ (fun w : ℂ => 1 - w) '' K, MeromorphicOn.divisor riemannXi U z
      = ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z
```

Proof skeletons:

```lean
  -- comp form
  exact finsum_mem_congr rfl fun z _ => riemannXi_divisor_one_sub hU z     -- M14
  -- image form
  have hinv : Function.Involutive (fun w : ℂ => 1 - w) := fun w => sub_sub_cancel 1 w
  rw [finsum_mem_image (Set.injOn_of_injective hinv.injective)]
  exact riemannXi_divisor_finsum_mem_comp_one_sub hU K
```

The symmetry hypothesis `hU` is M14's own hypothesis shape, verbatim
(`MULTIPLICITY_CONTRACT.md:1098–1099`, re-verified).

Pinned dependencies: Finprod.lean:565–566, :929–936; Group/Basic.lean:933;
Logic/Function/Basic.lean:1030; Data/Set/Function.lean:295. Package: M14.

Obligations: **S1N1-6** (LOW, finding-A2 class): after
`rw [finsum_mem_image …]` the summand carries the beta-redex
`D ((fun w => 1 - w) z)`; as in the M-contract's M3 (and unlike M2) the redex
sits under an `exact`, which works up to defeq — no syntactic rewrite must
see through it. Fallback `simpa using …`.

## N1.7. Conjugation `s ↦ conj s` `[MULT: M15]` (hence `[CONJ]` provenance, repo:`Conj.lean:452`, merged PR #307)

```lean
theorem riemannXi_divisor_finsum_mem_comp_conj {U : Set ℂ}
    (hU : ∀ z : ℂ, (starRingEnd ℂ) z ∈ U ↔ z ∈ U) (K : Set ℂ) :
    ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U ((starRingEnd ℂ) z)
      = ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z

theorem riemannXi_divisor_finsum_mem_image_conj {U : Set ℂ}
    (hU : ∀ z : ℂ, (starRingEnd ℂ) z ∈ U ↔ z ∈ U) (K : Set ℂ) :
    ∑ᶠ z ∈ (starRingEnd ℂ) '' K, MeromorphicOn.divisor riemannXi U z
      = ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z
```

Skeletons identical to N1.6 with `riemannXi_divisor_conj hU z` (M15) in the
congruence and
`hinv : Function.Involutive ⇑(starRingEnd ℂ) := fun z => starRingEnd_self_apply z`.

Pinned dependencies: Star/Basic.lean:348; the N1.6 finsum/injectivity kit.
Package: M15 (which itself consumes the merged conjugation package).

Obligations: **S1N1-7a** (LOW) — `(starRingEnd ℂ) '' K` needs the
`RingHom → function` coercion under `Set.image`; fallback: explicit lambda.
**S1N1-7b** (LOW) — do not reach for `Complex.conj_conj`: no such name at the
pin; `starRingEnd_self_apply` is the pinned spelling.

## N1.8. Composite `s ↦ 1 - conj s` `[MULT: M15]`

```lean
theorem riemannXi_divisor_finsum_mem_comp_one_sub_conj {U : Set ℂ}
    (hU₁ : ∀ z : ℂ, (1 - z) ∈ U ↔ z ∈ U)
    (hU₂ : ∀ z : ℂ, (starRingEnd ℂ) z ∈ U ↔ z ∈ U) (K : Set ℂ) :
    ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U (1 - (starRingEnd ℂ) z)
      = ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z

theorem riemannXi_divisor_finsum_mem_image_one_sub_conj {U : Set ℂ}
    (hU₁ : ∀ z : ℂ, (1 - z) ∈ U ↔ z ∈ U)
    (hU₂ : ∀ z : ℂ, (starRingEnd ℂ) z ∈ U ↔ z ∈ U) (K : Set ℂ) :
    ∑ᶠ z ∈ (fun w : ℂ => 1 - (starRingEnd ℂ) w) '' K, MeromorphicOn.divisor riemannXi U z
      = ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z
```

Skeletons as N1.6 with `riemannXi_divisor_one_sub_conj hU₁ hU₂ z` (M15) and

```lean
  have hinv : Function.Involutive (fun w : ℂ => 1 - (starRingEnd ℂ) w) := fun z => by
    simp only [map_sub, map_one, starRingEnd_self_apply, sub_sub_cancel]
```

Mirroring M15's own note: **neither symmetry hypothesis alone stabilizes
`1 - conj ·`**; both `hU₁` and `hU₂` are required, in the same order M15
takes them (`MULTIPLICITY_CONTRACT.md:1176–1178`, re-verified).

Pinned dependencies: Hom/Defs.lean:461 (`map_sub` via `RingHomClass`;
fallback `RingHom.map_sub`, Ring/Hom/Defs.lean:500), :234;
Star/Basic.lean:348; Group/Basic.lean:933. Package: M15.

Obligations: **S1N1-8** (LOW) — the involution `simp only` chain must close
`1 - conj (1 - conj z) = z`; fallback calc via `map_sub`/`map_one`/
`starRingEnd_self_apply` then `sub_sub_cancel 1 z`.

### Block E — the symmetric-window set identities (N1.9) `[GEN]` `[PIN]` — the `hK`-consuming lemmas

```lean
theorem image_one_sub_of_symm {K : Set ℂ} (hK : ∀ z : ℂ, (1 - z) ∈ K ↔ z ∈ K) :
    (fun w : ℂ => 1 - w) '' K = K

theorem image_conj_of_symm {K : Set ℂ} (hK : ∀ z : ℂ, (starRingEnd ℂ) z ∈ K ↔ z ∈ K) :
    (starRingEnd ℂ) '' K = K

theorem image_one_sub_conj_of_symm {K : Set ℂ}
    (hK : ∀ z : ℂ, (1 - (starRingEnd ℂ) z) ∈ K ↔ z ∈ K) :
    (fun w : ℂ => 1 - (starRingEnd ℂ) w) '' K = K
```

Proof skeleton (one_sub; the others substitute their involution witness):

```lean
  have hinv : Function.Involutive (fun w : ℂ => 1 - w) := fun w => sub_sub_cancel 1 w
  ext z
  rw [Set.mem_image_iff_of_inverse hinv.leftInverse hinv.rightInverse]
  exact hK z
```

*Role.* These are the only statements in the contract where "`K` is
symmetric" does any work. Composed with the N1.6–N1.8 image forms they give,
for symmetric `K`, that `∑ᶠ z ∈ K, divisor ξ U z` is **literally fixed** by
each of the three symmetries; they are exported standalone because future
route bookkeeping will consume `σ '' K = K` directly. Note they are generic
set identities over ℂ — no divisor content, no package prerequisite, natural
Mathlib upstream (`[GEN]`).

Pinned dependencies: Image.lean:355; Logic/Function/Basic.lean:1022, :1028
(corrected locators — Annex N, R4); involution witnesses as in N1.6–N1.8.
Alternative route: `Function.Involutive.image_eq_preimage_symm`
(Image.lean:351, declared `_root_.`) plus `Set.ext hK`.

Obligations: **S1N1-9** (LOW) — after `ext z; rw [...]` the membership goal
carries a beta-redex; `exact hK z` closes up to defeq; fallback `show`.

**Verdicts (Blocks C–E):** N1.2–N1.5 — pinned + M-package (M10/M11 through
N1.1). N1.6 — pinned + M14. N1.7/N1.8 — pinned + M15 (which carries the
merged, kernel-checked `Conj.lean:452` on `main`). N1.9 — **fully pinned,
nothing else.**

---

## Obligation register

| ID | Statement | Severity | Content | Fallback recorded |
|---|---|---|---|---|
| **N-SEQ** | N1.1/D8, D9, N1.2–N1.8 | **HIGH** | every `[MULT]` statement is sequenced behind the `RH-010` kernel promotion of the M-package; no proof route exists at this pin without it, and inline re-derivation of M9–M15 content is forbidden | yes (sequencing: land after the Mult promotion merges; never split M-package content) |
| N2-a | D1 | MEDIUM | `ConnectedSpace ℂ` instance resolution (Convex.lean:168 → PathConnected.lean:607); mirrors S1M-12a | yes (chain spelled; `inferInstance` probe) |
| N2-d | D5 | MEDIUM | four-link instance chain to `HereditarilyLindelofSpace ℂ` | yes (closed-ball exhaustion via D4 — proof-internal, statement stays shape-free) |
| N2-f | D7, N1.1/D8, D9 | MEDIUM | `D.support` (dot) vs `Function.support ⇑D` (coercion) spelling seam against M13's spelling; one spelling fixed package-wide | yes (explicit `⇑`, or dot form + one rewrite; precedent Divisor.lean:91–99) |
| **S1N1-SUM** | N1.2 (touches N1.3–N1.8) | MEDIUM | additive names `finsum_mem_eq_sum` / `finsum_mem_image` are `to_additive`-generated (Finprod.lean:499/:929), never spelled in source at the pin (grep re-verified); only `finsum_mem_congr` has usage precedent (Card/Arithmetic.lean:112) | yes (twins of :495/:481/:543; `#check` probe in the promotion PR) |
| S1N1-1a | N1.1 | MEDIUM | `toFun` vs `⇑` seam at LocallyFinsupp.lean:115, bridged by the `rfl`-simp `toFun_eq_coe` :130 (attr :128) | yes (`simp only [toFun_eq_coe]` on a `have`) |
| S1N1-5 | N1.5 | MEDIUM | `toFinset_subset_toFinset.mpr` implicit-proof-term unification against the post-`rw` goal | yes (`gcongr` — :131 and :148–149 both carry the attr, re-verified; or `toFinset_mono` :156) |
| N2-b | D1 | LOW | `f ⁻¹' {0}ᶜ` vs `(f ⁻¹' {0})ᶜ` — `Set.preimage_compl` is `rfl` | yes (state D1 in pinned orientation) |
| N2-c | D2, D3 | LOW | bare `simpa` normalization | yes (`simpa only [...]`; precedent ZetaZeros.lean:58/:61) |
| N2-c′ | D5 | LOW | `countable_of_isDiscrete` takes `IsDiscrete` directly | n/a (informational) |
| N2-e | D6 | LOW | subtype-coercion source ascription without a zero-set def | yes (`show`/`set` forms) |
| N2-h | D4, N1.1 alt route | LOW | `Set.inter_subset_right` implicit-arg form; nested-`And` membership term | yes (ζ-precedent idiom; `simp only [Set.mem_inter_iff]`) |
| N2-i | D9 | LOW | `Set.Countable.mono` argument order (subset first) | yes (explicit application primary) |
| S1N1-1b | N1.1 | LOW | root-namespace resolution of LocallyFinsupp.lean:106 (above the :119 namespace block — verified) | yes (fully-qualified) |
| S1N1-2 | N1.2 | LOW | eta between `support ⇑D` and `support (fun z => D z)` | yes (restate N1.1 with the lambda) |
| S1N1-3 | N1.3/N1.5 | LOW | pointwise nonneg extraction: M11 → `le_def` (:404) → Pi order application at `z` → `Pi.zero_apply` | yes (`have` + `simpa`) |
| S1N1-6 | N1.6–N1.8 | LOW | image-form beta-redex under `exact` (finding-A2 class; harmless as in M3, unlike M2) | yes (`simpa using …`) |
| S1N1-7a | N1.7 | LOW | `(starRingEnd ℂ) '' K` coercion insertion | yes (explicit lambda) |
| S1N1-7b | N1.7 | LOW | `Complex.conj_conj` does not exist at the pin | yes (`starRingEnd_self_apply`) |
| S1N1-8 | N1.8 | LOW | involution `simp only` chain | yes (explicit calc) |
| S1N1-9 | N1.9 | LOW | `mem_image_iff_of_inverse` orientation + beta-redex membership | yes (`show`) |

No obligation is analytic. Every analytic input — ξ's entirety, ξ's
nonvanishing at a point, finite local order, the divisor-support
identification, effectivity, the pointwise divisor symmetries — is either
already kernel-checked on `main` (`Xi.lean`, `Conj.lean`) or carried by the
accepted M-package surface. Everything this contract itself adds is point-set
topology and finite-sum bookkeeping from the pin.

## Deferred items (explicitly out of this contract)

- **N-DEFERRED-1 — generic carrier lemma**
  `Function.locallyFinsuppWithin.finite_inter_support_of_isCompact_subset
  (hK : IsCompact K) (hKU : K ⊆ U) : (K ∩ D.support).Finite`. True by finite
  subcover, natural Mathlib upstream, **not at the pin** (scan of
  LocallyFinsupp.lean confirms), and not needed here — the ξ statements are
  stronger (no `K ⊆ U`) via entirety. **Do not state the hypothesis-free
  generic form: false** (Decision 3's boundary-accumulation counterexample).
- **N-DEFERRED-2 — any ℕ-valued or named counting object** (`def zeroCount K`,
  `logCounting`-style weightings, shaped instances). Each is either a new
  `def` (death condition 4) or a route selection (death condition 2). The
  `toClosedBall`/`logCounting` machinery at the pin
  (ValueDistribution/LogCounting/Basic.lean:97) is cutoff-shaped and is cited
  only as idiom evidence.
- **N-DEFERRED-3 — strip-restricted variants** of any statement here: ξ's
  zero set already lies in the open strip (repo:`Xi.lean:192`), so they are
  one-line corollaries whose statement would begin shaping a cutoff; a route
  states them when a route is selected.
- **Divisor pullback** stays deferred exactly as M-contract DEFERRED-1; the
  image forms above need only `Set.image`, not a carrier-level comap.

## Claim boundary

This is a DRAFT statement surface: not Lean-checked, carrying no kernel
verdict, closing no barrier, selecting no route, and claiming nothing about
the truth of the Riemann Hypothesis. Specifically:

- **What is claimed.** D1–D7 and N1.9 rest on pinned Mathlib plus
  kernel-checked theorems on `main` only. N1.1/D8, D9, and N1.2–N1.8
  additionally cite M-package statements as PACKAGE PREREQUISITES of the
  surface accepted under `RH-009`, whose promotion `RH-010` is in flight, and
  are explicitly flagged as sequenced behind it (N-SEQ).
- **What is not claimed.** Closing this contract — even once kernel-checked —
  does **not** close `S1-GLOBAL-ZEROS`. Of the capability row's remaining
  exit evidence, this contract supplies only the cutoff-free "finite divisor
  sums" layer; weighted summability, star convergence of `Σ 1/ρ`,
  source-matched limits, the `|ρ| ≤ T` (Li) and `|Im ρ| < T` (Weil)
  truncations, and Weil-combination convergence are all untouched, and every
  route that would supply them stays PARKED. Nothing here states or implies a
  zero enumeration, an ordering of zeros, a counting asymptotic, a growth or
  density bound, zero simplicity, or positivity of any sum.
- **The neutrality boundary.** The compact `K` in D4/D6/N1.1–N1.5 and the
  carrier `U` in every divisor statement are universally quantified. The
  choice between `|ρ| ≤ T` and `|Im ρ| < T` style cutoffs is deliberately
  left unmade, because making it is the first act of a route, and no route is
  active. A built promotion changes the `S1-GLOBAL-ZEROS` row only by
  recording that its neutral slice (N1 + N2) is machine-checked, with the
  barrier itself still open and all routes still PARKED. Generic pinned
  machinery lowering the cost of an exit never retires a barrier row (the
  M-contract's finding-A4 discipline, applied verbatim).
- **Interface to the M-package.** Nothing here re-scopes, re-states, or
  forks any M1–M17 signature; every consumption is by exact name and exact
  hypothesis shape (re-verified against `MULTIPLICITY_CONTRACT.md` during
  consolidation). If `RH-010` alters any consumed statement, the altered
  statement re-enters here as a statement change, not silently.

## Death conditions

1. Stop if any statement would need a zero enumeration, an ordering of zeros,
   a counting function, a density/growth bound, a summability or convergence
   fact, a Hadamard product, or Li coefficients — that is route work on
   `S1-GLOBAL-ZEROS`, and all routes are PARKED by the current dated
   decision.
2. Stop if a cutoff shape (`Metric.closedBall`, `Metric.sphere`,
   `{ρ | ‖ρ‖ ≤ T}`, `{ρ | |ρ.im| < T}`, a strip, a box, an interval) appears
   in any **signature**. Proof-internal exhaustions are permitted (N2-d
   fallback); signature-level shapes are route selections.
3. Stop if a proof would need a new axiom or an unproved conjecture.
4. Stop if a new `def` is needed. The package has zero defs; the zero set
   stays the inline `riemannXi ⁻¹' {0}` (M13's spelling); the sum stays the
   `∑ᶠ` spelling.
5. Stop rather than inline-derive any M-package content (N-SEQ); a clean
   sequencing blocker is preferable to a duplicated surface.
6. Stop rather than state the hypothesis-free generic carrier finiteness
   lemma (Decision 3: it is false; a clean blocker is preferable to a false
   generality).
7. Do not declare `S1-GLOBAL-ZEROS` — or any capability-map row — closed,
   weakened, or stale on the strength of this contract. It is the barrier's
   neutral entry slice, not its exit.

---

## ANNEX N: consolidation adversarial review record (2026-08-07)

Independent re-verification run during consolidation of the two designer
sections (N2 discreteness package; N1 compact divisor sums) into this
contract. Mathlib checkout re-verified by `git rev-parse HEAD` at
`/workspace/leanprover-community/mathlib4` →
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`. Every pinned `file:line` locator
in both source sections was re-opened at that revision; every repo-side
locator was re-opened on the working branch (`Xi.lean`, `Conj.lean`,
`MULTIPLICITY_CONTRACT.md`, `MATHLIB_CAPABILITY_MAP.md`,
`tasks/RIEMANN_HYPOTHESIS.md`); both name-collision scans were re-run.

**Verdict: `SOUND_WITH_FIXES`.** Six findings (R1–R6), all resolved in place
before this contract was written. The combined surface shrank from 24 to
**23 public signatures** as a result of finding R1. This verdict accepts a
statement surface only: it is not a Lean kernel verdict, it does not promote
a module, and it does not close or advance-to-closure `S1-GLOBAL-ZEROS` or
any other barrier row.

### A. Findings resolved in place

| ID | Severity | Finding | Fix applied |
|---|---|---|---|
| **R1** | MEDIUM | **Duplicate proposition across the two halves.** N2-D8 (`IsCompact.inter_riemannXi_divisor_support_finite`) and N1.1 (`riemannXi_divisor_inter_support_finite`) state the *same* theorem — `(K ∩ Function.support (MeromorphicOn.divisor riemannXi U)).Finite` for arbitrary `U`, arbitrary compact `K` — under two names with two different proof routes (M13-rewrite vs `Set.univ`-comparison via M10). Two names for one proposition is exactly the naming-seam class this package's own zero-defs rule exists to prevent | Unified as **N1.1 = N2-D8** (§1 Decision 2): stated once, name `riemannXi_divisor_inter_support_finite` retained (N1.2's statement embeds its proof term), both routes recorded, the M10-comparison route primary (keeps the finiteness layer independent of M13's statement shape), superseded name recorded and collision-scanned. Signature count 24 → 23 |
| **R2** | MEDIUM | **Phantom provenance file.** Both designer sections cite `domains/riemann-hypothesis/GLOBAL_ZEROS_RECON.md` as on-disk ground truth ("identified exactly one genuinely route-neutral slice"). No such file exists in the working tree, in `notes/`, or anywhere in git history (checked `git log --all --diff-filter=A`). It was workflow-internal context never committed | Provenance section rewritten: the recon is named as workflow-internal and non-citable; the slice is re-anchored to the two on-disk authorities that carry the same content — `MULTIPLICITY_CONTRACT.md:1714–1723` (DEFERRED-2 names N2's four predicates verbatim) and `MATHLIB_CAPABILITY_MAP.md:387` ("finite divisor sums" = N1). No statement, obligation, or death condition depended on the phantom file |
| R3 | LOW | N2 cited DEFERRED-2 at `MULTIPLICITY_CONTRACT.md:1712–1720`; the block actually spans **:1714–1723** | Locator corrected throughout |
| R4 | LOW | N1 cited `Function.Involutive.leftInverse` at Logic/Function/Basic.lean:1021 and `.rightInverse` at :1027; the declarations are at **:1022** and **:1028** (`.injective` :1030 was correct) | Locators corrected (N1.9 dependencies) |
| R5 | LOW | N1.5's verdict sentence was garbled ("unconditionally meaningful even when `K₁` has infinite support-intersection is impossible here") and, read literally, gestured at a junk-value caveat that does not arise | Rewritten: `K₁ ⊆ K₂` forces `K₁ ∩ support ⊆ K₂ ∩ support`, so both sums are honest finite sums and no junk-value caveat exists for N1.5 |
| R6 | LOW | S1N1-3's recorded seam was incomplete: `le_def` (:404) yields the **Pi-order** fact `(0 : ℂ → ℤ) ≤ ⇑D`, so the pointwise extraction crosses the Pi `≤` application at `z` (definitional, `Pi.le_def` if not) *in addition to* `Pi.zero_apply` | Obligation restated with the extra link; fallback unchanged |

### B. Citations re-verified as CORRECT (no change)

Pinned Mathlib — `Analysis/Analytic/Order.lean` :682 (signature and
`f ⁻¹' {0}ᶜ` conclusion orientation verbatim; `[ConnectedSpace 𝕜]` confirmed;
namespace `AnalyticOnNhd` :575–:700), :664.
`Topology/DiscreteSubset.lean` :148, :170, :188, :333, :343 (all
root-namespace — the file has only section blocks; the ζ file's unqualified
use at :58 is consistent). `Topology/Constructions.lean` :262, :614.
`Topology/Compactness/Compact.lean` :86, :1046 (consumes `IsDiscrete`, not
`DiscreteTopology`). `Topology/Compactness/Lindelof.lean` :655–:656, :723,
:738 (priority 100). Instance chain:
`LinearAlgebra/Complex/FiniteDimensional.lean:27`,
`Analysis/Normed/Module/FiniteDimension.lean:532` (priority 900),
`Topology/MetricSpace/ProperSpace.lean:64` (priority 100),
`Analysis/Normed/Module/Convex.lean:168` (priority 100),
`Topology/Connected/PathConnected.lean:607` (priority 100).
`NumberTheory/LSeries/ZetaZeros.lean` :33, :39 (**private** confirmed), :46
(**private** confirmed), :57–:58, :60–:61, :64–:67 (proof idiom verbatim,
including the bare `Set.inter_subset_right`), :70.
`Topology/LocallyFinsupp.lean` :48, :52, :54 (local finiteness only at points
of `U` — Decision 3's premise), :61 (reducible abbrev), :91, :106 (root
level, **above** the namespace block at :119 — S1N1-1b's premise confirmed),
:115 (concludes at `f.toFun` — S1N1-1a's premise confirmed), :125, :128–:130
(`@[simp]`, `rfl`), :140, :218, :237, :254 (domain-compact hypothesis shape
confirmed — the near-miss), :368, :376 (the only sum-adjacent lemmas in the
file; sum-API audit conclusion re-confirmed), :401, :404.
`Analysis/Meromorphic/Divisor.lean` :39 (total, junk 0), :71, :83
(`_root_.divisor_sphere_support_finite`, shaped), :91–:99 (support-comparison
proof pattern — N1.1's precedent), :104 (shaped).
`Algebra/BigOperators/Finprod.lean` :481, :495, :499–:501, :543, :565–:566,
:929–:936 (`@[to_additive]` present at each; `finprod_mem_image` and
`finprod_mem_congr` hypothesis-free on finiteness — Block D's
unconditionality premise); generated-name absence re-confirmed (zero source
hits for `finsum_mem_eq_sum` / `finsum_mem_image`; `finsum_mem_congr` usage
at `Data/Set/Card/Arithmetic.lean:112`).
`Algebra/Order/BigOperators/Group/Finset.lean` :32, :119–:120, :131–:132
(additive name explicit in attribute; hypothesis shape verbatim; `gcongr`
confirmed). `Data/Set/Finite/Basic.lean` :54, :101, :148–:149 (**`@[gcongr,
mono]` on `toFinset_subset_toFinset` confirmed** — the attribute at :148
belongs to :149, not to the ssubset variant at :152–:153), :156, :497.
`Data/Set/Basic.lean` :268, :772 (implicit-argument form confirmed), :814.
`Data/Set/Countable.lean` :40, :115 (argument order confirmed), :214, :256.
`Data/Set/Image.lean` :83 (`rfl`), :351 (`_root_.` confirmed), :355 (inside
`namespace Set` :45–:1076). `Data/Set/Function.lean` :33, :295.
`Logic/Function/Basic.lean` :1030. `Algebra/Star/Basic.lean` :348 (and
`Complex.conj_conj` absence re-confirmed). `Algebra/Group/Basic.lean`
:932–:933. `Algebra/Group/Hom/Defs.lean` :234, :460–:461.
`Algebra/Ring/Hom/Defs.lean` :500. `Algebra/Notation/Pi/Defs.lean` :49.
`Analysis/Complex/CauchyIntegral.lean` :678 (namespace `Complex` :173).
`NumberTheory/Pell.lean` :472. Idiom evidence:
`Analysis/Complex/JensenFormula.lean` :235, :315;
`Analysis/Complex/ValueDistribution/LogCounting/Basic.lean` :97, :109, :166;
`Analysis/SpecialFunctions/Integrability/LogMeromorphic.lean` :48 (all
shaped, none arbitrary-compact — the gap claim confirmed).

Repo — `Xi.lean` :41, :46, :61, :72, :78, :157, :192, :248 (all verbatim).
`Conj.lean` :163, :292, :357, :440, :452 (all verbatim).
`MULTIPLICITY_CONTRACT.md` :851 (M9), :882 (M10), :910 (M11), :933 (M12,
S1M-FIN), :1056 (M13, equation shape `= U ∩ riemannXi ⁻¹' {0}` and universal
`U` confirmed), :1091 (M14, `hU` hypothesis shape confirmed), :1160 (M15,
`hU₁`/`hU₂` shapes and order confirmed). `tasks/RIEMANN_HYPOTHESIS.md` :616
(`RH-010` ACTIVE 2026-08-07). `MATHLIB_CAPABILITY_MAP.md` :387.

Name-collision scan re-run at the pin and over the repo: all 23 proposed
names plus the superseded `IsCompact.inter_riemannXi_divisor_support_finite`
— **0 hits each**; `riemannXi` — 0 hits in pinned `Mathlib/`.

### C. Soundness checks passed (attack fronts)

- **Front 1 (hallucinated citations).** No hallucinated lemma in either
  section. Two off-by-one locators (R4) and one range slip (R3); every cited
  declaration exists at the pin with the claimed signature, namespace, and
  hypothesis shape.
- **Front 2 (exceptional points).** ξ is entire with no excluded point, so
  the D1 engine has no pole to patch (unlike ζ at 1); witness point `0` has
  `riemannXi 0 = 1/2 ≠ 0` (kernel-checked). `0` and `1` are not zeros
  (`riemannXi_zero`/`riemannXi_one` = 1/2), so no boundary case of the three
  involutions touches the zero set's edge cases. The divisor is total with
  junk value 0 (Divisor.lean:39), so D7 holds for arbitrary `U` with no
  hidden meromorphy hypothesis; the one genuine exceptional-point hazard —
  support accumulation at `∂U` for a general carrier — is confronted
  head-on: it is Decision 3's counterexample, it is why N1.1 is a ξ theorem,
  and death condition 6 forbids the false generic form. Block D's image
  forms were checked at non-compact and infinite-support `K`: both
  combinators are finiteness-hypothesis-free at the pin, and on
  infinite-support windows both sides of each equation take the same junk
  value, so no statement narrows its quantifiers to dodge an exceptional
  case.
- **Front 3 (hidden cutoff shapes).** Every one of the 23 signatures was
  scanned for `closedBall`, `sphere`, `ball`, `‖·‖`, `.im`, `.re`, strip
  literals, boxes, and intervals: **none appears in any signature.** Shapes
  occur in exactly three places, all legitimate: (i) the pinned shaped
  lemmas quoted as what this package deliberately does *not* mirror; (ii)
  N2-d's proof-internal closed-ball exhaustion fallback, licensed by the
  neutrality rule's proof-internals clause and invisible at the statement
  surface; (iii) N-DEFERRED-3's refusal to state strip variants. The
  `IsCompact K` hypothesis itself is shape-free; D6's filter form was
  checked against DiscreteSubset.lean:148 — its compact remains universally
  quantified.
- **Front 4 (scope creep into counting/growth).** No signature produces an
  enumeration, an ordering, a count, a density, a growth bound, or a
  convergence fact. D5/D9 (`Set.Countable`) yield existence of an injection,
  not a listing. N1.4 is a `toNat`-cast identity, not a counting function —
  no ℕ-valued object is named (N-DEFERRED-2). N1.5 is finite-sum
  monotonicity, not a growth statement. The "number of zeros with
  multiplicity" reading lives in prose via M12/M13 and is flagged as
  interpretive. The capability row's remaining shaped/analytic items are
  enumerated in the claim boundary as untouched.
- **Front 5 (prerequisite laundering).** Checked that no M-package statement
  is cited as pinned Mathlib or as kernel-checked: all seven consumed
  M-signatures are tabled as PACKAGE PREREQUISITES tied to `RH-010`
  (ACTIVE, in flight — queue state re-verified at
  `tasks/RIEMANN_HYPOTHESIS.md:616`), and N-SEQ (HIGH) is the register's
  head entry. D1–D7/N1.9 were re-checked to consume no M-signature —
  confirmed (D7 needs only the divisor def; D1–D6 need only `Xi.lean` +
  pin; N1.9 needs only the pin).
- **Front 6 (barrier/row integrity).** The contract nowhere claims a row
  closed, weakened, or stale; the finding-A4 discipline is restated in the
  claim boundary; death condition 7 forbids the re-scoping class. No queue
  slot is claimed; the document self-identifies as an offered artifact.

### D. Open items

- **N-SEQ** remains the package's HIGH obligation until the `RH-010`
  promotion merges; it is ordering-only, with no analytic content.
- **S1N1-SUM** (generated additive names) is the most likely single CI
  bounce; probe with `#check` in the promotion PR before building.
- The N2-f spelling decision (dot vs coercion support spelling) must be made
  and recorded at build time, package-wide, in the promotion PR description.
