# RH conjugation-symmetry theorem contract (S1-CONJ): draft v2

Status: **DRAFT v2 (2026-08-06) — non-built review artifact. Not Lean-checked. Independent statement review is complete; built promotion remains blocked until the preconditions carried from `TARGET_BRIDGE_CONTRACT.md` / `XI_PACKAGE_CONTRACT.md` are met and the real module passes kernel and axiom CI. The `S0-TRUST` prerequisite was satisfied by merged PR #298 (`d6e146fa`) on 2026-08-05. The internal adversarial verdict was `SOUND_WITH_FIXES` with zero S0/S1/S2 findings; the external acceptance pass synchronized both LOW proof skeletons, including the corrected F1 sign (Annex B and the dated acceptance note below).**

**Status addendum (2026-08-07).** The status paragraph above is the frozen pre-promotion text, retained verbatim; it no longer describes the current state. The built counterpart merged as PR #307 (`c277b86`) into `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Conj.lean` (the sixteen Z1-Z9 declarations, including the two `S1C-ORD` generic lemmas `AnalyticAt.conj_conj` and `analyticOrderAt_conj_conj`) after both carried preconditions landed — the target bridge in PR #299 (`288d65b`), the xi package in PR #304 (`afdae08`) — and after the head passed the full build, the no-incomplete-proof scan, ResearchOS inverse ledger coverage, and both axiom audits with every `RH-CONJ-*` row at axiom base `standard`. This document is retained as the specification artifact. Two corrections to the frozen text above: (i) "zero S0/S1/S2 findings" is a retroactive grading the review record does not carry — Annex B records four findings (F1/F2 LOW, F3/F4 INFO), none statement-level: no declaration name, binder, hypothesis, conclusion, or claim boundary was challenged, and all four were proof-skeleton or locator fixes of the class the sibling bridge and xi reviews scored S2/S3; the corrected F1 sign is preserved as history in Z3, Annex B, and the acceptance note below, and in the merged module (`Conj.lean:202-207`). (ii) Promotion does **not** close the barrier: `S1-CONJ` remains OPEN — see the Barrier-closure boundary below.

Scope: the `S1-CONJ` barrier of `MATHLIB_CAPABILITY_MAP.md` ("no named zeta/xi conjugation symmetry or multiplicity-preserving fourfold zero action"), i.e. the A/C-DAG node "conjugation symmetry for xi/zeta" and the local-order part of its follow-on "analytic-order equality … invariant under reflection/conjugation". It contains no divisor construction, no Li coefficients, no zero enumeration, no growth theorem, and no claim of progress on RH. Per the capability map, conjugation symmetry **must not be silently inferred from the `s ↦ 1−s` functional equation**; this package proves it independently, from the Dirichlet series and the identity theorem.

Pinned Mathlib: `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0), verified this session via `git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD`. Every declaration cited below was grep-verified at that exact revision this session; all `file:line` locators are from that tree (paths relative to the `Mathlib/` root of the pin).

Package prerequisites (cited as **package prerequisites**, not pinned Mathlib):

- `TARGET_BRIDGE_CONTRACT.md` P2 (`riemannZeta_zero_mem_critical_strip`) and P3 (`riemannZeta_one_sub_eq_zero_iff`) — used by Z8 only;
- `XI_PACKAGE_CONTRACT.md` X1 (`riemannXi`) — used by Z7 and Z9-xi only. Z1–Z6, Z8, Z9-zeta are independent of the xi package.

Barrier-closure boundary (stated up front, honestly): `S1-CONJ`'s exit evidence is "conjugation theorem **plus divisor invariance under `ρ ↦ 1−conj(ρ)`**". This package supplies the conjugation theorems, the fourfold zero action, and pointwise `analyticOrderAt` transport under conjugation. Divisor invariance (and order transport under `s ↦ 1−s`, hence under `ρ ↦ 1−conj ρ`) requires the `S1-MULTIPLICITY` divisor package and is **out of scope here**; `S1-CONJ` closes only when both land. `SOURCE_CONTRACTS.md` §Shared notation lists the three multiplicity-preserving symmetries `ρ ↦ 1−ρ`, `ρ ↦ conj ρ`, `ρ ↦ 1−conj ρ`; this contract delivers the multiplicity statement for the middle one and the set-level statement for all three.

## Candidate fields

- **Mechanism.** The Dirichlet series `zeta_eq_tsum_one_div_nat_cpow` has termwise-real coefficients and a real-**nonnegative** cpow base `(n : ℂ)` — including `n = 0`, whose `arg` is `0 ≠ π` by `natCast_arg`, so no term is split off — hence `conj ∘ ζ ∘ conj` agrees with `ζ` on the open half-plane `1 < re s`; both are analytic on the preconnected set `{1}ᶜ`, so the pinned identity principle `AnalyticOnNhd.eqOn_of_preconnected_of_eventuallyEq` propagates the agreement to all `s ≠ 1`; the totalized value `ζ(1) = (γ − log(4π))/2` is real, closing the last point. A second, puncture-free identity-theorem pass gives the same symmetry for the entire `completedRiemannZeta₀`, from which `completedRiemannZeta` and `riemannXi` inherit it by totalized field algebra. The zero-set, fourfold-action, and order-transport corollaries follow.
- **Expected information gain.** Supplies a repo-local theorem package for the capability that remains `NOT-FOUND-IN-SCOPE` in the pinned Mathlib inventory; supplies the `ρ ↦ conj ρ` leg of the three symmetries required by `SOURCE_CONTRACTS.md` before `SC-LI-04`'s one-sided Li criterion; partially advances `S1-CONJ` (see boundary above). No information about the truth of RH is produced.
- **Claim boundary.** Z1–Z6 are unconditional consequences of pinned Mathlib theorems. Z7 and Z9-xi additionally assume the xi package (X1); Z8 additionally assumes bridge P2/P3. Nothing touches divisors, enumeration, growth, Hadamard products, Li coefficients, or any route's research obligation. The two generic order lemmas of Z9 are genuinely missing at the pin and are registered as this contract's main obligation, with a complete assembly sketch from pinned ingredients.
- **Death condition (stop rule).** Stop or split if any proof requires weakening an exclusion, deriving conjugation from the `s ↦ 1−s` functional equation, treating a totalized exceptional value as a meromorphic value, transferring `Λ` pointwise from `ζ` across the `Gammaℝ` zero set, or introducing a competing RH proposition. A clean blocker is preferable to a false symmetry.

Proposed module preamble (name-resolution review only; the built file — `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Conj.lean`, merged as PR #307 (`c277b86`) — also imports the built bridge/xi modules where required):

```lean
import Mathlib.NumberTheory.LSeries.ZetaZeros              -- riemannZeta API (transitively RiemannZeta.lean)
import Mathlib.NumberTheory.Harmonic.ZetaAsymp             -- riemannZeta_one (totalized value at the pole)
import Mathlib.Analysis.Calculus.Deriv.Star                -- DifferentiableAt.conj_conj / differentiableAt_conj_conj_iff
import Mathlib.Analysis.Analytic.Uniqueness                -- AnalyticOnNhd.eqOn_of_preconnected_of_eventuallyEq / eq_of_eventuallyEq
import Mathlib.Analysis.Normed.Module.Connected            -- isConnected_compl_singleton_of_one_lt_rank
import Mathlib.LinearAlgebra.Complex.FiniteDimensional     -- rank_real_complex
import Mathlib.Analysis.SpecialFunctions.Complex.Arg       -- Complex.natCast_arg, arg_ofReal_of_nonneg
import Mathlib.Analysis.Analytic.Order                     -- analyticOrderAt API (Z9)
import Mathlib.Analysis.Complex.CauchyIntegral             -- DifferentiableOn.analyticAt / .analyticOnNhd
-- + import of the built bridge module providing P2, P3 (Z8)
-- + import of the built xi module providing riemannXi (Z7, Z9-xi)

open Complex
open Filter
open scoped Real ComplexConjugate Topology
```

(The `Filter` and `Topology` opens are required for the `eventually_of_mem` / `∀ᶠ` / `=ᶠ` API and the `𝓝` notation used by the Z2/Z3/Z9 skeletons; the merged module carries them at `Conj.lean:46-50`.)

Name-collision scan (grep over the pinned tree this session): **zero hits** for every proposed name — `riemannZeta_conj`, `riemannZeta_comp_conj`, `completedRiemannZeta_conj`, `completedRiemannZeta₀_conj`, `Gammaℝ_conj`, `riemannZeta_conj_eq_zero_iff`, `riemannZetaZeros_conj_preimage`, `riemannZetaZeros_conj_image`, `riemannXi_conj`, `riemannXi_comp_conj`, `riemannZeta_fourfold_zero`, `riemannZeta_fourfold_zero'`, `AnalyticAt.conj_conj`, `analyticOrderAt_conj_conj`, `analyticOrderAt_riemannZeta_conj`, `analyticOrderAt_riemannXi_conj`. The scan also confirms the map's `NOT-FOUND` row: no conjugation lemma for `riemannZeta`, `completedRiemannZeta(₀)`, `hurwitzZetaEven`, or any `LSeries` exists at the pin.

