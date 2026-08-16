#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from uorc056_c39_half_miller import TOYS, half_sequence
from uorc056_c39_orbit import add, sub, scale, mul, roots, trim


def degree(poly):
    return len(trim(poly[:])) - 1


def poly_pow(poly, exponent):
    one = poly[0] ** 0
    out = [one]
    base = poly[:]
    value = exponent
    while value:
        if value & 1:
            out = mul(out, base)
        base = mul(base, base)
        value >>= 1
    return trim(out)


def proper_divisors(value):
    return [d for d in range(2, value) if value % d == 0]


def monic_normalize(poly):
    return scale(poly, poly[-1].inv())


def decompose_candidate(poly, right_degree, field_one):
    f = monic_normalize(poly)
    n = degree(f)
    if n % right_degree:
        return None
    left_degree = n // right_degree
    if left_degree < 2 or left_degree % field_one.p == 0:
        return None
    zero = field_one * 0
    h = [zero for _ in range(right_degree + 1)]
    h[right_degree] = field_one
    inv_left = field_one * pow(left_degree, -1, field_one.p)
    for offset in range(1, right_degree):
        current_power = poly_pow(h, left_degree)
        index = n - offset
        current = current_power[index] if index < len(current_power) else zero
        target = f[index] if index < len(f) else zero
        h[right_degree - offset] = (target - current) * inv_left
    h[0] = zero

    powers = [[field_one]]
    for _ in range(left_degree):
        powers.append(mul(powers[-1], h))
    remainder = f[:]
    outer = [zero for _ in range(left_degree + 1)]
    for power in range(left_degree, -1, -1):
        remainder = trim(remainder)
        if len(remainder) == 1 and not remainder[0]:
            break
        expected = power * right_degree
        actual = degree(remainder)
        if actual > expected:
            return None
        if actual == expected:
            coefficient = remainder[-1]
            outer[power] = coefficient
            remainder = sub(remainder, scale(powers[power], coefficient))
    remainder = trim(remainder)
    if not (len(remainder) == 1 and not remainder[0]):
        return None
    recomposed = [zero]
    for coefficient in reversed(outer):
        recomposed = add(mul(recomposed, h), [coefficient])
    if monic_normalize(recomposed) != f:
        return None
    return {
        'left_degree': left_degree,
        'right_degree': right_degree,
        'right_component_nonzero_coefficients': sum(bool(x) for x in h),
        'outer_nonzero_coefficients': sum(bool(x) for x in outer),
    }


def berlekamp_massey(sequence):
    if not sequence:
        return 0
    one = sequence[0] ** 0
    zero = one * 0
    C = [one]
    B = [one]
    L = 0
    shift = 1
    discrepancy_scale = one
    for index in range(len(sequence)):
        discrepancy = sequence[index]
        for j in range(1, L + 1):
            if j < len(C):
                discrepancy = discrepancy + C[j] * sequence[index - j]
        if not discrepancy:
            shift += 1
            continue
        old = C[:]
        factor = discrepancy / discrepancy_scale
        need = len(B) + shift
        if len(C) < need:
            C.extend([zero] * (need - len(C)))
        for j, value in enumerate(B):
            C[j + shift] = C[j + shift] - factor * value
        if 2 * L <= index:
            L = index + 1 - L
            B = old
            discrepancy_scale = discrepancy
            shift = 1
        else:
            shift += 1
    return L


class IncrementalColumnRank:
    def __init__(self):
        self.basis = {}
        self.columns = 0

    @property
    def rank(self):
        return len(self.basis)

    def add(self, column):
        vector = column[:]
        self.columns += 1
        for pivot in sorted(self.basis, reverse=True):
            if vector[pivot]:
                factor = vector[pivot]
                basis_vector = self.basis[pivot]
                vector = [left - factor * right for left, right in zip(vector, basis_vector)]
        pivot = next((index for index in range(len(vector) - 1, -1, -1) if vector[index]), None)
        if pivot is None:
            return False
        inverse = vector[pivot].inv()
        vector = [value * inverse for value in vector]
        self.basis[pivot] = vector
        return True


