#!/usr/bin/env python3
"""Independent validator for the TASK-023 exact chart-cover certificate."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ARTIFACT_PATH = HERE / "artifact.json"
SIDECAR_PATH = HERE / "artifact.sha256"

ARTIFACT_ID = "PKC-SMOOTH-M16-EXACT-CHART-COVER-001"
ARTIFACT_KIND = "source_bound_non_run_certificate"
SOURCE_PATH = "Ecdlp/Proved/FrozenProjectiveChartSystem.lean"
SOURCE_SHA256 = (
    "4f7b95453d8fafba3ec9cae0a9bbad5d8f782c6c0202f6e7cf37e17981b63019"
)

TASK022_ARTIFACT_PATH = (
    "experiments/engine/pkc_smooth_m16_guarded_projective_system/artifact.json"
)
TASK022_ARTIFACT_SHA256 = (
    "3445da55b44a71d0f40ee60206c90f2ef1798c28abd125542ce3acbeeb8e1d46"
)
TASK022_SOURCE_PATH = "Ecdlp/Proved/FrozenProjectiveGuardSystem.lean"
TASK022_SOURCE_SHA256 = (
    "37feeef48e77437b44b6ae6dd4750782e19ecd824e3ea2e73b657e2fb8296fb9"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "artifact_id",
    "binding_state",
    "chart_cover_contract",
    "degree_fixture",
    "depends_on",
    "downstream_open_boundary",
    "exactness_contract",
    "finite_field_fixture",
    "kind",
    "producer_checks",
    "proof_status",
    "schema_version",
    "scope",
    "terminal_disposition",
    "theorem_bindings",
}

EXPECTED_BINDING = {
    "artifact_sidecar": "artifact.sha256",
    "digest_match": True,
    "source_path": SOURCE_PATH,
    "source_sha256": SOURCE_SHA256,
    "source_status": "final",
}

EXPECTED_CHART_CONTRACT = {
    "affine_chart_representative": "[X_i:1]",
    "equation_families": {
        "base": {"count": 1, "degree_upper_bound": 2},
        "final": {"count": 1, "degree_upper_bound": 2},
        "guard": {"count": 0},
        "step": {"count": 13, "degree_upper_bound": 4},
    },
    "exact_total_degree_claimed": False,
    "fixed_mask_variable_count_formula": "14 - I.card",
    "fixed_mask_variable_count_range": [0, 14],
    "fixed_mask_variable_index_type": "{i : Fin 14 // i notin I}",
    "infinity_chart_representative": "[1:0]",
    "infinity_mask_type": "Finset (Fin 14)",
    "leaf_count": 16,
    "logical_mask_count": 16384,
    "logical_mask_count_formula": "2^14",
    "mask_membership_semantics": (
        "i in I iff slot i is represented by [1:0]"
    ),
    "overall_degree_upper_bound": 4,
    "production_mask_enumeration_required": False,
    "production_mask_materialized": False,
    "projective_slot_count": 14,
    "stage": 14,
    "total_equation_count_per_fixed_mask": 15,
    "variables_per_affine_slot": 1,
    "variables_per_infinity_slot": 0,
}

EXPECTED_EXACTNESS = {
    "cover_quantifier": (
        "exists I : Finset (Fin 14), exists x : ChartVar I -> K, "
        "FrozenChartPolynomialSystem q y I x"
    ),
    "equivalence_direction": "iff",
    "guarded_system_bridge": (
        "FrozenGuardedProjectiveSystem q y iff "
        "FrozenChartPolynomialCover q y"
    ),
    "infinity_representative": [1, 0],
    "infinity_retained": True,
    "prior_chain": "FrozenProjectiveChain q 14 y",
    "projective_zero_pair_admitted": False,
    "representative_partition": (
        "every valid projective slot is uniquely either [1:0] or [X:1]"
    ),
    "target_statement": (
        "FrozenProjectiveChain q 14 y iff FrozenChartPolynomialCover q y"
    ),
}

EXPECTED_FIXTURE = {
    "affine_projective_point_count": 5,
    "distinguished_infinity_pair": [1, 0],
    "field_prime": 5,
    "infinity_projective_point_count": 1,
    "mask_cardinality_chain_distribution": {
        "0": 125,
        "1": 75,
        "2": 15,
        "3": 1,
    },
    "normalized_chain_count": 216,
    "observed_reduced_mask_count": 8,
    "per_fixed_mask_chain_count_formula": "5^(3-|I|)",
    "production_mask_enumeration_executed": False,
    "projective_point_count": 6,
    "raw_nonzero_pair_count": 24,
    "reduced_chain_slot_count": 3,
    "reduced_mask_count_formula": "2^3",
    "sample_production_variable_counts": {
        "I.card=0": 14,
        "I.card=1": 13,
        "I.card=14": 0,
        "I.card=3": 11,
    },
    "scalar_multiples_per_projective_point": 4,
    "zero_pair_rejected": True,
}

EXPECTED_DEGREE_FIXTURE = {
    "constant_pair_coordinate_degree": 0,
    "derived_family_degree_ceilings": {
        "base": 2,
        "final": 2,
        "step": 4,
    },
    "h_argument_multidegree": [2, 2, 2],
    "literal_h_monomial_count": 9,
    "variable_pair_coordinate_degree_upper_bound": 1,
    "variable_pair_positions": {
        "base": [2],
        "final": [0],
        "step": [0, 2],
    },
}

EXPECTED_PRODUCER = {
    "chart_cover_lean_source_materialized": True,
    "discrete_log_executed": False,
    "exact_target_search_executed": False,
    "experiment_authorized": False,
    "full_production_mask_family_enumerated": False,
    "full_production_mask_family_materialized": False,
    "parameter_sweep_executed": False,
    "rank_estimated": False,
    "relation_yield_estimated": False,
    "solver_input_emitted": False,
    "solver_executed": False,
}

EXPECTED_PROOF_STATUS = {
    "card_chartEquation": "compiler_trusted_native_decide",
    "card_chartVar": "kernel_checked",
    "chartPolynomialEquation_base_totalDegree_le_two": "kernel_checked",
    "chartPolynomialEquation_final_totalDegree_le_two": "kernel_checked",
    "chartPolynomialEquation_step_totalDegree_le_four": "kernel_checked",
    "chartPolynomialEquation_totalDegree_le_four": "kernel_checked",
    "expanded_S17_polynomial": "not_claimed",
    "frozenGuardedProjectiveSystem_iff_chartPolynomialCover":
        "kernel_checked",
    "frozenProjectiveChain_iff_chartPolynomialCover": "kernel_checked",
    "frozenRecS17_iff_chartPolynomialCover_over": "kernel_checked",
    "mask_enumeration_theorem": "not_required",
    "solving_rank_yield_cost_claim": "not_claimed",
}

EXPECTED_SCOPE = {
    "barrier": "B-PKC-M16-COMPLETE-COST-BRIDGE",
    "cell": "CELL-M-PKC-SMOOTH-M16",
    "cost_quantity": "CQ-SEMAEV-S17-SYSTEM-COST",
    "excluded": [
        "enumerating or materializing all 16384 production masks",
        "solver, rank, yield, recovery, cost, or parameter-sweep work",
        "base-field descent or witness rationality",
        "experiment authorization, retention, promotion, or rejection",
    ],
    "included": [
        "exact infinity-mask decomposition of fourteen projective slots",
        "fourteen minus mask cardinality variables for each fixed mask",
        "exactly fifteen H equations per fixed mask",
        "base, step, and final degree ceilings two, four, and two",
        "exact equivalence to the prior projective chain and guarded system",
        "retention of the distinguished infinity representative [1:0]",
        "independent reduced F5 chart-cover fixture",
    ],
    "task": "TASK-023",
}

EXPECTED_TERMINAL = {
    "assurance": "kernel_bound_non_run_certificate",
    "authorization": "none",
    "barrier_effect": "chart_guard_redundancy_removed_only_complete_cost_barrier_still_open",
    "cell_status": "open_non_executable",
    "cost_quantity_status": "partial",
    "experiment_permission": "none",
    "hypothesis_effect": "none",
    "rank_status": "unpriced",
    "representation_status": "exact_chart_polynomial_cover_closed",
    "retention_disposition": "zero_retention_success",
    "route_effect": "none",
    "route_status": "open_parked",
    "solving_cost_status": "unpriced",
    "yield_status": "unpriced",
}

EXPECTED_CLOSED_HERE = [
    "each infinity mask I gives a literal chart-polynomial system with "
    "14-I.card scalar variables",
    "each fixed-mask system has one base, thirteen step, and one final H "
    "equation",
    "the family-specific total-degree ceilings are base two, step four, "
    "and final two",
    "the existential cover over infinity masks is exactly equivalent to "
    "FrozenProjectiveChain at stage 14",
    "the chart cover retains the infinity representative [1:0]",
    "the chart cover is equivalent to the prior guarded system",
    "the injective coefficient-map bridge from frozen RecS17 reaches the "
    "exact chart cover",
]

EXPECTED_NOT_CLAIMED = [
    "enumeration or materialization of all 16384 production masks",
    "base-field descent or rationality of intermediate witnesses",
    "independence, relation yield, rank, solving degree, fill-in, memory, "
    "recovery, or total cost",
    "a solver run, parameter sweep, exact-target search, or discrete-log "
    "execution",
    "experiment authorization, hypothesis retention, route promotion, "
    "or route rejection",
]

EXPECTED_REMAINING_BLOCKER = (
    "after the chart-cover proof, any solver-facing use still requires a "
    "separately authorized design for mask selection, relation yield and "
    "rank, solving, recovery, and complete cost"
)

EXPECTED_THEOREMS = {
    "card_chartEquation": (
        "Ecdlp.FrozenProjectiveSemaev.card_chartEquation",
        "theorem",
        "compiler_trusted_native_decide",
    ),
    "card_chartVar": (
        "Ecdlp.FrozenProjectiveSemaev.card_chartVar",
        "theorem",
        "kernel_checked",
    ),
    "chartPolynomialEquation_base_totalDegree_le_two": (
        "Ecdlp.FrozenProjectiveSemaev."
        "chartPolynomialEquation_base_totalDegree_le_two",
        "theorem",
        "kernel_checked",
    ),
    "chartPolynomialEquation_final_totalDegree_le_two": (
        "Ecdlp.FrozenProjectiveSemaev."
        "chartPolynomialEquation_final_totalDegree_le_two",
        "theorem",
        "kernel_checked",
    ),
    "chartPolynomialEquation_step_totalDegree_le_four": (
        "Ecdlp.FrozenProjectiveSemaev."
        "chartPolynomialEquation_step_totalDegree_le_four",
        "theorem",
        "kernel_checked",
    ),
    "chartPolynomialEquation_totalDegree_le_four": (
        "Ecdlp.FrozenProjectiveSemaev."
        "chartPolynomialEquation_totalDegree_le_four",
        "theorem",
        "kernel_checked",
    ),
    "frozenGuardedProjectiveSystem_iff_chartPolynomialCover": (
        "Ecdlp.FrozenProjectiveSemaev."
        "frozenGuardedProjectiveSystem_iff_chartPolynomialCover",
        "theorem",
        "kernel_checked",
    ),
    "frozenProjectiveChain_iff_chartPolynomialCover": (
        "Ecdlp.FrozenProjectiveSemaev."
        "frozenProjectiveChain_iff_chartPolynomialCover",
        "theorem",
        "kernel_checked",
    ),
    "frozenRecS17_iff_chartPolynomialCover_over": (
        "Ecdlp.FrozenProjectiveSemaev."
        "frozenRecS17_iff_chartPolynomialCover_over",
        "theorem",
        "kernel_checked",
    ),
}

# Literal coordinate exponents of the nine HValue monomials. Each entry has
# ((q1.u, q1.v), (q2.u, q2.v), (q3.u, q3.v)).
H_MONOMIAL_EXPONENTS = (
    ((2, 0), (2, 0), (0, 2)),
    ((2, 0), (0, 2), (2, 0)),
    ((0, 2), (2, 0), (2, 0)),
    ((2, 0), (1, 1), (1, 1)),
    ((1, 1), (2, 0), (1, 1)),
    ((1, 1), (1, 1), (2, 0)),
    ((1, 1), (0, 2), (0, 2)),
    ((0, 2), (1, 1), (0, 2)),
    ((0, 2), (0, 2), (1, 1)),
)


class ValidationError(RuntimeError):
    """Raised when the certificate contract or a fixture drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and re.fullmatch(r"[0-9a-f]{64}", value) is not None
    )


