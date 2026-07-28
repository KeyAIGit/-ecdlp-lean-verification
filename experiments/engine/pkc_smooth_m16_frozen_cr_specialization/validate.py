#!/usr/bin/env python3
"""Independently validate the TASK-020 frozen-Cr kernel certificate.

This standard-library-only validator imports neither Lean nor repository
mathematical helpers. It binds declaration names to exact source digests,
reconstructs the complete C2-C16 degree schedule, evaluates the literal
nine-term H form, and replays small fixed-degree Sylvester controls.
"""

from __future__ import annotations

import argparse
import hashlib
from itertools import permutations
import json
from pathlib import Path
import re
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
ARTIFACT_PATH = HERE / "artifact.json"
HASH_PATH = HERE / "artifact.sha256"

ARTIFACT_ID = "PKC-SMOOTH-M16-FROZEN-CR-SPECIALIZATION-001"
ARTIFACT_KIND = "non_run_kernel_binding_certificate"
FROZEN_PATH = "Ecdlp/Proved/FrozenRecursiveProjectiveSemaev.lean"
SYLVESTER_PATH = "Ecdlp/Proved/TaskSylvesterConvention.lean"
TASK018_PATH = (
    "experiments/engine/pkc_smooth_m16_projective_bridge/artifact.json"
)
TASK019_PATH = (
    "experiments/engine/"
    "pkc_smooth_m16_projective_resultant_kernel/artifact.json"
)
EXPECTED_DEPENDENCIES = (
    TASK018_PATH,
    TASK019_PATH,
    FROZEN_PATH,
    SYLVESTER_PATH,
)

EXPECTED_ASSUMPTIONS = {
    "affine_output": "[y:1] is an explicit specialization corollary",
    "coefficient_map": (
        "the source is a CommRing k and the named coefficient map is an "
        "explicit ring homomorphism k ->+* K"
    ),
    "common_root_target": (
        "the unconditional common-projective-root equivalence uses a "
        "Field K with IsAlgClosed K"
    ),
    "degree_bound_target": (
        "the universal output-slice degree bound uses a Field K after any "
        "coefficient map from a CommRing k"
    ),
    "infinity_output": (
        "[1:0] is an explicit specialization corollary and is not reduced "
        "to an affine chart"
    ),
    "normalization": (
        "fixed formal degrees and leading zero coefficients are retained; "
        "no primitive, content, monic, sign, actual-degree, or "
        "variable-dependent normalization"
    ),
    "projective_domain": (
        "every ProjectivePair satisfies u!=0 or v!=0; only [0:0] is "
        "excluded"
    ),
    "zero_forms_and_degree_drops": (
        "included by the fixed-degree resultant interface"
    ),
}

EXPECTED_FAMILY = {
    "C16_binding": "frozenC R 14 = C16",
    "argument_order": "H(T,Q_(s+3),Y) is the right operand",
    "base": "frozenC R 0 = C2(Q1,Q2;Y) = H(Q1,Q2,Y)",
    "coefficient_unit": 1,
    "family_index": "frozenC R s = C_(s+2)",
    "formal_degrees": ["2^(s+1)", "2"],
    "left_operand": "outputSlice(frozenC R s)",
    "normalization": "none",
    "output_branches": ["[y:1]", "[1:0]"],
    "right_operand": "localSlice(s+2) = H(T,Q_(s+3),Y)",
    "successor": (
        "frozenC R (s+1) = resultant(outputSlice(frozenC R s),"
        "localSlice(s+2),2^(s+1),2)"
    ),
    "topology": "fixed_left_fold",
}

EXPECTED_SYLVESTER = {
    "argument_order": "(left,right,m,2)",
    "coefficient_order": "descending eliminated-coordinate degree",
    "column_order": "descending monomial slots",
    "formal_degree_reduction": "forbidden",
    "literal_coefficient_unit": 1,
    "monic_normalization": "forbidden",
    "primitive_part_or_content_division": "forbidden",
    "row_order": (
        "first 2 shifted rows of the left operand, then m shifted rows of "
        "the right operand"
    ),
    "successor_formal_degrees": ["2^(s+1)", "2"],
}

