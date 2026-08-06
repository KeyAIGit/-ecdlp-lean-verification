# RH xi-package theorem contract (A/C follow-on): draft v2

Status: **DRAFT v2 (2026-08-06) — retained non-built review artifact. The initial
adversarial verdict was `SOUND_WITH_FIXES`; its four findings are dispositioned
in Annex B, with the F1 usage correction recorded in Annex C. Independent
statement acceptance is complete with editorial-only
fixes; record: `notes/reviews/RH007_XI_CONTRACT_ACCEPTANCE_2026_08_06.md`.
The separate built counterpart merged in PR #304 (`afdae08`) after the first
promotion pass exposed one proof-only X11 composition-call error. The
statement-preserving repair is recorded in Annex C; the final head passed the
full build, no-incomplete-proof gate, ledger/registry coverage, and both axiom
audits. `S0-TRUST` was
satisfied by PR #298 (`d6e146fa`), the target bridge by PR #299 (`288d65b`),
and the source-contract prerequisite by the accepted `RH-006` replay and
amendments on 2026-08-06.**

Scope: the package designated by `MATHLIB_CAPABILITY_MAP.md` §"Gate 0: safe entire xi specification" and §"First implementable foundation and stop rule" (*"A following A/C-only foundation PR may contain the normalized xi bridge package"*), with the statement list frozen in `TARGET_BRIDGE_CONTRACT.md` Annex A. It contains no Li coefficients, no zero enumeration, no divisor packaging, no conjugation symmetry, no growth theorem, and no claim of progress on RH. X11 is the only `S1-MULTIPLICITY`-adjacent statement and transports local analytic order only; it does not construct a divisor.

Pinned Mathlib: `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0), verified this session via `git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD`. Every declaration cited below was grep-verified at that exact revision this session; all `file:line` locators are from that tree (paths relative to `Mathlib/` root of the pin).

Package prerequisites (cited as **bridge prerequisites**, not pinned Mathlib): `TARGET_BRIDGE_CONTRACT.md` theorems P1–P5, specifically `riemannZeta_zero_mem_critical_strip` (P2) in X10. The A/C DAG lists the bridge package as a prerequisite of this one.

## Candidate fields

- **Mechanism.** The entire pole-removed completion `completedRiemannZeta₀` and the proved sign identity `completedRiemannZeta_eq` (`Λ(s) = Λ₀(s) − 1/s − 1/(1−s)`, RiemannZeta.lean:84 — the theorem, not the conflicting module comment) determine the chosen entire normalization `riemannXi` under this contract, with `ξ(0) = ξ(1) = 1/2`, `ξ(1−s) = ξ(s)`, zeros exactly the nontrivial zeta zeros, and local analytic order equal to zeta's inside the open strip. No uniqueness claim is made beyond these frozen contract choices.
- **Expected information gain.** The kernel-checked promotion closes the repo-local `S1-XI` barrier and supplies theorems for the map's pinned-Mathlib `NOT-FOUND` capabilities "standard Riemann xi" and "zeta/xi analytic order equality"; it partially advances `S1-MULTIPLICITY` (order transport only — no divisor, no symmetry action). No information about the truth of RH is produced.
- **Claim boundary.** All eleven contract clauses (twelve public declarations) are unconditional consequences of pinned Mathlib theorems plus bridge P2. Nothing touches enumeration, growth, Hadamard products, conjugation, or any route's research obligation.
- **Death condition (stop rule).** Stop or split if any proof requires weakening an exclusion, assuming a hidden nonvanishing fact, treating a totalized exceptional value as a meromorphic value, or introducing a competing RH proposition. A clean blocker is preferable to a false xi bridge.

Proposed module preamble (name-resolution review only; the eventual built file also imports the built bridge module):

```lean
import Mathlib.NumberTheory.LSeries.ZetaZeros              -- riemannZeta API (transitively RiemannZeta.lean)
import Mathlib.NumberTheory.Harmonic.ZetaAsymp             -- riemannZeta_one_ne_zero
import Mathlib.Analysis.Analytic.Order                     -- analyticOrderAt API (X11)
import Mathlib.Analysis.SpecialFunctions.Gamma.Deriv       -- Complex.differentiableAt_Gamma (X11)
import Mathlib.Analysis.SpecialFunctions.Pow.Deriv         -- DifferentiableAt.const_cpow (X11)
import Mathlib.Analysis.Complex.CauchyIntegral             -- DifferentiableOn.analyticAt (X11)
-- + import of the built bridge module providing P1–P5

open Complex
open scoped Real
```

Name-collision scan: `grep -rn "riemannXi" Mathlib/` over the pinned tree returns **zero hits** (verified this session). None of the proposed names (`riemannXi`, `differentiable_riemannXi`, `riemannXi_one_sub`, `riemannXi_zero`, `riemannXi_one`, `riemannXi_eq_of_ne`, `riemannXi_eq_zero_iff_riemannZeta_eq_zero`, `riemannXi_ne_zero_of_one_le_re`, `riemannXi_ne_zero_of_re_le_zero`, `riemannXi_zero_mem_critical_strip`, `riemannHypothesis_iff_riemannXi_zeros_re_eq_half`, `analyticOrderAt_riemannXi_eq_riemannZeta`) collides with any pinned declaration.

---

## 0. Exact pinned interface (quoted from the tree at the pin)

```lean
-- RiemannZeta.lean:63, :67
def completedRiemannZeta₀ (s : ℂ) : ℂ := completedHurwitzZetaEven₀ 0 s
def completedRiemannZeta (s : ℂ) : ℂ := completedHurwitzZetaEven 0 s

-- RiemannZeta.lean:84  (SIGN SOURCE OF TRUTH; the module comment disagrees — the theorem wins)
lemma completedRiemannZeta_eq (s : ℂ) :
    completedRiemannZeta s = completedRiemannZeta₀ s - 1 / s - 1 / (1 - s)

-- RiemannZeta.lean:89
theorem differentiable_completedZeta₀ : Differentiable ℂ completedRiemannZeta₀

-- RiemannZeta.lean:99
theorem completedRiemannZeta₀_one_sub (s : ℂ) :
    completedRiemannZeta₀ (1 - s) = completedRiemannZeta₀ s

-- RiemannZeta.lean:144 (AnalyticOnNhd — pointwise AnalyticAt on {1}ᶜ by application)
lemma analyticOn_riemannZeta : AnalyticOnNhd ℂ riemannZeta {1}ᶜ

-- RiemannZeta.lean:152
lemma riemannZeta_def_of_ne_zero {s : ℂ} (hs : s ≠ 0) :
    riemannZeta s = completedRiemannZeta s / Gammaℝ s

-- RiemannZeta.lean:182 (canonical target; never restated, never replaced)
def RiemannHypothesis : Prop :=
  ∀ (s : ℂ) (_ : riemannZeta s = 0) (_ : ¬∃ n : ℕ, s = -2 * (n + 1)) (_ : s ≠ 1), s.re = 1 / 2

-- Gamma/Deligne.lean:43, :66, :73 (namespace Complex opens at Deligne.lean:37).
-- NOTE the Gammaℝ zero set -(2*n) INCLUDES 0 (n = 0): strictly larger than the trivial-zero set.
noncomputable def Gammaℝ (s : ℂ) := π ^ (-s / 2) * Gamma (s / 2)
lemma Gammaℝ_ne_zero_of_re_pos {s : ℂ} (hs : 0 < re s) : Gammaℝ s ≠ 0
lemma Gammaℝ_eq_zero_iff {s : ℂ} : Gammaℝ s = 0 ↔ ∃ n : ℕ, s = -(2 * n)

-- Nonvanishing.lean:410 (namespace DirichletCharacter; _root_ prefix; STRICT-implicit ⦃s⦄)
lemma _root_.riemannZeta_ne_zero_of_one_le_re ⦃s : ℂ⦄ (hs : 1 ≤ s.re) : riemannZeta s ≠ 0

