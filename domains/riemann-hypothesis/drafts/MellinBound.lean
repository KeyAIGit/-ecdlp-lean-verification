/-
DRAFTS-LANE DRAFT — Mellin norm-bound package (UPSTREAM-POOL §6), MB1-MB4.

This file is the non-built Lean draft of
`domains/riemann-hypothesis/MELLIN_BOUND_CONTRACT.md` (DRAFT v1, 2026-08-07,
with the red-team Annex A findings R1-R4 already folded in; the proofs below
follow the POST-fix skeletons). Statement surface: MB1-MB4, exactly five
public signatures, each character-identical to the contract's §2 `lean`
statement blocks. It is NOT part of any lake target, is outside the no-sorry
gate's scan surface, and the Lean kernel has NOT checked it: no CI workflow
elaborates this path, so no kernel verdict of any kind is claimed here. The
kernel's verdict, if ever, is delivered by a separate stage-two promotion PR
(contract §Two-stage gate); any statement change stops promotion and returns
the changed statement to contract review (§Return condition).

Contents: five generic `[GEN]` theorems bounding `‖mellin f s‖` by real
integrals in `s.re`. Zero `def`s, zero instances, zero axioms, zero `sorry`.
Nothing here mentions ζ, ξ, `completedRiemannZeta₀`, theta kernels, zeros, or
any route's research obligation (contract §Claim boundary; death condition 5).

Pinned Mathlib: fabf563a7c95a166b8d7b6efca11c8b4dc9d911f (v4.31.0), verified
this session via `git -C /workspace/leanprover-community/mathlib4 rev-parse
HEAD`. Every `file:line` locator below is from that tree.
-/
import Mathlib.Analysis.MellinTransform          -- mellin, MellinConvergent
import Mathlib.MeasureTheory.Integral.Bochner.Basic  -- norm_integral_le_integral_norm
import Mathlib.MeasureTheory.Integral.Bochner.Set    -- setIntegral_congr_fun, setIntegral_mono_on
import Mathlib.Analysis.SpecialFunctions.Pow.Real    -- norm_cpow_eq_rpow_re_of_pos, rpow monotonicity

-- Import list is the contract's proposed preamble verbatim (contract
-- §Packaging: "documentation of intent, to be minimized by `shake` at stage
-- two"). The MB4-only dependencies — `ContinuousOn.rpow_const`
-- (Pow/Continuity.lean:278, root namespace, verified after `end Real` :231),
-- `ContinuousOn.aestronglyMeasurable` (Integral/IntegrableOn.lean:760, root
-- namespace, verified after `end MeasureTheory` :716), `continuousOn_id'`
-- (Topology/ContinuousOn.lean:737), `IntegrableOn.add`
-- (Integral/IntegrableOn.lean:266), `Integrable.mono`
-- (L1Space/Integrable.lean:86), `AEStronglyMeasurable.mul`
-- (StronglyMeasurable/AEStronglyMeasurable.lean:300), `Real.norm_of_nonneg`
-- (Normed/Group/Real.lean:62) — all arrive through
-- `Mathlib.Analysis.MellinTransform`'s transitive closure (its own proofs use
-- this exact machinery at :193-:198 and :338-:366), as the contract records.

open Complex MeasureTheory Real Set
-- Contract preamble verbatim. `MeasureTheory` is load-bearing for the
-- unqualified `norm_integral_le_integral_norm` / `norm_integral_le_of_norm_le`
-- spellings below (both live inside `namespace MeasureTheory`,
-- Bochner/Basic.lean:141); `Complex`/`Real` mirror the in-tree call sites at
-- MellinTransform.lean:198/:353; `Set` supplies bare `Ioi`/`Ioo` in fallback
-- spellings. Primary statement text stays fully qualified (character-identical
-- to the contract), so a lost `open` degrades proofs, never statements.

/-! ## MB1. The core norm bound `[GEN]` — unconditional

No hypothesis at all: `norm_integral_le_integral_norm` (Bochner/Basic.lean:924)
is unconditional (its proof internalizes the non-`AEStronglyMeasurable` case),
and `setIntegral_congr_fun` (Bochner/Set.lean:73) is a congruence needing no
integrability. Adding any guard to MB1 is death condition 3. -/

