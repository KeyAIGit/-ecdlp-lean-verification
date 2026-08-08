/-
Built zero-set slice package (RH-012): promotion of the independently accepted
23-signature statement surface of
`domains/riemann-hypothesis/ZERO_SET_SLICE_CONTRACT.md` (acceptance record:
`notes/reviews/RH011_ZERO_SLICE_ACCEPTANCE_2026_08_07.md`; promotion record:
`notes/reviews/RH_SLICE_PROMOTION_2026_08_08.md`).

Twenty-three declarations in three blocks. Block D (D1-D9) is the topology of
the ξ zero set: its complement is codiscrete, the set is closed and discrete,
it meets every compact in a finite set, it is countable, and its points escape
every compact in the filter sense; then the same discreteness, closedness,
compact-finiteness and countability for the SUPPORT of the ξ divisor on an
arbitrary region `U`. Block N (N1.2-N1.8) is the divisor sum over a compact:
that the `finsum` is an honest finite sum, that it is nonnegative and reads as
a natural number, that it is monotone in the compact, and that it is invariant
under the three symmetries `s ↦ 1 - s`, `s ↦ conj s` and `s ↦ 1 - conj s`,
each in a substitution form and an image form. Block E (N1.9) is three generic
set identities saying a window symmetric under one of those maps is its own
image.

WHAT THIS DOES NOT DO, stated before anything else, because this is the RH-lane
package where a reader is most likely to over-read. No zero is located. No zero
is counted: there is no counting function, no `N(T)`, no zero-density estimate,
and no statement that the zero set is infinite or even nonempty — every
statement here is compatible with ξ having no zeros at all, and none of them
rules that out. No zero-free region is established, and nothing is said about
the critical line. The divisor sums are over an ARBITRARY compact `K` and an
ARBITRARY region `U`; no cutoff shape, contour, or window family is chosen, so
no proof route is selected or nudged toward. The three symmetry statements
transport a sum that has already been assumed to be over a symmetric window;
they do not establish any symmetry of the zeros themselves beyond what the
merged multiplicity and conjugation packages already proved.

Barrier effect: on a green merge this ADVANCES the `S1-GLOBAL-ZEROS`
bookkeeping and does NOT close it, exactly as `RH-012`'s exit criteria state.
Global zero counting is what that barrier asks for, and a compact-by-compact
finiteness statement is not global counting. The capability map is not edited
by this promotion change; any dated addendum recording the advance is a
separate change with its own review.

