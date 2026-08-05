# RH-002 route triage record

Status: **executed 2026-08-05 — dispositions `PARK` / `PARK` / `PARK`, no
`SELECT`; pending independent disposition review**

This document is the `RH-002` output: one source-anchored desk screen per
admitted route family, matched budgets, an explicit disposition for every
route, and the honest outcome that **no theorem-bearing route is selected**.
It claims no proof and no progress on the Riemann Hypothesis. Per the
`RH-002` exit criteria, these dispositions become final only after
independent mathematical review of all three, with source locators replayed
by a second agent; until then this record is a first-agent output.

## Inputs and admitted candidates

Candidates admitted from `RH-001` (exactly three, per the capability map's
"RH-002 admission decision" table): Weil-first Li positivity,
Nyman-Beurling/Báez-Duarte closure, and the explicit-formula-plus-global-
inequality family. The de Bruijn-Newman route, mollifier sweeps, spectral
analogies without an identified operator, and bounded zero computation were
never admitted and stay `PARK`/evidence-only.

Inputs: `MATHLIB_CAPABILITY_MAP.md` (independently replayed 2026-08-05 with
0 mismatches — `notes/reviews/RH001_INDEPENDENT_REPLAY_2026_08_05.md`),
`SOURCE_CONTRACTS.md` (still "proposed under independent review"),
`corpus.md`, and the pinned Mathlib tree at
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`.

## Matched budgets (actually spent)

| route | desk-review budget spent | execution budget spent |
|---|---|---|
| Weil-first Li | one full desk-screen session at the same effort tier as the others | 0 |
| Nyman-Beurling/Báez-Duarte | one full desk-screen session, same tier | **0% of the 20% pilot cap** |
| explicit formula + inequality | one full desk-screen session, same tier | 0 |

All three screens ran against the same preregistered day-45 evidence bars and
death conditions frozen in the capability map's admission table before this
cycle. No compute, no model sweep, and no Lean execution was authorized or
performed.

## Citation policy for this record

Sources already pinned with locators and checksums (`LAG07`, `BOM-CLAY`,
`BD02-v2` in `SOURCE_CONTRACTS.md`; `RH-SRC-001..008` in `corpus.md`) are
cited by those IDs. All other literature references below are **desk-level
citations** from the screening session; the independent disposition review
must pin exact locators for every load-bearing one before the dispositions
become final. Load-bearing desk citations are marked `[D]`.

---

## Route A: Weil-first Li positivity — `PARK` (direct screen); alive as formalization lane

**Bar (preregistered):** a named unconditional theorem with explicit
variables, constants, and range, plus a proved chain to `Re λ_n` for
unbounded `n` whose remainder beats a preregistered positivity/coercivity
threshold on an infinite tail.

**Survey verdict: no published unconditional theorem meets or approaches the
bar — and any theorem meeting it would itself be a proof of RH.**

- Li 1997 (`RH-SRC-003`, Thm 1): RH ⟺ `λ_n ≥ 0` for all `n ≥ 1`. Pure
  equivalence; no unconditional lower bound on any `λ_n`.
- Bombieri-Lagarias 1999 (`RH-SRC-004`): the abstract multiset criterion
  (under the (1.6) summability hypothesis) is an equivalence; the arithmetic
  representation of `λ_n` via the explicit formula is an identity that
  relocates the difficulty into an oscillatory prime-power sum with no
  unconditional bound; the (1.6) hypothesis is itself a contract obligation
  (`SC-LI-01`), not a free premise.
- `LAG07`: Thm 2.4 (one-sided criterion) is an equivalence; Thm 3.1 (Weil
  Gram identity `‖G_n‖²_W = 2 Re λ_n`) is an unconditional identity between
  two quantities neither of which is unconditionally bounded below; the
  growth `λ_n = (n/2) log n + c₁ n + O(√n log n)` is proved only under
  GRH-type hypotheses.
- Coffey's explicit expansions `[D]` prove the archimedean/trivial part
  `A(n) = (n/2)(log n + γ − 1 − log 2π) + O(1)` unconditionally; the
  oscillatory prime part is bounded only by an unproved conjecture. The
  proved chain stops strictly short of `Re λ_n`.
- Arias de Reyna `[D]`: rigorous archimedean asymptotics and sharpened
  equivalences only.
- Voros 2004/2006 (Sharpenings of Li's criterion) `[D]`: unconditional
  dichotomy — under RH, `λ_n` grows temperedly `~ (n/2)(log n + γ − 1 −
  log 2π)`; if RH is false, `Re λ_n` oscillates with exponentially growing
  amplitude and is negative infinitely often. This is a named unconditional
  theorem, but it **proves the bar unreachable short of RH**: tail
  positivity `Re λ_n ≥ 0` for all `n ≥ N₀` already forces RH.
- Finite numerics (Keiper, Maslanka, `n ≲ 10⁵`) `[D]`: bounded computational
  evidence only, per the corpus rules.

**Death conditions already triggered at desk time** (4 of 6 from the
admission row): "only definitions/equivalences"; "finite positive
coefficients or PSD blocks, numerics"; "a bound with no strict asymptotic
margin"; "an RH-equivalent premise" — decisively, the day-45 target itself
is RH-equivalent via Bombieri-Lagarias + Voros oscillation, so executing the
direct screen guarantees a death-condition outcome.

**Disposition: `PARK` as a direct research screen.** `STOP` would be wrong:
nothing refutes the framework; the Lagarias Weil-Gram structure is a sound
equivalence lane whose dependency chain (xi bridge, divisor, Hadamard,
explicit formula) is exactly the shared infrastructure Route C's dependency
screen also needs. Recorded status: **PARKED-DIRECT /
ALIVE-AS-FORMALIZATION-LANE**.

**Reconsideration triggers (preregistered):**

- `A-T1`: peer-reviewed unconditional bound on the prime-side term `P(n)` of
  the form `|P(n)| ≤ (1−η)·A(n)` with explicit `η > 0` and explicit `N₀` on
  an infinite tail — to be triaged at full RH-proof severity, since it
  implies RH;
- `A-T2`: any published unconditional `Re λ_n ≥ ε·n` on a tail (same
  severity note);
- `A-T3`: a materially new positivity mechanism for the Weil quadratic form
  provably not an RH restatement (corpus rule 4);
- `A-T4` (cost-only): Mathlib gains Hadamard factorization, order-one growth
  for completed L-functions, or a Riemann-Weil explicit formula.

**Preregistration binding any revival:** conventions frozen per
`SOURCE_CONTRACTS.md` (`S_xi` per Gate 0; multiplicity
`analyticOrderNatAt riemannXi ρ` counted exactly once; `λ_n` by the
`SC-LI-02` star limit with radial cutoff `|ρ| ≤ T`; no `tsum` substitution;
no cutoff swap without `SC-BRIDGE-02`). Parameter: the Li index `n → ∞`,
full tail, not a subsequence. Threshold: `θ(n) = ε·n` with declared `ε > 0`
and explicit `N₀`; equivalently explicit `η > 0` with `|P(n)| ≤ (1−η)A(n)`
for all `n ≥ N₀`, all O-constants explicit. Strict margin:
`liminf_{n→∞} Re λ_n / θ(n) ≥ 1` with `θ(n) → ∞`; explicitly NOT satisfied
by `Re λ_n ≥ 0` with no growing margin, any finite range, unspecified
constants, uniform non-decaying bounds, subsequence positivity, finite PSD
Gram blocks, or numerics. Anti-circularity: no RH/GRH-equivalent premise
(zero-freeness in `re > 1/2`, RH-Lindelöf, tempered `λ_n` growth); the
BL (1.6) summability and star convergence must be derived from a proved
counting theorem, never assumed; all three Gram-identity terms from one
common finite cutoff. Recorded consequence: any claim satisfying this block
implies RH and is triaged at the repository's highest review severity.

---

## Route B: Nyman-Beurling/Báez-Duarte closure — `PARK` as route-to-RH; foundation objects clean

**Bar (preregistered):** a concrete natural-span family `F_N`, a complete
identity for `‖χ − F_N‖²`, and an explicit unconditional bound `B(N)` with
proved `B(N) → 0` at a preregistered rate.

**Structural reason the bar is unreachable today:** `χ ∈ closure(B_nat)`
implies RH **unconditionally** (the closure→RH direction of `BD02-v2`
Thm 1.1 via the classical Nyman-Beurling criterion; only the RH→closure
direction uses RH-dependent Littlewood/Lindelöf input, per `SC-NB-05`). An
unconditional proved `B(N) → 0` would therefore literally be a published
proof of RH. None exists; the bar is logically equivalent in strength to RH.

**Survey of the closest unconditional results** — everything divides into
identities, equivalences, and obstructions:

- identities: Vasyunin's closed-form Gram entries `⟨ρ_a, ρ_b⟩` via cotangent
  sums `[D]`; Bettin-Conrey reciprocity for those cotangent sums `[D]` —
  admissible unconditional ingredients for the norm identity, but no
  coefficient choice with a proved decaying bound;
- equivalences: Nyman, Beurling, Báez-Duarte 2002/2003 (`RH-SRC-005` /
  `BD02-v2`), Balazard-Saias `[D]`;
- obstructions: the BDBLS/Burnol unconditional lower bound
  `d_N² ≥ (Σ_{ρ distinct} 1/|ρ|² + o(1)) / log N` `[D]`, and the `BD02-v2`
  (1.2) universal bound `‖F − χ‖ ≥ C/√(log N(F))` — the distance cannot
  decay faster than order `1/log N`, and the matching upper asymptotic
  `d_N² ~ (2 + γ − log 4π)/log N` is known only under RH (plus simplicity
  hypotheses in the sharpest forms).

**Death conditions already triggered pre-execution:** "a uniform but
non-decaying bound" (the only unconditional upper-bound type available);
"unconditional use of RH-derived Littlewood/Lindelöf or zero-free
`re(s) > 1/2` input" (the sole published decay mechanism is exactly this
chain); "the divergent raw family `Σ_{a≤N} μ(a) ρ_a`" (rejected by the
source itself, `BD02-v2` (1.1), and by `SC-NB-06`). Burnol's lower bound
additionally pre-falsifies any preregistered rate faster than order
`1/log N` — such a rate is an automatic `STOP` at preregistration time.

**Disposition: `PARK` as a route to RH. 0% of the 20% pilot execution cap
spent, and none should be spent** hunting an object whose existence proof is
RH. The route's **foundation objects remain clean and valuable**:
`SC-NB-01` (measurability, `L²` membership, dilations, spans of `ρ_a` —
`measurable_fract`-class and `rpow`-integrability API present at the pin),
`SC-NB-03` (the Mellin identity `−ζ(s)/s = ∫₀^∞ x^{s−1} ρ₁(x) dx` on
`0 < re(s) < 1` — de-risked by the present Abel-summation machinery
`LSeries_eq_tsum...`/`LSeries_eq_mul_integral`,
`Mathlib/NumberTheory/LSeries/SumCoeff.lean:137`), and `SC-NB-04` (the
Fourier-Mellin unitary — de-risked by the newly recorded Fourier-Plancherel
`L²` capability, `Mathlib/Analysis/Fourier/LpSpace.lean:50,89`). These are
formalization-only items, ordered strictly after the route-neutral bridge
and `S0-TRUST`, and are not progress on RH.

**Reconsideration trigger** `B-T1`: a new peer-reviewed unconditional
quantitative theorem changing the structure — e.g. an unconditional `o(1)`
upper bound for any modified natural-span family (RH-grade news, triaged as
such), or an unconditional change to the Burnol lower-bound landscape.

**Preregistration binding any future pilot:** parameter `N → ∞` declared as
the scale `N(F_N) = max_k a_k` over positive-natural indices (not the term
count); family and coefficients frozen before any bound is computed; a
complete proved identity for `‖χ − F_N‖²_H` in `H = L²((0,∞), dx)`
(Vasyunin/Bettin-Conrey entries admissible); an explicit unconditional
`B(N)` with proved `B(N) → 0`, admissible target window only
`B(N) = C/log N + o(1/log N)` with
`C ≥ Σ_{ρ distinct} 1/|ρ|²`; `limsup_{N→∞} B(N)·log N` proved finite with an
explicit value; no Littlewood/Lindelöf/zero-free-`re>1/2` input outside an
explicit RH hypothesis; no unquantified iterated limits passed off as a
diagonal family; the raw Möbius family and any mollified variant require
their own pinned source contract. Satisfying this block unconditionally is
equivalent to proving RH; it is recorded so future claims are judged against
it, not because it is expected to be met.

---

## Route C: explicit formula + global inequality — `PARK` as direct route confirmed; mandatory dependency screen for Route A

**Bar (preregistered):** a named test family with frozen function,
parameters, norm, transform, and a proof that its bound excludes an
individual off-line zero at arbitrary height.

**Survey verdict: nothing published has the required shape, for structural
reasons:**

- zero-free regions (de la Vallée Poussin; Vinogradov-Korobov `[D]`) exclude
  individual zeros only in a region shrinking to `re = 1`; for any fixed
  `β > 1/2` the exclusion holds only up to bounded height; no uniform
  vertical-strip zero-free region `σ ≥ σ₀ < 1` exists;
- zero-density estimates (Ingham, Huxley, Bourgain, Guth-Maynard `[D]`) are
  cardinality upper bounds `≥ 1` in the relevant ranges — structurally
  incapable of excluding a single zero (the map's semantic-mismatch register
  already records this);
- Weil positivity results: Weil's positivity ⟺ RH is an equivalence;
  Yoshida `[D]` and Connes' trace-formula program `[D]` prove positivity
  unconditionally only on restricted/truncated classes; Connes-Consani
  finite/low-frequency positivity `[D]` is support/bandwidth-restricted, so
  it can only certify zero-freeness already covered by bounded-height
  verification (`RH-SRC-007`); the support parameter does not tend to
  infinity with controlled constants;
- mollifier/proportion results (Selberg; Levinson ≥ 1/3; Conrey ≥ 40%;
  Pratt-Robles-Zaharescu-Zeindler > 41.7% `[D]`) bound the proportion of
  on-line zeros and exclude nothing off-line;
- bounded-height verification (`RH-SRC-007`, to 3·10¹²) is finite by
  definition.

Meeting the bar for even one fixed off-line abscissa uniformly in height
would already imply a vertical-strip zero-free region — strictly beyond the
entire literature.

**Death condition in force:** "family still unnamed" — in the repository and
in the literature.

**Disposition: `PARK` as a direct route (confirmed adversarially);
`REQUIRED DEPENDENCY SCREEN` for Route A retained**, since the Route A DAG
consumes the same explicit formula (`SC-BOMB-01/02/03`, `SC-BRIDGE-01..04`),
with budget charged to Route A. On formalizability: the Riemann-Weil trace
formula is unconditionally provable classical mathematics but is a
**program, not a theorem-sized target**, at the pin — the missing chain is
(i) target bridge (theorem-sized, prerequisites present), (ii) xi package
(theorem-sized-though-large), (iii) multiplicity-aware divisor (moderate,
generic API present), (iv) vertical growth of zeta/xi in strips (missing,
serious; only real Stirling exists), (v) `N(T) ≪ T log T` with multiplicity
(moderate once (iii)+(iv) exist, via the present generic Jensen formula),
(vi) Landau-type log-derivative lemmas (`Complex.borelCaratheodory` now
recorded as present helps), (vii) the contour shift for the weak Bombieri
class with the strict `|im ρ| < T` cutoff (large; the `SC-BOMB-03`
regularity bridge is a genuine blocker). Order of magnitude: comparable to
or larger than the PrimeNumberTheoremAnd analytic core — plausibly 10k-30k
lines of new Lean, decomposable, of which only (i)-(iii) are cheap. No
Route-C-specific Lean work is justified while parked.

**Reconsideration triggers (preregistered; each reopens desk review only,
never auto-`SELECT`):** `C-T1`: published, independently checked
unconditional Weil-form positivity (or Bombieri negativity) on a test class
whose support/bandwidth parameter provably tends to infinity with explicit
constants; `C-T2`: a published unconditional vertical-strip zero-free region
`σ ≥ σ₀`, `σ₀ < 1`, uniform in `t`; `C-T3` (cost-only): upstream Mathlib
explicit-formula/vertical-growth/Hadamard infrastructure.

**Preregistration binding any revival:** a frozen family `{g_{δ,h}}` with
exact functional form; frozen parameters (`δ` = off-line distance, `h` =
height); frozen norm; frozen `SC-BOMB-01` Mellin convention; frozen strict
`|im ρ| < T` cutoff with multiplicity, and a proved `SC-BRIDGE-02`
conversion if any `|ρ| ≤ T` object is used; exclusion margin
`m(δ,h) ≥ c(δ) > 0` on the entire tail `h ≥ h₀(δ)` with explicit `h₀` and
`liminf_{h→∞} m(δ,h) > 0`; no RH-equivalent premise; conventions replayed
independently per the `SC` contract rules.

---

## RH-002 outcome

1. **No theorem-bearing route is `SELECT`ed.** All three admitted families
   are `PARK`ed with scoped reasons, preregistered revival bars, and
   reconsideration triggers, as recorded above. This satisfies the `RH-002`
   requirement "at most one selected theorem-bearing candidate" by selecting
   zero, and it is the honest reading of the evidence: each route's day-45
   bar is provably unreachable short of RH itself.
2. **The successor work item is foundation, not route execution.** Per the
   capability map's "First implementable foundation and stop rule", the next
   kernel-checkable step is the **route-neutral target-equivalence bridge**,
   which closes the named barrier `S1-TARGET`. Under corpus rule
   "equivalent restatements are not progress unless they remove a named
   barrier", this qualifies as admissible foundation work — and it is
   explicitly **not** counted as a selected route, **not** counted as
   progress on RH, and **not** buildable before `S0-TRUST` closes.
   `RH-003` is activated on this basis; its frozen contract is
   `TARGET_BRIDGE_CONTRACT.md`.
3. **90-day exit clause 5** ("either one kernel-checked missing foundation
   or an honest `PARK`/`STOP` decision") is on track via the foundation
   path: this cycle delivers the honest `PARK` decisions plus a frozen,
   adversarially reviewed foundation contract; the kernel check itself
   remains gated on `S0-TRUST` and independent review (`RH-004`).
4. **Pending for finality:** independent mathematical review of all three
   dispositions; second-agent replay of every `[D]` citation's exact
   locator; acceptance review of `SOURCE_CONTRACTS.md`.
