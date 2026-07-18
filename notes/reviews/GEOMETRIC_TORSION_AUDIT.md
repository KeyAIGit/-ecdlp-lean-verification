# Geometric-torsion audit — PRs #172 / #173 / #174 (adversarial, 2026-07-16)

Adversarial audit and generalization review of the geometric-torsion branch. Companion
documents: `PR172_SPLIT_PLAN.md` (work package B), `PROMOTION_GATE_DESIGN.md` (work
package F). The generic-API deliverable (work package C) is
`Ecdlp/Proved/TorsionCounting.lean` on this branch. The **full** per-declaration tables
(exact verbatim signatures, hypotheses, evidence class, "does not follow",
counterexample-if-dropped, plus each row's independent verifier verdict) are the
machine-readable `geometric_torsion_audit_tables.json` beside this file; the tables below
are the trimmed human view.

**Method.** Role-separated agents: per-layer auditor → independent adversarial verifier
(re-opened the sources, re-checked every quoted signature and hypothesis), then two
distinct designers (generic API, promotion gate), integrated by the session agent. 18
agents, 0 errors, ~1.7M tokens. Every quoted `exact_type` was re-checked against the PR
branches fetched locally.

**Ground rule:** a green CI build proves the kernel accepted the stated *types* — it does
not certify the *prose* says what the types say. That gap is the entire subject here.

## 0. Fixed inputs (verified)

| Ref | Value | Verified how |
|---|---|---|
| `main` | `ac1ec94` | local `origin/main` |
| PR #172 head | `5f61fa5` (`claude/repo-analysis-next-steps-btomml`, 22 commits) | GitHub API + local fetch |
| PR #173 head | `5187d70` (`claude/agi-final-technology-usdtmk`, 9 commits) | GitHub API + local fetch |
| PR #174 head | `b867e1d` (this session's own PR; the spec's `223fdea` + engine hygiene, TASK-005 memo, graph resync, **scope-correction `b867e1d`**) | local |
| Merge-base of #172/#173 vs `main` | `847ac5a` (both cut pre-#169/#170/#171) | `git merge-base` |

**CI (check runs, GitHub API):** #172 @ `5f61fa5` — `build`×2 + `docs-sync` all `success`.
#173 @ `5187d70` — `build`×2 + `docs-sync` all `success`. #174 — `build` green through
`f2ace33`; `b867e1d` re-verifies.

**Merge-surface facts (`git diff origin/main...`):** #172 adds exactly **13 new Lean
modules** (+`Ecdlp.lean` imports + docs/scripts); its copies of `TorsionStructure.lean` /
`DivisionPolynomialEvalBridge.lean` are **byte-identical** to `main` (no silent fork). #173
adds exactly **one** module (`TripleDivisionPolynomial.lean`); its copies of main files are
identical too. The three counting scripts (`check_counts.py`, `gen_stats.py`,
`gen_status.py`) are **byte-identical blob hashes** on `main` and `5f61fa5` — #172 changed
counted *data*, never counting *rules*.

## 1. Evidence classes (adopted)

`kernel_theorem` (exact type, kernel-accepted) · `derived_corollary` · `certificate`
(checked computation + validator) · `measured_evidence` (experiment, fixed params only) ·
`literature` (sourced, unformalized) · `open_hypothesis`. Rule: **no prose stronger than
the type**; algorithmic conclusions never follow from an algebraic identity or a small
experiment (P0–P4 GLV–Semaev stay `measured_evidence`).

## 2. Theorem audit — PR #172 (work package A)

**Bottom line: the mathematics is sound at the kernel level.** Across all five layers, the
adversarial verifier confirmed the headline types match their claims; the ~13 CORRECTED
rows (of ~69) are prose/trust-disclosure corrections, not soundness defects. No `sorry`, no
custom axioms; the whole chain does rest transitively on `native_decide` Bézout/​squarefree
certificates (an existing TCB class, see red flags).

### Layer 1 — EDS rigidity & coprimality (`NormEDSConsecutiveZeros`, `DivisionPolynomialCoprime`, `CoprimePsi2Psi7`)

| Declaration | Field | Class | Does **not** follow |
|---|---|---|---|
| `normEDS_not_consecutive_zeros` | any integral domain | kernel_theorem | no curve/torsion; b,c,d nondegeneracy discharged elsewhere; not the full "zeros = ρℤ" theorem |
| `normEDS_shift_mul_shift_of_eq_zero` | generic CommRing | kernel_theorem | zeros do **not** propagate without a domain + nonzero neighbours |
| `normEDS_sub_eq_zero_of_eq_zero` | generic domain | kernel_theorem | neighbour-nonzero is a separate case; not divisibility directly |
| `secp256k1_isCoprime_Φ_ΨSq` (all `n:ℤ`) | 𝔽_p[X] | kernel_theorem | says nothing over 𝔽̄_p by itself; N5 is the *coprimality*, not the torsion count |

This layer **is** the N5 scalar statement that PR #174's open stem
(`normeds_no_consecutive_zero`) targets — confirming the supersession note there.
**Red flags:** (1) `CoprimePsi2Psi7` docstring sells "E[2]⊥E[7]: no nonidentity point is
simultaneously 2- and 7-torsion" and "y≠0 at every root of preΨ₇", but the *type* is only
`IsCoprime Ψ₂Sq (preΨ' 7)` over 𝔽_p[X] — the roots→points reading is unformalized here.
(2) `DivisionPolynomialCoprime` advertises "No native_decide in this file" while its
headline transitively depends on 10+ `native_decide` Bézout calls in the imported
`CoprimePsi*` certificates — trust is systematically understated. (3) Ward-hypothesis
sharpness (`¬(b=0∧c=0)`, `¬(c=0∧d=0)`) is claimed "sharp/both necessary" in prose but never
formalized as counterexample lemmas.

### Layer 2 — multiplication formulas (`TripleMultiplicationFormula`, `QuintupleMultiplicationFormula`)

`x(3•P)=Φ₃/ΨSq₃` and `x(5•P)=Φ₅/ΨSq₅` — kernel theorems. **Correction:** not "side-condition
free" as the PR prose says — they carry the `y≠0` / non-2-torsion branch via imported
coprimality; the equality is of field elements after the division is justified, at points
where `ΨSq n ≠ 0`. Statement is over the base field points, not the closure.

### Layer 3 — squarefree / separability & exact root counts (`DivisionPolynomialSquarefree`, `DivisionPolynomialSeparable`)

Squarefree/separable of the division polynomials for `n∈{3,5,7}` and the exact distinct-root
counts `(n²−1)/2`. **Corrections:** the exact-count statements are `Finset`/`Nodup` facts
about roots **over 𝔽̄_p** (correctly, `AlgebraicClosure`), and the squarefree→closure-count
implication *is* proved here (not assumed) — the auditor initially under-credited it. Rests
on separability certificates (`native_decide`).

### Layer 4 — closure torsion bridges (`{Three,Five,Seven}TorsionBridgeBar`)

`n•P = O ⟺ ψₙ(P)=0` over `AlgebraicClosure (ZMod p)`, all three genuinely re-proved over the
closure (both `mp` and `mpr`), quantified over affine `P` with the `y=0` branch handled.
Confirmed. **Red flag:** the PR calls them "token-identical ports" of the 𝔽_p bridges — true
of the tactic scripts, but the closure statements are genuinely new content (the 𝔽_p
versions are vacuous for closure counting), so "token-identical" *undersells* them while the
count treats one as a fresh distinct result (see §5).

### Layer 5 — counting + structure assembly (`{Three,Five,Seven}TorsionStructure`) — the crux

| Declaration | Field | Class | Note |
|---|---|---|---|
| `secp256k1Bar_{three,five,seven}_torsion_structure` | 𝔽̄_p | kernel_theorem | `E[ℓ](𝔽̄_p) ≃+ ZMod ℓ × ZMod ℓ`, ℓ∈{3,5,7} |
| `…_torsionBy_card` | 𝔽̄_p | kernel_theorem | `Nat.card E[ℓ] = ℓ²` (9/25/49) |

The counting chain is **sound as written**: `card = 1 + 2·((ℓ²−1)/2)` via an explicit
`Finset` (insert `O` into two disjoint images), injectivity by `x`-projection, disjointness
from `y ≠ −y` (`char ≠ 2` by `decide p∤2`), `y ≠ 0` from a transported `Ψ₂Sq ⊥ ψₙ` Bézout
cert, `O` excluded by `Point.some_ne_zero`, roots→points by `exists_nonsingular_y` over
`IsAlgClosed`, and the bridge `iff` quoted verbatim from Layer 4. **No `Fintype`/`Finite`
assumed** — `Nat.card` is used and finiteness is derived. The N10(iii) lemma
`nonempty_addEquiv_zmod_prod_of_card_eq_sq` (on `main`) has its `[Fact ℓ.Prime]` / kill /
card hypotheses genuinely discharged at each site. **Does not follow:** anything about
`E(𝔽_p)[ℓ]` over the base field (trivial there — group order is the ~2²⁵⁶ prime `n∤ℓ`); any
uniform-`n` statement; any *canonical* isomorphism (`Nonempty` = noncomputable choice); any
Galois-equivariance or pairing compatibility; anything about ECDLP. **Red flag:**
`SevenTorsionStructure`'s header claims the file has "no `decide`" — false (char≠2 uses
`decide`); and the per-file "no native_decide" prose contradicts the transitive certificate
dependency.

