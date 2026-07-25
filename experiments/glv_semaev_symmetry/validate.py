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


def classify(name: str, polynomial: Polynomial, variable_names: list[str]):
    zero_exponents = (0,) * len(variable_names)
    base_terms = encode_scaled(polynomial, zero_exponents)
    entries = []
    for exponents in itertools.product(range(3), repeat=len(variable_names)):
        transformed = encode_scaled(polynomial, exponents)
        characters = [
            character
            for character in range(3)
            if transformed == beta_shift(base_terms, character)
        ]
        if len(characters) > 1:
            fail(f"{name} has ambiguous character at {exponents}")
        character = characters[0] if characters else None
        target_exponent = exponents[-1]
        diagonal = len(set(exponents)) == 1
        if character is not None and target_exponent == 0:
            fixed_target_class = "preserves_generic_fixed_target_fiber"
        elif character is not None:
            fixed_target_class = "transports_target_fiber"
        elif target_exponent == 0:
            fixed_target_class = "does_not_preserve_fixed_target_fiber"
        else:
            fixed_target_class = "not_a_zero_set_symmetry"
        entries.append(
            {
                "exponents": list(exponents),
                "transformed_sha256": digest(transformed),
                "unit_scalar_character": character,
                "exact_polynomial_equality": character == 0,
                "diagonal_action": diagonal,
                "target_exponent": target_exponent,
                "fixed_target_class": fixed_target_class,
            }
        )
    summary = {
        "total_scalings": len(entries),
        "unit_scalar_symmetries": sum(
            entry["unit_scalar_character"] is not None for entry in entries
        ),
        "exact_polynomial_symmetries": sum(
            entry["exact_polynomial_equality"] for entry in entries
        ),
        "generic_fixed_target_symmetries": sum(
            entry["fixed_target_class"]
            == "preserves_generic_fixed_target_fiber"
            for entry in entries
        ),
        "diagonal_target_transports": sum(
            entry["diagonal_action"]
            and entry["target_exponent"] != 0
            and entry["unit_scalar_character"] is not None
            for entry in entries
        ),
        "rejected_scalings": sum(
            entry["unit_scalar_character"] is None for entry in entries
        ),
        "character_counts": {
            str(character): sum(
                entry["unit_scalar_character"] == character for entry in entries
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
        "scalings": entries,
        "summary": summary,
    }


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_metadata(certificate: dict[str, object]) -> None:
    if certificate.get("schema_version") != 1:
        fail("unexpected schema version")
    if certificate.get("certificate_id") != "GLV-SEMAEV-ITER-001-SYMMETRY":
        fail("unexpected certificate id")
    algebra = certificate.get("algebra", {})
    if algebra.get("coefficient_ring") != "Z[b,beta]/(beta^3-1)":
        fail("unexpected coefficient ring")
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
