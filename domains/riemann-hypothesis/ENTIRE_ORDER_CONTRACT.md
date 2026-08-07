# RH growth-order definition contract (S1-GROWTH, definitional pillar): DRAFT v1

Status: **DRAFT v1 (2026-08-07) — non-built review artifact, offered for STAGE ONE
(INDEPENDENT CONTRACT ACCEPTANCE) ONLY. NOT Lean-checked.** No declaration below
has been elaborated; no `lake build` has been run against any of it. Under the one
invariant, the Lean kernel via CI is the sole judge of every statement in this
contract, and this document carries no kernel verdict of any kind.

**This contract closes no barrier, selects no route, and makes no claim about the
truth of the Riemann Hypothesis.**

**Honesty constraint, stated up front and repeated in the claim boundary:
`S1-GROWTH` is NOT closed and NOT advanced by definitions alone.** The
`S1-GROWTH` row (repo:`MATHLIB_CAPABILITY_MAP.md:388`) reads "no zeta/xi
vertical or order-one growth theorem", with exit evidence "explicit
quantitative bounds sufficient for the selected theorem". A definition
produces zero quantitative bounds. What a definition IS, uniquely in this
lane, is **design-bearing**: this is the one pillar of the RH program for
which **no notion exists at the pin at all** (absence re-verified this
session, §Absence audit below), so every future growth theorem will be stated
*about this object*. Get the definition wrong and every downstream theorem is
stated about the wrong object — which is exactly why it is offered for
independent review **before** anything is built on it. **The repo will not
build downstream growth theorems on this definition before the definition
itself passes independent stage-one acceptance.** That commitment is a death
condition (§Death conditions, condition 1 — the design-bearing acceptance
gate), not a preference.

**Two-stage gate (same discipline as `MULTIPLICITY_CONTRACT.md`).** Stage one
is *independent contract acceptance*: a review of the statement surface G0–G2,
L1–L6 only. It produces **no built module, no ledger row, no registry or
axiom-audit entry, and no kernel verdict**. Stage two is a **separate built
promotion PR** whose verdict is delivered by CI. An acceptance PR must not
carry a promotion. Any drafts-lane file for this surface (working name
`drafts/RiemannGrowthOrder.lean`) lies outside every lake target
(`lakefile.toml:2` declares `defaultTargets = ["Ecdlp", "ResearchOS"]`), so
**no green CI run on an acceptance PR is evidence of anything about the
draft.**

**Ordering / authority.** The authority for this lane is the RH queue,
repo:`tasks/RIEMANN_HYPOTHESIS.md`; no route execution is authorized, and
this document is an offered artifact, not an active task.
`repo/ECDLP_DECISION_SUBSTRATE.json` governs the ECDLP lane and is not the
authority here. `repo/FINAL_REVIEW_PACKET.md` is frozen to draft PR #235 and
is not reused by this document.

Working name: `GrowthOrder.lean` (eventual module
`ResearchOS.AnalyticNumberTheory.RiemannHypothesis.GrowthOrder`; drafts lane
first). Statement surface: **G0–G2 (three definitions) and L1–L6 (six
lemmas), comprising exactly 9 public signatures**, every one spelled
explicitly in a `lean` block in §2. No signature is mandated in prose only.

Scope: the definitional prerequisite of the `S1-GROWTH` barrier only. This
contract contains **no** growth theorem about ζ or ξ, **no** Hadamard
factorization, **no** Jensen/counting input, **no** zero enumeration, and
**no** claim of progress on RH. It deliberately does not mention `riemannXi`
or `riemannZeta` in any signature: the definition must be accepted as a
*generic* object before it is ever applied to ξ.