**Duplication (feeds work package C).** The three files are near-verbatim copies of **one
18-role skeleton**, identical declaration order, ~400 lines each. The *only* genuinely
per-ℓ inputs are four: `{bridge iff, root-count pair, coprimality cert, prime fact}`. The
base-change hom is privately re-declared ≥5× across the PR (`φ_cl`×3, `φ_ac`, `φ_K`,
`φ_bar`) — all definitionally `algebraMap`. This is exactly the ~1200-line redundancy the
generic API removes.

## 3. PR #173 review (work package D)

`TripleDivisionPolynomial.lean` — 4 unconditional identities over 𝔽_p (`secp256k1_Φ₃`,
`secp256k1_ΨSq₃`, and the evals `Φ₃(x)=x⁹−672x⁶+2352x³+21952`, `ΨSq₃(x)=9x⁸+504x⁵+7056x²`).
All `kernel_theorem`, no hypotheses. **Findings (verifier-confirmed):** #172 **mathematically
subsumes 100 %** of #173 — its `TripleMultiplicationFormula.lean` re-proves the two eval
identities as *private* lemmas (proposition-identical) and goes strictly further to the
point-level `x(3•P)=Φ₃/ΨSq₃`. #173's only additive value is *public naming*. **Zero name
collisions** in the "merge #173 first, rebase #172" order (`#172` uses `Φ₃_eval`/`ΨSq₃_eval`,
private; `#173` uses `secp256k1_Φ₃_eval`/`secp256k1_ΨSq₃_eval`, public; disjoint `Ecdlp.lean`
hunks). Both PRs rewrite the same **14** generated artifacts (incl. `BARRIERS.md`) — resolve
by regeneration, never hand-merge. Docstring oversell: degree facts (9=3²) and the `x(3•P)`
framing are prose, not types, in this module. Vestigial imports (`FourDivisionPolynomial`,
`DivisionPolynomial`). **Recommendation:** merge #173 first (cheap, atomic); after #172
lands, dedup its private copies via `import Ecdlp.Proved.TripleDivisionPolynomial`.

