# Repository structure and public-site audit, 2026-08-16

## Scope

This audit reviewed the repository front door, canonical ledgers, generated
views, folder ownership model, public site, and the risk of moving or merging
existing artifacts. It introduces no mathematical claim.

## Decision

Do not physically merge `VERIFIED.md` and `VERIFIED_RESEARCHOS.md`.

They are intentionally different verification surfaces:

- ECDLP uses a five-column theorem ledger and owns the public ECDLP headline
  count in `data/stats.json`.
- ResearchOS uses a twelve-column ledger with statement anchors, source
  contracts, review records, dates, axiom bases, and scoped claims.
- `scripts/check_ledger_isolation.py` explicitly prevents ResearchOS rows from
  changing the ECDLP denominator.

The correct optimization is a generated human-facing index over both canonical
sources. It improves discoverability without weakening provenance or inventing
a cross-domain distinct-theorem metric.

## Findings

### 1. The truth architecture is stronger than the navigation

`REPOSITORY_ARCHITECTURE.md` and `repo/ARTIFACTS.yaml` already separate
canonical, generated, operational, experimental, public, and archived layers.
The primary gap was that a visitor had to infer this separation from several
large documents.

### 2. The root README carried too many responsibilities

The previous README mixed product positioning, current decisions, theorem
highlights, trust explanation, layout, automation history, and deep links. It
was useful as a record but expensive for a low-context reader and vulnerable to
prose drift.

### 3. Verified results had no single public entry point

The site linked prominently to the ECDLP ledger but did not expose the separate
ResearchOS verified surface with equal clarity. The repository likewise lacked
one generated navigation page across both ledgers.

### 4. The Workspace page was accurate but cognitively dense

It exposes route decisions, formal blockers, engine state, evidence, and queues
in one operator view. The missing piece was a short orientation layer that tells
a visitor which surface answers which question before they enter the tabs.

### 5. Mass folder movement is not justified in this change

The highest-volume areas are already classified and have import, provenance,
generator, or site references. Moving them now would create link and history
risk without improving the source-of-truth model. Archive deletion remains a
separate inventory-first action.

## Changes executed

1. Added generated `VERIFIED_ALL.md` as a non-canonical index.
2. Added generated `results.html` with direct routes to both ledgers, live
   status, corpus coverage, trust, and architecture. Added `sitemap.xml` and
   `robots.txt` so crawlers discover the current five-page public surface.
3. Added a deterministic results generator plus a small public-site enhancement
   layer. `assets/site.js` adds Results navigation, a homepage results ribbon,
   and a Workspace orientation strip; `assets/site-refresh.css` applies a calmer
   visual hierarchy without changing canonical data.
4. Replaced the root README with a shorter routing document that delegates
   live state instead of repeating it.
5. Added `docs/README.md`, `scripts/README.md`, and `repo/README.md` as
   folder-level entry points.
6. Added generated-artifact freshness coverage, unit tests, and a focused CI
   workflow for the results portal.

## Explicitly deferred

- No canonical ledger schema merge.
- No theorem-file relocation.
- No renaming of `Ecdlp/`, `ResearchOS/`, `repo/`, `data/`, `experiments/`, or
  `archive/`.
- No archive deletion.
- No external reviewer or customer involvement for this maintenance change.

## Next structural threshold

A physical root-document cleanup should happen only after an automated inbound
reference scan can prove that every moved document has a replacement link and a
rollback path. Until that gate exists, navigation indexes provide most of the
benefit at much lower risk.
