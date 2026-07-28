#!/usr/bin/env python3
"""Independently validate the non-run TASK-019 kernel-binding certificate.

This validator imports neither a producer nor repository mathematical helpers.
It binds exact Lean declaration names to source digests and independently
replays small fixed-degree binary-form resultants.  It does not invoke Lean,
materialize C16/S17, or execute a solver.
"""

from __future__ import annotations

import argparse
from itertools import permutations
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
ARTIFACT_PATH = HERE / "artifact.json"
HASH_PATH = HERE / "artifact.sha256"

ARTIFACT_ID = "PKC-SMOOTH-M16-PROJECTIVE-RESULTANT-KERNEL-001"
ARTIFACT_KIND = "non_run_kernel_binding_certificate"

TASK018_PATH = (
    "experiments/engine/pkc_smooth_m16_projective_bridge/artifact.json"
)
FIXED_PATH = "Ecdlp/Proved/FixedDegreeProjectiveResultant.lean"
SYLVESTER_PATH = "Ecdlp/Proved/TaskSylvesterConvention.lean"

EXPECTED_DEPENDENCIES = (TASK018_PATH, FIXED_PATH, SYLVESTER_PATH)

EXPECTED_THEOREMS = {
    "projective_root_predicate": (
        "Ecdlp.ProjectiveResultant.HasCommonProjectiveRoot",
        FIXED_PATH,
        "def",
    ),
    "infinity_evaluation": (
        "Ecdlp.ProjectiveResultant.eval_homogenize_second_zero",
        FIXED_PATH,
        "theorem",
    ),
    "distinguished_infinity_evaluation": (
        "Ecdlp.ProjectiveResultant.eval_homogenize_one_zero",
        FIXED_PATH,
        "theorem",
    ),
    "distinguished_infinity_common_root": (
        "Ecdlp.ProjectiveResultant.one_zero_is_common_root_iff",
        FIXED_PATH,
        "theorem",
    ),
    "degree_drop": (
        "Ecdlp.ProjectiveResultant.natDegree_lt_of_le_of_coeff_eq_zero",
        FIXED_PATH,
        "theorem",
    ),
    "fixed_degree_common_root": (
        "Ecdlp.ProjectiveResultant."
        "fixedDegree_resultant_eq_zero_iff_common_projective_root",
        FIXED_PATH,
        "theorem",
    ),
    "mapped_fixed_degree_common_root": (
        "Ecdlp.ProjectiveResultant."
        "map_fixedDegree_resultant_eq_zero_iff_common_projective_root",
        FIXED_PATH,
        "theorem",
    ),
    "injective_algebraic_closure_reflection": (
        "Ecdlp.ProjectiveResultant."
        "fixedDegree_resultant_eq_zero_iff_common_projective_root_over",
        FIXED_PATH,
        "theorem",
    ),
    "literal_matrix_relation": (
        "Ecdlp.TaskSylvester.taskSylvester_eq_reindex_transpose",
        SYLVESTER_PATH,
        "theorem",
    ),
    "literal_determinant_unit_one": (
        "Ecdlp.TaskSylvester.det_taskSylvester_eq_resultant",
        SYLVESTER_PATH,
        "theorem",
    ),
    "literal_end_to_end_common_root": (
        "Ecdlp.TaskSylvester."
        "det_taskSylvester_eq_zero_iff_common_projective_root",
        SYLVESTER_PATH,
        "theorem",
    ),
}

EXPECTED_ASSUMPTIONS = {
    "coefficient_domain": (
        "the generic common-root theorem uses a Field K with IsAlgClosed K"
    ),
    "formal_degrees": "m>0 and n>0",
    "degree_bounds": "natDegree(f)<=m and natDegree(g)<=n",
    "zero_forms": (
        "included; no f!=0 or g!=0 hypothesis is imposed"
    ),
    "projective_domain": "a witness pair (U,V) satisfies U!=0 or V!=0",
    "affine_output": (
        "when V!=0 the witness dehomogenizes to x=U/V and [x:1]"
    ),
    "infinity_output": (
        "when V=0 the valid witness is represented by [1:0]"
    ),
    "specialization_map": (
        "the mapped theorem keeps the coefficient ring homomorphism explicit"
    ),
    "normalization": (
        "formal degrees and leading zero coefficients are retained; no "
        "primitive, content, monic, or actual-degree normalization"
    ),
}