def discover_repo_root(explicit: Path | None = None) -> Path:
    """Find the repository without using network access or Git metadata."""
    starts = [explicit] if explicit is not None else [Path.cwd(), HERE]
    seen: set[Path] = set()
    for start in starts:
        if start is None:
            continue
        resolved = start.resolve()
        for candidate in (resolved, *resolved.parents):
            if candidate in seen:
                continue
            seen.add(candidate)
            if (
                (candidate / "Ecdlp.lean").is_file()
                and (candidate / TASK022_SOURCE_PATH).is_file()
                and (candidate / TASK022_ARTIFACT_PATH).is_file()
            ):
                return candidate
    raise ValidationError(
        "repository root not found; pass --repo-root"
    )


def normalize_projective_pair(
    u: int, v: int, prime: int = 5
) -> tuple[int, int]:
    u %= prime
    v %= prime
    require((u, v) != (0, 0), "[0:0] has no projective normalization")
    if v == 0:
        return (1, 0)
    return ((u * pow(v, -1, prime)) % prime, 1)


def chart_encode(
    point: tuple[int, int], prime: int = 5
) -> tuple[str, int | None]:
    normalized = normalize_projective_pair(*point, prime)
    if normalized == (1, 0):
        return ("infinity", None)
    return ("affine", normalized[0])


