# Mellin norm-bound contract (UPSTREAM-POOL §6): draft v1

Status: **DRAFT v1 (2026-08-07) — non-built design artifact, offered for STAGE ONE
(INDEPENDENT CONTRACT ACCEPTANCE) ONLY. NOT Lean-checked.** No declaration below
has been elaborated; no `lake build` has been run against any of it; no draft
`.lean` file exists for this package yet. Under the one invariant, the Lean
kernel via CI is the sole judge of every statement in this contract, and this
document carries no kernel verdict of any kind. Red-team re-verification of
every locator at the pin: **Annex A (2026-08-07)** — four locator corrections
and one obligation resolution applied in place, no signature changed.

**Two-stage gate.** Same convention as `MULTIPLICITY_CONTRACT.md`
(§Two-stage gate and promotion ordering there). Stage one is acceptance of the
statement surface MB1–MB4 only: it produces no built module, no ledger row, no
registry or axiom-audit entry, and no kernel verdict. Stage two is a separate
built promotion PR whose verdict is delivered by CI. An acceptance PR must not
carry a promotion.

**Ordering.** The RH queue is the authority for this lane (see
`MULTIPLICITY_CONTRACT.md` §Ordering); this document is an offered artifact,
not an active task, and it is not authorization to work a route. It selects no
route and does not touch `repo/ECDLP_DECISION_SUBSTRATE.json`'s lane.

Working name: `MellinBound.lean` (module name to be fixed at stage two; the
package is **generic** — see §Packaging below).
Statement surface: **MB1 – MB4**, comprising **exactly 5 public signatures**,
every one spelled explicitly in a `lean` statement block in §2 (MB3 carries
two). No signature of this package is mandated in prose only.

Scope: item §6 of `UPSTREAM_POOL.md` ("A norm bound for the Mellin transform",
named there **the cheapest item in the pool** — estimated *hours* — with all
three proof steps located at the pin; checklist row 8 at
`UPSTREAM_POOL.md:71`, priority row 1 at `:787`). The package is a bound on
`‖mellin f s‖` and its elementary consequences. It contains **no** functional
equation, **no** theta function, **no** statement about `completedRiemannZeta₀`
(`Λ₀`), ζ, ξ, or any zero of anything, and **no** claim of progress on the
Riemann Hypothesis. It closes **no** barrier of `MATHLIB_CAPABILITY_MAP.md`:
generic pinned-Mathlib-shaped machinery lowers the cost of a future exit but
never retires a row (`MULTIPLICITY_CONTRACT.md` finding A4 / death condition 9;
inherited here as death condition 6).

Pinned Mathlib: `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0),
toolchain `leanprover/lean4:v4.31.0`, verified this session via
`git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD`. Every
`file:line` locator below is from that exact tree (paths relative to the
`Mathlib/` root of the pin) unless prefixed `repo:`. Every locator inherited
from `UPSTREAM_POOL.md` §6 was **re-verified this session** against the pin;
one signature of the pool was found ill-typed and is corrected below
(§1, correction C1).

Repo prerequisites: **none.** Every dependency of every statement MB1–MB4 is
pinned Mathlib. No statement waits on any repo module, merged or unmerged.

## Candidate fields

- **Mechanism.** Three pinned steps. (1) `mellin f s` unfolds definitionally
  (`mellin`, MellinTransform.lean:91) to the Bochner set integral
  `∫ t in Ioi 0, (t:ℂ)^(s-1) • f t`. (2) `norm_integral_le_integral_norm`
  (Bochner/Basic.lean:924) — **unconditional**: it needs no integrability
  hypothesis, handling the non-`AEStronglyMeasurable` case internally — bounds
  the norm by `∫ t in Ioi 0, ‖(t:ℂ)^(s-1) • f t‖`. (3) On `Ioi 0` the
  integrand rewrites pointwise via `norm_smul` (MulAction.lean:98) and
  `Complex.norm_cpow_eq_rpow_re_of_pos` (Pow/Real.lean:337) to
  `t ^ (s.re - 1) * ‖f t‖`, transported through the integral by
  `setIntegral_congr_fun` (Bochner/Set.lean:73). Mathlib itself runs exactly
  this `simp_rw` chain at the pin (MellinTransform.lean:198 inside
  `mellin_convergent_iff_norm`), and fires the key cpow→rpow rewrite a second
  time at :353 (`rw [norm_cpow_eq_rpow_re_of_pos ht]`, after a *different*
  `simp_rw` set at :351 — Annex A finding R1), so the rewrite is known to fire.
  The corollaries are order-of-integrand arithmetic on the real bound:
  domination (`norm_integral_le_of_norm_le`, Bochner/Basic.lean:937),
  exponent monotonicity (`Real.rpow_le_rpow_of_exponent_le`, Pow/Real.lean:613),
  and the two-endpoint strip split (`rcases le_or_gt 1 t`, precedent in-tree at
  MellinTransform.lean:354–366).
- **Expected information gain.** A reusable interface fact: `‖mellin f s‖`
  depends on `s` only through `s.re` (MB2), is monotone in `re s` on the
  fixed integrand class supported in `[1, ∞)` (MB3), and is uniformly bounded
  on closed vertical strips from endpoint data alone (MB4). No information
  about the truth of RH is produced.
- **Claim boundary.** All of MB1–MB4 are unconditional consequences of pinned
  Mathlib theorems. Nothing touches ζ, ξ, `Λ₀`, theta kernels, zeros,
  enumeration, growth, functional equations, or any route's research
  obligation. The package contains **zero `def`s**. The `Λ₀` seam of §3 is a
  **FUTURE consumer citation only** — nothing in the statement surface
  mentions it, and this contract asserts nothing about it.
- **Death condition (stop rule).** Stop or split if a proof would need a new
  axiom, an unproved conjecture, a new definition, any hypothesis on `f`
  beyond those written (in particular any integrability hypothesis in MB1),
  or any fact about ζ/ξ/`Λ₀`; and do not declare a capability-map row stale on
  the strength of this generic package. Full list in §Death conditions. A
  clean blocker is preferable to a silently weakened bound.

## Packaging

The whole surface is `[GEN]`: generic statements over pinned objects, with
`Mathlib/Analysis/MellinTransform.lean` as the natural upstream home
(`UPSTREAM_POOL.md:555`). Two consequences, stated without promises:

1. **Ride-along.** These lemmas may later ride an RH-prefixed repo package
   exactly as the conjugation package carried its generic `AnalyticAt.conj_conj`
   alongside the ζ/ξ-specific statements: the generic lemma lands in the repo
   module that first consumes it, keeping the barrier-scoped package
   self-contained. No such consumer package exists yet; none is created here.
2. **Upstream potential.** The signatures are written Mathlib-style so a later
   upstream PR is a copy, not a redesign. This contract does **not** promise,
   schedule, or depend on upstreaming; acceptance and (eventual) promotion are
   evaluated entirely against this repository's gates.

Proposed module preamble (name-resolution review only):

```lean
import Mathlib.Analysis.MellinTransform          -- mellin, MellinConvergent
import Mathlib.MeasureTheory.Integral.Bochner.Basic  -- norm_integral_le_integral_norm
import Mathlib.MeasureTheory.Integral.Bochner.Set    -- setIntegral_congr_fun, setIntegral_mono_on
import Mathlib.Analysis.SpecialFunctions.Pow.Real    -- norm_cpow_eq_rpow_re_of_pos, rpow monotonicity

