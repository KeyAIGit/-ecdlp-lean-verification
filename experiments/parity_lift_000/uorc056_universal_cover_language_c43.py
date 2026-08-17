#!/usr/bin/env python3
"""Exact replay for UORC-056 C43 universal-cover and gauge-language atlas.

The package uses only public constants, synthetic cyclic groups, and frozen toy
orders. It accepts no external point, wallet, key, or unknown production scalar.
"""
from __future__ import annotations

import argparse
import cmath
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import mpmath as mp
import sympy as sp

SECP_P = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16
)
SECP_N = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16
)
SECP_N_MINUS_ONE_FACTORS = {
    2: 6,
    3: 1,
    149: 1,
    631: 1,
    107361793816595537: 1,
    174723607534414371449: 1,
    341948486974166000522343609283189: 1,
}
SECP_P_MINUS_ONE_FACTORS = {
    2: 1,
    3: 1,
    7: 1,
    13441: 1,
    205115282021455665897114700593932402728804164701536103180137503955397371: 1,
}
FROZEN_ORDERS = (31, 79, 67, 127, 139)
HELD_OUT_ORDER = 61
DIAGNOSTIC_ORDERS = (5, 7, 11, 13, 17, 19, *FROZEN_ORDERS, HELD_OUT_ORDER)


def canonical(value: int, order: int) -> int:
    return value % order


def parity_sign(value: int, order: int) -> int:
    """Canonical parity on residues 0,...,order-1."""
    return 1 if canonical(value, order) % 2 == 0 else -1


def carry(a: int, b: int, order: int) -> int:
    """The section defect for the canonical section C_n -> Z."""
    aa, bb = canonical(a, order), canonical(b, order)
    return (aa + bb - canonical(aa + bb, order)) // order


def gauge_profile(value: int, order: int, seed: int) -> int:
    """A deterministic integer-valued section gauge."""
    residue = canonical(value, order)
    return ((seed * residue + residue * residue + 3) % 5) - 2


def verify_universal_cover(order: int) -> dict[str, int | bool]:
    if order <= 1 or order % 2 == 0:
        raise ValueError("order must be odd and greater than one")

    addition_checks = 0
    cocycle_checks = 0
    gauge_checks = 0

    for a in range(order):
        for b in range(order):
            c = carry(a, b, order)
            lhs = parity_sign(a + b, order)
            rhs = parity_sign(a, order) * parity_sign(b, order) * ((-1) ** c)
            if lhs != rhs:
                raise AssertionError("canonical section carry identity failed")
            addition_checks += 1

            for d in range(order):
                left = carry(a, b, order) + carry(a + b, d, order)
                right = carry(b, d, order) + carry(a, b + d, order)
                if left != right:
                    raise AssertionError("integer carry cocycle failed")
                cocycle_checks += 1

    for seed in (1, 3, 7):
        for residue in range(order):
            t = gauge_profile(residue, order, seed)
            lifted = residue + order * t
            if canonical(lifted, order) != residue:
                raise AssertionError("gauged section stopped being a section")
            ratio = 1 if (lifted - residue) % 2 == 0 else -1
            expected_ratio = 1 if t % 2 == 0 else -1
            if ratio != expected_ratio:
                raise AssertionError("section-gauge sign law failed")
            gauge_checks += 1

    if ((-1) ** order) != -1:
        raise AssertionError("cover character unexpectedly descends")

    pair_components = (order - 1) // 2
    return {
        "order": order,
        "addition_checks": addition_checks,
        "cocycle_checks": cocycle_checks,
        "gauge_checks": gauge_checks,
        "cover_character_descends": False,
        "pair_components": pair_components,
        "anchored_component_gauge_exponent": max(0, pair_components - 1),
    }


def verify_mu2_cohomology(order: int) -> dict[str, int | bool]:
    """Elementary H^1/H^2 splitting diagnostics for C_n with n odd."""
    if order % 2 == 0:
        raise ValueError("order must be odd")

    hom_images = [u for u in (-1, 1) if u**order == 1]
    if hom_images != [1]:
        raise AssertionError("a nontrivial C_n -> mu_2 character survived")

    splitting_checks = 0
    for extension_parameter in (-1, 1):
        rescale = extension_parameter
        normalized_parameter = (rescale**order) * extension_parameter
        if normalized_parameter != 1:
            raise AssertionError("mu_2 central extension did not split")
        splitting_checks += 1

    coboundary_checks = 0
    for a in range(order):
        for b in range(order):
            omega = (-1) ** carry(a, b, order)
            delta_sigma = (
                parity_sign(a, order)
                * parity_sign(b, order)
                * parity_sign(a + b, order)
            )
            if omega != delta_sigma:
                raise AssertionError("carry sign is not the parity coboundary")
            coboundary_checks += 1

    return {
        "order": order,
        "h1_mu2_nontrivial_classes": 0,
        "h2_mu2_nontrivial_classes": 0,
        "central_extension_splitting_checks": splitting_checks,
        "carry_coboundary_checks": coboundary_checks,
        "intrinsic_spin_bit_found": False,
    }


