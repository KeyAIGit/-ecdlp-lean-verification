# Milestone feasibility: is there a real zeta theorem reachable in one focused week?

**Status: RECON ONLY (2026-08-08).** This note is reconnaissance. It is **not** a
contract, **not** a route selection, **not** an unparking of any barrier or route,
and it **closes nothing**. It asserts nothing whatsoever about the truth of the
Riemann Hypothesis. It does not activate a queue task; the RH queue
(`tasks/RIEMANN_HYPOTHESIS.md`) keeps `RH-012` as the sole ACTIVE slot and
`ROUTE_TRIAGE.md` keeps all three theorem-bearing routes `PARK`ed. Nothing below
is authorization to work a route. No file outside this one was modified.

**Method: source reading only.** No Lean toolchain exists in this container
(`which lake lean elan` → nothing). **Nothing in this note is kernel-checked.**
Every feasibility judgement is static reading of the pinned tree and the repo.
Costs are estimates, not measurements.

**Pin.** Mathlib `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` at
`/workspace/leanprover-community/mathlib4` (confirmed by `git rev-parse` this
session). Repo branch `claude/rimmen-hypothesis-b6gd62`, head `543f794`. Locators
below are `file:line` at those two revisions and were re-read this session; see
Annex A for the ones that moved.

---

## 0. Substrate, as measured rather than as reported

Counted directly, not quoted from an earlier note:

| built module | thm/lemma | def |
|---|---|---|
| `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/TargetBridge.lean` | 8 | 0 |
| `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Xi.lean` | 11 | 1 |
| `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Conj.lean` | 16 | 0 |
| `ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Mult.lean` | 34 | 0 |
| **RH lane total** | **69** | **1** (= 70 declarations) |
| `ResearchOS/Analysis/MellinBound.lean` (domain-neutral shelf, committed `543f794`) | 5 | 0 |

The owner's framing is correct and I confirm it independently: **not one
inequality about ζ or ξ appears anywhere in the built surface.** The strongest
quantitative fact in the lane is a point value, `riemannXi_zero : riemannXi 0 =
1 / 2` (`Xi.lean:72`). Everything else is transport, order bookkeeping, and
definitional bridging.

**One candidate on the charge list is already built and is exactly why the lane
reads as vocabulary.** "Functional-equation-based zero symmetry counting" is
`analyticOrderAt_riemannXi_fourfold` (`Mult.lean:328`) plus
`riemannXi_divisor_univ_one_sub_conj` (`Mult.lean:689`). It is kernel-checked, it
is not a milestone, and it must not be re-targeted.

### Lane throughput, calibrated from the git record

TargetBridge (8 decls) landed 2026-08-05, Xi (12) 2026-08-05, Conj (16)
2026-08-06, Mult (34) 2026-08-07, MellinBound (5) 2026-08-08. That is **~70
declarations in four days**, which is a high rate and is the honest baseline for
this lane — *for transcription-grade work where every ingredient is pinned and
named*. It is not a rate for producing an estimate that does not yet exist. The
lane has produced **zero** real-analysis estimates, so its rate on that class of
work is **unmeasured, not fast**. Both halves of that sentence matter below: the
first makes the cheap candidates cheaper than the scouting reports said, the
second means nothing in the expensive column may be discounted by pointing at
the fast column.

---

## 1. Candidate assessment

Ordering here is by charge, not by rank. Rank is §2.

### C1 — Hardy's theorem (infinitely many zeros on `re s = 1/2`)

Unconditionally proved (Hardy 1914). Absent at pin. Route-neutral.

Two standard proofs; both were walked ingredient-by-ingredient.

*Proof I (theta–Mellin + sign contradiction, Titchmarsh §10.2).*

| ingredient | pinned? | locator / verdict |
|---|---|---|
| entire ξ, functional equation, zero bridge | in-repo | `Xi.lean:41,46,61,120,192` |
| Ξ real on the critical line | free from repo | see C8 |
| Jacobi theta + S-transform | **yes** | `JacobiTheta/OneVariable.lean:29`, `:43`, `:90`, `:112` — **all conditioned on `0 < im τ`** |
| theta blow-up as `τ → −i` (real-axis boundary) | **no** | pin's theta API has no rate as `im τ → 0`. This is the analytic heart of the proof |
| generic Mellin transform + inversion | **yes** | `MellinTransform.lean:91`, `:160`, `:86`; `MellinInversion.lean:98` |
| `VerticalIntegrable (mellin f) σ` for the ζ pair | **no** | it is the load-bearing hypothesis of `mellinInv_mellin_eq` (`MellinInversion.lean:99`), and discharging it *is* decay of Λ in `t`, i.e. complex Stirling |
| complex Stirling / any `‖Complex.Gamma z‖` bound | **no** | `Stirling.lean` is `n!`-only (`:56`, `:246`, `:276`, `:293`); tree-wide grep for `norm_Gamma\|abs_Gamma\|‖Gamma\|‖Complex.Gamma` → **0 hits**, re-run this session |
| IVT for sign changes | **yes** | `Topology/Order/IntermediateValue.lean:553` |

