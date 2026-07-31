#!/usr/bin/env python3
"""Generate the exact nonsplit-torus applicability desk screen.

The script performs integer arithmetic only.  It neither constructs an ECDLP
solver nor authorizes an experiment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


P = (1 << 256) - (1 << 32) - 977
Q23 = 7_322_137
Q46 = 45_422_601_869_677
REMAINING_COFACTOR = (
    21_759_506_893_163_426_790_183_529_804_034_058_295_931_507_131_047_955_271
)
KNOWN_FACTOR_POWERS = ((2, 4), (Q23, 1), (Q46, 1))
M_VALUES = range(2, 21)
CONSERVATIVE_LINEAR_ALGEBRA_CAP = 1 << 126

HERE = Path(__file__).resolve().parent
ARTIFACT_PATH = HERE / "artifact.json"
HASH_PATH = HERE / "artifact.sha256"


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("ascii")


def ceil_div(numerator: int, denominator: int) -> int:
    return (numerator + denominator - 1) // denominator


def ceil_nth_root(value: int, exponent: int) -> int:
    if value < 0 or exponent <= 0:
        raise ValueError("invalid root arguments")
    if value <= 1:
        return value
    low = 0
    high = 1 << ceil_div(value.bit_length(), exponent)
    while low + 1 < high:
        middle = (low + high) // 2
        if middle**exponent >= value:
            high = middle
        else:
            low = middle
    return high


def is_prime_u64(value: int) -> bool:
    """Deterministic Miller-Rabin for unsigned 64-bit integers."""
    if value < 2:
        return False
    for prime in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if value % prime == 0:
            return value == prime
    odd_part = value - 1
    twos = 0
    while odd_part % 2 == 0:
        odd_part //= 2
        twos += 1
    for base in (2, 325, 9_375, 28_178, 450_775, 9_780_504, 1_795_265_022):
        if base % value == 0:
            continue
        residue = pow(base, odd_part, value)
        if residue in (1, value - 1):
            continue
        for _ in range(twos - 1):
            residue = pow(residue, 2, value)
            if residue == value - 1:
                break
        else:
            return False
    return True


def known_divisors() -> list[int]:
    divisors = [1]
    for prime, exponent in KNOWN_FACTOR_POWERS:
        powers = [prime**power for power in range(exponent + 1)]
        divisors = [left * right for left in divisors for right in powers]
    return sorted(set(divisors))


def trace_root_count(group_order: int) -> int:
    """Number of inversion orbits in a cyclic group of this order."""
    return (group_order + math.gcd(group_order, 2)) // 2


def largest_power_of_two_divisor(value: int) -> int:
    divisor = 1
    while value % 2 == 0:
        divisor *= 2
        value //= 2
    return divisor


def prime_steps(group_order: int) -> list[int]:
    return [prime for prime, _ in KNOWN_FACTOR_POWERS if group_order % prime == 0]


def build_row(m: int, divisors: list[int]) -> dict[str, Any]:
    threshold = ceil_nth_root(math.factorial(m) * P, m)
    candidates: list[tuple[int, int]] = []
    for order in divisors:
        root_count = trace_root_count(order)
        if (
            root_count >= threshold
            and root_count**2 <= CONSERVATIVE_LINEAR_ALGEBRA_CAP
        ):
            candidates.append((root_count, order))

    if not candidates:
        return {
            "m": m,
            "paper_balance_threshold": str(threshold),
            "size_and_conservative_linear_algebra_screen": "no_candidate",
            "selected": None,
        }

    root_count, order = min(candidates)
    steps = prime_steps(order)
    return {
        "m": m,
        "paper_balance_threshold": str(threshold),
        "size_and_conservative_linear_algebra_screen": "candidate_exists",
        "selected": {
            "group_order": str(order),
            "trace_root_count": str(root_count),
            "yield_margin": str(root_count - threshold),
            "prime_degree_steps": steps,
            "maximum_prime_degree_step": max(steps),
            "nominal_linear_algebra_work": str(root_count**2),
        },
    }


def build_artifact() -> dict[str, Any]:
    divisors = known_divisors()
    rows = [build_row(m, divisors) for m in M_VALUES]
    surviving = [
        row["m"]
        for row in rows
        if row["size_and_conservative_linear_algebra_screen"]
        == "candidate_exists"
    ]

    p_plus_one_product = (
        (2**4) * Q23 * Q46 * REMAINING_COFACTOR
    )
    if p_plus_one_product != P + 1:
        raise AssertionError("p+1 factorization identity failed")
    if not is_prime_u64(Q23) or not is_prime_u64(Q46):
        raise AssertionError("displayed finite factors must be prime")

    return {
        "schema_version": "1.0",
        "artifact_id": "PKC-NONSPLIT-TORUS-DESK-SCREEN-001",
        "kind": "deterministic_desk_arithmetic",
        "inputs": {
            "p": str(P),
            "p_formula": "2^256 - 2^32 - 977",
            "m_min": min(M_VALUES),
            "m_max": max(M_VALUES),
            "conservative_linear_algebra_cap": str(
                CONSERVATIVE_LINEAR_ALGEBRA_CAP
            ),
        },
        "p_plus_one_factorization": {
            "identity": (
                "p + 1 = 2^4 * 7322137 * 45422601869677 * "
                "21759506893163426790183529804034058295931507131047955271"
            ),
            "identity_replayed": True,
            "largest_power_of_two_divisor": largest_power_of_two_divisor(P + 1),
            "largest_power_of_two_trace_root_count": trace_root_count(
                largest_power_of_two_divisor(P + 1)
            ),
            "known_factor_powers": [
                {"prime": prime, "exponent": exponent}
                for prime, exponent in KNOWN_FACTOR_POWERS
            ],
            "finite_factor_primality": {
                str(Q23): "deterministic_u64_miller_rabin_pass",
                str(Q46): "deterministic_u64_miller_rabin_pass",
            },
            "remaining_cofactor": str(REMAINING_COFACTOR),
            "remaining_cofactor_primality": "not_claimed_by_this_artifact",
            "known_divisors_excluding_remaining_cofactor": [
                str(value) for value in divisors
            ],
        },
        "trace_model": {
            "torus": "T(F_p) = {alpha in F_(p^2)^* : alpha^(p+1) = 1}",
            "coordinate": "t(alpha) = alpha + alpha^(-1)",
            "identification": "t(alpha) = t(alpha^(-1))",
            "root_count_formula": "(|H| + gcd(|H|,2))/2",
            "dickson_identity": (
                "D_d(t(alpha),1) - 2 = alpha^d + alpha^(-d) - 2"
            ),
            "multiplicity_boundary": (
                "D_d(x,1)-2 has degree d but only "
                "(d+gcd(d,2))/2 distinct trace roots; non-endpoint roots "
                "are repeated. A radical presentation and recovery contract "
                "are separate obligations."
            ),
        },
        "prior_art": {
            "classification": "confirmed_prior_art",
            "source_claim_id": "SC-WCC2017-PPLUS1-TRACE-EXTENSION",
            "source_id": "yokota_kudo_yasuda2017_wcc",
            "locator": "Section 4.1, equations (9)-(10); Section 4.2; Section 5",
            "scope": (
                "The source already constructs a p-plus-one nonsplit-torus "
                "root-of-unity trace factor base. Its implemented low-degree "
                "variant uses N=2^r and m=2; it does not validate the submitted "
                "large-prime m=6,7 instantiation."
            ),
        },
        "smooth_composition_screen": {
            "pkc_source_rule": (
                "In the Section 3.3 factor chain, each prime factor p_i of "
                "the subgroup order becomes a map x -> x^(p_i); low degree "
                "therefore requires every p_i to be explicitly priced."
            ),
            "submitted_m6_m7_order": str(Q46),
            "submitted_m6_m7_maximum_prime_degree_step": Q46,
            "submitted_m6_m7_is_B_smooth_for_every_B_at_most_step": False,
            "largest_divisor_with_all_prime_steps_below_7322137": 16,
            "its_trace_root_count": 9,
            "largest_divisor_with_all_prime_steps_below_45422601869677": (
                16 * Q23
            ),
            "its_trace_root_count_below_45422601869677": trace_root_count(
                16 * Q23
            ),
            "boundary": (
                "This does not prove that no low-degree arithmetic-circuit or "
                "rational-map presentation exists. It proves that the submitted "
                "memo did not supply one and that its claimed direct PKC factor "
                "chain contains a 46-bit prime-degree step at m=6 and m=7."
            ),
        },
        "arity_rows": rows,
        "audit_findings": {
            "exact_surviving_arities_under_size_and_conservative_linear_algebra_only": surviving,
            "submitted_focus_arities": [6, 7],
            "submitted_table_is_exhaustive": False,
            "classification_correction": (
                "G_a, G_m and the nonsplit one-dimensional torus exhaust the "
                "connected one-dimensional affine linear algebraic groups over "
                "F_p, not all connected one-dimensional algebraic groups; "
                "elliptic curves are omitted by the broader wording."
            ),
        },
        "assessment": {
            "submitted_candidate": "rejected_missing_exact_low_degree_mechanism",
            "submitted_size_leg": "retracted_not_cleared",
            "broader_nonsplit_torus_trace_question": (
                "known_prior_art_application_inconclusive_exact_mechanism_and_cost_bridge_missing"
            ),
            "route_status": "open_parked",
            "experiment_authorized": False,
            "route_promoted": False,
            "reason": (
                "The arithmetic trace set exists, but the submitted candidate "
                "repackages known WCC 2017 prior art, uses large prime-degree "
                "factors, misstates the exhaustive arity screen, and supplies "
                "neither a faithful radical low-degree presentation nor recovery "
                "and full-cost contracts."
            ),
            "reopening_conditions": [
                "an exact Dickson or rational-map presentation with bounded local degrees",
                "radical or saturation treatment for repeated trace roots",
                "complete forward and inverse recovery semantics",
                "a full offline and online cost bridge against matched baselines",
                "independent source-level prior-art review",
                "a source-checked delta beyond the WCC 2017 trace construction",
            ],
        },
        "scope": {
            "included": [
                "exact p+1 factorization identity",
                "u64 primality of the 23-bit and 46-bit displayed factors",
                "trace inversion-orbit cardinality",
                "paper-balance threshold enumeration for m=2..20",
                "prime-degree steps forced by the submitted factor chain",
                "claim-level prior-art binding to WCC 2017",
            ],
            "excluded": [
                "Groebner or solver execution",
                "secp256k1 relation search",
                "novelty claim",
                "proof that every torus-based mechanism is impossible",
                "experiment authorization",
                "route promotion",
            ],
        },
    }


def write_artifact(artifact: dict[str, Any]) -> None:
    artifact_bytes = canonical_bytes(artifact)
    ARTIFACT_PATH.write_bytes(artifact_bytes)
    digest = hashlib.sha256(artifact_bytes).hexdigest()
    HASH_PATH.write_text(f"{digest}  artifact.json\n", encoding="ascii")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    artifact = build_artifact()
    expected = canonical_bytes(artifact)
    if args.write:
        write_artifact(artifact)
        print(f"wrote {ARTIFACT_PATH.relative_to(HERE.parent.parent.parent)}")
        return 0

    if not ARTIFACT_PATH.is_file() or ARTIFACT_PATH.read_bytes() != expected:
        print("nonsplit-torus desk screen FAILED: artifact is stale")
        return 1
    expected_hash = hashlib.sha256(expected).hexdigest()
    expected_hash_line = f"{expected_hash}  artifact.json\n"
    if not HASH_PATH.is_file() or HASH_PATH.read_text(encoding="ascii") != expected_hash_line:
        print("nonsplit-torus desk screen FAILED: hash is stale")
        return 1
    print(
        "nonsplit-torus desk screen OK: exact arithmetic replayed, "
        "submitted candidate rejected, 0 authorized"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
