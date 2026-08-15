#!/usr/bin/env python3
"""Frozen-cycle and secp256k1 records for UORC-056 V19."""
from __future__ import annotations

from typing import Any

from uorc056_shared_parity_cauchy_core import verify_sampled_cauchy_minors
from uorc056_shared_parity_fourier import (
    bilinear_leaf_sum_bound,
    dft,
    find_root_field,
    pair_sum_cover_bound,
    parity_dft_formula,
    parity_values,
    support,
)

SECP256K1_N = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16
)
FROZEN_INSTANCES = (
    ("E7-P43-N31", 43, 31),
    ("E7-P67-N79", 67, 79),
    ("E7-P79-N67", 79, 67),
    ("E7-P127-N127", 127, 127),
    ("E7-P163-N139", 163, 139),
)
EXHAUSTIVE_CAUCHY_ORDERS = (5, 7)


def cycle_record(instance_id: str, field_prime: int, order: int) -> dict[str, Any]:
    modulus, root = find_root_field(order)
    parity = parity_values(order, modulus)
    transform = dft(parity, root, modulus)
    if transform != parity_dft_formula(order, root, modulus):
        raise AssertionError("odd-cycle parity DFT formula failed")
    if len(set(transform)) != order or 0 in transform:
        raise AssertionError("canonical parity spectrum is not full and distinct")

    free_zero = list(parity)
    free_zero[0] = 0
    free_transform = dft(free_zero, root, modulus)
    free_support = support(free_transform)
    if free_support != tuple(range(1, order)):
        raise AssertionError("free-zero extension did not have support n-1")

    constant_transform = dft([1] * order, root, modulus)
    if support(constant_transform) != (0,):
        raise AssertionError("constant denominator did not have one frequency")

    return {
        "id": instance_id,
        "curve_field_prime": field_prime,
        "n": order,
        "Fourier_replay_field_prime": modulus,
        "Fourier_root": root,
        "canonical_parity_spectrum_support": len(support(transform)),
        "canonical_parity_spectrum_distinct_values": len(set(transform)),
        "free_identity_parity_support": len(free_support),
        "extremal_rational_numerator_support": len(free_support),
        "extremal_rational_denominator_support": len(support(constant_transform)),
        "extremal_rational_total_support": order,
        "direct_rational_total_support_lower_bound": order,
        "direct_rational_shared_union_lower_bound": (order + 1) // 2,
        "bilinear_leaf_product_target": order - 1,
        "bilinear_leaf_sum_lower_bound": bilinear_leaf_sum_bound(order - 1),
        "bilinear_shared_dictionary_lower_bound": pair_sum_cover_bound(order - 1),
        "sampled_cauchy": verify_sampled_cauchy_minors(order),
    }


def secp256k1_record() -> dict[str, Any]:
    order = SECP256K1_N
    target = order - 1
    union = (order + 1) // 2
    leaf_sum = bilinear_leaf_sum_bound(target)
    dictionary = pair_sum_cover_bound(target)
    expected = (
        57896044618658097711785492504343953926418782139537452191302581570759080747169,
        680564733841876926926749214863536422911,
        481231938336009023090067544955250113853,
    )
    if (union, leaf_sum, dictionary) != expected:
        raise AssertionError("fixed secp256k1 bounds drifted")
    if (leaf_sum // 2) * ((leaf_sum + 1) // 2) < target:
        raise AssertionError("leaf-sum bound is insufficient")
    if ((leaf_sum - 1) // 2) * (leaf_sum // 2) >= target:
        raise AssertionError("preceding leaf-sum bound unexpectedly suffices")
    if dictionary * (dictionary + 1) // 2 < target:
        raise AssertionError("dictionary bound is insufficient")
    if (dictionary - 1) * dictionary // 2 >= target:
        raise AssertionError("preceding dictionary bound unexpectedly suffices")
    return {
        "n": order,
        "direct_parity_spectrum_support_with_free_identity_lower_bound": target,
        "direct_parity_spectrum_support_with_canonical_identity": order,
        "direct_sparse_rational_separate_support_lower_bound": order,
        "direct_sparse_rational_separate_support_lower_bound_exact": True,
        "direct_sparse_rational_canonical_identity_lower_bound": order + 1,
        "direct_sparse_rational_shared_union_lower_bound": union,
        "direct_sparse_rational_shared_union_lower_bound_bit_length": union.bit_length(),
        "bilinear_leaf_sum_lower_bound": leaf_sum,
        "bilinear_leaf_sum_lower_bound_bit_length": leaf_sum.bit_length(),
        "bilinear_leaf_sum_gap_below_2_pow_129": 2**129 - leaf_sum,
        "bilinear_shared_dictionary_lower_bound": dictionary,
        "bilinear_shared_dictionary_lower_bound_bit_length": dictionary.bit_length(),
        "rational_union_exceeds_2_pow_254": union > 2**254,
        "rational_union_below_2_pow_255": union < 2**255,
        "rational_separate_support_exceeds_2_pow_255": order > 2**255,
        "rational_separate_support_below_2_pow_256": order < 2**256,
    }
