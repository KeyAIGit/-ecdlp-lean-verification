#!/usr/bin/env python3
"""Validate the SHA-bound UORC-056 C36 -> C37 authority repair.

The scientific packages are historical Git objects.  This checker keeps the
metadata correction narrow: C37 realizes C36's planned successor, while the
parallel multi-argument C36 package remains a distinct non-parent package.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parent.parent
CONTRACT = ROOT / "notes" / "UORC056_C_TRACK_LINEAGE_C36.json"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

CANONICAL_PARENT_BRANCH = "research/uorc056-regularized-anchor-miller-c36"
CANONICAL_PARENT_ID = "REGULARIZED-ANCHOR-MILLER-TRANSLATION-084"
CANONICAL_PARENT_SHA = "330ea2f084441c0375b2a6c675112b2b2e23bd88"
CANONICAL_PARENT_BLOB = "8d86765d4abd3842dceb71a781d7934032b37e7d"

REALIZED_CHILD_BRANCH = "research/uorc056-half-index-miller-c37"
REALIZED_CHILD_ID = "HALF-INDEX-MILLER-QUADRATIC-BRANCH-085"
REALIZED_CHILD_SHA = "0b36801d1d413ec595fad87509e85c0368a9ead7"
REALIZED_CHILD_PATH = "notes/UORC056_C_TRACK_LINEAGE_C37.json"
REALIZED_CHILD_BLOB = "df8514d695f703bc5f2acb9bb2b0119f001a4de2"

PARALLEL_C36_BRANCH = "research/uorc056-multi-argument-miller-decoder-c36"
PARALLEL_C36_ID = "MULTI-ARGUMENT-MILLER-DECODER-084"
PARALLEL_C36_SHA = "7fc757fa31740e40ec68f8d27b572765fc244a39"
PARALLEL_C36_BLOB = "7291998b654cb37b4bf5812babba343b519757cf"

PLANNED_SUCCESSOR = "MIXED-INDEX-ELLIPTIC-NET-OR-RESULTANT-C37"
C35_CURRENT_SHA = "7c64cf1acda8569945e7f5298b557571f3585a3a"
C35_FORK_SHA = "a19e137f5a0a06c4a00506141ccb89be053ab8bc"


class AuthorityError(ValueError):
    """The authority contract is inconsistent or ambiguous."""


def _mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AuthorityError(f"{label} must be an object")
    return value


def _exact(value: object, expected: object, label: str) -> None:
    if value != expected:
        raise AuthorityError(f"{label} must be {expected!r}, got {value!r}")


def _sha(value: object, label: str) -> str:
    if not isinstance(value, str) or SHA_RE.fullmatch(value) is None:
        raise AuthorityError(f"{label} must be one lowercase 40-hex Git SHA")
    return value


def load_contract(path: Path = CONTRACT) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AuthorityError("lineage contract root must be an object")
    return value


def validate_contract(value: Mapping[str, Any]) -> None:
    """Validate the downstream-compatible edge and all typed provenance."""

    _exact(value.get("package"), "C36", "package")
    _exact(value.get("canonical_id"), CANONICAL_PARENT_ID, "canonical_id")
    _exact(value.get("branch"), CANONICAL_PARENT_BRANCH, "branch")
    _exact(value.get("successor"), REALIZED_CHILD_BRANCH, "successor")
    _exact(
        value.get("planned_successor"),
        PLANNED_SUCCESSOR,
        "planned_successor",
    )

    authority = _mapping(value.get("authority"), "authority")
    _exact(
        authority.get("schema_version"),
        "uorc056-lineage-authority/v1",
        "authority.schema_version",
    )
    entities = _mapping(authority.get("entities"), "authority.entities")
    expected_names = {
        "canonical_parent",
        "planned_successor",
        "realized_child",
        "parallel_c36",
    }
    _exact(set(entities), expected_names, "authority entity names")

    parent = _mapping(entities["canonical_parent"], "canonical_parent")
    child = _mapping(entities["realized_child"], "realized_child")
    parallel = _mapping(entities["parallel_c36"], "parallel_c36")
    planned = _mapping(entities["planned_successor"], "planned_successor")

    for actual, expected, label in (
        (parent.get("canonical_id"), CANONICAL_PARENT_ID, "parent canonical ID"),
        (parent.get("branch"), CANONICAL_PARENT_BRANCH, "parent branch"),
        (parent.get("pr"), 407, "parent PR"),
        (parent.get("scientific_head_sha"), CANONICAL_PARENT_SHA, "parent SHA"),
        (parent.get("source_blob_sha"), CANONICAL_PARENT_BLOB, "parent blob"),
        (planned.get("planned_id"), PLANNED_SUCCESSOR, "planned ID"),
        (child.get("canonical_id"), REALIZED_CHILD_ID, "child canonical ID"),
        (child.get("branch"), REALIZED_CHILD_BRANCH, "child branch"),
        (child.get("pr"), 408, "child PR"),
        (child.get("scientific_head_sha"), REALIZED_CHILD_SHA, "child SHA"),
        (child.get("parent_branch"), CANONICAL_PARENT_BRANCH, "child parent branch"),
        (
            child.get("parent_scientific_head_sha"),
            CANONICAL_PARENT_SHA,
            "child parent SHA",
        ),
        (child.get("source_path"), REALIZED_CHILD_PATH, "child source path"),
        (child.get("source_blob_sha"), REALIZED_CHILD_BLOB, "child source blob"),
        (parallel.get("canonical_id"), PARALLEL_C36_ID, "parallel canonical ID"),
        (parallel.get("branch"), PARALLEL_C36_BRANCH, "parallel branch"),
        (parallel.get("pr"), 406, "parallel PR"),
        (parallel.get("scientific_head_sha"), PARALLEL_C36_SHA, "parallel SHA"),
        (parallel.get("source_blob_sha"), PARALLEL_C36_BLOB, "parallel source blob"),
        (parallel.get("authorizing"), False, "parallel authorizing flag"),
    ):
        _exact(actual, expected, label)

    for entity_name, entity in (
        ("canonical_parent", parent),
        ("realized_child", child),
        ("parallel_c36", parallel),
    ):
        _sha(entity.get("scientific_head_sha"), f"{entity_name} scientific SHA")
        _sha(entity.get("source_blob_sha"), f"{entity_name} source blob")

    raw_relations = authority.get("relations")
    if not isinstance(raw_relations, list):
        raise AuthorityError("authority.relations must be a list")
    relations: list[tuple[str, str, str]] = []
    for index, raw_relation in enumerate(raw_relations):
        relation = _mapping(raw_relation, f"authority.relations[{index}]")
        if set(relation) != {"type", "source", "target"}:
            raise AuthorityError(f"relation {index} has unsupported fields")
        row = (
            str(relation["type"]),
            str(relation["source"]),
            str(relation["target"]),
        )
        if row[1] not in entities or row[2] not in entities:
            raise AuthorityError(f"relation {index} references an unknown entity")
        relations.append(row)

    expected_relations = {
        ("REALIZES", "realized_child", "planned_successor"),
        ("SUCCESSOR", "canonical_parent", "realized_child"),
        ("PARENT", "realized_child", "canonical_parent"),
        ("PARALLEL", "parallel_c36", "canonical_parent"),
    }
    if len(relations) != len(set(relations)):
        raise AuthorityError("authority relations contain duplicates")
    _exact(set(relations), expected_relations, "typed authority relations")
    if any(kind == "SUPERSEDES" for kind, _, _ in relations):
        raise AuthorityError("parallel C36 packages must not be marked SUPERSEDES")
    _exact(authority.get("supersession_relations"), [], "supersession relations")

    parent_relations = [
        (source, target)
        for kind, source, target in relations
        if kind == "PARENT" and source == "realized_child"
    ]
    _exact(
        parent_relations,
        [("realized_child", "canonical_parent")],
        "C37 typed parent",
    )
    if any(
        kind in {"PARENT", "SUCCESSOR"}
        and "parallel_c36" in {source, target}
        and "realized_child" in {source, target}
        for kind, source, target in relations
    ):
        raise AuthorityError("parallel C36 #406 must never be a C37 parent")

    provenance = _mapping(authority.get("git_provenance"), "git_provenance")
    _exact(provenance.get("audited_at"), "2026-08-17", "audit date")
    _exact(
        provenance.get("parallel_c36_is_ancestor_of_realized_child"),
        False,
        "parallel-C36 ancestry declaration",
    )
    expected_bases = {
        "canonical_parent_pr_base": (
            C35_CURRENT_SHA,
            C35_FORK_SHA,
            False,
        ),
        "parallel_c36_pr_base": (
            C35_CURRENT_SHA,
            C35_CURRENT_SHA,
            True,
        ),
        "realized_child_pr_base": (
            CANONICAL_PARENT_SHA,
            CANONICAL_PARENT_SHA,
            True,
        ),
    }
    for name, (head, merge_base, is_ancestor) in expected_bases.items():
        row = _mapping(provenance.get(name), name)
        _exact(row.get("observed_head_sha"), head, f"{name} observed head")
        _exact(row.get("merge_base_sha"), merge_base, f"{name} merge base")
        _exact(
            row.get("observed_head_is_ancestor"),
            is_ancestor,
            f"{name} ancestry",
        )
        _sha(row.get("observed_head_sha"), f"{name} observed head")
        _sha(row.get("merge_base_sha"), f"{name} merge base")


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", *args),
        cwd=ROOT,
        check=check,
        text=True,
        capture_output=True,
        encoding="utf-8",
    )


def _is_ancestor(ancestor: str, descendant: str) -> bool:
    result = _git("merge-base", "--is-ancestor", ancestor, descendant, check=False)
    if result.returncode not in {0, 1}:
        raise AuthorityError(
            f"git ancestry check failed for {ancestor} -> {descendant}: "
            f"{result.stderr.strip()}"
        )
    return result.returncode == 0


def _git_json(commit: str, path: str) -> Mapping[str, Any]:
    result = _git("show", f"{commit}:{path}")
    return _mapping(json.loads(result.stdout), f"{path}@{commit}")


def verify_git_provenance() -> None:
    """Verify pinned blobs and the positive/negative ancestry regression."""

    for sha in {
        CANONICAL_PARENT_SHA,
        REALIZED_CHILD_SHA,
        PARALLEL_C36_SHA,
        C35_CURRENT_SHA,
        C35_FORK_SHA,
    }:
        _git("cat-file", "-e", f"{sha}^{{commit}}")

    for commit, path, expected_blob in (
        (
            CANONICAL_PARENT_SHA,
            "notes/UORC056_C_TRACK_LINEAGE_C36.json",
            CANONICAL_PARENT_BLOB,
        ),
        (REALIZED_CHILD_SHA, REALIZED_CHILD_PATH, REALIZED_CHILD_BLOB),
    ):
        actual = _git("rev-parse", f"{commit}:{path}").stdout.strip()
        _exact(actual, expected_blob, f"Git blob {path}@{commit}")

    _git("cat-file", "-e", f"{PARALLEL_C36_BLOB}^{{blob}}")
    parallel_tree = _git("ls-tree", "-r", PARALLEL_C36_SHA).stdout.splitlines()
    if not any(
        row.startswith(f"100644 blob {PARALLEL_C36_BLOB}\t")
        for row in parallel_tree
    ):
        raise AuthorityError("parallel C36 source blob is absent from its pinned head")

    _exact(
        _is_ancestor(CANONICAL_PARENT_SHA, REALIZED_CHILD_SHA),
        True,
        "canonical C36 ancestry to C37",
    )
    _exact(
        _is_ancestor(PARALLEL_C36_SHA, REALIZED_CHILD_SHA),
        False,
        "parallel C36 ancestry to C37",
    )
    _exact(
        _git("merge-base", CANONICAL_PARENT_SHA, REALIZED_CHILD_SHA).stdout.strip(),
        CANONICAL_PARENT_SHA,
        "canonical C36/C37 merge base",
    )
    _exact(
        _git("merge-base", PARALLEL_C36_SHA, REALIZED_CHILD_SHA).stdout.strip(),
        C35_FORK_SHA,
        "parallel C36/C37 merge base",
    )

    child = _git_json(REALIZED_CHILD_SHA, REALIZED_CHILD_PATH)
    _exact(child.get("canonical_id"), REALIZED_CHILD_ID, "Git child canonical ID")
    _exact(child.get("branch"), REALIZED_CHILD_BRANCH, "Git child branch")
    _exact(
        child.get("parent_branch"),
        CANONICAL_PARENT_BRANCH,
        "Git child parent branch",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify-git",
        action="store_true",
        help="also verify the pinned historical Git objects and ancestry",
    )
    args = parser.parse_args(argv)
    try:
        validate_contract(load_contract())
        if args.verify_git:
            verify_git_provenance()
    except (AuthorityError, json.JSONDecodeError, OSError, subprocess.CalledProcessError) as error:
        print(f"UORC056_C36_C37_AUTHORITY_FAILED: {error}", file=sys.stderr)
        return 1
    print("UORC056_C36_C37_AUTHORITY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
