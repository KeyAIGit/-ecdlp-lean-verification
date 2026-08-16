#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

from uorc056_c39_half_miller import TOYS, half_sequence, legendre, shifted
from uorc056_c39_orbit import roots


def frobenius_point(point):
    if point is None:
        return None
    x, y = point
    return x ** x.p, y ** y.p


def point_count(p: int) -> int:
    total = 1
    for x in range(p):
        rhs = (x * x * x + 7) % p
        if rhs == 0:
            total += 1
        elif legendre(rhs, p) == 1:
            total += 2
    return total


def full_product(values):
    out = values[0] ** 0
    for value in values:
        out = out * value
    return out


def curve_replay(row):
    E, n, G, S, beta, lam, h, values = half_sequence(row)
    m = (n - 1) // 2
    even = tuple(range(2, n, 2))
    odd = tuple(range(1, n, 2))
    assert len(even) == len(odd) == m
    assert set(even).isdisjoint(odd)
    assert set(even) | set(odd) == set(range(1, n))
    assert (1 + 1) % n not in odd
    assert ((n - 1) + (n - 1)) % n not in even

    product0 = full_product(values)
    translation_product_checks = 0
    for a in range(n):
        translated = [values[(a + k) % n] for k in range(n)]
        assert full_product(translated) == product0
        translation_product_checks += 1

    one = E.c(1)
    full_polynomial = roots(values, one)
    Gm, Sm = E.neg(G), E.neg(S)
    reversed_values = [one] + [shifted(E, h, Gm, E.mul(k, G), Sm) for k in range(1, n)]
    for k in range(1, n):
        assert reversed_values[k] == values[n - k]
    assert roots(reversed_values, one) == full_polynomial

    assert point_count(E.p) == n
    frobenius_kernel_checks = 0
    frobenius_fibre_checks = 0
    phiS = E.add(frobenius_point(S), E.neg(S))
    assert phiS is not None
    for k in range(n):
        point = E.mul(k, G)
        assert E.add(frobenius_point(point), E.neg(point)) is None
        frobenius_kernel_checks += 1
        shifted_point = E.add(S, point)
        assert E.add(frobenius_point(shifted_point), E.neg(shifted_point)) == phiS
        frobenius_fibre_checks += 1

    return {
        'p': E.p,
        'n': n,
        'half_size': m,
        'point_count_equals_subgroup_order': True,
        'even_half_is_subgroup': False,
        'odd_half_is_subgroup': False,
        'half_can_be_kernel_coset_inside_prime_group': False,
        'full_product_translation_checks': translation_product_checks,
        'full_orbit_polynomial_marking_invariant': True,
        'frobenius_kernel_checks': frobenius_kernel_checks,
        'frobenius_fibre_checks': frobenius_fibre_checks,
        'frobenius_minus_identity_fibre_size': n,
        'errors': 0,
    }


def build_payload():
    curves = [curve_replay(row) for row in TOYS]
    aggregate = {
        'curves': len(curves),
        'full_product_translation_checks': sum(r['full_product_translation_checks'] for r in curves),
        'frobenius_kernel_checks': sum(r['frobenius_kernel_checks'] for r in curves),
        'frobenius_fibre_checks': sum(r['frobenius_fibre_checks'] for r in curves),
        'all_point_counts_equal_prime_subgroup_orders': all(r['point_count_equals_subgroup_order'] for r in curves),
        'all_marked_halves_non_subgroups': all(not r['even_half_is_subgroup'] and not r['odd_half_is_subgroup'] for r in curves),
        'all_full_orbit_polynomials_marking_invariant': all(r['full_orbit_polynomial_marking_invariant'] for r in curves),
        'errors': 0,
    }
    out = {
        'profile_id': 'UORC-056-PRIME-KERNEL-NORM-RIGIDITY-C40',
        'schema_version': '1.0',
        'central_target': 'Y_G(x([k]G))/y([k]G)=(-1)^k',
        'predecessor': 'C39 exact degree-optimal parity orbit factorization',
        'curves': curves,
        'theorems': {
            'prime_kernel_no_half_subgroup': 'A cyclic group of prime order has no subgroup or subgroup coset of size (n-1)/2.',
            'full_norm_marking_blind': 'A product or norm over the full kernel is invariant under translation and generator re-marking because both actions permute the fibre.',
            'frobenius_fibre': 'When E(F_p)=H, the fibre of Frobenius-minus-identity through S is S+H.',
            'no_subgroup_norm_tower': 'A tower whose steps are norms over subgroups of H has only trivial or full-kernel steps when |H| is prime.',
        },
        'decision': {
            'compact_full_kernel_norm_geometry_found': True,
            'full_kernel_norm_can_select_ordered_parity_factor': False,
            'ordinary_isogeny_norm_decoder_closed': True,
            'subgroup_norm_tower_decoder_closed': True,
            'incomplete_oriented_half_norm_evaluator_found': False,
            'parity_oracle_found': False,
            'sub_sqrt_ecdlp_found': False,
        },
        'aggregate': aggregate,
    }
    out['digest'] = hashlib.sha256(json.dumps(out, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    payload = build_payload()
    if args.out:
        args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    print('UORC056_PRIME_KERNEL_NORM_RIGIDITY_C40_OK')
    print(json.dumps(payload['aggregate'], indent=2, sort_keys=True))
    print('digest=' + payload['digest'])


if __name__ == '__main__':
    main()
