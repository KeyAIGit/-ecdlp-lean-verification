# RH multiplicity / divisor theorem contract (S1-MULTIPLICITY): draft v2

Status: **DRAFT v2 (2026-08-07) — non-built review artifact, offered for STAGE ONE
(INDEPENDENT CONTRACT ACCEPTANCE) ONLY. NOT Lean-checked.** No declaration below
has been elaborated; no `lake build` has been run against any of it. Under the one
invariant, the Lean kernel via CI is the sole judge of every statement in this
contract, and this document carries no kernel verdict of any kind.

**Two-stage gate (reviewer requirement; the full statement is §Two-stage gate and
promotion ordering at the end of this file).** Stage one is *independent contract
acceptance*: a review of the statement surface M1–M17 only. It produces **no built
module, no ledger row, no registry or axiom-audit entry, and no kernel verdict**.
Stage two is a **separate built promotion PR** that carries the module, its ledger
rows, the regenerated registry and axiom audit, and the promotion review record,
and whose verdict is delivered by CI. The reviewer requires these to be two
separate changes; **an acceptance PR must not carry a promotion.** Current CI does
not elaborate the drafts-lane file `drafts/RiemannMult.lean`, because it lies
outside every lake target (`lakefile.toml:2` declares
`defaultTargets = ["Ecdlp", "ResearchOS"]`; the build step at
`.github/workflows/ci.yml:420` runs `lake build` over those targets, and the
no-incomplete-proof scan at `:359` covers only `Ecdlp.lean Ecdlp/ ResearchOS/
ResearchOS.lean`). **Therefore no green CI run on an acceptance PR is evidence of
anything about the draft.**

