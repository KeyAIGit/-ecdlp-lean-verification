#!/usr/bin/env python3
"""Frozen toy-only screen for DIRECT-GLV-CARRY-DESCENT-010.

Tests exact decoders chi(y(Q) R(x(Q)^3)) = g(Q) on fifteen frozen toy
subgroups.  No external point, key, curve, or production-sized target is
accepted.  Exhausted classes: split squarefree R with <=4 linear factors; and
all rational square classes with total numerator-plus-denominator degree <=2.
"""
from __future__ import annotations

import argparse, json, random, subprocess, sys
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from mixed_weight_pencil_screen import (
    FROZEN_CASES, orbit, primitive_cube_root, quadratic_character,
)

FACTOR_LIMIT = 4
BASIS_TRIALS = 20
ORDER_FLOOR = 271


def signs_to_bits(signs: list[int]) -> int:
    out = 0
    for i, sign in enumerate(signs):
        if sign not in (-1, 1):
            raise AssertionError("non-binary sign")
        if sign < 0:
            out |= 1 << i
    return out


def quotient_data(p: int, n: int, generator: tuple[int, int]) -> dict:
    if p % 4 != 3:
        raise AssertionError("screen assumes p=3 mod 4")
    points = orbit(generator, n, p)
    beta = primitive_cube_root(p)
    scalar_of = {point: k for k, point in enumerate(points)}
    lam = scalar_of[(beta * generator[0] % p, generator[1])]
    lam2 = lam * lam % n
    if (1 + lam + lam2) % n:
        raise AssertionError("invalid GLV eigenvalue")

    visited, z_values, targets = set(), [], []
    for k in range(1, n):
        if k in visited:
            continue
        positive = {k, lam * k % n, lam2 * k % n}
        orbit6 = positive | {n - member for member in positive}
        if len(orbit6) != 6:
            raise AssertionError("non-free C6 orbit")
        visited.update(orbit6)
        representative = min(positive)
        point = points[representative]
        if point is None:
            raise AssertionError("unexpected infinity")
        x, y = point
        z = pow(x, 3, p)
        total = representative + lam * representative % n + lam2 * representative % n
        if total not in (n, 2 * n):
            raise AssertionError("invalid carry")
        g = 1 if total == 2 * n else -1
        target = g * quadratic_character(y, p)

        for member in orbit6:
            member_point = points[member]
            if member_point is None:
                raise AssertionError("unexpected infinity in C6 orbit")
            xm, ym = member_point
            member_total = member + lam * member % n + lam2 * member % n
            gm = 1 if member_total == 2 * n else -1
            if pow(xm, 3, p) != z or gm * quadratic_character(ym, p) != target:
                raise AssertionError("quotient descent failed")
        z_values.append(z)
        targets.append(target)

    expected = (n - 1) // 6
    if len(z_values) != expected or len(set(z_values)) != expected:
        raise AssertionError("z=x^3 did not separate quotient orbits")
    return {"beta": beta, "lam": lam, "z": z_values, "target": targets}


def factor_family(p: int, z_values: list[int], targets: list[int]):
    target = signs_to_bits(targets)
    forbidden = set(z_values)
    vectors, labels = [], []
    for c in range(p):
        if c in forbidden:
            continue
        vectors.append(signs_to_bits([quadratic_character(z - c, p) for z in z_values]))
        labels.append(c)
    return target, vectors, labels


def verify_split(p: int, z_values: list[int], targets: list[int], answer: dict) -> None:
    for z, target in zip(z_values, targets):
        sign = -1 if answer["constant_nonsquare"] else 1
        for c in answer["coefficients"]:
            sign *= quadratic_character(z - c, p)
        if sign != target:
            raise AssertionError("split solution replay failed")


