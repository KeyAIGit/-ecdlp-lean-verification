#!/usr/bin/env python3
"""Capture a non-destructive snapshot of real remote branch heads."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "repo" / "BRANCH_INVENTORY.json"
REMOTE = "origin"

ACTIVE = {
    "agent/research-engine-hypothesis-generation",
    "agent/glv-semaev-affine-closeout",
    "agent/task022-s17-materialization",
    "agent/task023-chart-cover",
    "agent/task024-infinity-strata",
    "agent/hyp-select-002-authorization",
    "agent/hyp-select-002-route-binding-correction",
}
SUPERSEDED = {
    "agent/n7-certificate-generator",
    "claude/research-engine-review",
}
CANDIDATE_QUEUES = {"prover/candidates", "server/candidates"}


def git(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def remote_heads() -> dict[str, str]:
    heads: dict[str, str] = {}
    for line in git("ls-remote", "--heads", REMOTE).splitlines():
        tip, ref = line.split()
        heads[ref.removeprefix("refs/heads/")] = tip
    return heads


def disposition(name: str) -> str:
    if name == "main":
        return "keep_default"
    if name in ACTIVE:
        return "active_integration"
    if name in SUPERSEDED:
        return "superseded_draft"
    if name in CANDIDATE_QUEUES:
        return "candidate_queue"
    return "historical_unmerged"


def build() -> dict:
    heads = remote_heads()
    main = heads["main"]
    branches = []
    for name, tip in sorted(
        heads.items(), key=lambda item: (item[0] != "main", item[0])
    ):
        git(
            "fetch",
            "-q",
            REMOTE,
            f"refs/heads/{name}:refs/remotes/{REMOTE}/{name}",
        )
        behind, ahead = (
            int(value)
            for value in git(
                "rev-list", "--left-right", "--count", f"{main}...{tip}"
            ).split()
        )
        merged = (
            subprocess.run(
                ["git", "merge-base", "--is-ancestor", tip, main],
                cwd=ROOT,
                check=False,
            ).returncode
            == 0
        )
        state = disposition(name)
        if name == "main":
            next_action = "keep"
        elif state == "active_integration":
            next_action = (
                "retain for the scoped draft integration; inventory does not "
                "authorize merge"
            )
        elif state == "superseded_draft":
            next_action = (
                "recommend closure as superseded; owner approval is required"
            )
        else:
            next_action = (
                "retain pending a dedicated content and restore-path audit"
            )
        branches.append(
            {
                "name": name,
                "tip": tip,
                "tip_date": git("show", "-s", "--format=%cs", tip),
                "behind_main": behind,
                "ahead_main": ahead,
                "merged_by_ancestry": merged,
                "disposition": state,
                "delete_now": False,
                "next_action": next_action,
            }
        )
    names_payload = "\n".join(sorted(heads)).encode("utf-8")
    groups = Counter(item["disposition"] for item in branches)
    return {
        "schema_version": 2,
        "snapshot": {
            "captured_at": datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),
            "remote": REMOTE,
            "base_ref": "origin/main",
            "base_sha": main,
            "real_remote_branch_count": len(branches),
            "remote_names_sha256": hashlib.sha256(names_payload).hexdigest(),
            "comparison": (
                "git rev-list --left-right --count <main-tip>...<branch-tip>"
            ),
            "recording_note": (
                "Tips are a dated observation. The active branch necessarily "
                "advances when this snapshot is committed; the gate compares "
                "the remote name set, not mutable tips."
            ),
        },
        "policy": {
            "snapshot_only": True,
            "merge_now": False,
            "delete_now": False,
            "active_integrations": sorted(ACTIVE & set(heads)),
            "superseded_drafts": sorted(SUPERSEDED & set(heads)),
            "cleanup_gate": (
                "Content comparison, reference scan, restore path, and explicit "
                "owner approval are required before deletion or closure."
            ),
        },
        "groups": dict(sorted(groups.items())),
        "branches": branches,
    }


def render(value: dict) -> str:
    return json.dumps(value, indent=2, ensure_ascii=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    OUTPUT.write_text(render(build()), encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
