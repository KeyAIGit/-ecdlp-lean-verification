#!/usr/bin/env python3
"""Generate the exact GLV/Semaev coordinate-scaling certificate.

The producer uses SymPy for expansion and for the defining S4 resultant. The
committed validator deliberately does not import this module or SymPy.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
from pathlib import Path

import sympy


HERE = Path(__file__).resolve().parent
CERTIFICATE_PATH = HERE / "certificate.json"
DIGEST_PATH = HERE / "certificate.sha256"
EXPECTED_SYMPY = "1.14.0"

BETA, CURVE_B, X1, X2, X3, X4, Z = sympy.symbols(
    "beta b x1 x2 x3 x4 z"
)


def s3(left, right, third):
    """Exact S3 for y^2 = x^3 + b."""
    return (
        (left - right) ** 2 * third**2
        - 2 * ((left + right) * left * right + 2 * CURVE_B) * third
        + (left * right) ** 2
        - 4 * CURVE_B * (left + right)
    )


def canonical_terms(expression, variables):
    """Canonical terms in Z[beta,b,x...]/(beta^3-1).

    Each term is ``[coefficient, [beta_power, b_power, x_powers...]]``.
    Reduction modulo beta^3-1 is exact exponent reduction modulo three.
    """
    polynomial = sympy.Poly(
        sympy.expand(expression), BETA, CURVE_B, *variables, domain=sympy.ZZ
    )
    accumulated: dict[tuple[int, ...], int] = {}
    for powers, coefficient in polynomial.terms():
        key = (int(powers[0]) % 3, *(int(power) for power in powers[1:]))
        accumulated[key] = accumulated.get(key, 0) + int(coefficient)
    return [
        [coefficient, list(powers)]
        for powers, coefficient in sorted(accumulated.items())
        if coefficient
    ]


def canonical_bytes(value) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def digest(value) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def beta_shift(terms, amount):
    shifted: dict[tuple[int, ...], int] = {}
    for coefficient, raw_powers in terms:
        powers = tuple(raw_powers)
        key = ((powers[0] + amount) % 3, *powers[1:])
        shifted[key] = shifted.get(key, 0) + coefficient
    return [
        [coefficient, list(powers)]
        for powers, coefficient in sorted(shifted.items())
        if coefficient
    ]


def source_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify_scalings(name, expression, variables):
    base_terms = canonical_terms(expression, variables)
    entries = []
    for exponents in itertools.product(range(3), repeat=len(variables)):
        substitutions = {
            variable: BETA ** exponent * variable
            for variable, exponent in zip(variables, exponents)
        }
        transformed_terms = canonical_terms(
            expression.xreplace(substitutions), variables
        )
        characters = [
            character
            for character in range(3)
            if transformed_terms == beta_shift(base_terms, character)
        ]
        if len(characters) > 1:
            raise RuntimeError(f"{name} has ambiguous beta character at {exponents}")
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
                "transformed_sha256": digest(transformed_terms),
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
        "variables": [str(variable) for variable in variables],
        "base_terms": base_terms,
        "base_sha256": digest(base_terms),
        "base_term_count": len(base_terms),
        "scalings": entries,
        "summary": summary,
    }


def build_certificate() -> dict[str, object]:
    if sympy.__version__ != EXPECTED_SYMPY:
        raise RuntimeError(
            f"expected SymPy {EXPECTED_SYMPY}, found {sympy.__version__}"
        )

    exact_s3 = sympy.expand(s3(X1, X2, X3))
    exact_s4 = sympy.expand(
        sympy.resultant(s3(X1, X2, Z), s3(X3, X4, Z), Z)
    )

    tracked_sources = ("generate.py", "validate.py", "requirements.txt")
    return {
        "schema_version": 1,
        "certificate_id": "GLV-SEMAEV-ITER-001-SYMMETRY",
        "claim_boundary": (
            "Exact symbolic classification of coordinatewise C3 scalings for "
            "S3 and resultant-defined S4. It is not an ECDLP attack, a solving "
            "cost result, or a secp256k1 claim."
        ),
        "algebra": {
            "coefficient_ring": "Z[b,beta]/(beta^3-1)",
            "curve_family": "y^2=x^3+b",
            "curve_parameter": "b remains symbolic",
            "s3_formula": (
                "(x1-x2)^2*x3^2"
                "-2*((x1+x2)*x1*x2+2*b)*x3"
                "+(x1*x2)^2-4*b*(x1+x2)"
            ),
            "s4_definition": (
                "Resultant_z(S3(x1,x2,z),S3(x3,x4,z))"
            ),
            "reduction_rule": "beta^k -> beta^(k mod 3)",
            "unit_scalar_test": (
                "transformed polynomial equals beta^k times the base "
                "polynomial for exactly one k in {0,1,2}"
            ),
        },
        "fixed_target_convention": {
            "target_variable": "the final x-coordinate in each polynomial",
            "relation_interpretation": (
                "S3(x1,x2,xT)=0 or S4(x1,x2,x3,xT)=0; xT also "
                "represents -T because elliptic-curve negation preserves x"
            ),
            "generic_scope": (
                "The target is symbolic and non-special. A scaling is a "
                "fixed-target symmetry only when its target exponent is zero."
            ),
            "transport_scope": (
                "A full diagonal scaling with nonzero target exponent "
                "transports the target fiber to its GLV image; it does not "
                "preserve one generic fixed target."
            ),
        },
        "producer": {
            "python_major_minor": ".".join(platform.python_version().split(".")[:2]),
            "sympy_version": sympy.__version__,
            "source_sha256": {
                name: source_hash(HERE / name) for name in tracked_sources
            },
        },
        "commands": {
            "install": (
                "python3 -m pip install -r "
                "experiments/glv_semaev_symmetry/requirements.txt"
            ),
            "generate_check": (
                "python3 experiments/glv_semaev_symmetry/generate.py --check"
            ),
            "independent_replay": (
                "python3 experiments/glv_semaev_symmetry/validate.py"
            ),
        },
        "polynomials": {
            "S3": classify_scalings("S3", exact_s3, (X1, X2, X3)),
            "S4": classify_scalings("S4", exact_s4, (X1, X2, X3, X4)),
        },
        "conclusions": {
            "scope": (
                "Only tuples classified by exact unit-scalar equality preserve "
                "the corresponding symbolic zero set."
            ),
            "fixed_target": (
                "Nonidentity diagonal tuples move a generic target and are "
                "therefore target transports, not fixed-target symmetries."
            ),
            "complexity": (
                "The certificate makes no claim about Groebner complexity, "
                "relation probability, or asymptotic ECDLP cost."
            ),
        },
    }


def render(certificate: dict[str, object]) -> bytes:
    return (
        json.dumps(certificate, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("ascii")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the committed certificate or digest is stale.",
    )
    args = parser.parse_args()

    certificate = build_certificate()
    payload = render(certificate)
    sha256 = hashlib.sha256(payload).hexdigest()
    digest_record = f"{sha256}  certificate.json\n".encode("ascii")
    if args.check:
        problems = []
        if not CERTIFICATE_PATH.is_file() or CERTIFICATE_PATH.read_bytes() != payload:
            problems.append("certificate.json is stale")
        if not DIGEST_PATH.is_file() or DIGEST_PATH.read_bytes() != digest_record:
            problems.append("certificate.sha256 is stale")
        if problems:
            for problem in problems:
                print(f"ERROR: {problem}")
            return 1
        print(f"GENERATOR CHECK: PASS ({sha256})")
        return 0

    CERTIFICATE_PATH.write_bytes(payload)
    DIGEST_PATH.write_bytes(digest_record)
    s3_summary = certificate["polynomials"]["S3"]["summary"]
    s4_summary = certificate["polynomials"]["S4"]["summary"]
    print(f"wrote {CERTIFICATE_PATH.relative_to(HERE.parent.parent)}")
    print(f"sha256={sha256}")
    print(f"S3 summary: {s3_summary}")
    print(f"S4 summary: {s4_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
