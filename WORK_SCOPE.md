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
- 🔄 **A3 · One human snapshot (`STATUS.md`) + kill drift.** A single generated snapshot every other
  doc points to instead of duplicating numbers; make the stale summaries reference it. Extend
  `check_counts.py`/CI so a drifted summary fails the build, not just the badge.
- ⬜ **A4 · `docs-sync` workflow.** One CI pass that regenerates *all* derived artifacts
  (`gen_stats` · `build_frontier_map` · `build_dashboard` · `build_knowledge_graph` ·
  `coverage_report`) and fails if the tree is dirty — so summaries can never drift again.
- ⬜ **A5 · Honest labels everywhere (not only in the review dossier).** Propagate the three
  corrections the project already made internally: protocol theorems = *verified protocol algebra*
  (abstract identities), not proven security of deployed protocols; GLV object = *homomorphism half
  proved, `[λ]` eigenvalue still open*; autonomy = *tactic-ladder + human-in-loop is the real path*,
  external model-provers *attempted, 0 accepted*.
- ⬜ **A6 · External packaging.** GitHub About (description/topics/website), a real `SETUP.md`
  (currently one line), license decision, a short "read-this-first" entrypoint for low-context AI.
- ⬜ **A7 · Land the corrected state on `main`.** PR #102 (dev → main) carries the newer Weil/Semaev/
  multi-curve results **and** these doc fixes; the audit read `main`, so several "under-reporting"
  findings resolve on merge. *Human-gated (charter): the maintainer merges.*

## Horizon B — The math keystone (weeks–months)

The audit and the repo's own notes converge on one node that unlocks several doors.

- ⬜ **B1 · Point counting `#E(𝔽_p) = n`.** The keystone: it gates (a) instantiating the abstract
  protocol algebra on the *real* secp256k1 group, (b) the `Module (ℤ/n)` structure, and (c) the GLV
  eigenvalue `glvPoint G = λ·G`. Scope the dependency DAG; assess whether a Hasse/Schoof or a
  certificate route is formalizable at this size.
- ⬜ **B2 · GLV eigenvalue `glvPoint G = λ·G`** — completes the CM/GLV object once B1 lands.
- ⬜ **B3 · Weil ladder W4/W5** — reciprocity `f(div g)=g(div f)` then bilinear/non-degenerate `eₙ`;
  a genuine Mathlib gap (W1–W3 already landed). Semaev `S₄`-degree `2^{m−2}` tower (recorded open).

## Horizon C — Publication packaging (optional, high value)

- ⬜ **C1 · `PUBLISHABLE_UNITS.md`** — separate the ≥3 publishable narratives from the engine story:
  (i) the generic-group `Θ(√n)` combinatorial core; (ii) machine-checked Pratt certificates for
  secp256k1 `p`/`n`; (iii) the Weil/Semaev foundational ladder (first-in-Lean). Each with an honest
  scope and a paper hook.
- ⬜ **C2 · Engine as a reusable product** — keep the ontology/target layer swappable so the
  propose→judge→verify loop generalizes beyond ECDLP (the licensable asset).

---

## Honest scope (unchanged)

Breaking ECDLP on secp256k1 is not the deliverable and is not claimed. The generic-group `Ω(√n)`
bound (formalized here) constrains only black-box algorithms; it says nothing about non-generic
attacks on this concrete curve, whose hardness is an open conjecture, not a theorem. The value is
the verified asset, the barrier map, the reusable engine, and publishable formalizations.

*Started this session: A1, A2 (committed on the dev branch). Continuing top-down.*
