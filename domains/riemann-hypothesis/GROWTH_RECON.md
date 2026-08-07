# `S1-GROWTH` reconnaissance note

Status: **reconnaissance only — capability note, not a contract, not a Lean
draft, not a promotion.** Nothing here claims a proof, selects or unparks a
route, asserts that any barrier is closed or stale, or asserts progress on the
truth of the Riemann Hypothesis. Honest negative findings are recorded on the
same footing as positive ones. No barrier is re-scoped: the exit string at
`MATHLIB_CAPABILITY_MAP.md:388` is quoted, never narrowed, and no theorem below
is offered as a substitute for it.

Audit date: 2026-08-07

Mathlib revision: `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0), verified
this session by `git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD`.
Local checkout read with ripgrep/`sed` only; **no Lean toolchain is available in
this container, so every feasibility judgement below is a source-reading
estimate and none of it has been kernel-checked.** Following
`GLOBAL_ZEROS_RECON.md` Annex A-5, no search below used `rg -E` (ripgrep parses
that as `--encoding` and the invocation aborts without running); every search
was `rg -n` / `rg -ni`. Line numbers are declaration-keyword lines, not
doc-comment openers (Annex A-8).

Barrier under examination, `MATHLIB_CAPABILITY_MAP.md:388`:

> `S1-GROWTH` | no zeta/xi vertical or order-one growth theorem | Hadamard and
> contour shifts | exit evidence: explicit quantitative bounds sufficient for
> the selected theorem

Repository state assumed: `TargetBridge.lean` and `Xi.lean` merged and
kernel-checked; `Conj.lean` CI-green and pending merge; `S1-MULTIPLICITY` in
flight. The xi normalization in play is
`riemannXi s = (1 + s * (s - 1) * completedRiemannZeta₀ s) / 2`
(`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Xi.lean:41`).

Relation to the sibling note. `GLOBAL_ZEROS_RECON.md` concluded that
`S1-GLOBAL-ZEROS` should not be attempted next and named `S1-GROWTH` as the real
gate (its §7, and Option D at `:539-546`). This note is the execution of that
Option D. It contradicts none of the sibling's verified findings; it refines two
of its estimates, corrects one of its Annex claims in the direction unfavourable
to convenience, and disputes the *queue-order* implicature of "the real gate"
while confirming its dependency content. See §8.

---

## 1. Headline

Four things, stated separately because they are easy to conflate.

1. **The pin is far richer in *conditional strip machinery* than the row's
   nine-word gap phrase suggests, and completely empty of the *unconditional
   ζ/ξ bounds* the row's exit string names.** Phragmén–Lindelöf exists in
   genuine vertical-strip form (already map row 134); Hadamard's **three-lines**
   theorem exists in general-strip form with a named sup-norm-on-vertical-lines
   function `sSupNormIm`, and is **absent from `MATHLIB_CAPABILITY_MAP.md`
   entirely** — the one genuine inventory gap this note found (§2.2, verified:
   `rg -ni "three.?line|Complex/Hadamard|sSupNormIm"` over the map and the
   search log returns 0 hits). Every one of these tools is a *consumer* of a
   bound, not a producer of one. That is the precise sense in which this row is
   a gate.

2. **`S1-GROWTH` is not one statement.** The row texts decompose it into three
   growth facts with three different route profiles, three different pin-side
   feasibilities, and three different neutrality verdicts:
   - **G1** — polynomial growth of ξ in a vertical strip (equivalently:
     boundedness of `completedRiemannZeta₀` on `a ≤ re s ≤ b`, uniformly in
     `Im s`). Consumed by `map:134`, `map:278`, `map:366`, triage item (iv), and
     — this is the finding the sibling does not carry — by Route B through
     `SC-NB-05` (`SOURCE_CONTRACTS.md:780-794`).
   - **G2** — global entire order ≤ 1 for ξ. `SC-XI-01`(1)
     (`SOURCE_CONTRACTS.md:182-183`), `map:154`, `map:278-279`. Consumers:
     Routes A and C only, and its declared purpose in every row that names it is
     the Hadamard product.
   - **G3** — vertical growth of `ζ'/ζ`, Landau-type log-derivative estimates,
     and the contour-shift/residue package. Triage items (vi), (vii);
     `map:366`; `SC-BOMB-02`. Overlaps `S1-EXPLICIT` (`map:390`).
   The row's exit string does not distinguish them, and its "blocks" column
   ("Hadamard and contour shifts") names only G2's and G3's consumers.

3. **The natural production route for G1 is broken at exactly one nameable,
   route-neutral, RH-free generic lemma, and at no other pinned point I could
   find.** The repo's ξ carries `completedRiemannZeta₀`, which is by
   construction `mellin ((hurwitzEvenFEPair 0).f_modif) (s/2) / 2`
   (§2.6), and the pin proves the Mellin integral converges at **every** `s`
   (`StrongFEPair.hasMellin`, `AbstractFuncEq.lean:203`, applied through
   `toStrongFEPair`, `:307`). Since `‖(t:ℂ)^(s-1)‖ = t^(re s - 1)` for `t > 0`
   (`Pow/Real.lean:337`), a modulus bound depends only on `re s`. The missing
   step is a norm bound for `mellin`: `rg -n "norm_mellin|‖mellin" Mathlib/`
   returns **0 hits**, tree-wide. This is inventory, not a plan, and building
   that lemma would be an *ingredient*, not an exit. §7.3 states the reasons not
   to inflate it.

4. **As written, this barrier is no more closable by route-neutral work than the
   one the sibling declined, and for a structurally identical reason.** Its
   exit evidence is "explicit quantitative bounds sufficient for **the selected
   theorem**", and `ROUTE_TRIAGE.md` selected zero theorem-bearing routes
   (`:294 ff.`). There is no selected theorem for a bound to be sufficient for,
   so the exit condition is currently unsatisfiable by construction. Separately,
   `S1-GROWTH` has **no contract, no draft, no ledger row, and no accepted
   statement surface**: repo-wide the string occurs in exactly two places
   outside the sibling note — `MATHLIB_CAPABILITY_MAP.md:388` and `:553` — and
   `domains/riemann-hypothesis/drafts/` contains `RiemannTargetBridge.lean`,
   `RiemannXi.lean`, `RiemannConj.lean`, `RiemannMult.lean` and no growth file.
   See §8 and §9.

---

## 2. Inventory: what exists at the pin

All locators re-verified this session against the pinned tree by direct `sed -n`
extraction of the cited line. Where a scout cited a different line, the
correction is recorded in §5 and the Annex.

### 2.1 Phragmén–Lindelöf — the only genuine vertical-strip principle

`Mathlib/Analysis/Complex/PhragmenLindelof.lean`, 828 lines; **twenty-four**
declarations (`:65`, `:80`, three horizontal, three vertical, twelve quadrant,
four half-plane — corrected in Annex B-5); `variable [NormedSpace ℂ E]
{a b C : ℝ} {f g : ℂ → E} {z : ℂ}` (`:96`; the file's first `variable` line is
`:61`). Namespace `PhragmenLindelof` (`:54`). Already at **map row 134**, cited
there by `vertical_strip` alone.

```
PhragmenLindelof.lean:275
theorem vertical_strip (hfd : DiffContOnCl ℂ f (re ⁻¹' Ioo a b))
    (hB : ∃ c < π / (b - a), ∃ B, f =O[comap (_root_.abs ∘ im) atTop ⊓ 𝓟 (re ⁻¹' Ioo a b)]
      fun z ↦ expR (B * expR (c * |z.im|)))
    (hle_a : ∀ z : ℂ, re z = a → ‖f z‖ ≤ C) (hle_b : ∀ z, re z = b → ‖f z‖ ≤ C)
    (hza : a ≤ re z) (hzb : re z ≤ b) : ‖f z‖ ≤ C
```

Region: the open strip `re ⁻¹' Ioo a b`, with the conclusion on the closed strip
via `hza`/`hzb`. The escape clause `hB` is **doubly exponential in `|im z|`**
and only along `comap (|im ·|) atTop ⊓ 𝓟 (strip)`, i.e. it is very generous —
any function of finite order in the strip satisfies it comfortably. The two
boundary hypotheses are pointwise on the lines `re z = a`, `re z = b`, with **one
shared constant `C`**.

| capability | pinned declaration |
|---|---|
| vertical strip, zero and equality variants | `:275`, `eq_zero_on_vertical_strip` `:303`, `eqOn_vertical_strip` `:321` |
| horizontal strip family | `horizontal_strip` `:113`, `:231`, `:249` (growth condition in `|re z|`) |
| quadrants I–IV | `:344`, `:446`, `:508`, `:574`; zero/equality variants `:409/:426`, `:472/:489`, `:539/:555`, `:603/:620`; growth `expR (B * ‖z‖^c)`, `c < 2` |
| right half-plane | `right_half_plane_of_tendsto_zero_on_real` `:646`, `…_of_bounded_on_real` `:717`, `eq_zero_on_right_half_plane_of_superexponential_decay` `:759`, `eqOn_…` `:812` |
| difference-of-growth auxiliaries | `isBigO_sub_exp_exp` `:65`, `isBigO_sub_exp_rpow` `:80` |

`vertical_strip` is proved from `horizontal_strip` by the rotation `z ↦ z * -I`.
The half-plane family is anchored at `re = 0` (region literally
`{z | 0 < z.re}`, boundary hypothesis literally `∀ x : ℝ, ‖f (x * I)‖ ≤ C`);
there is no `{z | σ < z.re}` version and no translation lemma.

### 2.2 Hadamard **three lines** — present, general strip, **not in the capability map**

`Mathlib/Analysis/Complex/Hadamard.lean`, namespace `Complex.HadamardThreeLines`.
This file is not cited anywhere in `MATHLIB_CAPABILITY_MAP.md` or
`MATHLIB_SEARCH_LOG.md` (verified by search). The map's `NOT-FOUND-IN-SCOPE` row
`:155` ("canonical product or Hadamard factorization") is **correct** — that is a
different theorem — but a reader can take "no Hadamard" for more than it says.

```
Hadamard.lean:70   def verticalStrip (a b : ℝ) : Set ℂ := re ⁻¹' Ioo a b
Hadamard.lean:73   def verticalClosedStrip (a b : ℝ) : Set ℂ := re ⁻¹' Icc a b
Hadamard.lean:77   noncomputable def sSupNormIm (f : ℂ → E) (x : ℝ) : ℝ := sSup ((norm ∘ f) '' re ⁻¹' {x})
Hadamard.lean:246  noncomputable def interpStrip (z : ℂ) : ℂ
Hadamard.lean:301  noncomputable def interpStrip' (f : ℂ → E) (l u : ℝ) (z : ℂ) : ℂ

Hadamard.lean:607
lemma norm_le_interp_of_mem_verticalClosedStrip' {f : ℂ → E} {z : ℂ} {a b l u : ℝ}
    (hul : l < u) (hz : z ∈ verticalClosedStrip l u) (hd : DiffContOnCl ℂ f (verticalStrip l u))
    (hB : BddAbove ((norm ∘ f) '' verticalClosedStrip l u))
    (ha : ∀ z ∈ re ⁻¹' {l}, ‖f z‖ ≤ a) (hb : ∀ z ∈ re ⁻¹' {u}, ‖f z‖ ≤ b) :
    ‖f z‖ ≤ a ^ (1 - (z.re - l) / (u - l)) * b ^ ((z.re - l) / (u - l))
```

