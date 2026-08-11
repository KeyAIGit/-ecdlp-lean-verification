"""Generate the six deterministic, bounded P02 CI curve fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from math import gcd, isqrt
from pathlib import Path
from typing import Any, Iterator, Mapping

from experiments.ecdlp_lab.core.canonical import (
    canonical_json_bytes,
    load_json,
    sha256_bytes,
)

from .producer_adapter import (
    Curve,
    certified_prime_full_order,
    derive_integer,
    glv_parameters,
    is_prime,
    prime_factors,
    tonelli_shanks,
    verify_p1_arithmetic,
)

LAB_ROOT = Path(__file__).resolve().parent.parent
CI_SPEC_PATH = LAB_ROOT / "fixtures/curves/ci_catalog_spec_v1.json"
CI_CATALOG_PATH = LAB_ROOT / "fixtures/curves/ci_curve_catalog_v1.json"

FAMILIES = (
    "j0_glv_like",
    "random_generic_j_prime_subgroup",
    "j0_no_fp_glv_control",
)
FIELD_BITS = (11, 13)
REQUIRED_LIMITS = {
    "max_prime_candidates": 4096,
    "max_curve_candidates": 4096,
    "max_point_attempts": 1024,
}
GENERIC_CURVES_PER_PRIME = 64
MINIMUM_SUBGROUP_ORDER_BITS_MARGIN = 2


def _same_json(left: Any, right: Any) -> bool:
    """Compare JSON values without Python's ``False == 0`` coercion."""

    try:
        return canonical_json_bytes(left) == canonical_json_bytes(right)
    except (TypeError, ValueError):
        return False


class CatalogSpecError(ValueError):
    """Raised when the committed generator specification drifts."""


class SearchExhausted(RuntimeError):
    """Raised when one globally bounded per-fixture search counter is spent."""

    def __init__(self, family: str, field_bits: int, counter: str) -> None:
        super().__init__(f"{family}/{field_bits}: exhausted {counter}")
        self.family = family
        self.field_bits = field_bits
        self.counter = counter


@dataclass
class SearchState:
    family: str
    field_bits: int
    limits: Mapping[str, int]
    prime_candidates_examined: int = 0
    curve_candidates_examined: int = 0
    point_attempts: int = 0

    def consume(self, counter: str) -> int:
        limit_name = {
            "prime_candidates_examined": "max_prime_candidates",
            "curve_candidates_examined": "max_curve_candidates",
            "point_attempts": "max_point_attempts",
        }[counter]
        current = getattr(self, counter)
        if current >= self.limits[limit_name]:
            raise SearchExhausted(self.family, self.field_bits, limit_name)
        setattr(self, counter, current + 1)
        return current

    def receipt(self) -> dict[str, int]:
        return {
            "prime_candidates_examined": self.prime_candidates_examined,
            "curve_candidates_examined": self.curve_candidates_examined,
            "point_attempts": self.point_attempts,
        }


def render_spec(spec: Mapping[str, Any]) -> bytes:
    """Return the one deterministic persisted representation of the spec."""

    return json.dumps(
        dict(spec), ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False
    ).encode("utf-8") + b"\n"