def chart_decode(
    chart: tuple[str, int | None], prime: int = 5
) -> tuple[int, int]:
    tag, coordinate = chart
    if tag == "infinity":
        require(coordinate is None, "infinity chart must have no variable")
        return (1, 0)
    require(tag == "affine", "unknown chart tag")
    require(isinstance(coordinate, int), "affine chart needs one scalar")
    return (coordinate % prime, 1)


def enumerate_f5_reduced_chart_fixture() -> dict[str, Any]:
    """Exhaust a 3-slot F5 fixture, never the 14-slot production mask set."""
    prime = 5
    raw_pairs = [
        (u, v)
        for u, v in itertools.product(range(prime), repeat=2)
        if (u, v) != (0, 0)
    ]
    fibers: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    for raw in raw_pairs:
        fibers[normalize_projective_pair(*raw, prime)].append(raw)

    projective_points = sorted(fibers)
    for point in projective_points:
        require(
            chart_decode(chart_encode(point, prime), prime) == point,
            "chart encode/decode is not inverse on normalized F5 points",
        )

    mask_counts: Counter[tuple[int, ...]] = Counter()
    for chain in itertools.product(projective_points, repeat=3):
        mask = tuple(
            index for index, point in enumerate(chain) if point == (1, 0)
        )
        mask_counts[mask] += 1

    cardinality_distribution: Counter[int] = Counter()
    for mask, count in mask_counts.items():
        expected_per_mask = prime ** (3 - len(mask))
        require(
            count == expected_per_mask,
            "reduced fixture violates 5^(3-|I|) per-mask count",
        )
        cardinality_distribution[len(mask)] += count

    return {
        "raw_nonzero_pairs": len(raw_pairs),
        "projective_points": len(projective_points),
        "fiber_sizes": set(map(len, fibers.values())),
        "affine_points": sum(point[1] == 1 for point in projective_points),
        "infinity_points": sum(
            point == (1, 0) for point in projective_points
        ),
        "zero_rejected": (0, 0) not in fibers,
        "chain_count": sum(mask_counts.values()),
        "mask_count": len(mask_counts),
        "mask_cardinality_distribution": dict(
            sorted(cardinality_distribution.items())
        ),
        "infinity_chart": chart_encode((1, 0), prime),
        "production_masks_enumerated": False,
    }


