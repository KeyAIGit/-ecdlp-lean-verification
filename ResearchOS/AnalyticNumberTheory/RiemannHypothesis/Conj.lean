/-
Built RH conjugation-symmetry package: promotion of the independently
accepted Z1-Z9 statement surface in
`domains/riemann-hypothesis/CONJ_SYMMETRY_CONTRACT.md`.

The package proves that complex conjugation commutes with `riemannZeta`, with
both completions, and with the built `riemannXi`; that the zero set is
invariant under conjugation as a set; that a nontrivial zero forces all four
of `ρ`, `1 − ρ`, `conj ρ`, `1 − conj ρ` to be zeros; and that the local
`analyticOrderAt` is transported by conjugation. Two generic complex-analysis
lemmas missing at the pin (`AnalyticAt.conj_conj`, `analyticOrderAt_conj_conj`)
are supplied as the package's registered obligation `S1C-ORD`.

Conjugation is proved **independently of the functional equation**, from the
Dirichlet series on `1 < re s` plus the identity theorem; `1 − s` enters only
in Z8, through the already kernel-checked bridge P3, after conjugation is
established. These are foundation interfaces only: nothing here proves,
disproves, or supplies evidence about the Riemann Hypothesis.

Barrier boundary: this package supplies the conjugation leg of `S1-CONJ` only.
The barrier's exit evidence also requires divisor invariance under
`ρ ↦ 1 − conj ρ`, which belongs to the still-open `S1-MULTIPLICITY` divisor
package. `S1-CONJ` therefore remains open after this promotion.

Z8 imports the kernel-checked target bridge (P2, P3); Z7 and Z9-xi import the
kernel-checked xi package (`riemannXi`). All sixteen public declarations are
ledgered as `RH-CONJ-*` rows in `VERIFIED_RESEARCHOS.md` and audited through
the generated `ResearchOS/LedgerAxiomAudit.lean` with axiom base `standard`.

Pinned Mathlib: fabf563a7c95a166b8d7b6efca11c8b4dc9d911f (v4.31.0).
-/
import ResearchOS.AnalyticNumberTheory.RiemannHypothesis.TargetBridge  -- Z8: bridge P2, P3
import ResearchOS.AnalyticNumberTheory.RiemannHypothesis.Xi            -- Z7, Z9-xi: riemannXi
import Mathlib.NumberTheory.LSeries.ZetaZeros              -- riemannZeta API (transitively RiemannZeta.lean)
import Mathlib.NumberTheory.Harmonic.ZetaAsymp             -- riemannZeta_one (totalized value at the pole)
import Mathlib.Analysis.Calculus.Deriv.Star                -- DifferentiableAt.conj_conj / differentiableAt_conj_conj_iff
import Mathlib.Analysis.Analytic.Uniqueness                -- AnalyticOnNhd.eqOn_of_preconnected_of_eventuallyEq / eq_of_eventuallyEq
import Mathlib.Analysis.Normed.Module.Connected            -- isConnected_compl_singleton_of_one_lt_rank
import Mathlib.LinearAlgebra.Complex.FiniteDimensional     -- rank_real_complex
import Mathlib.Analysis.SpecialFunctions.Complex.Arg       -- Complex.natCast_arg, arg_ofReal_of_nonneg
import Mathlib.Analysis.Analytic.Order                     -- analyticOrderAt API (Z9)
import Mathlib.Analysis.Complex.CauchyIntegral             -- DifferentiableOn.analyticAt / .analyticOnNhd

open Complex
open scoped Real ComplexConjugate
open Filter          -- deviation from contract preamble: needed for `eventually_of_mem`
                     -- (namespace Filter, Order/Filter/Basic.lean:641) and the `∀ᶠ`/`=ᶠ`
                     -- API, exactly as the in-tree template DirichletContinuation.lean:45
open scoped Topology -- deviation from contract preamble: needed for the `𝓝` neighborhood
                     -- notation used in Z2, Z3, Z9

/-! ## Z1. `Gammaℝ` conjugation (helper; also a natural Mathlib upstream)

Unconditional: both sides are total, and every factor is conj-equivariant.
Branch discipline: the only `cpow` conjugation is on the real-positive base
`↑π`, discharged with `arg_ofReal_of_nonneg`. -/

