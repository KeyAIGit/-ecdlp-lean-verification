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
    status = read_text("STATUS.md")
    index = read_text("index.html")
    dashboard = read_text("dashboard.html")
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

    check(f'data-to="{ledger_rows}"' in index,
          "index.html ledger counter does not match data/stats.json")
    check(f'data-to="{distinct}"' in index,
          "index.html distinct-results counter does not match data/stats.json")
    check(f"snapshot {ledger_rows} ledger rows / ~{distinct} distinct" in dashboard,
          "dashboard.html snapshot stamp does not match data/stats.json")
    check("Sync Health" in dashboard,
          "dashboard.html must expose a Sync Health section")
    check("repo/ARTIFACTS.yaml" in dashboard and "scripts/check_repo_artifacts.py" in dashboard,
          "dashboard.html Sync Health must link the artifact manifest to its gate")

    graph_counts = graph.get("counts", {})
    check(isinstance(graph_counts.get("theorems"), int) and graph_counts["theorems"] > 0,
          "data/knowledge_graph.json must expose counts.theorems")
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

    if errors:
        print("Research OS consistency check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Research OS consistency OK: "
        f"{ledger_rows} ledger rows / ~{distinct} distinct; "
        f"{corpus_claims} corpus claims; {graph_counts['theorems']} graph theorems"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
