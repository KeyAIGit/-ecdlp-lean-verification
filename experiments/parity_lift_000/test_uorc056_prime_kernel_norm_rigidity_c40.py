import unittest
from uorc056_prime_kernel_norm_rigidity_c40 import build_payload

class C40Tests(unittest.TestCase):
    def test_payload(self):
        payload = build_payload()
        aggregate = payload['aggregate']
        self.assertEqual(aggregate['curves'], 5)
        self.assertEqual(aggregate['full_product_translation_checks'], 443)
        self.assertEqual(aggregate['frobenius_kernel_checks'], 443)
        self.assertEqual(aggregate['frobenius_fibre_checks'], 443)
        self.assertTrue(aggregate['all_point_counts_equal_prime_subgroup_orders'])
        self.assertTrue(aggregate['all_marked_halves_non_subgroups'])
        self.assertTrue(aggregate['all_full_orbit_polynomials_marking_invariant'])
        self.assertTrue(payload['decision']['ordinary_isogeny_norm_decoder_closed'])
        self.assertFalse(payload['decision']['parity_oracle_found'])

if __name__ == '__main__':
    unittest.main()
