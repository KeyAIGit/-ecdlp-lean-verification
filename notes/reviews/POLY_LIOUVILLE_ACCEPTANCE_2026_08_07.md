# Polynomial-growth Liouville contract acceptance record (UPSTREAM-POOL item 4)

Date: 2026-08-07

Status: FINAL — the six applied editorial fixes landed on the branch in the
in-flight panel-edits commit `59d5220` (post-fix contract blob `d09f5fa`
verified identical at HEAD); this record accompanies them. Format precedent
`notes/reviews/RH011_ZERO_SLICE_ACCEPTANCE_2026_08_07.md`.

## Reviewed baseline

- repository branch `claude/rimmen-hypothesis-b6gd62` at `3201153`
  (post-PR #314 `3783f31`, which landed the contract, and post-PR #315
  `9129e8c`, which landed the drafts-lane pillar files);
- reviewed object `domains/riemann-hypothesis/POLY_LIOUVILLE_CONTRACT.md`
  (919 lines pre-fix by `wc -l`, SHA-256
  `01dfede36163cbac1ef189913d6c52240645c7dee119bb45b9db388ae417c31b`, Git
  blob `b0288e473abc8d204a7d6fe408d3704edf0204ce`); post-editorial-fix state
  (957 lines) SHA-256
  `b9d4f9cf1c81254325d39389935114c103d3f582c608ccd2cf933b6d44b95174`
  (Git blob `d09f5fa97b49f20b09f98ab2fbc8eab1096fbfcc`);
- pinned Mathlib revision `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`
  (v4.31.0), re-verified by `git rev-parse HEAD` at
  `/workspace/leanprover-community/mathlib4` during this review and again at
  consolidation; repo agreement re-verified at `lake-manifest.json:8`;
- adjacent repo evidence read during the review:
  `domains/riemann-hypothesis/drafts/PolyLiouville.lean` (PR #315
  `9129e8c` — Fixes 2–3 evidence), `tasks/RIEMANN_HYPOTHESIS.md:476` /
  `:809–835` (Fix 1 evidence),
  `domains/riemann-hypothesis/MATHLIB_CAPABILITY_MAP.md:388` (`S1-GROWTH`
  row), `UPSTREAM_POOL.md:461/:462/:472`, `lakefile.toml:2`,
  `.github/workflows/ci.yml:359/:420`.

No Lean toolchain was run. Every check below is source reading; nothing in
this record is a kernel verdict.

## Authority and effect

This panel acted under **owner-delegated review authority**. The reviewed
object is an `UPSTREAM_POOL.md` §4 pool-item contract — a **generic complex
analysis** surface whose natural home is upstream Mathlib — not an RH-queue
task: the RH queue's sole ACTIVE task is `RH-012`
(`tasks/RIEMANN_HYPOTHESIS.md:809–835`), which concerns the zero-set slice
and authorizes nothing for this pool item; this acceptance neither uses nor
touches that slot. The two-stage gate of `MULTIPLICITY_CONTRACT.md`
§Two-stage gate applies verbatim, with the contract's own Mathlib-CI fork
for a possible upstream stage two. Acceptance under this record:

- covers the **statement surface only** of the polynomial-growth Liouville
  package (L1–L5, **exactly 5 public signatures**, retallied by both
  lenses);
- carries **no kernel verdict** — no Lean toolchain was run, and only the
  Lean kernel via CI (or Mathlib CI at a re-derived revision, for the
  upstream fork) can ever supply one;
