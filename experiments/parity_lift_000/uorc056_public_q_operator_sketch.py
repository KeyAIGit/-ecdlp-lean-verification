#!/usr/bin/env python3
"""Exact public-Q operator-state barriers for UORC-056 C27.

This package separates three public-Q representation grammars:

1. base-field linear quotient states for the cyclic translation algebra;
2. sparse trace sketches of fixed relative-translation monomials;
3. coordinate-sparse bilinear/Krylov probes.

The code uses only public group orders, public field primes, deterministic
integer arithmetic, and fixed synthetic supports. It accepts no unknown
production point, private key, wallet, hidden scalar, or target-dependent
advice.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import itertools
import json
import math
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

PROFILE_ID = "UORC-056-PUBLIC-Q-OPERATOR-SKETCH-C27"
DEFAULT_OUTPUT = Path(
    "experiments/parity_lift_000/"
    "uorc056_public_q_operator_sketch_result.json"
)

SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP_LINEAR_DEGREE = (SECP_N - 1) // 6
SECP_HALF = (SECP_N - 1) // 2

# Public toy (base-field prime, subgroup order) pairs already frozen in UORC-056.
# The p=n=127 case is retained for trace/Krylov combinatorics but excluded from
# the semisimple base-field representation theorem because char(F_p) divides n.
FROZEN_FIELD_ORDER_PAIRS = (
    (43, 31),
    (67, 79),
    (79, 67),
    (127, 127),
    (163, 139),
)

SECP_LINEAR_DEGREE_FACTORIZATION = {
    2: 5,
    149: 1,
    631: 1,
    107361793816595537: 1,
    174723607534414371449: 1,
    341948486974166000522343609283189: 1,
}

# Complete recursive Lucas certificates for every prime used in the
# factorization of (n-1)/6. A node p>2 stores the complete factorization of
# p-1 and one Lucas witness a:
#   a^(p-1)=1 mod p,
#   gcd(a^((p-1)/q)-1,p)=1 for every prime q | p-1.
# The verifier below uses only Python's exact pow and gcd.
_LUCAS_CERTIFICATES_B85 = (
    "c-pO4%Z}SH47}$nf}DF0-%|gkC|aPG7U(X}!(#uvYV25+8(ZWiN6Yc>G31cS+v$A1Kr&LWLK#$w2-)TH`K`XG@4kQe`ugkl%W_bUus-mo+Y_jkQcqwx$&v}W6V{5HuD`k-y-#m0e}26F{Pyw>oKEv;b*2oh<AO}{xA!o$VZsoyIV%Tl;tG-iNitvPn2^S>)WbF=dKxAV9abrrZ%1<2L87fZ^*PF+$}pd+ie?t65Bk4amM7d$kj)v|+(aMq;hMh|IXZcFbh!hB4M~#;F$0qUJ6LKJ41EbppFd903(3+UtKYCCE#MTFY+)(bl<CIx9h1P#W|UYQ7j3v$FxqT**T9`X+ZPF*)kf;mOQe9k!?>kk8a*qDjXL|f5;J57$lRtx`EbhO%8Wi>1^kh%Oh(k(oREo4p>}mu9~2X1<6<VcZZiQEvGhDrk_y>V%R==KX!D_g6jD_4dK{Uy=FM#9MP!!a9;vJwl9xF-_Q%ndV~iUGp%tqUGqv%!--w}b=B&lIPT`c2AQIP+R<N$IIlPRvjHR-vmE&S{<Rr}Q5OSWd5xL_|74}R(YBnIS5FBmaZJ}Qc{f{ZNmA+mIaq(GxKsV9X&h573O<Et@CbW4j@7is>Amhk}&aZXS>psKL5_p@4<Jm1S&3BQZ;dKCy)`6iOsXcZL7)KN~F!b3dSgSasa_UcSn@#)hIP}{;6HmG7O&ioWJF~QeZrFQwdiGK5NS?Sjz7leJ{|ot{gv<"
)
_LUCAS_CERTIFICATES_JSON = zlib.decompress(
    base64.b85decode(_LUCAS_CERTIFICATES_B85)
).decode("utf-8")
LUCAS_CERTIFICATES: dict[int, dict[str, Any]] = {
    int(key): {
        "factors": {int(q): int(e) for q, e in value["factors"].items()},
        "witness": int(value["witness"]),
    }
    for key, value in json.loads(_LUCAS_CERTIFICATES_JSON).items()
}


def stable_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def digest_without_digest(value: dict[str, Any]) -> str:
    payload = dict(value)
    payload.pop("digest", None)
    return hashlib.sha256(stable_json(payload).encode("utf-8")).hexdigest()


def canonical_parity(k: int) -> int:
    """Return +1 for an even canonical representative and -1 for odd."""
    return 1 if k % 2 == 0 else -1


def factorization_product(factors: dict[int, int]) -> int:
    product = 1
    for prime, exponent in factors.items():
        if exponent < 1:
            raise AssertionError("factor exponent must be positive")
        product *= prime**exponent
    return product


def verify_lucas_certificates() -> dict[str, Any]:
    verified: set[int] = set()

    def verify(prime: int) -> None:
        if prime in verified:
            return
        if prime not in LUCAS_CERTIFICATES:
            raise AssertionError(f"missing Lucas certificate for {prime}")
        node = LUCAS_CERTIFICATES[prime]
        factors: dict[int, int] = node["factors"]
        witness = int(node["witness"])
        if prime == 2:
            if factors or witness != 1:
                raise AssertionError("invalid base certificate for 2")
            verified.add(prime)
            return
        if factorization_product(factors) != prime - 1:
            raise AssertionError(f"incomplete factorization of {prime}-1")
        for factor in factors:
            verify(factor)
        if pow(witness, prime - 1, prime) != 1:
            raise AssertionError(f"Lucas Fermat condition failed for {prime}")
        for factor in factors:
            residue = pow(witness, (prime - 1) // factor, prime)
            if math.gcd(residue - 1, prime) != 1:
                raise AssertionError(
                    f"Lucas order condition failed for {prime}, factor {factor}"
                )
        verified.add(prime)

    for prime in SECP_LINEAR_DEGREE_FACTORIZATION:
        verify(prime)
    return {
        "certificate_nodes": len(verified),
        "largest_certified_prime": max(verified),
        "all_required_factor_primes_certified": True,
    }


def multiplicative_order_from_factorization(
    base: int,
    modulus: int,
    expected_order: int,
    order_factorization: dict[int, int],
) -> dict[str, Any]:
    if factorization_product(order_factorization) != expected_order:
        raise AssertionError("order factorization product drifted")
    if math.gcd(base, modulus) != 1:
        raise AssertionError("base is not a unit modulo modulus")
    if pow(base, expected_order, modulus) != 1:
        raise AssertionError("claimed order does not annihilate the base")
    witnesses: dict[str, int] = {}
    for prime in order_factorization:
        value = pow(base, expected_order // prime, modulus)
        if value == 1:
            raise AssertionError(
                f"claimed order is divisible by a removable prime {prime}"
            )
        witnesses[str(prime)] = value
    return {
        "base": base,
        "modulus": modulus,
        "exact_order": expected_order,
        "exact_order_bits": expected_order.bit_length(),
        "factorization": {
            str(prime): exponent
            for prime, exponent in sorted(order_factorization.items())
        },
        "proper_divisor_witnesses": witnesses,
    }


def factor_small(value: int) -> dict[int, int]:
    if value < 1:
        raise ValueError("factor_small expects a positive integer")
    factors: dict[int, int] = {}
    divisor = 2
    remaining = value
    while divisor * divisor <= remaining:
        while remaining % divisor == 0:
            factors[divisor] = factors.get(divisor, 0) + 1
            remaining //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if remaining > 1:
        factors[remaining] = factors.get(remaining, 0) + 1
    return factors


def multiplicative_order_small(base: int, prime_modulus: int) -> int:
    if math.gcd(base, prime_modulus) != 1:
        raise ValueError("base must be a unit")
    candidate = prime_modulus - 1
    for factor in factor_small(prime_modulus - 1):
        while candidate % factor == 0 and pow(
            base, candidate // factor, prime_modulus
        ) == 1:
            candidate //= factor
    if pow(base, candidate, prime_modulus) != 1:
        raise AssertionError("small multiplicative-order computation failed")
    return candidate


@dataclass(frozen=True)
class TraceAtom:
    """One fixed monomial c*T_G^a*T_Q^b in the regular translation algebra."""

    a: int
    b: int
    coefficient: int = 1


TraceChannel = tuple[TraceAtom, ...]


def trace_shift(order: int, exponent: int) -> int:
    """Integer trace of the order-n regular cyclic shift by exponent."""
    return order if exponent % order == 0 else 0


def trace_channel(order: int, scalar: int, channel: TraceChannel) -> int:
    return sum(
        atom.coefficient
        * trace_shift(order, atom.a + atom.b * scalar)
        for atom in channel
    )


def trace_transcript(
    order: int, scalar: int, channels: Sequence[TraceChannel]
) -> tuple[int, ...]:
    return tuple(trace_channel(order, scalar, channel) for channel in channels)


def atom_exceptional_residue(order: int, atom: TraceAtom) -> int | None:
    b = atom.b % order
    if b == 0:
        return None
    residue = (-atom.a * pow(b, -1, order)) % order
    return residue if residue != 0 else None


def trace_exceptional_residues(
    order: int, channels: Sequence[TraceChannel]
) -> set[int]:
    residues: set[int] = set()
    for channel in channels:
        for atom in channel:
            residue = atom_exceptional_residue(order, atom)
            if residue is not None:
                residues.add(residue)
    return residues


def transcript_decodes_parity(
    order: int, channels: Sequence[TraceChannel]
) -> bool:
    fibres: dict[tuple[int, ...], set[int]] = {}
    for scalar in range(1, order):
        fibres.setdefault(trace_transcript(order, scalar, channels), set()).add(
            canonical_parity(scalar)
        )
    return all(len(values) == 1 for values in fibres.values())


def parity_is_mixed_outside(order: int, exceptional: set[int]) -> bool:
    parities = {
        canonical_parity(scalar)
        for scalar in range(1, order)
        if scalar not in exceptional
    }
    return len(parities) > 1


def tight_trace_channel(order: int, target_parity: int = -1) -> TraceChannel:
    residues = [
        scalar
        for scalar in range(1, order)
        if canonical_parity(scalar) == target_parity
    ]
    return tuple(TraceAtom(a=(-scalar) % order, b=1) for scalar in residues)


def exhaustive_exceptional_set_check(order: int) -> dict[str, Any]:
    domain = tuple(range(1, order))
    half = (order - 1) // 2
    subsets_checked = 0
    for size in range(half):
        for subset in itertools.combinations(domain, size):
            subsets_checked += 1
            if not parity_is_mixed_outside(order, set(subset)):
                raise AssertionError(
                    "an exceptional set below half the cycle made parity constant"
                )
    return {
        "order": order,
        "half": half,
        "subsets_below_half_checked": subsets_checked,
        "all_complements_mixed": True,
    }


@dataclass(frozen=True)
class BilinearProbe:
    """Coordinate-sparse u^T T_G^a T_Q^b v probe."""

    a: int
    b: int
    left_support: tuple[int, ...]
    right_support: tuple[int, ...]


def probe_exceptional_residues(order: int, probe: BilinearProbe) -> set[int]:
    b = probe.b % order
    if b == 0:
        return set()
    inv_b = pow(b, -1, order)
    return {
        ((left - right - probe.a) * inv_b) % order
        for left in probe.left_support
        for right in probe.right_support
        if ((left - right - probe.a) * inv_b) % order != 0
    }


def probe_value(order: int, scalar: int, probe: BilinearProbe) -> int:
    exponent = (probe.a + probe.b * scalar) % order
    return sum(
        1
        for left in probe.left_support
        for right in probe.right_support
        if (left - right) % order == exponent
    )


def probe_transcript(
    order: int, scalar: int, probes: Sequence[BilinearProbe]
) -> tuple[int, ...]:
    return tuple(probe_value(order, scalar, probe) for probe in probes)


def probes_decode_parity(
    order: int, probes: Sequence[BilinearProbe]
) -> bool:
    fibres: dict[tuple[int, ...], set[int]] = {}
    for scalar in range(1, order):
        fibres.setdefault(probe_transcript(order, scalar, probes), set()).add(
            canonical_parity(scalar)
        )
    return all(len(values) == 1 for values in fibres.values())


def probe_cross_support_cost(probes: Sequence[BilinearProbe]) -> int:
    return sum(
        len(probe.left_support) * len(probe.right_support)
        for probe in probes
        if probe.b != 0
    )


def tight_probe(order: int, target_parity: int = -1) -> BilinearProbe:
    support = tuple(
        scalar
        for scalar in range(1, order)
        if canonical_parity(scalar) == target_parity
    )
    return BilinearProbe(
        a=0,
        b=1,
        left_support=support,
        right_support=(0,),
    )


def minimum_full_moment_depth(target_atoms: int) -> int:
    """Smallest d with sum_{m=1}^d m(m+1)/2 >= target_atoms."""
    low, high = 0, 1
    while high * (high + 1) * (high + 2) // 6 < target_atoms:
        high *= 2
    while low < high:
        middle = (low + high) // 2
        capacity = middle * (middle + 1) * (middle + 2) // 6
        if capacity >= target_atoms:
            high = middle
        else:
            low = middle + 1
    return low


def toy_record(order: int) -> dict[str, Any]:
    half = (order - 1) // 2
    trace_channel_tight = tight_trace_channel(order)
    if len(trace_channel_tight) != half:
        raise AssertionError("tight trace atom count drifted")
    if not transcript_decodes_parity(order, (trace_channel_tight,)):
        raise AssertionError("tight trace channel failed to decode parity")
    exceptional = trace_exceptional_residues(order, (trace_channel_tight,))
    if len(exceptional) != half:
        raise AssertionError("tight trace exceptional set drifted")

    probe = tight_probe(order)
    if probe_cross_support_cost((probe,)) != half:
        raise AssertionError("tight probe cross-support cost drifted")
    if not probes_decode_parity(order, (probe,)):
        raise AssertionError("tight bilinear probe failed to decode parity")
    probe_exceptional = probe_exceptional_residues(order, probe)
    if len(probe_exceptional) != half:
        raise AssertionError("tight probe exceptional set drifted")

    library = (
        (
            TraceAtom(0, 0, 3),
            TraceAtom(1, 1, 2),
            TraceAtom(2, 3, -1),
        ),
        (
            TraceAtom(4, 2, 5),
            TraceAtom(-3, 1, 7),
        ),
    )
    direct_trace_checks = 0
    for scalar in range(1, order):
        for channel in library:
            direct = sum(
                atom.coefficient
                * (order if (atom.a + atom.b * scalar) % order == 0 else 0)
                for atom in channel
            )
            if trace_channel(order, scalar, channel) != direct:
                raise AssertionError("regular-shift trace identity failed")
            direct_trace_checks += 1

    return {
        "order": order,
        "half_parity_fibre": half,
        "trace_atom_lower_bound": half,
        "tight_trace_atoms": len(trace_channel_tight),
        "tight_trace_decoder_passed": True,
        "krylov_cross_support_lower_bound": half,
        "tight_krylov_cross_support": probe_cross_support_cost((probe,)),
        "tight_krylov_decoder_passed": True,
        "direct_trace_checks": direct_trace_checks,
    }


def build_result() -> dict[str, Any]:
    lucas = verify_lucas_certificates()
    secp_order = multiplicative_order_from_factorization(
        SECP_P,
        SECP_N,
        SECP_LINEAR_DEGREE,
        SECP_LINEAR_DEGREE_FACTORIZATION,
    )
    if secp_order["exact_order"] != SECP_LINEAR_DEGREE:
        raise AssertionError("secp exact order drifted")

    toy_linear_rows: list[dict[str, Any]] = []
    for field_prime, subgroup_order in FROZEN_FIELD_ORDER_PAIRS:
        if field_prime % subgroup_order == 0:
            toy_linear_rows.append(
                {
                    "field_prime": field_prime,
                    "subgroup_order": subgroup_order,
                    "semisimple_linear_theorem_applies": False,
                    "reason": "base-field characteristic divides subgroup order",
                }
            )
            continue
        exact_order = multiplicative_order_small(
            field_prime % subgroup_order, subgroup_order
        )
        toy_linear_rows.append(
            {
                "field_prime": field_prime,
                "subgroup_order": subgroup_order,
                "semisimple_linear_theorem_applies": True,
                "minimum_nontrivial_base_field_linear_dimension": exact_order,
            }
        )

    small_exhaustive = [
        exhaustive_exceptional_set_check(order)
        for order in (5, 7, 11, 13)
    ]
    toy_rows = [toy_record(order) for order in (31, 79, 67, 127, 139)]
    moment_depth = minimum_full_moment_depth(SECP_HALF)
    previous_capacity = (
        (moment_depth - 1) * moment_depth * (moment_depth + 1) // 6
    )
    current_capacity = (
        moment_depth * (moment_depth + 1) * (moment_depth + 2) // 6
    )
    if not previous_capacity < SECP_HALF <= current_capacity:
        raise AssertionError("moment-depth minimality failed")

    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "profile_id": PROFILE_ID,
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "input_contracts": {
            "numeric_k": "(n,k,a,b,c); may branch on k and is not credited as public-Q",
            "public_Q": "(E,G,Q=[k]G,n,a,b,c); k, its bits, quotients and tables are forbidden inputs",
        },
        "linear_state_theorem": {
            "statement": (
                "For char(F_p) not dividing prime n, every nontrivial "
                "F_p-linear representation of C_n has dimension at least "
                "ord_n(p). A representation below that dimension is trivial "
                "and makes every state built only from rho(G),rho(Q) "
                "independent of k."
            ),
            "secp256k1_order_certificate": secp_order,
            "lucas_prime_certificates": lucas,
            "secp256k1_minimum_nontrivial_dimension": SECP_LINEAR_DEGREE,
            "secp256k1_minimum_nontrivial_dimension_bits": (
                SECP_LINEAR_DEGREE.bit_length()
            ),
            "secp256k1_below_sqrt_gate": False,
            "toy_rows": toy_linear_rows,
            "formalization_boundary": (
                "Python verifies the complete Lucas certificates and exact "
                "multiplicative-order witnesses. Lean checks the generic "
                "information/counting transfer and fixed secp integer bounds, "
                "not the full finite-field representation theorem."
            ),
        },
        "sparse_trace_sketch_theorem": {
            "model": (
                "r public channels Tr(sum c_ab T_G^a T_Q^b), with fixed "
                "k-independent sparse monomial supports; expanded relative "
                "translation atoms are charged"
            ),
            "identity": "Tr(T_G^a T_Q^b)=n if a+b*k=0 mod n, else 0",
            "invariant": (
                "outside the union E of exceptional ratios -a/b, the entire "
                "transcript is constant"
            ),
            "exact_lower_bound": "(n-1)/2 distinct nonzero exceptional ratios",
            "secp256k1_distinct_atom_lower_bound": SECP_HALF,
            "secp256k1_lower_bound_bits": SECP_HALF.bit_length(),
            "bound_is_tight_in_expanded_atom_model": True,
            "tight_witness": (
                "one trace channel summing one monomial for every odd "
                "canonical scalar; this is exactly the forbidden half-orbit table"
            ),
            "small_exhaustive_checks": small_exhaustive,
            "frozen_replay": toy_rows,
        },
        "coordinate_sparse_krylov_theorem": {
            "model": (
                "fixed probes u_i^T T_G^a_i T_Q^b_i v_i with coordinate-sparse "
                "public vectors; every support coordinate and cross pair is charged"
            ),
            "invariant": (
                "probe i is zero outside at most |supp(u_i)|*|supp(v_i)| "
                "relative translations"
            ),
            "exact_lower_bound": (
                "sum_i |supp(u_i)|*|supp(v_i)| >= (n-1)/2"
            ),
            "secp256k1_cross_support_lower_bound": SECP_HALF,
            "secp256k1_lower_bound_bits": SECP_HALF.bit_length(),
            "bound_is_tight_in_coordinate_sparse_model": True,
        },
        "newton_moment_corollary": {
            "scope": (
                "expanded traces of all powers (aI+bT_G+cT_Q)^m for 1<=m<=d, "
                "with m<n and every relative-translation monomial charged"
            ),
            "expanded_nonconstant_atom_capacity": "d(d+1)(d+2)/6",
            "secp256k1_minimum_full_moment_depth": moment_depth,
            "secp256k1_minimum_depth_bits": moment_depth.bit_length(),
            "previous_depth_capacity": previous_capacity,
            "minimum_depth_capacity": current_capacity,
            "warning": (
                "This cubic-depth corollary is not a lower bound against an "
                "implicit nonlinear moment recurrence whose expanded atoms are "
                "never materialized."
            ),
        },
        "decision": {
            "sublinear_numeric_k_lacunary_algorithm_found": False,
            "numeric_k_control_eliminated": False,
            "sublinear_public_Q_operator_representation_found": False,
            "sublinear_base_field_linear_quotient_found": False,
            "sublinear_sparse_trace_sketch_found": False,
            "sublinear_coordinate_sparse_krylov_found": False,
            "sublinear_black_box_determinant_found": False,
            "projective_cubic_exact_phase_decoder_found": False,
            "a_eq_b_exact_value_formula_found": False,
            "all_point_public_Q_replay_passed": False,
            "exact_parity_extraction_found": False,
            "exact_Hilbert90_branch_bridge_found": False,
            "complete_cost_gate_passed": False,
            "compact_branch_odd_evaluator_found": False,
            "sub_sqrt_evaluator_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "closed_classes": [
            "nontrivial base-field linear quotient state below ord_n(p)",
            "fixed sparse trace sketches with fewer than (n-1)/2 relative-translation atoms",
            "coordinate-sparse bilinear/Krylov probes with total cross-support below (n-1)/2",
        ],
        "not_closed": [
            "nonlinear implicit-spectrum arithmetic circuits",
            "structured dense vectors generated and queried without linear storage",
            "black-box determinant algorithms outside the declared sparse probes",
            "modular composition and nonlinear algebraic-state recurrences",
            "p-adic, theta, elliptic-unit, or Hilbert-90 branch-sensitive states",
        ],
        "successor": (
            "NONLINEAR-PUBLIC-Q-ALGEBRAIC-STATE-077: bound or construct "
            "bounded-dimensional nonlinear rational dynamics with an explicit "
            "branch-sensitive public leaf and complete cost ledger"
        ),
    }
    payload["digest"] = digest_without_digest(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = stable_json(build_result())
    if args.check:
        if not args.out.exists():
            raise SystemExit(f"missing frozen C27 result: {args.out}")
        if args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("C27 public-Q operator-sketch artifact drift")
        print("UORC056_PUBLIC_Q_OPERATOR_SKETCH_C27_OK")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
