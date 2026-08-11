#!/usr/bin/env python3
"""Agent-bundle export — make the Research OS consumable by an AI agent at any context size.

The repo's truth is spread across many files. An agent with a *small* context window can't
load all of them, and shouldn't have to guess which matter. This script defines three
cumulative context tiers and can either:

  * ``--manifest``   write ``bundles/MANIFEST.json`` — a small, machine-readable routing
                     table (tier -> ordered file list + one-line reason + size). This is the
                     committed, drift-gated artifact: an agent (or a site) fetches it to learn
                     exactly what to load.
  * ``--tier NAME``  print a single self-contained context pack (a header + every tier file
                     inlined) to stdout or ``--out FILE``. Generated on demand, NOT committed
                     (the packs duplicate repo content and would otherwise drift).
  * ``--check``      fail if any file a tier references is missing (a cheap CI gate).

Tiers are cumulative: medium ⊇ small, large ⊇ medium. The single source of truth for what a
tier contains is ``TIERS`` below; ``AGENTS.md`` describes the same routing in prose.

Usage:
  python3 scripts/export_agent_bundle.py --manifest         # regenerate bundles/MANIFEST.json
  python3 scripts/export_agent_bundle.py --check            # CI gate: referenced files exist
  python3 scripts/export_agent_bundle.py --tier small       # print the small pack to stdout
  python3 scripts/export_agent_bundle.py --tier large --out /tmp/large.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Ordered, cumulative tier definitions: (path, why-an-agent-needs-it).
# Keep this the ONLY place tiers are defined; AGENTS.md mirrors it in prose.
_SMALL = [
    ("STATUS.md", "canonical live snapshot — counts, active goal, bottleneck; wins over prose"),
    ("domains/riemann-hypothesis/README.md",
     "active RH Stage 0 boundary, exact target, evidence rules, and repository isolation"),
    ("repo/ECDLP_DECISION_SUBSTRATE.json",
     "exact target, route dispositions, evidence gates, and foundation priority"),
    ("repo/RESEARCH_ENGINE_V0.json",
     "bounded exploration policy, selector, taxonomy, budgets, and promotion boundary"),
    ("repo/ECDLP_TYPED_EVIDENCE_V0.json",
     "claim-level evidence, target properties, mechanism requirements, and scoped barriers"),
    ("data/typed_evidence_state.json",
     "materialized applicability cells and non-experimental desk decisions"),
    ("repo/RESEARCH_CLAIMS_V0.json",
     "route-question-claim-variant-event truth model with disposition and assurance separated"),
    ("data/research_claim_state.json",
     "generated claim-level truth state and calibration-exclusion boundary"),
    ("repo/HYPOTHESIS_GENERATION_V0.json",
     "typed-evidence-bound seed axes, proposal quality gates, and adversarial review contract"),
    ("repo/HYPOTHESIS_MODEL_DRAFTER_V0.json",
     "bounded provider policy for untrusted, non-executable model-assisted proposal fragments"),
    ("repo/HYPOTHESIS_SPACE_V2.json",
     "million-scale typed challenge-space policy and hot/warm/cold map contract"),
    ("data/hypothesis_space_state.json",
     "generated one-million-cell screening state and bounded review queue"),
    ("data/hypothesis_space_map.json",
     "aggregate evidence-bounded hot/warm/cold research-space map"),
    ("repo/HYPOTHESIS_SPACE_RUN_LEDGER_V1.json",
     "append-only operational-run policy and scientific-evidence exclusion boundary"),
    ("data/hypothesis_space_run_state.json",
     "auditable benchmark, pipeline-error, and distinct-map-root history"),
    ("data/research_engine_state.json",
     "generated dual-gate state, selected sequence, and retained outcome summaries"),
    ("repo/RESEARCH_ENGINE_LIFECYCLE_V0.json",
     "immutable candidate lifecycle, portfolio, calibration, and owner-authorization boundary"),
    ("data/research_engine_v02_state.json",
     "generated non-executing lifecycle state and byte-pinned historical boundary"),
    ("data/research_engine_shadow_intake.json",
     "derived unread-source, applicability, and cost-contract proposal stubs"),
    ("repo/RESEARCH_ENGINE_V0_2_ACCEPTANCE.json",
     "the 19 owner regression cases and their concrete fault-injection tests"),
    ("repo/PRODUCT_MODEL.json",
     "product category, current-vs-future boundary, public claims, and MVP evidence gate"),
    ("repo/PILOT_PROTOCOL.json",
     "TASK-011 discovery contract, safety boundary, evidence schema, and disposition gate"),
    ("tasks/NEXT.md", "router for the separate RH, ECDLP, and KeyAI product queues"),
    ("tasks/RIEMANN_HYPOTHESIS.md",
     "active RH foundation-audit contracts, route gates, and hard stop rules"),
    ("tasks/ECDLP_RESEARCH.md", "bounded ECDLP research contracts and exit criteria"),
    ("tasks/ECDLP_LAB_BUILD.md",
     "owner-directed sequential ECDLP lab engineering contract and safety gates"),
    ("tasks/ECDLP_LAB_REUSE_INVENTORY.json",
     "digest-bound frozen inputs and upstream state for the ECDLP lab"),
    ("scripts/lab_check_reuse_inventory.py",
     "offline integrity gate for the ECDLP lab frozen-input inventory"),
    ("tasks/KEYAI_PRODUCT.md", "product-validation contracts and separate product KPIs"),
    ("data/stats.json", "machine-readable headline counts (ledger rows / distinct / modules)"),
    ("data/frontier_map.json", "per-claim frontier status: verified / tractable / blocked / informal"),
]
_SOURCE_CLAIM_EXTRACTS = [
    (
        path.relative_to(ROOT).as_posix(),
        "claim-level primary-source extraction bound to the typed evidence layer",
    )
    for path in sorted((ROOT / "data" / "source_claim_extracts").glob("*.json"))
]
_MEDIUM_EXTRA = [
    ("README.md", "the front door: what this is, what it does NOT claim"),
    ("AGENTS.md", "agent operating rules, invariants, and forbidden moves"),
    ("domains/riemann-hypothesis/corpus.md",
     "RH source register, formal baseline, claim map, route ranking, and red-team checks"),
    ("VERIFIED.md", "the canonical ledger — every kernel-verified theorem, one row each"),
    ("BARRIERS.md", "the no-go / blocked map — what needs missing Mathlib foundations"),
    ("notes/SECURITY_SCOPE.md", "precise scope of the generic-hardness claim (not unconditional)"),
    ("notes/FOUNDATIONS.md", "the Weil/Semaev foundation ladder and its open rungs"),
    ("experiments/HYPOTHESES.yaml", "testable directions with evidence and exit criteria"),
    ("experiments/engine/README.md", "Research Engine event lifecycle and regeneration contract"),
    ("experiments/engine/hypothesis_seed.schema.json",
     "deterministic non-executable seed contract"),
    ("experiments/engine/hypothesis_proposal.schema.json",
     "structured untrusted proposal contract before candidate intake"),
    ("experiments/engine/hypothesis_review.schema.json",
     "digest-bound five-role adversarial review contract"),
    ("experiments/engine/research_claim.schema.json",
     "claim-level disposition, assurance, scope, and reopening contract"),
    ("experiments/engine/candidate_snapshot.schema.json",
     "immutable v0.2 candidate/version scientific identity"),
    ("experiments/engine/candidate_lifecycle.schema.json",
     "append-only v0.2 candidate lifecycle transitions"),
    ("experiments/engine/mechanism_contract.schema.json",
     "exact map, fixed-target, recovery, and cost-changing mechanism contract"),
    ("experiments/engine/prediction_contract.schema.json",
     "matched baseline, effect threshold, and stop-rule contract"),
    ("experiments/engine/cost_contract.schema.json",
     "online, offline, memory, storage, money, effort, setup, and amortization"),
    ("experiments/engine/validator_contract.schema.json",
     "raw-artifact recomputation and three-axis validator independence"),
    ("experiments/engine/research_lane.schema.json",
     "lane-specific applicability, structural, mechanism, validator, experiment, and formal gates"),
    ("experiments/engine/hypothesis_space_run.schema.json",
     "strict non-scientific screening-run and benchmark record contract"),
    ("notes/RESEARCH_ENGINE_V0_TO_V0_2.md",
     "migration boundary, preserved history, lifecycle semantics, and regeneration order"),
    ("experiments/engine/outcome.schema.json", "strict terminal-outcome event schema"),
    ("experiments/engine/run.schema.json", "native run envelope and frozen matrix binding"),
    ("experiments/engine/instance_result.schema.json", "per-instance result and artifact binding"),
    ("experiments/engine/instance_validation.schema.json",
     "independent per-instance validation and recomputed outcome classification"),
    ("experiments/engine/validator_request.schema.json",
     "sanitized replay input without claimed value, terminal outcome, or result digest"),
    ("experiments/engine/validator_output.schema.json",
     "strict machine-readable output from pure validator replay"),
    ("experiments/engine/validators/README.md",
     "scientific-validator boundary and current no-validator status"),
    ("experiments/framework/fixtures/pure_engine_validator.py",
     "protocol regression fixture; explicitly not scientific evidence"),
] + _SOURCE_CLAIM_EXTRACTS
def outcome_reason(path: Path) -> str:
    event = json.loads(path.read_text(encoding="utf-8"))
    source_kind = event.get("provenance", {}).get("source_kind")
    if source_kind == "historical_migration":
        return "digest-pinned historical outcome retained by Research Engine v0"
    if source_kind == "native_engine_run":
        return "source-commit-bound native outcome retained by Research Engine v0"
    return "Research Engine outcome with an invalid or unknown provenance kind"


_OUTCOME_FILES = [
    (path.relative_to(ROOT).as_posix(), outcome_reason(path))
    for path in sorted((ROOT / "experiments" / "engine" / "outcomes").glob("*.json"))
]
_HYPOTHESIS_SPACE_RUN_FILES = [
    (
        path.relative_to(ROOT).as_posix(),
        "immutable operational screening benchmark; never scientific outcome evidence",
    )
    for path in sorted(
        (ROOT / "experiments" / "engine" / "hypothesis_space_runs").glob("*.json")
    )
]
_LARGE_EXTRA = [
    ("data/knowledge_graph.json", "full machine-readable theorem/dependency/barrier graph"),
    ("REPOSITORY_ARCHITECTURE.md", "whole-repo map: canonical / generated / scratch / archive"),
    ("PUBLISHABLE_UNITS.md", "the standalone publishable narratives with honest scope"),
    ("TRUST_REPORT.md", "the trust boundary: what native_decide adds to the TCB"),
] + _OUTCOME_FILES + _HYPOTHESIS_SPACE_RUN_FILES

TIERS: dict[str, list[tuple[str, str]]] = {
    "small": _SMALL,
    "medium": _SMALL + _MEDIUM_EXTRA,
    "large": _SMALL + _MEDIUM_EXTRA + _LARGE_EXTRA,
}

MANIFEST_PATH = "bundles/MANIFEST.json"

HEADER = """\
# KeyAI Research OS — agent context bundle ({tier} tier)

