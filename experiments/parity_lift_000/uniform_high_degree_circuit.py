#!/usr/bin/env python3
"""Exact circuit-cost replay for UNIFORM-ORIENTED-ROOT-CIRCUIT-056, track C.

The script does not implement curve arithmetic. It consumes the frozen package
046 replay, checks its exact oriented-root certificates, and independently
constructs uniform binary straight-line programs for high-degree monomials.
This separates the degree question from the mandatory generator-orientation
question without duplicating the existing elliptic-curve engine.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Literal

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Operation = Literal["square", "multiply_input"]


def binary_program(exponent: int) -> list[Operation]:
    if exponent < 1:
        raise ValueError("positive exponent required")
    program: list[Operation] = []
    for bit in f"{exponent:b}"[1:]:
        program.append("square")
        if bit == "1":
            program.append("multiply_input")
    return program


def replay_exponent(program: list[Operation]) -> int:
    exponent = 1
    for operation in program:
        exponent = 2 * exponent if operation == "square" else exponent + 1
    return exponent


def ledger(preprocessing: int, advice: int, memory: int, representation: int, online: int) -> dict[str, int]:
    row = {
        "preprocessing": preprocessing,
        "advice": advice,
        "memory": memory,
        "representation": representation,
        "online": online,
    }
    return {**row, "total": sum(row.values())}


def audit_exponent(label: str, exponent: int) -> dict[str, object]:
    program = binary_program(exponent)
    if replay_exponent(program) != exponent:
        raise AssertionError(f"binary replay failed for {label}")
    bits = exponent.bit_length()
    expected = bits - 1 + exponent.bit_count() - 1
    if len(program) != expected:
        raise AssertionError("binary instruction count formula failed")
    return {
        "label": label,
        "exponent": exponent,
        "degree": exponent,
        "bit_length": bits,
        "popcount": exponent.bit_count(),
        "squarings": program.count("square"),
        "multiply_input": program.count("multiply_input"),
        "instruction_count": len(program),
        "replay_exact": True,
        "streamed_ledger": ledger(0, 0, 2, bits, len(program)),
        "materialized_ledger": ledger(bits, 0, 2, len(program), len(program)),
        "generator_sensitive": False,
        "g_to_neg_g_code_change": False,
        "passes_oriented_root_gate": False,
    }


def load_oriented_root_certificates(path: Path) -> list[dict[str, object]]:
    data = json.loads(path.read_text())
    if data.get("package") != "ORIENTED-PARITY-DIVISOR-CIRCUIT-046":
        raise AssertionError("unexpected predecessor package")
    aggregate = data["aggregate"]
    required = (
        "all_square_root_congruences_passed",
        "all_parity_decoders_exact",
        "all_generator_orbits_distinct",
        "all_negations_global",
        "all_scalar_factorizations_exact",
        "all_toy_oriented_sqrts_maximal_degree",
    )
    if not all(aggregate[name] for name in required):
        raise AssertionError("predecessor frozen certificate failed")
    certificates = []
    for case in data["cases"]:
        if case["oriented_sqrt_degree"] != case["kummer_pairs"] - 1:
            raise AssertionError("toy oriented root lost maximal degree")
        if case["generator_oriented_roots"] != case["order"] - 1:
            raise AssertionError("marked-generator orbit was incomplete")
        if not case["negating_generator_negates_orientation"]:
            raise AssertionError("G -> -G did not negate the root")
        certificates.append({
            "field_prime": case["field_prime"],
            "order": case["order"],
            "generator": case["generator"],
            "half_kernel_size": case["kummer_pairs"],
            "oriented_root_degree": case["oriented_sqrt_degree"],
            "maximal_interpolation_degree": case["oriented_sqrt_has_maximal_interpolation_degree"],
            "parity_checks": case["parity_checks"],
            "generator_orientations": case["generator_oriented_roots"],
            "g_to_neg_g_action": "global root negation",
        })
    return certificates


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--oriented-root-results", type=Path, required=True)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("uniform_high_degree_circuit_results.json"),
    )
    args = parser.parse_args()

    n = SECP_N
    middle = (n - 1) // 2
    exponent_audits = [
        audit_exponent("power_of_two_2^255", 1 << 255),
        audit_exponent("secp256k1_order_n", n),
        audit_exponent("half_kernel_scale_M", middle),
        audit_exponent("maximal_Y_G_degree_scale_M_minus_1", middle - 1),
    ]
    certificates = load_oriented_root_certificates(args.oriented_root_results)
    maximal = next(
        item for item in exponent_audits
        if item["label"] == "maximal_Y_G_degree_scale_M_minus_1"
    )
    sqrt_n = math.isqrt(n)
    payload = {
        "package": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
        "track": "C: uniform high-degree straight-line circuits",
        "exact_result": (
            "degree alone gives only a logarithmic arithmetic-circuit barrier; "
            "uniform repeated squaring attains degree 2^s in s instructions"
        ),
        "degree_envelope": {
            "initial_degree_cap": 1,
            "per_binary_gate_rule": "D_(s+1) <= 2 D_s",
            "conclusion": "D_s <= 2^s",
            "degree_only_gate_lower_bound": "s >= ceil(log2 degree)",
            "tight_on_power_of_two_monomials": True,
        },
        "secp256k1": {
            "n": n,
            "n_bit_length": n.bit_length(),
            "M": middle,
            "M_minus_1": middle - 1,
            "sqrt_n_floor": sqrt_n,
            "binary_program_for_M_minus_1": maximal,
            "program_is_below_sqrt_n": maximal["materialized_ledger"]["total"] < sqrt_n,
            "warning": (
                "this is only a same-degree monomial witness; it is not Y_G "
                "and fails the marked-generator orientation gate"
            ),
        },
        "exponent_audits": exponent_audits,
        "predecessor_oriented_root_certificates": certificates,
        "aggregate": {
            "all_binary_programs_replay_exactly": all(item["replay_exact"] for item in exponent_audits),
            "all_high_degree_witnesses_fail_orientation_gate": all(
                not item["passes_oriented_root_gate"] for item in exponent_audits
            ),
            "all_predecessor_parity_certificates_passed": True,
            "all_predecessor_roots_maximal_degree": all(
                case["maximal_interpolation_degree"] for case in certificates
            ),
            "predecessor_certificate_count": len(certificates),
            "evaluator_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "scoped_conclusion": (
            "Track C closes degree-only and explicit-table arguments as routes to a general no-go. "
            "A positive Y_G circuit remains possible only if its uniformly generated code is "
            "marked-generator-sensitive and its full charged representation stays below the target budget."
        ),
    }
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps({
        "M_minus_1_bit_length": (middle - 1).bit_length(),
        "M_minus_1_binary_instructions": maximal["instruction_count"],
        "M_minus_1_materialized_total": maximal["materialized_ledger"]["total"],
        "sqrt_n_floor_bit_length": sqrt_n.bit_length(),
    }, indent=2))


if __name__ == "__main__":
    main()
