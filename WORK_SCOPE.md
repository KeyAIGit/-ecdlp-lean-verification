# WORK_SCOPE.md — improvement program (from the external audit)

Derived from an independent deep-research audit of this repository. The audit's central finding:
**the math core is a real formal-research asset; the packaging — a single, non-drifting source of
truth legible to AI of any context — lags the math.** This file turns that into a prioritized,
honest, executable scope. It is a plan, not a claim: nothing here asserts a solution to ECDLP.

Status legend: ✅ done · 🔄 in progress · ⬜ todo.

---

## Horizon A — Packaging & single source of truth (days–weeks; highest leverage)

The #1 issue: canonical machine metrics (`data/stats.json`, `VERIFIED.md`) auto-update, but the
human summary layer drifts (COVERAGE / TRUST_REPORT / ONE_PAGE_SUMMARY / ENVIRONMENT_PLAN /
ABSTRACT_SCOPE showed 126/116/114/117 while the source said 189/167). A low-context AI then reads
the wrong snapshot.

- ✅ **A1 · Corpus→theorem traceability, adversarially verified.** Re-mapped all 486 corpus claims
  against `VERIFIED.md`; every `verified`/`partial` upgrade re-checked by an independent skeptic
  (18 confirmed, 2 downgraded, 0 rejected). Result recorded in `data/corpus_coverage_overrides.json`
  (auditable, with provenance), consumed by `scripts/build_frontier_map.py`, so
  `frontier_map.json` is reproducible. Coverage: **verified 5→10, partial 32→46** (honest, gated).
- ✅ **A2 · Reconcile `stats.json`.** Regenerated from `VERIFIED.md` → **210 rows / 177 distinct /
  85 modules / 0 sorry / 0 axioms** (was stale 189/167/76).
- ✅ **A3 · One human snapshot (`STATUS.md`) + kill drift.** `STATUS.md` is the single generated
  snapshot; stale summaries now point to it. The real disease was deeper than stale files: several
  *generators* computed the headline independently and disagreed (coverage_report said 209/198 vs
  stats' 210/177). Fixed at the root — `coverage_report`/`build_frontier_map`/`build_knowledge_graph`
  now read the count from `stats.json`, never re-tally. `check_counts.py` extended to scan the
  summary docs (with a `count-check: ignore` escape for docs that quote retired strings), wired in CI.
- ✅ **A4 · `docs-sync` workflow.** `.github/workflows/docs-sync.yml` regenerates *all* derived
  artifacts in dependency order, runs `check_counts.py`, and **fails a PR if the tree is dirty**
  (auto-commits on `main`). Supersedes `stats.yml` (strict superset) — `stats.yml` retired to avoid
  two workflows racing to push the same files.
- ✅ **A5 · Honest labels everywhere.** Propagated to README/AGENTS/ENVIRONMENT_PLAN: protocol
  theorems = *verified protocol algebra* (abstract identities), not deployed-protocol security; GLV =
  *homomorphism half proved, `[λ]` eigenvalue open*; autonomy = *tactic-ladder + human-in-loop*,
  external model-provers *attempted, 0 accepted*. Hardcoded counts in README/AGENTS → STATUS.md
  pointers (they contradicted their own "don't hardcode a number" note).
- ✅ **A6 · External packaging.** Real `SETUP.md` (build + CI-gate walkthrough + warm-server loop +
  regen + infra reality), `READ_FIRST.md` (low-context-AI entrypoint), `requirements.txt` (optional
  Python deps pinned, with a note that the correctness pipeline needs none). GitHub About
  description/topics drafted (see the PR body). License decision still open.
- ⬜ **A7 · Land the corrected state on `main`.** PR #102 (dev → main) carries the newer Weil/Semaev/
  multi-curve results **and** these doc fixes; the audit read `main`, so several "under-reporting"
  findings resolve on merge. *Human-gated (charter): the maintainer merges.*

## Horizon B — The math keystone (weeks–months)

The audit and the repo's own notes converge on one node that unlocks several doors.

- 🔄 **B1 · Point counting `#E(𝔽_p) = n`.** The keystone: it gates (a) instantiating the abstract
  protocol algebra on the *real* secp256k1 group, (b) the `Module (ℤ/n)` structure, and (c) the GLV
  eigenvalue `glvPoint G = λ·G`. **Scoped** in `notes/POINT_COUNTING_KEYSTONE.md`: separates the
  strong `#E=n` (gated on Hasse — a multi-month Mathlib port) from a **weak, certificate-shaped**
  base-point-subgroup fact that unlocks most downstream results and is bounded engineering gated on
  one empirical unknown (whether Mathlib `Point` arithmetic reduces under `native_decide`), not on
  point-counting. Next: probe that reduction.
- ⬜ **B2 · GLV eigenvalue `glvPoint G = λ·G`** — completes the CM/GLV object once B1 lands.
- ⬜ **B3 · Weil ladder W4/W5** — reciprocity `f(div g)=g(div f)` then bilinear/non-degenerate `eₙ`;
  a genuine Mathlib gap (W1–W3 already landed). Semaev `S₄`-degree `2^{m−2}` tower (recorded open).

## Horizon C — Publication packaging (optional, high value)

- ✅ **C1 · `PUBLISHABLE_UNITS.md`** — separates the 3 publishable narratives from the engine story:
  (i) the generic-group `Θ(√n)` combinatorial core; (ii) machine-checked Pratt certificates for
  secp256k1 `p`/`n`; (iii) the Weil/Semaev foundational ladder (first-in-Lean). Each with the actual
  theorem names (spot-checked against the codebase), honest scope, target venue, and an abstract's
  opening sentence; §5 keeps the engine story a *separate* methods track; §6 the global non-claims.
  Also `data/claim_traceability.jsonl` — the 20 adversarially-verified corpus overrides mapped to
  their theorems with an explicit open-gap + paper hook each.
- ⬜ **C2 · Engine as a reusable product** — keep the ontology/target layer swappable so the
  propose→judge→verify loop generalizes beyond ECDLP (the licensable asset).

---

## Honest scope (unchanged)

Breaking ECDLP on secp256k1 is not the deliverable and is not claimed. The generic-group `Ω(√n)`
bound (formalized here) constrains only black-box algorithms; it says nothing about non-generic
attacks on this concrete curve, whose hardness is an open conjecture, not a theorem. The value is
the verified asset, the barrier map, the reusable engine, and publishable formalizations.

*Started this session: A1, A2 (committed on the dev branch). Continuing top-down.*
