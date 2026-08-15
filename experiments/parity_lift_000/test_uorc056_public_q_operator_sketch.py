#!/usr/bin/env python3
"""Unit tests for UORC-056 C27 public-Q operator-state barriers."""
from __future__ import annotations

import itertools
import unittest

from uorc056_public_q_operator_sketch import (
    FROZEN_FIELD_ORDER_PAIRS,
    SECP_HALF,
    SECP_LINEAR_DEGREE,
    SECP_LINEAR_DEGREE_FACTORIZATION,
    SECP_N,
    SECP_P,
    BilinearProbe,
    TraceAtom,
    build_result,
    exhaustive_exceptional_set_check,
    minimum_full_moment_depth,
    multiplicative_order_from_factorization,
    parity_is_mixed_outside,
    probe_cross_support_cost,
    probes_decode_parity,
    tight_probe,
    tight_trace_channel,
    trace_exceptional_residues,
    transcript_decodes_parity,
    verify_lucas_certificates,
)


class PublicQOperatorSketchTests(unittest.TestCase):
    def test_recursive_lucas_certificates(self) -> None:
        result = verify_lucas_certificates()
        self.assertEqual(result["certificate_nodes"], 45)
        self.assertTrue(result["all_required_factor_primes_certified"])

    def test_exact_secp_multiplicative_order(self) -> None:
        row = multiplicative_order_from_factorization(
            SECP_P,
            SECP_N,
            SECP_LINEAR_DEGREE,
            SECP_LINEAR_DEGREE_FACTORIZATION,
        )
        self.assertEqual(row["exact_order"], (SECP_N - 1) // 6)
        self.assertEqual(row["exact_order_bits"], 254)
        self.assertEqual(
            set(map(int, row["proper_divisor_witnesses"])),
            set(SECP_LINEAR_DEGREE_FACTORIZATION),
        )
        self.assertTrue(
            all(value != 1 for value in row["proper_divisor_witnesses"].values())
        )

    def test_exceptional_sets_below_half_are_mixed(self) -> None:
        expected_counts = {5: 5, 7: 22, 11: 386, 13: 1586}
        for order, expected in expected_counts.items():
            row = exhaustive_exceptional_set_check(order)
            self.assertEqual(row["subsets_below_half_checked"], expected)
            self.assertTrue(row["all_complements_mixed"])

    def test_tight_trace_construction(self) -> None:
        for order in (5, 7, 11, 31):
            channel = tight_trace_channel(order)
            self.assertEqual(len(channel), (order - 1) // 2)
            self.assertEqual(
                len(trace_exceptional_residues(order, (channel,))),
                (order - 1) // 2,
            )
            self.assertTrue(transcript_decodes_parity(order, (channel,)))

    def test_subhalf_trace_cannot_decode(self) -> None:
        for order in (5, 7, 11):
            half = (order - 1) // 2
            domain = range(1, order)
            for size in range(half):
                for exceptional in itertools.combinations(domain, size):
                    channels = tuple(
                        (TraceAtom(a=(-residue) % order, b=1),)
                        for residue in exceptional
                    )
                    self.assertTrue(
                        parity_is_mixed_outside(order, set(exceptional))
                    )
                    self.assertFalse(transcript_decodes_parity(order, channels))

    def test_tight_coordinate_sparse_probe(self) -> None:
        for order in (5, 7, 11, 31):
            probe = tight_probe(order)
            self.assertEqual(
                probe_cross_support_cost((probe,)),
                (order - 1) // 2,
            )
            self.assertTrue(probes_decode_parity(order, (probe,)))

    def test_subhalf_probe_cannot_decode(self) -> None:
        for order in (5, 7, 11):
            half = (order - 1) // 2
            for size in range(half):
                for support in itertools.combinations(range(1, order), size):
                    probe = BilinearProbe(
                        a=0,
                        b=1,
                        left_support=tuple(support),
                        right_support=(0,),
                    )
                    self.assertLess(probe_cross_support_cost((probe,)), half)
                    self.assertFalse(probes_decode_parity(order, (probe,)))

    def test_moment_depth_minimality(self) -> None:
        depth = minimum_full_moment_depth(SECP_HALF)
        self.assertEqual(depth, 70296448064902889502766530)
        previous = (depth - 1) * depth * (depth + 1) // 6
        current = depth * (depth + 1) * (depth + 2) // 6
        self.assertLess(previous, SECP_HALF)
        self.assertGreaterEqual(current, SECP_HALF)

    def test_full_result_boundaries(self) -> None:
        result = build_result()
        self.assertEqual(result["profile_id"], "UORC-056-PUBLIC-Q-OPERATOR-SKETCH-C27")
        self.assertEqual(
            result["linear_state_theorem"][
                "secp256k1_minimum_nontrivial_dimension"
            ],
            SECP_LINEAR_DEGREE,
        )
        self.assertEqual(
            result["sparse_trace_sketch_theorem"][
                "secp256k1_distinct_atom_lower_bound"
            ],
            SECP_HALF,
        )
        self.assertEqual(
            result["coordinate_sparse_krylov_theorem"][
                "secp256k1_cross_support_lower_bound"
            ],
            SECP_HALF,
        )
        self.assertEqual(
            len(result["linear_state_theorem"]["toy_rows"]),
            len(FROZEN_FIELD_ORDER_PAIRS),
        )
        self.assertFalse(any(result["decision"].values()))
        self.assertEqual(len(result["digest"]), 64)


if __name__ == "__main__":
    unittest.main()
