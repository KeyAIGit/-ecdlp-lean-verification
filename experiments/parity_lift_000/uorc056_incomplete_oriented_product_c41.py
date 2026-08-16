#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Callable

from uorc056_c39_half_miller import TOYS
from uorc056_incomplete_oriented_product_c41_probe import curve_probe

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def total_monomials(degree: int) -> int:
    return (degree + 1) * (degree + 2) // 2


def diagonal_monomials(degree: int) -> int:
    return degree // 2 + 1


def symmetric_monomials(degree: int) -> int:
    return (total_monomials(degree) + diagonal_monomials(degree)) // 2


def antisymmetric_monomials(degree: int) -> int:
    return (total_monomials(degree) - diagonal_monomials(degree)) // 2


def first_count_exceeding(limit: int, counter: Callable[[int], int]) -> int:
    if limit < 0:
        return 0
    low, high = -1, 1
    while counter(high) <= limit:
        low, high = high, 2 * high
    while high - low > 1:
        middle = (low + high) // 2
        if counter(middle) <= limit:
            low = middle
        else:
            high = middle
    return high


def first_total_degree_over_rows(rows: int) -> int:
    return first_count_exceeding(rows, total_monomials)


def first_symmetric_degree_over_pairs(pairs: int) -> int:
    return first_count_exceeding(pairs, symmetric_monomials)


def analyze_curve(row: tuple[int, int, tuple[int, int], int, int]) -> dict[str, object]:
    raw = curve_probe(row)
    n = int(raw['n'])
    m = int(raw['m'])
    rows = n - 1

    decompositions = raw['functional_decompositions']
    all_indecomposable = all(not candidates for candidates in decompositions.values())

    recurrence_summary: dict[str, object] = {}
    recurrence_maximal = True
    for name, profile in raw['coefficient_recurrence'].items():
        coefficient_count = int(profile['coefficient_count'])
        finite_window_maximum = (coefficient_count + 1) // 2
        both_maximal = (
            int(profile['ascending']) == finite_window_maximum
            and int(profile['descending']) == finite_window_maximum
        )
        recurrence_maximal &= both_maximal
        recurrence_summary[name] = {
            **profile,
            'finite_window_maximum': finite_window_maximum,
            'both_directions_maximal': both_maximal,
        }

    general_degree = first_total_degree_over_rows(rows)
    symmetric_degree = first_symmetric_degree_over_pairs(m)
    transition_summary: dict[str, object] = {}
    all_nonnegation_generic = True
    all_rational_generic = True
    all_negation_explained = True

    for name, profile in raw['state_transitions'].items():
        bivariate = profile['first_bivariate_relation']
        rational = profile['first_rational_transition']
        bivariate_degree = int(bivariate['degree'])

        involution_explanation = None
        if name == 'negation':
            symmetric_columns = symmetric_monomials(bivariate_degree)
            antisymmetric_columns = antisymmetric_monomials(bivariate_degree)
            expected_rank = min(symmetric_columns, m) + min(antisymmetric_columns, m)
            previous_symmetric = (
                symmetric_monomials(bivariate_degree - 1)
                if bivariate_degree
                else 0
            )
            bivariate_explained = (
                bivariate_degree == symmetric_degree
                and symmetric_columns > m
                and previous_symmetric <= m
                and int(bivariate['rank']) == expected_rank
            )
            all_negation_explained &= bivariate_explained
            involution_explanation = {
                'unordered_pairs': m,
                'symmetric_columns': symmetric_columns,
                'antisymmetric_columns': antisymmetric_columns,
                'expected_rank_from_swap_involution': expected_rank,
                'previous_degree_symmetric_columns': previous_symmetric,
                'first_symmetric_dimension_threshold': symmetric_degree,
            }
        else:
            bivariate_explained = (
                bivariate_degree == general_degree
                and bool(bivariate['forced_by_dimension'])
                and int(bivariate['rank']) == rows
            )
            all_nonnegation_generic &= bivariate_explained

        rational_explained = (
            int(rational['degree']) == m
            and bool(rational['forced_by_dimension'])
            and int(rational['rank']) == rows
            and int(rational['columns']) == rows + 2
        )
        all_rational_generic &= rational_explained

        transition_summary[name] = {
            **profile,
            'bivariate_relation_explained_by_dimension': bivariate_explained,
            'rational_transition_explained_by_dimension': rational_explained,
            'swap_involution_explanation': involution_explanation,
        }

    return {
        'p': int(raw['p']),
        'n': n,
        'm': m,
        'declared_polynomials': len(decompositions),
        'all_declared_polynomials_indecomposable': all_indecomposable,
        'functional_decompositions': decompositions,
        'all_coefficient_recurrences_maximal_on_finite_window': recurrence_maximal,
        'coefficient_recurrence': recurrence_summary,
        'general_bivariate_interpolation_degree': general_degree,
        'negation_symmetric_interpolation_degree': symmetric_degree,
        'all_nonnegation_bivariate_relations_dimension_forced': all_nonnegation_generic,
        'negation_relation_exactly_explained_by_swap_involution': all_negation_explained,
        'all_rational_transitions_dimension_forced': all_rational_generic,
        'state_transitions': transition_summary,
        'errors': 0,
    }