-- Harmonic/ZetaAsymp.lean:408 and :431 (totalized value at the pole IS known and IS nonzero)
lemma riemannZeta_one : riemannZeta 1 = (γ - log (4 * π)) / 2
lemma riemannZeta_one_ne_zero : riemannZeta 1 ≠ 0

-- Analysis/Analytic/Order.lean:47, :61, :133, :175, :497
noncomputable def analyticOrderAt (f : 𝕜 → E) (z₀ : 𝕜) : ℕ∞
noncomputable def analyticOrderNatAt (f : 𝕜 → E) (z₀ : 𝕜) : ℕ := (analyticOrderAt f z₀).toNat
protected lemma AnalyticAt.analyticOrderAt_eq_zero (hf : AnalyticAt 𝕜 f z₀) :
    analyticOrderAt f z₀ = 0 ↔ f z₀ ≠ 0
lemma analyticOrderAt_congr (hfg : f =ᶠ[𝓝 z₀] g) :
    analyticOrderAt f z₀ = analyticOrderAt g z₀
theorem analyticOrderAt_mul (hf : AnalyticAt 𝕜 f z₀) (hg : AnalyticAt 𝕜 g z₀) :
    analyticOrderAt (f * g) z₀ = analyticOrderAt f z₀ + analyticOrderAt g z₀

-- Analysis/Complex/CauchyIntegral.lean:625
protected theorem _root_.DifferentiableOn.analyticAt {s : Set ℂ} {f : ℂ → E} {z : ℂ}
    (hd : DifferentiableOn ℂ f s) (hz : s ∈ 𝓝 z) : AnalyticAt ℂ f z

-- Gamma/Deriv.lean:65 (namespace Complex)
theorem differentiableAt_Gamma (s : ℂ) (hs : ∀ m : ℕ, s ≠ -m) : DifferentiableAt ℂ Gamma s

-- Pow/Deriv.lean:111
theorem DifferentiableAt.const_cpow (hf : DifferentiableAt ℂ f x) (h0 : c ≠ 0 ∨ f x ≠ 0) :
    DifferentiableAt ℂ (fun x => c ^ f x) x
```

**Confirmed absences at the pin (grep-verified this session):** there is **no** `differentiable_Gammaℝ`, no `differentiableAt_Gammaℝ`, and no `analyticAt_Gammaℝ` anywhere in the tree — only `differentiable_Gammaℝ_inv` (Deligne.lean:88), which is the wrong direction for X11 (analyticity of `Gammaℝ` itself is needed, since the factorization multiplies by `Gammaℝ`, not by its inverse). See OBLIGATION X11-G. The product/unit order lemmas needed by X11 **do all exist**: `analyticOrderAt_mul` (Order.lean:497), `analyticOrderAt_congr` (:175), `AnalyticAt.analyticOrderAt_eq_zero` (:133).

## Sign derivation from the theorem (the S0-SEMANTIC trap, discharged once, on paper)

From `completedRiemannZeta_eq` (RiemannZeta.lean:84), for `s ≠ 0`, `s ≠ 1`:

```text
s(s−1)·Λ(s) = s(s−1)·Λ₀(s) − s(s−1)·(1/s) − s(s−1)·(1/(1−s))
  s(s−1)/s      = s−1                                  [cancel s, s ≠ 0]
  s(s−1)/(1−s)  = s·(−(1−s))/(1−s) = −s                [s−1 = −(1−s), 1−s ≠ 0]
⟹ s(s−1)·Λ(s) = s(s−1)·Λ₀(s) − (s−1) − (−s) = s(s−1)·Λ₀(s) + 1.
```

Hence `(1 + s(s−1)Λ₀(s))/2 = s(s−1)Λ(s)/2` away from `0, 1`. Had the (wrong) module-comment sign `Λ = Λ₀ + 1/s + 1/(1−s)` been used, the constant would come out `−1`, and X4 (`ξ(0) = ξ(1) = 1/2`, matching the classical value and `LAG07`'s (2.7) normalization up to its declared factor 2) would fail — X4 is therefore also the built-in sign self-check.

---

## X1. Definition

```lean
noncomputable def riemannXi (s : ℂ) : ℂ :=
  (1 + s * (s - 1) * completedRiemannZeta₀ s) / 2
```

Verbatim the Gate-0 / Annex-A normalization. `completedRiemannZeta₀` is the real pinned name (RiemannZeta.lean:63). Total, entire-by-construction (X2), no exceptional points. This does **not** restate or replace `RiemannHypothesis`. Implementation latitude: a non-exported `lemma riemannXi_def (s : ℂ) : riemannXi s = (1 + s * (s - 1) * completedRiemannZeta₀ s) / 2 := rfl` may be added as unfolding glue; it is not a package statement.

Pinned dependencies (X1): `completedRiemannZeta₀` (NumberTheory/LSeries/RiemannZeta.lean:63).

Obligations (X1): none.

## X2. Entirety

### Statement

```lean
theorem differentiable_riemannXi : Differentiable ℂ riemannXi
```

### Proof skeleton

```lean
theorem differentiable_riemannXi : Differentiable ℂ riemannXi := by
  unfold riemannXi
  exact ((differentiable_const _).add
      ((differentiable_id.mul (differentiable_id.sub (differentiable_const _))).mul
        differentiable_completedZeta₀)).div_const _
```

Step by step: `differentiable_const` (FDeriv/Const.lean:243) for `1`; `differentiable_id` (FDeriv/Basic.lean:708) for `s`; `Differentiable.sub` (FDeriv/Add.lean:688) for `s − 1`; `Differentiable.mul` (FDeriv/Mul.lean:226, stated in `fun y => a y * b y` form) twice, the second against `differentiable_completedZeta₀` (RiemannZeta.lean:89); `Differentiable.add` (FDeriv/Add.lean:227); `Differentiable.div_const` (Deriv/Mul.lean:585, `fun x => c x / d`).

### Pinned dependencies (X2)

`differentiable_completedZeta₀` (RiemannZeta.lean:89), `differentiable_const` (FDeriv/Const.lean:243), `differentiable_id` (FDeriv/Basic.lean:708), `Differentiable.add` (FDeriv/Add.lean:227), `Differentiable.sub` (FDeriv/Add.lean:688), `Differentiable.mul` (FDeriv/Mul.lean:226), `Differentiable.div_const` (Deriv/Mul.lean:585).

### Obligations (X2)

- **OBLIGATION X2-a (LOW):** `differentiable_id` is stated for `(id : E → E)`, not the lambda `fun s => s`; there is **no** `differentiable_id'` at the pin (grep-confirmed). Defeq normally elaborates; fallback is `fun s => s` via `differentiableAt_id` pointwise, or `by unfold riemannXi; fun_prop` for the polynomial skeleton with `differentiable_completedZeta₀` supplied manually.

## X3. Functional equation

### Statement

```lean
theorem riemannXi_one_sub (s : ℂ) : riemannXi (1 - s) = riemannXi s
```

### Proof skeleton

```lean
theorem riemannXi_one_sub (s : ℂ) : riemannXi (1 - s) = riemannXi s := by
  unfold riemannXi
  rw [completedRiemannZeta₀_one_sub]
  ring
```

After the rewrite (RiemannZeta.lean:99), the goal is `(1 + (1−s)·((1−s)−1)·Λ₀ s)/2 = (1 + s·(s−1)·Λ₀ s)/2`; `(1−s)·((1−s)−1) = (1−s)·(−s) = s² − s = s·(s−1)` is exactly the `ring`-closable identity required by the task. `Λ₀ s` is an opaque atom for `ring`.

### Pinned dependencies (X3)