You are working on KeyAI, a verification workspace for AI research. Its public reference
deployment is a Lean 4 + Mathlib environment for secp256k1 / ECDLP, and its primary new
frontier lane is an exploratory Stage 0 program for the Riemann Hypothesis. The Lean kernel
is the only judge of proof acceptance: a green build means every listed theorem is fully
proved, with no `sorry` and no custom axioms. The RH lane currently claims no proof candidate
or result on the conjecture. This is a **verified research asset**, not an attempt to break
secp256k1 or a claim that the hosted product is complete.

Ground rules:
- `STATUS.md` is the canonical live snapshot. If prose anywhere conflicts with it, STATUS wins.
- `domains/riemann-hypothesis/README.md` and `tasks/RIEMANN_HYPOTHESIS.md` own RH Stage 0.
  ECDLP evidence, decisions, metrics, and authorizations do not transfer to RH.
- `repo/ECDLP_DECISION_SUBSTRATE.json` owns route applicability and foundation priority.
- `repo/RESEARCH_ENGINE_V0.json` owns bounded exploration; generated evidence cannot promote a route.
- `repo/ECDLP_TYPED_EVIDENCE_V0.json` owns claim-level target-property and mechanism applicability screens.
- `repo/RESEARCH_CLAIMS_V0.json` owns exact child-claim dispositions and assurance; a child result never closes its route by implication.
- `repo/HYPOTHESIS_GENERATION_V0.json` owns non-executable seed and proposal-quality compilation.
- `repo/HYPOTHESIS_MODEL_DRAFTER_V0.json` owns optional model drafting. Its default typed-evidence input is provenance-bound; its separate brainstorm input is not. Model-authored claim links are not semantic support, and both outputs remain untrusted and non-executable.
- `repo/HYPOTHESIS_SPACE_RUN_LEDGER_V1.json` owns operational benchmark/error memory; screening rejects are not scientific outcomes.
- `repo/RESEARCH_ENGINE_LIFECYCLE_V0.json` owns immutable candidate lifecycle and portfolio selection.
- `repo/RESEARCH_ENGINE_V0_2_ACCEPTANCE.json` owns the 19 required regression cases.
- `repo/PRODUCT_MODEL.json` owns product rhetoric, current capability, and MVP boundaries.
- `repo/PILOT_PROTOCOL.json` owns TASK-011 discovery, safety, evidence, and disposition.
- Never weaken a proof, add a `sorry`/`admit`, or add an axiom to make anything pass.
- Use `tasks/NEXT.md` to route work to the owning RH, ECDLP, or product queue.

