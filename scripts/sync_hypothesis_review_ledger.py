#!/usr/bin/env python3
"""Check or append review snapshots for the current hypothesis-funnel root."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from hypothesis_funnel import ROOT, STATE_PATH, load_policy, sha256_json
from hypothesis_ranker import (
    REVIEW_LEDGER_PATH,
    candidate_evidence_manifest,
    load_review_ledger,
    review_ledger_entry_digest,
    reviewed_evidence_closure_sha256,
)


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


def load_existing_reviews(path: Path = REVIEW_LEDGER_PATH) -> list[dict[str, Any]]:
    """Use the ranker's full integrity checks before reporting sync status."""

    return load_review_ledger(path)


def current_entries() -> list[dict[str, Any]]:
    policy = load_policy()
    state = load_json(STATE_PATH)
    root = state["bulk_contract"]["merkle_root_sha256"]
    evidence_closure = reviewed_evidence_closure_sha256()
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
        manifest = candidate_evidence_manifest(frozen_review)
        entry = {
            "schema_version": "2.0",
            "funnel_id": policy["funnel_id"],
            "batch_merkle_root_sha256": root,
            "global_evidence_closure_sha256": evidence_closure,
            "reviewed_evidence_manifest": manifest,
            "reviewed_evidence_closure_sha256": sha256_json(manifest),
            "semantic_signature_sha256": review["semantic_signature_sha256"],
            "candidate_snapshot": {
                key: copy.deepcopy(candidate[key]) for key in SNAPSHOT_FIELDS
            },
            "review_record": frozen_review,
            "review_record_sha256": digest,
        }
        entry_digest = review_ledger_entry_digest(entry)
        entry["ledger_entry_sha256"] = entry_digest
        entry["label_id"] = f"HRL-{entry_digest[:24].upper()}"
        entries.append(entry)
    return entries


def scientific_identity(entry: dict[str, Any]) -> dict[str, Any]:
    """Return the immutable label content, excluding its evidence-batch binding."""

    return {
        key: value
        for key, value in entry.items()
        if key
        not in {
            "batch_merkle_root_sha256",
            "global_evidence_closure_sha256",
            "ledger_entry_sha256",
            "label_id",
        }
    }


def legacy_scientific_identity(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        key: entry.get(key)
        for key in (
            "funnel_id",
            "semantic_signature_sha256",
            "candidate_snapshot",
            "review_record",
            "review_record_sha256",
        )
    }


def is_legacy_unbound_match(
    existing: dict[str, Any], expected: dict[str, Any]
) -> bool:
    return (
        existing.get("schema_version") == "1.0"
        and "reviewed_evidence_closure_sha256" not in existing
        and legacy_scientific_identity(existing) == legacy_scientific_identity(expected)
    )


def check(existing: list[dict[str, Any]], expected: list[dict[str, Any]]) -> list[str]:
    index = {
        item["review_record"]["review_id"]: item for item in existing
    }
    problems: list[str] = []
    for item in expected:
        review_id = item["review_record"]["review_id"]
        if review_id not in index:
            problems.append(f"missing current review snapshot: {review_id}")
        elif scientific_identity(index[review_id]) != scientific_identity(item) and not is_legacy_unbound_match(
            index[review_id], item
        ):
            problems.append(f"current review snapshot drifted: {review_id}")
    return problems


def append_missing(
    path: Path,
    existing: list[dict[str, Any]],
    expected: list[dict[str, Any]],
) -> int:
    index = {
        item["review_record"]["review_id"]: item for item in existing
    }
    additions: list[dict[str, Any]] = []
    for item in expected:
        review_id = item["review_record"]["review_id"]
        if review_id in index:
            if scientific_identity(index[review_id]) != scientific_identity(item) and not is_legacy_unbound_match(
                index[review_id], item
            ):
                raise ValueError(
                    f"refusing to rewrite current snapshot: {review_id}"
                )
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

    existing = load_existing_reviews(REVIEW_LEDGER_PATH)
    expected = current_entries()
    if args.check:
        problems = check(existing, expected)
        if problems:
            for problem in problems:
                print(problem)
            return 1
        index = {item["review_record"]["review_id"]: item for item in existing}
        legacy_unbound = sum(
            is_legacy_unbound_match(index[item["review_record"]["review_id"]], item)
            for item in expected
        )
        current_bound = sum(
            index[item["review_record"]["review_id"]].get("schema_version") == "2.0"
            and scientific_identity(index[item["review_record"]["review_id"]])
            == scientific_identity(item)
            for item in expected
        )
        stale = len(expected) - legacy_unbound - current_bound
        print(
            "hypothesis review ledger OK: "
            f"current_bound={current_bound} legacy_unbound={legacy_unbound} "
            f"stale={stale}; historical rows retained."
        )
        return 0
    added = append_missing(REVIEW_LEDGER_PATH, existing, expected)
    print(f"appended {added} current-root review snapshots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
