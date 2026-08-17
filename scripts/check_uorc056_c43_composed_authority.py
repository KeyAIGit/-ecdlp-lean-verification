#!/usr/bin/env python3
"""Validate the SHA-bound C43/C43B composed-frontier authority record."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
LINEAGE_PATH = REPO_ROOT / "notes/UORC056_C_TRACK_LINEAGE_C43B.json"

C42 = "728d1a7a1c60463cc4546e2bb21fa3eaf3936d58"
C43 = "52015c53ce3770268437aac71ee74e0517719834"
C43B = "acdc7c6ea5d76ac58afb1574d1efa9bbf60c050f"
COMPOSITION = "1d436cba35b78526e800dae005aa2abce33a9994"
UNRELATED_C43 = "0122f7bbffb85f1240797626fedee7a7ee9c25e1"

C42_ENTITY = "C42-ORIENTED-TRANSPOSED-RESULTANT"
PLANNED_ENTITY = "C42-PLANNED-LOCAL-GLV-ROUTE"
C43_ENTITY = "C43-UNIVERSAL-COVER-FRAMEWORK"
C43B_ENTITY = "C43B-LOCAL-GLV-SPECIALIZATION"
COMPOSED_ENTITY = "C43-C43B-COMPOSED-FRONTIER"
OPEN_ENTITY = "C44-ORDERED-SECTOR-TRANSPORT-OPEN"
EXCLUDED_ENTITY = "C43-PERIOD-LATTICE-NET-GAUGE-UNTRUSTED"

EXPECTED_ENTITY_IDS = {
    C42_ENTITY,
    PLANNED_ENTITY,
    C43_ENTITY,
    C43B_ENTITY,
    COMPOSED_ENTITY,
    OPEN_ENTITY,
    EXCLUDED_ENTITY,
}

GENERAL_CLAIMS = {
    "hypotheses/H1-UNIVERSAL-COVER-SECTION",
    "hypotheses/H2-MU2-COHOMOLOGY-SPIN",
    "hypotheses/H3-DOUBLING-SYMBOLIC-DYNAMICS",
    "hypotheses/H4-P-ADIC-LOG-LIFT",
    "hypotheses/H5-TROPICAL-SKELETON",
    "hypotheses/H6-L-ADIC-TRACE-FUNCTION",
    "hypotheses/H7-GAUGE-TYPED-OPEN-TRANSPORT",
    "secp256k1_doubling_correction/ord_n(2)=(n-1)/64",
    "secp256k1_doubling_correction/ord_p(2)=(p-1)/14",
    "secp256k1_doubling_correction/pair_action_cycles=32",
}

LOCAL_CLAIMS = {
    "exact_algebra/kernel",
    "exact_algebra/carry_root",
    "exact_algebra/carry_square",
    "exact_algebra/sector_root",
    "exact_algebra/sector_square",
    "exact_algebra/reconstruction",
    "exact_algebra/parity",
    "secp256k1_frontier/residual_gauge",
}

EXPECTED_RELATIONS = {
    ("DECLARED_PARENT", C43_ENTITY, C42_ENTITY, None),
    ("DECLARED_PARENT", C43B_ENTITY, C42_ENTITY, None),
    ("REALIZES", C43B_ENTITY, PLANNED_ENTITY, None),
    (
        "REFINES",
        C43B_ENTITY,
        C43_ENTITY,
        "hypotheses/H7-GAUGE-TYPED-OPEN-TRANSPORT",
    ),
    ("COMPOSES", COMPOSED_ENTITY, C43_ENTITY, None),
    ("COMPOSES", COMPOSED_ENTITY, C43B_ENTITY, None),
    ("FRONTIER_CARRIER", COMPOSED_ENTITY, C43B_ENTITY, None),
    ("NEXT_OPEN_PROBLEM", COMPOSED_ENTITY, OPEN_ENTITY, None),
    ("EXCLUDES_FROM_AUTHORITY", COMPOSED_ENTITY, EXCLUDED_ENTITY, None),
}

EXPECTED_BINDINGS = {
    (
        C42_ENTITY,
        C42,
        "experiments/parity_lift_000/uorc056_oriented_transposed_resultant_c42.py",
        "2a0b5ea76adb749e877c963dc2ac5ad1717b44f9",
    ),
    (
        C42_ENTITY,
        C42,
        "notes/UORC056_ORIENTED_TRANSPOSED_RESULTANT_C42.md",
        "3a9ac5dc1e2e86cb20835fb1e5de5828acb63872",
    ),
    (
        C42_ENTITY,
        C42,
        "notes/UORC056_ORIENTED_TRANSPOSED_RESULTANT_C42_CONTRACT.md",
        "4122ff6302aae227c360cc005b03ea5165b5cdeb",
    ),
    (
        C43_ENTITY,
        C43,
        "experiments/parity_lift_000/uorc056_universal_cover_language_c43.py",
        "1d394d486b5d3cc343cb49a8e2cb2c436070232c",
    ),
    (
        C43_ENTITY,
        C43,
        "experiments/parity_lift_000/test_uorc056_universal_cover_language_c43.py",
        "cd0de291b0ba8de71cdc93c26db6b03ef735615d",
    ),
    (
        C43_ENTITY,
        C43,
        "notes/UORC056_UNIVERSAL_COVER_LANGUAGE_C43.md",
        "f5b3c3f43375c1d8622974f6018b3ab95ed2fb68",
    ),
    (
        C43_ENTITY,
        C43,
        "notes/UORC056_UNIVERSAL_COVER_LANGUAGE_C43_CONTRACT.md",
        "327072e0cbb492d7d022a335347922fe0d3852a9",
    ),
    (
        C43B_ENTITY,
        C43B,
        "experiments/parity_lift_000/uorc056_local_glv_sector_factorization_c43b.py",
        "e081f49e4ae5eb1473cbafe08c027bc1eb2f3724",
    ),
    (
        C43B_ENTITY,
        C43B,
        "experiments/parity_lift_000/test_uorc056_local_glv_sector_factorization_c43b.py",
        "8dd29c00641b2180fd642fe3bf117adb2a733f5c",
    ),
    (
        C43B_ENTITY,
        C43B,
        "Ecdlp/Proved/Uorc056LocalGlvGaugeBreaking.lean",
        "b75b35ffddbb5b161d81edeacd80078e67524696",
    ),
    (
        C43B_ENTITY,
        C43B,
        "notes/UORC056_LOCAL_GLV_SECTOR_FACTORIZATION_C43B.md",
        "3db15ef106b40fb900c4ba66e1ffe5e2ea25f9fe",
    ),
}

OPEN_GATES = {
    "sensitive to the residual Klein-four sector gauge",
    "generator-marked and ordered",
    "does not enumerate the (n-1)/6 GLV quotient roots",
    "does not hide an order-n table in advice or coefficients",
    (
        "exposes a circuit, recurrence, transfer law, or local functional "
        "equation whose total charged cost is explicit"
    ),
}

SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class AuthorityError(ValueError):
    """The authority record is incomplete, ambiguous, or historically false."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AuthorityError(message)