*Proof II (Hardy–Littlewood mean value).* Needs `∫₀^T Z(t)dt = O(T^{1/4})`, the
second moment `∫₀^T |ζ(½+it)|²dt ~ T log T`, and convexity `ζ(½+it) ≪ t^{1/4+ε}`.
None exists. There is no approximate functional equation and no moment theorem
anywhere in `Mathlib/`. Phragmén–Lindelöf (`PhragmenLindelof.lean:275`) and
Hadamard three lines (`Hadamard.lean:588`, `:607`) are pinned but are *consumers*
of finite line sups, never producers.

The Hardy `Z`-function and Riemann–Siegel `θ(t) = arg Γ(¼+it/2) − (t/2)log π` are
both unavailable: there is **no `Real.logGamma` and no `Complex.logGamma` at the
pin at all** (only `logGammaSeq`, `Gamma/BohrMollerup.lean:140`, an approximating
sequence), hence no continuous arg branch. Ξ substitutes in Proof I, so this is
avoidable — but Proof I then lands on the theta boundary blow-up instead.

**Honest cost: 12–24 months.** Two of the missing pieces (theta boundary
blow-up; vertical decay of Λ) are research-grade formalization, not
transcription. Not a week. Not a quarter.

### C2 — Classical zero-free region near `re = 1` (de la Vallée Poussin)

Unconditionally proved. Absent at pin (only the *line* `re = 1` is pinned).
Route-neutral.

Pinned and cheap:

- 3-4-1 inequality, in **product form and public**:
  `norm_LSeries_product_ge_one` (`Nonvanishing.lean:284`),
  `norm_LFunction_product_ge_one` (`:307`); scalar kernel
  `re_log_comb_nonneg'`/`re_log_comb_nonneg` (`:220`, `:241`, both `private`).
  Specialise to `N = 1` through `LFunction_modOne_eq`
  (`DirichletContinuation.lean:67`). Cost: hours.
- Endpoint `riemannZeta_ne_zero_of_one_le_re` (`Nonvanishing.lean:410`) — the
  qualitative theorem is already done.
- Cauchy derivative estimate for the Landau/MVT step:
  `norm_deriv_le_of_forall_mem_sphere_norm_le` (`Liouville.lean:76`).
- Argument principle and complex Stirling are **not needed** for the classical
  region worked in `1−δ ≤ σ ≤ 2`. This is what makes C2 the cheapest of the
  charged milestones.