`completedRiemannZeta₀_one_sub` (RiemannZeta.lean:99).

### Obligations (X3)

None (pure `ring` over a commutative ring; no division involved).

## X4. Endpoint values

### Statements

```lean
theorem riemannXi_zero : riemannXi 0 = 1 / 2
theorem riemannXi_one  : riemannXi 1 = 1 / 2
```

Both values are read off the **entire formula**, never from a totalized pointwise product (`Λ` and `Gammaℝ` do not appear) — exactly the `SOURCE_CONTRACTS.md` §Shared-notation requirement "Derive values at all excluded points from the entire formula".

### Proof skeletons

```lean
theorem riemannXi_zero : riemannXi 0 = 1 / 2 := by
  unfold riemannXi; norm_num          -- 0 * (0 - 1) * Λ₀ 0 = 0 via zero_mul inside norm_num

theorem riemannXi_one : riemannXi 1 = 1 / 2 := by
  unfold riemannXi; norm_num          -- (1 - 1) = 0, then mul_zero/zero_mul
```

### Pinned dependencies (X4)

Definition X1 only; `zero_mul`/`mul_zero`/`sub_self` fire inside `norm_num`'s simp set (core simp lemmas, no locator needed per bridge precedent for core glue).

### Obligations (X4)

- **OBLIGATION X4-a (LOW):** exact `norm_num`/`simp` set (schematic; `simp [riemannXi]` followed by `norm_num` is the fallback).

## X5. Off-endpoint equality with `s(s−1)Λ(s)/2`

### Statement

```lean
theorem riemannXi_eq_of_ne {s : ℂ} (hs0 : s ≠ 0) (hs1 : s ≠ 1) :
    riemannXi s = s * (s - 1) * completedRiemannZeta s / 2
```

The sign arithmetic is the derivation in §"Sign derivation" above, from `completedRiemannZeta_eq` **the theorem** (RiemannZeta.lean:84). The exclusions `hs0`, `hs1` are exactly the denominators' nonvanishing (`1/s` and `1/(1−s)`); neither can be weakened.

### Proof skeleton

```lean
theorem riemannXi_eq_of_ne {s : ℂ} (hs0 : s ≠ 0) (hs1 : s ≠ 1) :
    riemannXi s = s * (s - 1) * completedRiemannZeta s / 2 := by
  have h1s : (1 : ℂ) - s ≠ 0 := sub_ne_zero.mpr (Ne.symm hs1)
  unfold riemannXi
  rw [completedRiemannZeta_eq]
  -- goal: (1 + s*(s-1)*Λ₀ s)/2 = s*(s-1)*(Λ₀ s - 1/s - 1/(1-s))/2
  field_simp
  ring
```

The exact `field_simp`/`ring` chain: `field_simp` picks up `hs0` and `h1s` from context, clears the three denominators `s`, `1 − s`, `2`, and the residual polynomial identity — equivalent to `s(s−1)Λ = s(s−1)Λ₀ − (s−1) + s`, i.e. the two cancellations `s(s−1)/s = s−1` and `−s(s−1)/(1−s) = +s` (since `s−1 = −(1−s)`) — is closed by `ring`. On paper the two cancellations are `mul_div_cancel_left₀`-shaped and `mul_div_cancel₀`-shaped (GroupWithZero/Units/Basic.lean:458 for the latter); inside the skeleton they are absorbed by `field_simp; ring`.

### Pinned dependencies (X5)

`completedRiemannZeta_eq` (RiemannZeta.lean:84), `sub_ne_zero` (to_additive of `div_ne_one`, Algebra/Group/Basic.lean:753), `mul_div_cancel₀` (Algebra/GroupWithZero/Units/Basic.lean:458 — paper derivation; may not appear in the final term), `two_ne_zero` (Algebra/NeZero.lean:36 — implicit in `field_simp`).

### Obligations (X5)

- **OBLIGATION X5-a (MEDIUM):** the exact `field_simp` normal form is version-sensitive (same class as bridge P1-c). Review fix F2: a bare `linear_combination (s * (s - 1) / 2) * completedRiemannZeta_eq s` canNOT close the goal by itself — the residual contains `s * s⁻¹`-type terms that are not commutative-ring identities (inverses are atoms to `ring`), so every variant must clear denominators under `hs0`/`hs1`. Admissible fallback: `have h1 : s * (s - 1) * (1 / s) = s - 1 := by field_simp` and `have h2 : s * (s - 1) * (1 / (1 - s)) = -s := by field_simp` (both use the hypotheses), then `rw [completedRiemannZeta_eq]` and close with `linear_combination`-over-the-cleared identity. Pure field algebra; no analytic content.

## X6. Exact zero correspondence

### Statement

```lean
theorem riemannXi_eq_zero_iff_riemannZeta_eq_zero {s : ℂ} (hs0 : s ≠ 0) (hs1 : s ≠ 1)
    (htriv : ¬∃ n : ℕ, s = -2 * (n + 1)) :
    riemannXi s = 0 ↔ riemannZeta s = 0
```

### Set-coverage argument (the reverse direction's load-bearing step, verified precisely)

`Complex.Gammaℝ_eq_zero_iff` (Deligne.lean:73) places the zeros of `Gammaℝ` at `s = -(2*n)`, `n : ℕ`. As a set:

```text
{ -(2n) | n : ℕ } = { -(2·0) } ∪ { -(2(m+1)) | m : ℕ } = {0} ∪ { -2·(m+1) | m : ℕ }.
```

- the `n = 0` branch is `s = -(2·0) = 0`, excluded **exactly** by `hs0` (and by nothing else: `htriv` does *not* cover `0`, since trivial zeros start at `−2`);
- the `n = m+1` branch is `s = -(2·(m+1))`, and the witness `m` converts it to the **exact** target trivial-zero form `s = -2 * (↑m + 1)` (cast identity `-(2*↑(m+1)) = -2*(↑m + 1)` by `push_cast; ring`), excluded exactly by `htriv`.

The coverage is exhaustive and non-overlapping; neither exclusion is redundant and neither may be weakened. This is precisely the `S0-SEMANTIC` boundary item "the distinct `Gammaℝ` zero set `-(2*n)` (which additionally contains `0`) is never conflated with the trivial-zero form".

### Proof skeleton

```lean
theorem riemannXi_eq_zero_iff_riemannZeta_eq_zero {s : ℂ} (hs0 : s ≠ 0) (hs1 : s ≠ 1)
    (htriv : ¬∃ n : ℕ, s = -2 * (n + 1)) :
    riemannXi s = 0 ↔ riemannZeta s = 0 := by
  -- Gammaℝ s ≠ 0 under exactly the stated exclusions (set coverage above)
  have hG : Gammaℝ s ≠ 0 := by
    rw [Ne, Complex.Gammaℝ_eq_zero_iff]
    rintro ⟨n, rfl⟩
    match n with
    | 0     => exact hs0 (by norm_num)
    | m + 1 => exact htriv ⟨m, by push_cast; ring⟩          -- OBLIG X6-a
  have hs1' : s - 1 ≠ 0 := sub_ne_zero.mpr hs1
  rw [riemannXi_eq_of_ne hs0 hs1,                            -- X5
      riemannZeta_def_of_ne_zero hs0,                        -- ζ = Λ / Gammaℝ, only under s ≠ 0
      div_eq_zero_iff, div_eq_zero_iff]
  -- LHS: s*(s-1)*Λ s = 0 ∨ (2:ℂ) = 0 ; RHS: Λ s = 0 ∨ Gammaℝ s = 0
  constructor
  · rintro (h | h)
    · rcases mul_eq_zero.mp h with h' | hΛ
      · rcases mul_eq_zero.mp h' with h0 | h1
        · exact absurd h0 hs0
        · exact absurd h1 hs1'
      · exact Or.inl hΛ
    · exact absurd h two_ne_zero
  · rintro (hΛ | hGz)
    · exact Or.inl (by rw [hΛ, mul_zero])
    · exact absurd hGz hG
```