open Complex MeasureTheory Real Set
```

`Mathlib.Analysis.MellinTransform` transitively supplies everything else used
below; the explicit imports are documentation of intent, to be minimized by
`shake` at stage two.

Name-collision scan (grep over the pinned tree this session): **zero hits** for
every proposed name — `norm_mellin_le`, `norm_mellin_le_of_norm_le`,
`setIntegral_rpow_mul_mono_exponent`, `norm_mellin_le_of_re_le`,
`norm_mellin_le_add_of_re_mem_Icc` — and zero hits for the pool's withdrawn
name `norm_mellin_le_mellin_norm`.

---

## 0. Exact pinned interface (quoted from the tree at the pin)

```lean
-- Analysis/MellinTransform.lean:42 (section variables), :45, :91
variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
def MellinConvergent (f : ℝ → E) (s : ℂ) : Prop :=
  IntegrableOn (fun t : ℝ => (t : ℂ) ^ (s - 1) • f t) (Ioi 0)
def mellin (f : ℝ → E) (s : ℂ) : E :=
  ∫ t : ℝ in Ioi 0, (t : ℂ) ^ (s - 1) • f t

-- MeasureTheory/Integral/Bochner/Basic.lean:924 — UNCONDITIONAL: the
-- non-AEStronglyMeasurable case is handled inside the proof (integral = 0).
theorem norm_integral_le_integral_norm (f : α → G) : ‖∫ a, f a ∂μ‖ ≤ ∫ a, ‖f a‖ ∂μ

-- MeasureTheory/Integral/Bochner/Basic.lean:937
theorem norm_integral_le_of_norm_le {f : α → G} {g : α → ℝ} (hg : Integrable g μ)
    (h : ∀ᵐ x ∂μ, ‖f x‖ ≤ g x) : ‖∫ x, f x ∂μ‖ ≤ ∫ x, g x ∂μ

-- Analysis/SpecialFunctions/Pow/Real.lean:337 — the cpow→rpow rewrite
theorem norm_cpow_eq_rpow_re_of_pos {x : ℝ} (hx : 0 < x) (y : ℂ) : ‖(x : ℂ) ^ y‖ = x ^ y.re

-- Analysis/MellinTransform.lean:198 — the SAME chain, firing in-tree at the pin
-- (inside mellin_convergent_iff_norm, :188; the key rewrite fires again at
-- :353, `rw [norm_cpow_eq_rpow_re_of_pos ht]`, inside a different chain — R1):
--   simp_rw [norm_smul, norm_cpow_eq_rpow_re_of_pos (hT ht), sub_re, one_re]

-- MeasureTheory/Integral/Bochner/Set.lean:73
theorem setIntegral_congr_fun (hs : MeasurableSet s) (h : EqOn f g s) :
    ∫ x in s, f x ∂μ = ∫ x in s, g x ∂μ

-- MeasureTheory/Integral/Bochner/Set.lean:764. Section variables at :752,
-- `include hf hg` — so BOTH IntegrableOn hypotheses are leading explicit
-- arguments at every call site: `setIntegral_mono_on hf hg hs h`.
variable (hf : IntegrableOn f s μ) (hg : IntegrableOn g s μ)
theorem setIntegral_mono_on (hs : MeasurableSet s) (h : ∀ x ∈ s, f x ≤ g x) :
    ∫ x in s, f x ∂μ ≤ ∫ x in s, g x ∂μ
theorem setIntegral_nonneg (hs : MeasurableSet s) (hf : ∀ x, x ∈ s → 0 ≤ f x) :
    0 ≤ ∫ x in s, f x ∂μ                                       -- :818

-- Analysis/Normed/MulAction.lean:98 (via NormSMulClass, field at :96; the ℂ-on-E
-- instance is what MellinTransform.lean:198 already exercises)
lemma norm_smul [Norm α] [Norm β] [SMul α β] [NormSMulClass α β] (r : α) (x : β) :
    ‖r • x‖ = ‖r‖ * ‖x‖

-- Analysis/SpecialFunctions/Pow/Real.lean:163, :613, :639
theorem rpow_nonneg {x : ℝ} (hx : 0 ≤ x) (y : ℝ) : 0 ≤ x ^ y
theorem rpow_le_rpow_of_exponent_le (hx : 1 ≤ x) (hyz : y ≤ z) : x ^ y ≤ x ^ z
theorem rpow_le_rpow_of_exponent_ge (hx0 : 0 < x) (hx1 : x ≤ 1) (hyz : z ≤ y) :
    x ^ y ≤ x ^ z

-- MeasureTheory/Function/L1Space/Integrable.lean:86
theorem Integrable.mono {f : α → β} {g : α → γ} (hg : Integrable g μ)
    (hf : AEStronglyMeasurable f μ) (h : ∀ᵐ a ∂μ, ‖f a‖ ≤ ‖g a‖) : Integrable f μ

-- MeasureTheory/Integral/Bochner/Basic.lean:241
theorem integral_add {f g : α → G} (hf : Integrable f μ) (hg : Integrable g μ) :
    ∫ a, f a + g a ∂μ = ∫ a, f a ∂μ + ∫ a, g a ∂μ

-- MeasureTheory/Measure/Restrict.lean:641; BorelSpace/Order.lean:197
theorem ae_restrict_mem (hs : MeasurableSet s) : ∀ᵐ x ∂μ.restrict s, x ∈ s
theorem measurableSet_Ioi : MeasurableSet (Ioi a)

-- Complex `re` arithmetic (same pins as MULTIPLICITY_CONTRACT.md §0)
theorem one_re : (1 : ℂ).re = 1                     -- Data/Complex/Basic.lean:147
theorem sub_re (z w : ℂ) : (z - w).re = z.re - w.re -- Data/Complex/Basic.lean:640