def search_le_three(target: int, vectors: list[int], labels: list[int], m: int):
    ones = (1 << m) - 1
    lookup = {}
    for i, vector in enumerate(vectors):
        lookup.setdefault(vector, i)
    for flip, wanted in ((False, target), (True, target ^ ones)):
        if wanted == 0:
            return {"degree": 0, "constant_nonsquare": flip, "coefficients": []}
        if wanted in lookup:
            return {"degree": 1, "constant_nonsquare": flip,
                    "coefficients": [labels[lookup[wanted]]]}
        for i, vector in enumerate(vectors):
            j = lookup.get(wanted ^ vector)
            if j is not None and j != i:
                return {"degree": 2, "constant_nonsquare": flip,
                        "coefficients": sorted([labels[i], labels[j]])}
        for i, left in enumerate(vectors):
            for j in range(i + 1, len(vectors)):
                k = lookup.get(wanted ^ left ^ vectors[j])
                if k is not None and k not in (i, j):
                    return {"degree": 3, "constant_nonsquare": flip,
                            "coefficients": sorted([labels[i], labels[j], labels[k]])}
    return None


def fingerprint(vector: int, masks: list[int]) -> int:
    out = 0
    while vector:
        low = vector & -vector
        out ^= masks[low.bit_length() - 1]
        vector ^= low
    return out


def search_four(target: int, vectors: list[int], labels: list[int], m: int):
    """Exact MITM: projected absence is exact; projected hits get full replay."""
    ones = (1 << m) - 1
    rng = random.Random(0xD1EEC7A5 + 65537 * m + len(vectors))
    masks1 = [rng.getrandbits(64) for _ in range(m)]
    masks2 = [rng.getrandbits(64) for _ in range(m)]
    fp1 = np.array([fingerprint(v, masks1) for v in vectors], dtype=np.uint64)
    fp2 = np.array([fingerprint(v, masks2) for v in vectors], dtype=np.uint64)
    left, right = np.triu_indices(len(vectors), k=1)
    left, right = left.astype(np.int32), right.astype(np.int32)
    pair1, pair2 = fp1[left] ^ fp1[right], fp2[left] ^ fp2[right]
    order = np.argsort(pair1, kind="quicksort")
    sorted1 = pair1[order]

    for flip, wanted in ((False, target), (True, target ^ ones)):
        target1 = np.uint64(fingerprint(wanted, masks1))
        target2 = np.uint64(fingerprint(wanted, masks2))
        complements = pair1 ^ target1
        positions = np.searchsorted(sorted1, complements, side="left")
        valid_indices = np.nonzero(positions < len(sorted1))[0]
        if valid_indices.size:
            pos = positions[valid_indices]
            valid_indices = valid_indices[sorted1[pos] == complements[valid_indices]]
        for first_pair in valid_indices.tolist():
            key = np.uint64(complements[first_pair])
            lo = int(np.searchsorted(sorted1, key, side="left"))
            hi = int(np.searchsorted(sorted1, key, side="right"))
            need2 = np.uint64(target2 ^ pair2[first_pair])
            candidates = order[lo:hi]
            candidates = candidates[pair2[candidates] == need2]
            i, j = int(left[first_pair]), int(right[first_pair])
            first_full = vectors[i] ^ vectors[j]
            for second_pair_raw in candidates.tolist():
                second_pair = int(second_pair_raw)
                u, v = int(left[second_pair]), int(right[second_pair])
                if len({i, j, u, v}) != 4:
                    continue
                if first_full ^ vectors[u] ^ vectors[v] == wanted:
                    return {"degree": 4, "constant_nonsquare": flip,
                            "coefficients": sorted([labels[i], labels[j], labels[u], labels[v]])}
    return None


def sparse_solution(p: int, z_values: list[int], targets: list[int], target: int,
                    vectors: list[int], labels: list[int]):
    answer = search_le_three(target, vectors, labels, len(z_values))
    if answer is None:
        answer = search_four(target, vectors, labels, len(z_values))
    if answer is not None:
        verify_split(p, z_values, targets, answer)
    return answer


