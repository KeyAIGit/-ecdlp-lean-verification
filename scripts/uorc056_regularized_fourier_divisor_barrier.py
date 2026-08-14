#!/usr/bin/env python3
"""Certified subgroup Fourier-to-divisor barrier for regularized characters.

The package records the theorem-level implication

    lambda_f([k]G) = (-1)^k  for 1 <= k < n

for any odd cyclic subgroup H=<G> of E(F_q), where lambda_f agrees with the
quadratic character of a rational function away from its divisor and may use
arbitrary unit-modulus regularized values at rational odd-valuation points.
If s is the geometric odd-valuation support size, then

    cot(pi/(2*n)) <= s*sqrt(q) + s + 1,

hence

    s >= (cot(pi/(2*n)) - 1)/(sqrt(q) + 1).

The sheaf input has sharp constant one: after extending the peak character from
H to E(F_q), the Lang local system has order divisible by odd n and therefore
cannot cancel a quadratic Kummer local system. Grothendieck-Ogg-Shafarevich
then gives dim H_c^1=s, and Deligne gives the s*sqrt(q) trace bound.

No external point, scalar, wallet, or production target is accepted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

PROFILE_ID = "UORC-056-REGULARIZED-FOURIER-DIVISOR-BARRIER-V8"
SECP256K1_P = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F",
    16,
)
SECP256K1_N = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141",
    16,
)


def stable_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def peak_frequency_pair(n: int) -> tuple[int, int]:
    if n < 3 or n % 2 == 0:
        raise ValueError("n must be odd and at least three")
    return (n - 1) // 2, (n + 1) // 2


def parity_peak(n: int) -> float:
    peak_frequency_pair(n)
    return 1.0 / math.tan(math.pi / (2.0 * n))


def direct_nonzero_fourier_sum(n: int, frequency: int) -> complex:
    return sum(
        ((-1) ** k)
        * complex(
            math.cos(2.0 * math.pi * frequency * k / n),
            math.sin(2.0 * math.pi * frequency * k / n),
        )
        for k in range(1, n)
    )


def verify_peak_identity(n: int) -> None:
    expected = parity_peak(n)
    for frequency in peak_frequency_pair(n):
        direct = abs(direct_nonzero_fourier_sum(n, frequency))
        tolerance = 2e-10 * max(1.0, expected)
        if abs(direct - expected) > tolerance:
            raise AssertionError(
                f"parity Fourier identity drifted for n={n}, r={frequency}"
            )


def certified_cot_lower_fraction(n: int) -> tuple[int, int]:
    """Return A,B with cot(pi/(2n)) > A/B."""
    peak_frequency_pair(n)
    return 98 * n * n - 121, 154 * n


def floor_rational_over_sqrt_plus_one(
    numerator: int,
    denominator: int,
    q: int,
) -> int:
    """Exactly floor(numerator/(denominator*(sqrt(q)+1)))."""
    if numerator < 0 or denominator <= 0 or q <= 0:
        raise ValueError("invalid radical quotient")

    def admissible(candidate: int) -> bool:
        scaled = candidate * denominator
        remainder = numerator - scaled
        return (
            remainder >= 0
            and scaled * scaled * q <= remainder * remainder
        )

    low = 0
    high = numerator // denominator + 1
    while low + 1 < high:
        middle = (low + high) // 2
        if admissible(middle):
            low = middle
        else:
            high = middle
    return low


def certified_regularized_support_lower_bound(q: int, n: int) -> int:
    """Integer lower bound from cot <= s*(sqrt(q)+1)+1.

    Since cot(pi/(2n)) > A/B, the integer s satisfies

        s > (A-B)/(B*(sqrt(q)+1)).

    Therefore s is at least floor of that radical quotient plus one.
    """
    a, b = certified_cot_lower_fraction(n)
    return floor_rational_over_sqrt_plus_one(a - b, b, q) + 1


def sharp_floating_support_lower_bound(q: int, n: int) -> int:
    return max(
        0,
        math.ceil((parity_peak(n) - 1.0) / (math.sqrt(q) + 1.0)),
    )


def load_corpus(grammar_path: Path) -> list[tuple[str, int, int, str]]:
    grammar = json.loads(grammar_path.read_text(encoding="utf-8"))
    rows: list[tuple[str, int, int, str]] = []
    for corpus_name in ("discovery_corpus", "holdout_corpus"):
        for index, item in enumerate(grammar[corpus_name], start=1):
            p = int(item["p"])
            n = int(item["n"])
            rows.append(
                (
                    f"{corpus_name}_{index}_p{p}_n{n}",
                    p,
                    n,
                    corpus_name,
                )
            )
    return rows


def record(label: str, q: int, n: int, source: str) -> dict[str, Any]:
    certified = certified_regularized_support_lower_bound(q, n)
    sharp = sharp_floating_support_lower_bound(q, n)
    peak = parity_peak(n)
    ratio = (peak - 1.0) / (math.sqrt(q) + 1.0)
    return {
        "label": label,
        "source": source,
        "q": str(q),
        "n": str(n),
        "peak_frequencies": list(peak_frequency_pair(n)),
        "nonzero_parity_fourier_peak": f"{peak:.15e}",
        "regularized_ratio": f"{ratio:.15e}",
        "regularized_ratio_log2": (
            f"{math.log2(ratio):.12f}" if ratio > 0 else None
        ),
        "certified_odd_divisor_support_lower_bound": str(certified),
        "certified_odd_divisor_support_lower_bound_bits": (
            certified.bit_length() - 1 if certified else 0
        ),
        "certified_rational_map_degree_lower_bound": str(
            (certified + 1) // 2
        ),
        "floating_point_sharp_support_lower_bound": str(sharp),
    }


def run(grammar_path: Path) -> dict[str, Any]:
    rows = load_corpus(grammar_path)
    for _, _, n, _ in rows:
        verify_peak_identity(n)

    records = [record(label, q, n, source) for label, q, n, source in rows]
    records.append(
        record(
            "secp256k1",
            SECP256K1_P,
            SECP256K1_N,
            "SEC2 public domain parameters; cofactor one",
        )
    )

    grammar_bytes = grammar_path.read_bytes()
    return {
        "schema_version": "1.0",
        "experiment": PROFILE_ID,
        "review_status": (
            "provisional theorem-level proof assembled from standard sheaf "
            "results and executable arithmetic checks; independent specialist "
            "review and formalization remain pending"
        ),
        "input_grammar_sha256": hashlib.sha256(grammar_bytes).hexdigest(),
        "theorem": {
            "group_setting": (
                "E/F_q with arbitrary finite E(F_q), H=<G> an odd cyclic "
                "subgroup of order n"
            ),
            "function_setting": (
                "f in F_q(E)^*, s=#{geometric P: ord_P(f) odd}; evaluator "
                "equals the quadratic character off the divisor and may use "
                "arbitrary unit-modulus regularized values at rational odd "
                "support points"
            ),
            "target": "lambda_f([k]G)=(-1)^k for 1<=k<n",
            "hybrid_sum_bound": (
                "for every extension theta of the faithful peak character, "
                "|sum_{P in E(F_q)} theta(P) Tr(K_f)_P| <= s*sqrt(q)"
            ),
            "regularized_conclusion": (
                "cot(pi/(2*n)) <= s*sqrt(q)+s+1"
            ),
            "support_consequence": (
                "s >= (cot(pi/(2*n))-1)/(sqrt(q)+1)"
            ),
            "map_degree_consequence": "deg(f:E->P^1) >= ceil(s/2)",
        },
        "proof_kernel": [
            "The parity sequence has Fourier peak cot(pi/(2n)) at the two near-half frequencies.",
            "Every character of H extends to E(F_q); the indicator of H is the average over the annihilator H^perp.",
            "Every resulting full-group character restricts to a faithful odd-order character on H.",
            "Its Lang local system has geometric order divisible by n and cannot cancel the order-at-most-two quadratic Kummer local system.",
            "On U=E-S_odd(f), the tensor is rank one, tame, pure of weight zero and geometrically nontrivial.",
            "Grothendieck-Ogg-Shafarevich gives dim H_c^1(U_bar,F)=s; H_c^0 and H_c^2 vanish.",
            "The trace formula and Deligne weights give the complete hybrid bound s*sqrt(q).",
            "Regularization changes at most s rational odd-support terms and omission of O changes at most one term.",
        ],
        "certified_elementary_bound": {
            "cot_lower_bound": (
                "cot(pi/(2*n)) > (98*n^2-121)/(154*n)"
            ),
            "radical_floor": (
                "the script compares integer squares to evaluate floor(A/(B*(sqrt(q)+1))) exactly"
            ),
        },
        "records": records,
        "scope": {
            "closed": [
                "single rational quadratic-character evaluators",
                "finite products and quotients of rational character atoms after collapsing them to one rational function",
                "divisor-aware local-leading-coefficient regularizations",
                "all families with odd-divisor support o(n/sqrt(q))",
            ],
            "open": [
                "short straight-line programs defining rational functions of square-root or larger divisor support",
                "direct field-valued evaluators not reducible to one multiplicative character",
                "theta, elliptic-unit, EDS or long Miller representations with succinct high degree",
                "adaptive branching and non-character outputs",
            ],
        },
        "references": [
            "P. Deligne, La conjecture de Weil II, Publ. Math. IHES 52 (1980), 137-252.",
            "C. Cunningham and D. Roe, From the function-sheaf dictionary to quasicharacters of p-adic tori, J. Inst. Math. Jussieu 17 (2018), 1-37.",
            "M. Perret, Multiplicative character sums and Kummer coverings, Acta Arith. 59 (1991), 279-290.",
            "SGA 5, Cohomologie l-adique et fonctions L.",
            "SEC 2, Recommended Elliptic Curve Domain Parameters, Version 2.0 (2010).",
        ],
        "scientific_boundary": [
            "This is a divisor-support and rational-map-degree barrier, not an arithmetic-circuit lower bound.",
            "The proof does not produce an evaluator or recover any unknown scalar.",
            "No external point, wallet, real key or production-sized target is accepted.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--grammar",
        type=Path,
        default=Path(
            "experiments/uorc056/divisor_aware_rational_grammar.json"
        ),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(
            "experiments/uorc056/regularized_fourier_divisor_barrier_results.json"
        ),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = stable_json(run(args.grammar))
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("regularized Fourier-divisor artifact drift")
        print("UORC056_REGULARIZED_FOURIER_DIVISOR_BARRIER_OK")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