Pinned Mathlib: `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0),
toolchain `leanprover/lean4:v4.31.0`, verified this session via
`git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD`. Every
`file:line` locator below is from that exact tree (paths relative to the
`Mathlib/` root of the pin) unless prefixed `repo:`. Every locator was
verified by direct source reading this session; **nothing was elaborated** —
source reading only, no Lean toolchain in this environment.

Grounding note: `UPSTREAM_POOL.md` §1 (scout A) proposed a limsup-based
definition with `EReal` codomain. This contract **re-derives the definition
independently** and *diverges from scout A in two load-bearing places* (§1:
codomain `ℝ≥0∞` instead of `EReal`; an inner clamp `max … 1` that scout A's
formula omits and without which two of the six lemmas below are **false**).
The divergences are argued, not asserted; a reviewer who rejects them rejects
the whole surface, which is the point of stage one.

---

## Absence audit (why this is the definitional pillar)

Re-verified this session at the pin, source reading only:

| Probe | Command shape | Result |
|---|---|---|
| Any growth-order notion | `grep -rn "growthOrder\|GrowthOrder" Mathlib/` | **0 hits** |
| Any "order of growth" docstring | `grep -rci "order of growth" Mathlib/Analysis/Complex/*.lean` | **0 hits** |
| Any `def order` in complex analysis | `grep -rn "def order" Mathlib/Analysis/Complex/` | **0 hits** |
| Hadamard factorization / canonical product | `grep -rn "Hadamard factorization\|canonical product" Mathlib/ --include=*.lean` | 1 hit, category theory (`CategoryTheory/Limits/Sifted.lean:185`), unrelated |

Namespace hazard (carried over from `UPSTREAM_POOL.md` §Namespace hazard, and
honored here): `analyticOrderAt` (`Analysis/Analytic/Order.lean:47`) is the
**vanishing order at a point**, not a growth order;
`Analysis/Complex/Order.lean` is the partial order on `ℂ`. The definition
below is therefore named `growthOrder`, never `Complex.order`, and this
contract never uses the bare word "order" in a signature.

Name-collision scan run at the pin this session: `maxModulus`, `growthOrder`,
`growthType`, `growthOrder_const`, `growthOrder_polynomial`, `growthOrder_exp`,
`growthOrder_le_of_eventually_le`, `growthOrder_mul_le`, `growthType_exp` —
**zero hits for all**.

---

## 0. Exact pinned interface (quoted from the tree at the pin)

```lean
-- Order/LiminfLimsup.lean:64 — limsup is sInf of eventual upper bounds; total in a
-- CompleteLinearOrder, side-conditioned in a ConditionallyCompleteLattice.
def limsup (u : β → α) (f : Filter β) : α := limsSup (map u f)

-- Order/LiminfLimsup.lean:198 — the comparison workhorse. In a COMPLETE lattice the
-- two side conditions are discharged by the `isBoundedDefault` autoParam; in ℝ they are NOT.
theorem limsup_le_limsup [ConditionallyCompleteLattice β] (h : u ≤ᶠ[f] v)
    (hu : f.IsCoboundedUnder (· ≤ ·) u := by isBoundedDefault)
    (hv : f.IsBoundedUnder (· ≤ ·) v := by isBoundedDefault) : limsup u f ≤ limsup v f

-- Order/LiminfLimsup.lean:265 (limsup_congr), :284 (limsup_const, needs [NeBot f]),
-- :1141 (limsup_max — four isBoundedDefault autoParams, all free in a complete lattice):
theorem limsup_max [ConditionallyCompleteLinearOrder β] … :
    limsup (fun a ↦ max (u a) (v a)) f = max (limsup u f) (limsup v f)

-- Data/ENNReal/Basic.lean:152 — limsup in ℝ≥0∞ is total, no side goals ever:
noncomputable instance : CompleteLinearOrder ℝ≥0∞

-- Data/ENNReal/Basic.lean:224, :291; Data/ENNReal/Real.lean:137, :181 — the outer clamp:
protected def ofReal (r : Real) : ℝ≥0∞ := r.toNNReal
@[simp] theorem ofReal_one : ENNReal.ofReal (1 : ℝ) = (1 : ℝ≥0∞)
theorem ofReal_le_ofReal {p q : ℝ} (h : p ≤ q) : ENNReal.ofReal p ≤ ENNReal.ofReal q
theorem ofReal_eq_zero {p : ℝ} : ENNReal.ofReal p = 0 ↔ p ≤ 0

-- Topology/Instances/ENNReal/Lemmas.lean:70 (namespace ENNReal), :817:
theorem continuous_ofReal : Continuous ENNReal.ofReal
lemma limsup_mul_le' (h : limsup u f ≠ 0 ∨ limsup v f ≠ ∞)
    (h' : limsup u f ≠ ∞ ∨ limsup v f ≠ 0) : limsup (u * v) f ≤ limsup u f * limsup v f

-- Order/Filter/ENNReal.lean:231 — TRAP, recorded so nobody reaches for it: this
-- requires [CountableInterFilter f], which `atTop : Filter ℝ` does NOT satisfy.
theorem limsup_add_le [CountableInterFilter f] (u v : α → ℝ≥0∞) :
    limsup (u + v) f ≤ limsup u f + limsup v f

-- Analysis/SpecialFunctions/Log/Basic.lean:44 — THE junk convention that drives the
-- whole design. Real.log x = log |x| for x < 0 (NOT 0), and log 0 = 0:
noncomputable def log (x : ℝ) : ℝ :=
  if hx : x = 0 then 0 else expOrderIso.symm ⟨|x|, abs_pos.2 hx⟩
theorem log_neg_eq_log (x : ℝ) : log (-x) = log x        -- :120 (the |·| behavior)
theorem log_exp (x : ℝ) : log (exp x) = x                -- :74
theorem log_zero : log 0 = 0                             -- :102
lemma log_le_log (hx : 0 < x) (hxy : x ≤ y) : log x ≤ log y   -- :150 (positivity REQUIRED)
theorem log_pos (hx : 1 < x) : 0 < log x                 -- :187
theorem log_nonneg (hx : 1 ≤ x) : 0 ≤ log x              -- :212
theorem log_nonpos (hx : 0 ≤ x) (h'x : x ≤ 1) : log x ≤ 0  -- :221
theorem tendsto_log_atTop : Tendsto log atTop atTop      -- :350
theorem isLittleO_log_id_atTop : log =o[atTop] id        -- :449

-- Analysis/Complex/Hadamard.lean:77 — the sup-carrier precedent this contract copies
-- (bare real sSup of a norm image, positivity supplied separately at :99):
noncomputable def sSupNormIm {E : Type*} [NormedAddCommGroup E] (f : ℂ → E) (x : ℝ) : ℝ :=
  sSup ((norm ∘ f) '' re ⁻¹' {x})

-- Real sSup junk values (make maxModulus total):
-- Algebra/Order/Archimedean/Real/Basic.lean:171, :189, :294
theorem sSup_empty : sSup (∅ : Set ℝ) = 0
lemma sSup_of_not_bddAbove (hs : ¬BddAbove s) : sSup s = 0
lemma sSup_nonneg (hs : ∀ x ∈ s, 0 ≤ x) : 0 ≤ sSup s

-- Order/ConditionallyCompleteLattice/Basic.lean:198, :202;
-- Order/ConditionallyCompletePartialOrder/Basic.lean:72, :120
theorem le_csSup (h₁ : BddAbove s) (h₂ : a ∈ s) : a ≤ sSup s
theorem csSup_le (h₁ : s.Nonempty) (h₂ : ∀ b ∈ s, b ≤ a) : sSup s ≤ a
theorem IsGreatest.csSup_eq (H : IsGreatest s a) : sSup s = a
theorem csSup_singleton (a : α) : sSup {a} = a

-- The exp test ingredients:
theorem norm_exp (z : ℂ) : ‖exp z‖ = Real.exp z.re   -- Analysis/Complex/Trigonometric.lean:995
theorem re_le_norm (z : ℂ) : z.re ≤ ‖z‖              -- Analysis/Complex/Norm.lean:43
protected theorem norm_of_nonneg {r : ℝ} (h : 0 ≤ r) : ‖(r : ℂ)‖ = r   -- Norm.lean:106
theorem one_le_exp {x : ℝ} (hx : 0 ≤ x) : 1 ≤ exp x  -- Analysis/Complex/Exponential.lean:279
theorem exp_le_exp {x y : ℝ} : exp x ≤ exp y ↔ x ≤ y -- Analysis/Complex/Exponential.lean:315

-- The polynomial test ingredient (namespace Polynomial, section variables at :341:
-- {R : Type*} [NormedRing R] [NormMulClass R] — ℂ qualifies):
theorem isBigO_cobounded_of_degree_le (h : P.degree ≤ Q.degree) :
    P.eval =O[cobounded R] Q.eval                     -- Analysis/Polynomial/Basic.lean:362

-- Compactness route for the mul lemma:
theorem isCompact_sphere [ProperSpace α] (x : α) (r : ℝ) : …  -- Topology/MetricSpace/ProperSpace.lean:45
theorem IsCompact.bddAbove [ClosedIciTopology α] … : BddAbove s  -- Topology/Order/Compact.lean:322
theorem NormedSpace.sphere_nonempty {x : E} {r : ℝ} : (sphere x r).Nonempty ↔ 0 ≤ r
                                                  -- Analysis/Normed/Module/RCLike/Real.lean:128

-- rpow (used only in growthType): Analysis/SpecialFunctions/Pow/Real.lean:35 (def rpow),
-- :38 (noncomputable instance : Pow ℝ ℝ), :148 (rpow_one)

-- Convergence closers:
theorem Filter.Tendsto.limsup_eq [NeBot f] … : Tendsto u f (𝓝 a) → limsup u f = a
                                                  -- Topology/Order/LiminfLimsup.lean:191
lemma Filter.Tendsto.const_div_atTop (hg : Tendsto g l atTop) (r : 𝕜) : …
                                                  -- Topology/Algebra/Order/Field.lean:222

-- The design precedent scout A cited, quoted for the codomain comparison (§1):
-- Analysis/Asymptotics/ExpGrowth.lean:38, :41 — codomain EReal, over sequences ℕ → ℝ≥0∞:
noncomputable def expGrowthSup (u : ℕ → ℝ≥0∞) : EReal := limsup (fun n ↦ log (u n) / n) atTop
-- EReal := WithBot (WithTop ℝ), deriving CompleteLinearOrder — Data/EReal/Basic.lean:35
-- ENNReal.log : ℝ≥0∞ → EReal — Analysis/SpecialFunctions/Log/ENNRealLog.lean:46
```

---

## 1. Codomain decision

### Decision: **`ℝ≥0∞` (ENNReal), reached by an `ENNReal.ofReal` clamp on a real
quotient, with an inner clamp `max (maxModulus f r) 1` under the double log.
The API supports it — verified at the pin, table below.**

The task brief said "ENNReal recommended if the API supports it — verify". It
was verified, it supports it, and the recommendation is adopted — but the
verification also surfaced a defect in the *raw* limsup formula (scout A's and
the textbook's alike) that no codomain fixes on its own. Both halves are
argued here.

### 1.1 The junk-value analysis that forces the design (read this first)

The classical formula is `order f = limsup_{r→∞} log log M(f,r) / log r`. Its
degenerate cases must be handled by *stated* conventions, and — per this
contract's brief — **symmetrically**, so that downstream equalities are
honest. At the pin the degenerate cases are worse than "bounded f" and
"f = 0", because of one Mathlib fact:

> **`Real.log x = log |x|` for `x < 0`** (Log/Basic.lean:44, junk documented
> in the def's docstring; `log_neg_eq_log` at :120). The junk value on the
> negatives is NOT `0`.

Consequence, computed exactly:

- **Spurious positive order.** Take any `f` with `maxModulus f r = exp (-r)`
  (fast decay; not entire, but the definition is total over all `f : ℂ → E`).
  Then `log M = -r`, and `Real.log (-r) = Real.log r`, so the raw quotient is
  `log r / log r = 1`. The raw formula assigns **order 1** to a function whose
  modulus decays like `e^{-r}`. This is not a negative-junk leak that an
  `EReal`/`ENNReal` choice could absorb — it is a spurious **positive** value.
- **Monotonicity failure.** With `maxModulus f r = exp (-r) ≤ 1/2 = maxModulus g r`
  eventually, the raw formula gives `order f = 1 > 0 = order g`. So the
  comparison lemma (L4, one of the lemmas this contract is required to make
  true) is **false** for the raw formula in every codomain.

Fix: clamp **inside**, before the double log. Replace `maxModulus f r` by
`max (maxModulus f r) 1` in the definition. Then:

- the inner `Real.log` argument is `≥ 1`, so it never touches the `log |x|`
  junk region and the inner log is `≥ 0` (`log_nonneg`, :212);
- the outer `Real.log` argument is `≥ 0`; its residual junk (`log 0 = 0`,
  negative values on `(0,1)`) is nonpositive-or-zero and is absorbed by the
  outer `ENNReal.ofReal` clamp (`ofReal_eq_zero`, Real.lean:181);
- for the intended class — nonconstant entire `f` — `maxModulus f r → ∞`
  (maximum-modulus/Liouville; a true fact NOT used and NOT needed by any
  statement below), so the clamp is eventually inactive and the value agrees
  with the textbook order. For bounded `f` the clamped order is `0`, which IS
  the textbook convention.

**Symmetry (contract requirement):** the *same two clamps in the same order* —
inner `max … 1`, outer `ENNReal.ofReal` — appear in `growthOrder` (G1) and
`growthType` (G2). No definition in this surface applies one clamp without
the other. Downstream equalities between order-statements and type-statements
therefore compare objects with identical degenerate-case conventions.

### 1.2 Why `ℝ≥0∞` and not `EReal` (scout A) or `ℝ`

1. **The mathematical value set is `[0, ∞]`.** Every textbook order is
   nonnegative, and `∞` is a genuine value (e.g. `exp ∘ exp`). `ℝ≥0∞` encodes
   both facts in the type: downstream statements like `growthOrder f ≤ 1`
   never need a separate `0 ≤ growthOrder f` companion lemma, and
   `le_max_iff`-style reasoning stays in one order. In `EReal`, every consumer
   inherits a `⊥`/negative-values proof obligation that the object never
   honestly takes once the §1.1 clamps are in place — and *without* the
   clamps, negative and spuriously-positive values both really occur, which is
   the §1.1 defect. `EReal`'s extra expressiveness below `0` buys nothing but
   dead cases.
2. **The limsup API in `ℝ≥0∞` is at least as strong as in `EReal` at the pin —
   verified:**

   | Needed | `ℝ≥0∞` at the pin | `EReal` at the pin |
   |---|---|---|
   | total `limsup`, no side goals | ✓ `CompleteLinearOrder` (Data/ENNReal/Basic.lean:152) | ✓ (Data/EReal/Basic.lean:35, derived) |
   | `limsup_le_limsup` autoParams discharge | ✓ complete lattice, `isBoundedDefault` free (Order/LiminfLimsup.lean:198) | ✓ same |
   | `limsup_max` (for L5) | ✓ :1141, autoParams free | ✓ same |
   | `limsup_congr`/`limsup_const` (for L1/L3/L6) | ✓ :265/:284 | ✓ same |
   | product bound | ✓ `ENNReal.limsup_mul_le'` (Topology/Instances/ENNReal/Lemmas.lean:817), usable at `atTop` | `EReal.limsup_add_le` (Topology/Instances/EReal/Lemmas.lean:265) — additive, needs `⊥/⊤` disjunctions |
   | order-topology closers (`Tendsto.limsup_eq`) | ✓ Topology/Order/LiminfLimsup.lean:191 applies | ✓ same |

   One trap found and recorded: `ENNReal.limsup_add_le`
   (Order/Filter/ENNReal.lean:231) requires `[CountableInterFilter f]`, which
   `atTop : Filter ℝ` does **not** satisfy. No skeleton below uses it; L5's
   obligation register names the workaround.
3. **`ℝ` is rejected outright**: `limsup` over `ℝ` is the conditionally
   complete one — every use drags `IsBoundedUnder`/`IsCoboundedUnder` side
   goals, and infinite order is unrepresentable (junk `sSup ∅ = 0` would
   conflate `exp ∘ exp` with a constant). Scout A already rejected `ℝ` for the
   same reason; re-derived and confirmed.
4. **Why not an `ℝ≥0∞`-native carrier** (`⨆ z ∈ sphere, ‖f z‖ₑ` with
   `ENNReal.log`): `ENNReal.log` exists at the pin but is valued in `EReal`
   (Log/ENNRealLog.lean:46), so the double-log chain would still leave
   `ℝ≥0∞`, adding an `EReal` middle layer and two coercion seams for zero
   benefit. The real-valued `sSup` carrier also matches the only in-tree sup
   precedent, `sSupNormIm` (Hadamard.lean:77), which any future Hadamard
   three-lines work will consume — keeping the carriers aligned avoids a
   future bridging lemma. Recorded as the road not taken, **DEFERRED-G1**.
5. **Divergence from the `expGrowthSup` precedent is deliberate and argued.**
   `expGrowthSup` (ExpGrowth.lean:41) uses `EReal` because exponential growth
   of an arbitrary `ℕ → ℝ≥0∞` sequence genuinely takes negative values
   (decay rates) and `⊥`. The growth order of an entire function does not:
   its honest value set is `[0,∞]`. Copying the precedent's codomain without
   copying its semantics would import dead cases; this is exactly the kind of
   silent design transfer stage-one review exists to catch.

### 1.3 The riskiest design choice, named for the reviewer

**The inner clamp `max (maxModulus f r) 1` is the riskiest choice in this
contract.** It deviates from the raw textbook formula, from scout A's
proposal, and from the `expGrowthSup` shape. It is forced by pinned-Mathlib
junk semantics (§1.1), it is what makes L4 true and L1–L3 clamp-stable, and
on nonconstant entire functions it is invisible. But if a reviewer rejects it
(e.g. prefers restricting by hypothesis instead of totalizing by clamp), then
**G1, G2 and all six lemmas change shape**, and any Mathlib-upstream ambition
would need the upstream community's own convention call. This is precisely
why nothing may be built downstream before acceptance. A secondary risk:
`growthType`'s exponent lives in `ℝ` via `rpow` (Pow/Real.lean:35/:38), whose
own junk at negative bases is documented in G2 and gated by `atTop`.

---

## 2. Statement surface G0–G2, L1–L6

Proposed preamble (name-resolution review only):

```lean
import Mathlib.Analysis.Complex.Trigonometric      -- Complex.norm_exp
import Mathlib.Analysis.Polynomial.Basic           -- Polynomial.isBigO_cobounded_of_degree_le
import Mathlib.Analysis.SpecialFunctions.Pow.Real  -- rpow for growthType
import Mathlib.Topology.Instances.ENNReal.Lemmas   -- ENNReal limsup API, continuous_ofReal
import Mathlib.Analysis.Complex.Hadamard           -- sSupNormIm precedent (comment-cited only)

open Filter Metric
open scoped ENNReal Topology

namespace Complex
variable {E : Type*} [NormedAddCommGroup E]
```

Tags: `[PIN]` provable from pinned Mathlib alone; `[GEN]` generic, natural
Mathlib upstream (every statement here is `[GEN]` — none mentions a repo
symbol); `[ASM]` the statement is cheap but its proof needs an **unassembled**
limsup asymptotic — pieces pinned, no assembled lemma exists, honest
obligation HIGH.

---

### G0. The maximum-modulus carrier `[GEN]` `[PIN]`

```lean
/-- `M(f, r) = sup {‖f z‖ : ‖z‖ = r}`, as a bare real `sSup` in the style of
`Complex.HadamardThreeLines.sSupNormIm` (Hadamard.lean:77). Total: junk value `0`
when the sphere is empty (`r < 0`, `Real.sSup_empty`) or the image is unbounded
(`Real.sSup_of_not_bddAbove`); nonnegative always (`Real.sSup_nonneg` — norms). -/
noncomputable def maxModulus (f : ℂ → E) (r : ℝ) : ℝ :=
  sSup ((norm ∘ f) '' Metric.sphere (0 : ℂ) r)
```

Pinned dependencies (G0): `sSupNormIm` precedent Hadamard.lean:77 (shape
copied verbatim, sphere for line); `Real.sSup_empty`
Algebra/Order/Archimedean/Real/Basic.lean:171; `Real.sSup_of_not_bddAbove`
:189; `Real.sSup_nonneg` :294; `NormedSpace.sphere_nonempty`
Analysis/Normed/Module/RCLike/Real.lean:128 (nonempty iff `0 ≤ r`).

Design note: sphere, not closed ball. For continuous `f` on a compact sphere
the sup is attained (isCompact_sphere ProperSpace.lean:45 +
IsCompact.bddAbove Topology/Order/Compact.lean:322); the sphere/ball
distinction matters only through the maximum-modulus principle, which is a
*theorem about entire functions*, not part of the definition. Choosing the
sphere keeps G0 hypothesis-free and matches the classical `M(r)`.

Obligations (G0): **S1G-0** (LOW) — none beyond elaboration; the junk values
are the documented ones.

---

### G1. The growth order `[GEN]` `[PIN]` — THE definition under review

```lean
/-- The growth order of `f : ℂ → E`, valued in `ℝ≥0∞`:
`limsup_{r→∞} log log (max (M(f,r)) 1) / log r`, clamped into `[0,∞]`.

Degenerate-case conventions, stated exactly and shared verbatim with `growthType`:
* inner clamp `max … 1`: the argument of the inner `Real.log` is `≥ 1`, so the
  `Real.log = log |·|` junk on negatives (Log/Basic.lean:44) is never reached and
  the inner log is `≥ 0`; without this clamp a modulus decaying like `exp (-r)`
  would receive order 1 (see contract §1.1);
* outer clamp `ENNReal.ofReal`: transient negative quotients (outer log of a value
  in `[0,1)`, i.e. `1 ≤ M(f,r) ≤ e`) collapse to `0`;
* consequences: `growthOrder f = 0` for `f = 0`, for constants, and for every `f`
  with `maxModulus f · ≤ 1` eventually — the textbook convention for bounded
  entire functions;
* for nonconstant entire `f` the clamps are eventually inactive and the value is
  the classical order. That fact is NOT asserted by this definition and no lemma
  below depends on it. -/
noncomputable def growthOrder (f : ℂ → E) : ℝ≥0∞ :=
  Filter.limsup
    (fun r : ℝ =>
      ENNReal.ofReal (Real.log (Real.log (max (maxModulus f r) 1)) / Real.log r))
    Filter.atTop
```

Pinned dependencies (G1): `Filter.limsup` Order/LiminfLimsup.lean:64;
`CompleteLinearOrder ℝ≥0∞` Data/ENNReal/Basic.lean:152 (totality — no
boundedness side goals ever); `ENNReal.ofReal` Data/ENNReal/Basic.lean:224;
`Real.log` Log/Basic.lean:44 with `log_neg_eq_log` :120 (the hazard the inner
clamp neutralizes), `log_zero` :102, `log_nonneg` :212, `log_nonpos` :221.

Obligations (G1): **S1G-1** (LOW) — elaboration only. The design risk is not
an elaboration risk; it is the stage-one review question itself (§1.3).

---

### G2. The growth type, gated on finite positive order `[GEN]` `[PIN]`

```lean
/-- The type of `f` relative to exponent `p`:
`limsup_{r→∞} log (max (M(f,r)) 1) / r ^ p`, with the SAME two clamps as
`growthOrder` (inner `max … 1`, outer `ENNReal.ofReal`) so the degenerate-case
conventions of order and type are identical.

GATE (design-bearing, enforced by documentation and by death condition 6, not by a
hypothesis binder): `growthType f p` is meaningful only when
`0 < p` and `growthOrder f = ENNReal.ofReal p` — i.e. finite positive order. The
definition is total (repo totalization convention; junk documented):
* `p ≤ 0`: junk (the gate excludes it; no lemma below is stated there);
* `r ^ p` is `Real.rpow` (Pow/Real.lean:35, instance :38); its own junk at
  negative bases is invisible under `atTop`;
* bounded `f`, `0 < p`: inner log eventually `0`, so `growthType f p = 0`. -/
noncomputable def growthType (f : ℂ → E) (p : ℝ) : ℝ≥0∞ :=
  Filter.limsup
    (fun r : ℝ => ENNReal.ofReal (Real.log (max (maxModulus f r) 1) / r ^ p))
    Filter.atTop
```

Pinned dependencies (G2): G1's list; `Real.rpow` Pow/Real.lean:35, `instance :
Pow ℝ ℝ` :38, `rpow_one` :148.

Why the gate is documentation + death condition rather than a hypothesis
binder: a `(hp : 0 < p)`-binding `def` would make `growthType` a dependent
function whose equalities carry proof terms, poisoning every downstream `rw`.
The repo's own precedent (`MeromorphicOn.divisor`, Divisor.lean:39 — total,
hypotheses live in the `_apply` lemmas) is followed: total definition,
gated *lemmas*. A reviewer who prefers the binder is making exactly the kind
of call stage one exists for.

Obligations (G2): **S1G-2** (LOW) — elaboration only; `r ^ p` must elaborate
via the `Pow ℝ ℝ` instance (:38), not `Monoid.npow`; if ambiguous, write
`r ^ (p : ℝ)` or `Real.rpow r p` explicitly.

---

### L1. Order of a constant is zero `[GEN]` `[PIN]` — the smoke test

```lean
theorem growthOrder_const (c : E) : growthOrder (fun _ : ℂ => c) = 0
```

Proof skeleton:

```lean
  -- Step 1: for 0 ≤ r, maxModulus (fun _ => c) r = ‖c‖:
  --   image = {‖c‖} on a nonempty sphere (NormedSpace.sphere_nonempty, RCLike/Real.lean:128),
  --   then csSup_singleton (ConditionallyCompletePartialOrder/Basic.lean:120)
  --   [for r < 0 the value is junk 0 — irrelevant under atTop].
  -- Step 2: set K := max ‖c‖ 1 (constant, 1 ≤ K). Two cases:
  --   • Real.log K ≤ 1: then Real.log (Real.log K) ≤ 0 (log_nonpos :221, using
  --     0 ≤ log K from log_nonneg :212), so eventually (log r > 0, log_pos :187 for r > 1)
  --     the quotient is ≤ 0 and ENNReal.ofReal _ = 0 (ofReal_eq_zero, Real.lean:181).
  --     Close with limsup_congr (:265) against 0 and limsup_const (:284).
  --   • 1 < Real.log K: quotient = C / log r with C := log (log K) > 0 fixed;
  --     Tendsto.const_div_atTop (Topology/Algebra/Order/Field.lean:222) with
  --     tendsto_log_atTop (Log/Basic.lean:350) gives quotient → 0;
  --     ENNReal.continuous_ofReal (Topology/Instances/ENNReal/Lemmas.lean:70) pushes to
  --     𝓝 (ofReal 0) = 𝓝 0; close with Filter.Tendsto.limsup_eq
  --     (Topology/Order/LiminfLimsup.lean:191).
```

Pinned dependencies (L1): all cited inline above.

Obligations (L1): **S1G-L1** (MEDIUM): the case split and the
`Tendsto.limsup_eq` closer need the `OrderTopology ℝ≥0∞` instance to be found
by instance search (it is the standard ENNReal topology; not settleable by
source reading alone — CI is the judge). Fallback: replace the tendsto route
by an `∀ ε > 0` eventual-bound argument closed with `limsup_le_iff`.

---

### L2. Order of a polynomial is zero `[GEN]` `[ASM]` — the required test, honestly costed

```lean
theorem growthOrder_polynomial (P : Polynomial ℂ) :
    growthOrder (fun z : ℂ => P.eval z) = 0
```

Proof skeleton:

```lean
  -- Step 1 (pinned): Polynomial.isBigO_cobounded_of_degree_le
  --   (Analysis/Polynomial/Basic.lean:362; section variables :341 — [NormedRing R]
  --   [NormMulClass R], ℂ qualifies) with Q := X ^ P.natDegree gives
  --   ∃ C, ∀ᶠ z in cobounded ℂ, ‖P.eval z‖ ≤ C * ‖z‖ ^ P.natDegree.
  -- Step 2 (pinned): transfer to spheres — cobounded eventual sets contain
  --   {z | R₀ ≤ ‖z‖}; for r ≥ R₀ every z ∈ sphere 0 r qualifies, so
  --   maxModulus (P.eval ·) r ≤ C * r ^ P.natDegree eventually, by csSup_le (:202)
  --   over the nonempty image (sphere_nonempty).
  -- Step 3 (NOT assembled — the named hard step): for every ε > 0, eventually
  --   log (log (max (C * r ^ n) 1)) / log r ≤ ε.
  --   Pieces pinned: Real.log_mul, Real.log_pow / log_rpow, isLittleO_log_id_atTop
  --   (Log/Basic.lean:449), tendsto_log_atTop (:350). NO assembled
  --   "log log (C·r^n) / log r → 0" lemma exists at the pin — this is the same
  --   unassembled asymptotic UPSTREAM_POOL.md §1.3 named as the hardest step of
  --   growthOrder_le_of_hasGrowthOrderLE. Then close through limsup ≤ ε for all ε.
```

Pinned dependencies (L2): Polynomial.isBigO_cobounded_of_degree_le
Analysis/Polynomial/Basic.lean:362 (verified with its section variables at
:341); csSup_le Order/ConditionallyCompleteLattice/Basic.lean:202;
sphere_nonempty RCLike/Real.lean:128; log asymptotics Log/Basic.lean:350/:449.

Obligations (L2): **S1G-L2** (HIGH, honest): Step 3 is an unassembled limsup
asymptotic. The statement is part of the surface because it is the required
testability witness for the definition; its proof cost is NOT claimed cheap,
and stage-two may land L1/L3–L6 first with L2 split into its own PR. If Step 3
resists, the fallback test pair is L1 + L3, and L2 converts to a deferred
item — it must NOT be weakened to `≤ ε` phrasing or to a `natDegree = 0` case.

---

### L3. Order of `exp` is one `[GEN]` `[PIN]` — pinned ingredients SUFFICE

```lean
theorem growthOrder_exp : growthOrder Complex.exp = 1
```

Proof skeleton (complete route; every ingredient pinned, nothing asymptotic):

```lean
  -- Step 1: maxModulus Complex.exp r = Real.exp r for 0 ≤ r, by IsGreatest.csSup_eq
  --   (ConditionallyCompletePartialOrder/Basic.lean:72) applied to
  --   IsGreatest ((norm ∘ exp) '' sphere 0 r) (Real.exp r):
  --   • membership: (r : ℂ) ∈ sphere 0 r  — Complex.norm_of_nonneg (Norm.lean:106);
  --     ‖exp (r : ℂ)‖ = Real.exp r — Complex.norm_exp (Trigonometric.lean:995) +
  --     Complex.ofReal_re (Data/Complex/Basic.lean:88);
  --   • upper bound: ‖exp z‖ = Real.exp z.re ≤ Real.exp ‖z‖ = Real.exp r —
  --     norm_exp again, re_le_norm (Norm.lean:43), Real.exp_le_exp
  --     (Analysis/Complex/Exponential.lean:315), and ‖z‖ = r on the sphere.
  -- Step 2: clamp inactive: 1 ≤ Real.exp r for 0 ≤ r (one_le_exp, Exponential.lean:279),
  --   so max (Real.exp r) 1 = Real.exp r (max_eq_left).
  -- Step 3: for r > 1: Real.log (Real.log (Real.exp r)) = Real.log r (log_exp :74,
  --   twice), and Real.log r / Real.log r = 1 (div_self; log_pos :187 gives ≠ 0).
  -- Step 4: the integrand is therefore eventually-equal to the constant
  --   ENNReal.ofReal 1 = 1 (ofReal_one, Data/ENNReal/Basic.lean:291); close with
  --   limsup_congr (Order/LiminfLimsup.lean:265) + limsup_const (:284).
```

**What its proof needs and whether pinned ingredients suffice (asked by the
brief): they SUFFICE.** No limsup asymptotic is needed anywhere — the
integrand is *eventually exactly* the constant `1`, so the only limsup facts
used are `limsup_congr`/`limsup_const`, which are pinned and side-goal-free in
`ℝ≥0∞`. The only nontrivial content is Step 1's `IsGreatest`, all four of
whose ingredients are quoted in §0 with verified locators. This is the
definition's decisive calibration test: any competing definition that cannot
prove L3 at this cost should lose the review.

Pinned dependencies (L3): all cited inline; every locator in §0.

Obligations (L3): **S1G-L3** (LOW-MEDIUM): elaboration only. Named risks: the
`IsGreatest` pair must be assembled in the image-form `(norm ∘ exp) '' sphere`
(fallback: rewrite with `Set.mem_image` and `mem_sphere_zero_iff_norm` —
name verified in use at the pin, e.g. Geometry/Manifold/Instances/Sphere.lean:131);
`max_eq_left` orientation.

---

### L4. Comparison/monotonicity `[GEN]` `[PIN]` — true BECAUSE of the clamps

```lean
theorem growthOrder_le_of_eventually_le {f : ℂ → E} {g : ℂ → E}
    (h : ∀ᶠ r in Filter.atTop, maxModulus f r ≤ maxModulus g r) :
    growthOrder f ≤ growthOrder g
```

Proof skeleton:

```lean
  -- limsup_le_limsup (Order/LiminfLimsup.lean:198; autoParams free in ℝ≥0∞) reduces to
  -- the eventual pointwise bound. Fix r with maxModulus f r ≤ maxModulus g r and 1 < r.
  -- Write qf, qg for the two clamped quotients. Case split:
  -- • If Real.log (Real.log (max (maxModulus f r) 1)) ≤ 0: then qf ≤ 0 (log r > 0,
  --   div_le_div junk-free), so ofReal qf = 0 (ofReal_eq_zero, Real.lean:181) ≤ ofReal qg
  --   (zero_le).
  -- • Else the outer log on the f-side is > 0, forcing Real.log (max (M f) 1) > 1,
  --   hence max (M f) 1 > e > 1. Chain: 1 ≤ max (M f) 1 ≤ max (M g) 1 (max_le_max,
  --   Order/MinMax.lean:54) → Real.log_le_log (:150; positivity from the chain) on the
  --   inner pair → both inner logs > 1 → Real.log_le_log again on the outer pair →
  --   div_le_div_of_nonneg_right (Algebra/Order/GroupWithZero/Basic.lean:1199) with
  --   0 ≤ log r → ENNReal.ofReal_le_ofReal (Real.lean:137).
```

The case split is not an inconvenience — it is the §1.1 argument in proof
form. Without the inner clamp the second branch's positivity chain has no
floor and the lemma is **false** (counterexample in §1.1). This lemma is the
acceptance test for the clamp design: a reviewer verifying this contract
should check the §1.1 counterexample against the raw formula first.

Pinned dependencies (L4): limsup_le_limsup :198; max_le_max MinMax.lean:54;
Real.log_le_log Log/Basic.lean:150; div_le_div_of_nonneg_right
GroupWithZero/Basic.lean:1199; ofReal_le_ofReal Real.lean:137; ofReal_eq_zero
:181; log_pos :187.

Obligations (L4): **S1G-L4** (MEDIUM): pure case-assembly; no unassembled
asymptotics. The `e`-threshold in the second branch should be phrased as
`1 < Real.log (max …)` (never introducing the constant `e`), to stay inside
`log_le_log`'s hypotheses.

---

### L5. Order of a product is at most the max `[GEN]` `[ASM]`

```lean
theorem growthOrder_mul_le {f g : ℂ → ℂ} (hf : Continuous f) (hg : Continuous g) :
    growthOrder (f * g) ≤ max (growthOrder f) (growthOrder g)
```

Continuity hypotheses are load-bearing: without them `maxModulus` can take
the `sSup_of_not_bddAbove` junk `0` on the *factors* while the product is
bounded, and the statement would compare junk against junk asymmetrically.
(Entire `f g` are continuous; the hypothesis costs consumers nothing.)

Proof skeleton:

```lean
  -- Step 1 (pinned): submultiplicativity of the carrier, for 0 ≤ r:
  --   maxModulus (f * g) r ≤ maxModulus f r * maxModulus g r
  --   via csSup_le (:202) on the nonempty image; pointwise ‖f z * g z‖ = ‖f z‖ * ‖g z‖
  --   (norm_mul; ℂ is a normed field); each factor ≤ its own sSup by le_csSup (:198)
  --   with BddAbove from isCompact_sphere (ProperSpace.lean:45), Continuous.image,
  --   IsCompact.bddAbove (Topology/Order/Compact.lean:322); combine with mul_le_mul
  --   and norm_nonneg.
  -- Step 2 (small, unpinned as a name): clamp submultiplicativity for 0 ≤ a, b:
  --   max (a * b) 1 ≤ max a 1 * max b 1 — four-case `rcases le_total`; private have.
  -- Step 3: Real.log_mul on the clamped factors (both ≥ 1 > 0, so nonzero) turns the
  --   inner log of the product bound into a sum: log (max (M(fg)) 1) ≤ Lf + Lg with
  --   Lf, Lg ≥ 0.
  -- Step 4 (NOT assembled): outer log of a sum: Lf + Lg ≤ 2 * max Lf Lg, then
  --   log (Lf + Lg) ≤ log 2 + log (max Lf Lg) (log_mul again; the max Lf Lg = 0
  --   degenerate branch collapses through the ofReal clamp as in L4). Dividing by
  --   log r: quotient(fg) ≤ (log 2)/(log r) + max (quotient f) (quotient g).
  --   The vanishing (log 2)/(log r) term must be absorbed into the limsup:
  --   ENNReal.limsup_add_le (Order/Filter/ENNReal.lean:231) is UNUSABLE here
  --   ([CountableInterFilter] — atTop on ℝ is not one; §0 trap). Route: for every
  --   ε > 0 eventually (log 2)/(log r) < ε, giving
  --   growthOrder (f*g) ≤ limsup (max-quotients) + ε for all ε; close by
  --   ENNReal ε-induction (le_of_forall_pos_le_add or iInf over ε), then split the
  --   RHS with limsup_max (Order/LiminfLimsup.lean:1141, autoParams free).
```

Pinned dependencies (L5): csSup_le :202 / le_csSup :198; isCompact_sphere
ProperSpace.lean:45; IsCompact.bddAbove Compact.lean:322; Real.log_mul
(Log/Basic.lean — product-to-sum, nonzero args); limsup_max
Order/LiminfLimsup.lean:1141; Tendsto.const_div_atTop
Topology/Algebra/Order/Field.lean:222; tendsto_log_atTop :350.

Obligations (L5): **S1G-L5** (HIGH, honest): Step 4's ε-absorption is an
unassembled limsup argument (same family as L2's Step 3), and Step 2 is an
unpinned (trivial) private lemma. This is the priciest lemma of the surface.
Do NOT reach for `ENNReal.limsup_add_le` (the `CountableInterFilter` trap) or
`ENNReal.limsup_mul_le'` on the *quotients* (the quotient of a product is not
the product of quotients). If Step 4 resists, the honest fallback is to state
L5 with an explicit `+ ε` slack — and record that as a FAILED design gate,
not as a success, since the clean `≤ max` form is part of what makes the
definition "usable".

---

### L6. Type of `exp` at exponent one `[GEN]` `[PIN]` — the type's smoke test

```lean
theorem growthType_exp : growthType Complex.exp 1 = 1
```

Proof skeleton:

```lean
  -- Reuses L3's Step 1 and Step 2 verbatim (maxModulus exp r = Real.exp r, clamp
  -- inactive). Then for r > 0: Real.log (Real.exp r) / r ^ (1 : ℝ) = r / r = 1
  -- (log_exp :74; rpow_one Pow/Real.lean:148; div_self, r ≠ 0). Eventually-constant;
  -- limsup_congr (:265) + limsup_const (:284) + ofReal_one (Basic.lean:291).
```

This exercises the gate honestly: by L3, `growthOrder Complex.exp = 1 =
ENNReal.ofReal 1` and `0 < 1`, so `exp` satisfies G2's gate at `p = 1` and L6
evaluates the type *at* the order — the pair (L3, L6) is the full
order-then-type calibration the classical theory starts from
(`exp` has order 1, type 1).

Pinned dependencies (L6): L3's list; rpow_one Pow/Real.lean:148.

Obligations (L6): **S1G-L6** (LOW): elaboration only; the `r ^ (1 : ℝ)`
rpow-vs-npow elaboration pitfall of S1G-2 applies here concretely.

---

## Pinned API dependencies table (consolidated)

`Order/LiminfLimsup.lean` :64, :198, :265, :284, :1141.
`Data/ENNReal/Basic.lean` :152, :224, :291. `Data/ENNReal/Real.lean` :137, :181.
`Topology/Instances/ENNReal/Lemmas.lean` :70, :817 (and the :30/:745
`namespace ENNReal` spans — both cited lemmas are namespaced).
`Order/Filter/ENNReal.lean` :231 (cited as a TRAP, not a dependency).
`Analysis/SpecialFunctions/Log/Basic.lean` :44, :74, :102, :120, :150, :187,
:212, :221, :350, :449.
`Analysis/SpecialFunctions/Pow/Real.lean` :35, :38, :148.
`Analysis/Complex/Hadamard.lean` :77 (precedent), :99 (`sSupNormIm_nonneg`).
`Algebra/Order/Archimedean/Real/Basic.lean` :171, :189, :294.
`Order/ConditionallyCompleteLattice/Basic.lean` :198, :202.
`Order/ConditionallyCompletePartialOrder/Basic.lean` :72, :120.
`Analysis/Complex/Trigonometric.lean` :995 (inside `namespace Complex`,
opened :24 — the bare `norm_exp` spelling needs `open Complex`).
`Analysis/Complex/Norm.lean` :43, :106. `Data/Complex/Basic.lean` :88.
`Analysis/Complex/Exponential.lean` :279, :315.
`Analysis/Polynomial/Basic.lean` :362 (namespace `Polynomial` :32; section
variables :341). `Analysis/Normed/Module/RCLike/Real.lean` :128.
`Topology/MetricSpace/ProperSpace.lean` :45. `Topology/Order/Compact.lean` :322.
`Topology/Order/LiminfLimsup.lean` :191. `Topology/Algebra/Order/Field.lean` :222.
`Order/MinMax.lean` :54. `Algebra/Order/GroupWithZero/Basic.lean` :1199.
Comparison-only (codomain argument, §1): `Data/EReal/Basic.lean` :35;
`Analysis/Asymptotics/ExpGrowth.lean` :38, :41;
`Analysis/SpecialFunctions/Log/ENNRealLog.lean` :46;
`Topology/Instances/EReal/Lemmas.lean` :265.

## Obligation register

| ID | Severity | Statement | What must hold |
|---|---|---|---|
| S1G-0 | LOW | G0 | elaboration; junk values are the documented `sSup` ones |
| S1G-1 | LOW | G1 | elaboration; design risk is the review itself (§1.3) |
| S1G-2 | LOW | G2 | `r ^ p` elaborates via `Pow ℝ ℝ` (Pow/Real.lean:38), not npow |
| S1G-L1 | MEDIUM | L1 | `OrderTopology ℝ≥0∞` instance search for the `Tendsto.limsup_eq` closer; fallback ε-route recorded |
| S1G-L2 | **HIGH** | L2 | the unassembled `log log (C·rⁿ)/log r → 0` asymptotic (same gap `UPSTREAM_POOL.md` §1.3 names); may split to its own stage-two PR |
| S1G-L3 | LOW-MED | L3 | `IsGreatest` assembly in image form; **pinned ingredients suffice — no asymptotics** |
| S1G-L4 | MEDIUM | L4 | the two-branch clamp case split; no unassembled asymptotics |
| S1G-L5 | **HIGH** | L5 | ε-absorption of `(log 2)/(log r)`; `CountableInterFilter` trap avoided; private clamp-submultiplicativity lemma |
| S1G-L6 | LOW | L6 | elaboration; rpow pitfall of S1G-2 |

Deferred items: **DEFERRED-G1** — the `ℝ≥0∞`-native carrier
(`⨆ ‖f z‖ₑ` + `ENNReal.log`), rejected in §1.2(4), revisit only if the
Hadamard-side consumers demand it. **DEFERRED-G2** — the `Prop`-layer
`HasGrowthOrderLE` and the numeric bridge
`growthOrder_le_of_hasGrowthOrderLE` from scout A: deliberately **out of this
surface**; they are theorems *about* the definition, belong to a later
contract, and must not ride along with the definitional acceptance.

## Claim boundary

- This is an **unbuilt statement surface**. Nothing here is kernel-checked;
  nothing here closes, advances, weakens, or re-scopes the `S1-GROWTH` row
  (repo:`MATHLIB_CAPABILITY_MAP.md:388`) or any other row. Stage-one
  acceptance changes **no** barrier row. The row's exit evidence is "explicit
  quantitative bounds sufficient for the selected theorem"; **definitions
  supply zero bounds**, and no selected theorem exists (no route is active in
  the RH queue).
- What acceptance DOES produce: a reviewed, frozen definitional target so
  that any future growth theorem in this lane is stated about a vetted object
  instead of an improvised one. That is the entire claim.
- **The repo will not build downstream growth theorems on `growthOrder` /
  `growthType` before this definition itself passes independent stage-one
  acceptance** (death condition 1). A later contract that consumes G1/G2 must
  cite the acceptance record, not this draft.
- No statement here mentions ζ, ξ, RH, zero sets, counting functions, or any
  repo theorem; consequently nothing here can smuggle an RH-relevant claim.
  Generic pinned Mathlib machinery lowers the *cost* of a future exit; it
  never retires a row (MULTIPLICITY_CONTRACT finding A4 discipline, inherited
  here as death condition 7).
- L2 and L5 carry HIGH proof obligations, stated as such; this contract does
  not represent them as cheap, and their statements are offered for
  acceptance *with* their cost estimates, so acceptance cannot be read as a
  claim that the proofs are routine.

## Death conditions

Stop and re-plan — do **not** patch around — if any of the following occurs.

1. **The design-bearing acceptance gate (THE gate of this contract).** If any
   downstream module, contract, or draft states a theorem consuming
   `growthOrder` or `growthType` before this definition has an independent
   stage-one acceptance record, stop and retract the consumer. A definition
   error propagates into every downstream statement; the entire value of this
   document is that the object is reviewed **before** it acquires dependents.
   Corollary: this contract must be re-opened (not patched) if review rejects
   the inner clamp or the codomain — every signature changes (§1.3).
2. **A new axiom would be needed.** No `axiom`, `sorry`, `admit`, or
   `native_decide` on an unproved side condition, anywhere in stage two.
3. **Any dependency on an unproved conjecture** — including smuggled binders.
4. **A junk convention is weakened or de-symmetrized.** If a proof becomes
   easier by removing the inner `max … 1` from ONE of G1/G2 but not the
   other, or by letting `growthOrder` and `growthType` disagree on degenerate
   inputs, stop: the symmetric conventions are load-bearing for downstream
   equalities (§1.1) and asymmetric clamps would make order/type identities
   silently false on junk inputs.
5. **The comparison lemma acquires hypotheses to survive.** If L4 cannot be
   proved unconditionally as stated, the definition is wrong (that is what
   the clamps are for) — fix the definition at stage one; do not ship an L4
   with positivity side conditions.
6. **A statement is proposed outside `growthType`'s gate.** Any lemma
   evaluating `growthType f p` at `p ≤ 0`, or binding it to `growthOrder f`
   without the finiteness-and-positivity hypotheses, is junk arithmetic
   dressed as mathematics.
7. **A capability-map row is declared "stale" or "closed" from this work.**
   Definitions never retire a row; any re-scoping is a maintainer decision on
   the map file (inherited from MULTIPLICITY_CONTRACT finding A4).
8. **The barrier row is used as a target.** The RH queue
   (repo:`tasks/RIEMANN_HYPOTHESIS.md`) is the sole authority for this lane;
   no route execution is authorized by this document, and nothing here
   selects, unparks, or advances a route.
9. **Scope creep into the theory.** If closing any L-statement starts to
   require the maximum-modulus principle as a *hypothesis discharge* (rather
   than the recorded compactness facts), Hadamard factorization, Jensen,
   zero-counting, or any ζ/ξ fact — stop; that is a different contract and,
   for ζ/ξ, a different barrier.

---

*Return summary for the caller: 9 public signatures (3 defs G0–G2 + 6 lemmas
L1–L6); codomain `ℝ≥0∞` via `ENNReal.ofReal` outer clamp with a `max … 1`
inner clamp, API verified at the pin; riskiest design choice: the inner clamp
(§1.3). DRAFT, stage-one acceptance only; closes no barrier.*

---

## Annex A — Red-team audit record (2026-08-07)

**Method.** Independent adversarial re-verification against the pinned tree
(`git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD` →
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`, re-confirmed this audit). Source
reading only; no Lean toolchain; nothing elaborated; CI remains the sole
judge. This annex changes **no signature** and does not constitute stage-one
acceptance — it is a hostile pre-review, and the honesty constraint stands
unchanged: **`S1-GROWTH` is neither closed nor advanced by this contract, and
no downstream growth theorem may consume G1/G2 before independent stage-one
acceptance of the definition itself (death condition 1).**

**A.1 Citation re-verification: every locator printed and compared.**
All 60 `file:line` locators in §0, G0–G2, L1–L6, and the consolidated table
were re-printed with `sed -n Np` at the pin and matched the quoted text
**verbatim** — including the four load-bearing traps: `Real.log` junk
(Log/Basic.lean:44, `log_neg_eq_log` :120), the `[CountableInterFilter f]`
hypothesis on `ENNReal.limsup_add_le` (Order/Filter/ENNReal.lean:231; `atTop :
Filter ℝ` is indeed not one: `⋂ n, Set.Ici (n : ℝ) = ∅ ∉ atTop`), the four
`isBoundedDefault` autoParams on `limsup_max` (:1141–:1145, exactly four), and
`div_le_div_of_nonneg_right` (GroupWithZero/Basic.lean:1199), which needs only
`0 ≤ c` — *weaker* than the L4 skeleton assumes. Repo-side locators verified:
`S1-GROWTH` row text at repo:`MATHLIB_CAPABILITY_MAP.md:388`;
`defaultTargets = ["Ecdlp", "ResearchOS"]` at repo:`lakefile.toml:2`;
`tasks/RIEMANN_HYPOTHESIS.md` present; scout A's `EReal` `growthOrder` /
`maxModulus` at `UPSTREAM_POOL.md` (~:110–:128) — same sphere/bare-`sSup`
carrier, so the claimed **two** load-bearing divergences (codomain, inner
clamp) are exactly two, not three; §1.3-hardest-step cross-reference (:193)
accurate; drafts lane exists and contains **no** `RiemannGrowthOrder.lean`
(the surface has acquired no dependents). Absence audit and all-9-name
collision scan re-run: **0 hits**, unchanged.

**A.2 Degenerate-point attack on G0/G1/G2 (all survived).**
* `f = 0`: `maxModulus = sSup {0} = 0` (r ≥ 0) → clamp → `log (log 1) =
  log 0 = 0` → quotient `0` → `growthOrder 0 = 0`. Matches the docstring.
* constants: L1's two branches re-derived; `log_nonpos` (:221) hypotheses
  `0 ≤ log K` (from `K ≥ 1`) and `log K ≤ 1` both available; branch 2's
  `Tendsto`-chain closes with the now-pinned `OrderTopology ℝ≥0∞` (F2).
* bounded nonconstant (none is entire; the definition must not care): clamped
  quotient eventually `≤ log log (max B e) / log r → 0`; order `0`.
* values with norm `< 1` / `M ∈ [0,1)`: inner clamp lifts to `1` before any
  log; the negative-log junk region is unreachable, as designed.
* `sSup = ∞`-type degeneracy (norm-image unbounded at some `r`; impossible
  for entire `f`): `Real.sSup_of_not_bddAbove` junk `0` → clamp `1` →
  contributes `0`. The expression is total and typechecks. **Finding F4:**
  this fourth junk family was handled but *not stated* in G1's docstring,
  violating the "degenerate cases stated explicitly" brief — fixed in place
  (bullet added to G1; symmetry with G2 is automatic through the shared G0
  carrier, so death condition 4 is not tripped).
* `r ≤ 1` region: `log r ≤ 0`, division junk `x/0 = 0` — all germ-irrelevant
  under `atTop`; limsup depends only on the filter germ.
* §1.1 counterexample re-computed: `M = exp (−r)` ⇒ inner `log M = −r` ⇒
  `Real.log (−r) = Real.log r` ⇒ raw quotient `= 1`. Confirmed: the raw
  (unclamped) formula assigns order 1 to exponential *decay* and falsifies
  L4 in every codomain. The inner clamp is load-bearing, as §1.1 argues.

**A.3 Shape-typecheck of the limsup/coercion chain (paper audit).**
`fun r : ℝ => ENNReal.ofReal (…) : ℝ → ℝ≥0∞`; `Filter.limsup` (:64) at
`β := ℝ`, `α := ℝ≥0∞` needs `ConditionallyCompleteLattice ℝ≥0∞` — supplied by
`CompleteLinearOrder ℝ≥0∞` (Data/ENNReal/Basic.lean:152); `atTop : Filter ℝ`
from `Preorder ℝ`; `NeBot atTop` instance present for `limsup_const`. The
inner expression is all-`ℝ` with a **single** `ENNReal.ofReal` at the
boundary — no coercion seam anywhere (scout A's `EReal` version needs an
`(↑ : ℝ → EReal)` inside the lambda). G2's `r ^ p` with `p : ℝ` resolves to
the `Pow ℝ ℝ` rpow instance (Pow/Real.lean:38); S1G-2's caution retained.

**A.4 The exp-order-1 claim (L3): [PIN] UPHELD, not demoted.** Every
ingredient exists at the pin with the exact quoted signature, and the
namespaces were verified by span: `Complex.norm_exp` at
Trigonometric.lean:995 inside the `Complex` span :954–:1002 (**finding F1:**
the consolidated table said "opened :24", which is a different, earlier
`Complex` span in that file — locator corrected in place; the qualified name
and usability are unaffected); `Real.one_le_exp` (:279) and `Real.exp_le_exp`
(:315) inside the `Real` span opening at Analysis/Complex/Exponential.lean:200
— the file placement is surprising but true at this pin. The route was
re-derived end-to-end: `IsGreatest` membership needs `0 ≤ r` (eventual under
`atTop`) via `Complex.norm_of_nonneg` + `mem_sphere_zero_iff_norm` (**finding
F3:** that name is `to_additive`-generated from `mem_sphere_one_iff_norm`,
Analysis/Normed/Group/Basic.lean:302–303 — a declaration-grep finds nothing,
which this audit hit and traced; generation site now recorded in S1G-L3);
upper bound via `re_le_norm` + `Real.exp_le_exp`; clamp discharged by
`one_le_exp`; Steps 3–4 close with `log_exp`/`log_pos`/`div_self` and
`limsup_congr`/`limsup_const` only. **No limsup asymptotic is consumed
anywhere in L3**; the `[PIN]` tag and the "pinned ingredients SUFFICE" claim
stand. `NormedSpace.sphere_nonempty` instance context verified: section
variables `[SeminormedAddCommGroup E] [NormedSpace ℝ E]` (RCLike/Real.lean:38)
+ `[NontrivialTopology E]` (:103), all satisfied at the use site `E := ℂ`.

**A.5 Obligation changes (register updated in place).**
* **F2 — S1G-L1 downgraded MEDIUM → LOW.** The draft's hedge ("not settleable
  by source reading alone") was wrong in the safe direction: `instance :
  TopologicalSpace ℝ≥0∞ := Preorder.topology ℝ≥0∞` and `instance :
  OrderTopology ℝ≥0∞ := ⟨rfl⟩` are literal pinned declarations
  (Topology/Order/Real.lean:53/:55), and `Tendsto.limsup_eq`'s section
  variables (Topology/Order/LiminfLimsup.lean:151) are exactly satisfied.
* **F3 — S1G-L3 sharpened** (generation-site locator; severity unchanged
  LOW-MED).
* S1G-L2 and S1G-L5 remain **HIGH** and are *confirmed* honest: the audit
  found no assembled `log log (C·rⁿ)/log r → 0` lemma and no
  `atTop`-compatible ENNReal limsup-additivity at the pin; the demote-or-prove
  question posed by the audit brief lands on "already registered at the
  correct severity".

**A.6 What the audit did NOT find.** No false citation (one imprecise span
locator, F1). No degenerate input on which G1/G2 disagree or fail to
typecheck. No counterexample to L1, L3, L4, or L6 as stated. No hidden axiom,
hypothesis smuggling, or route selection. No dependent of `growthOrder` /
`growthType` anywhere in the repo (death condition 1 unviolated).

**Verdict: PASS WITH CORRECTIONS (all applied in place, this annex is the
record).** The statement surface G0–G2, L1–L6 is fit to be *offered* for
stage-one independent acceptance exactly as the contract frames it: a
design-bearing, unbuilt, kernel-unchecked definitional proposal that closes no
barrier, advances no route, and asserts nothing about RH.
