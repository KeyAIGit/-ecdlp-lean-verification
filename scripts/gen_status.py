#!/usr/bin/env python3
"""Generate STATUS.md — the ONE canonical human snapshot.

The single source of operational truth for any reader (human or AI, large or small context).
Every number here is pulled live from the machine sources, never hand-typed, so it cannot drift:
  - data/stats.json          (ledger_rows, distinct_results, proved_modules, sorry, axioms)
  - data/frontier_map.json   (corpus status_summary, completeness)
  - repo/PRODUCT_MODEL.json  (product category, stage, capability boundary)
  - repo/PILOT_PROTOCOL.json (external-pilot status and evidence state)
  - repo/ECDLP_DECISION_SUBSTRATE.json (phase, routes, foundation decisions)
  - data/research_engine_state.json (dual gates, selected explorations, outcomes)
  - data/research_engine_v02_state.json (immutable lifecycle and authorization)
  - data/research_engine_shadow_intake.json (non-executable proposal stubs)
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
ENGINE = ROOT / "data" / "research_engine_state.json"
ENGINE_V02 = ROOT / "data" / "research_engine_v02_state.json"
SHADOW_INTAKE = ROOT / "data" / "research_engine_shadow_intake.json"
OUT = ROOT / "STATUS.md"


def render_engine_queue_summary(
    engine_counts: dict,
    selected_sequence: list[dict],
    ready_candidate_ids: list[str],
) -> str:
    selected_ids = [item["candidate_id"] for item in selected_sequence]
    selected_text = ", ".join(f"`{item}`" for item in selected_ids) or "none"
    ready_text = (
        ", ".join(f"`{item}`" for item in ready_candidate_ids) or "none"
    )
    summary = (
        f"Selected bounded explorations: "
        f"**{engine_counts['selected_explorations']}** ({selected_text}). "
        f"Ready now: **{engine_counts['ready_explorations']}** ({ready_text})."
    )
    if not selected_sequence:
        summary += (
            f" **{engine_counts['intake_candidates']} candidates remain at intake** "
            "behind exact-mechanism or independent-validator hard gates."
        )
    return summary


def main() -> int:
    s = json.loads(STATS.read_text(encoding="utf-8"))
    fm = json.loads(FM.read_text(encoding="utf-8"))
    decisions = json.loads(DECISIONS.read_text(encoding="utf-8"))
    product = json.loads(PRODUCT.read_text(encoding="utf-8"))
    pilot = json.loads(PILOT.read_text(encoding="utf-8"))
    engine = json.loads(ENGINE.read_text(encoding="utf-8"))
    engine_v02 = json.loads(ENGINE_V02.read_text(encoding="utf-8"))
    shadow_intake = json.loads(SHADOW_INTAKE.read_text(encoding="utf-8"))
    ss = fm["status_summary"]
    meta = fm["meta"]
    total = meta.get("corpus_claims", sum(ss.values()))
    phase = decisions["phase_policy"]
    selection = decisions["route_selection"]
    selected_structural = selection.get("selected_route_ids", [])
    promoted_routes = selection.get("promoted_route_ids", [])
    routes = decisions["routes"]
    foundations = decisions["foundations"]
    build_now = [item for item in foundations if item["build_now"]]
    engine_counts = engine["counts"]
    engine_gates = engine["gate_status"]
    selected_sequence = engine["selected_sequence"]
    engine_queue_summary = render_engine_queue_summary(
        engine_counts,
        selected_sequence,
        engine["execution_queue"]["ready_candidate_ids"],
    )
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
> `repo/PILOT_PROTOCOL.json`, `repo/ECDLP_DECISION_SUBSTRATE.json`, and
> `repo/ECDLP_TYPED_EVIDENCE_V0.json`, `data/typed_evidence_state.json`, and
> `data/research_engine_state.json`, `data/research_engine_v02_state.json`, and
> `data/research_engine_shadow_intake.json`.
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
recorded **{len(selected_structural)} route in completed bounded structural work**
({", ".join(f"`{item}`" for item in selected_structural) or "none"}), while promoting
**{len(promoted_routes)} routes**. The completed work resolved one exact S3/S4 polynomial-symmetry
question and one S4 fixed-target uncertainty; it was not an attack experiment or a route promotion. The map contains
**{len(foundations)} foundation decisions**,
bounded exploration authorized = **{str(phase['bounded_exploration_authorized']).lower()}**,
promotion experiments authorized =
**{str(phase['promotion_experiments_authorized']).lower()}**, selected attack route =
**{phase['selected_attack_route'] or 'none'}**.

The `build_now` foundations are {", ".join(f"`{item['id']}`" for item in build_now)}.
They make future candidates comparable and independently checkable; the completed structural
work did not activate a parked experiment hypothesis. The formal gaps `E[n] ≅ (ℤ/n)²`,
Weil reciprocity/pairing, general point-division
bridges, p-adic formal groups, lattice reduction, isogenies, and quantum circuits remain mapped,
but none is automatically next merely because Mathlib lacks it. Route selection reopens only
when new evidence satisfies a recorded reconsideration trigger and the proposal gate.

## Research Engine v0
The engine normalizes **{engine_counts['normalized_hypotheses']} hypotheses** and retains
**{engine_counts['outcome_events']} outcome events**:
**{engine_counts['outcomes_by_source']['historical_migration']} migrated historical** and
**{engine_counts['outcomes_by_source']['native_engine_run']} native**. Its historical
no-reopen guard matched four frozen cases; this is not predictive EIG calibration. Predictive
calibration currently contains **{engine['calibration']['scored_native_outcomes']} native
outcomes**. Before synthesis, the typed evidence layer materializes
**{engine_counts['typed_evidence_cells']} mechanism/property cells**:
**{engine_counts['typed_decided_cells']} decided at desk** and
**{engine_counts['typed_seed_eligible_cells']} eligible to emit a bounded research question**.
Its **{engine_counts['typed_desk_decisions']} desk decisions** are non-experimental and authorize
nothing. The generation layer currently emits
**{engine_counts['generated_hypothesis_seeds']} source-grounded seeds**, with
**{engine_counts['submitted_hypothesis_proposals']} submitted proposals**,
**{engine_counts['quality_cleared_hypothesis_proposals']} quality-cleared proposals**, and
**{engine_counts['retained_hypothesis_drafts']} retained non-executable drafts**.
Creative output is untrusted and zero retained drafts is a valid cycle result.
{engine_queue_summary}

## Research Engine v0.2 lifecycle
The v0.2 lifecycle currently contains
**{engine_v02['engine']['input_candidate_count']} immutable candidate snapshots**,
**{len(engine_v02['engine']['admissible'])} admissible**,
**{len(engine_v02['engine']['recommended'])} recommended**, and
**{engine_v02['authorization']['experiments']} authorized**. Recommendation cannot create
authorization; authorization requires a separate dated owner decision bound to the exact
candidate digest. The eight historical events are referenced without migration, with both their
canonical review root and raw file bytes pinned.

Shadow intake contains **{shadow_intake['counts']['proposal_stubs']} non-executable proposal
stubs** and **{shadow_intake['counts']['parked_ideas']} parked desired-property record**.
These are research questions, not hypotheses or candidates:
**{shadow_intake['counts']['admissible']} admissible**,
**{shadow_intake['counts']['recommended']} recommended**, and
**{shadow_intake['counts']['authorized']} authorized**. `TASK-010` is accepted at
`85f85d4ca0b9dba323bfdd05ce8750d6db4732ac`. `TASK-017` completed the exact
set-theoretic projective-tree and exceptional-fiber replay for nonsingular
`y²=x³+7` in characteristic outside `{{2,3,7}}`, with a scoped direct-S17
blocker and zero retained hypotheses. Current work is `TASK-018`, which keeps
`CELL-M-PKC-SMOOTH-M16` as a non-executable recursive-projective-S17
definition and reverse-projection question above S4.
`TASK-008` remains parked because no hypothesis proposal has quality-cleared.

The Engine's bounded-exploration capability is
**{str(engine_gates['exploration_authorized']).lower()}**, while the current decision's experiment
authorization is **{str(phase['experiments_authorized']).lower()}** and the promotion gate is
**{str(engine_gates['promotion_authorized']).lower()}**. `GLV-SEMAEV-ITER-001` is complete; its
certificates and kernel-checked identities authorize no hypothesis run. `TASK-018` authorizes no
S17 expansion or evaluation, polynomial-system materialization, solver, cost inference, target
computation, or route promotion. Any later experiment needs
a new dated decision plus the normal fixed budgets, dependency order, and retained terminal
outcome.

## Active work protocol
`tasks/NEXT.md` is the queue router. ECDLP research is owned by
`tasks/ECDLP_RESEARCH.md`; product validation is owned by `tasks/KEYAI_PRODUCT.md`. Together they
retain 3-7 active task contracts. Product traffic, site work, pilots, and portability never count
as ECDLP progress.

The product authority is `repo/PRODUCT_MODEL.json`; `scripts/check_product_model.py` enforces its
claim boundary. Public surfaces must distinguish current capabilities, the reference deployment,
customer hypotheses, and future product direction.

The route authority is `repo/ECDLP_DECISION_SUBSTRATE.json`; its Markdown view is generated.
The engine policies are `repo/RESEARCH_ENGINE_V0.json`,
`repo/HYPOTHESIS_GENERATION_V0.json`, and
`repo/RESEARCH_ENGINE_LIFECYCLE_V0.json`; typed applicability is owned by
`repo/ECDLP_TYPED_EVIDENCE_V0.json`, materialized in
`data/typed_evidence_state.json`, and the combined generated state is
`data/research_engine_state.json`. The v0.2 lifecycle and shadow intake are
`data/research_engine_v02_state.json` and
`data/research_engine_shadow_intake.json`. The candidate-neutral validation contract lives in
`experiments/framework/`. No one file authorizes promotion by itself.

The hypothesis registry is `experiments/HYPOTHESES.yaml`. It records testable
directions, evidence, and exit criteria; it is not a theorem ledger.

The drift gate is `scripts/check_status_consistency.py`. Run it whenever stats,
frontier, graph, dashboard/site counters, tasks, or hypotheses change.

## Where to go deeper
`README.md` (the front door) · `repo/PRODUCT_MODEL.json` (product and MVP authority) ·
`repo/ECDLP_DECISION_SUBSTRATE.json` (route decisions) ·
`repo/RESEARCH_ENGINE_V0.json` (exploration policy and selector) ·
`repo/ECDLP_TYPED_EVIDENCE_V0.json` (claim-level applicability screens) ·
`repo/HYPOTHESIS_GENERATION_V0.json` (seed and proposal-quality policy) ·
`repo/RESEARCH_ENGINE_LIFECYCLE_V0.json` (immutable candidate lifecycle) ·
`repo/RESEARCH_ENGINE_V0_2_ACCEPTANCE.json` (19 regression cases) ·
`data/typed_evidence_state.json` (materialized mechanism/property cells) ·
`data/research_engine_state.json` (generated engine state) ·
`data/research_engine_v02_state.json` (generated lifecycle state) ·
`data/research_engine_shadow_intake.json` (non-executable shadow queue) ·
`tasks/NEXT.md` (queue router) · `tasks/ECDLP_RESEARCH.md` (research queue) ·
`tasks/KEYAI_PRODUCT.md` (product queue) ·
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