The forward direction is `mul_eq_zero` chains plus the `/2` factor (`two_ne_zero`); the reverse direction genuinely needs `hG`, i.e. `Gammaℝ_eq_zero_iff` — not field algebra alone — exactly as `SOURCE_CONTRACTS.md` and the capability map require. `riemannZeta_def_of_ne_zero` is applied only under the proved `hs0`.

### Pinned dependencies (X6)

X5; `riemannZeta_def_of_ne_zero` (RiemannZeta.lean:152), `Complex.Gammaℝ_eq_zero_iff` (Gamma/Deligne.lean:73), `div_eq_zero_iff` (Algebra/GroupWithZero/Units/Basic.lean:289), `mul_eq_zero` (Algebra/GroupWithZero/Defs.lean:304), `two_ne_zero` (Algebra/NeZero.lean:36), `sub_ne_zero` (Algebra/Group/Basic.lean:753, to_additive), `mul_zero` (core).

### Obligations (X6)

- **OBLIGATION X6-a (LOW):** the `ℕ → ℂ` cast identity `-(2 * ((m + 1 : ℕ) : ℂ)) = -2 * ((m : ℂ) + 1)` for the trivial-zero witness (`push_cast; ring`), and the `n = 0` branch `-(2 * ((0 : ℕ) : ℂ)) = 0` (`norm_num`). Same class as bridge P1-d.

## X7. Nonvanishing on the closed right half-plane

### Statement

```lean
theorem riemannXi_ne_zero_of_one_le_re {s : ℂ} (hs : 1 ≤ s.re) : riemannXi s ≠ 0
```

`s = 1` is handled by the totalized-free value `riemannXi_one` (X4) — the closed half-plane comes for free, mirroring the bridge's use of `riemannZeta_ne_zero_of_one_le_re` which itself covers the totalized point 1 via `riemannZeta_one_ne_zero` (Nonvanishing.lean:412-415).

### Proof skeleton

```lean
theorem riemannXi_ne_zero_of_one_le_re {s : ℂ} (hs : 1 ≤ s.re) : riemannXi s ≠ 0 := by
  rcases eq_or_ne s 1 with rfl | hs1
  · rw [riemannXi_one]; norm_num                               -- 1/2 ≠ 0
  · have hs0 : s ≠ 0 := by
      rintro rfl; rw [Complex.zero_re] at hs; linarith
    have htriv : ¬∃ n : ℕ, s = -2 * (n + 1) := by
      rintro ⟨n, rfl⟩
      rw [show ((-2 : ℂ) * (n + 1)).re = -2 * ((n : ℝ) + 1) by push_cast; simp] at hs
      nlinarith [Nat.cast_nonneg (α := ℝ) n]                   -- OBLIG X7-a (= bridge P2-a form)
    intro hz
    exact riemannZeta_ne_zero_of_one_le_re hs
      ((riemannXi_eq_zero_iff_riemannZeta_eq_zero hs0 hs1 htriv).mp hz)
```

### Pinned dependencies (X7)

X4, X6; `riemannZeta_ne_zero_of_one_le_re` (Nonvanishing.lean:410 — `_root_` prefix, strict-implicit `⦃s⦄`, applies by unification here), `Complex.zero_re` (Data/Complex/Basic.lean:125), `Nat.cast_nonneg` (core cast API).

### Obligations (X7)

- **OBLIGATION X7-a (LOW):** the real-part cast computation `((-2 : ℂ) * (↑n + 1)).re = -2 * (n + 1)`; identical to bridge P2-a/P4-a (shared discharge).

## X8. Nonvanishing on the closed left half-plane (covers all negative even points)

### Statement

```lean
theorem riemannXi_ne_zero_of_re_le_zero {s : ℂ} (hs : s.re ≤ 0) : riemannXi s ≠ 0
```

### Design note

Pure reflection: `re s ≤ 0 ⟹ re (1−s) ≥ 1`, then X3 + X7. The `s = 0` case named in the package spec is **subsumed**: for `s = 0` the reflection lands on `1 − 0 = 1`, which X7 already handles via `riemannXi_one`; equivalently one may split `s = 0` off explicitly via `riemannXi_zero` — both are faithful, the skeleton takes the split-free form and the reviewer may demand the explicit split for literal Annex-A alignment (`riemannXi_zero` remains a package statement either way, via X4). This theorem is exactly the map's "xi is nonzero at every negative even point: symmetry maps `−2(n+1)` to `2n+3`" requirement, strengthened to the whole closed half-plane, in the map's required non-circular order (X6 before X8, X8 before X9).

### Proof skeleton

```lean
theorem riemannXi_ne_zero_of_re_le_zero {s : ℂ} (hs : s.re ≤ 0) : riemannXi s ≠ 0 := by
  intro hz
  refine riemannXi_ne_zero_of_one_le_re (s := 1 - s) ?_ ?_
  · rw [Complex.sub_re, Complex.one_re]; linarith
  · rw [riemannXi_one_sub]; exact hz
```

### Pinned dependencies (X8)

X3, X7; `Complex.sub_re` (Data/Complex/Basic.lean:640), `Complex.one_re` (Data/Complex/Basic.lean:147).

### Obligations (X8)

None.

## X9. Xi-side critical-strip localization

### Statement

```lean
theorem riemannXi_zero_mem_critical_strip {s : ℂ} (hz : riemannXi s = 0) :
    0 < s.re ∧ s.re < 1
```

Note: unlike the zeta-side P2, **no** trivial-zero hypothesis is needed — X8 excludes the entire closed left half-plane including the trivial points, because `riemannXi` genuinely does not vanish there (that is the point of the xi normalization). Hypothesis-free localization is the xi package's own localization required by the map's addendum §3.

### Proof skeleton

```lean
theorem riemannXi_zero_mem_critical_strip {s : ℂ} (hz : riemannXi s = 0) :
    0 < s.re ∧ s.re < 1 := by
  constructor
  · by_contra h; exact riemannXi_ne_zero_of_re_le_zero (not_lt.mp h) hz
  · by_contra h; exact riemannXi_ne_zero_of_one_le_re (not_lt.mp h) hz
```

### Pinned dependencies (X9)

X7, X8; `not_lt` (order core).

### Obligations (X9)

None.

## X10. RH equivalence via xi zeros

### Statement

```lean
theorem riemannHypothesis_iff_riemannXi_zeros_re_eq_half :
    RiemannHypothesis ↔ ∀ s : ℂ, riemannXi s = 0 → s.re = 1 / 2
```

Left side is `_root_.RiemannHypothesis` verbatim (RiemannZeta.lean:182); no competing proposition is introduced. The xi side needs **no** exclusions at all — X9 makes every xi zero automatically nontrivial, non-pole, non-zero-point.

### Proof skeleton

```lean
theorem riemannHypothesis_iff_riemannXi_zeros_re_eq_half :
    RiemannHypothesis ↔ ∀ s : ℂ, riemannXi s = 0 → s.re = 1 / 2 := by
  constructor
  · -- forward: RH ⟹ xi zeros on the line
    intro hRH s hz
    obtain ⟨h0, h1⟩ := riemannXi_zero_mem_critical_strip hz            -- X9
    have hs0 : s ≠ 0 := fun e => by simp [e] at h0
    have hs1 : s ≠ 1 := fun e => by simp [e] at h1
    have htriv : ¬∃ n : ℕ, s = -2 * (n + 1) := by
      rintro ⟨n, rfl⟩
      rw [show ((-2 : ℂ) * (n + 1)).re = -2 * ((n : ℝ) + 1) by push_cast; simp] at h0
      nlinarith [Nat.cast_nonneg (α := ℝ) n]                           -- OBLIG X10-a
    exact hRH s ((riemannXi_eq_zero_iff_riemannZeta_eq_zero hs0 hs1 htriv).mp hz) htriv hs1
  · -- reverse: xi-line condition ⟹ RH; strip localization comes from BRIDGE P2
    intro h s hz htriv _hs1
    obtain ⟨h0, h1⟩ := riemannZeta_zero_mem_critical_strip hz htriv    -- BRIDGE PREREQUISITE P2
    have hs0 : s ≠ 0 := fun e => by simp [e] at h0
    have hs1 : s ≠ 1 := fun e => by simp [e] at h1
    exact h s ((riemannXi_eq_zero_iff_riemannZeta_eq_zero hs0 hs1 htriv).mpr hz)
```

