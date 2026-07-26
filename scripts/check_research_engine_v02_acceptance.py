#!/usr/bin/env python3
"""Check that every owner-mandated v0.2 regression has a concrete test."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
ACCEPTANCE_PATH = ROOT / "repo" / "RESEARCH_ENGINE_V0_2_ACCEPTANCE.json"
DECISION_PATH = ROOT / "repo" / "ECDLP_DECISION_SUBSTRATE.json"
LIFECYCLE_PATH = ROOT / "repo" / "RESEARCH_ENGINE_LIFECYCLE_V0.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
    print(
        "Research Engine v0.2 acceptance passed: "
        f"19/19 owner cases, {referenced} test references, "
        "0 authorization and 0 promotion."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