The whole problem is one item: **a uniform bound `|ζ(σ+it)| ≪ log|t|` for
`1−δ ≤ σ ≤ 2`, `|t| ≥ 2`.** It needs a representation of ζ valid *left of*
`re s = 1` with an explicit remainder. Nothing at the pin provides one:
`ZetaAsymp.lean` is entirely about **real** `s > 1` (`:156`, `:248`, `:365`);
`LSeries_eq_mul_integral` (`SumCoeff.lean:137`) carries `hs : r < s.re` which for
`f = 1` confines it to `re s > 1`; `AbelSummation.lean:129` is raw material, not
an assembled continuation. The repo already measured this and parked it
(`GROWTH_RECON.md:652`: "large … a genuinely new development. **Blocks the ζ half
of the row**").

The ξ side does not rescue it: converting a ξ bound to a ζ bound needs a *lower*
bound on `‖Γℝ(s/2)‖`, and `Gamma/Deligne.lean` (`:43` onward) contains no norm,
modulus, or asymptotic lemma of any kind. Borel–Carathéodory
(`BorelCaratheodory.lean:109`) is `ball 0 R`-shaped and its hypothesis
`Re f ≤ M` for `f = log ζ` *is* the missing bound — circular
(`GROWTH_RECON.md:215`).

**Honest cost: ~2,000–4,000 lines of new Lean; 3–6 months of focused expert
work.** That is the same class of effort `PrimeNumberTheoremAnd`'s strong-PNT
branch spent months on. I will not soften it.

### C3 — Riemann–von Mangoldt zero-counting asymptotic

`N(T) = (T/2π)log(T/2π) − T/2π + 7/8 + S(T) + O(1/T)`. Unconditional. Absent.
Blocked simultaneously behind four things:

1. **Rectangle argument principle.** `rg -ni "argument.?principle|winding"
   Mathlib/` → **0 hits** (re-run this session; independently matches
   `GROWTH_RECON.md:397`, `GLOBAL_ZEROS_RECON.md:215`, `EXPLICIT_RECON.md:108`).
   The pin has only the vanishing theorem
   (`CauchyIntegral.lean:266`) and the circle residue
   (`CircleIntegral.lean:699`). The repo's own `ARG_PRINCIPLE_CONTRACT.md` is
   **deliberately circle-only** (`:85`), is DRAFT v1.1 statement-surface-only,
   and **no Lean file exists** (`drafts/ArgPrinciple.lean` absent — verified).
2. **Complex Stirling** for the main term: `(T/2π)log(T/2π) − T/2π` *is* the
   Γ-factor's argument. No way around it.
3. **`S(T) = O(log T)`**, which needs C2's missing bound plus a *circle* sup for
   ξ.
4. **Stating `N(T)` at all is governance-blocked.** Choosing `|Im ρ| < T` over
   `|ρ| ≤ T` is route-indexed and non-interchangeable
   (`GLOBAL_ZEROS_RECON.md:64`; `SC-BRIDGE-02` "Sharing the symbol `T` is not a
   proof"). RvM's `N(T)` is the `|Im ρ| < T` convention. Writing it selects a
   route by the back door.

**Honest cost: 12–24 months**, and it is disqualified on route-neutrality as
written.

### C4 — RvM *upper bound* `N(T) ≪ T log T` (the weakened cousin)

Worth separating, because Jensen **is** pinned:

```
Mathlib/Analysis/Complex/JensenFormula.lean:389
theorem AnalyticOnNhd.sum_divisor_le {c : ℂ} {r R M : ℝ} {f : ℂ → ℂ} (r_pos : 0 < |r|)
    (r_lt_R : |r| < |R|) (hM : 1 ≤ M) (h₁f : AnalyticOnNhd ℂ f (closedBall c |R|))
    (h₂f : f c ≠ 0) (f_bound : ∀ z ∈ sphere c |R|, ‖f z‖ ≤ M) :
    ∑ᶠ u, divisor f (closedBall c |r|) u ≤ Real.log (M / ‖f c‖) / Real.log (R / r)
```

With `f = riemannXi`, `c = 0`: `h₁f` from `analyticOnNhd_riemannXi`
(`Mult.lean:361`), `h₂f` from `riemannXi_zero` (`Xi.lean:72`), divisor plumbing
from `Mult.lean:388,410,538` and the reviewed `ZeroSetSlice.lean` draft.
`f_bound` is the only ungiven hypothesis.

**This is the candidate most likely to be over-sold, and I am flagging it
against the charge.** Two independent defects:

- `f_bound` is a sup on a **circle of radius `|R|`**. G1's strip bound does not
  supply it — a strip leaves every large circle (`GROWTH_RECON.md:663`, which
  says so in as many words). What is needed is an order-one-shape bound
  `‖ξ s‖ ≤ exp(C‖s‖log‖s‖)`, i.e. G2, not G1.
- Converting the radial conclusion `|ρ| ≤ r` into a height cutoff `|Im ρ| ≤ T`
  **is a cutoff-convention choice**, and therefore the same route selection that
  disqualifies C3. A purely radial statement may be defensible as neutral; the
  moment the note says "so `N(T) ≪ T log T`" it has picked a convention.

**Honest cost: 4–8 months**, and it carries a route-selection trap at its last
step.

### C5 — Hardy–Littlewood density `N₀(T) ≫ T`

Everything Hardy needs plus critical-line mean values. Strictly harder than C1.
**Out of reach; multi-year.** Not assessed further.

### C6 — Functional-equation-based zero symmetry counting

**Already built** (`Mult.lean:328`, `:689`). Vocabulary. Not a milestone. Do not
re-target.

### C7 — Mertens-type estimates

Unconditionally proved, elementary, and genuinely absent
(`rg -ni "mertens" Mathlib/` → 1 hit, `RingTheory/Polynomial/ContentIdeal.lean:38`,
the unrelated Dedekind–Mertens lemma).

Mertens' first theorem `∑_{n≤x} Λ(n)/n = log x + O(1)` is reachable from what the
pin actually has:

- `vonMangoldt_sum : ∑ i ∈ n.divisors, Λ i = Real.log n`
  (`ArithmeticFunction/VonMangoldt.lean:102`) gives
  `∑_{n≤x} log n = ∑_{d≤x} Λ(d)⌊x/d⌋`;
- `Stirling.le_log_factorial_stirling` (`Stirling.lean:293`) for
  `∑ log n = x log x − x + O(log x)`;
- `Chebyshev.psi_le_const_mul_self` (`Chebyshev.lean:413`), `psi_le` (`:401`),
  `psi_ge'` (`:443`), `theta_le_log4_mul_x` (`:166`) to control the floor error;
- `AbelSummation.lean:129`, `:189`, `:281` for the summation-by-parts step.

`Mathlib/NumberTheory/Chebyshev.lean` is materially richer than the earlier
scouting reports credited — it carries the full ψ/θ/π transfer including
integral remainders (`:474`–`:697`).

**Honest cost: ~300–600 lines; 1–3 weeks** (the low end is plausible given the
lane's demonstrated transcription rate; the high end allows for the
floor-error bookkeeping, which is the only part that is genuinely fiddly).
Mertens' second theorem, `∑_{p≤x} 1/p = log log x + M + O(1/log x)` with `M`
merely *existing*, is another 2–3 weeks on top.

**But state the trade plainly.** This is a theorem about **primes**. It uses
**zero** of the 70-declaration zeta substrate, closes no barrier row in
`MATHLIB_CAPABILITY_MAP.md`, touches no RH-lane contract, and belongs upstream in
Mathlib rather than in `ResearchOS/`. If the week is measured in "real classical
mathematics landed," this is the honest answer. If it is measured in "RH lane
advanced," it is zero.

### C8 — Ξ real on the critical line

`Ξ(t) := riemannXi (1/2 + t*I)` is real for real `t`. Since
`conj(½+it) = 1−(½+it)`, compose `riemannXi_conj` (`Conj.lean:282`) with
`riemannXi_one_sub` (`Xi.lean:61`), then `Complex.conj_eq_iff_im`
(`Data/Complex/Basic.lean:496`). **One statement, cost ≈ 0.** It is also the
*only* Hardy ingredient the substrate supplies, and it is precisely the
vocabulary-grade one. It does not move Hardy measurably closer.

### C9 — de Bruijn–Newman direction (Λ ≥ 0, Rodgers–Tao 2018; Λ ≤ 1/2, Ki–Kim–Lee)

Both unconditional. Both out of reach by a wide margin. Even *defining* Λ needs
the `H_t` heat flow, de Bruijn's reality theorem, the order of an entire
function, and Laguerre–Pólya theory. **None exists at the pin**: grep across
`Mathlib/Analysis/` for entire order, Hadamard/Weierstrass factorization, genus,
or Laguerre → **0 hits** (re-run this session). Multi-year. Only the *definition*
of Λ_DBN is week-sized, and a definition is more vocabulary — `corpus.md:99-100`
is explicit that a restatement is not progress unless it removes a named barrier.

### C10 — Special values (added by me, and it is dead)

Comprehensively pinned already: `riemannZeta_two_mul_nat`
(`HurwitzZetaValues.lean:206`), `hasSum_zeta_two`/`hasSum_zeta_four`
(`ZetaValues.lean:452`, `:457`), `riemannZeta_zero = -1/2`
(`RiemannZeta.lean:149`), `riemannZeta_one = (γ − log(4π))/2`
(`ZetaAsymp.lean:408`), `deriv_riemannZeta_zero` (`:451`),
`riemannZeta_eulerProduct` (`EulerProduct/DirichletLSeries.lean:102`), and all of
`LSeries/ZetaZeros.lean` (74 lines: closed, discrete, finite-in-compacts).
Nothing to harvest.

### C11 — Simplicity of the trivial zeros (added by me; the best of the sweep)

**`analyticOrderAt riemannZeta (-2 * (n + 1)) = 1` for every `n : ℕ`.**

Classical and unconditional (textbook). Route-neutral — it is a statement about
the trivial zeros, entirely off the critical line, with no cutoff shape and no
route-indexed convention anywhere in it. Absent from Mathlib. And it is a
**named open gap in this repository's own contract**:

> `MULTIPLICITY_CONTRACT.md:686` — *"Do not sharpen this note to 'the trivial
> zeros are simple.'* Simplicity of the trivial zeros is **not** pinned…"

with finding A7 (`:1945`) having deliberately weakened the M4 note to `≠ 0` for
exactly this reason.

Every ingredient is pinned and named:

| step | locator |
|---|---|
| reflection formula `ζ(1−s) = 2(2π)^{−s} Γ(s) cos(πs/2) ζ(s)` | `RiemannZeta.lean:176` (hyps `∀ n:ℕ, s ≠ -n`, `s ≠ 1` — both clear at `s = 2n+3`) |
| `cos(πs/2) = 0` at `s = 2n+3` | `Complex.cos_eq_zero_iff` (`Trigonometric/Complex.lean:33`), with `k = n+1` |
| `deriv ≠ 0` there | `Complex.deriv_cos'` (`Trigonometric/Deriv.lean:131`) + `Complex.sin_ne_zero_iff` (`Trigonometric/Complex.lean:58`) |
| simple-zero order | `AnalyticAt.analyticOrderAt_eq_one_of_zero_deriv_ne_zero` (`Analytic/Order.lean:328`) |
| order of a product is additive | `analyticOrderAt_mul` (`Analytic/Order.lean:497`) |
| unit factors have order 0 | `AnalyticAt.analyticOrderAt_eq_zero` (`Analytic/Order.lean:133`) |
| `Γ(2n+3) ≠ 0`, analytic | `Complex.Gamma_ne_zero_of_re_pos` (`Gamma/Beta.lean:453`), `Complex.differentiableAt_Gamma` (`Gamma/Deriv.lean:65`) |
| `ζ(2n+3) ≠ 0` | `riemannZeta_ne_zero_of_one_le_re` (`Nonvanishing.lean:410`) |
| transport through `s ↦ 1 − s` | **in-repo**: `analyticOrderAt_comp_const_sub` (`Mult.lean:128`) — the exact reparametrisation needed |

Mathematics: at `s = 2n+3` the product `2(2π)^{−s}·Γ(s)·cos(πs/2)·ζ(s)` has
orders `0 + 0 + 1 + 0 = 1`; transport through `1 − s` lands it at `−2(n+1)`.

**Honest content grade: small but real.** It *computes* a multiplicity rather
than relating multiplicities to each other — the first thing in the lane that
does. It is **not** a milestone in the sense the owner means (a named classical
theorem about ζ). It completes the trivial-zero picture: location was pinned,
order was not.

**Honest cost.** ~4–6 declarations, all transport of pinned-and-named
ingredients. At the lane's demonstrated transcription rate that is **1–2 days of
drafting**. The gate is the rest: a new contract with its own claim boundary, one
independent statement-surface acceptance, an adversarial draft review, and a
separate kernel-promotion change carrying ledger rows, registries, and both axiom
audits. **Total 3–6 days**, i.e. one focused week, with one governance caveat and
two technical risks recorded honestly:

- *Governance.* `MULTIPLICITY_CONTRACT.md`'s "No simplicity" boundary forbids
  sharpening *that* package's M4 note. Proving it in a **new** package is not
  forbidden, but the new package's claim boundary must explicitly interact with
  the existing one, and A7 must be marked superseded-in-scope rather than
  silently contradicted. That is a review step, and it is not free.
- *Technical risk 1.* Computing `analyticOrderAt` at `1 − s` from a pointwise
  identity needs the identity on a **neighbourhood**. `riemannZeta_one_sub`'s
  excluded set is discrete and away from `2n+3`, so an `EventuallyEq` is
  available — but it must be produced, and this step has never been elaborated.
- *Technical risk 2.* `Mult.lean:128`'s consumer `analyticOrderAt_comp_of_deriv_ne_zero`
  is the site of the recorded **beta-redex trap** (`MULTIPLICITY_CONTRACT.md`
  finding A2): the point argument arrives as `(fun w => c - w) (c - z)` and
  `rw [sub_sub_cancel]` cannot match it. The repaired idiom
  (`simpa only [sub_sub_cancel] using …`) is recorded and must be reused.

---

## 2. Ranking by genuine mathematical content per unit cost

"Content" here means: does it say something about ζ that the vocabulary does not
already say? "Cost" is the honest calendar figure including this repo's two-stage
gate.

| rank | item | content | cost | content/cost |
|---|---|---|---|---|
| **1** | **C11 — trivial zeros of ζ are simple** | small but **real**: first computed multiplicity in the lane | **3–6 days** | **best available** |
| 2 | `‖Complex.Gamma z‖ ≤ Real.Gamma (re z)` for `0 < re z` | small, real; first brick against the Γ wall; clean upstream PR | 1–2 days (`GROWTH_RECON.md:650` rates it ~1–2 statements, all pinned: `Gamma_eq_integral` `Basic.lean:318`, `GammaIntegral` `:110`, `Real.Gamma_eq_integral` `:404`) | high — but it unblocks nothing on its own, and `GROWTH_RECON.md:650` says it is **not needed on the Mellin route** |
| 3 | C8 — Ξ real on the critical line | **vocabulary** | ≈ 0 | high ratio, ~zero numerator |
| 4 | G1 — Λ₀/ξ bounded on every vertical strip | **first quantitative estimate about ζ in the lane** | **2–4 weeks**, real downside risk | moderate |
| 5 | C7 — Mertens' first theorem | genuine classical theorem | 1–3 weeks | moderate, but the content is **off-lane** (primes, not zeta) |
| 6 | G2 — order-one-shape bound on ξ | genuine; the first thing that feeds a counting theorem | 2–4 months beyond G1 | low |
| 7 | C2 — zero-free region near `re = 1` | **milestone** | 3–6 months | low |
| 8 | C4 — `N(T) ≪ T log T` | **milestone** | 4–8 months **+ a route-selection trap** | low |
| 9 | complex Stirling (the blocker itself) | infrastructure, but the one that gates everything | 3–6 months | low in-lane; **highest strategic value** |
| 10 | C3 / C1 / C5 / C9 | milestones | 12 months to multi-year | negligible |

---

## 3. Blocked behind our own measured barriers vs merely expensive

The owner asked for this distinction explicitly. It is not decorative: an item in
the left column cannot be bought with more effort inside the current disposition,
because the thing standing in front of it is a parked barrier or a forbidden
selection, not a workload.

### Blocked behind a measured-and-parked barrier

| item | barrier | evidence |
|---|---|---|
| ζ bound in the strip (C2's only real gap) | **`S1-GROWTH`, ζ half** | `GROWTH_RECON.md:652` — "large / a genuinely new development / **Blocks the ζ half of the row**" |
| complex Stirling / any `‖Γ‖` bound (C1, C3, C2's ξ-detour) | **`S1-GROWTH`** | `GROWTH_RECON.md:401`, `:651`; `UPSTREAM_POOL.md` §9 "months, no near-miss" |
| `S(T) = O(log T)` (C3) | **`S1-GROWTH`** | `sum_divisor_le`'s `f_bound`, `GROWTH_RECON.md:240` |
| stating `N(T)` at all (C3); the last step of C4 | **`S1-GLOBAL-ZEROS`** | freezing `` `\|Im ρ\| < T` `` is a route selection under a zero-route disposition, `GLOBAL_ZEROS_RECON.md:64` |
| explicit formula, Li coefficients, Hadamard product | **`S1-EXPLICIT`** | `EXPLICIT_RECON.md:120`, verdict "not a closable next target" |
| ξ order ≤ 1 as Hadamard input (G2) | `S1-GROWTH`; **every named consumer parked** | `GROWTH_RECON.md:678` — "the **sharpest** flag … maximum cost with minimum neutrality" |

### Merely expensive (no barrier, just work)

| item | cost |
|---|---|
| rectangle argument principle (Form B) | months, multi-PR; an **absent upstream**, not a repo barrier. `UPSTREAM_POOL.md` §9: π₁(S¹)≅ℤ, homology Cauchy, cycles all absent |
| explicit `ζ(σ) ≤ 1/(σ−1) + C` on `(1,2]` | ~1 week (re-derive `ZetaAsymp` for complex `s`) |
| C7 Mertens | 1–3 weeks |
| `‖Complex.Gamma z‖ ≤ Real.Gamma (re z)` | 1–2 days |
| **C11 trivial-zero simplicity** | **3–6 days** |
| C8 Ξ realness | ≈ 0 |

### Present or nearly free (do not bill these as work)

3-4-1 inequality (`Nonvanishing.lean:284`, `:307`) — hours to specialise, and it
is the *easy* half of a two-half proof; endpoint non-vanishing
(`Nonvanishing.lean:410`) — already proved; FE-based symmetry counting — already
built.

### The governance fact that bears on all of it

**`S1-GROWTH`'s exit condition is currently unsatisfiable by construction.** Its
exit evidence at `MATHLIB_CAPABILITY_MAP.md:388` reads "explicit quantitative
bounds sufficient for **the selected theorem**", and `ROUTE_TRIAGE.md:3-5`
records `PARK`/`PARK`/`PARK` with no `SELECT`. `GROWTH_RECON.md:766`: "There is no
selected theorem. … Choosing a theorem for a bound to be sufficient for **would
be** a route selection." Any week aimed at "closing `S1-GROWTH`" cannot succeed as
the row is written. That is a wording question for the maintainer. This note does
not answer it and does not propose re-scoping the row.

---

## 4. Verdict on the week

**No. There is no genuine, classical, already-proved, route-neutral milestone
theorem about zeta that is reachable in a focused week.**

Every candidate that would count as a milestone — Hardy, the zero-free region,
Riemann–von Mangoldt in either form, Hardy–Littlewood density, de Bruijn–Newman —
runs through one of exactly two absences: **asymptotics/modulus bounds for
`Γ(σ+it)` as `|t| → ∞`**, or **an explicit modulus bound on ζ/ξ off `re s > 1`**.
The pin has neither, has no near-miss for either, and the lane has produced zero
real-analysis estimates to date. The nearest milestone (C2) is 3–6 months and
sits behind a barrier the repo itself measured and parked.

I will not dress a smaller thing as a milestone to make the week look better.

### The smallest genuine thing, and its true timescale

Three honest answers at three different definitions of "genuine," stated
separately so none of them can be quoted as the others:

1. **Smallest genuine mathematical statement about ζ reachable in a week:**
   **C11, simplicity of the trivial zeros** — `analyticOrderAt riemannZeta
   (-2*(n+1)) = 1`. **3–6 days.** Every ingredient pinned and named; route-neutral;
   named as an open gap by this repo's own contract. It is a *small theorem*, not
   a milestone, and the note that carries it must say so.

2. **Smallest genuine *quantitative* statement about ζ — the first inequality in
   the lane:** **G1**, `Λ₀` bounded on every vertical strip, hence
   `‖riemannXi s‖ ≤ (1 + ‖s‖‖s−1‖·M(a,b))/2` on `a ≤ re s ≤ b`
   (`GROWTH_RECON.md:645`). **2–4 weeks, not one**, with real downside risk. Its
   generic lever, `norm_mellin_le_add_of_re_mem_Icc`, is now on the built surface
   (`ResearchOS/Analysis/MellinBound.lean:224`, committed `543f794`) — see Annex
   A, item F1. What remains is Stage 0 (an unelaborated unfolding through three
   `def`s into Mathlib construction internals, `GROWTH_RECON.md:604`) and an
   explicit two-sided decay bound for `(hurwitzEvenFEPair 0).f_modif`, where
   `evenKernel`/`cosKernel` are `@[irreducible]` (`HurwitzZetaEven.lean:65`,
   `:89`) so every estimate must route through the exposed `_def` lemmas and
   `isBigO_atTop_evenKernel_sub` (`:223`) — all `IsBigO` with **non-explicit
   constants**. Workable for `exp(C|s|log|s|)` with unspecified `C`; **not**
   workable for anything needing a numeric constant. And it must travel with its
   own caution: a strip bound is not order one, does not discharge `SC-XI-01`(1),
   and does **not** feed `sum_divisor_le` (`GROWTH_RECON.md:662-668`).

3. **Smallest genuine *milestone-grade classical theorem* about ζ:** **C2, the de
   la Vallée Poussin zero-free region. 3–6 months**, blocked behind `S1-GROWTH`'s
   ζ half as measured. Nothing shortens it except building the missing
   continuation-with-explicit-remainder, which is the barrier.

If instead the week must land a classical theorem of any kind and the lane
coherence is expendable, **C7 Mertens' first theorem (1–3 weeks)** is the only
classical named result on the whole list whose ingredients are all pinned. It
advances the RH lane by exactly nothing, and anyone taking it should be told that
in the same sentence in which it is proposed.

---

## Annex A — red-team of this note, 2026-08-08

Every `file:line` in the body was re-read at the two pinned revisions this
session, and every negative grep was re-run. Findings are recorded below with the
fix applied in place. Fourteen findings; five are corrections to claims inherited
from the three scouting reports this note synthesises, one is a live-repo hazard,
and three are route-selection traps.

### F1 — STALE PLAN (major). "Promote the MellinBound draft" is spent

Two scouting reports proposed, as the concrete content of the focused week,
"Step 1 (~1 week): promote the reviewed `MellinBound.lean` draft." That week is
gone. `ResearchOS/Analysis/MellinBound.lean` exists on the built surface with all
five declarations (`norm_mellin_le` `:86`, `norm_mellin_le_of_norm_le` `:125`,
`setIntegral_rpow_mul_mono_exponent` `:169`, `norm_mellin_le_of_re_le` `:200`,
`norm_mellin_le_add_of_re_mem_Icc` `:224`), is imported from `ResearchOS.lean`,
and is committed as `543f794` (2026-08-08) with its promotion review at
`notes/reviews/MELLIN_PROMOTION_2026_08_07.md`.

Two things must be said with it, and neither may be dropped: the commit is on
branch `claude/rimmen-hypothesis-b6gd62` and is **not merged**, and **no CI run
has elaborated it in this session's view** — under the one invariant the kernel
verdict is still outstanding. So the correct status is *"transcription and review
done, staged, kernel verdict pending"* — neither "not started" nor "done." The
body of this note was corrected to say so (§4, answer 2).

### F2 — LIVE-REPO HAZARD. The tree changed under this recon

At the start of this session `git log` showed head `d97cb3f` with
`ResearchOS/Analysis/` **untracked** and nine files modified. Midway through, a
concurrent session committed `543f794` and the working tree went clean. Any count
or status in this note is therefore accurate as of head `543f794` only. Readers
comparing against a later head should re-derive §0 rather than trust it.

### F3 — COUNT CORRECTION. "71 declarations", "Conj.lean (17)", "70 theorems"

Recounted directly: TargetBridge 8, Xi 11 (+1 `def`), Conj **16**, Mult 34 —
**69 theorems/lemmas plus one `def` = 70 declarations**, not 71, and Conj is 16
not 17. §0 uses the recounted figures.

### F4 — COUNT CORRECTION. "ten route-neutral contracts"

There are **13** `*_CONTRACT.md` files in `domains/riemann-hypothesis/`; removing
`SOURCE_CONTRACTS.md` (a source-extract ledger, a different kind of artifact)
leaves **12** theorem-package contracts. "Ten" is an undercount. Not load-bearing
for any conclusion, but corrected here so it is not propagated again.

### F5 — COUNT CORRECTION. "six reviewed drafts awaiting promotion"

Reconciled rather than rejected. `drafts/` holds ten Lean drafts. Four are
promoted and merged (`RiemannTargetBridge`, `RiemannXi`, `RiemannConj`,
`RiemannMult`). Five await promotion outright (`HarnackDisc`, `PolyLiouville`,
`ThreeCircles`, `ZeroSetSlice`, `RiemannGrowthOrder`). `MellinBound` is the sixth
only in the sense of F1 — promoted-but-unmerged with the kernel verdict pending.
So "six awaiting" is defensible; "six not yet transcribed" is not.

### F6 — LOCATOR FIX. `Complex.Gamma` is not at `Gamma/Basic.lean:311`

`Basic.lean:311` is `Gamma_add_one`. The definition is
**`Gamma/Basic.lean:287`**, and — a fact none of the three reports recorded —
it is **`@[irreducible]`**. `Real.Gamma` is `Basic.lean:401`. This matters for
rank-2 in §2: the `‖Complex.Gamma‖ ≤ Real.Gamma (re ·)` route *must* go through
the public `Gamma_eq_integral` (`Basic.lean:318`), which is exactly what
`GROWTH_RECON.md:650` proposes, so the candidate survives — but "unfold `Gamma`"
will fail, and the estimate is confined to `0 < re s` by that lemma's hypothesis.

### F7 — LOCATOR FIX (and the claim is stronger than stated). No `logGamma` at all

One report wrote "`logGamma` at the pin is real-only (`Gamma/BohrMollerup.lean:140`)."
`:140` is `def logGammaSeq`, an approximating **sequence**. Grepping `logGamma`
across `Mathlib/` returns only `logGammaSeq` and its five companions
(`BohrMollerup.lean:190,206,214,225,241`). There is **no `Real.logGamma` and no
`Complex.logGamma` at the pin.** The correct statement is stronger than the one
inherited, and §C1 now says so.

### F8 — LOCATOR FIX. Two different `hasMellin` theorems were cited as one

One report cited "`AbstractFuncEq.lean:203/:414 hasMellin`" as a single
ingredient. They are different theorems with different hypotheses:
`StrongFEPair.hasMellin` (`:203`, namespace opened at `:183`) holds for **all
`s`**; `WeakFEPair.hasMellin` (`:414`) requires **`hs : P.k < s.re`**. Any G1
argument must name which one it uses. §4 answer 2 now routes through the
`StrongFEPair` form via `toStrongFEPair` (`:307`), matching
`GROWTH_RECON.md:645`.

### F9 — LOCATOR FIX. `IntermediateValue.lean` path

`Mathlib/Order/Interval/Set/IntermediateValue.lean` does not exist. The IVT cited
for Hardy's sign-change step is
**`Mathlib/Topology/Order/IntermediateValue.lean:553`**
(`intermediate_value_Icc`). Corrected in §C1.

### F10 — LOCATOR FIX. `LFunction_modOne_eq`

Cited as `DirichletContinuation.lean:68`; `:68` is the statement body. The
declaration head is **`:67`**. Corrected in §C2.

### F11 — SOFTENED COST (caught in the inherited material). Mertens at "one week"

One report gave Mertens' first theorem as "~300–600 lines, a realistic focused
week"; another gave "3–6 weeks." Both cannot be right. The pinned inventory is
genuinely complete (verified in §C7, and `Chebyshev.lean` is *richer* than either
report credited), so the low figure is not fantasy — but the floor-error
bookkeeping `∑_{d≤x} Λ(d)⌊x/d⌋` is the fiddly part and no report costed it
separately. Recorded as **1–3 weeks**, with the range stated rather than a point
estimate chosen for convenience.

### F12 — SOFTENED COST (caught in the inherited material). "C11 in 4–8 days"

The 4–8 day figure was given without accounting for the two-stage gate, and
without naming the beta-redex trap that this repository's own multiplicity audit
already found on the exact transport lemma the proof needs
(`MULTIPLICITY_CONTRACT.md` finding A2, `Mult.lean:128`'s consumer). Two
technical risks and one governance caveat are now recorded explicitly in §C11.
The figure moved to **3–6 days** — *lower* on the drafting, because the lane's
measured throughput (§0) supports it, and *with the risks named* rather than
absorbed silently. This is the one place where honest re-costing moved a number
down, and the reasoning is on the page so it can be checked.

### F13 — ROUTE-SELECTION TRAP (major). The "smallest milestone" one report chose

One report's headline recommendation was `N(T) ≪ T log T` via
`sum_divisor_le`, with "Step 3 (~1–2 weeks): convert radial `|ρ| ≤ T` to
`|Im ρ| ≤ T` using strip localization." **That step is a cutoff-convention
choice, and freezing a cutoff convention is a route selection** under
`GLOBAL_ZEROS_RECON.md:64` and `SC-BRIDGE-02`. The same report also proposed
feeding `sum_divisor_le` from a strip bound, which `GROWTH_RECON.md:663` states
in as many words does not work — `f_bound` is a **circle** sup. Both defects are
now recorded in §C4, and C4 is disqualified as a week target on both grounds.

### F14 — ROUTE-SELECTION SWEEP of everything this note recommends

Each surviving recommendation was checked for a hidden selection:

- **C11 (trivial-zero simplicity)** — clean. No cutoff shape, no critical-line
  claim, no `T`, no zero-sum, no route-indexed convention. The only governance
  interaction is `MULTIPLICITY_CONTRACT.md`'s claim boundary (§C11), which is a
  review step, not a selection.
- **`‖Complex.Gamma‖ ≤ Real.Gamma (re ·)`** — clean; generic analysis, zero repo
  prerequisites, natural upstream.
- **C8 (Ξ realness)** — clean; it is a corollary of two built theorems.
- **G1** — clean as a statement, but `GROWTH_RECON.md:678` is right that its
  neighbour G2 is the trap, and any contract for G1 must not quietly widen to G2.
  G1 also closes no barrier row: its exit terminates nowhere, and proposing it as
  "closing `S1-GROWTH`" would be re-scoping.
- **C7 (Mertens)** — clean and route-neutral, because it is not about zeta at all.
- **C2, C3, C4** — C3 and C4 carry the cutoff trap (F13); C2 does not, but is
  barrier-blocked.

### Claims deliberately **not** made

No route is selected or unparked. No barrier is closed, re-scoped, or declared
satisfiable. No statement is made about the truth of RH. No queue task is
activated: `RH-012` remains the sole ACTIVE slot. `S1-GROWTH`'s unsatisfiable
exit wording is reported, not repaired. No draft is promoted and no contract is
accepted by this note. Nothing here has been seen by the Lean kernel.