EXPECTED_H_TERMS: tuple[tuple[int, tuple[int, ...]], ...] = (
    (1, (2, 0, 2, 0, 0, 2)),
    (1, (2, 0, 0, 2, 2, 0)),
    (1, (0, 2, 2, 0, 2, 0)),
    (-2, (2, 0, 1, 1, 1, 1)),
    (-2, (1, 1, 2, 0, 1, 1)),
    (-2, (1, 1, 1, 1, 2, 0)),
    (-28, (1, 1, 0, 2, 0, 2)),
    (-28, (0, 2, 1, 1, 0, 2)),
    (-28, (0, 2, 0, 2, 1, 1)),
)

EXPECTED_KERNEL = {
    "allowed_axioms": ["propext", "Classical.choice", "Quot.sound"],
    "axiom_audit_status": "standard_lean_axioms_only",
    "build_status": "passed",
    "build_targets": [
        "Ecdlp.Proved.FrozenRecursiveProjectiveSemaev"
    ],
    "forbidden_axioms": ["sorryAx"],
    "lean_toolchain": "leanprover/lean4:v4.31.0",
    "mathlib_commit": (
        "fabf563a7c95a166b8d7b6efca11c8b4dc9d911f"
    ),
    "mathlib_input_revision": "v4.31.0",
    "no_sorry_status": "passed",
    "validator_invokes_lean": False,
}

EXPECTED_PROOF_STATUS = {
    "actual_frozen_family_definition": "kernel_checked",
    "affine_output_specialization": "kernel_checked",
    "coefficient_map_specialization": "kernel_checked",
    "direct_S17_equivalence": "not_claimed",
    "infinity_output_specialization": "kernel_checked",
    "literal_H_including_minus_28": "kernel_checked",
    "literal_sylvester_unit_one": "kernel_checked",
    "scheme_or_multiplicity_claim": "not_claimed",
    "solving_rank_yield_cost_claim": "not_claimed",
    "unconditional_one_step_common_projective_root": "kernel_checked",
    "universal_C16_to_C2_reverse_induction": "open_exact_blocker",
    "universal_output_degree_bound": "kernel_checked",
}

EXPECTED_PRODUCER_CHECKS = {
    "C16_evaluated": False,
    "C16_expanded": False,
    "M16_system_materialized": False,
    "S17_materialized": False,
    "exact_target_search_executed": False,
    "experiment_authorized": False,
    "normalization_executed": False,
    "parameter_sweep_executed": False,
    "solver_executed": False,
}

EXPECTED_BLOCKER = {
    "depends_on_kernel_checked_components": [
        "actual_frozen_family",
        "coefficient_map_specialization",
        "affine_and_infinity_outputs",
        "universal_output_degree_bound",
        "unconditional_one_step_common_projective_root",
    ],
    "downstream_open": [
        "universal_C16_to_C2_reverse_induction",
        "RecS17_iff_GeoCat",
    ],
    "forbidden_promotions": [
        "RecS17_iff_GeoCat",
        "RecS17_implies_RatCat",
        "RecS17_implies_Recover",
        "cost_complete",
        "route_promotion",
    ],
    "not_refuted": True,
    "smallest_missing_component": {
        "id": "universal_C16_to_C2_reverse_induction",
        "reason": (
            "the one-step interface does not yet bind every recovered "
            "common root back to predecessor frozen-form specialization "
            "and assemble the full fourteen-node internal projective tree"
        ),
        "requirement": (
            "iterate the unconditional one-step projective-root witness "
            "from C16 through C2, retaining affine and [1:0] branches at "
            "every level"
        ),
    },
    "status": "open_exact_blocker",
}