## 4. PR #174 review (work package E)

The spec's critique is **confirmed and already remediated** on this session's branch
(`b867e1d`): the ℓ=11,13 modules prove only `natDegree (preΨ' ℓ)` (60/84), `ne_zero`, and
`Multiset.card roots ≤ bound` **over 𝔽_p** (with multiplicity) — **no ℓ∈{11,13} torsion
bridge exists** anywhere in the repo (bridges stop at ℓ=7), and the base field's `E(𝔽_p)[ℓ]`
is `{O}` anyway. Applied: theorems renamed `*_torsion_x_card_le → *_preΨ_roots_card_le`;
docstrings gained "what is NOT proved here" blocks; the six `VERIFIED.md` rows narrowed to
polynomial-layer claims. **One correction to the audit itself** (verifier): the global
`Fact p.Prime` instance is **not** load-bearing for the `natDegree`/`ne_zero` theorems — at
Mathlib v4.31 `natDegree_preΨ'` needs only `[CommRing R]` + `(n:R)≠0`, and
`ZMod.natCast_eq_zero_iff` is typeclass-free; the Pratt certificate enters only the two
`card_le` theorems (whose `.roots` needs `IsDomain`). So those docstrings are type-accurate.
**Verifier-found live bug (see §5): `explore.html` still shows a stale `228 ledger rows`.**
**Open recommendation for the maintainer:** mark the 3/5/7/11/13 degree-rung rows as one
*family/instance unit* in the alternate-form discount (uniformly, not just 11/13); Mathlib
v4.31 even has `preΨ'_ne_zero`, so the `ne_zero` rungs are one-line instances of an existing
lemma.

