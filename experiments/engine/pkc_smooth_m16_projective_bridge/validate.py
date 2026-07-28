#!/usr/bin/env python3
"""Independently replay the TASK-018 projective-S17 certificate.

This validator imports neither the producer nor a shared mathematical helper.
It reconstructs the homogeneous S3 form, fixed-degree Sylvester resultants,
the recursive degree schedule, the F5/F25 boundary witnesses, and the complete
S5 enumerations over F5, F11, and F13 from constants in this file.
"""

from __future__ import annotations

import argparse
from functools import cache
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]

ARTIFACT_ID = "PKC-SMOOTH-M16-PROJECTIVE-S17-BRIDGE-001"
ARTIFACT_PATH = HERE / "artifact.json"
HASH_PATH = HERE / "artifact.sha256"
M = 16

TASK017_PATH = (
    "experiments/engine/pkc_smooth_m16_exceptional_fibers/artifact.json"
)
TASK017_SHA256 = (
    "578db732807a452e26de03dcd338d62c25a7d90490a62bbf427b1f96c3a869cf"
)
TASK016_PATH = (
    "experiments/engine/pkc_smooth_m16_semantic_bridge/artifact.json"
)
TASK016_SHA256 = (
    "963eea60097807ae0aa66a5d881b0c34bf0497ade53ed4d37d38861a73887c19"
)
PRIMARY_PATH = "data/source_claim_extracts/petit_kosters_messeng2016.json"
PRIMARY_SHA256 = (
    "f8839553f6935ed5cd331369cc13d91124373750c757b28eeca3ee773835f14f"
)

Projective = tuple[int, int]
F25 = tuple[int, int]

# Exponents are ordered X1,Z1,X2,Z2,X3,Z3.  Keeping the full term table here
# makes the replay independent of the producer's specialized coefficient code.
H_TERMS: tuple[tuple[int, tuple[int, ...]], ...] = (
    (1, (2, 0, 2, 0, 0, 2)),
    (1, (2, 0, 0, 2, 2, 0)),
    (1, (0, 2, 2, 0, 2, 0)),
    (-2, (2, 0, 1, 1, 1, 1)),
    (-2, (1, 1, 2, 0, 1, 1)),
    (-2, (1, 1, 1, 1, 2, 0)),
    (-28, (1, 1, 0, 2, 0, 2)),
    (-28, (0, 2, 1, 1, 0, 2)),
    (-28, (0, 2, 0, 2, 1, 1)),
)