EXPECTED_SCOPE = {
    "barrier": "B-PKC-M16-COMPLETE-COST-BRIDGE",
    "cell": "CELL-M-PKC-SMOOTH-M16",
    "characteristic_seven_transfer": "forbidden",
    "cost_quantity": "CQ-SEMAEV-S17-SYSTEM-COST",
    "excluded": [
        "expanded or evaluated C16 or S17",
        "materialized M16 polynomial system",
        "universal C16-to-C2 reverse induction claimed without a theorem",
        "direct RecS17 iff GeoCat equivalence",
        "scheme equality, radicality, or multiplicity preservation",
        "solver, parameter sweep, exact-target, or discrete-log execution",
        "degree of regularity, fill-in, rank, yield, memory, or cost",
        "experiment authorization, route promotion, or hypothesis "
        "retention",
    ],
    "generic_kernel_scope": (
        "the recursive identities are algebraic over CommRing "
        "coefficients; the common-root equivalence targets an "
        "algebraically closed field"
    ),
    "included": [
        "actual frozenC family from C2 through C16",
        "literal nine-term H including the -28 block",
        "fixed degrees (2^(s+1),2) and TASK Sylvester coefficient unit +1",
        "same-field and explicit coefficient-map specialization",
        "affine [y:1] and infinity [1:0] output branches",
        "universal output-slice degree bound",
        "unconditional one-step common-projective-root equivalence",
        "exact blocker registration for universal C16-to-C2 reverse "
        "induction",
    ],
    "recursive_curve_scope": (
        "E:y^2=x^3+7 over fields of characteristic not in {2,3,7}"
    ),
    "task": "TASK-020",
}

EXPECTED_TERMINAL = {
    "assurance": "kernel_bound_non_run_certificate",
    "authorization": "none",
    "barrier_effect": "narrowed_open",
    "cell_status": "open_non_executable",
    "cost_quantity_status": "partial",
    "experiment_permission": "none",
    "hypothesis_effect": "none",
    "rank_status": "unpriced",
    "remaining_blocker": (
        "universal C16-to-C2 reverse induction and full projective-tree "
        "assembly remain open_exact_blocker"
    ),
    "retention_disposition": "zero_retention_success",
    "route_effect": "none",
    "solving_cost_status": "unpriced",
    "yield_status": "unpriced",
}

THEOREMS = {
    "actual_frozen_family": (
        "Ecdlp.FrozenProjectiveSemaev.frozenC",
        FROZEN_PATH,
        "noncomputable def",
    ),
    "affine_output_specialization": (
        "Ecdlp.FrozenProjectiveSemaev."
        "specialize_frozenC_succ_over_affine",
        FROZEN_PATH,
        "theorem",
    ),
    "coefficient_map_specialization": (
        "Ecdlp.FrozenProjectiveSemaev.specialize_frozenC_succ_over",
        FROZEN_PATH,
        "theorem",
    ),
    "infinity_output_specialization": (
        "Ecdlp.FrozenProjectiveSemaev."
        "specialize_frozenC_succ_over_infinity",
        FROZEN_PATH,
        "theorem",
    ),
    "literal_H": (
        "Ecdlp.FrozenProjectiveSemaev.HValue",
        FROZEN_PATH,
        "def",
    ),
    "literal_determinant_unit_one": (
        "Ecdlp.TaskSylvester.det_taskSylvester_eq_resultant",
        SYLVESTER_PATH,
        "theorem",
    ),
    "local_slice_degree_bound": (
        "Ecdlp.FrozenProjectiveSemaev.localSliceAt_natDegree_le",
        FROZEN_PATH,
        "theorem",
    ),
    "projective_pair_domain": (
        "Ecdlp.FrozenProjectiveSemaev.ProjectivePair",
        FROZEN_PATH,
        "structure",
    ),
    "same_field_affine_output": (
        "Ecdlp.FrozenProjectiveSemaev.specialize_frozenC_succ_affine",
        FROZEN_PATH,
        "theorem",
    ),
    "same_field_infinity_output": (
        "Ecdlp.FrozenProjectiveSemaev.specialize_frozenC_succ_infinity",
        FROZEN_PATH,
        "theorem",
    ),
    "same_field_one_step_common_root": (
        "Ecdlp.FrozenProjectiveSemaev."
        "specialize_frozenC_succ_eq_zero_iff_common_projective_root",
        FROZEN_PATH,
        "theorem",
    ),
    "same_field_specialization": (
        "Ecdlp.FrozenProjectiveSemaev.specialize_frozenC_succ",
        FROZEN_PATH,
        "theorem",
    ),
    "unconditional_mapped_one_step_common_root": (
        "Ecdlp.FrozenProjectiveSemaev."
        "specialize_frozenC_succ_over_eq_zero_iff_common_projective_root",
        FROZEN_PATH,
        "theorem",
    ),
    "universal_output_degree_bound": (
        "Ecdlp.FrozenProjectiveSemaev."
        "previousSliceAtOver_frozenC_natDegree_le",
        FROZEN_PATH,
        "theorem",
    ),
}


