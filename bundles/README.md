# bundles/ — agent context routing

This directory makes the Research OS **consumable by an AI agent at any context size**.
The repo's truth is spread across many files; an agent with a small context window can't
load them all and shouldn't have to guess which ones matter. `MANIFEST.json` is the
routing table that answers *"what do I load, and in what order?"* for three cumulative
tiers.

## Files

| File | Committed? | What it is |
|---|---|---|
| `MANIFEST.json` | **yes** (drift-gated) | machine-readable routing table: tier → ordered file list, one-line reason, byte size |
| `small.md` / `medium.md` / `large.md` | **no** (git-ignored) | self-contained context packs (header + every tier file inlined), generated on demand |

## Tiers (cumulative: `medium ⊇ small`, `large ⊇ medium`)

- **small** — the live snapshot only: `STATUS.md`, `tasks/NEXT.md`, `data/stats.json`,
  `data/frontier_map.json`. Enough to know the counts, the active goal, and where to start.
- **medium** — adds orientation and the ledger: `README.md`, `AGENTS.md`, `VERIFIED.md`,
  `BARRIERS.md`, the security-scope and foundations notes, and `experiments/HYPOTHESES.yaml`.
- **large** — adds the full machine views: `data/knowledge_graph.json`,
  `REPOSITORY_ARCHITECTURE.md`, `PUBLISHABLE_UNITS.md`, `TRUST_REPORT.md`.

The single source of truth for tier membership is `TIERS` in
`scripts/export_agent_bundle.py`; `AGENTS.md` mirrors it in prose.

## Commands

```bash
# regenerate MANIFEST.json (run after any tier file changes)
python3 scripts/export_agent_bundle.py --manifest

# CI gate: fail if a referenced file is missing or MANIFEST.json is stale
python3 scripts/export_agent_bundle.py --check

# print a self-contained context pack (on demand — NOT committed)
python3 scripts/export_agent_bundle.py --tier small
python3 scripts/export_agent_bundle.py --tier large --out bundles/large.md
```

## Why the packs aren't committed

`small.md` / `medium.md` / `large.md` inline the full text of their tier files. Committing
them would duplicate repo content and drift the instant any source changed. Only the small
`MANIFEST.json` is committed, and it is regenerated + drift-gated in `docs-sync.yml` (it
records byte sizes of the tier files, so it is a pure function of committed sources) and
existence-checked in `ci.yml` via `--check`. Generate a pack fresh whenever you need one.
