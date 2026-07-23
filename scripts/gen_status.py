#!/usr/bin/env python3
"""Generate STATUS.md — the ONE canonical human snapshot.

The single source of operational truth for any reader (human or AI, large or small context).
Every number here is pulled live from the machine sources, never hand-typed, so it cannot drift:
  - data/stats.json          (ledger_rows, distinct_results, proved_modules, sorry, axioms)
  - data/frontier_map.json   (corpus status_summary, completeness)
  - repo/PRODUCT_MODEL.json  (product category, stage, capability boundary)
  - repo/PILOT_PROTOCOL.json (external-pilot status and evidence state)
  - repo/ECDLP_DECISION_SUBSTRATE.json (phase, routes, foundation decisions)
Other summary docs should link to STATUS.md rather than duplicate counts.

Run: python3 scripts/gen_status.py   (also run by the docs-sync workflow on every ledger change)
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATS = ROOT / "data" / "stats.json"
FM = ROOT / "data" / "frontier_map.json"
DECISIONS = ROOT / "repo" / "ECDLP_DECISION_SUBSTRATE.json"
PRODUCT = ROOT / "repo" / "PRODUCT_MODEL.json"
PILOT = ROOT / "repo" / "PILOT_PROTOCOL.json"
OUT = ROOT / "STATUS.md"


def main() -> int:
    s = json.loads(STATS.read_text(encoding="utf-8"))
    fm = json.loads(FM.read_text(encoding="utf-8"))
    decisions = json.loads(DECISIONS.read_text(encoding="utf-8"))
    product = json.loads(PRODUCT.read_text(encoding="utf-8"))
    pilot = json.loads(PILOT.read_text(encoding="utf-8"))
    ss = fm["status_summary"]
    meta = fm["meta"]
    total = meta.get("corpus_claims", sum(ss.values()))
    phase = decisions["phase_policy"]
    selection = decisions["route_selection"]
    routes = decisions["routes"]
    foundations = decisions["foundations"]
    build_now = [item for item in foundations if item["build_now"]]
    product_stage = product["current_stage"]
    customer_hypotheses = product["customer_hypotheses"]
    hypothesis_status_counts = {
        status: sum(item["status"] == status for item in customer_hypotheses)
        for status in ("unvalidated", "testing", "supported", "rejected")
    }
    hypothesis_status_summary = ", ".join(
        f"{count} {status}"
        for status, count in hypothesis_status_counts.items()
        if count
    )

    def g(k, d=0):
        return s.get(k, d)

    md = f"""# STATUS — canonical snapshot

> **Generated** by `scripts/gen_status.py` from `data/stats.json`,
> `data/frontier_map.json`, `repo/PRODUCT_MODEL.json`, and
> `repo/PILOT_PROTOCOL.json`, and `repo/ECDLP_DECISION_SUBSTRATE.json`.
> Do not hand-edit the numbers. Other summary docs should link here, not duplicate counts.

## Verified asset (the ledger)
| metric | value | source |
|---|---|---|
| ledger rows | **{g('ledger_rows')}** | `VERIFIED.md` → `data/stats.json` |
| distinct results | **~{g('distinct_results')}** | `data/stats.json` |
| proved modules | **{g('proved_modules')}** | `data/stats.json` |
| `sorry` | **{g('sorry_count')}** | axiom-audit + no-sorry gate |
| custom axioms | **{g('custom_axioms')}** | axiom-audit gate |

Toolchain: {g('toolchain', 'Lean 4 + Mathlib (see lakefile.toml)')}.

## Product state
- **Category:** {product['category']}.
- **Current stage:** {product_stage['label']}. {product_stage['summary']}
- **Reference deployment:** this secp256k1 repository demonstrates the research-state loop on one
  difficult domain; it is evidence for the product design, not a claim of a hosted multi-project
  product or an ECDLP break.
- **MVP boundary:** {product['mvp']['definition']}
- **External pilot:** {pilot['id']} is **{pilot['status']}**. {pilot['evidence_state']}
- **Customer evidence:** {len(customer_hypotheses)} customer hypotheses are recorded:
  {hypothesis_status_summary}. Status changes require dated evidence.
- **Accelerator boundary:** {product['mvp']['yc_readiness']}

## Corpus coverage (the 486-claim map)
The 486 corpus claims (`data/KG_CLAIM_FORMALIZATION_v1.csv`) are a *different* denominator from the
ledger: most verified theorems are foundations/new results, not original corpus items. Current
frontier-map status (adversarially-verified upgrades in `data/corpus_coverage_overrides.json`):

| status | claims | meaning |
|---|---|---|
| verified | **{ss.get('verified',0)}** | a named kernel-verified theorem discharges the claim |
| partial | **{ss.get('partial',0)}** | a theorem addresses part of it |
| tractable | **{ss.get('tractable',0)}** | reachable now, no theorem yet |
| blocked | **{ss.get('blocked',0)}** | needs a missing Mathlib foundation |
| informal | **{ss.get('informal',0)}** | not a formal statement by nature |
| unassigned | **{ss.get('unassigned',0)}** | not yet triaged |
| **total** | **{total}** | frontier completeness {meta.get('frontier_completeness_pct','?')}% |