def load_spec(path: Path | str = CI_SPEC_PATH) -> dict[str, Any]:
    """Load and validate the exact committed P02 generator specification."""

    document = load_json(path)
    if not isinstance(document, dict):
        raise CatalogSpecError("catalog spec root must be an object")
    expected_keys = {
        "schema_version",
        "spec_kind",
        "catalog_nonce",
        "field_bits",
        "family_order",
        "limits",
        "search_policy",
        "family_parameters",
    }
    if set(document) != expected_keys:
        raise CatalogSpecError("catalog spec top-level keys drifted")
    if type(document.get("schema_version")) is not int or document.get(
        "schema_version"
    ) != 1 or document.get("spec_kind") != (
        "ecdlp_lab_ci_curve_catalog_spec_v1"
    ):
        raise CatalogSpecError("catalog spec identity drifted")
    if document.get("catalog_nonce") != "ecdlp-lab-ci-v1":
        raise CatalogSpecError("catalog nonce drifted")
    if not _same_json(document.get("field_bits"), list(FIELD_BITS)):
        raise CatalogSpecError("CI field ladder must be exactly [11, 13]")
    if not _same_json(document.get("family_order"), list(FAMILIES)):
        raise CatalogSpecError("CI family order drifted")
    if not _same_json(document.get("limits"), REQUIRED_LIMITS):
        raise CatalogSpecError("CI search ceilings must remain exactly frozen")
    policy = document.get("search_policy")
    if not _same_json(policy, {
        "generic_curves_per_prime": GENERIC_CURVES_PER_PRIME,
        "minimum_subgroup_order_bits_margin": MINIMUM_SUBGROUP_ORDER_BITS_MARGIN,
        "point_derivation": "sha256_x_then_canonical_parity_v1",
        "prime_slot_order": "sha256_rotated_exact_width_odd_v1",
        "subgroup_selection": "largest_prime_factor",
    }):
        raise CatalogSpecError("catalog search policy drifted")
    parameters = document.get("family_parameters")
    if not _same_json(parameters, {
        "j0_glv_like": {
            "certificate_type": "prime_order_hasse_unique_v1",
            "curve_a": 0,
            "curve_b": 7,
        },
        "random_generic_j_prime_subgroup": {
            "certificate_type": "exact_legendre_sum_v1"
        },
        "j0_no_fp_glv_control": {
            "certificate_type": "j0_p_plus_one_v1",
            "curve_a": 0,
            "curve_b": 7,
        },
    }):
        raise CatalogSpecError("catalog family parameters drifted")
    if Path(path).resolve() == CI_SPEC_PATH.resolve():
        try:
            if Path(path).read_bytes() != render_spec(document):
                raise CatalogSpecError("committed catalog spec bytes are not canonical")
        except OSError as error:
            raise CatalogSpecError(f"cannot reread committed catalog spec: {error}") from error
    return document


def render_catalog(catalog: Mapping[str, Any]) -> bytes:
    """Return deterministic, observation-free catalog bytes."""

    return json.dumps(
        dict(catalog), ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False
    ).encode("utf-8") + b"\n"


def _domain(spec: Mapping[str, Any], family: str, bits: int, suffix: str) -> bytes:
    return (
        "keyai/ecdlp-lab/ci-curves/v1/"
        f"{spec['catalog_nonce']}/{family}/{bits}/{suffix}"
    ).encode("ascii")