The two `def` lines and `sSupNormIm` above are **condensed**, not byte-verbatim:
at the pin `:70`/`:73` bind `(a : ℝ) (b : ℝ)` separately, and `sSupNormIm` spans
`:77-79` carrying its own `{E : Type*} [NormedAddCommGroup E]` binders. The
`:607` block is byte-verbatim. (Annex B-8.)

with `norm_le_interpStrip_of_mem_verticalClosedStrip` `:588`, the `[0,1]`
specializations `:463` and `:477`, and the sup-norm API `sSupNormIm_nonneg` `:99`,
`norm_le_sSupNormIm` `:133`, `norm_lt_sSupNormIm_eps` `:143`,
`sSupNormIm_scale_left/right` `:343`/`:367`, `interpStrip_scale` `:391`.

**Critical hypothesis, stated plainly and deliberately three times in this
note.** Every three-lines statement requires
`hB : BddAbove ((norm ∘ f) '' verticalClosedStrip l u)` — *uniform boundedness of
`f` on the whole closed strip*. The theorem interpolates between two
**already finite** line-sups; it cannot manufacture them. `sSupNormIm f x` is a
bare `sSup`, hence `0` by junk convention on an unbounded set, so finiteness is a
proof obligation, not a side note. This is the single most misreadable signature
in the inventory: it *looks* like the classical Lindelöf convexity tool and sits
on exactly the right region.

**Naming hazard.** `Complex.HadamardThreeLines.verticalStrip` (`Hadamard.lean:70`,
a subset of ℂ cut by `re`) is unrelated to `UpperHalfPlane.verticalStrip`
(`Analysis/Complex/UpperHalfPlane/Topology.lean:98`,
`{z : ℍ | |z.re| ≤ A ∧ B ≤ z.im}`). Anything written here must carry the
namespace.

### 2.3 Maximum modulus, Schwarz, Cauchy estimates, Borel–Carathéodory

| capability | pinned declaration | shape |
|---|---|---|
| max modulus, boundary ⇒ interior | `Complex.norm_le_of_forall_mem_frontier_norm_le`, `AbsMax.lean:400` | **any bounded `U`**; a strip is unbounded, so this reaches a strip only as a truncated rectangle |
| max attained on frontier | `Complex.exists_mem_frontier_isMaxOn_norm`, `AbsMax.lean:383` | needs `[FiniteDimensional ℂ E]` |
| Cauchy estimate, iterated | `Complex.norm_iteratedDeriv_le_of_forall_mem_sphere_norm_le`, `Liouville.lean:44` | circle sup `C` ⇒ `‖iteratedDeriv n f c‖ ≤ n ! * C / R ^ n`, needs `[CompleteSpace F]` |
| Cauchy estimate, first order | `Complex.norm_deriv_le_of_forall_mem_sphere_norm_le`, `Liouville.lean:76` | `‖deriv f c‖ ≤ C / R` |
| Schwarz | `Complex.dist_le_div_mul_dist_of_mapsTo_ball` `Schwarz.lean:188`, `norm_fderiv_le_div_of_mapsTo_ball` `:201`, `norm_deriv_le_div_of_mapsTo_ball` `:255`, `norm_dslope_le_div_of_mapsTo_ball` `:277` | ball only |
| Borel–Carathéodory | `Complex.borelCaratheodory`, `BorelCaratheodory.lean:109`; `borelCaratheodory_zero` `:86` | `ball 0 R` **only** (not `ball c R`); hypothesis is on the **real part** (`MapsTo f (ball 0 R) {z \| z.re ≤ M}`, `0 < M`); conclusion fully explicit |

`Complex.borelCaratheodory` is already at the map's 2026-08-05 addendum
(`MATHLIB_CAPABILITY_MAP.md:490-492`) and at triage item (vi). It is the pinned
theorem whose *hypothesis shape* matches the classical Landau/log-derivative
technique — and for `f = log ξ` its `Re f ≤ M` hypothesis is a sup bound on
`‖ξ‖`, i.e. `S1-GROWTH` again, upstream of itself.

Liouville at the pin is **bounded-range only**: `Complex.liouville_theorem_aux`
`Liouville.lean:92`, `exists_eq_const_of_bounded` `:128`,
`eq_const_of_tendsto_cocompact` `:135`, and the harmonic analogue
`Harmonic/Liouville.lean:47`. No polynomial-growth Liouville (§3.1).

### 2.4 The one pinned consumer that is live today

```
JensenFormula.lean:389
theorem AnalyticOnNhd.sum_divisor_le {c : ℂ} {r R M : ℝ} {f : ℂ → ℂ} (r_pos : 0 < |r|)
    (r_lt_R : |r| < |R|) (hM : 1 ≤ M) (h₁f : AnalyticOnNhd ℂ f (closedBall c |R|))
    (h₂f : f c ≠ 0) (f_bound : ∀ z ∈ sphere c |R|, ‖f z‖ ≤ M) :
    ∑ᶠ u, divisor f (closedBall c |r|) u ≤ Real.log (M / ‖f c‖) / Real.log (R / r)
```

Already **map row 133**, with the gap text "no zeta/xi growth input" — the map
already named this barrier's blockage at that row. Companions
`MeromorphicOn.circleAverage_log_norm` `:307`, `AnalyticOnNhd.circleAverage_log_norm`
`:375`.

For `f = riemannXi`, `c = 0`: analyticity follows from `differentiable_riemannXi`
(`Xi.lean:46`) via `analyticOnNhd_univ_iff_differentiable`
(`CauchyIntegral.lean:678`), and `f c ≠ 0` is already kernel-checked in-repo as
`riemannXi_zero : riemannXi 0 = 1 / 2` (`Xi.lean:72`). **`f_bound` is the only
ungiven hypothesis** — a source-reading estimate, not kernel-checked. Two
consequences worth recording: the hypothesis is a **circle** sup, not a strip
sup; and the conclusion counts on `|s| ≤ r`, i.e. radially, matching
`SC-XI-01`(2)'s `|ρ| ≤ T` and *not* `SC-BOMB-02`'s `|Im ρ| < T`.

### 2.5 Growth-shaped objects that are not this barrier's objects

- Nevanlinna: `ValueDistribution.proximity` (`Proximity/Basic.lean:50`),
  `ValueDistribution.characteristic` (`CharacteristicFunction.lean:53`),
  First Main Theorem (`FirstMainTheorem.lean:97,:109,:131,:160`),
  `logCounting_isBigO_one_iff_analyticOnNhd` (`LogCounting/Asymptotic.lean:108`).
  All radial and logarithmically weighted — the sibling's amendment 2 mismatch
  applies here on the growth side exactly as it does on the counting side.
- `Asymptotics/ExpGrowth.lean:38,:41` — `expGrowthInf`/`expGrowthSup` over
  `u : ℕ → ℝ≥0∞`, `liminf/limsup (log (u n) / n)`. Right *idiom* for how a
  growth rate is packaged at the pin (`EReal`-valued, `limsup`-based); wrong
  index type and wrong normalization (one `log`, divided by `n`, not
  `log log M(r) / log r`). Recorded only so "no order definition exists" is not
  misread as "no `limsup`-of-`log` idiom exists".

### 2.6 The Mellin / FE-pair construction layer — a *growth* resource, currently mapped only as construction

This is the load-bearing positive find, and it is not in the map under any
growth heading.

```
AbstractFuncEq.lean:81   structure WeakFEPair
AbstractFuncEq.lean:258  def f_modif : ℝ → E :=
                           (Ioi 1).indicator (fun x ↦ P.f x - P.f₀) +
                           (Ioo 0 1).indicator (fun x ↦ P.f x - (P.ε * ↑(x ^ (-P.k))) • P.g₀)
AbstractFuncEq.lean:307  def toStrongFEPair : StrongFEPair E where f := P.f_modif; …
AbstractFuncEq.lean:385  def Λ₀ : ℂ → E := mellin P.f_modif
AbstractFuncEq.lean:203  theorem hasMellin (s : ℂ) : HasMellin P.f s (P.Λ s)     -- namespace StrongFEPair
```

`StrongFEPair.hasMellin` is quantified over **all** `s : ℂ` (verified by reading
`:200-205`: it obtains `⟨_, ht⟩ := exists_gt s.re` and `⟨_, hu⟩ := exists_lt s.re`
and feeds `mellinConvergent_of_isBigO_rpow`). Applied through `toStrongFEPair`,
it gives `MellinConvergent f_modif s` for every `s`. Supporting:
`hf_modif_int` `:267`, `hf_modif_top` `:298`, `differentiable_Λ₀` `:399`,
`WeakFEPair.hasMellin` `:414`, `functional_equation₀` `:429`, `hf_top'` `:188`,
`hf_zero'` `:192`.

Chain down to the repo's ξ, each link verified:

```
Xi.lean:41                 riemannXi s = (1 + s * (s - 1) * completedRiemannZeta₀ s) / 2
RiemannZeta.lean:63        def completedRiemannZeta₀ (s : ℂ) : ℂ := completedHurwitzZetaEven₀ 0 s
RiemannZeta.lean:73        completedHurwitzZetaEven₀ 0 s = completedRiemannZeta₀ s := rfl
HurwitzZetaEven.lean:302   def completedHurwitzZetaEven₀ a s = ((hurwitzEvenFEPair a).Λ₀ (s / 2)) / 2
HurwitzZetaEven.lean:254   def hurwitzEvenFEPair (a) : WeakFEPair ℂ  -- k = 1/2, ε = 1, f₀ = if a = 0 then 1 else 0, g₀ = 1
```

Mellin layer: `MellinConvergent` `MellinTransform.lean:45`, `mellin` `:91`,
`HasMellin` `:160`, `mellinConvergent_of_isBigO_rpow` `:277`,
`mellin_differentiableAt_of_isBigO_rpow` `:401`,
`mellinConvergent_of_isBigO_rpow_exp` `:414`.

Accessibility: all four files are `module` + `@[expose] public section`
(`AbstractFuncEq.lean:6,:60`; `HurwitzZetaEven.lean:6,:50`;
`MellinTransform.lean:6,:28`; `RiemannZeta.lean:6,:47`), and only
`tendsto_div_two_punctured_nhds` (`HurwitzZetaEven.lean:449`) is `private` in
the relevant region. "Looks accessible under the module system" is precisely the
class of claim this container cannot check.

**Loss at the abstraction boundary, recorded because it matters:**
`WeakFEPair.hf_top` keeps only "decays faster than every power", discarding the
exponential rate the concrete kernels have. Anything quantitative in `σ` must be
re-derived at the kernel level, not through `WeakFEPair`.

### 2.7 Explicit theta-kernel bounds — present and sharp

All `JacobiTheta/` paths in this note are under
`Mathlib/NumberTheory/ModularForms/JacobiTheta/` — **not** under
`Mathlib/Analysis/SpecialFunctions/`, where a reader would otherwise look
(Annex B-9).

```
JacobiTheta/OneVariable.lean:90
theorem norm_jacobiTheta_sub_one_le {τ : ℂ} (hτ : 0 < im τ) :
    ‖jacobiTheta τ - 1‖ ≤ 2 / (1 - rexp (-π * τ.im)) * rexp (-π * τ.im)
```