def production_variable_count_samples() -> dict[str, int]:
    """Check cardinality arithmetic only, with no powerset enumeration."""
    counts = {cardinality: 14 - cardinality for cardinality in range(15)}
    require(all(0 <= value <= 14 for value in counts.values()),
            "production chart-variable count left [0,14]")
    return {
        "I.card=0": counts[0],
        "I.card=1": counts[1],
        "I.card=3": counts[3],
        "I.card=14": counts[14],
    }


def _h_term_degree(
    exponents: tuple[tuple[int, int], ...],
    pair_kinds: tuple[str, str, str],
) -> int | None:
    degree = 0
    for (u_exponent, v_exponent), kind in zip(exponents, pair_kinds):
        if kind == "infinity":
            if v_exponent > 0:
                return None
        elif kind == "affine":
            degree += u_exponent
        else:
            require(kind == "constant", "unknown H argument kind")
    return degree


def _family_degree_ceiling(variable_positions: Iterable[int]) -> int:
    positions = tuple(variable_positions)
    observed: list[int] = []
    for choices in itertools.product(("affine", "infinity"),
                                     repeat=len(positions)):
        kinds = ["constant", "constant", "constant"]
        for position, choice in zip(positions, choices):
            kinds[position] = choice
        term_degrees = [
            degree
            for exponents in H_MONOMIAL_EXPONENTS
            if (degree := _h_term_degree(exponents, tuple(kinds)))
            is not None
        ]
        require(term_degrees, "a chart pattern erased every H monomial")
        observed.append(max(term_degrees))
    return max(observed)


