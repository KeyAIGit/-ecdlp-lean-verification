from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from uorc056_sector_factor_reconciliation import (
    SECP256K1_LAMBDA,
    SECP256K1_N,
    parity_correlation_certificate,
)
from uorc056_toy_factory import DEFAULT_INSTANCES

PROFILE_ID = "UORC-056-SECTOR-SPARSE-RATIONAL-SPECTRAL-BARRIER-V18"
DEFAULT_OUTPUT = Path(
    "experiments/uorc056/sector_sparse_rational_spectral_barrier_results.json"
)


def stable_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def pair_sum_cover_bound(target_size: int) -> int:
    """Smallest t with t(t+1)/2 >= target_size."""
    if target_size < 0:
        raise ValueError("target size must be nonnegative")
    root = math.isqrt(1 + 8 * target_size)
    candidate = max(0, (root - 1) // 2)
    while candidate * (candidate + 1) // 2 < target_size:
        candidate += 1
    while (
        candidate > 0
        and (candidate - 1) * candidate // 2 >= target_size
    ):
        candidate -= 1
    return candidate


def scalar_sector_counts(order: int, correlation: int) -> tuple[int, int]:
    if order % 2 == 0:
        raise ValueError("order must be odd")
    if (order - 1 + correlation) % 2:
        raise ValueError("sector correlation has wrong parity")
    plus = (order - 1 + correlation) // 2
    minus = (order - 1 - correlation) // 2
    if plus + minus != order - 1:
        raise AssertionError("sector scalar counts do not partition nonzero scalars")
    return plus, minus


def square_exact_uncertainty_bounds(
    order: int, correlation: int
) -> dict[str, int]:
    plus, minus = scalar_sector_counts(order, correlation)
    # U=A-B is supported on the negative fiber plus possibly zero.
    # Tao's prime-cycle support uncertainty gives
    # |supp(Uhat)| >= order - minus = plus + 1.
    u_bound = order - minus
    # V=A+B is supported on the positive fiber plus possibly zero.
    v_bound = order - plus
    return {
        "nonzero_plus_scalars": plus,
        "nonzero_minus_scalars": minus,
        "A_minus_B_frequency_union_lower_bound": u_bound,
        "A_plus_B_frequency_union_lower_bound": v_bound,
        "square_exact_frequency_union_lower_bound": max(u_bound, v_bound),
    }


def curve_record(instance: Any) -> dict[str, Any]:
    order = int(instance.subgroup_order)
    eigenvalue = int(instance.glv_lambda)
    correlation = parity_correlation_certificate(
        order, eigenvalue
    )["correlation"]
    nonzero_square_bound = pair_sum_cover_bound(order)
    if (nonzero_square_bound - 1) * nonzero_square_bound // 2 >= order:
        raise AssertionError("nonzero-square pair bound is not minimal")
    if nonzero_square_bound * (nonzero_square_bound + 1) // 2 < order:
        raise AssertionError("nonzero-square pair bound is insufficient")
    square_exact = square_exact_uncertainty_bounds(order, correlation)
    if square_exact["square_exact_frequency_union_lower_bound"] <= nonzero_square_bound:
        raise AssertionError("square-exact case should be the stronger branch")
    return {
        "id": instance.instance_id,
        "n": order,
        "lambda": eigenvalue,
        "sector_correlation": correlation,
        "H_nonzero_frequency_union_lower_bound": nonzero_square_bound,
        **square_exact,
        "universal_sparse_rational_frequency_union_lower_bound": nonzero_square_bound,
    }


def secp256k1_record() -> dict[str, Any]:
    order = SECP256K1_N
    correlation = parity_correlation_certificate(
        order, SECP256K1_LAMBDA
    )["correlation"]
    if correlation != 208:
        raise AssertionError("secp256k1 sector correlation drifted")
    nonzero_square_bound = pair_sum_cover_bound(order)
    expected_root_bound = (
        481231938336009023090067544955250113853
    )
    if nonzero_square_bound != expected_root_bound:
        raise AssertionError("secp256k1 rational spectral root bound drifted")
    if (nonzero_square_bound - 1) * nonzero_square_bound // 2 >= order:
        raise AssertionError("preceding secp256k1 root bound unexpectedly covers")
    if nonzero_square_bound * (nonzero_square_bound + 1) // 2 < order:
        raise AssertionError("fixed secp256k1 root bound does not cover")
    square_exact = square_exact_uncertainty_bounds(order, correlation)
    expected_square_exact = (
        57896044618658097711785492504343953926418782139537452191302581570759080747273
    )
    if (
        square_exact["square_exact_frequency_union_lower_bound"]
        != expected_square_exact
    ):
        raise AssertionError("secp256k1 square-exact uncertainty bound drifted")
    return {
        "n": order,
        "lambda": SECP256K1_LAMBDA,
        "sector_correlation": correlation,
        "H_nonzero_frequency_union_lower_bound": nonzero_square_bound,
        "H_nonzero_lower_bound_bit_length": nonzero_square_bound.bit_length(),
        "H_nonzero_pair_capacity": (
            nonzero_square_bound * (nonzero_square_bound + 1) // 2
        ),
        "H_nonzero_pair_capacity_slack": (
            nonzero_square_bound * (nonzero_square_bound + 1) // 2
            - order
        ),
        **square_exact,
        "universal_sparse_rational_frequency_union_lower_bound": (
            nonzero_square_bound
        ),
        "universal_lower_bound_exceeds_2_pow_128": (
            nonzero_square_bound > 2**128
        ),
        "universal_lower_bound_below_2_pow_129": (
            nonzero_square_bound < 2**129
        ),
        "claim_boundary": (
            "The support cost is the union of nonzero additive-character "
            "frequencies used by numerator and denominator. The result is not "
            "a lower bound for nonlinear circuits that do not expand this union."
        ),
    }


def run() -> dict[str, Any]:
    rows = [curve_record(instance) for instance in DEFAULT_INSTANCES]
    if len(rows) != 5:
        raise AssertionError("frozen curve count drifted")
    return {
        "schema_version": "1.0",
        "profile_id": PROFILE_ID,
        "model": {
            "numerator": "A(k)=sum_{r in S_A} a_r exp(2*pi*i*r*k/n)",
            "denominator": "B(k)=sum_{r in S_B} b_r exp(2*pi*i*r*k/n)",
            "requirement": (
                "B(k)!=0 and A(k)/B(k)=J_G(k) in {+1,-1} "
                "for every k!=0"
            ),
            "charged_support": "T=S_A union S_B, t=|T|",
            "zero_point_is_free": True,
        },
        "dichotomy": {
            "residual": "H=A^2-B^2 vanishes on every nonzero scalar",
            "H_nonzero": {
                "identity": "H is a nonzero multiple of delta_0",
                "spectral_consequence": (
                    "every frequency lies in (S_A+S_A) union "
                    "(S_B+S_B), which is contained in T+T"
                ),
                "count": "t(t+1)/2 >= n",
            },
            "H_zero": {
                "identity": "(A-B)(A+B)=0 pointwise",
                "fiber_support": (
                    "A-B is supported on the negative sector plus possibly "
                    "zero; A+B is supported on the positive sector plus "
                    "possibly zero"
                ),
                "prime_uncertainty": (
                    "|supp f|+|supp fhat|>=n+1 on Z/nZ for prime n"
                ),
                "source": "Terence Tao, arXiv:math/0308286",
            },
        },
        "secp256k1": secp256k1_record(),
        "exact_toy_arithmetic_replay": {
            "curves": len(rows),
            "all_root_bounds_minimal": True,
            "all_square_exact_bounds_stronger": True,
            "curve_rows": rows,
        },
        "decision": (
            "A quotient of two sparse additive-character sums cannot evaluate "
            "the Kummer sector bit on all nonzero secp256k1 scalars with "
            "o(sqrt(n)) distinct expanded frequencies."
        ),
        "closed_class": (
            "sparse additive-character numerator/denominator quotient with "
            "sub-square-root union support"
        ),
        "next_frontier": [
            "nonlinear circuits that generate dense spectra without expanded storage",
            "modular-composition or recurrence-compressed sector evaluation",
            "shared carry-sector circuits",
            "representation-specific circuit lower bounds",
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
            raise SystemExit("V18 sparse rational spectral artifact drift")
        print("UORC056_SECTOR_SPARSE_RATIONAL_SPECTRAL_BARRIER_V18_OK")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
