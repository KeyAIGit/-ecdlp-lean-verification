#!/usr/bin/env python3
"""Check or append review snapshots for the current hypothesis-funnel root."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from hypothesis_funnel import ROOT, STATE_PATH, load_policy, sha256_json
from hypothesis_ranker import REVIEW_LEDGER_PATH


SNAPSHOT_FIELDS = (
    "semantic_signature_sha256",
    "base_id",
    "family",
    "type",
    "mechanism_obligation_id",
    "cost_bridge_id",
    "decisive_test_id",
    "dimensions",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_lines(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def current_entries() -> list[dict[str, Any]]:
    policy = load_policy()
    state = load_json(STATE_PATH)
    root = state["bulk_contract"]["merkle_root_sha256"]
    queue = {
        item["semantic_signature_sha256"]: item
        for item in state["review_queue"]
    }
    entries: list[dict[str, Any]] = []
    for review in policy["review_decisions"]:
        candidate = queue.get(review["semantic_signature_sha256"])
        if candidate is None:
            raise ValueError(
                f"review {review['review_id']} is outside the current queue"
            )
        frozen_review = copy.deepcopy(review)
        digest = sha256_json(frozen_review)
        entries.append(
            {
                "schema_version": "1.0",
                "funnel_id": policy["funnel_id"],
                "batch_merkle_root_sha256": root,
                "semantic_signature_sha256": review[
                    "semantic_signature_sha256"
                ],
                "candidate_snapshot": {
                    key: copy.deepcopy(candidate[key]) for key in SNAPSHOT_FIELDS
                },
                "review_record": frozen_review,
                "review_record_sha256": digest,
                "label_id": f"HRL-{digest[:24].upper()}",
            }
        )
    return entries


def identity(entry: dict[str, Any]) -> tuple[str, str, str]:
    return (
        entry["funnel_id"],
        entry["batch_merkle_root_sha256"],
        entry["review_record"]["review_id"],
    )


def check(existing: list[dict[str, Any]], expected: list[dict[str, Any]]) -> list[str]:
    index = {identity(item): item for item in existing}
    problems: list[str] = []
    for item in expected:
        key = identity(item)
        if key not in index:
            problems.append(f"missing current review snapshot: {key[2]}")
        elif index[key] != item:
            problems.append(f"current review snapshot drifted: {key[2]}")
    return problems


def append_missing(
    path: Path,
    existing: list[dict[str, Any]],
    expected: list[dict[str, Any]],
) -> int:
    index = {identity(item): item for item in existing}
    additions: list[dict[str, Any]] = []
    for item in expected:
        key = identity(item)
        if key in index:
            if index[key] != item:
                raise ValueError(f"refusing to rewrite current snapshot: {key[2]}")
            continue
        additions.append(item)
    if not additions:
        return 0
    with path.open("ab") as handle:
        for item in additions:
            line = json.dumps(
                item, ensure_ascii=True, separators=(",", ":"), sort_keys=True
            )
            handle.write((line + "\n").encode("ascii"))
    return len(additions)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--append-current", action="store_true")
    args = parser.parse_args()

    existing = load_lines(REVIEW_LEDGER_PATH)
    expected = current_entries()
    if args.check:
        problems = check(existing, expected)
        if problems:
            for problem in problems:
                print(problem)
            return 1
        print(
            "hypothesis review ledger OK: current root has "
            f"{len(expected)} review snapshots; historical rows retained."
        )
        return 0
    added = append_missing(REVIEW_LEDGER_PATH, existing, expected)
    print(f"appended {added} current-root review snapshots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