Both directions route through X6 with all three exclusions **proved**, never assumed: forward from X9 (xi-side localization), reverse from bridge P2 (zeta-side localization). The reverse direction ignores the target's redundant `s ≠ 1` binder and re-derives it from P2 (`re s < 1`), keeping the proof independent of binder bookkeeping. No conjugation symmetry is used anywhere (consistent with its `NOT-FOUND` status).

### Pinned dependencies (X10)

X6, X9; **bridge prerequisite** `riemannZeta_zero_mem_critical_strip` (TARGET_BRIDGE_CONTRACT.md P2 — not pinned Mathlib); `RiemannHypothesis` (RiemannZeta.lean:182), `Complex.zero_re`/`one_re` (Data/Complex/Basic.lean:125/147), `Nat.cast_nonneg` (core cast API).

### Obligations (X10)

- **OBLIGATION X10-a (LOW):** same cast computation as X7-a / bridge P2-a (shared discharge).
- **OBLIGATION X10-b (LOW):** `RiemannHypothesis` is a semireducible `def`: `intro`/application must unfold it; fallback `show ∀ (s : ℂ) ...` — identical to bridge P4-b/P5-a.

## X11. Analytic-order transport (the hard one)

### Statement

```lean
theorem analyticOrderAt_riemannXi_eq_riemannZeta {s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) :
    analyticOrderAt riemannXi s = analyticOrderAt riemannZeta s
```

### Design

`Analysis/Analytic/Order.lean` was studied in full at the pin. The relevant API triple exists and is exactly sufficient:

| need | pinned lemma | file:line |
|---|---|---|
| order invariant under local (`𝓝`-eventual) equality | `analyticOrderAt_congr (hfg : f =ᶠ[𝓝 z₀] g)` | Order.lean:175 |
| order of a product of analytic factors is additive | `analyticOrderAt_mul (hf : AnalyticAt) (hg : AnalyticAt) : analyticOrderAt (f * g) z₀ = ... + ...` | Order.lean:497 |
| order zero iff nonvanishing (for analytic `f`) | `AnalyticAt.analyticOrderAt_eq_zero : analyticOrderAt f z₀ = 0 ↔ f z₀ ≠ 0` | Order.lean:133 |

(Neighbors checked and not needed: `analyticOrderAt_eq_zero` :120 unprotected version, `AnalyticAt.analyticOrderAt_ne_zero` :137, `analyticOrderNatAt_mul` :502 — the latter is the statement to use if a reviewer later wants the `ℕ`-valued `analyticOrderNatAt` corollary demanded by `SOURCE_CONTRACTS.md`; it additionally needs both orders `≠ ⊤`, available from `AnalyticAt.analyticOrderAt_ne_top` :113 once ξ, ζ are known not to vanish identically — deferred, not in this package.)

Factorization: on the **open** strip `U = {z | 0 < re z ∧ re z < 1}` (open since `re` is continuous — `Complex.continuous_re`, Analysis/Complex/Basic.lean:153 — and `isOpen_lt`, Topology/Order/OrderClosed.lean:556; `U ∈ 𝓝 s` by `IsOpen.mem_nhds`, Topology/Neighborhoods.lean:90), every `z ∈ U` satisfies `z ≠ 0`, `z ≠ 1`, `Gammaℝ z ≠ 0`, so X5 + `riemannZeta_def_of_ne_zero` + `mul_div_cancel₀` give the pointwise identity

```text
riemannXi z = (z·(z−1)/2 · Gammaℝ z) · riemannZeta z,
```

i.e. `riemannXi =ᶠ[𝓝 s] u * riemannZeta` with `u := fun z => z * (z - 1) / 2 * Gammaℝ z`. The cofactor `u` is analytic at `s` and `u s ≠ 0` (each factor: `hs0`, `sub_ne_zero.mpr hs1`, `two_ne_zero`, `Gammaℝ_ne_zero_of_re_pos h0`). Then

```text
order(ξ) at s = order(u·ζ) at s        [analyticOrderAt_congr]
            = order(u) + order(ζ)      [analyticOrderAt_mul]
            = 0 + order(ζ)             [AnalyticAt.analyticOrderAt_eq_zero, u s ≠ 0]
            = order(ζ).                [zero_add]
```

Analyticity inputs: `ζ` at `s ≠ 1` from `analyticOn_riemannZeta` (RiemannZeta.lean:144, an `AnalyticOnNhd`, applied at `s ∈ {1}ᶜ` via `Set.mem_compl_singleton_iff`, Order/BooleanAlgebra/Set.lean:195). The polynomial part from `analyticAt_id` (Analytic/Linear.lean:156), `analyticAt_const` (Analytic/Constructions.lean:54), `AnalyticAt.sub` (:187), `AnalyticAt.mul` (:639), `AnalyticAt.div_const` (:244). **`Gammaℝ` analyticity has no pinned lemma** — see OBLIGATION X11-G; the assembly path below uses only pinned ingredients.

### Proof skeleton

