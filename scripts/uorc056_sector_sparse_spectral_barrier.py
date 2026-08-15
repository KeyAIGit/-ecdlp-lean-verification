from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Iterable, Sequence

from uorc056_sector_factor_reconciliation import (
    SECP256K1_LAMBDA,
    SECP256K1_N,
    glv_state,
    parity_correlation_certificate,
)
from uorc056_toy_factory import DEFAULT_INSTANCES

PROFILE_ID = "UORC-056-SECTOR-SPARSE-SPECTRAL-BARRIER-V17"
DEFAULT_OUTPUT = Path("experiments/uorc056/sector_sparse_spectral_barrier_results.json")
RANK_CERTIFICATE_PRIME = 1_000_003


def stable_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def ceil_sqrt(value: int) -> int:
    if value < 0:
        raise ValueError("ceil_sqrt expects a nonnegative integer")
    root = math.isqrt(value)
    return root if root * root == value else root + 1


def pair_sum_cover_lower_bound(group_order: int) -> int:
    """Smallest m with m(m+1)/2 >= group_order-1."""
    if group_order < 2:
        raise ValueError("group order must be at least two")
    target = group_order - 1
    root = math.isqrt(1 + 8 * target)
    candidate = max(0, (root - 1) // 2)
    while candidate * (candidate + 1) // 2 < target:
        candidate += 1
    while candidate > 0 and (candidate - 1) * candidate // 2 >= target:
        candidate -= 1
    return candidate


def is_prime_small(value: int) -> bool:
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


def canonical_sector_sequence(group_order: int, eigenvalue: int) -> list[int]:
    """Extend the nonzero sector bit by the canonical value +1 at zero."""
    sequence = [1]
    sequence.extend(
        glv_state(k, group_order, eigenvalue)["sector"]
        for k in range(1, group_order)
    )
    return sequence


def trim_mod(poly: Sequence[int], modulus: int) -> list[int]:
    result = [int(coefficient) % modulus for coefficient in poly]
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result or [0]


def poly_divmod_mod(
    dividend: Sequence[int], divisor: Sequence[int], modulus: int
) -> tuple[list[int], list[int]]:
    left = trim_mod(dividend, modulus)
    right = trim_mod(divisor, modulus)
    if right == [0]:
        raise ZeroDivisionError("polynomial division by zero")
    quotient = [0] * max(1, len(left) - len(right) + 1)
    inverse_leading = pow(right[-1], -1, modulus)
    while left != [0] and len(left) >= len(right):
        degree = len(left) - len(right)
        coefficient = left[-1] * inverse_leading % modulus
        quotient[degree] = coefficient
        for index, right_coefficient in enumerate(right):
            left[index + degree] = (
                left[index + degree] - coefficient * right_coefficient
            ) % modulus
        left = trim_mod(left, modulus)
    return trim_mod(quotient, modulus), left


def poly_gcd_mod(
    left: Sequence[int], right: Sequence[int], modulus: int
) -> list[int]:
    a = trim_mod(left, modulus)
    b = trim_mod(right, modulus)
    while b != [0]:
        _quotient, remainder = poly_divmod_mod(a, b, modulus)
        a, b = b, remainder
    inverse_leading = pow(a[-1], -1, modulus)
    return trim_mod(
        [coefficient * inverse_leading for coefficient in a], modulus
    )


def exact_circulant_rank_certificate(
    sequence: Sequence[int], modulus: int = RANK_CERTIFICATE_PRIME
) -> dict[str, int | bool]:
    """Certify a nonzero integer circulant determinant modulo one prime."""
    order = len(sequence)
    x_to_order_minus_one = [-1] + [0] * (order - 1) + [1]
    gcd = poly_gcd_mod(sequence, x_to_order_minus_one, modulus)
    return {
        "modulus": modulus,
        "gcd_degree": len(gcd) - 1,
        "full_rank_mod_prime": gcd == [1],
    }


def additive_basis(order: int) -> set[int]:
    """A deterministic order-two additive basis of size at most 2 ceil(sqrt n)-1."""
    block = ceil_sqrt(order)
    return {
        value % order
        for value in (
            *range(block),
            *(multiple * block for multiple in range(block)),
        )
    }


def sumset(values: Iterable[int], modulus: int) -> set[int]:
    normalized = sorted({int(value) % modulus for value in values})
    return {
        (left + right) % modulus
        for left in normalized
        for right in normalized
    }


def curve_record(instance: Any) -> dict[str, Any]:
    order = int(instance.subgroup_order)
    eigenvalue = int(instance.glv_lambda)
    if not is_prime_small(order):
        raise AssertionError("frozen subgroup order is not prime")
    sequence = canonical_sector_sequence(order, eigenvalue)
    if any(value not in (-1, 1) for value in sequence):
        raise AssertionError("sector sequence left the binary alphabet")
    if sequence == [sequence[0]] * order:
        raise AssertionError("sector sequence is constant")
    if any(sequence[k] != sequence[-k % order] for k in range(order)):
        raise AssertionError("sector sequence is not Kummer-even")
    correlation = sum(sequence[1:])
    certificate = parity_correlation_certificate(order, eigenvalue)
    if correlation != certificate["correlation"]:
        raise AssertionError("sector correlation certificate drifted")
    plus_nonzero = sequence[1:].count(1)
    minus_nonzero = sequence[1:].count(-1)
    if plus_nonzero == 0 or minus_nonzero == 0:
        raise AssertionError("both nonzero sector fibers must occur")
    rank_certificate = exact_circulant_rank_certificate(sequence)
    if not rank_certificate["full_rank_mod_prime"]:
        raise AssertionError("canonical sector circulant lost exact full rank")
    lower_bound = pair_sum_cover_lower_bound(order)
    if (lower_bound - 1) * lower_bound // 2 >= order - 1:
        raise AssertionError("pair-cover lower bound is not minimal")
    if lower_bound * (lower_bound + 1) // 2 < order - 1:
        raise AssertionError("pair-cover lower bound is insufficient")
    basis = additive_basis(order)
    covered = sumset(basis, order)
    if len(covered) != order:
        raise AssertionError("deterministic order-two additive basis failed")
    return {
        "id": instance.instance_id,
        "n": order,
        "lambda": eigenvalue,
        "nonzero_plus_count": plus_nonzero,
        "nonzero_minus_count": minus_nonzero,
        "nonzero_sector_sum": correlation,
        "canonical_full_cycle_sum": sum(sequence),
        "canonical_binary_extension_full_rank_mod_prime": True,
        "rank_certificate_prime": rank_certificate["modulus"],
        "rank_certificate_gcd_degree": rank_certificate["gcd_degree"],
        "nonzero_domain_sparse_frequency_lower_bound": lower_bound,
        "deterministic_pair_basis_size": len(basis),
        "deterministic_pair_basis_upper_bound": 2 * ceil_sqrt(order) - 1,
        "pair_basis_covers_group": True,
    }


def secp256k1_record() -> dict[str, Any]:
    order = SECP256K1_N
    correlation = parity_correlation_certificate(
        order, SECP256K1_LAMBDA
    )["correlation"]
    if correlation != 208:
        raise AssertionError("secp256k1 sector correlation drifted")
    plus_half = (order - 1 + correlation) // 4
    minus_half = (order - 1 - correlation) // 4
    if plus_half <= 0 or minus_half <= 0:
        raise AssertionError("secp256k1 sector must be nonconstant")
    lower_bound = pair_sum_cover_lower_bound(order)
    expected_lower_bound = (
        481231938336009023090067544955250113853
    )
    if lower_bound != expected_lower_bound:
        raise AssertionError("secp256k1 sparse spectral bound drifted")
    target = order - 1
    if (lower_bound - 1) * lower_bound // 2 >= target:
        raise AssertionError("secp256k1 lower bound is not minimal")
    if lower_bound * (lower_bound + 1) // 2 < target:
        raise AssertionError("secp256k1 lower bound is insufficient")
    block = ceil_sqrt(order)
    if block != 2**128:
        raise AssertionError("unexpected secp256k1 square-root block")
    return {
        "n": order,
        "lambda": SECP256K1_LAMBDA,
        "canonical_binary_extension_dc_sum": 1 + correlation,
        "canonical_binary_extension_fourier_support": order,
        "nonzero_domain_sparse_frequency_lower_bound": lower_bound,
        "lower_bound_bit_length": lower_bound.bit_length(),
        "lower_bound_exceeds_2_pow_128": lower_bound > 2**128,
        "lower_bound_below_2_pow_129": lower_bound < 2**129,
        "pair_count_at_lower_bound": lower_bound * (lower_bound + 1) // 2,
        "pair_count_slack": (
            lower_bound * (lower_bound + 1) // 2 - target
        ),
        "support_only_pair_basis_block": block,
        "support_only_pair_basis_size_upper_bound": 2 * block - 1,
        "sector_plus_half_kernel_degree": plus_half,
        "sector_minus_half_kernel_degree": minus_half,
        "claim_boundary": (
            "The bound applies to one exact linear combination of additive "
            "characters on the scalar cycle. It is not an arithmetic-circuit "
            "lower bound because multiplication can create many frequencies."
        ),
    }


def run() -> dict[str, Any]:
    rows = [curve_record(instance) for instance in DEFAULT_INSTANCES]
    if sum(row["n"] - 1 for row in rows) != 438:
        raise AssertionError("frozen nonzero-scalar total drifted")
    if any(not row["pair_basis_covers_group"] for row in rows):
        raise AssertionError("toy pair-basis coverage failed")
    return {
        "schema_version": "1.0",
        "profile_id": PROFILE_ID,
        "model": {
            "candidate": (
                "F(k)=sum_{r in S} c_r exp(2*pi*i*r*k/n), "
                "required to equal J_G(k) in {+1,-1} for every k!=0"
            ),
            "zero_point_is_free": True,
            "support_size": "m=|S| after zero coefficients are removed",
        },
        "exact_argument": {
            "square_residual": (
                "H=F^2-1 vanishes at every nonzero scalar"
            ),
            "case_H_zero": (
                "F is a nonconstant binary function on the full prime cycle; "
                "the prime cyclotomic polynomial forces all n Fourier "
                "coefficients to be nonzero"
            ),
            "case_H_nonzero": (
                "H is a nonzero multiple of delta_0, so every nonzero "
                "frequency belongs to S+S"
            ),
            "unordered_pair_bound": "|S+S| <= m(m+1)/2",
            "conclusion": "m(m+1)/2 >= n-1",
        },
        "secp256k1": secp256k1_record(),
        "exact_toy_replay": {
            "curves": len(rows),
            "nonzero_scalars": sum(row["n"] - 1 for row in rows),
            "all_sequences_binary_even_nonconstant": True,
            "all_canonical_circulants_full_rank_mod_prime": True,
            "all_pair_basis_constructions_cover": True,
            "curve_rows": rows,
        },
        "tightness_boundary": {
            "construction": (
                "For b=ceil(sqrt(n)), S={0,...,b-1} union "
                "{0,b,2b,...,(b-1)b} satisfies S+S=Z/nZ"
            ),
            "size": "|S| <= 2*ceil(sqrt(n))-1",
            "interpretation": (
                "The support-cardinality argument is exponent-tight at "
                "one half. Coverage of S+S is necessary, not sufficient "
                "for coefficients that evaluate the sector bit."
            ),
        },
        "decision": (
            "Exact sparse additive-character sums with "
            "o(sqrt(n)) frequencies cannot evaluate the Kummer sector bit "
            "on all nonzero secp256k1 scalars."
        ),
        "next_frontier": [
            "nonlinear low-size circuits whose frequency support grows by multiplication",
            "modular-composition and recurrence representations not charged by expanded support",
            "shared carry-sector circuits",
            "sparse rational character quotients with separately charged numerator and denominator supports",
        ],
        "scientific_boundary": (
            "No public sector decoder, parity evaluator, or ECDLP algorithm is constructed."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = stable_json(run())
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("V17 sparse spectral artifact drift")
        print("UORC056_SECTOR_SPARSE_SPECTRAL_BARRIER_V17_OK")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
