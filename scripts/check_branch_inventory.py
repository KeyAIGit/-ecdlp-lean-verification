#!/usr/bin/env python3
"""Validate the non-destructive remote-branch inventory snapshot."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INVENTORY = ROOT / "repo" / "BRANCH_INVENTORY.json"
ALLOWED = {
    "keep_default",
    "active_integration",
    "predecessor_draft",
    "candidate_queue",
    "historical_unmerged",
}


def main() -> int:
    data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    snapshot = data.get("snapshot", {})
    policy = data.get("policy", {})
    branches = data.get("branches", [])
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    names = [branch.get("name") for branch in branches]
    check(all(isinstance(name, str) and name for name in names),
          "branch names must be non-empty strings")
    check(len(names) == len(set(names)), "branch names must be unique")
    check(len(branches) == snapshot.get("real_remote_branch_count"),
          "snapshot branch count does not match branch entries")
    check(policy.get("merge_now") is False, "branch policy must forbid merge_now")
    check(policy.get("delete_now") is False, "branch policy must forbid delete_now")

    counts = Counter(branch.get("disposition") for branch in branches)
    check(set(counts) <= ALLOWED, "branch inventory contains an unsupported disposition")
    check(dict(counts) == data.get("groups"), "group counts do not match branch entries")

    by_name = {branch.get("name"): branch for branch in branches}
    main = by_name.get("main", {})
    check(main.get("disposition") == "keep_default", "main must be keep_default")
    check(main.get("ahead_main") == 0 and main.get("behind_main") == 0,
          "main must be the zero-distance comparison base")
    check(main.get("tip") == snapshot.get("base_sha"), "main tip/base_sha mismatch")

    active = [branch for branch in branches
              if branch.get("disposition") == "active_integration"]
    check(len(active) == 1, "exactly one active integration branch is required")
    if active:
        check(active[0].get("name") == policy.get("active_integration"),
              "active branch does not match policy.active_integration")
        check(active[0].get("based_on_branch") in by_name,
              "active branch must identify its predecessor branch")

    predecessors = [branch for branch in branches
                    if branch.get("disposition") == "predecessor_draft"]
    check(len(predecessors) == 1, "exactly one predecessor draft is required")
    if predecessors:
        check(predecessors[0].get("pull_request") == policy.get("predecessor_draft_pr"),
              "predecessor PR does not match policy")

    for branch in branches:
        name = branch.get("name", "<missing>")
        check(branch.get("delete_now") is False, f"{name}: delete_now must be false")
        check(bool(branch.get("next_action")), f"{name}: next_action is required")
        check(isinstance(branch.get("ahead_main"), int)
              and branch.get("ahead_main", -1) >= 0, f"{name}: invalid ahead_main")
        check(isinstance(branch.get("behind_main"), int)
              and branch.get("behind_main", -1) >= 0, f"{name}: invalid behind_main")
        check(bool(re.fullmatch(r"[0-9a-f]{40}", branch.get("tip", ""))),
              f"{name}: tip must be a full commit SHA")

    if errors:
        print("branch-inventory check FAILED:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"branch-inventory check OK: {len(branches)} real remote branches; "
        f"{counts['active_integration']} active, {counts['predecessor_draft']} predecessor, "
        f"{counts['candidate_queue']} candidate, {counts['historical_unmerged']} historical; "
        "no deletions authorized"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