**Ordering.** The reviewer's constraint is that the corrected contract returns as
an acceptance-only PR **after `RH-002` closes**. `RH-002` is currently the **sole
ACTIVE task** in the RH queue (`tasks/RIEMANN_HYPOTHESIS.md:28`, and its own
status line at `:122`, "ACTIVE — independent disposition review only; no route
execution authorized"). The RH queue — not `repo/ECDLP_DECISION_SUBSTRATE.json`,
which governs the ECDLP lane — is the authority for this lane. This document is an
offered artifact, not an active task, and not authorization to work a route.

An internal adversarial review was run on the source skeleton (verdict
`SOUND_WITH_FIXES`, ten findings A1–A10, all applied in place; see Annex A). That
review accepts a statement surface only: it is not a kernel verdict, it does not
promote a module, and it does not close `S1-MULTIPLICITY` or `S1-CONJ`.

Working name: `Mult.lean` (module
`ResearchOS.AnalyticNumberTheory.RiemannHypothesis.Mult`).
Statement surface: **M1 – M17**, comprising **exactly 34 public signatures**,
every one of which is spelled explicitly in a `lean` statement block in §2 (the
M-numbers are section labels, not a declaration count: several sections carry
more than one signature, and M15 carries six). No signature of this package is
mandated in prose only.

Scope: the `S1-MULTIPLICITY` barrier of `MATHLIB_CAPABILITY_MAP.md` ("zero set
loses analytic multiplicity and no conjugation/reflection action preserves
it"; remaining exit evidence "zeta/xi divisor interface and
multiplicity-preserving divisor symmetries"), and the divisor half of the
`S1-CONJ` exit. It contains **no** zero enumeration, **no** counting function,
**no** Li coefficients, **no** growth theorem, **no** Hadamard product, and
**no** claim of progress on the Riemann Hypothesis. `S1-GLOBAL-ZEROS` is a
different barrier and is not touched.

Pinned Mathlib: `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` (v4.31.0),
toolchain `leanprover/lean4:v4.31.0`, verified this session via
`git -C /workspace/leanprover-community/mathlib4 rev-parse HEAD`. Every
`file:line` locator below is from that exact tree (paths relative to the
`Mathlib/` root of the pin) unless prefixed `repo:`. Every locator in the
source skeleton was re-verified during the adversarial review and re-verified
again during repository integration; the integration pass corrected six
locators, recorded in Annex A §E.

Repo prerequisites (kernel-checked on `main`):

| Symbol | Location |
|---|---|
| `riemannXi` | repo:`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/Xi.lean:41` |
| `differentiable_riemannXi` | repo:`…/Xi.lean:46` |
| `riemannXi_one_sub` | repo:`…/Xi.lean:61` |
| `riemannXi_zero` (`= 1/2`) | repo:`…/Xi.lean:72` |
| `riemannXi_one` (`= 1/2`) | repo:`…/Xi.lean:78` |
| `riemannXi_zero_mem_critical_strip` | repo:`…/Xi.lean:192` |
| `analyticOrderAt_riemannXi_eq_riemannZeta` (X11) | repo:`…/Xi.lean:248` |

Conjugation-package prerequisites, **also kernel-checked on `main`** — merged in
PR #307 (`c277b86`), imported from `ResearchOS.lean`:

| Symbol | Location |
|---|---|
| `riemannZeta_comp_conj` | repo:`…/Conj.lean:163` |
| `riemannXi_comp_conj` | repo:`…/Conj.lean:292` |
| `analyticOrderAt_conj_conj` | repo:`…/Conj.lean:357` |
| `analyticOrderAt_riemannZeta_conj` | repo:`…/Conj.lean:440` |
| `analyticOrderAt_riemannXi_conj` | repo:`…/Conj.lean:452` |

**Provenance.** Every prerequisite of every statement M1–M17 is now either pinned
Mathlib or a kernel-checked theorem on current `main`: the target bridge merged in
PR #299 (`288d65b`), the xi package in PR #304 (`afdae08`), and the conjugation
package in PR #307 (`c277b86`). **No statement in this contract waits on an
unmerged PR.** PR #306 and PR #308 are **CLOSED and UNMERGED** and are cited
nowhere in this document as provenance for anything; the only mentions of either
number are this sentence and the historical note in Annex A §D.1, both of which
say only that they must not be cited. The earlier landing-order split between
"#306-independent" and "#306-blocked" statements is obsolete and has been removed
from §3: the whole surface can be stated against current `main` plus the pin. The
tag for a statement that consumes the merged conjugation package is `[CONJ]`; it
marks a **merged package prerequisite**, never a blocker.

Barrier-closure boundary (stated up front, honestly): closing this package
supplies the ζ/ξ divisor interface (M9–M13 for ξ on an arbitrary set; M16–M16''
for ζ on the open strip) and the multiplicity-preserving symmetries at both the
order level (M3–M8) and the divisor level (M14, M15, M17). It does **not** on
its own close either barrier, and nothing here closes any barrier at stage one:
acceptance of a statement surface changes no barrier row. `S1-CONJ`'s remaining
divisor-invariance half is carried by M15/M17c, which themselves consume
repo:`Conj.lean:440/452`; that half is discharged only when this package is
kernel-checked and promoted at stage two — not by this document.
`S1-MULTIPLICITY`'s row is scoped to this repository's ζ/ξ layer; generic
pinned Mathlib machinery lowers the cost of an exit but never retires a row
(finding A4, death condition 9). See §Claim boundary.

## Candidate fields

- **Mechanism.** Pointwise `analyticOrderAt` is the primary carrier. The
  reflection leg comes from the pinned generic lemma
  `analyticOrderAt_comp_of_deriv_ne_zero` (Order.lean:561) applied to the
  ℂ-analytic involution `fun w => c - w`, whose derivative is `-1 ≠ 0`
  (Deriv/Add.lean:449); composed with the repo's `riemannXi_one_sub`
  (repo:`Xi.lean:61`) this gives ξ order transport under `s ↦ 1 - s`, and X11
  (repo:`Xi.lean:248`) transports it to ζ inside the open strip. The
  conjugation leg is imported wholesale from the merged conjugation package
  (repo:`Conj.lean:440/452`, PR #307 (`c277b86`), on `main`). The divisor half runs
  through the single bridge lemma `MeromorphicOn.AnalyticOnNhd.divisor_apply`
  (Divisor.lean:71), which rewrites every order identity into the
  corresponding divisor identity by `congrArg`; ξ reaches
  `MeromorphicOn.divisor` in four pinned steps from
  `differentiable_riemannXi`, and ζ reaches it on the open strip from
  `differentiableAt_riemannZeta` (RiemannZeta.lean:137). Divisor support is
  identified with the zero set via `MeromorphicNFOn.zero_set_eq_divisor_support`
  (NormalForm.lean:578), whose only hypothesis is pointwise **finite local
  meromorphic order** (`∀ u : U, meromorphicOrderAt f u ≠ ⊤`) — never a growth
  order of an entire function — supplied by M12 for ξ and by X11 + M12 for ζ on
  the strip.
- **Expected information gain.** Supplies the repo-local ζ/ξ divisor interface
  and the multiplicity-preserving divisor symmetries named as the remaining
  `S1-MULTIPLICITY` exit evidence, plus the divisor-invariance leg of the
  `S1-CONJ` exit. No information about the truth of RH is produced.
- **Claim boundary.** M1–M4, M9–M14, M16–M16'' and M17a are unconditional
  consequences of pinned Mathlib theorems plus kernel-checked repo theorems on
  `main`. M5–M8, M15, M17b, M17c additionally consume the merged conjugation
  package (repo:`Conj.lean:440/452`, PR #307 (`c277b86`), on `main`) — a merged
  package prerequisite, not pinned Mathlib and not a blocker. Nothing touches
  enumeration, counting, growth, Hadamard products, Li coefficients, zero
  simplicity, or any route's research obligation. The package contains zero
  `def`s.
- **Death condition (stop rule).** Stop or split if a proof would need a new
  axiom, an unproved conjecture, a zero enumeration, a growth or counting
  bound, a ζ statement without the strip hypotheses, or a new definition; and
  do not declare a capability-map row stale on the strength of generic pinned
  Mathlib. Full list in §Death conditions. A clean blocker is preferable to a
  false symmetry.

Proposed module preamble (name-resolution review only; the eventual built file
also imports the built xi and conjugation modules):

```lean
import ResearchOS.AnalyticNumberTheory.RiemannHypothesis.Xi     -- riemannXi, X11
import ResearchOS.AnalyticNumberTheory.RiemannHypothesis.Conj   -- Z9 order legs (merged, PR #307)
import Mathlib.Analysis.Analytic.Order          -- analyticOrderAt_comp_of_deriv_ne_zero
import Mathlib.Analysis.Calculus.Deriv.Add      -- deriv_const_sub_id
import Mathlib.Analysis.Meromorphic.Divisor     -- MeromorphicOn.divisor
import Mathlib.Analysis.Meromorphic.NormalForm  -- zero_set_eq_divisor_support
import Mathlib.Analysis.Complex.CauchyIntegral  -- analyticOnNhd_univ_iff_differentiable

open Complex Filter
open scoped Real Topology ComplexConjugate
```

`Mathlib.Analysis.Analytic.Order` is already pulled by both built packages
(repo:`Xi.lean:22`, repo:`Conj.lean:41` — both re-verified) and transitively
supplies `Mathlib.Analysis.Calculus.InverseFunctionTheorem.Analytic`
(**Order.lean:10**, not :9 — :9 is `Mathlib.Analysis.Calculus.Deriv.Pow`;
finding A6), so the `CompleteSpace ℂ` / `CharZero ℂ` machinery for M2 arrives
for free.

`analyticAt_id` lives in `Mathlib/Analysis/Analytic/Linear.lean:156`
(finding A1). It is reachable transitively, but the `fun_prop` discharge used
in M2/M3 does not depend on the name being in scope, so no extra import is
listed.

Notation used below: `Ω : Set ℂ := {s : ℂ | 0 < s.re ∧ s.re < 1}` — written
inline as a set-builder literal at each use site, **not** as a new definition.

Name-collision scan (grep over the pinned tree this session): **zero hits** for
every proposed name — `analyticOrderAt_comp_const_sub`, `riemannXi_comp_one_sub`,
`analyticOrderAt_riemannXi_one_sub`, `analyticOrderAt_riemannZeta_one_sub`,
`riemannXi_divisor_apply`, `divisor_comp`, `locallyFinsuppWithin.comap`.
`riemannXi` itself is repo-local: `grep -rn "riemannXi" Mathlib/` at the pin
returns zero hits. A repo-side scan for the Block D/E names
(`analyticOnNhd_riemannXi`, `meromorphicOn_riemannXi`, `riemannXi_divisor*`,
`riemannZeta_divisor*`, `analyticOnNhd_riemannZeta_strip`,
`analyticOrderAt_riemannXi_ne_top`, `analyticOrderAt_riemannXi_fourfold`,
`analyticOrderAt_riemannZeta_fourfold`) also returns **zero hits**. The single
new *generic* statement (M2) is a theorem over pinned objects, not a definition.

---

## 0. Exact pinned interface (quoted from the tree at the pin)

```lean
-- Analysis/Analytic/Order.lean:47 (def; junk value 0 at non-analytic points, :64)
noncomputable def analyticOrderAt (f : 𝕜 → E) (z₀ : 𝕜) : ℕ∞
lemma analyticOrderAt_of_not_analyticAt (hf : ¬ AnalyticAt 𝕜 f z₀) :
    analyticOrderAt f z₀ = 0

-- Analysis/Analytic/Order.lean:133, :137 (both `protected`; dot notation resolves)
protected lemma AnalyticAt.analyticOrderAt_eq_zero (hf : AnalyticAt 𝕜 f z₀) :
    analyticOrderAt f z₀ = 0 ↔ f z₀ ≠ 0
protected lemma AnalyticAt.analyticOrderAt_ne_zero (hf : AnalyticAt 𝕜 f z₀) :
    analyticOrderAt f z₀ ≠ 0 ↔ f z₀ = 0

-- Analysis/Analytic/Order.lean:525 (section variables constraining :561)
variable {f : 𝕜 → E} {g : 𝕜 → 𝕜} {z₀ : 𝕜}

-- Analysis/Analytic/Order.lean:561 — THE reflection-transport input.
-- Docstring: "even if `f` is not analytic"; junk branch discharged at :566-567.
lemma analyticOrderAt_comp_of_deriv_ne_zero (hg : AnalyticAt 𝕜 g z₀) (hg' : deriv g z₀ ≠ 0)
    [CompleteSpace 𝕜] [CharZero 𝕜] :
    analyticOrderAt (f ∘ g) z₀ = analyticOrderAt f (g z₀)

-- Analysis/Analytic/Order.lean:575 opens `namespace AnalyticOnNhd` (closes :700), so the
-- next two are AnalyticOnNhd.exists_… and AnalyticOnNhd.analyticOrderAt_ne_top_of_…
theorem exists_analyticOrderAt_ne_top_iff_forall (hf : AnalyticOnNhd 𝕜 f U) (hU : IsConnected U) :
    (∃ u : U, analyticOrderAt f u ≠ ⊤) ↔ (∀ u : U, analyticOrderAt f u ≠ ⊤)          -- :614
theorem analyticOrderAt_ne_top_of_isPreconnected {x y : 𝕜} (hf : AnalyticOnNhd 𝕜 f U)
    (hU : IsPreconnected U) (h₁x : x ∈ U) (hy : y ∈ U) (h₂x : analyticOrderAt f x ≠ ⊤) :
    analyticOrderAt f y ≠ ⊤                                                          -- :624

-- Analysis/Analytic/Order.lean:687, :693. :687 is STILL inside `namespace AnalyticOnNhd`
-- (opened :575, closed :700), so its full name is
-- `AnalyticOnNhd.analyticOrderAt_eq_top_iff_eq_zero`. It takes NO `AnalyticOnNhd`
-- argument: its hypotheses are `[PreconnectedSpace 𝕜]` and pointwise analyticity
-- everywhere, `∀ z₀, AnalyticAt 𝕜 f z₀`. Dot notation on an `AnalyticOnNhd` hypothesis
-- therefore does NOT resolve; always write the fully-qualified name.
-- :693 does carry an explicit `_root_.` prefix, so it is `IsOpen.forall_…` at root.
lemma analyticOrderAt_eq_top_iff_eq_zero [PreconnectedSpace 𝕜] {f : 𝕜 → E} (z : 𝕜)
    (hf : ∀ z₀, AnalyticAt 𝕜 f z₀) : analyticOrderAt f z = ⊤ ↔ f = 0
lemma _root_.IsOpen.forall_analyticOrderAt_eq_top_iff_eqOn_zero {s : Set 𝕜} (hs : IsOpen s)
    (f : 𝕜 → E) : (∀ z ∈ s, analyticOrderAt f z = ⊤) ↔ EqOn f 0 s

-- Analysis/Calculus/InverseFunctionTheorem/Analytic.lean:40 (used internally by :561)
lemma analyticAt_comp_iff_of_deriv_ne_zero (hf : AnalyticAt 𝕜 f x) (hf' : deriv f x ≠ 0) : …

-- Analysis/Calculus/Deriv/Add.lean:449, :453 (`@[simp]` twin)
theorem deriv_const_sub_id (c : 𝕜) : deriv (c - ·) x = -1
theorem deriv_const_sub_id' (c : 𝕜) : deriv (c - ·) = fun _ => -1

-- Algebra/Group/Basic.lean:933 — the involution identity, via `@[to_additive (attr := simp)]`
-- at :932; the additive twin is `sub_sub_cancel : a - (a - b) = b`
@[to_additive (attr := simp)]
theorem div_div_cancel (a b : G) : a / (a / b) = b

-- Analysis/Meromorphic/Divisor.lean:39 — TOTAL: no hypotheses on `f` or `U` at all.
-- `namespace MeromorphicOn` spans :28-:468 (see §1 naming trap).
noncomputable def divisor (f : 𝕜 → E) (U : Set 𝕜) :
    Function.locallyFinsuppWithin U ℤ where
  toFun := fun z ↦ if MeromorphicOn f U ∧ z ∈ U then (meromorphicOrderAt f z).untop₀ else 0
  supportWithinDomain' := …                        -- :42-44
  supportLocallyFiniteWithinDomain' := …           -- :45-55, via
    -- codiscrete_setOf_meromorphicOrderAt_eq_zero_or_top (:51). Discharged INSIDE the
    -- definition, for every `f` and every `U`. No growth input. (Finding A10.)

-- Analysis/Meromorphic/Divisor.lean:68, :71 — the two `_apply` lemmas (hypotheses live here)
lemma divisor_apply {f : 𝕜 → E} (hf : MeromorphicOn f U) (hz : z ∈ U) :
    divisor f U z = (meromorphicOrderAt f z).untop₀
lemma AnalyticOnNhd.divisor_apply {f : 𝕜 → E} (hf : AnalyticOnNhd 𝕜 f U) (hz : z ∈ U) :
    divisor f U z = ((analyticOrderAt f z).map (↑)).untop₀

-- Analysis/Meromorphic/Divisor.lean:177 (same namespace trap), :83 (the `_root_` contrast), :104
theorem AnalyticOnNhd.divisor_nonneg {f : 𝕜 → E} (hf : AnalyticOnNhd 𝕜 f U) :
    0 ≤ MeromorphicOn.divisor f U
lemma _root_.divisor_sphere_support_finite [ProperSpace 𝕜] {f : 𝕜 → E} {R : ℝ} {c : 𝕜} : …
lemma divisor_ball_support_finite [ProperSpace 𝕜] {f : 𝕜 → E} {R : ℝ} {c : 𝕜} : …

-- Topology/LocallyFinsupp.lean:48 (structure), :125 (FunLike), :197, :401 (pointwise LE)
structure Function.locallyFinsuppWithin [Zero Y] where
  toFun : X → Y
  supportWithinDomain' : toFun.support ⊆ U
  supportLocallyFiniteWithinDomain' : ∀ z ∈ U, ∃ t ∈ 𝓝 z, Set.Finite (t ∩ toFun.support)
instance [Zero Y] : FunLike (locallyFinsuppWithin U Y) X Y
lemma apply_eq_zero_of_notMem [Zero Y] {z : X} (D : locallyFinsuppWithin U Y) (hz : z ∉ U) :
    D z = 0
instance [LE Y] [Zero Y] : LE (locallyFinsuppWithin U Y)

-- Algebra/Order/WithTop/Untop0.lean:30, :41 — the information-losing totalization
def untop₀ (a : WithTop α) : α := a.untopD 0
lemma untop₀_top : untop₀ ⊤ = (0 : α)

-- Analysis/Meromorphic/Order.lean:47 (junk 0 off meromorphy), :279
noncomputable def meromorphicOrderAt (f : 𝕜 → E) (x : 𝕜) : WithTop ℤ
lemma AnalyticAt.meromorphicOrderAt_eq (hf : AnalyticAt 𝕜 f x) :
    meromorphicOrderAt f x = (analyticOrderAt f x).map (↑)

-- Analysis/Meromorphic/NormalForm.lean:567, :578. The file has NO `namespace` block, so
-- both are root names and dot notation works. Note the orientation of :578.
theorem AnalyticOnNhd.meromorphicNFOn (h₁f : AnalyticOnNhd 𝕜 f U) : MeromorphicNFOn f U
theorem MeromorphicNFOn.zero_set_eq_divisor_support (h₁f : MeromorphicNFOn f U)
    (h₂f : ∀ u : U, meromorphicOrderAt f u ≠ ⊤) :
    U ∩ f ⁻¹' {0} = Function.support (MeromorphicOn.divisor f U)

-- Analysis/Meromorphic/Basic.lean:475, Analysis/Analytic/Basic.lean:498
lemma AnalyticOnNhd.meromorphicOn {f : 𝕜 → E} {U : Set 𝕜} (hf : AnalyticOnNhd 𝕜 f U) :
    MeromorphicOn f U
theorem AnalyticOnNhd.mono {s t : Set E} (hf : AnalyticOnNhd 𝕜 f t) (hst : s ⊆ t) :
    AnalyticOnNhd 𝕜 f s

-- Analysis/Complex/CauchyIntegral.lean:678, :625. :678 is INSIDE `namespace Complex`
-- (opened :173, closed :770), so its fully-qualified name is
-- `Complex.analyticOnNhd_univ_iff_differentiable`; the bare spelling used in M9
-- resolves only under this file's `open Complex`. :625 carries an explicit
-- `_root_.` prefix, so `DifferentiableOn.analyticAt` really is a root name.
theorem analyticOnNhd_univ_iff_differentiable {f : ℂ → E} :
    AnalyticOnNhd ℂ f univ ↔ Differentiable ℂ f
protected theorem _root_.DifferentiableOn.analyticAt {s : Set ℂ} {f : ℂ → E} {z : ℂ}
    (hd : DifferentiableOn ℂ f s) (hz : s ∈ 𝓝 z) : AnalyticAt ℂ f z

-- Data/ENat/Basic.lean:526 (namespace ENat). Mathlib itself uses this lemma in exactly
-- this position at Analysis/Meromorphic/Order.lean:71.
lemma map_eq_top_iff {f : ℕ → α} : map f n = ⊤ ↔ n = ⊤

-- NumberTheory/LSeries/RiemannZeta.lean:137, :171; Nonvanishing.lean:410
theorem differentiableAt_riemannZeta {s : ℂ} (hs' : s ≠ 1) : DifferentiableAt ℂ riemannZeta s
theorem riemannZeta_neg_two_mul_nat_add_one (n : ℕ) : riemannZeta (-2 * (n + 1)) = 0
lemma _root_.riemannZeta_ne_zero_of_one_le_re ⦃s : ℂ⦄ (hs : 1 ≤ s.re) : riemannZeta s ≠ 0

-- Analytic constructors used by `fun_prop` in M2/M3
theorem analyticAt_const {v : F} {x : E} : AnalyticAt 𝕜 (fun _ => v) x  -- Constructions.lean:54
@[to_fun (attr := fun_prop)]                                           -- Constructions.lean:186
theorem AnalyticAt.sub (hf : AnalyticAt 𝕜 f x) (hg : AnalyticAt 𝕜 g x) : …  -- :187
@[fun_prop]                                                            -- Linear.lean:155
lemma analyticAt_id : AnalyticAt 𝕜 (id : E → E) z                      -- Linear.lean:156

-- Instances on the BASE FIELD (nothing to build)
instance : CompleteSpace ℂ                       -- Analysis/Complex/Basic.lean:124
instance instCharZero : CharZero ℂ               -- Data/Complex/Basic.lean:773
instance (priority := 100) NormedSpace.instPathConnectedSpace : PathConnectedSpace E
                                                 -- Analysis/Normed/Module/Convex.lean:168

-- Complex `re` arithmetic
theorem one_re : (1 : ℂ).re = 1                  -- Data/Complex/Basic.lean:147
theorem conj_re (z : ℂ) : (conj z).re = z.re     -- Data/Complex/Basic.lean:467
theorem sub_re (z w : ℂ) : (z - w).re = z.re - w.re  -- Data/Complex/Basic.lean:640
theorem continuous_re : Continuous re            -- Analysis/Complex/Basic.lean:153
```

---

## 1. Carrier decision

### Decision: **both, with an explicit one-lemma bridge; `analyticOrderAt` is primary.**

- **Primary carrier — pointwise `analyticOrderAt : (𝕜 → E) → 𝕜 → ℕ∞`**
  (`Mathlib/Analysis/Analytic/Order.lean:47`). All *transport* content
  (M1–M8) is stated and proved here. This is the carrier the two built
  packages already use (repo:`Xi.lean:248`, repo:`Conj.lean:357/440/452`), so
  the new package composes with them by plain `rw`, with no coercion layer.

- **Secondary carrier — `MeromorphicOn.divisor : (𝕜 → E) → Set 𝕜 →
  Function.locallyFinsuppWithin U ℤ`**
  (`Mathlib/Analysis/Meromorphic/Divisor.lean:39`), valued in
  `Function.locallyFinsuppWithin` (`Mathlib/Topology/LocallyFinsupp.lean:48`).
  Used for the divisor-object half of the exit evidence — **ξ on an arbitrary
  `U` (M9–M15) and ζ on the open strip (M16–M17)**; the exit row asks for a
  *zeta/xi* interface, not a ξ-only one (finding A5).

- **Bridge — `MeromorphicOn.AnalyticOnNhd.divisor_apply`**
  (`Mathlib/Analysis/Meromorphic/Divisor.lean:71`):
  `divisor f U z = ((analyticOrderAt f z).map (↑)).untop₀`.
  This single lemma turns every M1–M8 order identity into the corresponding
  M14/M15 divisor identity by `congrArg`. It is the *only* seam between the
  two carriers.

### Justification

1. **The divisor API is genuinely usable at the pin.** `MeromorphicOn.divisor`
   is *total*: it takes `f` and `U` with **no hypotheses at all**
   (Divisor.lean:39; the meromorphy and membership guards live inside the `if`,
   and hypotheses appear only in the `_apply` lemmas at :68/:71). This matches
   the repo's totalization convention exactly. `U` need not be open, connected,
   bounded, or compact. The divisor block is therefore **in scope, not
   deferred**. *This is a statement about cost, not about the capability-map
   row — see finding A4 and death condition 9.*

2. **`riemannXi` reaches the divisor with four pinned steps and no new
   analysis**: `differentiable_riemannXi` (repo:`Xi.lean:46`) →
   `analyticOnNhd_univ_iff_differentiable`
   (`Mathlib/Analysis/Complex/CauchyIntegral.lean:678`) →
   `AnalyticOnNhd.mono` (`Mathlib/Analysis/Analytic/Basic.lean:498`) →
   `AnalyticOnNhd.meromorphicOn` (`Mathlib/Analysis/Meromorphic/Basic.lean:475`).

3. **`analyticOrderAt` stays primary because the divisor loses information.**
   `divisor` composes `meromorphicOrderAt` (junk `0` off meromorphy,
   `Mathlib/Analysis/Meromorphic/Order.lean:47`) with `WithTop.untop₀`
   (`Mathlib/Algebra/Order/WithTop/Untop0.lean:30`, `untop₀_top = 0` at :41).
   So `divisor riemannXi U z = 0` conflates *"z is not a zero"* with
   *"ξ vanishes identically near z"*. `analyticOrderAt` keeps `⊤` distinct.
   Proving the transport at the `ℕ∞` level and pushing forward is strictly
   stronger than proving it at the `ℤ` level. (See obligation **S1M-FIN**.)

4. **No new definitions.** Name-collision scan run at the pin over `Mathlib/`
   for `analyticOrderAt_comp_const_sub`, `riemannXi_comp_one_sub`,
   `analyticOrderAt_riemannXi_one_sub`, `analyticOrderAt_riemannZeta_one_sub`,
   `riemannXi_divisor_apply`, `divisor_comp`, `locallyFinsuppWithin.comap`:
   **zero hits for all seven**. `riemannXi` itself is repo-local (no Mathlib
   `riemannXi` at the pin). The single new *statement* that is generic
   (M2) is a theorem over pinned objects, not a definition.

5. **What we deliberately do NOT build: a divisor pullback.** Exhaustive
   search of `Mathlib/Topology/LocallyFinsupp.lean` confirms the only
   carrier-changing maps are `restrict` (:584), `restrictMonoidHom` (:625),
   `restrictLatticeHom` (:661). There is **no** `comap` / `map` /
   pushforward / pullback along a self-map `X → X`, and no `divisor_comp` in
   `Mathlib/Analysis/Meromorphic/Divisor.lean`. Building one would be a new
   definition with a nontrivial `supportLocallyFiniteWithinDomain'` field
   obligation, for a single use. **We avoid it by stating M14/M15 pointwise**
   (`Function.locallyFinsuppWithin` is a `FunLike`, LocallyFinsupp.lean:125),
   which is exactly as strong for the exit evidence and costs nothing.
   Recorded as **DEFERRED-1**.

### Naming trap (pre-registered, cost one CI cycle if missed)

`namespace MeromorphicOn` spans Divisor.lean:28–468 and lines :71 and :177
carry **no** `_root_` prefix (contrast :83, which writes
`_root_.divisor_sphere_support_finite` explicitly). Their true full names are
therefore `MeromorphicOn.AnalyticOnNhd.divisor_apply` and
`MeromorphicOn.AnalyticOnNhd.divisor_nonneg`. Dot-notation `hf.divisor_apply`
on an `AnalyticOnNhd` hypothesis **will not resolve**. Every M9–M15 skeleton
below writes the fully-qualified name.

---

## 2. Statement list M1 – M17

Legend for tags: `[PIN]` provable from pinned Mathlib + `main`;
`[CONJ]` additionally consumes the **merged** conjugation package
(repo:`Conj.lean:440/452`, PR #307 (`c277b86`), on `main`, imported from
`ResearchOS.lean`) — a merged package prerequisite, **not** a blocker and **not**
pinned Mathlib; `[GEN]` generic, natural Mathlib upstream.

---

### Block A — reflection order transport for ξ (barrier exit item (a))

## M1. Function-level reflection glue `[PIN]`

### Statement

```lean
theorem riemannXi_comp_one_sub :
    riemannXi ∘ (fun s : ℂ => 1 - s) = riemannXi
```

### Proof skeleton

```lean
  funext s
  simpa only [Function.comp_apply] using riemannXi_one_sub s
```

### Pinned dependencies (M1)

repo:`Xi.lean:61` (`riemannXi_one_sub (s) : riemannXi (1 - s) = riemannXi s`).

*Notes.* Deliberately mirrors `riemannXi_comp_conj` (repo:`Conj.lean:292`) so
that M3 has the same one-`rw` shape as `analyticOrderAt_riemannXi_conj`
(repo:`Conj.lean:452`).

### Obligations (M1)

- **S1M-1** (LOW): the `∘`-form must elaborate against
  `analyticOrderAt_comp_of_deriv_ne_zero`'s `f ∘ g`; fallback is
  `funext s; show riemannXi (1 - s) = riemannXi s; exact riemannXi_one_sub s`.

---

## M2. Generic precomposition-order lemma for an affine reflection `[GEN]` `[PIN]`

### Statement

```lean
theorem analyticOrderAt_comp_const_sub {E : Type*} [NormedAddCommGroup E]
    [NormedSpace ℂ E] (f : ℂ → E) (c z : ℂ) :
    analyticOrderAt (f ∘ (fun w : ℂ => c - w)) (c - z) = analyticOrderAt f z
```

### Proof skeleton

*Full assembly sketch* (the S1C-ORD analogue; see the honesty note below).

```lean
  have hg : AnalyticAt ℂ (fun w : ℂ => c - w) (c - z) := by fun_prop
  have hg' : deriv (fun w : ℂ => c - w) (c - z) ≠ 0 := by
    rw [deriv_const_sub_id]                    -- Deriv/Add.lean:449 : = -1
    exact neg_ne_zero.mpr one_ne_zero
  simpa only [sub_sub_cancel] using
    analyticOrderAt_comp_of_deriv_ne_zero (f := f) hg hg'   -- Order.lean:561
```

**Beta-redex warning (finding A2 — this is why the closer is `simpa`, not
`rw`).** `analyticOrderAt_comp_of_deriv_ne_zero` concludes
`… = analyticOrderAt f (g z₀)`. Instantiated here, `g z₀` is the **beta-redex**
`(fun w : ℂ => c - w) (c - z)`, *not* the syntactic term `c - (c - z)`.
`rw [sub_sub_cancel]` matches syntactically and can therefore fail outright;
`simp only` beta-reduces first and then matches. Do **not** use the bare
`rw [analyticOrderAt_comp_of_deriv_ne_zero hg hg']; rw [sub_sub_cancel]` form,
and do not use `rw [sub_sub_cancel] at h` on a `have`-bound instance either —
same defect. If `simpa only` misfires, insert `beta_reduce` or a `show
analyticOrderAt f (c - (c - z)) = analyticOrderAt f z` before the `rw`.

### Pinned dependencies (M2)

- `analyticOrderAt_comp_of_deriv_ne_zero` — `Mathlib/Analysis/Analytic/Order.lean:561`.
  Verified verbatim: `(hg : AnalyticAt 𝕜 g z₀) (hg' : deriv g z₀ ≠ 0)
  [CompleteSpace 𝕜] [CharZero 𝕜] : analyticOrderAt (f ∘ g) z₀ = analyticOrderAt f (g z₀)`.
  Its docstring reads *"even if `f` is not analytic"* — the junk-value branch
  is discharged internally at Order.lean:566–567 via
  `analyticAt_comp_iff_of_deriv_ne_zero`
  (`Mathlib/Analysis/Calculus/InverseFunctionTheorem/Analytic.lean:40`). This
  is exactly the three-case split repo:`Conj.lean:357` had to hand-roll, and it
  is the single largest cost difference between the two legs.
  Its `g` is constrained to `g : 𝕜 → 𝕜` by the section variable at
  Order.lean:525 (`variable {f : 𝕜 → E} {g : 𝕜 → 𝕜} {z₀ : 𝕜}`); `fun w : ℂ => c - w`
  satisfies this, and `f` may stay `ℂ → E`. M2's binders are therefore correct
  as written.
- `deriv_const_sub_id` — `Mathlib/Analysis/Calculus/Deriv/Add.lean:449`
  (`deriv (c - ·) x = -1`, `c x : 𝕜` the base field); `@[simp]` twin
  `deriv_const_sub_id'` at :453.
- `sub_sub_cancel` — `Mathlib/Algebra/Group/Basic.lean:933`, the
  `@[to_additive (attr := simp)]` twin of `div_div_cancel (a b : G) : a / (a / b) = b`.
  It is a `simp` lemma, which is what makes the `simpa only` closer above safe.
  **This is the involution identity `c - (c - z) = z`**, i.e. `1 - (1 - z) = z`
  at `c = 1`; it is the whole orientation content of the reflection leg.
- `analyticAt_const` — `Mathlib/Analysis/Analytic/Constructions.lean:54`
  (`@[fun_prop]`); `AnalyticAt.sub` — `Mathlib/Analysis/Analytic/Constructions.lean:187`
  (`@[to_fun (attr := fun_prop)]` at :186, so the lambda-form twin
  `AnalyticAt.fun_sub` also exists); `analyticAt_id` —
  **`Mathlib/Analysis/Analytic/Linear.lean:156`** (`@[fun_prop]` at :155),
  stated for `(id : E → E)`, **not** in `Constructions.lean` (finding A1).
- `CompleteSpace ℂ` — `Mathlib/Analysis/Complex/Basic.lean:124`;
  `CharZero ℂ` — `Mathlib/Data/Complex/Basic.lean:773`. Both are on the
  **base field**, both instances, nothing to build.

### Obligations (M2)

- **S1M-2a** (MEDIUM). The `simpa only [sub_sub_cancel] using …` closer must
  (i) match the goal head against the literal `f ∘ g` of Order.lean:561 with
  `f` supplied by name, and (ii) beta-reduce `(fun w => c - w) (c - z)` before
  `sub_sub_cancel` fires. Fallback: `have h := analyticOrderAt_comp_of_deriv_ne_zero
  (f := f) (g := fun w : ℂ => c - w) (z₀ := c - z) hg hg'` then
  `simp only [sub_sub_cancel] at h; exact h` — note **`simp only`, not `rw`**,
  for the beta reason above. Second fallback for `hg'`:
  `((hasDerivAt_id (c - z)).const_sub c).deriv`.
- **S1M-2b** (LOW). `(fun w : ℂ => c - w)` must be the same term
  `deriv_const_sub_id` is stated at (`c - ·`). It is; if `rw` misfires use
  `simp [deriv_const_sub_id']`.
- **S1M-2c** (LOW, finding A1). `hg` is discharged by `fun_prop` because
  `analyticAt_const` (Constructions.lean:54) and `analyticAt_id` (Linear.lean:156)
  both carry `@[fun_prop]` and `AnalyticAt.sub` carries
  `@[to_fun (attr := fun_prop)]` (Constructions.lean:186). The term-mode form
  `analyticAt_const.sub analyticAt_id` produces `AnalyticAt ℂ ((fun _ => c) - id) (c - z)`
  and matches `fun w : ℂ => c - w` only up to `Pi.instSub`/`id` unfolding — the
  same defeq risk the repo already logged as OBLIG X2-a at repo:`Xi.lean:46`.
  In-Mathlib precedent that the term form does elaborate:
  `Mathlib/Analysis/Analytic/Constructions.lean:857`
  (`analyticAt_const.sub (analyticAt_const.mul analyticAt_id)`). Second
  fallback: `analyticAt_const.fun_sub analyticAt_id`.

*Honesty note — this is NOT a pin gap.* Unlike `S1C-ORD` (where
`starRingEnd ℂ` is antiholomorphic, `AnalyticAt ℂ (starRingEnd ℂ) z` is
**false**, and repo:`Conj.lean:336/357` genuinely had to be built by hand),
`fun w => c - w` is ℂ-analytic with nonvanishing derivative, so the
order-transport content is **already at the pin** at Order.lean:561. M2 is a
*convenience wrapper*, registered as obligation **S1M-ORD** at severity
**LOW**, and its only engineering justification is that it isolates the two
`rw`-fragile steps (the `f ∘ g` syntactic match and `sub_sub_cancel`) into one
place with stated fallbacks, exactly as `Conj.lean` isolated its two lemmas.
**It must not be presented as a missing-Mathlib gap the way S1C-ORD was.**
If M2 fails to elaborate, M3 has an independent route (below) that does not
use it; M2 is then droppable without touching the rest of the package.

---

## M3. ξ reflection order transport `[PIN]` — *the reflection leg*

### Statement

```lean
theorem analyticOrderAt_riemannXi_one_sub (s : ℂ) :
    analyticOrderAt riemannXi (1 - s) = analyticOrderAt riemannXi s
```

### Proof skeleton

*Via M2.*

```lean
  simpa only [riemannXi_comp_one_sub] using
    (analyticOrderAt_comp_const_sub riemannXi 1 s)
```

*Independent route (if M2 is dropped).*

```lean
  have hg : AnalyticAt ℂ (fun w : ℂ => 1 - w) s := by fun_prop
  have hg' : deriv (fun w : ℂ => 1 - w) s ≠ 0 := by
    rw [deriv_const_sub_id]; exact neg_ne_zero.mpr one_ne_zero
  have h := analyticOrderAt_comp_of_deriv_ne_zero (f := riemannXi) hg hg'
  -- h : analyticOrderAt (riemannXi ∘ (1 - ·)) s
  --       = analyticOrderAt riemannXi ((fun w => 1 - w) s)   ← beta-redex, see A2
  rw [riemannXi_comp_one_sub] at h
  exact h.symm
```

*Why the beta-redex of finding A2 is harmless here (unlike in M2).* The redex
sits in the **point argument** and is discharged by `exact`, which works up to
defeq; no syntactic `rw` has to see through it. Only M2 needs a `sub_sub_cancel`
rewrite *at* the redex, which is why only M2's closer had to change.

### Pinned dependencies (M3)

M1, M2 (or Order.lean:561 directly), repo:`Xi.lean:61`.

### Obligations (M3)

- **S1M-3** (LOW): occurrence audit — in the M2 route the rewrite target
  `riemannXi ∘ (1 - ·)` occurs exactly once in the LHS and zero times in the
  point argument `1 - s`, mirroring the audit comment at
  repo:`Conj.lean:443–449`. Fallback is the independent route.

---

### Block B — reflection order transport for ζ, **open strip only** (exit item (a))

## M4. ζ reflection order transport inside the open critical strip `[PIN]`

### Statement

```lean
theorem analyticOrderAt_riemannZeta_one_sub {s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) :
    analyticOrderAt riemannZeta (1 - s) = analyticOrderAt riemannZeta s
```

### Proof skeleton

```lean
  have hre : (1 - s).re = 1 - s.re := by simp [Complex.sub_re, Complex.one_re]
  have h0' : 0 < (1 - s).re := by rw [hre]; linarith
  have h1' : (1 - s).re < 1 := by rw [hre]; linarith
  calc analyticOrderAt riemannZeta (1 - s)
      = analyticOrderAt riemannXi (1 - s) :=
        (analyticOrderAt_riemannXi_eq_riemannZeta h0' h1').symm     -- X11 at 1-s
    _ = analyticOrderAt riemannXi s := analyticOrderAt_riemannXi_one_sub s   -- M3
    _ = analyticOrderAt riemannZeta s :=
        analyticOrderAt_riemannXi_eq_riemannZeta h0 h1              -- X11 at s
```

### Pinned dependencies (M4)

M3; `analyticOrderAt_riemannXi_eq_riemannZeta` repo:`Xi.lean:248`
(verified verbatim: `{s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) :
analyticOrderAt riemannXi s = analyticOrderAt riemannZeta s`);
`Complex.sub_re` — `Mathlib/Data/Complex/Basic.lean:640`;
`Complex.one_re` — `Mathlib/Data/Complex/Basic.lean:147`.

### Obligations (M4)

- **S1M-4** (LOW): the `re` arithmetic; fallback `simp` then
  `constructor <;> linarith`.

**"Where the Γ-factor allows" — the strip hypotheses are not decoration.**
X11 exists only on `0 < re s < 1` because ξ = (Γℝ-factor) · ζ · (unit) holds
with a *nonvanishing* Γℝ cofactor only there (repo:`Xi.lean:239–246`, the X11
docstring). Outside the strip the identity fails as a statement about orders,
not merely as a proof technique: `riemannZeta (-2) = 0`
(`riemannZeta_neg_two_mul_nat_add_one`,
`Mathlib/NumberTheory/LSeries/RiemannZeta.lean:171`, at `n = 0`), so
`analyticOrderAt riemannZeta (-2) ≠ 0` (`AnalyticAt.analyticOrderAt_ne_zero`,
`Mathlib/Analysis/Analytic/Order.lean:137`), while `riemannZeta 3 ≠ 0`
(`riemannZeta_ne_zero_of_one_le_re`,
`Mathlib/NumberTheory/LSeries/Nonvanishing.lean:410`) gives
`analyticOrderAt riemannZeta 3 = 0` (`AnalyticAt.analyticOrderAt_eq_zero`,
Order.lean:133). Since `1 - (-2) = 3`, the naive global form of M4 is
**false**. Any attempt to state M4 without `h0`/`h1` is a **death condition**.

*Do not sharpen this note to "the trivial zeros are simple."* Simplicity of the
trivial zeros is **not** pinned, is not needed for the falsity argument, and
asserting it here would contradict this package's own "No simplicity" claim
boundary. Finding A7.

**Exceptional-point audit for M4 (both sides, junk-value symmetric).** Under
`0 < s.re < 1`: `s ≠ 1` and `s ≠ 0`, and `1 - s` also lies in the open strip
(`hre`), so `1 - s ≠ 1` and `1 - s ≠ 0`. ζ is therefore analytic at **both**
evaluation points (`differentiableAt_riemannZeta`,
`Mathlib/NumberTheory/LSeries/RiemannZeta.lean:137`), and the
`analyticOrderAt` junk value `0` at non-analytic points
(`analyticOrderAt_of_not_analyticAt`, Order.lean:64) is never reached on
either side of the equality. The ζ pole at `1` and the Γℝ poles at
`0, -2, -4, …` are all outside the strip. For ξ (M1–M3, M5, M7, M9–M15) the
question does not arise at all: ξ is entire (repo:`Xi.lean:46`), so
`AnalyticAt ℂ riemannXi z` holds at **every** `z` including `0` and `1`, where
`riemannXi 0 = riemannXi 1 = 1/2 ≠ 0` (repo:`Xi.lean:72,78`) forces
`analyticOrderAt riemannXi 0 = analyticOrderAt riemannXi 1 = 0` — consistent
with M3 at `s = 0`, which is the sharpest available self-check.

---

### Block C — the composite ρ ↦ 1 − conj ρ (barrier exit item (b)) `[CONJ]`

## M5. ξ composite order transport `[CONJ]`

### Statement

```lean
theorem analyticOrderAt_riemannXi_one_sub_conj (s : ℂ) :
    analyticOrderAt riemannXi (1 - (starRingEnd ℂ) s) = analyticOrderAt riemannXi s
```

### Proof skeleton

```lean
  rw [analyticOrderAt_riemannXi_one_sub ((starRingEnd ℂ) s),   -- M3 at conj s
      analyticOrderAt_riemannXi_conj s]                        -- Conj.lean:452
```

### Pinned dependencies (M5)

M3; `analyticOrderAt_riemannXi_conj` repo:`Conj.lean:452` **(merged conjugation
package, PR #307 (`c277b86`), on `main` — a package prerequisite, NOT pinned
Mathlib)**.

### Obligations (M5)

None. The conjugation package is merged (PR #307 (`c277b86`), on `main`), so
no prerequisite is outstanding.

---

## M6. ζ composite order transport, open strip only `[CONJ]`

### Statement

```lean
theorem analyticOrderAt_riemannZeta_one_sub_conj {s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) :
    analyticOrderAt riemannZeta (1 - (starRingEnd ℂ) s) = analyticOrderAt riemannZeta s
```

### Proof skeleton

```lean
  have hc0 : 0 < ((starRingEnd ℂ) s).re := by rwa [Complex.conj_re]
  have hc1 : ((starRingEnd ℂ) s).re < 1 := by rwa [Complex.conj_re]
  rw [analyticOrderAt_riemannZeta_one_sub hc0 hc1,   -- M4 at conj s
      analyticOrderAt_riemannZeta_conj s]            -- Conj.lean:440
```

### Pinned dependencies (M6)

M4; `analyticOrderAt_riemannZeta_conj` repo:`Conj.lean:440` **(merged
conjugation package, PR #307 (`c277b86`), on `main`)**;
`Complex.conj_re` — `Mathlib/Data/Complex/Basic.lean:467`. The `hc0`/`hc1`
idiom is verbatim the one already used at repo:`Conj.lean:310–311`
(re-verified).

### Obligations (M6)

None. The conjugation package is merged (PR #307 (`c277b86`), on `main`), so
no prerequisite is outstanding.

**Composite commutation check (attack front 4).** M5/M6 apply the reflection leg
**at `conj s`** and then the conjugation leg **at `s`**. Both legs are
universally quantified in their point argument, so the instantiation is
legitimate and the two rewrites commute: applying conjugation first (at
`1 - s`, via `analyticOrderAt_riemannXi_conj (1 - s)` plus
`(starRingEnd ℂ) (1 - s) = 1 - (starRingEnd ℂ) s`) reaches the same identity.
The skeleton's order is preferred only because it needs no `map_sub`/`map_one`
normalization step. The reflection map is an involution
(`sub_sub_cancel`, Algebra/Group/Basic.lean:933) and conjugation is an
involution (`Complex.conj_conj`), and they commute as maps on ℂ, so the group
generated is the Klein four-group acting on `{ρ, 1-ρ, conj ρ, 1-conj ρ}` — M7/M8
are exactly the orbit statement for that action, with **no orientation
subtlety**: `analyticOrderAt_comp_of_deriv_ne_zero` (Order.lean:561) is
insensitive to the *sign* of `deriv g z₀`, requiring only `≠ 0`, and
`deriv (1 - ·) = -1 ≠ 0` (Deriv/Add.lean:449).

---

## M7. ξ fourfold order action `[CONJ]`

### Statement and proof skeleton

```lean
theorem analyticOrderAt_riemannXi_fourfold (s : ℂ) :
    analyticOrderAt riemannXi (1 - s) = analyticOrderAt riemannXi s ∧
    analyticOrderAt riemannXi ((starRingEnd ℂ) s) = analyticOrderAt riemannXi s ∧
    analyticOrderAt riemannXi (1 - (starRingEnd ℂ) s) = analyticOrderAt riemannXi s :=
  ⟨analyticOrderAt_riemannXi_one_sub s,
   analyticOrderAt_riemannXi_conj s,
   analyticOrderAt_riemannXi_one_sub_conj s⟩
```

### Pinned dependencies (M7)

M3, M5; `analyticOrderAt_riemannXi_conj` repo:`Conj.lean:452` **(merged
conjugation package, PR #307 (`c277b86`), on `main`)**.

*Notes.* Deliberately shaped as the order-level analogue of
`riemannZeta_fourfold_zero` (repo:`Conj.lean:306`): the built package says the
four points are *zeros together*; M7 says they are zeros **of the same
multiplicity**. That upgrade is the barrier's exit sentence.

### Obligations (M7)

None. The conjugation package is merged (PR #307 (`c277b86`), on `main`), so
no prerequisite is outstanding.

---

## M8. ζ fourfold order action, open strip only `[CONJ]`

### Statement and proof skeleton

```lean
theorem analyticOrderAt_riemannZeta_fourfold {s : ℂ} (h0 : 0 < s.re) (h1 : s.re < 1) :
    analyticOrderAt riemannZeta (1 - s) = analyticOrderAt riemannZeta s ∧
    analyticOrderAt riemannZeta ((starRingEnd ℂ) s) = analyticOrderAt riemannZeta s ∧
    analyticOrderAt riemannZeta (1 - (starRingEnd ℂ) s) = analyticOrderAt riemannZeta s :=
  ⟨analyticOrderAt_riemannZeta_one_sub h0 h1,
   analyticOrderAt_riemannZeta_conj s,
   analyticOrderAt_riemannZeta_one_sub_conj h0 h1⟩
```

### Pinned dependencies (M8)

M4, M6; `analyticOrderAt_riemannZeta_conj` repo:`Conj.lean:440` **(merged
conjugation package, PR #307 (`c277b86`), on `main`)**.

*Note.* The conjugation leg needs no strip hypothesis (repo:`Conj.lean:440` is
global); the two reflection legs do. Keep the hypotheses on the theorem
rather than weakening the middle conjunct.

### Obligations (M8)

None. The conjugation package is merged (PR #307 (`c277b86`), on `main`), so
no prerequisite is outstanding.

---

### Block D — the ξ divisor object and its symmetries (exit item (d))

## M9. ξ is analytic / meromorphic on every set `[PIN]`

### Statement and proof skeleton

```lean
theorem analyticOnNhd_riemannXi (U : Set ℂ) : AnalyticOnNhd ℂ riemannXi U :=
  (analyticOnNhd_univ_iff_differentiable.mpr differentiable_riemannXi).mono (Set.subset_univ U)

theorem meromorphicOn_riemannXi (U : Set ℂ) : MeromorphicOn riemannXi U :=
  (analyticOnNhd_riemannXi U).meromorphicOn
```

### Pinned dependencies (M9)

repo:`Xi.lean:46`;
`analyticOnNhd_univ_iff_differentiable` — `Mathlib/Analysis/Complex/CauchyIntegral.lean:678`,
declared **inside `namespace Complex`** (opened :173, closed :770), so the
fully-qualified name is `Complex.analyticOnNhd_univ_iff_differentiable` and the
bare spelling in the skeleton above depends on the preamble's `open Complex`;
`AnalyticOnNhd.mono` — `Mathlib/Analysis/Analytic/Basic.lean:498`;
`AnalyticOnNhd.meromorphicOn` — `Mathlib/Analysis/Meromorphic/Basic.lean:475`.

### Obligations (M9)

- **S1M-9** (LOW): `analyticOnNhd_univ_iff_differentiable` is stated
  for `{f : ℂ → E}` with `E` a normed space; `E := ℂ` must unify. Fallback:
  `fun z _ => ((differentiable_riemannXi.differentiableOn).analyticAt
  (isOpen_univ.mem_nhds (Set.mem_univ z)))` via CauchyIntegral.lean:625.

---

## M10. Divisor evaluation bridge `[PIN]` — the carrier seam

### Statement and proof skeleton

```lean
theorem riemannXi_divisor_apply {U : Set ℂ} {z : ℂ} (hz : z ∈ U) :
    MeromorphicOn.divisor riemannXi U z = ((analyticOrderAt riemannXi z).map (↑)).untop₀ :=
  MeromorphicOn.AnalyticOnNhd.divisor_apply (analyticOnNhd_riemannXi U) hz
```

### Pinned dependencies (M10)

M9; `MeromorphicOn.AnalyticOnNhd.divisor_apply` —
`Mathlib/Analysis/Meromorphic/Divisor.lean:71` **(note the
`MeromorphicOn.` prefix — see §1 naming trap)**;
`WithTop.untop₀` — `Mathlib/Algebra/Order/WithTop/Untop0.lean:30`.

### Obligations (M10)

- **S1M-10** (MEDIUM): the coercion `(↑)` in `.map (↑)` is
  `Nat.cast : ℕ → ℤ`, mapping `ℕ∞ → WithTop ℤ`. It must elaborate identically on
  both sides. Fallback: state the RHS as
  `((analyticOrderAt riemannXi z).map (Nat.cast : ℕ → ℤ)).untop₀`, or route
  through `MeromorphicOn.divisor_apply` (Divisor.lean:68) plus
  `AnalyticAt.meromorphicOrderAt_eq` (`Mathlib/Analysis/Meromorphic/Order.lean:279`).

---

## M11. The ξ divisor is effective (non-negative) `[PIN]`

### Statement and proof skeleton

```lean
theorem riemannXi_divisor_nonneg (U : Set ℂ) :
    0 ≤ MeromorphicOn.divisor riemannXi U :=
  MeromorphicOn.AnalyticOnNhd.divisor_nonneg (analyticOnNhd_riemannXi U)
```

### Pinned dependencies (M11)

M9; `MeromorphicOn.AnalyticOnNhd.divisor_nonneg` —
`Mathlib/Analysis/Meromorphic/Divisor.lean:177` (same naming trap).
The `≤` is the pointwise order from `Mathlib/Topology/LocallyFinsupp.lean:401`.
Semantic content: ξ has zeros, no poles — the divisor is a *zero* divisor.

### Obligations (M11)

None.

---

## M12. ξ has finite local analytic order at every point `[PIN]` — **THE MAIN OBLIGATION (S1M-FIN)**

### Statement

```lean
theorem analyticOrderAt_riemannXi_ne_top (z : ℂ) : analyticOrderAt riemannXi z ≠ ⊤

theorem meromorphicOrderAt_riemannXi_ne_top (z : ℂ) : meromorphicOrderAt riemannXi z ≠ ⊤
```

**Reading of "order" (fixed once, for the whole package).** Throughout this
contract "order" means the **local analytic order at a point**
(`analyticOrderAt`, `ℕ∞`-valued, Order.lean:47) or the **local meromorphic
order at a point** (`meromorphicOrderAt`, `WithTop ℤ`-valued,
Meromorphic/Order.lean:47). The first statement above says ξ's local analytic
order at `z` is finite (`≠ ⊤`), i.e. ξ does not vanish identically near `z`;
the second says the same for the local meromorphic order. Neither is a
statement about the **growth order of an entire function** — that notion is
nowhere in this package, is a `S1-GLOBAL-ZEROS` / Hadamard-side object, and is
excluded by death condition 4.

### Proof skeleton

*First.*

```lean
  have hA : ∀ z₀ : ℂ, AnalyticAt ℂ riemannXi z₀ :=
    fun z₀ => analyticOnNhd_riemannXi Set.univ z₀ (Set.mem_univ z₀)
  intro htop
  have hzero : riemannXi = 0 :=
    (AnalyticOnNhd.analyticOrderAt_eq_top_iff_eq_zero z hA).mp htop
  have h0 : riemannXi 0 = 0 := congrFun hzero 0
  rw [riemannXi_zero] at h0        -- (1/2 : ℂ) = 0
  norm_num at h0
```

*Second.*

```lean
  rw [(analyticOnNhd_riemannXi Set.univ z (Set.mem_univ z)).meromorphicOrderAt_eq]
  exact fun h => analyticOrderAt_riemannXi_ne_top z (ENat.map_eq_top_iff.mp h)
```

### Pinned dependencies (M12)

- **`AnalyticOnNhd.analyticOrderAt_eq_top_iff_eq_zero`** —
  `Mathlib/Analysis/Analytic/Order.lean:687`, verified verbatim at the pin:
  `lemma analyticOrderAt_eq_top_iff_eq_zero [PreconnectedSpace 𝕜] {f : 𝕜 → E}
  (z : 𝕜) (hf : ∀ z₀, AnalyticAt 𝕜 f z₀) : analyticOrderAt f z = ⊤ ↔ f = 0`,
  declared **inside `namespace AnalyticOnNhd`** (opened Order.lean:575, closed
  Order.lean:700). Two qualifications that must be carried at every use site:
  (i) the fully-qualified name is
  `AnalyticOnNhd.analyticOrderAt_eq_top_iff_eq_zero`, not the bare
  `analyticOrderAt_eq_top_iff_eq_zero`; (ii) despite living in that namespace
  the lemma takes **no `AnalyticOnNhd` argument** — its hypotheses are the
  instance `[PreconnectedSpace 𝕜]` and *pointwise analyticity at every point of
  the whole space*, `hf : ∀ z₀, AnalyticAt 𝕜 f z₀` — so dot notation
  `hf.analyticOrderAt_eq_top_iff_eq_zero` on an `AnalyticOnNhd` hypothesis does
  **not** resolve (the §1 naming trap, second instance). Its conclusion is the
  *global* `f = 0`, not an `EqOn` on a subset; M12 supplies `hf` from M9 at
  `Set.univ` and refutes `riemannXi = 0` by `riemannXi 0 = 1/2`.
- `riemannXi_zero` — repo:`Xi.lean:72` (`riemannXi 0 = 1/2`).
- `AnalyticAt.meromorphicOrderAt_eq` — `Mathlib/Analysis/Meromorphic/Order.lean:279`.
- `ENat.map_eq_top_iff` — `Mathlib/Data/ENat/Basic.lean:526`
  (`map f n = ⊤ ↔ n = ⊤`). **Precedent**: Mathlib itself uses exactly this
  lemma in exactly this position at `Mathlib/Analysis/Meromorphic/Order.lean:71`.

### Obligations (M12)

- **S1M-FIN** (**HIGH — the package's main obligation**). Read the `FIN` as
  *finiteness of the local analytic order at a point* (`analyticOrderAt … ≠ ⊤`)
  and never as finiteness of a growth order. Without M12, the
  `untop₀` totalization makes `divisor riemannXi U z = 0` ambiguous between
  "not a zero" and "identically zero nearby", and M13 is false-shaped. M12 is
  what licenses reading the divisor as a multiplicity function at all. It is
  the S1-MULTIPLICITY analogue of the S0-SEMANTIC totalization discharge that
  `Xi.lean` already performs. **Not optional; land M12 before M13.**
- **S1M-12a** (MEDIUM): `PreconnectedSpace ℂ` must resolve by instance search
  (`NormedSpace.instPathConnectedSpace`,
  `Mathlib/Analysis/Normed/Module/Convex.lean:168` (priority 100) →
  `ConnectedSpace` → `PreconnectedSpace`). Narrow instance check required —
  do not assume.

  **Fallback (corrected — finding A3).** Both fallbacks previously recorded
  here were defective. The valid route needs a *finite-local-analytic-order
  witness* (`analyticOrderAt riemannXi 0 ≠ ⊤`) first:

  ```lean
  have hA0 : AnalyticAt ℂ riemannXi 0 := analyticOnNhd_riemannXi Set.univ 0 (Set.mem_univ 0)
  have hw : analyticOrderAt riemannXi 0 ≠ ⊤ := by
    rw [hA0.analyticOrderAt_eq_zero.mpr (by rw [riemannXi_zero]; norm_num)]  -- Order.lean:133
    exact (by simp)                                    -- (0 : ℕ∞) ≠ ⊤
  exact AnalyticOnNhd.analyticOrderAt_ne_top_of_isPreconnected
    (analyticOnNhd_riemannXi Set.univ) isPreconnected_univ (Set.mem_univ 0) (Set.mem_univ z) hw
  ```

  `AnalyticOnNhd.analyticOrderAt_ne_top_of_isPreconnected` —
  `Mathlib/Analysis/Analytic/Order.lean:624`, verified verbatim:
  `{x y : 𝕜} (hf : AnalyticOnNhd 𝕜 f U) (hU : IsPreconnected U) (h₁x : x ∈ U)
  (hy : y ∈ U) (h₂x : analyticOrderAt f x ≠ ⊤) : analyticOrderAt f y ≠ ⊤`.
  (`namespace AnalyticOnNhd` opens at Order.lean:575 and closes at :700, so the
  qualified name is correct.)
  `AnalyticAt.analyticOrderAt_eq_zero` — Order.lean:133 (`protected`, dot
  notation still resolves), `analyticOrderAt f z₀ = 0 ↔ f z₀ ≠ 0`.
  Second fallback: `AnalyticOnNhd.exists_analyticOrderAt_ne_top_iff_forall`
  (Order.lean:614), which needs `IsConnected U` (i.e. `isConnected_univ`), same
  witness `hw`.

  **Two routes that do NOT work and must not be re-recorded (A3).**
  (i) `IsOpen.forall_analyticOrderAt_eq_top_iff_eqOn_zero` (Order.lean:693) has
  the shape `(∀ z ∈ s, analyticOrderAt f z = ⊤) ↔ EqOn f 0 s`; its forward
  direction consumes a **universally quantified** hypothesis, whereas M12
  supplies `⊤` at a *single* point. It is not a drop-in.
  (ii) `analyticOrderAt_ne_top_of_isPreconnected` "with the witness point `0`"
  is incomplete as previously written: the lemma's fifth argument *is* the
  finite-local-analytic-order fact at the witness
  (`analyticOrderAt riemannXi 0 ≠ ⊤`), which has to be produced from
  `riemannXi_zero` as above — it is not free.
- **S1M-12b** (LOW): `norm_num` closing `(1/2 : ℂ) = 0`. Fallback:
  `exact absurd h0 (by norm_num)` or `simp at h0`.

---

## M13. Divisor support **is** the ξ zero set `[PIN]`

### Statement and proof skeleton

```lean
theorem riemannXi_divisor_support (U : Set ℂ) :
    Function.support (MeromorphicOn.divisor riemannXi U) = U ∩ riemannXi ⁻¹' {0} :=
  ((analyticOnNhd_riemannXi U).meromorphicNFOn.zero_set_eq_divisor_support
    (fun u => meromorphicOrderAt_riemannXi_ne_top (u : ℂ))).symm
```

### Pinned dependencies (M13)

M9, M12;
`AnalyticOnNhd.meromorphicNFOn` — `Mathlib/Analysis/Meromorphic/NormalForm.lean:567`;
`MeromorphicNFOn.zero_set_eq_divisor_support` —
`Mathlib/Analysis/Meromorphic/NormalForm.lean:578`, verified verbatim:
`(h₁f : MeromorphicNFOn f U) (h₂f : ∀ u : U, meromorphicOrderAt f u ≠ ⊤) :
U ∩ f ⁻¹' {0} = Function.support (MeromorphicOn.divisor f U)`.

### Obligations (M13)

- **S1M-13** (MEDIUM): the pinned hypothesis is subtype-bound (`∀ u : U`), so
  the M12 instance needs the coercion `(u : ℂ)`; and the pinned conclusion is
  oriented `U ∩ f ⁻¹' {0} = support`, hence the `.symm`. Fallback: state M13 in
  the pinned orientation instead of flipping it.

*Why this statement is in scope.* It is what makes "divisor" mean anything for
this barrier: the capability-map row says *the zero set loses analytic
multiplicity*. M13 + M10 together say the divisor is exactly the zero set
**decorated with its multiplicity**. Without M13 the divisor is an
uninterpreted `locallyFinsuppWithin` object.

---

## M14. Divisor reflection invariance `[PIN]`

### Statement

Generic form (symmetric `U`), then the two instances:

```lean
theorem riemannXi_divisor_one_sub {U : Set ℂ}
    (hU : ∀ z : ℂ, (1 - z) ∈ U ↔ z ∈ U) (s : ℂ) :
    MeromorphicOn.divisor riemannXi U (1 - s) = MeromorphicOn.divisor riemannXi U s

theorem riemannXi_divisor_univ_one_sub (s : ℂ) :
    MeromorphicOn.divisor riemannXi Set.univ (1 - s)
      = MeromorphicOn.divisor riemannXi Set.univ s

theorem riemannXi_divisor_strip_one_sub (s : ℂ) :
    MeromorphicOn.divisor riemannXi {z : ℂ | 0 < z.re ∧ z.re < 1} (1 - s)
      = MeromorphicOn.divisor riemannXi {z : ℂ | 0 < z.re ∧ z.re < 1} s
```

### Proof skeleton

*Generic.*

```lean
  by_cases hs : s ∈ U
  · rw [riemannXi_divisor_apply ((hU s).mpr hs), riemannXi_divisor_apply hs,
        analyticOrderAt_riemannXi_one_sub s]                       -- M10, M10, M3
  · rw [Function.locallyFinsuppWithin.apply_eq_zero_of_notMem _ (fun h => hs ((hU s).mp h)),
        Function.locallyFinsuppWithin.apply_eq_zero_of_notMem _ hs]
```

*Univ instance.* `riemannXi_divisor_one_sub (fun z => by simp) s`.

*Strip instance.*

```lean
  refine riemannXi_divisor_one_sub (fun z => ?_) s
  simp only [Set.mem_setOf_eq, Complex.sub_re, Complex.one_re]
  constructor <;> (rintro ⟨a, b⟩; exact ⟨by linarith, by linarith⟩)
```

### Pinned dependencies (M14)

M3, M9, M10;
`Function.locallyFinsuppWithin.apply_eq_zero_of_notMem` —
`Mathlib/Topology/LocallyFinsupp.lean:197`;
`FunLike` instance at LocallyFinsupp.lean:125.

### Obligations (M14)

- **S1M-14a** (LOW). Note M14 needs **no** `≠ ⊤` hypothesis: it is
  `congrArg untop₀ ∘ congrArg (·.map ↑)` applied to M3, and equal orders give
  equal `untop₀` regardless of finiteness. M12 is required for M13, **not**
  for M14/M15 — this deliberately decouples the risky obligation from the
  exit-evidence symmetries.
- **S1M-14b** (LOW). The strip-symmetry side goal
  `0 < (1-z).re ∧ (1-z).re < 1 ↔ 0 < z.re ∧ z.re < 1`. Fallback:
  `simp [Complex.sub_re, Complex.one_re]; constructor <;> intro h <;>
   omega`-style is wrong over `ℝ`; use `constructor <;> intro h <;>
   exact ⟨by linarith [h.1, h.2], by linarith [h.1, h.2]⟩`.

*Design note.* This is stated **pointwise**, not as an equality of
`locallyFinsuppWithin` terms, because the pin has no pullback along a self-map
(§1 item 5). A `locallyFinsuppWithin`-level equality would require a new
`comap` definition; see **DEFERRED-1**.

---

## M15. Divisor conjugation and composite invariance `[CONJ]`

### Statement

```lean
theorem riemannXi_divisor_conj {U : Set ℂ}
    (hU : ∀ z : ℂ, (starRingEnd ℂ) z ∈ U ↔ z ∈ U) (s : ℂ) :
    MeromorphicOn.divisor riemannXi U ((starRingEnd ℂ) s)
      = MeromorphicOn.divisor riemannXi U s

theorem riemannXi_divisor_univ_conj (s : ℂ) :
    MeromorphicOn.divisor riemannXi Set.univ ((starRingEnd ℂ) s)
      = MeromorphicOn.divisor riemannXi Set.univ s

theorem riemannXi_divisor_strip_conj (s : ℂ) :
    MeromorphicOn.divisor riemannXi {z : ℂ | 0 < z.re ∧ z.re < 1} ((starRingEnd ℂ) s)
      = MeromorphicOn.divisor riemannXi {z : ℂ | 0 < z.re ∧ z.re < 1} s

theorem riemannXi_divisor_one_sub_conj {U : Set ℂ}
    (hU₁ : ∀ z : ℂ, (1 - z) ∈ U ↔ z ∈ U)
    (hU₂ : ∀ z : ℂ, (starRingEnd ℂ) z ∈ U ↔ z ∈ U) (s : ℂ) :
    MeromorphicOn.divisor riemannXi U (1 - (starRingEnd ℂ) s)
      = MeromorphicOn.divisor riemannXi U s

theorem riemannXi_divisor_univ_one_sub_conj (s : ℂ) :
    MeromorphicOn.divisor riemannXi Set.univ (1 - (starRingEnd ℂ) s)
      = MeromorphicOn.divisor riemannXi Set.univ s

theorem riemannXi_divisor_strip_one_sub_conj (s : ℂ) :
    MeromorphicOn.divisor riemannXi {z : ℂ | 0 < z.re ∧ z.re < 1} (1 - (starRingEnd ℂ) s)
      = MeromorphicOn.divisor riemannXi {z : ℂ | 0 < z.re ∧ z.re < 1} s
```

The four instances carry M14's carrier sets (`Set.univ` and the open-strip
literal `{z : ℂ | 0 < z.re ∧ z.re < 1}`) and M14's `_univ_`/`_strip_` naming.
They were previously mandated here in prose only ("with the same `Set.univ` and
open-strip instances as M14"); they are now spelled explicitly above, so the
contract states every signature it requires. The strip is conj-stable because
`((starRingEnd ℂ) z).re = z.re` (`Complex.conj_re`,
`Mathlib/Data/Complex/Basic.lean:467`), and 1-reflection-stable by the same
`re` arithmetic M14 uses.

### Proof skeleton

*Generic (both).* Identical to M14's generic skeleton with
`analyticOrderAt_riemannXi_conj` (repo:`Conj.lean:452`) resp.
`analyticOrderAt_riemannXi_one_sub_conj` (M5) in place of M3. For
`riemannXi_divisor_one_sub_conj` the `∉ U` branch needs both hypotheses
chained: from `h : (1 - (starRingEnd ℂ) s) ∈ U`, `hU₁ ((starRingEnd ℂ) s)`
gives `(starRingEnd ℂ) s ∈ U` and `hU₂ s` then gives `s ∈ U`, contradicting
`hs`. Neither symmetry alone stabilizes `1 - conj ·`.

*Univ instances.* `riemannXi_divisor_conj (fun z => by simp) s`, resp.
`riemannXi_divisor_one_sub_conj (fun z => by simp) (fun z => by simp) s`.

*Strip instances.*

```lean
  -- riemannXi_divisor_strip_conj
  refine riemannXi_divisor_conj (fun z => ?_) s
  simp only [Set.mem_setOf_eq, Complex.conj_re]

  -- riemannXi_divisor_strip_one_sub_conj
  refine riemannXi_divisor_one_sub_conj (fun z => ?_) (fun z => ?_) s
  · simp only [Set.mem_setOf_eq, Complex.sub_re, Complex.one_re]
    constructor <;> (rintro ⟨a, b⟩; exact ⟨by linarith, by linarith⟩)
  · simp only [Set.mem_setOf_eq, Complex.conj_re]
```

### Pinned dependencies (M15)

M5, M10, M14 pattern; `analyticOrderAt_riemannXi_conj`
repo:`Conj.lean:452` **(merged conjugation package, PR #307 (`c277b86`), on
`main`)**; `Complex.conj_re` —
`Mathlib/Data/Complex/Basic.lean:467`. The four instances additionally use
`Complex.sub_re` — `Mathlib/Data/Complex/Basic.lean:640` — and
`Complex.one_re` — `Mathlib/Data/Complex/Basic.lean:147` — in the
`_strip_one_sub_conj` side goal, exactly as M14's strip instance does.

### Obligations (M15)

Same class as S1M-14a/S1M-14b. No package prerequisite is outstanding: the
conjugation package is merged (PR #307 (`c277b86`), on `main`). Specifically:

- **S1M-15a** (LOW). Like M14, none of the six needs a `≠ ⊤` hypothesis: each
  is `congrArg untop₀ ∘ congrArg (·.map ↑)` applied to an order identity, and
  equal orders give equal `untop₀` regardless of finiteness. M12 is required
  for M13, **not** for M14/M15.
- **S1M-15b** (LOW). The conj side goal
  `0 < ((starRingEnd ℂ) z).re ∧ ((starRingEnd ℂ) z).re < 1 ↔ 0 < z.re ∧ z.re < 1`.
  After `Complex.conj_re` both sides are literally `0 < z.re ∧ z.re < 1`;
  `simp only` closes the `Iff` only if it reduces `P ↔ P` (`iff_self` is not in
  a `simp only` set). Fallback: append `exact Iff.rfl`.
- **S1M-15c** (LOW). The reflection side goal of
  `riemannXi_divisor_strip_one_sub_conj` is M14's S1M-14b goal verbatim; it is
  over `ℝ`, so `omega` is wrong and `linarith` is the tool. Fallback:
  `constructor <;> intro h <;> exact ⟨by linarith [h.1, h.2], by linarith [h.1, h.2]⟩`.

*Note.* M14 + M15 give the ξ half of the capability-map's exit phrase
"multiplicity-preserving divisor symmetries" under the three maps `ρ ↦ 1-ρ`,
`ρ ↦ conj ρ`, `ρ ↦ 1 - conj ρ`, at the divisor level rather than only at
zero-membership level. The **ζ half** is Block E (finding A5).

---

### Block E — the ζ divisor on the open strip (exit item (d), ζ half) `[CONJ]` for M17b/c

Write `Ω := {z : ℂ | 0 < z.re ∧ z.re < 1}` (inline set-builder literal at each
use site, never a `def`).

**Why this block exists (finding A5).** The capability-map row
(repo:`domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md:386`) names its
remaining exit evidence as a "**zeta/xi** divisor interface and
multiplicity-preserving divisor symmetries". The original DEFERRED-3 dropped
the ζ half on the grounds that "ζ has a pole at `1`, so its divisor is
genuinely meromorphic (`negPart ≠ 0`)". That rationale is **false on Ω**:
`1 ∉ Ω`, ζ is analytic on Ω, and the ξ pattern transfers verbatim with no new
analysis. Deferring the ζ half would have left the exit item only half met
while the claim boundary said it was closed.

## M16. ζ is analytic on Ω; the ζ divisor on Ω `[PIN]`

### Statement

```lean
theorem analyticOnNhd_riemannZeta_strip :
    AnalyticOnNhd ℂ riemannZeta {z : ℂ | 0 < z.re ∧ z.re < 1}

theorem meromorphicOn_riemannZeta_strip :
    MeromorphicOn riemannZeta {z : ℂ | 0 < z.re ∧ z.re < 1} :=
  analyticOnNhd_riemannZeta_strip.meromorphicOn

theorem riemannZeta_divisor_strip_apply {z : ℂ} (hz : z ∈ {w : ℂ | 0 < w.re ∧ w.re < 1}) :
    MeromorphicOn.divisor riemannZeta {w : ℂ | 0 < w.re ∧ w.re < 1} z
      = ((analyticOrderAt riemannZeta z).map (↑)).untop₀ :=
  MeromorphicOn.AnalyticOnNhd.divisor_apply analyticOnNhd_riemannZeta_strip hz

theorem riemannZeta_divisor_strip_nonneg :
    0 ≤ MeromorphicOn.divisor riemannZeta {w : ℂ | 0 < w.re ∧ w.re < 1} :=
  MeromorphicOn.AnalyticOnNhd.divisor_nonneg analyticOnNhd_riemannZeta_strip
```

### Proof skeleton

*First.*

```lean
  have hopen : IsOpen {z : ℂ | 0 < z.re ∧ z.re < 1} :=
    (isOpen_lt continuous_const Complex.continuous_re).inter
      (isOpen_lt Complex.continuous_re continuous_const)
  intro z hz
  refine DifferentiableOn.analyticAt (fun w hw => ?_) (hopen.mem_nhds hz)
  exact (differentiableAt_riemannZeta (fun e => by simp [e] at hw)).differentiableWithinAt
```

### Pinned dependencies (M16)

`differentiableAt_riemannZeta` —
`Mathlib/NumberTheory/LSeries/RiemannZeta.lean:137`, verified verbatim:
`{s : ℂ} (hs' : s ≠ 1) : DifferentiableAt ℂ riemannZeta s`;
`DifferentiableOn.analyticAt` — `Mathlib/Analysis/Complex/CauchyIntegral.lean:625`
(`protected`, `_root_`; dot notation resolves);
`MeromorphicOn.AnalyticOnNhd.divisor_apply` / `_nonneg` —
`Mathlib/Analysis/Meromorphic/Divisor.lean:71` / `:177` (§1 naming trap);
`AnalyticOnNhd.meromorphicOn` — `Mathlib/Analysis/Meromorphic/Basic.lean:475`;
`Complex.continuous_re` — `Mathlib/Analysis/Complex/Basic.lean:153`.

### Obligations (M16)

- **S1M-16a** (MEDIUM): `IsOpen ({z | 0 < z.re} ∩ {z | z.re < 1})` must unify
  with `IsOpen {z | 0 < z.re ∧ z.re < 1}` (`Set.inter` of `setOf` vs `setOf` of
  `∧`) — defeq, but `exact`-level. Fallback: the repo's own idiom at
  repo:`Xi.lean:255` (`isOpen_lt continuous_const Complex.continuous_re`; also
  at repo:`Xi.lean:309`) plus `Set.setOf_and` / `simp only [Set.setOf_and]`.

  *Skeleton-vs-draft delta (proof engineering only; the M16 statement is
  unaffected).* The skeleton above spells the witness with `.inter`. The
  drafts-lane mirror `drafts/RiemannMult.lean` instead spells it with `.and`,
  which is the form already built and merged in the xi module at
  repo:`Xi.lean:308–310` (recorded there as "fix F3 (a) discharged
  syntactically") and which needs no `∩`-vs-set-builder unfolding. Either
  spelling is admissible under §Return-to-stage-one condition, since neither
  changes a signature; whichever CI accepts is the one the stage-two promotion
  records.
- **S1M-16b** (LOW): `w ≠ 1` from `hw`. Fallback is the repo idiom
  `fun e => by simp [e] at hw` used at repo:`Xi.lean:250–251` (also at
  repo:`Xi.lean:214–215`, `:233–234`, `:318–319`).

**No pole bookkeeping is needed and none is smuggled in.** `1 ∉ Ω` because
`(1 : ℂ).re = 1` (`Complex.one_re`, Data/Complex/Basic.lean:147) is not `< 1`.
`negPart (divisor riemannZeta Ω) = 0` follows from `riemannZeta_divisor_strip_nonneg`;
nothing here says anything about ζ's divisor on a set containing `1`
(DEFERRED-3, restated).

## M16'. ζ has finite local analytic order at every point of Ω `[PIN]` — free from X11 + M12

### Statement and proof skeleton

```lean
theorem analyticOrderAt_riemannZeta_ne_top_of_mem_strip
    {z : ℂ} (h0 : 0 < z.re) (h1 : z.re < 1) : analyticOrderAt riemannZeta z ≠ ⊤ :=
  (analyticOrderAt_riemannXi_eq_riemannZeta h0 h1) ▸ analyticOrderAt_riemannXi_ne_top z

theorem meromorphicOrderAt_riemannZeta_ne_top_of_mem_strip
    {z : ℂ} (h0 : 0 < z.re) (h1 : z.re < 1) : meromorphicOrderAt riemannZeta z ≠ ⊤
```

### Pinned dependencies (M16')

M12; `analyticOrderAt_riemannXi_eq_riemannZeta` repo:`Xi.lean:248` (X11);
`AnalyticAt.meromorphicOrderAt_eq` — `Mathlib/Analysis/Meromorphic/Order.lean:279`;
`ENat.map_eq_top_iff` — `Mathlib/Data/ENat/Basic.lean:526`.

*Note.* This costs **nothing new**: X11 (repo:`Xi.lean:248`) transports M12's
finiteness of the **local analytic order at a point** (first statement) and of
the **local meromorphic order at a point** (second statement) from ξ to ζ
inside the strip; no growth order of any function is involved anywhere in the
transport. No nonvanishing witness for ζ on Ω has
to be produced, and in particular **no zero-free region, no growth bound, and
no unproved analytic input** enters. The second statement mirrors M12's second
via `AnalyticAt.meromorphicOrderAt_eq` and `ENat.map_eq_top_iff`.

### Obligations (M16')

- **S1M-16c** (LOW): the `▸` direction. Fallback:
  `rw [← analyticOrderAt_riemannXi_eq_riemannZeta h0 h1]; exact analyticOrderAt_riemannXi_ne_top z`.

## M16''. ζ divisor support on Ω `[PIN]`

### Statement

```lean
theorem riemannZeta_divisor_strip_support :
    Function.support (MeromorphicOn.divisor riemannZeta {z : ℂ | 0 < z.re ∧ z.re < 1})
      = {z : ℂ | 0 < z.re ∧ z.re < 1} ∩ riemannZeta ⁻¹' {0}
```

### Proof skeleton

M13's, with `analyticOnNhd_riemannZeta_strip.meromorphicNFOn`
(NormalForm.lean:567) and the subtype-bound hypothesis discharged by
`fun u => meromorphicOrderAt_riemannZeta_ne_top_of_mem_strip u.2.1 u.2.2`, then
`.symm` (NormalForm.lean:578 is oriented `U ∩ f ⁻¹' {0} = support`).

### Pinned dependencies (M16'')

M16, M16'; `AnalyticOnNhd.meromorphicNFOn` —
`Mathlib/Analysis/Meromorphic/NormalForm.lean:567`;
`MeromorphicNFOn.zero_set_eq_divisor_support` — `…/NormalForm.lean:578`.

### Obligations (M16'')

- **S1M-16d** (MEDIUM): the subtype projection `u.2.1` / `u.2.2`
  must see through `u : ↥{z | 0 < z.re ∧ z.re < 1}`. Fallback:
  `fun u => by obtain ⟨w, hw⟩ := u; exact meromorphicOrderAt_riemannZeta_ne_top_of_mem_strip hw.1 hw.2`.

## M17. ζ divisor symmetries on Ω

### Statement

```lean
theorem riemannZeta_divisor_strip_one_sub (s : ℂ) :
    MeromorphicOn.divisor riemannZeta {z : ℂ | 0 < z.re ∧ z.re < 1} (1 - s)
      = MeromorphicOn.divisor riemannZeta {z : ℂ | 0 < z.re ∧ z.re < 1} s          -- [PIN]

theorem riemannZeta_divisor_strip_conj (s : ℂ) :
    MeromorphicOn.divisor riemannZeta {z : ℂ | 0 < z.re ∧ z.re < 1} ((starRingEnd ℂ) s)
      = MeromorphicOn.divisor riemannZeta {z : ℂ | 0 < z.re ∧ z.re < 1} s          -- [CONJ]

theorem riemannZeta_divisor_strip_one_sub_conj (s : ℂ) :
    MeromorphicOn.divisor riemannZeta {z : ℂ | 0 < z.re ∧ z.re < 1} (1 - (starRingEnd ℂ) s)
      = MeromorphicOn.divisor riemannZeta {z : ℂ | 0 < z.re ∧ z.re < 1} s          -- [CONJ]
```

### Proof skeleton

*First; the other two are identical with M6 / repo:`Conj.lean:440` in place of M4.*

```lean
  by_cases hs : s ∈ {z : ℂ | 0 < z.re ∧ z.re < 1}
  · obtain ⟨h0, h1⟩ := hs
    have hs' : (1 - s) ∈ {z : ℂ | 0 < z.re ∧ z.re < 1} := by
      simp only [Set.mem_setOf_eq, Complex.sub_re, Complex.one_re]
      constructor <;> linarith
    rw [riemannZeta_divisor_strip_apply hs', riemannZeta_divisor_strip_apply ⟨h0, h1⟩,
        analyticOrderAt_riemannZeta_one_sub h0 h1]                       -- M16, M16, M4
  · rw [Function.locallyFinsuppWithin.apply_eq_zero_of_notMem _ (fun h => hs ?_),
        Function.locallyFinsuppWithin.apply_eq_zero_of_notMem _ hs]
    · simp only [Set.mem_setOf_eq, Complex.sub_re, Complex.one_re] at h ⊢
      constructor <;> linarith [h.1, h.2]
```

### Pinned dependencies (M17)

M4, M6, M16; `analyticOrderAt_riemannZeta_conj` repo:`Conj.lean:440`
**(merged conjugation package, PR #307 (`c277b86`), on `main`)**; `Complex.conj_re` — `Mathlib/Data/Complex/Basic.lean:467` (the
strip is conj-stable because `((starRingEnd ℂ) z).re = z.re`);
`Function.locallyFinsuppWithin.apply_eq_zero_of_notMem` —
`Mathlib/Topology/LocallyFinsupp.lean:197`.

### Obligations (M17)

- **S1M-17** (LOW): the `Ω`-stability side goals over `ℝ` — same class as
  S1M-14b, same `linarith` fallback. Note that **unlike M14/M15 for ξ**, M17
  cannot be stated for an arbitrary symmetric `U`: the ζ order transport (M4)
  itself is strip-bound, so `Ω` is not a convenience choice but a hypothesis
  carrier. Stating M17 over a general `U` would require M4 without `h0`/`h1`,
  which is **false** — death condition 6.

- **S1M-17-skel** (LOW, proof engineering only; the M17 statements are
  unaffected). The negative branch of the skeleton above writes
  `rw [… (fun h => hs ?_), …]`, i.e. a synthetic `?_` hole **inside a `rw`
  argument**, discharged as a following bullet. `rw` does not admit `?_` holes
  that spawn later goals — only `refine`/`exact` do — so that skeleton is not
  expected to elaborate as written. The drafts-lane mirror
  `drafts/RiemannMult.lean` hoists the Ω-stability fact into a `have hrefl`
  above the case split and reuses it in both branches; the lemma set, the
  mathematical content and the statements are unchanged. Recorded here so a
  stage-one reviewer is not misled into reading the skeleton as a shipped proof
  body: under §Stage one, only the thirty-four signatures, their hypothesis
  carriers, the locators, the claim boundary and the death conditions are under
  review — the skeletons are illustrative and carry no kernel verdict.

---

## 3. Conjugation-package dependency map

**Merged package prerequisites, not pinned Mathlib.** These statements consume
`Conj.lean`, which is **built, merged and on `main`** (the conjugation package,
PR #307 (`c277b86`), imported from `ResearchOS.lean`). Nothing below is blocked,
and nothing below waits on an unmerged PR:

| Statement | Consumes (merged, on `main`) | Symbol consumed |
|---|---|---|
| M5 | conjugation package, PR #307 | `analyticOrderAt_riemannXi_conj` (repo:`Conj.lean:452`) |
| M6 | conjugation package, PR #307 | `analyticOrderAt_riemannZeta_conj` (repo:`Conj.lean:440`) |
| M7 | conjugation package, PR #307 | M5 + `analyticOrderAt_riemannXi_conj` |
| M8 | conjugation package, PR #307 | M6 + `analyticOrderAt_riemannZeta_conj` |
| M15 | conjugation package, PR #307 | M5 + `analyticOrderAt_riemannXi_conj` |
| M17b, M17c | conjugation package, PR #307 | `analyticOrderAt_riemannZeta_conj` (repo:`Conj.lean:440`) + M6 |

**M1–M4, M9–M14, M16, M16', M16'' and M17a consume no conjugation-package lemma
at all**; they need only `main` + the pin. A review-convenience ordering —
`M1, M2, M3, M4` (reflection leg, self-contained) →
`M9, M10, M11, M12, M13, M14` (ξ divisor interface + reflection invariance) →
`M16, M16', M16'', M17a` (ζ divisor interface on Ω + reflection invariance) →
`M5, M6, M7, M8, M15, M17b, M17c` (conjugation composite) — **contains no wait
state.** Every prerequisite of every M is either pinned Mathlib or a
kernel-checked theorem on current `main`.

What still gates this contract is **not** a package prerequisite: it is
independent acceptance of the statement surface, and separately and later,
kernel promotion of a built module. See §Two-stage gate and promotion ordering.

---

## Pinned API dependencies table

All paths relative to the pinned Mathlib tree; all line numbers grep-verified
this session at `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`.

| declaration | file:line | used in |
|---|---|---|
| `analyticOrderAt` (def; junk `0` off analyticity) | Mathlib/Analysis/Analytic/Order.lean:47 | all |
| `analyticOrderAt_of_not_analyticAt` | Mathlib/Analysis/Analytic/Order.lean:64 | M4 audit, M2 |
| `AnalyticAt.analyticOrderAt_eq_zero` | Mathlib/Analysis/Analytic/Order.lean:133 | M4 note, S1M-12a |
| `AnalyticAt.analyticOrderAt_ne_zero` | Mathlib/Analysis/Analytic/Order.lean:137 | M4 note |
| section variables `{f : 𝕜 → E} {g : 𝕜 → 𝕜} {z₀ : 𝕜}` | Mathlib/Analysis/Analytic/Order.lean:525 | M2 binder audit |
| `analyticOrderAt_comp_of_deriv_ne_zero` | Mathlib/Analysis/Analytic/Order.lean:561 (junk branch :566–567) | M2, M3 |
| `namespace AnalyticOnNhd` (opens :575, closes :700) | Mathlib/Analysis/Analytic/Order.lean:575 | name audit for :614/:624 |
| `AnalyticOnNhd.exists_analyticOrderAt_ne_top_iff_forall` | Mathlib/Analysis/Analytic/Order.lean:614 | S1M-12a fallback 2 |
| `AnalyticOnNhd.analyticOrderAt_ne_top_of_isPreconnected` | Mathlib/Analysis/Analytic/Order.lean:624 | S1M-12a fallback 1 |
| `AnalyticOnNhd.analyticOrderAt_eq_top_iff_eq_zero` (inside `namespace AnalyticOnNhd`, :575–:700; hypotheses `[PreconnectedSpace 𝕜]` + `∀ z₀, AnalyticAt 𝕜 f z₀`, **no** `AnalyticOnNhd` argument, so dot notation does not resolve) | Mathlib/Analysis/Analytic/Order.lean:687 | M12 |
| `IsOpen.forall_analyticOrderAt_eq_top_iff_eqOn_zero` | Mathlib/Analysis/Analytic/Order.lean:693 | recorded as **invalid** for M12 (A3) |
| `analyticAt_comp_iff_of_deriv_ne_zero` | Mathlib/Analysis/Calculus/InverseFunctionTheorem/Analytic.lean:40 | internal to :561 |
| `deriv_const_sub_id` | Mathlib/Analysis/Calculus/Deriv/Add.lean:449 | M2, M3 |
| `deriv_const_sub_id'` (`@[simp]` twin) | Mathlib/Analysis/Calculus/Deriv/Add.lean:453 | S1M-2b fallback |
| `div_div_cancel` / additive twin `sub_sub_cancel` | Mathlib/Algebra/Group/Basic.lean:933 (`@[to_additive (attr := simp)]` at :932) | M2, M6 note |
| `analyticAt_const` | Mathlib/Analysis/Analytic/Constructions.lean:54 | M2 (`fun_prop`) |
| `AnalyticAt.sub` (`@[to_fun (attr := fun_prop)]` at :186) | Mathlib/Analysis/Analytic/Constructions.lean:187 | M2 (`fun_prop`) |
| term-mode precedent `analyticAt_const.sub (…)` | Mathlib/Analysis/Analytic/Constructions.lean:857 | S1M-2c fallback |
| `analyticAt_id` (`@[fun_prop]` at :155) | Mathlib/Analysis/Analytic/Linear.lean:156 | M2 (**A1**) |
| `CompleteSpace ℂ` | Mathlib/Analysis/Complex/Basic.lean:124 | M2 |
| `CharZero ℂ` | Mathlib/Data/Complex/Basic.lean:773 | M2 |
| `NormedSpace.instPathConnectedSpace` (prio 100) | Mathlib/Analysis/Normed/Module/Convex.lean:168 | S1M-12a |
| `MeromorphicOn.divisor` (total, no hypotheses) | Mathlib/Analysis/Meromorphic/Divisor.lean:39 | M10, M11, M13–M17 |
| `supportLocallyFiniteWithinDomain'` discharge inside `divisor` | Mathlib/Analysis/Meromorphic/Divisor.lean:45–55 | anti-pitfall (**A10**) |
| `MeromorphicOn.divisor_apply` | Mathlib/Analysis/Meromorphic/Divisor.lean:68 | S1M-10 fallback |
| `MeromorphicOn.AnalyticOnNhd.divisor_apply` | Mathlib/Analysis/Meromorphic/Divisor.lean:71 | M10, M16 |
| `_root_.divisor_sphere_support_finite` (the `_root_` contrast) | Mathlib/Analysis/Meromorphic/Divisor.lean:83 | naming trap |
| `MeromorphicOn.divisor_ball_support_finite` | Mathlib/Analysis/Meromorphic/Divisor.lean:104 | cited as **not** counting |
| `MeromorphicOn.AnalyticOnNhd.divisor_nonneg` | Mathlib/Analysis/Meromorphic/Divisor.lean:177 | M11, M16 |
| `namespace MeromorphicOn` span | Mathlib/Analysis/Meromorphic/Divisor.lean:28–468 | naming trap |
| `Function.locallyFinsuppWithin` (structure) | Mathlib/Topology/LocallyFinsupp.lean:48 | carrier |
| `FunLike` instance | Mathlib/Topology/LocallyFinsupp.lean:125 | M14, M15, M17 |
| `Function.locallyFinsuppWithin.apply_eq_zero_of_notMem` | Mathlib/Topology/LocallyFinsupp.lean:197 | M14, M17 |
| `.discreteSupport` / `.closedSupport` / `.finiteSupport` | Mathlib/Topology/LocallyFinsupp.lean:218 / :237 / :254 | DEFERRED-2 |
| pointwise `LE` instance | Mathlib/Topology/LocallyFinsupp.lean:401 | M11 |
| `restrict` / `restrictMonoidHom` / `restrictLatticeHom` | Mathlib/Topology/LocallyFinsupp.lean:584 / :625 / :661 | DEFERRED-1 (only carrier-changing maps) |
| `WithTop.untop₀` | Mathlib/Algebra/Order/WithTop/Untop0.lean:30 | M10, M16 |
| `WithTop.untop₀_top` (`= 0`) | Mathlib/Algebra/Order/WithTop/Untop0.lean:41 | carrier decision item 3 |
| `meromorphicOrderAt` (junk `0` off meromorphy) | Mathlib/Analysis/Meromorphic/Order.lean:47 | carrier decision item 3 |
| `ENat.map_eq_top_iff` precedent usage | Mathlib/Analysis/Meromorphic/Order.lean:71 | M12 |
| `AnalyticAt.meromorphicOrderAt_eq` | Mathlib/Analysis/Meromorphic/Order.lean:279 | M12, M16', S1M-10 fallback |
| `AnalyticOnNhd.meromorphicOn` | Mathlib/Analysis/Meromorphic/Basic.lean:475 | M9, M16 |
| `AnalyticOnNhd.mono` | Mathlib/Analysis/Analytic/Basic.lean:498 | M9 |
| `DifferentiableOn.analyticAt` | Mathlib/Analysis/Complex/CauchyIntegral.lean:625 | M16, S1M-9 fallback |
| `analyticOnNhd_univ_iff_differentiable` | Mathlib/Analysis/Complex/CauchyIntegral.lean:678 | M9 |
| `AnalyticOnNhd.meromorphicNFOn` | Mathlib/Analysis/Meromorphic/NormalForm.lean:567 | M13, M16'' |
| `MeromorphicNFOn.zero_set_eq_divisor_support` (no `namespace` in file) | Mathlib/Analysis/Meromorphic/NormalForm.lean:578 | M13, M16'' |
| `ENat.map_eq_top_iff` | Mathlib/Data/ENat/Basic.lean:526 | M12, M16' |
| `differentiableAt_riemannZeta` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:137 | M16, M4 audit |
| `riemannZeta_neg_two_mul_nat_add_one` | Mathlib/NumberTheory/LSeries/RiemannZeta.lean:171 | M4 falsity argument |
| `riemannZeta_ne_zero_of_one_le_re` | Mathlib/NumberTheory/LSeries/Nonvanishing.lean:410 | M4 falsity argument |
| `isClosed_/isDiscrete_riemannZetaZeros`, `IsCompact.inter_riemannZetaZeros_finite` | Mathlib/NumberTheory/LSeries/ZetaZeros.lean:57 / :60 / :64 | DEFERRED-2 |
| `Complex.one_re` | Mathlib/Data/Complex/Basic.lean:147 | M4, M14, M16, M17 |
| `Complex.conj_re` | Mathlib/Data/Complex/Basic.lean:467 | M6, M15, M17 |
| `Complex.sub_re` | Mathlib/Data/Complex/Basic.lean:640 | M4, M14, M17 |
| `Complex.continuous_re` | Mathlib/Analysis/Complex/Basic.lean:153 | M16 |
| `Function.comp_apply`, `congrArg`, `congrFun`, `neg_ne_zero`, `one_ne_zero`, `isOpen_lt`, `Set.subset_univ`, `Set.mem_univ`, `Set.setOf_and`, `isPreconnected_univ`, `isConnected_univ`, `linarith`/`norm_num` glue | (core API, bridge-precedent no-locator glue) | throughout |
| **repo (built, `main`)** `riemannXi`, `differentiable_riemannXi`, `riemannXi_one_sub`, `riemannXi_zero`, `riemannXi_one`, `analyticOrderAt_riemannXi_eq_riemannZeta` | repo:`…/Xi.lean:41`, `:46`, `:61`, `:72`, `:78`, `:248` | M1, M3, M4, M9, M12, M16' |
| **repo (built, `main`)** conjugation package, PR #307 (`c277b86`): `analyticOrderAt_riemannZeta_conj`, `analyticOrderAt_riemannXi_conj` | repo:`…/Conj.lean:440`, `:452` | M5–M8, M15, M17b/c |

In-repo template witnesses (not dependencies): repo:`Conj.lean:310–311` (the
`hc0`/`hc1` conj-`re` idiom), repo:`Conj.lean:443–449` (the rewrite
occurrence-audit precedent), repo:`Conj.lean:336/357` (the hand-built
antiholomorphic order transport that Order.lean:561 makes unnecessary on the
reflection leg), repo:`Xi.lean:255` and `:309` (the `isOpen_lt` idiom),
repo:`Xi.lean:250–251` (the `fun e => by simp [e] at h` idiom),
repo:`Xi.lean:239–246` (the X11 docstring stating the strip-only
factorization).

## Anti-pitfall compliance (repo contracts)

- **Totalized values.** The `untop₀` totalization
  (Untop0.lean:30, `untop₀_top = 0` at :41) is treated as information-losing
  and never as a multiplicity: M12 is what licenses reading
  `divisor riemannXi U z` as a multiplicity at all, and M14/M15/M17 are proved
  at the `ℕ∞` level *before* pushing forward, so no equality is obtained by
  collapsing `⊤`. `analyticOrderAt`'s junk value `0` at non-analytic points
  (Order.lean:64) is audited on both sides of every ζ equality (M4 exceptional-
  point audit); M2 inherits Order.lean:561's own internal junk discharge.
- **Exceptional points.** Every ζ statement is strip-bound: M4/M6/M8 carry
  `0 < s.re` and `s.re < 1` as hypotheses; M16–M17 carry Ω as the divisor's
  carrier set, outside which both sides are zero by
  `apply_eq_zero_of_notMem`. Ω excludes `1` (the ζ pole), `0`, and every Γℝ
  pole `0, -2, -4, …`. ξ is entire, so no exceptional point arises in M1–M3,
  M5, M7, M9–M15.
- **No inference from an unproved fact.** X11 (repo:`Xi.lean:248`) is a
  kernel-checked repo theorem on `main`; the conjugation package's legs
  (repo:`Conj.lean:440/452`, PR #307 (`c277b86`), merged) are declared as
  package prerequisites, never as pinned Mathlib.
- **No zero enumeration.** No index type, no ordering of zeros, no
  `ρ : ℕ → ℂ`, no `Finset` of zeros, no `⋃`/`∑` over zeros. The divisor is a
  `locallyFinsuppWithin` object, so what this package has is exactly **local
  finiteness** of its support — discharged inside `MeromorphicOn.divisor`
  itself (Divisor.lean:45–55) for every `f` and `U` — together with the
  identification of that support with the zero set on the carrier region (M13
  for ξ on `U`, M16'' for ζ on Ω). **Nothing here establishes, asserts, or
  implies that the ξ or ζ divisor support is infinite.** Infinitude of the
  nontrivial zero set is not proved anywhere in this package, is not needed by
  any M, and must not be written. (An earlier draft of this bullet claimed
  "on `Set.univ` and on the strip its support is infinite and it is never a
  `Finsupp`"; that claim is **withdrawn** as unsupported by anything
  established here.)
- **No counting.** No `N(T)`, no `|ρ| ≤ T` truncation, no zero-density, no
  `logCounting`. `Function.locallyFinsuppWithin.finiteSupport`
  (LocallyFinsupp.lean:254) and `divisor_ball_support_finite`
  (Divisor.lean:104) are compact-set statements and must not be dressed up as
  counting. Any such statement belongs to `S1-GLOBAL-ZEROS`.
- **No simplicity.** Nothing here yields `analyticOrderAt riemannXi ρ = 1` for
  any ρ. Multiplicity-*preservation* under symmetries is not a
  multiplicity-*bound*. This applies to *prose* as well as to statements: the
  M4 note must not assert that the trivial ζ zeros are simple (finding A7).
- **No growth, and none is hidden in the divisor.** The local-finiteness field
  `supportLocallyFiniteWithinDomain'` of `Function.locallyFinsuppWithin`
  (LocallyFinsupp.lean:48) is discharged **inside** `MeromorphicOn.divisor`
  itself (Divisor.lean:45–55), for *every* `f` and `U`, via
  `codiscrete_setOf_meromorphicOrderAt_eq_zero_or_top` (Divisor.lean:51) — no
  Jensen inequality, no bound on the **growth order** of an entire function (in
  particular no "ξ has growth order one" input), and nothing ζ/ξ-specific.
  M9/M16 contribute only analyticity. Verified by reading the definition body
  at the pin (finding A10).
- **M12 and M16' are the only order-finiteness claims — finiteness of the
  *local analytic* order (`analyticOrderAt … ≠ ⊤`) and of the *local
  meromorphic* order (`meromorphicOrderAt … ≠ ⊤`) at a point, never of a growth
  order — and neither needs a zero-free region.** M12 comes from `riemannXi 0 = 1/2 ≠ 0` (repo:`Xi.lean:72`) plus
  connectedness; M16' comes from M12 through X11. No lower bound on `|ζ|`, no
  nonvanishing witness on Ω, and no unproved analytic fact is used.
- **No competing definitions, no new RH `Prop`.** The package contains zero
  `def`s; every ζ/ξ object is the pinned or already-built one. No statement
  mentions `RiemannHypothesis`, and repo:`Xi.lean:208` (X10, the only
  RH-mentioning prerequisite) is not consumed by any M.
- **No RH-truth claim.** Every statement is symmetric bookkeeping on the zero
  set. M7/M8 say the four points `ρ, 1-ρ, conj ρ, 1-conj ρ` carry equal
  multiplicity; that is compatible with every conceivable zero configuration,
  including all counterexamples to RH. This package supplies neither evidence
  for nor evidence against the Riemann Hypothesis, and must not be described
  as progress toward it.
- **Name collisions.** Zero hits at the pin for all seven proposed generic /
  ξ-divisor names, zero hits for `riemannXi` anywhere in `Mathlib/`, and zero
  hits repo-side for the Block D/E names (both scans re-run this session).

## Obligation register

| ID | Statement | Severity | Content | Fallback recorded |
|---|---|---|---|---|
| **S1M-FIN** | M12 | **HIGH** | `analyticOrderAt riemannXi z ≠ ⊤`; without it the `untop₀` totalization conflates "no zero" with "identically zero nearby" and M13 is false-shaped | yes (Order.lean:624 / :614 routes) |
| S1M-13 | M13 | MEDIUM | subtype-bound `∀ u : U` hypothesis + orientation flip of the pinned equality | yes (state in pinned orientation) |
| S1M-10 | M10 | MEDIUM | `(↑)` in `.map (↑)` must elaborate as `Nat.cast : ℕ → ℤ` on both sides | yes (explicit `Nat.cast`, or Divisor:68 + Order:279) |
| S1M-2a | M2 | MEDIUM | `f ∘ g` head match against Order.lean:561 **plus** the `(fun w => c - w) (c - z)` beta-redex in its RHS — `rw [sub_sub_cancel]` can fail, `simpa only` is required (A2) | yes (`simp only … at h`, `beta_reduce`, `show`) |
| S1M-12a | M12 | MEDIUM | `PreconnectedSpace ℂ` instance resolution — narrow check, do not assume | yes, **corrected (A3)**: Order:624/:614 with an explicit `analyticOrderAt riemannXi 0 = 0` witness from Order:133 + `riemannXi_zero`. The previously recorded Order:693 fallback is **invalid** |
| S1M-16a | M16 | MEDIUM | `IsOpen ({0<re} ∩ {re<1})` vs `IsOpen {0<re ∧ re<1}` | yes (`Set.setOf_and`; repo:`Xi.lean:255` idiom) |
| S1M-16d | M16'' | MEDIUM | subtype projection `u.2.1`/`u.2.2` on `↥Ω` | yes (`obtain ⟨w, hw⟩ := u`) |
| S1M-2c | M2 | LOW | `analyticAt_id` is at **Linear.lean:156**, stated for `id`; term-mode `.sub` matches the lambda only up to `Pi.instSub`/`id` defeq (A1) | yes (`fun_prop`; `AnalyticAt.fun_sub`; precedent Constructions:857) |
| S1M-2b | M2 | LOW | `(fun w : ℂ => c - w)` must be the term `deriv_const_sub_id` (Deriv/Add.lean:449) is stated at (`c - ·`) | yes (`simp [deriv_const_sub_id']`, Deriv/Add.lean:453; or `HasDerivAt.const_sub`, Deriv/Add.lean:434) |
| S1M-16b | M16 | LOW | `w ≠ 1` on Ω | yes (repo:`Xi.lean:250–251` idiom) |
| S1M-16c | M16' | LOW | `▸` direction on X11 | yes (`rw [←…]`) |
| S1M-17 | M17 | LOW | Ω-stability side goals over `ℝ`; Ω is a hypothesis carrier, not a convenience | yes (`linarith`) |
| S1M-17-skel | M17 | LOW | (proof engineering, no statement content) the M17 skeleton's `?_` hole **inside** a `rw` argument does not elaborate; `rw` admits no goal-spawning holes | yes (the draft's `have hrefl` hoisted above the case split) |
| **S1M-ORD** | M2 | **LOW** | the generic reflection wrapper. **Explicitly NOT a pin gap** — Order.lean:561 already supplies the content, unlike S1C-ORD where `starRingEnd ℂ` is antiholomorphic | yes (M3 independent route; M2 droppable) |
| S1M-1 | M1 | LOW | `∘`-form elaboration of the reflection glue | yes |
| S1M-3 | M3 | LOW | rewrite occurrence audit (mirrors repo:`Conj.lean:443–449`) | yes |
| S1M-4 | M4 | LOW | `(1-s).re` arithmetic | yes |
| S1M-9 | M9 | LOW | `E := ℂ` unification in CauchyIntegral.lean:678 | yes |
| S1M-12b | M12 | LOW | `(1/2 : ℂ) = 0` discharge | yes |
| S1M-14a | M14 | LOW | (informational) M14/M15 need **no** `≠ ⊤` hypothesis | n/a |
| S1M-14b | M14 | LOW | strip reflection-symmetry side goal over `ℝ` | yes |
| S1M-15a | M15 | LOW | (informational) none of M15's six needs a `≠ ⊤` hypothesis — same decoupling as S1M-14a | n/a |
| S1M-15b | M15 | LOW | the conj side goal `0 < ((starRingEnd ℂ) z).re ∧ … ↔ 0 < z.re ∧ …`; after `Complex.conj_re` both sides are literally `P`, and `simp only` closes `P ↔ P` only if it reduces it (`iff_self` is not in a `simp only` set) | yes (append `exact Iff.rfl`) |
| S1M-15c | M15 | LOW | the reflection side goal of `riemannXi_divisor_strip_one_sub_conj` — S1M-14b's goal verbatim, over `ℝ`, so `omega` is wrong | yes (`constructor <;> intro h <;> exact ⟨by linarith [h.1, h.2], by linarith [h.1, h.2]⟩`) |

No obligation is analytic. Every analytic input — ξ's entirety, ζ's
analyticity off `1`, the affine-reflection order transport, the divisor
construction and its `_apply`/`_nonneg` lemmas, the normal-form support
identity, and the `analyticOrderAt` characterization API — is a quoted pinned
theorem at `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f` or a kernel-checked repo
theorem. Nothing here is claimed proved until the kernel checks it in a built
PR after independent review. No item waits on an unmerged PR: the conjugation
package the `[CONJ]` items consume is merged (PR #307 (`c277b86`), on `main`).

### Deferred items (explicitly out of this package)

- **DEFERRED-1 — divisor pullback / `locallyFinsuppWithin.comap`.** The pin
  has no pushforward, pullback, comap, or precomposition API for
  `Function.locallyFinsuppWithin` (only `restrict` :584,
  `restrictMonoidHom` :625, `restrictLatticeHom` :661), and no `divisor_comp`
  in `Mathlib/Analysis/Meromorphic/Divisor.lean`. A `locallyFinsuppWithin`-level
  statement `(divisor ξ U).comap σ = divisor (ξ ∘ σ) (σ ⁻¹' U)` therefore
  requires a **new definition** carrying a nontrivial local-finiteness field
  obligation, for one use. Deferred; M14/M15 obtain the same exit evidence
  pointwise via the `FunLike` coercion (LocallyFinsupp.lean:125). Revisit only
  if a later barrier needs divisor *algebra* under the symmetries, not just
  values.
- **DEFERRED-2 — ξ zero-set discreteness / closedness / compact-finiteness /
  countability.** Free once M13 lands, via
  `Function.locallyFinsuppWithin.discreteSupport` (LocallyFinsupp.lean:218),
  `.closedSupport` (:237), `.finiteSupport` (:254), and the ζ analogues
  already pinned at `Mathlib/NumberTheory/LSeries/ZetaZeros.lean:57,60,64`.
  **Not a S1-MULTIPLICITY exit item** — the exit is a multiplicity interface
  plus its symmetries, not a zero-set topology package. Excluded to hold
  scope; it would also be the first step toward `S1-GLOBAL-ZEROS`, which is a
  different barrier.
- **DEFERRED-3 (RESTATED — finding A5) — ζ divisor on sets containing `1`.**
  The original text deferred the ζ divisor *entirely*, on the grounds that "ζ
  has a pole at `1`, so its divisor is genuinely meromorphic (`negPart ≠ 0`)".
  That rationale is **wrong for the open strip**, which is the only set this
  package needs: `1 ∉ Ω` (`Complex.one_re`, Data/Complex/Basic.lean:147), ζ is
  analytic on Ω (`differentiableAt_riemannZeta`, RiemannZeta.lean:137), and the
  divisor is effective there (M16). Since the capability-map row
  (repo:`MATHLIB_CAPABILITY_MAP.md:386`) asks for a **zeta/xi** divisor
  interface, the ζ-on-Ω half is now **in scope as Block E (M16–M17)**.
  What remains deferred is only the ζ divisor on a set that *contains* `1`
  (e.g. `Set.univ`, or the closed strip): there `negPart ≠ 0`, `divisor_nonneg`
  fails, and any symmetry statement needs pole bookkeeping — and it is not
  required by the exit, because M4/M6/M8 and M16/M17 are all strip-bound
  anyway. Also still deferred: the ζ divisor *outside* the strip, where M4 is
  outright false (death condition 6).

---

## Claim boundary

The exact wording being answered is
repo:`domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md:386`:

> `S1-MULTIPLICITY` — **OPEN; local xi/zeta analytic-order equality discharged
> by PR #304** | zero set loses analytic multiplicity and no
> conjugation/reflection action preserves it | … | remaining exit evidence:
> **zeta/xi divisor interface and multiplicity-preserving divisor symmetries**

and repo:`MATHLIB_CAPABILITY_MAP.md:389` for `S1-CONJ`:

> no named zeta/xi conjugation symmetry or multiplicity-preserving fourfold
> zero action | … | **conjugation theorem plus divisor invariance under
> `ρ ↦ 1-conj(ρ)`**

**What this package would supply once kernel-checked and promoted.** As it
stands it is an unbuilt statement surface: it closes nothing, and none of the
items below is a closure claim. Stage-one acceptance of these statements changes
no barrier row (see the next list, and §Two-stage gate and promotion ordering).

- `S1-MULTIPLICITY` exit item *"zeta/xi divisor interface"*: M9–M13 for ξ
  (`MeromorphicOn.divisor riemannXi U` evaluates by local analytic order at a
  point, is effective, has finite local analytic order at every point, and its
  support is exactly the ξ zero set on `U`; the support is **locally** finite
  by the construction of `MeromorphicOn.divisor` itself, and no claim is made
  about it being infinite)
  **and** M16–M16'' for ζ on the open strip (same four properties, Ω-bound).
  Both halves are needed; the row says *zeta/xi*, not *xi* (finding A5).
- `S1-MULTIPLICITY` exit item *"multiplicity-preserving divisor symmetries"*:
  order level M3, repo:`Conj.lean:452`, M5 (and M7/M8); divisor level M14, M15
  (ξ, arbitrary symmetric `U`) and M17 (ζ, Ω only).
- The reflection leg of order transport (M3, M4), which is the ζ/ξ-level leg
  the capability-map row correctly identified as missing.

**What this package does NOT close.**

- **`S1-CONJ` closes only if both packages are built and merged.** The
  conjugation package (PR #307 (`c277b86`)) is merged and supplies the
  conjugation theorem; **this** package would supply the divisor invariance under
  `ρ ↦ 1 - conj ρ` (M15, M17c) — but M15/M17c *themselves* consume
  repo:`Conj.lean:440/452`, and this package is **unbuilt**, so it retires
  nothing and `S1-CONJ` stays open. A merged prerequisite is evidence about the
  prerequisite, never about this contract. This
  matches repo:`MATHLIB_CAPABILITY_MAP.md:614–618` verbatim ("Its exit evidence
  is the conjugation theorem *together with* divisor invariance under
  `ρ ↦ 1 − conj ρ`"). If only one merges, both barrier rows stay open.
- **Correction (finding A4): the capability-map row is NOT stale.** An earlier
  draft of this section claimed the row was "stale in two places" because the
  pin already has `MeromorphicOn.divisor` and
  `analyticOrderAt_comp_of_deriv_ne_zero`. That is a misreading of scope. The
  row and its fourth addendum (repo:`MATHLIB_CAPABILITY_MAP.md:591–593`) say
  "no divisor interface, reflection-order package, or multiplicity-preserving
  divisor symmetries **are present**" — present *in this repository's ζ/ξ
  layer*. Generic Mathlib machinery existing at the pin is what makes the
  package cheap; it is not a defect in the row, and the row must not be
  re-scoped on that basis. **The claim that the row is stale is retracted.**
  What *is* newly established and worth recording is narrower and purely about
  cost:
  - `MeromorphicOn.divisor` (Divisor.lean:39) over
    `Function.locallyFinsuppWithin` (LocallyFinsupp.lean:48) is total and
    hypothesis-free, so no divisor *formalism* has to be built here — only the
    ζ/ξ instances;
  - `analyticOrderAt_comp_of_deriv_ne_zero` (Order.lean:561) already covers
    affine reflection, so the reflection leg — unlike the conjugation leg,
    where `starRingEnd ℂ` is antiholomorphic and repo:`Conj.lean:336/357` had
    to be hand-built — needs no new generic analysis.

  The genuine residual generic gap is only the divisor pullback (DEFERRED-1),
  and that gap is avoidable by stating M14/M15/M17 pointwise.
- **No zero enumeration.** No index type, no ordering of zeros, no
  `ρ : ℕ → ℂ`, no `Finset` of zeros, no `⋃`/`∑` over zeros. The divisor is a
  `locallyFinsuppWithin` object, so what this package has is exactly **local
  finiteness** of its support — discharged inside `MeromorphicOn.divisor`
  itself (Divisor.lean:45–55) for every `f` and `U` — together with the
  identification of that support with the zero set on the carrier region (M13
  for ξ on `U`, M16'' for ζ on Ω). **Nothing here establishes, asserts, or
  implies that the ξ or ζ divisor support is infinite.** Infinitude of the
  nontrivial zero set is not proved anywhere in this package, is not needed by
  any M, and must not be written. (An earlier draft of this bullet claimed
  "on `Set.univ` and on the strip its support is infinite and it is never a
  `Finsupp`"; that claim is **withdrawn** as unsupported by anything
  established here.)
- **No counting function.** No `N(T)`, no `|ρ| ≤ T` truncation, no
  zero-density, no `logCounting`. `Function.locallyFinsuppWithin.finiteSupport`
  (LocallyFinsupp.lean:254) and `divisor_ball_support_finite`
  (Divisor.lean:104) are compact-set statements and must not be dressed up as
  counting. **Any such statement belongs to `S1-GLOBAL-ZEROS`, which is a
  different barrier and is untouched here.**
- **No simplicity.** Nothing here yields `analyticOrderAt riemannXi ρ = 1` for
  any ρ. Multiplicity-*preservation* under symmetries is not a
  multiplicity-*bound*. This applies to *prose* as well as to statements: the
  M4 note must not assert that the trivial ζ zeros are simple (finding A7).
- **No growth, and none is hidden in the divisor.** The local-finiteness field
  `supportLocallyFiniteWithinDomain'` of `Function.locallyFinsuppWithin`
  (LocallyFinsupp.lean:48) is discharged **inside** `MeromorphicOn.divisor`
  itself (Divisor.lean:45–55), for *every* `f` and `U`, via
  `codiscrete_setOf_meromorphicOrderAt_eq_zero_or_top` — no Jensen inequality,
  no bound on the **growth order** of an entire function (in particular no
  "ξ has growth order one" input), and nothing ζ/ξ-specific. M9/M16 contribute
  only analyticity. Verified by reading the definition body at the pin.
- **M12 and M16' are the only order-finiteness claims — finiteness of the
  *local analytic* order (`analyticOrderAt … ≠ ⊤`) and of the *local
  meromorphic* order (`meromorphicOrderAt … ≠ ⊤`) at a point, never of a growth
  order — and neither needs a zero-free region.** M12 comes from `riemannXi 0 = 1/2 ≠ 0` (repo:`Xi.lean:72`) plus
  connectedness; M16' comes from M12 through X11. No lower bound on `|ζ|`, no
  nonvanishing witness on Ω, and no unproved analytic fact is used.
- **Nothing here bears on the truth of the Riemann Hypothesis.** Every
  statement is symmetric bookkeeping on the zero set. M7/M8 say the four points
  `ρ, 1-ρ, conj ρ, 1-conj ρ` carry equal multiplicity; that is compatible with
  every conceivable zero configuration, including all counterexamples to RH.
  This package supplies neither evidence for nor evidence against RH, and must
  not be described as progress toward it.
- **ζ statements are open-strip only.** M4/M6/M8 carry `0 < s.re` and
  `s.re < 1` because X11 (repo:`Xi.lean:248`) holds only where the Γℝ cofactor
  is a nonvanishing unit. The global form of M4 is **false** (trivial zeros).

---

## Death conditions

Stop and re-plan — do **not** patch around — if any of the following occurs.

1. **A new axiom would be needed.** No `axiom`, no `sorry`, no `admit`, no
   `native_decide` on an unproved side condition. The Lean kernel is the sole
   verifier; every declaration must be reachable with axiom base `standard`
   in the generated `ResearchOS/LedgerAxiomAudit.lean`.
2. **Any dependency on an unproved conjecture.** Nothing may be derived from
   RH, GRH, Lindelöf, density hypotheses, or any open statement — including
   as a hypothesis smuggled into a package theorem's binders.
3. **A statement needs enumeration.** If closing any M requires indexing the
   zeros, choosing an ordering, or producing a `Finset`/sequence of zeros —
   stop. That is `S1-GLOBAL-ZEROS`, a different barrier.
4. **A statement needs growth or counting bounds.** If any M requires a
   Jensen-type inequality, `logCounting`, an `N(T)` estimate, or a bound on the
   **growth order of an entire function** (the Hadamard-factorization notion
   of "order") — stop. *"Order" in this condition is the growth order only.*
   The finiteness of the **local analytic / local meromorphic order at a
   point** established by M12 and M16' (`analyticOrderAt … ≠ ⊤`,
   `meromorphicOrderAt … ≠ ⊤`) is a different notion, is not covered by this
   condition, and never yields a growth statement.
5. **M12 (S1M-FIN) cannot be discharged.** If `analyticOrderAt riemannXi z ≠ ⊤`
   resists all three recorded routes, M13 — and with it M16' and M16'', which
   derive their finiteness from M12 through X11 — must be dropped, and the
   divisor block reduced to M9–M11, M14/M15, M16 and M17 (none of which needs
   M12), with both support identifications (ξ on `U`, ζ on Ω) recorded as a new
   deferred item. Do **not** state M13 or M16'' with the `≠ ⊤` hypothesis
   floated to the caller and then call either half of the interface exit item
   closed.
6. **A ζ statement is proposed without the strip hypotheses.** M4/M6/M8
   without `0 < s.re` and `s.re < 1` are false statements, not hard ones.
7. **A new definition is proposed.** The package must contain zero `def`s. If
   a `comap` on `locallyFinsuppWithin` starts to look necessary, that is a
   signal the statement should be pointwise (M14/M15 pattern), or that the
   item belongs upstream in Mathlib rather than in this repo.
8. **The barrier row is used as a target.** An open row is not by itself
   authorization to work a route. The authority for this lane is the RH queue,
   repo:`tasks/RIEMANN_HYPOTHESIS.md`, under whose current dated decision
   `RH-002` is the **sole ACTIVE task** (`:28`; status line `:122`, "ACTIVE —
   independent disposition review only; no route execution authorized") and no
   route is selected. `repo/ECDLP_DECISION_SUBSTRATE.json` governs the ECDLP
   lane and is **not** the authority here; no authorization for this contract
   may be read out of it, in either direction. This contract is a statement
   design, not a claim that `S1-MULTIPLICITY` is the selected target.
9. **A capability-map row is declared "stale" from generic-Mathlib evidence.**
   The rows are scoped to this repository's ζ/ξ layer
   (repo:`MATHLIB_CAPABILITY_MAP.md:591–593`, "are present"). Finding a pinned
   generic lemma lowers the *cost* of an exit; it never retires a row. Any
   re-scoping is a maintainer decision on the map file, not a side effect of a
   contract draft. (Finding A4.)

**Provenance of these conditions.** Condition 9 was **added by the adversarial
review** (finding A4). Condition 5's disposition was rewritten after finding A3
invalidated both previously recorded M12 fallbacks. Condition 6's falsity
argument was corrected after finding A7 removed an unpinned simplicity claim
from the M4 note. Conditions 1–4, 7 and 8 carry over unchanged from the
skeleton.

---

## ANNEX A: adversarial review record (2026-08-06)

Independent adversarial review of the source skeleton. Mathlib checkout
re-verified by `git rev-parse HEAD` at `/workspace/leanprover-community/mathlib4`
→ `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`. Every `file:line` in the
skeleton was re-opened at that revision; the repo-side citations were re-opened
on the working branch at HEAD `b04c089`.

**Verdict: `SOUND_WITH_FIXES`.** Ten findings (A1–A10), all resolved in place
before this contract was written. The statement surface grew from M1–M15 to
**M1–M17** as a result of finding A5. This verdict accepts a statement surface
only: it is not a Lean kernel verdict, it does not promote a module, and it
does not close `S1-MULTIPLICITY` or `S1-CONJ`.

### A. Findings resolved in place

| ID | Severity | Finding | Fix applied |
|---|---|---|---|
| **A1** | MEDIUM | `analyticAt_id` cited as `Constructions.lean:54,187`. It is at **`Mathlib/Analysis/Analytic/Linear.lean:156`** (`@[fun_prop]` at :155); Constructions.lean:54 is `analyticAt_const`, :187 is `AnalyticAt.sub`. The citation also hid a defeq risk: `analyticAt_id` is stated for `(id : E → E)` and `AnalyticAt.sub` for the Pi-operation `f - g`, so the term-mode `analyticAt_const.sub analyticAt_id` matches `fun w => c - w` only up to `Pi.instSub`/`id` unfolding | M2 *Pinned dependencies* corrected; `hg` in M2 and in M3's independent route switched to `by fun_prop`; obligation **S1M-2c** added with `AnalyticAt.fun_sub` (from `@[to_fun]` at Constructions.lean:186) and the in-Mathlib precedent Constructions.lean:857 as fallbacks |
| **A2** | MEDIUM | M2's closer `rw [analyticOrderAt_comp_of_deriv_ne_zero …]; rw [sub_sub_cancel]` is unsound as *proof engineering*: Order.lean:561 concludes `… = analyticOrderAt f (g z₀)`, so the point argument is the **beta-redex** `(fun w => c - w) (c - z)`, which `rw [sub_sub_cancel]` cannot match syntactically. The recorded fallback (`rw [sub_sub_cancel] at h`) had the identical defect | M2 closer rewritten to `simpa only [sub_sub_cancel] using analyticOrderAt_comp_of_deriv_ne_zero (f := f) hg hg'`; explicit "Beta-redex warning" block added; S1M-2a restated; a note added to M3's independent route explaining why the same redex is harmless there (it is discharged by `exact`, which works up to defeq) |
| **A3** | MEDIUM | Both fallbacks recorded under **S1M-12a** were invalid. (i) `IsOpen.forall_analyticOrderAt_eq_top_iff_eqOn_zero` (Order.lean:693) consumes `∀ z ∈ s, analyticOrderAt f z = ⊤`; M12 has `⊤` at one point only — not a drop-in. (ii) `AnalyticOnNhd.analyticOrderAt_ne_top_of_isPreconnected` (Order.lean:624) takes a fifth argument `h₂x : analyticOrderAt f x ≠ ⊤`, i.e. the witness is **not free** and was never produced | S1M-12a rewritten with a complete corrected route: witness `analyticOrderAt riemannXi 0 = 0` via `AnalyticAt.analyticOrderAt_eq_zero` (Order.lean:133) + `riemannXi_zero` (repo:`Xi.lean:72`), then Order.lean:624; second fallback `AnalyticOnNhd.exists_analyticOrderAt_ne_top_iff_forall` (Order.lean:614, needs `IsConnected U`). The two invalid routes are recorded as must-not-re-record |
| **A4** | MEDIUM | The claim-boundary section asserted that the `S1-MULTIPLICITY` capability-map row is "stale in two places" because pinned Mathlib has `MeromorphicOn.divisor` and `analyticOrderAt_comp_of_deriv_ne_zero`. Misreading of scope: the row (repo:`MATHLIB_CAPABILITY_MAP.md:386`) and its fourth addendum (:591–593) say the divisor interface / reflection-order package / divisor symmetries "are present" — meaning *in this repository's ζ/ξ layer*, not in Mathlib. Generic machinery existing lowers cost; it does not retire the row | Claim boundary rewritten: the two capability-map rows quoted verbatim with line numbers; the "stale" claim **retracted** and replaced with a narrow cost statement; **death condition 9** added forbidding this class of re-scoping |
| **A5** | MEDIUM | Scope gap against the exit wording. The row's remaining exit evidence is a "**zeta/xi** divisor interface"; the draft supplied ξ only and deferred ζ (DEFERRED-3) while the claim boundary said the interface item was closed. Worse, DEFERRED-3's rationale ("ζ has a pole at `1`, so its divisor is genuinely meromorphic, `negPart ≠ 0`") is **false on the open strip**: `1 ∉ Ω`, ζ is analytic on Ω (`differentiableAt_riemannZeta`, RiemannZeta.lean:137), and the ξ pattern transfers with no new analysis | New **Block E (M16, M16', M16'', M17)** added: `analyticOnNhd_riemannZeta_strip`, ζ divisor on Ω with `divisor_apply`/`divisor_nonneg`, ζ finite local analytic order at every point of Ω *free from X11 + M12*, ζ divisor support on Ω, and the three ζ divisor symmetries on Ω. Statement surface M1–M15 → **M1–M17**. DEFERRED-3 restated as "ζ divisor on sets containing `1`". The conjugation-package dependency map and landing order updated. Claim boundary rewritten to claim exactly the ξ **and** ζ halves |
| **A6** | LOW | "`Mathlib.Analysis.Calculus.InverseFunctionTheorem.Analytic` (Order.lean:9)" — it is **Order.lean:10**; :9 is `Mathlib.Analysis.Calculus.Deriv.Pow` | Preamble note corrected |
| **A7** | LOW | M4's note asserted `analyticOrderAt riemannZeta (-2) = 1`. Simplicity of the trivial zeros is **not pinned**, is not needed for the falsity argument, and asserting it contradicts the package's own "No simplicity" boundary | Weakened to `≠ 0`, with pinned citations `riemannZeta_neg_two_mul_nat_add_one` (RiemannZeta.lean:171), `AnalyticAt.analyticOrderAt_ne_zero` (Order.lean:137), `riemannZeta_ne_zero_of_one_le_re` (Nonvanishing.lean:410), `AnalyticAt.analyticOrderAt_eq_zero` (Order.lean:133); explicit "do not sharpen" note added; the "No simplicity" boundary extended to prose |
| **A8** | LOW | Missing `file:line` on lemmas the protocol requires to be cited: `sub_sub_cancel`, `Complex.sub_re`, `Complex.one_re`, `Complex.conj_re`, and the `g : 𝕜 → 𝕜` constraint on Order.lean:561 | Added: `sub_sub_cancel` = `Mathlib/Algebra/Group/Basic.lean:933` (`@[to_additive (attr := simp)]` twin of `div_div_cancel`); `Complex.one_re` Data/Complex/Basic.lean:147, `Complex.conj_re` :467, `Complex.sub_re` :640; Order.lean:525 section-variable note |
| **A9** | LOW | Attack fronts 3 and 4 were addressed only implicitly | Explicit **exceptional-point audit** added to M4 (both sides junk-value-symmetric; ζ pole at `1` and Γℝ poles at `0,-2,-4,…` all outside Ω; ξ entire so `analyticOrderAt riemannXi 0 = analyticOrderAt riemannXi 1 = 0` and M3 at `s = 0` is a self-check) and an explicit **composite commutation check** added to M6 (Klein four-group orbit; Order.lean:561 needs only `deriv ≠ 0`, not a sign, so there is no orientation subtlety) |
| **A10** | LOW | The "no growth / no counting" boundary did not address the local-finiteness field of `locallyFinsuppWithin`, the most plausible place for a hidden analytic obligation | Boundary extended: `supportLocallyFiniteWithinDomain'` is discharged **inside** `MeromorphicOn.divisor` for every `f` and `U`; M9/M16 contribute only analyticity. Also recorded that M12/M16' need no zero-free region |

### B. Citations re-verified as CORRECT (no change)

Pinned Mathlib — `Analysis/Analytic/Order.lean` :47 (`analyticOrderAt` def,
junk `0` off analyticity), :64 (`analyticOrderAt_of_not_analyticAt`), :561
(signature and `[CompleteSpace 𝕜] [CharZero 𝕜]` verbatim; junk branch
discharged at :566–567), :614, :624, :687
(`AnalyticOnNhd.analyticOrderAt_eq_top_iff_eq_zero` verbatim — declared inside
`namespace AnalyticOnNhd` (:575–:700) but taking **no** `AnalyticOnNhd`
argument, only `[PreconnectedSpace 𝕜]` and `∀ z₀, AnalyticAt 𝕜 f z₀`, so the
fully-qualified name must be written and dot notation does not resolve), :693
(explicit `_root_.` prefix, so `IsOpen.forall_…` really is a root name). `Calculus/InverseFunctionTheorem/Analytic.lean:40`.
`Calculus/Deriv/Add.lean:449`, `:453` (`@[simp]` twin).
`Meromorphic/Divisor.lean` :39 (`divisor` total, **no hypotheses**, `U`
unconstrained), :68, :71, :83 (the `_root_` contrast), :104, :177;
`namespace MeromorphicOn` spans :28–:468, so
`MeromorphicOn.AnalyticOnNhd.divisor_apply` / `_nonneg` are the true full names
and dot notation on an `AnalyticOnNhd` hypothesis does **not** resolve —
**the §1 naming trap is confirmed**.
`Meromorphic/NormalForm.lean` :567, :578 (statement and orientation verbatim;
the file has **no** `namespace` block, so both are root names and dot notation
works). `Meromorphic/Order.lean` :47, :71 (the claimed `ENat.map_eq_top_iff`
precedent is real), :279. `Meromorphic/Basic.lean:475`.
`Analytic/Basic.lean:498`. `Complex/CauchyIntegral.lean` :625, :678.
`Topology/LocallyFinsupp.lean` :48, :125, :197, :218, :237, :254, :401, :584,
:625, :661. `Algebra/Order/WithTop/Untop0.lean` :30, :41.
`Data/ENat/Basic.lean:526` (namespace `ENat` confirmed).
`Analysis/Complex/Basic.lean:124`, `Data/Complex/Basic.lean:773`,
`Analysis/Normed/Module/Convex.lean:168`,
`NumberTheory/LSeries/ZetaZeros.lean` :57, :60, :64.

Repo — `Xi.lean` :22 (import), :41, :46, :61, :72, :192, :248 (X11 hypotheses
`0 < s.re`, `s.re < 1` verbatim). `Conj.lean` :41 (import), :163, :292, :357,
:440, :452.

Name-collision scan re-run at the pin: `analyticOrderAt_comp_const_sub`,
`riemannXi_comp_one_sub`, `analyticOrderAt_riemannXi_one_sub`,
`analyticOrderAt_riemannZeta_one_sub`, `riemannXi_divisor_apply`,
`divisor_comp` — **0 hits each**; no `riemannXi` anywhere in `Mathlib/`;
no `comap`/`map`/pushforward/pullback in `Topology/LocallyFinsupp.lean`
(**DEFERRED-1 confirmed**). Repo-side scan for the new Block D/E names —
**0 hits**.

### C. Soundness checks passed (attack fronts)

- **Front 1 (hallucinated citations).** One wrong file (A1), two wrong lines
  (A6, and the A3 mis-selection); no hallucinated lemma. Every cited
  declaration exists at the pin with the claimed signature.
- **Front 2 (hidden enumeration / counting / growth).** None found. See A10.
  M13/M16'' rest on `MeromorphicNFOn.zero_set_eq_divisor_support`, whose only
  hypothesis is pointwise finite **local meromorphic** order
  (`∀ u : U, meromorphicOrderAt f u ≠ ⊤`) — not a growth order.
- **Front 3 (exceptional points).** No false claim found. ξ is entire, so no
  junk value is ever reached in M1–M3, M5, M7, M9–M15; `ξ(0) = ξ(1) = 1/2 ≠ 0`
  is consistent with M3. All ζ statements are Ω-bound, and Ω excludes `1`,
  `0`, and every Γℝ pole, so both sides of every claimed ζ equality are
  evaluated at points of analyticity — the junk convention is symmetric.
  M2 inherits Order.lean:561's internal three-case discharge, so it is
  junk-symmetric by construction even for non-analytic `f`.
- **Front 4 (reflection transport).** Sound. `fun w => c - w` is ℂ-analytic
  with `deriv = -1 ≠ 0`; Order.lean:561 needs only `≠ 0`, not a sign, so
  orientation is a non-issue; the involution is `sub_sub_cancel`
  (Algebra/Group/Basic.lean:933); the composite commutes (Klein four-group),
  documented at M6. The only defect was the beta-redex (A2).
- **Front 5 (scope creep / overclaim).** Two real defects: A4 (row declared
  stale) and A5 (ζ half of the interface silently dropped while claimed
  closed). Both fixed. The statement that **`S1-CONJ` closes only if both
  packages land** was checked against repo:`MATHLIB_CAPABILITY_MAP.md:614–618`
  and is **correct as written**.
- **Front 6 (RH dependency).** None. No statement mentions
  `RiemannHypothesis`, and repo:`Xi.lean:208` (X10, the only RH-mentioning
  prerequisite) is not consumed by any M. Every dependency is either pinned
  Mathlib or a kernel-checked repo theorem. M16' in particular takes its
  finiteness from `riemannXi 0 = 1/2`, not from any zero-free region.

### D. Open items (and one blocker since superseded)

1. **RESOLVED and SUPERSEDED — the conjugation sequencing blocker is gone.**
   The 2026-08-06 review recorded a sequencing blocker on an unmerged
   conjugation package. That blocker no longer exists: the conjugation package
   is merged as PR #307 (`c277b86`), is on `main`, and is imported from
   `ResearchOS.lean`, so M5–M8, M15, M17b and M17c have no outstanding package
   prerequisite. The PR number the 2026-08-06 record carried (#306) is **closed
   and unmerged** and must never be cited as provenance; #308 likewise. This
   entry is retained only so the correction is auditable — the current
   provenance is §3 and the header Provenance paragraph, not this entry.
2. **S1M-FIN (M12) remains the package's single HIGH obligation.** The primary
   route needs `PreconnectedSpace ℂ` to resolve by instance search; that could
   not be settled by source reading alone (no Lean toolchain in this
   environment). The corrected fallbacks of A3 are believed complete but are
   likewise unexecuted. **CI is the only judge.**
3. **No elaboration was executed.** Every skeleton in this document is
   unverified by the kernel. Under the one invariant, nothing here counts as
   built until `lake build` is green with no `sorry`. In particular S1M-10
   (the `(↑) = Nat.cast` elaboration), S1M-16a (`Set.setOf_and` defeq) and
   S1M-2a/S1M-2c remain open engineering risks.
4. **No route is selected in the RH queue.** The authority for this lane is
   repo:`tasks/RIEMANN_HYPOTHESIS.md`, where `RH-002` is the sole ACTIVE task
   (`:28`; status line `:122`) and no route execution is authorized. (The
   2026-08-06 record cited `repo/ECDLP_DECISION_SUBSTRATE.json` here; that is
   the ECDLP lane's substrate and is **not** the authority for this lane —
   corrected in place.) Death condition 8 stands: this document is a statement
   design only, and nothing in it selects, unparks, or advances a route.

### E. Locator corrections made during repository integration (2026-08-06)

Every `file:line` carried over from the skeleton was re-checked against the pin
(`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`) and against the repo modules on
this branch. Six locators were wrong and have been **fixed in place** in the
text above. No locator was invented; no citation was dropped.

| # | Skeleton locator | Corrected locator | What is actually there |
|---|---|---|---|
| E1 | `Meromorphic/Divisor.lean:44–56` (the `supportLocallyFiniteWithinDomain'` discharge) | **`Divisor.lean:45–55`** | :42–44 is `supportWithinDomain'`; the local-finiteness field runs :45–55, with `codiscrete_setOf_meromorphicOrderAt_eq_zero_or_top` at :51 |
| E2 | repo:`Conj.lean:307–308` (the `hc0`/`hc1` conj-`re` idiom) | **repo:`Conj.lean:310–311`** | :306–309 is the statement of `riemannZeta_fourfold_zero`; the two `have hc0`/`hc1` lines are :310–311 |
| E3 | repo:`Conj.lean:441–447` (the rewrite occurrence-audit precedent) | **repo:`Conj.lean:443–449`** | :441 is the statement line and :442 the `conv_lhs`; the audit comment block plus its recorded fallback runs :443–449 |
| E4 | repo:`Xi.lean:250` (the `isOpen_lt continuous_const Complex.continuous_re` idiom, S1M-16a fallback) | **repo:`Xi.lean:255`** (also `:309`) | :250 is `have hs0 : s ≠ 0 := …`; the `isOpen_lt` idiom is at :255 (`hHopen`) and again at :309 |
| E5 | repo:`Xi.lean:249` and repo:`Xi.lean:212` (the `fun e => by simp [e] at h` idiom, S1M-16b fallback) | **repo:`Xi.lean:250–251`** (also `:214–215`, `:233–234`, `:318–319`) | :249 is the X11 conclusion line and :212 is `intro hRH s hz`; the idiom occurs at the four ranges listed |
| E6 | repo:`Xi.lean:240–260` (the strip-only ξ = Γℝ·ζ·unit factorization) | **repo:`Xi.lean:239–246`** | the X11 docstring making exactly this statement runs :237–246 (the substantive sentences :239–246); :248 onward is the theorem itself |

**One prose inconsistency was also repaired.** The skeleton applied finding A4
to its claim-boundary section but left the retracted wording standing in its
carrier-decision justification, where item 1 was still headed *"The divisor API
is genuinely usable at the pin — the capability-map row is stale on this
point."* That half-sentence is exactly what A4 retracted. In §1 item 1 above it
has been removed and replaced with an explicit pointer to A4 and death
condition 9: the divisor API's usability is a statement about **cost**, and the
`S1-MULTIPLICITY` row — which is about this repository's ζ/ξ layer — is **not**
stale and is not retired by it. No other prose was changed in meaning.

Additionally confirmed during integration (no change needed): Order.lean opens
`namespace AnalyticOnNhd` at :575 and closes it at :700, so the qualified names
`AnalyticOnNhd.exists_analyticOrderAt_ne_top_iff_forall` (:614) and
`AnalyticOnNhd.analyticOrderAt_ne_top_of_isPreconnected` (:624) used in S1M-12a
are correct; `sub_sub_cancel` exists as the `to_additive` twin of
`div_div_cancel` (Algebra/Group/Basic.lean:933) and is used under that name
elsewhere in the pinned tree; `Function.locallyFinsuppWithin` is the structure
at LocallyFinsupp.lean:48 with `supportLocallyFiniteWithinDomain'` as its third
field; and both the pinned and repo-side name-collision scans still return zero
hits for every proposed name.

---

## Two-stage gate and promotion ordering

This section is normative for how this document may be landed. The reviewer
requires **two separate changes**, in this order. Acceptance never implies
promotion, and **an acceptance PR must not carry a promotion.**

### Stage one — independent contract acceptance (what this document is offered for)

A review of the **statement surface M1–M17 (thirty-four public signatures) only**:
signature fidelity, hypothesis carriers, the pinned and repo-side `file:line`
locators, the claim boundary, and the death conditions.

Stage one produces, by construction:

- **no built module** — no file is added under `Ecdlp/` or `ResearchOS/`, and
  `ResearchOS.lean` gains no import;
- **no ledger row**, no entry in `data/researchos_result_registry.json` or
  `data/result_registry.json`, no line in `VERIFIED_RESEARCHOS.md`, and no
  regenerated axiom audit;
- **no kernel verdict.** A stage-one acceptance is a human/static review record
  (the sibling precedents are `notes/reviews/RH007_XI_CONTRACT_ACCEPTANCE_2026_08_06.md`
  and the `Acceptance note 2026-08-06` of `CONJ_SYMMETRY_CONTRACT.md`). It is not
  evidence that any statement elaborates, and it closes no barrier row.

The only artifacts a stage-one PR may touch are this contract, the drafts-lane
mirror `drafts/RiemannMult.lean` and its `drafts/README.md` row, and the
acceptance review record.

### Stage two — the separate built promotion PR (kernel verdict from CI)

A later, independently gated PR that carries, together in one change:

- the built module under a lake target
  (`ResearchOS/AnalyticNumberTheory/RiemannHypothesis/…`) plus its import line in
  `ResearchOS.lean`;
- one ledger row per public declaration with its declared axiom base, complete
  inverse registry coverage, and the regenerated axiom audit
  (`ResearchOS/LedgerAxiomAudit.lean`, `data/researchos_result_registry.json`,
  `VERIFIED_RESEARCHOS.md`);
- the drafts-lane mirror synchronized byte-identically from its first `import` to
  end of file;
- the promotion review record under `notes/reviews/`, and the capability-map and
  RH-queue updates the outcome actually supports.

The verdict for stage two comes from **CI, not from this document**: the full
build (`.github/workflows/ci.yml:420`), the no-incomplete-proof scan (`:359`), and
both axiom audits (`:428`, `:438`) must be green on the exact merged head. This is
the path the bridge took in PR #299 (`288d65b`), the xi package in PR #304
(`afdae08`) after its separate acceptance in PR #303 (`202eba0`), and the
conjugation package in PR #307 (`c277b86`) after its separate acceptance in PR
#301 (`7bf13ab`).

### What current CI does and does not say about the draft

`drafts/RiemannMult.lean` lies **outside every lake target**: `lakefile.toml:2`
declares `defaultTargets = ["Ecdlp", "ResearchOS"]`, the two `lean_lib` roots are
`Ecdlp` (`:10`) and `ResearchOS` (`:14`), and no file under
`domains/riemann-hypothesis/drafts/` is under either. The build step runs `lake
build` over those targets only, and the no-incomplete-proof scan covers only
`Ecdlp.lean Ecdlp/ ResearchOS/ ResearchOS.lean`. No workflow elaborates or
typechecks the drafts path.

Consequently: **a green CI run on a stage-one acceptance PR says nothing whatever
about `drafts/RiemannMult.lean`.** It is not a signal that the draft elaborates,
that any M-statement typechecks, that any name resolves, or that the package is
`sorry`-free in the kernel's judgment. Every static verdict recorded for that
draft is source reading. Under the one invariant, only a stage-two build makes a
kernel claim, and until then nothing in this package counts as proved.

### Ordering constraint

1. **`RH-002` closes first.** It is currently the sole ACTIVE task in the RH queue
   (`tasks/RIEMANN_HYPOTHESIS.md:28`; status line `:122`), open for independent
   disposition review only, with **no route execution authorized** and no route
   selected. Nothing in this contract selects, unparks, or advances a route.
2. **Then the corrected contract returns as an acceptance-only PR** (stage one),
   carrying no module, no ledger row, and no promotion.
3. **Only afterwards may the built promotion be opened as its own PR** (stage
   two), and only if the RH queue authorizes it as a separate task.

The authority for this ordering is the RH queue, `tasks/RIEMANN_HYPOTHESIS.md`;
`repo/ECDLP_DECISION_SUBSTRATE.json` governs the ECDLP lane and is not the
authority here.

### Return-to-stage-one condition

If stage two would require **any** change to an accepted statement — a weakened
hypothesis, an added or dropped signature, a renamed carrier, a new `def`, an
axiom, or a `sorry`/`admit` — promotion **stops** and the change returns to stage
one for re-acceptance. Proof-only repairs (term shapes, tactic choices, elaboration
order) do not change the statement surface and stay inside stage two, recorded in
the promotion review. A clean blocker is preferable to a promotion that quietly
edits what was accepted.
