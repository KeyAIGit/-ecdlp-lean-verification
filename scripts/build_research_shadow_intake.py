#!/usr/bin/env python3
"""Build non-executable research-question and proposal stubs from canonical gaps."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SOURCE_REGISTRY_PATH = ROOT / "data" / "source_registry.json"
TYPED_STATE_PATH = ROOT / "data" / "typed_evidence_state.json"
CLAIM_STATE_PATH = ROOT / "data" / "research_claim_state.json"
OUTPUT_PATH = ROOT / "data" / "research_engine_shadow_intake.json"


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("ascii")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _stub_id(kind: str, anchor: str, purpose: str) -> str:
    digest = sha256_json(
        {"kind": kind, "anchor": anchor, "purpose": purpose}
    )[:12].upper()
    return f"RSI-{digest}"


def _base_stub(
    *,
    kind: str,
    anchor: str,
    purpose: str,
    lane: str,
    title: str,
    required_output: list[str],
    evidence_refs: list[str],
    route_id: str | None = None,
) -> dict[str, Any]:
    return {
        "stub_id": _stub_id(kind, anchor, purpose),
        "stub_kind": kind,
        "anchor_id": anchor,
        "route_id": route_id,
        "lane": lane,
        "title": title,
        "purpose": purpose,
        "required_output": required_output,
        "evidence_refs": sorted(set(evidence_refs)),
        "lifecycle_state": "idea",
        "scientific_identity": "research_question_seed",
        "executable": False,
        "admissible": False,
        "recommended": False,
        "authorized": False,
        "route_promotion": False,
        "exact_target_experiment": False,
        "boundary": (
            "This is a non-executable intake stub, not a hypothesis, "
            "candidate, route promotion, or experiment authorization."
        ),
    }


def _unread_source_stubs(
    source_registry: dict[str, Any],
) -> list[dict[str, Any]]:
    stubs: list[dict[str, Any]] = []
    for source in source_registry.get("sources", []):
        if source.get("full_text_status") != "full_text_unread":
            continue
        source_id = source["id"]
        stubs.append(
            _base_stub(
                kind="literature_full_text_ingestion",
                anchor=source_id,
                purpose=(
                    "Obtain the primary full text and extract exact mechanism, "
                    "limitations, assumptions, and claim-level anchors without "
                    "inferring novelty from absence."
                ),
                lane="literature_applicability",
                title=f"Primary-source ingestion: {source['title']}",
                required_output=[
                    "primary artifact hash or a documented access failure",
                    "page, section, theorem, or algorithm anchors",
                    "exact mechanism and limitation extraction",
                    "read-status update only after full-text inspection",
                ],
                evidence_refs=[f"source:{source_id}", source.get("url", "")],
            )
        )
    return stubs


def _typed_cell_stubs(
    typed_state: dict[str, Any],
) -> list[dict[str, Any]]:
    stubs: list[dict[str, Any]] = []
    for cell in typed_state.get("cells", []):
        if not cell.get("seed_eligible"):
            continue
        cell_id = cell["cell_id"]
        route_id = cell["route_id"]
        evidence_refs = [
            f"cell:{cell_id}",
            *cell.get("evidence_paths", []),
        ]
        intake_mode = cell.get("intake_mode")
        if intake_mode == "property_resolution":
            stubs.append(
                _base_stub(
                    kind="structural_applicability",
                    anchor=cell_id,
                    purpose=(
                        "Resolve the unknown target-property requirement with "
                        "an exact construction or a scoped no-instance result. "
                        "Do not run an ECDLP experiment."
                    ),
                    lane="structural",
                    route_id=route_id,
                    title=f"Applicability resolution: {cell['mechanism_id']}",
                    required_output=[
                        "exact map, domain, codomain, kernel, and degree",
                        "target and fixed-target semantics",
                        "recovery map and exceptional components",
                        "complete preprocessing estimate",
                        "property verdict limited to this mechanism instance",
                    ],
                    evidence_refs=evidence_refs,
                )
            )
        if intake_mode == "desk_cost_bridge":
            stubs.append(
                _base_stub(
                    kind="desk_cost_contract",
                    anchor=cell_id,
                    purpose=(
                        "Price the exact symbolic system before any solver run "
                        "and compare it with matched generic and plain-relation "
                        "baselines."
                    ),
                    lane="mechanism",
                    route_id=route_id,
                    title=f"Desk cost bridge: {cell['mechanism_id']}",
                    required_output=[
                        "degree and monomial-size bounds",
                        "online and offline compute",
                        "memory, storage, money, and reviewer effort",
                        "preprocessing, amortization, and recovery",
                        "a scoped stop decision with no solver execution",
                    ],
                    evidence_refs=evidence_refs,
                )
            )
        cost_quantity = cell.get("cost_quantity", {})
        if (
            intake_mode == "property_resolution"
            and cost_quantity.get("status") in {"missing", "partial"}
        ):
            stubs.append(
                _base_stub(
                    kind="full_cost_contract",
                    anchor=cell_id,
                    purpose=(
                        "Specify the faithful generalized-root and recovery "
                        "pipeline as a separate full-cost obligation after, "
                        "and not as a substitute for, applicability."
                    ),
                    lane="mechanism",
                    route_id=route_id,
                    title=f"Full cost contract: {cost_quantity.get('label')}",
                    required_output=[
                        "source and target objects",
                        "generalized-root solver interface",
                        "recovery and spurious-fiber accounting",
                        "offline and online costs",
                        "matched end-to-end baseline and cost-changing bridge",
                    ],
                    evidence_refs=[
                        *evidence_refs,
                        f"cost_quantity:{cell.get('cost_quantity_id')}",
                    ],
                )
            )
    return stubs


def _parked_claim_ideas(
    typed_state: dict[str, Any],
    claim_state: dict[str, Any],
) -> list[dict[str, Any]]:
    claim_by_variant = {
        claim.get("mechanism_variant_id"): claim
        for claim in claim_state.get("claims", [])
    }
    parked: list[dict[str, Any]] = []
    for cell in typed_state.get("cells", []):
        if cell.get("status") != "open" or cell.get("intake_mode") != "none":
            continue
        mechanism_id = cell.get("mechanism_id", "")
        if "GLV-FAITHFUL-PHASE" not in mechanism_id:
            continue
        claim = claim_by_variant.get("MV-GLV-PHASE-PRESERVING-UNSPECIFIED")
        parked.append(
            {
                "parked_id": f"PARKED-{mechanism_id}",
                "cell_id": cell["cell_id"],
                "route_id": cell["route_id"],
                "claim_id": claim.get("claim_id") if claim else None,
                "status": "desired_properties_only",
                "seed_eligible": False,
                "executable": False,
                "authorized": False,
                "missing_before_intake": [
                    "exact phase-preserving map",
                    "complete recovery semantics",
                    "exceptional-locus treatment",
                    "non-orbit cost-changing bridge",
                ],
                "boundary": cell.get("boundary"),
            }
        )
    return parked


def build_state(
    source_registry: dict[str, Any],
    typed_state: dict[str, Any],
    claim_state: dict[str, Any],
) -> dict[str, Any]:
    stubs = [
        *_unread_source_stubs(source_registry),
        *_typed_cell_stubs(typed_state),
    ]
    stubs = sorted(stubs, key=lambda stub: stub["stub_id"])
    parked = sorted(
        _parked_claim_ideas(typed_state, claim_state),
        key=lambda item: item["parked_id"],
    )
    return {
        "schema_version": "0.1-generated",
        "state_id": "research-engine-shadow-intake-v0",
        "status": "shadow_non_executing",
        "source_hashes": {
            "source_registry_sha256": sha256_json(source_registry),
            "typed_evidence_state_sha256": sha256_json(typed_state),
            "research_claim_state_sha256": sha256_json(claim_state),
        },
        "counts": {
            "proposal_stubs": len(stubs),
            "parked_ideas": len(parked),
            "admissible": 0,
            "recommended": 0,
            "authorized": 0,
            "route_promotions": 0,
            "exact_target_experiments": 0,
        },
        "proposal_stubs": stubs,
        "parked_ideas": parked,
        "generation_contract": {
            "inputs": [
                "unread primary sources",
                "typed property-resolution cells",
                "typed missing cost bridges",
                "inconclusive claims with desired properties only",
            ],
            "excluded_inputs": [
                "closed child claims",
                "decided-inapplicable cells",
                "prose-only desired mechanisms",
                "lexical duplicates",
            ],
            "rule": (
                "A stub remains a non-executable research-question seed until "
                "an immutable exact mechanism snapshot and all required "
                "independent reviews exist."
            ),
        },
    }


def render(state: dict[str, Any]) -> str:
    return json.dumps(state, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    state = build_state(
        load_json(SOURCE_REGISTRY_PATH),
        load_json(TYPED_STATE_PATH),
        load_json(CLAIM_STATE_PATH),
    )
    expected = render(state)
    if "--check" in sys.argv:
        if not OUTPUT_PATH.is_file():
            print(f"shadow intake FAILED: missing {OUTPUT_PATH}")
            return 1
        if OUTPUT_PATH.read_text(encoding="utf-8") != expected:
            print(
                "shadow intake FAILED: generated state is stale; "
                "run scripts/build_research_shadow_intake.py"
            )
            return 1
        print(
            "shadow intake passed: "
            f"{state['counts']['proposal_stubs']} non-executable stubs, "
            f"{state['counts']['parked_ideas']} parked idea, 0 authorized."
        )
        return 0
    OUTPUT_PATH.write_text(expected, encoding="utf-8", newline="\n")
    print(
        f"wrote {OUTPUT_PATH.relative_to(ROOT)}: "
        f"{state['counts']['proposal_stubs']} non-executable stubs, "
        f"{state['counts']['parked_ideas']} parked idea."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
