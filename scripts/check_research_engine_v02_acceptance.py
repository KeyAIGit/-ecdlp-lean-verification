#!/usr/bin/env python3
"""Validate v0.2 acceptance references and non-execution safety gates.

This command checks that named tests and committed digest anchors exist. It does
not execute the referenced test functions; CI and the explicit test commands do.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any

from research_claims import load_and_build as load_and_build_claims

ROOT = Path(__file__).resolve().parent.parent
ACCEPTANCE_PATH = ROOT / "repo" / "RESEARCH_ENGINE_V0_2_ACCEPTANCE.json"
DECISION_PATH = ROOT / "repo" / "ECDLP_DECISION_SUBSTRATE.json"
LIFECYCLE_PATH = ROOT / "repo" / "RESEARCH_ENGINE_LIFECYCLE_V0.json"
LIFECYCLE_STATE_PATH = ROOT / "data" / "research_engine_v02_state.json"
GENERATION_STATE_PATH = ROOT / "data" / "research_engine_state.json"
DIGEST_ANCHOR_PATH = (
    ROOT
    / "experiments"
    / "engine"
    / "fixtures"
    / "research_engine_v02_snapshot_digest_anchors.json"
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_json(value: Any) -> str:
    payload = (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def source_binding_problems(
    lifecycle_state: dict[str, Any],
    lifecycle_policy: dict[str, Any],
    generation_state: dict[str, Any],
) -> list[str]:
    source_hashes = lifecycle_state.get("source_hashes", {})
    expected = {
        "lifecycle_policy_sha256": sha256_json(lifecycle_policy),
        "quality_cleared_generation_state_sha256": sha256_json(
            generation_state
        ),
    }
    return [
        f"generated lifecycle state {key} does not bind its canonical source"
        for key, digest in expected.items()
        if source_hashes.get(key) != digest
    ]


def digest_anchor_problems() -> list[str]:
    fixture = load_json(DIGEST_ANCHOR_PATH)
    anchors = fixture.get("anchors")
    if not isinstance(anchors, list) or len(anchors) < 2:
        return ["snapshot digest fixture must contain at least two anchors"]
    problems: list[str] = []
    computed: list[str] = []
    for index, anchor in enumerate(anchors):
        label = f"snapshot digest anchors[{index}]"
        if not isinstance(anchor, dict):
            problems.append(f"{label}: expected object")
            continue
        snapshot = anchor.get("snapshot")
        expected = anchor.get("expected_snapshot_sha256")
        if not isinstance(snapshot, dict):
            problems.append(f"{label}.snapshot: expected object")
            continue
        payload = dict(snapshot)
        payload.pop("snapshot_digest", None)
        actual = sha256_json(payload)
        computed.append(actual)
        if actual != expected:
            problems.append(f"{label}: external SHA-256 anchor mismatch")
    if len(computed) == len(anchors) and len(set(computed)) != len(computed):
        problems.append("snapshot digest anchors must have distinct digests")
    return problems


def test_functions(relative: str) -> set[str]:
    path = ROOT / relative
    if not path.is_file():
        return set()
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    }


def check_ref(ref: Any) -> str | None:
    if not isinstance(ref, str) or "::" not in ref:
        return f"invalid test ref {ref!r}"
    relative, function = ref.split("::", 1)
    if function not in test_functions(relative):
        return f"{ref}: test function does not exist"
    return None


def main() -> int:
    manifest = load_json(ACCEPTANCE_PATH)
    problems: list[str] = []
    cases = manifest.get("cases")
    if not isinstance(cases, list):
        problems.append("cases must be an array")
        cases = []
    if manifest.get("required_case_count") != 19 or len(cases) != 19:
        problems.append("acceptance manifest must contain exactly 19 cases")
    ids = [case.get("id") for case in cases if isinstance(case, dict)]
    if len(ids) != len(set(ids)):
        problems.append("acceptance case ids must be unique")
    for index, case in enumerate(cases):
        label = f"cases[{index}]"
        if not isinstance(case, dict):
            problems.append(f"{label}: expected object")
            continue
        for field in (
            "id",
            "requirement",
            "invariant",
            "test_refs",
            "fault_injection",
            "status",
        ):
            if field not in case:
                problems.append(f"{label}: missing {field}")
        if case.get("status") != "implemented":
            problems.append(f"{label}: status must be implemented")
        if not isinstance(case.get("fault_injection"), str) or not case[
            "fault_injection"
        ].strip():
            problems.append(f"{label}: fault_injection must be substantive")
        refs = case.get("test_refs")
        if not isinstance(refs, list) or not refs:
            problems.append(f"{label}: test_refs must be nonempty")
        else:
            for ref in refs:
                problem = check_ref(ref)
                if problem:
                    problems.append(problem)
    for oracle in manifest.get("supplementary_oracles", []):
        problem = check_ref(oracle.get("test_ref"))
        if problem:
            problems.append(problem)

    boundary = manifest.get("authorization_boundary", {})
    if any(boundary.get(key) != 0 for key in boundary):
        problems.append("acceptance authorization boundary must remain all zero")
    lifecycle = load_json(LIFECYCLE_PATH)
    lifecycle_state = load_json(LIFECYCLE_STATE_PATH)
    generation_state = load_json(GENERATION_STATE_PATH)
    problems += source_binding_problems(
        lifecycle_state,
        lifecycle,
        generation_state,
    )
    problems += digest_anchor_problems()
    claim_problems, _ = load_and_build_claims()
    problems += [
        f"canonical research claims: {problem}" for problem in claim_problems
    ]
    for key in (
        "authorization_count",
        "route_promotion_count",
        "direct_target_experiment_count",
    ):
        if lifecycle.get(key) != 0:
            problems.append(f"lifecycle {key} must remain zero")
    decisions = load_json(DECISION_PATH)
    phase = decisions.get("phase_policy", {})
    if phase.get("promotion_experiments_authorized") is not False:
        problems.append("decision substrate promotion must remain unauthorized")
    if phase.get("selected_attack_route") is not None:
        problems.append("decision substrate selected_attack_route must remain null")
    if any(
        route.get("authorized_experiment") is not False
        for route in decisions.get("routes", [])
    ):
        problems.append("every decision-substrate route must remain unauthorized")

    if problems:
        print("Research Engine v0.2 acceptance FAILED:")
        for problem in sorted(set(problems)):
            print(f"  - {problem}")
        return 1
    referenced = sum(len(case["test_refs"]) for case in cases)
    supplementary = len(manifest.get("supplementary_oracles", []))
    print(
        "Research Engine v0.2 acceptance manifest validated: "
        f"19 owner cases reference {referenced} existing test functions; "
        f"{supplementary} supplementary oracle references also resolve; "
        "this command did not execute them. "
        "Safety state: 0 authorization and 0 promotion."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
