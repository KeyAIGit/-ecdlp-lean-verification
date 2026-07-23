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

ROOT = Path(__file__).resolve().parent.parent


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def read_json(path: str) -> dict:
    return json.loads(read_text(path))


def main() -> int:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    stats = read_json("data/stats.json")
    frontier = read_json("data/frontier_map.json")
    graph = read_json("data/knowledge_graph.json")
    decisions = read_json("repo/ECDLP_DECISION_SUBSTRATE.json")
    product = read_json("repo/PRODUCT_MODEL.json")
    status = read_text("STATUS.md")
    index = read_text("index.html")
    dashboard = read_text("dashboard.html")
    explore = read_text("explore.html")
    tasks = read_text("tasks/NEXT.md")
    hypotheses = read_text("experiments/HYPOTHESES.yaml")

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
    check("repo/ARTIFACTS.yaml" in dashboard and "scripts/check_repo_artifacts.py" in dashboard,
          "dashboard.html Sync Health must link the artifact manifest to its gate")
    check(
        product.get("category") in index
        and product.get("category") in dashboard
        and product.get("category") in explore,
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
        and "repo/PRODUCT_MODEL.json" in explore,
        "all public surfaces must link the canonical product model",
    )
    check(
        all("assets/site.css" in page and "assets/site.js" in page
            for page in (index, dashboard, explore)),
        "all public surfaces must use the shared site assets",
    )
    public_site = (index + dashboard + explore).lower()
    for retired_claim in ("autonomous engine", "verified environment for a strong ai"):
        check(
            retired_claim not in public_site,
            f"public site contains retired product claim: {retired_claim!r}",
        )
    route_count = len(decisions.get("routes", []))
    check(
        f"{route_count} canonical routes" in dashboard,
        "dashboard route count must match the decision substrate",
    )
    check(
        f"data-route-count>{route_count} routes" in explore,
        "explore route count must match the decision substrate",
    )
    check(
        route_selection.get("decision_id") in dashboard
        and route_selection.get("decision_id") in explore
        and "Select none" in dashboard
        and "Select none" in explore,
        "dashboard and explore must expose the canonical select-none decision",
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
    check(graph_counts.get("decision_foundations") == 11,
          "data/knowledge_graph.json must expose all 11 decision foundations")
    check(graph.get("schema_version") == "3.0",
          "data/knowledge_graph.json must use decision-aware schema 3.0")
    check(
        graph.get("decision_substrate", {}).get("route_selection") == route_selection,
        "knowledge graph route selection must match ECDLP_DECISION_SUBSTRATE.json",
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
    ):
        check(edge_types.get(edge_type, 0) > 0,
              f"knowledge graph is missing semantic edge type {edge_type!r}")
    check(graph.get("invariant", "").lower().find("lean kernel") >= 0,
          "data/knowledge_graph.json invariant should mention the Lean kernel")

    check("Task Contract Template" in tasks,
          "tasks/NEXT.md must include the task contract template")
    check(3 <= len(re.findall(r"^### TASK-", tasks, flags=re.MULTILINE)) <= 7,
          "tasks/NEXT.md must keep 3-7 active tasks")
    check("canonical_source: STATUS.md" in hypotheses,
          "experiments/HYPOTHESES.yaml must point at STATUS.md")
    check("task_queue: tasks/NEXT.md" in hypotheses,
          "experiments/HYPOTHESES.yaml must point at tasks/NEXT.md")
    check(len(re.findall(r"^  - id: H", hypotheses, flags=re.MULTILINE)) >= 3,
          "experiments/HYPOTHESES.yaml must define at least three hypotheses")
    check('status: "parked"' in hypotheses and "resume_after:" in hypotheses,
          "deferred experiments must be parked with an explicit resume condition")

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