- **changes no barrier row** — `S1-GROWTH`
  (`MATHLIB_CAPABILITY_MAP.md:388`, quoted verbatim and re-verified
  unchanged: "no zeta/xi vertical or order-one growth theorem") remains
  **OPEN**; both lenses independently re-confirmed that polynomial growth of
  a generic `f` does not touch the row's order-one exponential ζ/ξ scope,
  and the `MULTIPLICITY_CONTRACT.md` finding-A4 rule ("lowers cost, never
  retires a row", `:110`/`:1908`/`:1942`) applies;
- **promotes nothing and schedules nothing** — in particular it confers
  **no standing** on `drafts/PolyLiouville.lean` (see Fix 3);
- selects no route and provides no evidence for or against the Riemann
  Hypothesis.

## Panel composition

Two independent lenses, each reading the contract in full against the
pinned Mathlib checkout and the working tree:

1. **Truth-pin lens** — re-derived L1–L5 end-to-end at every point of their
   stated domains (including `n = 0`, `C = 0`, the `R = 0` junk-symmetry
   check made moot by `eventually_gt_atTop`), audited the Banach-valued
   generality (`[CompleteSpace F]` forced by the pin), and re-opened ~45
   load-bearing `file:line` locators at the pin, including the full
   SummationFilter seam (PL-2a) verified in every detail.
2. **Claim-boundary lens** — audited the claim boundary (mechanical token
   scan for ζ/ξ/`LSeries` in `lean` blocks: zero hits), the 8 death
   conditions, name freshness at the pin and on the working tree, the
   two-stage gate text and its three repo anchors, and the queue-authority
   paragraph.

## Decision: **ACCEPT WITH APPLIED EDITORIAL FIXES**

All five statements are mathematically true as stated; **no declaration
name, binder, hypothesis, conclusion, or proof skeleton changed**. Zero
blocking items. The applied fixes fall in two classes: (i) staleness-of-
status prose — the contract landed in PR #314 and was reviewed after
PR #315 (`9129e8c`) landed the implementing draft and after `RH-002` closed
the same day (exactly the RH-011 Fix-1 class); (ii) three small locator /
record-completeness corrections found by the truth-pin lens (a
section-variables line span, an omitted instance obligation, an elided
instance binder in a verbatim quote), each confirmed by direct source read
at the pin during consolidation.

## Per-lens verdicts

| Lens | Verdict | Blocking defects | Editorial fixes |
|---|---|---|---|
| Truth-pin | **ACCEPT WITH EDITORIAL FIXES** | none | 3 required + 1 optional (its Fixes 1–3 map onto consolidated Fixes 4, 2+3, 5; the optional binder-elision fix is applied as Fix 6) |
| Claim boundary | **ACCEPT WITH REQUIRED EDITORIAL FIXES** | none | 3 required (D1–D3 map onto consolidated Fixes 1, 2, 3) |

No lens returned BLOCK or REJECT. **Blocking items: none.** No inter-lens
conflict arose; the two lenses' overlapping findings (repo-side collision
staleness; drafting-status staleness) agree in substance and were merged.

## Applied editorial fixes

All six consolidated fixes were applied to
`domains/riemann-hypothesis/POLY_LIOUVILLE_CONTRACT.md` during this
acceptance session; the post-fix baseline hashes above are of the fixed
file. None touches a signature.

**Fix 1 — Queue position (boundary D1).** The stale "sole ACTIVE task is
`RH-002`" sentence in §Ordering and authority now records the dated
2026-08-07 queue decision: sole ACTIVE task `RH-012` (zero-set slice
build-out, `tasks/RIEMANN_HYPOTHESIS.md:809–835`), authorizing no route
execution and nothing for this pool item, with `RH-002`'s same-day closure
(`:476`) noted as the correction basis. The rest of the paragraph is
unchanged.

**Fix 2 — Repo-side name-collision supersession (truth-pin Fix 2 =
boundary D2).** The §Candidate fields claim "A repo-side scan also returns
zero hits" — false at head since PR #315 — now carries a dated supersession
note: the repo-side scan hits exactly one file, `drafts/PolyLiouville.lean`,
the contract's own non-built implementing draft carrying all five names
with character-identical statements; not a collision. The pin-side zero-hit
claim was re-verified at acceptance and stands; the freshness claim is
re-scoped to the pin plus the repo outside the implementing draft, with the
built targets (`Ecdlp/`, `ResearchOS/`) at zero hits. Annex C.3's parallel
sentence received a dated pointer note (the annex's frozen pre-PR-#315
record is otherwise untouched, per the RH-011 convention on frozen review
annexes).

**Fix 3 — Drafting status, two sites (truth-pin Fix 2 partial = boundary
D3).** The header's "Working name (if ever drafted in-repo)" and the
§Two-stage gate's "If instead it is ever drafted in-repo" both predated the
draft. Both sites now carry a dated note: `drafts/PolyLiouville.lean`
exists as of PR #315 (`9129e8c`), sits outside every lake target and
outside the `ci.yml:359` scan surface, carries no kernel verdict, and has
**no standing under this acceptance** — stage one accepts the §2 statement
blocks only, and any stage-two use of the draft requires an independent
character-identity check of its statements against §2 (the RH-012
pattern). The draft must never be cited as an accepted or reviewed object.

**Fix 4 — Liouville section-variables locator (truth-pin Fix 1).** The
`variable {E …} {F …}` statement of the pinned `Liouville.lean` spans
`:33–34` (re-verified by direct read at consolidation), not `:31-32` (§0
quote comment) or `:32-33` (Annex A §B). Both sites corrected to `:33-34`;
the Annex site carries the correction attribution.

**Fix 5 — `[OrderTopology 𝕜]` instance record (truth-pin Fix 3).** L1's
pinned-dependencies row for `div_tendsto_atTop_zero_of_degree_lt` omitted
the `[OrderTopology 𝕜]` obligation (variable at
`Analysis/Polynomial/Basic.lean:44`, in scope for `:161`; re-verified at
consolidation). ℝ satisfies it, so nothing breaks, but the recorded
obligation set was incomplete; the row now includes it.