---

## 0. Exact pinned interface (quoted from the tree at the pin)

```lean
-- NumberTheory/LSeries/RiemannZeta.lean:204
theorem zeta_eq_tsum_one_div_nat_cpow {s : ℂ} (hs : 1 < re s) :
    riemannZeta s = ∑' n : ℕ, 1 / (n : ℂ) ^ s

-- RiemannZeta.lean:137, :144
theorem differentiableAt_riemannZeta {s : ℂ} (hs' : s ≠ 1) : DifferentiableAt ℂ riemannZeta s
lemma analyticOn_riemannZeta : AnalyticOnNhd ℂ riemannZeta {1}ᶜ

-- RiemannZeta.lean:84 (SIGN SOURCE OF TRUTH), :89, :152
lemma completedRiemannZeta_eq (s : ℂ) :
    completedRiemannZeta s = completedRiemannZeta₀ s - 1 / s - 1 / (1 - s)
theorem differentiable_completedZeta₀ : Differentiable ℂ completedRiemannZeta₀
lemma riemannZeta_def_of_ne_zero {s : ℂ} (hs : s ≠ 0) :
    riemannZeta s = completedRiemannZeta s / Gammaℝ s

-- Harmonic/ZetaAsymp.lean:408 (γ is the file-local notation for Real.eulerMascheroniConstant,
-- ZetaAsymp.lean:39; `log` is Complex.log under the file's `open Complex`)
lemma riemannZeta_one : riemannZeta 1 = (γ - log (4 * π)) / 2

-- Gamma/Deligne.lean:43, :45, :66 (namespace Complex)
noncomputable def Gammaℝ (s : ℂ) := π ^ (-s / 2) * Gamma (s / 2)
lemma Gammaℝ_def (s : ℂ) : Gammaℝ s = π ^ (-s / 2) * Gamma (s / 2) := rfl
lemma Gammaℝ_ne_zero_of_re_pos {s : ℂ} (hs : 0 < re s) : Gammaℝ s ≠ 0

-- Gamma/Basic.lean:355 (namespace Complex) — THE key special-function conj input
theorem Gamma_conj (s : ℂ) : Gamma (conj s) = conj (Gamma s)

-- Pow/Complex.lean:231, :234 (namespace Complex) — cpow conj with the branch-cut hypothesis
theorem conj_cpow (x : ℂ) (n : ℂ) (hx : x.arg ≠ π) : conj x ^ n = conj (x ^ conj n)
theorem cpow_conj (x : ℂ) (n : ℂ) (hx : x.arg ≠ π) : x ^ conj n = conj (conj x ^ n)

-- Complex/Arg.lean:226, :223 (namespace Complex) — discharge the branch-cut hypothesis
lemma natCast_arg {n : ℕ} : arg n = 0
theorem arg_ofReal_of_nonneg {x : ℝ} (hx : 0 ≤ x) : arg x = 0

-- Data/Complex/Basic.lean:467, :475, :482, :484 (namespace Complex)
theorem conj_re (z : ℂ) : (conj z).re = z.re
theorem conj_ofReal (r : ℝ) : conj (r : ℂ) = r
theorem conj_natCast (n : ℕ) : conj (n : ℂ) = n
theorem conj_ofNat (n : ℕ) [n.AtLeastTwo] : conj (ofNat(n) : ℂ) = ofNat(n)

-- Algebra/Star/Basic.lean:345, :364, :267
theorem starRingEnd_apply (x : R) : starRingEnd R x = star x := rfl
alias Complex.conj_conj := starRingEnd_self_apply   -- conj (conj x) = x
theorem star_eq_zero [AddMonoid R] [StarAddMonoid R] {x : R} : star x = 0 ↔ x = 0

-- Topology/Algebra/InfiniteSum/Constructions.lean:361.  NOTE: at this pin `tsum` carries a
-- SummationFilter; the plain `∑'` notation is `tsum f (unconditional _)` (InfiniteSum/Defs.lean:160)
-- and `tsum_star` is stated for an arbitrary `L`, so it applies to `∑'` by instantiation.
theorem tsum_star [T2Space α] : star (∑'[L] b, f b) = ∑'[L] b, star (f b)

-- Analysis/Calculus/Deriv/Star.lean:93, :117, :123 — THE antiholomorphic-composition input.
lemma HasDerivAt.conj_conj {f : 𝕜 → 𝕜} {f' : 𝕜} (hf : HasDerivAt f f' x) :
    HasDerivAt (conj ∘ f ∘ conj) (conj f') (conj x)
lemma DifferentiableAt.conj_conj {f : 𝕜 → 𝕜} (hf : DifferentiableAt 𝕜 f x) :
    DifferentiableAt 𝕜 (conj ∘ f ∘ conj) (conj x)
@[simp] lemma differentiableAt_conj_conj_iff {f : 𝕜 → 𝕜} :
    DifferentiableAt 𝕜 (conj ∘ f ∘ conj) x ↔ DifferentiableAt 𝕜 f (conj x)

-- Analysis/Analytic/Uniqueness.lean:223, :234 — the identity principle used
theorem AnalyticOnNhd.eqOn_of_preconnected_of_eventuallyEq {f g : E → F} {U : Set E}
    (hf : AnalyticOnNhd 𝕜 f U) (hg : AnalyticOnNhd 𝕜 g U) (hU : IsPreconnected U)
    {z₀ : E} (h₀ : z₀ ∈ U) (hfg : f =ᶠ[𝓝 z₀] g) : EqOn f g U
theorem AnalyticOnNhd.eq_of_eventuallyEq {f g : E → F} [PreconnectedSpace E]
    (hf : AnalyticOnNhd 𝕜 f univ) (hg : AnalyticOnNhd 𝕜 g univ) {z₀ : E}
    (hfg : f =ᶠ[𝓝 z₀] g) : f = g
-- (frequently-eq variant, available but NOT needed since agreement holds on an open set:
--  AnalyticOnNhd.eqOn_of_preconnected_of_frequently_eq, Analytic/IsolatedZeros.lean:238)

-- Analysis/Normed/Module/Connected.lean:125 and LinearAlgebra/Complex/FiniteDimensional.lean:35
theorem isConnected_compl_singleton_of_one_lt_rank (h : 1 < Module.rank ℝ E) (x : E) :
    IsConnected {x}ᶜ
theorem rank_real_complex : Module.rank ℝ ℂ = 2

-- Analysis/Complex/CauchyIntegral.lean:625, :631
protected theorem _root_.DifferentiableOn.analyticAt {s : Set ℂ} {f : ℂ → E} {z : ℂ}
    (hd : DifferentiableOn ℂ f s) (hz : s ∈ 𝓝 z) : AnalyticAt ℂ f z
theorem _root_.DifferentiableOn.analyticOnNhd {s : Set ℂ} {f : ℂ → E}
    (hd : DifferentiableOn ℂ f s) (hs : IsOpen s) : AnalyticOnNhd ℂ f s

-- Analysis/Analytic/Order.lean:47 (def), :64, :75, :86
noncomputable def analyticOrderAt (f : 𝕜 → E) (z₀ : 𝕜) : ℕ∞   -- junk value 0 if ¬AnalyticAt
@[simp] lemma analyticOrderAt_of_not_analyticAt (hf : ¬ AnalyticAt 𝕜 f z₀) :
    analyticOrderAt f z₀ = 0
lemma analyticOrderAt_eq_top : analyticOrderAt f z₀ = ⊤ ↔ ∀ᶠ z in 𝓝 z₀, f z = 0
lemma AnalyticAt.analyticOrderAt_eq_natCast (hf : AnalyticAt 𝕜 f z₀) :
    analyticOrderAt f z₀ = n ↔
      ∃ (g : 𝕜 → E), AnalyticAt 𝕜 g z₀ ∧ g z₀ ≠ 0 ∧ ∀ᶠ z in 𝓝 z₀, f z = (z - z₀) ^ n • g z
```

**In-tree template evidence (decisive for elaboration risk):** the pinned tree itself executes the exact identity-theorem idiom this contract needs, at `NumberTheory/LSeries/DirichletContinuation.lean:124-144` (`isConnected_compl_singleton_of_one_lt_rank (rank_real_complex ▸ Nat.one_lt_ofNat)` on `({1}ᶜ : Set ℂ)`, base point `2`, eventual equality from `(continuous_re.isOpen_preimage _ isOpen_Ioi).mem_nhds (by simp : 1 < (2 : ℂ).re)`), and the univ-version `AnalyticOnNhd.eq_of_eventuallyEq` with the `PreconnectedSpace ℂ` instance resolving at `NumberTheory/LSeries/ZMod.lean:526`. Both uses compile at the pin, so instance availability and signature shapes are not speculative.

## Strategy decision (task-mandated evaluation)

- **Route (b) — pre-existing hurwitz/L-series conj lemma: UNAVAILABLE.** Grep over the pinned tree finds conjugation facts only at the theta-kernel level (`jacobiTheta₂''_conj`, `HurwitzZetaOdd.lean:64`; kernel-realness rewrites at `HurwitzZetaEven.lean:79/94`), consumed internally to prove the kernels are real-valued and **not** exposed as any `hurwitzZetaEven`/`completedHurwitzZetaEven`/`LSeries`/zeta conjugation statement. No shortcut exists at the pin.
- **Route (a) — Schwarz-reflection via the identity theorem: ADOPTED.** All four ingredients are pinned theorems: antiholomorphic composition (`DifferentiableAt.conj_conj` / `differentiableAt_conj_conj_iff`, Deriv/Star.lean:117/123 — exactly the lemma the task asked to hunt for), Dirichlet-series agreement on the **open** half-plane `1 < re s` (so the *eventuallyEq* identity principle applies; the weaker frequently-eq variant is not needed), preconnectedness of `{1}ᶜ` (Connected.lean:125 + rank_real_complex), and the identity principle itself (Uniqueness.lean:223).
- **Strongest true statement: GLOBAL, for all `s : ℂ`, with no hypotheses.** At `s = 1` both sides are conj-fixed: `conj 1 = 1` and `riemannZeta_one` gives `ζ(1) = ((γ : ℂ) − Complex.log (4π))/2`, which is the coercion of the real number `(γ − Real.log(4π))/2` (via `Complex.ofReal_log`, Log.lean:71 — the pinned proof of `riemannZeta_one_ne_zero` at ZetaAsymp.lean:431-435 performs this exact cast walk). Since `conj s = 1 ↔ s = 1`, no other point interacts with the puncture. Hence the totalization does **not** force any hypothesis; Z2 below is stated for all `s`.
- **Order of C2 (decided): ζ first, then Λ₀ by a second identity-theorem pass, then Λ by totalized algebra.** The alternative — transporting `Λ = Gammaℝ · ζ` pointwise from Z2 — **fails** on the `Gammaℝ` zero set `−2ℕ ∪ {0}` (where `ζ w = Λ w / Gammaℝ w = 0` holds for every value of `Λ w`, so `Λ` is not recoverable from `ζ` there) and at the totalized points `0, 1`. The Λ₀ pass runs on all of ℂ with no punctures (Λ₀ is entire), so it is strictly cleaner; Λ then follows from `completedRiemannZeta_eq` **totally** (Lean's `1/0 = 0` and `conj 0 = 0` make the pole-correction terms conj-equivariant even at `s = 0, 1`).

---

## Z1. Gammaℝ conjugation (helper; also a natural Mathlib upstream)

### Statement

```lean
theorem Gammaℝ_conj (s : ℂ) : Gammaℝ ((starRingEnd ℂ) s) = (starRingEnd ℂ) (Gammaℝ s)
```

Unconditional: both sides are total, and every factor is conj-equivariant.

### Proof skeleton

```lean
theorem Gammaℝ_conj (s : ℂ) : Gammaℝ ((starRingEnd ℂ) s) = (starRingEnd ℂ) (Gammaℝ s) := by
  rw [Gammaℝ_def, Gammaℝ_def, map_mul]
  congr 1
  · -- π ^ (-(conj s) / 2) = conj (π ^ (-s / 2)) : real-positive base, off the branch cut
    have harg : (↑π : ℂ).arg ≠ π :=
      by rw [Complex.arg_ofReal_of_nonneg Real.pi_pos.le]; exact (Real.pi_ne_zero).symm
    have h : -((starRingEnd ℂ) s) / 2 = (starRingEnd ℂ) (-s / 2) := by
      rw [map_div₀, map_neg, Complex.conj_ofNat]                        -- OBLIG S1C-6
    rw [h, Complex.cpow_conj _ _ harg, Complex.conj_ofReal]
  · -- Gamma (conj s / 2) = conj (Gamma (s / 2))
    have h : (starRingEnd ℂ) s / 2 = (starRingEnd ℂ) (s / 2) := by
      rw [map_div₀, Complex.conj_ofNat]
    rw [h, Complex.Gamma_conj]
```

### Pinned dependencies (Z1)

`Complex.Gammaℝ_def` (Gamma/Deligne.lean:45), `Complex.Gamma_conj` (Gamma/Basic.lean:355), `Complex.cpow_conj` (Pow/Complex.lean:234), `Complex.arg_ofReal_of_nonneg` (Complex/Arg.lean:223), `Real.pi_pos` (Trigonometric/Basic.lean:157), `Real.pi_ne_zero` (Trigonometric/Basic.lean:165), `Complex.conj_ofReal` (Data/Complex/Basic.lean:475), `Complex.conj_ofNat` (:484), `map_div₀` (Algebra/GroupWithZero/Units/Lemmas.lean:117), `map_mul`/`map_neg` (core RingHom glue, bridge-precedent no-locator).

### Obligations (Z1)

- **OBLIGATION S1C-6 (LOW):** the conj-push through `-·/2` and the branch-cut discharge `(↑π).arg = 0 ≠ π` (`Ne.symm`-direction bookkeeping); the exact rewrite chain is schematic. Note `cpow_conj`'s statement produces `conj (conj x ^ n)`; with `conj ↑π = ↑π` (`conj_ofReal`) the shape matches after one rewrite — same class as bridge P1-d.

---

## Z2. C1: global zeta conjugation symmetry

### Statement

```lean
theorem riemannZeta_conj (s : ℂ) :
    riemannZeta ((starRingEnd ℂ) s) = (starRingEnd ℂ) (riemannZeta s)
```

**Design note (strongest true form).** Global, hypothesis-free. The two ingredients that make the totalized points harmless: (i) `conj 1 = 1` and `ζ(1)` is real (`riemannZeta_one` + `ofReal_log`), so the `s = 1` instance is a statement about one real number; (ii) for `s ≠ 1` the identity theorem applies on `{1}ᶜ`, and the agreement set is the **open** half-plane `1 < re`, since for *every* such `s` (not only real `s`) the Dirichlet series conjugates termwise: `re (conj s) = re s` (`conj_re`) keeps `conj s` in the summability region, and `(n : ℂ) ^ conj s = conj ((n:ℂ) ^ s)` holds for every `n : ℕ` **including `n = 0`** because `natCast_arg` gives `arg = 0 ≠ π` even at `0` (both sides are governed by the same `cpow` zero-base convention, so no term must be split off).

### Proof skeleton

```lean
theorem riemannZeta_conj (s : ℂ) :
    riemannZeta ((starRingEnd ℂ) s) = (starRingEnd ℂ) (riemannZeta s) := by
  rcases eq_or_ne s 1 with rfl | hs1
  · -- totalized point: conj 1 = 1, and ζ(1) is the coercion of a real number.
    rw [map_one]
    -- goal: riemannZeta 1 = conj (riemannZeta 1)
    have hre : riemannZeta 1 =
        (((Real.eulerMascheroniConstant - Real.log (4 * π)) / 2 : ℝ) : ℂ) := by
      simp only [riemannZeta_one,
        ofReal_log (by positivity : (0 : ℝ) ≤ 4 * π), push_cast]
    rw [hre, Complex.conj_ofReal]
  · -- identity theorem on {1}ᶜ; template: DirichletContinuation.lean:124-144
    have hpc : IsPreconnected ({1}ᶜ : Set ℂ) :=
      (isConnected_compl_singleton_of_one_lt_rank
        (rank_real_complex ▸ Nat.one_lt_ofNat) 1).isPreconnected
    have h2 : (2 : ℂ) ∈ ({1}ᶜ : Set ℂ) := by simp
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
    -- agreement on the OPEN half-plane 1 < re, an 𝓝 2 neighborhood
    have hfg : ((starRingEnd ℂ) ∘ riemannZeta ∘ (starRingEnd ℂ)) =ᶠ[𝓝 2]
        riemannZeta := by
      refine eventually_of_mem
        ((Complex.continuous_re.isOpen_preimage _ isOpen_Ioi).mem_nhds
          (by simp : 1 < (2 : ℂ).re)) (fun z (hz : 1 < z.re) => ?_)
      have hz' : 1 < ((starRingEnd ℂ) z).re := by rwa [Complex.conj_re]
      simp only [Function.comp_apply]
      rw [zeta_eq_tsum_one_div_nat_cpow hz', zeta_eq_tsum_one_div_nat_cpow hz,
        starRingEnd_apply, tsum_star]
      refine tsum_congr fun n => ?_
      have harg : ((n : ℂ)).arg ≠ π := by
        rw [Complex.natCast_arg]
        exact Real.pi_ne_zero.symm
      rw [← starRingEnd_apply, map_div₀, map_one, Complex.cpow_conj (n : ℂ) z harg,
        Complex.conj_conj, Complex.conj_natCast]
    have hEq := AnalyticOnNhd.eqOn_of_preconnected_of_eventuallyEq (𝕜 := ℂ)
      hg analyticOn_riemannZeta hpc h2 hfg
    -- at s : conj (ζ (conj s)) = ζ s ; apply conj to both sides
    have h := hEq (Set.mem_compl_singleton_iff.mpr hs1)
    have h' := congrArg (starRingEnd ℂ) h
    simp only [Function.comp_apply, Complex.conj_conj] at h'
    exact h'
```

Function-level corollary (glue for Z9):

```lean
theorem riemannZeta_comp_conj :
    (starRingEnd ℂ) ∘ riemannZeta ∘ (starRingEnd ℂ) = riemannZeta :=
  funext fun s => by
    simp only [Function.comp_apply]
    rw [riemannZeta_conj, Complex.conj_conj]
```

### Pinned dependencies (Z2)

`zeta_eq_tsum_one_div_nat_cpow` (RiemannZeta.lean:204), `differentiableAt_riemannZeta` (:137), `analyticOn_riemannZeta` (:144), `riemannZeta_one` (ZetaAsymp.lean:408), `Complex.ofReal_log` (Complex/Log.lean:71), `AnalyticOnNhd.eqOn_of_preconnected_of_eventuallyEq` (Analytic/Uniqueness.lean:223), `isConnected_compl_singleton_of_one_lt_rank` (Normed/Module/Connected.lean:125), `rank_real_complex` (LinearAlgebra/Complex/FiniteDimensional.lean:35), `isOpen_compl_singleton` (Topology/Separation/Basic.lean:354), `DifferentiableOn.analyticOnNhd` (Complex/CauchyIntegral.lean:631), `differentiableAt_conj_conj_iff` (Calculus/Deriv/Star.lean:123), `tsum_star` (Topology/Algebra/InfiniteSum/Constructions.lean:361), `∑'`-notation = `unconditional` SummationFilter (InfiniteSum/Defs.lean:160), `Complex.cpow_conj` (Pow/Complex.lean:234), `Complex.natCast_arg` (Complex/Arg.lean:226), `Real.pi_ne_zero` (Trigonometric/Basic.lean:165), `Complex.conj_re` (Data/Complex/Basic.lean:467), `Complex.conj_natCast` (:482), `Complex.conj_conj` (Algebra/Star/Basic.lean:364), `starRingEnd_apply` (:345), `map_div₀` (GroupWithZero/Units/Lemmas.lean:117), `Complex.continuous_re` (Analysis/Complex/Basic.lean:153), `isOpen_Ioi` (Topology/Order/OrderClosed.lean:216), `Continuous.isOpen_preimage` (structure field, Topology/Defs/Basic.lean:154), `IsOpen.mem_nhds` (Topology/Neighborhoods.lean:90), `eventually_of_mem` (Order/Filter/Basic.lean:641), `Set.mem_compl_singleton_iff` (Order/BooleanAlgebra/Set.lean:195), `Nat.one_lt_ofNat`/`map_one` (core glue).

### Obligations (Z2)

- **OBLIGATION S1C-1 (LOW):** the termwise conj computation — `map_div₀`/`map_one` shape, the `cpow_conj` triple-conj unwind in the `calc`, and the `n = 0` degenerate term (covered uniformly by `natCast_arg`, no case split expected; verify in build).
- **OBLIGATION S1C-2 (LOW):** `tsum_star` is stated with `star` and a general SummationFilter `L`; the skeleton's `starRingEnd_apply`-mediated rewrite between `conj` and `star`, and the instantiation at `unconditional`, are schematic.
- **OBLIGATION S1C-3 (LOW):** realness of `ζ(1)`: the `ofReal_log`/`push_cast`/`conj_ofReal` cast walk (the pinned tree performs the identical walk at ZetaAsymp.lean:434-435; mirror it).
- **OBLIGATION S1C-4 (LOW):** the `𝓝 2` membership glue — character-identical to the pinned template DirichletContinuation.lean:143.
- No analytic obligation: the identity principle, the half-plane series, antiholomorphic differentiability, and preconnectedness are all quoted pinned theorems.

---

## Z3. C2: conjugation symmetry of the entire completion `Λ₀`

### Statement

```lean
theorem completedRiemannZeta₀_conj (s : ℂ) :
    completedRiemannZeta₀ ((starRingEnd ℂ) s) = (starRingEnd ℂ) (completedRiemannZeta₀ s)
```

Global, hypothesis-free (`Λ₀` is entire; nothing is totalized).

### Proof skeleton

```lean
theorem completedRiemannZeta₀_conj (s : ℂ) :
    completedRiemannZeta₀ ((starRingEnd ℂ) s) = (starRingEnd ℂ) (completedRiemannZeta₀ s) := by
  -- identity theorem on ALL of ℂ (no puncture): PreconnectedSpace ℂ instance is
  -- witnessed in-tree at ZMod.lean:526
  have hg : AnalyticOnNhd ℂ (conj ∘ completedRiemannZeta₀ ∘ conj) Set.univ := by
    refine DifferentiableOn.analyticOnNhd (fun z _ => ?_) isOpen_univ
    exact (differentiableAt_conj_conj_iff.mpr
      (differentiable_completedZeta₀ _)).differentiableWithinAt
  have hf : AnalyticOnNhd ℂ completedRiemannZeta₀ Set.univ :=
    differentiable_completedZeta₀.differentiableOn.analyticOnNhd isOpen_univ
  have hfg : (conj ∘ completedRiemannZeta₀ ∘ conj) =ᶠ[𝓝 2] completedRiemannZeta₀ := by
    refine eventually_of_mem
      ((Complex.continuous_re.isOpen_preimage _ isOpen_Ioi).mem_nhds
        (by norm_num : (1:ℝ) < (2:ℂ).re)) (fun z (hz : 1 < z.re) => ?_)
    -- On re > 1 : Λ₀ w = Gammaℝ w * ζ w + 1/w + 1/(1-w)                 (OBLIG S1C-5)
    have key : ∀ w : ℂ, 1 < w.re →
        completedRiemannZeta₀ w = Gammaℝ w * riemannZeta w + 1 / w + 1 / (1 - w) := by
      intro w hw
      have hw0 : w ≠ 0 := fun e => by rw [e, Complex.zero_re] at hw; linarith
      have hG : Gammaℝ w ≠ 0 := Complex.Gammaℝ_ne_zero_of_re_pos (by linarith)
      have hΛ : completedRiemannZeta w = Gammaℝ w * riemannZeta w := by
        rw [riemannZeta_def_of_ne_zero hw0, mul_div_cancel₀ _ hG]
      have h := completedRiemannZeta_eq w      -- Λ = Λ₀ − 1/w − 1/(1−w)  (the THEOREM)
      linear_combination hΛ - h  -- review fix F1 (sign)
    have hz' : 1 < ((starRingEnd ℂ) z).re := by rwa [Complex.conj_re]
    simp only [Function.comp_apply]
    rw [key _ hz', key _ hz]
    -- push conj through: Gammaℝ (conj z) = conj (Gammaℝ z) [Z1], ζ (conj z) = conj (ζ z) [Z2],
    -- conj of 1/w and 1/(1−w) via map_div₀ / map_sub / map_one
    rw [Gammaℝ_conj, riemannZeta_conj]
    simp only [map_add, map_mul, map_div₀, map_one, map_sub, Complex.conj_conj]
  have h := congrFun (hg.eq_of_eventuallyEq hf hfg) s   -- conj (Λ₀ (conj s)) = Λ₀ s
  simpa [Complex.conj_conj, Function.comp_apply] using congrArg (starRingEnd ℂ) h
```

**Anti-pitfall note.** `key` is asserted only on the open half-plane `1 < re`, where `w ≠ 0`, `Gammaℝ w ≠ 0`, and `riemannZeta_def_of_ne_zero`'s hypothesis all hold with proofs. The pointwise identity `Λ = Gammaℝ · ζ` is **never** used outside that region (it is false as a transfer device on `−2ℕ ∪ {0}`, where `Gammaℝ = 0` erases `Λ`). The sign chain is from `completedRiemannZeta_eq` the theorem (RiemannZeta.lean:84), never the conflicting module comment.

### Pinned dependencies (Z3)

Z1, Z2; `completedRiemannZeta_eq` (RiemannZeta.lean:84), `differentiable_completedZeta₀` (:89), `riemannZeta_def_of_ne_zero` (:152), `AnalyticOnNhd.eq_of_eventuallyEq` (Analytic/Uniqueness.lean:234; `PreconnectedSpace ℂ` instance usage witnessed at NumberTheory/LSeries/ZMod.lean:526), `Complex.Gammaℝ_ne_zero_of_re_pos` (Gamma/Deligne.lean:66), `mul_div_cancel₀` (GroupWithZero/Units/Basic.lean:458), `DifferentiableOn.analyticOnNhd` (CauchyIntegral.lean:631), `differentiableAt_conj_conj_iff` (Deriv/Star.lean:123), `isOpen_univ` (Topology/Defs/Basic.lean:94), `Complex.zero_re` (Data/Complex/Basic.lean:125), `Complex.conj_re` (:467), plus the Z2 filter/topology glue set.

### Obligations (Z3)

- **OBLIGATION S1C-5 (MEDIUM):** the `key` rearrangement (`linear_combination` coefficient over `completedRiemannZeta_eq` + `hΛ`) and the closing `simp only` conj-push must produce syntactically equal sides; same class as xi X5-a (pure field/ring-hom algebra, version-sensitive normal form, no analytic content).
- **OBLIGATION S1C-7 (LOW):** `PreconnectedSpace ℂ` instance resolution for `eq_of_eventuallyEq` (witnessed in-tree; fallback: `eqOn_of_preconnected_of_eventuallyEq` on `U := Set.univ` with the `{1}ᶜ`-style connectedness lemma applied to any point, or `convex_univ`-based preconnectedness).

---

## Z4. C2: conjugation symmetry of `Λ` (totalized, global)

### Statement

```lean
theorem completedRiemannZeta_conj (s : ℂ) :
    completedRiemannZeta ((starRingEnd ℂ) s) = (starRingEnd ℂ) (completedRiemannZeta s)
```

Global including the totalized points `s = 0, 1`: Lean's total division gives `1/0 = 0` and `conj 0 = 0`, so `map_div₀` is valid with **no** nonvanishing hypothesis — the exceptional values transport by construction, not by meromorphic reasoning.

### Proof skeleton

```lean
theorem completedRiemannZeta_conj (s : ℂ) :
    completedRiemannZeta ((starRingEnd ℂ) s) = (starRingEnd ℂ) (completedRiemannZeta s) := by
  rw [completedRiemannZeta_eq, completedRiemannZeta_eq s, completedRiemannZeta₀_conj]
  simp only [map_sub, map_div₀, map_one]
  -- residual: conj-image of (1 - s) vs 1 - conj s : map_sub + map_one, then rfl/ring_nf
```

### Pinned dependencies (Z4)

Z3; `completedRiemannZeta_eq` (RiemannZeta.lean:84), `map_div₀` (GroupWithZero/Units/Lemmas.lean:117), `map_sub`/`map_one` (core glue).

### Obligations (Z4)

- **OBLIGATION S1C-8 (LOW):** the final `simp only` set closing `conj (1 − s) = 1 − conj s` inside the two pole-correction terms; trivial ring-hom bookkeeping.

---

## Z5. C2: membership-level zero symmetry

### Statement

```lean
theorem riemannZeta_conj_eq_zero_iff {s : ℂ} :
    riemannZeta ((starRingEnd ℂ) s) = 0 ↔ riemannZeta s = 0
```

### Proof skeleton

```lean
theorem riemannZeta_conj_eq_zero_iff {s : ℂ} :
    riemannZeta ((starRingEnd ℂ) s) = 0 ↔ riemannZeta s = 0 := by
  rw [riemannZeta_conj, starRingEnd_apply, star_eq_zero]
```

### Pinned dependencies (Z5)

Z2; `starRingEnd_apply` (Algebra/Star/Basic.lean:345), `star_eq_zero` (:267).

### Obligations (Z5)

None.

---

## Z6. C2: zero-set invariance as set equalities

### Statements

```lean
theorem riemannZetaZeros_conj_preimage :
    (starRingEnd ℂ) ⁻¹' riemannZetaZeros = riemannZetaZeros

theorem riemannZetaZeros_conj_image :
    (starRingEnd ℂ) '' riemannZetaZeros = riemannZetaZeros
```

`riemannZetaZeros` is used **as a set only** (ZetaZeros.lean:33; membership-only, no multiplicity — capability-map `S1-MULTIPLICITY` boundary respected; multiplicity transport is Z9, divisor invariance is out of scope).

### Proof skeletons

```lean
theorem riemannZetaZeros_conj_preimage :
    (starRingEnd ℂ) ⁻¹' riemannZetaZeros = riemannZetaZeros := by
  ext z
  simp only [Set.mem_preimage, mem_riemannZetaZeros]
  exact riemannZeta_conj_eq_zero_iff

theorem riemannZetaZeros_conj_image :
    (starRingEnd ℂ) '' riemannZetaZeros = riemannZetaZeros := by
  rw [Set.image_eq_preimage_of_inverse
      (fun z => Complex.conj_conj z) (fun z => Complex.conj_conj z)]
  exact riemannZetaZeros_conj_preimage
```

### Pinned dependencies (Z6)

Z5; `riemannZetaZeros` (ZetaZeros.lean:33), `mem_riemannZetaZeros` (:35, `.rfl`), `Set.mem_preimage` (core), `Set.image_eq_preimage_of_inverse` (Data/Set/Image.lean:346), `Complex.conj_conj` (Algebra/Star/Basic.lean:364).

### Obligations (Z6)

- **OBLIGATION S1C-9 (LOW):** `LeftInverse`/`RightInverse` bundling shapes for `image_eq_preimage_of_inverse` (both are `conj_conj`); schematic.

---

## Z7. C2: xi conjugation symmetry (xi-package prerequisite)

### Statement

```lean
theorem riemannXi_conj (s : ℂ) :
    riemannXi ((starRingEnd ℂ) s) = (starRingEnd ℂ) (riemannXi s)
```

`riemannXi` is the X1 definition `(1 + s*(s-1)*completedRiemannZeta₀ s)/2` (XI_PACKAGE_CONTRACT.md; **not** a pinned declaration). The polynomial factor's conj-compatibility is trivial ring-hom algebra; the analytic content is exactly Z3 (`Λ₀` conj symmetry), as the task specifies.

### Proof skeleton

```lean
theorem riemannXi_conj (s : ℂ) :
    riemannXi ((starRingEnd ℂ) s) = (starRingEnd ℂ) (riemannXi s) := by
  unfold riemannXi
  rw [completedRiemannZeta₀_conj]
  simp only [map_div₀, map_add, map_mul, map_sub, map_one, Complex.conj_ofNat]
```

Function-level corollary (glue for Z9-xi): `riemannXi_comp_conj : (starRingEnd ℂ) ∘ riemannXi ∘ (starRingEnd ℂ) = riemannXi` (funext + Z7 + `conj_conj`).

### Pinned dependencies (Z7)

Z3; **xi-package prerequisite** `riemannXi` (XI_PACKAGE_CONTRACT.md X1 — not pinned Mathlib); `Complex.conj_ofNat` (Data/Complex/Basic.lean:484), `map_*` core glue.

### Obligations (Z7)

- **OBLIGATION S1C-10 (LOW):** the exact `simp only` normal form aligning the two sides after the Z3 rewrite (`2` under `conj`, associativity); `ring_nf` fallback with `conj (Λ₀ s)` as atom.

---

## Z8. C3: the fourfold zero action

### Statements

Primary (strip-hypothesis form; the exclusions are exactly bridge P3's):

```lean
theorem riemannZeta_fourfold_zero {ρ : ℂ} (h0 : 0 < ρ.re) (h1 : ρ.re < 1)
    (hz : riemannZeta ρ = 0) :
    riemannZeta (1 - ρ) = 0 ∧ riemannZeta ((starRingEnd ℂ) ρ) = 0 ∧
      riemannZeta (1 - (starRingEnd ℂ) ρ) = 0
```

Corollary in the exact bridge-package exclusion form (trivial-zero exclusion **verbatim** `¬∃ n : ℕ, s = -2 * (n + 1)`; no `ρ ≠ 1` binder needed — bridge P2 needs none):

```lean
theorem riemannZeta_fourfold_zero' {ρ : ℂ} (hz : riemannZeta ρ = 0)
    (htriv : ¬∃ n : ℕ, ρ = -2 * (n + 1)) :
    riemannZeta (1 - ρ) = 0 ∧ riemannZeta ((starRingEnd ℂ) ρ) = 0 ∧
      riemannZeta (1 - (starRingEnd ℂ) ρ) = 0
```

Together with `hz` itself these give all four of `ρ, 1−ρ, conj ρ, 1−conj ρ` as zeros — the set-level fourfold action over the three `SOURCE_CONTRACTS.md` symmetries. (All four stay in the open strip: `re (conj ρ) = re ρ` and `re (1−ρ) = 1 − re ρ`.)

### Proof skeletons

```lean
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
```

### Pinned dependencies (Z8)

Z5; **bridge prerequisites** `riemannZeta_one_sub_eq_zero_iff` (TARGET_BRIDGE_CONTRACT.md P3) and `riemannZeta_zero_mem_critical_strip` (P2) — not pinned Mathlib; `Complex.conj_re` (Data/Complex/Basic.lean:467).

### Obligations (Z8)

None beyond the bridge landing (P2/P3 kernel-checked first — a package-ordering constraint, not a proof risk; satisfied: the bridge merged as PR #299 (`288d65b`) and the promotion PR #307 (`c277b86`) imports it).

---

## Z9. C4: analytic-order transport under conjugation (the hard one)

### Investigation result (honest)

The pin has **no** order-under-conjugation or order-under-antiholomorphic-composition lemma of any kind: `Analysis/Analytic/Order.lean` (studied in full) contains congruence (:175), products (:497), and the characterizations quoted in §0, but nothing touching `conj`/`star`; the only analytic-conj composition result anywhere in the tree is harmonicity (`AnalyticAt.harmonicAt_conj`, InnerProductSpace/Harmonic/Constructions.lean:65), which is useless here. There is also **no** `AnalyticAt.conj_conj` (only the `DifferentiableAt` version, Deriv/Star.lean:117). Both gaps are assemblable from pinned ingredients — the characterization API (`analyticOrderAt_eq_top` :75, `AnalyticAt.analyticOrderAt_eq_natCast` :86, `analyticOrderAt_of_not_analyticAt` :64) is exactly the power-series-free interface the assembly needs. Accordingly this is registered as the contract's **main obligation S1C-ORD** (not DEFERRED): all ingredients are pinned, no analytic gap, but two new generic lemmas must be built.

### Statements

Generic lemmas (**OBLIGATION S1C-ORD**; natural Mathlib upstreams):

```lean
-- (i) analytic transport of conj ∘ f ∘ conj  (ℂ-specific; missing at the pin)
theorem AnalyticAt.conj_conj {f : ℂ → ℂ} {x : ℂ} (hf : AnalyticAt ℂ f x) :
    AnalyticAt ℂ ((starRingEnd ℂ) ∘ f ∘ (starRingEnd ℂ)) ((starRingEnd ℂ) x)

-- (ii) order transport (missing at the pin)
theorem analyticOrderAt_conj_conj (f : ℂ → ℂ) (z : ℂ) :
    analyticOrderAt ((starRingEnd ℂ) ∘ f ∘ (starRingEnd ℂ)) ((starRingEnd ℂ) z)
      = analyticOrderAt f z
```

Package theorems (global, hypothesis-free — the junk-value-0 convention at non-analytic points is conj-symmetric, so even `s = 1` needs no exclusion):

```lean
theorem analyticOrderAt_riemannZeta_conj (s : ℂ) :
    analyticOrderAt riemannZeta ((starRingEnd ℂ) s) = analyticOrderAt riemannZeta s

-- xi version (xi-package prerequisite)
theorem analyticOrderAt_riemannXi_conj (s : ℂ) :
    analyticOrderAt riemannXi ((starRingEnd ℂ) s) = analyticOrderAt riemannXi s
```

### Proof skeletons (package theorems — one rewrite each, given the generic lemmas)

```lean
theorem analyticOrderAt_riemannZeta_conj (s : ℂ) :
    analyticOrderAt riemannZeta ((starRingEnd ℂ) s) = analyticOrderAt riemannZeta s := by
  conv_lhs => rw [← riemannZeta_comp_conj]        -- Z2 corollary, function-level
  exact analyticOrderAt_conj_conj riemannZeta s

theorem analyticOrderAt_riemannXi_conj (s : ℂ) :
    analyticOrderAt riemannXi ((starRingEnd ℂ) s) = analyticOrderAt riemannXi s := by
  conv_lhs => rw [← riemannXi_comp_conj]          -- Z7 corollary
  exact analyticOrderAt_conj_conj riemannXi s
```

### Assembly sketch for S1C-ORD (every named ingredient pinned)

**(i) `AnalyticAt.conj_conj`.** From `hf : AnalyticAt ℂ f x`: `hf.eventually_analyticAt` (ChangeOrigin.lean:378) gives `∀ᶠ y in 𝓝 x, AnalyticAt ℂ f y`; `eventually_nhds_iff` (Topology/Neighborhoods.lean:68) extracts an open `U ∋ x` on which `f` is analytic, hence `DifferentiableOn ℂ f U` via `AnalyticAt.differentiableAt` (Calculus/FDeriv/Analytic.lean:126). Set `V := (starRingEnd ℂ) ⁻¹' U`: open by `Complex.continuous_conj` (Analysis/Complex/Basic.lean:243) + `Continuous.isOpen_preimage` (Topology/Defs/Basic.lean:154), and `conj x ∈ V` by `conj_conj`. On `V`, `differentiableAt_conj_conj_iff.mpr` (Deriv/Star.lean:123) gives `DifferentiableAt ℂ (conj ∘ f ∘ conj)` pointwise; conclude with `DifferentiableOn.analyticAt` (CauchyIntegral.lean:625) at `conj x`. (~10-15 lines; same cost class as xi X11-G.)

**(ii) `analyticOrderAt_conj_conj`.** Write `g := conj ∘ f ∘ conj` and note the involution `conj ∘ g ∘ conj = f` (funext + `conj_conj`). Split on `AnalyticAt ℂ f z`:

1. `¬AnalyticAt ℂ f z`: then `¬AnalyticAt ℂ g (conj z)` — otherwise (i) applied to `g` at `conj z` plus the involution and `conj_conj` would rebuild `AnalyticAt ℂ f z`. Both sides are the junk value `0` by `analyticOrderAt_of_not_analyticAt` (Order.lean:64).
2. `AnalyticAt`, order `= ⊤`: `analyticOrderAt_eq_top` (Order.lean:75) both sides; transport `∀ᶠ w in 𝓝 z, f w = 0` to `∀ᶠ w in 𝓝 (conj z), g w = 0` by the open-set extraction of `eventually_nhds_iff` + `continuous_conj`-preimage (as in (i)) + `star_eq_zero` (Star/Basic.lean:267); the converse direction by the involution.
3. `AnalyticAt`, order `= ↑n`: `AnalyticAt.analyticOrderAt_eq_natCast` (Order.lean:86) both sides; witness transport `w ↦ conj (w (conj ·))`: if `f w = (w − z)^n • h w` eventually near `z` with `h` analytic, `h z ≠ 0`, then eventually near `conj z`, `g w' = conj(f (conj w')) = conj((conj w' − z)^n • h (conj w')) = (w' − conj z)^n • (conj ∘ h ∘ conj) w'` — by `map_mul`/`map_pow`/`map_sub` (`smul_eq_mul` in ℂ, core) and `conj_conj`; `conj ∘ h ∘ conj` is analytic at `conj z` by (i) and nonvanishing there by `star_eq_zero`; the eventual set transports as in step 2. Case exhaustion over `ℕ∞` via `cases h : analyticOrderAt f z` after the analyticity split.

**Estimated cost:** 40-60 lines total for both generic lemmas. **No analytic gap** — every input is a quoted pinned theorem; the risk is elaboration bookkeeping (filter/open-set extraction, `Function.comp` vs lambda shapes), the same class as xi X11-b.

### Pinned dependencies (Z9)

Z2 (`riemannZeta_comp_conj`), Z7 (`riemannXi_comp_conj`, xi-conditional); `analyticOrderAt` (Analytic/Order.lean:47), `analyticOrderAt_of_not_analyticAt` (:64), `analyticOrderAt_eq_top` (:75), `AnalyticAt.analyticOrderAt_eq_natCast` (:86), `AnalyticAt.eventually_analyticAt` (Analytic/ChangeOrigin.lean:378), `AnalyticAt.differentiableAt` (Calculus/FDeriv/Analytic.lean:126), `eventually_nhds_iff` (Topology/Neighborhoods.lean:68), `Complex.continuous_conj` (Analysis/Complex/Basic.lean:243), `Continuous.isOpen_preimage` (Topology/Defs/Basic.lean:154), `DifferentiableOn.analyticAt` (CauchyIntegral.lean:625), `differentiableAt_conj_conj_iff` (Deriv/Star.lean:123), `star_eq_zero` (Star/Basic.lean:267), `Complex.conj_conj` (:364), `smul_eq_mul`/`map_pow`/`map_sub` (core glue).

### Obligations (Z9)

- **OBLIGATION S1C-ORD (MEDIUM-HIGH — the contract's main obligation):** the two generic lemmas above do not exist at the pin and must be assembled per the sketch. Fallback if assembly stalls: mark `analyticOrderAt_riemannXi_conj`/`_riemannZeta_conj` as split-off to the divisor package **with** this sketch attached — but no mathematical blocker was found, so the default plan is to build them in this package. **Discharged (2026-08-07 note):** both generic lemmas were built in this package and kernel-checked in merged PR #307 (`c277b86`), at `Conj.lean:336` (`AnalyticAt.conj_conj`) and `Conj.lean:357` (`analyticOrderAt_conj_conj`); no split-off was needed.

---

## Pinned API dependencies table

All paths relative to the pinned Mathlib tree; all line numbers grep-verified this session at `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`.

| declaration | file:line | used in |
|---|---|---|
| `riemannZeta` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:119 | all |
| `zeta_eq_tsum_one_div_nat_cpow` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:204 | Z2 |
| `differentiableAt_riemannZeta` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:137 | Z2 |
| `analyticOn_riemannZeta` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:144 | Z2 |
| `completedRiemannZeta_eq` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:84 | Z3, Z4 (sign source of truth) |
| `differentiable_completedZeta₀` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:89 | Z3 |
| `riemannZeta_def_of_ne_zero` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:152 | Z3 (only under proved `≠ 0`) |
| `riemannZeta_one` | Mathlib/NumberTheory/Harmonic/ZetaAsymp.lean:408 | Z2 (`s = 1` branch) |
| `riemannZetaZeros` / `mem_riemannZetaZeros` | Mathlib/NumberTheory/LSeries/ZetaZeros.lean:33 / :35 | Z6 |
| `Complex.Gammaℝ_def` | Mathlib/Analysis/SpecialFunctions/Gamma/Deligne.lean:45 | Z1 |
| `Complex.Gammaℝ_ne_zero_of_re_pos` | Mathlib/Analysis/SpecialFunctions/Gamma/Deligne.lean:66 | Z3 |
| `Complex.Gamma_conj` | Mathlib/Analysis/SpecialFunctions/Gamma/Basic.lean:355 | Z1 |
| `Complex.conj_cpow` | Mathlib/Analysis/SpecialFunctions/Pow/Complex.lean:231 | (available alternative) |
| `Complex.cpow_conj` | Mathlib/Analysis/SpecialFunctions/Pow/Complex.lean:234 | Z1, Z2 |
| `Complex.natCast_arg` | Mathlib/Analysis/SpecialFunctions/Complex/Arg.lean:226 | Z2 |
| `Complex.arg_ofReal_of_nonneg` | Mathlib/Analysis/SpecialFunctions/Complex/Arg.lean:223 | Z1 |
| `Complex.ofReal_log` | Mathlib/Analysis/SpecialFunctions/Complex/Log.lean:71 | Z2 (`s = 1`) |
| `Real.pi_pos` | Mathlib/Analysis/SpecialFunctions/Trigonometric/Basic.lean:157 | Z1 |
| `Real.pi_ne_zero` | Mathlib/Analysis/SpecialFunctions/Trigonometric/Basic.lean:165 | Z1, Z2 |
| `HasDerivAt.conj_conj` | Mathlib/Analysis/Calculus/Deriv/Star.lean:93 | (context; iff form used) |
| `DifferentiableAt.conj_conj` | Mathlib/Analysis/Calculus/Deriv/Star.lean:117 | (context) |
| `differentiableAt_conj_conj_iff` | Mathlib/Analysis/Calculus/Deriv/Star.lean:123 | Z2, Z3, Z9(i) |
| `AnalyticOnNhd.eqOn_of_preconnected_of_eventuallyEq` | Mathlib/Analysis/Analytic/Uniqueness.lean:223 | Z2 |
| `AnalyticOnNhd.eq_of_eventuallyEq` | Mathlib/Analysis/Analytic/Uniqueness.lean:234 | Z3 |
| `AnalyticOnNhd.eqOn_of_preconnected_of_frequently_eq` | Mathlib/Analysis/Analytic/IsolatedZeros.lean:238 | cited as not-needed alternative |
| `isConnected_compl_singleton_of_one_lt_rank` | Mathlib/Analysis/Normed/Module/Connected.lean:125 | Z2 |
| `rank_real_complex` | Mathlib/LinearAlgebra/Complex/FiniteDimensional.lean:35 | Z2 |
| `isOpen_compl_singleton` | Mathlib/Topology/Separation/Basic.lean:354 | Z2 |
| `isOpen_univ` | Mathlib/Topology/Defs/Basic.lean:94 | Z3 |
| `DifferentiableOn.analyticOnNhd` | Mathlib/Analysis/Complex/CauchyIntegral.lean:631 | Z2, Z3 |
| `DifferentiableOn.analyticAt` | Mathlib/Analysis/Complex/CauchyIntegral.lean:625 | Z9(i) |
| `tsum_star` | Mathlib/Topology/Algebra/InfiniteSum/Constructions.lean:361 | Z2 |
| `∑'` = unconditional SummationFilter | Mathlib/Topology/Algebra/InfiniteSum/Defs.lean:160 | Z2 (notation audit) |
| `Complex.continuous_re` | Mathlib/Analysis/Complex/Basic.lean:153 | Z2, Z3 |
| `Complex.continuous_conj` | Mathlib/Analysis/Complex/Basic.lean:243 | Z9 |
| `Continuous.isOpen_preimage` | Mathlib/Topology/Defs/Basic.lean:154 (structure field) | Z2, Z3, Z9 |
| `isOpen_Ioi` | Mathlib/Topology/Order/OrderClosed.lean:216 | Z2, Z3 |
| `IsOpen.mem_nhds` | Mathlib/Topology/Neighborhoods.lean:90 | Z2, Z3 |
| `eventually_nhds_iff` | Mathlib/Topology/Neighborhoods.lean:68 | Z9 |
| `eventually_of_mem` | Mathlib/Order/Filter/Basic.lean:641 | Z2, Z3 |
| `Set.mem_compl_singleton_iff` | Mathlib/Order/BooleanAlgebra/Set.lean:195 | Z2 |
| `Set.image_eq_preimage_of_inverse` | Mathlib/Data/Set/Image.lean:346 | Z6 |
| `starRingEnd_apply` | Mathlib/Algebra/Star/Basic.lean:345 | Z2, Z5 |
| `Complex.conj_conj` (alias of `starRingEnd_self_apply`) | Mathlib/Algebra/Star/Basic.lean:364 | Z2-Z9 |
| `star_eq_zero` | Mathlib/Algebra/Star/Basic.lean:267 | Z5, Z9 |
| `Complex.conj_re` | Mathlib/Data/Complex/Basic.lean:467 | Z2, Z3, Z8 |
| `Complex.conj_ofReal` | Mathlib/Data/Complex/Basic.lean:475 | Z1, Z2 |
| `Complex.conj_natCast` | Mathlib/Data/Complex/Basic.lean:482 | Z2 |
| `Complex.conj_ofNat` | Mathlib/Data/Complex/Basic.lean:484 | Z1, Z7 |
| `Complex.zero_re` | Mathlib/Data/Complex/Basic.lean:125 | Z3 |
| `map_div₀` | Mathlib/Algebra/GroupWithZero/Units/Lemmas.lean:117 | Z1-Z4, Z7 |
| `mul_div_cancel₀` | Mathlib/Algebra/GroupWithZero/Units/Basic.lean:458 | Z3 |
| `analyticOrderAt` | Mathlib/Analysis/Analytic/Order.lean:47 | Z9 |
| `analyticOrderAt_of_not_analyticAt` | Mathlib/Analysis/Analytic/Order.lean:64 | Z9 |
| `analyticOrderAt_eq_top` | Mathlib/Analysis/Analytic/Order.lean:75 | Z9 |
| `AnalyticAt.analyticOrderAt_eq_natCast` | Mathlib/Analysis/Analytic/Order.lean:86 | Z9 |
| `AnalyticAt.eventually_analyticAt` | Mathlib/Analysis/Analytic/ChangeOrigin.lean:378 | Z9 |
| `AnalyticAt.differentiableAt` | Mathlib/Analysis/Calculus/FDeriv/Analytic.lean:126 | Z9 |
| `Nat.one_lt_ofNat`, `map_one/mul/sub/add/neg/pow`, `smul_eq_mul`, `Set.mem_preimage`, `Function.comp_apply` | (core API, bridge-precedent no-locator glue) | throughout |
| **bridge P2** `riemannZeta_zero_mem_critical_strip` | TARGET_BRIDGE_CONTRACT.md §P2 (package prerequisite, NOT pinned) | Z8' |
| **bridge P3** `riemannZeta_one_sub_eq_zero_iff` | TARGET_BRIDGE_CONTRACT.md §P3 (package prerequisite, NOT pinned) | Z8 |
| **xi X1** `riemannXi` | XI_PACKAGE_CONTRACT.md §X1 (package prerequisite, NOT pinned) | Z7, Z9-xi |

In-tree template witnesses (not dependencies): `NumberTheory/LSeries/DirichletContinuation.lean:124-144` (compl-singleton identity-theorem idiom), `NumberTheory/LSeries/ZMod.lean:526` (`eq_of_eventuallyEq` with the `PreconnectedSpace ℂ` instance), `Harmonic/ZetaAsymp.lean:434-435` (the `ofReal_log` realness cast walk).

## Anti-pitfall compliance (repo contracts)

- **Totalized values:** the `s = 1` value of `ζ` enters only through the pinned `riemannZeta_one` and its provable realness — never as a meromorphic value; `Λ`, `Λ₀` at `0, 1` are handled by total division (`1/0 = 0`, `conj 0 = 0`) in Z4, never by a pointwise product; `riemannZeta_def_of_ne_zero` is applied only under proved `w ≠ 0` inside the open half-plane (Z3); the pointwise transfer `Λ = Gammaℝ·ζ` is **never** used on the `Gammaℝ` zero set (documented in the Strategy decision — this is exactly why `Λ₀` gets its own identity-theorem pass).
- **Exact trivial-zero form:** the only trivial-zero exclusion in the package (Z8') is literally `¬∃ n : ℕ, s = -2 * (n + 1)`, character-identical to `RiemannHypothesis` (RiemannZeta.lean:182); no other statement needs it.
- **No inference from the functional equation:** no proof step uses `riemannZeta_one_sub`, `completedRiemannZeta(₀)_one_sub`, or any `s ↦ 1−s` fact to obtain conjugation — the capability map's explicit warning is honored; `1−s` enters only in Z8 through the already-built bridge P3, *after* conjugation is independently proved.
- **No competing definitions, no new RH `Prop`:** the package defines nothing except (via obligation S1C-ORD) two generic analytic lemmas; every zeta/xi object is the pinned or previously-contracted one.
- **Multiplicity discipline:** `riemannZetaZeros` is used as a set only (Z6); the only multiplicity-adjacent statement is Z9's local `analyticOrderAt` transport; no divisor, no enumeration, no sum over zeros. The remaining `S1-CONJ` exit item (divisor invariance under `ρ ↦ 1−conj ρ`) is explicitly left to the divisor package, and this contract does not claim to close the barrier alone.
- **Branch discipline:** every `cpow` conjugation is discharged with an explicit branch-cut hypothesis (`natCast_arg` / `arg_ofReal_of_nonneg` — real nonnegative bases only); no global `Complex.log` of anything is used.
- **Name collisions:** zero hits at the pin for all sixteen proposed names (grep-verified this session).

## Obligation register (v1 summary)

| id | severity | content |
|---|---|---|
| S1C-1 | LOW | termwise Dirichlet-series conj (`map_div₀` + `cpow_conj` triple-conj unwind; `n = 0` covered by `natCast_arg`) |
| S1C-2 | LOW | `tsum_star` star/conj mediation and SummationFilter instantiation (`∑'` = `unconditional`) |
| S1C-3 | LOW | realness of `ζ(1)`: `ofReal_log`/`push_cast`/`conj_ofReal` walk (in-tree mirror at ZetaAsymp.lean:434) |
| S1C-4 | LOW | `{1 < re} ∈ 𝓝 2` glue (in-tree template DirichletContinuation.lean:143) |
| S1C-5 | MEDIUM | Z3's `key` rearrangement (`linear_combination` over `completedRiemannZeta_eq` + `mul_div_cancel₀`) and the closing conj-push normal form; pure field/ring-hom algebra |
| S1C-6 | LOW | Z1 branch-cut/cast dance (`(↑π).arg = 0 ≠ π`, conj through `-·/2`) |
| S1C-7 | LOW | `PreconnectedSpace ℂ` instance resolution for `eq_of_eventuallyEq` (witnessed in-tree at ZMod.lean:526; fallbacks listed) |
| S1C-8 | LOW | Z4 closing `simp only` (`conj (1−s) = 1 − conj s` inside the pole terms) |
| S1C-9 | LOW | Z6 `LeftInverse`/`RightInverse` bundling for `image_eq_preimage_of_inverse` |
| S1C-10 | LOW | Z7 normal-form alignment after the Z3 rewrite |
| **S1C-ORD** | **MEDIUM-HIGH (main)** | **`AnalyticAt.conj_conj` and `analyticOrderAt_conj_conj` do not exist at the pin**; full assembly sketch given (three-case split over `analyticOrderAt_of_not_analyticAt` :64 / `analyticOrderAt_eq_top` :75 / `analyticOrderAt_eq_natCast` :86, witness transport `g ↦ conj∘g∘conj`, involution trick); all ingredients pinned, no analytic gap; ~40-60 lines |

No obligation is analytic. Every analytic input — the Dirichlet series on `1 < re`, zeta's analyticity off `1`, entirety of `Λ₀`, `Λ = Λ₀ − 1/s − 1/(1−s)`, `Gamma` conjugation, `cpow` conjugation off the branch cut, antiholomorphic-composition differentiability, the identity principle, preconnectedness of `ℂ` and `ℂ∖{1}`, the totalized `ζ(1)` value, and the analytic-order characterization API — is a quoted pinned theorem at `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`. These obligations were kernel-checked by the merged promotion PR #307 (`c277b86`), after independent review, bridge (P1-P5) landing in PR #299 (for Z8), xi-package landing in PR #304 (for Z7/Z9-xi), and closure of the carried preconditions; the contract itself remains the retained specification artifact. Kernel verification of the package does not close `S1-CONJ`.

---

## ANNEX B: adversarial review record (2026-08-06)

Independent adversarial re-verification at the pin confirmed every cited
declaration, file, line, and signature — including the two mandated danger
zones: the cpow-conjugation lemmas carry exactly the branch-cut hypothesis
`x.arg ≠ π`, and the draft discharges it only on real-nonnegative bases
(`↑π` and ℕ-casts, `n = 0` included via `natCast_arg`) — **no branch-cut
error**; the identity principle is applied in its `eventuallyEq` form on the
open half-plane with base point `2 ∈ {1}ᶜ` where both functions are proved
analytic — the accumulation framing is correct. C1's hypothesis-free global
claim at `s = 1` is sound (the totalized value is the coercion of a real).
Verdict `SOUND_WITH_FIXES`; findings (all applied in v2): **F1** (LOW)
`linear_combination` sign in the Z3 skeleton; **F2** (LOW) the Z2 `s = 1`
closing step now mirrors the pin's own `ZetaAsymp.lean:434` one-step simp
set; **F3/F4** (INFO) two locator cosmetics.

## Acceptance note 2026-08-06

Independent review rechecked all sixteen Z1-Z9 statement signatures, the
functional-equation separation, the branch-cut hypotheses, and the pinned API
surface. No mathematical statement blocker was found. Before acceptance, the
review synchronized the Z2 skeleton with its coherent real-value proof and
corrected F1 to `linear_combination hΛ - h`; the opposite order is the
negative of the goal. This accepts the contract surface only. It is not a Lean
kernel verdict, does not promote a module, and does not close `S1-CONJ`.

**Post-promotion addendum (2026-08-07).** The note above is retained verbatim
as a dated record of the acceptance pass; it was accurate when written and its
boundaries stand. The promotion it declined to perform subsequently occurred
as merged PR #307 (`c277b86`) — see the status addendum at the head of this
document. The merged module carries the corrected F1 sign
(`linear_combination hΛ - h`, `Conj.lean:202`) and preserves the sign history
as history (`Conj.lean:205-207`). `S1-CONJ` remains OPEN.