EXPECTED_CONVENTIONS = {
    "binary_form": (
        "p.homogenize d=sum_(k=0)^d p.coeff(k)*U^k*V^(d-k)"
    ),
    "task_coefficient_order": (
        "descending U degree [p.coeff(d),...,p.coeff(0)]"
    ),
    "task_row_order": (
        "first n shifted rows of f, then m shifted rows of g"
    ),
    "task_column_order": "descending monomial slots",
    "mathlib_relation": (
        "taskSylvester(f,g,m,n)=reindex(Fin.revPerm,Fin.revPerm,"
        "transpose(Polynomial.sylvester(f,g,m,n)))"
    ),
    "argument_order": "(f,g,m,n) is retained",
    "determinant": "ordinary determinant",
    "literal_coefficient_unit": 1,
    "formal_degree_reduction": "forbidden",
    "primitive_part_or_content_division": "forbidden",
    "monic_normalization": "forbidden",
}

EXPECTED_STATUSES = {
    "fixed_degree_common_root": "kernel_checked",
    "task_sylvester_matrix_bridge": "kernel_checked",
    "task_sylvester_end_to_end": "kernel_checked",
    "recursive_Cr_specialization": "open_exact_blocker",
    "universal_reverse_C16_to_C2": "open_exact_blocker",
    "direct_S17_equivalence": "not_claimed",
    "scheme_or_multiplicity_claim": "not_claimed",
    "cost_rank_yield_claim": "not_claimed",
}

EXPECTED_KERNEL = {
    "lean_toolchain": "leanprover/lean4:v4.31.0",
    "mathlib_input_revision": "v4.31.0",
    "mathlib_commit": "fabf563a7c95a166b8d7b6efca11c8b4dc9d911f",
    "build_targets": [
        "Ecdlp.Proved.FixedDegreeProjectiveResultant",
        "Ecdlp.Proved.TaskSylvesterConvention",
    ],
    "build_status": "passed",
    "no_sorry_status": "passed",
    "axiom_audit_status": "standard_lean_axioms_only",
    "allowed_axioms": ["propext", "Classical.choice", "Quot.sound"],
    "forbidden_axioms": ["sorryAx"],
    "validator_invokes_lean": False,
}

EXPECTED_SCOPE = {
    "task": "TASK-019",
    "cell": "CELL-M-PKC-SMOOTH-M16",
    "barrier": "B-PKC-M16-COMPLETE-COST-BRIDGE",
    "cost_quantity": "CQ-SEMAEV-S17-SYSTEM-COST",
    "generic_resultant_scope": (
        "any algebraically closed field; no curve or characteristic "
        "restriction is used by the generic theorem"
    ),
    "recursive_curve_scope": (
        "E:y^2=x^3+7 over fields of characteristic not in {2,3,7}"
    ),
    "characteristic_seven_transfer": "forbidden",
    "included": [
        "fixed-degree projective resultant common-root theorem",
        "literal TASK-018 Sylvester matrix and determinant unit-one bridge",
        "small independent degree-drop, zero-form, affine, infinity, "
        "ordering, and specialization fixtures",
        "exact blocker registration for recursive specialization and "
        "universal reverse projection",
    ],
    "excluded": [
        "expanded or evaluated S17",
        "materialized M16 polynomial system",
        "recursive C_r specialization claimed without a theorem",
        "universal reverse C16-to-C2 projection claimed without a theorem",
        "scheme equality, radicality, or multiplicity preservation",
        "solver, parameter sweep, exact-target, or discrete-log execution",
        "degree of regularity, fill-in, rank, yield, memory, or cost",
        "experiment authorization, route promotion, or hypothesis retention",
    ],
}

EXPECTED_PRODUCER_CHECKS = {
    "S17_materialized": False,
    "C16_expanded": False,
    "C16_evaluated": False,
    "M16_system_materialized": False,
    "solver_executed": False,
    "parameter_sweep_executed": False,
    "exact_target_search_executed": False,
    "experiment_authorized": False,
}

