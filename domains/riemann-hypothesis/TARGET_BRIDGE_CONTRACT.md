# RH-003 frozen theorem contract: route-neutral target bridge

Status: **DRAFT v2 (2026-08-05) — non-built review artifact, adversarially
reviewed once (verdict `SOUND_WITH_FIXES`, all five findings applied below;
see Annex B). Not Lean-checked. No file in `Ecdlp/`, `ResearchOS/`, or any
built target may be created from this document before independent review
(RH-003 exit) and `S0-TRUST` closure.**

Scope: the package designated by `MATHLIB_CAPABILITY_MAP.md` §"First
implementable foundation and stop rule": *"After `S0-TRUST` is closed, the
first Lean PR should contain only the route-neutral target-equivalence
bridge."* This is the "Cross-route target bridge" DAG node only. It contains
no xi definition (Annex A lists the A/C follow-on statements only), no Li
coefficients, no zero enumeration, no multiplicity API, and no claim of
progress on RH.

Pinned Mathlib: `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0). Every
declaration cited below was grep-verified at that exact revision by two
independent agents; all `file:line` locators are from that tree.

## RH-002/RH-003 candidate fields

- **Mechanism.** The pinned functional equation `riemannZeta_one_sub`
  (instantiated at `s := 1 − σ`), the unconditional completed-zeta symmetry
  `completedRiemannZeta_one_sub`, the closed-half-plane nonvanishing
  `riemannZeta_ne_zero_of_one_le_re`, and the Gamma/cos/cpow zero
  classifications jointly determine the exact nontrivial-zero domain of the
  totalized `riemannZeta` and make the three classical formulations of RH
  (Mathlib target; zero-free `re > 1/2`; critical-line via the zero set)
  provably equivalent — with every exceptional point handled explicitly.
- **Expected information gain.** Closes the named barrier `S1-TARGET` (the
  route-neutral gate every admitted route needs); converts the map's
  `NOT-FOUND` row "critical-strip localization" into a theorem; hardens the
  `S0-SEMANTIC` boundary (totalized values, trivial-zero form, Gammaℝ zero
  set) into kernel-checked facts instead of conventions. No information
  about the truth of RH is produced.
- **Claim boundary.** All five theorems are unconditional consequences of
  pinned Mathlib theorems; none touches multiplicity, growth, zero counting,
  or any route's research obligation. The equivalences are admissible under
  corpus rule "equivalent restatements are not progress unless they remove a
  named barrier" — they remove `S1-TARGET` and nothing else.
- **Death condition (stop rule).** Stop or split the package if any proof
  obligation cannot be discharged without weakening an exclusion, assuming a
  hidden nonvanishing fact, or treating a totalized exceptional value as a
  meromorphic value. A clean blocker is preferable to a false bridge.

## Review preconditions (carried from RH-001/RH-002 closure)

1. Independent reviewer confirms each Lean statement against this contract
   and against the map's semantic-mismatch register.
2. `S0-TRUST` closes (non-ECDLP result ledger + generated axiom audit) before
   any built `.lean` exists.
3. The `SOURCE_CONTRACTS.md` package acceptance review (against the
   SHA-256-pinned PDFs) — pending from RH-001's scoped carve-out — is not a
   blocker for this route-neutral package (which cites no external PDF), but
   must complete before any Annex A xi work that touches `LAG07` conventions.

## Scope note (adversarial-review finding F5, resolved)

P1-P2 derive critical-strip localization **FE-first** (from
`riemannZeta_one_sub`), inside this bridge package, while the map's
missing-interface row said localization would be "derived with the xi
bridge". The FE-first derivation is required: P4's reverse direction cannot
close without strip localization plus reflection, and the map's own
"Cross-route target bridge" DAG already lists "exact nontrivial-zero domain"
as a bridge output. The map carries a dated addendum reconciling this; the
xi package (Annex A) still proves its own xi-side localization. This scope
decision requires explicit RH-003 reviewer acknowledgment.

Canonical target (never restated, never replaced) —
`Mathlib/NumberTheory/LSeries/RiemannZeta.lean:182`:

```lean
def RiemannHypothesis : Prop :=
  ∀ (s : ℂ) (_ : riemannZeta s = 0) (_ : ¬∃ n : ℕ, s = -2 * (n + 1)) (_ : s ≠ 1), s.re = 1 / 2
```

Proposed module preamble for the eventual built file (recorded here for
name-resolution review only):

```lean
import Mathlib.NumberTheory.LSeries.ZetaZeros          -- riemannZetaZeros, Nonvanishing (transitively)
import Mathlib.NumberTheory.Harmonic.ZetaAsymp          -- riemannZeta_one, riemannZeta_one_ne_zero
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Complex  -- Complex.cos_eq_zero_iff

