#!/usr/bin/env python3
from __future__ import annotations

import unittest

import uorc056_transfer_synth_v2 as synth


class TransferSynthV2Tests(unittest.TestCase):
    def test_catalogue_is_frozen_and_unique(self) -> None:
        specs = synth.generate_specs()
        self.assertEqual(len(specs), 1639)
        self.assertEqual(len({spec.atom_id for spec in specs}), len(specs))

    def test_frozen_contexts_have_declared_orbits_and_cm_roots(self) -> None:
        for curve in synth.FROZEN_CURVES:
            context = synth.build_context(*curve)
            self.assertEqual(len(context.points), context.order)
            self.assertIsNone(context.points[0])
            self.assertEqual(context.points[1], context.generator)
            self.assertEqual(pow(context.beta, 3, context.p), 1)
            self.assertEqual(pow(context.beta2, 3, context.p), 1)
            self.assertNotEqual(context.beta, 1)
            self.assertNotEqual(context.beta2, 1)

    def test_parity_target_has_half_the_nonzero_orbit(self) -> None:
        for _, order, _ in synth.FROZEN_CURVES:
            self.assertEqual(synth.parity_target(order).bit_count(), (order - 1) // 2)

    def test_phase_semantics_on_first_frozen_curve(self) -> None:
        context = synth.build_context(*synth.FROZEN_CURVES[0])
        specs = (
            synth.AtomSpec(kind="phase", constant="one"),
            synth.AtomSpec(kind="phase", constant="neg_one"),
        )
        compiled = synth.compile_atoms((context,), specs)
        self.assertEqual(compiled[0].curve_bits, (0,))
        self.assertEqual(
            compiled[1].curve_bits,
            ((1 << (context.order - 1)) - 1,),
        )

    def test_exact_search_finds_a_weight_two_synthetic_identity(self) -> None:
        context = synth.CurveContext(
            p=7,
            order=5,
            generator=(1, 1),
            points=(None, (1, 1), (2, 1), (3, 1), (4, 1)),
            beta=2,
            beta2=4,
        )
        compiled = (
            synth.CompiledAtom(
                synth.AtomSpec(kind="unary", left="x1", constant="zero"),
                (0b0001,),
            ),
            synth.CompiledAtom(
                synth.AtomSpec(kind="unary", left="y1", constant="zero"),
                (0b0100,),
            ),
        )
        outcome = synth.search_exact(
            compiled,
            (context,),
            (0,),
            maximum_weight=2,
        )
        self.assertTrue(outcome.found)
        self.assertEqual(outcome.minimum_weight, 2)
        self.assertEqual(outcome.candidates, ((0, 1),))

    def test_binary_templates_do_not_use_fitted_field_constants(self) -> None:
        self.assertEqual(
            set(synth.BINARY_CONSTANT_NAMES),
            {"zero", "one", "neg_one", "two", "neg_two", "curve_b", "neg_curve_b"},
        )
        forbidden = {"17", "41", "field_element_fit", "Y_G_coefficient"}
        for spec in synth.generate_specs():
            self.assertNotIn(spec.constant, forbidden)


if __name__ == "__main__":
    unittest.main()
