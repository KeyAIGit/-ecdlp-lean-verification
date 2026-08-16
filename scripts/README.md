# Scripts map

The scripts directory contains generators, consistency gates, tests, and
bounded operational helpers. Names are intentionally action-oriented.

## Main categories

| Prefix or role | Purpose | Typical rule |
|---|---|---|
| `gen_*` | Generate a canonical registry, audit, or compact index | Commit the generated output and support `--check` when practical. |
| `build_*` | Build a derived state or public view from canonical inputs | Never make the rendered view a competing source of truth. |
| `check_*` | Fail on drift, unsafe claims, missing ownership, or broken contracts | Read-only and deterministic. |
| `test_*` | Unit or regression tests for generators and gates | No network or secret dependency. |
| experiment-specific helpers | Reproduce bounded non-kernel evidence | Measurements are evidence, not proof. |

## High-level regeneration order

The authoritative integration order is encoded in
[`check_generated_fixpoint.py`](check_generated_fixpoint.py). The final public
site entry point is:

```bash
python scripts/build_dashboard.py
```

It runs the canonical site generator and then `build_results_portal.py`, which
creates `VERIFIED_ALL.md`, `results.html`, `sitemap.xml`, and `robots.txt`. The shared cross-page enhancement
lives in `assets/site.js` and `assets/site-refresh.css`; the portal checker
verifies that those navigation and visual hooks are present.

## Before adding a script

1. Prefer extending an existing generator when ownership is the same.
2. Give every committed generated artifact a freshness check.
3. Add a regression test for parsing, idempotency, or boundary semantics.
4. Classify any new output in `repo/ARTIFACTS.yaml`.
5. Keep network access and secrets out of ordinary verification gates.