open Complex
open scoped Real
```

---

## 0. Exact pinned functional-equation interface (quoted literally)

The pinned `riemannZeta_one_sub` does **not** have the classical
`2^s π^(s-1) sin(πs/2) Γ(1-s)` shape. At `RiemannZeta.lean:176`, quoted
exactly:

```lean
theorem riemannZeta_one_sub {s : ℂ} (hs : ∀ n : ℕ, s ≠ -n) (hs' : s ≠ 1) :
    riemannZeta (1 - s) = 2 * (2 * π) ^ (-s) * Gamma s * cos (π * s / 2) * riemannZeta s
```

Exact hypotheses: `hs : ∀ n : ℕ, s ≠ -n` (excludes `s = 0` via `n = 0`, and
all negative integers) and `hs' : s ≠ 1`. Exact conclusion prefactor:
`2 * (2 * π) ^ (-s) * Gamma s * cos (π * s / 2)` (the docstring's
`sin (π * (1 - s) / 2)` equals `cos (π * s / 2)` — the **theorem** term is
authoritative, per the repo rule of deriving from theorems, not comments).
The equation produces `ζ(1 - s)` from `ζ(s)`; the package below instantiates
it at `s := 1 - σ` to express `ζ(σ)` on the left.

Supporting pinned quotes:

```lean
-- Nonvanishing.lean:410 (namespace DirichletCharacter; note the _root_ prefix and STRICT-implicit ⦃s⦄)
lemma _root_.riemannZeta_ne_zero_of_one_le_re ⦃s : ℂ⦄ (hs : 1 ≤ s.re) : riemannZeta s ≠ 0

-- RiemannZeta.lean:149
theorem riemannZeta_zero : riemannZeta 0 = -1 / 2

-- Harmonic/ZetaAsymp.lean:408 and :431 (totalized value at the pole IS known and IS nonzero)
lemma riemannZeta_one : riemannZeta 1 = (γ - log (4 * π)) / 2
lemma riemannZeta_one_ne_zero : riemannZeta 1 ≠ 0

-- RiemannZeta.lean:152
lemma riemannZeta_def_of_ne_zero {s : ℂ} (hs : s ≠ 0) :
    riemannZeta s = completedRiemannZeta s / Gammaℝ s

-- RiemannZeta.lean:105
theorem completedRiemannZeta_one_sub (s : ℂ) :
    completedRiemannZeta (1 - s) = completedRiemannZeta s

-- RiemannZeta.lean:84 (sign source of truth; the module comment disagrees — theorem wins)
lemma completedRiemannZeta_eq (s : ℂ) :
    completedRiemannZeta s = completedRiemannZeta₀ s - 1 / s - 1 / (1 - s)

-- Gamma/Deligne.lean:66 and :73 (namespace Complex). NOTE: Gammaℝ vanishes at s = -(2*n),
-- which INCLUDES s = 0 (n = 0) — a strictly larger set than the trivial-zero form -2*(n+1).
lemma Gammaℝ_ne_zero_of_re_pos {s : ℂ} (hs : 0 < re s) : Gammaℝ s ≠ 0
lemma Gammaℝ_eq_zero_iff {s : ℂ} : Gammaℝ s = 0 ↔ ∃ n : ℕ, s = -(2 * n)

-- Gamma/Beta.lean:427, :447, :453 (namespace Complex)
theorem Gamma_ne_zero {s : ℂ} (hs : ∀ m : ℕ, s ≠ -m) : Gamma s ≠ 0
theorem Gamma_eq_zero_iff (s : ℂ) : Gamma s = 0 ↔ ∃ m : ℕ, s = -m
theorem Gamma_ne_zero_of_re_pos {s : ℂ} (hs : 0 < re s) : Gamma s ≠ 0

-- Trigonometric/Complex.lean:33 (namespace Complex); the pinned prefactor uses cos.
theorem cos_eq_zero_iff {θ : ℂ} : cos θ = 0 ↔ ∃ k : ℤ, θ = (2 * k + 1) * π / 2

-- Pow/Complex.lean:45 (namespace Complex)
theorem cpow_eq_zero_iff (x y : ℂ) : x ^ y = 0 ↔ x = 0 ∧ y ≠ 0

-- ZetaZeros.lean:33 and :35
def riemannZetaZeros : Set ℂ := riemannZeta ⁻¹' {0}
lemma mem_riemannZetaZeros {z : ℂ} : z ∈ riemannZetaZeros ↔ riemannZeta z = 0 := .rfl
```

---

## P1. Lower exclusion: no zeros in `re ≤ 0` except the trivial ones

### Statement

```lean
theorem riemannZeta_ne_zero_of_re_le_zero {s : ℂ} (hs : s.re ≤ 0)
    (htriv : ¬∃ n : ℕ, s = -2 * (n + 1)) : riemannZeta s ≠ 0
```

The trivial-zero exclusion is stated in the **exact** target form
`¬∃ n : ℕ, s = -2 * (n + 1)`, matching `RiemannHypothesis` and
`riemannZeta_neg_two_mul_nat_add_one` (`RiemannZeta.lean:171`) verbatim.
Note `s = 0` is *not* excluded by `htriv` (trivial zeros start at `-2`) and
is handled by the totalized value `riemannZeta_zero : ζ(0) = -1/2`.

### Exact vanishing analysis of the pinned prefactor (instantiated at `s := 1 - σ`, `σ.re ≤ 0`, `σ ≠ 0`)

The functional equation gives
`ζ(σ) = 2 * (2π)^(-(1-σ)) * Gamma (1-σ) * cos (π*(1-σ)/2) * ζ(1-σ)`, with
`re(1-σ) = 1 - σ.re ≥ 1`. Factor by factor:

| factor | can it vanish? | discharge |
|---|---|---|
| `2` | never | `two_ne_zero` |
| `(2*π) ^ (-(1-σ))` | never: `cpow` vanishes only for base `0` (`Complex.cpow_eq_zero_iff`), and `(2*π : ℂ) ≠ 0` | `mul_ne_zero two_ne_zero (ofReal_ne_zero.mpr Real.pi_ne_zero)` |
| `Gamma (1-σ)` | only at `1-σ = -m` (`Complex.Gamma_eq_zero_iff`), i.e. `σ = m+1`, `re = m+1 ≥ 1` — impossible for `σ.re ≤ 0` | `Complex.Gamma_ne_zero_of_re_pos`, since `re(1-σ) ≥ 1 > 0` |
| `cos (π*(1-σ)/2)` | **the load-bearing factor.** Vanishes iff `π*(1-σ)/2 = (2k+1)*π/2`, `k : ℤ` (`Complex.cos_eq_zero_iff`), iff `1-σ = 2k+1`, iff `σ = -2k`. On `σ.re ≤ 0` this forces `k ≥ 0`; `k = 0` is `σ = 0` (already split off); `k ≥ 1` is exactly `σ = -2*((k-1)+1)`, the excluded trivial zero | contradiction with `hσ0` / `htriv` |
| `ζ(1-σ)` | never on `re ≥ 1`, including the totalized point `1` | `riemannZeta_ne_zero_of_one_le_re` (closed half-plane, `Nonvanishing.lean:410`) |

So the exclusions `σ ≠ 0` (case split) and `htriv` are exactly what kills
the unique vanishing channel (`cos`), and no other factor can vanish
anywhere in `re ≤ 0`. In particular the line `re = 0` is completely covered:
for `σ ≠ 0` on that line the `cos` factor would need `σ = -2k` with `k ≥ 1`,
impossible at `re = 0`; `ζ(1-σ)` sits on `re = 1` where the closed-half-plane
theorem holds.

### Proof skeleton (v2 — review fixes F1, F2 applied)

```lean
theorem riemannZeta_ne_zero_of_re_le_zero {s : ℂ} (hs : s.re ≤ 0)
    (htriv : ¬∃ n : ℕ, s = -2 * (n + 1)) : riemannZeta s ≠ 0 := by
  rcases eq_or_ne s 0 with rfl | hs0
  · -- totalized value at 0
    rw [riemannZeta_zero]; norm_num
  · have hw_re : 1 ≤ (1 - s).re := by rw [Complex.sub_re, Complex.one_re]; linarith
    -- hypothesis hs of riemannZeta_one_sub at s := 1 - s, by real parts
    have hw_nat : ∀ n : ℕ, (1 : ℂ) - s ≠ -n := by
      intro n h
      have h' := congrArg Complex.re h
      rw [Complex.sub_re, Complex.one_re, Complex.neg_re, Complex.natCast_re] at h'
      have : (0 : ℝ) ≤ n := n.cast_nonneg
      linarith
    -- hypothesis hs' of riemannZeta_one_sub at s := 1 - s
    have hw_ne_one : (1 : ℂ) - s ≠ 1 := fun h => hs0 (by linear_combination -h)
    have hFE := riemannZeta_one_sub hw_nat hw_ne_one
    rw [show (1 : ℂ) - (1 - s) = s by ring] at hFE
    rw [hFE]
    refine mul_ne_zero (mul_ne_zero (mul_ne_zero (mul_ne_zero two_ne_zero ?_) ?_) ?_) ?_
    · -- (2 * π) ^ (-(1 - s)) ≠ 0
      simp only [ne_eq, Complex.cpow_eq_zero_iff, not_and_or, not_not]
      exact Or.inl (mul_ne_zero two_ne_zero (Complex.ofReal_ne_zero.mpr Real.pi_ne_zero))
    · -- Gamma (1 - s) ≠ 0                                     (fix F1)
      exact Complex.Gamma_ne_zero_of_re_pos (one_pos.trans_le hw_re)
    · -- cos (π * (1 - s) / 2) ≠ 0 : the only genuine vanishing channel
      intro hcos
      obtain ⟨k, hk⟩ := Complex.cos_eq_zero_iff.mp hcos
      have hπ : (π : ℂ) ≠ 0 := Complex.ofReal_ne_zero.mpr Real.pi_ne_zero
      -- cancel π/2 : π * (1 - s) / 2 = (2k+1) * π / 2  ⟹  s = -2k        (OBLIG P1-c)
      have hs_eq : s = -2 * (k : ℂ) := by
        field_simp at hk
        linear_combination (2 / (π : ℂ)) * hk   -- exact incantation to be fixed in build
      -- real part: -2k ≤ 0 ⟹ 0 ≤ k; s ≠ 0 ⟹ k ≠ 0 ⟹ 1 ≤ k             (OBLIG P1-d)
      have hk_re : s.re = -2 * (k : ℝ) := by
        rw [hs_eq]; simp [Complex.mul_re, Complex.intCast_re, Complex.intCast_im]
      have hk0 : 0 ≤ k := by
        by_contra hneg
        push_neg at hneg
        have : (0 : ℝ) < s.re := by
          rw [hk_re]; have : (k : ℝ) < 0 := by exact_mod_cast hneg
          nlinarith
        linarith
      have hkne : k ≠ 0 := by                                  -- (fix F2)
        rintro rfl
        exact hs0 (by simpa using hs_eq)
      have hk1 : 1 ≤ k := by omega
      -- produce the exact trivial-zero witness
      exact htriv ⟨(k - 1).toNat, by
        rw [hs_eq]
        push_cast [Int.toNat_of_nonneg (by omega : (0 : ℤ) ≤ k - 1)]
        ring⟩
    · -- ζ(1 - s) ≠ 0 on the closed right half-plane
      exact riemannZeta_ne_zero_of_one_le_re hw_re
```

### Pinned dependencies (P1)

`riemannZeta_zero` (RiemannZeta.lean:149), `riemannZeta_one_sub` (:176),
`riemannZeta_ne_zero_of_one_le_re` (Nonvanishing.lean:410),
`Complex.Gamma_ne_zero_of_re_pos` (Beta.lean:453), `Complex.cos_eq_zero_iff`
(Trigonometric/Complex.lean:33), `Complex.cpow_eq_zero_iff`
(Pow/Complex.lean:45), `Real.pi_ne_zero` (Trigonometric/Basic.lean:165),
`Complex.ofReal_ne_zero` (Data/Complex/Basic.lean:140),
`Complex.sub_re`/`one_re`/`neg_re`/`natCast_re`
(Data/Complex/Basic.lean:640/147/184/356), `Complex.intCast_re`/`intCast_im`
(Data/Complex/Basic.lean:358/359), `mul_ne_zero`
(Algebra/GroupWithZero/Basic.lean:84), `Int.toNat_of_nonneg`.

### Obligations (P1)

- **OBLIGATION P1-c (MEDIUM):** algebraic cancellation
  `π * (1 - s) / 2 = (2*k + 1) * π / 2 ⟹ s = -2*k` in `ℂ` using `hπ`. Pure
  field algebra (`field_simp` + `linear_combination`/`mul_left_cancel₀`),
  but the exact tactic term must be fixed against the kernel; the skeleton's
  `linear_combination` coefficient is a placeholder.
- **OBLIGATION P1-d (LOW):** `ℤ → ℕ → ℂ` cast bookkeeping for the witness
  `(k - 1).toNat` and the identity `-2 * (((k-1).toNat : ℂ) + 1) = -2 * k`
  under `1 ≤ k`; `push_cast`+`omega`+`ring`. The `hk0` derivation above is
  spelled out longhand; a build may compress it.
- P1-e (the `Gamma` glue-term shape) — **resolved in v2** by fix F1.
- No analytic obligation remains: every nonvanishing input is a pinned
  theorem.

---

## P2. Critical-strip localization of nontrivial zeros

### Statement

```lean
theorem riemannZeta_zero_mem_critical_strip {s : ℂ} (hz : riemannZeta s = 0)
    (htriv : ¬∃ n : ℕ, s = -2 * (n + 1)) : 0 < s.re ∧ s.re < 1
```

**Design note.** P1 excludes the *closed* half-plane `re ≤ 0` (not merely
`re < 0`): the line `re = 0` carries no zeta zeros at all — `s = 0` because
`ζ(0) = -1/2`, and `s ≠ 0` with `re s = 0` because the reflection lands on
`re(1-s) = 1` where `riemannZeta_ne_zero_of_one_le_re` holds *including* the
totalized point (its proof at Nonvanishing.lean:412-414 splits on `s = 1`
and uses `riemannZeta_one_ne_zero`), and the cos factor cannot vanish off
the real axis. Hence the conclusion is the **open** strip `0 < re < 1`, and
the target's `s ≠ 1` hypothesis is *not needed*: `re s < 1` already implies
`s ≠ 1`, and the `re < 1` bound comes from the closed-half-plane theorem
which needs no `s ≠ 1`. We state the stronger hypothesis-free form; a
wrapper with the redundant `s ≠ 1` is trivial if reviewers want literal
source alignment.

### Proof skeleton

```lean
theorem riemannZeta_zero_mem_critical_strip {s : ℂ} (hz : riemannZeta s = 0)
    (htriv : ¬∃ n : ℕ, s = -2 * (n + 1)) : 0 < s.re ∧ s.re < 1 := by
  constructor
  · by_contra h
    exact riemannZeta_ne_zero_of_re_le_zero (not_lt.mp h) htriv hz   -- P1
  · by_contra h
    exact riemannZeta_ne_zero_of_one_le_re (not_lt.mp h) hz
```

Corollary (free, records the exact `re = 0` treatment; the trivial-zero
exclusion discharges itself because `re(-2*(n+1)) = -(2*n+2) ≠ 0`):

```lean
theorem riemannZeta_ne_zero_of_re_eq_zero {s : ℂ} (hs : s.re = 0) : riemannZeta s ≠ 0 :=
  riemannZeta_ne_zero_of_re_le_zero hs.le (by
    rintro ⟨n, rfl⟩
    rw [show ((-2 : ℂ) * (n + 1)).re = -2 * ((n : ℝ) + 1) by push_cast; simp] at hs
    nlinarith [Nat.cast_nonneg (α := ℝ) n])   -- (fix F3); OBLIG P2-a cast form
```

### Pinned dependencies (P2)

P1 + `riemannZeta_ne_zero_of_one_le_re` (Nonvanishing.lean:410), `not_lt`.

### Obligations (P2)

- **OBLIGATION P2-a (LOW):** the real-part computation
  `((-2 : ℂ) * (↑n + 1)).re = -2 * (n + 1)` (simp set
  `Complex.mul_re`/`natCast_re` or `push_cast`; the skeleton's exact simp
  call is schematic).

---

## P3. Reflection of zeros inside the strip

### Statement

```lean
theorem riemannZeta_one_sub_eq_zero_iff {s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) :
    riemannZeta (1 - s) = 0 ↔ riemannZeta s = 0
```

Exact hypotheses needed: only the open strip. They imply all four
exceptional-point exclusions used: `s ≠ 0`, `s ≠ 1`, `1 - s ≠ 0`,
`1 - s ≠ 1` (each by taking real parts), and both gamma-factor
nonvanishings `Gammaℝ s ≠ 0`, `Gammaℝ (1-s) ≠ 0`
(`Gammaℝ_ne_zero_of_re_pos`; equivalently `Gammaℝ_eq_zero_iff` places all
`Gammaℝ` zeros at `-(2*n) ≤ 0`, outside the open strip — note this zero set
includes `0`, which is precisely why `0 < re` and not `0 ≤ re` is required).
This route goes through the **completed** zeta and its unconditional
symmetry `completedRiemannZeta_one_sub`, so no `cos`/`Gamma s` analysis
recurs.

### Proof skeleton

```lean
theorem riemannZeta_one_sub_eq_zero_iff {s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) :
    riemannZeta (1 - s) = 0 ↔ riemannZeta s = 0 := by
  have hs0 : s ≠ 0 := fun h => by simp [h] at h0
  have hs0' : (1 : ℂ) - s ≠ 0 := fun h => by
    have := congrArg Complex.re h
    rw [Complex.sub_re, Complex.one_re, Complex.zero_re] at this; linarith
  have hG : Gammaℝ s ≠ 0 := Complex.Gammaℝ_ne_zero_of_re_pos h0
  have hG' : Gammaℝ (1 - s) ≠ 0 := Complex.Gammaℝ_ne_zero_of_re_pos
    (by rw [Complex.sub_re, Complex.one_re]; linarith)
  rw [riemannZeta_def_of_ne_zero hs0', riemannZeta_def_of_ne_zero hs0,
    completedRiemannZeta_one_sub, div_eq_zero_iff, div_eq_zero_iff]
  -- both sides are now `completedRiemannZeta s = 0 ∨ (Gammaℝ _) = 0`
  simp [hG, hG']
```

### Pinned dependencies (P3)

`riemannZeta_def_of_ne_zero` (RiemannZeta.lean:152),
`completedRiemannZeta_one_sub` (:105), `Complex.Gammaℝ_ne_zero_of_re_pos`
(Deligne.lean:66), `Complex.Gammaℝ_eq_zero_iff` (Deligne.lean:73, cited for
the boundary analysis in review, not in the proof term), `Complex.zero_re`
(Data/Complex/Basic.lean:125), `div_eq_zero_iff`
(Algebra/GroupWithZero/Units/Basic.lean:289).

### Obligations (P3)

- **OBLIGATION P3-a (LOW):** final `simp [hG, hG']` closing the `∨`-shaped
  iff; if fragile, replace by explicit `or_iff_left hG'` / `or_iff_left hG`.
- None analytic.

---

## P4. Half-plane equivalence (strongest clean form)

### Design decision

Pinned Mathlib **does** know the totalized value at `1`: `riemannZeta_one`
(ZetaAsymp.lean:408) and, decisively, `riemannZeta_one_ne_zero`
(ZetaAsymp.lean:431). Therefore the equivalence needs **no** `s ≠ 1` guard
and **no** trivial-zero guard (trivial zeros have `re = -2(n+1) ≤ -2 < 1/2`),
and no `re < 1` upper guard (`re ≥ 1` is unconditionally zero-free by
Nonvanishing). The strongest clean statement the pinned API supports:

```lean
theorem riemannHypothesis_iff_zero_free_gt_half :
    RiemannHypothesis ↔ ∀ s : ℂ, 1 / 2 < s.re → riemannZeta s ≠ 0
```

### Proof skeleton (both directions)

```lean
theorem riemannHypothesis_iff_zero_free_gt_half :
    RiemannHypothesis ↔ ∀ s : ℂ, 1 / 2 < s.re → riemannZeta s ≠ 0 := by
  constructor
  · -- forward: RH ⟹ zero-free right open half-plane past 1/2
    intro hRH s hs hz
    have htriv : ¬∃ n : ℕ, s = -2 * (n + 1) := by
      rintro ⟨n, rfl⟩
      rw [show ((-2 : ℂ) * (n + 1)).re = -2 * ((n : ℝ) + 1) by push_cast; simp] at hs
      nlinarith [Nat.cast_nonneg (α := ℝ) n]     -- (fix F3); -2(n+1) ≤ -2 < 1/2 (OBLIG P4-a)
    have hs1 : s ≠ 1 := by rintro rfl; exact riemannZeta_one_ne_zero hz
    have h := hRH s hz htriv hs1                -- s.re = 1/2
    rw [h] at hs
    exact lt_irrefl _ hs
  · -- reverse: uses P2 (strip) + P3 (reflection)
    intro hfree s hz htriv _hs1
    obtain ⟨h0, h1⟩ := riemannZeta_zero_mem_critical_strip hz htriv
    by_contra hne
    rcases lt_or_gt_of_ne hne with hlt | hgt
    · -- s.re < 1/2 : reflect across the line; 1-s has re > 1/2
      have hz' : riemannZeta (1 - s) = 0 :=
        (riemannZeta_one_sub_eq_zero_iff h0 h1).mpr hz
      exact hfree (1 - s) (by rw [Complex.sub_re, Complex.one_re]; linarith) hz'
    · exact hfree s hgt hz
```

Note (adversarial review, confirmed): no step uses zeta-conjugation
symmetry — consistent with its `NOT-FOUND` status at the pin. The reverse
direction genuinely closes with `s ↦ 1-s` alone because P2 confines zeros to
the open strip first.

### Pinned dependencies (P4)

P2, P3, `riemannZeta_one_ne_zero` (ZetaAsymp.lean:431), `riemannZeta_one`
(ZetaAsymp.lean:408, design decision), `RiemannHypothesis`
(RiemannZeta.lean:182), `lt_or_gt_of_ne`, `lt_irrefl`.

### Obligations (P4)

- **OBLIGATION P4-a (LOW):** same cast computation as P2-a.
- **OBLIGATION P4-b (LOW):** `RiemannHypothesis` is a `def`, not a
  structure: `intro`/application must unfold it by default (semireducible)
  transparency. Expected to work as written; fallback `show ∀ (s : ℂ) ...`
  before `intro` (`rw [RiemannHypothesis]` is **not** available — use
  `show`/`delta`).

---

## P5. Critical-line equivalence via the zero-set object

### Translation lemma (exact bridge between the map's target and `riemannZetaZeros`)

`mem_riemannZetaZeros : z ∈ riemannZetaZeros ↔ riemannZeta z = 0` is
definitional (`.rfl`, ZetaZeros.lean:35): `riemannZetaZeros =
riemannZeta ⁻¹' {0}` records membership only — **no multiplicity**
(capability-map `S1-MULTIPLICITY`; nothing in this package touches
multiplicity). Additional free translation fact:

```lean
theorem one_notMem_riemannZetaZeros : (1 : ℂ) ∉ riemannZetaZeros :=
  fun h => riemannZeta_one_ne_zero (mem_riemannZetaZeros.mp h)
```

### Statements

Primary (strongest clean form — the `s ≠ 1` conjunct is redundant by
`one_notMem_riemannZetaZeros`):

```lean
theorem riemannHypothesis_iff_zetaZeros_re_eq_half :
    RiemannHypothesis ↔
      ∀ s ∈ riemannZetaZeros, (¬∃ n : ℕ, s = -2 * (n + 1)) → s.re = 1 / 2
```

Literal source-side form ("all nontrivial zeros lie on the line", with both
exclusions), as a corollary:

```lean
theorem riemannHypothesis_iff_zetaZeros_re_eq_half' :
    RiemannHypothesis ↔
      ∀ s ∈ riemannZetaZeros, (¬∃ n : ℕ, s = -2 * (n + 1)) ∧ s ≠ 1 → s.re = 1 / 2
```

### Proof skeletons

```lean
theorem riemannHypothesis_iff_zetaZeros_re_eq_half :
    RiemannHypothesis ↔
      ∀ s ∈ riemannZetaZeros, (¬∃ n : ℕ, s = -2 * (n + 1)) → s.re = 1 / 2 := by
  constructor
  · intro hRH s hmem htriv
    have hz : riemannZeta s = 0 := mem_riemannZetaZeros.mp hmem
    have hs1 : s ≠ 1 := by rintro rfl; exact riemannZeta_one_ne_zero hz
    exact hRH s hz htriv hs1
  · intro h s hz htriv _hs1
    exact h s (mem_riemannZetaZeros.mpr hz) htriv

theorem riemannHypothesis_iff_zetaZeros_re_eq_half' :
    RiemannHypothesis ↔
      ∀ s ∈ riemannZetaZeros, (¬∃ n : ℕ, s = -2 * (n + 1)) ∧ s ≠ 1 → s.re = 1 / 2 := by
  rw [riemannHypothesis_iff_zetaZeros_re_eq_half]
  constructor
  · exact fun h s hmem ⟨htriv, _⟩ => h s hmem htriv
  · intro h s hmem htriv
    exact h s hmem ⟨htriv, fun e => one_notMem_riemannZetaZeros (e ▸ hmem)⟩
```

### Pinned dependencies (P5)

`riemannZetaZeros` (ZetaZeros.lean:33), `mem_riemannZetaZeros` (:35),
`riemannZeta_one_ne_zero` (ZetaAsymp.lean:431), `RiemannHypothesis`
(RiemannZeta.lean:182).

### Obligations (P5)

- **OBLIGATION P5-a (LOW):** same def-unfolding note as P4-b.
- None analytic; P5 is pure translation and does not even need P1-P3.

---

## ANNEX A: xi-package statements (Gate 0 of the capability map — A/C-only follow-on PR; STATEMENTS ONLY, no skeletons, not part of this bridge PR)

Normalization derived from the **theorem** `completedRiemannZeta_eq`
(RiemannZeta.lean:84), `Λ(s) = Λ₀(s) - 1/s - 1/(1-s)`, giving
`s(s-1)Λ(s) = 1 + s(s-1)Λ₀(s)` away from `0,1` — not from the (conflicting)
module comment:

```lean
noncomputable def riemannXi (s : ℂ) : ℂ :=
  (1 + s * (s - 1) * completedRiemannZeta₀ s) / 2

theorem differentiable_riemannXi : Differentiable ℂ riemannXi
theorem riemannXi_one_sub (s : ℂ) : riemannXi (1 - s) = riemannXi s
theorem riemannXi_zero : riemannXi 0 = 1 / 2
theorem riemannXi_one  : riemannXi 1 = 1 / 2

theorem riemannXi_eq_of_ne {s : ℂ} (hs0 : s ≠ 0) (hs1 : s ≠ 1) :
    riemannXi s = s * (s - 1) * completedRiemannZeta s / 2

theorem riemannXi_eq_zero_iff_riemannZeta_eq_zero {s : ℂ} (hs0 : s ≠ 0) (hs1 : s ≠ 1)
    (htriv : ¬∃ n : ℕ, s = -2 * (n + 1)) :
    riemannXi s = 0 ↔ riemannZeta s = 0
-- reverse direction depends on Complex.Gammaℝ_eq_zero_iff (Deligne.lean:73), not field algebra

theorem riemannXi_ne_zero_of_re_le_zero {s : ℂ} (hs : s.re ≤ 0) : riemannXi s ≠ 0
theorem riemannXi_ne_zero_of_one_le_re  {s : ℂ} (hs : 1 ≤ s.re) : riemannXi s ≠ 0
theorem riemannXi_zero_mem_critical_strip {s : ℂ} (hz : riemannXi s = 0) :
    0 < s.re ∧ s.re < 1

theorem riemannHypothesis_iff_riemannXi_zeros_re_eq_half :
    RiemannHypothesis ↔ ∀ s : ℂ, riemannXi s = 0 → s.re = 1 / 2

-- multiplicity transport (S1-MULTIPLICITY; statement only, uses Analysis/Analytic/Order.lean:47)
theorem analyticOrderAt_riemannXi_eq_riemannZeta {s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) :
    analyticOrderAt riemannXi s = analyticOrderAt riemannZeta s
```

Dependencies for the annex when it is executed: `completedRiemannZeta₀`
(RiemannZeta.lean:63), `completedRiemannZeta` (:67), `completedRiemannZeta_eq`
(:84), `differentiable_completedZeta₀` (:89), `completedRiemannZeta₀_one_sub`
(:99), `Complex.Gammaℝ_eq_zero_iff` (Deligne.lean:73), `analyticOrderAt`
(Analysis/Analytic/Order.lean:47), `analyticOrderNatAt` (:61), plus this
bridge package (P1-P5 are its prerequisites in the A/C DAG).

---

## Pinned API dependencies table

All paths relative to the pinned Mathlib tree, all line numbers
grep-verified at `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (twice: drafter
and adversarial reviewer).

| declaration | file:line | used in |
|---|---|---|
| `RiemannHypothesis` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:182 | P4, P5 |
| `riemannZeta` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:119 | all |
| `riemannZeta_zero` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:149 | P1 |
| `riemannZeta_def_of_ne_zero` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:152 | P3 |
| `riemannZeta_neg_two_mul_nat_add_one` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:171 | statement-form alignment (review) |
| `riemannZeta_one_sub` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:176 | P1 |
| `completedRiemannZeta` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:67 | P3, annex |
| `completedRiemannZeta₀` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:63 | annex |
| `completedRiemannZeta_eq` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:84 | annex sign derivation |
| `differentiable_completedZeta₀` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:89 | annex |
| `completedRiemannZeta₀_one_sub` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:99 | annex |
| `completedRiemannZeta_one_sub` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:105 | P3 |
| `riemannZeta_ne_zero_of_one_le_re` | Mathlib/NumberTheory/LSeries/Nonvanishing.lean:410 | P1, P2 |
| `riemannZeta_one` | Mathlib/NumberTheory/Harmonic/ZetaAsymp.lean:408 | P4 design |
| `completedRiemannZeta_one` | Mathlib/NumberTheory/Harmonic/ZetaAsymp.lean:416 | (context) |
| `riemannZeta_one_ne_zero` | Mathlib/NumberTheory/Harmonic/ZetaAsymp.lean:431 | P4, P5 |
| `riemannZetaZeros` | Mathlib/NumberTheory/LSeries/ZetaZeros.lean:33 | P5 |
| `mem_riemannZetaZeros` | Mathlib/NumberTheory/LSeries/ZetaZeros.lean:35 | P5 |
| `Complex.Gammaℝ` | Mathlib/Analysis/SpecialFunctions/Gamma/Deligne.lean:43 | P3 |
| `Complex.Gammaℝ_ne_zero_of_re_pos` | Mathlib/Analysis/SpecialFunctions/Gamma/Deligne.lean:66 | P3 |
| `Complex.Gammaℝ_eq_zero_iff` | Mathlib/Analysis/SpecialFunctions/Gamma/Deligne.lean:73 | P3 boundary analysis, annex |
| `Complex.Gamma_ne_zero` | Mathlib/Analysis/SpecialFunctions/Gamma/Beta.lean:427 | P1 (alternative) |
| `Complex.Gamma_eq_zero_iff` | Mathlib/Analysis/SpecialFunctions/Gamma/Beta.lean:447 | P1 vanishing analysis |
| `Complex.Gamma_ne_zero_of_re_pos` | Mathlib/Analysis/SpecialFunctions/Gamma/Beta.lean:453 | P1 |
| `Complex.cos_eq_zero_iff` | Mathlib/Analysis/SpecialFunctions/Trigonometric/Complex.lean:33 | P1 |
| `Complex.sin_eq_zero_iff` | Mathlib/Analysis/SpecialFunctions/Trigonometric/Complex.lean:46 | unused (pinned FE uses `cos`) |
| `Complex.cpow_eq_zero_iff` | Mathlib/Analysis/SpecialFunctions/Pow/Complex.lean:45 | P1 |
| `Real.pi_ne_zero` | Mathlib/Analysis/SpecialFunctions/Trigonometric/Basic.lean:165 | P1 |
| `Complex.ofReal_ne_zero` | Mathlib/Data/Complex/Basic.lean:140 | P1 |
| `Complex.zero_re` | Mathlib/Data/Complex/Basic.lean:125 | P3 (fix F4) |
| `Complex.one_re` | Mathlib/Data/Complex/Basic.lean:147 | P1-P4 |
| `Complex.neg_re` | Mathlib/Data/Complex/Basic.lean:184 | P1 |
| `Complex.natCast_re` | Mathlib/Data/Complex/Basic.lean:356 | P1 |
| `Complex.intCast_re` | Mathlib/Data/Complex/Basic.lean:358 | P1 (fix F4) |
| `Complex.intCast_im` | Mathlib/Data/Complex/Basic.lean:359 | P1 (fix F4) |
| `Complex.sub_re` | Mathlib/Data/Complex/Basic.lean:640 | P1-P4 |
| `mul_ne_zero` | Mathlib/Algebra/GroupWithZero/Basic.lean:84 | P1 |
| `div_eq_zero_iff` | Mathlib/Algebra/GroupWithZero/Units/Basic.lean:289 | P3 |
| `Nat.cast_nonneg` | (core cast API) | P2, P4 (fix F3) |
| `analyticOrderAt` | Mathlib/Analysis/Analytic/Order.lean:47 | annex only |
| `analyticOrderNatAt` | Mathlib/Analysis/Analytic/Order.lean:61 | annex only |

Name-collision scan: grep over pinned Mathlib finds no occurrence of any
proposed name (`riemannZeta_ne_zero_of_re_le_zero`,
`riemannZeta_zero_mem_critical_strip`, `riemannZeta_one_sub_eq_zero_iff`,
`riemannHypothesis_iff_*`, `one_notMem_riemannZetaZeros`, `riemannXi*`).

---

## Anti-pitfall compliance (repo contracts)

- **Totalized values at exceptional points:** `s = 0` handled via
  `riemannZeta_zero` (P1); `s = 1` handled via `riemannZeta_one_ne_zero`
  (P4/P5); no statement treats totalized values as meromorphic values;
  `riemannZeta_def_of_ne_zero` is applied only under proved `≠ 0` side
  conditions (P3).
- **Exact trivial-zero form:** every exclusion is literally
  `¬∃ n : ℕ, s = -2 * (n + 1)`, character-identical to `RiemannHypothesis`
  at RiemannZeta.lean:182. The distinct `Gammaℝ` zero set `-(2*n)` (which
  additionally contains `0`) is never conflated with it.
- **No competing RH definition:** every equivalence has
  `_root_.RiemannHypothesis` verbatim on the left; no new `Prop` is
  introduced.
- **No Euler product / Dirichlet series:** the package never references
  them; all nonvanishing on `re ≥ 1` enters exclusively through
  `riemannZeta_ne_zero_of_one_le_re`.
- **No conjugation symmetry:** no proof step uses it (verified
  adversarially); consistent with its `NOT-FOUND` status.
- **Signs from `completedRiemannZeta_eq` (the theorem):** the annex
  normalization is derived from RiemannZeta.lean:84, not from the module
  comment; the bridge proper (P1-P5) needs no sign algebra at all because it
  uses `completedRiemannZeta_one_sub` and `riemannZeta_one_sub` as opaque
  pinned equations.
- **No multiplicity claims:** `riemannZetaZeros` is used as a set only (P5);
  multiplicity transport is explicitly deferred to the annex/A-C PR.

## Obligation register (v2 summary)

| id | severity | content |
|---|---|---|
| P1-c | MEDIUM | field cancellation `π*(1-s)/2 = (2k+1)*π/2 ⟹ s = -2k` in `ℂ`; exact tactic term unproved |
| P1-d | LOW | `ℤ→ℕ→ℂ` witness casts for `(k-1).toNat` |
| P2-a / P4-a | LOW | `((-2 : ℂ)*(↑n+1)).re = -2*(n+1)` simp/cast form |
| P3-a | LOW | closing `simp [hG, hG']` on the `∨`-iff |
| P4-b / P5-a | LOW | `RiemannHypothesis` def-unfolding via `intro`/application; fallback `show` |

Resolved in v2: P1-e (fix F1), the `1 ≤ k` defeq fragility (fix F2), the
`cast_nonneg` elaboration bug (fix F3), two uncited glue lemmas (fix F4),
and the scope-expansion question (fix F5, §Scope note).

No obligation is analytic; every analytic input (functional equations,
closed-half-plane nonvanishing, `ζ(0)`, `ζ(1) ≠ 0`, Gamma/cos zero
classifications, cpow nonvanishing) is a quoted pinned theorem. Nothing here
is claimed proved until the kernel checks it in the RH-004 built PR after
independent review.

---

## ANNEX B: adversarial review record (2026-08-05)

An independent adversarial reviewer attempted to refute draft v1 against the
pinned tree and the repo contracts. Verdict: **`SOUND_WITH_FIXES`** —
"refutation attempt failed on all substantive fronts": all 30+ cited
declarations verified at exact `file:line` with exact hypotheses and binder
structure (including the strict-implicit `⦃s⦄` and `_root_` prefix on
`riemannZeta_ne_zero_of_one_le_re`, and the exact cos-shaped prefactor); the
exceptional-point analysis (`s = 0`, `s = 1`, `re = 0`, `re = 1`,
trivial-zero form vs `Gammaℝ` zero set) found exhaustive and correct; no
circular input; both directions of P4/P5 derivable from the cited lemmas
with no missing case and no hidden use of conjugation; no competing RH
definition and no name collisions. Findings, all severity S2, all applied in
v2: **F1** `Gamma` glue-term shape (fixed), **F2** fragile defeq for
`1 ≤ k` (replaced by `k ≠ 0` + `omega`), **F3** `(n : ℝ).cast_nonneg`
elaboration bug (replaced by `Nat.cast_nonneg (α := ℝ) n`), **F4** two
uncited glue lemmas (`Complex.zero_re`, `Complex.intCast_re/_im` — added to
the dependency table with pinned locators), **F5** scope expansion of P1-P3
relative to a literal reading of the stop rule (resolved by the explicit
§Scope note and the capability-map addendum; requires reviewer
acknowledgment at RH-003 exit).