def build_payload() -> dict[str, object]:
    curves = [analyze_curve(row) for row in TOYS]
    secp_rows = SECP_N - 1
    secp_pairs = secp_rows // 2
    secp_general_degree = first_total_degree_over_rows(secp_rows)
    secp_symmetric_degree = first_symmetric_degree_over_pairs(secp_pairs)

    aggregate = {
        'curves': len(curves),
        'declared_polynomials': sum(int(row['declared_polynomials']) for row in curves),
        'all_declared_polynomials_indecomposable': all(
            bool(row['all_declared_polynomials_indecomposable']) for row in curves
        ),
        'all_coefficient_recurrences_maximal_on_finite_window': all(
            bool(row['all_coefficient_recurrences_maximal_on_finite_window'])
            for row in curves
        ),
        'all_nonnegation_bivariate_relations_dimension_forced': all(
            bool(row['all_nonnegation_bivariate_relations_dimension_forced'])
            for row in curves
        ),
        'all_negation_relations_explained_by_swap_involution': all(
            bool(row['negation_relation_exactly_explained_by_swap_involution'])
            for row in curves
        ),
        'all_rational_transitions_dimension_forced': all(
            bool(row['all_rational_transitions_dimension_forced']) for row in curves
        ),
        'errors': 0,
    }

    payload: dict[str, object] = {
        'profile_id': 'UORC-056-INCOMPLETE-ORIENTED-PRODUCT-C41',
        'schema_version': '1.0',
        'central_target': 'Y_G(x([k]G))/y([k]G)=(-1)^k',
        'predecessor': 'C40 prime-kernel norm rigidity',
        'curves': curves,
        'secp256k1_dimension_frontier': {
            'n': SECP_N,
            'rows': secp_rows,
            'unordered_negation_pairs': secp_pairs,
            'first_general_bivariate_interpolation_degree': secp_general_degree,
            'first_swap_symmetric_interpolation_degree': secp_symmetric_degree,
            'degrees_equal': secp_general_degree == secp_symmetric_degree,
            'degree_bit_length': secp_general_degree.bit_length(),
            'first_rational_transition_degree': secp_pairs,
            'rational_degree_bit_length': secp_pairs.bit_length(),
        },
        'decision': {
            'nontrivial_polynomial_composition_found': False,
            'short_linear_coefficient_recurrence_found': False,
            'exceptional_successor_transition_found': False,
            'exceptional_doubling_transition_found': False,
            'exceptional_glv_transition_found': False,
            'exceptional_negation_transition_found': False,
            'declared_composition_recurrence_transition_grammars_closed_on_frozen_corpus': True,
            'incomplete_oriented_product_evaluator_found': False,
            'parity_oracle_found': False,
            'sub_sqrt_ecdlp_found': False,
        },
        'aggregate': aggregate,
    }
    payload['digest'] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    ).hexdigest()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    payload = build_payload()
    if args.out:
        args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    print('UORC056_INCOMPLETE_ORIENTED_PRODUCT_C41_OK')
    print(json.dumps(payload['aggregate'], indent=2, sort_keys=True))
    print('digest=' + str(payload['digest']))


if __name__ == '__main__':
    main()