def multiplicative_order_from_factorization(
    base: int, modulus: int, group_order: int, factorization: dict[int, int]
) -> int:
    if pow(base, group_order, modulus) != 1:
        raise AssertionError("declared group order does not annihilate the base")
    result = group_order
    for prime, exponent in sorted(factorization.items()):
        if not sp.isprime(prime):
            raise AssertionError("declared factor is not prime")
        for _ in range(exponent):
            candidate = result // prime
            if pow(base, candidate, modulus) != 1:
                break
            result = candidate
    return result


def pair_action_order(base: int, prime_order: int, ordinary_order: int) -> int:
    """Order of multiplication by base on (Z/nZ)^*/{+-1}."""
    if ordinary_order % 2 == 0 and pow(base, ordinary_order // 2, prime_order) == (
        prime_order - 1
    ):
        return ordinary_order // 2
    return ordinary_order


def doubling_row(order: int) -> dict[str, int | bool]:
    if not sp.isprime(order):
        raise ValueError("diagnostic doubling rows require prime order")
    ordinary = int(sp.n_order(2, order))
    pair_order = pair_action_order(2, order, ordinary)
    pair_count = (order - 1) // 2
    if pair_count % pair_order != 0:
        raise AssertionError("pair action order does not divide pair count")
    return {
        "order": order,
        "ordinary_order_of_two": ordinary,
        "pair_action_order": pair_order,
        "pair_action_cycles": pair_count // pair_order,
        "pair_action_transitive": pair_count == pair_order,
    }