reachable from the kernels via `jacobiTheta_eq_jacobiTheta₂` (`OneVariable.lean:31`),
`cosKernel_def` (`HurwitzZetaEven.lean:93`), `evenKernel_eq_cosKernel_of_zero`
(`:102`); the `(0,1)` half via `evenKernel_functional_equation` (`:132`).
Series-side alternatives `HurwitzKernelBounds.F_nat_zero_le`
(`JacobiTheta/Bounds.lean:115`) and `F_nat_zero_zero_sub_le` (`:124`). The
qualitative forms actually consumed by `hurwitzEvenFEPair` are
`isBigO_atTop_evenKernel_sub` (`HurwitzZetaEven.lean:223`) and
`isBigO_atTop_cosKernel_sub` (`:232`).

**`evenKernel` and `cosKernel` are `@[irreducible]`** (`HurwitzZetaEven.lean:65`,
`:89`) and must be reached through `evenKernel_def`/`cosKernel_def`; `unfold`-style
drafting will fail here.

### 2.8 Γ: what exists, and what it is

`Gammaℝ` (`Gamma/Deligne.lean:43`, with `Gammaℝ_def` `:45`), `Gammaℝ_eq_zero_iff`
`:73`, `differentiable_Gammaℝ_inv` `:88`, `Gammaℝ_residue_zero` `:95`,
`Gammaℝ_div_Gammaℝ_one_sub` `:148`. **No norm, modulus, or asymptotic lemma
anywhere in that file** (§3.2).

Ingredients from which a *real* Γ bound could be assembled:
`Complex.GammaIntegral` `Gamma/Basic.lean:110`, `GammaIntegral_convergent` `:87`,
`Complex.Gamma_eq_integral` `:318`, `Real.Gamma_eq_integral` `:404`,
`Real.integral_rpow_mul_exp_neg_mul_Ioi` `:464`,
`Complex.integral_cpow_mul_exp_neg_mul_Ioi` `:371`,
`Real.Gamma_nat_eq_factorial` `:421`, `Real.Gamma_strictMonoOn_Ici`
(`Gamma/BohrMollerup.lean:353`), `Nat.factorial_le_pow`
(`Data/Nat/Factorial/Basic.lean:182`).

Real Stirling, which is what triage item (iv) means by "only real Stirling
exists". **Namespace correction (Annex B-3): these live in `namespace Stirling`
(`Analysis/SpecialFunctions/Stirling.lean:45`–`:302`), not in `Real`** — the
qualified names are `Stirling.stirlingSeq` etc., and `Real.stirlingSeq` does not
exist at the pin. `Stirling.stirlingSeq` `Stirling.lean:56` (`:53` is the doc
comment), `log_stirlingSeq_formula` `:67`, `log_stirlingSeq_sdiff_le` `:126`,
`log_stirlingSeq_bounded_by_constant` `:165`, `factorial_isEquivalent_stirling`
`:246`, `le_factorial_stirling` `:276`, `le_log_factorial_stirling` `:293`. All
are `ℕ → ℝ` statements about `n !`; `:276` and `:293` are **lower** bounds, i.e.
the wrong direction for a growth bound; `:246` is two-sided but `atTop` with no
explicit constant. Confirmed: `rg -ni "vertical|strip"` over
`Mathlib/Analysis/SpecialFunctions/Gamma/` returns **0 hits**.

### 2.9 ζ: what exists

`riemannZeta_ne_zero_of_one_le_re` (`Nonvanishing.lean:410`),
`riemannZeta_ne_zero_of_one_lt_re` (`Dirichlet.lean:326`),
`zeta_eq_tsum_one_div_nat_cpow` (`RiemannZeta.lean:204`, `1 < re s` only),
`riemannZeta_def_of_ne_zero` (`:152`), `differentiable_completedZeta₀` (`:89`).
`Harmonic/ZetaAsymp.lean` is local to `s = 1` or restricted to real `s > 1`:
`tendsto_riemannZeta_sub_one_div` `:332`, `isBigO_riemannZeta_sub_one_div` `:365`
(both at map row 103, correctly labelled "local statement"), `riemannZeta_one`
`:408`, `completedRiemannZeta₀_one` `:425`, `completedRiemannZeta₀_zero` `:446`,
`deriv_riemannZeta_zero` `:451`. **The file name is misleading for this barrier:
it contains no asymptotic in `|Im s|` and no bound in any strip.**

---

## 3. What is missing

Split as the sibling splits it: generic complex analysis that would be a natural
Mathlib upstream, versus ζ-specific work that must be built here. Every row was
searched this session with `rg -n` / `rg -ni`.

### 3.1 Generic complex analysis — natural Mathlib upstreams, no ζ/ξ/RH content

| missing item | search evidence | note |
|---|---|---|
| **norm bound for a Mellin transform** — `‖mellin f s‖ ≤ ∫ t in Ioi 0, t^(σ-1) * ‖f t‖` | `rg -n "norm_mellin\|‖mellin" Mathlib/` → **0 hits** | `MellinTransform.lean` proves convergence, differentiability, inversion, substitution — and no inequality. The smallest genuinely route-neutral missing piece under this barrier; §6 |
| definition of the **order** (growth order) or **type** of an entire function | `rg -ni "exponential type\|growth order\|orderOfGrowth\|order of an entire\|IsExpType\|paley.?wiener" Mathlib/` → **0 hits** | `analyticOrderAt` (`Analytic/Order.lean:47`) is local vanishing order in `ℕ∞` — `SC-XI-01`'s own closing sentence (`SOURCE_CONTRACTS.md:215-216`) already says so |
| genus | `rg -ni "\bgenus\b" Mathlib/Analysis/` → 0 hits | |
| Weierstrass elementary factors, canonical/Hadamard product | `rg -ni "canonical.?product\|hadamard.?factor\|weierstrass.?product\|elementaryFactor\|primaryFactor" Mathlib/` → 1 hit, `CategoryTheory/Limits/Sifted.lean:185`, unrelated | confirms sibling §3.1 and map `:155` independently |
| Hadamard **three circles**; convexity of `log M(r)` in `log r` | `rg -ni "three.?circle\|threeCircle" Mathlib/` → **0 hits** | every "three" hit under `Analysis/` is `Hadamard.lean`'s three-***lines*** |
| polynomial-growth Liouville (`‖f z‖ ≲ ‖z‖^n ⇒ polynomial`) | read `Liouville.lean`, `Harmonic/Liouville.lean`, `Polynomial/Basic.lean`, `TaylorSeries.lean` | **absent**; every pinned Liouville needs `IsBounded (range f)` or a `cocompact` limit |
| argument principle / winding number / contour residue theorem | `rg -ni "argument.?principle\|winding" Mathlib/` → **0 hits** | sibling §3.1 and Annex A-6 re-confirmed; `AnalyticAt.tendsto_mul_logDeriv_simple_zero` (`Calculus/LogDeriv.lean:146`) is a `Tendsto` at a **simple** zero, no contour, no multiplicity |
| strip or half-plane bound ⇒ derivative or logarithm bound | read `Schwarz.lean`, `Liouville.lean`, `AbsMax.lean`, `Calculus/LogDeriv.lean` | **absent**; every derivative bound at the pin is disc-shaped. `logDeriv` (`Calculus/LogDeriv.lean:34`) carries **no estimate of any kind** |
| Harnack inequality | `rg -ni "harnack" Mathlib/` → **0 hits** | `Harmonic/Poisson.lean` has the circle-average representations only |
| named sup-norm on a **sphere** | `rg -ni "sSup.*sphere\|supNorm\|sSupNorm" Mathlib/Analysis/` → **many** hits, none of them a sup of `‖f‖` over a sphere/circle in ℂ (Annex B-4) | the hits are `HadamardThreeLines.sSupNormIm` (vertical **lines**, `Hadamard.lean:77`, ~60 use sites), `sSup_sphere_eq_norm`/`_eq_nnnorm` for continuous linear maps (`Normed/Operator/NNNorm.lean:209`/`:195`, sphere of the *domain*, value `‖f‖` the operator norm), `Polynomial.supNorm` (`Analysis/Polynomial/Norm.lean:53`, with `le_supNorm` `:83`, `isGreatest_supNorm` `:89`, `supNorm_eq_iSup` `:94`; a sup over **coefficients**) and its `MahlerMeasure` uses (`:353`, `:414`), and `EntrywiseSupNorm` (`CStarAlgebra/Matrix.lean:44`). ABSENT verdict stands — see §5(4) |
| complex Stirling / asymptotic expansion of Γ; any `‖Complex.Gamma z‖` bound | `rg -n "norm_Gamma\|abs_Gamma\|‖Gamma\|‖Complex.Gamma" Mathlib/` → **0 hits**; `rg -lni "stirling" Mathlib/` → 3 files, none complex | genuinely large; also the ingredient Route B's `SC-NB-05` needs (§4.4) |

### 3.2 ζ-specific — cannot be pushed upstream, must be built here

| missing item | evidence / note |
|---|---|
| any bound of any shape on `completedRiemannZeta₀` | `rg -n "completedRiemannZeta₀" Mathlib/` → **25 occurrences**, in exactly two files (`RiemannZeta.lean`, `Harmonic/ZetaAsymp.lean`), and **not one of them is an inequality** (`rg -n "completedRiemannZeta" Mathlib/ \| rg "≤\|<\|‖\|isBigO"` → 0 hits). The pinned facts are `differentiable_completedZeta₀` plus two point values |
| any vertical or order bound on `riemannZeta` | the only `isBigO` hit is `ZetaAsymp.lean:365`, `ζ(s) − 1/(s−1) = O(1)` **at `𝓝 1`** — a local pole statement |
| any zero-free region beyond `re s ≥ 1` | `rg -ni "zero.?free" Mathlib/` → **0 hits** (confirms sibling §3.2) |
| any bound on `Gammaℝ` or its reflection ratio | `Gamma/Deligne.lean` has no norm/asymptotic lemma; `Gamma/` has no `vertical`/`strip` hit |
| G1: strip bound for ξ / `Λ₀` | absent; §6 gives the only assembly this note found |
| G2: order ≤ 1 for ξ (`SC-XI-01`(1)) | absent, and its *definitional* half (§3.1 row 2) is absent too |
| G3: `ζ'/ζ` vertical estimates, contour shift, residues | absent; overlaps `S1-EXPLICIT` — see the scope boundary in §6 |
| continuation of ζ below `re s = 1` with an explicit remainder | absent. `LSeries_eq_mul_integral` (`SumCoeff.lean:137`) is the one candidate the map's 2026-08-05 addendum item 2 flagged as useful for `SC-NB-03`; its `LSeriesSummable f s` hypothesis confines `f = 1` to `re s > 1`, so it is **not** a handle for ζ in the strip. Honest negative |

---

## 4. Repo-side demand analysis

Which rows consume which growth fact, and for which route. Row identifiers are
`MATHLIB_CAPABILITY_MAP.md` line numbers (`map:N`), `SOURCE_CONTRACTS.md` `SC-*`
IDs with line anchors, and `ROUTE_TRIAGE.md` Route C items (i)–(vii) and trigger
IDs. Every quotation below was checked against the cited line this session.

### 4.1 Capability-map rows

