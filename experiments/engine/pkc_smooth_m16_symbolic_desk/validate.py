#!/usr/bin/env python3
"""Independently replay the M16 symbolic desk-cost artifact.

The validator imports neither the producer nor its helpers.  It checks
canonical JSON, the committed hash, exact arithmetic, presentation counts,
and the non-authorizing terminal boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


EXPECTED_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
EXPECTED_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
EXPECTED_D = 564_522
EXPECTED_M = 16
EXPECTED_DELTA = 10
EXPECTED_FACTORS = (2, 3, 7, 13_441)
EXPECTED_SOURCE_CLAIMS = [
    "SC-GLV-ENDOMORPHISM",
    "SC-GLV-ENDOMORPHISM-NONTRIVIAL",
    "SC-PKC-SMOOTH-SUBGROUP",
    "SC-PKC-RELATION-YIELD",
    "SC-SECP-NO-TWO-TORSION",
    "SC-SECP-PMINUS1-FACTORIZATION",
    "SC-SECP-PRIME-FIELD",
    "SC-SEMAEV-RELATION-SEMANTICS",
]
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]


class Replay:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def expect(self, path: str, actual: Any, expected: Any) -> None:
        if actual != expected:
            self.failures.append(
                f"{path}: expected {expected!r}, observed {actual!r}"
            )

    def require_dict(self, path: str, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            self.failures.append(f"{path}: expected object")
            return {}
        return value

    def require_list(self, path: str, value: Any) -> list[Any]:
        if not isinstance(value, list):
            self.failures.append(f"{path}: expected array")
            return []
        return value


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def independent_gate_count(exponent: int) -> tuple[str, int, int, int]:
    bits_reversed: list[str] = []
    value = exponent
    while value:
        bits_reversed.append(str(value & 1))
        value >>= 1
    bits = "".join(reversed(bits_reversed))
    squarings = len(bits) - 1
    multiplies = sum(int(bit) for bit in bits) - 1
    return bits, squarings, multiplies, squarings + multiplies


def independent_source_factor_chain() -> list[int]:
    """Replay every exponent produced by the four factored binary maps."""
    exponents = [1]
    current = 1
    for factor in EXPECTED_FACTORS:
        source = current
        accumulator = current
        bits = independent_gate_count(factor)[0]
        for bit in bits[1:]:
            accumulator += accumulator
            exponents.append(accumulator)
            if bit == "1":
                accumulator += source
                exponents.append(accumulator)
        current = accumulator
    return exponents


def exact_macaulay_counts(
    variables: int, degrees: list[int], cutoff: int
) -> tuple[int, int, int]:
    columns = math.comb(variables + cutoff, cutoff)
    rows = 0
    for degree in degrees:
        if degree <= cutoff:
            rows += math.comb(variables + cutoff - degree, cutoff - degree)
    return columns, rows, columns * rows * 32


def get(
    mapping: dict[str, Any], key: str, path: str, replay: Replay
) -> Any:
    if key not in mapping:
        replay.failures.append(f"{path}.{key}: missing")
        return None
    return mapping[key]


def check_hash(
    artifact_bytes: bytes, hash_path: Path, replay: Replay
) -> None:
    try:
        hash_text = hash_path.read_text(encoding="ascii")
    except (FileNotFoundError, UnicodeDecodeError) as error:
        replay.failures.append(f"artifact.sha256 unreadable: {error}")
        return
    match = re.fullmatch(r"([0-9a-f]{64})  artifact\.json\n", hash_text)
    if match is None:
        replay.failures.append("artifact.sha256 has noncanonical format")
        return
    replay.expect(
        "artifact.sha256",
        match.group(1),
        hashlib.sha256(artifact_bytes).hexdigest(),
    )


def check_metadata(document: dict[str, Any], replay: Replay) -> None:
    replay.expect("schema_version", document.get("schema_version"), "1.0")
    replay.expect(
        "artifact_id",
        document.get("artifact_id"),
        "PKC-SMOOTH-M16-SYMBOLIC-DESK-001",
    )
    replay.expect(
        "kind",
        document.get("kind"),
        "deterministic_nonexperimental_symbolic_desk",
    )
    inputs = replay.require_dict("inputs", document.get("inputs"))
    replay.expect("inputs.p", inputs.get("p"), str(EXPECTED_P))
    replay.expect("inputs.n", inputs.get("n"), str(EXPECTED_N))
    replay.expect("inputs.D", inputs.get("D"), EXPECTED_D)
    replay.expect("inputs.m", inputs.get("m"), EXPECTED_M)
    replay.expect(
        "inputs.factor_chain",
        inputs.get("factor_chain"),
        list(EXPECTED_FACTORS),
    )
    replay.expect(
        "inputs.delta_from_source",
        inputs.get("delta_from_source"),
        EXPECTED_DELTA,
    )
    replay.expect(
        "inputs.bytes_per_field_element_for_conditional_dense_models",
        inputs.get("bytes_per_field_element_for_conditional_dense_models"),
        32,
    )
    replay.expect(
        "inputs.target_x_treated_as_fixed_constant",
        inputs.get("target_x_treated_as_fixed_constant"),
        True,
    )
    replay.expect(
        "arithmetic.factor_chain_product",
        math.prod(EXPECTED_FACTORS),
        EXPECTED_D,
    )
    replay.expect(
        "arithmetic.D_divides_p_minus_1",
        (EXPECTED_P - 1) % EXPECTED_D,
        0,
    )
    replay.expect(
        "arithmetic.gcd_D_p",
        math.gcd(EXPECTED_D, EXPECTED_P),
        1,
    )
    replay.expect("arithmetic.three_divides_D", EXPECTED_D % 3, 0)

    scope = replay.require_dict("scope", document.get("scope"))
    excluded = replay.require_list("scope.excluded", scope.get("excluded"))
    for required in (
        "materialized S17 or recursive polynomial system",
        "solver execution",
        "exact-target relation search",
        "discrete-log computation",
        "route promotion or experiment authorization",
        "asymptotic or security claim",
    ):
        if required not in excluded:
            replay.failures.append(f"scope.excluded lacks {required!r}")


def check_source_model(document: dict[str, Any], replay: Replay) -> None:
    model = replay.require_dict(
        "source_cost_model", document.get("source_cost_model")
    )
    yield_record = replay.require_dict(
        "source_cost_model.paper_yield", model.get("paper_yield")
    )
    expected_yield = Fraction(
        EXPECTED_D**EXPECTED_M,
        math.factorial(EXPECTED_M) * EXPECTED_P,
    )
    replay.expect(
        "paper_yield.numerator",
        yield_record.get("numerator"),
        str(expected_yield.numerator),
    )
    replay.expect(
        "paper_yield.denominator",
        yield_record.get("denominator"),
        str(expected_yield.denominator),
    )
    replay.expect(
        "paper_yield.formula",
        yield_record.get("formula"),
        "D^16 / (16! * p)",
    )
    yield_interpretation = yield_record.get("interpretation")
    if not isinstance(yield_interpretation, str) or (
        "not a success probability" not in yield_interpretation
        or "independent-relation rate" not in yield_interpretation
    ):
        replay.failures.append(
            "paper_yield.interpretation must reject success and rank meanings"
        )

    multiplier_record = replay.require_dict(
        "source_cost_model.paper_relation_multiplier",
        model.get("paper_relation_multiplier"),
    )
    multiplier = Fraction(
        math.factorial(EXPECTED_M) * EXPECTED_P,
        EXPECTED_D ** (EXPECTED_M - 1),
    )
    replay.expect(
        "paper_relation_multiplier.numerator",
        multiplier_record.get("numerator"),
        str(multiplier.numerator),
    )
    replay.expect(
        "paper_relation_multiplier.denominator",
        multiplier_record.get("denominator"),
        str(multiplier.denominator),
    )
    replay.expect(
        "paper_relation_multiplier.ceiling",
        multiplier_record.get("ceiling"),
        str((multiplier.numerator + multiplier.denominator - 1)
            // multiplier.denominator),
    )
    replay.expect(
        "paper_relation_multiplier.formula",
        multiplier_record.get("formula"),
        "16! * p / D^15",
    )

    benchmark = math.isqrt(EXPECTED_N)
    if benchmark * benchmark < EXPECTED_N:
        benchmark += 1
    benchmark_record = replay.require_dict(
        "source_cost_model.uncalibrated_generic_reference_ceiling",
        model.get("uncalibrated_generic_reference_ceiling"),
    )
    replay.expect(
        "uncalibrated_generic_reference_ceiling.ceil_sqrt_target_group_order",
        benchmark_record.get("ceil_sqrt_target_group_order"),
        str(benchmark),
    )
    benchmark_scope = benchmark_record.get("scope")
    if not isinstance(benchmark_scope, str) or (
        "not a matched Pollard-rho baseline" not in benchmark_scope
        or "common units" not in benchmark_scope
        or "equal-success" not in benchmark_scope
    ):
        replay.failures.append(
            "uncalibrated reference must reject a matched generic comparison"
        )
    optimistic = replay.require_dict(
        "source_cost_model.optimistic_necessary_per_system_cost",
        model.get("optimistic_necessary_per_system_cost"),
    )
    maximum_t = (
        benchmark * multiplier.denominator - 1
    ) // multiplier.numerator
    replay.expect(
        "optimistic_necessary_per_system_cost.maximum_integer_T",
        optimistic.get("maximum_integer_T"),
        str(maximum_t),
    )
    assumptions = replay.require_list(
        "optimistic_necessary_per_system_cost.assumptions",
        optimistic.get("assumptions"),
    )
    for required in (
        (
            "assume T, field operations, and group operations can be compared "
            "in one common work unit"
        ),
        "ignore the equal-success probability conversion",
    ):
        if required not in assumptions:
            replay.failures.append(
                "optimistic threshold lacks required uncalibrated assumption "
                f"{required!r}"
            )
    optimistic_meaning = optimistic.get("meaning")
    if not isinstance(optimistic_meaning, str) or (
        "uncalibrated" not in optimistic_meaning
        or "does not establish T(E,16,L)" not in optimistic_meaning
        or "matched generic comparison" not in optimistic_meaning
    ):
        replay.failures.append(
            "optimistic threshold meaning overstates the arithmetic ceiling"
        )
    linear_algebra = replay.require_dict(
        "source_cost_model.linear_algebra_term",
        model.get("linear_algebra_term"),
    )
    replay.expect(
        "linear_algebra_term.D_squared",
        linear_algebra.get("D_squared"),
        str(EXPECTED_D**2),
    )
    replay.expect(
        "linear_algebra_term.D_cubed",
        linear_algebra.get("D_cubed"),
        str(EXPECTED_D**3),
    )
    replay.expect(
        "linear_algebra_term.paper_model",
        linear_algebra.get("paper_model"),
        "D^omega with 2 < omega <= 3",
    )
    replay.expect(
        "source_cost_model.total_cost_formula",
        model.get("total_cost_formula"),
        "P(p,16) + (16! * p / D^15) * T(E,16,L) + D^omega",
    )


def check_source_scope(document: dict[str, Any], replay: Replay) -> None:
    source_scope = replay.require_dict(
        "source_scope", document.get("source_scope")
    )
    expected_paths = {
        "factorization_artifact": (
            "experiments/engine/pkc_smooth_desk_screen/artifact.json"
        ),
        "kernel_curve_cardinality": (
            "Ecdlp/Proved/CurveCardinalityExact.lean"
        ),
        "kernel_full_group": "Ecdlp/Proved/CurveFullGroup.lean",
        "kernel_glv_eigenvalue": (
            "Ecdlp/Proved/GlvSubgroupEigenvalue.lean"
        ),
        "kernel_glv_orbits": "Ecdlp/Proved/GlvOrbit.lean",
        "kernel_s3_definition": "Ecdlp/Proved/SemaevThree.lean",
        "primary_claim_extract": (
            "data/source_claim_extracts/petit_kosters_messeng2016.json"
        ),
    }
    for field, expected in expected_paths.items():
        replay.expect(
            f"source_scope.{field}", source_scope.get(field), expected
        )
        if not (REPO_ROOT / expected).is_file():
            replay.failures.append(
                f"source_scope.{field}: referenced repository file is missing"
            )
    expected_theorems = {
        "curve_cardinality": "Ecdlp.Curve.secp256k1_card_point_eq_n",
        "full_group": "Ecdlp.Curve.secp256k1_grp_eq_top",
        "glv_eigenvalue_on_subgroup": (
            "Ecdlp.Curve.secp256k1_glvPoint_eq_lam_on_zmultiples"
        ),
        "glv_nonfixed_orbit_size_three": (
            "Ecdlp.Curve.secp256k1_glvPoint_orbit_three_distinct"
        ),
        "no_nonzero_two_torsion": (
            "Ecdlp.Curve.secp256k1_no_nonzero_two_torsion"
        ),
        "semaev_three_semantics": (
            "Ecdlp.Semaev.secp256k1_semaev_three_iff"
        ),
    }
    replay.expect(
        "source_scope.kernel_theorems",
        source_scope.get("kernel_theorems"),
        expected_theorems,
    )
    locators = replay.require_dict(
        "source_scope.primary_locators",
        source_scope.get("primary_locators"),
    )
    replay.expect(
        "source_scope.primary_locators.delta_and_algorithm",
        locators.get("delta_and_algorithm"),
        "PKC 2016 Section 3.1, Algorithm 1 and paragraph after it",
    )
    replay.expect(
        "source_scope.primary_locators.source_maps",
        locators.get("source_maps"),
        "PKC 2016 Section 3.3",
    )
    replay.expect(
        "source_scope.primary_locators.total_cost",
        locators.get("total_cost"),
        "PKC 2016 Section 3.2",
    )
    replay.expect(
        "source_scope.source_claim_ids",
        source_scope.get("source_claim_ids"),
        EXPECTED_SOURCE_CLAIMS,
    )
    try:
        typed_evidence = json.loads(
            (REPO_ROOT / "repo/ECDLP_TYPED_EVIDENCE_V0.json").read_text(
                encoding="utf-8"
            )
        )
        registered_claim_ids = {
            item.get("id")
            for item in typed_evidence.get("source_claims", [])
            if isinstance(item, dict)
        }
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError) as error:
        replay.failures.append(f"typed evidence registry unreadable: {error}")
    else:
        missing_claim_ids = sorted(
            set(EXPECTED_SOURCE_CLAIMS) - registered_claim_ids
        )
        if missing_claim_ids:
            replay.failures.append(
                "source_scope.source_claim_ids are absent from typed evidence: "
                + ", ".join(missing_claim_ids)
            )


def check_envelope(
    path: str,
    representation: dict[str, Any],
    variables: int,
    degrees: list[int],
    cutoff: int,
    expected_degree_profile_assumption: str,
    replay: Replay,
) -> None:
    envelope = replay.require_dict(
        f"{path}.macaulay_cutoff_envelope",
        representation.get("macaulay_cutoff_envelope"),
    )
    columns, rows, dense_bytes = exact_macaulay_counts(
        variables, degrees, cutoff
    )
    replay.expect(
        f"{path}.macaulay.variable_count",
        envelope.get("variable_count"),
        variables,
    )
    replay.expect(
        f"{path}.macaulay.cutoff",
        envelope.get("cutoff_total_degree"),
        cutoff,
    )
    replay.expect(
        f"{path}.macaulay.columns",
        envelope.get("column_monomials_through_cutoff"),
        str(columns),
    )
    replay.expect(
        f"{path}.macaulay.rows",
        envelope.get("equation_multiple_templates_before_deduplication"),
        str(rows),
    )
    replay.expect(
        f"{path}.macaulay.dense_bytes",
        envelope.get("dense_byte_capacity_if_every_cell_is_stored"),
        str(dense_bytes),
    )
    replay.expect(
        f"{path}.macaulay.bytes_per_dense_field_element",
        envelope.get("bytes_per_dense_field_element"),
        32,
    )
    replay.expect(
        f"{path}.macaulay.degree_profile_assumption",
        envelope.get("degree_profile_assumption"),
        expected_degree_profile_assumption,
    )
    interpretation = envelope.get("interpretation")
    if not isinstance(interpretation, str) or (
        "not" not in interpretation and "neither" not in interpretation
    ):
        replay.failures.append(
            f"{path}.macaulay interpretation must reject a solver bound"
        )


def check_representations(
    document: dict[str, Any], replay: Replay
) -> None:
    representations = replay.require_dict(
        "representations", document.get("representations")
    )
    direct = replay.require_dict(
        "representations.direct",
        representations.get("direct_s17_with_source_factor_chain"),
    )
    replay.expect("direct.variable_count", direct.get("variable_count"), 64)
    replay.expect("direct.equation_count", direct.get("equation_count"), 65)
    replay.expect(
        "direct.maximum_input_equation_degree",
        direct.get("maximum_input_equation_degree"),
        524_288,
    )
    direct_relation = replay.require_dict(
        "direct.relation", direct.get("relation")
    )
    replay.expect(
        "direct.relation.per_leaf_variable_degree",
        direct_relation.get("per_leaf_variable_degree"),
        32_768,
    )
    replay.expect(
        "direct.relation.polynomial",
        direct_relation.get("polynomial"),
        "S_17",
    )
    replay.expect(
        "direct.relation.target_specialized_total_degree_upper_bound",
        direct_relation.get("target_specialized_total_degree_upper_bound"),
        524_288,
    )
    replay.expect(
        "direct.relation.actual_expanded_support",
        direct_relation.get("actual_expanded_support"),
        None,
    )
    replay.expect(
        "direct.relation.dense_box_support_capacity_upper_bound",
        direct_relation.get("dense_box_support_capacity_upper_bound"),
        str((32_768 + 1) ** 16),
    )
    direct_membership = replay.require_dict(
        "direct.membership", direct.get("membership")
    )
    replay.expect(
        "direct.membership.equation_count",
        direct_membership.get("equation_count"),
        64,
    )
    replay.expect(
        "direct.membership.intermediate_variable_count",
        direct_membership.get("intermediate_variable_count"),
        48,
    )
    replay.expect(
        "direct.membership.map_degrees",
        direct_membership.get("map_degrees"),
        list(EXPECTED_FACTORS),
    )
    replay.expect(
        "direct.membership.term_occurrences",
        direct_membership.get("term_occurrences"),
        128,
    )
    check_envelope(
        "direct",
        direct,
        64,
        [524_288] + list(EXPECTED_FACTORS) * 16,
        524_288,
        (
            "Conditional on assigning the target-specialized S17 relation "
            "total degree 524288. The committed evidence provides this value "
            "as an upper bound; if specialization lowers the degree, the "
            "row-template count changes and this count is not a bound for "
            "that different profile."
        ),
        replay,
    )

    recursive_source = replay.require_dict(
        "representations.recursive_source",
        representations.get("recursive_s3_with_source_factor_chain"),
    )
    replay.expect(
        "recursive_source.variable_count",
        recursive_source.get("variable_count"),
        78,
    )
    replay.expect(
        "recursive_source.equation_count",
        recursive_source.get("equation_count"),
        79,
    )
    replay.expect(
        "recursive_source.maximum_input_equation_degree",
        recursive_source.get("maximum_input_equation_degree"),
        13_441,
    )
    check_envelope(
        "recursive_source",
        recursive_source,
        78,
        [4] * 15 + list(EXPECTED_FACTORS) * 16,
        13_441,
        (
            "Exact input-degree profile for 15 quartic S3 equations and 16 "
            "copies of the degree-2, 3, 7, 13441 source chain."
        ),
        replay,
    )
    source_membership = replay.require_dict(
        "recursive_source.membership",
        recursive_source.get("membership"),
    )
    replay.expect(
        "recursive_source.membership.equation_count",
        source_membership.get("equation_count"),
        64,
    )
    replay.expect(
        "recursive_source.membership.intermediate_variable_count",
        source_membership.get("intermediate_variable_count"),
        48,
    )
    replay.expect(
        "recursive_source.membership.map_degrees",
        source_membership.get("map_degrees"),
        list(EXPECTED_FACTORS),
    )
    replay.expect(
        "recursive_source.membership.term_occurrences",
        source_membership.get("term_occurrences"),
        128,
    )
    source_relation = replay.require_dict(
        "recursive_source.relation", recursive_source.get("relation")
    )
    expected_relation = {
        "equation_count": 15,
        "internal_variable_count": 14,
        "maximum_term_occurrences": 135,
        "nonconstant_x_variable_count": 30,
        "target_zero_term_occurrences": 129,
        "total_degree": 4,
    }
    for field, expected in expected_relation.items():
        replay.expect(
            f"recursive_source.relation.{field}",
            source_relation.get(field),
            expected,
        )
    source_terms = replay.require_dict(
        "recursive_source.term_occurrences",
        recursive_source.get("term_occurrences"),
    )
    replay.expect(
        "recursive_source.term_occurrences.symbolic",
        source_terms.get("target_nonzero_or_symbolic"),
        263,
    )
    replay.expect(
        "recursive_source.term_occurrences.target_zero",
        source_terms.get("target_zero"),
        257,
    )

    recursive_circuit = replay.require_dict(
        "representations.recursive_circuit",
        representations.get(
            "recursive_s3_with_quadratic_source_factor_circuit"
        ),
    )
    replay.expect(
        "recursive_circuit.variable_count",
        recursive_circuit.get("variable_count"),
        398,
    )
    replay.expect(
        "recursive_circuit.equation_count",
        recursive_circuit.get("equation_count"),
        399,
    )
    replay.expect(
        "recursive_circuit.maximum_input_equation_degree",
        recursive_circuit.get("maximum_input_equation_degree"),
        4,
    )
    membership = replay.require_dict(
        "recursive_circuit.membership_circuit",
        recursive_circuit.get("membership_circuit"),
    )
    profile = replay.require_list(
        "recursive_circuit.membership_circuit.map_profile",
        membership.get("map_profile"),
    )
    replay.expect(
        "recursive_circuit.membership_circuit.map_profile.length",
        len(profile),
        len(EXPECTED_FACTORS),
    )
    expected_gates = 0
    for index, exponent in enumerate(EXPECTED_FACTORS):
        if index >= len(profile) or not isinstance(profile[index], dict):
            replay.failures.append(f"map_profile[{index}] missing")
            continue
        bits, squarings, multiplies, gates = independent_gate_count(exponent)
        expected_gates += gates
        replay.expect(
            f"map_profile[{index}].exponent",
            profile[index].get("exponent"),
            exponent,
        )
        replay.expect(
            f"map_profile[{index}].binary",
            profile[index].get("binary"),
            bits,
        )
        replay.expect(
            f"map_profile[{index}].squarings",
            profile[index].get("squarings"),
            squarings,
        )
        replay.expect(
            f"map_profile[{index}].nonsquare_multiplications",
            profile[index].get("nonsquare_multiplications"),
            multiplies,
        )
        replay.expect(
            f"map_profile[{index}].gate_count",
            profile[index].get("gate_count"),
            gates,
        )
        replay.expect(
            f"map_profile[{index}].bit_length",
            profile[index].get("bit_length"),
            len(bits),
        )
        replay.expect(
            f"map_profile[{index}].popcount",
            profile[index].get("popcount"),
            bits.count("1"),
        )
    replay.expect(
        "recursive_circuit.gate_count_per_coordinate",
        membership.get("gate_count_per_coordinate"),
        expected_gates,
    )
    replay.expect(
        "recursive_circuit.membership_equations",
        membership.get("equation_count"),
        16 * expected_gates,
    )
    replay.expect(
        "recursive_circuit.membership_auxiliaries",
        membership.get("auxiliary_variable_count"),
        16 * (expected_gates - 1),
    )
    replay.expect(
        "recursive_circuit.membership_term_occurrences",
        membership.get("term_occurrences"),
        2 * 16 * expected_gates,
    )
    replay.expect(
        "recursive_circuit.generic_multiplication_lower_bound",
        membership.get(
            "generic_multiplication_only_lower_bound_for_x_to_D"
        ),
        (EXPECTED_D - 1).bit_length(),
    )
    replay.expect(
        "recursive_circuit.addition_chain",
        membership.get("addition_chain_exponents_including_input_one"),
        independent_source_factor_chain(),
    )
    replay.expect(
        "recursive_circuit.addition_chain_terminal",
        independent_source_factor_chain()[-1],
        EXPECTED_D,
    )
    replay.expect(
        "recursive_circuit.pointwise_membership_equivalence",
        membership.get("pointwise_membership_equivalence"),
        (
            "The triangular circuit has unique intermediates and terminates "
            "at x^D = 1."
        ),
    )
    check_envelope(
        "recursive_circuit",
        recursive_circuit,
        398,
        [4] * 15 + [2] * 384,
        4,
        (
            "Exact input-degree profile for 15 quartic S3 equations and 384 "
            "quadratic circuit equations."
        ),
        replay,
    )
    circuit_relation = replay.require_dict(
        "recursive_circuit.relation", recursive_circuit.get("relation")
    )
    for field, expected in expected_relation.items():
        replay.expect(
            f"recursive_circuit.relation.{field}",
            circuit_relation.get(field),
            expected,
        )
    scope_boundary = recursive_circuit.get("scope_boundary")
    if not isinstance(scope_boundary, str) or (
        "not established" not in scope_boundary
        or "exceptional fibers" not in scope_boundary
        or "saturation" not in scope_boundary
    ):
        replay.failures.append(
            "recursive circuit must preserve the equivalence boundary"
        )
    circuit_terms = replay.require_dict(
        "recursive_circuit.term_occurrences",
        recursive_circuit.get("term_occurrences"),
    )
    replay.expect(
        "recursive_circuit.term_occurrences.symbolic",
        circuit_terms.get("target_nonzero_or_symbolic"),
        903,
    )
    replay.expect(
        "recursive_circuit.term_occurrences.target_zero",
        circuit_terms.get("target_zero"),
        897,
    )


def check_factor_base_and_recovery(
    document: dict[str, Any], replay: Replay
) -> None:
    layer = replay.require_dict(
        "factor_base_and_linear_algebra",
        document.get("factor_base_and_linear_algebra"),
    )
    membership = replay.require_dict(
        "factor_base.exact_membership_layer",
        layer.get("exact_membership_layer"),
    )
    replay.expect(
        "factor_base.membership.root_count",
        membership.get("root_count"),
        EXPECTED_D,
    )
    replay.expect(
        "factor_base.membership.square_free",
        membership.get("square_free"),
        True,
    )
    replay.expect(
        "factor_base.membership.denominator_components",
        membership.get("denominator_components"),
        0,
    )
    replay.expect(
        "factor_base.membership.group",
        membership.get("group"),
        "H = {x in F_p^* : x^D = 1}",
    )
    replay.expect(
        "factor_base.membership.polynomial",
        membership.get("membership_polynomial"),
        "x^D - 1",
    )
    replay.expect(
        "factor_base.membership.square_free_reason",
        membership.get("square_free_reason"),
        "D divides p-1, so p does not divide D.",
    )
    lift_count = replay.require_dict(
        "factor_base.lift_count", layer.get("lift_count")
    )
    replay.expect(
        "factor_base.lift_count.character_sum",
        lift_count.get("character_sum"),
        "S_H = sum_{x in H} chi(x^3 + 7)",
    )
    replay.expect(
        "factor_base.lift_count.compressed_character_sum",
        lift_count.get("compressed_character_sum"),
        "S_H = 3 * sum_{z in H^3} chi(z + 7)",
    )
    replay.expect(
        "factor_base.lift_count.coordinate_roots_with_curve_lifts",
        lift_count.get("coordinate_roots_with_curve_lifts"),
        "U = (D + S_H)/2",
    )
    replay.expect(
        "factor_base.lift_count.signed_factor_base_points",
        lift_count.get("signed_factor_base_points"),
        "2U = D + S_H",
    )
    replay.expect(
        "factor_base.lift_count.rational_two_torsion_roots",
        lift_count.get("rational_two_torsion_roots"),
        0,
    )
    replay.expect(
        "factor_base.lift_count.status",
        lift_count.get("status"),
        "unknown_without_character_sum_evaluation",
    )
    glv = replay.require_dict(
        "factor_base.glv_orbit_accounting",
        layer.get("glv_orbit_accounting"),
    )
    replay.expect(
        "factor_base.glv.coordinate_log_columns_after_negation",
        glv.get("coordinate_log_columns_after_negation"),
        "U",
    )
    replay.expect(
        "factor_base.glv.glv_aware_factor_log_columns",
        glv.get("glv_aware_factor_log_columns"),
        "U/3",
    )
    glv_justification = glv.get("justification")
    if not isinstance(glv_justification, str) or (
        "3 divides D" not in glv_justification
        or "order-three beta lies in H" not in glv_justification
        or "known GLV-related logarithms" not in glv_justification
    ):
        replay.failures.append(
            "factor_base.glv.justification lacks the orbit prerequisites"
        )
    glv_scope = glv.get("scope")
    if not isinstance(glv_scope, str) or (
        "not" not in glv_scope or "rank result" not in glv_scope
    ):
        replay.failures.append(
            "factor_base.glv.scope must reject a rank conclusion"
        )
    sparse = replay.require_dict(
        "factor_base.source_nominal_sparse_model",
        layer.get("source_nominal_sparse_model"),
    )
    replay.expect(
        "factor_base.nominal_rows",
        sparse.get("nominal_relation_rows_D_plus_delta"),
        EXPECTED_D + EXPECTED_DELTA,
    )
    replay.expect(
        "factor_base.nominal_occurrences",
        sparse.get("nominal_factor_entry_occurrences_upper_bound"),
        (EXPECTED_D + EXPECTED_DELTA) * EXPECTED_M,
    )
    replay.expect(
        "factor_base.nominal_unknown_columns",
        sparse.get("nominal_unknown_columns_D"),
        EXPECTED_D,
    )
    replay.expect(
        "factor_base.nominal_factor_entries",
        sparse.get("factor_entries_per_relation_upper_bound"),
        EXPECTED_M,
    )
    replay.expect(
        "factor_base.delta_is_not_rank_theorem",
        sparse.get("delta_is_a_priori_not_a_rank_theorem"),
        True,
    )
    warning = sparse.get("warning")
    if not isinstance(warning, str) or (
        "conditional" not in warning
        or "rank remain unresolved" not in warning
        or "GLV" not in warning
    ):
        replay.failures.append(
            "factor-base sparse model must preserve its conditional boundary"
        )

    recovery = replay.require_dict("recovery", document.get("recovery"))
    replay.expect(
        "recovery.coordinate_target_relative_sign_classes",
        recovery.get("coordinate_target_relative_sign_classes"),
        1 << 15,
    )
    direct = replay.require_dict(
        "recovery.direct_presentation", recovery.get("direct_presentation")
    )
    replay.expect(
        "recovery.direct.raw_factor_sign_assignments",
        direct.get("raw_factor_sign_assignments"),
        1 << 16,
    )
    replay.expect(
        "recovery.direct.meet_in_the_middle_list_sizes",
        direct.get(
            "meet_in_the_middle_list_sizes_after_fixing_one_global_sign"
        ),
        [1 << 7, 1 << 8],
    )
    required_final_check = direct.get("required_final_check")
    if not isinstance(required_final_check, str) or (
        "full elliptic-curve relation exactly" not in required_final_check
        or "either sign" not in required_final_check
        or "coefficient sign" not in required_final_check
    ):
        replay.failures.append(
            "direct recovery must require exact curve and sign verification"
        )
    recursive = replay.require_dict(
        "recovery.recursive_presentation",
        recovery.get("recursive_presentation"),
    )
    replay.expect(
        "recovery.recursive.status", recursive.get("status"), "unresolved"
    )
    replay.expect(
        "recovery.recursive.unresolved_items",
        recursive.get("unresolved_items"),
        [
            "partial sums at the point at infinity",
            "tangent and repeated-coordinate fibers",
            "extension-field lifts rejected by F_p recovery",
            "compatibility of local S3 sign choices across the tree",
            "permutation and duplicate-root multiplicities",
        ],
    )


def check_terminal(document: dict[str, Any], replay: Replay) -> None:
    terminal = replay.require_dict(
        "terminal_disposition", document.get("terminal_disposition")
    )
    expected = {
        "scientific_disposition": "scoped_blocker",
        "retention_disposition": "zero_retention_success",
        "cost_quantity_transition": "missing_to_partial",
        "cell_transition": "open_to_open",
        "route_effect": "none",
        "hypothesis_effect": "none",
        "authorization": "none",
        "calibration": "excluded_nonexperimental",
        "assurance": "certificate_replayed",
        "source_independence": "not_established",
    }
    for field, value in expected.items():
        replay.expect(
            f"terminal_disposition.{field}", terminal.get(field), value
        )
    reopening = replay.require_list(
        "terminal_disposition.reopening_conditions",
        terminal.get("reopening_conditions"),
    )
    replay.expect(
        "terminal_disposition.reopening_conditions",
        reopening,
        [
            (
                "Prove a source-faithful direct/recursive/circuit bridge "
                "including saturation and exceptional fibers."
            ),
            (
                "Determine usable F_p lifts, recovery multiplicities, and "
                "independent-relation rank under negation and GLV orbits."
            ),
            (
                "Bound solving degree, fill-in, online/offline work, memory, "
                "preprocessing, sparse linear algebra, money, and review "
                "effort against the matched generic baseline."
            ),
        ],
    )
    unresolved = replay.require_list(
        "unresolved_complete_cost_fields",
        document.get("unresolved_complete_cost_fields"),
    )
    replay.expect(
        "unresolved_complete_cost_fields",
        unresolved,
        [
            "actual expanded S17 support",
            "full recursive/direct equivalence after saturation",
            "exceptional components and extension-field fibers",
            "usable factor-base cardinality U",
            "solving degree and Macaulay fill-in",
            "recovery success and multiplicity distribution",
            "independent-relation probability and rank",
            "preprocessing and amortization",
            "sparse linear-algebra time and storage",
            (
                "total online/offline work, memory, money, and reviewer "
                "effort"
            ),
        ],
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, default=HERE / "artifact.json")
    parser.add_argument(
        "--hash-file", type=Path, default=HERE / "artifact.sha256"
    )
    args = parser.parse_args()

    replay = Replay()
    try:
        artifact_bytes = args.artifact.read_bytes()
        document = json.loads(artifact_bytes)
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError) as error:
        print(f"ERROR: artifact unreadable: {error}", file=sys.stderr)
        return 1
    if not isinstance(document, dict):
        print("ERROR: artifact root must be an object", file=sys.stderr)
        return 1
    if artifact_bytes != canonical_bytes(document):
        replay.failures.append("artifact.json is not canonical JSON")
    check_hash(artifact_bytes, args.hash_file, replay)
    check_metadata(document, replay)
    check_source_model(document, replay)
    check_source_scope(document, replay)
    check_representations(document, replay)
    check_factor_base_and_recovery(document, replay)
    check_terminal(document, replay)

    if replay.failures:
        for failure in replay.failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    print("independent M16 symbolic desk replay passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
