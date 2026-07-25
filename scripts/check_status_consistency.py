#!/usr/bin/env python3
"""Check Research OS truth-layer consistency.

This is a cheap, dependency-free gate for the non-Lean operating layer. It does
not prove mathematical claims; it catches drift between generated machine views,
the canonical status page, the public HTML counters, and the active work files.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pilot_evidence import task_012_unlocked

ROOT = Path(__file__).resolve().parent.parent


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def read_json(path: str) -> dict:
    return json.loads(read_text(path))


def relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted(
        (relative_luminance(foreground), relative_luminance(background)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def css_hex_variable(stylesheet: str, name: str) -> str | None:
    match = re.search(rf"{re.escape(name)}:\s*(#[0-9a-fA-F]{{6}})\s*;", stylesheet)
    return match.group(1) if match else None


def main() -> int:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    stats = read_json("data/stats.json")
    frontier = read_json("data/frontier_map.json")
    graph = read_json("data/knowledge_graph.json")
    decisions = read_json("repo/ECDLP_DECISION_SUBSTRATE.json")
    engine = read_json("data/research_engine_state.json")
    product = read_json("repo/PRODUCT_MODEL.json")
    pilot_protocol = read_json("repo/PILOT_PROTOCOL.json")
    status = read_text("STATUS.md")
    index = read_text("index.html")
    dashboard = read_text("dashboard.html")
    explore = read_text("explore.html")
    pilot = read_text("pilot.html")
    tasks = read_text("tasks/NEXT.md")
    research_tasks = read_text("tasks/ECDLP_RESEARCH.md")
    product_tasks = read_text("tasks/KEYAI_PRODUCT.md")
    hypotheses = read_text("experiments/HYPOTHESES.yaml")
    autonomy = read_text("AUTONOMY.md")
    agents = read_text("AGENTS.md")
    architecture = read_text("REPOSITORY_ARCHITECTURE.md")
    site_css = read_text("assets/site.css")
    autonomous_workflow = read_text(".github/workflows/autonomous-engine.yml")
    ci_workflow = read_text(".github/workflows/ci.yml")

    ledger_rows = stats.get("ledger_rows")
    distinct = stats.get("distinct_results")
    proved_modules = stats.get("proved_modules")
    sorry_count = stats.get("sorry_count")
    custom_axioms = stats.get("custom_axioms")
    corpus_claims = frontier.get("meta", {}).get("corpus_claims")
    frontier_rows = frontier.get("meta", {}).get("verified_ledger_rows")
    status_summary = frontier.get("status_summary", {})
    route_selection = decisions.get("route_selection", {})

    check(isinstance(ledger_rows, int) and ledger_rows > 0,
          "data/stats.json must expose a positive integer ledger_rows")
    check(isinstance(distinct, int) and distinct > 0,
          "data/stats.json must expose a positive integer distinct_results")
    check(frontier_rows == ledger_rows,
          "frontier_map.meta.verified_ledger_rows must match stats.ledger_rows")
    check(sum(int(v) for v in status_summary.values()) == corpus_claims,
          "frontier_map.status_summary must sum to meta.corpus_claims")

    check(f"| ledger rows | **{ledger_rows}**" in status,
          "STATUS.md ledger row does not match data/stats.json")
    check(f"| distinct results | **~{distinct}**" in status,
          "STATUS.md distinct-results row does not match data/stats.json")
    check(f"| proved modules | **{proved_modules}**" in status,
          "STATUS.md proved-modules row does not match data/stats.json")
    check(f"| `sorry` | **{sorry_count}**" in status,
          "STATUS.md sorry row does not match data/stats.json")
    check(f"| custom axioms | **{custom_axioms}**" in status,
          "STATUS.md custom-axioms row does not match data/stats.json")

    for name, value in status_summary.items():
        check(f"| {name} | **{value}**" in status,
              f"STATUS.md corpus row for {name!r} does not match frontier_map")

    check(
        f"**Category:** {product.get('category')}." in status,
        "STATUS.md must expose the canonical product category",
    )
    check(
        f"**Current stage:** {product.get('current_stage', {}).get('label')}." in status,
        "STATUS.md must expose the canonical product stage",
    )
    check(
        product.get("mvp", {}).get("definition") in status,
        "STATUS.md must expose the canonical MVP boundary",
    )
    check(
        pilot_protocol.get("id") in status
        and pilot_protocol.get("status") in status
        and pilot_protocol.get("evidence_state") in status,
        "STATUS.md must expose the canonical pilot state",
    )

    check(
        f'data-metric="ledger-rows">{ledger_rows}</div>' in index,
        "index.html ledger counter does not match data/stats.json",
    )
    check(
        f'data-metric="distinct-results">~{distinct}</div>' in index,
        "index.html distinct-results counter does not match data/stats.json",
    )
    check(f"snapshot {ledger_rows} ledger rows / ~{distinct} distinct" in dashboard,
          "dashboard.html snapshot stamp does not match data/stats.json")
    check(
        f'data-metric="ledger-rows">{ledger_rows}</span>' in explore,
        "explore.html ledger counter does not match data/stats.json",
    )
    check("Sync Health" in dashboard,
          "dashboard.html must expose a Sync Health section")
    check(
        "Work queues" in dashboard
        and "tasks/NEXT.md" in dashboard
        and "tasks/ECDLP_RESEARCH.md" in dashboard
        and "tasks/KEYAI_PRODUCT.md" in dashboard,
        "dashboard must expose the queue router and both owning queues",
    )
    check("repo/ARTIFACTS.yaml" in dashboard and "scripts/check_repo_artifacts.py" in dashboard,
          "dashboard.html Sync Health must link the artifact manifest to its gate")
    check(
        product.get("category") in index
        and product.get("category") in dashboard
        and product.get("category") in explore
        and product.get("category") in pilot,
        "all public surfaces must expose the canonical product category",
    )
    check(
        product.get("current_stage", {}).get("label") in index
        and product.get("current_stage", {}).get("label") in dashboard,
        "index and dashboard must expose the canonical product stage",
    )
    check(
        "repo/PRODUCT_MODEL.json" in index
        and "repo/PRODUCT_MODEL.json" in dashboard
        and "repo/PRODUCT_MODEL.json" in explore
        and "repo/PRODUCT_MODEL.json" in pilot,
        "all public surfaces must link the canonical product model",
    )
    check(
        all("assets/site.css" in page and "assets/site.js" in page
            for page in (index, dashboard, explore, pilot)),
        "all public surfaces must use the shared site assets",
    )
    check(
        all(
            "The Lean kernel checks declared statements and proof terms" in page
            for page in (index, dashboard, explore, pilot)
        ),
        "all public surfaces must expose the verifier-scope caveat",
    )
    check(
        pilot_protocol.get("task_id") in pilot
        and pilot_protocol.get("status", "").title() in pilot
        and pilot_protocol.get("evidence_state") in pilot,
        "pilot.html must expose the canonical task, status, and evidence state",
    )
    intake_template = Path(product.get("pilot", {}).get("intake_surface", "")).name
    intake_url = (
        f"{product.get('repository_url', '').rstrip('/')}/issues/new?template={intake_template}"
    )
    check(
        bool(intake_template)
        and intake_url in index
        and intake_url in pilot,
        "product and pilot pages must derive the public intake URL from PRODUCT_MODEL.json",
    )
    check(
        'data-route-count aria-live="polite"' in explore
        and 'data-route-empty role="status" aria-live="polite"' in explore,
        "route result changes must be announced to assistive technology",
    )
    public_site = (index + dashboard + explore + pilot).lower()
    for retired_claim in (
        "autonomous engine",
        "verified environment for a strong ai",
        "turn ai research into verified, reusable state",
        "source material to verified asset",
    ):
        check(
            retired_claim not in public_site,
            f"public site contains retired product claim: {retired_claim!r}",
        )
    route_count = len(decisions.get("routes", []))
    selected_structural = route_selection.get("selected_route_ids", [])
    promoted_routes = route_selection.get("promoted_route_ids", [])
    selected_explorations = engine.get("counts", {}).get("selected_explorations")
    check(
        f"{route_count} canonical routes" in dashboard,
        "dashboard route count must match the decision substrate",
    )
    check(
        f'data-route-count aria-live="polite">{route_count} routes' in explore,
        "explore route count must match the decision substrate",
    )
    check(
        route_selection.get("decision_id") in dashboard
        and route_selection.get("decision_id") in explore
        and "Structural selection" in dashboard
        and "Structural selection" in explore,
        "dashboard and explore must expose the canonical structural decision",
    )
    check(
        f"{selected_explorations} experiments selected" in index
        and f"{selected_explorations} selected;" in dashboard
        and f"{len(selected_structural)} structural route completed" in explore
        and f"{len(promoted_routes)} promoted" in explore
        and "0 experiments authorized" in explore,
        "public reference views must expose the selected bounded exploration count",
    )
    check(
        "The bounded structural question is resolved; no experiment is authorized." in dashboard
        and "No run authorized" in dashboard
        and "repo/RESEARCH_ENGINE_V0.json" in dashboard
        and "Promotion experiments" in dashboard,
        "dashboard must distinguish the exploration and promotion gates",
    )

    graph_counts = graph.get("counts", {})
    check(isinstance(graph_counts.get("theorems"), int) and graph_counts["theorems"] > 0,
          "data/knowledge_graph.json must expose counts.theorems")
    check(graph_counts.get("ledger_rows") == ledger_rows,
          "data/knowledge_graph.json counts.ledger_rows must match data/stats.json")
    check(graph_counts.get("families") == 8,
          "data/knowledge_graph.json must expose the exhaustive eight-family partition")
    check(graph_counts.get("critical_nodes", 0) > 0,
          "data/knowledge_graph.json must expose formal critical-path nodes")
    check(graph_counts.get("attack_routes") == 17,
          "data/knowledge_graph.json must expose all 17 decision routes")
    check(
        graph_counts.get("decision_foundations")
        == len(decisions.get("foundations", [])),
        "data/knowledge_graph.json foundation count must match the decision substrate",
    )
    check(
        graph_counts.get("selected_structural_routes") == len(selected_structural)
        and graph_counts.get("promoted_routes") == len(promoted_routes),
        "knowledge graph structural and promotion counts must match route selection",
    )
    check(
        graph_counts.get("research_engine_candidates")
        == engine.get("counts", {}).get("candidate_proposals"),
        "knowledge graph candidate count must match research_engine_state.json",
    )
    check(
        graph_counts.get("research_engine_outcomes")
        == engine.get("counts", {}).get("outcome_events"),
        "knowledge graph outcome count must match research_engine_state.json",
    )
    check(
        graph_counts.get("selected_explorations")
        == engine.get("counts", {}).get("selected_explorations"),
        "knowledge graph selected exploration count must match research_engine_state.json",
    )
    check(graph.get("schema_version") == "4.0",
          "data/knowledge_graph.json must use Research Engine-aware schema 4.0")
    check(
        graph.get("decision_substrate", {}).get("route_selection") == route_selection,
        "knowledge graph route selection must match ECDLP_DECISION_SUBSTRATE.json",
    )
    graph_engine = graph.get("research_engine", {})
    check(
        graph_engine.get("gate_status") == engine.get("gate_status")
        and graph_engine.get("selected_sequence") == engine.get("selected_sequence")
        and graph_engine.get("execution_queue") == engine.get("execution_queue")
        and graph_engine.get("outcome_events") == engine.get("outcome_events"),
        "knowledge graph Research Engine view must match generated engine state",
    )
    check(
        engine.get("gate_status", {}).get("exploration_authorized")
        == True
        and decisions.get("phase_policy", {}).get(
            "bounded_exploration_authorized"
        )
        == False
        and engine.get("gate_status", {}).get("promotion_authorized")
        == decisions.get("phase_policy", {}).get(
            "promotion_experiments_authorized"
        )
        == False,
        "the Engine must retain exploration capability while the current "
        "structural decision authorizes no experiment and both layers keep "
        "promotion closed",
    )
    check(
        route_selection.get("decision_id") in status,
        "STATUS.md must expose the current route-selection decision",
    )
    edge_types = graph_counts.get("by_edge_type", {})
    for edge_type in (
        "imports",
        "member_of",
        "supports",
        "depends_on",
        "blocked_by",
        "evaluated_under",
        "detailed_by",
        "requires_foundation",
        "decision_grounded_in",
        "governs_hypothesis",
        "extends_frontier",
        "tests_hypothesis",
        "explores_route",
        "depends_on_candidate",
        "records_outcome_for",
        "updates_hypothesis",
        "records_route_evidence",
    ):
        check(edge_types.get(edge_type, 0) > 0,
              f"knowledge graph is missing semantic edge type {edge_type!r}")
    check(graph.get("invariant", "").lower().find("lean kernel") >= 0,
          "data/knowledge_graph.json invariant should mention the Lean kernel")

    check("Task contract template" in tasks,
          "tasks/NEXT.md must include the task contract template")
    all_task_text = research_tasks + "\n" + product_tasks
    check(3 <= len(re.findall(r"^### TASK-", all_task_text, flags=re.MULTILINE)) <= 7,
          "the two owning queues must keep 3-7 active task contracts in total")
    check(
        "tasks/ECDLP_RESEARCH.md" in tasks
        and "tasks/KEYAI_PRODUCT.md" in tasks
        and "Product work never counts as ECDLP progress" in tasks,
        "tasks/NEXT.md must route to separate research and product queues",
    )
    check("canonical_source: STATUS.md" in hypotheses,
          "experiments/HYPOTHESES.yaml must point at STATUS.md")
    check("task_queue: tasks/ECDLP_RESEARCH.md" in hypotheses,
          "experiments/HYPOTHESES.yaml must point at the ECDLP research queue")
    check(len(re.findall(r"^  - id: H", hypotheses, flags=re.MULTILINE)) >= 3,
          "experiments/HYPOTHESES.yaml must define at least three hypotheses")
    check('status: "parked"' in hypotheses and "resume_after:" in hypotheses,
          "deferred experiments must be parked with an explicit resume condition")
    check("Never use `git reset --hard`" in autonomy,
          "AUTONOMY.md must explicitly forbid destructive branch resets")
    check("Reset branch to `main`" not in agents,
          "AGENTS.md must not prescribe ambiguous branch resets")
    check(
        "repo/PILOT_PROTOCOL.json" in agents
        and "`build/change/stop/pending`" in agents
        and re.search(r"does not validate\s+the\s+adapter", agents) is not None,
        "AGENTS.md must expose the canonical TASK-011 discovery boundary",
    )
    check(
        "on-demand autonomous cycle" in autonomy
        and "repository itself has no recurring scheduler" in autonomy
        and "workflow_dispatch:" in autonomous_workflow
        and "\n  schedule:" not in autonomous_workflow,
        "autonomy documentation must match the dispatch-only autonomous workflow",
    )
    check(
        "${{ secrets." not in ci_workflow,
        "ordinary push/PR verification CI must not receive repository secrets",
    )
    secret_auto_triggers: list[str] = []
    for workflow_path in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        workflow_text = workflow_path.read_text(encoding="utf-8")
        if "${{ secrets." not in workflow_text:
            continue
        if re.search(
            r"^  (?:push|pull_request|pull_request_target|schedule):",
            workflow_text,
            flags=re.MULTILINE,
        ):
            secret_auto_triggers.append(workflow_path.name)
    check(
        not secret_auto_triggers,
        "secret-bearing workflows must remain manual-only: "
        + ", ".join(secret_auto_triggers),
    )
    check(
        "only open PRs in this repository" in autonomy
        and "Never act on another repository" in autonomy,
        "autonomous PR reconciliation must remain scoped to this repository",
    )
    check(
        "repo/PILOT_PROTOCOL.json" in architecture
        and "pilot.html" in architecture
        and "Generate all four pages" in architecture,
        "repository architecture must map the pilot protocol and all four public surfaces",
    )
    task_012_match = re.search(
        r"^### TASK-012\b.*?^Status:\s*([^\n]+)",
        product_tasks,
        flags=re.MULTILINE | re.DOTALL,
    )
    task_012_status = task_012_match.group(1).strip() if task_012_match else None
    check(
        task_012_match is not None,
        "tasks/KEYAI_PRODUCT.md must retain a TASK-012 contract",
    )
    if task_012_unlocked(pilot_protocol):
        check(
            task_012_status in {"active", "done", "completed"},
            "TASK-012 must have an explicit actionable or completed status after the "
            "latest primary build disposition",
        )
    else:
        check(
            task_012_status == "blocked_on_task_011_build_disposition"
            and "completed `TASK-011` discovery record with a `build` disposition"
            in product_tasks,
            "TASK-012 must remain explicitly blocked unless the latest primary "
            "discovery disposition is build",
        )
    blue = css_hex_variable(site_css, "--blue")
    quiet = css_hex_variable(site_css, "--quiet")
    check(
        blue is not None and contrast_ratio(blue, "#ffffff") >= 4.5,
        "primary blue must meet WCAG AA contrast against white text",
    )
    check(
        quiet is not None and contrast_ratio(quiet, "#e9eef1") >= 4.5,
        "quiet text must meet WCAG AA contrast on muted surfaces",
    )

    if errors:
        print("Research OS consistency check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Research OS consistency OK: "
        f"{ledger_rows} ledger rows / ~{distinct} distinct; "
        f"{corpus_claims} corpus claims; "
        f"{graph_counts['ledger_rows']} graph ledger-row nodes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