class Replay:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def fail(self, message: str) -> None:
        self.failures.append(message)

    def exact(self, path: str, actual: Any, expected: Any) -> None:
        if actual != expected:
            self.fail(
                f"{path}: expected {expected!r}, observed {actual!r}"
            )

    def mapping(self, path: str, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            self.fail(f"{path}: expected object")
            return {}
        return value

    def sequence(self, path: str, value: Any) -> list[Any]:
        if not isinstance(value, list):
            self.fail(f"{path}: expected array")
            return []
        return value


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_hash(
    artifact_bytes: bytes, hash_path: Path, replay: Replay
) -> None:
    expected = hashlib.sha256(artifact_bytes).hexdigest()
    try:
        line = hash_path.read_text(encoding="ascii").strip()
    except FileNotFoundError:
        replay.fail("artifact.sha256 is missing")
        return
    parts = line.split()
    if len(parts) != 2 or parts[1] != "artifact.json":
        replay.fail(
            "artifact.sha256 must contain '<sha256>  artifact.json'"
        )
        return
    replay.exact("artifact.sha256", parts[0], expected)


def check_dependencies(
    document: dict[str, Any], replay: Replay
) -> None:
    rows = replay.sequence("depends_on", document.get("depends_on"))
    paths = [
        row.get("path") for row in rows if isinstance(row, dict)
    ]
    replay.exact("depends_on.paths", paths, list(EXPECTED_DEPENDENCIES))
    for index, expected_path in enumerate(EXPECTED_DEPENDENCIES):
        if index >= len(rows):
            continue
        row = replay.mapping(f"depends_on[{index}]", rows[index])
        replay.exact(
            f"depends_on[{index}].keys",
            sorted(row),
            [
                "digest_match",
                "observed_sha256",
                "path",
                "required_sha256",
            ],
        )
        path = REPO_ROOT / expected_path
        if not path.is_file():
            replay.fail(f"dependency is missing: {expected_path}")
            continue
        digest = file_digest(path)
        replay.exact(
            f"depends_on[{index}].required_sha256",
            row.get("required_sha256"),
            digest,
        )
        replay.exact(
            f"depends_on[{index}].observed_sha256",
            row.get("observed_sha256"),
            digest,
        )
        replay.exact(
            f"depends_on[{index}].digest_match",
            row.get("digest_match"),
            True,
        )


def source_declared(
    source: str, shape: str, local_name: str
) -> bool:
    escaped = re.escape(local_name)
    if shape == "noncomputable def":
        pattern = rf"(?m)^\s*noncomputable\s+def\s+{escaped}\b"
    else:
        pattern = rf"(?m)^\s*{re.escape(shape)}\s+{escaped}\b"
    return re.search(pattern, source) is not None


def check_theorems(
    document: dict[str, Any], replay: Replay
) -> None:
    bindings = replay.mapping(
        "theorem_bindings", document.get("theorem_bindings")
    )
    replay.exact(
        "theorem_bindings.keys", sorted(bindings), sorted(THEOREMS)
    )
    sources: dict[str, str] = {}
    for key, (name, path, shape) in THEOREMS.items():
        row = replay.mapping(f"theorem_bindings.{key}", bindings.get(key))
        replay.exact(
            f"theorem_bindings.{key}",
            row,
            {
                "declaration": name,
                "kernel_status": "kernel_checked",
                "source_path": path,
                "source_shape": shape,
            },
        )
        source_path = REPO_ROOT / path
        if not source_path.is_file():
            replay.fail(f"theorem source is missing: {path}")
            continue
        source = sources.setdefault(
            path, source_path.read_text(encoding="utf-8")
        )
        if not source_declared(source, shape, name.rsplit(".", 1)[-1]):
            replay.fail(
                f"{name}: declaration not found in digest-bound source"
            )

    frozen = sources.get(FROZEN_PATH, "")
    for token in ("sorry", "admit", "axiom", "unsafe"):
        if re.search(rf"\b{token}\b", frozen):
            replay.fail(f"{FROZEN_PATH}: forbidden Lean token {token!r}")
    imports = [
        line.strip()
        for line in frozen.splitlines()
        if line.startswith("import ")
    ]
    replay.exact(
        "FrozenRecursiveProjectiveSemaev.imports",
        imports,
        [
            "import Mathlib.Algebra.MvPolynomial.Equiv",
            "import Ecdlp.Proved.TaskSylvesterConvention",
        ],
    )
    for fragment in (
        "| 0 => HValue (leafPair 0) (leafPair 1) outputPair",
        "(outputSlice (frozenC R s))",
        "(localSlice (s + 2))",
        "(2 ^ (s + 1)) 2",
        "28 * (",
    ):
        if fragment not in frozen:
            replay.fail(
                f"{FROZEN_PATH}: missing frozen source fragment {fragment!r}"
            )


def expected_h_document() -> dict[str, Any]:
    return {
        "argument_coordinate_order": [
            "X1",
            "Z1",
            "X2",
            "Z2",
            "X3",
            "Z3",
        ],
        "multidegree": [2, 2, 2],
        "term_count": 9,
        "terms": [
            {
                "coefficient": coefficient,
                "exponents": list(exponents),
            }
            for coefficient, exponents in EXPECTED_H_TERMS
        ],
    }


def expected_stage_rows() -> list[dict[str, Any]]:
    return [
        {
            "frozen_index": stage,
            "name": f"C{stage + 2}",
            "output_degree_bound": 2 ** (stage + 1),
        }
        for stage in range(15)
    ]


def expected_successor_rows() -> list[dict[str, Any]]:
    rows = []
    for stage in range(14):
        left = 2 ** (stage + 1)
        rows.append(
            {
                "left_formal_degree": left,
                "right_formal_degree": 2,
                "row_degree_sum": 2 * left,
                "stage_index": stage,
                "successor": f"C{stage + 3}",
                "successor_output_degree_bound": 2 ** (stage + 2),
                "sylvester_size": left + 2,
                "weight_two_row_count": left,
                "weight_zero_row_count": 2,
            }
        )
    return rows


def check_static_contracts(
    document: dict[str, Any], replay: Replay
) -> None:
    replay.exact("artifact_id", document.get("artifact_id"), ARTIFACT_ID)
    replay.exact("schema_version", document.get("schema_version"), 1)
    replay.exact("kind", document.get("kind"), ARTIFACT_KIND)
    replay.exact(
        "top_level_keys",
        sorted(document),
        [
            "artifact_id",
            "assumption_contract",
            "depends_on",
            "fixtures",
            "frozen_family_contract",
            "h_literal",
            "kernel_contract",
            "kind",
            "literal_sylvester_contract",
            "open_exact_blocker",
            "producer_checks",
            "proof_status",
            "recurrence_schedule",
            "schema_version",
            "scope",
            "terminal_disposition",
            "theorem_bindings",
        ],
    )
    replay.exact(
        "assumption_contract",
        document.get("assumption_contract"),
        EXPECTED_ASSUMPTIONS,
    )
    replay.exact(
        "frozen_family_contract",
        document.get("frozen_family_contract"),
        EXPECTED_FAMILY,
    )
    replay.exact(
        "literal_sylvester_contract",
        document.get("literal_sylvester_contract"),
        EXPECTED_SYLVESTER,
    )
    replay.exact(
        "h_literal", document.get("h_literal"), expected_h_document()
    )
    replay.exact(
        "kernel_contract", document.get("kernel_contract"), EXPECTED_KERNEL
    )
    replay.exact(
        "proof_status",
        document.get("proof_status"),
        EXPECTED_PROOF_STATUS,
    )
    replay.exact(
        "producer_checks",
        document.get("producer_checks"),
        EXPECTED_PRODUCER_CHECKS,
    )
    replay.exact(
        "open_exact_blocker",
        document.get("open_exact_blocker"),
        EXPECTED_BLOCKER,
    )
    replay.exact("scope", document.get("scope"), EXPECTED_SCOPE)
    replay.exact(
        "terminal_disposition",
        document.get("terminal_disposition"),
        EXPECTED_TERMINAL,
    )


def check_schedule(
    document: dict[str, Any], replay: Replay
) -> None:
    schedule = replay.mapping(
        "recurrence_schedule", document.get("recurrence_schedule")
    )
    replay.exact(
        "recurrence_schedule.keys",
        sorted(schedule),
        ["stage_rows", "successor_rows"],
    )
    replay.exact(
        "recurrence_schedule.stage_rows",
        schedule.get("stage_rows"),
        expected_stage_rows(),
    )
    replay.exact(
        "recurrence_schedule.successor_rows",
        schedule.get("successor_rows"),
        expected_successor_rows(),
    )


Polynomial = list[int]
Coordinate = Polynomial
PolynomialPair = tuple[Coordinate, Coordinate]


def poly_add(left: Polynomial, right: Polynomial) -> Polynomial:
    result = [0] * max(len(left), len(right))
    for index in range(len(result)):
        result[index] = (
            (left[index] if index < len(left) else 0)
            + (right[index] if index < len(right) else 0)
        )
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def poly_mul(left: Polynomial, right: Polynomial) -> Polynomial:
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def poly_pow(value: Polynomial, exponent: int) -> Polynomial:
    result = [1]
    for _ in range(exponent):
        result = poly_mul(result, value)
    return result


def h_value(
    q1: PolynomialPair,
    q2: PolynomialPair,
    q3: PolynomialPair,
    terms: tuple[tuple[int, tuple[int, ...]], ...] = EXPECTED_H_TERMS,
) -> Polynomial:
    coordinates = q1 + q2 + q3
    result = [0]
    for coefficient, exponents in terms:
        term = [coefficient]
        for coordinate, exponent in zip(coordinates, exponents):
            term = poly_mul(term, poly_pow(coordinate, exponent))
        result = poly_add(result, term)
    return result


def fixed_descending(value: Polynomial, degree: int) -> list[int]:
    coefficients = value + [0] * max(0, degree + 1 - len(value))
    return list(reversed(coefficients[: degree + 1]))


def permutation_sign(values: tuple[int, ...]) -> int:
    inversions = sum(
        values[i] > values[j]
        for i in range(len(values))
        for j in range(i + 1, len(values))
    )
    return -1 if inversions % 2 else 1


def determinant(matrix: list[list[int]]) -> int:
    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise ValueError("determinant input must be square")
    result = 0
    for sigma in permutations(range(size)):
        term = permutation_sign(sigma)
        for row, column in enumerate(sigma):
            term *= matrix[row][column]
        result += term
    return result


def task_sylvester(
    left: list[int],
    right: list[int],
    left_degree: int,
    right_degree: int,
) -> list[list[int]]:
    if len(left) != left_degree + 1:
        raise ValueError("left fixed-degree coefficient length mismatch")
    if len(right) != right_degree + 1:
        raise ValueError("right fixed-degree coefficient length mismatch")
    size = left_degree + right_degree
    matrix = [[0] * size for _ in range(size)]
    for shift in range(right_degree):
        matrix[shift][shift : shift + left_degree + 1] = left
    for shift in range(left_degree):
        row = right_degree + shift
        matrix[row][shift : shift + right_degree + 1] = right
    return matrix


def binary_eval(
    coefficients: list[int],
    pair: tuple[int, int],
    prime: int,
) -> int:
    degree = len(coefficients) - 1
    u, v = pair
    return sum(
        coefficient * u ** (degree - index) * v**index
        for index, coefficient in enumerate(coefficients)
    ) % prime


def p1(prime: int) -> list[tuple[int, int]]:
    return [(x, 1) for x in range(prime)] + [(1, 0)]


def common_projective_roots(
    left: list[int], right: list[int], prime: int
) -> list[list[int]]:
    return [
        [u, v]
        for u, v in p1(prime)
        if binary_eval(left, (u, v), prime) == 0
        and binary_eval(right, (u, v), prime) == 0
    ]


def as_constant_pair(pair: list[int]) -> PolynomialPair:
    if (
        len(pair) != 2
        or not all(isinstance(value, int) for value in pair)
        or pair == [0, 0]
    ):
        raise ValueError("projective input must be a nonzero integer pair")
    return ([pair[0]], [pair[1]])


def replay_step(
    inputs: list[list[int]],
    terms: tuple[tuple[int, tuple[int, ...]], ...] = EXPECTED_H_TERMS,
) -> tuple[list[int], list[int]]:
    if len(inputs) != 4:
        raise ValueError("step fixture requires q0,q1,q2,y")
    q0, q1, q2, y = [as_constant_pair(pair) for pair in inputs]
    t_pair: PolynomialPair = ([0, 1], [1])
    left = fixed_descending(h_value(q0, q1, t_pair, terms), 2)
    right = fixed_descending(h_value(t_pair, q2, y, terms), 2)
    return left, right


def check_step_fixture(
    name: str,
    fixture: dict[str, Any],
    replay: Replay,
) -> None:
    prime = fixture.get("field_prime")
    formal = fixture.get("formal_degrees")
    inputs = fixture.get("projective_inputs_q0_q1_q2_y")
    if (
        not isinstance(prime, int)
        or not isinstance(formal, list)
        or formal != [2, 2]
        or not isinstance(inputs, list)
    ):
        replay.fail(f"fixtures.{name}: malformed input")
        return
    try:
        left, right = replay_step(inputs)
        matrix = task_sylvester(left, right, 2, 2)
        integer_resultant = determinant(matrix)
        mapped_matrix = [
            [entry % prime for entry in row] for row in matrix
        ]
        mapped_resultant = determinant(mapped_matrix) % prime
        roots = common_projective_roots(left, right, prime)
    except (TypeError, ValueError) as error:
        replay.fail(f"fixtures.{name}: replay failed: {error}")
        return
    replay.exact(
        f"fixtures.{name}.left_coefficients_descending_over_Z",
        fixture.get("left_coefficients_descending_over_Z"),
        left,
    )
    replay.exact(
        f"fixtures.{name}.right_coefficients_descending_over_Z",
        fixture.get("right_coefficients_descending_over_Z"),
        right,
    )
    replay.exact(
        f"fixtures.{name}.task_sylvester_matrix_over_Z",
        fixture.get("task_sylvester_matrix_over_Z"),
        matrix,
    )
    replay.exact(
        f"fixtures.{name}.integer_resultant",
        fixture.get("integer_resultant"),
        integer_resultant,
    )
    replay.exact(
        f"fixtures.{name}.mapped_resultant_mod_5",
        fixture.get("mapped_resultant_mod_5"),
        mapped_resultant,
    )
    replay.exact(
        f"fixtures.{name}.integer_map_resultant",
        integer_resultant % prime,
        mapped_resultant,
    )
    replay.exact(
        f"fixtures.{name}.coefficient_map_commutes",
        fixture.get("coefficient_map_commutes"),
        True,
    )
    replay.exact(
        f"fixtures.{name}.common_projective_roots_mod_5",
        fixture.get("common_projective_roots_mod_5"),
        roots,
    )
    witness = fixture.get("distinguished_witness")
    if witness is not None:
        replay.exact(
            f"fixtures.{name}.distinguished_witness_valid",
            witness in roots,
            True,
        )
        replay.exact(
            f"fixtures.{name}.distinguished_witness_nonirrelevant",
            witness != [0, 0],
            True,
        )


def check_fixtures(
    document: dict[str, Any], replay: Replay
) -> None:
    fixtures = replay.mapping("fixtures", document.get("fixtures"))
    replay.exact(
        "fixtures.keys",
        sorted(fixtures),
        [
            "F5_affine_intermediate_root",
            "F5_infinity_intermediate_root",
            "F5_minus_28_nonzero_control",
        ],
    )
    for name in (
        "F5_affine_intermediate_root",
        "F5_infinity_intermediate_root",
        "F5_minus_28_nonzero_control",
    ):
        fixture = replay.mapping(f"fixtures.{name}", fixtures.get(name))
        check_step_fixture(name, fixture, replay)

    affine = replay.mapping(
        "fixtures.F5_affine_intermediate_root",
        fixtures.get("F5_affine_intermediate_root"),
    )
    replay.exact(
        "fixtures.F5_affine_intermediate_root.required_branch",
        affine.get("required_branch"),
        "affine_common_root_[0:1]",
    )
    infinity = replay.mapping(
        "fixtures.F5_infinity_intermediate_root",
        fixtures.get("F5_infinity_intermediate_root"),
    )
    replay.exact(
        "fixtures.F5_infinity_intermediate_root.required_branch",
        infinity.get("required_branch"),
        "retain_common_root_[1:0]_after_degree_drop",
    )
    control = replay.mapping(
        "fixtures.F5_minus_28_nonzero_control",
        fixtures.get("F5_minus_28_nonzero_control"),
    )
    replay.exact(
        "fixtures.F5_minus_28_nonzero_control.required_disposition",
        control.get("required_disposition"),
        "literal_minus_28_block_is_semantically_detected",
    )
    zeroed_terms = tuple(
        (0 if coefficient == -28 else coefficient, exponents)
        for coefficient, exponents in EXPECTED_H_TERMS
    )
    try:
        left, right = replay_step(
            control.get("projective_inputs_q0_q1_q2_y"), zeroed_terms
        )
        zeroed_result = (
            determinant(task_sylvester(left, right, 2, 2)) % 5
        )
        replay.exact(
            "fixtures.F5_minus_28_nonzero_control."
            "zeroed_minus_28_resultant_mod_5",
            control.get("zeroed_minus_28_resultant_mod_5"),
            zeroed_result,
        )
        replay.exact(
            "fixtures.F5_minus_28_nonzero_control.literal_distinct",
            control.get("mapped_resultant_mod_5") != zeroed_result,
            True,
        )
    except (TypeError, ValueError) as error:
        replay.fail(f"minus-28 control failed: {error}")


def validate(
    artifact_path: Path = ARTIFACT_PATH,
    hash_path: Path = HASH_PATH,
) -> list[str]:
    replay = Replay()
    try:
        artifact_bytes = artifact_path.read_bytes()
    except FileNotFoundError:
        return [f"artifact is missing: {artifact_path}"]
    try:
        document = json.loads(artifact_bytes)
    except json.JSONDecodeError as error:
        return [f"artifact is not valid JSON: {error}"]
    if not isinstance(document, dict):
        return ["artifact root must be an object"]

    check_hash(artifact_bytes, hash_path, replay)
    check_static_contracts(document, replay)
    check_dependencies(document, replay)
    check_theorems(document, replay)
    check_schedule(document, replay)
    check_fixtures(document, replay)
    return replay.failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--artifact", type=Path, default=ARTIFACT_PATH
    )
    parser.add_argument("--hash", type=Path, default=HASH_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures = validate(args.artifact, args.hash)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print(
        "TASK-020 frozen-Cr specialization kernel certificate: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
