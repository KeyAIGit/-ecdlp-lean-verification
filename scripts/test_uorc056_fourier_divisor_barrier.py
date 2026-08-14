import unittest

import uorc056_fourier_divisor_barrier as module


class FourierDivisorBarrierTests(unittest.TestCase):
    def test_peak_frequency(self):
        self.assertEqual(module.peak_frequency(31), 15)
        with self.assertRaises(ValueError):
            module.peak_frequency(32)

    def test_frozen_result(self):
        result = module.run()
        self.assertEqual(result["experiment"], "UORC-056-FOURIER-DIVISOR-BARRIER-V7")
        self.assertEqual(len(result["frozen_replays"]), 5)
        self.assertEqual(result["secp256k1"]["cofactor"], 1)
        bounds = result["secp256k1"]["conditional_odd_divisor_support_lower_bounds"]
        self.assertGreater(int(bounds["C=1"]), 2**127)
        self.assertGreater(int(bounds["C=8"]), 2**124)


if __name__ == "__main__":
    unittest.main()