def load_record(path: Path = LINEAGE_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), "authority record root must be an object")
    return value


def _authority(record: Mapping[str, Any]) -> Mapping[str, Any]:
    value = record.get("authority")
    _require(isinstance(value, Mapping), "typed authority extension is missing")
    return value


def _entities(authority: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    rows = authority.get("entities")
    _require(isinstance(rows, list), "authority entities must be a list")
    result: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        _require(isinstance(row, Mapping), "authority entity must be an object")
        entity_id = row.get("entity_id")
        _require(isinstance(entity_id, str) and entity_id, "entity_id is missing")
        _require(entity_id not in result, f"duplicate authority entity: {entity_id}")
        result[entity_id] = row
    return result


def _relation_rows(authority: Mapping[str, Any]) -> Sequence[Mapping[str, Any]]:
    rows = authority.get("relations")
    _require(isinstance(rows, list), "authority relations must be a list")
    for row in rows:
        _require(isinstance(row, Mapping), "authority relation must be an object")
    return rows


def _relation_key(row: Mapping[str, Any]) -> tuple[object, object, object, object]:
    return (
        row.get("relation"),
        row.get("subject"),
        row.get("object"),
        row.get("scope"),
    )


def resolve_composed_frontier(record: Mapping[str, Any]) -> dict[str, object]:
    """Resolve only typed composition roles; never inspect PR order or time."""

    authority = _authority(record)
    entities = _entities(authority)
    composed = [
        row
        for row in entities.values()
        if row.get("kind") == "COMPOSED_AUTHORITY_STATE"
        and row.get("authority_status") == "AUTHORITATIVE_FRONTIER"
    ]
    _require(len(composed) == 1, "exactly one authoritative composed state is required")
    composed_row = composed[0]
    composed_id = str(composed_row["entity_id"])
    carrier_relations = [
        row
        for row in _relation_rows(authority)
        if row.get("relation") == "FRONTIER_CARRIER"
        and row.get("subject") == composed_id
    ]
    _require(len(carrier_relations) == 1, "composed state needs one typed carrier")
    carrier_id = carrier_relations[0].get("object")
    _require(isinstance(carrier_id, str) and carrier_id in entities, "carrier is unknown")
    members = composed_row.get("member_entity_ids")
    _require(isinstance(members, list), "composition members must be a list")
    _require(carrier_id in members, "frontier carrier must be a composition member")
    carrier = entities[carrier_id]
    _require(carrier.get("frontier_carrier") is True, "carrier role is not corroborated")
    _require(
        carrier.get("authority_status") == "AUTHORITATIVE_INHERITED",
        "superseded or non-authorizing entity cannot carry the frontier",
    )
    open_relations = [
        row
        for row in _relation_rows(authority)
        if row.get("relation") == "NEXT_OPEN_PROBLEM"
        and row.get("subject") == composed_id
    ]
    _require(len(open_relations) == 1, "composed state needs one next open problem")
    open_id = open_relations[0].get("object")
    _require(isinstance(open_id, str) and open_id in entities, "open problem is unknown")
    return {
        "composed_entity_id": composed_id,
        "composition_commit_sha": composed_row.get("commit_sha"),
        "carrier_entity_id": carrier_id,
        "carrier_branch": carrier.get("branch"),
        "carrier_scientific_head_sha": carrier.get("commit_sha"),
        "inherited_entity_ids": tuple(sorted(str(value) for value in members)),
        "open_problem_entity_id": open_id,
    }


def validate_record(record: Mapping[str, Any]) -> None:
    _require(record.get("schema_version") == "1.0", "lineage v1 compatibility drift")
    _require(record.get("package") == "C43B", "package identity drift")
    _require(
        record.get("canonical_id")
        == "UORC-056-LOCAL-GLV-SECTOR-FACTORIZATION-C43B",
        "canonical package identity drift",
    )
    _require(
        record.get("branch") == "research/uorc056-local-glv-gauge-breaking-c43",
        "carrier branch drift",
    )
    _require(
        record.get("parent_branch")
        == "research/uorc056-oriented-transposed-resultant-c42",
        "historical C43B parent must remain C42",
    )
    _require(record.get("successor") is None, "C44 must not be activated as a successor")
    _require(
        isinstance(record.get("status"), str) and "boundary" in record["status"],
        "lineage status must preserve the closed scientific boundary",
    )

    authority = _authority(record)
    _require(
        authority.get("schema_version") == "uorc056-composed-frontier-authority/v1",
        "composed authority schema drift",
    )
    entities = _entities(authority)
    _require(set(entities) == EXPECTED_ENTITY_IDS, "authority entity set is not exact")

    expected_heads = {
        C42_ENTITY: (C42, "AUTHORITATIVE_PARENT", 412),
        C43_ENTITY: (C43, "AUTHORITATIVE_INHERITED", 418),
        C43B_ENTITY: (C43B, "AUTHORITATIVE_INHERITED", 419),
    }
    for entity_id, (sha, status, pr_number) in expected_heads.items():
        row = entities[entity_id]
        _require(row.get("commit_sha") == sha and SHA_RE.fullmatch(sha), f"{entity_id} SHA drift")
        _require(row.get("authority_status") == status, f"{entity_id} authority drift")
        _require(row.get("advisory_pr_number") == pr_number, f"{entity_id} PR locator drift")

    _require(
        entities[PLANNED_ENTITY].get("planned_id") == "LOCAL-GLV-GAUGE-BREAKING-C43",
        "C42 planned route drift",
    )
    general_claims = entities[C43_ENTITY].get("claim_locators", [])
    local_claims = entities[C43B_ENTITY].get("claim_locators", [])
    _require(
        isinstance(general_claims, list)
        and len(general_claims) == len(GENERAL_CLAIMS)
        and set(general_claims) == GENERAL_CLAIMS,
        "C43 inherited claims are incomplete",
    )
    _require(
        isinstance(local_claims, list)
        and len(local_claims) == len(LOCAL_CLAIMS)
        and set(local_claims) == LOCAL_CLAIMS,
        "C43B inherited claims are incomplete",
    )
    _require(
        entities[C43_ENTITY].get("frontier_carrier") is False,
        "C43 framework cannot be the composed carrier",
    )
    _require(entities[C43B_ENTITY].get("frontier_carrier") is True, "C43B carrier role drift")

    relation_rows = _relation_rows(authority)
    relations = {_relation_key(row) for row in relation_rows}
    _require(
        len(relation_rows) == len(EXPECTED_RELATIONS)
        and relations == EXPECTED_RELATIONS,
        "typed authority relation set is not exact",
    )
    _require(
        not any(row.get("relation") == "SUPERSEDES" for row in _relation_rows(authority)),
        "neither C43 package supersedes the other",
    )
    _require(
        ("DECLARED_PARENT", C43B_ENTITY, C43_ENTITY, None) not in relations,
        "historical C43B parent cannot be rewritten to C43",
    )

    composition = entities[COMPOSED_ENTITY]
    _require(composition.get("commit_sha") == COMPOSITION, "composition SHA drift")
    _require(
        composition.get("member_entity_ids") == [C43_ENTITY, C43B_ENTITY],
        "composition must inherit exactly C43 and C43B",
    )
    _require(
        composition.get("frontier_carrier_entity_id") == C43B_ENTITY,
        "composition carrier field drift",
    )
    projection = resolve_composed_frontier(record)
    _require(
        projection["carrier_entity_id"] == C43B_ENTITY,
        "typed resolver selected the wrong carrier",
    )

    open_problem = entities[OPEN_ENTITY]
    _require(
        open_problem.get("planned_id") == "ORDERED-SECTOR-TRANSPORT-C44",
        "C44 planned ID drift",
    )
    _require(
        open_problem.get("target") == "public unsquared evaluator for J_G(x(Q))",
        "C44 target drift",
    )
    open_gates = open_problem.get("gates", [])
    _require(
        isinstance(open_gates, list)
        and len(open_gates) == len(OPEN_GATES)
        and set(open_gates) == OPEN_GATES,
        "C44 gates drift",
    )
    _require(
        open_problem.get("implementation_authorized") is False,
        "C44 implementation became authorized",
    )
    _require(open_problem.get("implementation_branch") is None, "C44 branch must remain unbound")
    _require(open_problem.get("implementation_commit_sha") is None, "C44 SHA must remain unbound")

    excluded = entities[EXCLUDED_ENTITY]
    _require(excluded.get("commit_sha") == UNRELATED_C43, "unrelated C43 exclusion SHA drift")
    _require(
        str(excluded.get("authority_status", "")).startswith("NON_AUTHORIZING"),
        "unrelated C43 became authorizing",
    )

    git_composition = authority.get("git_composition")
    _require(isinstance(git_composition, Mapping), "Git composition record is missing")
    _require(git_composition.get("merge_commit_sha") == COMPOSITION, "Git merge binding drift")
    _require(git_composition.get("ordered_parent_shas") == [C43B, C43], "merge parent order drift")
    _require(git_composition.get("common_parent_sha") == C42, "sibling base SHA drift")

    bindings = authority.get("source_bindings")
    _require(isinstance(bindings, list), "source bindings must be a list")
    _require(
        all(isinstance(row, Mapping) for row in bindings),
        "source binding must be an object",
    )
    binding_keys = {
        (row.get("entity_id"), row.get("commit_sha"), row.get("path"), row.get("blob_sha"))
        for row in bindings
    }
    _require(
        len(bindings) == len(EXPECTED_BINDINGS)
        and binding_keys == EXPECTED_BINDINGS,
        "source/blob provenance set is not exact",
    )

    disposition = authority.get("integration_disposition")
    _require(isinstance(disposition, Mapping), "integration disposition is missing")
    _require(disposition.get("package_entity_id") == C43_ENTITY, "integration target drift")
    _require(disposition.get("status") == "INTEGRATED_NOT_SUPERSEDED", "C43 disposition drift")
    _require(
        disposition.get("retain_branch_and_exact_provenance") is True,
        "C43 provenance retention drift",
    )


def _git(
    repo_root: Path,
    *args: str,
    allowed: tuple[int, ...] = (0,),
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode not in allowed:
        raise AuthorityError(
            f"git {' '.join(args)} failed ({result.returncode}): {result.stderr.strip()}"
        )
    return result


def _is_ancestor(repo_root: Path, ancestor: str, descendant: str) -> bool:
    return _git(
        repo_root,
        "merge-base",
        "--is-ancestor",
        ancestor,
        descendant,
        allowed=(0, 1),
    ).returncode == 0


def validate_git(record: Mapping[str, Any], repo_root: Path = REPO_ROOT) -> None:
    validate_record(record)
    for sha in (C42, C43, C43B, COMPOSITION):
        _git(repo_root, "cat-file", "-e", f"{sha}^{{commit}}")

    merge_base = _git(repo_root, "merge-base", C43, C43B).stdout.strip()
    _require(merge_base == C42, "C43/C43B merge base is not the exact C42 head")
    _require(_is_ancestor(repo_root, C42, C43), "C42 is not an ancestor of C43")
    _require(_is_ancestor(repo_root, C42, C43B), "C42 is not an ancestor of C43B")
    _require(not _is_ancestor(repo_root, C43, C43B), "original C43 unexpectedly parents C43B")
    _require(not _is_ancestor(repo_root, C43B, C43), "original C43B unexpectedly parents C43")

    parents = _git(repo_root, "show", "-s", "--format=%P", COMPOSITION).stdout.strip().split()
    _require(parents == [C43B, C43], "composition commit does not have the exact ordered parents")
    _require(_is_ancestor(repo_root, C43, COMPOSITION), "composition does not inherit C43")
    _require(_is_ancestor(repo_root, C43B, COMPOSITION), "composition does not inherit C43B")
    head = _git(repo_root, "rev-parse", "HEAD").stdout.strip()
    _require(
        _is_ancestor(repo_root, COMPOSITION, head),
        "composition commit was lost by squash or rebase",
    )

    for _, commit_sha, path, blob_sha in EXPECTED_BINDINGS:
        actual = _git(repo_root, "rev-parse", f"{commit_sha}:{path}").stdout.strip()
        _require(actual == blob_sha, f"pinned source blob drift: {path}@{commit_sha}")
        current = _git(repo_root, "rev-parse", f"HEAD:{path}").stdout.strip()
        _require(current == blob_sha, f"composed tree does not retain exact source: {path}")

    unrelated_exists = _git(
        repo_root,
        "cat-file",
        "-e",
        f"{UNRELATED_C43}^{{commit}}",
        allowed=(0, 1, 128),
    ).returncode == 0
    if unrelated_exists:
        _require(
            not _is_ancestor(repo_root, UNRELATED_C43, COMPOSITION),
            "unrelated C43 branch entered the composed frontier",
        )


def main() -> int:
    try:
        record = load_record()
        validate_git(record)
    except (AuthorityError, json.JSONDecodeError, OSError) as error:
        print(f"C43 composed authority check failed: {error}", file=sys.stderr)
        return 1
    projection = resolve_composed_frontier(record)
    print(
        "C43 composed authority check passed: "
        f"{projection['carrier_branch']} carries both exact C43 packages; "
        "ORDERED-SECTOR-TRANSPORT-C44 remains open and unauthorized"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
