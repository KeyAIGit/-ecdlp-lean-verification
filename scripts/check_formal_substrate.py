#!/usr/bin/env python3
"""Validate the canonical formal-substrate architecture manifest."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "repo" / "FORMAL_SUBSTRATE.json"

# The graph builder owns the ledger parser and area classifier. Importing it keeps
# the family partition identical to the generated graph without a second taxonomy.
sys.path.insert(0, str(ROOT / "scripts"))
import build_knowledge_graph as knowledge  # noqa: E402


def main() -> int:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"formal-substrate check FAILED: {exc}", file=sys.stderr)
        return 1

    families = data.get("families", [])
    blockers = data.get("blockers", [])
    nodes = data.get("critical_nodes", [])
    targets = data.get("open_targets", [])
    allowed_statuses = set(data.get("status_vocabulary", {}))

    def unique_ids(items: list[dict], label: str) -> set[str]:
        ids = [item.get("id") for item in items]
        check(all(isinstance(item_id, str) and item_id for item_id in ids),
              f"{label}: every item needs a non-empty id")
        check(len(ids) == len(set(ids)), f"{label}: ids must be unique")
        return {item_id for item_id in ids if isinstance(item_id, str)}

    family_ids = unique_ids(families, "families")
    blocker_ids = unique_ids(blockers, "blockers")
    node_ids = unique_ids(nodes, "critical_nodes")
    unique_ids(targets, "open_targets")

    ledger = knowledge.parse_ledger()
    ledger_names = [row["name"] for row in ledger]
    ledger_areas = {
        knowledge.classify_area(
            row["claim"],
            " ".join(knowledge.file_to_module(file) for file in row["files"]),
        )
        for row in ledger
    }
    family_areas = [family.get("area") for family in families]
    check(len(family_areas) == len(set(family_areas)),
          "families: each graph area must have exactly one family")
    check(set(family_areas) == ledger_areas,
          f"families: area partition mismatch (manifest={sorted(set(family_areas))}, "
          f"ledger={sorted(ledger_areas)})")

    graph: dict[str, list[str]] = {}
    for node in nodes:
        node_id = node.get("id", "<missing>")
        status = node.get("status")
        disposition = node.get("release_disposition")
        check(status in allowed_statuses, f"{node_id}: unsupported status {status!r}")
        check(disposition in {"closed", "blocked_accepted", "deferred"},
              f"{node_id}: unsupported release_disposition {disposition!r}")
        if status == "closed":
            check(disposition == "closed", f"{node_id}: closed node must have closed disposition")
        if status == "blocked":
            check(disposition == "blocked_accepted",
                  f"{node_id}: blocked node must be explicitly blocked_accepted")
            check(bool(node.get("blocker_ids")), f"{node_id}: blocked node needs blocker_ids")
        if status in {"parked", "out_of_release"}:
            check(disposition == "deferred", f"{node_id}: deferred node needs deferred disposition")

        deps = node.get("depends_on", [])
        graph[node_id] = deps
        for dep in deps:
            check(dep in node_ids, f"{node_id}: unknown dependency {dep}")
        for family_id in node.get("family_ids", []):
            check(family_id in family_ids, f"{node_id}: unknown family {family_id}")
        for blocker_id in node.get("blocker_ids", []):
            check(blocker_id in blocker_ids, f"{node_id}: unknown blocker {blocker_id}")
        for anchor in node.get("anchors", []):
            check(any(anchor in cell for cell in ledger_names),
                  f"{node_id}: anchor is not present in the ledger: {anchor}")
        for rel in node.get("evidence_files", []):
            check((ROOT / rel).exists(), f"{node_id}: missing evidence file {rel}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visiting:
            errors.append(f"critical_nodes: dependency cycle reaches {node_id}")
            return
        if node_id in visited:
            return
        visiting.add(node_id)
        for dep in graph.get(node_id, []):
            visit(dep)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in node_ids:
        visit(node_id)

    for blocker in blockers:
        blocker_id = blocker.get("id", "<missing>")
        check(bool(blocker.get("resume_condition")),
              f"{blocker_id}: blocker needs a resume_condition")
        for rel in blocker.get("evidence_files", []):
            check((ROOT / rel).exists(), f"{blocker_id}: missing evidence file {rel}")

    required = data.get("release", {}).get("required_nodes", [])
    check(len(required) == len(set(required)), "release.required_nodes contains duplicates")
    by_node = {node.get("id"): node for node in nodes}
    expected_required = {
        node.get("id") for node in nodes
        if node.get("release_disposition") != "deferred"
    }
    check(
        set(required) == expected_required,
        "release.required_nodes must contain every and only non-deferred critical node",
    )
    for node_id in required:
        check(node_id in by_node, f"release: unknown required node {node_id}")
        if node_id in by_node:
            check(by_node[node_id].get("release_disposition") in {"closed", "blocked_accepted"},
                  f"release: required node {node_id} has no closure disposition")

    for target in targets:
        target_id = target.get("id", "<missing>")
        check(target.get("critical_node") in node_ids,
              f"{target_id}: unknown critical_node {target.get('critical_node')}")
        registry = ROOT / target.get("registry", "")
        check(registry.is_file(), f"{target_id}: missing target registry {registry}")
        if registry.is_file():
            spec = json.loads(registry.read_text(encoding="utf-8"))
            check(spec.get("status") == target.get("status"),
                  f"{target_id}: manifest/registry status mismatch")
            check(set(spec.get("blocker_ids", [])) == set(target.get("blocker_ids", [])),
                  f"{target_id}: manifest/registry blocker_ids mismatch")
        check(
            set(target.get("blocker_ids", []))
            == set(by_node.get(target.get("critical_node"), {}).get("blocker_ids", [])),
            f"{target_id}: target/critical-node blocker_ids mismatch",
        )
        for stem in target.get("stems", []):
            path = ROOT / stem.get("file", "")
            check(path.is_file(), f"{target_id}: missing stem {stem.get('file')}")
            if path.is_file():
                count = len(re.findall(r"^\s*sorry\s*$", path.read_text(encoding="utf-8"),
                                       flags=re.MULTILINE))
                check(count == stem.get("expected_sorry"),
                      f"{target_id}: {stem.get('file')} has {count} bare sorry, "
                      f"expected {stem.get('expected_sorry')}")

    referenced_blockers = {
        blocker_id
        for node in nodes
        for blocker_id in node.get("blocker_ids", [])
    }
    check(referenced_blockers == blocker_ids,
          "blockers: every declared blocker must be referenced by a critical node")

    if errors:
        print("formal-substrate check FAILED:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    dispositions = {
        key: sum(node.get("release_disposition") == key for node in nodes)
        for key in ("closed", "blocked_accepted", "deferred")
    }
    print(
        "formal-substrate check OK: "
        f"{len(ledger)} ledger rows / {len(families)} exhaustive families / "
        f"{len(nodes)} critical nodes "
        f"({dispositions['closed']} closed, {dispositions['blocked_accepted']} blocked, "
        f"{dispositions['deferred']} deferred)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