def rotate_right(mask: int, shift: int, width: int) -> int:
    shift %= width
    if not shift:
        return mask
    low = mask & ((1 << shift) - 1)
    return (mask >> shift) | (low << (width - shift))


def verify_quadratic(p: int, z_values: list[int], targets: list[int], answer: dict) -> None:
    for z, target in zip(z_values, targets):
        value = (z * z + answer["a"] * z + answer["b"]) % p
        if answer["leading_character"] * quadratic_character(value, p) != target:
            raise AssertionError("quadratic solution replay failed")


def quadratic_solution(p: int, z_values: list[int], targets: list[int]):
    all_bits = (1 << p) - 1
    residue = nonresidue = 0
    for value in range(p):
        sign = quadratic_character(value, p)
        if sign == 1:
            residue |= 1 << value
        elif sign == -1:
            nonresidue |= 1 << value
    for a in range(p):
        square = nonsquare = all_bits
        for z, target in zip(z_values, targets):
            offset = (z * z + a * z) % p
            square &= rotate_right(residue if target == 1 else nonresidue, offset, p)
            nonsquare &= rotate_right(nonresidue if target == 1 else residue, offset, p)
            if not square and not nonsquare:
                break
        for lead, candidates in ((1, square), (-1, nonsquare)):
            if candidates:
                answer = {"leading_character": lead, "a": a,
                          "b": (candidates & -candidates).bit_length() - 1}
                verify_quadratic(p, z_values, targets, answer)
                return answer
    return None


def solve_columns(vectors: list[int], target: int, indices=None):
    if indices is None:
        indices = range(len(vectors))
    basis = {}
    for column in indices:
        vector, combination = vectors[column], 1 << column
        while vector:
            pivot = vector.bit_length() - 1
            if pivot in basis:
                base_vector, base_combination = basis[pivot]
                vector ^= base_vector
                combination ^= base_combination
            else:
                basis[pivot] = (vector, combination)
                break
    vector, combination = target, 0
    while vector:
        pivot = vector.bit_length() - 1
        if pivot not in basis:
            return len(basis), None
        base_vector, base_combination = basis[pivot]
        vector ^= base_vector
        combination ^= base_combination
    return len(basis), combination


def support_bounds(vectors: list[int], target: int, m: int, seed: int):
    ones = (1 << m) - 1
    rank, direct = solve_columns(vectors, target)
    _, flipped = solve_columns(vectors, target ^ ones)
    solutions = [x.bit_count() for x in (direct, flipped) if x is not None]
    deterministic = min(solutions) if solutions else None
    randomized = deterministic
    indices, rng = list(range(len(vectors))), random.Random(seed)
    for _ in range(BASIS_TRIALS):
        rng.shuffle(indices)
        _, direct = solve_columns(vectors, target, indices)
        _, flipped = solve_columns(vectors, target ^ ones, indices)
        trials = [x.bit_count() for x in (direct, flipped) if x is not None]
        if trials:
            randomized = min(randomized, min(trials)) if randomized is not None else min(trials)
    return rank, deterministic, randomized


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    beta: int
    lam: int
    quotient_orbits: int
    target_positive: int
    target_negative: int
    available_linear_factors: int
    linear_factor_rank: int
    rank_is_full: bool
    deterministic_support_upper_bound: int | None
    randomized_support_upper_bound: int | None
    split_degree_at_most_four_solution: dict | None
    quadratic_square_class_solution: dict | None


def run_case(p: int, n: int, generator: tuple[int, int]) -> CaseResult:
    data = quotient_data(p, n, generator)
    z_values, targets = data["z"], data["target"]
    target, vectors, labels = factor_family(p, z_values, targets)
    split = sparse_solution(p, z_values, targets, target, vectors, labels)
    quadratic = quadratic_solution(p, z_values, targets)
    rank, deterministic, randomized = support_bounds(
        vectors, target, len(z_values), 20260812 + p + n
    )
    return CaseResult(
        p, n, generator, data["beta"], data["lam"], len(z_values),
        sum(x == 1 for x in targets), sum(x == -1 for x in targets),
        len(vectors), rank, rank == len(z_values), deterministic, randomized,
        split, quadratic,
    )