theorem Gammaℝ_conj (s : ℂ) : Gammaℝ ((starRingEnd ℂ) s) = (starRingEnd ℂ) (Gammaℝ s) := by
  rw [Gammaℝ_def, Gammaℝ_def, map_mul]
  congr 1
  · -- π ^ (-(conj s) / 2) = conj (π ^ (-s / 2)) : real-positive base, off the branch cut
    have harg : (↑π : ℂ).arg ≠ π := by
      rw [Complex.arg_ofReal_of_nonneg Real.pi_pos.le]
      exact Real.pi_ne_zero.symm
    -- OBLIG S1C-6: conj-push through `-·/2`, then the `cpow_conj` triple-conj unwind
    have h : -((starRingEnd ℂ) s) / 2 = (starRingEnd ℂ) (-s / 2) := by
      rw [map_div₀, map_neg, Complex.conj_ofNat]
    rw [h, Complex.cpow_conj _ _ harg, Complex.conj_ofReal]
    -- `cpow_conj` (Pow/Complex.lean:234) : x ^ conj n = conj (conj x ^ n); after
    -- `conj ↑π = ↑π` (conj_ofReal) both sides are `conj (↑π ^ (-s / 2))`.
  · -- Gamma (conj s / 2) = conj (Gamma (s / 2)) via Gamma_conj (Gamma/Basic.lean:355)
    have h : (starRingEnd ℂ) s / 2 = (starRingEnd ℂ) (s / 2) := by
      rw [map_div₀, Complex.conj_ofNat]
    rw [h, Complex.Gamma_conj]

/-! ## Z2. C1: global zeta conjugation symmetry

Hypothesis-free. `s = 1`: totalized point, `ζ(1)` is the coercion of a real
number (`riemannZeta_one` + `ofReal_log`, mirroring the pin's own realness
cast walk in `riemannZeta_one_ne_zero`, ZetaAsymp.lean:431-435). `s ≠ 1`:
Schwarz reflection via the identity theorem on `{1}ᶜ` with agreement on the
open half-plane `1 < re` from the Dirichlet series (template:
DirichletContinuation.lean:124-144). NOT derived from the functional
equation. -/

