#!/usr/bin/env python3
"""Shared reachability rules for Git-pinned scientific evidence."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / "repo" / "SCIENTIFIC_PROVENANCE_V0.json"
COMMIT_ID = re.compile(r"[0-9a-f]{40}")


def load_policy(path: Path = POLICY_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_success(*args: str, root: Path = ROOT) -> bool:
    return (
        subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )


def git_commit_exists(commit: Any, *, root: Path = ROOT) -> bool:
    return (
        isinstance(commit, str)
        and COMMIT_ID.fullmatch(commit) is not None
        and _git_success("cat-file", "-e", f"{commit}^{{commit}}", root=root)
    )


def git_ref_commit(ref: Any, *, root: Path = ROOT) -> str | None:
    if not isinstance(ref, str) or not ref.startswith("refs/"):
        return None
    result = subprocess.run(
        ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
        cwd=root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    value = result.stdout.strip()
    return value if result.returncode == 0 and COMMIT_ID.fullmatch(value) else None


def validation_problems(policy: dict[str, Any] | None = None) -> list[str]:
    policy = policy or load_policy()
    problems: list[str] = []
    if policy.get("schema_version") != "0.1":
        problems.append("scientific provenance schema_version must be 0.1")
    protected = policy.get("protected_main")
    if not isinstance(protected, dict):
        return problems + ["scientific provenance protected_main must be an object"]
    anchor = protected.get("commit")
    if not git_commit_exists(anchor):
        problems.append("scientific provenance protected_main commit does not resolve")
    refs = policy.get("immutable_evidence_refs")
    if not isinstance(refs, list):
        return problems + ["immutable_evidence_refs must be an array"]
    seen: set[str] = set()
    for index, item in enumerate(refs):
        label = f"immutable_evidence_refs[{index}]"
        if not isinstance(item, dict):
            problems.append(f"{label} must be an object")
            continue
        if set(item) != {"ref", "commit", "purpose"}:
            problems.append(f"{label} has invalid fields")
            continue
        ref = item.get("ref")
        commit = item.get("commit")
        if not isinstance(ref, str) or not ref.startswith("refs/tags/evidence/"):
            problems.append(f"{label}.ref must live under refs/tags/evidence/")
        elif ref in seen:
            problems.append(f"{label}.ref is duplicated")
        else:
            seen.add(ref)
        if not git_commit_exists(commit):
            problems.append(f"{label}.commit does not resolve")
        resolved = git_ref_commit(ref)
        if resolved is not None and resolved != commit:
            problems.append(f"{label}.ref does not resolve to its pinned commit")
        if not isinstance(item.get("purpose"), str) or not item["purpose"].strip():
            problems.append(f"{label}.purpose must be nonempty")
    return problems


def scientific_source_commit_allowed(
    commit: Any,
    policy: dict[str, Any] | None = None,
    *,
    root: Path = ROOT,
) -> bool:
    if not git_commit_exists(commit, root=root):
        return False
    policy = policy or load_policy()
    protected = policy.get("protected_main", {})
    anchor = protected.get("commit")
    if git_commit_exists(anchor, root=root) and _git_success(
        "merge-base", "--is-ancestor", commit, anchor, root=root
    ):
        return True
    for item in policy.get("immutable_evidence_refs", []):
        if not isinstance(item, dict) or item.get("commit") != commit:
            continue
        ref = item.get("ref")
        if git_ref_commit(ref, root=root) == commit:
            return True
    return False


def git_file_bytes(commit: str, relative: str) -> bytes | None:
    if not scientific_source_commit_allowed(commit):
        return None
    result = subprocess.run(
        ["git", "show", f"{commit}:{relative}"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return result.stdout if result.returncode == 0 else None
