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
    ("tasks/NEXT.md", "the 3-7 active task contracts with exit criteria — where to start"),
    ("data/stats.json", "machine-readable headline counts (ledger rows / distinct / modules)"),
    ("data/frontier_map.json", "per-claim frontier status: verified / tractable / blocked / informal"),
]
_MEDIUM_EXTRA = [
    ("README.md", "the front door: what this is, what it does NOT claim"),
    ("AGENTS.md", "agent operating rules, invariants, and forbidden moves"),
    ("VERIFIED.md", "the canonical ledger — every kernel-verified theorem, one row each"),
    ("BARRIERS.md", "the no-go / blocked map — what needs missing Mathlib foundations"),
    ("notes/SECURITY_SCOPE.md", "precise scope of the generic-hardness claim (not unconditional)"),
    ("notes/FOUNDATIONS.md", "the Weil/Semaev foundation ladder and its open rungs"),
    ("experiments/HYPOTHESES.yaml", "testable directions with evidence and exit criteria"),
]
_LARGE_EXTRA = [
    ("data/knowledge_graph.json", "full machine-readable theorem/dependency/barrier graph"),
    ("REPOSITORY_ARCHITECTURE.md", "whole-repo map: canonical / generated / scratch / archive"),
    ("PUBLISHABLE_UNITS.md", "the standalone publishable narratives with honest scope"),
    ("TRUST_REPORT.md", "the trust boundary: what native_decide adds to the TCB"),
]

TIERS: dict[str, list[tuple[str, str]]] = {
    "small": _SMALL,
    "medium": _SMALL + _MEDIUM_EXTRA,
    "large": _SMALL + _MEDIUM_EXTRA + _LARGE_EXTRA,
}

MANIFEST_PATH = "bundles/MANIFEST.json"

HEADER = """\
# KeyAI Research OS — agent context bundle ({tier} tier)

You are working on the KeyAI machine-verifiable Research OS (Lean 4 + Mathlib), whose first
use case is secp256k1 / ECDLP. The Lean kernel is the only judge of correctness: a green
build means every listed theorem is fully proved, with no `sorry` and no custom axioms. This
is a **verified research asset**, not an attempt to break secp256k1.

Ground rules:
- `STATUS.md` is the canonical live snapshot. If prose anywhere conflicts with it, STATUS wins.
- Never weaken a proof, add a `sorry`/`admit`, or add an axiom to make anything pass.
- Pick work from `tasks/NEXT.md`; each task has explicit exit criteria.

The files below are inlined in full, in load order for this tier.
"""


def _entries(tier: str) -> list[dict]:
    out = []
    for path, reason in TIERS[tier]:
        p = ROOT / path
        exists = p.exists()
        out.append({
            "path": path,
            "reason": reason,
            "exists": exists,
            "bytes": (p.stat().st_size if exists else 0),
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