theorem norm_mellin_le {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
    (f : ℝ → E) (s : ℂ) :
    ‖mellin f s‖ ≤ ∫ t : ℝ in Set.Ioi 0, t ^ (s.re - 1) * ‖f t‖ := by
  refine (norm_integral_le_integral_norm _).trans_eq ?_
  -- OBLIG MEL-1a (LOW): the opening `refine` must see `mellin f s` as the
  -- Bochner set integral up to unfolding of the plain `def` at
  -- MellinTransform.lean:91; the unifier delta-unfolds it at default
  -- transparency ("unfolds by `rfl`", UPSTREAM_POOL.md §6). `.trans_eq` is
  -- `LE.le.trans_eq` (Order/Basic.lean:82).
  -- Fallbacks, in the contract's order:
  --   unfold mellin
  --   show ‖∫ t : ℝ in Set.Ioi 0, (t : ℂ) ^ (s - 1) • f t‖ ≤ _
  --   rw [mellin]
  -- goal: ∫ t in Ioi 0, ‖(t:ℂ)^(s-1) • f t‖ = ∫ t in Ioi 0, t^(s.re-1) * ‖f t‖
  refine setIntegral_congr_fun measurableSet_Ioi fun t ht => ?_
  -- setIntegral_congr_fun: Bochner/Set.lean:73; measurableSet_Ioi:
  -- BorelSpace/Order.lean:197. `ht : t ∈ Set.Ioi 0` coerces to `0 < t` by
  -- `rfl` (`Set.mem_Ioi`) everywhere below — the in-tree precedent passes the
  -- membership directly at MellinTransform.lean:198 (`hT ht`).
  rw [norm_smul, Complex.norm_cpow_eq_rpow_re_of_pos ht, Complex.sub_re,
    Complex.one_re]
  -- norm_smul: MulAction.lean:98; Complex.norm_cpow_eq_rpow_re_of_pos:
  -- Pow/Real.lean:337; Complex.sub_re / Complex.one_re:
  -- Data/Complex/Basic.lean:640/:147. `rw` closes the residual `rfl` goal.
  -- OBLIG MEL-1b (LOW, the pool's named hardest step): if the `rw` sequence
  -- misfires on implicit-argument shape, use the in-tree spelling verbatim
  -- (MellinTransform.lean:198):
  --   simp_rw [norm_smul, Complex.norm_cpow_eq_rpow_re_of_pos ht,
  --     Complex.sub_re, Complex.one_re]
  -- or `simp only` with the same lemma set.

/-! ## MB2. Dominated form `[GEN]` — the form downstream consumers use

`‖mellin f s‖` is controlled by data depending on `s` only through `s.re`:
the RHS is constant on every vertical line `re s = σ`. The `IntegrableOn`
hypothesis sits on the BOUND, never on `f` (contract §1; without it the
conclusion is false-by-junk, `not_integrableOn_Ioi_rpow`,
ImproperIntegrals.lean:160). -/

theorem norm_mellin_le_of_norm_le {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
    {f : ℝ → E} {g : ℝ → ℝ} {s : ℂ}
    (hg : MeasureTheory.IntegrableOn (fun t : ℝ => t ^ (s.re - 1) * g t) (Set.Ioi 0))
    (h : ∀ t ∈ Set.Ioi (0 : ℝ), ‖f t‖ ≤ g t) :
    ‖mellin f s‖ ≤ ∫ t : ℝ in Set.Ioi 0, t ^ (s.re - 1) * g t := by
  refine (norm_integral_le_of_norm_le hg ?_)
  -- norm_integral_le_of_norm_le: Bochner/Basic.lean:937, at
  -- μ := volume.restrict (Ioi 0).
  -- OBLIG MEL-2a (LOW): `hg : IntegrableOn … (Ioi 0)` must unify with
  -- `Integrable … (volume.restrict (Ioi 0))` — definitionally equal
  -- (`IntegrableOn` is a `def` wrapper, IntegrableOn.lean:92).
  -- Fallback: pass `hg.integrable` (`IntegrableOn.integrable`,
  -- IntegrableOn.lean:95) instead of `hg`.
  -- OBLIG MEL-2b (LOW): mellin unfolding as in MEL-1a; same fallbacks
  -- (`unfold mellin` / `show` / `rw [mellin]` BEFORE the `refine`).
  filter_upwards [MeasureTheory.ae_restrict_mem measurableSet_Ioi] with t ht
  -- ae_restrict_mem: Restrict.lean:641. In-tree precedent for the same a.e.
  -- extraction: `(ae_restrict_mem measurableSet_Ioi).mono`,
  -- MellinTransform.lean:350 — that spelling is the fallback if
  -- `filter_upwards` frustrates:
  --   refine (MeasureTheory.ae_restrict_mem measurableSet_Ioi).mono
  --     fun t ht => ?_
  rw [norm_smul, Complex.norm_cpow_eq_rpow_re_of_pos ht, Complex.sub_re,
    Complex.one_re]
  -- Same chain and same MEL-1b `simp_rw` fallback as MB1.
  exact mul_le_mul_of_nonneg_left (h t ht) (Real.rpow_nonneg (le_of_lt ht) _)
  -- Real.rpow_nonneg: Pow/Real.lean:163; mul_le_mul_of_nonneg_left: core
  -- order algebra (not line-pinned, contract §MB2 deps).
  -- DEVIATION (proof-body only) from the skeleton's `ht.le`: dot notation on
  -- `ht : t ∈ Set.Ioi 0` resolves in the `Membership.mem` namespace, not
  -- `LT.lt`, so `.le` is not reliable there; `le_of_lt ht` elaborates by the
  -- same `mem_Ioi`-defeq coercion the skeleton already uses for
  -- `Complex.norm_cpow_eq_rpow_re_of_pos ht`.
  -- Fallback (if even `le_of_lt ht` frustrates):
  --   have ht' : (0 : ℝ) < t := ht
  --   exact mul_le_mul_of_nonneg_left (h t ht) (Real.rpow_nonneg ht'.le _)

/-! ## MB3. Monotonicity in `re s` on the fixed integrand class supported in `[1, ∞)` `[GEN]`

The class restriction (`g` vanishes on `Ioo 0 1`) is load-bearing: the
unrestricted form is FALSE (death condition 4; rpow monotonicity flips across
`t = 1`). First the bound-level monotonicity, then the mellin-level
consequence. -/

theorem setIntegral_rpow_mul_mono_exponent {g : ℝ → ℝ} {a b : ℝ} (hab : a ≤ b)
    (hg0 : ∀ t ∈ Set.Ioi (0 : ℝ), 0 ≤ g t)
    (hgsupp : ∀ t ∈ Set.Ioo (0 : ℝ) 1, g t = 0)
    (hga : MeasureTheory.IntegrableOn (fun t : ℝ => t ^ (a - 1) * g t) (Set.Ioi 0))
    (hgb : MeasureTheory.IntegrableOn (fun t : ℝ => t ^ (b - 1) * g t) (Set.Ioi 0)) :
    (∫ t : ℝ in Set.Ioi 0, t ^ (a - 1) * g t) ≤ ∫ t : ℝ in Set.Ioi 0, t ^ (b - 1) * g t := by
  refine MeasureTheory.setIntegral_mono_on hga hgb measurableSet_Ioi fun t ht => ?_
  -- setIntegral_mono_on: Bochner/Set.lean:764; its section variables `hf hg`
  -- at :752 are under `include`, so BOTH `IntegrableOn` arguments are leading
  -- explicit arguments in exactly this order (contract §0 pre-registered call
  -- shape).
  -- OBLIG MEL-3a (LOW): if the `include`-generated order differs, name them:
  --   refine MeasureTheory.setIntegral_mono_on (hf := hga) (hg := hgb)
  --     measurableSet_Ioi fun t ht => ?_
  rcases lt_or_ge t 1 with h1 | h1
  -- lt_or_ge: Order/Defs/LinearOrder.lean:97.
  -- OBLIG MEL-3b (LOW): the boundary case `t = 1` must land in the SECOND
  -- branch (`1 ≤ t`, both rpow factors equal 1); `lt_or_ge t 1` places it
  -- there. Do not switch to `Ioc 0 1` support without re-checking this seam.
  · simp [hgsupp t ⟨ht, h1⟩]
    -- both sides are `_ * 0`; `simp` closes `0 ≤ 0`. The anonymous
    -- constructor `⟨ht, h1⟩ : t ∈ Set.Ioo 0 1` elaborates through the
    -- defeq `t ∈ Ioo 0 1 ↔ 0 < t ∧ t < 1` (`Set.mem_Ioo` is `rfl`).
    -- Fallback (structured):
    --   rw [hgsupp t ⟨ht, h1⟩, mul_zero, mul_zero]
  · exact mul_le_mul_of_nonneg_right
      (Real.rpow_le_rpow_of_exponent_le h1 (by linarith)) (hg0 t ht)
    -- Real.rpow_le_rpow_of_exponent_le: Pow/Real.lean:613 (`hx : 1 ≤ x`);
    -- the `by linarith` closes `a - 1 ≤ b - 1` from `hab`.
    -- Fallback for the linarith side goal: `sub_le_sub_right hab 1`.

theorem norm_mellin_le_of_re_le {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
    {f : ℝ → E} {g : ℝ → ℝ} {s : ℂ} {b : ℝ} (hsb : s.re ≤ b)
    (hg0 : ∀ t ∈ Set.Ioi (0 : ℝ), 0 ≤ g t)
    (hgsupp : ∀ t ∈ Set.Ioo (0 : ℝ) 1, g t = 0)
    (h : ∀ t ∈ Set.Ioi (0 : ℝ), ‖f t‖ ≤ g t)
    (hgs : MeasureTheory.IntegrableOn (fun t : ℝ => t ^ (s.re - 1) * g t) (Set.Ioi 0))
    (hgb : MeasureTheory.IntegrableOn (fun t : ℝ => t ^ (b - 1) * g t) (Set.Ioi 0)) :
    ‖mellin f s‖ ≤ ∫ t : ℝ in Set.Ioi 0, t ^ (b - 1) * g t := by
  exact (norm_mellin_le_of_norm_le hgs h).trans
    (setIntegral_rpow_mul_mono_exponent hsb hg0 hgsupp hgs hgb)
  -- Pure composition of MB2 with MB3's first signature at `a := s.re`;
  -- `LE.le.trans` is core. No fallback registered (both inputs are this
  -- file's own statements, applied at their exact signatures).

/-! ## MB4. Uniform bound on a closed vertical strip `[GEN]` — the seam-facing specialization

Endpoint data at `re s = a` and `re s = b` yields one `s`-independent bound on
all of `a ≤ re s ≤ b`, with no support restriction on `g`. The
`AEStronglyMeasurable` hypothesis `hmg` is carried explicitly (contract §1.4):
middle-exponent integrability goes through `Integrable.mono`
(L1Space/Integrable.lean:86), whose measurability leg is not derivable from
bare endpoint `IntegrableOn` hypotheses. This proof is obligation MEL-4a, the
package's only MEDIUM. -/

theorem norm_mellin_le_add_of_re_mem_Icc {E : Type*} [NormedAddCommGroup E]
    [NormedSpace ℂ E] {f : ℝ → E} {g : ℝ → ℝ} {s : ℂ} {a b : ℝ}
    (ha : a ≤ s.re) (hb : s.re ≤ b)
    (hg0 : ∀ t ∈ Set.Ioi (0 : ℝ), 0 ≤ g t)
    (h : ∀ t ∈ Set.Ioi (0 : ℝ), ‖f t‖ ≤ g t)
    (hmg : MeasureTheory.AEStronglyMeasurable g (MeasureTheory.volume.restrict (Set.Ioi 0)))
    (hga : MeasureTheory.IntegrableOn (fun t : ℝ => t ^ (a - 1) * g t) (Set.Ioi 0))
    (hgb : MeasureTheory.IntegrableOn (fun t : ℝ => t ^ (b - 1) * g t) (Set.Ioi 0)) :
    ‖mellin f s‖ ≤ (∫ t : ℝ in Set.Ioi 0, t ^ (a - 1) * g t)
      + ∫ t : ℝ in Set.Ioi 0, t ^ (b - 1) * g t := by
  -- Step 1: pointwise two-endpoint domination on Ioi 0 (in-tree maneuver,
  -- MellinTransform.lean:354-366).
  have hpt : ∀ t ∈ Set.Ioi (0 : ℝ),
      t ^ (s.re - 1) * g t ≤ t ^ (a - 1) * g t + t ^ (b - 1) * g t := by
    intro t ht
    rcases le_or_gt 1 t with h1 | h1
    -- le_or_gt: Order/Defs/LinearOrder.lean:100. `t = 1` lands in the first
    -- branch here; both branches are sound at `t = 1` regardless (both rpow
    -- factors are 1), so this split has no boundary seam.
    · have := Real.rpow_le_rpow_of_exponent_le h1 (by linarith : s.re - 1 ≤ b - 1)
      nlinarith [Real.rpow_nonneg (le_of_lt ht) (a - 1), hg0 t ht,
        mul_le_mul_of_nonneg_right this (hg0 t ht)]
      -- OBLIG MEL-4b (LOW): the `nlinarith` closer is convenience. Structured
      -- fallback (replaces the `nlinarith` line only):
      --   calc t ^ (s.re - 1) * g t
      --       ≤ t ^ (b - 1) * g t :=
      --         mul_le_mul_of_nonneg_right this (hg0 t ht)
      --     _ ≤ t ^ (a - 1) * g t + t ^ (b - 1) * g t :=
      --         le_add_of_nonneg_left
      --           (mul_nonneg (Real.rpow_nonneg (le_of_lt ht) _) (hg0 t ht))
    · have := Real.rpow_le_rpow_of_exponent_ge ht h1.le (by linarith : a - 1 ≤ s.re - 1)
      -- Real.rpow_le_rpow_of_exponent_ge: Pow/Real.lean:639. `ht` coerces to
      -- `0 < t` by defeq; `h1.le` on the `1 > t` disjunct is the in-tree
      -- spelling at MellinTransform.lean:363 (`rpow_le_rpow_of_exponent_ge ht
      -- h.le`), so it is known to resolve at the pin.
      nlinarith [Real.rpow_nonneg (le_of_lt ht) (b - 1), hg0 t ht,
        mul_le_mul_of_nonneg_right this (hg0 t ht)]
      -- MEL-4b structured fallback, mirror of the first branch:
      --   calc t ^ (s.re - 1) * g t
      --       ≤ t ^ (a - 1) * g t :=
      --         mul_le_mul_of_nonneg_right this (hg0 t ht)
      --     _ ≤ t ^ (a - 1) * g t + t ^ (b - 1) * g t :=
      --         le_add_of_nonneg_right
      --           (mul_nonneg (Real.rpow_nonneg (le_of_lt ht) _) (hg0 t ht))
  -- Step 2: middle-exponent integrability from the endpoints (OBLIG MEL-4a,
  -- MEDIUM — the riskiest step of the package; route (ii) of Annex A finding
  -- R4, fully located at the pin).
  have hsum : MeasureTheory.IntegrableOn
      (fun t : ℝ => t ^ (a - 1) * g t + t ^ (b - 1) * g t) (Set.Ioi 0) := hga.add hgb
  -- IntegrableOn.add: IntegrableOn.lean:266, concluding for the `Pi.instAdd`
  -- sum `f + g`; the ascribed lambda type forces that (definitionally equal)
  -- reading once, here, instead of at every use site.
  -- Fallback: drop the ascription (`have hsum := hga.add hgb`) and let each
  -- use site unify the `Pi.add`/lambda shapes itself.
  have hc : ContinuousOn (fun t : ℝ => t ^ (s.re - 1)) (Set.Ioi 0) :=
    (continuousOn_id' (Set.Ioi (0 : ℝ))).rpow_const fun t ht => Or.inl (ne_of_gt ht)
  -- continuousOn_id': Topology/ContinuousOn.lean:737 — its set argument is
  -- EXPLICIT, so it is supplied here (bare `continuousOn_id'.rpow_const`, the
  -- contract skeleton's spelling, is dot notation on a Pi-type term and may
  -- not resolve; supplying `(Set.Ioi (0 : ℝ))` is the same term).
  -- ContinuousOn.rpow_const: Pow/Continuity.lean:278 (root namespace, verified
  -- at the pin); side condition `∀ x ∈ s, x ≠ 0 ∨ 0 ≤ p` discharged by
  -- `Or.inl (ne_of_gt ht)` exactly as the contract records.
  -- Fallback (if the `Or.inl` shape misfires on the beta-redex `(fun x => x) t`):
  --   fun t ht => Or.inl (ne_of_gt (show (0 : ℝ) < t from ht))
  have hms : MeasureTheory.AEStronglyMeasurable (fun t : ℝ => t ^ (s.re - 1) * g t)
      (MeasureTheory.volume.restrict (Set.Ioi 0)) :=
    (hc.aestronglyMeasurable measurableSet_Ioi).mul hmg
  -- ContinuousOn.aestronglyMeasurable: Integral/IntegrableOn.lean:760 (root
  -- namespace; the `SecondCountableTopologyEither`/`OpensMeasurableSpace`/
  -- `PseudoMetrizableSpace` side instances are satisfied by ℝ, contract
  -- MEL-4a); AEStronglyMeasurable.mul:
  -- StronglyMeasurable/AEStronglyMeasurable.lean:300. The ascribed type again
  -- absorbs the `Pi.instMul`/lambda defeq.
  -- In-tree analogue of the continuity-on-`Ioi 0` maneuver:
  -- MellinTransform.lean:338/:345 (`continuousAt_ofReal_cpow_const`).
  have hgs : MeasureTheory.IntegrableOn (fun t : ℝ => t ^ (s.re - 1) * g t) (Set.Ioi 0) := by
    refine MeasureTheory.Integrable.mono hsum.integrable hms ?_
    -- Integrable.mono: L1Space/Integrable.lean:86, argument order
    -- `(hg) (hf) (h)`.
    -- DEVIATION (proof-body only) from the skeleton's
    -- `refine (hga.add hgb).mono ?_ ?_`: dot notation on an `IntegrableOn`
    -- term is CAPTURED by `IntegrableOn.mono` (IntegrableOn.lean:124,
    -- signature `(hs : s ⊆ t) (hμ : μ ≤ ν)` — a set/measure monotonicity
    -- lemma, the wrong target), so the skeleton's spelling cannot reach
    -- L1Space/Integrable.lean:86. `hsum.integrable`
    -- (`IntegrableOn.integrable`, IntegrableOn.lean:95) makes the
    -- restrict-measure reading explicit, and `hms` discharges the
    -- measurability leg directly. Same lemma, same hypotheses, same goal.
    -- Fallback (if the `IntegrableOn` goal refuses the `Integrable`-headed
    -- refine): precede the `refine` with
    --   show MeasureTheory.Integrable (fun t : ℝ => t ^ (s.re - 1) * g t)
    --     (MeasureTheory.volume.restrict (Set.Ioi 0))
    filter_upwards [MeasureTheory.ae_restrict_mem measurableSet_Ioi] with t ht
    have ht' : (0 : ℝ) < t := ht
    -- DEVIATION (proof-body only): `ht'` (and `h0` below, from the skeleton)
    -- restate the context in the `0 < _` / `0 ≤ _` shapes `positivity`'s
    -- hypothesis lookup consumes; `ht` alone is membership-shaped.
    have h0 : (0 : ℝ) ≤ g t := hg0 t ht
    rw [Real.norm_of_nonneg (by positivity), Real.norm_of_nonneg (by positivity)]
    -- Real.norm_of_nonneg: Normed/Group/Real.lean:62. First rewrite hits the
    -- LHS norm, second the RHS norm.
    -- Fallbacks (contract MEL-4a bookkeeping), in order:
    --   (a) if a stray beta-redex blocks the `rw` pattern, precede it with
    --       show ‖t ^ (s.re - 1) * g t‖ ≤ ‖t ^ (a - 1) * g t + t ^ (b - 1) * g t‖
    --   (b) if `positivity` misses, give the proofs explicitly:
    --       rw [Real.norm_of_nonneg (mul_nonneg (Real.rpow_nonneg ht'.le _) h0),
    --         Real.norm_of_nonneg (add_nonneg
    --           (mul_nonneg (Real.rpow_nonneg ht'.le _) h0)
    --           (mul_nonneg (Real.rpow_nonneg ht'.le _) h0))]
    exact hpt t ht
  -- Step 3: assemble.
  calc ‖mellin f s‖
      ≤ ∫ t in Set.Ioi 0, t ^ (s.re - 1) * g t := norm_mellin_le_of_norm_le hgs h
    _ ≤ ∫ t in Set.Ioi 0, (t ^ (a - 1) * g t + t ^ (b - 1) * g t) :=
        MeasureTheory.setIntegral_mono_on hgs hsum measurableSet_Ioi hpt
    _ = _ := MeasureTheory.integral_add hga hgb
  -- integral_add: Bochner/Basic.lean:241, at μ := volume.restrict (Ioi 0);
  -- the calc's middle integrand is already the pointwise sum it needs, and
  -- `hsum` (not the raw `hga.add hgb`) keeps the second step's `g` in the
  -- lambda shape of the middle integrand.
  -- OBLIG MEL-4c (LOW): if the final step's elaboration balks at
  -- `IntegrableOn` vs `Integrable`, apply MEL-2a's defeq note:
  --   _ = _ := MeasureTheory.integral_add hga.integrable hgb.integrable