Prerequisites, all kernel-checked on `main`: the target bridge (PR #299), the
xi package (PR #304), the conjugation package (PR #307), and the
multiplicity/divisor package (PR #313), whose M9-M15 statements Block N
consumes directly. This module imports the xi and multiplicity modules.

Kernel verdict: delivered by CI on this promotion change, never by this header.
`lake build` compiles the module, the no-incomplete-proof gate scans it, the
regenerated `ResearchOS/LedgerAxiomAudit.lean` + `check_axioms.py` enforce the
per-row `standard` axiom base, and `gen_researchos_registry.py --check`
enforces inverse coverage. If any gate is red, no row is counted, and `RH-012`
is not complete — its exit criteria require the full battery to pass on the
exact merged head.

All twenty-three public declarations are ledgered as `RH-SLICE-*` rows in
`VERIFIED_RESEARCHOS.md` and audited through the generated
`ResearchOS/LedgerAxiomAudit.lean` with axiom base `standard`.

Pinned Mathlib: fabf563a7c95a166b8d7b6efca11c8b4dc9d911f (v4.31.0).
-/
import ResearchOS.AnalyticNumberTheory.RiemannHypothesis.Xi    -- riemannXi, differentiable_riemannXi, riemannXi_zero
import ResearchOS.AnalyticNumberTheory.RiemannHypothesis.Mult  -- M9–M15 (PACKAGE PREREQUISITE; kernel-checked on main, merged PR #313)
import Mathlib.Analysis.Analytic.Order               -- AnalyticOnNhd.preimage_zero_mem_codiscrete
import Mathlib.Analysis.Complex.CauchyIntegral       -- Complex.analyticOnNhd_univ_iff_differentiable
import Mathlib.Analysis.Meromorphic.Divisor          -- MeromorphicOn.divisor
import Mathlib.Topology.DiscreteSubset               -- codiscrete, mem_codiscrete'
import Mathlib.Topology.Compactness.Lindelof         -- HereditarilyLindelofSpace.isLindelof
import Mathlib.Algebra.BigOperators.Finprod          -- finsum_mem_* (also transitive via LocallyFinsupp)
import Mathlib.Algebra.Order.BigOperators.Group.Finset -- sum_nonneg, sum_le_sum_of_subset_of_nonneg

-- Import list is the contract's proposed preamble verbatim (flagged there as
-- "name-resolution review only"; to be minimized by `shake` at stage two).
-- `Mathlib.Topology.Compactness.Compact` (IsCompact.inter_right :86,
-- IsCompact.finite :1046) and `Mathlib.Topology.Constructions` (IsDiscrete
-- :262, IsDiscrete.mono :614) arrive through the `public import` closure of
-- `Mathlib.Topology.Compactness.Lindelof` (:10 imports
-- Compactness.SigmaCompact) and `Mathlib.Topology.DiscreteSubset` (:9 imports
-- Constructions directly). `Mathlib.Topology.LocallyFinsupp`
-- (LocallyFiniteSupport :91/:106, locallyFiniteSupport :115, toFun_eq_coe
-- :130, supportWithinDomain :140, discreteSupport :218, closedSupport :237,
-- le_def :404) and `Mathlib.Data.Set.Finite.Basic` / `.Countable` /
-- `.Image` / `.Function` glue arrive through `Mathlib.Analysis.Meromorphic.
-- Divisor` (:11 is a `public import` of LocallyFinsupp) and the closure.
-- Because the pin uses the Lean module system (`module` / `public import`),
-- visibility is a closure property, not an import-line property; none is
-- re-listed.

open Complex Filter Function
open scoped Topology ComplexConjugate
-- `open Complex Filter` is the house convention of the built siblings
-- (Xi.lean, Conj.lean, Mult.lean). Primary spellings below are nevertheless
-- fully qualified wherever a namespace trap was recorded, so a lost `open`
-- degrades to a fallback, not a break.

/-! ### Block A — topology of the ξ zero set (N2-D1 … N2-D6)

The ξ zero set is spelled inline as `riemannXi ⁻¹' {0}` at every use site —
M13's spelling; no `riemannXiZeros` def is introduced (contract §1
Decision 1, death condition 4). -/

/-! ## N2-D1. The complement of the ξ zero set is codiscrete `[PIN]` — the engine

Strictly simpler than the ζ precedent (ZetaZeros.lean:39–55), which needs the
`codiscreteWithin {1}ᶜ` detour and a pole patch at 1: ξ is entire with no
excluded point, so the `[ConnectedSpace 𝕜]` global lemma Order.lean:682
applies in one stroke. Nonvanishing witness: `x := 0` via `riemannXi_zero`
(repo:`Xi.lean:72`). -/

theorem compl_riemannXi_zeroSet_mem_codiscrete :
    (riemannXi ⁻¹' {0})ᶜ ∈ Filter.codiscrete ℂ := by
  have hA : AnalyticOnNhd ℂ riemannXi Set.univ :=
    Complex.analyticOnNhd_univ_iff_differentiable.mpr differentiable_riemannXi
  have h0 : riemannXi 0 ≠ 0 := by rw [riemannXi_zero]; norm_num
  simpa only [Set.preimage_compl] using hA.preimage_zero_mem_codiscrete h0
  -- OBLIG N2-a (MEDIUM): `ConnectedSpace ℂ` instance resolution for
  -- Order.lean:682 — `NormedSpace.instPathConnectedSpace`
  -- (Analysis/Normed/Module/Convex.lean:168, priority 100) →
  -- `PathConnectedSpace.connectedSpace`
  -- (Topology/Connected/PathConnected.lean:607, priority 100); same class as
  -- the M-package's S1M-12a. Fallback: `haveI : ConnectedSpace ℂ :=
  -- inferInstance` probe line before the `simpa`.
  -- OBLIG N2-b (LOW): the pinned conclusion is `riemannXi ⁻¹' {0}ᶜ` (postfix
  -- `ᶜ` binds tighter); `Set.preimage_compl` (Data/Set/Image.lean:83) is
  -- `rfl` and `@[simp]`, so
  --   exact hA.preimage_zero_mem_codiscrete h0
  -- may already close the goal; if the `simpa only` instead reports "no
  -- progress", REPLACE it with that `exact`. Fallback of last resort (a
  -- STATEMENT change, returns to contract review — do not apply as a CI
  -- repair): state D1 in the pinned orientation and let D2/D3 do the flip.
  -- Alternate nonvanishing witness (fallback for `h0`):
  --   have h0 : riemannXi 2 ≠ 0 := riemannXi_ne_zero_of_one_le_re (by norm_num)
  -- mirroring the ζ file's witness choice (repo:`Xi.lean:157`).

/-! ## N2-D2 / N2-D3. The ξ zero set is closed and is discrete `[PIN]`

Verbatim the ζ idiom (ZetaZeros.lean:57–61) with the ξ engine substituted;
`mem_codiscrete'` is root-namespace (DiscreteSubset.lean:343 — the ζ file
uses it unqualified at :58). -/

theorem isClosed_riemannXi_zeroSet : IsClosed (riemannXi ⁻¹' {0}) := by
  simpa using (mem_codiscrete'.mp compl_riemannXi_zeroSet_mem_codiscrete).1
  -- OBLIG N2-c (LOW): the bare `simpa` must normalize
  -- `IsOpen (riemannXi ⁻¹' {0})ᶜ` to the goal via `isOpen_compl_iff`;
  -- precedent: the identical bare `simpa` compiles at the pin at
  -- ZetaZeros.lean:58. Fallback:
  --   simpa only [isOpen_compl_iff] using
  --     (mem_codiscrete'.mp compl_riemannXi_zeroSet_mem_codiscrete).1

theorem isDiscrete_riemannXi_zeroSet : IsDiscrete (riemannXi ⁻¹' {0}) := by
  simpa using (mem_codiscrete'.mp compl_riemannXi_zeroSet_mem_codiscrete).2
  -- OBLIG N2-c (LOW), same class: here the normalization is `compl_compl`
  -- on `IsDiscrete ((riemannXi ⁻¹' {0})ᶜ)ᶜ`; precedent ZetaZeros.lean:61.
  -- Fallback:
  --   simpa only [compl_compl] using
  --     (mem_codiscrete'.mp compl_riemannXi_zeroSet_mem_codiscrete).2

/-! ## N2-D4. Finite intersection with an ARBITRARY compact set `[PIN]` — the neutrality carrier

`K` is an arbitrary compact set — the exact quantifier shape of the pinned ζ
precedent (ZetaZeros.lean:64). No instantiation at `Metric.closedBall`, no
`{ρ | ‖ρ‖ ≤ T}`, no `{ρ | |ρ.im| < T}` appears in this package (neutrality
rule; death condition 2). Proof shape verbatim ZetaZeros.lean:65–67. -/

theorem IsCompact.inter_riemannXi_zeroSet_finite {K : Set ℂ} (hK : IsCompact K) :
    (K ∩ riemannXi ⁻¹' {0}).Finite := by
  apply (hK.inter_right isClosed_riemannXi_zeroSet).finite
  exact isDiscrete_riemannXi_zeroSet.mono Set.inter_subset_right
  -- OBLIG N2-h(i) (LOW): `Set.inter_subset_right` is the implicit-argument
  -- form `{s t}` at this pin (Data/Set/Basic.lean:772); the ζ precedent
  -- passes it bare in exactly this position (ZetaZeros.lean:67) — a mirrored
  -- idiom, not a guess. Fallback: `Set.inter_subset_right (s := K)
  -- (t := riemannXi ⁻¹' {0})`.

/-! ## N2-D5. The ξ zero set is countable `[PIN]` — beyond the ζ precedent

`Set.Countable` produces the *existence* of an injection into ℕ, never a
chosen listing: no enumeration and no ordering of zeros is introduced
(death condition 1). -/

theorem countable_riemannXi_zeroSet : (riemannXi ⁻¹' {0}).Countable :=
  (HereditarilyLindelofSpace.isLindelof (riemannXi ⁻¹' {0})).countable_of_isDiscrete
    isDiscrete_riemannXi_zeroSet
  -- OBLIG N2-d (MEDIUM): four-link instance chain to
  -- `HereditarilyLindelofSpace ℂ` — `FiniteDimensional ℝ ℂ`
  -- (LinearAlgebra/Complex/FiniteDimensional.lean:27) →
  -- `FiniteDimensional.proper_real`
  -- (Analysis/Normed/Module/FiniteDimension.lean:532, priority 900) →
  -- `secondCountable_of_proper` (Topology/MetricSpace/ProperSpace.lean:64,
  -- priority 100) → `SecondCountableTopology.toHereditarilyLindelof`
  -- (Lindelof.lean:738, priority 100). The longest inference chain in the
  -- package; every link is a priority-tagged instance at the pin.
  -- Fallback (statement unchanged, proof-internal exhaustion — permitted by
  -- the neutrality rule; the closed balls are proof scaffolding, not a
  -- signature-level cutoff):
  --   have hcover : riemannXi ⁻¹' {0}
  --       = ⋃ n : ℕ, (Metric.closedBall 0 n ∩ riemannXi ⁻¹' {0}) := by
  --     ext z
  --     simp only [Set.mem_iUnion, Set.mem_inter_iff, Metric.mem_closedBall,
  --       dist_zero_right]
  --     exact ⟨fun hz => (exists_nat_ge ‖z‖).imp fun n hn => ⟨hn, hz⟩,
  --       fun ⟨n, _, hz⟩ => hz⟩
  --   hcover ▸ Set.countable_iUnion fun n =>
  --     ((isCompact_closedBall 0 n).inter_riemannXi_zeroSet_finite).countable
  --   (Set.countable_iUnion — Data/Set/Countable.lean:214;
  --    Set.Finite.countable — Countable.lean:256.)
  -- OBLIG N2-c′ (LOW, informational): `countable_of_isDiscrete`
  -- (Lindelof.lean:655–656) consumes `IsDiscrete` directly (`.to_subtype`
  -- applied internally at :656); no manual coercion is inserted here.

/-! ## N2-D6. Zeros escape every compact (filter form) `[PIN]` — optional

By `tendsto_cofinite_cocompact_iff` (DiscreteSubset.lean:148) this is
literally "the preimage of every compact is finite", compact still
universally quantified — still neutral. Included because the ζ precedent
ships it (ZetaZeros.lean:70); droppable without weakening the package. -/

theorem tendsto_riemannXi_zeroSet_cofinite_cocompact :
    Filter.Tendsto ((↑) : (riemannXi ⁻¹' {0} : Set ℂ) → ℂ)
      Filter.cofinite (Filter.cocompact ℂ) :=
  isClosed_riemannXi_zeroSet.tendsto_coe_cofinite_of_isDiscrete
    isDiscrete_riemannXi_zeroSet
  -- (DiscreteSubset.lean:170: `(hs : IsClosed s) (hs' : IsDiscrete s)`, in
  -- that order — re-read at the pin.)
  -- OBLIG N2-e (LOW): the subtype-coercion source ascription
  -- `(riemannXi ⁻¹' {0} : Set ℂ)` without a zero-set def. Fallback if the
  -- ascription trips elaboration:
  --   by exact isClosed_riemannXi_zeroSet.tendsto_coe_cofinite_of_isDiscrete
  --        isDiscrete_riemannXi_zeroSet
  -- or a `show Filter.Tendsto _ Filter.cofinite (Filter.cocompact ℂ) from …`.

/-! ### Block B — topology of the ξ divisor support (N2-D7, N1.1 = N2-D8, N2-D9)

Support spelling package-wide: `Function.support (MeromorphicOn.divisor
riemannXi U)` — M13's left-hand-side spelling (N2-f decision, header). -/

/-! ## N2-D7. The ξ divisor has discrete support (any `U`) and closed support (closed `U`) `[PIN]` — carrier level

Carrier facts: `locallyFinsuppWithin` support is discrete by construction
(LocallyFinsupp.lean:218) for the divisor of *any* function (Divisor.lean:39
is total, junk value 0 where meromorphy fails). They acquire multiplicity
content only through M13/M10. `U` is arbitrary (D7a) or arbitrary-closed
(D7b) — no shape. -/

theorem isDiscrete_riemannXi_divisor_support (U : Set ℂ) :
    IsDiscrete (Function.support (MeromorphicOn.divisor riemannXi U)) :=
  (MeromorphicOn.divisor riemannXi U).discreteSupport
  -- OBLIG N2-f (MEDIUM): `D.support` (the carrier lemmas' spelling,
  -- LocallyFinsupp.lean:218/:237) vs `Function.support ⇑D` (this statement's
  -- spelling, per the package-wide N2-f decision): at the pin `D.support`
  -- is the reducible `abbrev Function.locallyFinsuppWithin.support`
  -- (:138) := `Function.support D`, so both elaborate to the same term and
  -- the term-mode `exact` works up to defeq. Precedent that the mixed
  -- spelling round-trips: Divisor.lean:91–99. Fallback:
  --   show IsDiscrete (MeromorphicOn.divisor riemannXi U).support from
  --     (MeromorphicOn.divisor riemannXi U).discreteSupport

theorem isClosed_riemannXi_divisor_support {U : Set ℂ} (hU : IsClosed U) :
    IsClosed (Function.support (MeromorphicOn.divisor riemannXi U)) :=
  (MeromorphicOn.divisor riemannXi U).closedSupport hU
  -- OBLIG N2-f (MEDIUM): same seam and same fallback as D7a, with
  -- `closedSupport` (LocallyFinsupp.lean:237, `[T1Space ℂ]` from the metric
  -- instance).

/-! ## N1.1 = N2-D8. Divisor support meets every compact in a finite set (arbitrary `U`, arbitrary `K`) `[MULT: M9, M10]` — the multiplicity-aware statement

Stated ONCE (contract §1 Decision 2, finding R1); the superseded draft name
`IsCompact.inter_riemannXi_divisor_support_finite` is NOT stated. Why the pin
alone does not suffice: the pinned carrier route (`finiteSupport`
LocallyFinsupp.lean:254; Divisor.lean:91) requires the DOMAIN compact or
compactly contained — the wrong quantifier shape for neutrality. Entirety of
ξ (through M9/M10) removes that: the `Set.univ` divisor dominates (contract
§1 Decision 3 — and the hypothesis-free GENERIC carrier form is FALSE, death
condition 6; do not generalize this lemma away from ξ).

Primary route below: the `Set.univ`-comparison (M9+M10 only — the same
support-comparison pattern Mathlib itself uses at Divisor.lean:94–98);
keeps the finiteness layer independent of M13's statement shape. -/

theorem riemannXi_divisor_inter_support_finite (U : Set ℂ) {K : Set ℂ} (hK : IsCompact K) :
    (K ∩ Function.support (MeromorphicOn.divisor riemannXi U)).Finite := by
  have hfin := (Function.locallyFinsupp.locallyFiniteSupport
      (MeromorphicOn.divisor riemannXi Set.univ)).finite_inter_support_of_isCompact hK
  simp only [Function.locallyFinsuppWithin.toFun_eq_coe] at hfin
  -- OBLIG S1N1-1a, discharged in concrete form. `locallyFiniteSupport`
  -- concludes `LocallyFiniteSupport f.toFun` (LocallyFinsupp.lean:115-117), the
  -- RAW FIELD spelling, so without this normalization every goal below is
  -- headed by `Function.locallyFinsuppWithin.toFun` while M10's pattern is
  -- headed by `DFunLike.coe`. `rw` matches through `kabstract`, which compares
  -- head indices and skips `isDefEq` on a head mismatch, so `toFun_eq_coe := rfl`
  -- would NOT save it: the M10 rewrite below would simply find nothing.
  apply Set.Finite.subset hfin
  apply Set.inter_subset_inter Set.Subset.rfl
  intro z hz
  have hzU : z ∈ U := (MeromorphicOn.divisor riemannXi U).supportWithinDomain hz
  rw [Function.mem_support] at hz ⊢
  rw [riemannXi_divisor_apply (Set.mem_univ z)]      -- M10 at Set.univ
  rwa [riemannXi_divisor_apply hzU] at hz            -- M10 at U
  -- Both M10 instances rewrite to the same RHS
  -- `((analyticOrderAt riemannXi z).map (↑)).untop₀` (re-verified verbatim in
  -- the built Mult.lean:388), so the `≠ 0` fact transports.
  -- OBLIG N-SEQ (DISCHARGED 2026-08-07): M9/M10 are consumed by IMPORT of
  -- the built Mult module (merged PR #313, `2a20629`); nothing here inline
  -- re-derives them (death condition 5).
  -- OBLIG S1N1-1a (MEDIUM): the finiteness term from LocallyFinsupp.lean
  -- :115/:106 is stated at `(divisor … Set.univ).toFun.support`, the goal at
  -- coercion-form support; defeq via the `rfl`-simp `toFun_eq_coe` (:130,
  -- attr :128), and `apply Set.Finite.subset` must see through it. Fallback:
  --   have hfin := (Function.locallyFinsupp.locallyFiniteSupport
  --       (MeromorphicOn.divisor riemannXi Set.univ)
  --     ).finite_inter_support_of_isCompact (W := K) hK
  --   simp only [Function.locallyFinsuppWithin.toFun_eq_coe] at hfin
  --   exact hfin.subset (Set.inter_subset_inter Set.Subset.rfl …)
  -- OBLIG S1N1-1b (LOW): `LocallyFiniteSupport.finite_inter_support_of_isCompact`
  -- is ROOT-level (:106 sits above the namespace block opening at :119 —
  -- verified), so dot notation on the `LocallyFiniteSupport` term resolves;
  -- fallback: the fully-qualified spelling
  -- `_root_.LocallyFiniteSupport.finite_inter_support_of_isCompact`.
  -- OBLIG N2-f applies (support spelling seam — see header decision).
  -- CORRECTED 2026-08-08: an earlier version of this note said to prepend the
  -- `toFun_eq_coe` normalization "if `rw [Function.mem_support]` balks". That
  -- aimed the mitigation at the wrong line. `Function.mem_support`'s pattern is
  -- `?x ∈ Function.support ?f` and matches EITHER spelling, so it does not
  -- balk; the M10 rewrite one line later is what fails. The normalization is
  -- now unconditional and sits on the witness itself, above.
  --
  -- ALTERNATIVE ROUTE (contract-recorded, via M13 + N2-D4; same PR #313
  -- prerequisites — swap the whole tactic block for):
  --   refine Set.Finite.subset hK.inter_riemannXi_zeroSet_finite ?_  -- N2-D4
  --   rw [riemannXi_divisor_support U]                 -- M13 (PACKAGE PREREQUISITE)
  --   exact fun x hx => ⟨hx.1, hx.2.2⟩                 -- K ∩ (U ∩ Z) ⊆ K ∩ Z
  -- OBLIG N2-h(ii) (LOW, alternative route only): the nested-`And`
  -- membership term `⟨hx.1, hx.2.2⟩`; fallback via
  -- `simp only [Set.mem_inter_iff]` before the `exact`. M13's equation is
  -- oriented support-to-zero-set, so the `rw` is forward, no `.symm`.

/-! ## N2-D9. Divisor support is countable (arbitrary `U`) `[MULT: M13]`

The one statement genuinely pinned to the M13 seam: no M13-free replacement
exists that does not re-derive its content (death condition 5). -/

theorem countable_riemannXi_divisor_support (U : Set ℂ) :
    (Function.support (MeromorphicOn.divisor riemannXi U)).Countable := by
  rw [riemannXi_divisor_support U]                                  -- M13 (PACKAGE PREREQUISITE)
  exact Set.Countable.mono Set.inter_subset_right countable_riemannXi_zeroSet  -- N2-D5
  -- OBLIG N-SEQ (DISCHARGED 2026-08-07, shared — see N1.1): M13 is the built
  -- Mult.lean:538, imported, forward-oriented
  -- `Function.support (MeromorphicOn.divisor riemannXi U) = U ∩ riemannXi ⁻¹' {0}`.
  -- OBLIG N2-i (LOW): `Set.Countable.mono` takes the subset argument FIRST
  -- (Data/Set/Countable.lean:115, re-verified) — the explicit application
  -- above is argument-order-safe. Fallback (dot form, also elaborates at
  -- this pin):
  --   exact countable_riemannXi_zeroSet.mono Set.inter_subset_right

/-! ### Block C — the sum over an arbitrary compact is a well-defined finite (natural) number (N1.2 – N1.5)

The compact sum is the SPELLING `∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z`
(the pinned idiom of JensenFormula.lean:235/:315 etc., there hard-wired to
shapes — the arbitrary-compact layer is exactly the gap this block fills),
not a definition. No ℕ-valued or named counting object is introduced
(N-DEFERRED-2). -/

/-! ## N1.2. The finsum over `K` is the honest finite sum `[MULT via N1.1]` — well-definedness bridge -/

theorem riemannXi_divisor_finsum_mem_eq_sum (U : Set ℂ) {K : Set ℂ} (hK : IsCompact K) :
    ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z
      = ∑ z ∈ (riemannXi_divisor_inter_support_finite U hK).toFinset,
          MeromorphicOn.divisor riemannXi U z :=
  finsum_mem_eq_sum _ (riemannXi_divisor_inter_support_finite U hK)
  -- (`Set.Finite.toFinset` is proof-irrelevant in its `Set.Finite` argument,
  -- so naming the N1.1 term in the statement is stable.)
  -- OBLIG S1N1-SUM (MEDIUM — the block's naming obligation): the additive
  -- name `finsum_mem_eq_sum` is COMPILER-GENERATED by `@[to_additive]`
  -- (Finprod.lean:499, attribute re-verified at the pin) and appears nowhere
  -- in source at the pin. Cost if the generated name differs: one CI cycle;
  -- probe with `#check @finsum_mem_eq_sum` in the promotion PR before
  -- building. Fallbacks: the additive twins of `finprod_mem_eq_prod_of_subset`
  -- (Finprod.lean:495), `finprod_mem_eq_prod_of_inter_mulSupport_eq` (:481),
  -- `finprod_mem_inter_mulSupport` (:543).
  -- OBLIG S1N1-2 (LOW): the hypothesis of Finprod.lean:499 is stated at
  -- `(s ∩ Function.support fun z => …).Finite` — eta between `support ⇑D`
  -- and `support (fun z => D z)` is definitional in Lean 4. Fallback:
  --   finsum_mem_eq_sum _ ((riemannXi_divisor_inter_support_finite U hK).subset
  --     (by intro x hx; exact hx))
  -- or restate the `have`-bound finiteness term with the lambda spelling.

/-! ## N1.3. Nonnegativity `[MULT: M11]` -/

theorem riemannXi_divisor_finsum_mem_nonneg (U : Set ℂ) {K : Set ℂ} (hK : IsCompact K) :
    0 ≤ ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z := by
  rw [riemannXi_divisor_finsum_mem_eq_sum U hK]
  exact Finset.sum_nonneg fun z _ => by
    simpa using Function.locallyFinsuppWithin.le_def.mp (riemannXi_divisor_nonneg U) z
  -- (`Finset.sum_nonneg` — the `to_additive`-named twin at
  -- Group/Finset.lean:119–120, additive name explicit in the attribute.)
  -- OBLIG N-SEQ (DISCHARGED): M11 = built Mult.lean:410, imported.
  -- OBLIG S1N1-3 (LOW, incl. finding R6): the pointwise extraction crosses
  -- the `FunLike` seam and the Pi order — `le_def.mp …` yields the Pi-order
  -- fact `(0 : ℂ → ℤ) ≤ ⇑D` (LocallyFinsupp.lean:404; the `LE` instance :401
  -- is pointwise, exactly the order M11 is stated in); its application at
  -- `z` is definitional (`Pi.le_def` if not), then `Pi.zero_apply`
  -- (Pi/Defs.lean:49) inside the `simpa`. Fallback:
  --   have h0 : (0 : ℂ → ℤ) ≤ ⇑(MeromorphicOn.divisor riemannXi U) :=
  --     Function.locallyFinsuppWithin.le_def.mp (riemannXi_divisor_nonneg U)
  --   have hz := Pi.le_def.mp h0 z
  --   simpa using hz

/-! ## N1.4. The natural-number reading `[MULT via N1.3]`

The honest form of "the sum is a natural number": the ℤ-valued sum equals the
cast of its `toNat`. A cast identity, NOT a counting function — no ℕ-valued
object is named (death condition 4; N-DEFERRED-2). -/

theorem riemannXi_divisor_finsum_mem_toNat (U : Set ℂ) {K : Set ℂ} (hK : IsCompact K) :
    ((∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z).toNat : ℤ)
      = ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z :=
  Int.toNat_of_nonneg (riemannXi_divisor_finsum_mem_nonneg U hK)
  -- (`Int.toNat_of_nonneg` — Lean core, in scope everywhere at the pin;
  -- usage precedent Mathlib/NumberTheory/Pell.lean:472.)

/-! ## N1.5. Monotonicity under `K₁ ⊆ K₂` `[MULT: M10, M11]`

Deliberate asymmetry: only `K₂` need be compact — `K₁` inherits finiteness by
inclusion, so both sums are honest finite sums and no junk-value caveat
arises (finding R5). Strictly more `K`-neutral than requiring both compact. -/

theorem riemannXi_divisor_finsum_mem_mono (U : Set ℂ) {K₁ K₂ : Set ℂ}
    (hK₂ : IsCompact K₂) (hK : K₁ ⊆ K₂) :
    ∑ᶠ z ∈ K₁, MeromorphicOn.divisor riemannXi U z
      ≤ ∑ᶠ z ∈ K₂, MeromorphicOn.divisor riemannXi U z := by
  have h₂ := riemannXi_divisor_inter_support_finite U hK₂
  have h₁ : (K₁ ∩ Function.support (MeromorphicOn.divisor riemannXi U)).Finite :=
    h₂.subset (Set.inter_subset_inter hK Set.Subset.rfl)
  rw [finsum_mem_eq_sum _ h₁, finsum_mem_eq_sum _ h₂]
  apply Finset.sum_le_sum_of_subset_of_nonneg
  · exact Set.Finite.toFinset_subset_toFinset.mpr (Set.inter_subset_inter hK Set.Subset.rfl)
  · intro z _ _
    simpa using Function.locallyFinsuppWithin.le_def.mp (riemannXi_divisor_nonneg U) z
  -- (`Finset.sum_le_sum_of_subset_of_nonneg` — additive name EXPLICIT in the
  -- attribute at Group/Finset.lean:131, hypothesis shape
  -- `(h : s ⊆ t) (hf : ∀ i ∈ t, i ∉ s → 0 ≤ f i)` verified verbatim, so this
  -- name is not S1N1-SUM-exposed. `Set.Finite.subset` —
  -- Data/Set/Finite/Basic.lean:497; `Set.inter_subset_inter` — Basic.lean:814;
  -- `Set.Subset.rfl` — Basic.lean:268.)
  -- OBLIG N-SEQ (DISCHARGED): M10 (via N1.1), M11 — built Mult.lean, imported.
  -- OBLIG S1N1-SUM applies to the two `finsum_mem_eq_sum` rewrites (see N1.2).
  -- OBLIG S1N1-5 (MEDIUM): the two `toFinset`s in the post-`rw` goal are
  -- attached to the specific proof terms `h₁`, `h₂`;
  -- `Set.Finite.toFinset_subset_toFinset.mpr` (protected,
  -- Finite/Basic.lean:149, `@[gcongr, mono]` at :148) must unify its implicit
  -- `{hs} {ht}` with exactly those (proof irrelevance guarantees the values;
  -- the elaborator must pick them from the goal). Fallbacks for the first
  -- bullet, in order:
  --   · gcongr    -- :131 and :148–:149 both carry the attr, re-verified
  --   · exact Set.Finite.toFinset_mono (Set.inter_subset_inter hK Set.Subset.rfl)
  --     -- alias at Finite/Basic.lean:156
  -- OBLIG S1N1-3 applies to the second bullet (same fallback as N1.3).

/-! ### Block D — invariance under the three symmetries, parameterized by `K` (N1.6 – N1.8)

Two signatures per symmetry: a summand-transport form (pure congruence from
the M14/M15 pointwise divisor identities) and an enumeration-transport
("image") form. Neither requires `K` compact: `finsum_mem_congr` and
`finsum_mem_image` are hypothesis-free on finiteness (verified at
Finprod.lean:565/:929), and on infinite-support windows both sides take the
same junk value, so the equations are unconditionally true and
unconditionally stated. The symmetry hypotheses are M14/M15's own hypothesis
shapes, verbatim (re-verified against the built Mult.lean:573/:634/:670). -/

/-! ## N1.6. Reflection `s ↦ 1 - s` `[MULT: M14]` -/

theorem riemannXi_divisor_finsum_mem_comp_one_sub {U : Set ℂ}
    (hU : ∀ z : ℂ, (1 - z) ∈ U ↔ z ∈ U) (K : Set ℂ) :
    ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U (1 - z)
      = ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z :=
  finsum_mem_congr rfl fun z _ => riemannXi_divisor_one_sub hU z     -- M14
  -- (`finsum_mem_congr` — additive twin of Finprod.lean:565–566, the one
  -- generated additive name WITH in-tree usage precedent,
  -- Data/Set/Card/Arithmetic.lean:112.)
  -- OBLIG N-SEQ (DISCHARGED): M14 = built Mult.lean:573, imported; `hU`
  -- shape verbatim.

theorem riemannXi_divisor_finsum_mem_image_one_sub {U : Set ℂ}
    (hU : ∀ z : ℂ, (1 - z) ∈ U ↔ z ∈ U) (K : Set ℂ) :
    ∑ᶠ z ∈ (fun w : ℂ => 1 - w) '' K, MeromorphicOn.divisor riemannXi U z
      = ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z := by
  have hinv : Function.Involutive (fun w : ℂ => 1 - w) := fun w => sub_sub_cancel 1 w
  rw [finsum_mem_image (Set.injOn_of_injective hinv.injective)]
  exact riemannXi_divisor_finsum_mem_comp_one_sub hU K
  -- (`sub_sub_cancel` — additive twin of `div_div_cancel`,
  -- Group/Basic.lean:933, attr `@[to_additive (attr := simp)]` :932, so
  -- `sub_sub_cancel 1 w : 1 - (1 - w) = w`. `Set.injOn_of_injective` —
  -- Data/Set/Function.lean:295; `Function.Involutive.injective` —
  -- Logic/Function/Basic.lean:1030.)
  -- OBLIG S1N1-SUM applies to `finsum_mem_image` (generated additive name,
  -- Finprod.lean:929–936, hypothesis-free on finiteness; `#check` probe in
  -- the promotion PR).
  -- OBLIG S1N1-6 (LOW, finding-A2 class): after the `rw` the summand carries
  -- the beta-redex `D ((fun w => 1 - w) z)`; the redex sits under an `exact`,
  -- which works up to defeq — no syntactic rewrite must see through it.
  -- Fallback:
  --   simpa using riemannXi_divisor_finsum_mem_comp_one_sub hU K

/-! ## N1.7. Conjugation `s ↦ conj s` `[MULT: M15]` (hence `[CONJ]` provenance, repo:`Conj.lean:452`, merged PR #307) -/

theorem riemannXi_divisor_finsum_mem_comp_conj {U : Set ℂ}
    (hU : ∀ z : ℂ, (starRingEnd ℂ) z ∈ U ↔ z ∈ U) (K : Set ℂ) :
    ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U ((starRingEnd ℂ) z)
      = ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z :=
  finsum_mem_congr rfl fun z _ => riemannXi_divisor_conj hU z        -- M15
  -- OBLIG N-SEQ (DISCHARGED): M15 = built Mult.lean:634, imported; `hU`
  -- shape verbatim (M15 itself carries the merged conjugation package,
  -- repo:`Conj.lean:452`, PR #307).

theorem riemannXi_divisor_finsum_mem_image_conj {U : Set ℂ}
    (hU : ∀ z : ℂ, (starRingEnd ℂ) z ∈ U ↔ z ∈ U) (K : Set ℂ) :
    ∑ᶠ z ∈ (starRingEnd ℂ) '' K, MeromorphicOn.divisor riemannXi U z
      = ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z := by
  have hinv : Function.Involutive ⇑(starRingEnd ℂ) := fun z => starRingEnd_self_apply z
  rw [finsum_mem_image (Set.injOn_of_injective hinv.injective)]
  exact riemannXi_divisor_finsum_mem_comp_conj hU K
  -- OBLIG S1N1-7a (LOW): `(starRingEnd ℂ) '' K` needs the
  -- `RingHom → function` coercion under `Set.image`, and `hinv` is stated at
  -- the coerced function so `hinv.injective` matches it. Fallback: the
  -- explicit lambda
  --   have hinv : Function.Involutive (fun z : ℂ => (starRingEnd ℂ) z) :=
  --     fun z => starRingEnd_self_apply z
  -- with, if needed, a preliminary
  --   `show ∑ᶠ z ∈ (fun z : ℂ => (starRingEnd ℂ) z) '' K, _ = _`.
  -- OBLIG S1N1-7b (LOW): `starRingEnd_self_apply` — Algebra/Star/Basic.lean
  -- :348 — is the primary recorded spelling; `Complex.conj_conj` exists at
  -- the pin only as `alias Complex.conj_conj := starRingEnd_self_apply`
  -- (:364; also `RCLike.conj_conj` :366) — a same-term fallback (correction
  -- recorded at RH-011 acceptance).
  -- OBLIG S1N1-SUM and S1N1-6 apply as in N1.6.

/-! ## N1.8. Composite `s ↦ 1 - conj s` `[MULT: M15]`

Mirroring M15's own note: NEITHER symmetry hypothesis alone stabilizes
`1 - conj ·`; both `hU₁` and `hU₂` are required, in the same order M15 takes
them (re-verified against the built Mult.lean:670). -/

theorem riemannXi_divisor_finsum_mem_comp_one_sub_conj {U : Set ℂ}
    (hU₁ : ∀ z : ℂ, (1 - z) ∈ U ↔ z ∈ U)
    (hU₂ : ∀ z : ℂ, (starRingEnd ℂ) z ∈ U ↔ z ∈ U) (K : Set ℂ) :
    ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U (1 - (starRingEnd ℂ) z)
      = ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z :=
  finsum_mem_congr rfl fun z _ => riemannXi_divisor_one_sub_conj hU₁ hU₂ z   -- M15
  -- OBLIG N-SEQ (DISCHARGED): M15 composite leg = built Mult.lean:670,
  -- imported; `hU₁`/`hU₂` shapes and order verbatim.

theorem riemannXi_divisor_finsum_mem_image_one_sub_conj {U : Set ℂ}
    (hU₁ : ∀ z : ℂ, (1 - z) ∈ U ↔ z ∈ U)
    (hU₂ : ∀ z : ℂ, (starRingEnd ℂ) z ∈ U ↔ z ∈ U) (K : Set ℂ) :
    ∑ᶠ z ∈ (fun w : ℂ => 1 - (starRingEnd ℂ) w) '' K, MeromorphicOn.divisor riemannXi U z
      = ∑ᶠ z ∈ K, MeromorphicOn.divisor riemannXi U z := by
  have hinv : Function.Involutive (fun w : ℂ => 1 - (starRingEnd ℂ) w) := fun z => by
    simp only [map_sub, map_one, starRingEnd_self_apply, sub_sub_cancel]
  rw [finsum_mem_image (Set.injOn_of_injective hinv.injective)]
  exact riemannXi_divisor_finsum_mem_comp_one_sub_conj hU₁ hU₂ K
  -- (`map_sub` — additive twin of `map_div`, Hom/Defs.lean:461, applies to
  -- `starRingEnd ℂ` through `RingHomClass`; `map_one` — Hom/Defs.lean:234.)
  -- OBLIG S1N1-8 (LOW): the involution `simp only` chain must close
  -- `1 - conj (1 - conj z) = z`. Fallback (explicit calc replacing the
  -- `simp only` line):
  --   calc 1 - (starRingEnd ℂ) (1 - (starRingEnd ℂ) z)
  --       = 1 - ((starRingEnd ℂ) 1 - (starRingEnd ℂ) ((starRingEnd ℂ) z)) := by
  --         rw [map_sub]
  --     _ = 1 - (1 - z) := by rw [map_one, starRingEnd_self_apply]
  --     _ = z := sub_sub_cancel 1 z
  -- (explicit `RingHom.map_sub` fallback: Ring/Hom/Defs.lean:500.)
  -- OBLIG S1N1-SUM and S1N1-6 apply as in N1.6.

/-! ### Block E — the symmetric-window set identities (N1.9) `[GEN]` `[PIN]` — the `hK`-consuming lemmas

The only statements where "`K` is symmetric" does any work. Composed with the
N1.6–N1.8 image forms they give, for symmetric `K`, that the compact sum is
literally fixed by each of the three symmetries; exported standalone because
future route bookkeeping will consume `σ '' K = K` directly. Generic set
identities over ℂ — no divisor content, no package prerequisite, natural
Mathlib upstream (`[GEN]`). -/

theorem image_one_sub_of_symm {K : Set ℂ} (hK : ∀ z : ℂ, (1 - z) ∈ K ↔ z ∈ K) :
    (fun w : ℂ => 1 - w) '' K = K := by
  have hinv : Function.Involutive (fun w : ℂ => 1 - w) := fun w => sub_sub_cancel 1 w
  ext z
  rw [Set.mem_image_iff_of_inverse hinv.leftInverse hinv.rightInverse]
  exact hK z
  -- (`Set.mem_image_iff_of_inverse` — Data/Set/Image.lean:355, inside
  -- `namespace Set`; `Function.Involutive.leftInverse` / `.rightInverse` —
  -- Logic/Function/Basic.lean:1022 / :1028, corrected locators per
  -- finding R4.)
  -- OBLIG S1N1-9 (LOW): after `ext z; rw [...]` the membership goal carries
  -- a beta-redex `(fun w => 1 - w) z ∈ K`; `exact hK z` closes up to defeq.
  -- Fallback:
  --   show (1 - z) ∈ K ↔ z ∈ K
  --   exact hK z
  -- Alternative route (contract-recorded):
  -- `Function.Involutive.image_eq_preimage_symm` (Data/Set/Image.lean:351,
  -- declared `_root_.`; that `_symm`-suffixed name is the one declared at the
  -- pin — no un-suffixed `image_eq_preimage` exists there) plus `Set.ext hK`.

theorem image_conj_of_symm {K : Set ℂ} (hK : ∀ z : ℂ, (starRingEnd ℂ) z ∈ K ↔ z ∈ K) :
    (starRingEnd ℂ) '' K = K := by
  have hinv : Function.Involutive ⇑(starRingEnd ℂ) := fun z => starRingEnd_self_apply z
  ext z
  rw [Set.mem_image_iff_of_inverse hinv.leftInverse hinv.rightInverse]
  exact hK z
  -- OBLIG S1N1-9 (LOW): same beta-redex note and `show` fallback as
  -- `image_one_sub_of_symm`; OBLIG S1N1-7a/7b (LOW): same coercion and
  -- `starRingEnd_self_apply` notes (and fallbacks) as N1.7.

theorem image_one_sub_conj_of_symm {K : Set ℂ}
    (hK : ∀ z : ℂ, (1 - (starRingEnd ℂ) z) ∈ K ↔ z ∈ K) :
    (fun w : ℂ => 1 - (starRingEnd ℂ) w) '' K = K := by
  have hinv : Function.Involutive (fun w : ℂ => 1 - (starRingEnd ℂ) w) := fun z => by
    simp only [map_sub, map_one, starRingEnd_self_apply, sub_sub_cancel]
  ext z
  rw [Set.mem_image_iff_of_inverse hinv.leftInverse hinv.rightInverse]
  exact hK z
  -- OBLIG S1N1-9 (LOW): same beta-redex note and `show` fallback as
  -- `image_one_sub_of_symm`; OBLIG S1N1-8 (LOW): same involution `simp only`
  -- chain and explicit-calc fallback as N1.8.

/-!
End of the 23-signature surface (N2-D1..D6: 6; N2-D7: 2; N1.1 = N2-D8: 1;
N2-D9: 1; N1.2-N1.5: 4; N1.6-N1.8: 6; N1.9: 3). No `def`, no `sorry`, no
`admit`, no `axiom`, no new instance. Neutrality re-checked at drafting: no
`closedBall`, `sphere`, `ball`, `‖·‖`, `.im`, `.re`, strip, box, or interval
appears in any SIGNATURE above (shapes occur only inside the N2-d fallback
comment, licensed as proof-internal by the neutrality rule). Promotion of
this draft is a separate stage-two change; the kernel via CI remains the
sole judge, and a green build on that change is the only claim of proof.
-/