## What is true right now (honest)
- KeyAI is a **verification workspace for AI research**. This repository is its public
  **verified substrate** and reference deployment for ECDLP / secp256k1 research. It does **not**
  solve ECDLP on secp256k1, and claims no shortcut.
- The generic-group `Ω(√n)` bound (formalized here) constrains only **black-box** algorithms; it
  says nothing about non-generic attacks on this concrete curve, whose hardness is an **open
  conjecture**, not a theorem.
- Strongest layers: verified secp256k1 arithmetic + machine-checked primality (Pratt); the
  generic-DLP `Θ(√n)` combinatorial core; attack-boundary facts (anti-MOV / anti-Smart); torsion /
  division-polynomial work; Semaev `S₃`/`S₄`; the early Weil ladder (W1–W3); **both point-counting
  keystones** — the weak `addOrderOf G = n` *and* the strong **`#E(𝔽_p) = n`** (proved
  curve-specifically, no Hasse/Schoof: `CurveCardinalityExact.lean`), giving
  `E(𝔽_p) = ⟨G⟩ ≃+ ℤ/n` (`CurveFullGroup.lean`, `PointGroupEquiv.lean`).
- Honest labels: the protocol library is **verified protocol algebra** (identities that hold in any
  `ℤ/n`-module), now also **instantiated on the concrete curve group** `⟨G⟩ = E(𝔽_p)` (the full
  point group, via the strong keystone) — not a proof of deployed-protocol security against a real
  adversary. The GLV endomorphism acts as the eigenvalue `[λ]` **on the whole point group**
  (`secp256k1_glvHom_eq_zsmul_unconditional`, no remaining hypotheses). The real prover path is the
  **tactic ladder + human-in-loop** (external model-provers attempted, 0 accepted).

## Main current bottleneck
The current bottleneck is **a missing proposal-level non-generic mechanism, not theorem
volume**. Decision `{selection['decision_id']}` evaluated all **{len(routes)} attack routes** and
selected **none**: no audited route currently clears the common gate for the exact plain
single-target objective. The map contains **{len(foundations)} foundation decisions**,
experiments authorized = **{str(phase['experiments_authorized']).lower()}**, selected route =
**{phase['selected_attack_route'] or 'none'}**.

The completed `build_now` foundations are {", ".join(f"`{item['id']}`" for item in build_now)}.
They make future candidates comparable and independently checkable; they do not test a parked
hypothesis. The formal gaps `E[n] ≅ (ℤ/n)²`, Weil reciprocity/pairing, general point-division
bridges, p-adic formal groups, lattice reduction, isogenies, and quantum circuits remain mapped,
but none is automatically next merely because Mathlib lacks it. Route selection reopens only
when new evidence satisfies a recorded reconsideration trigger and the proposal gate.

## Active work protocol
The active queue is `tasks/NEXT.md`. Keep it short (3-7 task contracts) so a
small-context agent can start work without rereading the whole repository.

The product authority is `repo/PRODUCT_MODEL.json`; `scripts/check_product_model.py` enforces its
claim boundary. Public surfaces must distinguish current capabilities, the reference deployment,
customer hypotheses, and future product direction.

The route authority is `repo/ECDLP_DECISION_SUBSTRATE.json`; its Markdown view is generated.
The candidate-neutral validation contract lives in `experiments/framework/`. Neither file
authorizes an experiment by itself.

The hypothesis registry is `experiments/HYPOTHESES.yaml`. It records testable
directions, evidence, and exit criteria; it is not a theorem ledger.

The drift gate is `scripts/check_status_consistency.py`. Run it whenever stats,
frontier, graph, dashboard/site counters, tasks, or hypotheses change.

## Where to go deeper
`README.md` (the front door) · `repo/PRODUCT_MODEL.json` (product and MVP authority) ·
`repo/ECDLP_DECISION_SUBSTRATE.json` (route decisions) ·
`tasks/NEXT.md` (active queue) ·
`experiments/HYPOTHESES.yaml` (hypotheses + exit criteria) · `PUBLISHABLE_UNITS.md` (the 3
standalone results) · `ROADMAP.md` (strategy & program) · `VERIFIED.md` (ledger) ·
`BARRIERS.md` (no-go map) · `notes/FOUNDATIONS.md` (Weil/Semaev ladder) ·
`notes/POINT_COUNTING_KEYSTONE.md` (the `#E=n` keystone) · `TRUST_REPORT.md` (trust boundary) ·
`data/frontier_map.json` (queryable per-claim status) ·
`experiments/framework/README.md` (candidate-evaluation contract).
"""
    OUT.write_text(md, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {g('ledger_rows')} rows / ~{g('distinct_results')} "
          f"distinct; corpus verified={ss.get('verified',0)}/{total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