theorem riemannZeta_conj (s : ℂ) :
    riemannZeta ((starRingEnd ℂ) s) = (starRingEnd ℂ) (riemannZeta s) := by
  rcases eq_or_ne s 1 with rfl | hs1
  · -- totalized point: conj 1 = 1, and ζ(1) is the coercion of a real number.
    -- DEVIATION from the contract skeleton: the skeleton's `s = 1` block is a
    -- review-annotated composite (simpa + leftover lines); replaced by ONE coherent
    -- proof mirroring the pinned ZetaAsymp.lean:434 one-step simp set (fix F2 / S1C-3).
    rw [map_one]
    -- goal: riemannZeta 1 = (starRingEnd ℂ) (riemannZeta 1)
    have hre : riemannZeta 1 =
        (((Real.eulerMascheroniConstant - Real.log (4 * π)) / 2 : ℝ) : ℂ) := by
      simp only [riemannZeta_one, ofReal_log (by positivity : (0 : ℝ) ≤ 4 * π), push_cast]
      -- LOWCONF: OBLIG S1C-3 — the `push_cast`-in-simp-set idiom is the pin's own
      -- (ZetaAsymp.lean:434), but the pinned precedent closes a ≠-goal; this is a
      -- two-sided equality, so the simp normal form could drift (finding L3-2).
      -- Fallback 1 (preferred, mediator-free — standalone `push_cast` takes extra
      -- lemmas and normalizes BOTH sides, no reliance on simp-only closing by rfl):
      --   rw [riemannZeta_one]; push_cast [ofReal_log (by positivity : (0 : ℝ) ≤ 4 * π)]
      -- Fallback 2 (explicit rw chain):
      --   rw [riemannZeta_one, show ((4 : ℂ) * ↑π) = (((4 * π : ℝ)) : ℂ) by push_cast; ring,
      --     ← ofReal_log (by positivity : (0 : ℝ) ≤ 4 * π)]; push_cast; ring
    rw [hre, Complex.conj_ofReal]
  · -- identity theorem on {1}ᶜ; template: DirichletContinuation.lean:124-144
    have hpc : IsPreconnected ({1}ᶜ : Set ℂ) :=
      (isConnected_compl_singleton_of_one_lt_rank
        (rank_real_complex ▸ Nat.one_lt_ofNat) 1).isPreconnected
    have h2 : (2 : ℂ) ∈ ({1}ᶜ : Set ℂ) := by simp
      -- (contract skeleton wrote `norm_num`; `simp` is the compiled in-tree template
      --  shape, DirichletContinuation.lean:133)
    -- g := conj ∘ ζ ∘ conj is ℂ-analytic on {1}ᶜ (antiholomorphic twice = holomorphic)
    have hg : AnalyticOnNhd ℂ
        ((starRingEnd ℂ) ∘ riemannZeta ∘ (starRingEnd ℂ)) ({1}ᶜ : Set ℂ) := by
      refine DifferentiableOn.analyticOnNhd (fun z hz => ?_) isOpen_compl_singleton
      have hz1 : (starRingEnd ℂ) z ≠ 1 := by
        intro h
        have h' := congrArg (starRingEnd ℂ) h
        rw [Complex.conj_conj, map_one] at h'
        exact Set.mem_compl_singleton_iff.mp hz h'
      exact (differentiableAt_conj_conj_iff.mpr
        (differentiableAt_riemannZeta hz1)).differentiableWithinAt
    -- agreement on the OPEN half-plane 1 < re, an 𝓝 2 neighborhood (OBLIG S1C-4)
    have hfg : ((starRingEnd ℂ) ∘ riemannZeta ∘ (starRingEnd ℂ)) =ᶠ[𝓝 2] riemannZeta := by
      refine eventually_of_mem
        ((Complex.continuous_re.isOpen_preimage _ isOpen_Ioi).mem_nhds
          (by simp : 1 < (2 : ℂ).re)) (fun z (hz : 1 < z.re) => ?_)
      have hz' : 1 < ((starRingEnd ℂ) z).re := by rwa [Complex.conj_re]
      simp only [Function.comp_apply]
      rw [zeta_eq_tsum_one_div_nat_cpow hz', zeta_eq_tsum_one_div_nat_cpow hz,
        starRingEnd_apply, tsum_star]
      -- OBLIG S1C-2: `tsum_star` (Constructions.lean:361) is stated for an arbitrary
      -- SummationFilter `L`; the plain `∑'` is `tsum · (unconditional _)`
      -- (Defs.lean:160), so it applies by instantiation. The `starRingEnd_apply`
      -- rewrite fires only on the OUTER application (rw rewrites the first-match
      -- instantiation; the exponent's `conj z` is a different instantiation).
      refine tsum_congr fun n => ?_
      -- OBLIG S1C-1: termwise — star (1 / ↑n ^ conj z) = 1 / ↑n ^ z, `n = 0` included
      -- (`natCast_arg` gives arg ↑0 = 0 ≠ π; both sides then use the same 0-base
      -- cpow convention, no case split)
      have harg : ((n : ℂ)).arg ≠ π := by
        rw [Complex.natCast_arg]
        exact Real.pi_ne_zero.symm
      rw [← starRingEnd_apply, map_div₀, map_one, Complex.cpow_conj (n : ℂ) z harg,
        Complex.conj_conj, Complex.conj_natCast]
      -- DEVIATION from the contract skeleton: the skeleton's `congr 1` + `calc`
      -- triple-conj unwind (with a `← cpow_conj` whose direction is wrong as written)
      -- is replaced by this direct forward rewrite chain:
      -- `↑n ^ conj z → conj (conj ↑n ^ z)` (cpow_conj), then the outer double conj
      -- cancels (conj_conj) and `conj ↑n = ↑n` (conj_natCast) closes by rfl.
    have hEq := AnalyticOnNhd.eqOn_of_preconnected_of_eventuallyEq (𝕜 := ℂ)
      hg analyticOn_riemannZeta hpc h2 hfg
    -- at s : conj (ζ (conj s)) = ζ s ; apply conj to both sides
    have h := hEq (Set.mem_compl_singleton_iff.mpr hs1)
    have h' := congrArg (starRingEnd ℂ) h
    simp only [Function.comp_apply, Complex.conj_conj] at h'
    exact h'

/-- Function-level corollary (glue for Z9). -/
theorem riemannZeta_comp_conj :
    (starRingEnd ℂ) ∘ riemannZeta ∘ (starRingEnd ℂ) = riemannZeta :=
  funext fun s => by
    simp only [Function.comp_apply]
    rw [riemannZeta_conj, Complex.conj_conj]

/-! ## Z3. C2: conjugation symmetry of the entire completion `Λ₀`

Second identity-theorem pass, on ALL of ℂ (no puncture): `Λ₀` is entire, so
the univ-version `AnalyticOnNhd.eq_of_eventuallyEq` applies (the
`PreconnectedSpace ℂ` instance resolves in-tree at ZMod.lean:526 — OBLIG
S1C-7). The pointwise identity `Λ = Gammaℝ · ζ` is asserted ONLY on the open
half-plane `1 < re`, where `w ≠ 0`, `Gammaℝ w ≠ 0` hold with proofs; it is
never used on the `Gammaℝ` zero set `−2ℕ ∪ {0}`. Sign source of truth:
`completedRiemannZeta_eq` the THEOREM (RiemannZeta.lean:84). -/

theorem completedRiemannZeta₀_conj (s : ℂ) :
    completedRiemannZeta₀ ((starRingEnd ℂ) s) = (starRingEnd ℂ) (completedRiemannZeta₀ s) := by
  have hg : AnalyticOnNhd ℂ
      ((starRingEnd ℂ) ∘ completedRiemannZeta₀ ∘ (starRingEnd ℂ)) Set.univ := by
    refine DifferentiableOn.analyticOnNhd (fun z _ => ?_) isOpen_univ
    exact (differentiableAt_conj_conj_iff.mpr
      (differentiable_completedZeta₀ _)).differentiableWithinAt
  have hf : AnalyticOnNhd ℂ completedRiemannZeta₀ Set.univ :=
    differentiable_completedZeta₀.differentiableOn.analyticOnNhd isOpen_univ
  have hfg : ((starRingEnd ℂ) ∘ completedRiemannZeta₀ ∘ (starRingEnd ℂ))
      =ᶠ[𝓝 2] completedRiemannZeta₀ := by
    refine eventually_of_mem
      ((Complex.continuous_re.isOpen_preimage _ isOpen_Ioi).mem_nhds
        (by simp : 1 < (2 : ℂ).re)) (fun z (hz : 1 < z.re) => ?_)
    -- On re > 1 : Λ₀ w = Gammaℝ w * ζ w + 1/w + 1/(1-w)                 (OBLIG S1C-5)
    have key : ∀ w : ℂ, 1 < w.re →
        completedRiemannZeta₀ w = Gammaℝ w * riemannZeta w + 1 / w + 1 / (1 - w) := by
      intro w hw
      have hw0 : w ≠ 0 := fun e => by rw [e, Complex.zero_re] at hw; linarith
      have hG : Gammaℝ w ≠ 0 := Complex.Gammaℝ_ne_zero_of_re_pos (by linarith)
      have hΛ : completedRiemannZeta w = Gammaℝ w * riemannZeta w := by
        rw [riemannZeta_def_of_ne_zero hw0, mul_div_cancel₀ _ hG]
      have h := completedRiemannZeta_eq w      -- Λ w = Λ₀ w − 1/w − 1/(1−w) (the THEOREM)
      linear_combination hΛ - h
      -- SIGN NOTE (corrected per review findings CONJ-L1-1, CONJ-L2-3): this closer
      -- MATCHES the merged contract's recorded review fix F1
      -- (`linear_combination hΛ - h  -- review fix F1 (sign)`,
      -- CONJ_SYMMETRY_CONTRACT.md:315; Acceptance note: "corrected F1 to
      -- linear_combination hΛ - h"). The pre-review draft's `h - hΛ` was the
      -- wrong-signed order; do NOT "restore" it. Independent re-derivation —
      -- goalL − goalR = Λ₀ − Gζ − 1/w − 1/(1−w);
      -- (hΛL − hΛR) − (hL − hR) = (Λ − Gζ) − (Λ − Λ₀ + 1/w + 1/(1−w))
      --                        = Λ₀ − Gζ − 1/w − 1/(1−w)  ✓  — so `hΛ - h`, not `h - hΛ`.
      -- The inverses `1/w`, `1/(1−w)` cancel syntactically as ring atoms (no
      -- denominator clearing is needed, so the xi-lane F2 rule is not violated).
    have hz' : 1 < ((starRingEnd ℂ) z).re := by rwa [Complex.conj_re]
    simp only [Function.comp_apply]
    rw [key _ hz', key _ hz, Gammaℝ_conj, riemannZeta_conj]
    simp only [map_add, map_mul, map_div₀, map_one, map_sub, Complex.conj_conj]
    -- OBLIG S1C-5 (closing conj-push): both sides normalize to
    -- `Gammaℝ z * ζ z + 1 / z + 1 / (1 − z)`; if the simp normal form drifts,
    -- alternate: close with `ring_nf` treating `conj z` as an atom is NOT needed —
    -- every conj has been eliminated by the ring-hom lemmas above.
  have h := congrFun (hg.eq_of_eventuallyEq hf hfg) s   -- conj (Λ₀ (conj s)) = Λ₀ s
  have h' := congrArg (starRingEnd ℂ) h
  simp only [Function.comp_apply, Complex.conj_conj] at h'
  exact h'

/-! ## Z4. C2: conjugation symmetry of `Λ` (totalized, global)

Global including the totalized points `s = 0, 1`: Lean's total division gives
`1/0 = 0` and `conj 0 = 0`, so `map_div₀` is valid with NO nonvanishing
hypothesis — the exceptional values transport by construction, not by
meromorphic reasoning. -/

theorem completedRiemannZeta_conj (s : ℂ) :
    completedRiemannZeta ((starRingEnd ℂ) s) = (starRingEnd ℂ) (completedRiemannZeta s) := by
  rw [completedRiemannZeta_eq, completedRiemannZeta_eq s, completedRiemannZeta₀_conj]
  simp only [map_sub, map_div₀, map_one]
  -- OBLIG S1C-8: the RHS conj distributes over `Λ₀ s − 1/s − 1/(1−s)`;
  -- `conj (1 − s) = 1 − conj s` closes via map_sub + map_one; both sides are then
  -- syntactically `conj (Λ₀ s) − 1 / conj s − 1 / (1 − conj s)`.
  -- Fallback if a residue remains: append `Complex.conj_conj` to the simp set or
  -- finish with `ring`.

/-! ## Z5. C2: membership-level zero symmetry -/

theorem riemannZeta_conj_eq_zero_iff {s : ℂ} :
    riemannZeta ((starRingEnd ℂ) s) = 0 ↔ riemannZeta s = 0 := by
  rw [riemannZeta_conj, starRingEnd_apply, star_eq_zero]

/-! ## Z6. C2: zero-set invariance as set equalities

`riemannZetaZeros` (ZetaZeros.lean:33) is used AS A SET ONLY — membership,
no multiplicity (the `S1-MULTIPLICITY` boundary; multiplicity transport is
Z9, divisor invariance is out of scope). -/

theorem riemannZetaZeros_conj_preimage :
    (starRingEnd ℂ) ⁻¹' riemannZetaZeros = riemannZetaZeros := by
  ext z
  simp only [Set.mem_preimage, mem_riemannZetaZeros]
  exact riemannZeta_conj_eq_zero_iff

theorem riemannZetaZeros_conj_image :
    (starRingEnd ℂ) '' riemannZetaZeros = riemannZetaZeros := by
  rw [Set.image_eq_preimage_of_inverse (f := ⇑(starRingEnd ℂ)) (g := ⇑(starRingEnd ℂ))
      (fun z => Complex.conj_conj z) (fun z => Complex.conj_conj z)]
  exact riemannZetaZeros_conj_preimage
  -- LOWCONF: OBLIG S1C-9 — the two lambdas must elaborate against
  -- `Function.LeftInverse`/`Function.RightInverse` (both are `∀ x, conj (conj x) = x`);
  -- the named `(f := ...) (g := ...)` arguments pin the higher-order unification.
  -- DEVIATION from the contract skeleton (which passed the lambdas positionally with
  -- f, g left implicit): `?g (?f x)` is not a Miller pattern, so f and g are supplied
  -- by name. Fallback: `ext z; simp only [Set.mem_image, mem_riemannZetaZeros];`
  -- then the two directions via `riemannZeta_conj_eq_zero_iff` and the witness
  -- `⟨conj z, ..., Complex.conj_conj z⟩`.

/-! ## Z7. C2: xi conjugation symmetry (xi-package prerequisite)

`riemannXi` is the X1 definition `(1 + s*(s−1)*Λ₀ s)/2` from the sibling xi
draft (see header) — referenced, not re-defined. The analytic content is
exactly Z3; the rest is ring-hom algebra. -/

theorem riemannXi_conj (s : ℂ) :
    riemannXi ((starRingEnd ℂ) s) = (starRingEnd ℂ) (riemannXi s) := by
  unfold riemannXi
  rw [completedRiemannZeta₀_conj]
  simp only [map_div₀, map_add, map_one, map_mul, map_sub, Complex.conj_ofNat]
  -- OBLIG S1C-10: both sides normalize to
  -- `(1 + conj s * (conj s − 1) * conj (Λ₀ s)) / 2` (same association as the
  -- definition body). Fallback: `ring_nf` with `conj s`, `conj (Λ₀ s)` as atoms.

/-- Function-level corollary (glue for Z9-xi). -/
theorem riemannXi_comp_conj :
    (starRingEnd ℂ) ∘ riemannXi ∘ (starRingEnd ℂ) = riemannXi :=
  funext fun s => by
    simp only [Function.comp_apply]
    rw [riemannXi_conj, Complex.conj_conj]

/-! ## Z8. C3: the fourfold zero action

Both statements consume the BRIDGE prerequisites (built module, see header):
P3 (`riemannZeta_one_sub_eq_zero_iff`) for the reflection legs, P2
(`riemannZeta_zero_mem_critical_strip`) for the primed form. `1 − s` enters
ONLY through P3 — conjugation itself was proved independently above. The
trivial-zero exclusion is verbatim `¬∃ n : ℕ, ρ = -2 * (n + 1)`. -/

theorem riemannZeta_fourfold_zero {ρ : ℂ} (h0 : 0 < ρ.re) (h1 : ρ.re < 1)
    (hz : riemannZeta ρ = 0) :
    riemannZeta (1 - ρ) = 0 ∧ riemannZeta ((starRingEnd ℂ) ρ) = 0 ∧
      riemannZeta (1 - (starRingEnd ℂ) ρ) = 0 := by
  have hc0 : 0 < ((starRingEnd ℂ) ρ).re := by rwa [Complex.conj_re]
  have hc1 : ((starRingEnd ℂ) ρ).re < 1 := by rwa [Complex.conj_re]
  have hzc : riemannZeta ((starRingEnd ℂ) ρ) = 0 := riemannZeta_conj_eq_zero_iff.mpr hz
  exact ⟨(riemannZeta_one_sub_eq_zero_iff h0 h1).mpr hz,          -- BRIDGE P3
    hzc,
    (riemannZeta_one_sub_eq_zero_iff hc0 hc1).mpr hzc⟩            -- BRIDGE P3 at conj ρ

theorem riemannZeta_fourfold_zero' {ρ : ℂ} (hz : riemannZeta ρ = 0)
    (htriv : ¬∃ n : ℕ, ρ = -2 * (n + 1)) :
    riemannZeta (1 - ρ) = 0 ∧ riemannZeta ((starRingEnd ℂ) ρ) = 0 ∧
      riemannZeta (1 - (starRingEnd ℂ) ρ) = 0 := by
  obtain ⟨h0, h1⟩ := riemannZeta_zero_mem_critical_strip hz htriv  -- BRIDGE P2
  exact riemannZeta_fourfold_zero h0 h1 hz

/-! ## Z9. C4: analytic-order transport under conjugation (OBLIGATION S1C-ORD)

The two generic lemmas below do not exist at the pin (Analytic/Order.lean
studied in full — no conj/star result of any kind) and are assembled here
from pinned ingredients per the contract sketch. Natural Mathlib upstreams. -/

/-- (i) Analytic transport of `conj ∘ f ∘ conj` (ℂ-specific; missing at the pin).
Assembly: `eventually_analyticAt` (ChangeOrigin.lean:378) extracts an open
`U ∋ x` of analyticity via `eventually_nhds_iff` (Neighborhoods.lean:68); on
the conj-preimage open set, pointwise `differentiableAt_conj_conj_iff`
(Deriv/Star.lean:123) gives differentiability; conclude with
`DifferentiableOn.analyticAt` (CauchyIntegral.lean:625). -/
theorem AnalyticAt.conj_conj {f : ℂ → ℂ} {x : ℂ} (hf : AnalyticAt ℂ f x) :
    AnalyticAt ℂ ((starRingEnd ℂ) ∘ f ∘ (starRingEnd ℂ)) ((starRingEnd ℂ) x) := by
  obtain ⟨U, hU, hUopen, hxU⟩ := eventually_nhds_iff.mp hf.eventually_analyticAt
  have hVopen : IsOpen ((starRingEnd ℂ) ⁻¹' U) :=
    Complex.continuous_conj.isOpen_preimage U hUopen
  have hxV : (starRingEnd ℂ) x ∈ (starRingEnd ℂ) ⁻¹' U := by
    simp only [Set.mem_preimage, Complex.conj_conj]
    exact hxU
  refine DifferentiableOn.analyticAt (fun z hz => ?_) (hVopen.mem_nhds hxV)
  -- hz : z ∈ conj ⁻¹' U, i.e. conj z ∈ U (defeq via `Set.mem_preimage : _ ↔ _ := .rfl`);
  -- the point argument is passed explicitly so no preimage-unfolding is left to
  -- higher-order unification.
  exact (differentiableAt_conj_conj_iff.mpr
    ((hU ((starRingEnd ℂ) z) hz).differentiableAt)).differentiableWithinAt

/-- (ii) Order transport under conjugation (missing at the pin). Three-case
split per the contract sketch: not-analytic (junk value `0` on both sides via
the involution argument), order `⊤` (`analyticOrderAt_eq_top`, Order.lean:75,
with the eventual vanishing set transported through the conj preimage), order
`↑n` (`AnalyticAt.analyticOrderAt_eq_natCast`, Order.lean:86, with witness
transport `g ↦ conj ∘ g ∘ conj`). -/
theorem analyticOrderAt_conj_conj (f : ℂ → ℂ) (z : ℂ) :
    analyticOrderAt ((starRingEnd ℂ) ∘ f ∘ (starRingEnd ℂ)) ((starRingEnd ℂ) z)
      = analyticOrderAt f z := by
  -- the involution: conj ∘ (conj ∘ f ∘ conj) ∘ conj = f
  have hinv :
      (starRingEnd ℂ) ∘ ((starRingEnd ℂ) ∘ f ∘ (starRingEnd ℂ)) ∘ (starRingEnd ℂ) = f := by
    funext w
    simp only [Function.comp_apply, Complex.conj_conj]
  by_cases hf : AnalyticAt ℂ f z
  · -- ℕ∞ case analysis: `⊤` versus `↑n`, via ENat.ne_top_iff_exists
    -- (Data/ENat/Basic.lean:371) — DEVIATION from the contract sketch's
    -- `cases h : analyticOrderAt f z` (WithTop constructor names are
    -- `none`/`some`; the iff-based split avoids that syntax entirely).
    rcases eq_or_ne (analyticOrderAt f z) ⊤ with htop | hne
    · -- order ⊤: transport the eventual vanishing set through the conj preimage
      have hev : ∀ᶠ w in 𝓝 ((starRingEnd ℂ) z),
          ((starRingEnd ℂ) ∘ f ∘ (starRingEnd ℂ)) w = 0 := by
        obtain ⟨t, ht, htopen, hzt⟩ :=
          eventually_nhds_iff.mp (analyticOrderAt_eq_top.mp htop)
        refine eventually_nhds_iff.mpr
          ⟨(starRingEnd ℂ) ⁻¹' t, fun w hw => ?_,
            Complex.continuous_conj.isOpen_preimage t htopen, ?_⟩
        · simp only [Function.comp_apply, ht ((starRingEnd ℂ) w) hw, map_zero]
        · simp only [Set.mem_preimage, Complex.conj_conj]
          exact hzt
      rw [htop]
      exact analyticOrderAt_eq_top.mpr hev
    · -- order ↑n: witness transport g ↦ conj ∘ g ∘ conj
      obtain ⟨n, hn⟩ := ENat.ne_top_iff_exists.mp hne   -- hn : ↑n = analyticOrderAt f z
      obtain ⟨g, hg_an, hg_ne, hg_ev⟩ := hf.analyticOrderAt_eq_natCast.mp hn.symm
      obtain ⟨t, ht, htopen, hzt⟩ := eventually_nhds_iff.mp hg_ev
      have hgc_ne : ((starRingEnd ℂ) ∘ g ∘ (starRingEnd ℂ)) ((starRingEnd ℂ) z) ≠ 0 := by
        simp only [Function.comp_apply, Complex.conj_conj]
        rw [ne_eq, starRingEnd_apply, star_eq_zero]
        exact hg_ne
        -- FIXED per finding L3E-1 (S2): the previous single simp set mixed
        -- `starRingEnd_apply` with `Complex.conj_conj`; simp rewrites bottom-up, so
        -- the innermost `(starRingEnd ℂ) z` became `star z` BEFORE the enclosing
        -- conj-conj node was visited, `Complex.conj_conj` (pattern
        -- `starRingEnd R (starRingEnd R x)`) never fired, and the goal stuck as
        -- `¬ g (star (star z)) = 0` (`star_star` was not in the set). Now the simp
        -- set carries no `starRingEnd_apply`, so `conj_conj` collapses the inner
        -- pair to `g z`; the sequential `rw` then converts only the OUTER conj to
        -- `star` form and discharges via `star_eq_zero` (Algebra/Star/Basic.lean:267).
        -- Fallback if `rw [ne_eq]` misfires on the already-unfolded `≠`:
        --   simp only [Function.comp_apply, Complex.conj_conj]
        --   rw [starRingEnd_apply, star_ne_zero]
        --   exact hg_ne
      rw [← hn]
      refine hf.conj_conj.analyticOrderAt_eq_natCast.mpr
        ⟨(starRingEnd ℂ) ∘ g ∘ (starRingEnd ℂ), hg_an.conj_conj, hgc_ne, ?_⟩
      -- RESTRUCTURED per finding L3-1: the ∀ᶠ witness equation is proved IN PLACE
      -- (as the `?_` hole of the lemma's own existential) rather than as a
      -- separately-stated `have hev'`, so the `•` in the goal carries
      -- `analyticOrderAt_eq_natCast`'s own SMul ℂ ℂ instance path (Order.lean:86)
      -- and no cross-statement defeq unification is needed.
      refine eventually_nhds_iff.mpr
        ⟨(starRingEnd ℂ) ⁻¹' t, fun w hw => ?_,
          Complex.continuous_conj.isOpen_preimage t htopen, ?_⟩
      · have hfw := ht ((starRingEnd ℂ) w) hw
        -- hfw : f (conj w) = (conj w − z) ^ n • g (conj w); push conj through:
        -- • = * in ℂ (smul_eq_mul), then map_mul/map_pow/map_sub + conj_conj give
        -- conj (f (conj w)) = (w − conj z) ^ n * conj (g (conj w)).
        simp only [Function.comp_apply, hfw, smul_eq_mul, map_mul, map_pow, map_sub,
          Complex.conj_conj]
        -- LOWCONF: the `smul_eq_mul` matching assumes the ℂ-module smul on ℂ is
        -- the mul-derived one (it is; same normal form Order.lean:557 itself uses
        -- on exactly this witness shape at the pin).
        -- Fallback: replace `smul_eq_mul` by `smul_eq_mul (α := ℂ)` or rewrite the
        -- goal with `show` into the `*` form first.
      · simp only [Set.mem_preimage, Complex.conj_conj]
        exact hzt
  · -- junk-value case: both sides are 0 (Order.lean:64); the involution argument
    -- shows conj ∘ f ∘ conj is not analytic at conj z either
    have hg : ¬ AnalyticAt ℂ ((starRingEnd ℂ) ∘ f ∘ (starRingEnd ℂ)) ((starRingEnd ℂ) z) := by
      intro h
      have h2 := h.conj_conj
      rw [hinv, Complex.conj_conj] at h2
      exact hf h2
    rw [analyticOrderAt_of_not_analyticAt hg, analyticOrderAt_of_not_analyticAt hf]

/-! ### Z9 package theorems (one rewrite each, given the generic lemmas) -/

theorem analyticOrderAt_riemannZeta_conj (s : ℂ) :
    analyticOrderAt riemannZeta ((starRingEnd ℂ) s) = analyticOrderAt riemannZeta s := by
  conv_lhs => rw [← riemannZeta_comp_conj]        -- Z2 corollary, function-level
  -- occurrence audit: the conv-LHS `analyticOrderAt riemannZeta ((starRingEnd ℂ) s)`
  -- contains exactly ONE occurrence of `riemannZeta` (the point argument contains
  -- none), so the rewrite leaves exactly
  -- `analyticOrderAt ((starRingEnd ℂ) ∘ riemannZeta ∘ (starRingEnd ℂ)) ((starRingEnd ℂ) s)`.
  -- Fallback if the conv occurrence behavior differs:
  --   have h := analyticOrderAt_conj_conj riemannZeta s
  --   rwa [riemannZeta_comp_conj] at h
  exact analyticOrderAt_conj_conj riemannZeta s

theorem analyticOrderAt_riemannXi_conj (s : ℂ) :
    analyticOrderAt riemannXi ((starRingEnd ℂ) s) = analyticOrderAt riemannXi s := by
  conv_lhs => rw [← riemannXi_comp_conj]          -- Z7 corollary
  -- same single-occurrence audit and fallback as the zeta version:
  --   have h := analyticOrderAt_conj_conj riemannXi s
  --   rwa [riemannXi_comp_conj] at h
  exact analyticOrderAt_conj_conj riemannXi s
