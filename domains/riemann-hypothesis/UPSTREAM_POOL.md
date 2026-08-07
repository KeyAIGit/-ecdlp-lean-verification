# UPSTREAM POOL — generic complex analysis absent from Mathlib

**Status: DESIGN NOTE. Dated 2026-08-07.**

Read this header before reading anything else in the file.

- This is a **design note for potential upstream contribution to Mathlib**. It is not a
  repository theorem contract, not a Lean draft, not a promotion, and not a target
  registration. Nothing in `targets/*.json` moves because of this file.
- **No proof is asserted here.** Every Lean fragment below is a *proposed statement*.
  None of it has been elaborated — this repository has no Lean toolchain, and the
  inventory below was produced by source reading (ripgrep + `sed`) against a checked-out
  Mathlib tree. A claim that "declaration `X` exists at `file:line`" is a claim about
  *what text is in the tree*, not a claim that anything typechecks, and certainly not a
  claim that any proposed statement is true.
- **No barrier is closed.** In particular this note does not bear on `S1-GLOBAL-ZEROS`
  or `S1-GROWTH`, and does not claim either is closer to closure.
- **No route is selected or unparked.** `repo/ECDLP_DECISION_SUBSTRATE.json` selects no
  route as of its current dated decision, and this note does not change that. It is not
  evidence for a route, and must not be cited as such.
- **Nothing here asserts anything about the Riemann Hypothesis.** Every proposed
  statement quantifies over an arbitrary function with a hypothesis on that function
  alone. None mentions `riemannZeta`, `completedRiemannZeta`, `LSeries`, a critical
  line, a critical strip, or a zero set of any specific function. That is the whole
  point of the pool: it is **route-neutral by construction**, because a generic theorem
  about entire functions selects no route.
- The one repository invariant is untouched: nothing here is a proof, nothing here is a
  `sorry`, nothing here adds an axiom.

## Pinned revision

| | |
|---|---|
| Mathlib checkout | `/workspace/leanprover-community/mathlib4` |
| `git rev-parse HEAD` | `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` |
| Tip commit | `chore: bump toolchain to v4.31.0 (#40633)`, 2026-06-15 |
| Working tree | clean |
| Repo agreement | `lake-manifest.json:8` records `"rev": "fabf563a7c95a166b8d7b6efca11c8b4dc9d911f"` with `"inputRev": "v4.31.0"`; `lean-toolchain` reads `leanprover/lean4:v4.31.0` |