## 5. Counting-script changes & count integrity (anti-inflation invariant)

**#172 changed no counting rules** (byte-identical scripts). The change is data-side: 12 new
ledger rows (248→260), alternate-form held at 39, mechanically forcing distinct 209→221 and
the public badge to `221 (260 rows)`. All gates pass at the PR head. **The structural
finding (verifier-confirmed):** the anti-inflation invariant is **arithmetic only** —
`rows − alternate-form = distinct` is enforced, but *which* rows are alternate-form is a
hand-stated constant (39), so distinctness rests entirely on PR review. #172 classified 0 of
12 new rows as restatements; ~±2 results of unaudited curation latitude live in the +12
(the `ρ-descent` supporting row shares its module with the theorem it supports; a
`ThreeTorsionBridgeBar` row self-describes as a "token-identical" port), partially offset by
E[5]/E[7] each folding two modules into one row.

**Live drift the gates miss (verifier, sharpest item):** `explore.html` carries
`<div class="n">228</div><div class="l">ledger rows</div>` on **both** `main` and every PR
head — and it escapes **every** gate (`check_counts.py`'s DOCS whitelist excludes it,
`check_status_consistency.py` reads only `index.html`/`dashboard.html`/`knowledge_graph`,
`docs-sync` never regenerates it; the digits are split across HTML tags so even a substring
scan could not catch it). This is ROADMAP §7 item 7 (ungated public surface) made concrete.
Secondary count-machinery gaps: retired-figure matching is exact-substring and
tilde-dependent (`~M distinct`); `re.search` first-match + retired-set-below-current means a
stale **higher** figure fails open; no table-identity anchoring above the `### Coverage
restatements` cutoff. These feed the promotion-gate design's §3.6 (typed registry → derived
headline counter) and are recorded here as backlog, not fixed in this PR.

## 6. Recommendations & merge order

1. **Merge order: #173 → #172 (as a split) → #174 (independent).** #173 is atomic and
   upstream of #172's `n=3` content; #174 shares only mechanical surfaces.
2. **Extract the generic counting API before landing the 3/5/7 copies.** This PR ships the
   candidate `Ecdlp/Proved/TorsionCounting.lean` (`torsion_card_of_divpoly_data` +
   `nonempty_addEquiv_zmod_prod_of_divpoly_data`); on green CI, #172's three structure files
   become thin instances (per-ℓ inputs only), cutting ~1200 duplicated lines. See
   `PR172_SPLIT_PLAN.md`.
3. **#172 docstring corrections before merge** (prose > type): `CoprimePsi2Psi7` header
   (`IsCoprime` only, not "E[2]⊥E[7] points"); disclose the transitive `native_decide`
   dependency in `DivisionPolynomialCoprime`; fix `SevenTorsionStructure`'s false "no decide".
4. **Count integrity:** re-bucket the `ρ-descent` supporting row and one bridge port as
   alternate-form (39→41) at #172 merge; fix or retire the `explore.html` stale counter
   (ROADMAP §7.7); harden the count machinery per the promotion-gate §3.6 typed-registry
   design (stale-high fail-open, tilde phrasing, table-identity anchoring).
5. **Promotion integrity:** land the fail-closed gate (`PROMOTION_GATE_DESIGN.md`), M0
   immediately — it closes the seven #160 gaps that a green CI + the current promoter do not.
6. **#174 (this session):** add non-headline instance markers to the six 11/13 rows; land the
   already-applied scope narrowing.

---
*Provenance: role-separated agents (auditor / adversarial verifier per layer; distinct
designers for the generic API and the promotion gate), integrated by the session agent;
every quoted signature re-checked against the PR branches. The Lean kernel remains the only
judge of mathematics — this document judges the prose. Full tables:
`geometric_torsion_audit_tables.json`.*