```lean
theorem analyticOrderAt_riemannXi_eq_riemannZeta {s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) :
    analyticOrderAt riemannXi s = analyticOrderAt riemannZeta s := by
  have hs0 : s ≠ 0 := fun e => by simp [e] at h0
  have hs1 : s ≠ 1 := fun e => by simp [e] at h1
  -- (1) Gammaℝ is analytic on the open right half-plane          (OBLIG X11-G: assembly, no pinned lemma)
  have hHopen : IsOpen {z : ℂ | 0 < z.re} := isOpen_lt continuous_const Complex.continuous_re
  have hGdiff : DifferentiableOn ℂ Gammaℝ {z : ℂ | 0 < z.re} := by
    intro z hz
    have hz2 : ∀ m : ℕ, z / 2 ≠ -m := by
      intro m e
      have h := congrArg Complex.re e
      rw [Complex.div_ofNat_re, Complex.neg_re, Complex.natCast_re] at h   -- OBLIG X11-a
      have : (0 : ℝ) ≤ m := Nat.cast_nonneg m
      have : 0 < z.re := hz
      linarith
    exact (((differentiableAt_id.neg.div_const 2).const_cpow
        (Or.inl (Complex.ofReal_ne_zero.mpr Real.pi_ne_zero))).mul
      (DifferentiableAt.fun_comp' z
        (Complex.differentiableAt_Gamma _ hz2)
        (differentiableAt_id.div_const 2))).differentiableWithinAt
      -- first kernel feedback: the lambda-safe form supplies the explicit point
      -- required by the pinned composition API (FDeriv/Comp.lean:121)
  have hG : AnalyticAt ℂ Gammaℝ s := hGdiff.analyticAt (hHopen.mem_nhds h0)
  -- (2) the nonvanishing analytic cofactor u = fun z => z * (z - 1) / 2 * Gammaℝ z
  have hu : AnalyticAt ℂ (fun z : ℂ => z * (z - 1) / 2 * Gammaℝ z) s :=
    ((analyticAt_id.mul (analyticAt_id.sub analyticAt_const)).div_const).mul hG   -- OBLIG X11-b
  have hu_ne : (fun z : ℂ => z * (z - 1) / 2 * Gammaℝ z) s ≠ 0 :=
    mul_ne_zero (div_ne_zero (mul_ne_zero hs0 (sub_ne_zero.mpr hs1)) two_ne_zero)
      (Complex.Gammaℝ_ne_zero_of_re_pos h0)
  -- (3) zeta is analytic at s (s ≠ 1 inside the strip)
  have hζ : AnalyticAt ℂ riemannZeta s :=
    analyticOn_riemannZeta s (Set.mem_compl_singleton_iff.mpr hs1)
  -- (4) pointwise factorization on the OPEN strip, upgraded to a 𝓝 s eventual equality
  have hstrip : IsOpen {z : ℂ | 0 < z.re ∧ z.re < 1} :=
    (isOpen_lt continuous_const Complex.continuous_re).inter
      (isOpen_lt Complex.continuous_re continuous_const)
  have hfac : riemannXi =ᶠ[𝓝 s]
      (fun z : ℂ => z * (z - 1) / 2 * Gammaℝ z) * riemannZeta := by
    filter_upwards [hstrip.mem_nhds ⟨h0, h1⟩] with z hz
    obtain ⟨hz0, hz1⟩ := hz
    have hz0' : z ≠ 0 := fun e => by simp [e] at hz0
    have hz1' : z ≠ 1 := fun e => by simp [e] at hz1
    have hGz : Gammaℝ z ≠ 0 := Complex.Gammaℝ_ne_zero_of_re_pos hz0
    have hΛ : completedRiemannZeta z = Gammaℝ z * riemannZeta z := by
      rw [riemannZeta_def_of_ne_zero hz0']
      exact (mul_div_cancel₀ _ hGz).symm
    simp only [Pi.mul_apply]
    rw [riemannXi_eq_of_ne hz0' hz1', hΛ]                              -- X5
    ring
  -- (5) order arithmetic
  rw [analyticOrderAt_congr hfac, analyticOrderAt_mul hu hζ,
    hu.analyticOrderAt_eq_zero.mpr hu_ne, zero_add]
```

Anti-pitfall checks specific to X11, verified: the pointwise identity is asserted **only** on the open strip (a genuine neighborhood — never on a boundary point or at `0`, `1`, where the totalized `riemannZeta_def_of_ne_zero` or X5 would fail); `riemannZeta_def_of_ne_zero` is used only under the proved `z ≠ 0`; `Gammaℝ z ≠ 0` comes from `re z > 0`, never from an implicit assumption; `analyticOrderAt_mul` demands `AnalyticAt` for **both** factors — supplied for `u` (constructed) and `ζ` (pinned, `s ≠ 1`); the `f * g` in `analyticOrderAt_mul` is Pi-multiplication, matched by `hfac`'s right-hand side and `Pi.mul_apply` inside the eventual-equality proof.

### Pinned dependencies (X11)

X5; `analyticOrderAt` (Analysis/Analytic/Order.lean:47), `analyticOrderAt_congr` (:175), `analyticOrderAt_mul` (:497), `AnalyticAt.analyticOrderAt_eq_zero` (:133); `analyticOn_riemannZeta` (RiemannZeta.lean:144), `riemannZeta_def_of_ne_zero` (:152); `Complex.Gammaℝ_ne_zero_of_re_pos` (Deligne.lean:66), `Complex.Gammaℝ` (:43); `DifferentiableOn.analyticAt` (Analysis/Complex/CauchyIntegral.lean:625); `Complex.differentiableAt_Gamma` (Gamma/Deriv.lean:65); `DifferentiableAt.const_cpow` (Pow/Deriv.lean:111); `differentiableAt_id` (FDeriv/Basic.lean:697), `DifferentiableAt.neg` (FDeriv/Add.lean:544), `DifferentiableAt.mul` (FDeriv/Mul.lean:217), `DifferentiableAt.div_const` (Deriv/Mul.lean:576), `DifferentiableAt.comp` (FDeriv/Comp.lean:127); `analyticAt_id` (Analytic/Linear.lean:156), `analyticAt_const` (Analytic/Constructions.lean:54), `AnalyticAt.sub` (:187), `AnalyticAt.mul` (:639), `AnalyticAt.div_const` (:244); `isOpen_lt` (Topology/Order/OrderClosed.lean:556), `Complex.continuous_re` (Analysis/Complex/Basic.lean:153), `IsOpen.mem_nhds` (Topology/Neighborhoods.lean:90), `Set.mem_compl_singleton_iff` (Order/BooleanAlgebra/Set.lean:195); `mul_div_cancel₀` (Algebra/GroupWithZero/Units/Basic.lean:458), `div_ne_zero` (:284), `mul_ne_zero` (Algebra/GroupWithZero/Basic.lean:84), `two_ne_zero` (Algebra/NeZero.lean:36), `sub_ne_zero` (Algebra/Group/Basic.lean:753, to_additive), `Complex.div_ofNat_re` (Data/Complex/Basic.lean:763), `Complex.neg_re` (:184), `Complex.natCast_re` (:356), `Complex.ofReal_ne_zero` (:140), `Real.pi_ne_zero` (Trigonometric/Basic.lean:165), `Pi.mul_apply`/`zero_add`/`Nat.cast_nonneg` (core).

### Obligations (X11)