The files below are inlined in full, in load order for this tier.
"""


def _logical_text_bytes(path: Path) -> int:
    """Return the repository (LF-normalized UTF-8) size of a text artifact."""
    text = path.read_text(encoding="utf-8")
    return len(text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))


def _entries(tier: str) -> list[dict]:
    out = []
    for path, reason in TIERS[tier]:
        p = ROOT / path
        exists = p.exists()
        out.append({
            "path": path,
            "reason": reason,
            "exists": exists,
            "bytes": (_logical_text_bytes(p) if exists else 0),
        })
    return out


def cmd_manifest() -> int:
    manifest = {
        "schema_version": 1,
        "purpose": "Routing table: which repo files an AI agent should load at each context tier.",
        "canonical_source": "STATUS.md",
        "rule": "STATUS.md wins over prose; never weaken a proof or add an axiom.",
        "regenerate": "python3 scripts/export_agent_bundle.py --manifest",
        "on_demand_pack": "python3 scripts/export_agent_bundle.py --tier <small|medium|large>",
        "tiers": {tier: _entries(tier) for tier in TIERS},
    }
    text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    (ROOT / MANIFEST_PATH).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / MANIFEST_PATH).write_text(text, encoding="utf-8", newline="\n")
    tot = {t: sum(e["bytes"] for e in _entries(t)) for t in TIERS}
    print(f"wrote {MANIFEST_PATH} — small {tot['small']}B / medium {tot['medium']}B / large {tot['large']}B")
    return 0


def cmd_check() -> int:
    missing = []
    for tier in TIERS:
        for e in _entries(tier):
            if not e["exists"]:
                missing.append(f"{tier}: {e['path']}")
    if missing:
        print("agent-bundle check FAILED — referenced files missing:")
        for m in missing:
            print(f"- {m}")
        return 1
    # If the manifest is committed, it must be in sync with the tier definitions.
    mp = ROOT / MANIFEST_PATH
    if mp.exists():
        want = {tier: _entries(tier) for tier in TIERS}
        got = json.loads(mp.read_text(encoding="utf-8")).get("tiers", {})
        if got != want:
            print(f"agent-bundle check FAILED — {MANIFEST_PATH} is stale; run --manifest")
            return 1
    print(f"agent-bundle check OK: {len(TIERS)} tiers, all referenced files present and manifest fresh")
    return 0


def cmd_tier(tier: str, out: str | None) -> int:
    if tier not in TIERS:
        print(f"unknown tier {tier!r}; choose from {', '.join(TIERS)}")
        return 2
    parts = [HEADER.format(tier=tier)]
    for path, reason in TIERS[tier]:
        p = ROOT / path
        parts.append(f"\n\n=== BEGIN {path} — {reason} ===\n")
        parts.append(p.read_text(encoding="utf-8") if p.exists() else f"(missing: {path})")
        parts.append(f"\n=== END {path} ===\n")
    text = "".join(parts)
    if out:
        Path(out).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {out} ({len(text)} chars)")
    else:
        sys.stdout.write(text)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Export agent context bundles.")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--manifest", action="store_true", help="write bundles/MANIFEST.json")
    g.add_argument("--check", action="store_true", help="fail if referenced files are missing/stale")
    g.add_argument("--tier", choices=list(TIERS), help="print/write a self-contained context pack")
    ap.add_argument("--out", help="with --tier: write to this file instead of stdout")
    args = ap.parse_args()

    if args.check:
        return cmd_check()
    if args.tier:
        return cmd_tier(args.tier, args.out)
    # default action is to (re)generate the manifest
    return cmd_manifest()


if __name__ == "__main__":
    raise SystemExit(main())
