import unittest
from uorc056_parity_orbit_factorization_c39_compact import SECP_N,build_payload
class C39Tests(unittest.TestCase):
 def test_payload(self):
  p=build_payload();a=p['aggregate'];self.assertEqual(a['curves'],5);self.assertEqual(a['orbit_decoder_checks'],438);self.assertTrue(a['all_orbit_polynomials_degree_optimal']);self.assertTrue(a['all_B_units_on_half_kernel']);self.assertTrue(a['all_even_odd_polynomials_dense_except_at_most_one_coefficient']);self.assertTrue(a['all_trace_power_character_product_grammars_inconsistent']);self.assertEqual(a['trace_power_atoms_declared'],7307232);self.assertFalse(p['decision']['parity_oracle_found'])
 def test_secp(self):
  h=(SECP_N-1)//2;self.assertTrue(2**254<h<2**255)
if __name__=='__main__':unittest.main()