class Replay:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def fail(self, message: str) -> None:
        self.failures.append(message)

    def exact(self, path: str, actual: Any, expected: Any) -> None:
        if actual != expected:
            self.fail(
                f"{path}: expected {expected!r}, observed {actual!r}"
            )

    def contains(self, path: str, actual: Any, token: str) -> None:
        if token not in str(actual):
            self.fail(f"{path}: missing required boundary {token!r}")

    def mapping(self, path: str, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            self.fail(f"{path}: expected object")
            return {}
        return value

    def sequence(self, path: str, value: Any) -> list[Any]:
        if not isinstance(value, list):
            self.fail(f"{path}: expected array")
            return []
        return value


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def value_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def p1(prime: int) -> tuple[Projective, ...]:
    return tuple((x, 1) for x in range(prime)) + ((1, 0),)


def h_eval(
    first: Projective,
    second: Projective,
    third: Projective,
    prime: int,
) -> int:
    values = (*first, *second, *third)
    total = 0
    for coefficient, exponents in H_TERMS:
        term = coefficient
        for value, exponent in zip(values, exponents, strict=True):
            term *= value**exponent
        total += term
    return total % prime


def h_coefficients(
    first: Projective, second: Projective, prime: int
) -> tuple[int, int, int]:
    """Return H(first,second,[U:V]) in descending U degree."""
    leading = h_eval(first, second, (1, 0), prime)
    constant = h_eval(first, second, (0, 1), prime)
    middle = (
        h_eval(first, second, (1, 1), prime) - leading - constant
    ) % prime
    return leading, middle, constant


def binary_eval(
    coefficients: tuple[int, ...] | list[int],
    value: Projective,
    prime: int,
) -> int:
    degree = len(coefficients) - 1
    u, v = value
    return sum(
        coefficient * u ** (degree - index) * v**index
        for index, coefficient in enumerate(coefficients)
    ) % prime


def sylvester(
    left: tuple[int, ...] | list[int],
    right: tuple[int, ...] | list[int],
    left_degree: int,
    right_degree: int,
) -> list[list[int]]:
    if len(left) != left_degree + 1:
        raise ValueError("left fixed-degree vector has the wrong length")
    if len(right) != right_degree + 1:
        raise ValueError("right fixed-degree vector has the wrong length")
    size = left_degree + right_degree
    matrix = [[0] * size for _ in range(size)]
    for shift in range(right_degree):
        matrix[shift][shift : shift + left_degree + 1] = left
    for shift in range(left_degree):
        row = right_degree + shift
        matrix[row][shift : shift + right_degree + 1] = right
    return matrix


def determinant_mod(matrix: list[list[int]], prime: int) -> int:
    work = [[entry % prime for entry in row] for row in matrix]
    result = 1
    for column in range(len(work)):
        pivot = next(
            (
                row
                for row in range(column, len(work))
                if work[row][column]
            ),
            None,
        )
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result = result * pivot_value % prime
        inverse = pow(pivot_value, -1, prime)
        for row in range(column + 1, len(work)):
            entry = work[row][column]
            if not entry:
                continue
            factor = entry * inverse % prime
            for offset in range(column, len(work)):
                work[row][offset] = (
                    work[row][offset]
                    - factor * work[column][offset]
                ) % prime
    return result % prime


@cache
def fixed_resultant_cached(
    left: tuple[int, ...],
    right: tuple[int, ...],
    left_degree: int,
    right_degree: int,
    prime: int,
) -> int:
    return determinant_mod(
        sylvester(left, right, left_degree, right_degree),
        prime,
    )


def fixed_resultant(
    left: tuple[int, ...] | list[int],
    right: tuple[int, ...] | list[int],
    left_degree: int,
    right_degree: int,
    prime: int,
) -> int:
    return fixed_resultant_cached(
        tuple(left), tuple(right), left_degree, right_degree, prime
    )


def polynomial_add(
    left: list[int], right: list[int], prime: int
) -> list[int]:
    result = [0] * max(len(left), len(right))
    for index in range(len(result)):
        result[index] = (
            (left[index] if index < len(left) else 0)
            + (right[index] if index < len(right) else 0)
        ) % prime
    return result


def polynomial_mul(
    left: list[int], right: list[int], prime: int
) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            result[left_index + right_index] = (
                result[left_index + right_index]
                + left_value * right_value
            ) % prime
    return result


def interpolate(values: list[int], prime: int) -> list[int]:
    """Interpolate ascending coefficients at x=0,...,len(values)-1."""
    total = [0] * len(values)
    for index, value in enumerate(values):
        basis = [1]
        denominator = 1
        for other in range(len(values)):
            if other == index:
                continue
            basis = polynomial_mul(basis, [(-other) % prime, 1], prime)
            denominator = denominator * (index - other) % prime
        scale = value * pow(denominator, -1, prime) % prime
        total = polynomial_add(
            total,
            [(coefficient * scale) % prime for coefficient in basis],
            prime,
        )
    return total


@cache
def c3_slice_coefficients(
    q1: Projective,
    q2: Projective,
    q3: Projective,
    prime: int,
) -> tuple[int, ...]:
    """Independently obtain fixed-degree C3 coefficients by interpolation."""
    left = h_coefficients(q1, q2, prime)
    values = []
    for y in range(5):
        # H(T,q3,Y) is symmetric, so its T-form is H(q3,Y,T).
        right = h_coefficients(q3, (y, 1), prime)
        values.append(fixed_resultant(left, right, 2, 2, prime))
    ascending = interpolate(values, prime)
    result = tuple(reversed(ascending))
    infinity = fixed_resultant(
        left, h_coefficients(q3, (1, 0), prime), 2, 2, prime
    )
    if result[0] != infinity:
        raise AssertionError("C3 interpolation lost its projective infinity value")
    return result


def legendre_symbol(value: int, prime: int) -> int:
    residue = value % prime
    if residue == 0:
        return 0
    power = pow(residue, (prime - 1) // 2, prime)
    if power == 1:
        return 1
    if power == prime - 1:
        return -1
    raise AssertionError("Euler criterion failed")


def base_liftable(value: Projective, prime: int) -> bool:
    if value[1] == 0:
        return True
    return legendre_symbol(value[0] ** 3 + 7, prime) >= 0


def projective_record(value: Projective, prime: int) -> dict[str, Any]:
    x, z = value
    if z == 0:
        return {"X": 1, "Z": 0, "kind": "infinity"}
    normalized = x * pow(z, -1, prime) % prime
    return {
        "X": normalized,
        "Z": 1,
        "kind": "finite",
        "x": normalized,
    }


def external_tuple_record(
    indices: tuple[int, int, int, int, int],
    domain: tuple[Projective, ...],
    prime: int,
) -> dict[str, Any]:
    return {
        name: projective_record(domain[index], prime)
        for name, index in zip(
            ("Q1", "Q2", "Q3", "Q4", "QT"),
            indices,
            strict=True,
        )
    }


def f25_add(left: F25, right: F25) -> F25:
    return (left[0] + right[0]) % 5, (left[1] + right[1]) % 5


def f25_mul(left: F25, right: F25) -> F25:
    # alpha^2 + 3 alpha + 4 = 0, hence alpha^2 = 2 alpha + 1.
    a, b = left
    c, d = right
    return (a * c + b * d) % 5, (a * d + b * c + 2 * b * d) % 5


def f25_pow(value: F25, exponent: int) -> F25:
    result = (1, 0)
    factor = value
    while exponent:
        if exponent & 1:
            result = f25_mul(result, factor)
        factor = f25_mul(factor, factor)
        exponent >>= 1
    return result


def f25_eval(coefficients: tuple[int, ...], value: F25) -> F25:
    result = (0, 0)
    for coefficient in coefficients:
        result = f25_add(
            f25_mul(result, value), (coefficient % 5, 0)
        )
    return result


def f25_h_eval(
    first: tuple[F25, F25],
    second: tuple[F25, F25],
    third: tuple[F25, F25],
) -> F25:
    values = (*first, *second, *third)
    total = (0, 0)
    for coefficient, exponents in H_TERMS:
        term = (coefficient % 5, 0)
        for value, exponent in zip(values, exponents, strict=True):
            term = f25_mul(term, f25_pow(value, exponent))
        total = f25_add(total, term)
    return total


def polynomial_product_desc(
    left: tuple[int, ...],
    right: tuple[int, ...],
    prime: int,
) -> tuple[int, ...]:
    ascending = polynomial_mul(
        list(reversed(left)), list(reversed(right)), prime
    )
    return tuple(reversed(ascending))


def expected_schedule() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for r in range(2, M + 1):
        output_degree = 1 << (r - 1)
        if r == 2:
            rows.append(
                {
                    "r": 2,
                    "name": "C2",
                    "semaev_arity": 3,
                    "leaf_count": 2,
                    "construction": "C2(Q1,Q2;Y)=H(Q1,Q2,Y)",
                    "output_projective_degree": 2,
                    "multidegree_each_coordinate_pair": 2,
                    "resultant_formal_degrees": None,
                    "sylvester_size": None,
                    "materialized_in_artifact": False,
                }
            )
            continue
        previous = 1 << (r - 2)
        rows.append(
            {
                "r": r,
                "name": f"C{r}",
                "semaev_arity": r + 1,
                "leaf_count": r,
                "construction": (
                    f"C{r}(Q1,...,Q{r};Y)="
                    f"hRes_T^({previous},2)("
                    f"C{r - 1}(Q1,...,Q{r - 1};T),H(T,Q{r},Y))"
                ),
                "elimination_coordinate": "T=[T_U:T_V]",
                "previous_formal_degree_in_T": previous,
                "right_H_formal_degree_in_T": 2,
                "resultant_formal_degrees": [previous, 2],
                "sylvester_size": previous + 2,
                "degree_in_left_form_coefficients": 2,
                "degree_in_right_H_coefficients": previous,
                "output_projective_degree": output_degree,
                "multidegree_each_coordinate_pair": output_degree,
                "materialized_in_artifact": False,
            }
        )
    return rows


@cache
def exhaustive_s5(prime: int) -> dict[str, Any]:
    domain = p1(prime)
    root_lists: dict[tuple[int, int], tuple[int, ...]] = {}
    root_masks: dict[tuple[int, int], int] = {}
    for left in range(len(domain)):
        for right in range(len(domain)):
            coefficients = h_coefficients(
                domain[left], domain[right], prime
            )
            roots = tuple(
                index
                for index, candidate in enumerate(domain)
                if binary_eval(coefficients, candidate, prime) == 0
            )
            root_lists[(left, right)] = roots
            root_masks[(left, right)] = sum(1 << index for index in roots)

    triples: list[tuple[int, int, int, tuple[int, ...], int]] = []
    for q1 in range(len(domain)):
        for q2 in range(len(domain)):
            first_roots = root_lists[(q1, q2)]
            for q3 in range(len(domain)):
                prefix_mask = 0
                for w2 in first_roots:
                    prefix_mask |= root_masks[(w2, q3)]
                triples.append(
                    (
                        q1,
                        q2,
                        q3,
                        c3_slice_coefficients(
                            domain[q1],
                            domain[q2],
                            domain[q3],
                            prime,
                        ),
                        prefix_mask,
                    )
                )

    right_forms = {
        (q4, target): h_coefficients(
            domain[q4], domain[target], prime
        )
        for q4 in range(len(domain))
        for target in range(len(domain))
    }
    liftable = tuple(base_liftable(value, prime) for value in domain)
    counts = {
        "tuple_count": 0,
        "recursive_zero_count": 0,
        "ratcat_count": 0,
        "recursive_zero_without_ratcat_count": 0,
        "ratcat_without_recursive_zero_count": 0,
        "base_liftable_tuple_count": 0,
        "base_liftable_recursive_zero_count": 0,
        "base_liftable_ratcat_count": 0,
        "base_liftable_mismatch_count": 0,
    }
    stream = hashlib.sha256()
    stream.update(f"TASK018-F{prime}-C4-ENUMERATION-v1\n".encode())
    examples: dict[str, Any] = {}
    for q1, q2, q3, left, prefix_mask in triples:
        for q4 in range(len(domain)):
            for target in range(len(domain)):
                right = right_forms[(q4, target)]
                resultant = fixed_resultant(left, right, 4, 2, prime)
                recursive_zero = resultant == 0
                ratcat = bool(prefix_mask & root_masks[(q4, target)])
                indices = (q1, q2, q3, q4, target)
                all_lift = all(liftable[index] for index in indices)
                counts["tuple_count"] += 1
                counts["recursive_zero_count"] += int(recursive_zero)
                counts["ratcat_count"] += int(ratcat)
                counts["recursive_zero_without_ratcat_count"] += int(
                    recursive_zero and not ratcat
                )
                counts["ratcat_without_recursive_zero_count"] += int(
                    ratcat and not recursive_zero
                )
                counts["base_liftable_tuple_count"] += int(all_lift)
                counts["base_liftable_recursive_zero_count"] += int(
                    all_lift and recursive_zero
                )
                counts["base_liftable_ratcat_count"] += int(
                    all_lift and ratcat
                )
                counts["base_liftable_mismatch_count"] += int(
                    all_lift and recursive_zero != ratcat
                )
                stream.update(
                    bytes(
                        [
                            q1,
                            q2,
                            q3,
                            q4,
                            target,
                            resultant,
                            int(ratcat),
                            int(all_lift),
                        ]
                    )
                )
                if recursive_zero and ratcat:
                    key = (
                        "base_liftable_zero"
                        if all_lift
                        else "ratcat_zero"
                    )
                    if key not in examples:
                        final_roots = set(root_lists[(q4, target)])
                        witness: tuple[int, int] | None = None
                        for w2 in root_lists[(q1, q2)]:
                            for w3 in root_lists[(w2, q3)]:
                                if w3 in final_roots:
                                    witness = (w2, w3)
                                    break
                            if witness is not None:
                                break
                        if witness is None:
                            raise AssertionError(
                                "RatCat classification lost its tree witness"
                            )
                        w2, w3 = witness
                        examples[key] = {
                            "external": external_tuple_record(
                                indices, domain, prime
                            ),
                            "witness": {
                                "W2": projective_record(domain[w2], prime),
                                "W3": projective_record(domain[w3], prime),
                            },
                            "fixed_resultant_mod_p": resultant,
                        }
                if (
                    recursive_zero
                    and not ratcat
                    and "recursive_zero_without_Fp_tree" not in examples
                ):
                    examples["recursive_zero_without_Fp_tree"] = {
                        "external": external_tuple_record(
                            indices, domain, prime
                        ),
                        "fixed_resultant_mod_p": resultant,
                        "Fp_tree_witness_count": 0,
                    }
    return {
        "counts": counts,
        "stream_sha256": stream.hexdigest(),
        "projective_coordinate_count": len(domain),
        "base_liftable_coordinate_count": sum(liftable),
        "base_liftable_coordinate_indices": [
            index for index, value in enumerate(liftable) if value
        ],
        "named_examples": examples,
    }


def check_hash(
    artifact_bytes: bytes, hash_path: Path, replay: Replay
) -> None:
    expected = hashlib.sha256(artifact_bytes).hexdigest()
    try:
        line = hash_path.read_text(encoding="ascii")
    except FileNotFoundError:
        replay.fail("artifact.sha256 is missing")
        return
    replay.exact(
        "artifact.sha256", line, f"{expected}  artifact.json\n"
    )


def check_dependencies(document: dict[str, Any], replay: Replay) -> None:
    dependencies = replay.sequence("depends_on", document.get("depends_on"))
    expected = (
        (TASK017_PATH, TASK017_SHA256),
        (TASK016_PATH, TASK016_SHA256),
        (PRIMARY_PATH, PRIMARY_SHA256),
    )
    replay.exact("depends_on length", len(dependencies), len(expected))
    for index, (path, digest) in enumerate(expected):
        if index >= len(dependencies):
            continue
        record = replay.mapping(f"depends_on[{index}]", dependencies[index])
        replay.exact(
            f"depends_on[{index}] keys",
            set(record),
            {
                "path",
                "required_sha256",
                "observed_sha256",
                "digest_match",
            },
        )
        replay.exact(f"depends_on[{index}].path", record.get("path"), path)
        replay.exact(
            f"depends_on[{index}].required_sha256",
            record.get("required_sha256"),
            digest,
        )
        replay.exact(
            f"depends_on[{index}].observed_sha256",
            record.get("observed_sha256"),
            digest,
        )
        replay.exact(
            f"depends_on[{index}].digest_match",
            record.get("digest_match"),
            True,
        )
        source = REPO_ROOT / path
        if not source.is_file():
            replay.fail(f"depends_on[{index}]: path does not exist")
        elif file_digest(source) != digest:
            replay.fail(f"depends_on[{index}]: live dependency digest drifted")


def check_definition(document: dict[str, Any], replay: Replay) -> None:
    frozen = replay.mapping(
        "frozen_definition", document.get("frozen_definition")
    )
    h_polynomial = (
        "X1^2*X2^2*Z3^2 + X1^2*Z2^2*X3^2 + "
        "Z1^2*X2^2*X3^2 - 2*X1^2*X2*Z2*X3*Z3 - "
        "2*X1*Z1*X2^2*X3*Z3 - "
        "2*X1*Z1*X2*Z2*X3^2 - "
        "28*(X1*Z1*Z2^2*Z3^2 + "
        "Z1^2*X2*Z2*Z3^2 + Z1^2*Z2^2*X3*Z3)"
    )
    coordinate_order = [
        *[
            f"Q{index}=[X{index}:Z{index}]"
            for index in range(1, 17)
        ],
        "QT=[XT:ZT]",
    ]
    irrelevant = {
        "external_pair_ideals": [
            *[
                f"<X{index},Z{index}>"
                for index in range(1, 17)
            ],
            "<XT,ZT>",
        ],
        "tree_internal_pair_ideals": [
            f"<U{index},V{index}>" for index in range(2, 16)
        ],
        "excluded_locus": (
            "the union where any listed coordinate pair is [0:0]"
        ),
        "only_allowed_set_theoretic_saturation": (
            "the product of the 31 coordinate-pair irrelevant ideals"
        ),
        "forbidden_extra_saturands": [
            "coordinate differences",
            "tangent loci",
            "duplicate loci",
            "identity or two-torsion loci",
        ],
    }
    replay.exact(
        "frozen_definition",
        frozen,
        {
            "name": "RecS17=C16(Q1,...,Q16;QT)",
            "curve_domain": {
                "curve": "E:y^2=x^3+7",
                "field": "any field k with char(k) not in {2,3,7}",
                "algebraic_closure": "kbar",
                "discriminant": "-16*27*7^2",
                "excluded_characteristics": [2, 3, 7],
            },
            "coordinate_order": coordinate_order,
            "valid_projective_domain": (
                "every external and internal coordinate pair differs "
                "from [0:0]"
            ),
            "kummer_coordinate": {
                "identity": "kappa(O)=[1:0]",
                "affine_point": "kappa((x,y))=[x:1]",
            },
            "H_name": "H=S3h",
            "H_multidegree": [2, 2, 2],
            "H_polynomial": h_polynomial,
            "base_case": "C2(Q1,Q2;Y)=H(Q1,Q2,Y)",
            "recursive_case": (
                "for 3<=r<=16, C_r(Q1,...,Qr;Y)="
                "hRes_T^(2^(r-2),2)("
                "C_(r-1)(Q1,...,Q_(r-1);T),H(T,Qr,Y))"
            ),
            "elimination_order": [
                f"C{r - 1} and H eliminate T to construct C{r}"
                for r in range(3, 17)
            ],
            "final_predicate": (
                "RecS17_k(Q1,...,Q16,QT) iff "
                "C16(Q1,...,Q16;QT)=0 in k"
            ),
            "literal_materialization": {
                "C16_expanded": False,
                "C16_evaluated": False,
                "M16_system_materialized": False,
                "definition_is_recursive_dag_only": True,
            },
            "irrelevant_ideal_exclusion": irrelevant,
        },
    )
    replay.exact(
        "frozen_definition.name",
        frozen.get("name"),
        "RecS17=C16(Q1,...,Q16;QT)",
    )
    domain = replay.mapping(
        "frozen_definition.curve_domain", frozen.get("curve_domain")
    )
    replay.exact(
        "frozen_definition.curve_domain.excluded_characteristics",
        domain.get("excluded_characteristics"),
        [2, 3, 7],
    )
    replay.contains(
        "frozen_definition.curve_domain.curve",
        domain.get("curve"),
        "y^2=x^3+7",
    )
    replay.exact(
        "frozen_definition.H_multidegree",
        frozen.get("H_multidegree"),
        [2, 2, 2],
    )
    replay.exact("frozen_definition.H_name", frozen.get("H_name"), "H=S3h")
    replay.exact(
        "frozen_definition.H_polynomial",
        frozen.get("H_polynomial"),
        h_polynomial,
    )
    replay.exact(
        "frozen_definition.base_case",
        frozen.get("base_case"),
        "C2(Q1,Q2;Y)=H(Q1,Q2,Y)",
    )
    replay.contains(
        "frozen_definition.recursive_case",
        frozen.get("recursive_case"),
        "hRes_T^(2^(r-2),2)",
    )
    replay.contains(
        "frozen_definition.final_predicate",
        frozen.get("final_predicate"),
        "C16(Q1,...,Q16;QT)=0",
    )
    replay.exact(
        "frozen_definition.kummer_coordinate.identity",
        replay.mapping(
            "frozen_definition.kummer_coordinate",
            frozen.get("kummer_coordinate"),
        ).get("identity"),
        "kappa(O)=[1:0]",
    )
    materialization = replay.mapping(
        "frozen_definition.literal_materialization",
        frozen.get("literal_materialization"),
    )
    replay.exact(
        "frozen_definition.literal_materialization",
        materialization,
        {
            "C16_expanded": False,
            "C16_evaluated": False,
            "M16_system_materialized": False,
            "definition_is_recursive_dag_only": True,
        },
    )
    irrelevant = replay.mapping(
        "frozen_definition.irrelevant_ideal_exclusion",
        frozen.get("irrelevant_ideal_exclusion"),
    )
    replay.contains(
        "frozen_definition.valid_projective_domain",
        frozen.get("valid_projective_domain"),
        "[0:0]",
    )
    replay.exact(
        "frozen_definition.irrelevant_ideal_exclusion.forbidden_extra_saturands",
        irrelevant.get("forbidden_extra_saturands"),
        [
            "coordinate differences",
            "tangent loci",
            "duplicate loci",
            "identity or two-torsion loci",
        ],
    )
    replay.exact(
        "frozen_definition.coordinate_order",
        replay.sequence(
            "frozen_definition.coordinate_order",
            frozen.get("coordinate_order"),
        ),
        coordinate_order,
    )
    replay.exact(
        "frozen_definition.irrelevant_ideal_exclusion.only_allowed_set_theoretic_saturation",
        irrelevant.get("only_allowed_set_theoretic_saturation"),
        "the product of the 31 coordinate-pair irrelevant ideals",
    )


def check_schedule(document: dict[str, Any], replay: Replay) -> None:
    degree = replay.mapping(
        "degree_schedule", document.get("degree_schedule")
    )
    rows = expected_schedule()
    expected_degree_schedule = {
        "formula": (
            "d_r=2^(r-1), where d_r is the degree of C_r in each "
            "of its r+1 projective coordinate pairs"
        ),
        "rows": rows,
        "rows_sha256": value_digest(rows),
        "C16_external_coordinate_pair_count": 17,
        "C16_multidegree_each_external_pair": 32_768,
        "C16_multidegree_vector": [32_768] * 17,
        "C16_final_resultant_formal_degrees": [16_384, 2],
        "C16_final_sylvester_size": 16_386,
        "full_17_coordinate_affine_total_degree_capacity": 557_056,
        "fixed_target_16_leaf_affine_degree_capacity_subtotal": 524_288,
        "capacity_warning": (
            "557056 and 524288 are multidegree-box capacity sums, "
            "not the actual total degree, solving degree, degree of "
            "regularity, matrix size, rank, memory, or work estimate"
        ),
    }
    replay.exact(
        "degree_schedule", degree, expected_degree_schedule
    )
    replay.exact("degree_schedule.rows", degree.get("rows"), rows)
    replay.exact(
        "degree_schedule.rows_sha256",
        degree.get("rows_sha256"),
        value_digest(rows),
    )
    replay.exact(
        "degree_schedule.C16_multidegree_each_external_pair",
        degree.get("C16_multidegree_each_external_pair"),
        32_768,
    )
    replay.exact(
        "degree_schedule.C16_multidegree_vector",
        degree.get("C16_multidegree_vector"),
        [32_768] * 17,
    )
    replay.exact(
        "degree_schedule.C16_final_resultant_formal_degrees",
        degree.get("C16_final_resultant_formal_degrees"),
        [16_384, 2],
    )
    replay.exact(
        "degree_schedule.C16_final_sylvester_size",
        degree.get("C16_final_sylvester_size"),
        16_386,
    )
    replay.exact(
        "degree_schedule.full_17_coordinate_affine_total_degree_capacity",
        degree.get("full_17_coordinate_affine_total_degree_capacity"),
        557_056,
    )
    replay.exact(
        "degree_schedule.fixed_target_16_leaf_affine_degree_capacity_subtotal",
        degree.get(
            "fixed_target_16_leaf_affine_degree_capacity_subtotal"
        ),
        524_288,
    )
    warning = degree.get("capacity_warning")
    for token in ("not the actual total degree", "solving degree", "work estimate"):
        replay.contains("degree_schedule.capacity_warning", warning, token)


def check_convention(document: dict[str, Any], replay: Replay) -> None:
    convention = replay.mapping(
        "coefficient_and_sylvester_convention",
        document.get("coefficient_and_sylvester_convention"),
    )
    replay.exact(
        "coefficient_and_sylvester_convention",
        convention,
        {
            "binary_form_coefficients": (
                "F(U,V)=sum_(i=0)^m f_i*U^(m-i)*V^i is stored "
                "as [f_0,...,f_m], descending U degree"
            ),
            "dehomogenization_chart": (
                "F(t,1)=sum f_i*t^(m-i), while the declared formal "
                "degree m and leading zero coefficients are retained"
            ),
            "sylvester_rows": (
                "for formal degrees (m,n), rows 0..n-1 are n shifted "
                "copies of [f_0,...,f_m]; rows n..n+m-1 are m shifted "
                "copies of [g_0,...,g_n]"
            ),
            "hRes_definition": (
                "hRes_T^(m,n)(F,G)=det(Syl_(m,n)(F(t,1),G(t,1)))"
            ),
            "matrix_column_order": (
                "descending monomial slots of total Sylvester width m+n"
            ),
            "determinant_sign": (
                "ordinary Leibniz determinant; row order above is literal"
            ),
            "swap_rule": (
                "hRes^(m,n)(F,G)=(-1)^(m*n)*hRes^(n,m)(G,F)"
            ),
            "formal_degree_reduction": "forbidden",
            "primitive_part_or_content_division": "forbidden",
            "monic_normalization": "forbidden",
            "literal_coefficient_unit": 1,
            "literal_unit_scope": (
                "coefficient unit 1 applies only when argument order, "
                "binary coefficient order, formal degrees, Sylvester row "
                "order, and determinant convention are exactly the frozen "
                "ones"
            ),
            "projective_rescaling_rule": (
                "rescaling any valid projective coordinate representative "
                "multiplies C_r by the corresponding nonzero field scalar "
                "raised to its declared degree d_r; for C16 each of the 17 "
                "representative scalars occurs to exponent 32768"
            ),
            "unit_convention": (
                "the recursive polynomial is the literal determinant with "
                "coefficient unit 1 under the frozen convention; projective "
                "coordinate rescaling may multiply its value by the declared "
                "nonzero field unit, while no variable-dependent factor may "
                "be discarded"
            ),
            "infinity_rule": (
                "[1:0] is a common root exactly when the two retained "
                "formal leading coefficients vanish; fixed-degree "
                "resultants therefore keep this valid stratum"
            ),
        },
    )
    replay.contains(
        "coefficient_and_sylvester_convention.binary_form_coefficients",
        convention.get("binary_form_coefficients"),
        "descending U degree",
    )
    replay.exact(
        "coefficient_and_sylvester_convention.sylvester_rows",
        convention.get("sylvester_rows"),
        (
            "for formal degrees (m,n), rows 0..n-1 are n shifted "
            "copies of [f_0,...,f_m]; rows n..n+m-1 are m shifted "
            "copies of [g_0,...,g_n]"
        ),
    )
    replay.exact(
        "coefficient_and_sylvester_convention.hRes_definition",
        convention.get("hRes_definition"),
        "hRes_T^(m,n)(F,G)=det(Syl_(m,n)(F(t,1),G(t,1)))",
    )
    replay.exact(
        "coefficient_and_sylvester_convention.swap_rule",
        convention.get("swap_rule"),
        "hRes^(m,n)(F,G)=(-1)^(m*n)*hRes^(n,m)(G,F)",
    )
    replay.contains(
        "coefficient_and_sylvester_convention.determinant_sign",
        convention.get("determinant_sign"),
        "ordinary Leibniz determinant",
    )
    for field in (
        "formal_degree_reduction",
        "primitive_part_or_content_division",
        "monic_normalization",
    ):
        replay.exact(
            f"coefficient_and_sylvester_convention.{field}",
            convention.get(field),
            "forbidden",
        )
    replay.contains(
        "coefficient_and_sylvester_convention.unit_convention",
        convention.get("unit_convention"),
        "literal determinant",
    )
    replay.exact(
        "coefficient_and_sylvester_convention.literal_coefficient_unit",
        convention.get("literal_coefficient_unit"),
        1,
    )
    replay.exact(
        "coefficient_and_sylvester_convention.literal_unit_scope",
        convention.get("literal_unit_scope"),
        (
            "coefficient unit 1 applies only when argument order, binary "
            "coefficient order, formal degrees, Sylvester row order, and "
            "determinant convention are exactly the frozen ones"
        ),
    )
    replay.exact(
        "coefficient_and_sylvester_convention.projective_rescaling_rule",
        convention.get("projective_rescaling_rule"),
        (
            "rescaling any valid projective coordinate representative "
            "multiplies C_r by the corresponding nonzero field scalar "
            "raised to its declared degree d_r; for C16 each of the 17 "
            "representative scalars occurs to exponent 32768"
        ),
    )
    replay.contains(
        "coefficient_and_sylvester_convention.unit_convention",
        convention.get("unit_convention"),
        "no variable-dependent factor may be discarded",
    )
    replay.contains(
        "coefficient_and_sylvester_convention.infinity_rule",
        convention.get("infinity_rule"),
        "[1:0]",
    )


def check_f5_infinity(fixture: dict[str, Any], replay: Replay) -> None:
    prime = 5
    q0 = (0, 1)
    q3 = (3, 1)
    left = h_coefficients(q0, q0, prime)
    right = h_coefficients(q3, q3, prime)
    fixed_matrix = sylvester(left, right, 2, 2)
    fixed_result = determinant_mod(fixed_matrix, prime)
    reduced_left = left[1:]
    reduced_right = right[1:]
    reduced_matrix = sylvester(reduced_left, reduced_right, 1, 1)
    reduced_result = determinant_mod(reduced_matrix, prime)
    common = [
        value
        for value in p1(prime)
        if binary_eval(left, value, prime) == 0
        and binary_eval(right, value, prime) == 0
    ]
    replay.exact(
        "fixtures.F5_fixed_vs_reduced_infinity",
        fixture,
        {
            "field": "F5",
            "curve": "y^2=x^3+7 = x^3+2",
            "recursive_step": "C3=S4",
            "external_tuple_x": [0, 0, 3, 3],
            "left_H00_coefficients_descending_U": list(left),
            "right_H33_coefficients_descending_U": list(right),
            "left_binary_factorization": "2*U*V",
            "right_binary_factorization": "V*(4*U+3*V)",
            "fixed_formal_degrees": [2, 2],
            "fixed_sylvester_matrix": fixed_matrix,
            "fixed_resultant_mod_5": fixed_result,
            "fixed_common_projective_roots": [
                {"U": 1, "V": 0, "kind": "infinity"}
            ],
            "reduced_affine_coefficients_descending_t": {
                "left": list(reduced_left),
                "right": list(reduced_right),
            },
            "reduced_actual_degrees": [1, 1],
            "reduced_sylvester_matrix": reduced_matrix,
            "reduced_affine_resultant_mod_5": reduced_result,
            "reduced_affine_common_roots": [],
            "fault_detected": (
                "reducing to actual affine degree deletes the valid "
                "common projective root [1:0]"
            ),
            "required_disposition": "retain_identity_infinity_stratum",
            "status": "exact",
        },
    )
    replay.exact(
        "fixtures.F5_fixed_vs_reduced_infinity.left",
        fixture.get("left_H00_coefficients_descending_U"),
        list(left),
    )
    replay.exact(
        "fixtures.F5_fixed_vs_reduced_infinity.right",
        fixture.get("right_H33_coefficients_descending_U"),
        list(right),
    )
    replay.exact(
        "fixtures.F5_fixed_vs_reduced_infinity.fixed_sylvester_matrix",
        fixture.get("fixed_sylvester_matrix"),
        fixed_matrix,
    )
    replay.exact(
        "fixtures.F5_fixed_vs_reduced_infinity.fixed_resultant_mod_5",
        fixture.get("fixed_resultant_mod_5"),
        fixed_result,
    )
    replay.exact(
        "fixtures.F5_fixed_vs_reduced_infinity.reduced_sylvester_matrix",
        fixture.get("reduced_sylvester_matrix"),
        reduced_matrix,
    )
    replay.exact(
        "fixtures.F5_fixed_vs_reduced_infinity.reduced_affine_resultant_mod_5",
        fixture.get("reduced_affine_resultant_mod_5"),
        reduced_result,
    )
    replay.exact(
        "fixtures.F5_fixed_vs_reduced_infinity.common root",
        common,
        [(1, 0)],
    )
    replay.exact(
        "fixtures.F5_fixed_vs_reduced_infinity.required_disposition",
        fixture.get("required_disposition"),
        "retain_identity_infinity_stratum",
    )
    replay.exact(
        "fixtures.F5_fixed_vs_reduced_infinity.status",
        fixture.get("status"),
        "exact",
    )


def check_f5_f25(fixture: dict[str, Any], replay: Replay) -> None:
    prime = 5
    q0 = (0, 1)
    q3 = (3, 1)
    left = c3_slice_coefficients(q0, q0, q3, prime)
    right = h_coefficients(q0, q3, prime)
    quotient = (4, 1, 1)
    resultant_matrix = sylvester(left, right, 4, 2)
    resultant = determinant_mod(resultant_matrix, prime)
    discriminant = (right[1] ** 2 - 4 * right[0] * right[2]) % prime
    base_roots = [
        value
        for value in range(prime)
        if binary_eval(right, (value, 1), prime) == 0
    ]
    all_f25 = tuple((a, b) for a in range(5) for b in range(5))
    common_f25 = [
        value
        for value in all_f25
        if f25_eval(left, value) == (0, 0)
        and f25_eval(right, value) == (0, 0)
    ]
    replay.exact("independent F5 C3 coefficients", left, (1, 2, 0, 3, 1))
    replay.exact("independent F5 H coefficients", right, (4, 2, 1))
    replay.exact("independent F5/F25 resultant", resultant, 0)
    replay.exact("independent F5 discriminant", discriminant, 3)
    replay.exact("independent F5 common roots", base_roots, [])
    replay.exact(
        "independent F25 common roots",
        common_f25,
        [(0, 1), (2, 4)],
    )
    replay.exact(
        "fixtures.F5_F25_extension_only_nonlift.external_tuple_x",
        fixture.get("external_tuple_x"),
        [0, 0, 3, 0, 3],
    )
    replay.exact(
        "fixtures.F5_F25_extension_only_nonlift.left",
        fixture.get("left_C3_S4_coefficients_descending_T"),
        list(left),
    )
    replay.exact(
        "fixtures.F5_F25_extension_only_nonlift.right",
        fixture.get("right_H_coefficients_descending_T"),
        list(right),
    )
    replay.exact(
        "fixtures.F5_F25_extension_only_nonlift.quotient",
        fixture.get("exact_division_quotient_descending_T"),
        list(quotient),
    )
    replay.exact(
        "fixtures.F5_F25_extension_only_nonlift.product",
        polynomial_product_desc(right, quotient, prime),
        left,
    )
    replay.exact(
        "fixtures.F5_F25_extension_only_nonlift.sylvester",
        fixture.get("C4_S5_sylvester_matrix"),
        resultant_matrix,
    )
    replay.exact(
        "fixtures.F5_F25_extension_only_nonlift.resultant",
        fixture.get("C4_S5_resultant_mod_5"),
        resultant,
    )
    replay.exact(
        "fixtures.F5_F25_extension_only_nonlift.discriminant",
        fixture.get("right_quadratic_discriminant_mod_5"),
        discriminant,
    )
    replay.exact(
        "fixtures.F5_F25_extension_only_nonlift.common_roots_in_F5",
        fixture.get("common_roots_in_F5"),
        base_roots,
    )
    expected_f25 = [
        {"constant": value[0], "alpha": value[1]}
        for value in common_f25
    ]
    replay.exact(
        "fixtures.F5_F25_extension_only_nonlift.common_roots_in_F25",
        fixture.get("common_roots_in_F25"),
        expected_f25,
    )
    replay.exact(
        "fixtures.F5_F25_extension_only_nonlift.alpha Frobenius",
        f25_pow((0, 1), 5),
        (2, 4),
    )
    replay.exact(
        "fixtures.F5_F25_extension_only_nonlift.nonlift positions",
        fixture.get("nonlift_external_positions_one_based"),
        [1, 2, 4],
    )
    nonlift = replay.mapping(
        "fixtures.F5_F25_extension_only_nonlift.nonlift_check",
        fixture.get("nonlift_check"),
    )
    replay.exact(
        "fixtures.F5_F25_extension_only_nonlift.nonlift_check",
        (
            nonlift.get("x"),
            nonlift.get("curve_rhs_mod_5"),
            nonlift.get("legendre_symbol"),
        ),
        (0, 2, -1),
    )
    replay.exact(
        "fixtures.F5_F25_extension_only_nonlift.required_disposition",
        fixture.get("required_disposition"),
        "EXTERNAL_NONLIFT",
    )
    replay.contains(
        "fixtures.F5_F25_extension_only_nonlift.combined_boundary",
        fixture.get("combined_boundary"),
        "not a pure internal-extension counterexample",
    )
    replay.exact(
        "fixtures.F5_F25_extension_only_nonlift.predicate_values",
        fixture.get("predicate_values"),
        {
            "RecS5_F5": True,
            "GeoCat_F25": True,
            "RatCat_F5": False,
            "Recover_F5": False,
        },
    )
    zero: F25 = (0, 0)
    one: F25 = (1, 0)
    alpha: F25 = (0, 1)
    q0 = (zero, one)
    q3 = ((3, 0), one)
    w2 = q0
    w3 = (alpha, one)
    vertex_values = {
        "H_Q1_Q2_W2": 0,
        "H_W2_Q3_W3": {"constant": 0, "alpha": 0},
        "H_W3_Q4_QT_by_symmetry": {"constant": 0, "alpha": 0},
    }
    expected_witness = {
        "W2": {"U": 0, "V": 1, "field": "F5"},
        "W3": {
            "U": {"constant": 0, "alpha": 1},
            "V": {"constant": 1, "alpha": 0},
            "field": "F25",
        },
        "vertex_values": vertex_values,
    }
    replay.exact(
        "independent F25 H(Q0,Q0,W2)",
        f25_h_eval(q0, q0, w2),
        zero,
    )
    replay.exact(
        "independent F25 H(W2,Q3,W3)",
        f25_h_eval(w2, q3, w3),
        zero,
    )
    replay.exact(
        "independent F25 H(W3,Q0,Q3)",
        f25_h_eval(w3, q0, q3),
        zero,
    )
    replay.exact(
        "fixtures.F5_F25_extension_only_nonlift.chosen_tree_witness",
        fixture.get("chosen_tree_witness"),
        expected_witness,
    )
    replay.exact(
        "fixtures.F5_F25_extension_only_nonlift",
        fixture,
        {
            "base_field": "F5",
            "witness_field": "F25",
            "witness_field_presentation": {
                "basis": ["1", "alpha"],
                "modulus_descending_alpha": [1, 3, 4],
                "relation": "alpha^2=2*alpha+1",
                "frobenius": "alpha^5=2-alpha",
            },
            "external_tuple": {
                "Q1": {"X": 0, "Z": 1},
                "Q2": {"X": 0, "Z": 1},
                "Q3": {"X": 3, "Z": 1},
                "Q4": {"X": 0, "Z": 1},
                "QT": {"X": 3, "Z": 1},
            },
            "external_tuple_x": [0, 0, 3, 0, 3],
            "left_form": "C3(Q1,Q2,Q3;T)=S4(Q1,Q2,Q3,T)",
            "left_C3_S4_coefficients_descending_T": list(left),
            "right_form": "H(T,Q4,QT)",
            "right_H_coefficients_descending_T": list(right),
            "exact_division_quotient_descending_T": list(quotient),
            "exact_division_remainder": [0],
            "right_quadratic_discriminant_mod_5": discriminant,
            "right_quadratic_irreducible_over_F5": True,
            "C4_S5_formal_resultant_degrees": [4, 2],
            "C4_S5_sylvester_matrix": resultant_matrix,
            "C4_S5_resultant_mod_5": resultant,
            "common_roots_in_F5": base_roots,
            "common_roots_in_F25": expected_f25,
            "chosen_tree_witness": expected_witness,
            "predicate_values": {
                "RecS5_F5": True,
                "GeoCat_F25": True,
                "RatCat_F5": False,
                "Recover_F5": False,
            },
            "nonlift_external_positions_one_based": [1, 2, 4],
            "nonlift_check": {
                "x": 0,
                "curve_rhs_mod_5": 2,
                "legendre_symbol": -1,
            },
            "combined_boundary": (
                "the common top-elimination roots are in F25 and the "
                "external x=0 coordinates do not lift to E(F5); this is "
                "not a pure internal-extension counterexample with "
                "liftable externals"
            ),
            "required_disposition": "EXTERNAL_NONLIFT",
            "status": "exact",
        },
    )


def check_exhaustive(
    fixtures: dict[str, Any], replay: Replay
) -> None:
    expected_counts = {
        5: {
            "tuple_count": 7_776,
            "recursive_zero_count": 1_648,
            "ratcat_count": 1_072,
            "recursive_zero_without_ratcat_count": 576,
            "ratcat_without_recursive_zero_count": 0,
            "base_liftable_recursive_zero_count": 432,
            "base_liftable_ratcat_count": 432,
            "base_liftable_mismatch_count": 0,
        },
        11: {
            "tuple_count": 248_832,
            "recursive_zero_count": 23_328,
            "ratcat_count": 15_352,
            "recursive_zero_without_ratcat_count": 7_976,
            "ratcat_without_recursive_zero_count": 0,
            "base_liftable_recursive_zero_count": 6_442,
            "base_liftable_ratcat_count": 6_442,
            "base_liftable_mismatch_count": 0,
        },
        13: {
            "tuple_count": 537_824,
            "recursive_zero_count": 87_507,
            "ratcat_count": 81_147,
            "recursive_zero_without_ratcat_count": 6_360,
            "ratcat_without_recursive_zero_count": 0,
            "base_liftable_recursive_zero_count": 766,
            "base_liftable_ratcat_count": 766,
            "base_liftable_mismatch_count": 0,
        },
    }
    bounded = replay.mapping(
        "fixtures.bounded_exhaustive_S5",
        fixtures.get("bounded_exhaustive_S5"),
    )
    replay.exact(
        "fixtures.bounded_exhaustive_S5 keys",
        set(bounded),
        {"F5", "F11", "F13"},
    )
    for prime, partial_expected in expected_counts.items():
        key = f"F{prime}"
        fixture = replay.mapping(
            f"fixtures.bounded_exhaustive_S5.{key}",
            bounded.get(key),
        )
        independently_replayed = exhaustive_s5(prime)
        counts = independently_replayed["counts"]
        expected_fixture = {
            "field": key,
            "curve": "nonsingular y^2=x^3+7",
            "projective_coordinate_count": prime + 1,
            "projective_representatives_order": (
                f"[0:1],...,[{prime - 1}:1],[1:0]"
            ),
            "external_arity": 5,
            "recursive_form": "C4(Q1,Q2,Q3,Q4;QT)=S5",
            "formal_top_resultant_degrees": [4, 2],
            "enumeration": f"all ordered P1(F{prime})^5 tuples",
            "base_liftable_coordinate_count": independently_replayed[
                "base_liftable_coordinate_count"
            ],
            "base_liftable_coordinate_indices": independently_replayed[
                "base_liftable_coordinate_indices"
            ],
            "counts": counts,
            "classification": {
                "fixed_recursive_resultant_zero_count": counts[
                    "recursive_zero_count"
                ],
                "RatCat_Fp_count": counts["ratcat_count"],
                "recursive_zero_without_Fp_tree_count": counts[
                    "recursive_zero_without_ratcat_count"
                ],
                "all_external_base_liftable_zero_count": counts[
                    "base_liftable_recursive_zero_count"
                ],
                "all_external_base_liftable_Rec_vs_Rat_mismatch": counts[
                    "base_liftable_mismatch_count"
                ],
            },
            "enumeration_stream_sha256": independently_replayed[
                "stream_sha256"
            ],
            "named_examples": independently_replayed["named_examples"],
            "status": "exact_exhaustive",
        }
        replay.exact(
            f"fixtures.bounded_exhaustive_S5.{key}",
            fixture,
            expected_fixture,
        )
        for field, value in partial_expected.items():
            replay.exact(
                f"independent F{prime} exhaustive {field}",
                counts.get(field),
                value,
            )
        replay.exact(
            f"fixtures.bounded_exhaustive_S5.{key}.counts",
            fixture.get("counts"),
            counts,
        )
        replay.exact(
            f"fixtures.bounded_exhaustive_S5.{key}.stream",
            fixture.get("enumeration_stream_sha256"),
            independently_replayed["stream_sha256"],
        )
        replay.exact(
            f"fixtures.bounded_exhaustive_S5.{key}.coordinate_count",
            fixture.get("projective_coordinate_count"),
            independently_replayed["projective_coordinate_count"],
        )
        replay.exact(
            f"fixtures.bounded_exhaustive_S5.{key}.liftable count",
            fixture.get("base_liftable_coordinate_count"),
            independently_replayed["base_liftable_coordinate_count"],
        )
        replay.exact(
            f"fixtures.bounded_exhaustive_S5.{key}.liftable indices",
            fixture.get("base_liftable_coordinate_indices"),
            independently_replayed["base_liftable_coordinate_indices"],
        )
        replay.exact(
            f"fixtures.bounded_exhaustive_S5.{key}.status",
            fixture.get("status"),
            "exact_exhaustive",
        )
        classification = replay.mapping(
            f"fixtures.bounded_exhaustive_S5.{key}.classification",
            fixture.get("classification"),
        )
        replay.exact(
            f"fixtures.bounded_exhaustive_S5.{key}.classification zero",
            classification.get("fixed_recursive_resultant_zero_count"),
            counts["recursive_zero_count"],
        )
        replay.exact(
            f"fixtures.bounded_exhaustive_S5.{key}.classification extension",
            classification.get("recursive_zero_without_Fp_tree_count"),
            counts["recursive_zero_without_ratcat_count"],
        )
        replay.exact(
            f"fixtures.bounded_exhaustive_S5.{key}.classification mismatch",
            classification.get(
                "all_external_base_liftable_Rec_vs_Rat_mismatch"
            ),
            0,
        )
    replay.exact(
        "fixtures.F13_boundary_and_base_lift duplicate",
        fixtures.get("F13_boundary_and_base_lift"),
        bounded.get("F13"),
    )


def check_fixtures(document: dict[str, Any], replay: Replay) -> None:
    fixtures = replay.mapping("fixtures", document.get("fixtures"))
    replay.exact(
        "fixtures keys",
        set(fixtures),
        {
            "F5_fixed_vs_reduced_infinity",
            "F5_F25_extension_only_nonlift",
            "bounded_exhaustive_S5",
            "F13_boundary_and_base_lift",
        },
    )
    check_f5_infinity(
        replay.mapping(
            "fixtures.F5_fixed_vs_reduced_infinity",
            fixtures.get("F5_fixed_vs_reduced_infinity"),
        ),
        replay,
    )
    check_f5_f25(
        replay.mapping(
            "fixtures.F5_F25_extension_only_nonlift",
            fixtures.get("F5_F25_extension_only_nonlift"),
        ),
        replay,
    )
    check_exhaustive(fixtures, replay)


def check_predicates(document: dict[str, Any], replay: Replay) -> None:
    predicates = replay.mapping(
        "predicate_boundaries", document.get("predicate_boundaries")
    )
    expected_strata = {
        "identity_or_infinity": "retain",
        "tangent_or_repeated_input": "retain",
        "rational_two_torsion": "retain",
        "duplicate_coordinates_or_roots": "retain",
        "extension_only_internal_roots": (
            "retain for GeoCat_kbar; reject for RatCat_Fp"
        ),
        "external_nonlift": (
            "valid projective input for Rec/Geo; reject Recover_Fp"
        ),
        "invalid_projective_pair_0_0": "exclude",
    }
    expected_contract = {
        "field_and_domain": (
            "for E/k nonsingular with char(k) not in {2,3,7}, all "
            "external pairs valid, and internals in P1(kbar)"
        ),
        "projection_map": "forget W2,...,W15 from a GeoCat_kbar witness",
        "forward": (
            "recorded algebraic argument: GeoCat_kbar should imply "
            "RecS17_k after embedding k into kbar by common-root vanishing "
            "at every fixed-degree resultant step; this producer replays "
            "only bounded C4=S5 instances and does not computationally or "
            "kernel prove generic C16 symbolic specialization"
        ),
        "reverse": (
            "unproved target: RecS17_k would imply GeoCat_kbar by "
            "repeated fixed-degree projective common-root reversal from "
            "C16 through C2, once specialization of every symbolic "
            "resultant at finite points and [1:0] is proved"
        ),
        "inverse_witness": (
            "target witness: one valid P1(kbar) common root at each "
            "reverse step; no universal witness construction is "
            "established by this producer"
        ),
        "forward_status": "algebraic_argument_recorded_bounded_replay",
        "reverse_status": "unproved_target",
        "equivalence": "not_established_universally",
        "claim_level": (
            "contract_frozen_algebraic_argument_recorded_bounded_replay_"
            "universal_forward_reverse_unproved"
        ),
        "missing_lemma": (
            "specialization compatibility of fixed-degree symbolic "
            "resultants, including the output point [1:0]"
        ),
    }
    expected_base = {
        "algebraic_arguments_recorded_not_generic_C16_proofs": [
            (
                "RatCat_Fp should imply RecS17_Fp by fixed-resultant "
                "common-root vanishing"
            ),
            (
                "Recover_Fp implies RatCat_Fp on its supplied valid tree "
                "by definition"
            ),
            (
                "TASK-017 records RatCat_Fp signed-point semantics on its "
                "stated supplied/liftable domain"
            ),
        ],
        "bounded_replay": [
            (
                "C4=S5 RatCat_Fp implies recursive-resultant zero for "
                "every tuple over F5, F11, and F13"
            ),
            (
                "all externally base-liftable recursive zeros have an Fp "
                "tree in those three bounded replays"
            ),
        ],
        "not_established_universally": [
            "RecS17_Fp implies GeoCat_kbar",
            "RecS17_Fp implies RatCat_Fp",
            "RecS17_Fp implies Recover_Fp",
        ],
        "combined_nonlift_boundary_fixture": (
            "fixtures.F5_F25_extension_only_nonlift; it is classified "
            "EXTERNAL_NONLIFT and is not an all-externals-liftable "
            "counterexample"
        ),
        "liftability_localization_target": (
            "after the universal reverse and specialization lemma are "
            "proved, all external E(Fp)-liftability is the target domain "
            "for RecS17_Fp iff RatCat_Fp; the current certificate "
            "establishes this only in bounded S5 replays"
        ),
        "bounded_exhaustive_check": (
            "the p=5,11,13 C4=S5 replays have respectively 432, 6442, "
            "and 766 base-liftable recursive zeros and zero Rec/Rat "
            "mismatches in all three fields"
        ),
    }
    replay.exact(
        "predicate_boundaries",
        predicates,
        {
            "RecS17_k": {
                "external_coordinates": "P1(k)^17",
                "internal_coordinates": "none in the predicate",
                "definition": (
                    "the frozen C16 determinant DAG evaluates to zero"
                ),
            },
            "GeoCat_kbar": {
                "external_coordinates": "P1(k)^17",
                "internal_coordinates": "W2,...,W15 in P1(kbar)",
                "definition": (
                    "all fifteen H vertices of the TASK-017 caterpillar vanish"
                ),
            },
            "RatCat_Fp": {
                "external_coordinates": "P1(Fp)^17",
                "internal_coordinates": "W2,...,W15 in P1(Fp)",
                "definition": "the same homogeneous caterpillar over Fp",
            },
            "Recover_Fp": {
                "inputs": (
                    "base-field leaf lifts, a full target point, supplied "
                    "valid projective internals, and exact backpointers"
                ),
                "definition": (
                    "exact point-DP recovery ending at R or -R; it is not "
                    "defined by resultant vanishing alone"
                ),
            },
            "algebraic_closure_projection_contract": expected_contract,
            "base_field_relations": expected_base,
            "strata": expected_strata,
        },
    )
    replay.exact(
        "predicate_boundaries keys",
        set(predicates),
        {
            "RecS17_k",
            "GeoCat_kbar",
            "RatCat_Fp",
            "Recover_Fp",
            "algebraic_closure_projection_contract",
            "base_field_relations",
            "strata",
        },
    )
    replay.exact(
        "predicate_boundaries.RecS17_k.internal_coordinates",
        replay.mapping(
            "predicate_boundaries.RecS17_k",
            predicates.get("RecS17_k"),
        ).get("internal_coordinates"),
        "none in the predicate",
    )
    replay.exact(
        "predicate_boundaries.RecS17_k.definition",
        replay.mapping(
            "predicate_boundaries.RecS17_k",
            predicates.get("RecS17_k"),
        ).get("definition"),
        "the frozen C16 determinant DAG evaluates to zero",
    )
    replay.contains(
        "predicate_boundaries.GeoCat_kbar.internal_coordinates",
        replay.mapping(
            "predicate_boundaries.GeoCat_kbar",
            predicates.get("GeoCat_kbar"),
        ).get("internal_coordinates"),
        "P1(kbar)",
    )
    replay.contains(
        "predicate_boundaries.RatCat_Fp.internal_coordinates",
        replay.mapping(
            "predicate_boundaries.RatCat_Fp",
            predicates.get("RatCat_Fp"),
        ).get("internal_coordinates"),
        "P1(Fp)",
    )
    replay.contains(
        "predicate_boundaries.Recover_Fp.definition",
        replay.mapping(
            "predicate_boundaries.Recover_Fp",
            predicates.get("Recover_Fp"),
        ).get("definition"),
        "not defined by resultant vanishing alone",
    )
    contract = replay.mapping(
        "predicate_boundaries.algebraic_closure_projection_contract",
        predicates.get("algebraic_closure_projection_contract"),
    )
    replay.exact(
        "projective contract forward_status",
        contract.get("forward_status"),
        "algebraic_argument_recorded_bounded_replay",
    )
    replay.exact(
        "projective contract reverse_status",
        contract.get("reverse_status"),
        "unproved_target",
    )
    replay.exact(
        "projective contract equivalence",
        contract.get("equivalence"),
        "not_established_universally",
    )
    replay.exact(
        "projective contract claim_level",
        contract.get("claim_level"),
        (
            "contract_frozen_algebraic_argument_recorded_bounded_replay_"
            "universal_forward_reverse_unproved"
        ),
    )
    replay.contains(
        "projective contract forward",
        contract.get("forward"),
        "does not computationally or kernel prove generic C16",
    )
    replay.contains("projective contract reverse", contract.get("reverse"), "unproved")
    replay.contains(
        "projective contract missing_lemma",
        contract.get("missing_lemma"),
        "[1:0]",
    )
    for forbidden in ("exact_set_theoretic", "RecS17_k iff GeoCat_kbar"):
        if forbidden in str(contract):
            replay.fail(
                "projective contract overclaims the unproved universal reverse"
            )

    base = replay.mapping(
        "predicate_boundaries.base_field_relations",
        predicates.get("base_field_relations"),
    )
    replay.exact(
        "predicate_boundaries.base_field_relations keys",
        set(base),
        {
            "algebraic_arguments_recorded_not_generic_C16_proofs",
            "bounded_replay",
            "not_established_universally",
            "combined_nonlift_boundary_fixture",
            "liftability_localization_target",
            "bounded_exhaustive_check",
        },
    )
    not_established = replay.sequence(
        "predicate_boundaries.base_field_relations.not_established_universally",
        base.get("not_established_universally"),
    )
    expected_not_established = [
        "RecS17_Fp implies GeoCat_kbar",
        "RecS17_Fp implies RatCat_Fp",
        "RecS17_Fp implies Recover_Fp",
    ]
    replay.exact(
        "predicate_boundaries.base_field_relations.not_established_universally",
        not_established,
        expected_not_established,
    )
    recorded_arguments = replay.sequence(
        (
            "predicate_boundaries.base_field_relations."
            "algebraic_arguments_recorded_not_generic_C16_proofs"
        ),
        base.get("algebraic_arguments_recorded_not_generic_C16_proofs"),
    )
    replay.exact(
        (
            "predicate_boundaries.base_field_relations."
            "algebraic_arguments_recorded_not_generic_C16_proofs"
        ),
        recorded_arguments,
        [
            (
                "RatCat_Fp should imply RecS17_Fp by fixed-resultant "
                "common-root vanishing"
            ),
            (
                "Recover_Fp implies RatCat_Fp on its supplied valid tree "
                "by definition"
            ),
            (
                "TASK-017 records RatCat_Fp signed-point semantics "
                "on its stated supplied/liftable domain"
            ),
        ],
    )
    replay.exact(
        "predicate_boundaries.base_field_relations.bounded_replay",
        replay.sequence(
            "predicate_boundaries.base_field_relations.bounded_replay",
            base.get("bounded_replay"),
        ),
        [
            (
                "C4=S5 RatCat_Fp implies recursive-resultant zero for "
                "every tuple over F5, F11, and F13"
            ),
            (
                "all externally base-liftable recursive zeros have an Fp "
                "tree in those three bounded replays"
            ),
        ],
    )
    replay.contains(
        "predicate_boundaries.base_field_relations.combined_nonlift_boundary_fixture",
        base.get("combined_nonlift_boundary_fixture"),
        "EXTERNAL_NONLIFT",
    )
    replay.contains(
        "predicate_boundaries.base_field_relations.liftability_localization_target",
        base.get("liftability_localization_target"),
        "bounded S5 replays",
    )

    strata = replay.mapping(
        "predicate_boundaries.strata", predicates.get("strata")
    )
    replay.exact(
        "predicate_boundaries.strata",
        strata,
        expected_strata,
    )


def check_scope_and_terminal(
    document: dict[str, Any], replay: Replay
) -> None:
    replay.exact("artifact_id", document.get("artifact_id"), ARTIFACT_ID)
    replay.exact("schema_version", document.get("schema_version"), "1.0")
    replay.exact(
        "kind",
        document.get("kind"),
        (
            "deterministic_nonexperimental_recursive_projective_"
            "definition_and_boundary_certificate"
        ),
    )
    scope = replay.mapping("scope", document.get("scope"))
    replay.exact("scope.task", scope.get("task"), "TASK-018")
    replay.exact(
        "scope.cell", scope.get("cell"), "CELL-M-PKC-SMOOTH-M16"
    )
    replay.exact(
        "scope.barrier",
        scope.get("barrier"),
        "B-PKC-M16-COMPLETE-COST-BRIDGE",
    )
    replay.exact(
        "scope.cost_quantity",
        scope.get("cost_quantity"),
        "CQ-SEMAEV-S17-SYSTEM-COST",
    )
    expected_scope = {
        "task": "TASK-018",
        "cell": "CELL-M-PKC-SMOOTH-M16",
        "barrier": "B-PKC-M16-COMPLETE-COST-BRIDGE",
        "cost_quantity": "CQ-SEMAEV-S17-SYSTEM-COST",
        "included": [
            "fixed-degree projective recursion C2 through C16",
            "degree and Sylvester determinant conventions",
            (
                "recorded algebraic GeoCat-to-RecS17 argument, bounded "
                "C4=S5 replay, and universal forward/reverse proof "
                "obligations"
            ),
            "RatCat and Recover boundary separation",
            (
                "F5/F25 explicit fixtures and exhaustive F5/F11/F13 "
                "C4=S5 replays"
            ),
        ],
        "excluded": [
            "expanded or evaluated S17",
            "materialized M16 polynomial system",
            "scheme equality, radicality, or multiplicity preservation",
            "Sage, msolve, F4, Groebner, or any solver run",
            "exact-target relation search or discrete-log computation",
            "degree of regularity, fill-in, rank, yield, memory, or cost",
            "experiment authorization, hypothesis retention, or promotion",
        ],
    }
    replay.exact("scope", scope, expected_scope)
    exclusions = replay.sequence("scope.excluded", scope.get("excluded"))
    replay.exact(
        "scope.included",
        replay.sequence("scope.included", scope.get("included")),
        [
            "fixed-degree projective recursion C2 through C16",
            "degree and Sylvester determinant conventions",
            (
                "recorded algebraic GeoCat-to-RecS17 argument, bounded "
                "C4=S5 replay, and universal forward/reverse proof "
                "obligations"
            ),
            "RatCat and Recover boundary separation",
            (
                "F5/F25 explicit fixtures and exhaustive F5/F11/F13 "
                "C4=S5 replays"
            ),
        ],
    )
    exclusion_text = " ".join(str(value) for value in exclusions)
    for token in (
        "expanded or evaluated S17",
        "materialized M16 polynomial system",
        "scheme equality",
        "solver run",
        "rank",
        "cost",
        "experiment authorization",
    ):
        replay.contains("scope.excluded", exclusion_text, token)

    terminal = replay.mapping(
        "terminal_disposition", document.get("terminal_disposition")
    )
    expected = {
        "scientific_disposition": "scoped_blocker",
        "retention_disposition": "zero_retention_success",
        "assurance": "certificate_replayed",
        "source_independence": "not_established",
        "calibration": "excluded_nonexperimental",
        "cell_status": "open_non_executable",
        "barrier_effect": "narrowed_open",
        "cost_quantity_status": "partial",
        "solving_cost_status": "unpriced",
        "rank_status": "unpriced",
        "yield_status": "unpriced",
        "authorization": "none",
        "experiment_permission": "none",
        "route_effect": "none",
        "hypothesis_effect": "none",
    }
    for field, value in expected.items():
        replay.exact(f"terminal_disposition.{field}", terminal.get(field), value)
    expected_terminal = {
        "scientific_disposition": "scoped_blocker",
        "completed_scope": (
            "one fixed recursive projective S17 definition, complete "
            "degree and determinant conventions, a recorded algebraic "
            "GeoCat-to-Rec argument, and bounded C4=S5 projective, "
            "nonlift, and no-Fp-tree replays"
        ),
        "remaining_blocker": (
            "neither the generic C16 forward specialization nor the "
            "universal reverse RecS17-to-GeoCat induction is "
            "computationally or kernel proved; symbolic fixed-resultant "
            "specialization, especially at [1:0], is missing, so "
            "Rec-to-Rat/Recover and solving cost remain unestablished"
        ),
        "next_mathematical_step": (
            "prove the fixed-degree P1 resultant common-root lemma and "
            "the symbolic-resultant specialization law at finite points "
            "and [1:0], kernel-check the generic forward implication, "
            "then run the reverse C16-to-C2 induction"
        ),
        "retention_disposition": "zero_retention_success",
        "assurance": "certificate_replayed",
        "source_independence": "not_established",
        "calibration": "excluded_nonexperimental",
        "cell_status": "open_non_executable",
        "barrier_effect": "narrowed_open",
        "cost_quantity_status": "partial",
        "solving_cost_status": "unpriced",
        "rank_status": "unpriced",
        "yield_status": "unpriced",
        "authorization": "none",
        "experiment_permission": "none",
        "route_effect": "none",
        "hypothesis_effect": "none",
    }
    replay.exact(
        "terminal_disposition", terminal, expected_terminal
    )
    for token in (
        "neither the generic C16 forward specialization",
        "universal reverse",
        "kernel proved",
        "[1:0]",
        "solving cost",
    ):
        replay.contains(
            "terminal_disposition.remaining_blocker",
            terminal.get("remaining_blocker"),
            token,
        )
    replay.contains(
        "terminal_disposition.next_mathematical_step",
        terminal.get("next_mathematical_step"),
        "fixed-degree P1 resultant",
    )
    replay.contains(
        "terminal_disposition.next_mathematical_step",
        terminal.get("next_mathematical_step"),
        "kernel-check the generic forward implication",
    )

    unresolved = replay.sequence(
        "unresolved_fields", document.get("unresolved_fields")
    )
    replay.exact(
        "unresolved_fields",
        unresolved,
        [
            "kernel-checked fixed-degree projective resultant theorem",
            "symbolic-resultant specialization at finite points and [1:0]",
            "generic C16 GeoCat-to-RecS17 forward kernel proof",
            "universal reverse RecS17-to-GeoCat induction",
            "unconditional base-field rational-root projection",
            (
                "recovery without explicit lift and supplied-coordinate "
                "hypotheses"
            ),
            "scheme equality, radicality, or multiplicity preservation",
            (
                "degree of regularity, fill-in, rank, yield, memory, "
                "and total work"
            ),
        ],
    )
    unresolved_text = " ".join(str(value) for value in unresolved)
    for token in (
        "kernel-checked fixed-degree projective resultant theorem",
        "specialization at finite points and [1:0]",
        "universal reverse RecS17-to-GeoCat induction",
        "rank",
        "total work",
    ):
        replay.contains("unresolved_fields", unresolved_text, token)

    producer = replay.mapping(
        "producer_checks", document.get("producer_checks")
    )
    replay.exact(
        "producer_checks",
        producer,
        {
            "dependency_digests_bound": True,
            "all_source_paths_exist": True,
            "schedule_rows_replayed": 15,
            "C16_multidegree_checked": 32_768,
            "C16_expanded": False,
            "C16_evaluated": False,
            "highest_materialized_recursive_form": (
                "C3=S4 in small fixtures"
            ),
            "highest_evaluated_recursive_form": (
                "C4=S5 in small fixtures"
            ),
            "F5_fixed_resultant": 0,
            "F5_reduced_affine_resultant": 1,
            "F25_common_root_count": 2,
            "bounded_S5_fields_replayed": [5, 11, 13],
            "bounded_S5_total_tuples_replayed": 794_432,
            "bounded_C4_S5_forward_replayed": True,
            "generic_C16_forward_computationally_replayed": False,
            "generic_C16_forward_kernel_checked": False,
            "F13_tuples_replayed": 537_824,
            "F13_recursive_zero_without_Fp_tree_count": 6_360,
            "F13_base_lift_mismatch_count": 0,
            "S17_materialized": False,
            "solver_executed": False,
            "experiment_authorized": False,
        },
    )
    replay.exact("producer_checks.C16_expanded", producer.get("C16_expanded"), False)
    replay.exact("producer_checks.C16_evaluated", producer.get("C16_evaluated"), False)
    replay.exact(
        "producer_checks.S17_materialized",
        producer.get("S17_materialized"),
        False,
    )
    replay.exact(
        "producer_checks.solver_executed",
        producer.get("solver_executed"),
        False,
    )
    replay.exact(
        "producer_checks.experiment_authorized",
        producer.get("experiment_authorized"),
        False,
    )
    replay.exact(
        "producer_checks.schedule_rows_replayed",
        producer.get("schedule_rows_replayed"),
        15,
    )
    replay.exact(
        "producer_checks.C16_multidegree_checked",
        producer.get("C16_multidegree_checked"),
        32_768,
    )


def validate_document(
    document: dict[str, Any],
    artifact_bytes: bytes,
    hash_path: Path,
) -> list[str]:
    replay = Replay()
    if artifact_bytes != canonical_bytes(document):
        replay.fail("artifact.json is not canonical JSON")
    check_hash(artifact_bytes, hash_path, replay)
    expected_top_level = {
        "artifact_id",
        "schema_version",
        "kind",
        "scope",
        "depends_on",
        "frozen_definition",
        "degree_schedule",
        "coefficient_and_sylvester_convention",
        "fixtures",
        "predicate_boundaries",
        "terminal_disposition",
        "unresolved_fields",
        "producer_checks",
    }
    replay.exact("top-level keys", set(document), expected_top_level)
    check_scope_and_terminal(document, replay)
    check_dependencies(document, replay)
    check_definition(document, replay)
    check_schedule(document, replay)
    check_convention(document, replay)
    check_fixtures(document, replay)
    check_predicates(document, replay)
    return replay.failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, default=ARTIFACT_PATH)
    parser.add_argument("--hash-file", type=Path, default=HASH_PATH)
    args = parser.parse_args()
    try:
        artifact_bytes = args.artifact.read_bytes()
        document = json.loads(artifact_bytes)
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError) as error:
        print(f"ERROR: artifact unreadable: {error}", file=sys.stderr)
        return 1
    if not isinstance(document, dict):
        print("ERROR: artifact root must be an object", file=sys.stderr)
        return 1
    try:
        failures = validate_document(document, artifact_bytes, args.hash_file)
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        print(f"ERROR: independent replay failed: {error}", file=sys.stderr)
        return 1
    if failures:
        print("TASK-018 projective-S17 validation FAILED:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("TASK-018 projective-S17 validation PASSED")
    print("  independently replayed H and C2..C16 degree schedule")
    print("  independently replayed fixed-degree Sylvester boundaries")
    print("  exhaustive S5 replay: F5=7776, F11=248832, F13=537824")
    print("  universal reverse remains an unproved target; no execution authorized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
