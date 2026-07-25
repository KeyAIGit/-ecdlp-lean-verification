#!/usr/bin/env python3
"""Independent stdlib replay of the GLV/Semaev symmetry certificate.

This validator imports neither SymPy nor the producer. It constructs S3 with a
sparse integer polynomial implementation and constructs S4 as the determinant
of the 4x4 Sylvester matrix for two quadratics in the eliminated variable.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CERTIFICATE_PATH = HERE / "certificate.json"
DIGEST_PATH = HERE / "certificate.sha256"
SECP256K1_P = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16
)
SECP256K1_BETA = int(
    "7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE",
    16,
)
SECP256K1_B = 7

Polynomial = dict[tuple[int, ...], int]


def fail(message: str) -> None:
    raise ValueError(message)


def constant(value: int, nvars: int) -> Polynomial:
    return {} if value == 0 else {(0,) * nvars: value}


def variable(index: int, nvars: int) -> Polynomial:
    powers = [0] * nvars
    powers[index] = 1
    return {tuple(powers): 1}


def add(left: Polynomial, right: Polynomial) -> Polynomial:
    result = dict(left)
    for powers, coefficient in right.items():
        result[powers] = result.get(powers, 0) + coefficient
        if result[powers] == 0:
            del result[powers]
    return result


def negate(polynomial: Polynomial) -> Polynomial:
    return {powers: -coefficient for powers, coefficient in polynomial.items()}


def subtract(left: Polynomial, right: Polynomial) -> Polynomial:
    return add(left, negate(right))


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    if not left or not right:
        return {}
    result: Polynomial = {}
    for left_powers, left_coefficient in left.items():
        for right_powers, right_coefficient in right.items():
            powers = tuple(
                a + b for a, b in zip(left_powers, right_powers)
            )
            result[powers] = (
                result.get(powers, 0)
                + left_coefficient * right_coefficient
            )
    return {powers: value for powers, value in result.items() if value}


def power(polynomial: Polynomial, exponent: int) -> Polynomial:
    if exponent < 0:
        fail("negative polynomial exponent")
    nvars = len(next(iter(polynomial), ()))
    result = constant(1, nvars)
    factor = polynomial
    remaining = exponent
    while remaining:
        if remaining & 1:
            result = multiply(result, factor)
        factor = multiply(factor, factor)
        remaining >>= 1
    return result


def scale(value: int, polynomial: Polynomial) -> Polynomial:
    return {
        powers: value * coefficient
        for powers, coefficient in polynomial.items()
        if value * coefficient
    }


def s3_polynomial(nvars: int, left_index: int, right_index: int, third_index: int):
    curve_b = variable(0, nvars)
    left = variable(left_index, nvars)
    right = variable(right_index, nvars)
    third = variable(third_index, nvars)
    first_term = multiply(
        power(subtract(left, right), 2),
        power(third, 2),
    )
    bracket = add(
        multiply(multiply(add(left, right), left), right),
        scale(2, curve_b),
    )
    second_term = scale(-2, multiply(bracket, third))
    third_term = subtract(
        power(multiply(left, right), 2),
        scale(4, multiply(curve_b, add(left, right))),
    )
    return add(add(first_term, second_term), third_term)


def strip_variable(
    polynomial: Polynomial, index: int, required_power: int
) -> Polynomial:
    result: Polynomial = {}
    for powers, coefficient in polynomial.items():
        if powers[index] != required_power:
            continue
        reduced = powers[:index] + powers[index + 1 :]
        result[reduced] = result.get(reduced, 0) + coefficient
    return {powers: value for powers, value in result.items() if value}


def permutation_sign(permutation) -> int:
    inversions = sum(
        permutation[i] > permutation[j]
        for i in range(len(permutation))
        for j in range(i + 1, len(permutation))
    )
    return -1 if inversions % 2 else 1


def determinant(matrix: list[list[Polynomial]]) -> Polynomial:
    n = len(matrix)
    nvars = len(next(iter(matrix[0][0]), (0,) * 5))
    total: Polynomial = {}
    for permutation in itertools.permutations(range(n)):
        term = constant(permutation_sign(permutation), nvars)
        for row, column in enumerate(permutation):
            term = multiply(term, matrix[row][column])
        total = add(total, term)
    return total


def build_s4() -> Polynomial:
    # Variables are b,x1,x2,x3,x4,z; z is stripped from the coefficients.
    nvars = 6
    first = s3_polynomial(nvars, 1, 2, 5)
    second = s3_polynomial(nvars, 3, 4, 5)
    a2, a1, a0 = (
        strip_variable(first, 5, degree) for degree in (2, 1, 0)
    )
    b2, b1, b0 = (
        strip_variable(second, 5, degree) for degree in (2, 1, 0)
    )
    zero = constant(0, 5)
    sylvester = [
        [a2, a1, a0, zero],
        [zero, a2, a1, a0],
        [b2, b1, b0, zero],
        [zero, b2, b1, b0],
    ]
    return determinant(sylvester)


def canonical_bytes(value) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def digest(value) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def encode_scaled(polynomial: Polynomial, exponents: tuple[int, ...]):
    accumulated: dict[tuple[int, ...], int] = {}
    for powers, coefficient in polynomial.items():
        # powers[0] is b; the remaining powers are x-coordinate powers.
        beta_power = sum(
            exponent * power_value
            for exponent, power_value in zip(exponents, powers[1:])
        ) % 3
        key = (beta_power, *powers)
        accumulated[key] = accumulated.get(key, 0) + coefficient
    return [
        [coefficient, list(powers)]
        for powers, coefficient in sorted(accumulated.items())
        if coefficient
    ]


def beta_shift(terms, amount):
    accumulated: dict[tuple[int, ...], int] = {}
    for coefficient, raw_powers in terms:
        powers = tuple(raw_powers)
        key = ((powers[0] + amount) % 3, *powers[1:])
        accumulated[key] = accumulated.get(key, 0) + coefficient
    return [
        [coefficient, list(powers)]
        for powers, coefficient in sorted(accumulated.items())
        if coefficient
    ]


def primitive_component(terms):
    accumulated: dict[tuple[int, ...], int] = {}
    for coefficient, raw_powers in terms:
        powers = tuple(raw_powers)
        if powers[0] < 2:
            accumulated[powers] = accumulated.get(powers, 0) + coefficient
            continue
        for beta_power in (0, 1):
            key = (beta_power, *powers[1:])
            accumulated[key] = accumulated.get(key, 0) - coefficient
    return [
        [coefficient, list(powers)]
        for powers, coefficient in sorted(accumulated.items())
        if coefficient
    ]


def specialize_terms(terms, field_prime, curve_b, beta):
    accumulated: dict[tuple[int, ...], int] = {}
    for coefficient, raw_powers in terms:
        beta_power, b_power, *x_powers = raw_powers
        value = (
            coefficient
            * pow(beta, beta_power, field_prime)
            * pow(curve_b, b_power, field_prime)
        ) % field_prime
        key = tuple(x_powers)
        accumulated[key] = (accumulated.get(key, 0) + value) % field_prime
    return {
        powers: coefficient
        for powers, coefficient in accumulated.items()
        if coefficient
    }


def scalar_multiple(left, right, field_prime):
    support = set(left) | set(right)
    anchor = next((powers for powers in sorted(support) if right.get(powers, 0)), None)
    if anchor is None:
        return None
    scalar = (
        left.get(anchor, 0)
        * pow(right[anchor], -1, field_prime)
    ) % field_prime
    if scalar == 0:
        return None
    if all(
        left.get(powers, 0) == scalar * right.get(powers, 0) % field_prime
        for powers in support
    ):
        return scalar
    return None


def classify(name: str, polynomial: Polynomial, variable_names: list[str]):
    zero_exponents = (0,) * len(variable_names)
    base_terms = encode_scaled(polynomial, zero_exponents)
    primitive_base_terms = primitive_component(base_terms)
    secp256k1_base = specialize_terms(
        base_terms, SECP256K1_P, SECP256K1_B, SECP256K1_BETA
    )
    entries = []
    for exponents in itertools.product(range(3), repeat=len(variable_names)):
        transformed = encode_scaled(polynomial, exponents)
        universal_characters = [
            character
            for character in range(3)
            if transformed == beta_shift(base_terms, character)
        ]
        primitive_terms = primitive_component(transformed)
        primitive_characters = [
            character
            for character in range(3)
            if primitive_terms
            == primitive_component(beta_shift(base_terms, character))
        ]
        if len(universal_characters) > 1 or len(primitive_characters) > 1:
            fail(f"{name} has ambiguous character at {exponents}")
        universal_character = (
            universal_characters[0] if universal_characters else None
        )
        primitive_character = (
            primitive_characters[0] if primitive_characters else None
        )
        secp256k1_transformed = specialize_terms(
            transformed, SECP256K1_P, SECP256K1_B, SECP256K1_BETA
        )
        secp256k1_scalar = scalar_multiple(
            secp256k1_transformed, secp256k1_base, SECP256K1_P
        )
        secp256k1_characters = [
            character
            for character in range(3)
            if secp256k1_scalar
            == pow(SECP256K1_BETA, character, SECP256K1_P)
        ]
        if secp256k1_scalar is not None and len(secp256k1_characters) != 1:
            fail(f"{name} has an unexpected secp256k1 scalar at {exponents}")
        secp256k1_character = (
            secp256k1_characters[0] if secp256k1_characters else None
        )
        target_exponent = exponents[-1]
        diagonal = len(set(exponents)) == 1
        if primitive_character is not None and target_exponent == 0:
            fixed_target_class = "certified_scalar_covariance_at_fixed_target"
        elif primitive_character is not None:
            fixed_target_class = "certified_target_fiber_transport"
        elif target_exponent == 0:
            fixed_target_class = "no_certified_scalar_covariance_at_fixed_target"
        else:
            fixed_target_class = "no_certified_scalar_covariance"
        entries.append(
            {
                "exponents": list(exponents),
                "transformed_sha256": digest(transformed),
                "universal_cube_root_character": universal_character,
                "primitive_unit_scalar_character": primitive_character,
                "secp256k1_unit_scalar_character": secp256k1_character,
                "exact_polynomial_equality": primitive_character == 0,
                "diagonal_action": diagonal,
                "target_exponent": target_exponent,
                "fixed_target_class": fixed_target_class,
            }
        )
    summary = {
        "total_scalings": len(entries),
        "universal_cube_root_semi_invariants": sum(
            entry["universal_cube_root_character"] is not None
            for entry in entries
        ),
        "primitive_root_semi_invariants": sum(
            entry["primitive_unit_scalar_character"] is not None
            for entry in entries
        ),
        "secp256k1_semi_invariants": sum(
            entry["secp256k1_unit_scalar_character"] is not None
            for entry in entries
        ),
        "exact_polynomial_symmetries": sum(
            entry["exact_polynomial_equality"] for entry in entries
        ),
        "certified_generic_fixed_target_covariances": sum(
            entry["fixed_target_class"]
            == "certified_scalar_covariance_at_fixed_target"
            for entry in entries
        ),
        "diagonal_target_transports": sum(
            entry["diagonal_action"]
            and entry["target_exponent"] != 0
            and entry["primitive_unit_scalar_character"] is not None
            for entry in entries
        ),
        "scalar_covariance_rejections": sum(
            entry["primitive_unit_scalar_character"] is None
            for entry in entries
        ),
        "primitive_character_counts": {
            str(character): sum(
                entry["primitive_unit_scalar_character"] == character
                for entry in entries
            )
            for character in range(3)
        },
    }
    return {
        "name": name,
        "variables": variable_names,
        "base_terms": base_terms,
        "base_sha256": digest(base_terms),
        "base_term_count": len(base_terms),
        "primitive_base_sha256": digest(primitive_base_terms),
        "scalings": entries,
        "summary": summary,
    }


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_metadata(certificate: dict[str, object]) -> None:
    if certificate.get("schema_version") != 2:
        fail("unexpected schema version")
    if certificate.get("certificate_id") != "GLV-SEMAEV-ITER-001-SYMMETRY":
        fail("unexpected certificate id")
    algebra = certificate.get("algebra", {})
    if algebra.get("universal_coefficient_ring") != "Z[b,beta]/(beta^3-1)":
        fail("unexpected universal coefficient ring")
    if algebra.get("primitive_component") != "Z[b,beta]/(beta^2+beta+1)":
        fail("unexpected primitive component")
    if algebra.get("curve_parameter") != "b remains symbolic":
        fail("curve parameter is not symbolic")
    producer = certificate.get("producer", {})
    if producer.get("sympy_version") != "1.14.0":
        fail("producer did not pin SymPy 1.14.0")
    expected_sources = {
        name: file_sha256(HERE / name)
        for name in ("generate.py", "validate.py", "requirements.txt")
    }
    if producer.get("source_sha256") != expected_sources:
        fail("source hashes do not match the committed replay sources")


def forcing_component_hash(polynomial: Polynomial, b_power: int) -> str:
    filtered = {
        powers: coefficient
        for powers, coefficient in polynomial.items()
        if powers[0] == b_power
    }
    return digest(encode_scaled(filtered, (0,) * (len(next(iter(filtered))) - 1)))


def evaluate(polynomial: Polynomial, curve_b: int, coordinates: list[int], prime: int) -> int:
    total = 0
    for powers, coefficient in polynomial.items():
        value = coefficient * pow(curve_b, powers[0], prime)
        for coordinate, exponent in zip(coordinates, powers[1:]):
            value *= pow(coordinate, exponent, prime)
        total = (total + value) % prime
    return total


def main() -> int:
    payload = CERTIFICATE_PATH.read_bytes()
    certificate_sha256 = hashlib.sha256(payload).hexdigest()
    expected_digest_record = f"{certificate_sha256}  certificate.json\n"
    if DIGEST_PATH.read_text(encoding="ascii") != expected_digest_record:
        fail("certificate.sha256 does not match certificate.json")

    certificate = json.loads(payload)
    validate_metadata(certificate)

    s3 = s3_polynomial(4, 1, 2, 3)
    s4 = build_s4()
    witnesses = certificate.get("classification_witnesses", {})
    if witnesses.get("S3", {}).get("forcing_component_sha256") != (
        forcing_component_hash(s3, 1)
    ):
        fail("S3 coefficient-classification witness differs from replay")
    if witnesses.get("S4", {}).get("forcing_component_sha256") != (
        forcing_component_hash(s4, 3)
    ):
        fail("S4 coefficient-classification witness differs from replay")
    counterexample = certificate.get("fixed_target_counterexample", {})
    replayed_counterexample = {
        "base_relation": evaluate(s4, 2, [1, 2, 3, 5], 13),
        "scaled_inputs_fixed_target": evaluate(s4, 2, [3, 6, 9, 5], 13),
        "scaled_inputs_scaled_target": evaluate(s4, 2, [3, 6, 9, 2], 13),
    }
    if counterexample.get("values") != replayed_counterexample:
        fail("fixed-target counterexample differs from replay")
    expected = {
        "S3": classify("S3", s3, ["x1", "x2", "x3"]),
        "S4": classify("S4", s4, ["x1", "x2", "x3", "x4"]),
    }
    if certificate.get("polynomials") != expected:
        fail("symbolic polynomial or scaling table differs from stdlib replay")

    for name, expected_total in (("S3", 27), ("S4", 81)):
        record = expected[name]
        if record["summary"]["total_scalings"] != expected_total:
            fail(f"{name} did not enumerate every coordinatewise scaling")
        vectors = {
            tuple(entry["exponents"]) for entry in record["scalings"]
        }
        if len(vectors) != expected_total:
            fail(f"{name} scaling vectors are duplicated or missing")

    print(
        "VALIDATION: PASS "
        f"(S3 terms={len(s3)}, scalings=27; "
        f"S4 terms={len(s4)}, scalings=81; "
        f"certificate_sha256={certificate_sha256})"
    )
    print(f"S3 summary: {expected['S3']['summary']}")
    print(f"S4 summary: {expected['S4']['summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
