import json, os, unittest
from pathlib import Path
from uorc056_c55_cycle_analysis import build_payload
from uorc056_c55_cycle_core import SECP_N, SECP_ORD2, doubling_cycles, mixed_parity, cycle_label

class CycleLabelOpenTranslationC55Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=os.environ.get('UORC056_C55_PAYLOAD')
        cls.payload=json.loads(Path(path).read_text()) if path else build_payload()

    def test_counts_and_identities(self):
        a=self.payload['aggregate']
        self.assertEqual(a['curves'],10)
        self.assertEqual(a['inherited'],6)
        self.assertEqual(a['new_heldout'],4)
        self.assertEqual(a['scalar_rows'],19194)
        self.assertEqual(a['carry_checks'],19194)
        self.assertEqual(a['parity_word_checks'],19194)
        self.assertEqual(a['label_checks'],19194)
        self.assertTrue(a['all_cycles_mixed_parity'])
        self.assertTrue(a['all_cycle_labels_have_correct_image_size'])
        self.assertEqual(a['errors'],0)

    def test_no_uniform_screen_survivor(self):
        a=self.payload['aggregate']
        self.assertEqual(a['universal_cycle_affine_character_survivors'],[])
        self.assertEqual(a['universal_cycle_representation_survivors'],[])
        self.assertEqual(a['universal_within_cycle_affine_character_survivors'],[])
        self.assertEqual(a['universal_within_cycle_representation_survivors'],[])

    def test_secp_certificate(self):
        s=self.payload['secp256k1']
        self.assertEqual(s['n'],SECP_N)
        self.assertEqual(s['ord_n_2'],SECP_ORD2)
        self.assertTrue(s['ord_n_2_is_odd'])
        self.assertEqual(s['full_cycle_count'],64)
        self.assertEqual(s['pair_cycle_count'],32)
        self.assertTrue(s['lambda_in_doubling_subgroup'])
        self.assertEqual(s['rational_cycle_invariant_pole_degree_lower_bound_bits'],254)
        self.assertGreaterEqual(s['generic_within_cycle_bsgs_cost_bits'],125)

    def test_decision(self):
        d=self.payload['decision']
        self.assertTrue(d['exact_64_state_secp_cycle_label_found'])
        self.assertFalse(d['cycle_label_is_publicly_evaluable_from_Q'])
        self.assertFalse(d['cycle_label_alone_can_decode_parity'])
        self.assertTrue(d['exact_cycle_orientation_norm_found'])
        self.assertFalse(d['cycle_orientation_norm_alone_can_decode_point_parity'])
        self.assertTrue(d['declared_cycle_and_phase_character_grammars_closed'])
        self.assertFalse(d['compressed_unsquared_open_translation_found'])
        self.assertFalse(d['cheap_parity_decoder_found'])
        self.assertFalse(d['parity_oracle_found'])
        self.assertFalse(d['sub_sqrt_ecdlp_found'])

    def test_small_cycle_mixed_parity_directly(self):
        cycles=doubling_cycles(31)
        self.assertEqual(len(cycles),6)
        self.assertTrue(all(len(c)==5 and mixed_parity(c) for c in cycles))
        labels={cycle_label(c[0],31,5) for c in cycles}
        self.assertEqual(len(labels),6)

if __name__=='__main__':unittest.main()
