# domains/ — the plug-in contract for the Research OS

This is the Phase-1 generalization layer (see `ROADMAP.md`). It turns the
ECDLP-specific repository into **instance #1 of a general machine-verifiable Research OS**:
any research domain whose claims have a machine-checkable core can flow through the *same*
pipeline —

> Corpus → Frontier → Hypotheses → Tasks → Proofs → Truth graph → Site → Papers

— by filling **three replaceable slots**. Everything else (the pipeline stages, the
consistency gates, the truth graph, the site generator, the agent bundles) is
domain-agnostic and shared.

## The three slots

| Slot | What it provides | ECDLP instance |
|---|---|---|
| **Corpus** | a set of atomic claims + provenance to triage | `data/KG_CLAIM_FORMALIZATION_v1.csv` (486 claims) |
| **Ontology / generator** | the domain's objects + statement templates the generator emits as open target stems | `Ecdlp/Ontology.lean` + `scripts/generator.py` |
| **Verifier** | a decision procedure: `verify(candidate) → {ok, log}` | the Lean kernel (`lake env lean`) |

A **domain is fully described by which files fill these three slots** plus a status. That
description lives in `domains/registry.json` — the machine-readable source of truth the
site and the honesty gate both read.

## Status model

- **live** — real, kernel-verified content is flowing through the whole pipeline. Every
  slot file must exist; the domain may reference live metric sources (`data/stats.json`,
  `data/frontier_map.json`, …).
- **planned** — the same machinery clearly applies, but the corpus/proofs are not started.
  Slots are `null`; the domain claims **no** metrics. It reserves space honestly.
- **exploratory** — a plausible direction that needs a *different* verifier or foundations
  not yet available (e.g. lattice/LWE). The verifier slot may be `unassigned`.

## The honesty rule (machine-checked)

`scripts/check_domains.py` enforces:
1. every domain has an `id`, `title`, `status`, and `slots`;
2. a **live** domain has every non-verifier slot file present on disk, and its
   `metrics_source`/`frontier_source` (if named) exist;
3. a **planned/exploratory** domain claims **no** metrics (`metrics_source` and
   `frontier_source` are `null`) — it cannot borrow another domain's numbers;
4. at least one **live** domain exists.

This is the same principle the rest of the repo runs on: *the site may only show what an
artifact can back up.* A placeholder must look like a placeholder.

## Adding a domain (the Phase-1 promise)

To add a new domain you edit **only its slot files + one registry entry** — never the
shared pipeline:

1. Add a corpus file and an ontology/generator for the domain.
2. Append an entry to `domains/registry.json` with the three slots and `status: "planned"`
   (or `"live"` once real content exists).
3. Run `python3 scripts/check_domains.py` and regenerate the site
   (`python3 scripts/build_dashboard.py`). The domain appears in the portfolio.

When a second domain flows through cleanly with only these edits, the platform thesis is
proven — and the Phase-2 investment (database, auth, hosted verification) becomes a
decision made on evidence. Until then, the registry keeps the ambition **visible and
honest**: one real case, and clearly-marked room for the rest.