EXPECTED_BLOCKER = {
    "status": "open_exact_blocker",
    "smallest_missing_component": {
        "id": "recursive_Cr_specialization_binding",
        "requirement": (
            "exact specialization of frozen C_r at formal degrees "
            "(2^(r-2),2), with coefficient unit 1, affine output, and [1:0]"
        ),
        "reason": (
            "no kernel-bound recursive C_r definition and application "
            "theorem is present"
        ),
    },
    "depends_on_kernel_checked_components": [
        "fixed_degree_common_root",
        "coefficient_map_resultant",
        "literal_task_sylvester_unit_one",
    ],
    "downstream_open": [
        "generic_C16_forward",
        "universal_reverse_C16_to_C2",
    ],
    "not_refuted": True,
    "forbidden_promotions": [
        "RecS17_iff_GeoCat",
        "RecS17_implies_RatCat",
        "RecS17_implies_Recover",
        "cost_complete",
        "route_promotion",
    ],
}

EXPECTED_TERMINAL = {
    "assurance": "kernel_bound_non_run_certificate",
    "authorization": "none",
    "experiment_permission": "none",
    "cell_status": "open_non_executable",
    "cost_quantity_status": "partial",
    "barrier_effect": "narrowed_open",
    "route_effect": "none",
    "hypothesis_effect": "none",
    "retention_disposition": "zero_retention_success",
    "rank_status": "unpriced",
    "yield_status": "unpriced",
    "solving_cost_status": "unpriced",
    "remaining_blocker": (
        "recursive symbolic C_r specialization, including output [1:0], "
        "and the universal C16-to-C2 reverse induction remain "
        "open_exact_blocker"
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


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def permutation_sign(values: tuple[int, ...]) -> int:
    inversions = sum(
        values[i] > values[j]
        for i in range(len(values))
        for j in range(i + 1, len(values))
    )
    return -1 if inversions % 2 else 1


def determinant_mod(matrix: list[list[int]], prime: int) -> int:
    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise ValueError("determinant input must be square")
    total = 0
    for sigma in permutations(range(size)):
        term = permutation_sign(sigma)
        for row, column in enumerate(sigma):
            term *= matrix[row][column]
        total += term
    return total % prime


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


def polynomial_add(left: list[int], right: list[int]) -> list[int]:
    result = [0] * max(len(left), len(right))
    for index in range(len(result)):
        result[index] = (
            (left[index] if index < len(left) else 0)
            + (right[index] if index < len(right) else 0)
        )
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def polynomial_mul(left: list[int], right: list[int]) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def determinant_polynomial(
    matrix: list[list[list[int]]],
) -> list[int]:
    size = len(matrix)
    total = [0]
    for sigma in permutations(range(size)):
        term = [permutation_sign(sigma)]
        for row, column in enumerate(sigma):
            entry = matrix[row][column]
            factor = entry if isinstance(entry, list) else [entry]
            term = polynomial_mul(term, factor)
        total = polynomial_add(total, term)
    return total


def evaluate_polynomial(
    coefficients_ascending: list[int], value: int, prime: int
) -> int:
    result = 0
    for coefficient in reversed(coefficients_ascending):
        result = (result * value + coefficient) % prime
    return result


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
        replay.fail("artifact.sha256 must contain '<sha256>  artifact.json'")
        return
    replay.exact("artifact.sha256", parts[0], expected)


def check_dependencies(
    document: dict[str, Any], replay: Replay
) -> None:
    rows = replay.sequence("depends_on", document.get("depends_on"))
    observed_paths = [
        row.get("path") for row in rows if isinstance(row, dict)
    ]
    replay.exact(
        "depends_on.paths", observed_paths, list(EXPECTED_DEPENDENCIES)
    )
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
    source: str, kind: str, local_name: str
) -> bool:
    pattern = rf"(?m)^\s*(?:@\[[^\n]*\]\s*)?{kind}\s+{re.escape(local_name)}\b"
    return re.search(pattern, source) is not None


def check_theorems(
    document: dict[str, Any], replay: Replay
) -> None:
    bindings = replay.mapping(
        "theorem_bindings", document.get("theorem_bindings")
    )
    replay.exact(
        "theorem_bindings.keys",
        sorted(bindings),
        sorted(EXPECTED_THEOREMS),
    )
    source_cache: dict[str, str] = {}
    for key, (name, path, kind) in EXPECTED_THEOREMS.items():
        row = replay.mapping(f"theorem_bindings.{key}", bindings.get(key))
        replay.exact(
            f"theorem_bindings.{key}",
            row,
            {
                "declaration": name,
                "kernel_status": "kernel_checked",
                "source_path": path,
            },
        )
        source_path = REPO_ROOT / path
        if not source_path.is_file():
            replay.fail(f"theorem source is missing: {path}")
            continue
        source = source_cache.setdefault(
            path, source_path.read_text(encoding="utf-8")
        )
        local_name = name.rsplit(".", 1)[-1]
        if not source_declared(source, kind, local_name):
            replay.fail(
                f"{name}: declaration not found in digest-bound source"
            )

    for path, source in source_cache.items():
        for token in ("sorry", "admit", "axiom", "unsafe"):
            if re.search(rf"\b{token}\b", source):
                replay.fail(f"{path}: forbidden Lean token {token!r}")

    fixed_imports = [
        line.strip()
        for line in source_cache.get(FIXED_PATH, "").splitlines()
        if line.startswith("import ")
    ]
    replay.exact(
        "FixedDegreeProjectiveResultant.imports",
        fixed_imports,
        [
            "import Mathlib.Algebra.Polynomial.Homogenize",
            "import Mathlib.FieldTheory.IsAlgClosed.Basic",
            "import Mathlib.RingTheory.Polynomial.Resultant.Basic",
        ],
    )
    if "import Mathlib\n" in source_cache.get(FIXED_PATH, ""):
        replay.fail("FixedDegreeProjectiveResultant uses umbrella Mathlib")
    if "SemaevFour" in source_cache.get(FIXED_PATH, ""):
        replay.fail("FixedDegreeProjectiveResultant depends on SemaevFour")


def check_static_contracts(
    document: dict[str, Any], replay: Replay
) -> None:
    replay.exact(
        "artifact_id", document.get("artifact_id"), ARTIFACT_ID
    )
    replay.exact("schema_version", document.get("schema_version"), 1)
    replay.exact("kind", document.get("kind"), ARTIFACT_KIND)
    replay.exact(
        "kernel_contract",
        document.get("kernel_contract"),
        EXPECTED_KERNEL,
    )
    replay.exact(
        "assumption_contract",
        document.get("assumption_contract"),
        EXPECTED_ASSUMPTIONS,
    )
    replay.exact(
        "literal_convention_binding",
        document.get("literal_convention_binding"),
        EXPECTED_CONVENTIONS,
    )
    replay.exact(
        "proof_status", document.get("proof_status"), EXPECTED_STATUSES
    )
    replay.exact("scope", document.get("scope"), EXPECTED_SCOPE)
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
    replay.exact(
        "terminal_disposition",
        document.get("terminal_disposition"),
        EXPECTED_TERMINAL,
    )


def check_fixed_fixture(
    name: str,
    fixture: dict[str, Any],
    replay: Replay,
) -> None:
    prime = fixture.get("field_prime")
    formal = fixture.get("formal_degrees")
    left = fixture.get("left_coefficients_descending")
    right = fixture.get("right_coefficients_descending")
    if (
        not isinstance(prime, int)
        or not isinstance(formal, list)
        or len(formal) != 2
        or not isinstance(left, list)
        or not isinstance(right, list)
    ):
        replay.fail(f"fixtures.{name}: malformed fixed-resultant input")
        return
    try:
        matrix = task_sylvester(left, right, formal[0], formal[1])
        resultant = determinant_mod(matrix, prime)
        roots = common_projective_roots(left, right, prime)
    except (TypeError, ValueError) as error:
        replay.fail(f"fixtures.{name}: {error}")
        return
    replay.exact(
        f"fixtures.{name}.task_sylvester_matrix",
        fixture.get("task_sylvester_matrix"),
        matrix,
    )
    replay.exact(
        f"fixtures.{name}.fixed_resultant_mod_p",
        fixture.get("fixed_resultant_mod_p"),
        resultant,
    )
    replay.exact(
        f"fixtures.{name}.common_projective_roots",
        fixture.get("common_projective_roots"),
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
            "F5_affine_output",
            "F5_degree_drop_infinity",
            "F5_odd_convention_control",
            "F5_one_sided_drop_no_root",
            "F5_recurrence_row_order",
            "F5_specialization_to_infinity",
            "F5_zero_both",
            "F5_zero_left",
            "F5_zero_right",
        ],
    )

    infinity = replay.mapping(
        "fixtures.F5_degree_drop_infinity",
        fixtures.get("F5_degree_drop_infinity"),
    )
    check_fixed_fixture("F5_degree_drop_infinity", infinity, replay)
    replay.exact(
        "fixtures.F5_degree_drop_infinity.required_disposition",
        infinity.get("required_disposition"),
        "retain_[1:0]_and_fixed_formal_degrees",
    )
    reduced = replay.mapping(
        "fixtures.F5_degree_drop_infinity.reduced_affine_control",
        infinity.get("reduced_affine_control"),
    )
    try:
        reduced_matrix = task_sylvester(
            reduced.get("left_coefficients_descending"),
            reduced.get("right_coefficients_descending"),
            reduced.get("degrees")[0],
            reduced.get("degrees")[1],
        )
        reduced_resultant = determinant_mod(reduced_matrix, 5)
        left = reduced.get("left_coefficients_descending")
        right = reduced.get("right_coefficients_descending")
        affine_roots = [
            x
            for x in range(5)
            if binary_eval(left, (x, 1), 5) == 0
            and binary_eval(right, (x, 1), 5) == 0
        ]
        replay.exact(
            "fixtures.F5_degree_drop_infinity."
            "reduced_affine_control.resultant_mod_5",
            reduced.get("resultant_mod_5"),
            reduced_resultant,
        )
        replay.exact(
            "fixtures.F5_degree_drop_infinity."
            "reduced_affine_control.common_roots",
            reduced.get("common_roots"),
            affine_roots,
        )
    except (TypeError, ValueError, IndexError) as error:
        replay.fail(f"reduced infinity control malformed: {error}")

    one_sided = replay.mapping(
        "fixtures.F5_one_sided_drop_no_root",
        fixtures.get("F5_one_sided_drop_no_root"),
    )
    check_fixed_fixture(
        "F5_one_sided_drop_no_root", one_sided, replay
    )
    replay.exact(
        "fixtures.F5_one_sided_drop_no_root.required_disposition",
        one_sided.get("required_disposition"),
        "one_degree_drop_alone_does_not_force_zero",
    )

    row_order = replay.mapping(
        "fixtures.F5_recurrence_row_order",
        fixtures.get("F5_recurrence_row_order"),
    )
    check_fixed_fixture("F5_recurrence_row_order", row_order, replay)
    replay.exact(
        "fixtures.F5_recurrence_row_order.row_order_check",
        row_order.get("row_order_check"),
        "full_matrix_equality_not_determinant_only",
    )

    zero_left = replay.mapping(
        "fixtures.F5_zero_left", fixtures.get("F5_zero_left")
    )
    check_fixed_fixture("F5_zero_left", zero_left, replay)
    replay.exact(
        "fixtures.F5_zero_left.zero_form_policy",
        zero_left.get("zero_form_policy"),
        "included_without_nonzero_hypothesis",
    )

    zero_right = replay.mapping(
        "fixtures.F5_zero_right", fixtures.get("F5_zero_right")
    )
    check_fixed_fixture("F5_zero_right", zero_right, replay)
    replay.exact(
        "fixtures.F5_zero_right.zero_form_policy",
        zero_right.get("zero_form_policy"),
        "right_zero_included",
    )

    zero_both = replay.mapping(
        "fixtures.F5_zero_both", fixtures.get("F5_zero_both")
    )
    check_fixed_fixture("F5_zero_both", zero_both, replay)
    replay.exact(
        "fixtures.F5_zero_both.zero_form_policy",
        zero_both.get("zero_form_policy"),
        "both_zero_included",
    )

    affine = replay.mapping(
        "fixtures.F5_affine_output", fixtures.get("F5_affine_output")
    )
    check_fixed_fixture("F5_affine_output", affine, replay)
    replay.exact(
        "fixtures.F5_affine_output.infinity_is_common_root",
        affine.get("infinity_is_common_root"),
        False,
    )

    control = replay.mapping(
        "fixtures.F5_odd_convention_control",
        fixtures.get("F5_odd_convention_control"),
    )
    replay.exact(
        "fixtures.F5_odd_convention_control",
        control,
        {
            "field_prime": 5,
            "formal_degrees": [1, 1],
            "left_coefficients_descending": [1, 0],
            "right_coefficients_descending": [1, 1],
            "task_sylvester_matrix": [[1, 0], [1, 1]],
            "literal_resultant_mod_5": 1,
            "swapped_argument_matrix": [[1, 1], [1, 0]],
            "swapped_argument_resultant_mod_5": 4,
            "swapped_row_block_resultant_mod_5": 4,
            "reversed_coefficient_resultant_mod_5": 4,
            "negative_unit_result_mod_5": 4,
        },
    )
    if control:
        literal_matrix = task_sylvester([1, 0], [1, 1], 1, 1)
        swapped_matrix = task_sylvester([1, 1], [1, 0], 1, 1)
        replay.exact(
            "odd_control.literal_matrix_replay",
            literal_matrix,
            control.get("task_sylvester_matrix"),
        )
        replay.exact(
            "odd_control.literal_resultant_replay",
            determinant_mod(literal_matrix, 5),
            control.get("literal_resultant_mod_5"),
        )
        replay.exact(
            "odd_control.swapped_resultant_replay",
            determinant_mod(swapped_matrix, 5),
            control.get("swapped_argument_resultant_mod_5"),
        )
        row_swapped = list(reversed(literal_matrix))
        replay.exact(
            "odd_control.row_block_replay",
            determinant_mod(row_swapped, 5),
            control.get("swapped_row_block_resultant_mod_5"),
        )
        reversed_coefficients = task_sylvester(
            [0, 1], [1, 1], 1, 1
        )
        replay.exact(
            "odd_control.coefficient_order_replay",
            determinant_mod(reversed_coefficients, 5),
            control.get("reversed_coefficient_resultant_mod_5"),
        )

    specialization = replay.mapping(
        "fixtures.F5_specialization_to_infinity",
        fixtures.get("F5_specialization_to_infinity"),
    )
    replay.exact(
        "fixtures.F5_specialization_to_infinity.parameter",
        specialization.get("parameter"),
        "s",
    )
    left_poly = specialization.get(
        "left_coefficients_descending_polynomials_ascending_s"
    )
    right_poly = specialization.get(
        "right_coefficients_descending_polynomials_ascending_s"
    )
    if (
        not isinstance(left_poly, list)
        or not isinstance(right_poly, list)
    ):
        replay.fail("specialization polynomial coefficient arrays malformed")
        return
    try:
        matrix_poly = task_sylvester(left_poly, right_poly, 2, 2)
        resultant_poly = determinant_polynomial(matrix_poly)
        replay.exact(
            "fixtures.F5_specialization_to_infinity."
            "resultant_polynomial_ascending_s_over_Z",
            specialization.get(
                "resultant_polynomial_ascending_s_over_Z"
            ),
            resultant_poly,
        )
        for value, expected, root in (
            (0, 0, [1, 0]),
            (1, 2, None),
        ):
            replay.exact(
                f"specialization.s={value}.resultant",
                evaluate_polynomial(resultant_poly, value, 5),
                expected,
            )
            row = replay.mapping(
                f"specialization.values.s={value}",
                specialization.get("values", {}).get(str(value)),
            )
            replay.exact(
                f"specialization.values.s={value}.resultant_mod_5",
                row.get("resultant_mod_5"),
                expected,
            )
            if root is not None:
                replay.exact(
                    f"specialization.values.s={value}.witness",
                    row.get("distinguished_witness"),
                    root,
                )
                specialized_left = [
                    evaluate_polynomial(entry, value, 5)
                    for entry in left_poly
                ]
                specialized_right = [
                    evaluate_polynomial(entry, value, 5)
                    for entry in right_poly
                ]
                replay.exact(
                    f"specialization.values.s={value}.witness.left",
                    binary_eval(specialized_left, tuple(root), 5),
                    0,
                )
                replay.exact(
                    f"specialization.values.s={value}.witness.right",
                    binary_eval(specialized_right, tuple(root), 5),
                    0,
                )
    except (TypeError, ValueError) as error:
        replay.fail(f"specialization replay failed: {error}")
    replay.exact(
        "fixtures.F5_specialization_to_infinity."
        "recursive_claim_status",
        specialization.get("recursive_claim_status"),
        "fixture_only_not_Cr_theorem",
    )


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
        "TASK-019 non-run projective-resultant kernel certificate: PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