def derive_literal_h_degree_fixture() -> dict[str, Any]:
    positions = {"base": (2,), "step": (0, 2), "final": (0,)}
    return {
        "literal_h_monomials": len(H_MONOMIAL_EXPONENTS),
        "argument_multidegrees": [
            max(u + v for term in H_MONOMIAL_EXPONENTS
                for u, v in [term[index]])
            for index in range(3)
        ],
        "family_ceilings": {
            name: _family_degree_ceiling(variable_positions)
            for name, variable_positions in positions.items()
        },
    }


def validate_dependencies(document: dict[str, Any], repo_root: Path) -> None:
    dependencies = document.get("depends_on")
    require(isinstance(dependencies, list), "depends_on must be a list")
    require(len(dependencies) == 3, "dependency count drift")

    expected_final = (
        (TASK022_ARTIFACT_PATH, TASK022_ARTIFACT_SHA256),
        (TASK022_SOURCE_PATH, TASK022_SOURCE_SHA256),
        (SOURCE_PATH, SOURCE_SHA256),
    )
    for item, (expected_path, expected_digest) in zip(
        dependencies, expected_final
    ):
        require(
            item == {
                "binding_status": "final",
                "digest_match": True,
                "observed_sha256": expected_digest,
                "path": expected_path,
                "required_sha256": expected_digest,
            },
            f"final dependency metadata drift for {expected_path}",
        )
        require(
            sha256(repo_root / expected_path) == expected_digest,
            f"repository digest mismatch for {expected_path}",
        )

def validate_fixture_metadata_and_observation(document: dict[str, Any]) -> None:
    require(
        document.get("finite_field_fixture") == EXPECTED_FIXTURE,
        "finite-field fixture metadata drift",
    )
    observed = enumerate_f5_reduced_chart_fixture()
    require(observed["raw_nonzero_pairs"] == 24,
            "F5 raw nonzero pair count is not 24")
    require(observed["projective_points"] == 6,
            "F5 projective point count is not 6")
    require(observed["fiber_sizes"] == {4},
            "F5 projective classes do not all have four representatives")
    require(observed["affine_points"] == 5,
            "F5 affine chart does not have five points")
    require(observed["infinity_points"] == 1,
            "F5 infinity chart is not a singleton")
    require(observed["zero_rejected"] is True,
            "F5 chart fixture admitted [0:0]")
    require(observed["chain_count"] == 216,
            "three-slot F5 chain count is not 216")
    require(observed["mask_count"] == 8,
            "three-slot F5 fixture did not observe eight masks")
    require(
        observed["mask_cardinality_distribution"]
        == {0: 125, 1: 75, 2: 15, 3: 1},
        "three-slot F5 mask-cardinality distribution drift",
    )
    require(observed["infinity_chart"] == ("infinity", None),
            "[1:0] was not retained as the variable-free chart")
    require(observed["production_masks_enumerated"] is False,
            "production mask family was unexpectedly enumerated")
    require(
        production_variable_count_samples()
        == EXPECTED_FIXTURE["sample_production_variable_counts"],
        "production variable-count arithmetic drift",
    )


