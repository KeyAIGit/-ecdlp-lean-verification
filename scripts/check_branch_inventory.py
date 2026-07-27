#!/usr/bin/env python3
"""Validate a dated snapshot against the current remote branch-name set."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INVENTORY = ROOT / "repo" / "BRANCH_INVENTORY.json"
ALLOWED = {
    "keep_default",
    "active_integration",
    "superseded_draft",
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

    check(data.get("schema_version") == 2, "branch inventory schema must be 2")
    names = [branch.get("name") for branch in branches]
    check(
        all(isinstance(name, str) and name for name in names),
        "branch names must be non-empty strings",
    )
    check(len(names) == len(set(names)), "branch names must be unique")
    check(
        len(branches) == snapshot.get("real_remote_branch_count"),
        "snapshot branch count does not match branch entries",
    )
    check(policy.get("snapshot_only") is True, "inventory must be snapshot-only")
    check(policy.get("merge_now") is False, "branch policy must forbid merge_now")
    check(policy.get("delete_now") is False, "branch policy must forbid delete_now")

    counts = Counter(branch.get("disposition") for branch in branches)
    check(set(counts) <= ALLOWED, "unsupported branch disposition")
    check(dict(sorted(counts.items())) == data.get("groups"), "group count drift")

    by_name = {branch.get("name"): branch for branch in branches}
    main = by_name.get("main", {})
    check(main.get("disposition") == "keep_default", "main must be keep_default")
    check(
        main.get("ahead_main") == 0 and main.get("behind_main") == 0,
        "main must be the zero-distance comparison base",
    )
    check(main.get("tip") == snapshot.get("base_sha"), "main/base SHA mismatch")

    active = sorted(
        branch["name"]
        for branch in branches
        if branch.get("disposition") == "active_integration"
    )
    superseded = sorted(
        branch["name"]
        for branch in branches
        if branch.get("disposition") == "superseded_draft"
    )
    check(
        active == policy.get("active_integrations"),
        "active integrations do not match policy",
    )
    check(
        superseded == policy.get("superseded_drafts"),
        "superseded drafts do not match policy",
    )

    for branch in branches:
        name = branch.get("name", "<missing>")
        check(branch.get("delete_now") is False, f"{name}: delete_now must be false")
        check(bool(branch.get("next_action")), f"{name}: next_action is required")
        check(
            isinstance(branch.get("ahead_main"), int)
            and branch.get("ahead_main", -1) >= 0,
            f"{name}: invalid ahead_main",
        )
        check(
            isinstance(branch.get("behind_main"), int)
            and branch.get("behind_main", -1) >= 0,
            f"{name}: invalid behind_main",
        )
        check(
            bool(re.fullmatch(r"[0-9a-f]{40}", branch.get("tip", ""))),
            f"{name}: tip must be a full commit SHA",
        )

    result = subprocess.run(
        ["git", "ls-remote", "--heads", snapshot.get("remote", "origin")],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    check(result.returncode == 0, "remote branch names could not be queried")
    if result.returncode == 0:
        remote_names = sorted(
            line.split()[1].removeprefix("refs/heads/")
            for line in result.stdout.splitlines()
            if line.strip()
        )
        names_hash = hashlib.sha256(
            "\n".join(remote_names).encode("utf-8")
        ).hexdigest()
        check(
            remote_names == sorted(names),
            "remote branch name set differs from the dated snapshot",
        )
        check(
            names_hash == snapshot.get("remote_names_sha256"),
            "remote branch-name digest differs from snapshot",
        )

    if errors:
        print("branch-inventory check FAILED:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"branch-inventory check OK: {len(branches)} remote heads; "
        f"{counts['active_integration']} active, "
        f"{counts['superseded_draft']} superseded, "
        f"{counts['candidate_queue']} candidate; no merge/deletion authorized"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