def build_payload(cases: list[CaseResult]) -> dict:
    nontrivial = [case for case in cases if case.order >= ORDER_FLOOR]
    return {
        "package": "DIRECT-GLV-CARRY-DESCENT-010",
        "scope": "fifteen frozen j=0 prime-order toy subgroups; no external or production target",
        "target": "chi(y(Q)*R(x(Q)^3)) = canonical GLV carry g(Q)",
        "exact_classes": [
            "all split squarefree R with at most four distinct F_p-linear factors and either constant square class",
            "all rational square classes with total numerator-plus-denominator degree at most two, represented by u*(z^2+a*z+b)",
        ],
        "protocol": {
            "sparse_factor_limit": FACTOR_LIMIT,
            "random_basis_trials": BASIS_TRIALS,
            "nontrivial_order_floor": ORDER_FLOOR,
            "quotient_coordinate": "z=x^3=y^2-7",
            "residual_target": "h=g*chi(y)",
        },
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "nontrivial_cases": len(nontrivial),
            "all_linear_factor_ranks_full": all(case.rank_is_full for case in cases),
            "split_degree_at_most_four_exact_decoders": sum(case.split_degree_at_most_four_solution is not None for case in cases),
            "split_degree_at_most_four_exact_decoders_order_at_least_271": sum(case.split_degree_at_most_four_solution is not None for case in nontrivial),
            "quadratic_square_class_exact_decoders": sum(case.quadratic_square_class_solution is not None for case in cases),
            "quadratic_square_class_exact_decoders_order_at_least_271": sum(case.quadratic_square_class_solution is not None for case in nontrivial),
            "largest_order": max(case.order for case in cases),
            "largest_quotient_orbits": max(case.quotient_orbits for case in cases),
            "largest_randomized_support_upper_bound": max(case.randomized_support_upper_bound or 0 for case in cases),
        },
        "conclusion": (
            "Small exact direct descents occur only on the three tiny quotients.  "
            "Across every frozen subgroup of order at least 271, there is no exact "
            "split decoder with at most four linear factors and no exact rational "
            "square class of total degree at most two.  The complete linear-factor "
            "family has full F_2 rank, so high-support finite interpolation remains "
            "possible; the recorded constructions use tens to hundreds of factors "
            "rather than a small formula."
        ),
        "claim_boundary": [
            "This is exact finite exhaustion only for the two declared low-complexity classes.",
            "It does not exclude irreducible factors of degree at least three, high-degree sparse polynomials, or general small arithmetic circuits.",
            "Support values from Gaussian bases are upper bounds, not minimum-degree certificates.",
            "The experiment is bounded toy evidence, not an asymptotic lower bound.",
            "No secp256k1 unknown point, private key, wallet, or external target is accepted or evaluated.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path,
                        default=Path(__file__).with_name("direct_glv_carry_descent_results.json"))
    parser.add_argument("--case-index", type=int, default=None, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.case_index is not None:
        if not 0 <= args.case_index < len(FROZEN_CASES):
            raise SystemExit("invalid frozen case index")
        print(json.dumps(asdict(run_case(*FROZEN_CASES[args.case_index])), sort_keys=True))
        return

    cases = []
    script = Path(__file__).resolve()
    for index in range(len(FROZEN_CASES)):
        completed = subprocess.run(
            [sys.executable, str(script), "--case-index", str(index)],
            check=True, capture_output=True, text=True,
        )
        cases.append(CaseResult(**json.loads(completed.stdout)))
    rendered = json.dumps(build_payload(cases), indent=2, sort_keys=True)
    args.out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