All `file:line` locators below are relative to that checkout at that revision and were
re-derived for this note. Where an earlier reconnaissance asserted "all ingredients are
pinned", that assertion was **spot-checked rather than trusted** — see
[§10 Verification log](#10-verification-log), which records both the checks that passed
and the four places where an earlier note was wrong about a name or a namespace.

## Provenance

Two earlier reconnaissance notes concluded that `S1-GLOBAL-ZEROS` and `S1-GROWTH` should
not be attempted next, because closing either requires a route selection and no route is
selected. Both observed that much of what is missing is not zeta-specific: it is generic
complex analysis absent from Mathlib. **Those notes are not in the working tree** (held
back from a superseded PR), so nothing below depends on them. Every absence and every
locator here was re-derived from the pinned tree.

---

## 0. The absence table (re-derived)

Nine candidates were named by the earlier scouting. All nine are **absent at the pin**.
Re-derivation, not inheritance:

| # | Candidate | Search | Result |
|---|---|---|---|
| 1 | Order / type of an entire function | `rg -i "growthOrder\|orderOfGrowth\|exponentOfConvergence"` over `Mathlib/` | 0 files |
| 2 | Genus, Weierstrass elementary factors | `rg -i "elementaryFactor\|weierstrassFactor"` | 0 in `Analysis/`; the only case-insensitive hits are `PowerSeries.IsWeierstrassFactorization*` in `Mathlib/RingTheory/PowerSeries/WeierstrassPreparation.lean` — unrelated commutative algebra |
| 3 | Hadamard canonical product | `rg -i "canonicalProduct"` | 0 files |
| 4 | Hadamard three-circles | `rg -i "three.circle"` | 0 files |
| 5 | Polynomial-growth Liouville | `Mathlib/Analysis/Complex/Liouville.lean` read in full | every statement hypothesises `IsBounded (range f)`; no degree conclusion anywhere |
| 6 | Argument principle, winding number | `rg -i "argument principle"`, `rg -i "windingNumber"`, `rg -i "winding number"` | 0 files each |
| 7 | Harnack inequality | `rg -i "harnack"` | 0 files |
| 8 | Norm bound for the Mellin transform | `rg "‖mellin\|norm_mellin"` | 0 lines |
| 9 | Norm bound for complex `Gamma` (complex Stirling) | `rg "‖Gamma\|norm_Gamma\|abs_Gamma"` | 0 lines |

Three further absences found while re-deriving, recorded so a later reader does not
repeat the search:

| # | Item | Search | Result |
|---|---|---|---|
| 10 | Any `Entire` / `IsEntire` predicate | `rg "def IsEntire\|def Entire\|abbrev Entire"` | 0 lines — Mathlib writes `Differentiable ℂ f` inline |
| 11 | Any named `Set` for an annulus | `rg "def annulus\|Annulus"` | 0 lines |
| 12 | Residue calculus / residue theorem | `rg -ni "\bresidueTheorem\b\|def residue\b"` | 2 hits, both unrelated: `RingTheory/LocalRing/ResidueField/Defs.lean:36`, `AlgebraicGeometry/ResidueField.lean:54` |
| 13 | `MultipliableLocallyUniformlyOn.differentiableOn` | `rg "MultipliableLocallyUniformlyOn.differentiableOn"` | 0 lines (the *additive* twin exists) |
| 14 | `HasProdLocallyUniformlyOn.mul_compl` | `rg "HasProdLocallyUniformlyOn.mul_compl\|HasProdUniformlyOn.mul_compl"` | 0 lines |

### Namespace hazard, recorded once

`analyticOrderAt` (`Mathlib/Analysis/Analytic/Order.lean:47`,
`noncomputable def analyticOrderAt (f : 𝕜 → E) (z₀ : 𝕜) : ℕ∞`) and
`analyticOrderNatAt` (`:61`) are the **vanishing order of `f` at a point**, not the
growth order of an entire function. `Mathlib/Analysis/Complex/Order.lean` is the partial
order on `ℂ`. Any grep for "order" in this region produces false positives, and any
future growth-order definition must not be called `Complex.order`.

---

## 1. Order and type of an entire function

**Proposed home:** `Mathlib/Analysis/Complex/GrowthOrder.lean`, namespace `Complex`.

### 1.1 Proposed signatures

```lean
namespace Complex

variable {E : Type*} [NormedAddCommGroup E]

/-- The maximum-modulus function `M(f, r) = sup {‖f z‖ | ‖z‖ = r}`. Follows the
convention of `Complex.HadamardThreeLines.sSupNormIm`: a bare `sSup`, meaningful when
`0 ≤ r` and `f` is continuous, with positivity supplied separately. -/
noncomputable def maxModulus (f : ℂ → E) (r : ℝ) : ℝ :=
  sSup ((norm ∘ f) '' Metric.sphere 0 r)

/-- `f` has growth order at most `p`: for every `ε > 0` there are `C, A` with
`‖f z‖ ≤ C * exp (A * (1 + ‖z‖) ^ (p + ε))` for all `z`. -/
def HasGrowthOrderLE (f : ℂ → E) (p : ℝ) : Prop :=
  ∀ ε : ℝ, 0 < ε → ∃ C A : ℝ, 0 ≤ A ∧
    ∀ z : ℂ, ‖f z‖ ≤ C * Real.exp (A * (1 + ‖z‖) ^ (p + ε))

/-- The order of growth: `limsup_{r → ∞} log (log (M (f, r))) / log r`. -/
noncomputable def growthOrder (f : ℂ → E) : EReal :=
  Filter.limsup
    (fun r : ℝ ↦ ((Real.log (Real.log (maxModulus f r)) / Real.log r : ℝ) : EReal))
    Filter.atTop

/-- The type of `f` relative to order `p`: `limsup_{r → ∞} log (M (f, r)) / r ^ p`. -/
noncomputable def growthType (f : ℂ → E) (p : ℝ) : EReal :=
  Filter.limsup
    (fun r : ℝ ↦ ((Real.log (maxModulus f r) / r ^ p : ℝ) : EReal)) Filter.atTop

variable {f g : ℂ → ℂ} {p q : ℝ}

theorem HasGrowthOrderLE.mono {f : ℂ → E} (h : HasGrowthOrderLE f p) (hpq : p ≤ q) :
    HasGrowthOrderLE f q

theorem hasGrowthOrderLE_of_norm_le_exp {f : ℂ → E} {C A : ℝ} (hp : 0 ≤ p) (hA : 0 ≤ A)
    (h : ∀ z : ℂ, ‖f z‖ ≤ C * Real.exp (A * ‖z‖ ^ p)) : HasGrowthOrderLE f p

theorem HasGrowthOrderLE.mul (hf : HasGrowthOrderLE f p) (hg : HasGrowthOrderLE g p) :
    HasGrowthOrderLE (f * g) p

theorem hasGrowthOrderLE_exp : HasGrowthOrderLE Complex.exp 1

theorem growthOrder_le_of_hasGrowthOrderLE {f : ℂ → E} (hf : Differentiable ℂ f)
    (h : HasGrowthOrderLE f p) : growthOrder f ≤ (p : EReal)

end Complex
```

Three design choices, stated so a reviewer can reject them cheaply:

1. **`EReal` codomain.** `EReal` is a `CompleteLinearOrder`, so `limsup` is total and no
   `IsBoundedUnder` side goals appear. This copies `ExpGrowth`, the existing precedent.
   A `ℝ`-valued order would carry `sSup ∅ = 0` junk for infinite-order functions.
2. **A `Prop` layer separate from the numeric layer.** `HasGrowthOrderLE f p` is what one
   actually needs in order to *state* "order at most one", and it is fully supported by
   pinned ingredients. `growthOrder` is the numeric invariant; the bridge between them is
   a genuine theorem, and is listed as **not** pinned.
3. **`(1 + ‖z‖)` base, free constant `A` in the exponent.** Both are load-bearing.
   `1 ≤ 1 + ‖z‖` is what lets `Real.rpow_le_rpow_of_exponent_le` (which *requires*
   `1 ≤ x`) apply, making monotonicity two lines rather than a case split on the unit
   disc. With `A` free, `Real.exp_add` closes the product lemma outright; with `A` pinned
   to 1 the product is off by a factor of 2 in the exponent and needs
   `x ^ a =o[atTop] x ^ b`, which **does not exist** (`rg "isLittleO_rpow_rpow"` → 0).

### 1.2 Pinned ingredients

| Ingredient | Locator |
|---|---|
| `Filter.limsup` | `Mathlib/Order/LiminfLimsup.lean:64` |
| `EReal := WithBot (WithTop ℝ)`, `CompleteLinearOrder` | `Mathlib/Data/EReal/Basic.lean:35` |
| Design precedent `expGrowthSup` | `Mathlib/Analysis/Asymptotics/ExpGrowth.lean:41` (`limsup (fun n ↦ log (u n) / n) atTop`), `expGrowthInf` at `:38` |
| `sSup`-of-norm-image precedent `sSupNormIm` | `Mathlib/Analysis/Complex/Hadamard.lean:77` |
| `Real.rpow_le_rpow (h : 0 ≤ x) (h₁ : x ≤ y) (h₂ : 0 ≤ z)` | `Mathlib/Analysis/SpecialFunctions/Pow/Real.lean:546` |
| `Real.rpow_le_rpow_of_exponent_le (hx : 1 ≤ x) (hyz : y ≤ z)` | `Pow/Real.lean:613` |
| `Complex.norm_exp (z) : ‖exp z‖ = Real.exp z.re` | `Mathlib/Analysis/Complex/Trigonometric.lean:995` |
| `Complex.re_le_norm` | `Mathlib/Analysis/Complex/Norm.lean:43` (via `abs_re_le_norm` at `:38`) |
| Cauchy estimates (for any later order⇒coefficient work) | `Mathlib/Analysis/Complex/Liouville.lean:44` |
| `MeromorphicOn.circleAverage_log_norm` (Jensen) | `Mathlib/Analysis/Complex/JensenFormula.lean:307` |
| Nevanlinna `characteristic = proximity + logCounting` | `Mathlib/Analysis/Complex/ValueDistribution/CharacteristicFunction.lean:53` |

### 1.3 Honest difficulty

**Statements: cheap. The numeric bridge: not pinned.**

`maxModulus`, `HasGrowthOrderLE`, and lemmas `mono` / `of_norm_le_exp` / `mul` /
`hasGrowthOrderLE_exp` need nothing that is not in the table above. Hours to days.

`growthOrder` and `growthType` are cheap to *state* but carry a caveat that must be said
plainly: the inner `Real.log (Real.log (maxModulus f r))` takes junk values whenever
`maxModulus f r ≤ 1`. This is harmless under `atTop` for non-constant entire `f`, but
*proving* it harmless is not part of the definition and is not pinned.

**Hardest step, named:** `growthOrder_le_of_hasGrowthOrderLE`. It needs the limsup
estimate `log (log (C · exp (A (1+r)^{p+ε}))) / log r → p`. The pieces exist
(`Real.log_mul`, `Real.log_rpow`, `isLittleO_log_id_atTop` at
`Mathlib/Analysis/SpecialFunctions/Log/Basic.lean:449`) but **no assembled lemma does
this**, and nothing was elaborated. Treat it as an open obligation, not a result. The
converse bridge (`growthOrder f ≤ p → HasGrowthOrderLE f p`) is strictly harder: it needs
the maximum modulus principle to pass from `sup_{‖z‖=r}` to `sup_{‖z‖≤r}` —
`Complex.norm_le_of_forall_mem_frontier_norm_le`
(`Mathlib/Analysis/Complex/AbsMax.lean:400`) is the right tool and is pinned — plus an
unwritten limsup-to-eventual-bound step.

**Suggested PR split:** definitions + the four cheap lemmas in one PR (all pinned);
`growthOrder` / `growthType` + bridges in a second PR (carries the unpinned obligation).

---

## 2. Weierstrass elementary factors, genus, and the canonical product

**Proposed home:** `Mathlib/Analysis/SpecialFunctions/Complex/WeierstrassFactor.lean`
(W1–W2) and `.../WeierstrassProduct.lean` (W3–W5), namespace `Complex`.

### 2.1 Proposed signatures

```lean
/-- The **Weierstrass elementary factor** of genus `p`:
`E p z = (1 - z) * exp (z + z ^ 2 / 2 + ⋯ + z ^ p / p)`. -/
noncomputable def weierstrassFactor (p : ℕ) (z : ℂ) : ℂ :=
  (1 - z) * Complex.exp (∑ k ∈ Finset.range p, z ^ (k + 1) / (k + 1))

@[simp] lemma weierstrassFactor_apply_zero (p : ℕ) : weierstrassFactor p 0 = 1
@[simp] lemma weierstrassFactor_zero (z : ℂ) : weierstrassFactor 0 z = 1 - z
lemma weierstrassFactor_succ (p : ℕ) (z : ℂ) :
    weierstrassFactor (p + 1) z
      = weierstrassFactor p z * Complex.exp (z ^ (p + 1) / (p + 1))
lemma weierstrassFactor_eq_zero_iff (p : ℕ) (z : ℂ) : weierstrassFactor p z = 0 ↔ z = 1
lemma differentiable_weierstrassFactor (p : ℕ) : Differentiable ℂ (weierstrassFactor p)

/-- Bridge to Mathlib's `Complex.logTaylor`. Pure algebra. -/
lemma logTaylor_neg (p : ℕ) (z : ℂ) :
    Complex.logTaylor (p + 1) (-z) = -∑ k ∈ Finset.range p, z ^ (k + 1) / (k + 1)

/-- Branch-free exponential form: avoids `log_mul` and argument bookkeeping. -/
lemma weierstrassFactor_eq_exp {p : ℕ} {z : ℂ} (hz : z ≠ 1) :
    weierstrassFactor p z
      = Complex.exp (Complex.log (1 - z) + ∑ k ∈ Finset.range p, z ^ (k+1) / (k+1))

theorem norm_log_weierstrassFactor_le {p : ℕ} {z : ℂ} (hz : ‖z‖ < 1) :
    ‖Complex.log (1 - z) + ∑ k ∈ Finset.range p, z ^ (k + 1) / (k + 1)‖
      ≤ ‖z‖ ^ (p + 1) * (1 - ‖z‖)⁻¹ / (p + 1)

/-- **The Weierstrass estimate.** The sole input to the convergence criterion. -/
theorem norm_weierstrassFactor_sub_one_le {p : ℕ} {z : ℂ} (hz : ‖z‖ ≤ 1 / 2) :
    ‖weierstrassFactor p z - 1‖ ≤ 4 / (p + 1) * ‖z‖ ^ (p + 1)

variable {ι : Type*}

/-- The **Weierstrass canonical product** of genus `p` over the zero family `a`. -/
noncomputable def weierstrassProduct (p : ℕ) (a : ι → ℂ) (z : ℂ) : ℂ :=
  ∏' i, weierstrassFactor p (z / a i)

variable {p : ℕ} {a : ι → ℂ}
  (hane  : ∀ i, a i ≠ 0)
  (hprop : Filter.Tendsto (‖a ·‖) Filter.cofinite Filter.atTop)
  (hsum  : Summable fun i ↦ ‖a i‖⁻¹ ^ (p + 1))

theorem hasProdLocallyUniformlyOn_weierstrassProduct :
    HasProdLocallyUniformlyOn (fun i z ↦ weierstrassFactor p (z / a i))
      (weierstrassProduct p a) Set.univ

theorem differentiable_weierstrassProduct : Differentiable ℂ (weierstrassProduct p a)

theorem weierstrassProduct_eq_zero_iff {z : ℂ} :
    weierstrassProduct p a z = 0 ↔ ∃ i, a i = z

theorem analyticOrderAt_weierstrassProduct (w : ℂ) :
    analyticOrderAt (weierstrassProduct p a) w = Nat.card {i | a i = w}

/-- **Weierstrass product theorem.** Genus chosen internally on the diagonal. -/
theorem exists_differentiable_analyticOrderAt_eq (a : ℕ → ℂ) (m : ℕ)
    (hane : ∀ n, a n ≠ 0)
    (hprop : Filter.Tendsto (‖a ·‖) Filter.atTop Filter.atTop) :
    ∃ f : ℂ → ℂ, Differentiable ℂ f ∧
      analyticOrderAt f 0 = m + Nat.card {n | a n = 0} ∧
      ∀ w ≠ 0, analyticOrderAt f w = Nat.card {n | a n = w}
```

Two supporting lemmas the package must also contribute, both **absent** at the pin:

```lean
lemma MultipliableLocallyUniformlyOn.differentiableOn {ι : Type*} {f : ι → ℂ → ℂ}
    {s : Set ℂ} (hs : IsOpen s) (h : MultipliableLocallyUniformlyOn f s)
    (hf : ∀ i, DifferentiableOn ℂ (f i) s) :
    DifferentiableOn ℂ (fun z ↦ ∏' i, f i z)

lemma HasProdLocallyUniformlyOn.mul_compl {s : Set ι} {g₁ g₂ : β → α}
    (h₁ : HasProdLocallyUniformlyOn (fun i : s ↦ f i) g₁ K)
    (h₂ : HasProdLocallyUniformlyOn (fun i : ↥sᶜ ↦ f i) g₂ K) :
    HasProdLocallyUniformlyOn f (g₁ * g₂) K
```

The genus-`= n` diagonal (`weierstrassFactor n (z / a n)`) is what makes W5
hypothesis-free in `p`: on `ball 0 R`, once `‖a n‖ ≥ 2R` the majorant is
`4 · 2^{-(n+1)}`, which is geometric. No exponent-of-convergence side condition is needed.

### 2.2 Pinned ingredients

| Ingredient | Locator |
|---|---|
| `Complex.logTaylor (n : ℕ) : ℂ → ℂ` | `Mathlib/Analysis/SpecialFunctions/Complex/LogBounds.lean:68` (plain `def`) |
| `norm_log_sub_logTaylor_le` | `LogBounds.lean:142` (a `lemma`) |
| **`norm_log_one_sub_inv_add_logTaylor_neg_le`** | `LogBounds.lean:231` (a `lemma`) |
| `Complex.norm_exp_sub_one_le (hx : ‖x‖ ≤ 1) : ‖exp x - 1‖ ≤ 2 * ‖x‖` | `Mathlib/Analysis/Complex/Exponential.lean:439` |
| `HasProdUniformlyOn` | `Mathlib/Topology/Algebra/InfiniteSum/UniformOn.lean:44` |
| `HasProdLocallyUniformlyOn` (**defeq** to `TendstoLocallyUniformlyOn (∏ i ∈ ·, f i ·) g atTop s`) | `UniformOn.lean:152` |
| `MultipliableLocallyUniformlyOn` | `UniformOn.lean:159` |
| `Summable.hasProdUniformlyOn_one_add` | `Mathlib/Analysis/Normed/Module/MultipliableUniformlyOn.lean:87` (inside `namespace Summable`, opened at `:80`) |
| `Summable.hasProdLocallyUniformlyOn_one_add` | `MultipliableUniformlyOn.lean:130` |
| `TendstoLocallyUniformlyOn.differentiableOn` | `Mathlib/Analysis/Complex/LocallyUniformLimit.lean:135` (declared `_root_.`) |
| `Complex.multipliable_one_add_of_summable` | `Mathlib/Analysis/SpecialFunctions/Log/Summable.lean:49` (`namespace Complex`, `:25`–`:53`) |
| `tprod_one_add_ne_zero_of_summable` | `Log/Summable.lean:216` |
| `analyticOrderAt` | `Mathlib/Analysis/Analytic/Order.lean:47` |
| Working template for product ⇒ differentiable | `Mathlib/NumberTheory/ModularForms/DedekindEta.lean:89–95` |

### 2.3 Honest difficulty — and a correction to the intuition

**The package is not estimate-bound.** The classically hardest step is already a theorem
at the pin. `LogBounds.lean:231` says, for `‖z‖ < 1`,
`‖log (1 - z)⁻¹ + logTaylor (n+1) (-z)‖ ≤ ‖z‖^(n+1) * (1 - ‖z‖)⁻¹ / (n+1)`.
Since `logTaylor (p+1) (-z) = -∑_{k=1}^{p} z^k / k`, that *is* the bound on `log E_p(z)`,
modulo `Complex.log_inv` and one `Finset.range` reindex. What remains for
`norm_weierstrassFactor_sub_one_le` is `Complex.exp_log`, `norm_exp_sub_one_le`, and
arithmetic.

Tiering:

- **Tier 0 (hours):** `weierstrassFactor` + simp lemmas, `differentiable_weierstrassFactor`,
  `weierstrassFactor_eq_zero_iff` (via `Complex.exp_ne_zero`), `logTaylor_neg`,
  `weierstrassFactor_eq_exp`, `MultipliableLocallyUniformlyOn.differentiableOn`
  (copy `DedekindEta.lean:89–95`).
- **Tier 1 (a day each):** the two estimates.
- **Tier 2 (a week):** `hasProdLocallyUniformlyOn_weierstrassProduct` — reshape into the
  `1 + f i z` normal form the criterion demands, then `hasProdLocallyUniformlyOn_of_forall_compact`.
  Fiddly properness bookkeeping; no new mathematics.
- **Tier 3 (a week):** `weierstrassProduct_eq_zero_iff` — pointwise split via
  `Multipliable.tprod_mul_tprod_compl`, complementary factor killed by
  `tprod_one_add_ne_zero_of_summable`.
- **Tier 4 — the actual obstruction (weeks):** `analyticOrderAt_weierstrassProduct`.
  Reading off the *order* rather than mere vanishing needs the factorization as an
  identity of **analytic functions on a neighbourhood** of `w`, which Tier 3's pointwise
  split does not deliver. It needs `HasProdLocallyUniformlyOn.mul_compl`, confirmed
  absent (§0, row 14).
- **Tier 5 — do not attempt here:** the sharp classical
  `‖1 - E_p z‖ ≤ ‖z‖^(p+1)` on the closed unit disc (Rudin RCA 15.8). It requires
  nonnegativity of every Taylor coefficient of `exp(∑_{k=1}^p z^k/k)` and a term-by-term
  comparison, with no Mathlib precursor. It is strictly stronger than the `4/(p+1)` form
  and is **not required** by anything in W1–W5.

**Hardest step, named:** `HasProdLocallyUniformlyOn.mul_compl` and the
`analyticOrderAt` computation it enables. Anyone budgeting for "the hard analytic
estimate" will mis-budget: the estimate is nearly free, the bookkeeping is not.

**Corroborating evidence that this is the real gap:** the existing Euler sine product
development (`Mathlib/Analysis/SpecialFunctions/Trigonometric/Cotangent.lean`,
`HasProdLocallyUniformlyOn_euler_sin_prod` at `:132`) states everything on `ℂ_ℤ`, the
complement of `ℤ`. The Weierstrass-shaped content — *the product is entire and its zeros
are exactly `ℤ`, simple* — is precisely what that development routes around.

---

## 3. Hadamard three-circles

**Proposed home:** an addition to `Mathlib/Analysis/Complex/Hadamard.lean`, or a small
new file next to it.

### 3.1 Proposed signature

```lean
/-- **Hadamard three-circles theorem.** -/
theorem Complex.norm_le_interp_of_norm_eq_of_le_of_le
    {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
    {f : ℂ → E} {r₁ r₂ r₃ M₁ M₃ : ℝ} {z : ℂ}
    (h₁ : 0 < r₁) (h₁₂ : r₁ ≤ r₂) (h₂₃ : r₂ ≤ r₃) (h₁₃ : r₁ < r₃)
    (hd : DifferentiableOn ℂ f {w : ℂ | r₁ < ‖w‖ ∧ ‖w‖ < r₃})
    (hc : ContinuousOn f {w : ℂ | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃})
    (hM₁ : ∀ w : ℂ, ‖w‖ = r₁ → ‖f w‖ ≤ M₁)
    (hM₃ : ∀ w : ℂ, ‖w‖ = r₃ → ‖f w‖ ≤ M₃)
    (hz : ‖z‖ = r₂) :
    ‖f z‖ ≤ M₁ ^ (Real.log (r₃ / r₂) / Real.log (r₃ / r₁))
            * M₃ ^ (Real.log (r₂ / r₁) / Real.log (r₃ / r₁))
```

Exponent check: with `l := log r₁`, `u := log r₃`, `z'.re = log r₂`, the three-lines
interpolation parameter is `t = (log r₂ − log r₁)/(log r₃ − log r₁) = log(r₂/r₁)/log(r₃/r₁)`
and `1 − t = log(r₃/r₂)/log(r₃/r₁)`. Consistent.

### 3.2 Pinned ingredients

| Ingredient | Locator |
|---|---|
| Three-**lines**, endpoint-bound form: `Complex.HadamardThreeLines.norm_le_interp_of_mem_verticalClosedStrip'` | `Mathlib/Analysis/Complex/Hadamard.lean:607` (namespaces `Complex` at `:66`, `HadamardThreeLines` at `:67`) |
| Sup-function form `norm_le_interpStrip_of_mem_verticalClosedStrip` | `Hadamard.lean:588` |
| `verticalStrip`, `verticalClosedStrip` | `Hadamard.lean:70`, `:73` |
| Engine: `PhragmenLindelof.vertical_strip` | `Mathlib/Analysis/Complex/PhragmenLindelof.lean:275` |
| `Complex.norm_mul_exp_arg_mul_I` (surjectivity onto each circle) | `Mathlib/Analysis/SpecialFunctions/Complex/Arg.lean:56` |
| `Complex.norm_exp` | `Mathlib/Analysis/Complex/Trigonometric.lean:995` |
| `differentiable_exp` | `Mathlib/Analysis/SpecialFunctions/ExpDeriv.lean:97` |
| `Real.exp_log` | `Mathlib/Analysis/SpecialFunctions/Log/Basic.lean:58` |
| `closure_preimage_re` (gives `closure (verticalStrip l u) = verticalClosedStrip l u`) | `Mathlib/Analysis/Complex/ReImTopology.lean:70` |
| `IsCompact.bddAbove_image` (discharges `hB`) | `Mathlib/Topology/Order/Compact.lean:332` |
| `Differentiable.diffContOnCl` | `Mathlib/Analysis/Calculus/DiffContOnCl.lean:42` |

Note the three-lines statement needs only `[NormedAddCommGroup E] [NormedSpace ℂ E]` —
**no `CompleteSpace`**.

### 3.3 Honest difficulty

**Cheap. This is a reduction, not a new analytic idea.** `exp` maps the closed strip
`re ⁻¹' Icc (log r₁) (log r₃)` *onto* the closed annulus. Because `f ∘ exp` needs only
holomorphy and boundedness — not injectivity — **no branch of `log` is required**. That
is exactly why three-circles is a corollary of three-lines rather than an independent
development.

**Hardest step, named:** discharging `hB : BddAbove ((norm ∘ f ∘ exp) '' verticalClosedStrip l u)`.
The closed annulus is compact (closed subset of a closed ball) and `f` is `ContinuousOn`
it, so `IsCompact.bddAbove_image` applies — but the strip itself is *not* compact, so the
bound must be transported through `exp` rather than taken on the strip directly. Routine,
and the only place a careful writer will spend time.

**Friction, not a gap:** there is no `Set`-level annulus abbreviation at the pin (§0, row
11), so the statement must spell out `{w | r₁ ≤ ‖w‖ ∧ ‖w‖ ≤ r₃}` or introduce one. A
Mathlib reviewer may have an opinion about which.

---

## 4. Polynomial-growth Liouville

**Proposed home:** an addition to `Mathlib/Analysis/Complex/Liouville.lean`.

### 4.1 Proposed signatures

```lean
/-- **Liouville, polynomial-growth form**: an entire function of polynomial growth of
degree `≤ n` is a polynomial of degree `≤ n`. -/
theorem Complex.exists_polynomial_of_norm_le_pow
    {f : ℂ → ℂ} {C : ℝ} {n : ℕ} (hf : Differentiable ℂ f)
    (hC : ∀ z : ℂ, ‖f z‖ ≤ C * (1 + ‖z‖) ^ n) :
    ∃ p : Polynomial ℂ, p.natDegree ≤ n ∧ ∀ z : ℂ, f z = p.eval z

/-- The step that carries all the analysis; strictly weaker, and it generalises to
Banach-valued `f`. -/
theorem Complex.iteratedDeriv_eq_zero_of_norm_le_pow
    {F : Type*} [NormedAddCommGroup F] [NormedSpace ℂ F] [CompleteSpace F]
    {f : ℂ → F} {C : ℝ} {n k : ℕ} (hkn : n < k) (hf : Differentiable ℂ f)
    (hC : ∀ z : ℂ, ‖f z‖ ≤ C * (1 + ‖z‖) ^ n) (c : ℂ) :
    iteratedDeriv k f c = 0
```

Setting `n = 0` recovers `Differentiable.exists_eq_const_of_bounded` up to the
`IsBounded (range f)` ↔ `∀ z, ‖f z‖ ≤ C` repackaging — a useful sanity target.

### 4.2 Pinned ingredients

| Ingredient | Locator |
|---|---|
| **Cauchy estimate, already `n`-indexed:** `Complex.norm_iteratedDeriv_le_of_forall_mem_sphere_norm_le [CompleteSpace F] (n) (hR) (hf) (hC) : ‖iteratedDeriv n f c‖ ≤ n.factorial * C / R ^ n` | `Mathlib/Analysis/Complex/Liouville.lean:44` |
| Existing (bounded-only) Liouville family | `Liouville.lean:114`, `:123`, `:128`, `:135` |
| `Polynomial.div_tendsto_atTop_zero_of_degree_lt` (the `R → ∞` kill) | `Mathlib/Analysis/Polynomial/Basic.lean:161` |
| `Complex.hasSum_taylorSeries_of_entire` | `Mathlib/Analysis/Complex/TaylorSeries.lean:129` (`[CompleteSpace E]` from `:35`) |
| `Complex.taylorSeries_eq_of_entire'` | `TaylorSeries.lean:139` |
| Finite-support `HasSum` collapse (`hasSum_sum_of_ne_finset_zero`) | used in-tree at `Mathlib/Analysis/Analytic/CPolynomialDef.lean:72,215` |
| Alternative codomain `HasFiniteFPowerSeriesOnBall` / `CPolynomialOn` | `CPolynomialDef.lean:62,79,94,99` |

### 4.3 Honest difficulty

**Cheap — close to a corollary.** With `C := C₀ * (1 + R)^n` the Cauchy estimate gives
`‖iteratedDeriv k f 0‖ ≤ k! · C₀ · (1+R)^n / R^k → 0` for `k > n`. All four pieces
(estimate, limit, Taylor expansion, finite collapse) are pinned.

**Hardest step, named:** repackaging the finitely-supported Taylor `HasSum` into an
honest `Polynomial ℂ` with a `natDegree` bound. `Polynomial.eval_finset_sum` and
`Polynomial.natDegree_sum_le` do the work, but this is the only place where a `∑`
over `Finset.range (n+1)` has to become a term of type `Polynomial ℂ` and the degree
bound has to survive. Bookkeeping, but real bookkeeping.

**Carry the hypothesis:** `[CompleteSpace F]` is required by the Cauchy estimate.
Harmless for `F = ℂ`, mandatory in the Banach-valued companion.

---

## 5. Harnack inequality

**Proposed home:** a new file under `Mathlib/Analysis/Complex/Harmonic/`.

### 5.1 Proposed signature

```lean
/-- **Harnack's inequality** for nonnegative harmonic functions on a disc. -/
theorem InnerProductSpace.HarmonicOnNhd.harnack
    {f : ℂ → ℝ} {c w : ℂ} {R : ℝ}
    (hf : HarmonicOnNhd f (Metric.closedBall c R))
    (hf₀ : ∀ z ∈ Metric.closedBall c R, 0 ≤ f z)
    (hR : 0 < R) (hw : w ∈ Metric.ball c R) :
    (R - ‖w - c‖) / (R + ‖w - c‖) * f c ≤ f w
      ∧ f w ≤ (R + ‖w - c‖) / (R - ‖w - c‖) * f c
```

Namespace note (a correction to earlier scouting): `HarmonicOnNhd` is defined inside
`namespace InnerProductSpace` (`Mathlib/Analysis/InnerProductSpace/Harmonic/Basic.lean:27`,
def at `:46`), so the full name of the proposed theorem is
`InnerProductSpace.HarmonicOnNhd.harnack`, not `HarmonicOnNhd.harnack`. The existing
`Mathlib/Analysis/Complex/Harmonic/MeanValue.lean` writes `theorem HarmonicOnNhd.…` only
because it has `open InnerProductSpace` at `:18`.

### 5.2 Pinned ingredients

| Ingredient | Locator |
|---|---|
| `HarmonicAt`, `HarmonicOnNhd` | `Mathlib/Analysis/InnerProductSpace/Harmonic/Basic.lean:39`, `:46` (ns `InnerProductSpace`, `:27`) |
| Harmonic ⇒ real part of analytic: `InnerProductSpace.HarmonicOnNhd.exists_analyticOnNhd_ball_re_eq` | `Mathlib/Analysis/Complex/Harmonic/Analytic.lean:70` |
| `poissonKernel` | `Mathlib/Analysis/Complex/Poisson.lean:54` |
| `poissonKernel_eq_re_herglotzRieszKernel` | `Poisson.lean:73` |
| **Sharp upper kernel bound** `re_herglotzRieszKernel_le` | `Poisson.lean:101` |
| **Sharp lower kernel bound** `le_re_herglotzRieszKernel` | `Poisson.lean:134` |
| Poisson representation `DiffContOnCl.circleAverage_poissonKernel_smul` | `Poisson.lean:245` (primed variant `:255`) |
| `circleAverage` | `Mathlib/MeasureTheory/Integral/CircleAverage.lean:54` |
| `circleAverage_mono` (`@[gcongr]`) | `CircleAverage.lean:271` |
| `ContinuousLinearMap.circleAverage_comp_comm` (pushes `reCLM` inside) | `CircleAverage.lean:318` |
| Mean value property `HarmonicOnNhd.circleAverage_eq` | `Mathlib/Analysis/Complex/Harmonic/MeanValue.lean:27` |
| `ContinuousOn.circleIntegrable` | `Mathlib/MeasureTheory/Integral/CircleIntegral.lean:337` |

### 5.3 Honest difficulty

**Cheap relative to how surprising the absence is.** The one genuinely analytic input —
the sharp two-sided Poisson-kernel bound — is *already two theorems* at
`Poisson.lean:101` and `:134`. Only the integration step against a nonnegative harmonic
function is unwritten.

Derivation entirely from the table: `exists_analyticOnNhd_ball_re_eq` on a slightly larger
ball gives `F` with `re ∘ F = f`; `DiffContOnCl.circleAverage_poissonKernel_smul` gives
`F w = circleAverage (poissonKernel c w • F) c R`;
`ContinuousLinearMap.circleAverage_comp_comm reCLM` pushes `re` inside;
`poissonKernel_eq_re_herglotzRieszKernel` plus the two kernel bounds bound the kernel by
the two constants; `f ≥ 0` with `circleAverage_mono` turns those into bounds on the
average; `HarmonicOnNhd.circleAverage_eq` replaces `circleAverage f c R` by `f c`.

**Hardest step, named:** the open/closed mismatch. `circleAverage_poissonKernel_smul`
wants `DiffContOnCl` on the *closed* ball, while `exists_analyticOnNhd_ball_re_eq` yields
`AnalyticOnNhd` on an *open* ball, so a thickening/shrink step is required. This is not a
missing ingredient — the pattern is copyable from the proof body of
`HarmonicOnNhd.circleAverage_eq` (`MeanValue.lean:30–36`), which already runs
`isCompact_closedBall.exists_thickening_subset_open` →
`exists_analyticOnNhd_ball_re_eq` → `DifferentiableOn ℂ F (closure (ball c |R|))`. The
second friction is discharging `CircleIntegrable` side conditions for
`circleAverage_mono`, needing continuity of `poissonKernel c w` on `sphere c R`.

The Harnack-chain corollary (`f w₁ ≤ K * f w₂` on a compact subset) follows by composing
the two halves and is the form usually consumed downstream.

---

## 6. A norm bound for the Mellin transform

**Proposed home:** an addition to `Mathlib/Analysis/MellinTransform.lean`.

### 6.1 Proposed signatures

```lean
/-- The Mellin transform is bounded by the Mellin transform of the norm, evaluated at
the real part of the exponent. -/
theorem norm_mellin_le
    {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E] (f : ℝ → E) (s : ℂ) :
    ‖mellin f s‖ ≤ ∫ t : ℝ in Set.Ioi 0, t ^ (s.re - 1) * ‖f t‖

theorem norm_mellin_le_mellin_norm (f : ℝ → E) (s : ℂ) :
    ‖mellin f s‖ ≤ mellin (fun t ↦ ‖f t‖) (s.re : ℂ)

theorem norm_mellin_le_of_norm_le {g : ℝ → ℝ}
    (hg : IntegrableOn (fun t ↦ t ^ (s.re - 1) * g t) (Set.Ioi 0))
    (h : ∀ t ∈ Set.Ioi (0:ℝ), ‖f t‖ ≤ g t) :
    ‖mellin f s‖ ≤ ∫ t in Set.Ioi 0, t ^ (s.re - 1) * g t
```

The third is the form actually consumed: it shows `‖mellin f s‖` depends on `s` only
through `s.re`.

### 6.2 Pinned ingredients

| Ingredient | Locator |
|---|---|
| `mellin (f) (s) := ∫ t in Ioi 0, (t : ℂ) ^ (s - 1) • f t` | `Mathlib/Analysis/MellinTransform.lean:91` (`[NormedAddCommGroup E] [NormedSpace ℂ E]` from `:42`) |
| `MellinConvergent` | `MellinTransform.lean:45` |
| `norm_integral_le_integral_norm (f) : ‖∫ a, f a ∂μ‖ ≤ ∫ a, ‖f a‖ ∂μ` — **unconditional** | `Mathlib/MeasureTheory/Integral/Bochner/Basic.lean:924` |
| `norm_integral_le_of_norm_le` | `Bochner/Basic.lean:937` |
| `Complex.norm_cpow_eq_rpow_re_of_pos (hx : 0 < x) (y) : ‖(x : ℂ) ^ y‖ = x ^ y.re` | `Mathlib/Analysis/SpecialFunctions/Pow/Real.lean:337` |
| The same rewrite already firing in-tree | `MellinTransform.lean:349` (and inside `mellin_convergent_iff_norm`) |
| `setIntegral_congr_fun` | `Mathlib/MeasureTheory/Integral/Bochner/Set.lean:73` |
| `integrableOn_Ioi_rpow_of_lt`, `not_integrableOn_Ioi_rpow` | `Mathlib/Analysis/SpecialFunctions/ImproperIntegrals.lean:131`, `:160` |

### 6.3 Honest difficulty

**The cheapest item in the pool.** Three steps: `mellin` unfolds by `rfl` to a set
integral; `norm_integral_le_integral_norm` applies with `μ := volume.restrict (Ioi 0)`;
`setIntegral_congr_fun measurableSet_Ioi` rewrites the RHS using the pointwise norm
identity. The first result is **unconditional** — `norm_integral_le_integral_norm` needs
no integrability hypothesis (it handles the non-`AEStronglyMeasurable` case internally),
and step 3 is an equality of integrals. A variant guarded by `MellinConvergent f s` is a
corollary, not a prerequisite.

**Hardest step, named:** the `EqOn` for step 3 — assembling
`‖(t:ℂ)^(s-1) • f t‖ = t^(s.re - 1) * ‖f t‖` on `Ioi 0` from `norm_smul`,
`norm_cpow_eq_rpow_re_of_pos`, `Complex.sub_re`, `Complex.one_re`. Mathlib already
performs this exact `simp_rw` chain at `MellinTransform.lean:349`, so it is known to fire
at this pin. Hours.

---

## 7. The argument principle and winding numbers

**Proposed home:** `Mathlib/Analysis/Complex/ArgumentPrinciple.lean`.

There are two inequivalent minimal targets and choosing between them is the whole
question. Both are laid out; neither is recommended over the other here.

### 7.1 Form A — fix the contour to be a circle

With a circle the index never has to be *defined*: it is 1 inside and 0 outside, and both
are theorems about `∮`.

```lean
/-- Fills the gap Mathlib's own docstring flags. -/
theorem circleIntegral.integral_sub_inv_of_notMem_closedBall
    {c w : ℂ} {R : ℝ} (hw : w ∉ Metric.closedBall c R) :
    (∮ z in C(c, R), (z - w)⁻¹) = 0

/-- Zeros of `f` in `ball c R`, with multiplicity. -/
noncomputable def Complex.zeroCount (f : ℂ → ℂ) (c : ℂ) (R : ℝ) : ℤ :=
  ∑ᶠ u, MeromorphicOn.divisor f (Metric.ball c R) u

/-- **Argument principle on a disc, analytic case.** -/
theorem Complex.circleIntegral_logDeriv_eq_zeroCount
    {f : ℂ → ℂ} {c : ℂ} {R : ℝ} (hR : 0 < R)
    (hf : AnalyticOnNhd ℂ f (Metric.closedBall c R))
    (hf₀ : ∀ z ∈ Metric.sphere c R, f z ≠ 0) :
    (∮ z in C(c, R), deriv f z / f z)
      = 2 * Real.pi * Complex.I * (Complex.zeroCount f c R : ℂ)

theorem MeromorphicOn.circleIntegral_logDeriv
    {f : ℂ → ℂ} {c : ℂ} {R : ℝ} (hR : 0 < R)
    (hf : MeromorphicOn f (Metric.closedBall c R))
    (h₂f : ∀ u : Metric.closedBall c R, meromorphicOrderAt f u ≠ ⊤)
    (hf₀ : ∀ z ∈ Metric.sphere c R, meromorphicOrderAt f z = 0) :
    (∮ z in C(c, R), deriv f z / f z)
      = 2 * Real.pi * Complex.I * (∑ᶠ u, MeromorphicOn.divisor f (Metric.ball c R) u : ℤ)

/-- Weighted form: `(2πi)⁻¹ ∮ g · (f'/f) = Σ mult(u) · g u`. Locates zeros rather
than merely counting them. -/
theorem Complex.circleIntegral_mul_logDeriv
    {f g : ℂ → ℂ} {c : ℂ} {R : ℝ} (hR : 0 < R)
    (hf : AnalyticOnNhd ℂ f (Metric.closedBall c R))
    (hg : AnalyticOnNhd ℂ g (Metric.closedBall c R))
    (hf₀ : ∀ z ∈ Metric.sphere c R, f z ≠ 0) :
    (∮ z in C(c, R), g z * (deriv f z / f z))
      = 2 * Real.pi * Complex.I *
          ∑ᶠ u, (MeromorphicOn.divisor f (Metric.ball c R) u : ℂ) * g u

/-- **Rouché's theorem** on a disc — the corollary that makes the addition worth
reviewing upstream. -/
theorem Complex.zeroCount_eq_of_norm_sub_lt
    {f g : ℂ → ℂ} {c : ℂ} {R : ℝ} (hR : 0 < R)
    (hf : AnalyticOnNhd ℂ f (Metric.closedBall c R))
    (hg : AnalyticOnNhd ℂ g (Metric.closedBall c R))
    (h : ∀ z ∈ Metric.sphere c R, ‖f z - g z‖ < ‖f z‖) :
    Complex.zeroCount f c R = Complex.zeroCount g c R
```

### 7.2 Form B — define a genuine index

```lean
noncomputable def Path.index {z : ℂ} (γ : Path z z) (w : ℂ) (hw : w ∉ Set.range γ) : ℤ

theorem Path.index_circle {c w : ℂ} {R : ℝ} (hw : w ∈ Metric.ball c R) :
    (Path.circle c R).index w … = 1
theorem Path.index_eq_zero_of_notMem_closedBall …
theorem Path.index_of_homotopic …
theorem Path.index_trans …
theorem Path.isLocallyConstant_index …
theorem Path.index_eq_curveIntegral …
theorem Complex.curveIntegral_logDeriv_eq_sum_index …
```

### 7.3 Pinned ingredients

| Ingredient | Locator |
|---|---|
| `circleIntegral.integral_sub_inv_of_mem_ball` (`= 2πI` inside) | `Mathlib/MeasureTheory/Integral/CircleIntegral.lean:699` |
| The documented gap (`n = -1`, `w` outside) | `CircleIntegral.lean:50–56` — the docstring says the proof is postponed until Cauchy's theorem is available, citing PR #10000. Cauchy's theorem *is* available now |
| `integral_sub_zpow_of_undef`, `integral_sub_zpow_of_ne` | `CircleIntegral.lean:557`, `:566` |
| `DiffContOnCl.circleIntegral_eq_zero` | `Mathlib/Analysis/Complex/CauchyIntegral.lean:459` |
| `circleIntegral_eq_zero_of_differentiable_on_off_countable` | `CauchyIntegral.lean:440` |
| `circleIntegral_congr_codiscreteWithin` | `CircleIntegral.lean:430` |
| **`divisor_ball_support_finite`** — finiteness of the zero set is a *theorem* | `Mathlib/Analysis/Meromorphic/Divisor.lean:104` |
| `MeromorphicOn.extract_zeros_poles` | `Mathlib/Analysis/Meromorphic/FactorizedRational.lean:291` |
| `logDeriv_prod` (over a `Finset` only) | `Mathlib/Analysis/Calculus/LogDeriv.lean:73` |
| Jensen's formula `MeromorphicOn.circleAverage_log_norm` | `Mathlib/Analysis/Complex/JensenFormula.lean:307` |
| Jensen's inequality `AnalyticOnNhd.sum_divisor_le` | `JensenFormula.lean:389` |
| Covering-map substrate: `isAddQuotientCoveringMap_exp`, `isCoveringMap_exp`, `isCoveringMapOn_exp` | `Mathlib/Analysis/Complex/CoveringMap.lean:29`, `:40`, `:43` |
| Curve integrals along a `Path` (new at this pin) | `Mathlib/MeasureTheory/Integral/CurveIntegral/{Basic,Poincare}.lean` |
| Borel–Carathéodory (adjacent, present) | `Mathlib/Analysis/Complex/BorelCaratheodory.lean:86`, `:109` |

### 7.4 Honest difficulty

**Form A: small-to-medium.** Roughly one new file, on the order of 400–900 lines. Not
larger, because the two things that would normally dominate are already done at this pin:
Cauchy's theorem on a disc, and the divisor/order/factorization stack with
`divisor_ball_support_finite` and `extract_zeros_poles`.

**Hardest step, named — the codiscreteness bridge.** `extract_zeros_poles` gives
`f =ᶠ[codiscreteWithin U] (∏ᶠ u, (· - u) ^ divisor f U u) • g`, but the argument
principle needs an identity of `deriv f / f` *pointwise on the sphere*. Two routes: (a)
upgrade codiscrete agreement to genuine `EqOn` near the sphere via the identity theorem,
then differentiate; or (b) bypass `extract_zeros_poles` and build the factorization
directly by induction on the finite zero set using `analyticOrderNatAt` and the local
lemmas in `Analysis/Analytic/Order.lean`. Route (b) is likely cleaner but re-proves part
of `extract_zeros_poles`. `circleIntegral_congr_codiscreteWithin` helps at the last step
but not with the derivative. This is where a competent formalizer should expect to lose
real time; everything else in Form A is assembly.

**Form B: a multi-month upstream project, not a task.** Additionally missing, each
independently significant: extraction of an `ℤ` from
`liftPath … 1 − liftPath … 0 ∈ AddSubgroup.zmultiples (2πI)`; local constancy of the
index in `w` and vanishing on the unbounded component; π₁(ℂ \ {0}) ≅ ℤ (absent — no
fundamental-group-of-the-circle result exists); a `curveIntegral` ↔ `circleIntegral`
bridge (absent — the two theories are currently disjoint); homotopy invariance of contour
integrals for *merely continuous* homotopies (the existing Poincaré result in
`CurveIntegral/Poincare.lean` demands a `C²` homotopy, and its own header defers the
simply-connected case); Cauchy's theorem for null-homologous cycles (absent —
`Mathlib/Analysis/Complex/HasPrimitives.lean` does not even have the simply-connected
case, per its own TODO); and a theory of cycles/chains (absent). Several thousand lines
across multiple PRs, with design questions needing maintainer buy-in before code.

### 7.5 Two framing caveats a reviewer will raise

- **Do not state "finitely many zeros" as a hypothesis.** `divisor_ball_support_finite`
  proves it from analyticity on the closed ball. Assuming it produces a weaker,
  less idiomatic theorem a Mathlib reviewer would ask to have removed.
- **Do not claim "Mathlib cannot count zeros."** It already does, twice: exactly via
  `MeromorphicOn.divisor` + Jensen's formula, and with a bound via
  `AnalyticOnNhd.sum_divisor_le`. The honest motivation for `∮ f'/f` is: Rouché (which
  does not follow from Jensen), the weighted form (which *locates* zeros), and the bridge
  to residue calculus (which is entirely absent, §0 row 12).

---

## 8. A norm bound for the complex Gamma function (complex Stirling)

**Status: named by the earlier scouting, and the worst-supported item in the pool.**
No signature is proposed here, deliberately.

### 8.1 What is present, and what is not

`Mathlib/Analysis/SpecialFunctions/Stirling.lean` is entirely about `n !` for `n : ℕ` —
`stirlingSeq n = n ! / (√(2n) (n/e)^n)`, `factorial_isEquivalent_stirling`,
`le_factorial_stirling`. It is a real-factorial development and does not generalise
mechanically. `Gamma/BohrMollerup.lean` is real; its own commentary notes the Stirling
constant is not deduced there. For complex `Gamma` the tree has `Gamma_ne_zero`,
`Gamma_eq_zero_iff`, reflection, duplication — and **no size bound of any kind**
(`rg "‖Gamma\|norm_Gamma\|abs_Gamma"` → 0 lines).

Also absent and adjacent: Paley–Wiener, exponential type, Bernstein spaces, Hardy spaces
(`SpecialFunctions/Bernstein.lean` is Bernstein *polynomials*).

### 8.2 Honest difficulty

**A project, not a reduction.** Unlike §3–§6, there is no pinned near-miss to reduce to:
the real Stirling development shares neither its statement shape nor its proof technique
with a complex-strip bound. A serious attempt would need a complex Binet/Stirling
development from scratch, or a route through the Mellin/Hadamard machinery that itself
does not exist yet.

**Recommendation for scoping, not for action:** do not bundle this with any of §3–§6.
If it is attempted at all it should be its own multi-PR effort, and it should be scoped
after §1 (order/type) exists, since the natural statements are growth statements.

---

## 9. Ranking: cost against neutrality

All eight pieces are equally route-neutral — every proposed statement quantifies over an
arbitrary function with a hypothesis on that function alone, and none mentions a zeta
function, an L-function, a critical strip, or a route. Neutrality therefore does not
discriminate; cost does.

| Rank | Piece | Cost | All ingredients pinned? | Hardest single step |
|---|---|---|---|---|
| 1 | **Mellin norm bound** (§6) | **hours** — cheapest | **Yes**, all three steps located; the rewrite already fires at `MellinTransform.lean:349` | assembling the `EqOn` for `setIntegral_congr_fun` |
| 2 | Polynomial-growth Liouville (§4) | days | **Yes** — Cauchy estimate at `Liouville.lean:44` is already `n`-indexed | repackaging the finite Taylor `HasSum` as a `Polynomial ℂ` with a `natDegree` bound |
| 3 | Hadamard three-circles (§3) | days | **Yes** — a genuine reduction; `exp` needs no `log` branch | transporting `BddAbove` through `exp` (the strip is not compact, the annulus is) |
| 4 | Harnack inequality (§5) | days–a week | **Yes** — sharp kernel bounds are already theorems at `Poisson.lean:101,134` | the open/closed `DiffContOnCl` mismatch; pattern copyable from `MeanValue.lean:30–36` |
| 5 | Order/type of an entire function (§1) | days for the `Prop` layer; **open** for the numeric bridge | **Partly** — definitions and the four cheap lemmas yes; `growthOrder_le_of_hasGrowthOrderLE` **no** | the `log log` limsup asymptotic; no assembled lemma exists |
| 6 | Argument principle, **Form A** (§7.1) | weeks | **Mostly** — one trivial missing lemma, plus a real bridge | codiscrete agreement ⇒ pointwise `deriv f / f` on the sphere |
| 7 | Weierstrass factors + canonical product (§2) | weeks–months | **No** — needs `HasProdLocallyUniformlyOn.mul_compl`, absent | that lemma, and the `analyticOrderAt` computation it enables (**not** the estimate) |
| 8 | Argument principle, **Form B** (§7.2) | months, multi-PR | **No** — π₁(S¹)≅ℤ, homology Cauchy, cycles, continuous-homotopy invariance all absent | Cauchy's theorem for null-homologous cycles |
| — | Complex Stirling / Γ norm bound (§8) | months, no near-miss | **No**, and nothing to reduce to | a complex Binet/Stirling development from scratch |

A free-standing freebie, worth recording separately because it is smaller than anything
in the table: **`circleIntegral.integral_sub_inv_of_notMem_closedBall`**. Mathlib's own
docstring (`CircleIntegral.lean:50–56`) flags this case as missing and defers it until
Cauchy's theorem exists. It now does (`CauchyIntegral.lean:459`), so this is a few-line
addition closing a gap the library itself documents — independent of whether any of §1–§8
is pursued.

---

## 10. Verification log

Everything in this note was checked against the pinned tree. Recording both outcomes.

**Passed (locator exists, name and shape as stated):** `analyticOrderAt` `Order.lean:47`;
`analyticOrderNatAt` `:61`; `sSupNormIm` `Hadamard.lean:77`;
`norm_le_interp_of_mem_verticalClosedStrip'` `Hadamard.lean:607`; `Filter.limsup`
`LiminfLimsup.lean:64`; `EReal` `Data/EReal/Basic.lean:35`; `expGrowthSup`/`expGrowthInf`
`ExpGrowth.lean:41`/`:38`; `rpow_le_rpow` `Pow/Real.lean:546`;
`rpow_le_rpow_of_exponent_le` `:613`; `norm_cpow_eq_rpow_re_of_pos` `:337`;
`Complex.norm_exp` `Trigonometric.lean:995`; `re_le_norm` `Norm.lean:43`;
`norm_exp_sub_one_le` `Exponential.lean:439`; `HasProdUniformlyOn` `UniformOn.lean:44`;
`HasProdLocallyUniformlyOn` `:152`; `MultipliableLocallyUniformlyOn` `:159`;
`Summable.hasProdUniformlyOn_one_add` `MultipliableUniformlyOn.lean:87`;
`Summable.hasProdLocallyUniformlyOn_one_add` `:130`;
`TendstoLocallyUniformlyOn.differentiableOn` `LocallyUniformLimit.lean:135`;
`Complex.multipliable_one_add_of_summable` `Log/Summable.lean:49`;
`tprod_one_add_ne_zero_of_summable` `:216`; `poissonKernel` `Poisson.lean:54`;
`poissonKernel_eq_re_herglotzRieszKernel` `:73`; `re_herglotzRieszKernel_le` `:101`;
`le_re_herglotzRieszKernel` `:134`; `circleAverage_poissonKernel_smul` `:245`;
`exists_analyticOnNhd_ball_re_eq` `Harmonic/Analytic.lean:70`;
`HarmonicOnNhd.circleAverage_eq` `MeanValue.lean:27`; `circleAverage` `CircleAverage.lean:54`;
`circleAverage_mono` `:271`; `circleAverage_comp_comm` `:318`;
`norm_iteratedDeriv_le_of_forall_mem_sphere_norm_le` `Liouville.lean:44`;
`exists_eq_const_of_bounded` `:128`; `mellin` `MellinTransform.lean:91`;
`MellinConvergent` `:45`; `norm_integral_le_integral_norm` `Bochner/Basic.lean:924`;
`norm_integral_le_of_norm_le` `:937`; `hasSum_taylorSeries_of_entire` `TaylorSeries.lean:129`;
`div_tendsto_atTop_zero_of_degree_lt` `Polynomial/Basic.lean:161`;
`integral_sub_inv_of_mem_ball` `CircleIntegral.lean:699`;
`circleIntegral_congr_codiscreteWithin` `:430`;
`DiffContOnCl.circleIntegral_eq_zero` `CauchyIntegral.lean:459`;
`divisor_ball_support_finite` `Divisor.lean:104`; `extract_zeros_poles`
`FactorizedRational.lean:291`; `circleAverage_log_norm` `JensenFormula.lean:307`;
`sum_divisor_le` `:389`; `logDeriv_prod` `LogDeriv.lean:73`;
`isAddQuotientCoveringMap_exp` `CoveringMap.lean:29`;
`characteristic` `ValueDistribution/CharacteristicFunction.lean:53`;
`borelCaratheodory` `BorelCaratheodory.lean:109`.

**Corrections to earlier scouting** — recorded because an earlier round was caught
asserting "all ingredients pinned" without checking, and these are exactly the kind of
error that produces:

1. `Complex.logTaylor` is at `LogBounds.lean:68` and is a **plain `def`**, not
   `noncomputable def` as an earlier note wrote.
2. `norm_log_sub_logTaylor_le` (`:142`) and `norm_log_one_sub_inv_add_logTaylor_neg_le`
   (`:231`) are **`lemma`s**, not `theorem`s. An earlier note gave `:142`/`:231` correctly
   but the wrong keyword.
3. `HarmonicOnNhd` lives in **`namespace InnerProductSpace`**
   (`InnerProductSpace/Harmonic/Basic.lean:27`, def at `:46`). The proposed Harnack
   theorem's full name is `InnerProductSpace.HarmonicOnNhd.harnack`; earlier scouting
   wrote `HarmonicOnNhd.harnack`, which reads correctly only under `open InnerProductSpace`.
4. The three-lines theorem's full name carries a sub-namespace:
   `Complex.HadamardThreeLines.norm_le_interp_of_mem_verticalClosedStrip'`
   (`namespace Complex` at `Hadamard.lean:66`, `namespace HadamardThreeLines` at `:67`).
   Earlier scouting dropped `HadamardThreeLines`.

None of these four changes any difficulty assessment. They are recorded so the next
reader does not inherit them.

**Not verified, and stated as such:** nothing in this note was elaborated. No proposed
statement is known to typecheck, and no proof sketch is known to close. Where a section
says "all ingredients pinned", it means *every named declaration exists in the tree with
the stated signature text* — it does **not** mean the assembly works.

---

## 11. The strategic choice — both sides, stated at equal strength

This section deliberately does **not** recommend an option.

### 11.1 The case for doing upstream work from this repository

- **It is the only kind of work that is unambiguously available.** The decision substrate
  selects no route. Route-dependent work is therefore blocked by construction, whereas a
  generic theorem about entire functions is blocked by nothing.
- **It is route-neutral, so it cannot be wasted by a later route decision.** Whichever
  route is eventually selected — or if none ever is — a proved Hadamard three-circles
  theorem is still a proved Hadamard three-circles theorem. Nothing in §1–§8 becomes dead
  weight when the substrate changes.
- **It cannot corrupt the invariant.** These are statements about arbitrary functions.
  There is no way for a generic complex-analysis lemma to smuggle in an assumption about
  zeta, and no way for it to make a barrier look closed.
- **Several items are genuinely cheap, and the cheapness is verified rather than hoped.**
  §6 is three located steps. §4's engine is already `n`-indexed at `Liouville.lean:44`.
  §5's sharp kernel bound is already two theorems. §3 is a change of variables. These are
  reductions to proved results, not new mathematics.
- **The work is externally legible.** A merged Mathlib PR is a durable, third-party-checked
  artifact in a way that a branch in this repository is not.
- **It builds capability that no other activity builds.** Writing four small Mathlib PRs
  teaches the library's conventions, review expectations, and naming discipline — which
  is exactly the skill any eventual route-dependent formalization will need.

### 11.2 The case against — stated as strongly

- **None of it closes a named barrier here.** Not `S1-GLOBAL-ZEROS`, not `S1-GROWTH`, not
  any other. The route-neutrality that makes this work safe is the same property that
  makes it *not progress on the repository's stated problem*. Every hour spent here is an
  hour not spent on the thing this repository exists for. That trade is real and should
  not be softened.
- **The timeline is outside our control.** Mathlib review is done by volunteers on their
  own schedule. A small PR can sit for weeks; a design-bearing one (a new `def` like
  `growthOrder` or `weierstrassFactor`) can sit for months while naming, generality, and
  file placement are negotiated. There is no mechanism by which this repository can
  accelerate that, and no fallback if it stalls.
- **Maintainers may reject the design outright.** Every §1–§8 signature embeds choices —
  `EReal` vs `ℝ≥0∞`, `(1 + ‖z‖)` vs `‖z‖`, `Prop` layer vs numeric layer, `Path` vs
  `C(I, ℂ)`, whether `zeroCount` should exist at all — and a maintainer is entitled to
  ask for a different one. That can invalidate not just the proofs but the statements,
  and the work does not transfer.
- **The estimates are cheap; the assembly is not, and the assembly is unverified.** No
  Lean toolchain exists in this environment. Every "all ingredients pinned" verdict above
  means *the declarations exist as text*, and nothing more. The gap between "the lemma
  exists" and "the `simp` set closes the goal" is where formalization time actually goes,
  and this note cannot measure it. The §2 experience is the warning: the classically hard
  estimate is nearly free, and the boring bookkeeping (`mul_compl`) is the blocker.
- **Some items are far more expensive than their one-line description suggests.** §7 Form
  B and §8 are each multi-month projects. If either is started under the impression that
  it is a task, the cost will be discovered late.
- **It creates a maintenance surface with an external owner.** Once a definition of
  `Complex.growthOrder` is upstream, its name, shape, and API are Mathlib's to change.
  Downstream code here would then track an interface we do not control.
- **A weak but honest version of the strongest objection:** doing safe, legible,
  route-neutral work is exactly what an agent does when the real problem is blocked. That
  it is safe is not evidence that it is the right use of the next unit of effort. The
  alternative — doing nothing on RH until a route is selected, and spending effort on the
  selection itself — is a coherent position and should not be dismissed because it
  produces no artifact.

### 11.3 The shape of the choice

Roughly four options, laid out without a preference:

1. **Do nothing upstream.** Accept that RH work is blocked pending a route decision, and
   spend effort on the decision substrate itself.
2. **Do only the freebie.** `circleIntegral.integral_sub_inv_of_notMem_closedBall` — a
   gap Mathlib's own docstring flags, a few lines, no design questions. Minimal cost,
   minimal claim, tests the upstream process end to end.
3. **Do the cheap reductions (§3, §4, §5, §6).** Four independent PRs, each a reduction to
   something already proved, each with all named ingredients located. No new definitions,
   so the design-rejection risk is lowest. This is the largest option that stays inside
   "verified reduction" and out of "new mathematics".
4. **Commit to the definitional layer (§1, then §2).** Higher value if it lands, higher
   risk: new `def`s invite design negotiation, and §2 is blocked on a lemma
   (`HasProdLocallyUniformlyOn.mul_compl`) that does not exist yet.

§7 Form B and §8 are out of scope for any of these as scoped here.

Whichever is chosen, the constraints in the header hold: no proof is asserted, no barrier
is closed, no route is selected or unparked, and nothing here bears on the Riemann
Hypothesis.
## Provenance correction (2026-08-07)

An independent re-verification of the capability map
(`notes/reviews/CAPABILITY_MAP_REVERIFICATION_2026_08_07.md`) found two defects
in this note and they are corrected here rather than left standing.

1. **Three locators were off by two lines.** At the pin,
   `Complex.HadamardThreeLines.verticalStrip` is `Hadamard.lean:70`,
   `verticalClosedStrip` is `:73`, and
   `norm_le_interpStrip_of_mem_verticalClosedStrip` is `:588`. The values first
   written here (`:68`, `:71`, `:590`) were wrong; `sSupNormIm` `:77` and
   `norm_le_interp_of_mem_verticalClosedStrip'` `:607` were correct.

2. **This note re-cited pinned ingredients as if freshly located, without
   referencing the capability map, which already records six of them.** That is
   the same defect class the lane has been caught on before — presenting
   existing inventory as a new find. This note claims no discovery: it is a
   design note over ingredients, wherever they were first recorded, and the
   capability map remains the lane inventory of record.

Neither correction changes a difficulty verdict or a signature. The absences
this note relies on were independently re-derived and all survived.