def first_bivariate_relation(xs, ys, max_degree=64):
    row_count = len(xs)
    one = xs[0] ** 0
    x_powers = [[one] for _ in xs]
    y_powers = [[one] for _ in ys]
    basis = IncrementalColumnRank()
    for total_degree in range(max_degree + 1):
        if total_degree:
            for index, value in enumerate(xs):
                x_powers[index].append(x_powers[index][-1] * value)
            for index, value in enumerate(ys):
                y_powers[index].append(y_powers[index][-1] * value)
        for x_degree in range(total_degree + 1):
            y_degree = total_degree - x_degree
            column = [
                x_powers[row][x_degree] * y_powers[row][y_degree]
                for row in range(row_count)
            ]
            basis.add(column)
        if basis.rank < basis.columns:
            return {
                'degree': total_degree,
                'columns': basis.columns,
                'rank': basis.rank,
                'forced_by_dimension': basis.columns > row_count,
            }
    return None


def first_rational_transition(xs, ys, max_degree=128):
    row_count = len(xs)
    one = xs[0] ** 0
    powers = [one for _ in xs]
    basis = IncrementalColumnRank()
    for degree_bound in range(max_degree + 1):
        if degree_bound:
            powers = [power * x for power, x in zip(powers, xs)]
        basis.add(powers)
        basis.add([-y * power for y, power in zip(ys, powers)])
        if basis.rank < basis.columns:
            return {
                'degree': degree_bound,
                'columns': basis.columns,
                'rank': basis.rank,
                'forced_by_dimension': basis.columns > row_count,
            }
    return None


def curve_probe(row):
    E, n, G, S, beta, lam, h, values = half_sequence(row)
    one = E.c(1)
    even_values = [values[k] for k in range(2, n, 2)]
    odd_values = [values[k] for k in range(1, n, 2)]
    p_even = roots(even_values, one)
    p_odd = roots(odd_values, one)
    polynomials = {
        'P_even': p_even,
        'P_odd': p_odd,
        'Sigma': add(p_even, p_odd),
        'Delta': sub(p_odd, p_even),
        'Pi': mul(p_even, p_odd),
    }
    decomposition = {}
    recurrence = {}
    for name, poly in polynomials.items():
        decomposition[name] = [
            candidate
            for divisor in proper_divisors(degree(poly))
            if (candidate := decompose_candidate(poly, divisor, one)) is not None
        ]
        recurrence[name] = {
            'ascending': berlekamp_massey(poly),
            'descending': berlekamp_massey(list(reversed(poly))),
            'coefficient_count': len(poly),
        }

    scalars = list(range(1, n))
    state = [values[k] for k in scalars]
    maps = {
        'successor': [values[(k + 1) % n] for k in scalars],
        'doubling': [values[(2 * k) % n] for k in scalars],
        'negation': [values[(-k) % n] for k in scalars],
        'glv_lambda': [values[(lam * k) % n] for k in scalars],
    }
    transitions = {}
    for name, target in maps.items():
        transitions[name] = {
            'first_bivariate_relation': first_bivariate_relation(state, target),
            'first_rational_transition': first_rational_transition(state, target),
        }

    return {
        'p': E.p,
        'n': n,
        'm': (n - 1) // 2,
        'functional_decompositions': decomposition,
        'coefficient_recurrence': recurrence,
        'state_transitions': transitions,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    payload = {
        'profile_id': 'UORC-056-INCOMPLETE-ORIENTED-PRODUCT-C41-PROBE',
        'curves': [curve_probe(row) for row in TOYS],
    }
    if args.out:
        args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    print('UORC056_INCOMPLETE_ORIENTED_PRODUCT_C41_PROBE_OK')
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