def _prime_slots(
    spec: Mapping[str, Any], family: str, bits: int, state: SearchState
) -> Iterator[int]:
    lower = 1 << (bits - 1)
    upper = 1 << bits
    first = lower | 1
    slots = ((upper - 1 - first) // 2) + 1
    start = derive_integer(_domain(spec, family, bits, "prime-start"), slots)
    for offset in range(slots):
        state.consume("prime_candidates_examined")
        yield first + 2 * ((start + offset) % slots)
    raise SearchExhausted(family, bits, "max_prime_candidates")


def _bounded_subgroup_point(
    curve: Curve,
    cofactor: int,
    point_domain: bytes,
    state: SearchState,
) -> tuple[int, int]:
    while True:
        ordinal = state.consume("point_attempts")
        x = derive_integer(point_domain, curve.p, ordinal)
        rhs = (pow(x, 3, curve.p) + curve.a * x + curve.b) % curve.p
        y = tonelli_shanks(rhs, curve.p)
        if y is None:
            continue
        parity = hashlib.sha256(
            point_domain + ordinal.to_bytes(8, "big")
        ).digest()[0] & 1
        if (y & 1) != parity:
            y = (-y) % curve.p
        point = curve.scalar_mul(cofactor, (x, y))
        if point is not None:
            return point


def _exact_legendre_full_order(curve: Curve) -> int:
    exponent = (curve.p - 1) // 2
    count = 1
    for x in range(curve.p):
        rhs = (pow(x, 3, curve.p) + curve.a * x + curve.b) % curve.p
        if rhs == 0:
            count += 1
        elif pow(rhs, exponent, curve.p) == 1:
            count += 2
    return count


def _largest_prime_factor(value: int) -> int:
    factors = prime_factors(value)
    if not factors:
        raise AssertionError("positive curve order has no prime factor")
    return max(factors)


def _j_invariant(curve: Curve) -> int:
    numerator = 1728 * 4 * pow(curve.a, 3, curve.p)
    denominator = (4 * pow(curve.a, 3, curve.p) + 27 * pow(curve.b, 2, curve.p)) % curve.p
    return numerator * pow(denominator, -1, curve.p) % curve.p


def _ids(family: str, bits: int, prime: int) -> tuple[str, str]:
    curve_id = f"ecdlp-lab-{family.replace('_', '-')}-b{bits}-p{prime}"
    return curve_id, f"{curve_id}-g0"


def _base_entry(
    *,
    family: str,
    bits: int,
    curve: Curve,
    full_order: int,
    subgroup_order: int,
    cofactor: int,
    generator: tuple[int, int],
    state: SearchState,
) -> dict[str, Any]:
    curve_id, fixture_id = _ids(family, bits, curve.p)
    return {
        "fixture_id": fixture_id,
        "curve_id": curve_id,
        "family": family,
        "field_bits": bits,
        "field_p": curve.p,
        "curve_a": curve.a,
        "curve_b": curve.b,
        "j_invariant": _j_invariant(curve),
        "full_order": full_order,
        "subgroup_order": subgroup_order,
        "subgroup_order_bits": subgroup_order.bit_length(),
        "cofactor": cofactor,
        "generator": list(generator),
        "generation_search": state.receipt(),
    }


def _generate_glv(
    spec: Mapping[str, Any], bits: int, state: SearchState
) -> dict[str, Any]:
    for prime in _prime_slots(spec, "j0_glv_like", bits, state):
        if not is_prime(prime) or prime % 3 != 1:
            continue
        state.consume("curve_candidates_examined")
        curve = Curve(prime, 0, 7)
        generator = _bounded_subgroup_point(
            curve, 1, _domain(spec, state.family, bits, f"point/{prime}"), state
        )
        full_order = certified_prime_full_order(curve, generator)
        if (
            full_order is None
            or full_order == prime
            or full_order.bit_length()
            < bits - MINIMUM_SUBGROUP_ORDER_BITS_MARGIN
        ):
            continue
        try:
            beta, eigenvalue = glv_parameters(curve, full_order, generator)
        except (RuntimeError, ValueError):
            continue
        entry = _base_entry(
            family=state.family,
            bits=bits,
            curve=curve,
            full_order=full_order,
            subgroup_order=full_order,
            cofactor=1,
            generator=generator,
            state=state,
        )
        bound = isqrt(4 * prime)
        entry.update(
            {
                "endomorphism": {
                    "status": "verified_j0_glv",
                    "beta": beta,
                    "lambda": eigenvalue,
                    "reason": None,
                },
                "family_property": {
                    "kind": "j0_glv_like_v1",
                    "equation_shape": "y^2=x^3+7",
                    "j_invariant": 0,
                    "field_p_mod_3": 1,
                },
                "order_certificate": {
                    "type": "prime_order_hasse_unique_v1",
                    "inputs": {
                        "field_p": prime,
                        "generator": list(generator),
                        "subgroup_order": full_order,
                        "full_order": full_order,
                        "cofactor": 1,
                        "hasse_lower": prime + 1 - bound,
                        "hasse_upper": prime + 1 + bound,
                        "twice_subgroup_order": 2 * full_order,
                    },
                },
            }
        )
        return entry
    raise SearchExhausted(state.family, bits, "max_prime_candidates")


def _generate_generic(
    spec: Mapping[str, Any], bits: int, state: SearchState
) -> dict[str, Any]:
    for prime in _prime_slots(spec, state.family, bits, state):
        if not is_prime(prime):
            continue
        for local_index in range(GENERIC_CURVES_PER_PRIME):
            state.consume("curve_candidates_examined")
            curve_a = derive_integer(
                _domain(spec, state.family, bits, f"a/{prime}"), prime, local_index
            )
            curve_b = derive_integer(
                _domain(spec, state.family, bits, f"b/{prime}"), prime, local_index
            )
            discriminant = (
                4 * pow(curve_a, 3, prime) + 27 * pow(curve_b, 2, prime)
            ) % prime
            if discriminant == 0:
                continue
            curve = Curve(prime, curve_a, curve_b)
            invariant = _j_invariant(curve)
            if invariant in {0, 1728 % prime}:
                continue
            full_order = _exact_legendre_full_order(curve)
            subgroup_order = _largest_prime_factor(full_order)
            if (
                subgroup_order.bit_length()
                < bits - MINIMUM_SUBGROUP_ORDER_BITS_MARGIN
            ):
                continue
            cofactor = full_order // subgroup_order
            generator = _bounded_subgroup_point(
                curve,
                cofactor,
                _domain(spec, state.family, bits, f"point/{prime}/{local_index}"),
                state,
            )
            if curve.scalar_mul(subgroup_order, generator) is not None:
                raise AssertionError("producer derived a point outside its prime subgroup")
            entry = _base_entry(
                family=state.family,
                bits=bits,
                curve=curve,
                full_order=full_order,
                subgroup_order=subgroup_order,
                cofactor=cofactor,
                generator=generator,
                state=state,
            )
            entry.update(
                {
                    "endomorphism": {
                        "status": "not_claimed_generic_control",
                        "beta": None,
                        "lambda": None,
                        "reason": "generic_j_control_has_no_claimed_j0_endomorphism",
                    },
                    "family_property": {
                        "kind": "random_generic_j_prime_subgroup_v1",
                        "j_invariant": invariant,
                        "excluded_j_residues": [0, 1728 % prime],
                        "subgroup_selection": "largest_prime_factor",
                    },
                    "order_certificate": {
                        "type": "exact_legendre_sum_v1",
                        "inputs": {
                            "field_p": prime,
                            "curve_a": curve_a,
                            "curve_b": curve_b,
                            "x_start": 0,
                            "x_stop_exclusive": prime,
                            "legendre_exponent": (prime - 1) // 2,
                            "expected_full_order": full_order,
                        },
                    },
                }
            )
            return entry
    raise SearchExhausted(state.family, bits, "max_prime_candidates")


def _generate_no_fp_glv(
    spec: Mapping[str, Any], bits: int, state: SearchState
) -> dict[str, Any]:
    for prime in _prime_slots(spec, state.family, bits, state):
        if not is_prime(prime) or prime % 3 != 2:
            continue
        state.consume("curve_candidates_examined")
        curve = Curve(prime, 0, 7)
        full_order = prime + 1
        subgroup_order = _largest_prime_factor(full_order)
        if (
            subgroup_order.bit_length()
            < bits - MINIMUM_SUBGROUP_ORDER_BITS_MARGIN
        ):
            continue
        cofactor = full_order // subgroup_order
        generator = _bounded_subgroup_point(
            curve,
            cofactor,
            _domain(spec, state.family, bits, f"point/{prime}"),
            state,
        )
        if curve.scalar_mul(subgroup_order, generator) is not None:
            raise AssertionError("producer derived a point outside its prime subgroup")
        entry = _base_entry(
            family=state.family,
            bits=bits,
            curve=curve,
            full_order=full_order,
            subgroup_order=subgroup_order,
            cofactor=cofactor,
            generator=generator,
            state=state,
        )
        entry.update(
            {
                "endomorphism": {
                    "status": "unavailable_no_base_field_cube_root",
                    "beta": None,
                    "lambda": None,
                    "reason": (
                        "gcd(3,field_p-1)=1_no_nontrivial_base_field_cube_root"
                    ),
                },
                "family_property": {
                    "kind": "j0_no_fp_glv_control_v1",
                    "equation_shape": "y^2=x^3+7",
                    "j_invariant": 0,
                    "field_p_mod_3": 2,
                    "cube_map_gcd": gcd(3, prime - 1),
                    "claim_scope": "base_field_only",
                },
                "order_certificate": {
                    "type": "j0_p_plus_one_v1",
                    "inputs": {
                        "field_p": prime,
                        "curve_a": 0,
                        "curve_b": 7,
                        "field_p_mod_3": 2,
                        "expected_full_order": prime + 1,
                    },
                },
            }
        )
        return entry
    raise SearchExhausted(state.family, bits, "max_prime_candidates")


def generate_catalog(spec: Mapping[str, Any]) -> dict[str, Any]:
    """Generate exactly one fixture for every frozen family/bit pair."""

    if not isinstance(spec, Mapping):
        raise CatalogSpecError("catalog spec must be an object")
    # Validate in-memory inputs without depending on their source path.
    if set(spec) != {
        "schema_version",
        "spec_kind",
        "catalog_nonce",
        "field_bits",
        "family_order",
        "limits",
        "search_policy",
        "family_parameters",
    }:
        raise CatalogSpecError("catalog spec top-level keys drifted")
    if type(spec.get("schema_version")) is not int or spec.get(
        "schema_version"
    ) != 1 or spec.get("spec_kind") != (
        "ecdlp_lab_ci_curve_catalog_spec_v1"
    ):
        raise CatalogSpecError("catalog spec identity drifted")
    if spec.get("catalog_nonce") != "ecdlp-lab-ci-v1":
        raise CatalogSpecError("catalog nonce drifted")
    if not _same_json(spec.get("field_bits"), list(FIELD_BITS)):
        raise CatalogSpecError("catalog field ladder drifted")
    if not _same_json(spec.get("family_order"), list(FAMILIES)):
        raise CatalogSpecError("catalog family order drifted")
    if not _same_json(spec.get("limits"), REQUIRED_LIMITS):
        raise CatalogSpecError("catalog limits drifted")
    if not _same_json(spec.get("search_policy"), {
        "generic_curves_per_prime": GENERIC_CURVES_PER_PRIME,
        "minimum_subgroup_order_bits_margin": MINIMUM_SUBGROUP_ORDER_BITS_MARGIN,
        "point_derivation": "sha256_x_then_canonical_parity_v1",
        "prime_slot_order": "sha256_rotated_exact_width_odd_v1",
        "subgroup_selection": "largest_prime_factor",
    }):
        raise CatalogSpecError("catalog search policy drifted")
    if not _same_json(spec.get("family_parameters"), {
        "j0_glv_like": {
            "certificate_type": "prime_order_hasse_unique_v1",
            "curve_a": 0,
            "curve_b": 7,
        },
        "random_generic_j_prime_subgroup": {
            "certificate_type": "exact_legendre_sum_v1"
        },
        "j0_no_fp_glv_control": {
            "certificate_type": "j0_p_plus_one_v1",
            "curve_a": 0,
            "curve_b": 7,
        },
    }):
        raise CatalogSpecError("catalog family parameters drifted")
    verify_p1_arithmetic()
    fixtures: list[dict[str, Any]] = []
    generators = {
        "j0_glv_like": _generate_glv,
        "random_generic_j_prime_subgroup": _generate_generic,
        "j0_no_fp_glv_control": _generate_no_fp_glv,
    }
    for bits in FIELD_BITS:
        for family in FAMILIES:
            state = SearchState(family, bits, REQUIRED_LIMITS)
            fixtures.append(generators[family](spec, bits, state))
    if len(fixtures) != 6:
        raise AssertionError("CI catalog generation did not produce six fixtures")
    return {
        "schema_version": 1,
        "catalog_kind": "ecdlp_lab_ci_curve_catalog_v1",
        "classification": "engineering_only",
        "native_research_outcome": False,
        "spec_sha256": sha256_bytes(render_spec(spec)),
        "curve_count": 6,
        "field_bits": list(FIELD_BITS),
        "families": list(FAMILIES),
        "limits": dict(REQUIRED_LIMITS),
        "fixtures": fixtures,
    }


def committed_catalog_bytes(path: Path | str = CI_CATALOG_PATH) -> bytes:
    """Read the bounded committed catalog bytes without parsing them."""

    candidate = Path(path)
    try:
        if candidate.stat().st_size > 1024 * 1024:
            raise ValueError("committed CI catalog exceeds one MiB")
        return candidate.read_bytes()
    except OSError as error:
        raise ValueError(f"cannot read committed CI catalog: {error}") from error


def check_committed_catalog() -> tuple[bool, str]:
    """Return whether fresh deterministic bytes match the committed catalog."""

    spec = load_spec()
    expected = render_catalog(generate_catalog(spec))
    actual = committed_catalog_bytes()
    if actual != expected:
        return False, "committed CI catalog differs from deterministic generation"
    return True, sha256_bytes(actual)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--print", action="store_true", dest="print_catalog")
    args = parser.parse_args(argv)
    try:
        spec = load_spec()
        rendered = render_catalog(generate_catalog(spec))
        if args.check:
            actual = committed_catalog_bytes()
            if actual != rendered:
                print("committed CI catalog differs from deterministic generation")
                return 1
            print(f"CI curve catalog pass: 6 fixtures, sha256={sha256_bytes(actual)}")
            return 0
        sys.stdout.buffer.write(rendered)
        return 0
    except (CatalogSpecError, SearchExhausted, RuntimeError, ValueError) as error:
        print(f"CI curve catalog error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