def verify_symbolic_doubling(order: int) -> dict[str, int | bool]:
    if order % 2 == 0:
        raise ValueError("order must be odd")
    checks = 0
    max_steps = 2 * order
    for scalar in range(1, order):
        for step in range(max_steps):
            residue = (pow(2, step, order) * scalar) % order
            next_residue = (2 * residue) % order
            digit = (2 * residue) // order
            long_division_digit = (
                (pow(2, step + 1) * scalar) // order
                - 2 * ((pow(2, step) * scalar) // order)
            )
            if digit != long_division_digit:
                raise AssertionError("doubling carry is not the binary digit")
            if next_residue % 2 != digit:
                raise AssertionError("next parity is not the doubling carry")
            if parity_sign(next_residue, order) != ((-1) ** digit):
                raise AssertionError("doubling parity sign identity failed")
            checks += 1
    return {
        "order": order,
        "symbolic_dynamics_checks": checks,
        "doubling_carry_is_binary_digit": True,
        "parity_recovered_from_public_coordinates": False,
        "reason": "the carry itself is the hidden upper-half branch",
    }


def secp_doubling_certificate() -> dict[str, object]:
    reconstructed_n = math.prod(
        prime**exponent for prime, exponent in SECP_N_MINUS_ONE_FACTORS.items()
    )
    reconstructed_p = math.prod(
        prime**exponent for prime, exponent in SECP_P_MINUS_ONE_FACTORS.items()
    )
    if reconstructed_n != SECP_N - 1:
        raise AssertionError("secp n-1 factorization product mismatch")
    if reconstructed_p != SECP_P - 1:
        raise AssertionError("secp p-1 factorization product mismatch")

    order_mod_n = multiplicative_order_from_factorization(
        2, SECP_N, SECP_N - 1, SECP_N_MINUS_ONE_FACTORS
    )
    order_mod_p = multiplicative_order_from_factorization(
        2, SECP_P, SECP_P - 1, SECP_P_MINUS_ONE_FACTORS
    )
    expected_n = (SECP_N - 1) // 64
    expected_p = (SECP_P - 1) // 14
    if order_mod_n != expected_n:
        raise AssertionError("unexpected exact order of 2 modulo secp n")
    if order_mod_p != expected_p:
        raise AssertionError("unexpected exact order of 2 modulo secp p")

    pair_order = pair_action_order(2, SECP_N, order_mod_n)
    pair_count = (SECP_N - 1) // 2
    cycles = pair_count // pair_order
    if cycles != 32:
        raise AssertionError("unexpected secp pair-quotient cycle count")
    if pow(2, pair_order, SECP_N) != 1:
        raise AssertionError("pair action order certificate failed")
    minimality_n = {
        str(prime): pow(2, pair_order // prime, SECP_N)
        for prime in sorted(SECP_N_MINUS_ONE_FACTORS)
        if prime != 2
    }
    minimality_p = {
        str(prime): pow(2, order_mod_p // prime, SECP_P)
        for prime in sorted(SECP_P_MINUS_ONE_FACTORS)
        if order_mod_p % prime == 0
    }
    if any(value == 1 for value in minimality_n.values()):
        raise AssertionError("secp order modulo n minimality witness failed")
    if any(value == 1 for value in minimality_p.values()):
        raise AssertionError("secp order modulo p minimality witness failed")

    return {
        "n": SECP_N,
        "p": SECP_P,
        "n_minus_one_factorization": {
            str(prime): exponent
            for prime, exponent in sorted(SECP_N_MINUS_ONE_FACTORS.items())
        },
        "p_minus_one_factorization": {
            str(prime): exponent
            for prime, exponent in sorted(SECP_P_MINUS_ONE_FACTORS.items())
        },
        "order_of_two_mod_n": order_mod_n,
        "order_of_two_mod_p": order_mod_p,
        "pair_components": pair_count,
        "pair_action_order": pair_order,
        "pair_action_cycles": cycles,
        "pair_action_transitive": False,
        "rejected_claims": [
            "ord_n(2)=(n-1)/2",
            "ord_p(2)=(n-1)/2",
            "doubling is transitive on the secp pair quotient",
        ],
        "correct_identities": [
            "ord_n(2)=(n-1)/64",
            "ord_p(2)=(p-1)/14",
            "the secp pair quotient has 32 doubling cycles",
        ],
        "minimality_residues_mod_n": minimality_n,
        "minimality_residues_mod_p": minimality_p,
    }


def verify_p_adic_log_boundary(order: int) -> dict[str, int | bool]:
    """Finite p-power shadows of the torsion-free additive-log argument."""
    if order % 2 == 0:
        raise ValueError("order must be odd")
    checks = 0
    for prime in (2, 3, 5, 7, 11, 13):
        if order % prime == 0:
            continue
        for exponent in (1, 2, 3, 4):
            modulus = prime**exponent
            survivors = [x for x in range(modulus) if (order * x) % modulus == 0]
            if survivors != [0]:
                raise AssertionError(
                    "prime-to-p torsion survived in additive p-power shadow"
                )
            checks += modulus
    return {
        "order": order,
        "finite_p_power_state_checks": checks,
        "hom_to_torsion_free_additive_group_is_zero": True,
        "ordinary_p_adic_log_phase_found": False,
        "surviving_class": "nonhomomorphic marked p-adic polylogarithm or regulator",
    }


def cyclic_sign_changes(order: int) -> int:
    values = [parity_sign(k, order) for k in range(order)]
    return sum(values[k] != values[(k + 1) % order] for k in range(order))


def verify_tropical_boundary(order: int) -> dict[str, int | bool]:
    changes = cyclic_sign_changes(order)
    if changes != order - 1:
        raise AssertionError("odd cyclic parity word has wrong alternation count")
    return {
        "order": order,
        "cyclic_sign_changes": changes,
        "minimum_zero_crossings": changes,
        "minimum_nonzero_affine_segments": changes,
        "sublinear_piecewise_linear_decoder": False,
    }


def nonzero_parity_fourier(order: int, frequency: int) -> complex:
    root = cmath.exp(-2j * math.pi * frequency / order)
    return sum(((-1) ** k) * (root**k) for k in range(1, order))


def verify_fourier_formula(order: int) -> dict[str, int | float | bool]:
    frequency = (order - 1) // 2
    observed = abs(nonzero_parity_fourier(order, frequency))
    expected = 1.0 / math.tan(math.pi / (2 * order))
    if not math.isclose(observed, expected, rel_tol=1e-10, abs_tol=1e-10):
        raise AssertionError("nonzero parity Fourier peak formula failed")
    return {
        "order": order,
        "peak_frequency": frequency,
        "observed_peak": observed,
        "cotangent_peak": expected,
        "formula_verified": True,
    }


def secp_trace_function_boundary(identity_bound: int = 1) -> dict[str, object]:
    mp.mp.dps = 120
    n = mp.mpf(SECP_N)
    p = mp.mpf(SECP_P)
    peak = 1 / mp.tan(mp.pi / (2 * n))
    required = (peak - identity_bound) / mp.sqrt(p)
    if required <= 0:
        raise AssertionError("trace-function lower bound is not positive")
    return {
        "identity_value_bound": identity_bound,
        "nonzero_fourier_peak": mp.nstr(peak, 50),
        "required_square_root_twist_constant": mp.nstr(required, 50),
        "required_constant_log2": float(mp.log(required, 2)),
        "interpretation": (
            "any candidate class with a uniform twist bound B*sqrt(p) "
            "needs B at least this large"
        ),
    }


@dataclass(frozen=True)
class GaugeType:
    """A Z/2 endpoint-charge type represented by a bit mask."""

    mask: int

    def multiply(self, other: "GaugeType") -> "GaugeType":
        return GaugeType(self.mask ^ other.mask)

    def square(self) -> "GaugeType":
        return GaugeType(0)

    def add(self, other: "GaugeType") -> "GaugeType":
        if self.mask != other.mask:
            raise TypeError("addition requires equal gauge charge")
        return self

    @property
    def neutral(self) -> bool:
        return self.mask == 0


def vertex_charge(index: int) -> GaugeType:
    return GaugeType(1 << index)


def transfer_charge(source: int, target: int) -> GaugeType:
    return vertex_charge(source).multiply(vertex_charge(target))


def verify_gauge_type_system(vertices: int = 9) -> dict[str, int | bool]:
    if vertices < 3:
        raise ValueError("at least three vertices are required")
    checks = 0
    for source in range(vertices):
        for target in range(vertices):
            edge = transfer_charge(source, target)
            if not edge.square().neutral:
                raise AssertionError("transfer square is not gauge neutral")
            checks += 1

    loop = GaugeType(0)
    for i in range(vertices):
        loop = loop.multiply(transfer_charge(i, (i + 1) % vertices))
    if not loop.neutral:
        raise AssertionError("closed loop retained endpoint charge")

    start, end = 1, vertices - 2
    open_path = GaugeType(0)
    for i in range(start, end):
        open_path = open_path.multiply(transfer_charge(i, i + 1))
    expected = transfer_charge(start, end)
    if open_path != expected:
        raise AssertionError("open path did not telescope to endpoint charge")

    neutral_atoms = [
        transfer_charge(0, 1).square(),
        loop,
        GaugeType(0),
    ]
    state = GaugeType(0)
    for atom in neutral_atoms:
        state = state.multiply(atom)
    if not state.neutral:
        raise AssertionError("neutral grammar unexpectedly created charge")
    if state == expected:
        raise AssertionError("neutral grammar synthesized open target")

    return {
        "vertices": vertices,
        "edge_square_checks": checks,
        "closed_loop_neutral": True,
        "open_path_endpoint_charge": expected.mask,
        "neutral_grammar_can_build_parity_charge": False,
        "surviving_typed_object": "anchor-to-query open transport",
    }


def build_payload() -> dict[str, object]:
    universal = [verify_universal_cover(order) for order in DIAGNOSTIC_ORDERS]
    cohomology = [verify_mu2_cohomology(order) for order in DIAGNOSTIC_ORDERS]
    symbolic = [verify_symbolic_doubling(order) for order in DIAGNOSTIC_ORDERS]
    doubling = [doubling_row(order) for order in (*FROZEN_ORDERS, HELD_OUT_ORDER)]
    p_adic = [verify_p_adic_log_boundary(order) for order in DIAGNOSTIC_ORDERS]
    tropical = [verify_tropical_boundary(order) for order in DIAGNOSTIC_ORDERS]
    fourier = [verify_fourier_formula(order) for order in DIAGNOSTIC_ORDERS]
    gauge_types = verify_gauge_type_system()
    secp_doubling = secp_doubling_certificate()
    trace = secp_trace_function_boundary()

    hypotheses = [
        {
            "id": "H1-UNIVERSAL-COVER-SECTION",
            "language": "central extension and set-theoretic section",
            "result": "exact positive normal form",
            "decision": (
                "parity is the cover character (-1)^z composed with the canonical "
                "section; it does not descend to the odd cyclic group"
            ),
        },
        {
            "id": "H2-MU2-COHOMOLOGY-SPIN",
            "language": "group cohomology and metaplectic splitting",
            "result": "closed",
            "decision": (
                "H^1(C_n,mu_2) and H^2(C_n,mu_2) are trivial for odd n; "
                "the carry cocycle is a coboundary"
            ),
        },
        {
            "id": "H3-DOUBLING-SYMBOLIC-DYNAMICS",
            "language": "binary long division and symbolic dynamics",
            "result": "exact recoding, not a decoder",
            "decision": (
                "the next parity bit equals the hidden upper-half carry, which is "
                "the next binary digit of k/n"
            ),
        },
        {
            "id": "H4-P-ADIC-LOG-LIFT",
            "language": "p-adic additive logarithms and period lifts",
            "result": "ordinary logarithmic route closed",
            "decision": (
                "any homomorphism from finite n-torsion to a torsion-free additive "
                "p-adic group is zero; a nonzero phase requires a noncanonical lift"
            ),
        },
        {
            "id": "H5-TROPICAL-SKELETON",
            "language": "piecewise-linear cyclic skeleton",
            "result": "linear representation boundary",
            "decision": (
                "the odd cyclic parity word has n-1 sign changes, so an exact "
                "thresholded PL decoder needs at least n-1 zero-crossing segments"
            ),
        },
        {
            "id": "H6-L-ADIC-TRACE-FUNCTION",
            "language": "character sheaves and arithmetic Fourier transform",
            "result": "square-root-twist transfer barrier",
            "decision": (
                "a class with twist bound B*sqrt(p) requires B=Omega(n/sqrt(p)); "
                "for secp256k1 the exact numeric lower bound exceeds 2^127.34"
            ),
        },
        {
            "id": "H7-GAUGE-TYPED-OPEN-TRANSPORT",
            "language": "Z/2 gauge type system for candidate ASTs",
            "result": "new exact static filter plus one surviving type",
            "decision": (
                "squares, norms, determinants and closed loops are neutral; only "
                "anchor-to-query open transport has the target endpoint charge"
            ),
        },
    ]

    payload: dict[str, object] = {
        "profile_id": "UORC-056-UNIVERSAL-COVER-LANGUAGE-C43",
        "schema_version": "1.0",
        "scope": {
            "external_targets_used": False,
            "production_unknown_scalars_used": False,
            "cheap_parity_decoder_claimed": False,
            "sub_sqrt_ecdlp_claimed": False,
        },
        "hypotheses": hypotheses,
        "universal_cover": universal,
        "mu2_cohomology": cohomology,
        "symbolic_doubling": symbolic,
        "frozen_doubling_actions": doubling,
        "secp256k1_doubling_correction": secp_doubling,
        "p_adic_log_boundary": p_adic,
        "tropical_boundary": tropical,
        "fourier_checks": fourier,
        "secp256k1_trace_boundary": trace,
        "gauge_type_system": gauge_types,
        "aggregate": {
            "hypotheses": len(hypotheses),
            "diagnostic_orders": len(DIAGNOSTIC_ORDERS),
            "universal_cover_addition_checks": sum(
                int(row["addition_checks"]) for row in universal
            ),
            "universal_cover_cocycle_checks": sum(
                int(row["cocycle_checks"]) for row in universal
            ),
            "symbolic_dynamics_checks": sum(
                int(row["symbolic_dynamics_checks"]) for row in symbolic
            ),
            "secp_pair_cycles": int(secp_doubling["pair_action_cycles"]),
            "errors": 0,
        },
        "decision": {
            "new_unifying_object_found": "canonical section of the universal cover",
            "new_search_language_found": "gauge-charged typed expressions",
            "old_transitivity_claim_correct": False,
            "ordinary_p_adic_log_route_open": False,
            "bounded_tropical_route_open": False,
            "bounded_trace_function_route_open": False,
            "only_surviving_local_type": "unsquared anchor-to-query open transport",
            "cheap_parity_decoder_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
    }

    canonical_bytes = json.dumps(
        payload, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    payload["digest"] = hashlib.sha256(canonical_bytes).hexdigest()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    payload = build_payload()
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print("UORC056_UNIVERSAL_COVER_LANGUAGE_C43_OK")
    print(json.dumps(payload["aggregate"], sort_keys=True))
    print("digest=" + str(payload["digest"]))


if __name__ == "__main__":
    main()