- **OBLIGATION X11-G (MEDIUM — the package's only genuinely missing interface):** there is **no pinned lemma** asserting differentiability or analyticity of `Gammaℝ` (grep-confirmed: only `differentiable_Gammaℝ_inv`, Deligne.lean:88, the inverse). The skeleton assembles it from pinned parts: `Gammaℝ = fun s => π ^ (-s/2) * Gamma (s/2)` (`Gammaℝ_def` is `rfl`, Deligne.lean:45), the cpow factor via `DifferentiableAt.const_cpow` with `(π : ℂ) ≠ 0`, the Gamma factor via `Complex.differentiableAt_Gamma` at `z/2` (pole-free since `re(z/2) > 0`), then `DifferentiableOn.analyticAt` on the open half-plane. All ingredients pinned; estimate 10–15 lines; the unfolding `Gammaℝ_def` step may need an explicit `simp only [Complex.Gammaℝ_def]`/`show` to expose the product to the two `DifferentiableAt` constructors. No analytic gap — this is assembly cost, not a missing theorem. (Upstreaming a `differentiableAt_Gammaℝ_of_re_pos` to Mathlib is the natural follow-up but is not assumed.)
- **OBLIGATION X11-a (LOW):** the `re`-computation `z / 2 ≠ -m` from `0 < re z`: essentially discharged by the pinned `Complex.div_ofNat_re` (Data/Complex/Basic.lean:763, `(z / OfNat n).re = z.re / n`) + `neg_re`/`natCast_re` + `linarith`; exact simp form to be fixed in build.
- **OBLIGATION X11-b (MEDIUM):** elaboration shapes: `analyticAt_id` is stated for `id`, not `fun z => z`; `AnalyticAt.div_const` is stated as `(f · / c)`; `analyticOrderAt_mul`'s `f * g` is Pi-mul against the lambda in `hfac`; review fix F3 adds two more registered shapes — (a) `hstrip` is built as `IsOpen (A ∩ B)` via `.inter` while the goal set is the set-builder `{z | 0 < z.re ∧ z.re < 1}` (defeq, not syntactic; fallback `show IsOpen ({z : ℂ | 0 < z.re} ∩ {z : ℂ | z.re < 1})`), and (b) `differentiableAt_id.neg` produces the Pi-neg `(-id)` which must defeq-match the exponent `fun z => -z / 2` inside `const_cpow`. The former composition-shape risk is discharged by the kernel-confirmed point-explicit `DifferentiableAt.fun_comp'`. Fallback for `hu` if still fragile: prove `DifferentiableOn ℂ (fun z => z * (z - 1) / 2 * Gammaℝ z) {z | 0 < z.re}` in one stroke (polynomial part differentiable everywhere + `hGdiff`) and apply `DifferentiableOn.analyticAt` once, avoiding the `AnalyticAt` constructor chain entirely.
- No analytic obligation: every analytic input (entirety of `Λ₀`, analyticity of `ζ` off 1, differentiability of `Gamma` off the poles, Cauchy–Goursat analyticity upgrade, order product law) is a quoted pinned theorem.

---

## Pinned API dependencies table

All paths relative to the pinned Mathlib tree; all line numbers grep-verified this session at `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`.

| declaration | file:line | used in |
|---|---|---|
| `RiemannHypothesis` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:182 | X10 |
| `riemannZeta` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:119 | X6–X11 |
| `completedRiemannZeta₀` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:63 | X1 (definition body) |
| `completedRiemannZeta` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:67 | X5, X6, X11 |
| `completedRiemannZeta_eq` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:84 | X5 (sign source of truth) |
| `differentiable_completedZeta₀` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:89 | X2 |
| `completedRiemannZeta₀_one_sub` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:99 | X3 |
| `analyticOn_riemannZeta` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:144 | X11 |
| `riemannZeta_def_of_ne_zero` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:152 | X6, X11 |
| `riemannZeta_neg_two_mul_nat_add_one` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:171 | statement-form alignment (review only) |
| `riemannZeta_ne_zero_of_one_le_re` | Mathlib/NumberTheory/LSeries/Nonvanishing.lean:410 | X7 |
| `riemannZeta_one` | Mathlib/NumberTheory/Harmonic/ZetaAsymp.lean:408 | context (X7 design note) |
| `riemannZeta_one_ne_zero` | Mathlib/NumberTheory/Harmonic/ZetaAsymp.lean:431 | context (X7 design note) |
| `Complex.Gammaℝ` | Mathlib/Analysis/SpecialFunctions/Gamma/Deligne.lean:43 | X6, X11 |
| `Complex.Gammaℝ_def` | Mathlib/Analysis/SpecialFunctions/Gamma/Deligne.lean:45 | X11 (OBLIG X11-G unfolding) |
| `Complex.Gammaℝ_ne_zero_of_re_pos` | Mathlib/Analysis/SpecialFunctions/Gamma/Deligne.lean:66 | X11 |
| `Complex.Gammaℝ_eq_zero_iff` | Mathlib/Analysis/SpecialFunctions/Gamma/Deligne.lean:73 | X6 (reverse direction, load-bearing) |
| `Complex.differentiable_Gammaℝ_inv` | Mathlib/Analysis/SpecialFunctions/Gamma/Deligne.lean:88 | cited as confirmed-insufficient (X11-G) |
| `analyticOrderAt` | Mathlib/Analysis/Analytic/Order.lean:47 | X11 |
| `analyticOrderNatAt` | Mathlib/Analysis/Analytic/Order.lean:61 | deferred corollary note only |
| `AnalyticAt.analyticOrderAt_eq_zero` | Mathlib/Analysis/Analytic/Order.lean:133 | X11 |
| `analyticOrderAt_congr` | Mathlib/Analysis/Analytic/Order.lean:175 | X11 |
| `analyticOrderAt_mul` | Mathlib/Analysis/Analytic/Order.lean:497 | X11 |
| `analyticOrderNatAt_mul` | Mathlib/Analysis/Analytic/Order.lean:502 | deferred corollary note only |
| `AnalyticAt.analyticOrderAt_ne_top` | Mathlib/Analysis/Analytic/Order.lean:113 | deferred corollary note only |
| `DifferentiableOn.analyticAt` | Mathlib/Analysis/Complex/CauchyIntegral.lean:625 | X11 |
| `Complex.differentiableAt_Gamma` | Mathlib/Analysis/SpecialFunctions/Gamma/Deriv.lean:65 | X11 |
| `DifferentiableAt.const_cpow` | Mathlib/Analysis/SpecialFunctions/Pow/Deriv.lean:111 | X11 |
| `differentiableAt_id` | Mathlib/Analysis/Calculus/FDeriv/Basic.lean:697 | X11 |
| `differentiable_id` | Mathlib/Analysis/Calculus/FDeriv/Basic.lean:708 | X2 |
| `differentiable_const` | Mathlib/Analysis/Calculus/FDeriv/Const.lean:243 | X2 |
| `Differentiable.add` | Mathlib/Analysis/Calculus/FDeriv/Add.lean:227 | X2 |
| `DifferentiableAt.neg` | Mathlib/Analysis/Calculus/FDeriv/Add.lean:544 | X11 |
| `Differentiable.sub` | Mathlib/Analysis/Calculus/FDeriv/Add.lean:688 | X2 |
| `DifferentiableAt.mul` | Mathlib/Analysis/Calculus/FDeriv/Mul.lean:217 | X11 |
| `Differentiable.mul` | Mathlib/Analysis/Calculus/FDeriv/Mul.lean:226 | X2 |
| `DifferentiableAt.div_const` | Mathlib/Analysis/Calculus/Deriv/Mul.lean:576 | X11 |
| `Differentiable.div_const` | Mathlib/Analysis/Calculus/Deriv/Mul.lean:585 | X2 |
| `DifferentiableAt.comp` | Mathlib/Analysis/Calculus/FDeriv/Comp.lean:127 | X11 |
| `analyticAt_id` | Mathlib/Analysis/Analytic/Linear.lean:156 | X11 |
| `analyticAt_const` | Mathlib/Analysis/Analytic/Constructions.lean:54 | X11 |
| `AnalyticAt.sub` | Mathlib/Analysis/Analytic/Constructions.lean:187 | X11 |
| `AnalyticAt.div_const` | Mathlib/Analysis/Analytic/Constructions.lean:244 | X11 |
| `AnalyticAt.mul` | Mathlib/Analysis/Analytic/Constructions.lean:639 | X11 |
| `isOpen_lt` | Mathlib/Topology/Order/OrderClosed.lean:556 | X11 |
| `Complex.continuous_re` | Mathlib/Analysis/Complex/Basic.lean:153 | X11 |
| `IsOpen.mem_nhds` | Mathlib/Topology/Neighborhoods.lean:90 | X11 |
| `Set.mem_compl_singleton_iff` | Mathlib/Order/BooleanAlgebra/Set.lean:195 | X11 |
| `mul_ne_zero` | Mathlib/Algebra/GroupWithZero/Basic.lean:84 | X11 |
| `zero_div` | Mathlib/Algebra/GroupWithZero/Basic.lean:388 | X6 alternative form (unused in final skeleton) |
| `div_ne_zero` | Mathlib/Algebra/GroupWithZero/Units/Basic.lean:284 | X11 |
| `div_eq_zero_iff` | Mathlib/Algebra/GroupWithZero/Units/Basic.lean:289 | X6 |
| `mul_div_cancel₀` | Mathlib/Algebra/GroupWithZero/Units/Basic.lean:458 | X5 (paper), X11 |
| `mul_eq_zero` | Mathlib/Algebra/GroupWithZero/Defs.lean:304 | X6 |
| `two_ne_zero` | Mathlib/Algebra/NeZero.lean:36 | X5, X6, X11 |
| `sub_ne_zero` | Mathlib/Algebra/Group/Basic.lean:753 (to_additive of `div_ne_one`) | X5, X6, X11 |
| `sub_eq_zero` | Mathlib/Algebra/Group/Basic.lean:745 (to_additive of `div_eq_one`) | review alternative (unused in final skeleton) |
| `Complex.zero_re` | Mathlib/Data/Complex/Basic.lean:125 | X7, X10 |
| `Complex.ofReal_ne_zero` | Mathlib/Data/Complex/Basic.lean:140 | X11 |
| `Complex.one_re` | Mathlib/Data/Complex/Basic.lean:147 | X8, X10 |
| `Complex.neg_re` | Mathlib/Data/Complex/Basic.lean:184 | X11 |
| `Complex.natCast_re` | Mathlib/Data/Complex/Basic.lean:356 | X11 |
| `Complex.sub_re` | Mathlib/Data/Complex/Basic.lean:640 | X8 |
| `Complex.div_ofNat_re` | Mathlib/Data/Complex/Basic.lean:763 | X11 (discharges X11-a core) |
| `Real.pi_ne_zero` | Mathlib/Analysis/SpecialFunctions/Trigonometric/Basic.lean:165 | X11 |
| `Nat.cast_nonneg`, `not_lt`, `zero_add`, `Pi.mul_apply`, `mul_zero`, `zero_mul`, `sub_self` | (core API, bridge-precedent no-locator glue) | X4, X6, X7, X9, X10, X11 |
| **bridge P2** `riemannZeta_zero_mem_critical_strip` | TARGET_BRIDGE_CONTRACT.md §P2 (package prerequisite, NOT pinned Mathlib) | X10 reverse |

## Anti-pitfall compliance (repo contracts, mirrored from the bridge)

- **Exact trivial-zero form:** every exclusion is literally `¬∃ n : ℕ, s = -2 * (n + 1)`, character-identical to `RiemannHypothesis` (RiemannZeta.lean:182). The strictly larger `Gammaℝ` zero set `-(2*n)` (which contains `0`) is decomposed **exactly once**, in X6, as `{0} ∪ {-2(n+1)}`, with `hs0` covering the first component and `htriv` the second — never conflated.
- **Totalized values:** `ξ(0)`, `ξ(1)` are read from the entire formula (X4), never from a totalized pointwise product; `riemannZeta_def_of_ne_zero` is applied only under proved `≠ 0` (X6, X11); X5's exclusions are exactly the appearing denominators; the X11 factorization lives strictly inside the open strip.
- **Signs from `completedRiemannZeta_eq` the theorem:** the whole sign chain is derived once in §Sign derivation from RiemannZeta.lean:84 and re-checked by X4's endpoint values; the conflicting module comment is never used.
- **No competing definitions:** `riemannXi` is the sole new object introduced by this package (Gate-0 normalization verbatim); X10's left side is `_root_.RiemannHypothesis` verbatim; no new `Prop` restates RH.
- **No conjugation symmetry, no Euler product, no multiplicity beyond local order:** verified per-statement; X11 transports `analyticOrderAt` only and constructs no divisor (per `S1-MULTIPLICITY`, the divisor/symmetry package is a separate later contract).
- **Name collisions:** zero `riemannXi*` hits at the pin (grep-verified this session).

## Pre-kernel obligation register (v2 historical summary)

| id | severity | content |
|---|---|---|
| X2-a | LOW | `id` vs `fun s => s` defeq shapes in the `Differentiable` chain (no `differentiable_id'` at pin) |
| X4-a | LOW | exact `norm_num`/`simp` set for the endpoint values |
| X5-a | MEDIUM | exact `field_simp`+`ring` (or `linear_combination` coefficient) for the sign chain; pure field algebra |
| X6-a | LOW | `ℕ → ℂ` cast witness `-(2*↑(m+1)) = -2*(↑m+1)` and the `n = 0` branch |
| X7-a / X10-a | LOW | `((-2 : ℂ)*(↑n+1)).re = -2*(n+1)` cast form (identical to bridge P2-a/P4-a; shared discharge) |
| X10-b | LOW | `RiemannHypothesis` def-unfolding via `intro`/application (identical to bridge P4-b/P5-a) |
| X11-G | MEDIUM | **no pinned `Gammaℝ` differentiability/analyticity lemma exists** (only `differentiable_Gammaℝ_inv`, Deligne.lean:88); assemble from `differentiableAt_Gamma` (Gamma/Deriv.lean:65) + `DifferentiableAt.const_cpow` (Pow/Deriv.lean:111) + `DifferentiableOn.analyticAt` (CauchyIntegral.lean:625); ~10–15 lines, all ingredients pinned, no analytic gap |
| X11-a | LOW | `z/2 ≠ -m` from `0 < re z`; core discharged by pinned `Complex.div_ofNat_re` (Data/Complex/Basic.lean:763) |
| X11-b | MEDIUM | elaboration shapes (Pi-mul vs lambda, `AnalyticAt.div_const` eta, `analyticAt_id`); fallback: one-shot `DifferentiableOn.analyticAt` for the whole cofactor on the half-plane |

No obligation was analytic. Every analytic input — entirety of `Λ₀`, the `Λ₀` functional equation, `Λ = Λ₀ − 1/s − 1/(1−s)`, analyticity of `ζ` off `1`, `Gamma` differentiability off its poles, the Cauchy–Goursat analyticity upgrade, the `Gammaℝ` and `Gamma` zero classifications, closed-half-plane zeta nonvanishing, and the analytic-order congruence/product/unit laws — is a quoted pinned theorem at `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`. The merged built counterpart in PR #304 kernel-checked these obligations after independent review, bridge P1–P5 landing, and closure of the carried preconditions; the contract itself remains the retained specification artifact.

---

## ANNEX B: adversarial review record (2026-08-05)

An independent adversarial reviewer attempted to refute draft v1 against the
pinned tree and the repo contracts. Verdict: **`SOUND_WITH_FIXES`** — all
~60 cited declarations exist at the exact claimed `file:line` with matching
signatures (one usage-level exception, F1); the X5 sign chain was
independently re-derived from `completedRiemannZeta_eq` with **no sign
discrepancy** (`s(s−1)·Λ = s(s−1)·Λ₀ + 1` under `s ≠ 0,1`); X6's zero-set
decomposition `{−2n} = {0} ∪ {−2(m+1)}` verified exhaustive and
non-overlapping, matching `Gammaℝ_eq_zero_iff` exactly (the pinned tree
itself uses the same rewrite idiom at Deligne.lean:165-166); X11's order
API claims verified (`analyticOrderAt_congr` :175, `analyticOrderAt_mul`
:497 with both `AnalyticAt` hypotheses supplied, factorization asserted
only as an `=ᶠ[𝓝 s]` equality on the open strip); no competing RH
proposition, no conjugation use, no growth/Hadamard/Li leakage; and the
grep-confirmed absence of any `Gammaℝ` differentiability lemma validates
OBLIGATION X11-G as the package's only genuinely missing interface.
Findings, all severity S2: **F1** historically recorded
`DifferentiableAt.comp` as taking no explicit point; the first promotion
kernel pass refuted that usage-level claim and Annex C records the repair.
**F2** found that the advertised `linear_combination` fallback for X5 could
not close without denominator-clearing (obligation reworded), **F3** folded
two uncovered defeq-shape risks into X11-b, and **F4** corrected a cosmetic
locator range.

## ANNEX C: first promotion kernel feedback (2026-08-06)

The first built promotion head elaborated through X10 and reached X11, where
the Gamma composition call

```lean
(Complex.differentiableAt_Gamma _ hz2).comp
  (differentiableAt_id.div_const 2)
```

failed because the pinned composition API's section point is explicit. The
statement-preserving repair uses the lambda-safe constructor with that point:

```lean
DifferentiableAt.fun_comp' z
  (Complex.differentiableAt_Gamma _ hz2)
  (differentiableAt_id.div_const 2)
```

A narrow kernel build confirmed the repaired X1-X11 module. The built file,
draft, and this proof skeleton carry the same repair. The repaired PR #304 head
then passed the full repository build and both axiom audits and was merged as
`afdae08`. No declaration name, binder, hypothesis, conclusion, or claim
boundary changed.
