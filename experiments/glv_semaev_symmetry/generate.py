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
SECP256K1_P = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16
)
SECP256K1_BETA = int(
    "7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE",
    16,
)
SECP256K1_B = 7

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


def primitive_component(terms):
    """Reduce beta powers modulo beta^2 + beta + 1.

    The beta^3-1 quotient retains both the trivial and primitive components.
    This second normal form excludes beta=1 and prevents a false rejection of
    an identity that holds only for a primitive cube root.
    """
    accumulated: dict[tuple[int, ...], int] = {}
    for coefficient, raw_powers in terms:
        powers = tuple(raw_powers)
        if powers[0] < 2:
            key = powers
            accumulated[key] = accumulated.get(key, 0) + coefficient
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
    """Evaluate beta and b, retaining a sparse polynomial in x variables."""
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
    """Return the nonzero scalar c with left = c*right, if one exists."""
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


def source_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify_scalings(name, expression, variables):
    base_terms = canonical_terms(expression, variables)
    primitive_base_terms = primitive_component(base_terms)
    secp256k1_base = specialize_terms(
        base_terms, SECP256K1_P, SECP256K1_B, SECP256K1_BETA
    )
    entries = []
    for exponents in itertools.product(range(3), repeat=len(variables)):
        substitutions = {
            variable: BETA ** exponent * variable
            for variable, exponent in zip(variables, exponents)
        }
        transformed_terms = canonical_terms(
            expression.xreplace(substitutions), variables
        )
        universal_characters = [
            character
            for character in range(3)
            if transformed_terms == beta_shift(base_terms, character)
        ]
        primitive_terms = primitive_component(transformed_terms)
        primitive_characters = [
            character
            for character in range(3)
            if primitive_terms
            == primitive_component(beta_shift(base_terms, character))
        ]
        if len(universal_characters) > 1 or len(primitive_characters) > 1:
            raise RuntimeError(f"{name} has ambiguous beta character at {exponents}")
        universal_character = (
            universal_characters[0] if universal_characters else None
        )
        primitive_character = (
            primitive_characters[0] if primitive_characters else None
        )
        secp256k1_transformed = specialize_terms(
            transformed_terms, SECP256K1_P, SECP256K1_B, SECP256K1_BETA
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
            raise RuntimeError(
                f"{name} has an unexpected secp256k1 scalar at {exponents}"
            )
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
                "transformed_sha256": digest(transformed_terms),
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
        "certified_symbolic_target_covariances": sum(
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
        "variables": [str(variable) for variable in variables],
        "base_terms": base_terms,
        "base_sha256": digest(base_terms),
        "base_term_count": len(base_terms),
        "primitive_base_sha256": digest(primitive_base_terms),
        "scalings": entries,
        "summary": summary,
    }


def characteristic_uniform_witnesses(expression, variables):
    """Certify every rejected action/character pair with a unit coefficient.

    A covariance by an arbitrary nonzero scalar is forced, by a coefficient-one
    anchor, to use one of the three beta characters.  For each rejected
    ``(exponents, character)`` pair we therefore record an x-monomial outside
    that character class whose coefficient is exactly ``+1`` or ``-1`` in
    ``Z[b]``.  Such a coefficient survives every field specialization.
    """
    polynomial = sympy.Poly(sympy.expand(expression), *variables)
    support = {
        tuple(int(power) for power in powers): sympy.expand(coefficient)
        for powers, coefficient in polynomial.terms()
        if coefficient != 0
    }
    valid = []
    rejected = []
    for exponents in itertools.product(range(3), repeat=len(variables)):
        for character in range(3):
            must_vanish = [
                (powers, coefficient)
                for powers, coefficient in support.items()
                if sum(
                    exponent * power
                    for exponent, power in zip(exponents, powers)
                )
                % 3
                != character
            ]
            if not must_vanish:
                valid.append(
                    {
                        "exponents": list(exponents),
                        "multiplier_beta_exponent": character,
                    }
                )
                continue
            units = [
                (powers, int(coefficient))
                for powers, coefficient in must_vanish
                if coefficient in (sympy.Integer(-1), sympy.Integer(1))
            ]
            witness = min(units, key=lambda item: item[0]) if units else None
            rejected.append(
                {
                    "exponents": list(exponents),
                    "multiplier_beta_exponent": character,
                    "witness": (
                        {
                            "x_exponents": list(witness[0]),
                            "integer_coefficient": witness[1],
                        }
                        if witness
                        else None
                    ),
                }
            )
    missing = [row for row in rejected if row["witness"] is None]
    if missing:
        raise RuntimeError(
            f"{len(missing)} rejected action/character pairs lack a unit witness"
        )
    expected_valid = [
        {
            "exponents": [t] * len(variables),
            "multiplier_beta_exponent": t if len(variables) == 3 else 0,
        }
        for t in range(3)
    ]
    indexed = {
        (tuple(row["exponents"]), row["multiplier_beta_exponent"])
        for row in valid + rejected
    }
    expected_rows = 3 ** len(variables) * 3
    if valid != expected_valid:
        raise RuntimeError(
            f"unexpected valid covariance set for {len(variables)} variables"
        )
    if len(indexed) != expected_rows or len(valid) + len(rejected) != expected_rows:
        raise RuntimeError(
            f"action/character table is not a complete {expected_rows}-row partition"
        )
    return {
        "valid_covariances": valid,
        "rejection_witnesses": rejected,
        "summary": {
            "valid_pairs": len(valid),
            "rejected_pairs": len(rejected),
            "complete_partition_rows": len(indexed),
            "rows_without_unit_witness": len(missing),
            "witness_integer_coefficients": sorted(
                {row["witness"]["integer_coefficient"] for row in rejected}
            ),
        },
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
    s3_b_linear = sympy.expand(CURVE_B * exact_s3.coeff(CURVE_B, 1))
    expected_s3_b_linear = -4 * CURVE_B * (X1 + X2 + X3)
    if sympy.expand(s3_b_linear - expected_s3_b_linear) != 0:
        raise RuntimeError("unexpected S3 b-linear coefficient witness")
    s4_b_cubic = sympy.expand(CURVE_B**3 * exact_s4.coeff(CURVE_B, 3))
    expected_s4_b_cubic = sympy.expand(
        64
        * CURVE_B**3
        * ((X1 + X2) - (X3 + X4))
        * ((X3 - X4) ** 2 - (X1 - X2) ** 2)
    )
    if sympy.expand(s4_b_cubic - expected_s4_b_cubic) != 0:
        raise RuntimeError("unexpected S4 b-cubic coefficient witness")
    fixed_target_values = {
        "base_relation": int(
            exact_s4.subs(
                {CURVE_B: 2, X1: 1, X2: 2, X3: 3, X4: 5}
            )
        )
        % 13,
        "scaled_inputs_fixed_target": int(
            exact_s4.subs(
                {CURVE_B: 2, X1: 3, X2: 6, X3: 9, X4: 5}
            )
        )
        % 13,
        "scaled_inputs_scaled_target": int(
            exact_s4.subs(
                {CURVE_B: 2, X1: 3, X2: 6, X3: 9, X4: 2}
            )
        )
        % 13,
    }
    if fixed_target_values != {
        "base_relation": 0,
        "scaled_inputs_fixed_target": 7,
        "scaled_inputs_scaled_target": 0,
    }:
        raise RuntimeError("unexpected fixed-target transport witness")

    tracked_sources = ("generate.py", "validate.py", "requirements.txt")
    return {
        "schema_version": 3,
        "certificate_id": "GLV-SEMAEV-ITER-001-SYMMETRY",
        "claim_boundary": (
            "Exact symbolic classification of coordinatewise C3 scalings for "
            "S3 and resultant-defined S4. It is not an ECDLP attack, a solving "
            "cost result, or a secp256k1 claim."
        ),
        "algebra": {
            "universal_coefficient_ring": "Z[b,beta]/(beta^3-1)",
            "primitive_component": "Z[b,beta]/(beta^2+beta+1)",
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
                "polynomial for exactly one k in {0,1,2}; a coefficient-one "
                "anchor monomial makes these three candidates exhaustive"
            ),
            "polynomial_classification_assumptions": [
                "the coefficient domain is a field",
                "beta is a primitive cube root of unity",
            ],
            "elliptic_interpretation_assumptions": [
                "b is nonzero",
                "the field characteristic is neither 2 nor 3",
            ],
            "identity_assumptions": (
                "The positive diagonal identities need only beta^3=1 in a "
                "commutative ring. The exact polynomial stabilizer classification "
                "uses a primitive cube root in a field. Interpreting y^2=x^3+b as "
                "an elliptic curve additionally requires b nonzero and "
                "characteristic different from 2 and 3."
            ),
        },
        "secp256k1_specialization": {
            "field_prime_hex": hex(SECP256K1_P),
            "curve_b": SECP256K1_B,
            "beta_hex": hex(SECP256K1_BETA),
            "scope": (
                "Every coordinatewise scaling is also checked for scalar "
                "proportionality after exact specialization to F_p."
            ),
        },
        "classification_witnesses": {
            "scalar_candidate_exhaustiveness": (
                "Each base polynomial has a coefficient-one anchor monomial. "
                "After coordinate scaling its coefficient ratio is beta^k, so "
                "an arbitrary nonzero proportionality scalar must be one of "
                "1, beta, beta^2."
            ),
            "S3": {
                "forcing_component": "-4*b*(x1+x2+x3)",
                "forcing_component_sha256": digest(
                    canonical_terms(s3_b_linear, (X1, X2, X3))
                ),
                "implication": (
                    "When 4*b is nonzero, the three linear coefficients force "
                    "e1=e2=e3=the scalar character."
                ),
            },
            "S4": {
                "forcing_component": (
                    "64*b^3*((x1+x2)-(x3+x4))*"
                    "((x3-x4)^2-(x1-x2)^2)"
                ),
                "forcing_component_sha256": digest(
                    canonical_terms(s4_b_cubic, (X1, X2, X3, X4))
                ),
                "implication": (
                    "When 2*b is nonzero, b^3*x_i^3 fixes character zero and "
                    "b^3*x_i^2*x_j forces all four exponents equal."
                ),
            },
            "characteristic_uniform": {
                "criterion": (
                    "Every rejected (coordinate action, scalar character) pair has "
                    "a must-vanish x-monomial with coefficient +1 or -1 in Z[b]. "
                    "The obstruction therefore survives every field characteristic; "
                    "in characteristic 3 the primitive-root field hypothesis is empty."
                ),
                "S3": characteristic_uniform_witnesses(
                    exact_s3, (X1, X2, X3)
                ),
                "S4": characteristic_uniform_witnesses(
                    exact_s4, (X1, X2, X3, X4)
                ),
            },
        },
        "fixed_target_counterexample": {
            "field": "F_13",
            "curve_b": 2,
            "beta": 3,
            "beta_cube_mod_13": pow(3, 3, 13),
            "base_coordinates": [1, 2, 3, 5],
            "scaled_inputs_fixed_target_coordinates": [3, 6, 9, 5],
            "scaled_inputs_scaled_target_coordinates": [3, 6, 9, 2],
            "values": fixed_target_values,
            "interpretation": (
                "Scaling the three relation variables does not preserve this "
                "fixed nonzero target; scaling the target as well transports "
                "the zero exactly."
            ),
        },
        "fixed_target_convention": {
            "target_variable": "the final x-coordinate in each polynomial",
            "relation_interpretation": (
                "S3(x1,x2,xT)=0 or S4(x1,x2,x3,xT)=0; xT also "
                "represents -T because elliptic-curve negation preserves x"
            ),
            "base_symbolic_scope": (
                "This base table treats a symbolic target. Its scope is superseded "
                "by fixed_target_certificate.json, which proves the classification "
                "for every nonzero affine target and isolates xT=0 as the complete "
                "exceptional locus."
            ),
            "transport_scope": (
                "A full diagonal scaling with nonzero target exponent "
                "transports the target fiber to its GLV image; it does not "
                "preserve the same nonzero target."
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
                "The tables classify H_k exactly: scalar polynomial "
                "covariance under coordinatewise C3 scaling. Failure of this "
                "test is not, by itself, a classification of all geometric "
                "zero-variety automorphisms."
            ),
            "fixed_target": (
                "Nonidentity diagonal tuples move every nonzero target and are "
                "therefore target transports, not fixed-target symmetries; the "
                "complete target-value classification is in "
                "fixed_target_certificate.json."
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
