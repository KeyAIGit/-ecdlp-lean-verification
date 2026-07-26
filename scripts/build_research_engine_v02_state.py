#!/usr/bin/env python3
"""Build the deterministic, non-executing Research Engine v0.2 state."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from research_engine_v02 import run_engine, sha256_json

ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / "repo" / "RESEARCH_ENGINE_LIFECYCLE_V0.json"
V0_POLICY_PATH = ROOT / "repo" / "RESEARCH_ENGINE_V0.json"
GENERATION_STATE_PATH = ROOT / "data" / "research_engine_state.json"
STATE_PATH = ROOT / "data" / "research_engine_v02_state.json"
OUTCOMES_DIR = ROOT / "experiments" / "engine" / "outcomes"

V0_REVIEWED_ROOT = (
    "d9de2351a499d395d09005199aac73744c1bf212ff9759ceed5d229d076ca7a3"
)
V0_RAW_FILE_SHA256 = {
    "REO-2026-07-24-001": (
        "04da083fdd540da92542d04bd8b436a4b81f653c5f2fe8f220186aed230b6f2f"
    ),
    "REO-2026-07-24-002": (
        "47f03443503d078c069081b2c5645e617dede099fd57ae8b93f6cf8447eebed9"
    ),
    "REO-2026-07-24-003": (
        "a2e846d65df808c65b9ea3cecf8af0ce09d65b9b04c0184599f6cd00a10e2359"
    ),
    "REO-2026-07-24-004": (
        "19b98cfe564a0fb07f081184af0e03504f0b36fe472c0681bff9e1598a7bea11"
    ),
    "REO-2026-07-24-005": (
        "6fdc5b81828447b43f91ed6cd5c0480454eee266832046489a4d3076c8dd68e0"
    ),
    "REO-2026-07-24-006": (
        "1dd743cb8cc12ca46e1212dd14e389763d1bcdca867660e045f0e08c09bb25ed"
    ),
    "REO-2026-07-24-007": (
        "e0e6916381f61884db2775caedb7d751443ec4bc117f76480a1915a3e8e21183"
    ),
    "REO-2026-07-24-008": (
        "4be39c49f910c4a3c33c9f2e2b6956b437debf5269a1afcdcfa7a9e998d45e45"
    ),
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def reviewed_sha256_json(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def historical_boundary() -> tuple[list[dict[str, str]], str, str]:
    events: list[dict[str, Any]] = []
    file_records: list[dict[str, str]] = []
    for path in sorted(OUTCOMES_DIR.glob("REO-2026-07-24-*.json")):
        event = load_json(path)
        event_id = event.get("event_id")
        if not isinstance(event_id, str):
            event_id = path.stem
        raw_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        events.append(event)
        file_records.append(
            {
                "event_id": event_id,
                "canonical_event_sha256": reviewed_sha256_json(event),
                "raw_file_sha256": raw_sha256,
            }
        )
    reviewed_root = reviewed_sha256_json(
        sorted(events, key=lambda event: event["event_id"])
    )
    raw_file_root = reviewed_sha256_json(file_records)
    return file_records, reviewed_root, raw_file_root


def validate_policy(policy: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if policy.get("schema_version") != "0.2":
        problems.append("lifecycle policy schema_version must be 0.2")
    if policy.get("status") != "implementation_non_executable":
        problems.append("lifecycle policy must remain non-executable")
    if policy.get("primary_threat_model") != (
        "classical-single-target-plain"
    ):
        problems.append("lifecycle policy threat model drifted")
    if policy.get("authorization_count") != 0:
        problems.append("lifecycle policy authorization_count must be zero")
    if policy.get("route_promotion_count") != 0:
        problems.append("lifecycle policy route_promotion_count must be zero")
    if policy.get("direct_target_experiment_count") != 0:
        problems.append(
            "lifecycle policy direct_target_experiment_count must be zero"
        )
    if policy.get("owner_decisions") != []:
        problems.append("no owner authorization decision is registered")
    for snapshot in policy.get("candidate_snapshots", []):
        if "authorization" in snapshot or "authorized" in snapshot:
            problems.append(
                "candidate snapshots cannot contain authorization fields"
            )
    return problems


def build() -> tuple[list[str], dict[str, Any]]:
    policy = load_json(POLICY_PATH)
    v0_policy = load_json(V0_POLICY_PATH)
    generation_state = load_json(GENERATION_STATE_PATH)
    problems = validate_policy(policy)
    historical_events, reviewed_root, raw_file_root = historical_boundary()
    if len(historical_events) != 8:
        problems.append("exactly eight frozen historical events are required")
    v0_baseline = v0_policy.get("historical_outcome_baseline", {})
    if v0_baseline.get("anchor_sha256") != V0_REVIEWED_ROOT:
        problems.append("v0 policy review-anchored root changed")
    if reviewed_root != V0_REVIEWED_ROOT:
        problems.append("review-anchored historical JSON root changed")
    expected_canonical = {
        record["event_id"]: record["event_sha256"]
        for record in v0_baseline.get("events", [])
    }
    for record in historical_events:
        event_id = record["event_id"]
        if record["canonical_event_sha256"] != expected_canonical.get(event_id):
            problems.append(f"{event_id}: canonical event digest changed")
        if record["raw_file_sha256"] != V0_RAW_FILE_SHA256.get(event_id):
            problems.append(f"{event_id}: raw file bytes changed")
    if set(V0_RAW_FILE_SHA256) != {
        record["event_id"] for record in historical_events
    }:
        problems.append("historical raw-file baseline membership changed")
    runtime_policy = dict(policy)
    runtime_policy["quality_cleared_draft_bindings"] = [
        {
            "draft_id": draft.get("draft_id"),
            "draft_sha256": draft.get("draft_sha256"),
            "proposal_id": draft.get("proposal_id"),
            "proposal_sha256": draft.get("proposal_sha256"),
            "source_commit": draft.get("source_commit"),
            "review_artifacts": draft.get("review_artifacts"),
        }
        for draft in generation_state.get(
            "retained_hypothesis_drafts", []
        )
        if isinstance(draft, dict)
    ]
    engine = run_engine(
        runtime_policy,
        policy.get("candidate_snapshots", []),
        {
            "lifecycle_events": policy.get("lifecycle_events", []),
            "outcomes": [],
        },
        policy.get("owner_decisions", []),
    )
    if engine.get("authorized") != []:
        problems.append("generated v0.2 state must authorize zero candidates")
    if engine.get("route_promotions") != []:
        problems.append("generated v0.2 state must promote zero routes")
    if engine.get("direct_target_executions") != []:
        problems.append("generated v0.2 state must run no exact target")
    state = {
        "schema_version": "0.2-generated",
        "engine_id": "ecdlp-research-engine-v0.2",
        "status": "shadow_non_executing",
        "source_hashes": {
            "lifecycle_policy_sha256": sha256_json(policy),
            "quality_cleared_generation_state_sha256": sha256_json(
                generation_state
            ),
            "review_anchored_v0_root_sha256": reviewed_root,
            "raw_historical_file_manifest_sha256": raw_file_root,
        },
        "historical_outcome_boundary": {
            "event_count": len(historical_events),
            "events": historical_events,
            "migration": "referenced_not_rewritten",
            "review_anchored_root_sha256": reviewed_root,
            "raw_bytes_pinned": true_value(),
            "calibration_eligible": false_value(),
        },
        "engine": engine,
        "authorization": {
            "experiments": 0,
            "route_promotions": 0,
            "exact_target_runs": 0,
        },
    }
    return sorted(set(problems)), state


def false_value() -> bool:
    return False


def true_value() -> bool:
    return True


def render(state: dict[str, Any]) -> str:
    return json.dumps(state, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    problems, state = build()
    if problems:
        print("Research Engine v0.2 state FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    expected = render(state)
    if "--check" in sys.argv:
        if not STATE_PATH.is_file():
            print(f"Research Engine v0.2 state FAILED: missing {STATE_PATH}")
            return 1
        if STATE_PATH.read_text(encoding="utf-8") != expected:
            print(
                "Research Engine v0.2 state FAILED: generated state is stale; "
                "run scripts/build_research_engine_v02_state.py"
            )
            return 1
        print(
            "Research Engine v0.2 state passed: shadow mode, "
            "0 candidates, 0 authorized, 8 frozen outcomes referenced."
        )
        return 0
    STATE_PATH.write_text(expected, encoding="utf-8", newline="\n")
    print(
        f"wrote {STATE_PATH.relative_to(ROOT)}: "
        f"{state['historical_outcome_boundary']['event_count']} frozen outcomes, "
        "0 authorized."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
