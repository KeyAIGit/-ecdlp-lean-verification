#!/usr/bin/env python3
"""Validate KeyAI's canonical product model and public-claim boundary."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "repo" / "PRODUCT_MODEL.json"


def main() -> int:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    try:
        model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"product model check failed: {exc}", file=sys.stderr)
        return 1

    check(model.get("schema_version") == "1.0", "schema_version must be 1.0")
    check(model.get("name") == "KeyAI", "name must be KeyAI")
    check(
        model.get("category") == "verification workspace for AI research",
        "category must remain the canonical product category",
    )

    workflow = model.get("workflow", [])
    workflow_ids = [step.get("id") for step in workflow if isinstance(step, dict)]
    check(
        workflow_ids == ["ingest", "structure", "decide", "execute", "verify", "retain"],
        "workflow must preserve the six-stage product loop",
    )
    check(
        all(step.get("label") and step.get("outcome") for step in workflow),
        "every workflow step needs a label and outcome",
    )

    hypotheses = model.get("customer_hypotheses", [])
    check(len(hypotheses) >= 2, "at least two customer hypotheses are required")
    check(
        all(item.get("status") == "unvalidated" for item in hypotheses),
        "customer hypotheses must stay unvalidated until pilot evidence is recorded",
    )

    reference = model.get("reference_environment", {})
    for key in (
        "decision_source",
        "formal_source",
        "stats_source",
        "frontier_source",
        "result_source",
        "task_source",
    ):
        path = reference.get(key)
        check(isinstance(path, str) and bool(path), f"reference_environment.{key} is required")
        if isinstance(path, str) and path:
            check((ROOT / path).exists(), f"reference_environment.{key} does not exist: {path}")
    check(
        "does not solve" in reference.get("boundary", "").lower(),
        "reference boundary must state that the environment does not solve ECDLP",
    )

    stage = model.get("current_stage", {})
    check(stage.get("id") == "reference-deployment", "current stage must be reference-deployment")
    check(
        len(stage.get("capabilities_now", [])) >= 4,
        "current stage must expose at least four evidenced capabilities",
    )
    for capability in stage.get("capabilities_now", []):
        for evidence in capability.get("evidence", []):
            check((ROOT / evidence).exists(), f"capability evidence does not exist: {evidence}")
    check(
        len(stage.get("not_yet", [])) >= 5,
        "current stage must retain an explicit not-yet boundary",
    )

    mvp = model.get("mvp", {})
    check("non-owner" in mvp.get("definition", ""), "MVP must require a non-owner user")
    check(
        any(metric.get("id") == "external-pilot" for metric in mvp.get("exit_metrics", [])),
        "MVP exit metrics must include an external pilot",
    )
    check(
        mvp.get("yc_readiness", "").startswith("Not ready today."),
        "YC readiness must remain evidence-gated until a pilot exists",
    )

    position = model.get("competitive_position", {})
    check(
        "general autonomous mathematician" in position.get("not_a", []),
        "competitive boundary must reject the autonomous-mathematician claim",
    )
    check(
        "Lean is the current exact verifier" in position.get("verifier_policy", ""),
        "verifier policy must identify Lean as the current verifier",
    )

    policy = model.get("public_claim_policy", {})
    check(len(policy.get("required", [])) >= 5, "public claim policy needs required claims")
    check(len(policy.get("forbidden", [])) >= 5, "public claim policy needs forbidden claims")
    check(
        any("finished autonomous research engine" in item for item in policy.get("forbidden", [])),
        "public claim policy must forbid the finished autonomous-engine claim",
    )

    surfaces = {item.get("path"): item for item in model.get("site_surfaces", [])}
    for path in ("index.html", "dashboard.html", "explore.html"):
        check(path in surfaces, f"site surface is missing: {path}")

    if errors:
        print("product model check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "product model check OK: "
        f"{len(workflow)} workflow stages, "
        f"{len(stage['capabilities_now'])} evidenced capabilities, "
        f"{len(hypotheses)} unvalidated customer hypotheses"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