| row | text (abbreviated) | fact | route |
|---|---|---|---|
| `map:31` | decision summary item 4: "no zeta/xi order-one growth theorem or Hadamard factorization" | G2 | A, C |
| `map:35-38` | generic Jensen / Phragmen-Lindelof etc. "reduce some implementation cost, but they do not discharge the zeta-specific statements" | G1/G2 | N |
| `map:103` | local Laurent remainder; boundary "local statement, not a global meromorphic specialization" | negative: the only pinned ζ `isBigO` is local at `s = 1` | — |
| `map:133` | Jensen formula and divisor bound; **gap "no zeta/xi growth input"** | G1/G2 as `f_bound` | A, C |
| `map:134` | Phragmen-Lindelof; **gap "no zeta boundary-growth package"** | G1 as the boundary input | N |
| `map:154` | `NOT-FOUND-IN-SCOPE` "vertical growth and finite/order-one entire growth" → "Hadamard and contour arguments are blocked" | G1+G2+G3 | A, C |
| `map:155` | `NOT-FOUND-IN-SCOPE` "canonical product or Hadamard factorization" | G2 (its hypothesis) | A, C |
| `map:278` | Route A DAG "A/C gate -> xi vertical growth and order one" | G1+G2 | A |
| `map:279` | "divisor + order-one growth -> normalized Hadamard product" | G2 | A |
| `map:366` | Route C DAG "+ vertical growth, contour shift, pole/zero residues" | G1+G3 | C |
| `map:242` | "The xi/divisor package is shared by Routes A and C only." | scoping fact used in §4.3 | — |
| `map:390` | `S1-EXPLICIT` exit: "residues, and limiting procedure" | G3 overlap | A-via-C, C |

### 4.2 Contract rows

| row | statement | fact | route |
|---|---|---|---|
| `SC:128` | shared Required property 1: "`riemannXi` is entire of order one" | G2 | **contested** — see §4.3 |
| **`SC:182-183`** (`SC-XI-01`(1)) | "an unconditional entire-growth theorem strong enough for order at most one, with its exact Mathlib predicate **or an explicit equivalent bound**" | **G2 — the canonical `S1-GROWTH` obligation** | A, C |
| `SC:184-192` (`SC-XI-01`(2)) | multiplicity-aware `N_xi(T) ≤ C·T·log T`, "derived from the source asymptotic rather than admitted as a new hypothesis" | counting ← G2 via Jensen | A, C |
| `SC:193-194` (`SC-XI-01`(3)) | `Σ m(ρ)/|ρ|²`; radial star limit | ← (2) | A |
| `SC:195-204` (`SC-XI-01`(4)) | genus-one canonical product | Hadamard ← G2 | A, C |
| `SC:205-210` (`SC-XI-01`(5)) | `A_ξ` identified, not absorbed | ← (4) | A |
| `SC:215-216` | "`analyticOrderAt` is a local zero-order API; it is not an entire-growth theorem" | explicit anti-substitution guardrail for G2 | N |
| `SC:220-249` (`SC-LI-01`) | weighted summability and star convergence are "a hypothesis … not yet a proved fact"; `FORMAL-OBLIGATION` to derive them from a counting theorem | ← (2) ← G2 | A |
| `SC:251` ff. (`SC-LI-02`), `SC:308-310` (`SC-LI-03`) | `λ_n` star limit; local/global equality "requires the normalized Hadamard product" | ← G2 | A |
| `SC:340-352` (`SC-WEIL-01` class `A`) | `F(s) = O(1/|s|)` uniformly for `|im s| ≥ 1` | growth of the **test function**, not of ξ | A |
| `SC:385`, `SC:412` | absolute convergence of the Weil combination; one common finite cutoff | ← `SC-LI-01` | A |
| `SC:420-441` (`SC-BOMB-01`) | `f(x) = O(x^δ)`, `O(x^{−1−δ})` | test-function growth | C, A-via-C |
| **`SC:458-475`** (`SC-BOMB-02`) | `|im ρ| < T` zero sum; "multiplicity: required by the residue theorem" | **G1+G3, contour-shift justification** | C, A-via-C |
| `SC:498-512` (`SC-BOMB-03`) | autocorrelation closure, "a formalization blocker" | test-function growth | C |
| `SC:569-584` (`SC-BRIDGE-02`) | "Sharing the symbol `T` is not a proof." | equality of two growth-derived limits | A+C |
| **`SC:780-794`** (`SC-NB-05`) | the **unconditional** cross-multiplied Lemma 2.2 estimate `\|ζ(1/2−ε+iτ)\| ≤ C(1+\|τ\|)^ε \|ζ(1/2+ε+iτ)\|`, "with a corrected gamma-factor ratio derived from the pinned functional equation" | a growth-shaped ζ estimate, unconditional | **B** — §4.4 |
| `SC:766-778` (`SC-NB-05`) | Littlewood convergence; "Lindelöf estimates derived from RH" — both `RH-DEPENDENT` | RH-dependent growth facts | B, only under an explicit RH hypothesis |
| `SC:858` | anti-circularity: "use Littlewood, Lindelöf, or zero-free `re(s) > 1/2` unconditionally — reject" | guardrail | N |

### 4.3 Triage rows, and the negative declarations

Triage: item **(iv)** `:262-263` "vertical growth of zeta/xi in strips (missing,
serious; only real Stirling exists)" — G1, Route C; item **(v)** `:263-264`
"`N(T) ≪ T log T` … (moderate once (iii)+(iv) exist …)"; item **(vi)** `:265`
Landau-type log-derivative lemmas; item **(vii)** `:266-268` the contour shift,
"large"; calibration `:270` "plausibly 10k-30k lines … of which only (i)-(iii)
are cheap". Trigger **`A-T4`** `:117-118` "(cost-only): Mathlib gains Hadamard
factorization, **order-one growth for completed L-functions**, or a Riemann-Weil
explicit formula" and trigger **`C-T3`** `:278-279` "(cost-only): upstream
Mathlib explicit-formula/**vertical-growth**/Hadamard infrastructure" are both
keyed to this barrier — both carry the verbatim `(cost-only)` label at `:117`
and `:278`. **Quotation correction (Annex B-1):** the clause "each reopens desk
review only, never auto-`SELECT`" is in the **Route C** trigger preamble only
(`:273-274`); the Route A preamble at `:107` reads simply "**Reconsideration
triggers (preregistered):**". So that governance sentence is quotable for `C-T3`
and *not* for `A-T4`; for `A-T4` only the `(cost-only)` label is textual.

