import unittest

from uorc056_incomplete_oriented_product_c41 import (
    SECP_N,
    build_payload,
    first_symmetric_degree_over_pairs,
    first_total_degree_over_rows,
)


class IncompleteOrientedProductC41Tests(unittest.TestCase):
    def test_payload(self) -> None:
        payload = build_payload()
        aggregate = payload['aggregate']
        self.assertEqual(aggregate['curves'], 5)
        self.assertEqual(aggregate['declared_polynomials'], 25)
        self.assertTrue(aggregate['all_declared_polynomials_indecomposable'])
        self.assertTrue(
            aggregate['all_coefficient_recurrences_maximal_on_finite_window']
        )
        self.assertTrue(
            aggregate['all_nonnegation_bivariate_relations_dimension_forced']
        )
        self.assertTrue(
            aggregate['all_negation_relations_explained_by_swap_involution']
        )
        self.assertTrue(aggregate['all_rational_transitions_dimension_forced'])
        self.assertEqual(aggregate['errors'], 0)
        decision = payload['decision']
        self.assertTrue(
            decision[
                'declared_composition_recurrence_transition_grammars_closed_on_frozen_corpus'
            ]
        )
        self.assertFalse(decision['incomplete_oriented_product_evaluator_found'])
        self.assertFalse(decision['parity_oracle_found'])
        self.assertFalse(decision['sub_sqrt_ecdlp_found'])

    def test_secp_dimension_frontier(self) -> None:
        rows = SECP_N - 1
        pairs = rows // 2
        expected = 481231938336009023090067544955250113852
        self.assertEqual(first_total_degree_over_rows(rows), expected)
        self.assertEqual(first_symmetric_degree_over_pairs(pairs), expected)
        payload = build_payload()['secp256k1_dimension_frontier']
        self.assertEqual(payload['first_general_bivariate_interpolation_degree'], expected)
        self.assertEqual(payload['first_swap_symmetric_interpolation_degree'], expected)
        self.assertEqual(payload['degree_bit_length'], 129)
        self.assertEqual(payload['first_rational_transition_degree'], pairs)
        self.assertEqual(payload['rational_degree_bit_length'], 255)


if __name__ == '__main__':
    unittest.main()