def validate_degree_fixture(document: dict[str, Any]) -> None:
    require(
        document.get("degree_fixture") == EXPECTED_DEGREE_FIXTURE,
        "degree-fixture metadata drift",
    )
    observed = derive_literal_h_degree_fixture()
    require(observed["literal_h_monomials"] == 9,
            "literal H fixture no longer has nine monomials")
    require(observed["argument_multidegrees"] == [2, 2, 2],
            "literal H fixture is not triquadratic")
    require(
        observed["family_ceilings"]
        == {"base": 2, "step": 4, "final": 2},
        "chart-substituted H degree ceilings are not 2/4/2",
    )


def validate_theorem_bindings(document: dict[str, Any]) -> None:
    bindings = document.get("theorem_bindings")
    require(isinstance(bindings, dict), "theorem_bindings must be an object")
    require(set(bindings) == set(EXPECTED_THEOREMS),
            "theorem-binding key drift")
    for key, (declaration, source_shape, kernel_status) in (
        EXPECTED_THEOREMS.items()
    ):
        require(
            bindings[key] == {
                "declaration": declaration,
                "kernel_status": kernel_status,
                "source_path": SOURCE_PATH,
                "source_shape": source_shape,
            },
            f"theorem binding drift for {key}",
        )


def validate_source_contract(repo_root: Path) -> None:
    source_path = repo_root / SOURCE_PATH
    require(sha256(source_path) == SOURCE_SHA256,
            "TASK-023 source digest changed")
    source_text = source_path.read_text(encoding="utf-8")
    forbidden = re.compile(r"\b(?:sorry|admit|axiom|unsafe)\b")
    require(forbidden.search(source_text) is None,
            "forbidden Lean trust token in TASK-023 source")
    required_fragments = (
        "import Ecdlp.Proved.FrozenProjectiveGuardSystem",
        "abbrev InfinityMask := Finset (Fin 14)",
        "abbrev ChartVar (I : InfinityMask) := {i : Fin 14 // i ∉ I}",
        "inductive ChartEquation",
        "noncomputable def chartPolynomialEquation",
        "def FrozenChartPolynomialSystem",
        "MvPolynomial.eval x (chartPolynomialEquation q y I e) = 0",
        "def FrozenChartPolynomialCover",
        "∃ (I : InfinityMask) (x : ChartVar I → K),",
    )
    for fragment in required_fragments:
        require(fragment in source_text,
                f"required source fragment missing: {fragment}")
    require(
        len(re.findall(r"^\s*native_decide\s*$", source_text,
                       flags=re.MULTILINE)) == 1,
        "native_decide proof-command count is not exactly one",
    )
    for declaration, source_shape, _status in EXPECTED_THEOREMS.values():
        short_name = declaration.rsplit(".", 1)[-1]
        require(
            re.search(
                rf"^(?:noncomputable )?{re.escape(source_shape)} "
                rf"{re.escape(short_name)}\b",
                source_text,
                flags=re.MULTILINE,
            ) is not None,
            f"declaration {short_name} absent from digest-bound source",
        )


def validate_boundary(document: dict[str, Any]) -> None:
    boundary = document.get("downstream_open_boundary")
    require(isinstance(boundary, dict),
            "downstream_open_boundary must be an object")
    require(
        set(boundary)
        == {"closed_here", "not_claimed", "remaining_blocker"},
        "downstream boundary field drift",
    )
    require(
        boundary.get("closed_here") == EXPECTED_CLOSED_HERE,
        "closed-here contract drift",
    )
    require(boundary.get("not_claimed") == EXPECTED_NOT_CLAIMED,
            "not-claimed boundary drift")
    require(
        boundary.get("remaining_blocker") == EXPECTED_REMAINING_BLOCKER,
        "remaining blocker drift",
    )