**Fix 6 — `pow_le_pow_left₀` quote binders (truth-pin optional,
applied).** The §0 verbatim quote elided the `[PosMulMono M₀]
[MulPosMono M₀]` instance binders present at
`Algebra/Order/GroupWithZero/Basic.lean:470` (re-verified at
consolidation). The binders are now in the quote, preserving §0's "quoted
from the tree" discipline. ℝ satisfies both.

## Review basis (spot summary of the panel's independent checks)

1. **Mathematical truth (L1 end-to-end).** On `sphere c R`,
   `‖z‖ ≤ ‖c‖ + ‖z − c‖ = ‖c‖ + R`, so the pinned `k`-indexed estimate
   (Liouville.lean:44, verbatim incl. `[CompleteSpace F]`) yields
   `‖iteratedDeriv k f c‖ ≤ k! · C(1+‖c‖+R)ⁿ / R^k`; `0 ≤ C` genuinely
   derivable from `hC 0`; the degree chain
   `degree P ≤ 0 + n·1 = n < k = degree Q` sound in `WithBot ℕ` including
   `C = 0` (`P = 0`, `degree ⊥`); `ge_of_tendsto` orientation and
   `rw [← norm_le_zero_iff]` produce exactly the squeeze goal; the eval
   reconciliation differs from the goal only by assoc/comm (PL-1b honestly
   registered). L2's collapse (`i ∉ range (n+1) → n < i`) and
   `HasSum.unique` composition, L3's constructed polynomial, and L4/L5 all
   true as stated. Degree bounds at `n = 0` sound throughout (L1: `hC0`
   still derives `0 ≤ C`, `degree_pow_le_of_le`'s `zero` case verified at
   `:407–408`; L3: `natDegree ≤ 0` holds including the zero polynomial;
   L4's `simpa` direction and double-`rw` + `simp` closer check out).
2. **Banach-valued generality — correct and forced.** `[CompleteSpace F]`
   in L1/L2 exactly what the pin demands (estimate `:44`;
   `hasSum_taylorSeries_of_entire` under `[CompleteSpace E]`,
   TaylorSeries.lean:35); the L2 summand character-identical to the pinned
   smul-shape/factor-order at `:130`, so `HasSum.unique` needs no
   congruence step; L3's restriction to `ℂ → ℂ` forced by
   `Polynomial.eval`, with L2 correctly retaining the Banach content.
3. **Pin fidelity.** ~45 load-bearing locators re-opened at the pin across
   Liouville.lean, TaylorSeries.lean, Analysis/Polynomial/Basic.lean,
   BigOperators.lean, Degree/Defs.lean (incl. the `:402` smul-shape vs
   `:406` mul-shape distinction — exactly right), Eval/Defs.lean
   (deprecation date string `"2026-04-08"` verbatim),
   Degree/Operations.lean, Degree/SmallDegree.lean,
   GroupWithZero/Basic.lean (`@[mono, gcongr, bound]` confirmed; A1's
   residual no-`@[gcongr]`-on-degree-lemmas claim re-confirmed),
   OrderClosed.lean, AtTopBot/Defs.lean, Tendsto.lean, AtTopBot/Ring.lean,
   Normed/Group/Basic.lean, Bounded.lean, DiffContOnCl.lean,
   IteratedDeriv/Defs.lean, CPolynomialDef.lean: all verbatim except the
   two sites of Fixes 4–6. The three `UPSTREAM_POOL.md` locator corrections
   verified honest against the pool (`:461/:462/:472`).
4. **SummationFilter seam (PL-2a) — verified in full.** `HasProd` at
   InfiniteSum/Defs.lean:106 with defaulted `(L := unconditional β)`;
   `{L}` implicit at `:149`, `{f a s}` at `:194` (so the
   `(L := unconditional ℕ)` fallback is well-formed);
   `hasProd_prod_of_ne_finset_one` at `:295` with `[L.LeAtTop]` under bare
   `@[to_additive]` (`:293`); `HasSum.unique` at `:326` under
   `[T2Space α] [L.NeBot]` (`:323`); both default instances at
   SummationFilter.lean:171/:173. Death condition 5's fallback caveat
   accurate: `tprod_eq_prod` at InfiniteSum/Basic.lean:457 carries
   `[L.LeAtTop]` — same seam, as the contract's A4 recorded.
5. **Claim boundary and death conditions — held.** ζ/ξ/`LSeries` tokens
   occur only in boundary prose, never in a `lean` block; all five
   signatures quantify over arbitrary `f`; zero `def`s. All 8 death
   conditions present and internally consistent; DC1 matches the one
   invariant; DC8 closes the barrier-readout loop. `S1-GROWTH` re-verified
   OPEN and out of scope (the 2026-08-07 capability-map addendum closing
   `S1-MULTIPLICITY`/`S1-CONJ` does not interact). No repo coupling in
   either direction: every §0 dependency is pinned Mathlib.
6. **Name freshness.** Grep at `fabf563a` over `Mathlib/`: 0 hits for all
   five proposed names; L1's honesty note verified (no degree/`Polynomial`
   conclusion anywhere in pinned `Liouville.lean`; zero `∃ p : Polynomial`
   conclusions across `Analysis/Complex/` + `Analysis/Analytic/` — Annex
   C.1's no-reverse-bridge claim holds). Repo side superseded by Fix 2.
7. **Two-stage gate.** Text matches `MULTIPLICITY_CONTRACT.md` §Two-stage
   gate; all three repo anchors re-verified (`lakefile.toml:2`,
   `ci.yml:359` — drafts lane excluded from the no-incomplete-proof scan —
   and `:420`); the Mathlib-CI fork with mandatory locator re-derivation is
   sound.

## Statement disposition

| Block | Declaration | Disposition |
|---|---|---|
| L1 | `Complex.iteratedDeriv_eq_zero_of_norm_le_pow` | ACCEPT. The unique analytic node; Banach-valued, `[CompleteSpace F]` forced by the pin; `0 ≤ C` derived, not assumed; degree chain and squeeze orientation re-derived sound, including `C = 0` and `n = 0`. |
| L2 | `Complex.taylorSum_eq_of_norm_le_pow` | ACCEPT. Summand character-identical to TaylorSeries.lean:129-130, so `HasSum.unique` applies with no congruence step; PL-2a seam verified in full at the pin and remains the honestly-registered riskiest stage-two obligation. |
| L3 | `Complex.exists_polynomial_of_norm_le_pow` | ACCEPT. Explicitly constructed polynomial (no FMS extraction); `natDegree ≤ n` decision sound (holds at the zero polynomial); pointwise eval conclusion deliberate. |
| L4 | `Complex.exists_const_forall_eq_of_norm_le` | ACCEPT. Sanity anchor; double derivability against pinned `Differentiable.exists_const_forall_eq_of_bounded` (Liouville.lean:123) + `isBounded_iff_forall_norm_le` (Bounded.lean:71-72) is real; `n = 0` massage checks. |
| L5 | `Complex.exists_affine_of_norm_le_pow_one` | ACCEPT. `exists_eq_X_add_C_of_natDegree_le_one` (SmallDegree.lean:50) verbatim; `:43` fallback real. |

## Notes not conditioning acceptance (recorded so they are not lost)

- **DC7 wording looseness (boundary lens).** Death condition 7's
  parenthetical calls the `‖z‖ ^ n` shape "false to apply at `z = 0`"; more
  precisely it is a *stronger* hypothesis (it forces `f 0 = 0` for
  `n ≥ 1`), not a false one. The prohibition itself is right and the text
  is left as-is.
- **Ordering observation.** The implementing draft (PR #315) landed before
  this stage-one acceptance ran. By the letter of the gate no clause was
  violated — no built target was touched — but the ordering is now on the
  record via Fix 3 so the draft is never cited as an accepted or reviewed
  object.
- **PL-2a** (the three-lemma `HasSum` seam under the SummationFilter API)
  remains the most likely single CI bounce for any stage two; the
  `(L := unconditional ℕ)` pin and the `tsum` fallback (same seam, one
  fewer lemma) are both real at the pin.
- The `R = 0` junk-symmetry of the eval reconciliation (`x/0 = 0` on both
  sides) is moot under the `eventually_gt_atTop` restriction but was
  checked anyway.

## Gate result and limits

Stage-one acceptance of the 5-signature polynomial-growth Liouville
statement surface is complete: **ACCEPT WITH APPLIED EDITORIAL FIXES** —
six consolidated fixes applied (five required, one optional quote-fidelity
fix), all prose/locator-only, zero blocking items, zero statement changes.

Stated plainly, the limits of this record:

- **No kernel verdict.** No Lean toolchain was run; nothing here is
  Lean-checked. Under the one invariant, only the Lean kernel via CI — or,
  for the upstream fork, Mathlib CI at whatever revision that PR targets,
  with every locator re-derived there — can verify L1–L5, and that judgment
  has not occurred.
- **No barrier-row change.** `S1-GROWTH` remains **OPEN**; no capability-map
  row is closed, weakened, or re-scoped by this acceptance.
- **No promotion, no standing for the draft.** Nothing was promoted,
  imported into the build, or scheduled. `drafts/PolyLiouville.lean` gains
  no standing from this record; any stage-two use of it requires an
  independent character-identity check against §2.
- **No route selection, no queue movement.** The RH queue's ACTIVE slot
  (`RH-012`) is untouched; no `targets/*.json` movement follows.
- **No claim about RH.** This record provides no evidence for or against
  the Riemann Hypothesis.
