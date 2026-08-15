from __future__ import annotations

import unittest

from uorc056_dynamic_carry_aggregation import (
    DIAGNOSTIC_ORDERS,
    TWO_CARRY_SCREEN_ORDERS,
    aggregate,
    balanced_dag,
    binary_dag,
    build_payload,
    evaluate_terms,
    linear_dag,
    screen_two_noncomplete_carries,
    sigma,
    three_carry_factors,
    verify_compiled_dag,
    verify_three_carry_identity,
)


class DynamicCarryAggregationTests(unittest.TestCase):
    def test_dag_compiler_normal_form(self) -> None:
        for order in DIAGNOSTIC_ORDERS:
            for dag in (binary_dag(order), balanced_dag(order), linear_dag(order)):
                row = verify_compiled_dag(dag, order, order)
                self.assertEqual(row["terminal_weight"], 0)
                self.assertEqual(row["terminal_leaf_parity"], 1)

    def test_chain_products_are_equal_as_functions(self) -> None:
        for order in DIAGNOSTIC_ORDERS:
            dags = (binary_dag(order), balanced_dag(order), linear_dag(order))
            terms = [dag.compile(order)[-1].carry_terms for dag in dags]
            for scalar in range(order):
                values = [evaluate_terms(term_set, scalar, order) for term_set in terms]
                self.assertTrue(all(value == values[0] for value in values))
                self.assertEqual(values[0], aggregate(order, scalar, order))
                self.assertEqual(values[0], sigma(scalar, order))

    def test_three_carry_identity(self) -> None:
        for order in (13, 17, 19, 23, 29, 31, 43, 67, 79, 127, 139):
            row = verify_three_carry_identity(order)
            self.assertTrue(row["all_factors_individually_noncomplete"])

    def test_three_carry_factor_count(self) -> None:
        for order in (13, 17, 19, 23, 29, 31):
            self.assertEqual(len(three_carry_factors(order)), 3)

    def test_no_two_noncomplete_carry_survivor_on_screen(self) -> None:
        for order in TWO_CARRY_SCREEN_ORDERS:
            row = screen_two_noncomplete_carries(order)
            self.assertEqual(row["two_factor_survivors"], 0)

    def test_full_replay(self) -> None:
        payload = build_payload()
        aggregate_row = payload["aggregate"]
        decision = payload["decision"]
        self.assertEqual(payload["profile_id"], "UORC-056-DYNAMIC-CARRY-AGGREGATION-C34")
        self.assertEqual(aggregate_row["dag_instances"], 24)
        self.assertEqual(aggregate_row["frozen_three_carry_checks"], 46260)
        self.assertEqual(aggregate_row["two_noncomplete_carry_survivors"], 0)
        self.assertTrue(aggregate_row["single_carry_classification_exact_on_all_screens"])
        self.assertTrue(aggregate_row["three_carry_factors_noncomplete_on_all_declared_orders"])
        self.assertEqual(aggregate_row["errors"], 0)
        self.assertTrue(decision["addition_dag_compiler_built"])
        self.assertTrue(decision["carry_product_chain_independence_proved"])
        self.assertTrue(decision["three_carry_semantic_compression_found"])
        self.assertTrue(decision["q_only_field_aggregate_blocked"])
        self.assertFalse(decision["anchor_dependent_field_aggregate_found"])
        self.assertFalse(decision["parity_oracle_found"])
        self.assertFalse(decision["sub_sqrt_ecdlp_found"])
        self.assertEqual(len(payload["digest"]), 64)


if __name__ == "__main__":
    unittest.main()