def validate_document(
    document: dict[str, Any],
    *,
    repo_root: Path | None = None,
    verify_dependency_files: bool = False,
    require_final_source_binding: bool = False,
) -> None:
    require(set(document) == EXPECTED_TOP_LEVEL_KEYS,
            "top-level certificate field drift")
    require(document.get("artifact_id") == ARTIFACT_ID,
            "artifact id drift")
    require(document.get("schema_version") == 1,
            "schema version drift")
    require(document.get("kind") == ARTIFACT_KIND,
            "artifact kind drift")
    require(document.get("binding_state") == EXPECTED_BINDING,
            "final source-binding state drift")
    require(is_sha256(document["binding_state"]["source_sha256"]),
            "final source digest is malformed")
    if require_final_source_binding:
        require(
            document["binding_state"]["source_status"] == "final"
            and document["binding_state"]["digest_match"] is True,
            "final-source binding is not asserted",
        )

    require(
        document.get("chart_cover_contract") == EXPECTED_CHART_CONTRACT,
        "chart-cover contract drift",
    )
    families = document["chart_cover_contract"]["equation_families"]
    require(
        sum(family["count"] for family in families.values()) == 15,
        "fixed-mask equation inventory does not total 15",
    )
    require(
        document["chart_cover_contract"]["logical_mask_count"] == 2 ** 14,
        "logical mask count is not 2^14",
    )
    require(
        document["chart_cover_contract"][
            "production_mask_enumeration_required"
        ] is False,
        "production mask enumeration was made a requirement",
    )
    require(
        document["chart_cover_contract"]["production_mask_materialized"]
        is False,
        "production mask family was marked materialized",
    )
    require(document.get("exactness_contract") == EXPECTED_EXACTNESS,
            "exactness contract drift")
    require(document.get("producer_checks") == EXPECTED_PRODUCER,
            "non-run producer contract drift")
    require(document.get("proof_status") == EXPECTED_PROOF_STATUS,
            "proof-status contract drift")
    require(document.get("scope") == EXPECTED_SCOPE,
            "scope drift")
    require(document.get("terminal_disposition") == EXPECTED_TERMINAL,
            "terminal nonauthorization contract drift")

    validate_fixture_metadata_and_observation(document)
    validate_degree_fixture(document)
    validate_theorem_bindings(document)
    validate_boundary(document)

    if verify_dependency_files:
        require(repo_root is not None,
                "repo_root is required for dependency verification")
        validate_dependencies(document, repo_root)
        validate_source_contract(repo_root)
    else:
        # Metadata is still checked even when mutation tests avoid filesystem
        # coupling.
        dependencies = document.get("depends_on")
        require(isinstance(dependencies, list),
                "depends_on must be a list")
        require(len(dependencies) == 3, "dependency count drift")
        expected_metadata = (
            (TASK022_ARTIFACT_PATH, TASK022_ARTIFACT_SHA256),
            (TASK022_SOURCE_PATH, TASK022_SOURCE_SHA256),
            (SOURCE_PATH, SOURCE_SHA256),
        )
        for item, (path, digest) in zip(
            dependencies, expected_metadata
        ):
            require(
                item == {
                    "binding_status": "final",
                    "digest_match": True,
                    "observed_sha256": digest,
                    "path": path,
                    "required_sha256": digest,
                },
                f"dependency metadata drift for {path}",
            )


def validate_artifact_sidecar() -> None:
    expected = f"{sha256(ARTIFACT_PATH)}  artifact.json\n"
    require(
        SIDECAR_PATH.read_text(encoding="utf-8") == expected,
        "artifact.sha256 drift",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, default=ARTIFACT_PATH)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument(
        "--require-final-source-binding",
        action="store_true",
        help="require the finalized TASK-023 Lean file and SHA-256 binding",
    )
    args = parser.parse_args()
    try:
        repo_root = discover_repo_root(args.repo_root)
        document = json.loads(args.artifact.read_text(encoding="utf-8"))
        validate_document(
            document,
            repo_root=repo_root,
            verify_dependency_files=True,
            require_final_source_binding=args.require_final_source_binding,
        )
        if args.artifact.resolve() == ARTIFACT_PATH.resolve():
            validate_artifact_sidecar()
    except (OSError, json.JSONDecodeError, ValidationError) as error:
        print(f"TASK-023 chart-cover validation failed: {error}",
              file=sys.stderr)
        return 1

    print("TASK-023 exact chart-cover certificate PASSED")
    print(
        "fixed mask: variables=14-I.card equations=15 "
        "degree_ceilings=2/4/2"
    )
    print(
        "F5 reduced fixture: P1_points=6 raw_pairs=24 "
        "three_slot_chains=216 masks=8; [1:0] retained"
    )
    print(
        "production 2^14 mask family was neither enumerated nor "
        "materialized"
    )
    print(
        f"SOURCE_SHA256={SOURCE_SHA256}; solver, rank, yield, cost, "
        "authorization, retention, and promotion remain absent"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