-- Integrability suppliers a consumer will typically use to discharge MB2–MB4
-- hypotheses (NOT dependencies of this package):
--   mellinConvergent_of_isBigO_rpow      MellinTransform.lean:277
--   mellinConvergent_of_isBigO_rpow_exp  MellinTransform.lean:414
--   integrableOn_Ioi_rpow_of_lt          ImproperIntegrals.lean:131
--   not_integrableOn_Ioi_rpow            ImproperIntegrals.lean:160
```

---

## 1. Design decisions

### Decision: real-valued bound, `IntegrableOn` hypotheses on the *bound*, never on `f`.

1. **The core bound is unconditional (MB1).** `norm_integral_le_integral_norm`
   (Bochner/Basic.lean:924) requires nothing: if the Mellin integrand is not
   even a.e. strongly measurable, both `mellin f s = 0` (integral of a
   non-measurable function) and the RHS is nonnegative, and the pin's proof
   already internalizes that case split. MB1 therefore takes **no hypothesis
   at all**. A `MellinConvergent`-guarded variant would be strictly weaker and
   is deliberately omitted; `MellinConvergent` (MellinTransform.lean:45)
   appears in this contract only as a supplier consumers may use to discharge
   MB2–MB4's `IntegrableOn` hypotheses (via `mellin_convergent_iff_norm`,
   :188).

2. **Correction C1 — the pool's second signature is withdrawn as ill-typed.**
   `UPSTREAM_POOL.md:566` proposed
   `norm_mellin_le_mellin_norm : ‖mellin f s‖ ≤ mellin (fun t ↦ ‖f t‖) (s.re : ℂ)`.
   At the pin `mellin` is defined only for `[NormedSpace ℂ E]`
   (MellinTransform.lean:42), and `ℝ` is **not** a `NormedSpace ℂ` instance,
   so `mellin (fun t ↦ ‖f t‖)` does not elaborate. The content that signature
   was after — the bound depends on `s` only through `s.re` — is carried
   instead by MB2's RHS, which is a plain real integral in `s.re`. An
   `ofReal`-decorated resurrection (`mellin (fun t ↦ (‖f t‖ : ℂ))`) is
   possible but adds `Complex.ofReal_cpow`/`integral_ofReal` glue for zero
   consumer value; recorded as **DEFERRED-1**, not part of the surface.

3. **Monotonicity needs a class restriction, and the restriction is the
   honest content of MB3.** `t ↦ t ^ (σ - 1)` is increasing in `σ` for
   `t ≥ 1` and *decreasing* for `t ≤ 1`, so no unconditional monotonicity in
   `re s` exists. MB3 fixes the integrand class `g = 0` on `Ioo 0 1`,
   `g ≥ 0` (support in `[1, ∞)`), where the bound is monotone
   **nondecreasing** in `re s`. The mirror class (support in `(0, 1]`,
   bound *nonincreasing*, via `rpow_le_rpow_of_exponent_ge`,
   Pow/Real.lean:639) is a rename-and-flip of the same skeleton; it is noted
   here and **not** stated, to keep the surface minimal (**DEFERRED-2**).
   Stating MB3 without the class restriction is a **death condition** (it is
   false: take `g` an indicator concentrated near `t = 0`).

4. **The strip form (MB4) takes both endpoint integrabilities as hypotheses
   plus one measurability hypothesis on `g`.** The pointwise split
   `t^(σ-1) ≤ t^(a-1) + t^(b-1)` for `a ≤ σ ≤ b`, `t > 0` (cases `1 ≤ t` /
   `t < 1`) is the exact maneuver Mathlib runs at MellinTransform.lean:350–355.
   Deriving integrability of the middle exponent from the endpoints, however,
   goes through `Integrable.mono` (L1Space/Integrable.lean:86), which demands
   `AEStronglyMeasurable` of the middle integrand — not derivable from bare
   `IntegrableOn` endpoint hypotheses. Rather than smuggle it, MB4 carries
   `hmg : AEStronglyMeasurable g (volume.restrict (Ioi 0))` explicitly. This
   is the package's riskiest assembly (obligation **MEL-4a**, the only
   MEDIUM).

5. **No new definitions, no `noncomputable`, no instances.** The package is
   five theorems.

---

## 2. Statement list MB1 – MB4

Legend: `[GEN]` generic, natural Mathlib upstream (whole surface).

---

## MB1. The core norm bound `[GEN]` — unconditional

### Statement

```lean
theorem norm_mellin_le {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
    (f : ℝ → E) (s : ℂ) :
    ‖mellin f s‖ ≤ ∫ t : ℝ in Set.Ioi 0, t ^ (s.re - 1) * ‖f t‖
```

(`t ^ (s.re - 1)` is `Real.rpow`; the RHS is a real Bochner set integral.)

### Proof skeleton

```lean
  refine (norm_integral_le_integral_norm _).trans_eq ?_      -- Bochner/Basic.lean:924
  -- goal: ∫ t in Ioi 0, ‖(t:ℂ)^(s-1) • f t‖ = ∫ t in Ioi 0, t^(s.re-1) * ‖f t‖
  refine setIntegral_congr_fun measurableSet_Ioi fun t ht => ?_   -- Bochner/Set.lean:73
  rw [norm_smul, Complex.norm_cpow_eq_rpow_re_of_pos ht,     -- MulAction.lean:98, Pow/Real.lean:337
      Complex.sub_re, Complex.one_re]                        -- Basic.lean:640, :147
```

The opening `refine` must see `mellin f s` as the set integral up to
unfolding of the plain `def` at MellinTransform.lean:91 (`UPSTREAM_POOL.md`'s
"unfolds by `rfl`"); fallbacks in MEL-1a.

### Pinned dependencies (MB1)

`mellin` MellinTransform.lean:91 (section variables :42);
`norm_integral_le_integral_norm` Bochner/Basic.lean:924 (**unconditional**);
`setIntegral_congr_fun` Bochner/Set.lean:73; `measurableSet_Ioi`
BorelSpace/Order.lean:197; `norm_smul` MulAction.lean:98;
`Complex.norm_cpow_eq_rpow_re_of_pos` Pow/Real.lean:337; `Complex.sub_re` /
`Complex.one_re` Data/Complex/Basic.lean:640/:147. In-tree precedent:
MellinTransform.lean:198 (the whole pointwise chain) and :353 (the cpow→rpow
step alone).

### Obligations (MB1)

- **MEL-1a** (LOW): the defeq unfolding of `mellin` under `refine`. Fallbacks,
  in order: `unfold mellin`; `show ‖∫ t : ℝ in Set.Ioi 0, (t:ℂ)^(s-1) • f t‖ ≤ _`;
  `rw [mellin]` via the equation lemma.
- **MEL-1b** (LOW, the pool's named hardest step): the `EqOn` pointwise chain.
  If the `rw` sequence misfires on implicit-argument shape, use the in-tree
  spelling verbatim: `simp_rw [norm_smul, Complex.norm_cpow_eq_rpow_re_of_pos ht,
  Complex.sub_re, Complex.one_re]` (MellinTransform.lean:198), or `simp only`
  with the same lemma set. `ht : t ∈ Set.Ioi 0` coerces to `0 < t` by `rfl`
  (`Set.mem_Ioi`).

---

## MB2. Dominated form `[GEN]` — the form downstream consumers use

Shows `‖mellin f s‖` is controlled by data depending on `s` only through
`s.re`: the RHS is constant on every vertical line `re s = σ`.

### Statement

```lean
theorem norm_mellin_le_of_norm_le {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
    {f : ℝ → E} {g : ℝ → ℝ} {s : ℂ}
    (hg : MeasureTheory.IntegrableOn (fun t : ℝ => t ^ (s.re - 1) * g t) (Set.Ioi 0))
    (h : ∀ t ∈ Set.Ioi (0 : ℝ), ‖f t‖ ≤ g t) :
    ‖mellin f s‖ ≤ ∫ t : ℝ in Set.Ioi 0, t ^ (s.re - 1) * g t
```

### Proof skeleton

```lean
  refine (norm_integral_le_of_norm_le hg ?_)                 -- Bochner/Basic.lean:937
  -- (mellin unfolding as in MB1; μ := volume.restrict (Ioi 0), IntegrableOn is defeq)
  filter_upwards [MeasureTheory.ae_restrict_mem measurableSet_Ioi] with t ht
                                                             -- Restrict.lean:641
  rw [norm_smul, Complex.norm_cpow_eq_rpow_re_of_pos ht, Complex.sub_re, Complex.one_re]
  exact mul_le_mul_of_nonneg_left (h t ht) (Real.rpow_nonneg ht.le _)
                                                             -- Pow/Real.lean:163
```

### Pinned dependencies (MB2)

MB1's pointwise chain; `norm_integral_le_of_norm_le` Bochner/Basic.lean:937;
`ae_restrict_mem` Restrict.lean:641 (in-tree precedent for the same a.e.
extraction, spelled `(ae_restrict_mem measurableSet_Ioi).mono`:
MellinTransform.lean:350); `Real.rpow_nonneg`
Pow/Real.lean:163; `mul_le_mul_of_nonneg_left` (core order algebra, not
line-pinned).

### Obligations (MB2)

- **MEL-2a** (LOW): `IntegrableOn … (Ioi 0)` must unify with
  `Integrable … (volume.restrict (Ioi 0))` at the `hg` argument — they are
  definitionally equal (`IntegrableOn` is a `def` wrapper); fallback
  `rw [MeasureTheory.IntegrableOn] at hg` or `exact hg.integrable` shapes.
- **MEL-2b** (LOW): same unfolding/rewrite fallbacks as MEL-1a/1b.

---

## MB3. Monotonicity in `re s` on the fixed integrand class supported in `[1, ∞)` `[GEN]`

Two signatures: the bound-level monotonicity, and the mellin-level
consequence. The class restriction (`g` vanishes on `Ioo 0 1`) is load-bearing;
see §1.3 and death condition 4.

### Statement

```lean
theorem setIntegral_rpow_mul_mono_exponent {g : ℝ → ℝ} {a b : ℝ} (hab : a ≤ b)
    (hg0 : ∀ t ∈ Set.Ioi (0 : ℝ), 0 ≤ g t)
    (hgsupp : ∀ t ∈ Set.Ioo (0 : ℝ) 1, g t = 0)
    (hga : MeasureTheory.IntegrableOn (fun t : ℝ => t ^ (a - 1) * g t) (Set.Ioi 0))
    (hgb : MeasureTheory.IntegrableOn (fun t : ℝ => t ^ (b - 1) * g t) (Set.Ioi 0)) :
    (∫ t : ℝ in Set.Ioi 0, t ^ (a - 1) * g t) ≤ ∫ t : ℝ in Set.Ioi 0, t ^ (b - 1) * g t

theorem norm_mellin_le_of_re_le {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
    {f : ℝ → E} {g : ℝ → ℝ} {s : ℂ} {b : ℝ} (hsb : s.re ≤ b)
    (hg0 : ∀ t ∈ Set.Ioi (0 : ℝ), 0 ≤ g t)
    (hgsupp : ∀ t ∈ Set.Ioo (0 : ℝ) 1, g t = 0)
    (h : ∀ t ∈ Set.Ioi (0 : ℝ), ‖f t‖ ≤ g t)
    (hgs : MeasureTheory.IntegrableOn (fun t : ℝ => t ^ (s.re - 1) * g t) (Set.Ioi 0))
    (hgb : MeasureTheory.IntegrableOn (fun t : ℝ => t ^ (b - 1) * g t) (Set.Ioi 0)) :
    ‖mellin f s‖ ≤ ∫ t : ℝ in Set.Ioi 0, t ^ (b - 1) * g t
```

`norm_mellin_le_of_re_le` is the monotonicity statement in usable form: on the
class, one integrability check at the top of a half-plane `re s ≤ b` bounds
`‖mellin f s‖` for **every** `s` below it, uniformly.

### Proof skeleton

```lean
-- setIntegral_rpow_mul_mono_exponent:
  refine MeasureTheory.setIntegral_mono_on hga hgb measurableSet_Ioi fun t ht => ?_
                                                             -- Bochner/Set.lean:764 (+ :752 include)
  rcases lt_or_ge t 1 with h1 | h1
  · simp [hgsupp t ⟨ht, h1⟩]                                 -- both sides 0
  · exact mul_le_mul_of_nonneg_right
      (Real.rpow_le_rpow_of_exponent_le h1 (by linarith)) (hg0 t ht)
                                                             -- Pow/Real.lean:613

-- norm_mellin_le_of_re_le:
  exact (norm_mellin_le_of_norm_le hgs h).trans
    (setIntegral_rpow_mul_mono_exponent hsb hg0 hgsupp hgs hgb)
```

### Pinned dependencies (MB3)

MB2; `setIntegral_mono_on` Bochner/Set.lean:764 (section variables `hf hg`
at :752 under `include` — both `IntegrableOn` arguments are **explicit and
leading**; pre-registered call shape in §0); `Real.rpow_le_rpow_of_exponent_le`
Pow/Real.lean:613; `mul_le_mul_of_nonneg_right` (core order algebra).

### Obligations (MB3)

- **MEL-3a** (LOW): the `setIntegral_mono_on` argument order (`hga hgb hs h`);
  if the `include`-generated order differs, name them:
  `setIntegral_mono_on (hf := hga) (hg := hgb) …`.
- **MEL-3b** (LOW): the boundary case `t = 1` must land in the second branch
  (`1 ≤ t`, both exponentials equal 1); `lt_or_ge t 1` places it there. Do
  not switch to `Ioc 0 1` support without re-checking this seam.

---

## MB4. Uniform bound on a closed vertical strip `[GEN]` — the seam-facing specialization

The form a `Λ₀`-type consumer would invoke (§3): endpoint data at `re s = a`
and `re s = b` yields one `s`-independent bound valid on all of
`a ≤ re s ≤ b`, with no support restriction on `g`.

### Statement

```lean
theorem norm_mellin_le_add_of_re_mem_Icc {E : Type*} [NormedAddCommGroup E]
    [NormedSpace ℂ E] {f : ℝ → E} {g : ℝ → ℝ} {s : ℂ} {a b : ℝ}
    (ha : a ≤ s.re) (hb : s.re ≤ b)
    (hg0 : ∀ t ∈ Set.Ioi (0 : ℝ), 0 ≤ g t)
    (h : ∀ t ∈ Set.Ioi (0 : ℝ), ‖f t‖ ≤ g t)
    (hmg : MeasureTheory.AEStronglyMeasurable g (MeasureTheory.volume.restrict (Set.Ioi 0)))
    (hga : MeasureTheory.IntegrableOn (fun t : ℝ => t ^ (a - 1) * g t) (Set.Ioi 0))
    (hgb : MeasureTheory.IntegrableOn (fun t : ℝ => t ^ (b - 1) * g t) (Set.Ioi 0)) :
    ‖mellin f s‖ ≤ (∫ t : ℝ in Set.Ioi 0, t ^ (a - 1) * g t)
      + ∫ t : ℝ in Set.Ioi 0, t ^ (b - 1) * g t
```

### Proof skeleton

```lean
  -- Step 1: pointwise two-endpoint domination on Ioi 0 (in-tree maneuver,
  -- MellinTransform.lean:354–366):
  have hpt : ∀ t ∈ Set.Ioi (0 : ℝ),
      t ^ (s.re - 1) * g t ≤ t ^ (a - 1) * g t + t ^ (b - 1) * g t := by
    intro t ht
    rcases le_or_gt 1 t with h1 | h1
    · have := Real.rpow_le_rpow_of_exponent_le h1 (by linarith : s.re - 1 ≤ b - 1)
      nlinarith [Real.rpow_nonneg (le_of_lt ht) (a - 1), hg0 t ht,
        mul_le_mul_of_nonneg_right this (hg0 t ht)]
    · have := Real.rpow_le_rpow_of_exponent_ge ht h1.le (by linarith : a - 1 ≤ s.re - 1)
                                                             -- Pow/Real.lean:639
      nlinarith [Real.rpow_nonneg (le_of_lt ht) (b - 1), hg0 t ht,
        mul_le_mul_of_nonneg_right this (hg0 t ht)]
  -- Step 2: middle-exponent integrability from the endpoints (MEL-4a):
  have hgs : MeasureTheory.IntegrableOn (fun t : ℝ => t ^ (s.re - 1) * g t) (Set.Ioi 0) := by
    refine (hga.add hgb).mono ?_ ?_                          -- L1Space/Integrable.lean:86
    · exact ((continuousOn_id'.rpow_const fun t ht => Or.inl (ne_of_gt ht)
        ).aestronglyMeasurable measurableSet_Ioi).mul hmg      -- see MEL-4a (route ii)
    · filter_upwards [MeasureTheory.ae_restrict_mem measurableSet_Ioi] with t ht
      have h0 : (0:ℝ) ≤ g t := hg0 t ht
      rw [Real.norm_of_nonneg (by positivity), Real.norm_of_nonneg (by positivity)]
      exact hpt t ht
  -- Step 3: assemble.
  calc ‖mellin f s‖ ≤ ∫ t in Set.Ioi 0, t ^ (s.re - 1) * g t :=
        norm_mellin_le_of_norm_le hgs h                      -- MB2
    _ ≤ ∫ t in Set.Ioi 0, (t ^ (a - 1) * g t + t ^ (b - 1) * g t) :=
        MeasureTheory.setIntegral_mono_on hgs (hga.add hgb) measurableSet_Ioi hpt
    _ = _ := MeasureTheory.integral_add hga hgb              -- Bochner/Basic.lean:241
```

### Pinned dependencies (MB4)

MB2; `Real.rpow_le_rpow_of_exponent_le` / `…_ge` Pow/Real.lean:613/:639
(in-tree precedent for the case split: MellinTransform.lean:354–366);
`Integrable.mono` L1Space/Integrable.lean:86; `setIntegral_mono_on`
Bochner/Set.lean:764; `integral_add` Bochner/Basic.lean:241;
`ae_restrict_mem` Restrict.lean:641; `Real.rpow_nonneg` Pow/Real.lean:163;
`measurableSet_Ioi` BorelSpace/Order.lean:197.

### Obligations (MB4)

- **MEL-4a** (MEDIUM — **the riskiest step of the package**). Step 2's
  `AEStronglyMeasurable` leg for `fun t => t ^ (s.re - 1) * g t` under
  `volume.restrict (Ioi 0)`: `t ↦ t ^ (s.re - 1)` is not globally continuous
  (rpow junk at `t ≤ 0`). **Route resolution (Annex A finding R4):** the
  originally-sketched route (i) — a `Measurable.rpow_const` /
  `measurable_rpow` name — has **zero grep hits at the pin** and is
  withdrawn. Route (ii) is now the primary route, fully located at the pin:
  `continuousOn_id'` (Topology/ContinuousOn.lean:737) `.rpow_const`
  (`ContinuousOn.rpow_const`, Analysis/SpecialFunctions/Pow/Continuity.lean:278,
  side condition `∀ t ∈ Ioi 0, t ≠ 0 ∨ _` discharged by `Or.inl (ne_of_gt ht)`),
  then `ContinuousOn.aestronglyMeasurable`
  (MeasureTheory/Integral/IntegrableOn.lean:760; instance side conditions are
  satisfied by `ℝ`) at `measurableSet_Ioi`, then `.mul hmg`. In-tree analogue
  of the continuity-on-`Ioi 0` maneuver: the `continuousAt_ofReal_cpow_const`
  usages at MellinTransform.lean:338 and :345 (complex variant).
  Also in this obligation: the two `Real.norm_of_nonneg` rewrites and the
  `positivity` side goals in the a.e. comparison. If (i) and (ii) both frustrate,
  the fallback is to **strengthen the hypothesis** from `hmg` to
  `hms : AEStronglyMeasurable (fun t => t ^ (s.re - 1) * g t) (volume.restrict (Set.Ioi 0))`
  — a signature change, which under the stage-one rules re-opens acceptance of
  MB4 only (see §Return condition).
- **MEL-4b** (LOW): the `nlinarith` closers in `hpt` are convenience; the
  structured fallback is
  `add_le_add (le_of_eq rfl) …`-style: bound the matching term with
  `mul_le_mul_of_nonneg_right`, then `le_add_of_nonneg_left/right` with
  `mul_nonneg (Real.rpow_nonneg ht.le _) (hg0 t ht)`.
- **MEL-4c** (LOW): `integral_add` needs the integrand written as a pointwise
  sum; the `calc`'s middle integrand is already in that shape. If the final
  step's elaboration balks at `IntegrableOn` vs `Integrable`, apply
  MEL-2a's defeq note.

---

## 3. FUTURE consumer citation: the `Λ₀` = mellin-of-theta seam (NOT asserted)

Cited for orientation only. **Nothing in this section is part of the statement
surface, nothing in it is claimed, and this contract does not assert that the
seam below composes, elaborates, or yields any particular bound.**

At the pin, `completedRiemannZeta₀` (the entire completion `Λ₀` that the
repo's ξ definition is built on, `TARGET_BRIDGE_CONTRACT.md` X1 /
`CONJ_SYMMETRY_CONTRACT.md` Z3) is definitionally a Mellin transform:

| Link | Locator (pinned tree) |
|---|---|
| `completedRiemannZeta₀ s = completedHurwitzZetaEven₀ 0 s` | NumberTheory/LSeries/RiemannZeta.lean:63 |
| `completedHurwitzZetaEven₀ a s = ((hurwitzEvenFEPair a).Λ₀ (s / 2)) / 2` | NumberTheory/LSeries/HurwitzZetaEven.lean:302 |
| `WeakFEPair.Λ₀ = mellin P.f_modif` | NumberTheory/LSeries/AbstractFuncEq.lean:385 (structure :81, `f_modif` :258) |
| `hurwitzEvenFEPair a` has `f := ofReal ∘ evenKernel a` (theta kernel) | HurwitzZetaEven.lean:254 (kernel :65, `evenKernel_def` :77) |

A **future** consumer holding (a) this chain and (b) decay/measurability facts
for `(hurwitzEvenFEPair 0).f_modif` — neither supplied nor promised here —
would invoke **MB4** at `f := (hurwitzEvenFEPair 0).f_modif`, exponent `s / 2`,
to get `‖completedRiemannZeta₀ s‖` bounded uniformly on closed vertical strips
by two endpoint integrals, and **MB2/MB3** for one-sided variants. That
hypothetical use is why MB4's hypotheses are endpoint-shaped. Whether the
`f_modif` side conditions are dischargeable at the pin is **explicitly outside
this contract** (death condition 5); no statement about `Λ₀`, ζ, ξ, theta
kernels, or `WeakFEPair` may enter this package.

---

## Pinned API dependencies table

| Symbol | Locator | Used by |
|---|---|---|
| `mellin` (def) | Analysis/MellinTransform.lean:91 (vars :42) | MB1–MB4 |
| `MellinConvergent` | MellinTransform.lean:45 | consumers only (§1.1) |
| `mellin_convergent_iff_norm` | MellinTransform.lean:188 (chain at :198) | precedent; consumers |
| `norm_integral_le_integral_norm` | MeasureTheory/Integral/Bochner/Basic.lean:924 | MB1 |
| `norm_integral_le_of_norm_le` | Bochner/Basic.lean:937 | MB2 |
| `integral_add` | Bochner/Basic.lean:241 | MB4 |
| `setIntegral_congr_fun` | MeasureTheory/Integral/Bochner/Set.lean:73 | MB1 |
| `setIntegral_mono_on` (vars :752, `include`) | Bochner/Set.lean:764 | MB3, MB4 |
| `setIntegral_nonneg` | Bochner/Set.lean:818 | fallbacks |
| `norm_smul` | Analysis/Normed/MulAction.lean:98 | MB1, MB2 |
| `Complex.norm_cpow_eq_rpow_re_of_pos` | Analysis/SpecialFunctions/Pow/Real.lean:337 | MB1, MB2 |
| in-tree rewrite precedent | MellinTransform.lean:198 (chain), :353 (cpow→rpow step) | MEL-1b |
| in-tree strip-split precedent | MellinTransform.lean:354–366 | MB4 |
| `ContinuousOn.rpow_const` | Analysis/SpecialFunctions/Pow/Continuity.lean:278 | MEL-4a |
| `ContinuousOn.aestronglyMeasurable` | MeasureTheory/Integral/IntegrableOn.lean:760 | MEL-4a |
| `continuousOn_id'` | Topology/ContinuousOn.lean:737 | MEL-4a |
| `Real.rpow_nonneg` | Pow/Real.lean:163 | MB2, MB4 |
| `Real.rpow_le_rpow_of_exponent_le` | Pow/Real.lean:613 | MB3, MB4 |
| `Real.rpow_le_rpow_of_exponent_ge` | Pow/Real.lean:639 | MB4 |
| `Integrable.mono` | MeasureTheory/Function/L1Space/Integrable.lean:86 | MB4 |
| `ae_restrict_mem` | MeasureTheory/Measure/Restrict.lean:641 | MB2, MB4 |
| `measurableSet_Ioi` | MeasureTheory/Constructions/BorelSpace/Order.lean:197 | MB1–MB4 |
| `Complex.sub_re` / `Complex.one_re` | Data/Complex/Basic.lean:640 / :147 | MB1, MB2 |
| `integrableOn_Ioi_rpow_of_lt` / `not_integrableOn_Ioi_rpow` | Analysis/SpecialFunctions/ImproperIntegrals.lean:131 / :160 | consumers; sanity (below) |

Sanity check recorded against over-claiming: `not_integrableOn_Ioi_rpow`
(ImproperIntegrals.lean:160) shows `t ^ σ` alone is **never** integrable on
`Ioi 0`, so MB2–MB4's `IntegrableOn` hypotheses are not vacuous decorations
and cannot be dropped. MB1's unconditionality needs **no case analysis at
all**: it is `norm_integral_le_integral_norm` (Bochner/Basic.lean:924, proved
at the pin with the non-`AEStronglyMeasurable` case internalized) composed
with `setIntegral_congr_fun`, an integral *congruence* that holds with or
without integrability. For orientation only, the degenerate case resolves as:
if the Mellin integrand is not a.e. strongly measurable, both sides are `0`
(`integral_non_aestronglyMeasurable`, used inside :924's own proof); if it is
a.e. strongly measurable but not integrable, `integrable_norm_iff` plus
`integral_undef` zero both sides. (An earlier draft cited
`mellin_convergent_iff_norm` here; that lemma carries an
`AEStronglyMeasurable f` hypothesis, MellinTransform.lean:190, so it does not
cover the non-measurable case — Annex A finding R3.) Junk-value semantics
make the real-valued unconditional shape of MB1 honest at the pin; no
`ENNReal`/`tsub` restatement and no `IntegrableOn` guard is needed on MB1,
and death condition 3 keeps it that way.

## Obligation register

| ID | Severity | Content |
|---|---|---|
| MEL-1a | LOW | `mellin` defeq unfolding under `refine`; three fallbacks listed |
| MEL-1b | LOW | the `EqOn` pointwise chain; in-tree `simp_rw` spelling at MellinTransform.lean:198 is the fallback |
| MEL-2a | LOW | `IntegrableOn` / `Integrable (restrict)` defeq at the `hg` argument |
| MEL-2b | LOW | as MEL-1a/1b for MB2's goal shape |
| MEL-3a | LOW | `setIntegral_mono_on` `include`-argument order |
| MEL-3b | LOW | `t = 1` boundary lands in the `1 ≤ t` branch |
| MEL-4a | **MEDIUM** | MB4 step 2: `AEStronglyMeasurable` of the middle-exponent integrand + `Real.norm_of_nonneg`/`positivity` bookkeeping; route (ii) now fully located at the pin (Continuity.lean:278 + IntegrableOn.lean:760 + ContinuousOn.lean:737 — Annex A R4); route (i) name withdrawn (zero hits); signature-strengthening fallback re-opens MB4 only |
| MEL-4b | LOW | structured replacement for the `nlinarith` closers in `hpt` |
| MEL-4c | LOW | `integral_add` final-step shape |

### Deferred items (explicitly out of this package)

- **DEFERRED-1**: `ofReal`-valued resurrection of the pool's
  `norm_mellin_le_mellin_norm` (withdrawn as ill-typed, correction C1).
- **DEFERRED-2**: the mirror monotonicity class (support in `(0, 1]`, bound
  nonincreasing in `re s`, via Pow/Real.lean:639).
- **DEFERRED-3**: any `Λ₀`/theta specialization (§3) — a different contract
  with its own hypotheses, if ever selected by the queue.

## Claim boundary

1. This is a DRAFT statement surface. **Nothing here is proved.** The Lean
   kernel via CI is the sole judge; this document carries no kernel verdict.
2. If kernel-checked and promoted at stage two, MB1–MB4 would be five generic
   theorems about `mellin` over pinned Mathlib, with **no repo prerequisites**.
   They assert norm inequalities only — no value of any Mellin transform is
   computed, no transform is shown convergent (MB2–MB4 *assume* integrability
   of the bound), and no analytic continuation, functional equation, or growth
   statement is made.
3. No statement about `completedRiemannZeta₀`, `riemannZeta`, `riemannXi`,
   theta kernels, `WeakFEPair`, or any zero of any function is made anywhere
   in the surface. §3 is a non-normative citation of a possible future
   consumer and asserts nothing.
4. Closing this package closes **no barrier row** of
   `MATHLIB_CAPABILITY_MAP.md` and no `S1-*` item: generic machinery lowers
   the cost of a future exit but never retires a row.
5. **No claim of progress on the Riemann Hypothesis, in either direction, is
   made or implied.** No route is selected, opened, or advanced.

## Death conditions

Stop, split, or return this contract to design if any of the following is
needed to make a proof go through:

1. Any new axiom, `sorry`/`admit`, or unproved conjecture (the one invariant).
2. Any new `def`, structure, or instance (the package is five theorems; a
   proof needing a definition is a different package).
3. Any integrability, measurability, or convergence hypothesis added to
   **MB1** (its whole value is unconditionality; a guarded MB1 is the pool
   item done wrong).
4. Stating MB3 without the support-class hypothesis `hgsupp`, or MB4 without
   both endpoint hypotheses — the unrestricted forms are **false** (§1.3;
   two-sided rpow monotonicity fails across `t = 1`).
5. Any statement mentioning `completedRiemannZeta₀`, `hurwitzEvenFEPair`,
   `evenKernel`, `WeakFEPair`, ζ, or ξ entering the surface: that is the
   FUTURE consumer of §3, a separate contract, never this one.
6. Declaring any capability-map or barrier row closed, stale, or exited on
   the strength of this generic package
   (`MULTIPLICITY_CONTRACT.md` finding A4 pattern).
7. Bumping the Mathlib pin or toolchain to make any locator or lemma exist.
8. MEL-4a's fallback failing too: if MB4 cannot be closed even with the
   strengthened `hms` hypothesis, MB4 is **dropped** and MB1–MB3 (four
   signatures) are re-offered alone; MB1–MB3 do not depend on MB4.

### Return-to-stage-one condition

Any signature change (including MEL-4a's hypothesis strengthening and death
condition 8's drop of MB4) invalidates stage-one acceptance for the changed
statements only; unchanged statements' acceptance stands. Stage two may not
promote a signature that differs from the accepted surface.

---

## Annex A — Red-team re-verification (2026-08-07)

Independent adversarial review of DRAFT v1. Pin re-confirmed this session:
`git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD` =
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`. Every locator in this contract was
re-checked against that tree by `grep -n`/`sed` on the source (source reading
only; nothing was elaborated — this annex, like the contract, carries **no
kernel verdict**). All corrections below are already applied in place in the
body; none changes any MB1–MB4 signature, so stage-one status is unaffected
(§Return condition: no signature changed, nothing re-opens).

### A.1 Attack fronts and outcomes

1. **Integrability shape (the mandated attack).** Which statement shape is
   honest — unconditional real-valued, `ENNReal`/`tsub`, or
   `IntegrableOn`-guarded? Verified at the pin: `norm_integral_le_integral_norm`
   (Bochner/Basic.lean:924) is proved **unconditionally** (its proof does
   `by_cases h : AEStronglyMeasurable f μ` and zeroes the non-measurable case),
   and `setIntegral_congr_fun` (Bochner/Set.lean:73) is a congruence needing no
   integrability, so **MB1's unconditional real-valued shape is honest**:
   in every degenerate case both sides are `0` and the inequality holds. No
   `ENNReal` restatement is needed, and adding an `IntegrableOn` guard to MB1
   would be strictly weaker (death condition 3 correctly forbids it). MB2–MB4
   place `IntegrableOn` on the **bound** integrand, exactly matching the
   hypotheses of `norm_integral_le_of_norm_le` (:937, `hg`) and
   `setIntegral_mono_on` (Set.lean:764, `hf hg` via the :752 `include`) —
   without them those conclusions are false-by-junk (a non-integrable RHS
   evaluates to `0`), and `not_integrableOn_Ioi_rpow` (ImproperIntegrals.lean:160)
   confirms they are never vacuous. **Shape audit: PASS; no finding.**
2. **Exceptional points.** `t = 1` boundary of the strip split lands in the
   `1 ≤ t` branch (MEL-3b, correct); rpow junk at `t ≤ 0` never arises (every
   rewrite is under `ht : t ∈ Ioi 0`, and `Complex.norm_cpow_eq_rpow_re_of_pos`
   Pow/Real.lean:337 demands `0 < x`); `a = b` and `s.re ∈ {a, b}` degenerate
   soundly; namespaces verified (`norm_cpow_eq_rpow_re_of_pos` is inside
   `namespace Complex`; `rpow_nonneg`/`rpow_le_rpow_of_exponent_le`/`…_ge` are
   inside `namespace Real`); `lt_or_ge`/`le_or_gt` exist at the pin
   (Order/Defs/LinearOrder.lean:97/:100). **PASS; no finding.**
3. **Scope creep.** Signature count is exactly 5 (MB1 + MB2 + 2×MB3 + MB4);
   zero `def`s; §3 is non-normative and its seam locators are exact
   (RiemannZeta.lean:63; HurwitzZetaEven.lean:302, :254 with `f := ofReal ∘
   evenKernel a` at :255, kernel :65, `evenKernel_def` :77;
   AbstractFuncEq.lean:385/:81/:258); the name-collision scan was re-run this
   session with zero hits for all five proposed names; cross-references stand
   (`MULTIPLICITY_CONTRACT.md` finding A4 at :1942, death condition 9 at :383;
   `AnalyticAt.conj_conj` really did ride the conjugation package,
   `CONJ_SYMMETRY_CONTRACT.md`:5, merged PR #307). **PASS; no finding.**
4. **Citation audit.** All Bochner, Pow/Real, MulAction, L1Space, Restrict,
   BorelSpace/Order, Data/Complex, ImproperIntegrals, and MellinTransform
   declaration locators verified exact, except the four drift findings below.

### A.2 Findings (all fixed in place)

| ID | Severity | Finding | Disposition |
|---|---|---|---|
| R1 | LOW (citation accuracy) | The claim that Mathlib "runs exactly this `simp_rw` chain twice", second occurrence ":349", was wrong on both counts: the full chain `norm_smul, norm_cpow_eq_rpow_re_of_pos, sub_re, one_re` fires **once** (:198); at the second site the pin runs a *different* `simp_rw` set (:351) followed by `rw [norm_cpow_eq_rpow_re_of_pos ht]` at **:353**. (`:349` is the drifted locator inherited from `UPSTREAM_POOL.md:787`, which carries the same error; the pool file is outside this contract's write scope and left untouched.) | Mechanism §, §0 comment, MB1 deps, and pinned-table row corrected to :198 (chain) / :353 (step) |
| R2 | LOW (citation accuracy) | Strip-split precedent cited as ":350–355"; the split `rcases le_or_gt 1 t` actually spans **:354–:366**. MB2's "`filter_upwards` shape at :347" was doubly off: the in-tree extraction is at **:350** and is spelled `(ae_restrict_mem measurableSet_Ioi).mono`, not `filter_upwards`. | All three citations corrected |
| R3 | LOW (unsound prose justification; statement unaffected) | The sanity paragraph justified MB1's degenerate case "via `mellin_convergent_iff_norm`", but that lemma requires `hfc : AEStronglyMeasurable f` (MellinTransform.lean:190) and so cannot cover the non-measurable case it was invoked for. MB1's truth never depended on the paragraph (see A.1.1). | Paragraph rewritten with the honest chain: `integral_non_aestronglyMeasurable` / `integrable_norm_iff` + `integral_undef` |
| R4 | MEDIUM (obligation resolution, favorable) | MEL-4a route (i) hinged on a `Measurable.rpow_const`-style name "if present at the pin — not re-verified". Re-verified: **no such name exists at the pin** (zero grep hits for `Measurable.rpow_const`, `measurable_rpow`, `Measurable.rpow` tree-wide); route (i) as written was dead. Route (ii) was then located exactly: `continuousOn_id'` (Topology/ContinuousOn.lean:737) + `ContinuousOn.rpow_const` (Pow/Continuity.lean:278, side condition by `Or.inl (ne_of_gt ht)`) + `ContinuousOn.aestronglyMeasurable` (Integral/IntegrableOn.lean:760) + `.mul hmg`. | MEL-4a rewritten around route (ii); three locators added to the pinned table; severity kept MEDIUM for the remaining `congr`/`norm_of_nonneg`/`positivity` assembly, but the "lemma name not located" risk is retired |

### A.3 Verdict

**ACCEPTED AS DRAFT (stage one surface unchanged) — verdict of this review
only, not a kernel verdict.** The statement surface MB1–MB4 survives the
integrability, exceptional-point, and scope attacks unmodified: the
unconditional real-valued MB1 is the honest shape at this pin, and MB2–MB4's
`IntegrableOn`-on-the-bound hypotheses are exactly the ones their pinned
dependencies demand — neither droppable nor over-strong. Four findings
(3 LOW, 1 MEDIUM-favorable) were locator/prose defects and one obligation
resolution, all fixed in place; no signature, hypothesis, death condition, or
claim-boundary item changed. Nothing in this annex closes a barrier, selects
a route, or claims progress on RH in either direction.