**The load-bearing negative.** No currently built or in-flight repository package
consumes any growth fact, deliberately and in writing:
`TARGET_BRIDGE_CONTRACT.md:39` ("none touches multiplicity, growth, zero
counting"), `XI_PACKAGE_CONTRACT.md:27` ("Nothing touches enumeration, growth,
Hadamard products…"), `CONJ_SYMMETRY_CONTRACT.md:20` (same form),
`MULTIPLICITY_CONTRACT.md:104` and death condition 4 at `:1646-1648` ("If any M
requires a Jensen-type inequality, `logCounting`, an `N(T)` estimate, or a
finite-order/Hadamard bound — **stop**"). Every in-repo consumer of a growth
fact is downstream of a `PARK`ed route or of another open barrier.

**On `SC:128`.** "Required property 1: `riemannXi` is entire of order one" sits
in the shared notation/target-mapping section, above the route split. That is
the strongest textual case for order-one being shared foundation, and it does
not survive inspection: the same section's `FORMAL-OBLIGATION` list does not
list a growth theorem, the obligation appears only in `SC-XI-01`(1) whose
`SOURCE` is a Route A source, `map:242` scopes the xi/divisor package to Routes
A and C only, and the built xi package proved the other required properties and
pointedly not this one (`XI_PACKAGE_CONTRACT.md:27`). Reading `SC:128` as licence
to build order-one now would be re-scoping the barrier toward what is
convenient, which the standing death condition forbids.

### 4.4 Route B does consume a growth-shaped fact

Recorded because two scouts disagreed and because the sibling's own Annex A-4
corrected exactly this class of over-narrow claim in the convenient direction.

`SC-NB-05` (`SOURCE_CONTRACTS.md:780-794`) states: "Lemma 2.2's zeta-ratio
estimate is unconditional… **The formal contract is the cross-multiplied
inequality** `|zeta(1/2 - epsilon + i*tau)| <= C * (1 + |tau|)^epsilon *
|zeta(1/2 + epsilon + i*tau)|`, for `tau : ℝ` and `0 <= epsilon <= epsilon0 <
1/4`, where `C > 0` depends only on `epsilon0`, **with a corrected gamma-factor
ratio derived from the pinned functional equation**." That is a
polynomial-in-height ζ estimate, it is Route B's, and it is unconditional.

Two honest qualifications, so this is not inflated in either direction. It is a
**ratio** bound, not an absolute growth bound, so it is not `SC-XI-01`(1) and
does not discharge G2. And its ingredient — a bound on the Γ-factor ratio,
uniform in height — is precisely the complex-Γ vertical estimate that
§3.1 records as absent, so this row is not a cheaper way into the barrier; it is
another consumer of the same missing ingredient. What it establishes is that
`S1-GROWTH` is **not** a purely A/C barrier.

**Attribution note (Annex B-7).** The contract's own words at `SC:791-792` are
"with a corrected gamma-factor ratio derived from the pinned functional
equation". *Uniformity in height* is this note's inference from the
`(1 + |tau|)^epsilon` factor, not a phrase the contract states. The inference
runs against convenience (it makes the barrier wider, not narrower), but it is
an inference and is marked as one.

---

## 5. Where the scouts disagreed, and where evidence is thin

Recorded, not averaged.

1. **"Is `S1-GROWTH` one statement or three?"** The generic and ζ scouts treated
   the row as a monolith ("the ξ half vs. the ζ half"); the demand scout
   decomposed it into G1/G2/G3 with distinct route profiles. **This note sides
   with the demand scout on the decomposition** — the row texts genuinely
   separate `map:134`'s boundary input from `map:279`'s Hadamard input from
   `map:366`'s contour-shift input — **and with the ζ scout on the further
   ξ/ζ split**, since a ξ bound does not yield a ζ bound without a *lower* bound
   on `‖Γ(s/2)‖`, which is absent and is where Stirling genuinely cannot be
   avoided. Both distinctions are recorded in §1(2) and §3.2. Neither is applied
   to the row itself: amending the row is a maintainer decision.

2. **Route B's consumption.** The ζ scout wrote that growth is "consumed by
   Routes A and C alike … while Route B's `SC-NB-*` obligations consume none of
   it". The demand scout found `SC-NB-05`'s unconditional Lemma 2.2 estimate.
   **The demand scout is right on the fact** (§4.4, quotation verified at
   `SOURCE_CONTRACTS.md:780-794`), and the ζ scout's framing would have made the
   barrier look purely A/C — which happens to support a tidier recommendation.
   Corrected here for the same reason the sibling's A-4 was corrected.

3. **"How close is a strip bound?"** The ζ and demand scouts independently
   reconstructed the same Mellin-majorant assembly and both called it feasible
   with no new upstream Mathlib development; the generic scout, working only
   from the complex-analysis side, concluded that nothing at the pin produces a
   bound at all. Both readings are defensible on their own evidence and they are
   not in conflict: the generic scout is right that no *complex-analytic* tool
   produces a bound, and the other two are right that the *construction* of
   `Λ₀` does. But the ζ scout's "**no new upstream Mathlib development**" is
   **too strong and is corrected here**: the assembly consumes a norm bound for
   `mellin` which does not exist at the pin (`rg -n "norm_mellin|‖mellin"` → 0
   hits, re-verified). That is one missing generic lemma, not zero. §6 records
   it as such and does not call the missing theory small.

4. **The sibling's Annex A-11, corrected in the unfavourable direction.** A-11
   wrote "No named sup-norm-on-a-sphere API exists at the pin". For **spheres**
   that is confirmed this session. For **vertical lines** it is not:
   `Complex.HadamardThreeLines.sSupNormIm` (`Hadamard.lean:77`) is exactly a
   named `sSup ((norm ∘ f) '' re ⁻¹' {x})`. This does **not** improve A-11's
   cost estimate for "definition: order of an entire function": the order needs
   the **circle** sup, which remains unnamed. It matters here because
   `S1-GROWTH`'s natural objects are line-sups.

5. **Locator corrections against the scouts** (this note's own §2 uses the
   verified numbers): `stirlingSeq` is `Stirling.lean:56`, not `:53` (`:53`
   is the doc comment) — the generic scout had `:53`, the ζ scout `:56`; and
   this note's own first draft qualified it as `Real.stirlingSeq`, which is
   wrong: the namespace is `Stirling` (Annex B-3);
   `Stirling.lean:126` is the declaration `log_stirlingSeq_sdiff_le` — the
   scout's "Robbins' bound" was a *description*, not a wrong claim, since
   Mathlib's own doc comments at `:273-274` and `:281-282` call it "Robbins'
   sharp bound"; only the declaration name needed pinning down (Annex B-6);
   `completedRiemannZeta₀` has **25** tree-wide occurrences, not 20 as
   the generic scout reported (the conclusion — none is an inequality — is
   unaffected and was re-verified); `UpperHalfPlane.verticalStrip` is defined at
   `Analysis/Complex/UpperHalfPlane/Topology.lean:98`, not at
   `EisensteinSeries/Summable.lean:94,155` (those are use sites);
   `AnalyticAt.tendsto_mul_logDeriv_simple_zero` is `Calculus/LogDeriv.lean:146`
   (`:144` is the doc-comment opener — the sibling's Annex A-6 cites `:144`).
   Everything else in §2 was found exactly at the cited line.

6. **Thin evidence — the strip-bound assembly of §6.** The chain reads correctly
   on paper and every ingredient except the `mellin` norm bound is pinned and
   was individually verified. It has **not** been kernel-checked; there is no
   toolchain here. Two specific soft points: the `EqOn`/a.e. step converting
   `‖(t:ℂ)^(s−1) • f t‖` to `t^(σ−1)‖f t‖` on `Ioi 0` (`setIntegral_congr_fun`,
   `Bochner/Set.lean:73`) was not stress-tested; and the unfolding of
   `completedRiemannZeta₀` through three `def`s and one `rfl` into
   `mellin f_modif` reaches into Mathlib's construction internals rather than
   its public zeta API. Accessibility *looks* fine under the module system
   (§2.6), and "looks fine under the module system" is exactly the class of
   claim this container cannot check. Treat "broken at one lemma" as a
   hypothesis about where to look, not as a cost estimate. It is precisely the
   kind of claim that inflates on retelling.

7. **Absence proofs are search proofs.** Every ABSENT verdict in §3 rests on
   keyword searches over `Mathlib/`. A theorem present under a name I did not
   guess would be missed; the searches most likely to be incomplete are "type of
   an entire function" and "three circles".

8. **`E`-generality was not audited.** Several statements are for a general
   `NormedSpace ℂ E`; `Liouville.lean:44` needs `[CompleteSpace F]`,
   `AbsMax.lean:383` needs `[FiniteDimensional ℂ E]`, `Schwarz.lean:296` needs
   `[StrictConvexSpace ℝ E]`. For `E = ℂ` all are satisfied, but not every
   instance path was checked.

---

## 6. Cost estimate per missing item

Units follow the earlier barriers: **statement count** (the `X1–X11`, `Z1–Z9`,
`M1–M17` convention, by analogy only) and **whether all ingredients are pinned**.
Source-reading estimates; **no Lean was run**. Per the standing instruction, no
row below is described as small unless every ingredient is demonstrably pinned
and named.

**Scope boundary for this table** (mirroring the sibling's Annex A-9/A-10). Rows
tagged `S1-EXPLICIT` or `S1-GLOBAL-ZEROS` appear as **consumers of, or immediate
neighbours of, this barrier — not as items claimed under `S1-GROWTH`**.
`S1-EXPLICIT` owns the explicit formula's residues and limiting procedure, and
owns the *test-function* growth conditions of `SC-WEIL-01`/`SC-BOMB-01`/
`SC-BOMB-03`: those are growth conditions on test functions, and `map:388` scopes
this row to "zeta/xi vertical or order-one growth". Counting them here would
inflate the barrier.

| item | statements | all ingredients pinned? | blocked on |
|---|---|---|---|
| **generic: `‖mellin f s‖ ≤ ∫ t in Ioi 0, t^(σ−1) * ‖f t‖`, given `MellinConvergent f s`** | ~1–2 | **yes, with one unverified step** — `norm_integral_le_integral_norm` (`Bochner/Basic.lean:924`), `norm_smul`, `Complex.norm_cpow_eq_rpow_re_of_pos` (`Pow/Real.lean:337`), `setIntegral_congr_fun` (`Bochner/Set.lean:73`); the `EqOn`-on-`Ioi 0` step was not stress-tested (§5.6) | nothing. Route-neutral, RH-free, and a natural upstream contribution rather than a repository barrier item |
| Stage 0: unfolding `completedRiemannZeta₀ s = mellin ((hurwitzEvenFEPair 0).f_modif) (s/2) / 2`, plus a pointwise description of `f_modif` at `a = 0` | ~2 | **yes on paper** — three `def`s and one `rfl` (`RiemannZeta.lean:63,:73`; `HurwitzZetaEven.lean:302`; `AbstractFuncEq.lean:385`), all in `@[expose] public section` | nothing, but this is the **single point of failure** for everything below it, and it is checkable in one narrow build |
| **G1: `Λ₀` bounded on every vertical strip, uniformly in `Im s`; hence `‖riemannXi s‖ ≤ (1 + ‖s‖‖s−1‖·M(a,b))/2` on `a ≤ re s ≤ b`** | ~6–8 | **no** — needs the `mellin` norm bound above; everything else is pinned (`StrongFEPair.hasMellin` `:203` via `toStrongFEPair` `:307`, `Integrable.norm`, `t^(σ−1) ≤ t^(a−1) + t^(b−1)`, `Xi.lean:41`) | the first two rows |
| crude upper bound on **real** `Γ(σ)`, e.g. `Γ(σ) ≤ exp(A(1+σ)log(2+σ))` for `σ ≥ 1/2` | ~2–3, **revised ~3–5** | **partly — corrected, Annex B-2.** For `σ ≥ 2`: yes — `Real.Gamma_strictMonoOn_Ici` (`BohrMollerup.lean:353`), `Real.Gamma_nat_eq_factorial` (`Basic.lean:421`), `Nat.factorial_le_pow` (`Factorial/Basic.lean:182`). For `σ ∈ [1/2, 2)`: **no named ingredient.** `Gamma_strictMonoOn_Ici` is literally `StrictMonoOn Gamma (Ici 2)` and says nothing below `2`; that range needs a separate continuity/compactness argument — the nearest pinned ingredients are `Real.differentiableAt_Gamma` (`Gamma/Deriv.lean:149`) / `Real.differentiableOn_Gamma_Ioi` (`:154`) composed to continuity, plus `IsCompact.exists_isMaxOn` (`Topology/Order/Compact.lean:246`); note there is **no** `Real.continuousAt_Gamma` at the pin (`continuousAt_Gamma`, `Deriv.lean:88`, is in `namespace Complex`). That route yields a **non-explicit** constant. This row therefore does **not** meet §6's own preamble rule ("no row is described as small unless every ingredient is demonstrably pinned and named") on `[1/2, 2)` | nothing on `[2,∞)`; an unnamed compactness step on `[1/2,2)` |
| explicit `‖f_modif t‖ ≤ C e^{−πt}` on `[1,∞)` and `≤ C t^{−1/2} e^{−π/t}` on `(0,1)` | ~2–4 | **yes** — `norm_jacobiTheta_sub_one_le` (`OneVariable.lean:90`), `jacobiTheta_eq_jacobiTheta₂` (`:31`), `cosKernel_def`/`evenKernel_eq_cosKernel_of_zero` (`HurwitzZetaEven.lean:93,:102`), `evenKernel_functional_equation` (`:132`) | Stage 0; must route through the `_def` lemmas (`@[irreducible]`, `:65,:89`) |
| **G2: `‖riemannXi s‖ ≤ C·exp(A(1+‖s‖)log(2+‖s‖))`, an *explicit bound of order-one shape*; offered only as a candidate for `SC-XI-01`(1)'s "explicit equivalent bound" alternative, a sufficiency judgement that belongs to contract acceptance, not to this note** | ~10–14 beyond G1, **and the Γ row's revision (Annex B-2) pushes this up, not down** | **no** — needs the three rows above plus `Real.integral_rpow_mul_exp_neg_mul_Ioi` (`Gamma/Basic.lean:464`, pinned) and the σ→∞ half; the reflection half is already kernel-checked in-repo (`riemannXi_one_sub`, `Xi.lean:61`) | the `mellin` norm bound; Stage 0 |
| **definition** of the order/type of an entire function, with usable API | ~1 def + ~6–10 API | **no** — the `limsup`/`log` idiom is pinned (`ExpGrowth.lean:38,:41` as a template) but there is **no named circle-sup**; it must be assembled from `IsCompact.exists_isMaxOn` (`Topology/Order/Compact.lean:246`) | nothing — but it is a *definition*, and `corpus.md:99-100` is explicit that a restatement is not progress unless it removes a named barrier |
| `‖Complex.Gamma z‖ ≤ Real.Gamma (re z)` for `0 < re z` | ~1–2 | **yes** — `Complex.Gamma_eq_integral` (`Basic.lean:318`), `GammaIntegral` (`:110`), `norm_integral_le_integral_norm`, `norm_cpow_eq_rpow_re_of_pos`, `Real.Gamma_eq_integral` (`:404`) | nothing. **Not needed** on the Mellin route; recorded as the honest cheap replacement if the `Gammaℝ·ζ` route is ever revisited |
| complex Stirling / Γ asymptotic expansion in a strip; the `Gammaℝ(s)/Gammaℝ(1−s)` vertical ratio bound | **large** | **no** — nothing complex exists; real Stirling is about `n !` and two of its three explicit bounds point the wrong way | a genuinely new upstream development |
| **any bound on ζ off `re s > 1`** (continuation with explicit remainder) | **large** | **no** — `SumCoeff.lean:137` does not provide it (§3.2); nothing else does | a genuinely new development. Blocks the ζ half of the row |
| G3: Landau-type `ζ'/ζ` estimates; contour shift; pole/zero residues | **large** | **no** — `Complex.borelCaratheodory` (`BorelCaratheodory.lean:109`) helps and is ball-shaped and needs `Re f ≤ M`, i.e. G1 upstream; no argument principle, no residue theorem at the pin | G1, plus new upstream. **`S1-EXPLICIT` neighbour** |
| Hadamard factorization for finite-order entire functions | **large** | **no** — no elementary factors, no genus, no order definition | all of the above. **A *consumer* of this barrier**, `SC-XI-01`(4) |
| `N_ξ(T) ≤ C·T·log T` (`SC-XI-01`(2)) | ~2–4 once its inputs exist | **no** | a **circle** sup bound for ξ (`sum_divisor_le`'s `f_bound`) plus the counting definitions. **`S1-GLOBAL-ZEROS` neighbour** |

For calibration: G1's ~6–8 statements plus its two prerequisites is the same
order as the merged `X1–X11` xi package (twelve declarations) and the `Z1–Z9`
conjugation package (sixteen). Everything from "complex Stirling" downward sits
inside triage's "10k-30k lines of new Lean" figure for the whole Route C chain.

**A caution about the G1 row that must travel with it.** A strip bound is not
order one. It says nothing as `σ → ±∞`; it does **not** discharge
`SC-XI-01`(1); and it does **not** feed `sum_divisor_le`, whose `f_bound` is a
sup on a **circle** of radius `|R|`, not on a strip. Conversely G2 alone does not
give a *sharp* strip bound. They are different statements with different
consumers, and a contract that conflated them would be re-scoping the barrier
toward whatever is convenient.

---

## 7. Misallocation warning

### 7.1 Items whose only consumer is a parked route

| item | row(s) | sole consumer(s) | why flagged |
|---|---|---|---|
| **ξ entire order ≤ 1 as Hadamard input** | `SC-XI-01`(1) `SC:182-183`; `map:278-279` | Routes A and C — both `PARK` | **sharpest flag.** This is the row most likely to be picked up as "the obvious next `S1-GROWTH` item", because it is what the barrier's own "blocks" column points at. It is also the row whose every named consumer is parked, whose *definitional* half is absent at the pin, and whose §6 cost is the largest of the ξ-side rows. Starting there combines maximum cost with minimum neutrality |
| genus-one canonical product; `A_ξ` identification | `SC-XI-01`(4),(5); `SC-LI-03` | Routes A and C | additionally blocked: no Hadamard/Weierstrass factorization and no entire-order definition at the pin |
| `N_ξ(T) ≤ C·T·log T` | `SC-XI-01`(2); triage (v) | Routes A and C | not next-buildable; triage (v) itself says "moderate **once (iii)+(iv) exist**" |
| weighted summability; star convergence; `Σ m(ρ)/\|ρ\|²` | `SC-LI-01`; `SC-XI-01`(3) | **Route A only** | triage `:131-134` forbids assuming them; strictly downstream of a counting theorem |
| absolute convergence of the Weil combination | `SC-WEIL-01` `SC:385` → `SC-WEIL-02` | **Route A only** | its only function is to make `‖G_n‖²_W = 2 Re λ_n` well-posed |
| Landau `ζ'/ζ` estimates; contour shift; residues (G3) | triage (vi), (vii); `map:366`; `SC-BOMB-02` | **Route C + A-via-C** — both `PARK` | also overlaps `S1-EXPLICIT` (`map:390`); building it under an `S1-GROWTH` banner is scope creep of the kind the sibling's A-9 caught |
| test-class growth conditions (`F(s)=O(1/\|s\|)`; `f(x)=O(x^δ)`, `O(x^{−1−δ})`; autocorrelation closure) | `SC-WEIL-01` `SC:344-352`; `SC-BOMB-01` `SC:420-441`; `SC-BOMB-03` `SC:498-512` | Routes A / C | **these are growth conditions on test functions, not on ζ/ξ.** They belong to `S1-EXPLICIT`; counting them here would inflate this barrier |
| RH-derived Littlewood convergence and Lindelöf estimates | `SC-NB-05` `SC:766-778` | Route B, **only below an explicit RH hypothesis** | `SC:858` and triage `:174-176` make unconditional use an automatic death condition. Never buildable as an unconditional item |
| the `SC-NB-05` cross-multiplied ζ-ratio inequality, as a whole statement | `SC:780-794` | **Route B only** | but its *ingredient* — the Γ-factor ratio bound — is shared with G2 and G3. The composite is Route B; the ingredient is not |

### 7.2 The two cost-only triggers are not a licence

`A-T4` (`ROUTE_TRIAGE.md:117-118`) and `C-T3` (`:278-279`) both fire on *Mathlib
gaining* growth/Hadamard infrastructure. Both are recorded there as
**cost-only** (verbatim `(cost-only)` at `:117` and `:278`). The further clause
"each reopens desk review only, never auto-`SELECT`" is textual **only for
`C-T3`** (`:273-274`, the Route C preamble); the Route A preamble (`:107`) has
no such clause, so for `A-T4` the non-auto-`SELECT` reading rests on the
`(cost-only)` label and on `RH-002` outcome 1 (`:294-300`), not on a quotable
sentence. Corrected in Annex B-1. Building the infrastructure here would fire
neither trigger as stated (they are about upstream Mathlib), and firing one
would not unpark anything.

### 7.3 On the `mellin` norm bound specifically

It is the one row in §6 whose ingredients are all pinned and named, and it is
therefore the row most likely to be over-sold. Three limits, stated so they
travel with it:

1. It is a **generic** lemma about `mellin`. It mentions no ζ, no ξ, no RH, and
   it removes no named barrier by itself — `corpus.md:99-100` applies.
2. Its value here is entirely conditional on Stage 0, which is the unverified
   step (§5.6). If the unfolding does not go through, the lemma is still a fine
   upstream contribution and is worth nothing to this barrier.
3. Composing it into G1 produces a **strip** bound. Per §6's caution, that is
   neither `SC-XI-01`(1) nor an input to `sum_divisor_le`. It would instantiate
   the hypotheses of `PhragmenLindelof.vertical_strip` and of the three-lines
   theorem, which are themselves consumers with no ζ/ξ instance. Nothing in that
   chain terminates in a barrier exit.

---

## 8. Does the sibling's "`S1-GROWTH` is the real gate" claim survive?

Stated plainly, clause by clause, against the row texts.

**Claim: "everything asymptotic under `S1-GLOBAL-ZEROS` is downstream of
`S1-GROWTH`" (`GLOBAL_ZEROS_RECON.md:66-68`, Option D `:541-543`, amendment 5
`:576-578`). — HOLDS.** Checked against the exit string at `map:387`:

| exit clause | downstream of growth? | chain |
|---|---|---|
| finite divisor sums | **no** | compactness only |
| weighted summability | **yes** | `SC-LI-01` `FORMAL-OBLIGATION` `SC:244` → `SC-XI-01`(2) → `SC-XI-01`(1) |
| star convergence of `Σ 1/ρ` | **yes** | same chain plus `SC-XI-01`(3) |
| source-matched `\|ρ\| ≤ T` limit with multiplicity | **yes** | `SC-LI-02` ← `SC-LI-01` ← counting ← growth |
| source-matched `\|Im ρ\| < T` limit with multiplicity | **yes** | `SC-BOMB-02` `SC:471` "required by the residue theorem" ← contour shift ← triage (iv)+(vii) |
| absolute convergence of the Weil combination | **yes** | `SC-WEIL-01` `SC:385` ← `SC-LI-01` ← counting ← growth |

Five of six, exactly as the sibling said. Triage item (v) states the dependency
in the triage's own words: "moderate **once (iii)+(iv) exist**".

**Claim: `sum_divisor_le` is "blocked entirely on its `f_bound` hypothesis, i.e.
exactly barrier `S1-GROWTH`" (`:162`). — HOLDS, and is sharper than stated**
(§2.4): analyticity and `f c ≠ 0` are both already available in-repo, so
`f_bound` really is the only ungiven hypothesis.

**Claim: growth has "no contract, no draft, and no accepted statement surface"
(`:543-546`). — HOLDS**, verified repo-wide (§1(4)).

**Where the claim does not survive: as a statement about queue order.** Three
findings, none of which contradicts a verified sibling finding.

1. **Necessary, not sufficient — and the sibling does not say which it means.**
   The sibling's own §7 shows that five of six `S1-GLOBAL-ZEROS` exit clauses
   are *convention-bound*, so closing that row requires freezing a truncation
   convention, which is a route selection. That obstruction is **orthogonal to
   growth**: discharging `S1-GROWTH` in full would leave `S1-GLOBAL-ZEROS`
   exactly as unclosable, for the sibling's own reason. Option D's wording is
   careful — it proposes "a reconnaissance note on `S1-GROWTH` — not a
   contract" — and on that narrow reading it is right, and this note is its
   execution. But "the real gate" read as "therefore the next closable target"
   is not supported by any row text.

2. **`S1-GROWTH` carries the same non-closability structure the sibling
   diagnosed for the row it declined, and the sibling does not note it.**
   `map:388`'s exit evidence is "explicit quantitative bounds sufficient for
   **the selected theorem**"; `ROUTE_TRIAGE.md` selected zero theorem-bearing
   routes. There is no selected theorem. Unlike `S1-GLOBAL-ZEROS`, the string
   contains no truncation convention and no route-indexed object *other than*
   those four words — so the failure mode here is not "closing it selects a
   route" but "the exit condition has no referent". Choosing a theorem for a
   bound to be sufficient for **would be** a route selection. This is a
   governance observation offered to the maintainer as a question about the
   row's wording, not a reading that licenses picking one.

3. **"`S1-GROWTH` owns every ξ growth bound" (`:410`) treats the barrier as a
   monolith; the row texts do not** (§1(2), §5(1)). The three components have
   different route profiles, different pin-side feasibility, and different
   neutrality. In particular Route B consumes a growth-shaped fact
   unconditionally (§4.4), which the sibling's Route B audit did not look for —
   its own unresolved concern 5 flags exactly this class of gap.

**Plain verdict.** The sibling's factual chain — growth is a strict prerequisite
for the quantitative half of `S1-GLOBAL-ZEROS`; growth blocks Routes A and C;
growth is unstarted here — **holds up clause by clause against the row texts. I
found no evidence contradicting it.** What does not hold up is the implicature
that `S1-GROWTH` is therefore the barrier to *close* next. "The real gate" is
accurate about mathematical dependency and misleading about queue order.

**And the honest conclusion for this barrier, stated as the instruction
requires: `S1-GROWTH` should not be attempted next either, if "attempted" means
"driven to a closure."** Its exit condition currently has no referent; its two
named consumers ("Hadamard and contour shifts") are both parked-route machinery;
its ζ half is blocked on continuation-with-remainder and complex Stirling, both
genuinely large; and its cheapest ξ-side item is a generic lemma that removes no
named barrier. What the barrier *can* absorb now is exactly what this note is:
reconnaissance. §9 names candidates for the queue.

---

## 9. Recommendation — options, not a selection

Selection belongs to the maintainer and to the queue. Five options with their
honest costs; this note picks none.

**Option A — do nothing under this barrier now; finish `S1-MULTIPLICITY`
first.** This is the sibling's Option A and it is unchanged by anything found
here. `MULTIPLICITY_CONTRACT.md` is drafted and awaiting independent acceptance,
and its second half is blocked on `Conj.lean` merging. It is the item with the
fewest ordering hazards, it consumes no growth fact by its own death condition 4
(`:1646-1648`), and nothing in this note competes with it. **If the queue needs
a next item and wants the safest one, this is it.**

**Option B — the narrow neutral slice under `S1-GLOBAL-ZEROS` (the sibling's
N1+N2), after `S1-MULTIPLICITY` lands.** Unchanged by this note; recorded so the
options are comparable. Cheap, unconditional, convention-free if parameterized
by an arbitrary compact `K`, and explicitly not a closure of that row either.

**Option C — offer the generic pieces upstream rather than building them here.**
The route-neutral, RH-free pool this barrier sits on is: a **norm bound for
`mellin`** (the one row in §6 whose ingredients are all pinned and named — with
§7.3's three limits attached); a definition of the **order/type of an entire
function** with its API; **Weierstrass elementary factors**; **three circles /
log-convexity of the maximum modulus**; **polynomial-growth Liouville**;
`‖Complex.Gamma z‖ ≤ Real.Gamma (re z)`. None mentions ζ, ξ, or RH; all would be
reviewable on their own merits. This is upstream work with long review latency
and it is **not a repository barrier item**. It is also the only pool here that
would fire `A-T4`/`C-T3` as those triggers are actually worded (§7.2) — and
those are cost-only and never auto-`SELECT`.

**Option D — a narrowly scoped in-repo pilot: G1 only, explicitly not an
exit.** The `Λ₀`-bounded-on-vertical-strips statement (§6) is the only item
under this barrier that is convention-free (no truncation cutoff, no zero
enumeration, no test class, no `|ρ| ≤ T` vs `|Im ρ| < T` choice), that is
consumed by all three route families rather than one, and whose ingredients are
pinned apart from one named generic lemma. Its honest limits are severe and must
be preregistered if it is ever contracted: it is **not** order one, it does
**not** discharge `SC-XI-01`(1), it does **not** feed `sum_divisor_le` (circle
vs strip), it says nothing about ζ, and it closes nothing. Its single point of
failure is Stage 0, which is checkable in one narrow build and which no reading
in this container can settle. Anyone considering this should first read §5.6 and
§6's closing caution, and should treat the ordering of §7.1 — that G2, not G1,
is what the barrier's own "blocks" column points at — as the reason G1 is *not*
the obvious item.

**Option E — leave the barrier alone and fix the row's wording question
first.** The maintainer may reasonably conclude that a row whose exit evidence
names "the selected theorem" under a zero-route disposition should be reworded
or split (ξ half / ζ half; G1/G2/G3) before any work is scheduled against it.
That is a decision about the map file, not a mathematical item, and this note
does not make it.

**Proposed capability-map amendments** (recon output; **not applied**; **none
retires a row**):

1. Add a `GENERIC` inventory row for **Hadamard three lines**:
   `Complex.HadamardThreeLines.norm_le_interpStrip_of_mem_verticalClosedStrip`
   (`Analysis/Complex/Hadamard.lean:588`) and
   `norm_le_interp_of_mem_verticalClosedStrip'` (`:607`), with `verticalStrip`
   `:70`, `verticalClosedStrip` `:73`, `sSupNormIm` `:77`; gap: "**requires
   `BddAbove` of `‖f‖` on the whole closed strip**; interpolates between two
   already-finite line sups; no ζ/ξ instance". This is the one genuine inventory
   gap found; it closes nothing.
2. Extend map row 134 to list the full pinned Phragmén–Lindelöf family
   (`horizontal_strip` `:113`, `vertical_strip` `:275`, quadrants
   `:344/:446/:508/:574`, right half-plane `:646/:717/:759/:812`), keeping the
   gap text unchanged.
3. Add `GENERIC` rows for the **Mellin/FE-pair layer as a growth resource**, not
   only as a construction resource: `WeakFEPair` (`AbstractFuncEq.lean:81`),
   `f_modif` (`:258`), `Λ₀` (`:385`), `StrongFEPair.hasMellin` (`:203`),
   `toStrongFEPair` (`:307`); gap: "no norm bound for `mellin`; `hf_top`
   discards the exponential rate the concrete kernels have".
4. Add a `PRESENT` row for the explicit theta bounds
   `norm_jacobiTheta_sub_one_le` (`JacobiTheta/OneVariable.lean:90`),
   `HurwitzKernelBounds.F_nat_zero_zero_sub_le` (`JacobiTheta/Bounds.lean:124`),
   `isBigO_atTop_evenKernel_sub` (`HurwitzZetaEven.lean:223`); gap: "kernel-side
   only; not transported to any ζ/ξ bound".
5. Add `GENERIC` rows for `Complex.norm_le_of_forall_mem_frontier_norm_le`
   (`AbsMax.lean:400`), the Cauchy estimates (`Liouville.lean:44`, `:76`), and
   the Schwarz derivative bounds (`Schwarz.lean:201`, `:255`), each gapped
   "disc- or bounded-region-shaped; no strip form".
6. Record the §3 `ABSENT` findings individually with their searches — **no norm
   bound for `mellin`**; order/type of an entire function; genus; three circles;
   log-convexity of the maximum modulus; polynomial-growth Liouville; complex
   Stirling / any `‖Complex.Gamma z‖` bound; no inequality anywhere involving
   `completedRiemannZeta₀`. These are currently implied by the severity table
   but not individually evidenced.
7. Add semantic-mismatch-register rows: (a) **there is no Mathlib predicate for
   the order of an entire function**, so `SC-XI-01`(1)'s "exact Mathlib
   predicate" alternative is currently unavailable and only its "explicit
   equivalent bound" alternative is realizable; (b)
   **`HadamardThreeLines.verticalStrip` is not `UpperHalfPlane.verticalStrip`**
   (`Hadamard.lean:70` vs `UpperHalfPlane/Topology.lean:98`).
8. Note in the `S1-GROWTH` row that its exit string is **route-parameterized**
   ("sufficient for the selected theorem", with zero routes selected), and that
   its ξ half and ζ half have very different cost at this pin — a single exit
   string invites discharging the cheap half and reporting the row.
9. Correct the sibling's Annex A-11 to distinguish spheres (no named sup-norm
   API) from vertical lines (`sSupNormIm`), noting that the order definition
   needs the **circle** sup and is therefore not made cheaper by this.
10. Record the honest negative on `LSeries_eq_mul_integral` (`SumCoeff.lean:137`,
    flagged useful by the map's 2026-08-05 addendum item 2): confined to
    `re s > 1` by its `LSeriesSummable` hypothesis, hence **not** a handle for ζ
    in the strip.

Whether to apply any of these is a maintainer decision on the map file. No route
is unparked, no revival bar is claimed met, no barrier is declared closed or
stale, and no statement in this note bears on the truth of the Riemann
Hypothesis.

---

## Annex — verification log, 2026-08-07

Every locator in §2 was extracted line-by-line from the pinned tree this session
(`sed -n "${n}p"` on the cited file) and matched the cited declaration, with the
five exceptions recorded at §5(5). Every `map:`, `SC:`, and triage locator in §4
and §7 was extracted the same way from the repository documents and matched the
quoted text. Every ABSENT verdict in §3 was produced by a `rg -n` / `rg -ni`
search re-run this session; the searches and their hit counts are in the tables.

Not verified, and named as such: nothing was kernel-checked; the module-system
accessibility of `WeakFEPair.f_modif` / `Λ₀` / `hurwitzEvenFEPair` from outside
their defining modules was read but not compiled; the `EqOn`-on-`Ioi 0` step in
the `mellin` norm bound was not stress-tested; instance paths for the
`E`-generality side conditions of §2.3 were not individually checked; and the
statement counts in §6 follow the `X`/`Z`/`M` convention by analogy only.

Re-read end to end for route selection, unparking, staleness, barrier closure,
or RH progress: **none found.** No file other than this note is amended.

---

## Annex B — adversarial review, 2026-08-07

Independent adversarial pass over this note. Pin re-verified this session:
`git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD` =
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`. Method: every Mathlib locator in §2,
§3 and §6 re-extracted by `sed -n "${n}p"`; every `map:`/`SC:`/triage anchor in
§4, §7 and §8 re-extracted the same way; **every ripgrep command quoted in the
note re-run verbatim**. Source reading only; no Lean toolchain, nothing below is
kernel-checked. Fixes applied in place. **No fix changed a verdict of the note,
retired a row, unparked a route, or altered its recommendation.**

### Fixes applied

| id | severity | finding | disposition |
|---|---|---|---|
| **B-1** | MEDIUM | §4.3 and §7.2 attributed to **both** triggers the clause "each reopens desk review only, never auto-`SELECT`". That clause exists only in the **Route C** preamble (`ROUTE_TRIAGE.md:273-274`). The **Route A** preamble (`:107`) reads "**Reconsideration triggers (preregistered):**" and carries no such clause, so the sentence is not quotable for `A-T4`. The substantive point survives: `(cost-only)` is verbatim at `:117` for `A-T4` and at `:278` for `C-T3`, and `RH-002` outcome 1 (`:294-300`) independently records that zero routes are `SELECT`ed | **FIXED** — both passages rewritten to attribute the clause to `C-T3` only and to say what `A-T4` actually rests on |
| **B-2** | MEDIUM | Over-optimistic "all ingredients pinned = **yes**" in §6, the exact defect class the sibling's A-11 recorded. The real-Γ row claims `σ ≥ 1/2` with `Gamma_strictMonoOn_Ici` as its engine, but at the pin that lemma is literally `StrictMonoOn Gamma (Ici 2)` (`BohrMollerup.lean:353`) — nothing listed covers `[1/2, 2)`. This violated §6's own preamble rule, and it understated a G2 ingredient | **FIXED** — row split by range, estimate revised `~2–3` → `~3–5`, the `[1/2,2)` gap named with its (non-explicit-constant) compactness route, and the G2 row annotated that this pushes its cost **up**. Also corrected while fixing: there is no `Real.continuousAt_Gamma` at the pin; `continuousAt_Gamma` (`Gamma/Deriv.lean:88`) is `Complex`-namespaced, and the Real-side lemmas are `Real.differentiableAt_Gamma` `:149` / `Real.differentiableOn_Gamma_Ioi` `:154` |
| **B-3** | LOW-MEDIUM | Wrong namespace in §2.8 and §5(5): `Real.stirlingSeq`. At the pin the whole family is in `namespace Stirling` (`Analysis/SpecialFunctions/Stirling.lean:45`–`:302`; the file's only `open`s are at `:40-43`), so `Real.stirlingSeq` does not exist. Every file/line number in that paragraph is correct; only the qualification was wrong — in the paragraph that is itself the note's locator-correction list | **FIXED** — namespace corrected and the self-correction recorded in §5(5) |
| **B-4** | LOW-MEDIUM | §3.1's sphere row mis-described its own search output: "only `sSup_sphere_eq_norm` … and `HadamardThreeLines.sSupNormIm`". Re-running `rg -ni "sSup.*sphere\|supNorm\|sSupNorm" Mathlib/Analysis/` returns many more — `Polynomial.supNorm` (`Analysis/Polynomial/Norm.lean:53`, `le_supNorm` `:83`, `isGreatest_supNorm` `:89`, `supNorm_eq_iSup` `:94`), `MahlerMeasure` uses (`:353`, `:414`), `EntrywiseSupNorm` (`CStarAlgebra/Matrix.lean:44`), plus `sSup_sphere_eq_nnnorm` (`NNNorm.lean:195`) | **FIXED** — row rewritten to report the real hit set. **The ABSENT verdict survives**: none of them is a sup of `‖f‖` over a sphere/circle in ℂ, so §5(4)'s conclusion that the *circle* sup remains unnamed is unchanged, and A-11's cost estimate is still not improved |
| **B-5** | LOW | §2.1 said `PhragmenLindelof.lean` has "twenty declarations". Actual: **24** (`:65`, `:80`; `:113/:231/:249`; `:275/:303/:321`; twelve quadrant `:344/:409/:426/:446/:472/:489/:508/:539/:555/:574/:603/:620`; `:646/:717/:759/:812`). The 828-line figure and every individual line number in §2.1 are correct | **FIXED** — count corrected, `variable` line `:96` and namespace `:54` added |
| **B-6** | LOW | §5(5) recorded "`Stirling.lean:126` is `log_stirlingSeq_sdiff_le`, not 'Robbins' bound' as labelled" as a scout error. Mathlib's own doc comments (`:273-274`, `:281-282`) call that lemma "Robbins' sharp bound", so the scout's label was a correct description; only the declaration name was missing | **FIXED** — softened to a naming clarification. A recon note should not book a correct description as an error |
| **B-7** | LOW | §4.4 called the height-uniform Γ-factor-ratio bound SC-NB-05's "**stated** ingredient". `SC:791-792` says only "with a corrected gamma-factor ratio derived from the pinned functional equation"; uniformity in height is an inference from the `(1 + \|tau\|)^epsilon` factor | **FIXED** — marked as inference. Direction noted: the inference widens the barrier, so it is not convenience-directed |
| **B-8** | LOW (cosmetic) | §2.2's first code block reads as byte-verbatim extraction but condenses three lines: `:70`/`:73` bind `(a : ℝ) (b : ℝ)` separately, and `sSupNormIm` spans `:77-79` with its own `{E : Type*} [NormedAddCommGroup E]` binders rather than inheriting a `variable` line | **FIXED** — condensation disclosed. The `:607` block is byte-verbatim, re-checked character by character |
| **B-9** | LOW (cosmetic) | §2.7 and §6 cite `JacobiTheta/OneVariable.lean` and `JacobiTheta/Bounds.lean` with no parent path. These are under `Mathlib/NumberTheory/ModularForms/`, not under `Mathlib/Analysis/SpecialFunctions/` where the note's other special-function paths sit | **FIXED** — parent path stated once in §2.7 |

### Verified sound, no change

- **Every ABSENT verdict in §3 survives re-running, and every quoted command
  runs as written.** The sibling's A-5 defect (`rg -E` parsed as `--encoding`)
  is **not** repeated anywhere: `norm_mellin\|‖mellin` → 0; entire-order/type/
  Paley-Wiener → 0; `\bgenus\b` under `Analysis/` → 0; canonical/Hadamard/
  Weierstrass product → 1 unrelated hit (`CategoryTheory/Limits/Sifted.lean:185`);
  three circles → 0; argument principle / winding → 0; Harnack → 0;
  `norm_Gamma\|abs_Gamma\|‖Gamma` → 0; `stirling` → exactly 3 files, none
  complex; `vertical\|strip` under `Gamma/` → 0; `zero.?free` → 0;
  `completedRiemannZeta₀` → **25** occurrences in exactly 2 files with **no
  inequality among them**; `three.?line\|Complex/Hadamard\|sSupNormIm` over the
  map and the search log → **0**, so §1(1)'s inventory-gap claim holds; and
  `Analysis/Calculus/LogDeriv.lean` contains no `≤` and no `‖` at all,
  confirming "`logDeriv` carries no estimate of any kind".
- **§2.2's load-bearing caution is exactly right.** All four three-lines
  statements — `:463`, `:477`, `:588`, `:607` — carry
  `hB : BddAbove ((norm ∘ f) '' verticalClosedStrip …)`, as do
  `norm_le_sSupNormIm` `:133` and `norm_lt_sSupNormIm_eps` `:143`. The
  `:607` signature quoted in §2.2 matches the source verbatim.
- **The FE-pair/Mellin chain is correct link by link**, including the two
  claims a reader would most want to distrust: `StrongFEPair.hasMellin`
  (`:203`) really is `∀ s : ℂ` and really is proved by `exists_gt s.re` /
  `exists_lt s.re` feeding `mellinConvergent_of_isBigO_rpow`; and
  `completedRiemannZeta₀ s = mellin ((hurwitzEvenFEPair 0).f_modif) (s/2) / 2`
  really does follow from `RiemannZeta.lean:63`, `HurwitzZetaEven.lean:302` and
  `AbstractFuncEq.lean:385`. Also confirmed: `hurwitzEvenFEPair`'s `k = 1/2`,
  `ε = 1`, `f₀ = if a = 0 then 1 else 0`, `g₀ = 1`; `WeakFEPair.hf_top` is
  `(f · - f₀) =O[atTop] (· ^ r)` for every `r`, so §2.6's
  "abstraction-boundary loss" is real; `evenKernel`/`cosKernel` really are
  `@[irreducible]` (`:65`, `:89`); the four files really are `module` +
  `@[expose] public section` at the cited lines; and
  `tendsto_div_two_punctured_nhds` (`:449`) really is the **only** `private`
  declaration across all four files.
- **§2.4 is sound and its sharpening of the sibling holds.**
  `sum_divisor_le`'s signature matches verbatim; `f_bound` is a **sphere** sup;
  `differentiable_riemannXi` (`Xi.lean:46`) and `riemannXi_zero` (`:72`) are
  in-repo as cited; `riemannXi` is defined at `Xi.lean:41-42` with the
  normalization named in the task.
- **Every `map:`, `SC:` and triage anchor checked matched its quoted text**,
  including `map:388`'s exit string, `map:387`, `map:154/155`, `map:242`,
  `map:278/279`, `map:366`, `map:390`, `SC:128`, `SC:182-183`, `SC:215-216`,
  `SC:780-794`, `SC:858`, triage `(iv)`–`(vii)`, `:270`'s 10k-30k calibration,
  `:294`'s zero-route outcome, and the four contract "claim boundary" lines
  (`TARGET_BRIDGE_CONTRACT.md:39`, `XI_PACKAGE_CONTRACT.md:27`,
  `CONJ_SYMMETRY_CONTRACT.md:20`, `MULTIPLICITY_CONTRACT.md:104` and death
  condition 4 at `:1646-1648`). §4.3's reading of `SC:128` is confirmed: it sits
  inside "## Shared notation and target mapping" (`:74-169`) and that section's
  `FORMAL-OBLIGATION` list (`:140-167`) contains no growth theorem.
- **§1(4)'s repo-wide negative holds.** `S1-GROWTH` occurs outside the sibling
  note at exactly `MATHLIB_CAPABILITY_MAP.md:388` and `:553`; `drafts/` contains
  `README.md`, `RiemannTargetBridge.lean`, `RiemannXi.lean`, `RiemannConj.lean`,
  `RiemannMult.lean` and no growth file.
- **The G1 skeleton has no third gap.** Working the assembly independently:
  `MellinConvergent` is integrability of `t ↦ (t:ℂ)^(s-1) • f t` on `Ioi 0`;
  `norm_cpow_eq_rpow_re_of_pos` (`Pow/Real.lean:337`) makes the modulus depend
  on `re s` only; `t^(σ-1) ≤ t^(a-1) + t^(b-1)` on `(0,∞)` for `a ≤ σ ≤ b`
  closes the strip. The two gaps the note names — the `mellin` norm bound and
  the `EqOn`-on-`Ioi 0` step — are the only ones this reviewer found. §5.6's
  instruction to treat "broken at one lemma" as a hypothesis about where to
  look, not a cost estimate, is the correct framing and is not weakened here.
- **Softened-negative audit (the sibling's own caught defect): none found.**
  §4.4 reports Route B consumption at full strength against the tidier scout
  framing; §5(3) corrects "no new upstream Mathlib development" to one missing
  lemma; §6's closing caution and §7.3's three limits both cut against Option D;
  §8's plain verdict — that `S1-GROWTH` should not be attempted next either —
  is stated without hedging. The single over-optimistic cell found (B-2) makes
  **G2** look cheaper, and G2 is the row §7.1 flags as the sharpest
  misallocation — so it cut *against* the note's own recommendation, not for it.
- **Scope audit, both directions: clean.** §6's scope-boundary paragraph and
  §7.1's last two rows keep test-function growth under `S1-EXPLICIT` and
  `N_ξ(T)` under `S1-GLOBAL-ZEROS`, mirroring the sibling's A-9/A-10. §4.4
  widens the barrier to Route B and says so explicitly. No re-scoping toward
  convenience found.
- **Sibling-contradiction handling is honest, not smoothed.** §5(4) corrects
  A-11 and immediately says the correction does **not** lower A-11's cost
  estimate; §5(5) corrects A-6's `:144` (the doc-comment opener; the theorem is
  `Calculus/LogDeriv.lean:146`); §8 disputes the queue-order implicature of "the
  real gate" in the open while confirming the sibling's dependency chain clause
  by clause. All three disagreements are surfaced rather than averaged.
- **Governance re-read.** No sentence claims a proof, selects or unparks a
  route, declares a barrier closed or stale, or asserts progress on the truth of
  RH — before or after these fixes.

### Unresolved concerns (not fixed)

1. **Nothing is kernel-checked, and Stage 0 remains the single point of
   failure.** §6's Stage 0 row is `yes on paper` — three `def`s and one `rfl`
   reaching into Mathlib's construction internals. Every accessibility check
   here was source reading under the module system, which is precisely the class
   of claim this container cannot settle. B-2 demonstrates that at least one
   further "yes" in §6 was softer than its phrasing; the remaining ones were
   spot-checked, not exhaustively stress-tested.
2. **The §6 statement counts remain unvalidated**, following the `X`/`Z`/`M`
   convention by analogy only, as §5.6 and the note's own Annex already say. The
   four "large" rows carry no evidence beyond the triage's own 10k-30k figure.
3. **Absence is still search-absence.** B-4 shows a search whose *reported* hit
   set was wrong while its verdict was right; the same could hide a present
   theorem under an unguessed name. The two the note flags as most at risk
   ("type of an entire function", "three circles") are still the two this
   reviewer would re-search first, and `E`-generality instance paths (§5.8)
   were again not audited.
4. **B-1 exposes a governance asymmetry in `ROUTE_TRIAGE.md` itself**, not in
   this note: Route C's trigger block carries the never-auto-`SELECT` clause and
   Route A's does not. That is a maintainer question about the triage file. This
   note may not and does not resolve it, and nothing here should be read as a
   proposal to edit `ROUTE_TRIAGE.md`.
5. **The sufficiency judgement in §6's G2 row is not this note's to make.**
   Whether an explicit bound of shape `exp(A(1+‖s‖)log(2+‖s‖))` satisfies
   `SC-XI-01`(1)'s "explicit equivalent bound" alternative is a contract
   acceptance decision. The row was reworded to say so; the underlying question
   stays open and stays with the maintainer.
