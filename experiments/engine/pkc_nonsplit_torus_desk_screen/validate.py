#!/usr/bin/env python3
"""Independently replay the nonsplit-torus desk-screen artifact.

This validator imports no producer code and recomputes every decisive field
from public constants.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
Q23 = 7_322_137
Q46 = 45_422_601_869_677
Q_REST = (
    21_759_506_893_163_426_790_183_529_804_034_058_295_931_507_131_047_955_271
)
CAP = 1 << 126
EXPECTED_SURVIVORS = list(range(6, 21))
HERE = Path(__file__).resolve().parent


class Replay:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def expect(self, label: str, actual: Any, expected: Any) -> None:
        if actual != expected:
            self.failures.append(
                f"{label}: expected {expected!r}, observed {actual!r}"
            )

    def require_dict(self, label: str, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            self.failures.append(f"{label}: expected object")
            return {}
        return value

    def require_list(self, label: str, value: Any) -> list[Any]:
        if not isinstance(value, list):
            self.failures.append(f"{label}: expected array")
            return []
        return value


def ceil_root_newton(value: int, exponent: int) -> int:
    estimate = 1 << ((value.bit_length() + exponent - 1) // exponent)
    while True:
        denominator = estimate ** (exponent - 1)
        updated = ((exponent - 1) * estimate + value // denominator) // exponent
        if updated >= estimate:
            break
        estimate = updated
    while estimate**exponent > value:
        estimate -= 1
    return estimate if estimate**exponent == value else estimate + 1


def factorial_descending(value: int) -> int:
    result = 1
    while value > 1:
        result *= value
        value -= 1
    return result


def is_prime_trial_division(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def is_prime_u64_independent(value: int) -> bool:
    if value < 2:
        return False
    for prime in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if value % prime == 0:
            return value == prime
    odd = value - 1
    power = 0
    while not odd & 1:
        power += 1
        odd >>= 1
    # This base set is deterministic for n < 2^64.
    for witness in (2, 325, 9_375, 28_178, 450_775, 9_780_504, 1_795_265_022):
        witness %= value
        if witness == 0:
            continue
        residue = pow(witness, odd, value)
        passed = residue in (1, value - 1)
        round_index = 1
        while not passed and round_index < power:
            residue = residue * residue % value
            passed = residue == value - 1
            round_index += 1
        if not passed:
            return False
    return True


def enumerate_divisors_independently() -> list[int]:
    values: set[int] = set()
    for exponent_two in range(5):
        for include_q23 in (False, True):
            for include_q46 in (False, True):
                value = 2**exponent_two
                if include_q23:
                    value *= Q23
                if include_q46:
                    value *= Q46
                values.add(value)
    return sorted(values)


def trace_count(order: int) -> int:
    fixed_by_inverse = 2 if order % 2 == 0 else 1
    return (order + fixed_by_inverse) // 2


def two_part_by_repeated_division(value: int) -> int:
    exponent = 0
    while value % 2 == 0:
        exponent += 1
        value //= 2
    return 1 << exponent


def step_primes(order: int) -> list[int]:
    return [prime for prime in (2, Q23, Q46) if order % prime == 0]


def expected_row(m: int, divisors: list[int]) -> dict[str, Any]:
    threshold = ceil_root_newton(factorial_descending(m) * P, m)
    candidates: list[tuple[int, int]] = []
    for order in divisors:
        roots = trace_count(order)
        if roots >= threshold and roots * roots <= CAP:
            candidates.append((roots, order))
    if not candidates:
        return {
            "m": m,
            "paper_balance_threshold": str(threshold),
            "size_and_conservative_linear_algebra_screen": "no_candidate",
            "selected": None,
        }
    roots, order = min(candidates)
    primes = step_primes(order)
    return {
        "m": m,
        "paper_balance_threshold": str(threshold),
        "size_and_conservative_linear_algebra_screen": "candidate_exists",
        "selected": {
            "group_order": str(order),
            "trace_root_count": str(roots),
            "yield_margin": str(roots - threshold),
            "prime_degree_steps": primes,
            "maximum_prime_degree_step": max(primes),
            "nominal_linear_algebra_work": str(roots * roots),
        },
    }


def check_hash(
    artifact_path: Path, hash_path: Path, raw: bytes, replay: Replay
) -> None:
    try:
        line = hash_path.read_text(encoding="ascii")
    except (OSError, UnicodeError) as error:
        replay.failures.append(f"hash file unreadable: {error}")
        return
    match = re.fullmatch(r"([0-9a-f]{64})  artifact\.json\n", line)
    if match is None:
        replay.failures.append("artifact.sha256 has a non-canonical format")
        return
    replay.expect(
        "artifact.sha256",
        match.group(1),
        hashlib.sha256(raw).hexdigest(),
    )


def replay_document(document: dict[str, Any], replay: Replay) -> None:
    replay.expect("schema_version", document.get("schema_version"), "1.0")
    replay.expect(
        "artifact_id",
        document.get("artifact_id"),
        "PKC-NONSPLIT-TORUS-DESK-SCREEN-001",
    )

    inputs = replay.require_dict("inputs", document.get("inputs"))
    replay.expect("inputs.p", inputs.get("p"), str(P))
    replay.expect("inputs.cap", inputs.get("conservative_linear_algebra_cap"), str(CAP))

    factorization = replay.require_dict(
        "p_plus_one_factorization", document.get("p_plus_one_factorization")
    )
    replay.expect(
        "p+1 identity",
        (2**4) * Q23 * Q46 * Q_REST,
        P + 1,
    )
    replay.expect(
        "known divisors",
        factorization.get("known_divisors_excluding_remaining_cofactor"),
        [str(value) for value in enumerate_divisors_independently()],
    )
    replay.expect(
        "largest power-of-two divisor",
        factorization.get("largest_power_of_two_divisor"),
        two_part_by_repeated_division(P + 1),
    )
    replay.expect(
        "largest power-of-two trace-root count",
        factorization.get("largest_power_of_two_trace_root_count"),
        trace_count(two_part_by_repeated_division(P + 1)),
    )
    if not is_prime_trial_division(Q23):
        replay.failures.append("q23 failed independent trial-division primality")
    if not is_prime_u64_independent(Q46):
        replay.failures.append("q46 failed independent u64 primality")
    replay.expect(
        "remaining cofactor boundary",
        factorization.get("remaining_cofactor_primality"),
        "not_claimed_by_this_artifact",
    )

    expected_rows = [
        expected_row(m, enumerate_divisors_independently()) for m in range(2, 21)
    ]
    replay.expect("arity_rows", document.get("arity_rows"), expected_rows)

    findings = replay.require_dict(
        "audit_findings", document.get("audit_findings")
    )
    replay.expect(
        "surviving arities",
        findings.get(
            "exact_surviving_arities_under_size_and_conservative_linear_algebra_only"
        ),
        EXPECTED_SURVIVORS,
    )
    replay.expect(
        "submitted table exhaustiveness",
        findings.get("submitted_table_is_exhaustive"),
        False,
    )

    smooth = replay.require_dict(
        "smooth_composition_screen", document.get("smooth_composition_screen")
    )
    replay.expect("submitted order", smooth.get("submitted_m6_m7_order"), str(Q46))
    replay.expect(
        "submitted maximum prime step",
        smooth.get("submitted_m6_m7_maximum_prime_degree_step"),
        Q46,
    )
    replay.expect(
        "strict B-smooth verdict",
        smooth.get("submitted_m6_m7_is_B_smooth_for_every_B_at_most_step"),
        False,
    )
    replay.expect(
        "below-q23 divisor",
        smooth.get("largest_divisor_with_all_prime_steps_below_7322137"),
        16,
    )
    replay.expect("below-q23 trace count", smooth.get("its_trace_root_count"), 9)
    replay.expect(
        "below-q46 divisor",
        smooth.get("largest_divisor_with_all_prime_steps_below_45422601869677"),
        16 * Q23,
    )

    prior_art = replay.require_dict("prior_art", document.get("prior_art"))
    replay.expect(
        "prior-art classification",
        prior_art.get("classification"),
        "confirmed_prior_art",
    )
    replay.expect(
        "prior-art source claim",
        prior_art.get("source_claim_id"),
        "SC-WCC2017-PPLUS1-TRACE-EXTENSION",
    )

    assessment = replay.require_dict("assessment", document.get("assessment"))
    replay.expect(
        "submitted disposition",
        assessment.get("submitted_candidate"),
        "rejected_missing_exact_low_degree_mechanism",
    )
    replay.expect(
        "broader disposition",
        assessment.get("broader_nonsplit_torus_trace_question"),
        "known_prior_art_application_inconclusive_exact_mechanism_and_cost_bridge_missing",
    )
    replay.expect("experiment authorization", assessment.get("experiment_authorized"), False)
    replay.expect("route promotion", assessment.get("route_promoted"), False)

    scope = replay.require_dict("scope", document.get("scope"))
    excluded = replay.require_list("scope.excluded", scope.get("excluded"))
    for phrase in (
        "Groebner or solver execution",
        "secp256k1 relation search",
        "novelty claim",
        "proof that every torus-based mechanism is impossible",
        "experiment authorization",
        "route promotion",
    ):
        if phrase not in excluded:
            replay.failures.append(f"scope.excluded missing {phrase!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, default=HERE / "artifact.json")
    parser.add_argument("--hash-file", type=Path, default=HERE / "artifact.sha256")
    args = parser.parse_args()

    replay = Replay()
    try:
        raw = args.artifact.read_bytes()
        document = json.loads(raw)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"nonsplit-torus replay FAILED: {error}")
        return 1
    check_hash(args.artifact, args.hash_file, raw, replay)
    if not isinstance(document, dict):
        replay.failures.append("artifact root must be an object")
    else:
        replay_document(document, replay)

    if replay.failures:
        print("nonsplit-torus replay FAILED:")
        for failure in replay.failures:
            print(f"  - {failure}")
        return 1
    print(
        "nonsplit-torus replay PASS: factor steps, trace counts, arity table, "
        "and zero-authorization disposition independently reproduced"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
