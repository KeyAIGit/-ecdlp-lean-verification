#!/usr/bin/env python3
"""Generate the UORC-056 parity-spectrum divisor-degree barrier artifact.

This package does not search a larger circuit grammar.  It records the exact
Fourier peak of the alternating sequence on an odd cyclic group and the
resulting rank-one sheaf bound for a quadratic character of a rational
function on an elliptic curve.

The theorem-level input is:

    (b(f) + 1) * sqrt(q) >= cot(pi / (2*n)),

where E(F_q)=<G> has odd order n and b(f) is the number of geometric points at
which ord_P(f) is odd.  Hence the rational-map degree is at least b(f)/2.

The machine artifact also gives an integer-certified lower bound using only

    sin(x) <= x,
    cos(x) >= 1 - x^2/2,
    pi < 22/7.

For x=pi/(2n), these imply

    cot(x) > (98*n^2 - 121)/(154*n).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

PROFILE_ID = "UORC-056-PARITY-SPECTRUM-DIVISOR-BARRIER-V6"
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
    """Magnitude of the nonzero-point Fourier sum at either peak frequency."""
    peak_frequency_pair(n)
    return 1.0 / math.tan(math.pi / (2.0 * n))


def certified_cot_lower_fraction(n: int) -> tuple[int, int]:
    """Return A,B with cot(pi/(2n)) > A/B, certified by elementary bounds."""
    peak_frequency_pair(n)
    return 98 * n * n - 121, 154 * n


def floor_rational_over_sqrt(
    numerator: int,
    denominator: int,
    q: int,
) -> int:
    """Compute floor(numerator/(denominator*sqrt(q))) exactly."""
    if numerator < 0 or denominator <= 0 or q <= 0:
        raise ValueError("invalid nonnegative radical quotient")
    return math.isqrt(
        (numerator * numerator) // (denominator * denominator * q)
    )


def certified_odd_support_lower_bound(q: int, n: int) -> int:
    numerator, denominator = certified_cot_lower_fraction(n)
    return floor_rational_over_sqrt(numerator, denominator, q)


def approximate_odd_support_lower_bound(q: int, n: int) -> int:
    return max(0, math.ceil(parity_peak(n) / math.sqrt(q)) - 1)


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
    for frequency in peak_frequency_pair(n):
        direct = abs(direct_nonzero_fourier_sum(n, frequency))
        expected = parity_peak(n)
        tolerance = 2e-10 * max(1.0, expected)
        if abs(direct - expected) > tolerance:
            raise AssertionError(
                f"parity Fourier identity drifted for n={n}, r={frequency}"
            )


def record(label: str, q: int, n: int, source: str) -> dict[str, Any]:
    certified_support = certified_odd_support_lower_bound(q, n)
    approximate_support = approximate_odd_support_lower_bound(q, n)
    peak = parity_peak(n)
    ratio = peak / math.sqrt(q)
    return {
        "label": label,
        "source": source,
        "q": str(q),
        "n": str(n),
        "peak_frequencies": list(peak_frequency_pair(n)),
        "nonzero_parity_fourier_peak": f"{peak:.15e}",
        "peak_over_sqrt_q": f"{ratio:.15e}",
        "peak_over_sqrt_q_log2": f"{math.log2(ratio):.12f}",
        "certified_odd_divisor_support_lower_bound": str(certified_support),
        "certified_odd_divisor_support_lower_bound_bits": (
            certified_support.bit_length() - 1
            if certified_support
            else 0
        ),
        "certified_rational_map_degree_lower_bound": str(
            (certified_support + 1) // 2
        ),
        "floating_point_sharp_support_lower_bound": str(approximate_support),
    }


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


def run(grammar_path: Path) -> dict[str, Any]:
    corpus_rows = load_corpus(grammar_path)
    for _, _, n, _ in corpus_rows:
        verify_peak_identity(n)

    records = [
        record(label, p, n, source)
        for label, p, n, source in corpus_rows
    ]
    records.append(
        record(
            "secp256k1",
            SECP256K1_P,
            SECP256K1_N,
            "SEC2 domain parameters; cofactor one",
        )
    )

    theorem = {
        "setting": (
            "E/F_q with E(F_q)=<G> cyclic of odd order n; eta is the "
            "quadratic character; f is a nonzero rational function whose "
            "values are finite and nonzero on E(F_q) minus {O}"
        ),
        "target_identity": "eta(f([k]G))=(-1)^k for 1<=k<n",
        "odd_support": (
            "b(f)=#{P in E(Fbar_q): ord_P(f) is odd}"
        ),
        "conclusion": "(b(f)+1)*sqrt(q) >= cot(pi/(2*n))",
        "map_degree_consequence": (
            "deg(f:E->P^1) >= ceil(b(f)/2)"
        ),
        "proof_dependencies": [
            "exact DFT of the alternating sequence on an odd cyclic group",
            "Lang rank-one character sheaves for characters of E(F_q)",
            "the quadratic Kummer sheaf attached to f",
            "Grothendieck trace formula",
            "Grothendieck-Ogg-Shafarevich on a punctured genus-one curve",
            "Deligne weight bound for H_c^1",
        ],
        "geometric_nontriviality_guard": (
            "use the two peak frequencies (n-1)/2 and (n+1)/2; their Lang "
            "local systems are distinct, so at least one tensor product "
            "with the fixed Kummer sheaf is geometrically nontrivial"
        ),
    }

    grammar_bytes = grammar_path.read_bytes()
    return {
        "schema_version": "1.0",
        "experiment": PROFILE_ID,
        "input_grammar_sha256": hashlib.sha256(grammar_bytes).hexdigest(),
        "theorem": theorem,
        "certified_elementary_bound": {
            "formula": (
                "cot(pi/(2*n)) > (98*n^2-121)/(154*n)"
            ),
            "derivation": [
                "cot(x)=cos(x)/sin(x) >= 1/x-x/2",
                "x=pi/(2*n)",
                "pi<22/7",
            ],
        },
        "records": records,
        "interpretation": [
            "For n asymptotic to q, odd divisor support is Omega(sqrt(n)).",
            "This closes bounded low-divisor-degree rational-character mechanisms, not succinct high-degree straight-line programs.",
            "A high-degree pullback or Miller/EDS construction can have short syntax, so representation and evaluation cost still require a separate argument.",
            "No external target, wallet, real key or unknown production scalar is used.",
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
            "experiments/uorc056/parity_spectrum_barrier_results.json"
        ),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = stable_json(run(args.grammar))
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("parity spectrum barrier result drift")
        print("UORC056_PARITY_SPECTRUM_BARRIER_OK")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
