#!/usr/bin/env python3
from __future__ import annotations

import unittest

import uorc056_nested_slp_v3 as implementation
import uorc056_nested_slp_v3_runner as runner
import uorc056_transfer_synth_v2 as base


class NestedSlpV3Tests(unittest.TestCase):
    def setUp(self) -> None:
        implementation.compute_endpoint_metrics = runner.corrected_endpoint_metrics

    def test_seed_catalogue_is_uniform_and_frozen(self) -> None:
        contexts = implementation.contexts()
        seeds = implementation.seed_terms(contexts)
        self.assertEqual(len(contexts), 5)
        self.assertEqual(len(seeds), 27)
        self.assertEqual(len({seed.values for seed in seeds}), len(seeds))
        self.assertFalse(any("17" in seed.expression or "41" in seed.expression for seed in seeds))

    def test_zero_is_charged_once_not_as_a_second_sign_error(self) -> None:
        context = base.CurveContext(
            p=7,
            order=5,
            generator=(1, 1),
            points=(None, (1, 1), (2, 1), (3, 1), (4, 1)),
            beta=2,
            beta2=4,
        )
        # k=1 is zero/undefined; k=2,3,4 have signs +,-,+ and are correct.
        values = ((0, 1, 6, 1),)
        errors, zeros, _ = runner.corrected_endpoint_metrics(values, (context,))
        self.assertEqual(errors, (0,))
        self.assertEqual(zeros, (1,))

    def test_inverse_rejects_any_zero_denominator(self) -> None:
        context = base.CurveContext(
            p=7,
            order=5,
            generator=(1, 1),
            points=(None, (1, 1), (2, 1), (3, 1), (4, 1)),
            beta=2,
            beta2=4,
        )
        term = implementation.make_term(
            expression="synthetic",
            size=0,
            values=((1, 0, 2, 3),),
            field_add=0,
            field_mul=0,
            field_inv=0,
            negations=0,
            features=(),
            constants=(),
            curve_contexts=(context,),
        )
        self.assertIsNone(implementation.unary_term("inv", term, (context,)))

    def test_one_gate_smoke_search_is_deterministic(self) -> None:
        first = implementation.run(max_size=1, beam_size=24)
        second = implementation.run(max_size=1, beam_size=24)
        self.assertEqual(first["decision"], second["decision"])
        self.assertEqual(first["layer_statistics"], second["layer_statistics"])
        self.assertEqual(
            first["best_all_five_near_miss"],
            second["best_all_five_near_miss"],
        )


if __name__ == "__main__":
    unittest.main()
